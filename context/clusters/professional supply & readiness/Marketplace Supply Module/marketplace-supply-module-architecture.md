# Marketplace Supply Module Architecture

> **Module ID:** `marketplace_supply`  
> **Module name:** Marketplace Supply Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md`\
> **Document status:** Implementation-grade Module architecture. Confirmed rulings are binding; Proposed Rulings require approval before schema/API commitment; Unresolved items must not be invented by implementation.

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

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
| Media / File Access | SH-090 `attachValidatedMedia`; SH-127 for protected reads if needed | Ready asset validation and signed-access mechanics. | asset ID/context/actor | Yes for required media | upload/scanner/R2/signed URL |
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
| SH-127 `requestMediaAccess` | Media capability | Protected Offering media access where needed. | Authorized read. | Business entitlement/context. | short-lived URL/access evidence | R2 presign helper |
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

**CL-03-R005:** Marketplace does not consume or depend on `ProfessionalReadinessChanged`; Professional Eligibility has not approved that producer contract. Generic dependency-triggered reevaluation remains valid, but the replacement producer/consumer handoff for downstream Offering consequences is unresolved. Shared event/job mechanics do not supply that missing contract.

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

Public Offering presentation may consume public-processed media according to Media policy. Protected assets use SH-127 and contextual authorization. Marketplace never creates a permanent public URL for private/protected Offering material.

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

1. `context/project-overview-v3.md`;
2. root architecture (**missing**; see `context/context-map.md`);
3. root code standards (**missing**; see `context/context-map.md`);
4. Canonical Shared Operations Registry (`context/shared/shared-operations.md`);
5. CL-03 `context/clusters/professional supply & readiness/professional-supply-readiness-architecture.md`;
6. CL-03 `context/clusters/professional supply & readiness/professional-supply-readiness-build-plan.md`;
7. this `context/clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md`;
8. `context/clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-implementation-plan.md`;
9. public-interface sections for Professional Eligibility, Taxonomy, Media, Search, Digital Goods, Video, Transaction / Order, Moderation/Hold, Privacy, Notification, Audit, and any other dependency touched by the feature;
10. progress tracker (**missing**; see `context/context-map.md`).

Before coding a numbered feature the agent must:

- confirm the Cluster feature/milestone it supports;
- confirm the previous Marketplace Supply exit gate passed;
- identify every owner record read or written;
- map every shared operation to its canonical SH ID;
- stop when a required Proposed/Unresolved operation or policy would require invented semantics;
- reject direct cross-domain repository access unless architecture explicitly authorizes it;
- update this architecture only when a binding decision legitimately changes.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.


## WA-R012 — Purchased session allowance and Booking cardinality (P02)

Product-owner ruling approved 2026-09-29: an Order may authorize multiple scheduled sessions **only when the purchased Offering/package explicitly includes them**. Four purchased sessions permit at most four allocated session entitlements, not unlimited Bookings. This closes U-BC-02 / CL-05-U014's product choice. Do not add uniqueness on Booking.orderId.

Supply owns the offered package description. Order validates and snapshots the purchased positive integer session allowance, source/version and applicable fulfillment/cancellation/refund terms; later Offering edits cannot change the purchase. Booking owns each appointment and its conflict, hold and scheduling lifecycle. Neither a paid flag nor counting local Booking rows supplies purchase authorization.

Technical ruling: Order owns durable per-session authorization identities bounded by the purchased allowance. An idempotent reservation command binds Order/session identity to one Booking command intent and reports authorized, exhausted, denied, or unavailable with the Order version. Concurrent attempts cannot reserve the same session twice or exceed the allowance. Booking persists the reservation identity with its local conversion; an outbox acknowledgement confirms attachment. An uncertain cross-owner outcome remains reserved until reconciliation queries Booking's durable result; never release merely on transport timeout. Failed conversion with proven absence can release its reservation idempotently. This is a recoverable workflow, not a cross-owner Prisma transaction.

Rescheduling retains the session authorization through the replacement chain and does not consume another session. A completed, cancelled or no-show appointment does not itself restore allowance or prove full Order completion. Order applies the purchased terms and owner-confirmed session outcomes; refunds and cancellation adjustments are Order decisions through Payment's rail. No automatic equal-price-per-session refund or forfeiture policy is invented. Packages cannot activate without explicit applicable terms. A normal SlotLock converts at most once (U-BC-03); that safety invariant is separate from Order multiplicity.

Implementation acceptance: four-session package permits four distinct authorizations and rejects a concurrent fifth; retry returns the same identity; single-session package remains bounded; reschedule reuses authorization; timeout recovery avoids double release/allocation; source edits do not rewrite terms; partial fulfillment does not finish the whole Order; refund/cancel outcome follows snapshotted terms. Current schema lacks this complete contract; the coordinated database pass must implement it before package activation.


## WA-R024 — Financial readiness is action-specific

Class: **AI_RESOLVED_WITH_TRADEOFF** from the approved separation of Identity, optional screening, Professional readiness and financial execution. Preserve the existing Professional identity/KYC baseline; do not equate optional background screening with KYC. Payment's financial decision identifies the named action and the applicable KYC, tax, account and restriction dimensions, rather than exposing one timeless professional-is-financially-ready boolean.

Profile editing/drafting never requires payout readiness. Public activation/publication/Gig response uses the applicable Professional identity, Track, taxonomy/Trust/Healthcare and Hold policies; incomplete payout-account or tax setup alone is not a new universal nonfinancial block unless an explicit applicable requirement demands it. Paid acceptance/checkout must meet Payment's current charge/recipient capability for that flow; payout execution requires current recipient/account/KYC/tax/hold requirements. The purchaser cannot be charged through an unsupported recipient capability merely because a listing is visible. UI shows the owner-provided unavailable transaction state without leaking the seller's private KYC/tax details.

Tradeoff: discoverability and action readiness can differ; each attempted financial action re-evaluates current Payment facts. This avoids silently extending payout-only requirements to every public profile or treating a public listing as financial clearance. Provider/regulatory prerequisites may tighten the financial action and remain EXTERNAL_REQUIREMENT. No legal threshold, automatic KYC approval or alternative sponsorship flow is invented.

This resolves the universal-versus-action-specific architecture in CL03-HD001 / CL-03 U-01 / PE-U01 / Payment UD-01. Implement the action/dimension matrix and owner fixtures before activation; do not treat this as proof that the selected provider permits a particular charge/transfer. Existing settled optional screening and explicit free Track baselines remain binding.

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

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.
