# Transaction / Order Module Architecture

> **Module ID:** `transaction_order`  
> **Module name:** Transaction / Order Module  
> **Module type:** `domain`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** CL-04 — Customer Demand, Order & Resolution  
> **Document status:** Implementation-grade Module architecture. Confirmed rulings are binding. Proposed rulings require explicit acceptance before schema/API commitment. Unresolved decisions remain non-authoritative.  
> **Audience:** coding agents, developers, reviewers, migration authors, test authors, provider-integration authors, maintainers.  

---

## 1. Module Header

This document defines the stable architecture for `transaction_order` only. It is subordinate to the Workin Ants root architecture and the CL-04 Cluster architecture, and it is more specific than those documents for Transaction / Order-owned truth, policies, interfaces, and implementation boundaries.

### Relationship to root architecture

Root Workin Ants architecture remains authoritative for platform-wide ownership, shared mechanisms, provider boundaries, security posture, privacy orchestration, and cross-cutting services. This Module must consume those decisions rather than restating or replacing them.

### Relationship to CL-04 architecture

CL-04 coordinates `gig_demand`, `transaction_order`, and `review_dispute`; it does not own their lifecycles. This Module owns Order transaction truth and Order-specific agreement truth. Gig / Demand owns accepted demand truth. Review / Dispute owns review and dispute truth.

### Update rule

Update this file only when a binding decision changes one of the following:

- Module ownership;
- lifecycle authority;
- schema meaning;
- public command/query contract;
- commercial snapshot semantics;
- agreement execution semantics;
- cross-Module integration boundary;
- compliance/retention boundary;
- required shared operation.

Build progress, code organization changes, or implementation convenience must not silently redefine this architecture.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Preserve Workin Ants' authoritative transaction record when an accepted marketplace source becomes commercial work, and preserve the Order-specific agreement evidence that governs that transaction where an agreement is required.

### Goal

Produce a durable answer to:

> What was purchased or commissioned, by which CustomerProfile, from which ProfessionalProfile, from which approved source, at what frozen commercial terms, under what agreement, what state did fulfillment reach, and what transaction effect followed payment, refund, cancellation, or dispute?

### What enters

- authenticated User/system actor context;
- resolved `CustomerProfile` buyer facts;
- `ProfessionalProfile` seller facts and, where required, readiness decisions;
- immutable Offering checkout facts from Marketplace Supply;
- immutable accepted `GigAssignment` checkout facts from Gig / Demand;
- Track-owned buyer fee-waiver and seller commission entitlement decisions;
- generic consent proof from Consent & Disclosure;
- `ComplianceHold` decisions;
- normalized provider-neutral payment/refund results from Payment / Payout / Tax;
- validated `MediaAsset` facts and Media-owned signed-access operations;
- Booking/delivery facts when an Order transition depends on them;
- dispute adjudication/settlement effects through Review / Dispute public contracts;
- Privacy / Data Erasure target instructions.

### What leaves

- authoritative `Order` state;
- immutable or versioned commercial snapshot evidence on Order;
- append-only `OrderEvent` transaction history;
- contextual `OrderFile` relationships;
- authoritative Order-specific `Agreement` execution state;
- agreement consent/signature/document/hash/access proof;
- `AgreementEvent` history;
- Order delivery-entitlement decisions for Booking, Media, Digital Goods, and Video consumers;
- provider-neutral payment/refund commands and normalized result application;
- domain events for downstream modules;
- audit/access-audit/notification requests;
- privacy target execution results.

### Business transformation

```text
Approved commercial source
+ buyer/seller actor facts
+ external commercial-policy decisions
→ Order source and participant truth
→ frozen pricing/entitlement evidence
→ agreement gate where required
→ verified payment effect
→ fulfillment transaction state
→ completion/cancellation/refund/dispute transaction effect
→ downstream entitlement and event facts
```

### Why this deserves its own Module boundary

Order is platform transaction truth and has a lifecycle distinct from Offering, GigAssignment, Booking, Payment, Payout, Review, and Dispute. Agreement execution also contains domain-specific consent, signature, document, hash, retention, and access semantics that must not be absorbed by Booking, Media, Consent, Payment, or a generic document service.

---

## 3. Owned Truth

### 3.1 Schemas/models owned

| Record | Meaning |
| --- | --- |
| `Order` | Authoritative commercial transaction record sourced from one Offering or one accepted GigAssignment. |
| `OrderEvent` | Append-only domain timeline for Order lifecycle changes and meaningful transaction events. |
| `OrderFile` | Transaction-context relationship between an Order and a MediaAsset, with buyer/professional/admin/system role meaning. |
| `AgreementTemplate` | Versioned reusable agreement template configuration used to instantiate Order-specific agreements. |
| `Agreement` | Authoritative contract/execution aggregate attached to one Order under the current schema. |
| `AgreementElectronicConsent` | Order-specific proof of electronic execution consent, decline, withdrawal, or manual opt-out, optionally linked to generic `ConsentLog` proof. |
| `AgreementSignature` | One signer-role execution record and associated proof for an Agreement. |
| `AgreementDocumentSnapshot` | Immutable versioned rendered/signed contract document proof bound to exact MediaAsset bytes and SHA-256 hash. |
| `AgreementEvent` | Append-only Agreement lifecycle/evidence event ledger. |
| `AgreementAccessGrant` | Order-contract contextual authorization for short-lived access to an Agreement or document snapshot. |

### 3.2 Enums/statuses owned

- `OrderStatus`
- `OrderSourceType`
- `OrderEventActor`
- `FileRole`
- `RefundStatus`
- `AgreementStatus`
- `AgreementTemplateStatus`
- `AgreementGenerationEngine`
- `AgreementDocumentStatus`
- `AgreementSignatureRole`
- `AgreementSignatureStatus`
- `AgreementConsentStatus`
- `AgreementConsentMethod`
- `AgreementEventType`
- `AgreementAccessGrantStatus`
- `AgreementHashAlgorithm`

### 3.3 Lifecycles owned

- Order lifecycle;
- Order-attached refund-status lifecycle;
- Agreement-template lifecycle;
- Order-specific Agreement lifecycle;
- Agreement electronic-consent/manual-opt-out lifecycle;
- Agreement signature lifecycle;
- Agreement document-snapshot lifecycle;
- Agreement access-grant lifecycle.

### 3.4 Source-of-truth records

- `Order.status` is transaction state, not Stripe/provider state.
- `Order.refundStatus` is the Order-facing refund attachment, not provider refund execution truth.
- `OrderEvent` is Order-domain history, not generic AuditEvent.
- `Agreement.status` is Order-specific contract execution state, not ConsentLog status.
- `AgreementSignature` is execution proof, not a signature image URL.
- `AgreementDocumentSnapshot` is immutable document/hash proof, not MediaAsset itself.
- `AgreementAccessGrant` is contract-context entitlement, not MediaAccessGrant or a permanent URL.

### 3.5 Projections owned

No public search projection is owned by this Module. Any Order list/detail DTO, participant view, or agreement package DTO is a read model over Module truth, not an independent source-of-truth projection.

### 3.6 Snapshots/proof owned

- commercial pricing/entitlement snapshot on `Order`;
- source Track subscription/grant references used to explain the frozen transaction result;
- template key/version captured on `Agreement`;
- agreement disclosure version/text hash;
- signature-mark hash and signer execution timestamps;
- document SHA-256 hash and previous-document hash;
- agreement event hash-chain fields where the proposed `hashChainRecords` mechanism is adopted;
- archival/retention-lock application fields on Agreement.

### 3.7 Policies/invariants owned

- exactly-one-valid-Order-source policy;
- Order transition policy;
- commercial snapshot freeze policy;
- which Order actions require agreement readiness;
- how normalized payment/refund outcomes affect Order state;
- participant relationship facts supplied to Role / Authority;
- Order delivery-entitlement decision policy;
- agreement template selection and execution requirements;
- agreement consent/signature completion policy;
- document finalization/versioning policy;
- AgreementAccessGrant context, scope, expiry, and revocation policy;
- transaction-specific privacy execution behavior after Privacy owner supplies disposition/retention decision.

### Ownership conflict resolved

Historical registry material lists Track subscription/grant/usage records under Transaction / Order. Current Cluster and Track architecture establish Track Subscription & Entitlement as the owner of plans, subscriptions, grants, usage events, and counters. **Binding Module interpretation:** Transaction / Order owns only the historical downstream commercial effect and evidence stored on `Order`; it must not own Track lifecycle records.

---

## 4. Explicit Non-Ownership

This Module must not own or recreate:

| Adjacent owner | Truth/responsibility that remains external |
| --- | --- |
| Identity & Access | authentication, session truth, User lifecycle, step-up challenge/session lifecycle. |
| Role / Authority | generic permission interpretation and reusable authorization infrastructure. |
| Customer / Buyer Profile | CustomerProfile lifecycle and buyer actor resolution. |
| Professional Eligibility | ProfessionalProfile lifecycle and composed selling/readiness decisions. |
| Marketplace Supply | Offering, PricingTier, service/product/course/bundle lifecycle and source pricing truth before Order snapshot. |
| Gig / Demand | Gig, GigResponse, GigAssignment lifecycle and accepted-assignment source truth. |
| Track Subscription & Entitlement | plans, subscriptions, grants, usage events, counters, current waiver/commission policy. |
| Payment / Payout / Tax | raw Stripe/provider adapters, webhook signature verification, `ProcessedStripeEvent`, provider dedupe, payment/refund execution, KYC, tax, sales tax, payout requests/transfers, financial ledger. |
| Booking & Calendar | BookingHold, Booking, slot locks, availability, calendar provider state. |
| Media / File Access | MediaAsset storage, upload validation, malware scan, processing, object keys, private-object transport, MediaAccessGrant, signed URLs. |
| Consent & Disclosure | generic ConsentLog lifecycle, consent version catalog, generic acceptance proof. |
| Review / Dispute | Review and Dispute lifecycle and adjudication truth. |
| Admin Review / Compliance Hold | ComplianceHold lifecycle and reusable stop-sign truth. |
| Messaging | Thread, ThreadParticipant, Message lifecycle. |
| Notification | Notification persistence, routing, email/SMS/push delivery and templates. |
| Audit / Event Ledger | generic AuditEvent and AccessAuditLog. |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob/Target, retention-exemption records, erasure/export orchestration. |
| Search / Public Visibility | SearchUpsertEvent, Typesense/search projection, indexing/reconciliation. |
| Observability / Ops | IntegrationFailure, QueueJob, SystemEvent, OpsIncident and generic telemetry infrastructure. |
| Video / Digital Goods / Delivery Modules | playback/download/access-grant and provider-resource lifecycles. |

Specific prohibitions:

- no local `isPremium`, `buyerHasFeeWaiver`, `commissionRateForPlan`, or Track usage counter;
- no direct Stripe webhook route owned by Transaction / Order;
- no custom `ProcessedStripeEvent` equivalent;
- no direct refund provider client;
- no generic current-user/session helper;
- no generic RBAC engine;
- no local `orderBlocked`/`payoutBlocked`/`disputeBlocked` boolean truth;
- no direct R2/S3 presigned URL implementation;
- no local file scanner;
- no generic ConsentLog replacement;
- no local PrivacyRequest state machine;
- no generic universal lifecycle ledger replacing OrderEvent/AgreementEvent.

---

## 5. Module Architecture Principles

1. **Order is transaction truth.** Provider financial state can cause a verified Order transition but cannot replace Order.
2. **Exactly one commercial source.** An Order is sourced from either an Offering or a GigAssignment according to `OrderSourceType`; invalid or mismatched combinations are rejected and must be database-enforced after the schema ruling is accepted.
3. **CustomerProfile is buyer-domain truth.** `buyerUserId` may remain auth/audit traceability, but new commercial behavior must not treat User as the complete buyer domain identity.
4. **ProfessionalProfile is seller identity.** User cannot be substituted for seller context.
5. **Historical commercial policy is frozen.** Current Track policy never retroactively changes a historical Order.
6. **Payment rail is external.** Payment / Payout / Tax verifies, deduplicates, and translates provider events before this Module applies a normalized result.
7. **Agreement proof is contextual.** ConsentLog, MediaAsset, AuditEvent, and provider envelopes support Agreement but do not replace its lifecycle.
8. **Finalized agreement bytes are immutable.** Corrections create a new snapshot or an approved supersession path.
9. **Hash exact bytes.** The Agreement owner binds the canonical shared checksum result to a document snapshot.
10. **Shared mechanism does not merge truth.** Locks, idempotency, queue execution, lifecycle plumbing, access-grant mechanics, and hashing are shared; Order/Agreement records remain local truth.
11. **Outbox after commit.** Cross-Module effects occur from committed authoritative state, not fire-and-forget callbacks inside the transaction.
12. **No direct cross-Module repository coupling by default.** Consume owner public contracts/DTOs.
13. **Privacy orchestrates; this Module executes.** No local legal-rights workflow.
14. **Audit and observability supplement truth.** They never replace OrderEvent or AgreementEvent.
15. **Unresolved decisions block affected production behavior.** Coding agents must not manufacture missing lifecycle, migration, legal, or retention rules.

---

## 6. Proposed Folder / Code Structure

```text
src/modules/transaction-order/
  application/
    commands/
      create-order-from-offering.ts
      create-order-from-gig-assignment.ts
      resolve-and-snapshot-order-pricing.ts
      apply-payment-confirmation.ts
      apply-payment-failure.ts
      apply-refund-outcome.ts
      accept-order.ts
      start-order-fulfillment.ts
      record-order-delivery.ts
      complete-order.ts
      cancel-order.ts
      attach-order-file.ts
    queries/
      get-order.ts
      list-orders-for-actor.ts
      get-order-timeline.ts
      get-order-payment-requirements.ts
      authorize-order-entitlement.ts
    agreements/
      commands/
      queries/
      orchestration/
    privacy/
      execute-privacy-target.ts
      enumerate-privacy-data.ts
    reconciliation/
      reconcile-order-effects.ts
  domain/
    order/
      policies/
      transitions/
      pricing/
      events/
    agreement/
      policies/
      transitions/
      evidence/
      events/
    errors/
    reason-codes/
  contracts/
    public-commands.ts
    public-queries.ts
    source-dtos.ts
    payment-result.ts
    privacy-target.ts
    events.ts
  infrastructure/
    repositories/
    document-generation/
      ports.ts
      puppeteer-adapter.ts        # only if selected/confirmed
      pdfkit-adapter.ts           # only if selected/confirmed
    workers/
      agreement-document-worker.ts
      agreement-grant-expiration-worker.ts
      reconciliation-worker.ts
  public/
    index.ts
    contracts.ts
  ui/
    order/
    agreement/
  tests/
    unit/
    contract/
    integration/
    concurrency/
    privacy/
```

Do not create a folder merely to mirror a conceptual layer. In particular, no `providers/stripe`, `storage/`, `auth/`, `rbac/`, `entitlements/`, `notifications/`, or generic `shared/` folder belongs here unless this Module is the canonical owner of that mechanism.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery/UI | Participant Order views, checkout/agreement progress surfaces, template admin surface if approved. | provider secrets, raw cross-Module repositories, authorization policy engine. |
| Application services | Command/query orchestration, shared-operation invocation, transaction boundaries, owner contract composition. | neighboring Module lifecycle rules. |
| Domain policy | Order/Agreement transition rules, source integrity, pricing freeze, agreement gate, entitlement decision. | current Track policy, payment-provider mapping, generic RBAC. |
| Repositories/data access | Transaction / Order-owned models only; atomic aggregate/event writes. | arbitrary reads/writes of Gig, Offering, Track, Payment, Hold, Media tables. |
| Workers | Agreement rendering/finalization, grant expiration, owner-local reconciliation. | generic queue engine or provider payment worker. |
| Document adapters | Render a domain-approved Agreement input into bytes through a provider-neutral port. | contract legal meaning, file storage truth, payment processing. |
| Contracts | Stable public DTOs, command/query/result envelopes, event schemas. | raw provider payload types. |
| Privacy executor | Enumerate and apply Privacy-owned instructions to local records. | PrivacyRequest/DataErasure lifecycle. |

---

## 8. Data Model

### `Order`

**Purpose:** authoritative transaction aggregate.

**Key relationships:** optional `offeringId`, unique optional `gigAssignmentId`, buyer User reference, optional CustomerProfile reference, seller ProfessionalProfile, Order files/events, optional Agreement, Review, Dispute, Thread, and downstream relations to Booking, payout/tax/digital-delivery records owned elsewhere.

**Authoritative fields:** `status`, `sourceType`, source IDs, participant IDs, price/currency, refundStatus, commercial snapshot fields, fulfillment notes/timestamps, `dataSensitivity`.

**Lifecycle fields:** `status`, `paidAt`, `acceptedAt`, `deliveredAt`, `completedAt`, `cancelledAt`, `refundStatus`.

**Commercial snapshot fields:** `priceCents`, `buyerPlatformFeeCents`, `buyerPlatformFeeWaived`, Track subscription/grant references, `sellerCommissionBps`, `sellerCommissionCents`, `pricingSnapshotJson`.

**Provider-correlation fields currently present:** Stripe checkout/payment/transfer/application-fee fields. These are not provider truth and require a later provider-neutrality/field-semantics ruling.

**Uniqueness:** `gigAssignmentId @unique` establishes at most one Order per GigAssignment. Offering purchases currently have no equivalent one-per-source rule because multiple purchases of an Offering can be valid.

**Concurrency-sensitive areas:** Order creation from a source, pricing freeze, payment application, seller acceptance, completion, cancellation, refund/dispute effects.

**Retention/privacy:** financial/commercial records may require payment/tax/dispute/fraud/legal retention. Nonessential personal metadata may be anonymizable only under Privacy-owned instructions and approved retention rules.

**Known schema issue:** source XOR is not structurally enforced by the visible schema; `customerProfileId` is optional despite current architecture naming CustomerProfile buyer truth.

### `OrderEvent`

Append-only Order-domain history containing actor class, actor ID, from/to status, event name, reason, metadata, and timestamp. `name` is currently free text; a controlled vocabulary/registry is a consolidation candidate. Event write should be atomic with authoritative Order mutation.

### `OrderFile`

Contextual join between Order and ready MediaAsset. `role` expresses transaction meaning. Deleting/detaching the contextual row does not imply deleting the underlying MediaAsset. Media readiness, storage, scans, and URL issuance remain Media-owned.

### `AgreementTemplate`

Versioned template identified by unique `(key, version)`. Holds generation engine, template body/media proof, signature requirements, electronic-consent requirement, manual-opt-out configuration, creator/approver facts, and status. Active versions must not be edited in place in a way that invalidates historical execution evidence.

### `Agreement`

Order-specific agreement aggregate. Current schema enforces `orderId @unique`, meaning one Agreement row per Order. It also contains a `supersededByAgreementId` relationship, which conflicts with true multi-Agreement-per-Order supersession. This is unresolved and blocks a production supersession design.

Important authoritative fields include template identity/version, status, generation/signing-provider correlation, execution requirement flags, finalization/archive/retention fields, void/supersession fields, and child consent/signature/document/event/access records.

Legacy/compatibility fields (`buyerSigUrl`, `professionalSigUrl`, `pdfMediaId`, `finalDocumentHash`) coexist with normalized signature/document-snapshot records and require a cleanup ruling. They must not become preferred truth merely because they are convenient.

### `AgreementElectronicConsent`

Order-specific execution-consent proof. It references User and optionally a generic ConsentLog. It records exact disclosure version/hash, method, manual alternative/opt-out fields, minimized request evidence, and timestamps. A valid ConsentLog does not by itself mark this record consented.

### `AgreementSignature`

Signer-role execution proof with optional User, linked contextual consent, typed name/signature mark hash, optional signature-image MediaAsset, signed document snapshot, minimized request evidence, and lifecycle timestamps. A signature image/URL is not legal proof by itself.

### `AgreementDocumentSnapshot`

Immutable Agreement document version. Unique `(agreementId, version)`. Stores MediaAsset reference, document status, SHA-256 hash, previous document hash, render engine, safe file metadata, audit-footer hash, and verification/tamper timestamps.

### `AgreementEvent`

Append-only Agreement history with controlled `AgreementEventType`, from/to status, target references, safe metadata, request ID, and optional hash-chain fields. Generic AuditEvent remains separate.

### `AgreementAccessGrant`

Short-lived contextual contract-access grant with status, token/signed-URL hashes, reason/denial/revocation fields, minimized request evidence, grant/use/expiry/revocation times, and optional specific document snapshot. Shared grant mechanics may be reused, but this record remains Agreement truth.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Order

**Status vocabulary:**

```text
draft
awaiting_agreement
pending_payment
paid
awaiting_seller
accepted
in_progress
delivered
completed
cancelled
refunded
disputed
```

**Transition owner:** Transaction / Order only.

**Triggers:** owner commands, normalized Payment results, Review / Dispute settlement effects, and approved delivery facts.

**Valid transitions:** **unresolved as a complete binding matrix.** The evidence defines vocabulary and major workflow direction but explicitly states that the exact graph may vary by source/delivery kind. Implementation may build creation/read foundations but must not invent a universal production transition graph.

**Conceptual progression, not a binding state machine:**

```text
draft
→ awaiting_agreement? 
→ pending_payment
→ paid
→ awaiting_seller? 
→ accepted
→ in_progress
→ delivered
→ completed

Exception effects may include:
→ cancelled
→ disputed
→ refunded
```

Question marks identify source-dependent stages whose exact applicability is unresolved.

**Terminal/reversal rules:** unresolved. `completed`, `cancelled`, `refunded` appear terminal-like, but dispute/reopen/refund interactions require explicit policy.

**Concurrency:** use `executeIdempotentCommand` plus `acquireAggregateLock` or `withOptimisticConcurrency`; never in-memory locks.

**History proof:** Order mutation and `OrderEvent` append must occur in the same transaction.

**Prohibited shortcut:** no client-provided status assignment and no provider webhook directly writing Order.

### 9.2 RefundStatus

```text
none → requested → partial/refunded/denied
```

This progression is suggested by the enum but exact reversal/reopen behavior and partial-refund accumulation semantics are unresolved. Payment executes the refund; this Module applies a normalized verified effect.

### 9.3 AgreementTemplate

```text
draft → active → retired → archived?
```

`archived` exists but exact entry rules are not supplied. Template activation/retirement must preserve historical versions. Unique `(key, version)` is binding.

### 9.4 Agreement

```text
draft
generated
consent_pending
pending_signatures
buyer_signed
professional_signed
fully_signed
manual_signature_requested
voided
expired
superseded
archived
```

**Transition owner:** Transaction / Order.

**Known progression:** generation, consent/manual choice, required signatures, finalization, archive. The exact legal transition graph and supersession implementation remain partly unresolved.

**Reopen/reversal:** finalized bytes are never mutated in place. Corrections require new snapshot or approved supersession path. Void/supersede/archive retain evidence.

**History proof:** AgreementEvent on significant lifecycle/evidence changes.

### 9.5 AgreementElectronicConsent

```text
pending → consented | declined | withdrawn | manual_opt_out
```

Exact transitions after withdrawal or decline are product/legal-policy dependent. Electronic signing must remain blocked until the required contextual consent state is satisfied or approved manual path is selected.

### 9.6 AgreementSignature

```text
pending / consent_required
→ signed | declined | manual_signature_requested | expired | voided | failed
```

Duplicate signature completion must be idempotent. Signer role/identity must match the Agreement requirement. Candidate/organization-member signature roles exist in the enum but their use inside Order agreements is unresolved.

### 9.7 AgreementDocumentSnapshot

```text
generated
→ pending_signatures
→ partially_signed
→ fully_signed
→ archived

Exception: superseded | voided | tamper_check_failed | corrupted
```

Snapshots are immutable versions. A status change does not permit overwriting exact bytes or hash.

### 9.8 AgreementAccessGrant

```text
active → used | expired | revoked | denied
```

TTL, one-time-use versus reusable semantics, and renewal rules require explicit policy. Grant state and Media signed URL state remain distinct.

---

## 10. Commands

| Command | Purpose | Actor/context | Preconditions | Writes | Shared operations | Effects | Idempotency/failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `createOrderFromOffering` | Create Order from an immutable Offering checkout source. | buyer/system + CustomerProfile | valid source DTO/version; authority; seller/source facts; source integrity | Order + initial OrderEvent + outbox | `resolveAuthenticatedActor`, `authorizeResourceAction`, `executeIdempotentCommand`, concurrency primitive, `appendDomainLifecycleEvent`, `publishDomainEvent` | `OrderCreated` | replay same semantic result; source unavailable/stale = no partial write. |
| `createOrderFromGigAssignment` | Create Order from accepted GigAssignment. | customer/system | accepted assignment source; one Order per assignment | Order + event/outbox | same as above | `OrderCreated` | unique assignment prevents duplicate transaction. |
| `resolveAndSnapshotOrderPricing` | Freeze base price, buyer fee/waiver, seller commission and evidence. | system/application workflow | Order at approved freeze point; Track decisions available | Order pricing/snapshot fields + event | `resolveEntitlement`, optional `consumeMeteredEntitlement`, idempotency | pricing-ready event | no silent fallback if policy unavailable unless explicitly approved. |
| `instantiateAgreementForOrder` | Create Order-specific Agreement from approved template/version. | system/buyer workflow | agreement required; active template; no conflicting current Agreement | Agreement + event | auth/authority as needed, `executeIdempotentCommand`, `appendDomainLifecycleEvent` | agreement-created notification/event | inactive template or duplicate/conflict fails deterministically. |
| `recordAgreementElectronicConsent` | Bind Agreement-specific execution consent to User and optional ConsentLog proof. | signer | correct disclosure/version, signer authorization | AgreementElectronicConsent + AgreementEvent | `queryConsentProof`, auth/authority, audit | consent event | duplicate same proof replays; mismatched proof denied. |
| `recordManualSignatureOptOut` | Record approved manual execution choice. | signer/admin per policy | manual path available; required disclosure shown | AgreementElectronicConsent + event | consent query, audit | manual-signature workflow event | unsupported template = denial. |
| `requestAgreementSignatures` | Establish required signer records/request state. | system/admin | contextual consent satisfied where required | AgreementSignature rows/status + AgreementEvent | idempotency, lifecycle transition | notification requests | duplicates do not create duplicate signer semantics. |
| `recordAgreementSignature` | Record one signer's execution evidence. | signer or normalized provider adapter | role/identity valid; consent/gate satisfied | AgreementSignature + Agreement/Document state as applicable + event | auth/authority, idempotency, audit | signature event | stale signer state = conflict; provider raw payload never enters domain API. |
| `generateAgreementDocument` | Queue/render Agreement document from frozen facts. | system/admin | approved template and source snapshot | worker state via queue; later snapshot/event | `enqueueReliableJob`, `executeRetryWithBackoff`, request context | document-generation events | retry technical failures; no duplicate version generation for same semantic job. |
| `recordAgreementDocumentSnapshot` | Bind ready private MediaAsset bytes and hash to immutable snapshot version. | worker/system | ready MediaAsset, exact hash, expected version | AgreementDocumentSnapshot + event | `calculateChecksum`, Media public interface, idempotency/concurrency | snapshot event | unique `(agreementId, version)` and exact-byte verification. |
| `finalizeAgreementDocument` | Mark required final execution/document proof complete. | system/worker | all required evidence satisfied | snapshot/Agreement status + timestamps + event | lifecycle transition, hash primitive, audit | `document_finalized` | duplicate finalization replays; missing signer/consent/hash fails. |
| `issueAgreementAccessGrant` | Authorize short-lived contract retrieval. | buyer/professional/admin/support if authorized | participant/resource authority; document available; hold/privacy restrictions | AgreementAccessGrant + event | `authorizeResourceAction`, `generateSecureToken`, `manageTemporaryAccessGrant`, `recordSensitiveAccess` | Media signed-access request | denied/expired/revoked paths stable and audited. |
| `revokeAgreementAccessGrant` | Revoke contextual grant. | participant/admin/system | authority and active grant | grant status/timestamps + event | `revokeTemporaryAccessGrant`, audit | access revoked event | idempotent. |
| `applyPaymentConfirmationToOrder` | Apply verified normalized payment success. | Payment module/system | current Order/gates; normalized result; idempotency | Order status/payment references/paidAt + OrderEvent/outbox | idempotency, concurrency, lifecycle transition | `OrderPaid` | duplicate provider result becomes one business effect; conflicting result -> reconciliation/manual review. |
| `applyPaymentFailureToOrder` | Apply normalized payment failure without provider-specific leakage. | Payment module/system | trusted normalized result | event and approved status/reference effect | idempotency | failure event/notification | provider outage does not fabricate failure/success. |
| `acceptOrder` | Apply seller acceptance if required by approved transition matrix. | ProfessionalProfile actor | authorization/readiness/holds/current state | Order status/acceptedAt + event | auth, authority, readiness, hold, concurrency | event/notification | unsupported source/delivery path denied. |
| `startOrderFulfillment` | Move eligible Order into active work. | seller/system | approved state and gates | Order + event | authority, hold, lifecycle transition | event | stale transition conflict. |
| `recordOrderDelivery` | Record transaction-level delivery milestone. | seller/system | approved fulfillment evidence | Order delivery fields + OrderFile refs + event | authority, `attachValidatedMedia`, lifecycle transition | delivery event | does not create Media truth. |
| `completeOrder` | Establish completed transaction truth. | approved actor/system | completion semantics satisfied | Order/completedAt + event/outbox | idempotency, concurrency, hold, lifecycle transition | completion event to payout/review/rewards/delivery consumers | duplicate completion replays. |
| `cancelOrder` | Cancel eligible Order. | buyer/seller/admin/system per policy | transition/financial rules satisfied | Order/cancelledAt + event | authority, lifecycle transition | refund/payment handoff if required | never assumes refund occurred. |
| `applyRefundOutcomeToOrder` | Apply normalized partial/full/denied refund result. | Payment or settlement workflow | trusted result + matching Order | refundStatus and permitted Order status/event | idempotency, concurrency | refund-effect event | financial execution remains Payment-owned. |
| `enterOrderDisputeState` | Apply transaction effect of Review/Dispute-owned open dispute. | Review / Dispute/system | trusted dispute reference | Order status/event | idempotency/concurrency/hold evaluation | dispute transaction event | does not create Dispute or hold. |
| `resolveOrderDisputeState` | Apply Order effect after adjudication/settlement result. | Review/Dispute or Payment workflow | approved normalized outcome | Order/refund state/event | idempotency/concurrency | settlement event | exact reopen/close mapping unresolved. |
| `attachOrderFile` | Create OrderFile context for a ready MediaAsset. | authorized participant/system | Media readiness + upload context + Order authority | OrderFile | `attachValidatedMedia`, authority | optional event | no direct object-storage mutation. |
| `executeOrderPrivacyTarget` | Apply Privacy-owned disposition to local records. | Privacy worker/system | validated privacy target + retention decision | anonymize/detach/revoke/retain local truth | privacy target contract, audit, Media revoke/delete handoffs | privacy result | destructive retention-sensitive behavior blocked until policy approved. |

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result kind | Result | Consumer must not infer |
| --- | --- | --- | --- | --- | --- |
| `getOrder` | UI, Payment, Review/Dispute, admin | Order ID + actor | source truth/contextual view | authorized Order DTO + source/participant/snapshot summary | provider payment truth, current Track policy. |
| `listOrdersForActor` | customer/professional/admin UI | actor/profile + filters | source-truth read model | paginated authorized summaries | authority from IDs alone. |
| `getOrderTimeline` | participants/admin/support | Order ID + actor | evidence | ordered OrderEvent DTOs | generic AuditEvent or provider history. |
| `getOrderPaymentRequirements` | checkout/Payment | Order ID | contextual facts/decision | frozen amount/currency, agreement gate, hold/readiness reason codes, source version | Stripe fields/status. |
| `evaluateOrderPrePaymentGates` | checkout/Payment | Order + requested payment action | decision | allowed/denied/warning/review with stable local reasons and evidence refs | compliance owner raw tables. |
| `authorizeOrderEntitlement` | Booking, Media, Digital Goods, Video | Order ID + actor + action/item | decision | Order state/participant facts/refund/dispute effect + allow/deny reasons | downstream access-grant truth. |
| `getAgreementPackage` | signer/participants/admin | Agreement/Order + actor | source truth/evidence | template/version, consent/signature progress, snapshot metadata, access options | Media signed URL entitlement until grant/Media checks pass. |
| `queryOrderParticipantFacts` | Role / Authority, Messaging, Notification | Order ID | owner facts | buyer/seller IDs/profiles and safe relationships | permission itself. |
| `getOrderSettlementFacts` | Review/Dispute, Payment, Payout | Order ID | contextual facts | Order/refund/dispute attachment facts and frozen pricing evidence | Dispute adjudication or payout availability. |
| `enumerateOrderPrivacyData` | Privacy / Data Erasure | subject + scope | evidence inventory | local records/targets and sensitivity/retention hints | legal disposition. |

Decision result shape should use the canonical shared contract: `allowed`, `denied`, `warning`, `review_required`, `step_up_required`, or `unavailable`, with owner-specific reason codes, safe explanation, evidence references, source/policy version, evaluatedAt, retryability, and remediation.

---

## 12. Public Module Interface

### Public commands

- `createOrderFromOffering`
- `createOrderFromGigAssignment`
- `resolveAndSnapshotOrderPricing`
- `instantiateAgreementForOrder`
- `recordAgreementElectronicConsent`
- `recordManualSignatureOptOut`
- `requestAgreementSignatures`
- `recordAgreementSignature`
- `generateAgreementDocument`
- `recordAgreementDocumentSnapshot`
- `finalizeAgreementDocument`
- `issueAgreementAccessGrant`
- `revokeAgreementAccessGrant`
- `applyPaymentConfirmationToOrder`
- `applyPaymentFailureToOrder`
- `acceptOrder`
- `startOrderFulfillment`
- `recordOrderDelivery`
- `completeOrder`
- `cancelOrder`
- `applyRefundOutcomeToOrder`
- `enterOrderDisputeState`
- `resolveOrderDisputeState`
- `attachOrderFile`

### Public queries/decisions

- `getOrder`
- `listOrdersForActor`
- `getOrderTimeline`
- `getOrderPaymentRequirements`
- `evaluateOrderPrePaymentGates`
- `authorizeOrderEntitlement`
- `getAgreementPackage`
- `queryOrderParticipantFacts`
- `getOrderSettlementFacts`

### Emitted domain events

Exact names/versioning require an event registry, but event families include:

- Order created/pricing frozen/payment confirmed/payment failed;
- Order accepted/started/delivered/completed/cancelled;
- refund/dispute transaction effect changed;
- agreement instantiated/consent requested or completed/manual path selected;
- signature requested/completed/declined;
- agreement document finalized/archived/voided/superseded;
- hash verified/tamper detected;
- agreement access issued/used/denied/revoked/expired.

### Privacy executor

`executeOrderPrivacyTarget(request)` implements the canonical privacy target result contract and may enumerate, anonymize, detach, revoke, retain, or report failure for Transaction / Order-owned records. It never changes PrivacyRequest/DataErasure state directly.

### Provider-facing interfaces

This Module may own a provider-neutral **Agreement document renderer port** and, only if adopted, a provider-neutral **e-sign adapter port**. It does not own Stripe/payment provider ports.

---

## 13. Inbound Dependencies

| Owning Module/capability | Public operation/interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | `resolveAuthenticatedActor` | trusted actor context | actor ID/type/session assurance | yes | current-user/session helper. |
| Role / Authority | `authorizeResourceAction` | protected commands/reads | action + resource + owner facts | yes | RBAC engine. |
| Customer / Buyer Profile | `resolveCustomerActor` | buyer commercial identity | CustomerProfile ID/status/owner User | yes | User-only buyer inference. |
| Professional Eligibility | `evaluateProfessionalReadiness` | selected seller actions | ProfessionalProfile + action + decision reasons | yes | verification/KYC/hold reconstruction. |
| Marketplace Supply | immutable Offering checkout source | source identity/pricing/delivery facts | Offering/PricingTier/seller/source version/required flags | yes | Offering repository reads/mutations. |
| Gig / Demand | `getGigAssignmentCheckoutSource` | accepted-demand source | assignment ID, buyer, seller, agreed amount/currency, version/status | yes | Gig tables. |
| Track Subscription & Entitlement | `resolveEntitlement`, `consumeMeteredEntitlement` | buyer fee waiver/seller commission and usage proof | typed key/value/effective evidence/grant refs | yes at freeze point | premium/commission helpers/counters. |
| Consent & Disclosure | `queryConsentProof` and active-version interfaces | generic disclosure evidence | type/version/proof ID/acceptedAt/validity | yes for electronic path | consent table/version catalog. |
| Admin Review / Compliance Hold | `evaluateComplianceHold` | reusable stop signs | target/action/hold IDs/safe reasons/expiry | yes | local blocked flag. |
| Payment / Payout / Tax | payment/refund command + normalized result contract | execute financial rail and return verified result | Order ref, frozen amount/tax context; normalized status/result | yes | Stripe client/webhook/dedupe/tax/ledger. |
| Media / File Access | ready asset facts, `issueSignedMediaUrl`, upload/access contracts | OrderFile and agreement document mechanics | MediaAsset ID/readiness/sensitivity; signed-access result | yes | R2/S3 client, scanner, MediaAccessGrant. |
| Booking & Calendar | public hold/booking facts | source-dependent live-service gates/completion facts | booking/hold IDs/status/version | yes for affected actions | Booking repository/calendar provider. |
| Review / Dispute | dispute adjudication/settlement command facts | apply Order dispute/refund effects | dispute ID/outcome/version | yes for affected transition | Dispute lifecycle. |
| Privacy / Data Erasure | privacy-target request/retention exemption refs | legal data-rights execution | disposition, target, exemption/evidence | yes for destructive actions | privacy workflow. |
| Audit / Event Ledger | audit/access commands | generic evidence | action/target/outcome/safe metadata | no business truth | local audit table. |
| Notification | `requestNotification` | user alerts | recipients/template/sensitivity/variables | no source truth | email/SMS/push client. |
| Observability / Ops | request context/log/failure/metric APIs | safe operation diagnostics | IDs, operation, category, retryability | no source truth | custom telemetry stack. |

---

## 14. Outbound Consumers and Effects

| Consumer | What it may consume | Typical trigger/effect | What Transaction / Order must not do |
| --- | --- | --- | --- |
| Payment / Payout / Tax | Order amount, pricing snapshot, completion/refund facts | payment, ledger, payout/tax coordination | mutate Payment/Payout/Tax records directly. |
| Booking & Calendar | `authorizeOrderEntitlement`, Order state | create/confirm/continue paid booking | create Booking or calendar state directly. |
| Media / File Access | contextual Order/Agreement access decision | signed file access | issue storage URL directly. |
| Digital Goods / Video | Order entitlement decision | create download/playback grants | create their grants/provider resources. |
| Review / Dispute | completed/order participant/settlement facts | review eligibility/dispute workflows | create Review/Dispute rows. |
| Messaging | participant/context facts and lifecycle events | Order thread/notifications | mutate Thread/Message internally. |
| Notification | safe event intent | deliver alerts | call providers. |
| Gamification/Sweepstakes | eligible completion event | points/entries if policy allows | create point/prize records. |
| Privacy | inventory/executor result | privacy orchestration | own PrivacyRequest status. |
| Audit/Observability | audit/access/telemetry | evidence/ops | substitute them for OrderEvent/AgreementEvent. |

This Module has no direct public-search projection requirement. If future private transaction projections are introduced, they must not make Search the source of Order truth.

---

## 15. Canonical Shared Operations Used

The supplied canonical registry does not provide binding permanent `SH-###` identifiers. This document therefore uses canonical operation names only and does not invent IDs.

| Canonical operation | Owner/class | Why used / invocation point | Local policy retained here | Expected contract/result | Prohibited duplicate names |
| --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Identity & Access; platform capability | every protected command/read | Order/Agreement action context | typed trusted actor | `currentUser`, `requireUser`, `orderAuth`. |
| `authorizeResourceAction` | Role / Authority; cross-cutting capability | before protected resource action | participant facts and action vocabulary | allow/deny decision with safe reasons | `orderPermissions`, `agreementRbac`. |
| `resolveCustomerActor` | Customer / Buyer Profile public interface | buyer-domain create/read commands | whether command requires active CustomerProfile | CustomerProfile owner facts | `customerFromUser`. |
| `resolveEntitlement` | Track commercial-policy capability | pricing freeze | how waiver/commission changes Order snapshot | typed value + grant/evidence + reason | `isPremium`, `feeWaiverService`, `commissionForPlan`. |
| `consumeMeteredEntitlement` | Track | when approved transaction event consumes a perk | which event counts | idempotent usage receipt | local usage counter. |
| `queryConsentProof` | Consent & Disclosure | agreement execution gate | whether exact proof satisfies Agreement requirement | proof ID/type/version/acceptedAt/validity | `agreementConsentLookup` over local table. |
| `evaluateProfessionalReadiness` | Professional Eligibility public interface | source-dependent seller actions | which Order action requires readiness | DecisionResult | `canSellerAccept`. |
| `evaluateComplianceHold` | Hold owner | payment/fulfillment/access transitions | which hold blocks which action | safe hold decision/evidence | `orderBlocked`. |
| `appendAuditEvent` | Audit / Event Ledger | significant admin/template/agreement actions | when generic audit is required | append acknowledgement | `contractAuditLog`. |
| `recordSensitiveAccess` | Audit / Event Ledger | contract view/download/sign/tamper evidence | target sensitivity and context | access-audit acknowledgement | `agreementViewLog`. |
| `appendDomainLifecycleEvent` | shared persistence mechanism; separate truth | same transaction as Order/Agreement mutation | event type/name/meaning | appended domain event | universal lifecycle ledger. |
| `executeIdempotentCommand` | platform primitive | commercial and retryable mutations | semantic key/conflict/replay rules | claimed/replayed command result | `orderIdempotency`. |
| `acquireAggregateLock` / `withOptimisticConcurrency` | platform primitive | creation/transition/finalization races | lock key/stale-write behavior | serialized or version-checked mutation | `orderMutex`, in-memory lock. |
| `transitionLifecycleState` | shared mechanism/separate truth | Order/Agreement transitions | legal transition graph | validated transition + event hook | generic Order policy table. |
| `publishDomainEvent` | platform outbox | after authoritative write commits | event vocabulary/payload minimization | versioned outbox event | fire-and-forget bus call. |
| `deduplicateDomainEvent` | platform inbox | inbound event handlers | handler identity/side effect | once-per-handler receipt | ad hoc processed-event table. |
| `enqueueReliableJob` | shared queue | PDF/finalization/expiry/reconciliation | payload/completion semantics | durable job ID | `agreementQueue` framework. |
| `executeRetryWithBackoff` | shared queue | worker technical retry | retryability classification | bounded retry/dead-letter | custom retry loop. |
| `runDeadlineExpiration` | shared scheduler | AgreementAccessGrant expiration; future approved expiries | what expiry means locally | owner command invocation | cron directly updating status. |
| `calculateChecksum` | shared hash primitive | exact finalized contract bytes | binding checksum to Agreement document legal proof | SHA-256 checksum metadata | `contractHash.ts`, divergent SHA helper. |
| `hashChainRecords` | proposed cross-cutting primitive | optional AgreementEvent tamper chain | Agreement canonical fields and response to failure | chain/verification result | bespoke chain helper if canonical ruling accepted. |
| `generateSecureToken` | security primitive | AgreementAccessGrant secret | TTL/target/use semantics | secret once + stored hash | `agreementToken.ts` random helper. |
| `manageTemporaryAccessGrant` | shared mechanism/separate truth | AgreementAccessGrant lifecycle | contract authorization/scope | status/expiry/token mechanics | generic grant table. |
| `revokeTemporaryAccessGrant` | shared pattern | privacy/moderation/refund/security revocation | whether Agreement grant must revoke | idempotent revocation | custom token revoker. |
| `attachValidatedMedia` | Media/context contract | OrderFile creation | Order role/context | ready MediaAsset + join result | `orderUploadService`. |
| `issueSignedMediaUrl` | Media / File Access | after AgreementAccessGrant authorization | Agreement contextual entitlement | short-lived Media URL result | `agreementSignedUrl`. |
| `createRequestContext` | Observability | every request/job/event | local safe dimensions only | request/correlation/causation IDs | local correlation helper. |
| `writeStructuredLog` | Observability | operations/workers | safe domain dimensions | structured log acknowledgement | custom logger. |
| `sanitizeTelemetryMetadata` | Observability/Audit payload policy | before logs/events/audits | domain sensitivity classification | safe allowlisted metadata | custom redaction regexes. |
| `recordIntegrationFailure` | Observability / Ops | provider/worker degradation | business truth remains local | normalized failure record | failure status as Order truth. |
| `requestNotification` | Notification | committed lifecycle facts | event meaning/recipients/safe variables | notification request acknowledgement | direct SES/SMS/push calls. |

### Another Module public interfaces, not neutral shared primitives

- immutable Offering checkout source;
- `getGigAssignmentCheckoutSource`;
- Payment initiation/refund execution and normalized outcome;
- Booking facts;
- Privacy target request;
- Media readiness/access contracts.

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `validateOrderSourceInvariant` | ensure sourceType/source IDs are semantically valid | source DTO + Order candidate | pass/fail | Order | defines Transaction source meaning. |
| `resolveOrderParticipants` | bind source-owner facts to buyer/seller IDs | source DTOs | participant snapshot | Order | commercial participant semantics belong here. |
| `composeOrderCommercialSnapshot` | create deterministic historical snapshot | source price + Track decisions | normalized snapshot | Order | historical transaction meaning is Order-owned. |
| `evaluateOrderPrePaymentGates` | compose Order-local agreement/source/hold/readiness requirements | Order + external decisions | DecisionResult | no direct write | action-owning Module composes gate. |
| `applyNormalizedPaymentResult` | map internal normalized payment outcome to Order effect | Payment result | transition/event | Order | provider mapping is external; Order effect local. |
| `applyNormalizedRefundResult` | map verified refund outcome to Order/refund effect | Payment result | state/event | Order | refund attachment semantics local. |
| `computeOrderEntitlementDecision` | decide delivery/access action from transaction truth | Order + actor/action | DecisionResult | none | downstream modules must not infer transaction truth. |
| `selectAgreementTemplateVersion` | choose approved template for Order context | Order/source policy | template ID/version | Agreement | agreement version choice is domain policy. |
| `evaluateAgreementExecutionReadiness` | determine whether consent/signature/document requirements are satisfied | Agreement aggregate | DecisionResult | none | contextual contract policy. |
| `bindDocumentHashProof` | bind shared checksum result to immutable snapshot | exact bytes checksum + Media ref | snapshot proof | AgreementDocumentSnapshot | legal/context meaning belongs here. |
| `evaluateAgreementAccess` | determine contextual contract-access eligibility | actor + Agreement/snapshot | DecisionResult | possibly grant | Media cannot infer Order participant/contract rules. |
| `applyPrivacyDispositionToOrderAggregate` | execute Privacy-owned instruction locally | target/disposition/exemption | privacy result | local records | data owner executes its own record changes. |

---

## 17. Shared Mechanism / Separate Truth Rules

| Mechanism | Shared | Separate Transaction / Order truth |
| --- | --- | --- |
| append-only ledgers | insert-only persistence, transaction hook | `OrderEvent`, `AgreementEvent` schemas and semantics. |
| access grants | token/expiry/use/revoke mechanics | `AgreementAccessGrant`; never merged with Media/Digital/Video grants. |
| provider-event dedupe | claim/unique/event hash primitive | Payment retains `ProcessedStripeEvent`; any future e-sign event ledger remains Agreement/provider-specific. |
| readiness responses | DecisionResult envelope | Order action composition stays local; Professional readiness truth external. |
| snapshots | version/provenance conventions | Order pricing snapshot and AgreementDocumentSnapshot meaning. |
| hashing | SHA-256/checksum and optional chain primitives | which exact bytes/fields are canonical and what mismatch means. |
| lifecycle plumbing | transition helper | Order and Agreement legal graphs. |
| workflow runner | durable steps/retries/correlation | Agreement execution or settlement orchestration state if introduced. |
| queue | leases/retries/dead-letter/telemetry | document finalization/expiration/reconciliation business meaning. |

---

## 18. Authentication and Authorization

- Every protected command begins with `resolveAuthenticatedActor` unless invoked by an authenticated internal system/event context.
- Role / Authority owns interpretation. Transaction / Order supplies minimum relationship facts: buyer User/CustomerProfile, seller ProfessionalProfile, signer role, Agreement target, and action name.
- Resource actions include create/read/cancel/accept/deliver/complete/order-admin-correct, agreement-template-admin, sign, view/download agreement, issue/revoke access grant, and settlement-effect application.
- CustomerProfile is the buyer commercial actor for new workflows; User remains authentication/audit identity.
- Seller authority derives from ProfessionalProfile relationship, not arbitrary User equality.
- Admin/support access is not blanket access to contracts. Sensitive agreement access must pass explicit authority/context and `recordSensitiveAccess`.
- Exact step-up action matrix is unresolved. Do not add local MFA flags. When root policy requires step-up, call Identity & Access `requireStepUpForSensitiveAction`.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying owner | Query consumed | Transaction / Order action | Local composition |
| --- | --- | --- | --- | --- |
| buyer actor | Customer / Buyer Profile | `resolveCustomerActor` | create/read/cancel Order | require correct CustomerProfile relationship. |
| seller readiness | Professional Eligibility | `evaluateProfessionalReadiness` | selected create/accept/fulfillment actions | map external decision to local action allow/deny. |
| buyer fee waiver | Track | `resolveEntitlement` | pricing freeze | freeze effective fee result and evidence. |
| seller commission | Track | `resolveEntitlement` | pricing freeze | freeze effective BPS/amount and evidence. |
| generic e-sign disclosure | Consent & Disclosure | `queryConsentProof` | Agreement electronic execution | contextual Agreement consent remains local. |
| reusable hold | Admin Review / Compliance Hold | `evaluateComplianceHold` | payment, fulfillment, agreement access, settlement actions | define action-specific block behavior. |
| payment verified | Payment / Payout / Tax | normalized result | transition to paid/refund effect | apply once through local state machine. |
| media ready/private | Media | Media readiness/access interface | OrderFile/document snapshot/access | local context does not override Media safety. |
| booking/delivery facts | Booking/delivery owner | public facts | source-specific fulfillment transition | Order consumes only approved facts. |
| dispute outcome | Review / Dispute | owner command/event | disputed/refund/settlement effect | Order state stays local. |

No single successful gate substitutes for another.

---

## 20. Provider Integrations

### Payment/refund providers

**Not owned here.** Transaction / Order must not contain Stripe SDK clients, webhook signature verification, provider-event dedupe, tax calculation, provider refund execution, or provider-native status mapping. Payment / Payout / Tax returns normalized provider-neutral results.

### Agreement document renderer

Transaction / Order may own a provider-neutral port because rendered agreement content/version/finalization is domain-specific.

```ts
interface AgreementDocumentRenderer {
  render(input: FrozenAgreementRenderInput): Promise<RenderedAgreementBytes>
}
```

Adapter choices may include Puppeteer, PDFKit, external provider, or manual upload only when confirmed. The adapter does not decide template/legal requirements and does not own Media storage.

### External e-sign provider

Optional and unresolved. If adopted:

- create a provider-neutral e-sign port;
- use shared `verifyProviderWebhookSignature` shell;
- maintain provider-specific dedupe truth separate from Stripe/calendar/video ledgers;
- translate provider status to canonical Agreement commands;
- reconcile provider state through shared worker framework;
- never persist provider-native payload as Agreement truth;
- minimize provider input and telemetry;
- define privacy deletion/revocation behavior.

The current schema has `signingProvider`/`providerEnvelopeId`, but provider selection and complete provider-neutral event schema are not binding.

---

## 21. Events and Outbox

### Domain event ownership

Transaction / Order owns event names, schema versions, payload meaning, emission conditions, privacy classification, and source aggregate version for Order/Agreement facts.

### Envelope

Use canonical event envelope fields:

- event ID/type/schema version;
- source Module;
- aggregate type/ID/version where available;
- occurredAt;
- request/correlation/causation IDs;
- actor/system context;
- privacy classification;
- minimized typed payload.

### Outbox

**Proposed ruling from CL-04:** cross-Module effects should use a transactional outbox. Order/Agreement write + lifecycle event + outbox record belong to one transaction where downstream effects are required.

### Consumer idempotency

Consumers use `deduplicateDomainEvent`. Event facts never encode hidden commands such as “set payout paid”; consumers interpret the event through their own policies/public commands.

### Payload minimization

Never emit full contract text, signatures, tax/payment secrets, raw provider payloads, private file URLs, or unnecessary PII.

---

## 22. Background Jobs / Scheduled Work

### Agreement document generation/finalization worker

- **Purpose:** render exact Agreement bytes, store through Media, hash, create immutable snapshot, and advance eligible Agreement state.
- **Input:** Agreement ID/version, render job version, correlation/idempotency key.
- **Owner:** Transaction / Order.
- **Idempotency key:** semantic Agreement + target document version + render input version.
- **Retryable failures:** renderer timeout, transient Media outage, queue/network errors.
- **Permanent failures:** invalid template/source snapshot, unsupported renderer configuration, corrupted deterministic input.
- **Dead-letter:** visible QueueJob/IntegrationFailure plus manual owner-safe retry command.
- **Business truth updated:** AgreementDocumentSnapshot/AgreementEvent/Agreement status only through owner commands.

### Agreement access-grant expiration

Use `runDeadlineExpiration` to find expired active AgreementAccessGrant rows and invoke the owner transition. Scheduler does not update status directly.

### Hash verification/reconciliation worker

Recompute exact archived byte checksum through Media access and compare with stored documentHash. Mismatch records tamper/corruption evidence; it never overwrites expected hash.

### Order/payment/refund reconciliation

A Transaction / Order reconciliation worker may detect missing local effects using **owner public interfaces or normalized reconciliation facts**, then invoke idempotent Order commands. It must not query Stripe directly.

### Privacy/backfill workers

Privacy orchestration remains external. Local backfills/reconciliation use canonical queue/retry/request-context/telemetry infrastructure.

---

## 23. Concurrency and Idempotency

### Races to prevent

- duplicate Order creation from one GigAssignment;
- two creation retries with different payload fingerprints;
- pricing snapshot applied twice or after freeze;
- payment success/failure races;
- seller acceptance/cancellation races;
- completion/dispute/refund races;
- duplicate agreement instantiation;
- duplicate signer completion;
- two final document versions claiming same `(agreementId, version)`;
- grant use/revoke/expire races.

### Resource/lock keys

- `order:{orderId}` for Order transitions;
- `order-source:gig-assignment:{gigAssignmentId}` for source conversion;
- `agreement:{agreementId}` for execution/finalization;
- `agreement-document:{agreementId}:{version}` for snapshot finalization;
- `agreement-access-grant:{grantId}` for use/revoke/expire.

Exact lock implementation uses platform/database primitives.

### Database constraints already present

- `Order.gigAssignmentId @unique`;
- `Agreement.orderId @unique`;
- `AgreementTemplate @@unique([key, version])`;
- `AgreementDocumentSnapshot @@unique([agreementId, version])`.

### Missing/required structural enforcement

- Order source XOR/type constraint;
- CustomerProfile nullability/backfill ruling;
- aggregate version/CAS field if optimistic concurrency is selected;
- any finalized pricing-freeze guard not otherwise transactionally enforced.

### Transaction boundary

For authoritative mutations, update aggregate + append domain lifecycle event + enqueue outbox fact atomically. External provider/network calls should not be held open inside long database transactions.

### Replay result

Same idempotency key + same semantic fingerprint returns the original semantic result. Same key + conflicting fingerprint returns deterministic idempotency conflict. Provider/event replays must not append duplicate business events.

---

## 24. Media / Storage

### Business meaning owned here

- `OrderFile` role/context;
- Agreement template Media reference as domain configuration;
- AgreementDocumentSnapshot version/hash/context;
- optional signature image Media reference;
- AgreementAccessGrant contextual entitlement.

### File mechanics owned by Media / File Access

- upload session/policy;
- MIME/binary validation;
- malware scan/quarantine;
- processing/metadata scrubbing;
- object storage key/bucket;
- MediaAsset status/checksum;
- MediaAccessGrant;
- signed URL issuance;
- provider object deletion.

### Rules

- Order/Agreement attachments must reference ready MediaAsset under appropriate context.
- contract files remain private;
- no permanent public agreement URL;
- signed URL is transport, not entitlement;
- viewing/downloading finalized agreements uses `recordSensitiveAccess`;
- deleting OrderFile context does not delete MediaAsset automatically;
- retention may require preserving underlying agreement MediaAsset.

---

## 25. Search / Projection

Transaction / Order owns no Typesense/public search projection.

- Search must not index private Order/Agreement details as a default public surface.
- Any future private operational projection remains derived and rebuildable.
- Transaction / Order events may be consumed by reputation, analytics, notification, payout, or delivery systems, but no `SearchUpsertEvent` should be created merely because an Order changed unless an approved public projection explicitly depends on it.
- Search must never reconstruct paid status or entitlement from provider state.

---

## 26. Notification

Transaction / Order owns **why** a notification should be requested; Notification owns **how** it is persisted/routed/delivered.

Typical business triggers:

- Order created or requires next action;
- agreement consent/signature requested;
- agreement manual path selected;
- document finalized/available;
- payment verified/failed in a user-actionable way;
- seller acceptance required;
- Order accepted/started/delivered/completed/cancelled;
- refund/dispute transaction effect changed;
- sensitive access/tamper warning where approved.

Payloads contain IDs, safe display facts, action route, template key, sensitivity, and minimal variables. Never send full agreement text, private URLs, raw payment data, or signatures.

---

## 27. Audit and Sensitive Access

Keep three evidence layers separate:

1. **OrderEvent** — Order-domain lifecycle/history truth.
2. **AgreementEvent** — Agreement-domain lifecycle/evidence truth.
3. **AuditEvent / AccessAuditLog** — generic significant-action and sensitive-access evidence owned by Audit / Event Ledger.

Generic audit is appropriate for template activation/retirement, administrative correction, agreement access, manual opt-out, signing, hash/tamper actions, and privileged settlement actions. AccessAuditLog is appropriate for agreement view/download/sign/hash verification and any other policy-designated sensitive read/use.

Audit writes must use minimized metadata and never duplicate full contracts or credentials.

---

## 28. Privacy and Retention

### Subject-data inventory

Transaction / Order may contain:

- buyer User/CustomerProfile references;
- seller ProfessionalProfile reference;
- brief/delivery text;
- OrderEvent actor/reason/metadata;
- OrderFile context;
- Agreement template/version references;
- signer display/email/typed name and request evidence;
- electronic-consent evidence;
- document snapshot/hash metadata;
- AgreementAccessGrant evidence;
- provider correlation identifiers.

### Privacy target executor

Must support enumeration and owner-local execution for:

- `Order` and participant metadata;
- `OrderEvent` where legally permitted;
- `OrderFile` contextual detach/retain;
- `Agreement`;
- `AgreementElectronicConsent`;
- `AgreementSignature` metadata;
- `AgreementDocumentSnapshot`;
- `AgreementAccessGrant`;
- `AgreementEvent`.

### Dispositions

Depending on Privacy-owned instruction and approved retention rule: anonymize, detach, revoke, retain, export contribution, skip, retryable failure, or terminal failure.

### Retention

Signed agreements and transaction records may require `contract_record`, `signature_record`, `payment_record`, `tax_record`, `dispute_record`, fraud-prevention, security-audit, or legal-obligation exemptions. Exact durations are unresolved. This Module must not decide them independently.

`Agreement.retentionLocked`/`retainUntil` applies an approved retention decision; it is not itself the legal policy engine.

---

## 29. Observability

Use canonical request context, structured logging, metrics, exception capture, queue telemetry, and IntegrationFailure.

### Safe dimensions

- operation name;
- Module/aggregate type;
- status/reason code;
- source type;
- attempt/retry category;
- worker/job type;
- provider adapter name/version where applicable;
- request/correlation IDs;
- duration and result category.

### Prohibited telemetry

- full contract text;
- signature images/typed signature content beyond safe necessity;
- private media URLs/tokens;
- payment secrets/raw provider payload;
- tax details;
- raw IP/user-agent unless specifically stored as domain/audit evidence rather than logs;
- unnecessary personal data.

Operational failures never become Order/Agreement business state unless the domain command explicitly records a business-relevant failure.

---

## 30. Security Boundaries

- validate all mutation/query inputs server-side;
- never trust client-provided ownership, seller/buyer identity, price snapshot, payment status, or agreement completion;
- require auth/authority/context gates server-side;
- use CustomerProfile and ProfessionalProfile owner facts;
- use canonical idempotency and DB concurrency controls;
- use canonical `calculateChecksum` SHA-256 primitive for exact document bytes;
- store access/signature/session secrets only as approved hashes/protected forms;
- use `generateSecureToken` for grant secrets;
- keep contract files private;
- issue signed URLs only through Media after contextual grant decision;
- raw payment webhooks never enter Transaction / Order domain services;
- future e-sign webhooks must be verified/deduped/translated in an adapter before domain commands;
- apply platform rate limiting to sensitive create/sign/access/financial actions;
- minimize event/audit/provider payloads;
- use managed encryption if sensitive values must be recoverable; do not invent Module-local crypto.

---

## 31. Error / Decision Result Pattern

Public interfaces return stable categories, not provider/framework exceptions.

### Decision categories

- `allowed`
- `denied`
- `warning`
- `review_required`
- `step_up_required`
- `unavailable`

### Command/error categories

- `validation_error`
- `authentication_required`
- `authorization_denied`
- `resource_not_found`
- `source_not_eligible`
- `policy_denied`
- `agreement_required`
- `agreement_not_ready`
- `hold_blocked`
- `stale_version`
- `transition_conflict`
- `idempotency_conflict`
- `dependency_unavailable`
- `provider_result_conflict`
- `retryable_failure`
- `manual_review_required`
- `retention_blocked`
- `unsupported_until_ruling`

Each result should include stable owner-local reason code, safe human explanation, request/correlation ID, retryability, and next action where applicable. Raw Stripe/e-sign/R2 errors must not leak directly to consumers.

---

## 32. Testing Architecture

### Domain unit tests

- source invariant;
- pricing snapshot deterministic calculations and freeze behavior;
- Order transition policy once approved;
- Agreement execution policy;
- consent/signature completion rules;
- document version/finalization rules;
- Order entitlement decisions;
- privacy disposition behavior.

### State-transition tests

Every allowed and forbidden Order/Agreement/consent/signature/document/grant transition after the matrices are approved.

### Public contract tests

- Offering checkout source → Order;
- GigAssignment source → Order;
- Track decision → pricing snapshot;
- normalized Payment result → Order effect;
- Order entitlement → CL-05 consumers;
- Review/Dispute settlement → Order effect;
- Media ready/signed-access contracts;
- Privacy target request/result.

### Database/integration tests

- source XOR constraint;
- unique GigAssignment conversion;
- template `(key, version)` uniqueness;
- document `(agreement, version)` uniqueness;
- aggregate/event/outbox atomicity;
- indexes/query plans for hot reads.

### Authorization tests

- wrong CustomerProfile;
- wrong ProfessionalProfile;
- unauthorized participant;
- support/admin without sensitive access;
- signer role mismatch;
- hold denial.

### Compliance tests

- ConsentLog vs AgreementElectronicConsent separation;
- manual opt-out behavior;
- immutable finalized document;
- exact-byte hash verification;
- private contract access;
- retention exemption blocks destructive action.

### Idempotency/concurrency tests

- duplicate Order creation;
- competing payment/status transitions;
- duplicate pricing freeze;
- duplicate signature;
- duplicate finalization;
- concurrent grant use/revoke/expire;
- duplicate normalized provider event effect.

### Provider adapter tests

Payment provider tests belong to Payment. This Module tests normalized fixtures only. If e-sign adapter is adopted, test signature verification, provider dedupe, status translation, unknown statuses, retry/reconciliation, and payload minimization outside core domain APIs.

### Privacy tests

Inventory completeness, anonymize/detach/revoke/retain behavior, idempotent replay, retention block, and export contribution.

### E2E participation

- Offering → Order → pricing → agreement → payment → fulfillment;
- GigAssignment → Order;
- agreement-required checkout;
- private agreement retrieval;
- completed Order → Review eligibility consumer;
- dispute/refund settlement effect;
- dependency outage/retry recovery.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `Order` is Workin Ants transaction truth; Stripe/provider objects are not.
2. Only Transaction / Order-owned application/domain operations may mutate Order, OrderEvent, Agreement, AgreementEvent, Agreement consent/signature/document/access records.
3. An Order must correspond to exactly one valid commercial source consistent with `OrderSourceType`.
4. `GigAssignment` remains Gig / Demand truth and must never be rewritten as an Order record.
5. Offering remains Marketplace Supply truth and is consumed through a stable checkout-source contract.
6. CustomerProfile is buyer-domain truth for new commerce; User is authentication/audit identity.
7. ProfessionalProfile is seller identity; User is not a seller substitute.
8. Track Subscription & Entitlement owns current plan/grant/usage truth.
9. Buyer fee waiver and seller commission effects are frozen at the approved Order pricing point and are never recomputed from future plan state.
10. Transaction / Order must not create local premium, waiver, commission-policy, or usage-counter truth.
11. Payment / Payout / Tax verifies and deduplicates raw provider events before Transaction / Order receives a normalized result.
12. Transaction / Order must never trust a browser redirect or client status as payment/refund proof.
13. `ProcessedStripeEvent` and financial ledgers are not Transaction / Order-owned.
14. Order payment/completion does not equal payout transfer or payout readiness.
15. ConsentLog is generic proof and does not replace AgreementElectronicConsent.
16. AgreementSignature is execution proof; signature images or URLs are not proof by themselves.
17. Finalized agreement bytes and document snapshots are immutable.
18. Agreement document hash must correspond to exact archived bytes.
19. MediaAsset remains file truth; OrderFile and AgreementDocumentSnapshot own only contextual meaning/evidence.
20. AgreementAccessGrant remains distinct from MediaAccessGrant and signed URLs.
21. ComplianceHold is the reusable stop sign; no local competing blocked flag may be introduced.
22. Review/Dispute owns adjudication truth; Transaction / Order applies only transaction effects through public contracts.
23. Refund decision/execution/Order effect are separate truths owned by the appropriate Modules.
24. Booking owns scheduling truth even when Order payment/agreement gates control whether booking may proceed.
25. AuditEvent/AccessAuditLog supplement, not replace, OrderEvent/AgreementEvent.
26. Observability records supplement, not replace, business state.
27. Privacy / Data Erasure owns privacy-request and retention-exemption workflows.
28. Cross-Module facts are consumed through owner public interfaces by default.
29. Idempotency is required for retryable commercial mutations.
30. Distributed concurrency uses database/platform primitives, never in-memory locks.
31. Domain events are published after authoritative writes commit and use minimized payloads.
32. Full contracts, secrets, private URLs, signatures, and raw provider payloads must not enter logs/events/analytics.
33. Provider-native payload types must not become Module public DTOs.
34. No unresolved migration, transition, supersession, retention, or step-up rule may be silently converted into implementation policy.

---

## 34. Prohibited Duplicate Implementations

Do not generate inside `transaction_order`:

- `currentUser.ts`, `requireUser.ts`, `getSessionActor.ts`;
- `orderPermissions.ts`, `agreementRbac.ts`, generic role matrices;
- `customerFromUser.ts`;
- `isPremium.ts`, `hasFeeWaiver.ts`, `commissionRateForPlan.ts`, local entitlement/usage tables;
- `canSellerAcceptOrder.ts` that reconstructs Professional Eligibility from raw checks;
- `orderBlocked.ts`, `payoutBlocked.ts`, local hold tables/booleans;
- Stripe webhook verification or raw webhook handlers;
- `ProcessedStripeEvent` clone;
- direct Stripe refund/payment client;
- direct R2/S3 object client or signed URL generator;
- file MIME/malware/metadata scanner;
- generic MediaAccessGrant clone;
- generic consent history/version table;
- custom AuditEvent/AccessAuditLog clone;
- universal lifecycle event table replacing OrderEvent/AgreementEvent;
- per-feature queue/retry framework;
- in-memory mutex or custom distributed lock table where shared primitive exists;
- divergent SHA-256 helper;
- generic access-grant source-of-truth table;
- local notification provider client/template renderer;
- local privacy-request/erasure state machine;
- direct Typesense client;
- generic “commerce service” that owns GigAssignment + Order + Dispute lifecycles together.

---

## 35. Unresolved Decisions

The following are not implementation details; affected production work must stop until explicitly resolved:

1. Does `customerProfileId` become non-null for new Orders, and what are the migration/backfill semantics for legacy `buyerUserId`?
2. What is the exact valid Order transition matrix by source and delivery kind?
3. Exactly when is commercial policy frozen: Order create, payment initiation, agreement lock, or another approved point?
4. What database rule/check constraint enforces exactly one source and consistency with `sourceType`?
5. What are the authoritative meanings of `priceCents`, `applicationFeeCents`, `buyerPlatformFeeCents`, seller commission, tax, processor fee, and seller proceeds?
6. Which Stripe/provider correlation fields remain on Order long-term, and what is the meaning of `stripeTransferId` given Payment-owned `PayoutTransfer[]`?
7. Are Track subscription/grant snapshot references foreign keys or intentionally non-FK historical identifiers?
8. What event/name registry replaces or constrains free-string `OrderEvent.name`?
9. What Order aggregate version/CAS strategy is canonical if optimistic concurrency is used?
10. What is the exact seller-acceptance requirement/timeout/rejection behavior for `awaiting_seller`?
11. Which source types require an Agreement and who supplies that requirement fact?
12. Does one Agreement row per Order remain the design, or must the schema support multiple Agreement rows for supersession? Current `orderId @unique` conflicts with a true multi-Agreement chain.
13. Are `buyerSigUrl`, `professionalSigUrl`, `pdfMediaId`, and `finalDocumentHash` compatibility fields to deprecate in favor of normalized records?
14. Are `organization_member` and `candidate` valid signer roles for Order agreements, or merely shared enum vocabulary for future contexts?
15. What is the approved manual-signature operational workflow after opt-out?
16. Is an external e-sign provider used for MVP; if so, which provider-event dedupe record/contract is owned here?
17. Is AgreementEvent hash chaining required for MVP? `hashChainRecords` is a proposed shared ruling, not confirmed ownership.
18. What are AgreementAccessGrant TTL, one-time/reuse, renewal, and download rules?
19. What are full/partial refund allocation and reversal semantics?
20. How exactly does Order exit or remain in `disputed` after Review / Dispute adjudication and financial settlement?
21. Which `ComplianceHold` reasons block which Order/Agreement actions?
22. Which actions require step-up authentication under root security policy?
23. Which Transaction / Order records require retention exemptions, and for what duration?
24. Which actor/signer fields may be anonymized while preserving required transaction/contract proof?

---

## 36. Architecture Decision Summary

### Binding rulings

1. Transaction / Order owns Order, OrderEvent, OrderFile context, Order-attached refund state, and the complete Order-specific Agreement aggregate/evidence.
2. Order remains transaction truth; Payment / Payout / Tax owns provider financial rail, dedupe, tax, payout, and financial proof.
3. Track owns commercial policy; Order freezes historical fee-waiver/commission effects and evidence.
4. CustomerProfile is buyer actor truth for new commerce; ProfessionalProfile is seller identity.
5. GigAssignment and Offering remain external source truth and are consumed through owner public DTOs.
6. Generic consent proof and Agreement execution proof remain separate.
7. Media owns file mechanics; Transaction / Order owns Order/Agreement contextual meaning and access entitlement.
8. ComplianceHold remains external stop-sign truth.
9. Review/Dispute owns adjudication; Transaction / Order owns only transaction/refund attachment effects.
10. Canonical auth, authority, idempotency, concurrency, event/outbox, queue, hashing, access-grant, audit, observability, notification, Media, and Privacy mechanisms must be reused.
11. Finalized agreement documents are immutable and hashed from exact archived bytes.
12. Cross-Module effects use stable public contracts/events; no direct neighboring lifecycle mutation.

### Proposed rulings carried from CL-04

- require CustomerProfile on new buyer-domain writes after explicit migration approval;
- use immutable source DTOs instead of cross-Module repositories;
- use canonical DB concurrency + idempotency for commercial transitions;
- use transactional outbox for cross-Module effects.

### Unresolved rulings

See Section 35. Coding agents must not infer answers.

---

## 37. Coding-Agent Usage

Before implementing any numbered Transaction / Order feature, read in this order:

1. root `project-overview.md`;
2. root architecture;
3. root code standards;
4. Canonical Shared Operations Registry/Architecture;
5. CL-04 `architecture.md`;
6. CL-04 `build-plan.md`;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. public-interface sections/contracts for direct dependencies: Customer / Buyer Profile, Role / Authority, Marketplace Supply, Gig / Demand, Professional Eligibility, Track Subscription & Entitlement, Consent & Disclosure, Payment / Payout / Tax, Media / File Access, Admin Review / Compliance Hold, Booking & Calendar, Review / Dispute, Privacy / Data Erasure, Audit / Event Ledger, Notification, Observability / Ops;
10. current progress tracker.

Before coding, verify that every unresolved decision required by the feature has an approved ruling. If not, stop the feature at that boundary and record the blocker rather than inventing policy.
