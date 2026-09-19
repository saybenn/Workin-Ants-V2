# Sweepstakes / Prize Module Architecture

> **Module ID:** `sweepstakes_prize`  
> **Module name:** Sweepstakes / Prize Module  
> **Module type:** `compliance_feature_ecosystem`  
> **Build status:** `mvp_active_legal_gated`  
> **Primary Cluster:** `CL-10` — Incentives, Rewards & Prize Economy  
> **Repository target:** `context/clusters/incentives, rewards & prize economy/sweepstakes-module/sweepstakes-prize-module-architecture.md`\
> **Document status:** Implementation-grade Module architecture derived from the current Workin Ants evidence set. Confirmed facts, inherited Proposed Rulings, and unresolved decisions are distinguished explicitly.  
> **Audience:** Coding agents, developers, reviewers, maintainers, architects, compliance reviewers, and operators implementing or reviewing this Module.

---

**Context routing and availability:** Follow [context/context-map.md](<../../../context-map.md>) for authority by concern and actual artifact paths; use [context/project-overview-v3.md](<../../../project-overview-v3.md>) as the overview entry point. Root architecture/build plan, `context/code-standards.md`, and the dedicated progress tracker are unavailable in the current context inventory. References below to those artifacts or their standards are conditional prerequisites, not evidence of an existing global sequence or approval. Do not invent missing root decisions or artifacts.

## 1. Module Header

### Relationship to root architecture

This document follows the authority-by-concern rules in `context/context-map.md`; root architecture and code standards are currently unavailable, and the overview provides product context. It does not redefine platform identity, authorization, consent, payment, tax, hold, notification, audit, privacy, queue, provider, or observability architecture.

The root rule that matters most here is **one owner per lifecycle**. The Sweepstakes / Prize Module owns chance-based drawing, entry, winning, prize-value, and prize-fulfillment-state truth. It consumes other owners through their public interfaces rather than rebuilding their records or interpreting their provider state.

### Relationship to CL-10 architecture

This file narrows CL-10 to the `sweepstakes_prize` Deep Module. CL-10 coordinates this Module with `gamification_rewards`, but the Cluster owns no lifecycle and no generic incentive repository. The Cluster's non-blurring rule is binding here:

```text
PrizeEntry != PointLedgerEntry
PrizeWinning != RewardRedemption
PrizeDrawing != GamificationProgram
```

### Evidence basis

This architecture is grounded in the current:

- Module Architecture Extract already established in this thread;
- Deep Module Registry;
- Cluster Registry v2.3;
- current Prisma schema;
- Ubiquitous Language / Compliance Inventory;
- Canonical Shared Operations Registry;
- CL-10 `architecture.md`;
- CL-10 `build-plan.md`;
- Workin Ants project overview.

Where these sources leave a material decision unresolved, this file preserves the blocker rather than inventing production behavior.

### Update rule

Update this file when any binding change affects:

- Module ownership;
- Prisma meaning or relationships;
- lifecycle transitions;
- public commands, queries, or event contracts;
- AMOE/equivalent-odds policy;
- immutable rules or drawing-run proof;
- tax/hold fulfillment composition;
- privacy/retention behavior;
- provider ownership;
- canonical Shared Operations consumed by this Module.

Build progress must not silently redefine this architecture.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own the Workin Ants source of truth for chance-based prize campaigns: drawing configuration and lifecycle, lawful entry methods, individual PrizeEntry issuance, winner selection, PrizeWinning lifecycle, prize fair-market-value snapshots, yearly prize-value aggregation, and prize-fulfillment-state decisions.

### Goal

Turn a legally and operationally valid chance-based campaign plus qualifying entry facts into auditable entries, one secure drawing outcome, and tax/hold-aware prize fulfillment **without** turning payment, points, subscriptions, consent, provider state, notification delivery, or audit logs into prize truth.

### What enters

- authenticated or system actor context;
- Role / Authority decisions for protected actions;
- drawing and entry-method configuration;
- approved official-rules evidence and exact consent version/proof;
- free-entry requests;
- authorized mail-in/admin/system entry facts;
- authoritative qualifying Order/payment-owner domain events where a purchase-triggered method is configured;
- ComplianceHold decisions;
- Payment / Payout / Tax readiness decisions;
- recognized-value reporting acknowledgments;
- Privacy owner instructions;
- canonical job, idempotency, locking, audit, notification, and telemetry mechanisms.

### What leaves

- `PrizeDrawing` state;
- `SweepstakesEntryMethod` configuration/state;
- `PrizeEntry` truth and eligibility evidence;
- immutable drawing-run evidence once U-CL10-02 is resolved;
- `PrizeWinning` truth and fulfillment state;
- `PrizeTaxYearSummary` aggregate;
- versioned domain events;
- hold requests when justified;
- taxable-value reports to Payment / Payout / Tax;
- notification requests;
- audit and sensitive-access requests;
- Privacy executor results;
- safe operational telemetry.

### Business transformation

```text
approved drawing/rules configuration
+ active lawful entry methods
+ authenticated/authorized actor or authoritative source event
+ exact consent proof where required
+ owner-controlled eligibility and limit policy

→ PrizeEntry truth

closed drawing
+ frozen eligible population
+ equivalent-odds validation
+ lock/idempotency
+ SH-116 secureRandomSelection
+ immutable run proof

→ PrizeWinning truth

PrizeWinning
+ Payment/Tax readiness
+ ComplianceHold decision
+ fulfillment evidence

→ approved / fulfilled / forfeited / cancelled prize outcome
+ PrizeTaxYearSummary
+ taxable-value handoff
```

### Why this is a separate Module boundary

Chance-based prize participation has distinct legal controls, source records, failure modes, audit requirements, tax coordination, and concurrency hazards. Those rules cannot safely live inside ordinary gamification, Order, payment, Notification, or a generic “incentive service.” The separate boundary keeps deterministic rewards from accidentally becoming paid prize odds and keeps provider/financial state from becoming winner truth.

---

## 3. Owned Truth

### 3.1 Owned models

#### `PrizeDrawing`

The campaign/container for a giveaway, sweepstakes, contest, or other chance-based drawing. `PrizeDrawing.status` is drawing lifecycle truth. It owns timing, prize description/value configuration, AMOE/no-purchase configuration, entry-limit configuration, and owner-defined eligibility configuration.

#### `SweepstakesEntryMethod`

One configured route by which entries may be issued for a drawing. It owns method type, status, free/purchase semantics, configured entries awarded, and the owner assertion about odds equivalence.

#### `PrizeEntry`

One auditable user entry into a specific drawing. It is not an Order, point, reward, consent record, or “ticket balance.” It records source, entry method, optional Order provenance, consent proof reference, token, eligibility state, ineligibility reason, weight, and issue time.

#### `PrizeWinning`

The authoritative Workin Ants record that a User won a prize and the lifecycle of that prize outcome. It snapshots the prize name, fair-market value, currency, tax year, tax-reporting metadata, optional TaxProfile/ComplianceHold references, and fulfillment timestamps/state.

#### `PrizeTaxYearSummary`

Sweepstakes-owned yearly aggregate of recognized prize fair-market value and winning count for one User, tax year, and currency. It supports reconciliation and tax handoff but is not TaxProfile, TaxYearEarningsSummary, or tax filing truth.

### 3.2 Owned enums/statuses

- `PrizeDrawingStatus`
  - `draft`
  - `active`
  - `closed`
  - `drawing`
  - `completed`
  - `cancelled`
- `SweepstakesEntryMethodType`
  - `purchase_triggered`
  - `free_daily_button`
  - `mail_in`
  - `admin_adjustment`
  - `system`
- `SweepstakesEntryMethodStatus`
  - `active`
  - `paused`
  - `retired`
- `PrizeEntrySource`
  - `purchase`
  - `free_daily`
  - `mail_in`
  - `admin_adjustment`
  - `system`
- `PrizeWinningStatus`
  - `pending_tax`
  - `pending_confirmation`
  - `approved`
  - `fulfilled`
  - `blocked`
  - `forfeited`
  - `cancelled`

### 3.3 Lifecycles owned

- PrizeDrawing lifecycle;
- SweepstakesEntryMethod lifecycle;
- PrizeWinning lifecycle;
- PrizeEntry issuance/eligibility behavior even though PrizeEntry has no status enum;
- yearly prize-value aggregation/reconciliation policy.

### 3.4 Domain events/ledgers owned

No current Prisma model is an explicit Sweepstakes domain-event ledger. Domain events must be published through SH-046 transactional outbox infrastructure, while source records above remain truth.

The following event vocabulary is proposed for implementation contracts and may be renamed to repository conventions without changing semantics:

- `PrizeDrawingActivated`
- `PrizeDrawingClosed`
- `PrizeDrawingCancelled`
- `PrizeEntryIssued`
- `PrizeEntryEligibilityChanged`
- `PrizeDrawingRunStarted`
- `PrizeDrawingCompleted`
- `PrizeWinningCreated`
- `PrizeWinningStatusChanged`
- `PrizeTaxYearSummaryUpdated`

Events describe facts that occurred; they do not command another Module to mutate its truth.

### 3.5 Projections/snapshots/proof owned

- `PrizeTaxYearSummary` is a rebuildable Sweepstakes-owned aggregate.
- `PrizeWinning` contains historical FMV/tax metadata snapshots for the winning outcome.
- Immutable official-rules proof is required but its final Module-owned schema is unresolved under **U-CL10-01**.
- Immutable drawing-run proof is required but its final Module-owned schema is unresolved under **U-CL10-02**.

### 3.6 Policies and invariants owned

The Module owns:

- AMOE/no-purchase composition policy for a drawing;
- free/purchase entry-method compatibility;
- effective odds/weight policy;
- per-user/free/paid/max entry limits;
- entry eligibility and correction policy;
- source-event-to-entry issuance semantics;
- eligible-population freeze policy;
- winner count/weighting/replacement behavior once approved;
- PrizeWinning transition policy;
- prize FMV recognition and inclusion policy for `PrizeTaxYearSummary`;
- mapping external Tax/Hold facts to local prize state;
- the point at which fulfillment becomes `fulfilled` after authoritative evidence.

---

## 4. Explicit Non-Ownership

This Module must **not** own or duplicate the following.

| Adjacent owner | Remains owned there | Sweepstakes may consume | Forbidden local duplicate |
|---|---|---|---|
| Identity & Access | User authentication, session, security posture, step-up challenge/session | SH-001, SH-014 | `prizeAuth.ts`, local session parser, local MFA state |
| Role / Authority | permission interpretation | SH-002 | `isSweepstakesAdmin`, prize role table/engine |
| Consent & Disclosure | consent version catalog and `ConsentLog` proof | SH-008/009 | local rules-consent table/checker/version resolver |
| Transaction / Order | Order lifecycle and qualifying commerce facts | versioned Order/payment-owner event/query | direct Order state mutation, local payment confirmation |
| Payment / Payout / Tax | Stripe/webhook truth, TaxProfile, tax provider state, tax filing/reporting lifecycle | SH-019, SH-118 | Stripe webhook, `ProcessedStripeEvent`, W-9 checker, filing service |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and release | SH-011/012 | local blocked table/boolean/hold service |
| Gamification / Rewards | points, challenges, rewards, RewardRedemption | approved event/contract only | points-to-ticket ledger, RewardRedemption mutation |
| Track Subscription & Entitlement | subscription/grant/usage truth | only approved contract if ever needed | premium/odds flag, local entitlement lookup |
| Notification | Notification and NotificationDelivery lifecycle, provider routing | SH-041 | winner email/SMS/push provider client |
| Audit / Event Ledger | generic AuditEvent and AccessAuditLog | SH-029/030 | `prizeAudit` table/repository, local access log |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob orchestration and exemption records | SH-095–098 | local privacy workflow/job/exemption table |
| Observability / Ops | logging, failures, queue telemetry, incidents | SH-032/033/034/037/038 | local queue/failure/incident truth |
| Shared platform persistence | idempotency, inbox/outbox, locks, lifecycle plumbing, jobs/retries | SH-044–048, 051, 053 | local idempotency/lock/retry/event-bus frameworks |
| Legal/compliance governance | drafting/approval of official rules and exact jurisdiction policy | approved evidence/policy version | legal authoring/rule engine invented by this Module |

### Provider boundary

The current evidence confirms **no external provider integration owned by Sweepstakes / Prize**. In particular:

- no Stripe client/webhook here;
- no tax-provider client here;
- no notification-provider client here;
- no external RNG provider is required;
- a future physical/gift-card/shipping fulfillment adapter requires an explicit ownership and proof ruling before implementation.

---

## 5. Module Architecture Principles

1. **Chance truth is local; supporting facts are external.** Order, Consent, TaxProfile, ComplianceHold, Notification, and provider records may support a prize decision but never replace PrizeEntry/PrizeWinning truth.
2. **AMOE is enforced by the owner.** A flag saying `amoeEnabled=true` is not enough; activation must validate the actual configured active entry paths.
3. **Equivalent odds are behavioral, not cosmetic.** `oddsEquivalent`, `entriesAwarded`, and `PrizeEntry.weight` must agree with the approved policy.
4. **No paid-plan/points/reward odds boost.** Track entitlement, point balances, RewardRedemption, or other paid benefits cannot improve chance-based odds absent explicit approved legal architecture.
5. **Entries are issuance records, not mutable counters.** Corrections are explicit and auditable; entries are not deleted to “fix” totals.
6. **Source-event idempotency is separate from token uniqueness.** `entryToken @unique` does not prove a purchase/free request was processed once.
7. **Drawing execution is single-run, lock-protected, and evidence-backed.** Never use transient memory, logs, or AuditEvent as the only drawing proof.
8. **Use SH-116 only for selection.** No `Math.random()` and no ad hoc raffle helper.
9. **Notification is downstream.** A delivered winner message does not create a winner or fulfill a prize.
10. **Tax/Hold facts are inputs; local transition remains local.** External owners never update `PrizeWinning.status` directly.
11. **Tax summaries are reconciliable.** `PrizeTaxYearSummary` must be rebuildable from recognized winning truth.
12. **Production legal gates fail closed.** Draft configuration may exist, but activation/drawing/fulfillment cannot guess through missing legal or architecture decisions.
13. **No destructive cleanup of evidence by convenience.** Activated/completed drawing evidence requires retention analysis before delete/cascade behavior is used.
14. **Cross-Module reads use public contracts.** Prisma relations do not grant permission to read another Module’s repository directly.
15. **Observability and audit are support evidence only.** They cannot be used to infer business lifecycle state.

---

## 6. Proposed Folder / Code Structure

The final repository convention is inherited from root `code-standards.md` when present. Until then, the CL-10 proposed Module organization is the binding planning shape:

```text
src/
  modules/
    sweepstakes-prize/
      domain/
        policies/
          drawing-policy.ts
          entry-method-policy.ts
          entry-eligibility-policy.ts
          prize-winning-policy.ts
          tax-value-policy.ts
        types/
          decisions.ts
          reason-codes.ts
      application/
        commands/
          configure-prize-drawing.ts
          configure-entry-method.ts
          activate-prize-drawing.ts
          close-prize-drawing.ts
          cancel-prize-drawing.ts
          issue-prize-entry.ts
          correct-prize-entry-eligibility.ts
          run-prize-drawing.ts
          transition-prize-winning.ts
          reconcile-prize-tax-year-summary.ts
        queries/
          get-prize-drawing.ts
          list-entry-methods.ts
          get-user-drawing-entries.ts
          get-prize-winning.ts
          get-prize-tax-year-summary.ts
          get-drawing-run-evidence.ts      # only after U-CL10-02 is resolved
        services/
          prize-entry-service.ts
          drawing-execution-service.ts
          prize-fulfillment-service.ts
      contracts/
        public.ts
        events.ts
        privacy.ts
        inbound-events.ts
      infrastructure/
        repositories/
          prize-drawing-repository.ts
          entry-method-repository.ts
          prize-entry-repository.ts
          prize-winning-repository.ts
          prize-tax-year-summary-repository.ts
          drawing-run-repository.ts        # only after approved schema exists
        randomness/
          secure-random-selection.ts       # SH-116 implementation boundary over shared CSPRNG
      workers/
        scheduled-drawing-worker.ts
        prize-tax-summary-reconciliation-worker.ts
        prize-fulfillment-retry-worker.ts  # only for approved fulfillment effects
      privacy/
        subject-data-enumerator.ts
        privacy-instruction-executor.ts
        retention-facts.ts
      admin/
        ...thin admin composition if repository/UI conventions place Module UI here...
      tests/
        unit/
        integration/
        contract/
        concurrency/
        privacy/
```

### Folder rules

- Do not create `providers/` until this Module is explicitly assigned a provider.
- Do not create a `shared/` subfolder for generic auth, audit, queue, crypto, locks, idempotency, or notification.
- Do not create a generic `incentive-service.ts` shared with Gamification.
- Prisma access for Module-owned tables remains behind Sweepstakes repositories/application services.
- Cross-Module DTOs/events live in contracts, not Prisma model imports.
- UI/server actions remain thin adapters into application commands/queries.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery/UI | input gathering, display of safe owner DTOs, explicit admin/user actions | lifecycle policy, direct Prisma mutation, provider clients, legal decisions |
| Application commands | orchestration of one Sweepstakes mutation, transactions, SH calls, events | generic authentication, provider verification, another Module’s transition |
| Application queries | safe source-truth/read-model DTOs | cross-domain joins that recreate another owner’s policy |
| Domain policy | AMOE, equivalent odds, limits, eligibility, transition matrices, value inclusion | Consent truth, tax readiness rules, hold lifecycle, Role policy |
| Repositories | Prisma persistence for Module-owned records only | generic cross-domain repository or direct ownership of Order/Tax/Consent/Hold data |
| Workers | owner-specific scheduled/async commands | generic queue runner, retry engine, queue telemetry truth |
| Randomness | SH-116 sampling policy/adapter over shared CSPRNG | in-house PRNG, external provider state, redraw policy not yet approved |
| Contracts/events | stable public DTO/event schemas | Prisma models as external contracts, disguised cross-Module commands |
| Privacy executor | enumerate/act on owned records according to Privacy instruction | PrivacyRequest/DataErasureJob orchestration or exemption storage |
| Provider adapters | none confirmed | Stripe/tax/notification clients; future provider without explicit ruling |

---

## 8. Data Model

### 8.1 `PrizeDrawing`

**Purpose:** drawing/campaign source truth.

**Important fields:** `status`, `startsAt`, `endsAt`, `drawsAt`, `officialRulesUrl`, `prizeDescription`, `prizeValueCents`, `currency`, `noPurchaseNecessary`, `amoeEnabled`, three per-user limit fields, `eligibilityJson`.

**Relationships:** owns many PrizeEntry, PrizeWinning, and SweepstakesEntryMethod rows.

**Authoritative fields:** status/timing/drawing configuration and the drawing-level AMOE/limit policy inputs.

**Concurrency:** lifecycle transitions and entry/drawing execution require transaction/lock protection.

**Retention/privacy:** current PrizeEntry and SweepstakesEntryMethod relations cascade on drawing deletion. Because those rows are compliance/evidence-bearing, activated/closed/completed drawings must not be destructively deleted through ordinary application commands until retention policy explicitly permits it.

**Schema gap:** `officialRulesUrl` is a mutable reference, not immutable rules evidence. U-CL10-01 blocks production activation until resolved.

### 8.2 `SweepstakesEntryMethod`

**Purpose:** source truth for one entry route.

**Important fields:** `type`, `status`, `label`, `instructions`, `isFree`, `requiresPurchase`, `entriesAwarded`, `oddsEquivalent`.

**Relationships:** belongs to PrizeDrawing; may be referenced by PrizeEntry.

**Concurrency:** material changes around active drawings must be controlled and audited. Retired methods cannot issue new entries.

**Invariant-sensitive combinations:** `isFree`, `requiresPurchase`, method type, entriesAwarded, and oddsEquivalent must be validated together. `isFree=true && requiresPurchase=true` is invalid unless a future explicit policy proves otherwise.

### 8.3 `PrizeEntry`

**Purpose:** one issued chance entry.

**Important fields:** `drawingId`, `userId`, optional `orderId`, optional `entryMethodId`, optional `rulesConsentId`, `source`, unique `entryToken`, `isEligible`, `ineligibleReason`, `weight`, `createdAt`.

**Relationships:** belongs to drawing and User; optionally references Order and entry method. `rulesConsentId` currently has no Prisma relation.

**Uniqueness:** only `entryToken` is unique in the current schema. This does **not** prevent duplicate business issuance from retries/events.

**Concurrency-sensitive behavior:** per-user/free/paid/max limits must be checked and written atomically under a user+drawing or equivalent lock/transaction strategy.

**Retention:** normal owner services must not delete entries to adjust counts. Eligibility changes are explicit and auditable. Post-freeze mutation is prohibited without approved void/redraw policy.

**Open schema issue:** U-CL10-09 decides whether `rulesConsentId` becomes an FK. Runtime must validate proof through SH-008 regardless.

### 8.4 `PrizeWinning`

**Purpose:** winner and prize-fulfillment source truth.

**Important fields:** drawing/user IDs, optional hold and TaxProfile refs, prize name, FMV, currency, taxYear, physicalPrize, tax reporting snapshot fields, status, approved/fulfilled/forfeited timestamps.

**Relationships:** belongs to drawing and User; references ComplianceHold and TaxProfile without taking ownership.

**Concurrency:** winner creation must be part of one lock-protected drawing run. Fulfillment transitions require idempotency and state checks.

**Retention/privacy:** contains tax-related/value evidence and personal linkage; erasure/anonymization must use Privacy owner protocol and retention evaluation.

**Current schema gap:** PrizeWinning has no direct `prizeEntryId`/selected-entry reference. U-CL10-02 drawing-run proof must preserve selected winning references; whether PrizeWinning itself gains a direct FK is unresolved.

### 8.5 `PrizeTaxYearSummary`

**Purpose:** yearly Sweepstakes-owned aggregate.

**Uniqueness:** `@@unique([userId, taxYear, currency])`.

**Unresolved SH-117 mismatch (CL-10-R009):** this key has no jurisdiction dimension. Production SH-117 aggregation and jurisdiction-sensitive annual reporting remain blocked until an approved interpretation either constrains the applicable jurisdiction with authoritative evidence elsewhere or preserves jurisdiction in the aggregate structure. Neither solution is approved; do not assume a single jurisdiction or add a field during this reconciliation.

**Important fields:** FMV total, winning count, reporting threshold snapshot, reportingRequired, thresholdMetAt, optional TaxProfile ref.

**Concurrency:** incremental updates must be transaction-safe and idempotent; reconciliation must be able to fully rebuild the aggregate.

**Boundary:** it is not combined tax filing truth. Payment / Payout / Tax consumes recognized-value facts and owns TaxProfile/TaxYearEarningsSummary/reporting submission truth.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 PrizeDrawing lifecycle

**Inherited Proposed Ruling PR-CL10-06:** until approved, implementation that depends on the exact graph must treat it as an architecture checkpoint.

```text
draft → active | cancelled
active → closed | cancelled
closed → drawing | cancelled
drawing → completed
```

- `completed` and `cancelled` are terminal for ordinary operations.
- `drawing` is entered only by the owner drawing command under SH-051.
- no “reopen completed” behavior;
- redraw/replacement is blocked by U-CL10-11;
- status writes must use SH-053 transition plumbing with Module-owned policy.

### 9.2 SweepstakesEntryMethod lifecycle

**Proposed graph:**

```text
active ↔ paused
active → retired
paused → retired
```

`retired` is terminal. A retired method issues no new entries. Reactivation from paused is allowed only while the drawing policy permits configuration changes.

### 9.3 PrizeEntry behavior

PrizeEntry has no lifecycle enum.

Binding behavior from PR-CL10-07:

- issue once per business source semantics;
- record eligibility at issuance;
- corrections change eligibility through an audited command, not row deletion;
- frozen drawing population cannot be mutated underneath a run;
- source-event replay returns prior/no-op result;
- `entryToken` never substitutes for source-event idempotency.

### 9.4 PrizeWinning lifecycle

**Inherited Proposed Ruling PR-CL10-08:**

- fulfillment only from `approved`;
- `pending_tax` and `blocked` cannot fulfill;
- `fulfilled`, `forfeited`, and `cancelled` are terminal unless a future explicit correction model is approved;
- external tax/hold/provider facts never write the status directly;
- winner notification never advances status.

The precise transition matrix between `pending_confirmation`, `pending_tax`, `blocked`, and `approved`, including hold-release and claim-window behavior, remains dependent on approved legal policy and the Module implementation specification for Feature 07.

### 9.5 PrizeTaxYearSummary

Not a lifecycle. It is a derived aggregate with rebuild/reconciliation behavior through SH-117.

---

## 10. Commands

### `configurePrizeDrawing`

- **Purpose:** create/update a draft drawing.
- **Actor/context:** authenticated authorized admin/system.
- **Inputs:** drawing fields, declarative eligibility payload/version, rules evidence reference when available.
- **Preconditions:** actor/authorization; draft/editable state; validated timing/value/limits.
- **Writes:** PrizeDrawing.
- **Shared operations:** SH-001, 002, 009 where version resolution is needed, 029, 044, 046.
- **Idempotency:** repeated same command key replays prior result.
- **Failure:** validation, authorization, stale state, missing required version.

### `configureSweepstakesEntryMethod`

- **Purpose:** add/update a drawing entry method.
- **Preconditions:** editable drawing; coherent type/free/purchase/award/odds combination.
- **Writes:** SweepstakesEntryMethod.
- **Events/audit:** material configuration change event/audit as policy requires.
- **Failure:** invalid combination, active/closed drawing immutability, authorization.

### `setSweepstakesEntryMethodStatus`

Pause/reactivate/retire an entry method through owner transition rules. Retired is terminal.

### `activatePrizeDrawing`

- **Purpose:** move an eligible draft to active production entry state.
- **Hard gates:** U-CL10-01 resolved; rules snapshot/evidence; applicable consent version; AMOE/free path; equivalent odds; valid schedule; no unresolved legal launch block.
- **Shared operations:** SH-001/002/008/009/029/044/046; SH-072/077 only if the approved rules-proof design uses them.
- **Failure:** structured decision result with stable reason codes; draft remains intact.

### `closePrizeDrawing`

Closes new entry issuance after schedule/manual authorized close. Must be idempotent and cannot silently run the drawing.

### `cancelPrizeDrawing`

Cancels a non-completed drawing under owner policy, with reason/audit. It does not erase entries or evidence.

### `issuePrizeEntry`

- **Purpose:** issue one or configured count of entries for a valid method/source.
- **Actor/context:** user, authorized admin/system, or authoritative source event.
- **Preconditions:** active drawing/method/time, exact consent proof if required, eligibility, applicable hold decision, race-safe limits, equivalent odds.
- **Writes:** PrizeEntry.
- **Shared operations:** SH-008, 011, 044, 045 for event consumers, 051, 046, optional 041, 029 for admin path.
- **Idempotency:** business-source identity, not entry token.
- **Failure:** no entry on denial; stable reason code.

### `correctPrizeEntryEligibility`

Changes `isEligible`/reason through an audited, freeze-aware owner command. Does not delete/reissue the row casually.

### `runPrizeDrawing`

- **Purpose:** perform one secure drawing run.
- **Hard gates:** drawing closed; U-CL10-02 resolved; lock/idempotency; frozen eligible population; AMOE/equivalent odds revalidated.
- **Writes:** drawing-run proof (approved schema), PrizeWinning, PrizeDrawing state.
- **Shared operations:** SH-116, 051, 044, 046, 047/048, 029, 014 where required, 032–034.
- **Failure:** safe retry/no duplicate selection; no partial winners.

### `transitionPrizeWinning`

- **Purpose:** owner-controlled winning transition after local and external evidence.
- **Preconditions:** valid current state; authority/system context; tax/hold/fulfillment evidence as required.
- **Shared operations:** SH-019, 011/012, 118, 041, 029/030, 044/053.
- **Failure:** stale transition, missing tax readiness, active hold, missing fulfillment evidence.

### `reconcilePrizeTaxYearSummary`

Rebuilds/repairs the aggregate from recognized PrizeWinning truth using SH-117. It never writes Tax-owned summaries.

---

## 11. Queries / Decisions

### `getPrizeDrawing`

Returns owner source truth plus safe entry-method/rules-readiness metadata. Consumers must not infer legal approval from `officialRulesUrl` alone.

### `listAvailableEntryMethods`

Returns currently usable method DTOs for context. It is contextual availability, not a guarantee that a specific entry request will pass all gates.

### `evaluatePrizeEntryEligibility`

Returns a stable decision such as:

```text
allow | deny | review
reasonCodes[]
evidenceRefs[]
evaluatedAt
policyVersion
```

Consumers must not reconstruct eligibility from raw rows or frontend counts.

### `getUserDrawingEntries`

Returns authorized PrizeEntry truth/counts for the subject and drawing. It must not expose another User’s identifiers or raw consent/provider details.

### `getDrawingRunEvidence`

Available only after U-CL10-02 defines the record. Returns immutable run evidence to authorized admin/audit workflows; not raw secrets/random bytes beyond the approved evidence model.

### `getPrizeWinning`

Returns authorized winner truth and next-action facts. It must not expose raw TaxProfile/provider internals or imply tax readiness from `taxProfileId` alone.

### `getPrizeTaxYearSummary`

Returns Sweepstakes aggregate truth/checkpoint. Consumers must not treat it as tax filing truth.

---

## 12. Public Module Interface

### Public commands

- `configurePrizeDrawing`
- `configureSweepstakesEntryMethod`
- `setSweepstakesEntryMethodStatus`
- `activatePrizeDrawing`
- `closePrizeDrawing`
- `cancelPrizeDrawing`
- `issuePrizeEntry`
- `correctPrizeEntryEligibility`
- `runPrizeDrawing`
- `transitionPrizeWinning`
- `reconcilePrizeTaxYearSummary`

### Public queries/decisions

- `getPrizeDrawing`
- `listAvailableEntryMethods`
- `evaluatePrizeEntryEligibility`
- `getUserDrawingEntries`
- `getDrawingRunEvidence` after schema resolution
- `getPrizeWinning`
- `getPrizeTaxYearSummary`

### Emitted domain events

Use the event vocabulary in Section 3.4 with stable envelope/version/correlation semantics through SH-046.

### Privacy executor

Expose the Privacy-defined owner protocol:

- `enumerateSubjectData`
- `executePrivacyInstruction`
- `evaluateRetentionRequirement`
- owner-supplied anonymization map for SH-098.

### Provider-facing interfaces

None confirmed. Do not expose Stripe/tax/notification webhook/provider ports from this Module.

---

## 13. Inbound Dependencies

| Owner | Interface consumed | Why | Minimum information | Can block? | Must not copy |
|---|---|---|---|---|---|
| Identity & Access | SH-001 `resolveAuthenticatedActor` | actor identity | actor/user/system context | yes | session/auth helper |
| Role / Authority | SH-002 `authorizeResourceAction` | admin/user permission | action + target relationship facts | yes | role engine |
| Consent & Disclosure | SH-008/009 | rules/disclosure proof/version | proof ID/type/version/acceptedAt/validity; active version | yes | ConsentLog/version catalog |
| Transaction / Order | versioned qualifying commerce event/public query | purchase-triggered entry provenance | event ID/version, Order ID, subject, occurredAt, qualifying facts | yes/no-op | Order repository/state machine |
| Payment / Payout / Tax | SH-019, SH-118 | tax readiness and value handoff | separate readiness dimensions; report acknowledgment | yes | TaxProfile/provider interpretation |
| Admin Review / Compliance Hold | SH-011/012 | reusable stop sign | hold IDs/scope/reason; hold request result | yes | blocked flags/hold lifecycle |
| Notification | SH-041 | communicate entry/winner/tax/fulfillment facts | recipient/template/safe variables/idempotency | no business mutation | provider clients/delivery state |
| Audit / Event Ledger | SH-029/030 | privileged action/access proof | safe actor/action/target/result | no business mutation | audit repository |
| Privacy / Data Erasure | SH-095–098 protocol | privacy fulfillment | target instruction/subject/disposition | may require retain/anonymize | privacy jobs/exemptions |
| Observability / Ops | SH-032/033/034/037/038 | diagnostics/failure visibility | correlation IDs, safe operation/source refs | no business mutation | local ops tables/logger |
| Shared queue/event/persistence | SH-044–048, 051, 053 | reliability/concurrency | typed semantic keys/payloads | yes on conflict/failure | local infrastructure copies |

### Gamification / Rewards dependency

Baseline Sweepstakes does not require Gamification to function. If a future legally reviewed Gamification event creates PrizeEntry eligibility, Sweepstakes must consume an explicit versioned event/contract and still issue its own PrizeEntry under AMOE/equivalent-odds policy. No direct PointLedgerEntry/RewardRedemption read may be used as a shortcut.

### Track Subscription dependency

No direct baseline dependency is confirmed. Track status must never improve chance-based odds. If a future rule references a track only for non-odds eligibility under approved legal architecture, use the Track owner interface rather than local premium state.

---

## 14. Outbound Consumers and Effects

- **Payment / Payout / Tax** consumes recognized prize value and may query PrizeTaxYearSummary; it owns tax reporting truth.
- **Notification** reacts to committed entry/winning/tax/fulfillment facts through requests/events.
- **Admin Review / Compliance Hold** receives justified hold requests and may show safe prize context.
- **Audit / Event Ledger** stores generic proof of material actions and sensitive access.
- **Transaction / Order** may show prize-entry provenance/results through stable owner interface/event but remains transaction truth.
- **Consent & Disclosure** may present the correct Sweepstakes rules version; it does not own entry eligibility.
- **Privacy / Data Erasure** orchestrates subject-data instructions and consumes owner results.
- **Observability / Ops** receives safe operational telemetry.

Sweepstakes must not directly mutate any of these owners’ tables.

---

## 15. Canonical Shared Operations Used

Only canonical operations relevant to Sweepstakes are included.

### SH-001 — `resolveAuthenticatedActor`

- **Class:** canonical shared capability.
- **Owner:** Identity & Access.
- **Why:** establish trusted actor for user/admin commands.
- **Invocation:** before protected command/query.
- **Local policy:** which action requires an actor and what resource facts are supplied.
- **Result:** typed actor context.
- **Prohibited:** `prizeAuth.ts`, local session/current-user helper.

### SH-002 — `authorizeResourceAction`

- **Class:** cross-cutting capability.
- **Owner:** Role / Authority.
- **Invocation:** before protected mutation/read.
- **Local policy:** action vocabulary and Sweepstakes relationship facts.
- **Prohibited:** `isSweepstakesAdmin`, local role/permission engine.

### SH-008 / SH-009 — `queryConsentProof` / `resolveActiveConsentVersion`

- **Class:** another Module’s public capability.
- **Owner:** Consent & Disclosure.
- **Invocation:** rules activation, entry issuance, winner/claim flows where policy requires.
- **Local policy:** which version/proof is sufficient for this drawing/action.
- **Prohibited:** local consent table/version catalog/checker.

### SH-011 / SH-012 — `evaluateComplianceHold` / `requestComplianceHold`

- **Class:** another Module’s public interface.
- **Owner:** Admin Review / Compliance Hold.
- **Invocation:** entry/drawing/approval/fulfillment gate and justified escalation.
- **Local policy:** how applicable holds affect Sweepstakes state.
- **Prohibited:** `winnerHoldService.ts`, local blocked truth.

### SH-014 — `requireStepUpForSensitiveAction`

- **Class:** platform security capability.
- **Owner:** Identity & Access.
- **Invocation:** winner-selection overrides/redraws and financially/tax-sensitive approvals if root security policy classifies them high risk.
- **Local policy:** action/target passed to central assurance.
- **Prohibited:** local MFA/OTP/session assurance.

### SH-019 — `evaluateFinancialReadiness`

- **Class:** Payment/Tax public interface.
- **Owner:** Payment / Payout / Tax.
- **Invocation:** before tax-sensitive approval/fulfillment.
- **Local policy:** how returned dimensions map to PrizeWinning state.
- **Prohibited:** `prizeTaxCheck.ts`, W-9 or provider-status interpretation.

### SH-029 / SH-030 — `appendAuditEvent` / `recordSensitiveAccess`

- **Class:** audit capabilities.
- **Owner:** Audit / Event Ledger.
- **Invocation:** material admin actions; sensitive winner/tax reads.
- **Local policy:** safe action names/target/sensitivity.
- **Prohibited:** local audit/access-log tables.

### SH-032 / SH-033 / SH-034 — request context, structured logging, telemetry sanitization

- **Class:** observability primitives/capabilities.
- **Owner:** Observability / Ops.
- **Invocation:** all server/worker paths and before logs/audit/failure payloads.
- **Local policy:** safe Module identifiers/labels.
- **Prohibited:** local logger/correlation/sanitizer framework.

### SH-037 / SH-038 — integration failure / queue telemetry

- **Class:** cross-cutting operational capabilities.
- **Owner:** Observability / Ops / shared queue.
- **Invocation:** downstream failures and worker attempts/retries/dead letters.
- **Local policy:** business state remains Sweepstakes-owned.
- **Prohibited:** local IntegrationFailure/QueueJob truth.

### SH-041 — `requestNotification`

- **Class:** Notification public capability.
- **Owner:** Notification.
- **Invocation:** after committed entry/winning/tax/fulfillment facts.
- **Local policy:** why/when/which safe template variables.
- **Prohibited:** `winnerEmailService.ts`, SMS/push/provider clients.

### SH-044 — `executeIdempotentCommand`

- **Class:** platform primitive.
- **Invocation:** every retryable mutation.
- **Local policy:** semantic identity for activate, entry, drawing run, winning transition, reconciliation.
- **Prohibited:** local idempotency table/helper.

### SH-045 — `deduplicateDomainEvent`

- **Class:** platform event primitive.
- **Invocation:** authoritative purchase-event consumer and any future source-event consumer.
- **Local policy:** one source event/order may create configured entries once under drawing/method semantics.
- **Prohibited:** `processedPrizeEvent.ts`, local inbox implementation.

### SH-046 — `publishDomainEvent`

- **Class:** transactional outbox primitive.
- **Invocation:** with/after owner transaction according to canonical outbox mechanics.
- **Local policy:** event vocabulary and privacy-minimized payload.
- **Prohibited:** `prizePublisher.ts`, custom event bus.

### SH-047 / SH-048 — reliable job / retry with backoff

- **Class:** shared queue primitives.
- **Invocation:** scheduled draw, tax summary reconciliation, downstream retry.
- **Local policy:** payload, idempotency key, retryable vs permanent failure.
- **Prohibited:** local queue/retry framework.

### SH-051 — `acquireAggregateLock`

- **Class:** database primitive.
- **Invocation:** entry-limit race protection and single drawing run.
- **Local policy:** lock key, conflicting actions, safe replay.
- **Prohibited:** in-memory mutex or Module lock table.

### SH-053 — `transitionLifecycleState`

- **Class:** shared mechanism / separate truth.
- **Invocation:** Drawing, EntryMethod, PrizeWinning status mutations.
- **Local policy:** exact transition graph/invariants.
- **Prohibited:** generic cross-domain status policy.

### SH-072 / SH-077 — canonical hashing/text snapshot

- **Class:** platform primitives.
- **Invocation:** only if U-CL10-01 adopts canonical text/hash rules evidence.
- **Local policy:** included fields, canonicalization version, what the hash proves.
- **Prohibited:** `prizeRulesHash.ts`, Sweepstakes-only cryptography.

### SH-095 / SH-096 / SH-097 / SH-098 — Privacy owner protocol

- **Class:** cross-cutting protocol/primitives.
- **Invocation:** Privacy orchestration callbacks, export/inventory, retention, anonymization.
- **Local policy:** record disposition and field map.
- **Prohibited:** local privacy request/job/exemption system or global DB crawler.

### SH-116 — `secureRandomSelection`

- **Class:** Module-internal capability over shared CSPRNG.
- **Owner:** Sweepstakes / Prize.
- **Invocation:** one frozen drawing run.
- **Local policy:** population, weights, winner count, repeat/replacement/redraw policy, proof.
- **Result:** unbiased selected entries plus approved evidence inputs.
- **Prohibited:** `Math.random()`, generic `raffleUtil.ts` outside owner.

### SH-117 — `aggregateYearlyReportableValue`

- **Class:** shared mechanism / separate truth.
- **Owner:** each value owner; Sweepstakes owns PrizeTaxYearSummary.
- **Invocation:** recognized winning and reconciliation only after the CL-10-R009 jurisdiction/grain contract is approved; production SH-117 aggregation remains blocked until then.
- **Local policy:** inclusion/recognition/year/currency/reversal semantics.
- **Prohibited:** merged prize+reward+earnings local tax cache.

### SH-118 — `reportTaxableValue`

- **Class:** Payment/Tax public interface.
- **Owner:** Payment / Payout / Tax.
- **Invocation:** when a recognized prize value must be handed off.
- **Local policy:** FMV snapshot and recognition event.
- **Prohibited:** CL-10 filing/1099/tax submission service.

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Truth affected | Why local |
|---|---|---|---|---|---|
| `validateDrawingConfiguration` | enforce schedule/value/limit/eligibility configuration | drawing draft | validation result | none | Sweepstakes owns drawing semantics |
| `evaluateDrawingActivationReadiness` | compose rules/AMOE/odds/legal prerequisites | drawing + methods + external proofs | DecisionResult | none | activation is Sweepstakes policy |
| `validateEntryMethodSemantics` | ensure type/free/purchase/awards/odds are coherent | method config | validation | none | domain meaning is local |
| `evaluatePrizeEntryEligibility` | decide whether this user/source/method may issue | owner facts + external proof refs | decision/reasons | none | entry permission is local |
| `enforceEntryLimits` | calculate permitted quantity within race-safe transaction | drawing/user/source counts | permitted/denied | none directly | limits belong to drawing policy |
| `buildFrozenEligiblePopulation` | produce exact selection population | closed drawing + entries | frozen population evidence | run proof | selection population is local truth |
| `selectWinningEntries` | apply SH-116 under local weighting policy | frozen population | selected entries | run proof | secure drawing policy is local |
| `buildPrizeWinningSnapshot` | snapshot name/FMV/currency/tax year | drawing + selected winner | PrizeWinning input | PrizeWinning | historical prize meaning is local |
| `mapFinancialReadinessToWinningDecision` | turn Tax owner facts into local next state | SH-019 result + winning | local decision | PrizeWinning transition | external owner supplies facts only |
| `mapHoldDecisionToWinningDecision` | map hold applicability to local behavior | SH-011 result | decision | PrizeWinning transition | hold lifecycle external; local effect local |
| `recognizePrizeValue` | decide inclusion in yearly summary/tax report | winning/state/policy | value-recognition fact | summary/outbox | prize FMV recognition is local |

---

## 17. Shared Mechanism / Separate Truth Rules

- **Lifecycle plumbing:** SH-053 may be shared; PrizeDrawing/EntryMethod/PrizeWinning transition graphs remain local.
- **Idempotency:** SH-044 is shared; the semantic key for a free entry, purchase event, run, or fulfillment remains local.
- **Event dedupe:** SH-045 is shared; the effect of one purchase event on one drawing/method remains local.
- **Outbox:** SH-046 is shared; Sweepstakes event names/payload meaning remain local.
- **Locks:** SH-051 is shared; the user+drawing/run lock key and conflict semantics remain local.
- **Randomness:** shared CSPRNG mechanism; eligible population, weight, winner/replacement/redraw policy and immutable proof remain Sweepstakes truth.
- **Hash/snapshot:** SH-072/077 mechanics may be shared; official-rules meaning and evidence association remain local.
- **Year aggregation:** SH-117 mechanism may be shared; PrizeTaxYearSummary remains separate from TaxYearEarningsSummary and reward records.
- **Audit:** SH-029/030 storage shared; drawing/entry/winning records remain business truth.
- **Privacy:** Privacy orchestration shared; record-specific disposition remains owner policy.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

- User free-entry requests require SH-001 actor context.
- Admin configuration/adjustment/drawing/fulfillment actions require SH-001 + SH-002.
- System/scheduled workers use trusted system actor/service context under root standards.

### Resource/action facts supplied by Sweepstakes

Examples:

- `prize_drawing.configure`
- `prize_drawing.activate`
- `prize_drawing.close`
- `prize_drawing.cancel`
- `prize_entry.create_free`
- `prize_entry.admin_adjust`
- `prize_entry.correct_eligibility`
- `prize_drawing.run`
- `prize_winning.read`
- `prize_winning.transition`
- `prize_winning.fulfill`
- `prize_tax_summary.read`

Role / Authority interprets permission; Sweepstakes supplies target ID, actor/subject relationship, and requested action.

### Step-up

Inherited PR-CL10-09: root security policy should consider step-up for winner-selection override/redraw and financially/tax-sensitive fulfillment approval. Sweepstakes consumes SH-014; it never implements MFA locally.

### RLS/server enforcement

Any RLS policy must align with the same Role / Authority contract. UI hiding alone is never authorization.

---

## 19. Compliance / Readiness / Entitlement Gates

### Drawing activation gate

- **Underlying truth owners:** Consent & Disclosure for version/proof; legal governance for approved rules/policy.
- **Consumed:** SH-008/009 plus approved immutable rules evidence.
- **Local action:** activate PrizeDrawing.
- **Local composition:** schedule + active method set + required AMOE + equivalent odds + legal/rules proof.
- **Result:** allow/deny with stable reasons.

### Entry issuance gate

- **External owners:** Identity/Role, Consent, Hold, Order/payment owner for purchase fact.
- **Local composition:** drawing/method/time + consent sufficiency + source validity + limits + odds + local eligibility.
- **Result:** one idempotent PrizeEntry effect or denial.

### Drawing-run gate

- **External owners:** authz/step-up as applicable.
- **Local composition:** closed drawing + frozen eligible population + no disallowed odds advantage + U-CL10-02 run proof + lock/idempotency.
- **Result:** exactly one run or conflict/replay.

### Prize fulfillment gate

- **Underlying truth owners:** Payment / Payout / Tax and ComplianceHold.
- **Consumed:** SH-019 and SH-011, optionally SH-012 for justified hold request.
- **Local action:** transition PrizeWinning.
- **Local composition:** current winning state + tax readiness + active holds + fulfillment evidence.
- **Result:** pending/blocked/approved/fulfilled/forfeited/cancelled according to approved policy.

### Entitlement gate

No baseline Track entitlement gate is confirmed. Paid entitlements cannot improve chance odds. Any future non-odds entitlement use requires an explicit architecture ruling and Track owner interface.

---

## 20. Provider Integrations

### Current ownership

Sweepstakes / Prize owns no confirmed external provider adapter.

### Explicit prohibitions

Do not implement here:

- Stripe webhook route, signature verification, `ProcessedStripeEvent`, or Stripe status mapping;
- tax-provider client/webhook/status mapping;
- notification-provider/email/SMS/push adapter;
- payment or payout execution;
- external random-drawing SaaS unless architecture explicitly changes.

### Future fulfillment provider

If a future physical-prize/gift-card/shipping provider is assigned to this Module, architecture must first define:

- provider-neutral port;
- credential ownership;
- SH-059 signature verification if webhooks exist;
- SH-060 provider-event dedupe record ownership;
- SH-061 status/error translation;
- reconciliation through SH-062;
- immutable fulfillment evidence;
- retry/idempotency;
- privacy deletion/retention;
- SH-037 operational failure reporting.

Until then, automated provider fulfillment is disabled.

---

## 21. Events and Outbox

All owner events use SH-046.

### Envelope expectations

Each event includes, where applicable:

- event ID;
- schema version;
- aggregate type/ID;
- aggregate version or source updatedAt/version token;
- occurredAt;
- correlation ID;
- causation/source event ID;
- privacy-minimized actor/subject IDs;
- safe evidence references, not raw Tax/Consent/provider payloads.

### Emission rule

Publish facts only after the corresponding owner transaction commits. Consumer retry uses SH-045. Event delivery cannot be used to infer a transition that did not commit.

### Not disguised commands

`PrizeWinningCreated` may cause Notification/Tax consumers to react; it must not say “set tax profile approved” or “send this exact provider payload.”

---

## 22. Background Jobs / Scheduled Work

### Scheduled drawing trigger

- **Purpose:** dispatch `runPrizeDrawing` when a closed/ready drawing reaches its approved draw time.
- **Owner:** Sweepstakes workflow; queue mechanics SH-047/048.
- **Idempotency key:** drawing ID + approved run generation/request ID.
- **Retry:** technical failures before committed run; post-commit replay returns existing run.
- **Permanent/manual failure:** unresolved proof/legal state, invalid drawing, irreconcilable population.
- **Truth updated:** only through `runPrizeDrawing`.
- **Telemetry:** SH-038, SH-033/037 as appropriate.

### Prize tax summary reconciliation worker

- **Purpose:** rebuild/compare PrizeTaxYearSummary to recognized PrizeWinning truth.
- **Key:** user + taxYear + currency + reconciliation version/window.
- **Retry:** safe and idempotent.
- **Truth updated:** PrizeTaxYearSummary only.
- **Downstream:** missing taxable-value reports use SH-118 idempotently.

### Fulfillment retry worker

Exists only for an approved fulfillment effect/provider. It may retry technical work but cannot bypass tax/hold gates or set fulfilled without evidence.

---

## 23. Concurrency and Idempotency

### Entry issuance race

- **Resource key:** `(drawingId, userId)` plus source/method as needed.
- **Mechanism:** SH-044 command idempotency, SH-051 DB/advisory/row lock or equivalent serializable transaction, SH-045 for domain event replay.
- **Invariant:** free/paid/max limits cannot be exceeded by concurrent requests.
- **Replay:** return prior/no-op effect; do not issue fresh token(s).

### Purchase event race

- **Identity:** source event ID + consumer handler/version + drawing/method semantics.
- **Mechanism:** SH-045 inbox claim in same logical transaction as resulting PrizeEntry effects.
- **Invariant:** one authoritative purchase fact cannot accidentally award twice.

### Drawing run race

- **Resource key:** drawing ID + approved run generation.
- **Mechanism:** SH-051 + SH-044 + approved immutable run proof.
- **Invariant:** only one runner selects for the run.
- **Replay:** crash after commit returns committed run/winners; never selects again.

### Winning transition race

- **Mechanism:** SH-044 + SH-053, optionally SH-052 optimistic concurrency if repository standards use versioning.
- **Invariant:** no stale pending/blocked state can be fulfilled after a concurrent hold/tax change without re-evaluation.

### Tax summary race

- **Key:** unique `(userId,taxYear,currency)`.
- **Mechanism:** SH-117 transactional increment/source-event uniqueness plus full reconciliation.

### Prohibition

No in-memory mutex is a valid distributed concurrency solution.

---

## 24. Media / Storage

No Module-owned file/media lifecycle is confirmed.

If immutable official rules or drawing evidence uses a stored document/file, Media / File Access owns file mechanics and access grants. Sweepstakes may own the **business meaning** of a rules snapshot/evidence reference but must not implement upload scanning, storage buckets, signed URLs, or MediaAsset lifecycle locally.

---

## 25. Search / Projection

Sweepstakes owns no Typesense/search projection in the current evidence.

- PrizeDrawing/PrizeWinning are source truth here.
- Any public discovery representation would be Search-owned and would consume an owner-issued public-readiness/projection contract.
- Search must not reconstruct AMOE, winner eligibility, tax readiness, or drawing state from unrelated records.

No Search integration is required for baseline Module correctness.

---

## 26. Notification

### Business triggers owned here

Potential notification intents include:

- entry accepted/denied summary where product UX requires;
- winner selected;
- tax information/action required;
- claim/confirmation action required;
- prize approved;
- prize fulfilled;
- prize forfeited/cancelled where policy requires.

### Delivery boundary

Use SH-041 with:

- recipient User ID;
- template key;
- sensitivity classification;
- safe variables;
- action route;
- idempotency key;
- source reference.

Do not include sensitive TaxProfile/provider details in payloads. NotificationDelivery success/failure never changes PrizeWinning automatically.

---

## 27. Audit and Sensitive Access

### Domain truth

PrizeDrawing, PrizeEntry, drawing-run proof, PrizeWinning, and PrizeTaxYearSummary remain domain truth.

### Generic audit

Use SH-029 for:

- drawing activation/cancellation;
- material entry-method changes;
- admin adjustment;
- eligibility override;
- manual drawing initiation/override where allowed;
- winning approval/forfeit/cancel/fulfillment;
- reconciliation/manual repair actions.

### Sensitive access

Use SH-030 where root data classification requires proof for reading/exporting sensitive winner/tax/fulfillment data.

### Separation

AuditEvent/AccessAuditLog do not substitute for immutable drawing-run proof, PrizeEntry, or PrizeWinning.

---

## 28. Privacy and Retention

### Subject-data inventory

At minimum, Sweepstakes may hold user-linked:

- PrizeEntry history;
- Order provenance references;
- consent proof references;
- PrizeWinning history and prize value;
- TaxProfile references and reporting metadata;
- PrizeTaxYearSummary;
- drawing-run winner references once implemented;
- audit/access references held by their own Modules.

### Privacy executor

Implement SH-095/096/097/098 contracts, not a local privacy workflow.

### Owner target/executor contract (CL-10-R015)

**Protocol owner:** Privacy / Data Erasure. **Executing owner:** `sweepstakes_prize`. The following maps existing owner records, not new DataErasureTargetType enum values:

| Subject inventory | Existing owner identity | Export contribution |
|---|---|---|
| `PrizeEntry` by `userId` | `id` | Entry history and owned Order/Consent proof references |
| `PrizeWinning` by `userId` | `id` | Winning/value history and owned fulfillment references |
| `PrizeTaxYearSummary` by `userId` | `id`; current unique key `(userId, taxYear, currency)` | Prize-year history subject to CL-10-R009 |
| Subject-linked drawing-run proof, once approved | Identity from the future approved U-CL10-02 contract | Permitted subject-linked run evidence only |

SH-096 accepts the Privacy subject/cursor context and returns minimized descriptors using Privacy's fields: `ownerModule`, `targetType`, `targetId` or `externalRef`, `subjectId`, `supportedActions`, `sensitivity`, `sourceVersion`, `retentionCandidate`, and `exportSerializerVersion`, with cursoring. Validate subject association in this Module; referenced foreign records remain their owners' inventory. Configuration records enter inventory only where a subject association or incidental personal data is established. Future provider/run-proof targets require their separately approved ownership/schema first.

SH-097 accepts the owned target and proposed action and returns required retention facts, reason/policy basis, authoritative `retainUntil` when available, minimum fields, permitted anonymization, and source references. Unknown policy is not permission to erase or a fabricated retention basis; Privacy records any exemption.

SH-095 accepts Privacy request/job/target references, the typed owner target, requested disposition, idempotency and execution context. Revalidate owner/subject/target and approved action before changing owned records. SH-098 uses only an approved versioned field map. Return Privacy's canonical target result: owner, requested disposition, idempotency key, result (erased, anonymized, retained, restricted, exported, detached, revoked, skipped, retryable failure, or terminal failure, as applicable under approved policy), evidence/exemption references, safe counts/completion metadata, and provider result only where applicable. Replays must not repeat side effects; unsupported targets/actions cannot be reported as successful execution. Privacy owns recorded target disposition and orchestration.

**Still unresolved:** bilateral registration of stable `targetType`/target-ID encoding, source-version strategy, per-target supported actions and result mappings; retain/anonymize/erase dispositions depend on CL-10-R014. This mapping documents owner participation without choosing those pending details. Production execution requires their approval. Do not infer an enum mapping, use a generic database crawler, create a local PrivacyRequest/DataErasureJob, or decide legal retention here.

### Disposition policy

The exact erase/anonymize/retain matrix is not fully resolved. Until legal/retention policy is approved:

- do not hard-delete compliance/tax/drawing evidence merely because a User requests erasure;
- return retention facts to Privacy through SH-097;
- allow Privacy to record DataRetentionExemption;
- anonymize/pseudonymize only fields approved by owner policy while preserving required relational/evidence truth;
- provide export serialization for permitted user-facing prize data.

### Cascade warning

Current Prisma `onDelete: Cascade` from PrizeDrawing to PrizeEntry/entry methods is dangerous for historical evidence if application code deletes activated/completed drawings. Owner commands should therefore prohibit destructive deletion of non-draft evidence-bearing drawings until retention architecture explicitly permits it.

---

## 29. Observability

Use canonical request context/logging/telemetry operations.

### Safe dimensions

Examples:

- operation name;
- drawing ID;
- entry method type;
- source enum;
- status transition;
- worker attempt;
- correlation/request ID;
- denial/retry reason code;
- aggregate counts.

Avoid high-cardinality/raw sensitive dimensions such as:

- tax IDs/documents;
- raw consent content;
- provider payloads/secrets;
- full user PII;
- raw official-rules documents when a hash/reference suffices;
- random secret material if the approved drawing-proof design treats it sensitive.

### Operational records

SH-037/038 may surface integration/job failures. They do not replace PrizeDrawing/Winning state.

---

## 30. Security Boundaries

- validate every command/query input with root schema/validation standards;
- server-side authorization for all protected operations;
- rate-limit public free-entry endpoint through canonical platform mechanism if available;
- do not trust client-provided Order/payment/consent/tax facts;
- use canonical hashing/text snapshot primitives if approved for rules evidence;
- use CSPRNG only through SH-116;
- never log secrets/raw tax data;
- minimize event/notification payloads;
- use database concurrency primitives, not in-memory locks;
- step-up sensitive admin actions according to root policy;
- no provider credentials in Module source/config outside provider owner.

---

## 31. Error / Decision Result Pattern

Public decisions should use stable categories rather than leaking Prisma/provider errors.

```text
ALLOW
DENY_VALIDATION
DENY_AUTHENTICATION
DENY_AUTHORIZATION
DENY_CONSENT_REQUIRED
DENY_DRAWING_NOT_ACTIVE
DENY_METHOD_NOT_AVAILABLE
DENY_ENTRY_LIMIT_REACHED
DENY_INELIGIBLE
DENY_HOLD_ACTIVE
DENY_TAX_READINESS
DENY_RULES_EVIDENCE_MISSING
DENY_LEGAL_GATE
CONFLICT_STALE_STATE
CONFLICT_ALREADY_PROCESSED
CONFLICT_DRAWING_IN_PROGRESS
REVIEW_REQUIRED
DEPENDENCY_UNAVAILABLE
RETRYABLE_FAILURE
PERMANENT_FAILURE
```

A result may include safe `reasonCodes`, `evidenceRefs`, `evaluatedAt`, policy/schema version, and `nextAction`.

Unknown provider/domain errors are normalized by their owner before Sweepstakes sees them.

---

## 32. Testing Architecture

### Domain unit tests

- drawing configuration/timing;
- AMOE/free-path validation;
- method semantic compatibility;
- equivalent odds/weight rules;
- entry limits/eligibility;
- lifecycle transitions;
- frozen population construction;
- PrizeWinning transition policy;
- value recognition/summary inclusion.

### Public contract tests

- command/query DTOs and stable reason codes;
- inbound qualifying purchase event versions;
- Payment/Tax SH-019/118;
- Hold SH-011/012;
- Consent SH-008/009;
- Privacy SH-095–098;
- Notification SH-041.

### Database/integration tests

- owner repositories only;
- transaction/outbox atomicity;
- current Prisma relationships/indexes;
- migrations for U-CL10-01/02 once approved;
- aggregate rebuild.

### Authorization/security tests

- self/admin/system context;
- unauthorized admin actions;
- step-up where required;
- rate limits/abuse resistance;
- no forbidden cross-domain Prisma imports.

### Compliance tests

- purchase method cannot become unlawful sole path where AMOE required;
- no paid/points/reward/entitlement odds boost;
- tax-blocked/held winning cannot fulfill;
- Notification delivery cannot fulfill;
- production draw disabled without required rules/run proof.

### Idempotency/concurrency tests

- duplicate free request;
- duplicate purchase event;
- simultaneous entries at limit boundary;
- concurrent drawing workers;
- crash before/after run commit;
- duplicate winning transition/tax report;
- concurrent summary updates.

### Privacy tests

- enumerate/export fixtures;
- erase/anonymize/retain instruction idempotency;
- retention result/exemption handoff;
- cascade-delete safety.

### E2E participation tests

- free entry → entry truth;
- authoritative purchase event → entry truth;
- close → secure draw → winner;
- winner → tax/hold → approved fulfillment;
- downstream notification outage does not corrupt truth.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `sweepstakes_prize` is the canonical Module ID; do not create a plural duplicate Module.
2. PrizeDrawing status is drawing lifecycle truth.
3. PrizeEntry is separate from Order, PointLedgerEntry, RewardRedemption, ConsentLog, and any ticket/balance abstraction.
4. PrizeWinning is separate from RewardRedemption and Notification.
5. PrizeTaxYearSummary is separate from TaxYearEarningsSummary and tax filing truth.
6. A purchase-triggered entry consumes an authoritative owner event; Sweepstakes owns no Stripe webhook.
7. `ProcessedStripeEvent` must never be recreated here.
8. ConsentLog proves acceptance; Sweepstakes owns whether that proof permits the action.
9. `amoeEnabled`/`noPurchaseNecessary` booleans do not replace validation of actual free entry methods.
10. A required free/AMOE path must be usable under the approved rules, not merely stored.
11. Paid, points-derived, reward-derived, or entitlement-derived participation must not receive better chance unless an explicit approved legal architecture says so.
12. `entryToken @unique` is not source-event idempotency.
13. Per-user entry limits must be enforced atomically under concurrency.
14. PrizeEntry corrections are explicit/audited; do not delete history to fix counts.
15. A frozen drawing population cannot be mutated beneath an active run.
16. A drawing run must be single-execution under SH-051/044.
17. SH-116 is the only approved winner-selection capability; never use `Math.random()`.
18. Audit logs/telemetry are not drawing-run proof.
19. Production winner selection is blocked until U-CL10-02 is resolved.
20. Production drawing activation is blocked until U-CL10-01 is resolved.
21. A winner notification cannot create/approve/fulfill a PrizeWinning.
22. `pending_tax` and `blocked` cannot transition directly to `fulfilled`.
23. TaxProfile/provider state is never interpreted directly here; use SH-019.
24. ComplianceHold lifecycle/release remains external; use SH-011/012.
25. Fulfillment requires owner-approved evidence and a valid current PrizeWinning state.
26. PrizeTaxYearSummary must be rebuildable from recognized PrizeWinning truth.
27. Taxable value is reported through SH-118; Sweepstakes does not file tax forms.
28. Track entitlements cannot affect sweepstakes odds.
29. Gamification points/rewards cannot be converted to entries without a separately approved Sweepstakes interface and AMOE policy.
30. Provider clients for Stripe, Tax, and Notification are prohibited in this Module.
31. Cross-Module Prisma reads are not the normal integration pattern.
32. Privacy / Data Erasure owns orchestration; Sweepstakes only executes owner instructions.
33. Activated/completed evidence must not be destructively deleted without retention approval.
34. Generic queue/retry/idempotency/lock/audit/logging infrastructure must be reused, not rebuilt.
35. Unsupported redraw/replacement winner behavior remains disabled until U-CL10-11 is resolved.
36. Exact legal thresholds/jurisdictions/claim windows must not be hardcoded from developer assumptions.
37. Unresolved architecture remains fail-closed rather than implemented ad hoc.

---

## 34. Prohibited Duplicate Implementations

Do not generate these or equivalent local responsibilities:

- `prizeAuth.ts`, `sweepstakesSession.ts`, `currentPrizeUser.ts`
- `isSweepstakesAdmin.ts`, `prizePermissions.ts`
- `prizeConsentService.ts`, `rulesCheckbox.ts`, local Consent tables/version resolver
- `winnerHoldService.ts`, `prizeBlocked.ts`, `blockedBoolean`
- `prizeTaxCheck.ts`, `w9Gate.ts`, local tax threshold/provider mapper
- `stripePrizeWebhook.ts`, `ProcessedPrizeStripeEvent`, Stripe signature verifier
- `winnerEmailService.ts`, `prizeSms.ts`, `prizePush.ts`
- `prizeAuditRepository.ts`, `winnerDataAuditTable`
- `prizeIdempotency.ts`, `dedupeEntry.ts`, local inbox/outbox/event bus
- `prizeQueue.ts`, feature retry loop, local QueueJob truth
- `drawingMutex.ts`, in-memory lock
- `raffleUtil.ts`, `randomWinner.ts` using non-canonical randomness
- `prizeRulesHash.ts`, bespoke crypto/text canonicalizer
- `annualPrizeTaxService.ts` that owns filing or merges tax truth
- `prizeDeleteService.ts` that creates its own privacy workflow
- generic `incentiveService.ts` shared with Gamification
- local premium/entitlement odds flags.

---

## 35. Unresolved Decisions

### U-CL10-01 — immutable official-rules evidence

The current schema stores only `officialRulesUrl`. Production activation requires an approved immutable evidence model/version. Do not invent the table. If approved design uses canonical text/hash, reuse SH-077/072.

### U-CL10-02 — immutable drawing-run proof schema

Required before production selection. Must preserve frozen population evidence, selection policy/version, randomness evidence appropriate to the design, winner count/replacement behavior, run identity, selected entry/winner references, actor/system/correlation/time, and immutable result proof.

### U-CL10-09 — `PrizeEntry.rulesConsentId` relational integrity

Runtime validates through SH-008. Whether the field becomes an FK to ConsentLog depends on ownership/deletion/retention policy and requires an explicit schema ruling.

### U-CL10-11 — redraw / replacement winner policy

No redraw/replacement behavior until official rules/legal policy and run-generation evidence are defined.

### U-CL10-12 — exact legal thresholds and jurisdictions

Production launch requires approved legal policy for eligibility, geography/age, tax/reporting thresholds, and claim windows. Do not hardcode guesses.

### Fraud/risk ownership

A shared fraud capability owner is not confirmed. Local validation, rate limits, idempotency, and hold requests may be implemented; a generic fraud-score platform must not be invented here.

### Winner-entry linkage

Current PrizeWinning has no direct PrizeEntry relation. U-CL10-02 must guarantee selected-entry proof; whether a direct FK is added remains unresolved.

### Fulfillment provider/evidence model

No external prize fulfillment provider or generic fulfillment-proof schema is confirmed. Automated provider fulfillment remains disabled until owned explicitly.

### CL-10-R009 — SH-117 jurisdiction/grain

Section 8.5 records the current unique-key mismatch. The architectural interpretation remains unresolved and blocks production SH-117 aggregation; no single-jurisdiction limitation or schema solution has been selected.

### Retention matrix

Exact legal retention/anonymization rules for entry, rules, drawing-run, winning, and prize-tax evidence remain to be approved with Privacy/legal context.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Module ID is `sweepstakes_prize`; type is `compliance_feature_ecosystem`; status is `mvp_active_legal_gated`.
2. The Module owns PrizeDrawing, SweepstakesEntryMethod, PrizeEntry, PrizeWinning, PrizeTaxYearSummary and their owned enums/lifecycles.
3. The Module owns AMOE/equivalent-odds, entry limits/eligibility, winner selection policy, prize FMV snapshot, and local fulfillment-state composition.
4. Order/payment, Consent, TaxProfile, ComplianceHold, Notification, Audit, Privacy, and provider state remain external truths.
5. Purchase-triggered entries use authoritative owner events; no Stripe webhook is owned here.
6. SH-### canonical operations are consumed rather than duplicated.
7. Secure selection uses SH-116 and immutable run evidence.
8. PrizeTaxYearSummary remains separate from Tax-owned yearly reporting truth.
9. Production legal-gated behavior fails closed when a required decision is unresolved.

### Inherited Proposed Rulings

- PR-CL10-01 purchase bridge through authoritative Order/payment-owner facts;
- PR-CL10-02 Deep Module code organization, no generic CL-10 source-truth service;
- PR-CL10-06 PrizeDrawing transition graph;
- PR-CL10-07 immutable/freeze-aware PrizeEntry behavior;
- PR-CL10-08 PrizeWinning terminal/fulfillment constraints;
- PR-CL10-09 central step-up consideration for high-risk CL-10 actions.

These remain proposed until approved by the governing architecture process.

### Implementation blockers

- U-CL10-01 blocks production activation.
- U-CL10-02 blocks production drawing execution.
- U-CL10-11 blocks redraw/replacement.
- U-CL10-12 blocks production behavior in jurisdictions/policies not yet approved.

---

## 37. Coding-Agent Usage

Before implementing a Sweepstakes / Prize feature, the agent must read:

1. root `context/project-overview-v3.md`;
2. root `context/architecture.md`, currently unavailable; consult only if recovered and reconciled;
3. root `context/code-standards.md`, currently unavailable; consult only when present;
4. `context/shared/shared-operations.md`;
5. `context/clusters/incentives, rewards & prize economy/incentives-rewards-prize-economy-cluster-architecture.md`;
6. `context/clusters/incentives, rewards & prize economy/incentives-rewards-prize-economy-cluster-build-plan.md`;
7. `context/clusters/incentives, rewards & prize economy/sweepstakes-module/sweepstakes-prize-module-architecture.md`;
8. `context/clusters/incentives, rewards & prize economy/sweepstakes-module/sweepstakes-prize-implementation-plan.md`;
9. public-interface sections for Consent & Disclosure, Transaction / Order, Payment / Payout / Tax, Admin Review / Compliance Hold, Notification, Audit / Event Ledger, Privacy / Data Erasure, Identity & Access, and Role / Authority as needed by the feature;
10. the current Prisma schema/migrations;
11. the progress tracker/current implementation status.

Before coding, the agent must identify which statements are **confirmed**, **Proposed Rulings**, and **unresolved blockers**. A feature may not turn an unresolved blocker into an implicit production decision.
