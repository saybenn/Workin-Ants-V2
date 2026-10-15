# Privacy & Location Safety Architecture

> **Repository location:** `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`<br>
> **Cluster ID:** CL-08  
> **Cluster name:** Privacy & Location Safety  
> **Cluster type:** `privacy_compliance_safety_control`  
> **Document status:** Implementation-grade cluster architecture with explicit decision gates  
> **Audience:** Coding agents, developers, reviewers, maintainers, compliance reviewers, and future architecture agents  
> **Update rule:** Update this file whenever a binding CL-08 architectural decision changes. Build progress must not redefine this architecture.

**Shared Operation status:** References use permanent IDs and canonical names from `context/shared/shared-operations.md`; that registry controls owner, classification, status, and reusable boundary. SH-003 queryOwnerFacts remains **Proposed ruling** and is not an unconditional prerequisite or an approved universal DTO/API. Adoption requires separate Shared Operations approval before API/schema commitment. Existing source-owner-specific public queries may be consumed within their approved contracts; direct cross-domain Prisma/repository reads remain prohibited. SH-069 geocodeAddress remains **Proposed ruling** wherever referenced; this pass does not approve it.

### Current context paths and missing artifact roles

Read `context/context-map.md` first for authority by concern, then the existing artifacts relevant to the feature:

- Overview: `context/project-overview-v3.md`.
- Shared Operations: `context/shared/shared-operations.md`.
- Cluster architecture: `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`.
- Cluster build plan: `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`.
- Member Module pairs: use the Privacy / Data Erasure and Location Safety paths in `context/context-map.md`.

Root/repository-root and context-root `architecture.md`, `build-plan.md`, `code-standards.md`, and dedicated `progress-tracker.md` are currently **missing**. References to those global artifacts below describe future roles, not loadable files or current authority. Do not create local substitutes or infer global approval. Apply existing concern owners through the context map; stop work that needs a missing global decision. Until a dedicated tracker is available, report progress/blockers in the task completion report; progress does not approve architecture.

---

## 1. Document Status and Scope

CL-08 coordinates two Deep Modules:

- `privacy_data_erasure` — Privacy / Data Erasure Module
- `location_safety` — Location Safety Module

This Cluster is a planning, integration, and controlled-context boundary. It is **not** a source-of-truth owner and does not take ownership of either Module's lifecycle.

Once reconciled and finalized, the currently missing root Workin Ants architecture will be authoritative for platform-wide rules such as actor identity, authorization, consent proof, entitlements, compliance holds, search projection, media/file mechanics, audit, observability, provider boundaries, and shared operations. This document narrows those rules to the privacy and location-safety workflows.

Module architectures remain authoritative for Module-local truth. Where this Cluster document introduces a required decision that is not yet established by stronger evidence, it is labeled **Proposed Ruling**. Proposed Rulings are not silently binding until approved. Items that still lack sufficient evidence are recorded in **Deferred / Unresolved Decisions** and must not be invented during implementation.

### Source reconciliation notes

The following source relationships are material to CL-08:

1. The Deep Module Registry, Location Safety extract, glossary definition of Exact Location Reveal, and Canonical Shared Operations place exact-location reveal policy and `LocationReveal` truth with Location Safety. Booking & Calendar also participates in the fuzzy-geolocation/exact-reveal compliance control by supplying supporting Booking/gate proof. This is compatible participation, not competing lifecycle ownership; preserve the supporting compliance mapping.
2. Privacy / Data Erasure declares GDPR/CCPA rights and contract-retention exemptions as compliance responsibilities. The Deep Module Registry now represents both in `complianceMet` and `complianceSatisfied`, with `DataRetentionExemption` as the contract-retention proof record. This is mechanical synchronization of existing Privacy ownership; retention policy remains decision-gated.

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
   ├─ resolveAuthenticatedActor # SH-001 resolveAuthenticatedActor
   ├─ validate input
   └─ authorizeResourceAction # SH-002 authorizeResourceAction
          │
          ▼
Privacy / Data Erasure application service
   │
   ├─ PrivacyRequest truth
   ├─ identity-verification orchestration
   ├─ enumerateSubjectData protocol # SH-096 enumerateSubjectData
   ├─ evaluateRetentionRequirement protocol # SH-097 evaluateRetentionRequirement
   ├─ DataErasureJob / DataErasureTarget truth
   └─ orchestratePrivacyFulfillment # SH-099 orchestratePrivacyFulfillment
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
   → enqueueReliableJob # SH-047 enqueueReliableJob
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
   ├─ resolveAuthenticatedActor # SH-001 resolveAuthenticatedActor
   ├─ authorizeResourceAction # SH-002 authorizeResourceAction
   └─ queryOwnerFacts from Booking / Order / source owner # SH-003 queryOwnerFacts (Proposed ruling; adoption gated)
          │
          ▼
Location Safety application service
   │
   ├─ classify precision
   ├─ applyFuzzyPublicLocation # SH-028 applyFuzzyPublicLocation
   ├─ resolveLocationReveal # SH-027 resolveLocationReveal
   └─ write LocationReveal / FuzzyLocationCache truth
          │
          ├─────────────► encryptSensitiveValue / normalizeAndHashIdentifier # SH-075 encryptSensitiveValue; SH-076 normalizeAndHashIdentifier
          ├─────────────► recordSensitiveAccess # SH-030 recordSensitiveAccess
          └─────────────► requestSearchProjectionRefresh # SH-091 requestSearchProjectionRefresh
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
└── clusters/
    └── Privacy & Location Safety/
        ├── privacy-location-safety-architecture.md
        └── privacy-location-safety-build-plan.md

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

The source Module performs the underlying action. Privacy records the authoritative target disposition returned through `SH-095 executePrivacyInstruction`.

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
| `SH-099 orchestratePrivacyFulfillment` | Privacy | Privacy worker only | Drive verification, inventory, retention, execution, aggregation, export, completion. | request ID, correlation context | aggregate outcome | truth/workflow result | owner record semantics |
| `SH-096 enumerateSubjectData` | each data owner through Privacy-defined contract | Privacy | Enumerate owner-held subject data and supported dispositions. | subject, request type, cursor | stable target descriptors, sensitivity, supported actions | owner evidence | permission to mutate |
| `SH-097 evaluateRetentionRequirement` | data owner supplies facts; Privacy records exemption | Privacy | Determine mandatory retention facts. | target descriptor, request context | required?, reason, basis, retainUntil, minimum fields, permitted anonymization | evidence/decision input | final privacy-request outcome |
| `SH-095 executePrivacyInstruction` | each data owner | Privacy | Apply owner-local erase/anonymize/export/restrict/etc. | target, requested action, request ID, idempotency key | typed disposition/result/evidence | owner result | privacy request completion |
| `SH-100 createPrivacyExportArtifact` | Privacy with Media mechanics | requester via Privacy | Assemble and stage export. | request, owner export sections | `DataExportBundle` + Media reference | truth + artifact reference | permanent file entitlement |

### Location Safety interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer |
|---|---|---|---|---|---|---|---|
| `SH-028 applyFuzzyPublicLocation` | Location Safety | Search; Marketplace; Gig; Hiring; map/public surfaces | Return approved approximate location. | target identity, owner-provided source version/location input or existing cache | fuzzy coordinates/area, radius, precision, expiry/source version | projection | exact coordinates |
| `getPublicLocationProjection` | Location Safety | Search/public consumers | Read current safe projection. | target type, target ID | safe projection + freshness | projection | source location |
| `SH-027 resolveLocationReveal` | Location Safety | Booking, Order, protected UI | Decide whether exact private location may be shown. | actor/viewer, Booking/Order context, owner gate facts, purpose | allow/deny, permitted precision, reason codes, reveal ID/state, expiry/revocation context | decision + domain proof | authorization from paid/provider state alone |
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

Common temporary reveal mechanics consume `SH-088 manageTemporaryAccessGrant`; revocation mechanics consume `SH-089 revokeTemporaryAccessGrant`. Location Safety supplies the approved policy and performs its own transitions/evidence. `LocationReveal` remains separate from `MediaAccessGrant` and all other grant truth; unresolved reveal/revocation policies remain gated.

The canonical registry supplies permanent SH IDs. Only operations consumed here are listed; Proposed references remain adoption-gated.

| Canonical operation | Plain-English meaning | Canonical owner | CL-08 consumers | Reusable mechanism | Local policy that remains local | Invocation point | Must not be duplicated |
|---|---|---|---|---|---|---|---|
| `SH-001 resolveAuthenticatedActor` | Resolve trusted actor context. | Identity & Access | both Modules | request/session actor resolution | privacy requester/reveal viewer intent | every protected entry point | feature-local current-user helpers |
| `SH-002 authorizeResourceAction` | Decide platform/org/participant/ownership permission. | Role / Authority | both Modules | typed authorization decision | privacy owner/admin scope; location contextual safety | before protected queries/mutations | `privacyAuth.ts`, `locationPermission.ts` policy engines |
| `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` | Read minimum owner facts through owner DTO. | Each source Module | both | shared contract, separate implementation | exact facts needed by Privacy/Location | before retention/reveal decisions | cross-domain repositories |
| `SH-011 evaluateComplianceHold` | Return active reusable stop signs. | Admin Review / Compliance Hold | Location Safety; Privacy where legally applicable | hold query | whether a hold is relevant to the requested action | before action if policy says hold applies | local block flags |
| `SH-026 authorizeContextualResourceAccess` | Standard shape for context-specific access decisions. | Relevant context owner | Location Safety and export access | shared response contract | location/export business predicates | before issuing sensitive result | universal entitlement service |
| `SH-027 resolveLocationReveal` | Decide exact-location reveal and create LocationReveal proof. | Location Safety | Booking/Order/public protected UI | Module public interface | reveal predicate and lifecycle | exact-location request | Booking/Order reveal service |
| `SH-028 applyFuzzyPublicLocation` | Produce safe approximate public location. | Location Safety | Search/public source Modules | Module public interface | fuzzing/radius/stability policy | before public projection | Search-side coordinate fuzzing |
| `SH-029 appendAuditEvent` | Append generic important-action proof. | Audit / Event Ledger | both | insert-only audit command | event meaning and safe metadata | important lifecycle decisions | local audit tables |
| `SH-030 recordSensitiveAccess` | Append protected-data access proof. | Audit / Event Ledger | both | `AccessAuditLog` writer | exact sensitivity and context | export issuance/download, location reveal | `LocationAccessLog`, `PrivacyAccessLog` |
| `SH-041 requestNotification` | Deliver a canonical notification request. | Notification | Privacy | channel routing/delivery | message meaning, sensitivity, recipients from owner facts | status-ready/failure notices where approved | direct SES/SMS/push dispatch |
| `SH-044 executeIdempotentCommand` | Guarantee one business effect under retry. | Platform application infrastructure | both | idempotency claim/result | semantic key and conflict behavior | every retryable mutation | Module-local idempotency frameworks |
| `SH-046 publishDomainEvent` | Publish versioned event after source commit. | Platform event/outbox infrastructure | both | transactional outbox | event name/payload/emission policy | post-commit cross-Module effects | ad hoc fire-and-forget |
| `SH-045 deduplicateDomainEvent` | Prevent repeated consumer effect. | Platform event infrastructure; consumer owns inbox | both workers | transactional inbox | handler-specific side effect | event consumers | per-worker dedupe tables without shared mechanism |
| `SH-047 enqueueReliableJob` | Durable async work with retries/dead-letter. | Shared queue infrastructure | Privacy and Location workers | queue/lease/heartbeat | business payload and terminal meaning | slow or retryable work | Module-specific queue frameworks |
| `SH-049 orchestrateWorkflowSteps` | Run persisted multi-step orchestration. | Workflow-owning Module using shared runner | Privacy | workflow runner | privacy sequence and compensation/partial semantics | fulfillment | generic Privacy replacement workflow |
| `SH-050 reconcileWorkflowStatus` | Aggregate step outcomes into owner status. | Workflow owner using shared helper | Privacy | deterministic aggregation hook | privacy-specific complete/partial/fail meaning | after target results | QueueJob-derived business status |
| `SH-053 transitionLifecycleState` | Reuse state-machine plumbing. | Shared mechanism; lifecycle owner supplies policy | both | transition validation/update/event hook | privacy and reveal transition graphs | every lifecycle mutation | generic lifecycle policy table |
| `SH-051 acquireAggregateLock` / `SH-052 withOptimisticConcurrency` | Serialize conflicting writes or reject stale updates. | Shared persistence infrastructure | both | DB lock/CAS | lock key and conflict semantics | request/reveal/target updates | in-memory locks |
| `SH-055 runDeadlineExpiration` | Invoke owner-defined expiry behavior. | Shared scheduler/queue infrastructure | Privacy exports; fuzzy caches | cursor/schedule dispatch | expiry semantics | `expiresAt` handling | custom cron frameworks |
| `SH-069 geocodeAddress (Proposed ruling; adoption gated)` | Resolve protected address through provider-neutral adapter. | Location Safety adapter ownership approved by WA-R016; contract/provider gated | Location Safety | adapter contract | location privacy, retention, public-safety rules | before fuzzy projection if coordinates absent | map-provider calls in Search/Booking |
| `SH-070 deleteProviderResource` | Delete/revoke provider resource after authorized instruction. | Provider-owning Module | Privacy orchestration | shared provider result contract | provider-specific mapping/retention | owner executor | provider SDKs in Privacy |
| `SH-075 encryptSensitiveValue` | Managed reversible encryption. | Shared security/cryptography capability | Location Safety/source owner | envelope encryption | whether/when exact location may be decrypted | exact-location storage/read | local AES helpers |
| `SH-076 normalizeAndHashIdentifier` | Keyed non-plaintext evidence hash. | Shared security/cryptography capability | Location Safety, Privacy | HMAC/normalization | which metadata is necessary and retention | IP/request proof | `location-ip-hash.ts` |
| `SH-091 requestSearchProjectionRefresh` | Ask Search to index/update/hide/remove/restore. | Search / Public Visibility | both | Search command/queue | CL-08 reason and safe source version | privacy/fuzzy-location change | direct `SearchUpsertEvent` writes or Typesense calls |
| `SH-095 executePrivacyInstruction` | Execute one owner-local privacy disposition. | Privacy orchestrates; each data owner executes | Privacy + Location executor | typed protocol | owner-specific fields/retention | per target | local PrivacyRequest workflow |
| `SH-096 enumerateSubjectData` | Enumerate owner-held subject data. | Each data-owning Module through Privacy-defined interface | Privacy | typed protocol | owner schema mapping | scope discovery | global database crawler |
| `SH-097 evaluateRetentionRequirement` | Return owner-held mandatory retention facts. | Data owner supplies facts; Privacy records exemption | Privacy | typed protocol | tax/contract/fraud/etc. facts | before target execution | owner-local exemption tables |
| `SH-098 anonymizePersonalFields` | Shared field-level anonymization mechanism. | Shared primitive; record owner supplies mapping | owner executors | versioned anonymization mechanism | exact fields/invariants | retained/erasable target execution | global unscoped scrubber |
| `SH-099 orchestratePrivacyFulfillment` | Coordinate Privacy request end to end. | Privacy / Data Erasure | Privacy | owner-local orchestration over shared mechanisms | privacy workflow meaning | after verification | privacy workflows in feature Modules |
| `SH-100 createPrivacyExportArtifact` | Build encrypted/private temporary export artifact. | Privacy owns bundle; Media/storage owns object mechanics | Privacy | artifact assembly + Media mechanics | export contents/eligibility/expiry | export request | R2/signed-URL implementation in Privacy |
| `SH-127 requestMediaAccess` | Issue short-lived private Media URL after gates. | Media / File Access | Privacy exports | signed URL mechanics | Privacy export entitlement | export download | custom presigning in Privacy |
| `SH-123 validateOwnedTargetReference` | Validate a cross-Module target through its owner. | Target owner | both | owner-specific validation contract | target relationship/eligibility | target registration/reveal context | direct cross-Module existence checks |
| `SH-032 createRequestContext`, `SH-033 writeStructuredLog`, `SH-034 sanitizeTelemetryMetadata`, `SH-037 recordIntegrationFailure` | Correlate and observe execution safely. | Per-operation owner in the canonical registry | both | request IDs, structured logs, redaction, failure records | domain failure status and sensitive-field policy | all workflows | business state in logs |

---

## 12. Cross-Module Data Flows

### 12.1 Privacy request intake

Login/authentication, SH-001 resolveAuthenticatedActor, SH-014 requireStepUpForSensitiveAction, and account-recovery proof are not automatically sufficient Privacy identity verification. Identity owns assurance/proof mechanics; Privacy alone decides whether the approved proof permits its `verified` transition. U-08-01 remains unresolved; no proof shape, assurance level, expiry, or schema representation is approved here.

```text
User
→ Identity.resolveAuthenticatedActor # SH-001 resolveAuthenticatedActor
→ Role/Authority.authorizeResourceAction(self privacy request) # SH-002 authorizeResourceAction
→ Privacy.submitPrivacyRequest
→ Privacy writes PrivacyRequest(status=submitted)
→ Audit.appendAuditEvent # SH-029 appendAuditEvent
→ optional Notification.requestNotification # SH-041 requestNotification
```

Privacy alone owns the request state.

### 12.2 Privacy erasure fulfillment

SH-091 requestSearchProjectionRefresh acceptance or queue acknowledgement is not proof of completed Search deletion. A Privacy target whose required disposition includes Search removal remains non-successful until Search supplies completion evidence under the approved Privacy executor contract. Accepted/queued work may be recorded as pending operational progress. Location Safety may independently complete its own cache/projection-source mutation. The durable completion receipt, correlation, and acknowledgement representation remain unresolved; this rule does not define that contract.

```text
PrivacyRequest verified
→ Privacy starts processing
→ Privacy creates DataErasureJob
→ each owner.enumerateSubjectData # SH-096 enumerateSubjectData
→ Privacy registers DataErasureTarget rows
→ each owner.evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
→ if retention required:
     Privacy writes DataRetentionExemption
     → owner executes permitted anonymization
     → Privacy marks target retained/anonymized as contract dictates
  else:
     Privacy dispatches executePrivacyInstruction # SH-095 executePrivacyInstruction
     → owner mutates its own records/providers
     → owner returns typed result
     → Privacy updates DataErasureTarget
→ Privacy.reconcileWorkflowStatus # SH-050 reconcileWorkflowStatus
→ Privacy updates DataErasureJob
→ Privacy updates PrivacyRequest aggregate result
→ Audit records sanitized lifecycle proof
→ Search/Media/other downstream effects occur through owner interfaces
```

### 12.3 Privacy export

```text
verified export request
→ owner.enumerateSubjectData / owner export serializers # SH-096 enumerateSubjectData
→ Privacy assembles purpose-limited manifest
→ Privacy.createPrivacyExportArtifact # SH-100 createPrivacyExportArtifact
→ Media stores private artifact and returns MediaAsset reference
→ Privacy writes DataExportBundle(ready)
→ requester passes authorization
→ Media.requestMediaAccess # SH-127 requestMediaAccess
→ Audit.recordSensitiveAccess # SH-030 recordSensitiveAccess
→ expiry worker marks bundle expired and asks Media to remove object
```

### 12.4 Correction / restriction

```text
verified request
→ owner enumeration
→ owner executes correction/restriction through executePrivacyInstruction # SH-095 executePrivacyInstruction
→ owner returns target-level proof
→ Privacy aggregates request outcome
```

**Decision gate:** current `DataErasureTargetStatus` cannot represent corrected/restricted outcomes. Do not implement target-level completion semantics until the proof model is approved.

### 12.5 Fuzzy public location

```text
source owner location created/changed
→ source owner calls LocationSafety.applyFuzzyPublicLocation # SH-028 applyFuzzyPublicLocation
   or emits approved source-location event
→ Location Safety obtains protected source facts through owner interface
→ optional geocodeAddress adapter # SH-069 geocodeAddress (Proposed ruling; adoption gated)
→ Location Safety applies precision/fuzzing policy
→ write/replace FuzzyLocationCache
→ Location Safety requests Search projection refresh
→ Search builds/indexes only safe fuzzy payload
```

Search never receives exact coordinates unless an entirely separate protected interface explicitly requires them; public search must not.

### 12.6 Exact location reveal

```text
viewer requests exact location
→ resolveAuthenticatedActor # SH-001 resolveAuthenticatedActor
→ authorizeResourceAction # SH-002 authorizeResourceAction
→ Booking/Order owner facts
→ optional evaluateComplianceHold if policy applies # SH-011 evaluateComplianceHold
→ LocationSafety.resolveLocationReveal # SH-027 resolveLocationReveal
→ if denied: return safe denial; optionally audit denial
→ if allowed:
     obtain/decrypt exact source location through approved owner/crypto boundary
     → write LocationReveal proof
     → recordSensitiveAccess(location_revealed) # SH-030 recordSensitiveAccess
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
| CL-01 Identity & Access | CL-08 | actor and privacy identity-proof result | Identity | `SH-001 resolveAuthenticatedActor`; privacy verification interface | Privacy reading auth-provider internals |
| CL-01 Role / Authority | CL-08 | permission decision | Role / Authority | `SH-002 authorizeResourceAction` | local permission engine |
| CL-01 Customer / Buyer Profile | CL-08 | customer subject data and privacy execution | Customer | `SH-096 enumerateSubjectData`, `SH-095 executePrivacyInstruction` | Privacy mutating CustomerProfile directly |
| CL-01 Track Subscription & Entitlement | CL-08 | subscription/usage target data and retention facts | Track | privacy executor protocol | local premium/retention booleans in Privacy |
| CL-02 Search | CL-08 | projection refresh acknowledgement; public projection consumer | Search for index; Location for safe payload | `SH-091 requestSearchProjectionRefresh`, `SH-028 applyFuzzyPublicLocation` | Privacy/Location calling Typesense directly |
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
| CL-07 Notification | CL-08 | privacy status notification delivery; notification data execution | Notification | `SH-041 requestNotification`, privacy executor | direct channel provider calls |
| CL-09 Admin Holds | CL-08 | reusable stop-sign facts where applicable | Hold Module | `SH-011 evaluateComplianceHold` | local CL-08 blocked flags |
| CL-09 Audit | CL-08 | generic and sensitive-access proof | Audit | `SH-029 appendAuditEvent`, `SH-030 recordSensitiveAccess` | LocationReveal/PrivacyRequest replaced by audit |
| CL-09 Observability | CL-08 | queue/integration failure visibility | Ops | canonical ops interfaces | IntegrationFailure replacing domain failure |
| CL-08 Privacy | CL-08 Location | approved location-data privacy instruction | Privacy request truth; Location executes own data | `SH-095 executePrivacyInstruction` | Privacy directly deleting Location tables |

The Cluster Registry's explicit CL-08 → CL-01 bridge for CustomerProfile and Track data is binding: Privacy owns request/job/target lifecycle; Customer and Track execute or preserve according to retention rules.

---

## 14. Authentication and Authorization

### Authenticated actor

Every public privacy or location command begins with `SH-001 resolveAuthenticatedActor`.

Anonymous public discovery may call only interfaces that return public-safe projections and must never be able to select exact precision.

### Authorization

`SH-002 authorizeResourceAction` owns permission interpretation.

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

`SH-030 recordSensitiveAccess` is required when the canonical audit policy classifies the action as sensitive.

### Step-up

`SH-014 requireStepUpForSensitiveAction` exists as the canonical platform mechanism. The evidence does **not** establish that all privacy exports or location reveals require step-up. Do not invent that policy. If root security architecture later requires step-up for these actions, CL-08 consumes the canonical Identity capability.

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

Cross-Module events must use `SH-046 publishDomainEvent` after the owning source-of-truth transaction commits.

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

CL-08 uses canonical `SH-047 enqueueReliableJob` for:

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

Canonical Shared Operations lists `SH-069 geocodeAddress (Proposed ruling; adoption gated)` with **Location Safety adapter ownership approved by WA-R016; contract/provider gated**.

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

Provider-owning Modules use `SH-062 reconcileProviderState` for missed or inconsistent provider state. Privacy consumes the typed result; it does not run a generic provider sweeper.

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

Privacy requests projection removal through `SH-091 requestSearchProjectionRefresh`.

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
- `SH-127 requestMediaAccess` provides short-lived access after Privacy authorization.
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

1. `SH-096 enumerateSubjectData`
2. `SH-097 evaluateRetentionRequirement`
3. `SH-095 executePrivacyInstruction`
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

- `SH-029 appendAuditEvent` for important lifecycle/action proof;
- `SH-030 recordSensitiveAccess` for protected access/issuance/download/reveal proof.

Audit metadata must use identifiers, reason codes, outcomes, and sanitized context. Do not store exact addresses, export contents, raw message bodies, raw resumes, tax details, provider secrets, or unnecessary personal data in audit metadata.

### Domain truth remains separate

- `PrivacyRequest` proves privacy workflow state.
- `DataErasureTarget` proves target disposition.
- `LocationReveal` proves reveal state.
- `AuditEvent`/`AccessAuditLog` prove that an action/access occurred.

None substitutes for another.

### Observability

Use:

- `SH-032 createRequestContext`;
- `SH-033 writeStructuredLog`;
- `SH-034 sanitizeTelemetryMetadata`;
- `SH-037 recordIntegrationFailure`;
- `SH-036 emitMetric` for operational counters/timings;
- `SH-038 recordQueueTelemetry` for worker attempts, retries, and outcomes;
- incidents through Ops.

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
4. Use canonical `SH-075 encryptSensitiveValue` for reversible exact-location storage where required.
5. Use canonical `SH-076 normalizeAndHashIdentifier` for non-plaintext request/IP evidence.
6. Do not log plaintext exact address/coordinates.
7. Do not put exact location in search documents.
8. Use short-lived signed access for privacy export files.
9. Recheck export status/expiry at access time.
10. Recheck reveal gates at disclosure time; cached UI eligibility is insufficient.
11. Use idempotency for request submission, target execution, export generation, fuzzy refresh, reveal, and revoke.
12. Use database concurrency controls for lifecycle writes.
13. Provider secrets live only in approved secret management and provider adapters.
14. Geocoding requests use `SH-078 minimizeAndRedactProviderInput` with source-owner policy to minimize payload and restrict purpose to location resolution.
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

- `SH-096 enumerateSubjectData`
- `SH-097 evaluateRetentionRequirement`
- `SH-095 executePrivacyInstruction`
- `SH-028 applyFuzzyPublicLocation`
- `SH-027 resolveLocationReveal`
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
11. Booking's fuzzy/exact-location compliance participation supplies supporting proof. Location Safety alone owns fuzzy/exact-location policy and reveal truth; Booking must not independently implement reveal policy.
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

1. `context/project-overview-v3.md`
2. Root architecture is currently missing; stop at any required global decision gap
3. Root code standards are currently missing; do not invent replacement standards
4. Canonical Shared Operations Registry
5. This Cluster `architecture.md`
6. This Cluster `build-plan.md`
7. Target Module architecture
8. Target Module implementation plan
9. Relevant dependency Module public-interface sections
10. Dedicated progress tracker is currently missing; use the task completion report for progress/blockers

For exact-location work, also read Booking & Calendar, Transaction / Order, Role / Authority, Audit / Event Ledger, Search / Public Visibility, and shared crypto interfaces.

For privacy fulfillment, also read every source Module whose records are in the requested executor set plus Media, Search, Audit, Observability, Identity, Customer / Buyer Profile, and Track Subscription & Entitlement.

If a required dependency interface or one of U-08-01 through U-08-23 remains unresolved, stop at that boundary and record the blocker. Do not replace missing architecture with a direct database read, local boolean, provider SDK call, or guessed legal rule.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


## WA-R017 — Owner facts and decision contracts

**Applied architecture ruling (AI_RESOLVED), 2026-09-30.** The [WA-R017 contract](../../reconciliation/platform-architecture-rulings.md#wa-r017--owner-facts-and-decision-contracts) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

SH-003 is a family of small owner-specific queries, not a mandatory universal DTO. Each query takes authenticated caller/purpose and a typed owner resource reference, exposes only required authorized facts with an owner-issued source token, and distinguishes unavailable/stale from absence or denial. Consumers do not load foreign Prisma records. SH-015 remains a reusable result pattern, not a universal domain enum: carry a decision category, stable owner reason code, evidence/source token and evaluation time; payload variants remain owner-specific. Domain outcomes such as Job Compliance warning/review_required and Healthcare redacted/blocked retain their distinct meaning. An unavailable prerequisite never becomes allow. Exact wire names/runtime schemas are DEFERRED_IMPLEMENTATION_DETAIL inside these constraints and must be fixed in producer/consumer fixtures before parallel integration.

Adopt this interpretation for all references that formerly treated SH-003/015 proposal status as an unconditional blocker on owner-specific interfaces. Neither SH status is promoted. New generic repositories, universal authorization or generic business-policy dispatch are forbidden. Grouped owner-specific contracts do not become interchangeable because their envelopes look similar.


## WA-R020 — Privacy executor identity and truthful completion

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R020 contract](../../reconciliation/platform-architecture-rulings.md#wa-r020--privacy-executor-identity-and-truthful-completion) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Privacy persists an immutable target descriptor with request identity, owner Module ID, registered owner target kind, opaque source ID/version, permitted action and descriptor/executor schema version. Each owner validates its own reference and field map. Typed child targets may be enumerated separately or included in an explicit versioned parent executor contract listing all covered child kinds; arbitrary `other`, a crawler or assumed cascade never supplies coverage. Deduplicate by request+owner+target-kind+source-id+action+source-version; preserve a new generation when re-evaluation changes an instruction. This is Privacy dispatch metadata, not polymorphic Media ownership.

Persist per-target attempts and final owner receipts independently of queue telemetry. A receipt names target/instruction identity, source version observed, action/outcome, executor version, completion time, evidence reference and any owner retention basis. Correction/restriction are explicit outcomes, never mislabeled deletion. Search acceptance is pending until Search returns its actual required projection outcome; Media artifact readiness similarly requires actual finalize/readiness proof. Retention is complete only when Privacy accepts an evidence-backed lawful exemption, not merely because an owner requested one.

Aggregate completion means every required target has either verified execution or an accepted lawful disposition. Summaries/exports disclose retained or restricted categories and reasons safely; `completed` never means all data was erased. Outstanding/failed targets prevent completed. A lawful fully accounted exemption does not by itself mean technical partial failure. An incomplete export stays pending/retryable or failed; no silent serializer omission or ready download. Any future deliberate partial-export product must explicitly distinguish partial from complete. This chooses correctness over premature delivery.

One request may have multiple execution/artifact generations for retries or refreshes; generations are immutable, correlated and only the current authorized ready artifact is offered. Revoke superseded access. Per-subject conflicting mutations serialize and re-evaluate owner state; do not reject or erase a legal request merely because another exists. Statutory verification, deadlines, restriction entitlement, backup completion wording, retention schedules and final User disposition remain EXTERNAL_REQUIREMENT. Identity markers are projections of Privacy outcomes, not a second rights lifecycle. Exact target enums/schema fields are deferred implementation constrained by this protocol.

Acceptance: restart routing, duplicate targets, changed source version, missing child coverage, failed serializer, lawful exemption versus unproven retention, Search queue acknowledgment versus completion, stale bundle access and concurrent conflicting instructions. No blanket claim of complete privacy coverage is authorized until all owner target/field matrices are reviewed.


## WA-R023 — Sensitive disclosure and audit failure boundaries

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Require a durable sensitive-access audit acceptance before returning exact private location, protected file/playback/join credentials, resumes, healthcare-sensitive fields, tax/identity/Agreement evidence, or sensitive admin exports. If required proof cannot be durably recorded, withhold the protected response and return a retriable unavailable result; never return the secret and log later. Record safe allowed/denied/redacted/blocked/unavailable outcomes under Audit-owned vocabulary without importing Healthcare enums as generic authorization. Include service/system/provider actor attribution and request correlation, not nullable User alone. A denied request must still disclose no target-existence details; audit trouble never changes denial into access.

Privileged irreversible mutations require durable owner decision/history plus atomic audit-outbox intent before committing owner state. If that local durable write fails, roll back the mutation. Later Audit transport failure retries/reconciles; it does not roll back an already executed external financial/legal effect or erase domain evidence. Where a legal action specifically requires pre-action Audit acceptance, its owner contract adds that stricter gate; legal deadlines/recovery remain scoped requirements. Low-risk diagnostics are best effort and never recursively produce infinite failures.

Identity owns fresh action-bound assurance; Role still authorizes the action. Require step-up for security-factor/recovery changes, financial adjudication/movement, privileged permission changes, bulk sensitive evidence export and administrative override/release of protective controls. Existing sessions or admin roles do not substitute. Exact assurance methods/lifetimes and action registration are security implementation policy, with provider capability checked before activation. Ordinary read access is not automatically all step-up; owner-specific policy may require it. Privacy identity verification is a separate statutory proof requirement.

Tradeoff: protected access becomes dependent on durable audit availability; this is preferable to an unprovable sensitive disclosure. Acceptance: audit unavailable before response, durable intent failure before mutation, outbox delivery outage after commit, privileged service actor, retry without duplicate effect, denied-target anti-enumeration and redaction-safe evidence. These rules amend failure/assurance portions only; per-owner legal retention and complete target/action matrices remain separate work.

Duplicate-collapse scope: CL01-HU-006/007/008/012 security portions; CL02-D025/044/056; CL04-U032; CL-05-U007/062; CL-06-U048/055; CL-08-U16 and HU-09/19; CL-09-D016/030/031/032/035/043/046; CL-10-HU031/PR-CL10-09. Unnamed adjacent questions are not closed.


## WA-R025 — Location consumer alignment and reveal evidence

Class: **AI_RESOLVED** from the binding location product ruling and canonical SH-027/028/131. U-08-13/14's product predicate/directionality is settled: exact service location is disclosed only to the authenticated Professional/provider legitimately performing the active in-person service, within its service-performance window. No buyer, Organization, Search or public-map entitlement to another party's exact location is implied. Completion ends that justification; cancellation, refund or dispute masks/revokes it. Rescheduling requires a fresh current decision. Payment, Booking confirmation or a cached flag alone is insufficient authorization.

Source Modules own their protected location facts/references. Booking's exact/fuzzy/precision/reveal fields are non-authoritative scheduling snapshots or compatibility fields; neither Booking nor Order operates a second reveal lifecycle. Location queries current typed participant, service-state, time-window and source-location facts through owners. Missing/stale/inconsistent facts deny disclosure. Each supported service context has a typed identity; an attached Booking and Order must be consistent, not arbitrarily XOR when both legitimately describe the service. A nullable context pair never permits context-free disclosure. Non-Booking source contexts require an explicitly supported service-performance contract; Job/Organization address fields do not automatically qualify.

Location stores current per-viewer/service/source decision plus immutable decision/revocation history using its owned lifecycle and SH-031 mechanism. The semantic current key includes viewer, typed service context and source reference; an owner source/policy token binds the decision. Atomically reject stale Location writes; revoke/expiry wins over a replayed old allow. Replays may reproduce proof identity but must never re-disclose exact data without a current authorization evaluation. Rescheduling updates evidence in the same owner lifecycle rather than creating a parallel reveal flag. WA-R023 requires durable sensitive-access proof before returning exact data. This resolves U-08-11/12/15/16/19 architecture; exact fields/constraints and coordinated migration remain implementation prerequisites.

Fuzzy generation uses a versioned Location policy per supported typed source, stable for the same source/policy generation. Radius/precision and refresh/expiry settings must be explicitly configured and validated before public use. Source/policy changes, privacy removal and expiry invalidate old results. SH-131 returns only current approved projection fields with source/policy version and validity; absent/stale data is unavailable, never exact fallback or read-triggered generation. Consumers use SH-028 only for generation/invalidation commands. The target-kind registry names actual source owners and validators; free-form target strings cannot broaden support. U-08-17/18 policy structure is AI_RESOLVED; numerical deployment settings are deferred configuration, and geocoder/KMS/vendor evidence is externally gated.

Acceptance: wrong viewer or source relation, absent context, Booking/Order mismatch, completed/cancelled/refunded/disputed service, reschedule, stale source/policy and delayed events, duplicate reveal after revocation, audit failure and expired public projection. Exact location remains absent from Search, notification payloads and telemetry. Legal retention/Privacy dispositions are not selected by this ruling.

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

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.

## WA-R056 — Privacy verification and request execution history

Classification: AI_RESOLVED_WITH_TRADEOFF; external activation and implementation qualification gates below remain explicit. This ruling supersedes conflicting historical proposals only for its stated scope.

Privacy alone owns request transition decisions. Identity supplies immutable verification evidence bound to request subject, requested action/purpose, assurance, method, issuer, verifiedAt, expiry and logical attempt. Privacy verifies applicability against its approved policy revision before submitted→verifying_identity→verified. Failed verification may remain verifying for a permitted new attempt or receive authorized rejection; no guessed legal deadline or attempt limit. Verified→processing dispatches only an immutable execution generation with target inventory and policy/source versions under WA-R020.

Access and export share owner-provided subject-data inventory but differ in output: access is a scoped authorized rights response; export creates a portable private artifact. Neither authorizes another participant's data. Correction/restriction executors acknowledge accepted work separately from completed effect; only verified owner receipts advance completion. Serialize conflicting subject mutations and re-evaluate current policy/source state before each effect. Identity privacy flags project Privacy's outcome; they cannot drive request completion. Search removal requires its qualifying target/generation receipt, not queue acknowledgment.

Cancellation is an authorized request decision for eligible nonterminal work: record actor/reason/version, prevent new dispatch, reconcile in-flight effects and preserve all completed receipts. It never reverses erasure or manufactures rollback. Late receipts remain attached to the cancelled generation and are disclosed in its accounted outcome. Rejection records controlled policy reason, authority, source evidence and applied policy revision, not free-text notes alone. Reopening starts a linked new execution generation after fresh verification/eligibility as required; prior terminal history and effects remain immutable. Notes are minimized append-only annotations with author/time, separate from decision proof. No terminal row overwrite or automatic reexecution of prior completed effects.

Privacy completion follows WA-R020: all targets must have confirmed effect or valid accepted exemption; pending/failed targets cannot be hidden by aggregate completed. A lawful accounted exemption is not automatically technical partial failure. Export readiness requires complete contribution inventory. Exact statutory verification sufficiency, rejection grounds, deadlines, retention periods, backup treatment and final identity disposition remain EXTERNAL_REQUIREMENT, supplied as approved jurisdiction/version policy before the affected path activates. Hold existence alone is not a statutory exemption. Verify stale verification proof, concurrent requests, cancellation during effect, late receipt, reopen after erasure and incomplete export before enabling execution.

## WA-R057 — Privacy owner inventory and private export handoff

Classification: AI_RESOLVED_WITH_TRADEOFF; external activation and implementation qualification gates below remain explicit. This ruling supersedes conflicting historical proposals only for its stated scope.

Each owner implements WA-R020 versioned enumerateSubjectData/evaluateRetentionRequirement/executePrivacyInstruction descriptors. Inventory is explicit, paginated with completion evidence and stable target/version identity; no generic other target or assumed database cascade can count as coverage. Messaging covers Thread, participant current state/history, Message/revisions/restrictions and MessageMedia joins. Notification covers Notification/interaction evidence, NotificationSubscription/credential generations, Delivery attempts and SubscriptionEvent. Location covers FuzzyLocationCache, reveal/revocation evidence and its provider references; exact source facts remain inventoried by their source owner. Restricted proof is accounted even when excluded from requester disclosure. Owner field/action matrices must identify erase, minimize, retain, export or restrict disposition with policy basis and executor receipts before destructive activation.

Privacy owns an immutable export manifest: subject/request/job/generation, owner contribution IDs and versions, authorized field scope, safely stated exclusions with disposition evidence, assembly completion, byte hash/algorithm, creation time and actor/correlation. Exact Location subject data may be included only under approved access policy after removing other parties' data; encryption keys, provider credentials and access tokens are never export content. Record opaque key-version/storage evidence where required, never keys. A complete manifest describes actual serialized bytes, not promised future contributions.

Use Media's WA-R050 createMediaUploadSession→bounded upload→completeMediaUpload→getMediaUploadStatus/getMediaReadiness protocol, with Privacy job/bundle revision as semantic key and purpose-bound private artifact authorization. Same key and bytes replay; changed bytes require a new revision or conflict. Upload acknowledgment never means ready. Require exact immutable ready Media version, matching hash/size and completed manifest before bundle ready. Bind through an explicit Privacy-owned MediaAsset/version reference, not polymorphic ownership. Failed scan/partial assembly keeps download unavailable. Terminal upload retry uses a linked Media attempt per WA-R050 while preserving bundle-generation lineage.

At download, Privacy rechecks requester/action/scope and current generation; Media rechecks asset safety/revocation and issues bounded access through SH-127. Commit required access evidence before protected disclosure. Superseded/expired/revoked generations cannot receive fresh access even if cleanup worker is late. Retain prior manifest/status evidence under approved retention while deleting bytes through Media's executor when authorized. No stored public URL, direct storage SDK or convenience export endpoint may bypass owner gates. Audit exports use the same Media mechanism but an Audit-owned manifest; this ruling does not transfer Audit export ownership.

Legal retention/exemption duration, backup-expiry representation and final retained shell require approved external policy. Location's geocoder/account/region/purpose and key lifecycle qualification remain external activation gates; consumers cannot choose their own geocoder or crypto. Verify omitted child inventory, partial serializer, hash mismatch, scan failure, changed-byte retry, stale generation access, retained shared Media references and provider-deletion uncertainty. Concrete schema, executor field matrices and bilateral fixtures remain implementation qualification, not unresolved architecture permission.

## WA-R071 — Purpose-specific Location facts and disclosure

Location owns closed purpose-qualified source catalog and current disclosure decisions. Service and interview purposes have distinct authorized fields/participants. Source owners provide current facts; revoked/stale/unsupported inputs deny, exact fields stay out of public/notification payloads. Numerical policies, legal retention and provider qualification remain explicit gates.
