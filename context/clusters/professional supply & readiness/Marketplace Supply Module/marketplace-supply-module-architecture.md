# Marketplace Supply Module Architecture

> **Module ID:** `marketplace_supply`  
> **Module name:** Marketplace Supply Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/marketplace_supply/module-architecture.md`  
> **Document status:** Implementation-grade Module architecture. Confirmed rulings are binding; Proposed Rulings require approval before schema/API commitment; Unresolved items must not be invented by implementation.

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `marketplace_supply` |
| Module name | Marketplace Supply Module |
| Module type | `domain` |
| Build status | `mvp_active` |
| Primary Cluster | CL-03 — Professional Supply & Readiness |
| Intended audience | Coding agents, developers, reviewers, maintainers, architecture reviewers |
| Relationship to root architecture | Subordinate to root Workin Ants architecture, code standards, security, persistence, event, privacy, search, audit, observability, and deployment rules. |
| Relationship to Cluster architecture | More authoritative for Marketplace Supply internal truth and policy; subordinate to CL-03 for cross-Module sequencing, collaboration boundaries, and approved shared-operation usage. |
| Update rule | Update this file before or in the same change as any binding Marketplace Supply ownership, lifecycle, public-contract, data-model, privacy, projection, or integration decision. Progress or implementation must not silently redefine it. |

### Evidence classification

- **Confirmed** — directly supported by current registry, schema, glossary/compliance pack, Canonical Shared Operations, Module Architecture Extract, or CL-03 architecture/build plan.
- **Proposed Ruling** — necessary implementation decision strongly supported by evidence but still requiring explicit approval.
- **Unresolved** — evidence is insufficient or conflicting. The affected behavior remains disabled, constrained, or fail-closed until resolved.

### Governing conflict rulings inherited from CL-03

The historical Marketplace Supply registry claims `DigitalGoodsPolicy`, `DigitalDownloadAsset`, `ChildDirectedContentDeclaration`, `MinorPrivacyControl`, `CourseAccessibilityAsset`, and `SalesTaxLineItem`. Stronger current Cluster ownership evidence places digital-goods lifecycle truth in **Digital Goods Access** and sales-tax line-item truth in **Payment / Payout / Tax**. Marketplace Supply may reference those records through public interfaces but must not own or mutate their lifecycles.

The following CL-03 Proposed Rulings materially constrain this Module and are carried forward:

- **PR-05:** Taxonomy owns tag/assignment validity semantics; Marketplace Supply owns attaching/detaching an accepted `OfferingTag` to an Offering.
- **PR-06:** `Offering.priceFromCents` is derived from active `PricingTier` rows or maintained only as a rebuildable projection; it is never independently authored price truth.
- **PR-07:** `Offering.isPublic` is compatibility/projection only; `Offering.isFeatured` is inert until promotion/ranking ownership is resolved.

## 2. Purpose, Goal, and Transformation

### Purpose

Marketplace Supply owns professional-created sellable supply. It provides the authoritative business representation and lifecycle for an `Offering` and its current service/product/course shape, current purchasable pricing, presentation-media context, and contextual taxonomy attachments.

### Goal

Turn a ProfessionalProfile's proposed supply into a structurally valid, lifecycle-controlled Offering that can be safely consumed by publication, Search, checkout, booking, and delivery workflows without absorbing professional eligibility, compliance, provider, payment, delivery, or search truth.

### What enters

- authenticated User/system actor context;
- Role / Authority decision for the requested Offering action;
- source-owner facts proving the controlling `ProfessionalProfile` relationship;
- Offering title, slug, description, kind, currency, and draft configuration;
- kind-specific service/product/course business details;
- current `PricingTier` inputs;
- accepted taxonomy Domain/Category/Tag references validated by Taxonomy;
- ready `MediaAsset` references validated by Media / File Access;
- Professional Eligibility decision for `publish_offering` or other seller action where required;
- Track entitlement, hold, verification, healthcare, moderation, and approved financial decisions indirectly through their owners;
- Digital Goods / Video delivery-readiness facts for product/course publication where applicable;
- Privacy-owned instructions and Moderation-owned enforcement decisions.

### What leaves

- authoritative `Offering` source truth;
- one valid kind-specific business shape for supported service/product/course Offerings;
- current active/inactive PricingTier truth for future purchases;
- `OfferingMedia` and contextual `OfferingTag` attachments;
- Marketplace-owned publication/lifecycle state;
- narrow owner-fact DTOs for Professional Eligibility, Trust, Healthcare, Order, Booking, Digital Goods, Video, and AI Taxonomy consumers;
- privacy-safe source projections for Search;
- versioned Offering domain events and controlled downstream Search/Notification/Audit requests;
- Marketplace-specific Privacy executor results.

### Business transformation

```text
Professional-owned draft intent
→ validate actor + ownership
→ validate Offering-owned shape
→ validate accepted taxonomy + ready media references
→ establish current pricing
→ persist draft Offering truth
→ when publication is requested:
   validate local structure/delivery context
   → consume Professional Eligibility publish decision
   → consume current moderation/hold/public-readiness facts
   → Marketplace alone transitions Offering lifecycle
   → publish owner event
   → build safe source projection
   → request Search refresh
```

### Why this is its own Module boundary

`Offering` has a business lifecycle and mutable supply shape distinct from `ProfessionalProfile`, `Order`, `MediaAsset`, Taxonomy, digital-delivery grants, provider video state, and compliance records. It therefore needs one owner for present-tense supply truth while consuming other owners' decisions through explicit contracts.

## 3. Owned Truth

### 3.1 Models and records owned

| Record | Meaning | Ownership status |
| --- | --- | --- |
| `Offering` | The authoritative sellable supply item created by a ProfessionalProfile. | Confirmed |
| `ServiceDetails` | Service-specific business shape for a service Offering. | Confirmed |
| `ProductDetails` | Product-specific business shape for a product Offering. | Confirmed |
| `CourseDetails` | Course-specific business shape for a course Offering. | Confirmed |
| `PricingTier` | A current purchasable price option for an Offering before downstream transaction snapshotting. | Confirmed |
| `OfferingMedia` | Contextual association and ordering of a ready MediaAsset in Offering presentation. | Confirmed |
| `OfferingTag` row lifecycle | Contextual attachment of an accepted TaxonomyTag to an Offering. Taxonomy still owns tag vocabulary/validity semantics. | Proposed Ruling inherited from CL-03 PR-05 |

### 3.2 Enums and controlled vocabularies owned

- `OfferingKind`: `service`, `product`, `course`, `bundle`.
- `OfferingStatus`: Prisma currently contains `draft`, `active`, `paused`, `under_moderation`, `disabled_by_dmca`, `disabled_by_moderation`, `rejected`, `archived`.
- `ServiceDeliveryMode`: `digital`, `in_person`, `hybrid`.
- `ProductDeliveryMode`: `download`, `external_access`.
- `CourseDeliveryMode`: `self_paced`, `live`, `cohort`, `hybrid`.

`TagSource` is Taxonomy-owned vocabulary even when stored on `OfferingTag`.

### 3.3 Lifecycles owned

Marketplace Supply owns:

- Offering creation and draft lifecycle;
- Offering content/detail updates;
- PricingTier current-state lifecycle;
- Offering presentation-media attachment/order lifecycle;
- contextual Offering tag attachment/detachment lifecycle;
- Offering publication, pause, resume, restriction consequence, restoration consequence, rejection handling when Marketplace-owned policy applies, and archive transitions.

External Modules may decide that a restriction, hold, compliance result, or seller-readiness result exists. They do not write `Offering.status` directly.

### 3.4 Source-of-truth records

- `Offering.status` is the authoritative Offering lifecycle field.
- `Offering.kind` plus the matching detail record defines current business shape.
- `PricingTier` rows define current available purchase options.
- `OfferingMedia` defines presentation-media context; `MediaAsset` remains file truth.
- `OfferingTag` defines attachment context; `TaxonomyTag` remains taxonomy truth.

### 3.5 Domain events and ledgers

Marketplace Supply owns the semantic meaning and payload policy of Offering domain events. It does **not** currently have a confirmed dedicated `OfferingEvent` Prisma ledger. Events are published through SH-046 transactional outbox mechanics.

Proposed stable event family:

- `OfferingCreated`
- `OfferingUpdated`
- `OfferingClassificationChanged`
- `OfferingPricingChanged`
- `OfferingActivated`
- `OfferingPaused`
- `OfferingRestricted`
- `OfferingRestored`
- `OfferingArchived`

Event names/versioning become binding only when introduced by a numbered implementation feature. Generic `AuditEvent` is never a substitute for a domain event stream.

### 3.6 Projections owned

Marketplace Supply may own only source-side, rebuildable projections derived from its own truth:

- `priceFromCents` if retained as a stored minimum-price projection;
- Search source projection produced through SH-094 `buildSourceProjection`.

Marketplace Supply does not own Typesense documents, `SearchUpsertEvent`, provider search schemas, or index execution.

### 3.7 Snapshots / proof owned

No standalone `OfferingPublicationDecision` or `OfferingReadinessSnapshot` source record is confirmed for MVP. Current publication authorization is evaluated from current owner decisions at transition time.

If historical publication-decision proof later becomes legally/product-required, it needs a separate approved ruling defining fields, owner, retention, and relationship to SH-029 generic audit. Implementation must not invent it.

### 3.8 Policies and invariants owned

Marketplace Supply owns the policy that determines whether its own aggregate is structurally valid and which local lifecycle transition follows a permitted external decision. It specifically owns:

- supported kind/detail compatibility;
- minimum local fields required for a draft versus publication;
- pricing validity for current supply;
- whether accepted taxonomy is mandatory for a given local transition;
- whether a ready MediaAsset can be attached in Offering presentation context;
- which Marketplace-controlled status transition is legal from the current status;
- how an external moderation/hold decision maps to an Offering lifecycle consequence;
- what Marketplace fields may enter a public source projection.

It does not own professional, healthcare, verification, financial, entitlement, hold, moderation-case, file-safety, digital-delivery, or Search policy.

## 4. Explicit Non-Ownership

Marketplace Supply must not own or recreate the following:

| Adjacent owner | Responsibility that remains external |
| --- | --- |
| Identity & Access | Authentication, User/session truth, system actor resolution, MFA/step-up lifecycles. |
| Role / Authority | Permission interpretation for resource actions. Marketplace supplies Offering/Profile relationship facts and action vocabulary only. |
| Professional Eligibility | `ProfessionalProfile` lifecycle and action-specific seller readiness, including `publish_offering`. |
| Track Subscription & Entitlement | Seller subscription, feature access, plan, quotas, commission, promotion entitlements, or premium policy. |
| Taxonomy & Classification | Taxonomy Domain/Category/Tag vocabulary, normalization, active-state semantics, assignment validation, and requirement triggers. |
| Trust Verification / Screening | `VerificationRequirement`, `VerificationCheck`, license, background, DMV, FCRA, and TrustBadge truth. |
| Healthcare / Regulated Services | `HealthcareComplianceProfile`, BAA, healthcare data boundaries, and healthcare-specific access policy. |
| Payment / Payout / Tax | Payment rail, KYC, tax, payout, sales-tax calculation, `SalesTaxLineItem`, provider-event truth. |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and reusable stop-sign truth. |
| Content Moderation & Legal Notice | Report, LegalNotice, ModerationCase, ModerationAction decision truth. Marketplace only executes its local lifecycle consequence. |
| Media / File Access | `MediaAsset`, upload sessions, MIME/binary validation, malware scan, metadata scrubbing, storage, derivatives, signed URLs, MediaAccessGrant. |
| Digital Goods Access | `DigitalGoodsPolicy`, `DigitalDownloadAsset`, grants/events, terms acceptance, child-directed controls, accessibility-asset lifecycle. |
| Video Infrastructure | CourseVideoAsset/provider lifecycle, playback policies/grants, Mux/Daily/other provider adapters. |
| Transaction / Order | Order creation/lifecycle, historical transaction snapshot, refunds, agreements, buyer/seller transaction truth. |
| Booking & Calendar | Availability, holds, bookings, scheduling truth. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense client/index workers/query surfaces/reconciliation. |
| Notification | Notification persistence and email/SMS/push delivery. |
| Audit / Event Ledger | Generic `AuditEvent` and `AccessAuditLog`. |
| Observability / Ops | `IntegrationFailure`, `SystemEvent`, `QueueJob`, `OpsIncident`, generic telemetry pipeline. |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob orchestration, DataRetentionExemption lifecycle, legal request completion. |
| AI Taxonomy | AI suggestion/classification run truth and provider integration. Marketplace may expose source context and consume only accepted taxonomy results. |

A foreign-key relation is not permission to bypass these owners.

## 5. Module Architecture Principles

1. **Offering is supply truth.** It is not professional readiness, transaction truth, search truth, file truth, or compliance proof.
2. **Only Marketplace Supply changes Offering lifecycle state.** Other Modules return decisions or send approved enforcement commands.
3. **Drafting and publishing are different gates.** Draft persistence may proceed without completed KYC/verification/healthcare unless an approved policy explicitly gates drafting.
4. **Publication consumes Professional Eligibility.** Marketplace does not reconstruct Trust, Healthcare, Payment, Entitlement, or Hold readiness itself.
5. **Classification is referenced, not copied.** Taxonomy validates IDs and requirements; Marketplace stores contextual attachments.
6. **File context and file mechanics are separate.** `OfferingMedia` is Marketplace truth; `MediaAsset` and signed access are Media truth.
7. **Current price and historical transaction price are separate.** `PricingTier` may change for future purchases; Order snapshots historical values.
8. **`priceFromCents` is derived.** No client or command independently authors it as a source field.
9. **`isPublic` is not lifecycle authority.** Publication uses `Offering.status` plus current owner public-readiness decisions.
10. **`isFeatured` is inert.** No ranking, paid placement, or promotion behavior may be implemented until U-13 is resolved.
11. **Bundles are disabled until modeled.** `OfferingKind.bundle` existing in an enum is not sufficient architecture for bundle composition.
12. **Digital goods remain CL-05 truth.** Marketplace references delivery readiness; it does not grant downloads/playback or own policy records.
13. **Search is downstream projection.** Marketplace builds approved input and calls SH-091; it never writes Search queue rows or Typesense.
14. **Moderation decides; Marketplace executes.** A moderation/legal action cannot directly update Offering tables.
15. **Privacy orchestrates; Marketplace executes.** Archive/delete is not legal erasure.
16. **No direct cross-Module Prisma access by default.** Owner facts come through small public queries/decisions/events.
17. **Shared operations are anti-duplication constraints.** Local wrappers cannot create competing semantics.
18. **Unresolved policy fails closed or remains unavailable.** No coding agent may guess U-01, U-13, U-14, U-15, or U-16 behavior.

## 6. Proposed Folder / Code Structure

The root repository layout remains authoritative. The following is a **Proposed Ruling** consistent with CL-03 organization:

```text
src/modules/marketplace-supply/
  application/
    commands/
      create-offering-draft.ts
      update-offering-core.ts
      upsert-service-details.ts
      upsert-product-details.ts
      upsert-course-details.ts
      manage-pricing-tier.ts
      manage-offering-media.ts
      manage-offering-tags.ts
      request-offering-publication.ts
      pause-offering.ts
      resume-offering.ts
      archive-offering.ts
      apply-offering-restriction.ts
      restore-offering.ts
    queries/
      get-offering-management-view.ts
      get-public-offering.ts
      get-offering-eligibility-context.ts
      get-offering-checkout-snapshot.ts
      get-offering-delivery-requirements.ts
    services/
      offering-application-service.ts

  domain/
    policies/
      offering-shape-policy.ts
      offering-pricing-policy.ts
      offering-publication-policy.ts
      offering-transition-policy.ts
      offering-projection-policy.ts
    types/
      offering-errors.ts
      offering-reason-codes.ts
      offering-events.ts

  contracts/
    public-commands.ts
    public-queries.ts
    owner-facts.ts
    source-projection.ts
    privacy-executor.ts

  infrastructure/
    repositories/
      marketplace-supply.repository.ts

  events/
    handlers/
      professional-readiness-changed.ts
      taxonomy-requirements-changed.ts
      moderation-decision-received.ts
      delivery-readiness-changed.ts

  workers/
    reevaluate-offering-publication-state.ts

  privacy/
    enumerate-marketplace-subject-data.ts
    execute-marketplace-privacy-instruction.ts
    marketplace-retention-facts.ts

  components/
    # only if root UI organization permits Module-local components
    offering-editor/
    offering-readiness/

  tests/
    unit/
    integration/
    contract/
    concurrency/
    privacy/
```

Do **not** create `providers/` under Marketplace Supply for R2, Typesense, Stripe, Bedrock, Mux, or tax providers. Marketplace Supply owns no direct provider integration in the current architecture.

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / UI | Offering editor interactions, pricing/media/tag management UI, publish/readiness display using safe owner reason codes. | Permission logic, readiness reconstruction, provider calls, Search writes, raw compliance/provider data. |
| Application commands | Validated use-case orchestration, owner repository writes, shared-operation calls, transaction boundaries. | Foreign repositories or another Module's lifecycle mutations. |
| Application queries | Marketplace-owned source reads and narrow DTO construction. | Cross-domain joins that reconstruct other Modules' truth. |
| Domain policy | Offering shape, pricing, local transition, local publication prerequisites, source projection allowlist. | Professional/Trust/Healthcare/Payment/Taxonomy/Moderation policy. |
| Repository/data access | Prisma access to Marketplace-owned models and minimal relation IDs needed to preserve referential integrity. | Direct lifecycle mutation of foreign records; generic polymorphic repositories. |
| Events | Marketplace event semantics and consumer handlers that reevaluate current Marketplace truth. | Generic event bus/outbox infrastructure or AuditEvent truth. |
| Workers | Marketplace-specific re-evaluation of affected Offerings. | Generic queue/retry/dead-letter framework, Search index worker, provider reconciliation. |
| Adapters | None currently owned. | R2, Typesense, Mux, Stripe, Bedrock, notification-provider, tax-provider clients. |
| Contracts | Public Marketplace commands/queries/events, owner facts, source projection, privacy executor. | Universal platform interfaces that belong in canonical shared operations. |
| Privacy | Owner-specific enumeration, anonymization mapping, local execution/retention facts. | PrivacyRequest/DataErasureJob/retention-exemption lifecycle. |

## 8. Data Model

### 8.1 `Offering`

**Purpose:** authoritative sellable supply aggregate root.

**Key relationships:**

- belongs to one `ProfessionalProfile`;
- references one TaxonomyDomain and optional TaxonomyCategory;
- has zero/one `ServiceDetails`, `ProductDetails`, `CourseDetails` rows in the physical schema, but the accepted business state must match `kind`;
- has many PricingTiers, OfferingMedia, OfferingTags, and Orders;
- physically relates to digital-goods and sales-tax records owned by other Modules.

**Authoritative fields:** `id`, `kind`, `slug`, `title`, `summary`, `description`, `status`, `professionalProfileId`, `domainId`, `categoryId`, `currency`, and owner-controlled lifecycle timestamps where their semantics are approved.

**Compatibility/projection fields:**

- `priceFromCents` — derived, never independent source truth;
- `isPublic` — compatibility/projection only;
- `isFeatured` — inert/unresolved;
- `requiresHealthcareCompliance` — trigger/snapshot convenience only, never healthcare proof;
- `dataSensitivity` — contextual classification hint, not a substitute for HealthcareDataBoundary.

**Lifecycle field:** `status`.

**Uniqueness:** `@@unique([professionalProfileId, slug])`.

**Concurrency-sensitive:** `status`, kind/details, classification, pricing, restriction timestamps, and any publish-affecting field. `updatedAt` exists; exact version/CAS strategy must use SH-052 or a root-approved equivalent.

**Retention/privacy:** archive is not erasure. Orders may require commercial records to remain. Privacy executor must consult retention facts before destructive action and remove Search projection separately.

### 8.2 `ServiceDetails`

**Purpose:** business shape for a service Offering.

**Key fields:** `deliveryMode`, `durationMinutes`, `minStartDelayDays`, `bookingBufferMin`.

**Relationship:** one-to-one by `offeringId` primary key.

**Invariants:** accepted only for `Offering.kind=service`; time values must be nonnegative and internally valid. Booking/availability truth remains Booking-owned.

### 8.3 `ProductDetails`

**Purpose:** business shape for a product Offering.

**Key fields:** `deliveryMode`, optional legacy `fileAssetId`, optional `externalUrl`.

**Relationship:** one-to-one by `offeringId`; may reference MediaAsset and DigitalDownloadAsset records.

**Boundary:** `fileAssetId` is not sufficient paid-download architecture. Downloadable products use Digital Goods Access records/decisions; Marketplace must not issue permanent download URLs or own grants.

### 8.4 `CourseDetails`

**Purpose:** business shape for a course Offering.

**Key fields:** `deliveryMode`, `courseLengthMinutes`, `lessonCount`, `startsAt`, `endsAt`, `enrollmentLimit`, `externalUrl`, `accessExpiresAfterDays`.

**Relationships:** one-to-one by `offeringId`; references Video and Digital Goods/Accessibility records owned elsewhere.

**Invariants:** date ranges and positive limits/durations must be validated; required course video/delivery/accessibility readiness is consumed through owner contracts before publication.

### 8.5 `PricingTier`

**Purpose:** current purchasable option for future Offering purchases.

**Key fields:** `name`, `description`, `priceCents`, `currency`, `displayOrder`, `isActive`.

**Relationship:** many-to-one with Offering; referenced by Payment-owned SalesTaxLineItems.

**Invariants:** price must be nonnegative and currency must match Marketplace pricing policy; historical Order prices are not rewritten when a tier changes.

**Concurrency:** create/update/deactivate/reorder operations should be transactional when combined; duplicate/replayed commands must be idempotent where appropriate.

### 8.6 `OfferingMedia`

**Purpose:** presentation context/order for MediaAsset.

**Primary key:** composite `(offeringId, mediaId)` prevents duplicate attachment.

**Boundary:** attachment requires Media-owned ready/valid asset decision. Deleting OfferingMedia must not silently delete MediaAsset unless a separate Media/Privacy instruction requires file deletion.

### 8.7 `OfferingTag`

**Purpose:** contextual accepted tag attachment.

**Primary key:** composite `(offeringId, tagId)`.

**Fields:** `source`, `confidence`, `verified`, `createdAt`.

**Boundary:** Taxonomy validates tag existence, hierarchy, active state, normalization, and assignment compatibility. Marketplace owns attach/detach row lifecycle only under PR-05.

### 8.8 Physically related but externally owned records

Marketplace code may not treat the following relations as write authority:

- DigitalGoodsPolicy / DigitalDownloadAsset / DigitalGoodsTermsAcceptance / ChildDirectedContentDeclaration / MinorPrivacyControl / CourseAccessibilityAsset — Digital Goods Access;
- SalesTaxLineItem — Payment / Payout / Tax;
- CourseVideoAsset — Video Infrastructure;
- Order — Transaction / Order;
- MediaAsset — Media / File Access;
- Taxonomy Domain/Category/Tag — Taxonomy & Classification.

## 9. Enums, Statuses, and Lifecycles

### 9.1 OfferingKind

Supported implementation scope:

```text
service → ServiceDetails required
product → ProductDetails required
course  → CourseDetails required
bundle  → enum exists, creation/publication disabled until U-15 is resolved
```

For supported kinds, contradictory detail rows are invalid accepted state. Exact database enforcement may combine application transaction checks and schema constraints available under Prisma/PostgreSQL.

### 9.2 OfferingStatus lifecycle

Prisma vocabulary:

```text
draft
active
paused
under_moderation
disabled_by_dmca
disabled_by_moderation
rejected
archived
```

#### Confirmed safe transition families

```text
draft --requestOfferingPublication + current allow--> active
active --pauseOffering--> paused
paused --resumeOffering + full current gate reevaluation--> active
active|paused|restricted --archiveOffering when policy permits--> archived
active|paused|draft --approved moderation action--> under_moderation / disabled_by_moderation / disabled_by_dmca
restricted --approved restoration + full current gate reevaluation--> active or paused according to approved restore policy
```

#### Transition authority

Marketplace Supply is the only writer of `Offering.status`. Professional Eligibility, Hold, Moderation, Healthcare, Verification, or Search may supply decisions but do not write the row.

#### Unresolved lifecycle details

The source set does not fully establish:

- exact adjacency among `under_moderation`, `disabled_by_moderation`, and `disabled_by_dmca`;
- whether `rejected` is terminal, editable, or resubmittable;
- whether archive can be reversed;
- whether every moderation state can originate from draft as well as active;
- canonical restoration target state after a temporary restriction.

A feature specification must settle only the transitions it implements. Unsupported transitions return a stable conflict/unsupported result.

#### Concurrency expectations

Publish, resume, moderation restriction, restore, archive, and publish-affecting edit operations must use SH-051/SH-052/SH-053 as appropriate. A stale publication command cannot overwrite a newer moderation restriction.

#### History proof

- SH-046 domain event/outbox for reliable downstream reaction;
- SH-029 generic audit where policy requires proof;
- Moderation's case/action remains source decision proof for restriction;
- no invented `OfferingEvent` ledger until explicitly approved.

### 9.3 PricingTier lifecycle

There is no status enum; `isActive` controls current availability. Marketplace owns create/update/deactivate/reorder. Physical deletion should be avoided when downstream historical references require retention; Orders own their own immutable snapshots.

## 10. Commands

The following are Module-owned mutations. Exact transport (server action/API/application call) follows root conventions.

### `createOfferingDraft`

- **Purpose:** create a draft Offering for a ProfessionalProfile.
- **Actor/context:** authenticated actor; controlling ProfessionalProfile owner facts; Role / Authority allow.
- **Inputs:** kind, slug, title, optional copy, domain/category, currency, optional initial details.
- **Preconditions:** supported kind; canonical taxonomy IDs; unique `(professionalProfileId, slug)`; bundle disabled until U-15.
- **Writes:** Offering and optionally one kind detail record in one transaction.
- **Shared operations:** SH-001, SH-002, SH-023, SH-044, SH-046.
- **Effects:** `OfferingCreated` outbox event where consumers require it; SH-029 if root audit policy requires.
- **Idempotency:** required for replay-prone create routes; semantic key binds professional + request identity.
- **Failure modes:** validation, forbidden, duplicate slug, unsupported bundle, stale/dependency error.

### `updateOfferingCore`

- **Purpose:** update Marketplace-owned descriptive/current classification fields.
- **Preconditions:** owner authority; non-archived; expected version/current state; Taxonomy validation when classification changes.
- **Writes:** Offering only.
- **Shared operations:** SH-001, SH-002, SH-023, SH-052, SH-046.
- **Effects:** update/classification event; Search refresh only if already public and changed fields affect public projection.
- **Failure:** stale write, invalid taxonomy, restricted field/state.

### `changeOfferingKind`

- **Purpose:** change kind only while policy permits, keeping one consistent detail shape.
- **Preconditions:** normally draft-only until later ruling; no unsupported bundle; downstream delivery references compatible.
- **Writes:** Offering.kind and detail records transactionally.
- **Shared operations:** SH-001, SH-002, SH-051/052, SH-053 when lifecycle interaction exists.
- **Failure:** non-draft conflict, incompatible external references, unsupported kind.

### `upsertServiceDetails` / `upsertProductDetails` / `upsertCourseDetails`

- **Purpose:** manage the correct kind-specific business shape.
- **Preconditions:** Offering.kind matches command; authority; expected version.
- **Writes:** corresponding detail row only plus updated aggregate timestamp as appropriate.
- **Shared operations:** SH-001, SH-002, SH-052.
- **Failure:** kind mismatch, invalid values, stale edit.

### PricingTier commands

`createPricingTier`, `updatePricingTier`, `deactivatePricingTier`, `reorderPricingTiers`:

- validate price/currency/display fields;
- never mutate historical Order truth;
- recalculate/read derived minimum price according to PR-06;
- use SH-001/002, SH-044 where replay-prone, SH-052, SH-046;
- Search refresh only if active public price projection changes.

### OfferingMedia commands

`attachOfferingMedia`, `detachOfferingMedia`, `reorderOfferingMedia`:

- attachment uses SH-090 `attachValidatedMedia` and Media owner readiness;
- Marketplace writes `OfferingMedia` only;
- duplicate composite key returns idempotent/no-op result where semantically same;
- no local upload, scan, R2, or signed URL code.

### OfferingTag commands

`attachOfferingTag`, `detachOfferingTag`:

- validate through SH-023 before attachment;
- Marketplace writes contextual join under PR-05;
- never create/normalize TaxonomyTag locally;
- classification changes may trigger publication re-evaluation and Search refresh if public.

### `requestOfferingPublication`

- **Purpose:** transition a structurally valid draft to active after current external gates permit it.
- **Actor/context:** authenticated controlling Professional/admin actor.
- **Inputs:** Offering ID, expected version/status, idempotency key.
- **Preconditions:** U-01 resolved for `publish_offering`; local shape/pricing/classification/media/delivery checks pass; SH-016 allows; current moderation/hold/public readiness allows; bundle unsupported.
- **Writes:** `Offering.status=active` and approved lifecycle timestamps only.
- **Shared operations:** SH-001, SH-002, SH-005 where Marketplace action itself needs entitlement, SH-011, SH-016, SH-024, SH-044, SH-051/052/053, SH-046, SH-094, SH-091, SH-041, SH-029 as required.
- **Effects:** owner event; Search refresh; safe notification request; audit request.
- **Idempotency:** repeated same publish command returns canonical committed result; conflicting semantic retry returns conflict.
- **Failure:** blocker decision, dependency unavailable, concurrent restriction/edit, unresolved U-01, unsupported bundle.

### `pauseOffering`

Owner-initiated temporary non-public lifecycle change. Uses auth, expected state, transition policy, domain event, Search refresh, and optional notification. It must not create a ComplianceHold or moderation case.

### `resumeOffering`

Re-evaluates **all current publication gates**. A stale prior allow result is never reused. Concurrency behavior matches publication.

### `archiveOffering`

Ends ordinary publication/new-sale behavior while preserving legally/commercially retained records. Archive is not privacy erasure. Search removal is requested through SH-091.

### `applyOfferingRestriction`

- accepts a typed SH-103 Moderation/Legal/Hold source decision envelope;
- validates target/version/action source;
- maps approved external decision to Marketplace lifecycle consequence;
- writes Offering status/timestamps only;
- emits restriction event and Search removal request;
- does not create or adjudicate ModerationCase/LegalNotice/ComplianceHold.

### `restoreOffering`

Requires an approved restoration/release source decision and full current publication re-evaluation before public restoration. Exact restore target status remains transition-policy specific.

## 11. Queries / Decisions

### `getOfferingManagementView`

- **Consumers:** professional editor/admin surface.
- **Input:** Offering ID + actor context.
- **Result:** Marketplace-owned aggregate plus safe owner references/ready-state summaries obtained through public interfaces where required.
- **Type:** source truth/contextual facts.
- **Must not imply:** that external compliance/provider records are Marketplace truth.

### `listProfessionalOfferings`

Returns paginated Marketplace-owned Offerings for a ProfessionalProfile subject to authority, including draft/restricted state where permitted.

### `getPublicOfferingBySlug`

Returns a public-safe Offering only when Marketplace lifecycle/public-readiness policy allows. It must not use `isPublic=true` alone. Search may point to this source but does not determine truth.

### `getOfferingEligibilityContext`

Narrow owner-fact DTO for Professional Eligibility/Trust/Healthcare/Taxonomy consumers. Expected fields may include Offering ID/version, professionalProfileId, kind, canonical classification IDs, delivery mode, Marketplace status, and sensitivity/trigger hints. It must not expose private copy/media/provider data unnecessarily.

### `getOfferingCheckoutSnapshot`

- **Consumer:** Transaction / Order.
- **Result:** current source facts needed for Order creation: Offering ID/version, professionalProfileId, selected PricingTier ID/current price/currency, kind, and approved display/fulfillment references.
- **Type:** source truth input for downstream snapshot.
- **Must not imply:** Order can reread this later as historical price truth; Order owns the transaction snapshot.

### `getOfferingDeliveryRequirements`

Returns service/product/course business delivery requirements to Booking, Digital Goods, or Video owners without granting them Marketplace write authority.

### Marketplace implementation of SH-024 `evaluatePublicReadiness`

Marketplace returns whether its **own source truth** is locally eligible for a requested public surface, using Offering status/local shape and owner-issued external decisions. Search composes but does not reconstruct this policy.

Stable reason namespaces should remain Marketplace-owned and safe, for example:

- `offering.invalid_shape`
- `offering.pricing_missing`
- `offering.taxonomy_invalid`
- `offering.media_not_ready`
- `offering.delivery_not_ready`
- `offering.professional_not_ready`
- `offering.hold_active`
- `offering.moderation_restricted`
- `offering.bundle_unsupported`
- `offering.policy_unresolved`

Reason-code details must not leak sensitive verification, financial, or healthcare data.

### SH-123 owner implementation `validateOwnedTargetReference`

Marketplace may expose a narrow target validation query for Trust/Healthcare/Moderation to confirm that an Offering exists, current version/status, and whether the requested relationship type is allowed. It does not expose a generic repository.

## 12. Public Module Interface

### Public commands

- `createOfferingDraft`
- `updateOfferingCore`
- `changeOfferingKind` for supported states only
- `upsertServiceDetails`
- `upsertProductDetails`
- `upsertCourseDetails`
- `createPricingTier`
- `updatePricingTier`
- `deactivatePricingTier`
- `reorderPricingTiers`
- `attachOfferingMedia`
- `detachOfferingMedia`
- `reorderOfferingMedia`
- `attachOfferingTag`
- `detachOfferingTag`
- `requestOfferingPublication`
- `pauseOffering`
- `resumeOffering`
- `archiveOffering`
- `applyOfferingRestriction`
- `restoreOffering`

### Public queries / decisions

- `getOfferingManagementView`
- `listProfessionalOfferings`
- `getPublicOfferingBySlug`
- `getOfferingEligibilityContext`
- `getOfferingCheckoutSnapshot`
- `getOfferingDeliveryRequirements`
- Marketplace implementation of SH-024 `evaluatePublicReadiness`
- Marketplace implementation of SH-123 `validateOwnedTargetReference`
- SH-094 source projection builder contract

### Emitted domain events

Marketplace-owned versioned Offering lifecycle/change events through SH-046. Events contain safe identifiers, source version, correlation/causation IDs, and minimal changed-field/reason context required by consumers.

### Privacy executor

- SH-096 `enumerateSubjectData` implementation for Marketplace-owned records;
- SH-097 `evaluateRetentionRequirement` owner facts;
- SH-095 `executePrivacyInstruction` implementation;
- SH-098 field-anonymization primitive where applicable.

### Provider-facing interfaces

None. Marketplace Supply owns no current direct provider integration or webhook route.

## 13. Inbound Dependencies

| Owning Module / capability | Public operation consumed | Why required | Minimum information needed | Can block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | Trusted actor for every protected command/query. | actor ID/type/session assurance | Yes | session/current-user helper |
| Role / Authority | SH-002 `authorizeResourceAction` | Decide if actor may act on Offering/Profile context. | action, resource ID, owner facts | Yes | Offering RBAC engine |
| Professional Eligibility | SH-016 `evaluateProfessionalReadiness` | Seller `publish_offering` decision and other approved actions. | professionalProfileId, action, immutable Offering gate context | Yes | eligibility reconstruction |
| Track Subscription & Entitlement | SH-005 `resolveEntitlement` | Seller access/perk if Marketplace action explicitly consumes entitlement. | actor/track, typed key, evaluation time | Yes where policy says so | premium/seller-plan flags |
| Taxonomy & Classification | SH-023 `validateTaxonomyAssignment`; SH-022 `resolveTaxonomyRequirements` | Canonical classification and triggered requirement context. | domain/category/tag IDs, entity type/version | Yes for required classification/publication | local taxonomy cleaner/map |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | Reusable stop signs. | target/action | Yes | `offeringBlocked` flag/table |
| Media / File Access | SH-090 `attachValidatedMedia`; SH-087 for protected reads if needed | Ready asset validation and signed-access mechanics. | asset ID/context/actor | Yes for required media | upload/scanner/R2/signed URL |
| Digital Goods Access | owner delivery-readiness query | Downloadable product/course policy, asset, child-directed, accessibility readiness. | Offering/product/course IDs and mode | Yes for digital publication | DigitalGoodsPolicy/DownloadAsset/grants |
| Video Infrastructure | owner course-video readiness query | Course asset/provider readiness. | Offering/course IDs and expected usage | Yes for required video | Mux/provider/playback state |
| Content Moderation & Legal Notice | SH-103 `executeModerationDecision` envelope / current restriction facts | Enforce external moderation/legal decisions. | action/case/source IDs, target/version, reason | Yes | moderation case/legal lifecycle |
| Notification | SH-041 `requestNotification` | Deliver approved lifecycle alerts. | template/event intent, recipient refs, safe variables | No to committed truth unless root criticality says otherwise | email/SMS/push clients |
| Audit / Event Ledger | SH-029 `appendAuditEvent`; SH-030 only if a Marketplace protected access case requires it | Generic action/access proof. | safe actor/action/resource metadata | Per root criticality | local audit log |
| Search / Public Visibility | SH-091 `requestSearchProjectionRefresh` | Index/update/hide/remove/restore public projection. | entity type/ID/action/reason/source version/idempotency | No rollback of committed source truth on transient Search failure | SearchUpsertEvent/Typesense |
| Privacy / Data Erasure | SH-095/096/097 protocol | Legal privacy fulfillment. | subject/target instruction and retention context | Destructive action may be blocked/retained | Privacy workflow |
| Platform event/job primitives | SH-044–053, SH-047/048 | Idempotency, event reliability, locks/CAS/state transitions, retries. | command/event/job identity | Yes | custom infra |
| Observability / Ops | SH-034/037/038 | Safe diagnostics/job telemetry. | correlation IDs, safe dimensions | No business truth replacement | local incident/job tables |

Marketplace should normally consume verification, healthcare, and financial detail **indirectly through SH-016 Professional Eligibility for publish policy**. It may call owner-specific readiness queries directly only when Marketplace owns a distinct local context decision not already composed by SH-016 and the Cluster architecture explicitly allows it.

## 14. Outbound Consumers and Effects

| Consumer | What it consumes | Marketplace effect / event |
| --- | --- | --- |
| Transaction / Order | Current Offering/PricingTier source facts. | `getOfferingCheckoutSnapshot`; no Order writes. |
| Search / Public Visibility | Safe source projection and public-readiness decision. | SH-094 + SH-091 after lifecycle/public field changes. |
| Booking & Calendar | Service delivery duration/mode/buffer. | `getOfferingDeliveryRequirements`; no Booking writes. |
| Digital Goods Access | Product/course context for delivery policy and grants. | Owner-fact query/events; no Digital Goods writes. |
| Video Infrastructure | Course context and expected content relationship. | Owner-fact query/events; no Video writes. |
| Professional Eligibility | Offering context for `publish_offering`. | `getOfferingEligibilityContext`. |
| Trust Verification / Screening | Offering target/classification context. | SH-123 / owner-fact DTO. |
| Healthcare / Regulated Services | Offering target/sensitivity/classification context. | SH-123 / owner-fact DTO. |
| AI Taxonomy | Offering content/current accepted classification for suggestion runs. | Safe source DTO/event only. AI does not write accepted taxonomy directly. |
| Media / File Access | OfferingMedia contextual relationship. | Contextual entitlement facts only. |
| Content Moderation | Target validation/context. | SH-123 owner reference; moderation commands later come through SH-103. |
| Notification | Business event intent. | SH-041 request after committed owner event. |
| Privacy | Owned data inventory/execution. | SH-096/095/097 responses. |

Marketplace never mutates these consumers' source records directly.

## 15. Canonical Shared Operations Used

Only operations relevant to Marketplace Supply are listed.

| Canonical operation | Classification / owner | Marketplace use | Invocation point | Local policy retained | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Platform capability — Identity & Access | Establish trusted actor. | Every protected entry point. | Requested action/target. | typed actor context | `marketplaceAuth.ts`, `offeringAuth.ts` |
| SH-002 `authorizeResourceAction` | Cross-cutting — Role / Authority | Permission decision. | Before protected read/write. | Offering/Profile relationship facts, action names. | allow/deny + safe reason | local RBAC/isAdmin helper |
| SH-003 `queryOwnerFacts` | Proposed shared contract — source owner | Small foreign owner DTO where approved. | Cross-Module target lookup. | Exact Marketplace facts exposed. | minimal typed DTO | generic cross-domain repository |
| SH-005 `resolveEntitlement` | Platform commercial policy — Track | Seller feature/perk where Marketplace action needs it. | Draft/publish/promotion only when policy says so. | Effect on local action. | typed entitlement/evidence | `sellerPlanCheck.ts`, premium boolean |
| SH-011 `evaluateComplianceHold` | Cross-cutting — Hold | Reusable stop-sign decision. | Hold-sensitive transitions. | Local Offering consequence. | active applicable holds/reasons | `offeringHold.ts`, blocked flag |
| SH-016 `evaluateProfessionalReadiness` | Module public interface — Professional Eligibility | Seller publish/action readiness. | Publication/resume. | Marketplace local shape still separate. | decision/reasons/evidence | `offeringEligibility.ts` reconstructing Trust/Payment/etc. |
| SH-022 `resolveTaxonomyRequirements` | Module public interface — Taxonomy | Trigger context. | Classification/publication. | Whether local transition requires classification. | requirement refs | hardcoded compliance categories |
| SH-023 `validateTaxonomyAssignment` | Module public interface — Taxonomy | Validate IDs/compatibility. | Create/update/tag attach. | Local mandatory classification policy. | normalized IDs/errors | local tag normalizer/taxonomy copy |
| SH-024 `evaluatePublicReadiness` | Shared contract/separate policy | Marketplace-owned public visibility decision. | Publication/source projection. | Offering lifecycle/local shape. | allow/deny/review + reasons/version | Search reconstructing policy |
| SH-029 `appendAuditEvent` | Audit capability — Audit/Event Ledger | Generic important-action proof. | Publish/restrict/admin/privacy actions per policy. | Which Marketplace action requires proof. | audit receipt | `offeringAudit.ts` table/writer |
| SH-034 `sanitizeTelemetryMetadata` | Observability payload capability | Strip sensitive metadata. | Before logs/metrics/error records. | Marketplace field allowlist. | sanitized metadata | raw Offering/provider dumps |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Operational dependency failure visibility. | Search/owner-contract/job failures. | Marketplace impact/correlation. | ops record | local integration-failure table |
| SH-038 `recordQueueTelemetry` | Queue/Ops infrastructure | Worker attempt/dead-letter telemetry. | Re-evaluation worker. | Job completion meaning. | telemetry receipt | custom worker ledger |
| SH-041 `requestNotification` | Notification interface | Deliver lifecycle alerts. | After owner event/decision. | Source meaning + safe variables. | delivery request ID/status | SES/SMS/push client |
| SH-044 `executeIdempotentCommand` | Platform primitive | One effect per replayed command. | Create/publish/restrict/attachments as needed. | semantic fingerprint/conflict policy. | replay/canonical result | local idempotency map/table |
| SH-045 `deduplicateDomainEvent` | Platform event inbox | Prevent repeated consumer side effects. | Dependency-change handlers. | Handler identity/local effect. | claimed/replay result | processed-event boolean |
| SH-046 `publishDomainEvent` | Platform outbox | Reliable Marketplace events. | Same transaction as authoritative write. | Event vocabulary/payload. | outbox event ID | emit-after-write helper |
| SH-047 `enqueueReliableJob` | Shared queue | Durable re-evaluation work. | Dependency-change propagation. | Payload/business completion. | durable job ID | `offeringQueue.ts` |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform | Bounded retry. | Worker transient failures. | Retryability classification. | retry/dead-letter outcome | custom infinite retry loop |
| SH-051 `acquireAggregateLock` | Shared persistence | Serialize critical lifecycle races. | Publish/restrict/restore when needed. | Lock key/conflicting actions. | lock acquisition result | in-memory mutex |
| SH-052 `withOptimisticConcurrency` | Shared persistence | Reject stale edits/transitions. | Mutable aggregate commands. | conflict/merge policy. | success/stale conflict | last-write-wins writes |
| SH-053 `transitionLifecycleState` | Shared mechanism/separate truth | Reuse transition plumbing. | Offering lifecycle commands. | Marketplace transition graph/reasons. | applied/denied transition | global status policy table |
| SH-087 `issueSignedMediaUrl` | Media capability | Protected Offering media access where needed. | Authorized read. | Business entitlement/context. | short-lived URL/access evidence | R2 presign helper |
| SH-090 `attachValidatedMedia` | Shared contract/separate contextual truth | Attach ready MediaAsset. | OfferingMedia create. | gallery role/order. | attachment eligibility/ready proof | upload/scan helper |
| SH-091 `requestSearchProjectionRefresh` | Search public interface | Index/update/hide/remove/restore. | After source/public readiness change. | action/reason/source version. | accepted Search request | direct SearchUpsertEvent/Typesense |
| SH-094 `buildSourceProjection` | Shared pattern/separate projection | Produce safe Offering index input. | Before SH-091. | public field allowlist/readiness. | versioned source document | Search raw DB reconstruction |
| SH-095 `executePrivacyInstruction` | Privacy protocol | Execute owner-local privacy action. | Privacy dispatch. | exact Marketplace erase/anonymize/retain semantics. | target result | local PrivacyRequest workflow |
| SH-096 `enumerateSubjectData` | Privacy protocol | List Marketplace-held subject data. | Privacy discovery/export. | owned record scope. | paged inventory/export facts | generic crawler |
| SH-097 `evaluateRetentionRequirement` | Privacy protocol | Return retention facts. | Before destructive privacy action. | commercial/legal record facts. | required/reason/min fields | local exemption table |
| SH-098 `anonymizePersonalFields` | Shared primitive/owner mapping | Apply approved field scrubbing. | Privacy execution. | exact field mapping. | deterministic result/proof | generic eraser |
| SH-103 `executeModerationDecision` | Cross-cutting protocol | Apply Moderation-owned action locally. | Restrict/restore command. | Offering lifecycle consequence. | completed/failed acknowledgment | local ModerationCase |
| SH-123 `validateOwnedTargetReference` | Shared contract/separate implementation | Validate Offering target for foreign relation/action. | Trust/Healthcare/Moderation setup. | allowed target relationship. | existence/version/status result | polymorphic Prisma target lookup |

SH-015 `returnDecisionResult` remains a Proposed Ruling. Marketplace contracts may align with its shape but must not depend on it as a global platform schema until approved.

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `validateOfferingKindShape` | Ensure supported kind has exactly the accepted detail shape. | Offering + detail state | validation result | none | Marketplace owns Offering business shape. |
| `validateOfferingPricing` | Validate current PricingTier configuration and derived minimum. | Offering + tiers | validation result/minimum | PricingTier / projection | Current supply pricing is Marketplace truth. |
| `evaluateOfferingLocalPublicationReadiness` | Evaluate only Marketplace-owned structural prerequisites. | aggregate + owner-delivery facts | local decision/reasons | none | Must remain separate from Professional Eligibility. |
| `mapModerationDecisionToOfferingTransition` | Convert approved external action into local lifecycle consequence. | SH-103 envelope + current status | proposed local transition | Offering.status | Marketplace alone owns status graph. |
| `buildOfferingSourceProjection` | Produce deterministic Search input allowlist. | current Offering public facts | versioned projection | none | Source owner decides what may leave its domain. |
| `buildOfferingCheckoutSourceFacts` | Provide present-tense price/supply facts to Order. | Offering + selected tier | DTO | none | Marketplace knows current supply; Order snapshots history. |
| `buildOfferingDeliveryRequirements` | Translate business shape into consumer-safe delivery facts. | Offering/details | DTO | none | Marketplace owns service/product/course business meaning. |
| `resolveDerivedPriceFrom` | Calculate lowest active current tier when needed. | active tiers | cents/null | `priceFromCents` only if stored | Prevents independent duplicate price truth. |

## 17. Shared Mechanism / Separate Truth Rules

- **Lifecycle state machines:** SH-053 may supply transition plumbing; Marketplace owns `OfferingStatus` transition graph and reasons.
- **Idempotency:** SH-044 owns mechanism; Marketplace defines command semantic identity.
- **Locks/concurrency:** SH-051/052 own mechanism; Marketplace defines which Offering actions conflict.
- **Domain events:** SH-046 owns outbox mechanics; Marketplace owns event meaning/payload/version.
- **Search projection:** SH-094 pattern may be shared; Offering projection fields/readiness remain Marketplace policy; Search owns index truth.
- **Media attachment:** SH-090 contract is shared; `OfferingMedia` remains Marketplace truth and MediaAsset remains Media truth.
- **Readiness responses:** SH-024 response shape may be shared; Marketplace local public-readiness policy remains separate from Professional/Healthcare/Verification decisions.
- **Privacy:** SH-095–098 share protocol/mechanics; Marketplace defines field/disposition semantics for its records.
- **Moderation enforcement:** SH-103 shares command envelope; Moderation owns case/action truth and Marketplace owns local Offering consequence.
- **Snapshots:** Order may use a shared snapshot mechanism, but historical Order price/supply snapshot is Order-owned, not Marketplace-owned.

## 18. Authentication and Authorization

- Every user-initiated protected entry point begins with SH-001 `resolveAuthenticatedActor`.
- Resource permission interpretation uses SH-002 `authorizeResourceAction`.
- Marketplace supplies owner facts: Offering ID, ProfessionalProfile ID, actor relationship, current status, and requested action.
- Professional owner access does not bypass lifecycle/readiness policy.
- Admin/support authority is explicit; admin role does not imply unrestricted access to healthcare, financial, private digital-delivery, or other foreign sensitive data.
- No organization/participant-scoped Marketplace authority is currently evidenced for Offering ownership; if introduced later it requires an explicit contract rather than reusing Organization hiring membership by assumption.
- No Marketplace-specific step-up requirement is currently confirmed for ordinary Offering edit/publication. If a future high-risk action requires step-up, use Identity SH-014 rather than local MFA.
- Client-side ownership checks are UX only; server authorization is mandatory.

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Truth owner | Operation consumed | Marketplace action gated | Marketplace local composition |
| --- | --- | --- | --- | --- |
| Professional seller readiness | Professional Eligibility | SH-016 | publication/resume and any approved seller action | Local shape must pass first; external allow is required. |
| Seller entitlement | Track | SH-005 directly or inside SH-016 | only actions explicitly mapped to an entitlement | No local premium/canSell boolean. |
| Taxonomy validity | Taxonomy | SH-023 | create/update/classification; publication if mandatory | Marketplace decides which local transition requires classification. |
| Taxonomy-triggered requirements | Taxonomy | SH-022 | publication context | Marketplace does not decide completion. |
| Verification readiness | Trust | normally through SH-016; SH-018 only when explicitly needed | high-risk Offering publication | No TrustBadge/provider inference. |
| Healthcare readiness | Healthcare | normally through SH-016; SH-020 when explicitly needed | healthcare-sensitive publication/access | `requiresHealthcareCompliance` is not proof. |
| Financial readiness | Payment | through SH-016 according to U-01 | publication only after U-01 is resolved; money actions elsewhere | Marketplace must not invent timing. |
| Compliance hold | Hold | SH-011 | hold-sensitive publication/resume/edit/enforcement according to scope | no local block flag. |
| Moderation/legal restriction | Moderation | SH-103/current source decision | publication/resume/restore/public visibility | source decision cannot be overridden by owner republish. |
| Media readiness | Media | SH-090 / owner query | attachment and required publication media | no file safety logic. |
| Digital delivery readiness | Digital Goods | owner public interface | downloadable/streaming publication where required | no grant/policy lifecycle writes. |
| Video readiness | Video | owner public interface | course publication where required | no provider state/token logic. |

**U-01 is a production blocker for a complete `publish_offering` financial-gate policy.** Until resolved, publication for any path whose financial requirement is unclear must return a policy-unresolved/non-allow decision.

## 20. Provider Integrations

Marketplace Supply owns **no direct provider integration** in the current architecture.

The following clients are explicitly prohibited here:

- Cloudflare R2/S3 client or presigned URL generator;
- Typesense client/indexer;
- Stripe/Stripe Tax/Stripe Checkout client used to mutate payment/order truth;
- Mux/Daily/Agora client or playback-token generator;
- Bedrock model client for AI taxonomy;
- notification email/SMS/push provider;
- verification/KYC/BAA provider.

Provider credentials, webhook verification, provider-event dedupe, provider-status translation, reconciliation, and provider deletion therefore do not belong in Marketplace Supply. Marketplace consumes normalized owner contracts.

## 21. Events and Outbox

### Emission rules

Marketplace domain events are emitted only after an authoritative local state change. The Offering write and SH-046 outbox append commit atomically.

### Payload requirements

Events should include only:

- event ID/type/version;
- Offering ID and source version;
- ProfessionalProfile ID where needed for routing;
- current status or changed semantic category;
- safe reason/source reference IDs;
- occurredAt;
- correlation/causation/request IDs.

Do not embed raw descriptions, provider payloads, PHI, financial details, private media URLs, or unneeded personal data.

### Consumer idempotency

Consumers use SH-045. An event is a fact that occurred, not a disguised command to mutate foreign truth. Consumers fetch current owner state before irreversible race-sensitive actions.

### Outbox need

Required for publication/restriction/restoration/archival and other changes where Search, Notification, or neighboring consumers must react reliably.

## 22. Background Jobs / Scheduled Work

### `reevaluateOfferingPublicationState`

- **Purpose:** reevaluate affected public Offerings after Professional readiness, taxonomy requirement, entitlement, hold, moderation, media, digital-delivery, or video readiness changes.
- **Input:** source event ID/type, affected Offering or ProfessionalProfile reference, correlation ID.
- **Owner:** Marketplace Supply.
- **Idempotency key:** handler type + source event ID + Offering ID.
- **Mechanics:** SH-045 claim, SH-047 durable job, SH-048 bounded retry, SH-038 telemetry.
- **Business truth updated:** Offering lifecycle only when an approved Marketplace transition policy requires a consequence. Otherwise only Search refresh/public-readiness result changes.
- **Retryable failures:** owner dependency/network timeout, Search request transient failure.
- **Permanent failures:** invalid/deleted target, unsupported unresolved policy, malformed event contract.
- **Dead-letter/manual review:** operationally visible through shared queue/Ops; no local QueueJob truth.
- **Important rule:** event payload does not supersede current owner state; worker refetches current Marketplace/external decisions.

### `priceFromCents` maintenance

No dedicated worker is approved by default. Calculate at read time until PR-06/U-16 explicitly selects stored projection maintenance semantics. If stored maintenance is approved later, it uses shared queue/concurrency and remains rebuildable.

No Marketplace cron/provider reconciliation worker is otherwise required.

## 23. Concurrency and Idempotency

### Races to prevent

- simultaneous creation with same professional slug;
- edit versus publish;
- publish versus moderation restriction;
- resume versus hold/moderation change;
- archive versus publish/resume;
- kind change versus details/delivery attachment mutation;
- duplicate PricingTier/media/tag commands;
- out-of-order dependency-change events.

### Lock/resource key

Critical lifecycle operations use `offering:{offeringId}` through SH-051 where serialization is required.

### Database constraints already available

- Offering unique `(professionalProfileId, slug)`;
- detail rows keyed by `offeringId` individually;
- OfferingMedia composite `(offeringId, mediaId)`;
- OfferingTag composite `(offeringId, tagId)`.

These do not by themselves guarantee exactly one detail **type** per Offering; application transaction policy must enforce kind/detail consistency until a stronger DB design is approved.

### Optimistic strategy

SH-052 using an approved version/CAS strategy is preferred for ordinary edits. `updatedAt` exists but is not itself a complete API contract until the repository exposes expected-version semantics.

### Idempotency

SH-044 is required for commands that may be replayed across network/server retries, especially create, publish, moderation execution, and privacy execution.

### Replay result

Same semantic request returns the original/canonical current result. A reused idempotency key with a different semantic fingerprint is a conflict.

No in-memory lock may protect database-owned invariants.

## 24. Media / Storage

### Marketplace-owned meaning

- `OfferingMedia` association and `sortOrder`;
- whether an asset belongs in Offering presentation context;
- whether a requested Offering view is allowed to reference a media item.

### Media-owned mechanics

- upload context/policy/session;
- MIME/binary/extension/size validation;
- malware scan;
- EXIF/GPS and metadata scrubbing;
- derivatives/processing;
- object storage/buckets/keys;
- public/private storage behavior;
- signed URL issuance and MediaAccessGrant;
- storage deletion.

### Attachment rule

Use SH-090. A raw object key or client URL is never accepted as proof that an asset is ready.

### Access

Public Offering presentation may consume public-processed media according to Media policy. Protected assets use SH-087 and contextual authorization. Marketplace never creates a permanent public URL for private/protected Offering material.

## 25. Search / Projection

### Source truth

Marketplace `Offering` aggregate and current Marketplace-owned fields.

### Marketplace source projection

SH-094 builder produces a deterministic, versioned allowlist. Candidate fields may include public slug/title/summary, kind, canonical category/tag IDs, public price range projection, approved presentation-media references, and safe delivery metadata. Exact schema is a Search/Marketplace contract and must exclude private/provider/compliance detail.

### Search-owned projection

Search owns `SearchUpsertEvent`, index workers, Typesense schema/client, ranking/query logic, reconciliation, and de-index execution.

### Indexing triggers

- Offering activation;
- pause/archive/restriction/restoration;
- public projection field change;
- accepted taxonomy change;
- current readiness change affecting public eligibility;
- Privacy erasure/de-index instruction;
- moderation/DMCA/hold effect.

Marketplace calls SH-091. It never writes `SearchUpsertEvent` or Typesense.

### Search must not reconstruct

- professional readiness;
- verification completion;
- healthcare readiness;
- moderation/hold policy;
- `isPublic` compatibility meaning;
- `isFeatured` promotion meaning;
- provider state.

## 26. Notification

Marketplace owns business triggers, not delivery.

Candidate notification intents include successful publication, pause/restriction/restoration, rejection where a supported rejection policy exists, and remediation-needed publication denial only if product policy wants asynchronous notification.

Requests go through SH-041 with safe recipient references and template variables. Do not include raw background, KYC, healthcare, financial, legal, or private media details. Direct SES/SMS/push calls are prohibited.

## 27. Audit and Sensitive Access

### Domain events/history

Marketplace domain events describe Offering facts and are published via SH-046.

### Generic audit

SH-029 may record publication, admin mutation, moderation execution acknowledgment, privacy execution, or other important actions. Audit is evidence, not lifecycle state.

### Sensitive access

Ordinary public Offering data is not a Marketplace-specific sensitive-access ledger case. If a future Marketplace query exposes protected Media/healthcare/digital-delivery data, the respective owner access policy and SH-030 may apply. Marketplace must not create `OfferingAccessLog` simply to duplicate AccessAuditLog.

## 28. Privacy and Retention

### Subject-data inventory

Marketplace may hold personal/commercial data in:

- Offering title/summary/description where personal information may appear;
- public slug;
- relationships to ProfessionalProfile;
- contextual media/tag joins;
- service/product/course detail URLs or descriptive configuration;
- timestamps and lifecycle state.

### Privacy executor responsibilities

Marketplace implements:

1. SH-096 enumeration of Marketplace-owned records for a subject;
2. SH-097 retention facts for each target;
3. SH-095 execution of Privacy instructions;
4. SH-098 owner field map for approved anonymization.

### Behavior

- archive/delete is not legal erasure;
- Order-referenced commercial records may require retention; Marketplace supplies facts, Privacy records the exemption;
- anonymize/remove personal copy where permitted while preserving minimum retained commercial identity/reference integrity;
- detach OfferingMedia context through Marketplace; actual object deletion remains Media-owned;
- request Search removal separately through SH-091;
- do not hard-delete retained Offering rows merely because a user requests erasure;
- if retention policy is unresolved, return retained/pending-policy rather than guessing destructive deletion.

### Export contribution

SH-096 may serialize Marketplace-owned data into Privacy's export workflow. Privacy owns the final bundle/storage/delivery.

## 29. Observability

Use root structured logging and correlation/request IDs.

Safe dimensions include:

- command/query name;
- Offering ID (where permitted);
- Offering kind/status;
- reason-code namespace;
- dependency owner name;
- duration/result class;
- job attempt count;
- correlation/causation IDs.

Never log raw descriptions by default, signed URLs, provider payloads, tax/verification/healthcare details, secrets, or private media metadata.

Use:

- SH-034 for telemetry sanitization;
- SH-037 for integration/dependency failures;
- SH-038 for job telemetry;
- root metrics/Sentry/health mechanisms as configured.

Operational records never replace Offering status or event truth.

## 30. Security Boundaries

- Validate all mutation inputs server-side with root-approved schema validation (project stack indicates Zod).
- Resolve actor and authorize server-side; frontend route state is not permission.
- Do not accept client-set lifecycle status as a generic input.
- Do not accept raw foreign provider IDs/statuses as Offering truth.
- Do not accept unvalidated Media object keys/URLs.
- External URLs in Product/Course details require root-approved URL validation and scheme allowlisting.
- Do not expose private/provider/compliance information in public projections or error messages.
- Use DB-backed concurrency/idempotency primitives; no process-local locks.
- No provider credentials or webhook secrets exist in Marketplace Supply.
- Rate limiting for public/write endpoints follows root platform policy rather than a Module-local limiter.
- Temporary signed tokens/URLs are issued by Media/Digital Goods/Video owners, not Marketplace.

## 31. Error / Decision Result Pattern

Public interfaces should return stable application categories, independent of framework/provider errors:

| Category | Meaning |
| --- | --- |
| `VALIDATION_FAILED` | Input or Marketplace-owned invariant failed. |
| `AUTHENTICATION_REQUIRED` | No trusted actor for protected action. |
| `FORBIDDEN` | Actor lacks authority. |
| `NOT_FOUND` | Offering/source object not found or safely hidden. |
| `CONFLICT` | Current state does not permit requested transition. |
| `STALE_VERSION` | Expected aggregate version is stale. |
| `IDEMPOTENCY_CONFLICT` | Same key reused for different semantic request. |
| `READINESS_BLOCKED` | Current owner decision denies publication/action. |
| `POLICY_UNRESOLVED` | Required architecture/product policy is intentionally unresolved. |
| `DEPENDENCY_UNAVAILABLE` | Required source owner cannot provide current decision; sensitive/publication gate fails closed. |
| `RETRYABLE_FAILURE` | Durable retry may succeed without changing business intent. |
| `INTERNAL_FAILURE` | Unexpected internal error with safe correlation ID. |

Owner-specific blocker reason codes accompany `READINESS_BLOCKED` without leaking sensitive underlying details. Provider-specific error codes must not escape because Marketplace owns no provider adapter.

## 32. Testing Architecture

### Domain unit tests

- kind/detail compatibility;
- draft/publication local completeness;
- PricingTier invariants and derived minimum;
- transition policy;
- projection allowlist;
- moderation decision mapping;
- privacy field mapping.

### State-transition tests

Cover every implemented legal transition and every prohibited transition, including publish/resume with current gate reevaluation and restriction races.

### Public contract tests

- Professional owner facts;
- Taxonomy SH-023/022;
- Media SH-090;
- Professional Eligibility SH-016;
- Search SH-091/094;
- Digital Goods/Video delivery-readiness contracts;
- Order checkout-source contract;
- SH-103 moderation execution;
- Privacy SH-095–097.

### Database/integration tests

- slug uniqueness;
- kind/detail transactional consistency;
- media/tag composite uniqueness;
- PricingTier writes and no historical Order mutation;
- authoritative owner-only writes;
- outbox transaction.

### Authorization tests

Professional owner, unrelated professional, admin/support approved path, unauthenticated, stale ownership facts.

### Compliance/readiness tests

- healthcare/verification requirement triggers do not become Marketplace truth;
- TrustBadge / `requiresHealthcareCompliance` / `isPublic` / `isFeatured` cannot bypass gates;
- U-01 unresolved path fails closed;
- moderation restriction cannot be bypassed by republish.

### Idempotency/concurrency tests

- duplicate create/publish/media/tag/tier commands;
- publish versus restriction;
- publish versus edit;
- resume versus hold change;
- out-of-order dependency events.

### Provider adapter tests

None inside Marketplace Supply. Contract tests verify no direct provider dependency is required.

### Privacy tests

- enumeration;
- retain/anonymize/delete decision handoff;
- no destructive erase on unresolved retention;
- Search removal separated from DB erasure;
- Media object deletion not performed locally.

### E2E participation tests

- professional creates service/product/course draft;
- blocked publish → remediation → publish;
- public Search handoff;
- pause/restrict/restore/archive de-index/re-index behavior;
- Order consumes current checkout snapshot without direct Marketplace repository access.

## 33. Module Invariants

**Rules coding agents must never violate:**

1. `Offering` is Marketplace Supply source truth; no other Module writes its lifecycle directly.
2. A User does not sell directly; every Offering belongs to a `ProfessionalProfile`.
3. Marketplace Supply never owns Professional Eligibility or reconstructs seller readiness from foreign tables.
4. `Offering.status` is lifecycle authority; `isPublic` is not an independent publication switch.
5. `isFeatured` remains inert until U-13 is resolved.
6. `bundle` creation/publication remains disabled until U-15 is resolved.
7. A supported Offering accepted state has kind-compatible detail shape; contradictory detail types are invalid.
8. PricingTier is current supply price, not historical Order price.
9. `priceFromCents` is derived and cannot be independently authored.
10. Marketplace Supply does not own SalesTaxLineItem or sales-tax calculations.
11. Marketplace Supply does not own DigitalGoodsPolicy, DigitalDownloadAsset, download grants/events, child-directed controls, or accessibility-asset lifecycle.
12. Marketplace Supply does not own MediaAsset storage/safety/signed access.
13. Marketplace Supply does not own CourseVideoAsset/provider/playback state.
14. Taxonomy owns vocabulary/validation; Marketplace only owns accepted contextual Offering attachment.
15. TrustBadge is never verification truth for publication.
16. `requiresHealthcareCompliance` is never healthcare proof.
17. Publication/resume must evaluate current owner decisions and fail closed on required dependency outage.
18. A stale publish command cannot overwrite a newer moderation restriction.
19. Search work goes through SH-091; Marketplace never writes SearchUpsertEvent or calls Typesense.
20. Notification delivery goes through SH-041; Marketplace never calls channel providers directly.
21. Generic AuditEvent/IntegrationFailure/QueueJob never become Offering lifecycle truth.
22. PrivacyRequest/DataErasureJob/DataRetentionExemption lifecycle remains Privacy-owned.
23. Archive/delete is not legal erasure.
24. Foreign Prisma relations do not grant cross-Module repository write access.
25. Shared operations are reused by SH ID rather than rebuilt under local aliases.
26. Unresolved policy is surfaced as unresolved/disabled; coding agents do not invent it.

## 34. Prohibited Duplicate Implementations

Do not create the following inside Marketplace Supply:

| Prohibited helper/service/file | Use instead |
| --- | --- |
| `marketplaceAuth.ts`, `offeringAuthService.ts`, `sellerAuthorization.ts` | SH-001 + SH-002 |
| `premiumOfferingGate.ts`, `sellerPlanCheck.ts`, `canSell.ts` | SH-005 / SH-016 |
| `offeringEligibility.ts`, `professionalVerificationService.ts` | Professional Eligibility SH-016; Trust SH-017/018 |
| `healthcareOfferingGate.ts`, `isHealthcareProvider.ts` | Healthcare SH-020 through approved readiness composition |
| `stripeReadyService.ts`, `paymentReadyForPublish.ts` | Payment SH-019 only according to resolved U-01 |
| `offeringHold.ts`, `blockedOffering.ts` | SH-011 / SH-103 local lifecycle consequence |
| `localTaxonomy.ts`, `tagNormalizer.ts`, `offeringTaxonomyRepository.ts` that owns terms | SH-022/023 |
| `offeringFileUpload.ts`, `offeringVirusScan.ts`, `r2MarketplaceUrl.ts`, `offeringSignedUrl.ts` | Media SH-090/087 |
| `muxOfferingToken.ts`, `coursePlaybackService.ts` | Video owner |
| `productDownload.ts`, `offeringDownloadGrant.ts`, Marketplace DigitalGoodsPolicy repository | Digital Goods Access owner |
| Marketplace `SalesTaxLineItem` repository/service | Payment / Payout / Tax owner |
| `searchIndexOffering.ts`, Typesense client, local SearchUpsertEvent repository | SH-091 + Search owner |
| `sendOfferingEmail.ts`, `offeringPush.ts` | SH-041 Notification |
| `offeringAudit.ts` generic audit table | SH-029 |
| `offeringQueue.ts`, custom retry/dead-letter runner | SH-047/048 |
| `offeringLock.ts`, in-memory publish mutex | SH-051/052 |
| `offeringPrivacyRequest.ts`, `marketplaceGDPR.ts` orchestration | Privacy + SH-095–098 executor protocol |
| local ModerationCase/LegalNotice tables | Content Moderation + SH-103 |
| direct Bedrock classification adapter | AI Taxonomy / Taxonomy owners |

## 35. Unresolved Decisions

| ID | Question | Effect on Marketplace Supply |
| --- | --- | --- |
| U-01 | Must full KYC/tax/payout-account readiness be satisfied before Offering publication or only before money receipt/payout? | Blocks final production `publish_offering` financial-gate matrix. Drafting remains unblocked. |
| U-13 | What is `Offering.isFeatured` and who owns promotion/ranking policy? | Field remains inert; no UI/behavior/ranking use. |
| U-14 | Final relationship among `isPublic`, `status`, hidden/frozen/takedown timestamps, moderation, and Search readiness? | Independent reads/writes of `isPublic` are prohibited; status + owner readiness may implement publication. Exact timestamp semantics remain limited to approved transitions. |
| U-15 | How are bundle Offerings composed? | Bundle creation/publication disabled. |
| U-16 | Is `priceFromCents` stored and how is it rebuilt? | Independent writes prohibited; calculate at read time until implementation ruling approves stored projection semantics. |
| MA-U-01 | Exact legal adjacency/reopen rules for `under_moderation`, `disabled_by_dmca`, `disabled_by_moderation`, `rejected`, `archived`. | Only transitions settled in feature specs may be implemented. |
| MA-U-02 | Is a dedicated immutable Offering lifecycle event ledger required beyond SH-046 outbox + Audit evidence? | Do not add `OfferingEvent` schema until approved. |
| MA-U-03 | Is historical publication-decision evidence required as a separate source record? | Current implementation re-evaluates current owner truth; no snapshot table by default. |
| MA-U-04 | Exact Marketplace retention durations and which fields can be anonymized when Orders reference an Offering. | Privacy destructive behavior must return retained/pending-policy when legal basis is not settled. |
| MA-U-05 | Exact behavior for changing Offering kind after any downstream Order/delivery reference exists. | Restrict to safe draft-only subset until approved. |

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Marketplace Supply owns `Offering`, kind-specific service/product/course business details, current PricingTier truth, OfferingMedia context, Offering lifecycle, and publication/update workflow.
2. Marketplace Supply is the only Module that writes `Offering.status`.
3. Professional Eligibility owns seller readiness and supplies `publish_offering` decision through SH-016.
4. Taxonomy owns vocabulary/assignment validity; Marketplace owns contextual OfferingTag attachment under PR-05.
5. Media owns MediaAsset mechanics; Marketplace owns OfferingMedia business context.
6. Digital Goods Access owns digital-goods policy/access lifecycle; Payment owns SalesTaxLineItem/sales-tax truth.
7. Video owns course-video provider/playback lifecycle.
8. Order owns transaction/historical price truth; Marketplace provides current source facts only.
9. Search owns SearchUpsertEvent/Typesense; Marketplace builds safe source projection and requests refresh.
10. Privacy, Moderation/Hold, Audit, Notification, Observability, Identity, Authority, and Track Entitlement remain external rails.
11. Provider clients/webhooks do not belong in Marketplace Supply.
12. Cross-Module collaboration uses public interfaces/events, not direct owner repositories by default.

### Proposed Rulings carried forward

1. OfferingTag contextual ownership split follows CL-03 PR-05.
2. `priceFromCents` follows CL-03 PR-06 as derived/rebuildable.
3. `isPublic` is compatibility/projection and `isFeatured` is inert under CL-03 PR-07.
4. The proposed folder organization in Section 6 applies only if root repository structure does not define a conflicting layout.
5. Proposed Offering event names are Module contract vocabulary, not a new Prisma ledger unless a later ruling requires one.

### Non-implementable until resolved

- financial publication timing under U-01;
- featured/promotion behavior under U-13;
- independent `isPublic` semantics beyond approved publication policy under U-14;
- bundle creation/publication under U-15;
- stored `priceFromCents` maintenance semantics under U-16;
- unsupported lifecycle adjacency/reopen cases listed in MA-U-01.

## 37. Coding-Agent Usage

Before implementing Marketplace Supply, an agent must read:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. Canonical Shared Operations Registry (`context/shared/shared-operations.md` or current canonical equivalent);
5. CL-03 `context/professional-supply-readiness/architecture.md`;
6. CL-03 `context/professional-supply-readiness/build-plan.md`;
7. this `marketplace_supply/module-architecture.md`;
8. `marketplace_supply/implementation-plan.md`;
9. public-interface sections for Professional Eligibility, Taxonomy, Media, Search, Digital Goods, Video, Transaction / Order, Moderation/Hold, Privacy, Notification, Audit, and any other dependency touched by the feature;
10. current progress tracker.

Before coding a numbered feature the agent must:

- confirm the Cluster feature/milestone it supports;
- confirm the previous Marketplace Supply exit gate passed;
- identify every owner record read or written;
- map every shared operation to its canonical SH ID;
- stop when a required Proposed/Unresolved operation or policy would require invented semantics;
- reject direct cross-domain repository access unless architecture explicitly authorizes it;
- update this architecture only when a binding decision legitimately changes.
