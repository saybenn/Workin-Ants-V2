# Customer Demand, Order & Resolution Architecture

> **Cluster ID:** CL-04  
> **Cluster name:** Customer Demand, Order & Resolution  
> **Cluster type:** `core_customer_demand_commerce_transaction_dispute`  
> **Document status:** Implementation-grade cluster architecture; confirmed rules are binding, proposed rulings require explicit acceptance, unresolved decisions remain non-authoritative  
> **Primary modules:** `gig_demand`, `transaction_order`, `review_dispute`

---

## 1. Document Status and Scope

This document defines the stable architecture for **CL-04 — Customer Demand, Order & Resolution**.

CL-04 is a **planning, integration, and controlled-context boundary**. It coordinates the customer-demand, transaction, agreement, review, and dispute workflows that turn buyer intent into durable transaction truth and post-transaction outcomes.

This document does **not** make the Cluster a source-of-truth owner. The three Deep Modules retain their own lifecycles:

- `gig_demand` owns `Gig`, `GigResponse`, and `GigAssignment`.
- `transaction_order` owns `Order`, `OrderEvent`, Order-specific agreement truth, agreement event truth, and Order-attached refund status.
- `review_dispute` owns `Review` and `Dispute`.

The root Workin Ants architecture remains authoritative for platform-wide rules. Target Module architecture remains authoritative for Module-local invariants and transition policy. If this document conflicts with an approved root ruling or a confirmed Module ownership ruling, the higher-authority ruling wins and this document must be updated.

### Intended audience

- coding agents;
- application and domain developers;
- reviewers;
- maintainers;
- migration authors;
- provider-integration authors;
- test authors.

### Update rule

Update this file only when a **binding architectural decision** changes: ownership, lifecycle authority, public contract, schema meaning, cross-Module integration boundary, compliance boundary, or platform primitive. Build progress alone must not silently redefine architecture.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

CL-04 controls customer-created paid demand, accepted Gig work relationships, transaction truth, Order-specific agreements, reviews, disputes, buyer-side fee-waiver snapshots, professional commission snapshots, and the transaction effects of refund/dispute outcomes.

### Goal

Produce a durable answer to:

> What CustomerProfile demand or purchase became an Order, what commercial policy was frozen at that moment, what agreement governed it, what happened during fulfillment, and what post-order outcome followed?

### What enters

- authenticated User/system actor context;
- `CustomerProfile` buyer context;
- active or draft Gigs and Professional responses;
- accepted `GigAssignment` facts;
- purchasable Offering/PricingTier facts from Marketplace Supply;
- `ProfessionalProfile` seller facts and readiness decisions;
- entitlement decisions from Track Subscription & Entitlement;
- consent proof from Consent & Disclosure;
- payment/tax/refund outcomes from Payment / Payout / Tax;
- MediaAsset readiness/access from Media / File Access;
- hold decisions from Admin Review / Compliance Hold;
- moderation decisions;
- privacy instructions;
- downstream delivery completion signals where Order state depends on them.

### What leaves

- authoritative `Gig`, `GigResponse`, and `GigAssignment` state;
- authoritative `Order` and `OrderEvent` state;
- immutable commercial pricing/entitlement snapshots on Order;
- Order-specific `Agreement`, consent, signature, document snapshot, access-grant, and agreement-event proof;
- `Review` and `Dispute` state;
- dispute resolution decisions;
- requests for payment/refund/payout/hold/media/search/notification actions through owner interfaces;
- domain events for downstream delivery, reputation, payout, search, notification, rewards, and operations.

### Major transformation

```text
CustomerProfile intent
→ Gig or direct Offering purchase
→ accepted commercial source
→ Order transaction truth
→ agreement/payment/fulfillment state
→ completed or exception outcome
→ Review and/or Dispute
→ refund/release/payout/reputation effects through owner interfaces
```

### Explicitly not owned by CL-04

CL-04 does not own:

- authentication or session truth;
- permission interpretation;
- CustomerProfile lifecycle;
- ProfessionalProfile lifecycle or readiness truth;
- Offering lifecycle;
- taxonomy vocabulary;
- Track plans, subscriptions, grants, usage events, or counters;
- payment processor webhook truth;
- payment, payout, KYC, tax, sales-tax, or financial ledger truth;
- `ComplianceHold` lifecycle;
- `MediaAsset` storage, scanning, processing, or signed URL mechanics;
- Messaging thread/message lifecycle;
- Notification delivery lifecycle;
- Search projection truth;
- PrivacyRequest orchestration;
- moderation/legal-notice lifecycle;
- Booking/video/digital-delivery lifecycle.

---

## 3. Module Inventory

| Module ID | Module name | Type | Purpose | Owned truth | Primary responsibility in CL-04 | Major inbound dependencies | Major outbound consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gig_demand` | Gig / Demand Module | domain | Own customer-created paid requests, Professional proposals, and accepted Gig work relationships. | `Gig`, `GigStatus`, `GigVisibility`, `GigResponse`, `GigResponseStatus`, `GigAssignment`, `GigAssignmentStatus`; Gig-context meaning of `GigMedia` and `GigTag`. | Convert CustomerProfile demand into a lifecycle-managed Gig, collect eligible responses, accept a response, and expose an accepted assignment to Order. | Identity, Role/Authority, CustomerProfile, Taxonomy, Professional Eligibility, verification indirectly, holds, Media, Location Safety. | Transaction / Order, Search, Messaging, Notification, Payment context consumers. |
| `transaction_order` | Transaction / Order Module | domain | Preserve paid transaction truth and Order-specific contract proof. | `Order`, `OrderEvent`, `OrderFile`, `Agreement`, `AgreementTemplate`, `AgreementElectronicConsent`, `AgreementSignature`, `AgreementDocumentSnapshot`, `AgreementEvent`, `AgreementAccessGrant`, Order-attached `RefundStatus`. | Create Order from Offering or GigAssignment, freeze commercial policy, enforce agreement gates, apply payment/refund outcomes, expose transaction entitlement. | CustomerProfile, Marketplace Supply, Gig / Demand, Professional Eligibility, Track Entitlement, Consent, Payment/Payout/Tax, holds, Media. | Booking, Digital Goods, Video, Payment/Payout/Tax, Review/Dispute, Messaging, Notification, rewards. |
| `review_dispute` | Review / Dispute Module | domain_compliance_support | Own post-order feedback and commercial conflict adjudication. | `Review`, `ReviewStatus`, `Dispute`, `DisputeStatus`. | Gate/record reviews, manage disputes, decide refund-vs-release outcome, request payout holds, and publish reputation/dispute outcomes. | Order facts, CustomerProfile, authority, holds, Payment/Payout/Tax, Media evidence, moderation, privacy. | Transaction / Order, Payment/Payout/Tax, Professional Eligibility/reputation, Search, Admin Review, Notification, Audit, Gamification. |

---

## 4. Cluster Architecture Principles

1. **Order is transaction truth.** Stripe or any other processor is a financial rail. Provider objects may cause a verified transition but never replace `Order` or `OrderEvent`.
2. **GigAssignment is not Order.** It is accepted demand-side work truth. It may source an Order, but payment and transaction state remain Order-owned.
3. **CustomerProfile is buyer-domain truth.** User remains authentication/audit identity. New commercial workflows should resolve the buyer through Customer / Buyer Profile rather than treating `User` as the only buyer identity.
4. **One lifecycle, one owner.** Gig, response, assignment, Order, agreement, review, and dispute transitions stay with their owning Modules.
5. **Pricing policy is read from Track and frozen by Order.** Buyer fee waivers and Professional commission rates are resolved through Track Subscription & Entitlement and snapshotted on Order. No local `premium`, `feeWaived`, or commission-policy booleans become source truth.
6. **Consent proof is not agreement state.** Generic versioned disclosure proof remains Consent-owned; Order-specific electronic-consent/manual-opt-out and signature execution remain Transaction / Order truth.
7. **Dispute decision is not refund execution.** Review / Dispute may decide `resolved_refund` or `resolved_release`; Transaction / Order owns Order/refund attachment effects; Payment / Payout / Tax owns provider-backed financial execution.
8. **Dispute does not own a blocked flag.** It requests/evaluates `ComplianceHold` through the hold owner.
9. **Review is reputation, not verification.** Review aggregates may influence presentation/ranking, but they cannot become `VerificationCheck`, TrustBadge, KYC, license, or professional-readiness truth.
10. **Files are contextual here, mechanical elsewhere.** `GigMedia`, `OrderFile`, dispute evidence references, and agreement snapshot relationships express business context. Media / File Access owns object safety, storage, signed access, and generic grants.
11. **Search is projection.** Gig/reputation changes request projection work. CL-04 never writes Typesense directly.
12. **Audit is evidence, not lifecycle.** `AuditEvent`/`AccessAuditLog` supplement `OrderEvent`, `AgreementEvent`, and Module-owned lifecycle state; they do not replace them.
13. **Privacy orchestrates; data owners execute.** CL-04 Modules must expose privacy target executors without inventing their own PrivacyRequest workflow.
14. **Shared mechanism does not merge truth.** Idempotency, locks, outbox, queue execution, hashing, and state-machine plumbing may be shared. Their business meaning remains Module-owned.

---

## 5. Runtime / Collaboration Topology

### Command path

```text
HTTP / server action / worker / verified internal event
→ resolveAuthenticatedActor
→ resolve CustomerProfile / ProfessionalProfile context as required
→ authorizeResourceAction
→ owning Module application service
→ owner-local policy / transition validation
→ external owner decisions through public interfaces
→ authoritative owner transaction
   → aggregate write
   → owner lifecycle event write
   → transactional outbox write when downstream effects exist
→ response
```

### Example: accepting a Gig response

```text
Customer action
→ Gig / Demand acceptGigResponse
→ authenticated actor + CustomerProfile
→ authority decision
→ lock Gig / response acceptance scope
→ re-evaluate Professional response readiness
→ atomically accept response + create/confirm GigAssignment
→ append Gig-domain lifecycle event/outbox
→ Transaction / Order createOrderFromGigAssignment command
→ notification/search/messaging effects through owner interfaces
```

### Example: payment confirmation

```text
Stripe webhook
→ Payment / Payout / Tax webhook adapter
→ verify signature
→ provider-event dedupe owned by Payment
→ translate provider state
→ Transaction / Order applyPaymentConfirmationToOrder
→ Order state + OrderEvent transaction
→ outbox
→ Booking / delivery / notification / payout consumers
```

### Cross-Module database rule

Direct cross-Module Prisma reads are **not the default integration pattern**. An owning Module exposes a stable query/command DTO when another Module needs its facts. Database foreign keys may exist across domains, but they do not authorize arbitrary repository use across Module boundaries.

---

## 6. Folder / Code Organization

The exact repository root may differ, but implementation should preserve this shape conceptually:

```text
src/
  modules/
    gig-demand/
      application/
        commands/
        queries/
        services/
        contracts/
      domain/
        policies/
        transitions/
        events/
      infrastructure/
        repositories/
        workers/
      public/
        index.ts
        contracts.ts
      ui/
      tests/

    transaction-order/
      application/
        commands/
        queries/
        agreements/
        pricing/
      domain/
        order/
        agreement/
        events/
        policies/
      infrastructure/
        repositories/
        document-generation/
        workers/
      public/
        index.ts
        contracts.ts
      ui/
      tests/

    review-dispute/
      application/
        reviews/
        disputes/
        resolution/
      domain/
        review/
        dispute/
        policies/
        events/
      infrastructure/
        repositories/
        workers/
      public/
        index.ts
        contracts.ts
      ui/
      tests/

  platform/
    auth/
    authorization/
    idempotency/
    concurrency/
    outbox/
    queue/
    observability/
    crypto/

  integrations/
    payment/
      ports/
      adapters/
    media/
      ports/
    notification/
      ports/
```

### Rules

- Module-owned domain/application code stays under its Module.
- A CL-04-specific coordinator is permitted only when a workflow genuinely spans the three Modules and no one Module is the semantic workflow owner. Prefer an owner Module orchestration service first.
- Do not create `src/modules/cl04/shared/` for convenience.
- Shared code belongs in a platform primitive only if the canonical registry identifies it as shared mechanism/capability.
- Provider adapters live behind the owning Module’s provider-neutral port. CL-04 must not create a Stripe adapter separate from Payment / Payout / Tax.
- Contracts imported across Modules come from `public/` surfaces, not internal repositories.

---

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
| --- | --- | --- | --- |
| Gig / Demand | Gig content, visibility, response and assignment lifecycles; Gig contextual joins. | CustomerProfile, taxonomy validation, Professional readiness, holds, Media readiness, location projection, Order handoff. | Order/payment/refund/payout truth, Professional verification, Search execution, MediaAsset mechanics. |
| Transaction / Order | Order lifecycle; transaction snapshots; OrderEvent; OrderFile context; agreement templates and Order-specific agreement execution/proof; refund attachment. | Offering/assignment source facts, Track decisions, consent proof, payment/refund outcomes, holds, Media. | Stripe/provider webhook dedupe, payout/tax/KYC truth, Booking/delivery truth, generic ConsentLog, file-storage mechanics. |
| Review / Dispute | Review lifecycle; dispute lifecycle; adjudication result; reputation feedback. | Order facts; hold commands; refund execution result; Media evidence access; moderation outcomes. | Order/refund lifecycle, payout execution, ComplianceHold, moderation/legal cases, TrustBadge/verification truth. |
| Payment / Payout / Tax | Provider payment/refund rail, Stripe webhook verification/dedupe, ledger, payout, tax. | Order facts and dispute decisions. | Order lifecycle or Dispute lifecycle. |
| Track Subscription & Entitlement | Plans, subscriptions, grants, counters, usage proof. | Order identifiers for usage correlation. | Historical transaction snapshot. |
| Media / File Access | MediaAsset, validation/scan/process, object storage, signed access mechanics. | Contextual entitlement decision from Order/Gig/Dispute. | Agreement/Order/Gig/Dispute business meaning. |
| Admin Review / Compliance Hold | ComplianceHold lifecycle. | Dispute/Gig/Order source evidence. | Review/Dispute/Order lifecycle. |
| Search / Public Visibility | SearchUpsertEvent and public projection execution. | Gig/reputation/source readiness facts. | Gig, Review, Professional, Order source truth. |
| Privacy / Data Erasure | PrivacyRequest, erasure/export orchestration, retention exemptions. | Module-specific executors and retention facts. | Direct ownership of Gig/Order/Review/Dispute records. |
| Messaging / Notification | Thread/Message and notification delivery truth respectively. | CL-04 domain events and recipient facts. | Gig/Order/Dispute business lifecycle. |

---

## 8. Data Ownership

### CL-04 owned data

| Record / enum | Owner | Meaning |
| --- | --- | --- |
| `Gig` | Gig / Demand | Customer demand request truth. |
| `GigStatus` | Gig / Demand | Gig lifecycle vocabulary. |
| `GigVisibility` | Gig / Demand | Public/private/invite-only visibility vocabulary. |
| `GigResponse` | Gig / Demand | One ProfessionalProfile commercial response per Gig under current uniqueness constraint. |
| `GigResponseStatus` | Gig / Demand | Response lifecycle vocabulary. |
| `GigAssignment` | Gig / Demand | Accepted work relationship; not transaction truth. |
| `GigAssignmentStatus` | Gig / Demand | Assignment lifecycle vocabulary. |
| `GigMedia` | Gig / Demand contextual meaning | Links validated MediaAsset into Gig context. |
| `GigTag` | Gig / Demand contextual use; Taxonomy owns vocabulary | Classification attachment. |
| `Order` | Transaction / Order | Paid/commercial transaction truth. |
| `OrderStatus` | Transaction / Order | Order lifecycle vocabulary. |
| `OrderSourceType` | Transaction / Order | Offering vs GigAssignment origin. |
| `OrderEvent` | Transaction / Order | Immutable Order-domain timeline. |
| `OrderFile` / `FileRole` | Transaction / Order contextual meaning | Order-specific file attachment role. |
| `RefundStatus` | Transaction / Order | Order-attached refund state, distinct from provider execution truth. |
| `AgreementTemplate` | Transaction / Order | Versioned reusable agreement template state. |
| `Agreement` | Transaction / Order | Order-specific agreement truth. |
| `AgreementElectronicConsent` | Transaction / Order | Order-specific electronic execution/manual opt-out proof. |
| `AgreementSignature` | Transaction / Order | Signer execution state/proof. |
| `AgreementDocumentSnapshot` | Transaction / Order | Immutable rendered/final document version and hash proof. |
| `AgreementEvent` | Transaction / Order | Agreement-domain lifecycle history. |
| `AgreementAccessGrant` | Transaction / Order | Contract-context retrieval authorization; actual URL mechanics remain Media-owned. |
| `Review` / `ReviewStatus` | Review / Dispute | Post-order feedback and visibility lifecycle. |
| `Dispute` / `DisputeStatus` | Review / Dispute | Order-bound commercial conflict and adjudication lifecycle. |

### External records referenced but not owned

- `CustomerProfile` — Customer / Buyer Profile.
- `ProfessionalProfile` — Professional Eligibility.
- `Offering`, `PricingTier` — Marketplace Supply.
- `TrackSubscription`, `TrackEntitlementGrant`, `TrackUsageEvent`, `TrackUsageCounter` — Track Subscription & Entitlement.
- `VerificationCheck`, `VerificationRequirement` — Trust Verification / Screening.
- `ComplianceHold` — Admin Review / Compliance Hold.
- `MediaAsset`, Media validation/scan/process/grant records — Media / File Access.
- `SearchUpsertEvent` — Search / Public Visibility.
- `ProcessedStripeEvent`, payout/tax/ledger records — Payment / Payout / Tax.
- `AuditEvent`, `AccessAuditLog` — Audit / Event Ledger.
- `PrivacyRequest`, `DataErasureTarget`, `DataRetentionExemption` — Privacy / Data Erasure.

### Ownership conflicts resolved by source hierarchy

The Deep Module Registry has historical claims that place Track records under Transaction / Order. The dedicated Track module and current Cluster Registry establish Track Subscription & Entitlement as commercial-policy owner. **Binding interpretation for CL-04:** Transaction / Order references Track truth and freezes only the downstream commercial effect on `Order`; it does not own Track lifecycle records.

---

## 9. Lifecycle Ownership

### 9.1 Gig

- **Owner:** Gig / Demand.
- **Known statuses:** `draft`, `open`, `paused`, `assigned`, `completed`, `cancelled`, `expired`, `archived`.
- **Transition authority:** Gig / Demand only.
- **Other Modules may:** supply gates, request restrictions, react to committed transitions.
- **Must not be confused with:** Order completion, assignment completion, moderation state, search visibility.

**Unresolved:** exact legal transition graph, reopening policy, and how `assigned/completed` synchronize with assignment/Order outcomes.

### 9.2 GigResponse

- **Owner:** Gig / Demand.
- **Known statuses:** `submitted`, `viewed`, `shortlisted`, `accepted`, `rejected`, `withdrawn`.
- **Constraint:** one response per Gig per ProfessionalProfile.
- **Transition authority:** Gig / Demand.
- **Other Modules may:** provide Professional readiness.
- **Unresolved:** revision rules after view/shortlist, acceptance after prior terminal state.

### 9.3 GigAssignment

- **Owner:** Gig / Demand.
- **Known statuses:** `proposed`, `accepted`, `active`, `delivered`, `completed`, `cancelled`, `disputed`.
- **Transition authority:** Gig / Demand.
- **Other Modules may:** Order/Dispute events may request/react to local assignment effects.
- **Must not be confused with:** `Order`.
- **Unresolved:** whether one Gig is single-award or multi-award; exact semantics of `disputed`; which completion events drive assignment/gig completion.

### 9.4 Order

- **Owner:** Transaction / Order.
- **Known vocabulary:** `draft`, `awaiting_agreement`, `pending_payment`, `paid`, `awaiting_seller`, `accepted`, `in_progress`, `delivered`, `completed`, `cancelled`, `refunded`, `disputed`.
- **Transition authority:** Transaction / Order only.
- **Other Modules may:** Payment submits verified payment/refund outcomes; Review/Dispute submits dispute effects; delivery owners submit completion evidence.
- **Must not be confused with:** Stripe payment state, payout state, GigAssignment status.
- **Unresolved:** exact transition matrix and whether every Order source requires the same seller-acceptance/delivery stages.

### 9.5 Agreement template

- **Owner:** Transaction / Order.
- **Lifecycle:** draft/versioned → active → retired, with immutable historical versions.
- **Authority:** approved admin/domain commands.
- **Must not be confused with:** general ConsentLog.

### 9.6 Order-specific Agreement

- **Owner:** Transaction / Order.
- **Lifecycle dimensions:** instantiation, document generation, electronic consent/manual opt-out, signer execution, finalization, supersession/void/archive/retention.
- **Authority:** Transaction / Order.
- **Must not be confused with:** MediaAsset, generic consent, provider envelope state.

### 9.7 Review

- **Owner:** Review / Dispute.
- **Known statuses:** `pending`, `published`, `hidden`, `removed`.
- **Authority:** Review / Dispute.
- **Other Modules may:** moderation supplies formal moderation outcomes; Search consumes visibility effects.
- **Unresolved:** rating scale, editing window, publication policy, re-publication rules.

### 9.8 Dispute

- **Owner:** Review / Dispute.
- **Known statuses:** `open`, `under_review`, `resolved_refund`, `resolved_release`, `dismissed`, `closed`.
- **Authority:** Review / Dispute.
- **Other Modules may:** Hold owns stop sign; Payment executes refund/release financial effects; Order applies transaction effects.
- **Unresolved:** one lifetime dispute vs reopenable case, meaning of resolved-vs-closed, evidence model and administrative note model.

---

## 10. Public Module Interfaces

These contracts are architectural surfaces, not claims that code already exists.

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `createGigDraft` | Gig / Demand | UI/application | Start customer demand. | actor, CustomerProfile, draft fields | Gig ID/status | truth | CustomerProfile lifecycle or taxonomy truth. |
| `publishGig` | Gig / Demand | UI | Open eligible demand. | Gig ID, actor | Gig status/version | truth/decision | Search indexing success. |
| `submitGigResponse` | Gig / Demand | Professional UI | Record one proposal after readiness gate. | Gig, ProfessionalProfile, proposal | response ID/status | truth | Professional readiness. |
| `acceptGigResponse` | Gig / Demand | Customer UI | Atomically accept response and create/identify assignment. | Gig, response, CustomerProfile, agreed terms, idempotency key | assignment snapshot | truth | Order creation/payment. |
| `getGigAssignmentCheckoutSource` | Gig / Demand | Transaction / Order | Return immutable/minimum accepted assignment facts needed to create Order. | assignment ID | buyer, seller, amount/currency, source version/status | truth | Gig tables via direct repository. |
| `createOrderFromGigAssignment` | Transaction / Order | Gig / Demand | Create transaction from accepted assignment. | assignment source DTO, buyer, seller, idempotency key | Order ID/status | truth | payment provider state. |
| `createOrderFromOffering` | Transaction / Order | checkout/UI | Create transaction from Offering source. | checkout source DTO, CustomerProfile, seller, idempotency key | Order ID/status | truth | Offering lifecycle mutation. |
| `resolveAndSnapshotOrderPricing` | Transaction / Order | internal Order workflow | Freeze base price, fee waiver, commission and evidence. | source facts + Track decisions | immutable pricing snapshot | truth | future entitlement values. |
| `applyPaymentConfirmationToOrder` | Transaction / Order | Payment / Payout / Tax | Apply verified provider-neutral payment result. | Order ID, translated result, idempotency | updated Order | truth | Stripe payload semantics. |
| `applyRefundOutcomeToOrder` | Transaction / Order | Payment/Dispute | Attach verified refund result to Order truth. | Order ID, translated outcome | refund/order state | truth | provider refund state directly. |
| `authorizeOrderEntitlement` | Transaction / Order | Booking, Media, Digital Goods, Video | Confirm current Order permits a delivery action. | Order ID, actor, action | allow/deny, reasons/evidence | decision | delivery-grant truth. |
| `instantiateAgreementForOrder` | Transaction / Order | Order workflow | Create Order-specific contract package. | Order, template version | Agreement | truth | generic consent. |
| `recordAgreementElectronicConsent` | Transaction / Order | agreement UI | Record Order-specific execution consent/opt-out context with ConsentLog reference. | agreement, actor, proof ref | agreement consent state | truth/evidence | ConsentLog lifecycle. |
| `recordAgreementSignature` | Transaction / Order | signer/provider adapter | Record signer execution proof. | agreement, signer/role, verified execution evidence | signature state | truth/evidence | provider envelope state. |
| `issueAgreementAccessGrant` | Transaction / Order | participants/admin | Authorize retrieval of contract snapshot. | agreement/snapshot, actor, reason, expiry | AgreementAccessGrant | decision/truth | signed URL mechanics. |
| `evaluateReviewEligibility` | Review / Dispute | buyer UI | Check whether Order may be reviewed by actor. | Order ID, actor | allow/deny | decision | Order truth. |
| `submitOrderReview` | Review / Dispute | buyer UI | Create one review for eligible Order. | Order, buyer actor, rating/comment | Review | truth | reputation aggregate as verification. |
| `evaluateDisputeEligibility` | Review / Dispute | participant UI | Check whether dispute may be opened. | Order ID, actor, reason | allow/deny | decision | refund result. |
| `openOrderDispute` | Review / Dispute | participants | Create dispute and initiate hold request. | Order, opener, reason/evidence refs, idempotency | Dispute | truth | ComplianceHold truth. |
| `resolveDisputeWithRefund` | Review / Dispute | admin/reviewer | Record adjudication in favor of refund and request downstream execution. | dispute, actor, amount/basis | resolution + workflow correlation | truth/decision | refund completion. |
| `resolveDisputeWithRelease` | Review / Dispute | admin/reviewer | Record release/no-refund adjudication and request hold/payout reevaluation. | dispute, actor, basis | resolution | truth/decision | payout release truth. |
| `applyOrderSettlementResultToDispute` | Review / Dispute | Order/Payment event consumer | Close/finalize dispute after actual settlement effects. | dispute, settlement result | updated dispute | truth | payment provider state. |

---

## 11. Canonical Shared Operations Used by This Cluster

The canonical registry currently standardizes operation names and ownership. No authoritative permanent `SH-###` identifiers are present in the supplied registry; therefore this document does **not invent IDs**.

| Canonical operation | Plain-English meaning | Canonical owner/class | CL-04 consumers | Reusable mechanism | Local policy that remains local | Invocation point | Must not be duplicated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Resolve trusted Workin Ants actor from valid session/system credential. | Identity & Access | all three | typed actor context | which domain action is attempted | every protected command | feature-local current-user/session helpers |
| `authorizeResourceAction` | Decide whether actor may perform named action in proper scope. | Role / Authority | all three | typed authorization decision | Order/Gig/Review/Dispute relationship facts and action vocabulary | before protected read/write | local role-permission engines |
| `resolveCustomerActor` | Resolve User into commercial CustomerProfile. | Customer / Buyer Profile | Gig, Order, Review/Dispute | buyer actor resolution | whether workflow requires active buyer profile | before buyer-domain commands | `User`-only buyer helper |
| `resolveEntitlement` | Return effective fee waiver, commission, perk, limit, etc. | Track Subscription & Entitlement | Transaction / Order primarily | commercial-policy lookup | when snapshot is taken and how effect changes Order | order pricing freeze | local premium/waiver/commission policy |
| `consumeMeteredEntitlement` | Atomically record permitted metered usage. | Track Subscription & Entitlement | Order where buyer perk usage is metered | atomic usage receipt | which transaction event counts | after authoritative transaction use | local quota counters |
| `recordConsentProof` / `queryConsentProof` | Store/read generic versioned acceptance proof. | Consent & Disclosure | Transaction / Order agreement workflows | versioned proof | whether proof satisfies current Order action | before electronic execution | local generic consent tables |
| `evaluateComplianceHold` | Return active reusable stop signs. | Admin Review / Compliance Hold | all three where action can be blocked | hold query | which target/action a hold blocks | before publish/accept/pay/refund/release/access | local `blocked` flags |
| `requestComplianceHold` / `releaseComplianceHold` | Create/release authoritative platform stop sign. | Admin Review / Compliance Hold | Review/Dispute primarily | hold lifecycle command | dispute evidence and requested scope | dispute open/resolution | dispute-local payout-hold state |
| `evaluateProfessionalReadiness` | Determine Professional may perform named selling action. | Professional Eligibility | Gig / Demand; Order where seller gate needed | readiness decision | Gig response/acceptance or Order action requiring it | response submit/accept and selected Order transitions | raw cross-table readiness reconstruction |
| `validateTaxonomyAssignment` / `resolveTaxonomyRequirements` | Validate accepted taxonomy and derive requirement triggers. | Taxonomy & Classification | Gig / Demand | canonical classification | whether Gig publish requires classification | Gig publish/update | local tag cleaners/requirement maps |
| `authorizeOrderEntitlement` | Confirm Order permits requested delivery/access action. | Transaction / Order | downstream CL-05 and Media contexts | source transaction decision | action-specific entitlement | delivery/access request | delivery modules inferring payment from provider |
| `appendAuditEvent` | Append generic significant-action proof. | Audit / Event Ledger | all three | generic audit write | which actions warrant audit and safe metadata | after/beside significant actions | custom audit tables replacing domain events |
| `recordSensitiveAccess` | Record protected file/contract/evidence access. | Audit / Event Ledger | Transaction / Order; Review/Dispute | access audit | sensitivity and contextual entitlement | agreement/evidence access | local access-log substitutes where generic rail applies |
| `appendDomainLifecycleEvent` | Reuse append-only persistence mechanics for domain event ledgers. | shared persistence mechanism | Order/Agreement; future Gig/Dispute if approved | insert-only transaction hook | event names and lifecycle meaning | same transaction as aggregate write | one universal lifecycle ledger |
| `executeIdempotentCommand` | Make retries produce one semantic business effect. | platform primitive | all three | key/fingerprint/result replay | command identity/conflict/replay semantics | create/accept/pay/refund/dispute commands | per-feature idempotency implementations |
| `acquireAggregateLock` / `withOptimisticConcurrency` | Prevent conflicting concurrent state changes. | platform primitive | Gig acceptance, Order transitions, Dispute resolution | DB locking/CAS | lock key and conflict semantics | critical transitions | in-memory mutex or bespoke lock tables |
| `transitionLifecycleState` | Reuse state-machine plumbing while owner supplies graph. | shared mechanism / separate truth | all three | transition validation/update hook | legal transition graph | every lifecycle mutation | generic policy table owning all statuses |
| `publishDomainEvent` | Reliably publish owner-defined event after commit. | platform outbox | all three | transactional outbox/envelope | event meaning/payload/privacy | after committed transitions | ad hoc fire-and-forget events |
| `deduplicateDomainEvent` | Prevent duplicate consumer side effects. | event infrastructure | all consumers | inbox claim | handler identity and side effect | event handlers | custom processed-event logic for ordinary domain events |
| `enqueueReliableJob` / `executeRetryWithBackoff` | Run asynchronous work with retries/leases/dead-letter. | queue infrastructure | expiration, PDF, hash verification, reconciliation | worker shell | payload and terminal business meaning | background jobs | custom queue systems |
| `runDeadlineExpiration` | Find expired records and invoke owner transition. | shared scheduler | Gig, agreement grants | scheduler batching | what expiry means | `closesAt`, grant expiry | scheduler owning domain status |
| `requestNotification` | Request alert through Notification owner. | Notification | all three | delivery command | event meaning/recipients | lifecycle events | direct email/SMS/push dispatch |
| Search refresh/public projection command | Request Search owner to index/update/remove projection. | Search / Public Visibility public interface | Gig; review/reputation effects | projection request | source public-readiness facts | source change | Typesense client in CL-04 |
| Media signed-access/file operations | Validate and issue storage access through Media owner. | Media / File Access public interfaces | Gig, Order, Review/Dispute | file mechanics | contextual business entitlement | attachment/access flow | direct R2/S3 signed URL code |
| `createRequestContext`, `writeStructuredLog`, `recordIntegrationFailure` | Correlate and observe execution without replacing domain truth. | Observability / Ops | all three | request IDs/logging/failure rail | domain failure state | all sync/async/provider boundaries | custom observability clients |

### Classification reminders

- `resolveAuthenticatedActor`, idempotency, concurrency, outbox, queue, crypto/hashing infrastructure are **platform primitives/capabilities**.
- `authorizeOrderEntitlement`, readiness queries, Track resolution, Search refresh are **Module public interfaces**.
- transition plumbing is **shared mechanism / separate truth**.
- decision response shapes may be **shared contract / separate policy**.
- Stripe/e-sign adapters are **provider-adapter patterns**, owned by the appropriate provider-owning Module.
- no generic “CL-04 shared service” may absorb these owners.

---

## 12. Cross-Module Data Flows

### 12.1 Customer posts and publishes a Gig

```text
Customer action
→ Identity resolves actor
→ Customer / Buyer Profile resolves CustomerProfile
→ Role / Authority authorizes Gig action
→ Gig / Demand validates draft
→ Taxonomy validates classification and requirement triggers
→ Location Safety supplies fuzzy public location when needed
→ Compliance Hold checked
→ Gig / Demand writes Gig status
→ owner event/outbox
→ Search projection request
→ Notification/Messaging effects if applicable
```

### 12.2 Professional responds to Gig

```text
Professional action
→ actor + authority
→ Gig / Demand loads Gig facts
→ Professional Eligibility evaluates respond_to_gig
→ Gig / Demand validates one-response constraint
→ GigResponse write
→ domain event/outbox
→ Notification request to customer
```

### 12.3 Customer accepts response and creates Order source

```text
Customer accepts
→ actor + CustomerProfile + authority
→ acquire acceptance lock / idempotency claim
→ Gig / Demand rechecks Gig/response state
→ Professional Eligibility rechecks acceptance readiness
→ Gig / Demand writes accepted response + GigAssignment atomically
→ publishes assignment-ready event
→ Transaction / Order reads immutable assignment source through public interface
→ createOrderFromGigAssignment
```

### 12.4 Direct Offering purchase becomes Order

```text
Customer checkout
→ actor + CustomerProfile
→ Transaction / Order requests immutable checkout source from Marketplace Supply
→ Professional readiness gate as required
→ Track resolves buyer fee waiver + seller commission
→ Transaction / Order freezes pricing/evidence snapshot
→ optional Agreement instantiation/gate
→ Order write + OrderEvent/outbox
→ Payment / Payout / Tax payment initiation
```

### 12.5 Payment confirmation

```text
Provider webhook
→ Payment owner verifies signature
→ Payment-owned provider-event dedupe
→ provider-neutral result
→ Transaction / Order applies payment confirmation
→ Order + OrderEvent transaction
→ domain event
→ booking/digital delivery/payout/notification consumers
```

### 12.6 Agreement execution

```text
Order requires agreement
→ Transaction / Order selects immutable template version
→ Agreement instantiated
→ generic Consent proof queried/recorded where required
→ Order-specific electronic consent or manual opt-out recorded
→ signature records satisfied
→ PDF/document generation job
→ Media stores validated private object
→ Transaction / Order records AgreementDocumentSnapshot + SHA-256 proof
→ Agreement finalized
→ Order pre-payment/pre-delivery gate may advance
```

### 12.7 Completed Order produces Review

```text
Order completed
→ outbox event
→ Review / Dispute exposes review eligibility
→ buyer submits review
→ Review truth written
→ publication/moderation policy applied
→ reputation projection recalculated
→ Search refresh requested through Search
→ notification/reward consumers react
```

### 12.8 Dispute with refund outcome

```text
authorized participant opens Dispute
→ Review / Dispute writes Dispute
→ requests ComplianceHold
→ Order enters transaction dispute effect through public command
→ admin/reviewer adjudicates resolved_refund
→ Payment / Payout / Tax executes refund
→ verified refund result
→ Transaction / Order updates RefundStatus / Order effect
→ Review / Dispute applies settlement result
→ hold release/adjustment requested
→ notification/audit events
```

---

## 13. Cross-Cluster Bridges

| Source | Destination | Transfer | Authoritative owner | Interface/event | Forbidden coupling |
| --- | --- | --- | --- | --- | --- |
| CL-01 Customer / Buyer Profile | CL-04 | CustomerProfile buyer context | Customer Profile | `resolveCustomerActor` / profile query | storing buyer policy on User or recreating CustomerProfile |
| CL-01 Track Subscription & Entitlement | Transaction / Order | buyer fee waiver, seller commission, usage receipt | Track | `resolveEntitlement`, `consumeMeteredEntitlement` | local premium/commission/waiver truth |
| CL-01 Identity/Authority/Consent | CL-04 | actor, permission decision, generic consent proof | respective owners | canonical shared interfaces | local auth/authz/consent engines |
| CL-02 Taxonomy | Gig / Demand | category/domain/tag validity and requirement triggers | Taxonomy | public validation query | copied taxonomy tables/rules |
| CL-02 Search | Gig/Review effects | projection request | Search | Search refresh/upsert interface | direct Typesense writes |
| CL-03 Marketplace Supply | Transaction / Order | Offering checkout source and pricing tier facts | Marketplace Supply | immutable checkout source query | Order repository reading Offering internals |
| CL-03 Professional Eligibility | Gig/Order | selling readiness decision | Professional Eligibility | `evaluateProfessionalReadiness` | raw compliance joins in CL-04 |
| CL-03 Payment/Payout/Tax | Order/Dispute | payment, sales tax, refund, payout effects | Payment/Payout/Tax for rail; Order for transaction effect | provider-neutral commands/events | Stripe webhook handling in CL-04 |
| CL-05 Delivery | Transaction / Order | delivery request/result; Order entitlement | Order + delivery owner | `authorizeOrderEntitlement`, delivery events | Order owning Booking/Media/Video lifecycles |
| CL-07 Messaging/Notification | all CL-04 | communication context and alerts | Messaging/Notification | context-thread and notification interfaces | direct provider dispatch |
| CL-08 Privacy/Location | CL-04 | erasure instructions, retention decisions, fuzzy/exact location gates | Privacy/Location owners | executor contracts | feature-owned privacy workflow or coordinate fuzzing |
| CL-09 Holds/Audit/Ops/Moderation | CL-04 | holds, audit, access logs, moderation decisions, ops failures | CL-09 Modules | public commands/events | local hold/audit/moderation/incident systems |
| CL-10 Rewards | Review/Order events | eligible business event | source Module | domain event | reward mutation inside CL-04 |

---

## 14. Authentication and Authorization

- Every protected operation starts from `resolveAuthenticatedActor`.
- Buyer-domain commands resolve `CustomerProfile`; authentication User ID may be retained for actor/audit trace.
- Professional commands use `ProfessionalProfile` plus authenticated User actor context.
- `authorizeResourceAction` interprets authority. CL-04 supplies relationship facts:
  - Gig poster/customer relationship;
  - GigResponse Professional ownership;
  - Order buyer/seller participant relationship;
  - Review eligible buyer;
  - Dispute participant/admin relation;
  - Agreement signer/participant relation.
- Admin/support roles are not blanket permission to read contracts, private evidence, or sensitive files. Contextual access decisions and sensitive-access audit still apply.
- Sensitive financial operations may require `requireStepUpForSensitiveAction` when root policy classifies them as high risk.
- Authorization must be server-side. Frontend route state is not permission proof.

---

## 15. Compliance and Readiness Composition

### Gig response/acceptance

Owner-local Gig policy composes:

- Professional Eligibility decision;
- taxonomy-triggered verification requirements;
- active ComplianceHolds;
- Gig status/visibility/deadline;
- actor authority.

Gig / Demand does not own VerificationCheck or ComplianceHold truth.

### Order creation and payment readiness

Transaction / Order composes:

- valid commercial source;
- CustomerProfile buyer;
- seller ProfessionalProfile;
- Professional readiness when required;
- buyer fee waiver and seller commission entitlement results;
- agreement requirement/satisfaction;
- active holds;
- payment/tax prerequisites supplied by Payment / Payout / Tax.

### Agreement compliance

- Generic consent/version proof: Consent & Disclosure.
- Order-specific electronic execution/manual opt-out: Transaction / Order.
- Signature proof/document hash/archive: Transaction / Order plus Media mechanics.
- Legal text correctness remains outside architectural automation; templates must be reviewed through appropriate business/legal process.

### Dispute

- Dispute adjudication: Review / Dispute.
- Stop sign: ComplianceHold.
- Refund execution: Payment / Payout / Tax.
- Refund attachment/transaction effect: Transaction / Order.
- Payout eligibility/release: Payment / Payout / Tax.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Domain events

At minimum, design versioned events around committed outcomes such as:

- GigCreated / GigPublished / GigExpired / GigCancelled;
- GigResponseSubmitted / Accepted / Rejected / Withdrawn;
- GigAssignmentAccepted / Cancelled / Completed;
- OrderCreated / AgreementRequired / PaymentConfirmed / Accepted / Delivered / Completed / Cancelled / Refunded / Disputed;
- AgreementInstantiated / ConsentRecorded / SignatureRecorded / Finalized / Voided / Accessed;
- ReviewSubmitted / Published / Hidden / Removed;
- DisputeOpened / ReviewStarted / RefundResolved / ReleaseResolved / Closed.

Exact names and payloads belong to owners.

### Transactional outbox

Use canonical `publishDomainEvent` with a transactional outbox whenever committed state must reliably trigger external work. Do not emit network calls inside the owner transaction as the only delivery mechanism.

### Jobs

Likely asynchronous work:

- Gig expiration;
- agreement document generation;
- final agreement rendering;
- hash verification;
- agreement access-grant expiration;
- interrupted assignment→Order reconciliation;
- payment/refund reconciliation requested from Payment owner;
- reputation projection recalculation;
- privacy executor batches.

### Retries and idempotency

- All retryable commands use canonical idempotency semantics.
- Jobs use queue lease/retry/dead-letter infrastructure.
- Provider retries never bypass provider-owner verification/dedupe.
- Domain events use consumer inbox deduplication.

### Concurrency

Critical concurrency points:

- simultaneous response acceptance;
- duplicate Order creation from one GigAssignment;
- repeated payment/refund outcomes;
- simultaneous Order transitions;
- dispute resolution races;
- agreement signature/finalization races.

Use database locking/optimistic concurrency primitives, not process-local mutexes.

### Workflow/saga boundary

The semantic workflow owner remains the Module whose business outcome is being advanced:

- Gig acceptance orchestration — Gig / Demand.
- Order creation/payment/agreement orchestration — Transaction / Order.
- Dispute adjudication/settlement coordination — Review / Dispute.
- shared workflow runner may persist technical steps but cannot own statuses of participants.

---

## 17. Provider Integrations

### Payment / refund provider

```text
Payment / Payout / Tax
→ provider-neutral payment/refund port
→ Stripe adapter
→ Stripe
→ verified signature + Payment-owned ProcessedStripeEvent dedupe
→ normalized provider-neutral result
→ Transaction / Order transition
```

CL-04 must not:

- verify Stripe webhooks;
- own `ProcessedStripeEvent`;
- interpret raw Stripe status as Order status;
- execute provider refund calls directly from Review / Dispute.

### Agreement renderer

PDFKit/Puppeteer may be infrastructure used by Transaction / Order to render an Order-specific document. Rendering technology is not contract truth. The immutable `AgreementDocumentSnapshot` and its hash are Transaction / Order truth; the stored object is Media truth.

### External e-sign provider, if adopted

```text
Transaction / Order
→ e-sign provider-neutral port
→ provider adapter
→ provider
→ verified provider event + provider-specific dedupe
→ normalized consent/signature/document result
→ Agreement command
```

**Unresolved:** no external e-sign provider is binding in supplied evidence. Do not make provider-specific schemas domain types before a provider decision.

### Operational failures

Provider failures use Observability / Ops `recordIntegrationFailure` and owner-local workflow state where business meaning requires it.

---

## 18. Search / Projection Boundaries

- Public Gig discovery is a Search projection of Gig source truth.
- Search may index only source-authorized public Gig fields, fuzzy public location, accepted taxonomy, and readiness/moderation-safe fields.
- Gig publish/pause/cancel/expire/archive/privacy/moderation changes request reindex/deindex through Search.
- Reviews influence public reputation only through Review-owned publication state and a derived rating projection.
- Search must never infer Professional verification from review score.
- Search must not reconstruct Gig eligibility or dispute state from raw CL-04 tables.
- Orders, agreements, disputes, and private evidence are not public search documents.

---

## 19. Media / File Boundaries

### Gig attachments

- `GigMedia` expresses Gig context and ordering/role.
- Media owns upload policy, binary validation, scanning, processing, metadata scrubbing, object key, storage, and signed access.
- Gig publish may require Media readiness but cannot mark an unsafe object ready.

### Order files

- `OrderFile` expresses transaction-specific attachment role.
- Deleting OrderFile context does not imply deleting MediaAsset.
- Retention may require keeping the underlying object even after product-level context removal.

### Agreement documents

- Transaction / Order owns Agreement document version, finalization state, SHA-256 evidence, and access authorization.
- Media owns private object and signed URL issuance.
- `AgreementAccessGrant` is contextual contract entitlement; Media grant/URL is transport access.

### Dispute evidence

Current schema evidence is insufficient for a dedicated DisputeEvidence model. Until resolved, dispute workflows may reference owner-approved OrderFile/Message/Media objects through stable evidence references, but must not create a shadow file pipeline.

### Sensitive access

Viewing/downloading finalized agreements or dispute evidence should use `recordSensitiveAccess` with minimized metadata.

---

## 20. Privacy / Retention

Privacy / Data Erasure owns:

- PrivacyRequest;
- DataErasureJob/Target;
- retention exemption decisions/records;
- export orchestration.

CL-04 owners must expose target executors.

### Gig executor

Must be able to enumerate and apply instructions to:

- draft/public Gig text and location fields;
- response message/proposal data;
- assignment actor references and commercial terms;
- contextual media joins;
- event/audit references consistent with retention rules.

Accepted/paid terms that are duplicated/frozen into Order may have separate retention obligations from unconverted Gig content.

### Transaction / Order executor

Must enumerate:

- Orders and participant data;
- OrderEvent;
- OrderFile context;
- agreements, signatures, electronic-consent evidence;
- document snapshots;
- agreement access grants/events.

Signed agreements and transaction records may require retention exemptions for contract, payment, tax, dispute, fraud, or signature proof. Privacy erasure may anonymize nonessential actor metadata where legally permitted but must not destroy retention-locked proof.

### Review / Dispute executor

Must distinguish:

- removable public Review content;
- retained commercial dispute evidence;
- required anonymization;
- downstream search/reputation effects.

Feature Modules must never implement their own PrivacyRequest status machine.

---

## 21. Audit and Observability

### Audit evidence

Use Audit / Event Ledger for generic significant-action proof such as:

- Gig publish/cancel/accept;
- Order administrative corrections;
- agreement template activation/retirement;
- agreement access;
- dispute opening/adjudication/closure;
- review moderation actions.

Use `AccessAuditLog` for sensitive agreement/evidence access where policy requires it.

### Domain-event truth

Keep separate:

- `OrderEvent`;
- `AgreementEvent`;
- Gig/Response/Assignment statuses and any future owner event ledger;
- Review/Dispute statuses and any future owner event ledger;
- Payment provider dedupe/financial ledger records.

### Observability

Use:

- request/correlation/causation IDs;
- structured logs;
- queue telemetry;
- integration-failure records;
- metrics for workflow latency/failures/retries;
- exception capture with redaction.

No logs should contain full contracts, raw dispute evidence, private message bodies, payment secrets, signatures, tax details, or unnecessary personal data.

---

## 22. Security Boundaries

- Validate all mutation payloads server-side with canonical schemas.
- Enforce ownership/participant/admin authorization server-side.
- Resolve CustomerProfile and ProfessionalProfile from trusted IDs and relationships; never trust client-provided actor ownership.
- Use idempotency keys for commercial create/accept/pay/refund/dispute commands.
- Use database concurrency controls for acceptance, Order creation, settlement, and finalization.
- Hash finalized agreement bytes using the approved hashing primitive; domain code stores hash result/evidence, not a custom crypto implementation.
- Keep agreement/dispute files private.
- Signed credentials/URLs are short lived and issued only after contextual entitlement.
- Verify all provider webhooks in the provider-owning adapter before domain commands.
- Minimize provider payload persistence.
- Apply rate limits to Gig creation/response, review/dispute submission, agreement access, and financial actions as defined by platform policy.
- Prevent replay of provider and internal event messages through canonical dedupe mechanisms.
- Do not trust client redirects as payment/refund proof.

---

## 23. Testing Architecture

### Module unit tests

Each Module tests:

- domain validation;
- transition rules;
- snapshot rules;
- decision composition;
- failure classification;
- privacy executor behavior.

### Public-interface contract tests

Cover:

- Gig assignment source DTO consumed by Order;
- Offering checkout DTO consumed by Order;
- Payment normalized result consumed by Order;
- Order entitlement decision consumed by delivery;
- dispute decision/result consumed by Order/Payment/Hold;
- Search and Notification request contracts.

### Lifecycle tests

Test every allowed and forbidden transition once transition matrices are approved.

### Cross-Module integration tests

At minimum:

1. Gig response acceptance → exactly one valid assignment effect under concurrency.
2. accepted assignment → exactly one Order.
3. Offering checkout → frozen pricing/entitlement snapshot.
4. verified payment result → Order paid, duplicate event no duplicate effect.
5. agreement-required Order cannot cross gated transition until agreement satisfied.
6. completed Order → eligible review.
7. dispute open → hold requested, not locally created.
8. resolved refund → Payment execution → Order refund effect → dispute close.

### Provider adapter tests

Owned by provider Module, but CL-04 contract tests must use normalized fixtures and prove raw provider statuses never enter domain APIs.

### Idempotency/concurrency tests

- duplicate Gig acceptance;
- competing response acceptance;
- duplicate Order creation;
- duplicate payment confirmation;
- duplicate dispute open;
- competing dispute resolution;
- duplicate agreement signature/finalization.

### Compliance/privacy tests

- agreement consent vs ConsentLog separation;
- private contract access and access auditing;
- hold enforcement;
- erasure/retention behavior;
- Review removed from public reputation;
- dispute retained/anonymized per exemption.

### E2E

Critical journeys:

- Gig → response → assignment → Order.
- Offering → Order → payment → fulfillment.
- Agreement-required checkout.
- completed Order → Review.
- Order → Dispute → refund/release resolution.

---

## 24. Invariants

### Rules coding agents must never violate

1. `Gig`, `GigResponse`, and `GigAssignment` are mutated only through Gig / Demand-owned application/domain operations.
2. `Order`, `OrderEvent`, and Order-specific agreement records are mutated only through Transaction / Order-owned operations.
3. `Review` and `Dispute` are mutated only through Review / Dispute-owned operations.
4. CL-04 itself never becomes a fourth lifecycle owner.
5. Stripe/payment-provider state never replaces Order truth.
6. Payment / Payout / Tax verifies and deduplicates provider events before CL-04 consumes a normalized result.
7. GigAssignment never becomes payment truth.
8. Buyer commercial identity resolves through CustomerProfile for new workflows; User remains auth/audit identity.
9. A User cannot be treated as a seller instead of ProfessionalProfile.
10. Track Subscription & Entitlement owns plan/grant/usage truth; Order stores only historical commercial effects/evidence.
11. Buyer fee waiver and Professional commission snapshots are frozen at the defined Order pricing point and are not recalculated from future plan state.
12. ConsentLog proves generic acceptance; it does not replace AgreementElectronicConsent or AgreementSignature.
13. Finalized agreement documents are immutable. Corrections produce a new snapshot/agreement/supersession path.
14. Agreement hash proof must correspond to the exact archived bytes.
15. MediaAsset remains file truth even when CL-04 owns contextual join/grant meaning.
16. AgreementAccessGrant is not a permanent public file URL.
17. Dispute resolution does not equal financial refund execution.
18. Refund provider state is not owned by Review / Dispute.
19. ComplianceHold is the only reusable platform stop sign; no `isPayoutBlocked`, `isDisputeBlocked`, or equivalent local competing truth.
20. Review scores are reputation feedback, not verification.
21. Search is rebuildable projection and cannot become Gig/reputation truth.
22. CL-04 never writes Typesense directly.
23. Audit/AccessAudit records never replace domain lifecycle events.
24. Observability records never replace domain status.
25. Privacy / Data Erasure owns privacy-request orchestration; CL-04 only executes target instructions against its records.
26. Product archive/removal is not privacy erasure.
27. Idempotency is required on commercially consequential retryable commands.
28. Distributed concurrency is controlled by database/platform primitives, never an in-memory mutex.
29. Cross-Module reads use public facts/contracts by default, not unrestricted repositories.
30. Provider payload types do not become domain DTOs.
31. Domain events are published only after authoritative writes commit.
32. Sensitive contract/dispute payloads are minimized in logs, audit metadata, events, and analytics.
33. Unresolved transition, actor, cardinality, and retention questions must not be decided implicitly by whichever feature is implemented first.

---

## 25. Prohibited Duplicate Implementations

Coding agents must not create CL-04-local versions of:

- `currentUser`, `requireUser`, or session-to-actor utilities that duplicate `resolveAuthenticatedActor`;
- Gig/Order/Dispute-specific generic RBAC engines that duplicate `authorizeResourceAction`;
- `customerFromUser` logic outside Customer / Buyer Profile;
- local `isPremium`, `hasFeeWaiver`, `commissionRateForPlan`, usage counters, or entitlement tables;
- `isVerifiedProfessional`, `canRespondToGig` logic that rebuilds Professional Eligibility;
- local `ComplianceHold`, `payoutBlocked`, or `disputeHold` truth;
- direct Stripe webhook handlers inside Transaction / Order or Review / Dispute;
- direct Stripe refund services inside Review / Dispute;
- custom `ProcessedStripeEvent`;
- direct Typesense indexing clients in Gig/Review services;
- custom R2/S3 signed URL services in Agreement/Dispute code;
- generic consent history tables inside Agreement;
- custom audit tables that replace AuditEvent/AccessAuditLog;
- universal domain event table that replaces `OrderEvent`/`AgreementEvent` meaning;
- ad hoc queue/retry/idempotency/locking frameworks;
- local SHA-256 helper with divergent encoding/streaming rules when canonical hashing primitive exists;
- a CL-04 privacy-request state machine;
- direct Notification provider clients;
- a generic “commerce service” that owns GigAssignment + Order + Dispute statuses together.

---

## 26. Deferred / Unresolved Decisions

| Question | Why unresolved | Evidence missing/conflict | Blocks |
| --- | --- | --- | --- |
| Are Gigs single-award or multi-award? | Schema permits multiple assignments; product wording often implies selected Professional. | explicit product ruling | DB constraint and acceptance semantics. |
| What are exact Gig/GigResponse/GigAssignment transition graphs? | Enums exist without legal transition matrices. | owner-approved transition policy | mutation implementation beyond safe draft/create foundations. |
| What do Gig `completed`, Assignment `completed`, and Order `completed` each mean? | Three lifecycles can overlap. | workflow semantic ruling | completion propagation, reviews/payout triggers. |
| How is `invite_only` enforced? | Visibility enum exists; no invitation/audience schema found. | audience owner/schema | enabling invite-only mode. |
| Does CustomerProfile become non-null for new Gig/Assignment/Order records? | Current schema has optional CustomerProfile alongside User IDs; new architecture says CustomerProfile is buyer truth. | migration/backfill policy | final schema constraints. |
| What are legacy `posterUserId` / `buyerUserId` semantics? | Could be actor snapshots, relations, or migration remnants. | migration and audit decision | schema cleanup/authorization implementation. |
| What is exact Order transition matrix per source/delivery kind? | vocabulary exists; legal paths not supplied. | Transaction / Order ruling | transition service and E2E acceptance. |
| Exactly when is Order commercial policy frozen? | Evidence requires snapshot but exact boundary is not explicit. | accepted rule: Order create vs payment initiation vs agreement lock | pricing snapshot implementation. |
| What DB rule enforces “exactly one valid Order source”? | source type exists; structural XOR enforcement not confirmed. | schema decision | migration/constraint. |
| Agreement supersession/provider fields: what exact schema supports them? | operations are evidenced but detailed provider-neutral shape may be incomplete. | schema/provider decision | advanced supersession/e-sign provider integration. |
| What is valid Review rating scale? | `Int` exists without constraint. | product rule | review submission. |
| Is Review published automatically or moderated from `pending`? | default pending exists; policy absent. | moderation/reputation rule | publication automation. |
| Can a Review be edited? | no explicit revision/history policy. | product/audit rule | edit feature; initial create can proceed without edit. |
| What actor schema identifies Review author? | CustomerProfile is buyer truth but current reviewer fields are optional/incomplete. | migration/schema ruling | production review write. |
| Who may open a Dispute and how is opener represented? | `openedById` is ambiguous. | participant actor model | production dispute write. |
| Is there one lifetime Dispute per Order or a reopenable case? | `orderId @unique`; semantics absent. | product/legal rule | reopen/episode behavior. |
| What evidence model does Dispute own? | no dedicated evidence schema confirmed. | evidence-reference schema decision | richer evidence intake; basic references may be deferred. |
| What is `resolved_*` versus `closed` semantics? | statuses exist without settlement-finality rule. | lifecycle ruling | close automation. |
| Which CL-04 records require retention exemptions and for how long? | legal obligations are identified but durations are not architecture evidence. | legal/retention policy | destructive erasure and purge jobs. |
| Which actions require step-up authentication? | sensitive financial boundary exists platform-wide but per-action matrix not supplied. | root security policy | exact enforcement on refund/admin financial actions. |

No coding agent may silently convert these rows into binding architecture.

---

## 27. Architecture Decision Summary

### Binding confirmed rulings

1. CL-04 coordinates exactly three primary Deep Modules: Gig / Demand, Transaction / Order, Review / Dispute.
2. Each Module retains source-of-truth lifecycle ownership.
3. Order is Workin Ants transaction truth.
4. Payment/Payout/Tax owns provider financial rail and provider-event dedupe.
5. Track Subscription & Entitlement owns commercial policy; Transaction / Order snapshots historical effects.
6. CustomerProfile is the buyer actor truth; User remains account/authentication identity.
7. GigAssignment is accepted work relationship, not Order.
8. Review/Dispute owns adjudication truth but not refund execution or ComplianceHold.
9. ConsentLog and Order-specific Agreement execution proof are separate truths.
10. Media owns file mechanics; Transaction / Order owns Agreement document context and entitlement.
11. Search is projection.
12. Privacy owns privacy-request orchestration.
13. Audit/observability remain supplemental evidence/operations, not business truth.
14. Canonical shared operations and platform primitives must be reused.

### Proposed rulings requiring explicit acceptance before schema/API commitment

1. New CL-04 buyer-domain writes should require CustomerProfile and preserve User IDs only as authenticated actor/audit references where useful.
2. Transaction / Order should consume immutable public source DTOs from Gig / Demand and Marketplace Supply rather than read their repositories directly.
3. Response acceptance, Order creation, and dispute resolution should use canonical DB concurrency + idempotency primitives.
4. CL-04 should use transactional outbox events for cross-Module effects.
5. Review/dispute production schemas should be strengthened before implementation where current actor/evidence fields are ambiguous.

---

## 28. Coding-Agent Usage

Before changing CL-04, an implementation agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry;
5. this Cluster `architecture.md`;
6. this Cluster `build-plan.md`;
7. target Module architecture;
8. target Module implementation plan;
9. relevant dependency Module public-interface sections;
10. `progress-tracker.md`.

For a feature touching payment, entitlement, media, privacy, search, holds, or notification, the agent must also read the owning dependency Module’s public contracts and any provider/library documentation relevant to that boundary.

The implementation agent must stop and record an architecture issue rather than inventing behavior when it reaches an unresolved decision listed in Section 26.
