# Privacy & Location Safety Architecture

> **Repository location:** `context/privacy-location-safety/architecture.md`  
> **Cluster ID:** CL-08  
> **Cluster name:** Privacy & Location Safety  
> **Cluster type:** `privacy_compliance_safety_control`  
> **Document status:** Implementation-grade cluster architecture with explicit decision gates  
> **Audience:** Coding agents, developers, reviewers, maintainers, compliance reviewers, and future architecture agents  
> **Update rule:** Update this file whenever a binding CL-08 architectural decision changes. Build progress must not redefine this architecture.

---

## 1. Document Status and Scope

CL-08 coordinates two Deep Modules:

- `privacy_data_erasure` — Privacy / Data Erasure Module
- `location_safety` — Location Safety Module

This Cluster is a planning, integration, and controlled-context boundary. It is **not** a source-of-truth owner and does not take ownership of either Module's lifecycle.

The root Workin Ants architecture remains authoritative for platform-wide rules such as actor identity, authorization, consent proof, entitlements, compliance holds, search projection, media/file mechanics, audit, observability, provider boundaries, and shared operations. This document narrows those rules to the privacy and location-safety workflows.

Module architectures remain authoritative for Module-local truth. Where this Cluster document introduces a required decision that is not yet established by stronger evidence, it is labeled **Proposed Ruling**. Proposed Rulings are not silently binding until approved. Items that still lack sufficient evidence are recorded in **Deferred / Unresolved Decisions** and must not be invented during implementation.

### Source reconciliation notes

Two source inconsistencies are material to CL-08:

1. The Deep Module Registry, Location Safety extract, glossary definition of Exact Location Reveal, and Canonical Shared Operations all place exact-location reveal policy and `LocationReveal` truth with Location Safety. A compliance-inventory row also associates the fuzzy-geolocation/exact-reveal control with Booking & Calendar. **Binding interpretation:** Booking is supporting gate evidence; Location Safety remains the lifecycle and policy owner. The compliance inventory should be synchronized.
2. Privacy / Data Erasure declares both GDPR/CCPA rights and contract-retention exemptions as compliance responsibilities, while its `complianceSatisfied` mapping explicitly lists only the GDPR/CCPA term. This is a registry synchronization gap, not a transfer of retention-exemption ownership.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

CL-08 protects personal data and location-sensitive data through two distinct controls:

```text
privacy right
→ verified request
→ cross-Module inventory
→ owner-executed disposition
→ retention/export/erasure proof

location-bearing source data
→ Location Safety precision policy
→ fuzzy public projection
or
→ gated, viewer-specific exact reveal
```

### Goal

The Cluster must make two questions answerable without ambiguity:

1. **Privacy:** What data must be exported, erased, anonymized, corrected, restricted, retained, or reported as failed, and which Module owns execution against that data?
2. **Location:** Which location representation may be exposed on a public surface, and when may an exact private location be disclosed to a specific viewer?

### Inputs

CL-08 receives:

- authenticated actor context;
- privacy request type and requester;
- identity-verification result when required;
- subject-data inventories from source Modules;
- record-owner retention facts;
- owner-executor results;
- source-domain location facts;
- Booking and Order gate facts;
- privacy, moderation, hold, and source-visibility changes;
- provider results through provider-owning Modules;
- policy/rule versions where established.

### Outputs

CL-08 produces:

- `PrivacyRequest` lifecycle state;
- `DataErasureJob` orchestration state;
- target-level privacy dispositions;
- `DataRetentionExemption` proof;
- `DataExportBundle` state;
- public-safe fuzzy location payloads backed by `FuzzyLocationCache`;
- exact-location reveal decisions and `LocationReveal` proof;
- requests to Search, Media, Audit, Notification, and other source owners;
- privacy/location domain events when event contracts are approved;
- operational failure signals without replacing domain truth.

### What CL-08 explicitly does not own

CL-08 does not own:

- authentication or account recovery;
- general authorization interpretation;
- consent acceptance;
- CustomerProfile, ProfessionalProfile, CandidateProfile, or Organization membership lifecycles;
- Order or Booking lifecycles;
- payment, tax, dispute, contract, or subscription truth;
- file storage, scanning, signed-URL mechanics, or EXIF/GPS scrubbing;
- search indexing or Typesense state;
- generic `AuditEvent`, `AccessAuditLog`, `QueueJob`, `IntegrationFailure`, or `ComplianceHold`;
- notification delivery;
- map rendering;
- provider state as domain truth;
- legal rules that determine tax, contract, fraud, dispute, security, or other mandatory retention.

---

## 3. Module Inventory

| Module ID | Module name | Module type | Purpose | Owned truth | Primary responsibility in CL-08 | Major inbound dependencies | Major outbound consumers |
|---|---|---|---|---|---|---|---|
| `privacy_data_erasure` | Privacy / Data Erasure Module | compliance; `mvp_active_legal_gated` | Own formal privacy-rights requests and cross-service fulfillment orchestration. | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, `DataExportBundle` and their statuses/enums. | Verify/scope requests, inventory subject data, dispatch owner instructions, aggregate outcomes, preserve retention exceptions, produce exports, and complete privacy proof. | Identity & Access; Role / Authority; each data owner; Media; Search; Audit; Observability; Notification. | Identity; Customer; Track; Media; Messaging; Video; Search; Transaction; Payment; Location Safety; Observability. |
| `location_safety` | Location Safety Module | compliance; `mvp_active` | Keep exact/sensitive locations private by default while providing safe public approximations and gated exact disclosure. | `FuzzyLocationCache`, `LocationReveal`, `LocationPrecision`, `LocationRevealStatus`; fuzzing and reveal policy. | Own public-location precision, fuzzy projection, reveal decisions, viewer-specific reveal state, revocation, and location-access proof context. | Identity & Access; Role / Authority; Booking; Order; Search; Audit; Privacy; crypto; geocoding adapter; shared jobs. | Search; Booking; Order; Marketplace Supply; Gig Demand; Hiring; Media policy consumers; Audit. |

---

## 4. Cluster Architecture Principles

1. **Privacy owns the legal/request workflow; data owners own their records.**  
   Privacy may orchestrate another Module's change but must not become a universal repository that rewrites every Module's tables.

2. **Location Safety owns reveal policy; source Modules own source location facts.**  
   A Booking, Gig, Offering, Job, Organization, or other source record remains owned by its source Module. Location Safety determines permitted precision and exact-reveal policy.

3. **Exact and fuzzy location are different truths.**  
   Exact location is private source data. `FuzzyLocationCache` is a derived, safe public-location projection.

4. **`LocationReveal` is not generic audit.**  
   It is domain proof of viewer/context reveal state. `AccessAuditLog` is separate append-only sensitive-access proof.

5. **Product deletion is not privacy erasure.**  
   `deletedAt` or local deletion flags cannot complete a privacy request.

6. **Retention is owner-informed, Privacy-recorded.**  
   Financial, contract, dispute, fraud, consent, security, and subscription owners supply authoritative retention facts. Privacy records the resulting `DataRetentionExemption`.

7. **Search remains projection.**  
   CL-08 requests Search-owned refresh/de-index work. It does not write `SearchUpsertEvent` directly or call Typesense as domain code.

8. **Media remains the file-mechanics owner.**  
   Privacy may require a file deletion or export artifact; Media owns storage-object deletion, processing truth, access grants, and signed URLs.

9. **Provider deletion stays with the provider-owning Module.**  
   Privacy issues the authorized instruction. The Module that owns Stripe, R2, Daily, Mux, Agora, Cronofy, subscription billing, or another provider owns its adapter and result translation.

10. **Shared mechanism does not merge truth.**  
    Idempotency, queues, workflow runners, encryption, hashing, retries, locks, and audit writers are reused without moving privacy or location lifecycle ownership.

11. **ComplianceHold is the only reusable platform stop sign.**  
    CL-08 must not create `privacyBlocked`, `locationBlocked`, `revealBlocked`, or equivalent competing lifecycle booleans.

12. **No public consumer receives exact coordinates by reconstruction.**  
    Search, map UI, marketplace listings, Gigs, Hiring, and other public consumers receive Location Safety-approved public payloads only.

13. **No entitlement creates privacy or location authority.**  
    Track entitlements remain commercial policy truth. They do not replace privacy-rights processing or exact-location authorization.

14. **Audit and observability are evidence about execution, not lifecycle truth.**  
    A successful log write cannot make a failed privacy target complete, and an `IntegrationFailure` cannot replace a privacy or reveal status.

---

## 5. Runtime / Collaboration Topology

### Privacy fulfillment topology

```text
User / Admin
   │
   ▼
route / server action / API
   │
   ├─ resolveAuthenticatedActor
   ├─ validate input
   └─ authorizeResourceAction
          │
          ▼
Privacy / Data Erasure application service
   │
   ├─ PrivacyRequest truth
   ├─ identity-verification orchestration
   ├─ enumerateSubjectData protocol
   ├─ evaluateRetentionRequirement protocol
   ├─ DataErasureJob / DataErasureTarget truth
   └─ orchestratePrivacyFulfillment
          │
          ├─────────────► source Module executor A
          ├─────────────► source Module executor B
          ├─────────────► source Module executor C
          │
          ├─────────────► Media / File Access
          ├─────────────► Search / Public Visibility
          ├─────────────► Notification
          └─────────────► Audit / Event Ledger
                              │
                              ▼
                       generic proof only

Asynchronous work:
Privacy truth
   → enqueueReliableJob
   → owner-specific worker
   → owner truth/provider adapter
   → typed privacy disposition result
   → Privacy target update
   → aggregate/reconcile request outcome
```

### Location safety topology

```text
Source Module or protected viewer request
   │
   ├─ resolveAuthenticatedActor
   ├─ authorizeResourceAction
   └─ queryOwnerFacts from Booking / Order / source owner
          │
          ▼
Location Safety application service
   │
   ├─ classify precision
   ├─ applyFuzzyPublicLocation
   ├─ resolveLocationReveal
   └─ write LocationReveal / FuzzyLocationCache truth
          │
          ├─────────────► encryptSensitiveValue / normalizeAndHashIdentifier
          ├─────────────► recordSensitiveAccess
          └─────────────► requestSearchProjectionRefresh
```

### Cross-Module database rule

The default integration pattern is:

```text
consumer
→ public Module command/query
→ owner application service
→ owner repository
→ owner truth
```

Direct cross-Module Prisma reads are not the default. They are prohibited when a public owner interface exists or when the read would require the consumer to reinterpret another Module's lifecycle.

---

## 6. Folder / Code Organization

The repository should preserve Module ownership in code. The following structure is the CL-08 target organization; if root `code-standards.md` establishes an equivalent naming convention, follow the root convention while preserving these boundaries.

```text
context/
└── privacy-location-safety/
    ├── architecture.md
    └── build-plan.md

src/
├── modules/
│   ├── privacy-data-erasure/
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   ├── orchestration/
│   │   │   └── services/
│   │   ├── domain/
│   │   │   ├── policies/
│   │   │   ├── transitions/
│   │   │   └── types/
│   │   ├── contracts/
│   │   │   ├── public.ts
│   │   │   ├── privacy-executor.ts
│   │   │   └── privacy-export.ts
│   │   ├── infrastructure/
│   │   │   └── repositories/
│   │   ├── workers/
│   │   ├── ui/
│   │   └── tests/
│   │
│   └── location-safety/
│       ├── application/
│       │   ├── commands/
│       │   ├── queries/
│       │   └── services/
│       ├── domain/
│       │   ├── precision/
│       │   ├── reveal/
│       │   └── types/
│       ├── contracts/
│       │   └── public.ts
│       ├── infrastructure/
│       │   ├── repositories/
│       │   └── geocoding/
│       ├── workers/
│       └── tests/
│
├── platform/
│   ├── shared-operations/       # only canonical shared operations
│   ├── events/                  # outbox/inbox mechanism
│   ├── jobs/                    # reliable queue mechanism
│   ├── crypto/                  # canonical encryption/hash primitives
│   └── observability/
│
└── integrations/
    └── ...                      # only where root architecture requires provider packages here
```

### Folder rules

- Do not create a cluster-wide `privacy-location-safety/service.ts` that owns both Modules.
- Do not create a generic `location/` helper library used to bypass Location Safety policy.
- Do not place R2, Typesense, Stripe, Daily, Mux, Agora, Cronofy, or notification-provider clients in Privacy.
- A geocoder adapter may live under Location Safety only if the proposed geocoder ownership ruling is approved.
- Generic crypto, queue, idempotency, audit, and observability mechanisms stay in their canonical shared owners.
- Cluster-local coordination should be minimal. Privacy-to-Location interaction occurs through the standard privacy executor protocol, not through a new Cluster lifecycle.

---

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
|---|---|---|---|
| Privacy / Data Erasure | Privacy request, erasure job, target disposition, retention-exemption record, export-bundle lifecycle, fulfillment orchestration | identity proof; owner inventories; owner retention facts; owner execution results; Media/Search/Audit/Notification interfaces | source records in other Modules; provider clients owned elsewhere; generic queue/audit truth |
| Location Safety | fuzzy-location projection, precision policy, viewer/context reveal state, reveal/revocation policy | source exact-location facts; Booking/Order facts; authority; holds where applicable; crypto; audit; Search | Booking/Order lifecycle; map UI; Search index; generic audit; Media EXIF processing |
| Identity & Access | authenticated actor, User identity, security assurance, account recovery | Privacy completion result where required | PrivacyRequest; LocationReveal |
| Role / Authority | permission interpretation | owner relationship facts supplied by source Modules | privacy eligibility, retention policy, reveal safety policy |
| Customer / Buyer Profile | CustomerProfile truth and its privacy executor | privacy instruction | privacy request lifecycle |
| Track Subscription & Entitlement | subscription, grant, usage, billing-policy truth and its privacy executor | privacy instruction | privacy request lifecycle; local privacy flags |
| Booking & Calendar | Booking lifecycle and Booking-owned location data physically stored on Booking | Location Safety reveal decision | exact-reveal lifecycle/policy |
| Transaction / Order | Order and transaction truth; agreement/contract records it owns | Location reveal status; privacy instruction | LocationReveal; privacy request |
| Search / Public Visibility | `SearchUpsertEvent`, provider indexing, reconciliation, public query | fuzzy location; privacy de-index requests | exact-location derivation; privacy request truth |
| Media / File Access | MediaAsset, validation/scanning, object mechanics, MediaAccessGrant, signed URL | privacy delete/export instructions; context authorization | PrivacyRequest; DataExportBundle lifecycle |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | sanitized privacy/location proof requests | PrivacyRequest; DataErasureTarget; LocationReveal |
| Observability / Ops | logs, queue telemetry, IntegrationFailure, incidents | correlation and safe operational metadata | privacy/reveal business status |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle | privacy/location source evidence | local CL-08 blocked-state systems |
| Notification | Notification and delivery lifecycle | CL-08 notification requests | privacy/location business event meaning |

---

## 8. Data Ownership

### 8.1 CL-08-owned models and enums

| Record / enum | Owner | Meaning |
|---|---|---|
| `PrivacyRequest` | Privacy / Data Erasure | Formal privacy-rights request and aggregate lifecycle. |
| `PrivacyRequestType` | Privacy / Data Erasure | `access`, `export`, `erasure`, `correction`, `restriction`. |
| `PrivacyRequestStatus` | Privacy / Data Erasure | `submitted`, `verifying_identity`, `verified`, `processing`, `completed`, `partially_completed`, `rejected`, `cancelled`. |
| `DataErasureJob` | Privacy / Data Erasure | Durable erasure orchestration record. |
| `DataErasureJobStatus` | Privacy / Data Erasure | `queued`, `running`, `completed`, `partially_completed`, `failed`, `cancelled`. |
| `DataErasureTarget` | Privacy / Data Erasure | One privacy-erasure target and its disposition evidence. |
| `DataErasureTargetType` | Privacy / Data Erasure | Controlled target vocabulary for currently modeled erasure targets. |
| `DataErasureTargetStatus` | Privacy / Data Erasure | `pending`, `erased`, `anonymized`, `retained`, `failed`, `skipped`. |
| `DataRetentionExemption` | Privacy / Data Erasure | Privacy-owned proof that an owner-held record is retained for a documented reason. |
| `DataRetentionExemptionReason` | Privacy / Data Erasure | `tax_record`, `payment_record`, `dispute_record`, `fraud_prevention`, `legal_obligation`, `security_audit`, `consent_proof`, `contract_record`, `signature_record`, `subscription_billing_record`, `other`. |
| `DataExportBundle` | Privacy / Data Erasure | Privacy export artifact lifecycle and Media reference. |
| `DataExportStatus` | Privacy / Data Erasure | `queued`, `generating`, `ready`, `expired`, `failed`. |
| `FuzzyLocationCache` | Location Safety | One approved fuzzy projection per `targetType + targetId`, including radius and freshness. |
| `LocationReveal` | Location Safety | Viewer/context-specific exact-location reveal state and proof. |
| `LocationPrecision` | Location Safety | `public_fuzzy`, `approximate`, `exact_after_booking`, `exact_private`. |
| `LocationRevealStatus` | Location Safety | `hidden`, `eligible`, `revealed`, `revoked`. |

### 8.2 Privacy target executor ownership

`DataErasureTarget` is Privacy truth. The target's underlying data remains owned elsewhere.

| `DataErasureTargetType` | Executor / owner of underlying truth | CL-08 rule |
|---|---|---|
| `postgres_user` | Identity & Access | Identity executes account-data disposition. |
| `postgres_profile` | The specific profile owner | The descriptor must identify the actual profile owner; Privacy must not infer one universal profile table policy. |
| `postgres_message` | Messaging | Messaging decides message/thread relational-safe erasure/anonymization. |
| `postgres_thread` | Messaging | Same owner; thread participation/retention stays Messaging-owned. |
| `postgres_notification` | Notification | Notification executes its own record disposition. |
| `media_asset` | Media / File Access | Media handles metadata and storage mechanics. |
| `r2_object` | Media / File Access | Privacy does not call R2 directly. |
| `typesense_document` | Search / Public Visibility | Search de-indexes through its public interface. |
| `daily_room_or_log` | Video Session | Video owner calls provider. |
| `stripe_customer_reference` | Payment / Payout / Tax | Financial owner supplies retention and provider disposition. |
| `calendar_provider_reference` | Booking & Calendar | Calendar owner handles provider unlink/deletion. |
| `mux_asset_or_playback_reference` | Video Session | Video owner handles provider resource. |
| `agora_room_or_log` | Video Session | Video owner handles provider resource. |
| `course_video_playback_grant` | Video Session | Video grant truth remains Video-owned. |
| `digital_download_grant` | Digital Goods Access | Digital Goods executes its own grant disposition. |
| `digital_download_event` | Digital Goods Access | Owner retention rules apply. |
| `course_accessibility_asset` | Digital Goods Access / Media by file mechanics | Business record stays Digital Goods-owned; bytes stay Media-owned. |
| `agreement_record` | Transaction / Order | Contract retention facts come from Transaction / Order. |
| `agreement_document_snapshot` | Transaction / Order; Media for bytes | Retention may require preservation; Privacy records exemption. |
| `agreement_signature_metadata` | Transaction / Order | Signature/legal proof remains owner truth. |
| `agreement_access_grant` | Transaction / Order | Contextual grant truth stays Transaction / Order-owned. |
| `media_upload_session` | Media / File Access | Media executes. |
| `media_scan_result` | Media / File Access | Security/legal retention may apply. |
| `media_processing_result` | Media / File Access | Media executes. |
| `media_access_grant` | Media / File Access | Media executes. |
| `media_access_event` | Media / File Access | Media retention policy applies. |
| `media_processed_derivative` | Media / File Access | Media removes derived objects through storage mechanics. |
| `customer_profile` | Customer / Buyer Profile | Customer owner executes profile disposition. |
| `track_subscription` | Track Subscription & Entitlement | Track owner executes while preserving billing retention where required. |
| `track_entitlement_grant` | Track Subscription & Entitlement | Track owner executes. |
| `track_usage_event` | Track Subscription & Entitlement | Track owner supplies retention facts. |
| `track_usage_counter` | Track Subscription & Entitlement | Rebuildable counter may be deleted/rebuilt under owner policy. |
| `track_subscription_event` | Track Subscription & Entitlement | Billing/legal history may require retention. |
| `billing_customer_reference` | Track Subscription & Entitlement | Subscription-provider boundary. |
| `subscription_provider_reference` | Track Subscription & Entitlement | Track owner calls billing provider. |
| `other` | Explicit owner required in target descriptor | `other` must never authorize a generic direct database/provider deletion. |

### 8.3 Referenced records that remain externally owned

CL-08 may consume, but does not own:

- `User`, `CustomerProfile`, `ProfessionalProfile`, `CandidateProfile`;
- `Organization`, `OrganizationMember`;
- `Booking`, `Order`, `Agreement`, `AgreementDocumentSnapshot`, `AgreementSignature`;
- `Thread`, `Message`, `Notification`;
- `MediaAsset`, `MediaAccessGrant`, Media processing/scan records;
- `TrackSubscription`, `TrackEntitlementGrant`, `TrackUsageEvent`, `TrackUsageCounter`, `TrackSubscriptionEvent`;
- `PayoutTransfer`, `TaxProfile` and other financial retention facts;
- `SearchUpsertEvent`;
- `AuditEvent`, `AccessAuditLog`;
- `ComplianceHold`;
- provider-specific processed-event ledgers.

### 8.4 Projections, snapshots, grants, and ledgers

- `FuzzyLocationCache` is CL-08-owned derived projection truth.
- Search-provider documents are **not** CL-08 truth.
- `DataExportBundle` is Privacy-owned export lifecycle; the stored file is a Media-owned asset.
- `LocationReveal` is a domain-specific sensitive access/reveal record, not a generic `MediaAccessGrant` and not `AccessAuditLog`.
- CL-08 owns no provider-event dedupe ledger.
- CL-08 owns no generic audit ledger.
- CL-08 currently has no dedicated privacy-domain event ledger model.
- `User.privacyErasedAt` and `User.privacyErasureStatus` physically live on Identity-owned `User`.

**Proposed Ruling PR-08-01 — Identity erasure marker projection**  
Treat `User.privacyErasedAt` and `User.privacyErasureStatus` as Identity-owned projections of a Privacy-owned completed result. They may not independently declare a PrivacyRequest complete.

---

## 9. Lifecycle Ownership

### 9.1 PrivacyRequest lifecycle

**Owner:** Privacy / Data Erasure

Status vocabulary:

```text
submitted
verifying_identity
verified
processing
completed
partially_completed
rejected
cancelled
```

Only Privacy may transition `PrivacyRequest.status`.

Other Modules may:

- return identity proof;
- enumerate subject data;
- return retention facts;
- execute a requested disposition;
- return target results;
- react to a final result.

They may not mark the request complete.

**Unresolved transition details:** cancellation cut-off, rejection authority/categories, identity-proof requirements, access-versus-export semantics, and whether retained targets produce `completed` or `partially_completed`.

### 9.2 DataErasureJob lifecycle

**Owner:** Privacy / Data Erasure

Status vocabulary:

```text
queued
running
completed
partially_completed
failed
cancelled
```

`QueueJob` or worker-attempt state is operational and must not be confused with this lifecycle.

### 9.3 DataErasureTarget lifecycle

**Owner:** Privacy / Data Erasure

Status vocabulary:

```text
pending
erased
anonymized
retained
failed
skipped
```

The source Module performs the underlying action. Privacy records the authoritative target disposition returned through `executePrivacyInstruction`.

A target-level `retained` result requires a Privacy-owned `DataRetentionExemption` based on owner-supplied retention facts.

### 9.4 DataExportBundle lifecycle

**Owner:** Privacy / Data Erasure

Status vocabulary:

```text
queued
generating
ready
expired
failed
```

Media owns the underlying object and temporary delivery mechanics. Privacy owns whether the bundle is ready and whether the request is entitled to receive it.

### 9.5 Fuzzy location projection lifecycle

**Owner:** Location Safety

Current schema permits one `FuzzyLocationCache` per `targetType + targetId`.

Lifecycle behavior:

```text
source location/policy changes
→ generate or refresh projection
→ public consumers read safe projection
→ expiry/source removal/privacy restriction
→ refresh or invalidate
```

The exact target registry, radius policy, stability algorithm, and regeneration policy are decision-gated.

### 9.6 Exact-location reveal lifecycle

**Owner:** Location Safety

Status vocabulary:

```text
hidden
eligible
revealed
revoked
```

`LocationReveal.status` is the domain reveal state. Booking's `locationRevealStatus` must not become a second lifecycle owner.

**Proposed Ruling PR-08-02 — Booking duplicate location fields**  
Until a schema reconciliation is approved, treat `Booking.locationPrecision`, `Booking.fuzzyLat`, `Booking.fuzzyLng`, and `Booking.locationRevealStatus` as non-authoritative compatibility/snapshot fields. New policy logic must read Location Safety truth, not infer reveal state from Booking. Migration/removal or explicit snapshot synchronization remains decision-gated.

---

## 10. Public Module Interfaces

### Privacy / Data Erasure interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer |
|---|---|---|---|---|---|---|---|
| `submitPrivacyRequest` | Privacy | self-service UI, support/admin | Create formal privacy request. | actor, request type, minimized request details | request ID, status, requestedAt | truth | fulfillment eligibility or completion |
| `getPrivacyRequest` | Privacy | requester, authorized admin | Read request state. | actor, request ID | status, dates, safe summary, bundle summary where applicable | truth | source Module state |
| `listUserPrivacyRequests` | Privacy | requester, authorized admin | Read request history. | actor/subject, filters | request summaries | truth | data-owner inventory |
| `orchestratePrivacyFulfillment` | Privacy | Privacy worker only | Drive verification, inventory, retention, execution, aggregation, export, completion. | request ID, correlation context | aggregate outcome | truth/workflow result | owner record semantics |
| `enumerateSubjectData` | each data owner through Privacy-defined contract | Privacy | Enumerate owner-held subject data and supported dispositions. | subject, request type, cursor | stable target descriptors, sensitivity, supported actions | owner evidence | permission to mutate |
| `evaluateRetentionRequirement` | data owner supplies facts; Privacy records exemption | Privacy | Determine mandatory retention facts. | target descriptor, request context | required?, reason, basis, retainUntil, minimum fields, permitted anonymization | evidence/decision input | final privacy-request outcome |
| `executePrivacyInstruction` | each data owner | Privacy | Apply owner-local erase/anonymize/export/restrict/etc. | target, requested action, request ID, idempotency key | typed disposition/result/evidence | owner result | privacy request completion |
| `createPrivacyExportArtifact` | Privacy with Media mechanics | requester via Privacy | Assemble and stage export. | request, owner export sections | `DataExportBundle` + Media reference | truth + artifact reference | permanent file entitlement |

### Location Safety interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer |
|---|---|---|---|---|---|---|---|
| `applyFuzzyPublicLocation` | Location Safety | Search; Marketplace; Gig; Hiring; map/public surfaces | Return approved approximate location. | target identity, owner-provided source version/location input or existing cache | fuzzy coordinates/area, radius, precision, expiry/source version | projection | exact coordinates |
| `getPublicLocationProjection` | Location Safety | Search/public consumers | Read current safe projection. | target type, target ID | safe projection + freshness | projection | source location |
| `resolveLocationReveal` | Location Safety | Booking, Order, protected UI | Decide whether exact private location may be shown. | actor/viewer, Booking/Order context, owner gate facts, purpose | allow/deny, permitted precision, reason codes, reveal ID/state, expiry/revocation context | decision + domain proof | authorization from paid/provider state alone |
| `getLocationRevealStatus` | Location Safety | Booking/Order UI, authorized support | Read status without returning exact value. | viewer/context | status, safe reason, timestamps | truth | exact location |
| `revokeLocationReveal` | Location Safety | Booking/Order workflow, authorized admin | Revoke access. | reveal/context, actor/system reason, idempotency key | revoked state | truth | source lifecycle change |
| `listLocationRevealHistory` | Location Safety | authorized compliance/support | Inspect reveal metadata without exact address. | authorized actor, filters | reveal metadata | truth | generic audit ledger |

### Owner-fact interfaces consumed by CL-08

CL-08 depends on narrow owner DTOs rather than direct repository reads:

- Booking gate facts: participant IDs, status, in-person/location mode, source location reference/version, schedule window, cancellation/reschedule facts.
- Order gate facts: participants, payment/transaction state, refund/cancellation/dispute effects, qualifying relationship.
- Source-location facts: target identity, source version, protected location reference/value according to owner policy.
- Identity verification result: durable proof reference suitable for Privacy processing.
- Search projection command acknowledgement.
- Media delete/access/artifact result.
- Audit append acknowledgement.

---

## 11. Canonical Shared Operations Used by This Cluster

The supplied Canonical Shared Operations Registry uses canonical names but does not supply numeric IDs. Only CL-08-relevant operations are listed here.

| Canonical operation | Plain-English meaning | Canonical owner | CL-08 consumers | Reusable mechanism | Local policy that remains local | Invocation point | Must not be duplicated |
|---|---|---|---|---|---|---|---|
| `resolveAuthenticatedActor` | Resolve trusted actor context. | Identity & Access | both Modules | request/session actor resolution | privacy requester/reveal viewer intent | every protected entry point | feature-local current-user helpers |
| `authorizeResourceAction` | Decide platform/org/participant/ownership permission. | Role / Authority | both Modules | typed authorization decision | privacy owner/admin scope; location contextual safety | before protected queries/mutations | `privacyAuth.ts`, `locationPermission.ts` policy engines |
| `queryOwnerFacts` | Read minimum owner facts through owner DTO. | each source Module | both | shared contract, separate implementation | exact facts needed by Privacy/Location | before retention/reveal decisions | cross-domain repositories |
| `evaluateComplianceHold` | Return active reusable stop signs. | Admin Review / Compliance Hold | Location Safety; Privacy where legally applicable | hold query | whether a hold is relevant to the requested action | before action if policy says hold applies | local block flags |
| `authorizeContextualResourceAccess` | Standard shape for context-specific access decisions. | relevant context owner | Location Safety and export access | shared response contract | location/export business predicates | before issuing sensitive result | universal entitlement service |
| `resolveLocationReveal` | Decide exact-location reveal and create LocationReveal proof. | Location Safety | Booking/Order/public protected UI | Module public interface | reveal predicate and lifecycle | exact-location request | Booking/Order reveal service |
| `applyFuzzyPublicLocation` | Produce safe approximate public location. | Location Safety | Search/public source Modules | Module public interface | fuzzing/radius/stability policy | before public projection | Search-side coordinate fuzzing |
| `appendAuditEvent` | Append generic important-action proof. | Audit / Event Ledger | both | insert-only audit command | event meaning and safe metadata | important lifecycle decisions | local audit tables |
| `recordSensitiveAccess` | Append protected-data access proof. | Audit / Event Ledger | both | `AccessAuditLog` writer | exact sensitivity and context | export issuance/download, location reveal | `LocationAccessLog`, `PrivacyAccessLog` |
| `requestNotification` | Deliver a canonical notification request. | Notification | Privacy | channel routing/delivery | message meaning, sensitivity, recipients from owner facts | status-ready/failure notices where approved | direct SES/SMS/push dispatch |
| `executeIdempotentCommand` | Guarantee one business effect under retry. | platform application infrastructure | both | idempotency claim/result | semantic key and conflict behavior | every retryable mutation | Module-local idempotency frameworks |
| `publishDomainEvent` | Publish versioned event after source commit. | platform outbox | both | transactional outbox | event name/payload/emission policy | post-commit cross-Module effects | ad hoc fire-and-forget |
| `deduplicateDomainEvent` | Prevent repeated consumer effect. | platform event infrastructure | both workers | transactional inbox | handler-specific side effect | event consumers | per-worker dedupe tables without shared mechanism |
| `enqueueReliableJob` | Durable async work with retries/dead-letter. | shared queue infrastructure | Privacy and Location workers | queue/lease/heartbeat | business payload and terminal meaning | slow or retryable work | Module-specific queue frameworks |
| `orchestrateWorkflowSteps` | Run persisted multi-step orchestration. | workflow owner using shared runner | Privacy | workflow runner | privacy sequence and compensation/partial semantics | fulfillment | generic Privacy replacement workflow |
| `reconcileWorkflowStatus` | Aggregate step outcomes into owner status. | workflow owner + shared helper | Privacy | deterministic aggregation hook | privacy-specific complete/partial/fail meaning | after target results | QueueJob-derived business status |
| `transitionLifecycleState` | Reuse state-machine plumbing. | shared mechanism; lifecycle owner supplies policy | both | transition validation/update/event hook | privacy and reveal transition graphs | every lifecycle mutation | generic lifecycle policy table |
| `acquireAggregateLock` / `withOptimisticConcurrency` | Serialize conflicting writes or reject stale updates. | shared persistence infrastructure | both | DB lock/CAS | lock key and conflict semantics | request/reveal/target updates | in-memory locks |
| `runDeadlineExpiration` | Invoke owner-defined expiry behavior. | shared scheduler/queue | Privacy exports; fuzzy caches | cursor/schedule dispatch | expiry semantics | `expiresAt` handling | custom cron frameworks |
| `geocodeAddress` | Resolve protected address through provider-neutral adapter. | **proposed:** Location Safety adapter | Location Safety | adapter contract | location privacy, retention, public-safety rules | before fuzzy projection if coordinates absent | map-provider calls in Search/Booking |
| `deleteProviderResource` | Delete/revoke provider resource after authorized instruction. | provider-owning Module | Privacy orchestration | shared provider result contract | provider-specific mapping/retention | owner executor | provider SDKs in Privacy |
| `encryptSensitiveValue` | Managed reversible encryption. | shared security/crypto capability | Location Safety/source owner | envelope encryption | whether/when exact location may be decrypted | exact-location storage/read | local AES helpers |
| `normalizeAndHashIdentifier` | Keyed non-plaintext evidence hash. | shared security/crypto capability | Location Safety, Privacy | HMAC/normalization | which metadata is necessary and retention | IP/request proof | `location-ip-hash.ts` |
| `requestSearchProjectionRefresh` | Ask Search to index/update/hide/remove/restore. | Search / Public Visibility | both | Search command/queue | CL-08 reason and safe source version | privacy/fuzzy-location change | direct `SearchUpsertEvent` writes or Typesense calls |
| `executePrivacyInstruction` | Execute one owner-local privacy disposition. | Privacy orchestrates; each owner executes | Privacy + Location executor | typed protocol | owner-specific fields/retention | per target | local PrivacyRequest workflow |
| `enumerateSubjectData` | Enumerate owner-held subject data. | each data owner through Privacy contract | Privacy | typed protocol | owner schema mapping | scope discovery | global database crawler |
| `evaluateRetentionRequirement` | Return owner-held mandatory retention facts. | data owner supplies facts; Privacy records exemption | Privacy | typed protocol | tax/contract/fraud/etc. facts | before target execution | owner-local exemption tables |
| `anonymizePersonalFields` | Shared field-level anonymization mechanism. | shared primitive; record owner supplies mapping | owner executors | versioned anonymization mechanism | exact fields/invariants | retained/erasable target execution | global unscoped scrubber |
| `orchestratePrivacyFulfillment` | Coordinate Privacy request end to end. | Privacy / Data Erasure | Privacy | owner-local orchestration over shared mechanisms | privacy workflow meaning | after verification | privacy workflows in feature Modules |
| `createPrivacyExportArtifact` | Build encrypted/private temporary export artifact. | Privacy owns bundle; Media owns storage | Privacy | artifact assembly + Media mechanics | export contents/eligibility/expiry | export request | R2/signed-URL implementation in Privacy |
| `issueSignedMediaUrl` | Issue short-lived private Media URL after gates. | Media / File Access | Privacy exports | signed URL mechanics | Privacy export entitlement | export download | custom presigning in Privacy |
| `validateOwnedTargetReference` | Validate a cross-Module target through its owner. | target owner | both | owner-specific validation contract | target relationship/eligibility | target registration/reveal context | direct cross-Module existence checks |
| `createRequestContext`, `writeStructuredLog`, `sanitizeTelemetryMetadata`, `recordIntegrationFailure` | Correlate and observe execution safely. | Observability / platform | both | request IDs, structured logs, redaction, failure records | domain failure status and sensitive-field policy | all workflows | business state in logs |

---

## 12. Cross-Module Data Flows

### 12.1 Privacy request intake

```text
User
→ Identity.resolveAuthenticatedActor
→ Role/Authority.authorizeResourceAction(self privacy request)
→ Privacy.submitPrivacyRequest
→ Privacy writes PrivacyRequest(status=submitted)
→ Audit.appendAuditEvent
→ optional Notification.requestNotification
```

Privacy alone owns the request state.

### 12.2 Privacy erasure fulfillment

```text
PrivacyRequest verified
→ Privacy starts processing
→ Privacy creates DataErasureJob
→ each owner.enumerateSubjectData
→ Privacy registers DataErasureTarget rows
→ each owner.evaluateRetentionRequirement
→ if retention required:
     Privacy writes DataRetentionExemption
     → owner executes permitted anonymization
     → Privacy marks target retained/anonymized as contract dictates
  else:
     Privacy dispatches executePrivacyInstruction
     → owner mutates its own records/providers
     → owner returns typed result
     → Privacy updates DataErasureTarget
→ Privacy.reconcileWorkflowStatus
→ Privacy updates DataErasureJob
→ Privacy updates PrivacyRequest aggregate result
→ Audit records sanitized lifecycle proof
→ Search/Media/other downstream effects occur through owner interfaces
```

### 12.3 Privacy export

```text
verified export request
→ owner.enumerateSubjectData / owner export serializers
→ Privacy assembles purpose-limited manifest
→ Privacy.createPrivacyExportArtifact
→ Media stores private artifact and returns MediaAsset reference
→ Privacy writes DataExportBundle(ready)
→ requester passes authorization
→ Media.issueSignedMediaUrl
→ Audit.recordSensitiveAccess
→ expiry worker marks bundle expired and asks Media to remove object
```

### 12.4 Correction / restriction

```text
verified request
→ owner enumeration
→ owner executes correction/restriction through executePrivacyInstruction
→ owner returns target-level proof
→ Privacy aggregates request outcome
```

**Decision gate:** current `DataErasureTargetStatus` cannot represent corrected/restricted outcomes. Do not implement target-level completion semantics until the proof model is approved.

### 12.5 Fuzzy public location

```text
source owner location created/changed
→ source owner calls LocationSafety.applyFuzzyPublicLocation
   or emits approved source-location event
→ Location Safety obtains protected source facts through owner interface
→ optional geocodeAddress adapter
→ Location Safety applies precision/fuzzing policy
→ write/replace FuzzyLocationCache
→ Location Safety requests Search projection refresh
→ Search builds/indexes only safe fuzzy payload
```

Search never receives exact coordinates unless an entirely separate protected interface explicitly requires them; public search must not.

### 12.6 Exact location reveal

```text
viewer requests exact location
→ resolveAuthenticatedActor
→ authorizeResourceAction
→ Booking/Order owner facts
→ optional evaluateComplianceHold if policy applies
→ LocationSafety.resolveLocationReveal
→ if denied: return safe denial; optionally audit denial
→ if allowed:
     obtain/decrypt exact source location through approved owner/crypto boundary
     → write LocationReveal proof
     → recordSensitiveAccess(location_revealed)
     → return exact value only to authorized request
```

**Decision gate:** exact predicate, directionality, source owner/storage form, context constraint, revocation triggers, and audit fail-closed behavior are unresolved.

### 12.7 Location revocation after gate change

```text
Booking/Order/source location event
→ Location Safety deduplicates event
→ re-evaluates affected reveals
→ revokes invalid reveals
→ writes LocationReveal truth
→ audit event/access proof as required
→ public projection refresh if source/public location changed
```

---

## 13. Cross-Cluster Bridges

| Source | Destination | Information / command | Authoritative owner | Interface / event | Forbidden coupling |
|---|---|---|---|---|---|
| CL-01 Identity & Access | CL-08 | actor and privacy identity-proof result | Identity | `resolveAuthenticatedActor`; privacy verification interface | Privacy reading auth-provider internals |
| CL-01 Role / Authority | CL-08 | permission decision | Role / Authority | `authorizeResourceAction` | local permission engine |
| CL-01 Customer / Buyer Profile | CL-08 | customer subject data and privacy execution | Customer | `enumerateSubjectData`, `executePrivacyInstruction` | Privacy mutating CustomerProfile directly |
| CL-01 Track Subscription & Entitlement | CL-08 | subscription/usage target data and retention facts | Track | privacy executor protocol | local premium/retention booleans in Privacy |
| CL-02 Search | CL-08 | projection refresh acknowledgement; public projection consumer | Search for index; Location for safe payload | `requestSearchProjectionRefresh`, `applyFuzzyPublicLocation` | Privacy/Location calling Typesense directly |
| CL-03 Marketplace Supply | CL-08 | location-bearing Offering facts and privacy targets where supported | source Module | owner facts + Location interface | Location owning Offering |
| CL-03 Payment / Payout / Tax | CL-08 | mandatory financial retention facts and provider execution | Payment | retention/executor protocol | Privacy interpreting Stripe state |
| CL-04 Gig / Demand | CL-08 | Gig location facts and privacy targets where supported | Gig | owner facts + Location interface | Location owning Gig |
| CL-04 Transaction / Order | CL-08 | transaction/reveal gate facts; agreement retention facts | Order | owner fact DTO + privacy executor | Location/Privacy owning Order |
| CL-04 Review / Dispute | CL-08 | dispute retention/hold facts | Review / Dispute | retention interface | Privacy deciding dispute retention itself |
| CL-05 Booking & Calendar | CL-08 | Booking gate/source location facts; provider deletion | Booking | owner facts; privacy executor | Location mutating Booking lifecycle |
| CL-05 Media / File Access | CL-08 | object deletion, export storage/access | Media | file executor + signed access | Privacy owning R2/signed URLs |
| CL-05 Video Session | CL-08 | video subject inventory/provider deletion | Video | privacy executor | Privacy owning Daily/Mux/Agora adapters |
| CL-05 Digital Goods Access | CL-08 | grants/events/accessibility targets | Digital Goods | privacy executor | Privacy owning paid-access truth |
| CL-06 Hiring | CL-08 | candidate/job location safe projection and privacy targets | Hiring/Candidate owners | owner facts + executor | Location/Privacy owning hiring lifecycles |
| CL-07 Messaging | CL-08 | messages/threads subject inventory and execution | Messaging | privacy executor | Privacy direct message deletion |
| CL-07 Notification | CL-08 | privacy status notification delivery; notification data execution | Notification | `requestNotification`, privacy executor | direct channel provider calls |
| CL-09 Admin Holds | CL-08 | reusable stop-sign facts where applicable | Hold Module | `evaluateComplianceHold` | local CL-08 blocked flags |
| CL-09 Audit | CL-08 | generic and sensitive-access proof | Audit | `appendAuditEvent`, `recordSensitiveAccess` | LocationReveal/PrivacyRequest replaced by audit |
| CL-09 Observability | CL-08 | queue/integration failure visibility | Ops | canonical ops interfaces | IntegrationFailure replacing domain failure |
| CL-08 Privacy | CL-08 Location | approved location-data privacy instruction | Privacy request truth; Location executes own data | `executePrivacyInstruction` | Privacy directly deleting Location tables |

The Cluster Registry's explicit CL-08 → CL-01 bridge for CustomerProfile and Track data is binding: Privacy owns request/job/target lifecycle; Customer and Track execute or preserve according to retention rules.

---

## 14. Authentication and Authorization

### Authenticated actor

Every public privacy or location command begins with `resolveAuthenticatedActor`.

Anonymous public discovery may call only interfaces that return public-safe projections and must never be able to select exact precision.

### Authorization

`authorizeResourceAction` owns permission interpretation.

CL-08 supplies contextual facts:

- requester owns the privacy request;
- support/admin role scope for privacy review;
- viewer relationship to Booking/Order;
- target ownership/context for reveal history;
- source record relationship facts supplied by their owning Modules.

### Sensitive/admin actions

At minimum, the following are sensitive:

- viewing another user's privacy request;
- issuing or downloading a privacy export;
- overriding/rejecting/cancelling privacy work administratively;
- viewing reveal history;
- revealing exact location;
- accessing retained-target notes containing personal or legal context.

`recordSensitiveAccess` is required when the canonical audit policy classifies the action as sensitive.

### Step-up

`requireStepUpForSensitiveAction` exists as the canonical platform mechanism. The evidence does **not** establish that all privacy exports or location reveals require step-up. Do not invent that policy. If root security architecture later requires step-up for these actions, CL-08 consumes the canonical Identity capability.

---

## 15. Compliance and Readiness Composition

### Privacy rights

Privacy / Data Erasure owns the formal request and proof records. Legal deadline, jurisdiction, verification, rejection, and retention policies are legal-gated where not explicitly established.

### Retention exemptions

A `DataRetentionExemption` is Privacy-owned proof. It must be based on authoritative facts supplied by the owner of the retained record.

Examples:

- Transaction / Order → contract/signature facts;
- Payment / Payout / Tax → tax/payment/fraud facts;
- Review / Dispute → dispute facts;
- Audit / Event Ledger → security/audit retention facts;
- Consent & Disclosure → consent-proof retention;
- Track Subscription & Entitlement → subscription billing retention.

Privacy must not hardcode those owners' substantive rules.

### ComplianceHold

CL-08 consumes `ComplianceHold` only where the requested action's policy says a hold applies. It never creates a competing local blocked state.

A hold must not be assumed to override a statutory privacy right. That legal interaction is unresolved and requires policy approval.

### Consent

Consent evidence may itself be exportable or retention-exempt. Consent does not grant permission to reveal exact location and does not replace privacy identity verification.

### Entitlements

Entitlement state is privacy-target data and may affect unrelated product capabilities. CL-08 does not own plan/entitlement policy.

### Location safety

Location Safety composes:

- actor authority;
- source owner participant facts;
- Booking/Order transaction facts;
- relevant holds if policy requires;
- Location Safety precision/reveal policy.

Only Location Safety returns the exact-reveal decision.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Transactional outbox

Cross-Module events must use `publishDomainEvent` after the owning source-of-truth transaction commits.

Potential event families are architectural contracts only when explicitly versioned and approved. No `PrivacyRequestEvent` or `LocationRevealEvent` table currently exists.

Recommended event families:

```text
privacy.request.submitted
privacy.request.verified
privacy.erasure_job.queued
privacy.target.resolved
privacy.export.ready
privacy.request.completed

location.public_projection.updated
location.public_projection.invalidated
location.reveal.eligible
location.revealed
location.reveal.revoked
```

These names are **Proposed Ruling PR-08-03** and must be registered in the root event contract before use.

### Jobs

CL-08 uses canonical `enqueueReliableJob` for:

- privacy target discovery;
- per-owner target execution;
- retries;
- privacy aggregation;
- export generation;
- export expiry cleanup;
- stalled/deadline review;
- fuzzy projection refresh/expiry;
- location gate-change reconciliation.

`DataErasureJob` is business truth. `QueueJob` is operational execution truth.

### Idempotency

Every retryable command and worker must define semantic idempotency identity.

Examples:

- privacy target: `privacyRequestId + targetType + targetId/externalRef + action + executorVersion`;
- export generation: `privacyRequestId + exportFormat/version`;
- fuzzy projection refresh: `targetType + targetId + sourceVersion + policyVersion`;
- reveal/revoke: viewer + context + requested operation + source/gate version.

The exact reveal uniqueness/current-row model remains unresolved.

### Retry and dead-letter

Transient failures use bounded retry/backoff. Permanent, unsafe, or legal/manual-review failures go to terminal domain state or a review path, not infinite retry.

### Concurrency

Use aggregate locks or optimistic concurrency for:

- PrivacyRequest status;
- DataErasureJob aggregation;
- individual DataErasureTarget execution;
- export generation;
- fuzzy projection replacement;
- LocationReveal state.

No in-memory mutex may be relied upon for correctness.

---

## 17. Provider Integrations

### Privacy provider rule

Privacy does not own external provider adapters merely because it requests erasure.

Flow:

```text
Privacy instruction
→ provider-owning Module
→ provider-neutral port
→ provider adapter
→ external provider
→ verified/normalized result
→ owner-local state
→ typed privacy disposition returned to Privacy
```

Examples:

- R2 → Media / File Access
- Typesense → Search / Public Visibility
- Daily/Mux/Agora → Video Session
- Stripe payment references → Payment / Payout / Tax
- subscription billing references → Track Subscription & Entitlement
- Cronofy/calendar → Booking & Calendar

Provider-event dedupe truth remains with each provider owner.

### Geocoding

Canonical Shared Operations lists `geocodeAddress` with **Location Safety adapter ownership proposed**.

Provider is intentionally undecided.

Flow:

```text
Location Safety
→ GeocodingPort
→ selected geocoder adapter
→ provider
→ normalized coordinates/confidence
→ Location Safety precision/fuzzing policy
→ FuzzyLocationCache
```

Provider response is input/evidence, not Workin Ants truth.

### Reconciliation

Provider-owning Modules use `reconcileProviderState` for missed or inconsistent provider state. Privacy consumes the typed result; it does not run a generic provider sweeper.

### Operational failures

Provider failures produce safe `IntegrationFailure` records and structured logs. The relevant CL-08 record must also remain nonterminal/failed according to its own lifecycle.

---

## 18. Search / Projection Boundaries

### Public location projection

`FuzzyLocationCache` is the Location Safety-owned safe projection source.

Search:

- consumes safe fuzzy coordinates/radius/precision;
- never calls a fuzzing helper itself;
- never reads exact private address/coordinates to derive a public value;
- never treats provider search coordinates as source truth.

### Privacy de-indexing

Privacy requests projection removal through `requestSearchProjectionRefresh`.

Search owns:

- `SearchUpsertEvent`;
- Typesense adapter;
- indexing/de-indexing;
- reconciliation;
- provider document schema.

Privacy owns why a request requires removal; Search owns how the projection is removed.

### Re-index triggers

At minimum:

- source location changed;
- fuzzy projection refreshed;
- fuzzy projection invalidated;
- privacy erasure/restriction requires removal;
- source visibility/moderation/readiness changes routed through source owner.

---

## 19. Media / File Boundaries

### Privacy export

- `DataExportBundle` is Privacy truth.
- export bytes live in Media-managed private storage.
- `mediaAssetId` points to the Media asset used for the bundle.
- `issueSignedMediaUrl` provides short-lived access after Privacy authorization.
- export access is sensitive and must be audited.

**Proposed Ruling PR-08-04 — DataExportBundle media relation**  
Add explicit referential integrity from `DataExportBundle.mediaAssetId` to `MediaAsset` or an equivalent approved Media reference contract. This does not transfer Media ownership.

### Erasure

Privacy instructs Media to:

- delete allowed objects and derivatives;
- remove/anonymize metadata;
- handle original filenames and object keys;
- preserve security/legal proof only when retention is required.

Privacy must not call R2 directly.

### Location metadata in files

EXIF/GPS scrubbing remains Media-owned. Location Safety may provide semantic sensitivity policy but must not implement file-processing pipelines.

---

## 20. Privacy / Retention

### Privacy target executor contract

Every personal-data-owning Module that participates in CL-08 must implement, as applicable:

1. `enumerateSubjectData`
2. `evaluateRetentionRequirement`
3. `executePrivacyInstruction`
4. export serialization
5. idempotent result proof
6. provider deletion through its own adapter
7. safe failure/retry classification

### Location Safety as a privacy executor

Location Safety must enumerate and disposition its own:

- `FuzzyLocationCache` rows tied to the subject or subject-owned targets;
- `LocationReveal` rows containing viewer/subject/context personal data.

Current `DataErasureTargetType` has no explicit location target values.

**Proposed Ruling PR-08-05 — explicit Location Safety privacy targets**  
Add explicit target types for Location Safety records rather than using `other`, for example conceptually `location_fuzzy_projection` and `location_reveal_record`. Final enum names require schema approval before migration.

### Retention

`LocationReveal` may itself require a safety/security/legal retention period while containing personal data. That policy is unresolved. Privacy may not delete it unconditionally.

### User row

Hard deletion versus permanent anonymized account shell is unresolved. Until resolved, implementation must not cascade-hard-delete `User` as a privacy shortcut.

### Backups

Delayed backup expiry/removal must not be represented as immediate erasure without an approved operational/legal policy.

---

## 21. Audit and Observability

### Audit

Audit / Event Ledger owns generic proof.

Relevant actions include:

- `privacy_export_generated`
- `privacy_erasure_started`
- `privacy_erasure_completed`
- `location_revealed`

Use:

- `appendAuditEvent` for important lifecycle/action proof;
- `recordSensitiveAccess` for protected access/issuance/download/reveal proof.

Audit metadata must use identifiers, reason codes, outcomes, and sanitized context. Do not store exact addresses, export contents, raw message bodies, raw resumes, tax details, provider secrets, or unnecessary personal data in audit metadata.

### Domain truth remains separate

- `PrivacyRequest` proves privacy workflow state.
- `DataErasureTarget` proves target disposition.
- `LocationReveal` proves reveal state.
- `AuditEvent`/`AccessAuditLog` prove that an action/access occurred.

None substitutes for another.

### Observability

Use:

- `createRequestContext`;
- `writeStructuredLog`;
- `sanitizeTelemetryMetadata`;
- `recordIntegrationFailure`;
- queue telemetry and incidents.

Correlation/request IDs must cross web request → job → owner executor → provider → result → audit.

Operational logs must redact:

- exact addresses and exact coordinates;
- private export contents;
- raw provider payloads containing personal data;
- IP addresses when only a hash is required;
- authentication/session material;
- signed URLs and storage secrets.

---

## 22. Security Boundaries

1. Validate all request payloads server-side.
2. Resolve actor and authorize on the server for every protected operation.
3. Never expose exact private location through a public projection or client-supplied precision switch.
4. Use canonical `encryptSensitiveValue` for reversible exact-location storage where required.
5. Use canonical `normalizeAndHashIdentifier` for non-plaintext request/IP evidence.
6. Do not log plaintext exact address/coordinates.
7. Do not put exact location in search documents.
8. Use short-lived signed access for privacy export files.
9. Recheck export status/expiry at access time.
10. Recheck reveal gates at disclosure time; cached UI eligibility is insufficient.
11. Use idempotency for request submission, target execution, export generation, fuzzy refresh, reveal, and revoke.
12. Use database concurrency controls for lifecycle writes.
13. Provider secrets live only in approved secret management and provider adapters.
14. Geocoding requests must minimize payload and use only the scope needed for location resolution.
15. Rate limits for privacy request abuse, export access, and reveal attempts must use the root platform rate-limit mechanism once its policy is defined; do not create a CL-08-only limiter.
16. Telemetry and analytics must not contain exact location or exported personal-data payloads.
17. Cross-Module target references must be validated through the target owner.
18. Admin/support access is not blanket permission to view export contents or exact location.

---

## 23. Testing Architecture

### Module unit tests

Privacy:

- request-type/status policies;
- target registration;
- retention-exemption rules;
- aggregate outcome logic;
- export expiry;
- target result mapping.

Location:

- precision classification;
- coordinate fuzzing;
- public payload minimization;
- reveal transition policy;
- revocation;
- cache freshness.

### Public-interface contract tests

- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- `applyFuzzyPublicLocation`
- `resolveLocationReveal`
- owner fact DTOs from Booking/Order
- Media/Search/Audit interfaces

### Lifecycle tests

- legal/illegal PrivacyRequest transitions once approved;
- DataErasureJob and target transitions;
- DataExportBundle transitions;
- LocationReveal transitions and timestamp consistency.

### Integration tests

- Privacy → Media deletion/export;
- Privacy → Search de-index;
- Privacy → Customer/Track executors;
- Privacy → Messaging/Video/Payment executors;
- Location → Booking/Order gate facts;
- Location → Search projection;
- Location → Audit proof;
- Privacy → Location executor.

### Idempotency and concurrency

- duplicate privacy submission;
- duplicate target job;
- duplicate provider result;
- concurrent target retries;
- duplicate export generation;
- concurrent fuzzy refresh;
- simultaneous reveal/revoke;
- stale Booking/Order gate facts.

### Provider tests

- geocoder adapter normalization, timeout, retry, bad/unknown output;
- owner provider deletion results through the privacy protocol;
- no provider payload becomes CL-08 domain state directly.

### Compliance/privacy tests

- retained target has exemption;
- erased target does not leave public projection;
- export omits nonexportable secrets and honors owner serializer;
- exact location never appears in public search;
- audit/telemetry payloads are redacted;
- admin access follows explicit authority;
- no local premium/hold/privacy booleans.

### Critical E2E workflows

1. User submits privacy request and sees status.
2. Verified erasure request executes against multiple owner Modules with one retained target and one deleted target.
3. Export becomes ready, is downloaded through short-lived Media access, and later expires.
4. Public source location appears only as fuzzy projection.
5. Authorized participant obtains exact location only after gate; another actor is denied.
6. Revocation stops subsequent exact-location access.
7. Privacy erasure of location records removes public projection and preserves only approved retained proof.

Decision-gated E2E tests must not be enabled until the associated architecture decision is approved.

---

## 24. Invariants

### Rules coding agents must never violate

1. A Cluster does not own either Module's lifecycle.
2. Only Privacy / Data Erasure changes `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, or `DataExportBundle` lifecycle truth.
3. Only Location Safety owns `FuzzyLocationCache`, `LocationReveal`, and location precision/reveal policy.
4. A feature Module may execute a privacy instruction against its own records; it may not create a parallel privacy-request workflow.
5. Privacy must not directly mutate another Module's source records as the default integration pattern.
6. Privacy must not own provider SDKs merely because erasure touches provider resources.
7. A lawfully retained target requires documented Privacy-owned retention-exemption proof based on owner-supplied facts.
8. Product deletion, `deletedAt`, or `erasedAt` on one record does not prove a PrivacyRequest is complete.
9. `QueueJob` does not replace `DataErasureJob`.
10. `AuditEvent` or `AccessAuditLog` does not replace privacy or location domain truth.
11. `IntegrationFailure` does not replace business failure state.
12. Search is a projection and never owns privacy or exact-location truth.
13. Search must never calculate its own fuzzy coordinates from exact private coordinates.
14. Public search/map payloads must never include exact private coordinates by default.
15. `FuzzyLocationCache` is not exact-location truth.
16. `LocationReveal` is not `AccessAuditLog`.
17. Booking and Order remain their own lifecycle owners even when their facts are reveal inputs.
18. Booking's duplicate location fields may not become a second reveal lifecycle owner.
19. Exact location is returned only after a fresh server-side Location Safety decision.
20. Revoked/no-longer-eligible reveal state must prevent subsequent exact-location return.
21. A map/geocoder provider is never Workin Ants location truth.
22. Generic encryption, hashing, queueing, retries, idempotency, and locking must use approved canonical mechanisms.
23. Exact addresses, exact coordinates, export contents, signed URLs, and provider secrets must not leak into telemetry.
24. Media owns file/object mechanics and EXIF/GPS processing.
25. Search owns `SearchUpsertEvent` and Typesense mechanics.
26. Audit owns `AuditEvent` and `AccessAuditLog`.
27. Notification owns channel routing/delivery.
28. ComplianceHold is the reusable platform stop sign; CL-08 must not invent local blocked flags.
29. Track entitlements remain commercial policy truth and do not replace privacy/reveal authority.
30. No unresolved legal or architectural policy may be filled in by a coding agent for convenience.

---

## 25. Prohibited Duplicate Implementations

Do not create:

- `deleteUserService` or `gdprService` in Identity;
- PrivacyRequest tables/workflows in Consent, Messaging, Media, Customer, Track, Payment, Transaction, Video, or Location;
- direct R2 deletion clients in Privacy;
- direct Typesense deletion/index clients in Privacy or Location;
- direct Stripe/Cronofy/Daily/Mux/Agora deletion clients in Privacy;
- `LocationAccessLog` or `AddressRevealAudit` as substitutes for `AccessAuditLog`;
- Search-side `randomizeCoordinates`, `fuzzLocation`, or `geoMask` helpers;
- Booking-owned or Order-owned exact-reveal policy service;
- a second exact-location reveal table;
- a generic `isLocationRevealed` boolean as source truth;
- `privacyBlocked`, `revealBlocked`, or local compliance-stop booleans;
- Module-specific AES/HMAC helpers;
- Module-specific queue/retry/idempotency frameworks;
- permanent public URL handling for privacy export artifacts;
- a generic cross-domain Prisma repository that scans/rewrites all personal data;
- a universal target deletion function that bypasses owner interfaces;
- a generic temporary-access record that replaces `LocationReveal`;
- a generic audit record that replaces `DataErasureTarget`;
- direct use of `Booking.locationRevealStatus` as authoritative reveal truth.

---

## 26. Deferred / Unresolved Decisions

| ID | Question | Why unresolved | Missing evidence / approval | Blocks |
|---|---|---|---|---|
| U-08-01 | What durable identity-verification proof is linked to a `PrivacyRequest`? | `verifiedAt` exists, but no method/reference record is modeled. | Identity + Privacy contract and schema ruling. | Transition to `verified`; production fulfillment. |
| U-08-02 | What distinguishes privacy `access` from `export`? | Both are declared request types; output semantics are not defined. | Privacy/legal product policy. | Access-request fulfillment UI/contract. |
| U-08-03 | How are correction and restriction proven per target? | `DataErasureTargetStatus` lacks corrected/restricted outcomes. | Privacy schema/proof-model ruling. | Correction/restriction completion. |
| U-08-04 | Do lawfully retained targets produce `completed` or `partially_completed`? | Aggregate semantics are not defined. | Privacy/legal policy. | Final aggregation for mixed outcomes. |
| U-08-05 | When may a request be cancelled or rejected, and by whom? | Statuses exist without policy. | Legal/admin authority policy. | Cancellation/rejection commands. |
| U-08-06 | What jurisdiction/policy version/deadline rules populate `dueAt`? | Schema has `dueAt`, but legal policy source is absent. | Legal review and policy versioning. | Automated statutory deadline logic. |
| U-08-07 | Can multiple active/conflicting privacy requests exist per User? | No uniqueness/concurrency rule exists. | Privacy policy/schema ruling. | Active-request conflict handling. |
| U-08-08 | Is the User eventually hard-deleted or retained as anonymized shell? | Identity row contains many relationships and privacy markers. | Identity/Privacy/legal ruling. | Final account disposition. |
| U-08-09 | How is backup expiry/removal represented? | Immediate application erasure is not the same as backup purge. | Ops/legal retention policy. | Backup completion wording and final proof. |
| U-08-10 | What is the canonical exact-location owner outside Booking? | No dedicated exact-location model exists for other source types. | Source-module location contracts. | Exact reveal for non-Booking targets. |
| U-08-11 | What is the semantic status of `Booking.exactAddressEncrypted`, `Booking.fuzzyLat/fuzzyLng`, and `Booking.locationRevealStatus`? | Physical schema duplicates Location Safety-owned concepts. | Booking + Location schema reconciliation. | Production reveal migration/synchronization. |
| U-08-12 | Must `LocationReveal` require Booking, Order, or exactly one of them? | Both foreign-key-shaped fields are nullable and not relationally enforced. | Reveal context model ruling. | Reveal persistence constraints. |
| U-08-13 | What exact predicate permits reveal? | Paid/confirmed/agreement/hold/dispute/participant/time-window rules are not settled. | Booking/Order/Location safety policy. | Exact reveal. |
| U-08-14 | Who may see whose exact location? | Viewer directionality is not defined. | Product/safety policy. | Exact reveal. |
| U-08-15 | What events revoke reveal? | Cancellation/refund/dispute/reschedule/location change/hold/time may differ. | Product/safety policy. | Revocation automation. |
| U-08-16 | Must audit proof commit successfully before exact data is returned? | Availability vs proof requirement is undecided. | Security/compliance policy. | Exact reveal transaction boundary. |
| U-08-17 | What are fuzzy radius, stability, expiry, regeneration, and algorithm-version rules by target type? | Cache fields exist but policy does not. | Location Safety policy. | Production fuzzy projection policy. |
| U-08-18 | What controlled target vocabulary validates `FuzzyLocationCache.targetType`? | Field is unrestricted String. | Location target registry/enum ruling. | Broad multi-source location support. |
| U-08-19 | What uniqueness/current-state model prevents conflicting `LocationReveal` rows? | No unique constraint or append-only event model is established. | Location schema ruling. | Concurrency-safe exact reveal. |
| U-08-20 | Which geocoder is selected and what KMS/key-management implementation backs shared encryption? | Provider/implementation selection is deferred. | Root integration/security choice. | Production provider calls; not port/contract tests. |
| U-08-21 | How long are `LocationReveal`, request metadata, and fuzzy caches retained under privacy erasure? | Safety proof may need retention while records contain personal data. | Privacy/Location/legal retention matrix. | Location privacy executor final policy. |
| U-08-22 | How will `DataExportBundle.mediaAssetId` be relationally enforced and what manifest/encryption metadata is required? | Logical reference exists without relation/proof fields. | Privacy + Media schema ruling. | Production export artifact hardening. |
| U-08-23 | Add explicit Location Safety target values to `DataErasureTargetType`? | Current enum cannot identify location records except `other`. | Approval of PR-08-05 and schema migration. | First-class Location privacy target execution. |

### Work that is not blocked by unresolved decisions

Coding agents may build:

- typed public contracts;
- request submission/status reads that stop before unapproved verification/fulfillment transitions;
- owner executor protocol and contract tests;
- shared-operation integration;
- disabled/stubbed provider adapters;
- observability/redaction;
- nonproduction policy fixtures;
- migrations already directly established by the current Prisma schema.

They may not invent production legal/safety values to make tests green.

---

## 27. Architecture Decision Summary

### Binding rulings

1. CL-08 coordinates; it owns no lifecycle.
2. Privacy / Data Erasure owns `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, `DataExportBundle`, aggregate outcome, and cross-service fulfillment.
3. Data-owning Modules enumerate, retain, export, erase, anonymize, correct, restrict, and delete provider resources through their own interfaces.
4. Privacy does not own external provider deletion adapters.
5. Location Safety owns `FuzzyLocationCache`, `LocationReveal`, `LocationPrecision`, `LocationRevealStatus`, coordinate-fuzzing policy, and exact-reveal policy.
6. Booking and Order supply gate facts but do not own exact-reveal truth.
7. Search receives only Location Safety-approved public location and owns index mechanics.
8. Media owns storage/file mechanics; Privacy owns export-bundle lifecycle.
9. Audit and observability remain separate from domain truth.
10. Canonical shared operations are mandatory anti-duplication boundaries.
11. The compliance-inventory ownership row that associates exact-reveal ownership with Booking is treated as supporting evidence only; stronger ownership evidence keeps Location Safety as owner.
12. Privacy retention exemptions are Privacy-owned records based on source-owner facts.

### Proposed rulings awaiting approval

- PR-08-01: Identity-owned `User` erasure markers are projections of Privacy result.
- PR-08-02: Booking duplicate precision/fuzzy/reveal fields are non-authoritative snapshots/compatibility fields pending schema reconciliation.
- PR-08-03: proposed CL-08 domain event family.
- PR-08-04: explicit `DataExportBundle` → Media reference integrity.
- PR-08-05: explicit Location Safety privacy target types.

No implementation may treat a Proposed Ruling as approved merely because it appears here.

---

## 28. Coding-Agent Usage

Before changing CL-08, an implementation agent must read, in order:

1. Root `project-overview.md`
2. Root `architecture.md`
3. Root `code-standards.md`
4. Canonical Shared Operations Registry
5. This Cluster `architecture.md`
6. This Cluster `build-plan.md`
7. Target Module architecture
8. Target Module implementation plan
9. Relevant dependency Module public-interface sections
10. Current progress tracker

For exact-location work, also read Booking & Calendar, Transaction / Order, Role / Authority, Audit / Event Ledger, Search / Public Visibility, and shared crypto interfaces.

For privacy fulfillment, also read every source Module whose records are in the requested executor set plus Media, Search, Audit, Observability, Identity, Customer / Buyer Profile, and Track Subscription & Entitlement.

If a required dependency interface or one of U-08-01 through U-08-23 remains unresolved, stop at that boundary and record the blocker. Do not replace missing architecture with a direct database read, local boolean, provider SDK call, or guessed legal rule.
