# Customer Demand, Order & Resolution Architecture

> **Cluster ID:** CL-04  
> **Cluster name:** Customer Demand, Order & Resolution  
> **Cluster type:** `core_customer_demand_commerce_transaction_dispute`  
> **Document status:** Implementation-grade cluster architecture; confirmed rules are binding, proposed rulings require explicit acceptance, unresolved decisions remain non-authoritative  
> **Primary modules:** `gig_demand`, `transaction_order`, `review_dispute`

**Shared Operation status (CL-04-R015/R016):** exact SH IDs/names resolve to the canonical registry. SH-046 publication/outbox is Confirmed. SH-003 `queryOwnerFacts` and SH-015 `returnDecisionResult` remain Proposed ruling: use owner-specific fact/decision DTOs, not binding APIs dependent on those proposals. SH-054, SH-073, and SH-111, wherever referenced, remain Proposed ruling and conditional on separate approval. All other referenced registered operations retain their registry status and owner.

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
| `transaction_order` | Transaction / Order Module | domain | Preserve paid transaction truth and Order-specific contract proof. | `Order`, `OrderEvent`, `OrderFile`, `Agreement`, `AgreementTemplate`, `AgreementElectronicConsent`, `AgreementSignature`, `AgreementDocumentSnapshot`, `AgreementEvent`, `AgreementAccessGrant`, Order-attached `RefundStatus`. | Create Order from Offering, GigAssignment, or approved platform-facilitated screening source, freeze commercial policy, enforce agreement gates, apply payment/refund outcomes, expose transaction entitlement. | CustomerProfile, Marketplace Supply, Gig / Demand, Professional Eligibility, Track Entitlement, Consent, Payment/Payout/Tax, holds, Media. | Booking, Digital Goods, Video, Payment/Payout/Tax, Review/Dispute, Messaging, Notification, rewards. |
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

### Ownership boundaries by concern

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
- **Confirmed — CL-04-R002:** MVP Gigs are single-award: many responses, at most one accepted/current winning assignment per Gig. Competing acceptance commands must serialize. Database enforcement design remains a later approved schema/migration task; losing-response treatment, complete transition graphs, completion/dispute synchronization, and invitation authority remain unresolved. `invite_only` stays disabled.
- **Unresolved:** exact semantics of `disputed`; which completion events drive assignment/gig completion.

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
| SH-025 `authorizeOrderEntitlement` | Transaction / Order | Booking, Media, Digital Goods, Video | Confirm current Order permits a delivery action. | Order ID, actor, action | allow/deny, reasons/evidence | decision | delivery-grant truth. |
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

The [canonical registry](<../../shared/shared-operations.md>) provides permanent SH IDs, canonical owners, boundaries, and statuses. Use those exact entries without locally renaming, approving, or redefining them.

| Canonical operation | Plain-English meaning | Canonical owner/class | CL-04 consumers | Reusable mechanism | Local policy that remains local | Invocation point | Must not be duplicated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Resolve trusted Workin Ants actor from valid session/system credential. | Identity & Access | all three | typed actor context | which domain action is attempted | every protected command | feature-local current-user/session helpers |
| SH-002 `authorizeResourceAction` | Decide whether actor may perform named action in proper scope. | Role / Authority | all three | typed authorization decision | Order/Gig/Review/Dispute relationship facts and action vocabulary | before protected read/write | local role-permission engines |
| SH-004 `resolveCustomerActor` | Resolve User into commercial CustomerProfile. | Customer / Buyer Profile | Gig, Order, Review/Dispute | buyer actor resolution | whether workflow requires active buyer profile | before buyer-domain commands | `User`-only buyer helper |
| SH-005 `resolveEntitlement` | Return effective fee waiver, commission, perk, limit, etc. | Track Subscription & Entitlement | Transaction / Order primarily | commercial-policy lookup | when snapshot is taken and how effect changes Order | order pricing freeze | local premium/waiver/commission policy |
| SH-006 `consumeMeteredEntitlement` | Atomically record permitted metered usage. | Track Subscription & Entitlement | Order where buyer perk usage is metered | atomic usage receipt | which transaction event counts | after authoritative transaction use | local quota counters |
| SH-007 `recordConsentProof` / SH-008 `queryConsentProof` | Store/read generic versioned acceptance proof. | Consent & Disclosure | Transaction / Order agreement workflows | versioned proof | whether proof satisfies current Order action | before electronic execution | local generic consent tables |
| SH-011 `evaluateComplianceHold` | Return active reusable stop signs. | Admin Review / Compliance Hold | all three where action can be blocked | hold query | which target/action a hold blocks | before publish/accept/pay/refund/release/access | local `blocked` flags |
| SH-012 `requestComplianceHold` / SH-013 `releaseComplianceHold` | Create/release authoritative platform stop sign. | Admin Review / Compliance Hold | Review/Dispute primarily | hold lifecycle command | dispute evidence and requested scope | dispute open/resolution | dispute-local payout-hold state |
| SH-016 `evaluateProfessionalReadiness` | Determine Professional may perform named selling action. | Professional Eligibility | Gig / Demand; Order where seller gate needed | readiness decision | Gig response/acceptance or Order action requiring it | response submit/accept and selected Order transitions | raw cross-table readiness reconstruction |
| SH-023 `validateTaxonomyAssignment` / SH-022 `resolveTaxonomyRequirements` | Validate accepted taxonomy and derive requirement triggers. | Taxonomy & Classification | Gig / Demand | canonical classification | whether Gig publish requires classification | Gig publish/update | local tag cleaners/requirement maps |
| SH-025 `authorizeOrderEntitlement` | Confirm Order permits requested delivery/access action. | Transaction / Order | downstream CL-05 and Media contexts | source transaction decision | action-specific entitlement | delivery/access request | delivery modules inferring payment from provider |
| SH-029 `appendAuditEvent` | Append generic significant-action proof. | Audit / Event Ledger | all three | generic audit write | which actions warrant audit and safe metadata | after/beside significant actions | custom audit tables replacing domain events |
| SH-030 `recordSensitiveAccess` | Record protected file/contract/evidence access. | Audit / Event Ledger | Transaction / Order; Review/Dispute | access audit | sensitivity and contextual entitlement | agreement/evidence access | local access-log substitutes where generic rail applies |
| SH-031 `appendDomainLifecycleEvent` | Reuse append-only persistence mechanics for domain event ledgers. | shared persistence mechanism | Order/Agreement; future Gig/Dispute if approved | insert-only transaction hook | event names and lifecycle meaning | same transaction as aggregate write | one universal lifecycle ledger |
| SH-044 `executeIdempotentCommand` | Make retries produce one semantic business effect. | platform primitive | all three | key/fingerprint/result replay | command identity/conflict/replay semantics | create/accept/pay/refund/dispute commands | per-feature idempotency implementations |
| SH-051 `acquireAggregateLock` / SH-052 `withOptimisticConcurrency` | Prevent conflicting concurrent state changes. | platform primitive | Gig acceptance, Order transitions, Dispute resolution | DB locking/CAS | lock key and conflict semantics | critical transitions | in-memory mutex or bespoke lock tables |
| SH-053 `transitionLifecycleState` | Reuse state-machine plumbing while owner supplies graph. | shared mechanism / separate truth | all three | transition validation/update hook | legal transition graph | every lifecycle mutation | generic policy table owning all statuses |
| SH-046 `publishDomainEvent` | Reliably publish owner-defined event after commit. | platform outbox | all three | transactional outbox/envelope | event meaning/payload/privacy | after committed transitions | ad hoc fire-and-forget events |
| SH-045 `deduplicateDomainEvent` | Prevent duplicate consumer side effects. | event infrastructure | all consumers | inbox claim | handler identity and side effect | event handlers | custom processed-event logic for ordinary domain events |
| SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` | Run asynchronous work with retries/leases/dead-letter. | queue infrastructure | expiration, PDF, hash verification, reconciliation | worker shell | payload and terminal business meaning | background jobs | custom queue systems |
| SH-055 `runDeadlineExpiration` | Find expired records and invoke owner transition. | shared scheduler | Gig, agreement grants | scheduler batching | what expiry means | `closesAt`, grant expiry | scheduler owning domain status |
| SH-041 `requestNotification` | Request alert through Notification owner. | Notification | all three | delivery command | event meaning/recipients | lifecycle events | direct email/SMS/push dispatch |
| Search refresh/public projection command | Request Search owner to index/update/remove projection. | Search / Public Visibility public interface | Gig; review/reputation effects | projection request | source public-readiness facts | source change | Typesense client in CL-04 |
| Media signed-access/file operations | Validate and issue storage access through Media owner. | Media / File Access public interfaces | Gig, Order, Review/Dispute | file mechanics | contextual business entitlement | attachment/access flow | direct R2/S3 signed URL code |
| SH-032 `createRequestContext`, SH-033 `writeStructuredLog`, SH-037 `recordIntegrationFailure` | Correlate and observe execution without replacing domain truth. | Observability / Ops | all three | request IDs/logging/failure rail | domain failure state | all sync/async/provider boundaries | custom observability clients |

### Classification reminders

- SH-001 `resolveAuthenticatedActor`, idempotency, concurrency, outbox, queue, crypto/hashing infrastructure are **platform primitives/capabilities**.
- SH-025 `authorizeOrderEntitlement`, readiness queries, Track resolution, Search refresh are **Module public interfaces**.
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

**Approved reputation handoff (CL-04-R005):** Review / Dispute owns Review inclusion and aggregate calculation. It supplies its owner-issued reputation result/facts for a ProfessionalProfile through the explicit Module contract: target ProfessionalProfile ID, derived ratingAverage/ratingCount, and source/projection version evidence. Professional Eligibility consumes that result, owns writes to its `ProfessionalProfile.ratingAverage`/`ratingCount`, and supplies the resulting Professional projection to Search. Review / Dispute must not mutate the ProfessionalProfile repository. SH-115 supplies shared projection/version/replay mechanics, not Review policy or Profile ownership. Dependency failure leaves Review truth committed and projection work retryable; exact transport/API naming is not newly selected here.

### 12.7 Completed Order produces Review

```text
Order completed
→ outbox event
→ Review / Dispute exposes review eligibility
→ buyer submits review
→ Review truth written
→ publication/moderation policy applied
→ Review / Dispute calculates authoritative reputation result
→ Professional Eligibility consumes the result and writes its derived ProfessionalProfile fields
→ Search consumes the resulting Professional projection
→ notification/reward consumers react
```

**Approved refund coordination (CL-04-R001).** Review / Dispute adjudicates → Transaction / Order coordinates SH-108 `requestOrderRefund` → Payment / Payout / Tax executes the provider refund → Order applies the verified provider-neutral result to RefundStatus/Order → Review / Dispute consumes settlement. Review / Dispute must not call Payment's refund executor directly.

### 12.8 Dispute with refund outcome

```text
authorized participant opens Dispute
→ Review / Dispute writes Dispute
→ requests ComplianceHold
→ Order enters transaction dispute effect through public command
→ admin/reviewer adjudicates resolved_refund with required SH-014 assurance
→ Transaction / Order receives the decision and coordinates SH-108 requestOrderRefund
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
| CL-01 Customer / Buyer Profile | CL-04 | CustomerProfile buyer context | Customer Profile | SH-004 `resolveCustomerActor` / profile query | storing buyer policy on User or recreating CustomerProfile |
| CL-01 Track Subscription & Entitlement | Transaction / Order | buyer fee waiver, seller commission, usage receipt | Track | SH-005 `resolveEntitlement`, SH-006 `consumeMeteredEntitlement` | local premium/commission/waiver truth |
| CL-01 Identity/Authority/Consent | CL-04 | actor, permission decision, generic consent proof | respective owners | canonical shared interfaces | local auth/authz/consent engines |
| CL-02 Taxonomy | Gig / Demand | category/domain/tag validity and requirement triggers | Taxonomy | public validation query | copied taxonomy tables/rules |
| CL-02 Search | Gig/Review effects | projection request | Search | Search refresh/upsert interface | direct Typesense writes |
| CL-03 Marketplace Supply | Transaction / Order | Offering checkout source and pricing tier facts | Marketplace Supply | immutable checkout source query | Order repository reading Offering internals |
| CL-03 Professional Eligibility | Gig/Order | selling readiness decision | Professional Eligibility | SH-016 `evaluateProfessionalReadiness` | raw compliance joins in CL-04 |
| CL-03 Payment/Payout/Tax | Order/Dispute | payment, sales tax, refund, payout effects | Payment/Payout/Tax for rail; Order for transaction effect | provider-neutral commands/events | Stripe webhook handling in CL-04 |
| CL-05 Delivery | Transaction / Order | delivery request/result; Order entitlement | Order + delivery owner | SH-025 `authorizeOrderEntitlement`, delivery events | Order owning Booking/Media/Video lifecycles |
| CL-07 Messaging/Notification | all CL-04 | communication context and alerts | Messaging/Notification | context-thread and notification interfaces | direct provider dispatch |
| CL-08 Privacy/Location | CL-04 | erasure instructions, retention decisions, fuzzy/exact location gates | Privacy/Location owners | executor contracts | feature-owned privacy workflow or coordinate fuzzing |
| CL-09 Holds/Audit/Ops/Moderation | CL-04 | holds, audit, access logs, moderation decisions, ops failures | CL-09 Modules | public commands/events | local hold/audit/moderation/incident systems |
| CL-10 Rewards | Review/Order events | eligible business event | source Module | domain event | reward mutation inside CL-04 |

---

## 14. Authentication and Authorization

- Every protected operation starts from SH-001 `resolveAuthenticatedActor`.
- Buyer-domain commands resolve `CustomerProfile`; authentication User ID may be retained for actor/audit trace.
- Professional commands use `ProfessionalProfile` plus authenticated User actor context.
- SH-002 `authorizeResourceAction` interprets authority. CL-04 supplies relationship facts:
  - Gig poster/customer relationship;
  - GigResponse Professional ownership;
  - Order buyer/seller participant relationship;
  - Review eligible buyer;
  - Dispute participant/admin relation;
  - Agreement signer/participant relation.
- Admin/support roles are not blanket permission to read contracts, private evidence, or sensitive files. Contextual access decisions and sensitive-access audit still apply.
- Sensitive financial operations may require SH-014 `requireStepUpForSensitiveAction` when root policy classifies them as high risk.
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

Use canonical SH-046 `publishDomainEvent` with a transactional outbox whenever committed state must reliably trigger external work. Do not emit network calls inside the owner transaction as the only delivery mechanism.

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

Provider failures use Observability / Ops SH-037 `recordIntegrationFailure` and owner-local workflow state where business meaning requires it.

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

Viewing/downloading finalized agreements or dispute evidence should use SH-030 `recordSensitiveAccess` with minimized metadata.

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
8. resolved refund → Order SH-108 coordination → Payment execution → Order refund effect → Dispute settlement/finality under its approved rules.

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
33. Unresolved transitions, historical actor migration, physical assignment enforcement, and retention questions must not be decided implicitly by whichever feature is implemented first.

---

## 25. Prohibited Duplicate Implementations

Coding agents must not create CL-04-local versions of:

- `currentUser`, `requireUser`, or session-to-actor utilities that duplicate SH-001 `resolveAuthenticatedActor`;
- Gig/Order/Dispute-specific generic RBAC engines that duplicate SH-002 `authorizeResourceAction`;
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

**Confirmed commercial freeze boundary (CL-04-R003):** resolve authoritative source and Track entitlement decisions, then freeze source pricing, buyer fee-waiver effect, seller commission effect, and supporting Track grant/evidence references before Agreement execution or payment initiation. An initial/draft Order may exist before freeze. Frozen effects must never be recomputed from later subscription state.

**Confirmed actor semantics (CL-04-R007):** CustomerProfile is required semantic buyer identity for new CL-04 buyer-domain records; User remains authenticated account/audit identity. After CustomerProfile migration, Gig/GigAssignment/Order buyer ownership must not be authorized from User ID alone. A Review author resolves to the Order's buyer CustomerProfile. Dispute opener proof must distinguish customer, professional, and privileged/admin initiation with an unambiguous typed domain actor; this representation requirement does not approve which actors may open a Dispute. Historical backfill, permanent legacy-User reference semantics, and the physical typed-opener schema remain unresolved.

**Binding marketplace-source invariant (CL-04-R008, scope amended by WA-R003):** for seller-backed marketplace Orders, `sourceType=offering` requires only its Offering source and `sourceType=gig_assignment` requires only its GigAssignment source. Mixed sources or mismatched discriminators are invalid. The approved platform-facilitated screening source is a separate family: it references a Trust-owned package/quote, requires no Professional seller, and must not fabricate an Offering or GigAssignment. Its discriminator, reference, participant constraints and migration are not yet represented in Prisma. Transaction / Order must enforce one valid source family in domain validation and coordinated database constraints before enabling that family. No schema/deployment change is implied.

**Mandatory durable Dispute proof (CL-04-R010):** persist the authorized adjudicator, decision, basis/reason, decision timestamp, refund amount/basis where applicable, idempotency/correlation identity, hold request/release correlation, settlement/refund correlation, and whether required downstream steps are pending or completed. This domain proof must survive retries/outages. Generic AuditEvent, QueueJob, or mutable `adminNotes` cannot substitute for it. The final decision/event/workflow persistence design remains unresolved and must be approved before production adjudication.

**Binding retention boundary (CL-04-R011):** hard deletion of an Order must not cascade-delete retained transaction, Agreement, Review, Dispute, or domain-history evidence without owner-specific Privacy/retention evaluation. Privacy issues the instruction; each owner enumerates its targets, evaluates retention/exemption facts, erases/anonymizes eligible data, preserves/minimizes retained evidence, and returns proof to Privacy. Database cascades must not provide an alternate destructive path. Existing cascade behavior requires a later approved database correction; legal retention durations remain unresolved.

**Confirmed sensitive-action gate (CL-04-R021):** refund/release adjudication or actions that cause or authorize financial movement require SH-014 `requireStepUpForSensitiveAction`, owned by Identity & Access. This gate does not approve finality, grant TTL/reuse/renewal, manual-signature procedure, non-payout hold effects, signer anonymization, or retention periods. Optional external e-sign adoption must not block the provider-neutral Agreement domain.

### Approved local Shared Operation mappings

- SH-107 `createChargeableOrder` — Confirmed; Transaction / Order owns creation. `createOrderFromOffering` and `createOrderFromGigAssignment` are typed source-specific specializations of this responsibility, not separate creation engines.
- SH-109 `snapshotExternalDecision` — Confirmed; Order freezes external Track decision/evidence while Track retains current policy truth.
- SH-110 `createDomainSnapshot` — Confirmed; Order owns immutable source/commercial snapshots where the registered semantics apply.
- SH-026 `authorizeContextualResourceAccess` — Confirmed; the context owner decides Agreement/Dispute business access; Media retains signed transport mechanics.
- SH-125 `recordDomainAccessEvent` — Confirmed; Agreement/domain access proof remains separate from generic AccessAuditLog.
- SH-111 `renderDocument` — Proposed ruling, conditional future shared normalization; not a required confirmed dependency. Transaction / Order retains its owner-local/provider-neutral rendering workflow until separate Shared Operations approval.

## 26. Deferred / Unresolved Decisions

| Question | Why unresolved | Evidence missing/conflict | Blocks |
| --- | --- | --- | --- |
| How is the approved single-award MVP invariant enforced in the database? | At most one accepted/current winning assignment is binding; current schema permits multiple assignments. | later enforcement design/migration | database readiness, not award-cardinality policy |
| What are exact Gig/GigResponse/GigAssignment transition graphs? | Enums exist without legal transition matrices. | owner-approved transition policy | mutation implementation beyond safe draft/create foundations. |
| What do Gig `completed`, Assignment `completed`, and Order `completed` each mean? | Three lifecycles can overlap. | workflow semantic ruling | completion propagation, reviews/payout triggers. |
| How is `invite_only` enforced? | Visibility enum exists; no invitation/audience schema found. | audience owner/schema | enabling invite-only mode. |
| How are CustomerProfile references physically enforced/backfilled? | CustomerProfile is required semantic identity for new buyer-domain records under CL-04-R007; current fields remain nullable. | historical backfill/legacy User semantics | physical migration and final schema constraints |
| What are legacy `posterUserId` / `buyerUserId` semantics? | Could be actor snapshots, relations, or migration remnants. | migration and audit decision | schema cleanup/authorization implementation. |
| What is exact Order transition matrix per source/delivery kind? | vocabulary exists; legal paths not supplied. | Transaction / Order ruling | transition service and E2E acceptance. |
| Commercial snapshot boundary | Confirmed CL-04-R003: resolve source/Track decisions and freeze before Agreement execution/payment initiation; draft Order may precede freeze. | Detailed fee/tax/proceeds meanings remain unresolved. | affected commercial calculation, not freeze ordering |
| Order source XOR implementation | CL-04-R008 approves domain validation plus database enforcement matching `sourceType`. | approved migration/constraint implementation | database readiness; source invariant is binding |
| Agreement supersession/provider fields: what exact schema supports them? | operations are evidenced but detailed provider-neutral shape may be incomplete. | schema/provider decision | advanced supersession/e-sign provider integration. |
| What is valid Review rating scale? | `Int` exists without constraint. | product rule | review submission. |
| Is Review published automatically or moderated from `pending`? | default pending exists; policy absent. | moderation/reputation rule | publication automation. |
| Can a Review be edited? | no explicit revision/history policy. | product/audit rule | edit feature; initial create can proceed without edit. |
| How is the approved Review-author identity persisted/backfilled? | Review author resolves to the Order buyer CustomerProfile under CL-04-R007. | physical migration/history treatment | production schema readiness |
| Who may open a Dispute and how is opener represented? | `openedById` is ambiguous. | participant actor model | production dispute write. |
| Is there one lifetime Dispute per Order or a reopenable case? | `orderId @unique`; semantics absent. | product/legal rule | reopen/episode behavior. |
| What evidence model does Dispute own? | no dedicated evidence schema confirmed. | evidence-reference schema decision | richer evidence intake; basic references may be deferred. |
| What is `resolved_*` versus `closed` semantics? | statuses exist without settlement-finality rule. | lifecycle ruling | close automation. |
| Which CL-04 records require retention exemptions and for how long? | legal obligations are identified but durations are not architecture evidence. | legal/retention policy | destructive erasure and purge jobs. |
| Other sensitive-action rules | Refund/release actions causing or authorizing financial movement require SH-014. | remaining action-specific policy | actions outside the approved financial gate |

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

### Confirmed reconciliation rulings

- **Confirmed CL-04-R007:** new buyer-domain records require CustomerProfile semantically; User remains account/audit identity. Historical backfill and long-term legacy references are unresolved.
- **Confirmed SH-046 (not a proposal):** CL-04 uses transactional outbox events for cross-Module effects.

### Proposed rulings requiring explicit acceptance before schema/API commitment

1. Transaction / Order should consume immutable public source DTOs from Gig / Demand and Marketplace Supply rather than read their repositories directly.
2. Response acceptance, Order creation, and dispute resolution should use canonical DB concurrency + idempotency primitives.
3. Review/dispute production schemas should be strengthened before implementation where current actor/evidence fields are ambiguous.

---

## 28. Coding-Agent Usage

Before changing CL-04, an implementation agent must read, in order:

1. [context map](<../../context-map.md>) and its authority-by-concern/path guidance;
2. [current project overview](<../../project-overview-v3.md>);
3. available concern-specific architecture and standards; root architecture/build plan and `code-standards.md` are currently missing, not available prerequisites;
4. Canonical Shared Operations Registry;
5. this Cluster `architecture.md`;
6. this Cluster `build-plan.md`;
7. target Module architecture;
8. target Module implementation plan;
9. relevant dependency Module public-interface sections;
10. progress evidence if available; a dedicated `progress-tracker.md` is currently missing.

For a feature touching payment, entitlement, media, privacy, search, holds, or notification, the agent must also read the owning dependency Module’s public contracts and any provider/library documentation relevant to that boundary.

The implementation agent must stop and record an architecture issue rather than inventing behavior when it reaches an unresolved decision listed in Section 26.

## WA-R003 — Approved platform-facilitated screening source (2026-09-29)

SH-107 authorizes three conceptual source families: Offering, accepted GigAssignment, and platform-facilitated screening service. The first two retain their Professional seller rules. Screening has a Customer buyer and explicit platform service context, with no Professional seller. Organization verification uses the business/EIN path; it is not a personal screening subject.

Trust owns VerificationPackage/check-package meaning, itemized quote, requirements, consent sufficiency and screening results. Order freezes the authoritative package/quote reference, source version, amount/currency, applicable fee/tax/disclosure facts and buyer attribution; Payment executes the financial rail. An authoritative paid Order outcome permits Trust to continue, but never proves screening clearance. Source contracts must reject stale/unavailable quotes and replay the original Order under the same semantic purchase key.

Voluntary Candidate/Professional screening is optional, subject-initiated and subject-paid by default. A required workflow gate does not silently create employer sponsorship; a different payer/initiator requires the separately approved sponsored workflow described by the canonical registry.

Implementation remains gated on a source-specific schema/constraint and transition contract, paid-result correlation, replay/refund/recovery semantics, and provider/legal requirements. Do not reuse marketplace seller-acceptance or fulfillment assumptions for screening. These are execution prerequisites, not a question about whether paid screening is allowed. Existing Prisma `OrderSourceType` values describe represented structure only.


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
