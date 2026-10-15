# Marketplace Supply Module Implementation Plan

> **Module ID:** `marketplace_supply`  
> **Module name:** Marketplace Supply Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-implementation-plan.md`\
> **Architecture dependency:** `context/clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md`\
> **Plan status:** Ordered Module implementation roadmap; subordinate to root architecture and CL-03 build plan; does not redefine ownership.

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

## Core Principle

Implement Marketplace Supply through narrow, owner-preserving, independently reviewable slices:

```text
observable Offering behavior
→ validated command/query
→ Marketplace-owned domain policy
→ authoritative Marketplace write/read
→ canonical shared-operation calls
→ owner domain event / Search / Notification / Audit effect
→ tests
→ feature exit gate
```

Marketplace Supply owns present-tense sellable supply. It does not become the seller-readiness engine, file system, digital-delivery system, Search engine, tax/payment system, moderation system, privacy system, or transaction system merely because those systems interact with an Offering.

This Module plan follows the Cluster sequence. It primarily implements Marketplace-owned portions of CL-03 Feature 02, Feature 08, Feature 11, Feature 12, and Feature 13. It must not reorder or bypass Cluster prerequisites such as Professional Profile Foundation or Professional Readiness Composition.

## Build Rules

1. Follow root Workin Ants project overview, architecture, code standards, Canonical Shared Operations, CL-03 architecture, and CL-03 build plan.
2. Implement one numbered Marketplace feature at a time. The next feature starts only after the current exit gate passes.
3. Marketplace Supply owns only the truth declared in `context/clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md`.
4. Consume foreign truth through approved public interfaces/events. Do not introduce direct cross-Module repositories as an implementation shortcut.
5. Reuse canonical SH operations by permanent ID. Do not recreate aliases locally.
6. Validate every mutation server-side and authorize it through SH-001/SH-002.
7. Lifecycle transitions must be explicit, transaction-safe, and concurrency-safe.
8. Replayed commands and consumed events must be idempotent through shared primitives.
9. Generic queue, retry, lock, outbox, audit, observability, Search, Media, Notification, and Privacy infrastructure stays outside Marketplace Supply.
10. Marketplace Supply has no direct provider adapter. R2, Typesense, Mux, Stripe, Bedrock, notification providers, and compliance providers stay behind their owning Modules.
11. `Offering.status` is lifecycle truth. `isPublic` cannot independently publish or unpublish.
12. `isFeatured` remains inert until U-13 is resolved.
13. Bundle creation/publication remains disabled until U-15 is resolved.
14. `priceFromCents` is derived; no feature may treat it as independently authored price truth.
15. Digital-goods records and `SalesTaxLineItem` remain externally owned despite historical Marketplace registry claims.
16. Search is downstream projection. Source changes request Search work through SH-091.
17. Privacy orchestration remains Privacy-owned. Marketplace implements only the owner executor protocol.
18. Moderation/Legal owns enforcement decisions; Marketplace owns only the Offering lifecycle consequence.
19. Unresolved architecture is surfaced as a blocker or disabled path, never invented by a coding agent.
20. Every numbered feature ends with tests and a concrete exit gate.

## Preconditions

### Hard platform dependencies

The following must exist, or have a root-approved implementation available before the first Marketplace feature that relies on them:

- Prisma/PostgreSQL repository foundation;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-046 `publishDomainEvent` transactional outbox before reliable cross-Module effects are claimed;
- SH-051/052/053 concurrency/lifecycle primitives or root-approved equivalent before publication/restriction races are enabled;
- structured validation according to root standards (project stack identifies Zod);
- test framework and database integration-test harness.

### Hard upstream Module dependencies

Before Marketplace Feature 02 draft creation can be considered integrated:

- CL-03 Feature 01 Professional Profile Foundation must expose a stable ProfessionalProfile owner/context query sufficient to prove Offering ownership.
- CL-02 Taxonomy must expose SH-023 `validateTaxonomyAssignment` or a stable equivalent contract.

Before Marketplace Feature 03 media attachment can be production-enabled:

- Media / File Access must expose SH-090 `attachValidatedMedia` or a stable ready-asset contract.

Before Marketplace Feature 05 publication can pass its exit gate:

- CL-03 Feature 03 Professional Readiness Composition must implement SH-016 for `publish_offering`;
- the required Trust/Healthcare/Track/Hold dependencies behind SH-016 must be available for the applicable Offering contexts;
- **U-01 must be resolved for `publish_offering`** so financial readiness timing is explicit;
- Moderation/Hold public restriction facts must be available;
- CL-05 Digital Goods/Video readiness contracts must exist for digital/course paths that require them.

Before Marketplace Feature 06 Search handoff can pass its exit gate:

- Search / Public Visibility must expose SH-091;
- SH-094 source-projection contract/pattern must be available.

Before Marketplace Feature 08 production privacy completion:

- Privacy SH-095/096/097 protocol must exist;
- Audit SH-029 and Observability SH-034/037/038 must exist for required paths;
- Notification SH-041 must exist for enabled lifecycle notifications.

### Dependencies that may initially be stubbed behind contracts

The Module may continue early draft development using contract fakes/test doubles for:

- Media ready-asset checks;
- Digital Goods readiness;
- Video readiness;
- Search refresh;
- Notification delivery request;
- Privacy executor dispatcher;
- AI Taxonomy consumer integration;
- Transaction / Order checkout-source consumer.

A stub does not transfer ownership. The public contract must remain owner-shaped so the stub can later be replaced without a Marketplace schema redesign.

### Unresolved decisions that constrain implementation

- **U-01:** financial readiness timing for publication — blocks Feature 05 production completion.
- **U-13:** `isFeatured` — all behavior disabled.
- **U-14:** overlapping visibility signals — no independent `isPublic` behavior.
- **U-15:** bundle composition — bundle path disabled.
- **U-16:** stored `priceFromCents` semantics — calculate at read time unless approved otherwise.
- Module MA-U-01 through MA-U-05 from `context/clusters/professional supply & readiness/Marketplace Supply Module/marketplace-supply-module-architecture.md` constrain unsupported lifecycle/retention/kind-change cases.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 — Marketplace Contracts, Repository Boundary, and Aggregate Validation Foundation

### Objective

Establish the Marketplace Supply code boundary, typed public contracts, owner-only repository, input validation, error/reason-code vocabulary, and initial aggregate policies without changing foreign truth.

### Observable Result

- Marketplace Supply has a single owner-scoped repository for its models.
- Public command/query contracts compile independently from foreign repositories.
- Unsupported bundle and `isFeatured` behavior are explicitly rejected/inert.
- Marketplace domain policies can validate supported Offering shape and return stable errors.
- Contract tests prove that another Module can request owner facts without importing Prisma repositories.

### Cluster Build-Plan Link

- **Primary:** CL-03 Feature 02 — Offering Draft, Shape, Pricing, Classification, and Media Context.
- **Preparation for:** CL-03 Feature 08 — Offering Publication and Public Professional Supply.

### Dependencies

- root repository/module conventions;
- current Prisma schema;
- CL-03 Feature 01 ProfessionalProfile public context contract;
- SH-001, SH-002;
- root validation/error conventions;
- module architecture Proposed Rulings PR-05/06/07 as inherited from Cluster architecture.

### In Scope

- create proposed `src/modules/marketplace-supply` boundary according to root layout;
- define validation schemas for supported Marketplace command inputs;
- define `MarketplaceSupplyRepository` interface/implementation limited to Marketplace-owned models;
- define public DTOs for owner facts, management view, checkout source facts, delivery requirements, public readiness, and target validation;
- define stable Marketplace error categories/reason-code namespace;
- implement `validateOfferingKindShape` skeleton for supported kinds;
- define explicit mutable/immutable field maps per command family;
- centralize non-authoritative-field treatment (`isPublic`, `isFeatured`, `priceFromCents`, healthcare trigger fields) so they cannot accidentally become gate truth.

### Out of Scope

- Offering creation UI or persistence workflow;
- publication transitions;
- Search projection;
- Media upload/attachment;
- digital-goods/video integrations;
- Order/checkout;
- bundle composition;
- migrations that remove legacy fields;
- generic platform infrastructure.

### Module-Owned Data

No new source model is required. Contracts target:

- `Offering`;
- `ServiceDetails`;
- `ProductDetails`;
- `CourseDetails`;
- `PricingTier`;
- `OfferingMedia`;
- `OfferingTag` contextual row lifecycle.

### Public Interfaces

Introduce types/contracts, not yet every implementation:

- `CreateOfferingDraftCommand`;
- `UpdateOfferingCoreCommand`;
- `OfferingManagementView`;
- `OfferingEligibilityContext`;
- `OfferingCheckoutSourceFacts`;
- `OfferingDeliveryRequirements`;
- Marketplace SH-024 decision type aligned to owner-specific current contract;
- Marketplace SH-123 target-reference result.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity & Access.** Invocation: protected contract entry point. Local policy: requested Marketplace action. **Prohibited duplicate:** current-user/marketplace-auth helper.
- **SH-002 `authorizeResourceAction` — Role / Authority.** Invocation: protected owner/context action. Local policy: Offering/Profile relationship facts. **Prohibited duplicate:** local RBAC engine.
- **SH-003 `queryOwnerFacts` — Proposed contract only.** Use only if already approved/implemented; otherwise call the explicit Professional owner context query. **Prohibited duplicate:** universal cross-domain repository.

### Domain Logic

- A supported Offering kind is `service`, `product`, or `course` for current implementation.
- `bundle` returns `POLICY_UNRESOLVED`/unsupported until U-15 resolves composition.
- `isFeatured` cannot appear as a command input that changes product behavior.
- `isPublic` cannot appear as a generic settable publication input.
- `priceFromCents` cannot appear as an independently authored price input.
- Foreign relation IDs are references only; repository methods must not expose write methods for foreign owner tables.

### Authorization / Compliance

- Actor resolution and authorization are modeled in application-layer contracts, not domain entities.
- The repository accepts already authorized owner IDs or scoped transaction context; it does not interpret roles itself.
- Draft persistence is not conditioned on complete Trust/KYC/Healthcare unless later policy explicitly says so.

### Database / Transaction Behavior

- Document current uniqueness/relationship constraints in repository tests.
- Do not add a schema migration merely to mirror a TypeScript abstraction.
- If implementation discovers a missing hard invariant that cannot be safely enforced in application transactions, raise a Proposed Ruling before migration.

### Events / Jobs

None required in Feature 01 beyond defining event contract types. SH-046 is not exercised until a meaningful mutation exists.

### Failure Behavior

Stable failures include validation, forbidden, unsupported/unresolved, not found, and stale/conflict placeholders. No raw Prisma/provider errors escape public contracts.

### Tests

- unit tests for `validateOfferingKindShape` baseline;
- contract compile tests for public DTOs;
- repository boundary tests proving no foreign write API exists;
- validation tests for prohibited client-set lifecycle/projection fields;
- regression test that `bundle` and `isFeatured` are not accidentally enabled;
- architecture lint/review test if repository has dependency-boundary tooling.

### Documentation Updates

- update Marketplace progress tracker entry;
- record any contract naming decision that becomes binding;
- update module architecture only if actual ownership/interface semantics change.

### Acceptance Criteria

1. Marketplace code can be imported by a consumer without importing Marketplace Prisma internals.
2. Foreign lifecycle tables are not writable through Marketplace repository.
3. unsupported bundle and featured paths are explicit.
4. stable error/reason contracts exist.
5. no duplicate auth/readiness/search/media infrastructure is introduced.

### Exit Gate

Run root typecheck/lint/tests plus Marketplace unit/contract tests. Feature 02 cannot begin until the repository boundary and contract suite prove owner-only data access and all architecture-prohibited fields remain non-authoritative.

---

## 02 — Draft Offering and Kind-Specific Shape

### Objective

Allow an authorized ProfessionalProfile to create and edit a draft service, product, or course Offering with one valid Marketplace-owned kind-specific business shape.

### Observable Result

- A professional can create a draft service/product/course Offering.
- The draft is persisted under the correct ProfessionalProfile.
- The correct detail row can be created/updated.
- Contradictory or wrong-kind detail mutations fail transactionally.
- Bundle remains unavailable.

### Cluster Build-Plan Link

- **Direct implementation of:** CL-03 Feature 02.

### Dependencies

- Module Feature 01;
- CL-03 Feature 01 ProfessionalProfile owner/context query;
- Taxonomy SH-023 for Domain/Category validation;
- SH-001, SH-002, SH-044, SH-046, SH-052;
- current Prisma Offering/detail models.

### In Scope

- `createOfferingDraft`;
- `updateOfferingCore` for Marketplace-owned core fields;
- `upsertServiceDetails`;
- `upsertProductDetails`;
- `upsertCourseDetails`;
- initial `changeOfferingKind` only for a safe, explicitly approved draft-only path;
- draft management query sufficient for editor UI;
- basic Offering editor UI if root UI organization places this Module in charge of it.

### Out of Scope

- PricingTier management beyond placeholder read state;
- OfferingMedia/OfferingTag mutations;
- publication/active state;
- Search;
- digital grants/playback;
- Order creation;
- external provider calls;
- post-purchase kind changes;
- bundle.

### Module-Owned Data

- `Offering`;
- `ServiceDetails`;
- `ProductDetails`;
- `CourseDetails`;
- `OfferingKind` and delivery-mode enums as used by these records.

### Public Interfaces

Implement:

- `createOfferingDraft`;
- `updateOfferingCore`;
- `changeOfferingKind` for approved draft-only subset;
- `upsertServiceDetails`;
- `upsertProductDetails`;
- `upsertCourseDetails`;
- `getOfferingManagementView` baseline;
- `getOfferingEligibilityContext` baseline owner facts.

### Shared Operations Used

- **SH-001** actor resolution.
- **SH-002** resource authorization. Local policy: controlling ProfessionalProfile relationship.
- **SH-023 `validateTaxonomyAssignment` — Taxonomy.** Validate Domain/Category before persistence. **Prohibited duplicate:** local taxonomy repository/normalizer.
- **SH-044** for idempotent draft creation.
- **SH-046** for `OfferingCreated` / meaningful `OfferingUpdated` events when downstream use is established.
- **SH-052** for stale edit rejection.

### Domain Logic

- enforce `(professionalProfileId, slug)` uniqueness;
- validate core title/slug/currency/copy rules per root standards;
- require exactly the supported detail type for locally complete draft state;
- wrong-kind detail command returns validation/conflict without partial writes;
- date/duration/limit fields must satisfy basic local consistency;
- Product/Course external URLs are validated but do not become delivery entitlement;
- `ProductDetails.fileAssetId` is legacy reference only and cannot serve as paid-download authorization;
- `requiresHealthcareCompliance` and `dataSensitivity` cannot be used as external readiness proof.

### Authorization / Compliance

- only controlling professional or explicitly approved admin/support action may mutate;
- no Trust/Healthcare/KYC completion needed merely to create a draft unless entitlement policy later says otherwise;
- no client may directly set `status`, `isPublic`, `isFeatured`, restriction timestamps, or foreign compliance state.

### Database / Transaction Behavior

- draft create and initial detail create occur in one transaction where supplied together;
- kind change removes/replaces incompatible detail rows transactionally only in the approved draft-only case;
- if a current row is stale, return `STALE_VERSION` and do not merge silently;
- unique slug conflict returns deterministic domain conflict.

### Events / Jobs

- emit `OfferingCreated` on successful first creation;
- emit `OfferingUpdated` when a change matters to consumers;
- no job required.

### UI / Admin Surface

If root UI is in scope:

- draft editor for service/product/course;
- kind-specific fields;
- visible draft status;
- bundle hidden/disabled;
- no publication button behavior yet beyond disabled/preparatory state.

### Failure Behavior

- invalid input: no write;
- unauthorized: no owner data leak;
- duplicate slug: conflict;
- wrong kind/detail: conflict/validation;
- stale edit: return current version;
- Taxonomy unavailable: if Domain/Category must be validated for the mutation, fail retryably; do not accept unvalidated IDs.

### Tests

- unit: kind/detail policy, dates/durations, prohibited fields;
- integration: create/update each supported kind;
- transaction test: contradictory detail state cannot commit;
- uniqueness test: duplicate professional slug;
- authorization: owner/unrelated professional/admin approved cases;
- idempotency: duplicate draft create;
- concurrency: stale core/detail edit;
- regression: no foreign record writes.

### Documentation Updates

- progress tracker;
- document any approved draft-only kind-change policy;
- update architecture if schema invariant/migration becomes binding.

### Acceptance Criteria

1. service/product/course draft flows work end to end;
2. bundle cannot be created;
3. one accepted kind/detail shape is enforced;
4. ProfessionalProfile is referenced through owner contract, not written/read via a generic cross-domain repository;
5. client cannot set lifecycle/projection fields directly.

### Exit Gate

Typecheck/lint/unit/integration/authorization/concurrency tests pass. Manual or automated editor flow verifies create → edit → read for all supported kinds. No publication, Search, Media, Digital Goods, Video, or Payment code has leaked into the feature.

---

## 03 — Current Pricing, Taxonomy Attachments, and Presentation Media Context

### Objective

Complete the editable draft aggregate with current PricingTier truth, accepted OfferingTag attachments, and ready OfferingMedia presentation context while preserving Taxonomy and Media ownership.

### Observable Result

A professional can:

- create/update/deactivate/reorder current pricing tiers;
- attach/detach accepted tags;
- attach/detach/reorder ready media;
- view a complete draft management state without Marketplace implementing file or taxonomy infrastructure.

### Cluster Build-Plan Link

- **Direct implementation of:** CL-03 Feature 02.

### Dependencies

- Module Features 01–02;
- SH-023 Taxonomy validation;
- SH-090 Media validated attachment or stable ready-asset contract;
- SH-001/002/044/046/052;
- PR-05 and PR-06;
- U-16 remains unresolved for stored `priceFromCents` maintenance.

### In Scope

- PricingTier command family;
- derived price-from read behavior;
- OfferingTag attach/detach;
- OfferingMedia attach/detach/reorder;
- management query expansion;
- editor UI for pricing, taxonomy, and media where root UI permits;
- public events for classification/pricing changes where required.

### Out of Scope

- tax calculation or SalesTaxLineItem writes;
- Media upload/scanning/signed URL mechanics;
- Taxonomy vocabulary creation/normalization;
- Search indexing;
- publication;
- digital download grants/policy;
- `isFeatured` behavior.

### Module-Owned Data

- `PricingTier`;
- `OfferingMedia`;
- `OfferingTag` row lifecycle under PR-05;
- `priceFromCents` only as derived output/projection, not independent truth.

### Public Interfaces

Implement:

- `createPricingTier`;
- `updatePricingTier`;
- `deactivatePricingTier`;
- `reorderPricingTiers`;
- `attachOfferingTag`;
- `detachOfferingTag`;
- `attachOfferingMedia`;
- `detachOfferingMedia`;
- `reorderOfferingMedia`;
- expanded `getOfferingManagementView`;
- `resolveDerivedPriceFrom` internal query/policy.

### Shared Operations Used

- **SH-001/002** authorization.
- **SH-023** tag assignment validation. Local policy: which classification is required to be complete.
- **SH-090 `attachValidatedMedia` — contextual owner/Media truth.** Invocation: before OfferingMedia insert. Local policy: presentation role/order. **Prohibited duplicate:** file uploader/scanner/presign helper.
- **SH-044** replay-safe attach/create commands.
- **SH-046** classification/pricing/media-context events where downstream use exists.
- **SH-052** stale update/reorder protection.

### Domain Logic

- price cents nonnegative and currency normalized/allowed;
- PricingTier current truth changes future purchases only;
- no direct SalesTaxLineItem write;
- derived minimum uses active tiers only;
- until U-16 is approved, calculate `priceFromCents` for reads/projections rather than treating stored field as authoritative;
- OfferingTag requires canonical active compatible tag from Taxonomy;
- `source/confidence/verified` values do not let Marketplace declare a new TaxonomyTag valid;
- OfferingMedia insert requires Media-ready asset and correct context;
- media detach does not delete MediaAsset.

### Authorization / Compliance

- controlling professional/admin authority required;
- draft pricing/tag/media changes are not publication approval;
- sensitive/private assets cannot be exposed by attaching them to an Offering if Media policy disallows public presentation.

### Database / Transaction Behavior

- composite keys make repeated media/tag attachment naturally conflict/idempotent; command layer normalizes same semantic replay to success/no-op;
- reorder operations should update all relevant rows transactionally;
- PricingTier update/deactivate uses expected version or parent Offering version strategy;
- no stored price projection update until U-16 is settled, unless implementation explicitly approves a transactional derived write.

### Events / Jobs

- emit pricing/classification/media-context changes only when a consumer needs them;
- no separate worker unless U-16 later approves asynchronous projection maintenance.

### UI / Admin Surface

- pricing tier manager;
- Taxonomy selector using canonical data;
- media gallery/picker limited to ready assets;
- no upload implementation inside Marketplace controls; Media component/flow may be invoked through its owner interface.

### Failure Behavior

- invalid/negative price: validation denial;
- Taxonomy tag invalid/inactive: normalized validation denial;
- Media asset unready/frozen/forbidden: attachment denial, Media state unchanged;
- duplicate attachment: idempotent existing result where semantic request matches;
- stale reorder: conflict;
- dependency unavailable: retryable failure; do not persist unvalidated foreign references.

### Tests

- PricingTier unit/integration tests;
- derived minimum property tests over active/inactive tiers;
- historical Order regression: Marketplace updates do not mutate Order snapshots;
- tag contract tests with Taxonomy;
- media contract tests with Media;
- duplicate attach/reorder concurrency tests;
- regression that Marketplace never writes Digital Goods/SalesTax/MediaAsset/TaxonomyTag.

### Documentation Updates

- progress tracker;
- if U-16 is resolved during implementation, update architecture before enabling stored projection behavior.

### Acceptance Criteria

1. current pricing is fully manageable and source-correct;
2. tags/media are contextual joins only;
3. no foreign lifecycle is mutated;
4. derived minimum is deterministic and non-authoritative as stored field;
5. draft management query provides complete editor state.

### Exit Gate

All Feature 03 tests pass, including Taxonomy/Media contract tests and historical-price regression. CL-03 Feature 02 Marketplace portion is complete only when service/product/course draft, current pricing, accepted taxonomy, and ready media context work end to end.

---

# Phase 2 — Public Lifecycle and Marketplace Decisions

## 04 — Stable Management/Public Queries, Owner Facts, and Local Readiness Decisions

### Objective

Expose stable Marketplace read boundaries needed by Professional Eligibility, Search, Order, Booking, Digital Goods, Video, Trust, Healthcare, Moderation, and UI without letting those consumers read Marketplace tables directly.

### Observable Result

Consumers can obtain only the Marketplace facts they are entitled to:

- management aggregate;
- public Offering view when currently eligible;
- Offering eligibility context;
- checkout source facts;
- delivery requirements;
- target-reference validation;
- Marketplace local public-readiness result.

### Cluster Build-Plan Link

- **Completes/strengthens:** CL-03 Feature 02 public contracts.
- **Prerequisite for:** CL-03 Feature 08 and Feature 11.

### Dependencies

- Module Features 01–03;
- SH-002 authorization;
- SH-024 public-readiness contract;
- SH-123 target validation;
- current CL-03 dependency interface definitions;
- no publication transition required yet.

### In Scope

- `getOfferingManagementView` final contract;
- `listProfessionalOfferings`;
- `getPublicOfferingBySlug` contract/implementation for currently eligible lifecycle states, while publication itself remains Feature 05;
- `getOfferingEligibilityContext`;
- `getOfferingCheckoutSnapshot` source facts;
- `getOfferingDeliveryRequirements`;
- Marketplace SH-024 `evaluatePublicReadiness` local decision;
- Marketplace SH-123 `validateOwnedTargetReference`;
- reason-code redaction rules.

### Out of Scope

- creating Order snapshots;
- Search indexing;
- delivery grant issuance;
- professional readiness composition;
- provider status interpretation;
- publication mutation.

### Module-Owned Data

Read-only access to Marketplace-owned aggregate and projections. No new model required.

### Public Interfaces

All interfaces listed in Scope become versioned/stable enough for contract tests. Define minimum fields explicitly; avoid returning Prisma models directly across Module boundaries.

### Shared Operations Used

- **SH-001/002** for protected management/source-fact queries.
- **SH-024 `evaluatePublicReadiness`** shared contract/separate Marketplace policy. Local policy: Offering status/local shape/approved current owner decisions. **Prohibited duplicate:** Search-side readiness inference.
- **SH-123 `validateOwnedTargetReference`** target-owner contract. Local policy: allowed Offering relationship types/statuses. **Prohibited duplicate:** foreign generic target repository.
- **SH-003** only if approved and helpful for reciprocal owner fact lookups; do not make it a new dependency if still Proposed.

### Domain Logic

- management view may include draft/restricted Marketplace source fields according to authority;
- public view returns not found/hidden rather than leaking restricted state to unauthorized users;
- public readiness does not use `isPublic` alone;
- checkout facts are present-tense and explicitly marked as source inputs that Order must snapshot;
- delivery requirements expose business mode/configuration, not grants/provider tokens;
- owner-fact DTOs minimize data and include source version/current status.

### Authorization / Compliance

- public query exposes only public allowlisted fields;
- protected owner facts require actor/authorized Module context according to root internal-interface conventions;
- healthcare/verification/financial detail is not embedded in Marketplace facts;
- reason codes remain safe and may collapse external blockers to generic categories.

### Database / Transaction Behavior

Read-only, consistent snapshot where multiple Marketplace tables are assembled. Use a transaction/read consistency level only if root data layer requires it for coherent aggregate reads.

### Events / Jobs

None.

### UI / Admin Surface

- management dashboard/list uses `listProfessionalOfferings`;
- public detail surface may use `getPublicOfferingBySlug` if product route ownership sits with Marketplace;
- no Search result UI or admin compliance UI is created here.

### Failure Behavior

- unauthorized protected query: forbidden/not found per leakage policy;
- stale source version request: current facts returned with current version or conflict according to contract;
- external readiness dependency unavailable: SH-024 returns non-allow/dependency-unavailable where the public decision requires current external facts.

### Tests

- public/protected DTO contract tests;
- data minimization tests;
- authorization/leakage tests;
- Order contract test that present price is explicitly not historical truth;
- Booking/Digital/Video delivery DTO tests;
- SH-123 relationship/status tests;
- regression that public view ignores `isPublic` as sole authority.

### Documentation Updates

- publish public interface section/version in module context or interface registry;
- progress tracker.

### Acceptance Criteria

1. direct consumer reads of Marketplace Prisma tables are unnecessary for documented use cases;
2. DTOs expose minimum required facts;
3. public-readiness reasons are stable and safe;
4. downstream consumers cannot infer ownership or write authority from the contract.

### Exit Gate

All public-contract and security tests pass. Feature 05 cannot begin until SH-016 consumers can receive `getOfferingEligibilityContext` without direct Marketplace repository access.

---

## 05 — Offering Publication, Pause, Resume, Restriction, Restoration, and Archive

### Objective

Implement the authoritative Marketplace Offering lifecycle transitions that make supply public or non-public while consuming current seller/readiness/moderation/hold decisions from their owners.

### Observable Result

- a structurally valid draft can publish only after current approved gates allow it;
- blocked publication returns actionable safe blockers and leaves Offering non-active;
- active Offerings can pause/archive;
- resume re-evaluates all current gates;
- Moderation/Hold decisions can restrict/restore through typed owner commands;
- a stale publish cannot overwrite a newer restriction.

### Cluster Build-Plan Link

- **Direct implementation of:** CL-03 Feature 08 — Offering Publication and Public Professional Supply.

### Dependencies

- Module Features 01–04;
- CL-03 Feature 03 SH-016 `publish_offering` decision;
- Track SH-005 when applicable;
- Hold SH-011;
- Taxonomy requirements SH-022/023;
- Moderation SH-103/current restriction contract;
- Digital Goods/Video readiness contracts for applicable product/course paths;
- SH-044/046/051/052/053;
- **U-01 resolved for `publish_offering` before production exit gate.**

### In Scope

- `evaluateOfferingLocalPublicationReadiness`;
- `requestOfferingPublication`;
- `pauseOffering`;
- `resumeOffering`;
- `archiveOffering`;
- `applyOfferingRestriction`;
- `restoreOffering` for explicitly approved transitions only;
- publish/readiness UI action and blocker display;
- lifecycle events;
- hooks/outbox entries needed for downstream Search/Notification, with actual Search source projection integration completed in Feature 06.

### Out of Scope

- Search provider execution;
- Order checkout/payment;
- digital grant issuance;
- promotion/featured ranking;
- bundle publication;
- unresolved `rejected`/archive-reopen transitions not explicitly approved;
- moderation case adjudication.

### Module-Owned Data

- `Offering.status`;
- approved lifecycle timestamps (`frozenAt`, `hiddenAt`, `takedownAt`) only where their exact semantics are tied to an implemented restriction transition;
- Marketplace domain event semantic payloads.

### Public Interfaces

Implement/finalize:

- `requestOfferingPublication`;
- `pauseOffering`;
- `resumeOffering`;
- `archiveOffering`;
- `applyOfferingRestriction`;
- `restoreOffering`;
- Marketplace SH-024 public-readiness decision used before public effect.

Do not expose generic `setOfferingStatus(status)`.

### Shared Operations Used

- **SH-001/002** publisher/resource authority.
- **SH-005** seller entitlement only as approved local/SH-016 policy input.
- **SH-011** current active holds.
- **SH-016 `evaluateProfessionalReadiness` — Professional Eligibility.** Invocation: publication/resume with immutable Offering context. Local policy: Marketplace shape/lifecycle remains separate. **Prohibited duplicate:** rebuild Trust/Healthcare/Payment/Entitlement logic.
- **SH-022/023** canonical classification/requirement context.
- **SH-024** public-readiness contract.
- **SH-044** idempotent publish/restrict/restore.
- **SH-046** transactional owner events.
- **SH-051** aggregate lock for publish/restriction races where required.
- **SH-052** expected-version conflict.
- **SH-053** shared transition plumbing/local graph.
- **SH-103** Moderation-owned decision execution envelope.
- **SH-029** generic audit for approved lifecycle/admin enforcement proof.

### Domain Logic

Publication order is binding:

```text
actor + SH-002 authority
→ current Offering/version/status
→ Marketplace local shape/pricing/classification/media/delivery validation
→ SH-016 Professional Eligibility(publish_offering, immutable Offering context)
→ current hold/moderation/public-readiness check
→ Marketplace transition under SH-053
→ authoritative write + SH-046 outbox atomically
→ downstream work may proceed
```

- `resumeOffering` repeats the entire current gate sequence.
- no stale readiness result can be reused after a relevant source version changes;
- moderation restriction cannot be overridden by a professional publish/resume request;
- unsupported lifecycle adjacency returns conflict/unresolved;
- `rejected` semantics are implemented only if a later approved feature spec defines source/reopen rules;
- `isPublic` is not written as a separate source decision.

### Authorization / Compliance

- U-01 action matrix is mandatory before publication exit;
- healthcare/verification gates apply only through canonical triggered context;
- hold scope is respected;
- moderation/legal source decision IDs are required for enforcement commands;
- blocker response is sensitivity-safe;
- no client status mutation.

### Database / Transaction Behavior

- lock/CAS current Offering before critical transition;
- re-read current status and relevant local Marketplace fields inside transition transaction;
- authoritative state write + outbox append atomically;
- restriction timestamp updates commit with status if they are part of the approved transition;
- idempotency record/claim follows root SH-044 behavior;
- rollback means no domain event is published.

### Events / Jobs

Emit versioned lifecycle events:

- `OfferingActivated`;
- `OfferingPaused`;
- `OfferingRestricted`;
- `OfferingRestored`;
- `OfferingArchived`.

No Search provider job here; event/outbox enables Feature 06 handoff.

### UI / Admin Surface

- publish action with current blocker summary;
- pause/archive controls where allowed;
- restricted state display;
- remediation links to owner surfaces without raw provider/compliance data;
- no featured control;
- no bundle publish action.

### Failure Behavior

- gate denial: `READINESS_BLOCKED`, no mutation;
- U-01 unresolved: `POLICY_UNRESOLVED`, no mutation;
- dependency unavailable: fail closed/retryable;
- stale version: conflict;
- moderation race: restriction/newer version wins; stale publish fails;
- audit/outbox failure follows root critical transaction policy; do not emit unreliable side effect after a rolled-back write.

### Tests

- unit transition matrix for implemented transitions;
- E2E blocked → remediate → publish;
- SH-016 contract integration;
- healthcare/high-risk trigger regression;
- U-01 unresolved fail-closed test until resolution, then approved matrix tests;
- publish versus edit/restriction concurrency;
- idempotent publish/restrict/restore replay;
- regression: `isPublic`, `isFeatured`, TrustBadge, healthcare trigger booleans cannot bypass gates;
- event/outbox transaction test.

### Documentation Updates

- record approved U-01 result in Cluster/module architecture before enabling production publication;
- record exact implemented transition table;
- progress tracker.

### Acceptance Criteria

1. Marketplace is sole writer of publication lifecycle;
2. publication/resume use current owner decisions;
3. unavailable required dependency never defaults to allow;
4. moderation restriction is race-safe;
5. events publish transactionally;
6. unsupported lifecycle branches remain unavailable.

### Exit Gate

Feature 05 passes the Offering publication transition slice only: U-01 is resolved, all implemented transitions are concurrency/idempotency tested, and the blocked→publish journey works without direct foreign DB access. It is a prerequisite to local Feature 06 and does not close CL-03 Feature 08. Local Feature 06 must also complete reliable Search-request handoff and required integration tests before the full Cluster Feature 08 gate can pass (CL-03-R018).

---

# Phase 3 — Cross-Module Workflow Integration

## 06 — Search Projection and Order / Booking / Delivery Contract Proof

### Objective

Connect active Marketplace source truth to Search and neighboring commerce/delivery consumers through stable public contracts without transferring lifecycle ownership.

### Observable Result

- active/restricted/paused/archived changes produce controlled Search refresh requests;
- Search receives a deterministic safe source projection;
- Order can snapshot current Offering/PricingTier source facts through a public query;
- Booking receives service delivery requirements;
- Digital Goods/Video receive product/course context and Marketplace consumes their readiness without owning grants/provider state.

### Cluster Build-Plan Link

- **Completes:** CL-03 Feature 08 Search handoff after the local Feature 05 publication slice; the Cluster gate closes only after both slices and required Search-request/integration tests pass (CL-03-R018).
- **Directly supports:** CL-03 Feature 11 — Readiness Change Propagation and Neighboring-Cluster Integration.

### Dependencies

- Module Features 01–05;
- Search SH-091/094;
- Transaction / Order public source/snapshot contract;
- Booking public contract;
- Digital Goods and Video readiness contracts;
- Media source projection rules for public media references;
- SH-046 event/outbox.

### In Scope

- `buildOfferingSourceProjection`;
- SH-091 request after relevant lifecycle/public field changes;
- `getOfferingCheckoutSnapshot` contract proof with Order;
- `getOfferingDeliveryRequirements` contract proof with Booking/Digital/Video;
- contract test harnesses and one integrated public Offering/Search path;
- safe public media references according to Media policy.

### Out of Scope

- Typesense client/index worker/query implementation;
- Order status/payment/agreement writes;
- Booking creation;
- digital download/playback grants;
- Media signed URL implementation;
- tax calculation;
- Search ranking/promotion.

### Module-Owned Data

No new authoritative model. Marketplace source projection is a deterministic rebuildable DTO.

### Public Interfaces

Finalize/prove:

- SH-094 Marketplace projection builder;
- SH-091 request integration;
- `getOfferingCheckoutSnapshot`;
- `getOfferingDeliveryRequirements`;
- public Offering query compatibility with Search route/deeplink;
- optional owner-fact event/DTO for AI Taxonomy consumer if that interface is in current build scope.

### Shared Operations Used

- **SH-094 `buildSourceProjection` — source owner pattern.** Invocation: after current public-readiness allow. Local policy: Marketplace field allowlist and version. **Prohibited duplicate:** Search raw DB reconstruction.
- **SH-091 `requestSearchProjectionRefresh` — Search.** Invocation: publish/update/pause/restrict/restore/archive/privacy-relevant change. Local policy: source action/reason/version. **Prohibited duplicate:** SearchUpsertEvent/Typesense client.
- **SH-046** reliable Marketplace source events.
- **SH-041** only for approved user-facing lifecycle notifications, not Search mechanics.
- **SH-090/087** Media contracts when source projection/public detail needs approved media representation.
- **SH-109 `snapshotExternalDecision`** is not Marketplace-owned; Order may use snapshot mechanism after consuming current source facts. Marketplace must not own the historical snapshot.

### Domain Logic

- source projection built only from current authoritative Marketplace fields plus owner-approved public signals;
- projection must not include raw professional readiness evidence, provider IDs, private URLs, PHI, financial data, or moderation case detail;
- Search refresh action reflects source state but Search owns execution/retry/reconciliation;
- checkout snapshot query returns selected current tier facts; Order decides and persists historical snapshot;
- delivery requirements describe business intent only;
- downloadable/course publication does not imply access grant creation.

### Authorization / Compliance

- public source projection requires SH-024 allow;
- protected checkout/delivery queries expose only necessary source facts;
- Search projection must be privacy-safe;
- public media follows Media visibility policy.

### Database / Transaction Behavior

- Search request is downstream side effect driven by committed Marketplace event/outbox; transient Search failure must not roll back an already committed Offering transition;
- repeated Search request uses stable idempotency source version/action;
- checkout source query should expose Offering/PricingTier version enough for Order to detect stale selection.

### Events / Jobs

- Offering event → Search request handler;
- handler uses SH-045 dedupe where event consumer boundary exists;
- SH-047/048 durable retry if Search request is asynchronous;
- no local Search reconciliation worker.

### Failure Behavior

- Search unavailable: source truth remains active; refresh request retries/dead-letters visibly;
- stale Search event: handler fetches current Marketplace state/source version and requests correct current action;
- Order requests inactive/invalid tier: Marketplace returns conflict/not purchasable source facts;
- Digital/Video readiness unavailable: public digital/course decision fails closed where required; no fallback provider logic.

### Tests

- projection allowlist snapshot tests;
- Search request contract/idempotency tests;
- Search outage test proving source truth remains intact;
- de-index/re-index integration test;
- Order checkout-source contract test, including stale tier version;
- Booking delivery DTO test;
- Digital Goods/Video ownership regression;
- public media/privacy leakage tests.

### Documentation Updates

- publish Marketplace source-projection schema/version contract;
- record Order/Booking/Delivery public interface versions;
- progress tracker.

### Acceptance Criteria

1. Search can rebuild Offering projection from owner-approved Marketplace contract;
2. Marketplace never writes SearchUpsertEvent or calls Typesense;
3. Order/Booking/Delivery consumers need no direct Marketplace repository;
4. no downstream owner state is mutated by Marketplace;
5. public projection contains only allowlisted data.

### Exit Gate

Search publish→index request and pause/restrict→remove request are verified through contract/integration tests. Order/Booking/Digital/Video contract tests pass. No direct foreign table/provider access exists in Marketplace integration code.

---

## 07 — Dependency Change Propagation and Moderation Enforcement

### Objective

Make Marketplace Supply react reliably to changes in seller readiness, taxonomy requirements, entitlement/holds, moderation, media, and delivery readiness while preserving current source-owner decisions and event idempotency.

### Observable Result

- affected active Offerings are reevaluated when relevant dependencies change;
- stale/out-of-order events do not cause stale lifecycle changes;
- moderation/legal actions are applied idempotently through SH-103;
- public Search projection is removed/restored when Marketplace public readiness changes;
- no cluster-wide readiness or processed-event table is created.

### Cluster Build-Plan Link

- **Direct implementation of Marketplace portion of:** CL-03 Feature 11.
- **Also supports enforcement portion of:** CL-03 Feature 12.

### Dependencies

- Module Features 01–06;
- platform outbox/inbox SH-045/046;
- SH-047/048;
- Professional readiness/owner events;
- Taxonomy requirement events;
- Hold/Moderation event/command contracts;
- Media/Digital/Video readiness events where available;
- Search SH-091;
- Observability SH-037/038.

### In Scope

- `reevaluateOfferingPublicationState` worker;
- event handlers for approved relevant source changes;
- SH-045 consumer dedupe;
- current-state refetch before local action;
- SH-103 moderation decision execution;
- Search refresh after changed public consequence;
- retry/dead-letter/telemetry behavior;
- explicit no-op behavior when dependency change does not alter Marketplace state/public readiness.

### Out of Scope

- changing ProfessionalProfile/Trust/Healthcare/Payment/Track/Hold source records;
- generic event bus or queue implementation;
- Search reconciliation;
- moderation case decisioning;
- Notification delivery infrastructure;
- universal cross-Module readiness table.

### Module-Owned Data

- Offering status only when approved Marketplace local consequence requires a change;
- Marketplace event/outbox semantics;
- no new propagation source table.

### Public Interfaces

- event consumer handlers are internal but contract-tested against owner events;
- `applyOfferingRestriction` / `restoreOffering` remain public target-owner commands;
- SH-024/094/091 may be invoked after reevaluation.

### Shared Operations Used

- **SH-045 `deduplicateDomainEvent`** consumer inbox.
- **SH-046** owner events.
- **SH-047 `enqueueReliableJob`** durable reevaluation.
- **SH-048 `executeRetryWithBackoff`** transient retry.
- **SH-038 `recordQueueTelemetry`** worker attempts/dead letter.
- **SH-037 `recordIntegrationFailure`** dependency failures.
- **SH-051/052/053** critical local transition race control.
- **SH-091** Search refresh after current state change.
- **SH-103** Moderation-owned enforcement command.
- **SH-041** Notification request only after source event if product policy says to alert.

### Domain Logic

- event is a trigger to reevaluate, not authoritative current truth;
- worker fetches current Offering and current required owner decisions before irreversible local change;
- if current source version supersedes event, current truth wins;
- if seller readiness is lost, Marketplace restricts/de-publicizes only if approved Marketplace/Cluster policy defines that consequence; otherwise it may only request Search reevaluation or surface non-public readiness without inventing a new status;
- moderation decision source ID/version must be validated and mapped through local transition policy;
- restoring public supply requires current gates again;
- duplicate event produces one local effect.

### Authorization / Compliance

- system-event handler uses approved system actor context;
- moderation commands verify source decision authenticity/authorization under root internal-command rules;
- event payloads contain safe IDs only;
- no sensitive blocker details placed in Search/Notification payloads.

### Database / Transaction Behavior

- consumer inbox claim and local effect follow platform transaction semantics;
- lock/CAS Offering for lifecycle consequence;
- local write + outbox atomic;
- if no local source change, handler may still request Search refresh only when current projection state is expected stale and owner policy allows.

### Events / Jobs

Potential consumed event categories:

- underlying dependency-owner changes only where an approved producer contract supplies them; no assumed `ProfessionalReadinessChanged` event (CL-03-R005);
- taxonomy assignment/requirements changed;
- hold applied/released;
- moderation action authorized/reversed;
- Media asset readiness/freeze/deletion changed;
- Digital Goods policy/asset readiness changed;
- Course video readiness changed;
- entitlement changed where it affects Marketplace action/public readiness.

Exact event names are dependency-owned and must come from their public contracts. The replacement producer/consumer handoff for downstream Offering consequences remains unresolved under CL-03-R005; do not invent an event or infer a producer commitment from this reevaluation feature.

### Failure Behavior

- dependency unavailable: retry; no allow by absence;
- duplicate event: no duplicate effect;
- stale event: current source wins;
- permanent malformed event: dead-letter/ops visibility;
- unsupported lifecycle consequence: explicit policy-unresolved/manual-review result rather than guessed transition;
- Search unavailable: Search request retries; source state remains authoritative.

### Tests

- duplicate/out-of-order event tests;
- current-state refetch regression;
- readiness lost/restored scenarios for approved policies;
- moderation restriction/restore idempotency;
- publish/restriction event race;
- Search deindex/reindex reaction;
- dead-letter telemetry;
- contract tests proving no foreign table read fallback.

### Documentation Updates

- document exact subscribed event contracts and consequence matrix;
- update unresolved register if a dependency event lacks enough semantics;
- progress tracker.

### Acceptance Criteria

1. every enabled dependency-change handler is idempotent and current-state based;
2. Marketplace writes only Offering truth;
3. no generic propagation/readiness table exists;
4. stale events cannot re-publicize restricted supply;
5. Search/public effects follow current owner state.

### Exit Gate

Run event replay/out-of-order suite, moderation enforcement integration, Search deindex/reindex E2E, queue failure/dead-letter checks, and dependency-boundary regression tests. Feature 08 governance work cannot claim production readiness until this event path is reliable.

---

# Phase 4 — Privacy, Audit, Notification, and Operational Integration

## 08 — Marketplace Privacy Executor, Audit Evidence, Safe Notifications, and Operational Telemetry

### Objective

Complete Marketplace Supply's owner responsibilities for privacy fulfillment, generic action proof, safe lifecycle notifications, and operational diagnostics without creating duplicate Privacy/Audit/Notification/Ops lifecycles.

### Observable Result

- Privacy can enumerate Marketplace-owned subject data and instruct retain/anonymize/delete/detach actions;
- retained/order-referenced records are not destructively erased by guess;
- Search removal occurs as a separate projection effect;
- important lifecycle/admin/privacy actions append generic Audit evidence where required;
- enabled notifications go through Notification owner with safe variables;
- queue/dependency failures are visible through Ops without altering Offering truth.

### Cluster Build-Plan Link

- **Direct implementation of Marketplace portion of:** CL-03 Feature 12 — Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion.

### Dependencies

- Module Features 01–07;
- Privacy SH-095/096/097/098;
- Audit SH-029;
- Search SH-091;
- Media deletion/detach public operations for file mechanics when Privacy instructs actual object action;
- Notification SH-041;
- Observability SH-034/037/038;
- retention policy evidence currently available; MA-U-04 remains unresolved for exact durations/fields.

### In Scope

- Marketplace SH-096 subject-data enumerator;
- Marketplace SH-097 retention-fact provider;
- Marketplace SH-095 executor for approved Marketplace targets;
- SH-098 field mapping for approved anonymization;
- Search removal request after privacy disposition;
- Media-context detach without direct object deletion;
- generic Audit calls for required Marketplace lifecycle/privacy/admin actions;
- safe Notification requests for enabled lifecycle events;
- telemetry sanitization and IntegrationFailure/queue telemetry use.

### Out of Scope

- PrivacyRequest/DataErasureJob/DataRetentionExemption creation/status;
- legal retention-period invention;
- Media object deletion implementation;
- Notification provider/delivery records;
- generic AuditEvent schema/writer;
- Ops incident/queue infrastructure;
- moderation adjudication;
- protected financial/healthcare access workflows not owned by Marketplace.

### Module-Owned Data

Potential privacy targets:

- `Offering` personal/commercial copy;
- `ServiceDetails`/`ProductDetails`/`CourseDetails` owner-held URLs/configuration where personal data exists;
- `PricingTier` where subject-specific personal data is not normally expected but ownership/retention relationship exists;
- `OfferingMedia` context;
- `OfferingTag` context;
- Marketplace-owned projections only.

### Public Interfaces

Implement Marketplace owner endpoints/contracts for:

- SH-096 `enumerateSubjectData`;
- SH-097 `evaluateRetentionRequirement`;
- SH-095 `executePrivacyInstruction`;
- export serializer contribution where Privacy protocol requests it.

### Shared Operations Used

- **SH-095** execute owner action.
- **SH-096** enumerate owner records.
- **SH-097** provide retention facts; Privacy owns exemption record.
- **SH-098** anonymization mechanism/local field map.
- **SH-091** Search removal/update.
- **SH-029** generic audit.
- **SH-041** Notification delivery request.
- **SH-034** sanitize telemetry.
- **SH-037** dependency/integration failure.
- **SH-038** job telemetry.
- **SH-044** idempotent privacy execution if replayed.
- **SH-090/Media owner command** where contextual detach/object action must be coordinated.

### Domain Logic

- archive is not erasure;
- privacy target execution checks current Order/commercial retention facts through approved owner contracts, not direct foreign repositories;
- if retention basis or exact destructive disposition is unresolved, return `retained`/`blocked-pending-policy`, not hard delete;
- anonymization preserves required keys/referential integrity while removing allowed personal copy;
- OfferingMedia context may be detached locally; object deletion is commanded to Media only when Privacy/retention policy permits;
- Search removal is separate and does not prove database erasure;
- generic Audit records action evidence but do not become privacy/job source truth.

### Authorization / Compliance

- privacy executor accepts only authenticated/authorized Privacy system instruction, not arbitrary user direct deletion;
- export data is minimized to Marketplace-owned subject data;
- no raw foreign compliance/provider data is exported by Marketplace;
- notification variables are safe;
- ordinary public Offering reads do not create a new sensitive access log; protected media still follows Media/SH-030 policy if applicable.

### Database / Transaction Behavior

- privacy instruction execution is idempotent;
- multi-row anonymization/detach uses transaction where atomic local outcome is required;
- retained results do not mutate data beyond permitted anonymization;
- local result + owner event/audit/outbox follow root transaction criticality policy.

### Events / Jobs

- privacy execution may emit `OfferingUpdated`/`OfferingArchived`/privacy-specific owner fact event if required by Search/consumers, but must not invent a Privacy lifecycle event;
- Search request durable retry as needed;
- no Marketplace retention scheduler until legal duration policy exists.

### Failure Behavior

- unresolved retention: retained/pending-policy, no destructive delete;
- Media deletion unavailable: return partial/retryable according to Privacy protocol, preserving explicit disposition;
- Search unavailable: privacy DB action may succeed while Search removal remains durable/retryable according to Privacy orchestration criticality;
- Audit mandatory failure: follow root critical-audit policy, never silently omit required proof;
- Notification failure: does not rewrite Offering truth.

### Tests

- privacy enumeration pagination/inventory;
- retain/anonymize/delete/detach mapping;
- retained Order-linked Offering scenario;
- unresolved retention fail-safe;
- Media object non-deletion regression;
- Search removal after privacy disposition;
- idempotent privacy replay;
- Audit call completeness;
- Notification payload sensitivity;
- telemetry redaction / no raw description/provider data in errors;
- regression that Audit/Ops/Privacy records do not replace Offering truth.

### Documentation Updates

- record Marketplace subject-data map and supported dispositions;
- record any legal retention blocker rather than guessing duration;
- progress tracker;
- architecture only if retention semantics become binding.

### Acceptance Criteria

1. Privacy orchestrator can fulfill Marketplace target protocol without direct Marketplace DB ownership;
2. unresolved retention never results in destructive deletion;
3. Search/Media effects use owner interfaces;
4. required Audit/Notification/Ops calls are safe and separate from domain truth;
5. telemetry contains no prohibited sensitive payloads.

### Exit Gate

Privacy integration, audit/notification contract tests, telemetry leakage tests, and Search/Media separation tests all pass. Marketplace portion of CL-03 Feature 12 is complete.

---

# Phase 5 — Hardening and Production Verification

## 09 — Marketplace Security, Concurrency, Replay, Backfill, Performance, and Production Hardening

### Objective

Prove Marketplace Supply is safe under concurrent edits/publication/enforcement, retries, stale events, Search outages, privacy execution, migration/backfill work, and public traffic while all neighboring ownership boundaries remain intact.

### Observable Result

- critical commands are deterministic under retries/concurrency;
- stale/out-of-order events cannot incorrectly publish or restore supply;
- Search can be rebuilt from Marketplace source projections;
- migrations/backfills have dry-run and recovery plans;
- provider outages in neighboring Modules fail publication safely rather than creating local fallbacks;
- security/authorization/data-minimization checks pass;
- production readiness report identifies every unresolved decision as resolved, production blocker, or explicit out-of-scope path.

### Cluster Build-Plan Link

- **Direct implementation of Marketplace portion of:** CL-03 Feature 13 — Security, Reliability, Reconciliation, Backfill, Compliance, and Production Hardening.

### Dependencies

- Module Features 01–08 complete;
- CL-03 Features 01–12 required dependencies complete for production scope;
- root security/deployment/observability standards;
- unresolved-decision register reviewed;
- production Search/Media/Professional Eligibility/Privacy contracts available for enabled paths.

### In Scope

- final schema/index review for Marketplace queries;
- concurrency/load tests;
- idempotency replay tests;
- event replay/out-of-order drills;
- Search rebuild/deindex/reindex drills;
- privacy partial-failure drills;
- migration/backfill rehearsal for any approved schema/projection changes;
- public query performance/index review;
- authorization/RLS alignment review;
- telemetry/PII leakage review;
- contract freeze/version documentation;
- critical Playwright seller journey.

### Out of Scope

- new bundle architecture;
- featured/promotion design;
- new providers;
- new compliance policy invented during hardening;
- architecture redesign unrelated to demonstrated risk;
- removing all legacy fields unless an approved migration exists.

### Module-Owned Data

Review all Marketplace-owned records and indexes. No new source record should be introduced merely for hardening unless an approved architecture ruling requires it.

Potential approved changes may include:

- stronger expected-version support;
- additional indexes for owner/status/public projection queries;
- safe deprecation of non-authoritative compatibility fields;
- DB constraint supporting kind/detail invariant if approved and migration-safe.

### Public Interfaces

Freeze/version:

- all Marketplace public commands/queries;
- blocker reason codes;
- owner fact DTOs;
- Search source projection schema/version;
- Privacy executor protocol implementation;
- domain event versions;
- retry/idempotency semantics.

### Shared Operations Used

Hardening verifies correct use of, and forbids replacements for:

- SH-001/002 auth/authority;
- SH-005/011/016/022/023/024 readiness/gates;
- SH-029/034/037/038 audit/ops safety;
- SH-041 notifications;
- SH-044/045/046 idempotency/inbox/outbox;
- SH-047/048 jobs/retry;
- SH-051/052/053 concurrency/lifecycle;
- SH-127/090 Media boundary;
- SH-091/094 Search boundary;
- SH-095–098 Privacy;
- SH-103 Moderation enforcement;
- SH-123 target validation.

### Domain Logic

Adversarial review covers:

- every path that can make an Offering active/public;
- every path that can remove/restrict/restore public supply;
- stale readiness result reuse;
- kind/detail contradictions;
- current pricing versus Order history;
- source projection consistency;
- `isPublic`/`isFeatured`/`priceFromCents` compatibility misuse;
- digital-goods/sales-tax ownership leakage;
- privacy retain/anonymize behavior;
- admin/system enforcement provenance.

### Authorization / Compliance

Verify:

- server authorization on every mutation and protected read;
- RLS behavior aligns with application authority where root architecture uses RLS;
- client cannot set status/restriction/projection fields;
- public source projection is allowlisted;
- no sensitive foreign data in logs/events/notifications/Search;
- no local premium/verified/healthcare/payment/hold booleans as truth;
- unresolved U-01/U-13/U-14/U-15/U-16/MA-U items are disabled or formally resolved for production scope.

### Database / Transaction Behavior

- stress unique slug concurrency;
- stress publish/edit/restriction/restore races;
- verify detail shape invariant under concurrent kind/detail changes;
- verify media/tag/tier idempotency;
- verify authoritative write + outbox atomicity;
- inspect query plans/indexes for professional listing, public slug, status/public projection, active tier, media/tag aggregates;
- any destructive migration has inventory, forward migration, backfill, validation report, and recovery/rollback strategy;
- Search is never used as rebuild source for Marketplace truth.

### Events / Jobs

- replay/out-of-order domain events;
- dead-letter and re-drive worker tests;
- current-state fetch behavior under delayed event;
- Search outage/recovery;
- dependency outage behavior for Professional Eligibility/Taxonomy/Media/Digital/Video/Hold;
- no failure defaults to public allow.

### Failure Behavior

Define/test:

- Identity/Authority outage;
- Professional Eligibility outage;
- Taxonomy outage during relevant mutation;
- Media outage during attachment;
- Digital Goods/Video readiness outage during publication;
- Search outage after commit;
- Notification outage;
- Audit/Ops outage according to root criticality;
- Privacy partial completion;
- stale/duplicate Moderation command;
- migration interruption;
- corrupted derived `priceFromCents` if stored — source tiers must permit rebuild.

### Tests

- full typecheck/lint/unit/integration/contract suite;
- authorization/RLS tests;
- concurrency/load tests on critical commands;
- command idempotency/replay tests;
- event replay/out-of-order tests;
- Search projection rebuild/deindex/reindex tests;
- Privacy E2E;
- telemetry secret/PII leakage tests;
- destructive migration rehearsal if any;
- Playwright critical journey:

```text
create ProfessionalProfile (dependency)
→ create Offering draft
→ configure kind/details/pricing/taxonomy/media
→ blocked publish with safe reasons
→ dependency remediation
→ publish
→ public projection request/search visibility
→ pause
→ resume with reevaluation
→ moderation restriction
→ restore if approved
→ archive
```

- contract regression proving no direct Digital Goods/SalesTax/Search/Media/Order/provider ownership.

### Documentation Updates

- freeze interface/event/source-projection versions;
- final Marketplace production-readiness report;
- progress tracker;
- architecture decision updates for any genuinely resolved U/MA-U items;
- migration/backfill/recovery runbooks where relevant.

### Acceptance Criteria

1. Features 01–08 exit gates remain passing in integrated build.
2. All critical Marketplace mutations are authorization-, idempotency-, and concurrency-tested.
3. no active/public path relies on `isPublic`, `isFeatured`, provider state, Search state, or foreign compatibility booleans as authority.
4. Search can rebuild from Marketplace source truth.
5. privacy behavior is safe and unresolved destructive cases remain disabled.
6. no direct provider client or foreign lifecycle repository exists in Marketplace Supply.
7. every unresolved decision is classified for production scope.
8. performance and migration/backfill evidence is documented.

### Exit Gate

Marketplace Supply is production-ready only when:

1. all Marketplace numbered feature gates pass;
2. CL-03 Feature 08/11/12/13 Marketplace dependencies pass their Cluster gates;
3. U-01 is resolved for enabled publication paths;
4. U-13 featured behavior and U-15 bundle behavior remain disabled unless separately resolved and implemented through new approved features;
5. U-14/U-16 compatibility fields cannot independently control truth;
6. critical command and event race suites pass;
7. Search projection removal/rebuild is proven;
8. Privacy executor/retention-safe behavior is proven;
9. typecheck, lint, unit, integration, contract, authorization, concurrency, privacy, security, projection, and critical E2E suites pass;
10. production readiness report and progress tracker are updated.

---

# Module Integration Phase

**Phase 3 / Features 06–07 are the explicit Marketplace Supply integration phase.** They must prove contract boundaries with the important neighbors rather than querying foreign Prisma tables because those tables happen to be related.

Minimum contract proof:

- Professional Eligibility → Marketplace: SH-016 `publish_offering` decision with Marketplace `OfferingEligibilityContext`;
- Taxonomy → Marketplace: SH-022/023;
- Media → Marketplace: SH-090 and approved public/protected media references;
- Marketplace → Search: SH-094 + SH-091;
- Marketplace → Transaction / Order: current checkout source facts only, with Order owning snapshot/lifecycle;
- Marketplace → Booking: service delivery requirements only;
- Marketplace ↔ Digital Goods/Video: source/delivery readiness only, no grant/provider ownership;
- Moderation → Marketplace: SH-103 enforcement envelope;
- Marketplace → Notification: SH-041;
- Privacy → Marketplace: SH-095–097;
- Trust/Healthcare/Moderation → Marketplace: SH-123 owner target validation where needed.

No integration is accepted merely because a test can perform a cross-domain Prisma join.

# Module Hardening Phase

**Phase 5 / Feature 09 is the Marketplace hardening phase.** It covers only Module-relevant production risks:

- Offering lifecycle races;
- stale edits and readiness decisions;
- idempotency/replay;
- event out-of-order handling;
- Search outage/projection rebuild;
- foreign dependency outage fail-closed behavior;
- privacy/retention safety;
- authorization/RLS alignment;
- telemetry data minimization;
- migration/backfill safety;
- query/index performance;
- disabled unresolved feature paths;
- final contract/version freeze.

Marketplace Supply has no provider-adapter hardening because it owns no provider. Provider outage tests are dependency-contract tests verifying that Marketplace fails safely and does not invent a local provider fallback.

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | 01 Marketplace Contracts, Repository Boundary, and Aggregate Validation Foundation; 02 Draft Offering and Kind-Specific Shape; 03 Current Pricing, Taxonomy Attachments, and Presentation Media Context |
| 2 | Public Lifecycle and Marketplace Decisions | 04 Stable Management/Public Queries, Owner Facts, and Local Readiness Decisions; 05 Offering Publication, Pause, Resume, Restriction, Restoration, and Archive |
| 3 | Cross-Module Workflow Integration | 06 Search Projection and Order / Booking / Delivery Contract Proof; 07 Dependency Change Propagation and Moderation Enforcement |
| 4 | Privacy, Audit, Notification, and Operational Integration | 08 Marketplace Privacy Executor, Audit Evidence, Safe Notifications, and Operational Telemetry |
| 5 | Hardening and Production Verification | 09 Marketplace Security, Concurrency, Replay, Backfill, Performance, and Production Hardening |

**Total numbered Marketplace Supply features: 9**

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture standards.
2. Read Canonical Shared Operations.
3. Read CL-03 architecture and build plan.
4. Read Marketplace Supply module architecture and this plan.
5. Read public-interface sections for every dependency touched by the feature.
6. Confirm the prior Marketplace feature exit gate passed.
7. Confirm the linked CL-03 feature/prerequisite state.
8. Check unresolved decisions that affect the feature.
9. Write a concise implementation specification for **only this numbered feature**.
10. Implement only the feature and approved sub-slices.
11. Run root quality checks plus feature-specific tests.
12. Verify the observable workflow and negative/failure paths.
13. Update progress.
14. Update architecture only when a binding decision legitimately changed.
15. Record unresolved risks, disabled paths, and deferred work.

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce:

- **Objective** — exact capability being added.
- **Observable result** — user/admin/consumer behavior that becomes verifiable.
- **Cluster build-plan link** — CL-03 feature/milestone this work supports.
- **Dependencies** — prior Marketplace features, owner Module interfaces, SH operations, providers if any, unresolved rulings.
- **In scope** — exact behavior/data/contracts.
- **Out of scope** — explicit neighboring ownership exclusions.
- **Owned data affected** — Marketplace models/enums/events/projections only.
- **Public contracts** — commands, queries, event or Privacy executor changes.
- **Shared operations consumed** — SH ID, owner, invocation, local policy, prohibited duplicate.
- **Permissions/compliance** — actor, authority, readiness/hold/moderation/privacy gates.
- **Primary workflow** — ordered behavior from entry point to authoritative result.
- **Provider integration** — normally `None; Marketplace Supply owns no provider`; if this changes, architecture must change first.
- **Jobs/events** — names, payload, idempotency, retry, current-state behavior.
- **Idempotency/concurrency** — command key, aggregate lock/version, replay result.
- **Error behavior** — stable categories/reason codes.
- **Tests** — exact unit/integration/contract/concurrency/privacy/E2E requirements.
- **Acceptance criteria** — concrete pass conditions.
- **Documentation updates** — architecture/interface/progress files affected.

Do not generate all feature specifications in advance. The specification is written immediately before that feature is implemented so it uses the current approved architecture and dependency contracts.

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- Feature completed;
- Files added;
- Files changed;
- Database changes;
- Migrations;
- Dependencies added;
- Marketplace public interfaces added/changed;
- Shared operations reused by SH ID;
- Marketplace events/jobs added;
- Provider adapter changes — expected `None` unless architecture changed first;
- Tests added/changed;
- Commands run;
- Manual/contract verification;
- Documentation updated;
- Assumptions;
- Known failures;
- Remaining risks;
- Deferred work;
- Unresolved decisions encountered;
- Disabled paths maintained;
- Exit-gate result.

A completion report may not describe a failed or skipped exit gate as complete.

# Final Quality Check

Before declaring the Marketplace Supply plan implemented, verify:

1. `Offering` lifecycle has exactly one owner: Marketplace Supply.
2. `ProfessionalProfile`, Trust, Healthcare, Payment, Taxonomy, Digital Goods, Video, Media, Search, Order, Hold, Moderation, Privacy, Audit, Notification, and Ops truth were not absorbed.
3. Every shared operation is consumed rather than duplicated.
4. shared mechanism / separate truth boundaries are explicit in code and tests.
5. public Marketplace commands/queries are stable and direct Prisma reads are unnecessary for normal consumers.
6. cross-Module reads/writes use approved public interfaces.
7. Marketplace has no provider adapters or provider truth.
8. Audit, domain events, Search projection, and Ops diagnostics are separate.
9. Privacy orchestration remains Privacy-owned.
10. Search remains rebuildable projection.
11. Marketplace feature sequence remains subordinate to CL-03 Feature 02 → 08 → 11 → 12 → 13 sequencing and prerequisites.
12. every numbered feature has passed tests and its exit gate.
13. U-01/U-13/U-14/U-15/U-16 and Marketplace MA-U items were not silently invented.
14. a coding agent can implement the next feature from context without making an ownership decision on its own.

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


## WA-R067 — Typed moderation execution and normalized receipts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-103 remains the existing cross-cutting execution protocol; no new Shared Operation ID or schema change is authorized. Each instruction carries authorized decision/action ID, case/cycle, typed owner target ID and expected owner revision, approved effect, actor/service authority, purpose/policy/evidence references, semantic effect key and correlation. Owners validate target/action compatibility and current authority before mutation. The following versioned ports name existing owner handlers, not new lifecycle ownership or permission.

| Existing primary target / typed downstream effect | Owner port v1 | Allowed effect and guard |
| --- | --- | --- |
| job, organization | Hiring applyHiringModerationDecision.v1 | Publication suppression/eligible restoration under R047; compliance, lifecycle and all restrictions still apply |
| candidate_profile, with owned current search projection reference | Candidate applyCandidateModerationDecision.v1 | Search-projection suppression/eligible restoration only; current explicit opt-in/readiness required. No application mutation or new Candidate Hold target |
| thread, message | Messaging applyMessagingModerationDecision.v1 | Persistent content restriction/authorized restoration under R054; current membership, sensitivity and all restriction sources still apply |
| media_asset, media_access_grant | Media executeMediaModerationInstruction.v1 | Existing asset freeze, public exposure/grant revocation, evidence preservation and eligible file exposure restoration; source context and safety remain required |
| digital_download_asset, affected owned grant references | Digital Goods applyDigitalModerationDecision.v1 | Disable/restore asset and revoke affected grants; current Order entitlement/Media safety/purchased policy required, no revival of terminal grant |
| course_video_asset, affected owned playback grant references | Video applyVideoModerationDecision.v1 | Disable/restore asset and revoke affected playback grants; current entitlement/safety/provider evidence required |
| review | Review applyReviewModerationDecision.v1 | Existing hide/remove/authorized restoration under R026; restore current eligible accepted revision and adjust original reputation contribution exactly once |
| offering | Marketplace applyOfferingModerationDecision.v1 | Valid moderation restriction/clearance under R035; clearance returns to draft, fresh publish remains separate |

Existing unversioned Media/Digital/Video handler names become aliases of their listed v1 contract and must not create duplicate effects. CandidateSearchProjection, DigitalDownloadGrant and playback-grant references are owner-local downstream effects under existing primary targets, not new ModerationTargetType values. The owner validates their parent/target relationship. Each port returns semantic effect key, source decision/action, target/revision, effect state, safe outcome/retry classification and durable receipt identity. No secret/provider payload or private evidence is returned.

| Local result | Canonical effect state | Required semantics |
| --- | --- | --- |
| accepted/queued | acknowledged | Durable acceptance only; mutation/provider effect not yet proved |
| applied | completed | Exact requested effect durable, resulting owner revision and proof retained |
| restoration applied | restored | New authorized linked restoration completed; original restriction/history untouched |
| already-applied | Original receipt state | Replay exact stored receipt, including pending state; dedupe alone is not completion |
| unsupported/denied/stale conflict | failed with terminal or reevaluate classification | No mutation; conflict requires fresh facts and applicable authorized decision, never silent overwrite |
| known retryable failure | failed with retryable classification | Retry the same semantic effect identity |
| uncertain owner/provider outcome | acknowledged with reconcile_required outcome | Durable unknown-state evidence; reconcile original effect before redispatch, never claim completed/restored |

Multi-owner work retains per-step receipts; Report/Case action_taken requires every required successful effect under R058. Search refresh and provider request acknowledgments do not prove de-indexing or revocation. Restoration is a new effect linked to the original, not an edit of the original receipt. Partial bulk revocation remains incomplete until its target inventory is accounted.

Order/payout reusable stops use Hold's registered typed action/command boundary per CL-09-R007/R059, not direct Moderation writes to Order/Payment. Release triggers current owner reevaluation, never financial execution, content restoration, service completion or review eligibility. Candidate Hold types absent from the typed Hold schema remain disabled. CL-01 has no generic moderation executor under R063: only separately named authorized security/entitlement/Hold/lifecycle commands may act. Enumeration of user or profile targets is not permission. Other target/effect families not listed here must have an existing explicit owner registration before activation; this scoped matrix does not invent their semantics or silently delete their historical proposals. Unsupported combinations return unsupported, with no fallback mutation.

R026 already settles explicitly authorized Review restoration; old unresolved base text is superseded. R042 settles Booking Professional reports, authorized support adjudication and Customer contest, with no automatic consequence; R052 completed/no_show aliases are performance-report facts, not final financial/review truth. These are existing rulings, not new product decisions. Contract adapters/fixtures, typed receipt persistence and coordinated migrations remain implementation qualification.


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `marketplace_supply` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`updateOfferingCore / requestOfferingPublication`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration — implementation obligations

Implement the owner’s WA-R070 descriptor/enumerator and assignment receipt before dependent AI/Search/merge work. Test stale source/assignment tokens, forbidden fields/purposes, cursor replay/expiry/interruption and atomic receipt retry/conflict. Bind serializer limits and applicable sensitivity/policy versions; registration is not vendor qualification.


## WA-R075 — Typed Hold action applicability and source readiness

This owner adopts its source/consumer obligations in `context/reconciliation/hold-action-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.
