# Professional Supply & Readiness Build Plan

> **Cluster ID:** CL-03  
> **Cluster name:** Professional Supply & Readiness  
> **Repository target:** `context/clusters/professional supply & readiness/professional-supply-readiness-build-plan.md`\
> **Architecture dependency:** `context/clusters/professional supply & readiness/professional-supply-readiness-architecture.md`\
> **Plan status:** Ordered implementation roadmap; it does not redefine architecture

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

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

### Migration-baseline prerequisite (CL-03-R016)

Current Prisma declarations are not proof of a deployable database baseline. Checked-in migrations do not reproduce all current CL-03 structures and enum values. Before claiming database readiness for an affected feature, establish migration coverage for the approved schema, verify the target database baseline, and record the migration/reconciliation evidence. Historical applied migrations must not be rewritten merely to resemble Prisma; address gaps through an approved forward migration/reconciliation process. Contract work may use the existing permitted test doubles, but cannot claim database or production readiness. This documentation pass creates or changes no migration.

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
- **SH-127/090** — Media signed access/context attachment where BAA/evidence documents are stored; Healthcare owns entitlement/context, not signing.
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

Marketplace local Feature 05 completes the Offering publication transition slice only; local Feature 06 completes the required Search handoff. Neither the publication slice alone nor an untested Search request closes Cluster Feature 08 (CL-03-R018).

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
- U-120/SH-120 global jurisdiction helper remains Proposed ruling; do not depend on it.

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

## 10A — Taxable-Value Intake and Tax-Reporting Coordination

**Approved CL-03-R017:** this numbered acceptance point follows Feature 10's Payment/Order bridge and precedes Feature 11 and final hardening. Existing feature IDs remain unchanged. Payment local Features 08–09 retain their internal implementation sequence.

### Objective / Observable Result

Prove the CL-10 Prize/Rewards-to-Payment taxable-value bridge and the approved reporting scope: source-owned recognized values reach Payment without duplicate counting, jurisdiction loss, or transfer of prize/reward lifecycle ownership.

### Owning Modules and Dependencies

- Payment owns tax intake, `TaxYearEarningsSummary`, reporting state, and tax reconciliation.
- CL-10 Prize/Reward and other approved value owners retain recognition, valuation evidence, source events, and their separate value summaries.
- Cluster Feature 10 and Payment local Features 08–09 supply the relevant implementation/contracts; coordinate with the enabled source-owner features rather than duplicating them here.
- Apply the CL-03-R016 migration baseline and Payment's remaining subject-representation/persistence, reporting-rule, provider, correction, and retention gates. Automated filing remains disabled where the existing Payment plan leaves it unapproved.

### Shared Operations / Public Integration

| Operation | Invocation and local policy | Boundary / integration proof |
| --- | --- | --- |
| SH-118 `reportTaxableValue` | Source owner sends recognized subject, value/currency, jurisdiction, source identity/date, valuation evidence, and idempotency context to Payment. Payment validates approved source and tax context. | Payment owns the public intake; source recognition and fair-market-value truth stay external. Contract-test the CL-10 bridge and reject unsupported input. |
| SH-117 `aggregateYearlyReportableValue` | Payment applies the shared mechanism to its own summary using tax subject + jurisdiction + tax year + currency, durable source-event uniqueness, transactional updates, and reversals. | Each value-owning Module retains separate summary truth. Verify replay, isolation, reversal, and rebuild behavior; do not create a universal value ledger. |
| SH-044/045/046/047/048 | Reuse approved command/event idempotency, outbox, and reliable reconciliation jobs at their existing owner boundaries. | No CL-03 queue, inbox, event contract, or provider implementation is created by this coordination feature. |

### Schema / Failure / Compliance Constraints

Current `TaxYearEarningsSummary` uniqueness is insufficient under CL-03-R014. Exact tax-subject representation and persistence/migration design remain open; contract tests do not establish production aggregation readiness. Missing required subject/jurisdiction/year/currency context, unsupported source contracts, or unresolved policy must fail explicitly without inventing recognition or reporting rules. Retain existing authorization, audit, privacy, and legal/provider gates from Payment local Features 08–09.

### Tests and Numbered Acceptance Gate

1. At least one representative approved source-owner intake contract is tested, with explicit CL-10 Prize/Reward bridge coverage for the enabled scope; no source lifecycle is copied into Payment.
2. Subject/jurisdiction/tax-year/currency validation and separation match CL-03-R014 and canonical SH-117/118.
3. Concurrent/replayed source recognition and correction/reversal cannot double-count; durable identity/retention requirements are accounted for.
4. Reporting/reconciliation tests cover rebuild, source-query failure/retry, discrepancies, and unchanged source ownership.
5. Record the approved reporting scope and prove unresolved automated filing/provider/correction/retention paths remain disabled. Disabled or contract-only paths must be identified rather than reported as production-complete.
6. Database/production readiness is claimed only with the required approved persistence and migration-baseline evidence; remaining blockers remain explicit before Feature 13 hardening.

---

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

- Features 01–10 and the approved-scope coordination acceptance point 10A.
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
| 4 | Cross-Cluster Contract Proof | 10A Taxable-Value Intake and Tax-Reporting Coordination; 11 Readiness Change Propagation and Neighboring-Cluster Integration |
| 5 | Governance, Privacy, and Enforcement Integration | 12 Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion |
| 6 | Hardening and Production Readiness | 13 CL-03 Security, Reliability, Reconciliation, Backfill, Compliance, and Production Hardening |

**Total numbered features: 14 (01–13 plus 10A; existing IDs preserved)**

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

Do **not** pre-write giant implementation specifications for all 14 numbered features. Specify the next numbered feature immediately before implementation so the spec reflects the real repository state and previously completed work.

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

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.

## WA-R009 — Jurisdiction normalization status and ownership

SH-120 is Proposed ruling, not Unresolved. It shares normalization/provenance mechanics while each jurisdiction-dependent owner selects and interprets evidence for its own purpose. Location's geography does not become neutral tax/employment authority; Payment owns tax interpretation and Job Compliance owns employment-jurisdiction interpretation. An owner-specific normalized-input contract may be implemented without adopting a universal jurisdiction DTO. Production use still requires sufficient legal/provider/source evidence and an explicit binding. No local competing universal normalizer or generic legal decision service is authorized.


## WA-R012 — Purchased session allowance and Booking cardinality (P02)

Product-owner ruling approved 2026-09-29: an Order may authorize multiple scheduled sessions **only when the purchased Offering/package explicitly includes them**. Four purchased sessions permit at most four allocated session entitlements, not unlimited Bookings. This closes U-BC-02 / CL-05-U014's product choice. Do not add uniqueness on Booking.orderId.

Supply owns the offered package description. Order validates and snapshots the purchased positive integer session allowance, source/version and applicable fulfillment/cancellation/refund terms; later Offering edits cannot change the purchase. Booking owns each appointment and its conflict, hold and scheduling lifecycle. Neither a paid flag nor counting local Booking rows supplies purchase authorization.

Technical ruling: Order owns durable per-session authorization identities bounded by the purchased allowance. An idempotent reservation command binds Order/session identity to one Booking command intent and reports authorized, exhausted, denied, or unavailable with the Order version. Concurrent attempts cannot reserve the same session twice or exceed the allowance. Booking persists the reservation identity with its local conversion; an outbox acknowledgement confirms attachment. An uncertain cross-owner outcome remains reserved until reconciliation queries Booking's durable result; never release merely on transport timeout. Failed conversion with proven absence can release its reservation idempotently. This is a recoverable workflow, not a cross-owner Prisma transaction.

Rescheduling retains the session authorization through the replacement chain and does not consume another session. A completed, cancelled or no-show appointment does not itself restore allowance or prove full Order completion. Order applies the purchased terms and owner-confirmed session outcomes; refunds and cancellation adjustments are Order decisions through Payment's rail. No automatic equal-price-per-session refund or forfeiture policy is invented. Packages cannot activate without explicit applicable terms. A normal SlotLock converts at most once (U-BC-03); that safety invariant is separate from Order multiplicity.

Implementation acceptance: four-session package permits four distinct authorizations and rejects a concurrent fifth; retry returns the same identity; single-session package remains bounded; reschedule reuses authorization; timeout recovery avoids double release/allocation; source edits do not rewrite terms; partial fulfillment does not finish the whole Order; refund/cancel outcome follows snapshotted terms. Current schema lacks this complete contract; the coordinated database pass must implement it before package activation.


## WA-R018 — Durable execution, receipts and operational evidence

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R018 contract](../../reconciliation/platform-architecture-rulings.md#wa-r018--durable-execution-receipts-and-operational-evidence) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one platform-owned persistent command-idempotency/inbox/outbox/job mechanism with Postgres transactional persistence in the coordinated database pass. Module application/domain boundaries own effect semantics. A successful owner mutation atomically stores its domain change and outbox record; no transaction is held across provider/network calls. Consumers atomically claim a stable source event plus effect identity and commit their owner effect. Unknown outcomes reconcile before a new business attempt. Same scoped command key plus same canonical fingerprint replays the original result; different fingerprint conflicts. Owner/operation/subject scope is part of the key. At-least-once delivery is assumed; never promise global exactly-once execution.

Provider callbacks use verified provider/account/event identity, payload fingerprint, receipt state and separate effect/attempt state under the provider-owning Module (SH-059/060). A received/claimed record is not proof of completed effect. Duplicates preserve original proof; telemetry records observations. A retry of one semantic effect reuses its downstream idempotency identity. A genuinely new business attempt has a new identity linked to the prior result and cannot silently overwrite history. Booking workflow steps likewise carry a stable run/step/effect key. Exact tables/index names and runner library are implementation details; production runtime evaluation remains a scoped provider/operational gate, not a reason to build Module-local queues.

Adopt Ops-owned Postgres persistence for operational SystemEvent, IntegrationFailure and OpsIncident; QueueJob remains an operational projection of the platform runner, not a second executable queue. SystemEvent is append-only; correction references the original. IntegrationFailure separates occurrence identity from recovery observations; recording the same occurrence replays, another actual attempt creates another occurrence. Incident operator state is open/triaged/mitigated/resolved, with explicit authorized reopening recorded as a new transition; automatic grouping/alerts require versioned configured rules. Ops success/recovery cannot finish a business workflow. Tradeoff: durable local diagnostic queries require migrations/storage; provider dashboards remain secondary. Accept PR-CL09-05 persistence direction without claiming schema deployment or selecting retention periods.

Acceptance: concurrent identical/conflicting keys, crash after receipt and before effect, crash after domain commit and before dispatch, duplicate/out-of-order callback, lease recovery, retry exhaustion and reconciliation. Do not activate a consumer merely because a queue accepted its job.


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


## WA-R026 — Approved Review and multi-episode Dispute policy (P06–P08)

**Binding product-owner ruling, 2026-10-01.** Review input is a whole-number 1–5 star rating. Zero and half-star input are invalid; aggregate/reputation values may be fractional. Review owns the rating calculation; Professional and Search consume its versioned result, not separate scales or calculators.

Automatically publish an otherwise eligible Review after completed-Order, buyer-author and applicable safety/moderation checks pass. An author may revise rating or comment. Every proposed revision is immutable history and passes the same applicable checks before becoming the public/reputation-bearing revision. Promotion is atomic against the expected Review version; a delayed check for an older revision cannot supersede a newer one. A rejected/unavailable revision does not overwrite the previously accepted public revision; an active restriction independently controls whether any revision is public. Author editing never restores hidden/removed state or bypasses a restriction. Restoration is an explicitly authorized Review owner/Moderation action. Revisions update the contribution of the same Review; they never add another rating count. Hiding/removal withdraws its contribution; restoration uses the current eligible accepted revision.

The Order's buyer Customer or seller Professional may open a commercial dispute. Authorized support may record one on behalf of an identified participant where policy allows; preserve both actual support actor and represented participant. There is **one durable Dispute case container per Order at launch**, not one dispute episode for the Order's lifetime. Authorized reviewers may reopen that case for new evidence, a correction, or a later episode associated with the same Order, including another session of a multi-session package.

Persist a distinct immutable cycle/episode identity for each review/adjudication/settlement cycle, with opening/reopening reason, initiating/represented actor, relevant Order version, session references where applicable, evidence, decisions and outcomes. The case's current state is a projection of its current cycle; reopening never overwrites prior closed decisions or settlement proof. Serialize cycle creation and adjudication per case. A current pending cycle can receive new evidence; it does not require competing active refund/release decisions. Any concurrency policy must preserve one authoritative current case decision path.

Every financial effect requires valid current owner authorization and an idempotent identity bound to the specific cycle/decision/effect, with prior effects retained for reconciliation. Never key a new valid effect only by case ID, and never mint a fresh identity merely to retry an old effect. Reopening itself cannot replay a previous refund, charge, payout adjustment, settlement or hold-release effect. Order/Payment validate cumulative amounts and remaining authorized source value across all cycles; a new cycle is not permission to exceed the purchased/refundable amount. Dispute decides, Order coordinates transaction effects, Payment executes its rail, and Holds retains its own action-scoped lifecycle.

Opening/appeal windows remain separately versioned product policy; no numerical deadline is introduced. Bind the applicable policy version to each cycle. Product case windows do not redefine statutory/provider rights. Current Prisma's one-case relation is compatible with the container rule but does not supply cycle/revision proof; the coordinated database pass must add that representation before activation.

Acceptance: ratings 0/6/fractions rejected, fractional aggregate allowed; two revisions race without double counting; failed safety check leaves the accepted revision unchanged; hidden/removed edit cannot restore; buyer/seller/support attribution; unrelated actor denied; later-session episode reuses the case with a new cycle; old cycle remains reconstructible; replay of old financial result cannot affect the new cycle; valid new effect has its own authorization and respects cumulative Order limits. These are required implementation checks, not claims of executed feature tests.

Duplicate collapse: CL04-U034/035/036/038/040 and owner §9/§35 product questions; CL04-U039 retains its versioned configuration gate. WA-R022/023 technical proof, financial finality and assurance rules remain binding. Classification: PRODUCT_OWNER_CHOICE — RESOLVED by explicit approval; enforcement/revision/cycle identity details AI_RESOLVED.

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

## WA-R037 — Payment effects, payout reservation and tax evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Payment owns immutable financial operation and attempt history, not just outbox delivery. Every effect has unique owner/sourceType/sourceId/sourceRevision/effectKind/effectOrdinal plus currency, semantic payload hash and original-effect reference for compensation. Reuse with different amount/subject/currency conflicts. Verified provider ingress receipt is separate from Payment and Track effect receipts; route by approved provider object/metadata ownership, never both owners applying the same business effect. Unknown routing is quarantined. Payment receipt fields: provider/account/eventId, eventType, fingerprint, handlerVersion, target operation, receivedAt, processing/attempt/recovery state and committed effect references. No raw secret payload by default; legal retention remains externally supplied.

Balance accounting uses immutable signed minor-unit effects with explicit bucket vectors and per-currency conservation. Earnings credit available (or pending until the approved availability rule); payout reservation moves available -A/reserved +A atomically with request acceptance; reservation release moves reserved -A/available +A only once after known cancellation/failure with no possible pending provider movement; successful payout moves reserved -A/paid +A. Transport retries have zero ledger effect. Provider return/reversal records its actual returned amount as a new linked effect, paid -R/available +R only after verified return and applicable financial restrictions; it never mutates the original payout. Fees/refunds/chargebacks are separate authorized signed effects, never hidden in payout status. Unknown money movement retains reservation and reconciles. Existing one-amount enum records are insufficient to infer these vectors: use an explicit owner allocation/bucket effect structure and forward constraints. This is accounting of processor-held value, not permission to introduce a wallet or new financial product.

At launch each PayoutTransfer belongs to one PayoutRequest; Order references are optional immutable allocation provenance, not a second transfer source. A request supplies an explicit validated active payoutAccountId; no guessed default among multiple accounts. Capture all blocking Hold IDs and decision versions in a separate immutable evaluation snapshot; blockedByHoldId is explanatory only. Reevaluate current holds/account/financial readiness immediately before dispatch. Keep one semantic transfer identity and stable provider idempotency key through network retries. Record each transport attempt separately. A terminal failed transfer never reopens; a new request/transfer after confirmed nonmovement and reservation release requires fresh authorization. Unknown is nonterminal even if transport timed out. No automatic retry of a terminal financially reversed/paid transfer.

Ratify the minimum Payment §9 graphs with these restrictions: KYC rejected/expired/disabled attempts are terminal; new attempt linked to previous evidence. TaxProfile rejected/expired creates a new collection revision, never overwrites submitted documents. One current applicable selector per subject+purpose+jurisdiction/provider scope points explicitly to the accepted evidence; pending new evidence does not silently replace valid current proof, while revocation immediately invalidates it. PayoutAccount disabled is terminal for that account; restriction recovery uses verified current provider evidence. PayoutRequest failed/cancelled/reversed terminal; processing cannot cancel without proven no movement. PayoutTransfer failed/cancelled/reversed terminal. SalesTaxCalculation changed quote requires a new calculation; finalized is immutable, voiding is a separately evidenced provider operation. Tax submission rejected/failed uses a new linked submission revision; transport retries of an unacknowledged submission retain semantic identity. Filed recipient correction creates replacement evidence and a link, preserving prior filing. No enum setter or provider callback bypasses these rules.

Tax subject is a Payment-owned stable subject reference mapped to an identified legal recipient, with explicit User and optional ProfessionalProfile provenance; profile identity is not automatically a separate legal taxpayer. Effective mappings/versioned evidence prevent accidental subject merge. Aggregate key is taxSubjectId + jurisdiction + taxYear + currency + reportingRegime; retain source owner/id/revision/recognition type and unique reversal identity. Prize-owned summaries use the same dimensions and preserve their own source valuation truth. SH-019 supports an explicit tax_fulfillment purpose and tax dimension; no second generic tax-readiness service is needed. Payment owns TaxReportingSubmissionStatus and TaxReportingRecipientStatus. Reporting bundle uniqueness includes regime/jurisdiction/year/currency/submission series/revision; recipients unique within submission by tax subject and applicable form/category. Rule versions, form requirements, recognition dates, thresholds and correction legality remain approved external configuration, never invented constants.

Order binds final calculation ID to exact immutable quote/order revision, currency, line IDs and buyer-tax-location evidence revision. Payment preserves line-level taxable basis, tax, jurisdiction, provider tax code and liability role even for mixed-liability lines. Tax-location provenance includes approved source owner, source/evidence revision, validation method/result and captured/effective time, minimum required location fields; it is not public-location consent. Each authorized refund has immutable line allocations against the original captured quantities/basis/tax and links its own provider refund and tax reversal attempts. Cumulative refunds cannot exceed captured refundable allocation; lock the operation allocation counters and reject mismatched currency. Use deterministic minor-unit residual allocation only within an approved tax/provider allocation policy; do not guess rates or liability. Partial/multiple refund representation requires separate child records, not one overwritten reversalId. Provider unsupported/ambiguous results stay pending/manual review, never fabricated successful tax reversal. Full provider/rule qualification remains external before affected execution.

Required verification: concurrent reservation conservation, duplicate callback/compensation, timeout followed by paid result, multiple holds, account changes before dispatch, line-level cumulative refund cap, subject/jurisdiction separation, replacement filing traceability. No live financial test or migration is claimed by this architecture decision.

## WA-R038 — Trust evidence provenance and screening boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

VerificationConsent remains a screening-context linkage: canonical ConsentLogId, identified User/subject, check type, provider, purpose, requirement/package revision and linked check. Generic acceptedAt/IP/user-agent fields are compatibility evidence only and cannot independently validate consent. New linkage requires canonical consent proof and current applicability checks; migration preserves unknown provenance without inventing consent. Each check has exactly one typed subject consistent with its User and optional Professional/Candidate profile; employer-requested screening additionally requires identified Organization/requester membership, Job/Application context, purpose and approved permissible-purpose evidence. Employer sponsorship is not activated by this technical representation.

Adopt the existing minimum Trust §9 check/package/badge graphs. Terminal checks never reopen; recheck is a new linked attempt with current consent/payment/requirement proof. License credential identity stays stable, but every verification/refresh/revocation creates an immutable evidence revision linked explicitly to its establishing VerificationCheck or authorized manual evidence decision. Current credential projection points to a valid revision; expired/revoked proof is never silently overwritten. Trust owns explicit check/credential-to-Media evidence join records, document kind, evidence revision and retention classification. Media owns bytes/scanning/access. No generic Media ownerType/ownerId joins are introduced.

Trust owns append-only check, credential, package/requirement and badge lifecycle histories with aggregate revision and source evidence, committed with outbox. Its provider effect receipt uses provider/account/eventId/handlerVersion uniqueness, fingerprint, check/credential target, normalized event kind, receivedAt, processing and attempt/recovery status, committed transition/effect refs. Unknown subject/events are quarantined; provider callbacks cannot mark a check passed from an unrecognized state. Short-lived provider report access is fetched on demand through an authorized adapter where supported. If persistence is necessary, reportToken is envelope-encrypted secret material with expiry/key version/rotation and restricted audited access; never public DTO/log/Search. Exact provider capability and retention remain external activation evidence.

Requirement rules are immutable schema-versioned records keyed to supported action, typed subject/target, jurisdiction and accepted classification revision; no free-form JSON policy or new implicit mandatory screening. Supported action vocabulary includes profile activation/publication, Offering publication, Gig response/acceptance, Order participation, Booking participation, Job application and Interview participation only where an explicitly approved requirement policy applies. Optional self-initiated Candidate/Professional screening remains optional; action enum presence does not mandate it. Single provider per package at launch; mixed-provider packages are deferred. Provider selection/check-type/jurisdiction rollout must be evidenced before activation, not inferred from a vendor enum.

Identity checks establish only their named verified identity claim; financial readiness stays Payment-owned; a healthcare credential check establishes that credential only, never BAA or Healthcare lane clearance. Broad platform_verified/gold_trust_check/healthcare_verified badges have no launch issuance or authorization effect without explicit scoped claim definitions; preserve legacy facts without minting misleading composite assurance. Public badge DTOs contain the approved claim label/type, subject profile reference, validity and evidence revision only. A badge never replaces current owner readiness.

FCRA technical evidence must link immutable notice template/version/content hash, identified recipient, approved purpose/check/report revision, delivery attempt and verified delivery outcome, policy/jurisdiction version, legally determined timing anchors, dispute submissions and outcome, final-action authorization and history. Notification delivery receipt is evidence, not a legal conclusion. Exact notice content, channels, required waits, adverse-action transitions and retention remain EXTERNAL_REQUIREMENT; no numeric windows or automated adverse decisions are approved here. Required tests cover consent-link mismatch, recheck history, expired supporting evidence, duplicate/late callback, secret exclusion and subject-context mismatch.


## WA-R065 — Shared sensitivity policy governance and Healthcare applicability

Implementation follows the corresponding applied owner architecture ruling. Required acceptance evidence before activation: unknown category denial; normal data remains private without publication authority; multi-context restriction intersection; stale classification grant invalidation; audit-unavailable disclosure denial; unqualified Healthcare provider denial. The versioned policy catalog and actual cryptographic/provider evidence must exist before enabling the protected surface.

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Professional and Marketplace supply their own minimized WA-R070 descriptors and stable affected-target enumeration. Taxonomy/AI cannot scan or mutate their joins. Healthcare applicability and qualified provider context remain separate gates; no unrestricted biography/description forwarding. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## Domain bridge qualification — 2026-10-15

For WA-R077; WA-R078; WA-R080, sequence the relevant owner contract/DTO fixtures, shared durable mechanism qualification and bilateral negative/replay/currentness checks before dependent consumer activation. Use the exact Module architecture ports and source scopes. Database posture D and policy/provider requirements gate their affected slices; no broad product implementation or parallel lane is authorized by this reconciliation. R079 creates no required Order-to-Sweepstakes dependency. Do not treat a successful queue dispatch, enumerator page or provider response as completion of the originating lifecycle.

## WA-R081–083 — Integrated bridge sequence

Follow Module owner contracts and the complete bridge inventory before cross-Cluster integration. CONTRACT_ONLY work may establish schemas/fakes; FOUNDATION_CAPABILITY is required before actual effects; executable bilateral and external evidence precede freeze/activation. R081 named queries/receipts, R082 Media invalidation, and R083 disabled optional paths supersede only the corresponding historical open labels. Keep current source checks at action/disclosure boundaries. Do not begin whole-Cluster parallel work, root synthesis or runtime implementation from source-coverage counts alone.

## WA-R084 — Order/Payment source event symmetry

Order outcome facts include Payment as a registered reconciliation consumer. Payment queries bound historical purchase and current settlement facts, preserving R037 economic dedupe and existing dispatch authority. This is an asynchronous source-fact edge, not an Order/Payment commit dependency or permission to send money. Bilateral runtime fixtures remain unqualified.


## WA-R085–087 — Platform convergence

Current platform reconciliation covers `healthcare_regulated_services`, `marketplace_supply`, `payment_payout_tax`, `professional_eligibility`, `trust_verification_screening`. Module owners retain all lifecycles and source facts. R085 separates terminating fact inputs from composed permissions, readiness, credential issuance and Hold release; R086 locates one shared execution capability and bootstrap dependencies; R087 routes Organization commercial schema responsibility to Track without enabling monetized ATS.

Coordinate required ports and semantic fixtures before actual adapters; do not require complete upstream Clusters from a contract edge. Source commits precede outbox delivery and downstream projection/Notification/provider setup. Recovery reuses stable effect identity and cannot infer completion from acknowledgment, telemetry or a read model. The platform dependency graph records typed edges and critical cycle dispositions; action-specific external gates remain scoped.

Root architecture synthesis is conditional on the recorded Gate 5 exit and Gate 6 posture confirmation. A root build plan, runtime choice, database migration, interface freeze and parallel implementation lanes remain later prerequisites. No such implementation approval is made by this coordination appendix.

**WA-R003/085 screening coordination.** Paid screening is a separate Order source under WA-R003: createChargeableOrder uses the authoritative Trust package quote and actual purchaser/subject relationship, not Professional seller readiness and not completion of the check being purchased. Trust initiates the paid check only after the source-bound Order qualification. evaluateVerificationReadiness reads existing requirement/evidence; it does not synchronously create a purchase or start a new check. Ordinary marketplace seller gates remain on their actual source/action, and acquired Order entitlement is evaluated separately from new-purchase seller eligibility. This terminates the initial paid-screening dependency without a fake seller or a free screening bypass.
