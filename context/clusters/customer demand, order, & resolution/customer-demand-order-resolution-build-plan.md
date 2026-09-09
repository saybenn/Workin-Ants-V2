# Customer Demand, Order & Resolution Build Plan

> **Cluster ID:** CL-04  
> **Cluster:** Customer Demand, Order & Resolution  
> **Modules:** `gig_demand`, `transaction_order`, `review_dispute`  
> **Plan status:** Sequential implementation plan; architecture decisions remain governed by `architecture.md`

---

## Core Principle

Build CL-04 as **vertical, observable slices** that preserve Module ownership:

```text
usable or observable behavior
→ owning application/domain service
→ authoritative database state
→ public contract
→ authorization/compliance
→ events/jobs/integrations
→ tests
→ exit gate
```

A slice is complete only when the owning source record, public behavior, integration boundary, failure behavior, and tests agree.

Do not front-load months of invisible “commerce infrastructure.” Reuse root shared primitives as they become necessary for a concrete slice. Infrastructure without a consuming behavior is not a CL-04 feature.

Unresolved architectural questions are preconditions, not invitations for implementation agents to improvise.

---

## Build Rules

1. Follow the CL-04 `architecture.md`, root architecture, and root code standards.
2. Do not expand Cluster scope beyond `gig_demand`, `transaction_order`, and `review_dispute`.
3. Do not redesign lifecycle ownership to simplify implementation.
4. Reuse canonical shared operations rather than creating feature-local copies.
5. Every mutation validates input, actor identity, authorization, current state, and contextual gates.
6. Every retryable commercial mutation is idempotent.
7. Every concurrent acceptance/settlement path uses shared database concurrency primitives.
8. Every provider remains behind its owning Module’s provider-neutral adapter.
9. CL-04 never handles raw Stripe webhook verification/dedupe.
10. Search writes occur only through Search public interfaces/events.
11. File access occurs only through Media / File Access mechanics after CL-04 contextual entitlement.
12. Privacy requests are orchestrated by Privacy / Data Erasure; CL-04 implements only target executors.
13. Asynchronous work is retryable, deduplicated, correlated, and observable.
14. Domain events are emitted after authoritative state commits, preferably via transactional outbox.
15. Each numbered feature ends with automated tests, workflow verification, and a concrete exit gate.
16. If a feature reaches an unresolved architecture decision, implementation stops at that boundary and records the blocker; it does not invent a rule.

---

## Dependencies and Preconditions

### Root/platform prerequisites

Available before the first production mutation that needs them:

- Prisma/Postgres migration workflow;
- strict TypeScript and validation conventions;
- authenticated actor context;
- Role / Authority public decision interface;
- canonical idempotency mechanism;
- shared DB concurrency primitive;
- transactional outbox/domain-event envelope;
- queue worker shell with retry/dead-letter behavior;
- structured logging/request correlation;
- Audit / Event Ledger public command.

### Upstream Module prerequisites

CL-04 can stub contracts initially, but integration features require owner contracts for:

- Customer / Buyer Profile — `resolveCustomerActor`;
- Taxonomy & Classification — Gig classification validation;
- Professional Eligibility — `evaluateProfessionalReadiness`;
- Track Subscription & Entitlement — `resolveEntitlement` and usage recording;
- Marketplace Supply — immutable Offering checkout source;
- Payment / Payout / Tax — payment/refund initiation and normalized outcomes;
- Consent & Disclosure — generic consent proof;
- Admin Review / Compliance Hold — evaluate/request/release hold;
- Media / File Access — validated attachment and signed access;
- Search / Public Visibility — projection refresh;
- Notification/Messaging — delivery/context commands;
- Privacy / Data Erasure — target executor contract.

### Architecture decision gates

Before affected production features:

- **Gig acceptance:** single-award vs multi-award and transition matrices.
- **Buyer schema migrations:** CustomerProfile nullability and legacy User ID semantics.
- **Order transitions:** transition matrix and commercial snapshot freeze point.
- **Review submission:** rating scale and actor schema.
- **Dispute production:** opener schema, resolution-vs-close semantics, dispute multiplicity.
- **Destructive erasure:** approved retention policy.

Providers such as Stripe and an external e-sign provider may be stubbed behind ports while domain slices are built. Provider choice must not block owner-domain tests.

---

# Phase 1 — Demand Capture and Accepted Work

## 01 Gig Draft and Publication Boundary

Create a customer-owned Gig draft/read surface and a publication command that stops at unresolved lifecycle/visibility boundaries rather than inventing them.

### Objective

A resolved CustomerProfile can create and edit a Gig draft with validated domain data; publication is available only for the subset of policy that is architecturally settled.

### User-visible / Observable Result

A customer can create a draft, retrieve it, edit supported fields, attach accepted taxonomy/media references, and receive specific validation/authorization errors. Public projection is requested only when publication prerequisites are satisfied.

### Owning Module(s)

- `gig_demand`.

### Dependencies

- authenticated actor;
- CustomerProfile resolver;
- Role / Authority;
- taxonomy validation;
- Media public readiness interface;
- Location Safety public projection if location is exposed;
- hold evaluation;
- Search refresh interface.

### Shared Operations Used

- `resolveAuthenticatedActor` — Identity & Access; resolve trusted actor; Gig supplies customer action context; do not rebuild session helpers.
- `authorizeResourceAction` — Role / Authority; authorize create/update/publish; Gig supplies ownership facts; do not build Gig RBAC.
- `resolveCustomerActor` — Customer / Buyer Profile; resolve buyer actor; do not treat User as sole commercial identity.
- `validateTaxonomyAssignment` — Taxonomy; validate domain/category/tags; Gig decides whether publication requires them; no local taxonomy cleaner.
- `evaluateComplianceHold` — Hold owner; block applicable publish/action; no local blocked flag.
- Search refresh public interface — Search owner; request projection; no Typesense client.
- `appendAuditEvent` / `publishDomainEvent` where policy requires.

### Data / Schema

- `Gig`;
- `GigStatus`;
- `GigVisibility`;
- `GigTag`;
- `GigMedia`;
- relevant indexes for customer/status/discovery;
- no new invitation schema unless invite-only architecture is separately approved.

CustomerProfile migration/nullability changes must follow an explicit migration ruling.

### Public Interfaces

- `createGigDraft`;
- `updateGigDraft`;
- `getGig`;
- `listCustomerGigs`;
- `publishGig` for approved visibility/policy paths.

### Logic

- validate budget/currency rules that are already approved;
- validate classification through Taxonomy;
- validate contextual Media references through Media owner;
- maintain Gig ownership;
- publication applies Gig-local status/visibility policy and external gate results;
- do not implement `invite_only` enforcement until an audience authority exists.

### UI / Administrative Surface

Minimum customer Gig draft/edit/view surface and validation states. Public discovery can remain Search-owned.

### Authorization / Compliance

- CustomerProfile must control the Gig.
- Professional/admin actors cannot mutate customer Gig unless an approved admin action explicitly allows it.
- exact location must not leak into public output.
- active holds can block publish.

### Events / Jobs / Integrations

- publish source-change event/outbox;
- request Search refresh after committed public-readiness change;
- optional notification hooks only through Notification.

### Failure Behavior

- invalid classification: reject with owner-provided reason;
- stale/non-ready Media: reject/hold draft;
- hold denial: preserve draft, do not publish;
- Search unavailable: Gig publication truth commits; projection retries asynchronously;
- unresolved invite-only mode: return unsupported/feature-disabled, not an invented ACL.

### Tests

- unit validation;
- authorization contract;
- CustomerProfile resolution;
- taxonomy contract;
- hold contract;
- Search request after commit;
- no direct Typesense/Media writes;
- privacy-safe location serialization.

### Out of Scope

- Professional responses;
- response acceptance;
- Order creation;
- payment;
- invite-only audience model.

### Exit Gate

- draft CRUD and authorized reads pass;
- publication for approved visibility paths writes only Gig-owned state;
- projection failure does not roll back source truth;
- no local auth/entitlement/search/media implementation exists;
- unresolved invite-only path remains explicitly disabled.

---

## 02 Professional Gig Response

Allow an eligible ProfessionalProfile to submit, view, revise within approved rules, withdraw, and allow the customer to view/shortlist/reject a single response.

### Objective

Create a complete response loop without yet accepting work.

### User-visible / Observable Result

An eligible Professional can submit one response per Gig; the customer can see and manage it; duplicates and ineligible responses fail deterministically.

### Owning Module(s)

- `gig_demand`.

### Dependencies

- Feature 01;
- Professional Eligibility public interface;
- authority;
- canonical idempotency;
- Notification.

### Shared Operations Used

- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `evaluateProfessionalReadiness` — Professional Eligibility owns readiness; Gig supplies `respond_to_gig` context; do not inspect raw verification/payment tables.
- `executeIdempotentCommand` — one semantic response creation per retry;
- `publishDomainEvent`;
- `requestNotification`.

### Data / Schema

- `GigResponse`;
- unique `(gigId, professionalProfileId)` constraint;
- response status enum.

### Public Interfaces

- `submitGigResponse`;
- `reviseGigResponse` only for explicitly approved editable states;
- `withdrawGigResponse`;
- `markGigResponseViewed`;
- `shortlistGigResponse`;
- `rejectGigResponse`;
- `listGigResponsesForPoster`;
- `getProfessionalGigResponse`.

### Logic

- Gig must be eligible to receive responses;
- Professional readiness must pass;
- proposal amount/currency must be valid;
- uniqueness is enforced both by policy and database;
- revision does not create multiple proposal rows.

### UI / Administrative Surface

Professional response form/status view and customer response list/actions.

### Authorization / Compliance

Professional may mutate only own response. CustomerProfile controlling Gig may view/shortlist/reject. Admin access follows explicit authority decisions.

### Events / Jobs / Integrations

Domain events and notification requests after commit.

### Failure Behavior

- duplicate create returns existing/replay or deterministic conflict per idempotency policy;
- readiness denial returns reason without leaking sensitive proof;
- concurrent duplicate insert is handled as domain conflict;
- Notification failure retries independently.

### Tests

- unique response constraint;
- readiness allow/deny contract;
- authorization;
- idempotent retry;
- transition tests for approved response states;
- notification/outbox integration.

### Out of Scope

- response acceptance;
- GigAssignment;
- payment or Order.

### Exit Gate

- one Professional cannot create two responses for one Gig;
- no response is accepted without readiness;
- customer and professional actions are correctly scoped;
- duplicate retries do not duplicate rows/events.

---

## 03 Atomic Response Acceptance and GigAssignment

Atomically accept an eligible response and create/identify the GigAssignment, using the approved assignment cardinality and transition rulings.

### Objective

Turn one accepted proposal into authoritative accepted-work truth without creating transaction/payment truth.

### User-visible / Observable Result

The customer can accept a response once; concurrent/duplicate acceptance produces one permitted assignment result and stable conflicts/replays.

### Owning Module(s)

- `gig_demand`.

### Dependencies

- Features 01–02;
- explicit single-award vs multi-award ruling;
- approved Gig/Response/Assignment transition matrices;
- shared idempotency and DB concurrency;
- Professional readiness recheck.

### Shared Operations Used

- `executeIdempotentCommand`;
- `acquireAggregateLock` or approved `withOptimisticConcurrency`;
- `transitionLifecycleState`;
- `evaluateProfessionalReadiness`;
- `publishDomainEvent`;
- `appendAuditEvent`.

No custom lock/idempotency/state-machine framework may be created.

### Data / Schema

- `GigAssignment`;
- any approved uniqueness/constraint enforcing assignment cardinality;
- transition-support fields/timestamps only if approved by Module architecture.

### Public Interfaces

- `acceptGigResponse`;
- `getGigAssignment`;
- `listProfessionalGigAssignments`;
- `getGigAssignmentCheckoutSource`.

### Logic

Within one transaction/serialized acceptance scope:

1. claim idempotency key;
2. verify controlling CustomerProfile;
3. verify Gig and response states;
4. recheck Professional readiness;
5. enforce assignment cardinality;
6. accept response;
7. create or replay assignment;
8. update Gig state only according to approved transition graph;
9. append owner event/outbox.

### UI / Administrative Surface

Customer acceptance action and Professional/customer assignment view.

### Authorization / Compliance

CustomerProfile must control Gig. Acceptance cannot bypass holds/readiness. Do not infer readiness from TrustBadge alone.

### Events / Jobs / Integrations

Emit assignment-ready event after commit. Order creation is Feature 05 and may consume the event/command.

### Failure Behavior

- two competing acceptances: exactly the approved number succeeds;
- stale response/readiness: conflict/deny with stable reason;
- retry after successful transaction: replay same assignment result;
- downstream Order unavailable: assignment remains accepted truth; reconciliation later creates Order, without duplicating assignment.

### Tests

- transaction/concurrency race tests;
- idempotent replay;
- transition matrix;
- readiness changed between submit and acceptance;
- assignment cardinality DB enforcement;
- outbox after commit only.

### Out of Scope

- Order lifecycle;
- payment;
- fulfillment.

### Exit Gate

- concurrency test proves no invalid double acceptance;
- assignment cardinality matches explicit architecture ruling;
- accepted assignment is retrievable as an immutable checkout-source DTO;
- no Order/payment state is written by Gig / Demand.

---

# Phase 2 — Transaction Truth and Commercial Snapshot

## 04 Order Aggregate and Source Contracts

Implement Order creation foundation and source XOR/integrity enforcement without payment integration.

### Objective

Create an authoritative Order from exactly one approved commercial source and persist its participants/source identity safely.

### User-visible / Observable Result

A consuming workflow can create a draft/initial Order from a source DTO and retrieve its timeline; duplicate source conversion is rejected/replayed.

### Owning Module(s)

- `transaction_order`.

### Dependencies

- CustomerProfile;
- ProfessionalProfile;
- Marketplace Supply source query;
- Feature 03 GigAssignment source query;
- explicit Order source-enforcement ruling;
- initial Order transition policy.

### Shared Operations Used

- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `executeIdempotentCommand`;
- `appendDomainLifecycleEvent`;
- `publishDomainEvent`;
- `withOptimisticConcurrency` or approved lock primitive.

### Data / Schema

- `Order`;
- `OrderStatus`;
- `OrderSourceType`;
- `OrderEvent`;
- unique `gigAssignmentId` where applicable;
- approved constraint enforcing sourceType/source IDs;
- CustomerProfile relation per migration ruling.

### Public Interfaces

- `createOrderFromGigAssignment`;
- `createOrderFromOffering`;
- `getOrder`;
- `listOrdersForActor`;
- `getOrderTimeline`.

### Logic

- validate source DTO version/status;
- resolve buyer/seller participants;
- enforce exactly one source;
- create initial Order + OrderEvent atomically;
- reject direct client-provided seller/buyer ownership facts not confirmed by source Modules.

### UI / Administrative Surface

Order detail/timeline skeleton sufficient to inspect authoritative state.

### Authorization / Compliance

Only eligible buyer/system workflow creates buyer Order. Participant reads are scoped. Admin/support access is explicit.

### Events / Jobs / Integrations

OrderCreated outbox event.

### Failure Behavior

- same GigAssignment converted twice: replay/existing Order;
- stale Offering/assignment: reject before write;
- source contract unavailable: no partial Order;
- event publication failure: outbox retries.

### Tests

- source XOR;
- one Order per GigAssignment;
- participant authorization;
- idempotency;
- OrderEvent atomicity;
- contract tests against both source DTOs.

### Out of Scope

- fees/commission;
- payment;
- agreements;
- delivery.

### Exit Gate

- both source types can create valid Order truth through public contracts;
- database prevents invalid source combinations;
- OrderEvent exists transactionally with creation;
- direct cross-Module repository reads are absent.

---

## 05 Commercial Pricing and Entitlement Snapshot

Resolve Track-owned policy and freeze the buyer fee waiver and Professional commission effect on Order.

### Objective

Make historical transaction pricing independent from future subscription/plan changes.

### User-visible / Observable Result

An Order exposes its frozen price, buyer-side fee effect, seller commission effect, source grant/plan evidence, and calculation reason.

### Owning Module(s)

- `transaction_order` owns snapshot;
- Track Subscription & Entitlement owns policy/usage truth.

### Dependencies

- Feature 04;
- explicit pricing-freeze point ruling;
- Track public contracts;
- Marketplace/Gig base price source.

### Shared Operations Used

- `resolveEntitlement`;
- `consumeMeteredEntitlement` where an entitlement use is metered;
- `executeIdempotentCommand`;
- `appendDomainLifecycleEvent`;
- `publishDomainEvent`.

### Data / Schema

Order pricing fields/snapshot JSON/source grant references already evidenced by schema/Module extract; migrations must not move Track records under Order.

### Public Interfaces

- `resolveAndSnapshotOrderPricing`;
- `getOrderPaymentRequirements`;
- optional `recordOrderCommercialUsage` orchestration.

### Logic

- resolve base source amount;
- resolve buyer fee waiver;
- resolve seller commission rate;
- calculate deterministic amounts;
- persist effective values + source evidence;
- never recompute historical Order from current entitlement later.

### UI / Administrative Surface

Order/checkout price breakdown with evidence-safe reason text.

### Authorization / Compliance

Entitlement result can change price but never grants unrelated authority. Do not expose internal plan metadata beyond needed explanation.

### Events / Jobs / Integrations

Track usage receipt recorded when the approved business event counts. Outbox event records pricing snapshot readiness.

### Failure Behavior

- Track unavailable before freeze: do not silently assume premium/default; apply explicitly approved fallback policy or fail closed;
- duplicate usage metering: idempotent receipt;
- entitlement changes after freeze: no retroactive Order mutation.

### Tests

- fee waiver yes/no;
- commission rates;
- future plan change leaves Order unchanged;
- metering idempotency;
- rounding/currency tests;
- no local premium flags.

### Out of Scope

- Stripe payment initiation;
- payout calculation beyond frozen commission input.

### Exit Gate

- an Order can explain exactly which values were frozen and why;
- future entitlement changes do not change historical pricing;
- Track remains owner of plan/grant/usage truth.

---

# Phase 3 — Agreement, Payment, and Fulfillment State

## 06 Agreement Template and Order-Specific Agreement

Build versioned templates, Order agreement instantiation, electronic-consent/manual-opt-out proof, and signer state without yet final document rendering.

### Objective

Create the authoritative legal-execution state required before gated Order actions.

### User-visible / Observable Result

An eligible Order can show its agreement version, required signer roles, generic consent linkage, Order-specific electronic-consent/manual path, and signature progress.

### Owning Module(s)

- `transaction_order`.

### Dependencies

- Feature 04–05;
- Consent & Disclosure;
- authority;
- approved agreement template governance.

### Shared Operations Used

- `queryConsentProof` / `recordConsentProof`;
- `authorizeResourceAction`;
- `executeIdempotentCommand`;
- `appendAuditEvent`;
- `appendDomainLifecycleEvent`;
- `publishDomainEvent`.

### Data / Schema

- `AgreementTemplate`;
- `Agreement`;
- `AgreementElectronicConsent`;
- `AgreementSignature`;
- `AgreementEvent`.

### Public Interfaces

- `createAgreementTemplate`;
- `activateAgreementTemplate`;
- `retireAgreementTemplate`;
- `instantiateAgreementForOrder`;
- `recordAgreementElectronicConsent`;
- `recordManualSignatureOptOut`;
- `requestAgreementSignatures`;
- `recordAgreementSignature`;
- `getAgreementPackage`.

### Logic

- immutable template version selection;
- Order-specific agreement;
- generic ConsentLog reference is evidence input, not Agreement replacement;
- signer authorization and role checks;
- all execution changes append AgreementEvent.

### UI / Administrative Surface

Admin template management; signer consent/signature progress; Order agreement status.

### Authorization / Compliance

- standalone disclosures when required;
- manual opt-out path preserved where required;
- signer identity bound to agreement role;
- no raw biometric/signature-provider secret storage.

### Events / Jobs / Integrations

Agreement lifecycle events only. External e-sign provider remains optional adapter, not required for local execution model.

### Failure Behavior

- inactive template cannot instantiate;
- stale signer state conflicts;
- missing required consent blocks electronic signing;
- generic consent success alone does not mark signature complete.

### Tests

- version immutability;
- consent-vs-agreement separation;
- signer authorization;
- manual opt-out;
- event atomicity;
- duplicate signature command idempotency.

### Out of Scope

- final PDF/hash;
- provider-specific e-sign integration;
- payment.

### Exit Gate

- Order-specific agreement state can reach “all required execution evidence satisfied” without conflating generic consent;
- every significant transition has AgreementEvent;
- template history is preserved.

---

## 07 Agreement Document Finalization and Secure Access

Render/finalize immutable agreement documents, hash exact bytes, archive privately, and issue contextual access grants through Media.

### Objective

Produce tamper-evident, private, retrievable contract proof.

### User-visible / Observable Result

Authorized participant can retrieve a finalized contract through a short-lived access path; hash verification detects byte mismatch.

### Owning Module(s)

- Transaction / Order owns agreement snapshot/hash/access authorization.
- Media / File Access owns file object/signed transport.

### Dependencies

- Feature 06;
- Media public interfaces;
- canonical queue;
- canonical hash primitive;
- sensitive access audit.

### Shared Operations Used

- `enqueueReliableJob`;
- `executeRetryWithBackoff`;
- canonical hashing primitive;
- `recordSensitiveAccess`;
- `appendAuditEvent`;
- `publishDomainEvent`;
- Media signed-access public interface.

### Data / Schema

- `AgreementDocumentSnapshot`;
- `AgreementAccessGrant`;
- Agreement event fields;
- MediaAsset reference only, not storage fields duplicated locally.

### Public Interfaces

- `generateAgreementDocument`;
- `recordAgreementDocumentSnapshot`;
- `finalizeAgreementDocument`;
- `verifyAgreementDocumentHash`;
- `issueAgreementAccessGrant`;
- `revokeAgreementAccessGrant`;
- `getAgreementPackage`.

### Logic

- render from frozen Order/template/signature facts;
- store object privately through Media;
- hash exact finalized bytes;
- record immutable snapshot version;
- never overwrite finalized bytes/snapshot;
- access requires Order participant/context + grant + Media URL issuance.

### UI / Administrative Surface

Download/view action and hash/access status for authorized users/admins.

### Authorization / Compliance

Sensitive access audited. Retention lock honored. No permanent public contract URLs.

### Events / Jobs / Integrations

PDF generation/finalization workers; grant expiration worker using shared scheduler/queue.

### Failure Behavior

- render/storage failure keeps Agreement unfinalized and retryable;
- hash mismatch marks verification failure/tamper condition, does not overwrite expected hash;
- expired/revoked grant denies access;
- Media outage does not change agreement truth.

### Tests

- exact-byte hash;
- immutable versioning;
- private access;
- grant expiry/revoke;
- sensitive-access log redaction;
- worker idempotency/retry.

### Out of Scope

- privacy deletion of retention-locked contracts;
- external e-sign vendor document truth.

### Exit Gate

- finalized snapshot cannot be edited in place;
- authorized retrieval uses Media mechanics;
- unauthorized/expired access is denied and audited;
- hash verification is reproducible.

---

## 08 Payment Initiation and Verified Order Payment

Connect Order to the Payment / Payout / Tax owner through provider-neutral commands and apply verified payment outcomes to Order truth.

### Objective

Advance Order through payment without treating Stripe as Order truth.

### User-visible / Observable Result

An eligible Order can initiate payment; verified provider success updates Order once; duplicate webhooks do not duplicate Order effects.

### Owning Module(s)

- Transaction / Order owns Order transition.
- Payment / Payout / Tax owns Stripe/payment adapter, webhook verification, provider dedupe, tax/payment records.

### Dependencies

- Features 04–07 as required by agreement gate;
- Payment public contracts;
- approved Order transition matrix;
- hold checks.

### Shared Operations Used

- `evaluateComplianceHold`;
- `executeIdempotentCommand`;
- `transitionLifecycleState`;
- `appendDomainLifecycleEvent`;
- `publishDomainEvent`;
- Observability request/failure primitives.

### Data / Schema

- Order payment/reference fields;
- OrderStatus/paid timestamp;
- `OrderEvent`;
- no `ProcessedStripeEvent` in CL-04.

### Public Interfaces

- `evaluateOrderPrePaymentGates`;
- `requestOrderPayment`;
- `applyPaymentConfirmationToOrder`;
- `applyPaymentFailureToOrder`;
- `getOrderPaymentRequirements`.

### Logic

- enforce source/pricing/agreement/hold gates;
- send frozen amount/tax context to Payment owner;
- receive normalized result;
- apply result once;
- never trust browser redirect.

### UI / Administrative Surface

Checkout/payment state and recoverable failure state.

### Authorization / Compliance

Buyer authorization; step-up only if root policy requires. Do not expose processor secrets.

### Events / Jobs / Integrations

Payment owner handles Stripe. Order emits payment-confirmed event after commit.

### Failure Behavior

- provider timeout: Order remains authoritative pre-payment state;
- duplicate verified webhook: replay/no duplicate OrderEvent;
- conflicting provider outcome: route to reconciliation/manual review, do not blindly transition;
- hold becomes active: block new payment action as policy requires.

### Tests

- normalized provider contract;
- duplicate webhook result;
- client redirect spoof attempt;
- agreement gate;
- hold gate;
- provider outage/reconciliation.

### Out of Scope

- payout execution;
- dispute refund adjudication.

### Exit Gate

- raw Stripe payload never enters Order domain service;
- one verified payment produces one business transition;
- Order remains correct during provider failure/retry.

---

## 09 Order Fulfillment, Delivery Entitlement, and Completion

Implement the approved post-payment Order transitions and stable entitlement query for CL-05 delivery consumers.

### Objective

Make Order a reliable gate for booking/media/video/digital delivery and establish completion truth.

### User-visible / Observable Result

Buyer/professional can see Order progress; authorized delivery Modules can ask whether the Order permits a specific action.

### Owning Module(s)

- `transaction_order`.

### Dependencies

- Feature 08;
- approved transition matrix;
- CL-05 contracts where needed;
- hold evaluation.

### Shared Operations Used

- `transitionLifecycleState`;
- `authorizeResourceAction`;
- `evaluateComplianceHold`;
- `executeIdempotentCommand`;
- `publishDomainEvent`.

### Data / Schema

Order status/timestamps, OrderEvent, OrderFile contextual attachments.

### Public Interfaces

- `acceptOrder`;
- `startOrderFulfillment`;
- `recordOrderDelivery`;
- `completeOrder`;
- `cancelOrder`;
- `authorizeOrderEntitlement`;
- `attachOrderFile`.

### Logic

- enforce source/delivery-kind-specific transitions;
- delivery entitlement returns Order truth/decision only;
- downstream Module owns its grant/booking/video/file lifecycle;
- Order completion semantics must be explicit and tested.

### UI / Administrative Surface

Participant Order progress and delivery-state actions appropriate to Offering/Gig source.

### Authorization / Compliance

Buyer/seller roles scoped. Holds may block selected transitions. Media attachments require validated MediaAsset.

### Events / Jobs / Integrations

Order events trigger delivery, payout, notification, review eligibility, rewards as appropriate.

### Failure Behavior

- downstream delivery unavailable: Order does not falsely become delivered/completed;
- duplicate completion: idempotent;
- cancellation after paid: invokes approved refund workflow rather than assuming refund.

### Tests

- transition matrix;
- participant authorization;
- delivery entitlement decisions;
- OrderFile/Media boundary;
- completion downstream event contract.

### Out of Scope

- Booking/video/download grant implementation;
- payout.

### Exit Gate

- CL-05 can consume Order entitlement without reading payment provider state;
- completion is authoritative and unambiguous under approved semantics;
- invalid transitions fail consistently.

---

# Phase 4 — Reviews and Commercial Resolution

## 10 Post-Order Review and Reputation Projection

Implement one eligible Review per completed Order and propagate publication changes to reputation/search without turning reviews into verification.

### Objective

Create trustworthy post-order reputation feedback.

### User-visible / Observable Result

Eligible buyer can submit a review; published reviews appear in Professional reputation views; hidden/removed reviews stop contributing.

### Owning Module(s)

- `review_dispute`.

### Dependencies

- Feature 09;
- explicit rating scale;
- Review actor schema ruling;
- initial publication policy;
- Professional reputation projection interface;
- Search refresh.

### Shared Operations Used

- `resolveCustomerActor`;
- `authorizeResourceAction`;
- `executeIdempotentCommand`;
- `appendAuditEvent`;
- `publishDomainEvent`;
- Search refresh public interface;
- `requestNotification`.

### Data / Schema

- `Review`;
- `ReviewStatus`;
- required actor relation/migration;
- rating constraint;
- professional target validation against Order seller.

### Public Interfaces

- `evaluateReviewEligibility`;
- `submitOrderReview`;
- `getOrderReview`;
- `listProfessionalReviews`;
- `publishReview`;
- `hideReview`;
- `removeReview`.

### Logic

- Order must meet approved review eligibility, normally completed;
- one Review per Order;
- reviewer must be Order buyer CustomerProfile;
- reviewed Professional must match Order seller;
- only reputation-eligible statuses contribute.

### UI / Administrative Surface

Review form, review list, moderation visibility state.

### Authorization / Compliance

Buyer-only submission; admin/system publication/hide/remove per authority. Review content may route to moderation but Review owns visibility status.

### Events / Jobs / Integrations

Reputation recalculation event; Search refresh; notifications/rewards consume published event.

### Failure Behavior

- duplicate submission returns existing/conflict;
- invalid rating rejected at application and DB layer;
- projection failure retries without changing Review truth;
- removed review is not privacy erasure by itself.

### Tests

- completed Order eligibility;
- buyer/seller relationship;
- rating constraint;
- one Review/order;
- publication contribution;
- Search/reputation event contract;
- never produces verification truth.

### Out of Scope

- review editing unless separately approved;
- moderation-case lifecycle.

### Exit Gate

- only authorized eligible Orders produce Reviews;
- public reputation is reproducible from Review source truth;
- hidden/removed states no longer contribute;
- no TrustBadge/VerificationCheck mutation occurs.

---

## 11 Dispute Intake and Payout Hold Coordination

Open an Order-bound dispute, establish administrative review state, and request an authoritative ComplianceHold.

### Objective

Create commercial conflict truth without creating a local financial block system.

### User-visible / Observable Result

An authorized participant can open a dispute; admin can see it in a review queue; payout-affecting stop sign is requested through the hold owner.

### Owning Module(s)

- `review_dispute`.

### Dependencies

- Feature 09;
- explicit opener actor schema;
- dispute multiplicity ruling;
- hold public interface;
- evidence-reference ruling sufficient for MVP.

### Shared Operations Used

- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `executeIdempotentCommand`;
- `requestComplianceHold`;
- `appendAuditEvent`;
- `publishDomainEvent`;
- `requestNotification`;
- Media contextual access interface for evidence.

### Data / Schema

- `Dispute`;
- `DisputeStatus`;
- approved opener relationship;
- evidence reference structure if approved;
- no local hold boolean.

### Public Interfaces

- `evaluateDisputeEligibility`;
- `openOrderDispute`;
- `getOrderDispute`;
- `listDisputesForActor`;
- `listDisputeReviewQueue`;
- `beginDisputeReview`;
- `recordDisputeEvidenceReference` if schema approved.

### Logic

- validate Order participant and dispute eligibility;
- create dispute once according to cardinality rule;
- request hold idempotently;
- ask Transaction / Order to apply disputed transaction effect through public command;
- evidence uses existing Media/Order context, not custom upload mechanics.

### UI / Administrative Surface

Participant dispute intake/status and admin dispute queue/detail.

### Authorization / Compliance

Participant/admin authority; sensitive evidence access audited; admin is not blanket file access.

### Events / Jobs / Integrations

Hold request, Order dispute-effect command, notifications, audit.

### Failure Behavior

- hold service unavailable after Dispute commit: durable workflow step retries; Dispute remains truth and visibly indicates pending coordination through workflow/ops state, not a fake hold status;
- duplicate open: replay/existing case;
- evidence file inaccessible: do not copy or expose raw object.

### Tests

- eligibility;
- duplicate/open concurrency;
- hold request exactly once semantically;
- Order dispute command contract;
- sensitive evidence authorization;
- no local ComplianceHold truth.

### Out of Scope

- refund execution;
- moderation/legal case ownership.

### Exit Gate

- Dispute can be opened and reviewed without direct Payment/Hold table mutation;
- hold coordination is retryable and auditable;
- evidence access is contextual and secure.

---

## 12 Dispute Adjudication, Refund/Release, and Closure

Implement refund-vs-release decisions and coordinate actual settlement effects across Review/Dispute, Transaction/Order, Payment/Payout/Tax, and Hold owner.

### Objective

Finish a dispute without conflating adjudication, transaction effect, financial execution, or hold lifecycle.

### User-visible / Observable Result

Admin resolves a dispute; participants see adjudication and eventual settlement completion; Order/refund/hold states are updated by their owners.

### Owning Module(s)

- Review / Dispute owns adjudication.
- Transaction / Order owns Order/refund attachment.
- Payment / Payout / Tax owns financial execution.
- Admin Review / Compliance Hold owns hold lifecycle.

### Dependencies

- Feature 11;
- explicit `resolved_*` vs `closed` semantics;
- Payment refund/release interface;
- Order refund/dispute interfaces;
- hold release interface.

### Shared Operations Used

- `executeIdempotentCommand`;
- `acquireAggregateLock`/optimistic concurrency;
- `requestComplianceHold` / `releaseComplianceHold`;
- `publishDomainEvent`;
- `appendAuditEvent`;
- `requestNotification`;
- workflow orchestration shared runner if available.

### Data / Schema

Dispute status/resolution fields; Order RefundStatus; no Payment-owned financial records migrate into Review/Dispute.

### Public Interfaces

- `resolveDisputeWithRefund`;
- `resolveDisputeWithRelease`;
- `applyOrderSettlementResultToDispute`;
- `dismissDispute`;
- `closeDispute`;
- Transaction / Order `applyRefundOutcomeToOrder` and dispute-effect commands.

### Logic

Refund path:

1. lock/validate dispute;
2. record adjudication;
3. request Payment refund;
4. Payment returns verified normalized result;
5. Order applies RefundStatus/Order effect;
6. Dispute applies settlement result;
7. hold updated/released according to policy;
8. close only when required downstream steps complete.

Release path follows equivalent owner-separated steps without pretending payout released until Payment owner confirms.

### UI / Administrative Surface

Admin adjudication controls, participant resolution status, explicit “decision made / settlement pending / settled” distinction if required by approved lifecycle.

### Authorization / Compliance

High-risk admin resolution may require step-up if root security policy says so. All decisions audited with safe reason/evidence refs.

### Events / Jobs / Integrations

Durable workflow, retries, reconciliation, notifications. Payment provider integration remains outside CL-04.

### Failure Behavior

- refund provider fails after adjudication: Dispute remains resolved decision with settlement pending according to approved semantics; retry/reconcile;
- conflicting admin decisions: concurrency conflict;
- duplicate result events: deduplicated;
- hold release failure: retry independently; never set local “released” truth.

### Tests

- refund success/failure/retry;
- release path;
- duplicate callbacks;
- concurrent resolution;
- Order/Payment/Hold contract tests;
- audit completeness;
- no direct Stripe call.

### Out of Scope

- chargeback provider lifecycle unless Payment Module separately introduces it;
- legal/moderation adjudication.

### Exit Gate

- architecture can answer separately: dispute decision, Order refund attachment, provider refund execution, hold state;
- each is owned and updated by correct Module;
- partial failures recover without double financial effects.

---

# Phase 5 — Cross-Cluster Proof and Production Hardening

## 13 Cross-Cluster Contract Proof

Prove CL-04’s major inbound/outbound contracts using owner APIs/events rather than shared database assumptions.

### Objective

Verify the Cluster works as a participant in the 10-cluster system.

### User-visible / Observable Result

Critical contract journeys pass with real/stub owner Modules and fail safely when a dependency denies or degrades.

### Owning Module(s)

- all CL-04 Modules for their own truth.

### Dependencies

- Features 01–12;
- neighboring Module contract fixtures.

### Shared Operations Used

All canonical operations actually exercised by the workflows; no new shared operation is created in this feature.

### Data / Schema

No ownership changes. Contract fixtures may reveal migrations that must go through architecture review.

### Public Interfaces

Prove:

- CustomerProfile → Gig/Order/Review;
- Professional Eligibility → response/Order gate;
- Track → Order pricing snapshot;
- Marketplace Supply/GigAssignment → Order source;
- Payment → Order outcomes;
- Order → CL-05 entitlement;
- Dispute → Hold/Payment/Order;
- source changes → Search;
- domain events → Notification/Messaging;
- Privacy → CL-04 executors.

### Logic

Run complete owner-boundary scenarios and enforce DTO/version contracts.

### UI / Administrative Surface

Playwright journeys for major customer/professional/admin surfaces where UI exists.

### Authorization / Compliance

Negative-path cross-cluster tests are mandatory: wrong buyer, wrong Professional, hold active, expired entitlement, private Media, privacy-restricted data.

### Events / Jobs / Integrations

Use real outbox/inbox/queue runner in integration environment.

### Failure Behavior

Simulate dependency timeout, duplicate event, stale version, dead-letter, and recovery.

### Tests

- contract tests;
- integration tests;
- E2E;
- idempotency;
- event ordering;
- privacy/compliance.

### Out of Scope

Neighboring Cluster source-truth implementation.

### Exit Gate

- no CL-04 test requires direct mutation/read of another Module’s internal repository to make a workflow pass;
- all critical cross-cluster contracts have positive and negative tests;
- event retry/dedupe paths are proven.

---

## 14 Security, Privacy, Reconciliation, and Production Readiness

Harden CL-04 for destructive operations, provider degradation, replay/concurrency, audit completeness, privacy/retention, performance, and deploy safety.

### Objective

Make the Cluster safe to operate under retries, concurrency, provider outages, privacy requests, and migrations.

### User-visible / Observable Result

Operators can diagnose failed workflows; privacy jobs can enumerate CL-04 data; reconciliations repair interrupted integrations; destructive migrations have rollback/backfill plans.

### Owning Module(s)

All CL-04 Modules for local truth; platform owners for cross-cutting rails.

### Dependencies

- Feature 13;
- approved retention rules for destructive erasure;
- production provider contracts.

### Shared Operations Used

- structured logs/request context;
- IntegrationFailure;
- queue telemetry;
- idempotency/concurrency;
- outbox/inbox;
- audit/access audit;
- privacy executor contract.

### Data / Schema

- indexes for primary queries;
- final constraints/backfills;
- no destructive migration without data audit, backfill, validation, and rollback strategy.

### Public Interfaces

- Module privacy target executors;
- reconciliation/admin-safe diagnostics;
- health checks for owner dependencies;
- no generic “repair by direct SQL” product API.

### Logic

- reconcile accepted assignment missing Order;
- reconcile provider-confirmed payment/refund missing Order effect through owner contracts;
- expire Gig/grants;
- recover dead-lettered projection/notification work;
- privacy export/erase/anonymize/retain according to instruction;
- verify audit and domain event completeness.

### UI / Administrative Surface

Minimal operator/admin diagnostics for stuck CL-04 workflows, without exposing secrets or full sensitive content.

### Authorization / Compliance

- sensitive admin access constrained and audited;
- telemetry redaction;
- step-up applied where root policy requires;
- retention exemptions honored;
- Search deindex requested on erasure/removal.

### Events / Jobs / Integrations

Backfills/reconciliation use resumable cursor batches, idempotent commands, rate limits, retries, dead-letter visibility, and correlation IDs.

### Failure Behavior

- poison item isolated, not infinite retry;
- destructive privacy operation blocked when retention exemption applies;
- reconciliation never overwrites newer domain state;
- provider outage produces degraded operational status without fabricating domain success.

### Tests

- security review tests;
- privacy executor tests;
- retention exemption tests;
- reconciliation idempotency;
- backfill resume;
- performance/query plans on hot paths;
- migration safety;
- full critical Playwright journeys;
- production-like webhook/event replay tests.

### Out of Scope

New product features, new pricing models, new dispute policy, new provider choices.

### Exit Gate

- all critical tests pass;
- no high-severity ownership/security/privacy findings remain;
- provider degradation and replay are demonstrably safe;
- privacy enumeration/execution is complete for CL-04 records;
- migration/backfill plans are verified;
- operator can identify and remediate stuck workflows through supported owner paths.

---

## Cross-Cluster Integration Phase

Phase 5 Feature 13 is the explicit cross-cluster integration proof. It validates contracts without pulling source truth into CL-04.

The minimum bridge set is:

```text
CL-01 → CustomerProfile / actor / authority / consent / entitlement
CL-02 → taxonomy + Search projection
CL-03 → Offering / Professional readiness / payment-payout-tax
CL-04 → authoritative demand/order/review/dispute truth
CL-05 ← Order delivery entitlement and completion collaboration
CL-07 ← communication events
CL-08 ↔ privacy/location controls
CL-09 ↔ holds/audit/moderation/ops
CL-10 ← eligible Order/Review events
```

---

## Hardening Phase

Feature 14 covers CL-04-specific hardening only:

- authorization review;
- financial/provider boundary review;
- provider degradation;
- idempotency and event replay;
- concurrent response acceptance and dispute resolution;
- Order/payment/refund reconciliation;
- Gig expiration and agreement grant expiration;
- privacy export/erasure/retention;
- audit/access-audit completeness;
- operational observability;
- query/index performance;
- backfill safety;
- destructive migration safety;
- production readiness.

It must not be used as a catch-all phase for unfinished feature logic.

---

## Phase Summary

| Phase | Name | Features |
| --- | --- | --- |
| 1 | Demand Capture and Accepted Work | 01–03 |
| 2 | Transaction Truth and Commercial Snapshot | 04–05 |
| 3 | Agreement, Payment, and Fulfillment State | 06–09 |
| 4 | Reviews and Commercial Resolution | 10–12 |
| 5 | Cross-Cluster Proof and Production Hardening | 13–14 |

**Total numbered features: 14**

---

## Phase Execution Pattern

Before each numbered feature:

1. Read required context.
2. Confirm the previous exit gate.
3. Write the feature implementation specification.
4. Confirm schemas, contracts, permissions, architecture decisions, and tests.
5. Implement only that feature.
6. Run typecheck, lint, unit/integration tests, migration checks, and build as applicable.
7. Perform workflow verification.
8. Update progress.
9. Update architecture only if a binding decision legitimately changed and was approved.
10. Record risks and deferred work.

If the next feature depends on a row in `architecture.md` Section 26, resolve that decision before implementation.

---

## Required Feature Specification

Immediately before implementation, each feature receives a concise specification containing:

- Objective;
- Observable result;
- Dependencies;
- In scope;
- Out of scope;
- Owning Module;
- Data records affected;
- Public interfaces;
- Shared operations consumed;
- Permissions;
- Primary workflow;
- UI/admin states if applicable;
- Provider integrations;
- Jobs/events;
- Idempotency/concurrency;
- Error/failure behavior;
- Tests;
- Acceptance criteria;
- Documentation updates.

Do not pre-write giant coding specs for all remaining features. The current feature should be precise; future features remain governed by this plan and architecture.

---

## Required Completion Report

After each feature, the coding agent must report:

- Feature completed;
- Files added;
- Files changed;
- Database changes;
- Migrations;
- Dependencies added;
- Shared operations reused;
- Public interfaces added/changed;
- Events/jobs added;
- Tests added/changed;
- Commands run;
- Manual/workflow verification;
- Documentation updated;
- Assumptions;
- Known failures;
- Remaining risks;
- Deferred work;
- Exit-gate result.

A feature is not complete if the exit gate is unproven.
