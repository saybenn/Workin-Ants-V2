# Sweepstakes / Prize Module Implementation Plan

> **Module ID:** `sweepstakes_prize`  
> **Module:** Sweepstakes / Prize Module  
> **Primary Cluster:** `CL-10` — Incentives, Rewards & Prize Economy  
> **Repository target:** `context/modules/sweepstakes_prize/implementation-plan.md`  
> **Companion:** this Module `module-architecture.md`, CL-10 `architecture.md` and `build-plan.md`, root Workin Ants context, Canonical Shared Operations Registry  
> **Implementation posture:** Greenfield/MVP planning against current Prisma/architecture evidence. Legal-gated production behavior remains disabled until its named architecture/legal blockers are resolved.

---

## Core Principle

Implement Sweepstakes / Prize through narrow, owner-controlled, verifiable slices:

```text
public / observable behavior
→ validated command/query or versioned inbound event
→ Sweepstakes-owned policy
→ authoritative Prize* write/read
→ canonical SH-### calls
→ transactional event / audit / notification effects
→ idempotency / concurrency proof
→ tests
→ explicit exit gate
```

The Module plan is subordinate to CL-10 `build-plan.md`. It narrows Cluster Features **06–11** into Module-only implementation work. It does not independently reorder the Cluster or pull Gamification work into Sweepstakes.

Draft/configuration behavior may be built before legal approval. Production activation, chance entry, winner selection, tax-sensitive fulfillment, redraw, and any unowned provider effect must fail closed when a required architecture decision is unresolved.

---

## Build Rules

1. Follow root architecture, root code standards, Canonical Shared Operations, CL-10 architecture, and CL-10 build plan.
2. This Module owns only PrizeDrawing, SweepstakesEntryMethod, PrizeEntry, PrizeWinning, PrizeTaxYearSummary, owned enums, and owner policies defined in `module-architecture.md`.
3. Consume other Modules through approved public commands/queries/events. Direct cross-domain Prisma reads are not the default.
4. Reuse canonical SH-### operations; do not create feature-local auth, consent, hold, tax, notification, audit, queue, retry, idempotency, lock, crypto, privacy, or telemetry infrastructure.
5. Every mutation is validated, authenticated where required, authorized server-side, and transaction-safe.
6. Every lifecycle transition goes through Sweepstakes owner policy and SH-053 plumbing; no raw status writes from UI/provider/event handlers.
7. Every source event and retryable command has stable idempotency semantics.
8. Purchase-triggered entry facts come from the authoritative Order/payment owner; Sweepstakes owns no Stripe webhook.
9. `entryToken` uniqueness is not considered sufficient idempotency proof.
10. Entry limits must be race-safe under concurrent requests.
11. Secure winner selection uses SH-116 only, under a database lock and immutable drawing-run evidence.
12. Notification delivery, audit logs, and telemetry never become PrizeWinning/drawing-run truth.
13. Tax provider/TaxProfile truth remains Payment / Payout / Tax-owned.
14. ComplianceHold lifecycle/release remains Admin Review-owned.
15. Track entitlement, points, rewards, or purchases must not create better prize odds unless separately approved by legal/architecture.
16. External provider details remain behind the explicit provider owner’s adapter. No prize fulfillment provider is currently approved.
17. Workers use canonical durable job/retry/telemetry mechanisms.
18. Every numbered feature ends with tests and an exit gate.
19. If implementation settles a deferred architecture decision, update architecture first or in the same reviewed change before depending on it.
20. Unresolved architecture is surfaced and fail-closed, never guessed.

---

## Preconditions

### Hard platform dependencies

The production implementation depends on canonical contracts or equivalent platform implementations for:

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-008 `queryConsentProof`;
- SH-009 `resolveActiveConsentVersion`;
- SH-011/012 ComplianceHold interfaces;
- SH-019 financial/tax readiness;
- SH-029/030 audit/sensitive access;
- SH-032/033/034 request context/logging/redaction;
- SH-037/038 failure/queue telemetry;
- SH-041 Notification request;
- SH-044/045 command/event idempotency;
- SH-046 transactional outbox;
- SH-047/048 durable jobs/retries;
- SH-051 aggregate locking;
- SH-053 lifecycle transition plumbing;
- SH-095–098 Privacy owner protocol;
- SH-116 secure random selection;
- SH-117 yearly value aggregation;
- SH-118 taxable-value reporting.

If a canonical operation is not yet implemented, feature development may use a contract fake in tests, but production code must depend on the canonical interface. Do not create a Sweepstakes replacement.

### Hard neighboring Module dependencies

- Identity & Access / Role & Authority contracts for protected actions.
- Consent & Disclosure version/proof contracts.
- Transaction / Order or Payment-owner versioned event contract for purchase-triggered entries.
- Payment / Payout / Tax readiness and taxable-value contracts before tax-sensitive fulfillment.
- Admin Review / Compliance Hold query/request contract.
- Notification request contract for production communications.
- Privacy / Data Erasure owner protocol before production privacy completion.

### Dependencies that may initially be stubbed

- real Order purchase event may be represented by a versioned contract fixture until the source Module event exists;
- SH-019/118 may be contract-faked until Payment/Tax is available;
- SH-041 may be contract-faked for workflow tests;
- SH-011/012 may be contract-faked in early isolated domain tests;
- no external prize fulfillment provider is required for early slices.

### Architecture blockers

- **U-CL10-01** must be resolved before production drawing activation.
- **U-CL10-02** must be resolved before production winner selection.
- **U-CL10-09** blocks only a schema/FK decision; runtime proof validation can proceed through SH-008.
- **U-CL10-11** blocks redraw/replacement-winner functionality.
- **U-CL10-12** blocks production launch for legal thresholds/jurisdictions not covered by approved policy.

---

# IMPLEMENTATION PHASES

## Phase 1 — Contracts and Source-of-Truth Foundation

### 01 Sweepstakes Module Contracts, Lifecycle Policy, and Repository Boundary

#### Objective

Establish a compilable/testable Sweepstakes Module boundary with typed public contracts, owner repositories, reason-code vocabulary, lifecycle-policy scaffolding, and no production behavior that depends on unresolved legal proof.

#### Observable Result

- Other code can import Sweepstakes public command/query/event types without importing Prisma models.
- Owner repositories can read/write the five current Sweepstakes models in isolated tests.
- Proposed lifecycle graphs are represented as policy tests/configuration but clearly marked as inherited Proposed Rulings.
- A static architecture test can detect forbidden provider/cross-domain repository imports.

#### Cluster Build-Plan Link

Supports **CL-10 Feature 06** foundation and the Module prerequisites for Features 07–10.

#### Dependencies

- current Prisma schema/migrations;
- Module architecture;
- root validation/error conventions;
- SH-015 decision-result pattern if the root adopts it; otherwise the Module-local stable result shape defined in architecture;
- SH-053 lifecycle plumbing interface.

#### In Scope

- create Module folder structure consistent with approved root conventions;
- define DTOs for PrizeDrawing, entry method, PrizeEntry, PrizeWinning, PrizeTaxYearSummary;
- define public command/query contract types;
- define inbound qualifying-purchase event contract placeholder/versioned consumer interface;
- define proposed event vocabulary/envelopes without custom event bus;
- define stable denial/conflict/review reason codes;
- create owner repository interfaces/Prisma implementations only for owned tables;
- encode lifecycle-policy tests for PrizeDrawing/EntryMethod/PrizeWinning without exposing raw status setters;
- define owner privacy contract surface types;
- add dependency-direction lint/test if repository tooling supports it.

#### Out of Scope

- actual drawing activation;
- entry issuance;
- secure random selection;
- tax/hold integration;
- privacy execution;
- provider adapters;
- new schemas for rules/run proof.

#### Module-Owned Data

Read/write scaffolding only for:

- PrizeDrawing;
- SweepstakesEntryMethod;
- PrizeEntry;
- PrizeWinning;
- PrizeTaxYearSummary;
- owned enums.

No migration unless the current schema is missing from the actual database foundation.

#### Public Interfaces

Introduce typed definitions for:

- `configurePrizeDrawing`;
- `configureSweepstakesEntryMethod`;
- `setSweepstakesEntryMethodStatus`;
- `activatePrizeDrawing`;
- `closePrizeDrawing`;
- `cancelPrizeDrawing`;
- `issuePrizeEntry`;
- `correctPrizeEntryEligibility`;
- `evaluatePrizeEntryEligibility`;
- `runPrizeDrawing`;
- `transitionPrizeWinning`;
- `reconcilePrizeTaxYearSummary`;
- corresponding public queries;
- Module domain event types.

Exact function filenames may follow repository standards; semantics remain as documented.

#### Shared Operations Used

- **SH-053 — transitionLifecycleState**; shared mechanism. Invoke from future owner transition services. Local policy is the transition matrix. Do not create a generic status engine.
- **SH-032/034 — request context/redaction contracts** in public application context types if root standards require them. Do not create local correlation/sanitization helpers.

#### Domain Logic

- no public command accepts a raw target status without owner transition intent;
- Prisma models are not returned directly across Module boundaries;
- reason codes are stable and safe;
- PrizeEntry/Winning DTOs do not expose raw Tax/Consent/provider payloads;
- architecture flags unresolved behavior explicitly.

#### Authorization / Compliance

No business action is completed yet, but public command signatures must require enough context for SH-001/002 and later consent/hold/tax gates. Do not bake authorization into repository methods.

#### Database / Transaction Behavior

- repositories may open/use caller transaction handles according to root persistence conventions;
- no cross-domain repository joins;
- tests confirm current unique/index semantics, especially PrizeTaxYearSummary unique key and PrizeEntry token uniqueness;
- destructive PrizeDrawing delete is not exposed as a public owner command.

#### Events / Jobs

Define event types only. No custom outbox/job implementation.

#### Provider Integration

None.

#### UI / Admin Surface

None required.

#### Failure Behavior

- unsupported/raw lifecycle mutation cannot compile through public contract or is rejected by owner policy;
- forbidden cross-domain repository dependency fails architecture test/review;
- unresolved contract fields are marked rather than fabricated.

#### Tests

- type/contract tests;
- repository integration tests against current Prisma schema;
- lifecycle-policy unit tests;
- serialization/redaction tests for public DTOs;
- architecture import-boundary test;
- migration/reset test if tables are newly created in environment.

#### Documentation Updates

- update Module architecture only if actual repository conventions force an equivalent folder/interface naming change;
- progress tracker records feature completion.

#### Acceptance Criteria

- all five owned models are accessible only through Sweepstakes repository boundary in new Module code;
- public contracts do not expose Prisma types;
- raw cross-domain Prisma imports are absent;
- no Stripe/tax/notification provider package is added;
- transition policies are testable and distinguish confirmed/proposed rules.

#### Exit Gate

Typecheck, lint, repository integration tests, architecture-boundary tests, and lifecycle-policy tests pass. No application behavior beyond source-of-truth scaffolding is enabled.

---

### 02 Drawing, Entry-Method, AMOE, and Immutable-Rules Activation Gate

#### Objective

Implement safe draft configuration and owner activation policy for PrizeDrawing and SweepstakesEntryMethod, with production activation blocked until approved immutable official-rules evidence exists.

#### Observable Result

- authorized admin can create/edit a draft drawing and entry methods through owner services;
- validation exposes schedule, value, AMOE/free-path, limit, and equivalent-odds errors;
- activation returns structured denial when immutable rules evidence or required consent version/proof is missing;
- no entry can be issued yet.

#### Cluster Build-Plan Link

Directly implements the Sweepstakes portion of **CL-10 Feature 06 — Prize Drawing, Entry-Method, AMOE, and Rules Activation Gate**.

#### Dependencies

- Feature 01;
- SH-001, 002, 008, 009, 029, 044, 046;
- SH-072/077 only after U-CL10-01 resolves in that direction;
- approved U-CL10-01 architecture decision is required for production activation exit.

#### In Scope

- drawing draft create/update;
- entry-method create/update/status transitions;
- declarative eligibility payload schema/version validation if `eligibilityJson` is used;
- coherent timing validation;
- prize value/currency validation;
- AMOE/free-method composition validation;
- `isFree`/`requiresPurchase`/type compatibility;
- entriesAwarded/oddsEquivalent effective-odds policy;
- active method set edit restrictions/audit policy;
- activate/close/cancel drawing transitions;
- optional thin admin configuration surface if CL-10 admin UI is in current Cluster scope.

#### Out of Scope

- PrizeEntry creation;
- purchase events;
- drawing selection;
- tax/fulfillment;
- legal drafting;
- inventing a rules-proof schema before U-CL10-01 approval.

#### Module-Owned Data

- PrizeDrawing;
- SweepstakesEntryMethod;
- PrizeDrawingStatus;
- SweepstakesEntryMethodStatus/Type.

Potential new official-rules proof record only after approved architecture/migration.

#### Public Interfaces

Implement:

- `configurePrizeDrawing`;
- `configureSweepstakesEntryMethod`;
- `setSweepstakesEntryMethodStatus`;
- `activatePrizeDrawing`;
- `closePrizeDrawing`;
- `cancelPrizeDrawing`;
- `getPrizeDrawing`;
- `listAvailableEntryMethods` for configuration/read context.

#### Shared Operations Used

- **SH-001** Identity & Access: resolve admin actor. Do not build local session helper.
- **SH-002** Role / Authority: authorize configuration/activation/close/cancel. Do not build `isSweepstakesAdmin`.
- **SH-009** Consent: resolve applicable active rules/disclosure version. Local policy decides which type applies.
- **SH-008** Consent: validate exact acceptance where activation policy requires proof. Do not copy ConsentLog.
- **SH-029** Audit: activation/cancellation/material method changes.
- **SH-044** Idempotent command: activation/transition retries.
- **SH-046** Outbox: drawing activated/closed/cancelled facts.
- **SH-072/077** only if approved rules-evidence design uses canonical hash/text snapshot. Do not create Sweepstakes crypto.

#### Domain Logic

- `startsAt < endsAt`; `drawsAt` must be coherent with close/end policy;
- limits cannot be negative and must be mutually coherent;
- purchase-triggered method cannot be treated as sufficient AMOE where a free path is required;
- active free method must actually be available, not only represented by booleans;
- paid method cannot receive better effective chance through `entriesAwarded`, `oddsEquivalent`, hidden eligibility payload, or downstream entitlement;
- `eligibilityJson` is declarative and versioned; no executable expression/function payload;
- retired method never reactivates;
- closed/completed/cancelled drawing configuration cannot be materially rewritten through normal owner service;
- production activation fails closed without approved rules evidence and legal launch policy.

#### Authorization / Compliance

- all admin mutations use SH-002;
- activation is compliance-sensitive and audited;
- no purchase-only flow where prohibited;
- no points/reward/entitlement odds influence;
- exact legal/jurisdiction policy is an input, not hardcoded.

#### Database / Transaction Behavior

- drawing + method configuration changes use owner transactions where consistency requires it;
- activation reads the active method set in the same transaction/lock context needed to prevent a concurrent material method change from invalidating readiness;
- status change and outbox record are atomic through platform conventions;
- no destructive delete for activated/evidence-bearing drawing.

#### Events / Jobs

Emit via SH-046:

- PrizeDrawingActivated;
- PrizeDrawingClosed;
- PrizeDrawingCancelled;
- material entry-method lifecycle fact if downstream consumers need it.

Scheduled close/draw job registration may be prepared, but draw execution remains disabled until Feature 06.

#### Provider Integration

None. Explicit test ensures no Stripe client/webhook.

#### UI / Admin Surface

If admin UI is in scope:

- draft drawing form;
- entry-method editor;
- status/timing/value fields;
- AMOE/equivalent-odds validation panel;
- immutable rules evidence status;
- activation checklist;
- close/cancel controls.

UI calls owner commands only.

#### Failure Behavior

- invalid config → validation denial/no write;
- unauthorized actor → denial/no write;
- consent/rules service unavailable → activation denied/dependency failure; draft remains;
- missing immutable rules evidence → explicit legal/rules denial;
- stale lifecycle → conflict;
- outbox dispatch outage after commit → canonical retry, no rollback of committed truth.

#### Tests

- unit: timing, limits, method semantics, AMOE, odds equivalence, transitions;
- contract: SH-008/009;
- authorization tests;
- transaction/outbox integration;
- compliance regression: purchase-triggered cannot bypass required free path;
- architecture test: no Stripe/provider import;
- schema test for U-CL10-01 migration if approved.

#### Documentation Updates

If U-CL10-01 is resolved here, update:

- Module architecture Section 35/36;
- CL-10 architecture U-CL10-01;
- Prisma/schema migration context;
- Shared Operations reference only if canonical operation contract changes.

#### Acceptance Criteria

- safe draft CRUD works through owner interfaces;
- all invalid method/odds combinations return stable reasons;
- activated state is unreachable without approved rules evidence;
- method set and lifecycle invariants are transactionally enforced;
- no entry/drawing/provider behavior leaks into feature.

#### Exit Gate

Feature passes only when U-CL10-01 is approved for production activation, required migration/contract exists, activation tests pass, and standard typecheck/lint/integration/build checks are green. If U-CL10-01 is not yet approved, the feature may be marked **draft-configuration complete / production activation blocked**, but Feature 03 production entry work cannot be enabled.

---

## Phase 2 — Idempotent Entry Issuance

### 03 Free, Mail-In, Admin, and System Prize Entry Issuance

#### Objective

Issue non-purchase PrizeEntry records exactly once under active method, consent, eligibility, hold, equivalent-odds, and race-safe entry-limit policy.

#### Observable Result

- user can execute the approved free entry path and receive accepted/denied result;
- duplicate click/retry does not create extra entries;
- concurrent free requests cannot exceed limits;
- authorized admin/mail/system path can issue entries with explicit provenance and audit;
- own entry query returns source/method/eligibility without exposing unrelated internals.

#### Cluster Build-Plan Link

Implements the non-purchase half of **CL-10 Feature 07 — Idempotent Prize Entry Issuance and Authoritative Purchase Bridge**.

#### Dependencies

- Features 01–02;
- active production-safe drawing configuration;
- SH-008, 011, 044, 051, 046, 041 optional, 029 for privileged paths;
- U-CL10-09 may remain unresolved because runtime validates proof via SH-008.

#### In Scope

- `evaluatePrizeEntryEligibility` owner policy;
- free_daily issuance;
- mail-in/admin/system command variants where product/admin workflow exists;
- per-user/free/max limit enforcement;
- configured `entriesAwarded` quantity;
- `weight` enforcement under equivalent-odds policy;
- `rulesConsentId` proof reference from SH-008;
- idempotency semantic keys;
- eligibility-correction command with audit/freeze guard;
- `getUserDrawingEntries` query.

#### Out of Scope

- purchase-triggered entry;
- Stripe/payment validation;
- random selection;
- redraw;
- tax/fulfillment;
- generic fraud scoring.

#### Module-Owned Data

- PrizeEntry;
- PrizeEntrySource;
- reads PrizeDrawing/SweepstakesEntryMethod.

No new local idempotency/inbox table.

#### Public Interfaces

- `issuePrizeEntry` with explicit source/method/request identity;
- `evaluatePrizeEntryEligibility`;
- `correctPrizeEntryEligibility`;
- `getUserDrawingEntries`.

If UX warrants, a narrow `requestFreeDailyPrizeEntry` adapter may call `issuePrizeEntry`; it is not a second domain service.

#### Shared Operations Used

- **SH-001/002** for user/admin actor/action authorization as applicable.
- **SH-008** exact rules consent proof. Local policy decides sufficiency.
- **SH-011** hold evaluation if entry issuance policy blocks on applicable holds.
- **SH-044** command idempotency. Local key includes user/drawing/method/source request identity.
- **SH-051** aggregate lock. Local key protects `(drawingId,userId)` count boundary.
- **SH-046** entry-issued/eligibility-change outbox events.
- **SH-041** optional confirmation notification after commit.
- **SH-029** admin adjustment and eligibility correction audit.

#### Domain Logic

- drawing and method must be active at authoritative request time;
- method type/source must match;
- free entry cannot require purchase;
- exact consent proof validated centrally if required;
- enforce source-specific and max limits atomically;
- create exactly `entriesAwarded` PrizeEntry rows/effects under one command outcome;
- all equivalent entry rows use approved weight policy;
- admin/system source does not gain special odds by default;
- eligibility denial returns reason with no PrizeEntry unless policy explicitly records ineligible issued entries; current implementation should prefer no issuance for precondition failure and reserve `isEligible=false` for post-issuance correction/known issued evidence;
- correction does not delete entry and is prohibited after population freeze unless approved run/redraw policy supports it.

#### Authorization / Compliance

- free path remains genuinely free;
- admin adjustment requires explicit authority/reason/audit;
- hold evaluation is owner-consumed, not local blocked truth;
- no Track/points/reward dependency;
- public endpoint uses root rate-limit mechanism if available.

#### Database / Transaction Behavior

Transaction boundary must include:

1. idempotency claim;
2. drawing/method current-state read;
3. lock for user+drawing entry limits;
4. count/limit evaluation;
5. PrizeEntry insert(s);
6. outbox record.

No check-then-write outside the transaction.

#### Events / Jobs

Emit `PrizeEntryIssued`; emit `PrizeEntryEligibilityChanged` for correction. Notification is post-commit. No background job required for normal free entry.

#### Provider Integration

None.

#### UI / Admin Surface

- user free-entry action and own count/result if in current product surface;
- admin entry list/filter, source/method/eligibility/consent-reference display;
- admin adjustment and eligibility correction controls where approved.

#### Failure Behavior

- duplicate request → replay existing outcome;
- limit reached → DENY_ENTRY_LIMIT_REACHED;
- missing consent → DENY_CONSENT_REQUIRED;
- method/drawing unavailable → denial;
- lock conflict → bounded retry/conflict using platform mechanism;
- audit/notification downstream failure does not fabricate/remove PrizeEntry;
- post-freeze correction → conflict/review required.

#### Tests

- unit eligibility/limit/source mapping;
- idempotency duplicate-click tests;
- concurrency tests at free/max boundary;
- consent/hold contract tests;
- authorization/admin audit tests;
- equivalent-odds tests;
- freeze-aware correction tests;
- E2E free-entry path.

#### Documentation Updates

If U-CL10-09 is resolved, update Module/Cluster architecture and Prisma relationship documentation before migration.

#### Acceptance Criteria

- free path issues exact configured count once;
- concurrent attempts cannot exceed limits;
- duplicate request cannot produce fresh token/effect;
- admin/system path is authorized/audited;
- own-entry query is privacy-safe;
- no provider/Order repository dependency exists.

#### Exit Gate

All unit/contract/integration/concurrency/E2E free-entry tests pass and DB fixtures prove configured limits cannot be exceeded under simultaneous requests.

---

### 04 Authoritative Purchase Event to PrizeEntry Bridge

#### Objective

Consume a versioned authoritative Order/payment-owner event and issue purchase-triggered PrizeEntry records exactly once without Sweepstakes touching Stripe or Payment repositories.

#### Observable Result

- a qualifying source-owner event creates the configured purchase entries with Order provenance;
- duplicate delivery/replay creates no duplicate entry effect;
- invalid/unqualified/out-of-window events are safely denied/no-op according to policy;
- no Stripe webhook/client exists under Sweepstakes.

#### Cluster Build-Plan Link

Completes the purchase bridge portion of **CL-10 Feature 07** and implements **PR-CL10-01** once approved.

#### Dependencies

- Feature 03;
- approved source event/public contract from Transaction / Order or Payment owner;
- SH-045, 044, 051, 046, 008 as required, 011 where applicable, 037/038 for worker failures;
- PR-CL10-01 approved before production activation of purchase-triggered methods.

#### In Scope

- versioned inbound event adapter/handler;
- source event validation and safe DTO;
- consumer inbox dedupe through SH-045;
- drawing/method lookup through Sweepstakes repositories only;
- Order ID provenance on PrizeEntry;
- paid/max limit enforcement under lock;
- equivalent-odds enforcement;
- event-time semantics for determining whether the method was valid;
- dead-letter/retry handling through canonical worker system;
- contract tests with source owner.

#### Out of Scope

- Stripe webhook/signature/dedupe;
- deciding whether payment succeeded from provider state;
- Order lifecycle mutation;
- points-to-entry bridge;
- refunds/cancellations invalidating entries unless official rules and source contract explicitly define that behavior.

#### Module-Owned Data

PrizeEntry only, plus owner outbox/events. Order remains external truth.

#### Public Interfaces

Inbound contract is a versioned owner event, conceptually:

```text
QualifyingPurchaseOutcomeV1 {
  eventId
  schemaVersion
  orderId
  userId / buyer subject ID as approved
  occurredAt
  qualifyingPromotion/drawing facts
  correlationId
}
```

Exact name/fields follow the source owner contract; do not invent extra source truth by querying its DB.

#### Shared Operations Used

- **SH-045** deduplicate inbound event; no local processed-event table.
- **SH-044** protect resulting owner command/replay semantics.
- **SH-051** entry-limit concurrency.
- **SH-046** publish PrizeEntryIssued facts.
- **SH-008** validate required rules consent proof if source event does not itself carry a valid proof reference and the entry policy requires one.
- **SH-011** applicable hold decision where entry policy requires.
- **SH-047/048/038/037** if event handling is queued and fails/retries.

#### Domain Logic

- only a configured `purchase_triggered` method may consume this source event;
- source event validity is trusted to its owner; Sweepstakes evaluates only drawing/method/entry policy;
- one event/order may create exactly the number allowed by approved drawing/method semantics once;
- purchase-derived entries cannot receive better effective weight/odds than the approved equivalent free path;
- event arrival time does not retroactively change the source occurrence time; use the approved authoritative occurrence semantics;
- event replay is safe;
- no hidden subscription/reward multiplier.

#### Authorization / Compliance

System event consumer uses trusted service context. No human UI authorization substitutes for source-event authenticity. AMOE/equivalent odds remain local Sweepstakes enforcement.

#### Database / Transaction Behavior

Transactional inbox claim + owner entry issuance effect must be atomic or follow the platform’s canonical inbox/command transaction pattern. Entry-limit lock/count/inserts/outbox are within the effect transaction.

#### Events / Jobs

- inbound source event through SH-045;
- owner PrizeEntryIssued event through SH-046;
- canonical queue/retry/dead-letter if asynchronous.

#### Provider Integration

Explicitly none. Add an architecture/test assertion that `sweepstakes-prize` does not import Stripe SDK/webhook modules or `ProcessedStripeEvent` repository.

#### UI / Admin Surface

Admin may display source=`purchase` and Order ID reference. It must not display raw Stripe/provider payload.

#### Failure Behavior

- duplicate event → processed/no-op prior result;
- incompatible event version → permanent/dead-letter with SH-037/038, no entry;
- method/drawing invalid at relevant time → policy no-op/denial, not fabricated provider retry;
- dependency unavailable for required consent/hold → retryable safe failure where appropriate;
- limit reached → denied/no additional entry.

#### Tests

- source contract compatibility;
- duplicate event/replay;
- concurrent source events at limit boundary;
- paid/free effective odds equivalence;
- event-before/after drawing window fixtures;
- worker retry/dead-letter;
- architecture test for absence of Stripe imports/direct Payment/Order repository access.

#### Documentation Updates

If source event naming/version or PR-CL10-01 is finalized, update Module/Cluster public-interface sections.

#### Acceptance Criteria

- one authoritative event yields one configured business effect;
- repeated event yields no duplicate PrizeEntry;
- Order provenance is stored;
- no Stripe provider code or Payment repository exists in Sweepstakes;
- AMOE/equivalent odds remain enforced.

#### Exit Gate

Real or contract-complete source owner event tests pass, including replay/concurrency. Purchase-triggered methods remain disabled in production until the source contract and PR-CL10-01 are approved.

---

## Phase 3 — Secure Drawing and Winner Truth

### 05 Immutable Drawing-Run Proof and Frozen Population Foundation

#### Objective

Resolve U-CL10-02 and implement the Module-owned immutable proof needed to freeze the eligible population and support one auditable drawing run without using AuditEvent/logs as run truth.

#### Observable Result

- approved Prisma model/migration exists for drawing-run proof;
- a closed drawing can produce a deterministic/frozen population evidence record without selecting a winner yet;
- authorized admin can inspect safe run-preparation evidence;
- post-freeze PrizeEntry correction is rejected or routed to explicit review according to approved policy.

#### Cluster Build-Plan Link

Architecture prerequisite for **CL-10 Feature 08 — Secure Drawing Execution and PrizeWinning Creation**.

#### Dependencies

- Features 01–04;
- **U-CL10-02 must be resolved before coding the schema**;
- SH-051, 044, 046, 029, 072 optionally for integrity hash, 032–034;
- U-CL10-11 remains out of scope.

#### In Scope

After architecture approval only:

- add approved drawing-run proof model(s)/enum(s) exactly as ruled;
- migration with indexes/unique constraints preventing competing active/completed runs;
- repository/contracts for run evidence;
- frozen eligible population query/build process;
- integrity count/hash/reference as approved;
- selection policy/version and winner-count/replacement metadata fields as approved;
- run preparation command/state if the approved design separates prepare/select;
- freeze guard in entry-correction policy;
- retention/privacy classification for run proof.

#### Out of Scope

- choosing schema/name before approval;
- random selection itself;
- redraw/replacement;
- tax/fulfillment;
- using AuditEvent as the proof record.

#### Module-Owned Data

Existing:

- PrizeDrawing;
- PrizeEntry.

New only after approval:

- approved drawing-run proof record(s).

#### Public Interfaces

- `getDrawingRunEvidence`;
- owner-internal `prepareDrawingRun` if approved design uses separate preparation;
- `runPrizeDrawing` contract updated to reference approved run proof.

#### Shared Operations Used

- **SH-051** single-run/resource lock.
- **SH-044** run-preparation idempotency.
- **SH-046** optional run-start/prepared facts after owner commit.
- **SH-029** audit manual run initiation/preparation.
- **SH-072** only if approved population/evidence hash design uses canonical hash. Local policy defines canonical input.
- **SH-032/033/034** safe request/worker telemetry.

#### Domain Logic

The approved proof must be sufficient to answer:

- which drawing/run was executed;
- which entry population was eligible/frozen;
- population count/integrity reference;
- selection policy/version;
- intended winner count;
- replacement/repeat-winner policy in effect, even if initial policy is “no replacement in this feature”;
- selected entry references once Feature 06 runs;
- actor/system/correlation/timestamps;
- completion/outcome evidence.

A run cannot be prepared from an active drawing that still accepts entries. Frozen population must not change beneath the run.

#### Authorization / Compliance

Manual preparation requires SH-002 and audit; automated system preparation uses trusted worker context. Equivalent-odds policy is checked before final freeze.

#### Database / Transaction Behavior

- acquire drawing lock before run claim/freeze;
- use unique constraints/owner transaction to prevent duplicate run identity;
- frozen population proof and drawing/run state change are atomic according to approved design;
- migration includes rollback/destructive-change analysis;
- no cascade that deletes completed run proof with ordinary record cleanup unless retention policy explicitly allows.

#### Events / Jobs

No selection yet. Optional `PrizeDrawingRunStarted/Prepared` event only if approved event vocabulary needs it. Jobs use canonical queue.

#### Provider Integration

None.

#### UI / Admin Surface

Safe run readiness/evidence summary; no winner or redraw controls yet.

#### Failure Behavior

- U-CL10-02 unresolved → feature cannot start;
- competing run claim → conflict/existing run result;
- population integrity failure → permanent/manual review, no selection;
- post-freeze entry mutation → conflict/review required.

#### Tests

- migration/reset tests;
- unique/lock concurrency tests;
- population eligibility/count/integrity tests;
- freeze guard tests;
- retention/privacy metadata tests;
- authorization/audit tests;
- evidence read contract tests.

#### Documentation Updates

Required when U-CL10-02 is resolved:

- Module architecture data/lifecycle/unresolved sections;
- CL-10 architecture U-CL10-02;
- Prisma/schema ownership references;
- Module implementation plan if approved schema alters Feature 06 transaction shape.

#### Acceptance Criteria

- approved immutable run proof exists in database and contracts;
- frozen population can be reconstructed/verified according to approved design;
- only one run claim/preparation can succeed for the initial drawing run;
- logs/AuditEvent are supplementary only.

#### Exit Gate

U-CL10-02 is formally resolved; migration and run-proof tests pass; concurrent run preparation cannot create two active proof records; no selection code exists yet.

---

### 06 Secure Drawing Execution and PrizeWinning Creation

#### Objective

Execute exactly one secure drawing against the frozen eligible population, select winner(s) only through SH-116, persist selection evidence and PrizeWinning snapshots, and complete the PrizeDrawing without duplicate outcomes under retries/crashes.

#### Observable Result

- closed/prepared drawing runs exactly once;
- concurrent worker attempts converge on one result;
- selected entries/winners are tied to immutable run evidence;
- PrizeWinning snapshots contain approved prize name/FMV/currency/tax year;
- downstream Tax/Notification outages do not change the selected outcome.

#### Cluster Build-Plan Link

Directly implements **CL-10 Feature 08**.

#### Dependencies

- Feature 05;
- SH-116, 051, 044, 046, 047, 048, 029, 014 as applicable, 032–034;
- approved winner count/repeat policy for initial run;
- U-CL10-11 remains explicitly out of scope.

#### In Scope

- `runPrizeDrawing` application command;
- closed→drawing→completed owner transitions;
- frozen population read from approved run proof/source;
- effective weight/equivalent-odds revalidation;
- SH-116 selection;
- selected-entry references in run evidence;
- PrizeWinning creation and FMV snapshot;
- post-commit outbox events;
- scheduled drawing worker;
- crash/replay recovery semantics;
- `getDrawingRunEvidence` and `getPrizeWinning` read paths.

#### Out of Scope

- redraw/replacement winner;
- manual winner choice disguised as random draw;
- tax readiness/fulfillment;
- external RNG provider;
- notification inside selection transaction.

#### Module-Owned Data

- PrizeDrawing;
- PrizeEntry read population;
- approved drawing-run proof;
- PrizeWinning.

#### Public Interfaces

- `runPrizeDrawing`;
- `getDrawingRunEvidence`;
- `getPrizeWinning`.

Emit PrizeDrawingCompleted/PrizeWinningCreated facts through SH-046.

#### Shared Operations Used

- **SH-116** secureRandomSelection. Local population/weight/winner policy; no other selection implementation.
- **SH-051** lock drawing/run.
- **SH-044** idempotent run command.
- **SH-046** atomic outbox after owner commit.
- **SH-047/048** scheduled worker/retry/dead-letter.
- **SH-029** audit run initiation/approved manual action.
- **SH-014** if root policy requires step-up for manual draw initiation/override.
- **SH-032/033/034/038** request/job telemetry and redaction.

#### Domain Logic

- only closed/approved prepared drawing is runnable;
- population is immutable for this run;
- ineligible rows are excluded according to frozen proof;
- equivalent odds/weight rules are rechecked;
- SH-116 selects exactly configured winner count;
- selected entries/winners are persisted to immutable run evidence;
- PrizeWinning snapshots prize value at run time from approved drawing configuration;
- drawing cannot complete without matching run/winning evidence;
- notification/tax work occurs after commit;
- no redraw path exists.

#### Authorization / Compliance

- scheduled system runner or authorized admin only;
- no direct winner override through normal path;
- manual/exception path, if ever approved, requires separate architecture and audit;
- no paid/free weighting advantage outside approved policy;
- high-risk action uses step-up when root policy requires.

#### Database / Transaction Behavior

Critical transaction/owner workflow must guarantee:

1. idempotency claim and drawing/run lock;
2. validate current closed/prepared state;
3. read frozen population/evidence;
4. select using SH-116;
5. update immutable run evidence with selected refs/result;
6. insert PrizeWinning row(s);
7. transition drawing to completed;
8. publish outbox records atomically.

If the approved persistence design cannot hold the entire selection transaction, it must use a recoverable run state that can replay the committed selection without calling SH-116 again.

#### Events / Jobs

- scheduled drawing job;
- retry/dead-letter through canonical worker;
- PrizeWinningCreated and PrizeDrawingCompleted events;
- correlation/causation IDs preserved.

#### Provider Integration

None.

#### UI / Admin Surface

- closed/ready status;
- run ID/evidence summary;
- eligible count;
- start control only if allowed;
- completed winner records;
- **no redraw button**.

#### Failure Behavior

- concurrent start → one proceeds, others get existing/in-progress result;
- crash before committed result → retry safely;
- crash after committed result → return existing run/winners, never select again;
- population integrity failure → stop/manual review, no partial winners;
- SH-116/internal failure before commit → safe retry if no selection persisted;
- downstream notification/tax failure → no change to winner truth.

#### Tests

- unit population/weight/state rules;
- selection property/statistical sanity tests around SH-116 implementation contract;
- integration closed→run→winning→completed;
- concurrency two+ workers;
- crash/replay before/after commit;
- compliance free/paid equivalence;
- authorization/step-up;
- downstream-outage isolation;
- explicit test that `Math.random()` is not used in Module selection code.

#### Documentation Updates

Record the final run-proof and selected-entry linkage design in Module architecture and current schema docs.

#### Acceptance Criteria

- one run produces one immutable outcome;
- one run cannot create competing winners under concurrency;
- SH-116 is sole selection mechanism;
- run proof links the selected entry/winner evidence;
- downstream failures cannot rerun or alter selection.

#### Exit Gate

All concurrency/recovery/compliance/security tests pass. A forced post-commit retry demonstrably returns the original result without another selection call.

---

## Phase 4 — Winning, Tax, Holds, and Fulfillment

### 07 PrizeWinning Tax/Hold Gate, Yearly Summary, Notification, and Fulfillment State

#### Objective

Carry PrizeWinning through approved tax/hold/confirmation/fulfillment transitions, maintain a reconciliable PrizeTaxYearSummary, report recognized value once to Payment/Tax, and request notifications without transferring lifecycle ownership.

#### Observable Result

- winner/admin can read accurate next state/action;
- tax-required or held winner cannot be fulfilled;
- yearly prize aggregate matches recognized PrizeWinning truth;
- Payment/Tax receives each recognized value once;
- Notification failure does not alter prize state;
- `fulfilled` requires approved fulfillment evidence.

#### Cluster Build-Plan Link

Directly implements **CL-10 Feature 09 — Prize Tax Summary, Hold Gate, and Fulfillment Lifecycle**.

#### Dependencies

- Feature 06;
- SH-019, 011, 012, 117, 118, 041, 047, 048, 037, 029, 030, 044, 053;
- approved legal/tax policy for enabled jurisdiction under U-CL10-12;
- fulfillment evidence contract for any automated effect. No provider is assumed.

#### In Scope

- `transitionPrizeWinning` owner service;
- local mapping of SH-019 financial/tax readiness to winning decisions;
- SH-011 active hold gate and SH-012 justified hold request when needed;
- pending_confirmation/pending_tax/blocked/approved/fulfilled/forfeited/cancelled policy as approved;
- immediate recheck before fulfillment;
- PrizeTaxYearSummary incremental update and full rebuild;
- SH-118 taxable-value handoff;
- winner/tax/fulfillment Notification requests;
- admin fulfillment queue/read model;
- sensitive-access audit where required;
- reconciliation worker.

#### Out of Scope

- tax filing/forms/provider client;
- ComplianceHold release;
- Stripe/payment execution;
- redraw/replacement;
- inventing shipping/gift-card provider;
- hardcoded legal thresholds not supplied by approved policy.

#### Module-Owned Data

- PrizeWinning;
- PrizeTaxYearSummary;
- owner domain events.

External references only:

- TaxProfile;
- ComplianceHold.

#### Public Interfaces

- `transitionPrizeWinning`;
- `getPrizeWinning`;
- `getPrizeTaxYearSummary`;
- `reconcilePrizeTaxYearSummary`;
- owner-internal `recognizePrizeValue` if useful;
- SH-019/118, SH-011/012, SH-041 calls.

#### Shared Operations Used

- **SH-019** Payment/Tax readiness. Never read provider status directly.
- **SH-011/012** hold query/request. Hold lifecycle remains external.
- **SH-117** yearly reportable-value aggregation. PrizeTaxYearSummary remains separate truth.
- **SH-118** report taxable/recognized value. Tax owner handles threshold/reporting/filing truth.
- **SH-041** Notification requests after committed facts.
- **SH-047/048** reconciliation/fulfillment retries.
- **SH-037/038** downstream/job failure visibility.
- **SH-029/030** privileged action and sensitive-read proof.
- **SH-044/053** transition idempotency and state-machine plumbing.
- **SH-014** fulfillment approval step-up if root policy classifies it sensitive.

#### Domain Logic

- external owner facts are evidence inputs only;
- `pending_tax` and `blocked` cannot fulfill;
- fulfillment rechecks applicable holds and SH-019 readiness immediately before transition;
- `approved → fulfilled` requires approved fulfillment evidence/reference;
- Notification success is never fulfillment evidence;
- recognized FMV comes from PrizeWinning snapshot, not mutable PrizeDrawing value;
- SH-117 update/rebuild keys by user+taxYear+currency;
- SH-118 uses source PrizeWinning ID and valuation evidence/idempotency;
- `forfeited`/`cancelled` only according to approved official rules/legal policy;
- completed/forfeited/cancelled evidence is retained according to Privacy/legal policy.

#### Authorization / Compliance

- winner sees only own safe status/context;
- admin transition/fulfillment uses SH-002;
- sensitive reads use SH-030 where classified;
- fulfillment approval uses step-up if required;
- exact legal thresholds are owner policy/config, not developer constants.

#### Database / Transaction Behavior

- winning transition uses idempotent command + current-state check;
- hold/tax decision must be fresh enough per approved policy;
- PrizeWinning status/timestamp + local outbox are atomic;
- yearly aggregate update is transactional/source-unique and full-rebuildable;
- tax report acknowledgment is not used as PrizeWinning source truth;
- no direct writes to TaxYearEarningsSummary/TaxProfile/ComplianceHold/Notification.

#### Events / Jobs

- PrizeWinningStatusChanged;
- PrizeTaxYearSummaryUpdated;
- value-report/reconciliation jobs;
- notification requests after commit;
- dead-letter/manual review for exhausted downstream retries.

#### Provider Integration

None confirmed. If fulfillment is manual for MVP, `fulfilled` requires a documented approved manual evidence reference/actor flow. Automated provider fulfillment is disabled until architecture assigns a provider owner/adapter.

#### UI / Admin Surface

Winner-facing where current product supports it:

- safe prize name/value;
- status;
- tax/confirmation next action;
- fulfillment state.

Admin:

- winning queue;
- run/rules evidence refs;
- minimal tax readiness;
- hold ID/safe reason;
- allowed transition controls;
- reconciliation/failure indicators;
- no raw provider/tax documents.

#### Failure Behavior

- Tax service unavailable → safe pending/retry, no approval/fulfillment;
- active hold → blocked/denied according to owner policy;
- hold release → re-evaluate, never auto-approve by inference;
- Notification failure → state unchanged;
- aggregate failure → winning truth remains; reconciliation repairs summary;
- duplicate SH-118 report → idempotent prior result;
- fulfillment evidence missing → deny transition;
- provider unavailable/unowned → automated fulfillment unavailable.

#### Tests

- unit transition matrix/mapping/value recognition;
- contract tests SH-019/011/012/118/041;
- integration pending tax → approved → fulfilled;
- active hold blocking tests;
- aggregate incremental vs full rebuild;
- taxable report replay/idempotency;
- notification outage isolation;
- sensitive access/authz/step-up;
- legal-policy fixtures for enabled jurisdiction;
- manual fulfillment evidence path if MVP uses it.

#### Documentation Updates

If U-CL10-12 or fulfillment evidence/provider architecture is resolved, update Module/Cluster architecture before enabling those branches.

#### Acceptance Criteria

- impossible to fulfill from pending_tax/blocked;
- active hold blocks prohibited fulfillment;
- PrizeTaxYearSummary exactly reconciles to recognized source values;
- SH-118 receives each source value once;
- notification/provider failure cannot fabricate fulfillment;
- no Tax/Hold/Notification truth is copied locally.

#### Exit Gate

All tax/hold/aggregate/idempotency/security tests pass for the exact enabled jurisdiction/fulfillment scope. Any unsupported provider/legal branch remains disabled and explicitly documented.

---

## Phase 5 — Module Integration, Privacy, and Boundary Proof

### 08 Real Cross-Module Contracts and Sweepstakes Privacy Executor

#### Objective

Replace Sweepstakes contract fakes with real neighboring Module interfaces where available, implement the Privacy owner protocol for Sweepstakes data, and prove normal workflows contain no direct cross-domain persistence coupling.

#### Observable Result

- real qualifying purchase outcome creates PrizeEntry without Stripe coupling;
- real Consent/Hold/Tax/Notification contracts drive workflows;
- Privacy can enumerate/export/erase/anonymize/retain Sweepstakes-owned subject data through owner executors;
- integration tests detect forbidden cross-domain Prisma access;
- correlation IDs trace source event → entry/draw/winning → downstream requests.

#### Cluster Build-Plan Link

Sweepstakes-specific implementation of **CL-10 Feature 10 — Cross-Cluster Integration, Privacy Executor, and Boundary Verification**.

#### Dependencies

- Features 01–07;
- production-ready or contract-complete neighboring interfaces;
- SH-095, 096, 097, 098;
- actual root observability/audit/notification implementations or stable public contracts.

#### In Scope

- replace mocks/fakes with real SH-001/002/008/009/011/012/019/041/118 contracts where available;
- real Order/payment-owner qualifying event contract;
- Privacy subject-data enumerator;
- Privacy instruction executor;
- retention fact provider;
- approved anonymization field map;
- export serializer for permitted subject data;
- correlation propagation;
- cross-module contract/integration tests;
- dependency boundary checks.

#### Out of Scope

- redesigning neighboring Modules;
- creating PrivacyRequest/DataErasureJob;
- creating DataRetentionExemption;
- solving generic fraud platform ownership;
- adding Track entitlement dependency merely because CL-10 Cluster has the rail;
- new provider types.

#### Module-Owned Data

Privacy covers Module-owned records and approved run-proof record:

- PrizeEntry;
- PrizeWinning;
- PrizeTaxYearSummary;
- PrizeDrawing/entry-method records only where subject association/export meaning exists;
- drawing-run subject references after approved schema.

#### Public Interfaces

- SH-096 enumeration implementation;
- SH-095 instruction execution implementation;
- SH-097 retention facts;
- owner field-map supplied to SH-098;
- real inbound/outbound contracts from earlier features.

#### Shared Operations Used

- **SH-095** execute privacy instruction; no local privacy job.
- **SH-096** enumerate subject data; no generic DB crawler.
- **SH-097** provide retention facts; Privacy stores exemption.
- **SH-098** approved anonymization mapping; no blanket delete.
- revalidate all earlier SH operations with real contract implementations.

#### Domain Logic

Privacy enumeration identifies records by subject and supported dispositions without exposing another Module’s owned records as Sweepstakes inventory.

Potential dispositions must be explicit:

- export;
- retain;
- anonymize/pseudonymize approved fields;
- detach optional references when permitted;
- erase only where owner invariants/retention allow.

Activated/completed prize evidence must not be destroyed merely to satisfy a generic delete request. Return retention facts to Privacy and let Privacy record the exemption.

Cross-module integration must not “fill missing data” by querying another Module’s Prisma models.

#### Authorization / Compliance

- Privacy calls are trusted orchestrator/system context under Privacy protocol;
- exports/minimized DTOs observe subject authorization and data classification;
- tax/winner sensitive data minimized;
- no paid entitlement odds effects introduced.

#### Database / Transaction Behavior

- privacy executor is idempotent per instruction/target;
- anonymization uses versioned mapping and preserves relational/compliance invariants;
- retained records return structured retained result rather than silent success;
- cross-module side effects use canonical idempotency/retry contracts.

#### Events / Jobs

- Privacy jobs remain Privacy-owned; Sweepstakes returns results;
- any owner event after anonymization/retention follows approved privacy/event policy;
- correlation IDs preserved across event/jobs/downstream calls.

#### Provider Integration

None. If future provider resources exist, their privacy deletion belongs to the provider owner and must be added only after architecture approval.

#### UI / Admin Surface

No new customer UI required. Optional internal view may show safe contract/worker/privacy executor status but must not become source truth.

#### Failure Behavior

- unsupported privacy disposition → structured unsupported/retained result;
- executor failure → structured retryable/permanent result to Privacy; no local job state;
- incompatible neighbor event version → dead-letter, no partial owner mutation;
- neighbor unavailable → valid pending/no-op state + operational failure;
- downstream timeout after possible commit → query/idempotency/reconciliation, not blind destructive retry.

#### Tests

- real contract tests;
- E2E purchase event → PrizeEntry;
- E2E winner → tax/hold → notification request;
- Privacy enumerate/export/anonymize/retain/erase fixtures;
- retention exemption handoff tests;
- architecture import scan for cross-domain Prisma/provider imports;
- correlation/replay tests;
- authorization/security tests.

#### Documentation Updates

Update public-interface docs if real neighboring contracts differ from placeholders while preserving ownership semantics. Update privacy/retention section when approved disposition matrix is established.

#### Acceptance Criteria

- all production-enabled Sweepstakes dependencies use explicit owner contracts;
- no Stripe/Payment repository coupling exists;
- Privacy can enumerate and execute supported owner dispositions;
- retained legal/tax evidence is reported to Privacy rather than deleted;
- normal workflows contain no direct cross-domain Prisma access;
- contract/E2E tests pass.

#### Exit Gate

Feature passes when real contract integration and Privacy tests pass for all production-enabled Sweepstakes flows and architecture-boundary checks report no forbidden dependencies.

---

## Phase 6 — Production Hardening and Reconciliation

### 09 Sweepstakes Production Hardening, Recovery, and Launch Verification

#### Objective

Harden the exact enabled Sweepstakes scope against duplicate entries/runs/winners, stale transitions, downstream outages, privacy/security failures, projection drift, migration issues, and accidental activation of unresolved legal/provider behavior.

#### Observable Result

- retries/replays cannot duplicate entries, draw runs, winners, summary values, tax reports, notifications, or fulfillment effects;
- admin can inspect safe run/reconciliation/failure state through owner/Ops interfaces;
- stale/failed worker states have documented recovery paths;
- disabled legal/provider/redraw branches remain visibly unavailable;
- full reconciliation proves summary/source consistency.

#### Cluster Build-Plan Link

Sweepstakes-specific portion of **CL-10 Feature 11 — CL-10 Production Hardening and Reconciliation**.

#### Dependencies

- Features 01–08;
- every architecture decision required by the enabled launch scope approved;
- unresolved items remain disabled/draft and documented.

#### In Scope

- all lifecycle transition race tests;
- command/event replay matrices;
- free/purchase entry concurrency/load;
- drawing-run concurrency and crash recovery;
- PrizeTaxYearSummary full reconciliation/backfill;
- missing taxable-value re-report using SH-118 idempotently;
- stale `drawing`/pending winning recovery procedure based on run proof;
- queue retry/dead-letter operational procedures;
- authorization/step-up/security review;
- rate limits for public entry endpoint;
- privacy/export/retention verification;
- audit/sensitive-access coverage;
- telemetry redaction/cardinality checks;
- query/index/performance tests;
- schema/migration/reset/backup-restore rehearsal for owned records;
- fail-closed feature flags/configuration for unresolved legal/provider/redraw branches.

#### Out of Scope

- new reward/provider types;
- redraw/replacement unless U-CL10-11 is separately resolved;
- generic fraud/risk platform;
- Search/analytics features unrelated to Sweepstakes correctness;
- changing neighboring Module ownership.

#### Module-Owned Data

Review indexes/constraints for:

- PrizeDrawing status/timing;
- entry method status/type;
- PrizeEntry drawing/source, user/time, Order, method, token;
- approved run-proof keys/constraints;
- PrizeWinning drawing/status, user/time, TaxProfile;
- PrizeTaxYearSummary unique user/year/currency and reporting indexes.

No denormalized source truth solely for performance.

#### Public Interfaces

Freeze/version all production-enabled contracts. Add owner-only reconciliation/inspection commands only where needed:

- reconcile yearly summary;
- inspect/retry failed owner jobs through canonical Ops/queue mechanisms;
- query run evidence;
- re-report missing value idempotently;
- inspect stuck winning state without direct row mutation.

#### Shared Operations Used

Revalidate all consumed canonical operations, especially:

- SH-032/033/034 telemetry safety;
- SH-037/038 failures/queue state;
- SH-044/045 replay safety;
- SH-047/048 retry/dead-letter;
- SH-051 concurrency;
- SH-095–098 privacy/retention;
- SH-116 selection;
- SH-117 aggregate rebuild;
- SH-118 taxable-value reporting.

Do not introduce “hardening” helpers that duplicate them.

#### Domain Logic

Hardening checklist:

- every status transition has explicit current-state validation;
- every entry source has semantic idempotency key;
- entry limits hold under concurrent load;
- run proof survives worker crash/restart and prevents blind rerun;
- a stuck `drawing` state can only be recovered from immutable run evidence, never by selecting again without proof;
- summary rebuild exactly matches recognized PrizeWinning values;
- failed SH-118 handoff can be reconciled/reported once;
- public entry endpoints resist abusive retry/velocity through root controls without inventing a fraud platform;
- no user can enumerate another user’s entries/winnings;
- admin sensitive reads are audited where required;
- disabled redraw/provider/legal branches cannot be activated by ordinary UI/API roles;
- migration/backfill scripts are idempotent/resumable where possible.

#### Authorization / Compliance

- verify all admin actions use SH-002;
- verify root step-up classification for drawing/fulfillment high-risk actions;
- verify AMOE/no-paid-odds across all enabled paths;
- verify exact enabled jurisdictions have approved policy;
- verify no entitlement/points/reward path affects odds;
- verify tax-sensitive fulfillment uses fresh owner decision;
- verify retention behavior with Privacy/legal owner.

#### Database / Transaction Behavior

- load/concurrency tests on real Postgres transaction strategy;
- index plans for entry count and frozen population queries;
- migration rollback/forward-fix analysis;
- no destructive cascade through normal application lifecycle;
- backfill/reconciliation uses cursors/batches and canonical job/idempotency mechanisms.

#### Events / Jobs

- chaos/degradation tests for source events, Payment/Tax, Hold, Notification, queue;
- dead-letter replay preserves correlation and dedupe;
- reconciliation dry-run before repair where appropriate;
- source-of-truth remains valid through downstream outage.

#### Provider Integration

No provider should appear unless explicitly approved before this phase. Any approved adapter is tested for webhook security/dedupe/reconciliation in its provider owner, not improvised here.

#### UI / Admin Surface

Optional internal operations visibility:

- failed/retryable owner jobs linked to canonical Ops records;
- drawing run status/evidence summary;
- stuck pending winning review;
- summary last reconciliation;
- safe downstream failure indicators;
- disabled-feature/legal-gate explanation.

No duplicate QueueJob/IntegrationFailure tables in Sweepstakes.

#### Failure Behavior

- infrastructure outage → safe pending/no-op/retry, never fabricated success;
- projection/summary drift → rebuild, not source rewrite;
- stale run → recover from run proof;
- privacy executor failure → return to Privacy orchestrator for retry;
- migration failure → documented rollback/forward-fix;
- unresolved legal/provider decision → branch remains disabled.

#### Tests

- full unit regression;
- all public contract tests;
- concurrency/load suite;
- command/event idempotency/replay;
- retry/dead-letter/reconciliation;
- security/authz/step-up;
- AMOE/no-paid-odds/tax-hold compliance;
- Privacy export/anonymize/retain/erase;
- telemetry redaction;
- migration/reset/seed/backfill;
- E2E free entry → secure draw → tax-aware fulfillment;
- E2E purchase event → entry → same draw path;
- forced downstream outage tests.

#### Documentation Updates

- final enabled scope in Module/Cluster architecture;
- progress tracker;
- migration/backfill runbook if repository context includes one;
- unresolved decisions list trimmed only when formally resolved.

#### Acceptance Criteria

- no duplicate business effect under replay/concurrency tests;
- full summary reconciliation equals source truth exactly;
- all downstream outages preserve valid owner states;
- sensitive payloads absent from telemetry;
- all production-enabled behavior has resolved architecture/legal prerequisites;
- deferred branches are disabled and documented;
- no prohibited duplicate implementation exists.

#### Exit Gate

Sweepstakes / Prize is production-ready for the explicitly enabled scope only when typecheck, lint, unit, integration, concurrency, privacy, security, migration, and E2E checks pass; reconciliation is exact; required audit/step-up/privacy controls are proven; and no enabled path depends on U-CL10-01/02/11/12 or another unresolved decision.

---

# MODULE INTEGRATION PHASE

Phase 5 / Feature 08 is the explicit Module integration proof. It must exercise public contracts rather than neighboring tables.

Minimum production bridges:

```text
Identity / Role
→ Sweepstakes actor and authority

Consent & Disclosure
→ exact rules/disclosure version + proof

Transaction / Order or Payment owner
→ qualifying purchase outcome event

Sweepstakes
→ PrizeEntry
→ secure draw / PrizeWinning

Payment / Payout / Tax
→ tax readiness
← recognized prize value

Admin Review / Compliance Hold
→ applicable hold decisions
← justified hold requests

Sweepstakes
→ Notification request
→ Audit / sensitive access request
→ Observability telemetry

Privacy / Data Erasure
→ subject-data instruction
← owner enumeration / disposition result
```

Required contract/integration tests:

- qualifying purchase event version compatibility;
- source event replay → one PrizeEntry effect;
- consent proof version mismatch denial;
- hold active/released facts → local re-evaluation without direct hold mutation;
- tax readiness outage/recovery;
- SH-118 duplicate report protection;
- Notification outage does not alter PrizeWinning;
- Privacy retain/anonymize/export/erase results;
- code-level prohibition of direct cross-domain Prisma imports.

---

# MODULE HARDENING PHASE

Phase 6 / Feature 09 is limited to Sweepstakes-specific production hardening:

- lifecycle races and stale transitions;
- command/event replay;
- entry-limit concurrency;
- run lock and crash recovery;
- secure random selection integration;
- immutable evidence integrity;
- yearly aggregate reconciliation;
- tax-value handoff reconciliation;
- provider/downstream outage safety;
- public endpoint security/rate limits;
- sensitive winner/tax access;
- privacy/retention;
- audit completeness;
- telemetry safety;
- migration/backfill/restore behavior;
- performance of entry counts/frozen population/run evidence queries;
- fail-closed legal/provider/redraw scope.

Hardening does not create a generic risk, tax, provider, or CL-10 lifecycle system.

---

# PHASE SUMMARY

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Contracts and Source-of-Truth Foundation | 01–02 |
| 2 | Idempotent Entry Issuance | 03–04 |
| 3 | Secure Drawing and Winner Truth | 05–06 |
| 4 | Winning, Tax, Holds, and Fulfillment | 07 |
| 5 | Module Integration, Privacy, and Boundary Proof | 08 |
| 6 | Production Hardening and Reconciliation | 09 |

**Total numbered Module features: 9**

### Cluster mapping

| Module feature | CL-10 build-plan support |
|---|---|
| 01 | prerequisite for Cluster 06–10 |
| 02 | Cluster Feature 06 |
| 03–04 | Cluster Feature 07 |
| 05–06 | Cluster Feature 08 |
| 07 | Cluster Feature 09 |
| 08 | Cluster Feature 10 |
| 09 | Cluster Feature 11 |

The Module plan does not authorize Sweepstakes work ahead of the corresponding Cluster milestone.

---

# MODULE EXECUTION PATTERN

Before implementing each numbered feature:

1. Read root project overview.
2. Read root architecture and code standards when present.
3. Read Canonical Shared Operations Registry.
4. Read CL-10 architecture and build plan.
5. Read this Module architecture and implementation plan.
6. Read direct dependency public-interface sections required by the feature.
7. Inspect current Prisma schema/migrations and progress tracker.
8. Confirm the prior feature exit gate.
9. Confirm all architecture blockers for the feature are resolved or the production branch is explicitly disabled.
10. Write the Required Feature Implementation Specification.
11. Implement only the numbered feature.
12. Run feature-specific tests plus standard quality checks.
13. Verify public contracts and forbidden-boundary checks.
14. Update progress.
15. Update architecture only when a binding decision legitimately changes.
16. Record unresolved risks/deferred branches.

Do not start the next numbered feature because “most of this one works.” The exit gate is the handoff boundary.

---

# REQUIRED FEATURE IMPLEMENTATION SPECIFICATION

Immediately before coding a numbered feature, the coding agent must produce a concise specification containing:

- **Feature:** number and name.
- **Objective:** one result.
- **Observable result:** what can be verified after implementation.
- **Cluster build-plan link:** exact CL-10 feature/milestone.
- **Dependencies:** prior Module features, public interfaces, SH operations, schema/migrations, legal/architecture gates.
- **In scope:** exact work for this feature.
- **Out of scope:** neighboring truth and deferred work.
- **Owned data affected:** Module models/enums/run-proof records/events.
- **Public contracts:** commands, queries, events, Privacy executor changes.
- **Shared operations consumed:** SH ID, owner, invocation, local policy, prohibited duplicate.
- **Permissions/compliance:** actor, authorization, consent, AMOE, odds, Hold, Tax, step-up, privacy as applicable.
- **Primary workflow:** ordered command/query/event path.
- **Provider integration:** normally none; if present, cite approved provider ownership decision.
- **Jobs/events:** payload, owner, retry/dead-letter, outbox, correlation.
- **Idempotency/concurrency:** semantic key, lock/resource, transaction boundary, replay result.
- **Error behavior:** stable denial/conflict/dependency categories.
- **Tests:** exact unit/contract/integration/concurrency/privacy/E2E categories.
- **Acceptance criteria:** observable requirements.
- **Documentation updates:** files/ADR/schema docs that must change.

Do **not** generate specifications for all future features in advance. The specification must reflect the repository state immediately before that feature begins.

---

# REQUIRED COMPLETION REPORT

After each numbered feature, the coding agent must report:

- Feature completed;
- Files added;
- Files changed;
- Database changes;
- Migrations;
- Dependencies added;
- Module public interfaces added/changed;
- Shared Operations reused by SH ID;
- Events/jobs added;
- Provider adapter changes, normally `none` unless explicitly approved;
- Tests added/changed;
- Commands run;
- Manual/contract/E2E verification;
- Documentation updated;
- Assumptions;
- Known failures;
- Remaining risks;
- Deferred work;
- Unresolved architecture blockers still applicable;
- Exit-gate result: **PASS / BLOCKED**, with evidence.

A completion report must explicitly state when a provider, cross-domain repository, local idempotency helper, local queue, local hold flag, or local consent/tax implementation was **not** created because the canonical owner was reused.

---

# FINAL QUALITY CHECK

Before declaring this Module implementation plan complete or using it as coding context, verify:

1. PrizeDrawing, SweepstakesEntryMethod, PrizeEntry, PrizeWinning, and PrizeTaxYearSummary have exactly one owner.
2. Gamification / Rewards truth was not absorbed.
3. Order/payment truth was not absorbed.
4. TaxProfile/tax filing/provider truth was not absorbed.
5. ComplianceHold lifecycle was not absorbed.
6. Consent proof/version truth was not copied.
7. Notification and Audit remain support capabilities, not prize truth.
8. Privacy orchestration remains Privacy-owned.
9. No baseline Track entitlement dependency can change chance odds.
10. Canonical SH operations are referenced by permanent IDs and reused.
11. `entryToken` uniqueness is not mistaken for source idempotency.
12. Entry-limit concurrency uses database/shared persistence mechanisms.
13. SH-116 is the only approved selection mechanism.
14. Production activation is blocked until immutable rules evidence exists.
15. Production selection is blocked until immutable drawing-run proof exists.
16. Redraw/replacement remains disabled until approved.
17. Exact legal thresholds/jurisdictions are not invented.
18. Cross-Module reads use public contracts where appropriate.
19. Provider adapters do not become business truth and no unowned provider client is added.
20. Domain events, AuditEvent, and observability are distinct.
21. PrizeTaxYearSummary remains separate from TaxYearEarningsSummary and is rebuildable.
22. Every numbered feature has exact tests and an exit gate.
23. Feature ordering maps to CL-10 Features 06–11 rather than redefining Cluster sequencing.
24. A coding agent can execute each slice without inventing architecture.

