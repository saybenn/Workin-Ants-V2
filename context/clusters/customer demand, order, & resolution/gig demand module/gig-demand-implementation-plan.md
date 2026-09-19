# Gig Demand Implementation Plan

> **Module ID:** `gig_demand`  
> **Module name:** Gig / Demand Module  
> **Primary Cluster:** `CL-04 — Customer Demand, Order & Resolution`  
> **Plan status:** Sequential Module implementation plan subordinate to the CL-04 build plan. It may refine work inside Gig / Demand but must not reorder or redefine Cluster ownership.  
> **Architecture dependency:** `gig_demand/module-architecture.md`

**Shared Operation status (CL-04-R015/R016):** exact SH IDs/names resolve to the canonical registry. SH-046 publication/outbox is Confirmed. SH-003 `queryOwnerFacts` and SH-015 `returnDecisionResult` remain Proposed ruling: use owner-specific fact/decision DTOs, not binding APIs dependent on those proposals. SH-054, SH-073, and SH-111, wherever referenced, remain Proposed ruling and conditional on separate approval. All other referenced registered operations retain their registry status and owner.

---

## Core Principle

Implement Gig / Demand through narrow, observable, owner-correct slices:

```text
public/observable behavior
→ validated command or query
→ Gig-owned domain policy
→ authoritative Gig-domain write/read
→ canonical shared-operation calls
→ transactional event/outbox effects
→ owner public-interface calls
→ tests
→ exit gate
```

The Module is complete only when the customer-demand source records, Professional-response behavior, accepted-work handoff, cross-Module contracts, privacy behavior, asynchronous maintenance, and concurrency rules agree.

This plan does not create a second CL-04 roadmap. The Cluster build plan remains the controlling sequence. The first five Module features refine CL-04 Features 01–03 and the Gig-to-Order boundary. Later features prove and harden Gig / Demand participation in CL-04 Features 13–14.

---

## Build Rules

1. Follow root Workin Ants architecture, code standards, the Canonical Shared Operations Registry, CL-04 architecture, CL-04 build plan, and `gig_demand/module-architecture.md`.
2. Gig / Demand owns only `Gig`, `GigResponse`, `GigAssignment`, their lifecycle policy, and the Gig-context meaning of `GigTag` and `GigMedia`.
3. Consume other Modules through approved public interfaces. A Prisma relation does not authorize direct cross-Module repository access.
4. Reuse canonical Shared Operations exactly by their canonical names. Do not create Module-local aliases that become competing infrastructure.
5. Every mutation validates input, trusted actor context, authority, current source version/state, and required external gates server-side.
6. Every retryable commercial mutation uses SH-044 `executeIdempotentCommand` or the approved platform idempotency mechanism.
7. Every concurrency-sensitive lifecycle transition uses shared database concurrency primitives. Never use process-memory locks for database-owned truth.
8. SH-053 `transitionLifecycleState` may provide state-machine plumbing, but Gig / Demand retains the legal transition graph and reason semantics.
9. External effects happen after authoritative Gig-domain state commits, preferably through SH-046 `publishDomainEvent` and a transactional outbox.
10. Search writes occur only through SH-091 `requestSearchProjectionRefresh`; Gig / Demand never writes `SearchUpsertEvent` directly and never instantiates a Typesense client.
11. Media validation/storage/access remains Media / File Access truth. Gig / Demand creates only contextual `GigMedia` relationships after Media says the asset is eligible.
12. Professional readiness comes from SH-016 `evaluateProfessionalReadiness`; Gig / Demand must not reconstruct verification, healthcare, KYC, tax, payout, entitlement, or hold truth from foreign tables.
13. Notification delivery and Messaging lifecycle remain external. Gig / Demand supplies business meaning, context, and recipients; their owners persist and deliver communication truth.
14. Privacy / Data Erasure owns request/job/orchestration truth. Gig / Demand only enumerates its data and executes Privacy-defined instructions against its own records.
15. No Stripe, tax, verification-provider, storage-provider, email/SMS/push, or Typesense provider client belongs in this Module.
16. `invite_only` remains unsupported until an authoritative audience/invitation model is approved.
17. Single-award MVP is confirmed. Exact lifecycle matrices, physical assignment enforcement, historical CustomerProfile migration, and destructive retention rules remain gates; coding agents must not choose them.
18. Every numbered feature ends with automated tests, contract/workflow verification, documentation review, and a concrete exit gate.
19. A later hardening feature may strengthen already-built behavior; it must not become a catch-all for missing business logic from an earlier feature.

---

## Preconditions

### Hard platform prerequisites

The following must exist before the first production mutation that depends on them:

- Prisma/Postgres migration and transaction workflow;
- strict TypeScript and server-side validation conventions;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- shared database concurrency support (SH-051 `acquireAggregateLock` and/or SH-052 `withOptimisticConcurrency`);
- SH-053 `transitionLifecycleState` plumbing if adopted;
- SH-046 `publishDomainEvent` transactional outbox/event envelope;
- SH-045 `deduplicateDomainEvent` inbox support for event consumers;
- shared queue worker shell (SH-047 `enqueueReliableJob`, SH-048 `executeRetryWithBackoff`);
- request/correlation context and structured logging;
- SH-029 `appendAuditEvent`.

### Hard Module-interface prerequisites by production slice

| Dependency owner | Interface required | Needed by | May initially be stubbed? |
| --- | --- | --- | --- |
| Customer / Buyer Profile | SH-004 `resolveCustomerActor` and minimal CustomerProfile facts | customer draft/publication/acceptance | Yes for isolated domain tests; no for production customer writes |
| Role / Authority | SH-002 `authorizeResourceAction` | every protected command/read | No for production |
| Taxonomy & Classification | SH-023 `validateTaxonomyAssignment`, SH-022 `resolveTaxonomyRequirements` | publication/classification | Yes for local tests; no for production publication |
| Professional Eligibility | SH-016 `evaluateProfessionalReadiness` | response submit and acceptance | Yes for local tests; no for production response/acceptance |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | publish/accept and other blocked actions | Yes for local tests; no where policy requires the gate |
| Media / File Access | validated Media reference contract; SH-090 `attachValidatedMedia` preconditions; signed-access contract as needed | Gig media | Yes for drafts without media; no for media-enabled production |
| Location Safety | SH-028 `applyFuzzyPublicLocation` where public location is projected | public Gig output/search source | Yes if public location is omitted; no if public location is exposed |
| Search / Public Visibility | SH-091 `requestSearchProjectionRefresh` | public source changes | Yes behind a test double; no for production public discovery |
| Messaging | SH-113 `ensureContextThread` | approved Gig/response/assignment conversation points | Yes until communication slice |
| Notification | SH-041 `requestNotification` | response/acceptance/lifecycle alerts | Yes until communication slice |
| Transaction / Order | `createOrderFromGigAssignment` or its approved command plus source DTO contract | assignment-to-Order handoff | Yes until Cluster Order feature exists |
| Privacy / Data Erasure | privacy target protocol | production privacy fulfillment | Yes until hardening; no before privacy launch |
| Content Moderation & Legal Notice | SH-103 `executeModerationDecision` protocol | moderation enforcement | Yes until cross-cluster integration |

### Architecture decision gates

The following are explicit preconditions, not implementation details:

1. **Before Feature 01 production migration:** decide how required CustomerProfile buyer identity applies to new writes and what `posterUserId` means after migration.
2. **Before Feature 03 enables response revision beyond a minimal safe subset:** approve the response transition/revision matrix.
3. **Before Feature 04:** apply confirmed single-award MVP semantics; obtain the remaining Gig/Response/Assignment transition and database-enforcement approvals.
4. **Before Feature 06 automates completion/dispute synchronization:** approve which Order/Dispute outcomes cause which GigAssignment/Gig transitions.
5. **Before Feature 07 destructive erasure:** approve retention rules for converted/accepted commercial terms and historical actor references.
6. **Before `invite_only` can ship:** approve a source of invitation/audience truth and its access interface.

A provider choice is not a prerequisite for this Module because Gig / Demand owns no direct provider integration.

---

# Phase 1 — Demand Source Foundation

## 01 Gig Draft Aggregate and Owner Contracts

### Objective

Create the minimum authoritative Gig draft lifecycle and owner-facing read contracts without crossing unresolved publication, audience, or acceptance decisions.

### Observable Result

An authenticated customer actor can create a Gig draft, retrieve it, update supported draft fields, and list their own Gigs. Unauthorized actors receive stable denial results. The Module exposes minimum owner facts without exposing its repository.

### Cluster Build-Plan Link

Supports **CL-04 Feature 01 — Gig Draft and Publication Boundary**, specifically the draft/read half of that Cluster feature.

### Dependencies

- root Prisma/migration conventions;
- SH-001 `resolveAuthenticatedActor`;
- SH-004 `resolveCustomerActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand` for retryable create;
- request/correlation context;
- approved CustomerProfile migration ruling for production writes.

### In Scope

- command and validation schemas for draft creation/update;
- `createGigDraft`;
- `updateGigDraft` for draft-safe fields;
- `getGig` authorized source read;
- `listCustomerGigs`;
- `queryGigOwnerFacts` or equivalent owner-specific minimal fact DTO; SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) is proposed future normalization, not a canonical prerequisite;
- repository methods that access only Gig / Demand-owned tables plus local join relations;
- source-version/concurrency result convention using current `updatedAt` if no explicit version column is approved;
- initial domain error/reason-code namespace;
- customer draft UI only if the application surface is part of the current Cluster implementation slice.

### Out of Scope

- public publication;
- `invite_only` behavior;
- Professional responses;
- acceptance and `GigAssignment`;
- Search indexing;
- media upload/storage mechanics;
- location fuzzing;
- Order creation/payment;
- generic authentication or RBAC helpers.

**Actor prerequisite (CL-04-R007):** enforce CustomerProfile as semantic buyer identity for new records; Review authors resolve from the Order buyer and Dispute opener identity is typed. Historical backfill and final Prisma representation remain separate approval gates. No schema is changed in this reconciliation.

### Module-Owned Data

- `Gig`;
- `GigStatus.draft`;
- local validation schemas/DTOs;
- no new lifecycle ledger is introduced unless separately approved.

### Public Interfaces

Introduced or stabilized:

- `createGigDraft(command): GigCommandResult`;
- `updateGigDraft(command): GigCommandResult`;
- `getGig(query): GigSourceView`;
- `listCustomerGigs(query): GigSummaryPage`;
- `queryGigOwnerFacts(query): GigOwnerFacts` — minimal relationship/version/status facts for other owners that need them.

The public contract must not expose Prisma models as its API shape.

### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | every customer command | Gig decides the attempted action | `gigAuth.ts`, `requireGigUser.ts`, `currentGigUser()` |
| SH-004 `resolveCustomerActor` | Customer / Buyer Profile | before customer-owned write | Gig decides that the action requires buyer identity | `getGigCustomer.ts`, local CustomerProfile lookup repository |
| SH-002 `authorizeResourceAction` | Role / Authority | create/update/read where protected | Gig supplies owner/status relationship facts and action key | `gigPermissions.ts`, `gigRbac.ts` |
| SH-044 `executeIdempotentCommand` | platform application infrastructure | draft creation | semantic key/fingerprint/replay behavior is Gig-specific | `gigIdempotency.ts` |
| SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) | source-owner pattern | exported owner-facts query | DTO is Gig-specific | universal cross-domain repository |
| SH-032 `createRequestContext` / SH-033 `writeStructuredLog` | platform/Observability | request execution | safe Gig dimensions only | Module-local logger/request-ID stack |

### Domain Logic

- A Gig draft represents customer demand, not an Offering or Job.
- Customer ownership must be derived from trusted CustomerProfile/User relationships, not a client assertion.
- Draft writes may set only fields approved as draft-editable.
- `status` is not accepted from the client as an arbitrary write field.
- Budget values, if supplied, must use integer cents and a supported currency representation; final publish-time budget rules remain Feature 02 policy.
- The Module must preserve `posterUserId`/`customerProfileId` according to the approved migration ruling. It must not invent dual-source ownership semantics.
- A deleted/archived CustomerProfile does not automatically delete Gig truth; exact policy is owner-contract dependent and must be handled explicitly.

### Authorization / Compliance

- authenticated actor required;
- active/resolved CustomerProfile is required semantic identity for new buyer-domain writes under CL-04-R007; historical backfill and physical schema changes remain separately gated;
- Role / Authority performs permission interpretation;
- only the controlling customer actor may update a normal Gig draft;
- admin/support mutation requires an explicitly approved action and must not be inferred from generic platform role alone;
- no Professional readiness gate is needed to create customer demand.

### Database / Transaction Behavior

- `createGigDraft` writes one `Gig` in a transaction compatible with canonical idempotency result storage;
- no client-controlled status mutation;
- update should use expected source version/`updatedAt` comparison where shared optimistic concurrency is available;
- preserve existing indexes for poster/customer/status access; add indexes only after query evidence justifies them;
- no destructive CustomerProfile nullability migration until the architecture ruling and backfill plan are accepted.

### Events / Jobs

- a `GigCreated` domain event may be emitted after commit if downstream consumers need it; payload is minimized and versioned;
- draft-only edits should emit source-change events only when a consumer has a real need; do not create event noise by default;
- no background job is required.

### Provider Integration

None. This feature must introduce no provider client or provider-native type.

### UI / Admin Surface

If UI is in the current application slice:

- customer Gig draft create/edit/read page;
- clear validation, forbidden, stale-write, and unsupported-state feedback;
- do not expose `invite_only` as a usable option yet unless the UI labels it disabled/unavailable.

No generic admin dashboard is introduced here.

### Failure Behavior

- unauthenticated → authentication-required result;
- no eligible CustomerProfile → stable buyer-context denial/unavailable result;
- wrong owner → forbidden;
- invalid field/budget/date → validation error with field-level reason;
- stale expected version → conflict with current version metadata;
- duplicate idempotent create → replay original result;
- architecture-gated CustomerProfile migration not accepted → production write remains blocked at that decision, not silently downgraded to User-only ownership.

### Tests

- Gig draft domain-validation unit tests;
- command validation tests;
- customer owner positive/negative authorization tests;
- CustomerProfile resolution contract tests;
- idempotent draft-create replay test;
- stale-update concurrency test if expected-version support exists;
- repository integration test proving only Gig-domain state is mutated;
- public DTO contract test proving Prisma internals are not leaked;
- UI tests for draft validation/ownership if UI ships.

### Documentation Updates

Update `gig_demand/module-architecture.md` only if implementation settles an approved CustomerProfile ownership/migration ruling or changes the public owner-facts contract. Update progress tracking after completion. Record any unresolved schema conflict; do not amend architecture merely because code was written.

### Acceptance Criteria

- a valid customer actor can create exactly one draft effect per idempotency key;
- the same customer can retrieve/update that draft through Gig-owned interfaces;
- another customer/professional cannot mutate it;
- source fields and status remain Gig-owned;
- no cross-Module repository is imported to resolve authority or CustomerProfile truth;
- no local auth/authz infrastructure exists.

### Exit Gate

Before Feature 02:

- typecheck/lint/format pass;
- Gig draft unit and DB integration tests pass;
- authorization/CustomerProfile contract tests pass;
- idempotency replay passes;
- the production CustomerProfile field strategy is explicitly documented as approved or remains a named blocker;
- no publication/search/media behavior has leaked into this feature.

---

## 02 Gig Publication, Classification, Media, Location, and Search Boundary

### Objective

Allow a valid customer Gig to become publicly open for the **approved visibility paths only**, while consuming taxonomy, media, location, hold, and search capabilities without importing their truth.

### Observable Result

A customer can classify and prepare a Gig, attach eligible MediaAssets, and publish an approved public Gig. Public output contains only allowed location/media data. Search projection is requested after the Gig commit, and Search failure does not roll back Gig truth. `invite_only` remains explicitly unsupported.

### Cluster Build-Plan Link

Completes the Gig-owned scope of **CL-04 Feature 01 — Gig Draft and Publication Boundary**.

### Dependencies

- Feature 01 exit gate;
- SH-023 `validateTaxonomyAssignment`;
- SH-022 `resolveTaxonomyRequirements`;
- Media readiness/target-reference contract and SH-090 `attachValidatedMedia` pattern;
- SH-028 `applyFuzzyPublicLocation` if public location is present;
- SH-011 `evaluateComplianceHold`;
- SH-091 `requestSearchProjectionRefresh`;
- SH-046 `publishDomainEvent` transactional outbox;
- SH-029 `appendAuditEvent` for publish/cancel policy as required;
- approved initial Gig transition subset for draft → open and supported pause/cancel behavior.

### In Scope

- `setGigClassification`;
- `setGigTags`;
- `attachGigMedia` / `detachGigMedia` using validated Media references;
- `evaluateGigPublishReadiness` as Gig-local composition of owner decisions;
- `publishGig` for approved visibility modes;
- `buildGigSearchSourceProjection` compatible with canonical SH-094 `buildSourceProjection` pattern;
- Search projection request after authoritative source change;
- public-safe location transformation/request;
- explicit unsupported result for `invite_only`;
- publish-time validation of close/due/budget relationships that are architecturally approved.

### Out of Scope

- Typesense client, schema, ranking, indexing worker, or `SearchUpsertEvent` repository;
- Media upload bytes, MIME detection, malware scanning, metadata scrubbing, storage keys, or signed URLs;
- geocoding/fuzzing algorithm implementation;
- Professional response eligibility;
- Order/payment;
- invitation/audience schema;
- a universal public-readiness engine.

### Module-Owned Data

- `Gig` classification/status/visibility fields;
- `GigTag` contextual association/provenance fields;
- `GigMedia` contextual role/sort-order fields;
- no MediaAsset or TaxonomyTag truth.

### Public Interfaces

- `setGigClassification`;
- `setGigTags`;
- `attachGigMedia` / `detachGigMedia`;
- `evaluateGigPublishReadiness`;
- `publishGig`;
- `buildGigSearchSourceProjection` or a public projection query consumed by Search;
- `getPublicGig` only if Gig / Demand owns a source-view endpoint; public discovery query itself remains Search-owned.

### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-023 `validateTaxonomyAssignment` | Taxonomy & Classification | classification set/publish | whether classification is required before open | `gigCategoryValidator.ts`, local taxonomy tables |
| SH-022 `resolveTaxonomyRequirements` | Taxonomy & Classification | publish readiness | how returned triggers affect Gig publication/context | `highRiskGigMap.ts` |
| SH-123 `validateOwnedTargetReference` | target owner | Media/Taxonomy reference validation | which relationship is permitted | direct cross-domain Prisma lookup |
| SH-090 `attachValidatedMedia` | contextual Module + Media contract | GigMedia creation | Gig role/sort semantics | `gigUploadService.ts`, file scanner |
| SH-028 `applyFuzzyPublicLocation` | Location Safety | public projection | which approved public location fields Gig exposes | `gigLocationMask.ts`, random coordinate jitter |
| SH-011 `evaluateComplianceHold` | Admin Review / Compliance Hold | publish gate | which hold scopes block Gig publication | `isGigBlocked` boolean/helper |
| SH-024 `evaluatePublicReadiness` | shared decision contract | publish/projection | Gig's own source-status/visibility policy | universal compliance composer |
| SH-091 `requestSearchProjectionRefresh` | Search / Public Visibility | after commit | reason/action/source version | `gigTypesenseService.ts`, direct SearchUpsertEvent insert |
| SH-094 `buildSourceProjection` | Gig / Demand using shared pattern | Search source DTO | allowlisted Gig fields | Search reconstructing private Gig rows |
| SH-046 `publishDomainEvent` | platform event infrastructure | after publish/update/visibility change | event names/payloads | fire-and-forget event emitter |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | publish/cancel where required | Gig action metadata | `gigAuditLog` table |

### Domain Logic

- Taxonomy validation is external truth; Gig / Demand decides whether valid classification is sufficient for `open`.
- `GigTag` records contextual attachment and provenance but does not redefine TaxonomyTag.
- Only MediaAssets confirmed eligible by Media may be attached. A Gig command cannot change a MediaAsset to ready.
- Exact/private location must never be placed into public/search projection by default.
- `visibility=public` plus Gig-local status policy is necessary but not sufficient for search projection; external moderation/privacy/hold readiness also applies through owner decisions.
- `private` Gigs are not sent to public Search. Exact semantics for how private Gigs are accessed must be explicit in owner authorization policy.
- `invite_only` returns `unsupported`/`feature_disabled` until audience truth exists.
- Publish status transition must use the approved transition matrix. If only `draft → open` is approved initially, no additional transition is inferred.

### Authorization / Compliance

- controlling CustomerProfile owns publish/edit actions;
- publication evaluates applicable holds;
- high-risk classification triggers are obtained from Taxonomy/Trust/Professional-readiness owners and must not be hardcoded locally;
- public output must use Location Safety-approved data;
- media attachment requires contextual authority plus Media readiness;
- admin/support override behavior must be separately authorized and audited.

### Database / Transaction Behavior

- classification/tag/media writes are transactional where they form one semantic update;
- Gig status transition and outbox event are committed atomically;
- Search request itself may be asynchronously consumed after commit;
- composite keys on `GigTag`/`GigMedia` prevent duplicate associations;
- do not delete a MediaAsset when a `GigMedia` row is detached;
- source version/`updatedAt` must advance on authoritative Gig change.

### Events / Jobs

Potential owner events, emitted only when meaningful:

- `GigPublished`;
- `GigUpdated`;
- `GigVisibilityChanged`;
- `GigClassificationChanged`.

Search projection requests are downstream effects, not Gig truth. Failed Search processing uses Search/queue retries and operational telemetry.

### Provider Integration

None. Typesense, object storage, and geocoder providers remain behind their owning Modules.

### UI / Admin Surface

- draft classification/tag/media controls;
- publish action with owner-provided denial reasons;
- public/private selector only for approved modes;
- `invite_only` disabled or omitted;
- public preview must use the same privacy-safe projection contract that Search may consume.

### Failure Behavior

- invalid/stale taxonomy → reject with taxonomy reason;
- Media not ready/eligible → reject attachment or publish as policy requires without changing Media state;
- hold denial → remain draft/previous state;
- location projection unavailable when required → fail closed for public location exposure or omit location only if approved policy allows;
- Search outage → source publication remains committed and projection retry is visible operationally;
- unsupported visibility → stable `unsupported_visibility` result.

### Tests

- taxonomy contract tests, including domain/category mismatch;
- tag uniqueness/provenance tests;
- Media ready/not-ready contract tests;
- proof that file safety code is not imported into Gig / Demand;
- Location Safety serialization test proving exact data is absent from public DTO;
- hold allow/deny tests;
- publication state-transition tests for approved subset;
- Search request emitted only after commit;
- Search failure does not roll back Gig;
- private Gig does not request public projection;
- `invite_only` is rejected/disabled;
- public projection allowlist snapshot/contract test.

### Documentation Updates

Document any approved publish matrix, location exposure rule, or supported visibility change in Module architecture. Update Search source DTO version documentation if its contract changes.

### Acceptance Criteria

- valid public Gig can be opened through Gig-owned command;
- taxonomy/media/location/hold truth is consumed from owners;
- public projection is minimized and reproducible;
- Search is requested asynchronously through its public interface;
- no exact location, raw Media internals, or foreign compliance data leaks into public projection;
- `invite_only` cannot accidentally ship as a permissive mode.

### Exit Gate

- CL-04 Feature 01 Gig scope is demonstrably complete for approved visibility paths;
- all publication dependency contract tests pass;
- no direct Typesense/storage/geocoder code exists in the Module;
- outbox-after-commit behavior is verified;
- public privacy/location tests pass;
- any unresolved visibility/lifecycle path remains explicitly disabled.

---

# Phase 2 — Professional Response

## 03 Professional Gig Response Lifecycle

### Objective

Implement the one-Professional/one-Gig proposal lifecycle through the safe, approved transition subset, gated by authoritative Professional readiness.

### Observable Result

An eligible ProfessionalProfile can submit one response to an eligible Gig, retrieve that response, and perform approved responder actions. The customer can list/view and perform approved customer-side response actions. Duplicate submission and ineligible Professional behavior fail deterministically.

### Cluster Build-Plan Link

Implements **CL-04 Feature 02 — Professional Gig Response**.

### Dependencies

- Features 01–02;
- SH-016 `evaluateProfessionalReadiness`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-046 `publishDomainEvent`;
- SH-041 `requestNotification`;
- approved response transition/revision subset.

### In Scope

- `submitGigResponse`;
- `getProfessionalGigResponse`;
- `listGigResponsesForPoster`;
- `markGigResponseViewed` if approved;
- `shortlistGigResponse` if approved;
- `rejectGigResponse` if approved;
- `withdrawGigResponse` if approved;
- `reviseGigResponse` only for explicitly approved editable states;
- response-specific reason codes and DTOs;
- notification requests after committed response events.

### Out of Scope

- response acceptance;
- assignment creation;
- direct VerificationCheck/KYC/healthcare/entitlement reads;
- Messaging implementation;
- Order/payment;
- revision history/version model unless separately approved.

### Module-Owned Data

- `GigResponse`;
- `GigResponseStatus`;
- current uniqueness constraint `@@unique([gigId, professionalProfileId])`;
- no separate application/hiring state.

### Public Interfaces

- `submitGigResponse`;
- `reviseGigResponse` — only if its state policy is approved;
- `withdrawGigResponse`;
- `markGigResponseViewed`;
- `shortlistGigResponse`;
- `rejectGigResponse`;
- `getProfessionalGigResponse`;
- `listGigResponsesForPoster`;
- `queryGigResponseOwnerFacts` if another owner needs minimal relationship facts.

### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | all response actions | whether actor acts as Professional or customer | responder-session helper |
| SH-002 `authorizeResourceAction` | Role / Authority | submit/read/mutate | responder/customer relationship facts | `responsePermissions.ts` |
| SH-016 `evaluateProfessionalReadiness` | Professional Eligibility | before submit and other policy-defined commercial actions | action key=`respond_to_gig`, Gig context | `professionalCanRespond`, raw verification composer |
| SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite) | shared contract | readiness/denial translation | Gig-specific safe reason mapping | one-off boolean `canRespond` API |
| SH-044 `executeIdempotentCommand` | platform | submission and retryable transitions | semantic command identity | response dedupe service |
| SH-053 `transitionLifecycleState` | shared plumbing | state changes | exact response graph | generic status setter |
| SH-046 `publishDomainEvent` | platform outbox | after committed response changes | event payload | fire-and-forget emitter |
| SH-041 `requestNotification` | Notification | response submitted/viewed/accepted/rejected as applicable | event meaning and intended recipients | `gigEmailService`, `responsePush.ts` |

### Domain Logic

- only an eligible `ProfessionalProfile` commercially responds; base User alone is insufficient;
- Gig must be in an approved response-accepting status;
- one ProfessionalProfile has at most one `GigResponse` per Gig;
- a revision, when allowed, updates the same response rather than creating another proposal row;
- proposed amount uses integer cents and canonical currency validation;
- readiness denial must expose safe reason codes/evidence references only, not raw background-check/financial details;
- `GigResponse` is not a `JobApplication` and may not reuse candidate/hiring pipeline code.

### Authorization / Compliance

- Professional may submit/update/withdraw only their response through trusted ProfessionalProfile ownership;
- controlling CustomerProfile may list/view/shortlist/reject according to approved response policy;
- Professional readiness is evaluated by Professional Eligibility;
- high-risk verification is therefore consumed through readiness, not implemented locally;
- active holds may already be composed by Professional Eligibility; Gig / Demand should not double-build the same readiness logic. If a Gig-local hold gate is required separately, use SH-011 `evaluateComplianceHold` explicitly.

### Database / Transaction Behavior

- `submitGigResponse` uses DB uniqueness plus idempotency; application checks alone are insufficient;
- duplicate concurrent insert maps the unique violation to a stable existing/conflict result;
- status transition and outbox write are atomic;
- expected-version protection should reject stale simultaneous customer/professional transitions where relevant;
- no assignment row is created in this feature.

### Events / Jobs

Potential events:

- `GigResponseSubmitted`;
- `GigResponseViewed`;
- `GigResponseShortlisted`;
- `GigResponseRejected`;
- `GigResponseWithdrawn`;
- `GigResponseRevised` only if revision is approved and materially observable.

Notification requests follow committed source events. No Module-owned scheduled job is required.

### Provider Integration

None.

### UI / Admin Surface

If UI ships:

- Professional response form and own-response status view;
- customer response list/detail/actions;
- safe readiness-denial/remediation message;
- no hiring terminology such as “application” or “candidate pipeline.”

### Failure Behavior

- Gig not open/eligible → state conflict;
- Professional readiness denied → decision denial with safe reason;
- duplicate response → idempotent replay or deterministic already-exists conflict according to command key semantics;
- stale response status → conflict;
- unauthorized customer/professional → forbidden;
- Notification unavailable → response truth remains committed; Notification retries independently;
- revision requested in an unresolved/unapproved state → unsupported transition, not guessed behavior.

### Tests

- Professional readiness allow/deny/unavailable contract tests;
- one-response-per-Gig DB uniqueness test;
- concurrent duplicate submission test;
- idempotent retry test;
- allowed/forbidden response transition matrix tests for approved subset;
- Professional ownership tests;
- customer control tests;
- safe reason-code/redaction test;
- notification emitted after commit only;
- test proving no raw verification/payment repository is used;
- UI workflow tests if UI is included.

### Documentation Updates

If response revision/transition rules are approved during implementation, update Module architecture before coding the affected transition. Do not infer the matrix from enum ordering.

### Acceptance Criteria

- eligible Professional submits exactly one proposal row per Gig;
- ineligible Professional cannot create a response;
- customer/professional actions are correctly scoped;
- retries and concurrent duplicates do not duplicate response/event effects;
- no neighboring compliance or hiring truth is imported.

### Exit Gate

- all response domain/authorization/readiness/idempotency tests pass;
- DB uniqueness is verified in an integration test;
- approved response transitions are exhaustively tested, and unapproved transitions remain blocked;
- Notification failure isolation is proven;
- CL-04 Feature 02 can be marked complete for Gig / Demand.

---

# Phase 3 — Accepted Work and Order Boundary

## 04 Atomic Response Acceptance and GigAssignment

### Objective

Turn an accepted response into authoritative `GigAssignment` truth exactly once under the approved assignment-cardinality and lifecycle rules, without creating Order or payment truth.

### Observable Result

The controlling customer can accept an eligible response. Concurrent or retried acceptance produces only the number of assignments permitted by the approved architecture, with stable replay/conflict behavior. An accepted assignment is independently retrievable.

### Cluster Build-Plan Link

Implements the core of **CL-04 Feature 03 — Atomic Response Acceptance and GigAssignment**.

### Dependencies

- Features 01–03;
- confirmed single-award MVP invariant; remaining acceptance transitions and physical enforcement must be approved;
- **hard architecture gate:** Gig, response, and assignment transition matrices approved for acceptance path;
- approved CustomerProfile buyer-reference strategy;
- SH-016 `evaluateProfessionalReadiness` recheck;
- SH-011 `evaluateComplianceHold` if the acceptance action has an independent hold gate;
- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock` or approved SH-052 `withOptimisticConcurrency` strategy;
- SH-053 `transitionLifecycleState`;
- SH-046 `publishDomainEvent`;
- SH-029 `appendAuditEvent`.

### In Scope

- `acceptGigResponse`;
- atomic acceptance policy;
- creation of `GigAssignment` using agreed commercial terms;
- response accepted transition;
- Gig status transition only as approved;
- `getGigAssignment`;
- `listProfessionalGigAssignments`;
- stable replay result;
- required DB constraint migration if the approved cardinality cannot be enforced by the current schema.

### Out of Scope

- Order creation or Order status;
- Stripe/payment;
- payout;
- Dispute creation/adjudication;
- automatic assignment completion based on Order until synchronization rules are approved;
- custom lock/idempotency framework;
- “first writer wins” behavior not explicitly approved.

### Module-Owned Data

- `GigResponse.status` acceptance transition;
- `GigAssignment`;
- `GigAssignmentStatus`;
- approved `Gig.status` acceptance-related transition;
- any Gig-domain event/outbox records, but not generic AuditEvent truth.

### Public Interfaces

- `acceptGigResponse`;
- `getGigAssignment`;
- `listProfessionalGigAssignments`;
- `queryGigAssignmentOwnerFacts`;
- checkout-source interface is introduced in Feature 05 to keep transaction boundary independently reviewable.

### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-044 `executeIdempotentCommand` | platform | whole acceptance command | key/fingerprint and replay result | `assignmentDeduper.ts` |
| SH-051 `acquireAggregateLock` | shared persistence | lock `gig:{gigId}` or approved equivalent | which actions conflict | `acceptanceMutex.ts`, Redis/in-memory lock invented locally |
| SH-052 `withOptimisticConcurrency` | shared persistence | expected response/Gig version as defense | stale behavior | local CAS helper |
| SH-053 `transitionLifecycleState` | shared mechanism | response/Gig/assignment status updates | owner transition graph | generic “setStatus” |
| SH-016 `evaluateProfessionalReadiness` | Professional Eligibility | fresh pre-acceptance gate | action=`respond_to_gig` or approved acceptance action | raw readiness composer |
| SH-011 `evaluateComplianceHold` | Hold owner | acceptance if independently required | Gig/actor target mapping | local blocked flag |
| SH-046 `publishDomainEvent` | platform | assignment-ready/accepted facts | payload and emission condition | event emitter bypassing outbox |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | acceptance proof when policy requires | safe relationship/action metadata | local audit table |

### Domain Logic

Within one serialized acceptance boundary:

1. claim the command idempotency key;
2. resolve authenticated actor and controlling CustomerProfile;
3. authorize `gig.response.accept`;
4. load current Gig and response in the owning repository;
5. verify response belongs to Gig and is in an acceptable state;
6. verify Gig is in an acceptance-eligible state;
7. fresh-check Professional readiness;
8. evaluate any independent hold gate;
9. enforce approved assignment cardinality;
10. freeze assignment-local agreed title/description/price/currency/timing fields required by the schema;
11. transition response to `accepted`;
12. create or replay the authoritative `GigAssignment`;
13. transition Gig only as approved;
14. persist outbox event in the same transaction;
15. return the same assignment result on retry.

**Confirmed CL-04-R002:** MVP is single-award and competing acceptance commands serialize. **Still proposed:** creating `GigAssignment.status=accepted` directly and leaving `proposed` unsupported; the acceptance transition must receive its separate lifecycle approval.

### Authorization / Compliance

- only the controlling CustomerProfile may accept under normal product flow;
- Professional readiness must be fresh enough for acceptance according to its owner contract;
- TrustBadge is never used as substitute readiness truth;
- admin/support acceptance override, if ever permitted, requires an explicit Role / Authority action and Audit event;
- an applicable ComplianceHold blocks acceptance without creating a local block field.

### Database / Transaction Behavior

- use a database transaction around acceptance state, assignment creation, lifecycle event/outbox, and idempotency completion;
- lock key centers on Gig aggregate because competing responses race for the same accepted-work capacity;
- enforce the confirmed single-award MVP rule and serialize acceptance; carry any selected physical DB invariant through a separately approved migration without choosing its design here;
- existing `gigResponseId @unique` already prevents one response from backing multiple assignments;
- current absence of `gigId` uniqueness must be treated as an architecture/schema gap, not silently ignored;
- map serialization/unique conflicts to stable domain conflict results.

### Events / Jobs

Emit after authoritative transaction via outbox:

- `GigResponseAccepted`;
- `GigAssignmentAccepted` or `GigAssignmentCreated` according to event vocabulary;
- `GigAssigned` only if the approved Gig transition makes that fact true.

No Order command executes inside the same DB transaction; cross-Module handoff is Feature 05.

### Provider Integration

None.

### UI / Admin Surface

- customer acceptance action with confirmation if product design requires;
- response/assignment status visible to customer and Professional;
- conflict state when another response won under single-award semantics;
- no payment-success UI because payment does not exist here.

### Failure Behavior

- two concurrent accepted responses → exactly approved cardinality succeeds; loser gets stable conflict;
- Professional readiness changed → deny before writes;
- stale response/Gig version → conflict;
- duplicate same idempotency key → replay same assignment;
- same key with different fingerprint → idempotency conflict;
- outbox persistence failure → whole transaction rolls back;
- downstream systems unavailable → no effect on assignment transaction because no synchronous downstream owner mutation is required here.

### Tests

- true concurrent acceptance integration test with separate DB transactions;
- single-award MVP constraint/concurrency test under the approved enforcement design;
- idempotent replay and fingerprint-conflict tests;
- stale readiness between response submission and acceptance;
- stale source-version test;
- ownership/authority tests;
- exact transition allowed/forbidden matrix tests;
- outbox atomicity test;
- DB constraint/migration test;
- proof no Order/payment record is written.

### Documentation Updates

Production acceptance remains gated by the unresolved acceptance transition and enforcement design; single-award cardinality itself is approved. Once approved, update Module architecture and CL-04 architecture if necessary **before** applying the schema migration.

### Acceptance Criteria

- acceptance creates only Gig / Demand-owned truth;
- assignment cardinality is enforced in both policy and DB where enforceable;
- retry replays one assignment result;
- competing acceptance cannot produce an invalid second winner;
- fresh Professional readiness is consumed, not reconstructed;
- no Order, payment, payout, or provider truth is created.

### Exit Gate

- explicit cardinality and transition rulings are recorded;
- concurrency tests prove the invariant;
- idempotency replay passes;
- all acceptance authorization/readiness tests pass;
- migration validation/rollback plan passes if schema changed;
- accepted assignment is retrievable through public Gig interface.

---

## 05 Assignment Checkout Source, Order Handoff, and Reconciliation

### Objective

Expose the accepted `GigAssignment` as a stable, minimized transaction source and reliably hand it to Transaction / Order without allowing either Module to reach into the other’s repositories.

### Observable Result

Transaction / Order can obtain an immutable/minimized accepted-assignment source DTO and create or retrieve exactly one downstream Order through its public command. If the cross-Module handoff is interrupted, reconciliation retries safely without duplicating the assignment or Order.

### Cluster Build-Plan Link

Completes the boundary portion of **CL-04 Feature 03**, and is the Gig / Demand prerequisite/contract for **CL-04 Feature 04 — Order Aggregate and Source Contracts**. It does **not** implement Cluster Feature 04 inside Gig / Demand.

### Dependencies

- Feature 04;
- approved public DTO version;
- Transaction / Order public `createOrderFromGigAssignment` command or equivalent;
- canonical event/outbox/inbox infrastructure;
- SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` for reconciliation if event/command delivery is asynchronous;
- SH-113 `ensureContextThread` if assignment conversation is part of the approved flow;
- SH-041 `requestNotification` for accepted-assignment communication.

### In Scope

- `getGigAssignmentCheckoutSource`;
- versioned `GigAssignmentCheckoutSource` contract;
- source eligibility checks (accepted/otherwise approved assignment state);
- assignment-ready event payload;
- Order handoff application coordinator that calls Order public interface, not its repository;
- optional SH-113 `ensureContextThread` request for the approved business context;
- reconciliation worker for accepted assignment with missing Order result/reference;
- stable correlation between assignment and downstream Order result without making Order status local truth.

### Out of Scope

- `Order` model/repository/status transitions;
- price/entitlement snapshot rules owned by Order;
- payment/agreement/refund;
- direct Order table query to repair handoff;
- Stripe/provider calls;
- transaction completion synchronization.

### Module-Owned Data

- `GigAssignment` source fields;
- no duplicate Order fields added merely for convenience;
- an optional cached downstream Order identifier may exist only if already supported/approved and must not become Order status truth. Prefer querying Order owner by assignment source where possible.

### Public Interfaces

- `getGigAssignmentCheckoutSource(assignmentId)` returning at minimum approved source ID/version, customer/buyer reference, Professional reference, agreed amount/currency, title/description or frozen source data, and source status;
- `requestOrderForGigAssignment` as an application orchestration entry if Gig / Demand owns initiating the handoff;
- event `GigAssignmentReadyForOrder` if event-driven;
- no public “setOrderStatus” or local Order mirror.

### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-123 `validateOwnedTargetReference` | source owner pattern | Order validates assignment source through Gig public interface | eligible assignment relationship | direct `prisma.gigAssignment` read from Order Module |
| SH-046 `publishDomainEvent` | platform | assignment-ready event | event payload/version | ad hoc cross-Module call after commit without retry strategy |
| SH-045 `deduplicateDomainEvent` | platform inbox | event consumers | handler identity/effect | local processed-event table for ordinary domain events |
| SH-047 `enqueueReliableJob` | queue infra | interrupted handoff/reconciliation | payload/terminal meaning | `gigOrderQueue` implementation |
| SH-048 `executeRetryWithBackoff` | queue infra | transient Order dependency failure | retryability | hand-written setTimeout retry loop |
| SH-113 `ensureContextThread` | Messaging | assignment/response thread if approved | context and participant selection | `assignmentConversation.ts`, Thread repository write |
| SH-041 `requestNotification` | Notification | acceptance/handoff alerts | business meaning/recipient intent | email/SMS/push provider code |
| SH-037 `recordIntegrationFailure` | Observability / Ops | repeated owner-interface failure | safe Gig/assignment references | storing failure as GigAssignment business status |

### Domain Logic

- only an assignment in the approved Order-source state can be returned as checkout source;
- source DTO is immutable for the Order-creation attempt by source version; later Gig edits must not silently alter an Order created from an earlier source version;
- Transaction / Order owns validation that its own Order source uniqueness is satisfied;
- Gig / Demand must not infer “paid”, “agreement complete”, or “Order completed” from handoff success;
- if Order creation returns an existing Order for the assignment, treat that as successful idempotent reconciliation;
- if Order is unavailable after assignment acceptance, assignment remains accepted source truth.

### Authorization / Compliance

- internal Module-to-Module source query requires trusted requesting context, not a public arbitrary ID scrape;
- customer/professional-facing assignment reads remain relationship-authorized;
- no financial readiness or entitlement snapshot is performed here unless Professional Eligibility explicitly makes it part of the accepted-assignment gate already consumed in Feature 04.

### Database / Transaction Behavior

- no distributed transaction spans Gig and Order databases/tables as one business owner transaction;
- source event is committed atomically with GigAssignment acceptance in Feature 04;
- Order handoff uses idempotency keyed to source assignment ID/version;
- reconciliation reads Gig-owned assignment and calls Order public query/command; it must not mutate Order tables directly;
- if storing local handoff operational metadata is necessary, use workflow/operational records approved by architecture, not a fake Order status field.

### Events / Jobs

- `GigAssignmentReadyForOrder` event with minimized source reference/version;
- queue job `reconcileGigAssignmentOrderHandoff` or equivalent Module-owned payload running on shared queue;
- retry transient Order-interface failures with bounded backoff;
- permanent invalid-source failures become terminal operational failures/manual review, not infinite retry;
- once Order exists, no periodic polling is needed unless an explicit synchronization rule is approved.

### Provider Integration

None. Payment providers belong to Payment / Payout / Tax.

### UI / Admin Surface

- assignment page may show “Order pending creation” only if backed by an explicit workflow/owner result, not guessed from absence;
- minimal operator diagnostic for stuck handoff may be added later in Feature 09; no generic commerce admin tool here.

### Failure Behavior

- Order command timeout → retry with same idempotency/correlation;
- Order command returns existing Order → success/reconciled;
- source assignment no longer eligible → terminal conflict/manual review according to approved rules;
- repeated infrastructure failure → dead-letter + IntegrationFailure, assignment source remains unchanged;
- Messaging/Notification failure → independent retry; no rollback of assignment/Order truth.

### Tests

- checkout-source DTO contract/version tests;
- direct-cross-repository prohibition test/static boundary if tooling supports it;
- Order command mock/contract: created/existing/unavailable/conflict;
- idempotent handoff replay;
- event inbox dedupe;
- reconciliation resumes after transient failure;
- permanent failure dead-letters once max attempts reached;
- Messaging Thread request uses SH-113 `ensureContextThread` if enabled;
- Notification failure isolation;
- end-to-end contract fixture: accepted assignment → one Order result when Transaction / Order feature is available.

### Documentation Updates

Record the final checkout-source DTO and versioning rules in Module architecture and Transaction / Order public-interface documentation. If the CL-04 Order feature settles a source-snapshot rule, update both owner documents before changing the DTO.

### Acceptance Criteria

- Order can create transaction truth without direct Gig repository reads;
- one assignment source maps to one downstream Order according to Order-owned uniqueness;
- handoff is retryable and idempotent;
- GigAssignment remains source truth during downstream outages;
- no Order/payment status mirror is introduced locally.

### Exit Gate

- checkout-source contract test passes against Transaction / Order fixture/real public API;
- reconciliation/idempotency/dead-letter tests pass;
- Module boundaries are verified by code/import review;
- no direct Order Prisma access exists under `gig-demand`;
- CL-04 Feature 03 boundary is ready for Cluster Feature 04.

---

# Phase 4 — Lifecycle Maintenance and Guardrails

## 06 Gig and Assignment Lifecycle Maintenance, Expiration, Moderation, and Communication

### Objective

Implement the remaining approved Gig/Assignment maintenance transitions and durable external effects, including deadline expiration and moderation execution, without allowing downstream Modules to own Gig state.

### Observable Result

Approved pause/reopen/cancel/archive/assignment-maintenance actions work through Gig-owned commands; closing deadlines expire eligible Gigs reliably; moderation decisions can restrict/restore Gig source behavior according to approved rules; Messaging/Notification effects are requested through their owners.

### Cluster Build-Plan Link

Supports **CL-04 Feature 13 — Cross-Cluster Contract Proof** and **Feature 14 — Security, Privacy, Reconciliation, and Production Readiness**. It must not reorder Cluster Features 04–12; it may be implemented when its dependencies are available and its transition rules are approved.

### Dependencies

- Features 01–05;
- approved Gig and Assignment transition matrices for each implemented action;
- approved semantics for downstream Order/Dispute signals before automatic assignment/Gig completion/disputed transitions;
- SH-055 `runDeadlineExpiration`;
- SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff`;
- SH-103 `executeModerationDecision` protocol;
- SH-091 `requestSearchProjectionRefresh`;
- SH-113 `ensureContextThread`;
- SH-041 `requestNotification`;
- SH-029 `appendAuditEvent`;
- SH-045 `deduplicateDomainEvent` for external owner events.

### In Scope

Depending on approved matrix:

- `pauseGig`;
- `reopenGig`;
- `cancelGig`;
- `archiveGig`;
- `activateGigAssignment`;
- `recordGigAssignmentDelivery`;
- `completeGigAssignment`;
- `cancelGigAssignment`;
- event handlers for approved Order/Dispute facts that request local transition evaluation;
- Gig expiration worker using `closesAt`;
- `executeGigModerationDecision` target-owner handler;
- Search refresh for public-source changes;
- context-thread requests at approved lifecycle points;
- notifications for approved business events.

### Out of Scope

- inventing assignment completion based on Order status without an approved mapping;
- owning Dispute truth;
- editing Order/Refund/Payout state;
- moderation case/action lifecycle;
- Search index worker;
- Notification/Messaging provider delivery;
- generic scheduler/queue implementation.

### Module-Owned Data

- Gig/Assignment statuses and timestamps already owned by the Module;
- no local `moderated`, `blocked`, `orderPaid`, or `disputeOpen` source-of-truth booleans;
- no generic QueueJob truth inside the Module.

### Public Interfaces

Only for actions approved by the final transition matrix:

- `pauseGig`;
- `reopenGig`;
- `cancelGig`;
- `archiveGig`;
- `activateGigAssignment`;
- `recordGigAssignmentDelivery`;
- `completeGigAssignment`;
- `cancelGigAssignment`;
- `executeGigModerationDecision` internal public handler;
- `applyOrderFactToGigAssignment` / `applyDisputeFactToGigAssignment` only if explicit owner-event mappings are approved.

### Shared Operations Used

- SH-053 `transitionLifecycleState` — lifecycle plumbing; graph remains Gig-owned;
- SH-055 `runDeadlineExpiration` — shared scheduler discovers due records and invokes owner expiration command;
- SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` — durable execution;
- SH-045 `deduplicateDomainEvent` — external Order/Dispute/moderation event effects;
- SH-103 `executeModerationDecision` — Moderation owns decision, Gig executes source action;
- SH-091 `requestSearchProjectionRefresh` — public visibility effects;
- SH-113 `ensureContextThread` — Messaging-owned communication context;
- SH-041 `requestNotification` — Notification-owned delivery;
- SH-029 `appendAuditEvent` — significant lifecycle/admin actions;
- SH-037 `recordIntegrationFailure` / queue telemetry — operational failure only.

### Domain Logic

- every lifecycle mutation validates the approved from→to edge, actor/system trigger, and required guard;
- expiration occurs only for statuses defined as expirable by Gig policy and only when `closesAt <= now` under a clock-controlled comparison;
- a stale expiration job must no-op if the Gig has already moved to a non-expirable state;
- moderation instruction carries authoritative case/action reference; Gig applies only actions allowed for Gig targets;
- Search removal/restoration is requested after Gig source state commits; it does not define Gig status;
- `GigAssignmentStatus.disputed` must not become a local copy of Dispute truth unless an explicit event-to-local-state mapping is approved;
- completion terms remain distinct: Gig fulfilled/closed, Assignment completed, and Order completed are separate facts.

### Authorization / Compliance

- customer owns normal Gig pause/cancel/archive paths when allowed;
- Professional owns only assignment actions explicitly assigned to Professional actor;
- admin/support actions require Role / Authority and Audit proof;
- moderation handler trusts only authenticated internal moderation command/event contract, not client-submitted moderation flags;
- holds may gate selected transitions through SH-011 `evaluateComplianceHold` if the approved matrix says so.

### Database / Transaction Behavior

- each lifecycle transition + owner outbox is atomic;
- expiration command is idempotent by Gig ID + deadline/version;
- event consumers use inbox dedupe;
- concurrent manual action versus expiration uses aggregate lock/optimistic version to prevent stale overwrite;
- do not use scheduler timestamp as source truth; the Gig status/timestamps are source truth.

### Events / Jobs

- deadline scan invokes `expireGig` through shared scheduler/queue;
- potential events: `GigPaused`, `GigReopened`, `GigCancelled`, `GigExpired`, `GigArchived`, `GigAssignmentActivated`, `GigAssignmentDelivered`, `GigAssignmentCompleted`, `GigAssignmentCancelled`;
- event names/payloads are versioned and minimized;
- poison jobs dead-letter with safe operator context.

### Provider Integration

None.

### UI / Admin Surface

- lifecycle actions/statuses for customer/professional as appropriate;
- no generic moderation UI—the Moderation Module owns case/reviewer surfaces;
- operator diagnostic may show safe stuck-job IDs/status in Feature 09.

### Failure Behavior

- stale transition → conflict/no overwrite;
- expiration after manual cancel/archive → idempotent no-op;
- Search/Notification/Messaging unavailable → source transition remains committed; effects retry;
- malformed/unauthorized moderation instruction → reject, audit operationally if appropriate;
- unresolved Order/Dispute synchronization → no transition rather than guessed mapping.

### Tests

- exhaustive approved lifecycle transition tests;
- manual transition vs expiration race;
- expiration clock/boundary tests;
- duplicate job/event dedupe;
- moderation action allowed/forbidden contract tests;
- Search de-index/restore request after commit;
- Messaging/Notification request contract tests;
- audit completeness for admin/significant actions;
- proof external dependency failure does not mutate source incorrectly.

### Documentation Updates

Update Module architecture whenever an unresolved transition/synchronization mapping becomes binding. If a new domain lifecycle ledger is approved, document its ownership before schema creation.

### Acceptance Criteria

- all implemented lifecycle transitions have explicit, tested owners/triggers;
- expiration cannot overwrite newer state;
- moderation affects Gig truth only through an owner-approved handler;
- downstream communication/projection failures are recoverable;
- no foreign lifecycle truth is mirrored locally.

### Exit Gate

- approved transition matrix coverage is complete for implemented actions;
- expiration race/idempotency tests pass;
- moderation/Search/Messaging/Notification contracts pass;
- no unsupported completion/dispute mapping has been introduced;
- queue/dead-letter behavior is observable.

---

## 07 Privacy Executor and Retention-Safe Gig Data Handling

### Objective

Make Gig / Demand a complete participant in Privacy / Data Erasure by enumerating its subject data and executing approved erase/anonymize/restrict/detach/retain/export instructions without owning privacy-request orchestration.

### Observable Result

Privacy / Data Erasure can discover Gig-domain records associated with a subject, receive supported dispositions/retention candidates, and invoke idempotent Gig-owned privacy actions. Search and Media context effects are requested through their owners.

### Cluster Build-Plan Link

Implements the Gig privacy executor prerequisite **before CL-04 Feature 13 privacy contract proof** under CL-04-R014. Feature 14 later hardens retention, destructive behavior, batching, and production safeguards.

### Dependencies

- prior Gig-domain features for records that may exist;
- Privacy target protocol;
- SH-096 `enumerateSubjectData`;
- SH-095 `executePrivacyInstruction`;
- SH-097 `evaluateRetentionRequirement`;
- SH-098 `anonymizePersonalFields` shared primitive if adopted;
- SH-091 `requestSearchProjectionRefresh`;
- Media detach/delete owner interfaces as instructed;
- approved destructive-retention rules before destructive accepted/converted commercial data treatment.

### In Scope

- subject-data inventory for `Gig`, `GigResponse`, `GigAssignment`, `GigTag`, `GigMedia` context;
- `enumerateGigSubjectData` implementation of Privacy contract;
- `executeGigPrivacyInstruction`;
- export serializer for Gig-domain data where Privacy requests it;
- retention-fact evaluation for draft/unconverted versus accepted/converted records;
- field-level anonymization maps once approved;
- contextual media detachment instructions without deleting MediaAsset directly;
- Search removal/refresh requests after privacy-relevant source changes;
- idempotent result/evidence references back to Privacy owner.

### Out of Scope

- `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, or `DataRetentionExemption` lifecycle;
- legal retention duration invention;
- direct R2/object deletion;
- direct Typesense deletion;
- deleting Order/Agreement/Dispute truth;
- a generic “delete user” command.

### Module-Owned Data

Privacy inventory must account for:

- Gig title/description/location fields and customer actor references;
- GigResponse message, proposed commercial terms, responder references;
- GigAssignment actor references, agreed terms, timing fields;
- GigTag provenance/confidence where tied to a subject;
- GigMedia contextual joins;
- any Gig-owned lifecycle event records if later approved.

### Public Interfaces

- `enumerateGigSubjectData(request): PrivacySubjectDataPage`;
- `evaluateGigRetentionRequirement(target): RetentionDecision`;
- `executeGigPrivacyInstruction(command): PrivacyTargetResult`;
- `serializeGigPrivacyExport(target)` internal/export contract.

### Shared Operations Used

| Canonical operation | Owner/class | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-096 `enumerateSubjectData` | each data owner via Privacy protocol | inventory | Gig schema/relations/dispositions | Privacy directly crawling Gig tables |
| SH-097 `evaluateRetentionRequirement` | data owner supplies facts; Privacy records exemption | before destructive action | accepted/converted commercial retention facts | local retention-exemption table |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; Gig executes | target action | exact Gig field/action mapping | `gigGdprService`, custom PrivacyRequest workflow |
| SH-098 `anonymizePersonalFields` | shared primitive | approved anonymization | Gig field map | global crawler rewriting all fields |
| SH-091 `requestSearchProjectionRefresh` | Search | deindex/refresh after source privacy change | source reason/version | direct Typesense delete |
| Media owner deletion/detach interface | Media / File Access | underlying object action when instructed | Gig only owns context link | direct object-storage delete |
| SH-029 `appendAuditEvent` | Audit | privacy execution proof where required | safe counts/target refs | raw personal-data audit payload |
| SH-034 `sanitizeTelemetryMetadata` | Observability/Audit policy | privacy execution logs | Gig sensitivity labels | logging erased content |

### Domain Logic

- product archive/cancel is not legal erasure;
- draft/unconverted customer demand may have different retention requirements from assignment terms that became an Order source;
- accepted/paid terms duplicated/frozen in Order are independently owned there; deleting/anonymizing Gig-domain source must not silently mutate Order truth;
- retain only fields justified by an approved retention result; anonymize other personal fields when permitted;
- `GigMedia` detachment does not imply MediaAsset deletion; Privacy/Media coordinate the underlying object independently;
- privacy execution is idempotent and returns `erased`, `anonymized`, `retained`, `restricted`, `detached`, `skipped`, or failure results according to the canonical protocol;
- if retention policy is unresolved for a destructive target, return a blocked/manual-review result rather than delete.

### Authorization / Compliance

- only trusted Privacy orchestration may invoke internal privacy executor;
- the executor validates request/job/target identifiers but does not own their status;
- export serialization follows actor/Privacy verification context supplied by Privacy owner;
- do not emit personal content into audit/telemetry metadata.

### Database / Transaction Behavior

- execute per-target disposition transactionally where feasible;
- source version check prevents stale privacy job from overwriting newer legally relevant state without reevaluation;
- contextual join detachment and Gig-field anonymization occur under owner transaction;
- external Search/Media effects use outbox/jobs and are not part of a distributed transaction;
- privacy target idempotency key makes retry return the same terminal disposition.

### Events / Jobs

- owner executor may emit minimized `GigPrivacyDispositionApplied` only if a downstream need exists;
- Search/Media commands are durable/retryable;
- no Module-owned Privacy scheduler;
- failed external effect becomes retryable operational work while owner disposition result clearly states local completion versus downstream pending when protocol permits.

### Provider Integration

None directly. Storage/search provider deletion remains behind Media/Search.

### UI / Admin Surface

No customer privacy-request UI here. Privacy Module owns request/status surfaces. A safe internal diagnostics view may expose target IDs/results later under platform ops.

### Failure Behavior

- retention rule unresolved → manual review/blocked, no destructive write;
- target already anonymized/erased → idempotent replay;
- stale source version → re-evaluate or conflict according to protocol;
- Search/Media unavailable → queue retry; do not fabricate provider deletion success;
- forbidden target/disposition → terminal unsupported result.

### Tests

- inventory completeness across Gig/Response/Assignment/tag/media context;
- draft erase/anonymize scenarios where policy allows;
- retained accepted/converted record scenario using retention decision fixture;
- idempotent executor replay;
- stale-version protection;
- Search deindex request contract;
- Media detach/delete boundary test;
- export serializer privacy-safe output;
- telemetry/audit redaction tests;
- no PrivacyRequest/DataErasureJob local mutation.

### Documentation Updates

When retention rules are legally/architecturally approved, update Module architecture privacy section and field disposition matrix before enabling destructive execution. Update Privacy owner’s target registry with final Gig target types/contracts.

### Acceptance Criteria

- Privacy owner can enumerate all Gig-domain subject data without direct table ownership;
- every supported disposition is idempotent and evidence-producing;
- unresolved retention blocks destructive action;
- Search/Media effects use owner interfaces;
- no local privacy workflow truth is created.

### Exit Gate

- privacy contract/integration tests pass;
- inventory coverage is reviewed against current Prisma schema;
- retention-denial test passes;
- telemetry contains no prohibited content;
- destructive paths remain disabled until their retention rulings are approved.

---

# Phase 5 — Module Integration Proof

## 08 Cross-Module Contract Proof

### Objective

Prove Gig / Demand works with its critical neighboring owners exclusively through public contracts/events, including positive, denial, timeout, replay, and stale-version paths.

### Observable Result

The complete customer-demand journey can run in an integration environment:

```text
CustomerProfile
→ Gig draft/publication
→ eligible Professional response
→ atomic acceptance
→ GigAssignment
→ Transaction / Order source handoff
```

Search, Messaging, Notification, Media, Location, Holds, Moderation, Audit, and Privacy participate through owner interfaces. No integration test needs a direct cross-Module repository mutation to make the workflow pass.

### Cluster Build-Plan Link

Implements the `gig_demand` portion of **CL-04 Feature 13 — Cross-Cluster Contract Proof**.

### Dependencies

- Features 01–07 relevant exit gates;
- approved cardinality/lifecycle decisions required by the acceptance path;
- neighboring Module contract fixtures or real test implementations;
- real transactional outbox/inbox/queue runner in integration environment;
- Transaction / Order source contract available.

### In Scope

Contract/integration proof for:

- Identity & Access → authenticated actor;
- Customer / Buyer Profile → buyer actor;
- Role / Authority → resource decisions;
- Taxonomy → classification/requirements;
- Professional Eligibility → response/acceptance readiness;
- Compliance Hold → publish/accept denial;
- Media → validated GigMedia context;
- Location Safety → fuzzy public location;
- Search → source projection refresh;
- Messaging → context Thread;
- Notification → business alert request;
- Transaction / Order → assignment source/order handoff;
- Moderation → target-owner action execution;
- Privacy → Gig target executor;
- Audit / Observability → evidence/telemetry.

### Out of Scope

- implementing missing neighboring Module internals;
- changing Cluster sequencing;
- provider end-to-end tests owned by another Module unless a normalized contract fixture is needed;
- new business features.

### Module-Owned Data

No new ownership. Test fixtures may reveal schema/contract gaps, but changes require architecture review.

### Public Interfaces

All Module public interfaces introduced in Features 01–07 are contract-tested. Particular emphasis:

- `createGigDraft`;
- `publishGig`;
- `submitGigResponse`;
- `acceptGigResponse`;
- `getGigAssignmentCheckoutSource`;
- privacy executor interfaces;
- source projection query/builder;
- moderation handler.

### Shared Operations Used

Use the real/shared test implementations of every canonical operation exercised by the journey. No new shared operation is introduced in this feature.

### Domain Logic

The integration suite must verify that passing one gate never substitutes for another:

- authenticated actor ≠ authorization;
- authorization ≠ Professional readiness;
- valid taxonomy ≠ verification readiness;
- Media ready ≠ business attachment authorization;
- Gig public ≠ Search indexed;
- GigAssignment accepted ≠ Order paid;
- Notification delivered ≠ source event occurred;
- privacy deindex ≠ source erase.

### Authorization / Compliance

Mandatory negative paths:

- wrong CustomerProfile tries to edit/publish/accept;
- ProfessionalProfile owned by another actor submits response;
- readiness denied/expired between submit and accept;
- ComplianceHold active;
- Media private/not ready;
- exact location attempts to enter public source projection;
- unauthorized moderation/privacy invocation;
- internal source DTO queried by untrusted caller.

### Database / Transaction Behavior

- use real database constraints for response uniqueness and accepted-assignment cardinality;
- use real idempotency/concurrency/outbox/inbox implementation;
- verify no test fixture bypasses owner interfaces by directly inserting foreign truth except setup owned by that test owner;
- simulate stale versions and transaction conflicts.

### Events / Jobs

- prove outbox commit and consumer inbox dedupe;
- simulate duplicate event delivery;
- simulate Search/Notification/Order dependency timeout then recovery;
- run expiration/reconciliation worker through shared queue;
- verify dead-letter behavior for a poison item.

### Provider Integration

Gig / Demand has no provider adapter. Use normalized neighboring contracts only; raw Stripe/Typesense/R2/provider payloads must not enter Gig domain APIs.

### UI / Admin Surface

Playwright/E2E where the Gig UI exists:

- customer creates/publishes Gig;
- Professional responds;
- customer views and accepts;
- both see assignment state;
- Order handoff result becomes visible through owner-composed UI without local payment assumptions.

### Failure Behavior

The integration test matrix must demonstrate:

- dependency unavailable → safe unavailable/retry result;
- duplicate command/event → one semantic effect;
- stale transition → conflict;
- downstream projection/notification failure → source truth survives;
- dead-lettered async work is discoverable and recoverable;
- no test passes only because of direct database coupling.

### Tests

- public-interface contract tests;
- cross-Module integration tests;
- event/outbox/inbox tests;
- authorization/compliance negative paths;
- concurrency/idempotency tests;
- privacy/moderation integration tests;
- Playwright critical Gig journey where UI exists;
- import/dependency boundary lint or architecture test if supported.

### Documentation Updates

Any contract discrepancy must be resolved in the owning architecture/public-interface document before code is changed. Update progress tracker with exact integration coverage and remaining blockers.

### Acceptance Criteria

- every major Gig dependency is consumed through a named public interface/shared operation;
- positive end-to-end demand journey passes;
- negative dependency/gate paths fail safely;
- duplicate/retry/event paths are proven;
- no direct foreign repository is needed by Gig implementation or tests.

### Exit Gate

- CL-04 Feature 13 Gig contract matrix passes;
- E2E/contract/integration suites pass;
- event replay/dedupe passes;
- no high-severity cross-Module ownership violation remains;
- all remaining failures are documented owner/dependency blockers, not hidden test workarounds.

---

# Phase 6 — Module Hardening and Production Verification

## 09 Concurrency, Replay, Migration, Reconciliation, Security, and Production Readiness

### Objective

Harden Gig / Demand against production races, stale commands, failed asynchronous effects, migration/backfill risk, privacy/security defects, and operational blind spots without adding new product behavior.

### Observable Result

Concurrent response/acceptance paths remain correct; retries are safe; expiration and Order-handoff reconciliation recover interrupted work; CustomerProfile/backfill migrations are validated; operators can diagnose stuck Gig workflows using safe telemetry; privacy and public projection remain correct under failure.

### Cluster Build-Plan Link

Implements the `gig_demand` portion of **CL-04 Feature 14 — Security, Privacy, Reconciliation, and Production Readiness**.

### Dependencies

- Feature 08;
- approved production CustomerProfile/cardinality/transition/retention rulings;
- production platform idempotency/concurrency/outbox/queue/observability implementations;
- final neighboring public contracts;
- migration/backfill tooling.

### In Scope

- acceptance race stress tests;
- response duplicate/revision race tests;
- pause/cancel/expire races;
- command replay and event replay matrix;
- accepted-assignment missing-Order reconciliation;
- failed Search/Notification/Messaging effect replay;
- CustomerProfile backfill/non-null migration if approved;
- assignment-cardinality constraint backfill/migration if approved;
- index/query-plan review for hot Gig/response/assignment queries;
- privacy inventory/disposition audit;
- authorization and rate-limit review;
- telemetry redaction and metric cardinality review;
- dead-letter recovery procedure;
- migration rollback/verification scripts and documentation;
- final production-like critical journey.

### Out of Scope

- new Gig pricing model;
- new visibility mode/audience system;
- new provider choice;
- new dispute/payment policy;
- unapproved lifecycle transitions;
- refactoring shared platform primitives into this Module.

### Module-Owned Data

- existing Gig-domain records and approved migration constraints/indexes only;
- operational telemetry remains Observability truth, not Gig status;
- no generic integration-failure or queue table is moved into the Module.

### Public Interfaces

No new public business API should be required. Production-safe diagnostics may expose:

- health/dependency readiness for Gig-owned workflows;
- reconciliation command restricted to operator/system authority;
- source version/status diagnostic query with safe fields;
- privacy inventory executor already introduced.

Any new business command discovered here must be moved back to the appropriate earlier feature and architecture reviewed.

### Shared Operations Used

- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock` / SH-052 `withOptimisticConcurrency`;
- SH-053 `transitionLifecycleState`;
- SH-046 `publishDomainEvent` / SH-045 `deduplicateDomainEvent`;
- SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff`;
- SH-055 `runDeadlineExpiration`;
- SH-032 `createRequestContext`, SH-033 `writeStructuredLog`, SH-034 `sanitizeTelemetryMetadata`, SH-036 `emitMetric`, SH-037 `recordIntegrationFailure`, SH-038 `recordQueueTelemetry`, SH-035 `captureException`;
- SH-029 `appendAuditEvent` and SH-030 `recordSensitiveAccess` where applicable;
- privacy protocol operations;
- Search/Notification/Messaging/Order public interfaces.

No substitute primitives may be created for testing convenience.

### Domain Logic

Hardening must preserve these facts under stress:

- one response row per Professional/Gig;
- accepted-assignment cardinality exactly matches approved ruling;
- retry never duplicates business effect;
- stale expiration cannot overwrite newer Gig state;
- stale external event cannot regress source state;
- Order reconciliation cannot create a second Order effect for one assignment;
- public projection never reveals exact/private location or unapproved media;
- privacy/retention result never silently destroys required accepted/converted commercial proof;
- operational failure never fabricates a Gig-domain success/failure status.

### Authorization / Compliance

- re-run authorization matrix for every public command/query;
- verify internal worker/moderation/privacy endpoints require trusted system context;
- apply platform rate limiting to Gig creation/response/acceptance endpoints according to root policy;
- admin/support access remains explicit and audited;
- telemetry payload allowlists exclude Gig response messages/location details unless strictly required and safe;
- public search source remains privacy-safe.

### Database / Transaction Behavior

- use production-like concurrency isolation;
- verify unique/index constraints with realistic contention;
- migration sequence for CustomerProfile/cardinality changes must include audit → backfill → validation → constraint → rollback plan;
- no destructive migration proceeds with unresolved orphan/conflict rows;
- query plans reviewed for customer Gig list, public source fetch, Gig response list, Professional assignments, expiration scan, and reconciliation scan;
- batch/backfill jobs use resumable cursors and idempotent owner commands.

### Events / Jobs

- replay outbox events and confirm consumer dedupe;
- run failure injection for Search/Notification/Order handoff;
- resume dead-lettered reconciliation safely;
- expiration uses clock-controlled batches and does not starve other work;
- record queue telemetry and IntegrationFailure for persistent technical degradation;
- no infinite retries.

### Provider Integration

No direct providers. Production verification must specifically prove raw provider payloads cannot cross into Gig public/domain contracts from neighboring Modules.

### UI / Admin Surface

- production Gig customer/professional flows receive stable conflict/unavailable/retry messages;
- operator diagnostics show IDs, operation, attempts, correlation, safe error category, and remediation path without exposing private response text or exact location;
- no “repair by arbitrary SQL” product endpoint.

### Failure Behavior

- poison job → dead-letter and operator action;
- dependency outage → degraded/unavailable result with retryability, no fabricated domain transition;
- migration conflict/backfill anomaly → deployment gate failure;
- concurrency serialization failure → bounded retry or conflict according to command policy;
- reconciliation sees newer incompatible state → do not overwrite; route manual review;
- privacy retention uncertainty → no destructive action.

### Tests

- high-contention acceptance test;
- repeated response insert/update race test;
- expiration/manual-transition race test;
- command replay/fingerprint mismatch tests;
- event replay/out-of-order tests;
- reconciliation idempotency/resume/dead-letter tests;
- migration/backfill dry-run tests;
- query-plan/performance thresholds for hot queries;
- full authorization matrix;
- rate-limit/security tests where platform harness exists;
- telemetry redaction fixtures;
- privacy/retention regression suite;
- production-like Playwright Gig→response→assignment→Order journey;
- static/import boundary check proving no provider or foreign repository leakage.

### Documentation Updates

- update progress tracker and production runbook;
- update Module architecture only for legitimately approved binding changes exposed by hardening;
- record final migration/backfill strategy;
- record dead-letter/reconciliation operator procedure;
- update Shared Operations Registry only if a genuinely missing cross-platform primitive is discovered and approved—never create it locally first.

### Acceptance Criteria

- no invalid assignment/response duplication under concurrency;
- all idempotent commands replay stable results;
- outbox/inbox replay is safe;
- expiration/reconciliation recover from interruptions;
- approved migrations are backfilled/validated/rollback-capable;
- privacy and public projection remain safe;
- telemetry is useful and minimized;
- no high-severity ownership/security/privacy defect remains.

### Exit Gate

Before Gig / Demand is production-ready:

- typecheck, lint, formatting, Module unit/integration/contract/E2E suites pass;
- migration validation and rollback drills pass;
- concurrency/replay stress tests pass;
- privacy/retention review passes for enabled destructive paths;
- Search/Notification/Order outage simulations recover correctly;
- no direct provider clients or cross-Module repositories exist in the Module;
- operator can identify and remediate stuck Gig expiration/handoff work through supported owner paths;
- all unresolved architecture items affecting enabled production behavior are either approved and documented or the affected behavior remains disabled.

---

# Module Integration Phase

Feature 08 is the explicit Module integration phase. It proves public contracts rather than shared database assumptions.

Minimum boundary proof:

```text
CL-01
  Identity & Access      → resolveAuthenticatedActor
  Role / Authority       → authorizeResourceAction
  Customer / Buyer       → resolveCustomerActor

CL-02
  Taxonomy               → validateTaxonomyAssignment / resolveTaxonomyRequirements
  Search                 ← buildGigSearchSourceProjection + requestSearchProjectionRefresh

CL-03
  Professional Eligibility → evaluateProfessionalReadiness

CL-04
  Gig / Demand           → Gig / GigResponse / GigAssignment truth
  Transaction / Order    ← GigAssignment checkout source / order handoff

CL-07
  Messaging              ← ensureContextThread
  Notification           ← requestNotification

CL-08
  Location Safety        → applyFuzzyPublicLocation
  Privacy                ↔ enumerate/execute Gig privacy targets

CL-09
  Compliance Hold        → evaluateComplianceHold
  Moderation             → executeModerationDecision
  Audit / Ops            ← audit and operational evidence
```

The proof is incomplete if a test reaches directly into a dependency’s Prisma repository to make the journey succeed.

---

# Module Hardening Phase

Feature 09 is the Module hardening phase. It is limited to already-approved Gig / Demand behavior:

- state-transition races;
- response uniqueness;
- assignment cardinality;
- command idempotency;
- event replay/deduplication;
- Gig expiration;
- accepted-assignment/Order reconciliation;
- dependency outage recovery;
- CustomerProfile/cardinality migration safety;
- privacy/retention execution;
- Search/location privacy;
- authorization/rate limiting;
- audit and telemetry completeness;
- query/index performance;
- dead-letter and operator recovery.

It must not introduce a new visibility model, a new lifecycle graph, a new provider, or a new commercial policy.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Demand Source Foundation | 01–02 |
| 2 | Professional Response | 03 |
| 3 | Accepted Work and Order Boundary | 04–05 |
| 4 | Lifecycle Maintenance and Guardrails | 06–07 |
| 5 | Module Integration Proof | 08 |
| 6 | Module Hardening and Production Verification | 09 |

**Total numbered features: 9**

### Cluster alignment

| Module feature | Governing CL-04 feature/milestone |
| --- | --- |
| 01–02 | CL-04 01 — Gig Draft and Publication Boundary |
| 03 | CL-04 02 — Professional Gig Response |
| 04–05 | CL-04 03 — Atomic Response Acceptance and GigAssignment; Feature 05 also supplies the contract required by CL-04 04 |
| 06–07 | Participates in CL-04 13–14; implementation must not interfere with CL-04 04–12 sequencing |
| 08 | CL-04 13 — Cross-Cluster Contract Proof |
| 09 | CL-04 14 — Security, Privacy, Reconciliation, and Production Readiness |

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root `project-overview.md`.
2. Read root `architecture.md` and code standards.
3. Read the Canonical Shared Operations Registry.
4. Read CL-04 `architecture.md` and `build-plan.md`.
5. Read `gig_demand/module-architecture.md` and this plan.
6. Read public-interface sections for every direct dependency used by the feature.
7. Confirm the previous Module exit gate and the governing Cluster sequencing point.
8. Check whether the feature touches an unresolved architecture decision. If yes, stop the affected production behavior until the ruling is approved.
9. Produce the Required Feature Implementation Specification below.
10. Implement only that numbered feature.
11. Run required type, lint, unit, DB/integration, contract, migration, and E2E checks applicable to the feature.
12. Verify source-truth boundaries and cross-Module contracts.
13. Update progress tracking.
14. Update architecture only when a binding decision legitimately changed and was approved.
15. Record assumptions, blockers, risks, and deferred work.

---

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise feature specification containing:

- **Feature:** number and name;
- **Objective:** one implementation result;
- **Observable result:** behavior visible through UI, public contract, persisted truth, worker, or event;
- **Cluster build-plan link:** governing CL-04 feature/milestone;
- **Dependencies:** prior Module exit gates, owner interfaces, shared operations, migrations, providers if any;
- **In scope:** exact files/behaviors/data to implement;
- **Out of scope:** neighboring responsibilities explicitly excluded;
- **Owned data affected:** Gig-domain models/enums/events/projections only;
- **Public contracts:** commands, queries, events, privacy handlers changed or introduced;
- **Shared operations consumed:** canonical names, owners, invocation points, local policy, prohibited duplicate;
- **Permissions/compliance:** actor, resource facts, readiness/hold/location/media/privacy rules;
- **Primary workflow:** ordered command/query flow;
- **Provider integration:** normally `None` for Gig / Demand; if a provider appears, stop and verify ownership;
- **Jobs/events:** outbox, queue, schedule, retry, dedupe, dead-letter behavior;
- **Idempotency/concurrency:** semantic key, lock/version, conflict/replay behavior;
- **Error behavior:** stable result categories/reason codes;
- **Tests:** exact categories and important scenarios;
- **Acceptance criteria:** observable completion conditions;
- **Documentation updates:** only files legitimately affected.

Do **not** generate all feature specifications in advance. Each specification is written immediately before its implementation so it reflects the then-current architecture and repository state.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed:** number/name;
- **Files added:** paths;
- **Files changed:** paths;
- **Database changes:** models/constraints/indexes/SQL affected;
- **Migrations:** migration names and validation/rollback status;
- **Dependencies added:** package/runtime dependencies, if any;
- **Module public interfaces added/changed:** exact contracts/versions;
- **Shared operations reused:** canonical operation names and owners;
- **Events/jobs added:** names, versions, queue/schedule, idempotency keys;
- **Provider adapter changes:** should normally be `None` for this Module;
- **Tests added/changed:** files and scenario counts where useful;
- **Commands run:** typecheck/lint/test/build/migration/Playwright commands;
- **Manual/contract verification:** workflows exercised and dependency fixtures used;
- **Documentation updated:** exact context/progress files;
- **Assumptions:** implementation assumptions still in force;
- **Known failures:** failing tests/commands or degraded dependencies;
- **Remaining risks:** architecture/security/privacy/performance concerns;
- **Deferred work:** explicitly excluded next work;
- **Exit-gate result:** PASS/FAIL with reason.

A completion report must not call the feature complete when its exit gate failed.

---

# Final Module Quality Check

Before declaring the Module implementation plan complete or using it to drive production code, verify:

1. `Gig`, `GigResponse`, and `GigAssignment` have exactly one lifecycle owner: Gig / Demand.
2. CustomerProfile, ProfessionalProfile, Taxonomy, Verification, ComplianceHold, MediaAsset, Thread, Notification, Search, Privacy, Order, payment, and dispute truth remain with their owners.
3. Every cross-cutting behavior names the canonical Shared Operation or owner public interface it consumes.
4. Aliases such as `requireAuthenticatedActor`, `gigPermissions`, `gigEligibilityService`, `gigTypesenseService`, `gigUploadService`, `gigGdprService`, or `gigChatService` have not become competing shared infrastructure.
5. Contextual `GigTag`/`GigMedia` meaning remains separate from TaxonomyTag/MediaAsset truth.
6. Public commands and queries use stable DTOs instead of leaking Prisma records.
7. `invite_only` remains disabled until audience truth exists.
8. Single-award MVP cardinality is approved; implement only approved transitions and enforcement design.
9. CustomerProfile non-null/migration semantics are not invented by a coding agent.
10. Lifecycle matrices are not inferred from enum order.
11. Professional response/acceptance consumes SH-016 `evaluateProfessionalReadiness` rather than foreign compliance tables.
12. Search remains rebuildable projection and uses SH-091 `requestSearchProjectionRefresh`.
13. Order remains downstream transaction truth and is reached through a public source DTO/command.
14. Domain events use outbox; consumers deduplicate through inbox; events describe facts rather than disguise commands.
15. Gig expiration uses the shared scheduler/queue while expiration policy stays local.
16. Privacy orchestration remains Privacy-owned; Gig / Demand only enumerates/executes against its own data.
17. AuditEvent, operational logs, and any future Gig lifecycle ledger remain distinct types of evidence.
18. No provider client is introduced into Gig / Demand.
19. Every numbered feature has explicit tests, acceptance criteria, documentation rules, and an exit gate.
20. The feature sequence remains subordinate to CL-04: Gig / Demand does not independently start Order/Agreement/Payment/Review/Dispute implementation.
21. A coding agent can identify exactly where to stop when it reaches an unresolved architectural decision.

---

# Binding Execution Summary

For implementation planning purposes:

```text
CL-04 01
→ Module 01 Gig Draft Aggregate and Owner Contracts
→ Module 02 Gig Publication / Classification / Media / Location / Search Boundary

CL-04 02
→ Module 03 Professional Gig Response Lifecycle

CL-04 03
→ Module 04 Atomic Response Acceptance and GigAssignment
→ Module 05 Assignment Checkout Source / Order Handoff

CL-04 04–12
→ owned by other CL-04 Modules; Gig / Demand participates only through its published contracts/events

CL-04 13
→ Module 06 relevant lifecycle contracts and Module 07 privacy executor prerequisites
→ Module 08 Cross-Module Contract Proof

CL-04 14
→ Module 06 lifecycle/expiration hardening (required contracts exist before proof)
→ Module 07 privacy hardening (executor exists before proof)
→ Module 09 production hardening
```

No numbered feature in this plan may be used to absorb Transaction / Order, Review / Dispute, Payment / Payout / Tax, Search, Media, Messaging, Notification, Privacy, Moderation, or Professional Eligibility truth into Gig / Demand.
