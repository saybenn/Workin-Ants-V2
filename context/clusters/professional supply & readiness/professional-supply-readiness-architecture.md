# Professional Supply & Readiness Architecture

> **Cluster ID:** CL-03  
> **Cluster name:** Professional Supply & Readiness  
> **Cluster type:** `core_marketplace_supply_eligibility_regulated_readiness`  
> **Document status:** Implementation-grade cluster architecture; binding where marked Confirmed, planning-only where marked Proposed Ruling, and non-implementable where marked Unresolved  
> **Repository target:** `context/professional-supply-readiness/architecture.md`

## 1. Document Status and Scope

This document defines the stable architecture for **CL-03 — Professional Supply & Readiness**. It coordinates the five Deep Modules that turn a User's seller intent into a professional identity, regulated-readiness evidence, sellable supply, and financial readiness.

The intended audience is coding agents, developers, reviewers, maintainers, and architecture reviewers implementing or changing CL-03.

This document is subordinate to the root Workin Ants architecture and code standards. It specializes those rules for CL-03. It does not override root decisions about authentication, authorization, persistence, events, queues, privacy orchestration, search, media, audit, observability, or deployment.

CL-03 is a **planning, integration, and controlled-context boundary**. It is not a lifecycle owner and it has no independent source-of-truth aggregate. The five included Deep Modules retain their own records, policies, provider mappings, events, and lifecycle transitions.

Module architecture remains more authoritative for a Module's internal domain behavior. This Cluster architecture is authoritative for collaboration boundaries, cross-Module contracts, anti-duplication rules, build sequencing, and the way the five Modules compose without stealing ownership from one another.

**Update rule:** when a binding ownership, lifecycle, public-interface, data-model, provider, compliance, or shared-operation decision changes, update this architecture before or in the same change as implementation. Build progress must never silently redefine this document.

### Evidence classification

- **Confirmed** — directly supported by the current Deep Module Registry, Cluster Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, supplied Module Architecture Extracts, or Canonical Shared Operations Registry.
- **Proposed Ruling** — a necessary implementation decision strongly supported by the evidence but not yet established as canonical authority. It must be approved before schema/API commitment that depends on it.
- **Unresolved** — the supplied evidence does not establish one safe answer. Implementation must not invent the answer.

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

CL-03 controls whether a `ProfessionalProfile` can operate as a seller, publish an `Offering`, pass professional or regulated-service gates, and receive money without collapsing seller identity, verification, healthcare, marketplace supply, and financial compliance into one lifecycle.

### Goal

Produce a professional seller state that can answer, with source-backed reasons:

```text
Who is the ProfessionalProfile?
What is the Professional trying to do?
What supply are they offering?
Which taxonomy-triggered requirements apply?
Which verification or healthcare gates are satisfied?
Which entitlement and ComplianceHold rules apply?
Is the Professional financially ready for the requested money action?
Which Module owns the final mutation?
```

### What enters the Cluster

- authenticated User/system actor context;
- Role / Authority decisions;
- professional profile data and intended seller action;
- accepted taxonomy domain/category/tag context;
- professional-track entitlement decisions;
- consent/version proof where required;
- verification requirements, checks, credentials, and provider outcomes;
- healthcare lane, BAA, data-boundary, and healthcare access-policy facts;
- Offering shape, pricing, classification, and media references;
- KYC, tax, payout-account, balance, payout, and sales-tax provider outcomes;
- reusable `ComplianceHold` decisions;
- moderation decisions affecting a profile or Offering;
- Privacy-owned erasure/export/retention instructions.

### What leaves the Cluster

- an authoritative `ProfessionalProfile` and its lifecycle state;
- action-specific professional-readiness decisions;
- verification requirement/readiness decisions and verification proof;
- healthcare-readiness decisions and healthcare compliance proof;
- structurally valid and lifecycle-controlled Offerings with pricing and presentation context;
- financial-readiness decisions and payout/tax proof;
- domain events and reliable downstream requests;
- approved source projections and Search projection requests;
- notifications, audit evidence, sensitive-access evidence, and operational diagnostics requested through their owning Modules.

### Major transformation

```text
User wants to sell
→ ProfessionalProfile exists
→ professional classifications and seller entitlement are established
→ action-specific verification / healthcare / hold gates are composed
→ Offering supply is created and validated
→ financial readiness is established for money actions
→ Marketplace Supply or Professional Eligibility performs its own authorized transition
→ downstream Order, Search, Delivery, Messaging, and Notification workflows consume public contracts
```

### Explicit non-ownership

CL-03 itself does **not** own authentication, permission interpretation, consent proof, taxonomy vocabulary, subscription/entitlement truth, `ComplianceHold`, Search execution, MediaAsset mechanics, PrivacyRequest orchestration, generic AuditEvent/AccessAuditLog storage, Notification delivery, Order lifecycle, Gig lifecycle, Booking lifecycle, digital-delivery grants, moderation case lifecycle, or operational incident truth.

## 3. Module Inventory

| Module ID | Module name | Module type | Purpose | Owned truth | Primary responsibility in CL-03 | Major inbound dependencies | Major outbound consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `professional_eligibility` | Professional Eligibility Module | `compliance_domain_gate` | Own the seller-role identity and compose action-specific seller readiness. | `ProfessionalProfile` lifecycle and professional-readiness policy. | Establish the professional actor and answer whether that actor may activate, publish, respond, participate, become public, or proceed toward selling. | Identity, Role / Authority, Taxonomy, Track Entitlement, Trust, Healthcare, Payment, Compliance Hold. | Marketplace Supply, Gig / Demand, Transaction / Order, Search / Public Visibility, Healthcare, Admin Review. |
| `trust_verification_screening` | Trust Verification / Screening Module | `compliance_trust_capability` | Define required checks, coordinate screening/credential workflows, preserve results, FCRA state, and trust projections. | Verification requirements/checks, screening-specific workflow records, license credentials, adverse-action workflow, `TrustBadge`. | Supply current verification readiness and legally usable verification proof. | Identity, Consent, Taxonomy, Order for paid screening, Media, Compliance Hold, provider adapters. | Professional Eligibility, Marketplace Supply, Hiring/Job flows, Search, Admin Review. |
| `marketplace_supply` | Marketplace Supply Module | `domain` | Own professional-created sellable supply. | `Offering`, kind-specific details, pricing tiers, Offering media context, Offering lifecycle, contextual classification attachment. | Turn a professional's proposed service/product/course/bundle into a valid Offering and own publication/status transitions. | Professional Eligibility, Taxonomy, Media, Trust, Healthcare, Track Entitlement, Moderation. | Search, Transaction / Order, Booking, Digital Goods Access, Video, Healthcare, Trust. |
| `payment_payout_tax` | Payment / Payout / Tax Module | `capability_compliance` | Own financial-compliance and processor-facing payment, payout, balance, tax, and provider-event truth. | KYC, tax profile/docs/reporting, payout account/request/transfer, balance ledger, Stripe-event dedupe, sales-tax proof. | Answer financial readiness and execute provider rails without replacing Order transaction truth. | Identity step-up, Role / Authority, ProfessionalProfile identity, Order, Compliance Hold, Review / Dispute, providers. | Professional Eligibility, Transaction / Order, CL-10 prize/reward tax flows, admin financial operations. |
| `healthcare_regulated_services` | Healthcare / Regulated Services Module | `compliance` | Own the healthcare-sensitive lane, BAA state, data boundaries, and healthcare-specific admin-access policy. | `HealthcareComplianceProfile`, `BaaAgreement`, `HealthcareDataBoundary`, `HealthcareAdminAccessPolicy`. | Answer whether healthcare-sensitive professional and Offering actions are permitted and how healthcare data may be handled. | Identity, Role / Authority, Consent, Taxonomy, ProfessionalProfile, Offering context, Media, providers. | Professional Eligibility, Marketplace Supply, Search, Media, Messaging, Video, Admin Review. |

### Ownership conflict preserved

The Marketplace Supply registry entry also claims several digital-goods records and `SalesTaxLineItem`. The current Ubiquitous Language, CL-05 ownership, and Payment module evidence place digital-download policy/access truth with **Digital Goods Access** and sales-tax line-item truth with **Payment / Payout / Tax**. CL-03 therefore **does not adopt those stale Marketplace ownership claims**. Marketplace may reference those records through public interfaces but must not own or mutate their lifecycles.

## 4. Cluster Architecture Principles

1. **Professional identity is separate from account identity.** A `User` cannot sell directly; seller activity is performed by `ProfessionalProfile`.
2. **Professional readiness is composition, not duplication.** Professional Eligibility composes Trust, Healthcare, Payment, Taxonomy, Entitlement, and Hold decisions; it does not copy their statuses into a second authoritative readiness system.
3. **Action-specific readiness replaces one global boolean.** `active`, `verified`, `stripeReady`, `canPayout`, or similar booleans must not answer every seller action.
4. **Offering lifecycle remains Marketplace-owned.** Professional Eligibility may authorize publication; only Marketplace Supply transitions `Offering.status`.
5. **Verification truth remains Trust-owned.** `TrustBadge` is display/projection; `VerificationCheck` and supporting Trust records are truth.
6. **Payout KYC is not marketplace screening.** Financial identity verification stays Payment-owned and must not reuse Trust verification records as payout truth.
7. **Healthcare is a contextual lane, not a user type.** Taxonomy, Offering, profile, and explicit healthcare data boundaries trigger healthcare requirements.
8. **Order remains transaction truth.** Payment executes processor rails and owns processor-event proof, but must command Order through its public interface for transaction-state changes.
9. **Processor-held funds are not a Workin Ants wallet or escrow.** Internal balance entries are an accounting projection over processor-held funds and domain effects.
10. **Tax-profile readiness and sales tax are distinct.** Seller tax identity/reporting must not be used as transaction-level sales-tax truth.
11. **ComplianceHold is the reusable stop sign.** Feature Modules may reflect a hold's consequences in their own lifecycle, but they do not create competing generic blocked-state systems.
12. **Search is downstream projection.** CL-03 owners supply approved projection inputs and request refreshes; Search owns `SearchUpsertEvent` and Typesense mechanics.
13. **Provider payloads are evidence inputs, not domain state.** Each provider-owning Module verifies, deduplicates, translates, and applies provider results to its own canonical records.
14. **Consent proves acceptance, not permission.** Trust and Healthcare decide whether a consent proof is sufficient for their action.
15. **Files remain Media-owned.** CL-03 Modules own contextual attachment/entitlement; Media owns upload, scan, processing, object storage, and signed URL mechanics.
16. **Privacy orchestrates; CL-03 owners execute.** No CL-03 Module creates a competing privacy-request lifecycle.
17. **Generic audit and observability remain separate from domain truth.** Audit proves actions/access; Ops diagnoses execution; neither substitutes for lifecycle events or provider dedupe records.
18. **No direct cross-Module Prisma reads as the default integration pattern.** Use small source-owner queries, commands, events, or approved snapshots.
19. **Canonical Shared Operations are anti-duplication constraints.** A local helper may wrap a canonical operation only when it preserves the canonical contract and does not create competing semantics.

## 5. Runtime / Collaboration Topology

### Request path

```text
Browser / server caller / worker / webhook
  → SH-001 resolveAuthenticatedActor when an actor exists
  → SH-002 authorizeResourceAction for protected operations
  → owning Module application service
      → local validation + local repository
      → source-owner public interfaces for external facts
      → SH-011 evaluateComplianceHold where action is hold-sensitive
      → canonical shared primitives for idempotency/concurrency/events
      → authoritative local write
      → transactional domain event/outbox when downstream reaction is required
      → downstream Module command / Search request / Notification request / Audit append
```

### Readiness composition

```text
Professional Eligibility
  ├─→ Taxonomy & Classification: which requirements apply?
  ├─→ Track Subscription & Entitlement: is seller action commercially entitled?
  ├─→ Trust Verification: are required checks/credentials current?
  ├─→ Healthcare: is the healthcare lane ready for this context?
  ├─→ Payment / Payout / Tax: is the requested financial action ready?
  └─→ Compliance Hold: is there an active reusable stop sign?
       ↓
   Professional Eligibility returns one action-specific decision
   without copying the participant Modules' source records
```

### Offering publication

```text
Marketplace Supply requestOfferingPublication
  → validate Offering-owned shape/pricing/classification/media context
  → SH-016 evaluateProfessionalReadiness(action=publish_offering)
       → Trust / Healthcare / Entitlement / Hold / policy dependencies
  → if allowed, Marketplace Supply alone transitions Offering.status
  → publish Offering lifecycle event
  → SH-091 requestSearchProjectionRefresh
  → SH-041 requestNotification where required
```

### Provider callback path

```text
Provider webhook
  → owning Module route adapter
  → SH-059 verifyProviderWebhookSignature
  → SH-060 deduplicateProviderEvent using owner-specific processed-event truth
  → SH-061 translateProviderStatus in that provider adapter
  → validate owner lifecycle transition
  → authoritative owner record update
  → SH-046 publishDomainEvent
  → SH-037 recordIntegrationFailure only on operational failure
```

A webhook route must never update another Module's table directly.

## 6. Folder / Code Organization

The exact root repository layout is owned by root Workin Ants architecture. Until that file establishes a different convention, the following is the **Proposed Ruling** for CL-03 organization because it preserves Deep Module ownership and keeps provider adapters close to their owner.

```text
src/
  modules/
    professional-eligibility/
      application/
      domain/
      contracts/
      infrastructure/
      workers/
      tests/

    trust-verification-screening/
      application/
      domain/
      contracts/
      infrastructure/
        providers/
      workers/
      tests/

    marketplace-supply/
      application/
      domain/
      contracts/
      infrastructure/
      workers/
      tests/

    payment-payout-tax/
      application/
      domain/
      contracts/
      infrastructure/
        providers/
      workers/
      tests/

    healthcare-regulated-services/
      application/
      domain/
      contracts/
      infrastructure/
        providers/
      workers/
      tests/

  platform/
    # only root-approved shared primitives / canonical SH implementations
    events/
    jobs/
    idempotency/
    observability/
    crypto/
```

### Organization rules

- **Domain/application code stays with its owner.** A Trust lifecycle policy does not move into `marketplace-supply` because publication uses it.
- **Public contracts live with the source owner.** Consumers import typed contracts or call interfaces; they do not import owner repositories.
- **Provider adapters stay with the provider-owning Module.** There is no generic `providers/` domain layer that centralizes Payment, screening, and BAA status semantics.
- **Shared platform code exists only for approved primitives/canonical shared operations.** Similar-looking code is not enough reason to create a shared folder.
- **No default cluster repository.** There is no `professional-supply-readiness.repository.ts` because the Cluster owns no data.
- **No default cluster orchestrator.** Professional Eligibility already owns readiness composition; Marketplace owns Offering publication; Payment owns payout workflows. Create cluster-local coordination only if a future workflow has no legitimate Module owner and an architecture ruling explicitly establishes one.
- Route/UI organization remains a root-architecture decision. UI handlers call Module application services rather than containing business workflows.

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
| --- | --- | --- | --- |
| Professional Eligibility | `ProfessionalProfile` lifecycle; action-to-gate composition; seller readiness result. | actor/authority, taxonomy requirements, entitlements, verification readiness, healthcare readiness, financial readiness, holds. | KYC, tax, payout-account, verification checks, TrustBadge, BAA, healthcare boundary, Offering lifecycle, Search queue. |
| Trust Verification / Screening | verification requirements/checks/packages, screening-specific linkage, license credentials, FCRA adverse action, TrustBadge projection. | ConsentLog proof, taxonomy triggers, Order payment truth for screening fees, Media safety, holds. | payout KYC/tax, Offering state, general consent lifecycle, Search state, legal interpretation of criminal records outside approved policy. |
| Marketplace Supply | Offering aggregate/lifecycle, kind-specific detail, PricingTier, OfferingMedia, contextual tag attachment, publication workflow. | Professional readiness, taxonomy validation, Media readiness, digital-delivery readiness, course-video readiness, moderation decisions. | professional readiness policy, verification truth, healthcare truth, Payment provider state, SalesTaxLineItem, digital-download grant/policy truth, Search state. |
| Payment / Payout / Tax | payment-provider dedupe, KYC, tax profile/doc/reporting, payout account/request/transfer, balance ledger, transaction sales-tax proof. | Order truth, professional identity, step-up proof, authority, holds, disputes, entitlement snapshots recorded by Order. | Order lifecycle, Agreement, Review/Dispute lifecycle, Trust checks, professional status, subscription policy. |
| Healthcare / Regulated Services | healthcare lane status, BAA lifecycle, healthcare data boundary, healthcare-specific admin payload policy. | actor/authority, ConsentLog proof, taxonomy/Offering/profile context, Media references, approved provider capability. | general authorization, file storage, Message/Thread lifecycle, video room lifecycle, verification license checks, generic audit storage. |
| Taxonomy & Classification | canonical taxonomy vocabulary/semantics and requirement triggers. | contextual entity facts. | completion of verification/healthcare gates; Offering lifecycle. |
| Track Subscription & Entitlement | professional plan/subscription/entitlement truth. | actor/track context. | Offering status, profile status, payout status. |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle. | domain evidence and requests from CL-03. | professional/Offering/payment/verification/healthcare lifecycle. |
| Media / File Access | `MediaAsset`, upload validation/scanning/processing, private object mechanics, generic signed access. | contextual entitlement supplied by CL-03 owner. | OfferingMedia meaning, verification credential meaning, BAA lifecycle, healthcare policy. |
| Search / Public Visibility | `SearchUpsertEvent`, index workers, search provider adapters/query surfaces. | owner-approved projection input/readiness. | professional, Offering, Trust, healthcare, financial truth. |
| Privacy / Data Erasure | PrivacyRequest/DataErasure orchestration and retention-exemption records. | data-owner enumeration/execution results. | CL-03 source records and their ordinary lifecycle. |
| Audit / Event Ledger | generic `AuditEvent` and `AccessAuditLog`. | safe actor/action/evidence metadata. | lifecycle truth, provider-event dedupe truth, business event ledgers. |
| Observability / Ops | `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident`. | safe operational metadata. | business lifecycle status or compliance proof. |
| Transaction / Order | `Order` and Order event truth. | CL-03 supply/readiness/payment effects through contracts. | payout, KYC, tax, VerificationCheck, Offering lifecycle. |

## 8. Data Ownership

The Prisma schema is executable schema evidence. This section explains semantic ownership. A relation or foreign key does not grant the referring Module permission to update the referenced owner's row directly.

### CL-03-owned records

| Record / enum / projection | Owner | Meaning / rule |
| --- | --- | --- |
| `ProfessionalProfile` | Professional Eligibility | Seller actor identity and profile lifecycle truth. |
| `ProfileStatus` as used by `ProfessionalProfile` | Professional Eligibility | Professional profile lifecycle vocabulary. The enum is also used by CandidateProfile; see Proposed Ruling PR-02. |
| `VerificationRequirement` | Trust | Requirement truth: which verification applies to which target/action. |
| `VerificationCheck` | Trust | Auditable screening/check attempt and result truth. |
| `VerificationConsent` | Trust, only for screening-specific linkage if retained | Must not replace `ConsentLog`; exact proof split remains unresolved. |
| `VerificationPackage`, `VerificationPackageItem` | Trust | Configured screening bundle/pricing/disclosure composition. |
| `FcraAdverseActionWorkflow` | Trust | FCRA adverse-action workflow truth. |
| `ProfessionalLicenseCredential` | Trust | Durable professional-license credential state. |
| `TrustBadge` | Trust | Public-facing trust display projection; never verification truth. |
| Trust-owned verification enums/statuses | Trust | Requirement/check/package/FCRA/license/badge controlled vocabularies. |
| `Offering` | Marketplace Supply | Sellable supply identity and lifecycle. |
| `ServiceDetails`, `ProductDetails`, `CourseDetails` | Marketplace Supply | Kind-specific Offering shape. |
| `PricingTier` | Marketplace Supply | Current purchasable Offering price option before Order snapshot. |
| `OfferingMedia` | Marketplace Supply | Contextual attachment/order of a MediaAsset to an Offering. |
| `OfferingTag` row lifecycle | Marketplace Supply (Proposed Ruling supported by join rule) | Contextual attachment only; Taxonomy owns the tag and assignment validity semantics. |
| `OfferingKind`, `OfferingStatus`, delivery-mode enums | Marketplace Supply | Supply lifecycle and shape vocabularies. |
| `ProcessedStripeEvent` | Payment / Payout / Tax | Stripe provider-event dedupe truth; not audit/business transaction truth. |
| `KycVerification` | Payment / Payout / Tax | Financial identity/KYC readiness truth. |
| `TaxProfile`, `TaxDocument` | Payment / Payout / Tax | Seller/recipient tax identity and provider-held document references. |
| `TaxYearEarningsSummary` | Payment / Payout / Tax | Yearly reportable-value projection. |
| `PayoutAccount`, `ProviderRequirementSnapshot` | Payment / Payout / Tax | Payout destination/capability and provider requirement evidence. |
| `ProfessionalBalanceLedgerEntry` | Payment / Payout / Tax | Append-only accounting projection of professional financial effects; not custody. |
| `PayoutRequest` | Payment / Payout / Tax | Professional intent to withdraw available processor-held funds. |
| `PayoutTransfer` | Payment / Payout / Tax | Provider-mediated transfer attempt/result. |
| `TaxReportingSubmission`, `TaxReportingRecipient` | Payment / Payout / Tax | Filing-bundle and recipient reporting lifecycle. |
| `SalesTaxCalculation`, `SalesTaxLineItem`, `SalesTaxTransaction` | Payment / Payout / Tax | Transaction-level provider-backed sales-tax proof. |
| Payment-owned status/enums | Payment / Payout / Tax | KYC, tax-profile/reporting, payout-account/request/transfer, sales-tax controlled vocabularies. |
| `HealthcareComplianceProfile` | Healthcare | Professional healthcare-lane readiness summary/truth. |
| `BaaAgreement` | Healthcare | BAA execution lifecycle truth. |
| `HealthcareDataBoundary` | Healthcare | Explicit healthcare-sensitive target boundary. |
| `HealthcareAdminAccessPolicy` | Healthcare | Healthcare-specific treatment of admin/support payload access. |
| healthcare enums (`HealthcareComplianceStatus`, `BaaAgreementStatus`, target type, access mode/decision) | Healthcare | Healthcare lane and access vocabulary. |

### Relevant records owned outside CL-03

| Record / evidence | Owner outside CL-03 | CL-03 use |
| --- | --- | --- |
| `User`, security/step-up records | Identity & Access | Actor identity and sensitive financial assurance. |
| platform/org permission facts | respective source + Role / Authority interpretation | Authorization only. |
| `ConsentLog` | Consent & Disclosure | Generic versioned proof for FCRA/healthcare/other required acceptance. |
| taxonomy domain/category/tag and professional/Offering classification validity | Taxonomy & Classification | Requirements and accepted classification. |
| `TrackSubscription`, `TrackEntitlementGrant`, `TrackUsageEvent` | Track Subscription & Entitlement | Professional selling access/perks/commission policy. |
| `ComplianceHold` | Admin Review / Compliance Hold | Reusable stop-sign decision. |
| `MediaAsset` and media processing/access records | Media / File Access | Files and signed access. |
| `SearchUpsertEvent` | Search / Public Visibility | Projection work queue. |
| `AuditEvent`, `AccessAuditLog` | Audit / Event Ledger | Generic action and sensitive-access evidence. |
| `IntegrationFailure`, `QueueJob`, `SystemEvent`, `OpsIncident` | Observability / Ops | Technical failure/worker evidence. |
| `Order`, `OrderEvent`, refund/agreement truth | Transaction / Order | Transaction truth, screening-fee order, payment bridge, delivery entitlement. |
| `Gig`, `GigResponse`, `GigAssignment` | Gig / Demand | Professional response context. |
| Digital goods policy/download assets/grants | Digital Goods Access | Delivery readiness for downloadable Offerings. |
| Course video assets/playback grants | Video Session / delivery owner | Course delivery readiness. |
| PrivacyRequest/erasure/export/retention-exemption records | Privacy / Data Erasure | Orchestration instructions and legal retention decision recording. |
| Moderation cases/actions | Content Moderation & Legal Notice | Source decisions that CL-03 target owners execute against profile/Offering state. |

### Fields that must not become source truth

The present schema contains fields that overlap more authoritative records. Until an approved migration removes or formally defines them, they are non-authoritative compatibility/projection fields:

- `ProfessionalProfile.stripeReady` — never financial-readiness truth; use Payment's public decision.
- `ProfessionalProfile.stripeAccountId` — never the payout-account provider source; `PayoutAccount` owns provider-account truth.
- `ProfessionalProfile.verifiedAt` / `verificationExpiresAt` — never replace Trust records.
- `ProfessionalProfile.trustScore` — no approved owner/formula/version; must not gate actions.
- `ProfessionalProfile.ratingAverage` / `ratingCount` — derived Review projection only, if retained.
- `Offering.requiresHealthcareCompliance` — trigger/snapshot convenience only; never Healthcare proof.
- `Offering.isPublic` — must not independently override lifecycle/readiness. See PR-07.
- `Offering.isFeatured` — owner/policy unresolved; do not implement behavior from this field.

## 9. Lifecycle Ownership

### Lifecycle authority rule

Only the owning Module may legally apply a lifecycle transition. Other Modules may return a decision, request a transition, or react to an emitted event. Shared state-machine mechanics may be used, but transition graphs and reasons remain owner policy.

| Lifecycle | Owner | Status vocabulary | Transition authority | Other Modules may | Must not be confused with |
| --- | --- | --- | --- | --- | --- |
| ProfessionalProfile | Professional Eligibility | `draft`, `active`, `paused`, `suspended`, `archived` | Professional Eligibility application/domain service. | Request eligibility decisions, react to status event, request suspension/restoration through defined interface. | Verification status, KYC status, healthcare status, TrustBadge. |
| Verification requirement | Trust | active/inactive plus requirement fields; no full status enum | Trust admin/application policy. | Resolve applicability; react to rule changes. | a completed verification check. |
| Verification check | Trust | `not_started`, `consent_required`, `pending`, `passed`, `failed`, `needs_review`, `expired`, `revoked`, `cancelled` | Trust workflow/provider/manual-review logic. | Consume readiness result. | TrustBadge, payout KYC. |
| Verification package | Trust | `draft`, `active`, `paused`, `retired` | Trust. | Quote/configure through Trust interface. | Offering pricing. |
| FCRA adverse action | Trust | adverse-action status vocabulary in schema | Trust legal-gated workflow only. | Receive restrictions/hold requests when legally authorized. | ordinary failed check or ComplianceHold lifecycle. |
| Professional license | Trust | `not_started`, `pending`, `verified`, `failed`, `needs_review`, `expired`, `revoked` | Trust. | Consume readiness result. | VerificationCheck attempt unless explicit relation is established. |
| TrustBadge | Trust | active/suspended/expired/revoked | Trust projection policy. | Display badge; Search may index approved badge projection. | Verification truth. |
| Offering | Marketplace Supply | Prisma includes `draft`, `active`, `paused`, `under_moderation`, `disabled_by_dmca`, `disabled_by_moderation`, `rejected`, `archived` | Marketplace Supply. Restriction-source decisions come from Moderation/Hold owners. | Authorize publish, request restriction/restoration, consume state. | Search visibility document or professional profile state. |
| PricingTier | Marketplace Supply | active/inactive and row lifecycle | Marketplace Supply. | Order snapshots selected price before purchase. | historical Order price truth. |
| KYC | Payment / Payout / Tax | `not_started`, `pending`, `requires_input`, `approved`, `rejected`, `expired`, `disabled` | Payment provider workflow/manual policy. | Consume `evaluateFinancialReadiness`. | Trust screening. |
| Tax profile | Payment / Payout / Tax | `not_started`, `requested`, `submitted`, `verified`, `rejected`, `expired` | Payment / Payout / Tax. | Consume readiness. | transaction sales-tax calculation. |
| Payout account | Payment / Payout / Tax | `not_started`, `onboarding`, `pending_review`, `active`, `restricted`, `disabled` | Payment / Payout / Tax. | Consume readiness. | ProfessionalProfile status. |
| Professional balance ledger | Payment / Payout / Tax | append-only entry types | Payment / Payout / Tax only. | Supply source-domain effects through typed commands/events. | wallet/escrow or Order truth. |
| Payout request | Payment / Payout / Tax | `requested`, `pending_review`, `blocked`, `approved`, `processing`, `paid`, `failed`, `cancelled`, `reversed` | Payment / Payout / Tax. | Hold/Dispute may supply blocking evidence. | provider transfer. |
| Payout transfer | Payment / Payout / Tax | `pending`, `blocked`, `processing`, `paid`, `failed`, `reversed`, `cancelled` | Payment / Payout / Tax provider workflow. | Observe result. | payout request intent. |
| Sales-tax calculation/transaction | Payment / Payout / Tax | calculation and transaction enums | Payment / Payout / Tax. | Order consumes proof/result. | TaxProfile. |
| Healthcare compliance profile | Healthcare | `not_applicable`, `pending_baa`, `baa_sent`, `baa_signed`, `verified`, `rejected`, `suspended` | Healthcare. | Consume healthcare readiness. | BaaAgreement execution truth. |
| BAA | Healthcare | `draft`, `sent`, `signed`, `verified`, `rejected`, `revoked`, `expired` | Healthcare provider/manual workflow. | Consume current BAA state/readiness. | ConsentLog or Order Agreement. |
| Healthcare data boundary | Healthcare | current schema is presence/absence, no safe retirement status | Healthcare. | Request/query boundary through interface. | generic `DataSensitivity`. |
| Healthcare admin access policy | Healthcare | mutable mode `allow`, `redact_payload`, `block_payload` | Healthcare. | Role / Authority first determines whether actor may attempt access; owner resource enforces returned mode. | general permission role. |

### Transition gaps

The supplied evidence does not define every legal adjacency, actor, reason, or reinstatement rule. Implementations must use only transition graphs explicitly settled in the target Module architecture/feature specification. A coding agent may not infer that every enum value may transition to every other enum value.

## 10. Public Module Interfaces

Public means exposed to another application boundary or Module. It does not mean unauthenticated HTTP.

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumer must not infer/recreate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `createProfessionalProfile` | Professional Eligibility | onboarding UI/application | Provision one seller-role profile for a User. | actor, user ID, initial profile fields, idempotency key | profile ID, status, version | Truth | profile row creation or uniqueness rules. |
| `getProfessionalProfileContext` | Professional Eligibility | Trust, Healthcare, Payment, Marketplace, Hold | Narrow seller identity/status facts. | professionalProfileId, requesting context | ID, User link if permitted, status, safe classification refs/version | Truth | direct cross-domain repository read. |
| **SH-016 `evaluateProfessionalReadiness`** | Professional Eligibility | Marketplace, Gig, Order, Search | Answer whether seller may perform named action. | profile ID, action, target/gate context, evaluation time | decision, reason codes, evidence refs, evaluatedAt; shared shape only if SH-015 approved | Decision | Trust/Healthcare/Payment/Entitlement/Hold policy. |
| `transitionProfessionalProfile` via owner commands | Professional Eligibility | profile owner/admin/system | Activate, pause, suspend, reinstate, archive under owner rules. | profile, expected status/version, actor/source decision | resulting profile state/version | Truth | arbitrary status writes. |
| **SH-017 `resolveVerificationRequirements`** | Trust | Professional Eligibility, Marketplace, Hiring | Return applicable required checks. | subject + taxonomy/target/action context | requirement IDs/types/severity/applicability/expiry expectation | Truth/decision input | completion state. |
| **SH-018 `evaluateVerificationReadiness`** | Trust | Professional Eligibility, Marketplace, Hiring | Determine whether requirements are currently satisfied. | subject, target/action, current time | allow/deny/review with evidence IDs/reasons | Decision | badge/provider status interpretation. |
| `initiateVerificationCheck` | Trust | onboarding/admin | Start idempotent check after consent/payment gates. | subject, requirement/package, consent proof, optional fee Order, idempotency key | check ID, canonical state, next step | Truth | provider-native state. |
| `submit/verifyProfessionalLicenseCredential` | Trust | professional/admin | Maintain professional credential truth. | subject, license identity/jurisdiction, safe evidence refs | credential ID/status/expiry | Truth/evidence | direct file mechanics or raw provider payload. |
| FCRA workflow commands | Trust | restricted legal/admin workflow | Execute approved pre-adverse/dispute/final adverse transitions. | check/workflow, approved proof refs, actor/provider result | FCRA workflow state/evidence refs | Truth/evidence | legal policy beyond approved rules. |
| `getOfferingManagementView` | Marketplace | professional/admin UI | Return owned Offering aggregate for editing. | Offering ID, actor | Offering + owned details/tiers/media refs/classification refs | Truth | verification/healthcare/payment truth. |
| `createOfferingDraft` / update commands | Marketplace | professional application | Create/edit supply without cross-domain writes. | actor, professionalProfileId, local Offering input | Offering state/version | Truth | readiness results from local flags. |
| `getOfferingEligibilityContext` | Marketplace | Professional Eligibility, Trust, Healthcare | Narrow immutable facts needed for a gate. | Offering ID/version | owner ID, kind, taxonomy refs, delivery/sensitivity trigger facts | Truth | direct Offering repository access. |
| `requestOfferingPublication` | Marketplace | professional UI/application | Validate local supply, request professional readiness, and transition if allowed. | Offering ID, actor, expected version, idempotency key | active Offering or structured blocker result | Truth + decision outcome | direct Professional/Trust/Healthcare writes. |
| `applyOfferingRestriction` / restore command | Marketplace | Moderation/Hold control workflows | Reflect externally owned restriction decision in Offering lifecycle. | Offering, source decision/hold ID, action, idempotency key | resulting Offering state | Truth | moderation decision ownership. |
| **SH-019 `evaluateFinancialReadiness`** | Payment | Professional Eligibility, payout flows, CL-10 consumers as applicable | Answer separate KYC/tax/payout-account/balance/restriction dimensions. | professionalProfileId, requested financial action, amount/currency where applicable | dimensioned readiness + reasons/evidence refs | Decision | Stripe object interpretation or `canPayout`. |
| `startKyc/Tax/PayoutAccountOnboarding` | Payment | professional finance UI | Create provider-neutral onboarding flow and local canonical state. | actor, profile, action, idempotency | local record IDs + provider-session/reference data safe for client | Truth + delivery instruction | provider objects as platform truth. |
| `createPayoutRequest` | Payment | professional finance UI | Record withdrawal intent after step-up/readiness. | actor, profile, account, amount/currency, idempotency | PayoutRequest state | Truth | transfer completion. |
| `getFinancialHistory` | Payment | professional/admin | Read balance/request/transfer/tax state under step-up and sensitive access audit. | actor, profile, filters | safe financial view | Truth/projection | raw provider secrets or unrestricted data. |
| Order payment/tax commands | Payment ↔ Transaction / Order | Order/payment workflows | Execute provider rail and report normalized payment/tax results while Order owns transaction status. | Order snapshot/ref, amount/currency/tax context/idempotency | normalized provider result/evidence refs | Evidence/decision | direct mutation of Order by Payment. |
| **SH-020 `evaluateHealthcareReadiness`** | Healthcare | Professional Eligibility, Marketplace, Search/Delivery context owners | Answer healthcare lane/BAA/data-boundary readiness. | profile/target/action/provider context | permitted/blocked/redacted/denied result, reasons, policy version/evidence refs | Decision | Role authorization or BAA/provider truth reconstruction. |
| `getHealthcareComplianceContext` | Healthcare | professional/admin/consumers | Return safe healthcare lane summary and current evidence refs. | profile/target context | healthcare profile status + current BAA ref/boundary refs | Truth/evidence | raw PHI or provider payload. |
| BAA lifecycle commands | Healthcare | professional/admin/provider worker | Create/send/apply/verify/revoke/expire BAA under approved policy. | BAA ref, actor/provider normalized result, evidence refs | BAA state + readiness effect | Truth | generic consent or agreement lifecycle. |
| `resolveEffectiveHealthcareBoundary` | Healthcare | Media/Messaging/Video/admin access middleware | Determine healthcare-sensitive boundary for a target. | owned target reference | boundary source/decision | Truth/decision | direct polymorphic DB probing. |
| `evaluateHealthcareAdminAccess` | Healthcare | admin/support resource owners | Apply healthcare-specific payload allow/redact/block policy after general auth. | authorized actor context, target, action | healthcare access decision + handling instruction | Decision | Role / Authority permission. |
| `execute*PrivacyInstruction` | each CL-03 owner | Privacy / Data Erasure | Execute owner-specific erase/anonymize/retain/export target. | Privacy-owned target instruction, subject, retention ruling | executed/retained/failed result | Execution evidence | PrivacyRequest lifecycle. |

### Public interface rule

If a public semantic operation already has a canonical `SH-###` ID, reuse that contract or intentionally wrap it without creating a competing operation. Do not create `getStripeReady`, `getIsVerified`, `isHealthcareProvider`, or `canPublishOffering` helpers that bypass the owner decision interface.

## 11. Canonical Shared Operations Used by This Cluster

Only CL-03-relevant operations are listed. Full semantics remain in `context/shared/shared-operations.md`.

| ID / operation | Plain-English meaning | Canonical owner / class | CL-03 consumers | Reusable mechanism | Local policy that remains local | Invocation point | Must not duplicate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | Establish trusted actor context. | Identity & Access / platform capability | all five Modules | session/system credential resolution | requested action and target | every protected entry point | `professionalAuth.ts`, `offeringAuth.ts`, `payoutAuth.ts`, healthcare/trust session helpers |
| **SH-002 `authorizeResourceAction`** | Decide permission for a resource action. | Role / Authority / cross-cutting | all five | typed authz decision | owner relationship facts and action vocabulary | before protected read/mutation | module-local role engines and `isAdmin` checks |
| **SH-005 `resolveEntitlement`** | Return effective seller-track feature/perk/commission/access. | Track Subscription & Entitlement | Professional Eligibility, Marketplace, Payment snapshot consumers | typed entitlement resolution | what the result means for current seller action | readiness/publication/commerce policy | local premium/sellerAccess/commission booleans |
| **SH-008 `queryConsentProof`** | Retrieve version-specific acceptance proof. | Consent & Disclosure | Trust, Healthcare | canonical ConsentLog query | whether proof is sufficient for screening/healthcare action | before protected provider workflow | local consent booleans/tables |
| **SH-010 `presentStandaloneConsent`** | Present required high-risk disclosure separately. | Consent & Disclosure | Trust; Healthcare when approved disclosure requires it | versioned standalone consent UI/application shell | workflow-specific context | before FCRA/high-risk collection | custom screening checkbox proof |
| **SH-011 `evaluateComplianceHold`** | Return applicable reusable stop signs. | Admin Review / Compliance Hold | Professional, Marketplace, Trust, Payment, Healthcare | canonical hold decision | effect on local lifecycle/action | every hold-sensitive transition | `isBlocked`, `payoutBlockedFlag`, profile hold booleans |
| **SH-012 `requestComplianceHold`** | Ask hold owner to create a stop sign. | Admin Review / Compliance Hold | Trust, Payment, Healthcare, moderation consequences | idempotent hold request | evidence/reason/source supplied by requester | approved legal/compliance restriction | local competing hold table |
| **SH-013 `releaseComplianceHold`** | Ask hold owner to release a hold. | Admin Review / Compliance Hold | same | canonical release command | whether source condition permits requesting release | after owner resolves source condition | direct hold status writes |
| **SH-014 `requireStepUpForSensitiveAction`** | Require fresh MFA/passkey assurance. | Identity & Access | Payment; high-risk admin actions if root policy requires | SensitiveActionSession | which financial action requires step-up | before balance/tax/payout sensitive access/mutation | payout-specific MFA system |
| **SH-016 `evaluateProfessionalReadiness`** | Determine whether ProfessionalProfile may perform a selling action. | Professional Eligibility / Module interface | Marketplace, Gig, Order, Search | source-owned decision API | action-to-gate composition | publish/respond/participate/public readiness | consumer-owned readiness reconstruction |
| **SH-017 `resolveVerificationRequirements`** | Return applicable verification requirements. | Trust / Module interface | Professional Eligibility, Marketplace, Hiring bridges | Trust requirement query | requirement resolution policy | before verification/readiness evaluation | hardcoded category-check maps |
| **SH-018 `evaluateVerificationReadiness`** | Determine whether required checks/credentials are satisfied. | Trust / Module interface | Professional Eligibility, Marketplace | Trust decision | exact requirement/check/license policy | professional readiness composition | badge/provider-status interpretation |
| **SH-019 `evaluateFinancialReadiness`** | Determine financial readiness dimensions. | Payment / Module interface | Professional Eligibility, payout workflows | Payment decision | when financial readiness is required by requested action | receive-money/payout and any approved publish gate | `canPayout`, `stripeReady` logic |
| **SH-020 `evaluateHealthcareReadiness`** | Determine healthcare/BAA/data-boundary readiness. | Healthcare / Module interface | Professional Eligibility, Marketplace, Search/Delivery context owners | Healthcare decision | lane/provider/access policy | healthcare-sensitive activation/access | local HIPAA/provider booleans |
| **SH-022 `resolveTaxonomyRequirements`** | Convert accepted classification into requirement triggers. | Taxonomy & Classification | Professional, Trust, Healthcare, Marketplace | requirement-resolution contract | downstream owner decides completion | classification/readiness evaluation | hardcoded compliance-category arrays |
| **SH-023 `validateTaxonomyAssignment`** | Validate canonical taxonomy assignment. | Taxonomy & Classification | Marketplace, Professional profile classification | taxonomy validation | whether classification is mandatory for local transition | create/update/publish | local taxonomy copies/normalizers |
| **SH-024 `evaluatePublicReadiness`** | Return owner-approved public visibility readiness. | source/compliance owner; Search composes | Professional, Marketplace, Healthcare/Trust inputs | shared response contract with separate policy | each source owner's public-readiness policy | before source projection/search request | Search reconstructing CL-03 compliance |
| **SH-029 `appendAuditEvent`** | Append generic action evidence. | Audit / Event Ledger | all five | generic append-only audit | which action needs generic proof and safe metadata | sensitive/admin/lifecycle actions | module-local generic audit tables |
| **SH-030 `recordSensitiveAccess`** | Append proof of protected data access/denial/redaction. | Audit / Event Ledger | Payment, Healthcare, Trust restricted evidence | AccessAuditLog | sensitivity and contextual authorization | financial/PHI/background evidence access | custom access-log substitutes |
| **SH-044 `executeIdempotentCommand`** | Guarantee one business effect for a retried command. | platform application infrastructure | mutating workflows across CL-03 | idempotency claim/result | semantic command identity/conflict behavior | profile/offering/provider/payout/BAA/check commands | ad-hoc idempotency maps |
| **SH-046 `publishDomainEvent`** | Reliably publish versioned event after commit. | platform event/outbox | all lifecycle owners | transactional outbox | event name/payload/emission conditions | after authoritative mutation | module-specific unreliable emit-after-write |
| **SH-047 `enqueueReliableJob`** | Persist async work with retry/lease/dead-letter. | shared queue | Trust, Payment, Healthcare, Marketplace projection work | shared worker shell | payload/completion/business meaning | expiry, reconciliation, provider processing | custom queue tables/runners |
| **SH-059 `verifyProviderWebhookSignature`** | Authenticate provider callback before side effects. | shared integration-security shell + adapter | Trust, Payment, Healthcare | raw-body verifier contract | provider secret/algorithm/tolerance | webhook edge | one-off unsigned webhook processors |
| **SH-060 `deduplicateProviderEvent`** | Claim provider event once. | provider owner using shared primitive | Trust, Payment, Healthcare | uniqueness/claim mechanism | owner-specific processed-event record and result | after signature verification | AuditEvent as webhook dedupe |
| **SH-061 `translateProviderStatus`** | Map provider state into owner canonical vocabulary. | provider-owning adapter | Trust, Payment, Healthcare | normalized mapping contract | provider/domain-specific mapping | after verified/deduped event | global provider status enum |
| **SH-062 `reconcileProviderState`** | Repair missed/divergent provider effects. | each provider owner using shared worker framework | Trust, Payment, Healthcare | reconciliation worker mechanism | what divergence means and safe repair | scheduled/admin recovery | cross-module provider reconciler with shared truth |
| **SH-078 `minimizeAndRedactProviderInput`** | Strip unnecessary sensitive data from provider/telemetry payloads. | shared serializer; source owner policy | Trust, Payment, Healthcare | allowlist/redaction mechanism | required provider fields/sensitivity | before external provider call/logging | raw domain-object serialization |
| **SH-090 `attachValidatedMedia`** | Attach ready MediaAsset through a contextual join. | contextual owner; Media owns asset truth | Marketplace; Trust/Healthcare where contextual file linkage is modeled | ready-asset contract | role/order/context of attachment | Offering media / credential / BAA evidence linking | local file upload/scan/signed-url implementation |
| **SH-091 `requestSearchProjectionRefresh`** | Ask Search to index/update/hide/remove/restore. | Search / Public Visibility | Professional Eligibility, Marketplace | canonical Search request | public-readiness/source projection | profile/Offering status or readiness change | direct `SearchUpsertEvent` writes / Typesense calls |
| **SH-094 `buildSourceProjection`** | Build safe source-owned index input. | each source Module | Professional Eligibility, Marketplace | deterministic projection pattern | allowlisted public fields and owner readiness | before SH-091/indexing | Search reading private CL-03 tables to infer documents |
| **SH-095 `executePrivacyInstruction`** | Execute Privacy-owned instruction against owner data. | Privacy orchestrates; data owner executes | all five | target command protocol | erase/anonymize/retain/provider-delete behavior for owner records | Privacy worker dispatch | local PrivacyRequest workflows |
| **SH-096 `enumerateSubjectData`** | List subject data owned by a Module. | each data owner under Privacy protocol | all five | enumeration contract | owner-specific record/provider scope | privacy planning/export/erasure | generic cross-domain repository |
| **SH-097 `evaluateRetentionRequirement`** | Supply retention facts while Privacy records exemption. | data owner + Privacy | Trust, Payment, Healthcare, Marketplace, Professional | retention decision protocol | legal/record-specific retention facts | before destructive privacy action | local retention-exemption lifecycle |
| **SH-103 `executeModerationDecision`** | Target owner executes a Moderation-owned decision. | Moderation decision; target owner executes | Professional Eligibility, Marketplace | typed enforcement protocol | local lifecycle consequence | suspension/de-index/restriction/restoration | CL-03 moderation-case lifecycle |
| **SH-107 `createChargeableOrder`** | Ask Order owner to create a chargeable transaction. | Transaction / Order | Trust screening-fee workflow; Marketplace purchase bridge outside owner write | Order public command | screening package fee context remains Trust | before paid screening checkout | Trust-owned mini order/payment table |
| **SH-114 `provisionOneToOneProfile`** | Reuse provisioning mechanics while each profile remains separate truth. | each profile Module using shared mechanism | Professional Eligibility | uniqueness/idempotent provisioning | ProfessionalProfile defaults/eligibility policy | seller profile creation | generic profile table/lifecycle |
| **SH-117 `aggregateYearlyReportableValue`** | Aggregate reportable value without merging source domains. | value owners; tax consumes | Payment | shared aggregation mechanism | tax rules/source value meaning | yearly tax reporting | cross-domain tax ownership theft |
| **SH-118 `reportTaxableValue`** | Payment consumes reportable value from other owners. | Payment / Payout / Tax | CL-10 prize/reward bridge and other reportable sources | canonical tax-reporting intake | source lifecycle stays external | after reportable event | prize/reward logic inside Payment |
| **SH-123 `validateOwnedTargetReference`** | Let target owner validate a referenced target. | target owner | Healthcare, Trust polymorphic targets | owner-specific resolver contract | target eligibility/allowed reference types | create requirement/boundary/policy against external target | generic polymorphic cross-domain Prisma lookup |


| **SH-003 `queryOwnerFacts`** | Read minimum owner facts without transferring lifecycle ownership. | each source Module / shared contract, **Proposed Ruling** | Professional, Marketplace, Trust, Healthcare, Payment cross-owner contexts | small owner DTO pattern | exact facts exposed by each owner | authorization/gate target lookup when approved | universal cross-domain repository |
| **SH-034 `sanitizeTelemetryMetadata`** | Strip secrets/PHI/payment/background data from telemetry. | Observability + Audit payload policy | all provider/sensitive CL-03 paths | allowlist/redaction | owner sensitivity labels | before logs/audit/provider diagnostics | raw payload logging |
| **SH-038 `recordQueueTelemetry`** | Record job attempts/retries/dead-letter state. | Observability / queue infrastructure | Trust, Payment, Healthcare workers | worker instrumentation | owner job completion meaning | every reliable CL-03 worker | custom per-Module queue ledger as business truth |
| **SH-041 `requestNotification`** | Ask Notification to deliver a business/compliance alert. | Notification | all five owners where user/admin alerts are required | delivery routing/persistence | source event meaning/template variables | after owner event/decision | direct SES/SMS/push dispatch from CL-03 |
| **SH-045 `deduplicateDomainEvent`** | Prevent a consumed domain event from repeating a side effect. | platform event infrastructure; consumer inbox | readiness propagation, Payment source effects | transactional inbox | handler identity and local side effect | event consumers | ad-hoc processed-event booleans |
| **SH-048 `executeRetryWithBackoff`** | Retry transient technical failure with bounded policy. | shared queue/platform | Trust, Payment, Healthcare providers/jobs | backoff/jitter/dead-letter | retryability classification | provider/job failure | infinite/custom retry loops |
| **SH-051 `acquireAggregateLock`** | Serialize conflicting commands on one aggregate/resource. | shared persistence | profile/Offering/payout/check/BAA critical races | DB lock primitive | lock key/conflicting actions | race-sensitive mutations | in-memory distributed mutex |
| **SH-052 `withOptimisticConcurrency`** | Reject stale writes using version/compare-and-set. | shared persistence | profile/Offering/admin edits and lifecycle writes | version/CAS mechanics | merge/retry/conflict policy | mutable aggregates | last-write-wins owner mutations |
| **SH-053 `transitionLifecycleState`** | Reuse state-machine plumbing while owner keeps graph/invariants. | shared mechanism; lifecycle owner policy | all five lifecycle owners | transition validation/update/event hook | legal transition graph/reasons | owner lifecycle command | generic CL-03 status policy table |
| **SH-055 `runDeadlineExpiration`** | Invoke owner-defined expiry when deadlines pass. | shared scheduler/queue | Trust, Healthcare, Payment | batch/scheduler mechanics | check/license/BAA/tax/payout expiry policy | expiry workers | custom cron truth tables |
| **SH-056 `executeAtomicReservation`** | Reserve scarce value atomically to prevent overspend/over-allocation. | shared DB primitive | Payment payout/balance workflow where reservation is used | transactional reservation | financial sufficiency/release semantics | payout request/transfer race boundary | mutable wallet lock/in-memory reservation |
| **SH-063 `captureProviderSnapshot`** | Persist owner-specific provider requirement/state snapshot. | provider-owning Module | Payment; Trust/Healthcare only where their owner model requires | snapshot mechanism | fields/meaning/retention remain owner-local | provider requirement capture/reconciliation | generic provider snapshot as source truth |
| **SH-070 `deleteProviderResource`** | Delete external provider resource under owner/Privacy instruction. | provider-owning Module | Trust, Payment, Healthcare privacy executors | adapter deletion contract | legal retention and provider semantics | approved privacy deletion | Privacy calling providers directly |
| **SH-087 `issueSignedMediaUrl`** | Issue short-lived private Media access after contextual entitlement. | Media / File Access | Trust, Healthcare, Payment restricted docs and Marketplace private context | signed URL mechanics | CL-03 owner decides business entitlement/sensitivity | protected document access | local presigned URL helpers |
| **SH-098 `anonymizePersonalFields`** | Apply shared anonymization mechanics with owner field mapping. | shared primitive; record owner policy | all five Privacy executors | deterministic anonymization | owner fields/retention meaning | Privacy instruction execution | one generic cross-domain eraser |
| **SH-108 `requestOrderRefund`** | Coordinate refund through Order while Payment executes provider rail. | Transaction / Order coordinates; Payment executes | Payment financial bridge | refund command contract | Payment provider outcome; Order owns refund lifecycle | supported refund flow | Payment-owned competing refund lifecycle |
| **SH-109 `snapshotExternalDecision`** | Persist an external decision on the consuming lifecycle when historical truth requires it. | consuming domain owner | Order/Payment/Track collaboration; downstream consumers | snapshot pattern | which decision must be snapshotted and fields | transaction creation/financial policy snapshot | reading today's entitlement/price for history |

### Proposed shared contract status

**SH-015 `returnDecisionResult`** is a canonical **Proposed Ruling**, not yet a confirmed implementation constraint. CL-03 planning should align its readiness APIs toward a stable decision shape, but code must not make SH-015 a platform-wide schema/API dependency until that ruling is approved. Owner-specific decision contracts remain authoritative in the meantime.

## 12. Cross-Module Data Flows

### 12.1 Professional profile creation and activation

```text
User requests seller profile
→ Identity & Access: SH-001 actor resolution
→ Role / Authority: SH-002 create-profile authorization
→ Professional Eligibility: SH-114 one-to-one provisioning mechanism
→ Professional Eligibility: authoritative ProfessionalProfile(draft) write
→ Professional Eligibility: SH-046 ProfessionalProfileCreated event
→ when activation requested:
   Professional Eligibility resolves taxonomy / entitlement / holds
   → calls Trust SH-018 where required
   → calls Healthcare SH-020 where required
   → calls Payment SH-019 only for financial dimensions required by the action policy
→ Professional Eligibility alone writes ProfessionalProfile.status
→ Audit / Notification / Search effects requested through owners
```

**Owner:** Professional Eligibility owns every profile status mutation. The participating gate Modules only return their decisions.

### 12.2 Verification requirement to completed check

```text
Taxonomy/target context changes or professional requests gated action
→ Trust: SH-017 resolveVerificationRequirements
→ Trust determines missing/current checks
→ Consent: SH-008/SH-010 prove required standalone acceptance
→ if screening fee applies, Trust → Order SH-107
→ Trust writes VerificationCheck before provider side effect
→ Trust provider adapter uses SH-059 / SH-060 / SH-061
→ Trust applies canonical VerificationCheck transition
→ Trust updates credential/badge/adverse-action workflow only under Trust policy
→ Trust SH-046 emits readiness-change event
→ Professional Eligibility re-evaluates seller action
→ Search refresh requested only if public projection changed
```

### 12.3 Professional license verification / expiration

```text
Professional submits license identity/evidence
→ Trust validates target and Media readiness
→ Trust writes/updates ProfessionalLicenseCredential
→ provider/manual verification updates Trust-owned credential/check truth
→ SH-055 expiration job detects expired credential/check
→ Trust applies expiration transition
→ SH-046 emits verification-readiness change
→ Professional Eligibility / Marketplace / Search react through public decisions, not local booleans
```

### 12.4 Healthcare lane and BAA readiness

```text
Taxonomy / Offering / profile context indicates healthcare-sensitive lane
→ Healthcare resolves lane requirement
→ Healthcare creates/updates HealthcareComplianceProfile under owner policy
→ required ConsentLog proof is queried, not copied
→ Healthcare owns BaaAgreement lifecycle
→ provider callback, when enabled, uses SH-059/060/061 and owner-specific dedupe truth
→ Healthcare evaluates BAA + provider + boundary readiness
→ Healthcare returns SH-020 decision
→ Professional Eligibility or Marketplace enforces returned decision
→ Healthcare-sensitive target boundaries are created only through Healthcare owner commands
→ downstream Media/Messaging/Video resource owner enforces healthcare contextual access and records sensitive access
```

### 12.5 Offering draft to public supply

```text
Professional creates Offering draft
→ Marketplace validates ProfessionalProfile relationship through owner facts
→ Taxonomy validates classification
→ Media validates file mechanics; Marketplace creates OfferingMedia contextual joins
→ Marketplace owns Service/Product/Course detail and PricingTier writes
→ publication requested
→ Marketplace validates local shape/pricing/delivery readiness
→ Professional Eligibility SH-016(action=publish_offering, Offering context)
→ Professional Eligibility composes Trust/Healthcare/Entitlement/Hold and approved financial timing
→ if denied: Marketplace keeps source status and returns structured blockers
→ if allowed: Marketplace alone writes Offering.status=active
→ Marketplace emits lifecycle event/outbox
→ Marketplace builds source projection and calls Search SH-091
→ Notification request if product policy requires
```

### 12.6 Financial onboarding to payout

```text
Professional requests financial setup
→ SH-001 actor + SH-002 authority
→ Payment creates KycVerification / TaxProfile / PayoutAccount workflow records
→ provider calls/callbacks use SH-059/060/061 and ProcessedStripeEvent where Stripe event applies
→ Payment updates canonical KYC/tax/account states
→ Payment SH-019 exposes dimensioned readiness
→ completed/eligible Order effects create append-only ProfessionalBalanceLedgerEntry through Payment-owned projection workflow
→ professional requests payout
→ SH-014 step-up + SH-011 hold evaluation + Payment SH-019
→ Payment writes PayoutRequest
→ Payment creates provider-mediated PayoutTransfer idempotently
→ provider result updates PayoutTransfer/PayoutRequest and ledger effects
→ Order state is never mutated directly by payout workflow
```

### 12.7 Payment / sales-tax bridge to Order

```text
Transaction / Order supplies authoritative Order pricing/participants/snapshots
→ Payment requests provider-backed tax calculation and payment rail
→ Payment stores SalesTaxCalculation/LineItem proof
→ Stripe event passes signature + ProcessedStripeEvent dedupe
→ Payment normalizes provider result
→ Payment calls Transaction / Order public command with verified payment/refund result
→ Order alone writes Order.status / RefundStatus / OrderEvent
→ Payment records related tax transaction / financial projection
```

### 12.8 Dependency-change reevaluation

```text
Trust / Healthcare / Payment / Track / Hold / Taxonomy source truth changes
→ owner emits versioned domain event
→ consumer inbox deduplicates event
→ Professional Eligibility re-evaluates only affected actions/profile contexts
→ Marketplace does not automatically mutate an active Offering unless its owner policy says the source change requires restriction/de-publication
→ when public visibility changes, source owner/Marketplace calls SH-091
→ Notification and Audit are downstream effects, not the readiness truth
```

## 13. Cross-Cluster Bridges

| Source | Destination | Information / command | Authoritative owner | Interface / event | Forbidden coupling |
| --- | --- | --- | --- | --- | --- |
| CL-01 Identity / Authority | CL-03 all Modules | actor context, permission decision, step-up assurance | Identity / Role / Authority | SH-001, SH-002, SH-014 | CL-03 auth tables, frontend-only permission checks. |
| CL-01 Consent | Trust / Healthcare | versioned proof | Consent | SH-008/010 | treating ConsentLog as readiness/permission. |
| CL-01 Track Subscription & Entitlement | Professional / Marketplace / Order snapshots | seller access, commission/perks | Track | SH-005 | local premium/seller-plan/commission booleans. |
| CL-02 Taxonomy | Professional / Trust / Healthcare / Marketplace | accepted classification and triggered requirements | Taxonomy | SH-022, SH-023 | hardcoded compliance categories or local tags-as-truth. |
| CL-03 Professional / Marketplace | CL-02 Search | owner-approved public source projection and refresh request | source owner + Search projection owner | SH-024, SH-094, SH-091 | direct Typesense writes; Search reconstructing compliance. |
| CL-04 Gig / Demand | Professional Eligibility | Gig context for professional-response gate | Gig | owner facts + SH-016 | Professional module reading Gig tables directly as default. |
| CL-04 Transaction / Order | Marketplace / Payment / Trust | transaction truth, pricing snapshot, screening-fee Order, payment/refund command boundary | Order | SH-107 plus Order public queries/commands | Payment/Trust writing Order rows. |
| CL-04 Review / Dispute | Payment | dispute/refund/hold effects | Review/Dispute + Hold | domain event/public command | Payment owning dispute case lifecycle. |
| CL-05 Media / File Access | Marketplace / Trust / Healthcare | validated private asset and signed access mechanics | Media | SH-090 / Media public access contracts | local R2/presigned URL/file scanning. |
| CL-05 Digital Goods Access | Marketplace | downloadable-product policy/asset readiness | Digital Goods Access | owner public interface | Marketplace owning DigitalGoodsPolicy/DownloadGrant. |
| CL-05 Video | Marketplace | course/live video asset readiness | Video Session | owner public interface | Marketplace owning video provider/session state. |
| CL-06 Hiring | Trust | verification requirement/readiness for Job/candidate contexts where supported | Trust remains verification owner; hiring owns Job/Application | SH-017/018 | Professional Eligibility being reused as candidate eligibility. |
| CL-07 Notification | all CL-03 owners | notification delivery request | Notification | SH-041 | direct SES/SMS provider calls from CL-03. |
| CL-07 Messaging | healthcare/order contexts | conversation workflows consume CL-03 facts but own message/thread state | Messaging | owner interfaces/events | Healthcare owning Thread/Message lifecycle. |
| CL-08 Privacy | all CL-03 owners | erasure/export/retention instruction | Privacy | SH-095/096/097 | CL-03 PrivacyRequest lifecycle. |
| CL-08 Location Safety | Marketplace/health/payment when exact/public location is needed | safe location decision/evidence | Location Safety | location public interfaces | raw coordinate fuzzing or reveal logic in CL-03. |
| CL-09 Moderation / Hold | Professional / Marketplace / Payment / Trust / Healthcare | restriction/hold decision and evidence | Moderation/Hold | SH-011/012/013/103 | local generic blocked flags or moderation cases. |
| CL-09 Audit / Ops | all CL-03 | generic audit, sensitive-access proof, operational diagnostics | Audit/Ops | SH-029/030/037 | lifecycle truth in logs/incidents. |
| CL-10 Prize / Rewards | Payment | reportable prize/reward value for tax reporting | Prize/Reward owns outcome; Payment owns tax intake/reporting | SH-118 | Payment owning prize/reward lifecycle. |

## 14. Authentication and Authorization

- Every protected CL-03 entry point begins with **SH-001 `resolveAuthenticatedActor`** or an approved system-actor equivalent.
- Permission interpretation uses **SH-002 `authorizeResourceAction`**. Module owners supply resource relationship facts, target IDs, and action vocabulary.
- Professional-owned mutations require server-side proof that the actor controls the relevant `ProfessionalProfile` or has approved platform/admin authority.
- General authorization does not establish professional readiness, verification readiness, healthcare permission, financial readiness, or entitlement.
- Payment balance, payout account, tax dashboard, payout requests, and similarly sensitive financial operations require **SH-014 `requireStepUpForSensitiveAction`** according to the Identity security policy and must record **SH-030** sensitive-access evidence where required.
- Healthcare admin/support workflows are two-stage: Role / Authority first determines whether the actor may attempt access; Healthcare then returns allow/redact/block/deny payload treatment. An admin role does not bypass Healthcare policy.
- Background workers and webhook handlers run under explicit system actor/service context with constrained capabilities, not a fabricated end-user identity.
- Client/UI state must never be accepted as proof of ownership, entitlement, hold clearance, KYC, verification, or healthcare readiness.

## 15. Compliance and Readiness Composition

CL-03 contains several independent compliance truths. The action owner composes them; no aggregate boolean replaces them.

| Gate / fact | Authoritative owner | Typical CL-03 use | Not equivalent to |
| --- | --- | --- | --- |
| authenticated actor / step-up | Identity & Access | all protected actions / sensitive finance | authorization or readiness |
| permission | Role / Authority | resource access/mutation | compliance readiness |
| seller plan / entitlement | Track Subscription & Entitlement | professional selling access, commission/perks | profile status |
| taxonomy requirement trigger | Taxonomy | decide which verification/healthcare requirements apply | completed check |
| ProfessionalProfile status/readiness composition | Professional Eligibility | seller action gate | verification/KYC/healthcare proof |
| professional screening/license | Trust | verified/high-risk actions | payout KYC |
| KYC/tax/payout account/balance | Payment | receive-money and payout actions | seller profile activation |
| healthcare lane/BAA/boundary | Healthcare | healthcare-sensitive public/delivery/admin actions | User type or generic sensitivity flag |
| ComplianceHold | Admin Review / Compliance Hold | reusable action stop sign | source-domain failure reason |
| consent proof | Consent | evidence of version acceptance | downstream permission |
| Job compliance | Job Compliance, outside CL-03 | hiring publication | professional seller readiness |

### Action composition

The evidence confirms action-specific composition but does not settle every financial gate timing. The following is binding where marked and otherwise leaves an explicit unresolved point rather than inventing one:

- **Create/edit draft ProfessionalProfile:** authenticated/authorized actor and profile invariants are required. Full verification/healthcare/KYC is not evidence-supported as a prerequisite for drafting.
- **Create/edit draft Offering:** ProfessionalProfile relationship, authorization, taxonomy validation, and local Offering invariants are required. Drafting must not be blocked merely because a later publish gate is incomplete unless a separate entitlement policy explicitly says drafting itself is gated.
- **Activate ProfessionalProfile:** Professional Eligibility owns the transition and composes the current action-required entitlement/verification/healthcare/hold dimensions. Whether full financial readiness is mandatory for activation is **Unresolved**.
- **Publish Offering:** Marketplace owns the transition; Professional Eligibility supplies professional action readiness; Trust/Healthcare/Track/Hold gates apply when triggered. Whether payout/KYC/tax readiness is mandatory *before publication* is **Unresolved** and must not be silently assumed.
- **Respond to a Gig:** Professional Eligibility supplies the seller gate using Gig-owned requirement context. Healthcare/verification apply when triggered. Financial timing remains action policy, not a local Gig boolean.
- **Participate seller-side in an Order:** Order remains transaction truth; Professional Eligibility may answer seller operational eligibility for the requested transition. Financial execution remains Payment-owned.
- **Receive/request payout:** Payment financial readiness, active hold state, authorized actor, and step-up assurance are mandatory. Payment authorization/capture does not imply payout authorization.
- **Healthcare-sensitive file/message/video/admin access:** general authorization plus Healthcare decision plus contextual resource entitlement plus Media/Message/Video mechanics are separate required gates.

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Domain events

Each source owner defines and versions its own event names and payload semantics. Expected families include:

- Professional profile created/status changed;
- verification requirement changed, check status changed, credential expired/revoked, badge changed, adverse-action changed;
- Offering created/status/classification/pricing/public-readiness changed;
- KYC/tax/payout-account readiness changed, payout request/transfer changed, balance effect recorded, sales-tax result changed;
- healthcare profile/BAA/boundary/admin-policy/readiness changed.

Event names shown in Module extracts are candidate contracts until their Module architecture/feature specification fixes exact names and payload versions.

### Transactional publication

Use **SH-046 `publishDomainEvent`** through a transactional outbox. The authoritative state write and outbox append must commit atomically. Generic AuditEvent is not the outbox and must not be consumed as a substitute domain-event stream.

### Consumer idempotency

Consumers use the canonical event inbox/deduplication mechanism. A repeated domain event must not duplicate Search requests, ledger entries, status transitions, hold requests, or notifications.

### Jobs / schedules

Use **SH-047** and **SH-055** for:

- verification/check/license expiry and recheck scheduling;
- Trust provider reconciliation;
- BAA expiration and provider reconciliation;
- KYC/tax/payout-account refresh where owner policy requires;
- payout transfer retries/reconciliation;
- tax-year aggregation/reporting jobs;
- sales-tax/payment reconciliation;
- projection/backfill repair requested by source owners.

### Retry and dead-letter

- retry only technical/transient failures;
- do not retry a legal denial, validation failure, explicit provider rejection, revoked credential, hold denial, or manual-review outcome as if it were a network error;
- use bounded backoff and visible dead-letter/terminal failure;
- record operational failure through Observability without converting it into a business status unless the owner lifecycle explicitly defines that effect.

### Concurrency

Use owner-selected optimistic concurrency/locks for:

- ProfessionalProfile status transitions;
- Offering edits/publication versus moderation restriction;
- verification-check initiation/recheck to avoid duplicate active attempts;
- payout requests and balance reservation/transfer creation;
- provider-event claims;
- BAA lifecycle updates.

### Workflow/saga boundary

A shared workflow runner may coordinate steps, but the Module that owns the business objective owns workflow meaning. Do not create a cluster-wide saga that becomes a hidden owner of Professional, Offering, Trust, Healthcare, or Payment status.

## 17. Provider Integrations

### 17.1 Trust Verification / Screening

```text
Trust Verification
→ provider-neutral screening / credential port
→ Checkr, Certn, manual, or approved adapter
→ external provider
→ verified + deduplicated + translated result
→ VerificationCheck / ProfessionalLicenseCredential / FCRA workflow transition
```

Rules:

- vendor-hosted collection is preferred for SSNs and highly sensitive background-screening data;
- Workin Ants must not store raw SSNs or complete provider reports in ordinary application tables;
- Trust owns status translation and check/provider relationship;
- webhook verification uses SH-059;
- provider-event dedupe must use owner-specific truth through SH-060;
- **current schema lacks a robust Trust processed-provider-event ledger**; external webhook activation is blocked by Unresolved Decision U-04 until that owner record is approved;
- reconcile stale/pending checks through SH-062;
- a failed check must not automatically cause an illegal or unreviewed adverse action; FCRA workflow remains legal-gated.

### 17.2 Payment / Payout / Tax

```text
Payment / Payout / Tax
→ provider-neutral payment / Connect / tax / KYC ports
→ Stripe / Stripe Connect / Stripe Tax and future approved tax/KYC adapters
→ external provider
→ signature-verified + ProcessedStripeEvent-deduplicated + translated result
→ Payment-owned record transition
→ Order owner command when transaction truth must change
```

Rules:

- `ProcessedStripeEvent` is Stripe dedupe truth, not generic audit;
- provider balances are not Workin Ants wallet truth;
- KYC, tax, and payout account retain canonical statuses even if provider vocabulary changes;
- Payment must not directly set `Order.status`;
- sales-tax location/evidence selection remains Payment tax policy; the unresolved global SH-120 jurisdiction helper must not be silently adopted.

### 17.3 Healthcare / BAA

```text
Healthcare
→ provider-neutral BAA/e-sign port
→ selected approved BAA/e-sign adapter
→ external provider
→ signature-verified + owner-deduplicated + translated result
→ BaaAgreement transition
→ HealthcareComplianceProfile readiness reevaluation
```

Rules:

- the specific BAA/e-sign provider is not canonically selected in the supplied evidence;
- the current schema lacks a robust healthcare processed-provider-event record;
- immutable BAA document/version/signer proof and legal-party semantics are incomplete;
- therefore automated BAA provider activation is **legal/architecture gated** until U-07/U-08 are resolved;
- Healthcare may still implement provider-neutral ports and manual/admin transition paths that do not pretend missing legal proof is complete.

### 17.4 Marketplace Supply

Marketplace Supply does not own Search, Media, Digital Goods, Video, AI Taxonomy, or payment provider adapters. It consumes their public owner interfaces. A future adapter added for an Offering-specific external fulfillment concern must have an explicit owner ruling before it is placed in Marketplace.

### Provider operational failures

All provider owners use Observability for normalized integration failures and service health. `IntegrationFailure` never replaces `VerificationCheck.status`, `BaaAgreement.status`, `PayoutTransfer.status`, or other owner truth.

## 18. Search / Projection Boundaries

### Source projection ownership

- Professional Eligibility builds the approved public ProfessionalProfile source projection.
- Marketplace Supply builds the approved public Offering source projection.
- Trust supplies safe verification/badge evidence through its public interface or public-ready projection input; Search must not inspect raw checks/reports.
- Healthcare supplies healthcare public-readiness decisions; Search must not infer healthcare status from a generic flag.
- Payment financial state is generally not a public search projection and must not leak into index documents unless a separately approved public field is explicitly defined.

### Indexing/de-indexing triggers

Relevant changes include:

- ProfessionalProfile active/paused/suspended/archived;
- professional public-readiness decision change;
- Offering active/paused/restricted/rejected/archived;
- TrustBadge active/suspended/expired/revoked where displayed;
- verification readiness change that affects public eligibility;
- healthcare readiness change affecting public eligibility;
- moderation/DMCA/hold restriction;
- Privacy erasure/de-index instruction;
- taxonomy/public projection field changes;
- approved entitlement-based search signal change, where Track/Search architecture explicitly permits it.

### Hard boundary

Source Modules call **SH-091**. They do not write `SearchUpsertEvent` directly and do not call Typesense. Search must be rebuildable from approved source projections and must never reconstruct readiness from `stripeReady`, `isPublic`, `trustScore`, or provider payloads.

## 19. Media / File Boundaries

### Contextual ownership

- `OfferingMedia` meaning/order belongs to Marketplace Supply.
- Verification credential/check evidence context belongs to Trust.
- BAA/document healthcare context belongs to Healthcare.
- any financial/tax document reference meaning belongs to Payment, subject to provider-hosted sensitive-data policy.

### File mechanics

Media / File Access owns:

- upload policy/session;
- binary validation;
- malware scan;
- metadata/GPS scrubbing;
- processing/readiness proof;
- private object keys/storage;
- generic access grants and signed URLs;
- storage deletion execution.

### Attachment / access rules

- use a ready `MediaAsset`; do not attach unvalidated object-store keys;
- contextual owner decides whether the business relationship permits the file to be attached/viewed;
- Media generates the signed credential only after contextual authorization is supplied;
- healthcare-sensitive or financial/screening evidence access may require SH-030 sensitive-access logging;
- permanent public URLs are forbidden for private verification, BAA, tax, payout, or protected digital-delivery evidence;
- raw provider reports/SSNs should remain provider-hosted whenever possible rather than becoming MediaAsset payloads.

## 20. Privacy / Retention

Privacy / Data Erasure owns request intake, legal-request lifecycle, cross-service orchestration, export bundles, and `DataRetentionExemption` records. CL-03 Modules implement owner-specific executors.

### Professional Eligibility executor

- enumerate ProfessionalProfile personal fields and dependent owned projections;
- erase/anonymize fields permitted by Privacy instructions;
- preserve links required by retained Orders/legal records only under a Privacy-recorded exemption;
- do not turn profile archive into legal erasure.

### Trust executor

- enumerate verification/check/license/badge/adverse-action records and provider resources;
- avoid deleting legally required FCRA/security proof without approved retention ruling;
- delete provider resources through provider-owner adapter where permitted;
- do not erase Audit proof needed to prove the erasure action itself;
- retention periods for screening/adverse-action evidence remain legal-gated where not supplied.

### Marketplace executor

- distinguish product archive/delete from legal erasure;
- anonymize/remove personal copy where permitted while preserving Order-referenced commercial records as directed;
- detach/delete Media context only through Media owner mechanics;
- request Search removal, never treat index deletion as database erasure.

### Payment executor

- enumerate KYC/tax/payout/balance/reporting/sales-tax records and provider references;
- preserve legally required financial/tax/fraud records using a Privacy-recorded retention exemption;
- anonymize nonessential personal metadata where allowed;
- provider deletion is conditional on legal retention and provider capability.

### Healthcare executor

- enumerate healthcare profile/BAA/boundary/admin policy records and provider resources;
- preserve BAA/legal proof when retention rules require it;
- execute Media/provider deletion only through their owners/adapters;
- healthcare retention specifics remain legal-gated where the source set is silent.

## 21. Audit and Observability

### Audit

Use **SH-029 `appendAuditEvent`** for generic proof of important actions such as:

- profile activation/suspension/reinstatement/archive;
- verification requirement/package/admin/manual review changes;
- adverse-action/admin decisions;
- Offering publication/restriction/restoration overrides;
- payout request approvals/blocks/manual adjustments;
- BAA/admin-policy/boundary admin changes.

Use **SH-030 `recordSensitiveAccess`** for protected reads/credential issuance such as:

- tax profile/tax dashboard/payout-account/balance views;
- healthcare payload view/redaction/block;
- restricted screening/license/report evidence access;
- private BAA document access where sensitivity policy requires.

Audit rows never replace VerificationCheck, FCRA workflow, PayoutRequest/Transfer, BaaAgreement, Offering, or profile state.

### Domain event truth

When a Module has or requires a domain lifecycle event ledger, append-only mechanics may be shared through SH-031, but the record remains owner-specific. `AuditEvent` is not a substitute for a missing domain event that consumers need for reliable workflow reaction.

### Observability

- create/propagate request and correlation IDs;
- structured logs must carry safe IDs, operation name, attempt, duration, result class, and provider correlation references where safe;
- use `IntegrationFailure`, queue telemetry, metrics, and incidents for operational failures;
- telemetry must be allowlisted/redacted through SH-034/SH-078 principles;
- never log PHI, raw background reports, SSNs, tax identifiers, payout credentials, secrets, full BAA documents, or provider webhook secrets.

## 22. Security Boundaries

1. Validate all server/action/webhook/provider inputs at the trust boundary; do not pass raw provider payloads into domain code.
2. Enforce authorization server-side and, where root architecture requires, through RLS; UI hiding is not permission.
3. Require step-up for approved sensitive financial actions.
4. Keep provider secrets in server-side secret/configuration infrastructure; never persist them in business tables or send them to clients.
5. Verify webhook raw bodies/signatures before JSON-derived side effects.
6. Deduplicate webhook events before business side effects.
7. Use idempotency for check initiation, BAA send, Offering publication, payout request/transfer, tax/payment callbacks, hold requests, and other replay-prone commands.
8. Prefer provider-hosted collection for SSNs, background-report details, and tax information. Store minimized references/statuses instead.
9. Store professional license identifiers masked/hashed where full value is not required; use shared normalize/hash/encryption primitives when the owning Module requires them.
10. Treat BAA, verification, tax, payout, healthcare, and private Offering assets as private by default.
11. Signed file URLs/tokens must be short-lived and issued only after contextual entitlement plus any healthcare/financial access policy.
12. Rate-limit profile provisioning, screening initiation, provider session creation, payout requests, sensitive reads, and webhook endpoints according to root security standards.
13. Apply optimistic concurrency/locking to status transitions and money/check workflows.
14. Minimize provider input and telemetry; never serialize whole Prisma aggregates to providers/logs.
15. Unknown provider status/event types fail safely and become operationally visible; they do not default to an allowed/passed state.

## 23. Testing Architecture

### Module unit tests

Each owner tests its own invariants, transition guards, pricing/readiness rules, provider-status mapping, reason-code generation, and privacy mappings without reaching across Module repositories.

### Public-interface contract tests

Required contracts include:

- SH-016 Professional readiness;
- SH-017/018 Trust requirements/readiness;
- SH-019 Financial readiness;
- SH-020 Healthcare readiness;
- Marketplace Offering eligibility-context/publication interfaces;
- Payment ↔ Order normalized payment/tax commands;
- owner-fact queries used by authorization/gates;
- Privacy executors;
- Search source projection + refresh request.

Contract tests must prove that consumers do not need direct owner-table access.

### Lifecycle transition tests

For every lifecycle implemented, test:

- allowed transitions;
- denied transitions;
- expected-version conflicts;
- source decision/hold references where required;
- terminal/archival behavior;
- duplicate command replay;
- emitted event/outbox behavior.

### Cross-Module integration tests

At minimum:

- profile activation calls owner readiness APIs and does not mutate their records;
- Offering publication is denied when Trust/Healthcare/Hold/Entitlement returns denial and becomes active only through Marketplace;
- a Trust expiry change causes reevaluation/search removal without Search reading Trust tables;
- Payment KYC is independent from Trust screening;
- payout uses step-up/hold/financial readiness and does not mutate Order;
- healthcare admin access layers Role authorization and Healthcare redaction policy;
- moderation executes against profile/Offering through target-owner command;
- Privacy orchestrates and owner executors report outcomes.

### Provider adapter tests

- signature validation fixtures;
- duplicate event replay;
- unknown status/event;
- out-of-order event handling;
- provider timeout/rate limit/retryability;
- normalized mapping contract;
- reconciliation after missed webhook;
- no raw sensitive payload persistence/logging.

### Concurrency/idempotency tests

- duplicate ProfessionalProfile creation;
- competing profile activation/suspension;
- concurrent Offering publish/edit/restriction;
- duplicate verification initiation/recheck;
- duplicate provider callback;
- double payout request/transfer;
- balance projection replay;
- duplicate BAA webhook/send;
- Search/notification side-effect replay.

### Compliance/privacy tests

- ConsentLog proof is queried, not duplicated as permission;
- expired/revoked verification blocks affected action;
- TrustBadge alone cannot satisfy verification readiness;
- healthcare-sensitive targets respect boundary/admin policy;
- sensitive access creates AccessAuditLog where required;
- legal retention prevents destructive erasure and Privacy receives retained disposition;
- profile archive is not treated as legal erasure;
- financial views require step-up.

### Critical CL-03 E2E journeys

1. User → ProfessionalProfile draft → action-specific activation decision.
2. Professional → Offering draft/details/pricing/media/classification → blocked publication → remediation → active publication → search refresh.
3. Verification-required professional → standalone consent → check → provider/manual result → readiness change.
4. Healthcare-triggered Offering → BAA/readiness gate → activation only after permitted result.
5. Financial onboarding → KYC/tax/payout account → financial readiness → payout request/transfer result.
6. Active seller loses required verification or receives hold → affected public/action readiness changes without ownership theft.
7. Privacy request executes across CL-03 owners with retention-aware outcomes.

## 24. Invariants

### Rules coding agents must never violate

1. CL-03 is not a data owner; never create a `ClusterReadiness` source-of-truth aggregate simply because multiple Modules collaborate.
2. `ProfessionalProfile` is the seller actor; a base `User` must not directly own an Offering or receive seller lifecycle state.
3. Only Professional Eligibility changes `ProfessionalProfile.status`.
4. `ProfessionalProfile.status=active` is not proof that every seller action is allowed.
5. Do not use `stripeReady`, `canPayout`, `isVerified`, `backgroundPassed`, `isHealthcareProvider`, or equivalent local booleans as authoritative gates.
6. Trust screening and Payment KYC are separate lifecycles and must not share one verification row/status.
7. `TrustBadge` is projection; `VerificationCheck`/credential truth determines Trust readiness.
8. ConsentLog proves acceptance; Trust/Healthcare still decide whether the proof is sufficient.
9. A failed screening result does not automatically authorize adverse action outside the approved FCRA workflow.
10. Only Marketplace Supply changes `Offering.status`.
11. Marketplace may consume professional readiness but must not reproduce Trust/Healthcare/Payment policy.
12. Marketplace does not own DigitalGoodsPolicy, DigitalDownloadAsset/grants, or `SalesTaxLineItem` lifecycle.
13. `PricingTier` is current Offering price truth; Order owns historical transaction snapshots.
14. Search documents, `SearchUpsertEvent`, and Typesense are not professional/Offering truth.
15. Source Modules request Search work through SH-091; they do not call Typesense or write Search queue rows directly.
16. Payment executes processor rails; Transaction / Order remains transaction lifecycle truth.
17. Payment must not write `Order.status` or `OrderEvent` directly.
18. Processor-held funds must not be modeled or labeled as a Workin Ants wallet/escrow.
19. `ProfessionalBalanceLedgerEntry` is append-only financial projection truth; mutable balance fields must not replace it.
20. Historical commission/fee policy is consumed from Order snapshots, not recalculated from today's Track plan.
21. TaxProfile is not sales-tax calculation truth.
22. Healthcare is triggered by context; do not add a blanket `User.isHealthcareProvider` source flag.
23. Role / Authority determines whether an actor may attempt access; Healthcare determines healthcare-specific payload handling.
24. `HealthcareDataBoundary` and BAA truth must not be replaced by generic `DataSensitivity` or Offering booleans.
25. ComplianceHold is the platform stop sign; no Module creates a competing generic blocked system.
26. Provider state is never accepted before signature verification, event dedupe, status translation, and owner transition validation.
27. Provider-event dedupe records stay with their provider-owning Module even when mechanics are shared.
28. AuditEvent/AccessAuditLog do not replace domain lifecycle events or provider dedupe truth.
29. IntegrationFailure/QueueJob/SystemEvent do not replace business status.
30. MediaAsset owns file mechanics; CL-03 contextual owners own attachment/business entitlement only.
31. No permanent public URL for private verification, BAA, tax, payout, healthcare, or protected Offering material.
32. Privacy / Data Erasure owns the request/workflow; each CL-03 owner only executes against its own records/providers.
33. Product archive/delete is not legal erasure.
34. Cross-Module reads use public owner interfaces/approved DTOs; direct cross-domain repositories are exceptional and require architecture approval.
35. Shared operations must be referenced/reused by `SH-###`; do not implement aliases as new infrastructure.
36. Unknown/unresolved legal or architecture policy must fail closed or remain unavailable; the first coding agent must not invent it.

## 25. Prohibited Duplicate Implementations

The following are examples of files/services a coding agent must **not** create as independent systems in CL-03:

| Do not create | Use instead |
| --- | --- |
| `professionalAuth.ts`, `offeringAuthService.ts`, `payoutAuth.ts`, `healthcareAdminAuth.ts` | SH-001 + SH-002 with owner-supplied facts/actions |
| `professionalPremium.ts`, `sellerPlanFlags.ts`, `commissionEntitlement.ts` | SH-005 Track Entitlement |
| `professionalBlocked.ts`, `offeringHold.ts`, `payoutBlockedService.ts` | SH-011/012/013 Compliance Hold; local lifecycle consequences only |
| `professionalVerificationService` inside Marketplace | Trust SH-017/018 |
| `stripeReadyService.ts`, `canPayout.ts` in Professional Eligibility | Payment SH-019 |
| `healthcareFlagService.ts` / `isHealthcareProvider.ts` | Healthcare SH-020 + boundary interfaces |
| `searchIndexOffering.ts` / direct Typesense client | SH-091; Search owns execution |
| local `SearchUpsertEvent` repository in CL-03 | Search / Public Visibility interface |
| `offeringFileUpload.ts`, Trust/BAA presigned URL utilities | Media / File Access public operations |
| CL-03 `ConsentProof` table or `acceptedBackgroundTerms` boolean | ConsentLog through SH-008/010 |
| generic `ClusterAuditLog` | SH-029 / SH-030; owner-specific domain event ledger where required |
| `WebhookLog` used as dedupe | SH-060 with provider-owner processed-event truth |
| one global `ProviderStatus` enum | SH-061 adapter mapping to each owner's canonical enum |
| `professionalPrivacyRequest.ts` or `offeringErasureWorkflow.ts` | Privacy orchestration + SH-095/096/097 executors |
| Marketplace `SalesTaxLineItem` service/repository | Payment / Payout / Tax owner |
| Marketplace `DigitalDownloadAsset` / `DigitalGoodsPolicy` lifecycle | Digital Goods Access owner |
| Trust-owned `screeningOrder` payment subsystem | Order SH-107 + Payment rail |
| mutable `professionalWalletBalance` | Payment-owned append-only balance ledger/query |
| generic `CL03ProviderAdapter` | owner-local provider ports/adapters |
| cluster-wide `ReadinessStatus` lifecycle | Professional action decision composition; underlying owner states remain separate |

## 26. Deferred / Unresolved Decisions

| ID | Question | Why unresolved | Missing evidence / conflict | Blocks |
| --- | --- | --- | --- | --- |
| U-01 | Must full KYC/tax/payout-account readiness be satisfied before ProfessionalProfile activation, Offering publication, Gig response, or only before money receipt/payout? | Sources require “relevant” financial readiness but do not fix timing per action. | Product/compliance policy decision. | Final action-to-gate matrix for activation/publication/respond. Drafting and payout workflows are not blocked. |
| U-02 | What is the final shared ownership treatment of `ProfileStatus` used by ProfessionalProfile and CandidateProfile? | Registry names Professional Eligibility; glossary says shared enum with separate profile lifecycle usage. | Root/module enum-governance ruling. | Enum relocation/splitting only; Professional Eligibility can still own ProfessionalProfile transitions. |
| U-03 | Does `VerificationConsent` remain, and if so which fields are screening linkage versus duplicate ConsentLog proof? | Current schema duplicates consent-like evidence while Consent is canonical proof owner. | Approved consent data model. | New screening-consent schema/API writes beyond safe ConsentLog linkage. |
| U-04 | What owner-specific processed-provider-event schema does Trust use? | SH-060 requires separate provider truth; current check only has last-provider-event style fields. | Trust provider-event schema/retention. | Production screening webhook side effects. Manual/stub flows are not blocked. |
| U-05 | How is `ProfessionalLicenseCredential` linked to `VerificationCheck` when a license verification is performed? | Both records exist and overlap verification attempt/result semantics without an explicit relation. | Data-model ruling. | Durable credential-to-check provenance; basic credential lifecycle can proceed only with an explicit feature-local approved contract. |
| U-06 | What exact FCRA notice artifact/version/delivery/retention proof and transition rules are required? | Schema has workflow timestamps/status but incomplete document/delivery proof. | Legal/compliance ruling and evidence model. | Automated adverse-action production workflow. Verification that does not trigger adverse action can proceed. |
| U-07 | Which parties/signers/countersigners and immutable document/version/hash proof must a `BaaAgreement` preserve? | Current BAA model is insufficient to prove full execution semantics. | Healthcare/legal/e-sign decision. | Production BAA automation and final legal-compliance claim. |
| U-08 | What owner-specific processed-provider-event schema/provider is used for Healthcare BAA callbacks? | No canonical provider or dedupe record is established. | Provider selection + Healthcare provider-event schema. | Automated BAA webhook. Manual provider-neutral workflow may proceed. |
| U-09 | How is `HealthcareDataBoundary` safely cleared/retired and how does inherited boundary propagation work? | Current schema is unique presence/absence with no lifecycle/history. | Healthcare boundary lifecycle ruling. | Boundary removal/propagation automation; basic explicit marking/query is possible. |
| U-10 | How is `HealthcareAdminAccessPolicy` versioned/effective and what is precedence when parent/child targets differ? | Current schema is one mutable exact-target mode. | Healthcare policy version/precedence design. | Audit-reproducible policy history and inherited access behavior. Exact-target current policy can be used only if feature spec limits scope. |
| U-11 | What does `HealthcareAccessDecision.blocked` versus `denied` mean canonically? | Vocabulary exists without clear semantic distinction. | Healthcare contract ruling. | Stable shared access-response semantics. |
| U-12 | Who owns generic `DataSensitivity` vocabulary/derivation, and how does it relate to healthcare boundaries? | Multiple modules reference sensitivity; Healthcare boundary is more specific. | Root/shared vocabulary ruling. | Cross-domain generic sensitivity automation; healthcare explicit boundary not blocked. |
| U-13 | What is `Offering.isFeatured` and who owns promotion/ranking policy? | Could conflict with Search ranking, paid ads, or Track entitlement. | Search/entitlement/product ruling. | Any feature behavior based on `isFeatured`. Field must remain inert. |
| U-14 | What is the final relationship among `Offering.isPublic`, `Offering.status`, hidden/frozen/takedown timestamps, moderation, and Search readiness? | Schema contains overlapping signals. | Marketplace/Moderation/Search ruling. | Independent writes/reads of `isPublic`; publication can use `Offering.status` + owner public-readiness contract. |
| U-15 | How are `bundle` Offerings composed? | `OfferingKind.bundle` exists but no BundleDetails/component model is present. | Marketplace schema/UX ruling. | Bundle creation/publication. Service/product/course remain unblocked. |
| U-16 | Is `Offering.priceFromCents` a mandatory stored projection and what rebuild semantics apply? | Current schema duplicates current PricingTier-derived minimum. | Marketplace projection ruling. | Independent writes must not occur; implementation may calculate at read time until approved. |
| U-17 | What is the approved fate of overlapping ProfessionalProfile fields (`stripeAccountId`, `stripeReady`, verification timestamps, `trustScore`)? | They conflict with Payment/Trust owner records. | Migration/compatibility decision. | Schema cleanup. Gate logic is not blocked because these fields are non-authoritative. |
| U-18 | Exact legal retention periods for verification, adverse action, healthcare, BAA, KYC/tax/payout proof. | Compliance pack identifies responsibilities but not all durations. | Legal counsel/compliance retention policy. | Destructive privacy deletion and production retention scheduler for affected records. |
| U-19 | Exact provider and policy for non-Stripe tax/KYC or future screening/BAA alternatives. | Registry names possible technologies but provider substitution remains open. | Provider selection/contract. | Provider-specific adapter activation only; domain ports can proceed. |

## 27. Architecture Decision Summary

### Confirmed binding rulings

1. CL-03 contains exactly five primary Deep Modules: Professional Eligibility, Trust Verification / Screening, Marketplace Supply, Payment / Payout / Tax, and Healthcare / Regulated Services.
2. The Cluster coordinates them but owns no lifecycle or source record.
3. `ProfessionalProfile` is seller actor truth; Professional Eligibility owns its status and action-readiness composition.
4. Trust owns verification requirements/checks/credentials/FCRA/TrustBadge; Payment KYC is separate.
5. Marketplace owns Offering lifecycle and current pricing/supply shape; it consumes readiness rather than owning it.
6. Payment owns financial/provider/tax/payout truth; Order remains transaction truth.
7. Healthcare owns healthcare lane, BAA, data boundaries, and healthcare-specific payload policy; general authorization stays external.
8. Digital-goods lifecycle remains outside Marketplace; sales-tax line-item truth remains Payment-owned.
9. Track Entitlement, ComplianceHold, Consent, Search, Media, Privacy, Audit, Notification, and Observability remain external owner rails.
10. Cross-Module collaboration uses public interfaces/events, not direct owner repositories by default.
11. Canonical Shared Operations are referenced by permanent ID and must not be rebuilt locally.
12. Search remains a rebuildable projection and provider state remains an input, not source truth.
13. Generic audit/ops records do not substitute for domain events, provider dedupe, or lifecycle truth.

### Proposed Rulings for approval

**PR-01 — No CL-03 aggregate/repository.** The Cluster has no persistent `ProfessionalSupplyReadiness` record. Professional Eligibility remains the readiness composer for seller actions.

**PR-02 — Shared ProfileStatus vocabulary, separate lifecycle authority.** Keep the existing shared enum for now; Professional Eligibility exclusively controls transitions on `ProfessionalProfile`, Candidate owner controls CandidateProfile transitions. Do not move Candidate lifecycle into CL-03.

**PR-03 — Overlapping ProfessionalProfile fields are non-authoritative.** Do not read or write `stripeReady`, `stripeAccountId`, verification summary timestamps, or `trustScore` for gating. Migration/removal can be separately planned.

**PR-04 — Review metrics on ProfessionalProfile are derived projections only.** If retained, `ratingAverage` and `ratingCount` are rebuildable from Review-owned truth.

**PR-05 — OfferingTag contextual ownership split.** Taxonomy owns term/assignment validity semantics; Marketplace owns attaching/detaching the accepted tag to an Offering.

**PR-06 — `priceFromCents` is derived.** It must be computed from active PricingTiers or maintained only as a rebuildable projection; it is never independently authored price truth.

**PR-07 — `Offering.isPublic` is projection/compatibility only; `isFeatured` is inert.** Publication authorization uses Offering lifecycle plus owner public-readiness decisions. Do not implement promotion behavior until U-13 is resolved.

**PR-08 — BAA execution truth stays on `BaaAgreement`.** HealthcareComplianceProfile may summarize lane readiness, but it must not be read instead of current BAA evidence and must only change as a Healthcare-owned consequence of that evidence.

**PR-09 — Trust and Healthcare need separate processed-provider-event truth before production webhook automation.** They may reuse SH-060 mechanics but may not reuse `ProcessedStripeEvent`, AuditEvent, or each other's records.

**PR-10 — Professional readiness is evaluated from current owner truth, not persisted as a new eligibility-decision source table in MVP.** If legal/audit needs later require immutable decision snapshots, add them through a separate architecture ruling; generic AuditEvent alone must not be mistaken for that source truth.

## 28. Coding-Agent Usage

Before changing CL-03, an implementation agent must read, in order appropriate to the current repository:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md`;
5. this `context/professional-supply-readiness/architecture.md`;
6. `context/professional-supply-readiness/build-plan.md`;
7. the target Module architecture;
8. the target Module implementation plan;
9. the public-interface sections of every dependency Module touched by the feature;
10. the current progress tracker.

The agent must then:

- confirm the numbered feature being implemented;
- confirm the previous feature exit gate passed;
- identify every owner record being read or written;
- map every shared operation to its `SH-###` identifier;
- stop if a required operation is Proposed/Unresolved and the feature would commit schema/API semantics without approval;
- reject direct cross-domain repository access unless the architecture explicitly authorizes it;
- update this file if and only if a binding architectural decision legitimately changes.
