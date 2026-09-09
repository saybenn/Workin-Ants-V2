# Track Subscription & Entitlement Implementation Plan

> **Module ID:** `track_subscription_entitlement`  
> **Module:** Track Subscription & Entitlement  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/modules/track_subscription_entitlement/implementation-plan.md`  
> **Companion architecture:** `module-architecture.md`  
> **Parent sequence:** `context/clusters/identity-authority-consent-entitlements/build-plan.md`  
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

Stripe Billing / Checkout / Customer Portal may be adapter-stubbed until CL-01 Feature 12. Live credentials and live callback side effects are **not** preconditions for catalog, entitlement resolution, or metering features.

### Mandatory architecture gates by slice

| Gate | Required before |
|---|---|
| U-CL01-18 free-plan representation | production default-free provisioning and free↔paid transitions |
| U-CL01-19 production entitlement catalog | activating production plan/entitlement keys |
| U-CL01-20 grant precedence | production SH-005 resolution over overlapping sources |
| U-CL01-21 subscription transition table | production paid subscription lifecycle |
| U-CL01-22 processed provider-event record | live provider webhook side effects |
| U-CL01-23 plan revision/effective history | material mutation of live production plans |
| U-CL01-24 typed value constraints | production plan mapping/grant writes |
| U-CL01-25 consent binding | paid enrollment/plan change |
| U-CL01-26 candidate usage period/refund rules | final Candidate Application quota integration |
| U-CL01-27 fee/commission calculation/snapshot rules | final Order pricing bridge |
| U-CL01-28 priority scheduling semantics | final Booking priority bridge |
| U-CL01-29 billing retention/anonymization | destructive privacy behavior |
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

Supports **CL-01 Feature 09 — Track Plan and Typed Entitlement Catalog Foundation** and its prerequisite ownership/schema work. It must not begin paid provider behavior from CL-01 Feature 12.

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

Potential migrations are allowed only for decisions already resolved, especially U-CL01-24/U-TSE-03/U-TSE-04 when ratified.

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
- U-CL01-24/U-TSE-03/U-TSE-04 remain visibly gated if unresolved;
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

Production keys/plan versions remain disabled if U-CL01-19/23/24 are unresolved.

### Cluster Build-Plan Link

Directly implements the Module portion of **CL-01 Feature 09 — Track Plan and Typed Entitlement Catalog Foundation**.

### Dependencies

- Module Feature 01;
- SH-001/002/029/044;
- plan/value architecture gates U-CL01-19, U-CL01-23, U-CL01-24;
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

- assigning subscriptions;
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
- **SH-080 `manageVersionedRules`** only after U-CL01-23 is resolved. Local policy: Track plan revision/effective dates.

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
- implement typed-value DB checks only after U-CL01-24;
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

Feature 02 passes only when catalog/domain/authorization/idempotency tests pass, seed replay is safe, no provider integration exists, and CL-01 Feature 09’s Track-specific exit conditions are satisfied.

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

Implements **CL-01 Feature 10 — Effective Entitlement Resolution and Actor Binding**.

### Dependencies

- Features 01–02;
- Customer SH-004;
- Candidate/Professional SH-003 owner facts;
- SH-011 if holds affect the requested policy;
- **production gate U-CL01-20 grant precedence**;
- U-CL01-24 typed-value validation.

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

When U-CL01-20 is resolved, update architecture first with the precedence table and then add full precedence tests.

### Acceptance Criteria

- SH-005 is the single resolution engine;
- wrappers delegate to it;
- consumers can obtain all needed current policy evidence without raw Track table access;
- unresolved precedence cannot silently grant access.

### Exit Gate

All SH-005 contract/domain tests pass and the production resolver remains disabled for ambiguous overlaps until U-CL01-20 is approved.

---

## 04 Entitlement Grant Lifecycle and Materialization

Create Track-owned grant mutation behavior independently from provider-specific paid subscription processing.

### Objective

Implement explicit grant create/suspend/restore/revoke/expire/consume semantics and the internal materialization hook that later subscription lifecycle work can call.

### Observable Result

Authorized admin/system workflows can create and transition a TrackEntitlementGrant through approved states, and SH-005 immediately reflects those state changes. Expiration is idempotent and historical usage remains untouched.

### Cluster Build-Plan Link

Supports **CL-01 Feature 10** (effective grants) and prepares **CL-01 Feature 12** (subscription-driven grant materialization) without starting provider integration.

### Dependencies

- Feature 03;
- SH-002/011/014/029/044/051/053/055/046;
- U-CL01-20 for overlapping precedence;
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
- temporary feature grants under SH-119 while ownership unresolved;
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

Implements the Track portion of **CL-01 Feature 11 — metered entitlement consumption and usage projection**.

### Dependencies

- Feature 03;
- SH-005/006;
- SH-044/051/057;
- SH-115 projection mechanism;
- U-TSE-04 semantic idempotency persistence;
- policy-specific gates such as U-CL01-26 before final Candidate Application activation.

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

When U-CL01-26 or another quota policy is resolved, add its period/reversal rules to architecture before consumer activation.

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

Implements **CL-01 Feature 12 — Paid Track Subscription Lifecycle and Billing Adapter**.

### Dependencies

Module Features 02–05 plus mandatory:

- U-CL01-18;
- U-CL01-20;
- U-CL01-21;
- U-CL01-22;
- U-CL01-23;
- U-CL01-25;
- U-CL01-29;
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
- owner-specific processed-event record after U-CL01-22;
- Track subscription transition service after U-CL01-21;
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
- Track transition table rejects invalid/out-of-order transitions according to U-CL01-21 ruling;
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
- billing retention follows U-CL01-29.

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

The feature cannot pass for production until every mandatory architecture gate is resolved, provider signature/dedupe/ordering/reconciliation suites pass, and CL-01 Feature 12 exit conditions are satisfied.

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

Completes asynchronous work associated with **CL-01 Features 11–12** and prepares cross-Cluster contract proof in **CL-01 Phase 4 / Features 13–15**.

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

Supports **CL-01 Phase 4 — Cross-Cluster Contract Proof**, specifically the Track bridges included in CL-01 Features 13–15.

### Dependencies

- Features 03–07;
- downstream public contracts or versioned fixtures;
- U-CL01-26/27/28 for final policy-specific production behavior;
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

`quoteOrderTrackPolicy` returns buyer fee waiver and professional commission value/evidence. Order applies U-CL01-27-approved calculation and persists its historical snapshot. A later Track change does not rewrite the Order.

#### Candidate application bridge

Candidate workflow authenticates/authorizes its JobApplication creation, then calls SH-006 when the business event counts. Transaction ordering must prevent quota loss without a corresponding accepted business event according to the final integration design. U-CL01-26 controls reversal/refund semantics.

#### Search bridge

Track returns boost; Search composes boost with privacy/readiness/moderation. Track change calls SH-091; it never writes SearchUpsertEvent/Typesense.

#### Booking bridge

Track returns priority semantics only after U-CL01-28. Booking owns slot/hold/booking record and any priority application.

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
- usage consumed but consumer source mutation fails → follow approved U-CL01-26/integration compensation policy; do not invent a reversal.
- unresolved U-CL01-27/28 → final consumer behavior disabled.

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

Resolve U-CL01-26/27/28 in both relevant consumer Module architecture and Track architecture before production integration.

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

Supports CL-01’s privacy/guardrail integration in **Phase 4** and hardening requirements in **CL-01 Feature 16**.

### Dependencies

- prior Track source features;
- SH-095–098;
- SH-029/030;
- U-CL01-29 before destructive billing evidence behavior;
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
- hard-delete before U-CL01-29.

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

Resolve U-CL01-29 and record exact field retention/anonymization map before destructive production path.

### Acceptance Criteria

Track participates in Privacy through owner executor only; required evidence is preserved; no generic privacy/audit/ops truth is duplicated.

### Exit Gate

Privacy, retention, audit and sensitive-access test suites pass. Production erase remains disabled if U-CL01-29 is unresolved.

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

Implements the Track-specific portion of **CL-01 Feature 16 — Hardening and Production Readiness**.

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
| 1 | Contracts and Source-of-Truth Foundation | 01–02 |
| 2 | Effective Entitlement and Grant Behavior | 03–04 |
| 3 | Metered Entitlement Consumption | 05 |
| 4 | Paid Subscription Lifecycle and Billing Provider | 06 |
| 5 | Track-Owned Workers and Side Effects | 07 |
| 6 | Module Integration | 08 |
| 7 | Privacy, Compliance, Audit, and Support Integration | 09 |
| 8 | Module Hardening and Production Verification | 10 |

**Total numbered Module features: 10.**

These are Module-local implementation slices. They do not renumber or replace CL-01 Features 09–16.

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
14. Module sequencing aligns with CL-01 Features 09–16.
15. A coding agent can execute the next feature without inventing ownership, lifecycle, provider, or concurrency architecture.
