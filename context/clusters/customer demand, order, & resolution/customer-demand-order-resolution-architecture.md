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

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration

Gig participates in owner enumeration/assignment receipts, while AI support remains disabled under WA-R033/070.

## WA-R071 — Purpose-specific Location facts and disclosure

Order supplies current service/session/participant/restriction facts to Location, which remains the sole reveal owner. Booking/Order mismatch or unavailable facts denies disclosure; public events never include exact location.

## Domain bridge integration — 2026-10-15

Apply WA-R077; WA-R079; WA-R080 from `context/reconciliation/platform-architecture-rulings.md` only to this Cluster's named owner/consumer boundaries. The affected Module architectures incorporate the typed contracts. R077 assigns private checkout tax evidence to Order and tax interpretation to Payment; R078 uses the existing Track command with durable owner intents; R079 keeps optional reverse prize display disabled; R080 binds owner enumerators and scoped Taxonomy recipients. No cross-Cluster repository access, generic tax-location authority, duplicate actor stream or AI Gig scope is introduced. Untouched concerns retain their existing owners. Review evidence is `context/reconciliation/bridge-review-domain.json`; seven families reviewed does not complete Gate 4.
