# Professional Supply & Readiness Build Plan

> **Cluster ID:** CL-03  
> **Cluster name:** Professional Supply & Readiness  
> **Repository target:** `context/professional-supply-readiness/build-plan.md`  
> **Architecture dependency:** `context/professional-supply-readiness/architecture.md`  
> **Plan status:** Ordered implementation roadmap; it does not redefine architecture

## Core Principle

Build CL-03 as a sequence of **vertical, owner-preserving, testable slices**. Each numbered feature must make a real seller, admin, worker, provider adapter, or consuming Module behavior observable while leaving source truth with the correct Deep Module.

The preferred slice is:

```text
usable / observable behavior
→ owning application/domain service
→ authoritative owner database state
→ stable public contracts
→ permissions / compliance gates
→ events / jobs / provider effects
→ tests
→ exit gate
```

A compliance capability does not need artificial UI. A vertical slice may terminate in a stable Module public interface, a worker result, a restricted admin surface, or provider-normalized state as long as the behavior is concrete and verifiable.

Do not create an early “CL-03 infrastructure framework” that owns no business outcome. Canonical event, job, idempotency, authorization, audit, media, Search, consent, hold, and entitlement primitives must be consumed from their existing owners.

## Build Rules

1. Follow the root Workin Ants architecture, code standards, Canonical Shared Operations Registry, and the CL-03 architecture.
2. Implement one numbered feature at a time. A feature may be split into implementation slices, but the next number does not start until the current exit gate passes.
3. Do not expand CL-03 scope into Gigs, Orders, Booking, Digital Goods, Search, Media, Moderation, Privacy, Notification, or Track Entitlement source ownership.
4. Do not redesign Module ownership for implementation convenience.
5. Reuse confirmed canonical Shared Operations by permanent `SH-###` identifier; do not recreate aliases locally.
6. A Proposed Shared Operation may guide planning but cannot become a new platform-wide schema/API dependency until approved.
7. Every mutation validates input, authenticated/system actor, authorization, expected owner state, and concurrency/idempotency requirements.
8. Every provider is isolated behind its owner’s provider-neutral port and adapter.
9. Every provider event is signature verified, deduplicated through owner-specific truth, translated, and transition-validated before side effects.
10. Every asynchronous operation is idempotent, retry-classified, observable, and dead-letter visible.
11. Generic audit/observability records never replace owner lifecycle or domain/provider-event truth.
12. Search is downstream projection. CL-03 source owners request projection work; they never write Search queue state or call Typesense directly.
13. Privacy remains Privacy-owned. CL-03 implements only owner-specific enumeration/execution/retention handlers.
14. `ComplianceHold` remains the reusable stop sign. No feature introduces generic local blocked flags.
15. Track Subscription & Entitlement remains commercial-policy truth. No feature introduces `isPremium`, `sellerPlan`, `canSell`, or commission-rate booleans as local truth.
16. Media / File Access remains file-mechanics truth. No feature implements local storage scanning or signed-URL infrastructure.
17. Provider state is never treated as Workin Ants domain state.
18. Unresolved legal/architectural questions are not silently invented. A feature must either resolve them through architecture approval, constrain itself to a supported path, or leave the affected path disabled.
19. Each phase ends with tests and a concrete exit gate.
20. A build-plan change cannot silently override `architecture.md`; change architecture first when a binding decision changes.

## Dependencies and Preconditions

### Root / platform prerequisites

Before Feature 01 implementation begins, the repository must provide or have an approved implementation plan for:

- Prisma/PostgreSQL access using the root data layer;
- Identity & Access actor resolution (**SH-001**);
- Role / Authority authorization (**SH-002**);
- Track entitlement lookup (**SH-005**);
- ComplianceHold evaluation/request/release (**SH-011/012/013**);
- shared idempotency and concurrency primitives (**SH-044**, locks/concurrency per root architecture);
- transactional domain event/outbox support (**SH-046**) before a feature relies on asynchronous downstream correctness;
- reliable jobs/retries (**SH-047/048**) before scheduled/provider reconciliation is enabled;
- Audit and sensitive-access interfaces (**SH-029/030**);
- Search refresh interface (**SH-091**) before public projection is enabled;
- Privacy target protocol (**SH-095/096/097**) before production privacy fulfillment is claimed.

If one of these is not yet implemented, the numbered feature may define and contract-test the dependency boundary, but it must not create a CL-03-owned duplicate implementation.

### Upstream cluster prerequisites

- **CL-01:** authenticated User, Role / Authority, ConsentLog, professional-track entitlement decisions.
- **CL-02:** accepted taxonomy IDs, taxonomy requirement resolution/assignment validation, Search public interface.
- **CL-09:** ComplianceHold, Audit, Observability, and Moderation public interfaces for relevant late-stage integrations.

### Neighboring cluster contracts

These may initially be stubbed behind stable interfaces so CL-03 can progress without taking their ownership:

- **CL-04 Transaction / Order:** `createChargeableOrder`, Order pricing/payment snapshot queries, verified payment/refund outcome commands.
- **CL-04 Gig / Demand:** narrow Gig requirement/owner context for `respond_to_gig` readiness.
- **CL-05 Media:** ready MediaAsset/context attachment contract.
- **CL-05 Digital Goods / Video:** delivery-readiness contracts for downloadable products/courses.
- **CL-07 Notification:** request interface.
- **CL-08 Privacy:** fulfillment protocol.

### Existing source-of-truth records

The current Prisma evidence already defines the main CL-03 records. Features should use those records rather than introducing parallel aggregates. Schema changes are permitted only where the feature requires a missing invariant/evidence record and the corresponding architecture ruling has been approved.

### Provider prerequisites

- Trust supports Checkr/Certn-style provider-neutral adapters plus manual review. Production callback processing is blocked until Trust gets approved owner-specific provider-event dedupe truth.
- Payment uses Stripe/Stripe Connect/Stripe Tax as current rails where the provider path is in scope. Other KYC/tax provider choices remain adapter concerns.
- Healthcare BAA/e-sign provider is not canonically selected. Manual/provider-neutral BAA lifecycle may be built; automated production webhook flow remains gated by the architecture's BAA proof/provider-event unresolved decisions.

### Dependencies that must not block early vertical slices

The following do **not** block draft profile/Offering work:

- completed KYC;
- completed background check;
- signed BAA;
- live Search provider;
- live Digital Goods/Video provider;
- live screening provider;
- live BAA provider.

Those gates become mandatory only when the corresponding action reaches the feature that owns/enforces them.

---

# Phase 1 — Seller and Supply Foundations

## 01 — Professional Profile Foundation

Create the authoritative seller-role profile and its safe baseline lifecycle without confusing profile state with verification, healthcare, or financial readiness.

### Objective

A User can obtain at most one `ProfessionalProfile`, view/update allowed seller identity fields, and exercise the initially approved profile lifecycle commands through Professional Eligibility.

### User-visible / Observable Result

- An authenticated User can create or retrieve their seller profile idempotently.
- The profile begins in the schema-supported baseline state and can be read through a stable public context query.
- Allowed profile edits are persisted by Professional Eligibility.
- Authorized lifecycle transitions supported by the approved Feature 01 transition table are observable and emit owner events.
- A second concurrent create request returns the same/duplicate-safe result instead of creating a second seller identity.

### Owning Module(s)

- **Professional Eligibility** — sole business owner.

No other CL-03 Module writes `ProfessionalProfile`.

### Dependencies

- Identity & Access actor context.
- Role / Authority.
- Current Prisma `ProfessionalProfile` and `ProfileStatus`.
- Root idempotency/concurrency/event infrastructure.
- Architecture PR-02 may remain pending as long as implementation does not relocate/split `ProfileStatus`; Professional Eligibility still owns transitions on its rows.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor`** — Identity & Access. Use at every profile command/query entry point. Local policy: which profile action is requested. **Do not rebuild:** `professionalAuth.ts` or current-user helper.
- **SH-002 `authorizeResourceAction`** — Role / Authority. Use for create/edit/lifecycle actions. Local policy: ProfessionalProfile ownership facts and action names. **Do not rebuild:** seller-specific role engine.
- **SH-011 `evaluateComplianceHold`** — Hold owner. Use only for lifecycle actions the approved transition policy makes hold-sensitive. Local policy: how a hold affects that transition. **Do not rebuild:** profile blocked flag.
- **SH-044 `executeIdempotentCommand`** — platform infrastructure. Use for profile provisioning and replay-prone transitions. Local policy: semantic fingerprint and conflict response. **Do not rebuild:** local idempotency table/helper.
- **SH-046 `publishDomainEvent`** — event/outbox infrastructure. Publish owner events after successful mutation. Local policy: event names/payload/version. **Do not rebuild:** emit-after-write code with no outbox.
- **SH-114 `provisionOneToOneProfile`** — shared mechanism, separate profile truth. Use for one User → one ProfessionalProfile creation. Local policy: Professional defaults and owned invariants. **Do not rebuild:** generic profile lifecycle.

### Data / Schema

Use `ProfessionalProfile` and its existing unique User relationship. No separate `Seller`, `Provider`, or cluster readiness record is introduced.

Treat `stripeReady`, `stripeAccountId`, `verifiedAt`, `verificationExpiresAt`, `trustScore`, `ratingAverage`, and `ratingCount` as non-authoritative compatibility/projection fields per architecture. Feature 01 must not add gate logic around them.

If current Prisma uniqueness cannot enforce one profile per User, that is a schema defect requiring an explicit migration inside this feature. Do not solve it only with frontend checks.

### Public Interfaces

Introduce/complete:

- `createProfessionalProfile`;
- `getProfessionalProfileContext`;
- `updateProfessionalProfile`;
- owner lifecycle commands for the approved Feature 01 transitions;
- version/expected-state contract for mutation conflicts.

Do not expose a `setProfessionalStatus(status)` public method that bypasses transition policy.

### Logic

- Validate profile input server-side.
- Resolve actor and verify User/profile relationship.
- Provision idempotently.
- Keep profile lifecycle separate from downstream readiness.
- Define explicit mutable versus immutable profile fields.
- Apply only approved state transitions; unsupported enum transitions return a stable conflict/validation result.
- Preserve source decision/actor/reason metadata in owner event/audit context when applicable.

### UI / Administrative Surface

Where the product currently has seller onboarding/profile UI, provide:

- create/start professional profile;
- edit safe profile identity fields;
- show current profile lifecycle state;
- show that compliance/readiness is separate rather than rendering one misleading “verified” badge.

No admin UI is required solely for Feature 01 unless root product context already provides profile support tooling.

### Authorization / Compliance

- User owns their own profile management unless an approved admin/support action applies.
- No seller action is authorized from client ownership alone.
- A profile archive/suspension is not privacy erasure.
- Do not require or infer Trust/KYC/Healthcare completion just to persist a draft profile.

### Events / Jobs / Integrations

Emit versioned ProfessionalProfile created/status-changed events when a lifecycle mutation occurs. No provider job is needed.

### Failure Behavior

- Duplicate create: return canonical existing profile or deterministic conflict, not a duplicate row.
- Stale expected version/status: return conflict with current owner state.
- Hold/authority denial: no mutation.
- Event publication failure after transaction: outbox remains retryable; do not roll back already committed domain state via ad-hoc compensating status.

### Tests

- unit: field validation and transition guards;
- integration: one-to-one uniqueness, owner writes, outbox transaction;
- contract: profile context DTO contains only required owner facts;
- concurrency: simultaneous profile creation and conflicting lifecycle transition;
- authorization: owner/admin/unauthorized cases;
- privacy semantics: archive ≠ erasure.

### Out of Scope

- verification/KYC/BAA completion;
- Offering creation;
- Search indexing;
- payout onboarding;
- candidate profile lifecycle;
- removing legacy projection fields from Prisma unless a separately approved migration is required.

### Exit Gate

Feature 01 is complete only when:

1. one User cannot acquire two ProfessionalProfiles under concurrent requests;
2. all implemented profile mutations pass server authorization and explicit transition guards;
3. no implemented gate reads `stripeReady`, verification summary fields, `trustScore`, or another Module's tables directly;
4. profile events publish transactionally/reliably;
5. unit/integration/concurrency/authorization tests pass;
6. the public context query is sufficient for downstream Module contract tests without direct ProfessionalProfile repository access.

---

## 02 — Offering Draft, Shape, Pricing, Classification, and Media Context

Build Marketplace Supply's editable Offering aggregate as real seller supply while keeping compliance publication gates for a later feature.

### Objective

An authorized ProfessionalProfile can create and manage a draft Offering with one valid kind-specific shape, pricing tiers, accepted taxonomy classification, and validated presentation media context.

### User-visible / Observable Result

A professional can create/edit a draft service, product, or course; configure its details and current pricing; attach/reorder/remove ready media; and select accepted taxonomy without publishing the Offering.

Bundle creation remains unavailable until the bundle model is resolved.

### Owning Module(s)

- **Marketplace Supply** — Offering, detail, pricing, OfferingMedia, contextual OfferingTag lifecycle.
- **Taxonomy & Classification** remains owner of term/assignment validity.
- **Media / File Access** remains owner of MediaAsset mechanics.

### Dependencies

- Feature 01 ProfessionalProfile context.
- Taxonomy SH-023 and accepted IDs.
- Media ready-asset contract.
- Current Offering/detail/PricingTier/OfferingMedia schema.
- Architecture PR-05 applies to `OfferingTag` contextual ownership.

### Shared Operations Used

- **SH-001 / SH-002** — actor and authorization. Local policy: the actor controls the Offering's ProfessionalProfile. **Do not rebuild:** Offering auth service.
- **SH-003 `queryOwnerFacts`** — proposed shared contract only. If approved/available, use Professional owner DTO; otherwise use the explicit Professional public context query defined by Feature 01. **Do not build:** generic cross-domain repository.
- **SH-023 `validateTaxonomyAssignment`** — Taxonomy. Use before accepting domain/category/tag references. Local policy: which classifications Marketplace requires for each lifecycle step. **Do not rebuild:** local taxonomy validator/copy.
- **SH-090 `attachValidatedMedia`** — Media/context shared contract. Marketplace owns `OfferingMedia`; Media owns asset readiness. **Do not rebuild:** upload scanning, object-store client, signed URL generator.
- **SH-044** — idempotent create/attachment commands as needed. Local policy: command identity.
- **SH-046** — publish Offering-created/changed domain events when downstream consumers need them.

### Data / Schema

Use:

- `Offering`;
- `ServiceDetails`;
- `ProductDetails`;
- `CourseDetails`;
- `PricingTier`;
- `OfferingMedia`;
- `OfferingTag` according to PR-05.

Enforce in domain/application logic and database constraints where feasible:

- `Offering.kind` matches exactly the allowed detail record shape;
- incompatible detail records cannot coexist as an accepted state;
- PricingTier amount/currency invariants are validated;
- OfferingMedia references ready assets only;
- taxonomy IDs are canonical/active/compatible.

Do not implement `bundle` until U-15 is resolved.

Do not independently author `priceFromCents`. Calculate from active tiers at read time or maintain it only after PR-06 is approved in implementation detail.

### Public Interfaces

Introduce/complete:

- `createOfferingDraft`;
- `getOfferingManagementView`;
- `updateOfferingCore`;
- kind-specific detail upsert commands;
- PricingTier create/update/deactivate/reorder commands;
- OfferingMedia attach/detach/reorder commands;
- contextual Offering tag attach/detach command using Taxonomy validation;
- `getOfferingEligibilityContext` narrow DTO for later gate owners.

### Logic

- Require valid ProfessionalProfile relationship but do not use profile compatibility fields as readiness proof.
- Validate kind-specific shape before accepting draft as locally valid.
- Keep historical transaction pricing out of Marketplace; PricingTier edits affect future purchases only.
- Keep DigitalGoodsPolicy/DownloadAsset and Video provider state outside Marketplace.
- For downloadable product/course configuration, store only owner-approved references/configuration and defer delivery entitlement truth to CL-05.
- Keep `Offering.isFeatured` behavior inert.
- Do not let `isPublic` become an independent lifecycle mutation.

### UI / Administrative Surface

Where Marketplace UI is in scope:

- draft editor for service/product/course;
- pricing tier manager;
- taxonomy selector using canonical taxonomy data;
- media gallery based on ready MediaAssets;
- explicit “not published yet” state;
- bundle option hidden/disabled with no partial model if unresolved.

### Authorization / Compliance

- Only controlling professional/admin authority may edit.
- Drafting does not imply public eligibility.
- Taxonomy flags may be shown as upcoming requirements, but Marketplace must not mark those requirements satisfied.
- Do not block draft creation based on incomplete KYC/verification/healthcare unless a separately approved entitlement says drafting itself is unavailable.

### Events / Jobs / Integrations

- emit Offering created/updated/classification/pricing change events only where downstream needs are established;
- no Search indexing for draft;
- no payment provider call;
- no digital-delivery grant;
- no background job required except a root-approved projection recalculation if PR-06 chooses stored `priceFromCents`.

### Failure Behavior

- invalid kind/details: reject mutation without partial contradictory detail state;
- stale edit: optimistic conflict;
- invalid taxonomy: return canonical validation error;
- unready MediaAsset: reject attachment while retaining Media-owned upload state;
- external CL-05 delivery-readiness API unavailable: draft may save supported configuration, but publication is not attempted.

### Tests

- unit: kind-shape and pricing invariants;
- integration: aggregate writes, one-to-one details, media/tag joins, ownership;
- contract: Professional owner facts, Taxonomy, Media;
- concurrency: duplicate tier/media operations and stale edits;
- authorization: owner versus other professional;
- regression: no Digital Goods/SalesTax records written by Marketplace.

### Out of Scope

- publication/activation;
- Search projection;
- KYC/verification/healthcare completion;
- Order checkout;
- digital download grants;
- bundle model;
- `isFeatured` behavior.

### Exit Gate

Feature 02 is complete only when:

1. service/product/course drafts can be created and edited end to end;
2. contradictory Offering kind/detail states are rejected;
3. current PricingTier truth is owner-correct and no historical Order price is mutated;
4. taxonomy/media integrations use owner contracts rather than direct foreign repositories;
5. Marketplace writes no digital-goods or sales-tax lifecycle records;
6. bundle and `isFeatured` paths remain explicitly unavailable;
7. all unit/integration/contract/concurrency tests pass.

---

## 03 — Professional Readiness Composition Contract

Implement the Professional Eligibility decision boundary that composes other owners without creating a second compliance database.

### Objective

Consumers can ask one stable Professional Eligibility question — whether a ProfessionalProfile may perform a named seller action — and receive structured blockers/evidence sourced from the actual owner Modules.

### User-visible / Observable Result

A developer, professional onboarding surface, or consuming Module can request readiness for an approved action and see which dimension blocks it: profile lifecycle, entitlement, taxonomy-triggered verification, healthcare, hold, or financial readiness.

Actions whose policy is unresolved return an explicit unavailable/review result; they are not guessed.

### Owning Module(s)

- **Professional Eligibility** owns action-to-gate composition and final professional decision.
- Trust, Healthcare, Payment, Track, Taxonomy, and Hold remain owners of their input decisions.

### Dependencies

- Feature 01 profile context/lifecycle.
- Interfaces/contracts for SH-005, SH-011, SH-017/018, SH-019, SH-020, SH-022.
- Trust/Healthcare/Payment implementations may initially be test doubles behind those owner contracts; Feature 03 must not create local truth for them.
- U-01 remains explicit: financial timing for profile activation/publication/respond is not yet approved.

### Shared Operations Used

- **SH-005 `resolveEntitlement`** — Track. Local policy: which seller action requires which entitlement key. **Do not rebuild:** premium/selling-access booleans.
- **SH-011 `evaluateComplianceHold`** — Hold. Local policy: which hold scopes block which professional actions. **Do not rebuild:** local block state.
- **SH-016 `evaluateProfessionalReadiness`** — this is the public contract being implemented. Owner: Professional Eligibility.
- **SH-017 / SH-018** — Trust requirement/readiness. Local composition only; **do not rebuild** from TrustBadge/check table reads.
- **SH-019** — Payment financial readiness. Local policy: when to invoke for each action; U-01 blocks guessing. **Do not rebuild:** `stripeReady`/`canPayout`.
- **SH-020** — Healthcare readiness. Local policy: invoke when target/Taxonomy indicates lane. **Do not rebuild:** healthcare booleans.
- **SH-022** — Taxonomy requirement triggers. **Do not rebuild:** hardcoded category compliance map.
- **SH-029** — audit selected high-impact decisions where product/legal policy requires generic proof. It does not become readiness truth.

### Data / Schema

No new `ProfessionalReadiness`, `EligibilitySnapshot`, or `canSell` source table is created in MVP.

Professional readiness is evaluated from current owner truth. If caching is added later, it is a rebuildable projection with source versions, not authority.

Do not persist SH-015 as a global schema unless the Proposed Ruling is approved. Owner-specific response types may share a TypeScript shape without claiming new platform authority.

### Public Interfaces

Implement **SH-016 `evaluateProfessionalReadiness`** with an explicit action vocabulary such as the approved subset of:

- profile activation;
- public professional visibility;
- publish Offering;
- respond to Gig;
- participate seller-side in Order.

The exact enum/key belongs to Professional Eligibility and must be versioned/controlled rather than free-form client strings.

Minimum response:

- decision class;
- safe reason codes;
- evidence references to owner records/decisions;
- warnings/remediation hints where approved;
- evaluated timestamp;
- source/policy versions sufficient for deterministic tests.

### Logic

- Reject nonexistent/archived target contexts.
- Evaluate profile lifecycle first.
- Resolve entitlement and active holds.
- Resolve Taxonomy-triggered requirements.
- Call Trust/Healthcare only when context requires them.
- Call Payment only for action dimensions explicitly approved; do not guess U-01.
- Never short-circuit in a way that leaks sensitive detail to an unauthorized caller; reason-code exposure is audience-aware.
- Return multiple blockers when safe/useful so onboarding can remediate without repeated trial-and-error.

### UI / Administrative Surface

Optional readiness summary can display owner-safe categories:

- Profile;
- Selling access;
- Verification;
- Healthcare;
- Financial setup;
- Holds/review.

It must not display raw provider payloads or imply that one “verified” badge represents all dimensions.

### Authorization / Compliance

- Caller must be authorized to ask for the subject/target decision.
- Admin/support callers receive only data permitted by their authority and healthcare/financial sensitivity rules.
- Consent proof is not evaluated directly here except through the owner decision returned by Trust/Healthcare.
- U-01 actions fail as policy-unresolved/review rather than silently allowing or requiring a financial dimension.

### Events / Jobs / Integrations

No authoritative write is required for a normal query. If readiness changes trigger event-driven reevaluation later, that belongs to Feature 11.

### Failure Behavior

- owner dependency unavailable: return dependency-unavailable/retryable result, not allow;
- unresolved action policy: return explicit unavailable/review reason;
- inconsistent owner evidence: fail closed and record operational diagnostic;
- forbidden caller: generic denied response without sensitive blocker leakage.

### Tests

- unit: action-to-gate composition matrix;
- contract: each owner decision interface;
- integration: no foreign writes and no reads of compatibility booleans;
- security: reason-code redaction by caller context;
- failure: owner timeout/unavailable/unresolved policy;
- regression: TrustBadge/stripeReady/healthcare flags cannot satisfy a gate.

### Out of Scope

- persistence of eligibility decisions as new source truth;
- provider integrations;
- Offering status transitions;
- final resolution of U-01;
- Search indexing.

### Exit Gate

Feature 03 is complete only when:

1. SH-016 returns deterministic decisions for every action whose gate policy is currently approved;
2. unresolved action policies return explicit non-allow outcomes and are covered by tests;
3. all Trust/Healthcare/Payment/Track/Hold facts are obtained through owner interfaces;
4. no new readiness source table/boolean exists;
5. dependency failure fails safely;
6. consumers can contract-test the decision without direct CL-03 cross-module DB reads.

---

# Phase 2 — Trust and Regulated Readiness

## 04 — Verification Requirements, Consent, Packages, and Manual Check Path

Build a complete Trust-owned verification requirement and check slice that works without a live screening provider and proves Consent ownership boundaries.

### Objective

Admins can configure applicable verification requirements/packages, a professional can satisfy required standalone consent, and Trust can create/evaluate a manual or provider-pending `VerificationCheck` without provider state becoming platform truth.

### User-visible / Observable Result

- Admin/restricted tooling can create/activate/deactivate verification requirements and packages.
- Professional onboarding can show required checks for current taxonomy/target context.
- Standalone screening consent is presented/queryable through Consent.
- A manual-provider or stubbed check can be initiated and moved through approved review states by an authorized reviewer.
- SH-018 returns satisfied/missing/pending/expired/review blockers from Trust truth.

### Owning Module(s)

- **Trust Verification / Screening** owns requirements, packages, checks, screening-specific linkage, and readiness.
- **Consent & Disclosure** owns generic versioned proof.
- **Taxonomy** owns requirement-trigger source classification.

### Dependencies

- Feature 01 ProfessionalProfile context.
- SH-017/018 contract from Feature 03.
- Consent SH-008/010.
- Taxonomy SH-022.
- Order SH-107 only when a configured package requires a fee; the no-fee/manual path must remain usable without CL-04 implementation.
- U-03 must be respected: do not deepen `VerificationConsent` duplication before approved proof split.

### Shared Operations Used

- **SH-001/002** — actor/admin/professional authorization.
- **SH-008/010** — Consent proof/presentation. Local policy: required consent type/version/check/vendor context. **Do not rebuild:** Trust-owned generic acceptance proof.
- **SH-017** — implement requirement resolution.
- **SH-018** — implement Trust readiness from Trust-owned records.
- **SH-022** — taxonomy requirement triggers.
- **SH-044** — check initiation/package mutation idempotency.
- **SH-046** — requirement/check readiness events.
- **SH-107** — request a screening fee Order where fee policy applies; Trust never owns Order/payment lifecycle.

### Data / Schema

Use:

- `VerificationRequirement`;
- `VerificationPackage` / `VerificationPackageItem`;
- `VerificationCheck`;
- `VerificationConsent` only as approved screening linkage, not duplicate generic consent authority.

Add only indexes/constraints required to enforce clearly approved invariants. If “one active check per subject/requirement unless explicit recheck” needs a schema design not established by evidence, implement a transactional application invariant with concurrency test and raise an ADR before a new uniqueness model that would block legitimate rechecks.

### Public Interfaces

- SH-017 `resolveVerificationRequirements`;
- SH-018 `evaluateVerificationReadiness`;
- requirement/package admin commands;
- quote package/read fee policy;
- `initiateVerificationCheck`;
- `completeManualVerificationReview`;
- narrow safe `getVerificationCheckStatus` for subject/admin views.

### Logic

- Requirements are resolved from active requirement records plus canonical target/taxonomy context.
- Requirement resolution does not assert completion.
- Check initiation validates standalone consent when required.
- If fee required, Trust obtains authoritative Order result before provider ordering; payment never marks check passed.
- Manual review is restricted and records reason/evidence safely.
- Readiness recognizes passed/current versus missing/pending/needs-review/failed/expired/revoked states according to approved Trust policy.
- TrustBadge is not used as readiness truth.

### UI / Administrative Surface

Where product/admin tooling is in scope:

- verification requirement/package manager;
- professional checklist with safe status/next action;
- restricted manual-review queue/view showing minimized evidence only.

Do not expose raw screening reports in general admin tables.

### Authorization / Compliance

- standalone FCRA/background consent must not be buried only in general terms;
- only authorized reviewers may resolve manual checks;
- avoid collecting/storing raw SSNs or full reports;
- fee consent/non-refundable disclosure follows approved package/legal policy;
- failed check alone does not execute adverse action.

### Events / Jobs / Integrations

- emit requirement changed and check status changed events;
- no live provider callback is required in this feature;
- schedule expiry only after Feature 05 establishes expiry worker behavior.

### Failure Behavior

- missing consent: check remains/returns consent-required with proof reference needs;
- fee required but Order dependency unavailable: retryable blocked result, no provider submission;
- manual reviewer unauthorized: deny and audit attempt as policy requires;
- duplicate initiation: replay existing check/result where semantic identity matches.

### Tests

- unit: requirement resolution, package pricing composition, readiness states;
- integration: Consent contract, manual check state writes;
- contract: SH-017/018;
- concurrency/idempotency: duplicate initiation;
- compliance: standalone consent and “badge != truth”;
- authorization: requirement admin/manual reviewer.

### Out of Scope

- live Checkr/Certn callback;
- FCRA final adverse-action automation;
- provider-event dedupe schema;
- professional license provenance relationship;
- Search badge projection.

### Exit Gate

Feature 04 is complete only when:

1. requirements can be resolved from canonical context and returned through SH-017;
2. Trust readiness is derived from Trust-owned requirements/checks, never badge/provider booleans;
3. standalone consent is queried through Consent and generic proof is not duplicated;
4. manual/no-fee verification can be completed end to end with audit/authorization;
5. paid screening uses an Order contract or remains explicitly unavailable — no Trust payment subsystem exists;
6. all tests pass and U-03 remains documented rather than silently expanded.

---

## 05 — Verification Providers, Credentials, Expiry, Trust Projection, and FCRA Boundary

Add provider-neutral screening/credential integration, durable license state, expiry/recheck behavior, safe TrustBadge projection, and the legally gated adverse-action boundary.

### Objective

Trust can safely process external verification results and credential expiry without provider payloads becoming domain types, while legally incomplete FCRA paths remain disabled rather than faked.

### User-visible / Observable Result

- A configured screening provider can receive a vendor-hosted check request when all gates pass.
- Provider results map into canonical Trust states.
- Professional license credentials can be submitted/verified/expired through an owner path.
- Expired/revoked proof changes SH-018 readiness and TrustBadge state.
- Admin/ops can reconcile stuck provider checks.
- FCRA adverse-action automation is enabled only for the subset whose legal proof model has been approved; otherwise it stays clearly gated.

### Owning Module(s)

- **Trust Verification / Screening**.
- Media owns file mechanics; Observability owns integration failure; Hold owns reusable hold state.

### Dependencies

- Feature 04.
- Shared provider/event/job infrastructure.
- Checkr/Certn provider credentials/configuration when live adapter is enabled.
- **U-04:** owner-specific provider-event ledger must be approved before live webhook side effects.
- **U-05:** credential ↔ check provenance must be approved before implementation claims a durable relationship.
- **U-06:** FCRA notice/delivery/retention proof must be approved before production adverse-action automation.

### Shared Operations Used

- **SH-059 `verifyProviderWebhookSignature`** — shared shell; Trust adapter supplies algorithm/secret/tolerance. **Do not rebuild:** custom unverified webhook path.
- **SH-060 `deduplicateProviderEvent`** — shared mechanics, Trust-owned event truth. **Do not rebuild:** AuditEvent or `lastProviderEventId` as complete dedupe.
- **SH-061 `translateProviderStatus`** — Trust adapter maps provider state to `VerificationCheckStatus`/credential result. **Do not rebuild:** global status enum.
- **SH-062 `reconcileProviderState`** — shared worker, Trust repair policy. **Do not rebuild:** global provider reconciliation truth.
- **SH-047/048/055** — reliable jobs, retry backoff, deadline expiration. Local policy: retryable provider errors and expiry semantics.
- **SH-078** — minimize provider payload/telemetry.
- **SH-090** — validated Media contextual evidence where license documents are allowed; Media retains mechanics.
- **SH-012/013** — Trust may request/release a ComplianceHold only when approved source/legal policy calls for it. The hold lifecycle remains external.
- **SH-029/030** — admin/action and sensitive evidence access proof.

### Data / Schema

Use existing Trust records/statuses.

**Provider-event rule:** live webhook processing cannot use only `VerificationCheck.lastProviderEventId` as complete dedupe truth. If PR-09/U-04 is approved, add the smallest Trust-owned processed-provider-event model with provider/event ID uniqueness, payload hash or equivalent integrity reference, processing result/version, timestamps, and safe correlation. Do not reuse `ProcessedStripeEvent`.

**Credential provenance rule:** if U-05 is approved, add the explicit relation or immutable provenance reference required between `ProfessionalLicenseCredential` and verification attempt/evidence. Do not invent a hidden convention in JSON/notes.

### Public Interfaces

Complete:

- provider-hosted collection/session creation;
- provider check submission;
- verified webhook entry point;
- manual/automated credential verification;
- license/check expiration/recheck commands;
- TrustBadge issuance/suspend/expire/revoke projection commands;
- provider reconciliation admin/worker entry point;
- FCRA workflow commands only for approved legal subset.

### Logic

- Create local `VerificationCheck` before external side effect.
- Validate consent/payment/requirement/current state before provider submission.
- Signature verify → dedupe → translate → transition.
- Unknown provider status is not “passed”; fail safe and report operationally.
- Expiry worker transitions current proof under Trust policy and emits readiness changes.
- TrustBadge derives from approved Trust evidence and must be revoked/suspended/expired when evidence no longer supports display.
- Failed background checks do not directly ban/profile-suspend; route through approved FCRA/hold policy.

### UI / Administrative Surface

- professional provider-hosted handoff/status;
- credential submission/status and expiry display;
- admin verification/reconciliation view with safe metadata;
- FCRA case surface only if legal proof path is approved.

### Authorization / Compliance

- vendor-hosted sensitive collection;
- no raw SSN/full report storage/logging;
- restricted reviewer/evidence access plus SH-030 where required;
- FCRA paths are legal-gated;
- provider credentials/secrets server-only;
- no adverse action based solely on provider failure/unknown state.

### Events / Jobs / Integrations

- provider callback worker;
- check/license expiry/recheck job;
- provider reconciliation job;
- Trust readiness/badge change events;
- retries use bounded backoff/dead-letter;
- notification requests for approved user-facing status/remediation events.

### Failure Behavior

- invalid signature: reject before dedupe/domain state;
- duplicate event: no repeated side effect;
- missing U-04 record: live webhook feature remains disabled, not approximated;
- out-of-order event: transition validator/reconciliation handles or quarantines;
- provider unavailable: check remains canonical pending/appropriate owner state; record IntegrationFailure;
- legal/FCRA proof incomplete: case remains review-gated; no final adverse-action automation.

### Tests

- provider adapter mapping fixtures;
- signature verification;
- duplicate/out-of-order webhook;
- reconciliation after dropped event;
- expiration/recheck clock tests;
- TrustBadge invalidation;
- credential provenance contract if approved;
- FCRA tests only against approved transition/proof rules;
- PHI/PII/redaction telemetry tests.

### Out of Scope

- inventing FCRA law/policy;
- using Trust for payout KYC;
- public Search implementation;
- provider-independent global event table shared with Payment/Healthcare.

### Exit Gate

Feature 05 is complete only when:

1. provider adapters are isolated from Trust domain types by normalized ports;
2. live callbacks are enabled **only** if U-04 is resolved with owner-specific dedupe truth; otherwise the callback path is feature-disabled and tests prove no unsafe side effect can occur;
3. duplicate/unknown/out-of-order provider events cannot silently create repeated or “passed” state;
4. license/check expiry changes SH-018 readiness and TrustBadge projection correctly;
5. FCRA automation is enabled only for an approved evidence/transition subset; all other adverse-action paths remain explicitly gated;
6. reconciliation/operational-failure paths are observable;
7. all enabled paths pass provider/idempotency/compliance tests.

---

## 06 — Healthcare Lane, BAA, Data Boundaries, and Admin Payload Policy

Implement the healthcare-specific readiness lane without turning healthcare into a User type or duplicating general authorization/file mechanics.

### Objective

Healthcare can own professional lane status, BAA state, explicit sensitive-data boundaries, and healthcare-specific admin payload handling; Professional Eligibility and Marketplace can consume SH-020 safely.

### User-visible / Observable Result

- A healthcare-sensitive professional/Offering context can be identified through canonical triggers.
- A HealthcareComplianceProfile exists and returns a current healthcare readiness decision.
- A BAA can progress through the approved manual/provider-neutral lifecycle.
- Explicit supported targets can be marked as healthcare-sensitive and queried.
- An authorized admin/support access attempt can return allow/redact/block/deny handling and create sensitive-access evidence.
- Automated BAA provider callback remains disabled until provider/proof gaps are resolved.

### Owning Module(s)

- **Healthcare / Regulated Services**.
- Taxonomy/Marketplace/Professional remain owners of trigger context.
- Role / Authority owns general permission.
- Media owns file mechanics.
- Audit owns AccessAuditLog.

### Dependencies

- Feature 01 profile context.
- Feature 02 Offering eligibility context.
- Feature 03 SH-020 consumption boundary.
- Consent SH-008 where approved healthcare disclosure proof is required.
- Media/Audit interfaces.
- U-07 through U-12 constrain provider automation, BAA proof, boundary retirement/inheritance, policy versioning, decision semantics, and generic sensitivity.

### Shared Operations Used

- **SH-001/002** — actor + general permission. Local policy: Healthcare acts after permission; **do not rebuild:** healthcare role engine.
- **SH-008** — Consent proof. Local policy: which proof applies; **do not rebuild:** healthcare consent table as generic proof.
- **SH-020** — implement healthcare readiness public interface.
- **SH-022** — taxonomy healthcare/sensitivity triggers.
- **SH-030** — sensitive healthcare access evidence.
- **SH-044/046** — idempotent healthcare mutations and owner events.
- **SH-059/060/061/062** — provider callback pattern only when U-08/provider selection is approved.
- **SH-078** — provider/telemetry minimization.
- **SH-087/090** — Media signed access/context attachment where BAA/evidence documents are stored; Healthcare owns entitlement/context, not signing.
- **SH-123** — validate external boundary target through target owner rather than generic polymorphic Prisma reads.

### Data / Schema

Use:

- `HealthcareComplianceProfile`;
- `BaaAgreement`;
- `HealthcareDataBoundary`;
- `HealthcareAdminAccessPolicy`;
- healthcare enums.

Feature 06 must operate within current schema limitations:

- exact-target boundary creation/query is supported;
- boundary clear/inheritance automation is unavailable until U-09 is approved;
- exact-target current admin policy may be supported if product scope accepts no historical precedence; production claims requiring historical/versioned policy are blocked by U-10;
- BAA execution may use manual/provider-neutral state, but production e-sign proof is blocked by U-07/U-08;
- `lockedHealthcareFlag` or generic `DataSensitivity` must not become substitute truth.

### Public Interfaces

- `declareHealthcareLane` / get healthcare profile;
- SH-020 `evaluateHealthcareReadiness`;
- BAA create/send-record/apply-signed/verify/reject/revoke/expire commands for the approved path;
- `markHealthcareDataBoundary`;
- `resolveEffectiveHealthcareBoundary` limited to explicit supported semantics;
- `set/getHealthcareAdminAccessPolicy` for approved exact-target scope;
- `evaluateHealthcareAdminAccess`;
- Healthcare privacy executor later integrated in Feature 12.

### Logic

- Resolve whether healthcare is required from taxonomy/Offering/profile/boundary context.
- Keep BAA lifecycle and healthcare-profile summary separate; profile summary may react to BAA truth but never replace it.
- Validate target existence through target owner.
- General permission check precedes healthcare payload policy.
- Healthcare decision determines allow/redact/block/deny only after caller authority exists.
- Any redaction instruction is enforced by the resource-owning delivery/read layer, not by returning raw payload then hiding it in UI.

### UI / Administrative Surface

Where in scope:

- professional healthcare readiness/BAA status and next action;
- restricted healthcare compliance case list using metadata only;
- admin access-policy editor for supported exact targets;
- access result should clearly distinguish redacted/blocked without exposing PHI.

### Authorization / Compliance

- healthcare is not a blanket User type;
- role/admin status alone cannot bypass healthcare policy;
- private BAA/healthcare evidence uses Media and SH-030 as required;
- no PHI in logs/analytics/provider metadata beyond approved minimum;
- BAA legal completeness is not claimed until U-07 is resolved.

### Events / Jobs / Integrations

- healthcare profile/BAA/boundary/policy change events;
- BAA expiry job after approved semantics;
- provider reconciliation only when provider adapter enabled;
- downstream readiness event for Professional/Marketplace/Search reevaluation;
- Notification requests for approved BAA/remediation events.

### Failure Behavior

- target cannot be validated: no boundary/policy write;
- general auth denied: stop before healthcare payload processing;
- healthcare result blocked/redacted: resource owner obeys instruction; no raw payload leakage;
- BAA provider unavailable/unselected: manual/provider-neutral path remains, automated path unavailable;
- unresolved clear/inheritance request: reject as unsupported rather than deleting a boundary ad hoc.

### Tests

- unit: healthcare requirement/readiness and BAA-to-profile summary logic;
- contract: Taxonomy/Offering target validation and SH-020;
- authorization: Role then Healthcare layering;
- integration: boundary uniqueness, admin policy, AccessAuditLog request;
- privacy/security: PHI redaction/telemetry minimization;
- provider tests only for enabled adapter;
- unsupported boundary clear/inheritance tests fail explicitly.

### Out of Scope

- defining BAA legal text/parties without approval;
- direct Messaging/Video/Media lifecycle ownership;
- inferred healthcare boundary propagation not established by U-09;
- global DataSensitivity owner;
- automated e-sign provider activation before U-07/U-08.

### Exit Gate

Feature 06 is complete only when:

1. SH-020 derives from Healthcare-owned records and canonical trigger context;
2. healthcare is never represented as a User-type flag;
3. Role authorization and healthcare payload policy are tested as separate gates;
4. explicit supported boundaries/policies are owner-validated and access decisions generate required sensitive-access proof;
5. automated BAA provider callbacks are either safely implemented after U-07/U-08 approval or remain disabled with no fake dedupe/proof;
6. unsupported boundary removal/inheritance/version-history behavior fails explicitly;
7. all enabled paths pass compliance/security tests.

---

# Phase 3 — Financial Readiness and Publication

## 07 — KYC, Tax Profile, Payout Account, and Financial Readiness

Build Payment-owned financial onboarding and the dimensioned financial-readiness interface required for safe money actions.

### Objective

A ProfessionalProfile can complete provider-backed financial onboarding and consumers can ask Payment, rather than reading Stripe/profile flags, whether KYC/tax/payout-account dimensions are ready.

### User-visible / Observable Result

- Professional can start/resume KYC, tax-profile, and payout-account onboarding through provider-neutral application services.
- Current KYC/tax/account states are visible in a safe financial setup surface.
- Provider callbacks update Payment-owned canonical records idempotently.
- SH-019 returns separate readiness dimensions and safe remediation reasons.
- Sensitive financial views require step-up and create sensitive-access proof.

### Owning Module(s)

- **Payment / Payout / Tax**.

Professional Eligibility consumes the result but owns none of these records.

### Dependencies

- Feature 01 ProfessionalProfile identity.
- Identity step-up SH-014.
- Hold SH-011.
- Payment provider adapters/Stripe configuration.
- `ProcessedStripeEvent` for Stripe event dedupe.
- Audit/Observability.

### Shared Operations Used

- **SH-001/002** — actor/financial resource authorization.
- **SH-014** — step-up for sensitive finance. Local policy: which reads/mutations are high risk. **Do not rebuild:** payout MFA.
- **SH-011** — hold input to financial readiness where applicable. **Do not rebuild:** financial generic block flag.
- **SH-019** — implement financial readiness.
- **SH-030** — balance/tax/account sensitive access proof.
- **SH-044** — onboarding command idempotency.
- **SH-059/060/061/062** — verified/deduped/translated/reconciled provider events. Payment owns `ProcessedStripeEvent` for Stripe callbacks.
- **SH-063 `captureProviderSnapshot`** — preserve provider requirement snapshot where applicable; owner remains Payment.
- **SH-078** — minimized provider input/logging.

### Data / Schema

Use:

- `KycVerification`;
- `TaxProfile` / `TaxDocument`;
- `PayoutAccount`;
- `ProviderRequirementSnapshot`;
- `ProcessedStripeEvent` for Stripe callback dedupe;
- corresponding enums/statuses.

Do not update `ProfessionalProfile.stripeReady` or `stripeAccountId` as gate truth. If compatibility projection maintenance is temporarily required by existing code, it must be one-way, clearly marked deprecated, and never read by readiness logic.

### Public Interfaces

- SH-019 `evaluateFinancialReadiness` with dimensioned result;
- KYC onboarding/start/resume/status query;
- tax-profile collection/status/document-reference query;
- payout-account onboarding/status query;
- provider requirement snapshot query;
- safe financial setup summary.

### Logic

- Local record exists before provider handoff where needed.
- Provider callback signature verifies and `ProcessedStripeEvent` claims event before side effects.
- Provider state maps into canonical Workin Ants statuses.
- Unknown provider state fails safe and becomes operationally visible.
- Financial readiness does not collapse to one boolean; return KYC, tax, account, hold/restriction dimensions independently.
- This feature does not decide U-01 timing for publication; it merely provides authoritative financial facts.

### UI / Administrative Surface

- professional financial setup checklist;
- payout account/KYC/tax status with safe next steps;
- restricted admin financial case metadata where product context requires;
- no raw tax identifiers/provider sensitive payloads.

### Authorization / Compliance

- step-up for approved sensitive reads/mutations;
- AccessAuditLog for sensitive views;
- provider-hosted collection preferred for tax/KYC sensitive fields;
- no raw tax/identity documents in ordinary tables unless approved Media flow explicitly requires it;
- KYC is distinct from Trust screening.

### Events / Jobs / Integrations

- KYC/tax/account status-change events;
- provider webhook processing;
- provider reconciliation job;
- expiry/refresh job where record semantics require;
- Notification requests for requires-input/restricted states as approved.

### Failure Behavior

- invalid/duplicate event: no state replay;
- provider unavailable: retain canonical pending/onboarding state and record operational failure;
- step-up missing: issue/require Identity challenge; no financial read/mutation;
- restricted account: SH-019 denies appropriate financial action with safe reason.

### Tests

- provider mapping/signature/dedupe/reconciliation;
- SH-019 contract and dimension logic;
- step-up and sensitive access audit;
- KYC versus Trust separation regression;
- no reads from ProfessionalProfile compatibility fields;
- provider timeout/unknown status.

### Out of Scope

- balance ledger;
- payout request/transfer;
- Order payment status;
- sales tax;
- U-01 publication timing decision.

### Exit Gate

Feature 07 is complete only when:

1. KYC/tax/payout-account source records are Payment-owned and provider-normalized;
2. Stripe callbacks are signature-verified and `ProcessedStripeEvent`-deduplicated;
3. SH-019 never reads `ProfessionalProfile.stripeReady` or Trust verification as payout KYC;
4. sensitive finance requires step-up/audit as specified;
5. provider failures/reconciliation are observable;
6. all provider/security/contract tests pass.

---

## 08 — Offering Publication and Public Professional Supply

Connect the already-built seller, Offering, Trust, Healthcare, Entitlement, Hold, and approved financial policy into the real publication transition and Search handoff.

### Objective

A structurally valid draft Offering can become active only through Marketplace Supply after Professional Eligibility authorizes `publish_offering`; public source projections are sent to Search without Search reconstructing CL-03 policy.

### User-visible / Observable Result

- Professional sees a publish-readiness result with actionable blockers.
- A denied Offering remains non-public and no Search projection is created.
- After all approved gates pass, Marketplace alone activates the Offering.
- The active Offering and eligible Professional are submitted to Search through owner-approved projections.
- Pausing/archiving/restriction leads to controlled Search refresh/removal requests.

### Owning Module(s)

- **Marketplace Supply** owns Offering publication/status.
- **Professional Eligibility** owns seller publish decision.
- Trust/Healthcare/Payment/Track/Hold/Taxonomy own inputs.
- Search owns indexing execution.

### Dependencies

- Features 02–07.
- **U-01 must be resolved for `publish_offering`** before this feature can declare production publication policy complete. The approved result may require or not require financial readiness, but it must be explicit.
- CL-05 delivery-readiness contracts for downloadable products/courses where required.
- Moderation current restriction check/contract.
- Search SH-091/094.

### Shared Operations Used

- **SH-001/002** — publisher authorization.
- **SH-005** — seller entitlement.
- **SH-011** — active hold gate.
- **SH-016** — Professional Eligibility `publish_offering` decision.
- **SH-017/018/019/020/022** — consumed indirectly/directly according to Professional action policy; Marketplace must not reproduce them.
- **SH-024 `evaluatePublicReadiness`** — owner-specific public-readiness composition contract.
- **SH-044/046** — idempotent publication and owner event.
- **SH-091** — Search refresh request.
- **SH-094** — Marketplace/Professional source projections.
- **SH-041 `requestNotification`** — approved publication/restriction notification delivery; source event meaning remains owner-local.

### Data / Schema

Use existing `Offering.status` as publication lifecycle truth.

Do not make independent source decisions from:

- `Offering.isPublic`;
- `Offering.isFeatured`;
- `ProfessionalProfile.stripeReady`;
- `ProfessionalProfile.trustScore`;
- `TrustBadge` alone.

`priceFromCents`, if stored, follows PR-06 projection policy.

### Public Interfaces

- `requestOfferingPublication`;
- `resumeOffering` with full current gate re-evaluation;
- `pauseOffering`;
- `archiveOffering`;
- `applyOfferingRestriction` / restoration command for external moderation/hold source decisions;
- Marketplace and Professional source projection builders;
- SH-091 request integration.

### Logic

Publication order:

```text
actor/authority
→ current Offering/version/status
→ Marketplace local shape/pricing/classification/media/delivery checks
→ Professional Eligibility SH-016(publish_offering, immutable Offering gate context)
→ current moderation/hold/public-readiness checks
→ Marketplace transition to active
→ owner domain event/outbox
→ source projection build
→ Search refresh request
```

Resume repeats current gates; it never reuses a stale prior allow result.

Restriction/restoration source decision comes from Moderation/Hold owner; Marketplace executes local lifecycle consequences.

### UI / Administrative Surface

- publish button/action with readiness blocker summary;
- remediation links to verification/healthcare/financial setup where safe;
- active/paused/restricted/archive states from Offering lifecycle;
- do not render `isFeatured` controls;
- do not show raw screening/KYC/PHI details in publish blockers.

### Authorization / Compliance

- U-01 approved gate matrix is mandatory;
- healthcare/verification only apply when canonical context triggers them;
- active hold blocks per approved scope;
- moderation restriction cannot be bypassed by professional republish;
- professional seller entitlement comes from Track;
- Search projection only after public-readiness allow.

### Events / Jobs / Integrations

- Offering status event + outbox;
- Search refresh requests for publish/pause/archive/restriction/restoration;
- Notification requests as approved;
- no direct Typesense or provider payment call.

### Failure Behavior

- any gate denies: no status change, return safe blockers;
- dependency unavailable: fail closed/retryable; do not publish;
- Search request failure after active commit: outbox/reliable job retries; do not roll back Offering to draft solely because Search is temporarily unavailable;
- concurrent moderation restriction versus publish: lock/version conflict resolves; restriction cannot be overwritten by stale publish command.

### Tests

- E2E: blocked → remediate → publish;
- integration: Trust/Healthcare/Track/Hold/approved Payment decision composition;
- concurrency: publish versus edit/restriction;
- contract: Search projection/request;
- compliance: Search receives allowlisted fields only;
- regression: `isPublic`, `isFeatured`, `stripeReady`, TrustBadge cannot bypass gates.

### Out of Scope

- Search provider execution;
- Order checkout;
- bundle Offering publication until U-15;
- paid promotion/featured ranking;
- Digital Goods grant issuance.

### Exit Gate

Feature 08 is complete only when:

1. U-01 has an approved `publish_offering` financial-gate ruling recorded in architecture/module policy;
2. Marketplace is the only writer of Offering publication state;
3. publication/resume reevaluate current owner gates and fail closed on unavailable dependencies;
4. active/restricted/paused/archive changes produce reliable Search requests without direct Search writes;
5. no compatibility/projection boolean can independently publish an Offering;
6. concurrent moderation/publication is safe;
7. full E2E/contract/compliance tests pass.

---

## 09 — Professional Balance, Payout Request, and Transfer

Implement the professional money-withdrawal path over append-only financial projection and provider-mediated transfers without introducing a wallet or escrow.

### Objective

Eligible professional earnings can be represented in Payment's append-only balance ledger, queried safely, requested for payout, and transferred through an idempotent provider workflow.

### User-visible / Observable Result

- Professional can view available/held/requested/paid financial projection totals after step-up.
- Eligible source events create immutable balance effects once.
- Professional can request payout when SH-019 permits it.
- Approved request creates a provider transfer and reflects paid/failed/reversed/cancelled results.
- Holds/disputes affect payout through Payment-owned financial consequences without owning the source case.

### Owning Module(s)

- **Payment / Payout / Tax** owns ledger, PayoutRequest, PayoutTransfer.
- Order/Review/Dispute/Hold remain owners of source commercial/restriction facts.

### Dependencies

- Feature 07.
- Order completion/earning snapshot contract from CL-04.
- Hold/Dispute events/contracts.
- Step-up and Audit.
- Provider transfer adapter.

### Shared Operations Used

- **SH-014** — sensitive payout step-up.
- **SH-011** — active hold gate.
- **SH-019** — payout financial readiness.
- **SH-030** — sensitive balance/payout access.
- **SH-044** — payout request/transfer idempotency.
- **SH-045 `deduplicateDomainEvent`** — prevent repeated source Order/dispute effects in Payment projection.
- **SH-046** — Payment events.
- **SH-047/048** — retries/dead-letter for transfer/reconciliation.
- **SH-051 `acquireAggregateLock`** or root-approved equivalent — serialize conflicting payout/balance reservation actions. Local policy: profile/currency/request lock key.
- **SH-056 `executeAtomicReservation`** where the root/Payment design uses reservation to prevent concurrent overspend. Local policy: availability/release semantics; **do not rebuild:** in-memory balance mutex.
- **SH-062** — transfer/provider reconciliation.

### Data / Schema

Use:

- `ProfessionalBalanceLedgerEntry` append-only;
- `PayoutRequest`;
- `PayoutTransfer`;
- `PayoutAccount`;
- KYC/tax readiness records;
- ComplianceHold reference where schema supports the financial consequence.

Never add `walletBalance` or mutable source-of-truth balance fields.

Ledger entries require deterministic source references/idempotency sufficient to avoid duplicate financial effects. If the current schema cannot uniquely identify a replayed source effect, add the smallest approved uniqueness/idempotency constraint in Payment rather than relying on best effort.

### Public Interfaces

- `calculateProfessionalAvailableBalance` / safe balance summary;
- `appendProfessionalBalanceEntry` through narrow source-specific commands, not arbitrary public amount mutation;
- `createPayoutRequest`;
- approve/block/process payout workflow;
- payout transfer update/reconcile;
- `getPayoutHistory`.

### Logic

- Source Order effect uses Order's snapshotted commission, never current Track plan.
- Refund/dispute/hold effects create additional ledger entries; never mutate prior entries.
- Calculate available amount from approved entry types/effective availability and payout state.
- Payout request verifies actor, step-up, account, KYC/tax, balance, currency, holds/disputes.
- Provider transfer creation is idempotent and separate from request intent.
- Reversal adds corrective ledger effect; no historical entry rewrite.

### UI / Administrative Surface

- professional balance/payout summary behind step-up;
- payout request form with amount/currency/account and safe denial reasons;
- payout history;
- restricted admin review for blocked/failed/reversed transfers.

### Authorization / Compliance

- step-up required;
- sensitive access logged;
- ComplianceHold remains external stop sign;
- no wallet/escrow language;
- provider-held balance/capabilities are inputs, not local custody claim;
- historical commission comes from Order snapshot.

### Events / Jobs / Integrations

- consume Order/refund/dispute/hold events idempotently;
- provider transfer callback/reconciliation;
- retries on transient provider errors only;
- Payment domain events for payout changes;
- notifications for requested/paid/failed/requires-action as approved.

### Failure Behavior

- insufficient available funds: deny without partial reservation;
- concurrent payout requests: lock/reservation prevents overspend;
- provider transient failure: retry without duplicate transfer;
- provider terminal failure: owner state failed/review; no blind retry;
- reversal: append correction and update transfer/request under owner rules;
- duplicate source event: no duplicate ledger entry.

### Tests

- ledger math and append-only invariant;
- source event dedupe;
- concurrent payout overspend prevention;
- idempotent provider transfer;
- step-up/access audit;
- commission snapshot regression;
- refund/hold/release/reversal effects;
- reconciliation.

### Out of Scope

- Order completion lifecycle;
- true wallet/custody/escrow;
- dispute case resolution;
- current subscription commission recalculation.

### Exit Gate

Feature 09 is complete only when:

1. balance is derivable from append-only Payment records and cannot be overspent under concurrent payout requests;
2. duplicate Order/dispute/provider effects do not duplicate financial entries/transfers;
3. payout is step-up/hold/SH-019 gated;
4. historical commission is sourced from Order snapshots;
5. no wallet/escrow source table or mutable balance truth exists;
6. provider failure/reversal/reconciliation paths are tested;
7. all financial/security/concurrency tests pass.

---

## 10 — Payment and Sales-Tax Bridge to Transaction / Order

Complete the CL-03 financial bridge into CL-04 so provider payment/tax effects update Payment truth and command Order truth without cross-writing ownership.

### Objective

An existing authoritative Order can be priced/taxed/paid/refunded through Payment provider rails, with provider-backed sales-tax proof and normalized commands back to the Order owner.

### User-visible / Observable Result

- Checkout/payment flow for an Order can obtain a provider result.
- Sales-tax calculation/line-item/transaction proof is stored by Payment.
- Verified payment success/failure/refund effects are reflected in Order only through Order public commands.
- Duplicate Stripe events do not repeat Order transitions/tax transactions.
- Payment/Order reconciliation can detect missed provider effects.

### Owning Module(s)

- **Payment / Payout / Tax** — provider rail, ProcessedStripeEvent, sales-tax records, financial effects.
- **Transaction / Order** — Order/RefundStatus/OrderEvent transaction truth.

### Dependencies

- Feature 07 provider foundation.
- CL-04 stable Order payment/query contracts.
- Stripe/Stripe Tax configuration.
- Any Digital Goods tax-code input comes through the owning Module/public context, not Marketplace ownership theft.
- U-120/SH-120 global jurisdiction helper remains unresolved; do not depend on it.

### Shared Operations Used

- **SH-059/060/061/062** — Stripe webhook verification/dedupe/status mapping/reconciliation.
- **SH-044** — checkout/refund command idempotency.
- **SH-046** — Payment-owned domain events.
- **SH-108 `requestOrderRefund`** — Order coordinates approved refund; Payment executes provider rail. **Do not rebuild:** Payment-owned refund case/status lifecycle that replaces Order.
- **SH-109 `snapshotExternalDecision`** where Order must retain a point-in-time tax/commission/entitlement decision; snapshot belongs to consuming lifecycle owner. Local Payment truth remains separate.
- **SH-123** — validate external Offering/Order target references through owners when polymorphic tax context is needed.

### Data / Schema

Use:

- `ProcessedStripeEvent`;
- `SalesTaxCalculation`;
- `SalesTaxLineItem`;
- `SalesTaxTransaction`;
- Payment provider references in Payment-owned records;
- Order-owned provider/payment snapshot fields only through Order public commands.

Seller `TaxProfile` is not transaction sales-tax truth.

### Public Interfaces

Payment side:

- prepare/execute provider checkout/payment instruction for an existing Order;
- calculate/finalize/void sales tax;
- record/reverse/refund tax transaction;
- normalized payment/refund result;
- provider reconciliation.

Order side consumed:

- get authoritative payment/pricing/participant snapshot;
- record verified payment result;
- record refund result;
- create chargeable Order if applicable to upstream flow.

### Logic

- Tax uses provider-backed calculation rather than custom state/local tax tables.
- Obtain buyer location from approved checkout/billing/shipping evidence selected by Payment tax policy.
- Verify/dedupe Stripe event before any Payment or Order side effect.
- Finalize tax result against the correct Order/version.
- Command Order owner for transaction transition.
- Record Payment-owned sales-tax/financial proof.
- Partial refund/tax reversal semantics must follow actual schema/provider capability; if incomplete, constrain feature to supported refund cases rather than inventing allocation logic.

### UI / Administrative Surface

Mostly CL-04 checkout UI. CL-03 may expose restricted payment/tax diagnostics/reconciliation metadata. Do not build a second checkout UI solely for Payment.

### Authorization / Compliance

- Order owner establishes buyer/seller transaction authority.
- Payment does not trust client-reported final amount/tax.
- No raw payment credentials stored.
- Webhook signature/dedupe mandatory.
- tax evidence/retention follows Payment policy.

### Events / Jobs / Integrations

- Stripe webhook;
- sales-tax provider calls;
- payment/tax reconciliation job;
- Order commands/events;
- Payment ledger effects as appropriate after Order-owned outcome.

### Failure Behavior

- provider tax unavailable: checkout follows approved fail/hold policy, never homemade tax guess;
- duplicate event: no duplicate Order transition/tax transaction;
- Order command conflict: reconcile against current Order and quarantine inconsistent provider result rather than direct DB patch;
- refund provider failure: Order remains authoritative about approved request/state according to CL-04 contract; Payment records technical/domain rail outcome separately.

### Tests

- webhook signature/dedupe;
- Order contract tests proving no direct Order writes;
- tax calculation/finalization/reversal;
- stale Order/version conflict;
- duplicate payment/refund event;
- reconciliation after missing webhook;
- retention/sensitive telemetry tests.

### Out of Scope

- Order lifecycle implementation;
- agreement/signature lifecycle;
- custom tax engine;
- generic jurisdiction normalization SH-120;
- Digital Goods lifecycle.

### Exit Gate

Feature 10 is complete only when:

1. Payment can complete supported payment/tax rails without becoming Order owner;
2. all Order state changes occur through tested Order public commands;
3. sales-tax proof is Payment-owned and separate from TaxProfile;
4. Stripe callback replay cannot duplicate effects;
5. reconciliation detects/repairs or escalates missed provider effects through owner commands;
6. unsupported partial/refund/tax cases fail explicitly rather than using invented allocation logic;
7. integration/provider tests pass.

---

# Phase 4 — Cross-Cluster Contract Proof

## 11 — Readiness Change Propagation and Neighboring-Cluster Integration

Prove that CL-03 collaborates correctly with Gig, Order, Search, Delivery, Notification, and Hiring consumers while preserving every neighbor's source truth.

### Objective

A change in CL-03 source truth reliably reaches affected consumers, and CL-03 can consume neighboring owner facts without direct cross-domain repositories.

### User-visible / Observable Result

- A verification/healthcare/hold/entitlement change causes affected professional/public readiness to be reevaluated.
- An active Offering or Professional can be de-indexed/re-indexed through Search requests.
- Gig response gate uses Gig-owned context and SH-016.
- Order seller participation/financial bridge uses Order-owned context.
- CL-05 delivery readiness for products/courses is consumed without Marketplace owning Digital Goods/Video.
- Hiring can consume Trust verification contracts without using Professional Eligibility as Candidate lifecycle truth.

### Owning Module(s)

- Source truth remains with each CL-03 Module.
- **Professional Eligibility** owns professional action reevaluation.
- **Marketplace Supply** owns Offering effects.
- Neighbor Modules own their own lifecycle/projection/delivery truth.

### Dependencies

- Features 01–10.
- CL-02 Search interface.
- CL-04 Gig/Order contracts.
- CL-05 Media/Digital Goods/Video readiness contracts.
- CL-06 Hiring Trust consumer contract where in MVP scope.
- CL-07 Notification request.
- platform outbox/inbox.

### Shared Operations Used

- **SH-016** — professional action gate for Gig/Order/Search consumers.
- **SH-024** — public readiness contract.
- **SH-045** — consumer event dedupe.
- **SH-046** — source events.
- **SH-047/048** — async reevaluation/retry.
- **SH-091** — Search projection refresh.
- **SH-094** — safe source projection.
- **SH-041** — Notification requests.
- **SH-003/123** — owner-fact/target validation contracts where approved; never generic cross-domain repository.

### Data / Schema

No cluster-wide change-propagation source table is introduced.

Use platform outbox/inbox/job records for mechanics only. Search owns `SearchUpsertEvent`. Notification owns delivery records. Neighbor source Modules own their data.

If a source owner needs a domain-specific immutable lifecycle event record for correctness, use the shared append-only mechanism while keeping that record owner-specific; do not reuse AuditEvent.

### Public Interfaces

Prove/complete:

- Gig → Professional narrow gate context + SH-016(`respond_to_gig`);
- Order → Professional narrow seller context + SH-016 where requested;
- Marketplace → CL-05 product/course delivery-readiness interfaces;
- Professional/Marketplace → Search source projection/refresh;
- Trust SH-017/018 → CL-06 consumers;
- Notification request contracts.

### Logic

- Event consumers fetch current authoritative state before irreversible local action; do not assume an old event payload is current truth when race-sensitive.
- Reevaluate only affected profiles/Offerings where event references permit.
- If readiness is lost, source owner decides local consequence: Professional may become unable to act; Marketplace may restrict/de-publicize only under approved policy/source decision.
- Search removal is a projection effect, not source deletion.
- Hiring uses Trust directly for its own candidate/job gate; Professional Eligibility is not generalized into a universal person-readiness service.

### UI / Administrative Surface

No new cluster dashboard is required. Observable behavior is through existing professional/Offering/Gig/Order/Search/admin surfaces and contract test harnesses.

### Authorization / Compliance

- events carry safe identifiers only;
- Search projections are allowlisted and privacy-safe;
- Notification variables are sensitivity-safe;
- CL-05 receives only contextual entitlement/readiness necessary for delivery;
- Candidate/hiring data stays outside professional seller profile.

### Events / Jobs / Integrations

- owner events → consumer inbox → reliable reevaluation job;
- Search refresh;
- Notification request;
- no direct provider calls from event coordinator unless the owner workflow owns them.

### Failure Behavior

- consumer unavailable: event remains retryable; source truth unchanged;
- duplicate event: one consumer effect;
- Search unavailable: pending Search work retries; active source truth remains intact;
- stale event versus newer owner state: current owner query wins;
- neighbor contract unavailable: do not bypass with direct database read.

### Tests

- cross-module contract tests;
- event replay/out-of-order tests;
- Search deindex/reindex E2E;
- Gig response gate E2E;
- Order seller/payment bridge contract;
- CL-05 delivery-readiness ownership regression;
- CL-06 Trust consumer test;
- notification sensitivity test.

### Out of Scope

- implementing neighbor lifecycle internals;
- cluster-wide read-model/dashboard;
- Search provider schema implementation;
- candidate lifecycle redesign.

### Exit Gate

Feature 11 is complete only when:

1. each material CL-03 readiness/status change has a tested downstream contract or an explicit no-effect ruling;
2. Search updates are requested through SH-091 and are replay-safe;
3. Gig/Order/Delivery/Hiring consumers operate through owner interfaces with no direct cross-domain repositories;
4. duplicate/out-of-order events cannot produce repeated or stale irreversible effects;
5. no neighbor source truth has been copied into CL-03 for convenience;
6. cross-cluster integration tests pass.

---

# Phase 5 — Governance, Privacy, and Enforcement Integration

## 12 — Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion

Complete the guardrail integrations required for production CL-03 ownership without turning Privacy, Moderation, Audit, or Ops into local submodules.

### Objective

Every CL-03 owner can execute Privacy instructions against its records, execute authorized moderation/hold consequences, preserve generic/sensitive access evidence, and expose provider/worker failures through shared operational rails.

### User-visible / Observable Result

- Privacy can enumerate and execute target-specific CL-03 erasure/anonymization/retention work with per-target results.
- Moderation/Hold can restrict/restore the correct ProfessionalProfile or Offering through owner commands.
- Sensitive financial/healthcare/screening evidence access is logged.
- Admin/ops can see stuck provider jobs/reconciliation failures without operational tables pretending to be domain truth.
- Retention-locked records return “retained with reason” to Privacy rather than being silently deleted or ignored.

### Owning Module(s)

- Each of the five CL-03 Modules owns execution against its records.
- Privacy owns the request/job/exemption lifecycle.
- Moderation owns case/action decisions.
- Hold owns ComplianceHold.
- Audit owns AuditEvent/AccessAuditLog.
- Observability owns IntegrationFailure/QueueJob/OpsIncident.

### Dependencies

- Features 01–11.
- Privacy protocol implementation.
- Moderation/Hold/Audit/Ops interfaces.
- Media/provider deletion interfaces.
- Legal retention policy for any destructive path being enabled; unresolved retention periods remain blocked.

### Shared Operations Used

- **SH-095 `executePrivacyInstruction`** — each data owner executes. Local policy: erase/anonymize/retain/provider-delete mapping. **Do not rebuild:** PrivacyRequest workflow.
- **SH-096 `enumerateSubjectData`** — each CL-03 owner inventories its records/provider references.
- **SH-097 `evaluateRetentionRequirement`** — owner supplies facts; Privacy records exemption. **Do not rebuild:** local exemption table.
- **SH-098 `anonymizePersonalFields`** — shared primitive; owner supplies field mapping.
- **SH-070 `deleteProviderResource`** — provider owner executes external deletion when permitted.
- **SH-103 `executeModerationDecision`** — Professional/Marketplace execute source decision. **Do not rebuild:** moderation case.
- **SH-011/012/013** — Hold gate/request/release.
- **SH-029/030** — generic/sensitive audit evidence.
- **SH-034/037/038** — telemetry sanitation, integration failure, queue telemetry.

### Data / Schema

No local PrivacyRequest, ModerationCase, ComplianceHold, AuditEvent, AccessAuditLog, IntegrationFailure, or QueueJob source schema is added.

Owner-specific erasure/anonymization may modify CL-03 records only under Privacy instruction and retention decision. Financial, FCRA, BAA, and compliance evidence cannot be hard-deleted if retention policy requires it.

If a CL-03 owner lacks fields needed to distinguish product deletion from erasure, do not invent a global `deletedAt`/`erasedAt` pattern locally; follow root Privacy/data-model standards and approved migration.

### Public Interfaces

For each CL-03 Module:

- subject-data enumeration;
- target-specific privacy execution;
- retention fact response;
- external provider-resource deletion hook where applicable.

Professional/Marketplace:

- moderation enforcement target command;
- hold consequence/remediation integration.

Audit/Ops:

- generic audit request;
- sensitive access request;
- provider/worker failure reporting.

### Logic

- Privacy target arrives with subject, target, requested disposition, and retention decision context.
- Owner verifies target belongs to it.
- Owner evaluates retention facts; Privacy records any exemption.
- Owner erases/anonymizes/deletes external resources only if permitted.
- Owner returns deterministic disposition/result.
- Moderation action is validated against source decision ID and executed idempotently.
- Hold status is queried/requested/released only through owner.
- Audit metadata is safe/minimized and does not include raw private documents/provider payloads.

### UI / Administrative Surface

Where admin tooling exists:

- CL-03 case links show owner status/evidence IDs rather than copying source payloads;
- financial/healthcare/screening sensitive views enforce access policy and log access;
- ops view surfaces stuck jobs/integration failures/reconciliation status.

No universal “super admin can see all payloads” screen is permitted.

### Authorization / Compliance

- destructive privacy behavior is legal-retention gated;
- healthcare access still follows Healthcare decision even in admin/privacy support context unless Privacy worker has a separately approved system capability;
- financial sensitive access requires appropriate assurance/audit;
- FCRA/BAA evidence retention follows approved policy;
- moderation/hold decision and target execution remain separate ownership.

### Events / Jobs / Integrations

- Privacy orchestration dispatch/ack events;
- provider deletion jobs where permitted;
- moderation/hold execution events;
- Search removal request after privacy/moderation/public-readiness effect;
- operational failure/dead-letter telemetry.

### Failure Behavior

- retention unresolved: return blocked/retained-pending-policy, never hard-delete by guess;
- provider deletion fails transiently: retry and report; domain retention disposition remains explicit;
- moderation decision stale/invalid target: reject/ack failure to owner, no local case mutation;
- audit/Ops unavailable: follow root critical-audit failure policy; do not silently skip mandatory sensitive-access proof.

### Tests

- privacy enumeration/execution per Module;
- retention exemption handoff;
- anonymization field mappings;
- provider deletion retry;
- moderation/hold enforcement idempotency;
- sensitive access logging;
- Search removal after privacy/moderation;
- telemetry redaction;
- regression that Audit/Ops do not become lifecycle truth.

### Out of Scope

- legal retention-period invention;
- Privacy request intake/UI;
- Moderation case adjudication;
- generic Ops incident lifecycle implementation;
- file storage deletion mechanics beyond Media/provider public command.

### Exit Gate

Feature 12 is complete only when:

1. every CL-03 Module can enumerate and execute Privacy targets through the canonical protocol;
2. unresolved/legal-retained records are never destructively deleted by default;
3. moderation and holds execute through source/target owner boundaries;
4. all required sensitive financial/healthcare/screening accesses generate AccessAuditLog evidence;
5. provider/queue failures are operationally visible without changing domain truth;
6. privacy/moderation/audit/ops integration tests and telemetry-redaction tests pass.

---

# Phase 6 — Hardening and Production Readiness

## 13 — CL-03 Security, Reliability, Reconciliation, Backfill, Compliance, and Production Hardening

Harden the completed Cluster against concurrency, provider degradation, migration/backfill risk, privacy failure, stale projections, and unresolved legal paths before production activation.

### Objective

CL-03 is safe to operate under retries, provider outages, concurrent seller/admin actions, stale events, privacy requests, partial provider state, and production observability without violating Module ownership.

### User-visible / Observable Result

- Critical seller workflows remain deterministic under retries/outages.
- Operators can reconcile provider/source discrepancies and see dead-lettered work.
- Backfills/reindex/reconciliation are dry-run capable and idempotent.
- Sensitive data is redacted from telemetry and protected by step-up/access logs.
- Unsupported legal/provider paths are disabled by configuration/feature gate, not accidentally reachable.
- Production readiness report shows every feature exit gate, unresolved blocker, migration, and rollback/backfill plan.

### Owning Module(s)

All five CL-03 Modules remain owners of their own hardening policy and source truth. Shared platform/guardrail Modules own the generic mechanisms they expose.

### Dependencies

- Features 01–12 complete.
- Root security/deployment/observability standards.
- Current unresolved-decision register reviewed and dispositioned for production scope.

### Shared Operations Used

Hardening verifies correct use rather than introducing local copies of:

- **SH-044** idempotent commands;
- **SH-045/046** inbox/outbox event reliability;
- **SH-047/048** jobs/retry/dead-letter;
- **SH-051/052/053** lock/optimistic concurrency/lifecycle mechanics;
- **SH-055** expiry scheduling;
- **SH-059–062** provider callback/reconciliation;
- **SH-029/030/034/037/038** audit/telemetry/ops;
- **SH-091/094** Search projection boundary;
- **SH-095–098** Privacy execution;
- **SH-011–014** holds and sensitive assurance.

For each, local policy remains with the owning Module. **Do not build** any CL-03-wide replacement queue, webhook log, audit table, incident system, privacy workflow, Search client, or auth layer.

### Data / Schema

Review and harden:

- indexes for owner queries/provider references/expiry scans;
- uniqueness/idempotency constraints;
- expected-version/concurrency support;
- append-only protection for balance/provider/domain ledgers where applicable;
- foreign key/delete behavior for legally retained verification/BAA/tax records;
- safe migration of any approved removal/deprecation of compatibility fields;
- approved provider-event records for Trust/Healthcare if live providers are enabled;
- projection rebuild/backfill safety.

Any destructive migration requires:

- data inventory;
- forward migration;
- backfill/reconciliation plan;
- validation query/report;
- rollback or recovery strategy appropriate to the change;
- no reliance on Search/provider state as the source for rebuilding domain truth.

### Public Interfaces

Freeze/version all CL-03 public contracts used by other Modules. Document:

- request/response versioning;
- reason-code stability;
- pagination/limits for sensitive admin queries;
- retry semantics;
- idempotency keys;
- conflict/unavailable responses;
- deprecation policy for aliases/compatibility fields.

### Logic

Perform adversarial review of:

- action-to-gate completeness;
- stale readiness decisions;
- provider event replay/order;
- lock/race behavior;
- payout ledger correctness;
- healthcare redaction enforcement;
- Trust/FCRA legal gates;
- Search deindex/reindex correctness;
- Privacy retention behavior;
- entitlement/hold changes during active workflows;
- admin overrides and source decision provenance.

### UI / Administrative Surface

Production admin/ops surfaces must provide only the minimum metadata needed to:

- inspect failed/retrying provider work;
- trigger approved reconciliation/retry;
- review Trust/Healthcare/Payment cases under permissions;
- see public-readiness blockers safely;
- verify Search projection request state through Search-owned tooling.

Do not create raw provider/PHI/tax/background report viewers as a debugging shortcut.

### Authorization / Compliance

Security review must verify:

- server-side authorization and RLS alignment;
- step-up freshness/target binding;
- provider secret isolation;
- webhook authentication/replay defense;
- PII/PHI/tax/background data minimization;
- file privacy/signed access;
- access-audit completeness;
- retention/exemption behavior;
- no local premium/hold/verified/payout booleans as truth;
- all legal-gated paths disabled unless approved evidence model is implemented.

### Events / Jobs / Integrations

- run provider reconciliation in dry-run then controlled repair mode;
- run event replay/idempotency tests;
- verify dead-letter visibility and re-drive controls;
- test Search rebuild/deindex after source changes;
- test expiry workers at clock boundaries;
- test notification/audit provider degradation according to root criticality policy;
- document rate limits/timeouts/circuit breakers for every live provider adapter.

### Failure Behavior

Define and test expected production behavior for:

- Identity/Authority dependency outage;
- Track/Hold dependency outage;
- Search outage;
- Trust screening provider outage;
- Stripe/Connect/Tax outage;
- BAA provider outage if enabled;
- queue delay/dead letter;
- Audit or sensitive-access write failure;
- stale provider callback;
- partial privacy/provider deletion;
- migration/backfill interruption;
- corrupted/inconsistent owner projection.

No failure mode may default to “allow” for a sensitive gate because the dependency failed.

### Tests

- full typecheck/lint/unit/integration suites;
- provider contract/replay/out-of-order tests;
- concurrency and idempotency load tests for critical commands;
- payout ledger/property-based accounting invariants where practical;
- privacy/retention end-to-end tests;
- security/authorization/RLS tests;
- telemetry secret/PHI/PII leakage tests;
- Search projection/rebuild tests;
- destructive migration rehearsal if any;
- Playwright critical seller journeys;
- recovery/reconciliation drills.

### Out of Scope

- unresolved future bundle model;
- featured/promotion behavior without U-13 ruling;
- legal automation whose evidence model remains unresolved;
- new providers or product lanes introduced solely during hardening;
- architecture redesign unrelated to demonstrated production risk.

### Exit Gate

CL-03 is production-ready only when:

1. Features 01–12 exit gates remain passing in the final integrated build;
2. every live provider has signature verification, owner-specific dedupe truth, status mapping, reconciliation, timeout/retry policy, and operational visibility;
3. no production path relies on compatibility booleans or provider/Search/Audit/Ops state as domain truth;
4. all critical mutations are idempotent and concurrency-tested;
5. all mandatory sensitive accesses are step-up/authorized/audited as specified;
6. Privacy execution and legal retention behavior are tested, with unresolved destructive paths disabled;
7. Search projection removal/rebuild is proven from source truth;
8. every unresolved decision is classified as **resolved**, **production blocker**, or **explicitly out of production scope** — none is silently bypassed;
9. migrations/backfills/reconciliation have dry-run and recovery plans where applicable;
10. typecheck, lint, unit, integration, contract, provider, security, privacy/compliance, and critical E2E suites pass;
11. production readiness report and progress tracker are updated.

---

# Cross-Cluster Integration Phase

**Phase 4 / Feature 11 is the explicit cross-cluster integration phase.** It must prove the important contracts with CL-02 Search, CL-04 Gig/Order, CL-05 Media/Digital/Video, CL-06 Trust consumers, and CL-07 Notification without importing those Clusters' source truth into CL-03.

Payment's Feature 10 establishes its special CL-04 bridge at the financial/provider boundary, but Feature 11 verifies the wider event/readiness/public-projection behavior across neighboring Clusters.

No cross-cluster integration is accepted merely because a foreign table can be queried through Prisma. Contract/integration tests must demonstrate the public interface/event boundary.

# Hardening Phase

**Phase 6 / Feature 13 is the hardening phase.** It covers only CL-03-relevant production concerns:

- server authorization/RLS alignment;
- sensitive step-up/access audit;
- provider degradation and reconciliation;
- provider webhook replay/out-of-order behavior;
- concurrency/idempotency;
- ledger correctness;
- expiry/recheck jobs;
- dead letters and operational visibility;
- Search projection consistency;
- privacy/retention/provider deletion;
- backfills and destructive migration safety;
- telemetry redaction;
- performance/indexing;
- legal-gated path enforcement;
- final production readiness.

# Phase Summary

| Phase | Name | Features |
| --- | --- | --- |
| 1 | Seller and Supply Foundations | 01 Professional Profile Foundation; 02 Offering Draft, Shape, Pricing, Classification, and Media Context; 03 Professional Readiness Composition Contract |
| 2 | Trust and Regulated Readiness | 04 Verification Requirements, Consent, Packages, and Manual Check Path; 05 Verification Providers, Credentials, Expiry, Trust Projection, and FCRA Boundary; 06 Healthcare Lane, BAA, Data Boundaries, and Admin Payload Policy |
| 3 | Financial Readiness and Publication | 07 KYC, Tax Profile, Payout Account, and Financial Readiness; 08 Offering Publication and Public Professional Supply; 09 Professional Balance, Payout Request, and Transfer; 10 Payment and Sales-Tax Bridge to Transaction / Order |
| 4 | Cross-Cluster Contract Proof | 11 Readiness Change Propagation and Neighboring-Cluster Integration |
| 5 | Governance, Privacy, and Enforcement Integration | 12 Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion |
| 6 | Hardening and Production Readiness | 13 CL-03 Security, Reliability, Reconciliation, Backfill, Compliance, and Production Hardening |

**Total numbered features: 13**

# Phase Execution Pattern

Before each numbered feature:

1. Read the required root and Cluster context.
2. Read the target Module architecture and implementation plan.
3. Read public-interface sections for every dependency Module used by the feature.
4. Confirm the previous feature's exit gate is passing.
5. Check the architecture Unresolved Decisions table for any blocker affecting this feature.
6. Write the concise implementation specification for **only this feature**.
7. Confirm owner records, schemas, contracts, permissions, Shared Operations, events/jobs, providers, and tests.
8. Implement only that feature and approved sub-slices.
9. Run typecheck, lint, tests, migrations/checks, and build commands required by root standards.
10. Perform workflow verification, including negative/failure paths.
11. Update progress.
12. Update architecture only if a binding decision legitimately changed; do not use the progress update to redefine ownership.
13. Record risks, unresolved decisions, production-disabled paths, and deferred work.

A phase is not complete until every numbered feature in it has passed its exit gate.

# Required Feature Specification

Immediately before implementation, each numbered feature must receive a concise specification containing:

- **Objective** — the exact new capability.
- **Observable result** — what a user/admin/worker/consumer can verify.
- **Dependencies** — numbered features, owner Modules, SH operations, providers, unresolved rulings.
- **In scope** — exact behavior and records.
- **Out of scope** — explicit ownership/scope exclusions.
- **Owning Module** — owner of each business truth changed.
- **Data records affected** — models/enums/indexes/migrations/projections.
- **Public interfaces** — commands, queries, events, provider ports.
- **Shared operations consumed** — permanent `SH-###` IDs, local policy, do-not-build duplicates.
- **Permissions** — actor/authority/step-up/hold context.
- **Primary workflow** — ordered happy path.
- **UI/admin states** — only if applicable.
- **Provider integrations** — owner port/adapter, signature/dedupe/translation/reconciliation.
- **Jobs/events** — outbox, inbox, async jobs, expiry/retry/dead-letter.
- **Idempotency/concurrency** — semantic key, lock/version strategy, replay result.
- **Error/failure behavior** — conflict, denial, dependency outage, provider failure, manual review, partial completion.
- **Tests** — unit/integration/contract/provider/concurrency/compliance/privacy/E2E as applicable.
- **Acceptance criteria** — concrete pass/fail conditions aligned to the feature exit gate.
- **Documentation updates** — progress and any legitimate architecture/module contract change.

Do **not** pre-write giant implementation specifications for all 13 features. Specify the next numbered feature immediately before implementation so the spec reflects the real repository state and previously completed work.

# Required Completion Report

After each feature, the coding agent must report:

- Feature completed;
- Files added;
- Files changed;
- Database changes;
- Migrations;
- Dependencies added;
- Shared Operations reused, by `SH-###`;
- Public interfaces added/changed;
- Events/jobs added;
- Provider adapters/webhooks/reconciliation added or explicitly left disabled;
- Tests added/changed;
- Commands run;
- Manual/workflow verification;
- Documentation updated;
- Assumptions;
- Approved Proposed Rulings used;
- Unresolved decisions encountered;
- Known failures;
- Remaining risks;
- Deferred work;
- Exit-gate result: **PASS / FAIL**, with failed criteria listed exactly.

If the exit gate is **FAIL**, the next numbered feature must not begin unless the build plan itself explicitly declares the failed item non-blocking and the architecture supports that declaration.
