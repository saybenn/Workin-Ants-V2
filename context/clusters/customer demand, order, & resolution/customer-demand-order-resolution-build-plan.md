# Customer Demand, Order & Resolution Build Plan

> **Cluster ID:** CL-04  
> **Cluster:** Customer Demand, Order & Resolution  
> **Modules:** `gig_demand`, `transaction_order`, `review_dispute`  
> **Plan status:** Sequential implementation plan; architecture decisions remain governed by `architecture.md`

**Shared Operation status (CL-04-R015/R016):** exact SH IDs/names resolve to the canonical registry. SH-046 publication/outbox is Confirmed. SH-003 `queryOwnerFacts` and SH-015 `returnDecisionResult` remain Proposed ruling: use owner-specific fact/decision DTOs, not binding APIs dependent on those proposals. SH-054, SH-073, and SH-111, wherever referenced, remain Proposed ruling and conditional on separate approval. All other referenced registered operations retain their registry status and owner.

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

- Customer / Buyer Profile — SH-004 `resolveCustomerActor`;
- Taxonomy & Classification — Gig classification validation;
- Professional Eligibility — SH-016 `evaluateProfessionalReadiness`;
- Track Subscription & Entitlement — SH-005 `resolveEntitlement` and usage recording;
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

- **Gig acceptance:** single-award MVP is confirmed; transition matrices and physical enforcement design remain gated.
- **Buyer schema migrations:** CustomerProfile nullability and legacy User ID semantics.
- **Order transitions:** full transition matrix remains unresolved; commercial snapshot freezes after source/Track resolution and before Agreement execution/payment initiation.
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

- SH-001 `resolveAuthenticatedActor` — Identity & Access; resolve trusted actor; Gig supplies customer action context; do not rebuild session helpers.
- SH-002 `authorizeResourceAction` — Role / Authority; authorize create/update/publish; Gig supplies ownership facts; do not build Gig RBAC.
- SH-004 `resolveCustomerActor` — Customer / Buyer Profile; resolve buyer actor; do not treat User as sole commercial identity.
- SH-023 `validateTaxonomyAssignment` — Taxonomy; validate domain/category/tags; Gig decides whether publication requires them; no local taxonomy cleaner.
- SH-011 `evaluateComplianceHold` — Hold owner; block applicable publish/action; no local blocked flag.
- Search refresh public interface — Search owner; request projection; no Typesense client.
- SH-029 `appendAuditEvent` / SH-046 `publishDomainEvent` where policy requires.

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

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-016 `evaluateProfessionalReadiness` — Professional Eligibility owns readiness; Gig supplies `respond_to_gig` context; do not inspect raw verification/payment tables.
- SH-044 `executeIdempotentCommand` — one semantic response creation per retry;
- SH-046 `publishDomainEvent`;
- SH-041 `requestNotification`.

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
- confirmed single-award MVP rule, serialized acceptance, and approved remaining transition/enforcement decisions;
- approved Gig/Response/Assignment transition matrices;
- shared idempotency and DB concurrency;
- Professional readiness recheck.

### Shared Operations Used

- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock` or approved SH-052 `withOptimisticConcurrency`;
- SH-053 `transitionLifecycleState`;
- SH-016 `evaluateProfessionalReadiness`;
- SH-046 `publishDomainEvent`;
- SH-029 `appendAuditEvent`.

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

Emit assignment-ready event after commit. Order creation is Feature 04 and may consume the event/command.

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

**Actor prerequisite (CL-04-R007):** enforce CustomerProfile as semantic buyer identity for new records; Review authors resolve from the Order buyer and Dispute opener identity is typed. Historical backfill and final Prisma representation remain separate approval gates. No schema is changed in this reconciliation.

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

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-031 `appendDomainLifecycleEvent`;
- SH-046 `publishDomainEvent`;
- SH-052 `withOptimisticConcurrency` or approved lock primitive.

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
- confirmed freeze boundary: source/Track resolution → immutable snapshot → Agreement execution/payment initiation;
- Track public contracts;
- Marketplace/Gig base price source.

### Shared Operations Used

- SH-005 `resolveEntitlement`;
- SH-006 `consumeMeteredEntitlement` where an entitlement use is metered;
- SH-044 `executeIdempotentCommand`;
- SH-031 `appendDomainLifecycleEvent`;
- SH-046 `publishDomainEvent`.

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

**Database readiness gate (CL-04-R012):** Agreement features require reproducible migration evidence for the current Prisma Agreement family; schema presence alone is not deployment evidence. Migration-history reconciliation remains a separate database task.

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

- SH-008 `queryConsentProof` / SH-007 `recordConsentProof`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-029 `appendAuditEvent`;
- SH-031 `appendDomainLifecycleEvent`;
- SH-046 `publishDomainEvent`.

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

SH-112 `verifyAgreementDocumentHash` is internal/background integrity work, not a general public API.

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

- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- canonical hashing primitive;
- SH-030 `recordSensitiveAccess`;
- SH-029 `appendAuditEvent`;
- SH-046 `publishDomainEvent`;
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
- `issueAgreementAccessGrant`;
- `revokeAgreementAccessGrant`;
- `getAgreementPackage`.

SH-112 `verifyAgreementDocumentHash` is internal/background integrity work, not a general public API.

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

- SH-011 `evaluateComplianceHold`;
- SH-044 `executeIdempotentCommand`;
- SH-053 `transitionLifecycleState`;
- SH-031 `appendDomainLifecycleEvent`;
- SH-046 `publishDomainEvent`;
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

- SH-053 `transitionLifecycleState`;
- SH-002 `authorizeResourceAction`;
- SH-011 `evaluateComplianceHold`;
- SH-044 `executeIdempotentCommand`;
- SH-046 `publishDomainEvent`.

### Data / Schema

Order status/timestamps, OrderEvent, OrderFile contextual attachments.

### Public Interfaces

- `acceptOrder`;
- `startOrderFulfillment`;
- `recordOrderDelivery`;
- `completeOrder`;
- `cancelOrder`;
- SH-025 `authorizeOrderEntitlement`;
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

**Approved reputation handoff (CL-04-R005):** Review / Dispute owns Review inclusion and aggregate calculation. It supplies its owner-issued reputation result/facts for a ProfessionalProfile through the explicit Module contract: target ProfessionalProfile ID, derived ratingAverage/ratingCount, and source/projection version evidence. Professional Eligibility consumes that result, owns writes to its `ProfessionalProfile.ratingAverage`/`ratingCount`, and supplies the resulting Professional projection to Search. Review / Dispute must not mutate the ProfessionalProfile repository. SH-115 supplies shared projection/version/replay mechanics, not Review policy or Profile ownership. Dependency failure leaves Review truth committed and projection work retryable; exact transport/API naming is not newly selected here.

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
- CL-04-R005 Review-owned aggregate handoff and Professional Eligibility-owned rating-field consumer/write contract, available before Feature 10 integration exit;
- Search refresh.

### Shared Operations Used

- SH-004 `resolveCustomerActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-029 `appendAuditEvent`;
- SH-046 `publishDomainEvent`;
- Search refresh public interface;
- SH-041 `requestNotification`.

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

Review-owned reputation recalculation; Professional Eligibility consumes the result and persists its rating fields; Search consumes its Professional projection; notifications/rewards consume the published event.

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

- Transaction / Order Feature 08a `enterOrderDisputeState` implementation and contract tests, available before intake integration;
- Feature 09;
- explicit opener actor schema;
- dispute multiplicity ruling;
- hold public interface;
- evidence-reference ruling sufficient for MVP.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-012 `requestComplianceHold`;
- SH-029 `appendAuditEvent`;
- SH-046 `publishDomainEvent`;
- SH-041 `requestNotification`;
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

- Order dispute-entry implementation exists and the intake → Order command integration test passes; refund settlement remains Feature 12;
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
- Transaction / Order SH-108 `requestOrderRefund` contract, Payment-owned execution/outcomes, and the approved release/reevaluation interface;
- Order refund/dispute interfaces;
- hold release interface.

### Shared Operations Used

- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock`/optimistic concurrency;
- SH-012 `requestComplianceHold` / SH-013 `releaseComplianceHold`;
- SH-046 `publishDomainEvent`;
- SH-029 `appendAuditEvent`;
- SH-041 `requestNotification`;
- workflow orchestration shared runner if available.

### Data / Schema

**Mandatory durable Dispute proof (CL-04-R010):** persist the authorized adjudicator, decision, basis/reason, decision timestamp, refund amount/basis where applicable, idempotency/correlation identity, hold request/release correlation, settlement/refund correlation, and whether required downstream steps are pending or completed. This domain proof must survive retries/outages. Generic AuditEvent, QueueJob, or mutable `adminNotes` cannot substitute for it. The final decision/event/workflow persistence design remains unresolved and must be approved before production adjudication.

Order owns RefundStatus; no Payment-owned financial records migrate into Review / Dispute.

### Public Interfaces

- `resolveDisputeWithRefund`;
- `resolveDisputeWithRelease`;
- `applyOrderSettlementResultToDispute`;
- `dismissDispute`;
- `closeDispute`;
- Transaction / Order SH-108 `requestOrderRefund`, `applyRefundOutcomeToOrder`, and dispute-effect commands.

### Logic

Refund path:

1. lock/validate dispute;
2. record adjudication;
3. send the refund decision to Transaction / Order, which coordinates SH-108 `requestOrderRefund` with Payment;
4. Payment returns verified normalized result;
5. Order applies RefundStatus/Order effect;
6. Dispute applies settlement result;
7. hold updated/released according to policy;
8. close only when required downstream steps complete.

Release path follows equivalent owner-separated steps without pretending payout released until Payment owner confirms.

### UI / Administrative Surface

Admin adjudication controls, participant resolution status, explicit “decision made / settlement pending / settled” distinction if required by approved lifecycle.

### Authorization / Compliance

Refund/release adjudication that causes or authorizes financial movement requires SH-014 `requireStepUpForSensitiveAction`. All decisions are audited with safe reason/evidence references.

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

**CL-04-R014 sequencing:** owner privacy executors must exist before their Feature 13 integration proof. Gig Feature 07, Order Feature 10a, and Review / Dispute Feature 09 supply the earlier executor contributions. Feature 14 retains destructive-operation/retention safety, batching, reconciliation, and production hardening; it is not the first implementation of an executor.

### Approved local Shared Operation mappings

- SH-107 `createChargeableOrder` — Confirmed; Transaction / Order owns creation. `createOrderFromOffering` and `createOrderFromGigAssignment` are typed source-specific specializations of this responsibility, not separate creation engines.
- SH-109 `snapshotExternalDecision` — Confirmed; Order freezes external Track decision/evidence while Track retains current policy truth.
- SH-110 `createDomainSnapshot` — Confirmed; Order owns immutable source/commercial snapshots where the registered semantics apply.
- SH-026 `authorizeContextualResourceAccess` — Confirmed; the context owner decides Agreement/Dispute business access; Media retains signed transport mechanics.
- SH-125 `recordDomainAccessEvent` — Confirmed; Agreement/domain access proof remains separate from generic AccessAuditLog.
- SH-111 `renderDocument` — Proposed ruling, conditional future shared normalization; not a required confirmed dependency. Transaction / Order retains its owner-local/provider-neutral rendering workflow until separate Shared Operations approval.

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
- implemented Gig, Order/Agreement, and Review/Dispute privacy executors before their privacy contract proof;
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

**Binding retention boundary (CL-04-R011):** hard deletion of an Order must not cascade-delete retained transaction, Agreement, Review, Dispute, or domain-history evidence without owner-specific Privacy/retention evaluation. Privacy issues the instruction; each owner enumerates its targets, evaluates retention/exemption facts, erases/anonymizes eligible data, preserves/minimizes retained evidence, and returns proof to Privacy. Database cascades must not provide an alternate destructive path. Existing cascade behavior requires a later approved database correction; legal retention durations remain unresolved.

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

- hardening of the Module privacy target executors already implemented before Feature 13;
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

## WA-R003 sequencing amendment — screening source

The Offering/GigAssignment feature slices above remain marketplace slices, not an exhaustive statement of approved Order sources. Before enabling paid screening, extend source-contract validation and Order creation with the architecture's platform-facilitated screening family, then prove quote freezing, source XOR/participant constraints, semantic replay, authoritative paid-result correlation and owner-specific refund/recovery behavior. Coordinate schema changes through one migration owner. Trust check continuation follows paid outcome and required consent; payment never marks a check passed. Unsupported screening must return an explicit unavailable/unsupported result, never a fake seller or Offering.

Exit evidence: source-family contract tests reject mixed references and marketplace seller substitution; duplicate purchase requests replay; stale quotes and unavailable prerequisites cause no partial purchase/check; provider receipt alone cannot resume screening; refunded/cancelled paths use the approved Order/Trust contract. No screening implementation or migration is completed by this amendment.


## WA-R012 — Purchased session allowance and Booking cardinality (P02)

Product-owner ruling approved 2026-09-29: an Order may authorize multiple scheduled sessions **only when the purchased Offering/package explicitly includes them**. Four purchased sessions permit at most four allocated session entitlements, not unlimited Bookings. This closes U-BC-02 / CL-05-U014's product choice. Do not add uniqueness on Booking.orderId.

Supply owns the offered package description. Order validates and snapshots the purchased positive integer session allowance, source/version and applicable fulfillment/cancellation/refund terms; later Offering edits cannot change the purchase. Booking owns each appointment and its conflict, hold and scheduling lifecycle. Neither a paid flag nor counting local Booking rows supplies purchase authorization.

Technical ruling: Order owns durable per-session authorization identities bounded by the purchased allowance. An idempotent reservation command binds Order/session identity to one Booking command intent and reports authorized, exhausted, denied, or unavailable with the Order version. Concurrent attempts cannot reserve the same session twice or exceed the allowance. Booking persists the reservation identity with its local conversion; an outbox acknowledgement confirms attachment. An uncertain cross-owner outcome remains reserved until reconciliation queries Booking's durable result; never release merely on transport timeout. Failed conversion with proven absence can release its reservation idempotently. This is a recoverable workflow, not a cross-owner Prisma transaction.

Rescheduling retains the session authorization through the replacement chain and does not consume another session. A completed, cancelled or no-show appointment does not itself restore allowance or prove full Order completion. Order applies the purchased terms and owner-confirmed session outcomes; refunds and cancellation adjustments are Order decisions through Payment's rail. No automatic equal-price-per-session refund or forfeiture policy is invented. Packages cannot activate without explicit applicable terms. A normal SlotLock converts at most once (U-BC-03); that safety invariant is separate from Order multiplicity.

Implementation acceptance: four-session package permits four distinct authorizations and rejects a concurrent fifth; retry returns the same identity; single-session package remains bounded; reschedule reuses authorization; timeout recovery avoids double release/allocation; source edits do not rewrite terms; partial fulfillment does not finish the whole Order; refund/cancel outcome follows snapshotted terms. Current schema lacks this complete contract; the coordinated database pass must implement it before package activation.


## WA-R019 — Consent catalog, acceptance causation and buyer provisioning

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R019 contract](../../reconciliation/platform-architecture-rulings.md#wa-r019--consent-catalog-acceptance-causation-and-buyer-provisioning) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Consent owns an immutable version/content catalog, including consent type, version, exact content or immutable content reference/hash, locale, jurisdiction applicability and effective interval. Existing logs cannot prove an unrecorded presentation. Bind acceptance to the catalog entry and the actual rendered presentation identity/version, subject, action/context and time; preserve an immutable rendering descriptor where composition changes presentation. SH-009 selects applicable content, SH-007 stores acceptance, and SH-008 queries proof. Same acceptance command key/fingerprint replays; a new intentional re-acceptance is a new command/proof, not a uniqueness collision on User+type+version. Current-state eligibility queries use current applicable proof; Orders, screening authorizations, digital terms, redemptions and other historically binding actions preserve their specific proof reference/content-version binding. A generic audit log alone is not that binding.

Withdrawal/decline is recorded separately as an append-only disposition, not by rewriting an earlier acceptance; the consuming policy evaluates its effect. Legal re-consent/material-change obligations and retention periods are external facts. ConsentType.age_gate can prove acknowledgment only; Identity separately evaluates age eligibility. This resolves proof/catalog/retry architecture, not legal sufficiency for every category.

Customer provisioning uses the Customer owner synchronously and idempotently at the first buyer action (SH-004), with durable uniqueness on User. Optional registration-time outbox provisioning can warm the profile but never substitutes for this precondition. Customer aggregate views use the existing SH-126 Customer application facade over authorized owner queries; default to query composition, introducing a durable projection only with a demonstrated query need and invalidation contract. Legacy backfill/deletion awaits the database-evidence gate; User remains authentication identity. Tradeoff: first buyer action depends on Customer availability, but avoids an eventually missing commercial actor and duplicate local provisioning.


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


## WA-R024 — Financial readiness is action-specific

Class: **AI_RESOLVED_WITH_TRADEOFF** from the approved separation of Identity, optional screening, Professional readiness and financial execution. Preserve the existing Professional identity/KYC baseline; do not equate optional background screening with KYC. Payment's financial decision identifies the named action and the applicable KYC, tax, account and restriction dimensions, rather than exposing one timeless professional-is-financially-ready boolean.

Profile editing/drafting never requires payout readiness. Public activation/publication/Gig response uses the applicable Professional identity, Track, taxonomy/Trust/Healthcare and Hold policies; incomplete payout-account or tax setup alone is not a new universal nonfinancial block unless an explicit applicable requirement demands it. Paid acceptance/checkout must meet Payment's current charge/recipient capability for that flow; payout execution requires current recipient/account/KYC/tax/hold requirements. The purchaser cannot be charged through an unsupported recipient capability merely because a listing is visible. UI shows the owner-provided unavailable transaction state without leaking the seller's private KYC/tax details.

Tradeoff: discoverability and action readiness can differ; each attempted financial action re-evaluates current Payment facts. This avoids silently extending payout-only requirements to every public profile or treating a public listing as financial clearance. Provider/regulatory prerequisites may tighten the financial action and remain EXTERNAL_REQUIREMENT. No legal threshold, automatic KYC approval or alternative sponsorship flow is invented.

This resolves the universal-versus-action-specific architecture in CL03-HD001 / CL-03 U-01 / PE-U01 / Payment UD-01. Implement the action/dimension matrix and owner fixtures before activation; do not treat this as proof that the selected provider permits a particular charge/transfer. Existing settled optional screening and explicit free Track baselines remain binding.


## WA-R025 — Location consumer alignment and reveal evidence

Class: **AI_RESOLVED** from the binding location product ruling and canonical SH-027/028/131. U-08-13/14's product predicate/directionality is settled: exact service location is disclosed only to the authenticated Professional/provider legitimately performing the active in-person service, within its service-performance window. No buyer, Organization, Search or public-map entitlement to another party's exact location is implied. Completion ends that justification; cancellation, refund or dispute masks/revokes it. Rescheduling requires a fresh current decision. Payment, Booking confirmation or a cached flag alone is insufficient authorization.

Source Modules own their protected location facts/references. Booking's exact/fuzzy/precision/reveal fields are non-authoritative scheduling snapshots or compatibility fields; neither Booking nor Order operates a second reveal lifecycle. Location queries current typed participant, service-state, time-window and source-location facts through owners. Missing/stale/inconsistent facts deny disclosure. Each supported service context has a typed identity; an attached Booking and Order must be consistent, not arbitrarily XOR when both legitimately describe the service. A nullable context pair never permits context-free disclosure. Non-Booking source contexts require an explicitly supported service-performance contract; Job/Organization address fields do not automatically qualify.

Location stores current per-viewer/service/source decision plus immutable decision/revocation history using its owned lifecycle and SH-031 mechanism. The semantic current key includes viewer, typed service context and source reference; an owner source/policy token binds the decision. Atomically reject stale Location writes; revoke/expiry wins over a replayed old allow. Replays may reproduce proof identity but must never re-disclose exact data without a current authorization evaluation. Rescheduling updates evidence in the same owner lifecycle rather than creating a parallel reveal flag. WA-R023 requires durable sensitive-access proof before returning exact data. This resolves U-08-11/12/15/16/19 architecture; exact fields/constraints and coordinated migration remain implementation prerequisites.

Fuzzy generation uses a versioned Location policy per supported typed source, stable for the same source/policy generation. Radius/precision and refresh/expiry settings must be explicitly configured and validated before public use. Source/policy changes, privacy removal and expiry invalidate old results. SH-131 returns only current approved projection fields with source/policy version and validity; absent/stale data is unavailable, never exact fallback or read-triggered generation. Consumers use SH-028 only for generation/invalidation commands. The target-kind registry names actual source owners and validators; free-form target strings cannot broaden support. U-08-17/18 policy structure is AI_RESOLVED; numerical deployment settings are deferred configuration, and geocoder/KMS/vendor evidence is externally gated.

Acceptance: wrong viewer or source relation, absent context, Booking/Order mismatch, completed/cancelled/refunded/disputed service, reschedule, stale source/policy and delayed events, duplicate reveal after revocation, audit failure and expired public projection. Exact location remains absent from Search, notification payloads and telemetry. Legal retention/Privacy dispositions are not selected by this ruling.


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

## WA-R030 — Track catalog, enrollment, immutable grants and usage protocol

Classification: AI_RESOLVED_WITH_TRADEOFF. Track remains the commercial-policy owner; Candidate owns applications, Search owns ranking projections, Order owns transaction snapshots and Payment owns financial effects. This resolves technical representation/protocol alternatives; paid cancellation/grace and application quota product policies are explicitly separated below.

Represent free participation as an explicit Track-owned enrollment in a versioned free plan for each activated actor track, not absence of a subscription, a Stripe-created $0 subscription or a consumer-local free flag. Introduce a provider-neutral free enrollment representation; current provider default `stripe` must not label free records. Provision idempotently by User/track/profile identity. At most one current base enrollment selection exists per User/track; pending paid attempts may coexist without becoming current. Exactly one Customer/Candidate/Professional profile binding must match the selected track and User. Enforce typed FK/check constraints, user/profile consistency and current-selection uniqueness in the coordinated migration. Separate Organization ATS subject scope remains WA-R005, never a fourth AccountTrack. Historical enrollment rows remain reconstructible.

TrackPlanPrice is canonical for immutable amount/currency/billing cadence and provider-price correlation. TrackPlan.monthlyPriceCents is a compatibility/display projection and never a second price editor. A paid enrollment binds an immutable plan revision, price revision and applicable Consent proof/presentation; old enrollments and Order quotes never silently read today's edited price. Separate BillingCadence from TrackUsagePeriod. Existing monthly prices remain product truth; no new cadence, trial or price is invented. Activate a new revision only after catalog validation, retain effective intervals and prevent conflicting active revisions for the same selection key. Retiring a plan stops new enrollment, not evidence or previously authorized benefit periods. Accept conservative plan graph draft→active→retired→archived and draft→archived; archived is terminal, later publication is a new revision.

Catalog definitions are immutable typed keys with actor scope, value schema/unit, combination rule, period applicability and consuming capability. At most the designated value field may be populated and its type must equal the definition. Validate integer/money bounds, basis points and versioned JSON schemas; raw JSON is not executable policy. The initial product-backed key meanings are Candidate application allowance (15/month free, unlimited paid), Candidate employer-search boost (0 or 1500 basis points), verified-applicant plan badge and application-view insights; Customer qualifying buyer-fee waiver and early-availability eligibility; Professional commission (1000 or 300 basis points). Exact persisted key spelling is a coordinated contract constant, not a consumer-created alias. Additional unspecified premium features/ATS prices/limits are inactive catalog entries until explicitly defined; enum presence grants no benefit.

Resolve one current base plan revision, then only applicable active grant revisions. Equivalent benefits do not stack automatically. Each grant must declare an approved composition mode: extend duration, add a bounded quota, provide separately scoped value, or no additional effect for an equivalent benefit. Reject ambiguous overlap/configuration before grant activation; do not choose a winner by insertion order or a universal max/sum rule. An explicit replacement identifies the superseded grant with history. A grant never bypasses Role, readiness, Hold or source-owner eligibility. Accept grant graph active→expired/revoked/suspended/consumed; suspended→active only with authorized restoration and current validity, or →expired/revoked. Consumed is one-shot only; expired/revoked/consumed records are terminal. Append Track-owned immutable grant transitions, separate from audit and provider receipts; use a dedicated grant-history record or typed owner event table with equivalent append-only guarantees, not only mutable grant columns.

Track's Billing adapter owns subscription normalization and owner-specific provider receipts. A shared verified Stripe ingress routes by registered integration/account/resource/event purpose to Track or Payment; each owner has an independent effect receipt keyed by owner+provider-account+event ID, so one owner's receipt never suppresses the other's legitimate effect. Neither owner mutates the other's subscription/payment truth. New paid checkout starts incomplete, never default active. Provider confirmation is authenticated evidence bound to the exact attempt/price/subject. Out-of-order callbacks trigger owner reconciliation/version checks, not timestamp-only last-write-wins. Transition, immutable history and outbox commit together. Unknown financial/provider state cannot create paid access. Exact trial/grace/cancellation/downgrade benefits remain product policy, not imported from a provider enum; this ruling does not enable them.

Usage is an owner protocol: versioned period policy supplies a durable period identity/start/end/timezone; subject+track+entitlement+period policy/version identifies the counter across free/paid plan switches. Switching plans or provisioning another record never resets same-period consumption. Keep the counter rebuildable from immutable accepted consumption and compensating events. No destructive monthly reset or consumer-local quota. Semantic key binds source owner, source command/logical action, subject and entitlement; same key/fingerprint returns the same receipt, different payload conflicts. Quantity and policy revision persist with the receipt. A correction references the original event, is authorized by the source/Track policy and can compensate once; withdrawal or a monetary refund is not automatically a usage reversal. The actual monthly boundaries and withdrawal policy still require the product ruling identified in the decision packet.

For Candidate application submission use durable reservation/commit/reconcile, not foreign repositories or a distributed database transaction. Candidate first validates subject/Job eligibility and creates a stable submission intent. Track atomically reserves allowance and returns reservation/period/policy proof. Candidate commits the application once with that reservation, then emits a durable confirmation; Track converts the reservation to consumption idempotently. A duplicate source submission returns the original application/receipt. In-flight reservations reduce remaining capacity. On timeout query the Candidate submission outcome; release only on proven non-commit or owner-confirmed cancellation that prevents later commit. Unknown remains reconcilable, never silently free capacity. Withdrawal after successful commit follows the separately approved quota policy. Background cleanup cannot free a reservation while an application can still commit against it. This protocol is FOUNDATION_CAPABILITY, not full CL-01 maturity.

The approved Candidate subscription boost is non-metered effective ranking metadata, not a billable impression/application event. Search applies a 1.15 multiplier to its nonnegative base relevance/quality score only after all audience/eligibility/privacy filters; zero remains zero and deterministic ties use the normal stable tie-breaker. It is not a guarantee of 15% more views or permission to enter a protected result set. No `candidate_search_boost_applied` usage debit is enabled merely because the enum exists. Bound the projection to Track evidence/version and refresh on effective benefit change; stale or unavailable paid-boost evidence cannot silently confer a bonus. Earned separate boosts require their explicitly approved combination rule.

Fee/commission quotes carry integer basis points, currency, applicable basis identifier/amount, policy/plan/grant revisions and evaluation time. Order freezes the quote at its approved pricing/acceptance boundary. Use checked integer minor-unit arithmetic with deterministic round-half-up for nonnegative fee/commission calculation; sum the persisted rounded line allocations to the total and distribute any explicitly required remainder deterministically by stable line identity. Never use binary floating point or recompute old orders from current rates. Tax's jurisdiction-specific rounding remains Tax policy. A missing approved fee basis/eligibility policy is unavailable, not an invented charge. Payment consumes the Order-authorized monetary result, not a second Track fee calculator.

Required validation before activation: free/paid concurrent selection, wrong profile/actor binding, price revision change, typed value mismatch, ambiguous grants, grant restoration after expiry, duplicate/provider cross-owner event, quota contention/plan switch, crash before/after Candidate commit, unknown reservation outcome, duplicate compensation, stale boost and exact price rounding vectors. Schema/runtime proof remains unperformed at this architecture checkpoint.

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

## WA-R032 — Approved subscription benefit periods and Candidate quota (P12/P13)

Binding product-owner ruling, 2026-10-01 America/New_York. Supersedes P12/P13 open alternatives; WA-R030's owner boundaries and durable reservation/history design remain binding.

Cancellation or voluntary downgrade takes effect at the end of the already-paid subscription period. Premium benefits remain active through that paid-through time. Failed renewal creates no unpaid premium grace at launch. Provider retry/recovery may continue, but premium benefits end at the previously paid boundary unless payment is successfully recovered. Later recovery may resume benefits within the valid renewed entitlement period; never fabricate retroactive usage rights. Return to the applicable free-track policy when premium entitlement ends.

Existing purchase, Order, Booking, digital-access and other rights validly acquired while premium are not revoked merely because the subscription ends. Their owning Module/policy determines continuing rights. Subscription change cannot reprice an accepted Order, cancel an accepted Booking or revoke a purchased download by itself. End only the current subscription-derived benefit. No automatic free trials, subscription pauses or automatic prorated cancellation refunds at launch. Refunds follow approved refund policy rather than cancellation implying a refund. Core account/security access is never paid-only.

Track separates provider billing/recovery state from effective benefit intervals. A cancel request records scheduled end plus immutable intent/history; it does not set present benefits to false. Verified payment evidence binds a specific enrollment/price revision and paid interval. Query-time evaluation enforces interval boundaries even if the expiry worker is late. Past-due/retry state alone cannot extend the paid-through interval. A late recovered payment records the valid new interval and observation/activation time; effective resumption starts no earlier than verified recovery and never reauthorizes denied historical actions. Duplicate receipts cannot extend a period twice. Terminal or expired enrollment history is preserved; renewed access is an explicit versioned entitlement selection, not history overwrite. Paused/trial enum values remain unsupported launch transitions. Payment truth, retries and Track entitlement evaluation remain separate owners.

Free Candidate users receive 15 successful application submissions per UTC calendar month. Consume one quota unit only when one logical submission succeeds and is durably accepted into Candidate's application workflow. Failed attempts, retries, duplicate transport and rejected technical writes consume zero. Later Candidate withdrawal, employer rejection or any downstream application outcome does not restore a consumed unit. A proven technical duplicate/error is corrected by an authorized append-only adjustment referencing the original, not by deleting usage history.

Persist successful monthly usage for every Candidate submission, including while Premium is unlimited. The effective unlimited plan bypasses the numeric cap, not usage recording. On return to Free within that UTC month, available allowance is max(0, 15 minus already-recorded successful monthly usage), including Premium-period successes. Plan changes cannot reset counters, duplicate usage or create another 15. Calendar boundaries are half-open [first day 00:00:00 UTC, next first day 00:00:00 UTC); the owning Candidate durable acceptance timestamp selects the month, not the client clock or delayed outbox delivery time. Preserve policy revision, source intent/application, accepted timestamp and consumption identity.

For a submission spanning a month boundary, Track's capacity reservation must cover the month in which Candidate commits acceptance. Candidate must not commit against an expired prior-month authorization: renew/rebind the reservation under the new period, check the current plan/remaining capacity, then durably accept once. Store the resulting period proof with acceptance. At the period boundary, use a server-authoritative time/transaction guard and reconciliation so cleanup cannot release a reservation still eligible to commit. Unknown outcomes remain reserved until reconciled; failed/noncommitted work consumes zero. Successful unlimited submissions still produce idempotent consumption evidence without denying submission for exceeding 15. A late confirmation applies to its proven acceptance month, never the arrival month.

Required implementation checks: cancellation before paid end; failed renewal at boundary; recovery before/after boundary; duplicate recovery; preserved purchased rights; no retroactive authorization; 15/16 simultaneous Free submissions; failed technical writes; duplicate receipt; withdrawal/rejection without credit; Premium submits above 15 with recorded usage; downgrade with zero remaining allowance; period-boundary submission and delayed confirmation. These are acceptance requirements, not claims of runtime execution.

## WA-R033 — Taxonomy semantics, history and AI proposal boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Taxonomy owns canonical term meaning and validation; contextual owners own accepted assignment joins. Join `verified` means an explicitly recorded authorized classification review, never Trust/KYC/Healthcare verification. Mere accepted attachment is not reviewed verification. Do not infer reviewed=true for legacy rows with unknown provenance; preserve them as unknown/unreviewed pending owner correction. Store reviewer/action/evidence/version when review is asserted. AI confidence is nullable integer basis points 0..10000 on the proposal, with model/prompt/output-schema/version provenance; it is model confidence, not calibrated correctness or authority. User/admin-authored assignments have no fabricated confidence. Accepted joins may retain a proposal reference and immutable provenance snapshot, but confidence never becomes a permission gate or competing current score. Legacy Float values are not auto-rescaled without proving their source scale. Candidate-authored tags use TagSource.user with CandidateProfile/User attribution; no new candidate source enum is required.

Adopt no normal hard-delete command for Domain/Category/Tag. Effective activity includes every ancestor's activity; ancestor reactivation does not rewrite child records. New assignments require effective-active terms. Historical accepted assignments retain term/version evidence even if the term later becomes inactive. Existing boolean active/inactive is sufficient for that lifecycle. A Tag must match the target's declared accepted Category at launch; multi-category assignment requires an explicit versioned compatibility policy, not arbitrary cross-category attachment. Parent IDs are immutable through ordinary edits. Exceptional reparent/merge runs require preflight affected-owner enumeration, compatibility review and controlled migration, never foreign join writes.

Persist immutable Taxonomy revisions/change records for labels, hierarchy, activity and represented compliance-trigger facts. Use stable term IDs and monotonically advancing owner revisions; updatedAt plus generic Audit is insufficient for historical interpretation. An alias points to exactly one stable canonical term within the same domain/type/locale normalization scope; alias cycles and conflicting normalized keys reject. Merge creates a durable from/to/version decision and alias/retirement mapping, preserves the source record, and requests each contextual owner to revalidate/repoint its own references with expected versions. Preserve original term/version in historical decision snapshots. Do not declare merge complete until required owner acknowledgments reconcile. No generic cross-owner migration service owns assignments.

Normalize term comparison keys using an explicitly versioned Unicode NFKC plus full case-fold and trimmed/collapsed Unicode whitespace; preserve punctuation and diacritics rather than conflating legally distinct terms. Include normalized locale and parent/type scope. Labels remain original display text. Alias registration is explicit, not automatic semantic synonym generation. Detect collision before creating or upgrading a normalization version; an algorithm change requires a dry-run collision report and owner migration. Slugs are owner-scoped stable public identifiers: use the shared primitive, uniqueness constraints and deterministic collision suffix; label edit does not silently rename an existing slug. Historical redirects/aliases are explicit owner records. Exact approved production seed content is an external reference-data requirement; no invented vocabulary is approved by this mechanism.

Additional license/background/location/Healthcare triggers use a versioned mapping owned by the interpreting requirement owner (Trust, Healthcare, Location or Job Compliance), keyed to Taxonomy term/revision and supported action/jurisdiction. Taxonomy supplies represented facts and change references, not clearance. Absent unsupported mappings do not imply readiness. DataSensitivity vocabulary follows Ubiquitous Language/compliance authority; source owners classify their own data and Healthcare separately owns explicit Healthcare boundaries. No generic scanner/AI inference can clear a sensitivity label.

Adopt the AI owner's two-record design: AiClassificationLog for a run and AiSuggestion for proposals, with append-only transition evidence. Run identity binds target owner/type/id/source version, allowed purpose, requester, model/prompt/normalization/output-schema versions and a semantic command identity. Keep queued→running→completed/failed/cancelled; queued may cancel. Cooperative cancellation prevents any late response from applying, even if provider work cannot be stopped; record late attempt outcome separately. Terminal runs never reopen; rerun is a new explicitly authorized run. Suggestions have unique run+candidateKey, exactly one value shape, and proposed→accepted/rejected/superseded/invalidated. Accepted requires a durable contextual-owner mutation receipt, never provider confidence or reviewer intent alone. Accepted/rejected dispositions are immutable; later assignment changes belong to the contextual owner.

Initial AI targets are ProfessionalProfile, Offering, Organization, Job and CandidateProfile; purposes are taxonomy_suggestion and skill_extraction. Gig AI is deferred because no bilateral target contract is established; ordinary Gig taxonomy assignment still works. Existing active canonical IDs only for taxonomy suggestions. Novel terms remain review-only and cannot be created by accepting an AI suggestion; independent authorized Taxonomy creation follows ordinary validation. Store logical term ID plus immutable term revision/label/path snapshot validated by Taxonomy; no cascading FK from proposal deletion into accepted truth. Keep normalized suggestions, validation result, canonical output hash and minimal provenance, not full raw provider bodies or source text. Provider/legal retention remains external; deleting AI evidence never deletes accepted assignments.

Use immutable code/config prompt versions with hashes at launch; no new database prompt publisher or first-class AiBackfill business model without a real additional lifecycle requirement. Bounded per-target runs and shared queue checkpoints suffice. Source adapters return purpose-limited normalized approved fields; Candidate supplies normalized skills/experience categories, never raw resume/application text at launch. Healthcare-sensitive transmission is disabled until source/Healthcare purpose-specific authorization and qualified provider/BAA evidence exist. No fallback model, region or logging change may silently widen the approved data boundary. Bedrock model/account/region/logging/retention configuration is external activation evidence, not selected by this architecture ruling.

Contextual owner commits accepted assignment and an immutable acceptance receipt/outbox fact atomically after fresh Taxonomy and source-version checks. AI consumes the receipt idempotently to record disposition; a timeout queries the contextual owner receipt rather than repeats the mutation with a new key. This is recoverable choreography over owner truth, not a generic CL-02 saga. Taxonomy admin composition may display proposal evidence and route assignment decisions through the actual context owner; shared review leases use WA-R031 and do not confer approval. No baseline AI→Search proposal feed or end-user classification notification. Broad backfill/configuration/merge and sensitive evidence exports require registered Role actions and fresh step-up under WA-R023/031; low confidence never creates a Hold by itself.

Required implementation checks: confidence source/range, unaudited verified claim, ancestor inactivity, normalization collision, alias cycle, stale assignment/term version, merge owner failure, late cancelled response, disposition-before-mutation rejection, duplicate acceptance receipt and raw/sensitive provider input rejection. Physical migrations, per-target DTO field allowlists, approved seeds, legal retention and provider capability are still separately qualified before activation.

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

## WA-R035 — Supply lifecycle, history and source projections

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

This ruling supersedes the proposed/unresolved lifecycle and projection alternatives named below; implementation still requires forward schema coverage and contract fixtures. Professional graph: create→draft; draft→active after current activation readiness; active→paused; paused→active after current readiness; draft/active/paused→suspended only by an authorized source restriction; draft/active/paused→archived by owner-authorized retirement. Archiving a suspended record may record retirement intent but cannot remove the restriction. Archived→draft is an explicit owner restore command, never implicit activation. Suspended→draft requires authorized release of all applicable restriction sources; subsequent activation rechecks readiness. Preserve previously acquired transactions and obligations. Ordinary dependency loss invalidates the affected action/public decision and requests reevaluation, not an automatic Profile status change. Only an explicit source policy may instruct suspension.

Offering graph: draft→active by publish; active→paused; paused→active by resume, each activation requiring current composed gates. Draft/active/paused may enter under_moderation/disabled_by_moderation/disabled_by_dmca only from a valid Moderation decision. Those restriction states may change to another restriction state only with a superseding valid decision. Restriction clearance restores to draft, preserving all other restriction sources; publication is a separate fresh command. Rejected→draft is an explicit correction/resubmission command after the rejecting owner permits it. Draft/active/paused/rejected→archived; archived→draft by explicit restore. Retirement never clears restrictions, destroys Order snapshots or grants a refund. An Offering kind can change in draft only before any Order, delivery or durable external reference; otherwise create a new Offering. isPublic is seller publication intent; effective visibility additionally requires active lifecycle, current SH-024 decision and no applicable restriction. Moderation timestamps are evidence, not independent allow flags.

Adopt immutable owner lifecycle histories for ProfessionalProfile and Offering, with aggregate version, prior/next state, command/source decision identity, actor, timestamp and policy/decision references. Mutations commit history and outbox atomically using expected opaque version plus row serialization for competing transitions; updatedAt alone is not the concurrency token. Publication/activation and seller Order acceptance retain immutable minimized gate decisions/source versions; current actions still reevaluate. Legacy financial/Trust columns remain non-authoritative compatibility projections until a measured reader inventory and forward migration remove them; never backfill authoritative readiness from a legacy boolean.

onboardingCompleteAt is the first successful owner activation after required onboarding facts pass, immutable except an audited data correction. It is not current readiness. ProfileCompleted.v1 may qualify one Gamification rule per profile and rule revision, containing profileId, subject User reference, firstCompletionAt, aggregateVersion, eventId; no raw onboarding facts. Gamification decides awards and source-event dedupe. Reinstatement does not emit another first completion. Dependency changes are owner outbox facts carrying target, changed dimension and source version; Professional/Supply consume idempotently and reevaluate current truth. Do not propagate a copied allow decision indefinitely. Booking availability is not an eligibility prerequisite; a public availability presentation uses Booking's separately authorized query and never changes Professional status.

Public Professional projection allowlist: professionalProfileId, slug, display name, approved biography, accepted active taxonomy IDs/labels/revisions, owner-supplied public avatar rendition reference, Review-owned ratingAverage/ratingCount with reputation version, and SH-131 fuzzy public location when allowed. Public Offering projection: offeringId, professionalProfileId, slug, title, approved summary, kind, accepted taxonomy IDs/labels/revisions, current public pricing summary/currency, approved public rendition references and public delivery/location mode. Each includes sourceVersion and current public-readiness evidence. Exclude User IDs, contact details, exact location, credential documents, provider refs, financial/Healthcare/hold reasons. Search must obtain URLs through approved Media/public rendition rules; no private original URL. Review→Professional transport is an outbox-triggered owner query getProfessionalReputation.v1 returning profileId, ratingAverage, ratingCount, projectionVersion, then a version-checked Professional projection command; stale events trigger current query rather than regress values.

priceFromCents is a rebuildable minimum of currently eligible active pricing options in one currency, not purchase truth. Missing or mixed-currency options produce no priceFrom value, never zero/implicit conversion. Orders bind the selected immutable price/package. isFeatured has no ranking or commercial effect at launch; promotion is deferred pending a separately approved owner policy. Heterogeneous bundle Offering creation remains disabled; this does not disable P02 multi-session packages within supported kinds. No new seller entitlement gates: supported effects remain approved Professional commission terms; unknown keys cannot gate drafting or fabricate quota. SH-016 action keys are activate_profile, public_visibility, publish_offering, respond_to_gig, participate_in_order; payout stays Payment-owned.

Owner status/remediation notifications use committed source-event identity, generic status/remediation template and safe authenticated destination; no sensitive provider/Healthcare/hold details. Notifications do not prove readiness. No generic admin force-ready override: each source owner must authorize and record its own correction, followed by reevaluation. Required verification includes stale-resume versus restriction, archive/restore preserving obligations, projection field exclusion, duplicate first-completion award, and reputation version replay. These are implementation acceptance criteria, not tests already executed.

## WA-R037 — Payment effects, payout reservation and tax evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Payment owns immutable financial operation and attempt history, not just outbox delivery. Every effect has unique owner/sourceType/sourceId/sourceRevision/effectKind/effectOrdinal plus currency, semantic payload hash and original-effect reference for compensation. Reuse with different amount/subject/currency conflicts. Verified provider ingress receipt is separate from Payment and Track effect receipts; route by approved provider object/metadata ownership, never both owners applying the same business effect. Unknown routing is quarantined. Payment receipt fields: provider/account/eventId, eventType, fingerprint, handlerVersion, target operation, receivedAt, processing/attempt/recovery state and committed effect references. No raw secret payload by default; legal retention remains externally supplied.

Balance accounting uses immutable signed minor-unit effects with explicit bucket vectors and per-currency conservation. Earnings credit available (or pending until the approved availability rule); payout reservation moves available -A/reserved +A atomically with request acceptance; reservation release moves reserved -A/available +A only once after known cancellation/failure with no possible pending provider movement; successful payout moves reserved -A/paid +A. Transport retries have zero ledger effect. Provider return/reversal records its actual returned amount as a new linked effect, paid -R/available +R only after verified return and applicable financial restrictions; it never mutates the original payout. Fees/refunds/chargebacks are separate authorized signed effects, never hidden in payout status. Unknown money movement retains reservation and reconciles. Existing one-amount enum records are insufficient to infer these vectors: use an explicit owner allocation/bucket effect structure and forward constraints. This is accounting of processor-held value, not permission to introduce a wallet or new financial product.

At launch each PayoutTransfer belongs to one PayoutRequest; Order references are optional immutable allocation provenance, not a second transfer source. A request supplies an explicit validated active payoutAccountId; no guessed default among multiple accounts. Capture all blocking Hold IDs and decision versions in a separate immutable evaluation snapshot; blockedByHoldId is explanatory only. Reevaluate current holds/account/financial readiness immediately before dispatch. Keep one semantic transfer identity and stable provider idempotency key through network retries. Record each transport attempt separately. A terminal failed transfer never reopens; a new request/transfer after confirmed nonmovement and reservation release requires fresh authorization. Unknown is nonterminal even if transport timed out. No automatic retry of a terminal financially reversed/paid transfer.

Ratify the minimum Payment §9 graphs with these restrictions: KYC rejected/expired/disabled attempts are terminal; new attempt linked to previous evidence. TaxProfile rejected/expired creates a new collection revision, never overwrites submitted documents. One current applicable selector per subject+purpose+jurisdiction/provider scope points explicitly to the accepted evidence; pending new evidence does not silently replace valid current proof, while revocation immediately invalidates it. PayoutAccount disabled is terminal for that account; restriction recovery uses verified current provider evidence. PayoutRequest failed/cancelled/reversed terminal; processing cannot cancel without proven no movement. PayoutTransfer failed/cancelled/reversed terminal. SalesTaxCalculation changed quote requires a new calculation; finalized is immutable, voiding is a separately evidenced provider operation. Tax submission rejected/failed uses a new linked submission revision; transport retries of an unacknowledged submission retain semantic identity. Filed recipient correction creates replacement evidence and a link, preserving prior filing. No enum setter or provider callback bypasses these rules.

Tax subject is a Payment-owned stable subject reference mapped to an identified legal recipient, with explicit User and optional ProfessionalProfile provenance; profile identity is not automatically a separate legal taxpayer. Effective mappings/versioned evidence prevent accidental subject merge. Aggregate key is taxSubjectId + jurisdiction + taxYear + currency + reportingRegime; retain source owner/id/revision/recognition type and unique reversal identity. Prize-owned summaries use the same dimensions and preserve their own source valuation truth. SH-019 supports an explicit tax_fulfillment purpose and tax dimension; no second generic tax-readiness service is needed. Payment owns TaxReportingSubmissionStatus and TaxReportingRecipientStatus. Reporting bundle uniqueness includes regime/jurisdiction/year/currency/submission series/revision; recipients unique within submission by tax subject and applicable form/category. Rule versions, form requirements, recognition dates, thresholds and correction legality remain approved external configuration, never invented constants.

Order binds final calculation ID to exact immutable quote/order revision, currency, line IDs and buyer-tax-location evidence revision. Payment preserves line-level taxable basis, tax, jurisdiction, provider tax code and liability role even for mixed-liability lines. Tax-location provenance includes approved source owner, source/evidence revision, validation method/result and captured/effective time, minimum required location fields; it is not public-location consent. Each authorized refund has immutable line allocations against the original captured quantities/basis/tax and links its own provider refund and tax reversal attempts. Cumulative refunds cannot exceed captured refundable allocation; lock the operation allocation counters and reject mismatched currency. Use deterministic minor-unit residual allocation only within an approved tax/provider allocation policy; do not guess rates or liability. Partial/multiple refund representation requires separate child records, not one overwritten reversalId. Provider unsupported/ambiguous results stay pending/manual review, never fabricated successful tax reversal. Full provider/rule qualification remains external before affected execution.

Required verification: concurrent reservation conservation, duplicate callback/compensation, timeout followed by paid result, multiple holds, account changes before dispatch, line-level cumulative refund cap, subject/jurisdiction separation, replacement filing traceability. No live financial test or migration is claimed by this architecture decision.


## WA-R039 — Gig award and Order outcome boundary

Apply the scoped WA-R039 contract in `context/reconciliation/platform-architecture-rulings.md`: Gig serializes one current winning assignment and retains immutable accepted proposal/terms and lifecycle history; Order binds its source revision and remains purchase/completion truth. Booking/delivery facts cannot independently finish a multi-session purchase. Review case cycles preserve completed work history and cannot replay financial effects. Gig consumes only the authorized current owner outcome; a closed dispute is not an automatic restoration instruction. P14/P15 response revision and loser-disposition choices remain open, so the full Gig acceptance contract is not frozen. No schema/runtime completion is claimed.

Sequence owner history and coordinated winner constraint/source DTO before acceptance integration. Verify competing awards, revise/withdraw races, altered-payload replay, partial-session completion, stale outcomes and repeated dispute cycles. Do not activate loser disposition or response-edit eligibility until P14/P15 is approved and applied. Database provenance and forward migration/replay remain separate gates.


## WA-R040 — P14/P15 approved

 received 2026-10-02. Supersedes WA-R039's open P14/P15 recommendations.

Professionals may revise active submitted, viewed or shortlisted proposals until accepted, rejected or withdrawn. Preserve immutable revisions. Material changes to price, scope, timing, included work or other acceptance-relevant terms must be visibly identified to the Customer. Viewing or shortlisting does not lock the proposal.

Acceptance binds an immutable snapshot of the latest revision actually presented for acceptance. The request carries that presented revision and terms fingerprint; under the Gig award lock compare it with the current proposal revision. If it changed, reject stale acceptance and require presentation of the new terms. Never silently substitute unseen newer terms. Accepted proposal terms cannot be rewritten by proposal editing; changes go through the owning Order/agreement/change workflow.

When a single-award Gig selects its winner, automatically reject other active submitted/viewed/shortlisted proposals with canonical reason ANOTHER_RESPONSE_SELECTED. Preserve records and immutable histories; leave previously terminal responses unchanged. Award, capacity exhaustion, rejection decisions and outbox effects commit under one serialized owner transaction so concurrent edits/submissions/acceptance cannot escape the closed award capacity. Retries reproduce the same effects. Notification delivery occurs after commit and is idempotent per source transition.

Launch capacity remains one. This rule is defined at award-capacity exhaustion; a future explicitly approved multi-award Gig must reject remaining active proposals only when its remaining capacity is exhausted. The launch unique-winner constraint is a launch implementation constraint, not a permanent prohibition on a future approved capacity model. No multi-award feature, re-award or cancellation-driven reopening is activated by this ruling.

Required implementation checks: edit after viewed/shortlisted; visible material-change marker; acceptance of presented current revision; stale presented revision conflict; edit-versus-accept serialization; accepted terms immutable; winner plus loser rejection consistency; concurrent submission after exhaustion denied; replay without duplicate effects; terminal proposal preservation; future capacity-policy test proving rejection is conditional on exhaustion. These are acceptance requirements, not executed runtime evidence.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P16

A Professional may report completion or no-show for an authorized service session. Authorized support may confirm, correct or adjudicate the service-performance state where policy permits; the Customer can contest the report. Preserve immutable report/correction history, reporting actor and authority, occurrence/recorded time, evidence references, affected session and which participant allegedly failed to attend. A correction references the original; it does not erase it. Reported outcome and contested/adjudicated status are distinguishable, so a Professional assertion is never represented as independent support verification.

Completion/no-show status alone must not automatically trigger refund, charge, payout release, forfeiture, review eligibility or any other financial consequence. Order, Payment/Payout, Review/Dispute, Booking and the applicable policy owner each evaluate their owned consequences from current authorized evidence. A single session report never proves full multi-session Order completion. Clock passage does not fabricate a performance report.


### P19

Booking and participant-facing Dispute discussion associated with the same Order reuse that Order's conversation. Context labels/session/case references aid navigation, but do not create duplicate buyer/seller threads. Messaging resolves the canonical Order thread and current membership through its public interface; source owners supply authoritative context and participant facts. Reuse does not automatically enroll a reviewer/support actor or expose unrelated history.

Private adjudication notes, reviewer deliberation, restricted evidence, internal support/moderation material and decision-making records remain separate from the participant conversation under their owning access/audit boundaries. No generic attachment forwarding or notification may leak those records into the thread. Sharing a conversation transfers none of Booking, Dispute, Messaging, Moderation or Order lifecycle ownership.


## WA-R048 — Order, Agreement and Gig outcome contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Implement the architecture contract below only after the coordinated forward schema and concrete owner/consumer contract tests exist. This is sequencing and acceptance criteria, not implementation-completion evidence.

Order is the only commercial transition owner. Adopt the following guarded transition contract; status names cannot replace predicates and the older conceptual paid-before-seller sequence is superseded. Creation starts draft from a validated immutable source DTO. A source-specific `agreementRequirement` contains required/not-required, requirement policy revision, and (when required) an approved template key/version; missing requirement evidence blocks checkout rather than defaulting to no Agreement. Marketplace supplies Offering requirements, Gig supplies accepted assignment requirements, and screening uses its approved separate source contract. Order selects the applicable approved requirement; it cannot create legal applicability from an enum.

| Current state | Command/fact and required guard | Result |
| --- | --- | --- |
| draft | immutable source/pricing ready; Agreement required | awaiting_agreement |
| draft / awaiting_agreement | no Agreement required or required execution ready; seller decision still required | awaiting_seller |
| draft / awaiting_agreement / awaiting_seller | required Agreement ready and P11 acceptance proof valid; capture not confirmed | pending_payment |
| pending_payment | Payment confirms exact authorized capture effect for frozen purchase | paid |
| paid | owner verifies current source, required Agreement and retained seller acceptance proof | accepted |
| accepted | authorized fulfillment-start command with current delivery gates | in_progress |
| accepted / in_progress | delivery-kind owner supplies qualifying delivery evidence | delivered |
| delivered | Order evaluates all purchased obligations and applicable completion policy | completed |
| any nonterminal operational state | authorized Order cancellation under applicable policy, with financial obligations separately reconciled | cancelled |

Authorization/hold of funds before acceptance is permitted by Payment architecture, but never advances paid or permits final capture without acceptance. Published digital fulfillment may advance accepted→delivered when the authoritative Digital Goods delivery predicate is satisfied; it cannot skip entitlement, policy or verification. Session completion/no-show reporting under P16 is input evidence only. Neither receipt nor session count alone manufactures an approved completion policy, review eligibility or financial action. For multi-session purchases, the frozen package defines obligations and Order evaluates them all. No timer, cancellation deadline, refund eligibility or seller-decision timeout is invented here.

A durable dispute cycle is an overlay on the last operational state, including completed/cancelled. If the legacy disputed status is exposed, retain that underlying state and case/cycle/source version explicitly. Opening or closing a case never reruns capture, refund, payout or fulfillment. Closure applies only an explicit current authorized disposition: continue the still-valid underlying state; cancel remaining fulfillment when authorized; or apply a verified refund outcome. A partial refund updates cumulative verified refund allocations without automatically cancelling unrefunded obligations. Fully refunded is a monetary outcome only after Payment confirms the full eligible captured amount; continuing access/fulfillment disposition is independently owner-authorized. Completed/cancelled history is never erased or silently reopened; correction is an append-only outcome revision. Refund reversals require a distinct authorized Payment effect, never subtraction by replaying an old event.

Retain one durable Agreement container per Order. Under it, use immutable execution revisions linked by supersedesRevisionId, each binding frozen source/pricing, approved template version, required signer set, exact document snapshot and contextual consent/signature evidence. Existing AgreementDocumentSnapshot.version is document identity, not sufficient by itself to represent execution revision identity. A correction creates a new execution revision with fresh applicable consent/signatures; previous signatures cannot be copied as acceptance. Buyer Customer and seller Professional are the supported marketplace signer roles; candidate/organization-member enum members remain reserved. Screening cannot fabricate a seller signature. Generated→consent_pending/pending_signatures is guarded by its requirements; individual signature receipts progress the revision only for the required signer against the same document; all required signatures and exact-byte finalization produce fully_signed. Void/supersede/archive preserve evidence. Expiry/manual execution remain disabled unless their approved policy/procedure is available. Template draft→active requires approval; active→retired prevents new selection; retired→archived retains historical resolvability. Editing an active template creates a new version.

Order's provider identifiers are correlation-only projections of Payment-owned effects. `stripeTransferId` is read-only legacy correlation, never transfer truth or a dispatch instruction; a collection of Payment operation/effect references represents multiple transfers/refunds. Normalized Agreement signature/document records own proof; buyerSigUrl/professionalSigUrl/pdfMediaId/finalDocumentHash are compatibility mirrors only, checked against authoritative records and never fallback authorization. Database migration must inventory readers, backfill or quarantine conflicts, then remove redundant writers; preserve history, no destructive reset.

Gig post-award outcomes consume this Order contract: accepted assignment→delivered only from matching Order delivered; accepted/delivered→completed only from matching Order completed; accepted/delivered→cancelled only from an authorized matching Order cancellation. A completed assignment retains completion history even if a later financial adjustment/dispute occurs. Gig assigned→completed/cancelled projects the matching terminal assignment; the winner slot remains occupied and no re-award is implied. Partial refunds and Booking reports cannot directly mutate these projections. Reject stale source versions; atomically record event/effect identity and history. A recovered missing event may advance directly to the verified latest outcome while preserving its source lineage, not fabricate intermediate performance.

Verify source-specific Agreement requirements, seller acceptance before capture, conflicting Agreement revisions, old-signature replay, partial package fulfillment, contested no-show, partial/full refund separation, dispute closure without effect replay, cancelled winner retention and out-of-order completion. Physical revision/source/actor constraints and migration replay remain implementation prerequisites.


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

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Gig participates in owner enumeration/assignment receipts, while AI support remains disabled under WA-R033/070. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## WA-R071 — Purpose-specific Location facts and disclosure — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Order supplies current service/session/participant/restriction facts to Location, which remains the sole reveal owner. Booking/Order mismatch or unavailable facts denies disclosure; public events never include exact location. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## Domain bridge qualification — 2026-10-15

For WA-R077; WA-R079; WA-R080, sequence the relevant owner contract/DTO fixtures, shared durable mechanism qualification and bilateral negative/replay/currentness checks before dependent consumer activation. Use the exact Module architecture ports and source scopes. Database posture D and policy/provider requirements gate their affected slices; no broad product implementation or parallel lane is authorized by this reconciliation. R079 creates no required Order-to-Sweepstakes dependency. Do not treat a successful queue dispatch, enumerator page or provider response as completion of the originating lifecycle.

## WA-R081–083 — Integrated bridge sequence

Follow Module owner contracts and the complete bridge inventory before cross-Cluster integration. CONTRACT_ONLY work may establish schemas/fakes; FOUNDATION_CAPABILITY is required before actual effects; executable bilateral and external evidence precede freeze/activation. R081 named queries/receipts, R082 Media invalidation, and R083 disabled optional paths supersede only the corresponding historical open labels. Keep current source checks at action/disclosure boundaries. Do not begin whole-Cluster parallel work, root synthesis or runtime implementation from source-coverage counts alone.

## WA-R084 — Order/Payment source event symmetry

Order outcome facts include Payment as a registered reconciliation consumer. Payment queries bound historical purchase and current settlement facts, preserving R037 economic dedupe and existing dispatch authority. This is an asynchronous source-fact edge, not an Order/Payment commit dependency or permission to send money. Bilateral runtime fixtures remain unqualified.
