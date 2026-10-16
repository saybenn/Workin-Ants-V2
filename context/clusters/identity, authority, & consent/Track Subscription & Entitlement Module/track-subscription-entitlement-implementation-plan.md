# Track Subscription & Entitlement Implementation Plan

> **Module ID:** `track_subscription_entitlement`  
> **Module:** Track Subscription & Entitlement  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-implementation-plan.md`\
> **Companion architecture:** `module-architecture.md`  
> **Parent sequence:** `context/clusters/identity, authority, & consent/identity-authority-consent-build-plan.md`\
> **Implementation posture:** greenfield MVP planning against current Workin Ants schema/context. This Module plan is narrower than the CL-01 build plan and must not independently change Cluster sequencing or ownership.

---

## Core Principle

Implement this Module through narrow, independently reviewable slices:

```text
public / observable behavior
→ validated command or query
→ Track-owned policy
→ authoritative Track write/read
→ canonical shared-operation calls
→ domain event / audit / notification / search effect
→ tests
→ exit gate
```

The Module’s primary observable results are contracts and persisted commercial-policy truth, not necessarily UI.

A feature is not complete because a table or provider client exists. It is complete only when the source-owned behavior can be exercised through the intended public boundary and the tests prove that neighboring Modules do not need to recreate Track policy.

---

## Build Rules

1. Follow root Workin Ants architecture, code standards, CL-01 architecture, and this Module architecture.
2. This Module owns only the Track records/enums/lifecycles declared in `module-architecture.md`.
3. Consume other Modules through approved public interfaces/owner-facts contracts; do not pull their Prisma repositories into Track.
4. Reuse the Canonical Shared Operations Registry by `SH-###` ID.
5. Do not create local substitutes for authentication, authorization, consent, holds, audit, notification, Search, Privacy orchestration, queue/retry, idempotency, locks, webhook verification, provider-event dedupe mechanics, or observability.
6. Every mutation is runtime validated, server authorized, transaction-safe, and explicit about actor-track/profile binding.
7. Every lifecycle transition is performed by Track’s application/domain service, not a route, worker, provider adapter, or consumer.
8. Provider details stay behind the Track billing adapter after `PR-CL01-04` is ratified.
9. Provider callbacks are authenticated, deduped, translated, transition-validated, and reconciled.
10. `TrackUsageEvent` remains immutable; `TrackUsageCounter` remains rebuildable.
11. Metering is atomic and semantically idempotent.
12. Current policy comes from SH-005; no consumer-local premium/waiver/commission/priority/boost/quota truth is added.
13. Order/Booking/other historical business decisions remain owned by those consumers.
14. Search receives refresh requests through SH-091; no Typesense call or SearchUpsertEvent write occurs here.
15. Privacy owns PrivacyRequest/DataErasureJob/DataErasureTarget; Track implements only its target executor and inventory.
16. Generic AuditEvent, Track domain events, provider-event dedupe records, and operational failures remain distinct.
17. Every asynchronous job is durable, idempotent, retry-classified, correlated, observable, and dead-letter visible through shared infrastructure.
18. Every numbered feature ends with tests, workflow/contract verification, documentation/progress update, and a concrete exit gate.
19. Do not begin a production behavior whose named architecture gate is unresolved. Resolve architecture first or leave the behavior fixture-only/disabled/fail-closed.
20. This plan must not be used to bypass the CL-01 feature order. If the parent build plan is not ready for the corresponding slice, Track work may prepare contracts/tests but must not activate dependent production behavior.

---

## Preconditions

### Hard platform dependencies

These must exist as real implementations or approved contract/test doubles before the corresponding Track feature:

- PostgreSQL/Prisma transaction and migration foundation;
- runtime request validation;
- SH-001 actor context;
- SH-002 authority;
- SH-029 Audit;
- SH-032–039 request context/logging/telemetry/failure reporting;
- SH-044 idempotency;
- SH-045/046 event inbox/outbox;
- SH-047/048 queue/retry;
- SH-051/052/053 concurrency/lifecycle primitives;
- SH-055 deadline expiration;
- SH-057 atomic counter;
- provider-security shell SH-059–062 before live provider work;
- SH-091 Search refresh before production boost propagation;
- SH-095–098 Privacy protocol before production destructive privacy support.

A missing canonical implementation may be represented by a typed test double. Track must not become the temporary owner of the platform primitive.

### Hard CL-01 dependencies

- Identity & Access public actor contract.
- Role / Authority decision contract.
- Customer / Buyer Profile resolver for customer-track binding.
- Candidate and Professional profile owner-facts contracts.
- Consent proof/version contract before paid production enrollment.
- ComplianceHold decision contract for actions where holds apply.

### Downstream interfaces that may initially be stubbed

The following consumers need stable contract fixtures, not full product UIs, during core Track implementation:

- Transaction / Order;
- Booking & Calendar;
- Candidate Application & Resume Privacy;
- Professional Eligibility;
- Search / Public Visibility;
- Video Infrastructure;
- Digital Goods Access;
- Notification;
- Privacy / Data Erasure.

### Provider setup

Stripe Billing / Checkout / Customer Portal may be adapter-stubbed until CL-01 Feature 13. Live credentials and live callback side effects are **not** preconditions for catalog, entitlement resolution, or metering features.

### Mandatory architecture gates by slice

| Gate | Required before |
|---|---|
| U-CL01-24 free-plan representation | production default-free provisioning and free↔paid transitions |
| U-CL01-26 production entitlement catalog | activating production plan/entitlement keys |
| U-CL01-26 grant precedence | production SH-005 resolution over overlapping sources |
| U-CL01-28 subscription transition table | production paid subscription lifecycle |
| U-CL01-28 processed provider-event record | live provider webhook side effects |
| U-CL01-27 plan revision/effective history | material mutation of live production plans |
| U-CL01-26 typed value constraints | production plan mapping/grant writes |
| U-CL01-28 consent binding | paid enrollment/plan change |
| U-CL01-29 candidate usage period/refund rules | final Candidate Application quota integration |
| U-CL01-30 fee/commission calculation/snapshot rules | final Order pricing bridge |
| U-CL01-31 resolved by P01 / WA-R011 | implement early-access Booking bridge; no further product-choice gate |
| U-CL01-32 billing retention/anonymization | destructive privacy behavior |
| PR-CL01-04 / PR-TSE-02 provider ownership | Track-owned live Stripe Billing adapter |
| U-TSE-01/02 pricing/billing-interval schema | production catalog price mutation where affected |
| U-TSE-03 actor-profile/active-subscription DB constraints | production subscription/grant creation |
| U-TSE-04 usage semantic idempotency persistence | production SH-006 |
| U-TSE-05 grant-history evidence | high-risk manual grant administration if audit standard requires separate domain history |

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Track Schema Ownership, Invariants, and Contract Foundation

Establish the Track boundary in code and migrations so later features cannot depend on ambiguous profile binding, typed values, or neighboring ownership.

### Objective

Produce the validated domain vocabulary, Track-owned repository boundary, public contract types, and approved schema hardening needed for CL-01’s commercial-policy rail without activating unresolved product policy.

### Observable Result

- The application has one `track-subscription-entitlement` feature boundary.
- Track-owned model/enums are explicitly mapped to this Module.
- Runtime schemas reject malformed actor-track contexts and malformed entitlement values.
- Repositories access only Track-owned tables.
- Contract tests prove consumers can compile against provider-neutral Track DTOs without importing Prisma models or Stripe SDK types.
- Unresolved schema changes are represented as explicit gates, not silent assumptions.

### Cluster Build-Plan Link

Supports **CL-01 Feature 10 — Track Catalog and Free-Track Foundation** and its prerequisite ownership/schema work. It must not begin paid provider behavior from CL-01 Feature 13.

### Dependencies

- root database/migration foundation;
- current Track Prisma models/enums;
- module architecture Sections 3, 8, 9, 33, 35;
- SH-003 owner-facts contract as a planning dependency;
- root runtime-validation convention.

### In Scope

- create Track feature folder and stable contract namespace;
- define provider-neutral actor-track reference DTO;
- define typed entitlement value representation;
- define plan/subscription/grant/usage public DTOs;
- define repository interfaces for Track models;
- implement/read schema-level invariant checks that are already approved;
- propose/execute only schema constraints whose architecture decisions are resolved;
- add architecture tests or static checks preventing direct foreign-repository imports where the project supports them;
- document all unresolved schema mismatches from current Prisma.

### Out of Scope

- production entitlement keys;
- plan admin UI;
- grant precedence;
- paid subscriptions;
- Stripe SDK;
- usage mutation;
- Order/Booking/Search integration;
- Privacy destructive execution.

### Module-Owned Data

Reviewed/affected:

- `AccountTrack`;
- all Track enums;
- `TrackPlan`;
- `TrackPlanPrice`;
- `TrackEntitlementDefinition`;
- `TrackPlanEntitlement`;
- `TrackSubscription`;
- `TrackEntitlementGrant`;
- `TrackUsageEvent`;
- `TrackUsageCounter`;
- `TrackSubscriptionEvent`.

Potential migrations are allowed only for decisions already resolved, especially U-CL01-26/U-TSE-03/U-TSE-04 when ratified.

### Public Interfaces

Introduce stable type contracts for:

- `TrackActorRef`;
- `EntitlementKey`/typed value DTO;
- `EntitlementDecision`;
- `UsageAllowance` / `MeteredEntitlementReceipt`;
- `TrackSubscriptionView`;
- `TrackPlanView`;
- owner-facts ports required to validate Customer/Candidate/Professional bindings.

No business command needs to be production-active yet.

### Shared Operations Used

- **SH-003 `queryOwnerFacts` — each profile owner.** Invocation: actor-binding validation contract. Local policy: required profile fields. **Prohibited duplicate:** generic `profileRepository.ts`.
- **SH-015 `returnDecisionResult` — shared contract, proposed.** Invocation: decision DTO design if ratified. Local policy: Track reason codes. **Prohibited duplicate:** universal Track decision engine.
- **SH-032 `createRequestContext` / SH-034 `sanitizeTelemetryMetadata`** for contract-safe diagnostics if runtime paths are introduced. **Prohibited duplicate:** local request context/redactor.

### Domain Logic

- track→profile mapping is explicit;
- provider-native fields are isolated from domain contract;
- typed entitlement shape must have one discriminant and one compatible value;
- source evidence references use opaque IDs, not copied foreign records;
- `TrackUsageCounter` is labeled projection in repository/contract semantics;
- `TrackSubscriptionEvent` is labeled lifecycle history, not provider dedupe.

### Authorization / Compliance

No user-facing mutation. Any schema/admin debug operation remains developer/admin-only and does not bypass SH-002 when exposed through runtime.

### Database / Transaction Behavior

- validate existing unique/index behavior;
- add no active-subscription uniqueness or value checks until the related rulings are approved;
- establish migration tests from a clean database;
- do not change `AccountTrack` to add organization;
- do not use database defaults (`active`, `stripe`) as business-policy decisions.

### Events / Jobs

None required.

### Provider Integration

None. Provider types must not enter the new contracts.

### UI / Admin Surface

None required. A development-only contract fixture/harness is enough.

### Failure Behavior

- unresolved constraint → mark production mutation unavailable; do not create permissive fallback;
- foreign profile mismatch → typed validation failure;
- unsupported value type → validation failure;
- stale schema assumption → test failure rather than runtime inference.

### Tests

- schema/enum ownership test;
- migration validation;
- runtime schema tests for every entitlement value type;
- actor-track/profile binding fixture tests;
- contract serialization tests;
- architecture import-boundary tests where supported;
- regression test that no public Track contract imports Stripe types or neighboring Prisma repositories.

### Documentation Updates

Update this Module architecture and CL-01 architecture if any schema-owner ruling changes. Record migration decisions and unresolved items in progress tracker.

### Acceptance Criteria

- one Track feature boundary exists;
- provider-neutral public contracts exist;
- every Track-owned Prisma model is represented by owner repository/service design;
- known schema gaps are either migrated under approved decisions or explicitly gated;
- no neighboring source record is made Track-owned;
- test suite proves typed DTOs and track/profile validation.

### Exit Gate

Do not begin Feature 02 until:

- schema/migration tests pass;
- runtime contract tests pass;
- no direct foreign lifecycle repository has been introduced;
- U-CL01-26/U-TSE-03/U-TSE-04 remain visibly gated if unresolved;
- typecheck/lint/test/build checks for the slice pass.

---

## 02 Plan Catalog, Lifecycle, and Idempotent Seeding

Make the TrackPlan catalog real through owner commands/queries while keeping production policy keys and live-plan mutation behind their architecture gates.

### Objective

Implement source-owned draft/active/retired/archived plan behavior, price/entitlement configuration, safe list queries, and idempotent seeding.

### Observable Result

An authorized admin or developer fixture can:

- create/update a draft TrackPlan;
- configure approved TrackPlanPrice records;
- define entitlement definitions and plan mappings;
- activate/retire/archive only through valid Track commands;
- list plans through a stable public query;
- run the same seed manifest repeatedly without duplicates.

Production keys/plan versions remain disabled if U-CL01-26/U-CL01-27 are unresolved.

### Cluster Build-Plan Link

Directly implements the Module portion of **CL-01 Feature 10 — Track Catalog and Free-Track Foundation**.

### Dependencies

- Module Feature 01;
- SH-001/002/029/044;
- plan/value architecture gates U-CL01-26 and U-CL01-27;
- U-TSE-01/02 where pricing/cadence are affected.

### In Scope

- plan application service;
- draft plan CRUD through commands;
- price configuration/deactivation;
- entitlement-definition/mapping administration;
- plan lifecycle transition service;
- `listTrackPlans`;
- idempotent seed command/manifest;
- restricted admin/debug presentation if the project requires an observable runtime surface.

### Out of Scope

- assigning subscriptions in the catalog work; default-free assignment is covered separately by gated slice 02A;
- resolving overlapping grants;
- metering;
- paid checkout/provider callbacks;
- feature-specific premium behavior.

### Module-Owned Data

- TrackPlan;
- TrackPlanPrice;
- TrackEntitlementDefinition;
- TrackPlanEntitlement;
- TrackPlanStatus and catalog enums.

### Public Interfaces

- `listTrackPlans`;
- `createTrackPlan`;
- `updateDraftTrackPlan`;
- `configureTrackPlanPrice`;
- `deactivateTrackPlanPrice`;
- `defineTrackEntitlement`;
- `configurePlanEntitlement`;
- `activateTrackPlan`;
- `retireTrackPlan`;
- `archiveTrackPlan`;
- `seedTrackCatalog`.

Public exposure of mutations is admin-only, not cross-module general access.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity.** Invocation: admin actions. Local policy: Track target/action. **Do not build:** `trackAdminAuth.ts`.
- **SH-002 `authorizeResourceAction` — Role.** Invocation: before each mutation. Local policy: plan-admin action vocabulary. **Do not build:** plan role engine.
- **SH-029 `appendAuditEvent` — Audit.** Invocation: activation/retirement/material catalog change. Local policy: safe change summary. **Do not build:** local generic audit.
- **SH-044 `executeIdempotentCommand` — platform.** Invocation: seed/create/transition retry protection. Local policy: plan natural key/transition semantic key. **Do not build:** Track idempotency table.
- **SH-051/052/053 — shared concurrency/lifecycle.** Invocation: activation/retirement/stale edit. Local policy: plan transition graph and lock/version strategy. **Do not build:** generic state machine.
- **SH-046 `publishDomainEvent`** only if plan-published/retired events are actually consumed. Local policy: minimized Track event. **Do not build:** private event bus.
- **SH-080 `manageVersionedRules`** only after U-CL01-27 is resolved. Local policy: Track plan revision/effective dates.

### Domain Logic

- plan key unique within track;
- draft is editable; active/retired mutation follows approved historical-version policy;
- activation validates mappings and prices required by the billing model;
- a `free` plan does not become a Stripe subscription merely because TrackPlanPrice defaults exist;
- entitlement mapping must use the definition’s value type;
- plan track and entitlement track applicability must be compatible;
- retirement prevents new selection but keeps historical references;
- archived plan is not returned in normal selectable plan query.

### Authorization / Compliance

- admin-only plan mutations through SH-002;
- generic audit on material catalog changes;
- step-up is consumed later if root action matrix requires;
- plan existence does not prove subscription terms/recurring billing consent.

### Database / Transaction Behavior

- one transaction per aggregate mutation;
- plan activation reads all relevant mappings/prices under consistent state;
- use expected version/updatedAt or lock for conflicting admin edits;
- preserve `[track,key]` uniqueness;
- implement typed-value DB checks only after U-CL01-26;
- do not allow `monthlyPriceCents` and TrackPlanPrice to drift once U-TSE-01 is resolved.

### Events / Jobs

No scheduled job. Optional plan lifecycle outbox event.

### Provider Integration

No provider calls. Provider IDs are metadata references only.

### UI / Admin Surface

Minimal restricted admin catalog or seed/debug CLI is sufficient. If UI exists, it must show draft/active/retired/archived status and distinguish unresolved/non-production plans.

### Failure Behavior

- duplicate plan key → conflict;
- incompatible value → validation error;
- invalid transition → invalid-transition error;
- stale update → conflict;
- unresolved production catalog/version/value rule → plan remains draft/non-production;
- missing provider price does not cause provider lookup or make provider source truth.

### Tests

- plan transition matrix;
- typed mapping validation;
- track applicability;
- seed replay/idempotency;
- authorization/audit;
- stale admin edit;
- clean DB migration/seed;
- query hides inappropriate statuses;
- regression: no feature-local premium fields introduced.

### Documentation Updates

Any resolved production catalog/version/price decision updates Module + CL-01 architecture before code is enabled.

### Acceptance Criteria

- plan catalog is Track-owned and queryable;
- all mutations route through Track service;
- seed is idempotent;
- production activation is impossible while its required architecture decisions remain unresolved;
- consumers need no plan-table direct access.

### Exit Gate

Feature 02's catalog work passes only when catalog/domain/authorization/idempotency tests pass, seed replay is safe, no provider integration exists, and the applicable CL-01 Feature 10 catalog exit conditions are satisfied. Enabled free-track assignment additionally requires slice 02A below.

### Implementation Slice 02A — Default Free-Track Assignment (Architecture-Gated)

**Cluster coordination:** CL-01 Feature 10. This slice implements the existing `assignDefaultFreeTrack` command from Track architecture §10.6; it does not renumber later Module features.

**Architecture gate:** U-CL01-24 remains unresolved. Production assignment is disabled until its representation is approved and recorded in architecture. Applicable actor-binding, typed-value, precedence, and history gates remain intact. This slice selects neither TrackSubscription nor grants nor a combination, and introduces no persistence model or constraint.

#### Scope and trigger integration

- Implement the Track-owned `assignDefaultFreeTrack` command after the representation gate is resolved.
- Integrate the approved profile-owner actor-created handoff through its public command/event contract. Do not invent event names or read/write foreign profile repositories.
- Profile creation must not depend on a Track record or successful free-track assignment.
- Catalog seeding remains separate from assigning commercial access to an actor.
- Use approved owner contracts or labeled test fixtures before production wiring exists. Any additional representation-dependent prerequisite must be explicitly coordinated in CL-01 before enabling assignment; this slice does not silently pull later Module features forward.

#### Idempotency, concurrency, and shared boundaries

- SH-044 `executeIdempotentCommand` protects retries using the approved assignment identity and replay result; this plan does not choose a durable key or schema constraint.
- Concurrent or repeated delivery for the same logical assignment must not create duplicate commercial effects. Use the shared persistence concurrency mechanism with Track-owned validation and the approved representation.
- If the approved handoff is asynchronous, use SH-045 `deduplicateDomainEvent` and SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff`; do not create a local inbox, queue, or retry engine.
- Commit only Track-owned effects. Use SH-031 owner evidence and SH-046 publication only where the approved lifecycle/integration contract requires them; neither substitutes for the other.
- Return a gated/unavailable result while required architecture or owner facts are missing; do not infer free access from absent records or provider defaults.

#### Tests and exit gate

- Verify actor-created handoff to the existing command using approved owner-contract fixtures.
- Test repeated delivery, retry after interruption, concurrent assignment, wrong-track/mismatched actor facts, and owner-fact unavailability.
- Prove that retries/concurrency produce the approved single logical assignment result without duplicate effects, and that assignment failure does not undo or prevent profile creation.
- Verify unresolved U-CL01-24 keeps production assignment disabled and introduces no default storage representation.
- After adjudication, test the approved representation and its applicable integrity/precedence/history rules before production activation.
- This slice passes for production only when the required architecture gates and owner handoff are approved, the above tests pass, and CL-01 Feature 10's enabled free-track behavior is demonstrated. Catalog-only completion does not claim that assignment is implemented.


---

# Phase 2 — Effective Entitlement and Grant Behavior

## 03 Actor Binding and Effective Entitlement Resolution

Implement SH-005 as the one authoritative current-policy resolver.

### Objective

Given an actor track/profile and entitlement key, return one deterministic typed decision with evidence, without requiring consumers to inspect plans/subscriptions/grants directly.

### Observable Result

A contract test consumer can ask for a customer/candidate/professional entitlement and receive:

- allow/deny/warning/review/unavailable as appropriate;
- typed value;
- stable reason code;
- source plan/subscription/grant/definition references;
- evaluatedAt;
- expiry/recheck time.

Wrong-track/wrong-profile requests are denied deterministically.

### Cluster Build-Plan Link

Implements **CL-01 Feature 11 — Effective Entitlement Resolution and Grant Materialization**.

### Dependencies

- Features 01–02;
- Customer SH-004;
- Candidate/Professional SH-003 owner facts;
- SH-011 if holds affect the requested policy;
- **production gate U-CL01-26 grant precedence**;
- U-CL01-26 typed-value validation.

Fixture-only tests may exercise an explicitly non-overlapping single grant without claiming a production precedence policy.

### In Scope

- actor/profile binding validator;
- effective-time filtering;
- plan/subscription/grant source collection;
- grant precedence hook with production gate;
- typed value normalization;
- SH-005 public query;
- `resolveTrackAccessSummary` as composition over SH-005;
- stable Track decision reason codes.

### Out of Scope

- consuming usage;
- changing grants;
- Stripe lifecycle;
- business readiness;
- Order snapshots;
- Search writes.

### Module-Owned Data

Reads TrackPlan/TrackPlanEntitlement/TrackSubscription/TrackEntitlementGrant/TrackEntitlementDefinition. No source mutation required.

### Public Interfaces

- SH-005 `resolveEntitlement`;
- `resolveTrackAccessSummary`;
- narrow wrapper queries only when they call the same resolution engine.

### Shared Operations Used

- **SH-004 `resolveCustomerActor`** for customer binding. Do not rebuild buyer profile resolution.
- **SH-003 `queryOwnerFacts`** for Candidate/Professional bindings. Do not direct-read foreign profiles by default.
- **SH-011 `evaluateComplianceHold`** where hold policy applies. Do not add local blocked flags.
- **SH-015 `returnDecisionResult`** if ratified for response shape. Track still owns reason policy.
- **SH-032/033/034** safe request/logging. No user-level high-cardinality logging.

### Domain Logic

Evaluation order should be deterministic:

1. validate actor/profile binding;
2. resolve entitlement definition and track applicability;
3. gather eligible source subscription/grants;
4. remove not-started, expired, revoked, suspended, consumed-as-inapplicable sources;
5. apply approved precedence;
6. validate winning typed value;
7. apply Track-specific hold policy if relevant;
8. return decision/evidence/expiry.

No plan-name logic. No consumer context may silently override grant precedence.

### Authorization / Compliance

The resolver is a server capability. A consumer’s access to another user’s decision must be authorized according to its workflow; SH-005 itself must not become a public enumeration endpoint.

### Database / Transaction Behavior

Read-only consistent query. No lock required for ordinary read, but the result must include evaluatedAt/source versions so consumers understand it is a point-in-time decision.

### Events / Jobs

None.

### Provider Integration

None. Current provider references may be evidence only.

### UI / Admin Surface

Optional entitlement inspector for authorized admin/developer use, showing source evidence and reason code. It must not allow editing foreign lifecycle truth.

### Failure Behavior

- unknown key → not found/configuration error according to contract;
- wrong track/profile → deny;
- no effective source → deny;
- overlapping sources while precedence unresolved → `CONFIGURATION_UNRESOLVED`, not arbitrary winner;
- corrupted typed value → unavailable/configuration error;
- hold service unavailable on a hard-required gate → fail closed/unavailable.

### Tests

- each AccountTrack binding;
- wrong User/profile pair;
- not-started/expired/revoked/suspended grant;
- type validation;
- one-source allow;
- no-source deny;
- overlapping source behavior gated until precedence approval;
- evidence/expiry fields;
- direct-consumer Prisma access prohibited in contract fixtures.

### Documentation Updates

When U-CL01-26 is resolved, update architecture first with the precedence table and then add full precedence tests.

### Acceptance Criteria

- SH-005 is the single resolution engine;
- wrappers delegate to it;
- consumers can obtain all needed current policy evidence without raw Track table access;
- unresolved precedence cannot silently grant access.

### Exit Gate

All SH-005 contract/domain tests pass and the production resolver remains disabled for ambiguous overlaps until U-CL01-26 is approved.

---

## 04 Entitlement Grant Lifecycle and Materialization

Create Track-owned grant mutation behavior independently from provider-specific paid subscription processing.

### Objective

Implement explicit grant create/suspend/restore/revoke/expire/consume semantics and the internal materialization hook that later subscription lifecycle work can call.

### Observable Result

Authorized admin/system workflows can create and transition a TrackEntitlementGrant through approved states, and SH-005 immediately reflects those state changes. Expiration is idempotent and historical usage remains untouched.

### Cluster Build-Plan Link

Supports **CL-01 Feature 11** (effective grants) and prepares **CL-01 Feature 13** (subscription-driven grant materialization) without starting provider integration.

### Dependencies

- Feature 03;
- SH-002/011/014/029/044/051/053/055/046;
- U-CL01-26 for overlapping precedence;
- U-TSE-05 if a dedicated grant-history ledger is required before high-risk admin launch.

### In Scope

- manual/comped grant creation;
- grant state transitions;
- startsAt/expiresAt enforcement;
- internal `materializeSubscriptionGrants` interface with provider-independent inputs;
- expiration command/worker hook;
- lifecycle audit/domain-event behavior;
- SH-005 integration.

### Out of Scope

- Stripe webhooks;
- choosing default free-plan representation;
- temporary reward-grant activation until its execution/compensation contract is bound; SH-119 ownership is confirmed under Track (WA-R002);
- rewriting usage history;
- consumer business lifecycle.

### Module-Owned Data

TrackEntitlementGrant; optional Track-owned grant history only if U-TSE-05 is resolved; TrackSubscriptionEvent is not misused as generic grant history.

### Public Interfaces

- `createManualEntitlementGrant`;
- `suspendEntitlementGrant`;
- `restoreEntitlementGrant`;
- `revokeEntitlementGrant`;
- owner/internal `expireEntitlementGrant`;
- internal `materializeSubscriptionGrants`.

### Shared Operations Used

- **SH-001/002** actor + authority for admin calls.
- **SH-011** hold gate.
- **SH-014** step-up if policy requires.
- **SH-029** generic audit.
- **SH-044** command idempotency.
- **SH-051/053** aggregate lock/transition plumbing.
- **SH-055** deadline expiration dispatcher.
- **SH-046** factual entitlement-change event.
- **SH-041** Notification request only for approved user-facing transitions.

No local scheduler, audit ledger, MFA, or Notification provider.

### Domain Logic

- active grant must have valid actor/track binding and typed value;
- startsAt in future does not grant current access;
- expiresAt in past cannot create active effective access;
- suspend is reversible only under approved grant policy;
- revoke/expire/consume are terminal for the record under PR-TSE-03;
- `consumed` is valid only for one-shot semantics;
- subscription materialization receives approved plan mappings and does not inspect provider payloads;
- downgrade/recalculation never deletes previous usage events.

### Authorization / Compliance

Manual/comped grants are privileged operations. Actor, authority, hold, and optional step-up must be enforced server-side. Audit the grant source/reason using safe metadata.

### Database / Transaction Behavior

- one grant aggregate transition per transaction;
- lock grant ID for conflicting transitions;
- create operation idempotent on supplied semantic key;
- validate profile/User/track consistency;
- add DB value/profile constraints only under approved migrations.

### Events / Jobs

- entitlement grant changed event via outbox;
- expiration work registered through shared scheduler/queue;
- no recurring custom cron.

### Provider Integration

None.

### UI / Admin Surface

A restricted grant inspector/editor may be built if needed for observable admin behavior. It must not expose raw provider data or direct database status editing.

### Failure Behavior

- unauthorized → deny;
- invalid state → conflict;
- expired deadline replay → return current terminal state;
- overlapping grant with unresolved precedence → grant may be persisted only if approved admin semantics allow, but SH-005 production effective result remains unresolved/fail-closed;
- notification failure after commit → retry side effect.

### Tests

- state transition tests;
- future start/expiry;
- idempotent expiration;
- concurrent suspend/revoke;
- SH-005 response after state changes;
- audit/outbox contract;
- no usage-event deletion;
- no provider dependency.

### Documentation Updates

Ratify/change PR-TSE-03 and U-TSE-05 before high-risk production admin surface if implementation evidence requires it.

### Acceptance Criteria

- all grant writes occur through Track commands;
- lifecycle is transaction-safe;
- current decision changes without consumer-local state;
- expiration uses shared scheduler;
- historical usage is preserved.

### Exit Gate

Grant lifecycle tests, authorization/audit tests, expiration replay tests and SH-005 integration pass.

---

# Phase 3 — Metered Entitlement Consumption

## 05 Atomic Usage Metering and Rebuildable Counter Projection

Implement SH-006 end-to-end.

### Objective

Ensure a metered business action cannot exceed its approved allowance under concurrency and produces one immutable usage proof plus a rebuildable counter.

### Observable Result

A trusted consumer can:

1. preflight with `checkUsageAllowance`;
2. execute SH-006 with a semantic business-event key;
3. receive a usage receipt;
4. replay the same request and receive the same result;
5. run concurrent requests at the limit without exceeding it;
6. rebuild the counter from usage events and get the same effective count.

### Cluster Build-Plan Link

Implements the Track portion of **CL-01 Feature 12 — Atomic Metered Entitlement Usage and Counter Projection**.

### Dependencies

- Feature 03;
- SH-005/006;
- SH-044/051/057;
- SH-115 projection mechanism;
- U-TSE-04 semantic idempotency persistence;
- policy-specific gates such as U-CL01-29 before final Candidate Application activation.

### In Scope

- `checkUsageAllowance`;
- SH-006 `consumeMeteredEntitlement`;
- usage period calculation hook;
- immutable TrackUsageEvent repository;
- atomic TrackUsageCounter mutation;
- usage receipt;
- counter rebuild operation/worker;
- mismatch telemetry.

### Out of Scope

- JobApplication creation;
- Booking creation;
- buyer fee/commission snapshot calculation;
- generic analytics;
- editing/deleting usage events;
- unapproved refund/reversal semantics.

### Module-Owned Data

TrackUsageEvent; TrackUsageCounter; reads entitlement/grant/subscription source.

### Public Interfaces

- `checkUsageAllowance`;
- SH-006 `consumeMeteredEntitlement`;
- internal/admin `rebuildTrackUsageCounters`.

### Shared Operations Used

- **SH-005** authoritative allowance source.
- **SH-006** capability implemented by this feature.
- **SH-044** semantic idempotency.
- **SH-051 or SH-057** serialize/atomically increment bounded counter.
- **SH-115** rebuild projection.
- **SH-047/048/038** durable rebuild/retry/telemetry.
- **SH-046** usage event only if external consumer needs factual publication.
- **SH-037** counter mismatch/worker failure.

### Domain Logic

Canonical transaction:

```text
validate consumer request
→ resolve SH-005 entitlement
→ derive approved period
→ claim semantic idempotency
→ lock/read counter
→ verify used + quantity <= limit
→ append TrackUsageEvent
→ increment/update TrackUsageCounter
→ persist idempotent receipt
→ commit
```

The consumer supplies `targetType/targetId` only as evidence and determines when the business event counts. Track owns quantity/limit/period accounting.

### Authorization / Compliance

- end users cannot call a generic “increment my usage” endpoint;
- consumer workflow must authenticate/authorize its own business action;
- Track accepts a trusted server/system context or an authorized direct command according to root design;
- privacy-safe metadata only.

### Database / Transaction Behavior

- event append + counter update + idempotency result are one atomic effect;
- lock key uses entitlement/track/user/period, refined if U-TSE-03 requires profile-specific uniqueness;
- counter cannot go below zero or exceed approved limit;
- no in-memory mutex;
- rebuild writes projection only.

### Events / Jobs

- optional `MeteredEntitlementConsumed` fact after commit;
- rebuild worker through shared queue;
- period rollover is not destructive reset.

### Provider Integration

None.

### UI / Admin Surface

Optional read-only usage summary showing used/limit/period and clearly labeling it derived from usage proof.

### Failure Behavior

- limit exceeded → deterministic denial, no event/counter increment;
- duplicate same fingerprint → prior receipt;
- duplicate key/different fingerprint → idempotency conflict;
- serialization conflict → bounded retry;
- unresolved period policy → unavailable;
- counter mismatch → alert/rebuild; source events remain untouched.

### Tests

- 20+ concurrent requests around exact limit;
- duplicate replay;
- duplicate key/different payload;
- period boundaries with controlled clock;
- expired/revoked entitlement;
- counter rebuild equals event sum;
- simulated worker retry;
- no TrackUsageEvent update/delete code path;
- consumer contract proving no JobApplication/Booking source mutation.

### Documentation Updates

When U-CL01-29 or another quota policy is resolved, add its period/reversal rules to architecture before consumer activation.

### Acceptance Criteria

- no race exceeds limit;
- one semantic event produces one usage proof;
- projection rebuild is deterministic;
- no destructive reset exists;
- SH-006 is the only canonical metering API consumers need.

### Exit Gate

Concurrency/idempotency/rebuild tests must pass under the project’s database integration environment before any consumer uses SH-006 for production gating.

---

# Phase 4 — Paid Subscription Lifecycle and Billing Provider

## 06 Paid Track Subscription Commands and Stripe Billing Adapter

Activate paid Track subscription behavior only after every mandatory architecture gate is approved.

### Objective

Turn authorized checkout/change/cancel intents and verified Stripe Billing events into authoritative TrackSubscription/grant transitions without making Stripe, a redirect, or Payment/Payout/Tax the owner of Track entitlement truth.

### Observable Result

When all gates are resolved:

- user can initiate approved plan enrollment/change/cancel;
- provider session creation does not itself grant access;
- a verified unique provider event changes TrackSubscription only through Track transition policy;
- grants materialize/suspend/revoke according to approved policy;
- duplicate/out-of-order/unknown events cannot corrupt state;
- SH-005 reflects the resulting current entitlement;
- reconciliation can repair missed provider events safely.

Before gates resolve, adapter contract/provider tests may pass but live callbacks cannot mutate production Track state.

### Cluster Build-Plan Link

Implements **CL-01 Feature 13 — Paid Track Subscription Lifecycle and Stripe Billing Adapter**.

### Dependencies

Module Features 02–05 plus mandatory:

- U-CL01-24;
- U-CL01-26;
- U-CL01-28 (subscription transitions, provider receipts, and consent binding);
- U-CL01-27;
- U-CL01-32;
- PR-CL01-04 / PR-TSE-02;
- U-TSE-03 where active subscription/profile constraints are required;
- Consent SH-008/009;
- Hold/step-up policy;
- SH-059–062.

### In Scope

- provider-neutral TrackBillingProviderPort;
- Stripe Billing/Checkout/Customer Portal adapter;
- start checkout/change/cancel/portal commands;
- provider route handler that delegates after SH-059;
- owner-specific processed-event record after U-CL01-28;
- Track subscription transition service after U-CL01-28;
- subscription-driven grant materialization;
- TrackSubscriptionEvent append;
- reconciliation worker;
- user/admin current subscription query/surface;
- notification/search effects after source commit.

### Out of Scope

- Payment/Payout/Tax ledger;
- Order payment status;
- payout/tax;
- storing raw Stripe payload as domain truth;
- feature-specific business actions;
- local webhook/retry infrastructure.

### Module-Owned Data

TrackSubscription; TrackEntitlementGrant; TrackSubscriptionEvent; provider price references; new Track-specific processed-event record only after approved architecture/migration.

### Public Interfaces

- `startTrackSubscriptionCheckout`;
- `changeTrackSubscriptionPlan`;
- `cancelTrackSubscription`;
- `openTrackBillingPortal`;
- `getCurrentTrackSubscription`;
- internal `applyTrackBillingProviderEvent`;
- `reconcileTrackBillingState`.

### Shared Operations Used

- **SH-001/002** user/admin actor and authorization.
- **SH-008/009** exact consent proof/version.
- **SH-011** holds.
- **SH-014** step-up where required.
- **SH-029** audit.
- **SH-044/051/052/053** idempotent concurrent lifecycle changes.
- **SH-046** Track fact publication.
- **SH-041** Notification intent.
- **SH-047/048** provider/reconcile retries.
- **SH-064 `authorizeExternalProviderConnection` — Confirmed; owner: provider-owning Module.** Invocation: hosted checkout/portal initiation. Reuse state/nonce, redirect allowlists, scoped permissions, callback validation, and provider-reference lifecycle. Track retains plan/price selection, commercial eligibility, Stripe-specific translation, and TrackSubscription lifecycle. **Prohibited duplicate:** a Track-local replacement for hosted-flow security mechanics. Integration tests cover rejected redirect/state/callback input and confirm that initiation alone does not activate a subscription.
- **SH-059** raw webhook signature verification.
- **SH-060** provider-event dedupe; local truth is Track-specific.
- **SH-061** Track adapter status mapping.
- **SH-062/063** provider reconciliation/snapshot mechanics.
- **SH-037/038/039** operational failure/queue/health.
- **SH-091** Search refresh when candidate boost changes.

Prohibited duplicates include Track-specific generic webhook security, Payment’s ProcessedStripeEvent clone without ruling, local retry engine, and direct Notification/Search providers.

### Domain Logic

- selected plan/price must be active and track-compatible;
- exact required consent proof is checked before provider session/plan-change action as approved;
- browser redirect never establishes active state;
- provider event identity is claimed before side effects;
- event maps through explicit adapter mapping version;
- Track transition table rejects invalid/out-of-order transitions according to U-CL01-28 ruling;
- transition + TrackSubscriptionEvent + grant materialization + outbox occur transactionally where feasible;
- downgrade/cancel preserves usage/history;
- unknown provider status results in review/unsupported, never active;
- general money movement remains external.

### Authorization / Compliance

- self-service only for own User/track/profile unless admin authority;
- recurring billing/terms/plan-change consent;
- hold gate;
- step-up if action matrix requires;
- material admin/reconciliation actions audited;
- billing retention follows U-CL01-32.

### Database / Transaction Behavior

- one active relevant subscription per actor track according to approved constraint;
- provider event uniqueness `(provider,eventId)`;
- provider callback claim + domain effect exactly once/effectively once;
- subscription lock on user command/provider transition conflict;
- expected event/order policy for out-of-order callbacks;
- no default `active` status used as lifecycle shortcut.

### Events / Jobs

- subscription change outbox;
- grant/effective entitlement change outbox;
- Notification request;
- Search refresh for candidate boost changes;
- reconciliation worker;
- grant/subscription expiration worker;
- all through shared infrastructure.

### Provider Integration

Stripe-specific implementation:

- Checkout session creation;
- Billing subscription operations;
- Customer Portal if product requirements approve;
- raw webhook verification through SH-059;
- normalized status/error mapping;
- fetch state for reconciliation.

Provider SDK types stop at adapter boundary.

### UI / Admin Surface

Genuine surfaces may include:

- plan selection;
- subscription status/account page;
- cancel/change action;
- safe trial/past-due/incomplete presentation;
- restricted provider/reconciliation inspector with opaque refs.

Do not build a payment ledger UI here.

### Failure Behavior

- forged signature → reject, no Track write;
- duplicate event → prior result/no second write;
- out-of-order event → approved policy or review, never blind overwrite;
- unknown status → unsupported/review;
- provider unavailable before local state mutation → user sees retry/unavailable;
- provider session created but local follow-up fails → reconciliation, not fake active state;
- local source committed but Notification/Search fails → source remains; outbox retries;
- consent/hold missing → provider mutation is not initiated where required.

### Tests

- provider adapter unit tests;
- signature contract tests;
- duplicate provider event integration;
- out-of-order event matrix;
- full approved subscription transition matrix;
- user change vs provider event concurrency;
- reconciliation after dropped event;
- grants reflected in SH-005;
- consent/hold/step-up;
- provider outage;
- no Payment/Payout/Tax ledger mutation;
- no raw Stripe type in public contracts.

### Documentation Updates

Before live activation, all named U-CL01 decisions must be marked resolved in CL-01 and Module architecture. Record provider mapping version and processed-event schema.

### Acceptance Criteria

- live provider callback cannot mutate Track until all gates are resolved;
- once enabled, verified unique events are the only provider callback path to Track transition;
- redirect does not grant access;
- general financial ownership remains outside Track;
- reconciliation is replay-safe.

### Exit Gate

The feature cannot pass for production until every mandatory architecture gate is resolved, provider signature/dedupe/ordering/reconciliation suites pass, and CL-01 Feature 13 exit conditions are satisfied.

---

# Phase 5 — Track-Owned Workers and Side Effects

## 07 Expiration, Reconciliation, Search Refresh, and Notification Effects

Complete Track’s asynchronous owner responsibilities without creating local infrastructure or downstream source truth.

### Objective

Make Track state self-maintaining over time and ensure committed entitlement changes propagate safely to Search/Notification/ops through canonical interfaces.

### Observable Result

- expired grant/subscription deadlines eventually apply the correct idempotent Track transition;
- usage counters can be rebuilt;
- billing state is periodically/on-demand reconciled when provider integration is active;
- candidate boost changes issue Search refresh requests;
- approved subscription/grant changes request Notification;
- failed downstream effects are retry-visible without rolling back Track truth.

### Cluster Build-Plan Link

Completes asynchronous work associated with **CL-01 Features 12–13** and prepares cross-Cluster contract proof in **CL-01 Phase 4 / Features 14–16**.

### Dependencies

- Features 04–06 as applicable;
- SH-041/046/047/048/055/062/091/115;
- Search and Notification contracts/test doubles;
- Ops interfaces.

### In Scope

- expiration worker handler;
- usage counter rebuild job;
- billing reconciliation handler;
- outbox consumers/dispatch for Search refresh;
- Notification request construction;
- safe job telemetry/health.

### Out of Scope

- queue engine;
- Search document schema/Typesense;
- Notification templates/providers;
- Privacy workflow;
- new business lifecycle.

### Module-Owned Data

TrackSubscription, TrackEntitlementGrant, TrackUsageEvent/Counter, TrackSubscriptionEvent; no foreign writes.

### Public Interfaces

No new broad public API. Internal job handlers call existing Track commands. Search/Notification are outbound contracts.

### Shared Operations Used

- **SH-055** deadline expiration dispatcher.
- **SH-047/048** durable queue/retry.
- **SH-038** queue telemetry.
- **SH-062** provider reconciliation.
- **SH-115** usage counter projection rebuild.
- **SH-091** Search refresh.
- **SH-041** Notification.
- **SH-046/045** outbox/inbox.
- **SH-037/039** failures/health.

### Domain Logic

- workers never write statuses directly; they call Track owner commands;
- expiration command checks current state/deadline again at execution time;
- Search refresh occurs only if effective candidate boost output changed, not on irrelevant record touch;
- Notification trigger uses committed Track fact and stable idempotency key;
- counter rebuild is source-event deterministic;
- provider reconciliation respects approved transition policy.

### Authorization / Compliance

Workers run as trusted system actors with scoped operation identity. Admin-triggered manual reconciliation still requires SH-001/002 and audit.

### Database / Transaction Behavior

Source transition remains in Track service transaction; outbox follows source commit. Worker retries must not produce duplicate events/grants/counters.

### Events / Jobs

This feature is job-heavy. Every job defines:

- typed payload;
- semantic idempotency key;
- max/retry classification;
- dead-letter/manual-review condition;
- correlation ID;
- business completion meaning;
- safe telemetry.

### Provider Integration

Only reconciliation handler calls provider adapter when Feature 06 is active.

### UI / Admin Surface

Optional ops inspector for failed/review-required Track jobs/provider reconciliation, relying on Ops records. It cannot edit source truth directly.

### Failure Behavior

- stale expiration job → no-op/current result;
- Search unavailable → retry request;
- Notification unavailable → retry request;
- reconciliation unknown status → manual review;
- counter rebuild mismatch → projection repair + ops signal;
- dead-letter → visible operational state, no invented Track status.

### Tests

- clock-controlled expiration;
- duplicate job replay;
- dead-letter classification;
- Search request exactly once/effectively once;
- Notification idempotency key;
- counter rebuild;
- reconciliation retry;
- source commit survives downstream outage.

### Documentation Updates

Update provider/job runbook context and progress tracker; architecture only if a new business transition is required.

### Acceptance Criteria

- no direct worker status writes;
- downstream outages do not corrupt Track truth;
- Search/Notification called only through canonical interfaces;
- all jobs replay safely.

### Exit Gate

Job replay, side-effect retry, Search/Notification contract and counter-rebuild tests pass.

---

# Phase 6 — Module Integration

## 08 Cross-Module Commercial Policy Contract Proof

Prove the Track rail works with its most important consumers while preserving every consumer’s source truth.

### Objective

Demonstrate through contract/integration tests that downstream Modules can use Track current policy, metering, and evidence without direct Track Prisma access or ownership theft.

### Observable Result

The integration harness proves at least these workflows:

```text
Customer fee waiver decision → Order-owned snapshot
Professional commission decision → Order-owned snapshot
Candidate application allowance → Track usage proof + Candidate-owned JobApplication
Candidate search boost change → Search refresh request
Customer priority policy → Booking-owned scheduling result
Professional entitlement → Professional Eligibility composition
Live-streaming/digital perk → delivery owner grant, not Track grant reuse
```

### Cluster Build-Plan Link

Supports **CL-01 Phase 4 — Cross-Cluster Contract Proof**, specifically the Track bridges included in CL-01 Features 14–16.

### Dependencies

- Features 03–07;
- downstream public contracts or versioned fixtures;
- U-CL01-29/U-CL01-30/U-CL01-31 for final policy-specific production behavior;
- SH-109 snapshot pattern;
- SH-091 Search refresh.

### In Scope

- typed consumer adapters/facades if needed;
- `quoteOrderTrackPolicy`;
- `evaluatePriorityScheduling`;
- `evaluateCandidateSearchBoost`;
- `evaluateProfessionalSellingEntitlement`;
- `authorizeLiveStreaming`/other narrow wrappers only if contract value exists;
- integration tests using public contracts.

### Out of Scope

- creating Order/Booking/JobApplication/Search documents/video rooms/download grants;
- Payment/payout/tax;
- feature UIs.

### Module-Owned Data

Read current Track source; SH-006 may write usage for metered consumer actions. No foreign data writes.

### Public Interfaces

Finalize consumer-facing decisions listed above.

### Shared Operations Used

- **SH-005/006** current policy/metering.
- **SH-003/004** actor-owner facts.
- **SH-016** professional readiness is consumed by the consumer, not merged into Track.
- **SH-091** Search refresh.
- **SH-109 `snapshotExternalDecision`** is executed by consuming domain owner. Track returns evidence only.
- **SH-025 `authorizeOrderEntitlement`** may be consumed by delivery Modules; Track does not replace it.

### Domain Logic

#### Order bridge

`quoteOrderTrackPolicy` returns buyer fee waiver and professional commission value/evidence. Order applies U-CL01-30-approved calculation and persists its historical snapshot. A later Track change does not rewrite the Order.

#### Candidate application bridge

Candidate workflow authenticates/authorizes its JobApplication creation, then calls SH-006 when the business event counts. Transaction ordering must prevent quota loss without a corresponding accepted business event according to the final integration design. U-CL01-29 controls reversal/refund semantics.

#### Search bridge

Track returns boost; Search composes boost with privacy/readiness/moderation. Track change calls SH-091; it never writes SearchUpsertEvent/Typesense.

#### Booking bridge

Track returns early-access eligibility/evidence under approved WA-R011. Booking owns release-time enforcement and slot/hold/booking truth.

#### Professional readiness bridge

Professional Eligibility combines Track commercial entitlement with verification/healthcare/financial/hold facts. Track does not return a global “professional can sell” result.

#### Delivery bridge

Track live/digital perk is a gate. Video/Digital owns temporary/playback/download grant truth.

### Authorization / Compliance

Each consumer retains its own authorization/readiness/consent gates. Track decisions must not be used as generic authorization.

### Database / Transaction Behavior

Cross-module tests should use public service contracts. If a same-database transaction is later required for SH-006 + consumer write, architecture must explicitly define ownership/transaction coordination; do not solve by allowing cross-module repositories.

### Events / Jobs

Search refresh and consumer events only through existing canonical mechanisms.

### Provider Integration

None beyond already active Feature 06.

### UI / Admin Surface

None required.

### Failure Behavior

- Track unavailable on hard commercial gate → consumer fails closed/unavailable;
- snapshot write failure → consumer transaction does not pretend historical decision was stored;
- Search refresh failure → retry;
- usage consumed but consumer source mutation fails → follow approved U-CL01-29/integration compensation policy; do not invent a reversal.
- unresolved U-CL01-30 → dependent Order policy disabled; U-CL01-31 is resolved by WA-R011, with early access gated on configuration and verified implementation.

### Tests

- Order contract test proving snapshot is foreign-owned;
- Track change after Order snapshot does not change snapshot;
- Candidate quota + JobApplication contract;
- Search refresh/no direct Typesense;
- Booking priority/no Booking write from Track;
- Professional Eligibility composition;
- Video/Digital grant separation;
- architecture test for no direct Track Prisma in consumer fixture and no direct foreign Prisma in Track.

### Documentation Updates

Resolve U-CL01-29/U-CL01-30; implement and validate the approved U-CL01-31 / WA-R011 contract in Track and Booking before production integration.

### Acceptance Criteria

Every major consumer can obtain the necessary Track answer through a stable public contract, and no consumer needs to mutate or reconstruct Track truth.

### Exit Gate

All cross-module contract tests pass; unresolved consumer-specific policy remains disabled; ownership sweep shows no duplicated current commercial policy.

---

# Phase 7 — Privacy, Compliance, Audit, and Support Integration

## 09 Track Privacy Executor, Retention, Audit Completeness, and Admin Support

Implement Track’s owner-side privacy obligations and prove that commercial evidence, generic audit, sensitive access, and operational evidence remain distinct.

### Objective

Allow Privacy/Admin/Ops to safely enumerate, retain/anonymize/erase/revoke Track-owned data and inspect Track state through controlled interfaces without taking over Track lifecycle or creating a second source of truth.

### Observable Result

- Privacy test harness enumerates Track subject data.
- A Privacy instruction returns an idempotent typed execution result.
- Retention-required records are retained rather than deleted.
- Approved anonymization works without breaking required relations.
- Material Track admin actions have AuditEvent coverage.
- Sensitive provider-reference access is logged where policy requires.
- Support can inspect safe source state and provider/reconciliation references without direct DB edits.

### Cluster Build-Plan Link

Supports CL-01’s privacy/guardrail integration in **CL-01 Feature 16** and hardening requirements in **CL-01 Feature 18**.

### Dependencies

- prior Track source features;
- SH-095–098;
- SH-029/030;
- U-CL01-32 before destructive billing evidence behavior;
- Notification/Ops contracts;
- provider deletion/detachment interface if required by approved retention policy.

### In Scope

- `enumerateSubjectData`;
- Track `executePrivacyInstruction`;
- retention-fact adapter;
- approved anonymization mappings;
- export serializer;
- admin/support safe queries;
- audit coverage matrix;
- sensitive-access coverage where applicable;
- provider reference deletion/detachment execution only when approved.

### Out of Scope

- PrivacyRequest/DataErasureJob/DataErasureTarget lifecycle;
- retention exemption source table;
- generic admin case workflow;
- provider-wide account deletion unrelated to Track;
- hard-delete before U-CL01-32.

### Module-Owned Data

Potentially all Track models, with special retention attention to TrackSubscription, TrackUsageEvent and TrackSubscriptionEvent.

### Public Interfaces

- SH-096 `enumerateSubjectData` implementation;
- SH-095 `executePrivacyInstruction` implementation;
- SH-097 Track retention facts;
- safe admin/support queries.

### Shared Operations Used

- **SH-095–098** Privacy protocol.
- **SH-029** generic AuditEvent.
- **SH-030** sensitive access where classification requires.
- **SH-044/047/048** idempotent/retryable privacy effects.
- **SH-037** provider/worker failure.
- **SH-070 `deleteProviderResource`** only if Track provider resource deletion is approved.
- **SH-041** user notification only if Privacy/Track policy requires and Privacy permits.

### Domain Logic

- product cancellation ≠ privacy erasure;
- current access may be revoked while historical billing evidence is retained;
- retained rows should minimize/anonymize personal data according to approved mapping;
- export returns Track source records, not generic Audit/Ops records owned elsewhere;
- Privacy parent completion is determined by Privacy, not Track.

### Authorization / Compliance

Only Privacy-authorized system workflow invokes destructive executor. Manual retry/support views require Role and potentially step-up. Sensitive provider IDs are minimized.

### Database / Transaction Behavior

- target execution is idempotent;
- retain/erase/anonymize outcome persisted only where owner record needs mutation; Privacy owns target status;
- no dangling required foreign keys;
- hard delete unavailable until retention decision is approved.

### Events / Jobs

Long-running provider deletion or bulk anonymization may use SH-047/048. Track returns partial/retryable/terminal result to Privacy according to protocol.

### Provider Integration

Provider resource deletion/detachment only through approved Track billing adapter/shared deletion contract; already-absent is idempotent success where protocol defines.

### UI / Admin Surface

No standalone Privacy UI. Restricted support view may show Track state, audit links and reconciliation status with safe opaque refs.

### Failure Behavior

- retention required → return retained;
- provider unavailable → retryable result;
- provider object absent → approved idempotent success;
- duplicate instruction → same result/no repeated destructive effect;
- unresolved retention → deny destructive action/unavailable;
- audit failure behavior follows root guarantee; do not fake source transition.

### Tests

- subject enumeration;
- export serializer;
- retain vs erase/anonymize;
- duplicate executor invocation;
- provider absent/retryable/terminal;
- audit coverage matrix;
- sensitive-access logging;
- no local PrivacyRequest/DataErasureJob;
- retained evidence relations valid.

### Documentation Updates

Resolve U-CL01-32 and record exact field retention/anonymization map before destructive production path.

### Acceptance Criteria

Track participates in Privacy through owner executor only; required evidence is preserved; no generic privacy/audit/ops truth is duplicated.

### Exit Gate

Privacy, retention, audit and sensitive-access test suites pass. Production erase remains disabled if U-CL01-32 is unresolved.

---

# Phase 8 — Module Hardening and Production Verification

## 10 Concurrency, Replay, Provider Degradation, Reconciliation, and Production Readiness

Exercise the Module as a production commercial-policy rail under race, retry, provider failure, stale configuration, migration, privacy, and high-volume read conditions.

### Objective

Prove Track maintains its invariants under realistic production failure and concurrency conditions and that every production-enabled unresolved decision has been explicitly resolved.

### Observable Result

A production-readiness test/report can demonstrate:

- SH-005 remains deterministic under load;
- SH-006 cannot overspend quota;
- subscription/provider event races cannot corrupt lifecycle;
- duplicate callbacks/jobs/commands are harmless;
- provider outage has documented behavior;
- counter/provider reconciliation repairs drift safely;
- Track logs/metrics are privacy-safe;
- destructive privacy paths obey retention;
- migrations/backfills are restartable;
- no duplicated current policy exists in consumers.

### Cluster Build-Plan Link

Implements the Track-specific portion of **CL-01 Feature 17 — Backfills, Reconciliation, and Migration Safety** and **Feature 18 — Security, Privacy, Concurrency, and Production Readiness Hardening**.

### Dependencies

All production-enabled Module features and every unresolved architecture item that their behavior depends on.

### In Scope

- concurrency stress suite;
- idempotency/replay suite;
- provider chaos/degradation tests;
- reconciliation/backfill restart tests;
- query/index performance;
- migration safety;
- security/secret logging scan;
- privacy/retention verification;
- audit/observability completeness;
- contract compatibility/version tests;
- production health checks/runbook;
- duplicate-ownership sweep.

### Out of Scope

- new plan/product features;
- organization fourth track;
- new provider;
- redesign of downstream lifecycles;
- convenience refactors that alter ownership.

### Module-Owned Data

All Track models and any approved new provider-event/version records.

### Public Interfaces

No new business interface should be introduced merely for hardening. Health/admin diagnostics may be added through approved Ops/admin contracts.

### Shared Operations Used

All relevant canonical operations already integrated, especially:

- SH-001/002/008/011/014;
- SH-029/030/032–039;
- SH-044–055/057;
- SH-059–063;
- SH-091;
- SH-095–098;
- SH-109/115.

Hardening verifies reuse; it does not replace them.

### Domain Logic

Prove invariants from `module-architecture.md` Section 33. Particular focus:

- plan version/history;
- grant precedence;
- exact track/profile binding;
- subscription transition ordering;
- metering boundaries;
- historical snapshot separation;
- billing retention.

### Authorization / Compliance

Perform final matrix review for:

- self-service vs admin;
- manual grants;
- plan publishing;
- reconciliation;
- provider inspection;
- step-up;
- consent;
- holds;
- Privacy destructive operations;
- sensitive access.

### Database / Transaction Behavior

Stress:

- quota boundary;
- subscription row/aggregate lock;
- provider event unique claim;
- stale plan edit;
- expiration/revoke;
- rebuild vs live metering;
- privacy vs provider update.

Review indexes for SH-005/006 hot paths and provider reconciliation. No destructive migration without rollback/backfill proof.

### Events / Jobs

- duplicate outbox delivery;
- consumer inbox replay;
- dead-letter and re-drive;
- delayed provider event;
- expiration backlog;
- counter rebuild resume;
- reconciliation cursor restart.

### Provider Integration

Chaos cases:

- Stripe unavailable on checkout;
- delayed webhook;
- duplicate webhook;
- out-of-order webhook;
- unknown status;
- reconciliation mismatch;
- provider rate limit;
- portal failure.

Each has documented user/system result and no “generic 500 then hope” path.

### UI / Admin Surface

Verify any plan/subscription/support UI handles:

- loading;
- denied;
- consent required;
- past due/incomplete;
- unavailable/provider degraded;
- stale action conflict;
- manual review;
- safe empty state.

Do not add UI solely to satisfy this phase.

### Failure Behavior

Every failure class maps to one of:

- deny;
- unavailable/retry;
- conflict/stale;
- pending;
- manual review;
- committed source + retried side effect.

No ambiguous provider error leaks to consumers.

### Tests

- full unit/contract/integration suite;
- DB concurrency stress;
- provider signature/dedupe/order/reconciliation;
- authorization/step-up/consent/hold;
- privacy/retention;
- event/job replay;
- migration from clean DB and representative legacy Track state;
- backfill restart;
- performance/load SH-005 and SH-006;
- secret/PII logging scan;
- production build.

### Documentation Updates

- update progress tracker;
- record all final architecture rulings;
- update provider runbook/library docs if repository uses one;
- update shared-ops registry only if a genuinely new canonical operation was approved;
- do not change architecture merely to match accidental implementation.

### Acceptance Criteria

Track is production-ready only when:

- every enabled production behavior has no unresolved architecture dependency;
- no lifecycle has two owners;
- all canonical shared operations are reused;
- provider callbacks are verified/deduped/translated/reconciled;
- metering satisfies atomic/idempotent invariants;
- privacy/retention paths are explicitly approved/tested;
- Search/Notification/Audit/Ops remain support rails;
- consumer snapshots remain consumer-owned;
- no secrets/raw provider payloads leak;
- all critical contract/E2E workflows pass.

### Exit Gate

All Track unit, contract, database, authorization, provider, privacy, concurrency, performance, lint/typecheck/build checks pass, and the progress tracker/architecture/build plans agree on the implemented state.

---

# Module Integration Phase

Phase 6 is the explicit integration phase for this Module. Its purpose is **contract proof, not ownership transfer**.

Minimum public-boundary proofs:

```text
Track → Order:
  current fee/commission decision + evidence
  → Order persists its own snapshot

Track → Candidate Application:
  SH-006 atomic usage
  → Candidate owner creates/owns JobApplication

Track → Search:
  boost fact/effective change
  → SH-091 request
  → Search owns projection

Track → Booking:
  priority decision
  → Booking owns hold/slot/booking application

Track → Professional Eligibility:
  commercial entitlement fact
  → Professional Eligibility composes readiness

Track → Video / Digital:
  entitlement gate
  → delivery Module owns grant/room/download truth

Privacy → Track:
  SH-095 instruction
  → Track changes only Track records
  → Privacy owns parent target/job state
```

If a neighbor is not implemented, use versioned contract fixtures. Do not import its schema/repository just to make integration tests pass.

---

# Module Hardening Phase

Phase 8 covers only Track-specific production risk:

- entitlement-resolution determinism;
- plan version/history safety;
- actor/profile binding;
- grant precedence;
- subscription state races;
- provider replay/out-of-order events;
- metering race/idempotency;
- counter rebuild;
- provider reconciliation;
- deadline expiration;
- audit completeness;
- Search/Notification side-effect retry;
- privacy retention/anonymization;
- migration/backfill restartability;
- query/index performance;
- telemetry/secret safety.

Hardening must not introduce:

- a new generic event bus;
- a new idempotency system;
- a new queue;
- a new authorization layer;
- a second processed-Stripe ledger copied from Payment;
- a generic CL-01 state machine;
- consumer-local current commercial policy.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Contracts and Source-of-Truth Foundation | 01–02, including gated slice 02A |
| 2 | Effective Entitlement and Grant Behavior | 03–04 |
| 3 | Metered Entitlement Consumption | 05 |
| 4 | Paid Subscription Lifecycle and Billing Provider | 06 |
| 5 | Track-Owned Workers and Side Effects | 07 |
| 6 | Module Integration | 08 |
| 7 | Privacy, Compliance, Audit, and Support Integration | 09 |
| 8 | Module Hardening and Production Verification | 10 |

**Total numbered Module features: 10, plus gated implementation slice 02A within Feature 02.**

These are Module-local implementation slices. They do not renumber or replace CL-01 Features 10–18.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read `context/shared/shared-operations.md`.
3. Read CL-01 architecture and build plan.
4. Read this Module architecture and implementation plan.
5. Read public-interface sections for direct dependencies/consumers.
6. Confirm the corresponding CL-01 feature is permitted to proceed.
7. Confirm the prior Module exit gate passed.
8. Confirm every named architecture blocker for this feature is resolved or that behavior is explicitly fixture-only/disabled/fail-closed.
9. Write the concise feature implementation specification.
10. Implement only the numbered feature.
11. Run required typecheck/lint/unit/integration/build checks.
12. Verify public contracts/workflow.
13. Update progress tracker.
14. Update architecture only if a binding decision legitimately changed.
15. Record unresolved risks/deferred work.

---

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise specification containing:

- **Objective**
- **Observable result**
- **Cluster build-plan link**
- **Dependencies**
- **Architecture gates**
- **In scope**
- **Out of scope**
- **Module-owned data affected**
- **Public contracts**
- **Shared operations consumed**
- **Permissions / consent / holds / step-up**
- **Primary workflow**
- **Provider integration**
- **Jobs / events**
- **Idempotency / concurrency**
- **Error behavior**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**
- **Exit gate commands/checks**

Do not generate detailed coding specifications for all remaining features in advance. Re-read current architecture before each feature because unresolved rulings may have changed.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed**
- **Cluster feature supported**
- **Files added**
- **Files changed**
- **Database changes**
- **Migrations**
- **Dependencies added**
- **Module public interfaces added/changed**
- **Shared operations reused**
- **Events/jobs added**
- **Provider adapter changes**
- **Tests added/changed**
- **Commands run**
- **Manual/contract verification**
- **Documentation updated**
- **Assumptions**
- **Known failures**
- **Remaining risks**
- **Architecture gates still unresolved**
- **Deferred work**
- **Exit-gate result**

The report must distinguish “implemented” from “contract stub/fixture-only/disabled pending architecture.”

---

# Final Quality Check

Before treating this plan as ready for implementation, verify:

1. Every Track source record has exactly one owner.
2. No User/Profile/Order/Booking/Search/Payment/Video/Digital lifecycle was absorbed.
3. SH-005 and SH-006 are implemented by Track and not duplicated by consumers.
4. All other shared operations are consumed rather than rebuilt.
5. TrackSubscriptionEvent, provider-event dedupe truth, AuditEvent, and IntegrationFailure remain distinct.
6. TrackUsageEvent remains source proof and TrackUsageCounter remains projection.
7. Cross-Module reads use owner public interfaces/DTOs.
8. Provider adapters do not become business truth.
9. Search remains projection and is changed only through SH-091.
10. Privacy orchestration remains Privacy-owned.
11. Order/Booking historical decisions remain consumer-owned snapshots.
12. Paid provider behavior cannot activate before U-CL01 gates resolve.
13. Every numbered feature has tests, acceptance criteria, and an exit gate.
14. Module sequencing aligns with CL-01 Features 10–18.
15. A coding agent can execute the next feature without inventing ownership, lifecycle, provider, or concurrency architecture.


## WA-R011 — Approved early-access scheduling (P01)

Product-owner ruling approved 2026-09-29: premium priority affects **when eligible customers may access newly released availability**. It never overrides an existing Booking, displaces a customer, reserves inventory permanently, or bypasses eligibility/conflict rules. This closes U-BC-05 / U-CL01-31 / CL-05-U017's product-effect choice.

Track owns the effective Customer-track benefit and returns eligibility, entitlement/grant evidence, policy version, evaluation time and expiry. Booking owns the release schedule and enforces the resulting access time on both slot queries and hold/confirmation commands. An early-access decision is not a slot reservation. Unavailable entitlement evidence cannot grant early access; ordinary access remains available once general release is reached, subject to normal gates. Existing holds follow their original bounded expiry; premium expiry cannot displace an already confirmed Booking.

Technical ruling: store timezone-independent release instants and a versioned release-window policy. Resolve the benefit against server time when creating a hold, bind evidence to that hold, and recheck normal conversion gates. No quota is consumed by this access-time benefit; SH-006 is not invoked unless a separately approved metered product is later introduced. Do not translate legacy priorityRank into request ordering. Missing release-window configuration disables early release for that availability; it does not invent a duration or disable ordinary booking. Exact window configuration is a launch prerequisite, not another ownership decision.

Implementation acceptance: premium/nonpremium boundary instants; expired/unavailable entitlement; concurrent claims; direct-command bypass attempts; replay of hold creation; no displacement; ordinary access at general release. Schema/API work must represent these facts before activation; this ruling is not implementation evidence.


## WA-R015 — User-wide points and no launch expiration (P04/P05)

**Binding product-owner ruling, approved 2026-09-30.** One User-wide Workin Ants points balance applies across Gamification/Rewards programs. Programs independently define earning rules and reward eligibility; they do not create separate point currencies or balances. This closes U-GR-01 / P04. Account identity and the atomic spending/ledger lock scope are User ID; optional program/profile references are provenance or eligibility context, never alternate wallets. All program-specific earning events credit the same account; reward eligibility is checked separately from point sufficiency. Cross-program spending uses the same canonical balance and cannot bypass a reward's eligibility conditions.

Points do not automatically function as cash, a Track/commercial entitlement, a purchased sweepstakes entry, or a mechanism for increasing chance-based prize odds. A separately approved conversion to a commercial benefit follows the explicit boundary and owner: Gamification owns redemption, Track owns commercial grants (SH-119), and the affected feature applies the granted benefit. No direct premium flag, implicit currency conversion, or automatic prize-entry creation is permitted.

**No automatic point expiration at launch.** Existing points remain valid unless spent, reversed or otherwise adjusted through an approved ledger operation. This closes U-GR-05 / P05 for launch. The `expired` enum remains reserved; launch commands, scheduled jobs and rules cannot append expiration effects. Program closure, inactivity, tier changes or profile changes do not expire a User's points. A future expiration feature requires explicit approved policy covering applicability, notice, effective dates, existing balances and auditable ledger behavior. Retention of proof is a separate concern and cannot be used to erase spendable value.

Technical application: calculate balance from the append-only owner ledger under WA-R014; serialize spending by User account, enforce sufficient available points atomically, and use immutable idempotent spend proof tied to redemption. Programs remain metadata/eligibility predicates, not lock partitions. Rebuildable balance/leaderboard projections never become source truth. Do not infer existing production balances or run a migration/backfill from this ruling.

Acceptance requirements: earnings from two programs combine into one balance; concurrent redemptions across programs cannot overspend it; reward eligibility can deny redemption despite sufficient points; profile/track changes preserve the account; program closure does not expire points; launch expiration attempts are rejected; replay creates no second spend; approved commercial conversion uses Track and never changes prize odds. These are future implementation tests, not a completion claim.


## WA-R018 — Durable execution, receipts and operational evidence

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R018 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r018--durable-execution-receipts-and-operational-evidence) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one platform-owned persistent command-idempotency/inbox/outbox/job mechanism with Postgres transactional persistence in the coordinated database pass. Module application/domain boundaries own effect semantics. A successful owner mutation atomically stores its domain change and outbox record; no transaction is held across provider/network calls. Consumers atomically claim a stable source event plus effect identity and commit their owner effect. Unknown outcomes reconcile before a new business attempt. Same scoped command key plus same canonical fingerprint replays the original result; different fingerprint conflicts. Owner/operation/subject scope is part of the key. At-least-once delivery is assumed; never promise global exactly-once execution.

Provider callbacks use verified provider/account/event identity, payload fingerprint, receipt state and separate effect/attempt state under the provider-owning Module (SH-059/060). A received/claimed record is not proof of completed effect. Duplicates preserve original proof; telemetry records observations. A retry of one semantic effect reuses its downstream idempotency identity. A genuinely new business attempt has a new identity linked to the prior result and cannot silently overwrite history. Booking workflow steps likewise carry a stable run/step/effect key. Exact tables/index names and runner library are implementation details; production runtime evaluation remains a scoped provider/operational gate, not a reason to build Module-local queues.

Adopt Ops-owned Postgres persistence for operational SystemEvent, IntegrationFailure and OpsIncident; QueueJob remains an operational projection of the platform runner, not a second executable queue. SystemEvent is append-only; correction references the original. IntegrationFailure separates occurrence identity from recovery observations; recording the same occurrence replays, another actual attempt creates another occurrence. Incident operator state is open/triaged/mitigated/resolved, with explicit authorized reopening recorded as a new transition; automatic grouping/alerts require versioned configured rules. Ops success/recovery cannot finish a business workflow. Tradeoff: durable local diagnostic queries require migrations/storage; provider dashboards remain secondary. Accept PR-CL09-05 persistence direction without claiming schema deployment or selecting retention periods.

Acceptance: concurrent identical/conflicting keys, crash after receipt and before effect, crash after domain commit and before dispatch, duplicate/out-of-order callback, lease recovery, retry exhaustion and reconciliation. Do not activate a consumer merely because a queue accepted its job.

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

## WA-R037 — Payment effects, payout reservation and tax evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Payment owns immutable financial operation and attempt history, not just outbox delivery. Every effect has unique owner/sourceType/sourceId/sourceRevision/effectKind/effectOrdinal plus currency, semantic payload hash and original-effect reference for compensation. Reuse with different amount/subject/currency conflicts. Verified provider ingress receipt is separate from Payment and Track effect receipts; route by approved provider object/metadata ownership, never both owners applying the same business effect. Unknown routing is quarantined. Payment receipt fields: provider/account/eventId, eventType, fingerprint, handlerVersion, target operation, receivedAt, processing/attempt/recovery state and committed effect references. No raw secret payload by default; legal retention remains externally supplied.

Balance accounting uses immutable signed minor-unit effects with explicit bucket vectors and per-currency conservation. Earnings credit available (or pending until the approved availability rule); payout reservation moves available -A/reserved +A atomically with request acceptance; reservation release moves reserved -A/available +A only once after known cancellation/failure with no possible pending provider movement; successful payout moves reserved -A/paid +A. Transport retries have zero ledger effect. Provider return/reversal records its actual returned amount as a new linked effect, paid -R/available +R only after verified return and applicable financial restrictions; it never mutates the original payout. Fees/refunds/chargebacks are separate authorized signed effects, never hidden in payout status. Unknown money movement retains reservation and reconciles. Existing one-amount enum records are insufficient to infer these vectors: use an explicit owner allocation/bucket effect structure and forward constraints. This is accounting of processor-held value, not permission to introduce a wallet or new financial product.

At launch each PayoutTransfer belongs to one PayoutRequest; Order references are optional immutable allocation provenance, not a second transfer source. A request supplies an explicit validated active payoutAccountId; no guessed default among multiple accounts. Capture all blocking Hold IDs and decision versions in a separate immutable evaluation snapshot; blockedByHoldId is explanatory only. Reevaluate current holds/account/financial readiness immediately before dispatch. Keep one semantic transfer identity and stable provider idempotency key through network retries. Record each transport attempt separately. A terminal failed transfer never reopens; a new request/transfer after confirmed nonmovement and reservation release requires fresh authorization. Unknown is nonterminal even if transport timed out. No automatic retry of a terminal financially reversed/paid transfer.

Ratify the minimum Payment §9 graphs with these restrictions: KYC rejected/expired/disabled attempts are terminal; new attempt linked to previous evidence. TaxProfile rejected/expired creates a new collection revision, never overwrites submitted documents. One current applicable selector per subject+purpose+jurisdiction/provider scope points explicitly to the accepted evidence; pending new evidence does not silently replace valid current proof, while revocation immediately invalidates it. PayoutAccount disabled is terminal for that account; restriction recovery uses verified current provider evidence. PayoutRequest failed/cancelled/reversed terminal; processing cannot cancel without proven no movement. PayoutTransfer failed/cancelled/reversed terminal. SalesTaxCalculation changed quote requires a new calculation; finalized is immutable, voiding is a separately evidenced provider operation. Tax submission rejected/failed uses a new linked submission revision; transport retries of an unacknowledged submission retain semantic identity. Filed recipient correction creates replacement evidence and a link, preserving prior filing. No enum setter or provider callback bypasses these rules.

Tax subject is a Payment-owned stable subject reference mapped to an identified legal recipient, with explicit User and optional ProfessionalProfile provenance; profile identity is not automatically a separate legal taxpayer. Effective mappings/versioned evidence prevent accidental subject merge. Aggregate key is taxSubjectId + jurisdiction + taxYear + currency + reportingRegime; retain source owner/id/revision/recognition type and unique reversal identity. Prize-owned summaries use the same dimensions and preserve their own source valuation truth. SH-019 supports an explicit tax_fulfillment purpose and tax dimension; no second generic tax-readiness service is needed. Payment owns TaxReportingSubmissionStatus and TaxReportingRecipientStatus. Reporting bundle uniqueness includes regime/jurisdiction/year/currency/submission series/revision; recipients unique within submission by tax subject and applicable form/category. Rule versions, form requirements, recognition dates, thresholds and correction legality remain approved external configuration, never invented constants.

Order binds final calculation ID to exact immutable quote/order revision, currency, line IDs and buyer-tax-location evidence revision. Payment preserves line-level taxable basis, tax, jurisdiction, provider tax code and liability role even for mixed-liability lines. Tax-location provenance includes approved source owner, source/evidence revision, validation method/result and captured/effective time, minimum required location fields; it is not public-location consent. Each authorized refund has immutable line allocations against the original captured quantities/basis/tax and links its own provider refund and tax reversal attempts. Cumulative refunds cannot exceed captured refundable allocation; lock the operation allocation counters and reject mismatched currency. Use deterministic minor-unit residual allocation only within an approved tax/provider allocation policy; do not guess rates or liability. Partial/multiple refund representation requires separate child records, not one overwritten reversalId. Provider unsupported/ambiguous results stay pending/manual review, never fabricated successful tax reversal. Full provider/rule qualification remains external before affected execution.

Required verification: concurrent reservation conservation, duplicate callback/compensation, timeout followed by paid result, multiple holds, account changes before dispatch, line-level cumulative refund cap, subject/jurisdiction separation, replacement filing traceability. No live financial test or migration is claimed by this architecture decision.


## WA-R041 — Retention-safe commercial snapshot links

Classification: AI_RESOLVED_WITH_TRADEOFF. Resolves CL04-U016; complements WA-R030/032/037.

Order retains an immutable purchase snapshot with the applied Track plan/price/grant policy identities and revisions, exact values used for fee/commission calculation, effective decision time and source decision references. Current catalog selection is separate. Historical identifiers remain meaningful even when an enrollment or catalog revision stops being current. Any navigation FK must restrict deletion or detach only that optional navigation while preserving the lawful retained immutable proof; never cascade-delete Order purchase evidence from Track cleanup. Actual lawful erasure/minimization follows Privacy's approved field disposition and retention policy, not indefinite retention by this ruling.

This resolves snapshot semantics and deletion behavior; exact FK names and coordinated forward migration remain implementation work. No catalog change reprices an accepted purchase. Verify retired plans, ended enrollment, valid privacy disposition, missing navigation target and historical refund reconstruction against the original basis.


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `track_subscription_entitlement` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`cancelTrackSubscription / createManualEntitlementGrant / revokeEntitlementGrant / resolveEntitlement`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.

## WA-R078 — Bilateral qualification sequence

Implement assignDefaultFreeTrack.v1 with current owner-binding verification, one current base selection and durable replay receipt; never downgrade a current paid selection. Follow the owner architecture and WA-R078 in `context/reconciliation/platform-architecture-rulings.md`. Qualify its named stale-source, wrong-scope, retry/conflict, unavailable and privacy cases on both sides before activation. External policy/provider and database prerequisites remain separate; no interface is frozen by this appendix.

## WA-R081–083 — Bridge qualification sequence

Implement only the owner architecture's reviewed bridge obligations (BF-005, BF-009, BF-010, BF-011, BF-012, BF-013, BF-015, BF-026, BF-027, BF-033, BF-034, BF-038, BF-063, BF-065, BF-066, BF-071, BF-099, BF-102, BF-131, BF-138, BF-159, BF-160, BF-162, BF-163, BF-164, BF-203, BF-204, BF-205, BF-210, BF-211, BF-224, BF-230, BF-231, BF-232, BF-236, BF-249, BF-256, BF-257, BF-262, BF-266). Load `context/reconciliation/bridge-contract-bindings.md` and the final inventory for current versions and disabled facets. First bind closed schemas and current source/actor/purpose fixtures; then qualify shared persistence/outbox/idempotency/receipt mechanisms; then connect producer and consumer. Required denial, stale/replay/conflicting-key, late-result and sensitive-field negative fixtures precede interface freeze. Provider/legal/database evidence gates only the affected activation. No full-Cluster dependency or parallel lane is implied, and no optional path is enabled by a fake or a passing structural checker. Preserve historical snapshots and P01–P19; do not implement schema/provider/product slices during readiness.
