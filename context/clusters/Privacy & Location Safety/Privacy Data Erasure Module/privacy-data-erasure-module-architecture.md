# Privacy / Data Erasure Module Architecture

> **Module ID:** `privacy_data_erasure`  
> **Canonical module name:** Privacy / Data Erasure Module  
> **Module type:** `compliance`  
> **Build status:** `mvp_active_legal_gated`  
> **Primary Cluster:** CL-08 Privacy & Location Safety  
> **Document status:** Implementation-grade Module architecture; decision-gated where legal or cross-Module policy is unresolved  
> **Audience:** Coding agents, developers, reviewers, maintainers, compliance reviewers, and future architecture agents  
> **Repository target:** `context/clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md`

**Shared Operation status:** References use permanent IDs and canonical names from `context/shared/shared-operations.md`; that registry controls owner, classification, status, and reusable boundary. SH-003 queryOwnerFacts remains **Proposed ruling** and is not an unconditional prerequisite or an approved universal DTO/API. Adoption requires separate Shared Operations approval before API/schema commitment. Existing source-owner-specific public queries may be consumed within their approved contracts; direct cross-domain Prisma/repository reads remain prohibited.

### Current context paths and missing artifact roles

Read `context/context-map.md` first for authority by concern, then the existing artifacts relevant to the feature:

- Overview: `context/project-overview-v3.md`.
- Shared Operations: `context/shared/shared-operations.md`.
- Cluster architecture: `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`.
- Cluster build plan: `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`.
- Module architecture: `context/clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-architecture.md`.
- Module implementation plan: `context/clusters/Privacy & Location Safety/Privacy Data Erasure Module/privacy-data-erasure-module-implementation-plan.md`.

Root/repository-root and context-root `architecture.md`, `build-plan.md`, `code-standards.md`, and dedicated `progress-tracker.md` are currently **missing**. References to those global artifacts below describe future roles, not loadable files or current authority. Do not create local substitutes or infer global approval. Apply existing concern owners through the context map; stop work that needs a missing global decision. Until a dedicated tracker is available, report progress/blockers in the task completion report; progress does not approve architecture.

---

## 1. Module Header

### Relationship to root architecture

Once reconciled and finalized, the currently missing root Workin Ants architecture will be authoritative for platform-wide rules: source-of-truth ownership, actor identity, authorization, shared operations, event/outbox infrastructure, queue mechanics, observability, audit, provider boundaries, media/file mechanics, search projection, entitlements, and compliance holds.

This Module architecture narrows those rules to `privacy_data_erasure`. It does not restate or replace the full platform architecture.

### Relationship to Cluster architecture

`context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md` is authoritative for CL-08 coordination between Privacy / Data Erasure and Location Safety. CL-08 is a planning and integration boundary; it owns no lifecycle. This file is authoritative for Privacy / Data Erasure's Module-local truth and implementation boundaries.

The CL-08 build plan controls Cluster sequencing. This Module's `implementation-plan.md` may subdivide Privacy work but must not reorder or redefine Cluster ownership.

### Update rule

Update this file when a **binding Module architectural decision** changes. Implementation progress must not silently alter ownership, lifecycle semantics, public contracts, provider boundaries, retention authority, or shared-operation usage.

If implementation encounters an unresolved item, record it in Section 35 and the progress tracker. Do not solve it by introducing a local helper, direct cross-Module Prisma access, provider SDK, hardcoded legal rule, or hidden boolean.

### Evidence reconciliation

The current evidence establishes:

- Privacy / Data Erasure owns formal privacy-rights requests, cross-service fulfillment, retention exemptions, anonymization coordination, and export/erasure proof.
- The authoritative proof schemas are `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, and `DataExportBundle`.
- The current Prisma schema includes request types for `access`, `export`, `erasure`, `correction`, and `restriction`, but several production semantics remain unresolved.
- The historical Deep Module Registry lists direct technologies such as Cloudflare R2 deletion, Daily deletion, and Typesense delete-by-id under Privacy. The later Canonical Shared Operations and CL-08 architecture establish the stronger boundary: **Privacy owns the instruction and orchestration; the provider-owning Module owns provider adapters and deletion mechanics.** This file follows that stronger boundary.
- The Cluster Registry adds CustomerProfile and Track Subscription/Entitlement privacy targets beyond the older target Module registry. This is treated as a registry synchronization update, not a transfer of Customer or Track lifecycle ownership.
- `DataExportBundle.mediaAssetId` is a logical reference without an explicit Prisma relation to `MediaAsset`; explicit referential integrity remains proposed, not yet binding.
- `User.privacyErasedAt` and `User.privacyErasureStatus` are physically on Identity-owned `User`; CL-08 proposes treating them as projections of Privacy completion rather than a second privacy lifecycle.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own the formal platform workflow for a person's privacy rights: access, export, erasure, correction, and restriction.

### Goal

Turn a verified and authorized privacy request into a durable, explainable, cross-Module outcome that answers:

- what data was in scope;
- which Module owned each target;
- what disposition was requested;
- what was erased, anonymized, retained, skipped, or failed;
- why any retained data remained;
- whether a private export was generated;
- whether the request reached a supported terminal result;
- what evidence was preserved without retaining unnecessary personal data.

### What enters

The Module receives:

- authenticated actor context;
- a `PrivacyRequestType`;
- identity-verification proof when required by approved policy;
- subject identity;
- owner-provided subject-data inventories;
- owner-provided retention facts;
- owner-executor results;
- Media artifact results for export generation/access;
- Search projection acknowledgements for privacy-driven de-indexing;
- generic audit and sensitive-access acknowledgements;
- Notification requests/acknowledgements;
- operational retry/failure context;
- policy/version information where approved.

### What leaves

The Module produces:

- authoritative `PrivacyRequest` state;
- authoritative `DataErasureJob` state;
- authoritative target-level `DataErasureTarget` disposition;
- `DataRetentionExemption` proof;
- `DataExportBundle` lifecycle state;
- typed privacy instructions to source Modules;
- typed requests to Search, Media, Audit, Notification, and shared jobs;
- proposed/versioned privacy domain events only after event contracts are approved;
- safe result summaries for requesters and authorized administrators.

### Capability transformation

```text
privacy request
→ authenticated/authorized intake
→ approved identity verification
→ request scoping
→ owner-by-owner subject-data inventory
→ target registration
→ owner-provided retention decision facts
→ owner-executed erase/anonymize/export/correct/restrict action
→ Privacy-owned disposition proof
→ aggregate reconciliation
→ export/erasure/other terminal result
```

### Why this deserves its own Module boundary

Privacy fulfillment is not ordinary deletion. It coordinates records owned across identity, commerce, hiring, messaging, media, video, search, subscriptions, location, audit, and providers while preserving legal/security retention exceptions.

Without a dedicated Module, feature teams would independently implement "delete user" behavior, contradict retention rules, erase evidence, leave provider resources behind, or treat local `deletedAt` fields as proof of legal erasure. This Module centralizes **privacy workflow meaning** without centralizing every Module's data or provider implementation.

---

## 3. Owned Truth

### 3.1 Models and records

| Record | Plain-English meaning | Source-of-truth role |
|---|---|---|
| `PrivacyRequest` | A User's formal request to access, export, erase, correct, or restrict personal data. | Owns aggregate request type, status, request/verification/completion timestamps, due date when approved, and rejection/admin metadata. |
| `DataErasureJob` | Durable orchestration record for one erasure fulfillment run. | Owns erasure workflow status, started/completed times, and aggregate failure state. It is not generic queue state. |
| `DataErasureTarget` | One target inside an erasure job. | Owns the authoritative privacy disposition recorded after the underlying owner executes or justifies retention. |
| `DataRetentionExemption` | Documented reason a target cannot be erased, or cannot yet be erased, under an approved retention basis. | Owns Privacy's retention-exemption proof. The underlying retention facts come from the record owner. |
| `DataExportBundle` | Lifecycle record for a generated, private, short-lived user-data export. | Owns bundle status, Media reference, generation time, expiry, and failure state. Media owns the actual stored object and signed access. |

### 3.2 Owned enums and status vocabularies

- `PrivacyRequestType`
  - `access`
  - `export`
  - `erasure`
  - `correction`
  - `restriction`
- `PrivacyRequestStatus`
  - `submitted`
  - `verifying_identity`
  - `verified`
  - `processing`
  - `completed`
  - `partially_completed`
  - `rejected`
  - `cancelled`
- `DataErasureJobStatus`
  - `queued`
  - `running`
  - `completed`
  - `partially_completed`
  - `failed`
  - `cancelled`
- `DataErasureTargetType`
  - current controlled target vocabulary defined by Prisma, including account/profile, message/thread/notification, Media/R2, Search, video, financial/provider, calendar, digital-good, agreement, CustomerProfile, Track subscription/entitlement/usage/billing, and `other`
- `DataErasureTargetStatus`
  - `pending`
  - `erased`
  - `anonymized`
  - `retained`
  - `failed`
  - `skipped`
- `DataRetentionExemptionReason`
  - `tax_record`
  - `payment_record`
  - `dispute_record`
  - `fraud_prevention`
  - `legal_obligation`
  - `security_audit`
  - `consent_proof`
  - `contract_record`
  - `signature_record`
  - `subscription_billing_record`
  - `other`
- `DataExportStatus`
  - `queued`
  - `generating`
  - `ready`
  - `expired`
  - `failed`

### 3.3 Lifecycles owned

Privacy / Data Erasure alone owns transitions for:

1. `PrivacyRequest.status`
2. `DataErasureJob.status`
3. `DataErasureTarget.status`
4. `DataExportBundle.status`

`DataRetentionExemption` is proof without a separate status lifecycle.

### 3.4 Domain events and ledgers owned

There is **no currently approved Privacy-specific event ledger model** and no binding event-name registry in the supplied evidence.

CL-08 proposes this event family:

```text
privacy.request.submitted
privacy.request.verified
privacy.erasure_job.queued
privacy.target.resolved
privacy.export.ready
privacy.request.completed
```

These names remain **Proposed Ruling PR-08-03** until registered in the root event contract. They must not be emitted as ad hoc strings before approval.

`AuditEvent` and `AccessAuditLog` are not Privacy-owned event ledgers.

### 3.5 Projections owned

Privacy / Data Erasure owns no public Search projection.

`User.privacyErasedAt` and `User.privacyErasureStatus` are not Privacy-owned source truth because `User` is Identity-owned.

**Inherited Proposed Ruling PR-08-01:** treat those fields as Identity-owned projections of a Privacy-owned result. They may not independently declare a `PrivacyRequest` complete.

### 3.6 Snapshots and proof owned

Privacy-owned proof includes:

- request state/timestamps;
- target registration;
- target disposition;
- target action summary;
- target processed time;
- failure summary;
- retention exemption and reason;
- `retainUntil` when supplied;
- export-bundle status and expiry.

The current schema does not yet contain a dedicated request policy-version snapshot, identity-verification reference, correction/restriction proof model, export manifest/hash metadata, executor version, or retry-attempt history. Those are not to be invented without an approved ruling.

### 3.7 Policies and invariants owned

Privacy owns:

- privacy request scope and aggregate lifecycle;
- target registration rules;
- privacy target result interpretation;
- when a returned owner-retention fact becomes a `DataRetentionExemption`;
- erasure/export/correction/restriction orchestration order;
- privacy-specific aggregate completion policy once approved;
- export eligibility and bundle lifecycle;
- what sanitized proof is sufficient to demonstrate fulfillment;
- privacy target executor protocol shape and completeness requirements.

Privacy does **not** own the substantive reason a tax, contract, dispute, fraud, security, consent, or billing record must be retained. The record owner supplies those facts.

---

## 4. Explicit Non-Ownership

Coding agents must treat the following as hard boundaries.

| Adjacent owner | Privacy / Data Erasure may consume | Privacy / Data Erasure must not own or duplicate |
|---|---|---|
| Identity & Access | authenticated actor; privacy identity-verification result; Identity executor result; final Privacy result consumption | authentication, sessions, passkeys/MFA, recovery, User lifecycle, provider identity proof mechanics |
| Role / Authority | `SH-002 authorizeResourceAction` decisions | generic authorization engine, platform/org/participant permission interpretation |
| Consent & Disclosure | consent proof and retention facts | consent acceptance/version lifecycle or consent tables |
| Customer / Buyer Profile | CustomerProfile privacy executor | CustomerProfile lifecycle, buyer actor semantics |
| Track Subscription & Entitlement | subscription/grant/usage/billing privacy executor and retention facts | plan, subscription, entitlement, usage, provider-billing lifecycle |
| Messaging | message/thread subject-data inventory and execution | `Thread`, `Message`, participant or messaging lifecycle |
| Notification | notification subject-data executor; delivery request | Notification/NotificationDelivery lifecycle, provider email/SMS/push clients |
| Media / File Access | Media privacy executor, private export artifact storage, signed Media access | `MediaAsset`, R2/S3 deletion mechanics, scanning, processing, EXIF/GPS scrubbing, `MediaAccessGrant`, signed URL implementation |
| Search / Public Visibility | privacy-driven projection-refresh/de-index request | `SearchUpsertEvent`, Typesense adapter, index state, Search reconciliation |
| Video Infrastructure | video subject-data executor and provider deletion | Daily/Mux/Agora clients, room/asset/grant lifecycle, provider-event dedupe |
| Booking & Calendar | calendar/provider reference executor; owner facts if needed | Booking lifecycle, Cronofy client, calendar provider dedupe |
| Transaction / Order | Agreement/Order executor and contract/signature retention facts | Order, Agreement, signature, document snapshot, refund/payment truth |
| Payment / Payout / Tax | financial executor and tax/payment/fraud retention facts | Stripe client, KYC, TaxProfile, Payout, financial lifecycle or retention law |
| Review / Dispute | dispute retention facts/executor where applicable | Dispute lifecycle and payout-hold meaning |
| Digital Goods Access | grant/event/accessibility privacy executor | digital entitlement/access lifecycle |
| Location Safety | Location privacy executor | `FuzzyLocationCache`, `LocationReveal`, fuzzing/reveal policy |
| Audit / Event Ledger | append audit and sensitive-access proof | `AuditEvent`, `AccessAuditLog`, generic audit schema |
| Observability / Ops | logs, IntegrationFailure, QueueJob, incidents | operational truth, queue infrastructure, generic incident lifecycle |
| Admin Review / Compliance Hold | active hold facts where approved | `ComplianceHold` lifecycle or local `privacyBlocked` flags |

### Provider non-ownership

Privacy does not own provider clients for:

- Cloudflare R2 / S3-compatible storage;
- Typesense;
- Daily;
- Mux;
- Agora;
- Stripe;
- subscription billing providers;
- Cronofy/calendar providers;
- identity-verification providers;
- Notification delivery providers.

The registry's historical listing of these technologies describes systems touched by erasure, not an implementation license to place provider SDKs inside this Module.

---

## 5. Module Architecture Principles

1. **Privacy owns the request; data owners own the data.**
2. **Privacy owns orchestration; owner Modules execute.**
3. **Product deletion is not privacy erasure.**
4. **A local `erasedAt` marker is evidence of an owner-local effect, not proof the full request is complete.**
5. **A retained target requires explicit `DataRetentionExemption` proof based on owner facts.**
6. **Privacy may not independently decide tax, contract, dispute, fraud, consent, security, or subscription-billing retention requirements.**
7. **Provider deletion must occur behind the provider-owning Module.**
8. **Search de-indexing must occur through Search-owned interfaces.**
9. **Export bytes and signed access remain Media-owned mechanics.**
10. **Generic audit and operational records never replace Privacy lifecycle truth.**
11. **Queues and workflow runners are mechanisms; `DataErasureJob` remains business truth.**
12. **Cross-Module reads use public interfaces, not generic Prisma repositories.**
13. **Target descriptors are minimized and must not carry raw personal-data payloads.**
14. **`DataErasureTargetType.other` never authorizes generic deletion; an explicit owner and supported executor are required.**
15. **No legal deadline, rejection ground, identity-verification method, retention period, or aggregate semantics may be guessed.**
16. **No Track entitlement gates the exercise of a privacy right unless future approved legal/product policy explicitly says otherwise.**
17. **Consent proof is not permission to process or reject a privacy request.**
18. **Admin/support roles do not automatically grant export-content access.**
19. **Sensitive export access is re-authorized at access time and audited.**
20. **Telemetry never contains export contents, signed URLs, raw provider payloads, credentials, message bodies, resumes, tax details, or other unnecessary subject data.**

---

## 6. Proposed Folder / Code Structure

Use the root code-standard naming conventions if they differ, but preserve these responsibilities.

```text
src/modules/privacy-data-erasure/
├── application/
│   ├── commands/
│   │   ├── submit-privacy-request.ts
│   │   ├── start-verified-erasure.ts
│   │   ├── register-erasure-targets.ts
│   │   ├── record-retention-exemption.ts
│   │   ├── resolve-erasure-target.ts
│   │   ├── generate-data-export-bundle.ts
│   │   ├── expire-data-export-bundle.ts
│   │   └── complete-privacy-request.ts          # decision-gated final semantics
│   ├── queries/
│   │   ├── get-privacy-request.ts
│   │   ├── list-user-privacy-requests.ts
│   │   ├── get-erasure-job-summary.ts
│   │   ├── get-privacy-export-status.ts
│   │   └── get-executor-coverage.ts
│   ├── orchestration/
│   │   ├── orchestrate-privacy-fulfillment.ts
│   │   ├── discover-subject-data.ts
│   │   ├── process-erasure-target.ts
│   │   ├── reconcile-erasure-job.ts
│   │   └── assemble-export-sections.ts
│   └── services/
│       └── privacy-executor-registry.ts
├── domain/
│   ├── policies/
│   │   ├── privacy-request-policy.ts
│   │   ├── target-registration-policy.ts
│   │   ├── target-disposition-policy.ts
│   │   └── export-policy.ts
│   ├── transitions/
│   │   ├── privacy-request-transitions.ts
│   │   ├── erasure-job-transitions.ts
│   │   ├── erasure-target-transitions.ts
│   │   └── export-bundle-transitions.ts
│   ├── reason-codes.ts
│   └── types.ts
├── contracts/
│   ├── public.ts
│   ├── privacy-executor.ts
│   ├── retention-result.ts
│   ├── export-section.ts
│   └── event-contracts.ts                       # only approved/registered events
├── infrastructure/
│   └── repositories/
│       ├── privacy-request-repository.ts
│       ├── erasure-job-repository.ts
│       ├── erasure-target-repository.ts
│       ├── retention-exemption-repository.ts
│       └── export-bundle-repository.ts
├── workers/
│   ├── privacy-inventory-worker.ts
│   ├── erasure-target-worker.ts
│   ├── erasure-reconciliation-worker.ts
│   ├── export-generation-worker.ts
│   └── export-expiry-worker.ts
├── ui/
│   ├── self-service/
│   └── admin/
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── concurrency/
    ├── compliance/
    └── e2e/
```

### Folder prohibitions

Do not create inside this Module:

```text
providers/r2.ts
providers/typesense.ts
providers/stripe.ts
providers/daily.ts
providers/mux.ts
providers/agora.ts
providers/cronofy.ts
auth/
permissions/
audit/
queue/
crypto/
search/
media/
notifications/
generic-repository/
```

If a dependency interface is missing, stub the **interface** for contract tests and schedule implementation in the owning Module. Do not create a local provider or lifecycle substitute.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery/UI | Self-service request intake/status, export readiness/download initiation; narrow admin diagnostics/review surfaces | authentication, generic admin permissions, raw provider data, direct Media/Search/provider calls |
| Application commands | Privacy request and Module-owned lifecycle mutations | neighboring Module mutations |
| Application queries | Privacy-owned request/job/target/export views and executor coverage diagnostics | federated universal user-data reads bypassing executors |
| Orchestration | sequencing verification, inventory, retention, target dispatch, export, reconciliation | provider SDK logic; source Module lifecycle decisions |
| Domain policy | request-type rules, target registration, result mapping, aggregate policy once approved | tax/contract/fraud/security retention law |
| Transition layer | Privacy-owned state-transition graphs | generic platform lifecycle policy |
| Repositories | CRUD and locking for Privacy-owned Prisma models only | cross-domain repositories |
| Contracts | public Privacy API and privacy executor protocol | source Module internal schemas |
| Workers | durable Privacy work and retries using shared queue primitives | generic queue framework or provider reconciliation |
| Provider adapters | none | all external provider clients touched indirectly by privacy instructions |
| Events | Privacy event names/payload meaning after approval | outbox/inbox infrastructure |
| Tests | Privacy domain, contract, integration, concurrency, compliance, E2E | testing another Module's internals through direct DB writes except approved fixtures |

---

## 8. Data Model

### 8.1 `PrivacyRequest`

**Purpose:** aggregate root for the formal privacy-rights request.

**Key relationships:**

- belongs to Identity-owned `User` through `userId`;
- has zero or more `DataErasureJob` records;
- has zero or more `DataExportBundle` records.

**Authoritative fields:**

- `id`
- `userId`
- `type`
- `status`
- `requestedAt`
- `verifiedAt`
- `dueAt`
- `completedAt`
- `rejectionReason`
- `adminNote`

**Lifecycle field:** `status`.

**Indexes:**

- `[userId, status]`
- `[type, status]`
- `[dueAt]`

**Uniqueness:** no current constraint prevents multiple active or conflicting requests for one User.

**Concurrency sensitivity:** high. Request transitions, duplicate submit, completion, rejection/cancellation, and worker progression may race.

**Retention/privacy concerns:**

- request metadata is itself personal/compliance data;
- `adminNote` can easily become an uncontrolled sensitive-data field; UI and services must restrict content;
- the retention/anonymization policy for Privacy's own proof records is not yet defined;
- parent deletion currently cascades to erasure jobs and export bundles, so ordinary cleanup must not delete the evidence needed to prove fulfillment.

### 8.2 `DataErasureJob`

**Purpose:** durable Privacy-owned orchestration record for erasure.

**Key relationships:**

- belongs to `PrivacyRequest`;
- has many `DataErasureTarget`.

**Authoritative fields:**

- `privacyRequestId`
- `userId`
- `status`
- `startedAt`
- `completedAt`
- `failureReason`

**Lifecycle field:** `status`.

**Indexes:**

- `[privacyRequestId]`
- `[userId, status]`
- `[status, createdAt]`

**Uniqueness:** no unique constraint currently enforces one job per request.

**Concurrency sensitivity:**

- duplicate start workers can create competing jobs unless command idempotency plus DB locking is applied;
- aggregate reconciliation must not be derived from generic queue state.

**Retention/privacy concerns:** contains subject identifiers and failure summaries; failure text must be sanitized.

### 8.3 `DataErasureTarget`

**Purpose:** one persisted target-level privacy disposition.

**Key relationships:**

- belongs to `DataErasureJob`;
- has zero or more `DataRetentionExemption` records.

**Authoritative fields:**

- `targetType`
- `targetId`
- `externalProvider`
- `externalRef`
- `status`
- `actionTaken`
- `failureReason`
- `processedAt`

**Lifecycle field:** `status`.

**Indexes:**

- `[erasureJobId, status]`
- `[targetType, targetId]`
- `[externalProvider, externalRef]`

**Uniqueness:** no current target fingerprint/unique constraint exists.

**Concurrency sensitivity:**

- discovery can duplicate targets;
- duplicate job delivery can execute the same owner effect twice;
- target rows lack `updatedAt` or version fields, so use a DB row/advisory lock after creation or an approved compare-and-set strategy.

**Retention/privacy concerns:**

- `targetId` and `externalRef` may be sensitive identifiers;
- `actionTaken` and `failureReason` must contain reason codes/minimized summaries rather than raw provider or subject payloads;
- `externalProvider` does not transfer provider ownership.

**Schema gap:** the protocol target descriptor requires `ownerModule` and `sourceVersion`, but the persisted model has no such fields. For target types with ambiguous owners, production execution must remain decision-gated until owner identity can be resolved durably through an approved registry/schema strategy.

### 8.4 `DataRetentionExemption`

**Purpose:** durable Privacy proof for a target that cannot be erased under an approved retention basis.

**Key relationship:** belongs to `DataErasureTarget`.

**Authoritative fields:**

- `reason`
- `note`
- `retainUntil`
- `createdAt`

**Lifecycle/status:** none.

**Indexes:**

- `[erasureTargetId]`
- `[reason]`

**Uniqueness:** multiple exemption records may currently exist for the same target.

**Concurrency sensitivity:** duplicate exemption creation under retry must be made idempotent through the command mechanism.

**Retention/privacy concerns:**

- the proof may itself need long retention;
- `note` must not become free-form legal/private-data dumping;
- parent target/job/request cascades could delete the exemption, conflicting with the rule that proof of erasure/retention must be preserved.

### 8.5 `DataExportBundle`

**Purpose:** lifecycle record for a private, short-lived export artifact.

**Key relationships:**

- belongs to `PrivacyRequest`;
- contains logical `mediaAssetId` reference to a Media-owned artifact.

**Authoritative fields:**

- `privacyRequestId`
- `userId`
- `status`
- `mediaAssetId`
- `expiresAt`
- `generatedAt`
- `failureReason`

**Lifecycle field:** `status`.

**Indexes:**

- `[privacyRequestId]`
- `[userId, status]`
- `[expiresAt]`

**Uniqueness:** multiple bundles per request are currently possible.

**Concurrency sensitivity:** duplicate generation and expiry race; use request/bundle lock and idempotent generation identity.

**Retention/privacy concerns:**

- artifact must be private and short-lived;
- signed URLs are temporary delivery credentials and must not be persisted here;
- bundle payload must not appear in logs;
- expired bundle state does not itself delete the Media object; cleanup must be requested from Media and reconciled.

**Inherited Proposed Ruling PR-08-04:** add explicit referential integrity to `MediaAsset` or an equivalent approved Media reference contract. Do not add the relation until approved.

### 8.6 External physical fields relevant to this Module

Identity-owned `User` currently contains:

- `privacyErasedAt`
- `privacyErasureStatus`

They are not Privacy source truth. See PR-08-01.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 `PrivacyRequest`

Current status vocabulary:

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

The complete production transition graph is **not yet binding** because U-08-01, U-08-04, U-08-05, U-08-06, and U-08-07 remain unresolved.

#### Build-safe subset

```text
create → submitted
verified → processing              # only from an authoritative verified fixture/result
processing → [not finalized by guessed aggregate policy]
```

#### Reserved, decision-gated transitions

Conceptually expected but not implementable as production policy until approved:

```text
submitted → verifying_identity
verifying_identity → verified
submitted/verifying_identity/... → rejected
eligible nonterminal states → cancelled
processing → completed
processing → partially_completed
```

**Transition owner:** Privacy / Data Erasure.

**Triggers:** Privacy commands/workers only, consuming approved Identity and owner results.

**Terminal states:** `completed`, `partially_completed`, `rejected`, `cancelled`; exact reopening/reversal rules are unresolved.

**Concurrency:** lock or CAS request aggregate; no client-side transition.

**History proof:** generic Audit events may be appended; no Privacy-specific event ledger currently exists.

**Prohibited shortcut:** direct status assignment from UI, provider callback, owner executor, QueueJob, Search result, or `User.privacyErasureStatus`.

### 9.2 `DataErasureJob`

Expected buildable graph:

```text
queued → running
running → completed
running → partially_completed
running → failed
```

`cancelled` exists in the enum, but cancellation policy must follow the approved request/job cancellation rules.

**Transition owner:** Privacy.

**Triggers:** worker start and aggregate reconciliation.

**Terminal states:** `completed`, `partially_completed`, `failed`, `cancelled`.

**Concurrency:** request/job aggregate lock during start and reconciliation.

**Proof:** job timestamps plus target dispositions; QueueJob is not proof.

### 9.3 `DataErasureTarget`

Expected graph:

```text
pending → erased
pending → anonymized
pending → retained
pending → failed
pending → skipped
```

A retryable technical error is not automatically a final privacy disposition. Shared queue retry state remains operational until either retry succeeds or the Module's approved retry policy reaches a terminal result.

**Transition owner:** Privacy records the disposition after owner execution.

**Trigger:** typed `SH-095 executePrivacyInstruction`/retention result.

**Terminal states:** all non-`pending` statuses under the current enum.

**Reversal:** no reopen semantics are established. A new instruction/job may be required if a new privacy request occurs.

**Concurrency:** one target effect at a time; use idempotency and DB locking.

**Proof:** `actionTaken`, `failureReason`, `processedAt`, exemption records, owner result evidence reference where supported.

**Prohibited shortcut:** marking `erased` because a job ran, because a provider call was queued, or because an owner-local soft-delete field changed.

### 9.4 `DataExportBundle`

Expected graph:

```text
queued → generating → ready → expired
queued/generating → failed
```

Whether `failed` may be retried in-place or via a new bundle is not explicitly established; use idempotent job retry before terminal failure.

**Transition owner:** Privacy.

**Triggers:** export worker, Media artifact completion, expiry worker.

**Terminal states:** `expired`, `failed`; `ready` is a stable deliverable state until expiry.

**Concurrency:** one semantic generation effect per request/export format/version; bundle row locking for finalization/expiry.

**Proof:** lifecycle timestamps plus Media reference and sensitive-access audit.

### 9.5 `DataRetentionExemption`

No status machine.

Rules:

- created only from owner-supplied retention facts accepted by Privacy policy;
- must identify a controlled reason;
- `other` requires explicit approved basis, not arbitrary admin preference;
- `retainUntil` is populated only if supplied by authoritative policy;
- exemption presence cannot be inferred from a source Module's local "do not delete" boolean.

---

## 10. Commands

### 10.1 `submitPrivacyRequest`

**Purpose:** create a formal Privacy request.

**Actor/context:** authenticated User for self-service; explicitly authorized support/admin for supported administrative intake.

**Authoritative inputs:**

- authenticated actor;
- subject User when administrative intake is allowed;
- `PrivacyRequestType`;
- idempotency key;
- minimized request metadata.

**Preconditions:**

- valid actor;
- runtime-valid request type;
- authority check;
- active-request concurrency policy is not guessed.

**State written:** new `PrivacyRequest(status=submitted)`.

**Shared operations:**

- `SH-001 resolveAuthenticatedActor`
- `SH-002 authorizeResourceAction`
- `SH-044 executeIdempotentCommand`
- `SH-029 appendAuditEvent`
- safe request/log context operations

**Effects:** optional approved submission event/notification only after corresponding contracts exist.

**Idempotency:** semantic fingerprint includes actor/subject + request type + intended intake operation. Same key/same fingerprint replays original result; same key/different fingerprint conflicts.

**Failure modes:** validation, unauthenticated, unauthorized, idempotency conflict, persistence failure.

### 10.2 `startVerifiedErasure`

**Purpose:** create and queue a durable erasure job for a request already proven `verified`.

**Actor/context:** system/worker context; production verification must originate from approved Identity proof.

**Inputs:** request ID, correlation context, idempotency key.

**Preconditions:**

- `PrivacyRequest.type=erasure`;
- `PrivacyRequest.status=verified`;
- no conflicting already-started semantic job;
- no invented retention or completion rule.

**State written:** `DataErasureJob(status=queued)`; request may move to `processing` when the approved transition occurs.

**Shared operations:**

- `SH-044 executeIdempotentCommand`
- `SH-053 transitionLifecycleState`
- `SH-051 acquireAggregateLock`
- `SH-047 enqueueReliableJob`
- `SH-029 appendAuditEvent`

**Idempotency:** one semantic start effect per privacy request.

**Failure modes:** stale status, conflict, queue failure, persistence failure.

### 10.3 `registerErasureTargets`

**Purpose:** persist stable target references discovered through owner inventories.

**Actor/context:** erasure orchestration worker.

**Inputs:** erasure job; owner target descriptors.

**Preconditions:**

- job active;
- each descriptor returned by a registered owner executor;
- target owner/reference revalidates;
- `other` has explicit owner and cannot invoke generic deletion.

**State written:** `DataErasureTarget(status=pending)`.

**Shared operations:**

- `SH-123 validateOwnedTargetReference`
- `SH-051 acquireAggregateLock`
- `SH-044 executeIdempotentCommand`

**Idempotency:** dedupe target registration under the erasure-job lock using the approved semantic target identity.

**Failure modes:** unknown executor, invalid target, ambiguous owner, duplicate/conflict, persistence failure.

### 10.4 `recordDataRetentionExemption`

**Purpose:** persist Privacy-owned proof that an owner-held target must be retained.

**Actor/context:** Privacy orchestration after an owner retention result.

**Inputs:** target ID; controlled reason; source/basis reference; sanitized note; `retainUntil` if authoritative.

**Preconditions:**

- target belongs to active job;
- owner returned required retention facts;
- reason maps to controlled Privacy vocabulary;
- no arbitrary legal reason invented locally.

**State written:** `DataRetentionExemption`; target disposition according to approved execution result.

**Shared operations:**

- `SH-097 evaluateRetentionRequirement` (owner protocol)
- `SH-044 executeIdempotentCommand`
- `SH-029 appendAuditEvent`

**Idempotency:** same target/basis/result must not create duplicate equivalent proof under retry.

**Failure modes:** missing owner basis, unsupported reason, stale target, conflict.

### 10.5 `resolveErasureTarget`

**Purpose:** record the authoritative Privacy disposition after the source owner executes the requested instruction.

**Actor/context:** target worker/system.

**Inputs:** target ID; owner result; evidence reference; safe action/reason code.

**Preconditions:**

- target pending;
- owner result conforms to privacy executor contract;
- provider result has already been normalized by provider owner;
- retention result satisfies exemption rule.

**State written:** target `status`, `actionTaken`, `failureReason`, `processedAt`; exemption where applicable.

**Shared operations:**

- `SH-095 executePrivacyInstruction`
- `SH-048 executeRetryWithBackoff`
- `SH-044 executeIdempotentCommand`
- `SH-053 transitionLifecycleState`
- `SH-029 appendAuditEvent`
- `SH-037 recordIntegrationFailure` for operational failures

**Idempotency:** duplicate worker deliveries replay prior result; do not repeat owner side effects.

**Failure modes:** retryable dependency failure, terminal owner failure, retained-without-basis invariant violation, stale result, unknown result category.

### 10.6 `generateDataExportBundle`

**Purpose:** build a private export for a verified `export` request.

Production export is gated until SH-100 createPrivacyExportArtifact is fully satisfied: manifest and per-owner sections, archive hash/encryption, protected MediaAccessGrant/access, expiry and cleanup, and sensitive-access audit. A bare `DataExportBundle.mediaAssetId` is not sufficient production proof. The Media handoff, integrity/persistence representation, algorithm, and key-management implementation remain unresolved; this requirement does not approve them.

**Actor/context:** export worker/system; requester authorization happens at read/access boundary.

**Inputs:** verified request ID; owner export sections; approved export format/version; correlation/idempotency.

**Preconditions:**

- `type=export`;
- authoritative `verified`;
- all required owner serializers accounted for under approved export policy;
- Media private artifact interface available.

**State written:** `DataExportBundle` lifecycle.

**Shared operations:**

- `SH-096 enumerateSubjectData`
- `SH-100 createPrivacyExportArtifact`
- Media artifact interface
- `SH-072 hashCanonicalPayload` for mandatory SH-100 createPrivacyExportArtifact archive/manifest integrity
- approved shared encryption mechanism for mandatory SH-100 createPrivacyExportArtifact archive protection
- `SH-047 enqueueReliableJob`
- `SH-044 executeIdempotentCommand`
- `SH-029 appendAuditEvent`

**Effects:** optional approved `privacy.export.ready` event and Notification request.

**Idempotency:** request + export format/version.

**Failure modes:** owner serializer failure, Media artifact failure, encryption/hash failure, incomplete export policy.

### 10.7 `expireDataExportBundle`

**Purpose:** make an expired bundle unavailable and request underlying artifact cleanup.

**Actor/context:** scheduled worker/system.

**Inputs:** bundle ID or bounded expiry scan.

**Preconditions:** `expiresAt` reached under approved export policy.

**State written:** `DataExportBundle.status=expired`.

**Shared operations:**

- `SH-055 runDeadlineExpiration`
- `SH-047 enqueueReliableJob`
- Media privacy/delete interface
- `SH-044 executeIdempotentCommand`
- `SH-029 appendAuditEvent`
- `SH-037 recordIntegrationFailure`

**Idempotency:** bundle ID + expiry version.

**Failure modes:** cleanup dependency failure must not restore access; cleanup is retried through Media owner.

### 10.8 Decision-gated commands

The following commands are part of the declared Module capability but are **not production-implementable until the referenced unresolved decisions are approved**:

- `verifyPrivacyRequestIdentity`
- `cancelPrivacyRequest`
- `rejectPrivacyRequest`
- `processDataAccessRequest`
- `processDataCorrectionRequest`
- `processDataRestrictionRequest`
- `completePrivacyRequest`

Their final inputs, transition rules, proof fields, and authority cannot be invented in this file.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result type | Meaning | Consumer must not infer |
|---|---|---|---|---|---|
| `getPrivacyRequest` | requester; authorized admin/support | actor, request ID | source truth | current request state, safe dates, safe summary, bundle summary | underlying owner-data state or legal completion beyond `status` |
| `listUserPrivacyRequests` | requester; authorized admin/support | actor/subject, paging/filter | source truth | request history | absence of unregistered owner data |
| `getErasureJobSummary` | requester-safe view; admin detailed view | actor, request/job ID | source truth/read model over Privacy records | job status and target counts | QueueJob/provider success |
| `getErasureTargetSummary` | authorized admin/compliance | actor, target ID | source truth | target status, owner/type, safe reason/evidence reference | source record contents |
| `getPrivacyExportStatus` | requester; authorized admin | actor, request/bundle ID | source truth | queued/generating/ready/expired/failed | permission to download without a fresh access check |
| `authorizePrivacyExportDownload` | Media access handoff | actor, bundle ID | decision | allow/deny with stable reason and Media reference if allowed | permanent entitlement or Media mechanics |
| `getExecutorCoverage` | developer/admin diagnostics | authorized actor | diagnostic projection | target type → owner executor/protocol/policy status | permission to read raw subject data |
| `evaluatePrivacyRequestEligibility` | Privacy application layer | request/actor/policy context | decision, **decision-gated** | whether processing may continue | general Identity or legal authority |
| `reconcileErasureJobOutcome` | Privacy worker | job + target states | domain decision | parent job result under approved aggregation policy | request completion when retained semantics unresolved |

### Stable reason-code guidance

Public/module contracts should return stable Privacy reason categories rather than raw provider strings, such as:

```text
validation_failed
unauthenticated
unauthorized
not_found
idempotency_conflict
stale_state
request_not_verified
unsupported_request_type
unsupported_target_type
owner_not_registered
owner_unavailable
retention_basis_required
retained
dependency_retryable
dependency_terminal_failure
export_not_ready
export_expired
manual_review_required
policy_not_configured
decision_gated
```

Exact names may align to root error conventions. Provider names/messages must not leak into consumer contracts.

---

## 12. Public Module Interface

### Public commands

Immediately implementable:

```text
submitPrivacyRequest
```

Decision-gated:

```text
cancelPrivacyRequest
verifyPrivacyRequestIdentity
rejectPrivacyRequest
```

### Public queries

```text
getPrivacyRequest
listUserPrivacyRequests
getPrivacyExportStatus
authorizePrivacyExportDownload
```

`getErasureJobSummary` and `getExecutorCoverage` are administrative/internal public interfaces, not ordinary user APIs.

### Module-owned internal commands/orchestration

```text
startVerifiedErasure
registerErasureTargets
recordDataRetentionExemption
resolveErasureTarget
generateDataExportBundle
expireDataExportBundle
reconcileErasureJobOutcome
orchestratePrivacyFulfillment # SH-099 orchestratePrivacyFulfillment
completePrivacyRequest              # decision-gated final semantics
```

### Privacy executor protocol owned as a cross-Module contract

Privacy defines the protocol shape; each source owner implements it:

```text
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
export serialization
```

The contract must carry only the minimum stable descriptor/evidence needed. It is not a universal repository.

### Emitted domain events

No event family is binding today. PR-08-03 names remain proposed.

### Provider-facing interfaces

Privacy owns **none**.

All provider actions occur through provider-owning Module interfaces such as:

```text
deleteProviderResource # SH-070 deleteProviderResource
requestSearchProjectionRefresh # SH-091 requestSearchProjectionRefresh
issueSignedMediaUrl # SH-087 issueSignedMediaUrl
```

---

## 13. Inbound Dependencies

| Owning Module / shared owner | Public operation/interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | `SH-001 resolveAuthenticatedActor` | establish trusted actor | actor ID, platform role/security context needed by auth layer | yes | session parsing/auth helpers |
| Identity & Access | approved privacy identity-verification interface | prove requester before destructive/export fulfillment | durable proof reference/result, evaluated time, assurance | yes | identity verification provider workflow |
| Role / Authority | `SH-002 authorizeResourceAction` | self/admin/support access | action, actor, resource relationship facts | yes | generic permission engine |
| each data owner | `SH-096 enumerateSubjectData` | discover subject-held data | stable target descriptor, actions, sensitivity, cursor | yes for complete inventory | global DB crawler |
| each data owner | `SH-097 evaluateRetentionRequirement` | receive mandatory retention facts | required, reason, basis, `retainUntil`, minimum fields, permitted anonymization | yes | local tax/legal retention law |
| each data owner | `SH-095 executePrivacyInstruction` | owner-local mutation | typed disposition/evidence | yes | cross-Module writes |
| target owner | `SH-123 validateOwnedTargetReference` | prevent stale/wrong-target execution | target exists/version/context/allowed relationship | yes | direct existence query |
| Media / File Access | Media privacy executor | delete/anonymize Media data | target result | yes for Media target | R2 client |
| Media / File Access | private artifact create/finalize + `SH-087 issueSignedMediaUrl` | export storage/delivery | Media reference/access result | yes for export | signed URL/storage code |
| Search / Public Visibility | `SH-091 requestSearchProjectionRefresh` | remove/update public projection | target, action, safe source version/reason | projection can lag but must be reconciled | `SearchUpsertEvent` write/Typesense |
| Audit / Event Ledger | `SH-029 appendAuditEvent` | generic lifecycle/action proof | actor/system, action, target, outcome, correlation, safe metadata | criticality follows root policy | privacy audit table |
| Audit / Event Ledger | `SH-030 recordSensitiveAccess` | export issuance/download proof | actor, sensitivity, target, decision, correlation | access policy may require it | `PrivacyAccessLog` |
| Notification | `SH-041 requestNotification` | request/export status communication | recipient, template key, sensitivity, variables, idempotency | normally no domain-state rollback | SES/SMS/push clients |
| Observability / Ops | request/log/failure interfaces | safe diagnostics | correlation, module, operation, safe reason/dimensions | operational only | business status in logs |
| shared platform | `SH-044 executeIdempotentCommand` | retry-safe mutations | semantic key/fingerprint/result | yes | local idempotency table/framework |
| shared queue | `SH-047 enqueueReliableJob`, `SH-048 executeRetryWithBackoff` | durable async work | typed job payload/correlation/retry classification | yes for async progress | local queue |
| shared workflow | `SH-049 orchestrateWorkflowSteps`, `SH-050 reconcileWorkflowStatus` | reusable orchestration plumbing | step/result hooks | no ownership transfer | generic Privacy workflow truth |
| shared persistence | `SH-051 acquireAggregateLock`, `SH-052 withOptimisticConcurrency` | prevent races | aggregate key/expected version | yes | in-memory mutex |
| shared lifecycle | `SH-053 transitionLifecycleState` | transition plumbing | current/next + local policy | yes | central generic privacy policy table |
| shared scheduler | `SH-055 runDeadlineExpiration` | export expiry | cursor/time/owner handler | yes for timely expiry | custom cron framework |
| Location Safety | privacy executor contract | disposition location-owned privacy data | Location target descriptors/results | yes for complete subject scope | Location rows/policy |
| Transaction / Payment / Dispute / Consent / Track | owner retention facts | justify exemptions | controlled owner reason/basis | yes for target deletion | substantive retention rules |

---

## 14. Outbound Consumers and Effects

### Consumers of Privacy truth

- **Identity & Access**
  - may consume final approved Privacy result to update Identity-owned erasure markers/account disposition;
  - must not infer completion from local User fields.
- **Media / File Access**
  - executes privacy instructions;
  - may consume export eligibility handoff for artifact creation/access.
- **Messaging, Video, Digital Goods, Booking, Payment, Transaction, Customer, Track, Notification, Location Safety**
  - implement owner executor protocol;
  - may use Privacy request/target correlation for execution evidence;
  - do not create their own `PrivacyRequest`.
- **Search / Public Visibility**
  - consumes explicit refresh/de-index requests;
  - must not inspect Privacy tables and reconstruct visibility policy.
- **Audit / Event Ledger**
  - receives sanitized proof requests.
- **Observability / Ops**
  - receives safe operational failures/correlation.
- **authorized requester/admin UI**
  - reads Privacy truth and safe summaries only.

### Downstream effects

Privacy may request:

- owner-local erasure/anonymization/restriction/correction/export;
- provider deletion through provider owner;
- Search projection refresh/removal;
- Media artifact creation, signed access, and cleanup;
- Notification delivery;
- Audit append/sensitive-access logging;
- reliable jobs;
- operational failure recording.

### Mutation rule

Privacy must not mutate another Module's source truth directly merely because it orchestrates the sequence.

---

## 15. Canonical Shared Operations Used

The canonical registry supplies permanent SH IDs. Only operations consumed here are listed; Proposed references remain adoption-gated.

| Canonical operation | Classification | Canonical owner | Why Privacy uses it | Invocation point | Privacy-local policy | Expected result | Prohibited duplicates |
|---|---|---|---|---|---|---|---|
| `SH-001 resolveAuthenticatedActor` | Platform capability | Identity & Access | establish trusted requester/admin/system actor | every protected entry | request intent and subject context | typed actor | `requireUser`, `privacyCurrentUser`, local session parser |
| `SH-002 authorizeResourceAction` | Cross-cutting capability | Role / Authority | authorize self/admin/support action | before protected read/write | resource ownership/action vocabulary | allow/deny + reasons | `privacyAuth`, `adminGuard`, local permission matrix |
| `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` | Shared contract; separate implementations | Each source Module | obtain minimum owner facts | retention/executor/context needs | exact DTO needed | owner facts + version | cross-domain repository |
| `SH-029 appendAuditEvent` | Platform audit capability | Audit / Event Ledger | preserve important action proof | request intake, lifecycle, exemptions, completion | event meaning + safe metadata | audit acknowledgement/reference | `privacyAudit` table/writer |
| `SH-030 recordSensitiveAccess` | Cross-cutting capability | Audit / Event Ledger | export issuance/download and sensitive admin reads | access boundary | sensitivity/context | access proof acknowledgement | `PrivacyAccessLog` |
| `SH-041 requestNotification` | Platform notification capability | Notification | status-ready/failure communications | after committed business state | template intent, safe variables | Notification acknowledgement | direct SES/SMS/push |
| `SH-044 executeIdempotentCommand` | Platform primitive | Platform application infrastructure | one business effect under retry | all retryable commands | semantic key/fingerprint/conflict | original/new result | module idempotency store |
| `SH-046 publishDomainEvent` | Platform primitive | Platform event/outbox infrastructure | publish approved facts after commit | only after PR-08-03/root registration | event names/payload minimization | outbox acknowledgement | fire-and-forget event bus |
| `SH-045 deduplicateDomainEvent` | Platform primitive | Platform event infrastructure; consumer owns inbox | prevent duplicate consumer effect | event consumers if/when events exist | handler identity/effect | inbox result | per-worker custom dedupe |
| `SH-047 enqueueReliableJob` | Platform primitive | Shared queue infrastructure | durable erasure/export work | async work | payload + business completion meaning | job reference | privacy queue framework |
| `SH-048 executeRetryWithBackoff` | Platform primitive | Shared queue/platform infrastructure | retry transient owner/provider failures | worker boundary | retry classification | retry/dead-letter outcome | custom sleep/retry loops |
| `SH-049 orchestrateWorkflowSteps` | Shared mechanism; separate workflow truth | Workflow-owning Module using shared runner | persisted multi-step fulfillment | orchestration | Privacy step order/partial semantics | step execution state | generic Privacy replacement workflow |
| `SH-050 reconcileWorkflowStatus` | Shared mechanism; separate policy | Workflow owner using shared helper | aggregate target outcomes | after child results | Privacy completed/partial/failed meaning | parent decision | QueueJob-derived status |
| `SH-053 transitionLifecycleState` | Shared mechanism; separate truth | Shared mechanism; lifecycle owner supplies policy | safe status transitions | each lifecycle mutation | Privacy transition graph | transition result | generic lifecycle table owning policy |
| `SH-051 acquireAggregateLock` | Platform primitive | Shared persistence infrastructure | serialize request/job/target writes | conflicting commands/workers | lock key/conflicts | lock/timeout | in-memory mutex |
| `SH-052 withOptimisticConcurrency` | Platform primitive | Shared persistence infrastructure | reject stale writes where supported | request/job/bundle mutations | retry/merge policy | updated/conflict | ad hoc updatedAt checks scattered |
| `SH-055 runDeadlineExpiration` | Cross-cutting capability | Shared scheduler/queue infrastructure | bundle expiry; future deadlines once approved | scheduled scans | export/request expiry meaning | due work | custom cron |
| `SH-072 hashCanonicalPayload` | Platform primitive | Shared security/cryptography capability | mandatory SH-100 createPrivacyExportArtifact export manifest/integrity; request fingerprints where approved | artifact/idempotency support | canonical input/proof meaning | digest + version | local crypto hash helper |
| `SH-075 encryptSensitiveValue` | Platform primitive | Shared security/cryptography capability | mandatory SH-100 createPrivacyExportArtifact export archive protection; implementation remains gated | artifact generation | export content/expiry | encrypted output/reference | local AES helper |
| `SH-076 normalizeAndHashIdentifier` | Platform primitive | Shared security/cryptography capability | non-plaintext request/IP evidence when required | intake/audit evidence | necessary identifiers/retention | normalized hash | `privacyIpHash` |
| `SH-091 requestSearchProjectionRefresh` | Module public interface | Search / Public Visibility | privacy de-index/update | after owner truth change | privacy reason/action | Search command acknowledgement | `typesenseDelete`, direct SearchUpsertEvent write |
| `SH-087 issueSignedMediaUrl` | Cross-cutting media capability | Media / File Access | short-lived export access | after Privacy access allow | export entitlement/expiry | signed Media URL/access ref | local presign code |
| `SH-070 deleteProviderResource` | Provider-adapter contract | Provider-owning Module | execute authorized external deletion | inside owner executor | Privacy requested disposition only | deleted/absent/retained/retryable/terminal result | R2/Stripe/Mux/etc clients in Privacy |
| `SH-096 enumerateSubjectData` | Cross-cutting protocol | Each data-owning Module through Privacy-defined interface | inventory subject data | scope discovery/export | protocol shape/completeness | target page + cursor | global DB crawler |
| `SH-097 evaluateRetentionRequirement` | Cross-cutting protocol | Data owner supplies facts; Privacy records exemption | determine mandatory retention input | before destructive disposition | exemption recording | required/reason/basis/etc. | tax/legal logic in Privacy |
| `SH-098 anonymizePersonalFields` | Cross-cutting capability | Shared primitive; record owner supplies mapping | preserve required records with reduced personal data | owner execution | acceptable disposition/proof | owner result | global unscoped scrubber |
| `SH-095 executePrivacyInstruction` | Cross-cutting protocol | Privacy orchestrates; each data owner executes | mutate owner-local target | per target | requested action/result mapping | typed disposition | local PrivacyRequest workflow in feature Modules |
| `SH-099 orchestratePrivacyFulfillment` | Module-internal orchestration with public interfaces | Privacy / Data Erasure | own end-to-end request sequence | after approved verification | all Privacy workflow meaning | aggregate workflow result | `deleteUserService` elsewhere |
| `SH-100 createPrivacyExportArtifact` | Cluster-local capability | Privacy owns bundle; Media/storage owns object mechanics | assemble private export | export generation | content/eligibility/expiry | bundle + Media reference | R2/archive delivery stack in Privacy |
| `SH-123 validateOwnedTargetReference` | Shared contract; separate implementations | Target owner | validate target before registration/execution | inventory and execution | Privacy relationship/action | valid/not-found/forbidden/stale | direct cross-Module existence query |
| `SH-032 createRequestContext` / `SH-033 writeStructuredLog` / `SH-034 sanitizeTelemetryMetadata` / `SH-037 recordIntegrationFailure` | Per-operation classification in the canonical registry | Per-operation owner in the canonical registry | correlate and observe safely | all workflows | domain failure state + redaction rules | safe ops evidence | business state in logs |

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
|---|---|---|---|---|---|
| `scopePrivacyRequest` | derive which executor families/request behavior apply | request + approved policy | request scope | none directly | request-type meaning is Privacy policy |
| `discoverAndRegisterTargets` | coordinate inventories and materialize erasure targets | verified erasure request | target set | `DataErasureTarget` | registration/coverage belongs to Privacy |
| `mapOwnerResultToTargetDisposition` | translate normalized executor result into Privacy status | owner result + target | target disposition | `DataErasureTarget` | target-status meaning is Privacy truth |
| `recordRetentionExemption` | convert authoritative owner retention facts into Privacy proof | target + owner facts | exemption | `DataRetentionExemption` | exemption is Privacy proof |
| `reconcileErasureJobOutcome` | aggregate target states into erasure job state | job + targets | job result | `DataErasureJob` | aggregate semantics are Privacy-owned |
| `assembleExportSections` | coordinate owner serializers into one export manifest/archive input | request + owner sections | export assembly input | none/bundle later | export contents are Privacy policy |
| `authorizePrivacyExportDownload` | decide if actor may receive current bundle | actor + bundle | allow/deny + Media ref | none | Privacy owns bundle eligibility |
| `expireExportBundle` | make bundle unavailable after expiry | bundle + time | expired state | `DataExportBundle` | export lifecycle is Privacy-owned |
| `completePrivacyRequest` | set final aggregate request outcome | request + child results | terminal request | `PrivacyRequest` | final right-fulfillment meaning belongs here; decision-gated today |

---

## 17. Shared Mechanism / Separate Truth Rules

### Workflow runner

Privacy may use shared workflow-runner primitives. It must still persist and own `DataErasureJob`/`DataErasureTarget`. A shared `WorkflowRun`, `QueueJob`, or job record cannot replace them.

### Lifecycle state-machine plumbing

A shared transition helper may validate expected current state, execute transactional write, and publish hooks. Privacy supplies the actual transition graph and invariants.

### Idempotency

The platform owns claim/result persistence. Privacy supplies semantic identities such as:

```text
request intake:
actor/subject + request type + submission intent

erasure start:
privacyRequestId + erasure + workflowVersion

target execution:
privacyRequestId + targetType + targetId/externalRef + action + executorVersion

export generation:
privacyRequestId + exportFormat + serializerVersion
```

### Locks

Shared DB locks are mechanisms. Privacy defines request/job/target lock keys and conflict meaning.

### Audit

Generic `AuditEvent`/`AccessAuditLog` writers are shared capabilities. `PrivacyRequest`, target disposition, and retention exemption remain separate Privacy proof.

### Anonymization

A shared versioned scrub/pseudonym primitive may be used by owner executors. Each record owner supplies the exact field map and relational constraints. Privacy does not run a global scrubber over other schemas.

### Provider deletion

All provider adapters may share a result contract. Provider-specific state, dedupe, credentials, and reconciliation remain with the provider owner.

### Search

`SH-091 requestSearchProjectionRefresh` is a Search-owned Module public interface. Search's `SearchUpsertEvent` and provider documents remain Search truth.

SH-091 requestSearchProjectionRefresh acceptance or queue acknowledgement is not proof of completed Search deletion. A Privacy target whose required disposition includes Search removal remains non-successful until Search supplies completion evidence under the approved Privacy executor contract. Accepted/queued work may be recorded as pending operational progress. Location Safety may independently complete its own cache/projection-source mutation. The durable completion receipt, correlation, and acknowledgement representation remain unresolved; this rule does not define that contract.

### Media access

Temporary access uses `SH-088 manageTemporaryAccessGrant` and `SH-089 revokeTemporaryAccessGrant` through Media-owned grant mechanics, alongside canonical signed delivery. `DataExportBundle` remains Privacy truth; `MediaAccessGrant` remains Media truth; Privacy does not transition Media grants locally.

### Events

Transactional outbox/inbox is shared infrastructure. Privacy owns approved event meaning and payload minimization.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

Login/authentication, SH-001 resolveAuthenticatedActor, SH-014 requireStepUpForSensitiveAction, and account-recovery proof are not automatically sufficient Privacy identity verification. Identity owns assurance/proof mechanics; Privacy alone decides whether the approved proof permits its `verified` transition. U-08-01 remains unresolved; no proof shape, assurance level, expiry, or schema representation is approved here.

Every protected public Privacy command/query begins with `SH-001 resolveAuthenticatedActor`.

Anonymous users may not submit or inspect Privacy requests through this Module unless a future root architecture explicitly introduces a pre-auth rights path.

### Resource authorization

Use `SH-002 authorizeResourceAction`.

Privacy supplies contextual facts such as:

- requester owns `PrivacyRequest.userId`;
- requester owns `DataExportBundle.userId`;
- admin/support actor is requesting a named privacy-review action;
- requested operation is view, submit, cancel, review, download, retry, or other approved action.

Role / Authority interprets permission. Privacy does not create a generic role matrix.

### Self-service resource ownership

A normal User may read only their own requests/bundles.

Cross-user resource IDs must follow root anti-enumeration behavior: do not reveal existence to unauthorized actors if the root contract returns not-found semantics.

### Admin/support actions

Admin/support access is action-specific, not blanket access.

Sensitive examples:

- viewing another user's request detail;
- reading retention-exemption notes;
- retrying a target;
- rejecting/cancelling a request;
- issuing/downloading another user's export;
- viewing export generation diagnostics.

`SH-030 recordSensitiveAccess` is required when the Audit policy classifies the action as sensitive.

### Step-up

`SH-014 requireStepUpForSensitiveAction` is canonical, but the evidence does not establish that every Privacy export/admin action requires step-up. Do not add local MFA checks. Consume Identity step-up only after root/Module policy explicitly requires it.

### System/worker authority

Workers use an approved system actor/service identity with least privilege. Service-role database access must be scoped to Privacy-owned repositories and explicit owner interfaces, not generic cross-schema deletion.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying truth owner | Query/interface consumed | Privacy action gated | Privacy-local composition | Result |
|---|---|---|---|---|---|
| requester authentication | Identity & Access | `SH-001 resolveAuthenticatedActor` | all protected intake/read/mutation | actor must be trusted | authenticated/deny |
| resource authority | Role / Authority | `SH-002 authorizeResourceAction` | request/admin/export actions | supply Privacy ownership/action facts | allow/deny |
| identity verification | Identity & Access | approved privacy verification interface | destructive/export/correction/restriction fulfillment as approved | Privacy requires durable proof before transition to `verified` | verified/deny/review |
| owner retention | data owner | `SH-097 evaluateRetentionRequirement` | erase/anonymize decision | Privacy records exemption; never invents owner law | erase/anonymize/retain input |
| ComplianceHold | Admin Review / Compliance Hold | `SH-011 evaluateComplianceHold` only where policy says applicable | specific action only | a hold cannot be presumed to defeat a statutory right | allow/block/review per approved policy |
| consent proof | Consent & Disclosure | `SH-008 queryConsentProof` when evidence must be exported/retained | not a general gate to exercise privacy rights | classify proof as subject data/retention candidate | evidence only |
| Track entitlement | Track Subscription & Entitlement | owner executor/retention interface | no general gate | Track data is itself a target; no premium requirement | no access gating |
| Media access | Privacy + Role, then Media mechanics | `authorizePrivacyExportDownload` + `SH-087 issueSignedMediaUrl` | export delivery | bundle must be ready/unexpired and actor authorized | allow/deny |
| source owner target validity | target owner | `SH-123 validateOwnedTargetReference` | target registration/execution | fail closed on stale/wrong owner | valid/stale/not-found/forbidden |

### Legal gate status

The Module is `mvp_active_legal_gated`. Production enabling of full request semantics requires the unresolved legal/product rules in Section 35 to be approved.

---

## 20. Provider Integrations

### Binding provider rule

Privacy / Data Erasure owns **no provider integration**.

The canonical flow is:

```text
Privacy instruction
→ source/provider-owning Module
→ provider-neutral port
→ provider adapter
→ external provider
→ normalized owner result
→ owner-local source truth
→ typed privacy disposition
→ Privacy target update
```

Examples:

- R2 object → Media / File Access
- Typesense document → Search / Public Visibility
- Daily/Mux/Agora → Video Infrastructure
- Stripe payment/customer reference → Payment / Payout / Tax
- subscription provider reference → Track Subscription & Entitlement
- calendar provider reference → Booking & Calendar

### Credentials

Privacy code does not read provider credentials for those systems.

### Webhooks and provider-event dedupe

Privacy owns no provider-event dedupe record. `ProcessedStripeEvent`, `ProcessedCalendarEvent`, `ProcessedVideoProviderEvent`, and equivalent provider records remain with their owners.

### Status/error translation

Provider errors are translated by the provider owner into the canonical privacy result contract:

```text
deleted/erased
absent/not_found
anonymized
retained
skipped
failed_retryable
failed_terminal
unsupported_action
```

Privacy maps that normalized result to its own target disposition.

### Reconciliation

Provider owners run provider reconciliation. Privacy reconciles **its own targets** against typed owner outcomes and cannot become a generic provider sweeper.

---

## 21. Events and Outbox

### Current binding status

No Privacy event family is currently approved as a binding root contract.

### Proposed event family

Inherited PR-08-03:

```text
privacy.request.submitted
privacy.request.verified
privacy.erasure_job.queued
privacy.target.resolved
privacy.export.ready
privacy.request.completed
```

Before any is emitted:

1. register the event name/version in the root event contract;
2. define the aggregate and source transaction;
3. define minimized payload;
4. define correlation/causation IDs;
5. define consumers;
6. define replay/idempotency expectations.

### Event rules

- Events describe facts already committed.
- Events do not command another Module to mutate its truth.
- Cross-Module commands use explicit public interfaces/protocols.
- Do not include export contents, raw personal data, signed URLs, provider secrets, raw messages/resumes, tax information, or unrestricted admin notes.
- Use `SH-046 publishDomainEvent` through the transactional outbox.
- Consumers use `SH-045 deduplicateDomainEvent`.

### Aggregate/version expectations

When the root envelope supports it, include:

- event ID;
- schema version;
- aggregate type/id;
- aggregate/source version;
- occurredAt;
- correlation ID;
- causation ID;
- actor/system reference;
- minimal reason/result code.

---

## 22. Background Jobs / Scheduled Work

### 22.1 Subject inventory worker

**Purpose:** enumerate owner-held data for a request.

**Input:** request ID, subject ID, executor cursor.

**Owner:** Privacy.

**Idempotency key:** request + owner + inventory protocol/version + cursor.

**Retryable failures:** owner timeout, transient dependency errors.

**Permanent failures:** unknown owner/protocol incompatibility; manual-review decision where required.

**Business truth:** inventory may lead to target registration; dry-run inventory itself is not a target disposition.

**Ops:** bounded page counts, cursor, duration, owner, correlation; no raw target payload.

### 22.2 Erasure target worker

**Purpose:** process one target through retention and owner execution.

**Input:** erasure target ID + request/job correlation.

**Owner:** Privacy orchestrator; source Module executes its effect.

**Idempotency key:** target semantic identity + action + executor version.

**Retryable:** transient owner/provider result.

**Permanent:** unsupported action, approved retention, terminal owner failure, manual review.

**Business truth:** updates `DataErasureTarget` only after normalized result; may create `DataRetentionExemption`.

**Dead-letter:** visible operational state plus target/job remains unresolved/failed according to approved policy; never falsely complete.

### 22.3 Erasure reconciliation worker

**Purpose:** aggregate target results.

**Input:** job ID.

**Owner:** Privacy.

**Idempotency:** job + target-state version/snapshot.

**Retryable:** transient DB/owner-late result.

**Permanent/manual review:** inconsistent target/exemption invariant.

**Business truth:** `DataErasureJob`; `PrivacyRequest` only when aggregate semantics are approved.

### 22.4 Export generation worker

**Purpose:** collect owner export sections and create a private Media-backed bundle.

**Input:** request/bundle ID, export format/version.

**Owner:** Privacy; Media stores artifact.

**Idempotency:** request + format + serializer/export version.

**Retryable:** owner serializer/Media transient failures.

**Permanent:** unsupported serializer, policy gap, failed validation.

**Business truth:** `DataExportBundle`.

### 22.5 Export expiry worker

**Purpose:** expire access and request artifact cleanup.

**Input:** due bundle page or bundle ID.

**Owner:** Privacy for bundle state; Media for object cleanup.

**Idempotency:** bundle + expiry timestamp/version.

**Business truth:** `DataExportBundle.status=expired`.

**Ops:** cleanup failure is observable/retryable without restoring Privacy access.

### 22.6 Stalled/deadline worker

Only implement generic stalled-work detection that does not invent statutory due dates. Automated `dueAt` legal deadlines remain gated by U-08-06.

---

## 23. Concurrency and Idempotency

### Races to prevent

1. duplicate request submission;
2. two workers starting erasure for the same request;
3. duplicate target registration;
4. duplicate target execution;
5. target execution racing cancellation/finalization;
6. two reconciliation workers updating one job;
7. duplicate export generation;
8. export generation racing expiry;
9. repeated owner/provider result delivery;
10. final request completion racing late target results.

### Aggregate/resource lock keys

Use canonical DB-backed locking.

Recommended semantic keys:

```text
PrivacyRequest:
privacy-request:{privacyRequestId}

erasure start:
privacy-erasure-start:{privacyRequestId}

target registration:
privacy-erasure-job:{erasureJobId}

target execution:
privacy-erasure-target:{dataErasureTargetId}

export generation:
privacy-export:{privacyRequestId}:{formatVersion}

bundle expiry:
privacy-export-bundle:{bundleId}
```

These are semantic examples; adapt to root lock-key conventions.

### Transaction boundaries

- request creation + idempotency claim/result: one atomic command boundary;
- job creation + request transition when that transition is approved: one transaction where feasible;
- target status + exemption creation: one Privacy transaction after owner result is received;
- bundle finalization only after Media returns valid artifact reference;
- outbox event record, when approved, is written transactionally with the source state.

Cross-Module provider/network calls do not occur inside long-held database transactions.

### Lock strategy

- prefer Postgres row/advisory locks or serializable transaction through `SH-051 acquireAggregateLock`;
- `SH-052 withOptimisticConcurrency` may use `updatedAt`/version where available;
- `DataErasureTarget` lacks `updatedAt`, so do not pretend CAS exists; row/advisory lock is the safe current mechanism;
- never use in-memory locks for correctness.

### Idempotent replay

A replay must return the original semantic result without repeating owner side effects. Reuse `SH-044 executeIdempotentCommand`; do not create a Privacy-local dedupe table.

### Schema constraints not yet approved

Do not add uniqueness for:

- active Privacy requests;
- one DataErasureJob per PrivacyRequest;
- target fingerprint;
- one DataExportBundle per request;

unless the relevant lifecycle policy is approved. Until then, command idempotency and aggregate locks enforce buildable slices.

---

## 24. Media / Storage

### Business meaning owned here

Privacy owns:

- whether an export should exist;
- whether the bundle is `ready`, `expired`, or `failed`;
- which owner sections belong in the export under approved policy;
- whether an actor may request delivery of the bundle;
- when cleanup must be requested.

### Mechanics owned by Media / File Access

Media owns:

- `MediaAsset`;
- object upload/storage;
- private bucket policy;
- object deletion;
- derivative deletion;
- validation/scanning/processing;
- Media access grants;
- signed URLs;
- original filename/object-key mechanics.

### Export storage rules

- export artifact is private;
- no permanent public URL;
- URL/access token is short-lived;
- re-authorize bundle status/ownership at access time;
- access issuance/download is sensitive and audited;
- artifact content is never browser-assembled from unrestricted APIs;
- expiry must make future URL issuance fail;
- Media cleanup failure does not make bundle accessible again.

### Current schema gap

`DataExportBundle.mediaAssetId` has no explicit Prisma relation.

PR-08-04 remains proposed. Until approved, application code validates the Media reference through Media's public interface; do not silently add cross-owned relational schema.

---

## 25. Search / Projection

### Source truth

Privacy source truth is the request/job/target/exemption/bundle records.

### Privacy-owned projection

None.

### Search-owned projection

Search / Public Visibility owns:

- `SearchUpsertEvent`;
- projection builders/worker mechanics as applicable;
- Typesense provider documents;
- index/de-index/reconciliation.

### Privacy-driven triggers

After an owner executes privacy erasure/restriction/correction that changes public visibility or public-safe data, Privacy or the source owner requests the appropriate Search refresh through `SH-091 requestSearchProjectionRefresh`.

For explicit `typesense_document` targets, Search's privacy executor owns the provider deletion.

### Rule

Privacy owns **why** a privacy action requires Search work. Search owns **how** the projection is changed.

Privacy must never:

- write `SearchUpsertEvent` directly;
- call Typesense;
- treat successful Search deletion as equivalent to owner-data erasure;
- mark a target `erased` while a required Search executor reports failure.

---

## 26. Notification

Privacy owns business triggers and safe message intent; Notification owns delivery.

Potential approved triggers:

- request submitted;
- verification required;
- export ready;
- export failed;
- request completed/partially completed;
- request rejected/cancelled when approved;
- manual action required.

Use `SH-041 requestNotification`.

Payload requirements:

- request ID/reference;
- safe request type/status;
- generic next action;
- no export contents;
- no signed URL;
- no target/provider identifiers unless explicitly safe;
- no raw retention note;
- no raw personal-data field.

Notification failure normally does not rewrite Privacy business truth. It is retried/observed by Notification/Ops.

---

## 27. Audit and Sensitive Access

### Privacy domain truth

- `PrivacyRequest`
- `DataErasureJob`
- `DataErasureTarget`
- `DataRetentionExemption`
- `DataExportBundle`

### Generic AuditEvent

Owned by Audit / Event Ledger. Use `SH-029 appendAuditEvent` for important actions such as:

- request submission;
- admin review action;
- erasure job start;
- retention exemption creation;
- request completion;
- administrative retry/override where approved.

### AccessAuditLog

Owned by Audit / Event Ledger. Use `SH-030 recordSensitiveAccess` for actions such as:

- export URL/access issuance;
- export download;
- sensitive admin inspection;
- protected proof access according to Audit policy.

The Prisma `AccessAuditAction` vocabulary currently includes:

- `privacy_export_generated`
- `privacy_erasure_started`
- `privacy_erasure_completed`

Despite the enum location/name, these records remain Audit-owned proof and do not replace Privacy status.

### No local audit table

Do not create:

```text
PrivacyAuditLog
PrivacyAccessLog
PrivacyEventLog
ErasureAudit
```

unless a future approved architecture establishes a genuinely domain-specific ledger distinct from generic Audit.

---

## 28. Privacy and Retention

This is the owning Module for privacy orchestration, so the responsibility divides into two layers.

### 28.1 Subject-data inventory protocol

Every personal-data-owning Module in scope implements, as applicable:

```text
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
export serialization
```

The target descriptor should contain at minimum:

```text
ownerModule
targetType
targetId or externalRef
subjectId
supportedActions
sensitivity
sourceVersion
retentionCandidate
exportSerializerVersion
```

This is a contract object, not a universal database record. Durable Privacy targets must preserve enough identity to deterministically route and replay the owner operation after restart. `postgres_profile` and `other` do not permit an untyped generic deletion path. Correction/restriction cannot be reported as proven target completion using an erasure-only status that fails to express the disposition. Persistence fields, descriptor snapshots, statuses/result models, and explicit Location target types remain unresolved; no representation is approved here.

### 28.2 Current target-owner map

Current Prisma target types map to explicit owners:

| Target family | Underlying owner |
|---|---|
| `postgres_user` | Identity & Access |
| `postgres_profile` | specific profile owner; ambiguous generic mapping must be resolved by executor descriptor |
| `postgres_message`, `postgres_thread` | Messaging |
| `postgres_notification` | Notification |
| `media_asset`, `r2_object`, Media upload/scan/processing/access/derivative targets | Media / File Access |
| `typesense_document` | Search / Public Visibility |
| `daily_room_or_log`, `mux_asset_or_playback_reference`, `agora_room_or_log`, `course_video_playback_grant` | Video Infrastructure |
| `stripe_customer_reference` | Payment / Payout / Tax |
| `calendar_provider_reference` | Booking & Calendar |
| digital download/event/accessibility targets | Digital Goods Access with Media for bytes |
| agreement record/snapshot/signature/access grant | Transaction / Order with Media for bytes |
| `customer_profile` | Customer / Buyer Profile |
| Track subscription/grant/usage/counter/event/billing/provider targets | Track Subscription & Entitlement |
| `other` | explicit executor owner required; no generic deletion |

Messaging and Notification participate through SH-096 `enumerateSubjectData`, expose owner-side SH-097 `evaluateRetentionRequirement`, and execute approved dispositions through SH-095 `executePrivacyInstruction`. Retention evaluation returns required, reason code, legal/policy basis, retainUntil, minimum fields, permitted anonymization, and source reference under approved policy. Privacy owns `DataRetentionExemption` creation and final workflow completion; it must not directly rewrite CL-07 tables.

**CL-07-R005 — unresolved Privacy target mapping:** inventory must cover `ThreadParticipant`, `MessageMedia`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` as well as Thread, Message, and Notification. How those child records become `DataErasureTarget` entries remains a Privacy-owned architecture decision. Do not silently omit them, invent enum values, select an ad hoc untyped `other` mapping, or assume parent erasure determines every child disposition. Destructive workflows depending on this mapping remain gated until it is approved.

### 28.3 Erase/anonymize/revoke/retain

Privacy chooses the requested privacy action and records the result. The record owner:

- validates its target;
- determines relational-safe action;
- supplies retention facts;
- applies approved field-level anonymization;
- revokes grants/access it owns;
- deletes provider resources through its own adapter;
- returns normalized evidence.

### 28.4 Retention

Privacy records the exemption. Owner examples:

- Transaction / Order → contract/signature facts;
- Payment / Payout / Tax → tax/payment/fraud facts;
- Review / Dispute → dispute facts;
- Audit → security/audit retention facts;
- Consent → consent proof;
- Track → subscription billing history;
- Media → security scan/audit facts;
- Location Safety → safety/security retention once approved.

### 28.5 Privacy-owned records as subject data

The Privacy records themselves contain subject identifiers and may be relevant to access/export/retention. No explicit self-target type or retention policy is currently established.

**Rule:** do not recursively erase `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, or `DataRetentionExemption` as part of the same request without an approved retention/anonymization policy. Do not destroy the evidence required to prove fulfillment.

### 28.6 User final disposition

Hard-delete versus permanent anonymized Identity shell remains U-08-08. Do not cascade-hard-delete `User` as a shortcut.

### 28.7 Backup handling

Backup expiry/removal is U-08-09. Do not represent delayed backup purge as immediate erasure unless approved policy explicitly permits that wording.

---

## 29. Observability

Use canonical:

- `SH-032 createRequestContext`;
- `SH-033 writeStructuredLog`;
- `SH-034 sanitizeTelemetryMetadata`;
- `SH-037 recordIntegrationFailure`;
- `SH-036 emitMetric` for operational counters/timings;
- `SH-038 recordQueueTelemetry` for worker attempts, retries, and outcomes;
- health/incident surfaces through Ops.

### Correlation

Correlation/request IDs must propagate:

```text
web request
→ Privacy command
→ job
→ owner executor
→ provider owner
→ owner result
→ Privacy target
→ audit/notification/search/media effect
```

### Safe dimensions

Permitted examples:

- operation name;
- request type;
- Privacy status;
- target type;
- owner Module;
- normalized result code;
- queue attempt number;
- duration;
- policy/protocol version;
- correlation ID.

Avoid or hash/minimize:

- User ID in broad analytics;
- external provider references;
- IP address;
- object keys.

Never log:

- export contents;
- signed URLs;
- raw message/resume/file content;
- raw provider payloads;
- exact tax/financial data;
- credentials/session tokens;
- full admin notes.

### Operational records

`IntegrationFailure`, `QueueJob`, `SystemEvent`, and `OpsIncident` are supplemental. They never set Privacy status by themselves.

---

## 30. Security Boundaries

1. Validate all public/internal command payloads at runtime.
2. Resolve and authorize protected actors on the server.
3. Treat request/export/admin identifiers as protected resources.
4. Do not trust client-supplied request status, subject identity, target owner, retention basis, or disposition.
5. Service-role workers must be least-privileged and must not perform generic cross-schema deletion.
6. Export artifacts are private and short-lived.
7. Signed URLs/tokens are temporary credentials and are never logged or persisted as Privacy truth.
8. Recheck bundle status, expiry, and actor authorization when issuing access.
9. Use canonical encryption/hashing for SH-100 createPrivacyExportArtifact production exports; other uses follow their approved contracts. Unresolved cryptographic implementation does not make SH-100 createPrivacyExportArtifact protections optional.
10. Provider credentials stay with provider-owning Modules.
11. Target descriptors and event payloads are minimized.
12. `actionTaken`, `failureReason`, `rejectionReason`, and `adminNote` require controlled validation/sanitization and must not store raw provider/subject payloads.
13. Rate limiting uses the root platform rate-limit mechanism once policy is established; do not create a Privacy-only limiter.
14. Cross-Module target references are revalidated by their owners at execution time.
15. Destructive commands are idempotent.
16. Database-backed locks protect lifecycle races.
17. No raw sensitive payload is sent to analytics.
18. Admin/support access is action-specific.
19. No entitlement or consent boolean substitutes for privacy authority.
20. No hard delete is performed merely because a User requested erasure; retention and approved final account disposition must be honored.

---

## 31. Error / Decision Result Pattern

Public interfaces should use the root typed-result/error envelope. At minimum, Privacy needs stable categories equivalent to:

```text
OK
VALIDATION_DENIED
UNAUTHENTICATED
UNAUTHORIZED
NOT_FOUND
CONFLICT
IDEMPOTENCY_CONFLICT
STALE_STATE
DECISION_GATED
POLICY_NOT_CONFIGURED
REQUEST_NOT_VERIFIED
UNSUPPORTED_REQUEST_TYPE
UNSUPPORTED_TARGET_TYPE
OWNER_NOT_REGISTERED
OWNER_UNAVAILABLE
RETENTION_REQUIRED
MANUAL_REVIEW_REQUIRED
DEPENDENCY_RETRYABLE
DEPENDENCY_TERMINAL_FAILURE
EXPORT_NOT_READY
EXPORT_EXPIRED
PARTIAL_COMPLETION
INVARIANT_VIOLATION
```

### Result rules

- Public reason codes are stable and provider-neutral.
- Detailed provider errors remain in owner/Ops diagnostics.
- A dependency timeout does not become `NOT_FOUND`.
- `retained` is not a technical error.
- `partially_completed` is a Privacy lifecycle result once U-08-04 defines its meaning.
- `failed` target/job and generic operational failure remain distinct.
- `decision_gated` is preferable to silently inventing a legal rule.

---

## 32. Testing Architecture

### Domain unit tests

- request type/status policy;
- safe request serialization;
- target descriptor validation;
- target result mapping;
- retention-exemption rules;
- erasure-job aggregation once approved;
- export lifecycle and expiry;
- export access decision;
- reason-code translation.

### State-transition tests

- all currently approved transitions;
- illegal/stale transitions;
- terminal-state protection;
- transition timestamps;
- cancellation/rejection transitions only after policy approval.

### Public contract tests

- `submitPrivacyRequest`
- `getPrivacyRequest`
- `listUserPrivacyRequests`
- `getPrivacyExportStatus`
- `authorizePrivacyExportDownload`
- `SH-096 enumerateSubjectData`
- `SH-097 evaluateRetentionRequirement`
- `SH-095 executePrivacyInstruction`
- owner target validation.

### Database/integration tests

- Prisma persistence/index use;
- request owner isolation;
- idempotent creation;
- job/target/exemption transactional writes;
- bundle finalization;
- lock behavior;
- cascade-safety tests for Privacy proof records.

### Authorization tests

- own request allow;
- cross-user deny;
- admin/support action-specific allow/deny;
- export access cross-user deny;
- no blanket admin export download.

### Compliance tests

- no soft-delete-as-erasure shortcut;
- retained target requires exemption;
- no arbitrary retention reason;
- no guessed `dueAt`;
- no guessed identity verification;
- no guessed cancellation/rejection;
- no hard-delete User shortcut;
- Privacy proof retained according to approved policy.

### Idempotency/concurrency tests

- duplicate submit;
- duplicate erasure start;
- duplicate target registration;
- duplicate target worker;
- concurrent target workers;
- duplicate owner result;
- duplicate export generation;
- generation vs expiry;
- reconciliation vs late target.

### Provider-boundary tests

Privacy should have **no direct provider adapter tests** because it owns none. Instead test normalized executor results from fake/real owner contracts.

### Media/Search/Audit/Notification integration tests

- Media failure prevents false target/bundle success;
- Search request uses Search interface;
- export signed access uses Media;
- sensitive access creates Audit proof;
- notification failure does not corrupt Privacy state.

### Privacy tests

- subject inventory pagination;
- data minimization;
- export serializer omission of prohibited secrets;
- export expires;
- no raw personal data in telemetry;
- Location Safety executor participation once approved;
- Customer/Track target coverage.

### E2E participation tests

1. submit request → history/detail reflects authoritative `submitted`;
2. seeded/approved verified erasure → multi-owner target processing with erased + retained outcomes;
3. verified export → private ready bundle → short-lived access → expiry denial;
4. approved complete semantics → access/correction/restriction/erasure request journeys;
5. representative cross-cluster erasure removes public Search projection through owner contracts.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. Only Privacy / Data Erasure changes `PrivacyRequest` lifecycle truth.
2. Only Privacy / Data Erasure changes `DataErasureJob` lifecycle truth.
3. Only Privacy / Data Erasure records `DataErasureTarget` privacy disposition truth.
4. Only Privacy / Data Erasure owns `DataRetentionExemption`.
5. Only Privacy / Data Erasure owns `DataExportBundle` lifecycle.
6. A source Module executes privacy instructions against its own records; Privacy does not become its repository.
7. A provider-owning Module executes provider deletion; Privacy does not own R2, Typesense, Stripe, Daily, Mux, Agora, Cronofy, or billing clients.
8. A `deletedAt` field is not legal erasure proof.
9. A local `erasedAt` field does not prove the aggregate request is complete.
10. `QueueJob` is operational truth, not `DataErasureJob`.
11. `AuditEvent` and `AccessAuditLog` are generic evidence, not Privacy lifecycle truth.
12. Search is a projection; Privacy never calls Typesense or writes `SearchUpsertEvent` directly.
13. Media owns file/object mechanics and signed URLs.
14. A retained target must have documented Privacy exemption proof.
15. Retention facts must come from the owner of the retained record or approved legal policy; Privacy must not invent them.
16. `DataErasureTargetType.other` cannot trigger a generic delete path.
17. Cross-Module target references are validated through their owner.
18. Privacy request creation is never gated by a paid entitlement.
19. Consent proof is not identity verification and is not general permission to reject a request.
20. No production identity-verification flow is invented before U-08-01 is resolved.
21. No production access-vs-export behavior is invented before U-08-02 is resolved.
22. No correction/restriction completion is claimed before U-08-03 is resolved.
23. No mixed retained-target aggregate result is invented before U-08-04 is resolved.
24. No cancellation/rejection policy is invented before U-08-05 is resolved.
25. `dueAt` is not populated from guessed legal deadlines.
26. Active-request uniqueness is not guessed before U-08-07.
27. `User` is not cascade-hard-deleted as a privacy shortcut before U-08-08.
28. Backup purge is not falsely represented as immediate erasure before U-08-09.
29. Export artifacts are private and short-lived.
30. Signed export URLs are not persisted or logged.
31. Admin/support authority is action-specific and does not imply export-content access.
32. Destructive effects are idempotent and concurrency-safe.
33. Privacy target failure cannot be hidden by successful audit, notification, or Search work.
34. Provider or owner failure cannot be translated into successful erasure.
35. Telemetry must not contain export contents or unnecessary personal data.
36. Proposed rulings are not binding until approved in architecture/progress context.

---

## 34. Prohibited Duplicate Implementations

Do not generate these inside `privacy_data_erasure`:

### Authentication / authority

```text
requireUser.ts
getCurrentUser.ts
privacyAuth.ts
privacyPermissions.ts
adminPrivacyGuard.ts
```

Use `SH-001 resolveAuthenticatedActor` and `SH-002 authorizeResourceAction`.

### Consent / entitlement / holds

```text
privacyConsent.ts
premiumPrivacyAccess.ts
privacyBlocked.ts
privacyHold.ts
```

Use Consent, Track, and ComplianceHold owners where relevant. Privacy rights are not locally premium-gated.

### Audit / observability

```text
PrivacyAuditLog
PrivacyAccessLog
privacy-audit-service.ts
privacy-incident-service.ts
privacy-queue-dashboard.ts
```

Use Audit and Ops.

### Queue / idempotency / locks

```text
privacyQueue.ts
privacyRetry.ts
privacyIdempotency.ts
privacyMutex.ts
privacyLockMap.ts
```

Use canonical shared infrastructure.

### Cross-domain data access

```text
userDataCrawler.ts
gdprDatabaseCrawler.ts
crossModulePrivacyRepository.ts
deleteEveryUserTable.ts
```

Use `SH-096 enumerateSubjectData`, owner validation, and owner executors.

### Provider clients

```text
r2PrivacyDelete.ts
typesensePrivacyDelete.ts
stripePrivacyDelete.ts
dailyPrivacyDelete.ts
muxPrivacyDelete.ts
agoraPrivacyDelete.ts
cronofyPrivacyDelete.ts
billingPrivacyDelete.ts
```

Use provider-owning Modules and `SH-070 deleteProviderResource`.

### Media / Search

```text
privacySignedUrl.ts
privacyPresign.ts
privacySearchDelete.ts
privacySearchIndexer.ts
```

Use Media and Search public interfaces.

### Generic anonymization

```text
scrubEveryTable.ts
globalPiiRemover.ts
anonymizeDatabase.ts
```

Use `SH-098 anonymizePersonalFields` with owner-supplied field maps.

### Competing privacy lifecycles

Do not create:

```text
DeleteUserRequest
GdprRequest
AccountDeletionJob
ErasureWorkflow
UserErasureStatus as independent truth
PrivacyRequestEventLog as generic replacement
```

unless an approved architecture explicitly changes the existing source-of-truth models.

---

## 35. Unresolved Decisions

### Inherited CL-08 privacy decisions

| ID | Question | Why unresolved | Blocks |
|---|---|---|---|
| U-08-01 | What durable proof and Identity interface transitions a request to `verified`? | `verifiedAt` exists but no proof reference/method contract is established. | production fulfillment |
| U-08-02 | What distinguishes `access` from `export`? | both types exist; output semantics are not defined | access request implementation |
| U-08-03 | How are correction and restriction proven per target? | `DataErasureTargetStatus` has no corrected/restricted result | correction/restriction completion |
| U-08-04 | Do lawfully retained targets yield `completed` or `partially_completed`? | aggregate semantics not defined | final erasure/request reconciliation |
| U-08-05 | When may requests be cancelled/rejected and by whom? | statuses exist without policy | cancellation/rejection commands |
| U-08-06 | What jurisdiction/policy/deadline rules populate `dueAt`? | no approved legal policy/version source | automated deadline behavior |
| U-08-07 | Can multiple active/conflicting requests exist for one User? | no uniqueness/concurrency rule | active-request conflict policy/schema |
| U-08-08 | Is the User hard-deleted or retained as an anonymized shell? | Identity relationships/markers exist; final disposition unresolved | final account erasure |
| U-08-09 | How is delayed backup removal represented? | application erasure differs from backup purge | completion wording/proof |
| U-08-22 | How is `DataExportBundle.mediaAssetId` enforced and what manifest/encryption metadata is required? | logical Media reference but no relation/proof fields | export hardening |
| U-08-21 | How long are Location Safety records retained under privacy erasure? | safety proof may require retention | Location executor production policy |
| U-08-23 | Should Location Safety receive explicit `DataErasureTargetType` values? | current enum can only use `other` for location records | first-class Location executor |

### Proposed rulings inherited from CL-08

- **PR-08-01:** Identity-owned User erasure marker fields are projections of Privacy result.
- **PR-08-03:** proposed Privacy domain event family.
- **PR-08-04:** explicit DataExportBundle → Media referential integrity.
- **PR-08-05:** explicit Location Safety privacy target types.

None are binding until approved.

### Module-specific implementation questions requiring resolution or explicit schema review

1. **Durable executor-owner identity:** `DataErasureTarget` does not persist `ownerModule`, while the privacy executor descriptor requires it and `postgres_profile`/`other` can be ambiguous.
2. **Target deduplication:** no target fingerprint/unique constraint exists.
3. **Retry evidence:** target schema has no attempt count, retry state, last-attempt timestamp, or executor version. Generic QueueJob can carry operational retry state, but final proof/replay requirements should be approved before hardening.
4. **One job/bundle semantics:** schema permits multiple erasure jobs and export bundles per request; product/retry semantics need confirmation before uniqueness constraints.
5. **Privacy proof self-retention:** no approved policy defines how long PrivacyRequest/Job/Target/Exemption records are retained or anonymized.
6. **Export completeness behavior:** when one owner serializer fails, whether to fail the whole export or wait/partial is not explicitly approved.
7. **Audit criticality:** root policy must define which privacy actions fail closed if Audit is unavailable.
8. **Admin note/rejection reason schema:** whether free text is acceptable or should be controlled/versioned reason codes is unresolved.
9. **Root event registry:** PR-08-03 cannot be used until event contracts are approved.

**Mechanical registry synchronization completed:** `Contract retention exemptions` is now represented in both `complianceMet` and `complianceSatisfied`, using the existing `DataRetentionExemption` proof record. No retention/lifecycle policy was resolved.

---

## 36. Architecture Decision Summary

### Binding rulings

1. `privacy_data_erasure` is the single owner of formal Privacy request, erasure-job, target-disposition, retention-exemption, and export-bundle truth.
2. Privacy orchestrates; source Modules execute changes to their own records/providers.
3. Privacy defines the cross-Module privacy executor protocol but does not own every executor implementation.
4. Data owners supply retention facts; Privacy records `DataRetentionExemption`.
5. Privacy owns no external provider SDK/client.
6. Media owns storage, object deletion, and signed URLs; Privacy owns `DataExportBundle`.
7. Search owns `SearchUpsertEvent`, Typesense, and projection reconciliation; Privacy requests refresh/removal.
8. Audit owns `AuditEvent` and `AccessAuditLog`; Privacy-owned proof remains separate.
9. Observability owns `QueueJob`, `IntegrationFailure`, and incidents; they do not replace Privacy status.
10. Product deletion and local erasure markers do not complete a Privacy request.
11. Canonical shared operations are mandatory anti-duplication boundaries.
12. Full production semantics remain legal/decision-gated where Section 35 says unresolved.

### Buildable now without inventing policy

Coding agents may implement:

- typed public contracts;
- authenticated request submission/status reads ending at `submitted`;
- executor protocol and dry-run inventory contract tests;
- erasure orchestration against an authoritative verified fixture/result without guessing how verification was obtained;
- target result/retention proof mechanics that do not guess final mixed-outcome request completion;
- export bundle generation for authoritative verified export fixtures using Media interfaces;
- shared-operation integration;
- safe diagnostics/observability/redaction;
- production-disabled policy fixtures;
- schema behavior already directly established by current Prisma.

### Must remain blocked until approved

- real transition to `verified`;
- `access` semantics;
- correction/restriction completion;
- final retained-target aggregation;
- cancel/reject policy;
- legal deadline calculation;
- active-request conflict policy;
- final User hard-delete/anonymized-shell behavior;
- backup completion claims;
- proposed events;
- production export hardening fields/relation where U-08-22 requires them;
- first-class Location Safety disposition where U-08-21/U-08-23 remain unresolved.

---

## 37. Coding-Agent Usage

Before implementing or modifying this Module, read in order:

1. root `context/project-overview-v3.md`;
2. Root architecture is currently missing; stop at any required global decision gap;
3. Root code standards are currently missing; do not invent replacement standards;
4. Canonical Shared Operations Registry;
5. `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`;
6. `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`;
7. this `module-architecture.md`;
8. this Module's `implementation-plan.md`;
9. public-interface sections for every direct dependency used by the current numbered feature;
10. Dedicated progress tracker is currently missing; report blockers/progress in the task completion report.

For erasure/executor work, additionally read the Module architecture/public privacy executor section for every target owner included in the feature.

For export work, additionally read Media / File Access, Audit / Event Ledger, Notification, and the shared crypto interfaces.

For target de-index/provider deletion, read Search or the provider-owning Module rather than adding local provider code.

Before coding, verify:

- the prior Module feature exit gate;
- the corresponding CL-08 feature sequencing;
- all required decision gates;
- canonical shared-operation availability;
- whether any Proposed Ruling has actually been approved.

If a required interface or decision is missing, stop at the contract boundary and record the blocker. Do not replace missing architecture with direct Prisma access, provider calls, local auth/audit/queue helpers, or guessed legal policy.
