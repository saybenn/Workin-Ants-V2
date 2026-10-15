# Transaction / Order Module Architecture

> **Module ID:** `transaction_order`  
> **Module name:** Transaction / Order Module  
> **Module type:** `domain`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** CL-04 — Customer Demand, Order & Resolution  
> **Document status:** Implementation-grade Module architecture. Confirmed rulings are binding. Proposed rulings require explicit acceptance before schema/API commitment. Unresolved decisions remain non-authoritative.  
> **Audience:** coding agents, developers, reviewers, migration authors, test authors, provider-integration authors, maintainers.  

**Shared Operation status (CL-04-R015/R016):** exact SH IDs/names resolve to the canonical registry. SH-046 publication/outbox is Confirmed. SH-003 `queryOwnerFacts` and SH-015 `returnDecisionResult` remain Proposed ruling: use owner-specific fact/decision DTOs, not binding APIs dependent on those proposals. SH-054, SH-073, and SH-111, wherever referenced, remain Proposed ruling and conditional on separate approval. All other referenced registered operations retain their registry status and owner.

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
| `Order` | Authoritative commercial transaction record sourced from one Offering, accepted GigAssignment, or approved platform-facilitated screening service (WA-R003; screening representation pending). |
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
- agreement event hash-chain fields where the proposed SH-073 `hashChainRecords` mechanism is adopted;
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
2. **Exactly one commercial source.** An Order has one valid source family: Offering, GigAssignment, or the approved platform-facilitated screening source (WA-R003). Each family requires its own source/reference constraints; reject mixed/mismatched sources. Screening schema/activation remains gated.
3. **CustomerProfile is buyer-domain truth.** `buyerUserId` may remain auth/audit traceability, but new commercial behavior must not treat User as the complete buyer domain identity.
4. **ProfessionalProfile is marketplace seller identity.** User cannot be substituted for seller context. Platform-facilitated screening uses explicit platform service context and requires no Professional seller (WA-R003).
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

**Concurrency:** use SH-044 `executeIdempotentCommand` plus SH-051 `acquireAggregateLock` or SH-052 `withOptimisticConcurrency`; never in-memory locks.

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
| `createOrderFromOffering` | Create Order from an immutable Offering checkout source. | buyer/system + CustomerProfile | valid source DTO/version; authority; seller/source facts; source integrity | Order + initial OrderEvent + outbox | SH-001 `resolveAuthenticatedActor`, SH-002 `authorizeResourceAction`, SH-044 `executeIdempotentCommand`, concurrency primitive, SH-031 `appendDomainLifecycleEvent`, SH-046 `publishDomainEvent` | `OrderCreated` | replay same semantic result; source unavailable/stale = no partial write. |
| `createOrderFromGigAssignment` | Create Order from accepted GigAssignment. | customer/system | accepted assignment source; one Order per assignment | Order + event/outbox | same as above | `OrderCreated` | unique assignment prevents duplicate transaction. |
| `resolveAndSnapshotOrderPricing` | Freeze base price, buyer fee/waiver, seller commission and evidence. | system/application workflow | Order at approved freeze point; Track decisions available | Order pricing/snapshot fields + event | SH-005 `resolveEntitlement`, optional SH-006 `consumeMeteredEntitlement`, idempotency | pricing-ready event | no silent fallback if policy unavailable unless explicitly approved. |
| `instantiateAgreementForOrder` | Create Order-specific Agreement from approved template/version. | system/buyer workflow | agreement required; active template; no conflicting current Agreement | Agreement + event | auth/authority as needed, SH-044 `executeIdempotentCommand`, SH-031 `appendDomainLifecycleEvent` | agreement-created notification/event | inactive template or duplicate/conflict fails deterministically. |
| `recordAgreementElectronicConsent` | Bind Agreement-specific execution consent to User and optional ConsentLog proof. | signer | correct disclosure/version, signer authorization | AgreementElectronicConsent + AgreementEvent | SH-008 `queryConsentProof`, auth/authority, audit | consent event | duplicate same proof replays; mismatched proof denied. |
| `recordManualSignatureOptOut` | Record approved manual execution choice. | signer/admin per policy | manual path available; required disclosure shown | AgreementElectronicConsent + event | consent query, audit | manual-signature workflow event | unsupported template = denial. |
| `requestAgreementSignatures` | Establish required signer records/request state. | system/admin | contextual consent satisfied where required | AgreementSignature rows/status + AgreementEvent | idempotency, lifecycle transition | notification requests | duplicates do not create duplicate signer semantics. |
| `recordAgreementSignature` | Record one signer's execution evidence. | signer or normalized provider adapter | role/identity valid; consent/gate satisfied | AgreementSignature + Agreement/Document state as applicable + event | auth/authority, idempotency, audit | signature event | stale signer state = conflict; provider raw payload never enters domain API. |
| `generateAgreementDocument` | Queue/render Agreement document from frozen facts. | system/admin | approved template and source snapshot | worker state via queue; later snapshot/event | SH-047 `enqueueReliableJob`, SH-048 `executeRetryWithBackoff`, request context | document-generation events | retry technical failures; no duplicate version generation for same semantic job. |
| `recordAgreementDocumentSnapshot` | Bind ready private MediaAsset bytes and hash to immutable snapshot version. | worker/system | ready MediaAsset, exact hash, expected version | AgreementDocumentSnapshot + event | SH-086 `calculateChecksum`, Media public interface, idempotency/concurrency | snapshot event | unique `(agreementId, version)` and exact-byte verification. |
| `finalizeAgreementDocument` | Mark required final execution/document proof complete. | system/worker | all required evidence satisfied | snapshot/Agreement status + timestamps + event | lifecycle transition, hash primitive, audit | `document_finalized` | duplicate finalization replays; missing signer/consent/hash fails. |
| `issueAgreementAccessGrant` | Authorize short-lived contract retrieval. | buyer/professional/admin/support if authorized | participant/resource authority; document available; hold/privacy restrictions | AgreementAccessGrant + event | SH-002 `authorizeResourceAction`, SH-074 `generateSecureToken`, SH-088 `manageTemporaryAccessGrant`, SH-030 `recordSensitiveAccess` | Media signed-access request | denied/expired/revoked paths stable and audited. |
| `revokeAgreementAccessGrant` | Revoke contextual grant. | participant/admin/system | authority and active grant | grant status/timestamps + event | SH-089 `revokeTemporaryAccessGrant`, audit | access revoked event | idempotent. |
| `applyPaymentConfirmationToOrder` | Apply verified normalized payment success. | Payment module/system | current Order/gates; normalized result; idempotency | Order status/payment references/paidAt + OrderEvent/outbox | idempotency, concurrency, lifecycle transition | `OrderPaid` | duplicate provider result becomes one business effect; conflicting result -> reconciliation/manual review. |
| `applyPaymentFailureToOrder` | Apply normalized payment failure without provider-specific leakage. | Payment module/system | trusted normalized result | event and approved status/reference effect | idempotency | failure event/notification | provider outage does not fabricate failure/success. |
| `acceptOrder` | Apply seller acceptance if required by approved transition matrix. | ProfessionalProfile actor | authorization/readiness/holds/current state | Order status/acceptedAt + event | auth, authority, readiness, hold, concurrency | event/notification | unsupported source/delivery path denied. |
| `startOrderFulfillment` | Move eligible Order into active work. | seller/system | approved state and gates | Order + event | authority, hold, lifecycle transition | event | stale transition conflict. |
| `recordOrderDelivery` | Record transaction-level delivery milestone. | seller/system | approved fulfillment evidence | Order delivery fields + OrderFile refs + event | authority, SH-090 `attachValidatedMedia`, lifecycle transition | delivery event | does not create Media truth. |
| `completeOrder` | Establish completed transaction truth. | approved actor/system | completion semantics satisfied | Order/completedAt + event/outbox | idempotency, concurrency, hold, lifecycle transition | completion event to payout/review/rewards/delivery consumers | duplicate completion replays. |
| `cancelOrder` | Cancel eligible Order. | buyer/seller/admin/system per policy | transition/financial rules satisfied | Order/cancelledAt + event | authority, lifecycle transition | refund/payment handoff if required | never assumes refund occurred. |
| `applyRefundOutcomeToOrder` | Apply normalized partial/full/denied refund result. | Payment or settlement workflow | trusted result + matching Order | refundStatus and permitted Order status/event | idempotency, concurrency | refund-effect event | financial execution remains Payment-owned. |
| `enterOrderDisputeState` | Apply transaction effect of Review/Dispute-owned open dispute. | Review / Dispute/system | trusted dispute reference | Order status/event | idempotency/concurrency/hold evaluation | dispute transaction event | does not create Dispute or hold. |
| `resolveOrderDisputeState` | Apply Order effect after adjudication/settlement result. | Review/Dispute or Payment workflow | approved normalized outcome | Order/refund state/event | idempotency/concurrency | settlement event | exact reopen/close mapping unresolved. |
| `attachOrderFile` | Create OrderFile context for a ready MediaAsset. | authorized participant/system | Media readiness + upload context + Order authority | OrderFile | SH-090 `attachValidatedMedia`, authority | optional event | no direct object-storage mutation. |
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
| SH-025 `authorizeOrderEntitlement` | Booking, Media, Digital Goods, Video | Order ID + actor + action/item | decision | Order state/participant facts/refund/dispute effect + allow/deny reasons | downstream access-grant truth. |
| `getAgreementPackage` | signer/participants/admin | Agreement/Order + actor | source truth/evidence | template/version, consent/signature progress, snapshot metadata, access options | Media signed URL entitlement until grant/Media checks pass. |
| `queryOrderParticipantFacts` | Role / Authority, Messaging, Notification | Order ID | owner facts | buyer/seller IDs/profiles and safe relationships | permission itself. |
| `getOrderSettlementFacts` | Review/Dispute, Payment, Payout | Order ID | contextual facts | Order/refund/dispute attachment facts and frozen pricing evidence | Dispute adjudication or payout availability. |
| `enumerateOrderPrivacyData` | Privacy / Data Erasure | subject + scope | evidence inventory | local records/targets and sensitivity/retention hints | legal disposition. |

The owner-specific decision result may express: `allowed`, `denied`, `warning`, `review_required`, `step_up_required`, or `unavailable`, with owner-specific reason codes, safe explanation, evidence references, source/policy version, evaluatedAt, retryability, and remediation.

---

## 12. Public Module Interface

**Approved refund coordination (CL-04-R001).** Review / Dispute adjudicates → Transaction / Order coordinates SH-108 `requestOrderRefund` → Payment / Payout / Tax executes the provider refund → Order applies the verified provider-neutral result to RefundStatus/Order → Review / Dispute consumes settlement. Review / Dispute must not call Payment's refund executor directly.

SH-108 accepts the authorized source decision, Order reference, amount/currency, reason/basis, actor authority, idempotency and correlation. It returns correlated asynchronous execution/settlement facts; an unavailable or failed Payment rail must not be recorded as refund success.

### Public commands

- SH-108 `requestOrderRefund`
- `createAgreementTemplate` — authorized administrative command
- `activateAgreementTemplate` — authorized administrative command
- `retireAgreementTemplate` — authorized administrative command
- `requestOrderPayment` — Order-owned application/module command delegating the provider rail to Payment
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

### Internal/background integrity operation

SH-112 `verifyAgreementDocumentHash` is Transaction / Order internal/background integrity work. It is not a generally consumable public API; public exposure requires a later approved consumer contract.

### Public queries/decisions

- `getOrder`
- `listOrdersForActor`
- `getOrderTimeline`
- `getOrderPaymentRequirements`
- `evaluateOrderPrePaymentGates`
- SH-025 `authorizeOrderEntitlement`
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
| Identity & Access | SH-001 `resolveAuthenticatedActor` | trusted actor context | actor ID/type/session assurance | yes | current-user/session helper. |
| Role / Authority | SH-002 `authorizeResourceAction` | protected commands/reads | action + resource + owner facts | yes | RBAC engine. |
| Customer / Buyer Profile | SH-004 `resolveCustomerActor` | buyer commercial identity | CustomerProfile ID/status/owner User | yes | User-only buyer inference. |
| Professional Eligibility | SH-016 `evaluateProfessionalReadiness` | selected seller actions | ProfessionalProfile + action + decision reasons | yes | verification/KYC/hold reconstruction. |
| Marketplace Supply | immutable Offering checkout source | source identity/pricing/delivery facts | Offering/PricingTier/seller/source version/required flags | yes | Offering repository reads/mutations. |
| Gig / Demand | `getGigAssignmentCheckoutSource` | accepted-demand source | assignment ID, buyer, seller, agreed amount/currency, version/status | yes | Gig tables. |
| Track Subscription & Entitlement | SH-005 `resolveEntitlement`, SH-006 `consumeMeteredEntitlement` | buyer fee waiver/seller commission and usage proof | typed key/value/effective evidence/grant refs | yes at freeze point | premium/commission helpers/counters. |
| Consent & Disclosure | SH-008 `queryConsentProof` and active-version interfaces | generic disclosure evidence | type/version/proof ID/acceptedAt/validity | yes for electronic path | consent table/version catalog. |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | reusable stop signs | target/action/hold IDs/safe reasons/expiry | yes | local blocked flag. |
| Payment / Payout / Tax | payment/refund command + normalized result contract | execute financial rail and return verified result | Order ref, frozen amount/tax context; normalized status/result | yes | Stripe client/webhook/dedupe/tax/ledger. |
| Media / File Access | ready asset facts, SH-127 `requestMediaAccess`, upload/access contracts | OrderFile and agreement document mechanics | MediaAsset ID/readiness/sensitivity; signed-access result | yes | R2/S3 client, scanner, MediaAccessGrant. |
| Booking & Calendar | public hold/booking facts | source-dependent live-service gates/completion facts | booking/hold IDs/status/version | yes for affected actions | Booking repository/calendar provider. |
| Review / Dispute | dispute adjudication/settlement command facts | apply Order dispute/refund effects | dispute ID/outcome/version | yes for affected transition | Dispute lifecycle. |
| Privacy / Data Erasure | privacy-target request/retention exemption refs | legal data-rights execution | disposition, target, exemption/evidence | yes for destructive actions | privacy workflow. |
| Audit / Event Ledger | audit/access commands | generic evidence | action/target/outcome/safe metadata | no business truth | local audit table. |
| Notification | SH-041 `requestNotification` | user alerts | recipients/template/sensitivity/variables | no source truth | email/SMS/push client. |
| Observability / Ops | request context/log/failure/metric APIs | safe operation diagnostics | IDs, operation, category, retryability | no source truth | custom telemetry stack. |

---

## 14. Outbound Consumers and Effects

| Consumer | What it may consume | Typical trigger/effect | What Transaction / Order must not do |
| --- | --- | --- | --- |
| Payment / Payout / Tax | Order amount, pricing snapshot, completion/refund facts | payment, ledger, payout/tax coordination | mutate Payment/Payout/Tax records directly. |
| Booking & Calendar | SH-025 `authorizeOrderEntitlement`, Order state | create/confirm/continue paid booking | create Booking or calendar state directly. |
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

Use the permanent IDs, canonical owners, and statuses in [Shared Operations](<../../../shared/shared-operations.md>). Confirmed references retain their registered boundaries; proposed references are conditional only.

| Canonical operation | Owner/class | Why used / invocation point | Local policy retained here | Expected contract/result | Prohibited duplicate names |
| --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access; platform capability | every protected command/read | Order/Agreement action context | typed trusted actor | `currentUser`, `requireUser`, `orderAuth`. |
| SH-002 `authorizeResourceAction` | Role / Authority; cross-cutting capability | before protected resource action | participant facts and action vocabulary | allow/deny decision with safe reasons | `orderPermissions`, `agreementRbac`. |
| SH-004 `resolveCustomerActor` | Customer / Buyer Profile public interface | buyer-domain create/read commands | whether command requires active CustomerProfile | CustomerProfile owner facts | `customerFromUser`. |
| SH-005 `resolveEntitlement` | Track commercial-policy capability | pricing freeze | how waiver/commission changes Order snapshot | typed value + grant/evidence + reason | `isPremium`, `feeWaiverService`, `commissionForPlan`. |
| SH-006 `consumeMeteredEntitlement` | Track | when approved transaction event consumes a perk | which event counts | idempotent usage receipt | local usage counter. |
| SH-008 `queryConsentProof` | Consent & Disclosure | agreement execution gate | whether exact proof satisfies Agreement requirement | proof ID/type/version/acceptedAt/validity | `agreementConsentLookup` over local table. |
| SH-016 `evaluateProfessionalReadiness` | Professional Eligibility public interface | source-dependent seller actions | which Order action requires readiness | DecisionResult | `canSellerAccept`. |
| SH-011 `evaluateComplianceHold` | Hold owner | payment/fulfillment/access transitions | which hold blocks which action | safe hold decision/evidence | `orderBlocked`. |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | significant admin/template/agreement actions | when generic audit is required | append acknowledgement | `contractAuditLog`. |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | contract view/download/sign/tamper evidence | target sensitivity and context | access-audit acknowledgement | `agreementViewLog`. |
| SH-031 `appendDomainLifecycleEvent` | shared persistence mechanism; separate truth | same transaction as Order/Agreement mutation | event type/name/meaning | appended domain event | universal lifecycle ledger. |
| SH-044 `executeIdempotentCommand` | platform primitive | commercial and retryable mutations | semantic key/conflict/replay rules | claimed/replayed command result | `orderIdempotency`. |
| SH-051 `acquireAggregateLock` / SH-052 `withOptimisticConcurrency` | platform primitive | creation/transition/finalization races | lock key/stale-write behavior | serialized or version-checked mutation | `orderMutex`, in-memory lock. |
| SH-053 `transitionLifecycleState` | shared mechanism/separate truth | Order/Agreement transitions | legal transition graph | validated transition + event hook | generic Order policy table. |
| SH-046 `publishDomainEvent` | platform outbox | after authoritative write commits | event vocabulary/payload minimization | versioned outbox event | fire-and-forget bus call. |
| SH-045 `deduplicateDomainEvent` | platform inbox | inbound event handlers | handler identity/side effect | once-per-handler receipt | ad hoc processed-event table. |
| SH-047 `enqueueReliableJob` | shared queue | PDF/finalization/expiry/reconciliation | payload/completion semantics | durable job ID | `agreementQueue` framework. |
| SH-048 `executeRetryWithBackoff` | shared queue | worker technical retry | retryability classification | bounded retry/dead-letter | custom retry loop. |
| SH-055 `runDeadlineExpiration` | shared scheduler | AgreementAccessGrant expiration; future approved expiries | what expiry means locally | owner command invocation | cron directly updating status. |
| SH-086 `calculateChecksum` | shared hash primitive | exact finalized contract bytes | binding checksum to Agreement document legal proof | SHA-256 checksum metadata | `contractHash.ts`, divergent SHA helper. |
| SH-073 `hashChainRecords` | proposed cross-cutting primitive | optional AgreementEvent tamper chain | Agreement canonical fields and response to failure | chain/verification result | bespoke chain helper if canonical ruling accepted. |
| SH-074 `generateSecureToken` | security primitive | AgreementAccessGrant secret | TTL/target/use semantics | secret once + stored hash | `agreementToken.ts` random helper. |
| SH-088 `manageTemporaryAccessGrant` | shared mechanism/separate truth | AgreementAccessGrant lifecycle | contract authorization/scope | status/expiry/token mechanics | generic grant table. |
| SH-089 `revokeTemporaryAccessGrant` | shared pattern | privacy/moderation/refund/security revocation | whether Agreement grant must revoke | idempotent revocation | custom token revoker. |
| SH-090 `attachValidatedMedia` | Media/context contract | OrderFile creation | Order role/context | ready MediaAsset + join result | `orderUploadService`. |
| SH-127 `requestMediaAccess` | Media / File Access | after AgreementAccessGrant authorization | Agreement contextual entitlement | short-lived Media URL result | `agreementSignedUrl`. |
| SH-032 `createRequestContext` | Observability | every request/job/event | local safe dimensions only | request/correlation/causation IDs | local correlation helper. |
| SH-033 `writeStructuredLog` | Observability | operations/workers | safe domain dimensions | structured log acknowledgement | custom logger. |
| SH-034 `sanitizeTelemetryMetadata` | Observability/Audit payload policy | before logs/events/audits | domain sensitivity classification | safe allowlisted metadata | custom redaction regexes. |
| SH-037 `recordIntegrationFailure` | Observability / Ops | provider/worker degradation | business truth remains local | normalized failure record | failure status as Order truth. |
| SH-041 `requestNotification` | Notification | committed lifecycle facts | event meaning/recipients/safe variables | notification request acknowledgement | direct SES/SMS/push calls. |

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

- Every protected command begins with SH-001 `resolveAuthenticatedActor` unless invoked by an authenticated internal system/event context.
- Role / Authority owns interpretation. Transaction / Order supplies minimum relationship facts: buyer User/CustomerProfile, seller ProfessionalProfile, signer role, Agreement target, and action name.
- Resource actions include create/read/cancel/accept/deliver/complete/order-admin-correct, agreement-template-admin, sign, view/download agreement, issue/revoke access grant, and settlement-effect application.
- CustomerProfile is the buyer commercial actor for new workflows; User remains authentication/audit identity.
- Seller authority derives from ProfessionalProfile relationship, not arbitrary User equality.
- Admin/support access is not blanket access to contracts. Sensitive agreement access must pass explicit authority/context and SH-030 `recordSensitiveAccess`.
- Refund/release actions that cause or authorize financial movement require Identity & Access SH-014 `requireStepUpForSensitiveAction`. Remaining action-specific rules stay unresolved; do not add local MFA flags.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying owner | Query consumed | Transaction / Order action | Local composition |
| --- | --- | --- | --- | --- |
| buyer actor | Customer / Buyer Profile | SH-004 `resolveCustomerActor` | create/read/cancel Order | require correct CustomerProfile relationship. |
| seller readiness | Professional Eligibility | SH-016 `evaluateProfessionalReadiness` | selected create/accept/fulfillment actions | map external decision to local action allow/deny. |
| buyer fee waiver | Track | SH-005 `resolveEntitlement` | pricing freeze | freeze effective fee result and evidence. |
| seller commission | Track | SH-005 `resolveEntitlement` | pricing freeze | freeze effective BPS/amount and evidence. |
| generic e-sign disclosure | Consent & Disclosure | SH-008 `queryConsentProof` | Agreement electronic execution | contextual Agreement consent remains local. |
| reusable hold | Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | payment, fulfillment, agreement access, settlement actions | define action-specific block behavior. |
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
- use shared SH-059 `verifyProviderWebhookSignature` shell;
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

**Confirmed SH-046:** cross-Module effects use the canonical transactional outbox. Order/Agreement write + lifecycle event + outbox record belong to one transaction where downstream effects are required.

### Consumer idempotency

Consumers use SH-045 `deduplicateDomainEvent`. Event facts never encode hidden commands such as “set payout paid”; consumers interpret the event through their own policies/public commands.

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

Use SH-055 `runDeadlineExpiration` to find expired active AgreementAccessGrant rows and invoke the owner transition. Scheduler does not update status directly.

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
- viewing/downloading finalized agreements uses SH-030 `recordSensitiveAccess`;
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
- use canonical SH-086 `calculateChecksum` SHA-256 primitive for exact document bytes;
- store access/signature/session secrets only as approved hashes/protected forms;
- use SH-074 `generateSecureToken` for grant secrets;
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

**Confirmed commercial freeze boundary (CL-04-R003):** resolve authoritative source and Track entitlement decisions, then freeze source pricing, buyer fee-waiver effect, seller commission effect, and supporting Track grant/evidence references before Agreement execution or payment initiation. An initial/draft Order may exist before freeze. Frozen effects must never be recomputed from later subscription state.

**Confirmed actor semantics (CL-04-R007):** CustomerProfile is required semantic buyer identity for new CL-04 buyer-domain records; User remains authenticated account/audit identity. After CustomerProfile migration, Gig/GigAssignment/Order buyer ownership must not be authorized from User ID alone. A Review author resolves to the Order's buyer CustomerProfile. Dispute opener proof must distinguish customer, professional, and privileged/admin initiation with an unambiguous typed domain actor; this representation requirement does not approve which actors may open a Dispute. Historical backfill, permanent legacy-User reference semantics, and the physical typed-opener schema remain unresolved.

**Binding marketplace-source invariant (CL-04-R008, scope amended by WA-R003):** for seller-backed marketplace Orders, `sourceType=offering` requires only its Offering source and `sourceType=gig_assignment` requires only its GigAssignment source. Mixed sources or mismatched discriminators are invalid. The approved platform-facilitated screening source is a separate family: it references a Trust-owned package/quote, requires no Professional seller, and must not fabricate an Offering or GigAssignment. Its discriminator, reference, participant constraints and migration are not yet represented in Prisma. Transaction / Order must enforce one valid source family in domain validation and coordinated database constraints before enabling that family. No schema/deployment change is implied.

**Binding retention boundary (CL-04-R011):** hard deletion of an Order must not cascade-delete retained transaction, Agreement, Review, Dispute, or domain-history evidence without owner-specific Privacy/retention evaluation. Privacy issues the instruction; each owner enumerates its targets, evaluates retention/exemption facts, erases/anonymizes eligible data, preserves/minimizes retained evidence, and returns proof to Privacy. Database cascades must not provide an alternate destructive path. Existing cascade behavior requires a later approved database correction; legal retention durations remain unresolved.

**Confirmed sensitive-action gate (CL-04-R021):** refund/release adjudication or actions that cause or authorize financial movement require SH-014 `requireStepUpForSensitiveAction`, owned by Identity & Access. This gate does not approve finality, grant TTL/reuse/renewal, manual-signature procedure, non-payout hold effects, signer anonymization, or retention periods. Optional external e-sign adoption must not block the provider-neutral Agreement domain.

### Approved local Shared Operation mappings

- SH-107 `createChargeableOrder` — Confirmed; Transaction / Order owns creation. `createOrderFromOffering` and `createOrderFromGigAssignment` are typed source-specific specializations of this responsibility, not separate creation engines.
- SH-109 `snapshotExternalDecision` — Confirmed; Order freezes external Track decision/evidence while Track retains current policy truth.
- SH-110 `createDomainSnapshot` — Confirmed; Order owns immutable source/commercial snapshots where the registered semantics apply.
- SH-026 `authorizeContextualResourceAccess` — Confirmed; the context owner decides Agreement/Dispute business access; Media retains signed transport mechanics.
- SH-125 `recordDomainAccessEvent` — Confirmed; Agreement/domain access proof remains separate from generic AccessAuditLog.
- SH-111 `renderDocument` — Proposed ruling, conditional future shared normalization; not a required confirmed dependency. Transaction / Order retains its owner-local/provider-neutral rendering workflow until separate Shared Operations approval.

## 35. Unresolved Decisions

The following are not implementation details; affected production work must stop until explicitly resolved:

1. CustomerProfile is required semantic buyer identity for new Orders; physical enforcement, historical backfill, and permanent legacy `buyerUserId` semantics remain unresolved.
2. What is the exact valid Order transition matrix by source and delivery kind?
3. Commercial freeze ordering is confirmed by CL-04-R003; detailed fee/tax/proceeds field meanings remain unresolved.
4. Source XOR/type consistency and domain + database enforcement are binding under CL-04-R008; the later approved constraint/migration is still required.
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
17. Is AgreementEvent hash chaining required for MVP? SH-073 `hashChainRecords` is a proposed shared ruling, not confirmed ownership.
18. What are AgreementAccessGrant TTL, one-time/reuse, renewal, and download rules?
19. What are full/partial refund allocation and reversal semantics?
20. How exactly does Order exit or remain in `disputed` after Review / Dispute adjudication and financial settlement?
21. Which `ComplianceHold` reasons block which Order/Agreement actions?
22. Refund/release actions causing or authorizing financial movement require SH-014; any remaining action-specific step-up matrix is unresolved.
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

### Confirmed reconciliation rulings

- **Confirmed CL-04-R007:** require CustomerProfile semantically on new buyer-domain writes; physical migration/backfill remains separately gated;
- **Confirmed SH-046 (not a proposal):** use transactional outbox for cross-Module effects.

### Proposed rulings carried from CL-04

- use immutable source DTOs instead of cross-Module repositories;
- use canonical DB concurrency + idempotency for commercial transitions;

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

## WA-R003 — Approved platform-facilitated screening source (2026-09-29)

SH-107 authorizes three conceptual source families: Offering, accepted GigAssignment, and platform-facilitated screening service. The first two retain their Professional seller rules. Screening has a Customer buyer and explicit platform service context, with no Professional seller. Organization verification uses the business/EIN path; it is not a personal screening subject.

Trust owns VerificationPackage/check-package meaning, itemized quote, requirements, consent sufficiency and screening results. Order freezes the authoritative package/quote reference, source version, amount/currency, applicable fee/tax/disclosure facts and buyer attribution; Payment executes the financial rail. An authoritative paid Order outcome permits Trust to continue, but never proves screening clearance. Source contracts must reject stale/unavailable quotes and replay the original Order under the same semantic purchase key.

Voluntary Candidate/Professional screening is optional, subject-initiated and subject-paid by default. A required workflow gate does not silently create employer sponsorship; a different payer/initiator requires the separately approved sponsored workflow described by the canonical registry.

Implementation remains gated on a source-specific schema/constraint and transition contract, paid-result correlation, replay/refund/recovery semantics, and provider/legal requirements. Do not reuse marketplace seller-acceptance or fulfillment assumptions for screening. These are execution prerequisites, not a question about whether paid screening is allowed. Existing Prisma `OrderSourceType` values describe represented structure only.

## WA-R008 — Media public-access integration

This consumer invokes SH-127 `requestMediaAccess` with its own actor/resource/action-bound contextual authorization and required evidence. Media independently evaluates asset safety, grant, scope, expiry and revocation, then performs SH-087 `issueSignedMediaUrl` internally. The consumer never calls the signer or reads storage directly. SH-127's identity is approved; its registry status remains Proposed ruling for owner-specific integration completion. Bind the caller's exact contextual decision and failure/access-proof semantics before production use. A Media failure must not be recorded as successful file access.


## WA-R012 — Purchased session allowance and Booking cardinality (P02)

Product-owner ruling approved 2026-09-29: an Order may authorize multiple scheduled sessions **only when the purchased Offering/package explicitly includes them**. Four purchased sessions permit at most four allocated session entitlements, not unlimited Bookings. This closes U-BC-02 / CL-05-U014's product choice. Do not add uniqueness on Booking.orderId.

Supply owns the offered package description. Order validates and snapshots the purchased positive integer session allowance, source/version and applicable fulfillment/cancellation/refund terms; later Offering edits cannot change the purchase. Booking owns each appointment and its conflict, hold and scheduling lifecycle. Neither a paid flag nor counting local Booking rows supplies purchase authorization.

Technical ruling: Order owns durable per-session authorization identities bounded by the purchased allowance. An idempotent reservation command binds Order/session identity to one Booking command intent and reports authorized, exhausted, denied, or unavailable with the Order version. Concurrent attempts cannot reserve the same session twice or exceed the allowance. Booking persists the reservation identity with its local conversion; an outbox acknowledgement confirms attachment. An uncertain cross-owner outcome remains reserved until reconciliation queries Booking's durable result; never release merely on transport timeout. Failed conversion with proven absence can release its reservation idempotently. This is a recoverable workflow, not a cross-owner Prisma transaction.

Rescheduling retains the session authorization through the replacement chain and does not consume another session. A completed, cancelled or no-show appointment does not itself restore allowance or prove full Order completion. Order applies the purchased terms and owner-confirmed session outcomes; refunds and cancellation adjustments are Order decisions through Payment's rail. No automatic equal-price-per-session refund or forfeiture policy is invented. Packages cannot activate without explicit applicable terms. A normal SlotLock converts at most once (U-BC-03); that safety invariant is separate from Order multiplicity.

Implementation acceptance: four-session package permits four distinct authorizations and rejects a concurrent fifth; retry returns the same identity; single-session package remains bounded; reschedule reuses authorization; timeout recovery avoids double release/allocation; source edits do not rewrite terms; partial fulfillment does not finish the whole Order; refund/cancel outcome follows snapshotted terms. Current schema lacks this complete contract; the coordinated database pass must implement it before package activation.


## WA-R019 — Consent catalog, acceptance causation and buyer provisioning

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R019 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r019--consent-catalog-acceptance-causation-and-buyer-provisioning) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

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


## WA-R041 — Retention-safe commercial snapshot links

Classification: AI_RESOLVED_WITH_TRADEOFF. Resolves CL04-U016; complements WA-R030/032/037.

Order retains an immutable purchase snapshot with the applied Track plan/price/grant policy identities and revisions, exact values used for fee/commission calculation, effective decision time and source decision references. Current catalog selection is separate. Historical identifiers remain meaningful even when an enrollment or catalog revision stops being current. Any navigation FK must restrict deletion or detach only that optional navigation while preserving the lawful retained immutable proof; never cascade-delete Order purchase evidence from Track cleanup. Actual lawful erasure/minimization follows Privacy's approved field disposition and retention policy, not indefinite retention by this ruling.

This resolves snapshot semantics and deletion behavior; exact FK names and coordinated forward migration remain implementation work. No catalog change reprices an accepted purchase. Verify retired plans, ended enrollment, valid privacy disposition, missing navigation target and historical refund reconstruction against the original basis.


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


## WA-R050 — Media stewardship, access evidence and export artifacts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Physical code/repository stewardship for contextual attachment joins follows their semantic owner: OrderFile belongs in Transaction / Order; MessageMedia in Messaging; ProfessionalProfileMedia in Professional Eligibility; OfferingMedia in Marketplace Supply; candidate/resume associations in Candidate Application. Any additional explicit association is placed in its parent business owner, not in a generic Media ownership repository. Prisma remains one coordinated schema/migration surface; storage placement is not lifecycle ownership. Media repositories mutate only Media assets, versions, renditions, upload sessions, grants and technical proof. Owners create/detach contextual joins after Media readiness checks; cross-owner cascade deletion is prohibited without Privacy disposition. This settles MFA-UR-03 without requesting cosmetic table migration.

Keep three distinct identities: contextual owner authorization/grant, Media transport grant/token, and actual delivery observation. `requestMediaAccess` receives authenticated actor/service, exact Media version, purpose/action, owner context and current decision proof; Media rechecks safety, sensitivity, expiry and revocation. Agreement document-view/download grants are reusable within bounded validity and current authorization; a renewed grant is a new decision linked to its predecessor. No perpetual renewal or automatic download entitlement follows possession. Issuance alone never marks `used` or completion. For reusable access, first-use is observation evidence, not terminal state; one-time transport policy may consume its own token atomically only when expressly specified, without consuming a Digital Goods logical-download allowance. Old ambiguous `used` values require migration classification and cannot silently deny an otherwise approved reusable flow.

Digital Goods duplicate filename/mime/size/checksum/version fields are immutable purchased/delivered version snapshots only. Current Media availability, safety, quarantine, deletion and access decisions govern each serving attempt; historical snapshot values never authorize bytes. The source identity cannot drift to a new asset version under an old purchase merely because metadata matches.

Privacy export bundle creation uses existing `createMediaUploadSession` with Privacy job/bundle/version context and owner authorization, then uploads through the returned Media-owned bounded mechanism, then `completeMediaUpload`. Completion is asynchronous if validation/scanning/processing remains; `getMediaUploadStatus` and `getMediaReadiness` return finalized version/readiness evidence. Privacy may report artifact-ready only for a private ready version and its complete owner contribution manifest, never merely upload acceptance. Logical key is Privacy job+bundle revision; same key replays session/artifact result, changed bytes conflict or require a new revision. A failed scan prevents distribution; incomplete upload resumes/retries the same session where supported, otherwise supersedes it with recorded lineage. Privacy evaluates export requester/current authority, Media applies SH-127, and sensitive proof follows WA-R023. No public export URL is persisted.

Upload-session state is separate from MediaAsset state: initiated→uploading→uploaded→validating→scanning (when required)→processing (when required)→completed, with failed/rejected/cancelled/expired terminal attempts. Required stages cannot be skipped by provider success. A retry after terminal failure creates a linked new attempt; ready/frozen/deleted are asset states only. Immutable policy revision identity is stored on the attempt; changes do not rewrite historical validation criteria, while current safety can still block serving. Scanner callbacks are required only if a selected provider uses callbacks; when used they pass canonical verification/dedupe/normalization.

Production scanner selection, encryption/key qualification, legal retention and broad public-original exposure remain separately gated; do not infer vendor approval. Verify detached associations retaining shared bytes, concurrent access/revocation, grant renewal, failed download not consuming allowance, stale snapshot quarantine, export failure/retry and policy revision replay before activation.


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


## WA-R068 / WA-R069 — Authority facts and committed event obligations

This Module adopts its `transaction_order` action/fact row and specifically registered producer/consumer effects in `context/reconciliation/authority-event-contracts.md`. Role interprets the catalog; this owner retains facts and lifecycle. Register each concrete protected port before activation; a grouped port row does not authorize unspecified commands.

Owner action scope: `createOrderFromOffering / acceptOrder / recordAgreementSignature / recordOrderDelivery`. Permitted relationships: current authorized buyer/seller/signatory; registered service for outcome receipts. Required owner facts: Order source/participants/revision, immutable commercial snapshot, agreement presented revision, signature authority and consent, effect identity. Assurance: ordinary B; signature/financial adjudication S; Agreement evidence A. These facts include typed target, source revision, subject relationship, purpose/action and evaluation time; missing/stale/unavailable facts cannot authorize, and current revisions are checked again at effect. B/S/A have the precise appendix meanings; source services cannot invent human assurance.

Producer obligations:

- `order.outcome_changed.v1`: Order/source, participant bindings, immutable outcome/revision, safe qualification evidence reference. Registered effect: Gig projection; Review eligibility; Booking/Digital access reevaluation; Gamification/Sweepstakes qualification.
- `order.purchase_qualification_changed.v1`: Order, buyer User, Professional/User when applicable, purchase fact revision, amount/currency, policy basis, correction lineage. Registered effect: Gamification/Sweepstakes consume approved purchase rule only; platform screening source never fabricates seller.
- `order.delivery_timeliness_changed.v1`: Order, seller User/Professional when applicable, contractual deadline/version, verified delivery time/evidence revision, onTime determination basis. Registered effect: Gamification delivery_on_time only for qualified supported source.

Consumer obligations:

- `customer.lifecycle_changed.v1`: consume only the effect naming this Module — Order/Gig: reevaluate new participation; existing rights remain owner-governed.
- `payment.financial_readiness_changed.v1`: consume only the effect naming this Module — Professional, Track, Order, Gamification, Sweepstakes: action-specific reevaluation.
- `payment.effect_recorded.v1`: consume only the effect naming this Module — Order/Track/Gamification/Sweepstakes: correlate only their instruction; reconcile unknown; no provider secrets.
- `booking.performance_reported.v1 / booking.performance_adjudicated.v1`: consume only the effect naming this Module — Order/Review may separately evaluate; no automatic money/review eligibility consequence.

Each audience receives only its needed fields. Obtain fresh source facts before protected decisions; invalidation is not authority.

Persist source history and outbox intent atomically; use event identity/fingerprint deduplication, source-revision watermarks, tombstones and correction lineage as specified by WA-R069. Delayed facts cannot restore revoked exposure; gaps require owner replay/current snapshot. Registered Hold applicability may prompt current reevaluation only for existing typed targets/actions; release is never automatic restoration or financial execution. Source events cannot substitute for explicit Privacy/Moderation/provider effect commands or WA-R066 notification intents.

Order owns purchase qualification and delivery timeliness facts. Bind contractual deadline/agreement revision, verified owner delivery receipts, participant User mappings, supported source kind and correction lineage. Missing deadline or disputed/unverified delivery cannot be guessed on-time. Booking performance reports do not independently establish full-Order completion or money/review consequences.

## WA-R071 — Purpose-specific Location facts and disclosure

Location alone decides precision/reveal under WA-R071. Supply current typed owner facts and opaque source revisions; an event or cache is not authorization. Changes emit only source/context identity, revision and change kind, never exact coordinates/address/phone. Source relocation, cancellation, disqualifying refund/dispute, completion, participant/restriction/policy changes invalidate prior allow; fresh queries must prevent stale events from restoring it.

Supply current Order revision, service/session authorization identity, buyer and performing Professional identities, current cancellation/refund/dispute restrictions and source reference. Validate consistent attached Booking/session relations; do not decide Location permission or use payment entitlement as reveal authority.


## WA-R075 — Typed Hold action applicability and source readiness

This owner adopts its source/consumer obligations in `context/reconciliation/hold-action-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.
