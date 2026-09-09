# Gamification / Rewards Module Architecture

> **Module ID:** `gamification_rewards`  
> **Module name:** Gamification / Rewards Module  
> **Module type:** `feature_compliance`  
> **Build status:** `mvp_active_legal_gated`  
> **Primary Cluster:** `CL-10 — Incentives, Rewards & Prize Economy`  
> **Repository target:** `context/modules/gamification_rewards/module-architecture.md`  
> **Document status:** Implementation-grade Module architecture derived from the current Workin Ants evidence set. Confirmed rules are binding; Proposed Rulings and Unresolved Decisions are explicitly labeled.  
> **Audience:** Coding agents, developers, reviewers, maintainers, architects, and compliance reviewers working on `gamification_rewards`.  
> **Update rule:** Update this file whenever a binding Module ownership boundary, lifecycle rule, public contract, shared-operation dependency, data meaning, or compliance gate changes. Build progress must not silently redefine architecture.

---

## 1. Module Header

### Relationship to root architecture

This file is subordinate to the root Workin Ants architecture and Project Overview. Root rules remain authoritative for platform-wide identity, authorization, privacy, observability, data access, provider isolation, and shared-operation behavior.

This file narrows those rules to the `gamification_rewards` Deep Module. It does not create a second platform architecture.

### Relationship to Cluster architecture

This file is subordinate to `CL-10 — Incentives, Rewards & Prize Economy` architecture and build plan.

The Cluster coordinates `gamification_rewards` with `sweepstakes_prize`; this Module file owns only the deterministic gamification side:

```text
GamificationProgram
→ GamificationRule
→ PointLedgerEntry
→ Challenge / ChallengeParticipant
→ Leaderboard / LeaderboardEntry
→ Reward
→ RewardRedemption
```

The Module must preserve the Cluster's non-blurring rule:

```text
PointLedgerEntry != PrizeEntry
RewardRedemption != PrizeWinning
GamificationProgram != PrizeDrawing
```

### Evidence basis

This architecture is grounded in the current:

- Workin Ants Project Overview;
- Deep Module Registry;
- Cluster Registry `v2.3-customer-subscription`;
- current Prisma schema;
- Ubiquitous Language / Compliance inventory;
- Canonical Shared Operations Registry;
- CL-10 Cluster architecture;
- CL-10 Cluster build plan;
- standardized Gamification / Rewards Module Architecture Extract already produced in this thread.

Where those sources do not settle a safe implementation decision, this file records a Proposed Ruling or Unresolved Decision rather than inventing code behavior.

---

## 2. Purpose, Goal, and Transformation

### Purpose

The Gamification / Rewards Module governs **deterministic engagement incentives**: programs, rules, point accounting, challenges, leaderboards, reward catalogs, and reward redemptions.

It exists to make engagement value auditable and deterministic without turning points, rewards, purchases, subscriptions, or profile benefits into chance-based prize odds.

### Goal

Convert authoritative platform activity into:

- exactly-once point-ledger effects;
- challenge participation and completion;
- rebuildable point-balance and leaderboard projections;
- deterministic reward eligibility and redemption truth;
- tax-value handoffs, hold checks, notifications, audits, and operational effects through their canonical owners;

while ensuring that this Module never becomes Sweepstakes / Prize, Payment / Tax, Notification, Consent, Hold, Search, Subscription, or generic infrastructure.

### What enters

The Module may consume:

- authenticated actor context;
- Role / Authority decisions;
- configured `GamificationProgram`, `GamificationRule`, `Challenge`, and `Reward` records;
- versioned source Module events such as authoritative order completion, eligible profile completion, eligible high-rating events, and approved challenge completion;
- Consent & Disclosure version/proof decisions;
- ComplianceHold decisions;
- Payment / Payout / Tax readiness and taxable-value contracts;
- approved downstream fulfillment/effect results;
- Privacy / Data Erasure instructions;
- canonical shared-operation results for idempotency, locking, events, queues, audit, telemetry, and projections.

### What leaves

The Module may produce:

- `PointLedgerEntry` truth;
- `ChallengeParticipant` state;
- `LeaderboardEntry` projections;
- `RewardRedemption` truth;
- versioned Gamification-owned domain events;
- tax-value reporting requests;
- ComplianceHold requests based on Gamification-owned evidence;
- notification requests;
- audit requests;
- privacy execution results;
- safe operational telemetry.

### Business/capability transformation

```text
authoritative external fact
+ active deterministic program/rule
+ Module policy
+ consent/hold/tax gates where applicable
+ idempotency/concurrency controls

→ Gamification-owned decision
→ authoritative append/write
→ transactional domain event
→ rebuildable projection or downstream owner handoff
```

### Why this deserves its own Module boundary

The Module owns a coherent set of truths that have different semantics from adjacent systems:

- points are not money;
- rewards are not prizes;
- leaderboard rank is not source truth;
- a challenge is not a drawing;
- a deterministic profile benefit is not a Track subscription entitlement;
- reward value may be tax-relevant without making Gamification the tax owner.

Keeping these truths in one owner prevents payment, search, subscription, and sweepstakes implementations from inventing local point/reward logic.

---

## 3. Owned Truth

### Owned schemas/models

| Record | Plain-English meaning | Source-of-truth role |
|---|---|---|
| `GamificationProgram` | A configured deterministic incentives program with lifecycle, dates, and terms-version reference. | Program configuration and lifecycle truth. |
| `GamificationRule` | A rule that maps an approved trigger to deterministic points under declarative conditions. | Point-award policy configuration truth. |
| `PointLedgerEntry` | One immutable point-value effect: earned, spent, reversed, expired, or adjusted. | Authoritative point transaction truth. |
| `Challenge` | A configured time/event-bound deterministic engagement goal. | Challenge definition and lifecycle truth. |
| `ChallengeParticipant` | A User's participation/completion record for one challenge. | Challenge participation truth, subject to unresolved participant-status vocabulary. |
| `Leaderboard` | A configured ranking context/window within a program. | Leaderboard definition truth. |
| `LeaderboardEntry` | A rebuildable rank/score row for one User within a leaderboard. | Gamification-owned projection, not point truth. |
| `Reward` | A deterministic benefit offered by the reward catalog. | Reward catalog/configuration truth. |
| `RewardRedemption` | A User's claim/redemption lifecycle for one Reward, including value snapshot and external proof references. | Reward redemption lifecycle truth. |

### Owned enums/status vocabularies

- `GamificationProgramStatus`
- `GamificationRuleTrigger`
- `PointLedgerEntryType`
- `PointLedgerEntrySource`
- `ChallengeStatus`
- `RewardType`
- `RewardStatus`
- `RewardRedemptionStatus`

### Lifecycles owned

- `GamificationProgram.status`
- `GamificationRule.isActive` activation/deactivation policy
- `Challenge.status`
- `ChallengeParticipant.status` use, subject to U-GR-06
- `Reward.status`
- `RewardRedemption.status`

`PointLedgerEntry` is not a mutable lifecycle. It is append-only accounting truth.

`LeaderboardEntry` is not a business lifecycle. It is a rebuildable projection.

### Source-of-truth records

1. **Program truth:** `GamificationProgram`.
2. **Rule truth:** `GamificationRule`.
3. **Point truth:** `PointLedgerEntry`.
4. **Challenge truth:** `Challenge` + `ChallengeParticipant`.
5. **Leaderboard definition:** `Leaderboard`.
6. **Leaderboard projection:** `LeaderboardEntry`.
7. **Reward catalog truth:** `Reward`.
8. **Reward claim/fulfillment lifecycle truth:** `RewardRedemption`.

### Domain ledgers/events owned

`PointLedgerEntry` is a Module-owned domain ledger using the shared append-only lifecycle-event mechanism.

The Module also owns the semantic meaning of its emitted domain events, such as:

- program activated/paused/ended;
- point entry appended;
- challenge joined/completed;
- reward redemption requested/status changed/fulfilled/reversed.

The platform outbox is shared infrastructure; event semantics remain Module-owned.

### Projections owned

- derived point balance query/read model;
- `LeaderboardEntry`;
- any future Gamification-only projection explicitly approved and fully rebuildable from Gamification truth.

The Module does **not** own global Search / Typesense projection.

### Snapshots/proof owned

Currently confirmed:

- `RewardRedemption.valueCents` and `currency` are historical redemption value snapshots;
- `PointLedgerEntry` preserves the point delta and provenance fields available in the schema.

Not yet confirmed as dedicated schema:

- immutable rule-version snapshot per award;
- reversal linkage record;
- reward inventory reservation proof;
- fulfillment-attempt record.

These remain unresolved and must not be silently invented.

### Policies/invariants owned

The Module owns:

- which supported authoritative events qualify for a Gamification rule;
- deterministic point award/spend/reversal/expiration/adjustment semantics;
- point balance derivation;
- Gamification program activation rules;
- challenge participation/completion policy;
- leaderboard scoring/window/tie policy;
- reward activation eligibility;
- reward point-cost and redemption eligibility;
- mapping external readiness/hold/fulfillment evidence into `RewardRedemption` transitions;
- no-paid-prize-odds policy on Gamification outputs;
- reward value snapshot timing once approved;
- local abuse-signal rules that justify requesting external review/holds.

---

## 4. Explicit Non-Ownership

The Module must not own or recreate the following.

| Adjacent owner | Remains with that owner | What Gamification must not create |
|---|---|---|
| Identity & Access | User authentication, session truth, step-up challenge/session lifecycle | `gamificationAuth`, local MFA/OTP tables, current-user session helpers |
| Role / Authority | Permission interpretation | reward-role engine, local admin-role booleans |
| Consent & Disclosure | `ConsentLog`, active consent-version catalog, acceptance proof | reward consent table, local terms acceptance truth |
| Sweepstakes / Prize | `PrizeDrawing`, `SweepstakesEntryMethod`, `PrizeEntry`, `PrizeWinning`, `PrizeTaxYearSummary`, AMOE/equivalent-odds policy | points-as-tickets, reward-as-prize lifecycle, local drawing/winner logic |
| Transaction / Order | `Order` and qualifying order lifecycle facts | order completion inference from Stripe or direct Order writes |
| Review / Dispute | `Review` lifecycle and authoritative rating outcome | local review truth or direct review status interpretation |
| Professional Eligibility | `ProfessionalProfile` lifecycle/readiness | local profile activation truth |
| Payment / Payout / Tax | `TaxProfile`, tax reporting, provider tax state, payouts, financial transfer | `taxApproved`, local 1099 service, reward wallet, Stripe webhook |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and release | reward block table/boolean, local hold release |
| Notification | `Notification`, `NotificationDelivery`, channel/provider behavior | reward email/SMS/push provider |
| Audit / Event Ledger | generic `AuditEvent` and `AccessAuditLog` | gamification audit storage as source truth |
| Observability / Ops | structured logging platform, queue telemetry, `IntegrationFailure`/incident abstractions | local queue/incident/failure tables |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, retention exemption lifecycle | local GDPR/privacy request workflow |
| Track Subscription & Entitlement | `TrackSubscription`, `TrackEntitlementGrant`, usage truth | premium reward flags, local temporary entitlements |
| Search / Public Visibility | Typesense/Search projection and indexing truth | direct Typesense writes, local search-rank flags |
| Media / File Access | binary/file storage, validation, scan, signed access | file URLs as fulfillment/consent/tax truth |
| External provider owner | provider credentials, webhook verification, provider-event dedupe, provider-native status | provider SDK/status inside core domain services without explicit ownership ruling |

### Especially prohibited ownership transfers

- `PointLedgerEntry` may share append-only mechanics with other ledgers, but remains separate point truth.
- `RewardRedemption` may consume tax/hold/provider results, but no provider or downstream Module may set its status directly.
- `RewardType.profile_boost` does not make Gamification the Search or entitlement owner.
- `RewardType.cash_bonus` does not make Gamification the payout/payment owner.
- `RewardType.platform_credit` does not authorize a local wallet/credit ledger.
- `RewardType.badge` must not impersonate verification `TrustBadge` truth.
- `RewardType.physical_prize` is a deterministic reward catalog label here; it must not become `PrizeWinning`.

---

## 5. Module Architecture Principles

1. **Deterministic incentives only.** This Module may not implement chance-based winner selection or odds.
2. **Point truth is append-only.** Normal business correction appends compensating entries; it does not rewrite history.
3. **Balance is derived.** No mutable point balance becomes authoritative.
4. **Exactly-once business effect under at-least-once delivery.** Event replay must not duplicate rule effects.
5. **Source Modules publish facts; Gamification decides points.** Gamification must not poll another Module's tables to reconstruct a source event.
6. **Rule configuration is declarative.** `ruleJson` is schema-validated configuration, never executable code.
7. **Program/rule time applies deliberately.** A source event is evaluated against owner-approved effective rule semantics, not whatever mutable configuration happens to exist later.
8. **Challenge state is not leaderboard state.**
9. **Leaderboard is a projection.** Projection loss must be recoverable from source truth.
10. **Reward request is atomic with point spend.**
11. **Limited inventory cannot use check-then-write.** Production use is blocked until U-GR-08 is resolved.
12. **Historical reward value is snapshotted.** Later Reward edits do not rewrite prior redemption value.
13. **External readiness is input, not local truth.** Tax/hold/consent/entitlement decisions remain source-owned.
14. **Provider results cannot bypass owner transitions.**
15. **No paid prize odds.** Points, rewards, subscriptions, profile boosts, or purchases cannot create better chance-based odds.
16. **Unsupported enum values remain inactive.** An enum value does not prove a provider or fulfillment path exists.
17. **Privacy is owner-executed, centrally orchestrated.**
18. **Audit and observability are evidence/diagnostics, not domain truth.**
19. **All asynchronous work is durable, replay-safe, and observable.**
20. **Unresolved architecture fails closed.** Draft/configuration may proceed where safe; production activation does not guess.

---

## 6. Proposed Folder / Code Structure

The root code standards own final repository conventions. If they do not already establish equivalent paths, use the following Module-local organization:

```text
src/
  modules/
    gamification-rewards/
      domain/
        policies/
          program-policy.ts
          rule-policy.ts
          point-ledger-policy.ts
          challenge-policy.ts
          leaderboard-policy.ts
          reward-policy.ts
          reward-redemption-policy.ts
          no-paid-prize-odds-policy.ts
        types/
          point-account.ts
          gamification-decisions.ts
          reward-effect.ts

      application/
        commands/
          configure-program.ts
          configure-rule.ts
          transition-program.ts
          record-eligible-activity.ts
          append-manual-point-adjustment.ts
          join-challenge.ts
          complete-challenge-participant.ts
          configure-reward.ts
          transition-reward.ts
          request-reward-redemption.ts
          transition-reward-redemption.ts
        queries/
          get-program.ts
          list-rules.ts
          get-point-ledger.ts
          get-point-balance.ts
          list-challenges.ts
          get-leaderboard.ts
          list-rewards.ts
          get-reward-redemption.ts
        services/
          rule-evaluator.ts
          challenge-evaluator.ts
          reward-eligibility.ts
          reward-effect-router.ts

      contracts/
        public.ts
        events.ts
        privacy.ts
        dependency-ports.ts

      infrastructure/
        repositories/
          gamification-program-repository.ts
          point-ledger-repository.ts
          challenge-repository.ts
          leaderboard-repository.ts
          reward-repository.ts
        projections/
          point-balance-projector.ts
          leaderboard-projector.ts
        providers/
          # empty until an explicitly approved provider is owned here

      workers/
        source-event-worker.ts
        challenge-evaluation-worker.ts
        projection-rebuild-worker.ts
        point-expiration-worker.ts       # only after U-GR-05 is resolved
        reward-fulfillment-worker.ts     # only for approved reward effects
        tax-value-report-worker.ts

      admin/
        # thin Module-specific admin composition only if root UI conventions permit

      privacy/
        enumerate-subject-data.ts
        execute-privacy-instruction.ts
        evaluate-retention.ts

      tests/
        unit/
        contract/
        integration/
```

### Folder rules

- Routes/server actions remain thin adapters according to root conventions.
- Repositories access only Module-owned records by default.
- Cross-Module reads use dependency ports/public contracts.
- `providers/` stays empty until provider ownership is explicitly approved.
- `workers/` contains owner job definitions, not a private queue framework.
- No `shared/rewards`, `generic-ledger`, `gamification-auth`, `reward-notifications`, or local privacy framework may be created.
- Public contracts expose bounded DTOs, never Prisma models.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / UI adapters | Input collection, DTO mapping, rendering of Module results, admin/user interaction approved by product context | business rules, direct Prisma writes, permission interpretation, tax/provider logic |
| Application commands | orchestration of one Module-owned mutation, shared-operation invocation, transaction boundary | generic auth/idempotency/queue implementation, other Module lifecycle writes |
| Application queries | authorized reads/projections and bounded DTOs | cross-domain repositories, provider reads, reconstructed external readiness |
| Domain policies | deterministic rule matching, point semantics, challenge policy, reward/redemption policy, no-paid-odds rule | Stripe/tax/consent/hold/notification/provider state |
| Repositories | CRUD/append access to Module-owned Prisma records | unrestricted access to Order, Review, TaxProfile, ComplianceHold, ConsentLog, Search, Notification tables |
| Projections | point balance and leaderboard rebuild/update logic | source point truth, Typesense/global Search truth |
| Workers | owner-specific event/job payload and completion behavior | queue engine, retry engine, operational incident lifecycle |
| Provider adapters | only future provider explicitly assigned to this Module | Payment/Tax, Notification, Search, Subscription, or other owners' providers |
| Public contracts | stable Module commands, queries, event schemas, privacy executor | Prisma models, provider payloads, generic platform contracts |
| Privacy executor | enumerate and apply approved privacy dispositions to owned records | `PrivacyRequest`, `DataErasureJob`, or retention-exemption lifecycle |
| Admin composition | Module-specific program/rule/reward/redemption controls | generic admin authorization, tax dashboard, hold management, provider dashboards |

---

## 8. Data Model

### `GamificationProgram`

**Purpose:** Root configuration/lifecycle record for one deterministic incentives program.

**Key relationships:**
- one-to-many `GamificationRule`;
- one-to-many `Challenge`;
- one-to-many `Leaderboard`;
- one-to-many `Reward`;
- one-to-many optional `PointLedgerEntry`.

**Authoritative fields:**
- `status`;
- `name`;
- `description`;
- `startsAt`;
- `endsAt`;
- `termsVersion`.

**Lifecycle:** `GamificationProgramStatus`.

**Concurrency:** Admin transitions/edits must use idempotent commands and stale-write protection where root persistence conventions require it.

**Retention/privacy:** Primarily configuration, not subject data. Terms references may need long-term retention to explain historical awards/redemptions.

### `GamificationRule`

**Purpose:** Declarative mapping from one trigger to deterministic point value and conditions.

**Key relationships:** belongs to one `GamificationProgram`.

**Authoritative fields:**
- `trigger`;
- `points`;
- `isActive`;
- `ruleJson`.

**Constraints:** Current schema indexes `(programId, isActive)` and `trigger`, but does not version historical rule edits.

**Concurrency:** Rule activation/edit conflicts must not lead to ambiguous award semantics.

**Retention/privacy:** `ruleJson` must not contain raw private source payloads or executable code.

**Architecture note:** PR-CL10-03 is inherited: `ruleJson` must be typed, schema-versioned declarative configuration.

### `PointLedgerEntry`

**Purpose:** Immutable point delta/provenance record.

**Key relationships:**
- required `User`;
- optional `ProfessionalProfile`;
- optional `GamificationProgram`;
- optional `Order`;
- optional `RewardRedemption`.

**Authoritative fields:**
- `type`;
- `source`;
- `points`;
- `createdAt`;
- safe provenance in `note`/`metadata` where approved.

**Indexes:** by User/time, Professional/time, program, type/source, Order, RewardRedemption.

**Concurrency:** Award dedupe and spend sufficiency must be transaction-safe. The row itself is append-only.

**Retention/privacy:** Contains subject identifiers and potentially personal content in `note`/`metadata`. Metadata must be schema-validated and minimized. Tax/fraud/reward evidence may create retention requirements evaluated through Privacy protocol.

**Missing structural proof:** No explicit `sourceEventId`, `ruleId`, or `reversalOfEntryId` is present. Canonical idempotency/inbox mechanisms must be used; schema expansion requires an approved ruling.

### `Challenge`

**Purpose:** Defines an engagement challenge under one program.

**Key relationships:** belongs to one Program; has many participants.

**Authoritative fields:** `status`, name/description, dates, `rewardJson`.

**Concurrency:** Lifecycle transitions and completion windows must be owner-controlled.

**Retention/privacy:** Configuration record; `rewardJson` must not contain executable logic or duplicate external reward/provider state.

**Unresolved:** Meaning of `rewardJson` relative to `Reward` and point rules (U-GR-07).

### `ChallengeParticipant`

**Purpose:** Records a User's participation and completion in one Challenge.

**Key relationships:** required User; optional ProfessionalProfile; composite primary key `(challengeId, userId)`.

**Authoritative fields:** `status`, `joinedAt`, `completedAt`.

**Uniqueness:** Composite PK makes join idempotent at the data layer.

**Concurrency:** Duplicate join/completion events must not create duplicate award effects.

**Retention/privacy:** Subject data. May be erased/anonymized only through Privacy owner protocol subject to evidence requirements.

**Unresolved:** The schema reuses `ChallengeStatus`, which includes values that may not be valid participant states.

### `Leaderboard`

**Purpose:** Defines a ranking context and optional time window within one Program.

**Key relationships:** belongs to Program; has many `LeaderboardEntry`.

**Authoritative fields:** name/window. It is definition truth, not point truth.

**Retention/privacy:** Configuration.

### `LeaderboardEntry`

**Purpose:** Rebuildable score/rank projection.

**Key relationships:** Leaderboard, required User, optional ProfessionalProfile.

**Authoritative projection fields:** `points`, `rank`, `updatedAt`.

**Uniqueness:** `@@unique([leaderboardId, userId])`.

**Concurrency:** Projector must be idempotent and checkpointed; concurrent rebuild/incremental writes must not corrupt final rank.

**Retention/privacy:** Public/private exposure depends on product policy and authorization. Privacy may require deletion/anonymization/rebuild.

### `Reward`

**Purpose:** Deterministic reward catalog definition.

**Key relationships:** optional Program; many `RewardRedemption`.

**Authoritative fields:**
- `type`;
- `status`;
- value/currency;
- `pointCost`;
- `inventory`;
- `termsVersion`.

**Lifecycle:** `RewardStatus`.

**Concurrency-sensitive fields:** `inventory` and point-cost redemption behavior.

**Retention/privacy:** Configuration. Historical redemptions snapshot value and must not be rewritten by later Reward edits.

**Unresolved:** inventory semantics and several reward effect contracts.

### `RewardRedemption`

**Purpose:** User claim and fulfillment lifecycle for one Reward.

**Key relationships:**
- Reward;
- required User;
- optional ProfessionalProfile;
- optional `ComplianceHold` reference;
- optional `TaxProfile` reference;
- related point-ledger entries.

**Authoritative fields:**
- `status`;
- `valueCents`/`currency` snapshot;
- `requestedAt`;
- `fulfilledAt`;
- `cancelledAt`;
- proof references.

**Indexes:** reward/status, User/time, Professional/time, status, tax profile.

**Concurrency:** Request + point spend + inventory reservation must be one transaction or equivalent canonical atomic operation.

**Retention/privacy:** Contains subject identity and potentially tax-relevant value evidence. Do not erase without Privacy-coordinated retention decision.

**External references do not transfer ownership:** `blockedByHoldId` does not make Hold local truth; `taxProfileId` does not make tax readiness local truth.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 `GamificationProgramStatus`

Statuses:

```text
draft
active
paused
ended
archived
```

**Transition owner:** Gamification / Rewards application service.

**Inherited Proposed Ruling PR-CL10-04:**

```text
draft → active
active → paused | ended
paused → active | ended
ended → archived
```

`archived` is terminal under the proposal.

**Triggers:** authorized admin command; date-based automation may request an owner transition if later specified.

**Concurrency:** transition command uses SH-044 and SH-053; stale concurrent admin edits use SH-052 where applicable.

**History proof:** authoritative Program state + outbox event + material AuditEvent.

**Prohibited shortcuts:** direct status update from UI or worker repository.

### 9.2 `GamificationRule.isActive`

There is no separate rule-status enum.

**Owner behavior:**
- create/update declarative rule configuration;
- activate/deactivate only through owner command;
- reject activation when the trigger source contract is unresolved or configuration fails schema/policy validation.

**History proof:** audit material changes; point entries must preserve enough causation/evidence to explain which rule produced an effect. Exact rule-version proof is U-GR-03.

### 9.3 `PointLedgerEntryType`

```text
earned
spent
reversed
expired
adjusted
```

This is append-only transaction vocabulary, not a mutable status lifecycle.

**Correction rule:**

```text
historical entry
→ new compensating entry
→ optional corrected entry
```

Never update/delete a historical point row to change balance in ordinary workflow.

**Unresolved:** exact signed-delta convention, reversal linkage, and expiration-lot semantics.

### 9.4 `ChallengeStatus`

```text
draft
active
paused
completed
cancelled
archived
```

**Inherited proposed transition graph:**

```text
draft → active | cancelled
active → paused | completed | cancelled
paused → active | completed | cancelled
completed | cancelled → archived
```

**Owner:** Gamification / Rewards.

**History proof:** Challenge state + domain events + audit for material admin transitions.

### 9.5 `ChallengeParticipant.status`

Current schema reuses `ChallengeStatus`.

**Binding constraint:** normal services must not freely expose/write all `ChallengeStatus` values as participant states.

**U-GR-06:** final participant vocabulary is unresolved.

**Proposed conservative write subset pending approval:**

```text
active → completed | cancelled
```

Do not write `draft`, `paused`, or `archived` for a participant unless architecture explicitly defines their participant meaning.

### 9.6 `RewardStatus`

```text
draft
active
paused
retired
```

**Inherited proposed transition graph:**

```text
draft → active | retired
active → paused | retired
paused → active | retired
```

`retired` is terminal under the proposal.

**Activation gate:** a Reward cannot become production-active if its effect/fulfillment contract is unsupported or if limited inventory semantics required by the Reward are unresolved.

### 9.7 `RewardRedemptionStatus`

```text
pending_confirmation
pending_tax
approved
fulfilled
blocked
cancelled
reversed
```

**Transition owner:** Gamification / Rewards only.

**Binding prohibitions inherited from CL-10:**
- `pending_tax` cannot directly become `fulfilled`;
- `blocked` cannot directly become `fulfilled`;
- provider callbacks cannot update status directly;
- `fulfilled` cannot be deleted/rewritten to hide fulfillment;
- correction uses `reversed` plus compensating effects where supported.

**Proposed baseline path:**

```text
pending_confirmation
  → pending_tax
  → approved
  → fulfilled

pending_confirmation | pending_tax | approved
  → blocked or cancelled where owner policy allows

approved | fulfilled
  → reversed only when the reward effect has an approved compensating path
```

**Unresolved:** exact `blocked` reopen path, cancellation after approval, and compensation rules (U-GR-16).

**History proof:** current row + owner domain events + audit for material admin transitions. A future fulfillment-attempt record is not approved yet.

---

## 10. Commands

### `configureGamificationProgram`

**Purpose:** Create/update a draft or otherwise editable Program.

**Actor/context:** authenticated authorized admin.

**Inputs:** program ID if update, name/description, timing, terms-version requirement, expected version/idempotency key.

**Preconditions:**
- SH-001 actor;
- SH-002 authorization;
- valid timing;
- terms version resolved through SH-009 when required.

**Writes:** `GamificationProgram`.

**Shared operations:** SH-001, SH-002, SH-009, SH-044, SH-052, SH-029, SH-046.

**Effects:** material changes audited; domain event when lifecycle-relevant.

**Idempotency:** same idempotency key + same fingerprint replays prior result.

**Failures:** invalid timing/configuration, stale write, forbidden, dependency unavailable.

### `configureGamificationRule`

**Purpose:** Create/update declarative rule configuration.

**Inputs:** Program, trigger, deterministic points, typed/versioned rule payload, active flag.

**Preconditions:** Program editable; trigger supported; rule payload schema valid; no executable code; no chance-odds effect.

**Writes:** `GamificationRule`.

**Shared operations:** SH-001, SH-002, SH-044, SH-052, SH-029.

**Failure:** unsupported trigger such as `delivery_on_time` before source contract resolution must remain inactive.

### `transitionGamificationProgram`

**Purpose:** Apply owner lifecycle transition.

**Inputs:** Program ID, requested state, actor/reason, idempotency key.

**Preconditions:** transition allowed; activation gates satisfied.

**Writes:** `GamificationProgram.status`.

**Shared operations:** SH-001, SH-002, SH-044, SH-053, SH-029, SH-046.

### `recordEligibleActivity`

**Purpose:** Consume one authoritative source event, evaluate active rules, append point effects exactly once.

**Actor/context:** system/event consumer with trusted source event envelope.

**Inputs:** event ID/type/version, subject User/profile, occurredAt, source reference, safe facts.

**Preconditions:**
- source event type is approved;
- SH-045 inbox claim succeeds;
- event payload/version valid;
- applicable Program/Rule active at owner-defined effective time;
- no-paid-odds policy passes.

**Writes:** one or more `PointLedgerEntry` rows in a transaction with owner outbox effects.

**Shared operations:** SH-045, SH-044, SH-031, SH-046, SH-032/033/034.

**Idempotency:** semantic effect key includes source event + rule/handler identity; duplicate delivery returns prior/no-op result.

**Failures:** malformed source event, unsupported version, source trigger unresolved, transaction failure, permanent policy denial.

### `appendManualPointAdjustment`

**Purpose:** Perform privileged adjustment or reversal without rewriting ledger history.

**Actor/context:** authenticated authorized admin/support; SH-014 if root policy classifies action as sensitive.

**Inputs:** subject, delta/reversal intent, reason, evidence reference, idempotency key.

**Preconditions:** authorization, optional step-up, valid point semantics, original entry exists for reversal where applicable.

**Writes:** new `PointLedgerEntry`.

**Shared operations:** SH-001, SH-002, conditional SH-014, SH-044, SH-031, SH-029, SH-046.

**Failures:** unauthorized, step-up required, invalid correction, duplicate/replay, unresolved reversal semantics.

### `joinChallenge`

**Purpose:** Create/return one ChallengeParticipant.

**Inputs:** challenge ID, actor User, optional ProfessionalProfile context, idempotency key.

**Preconditions:** Challenge active and in window; participant eligible; participant status behavior permitted.

**Writes:** `ChallengeParticipant`.

**Shared operations:** SH-001, SH-002 where required, SH-044, SH-046.

**Idempotency:** composite PK plus SH-044; duplicate join returns existing participant.

### `completeChallengeParticipant`

**Purpose:** Mark a participant complete after owner-approved evidence and emit the internal completion fact.

**Inputs:** challenge/subject, completion evidence/source event, idempotency key.

**Preconditions:** participant active; challenge completion allowed; source evidence valid; duplicate completion prevented.

**Writes:** `ChallengeParticipant.status/completedAt`; completion may feed `recordEligibleActivity` through the standard rule path.

**Shared operations:** SH-044, SH-045 when event-driven, SH-053, SH-046.

### `configureReward`

**Purpose:** Create/update Reward catalog configuration.

**Inputs:** Program context, type, point cost, value/currency, inventory, termsVersion, desired status.

**Preconditions:** supported reward type/effect for activation; terms version resolvable; no-paid-odds policy.

**Writes:** `Reward`.

**Shared operations:** SH-001, SH-002, SH-009, SH-044, SH-052, SH-029, SH-053.

**Failures:** unsupported effect, unresolved inventory semantics for finite inventory, invalid value/point configuration.

### `requestRewardRedemption`

**Purpose:** Atomically validate, spend/reserve required point value, and create RewardRedemption.

**Inputs:** actor, Reward ID, optional profile context, consent proof reference/lookup context, idempotency key.

**Preconditions:**
- Reward active;
- applicable Program active where required;
- SH-008 consent proof sufficient;
- SH-011 hold decision permits request;
- sufficient point value under approved point-account scope;
- reward effect supported at least through initial state;
- inventory rules satisfied when applicable.

**Writes:** `RewardRedemption`, point-spend `PointLedgerEntry`, inventory reservation/update only under approved U-GR-08 design.

**Shared operations:** SH-001, SH-002, SH-008, SH-011, SH-044, SH-056, SH-031, SH-046.

**Transaction:** redemption + point spend + reservation are atomic.

**Failures:** insufficient points, consent required, hold blocked, reward unavailable, unsupported effect, unresolved limited inventory, conflict.

### `transitionRewardRedemption`

**Purpose:** Apply one owner-controlled redemption status change after external evidence is returned.

**Inputs:** redemption ID, requested transition, evidence refs, actor/system context, idempotency key.

**Preconditions:** transition matrix permits move; hold/tax/effect evidence satisfies local policy.

**Writes:** `RewardRedemption`.

**Shared operations:** SH-044, SH-053, SH-011, SH-019/SH-118 where applicable, SH-029, SH-046, SH-041.

**Failures:** stale transition, active hold, tax review required, unsupported effect, dependency unavailable.

### `rebuildGamificationProjection`

**Purpose:** Rebuild point-balance/leaderboard projections from authoritative records.

**Inputs:** projection type/scope, checkpoint/version, admin/system context.

**Writes:** projection records only (`LeaderboardEntry` and any approved balance projection).

**Shared operations:** SH-047, SH-048, SH-115, SH-038, SH-037.

**Failures:** source read failure, projection write failure, retry exhaustion. Source truth remains unchanged.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result type | Meaning | Consumer must not infer |
|---|---|---|---|---|---|
| `getGamificationProgram` | admin/UI/internal services | Program ID | source truth DTO | Current Program configuration/state | consent acceptance or external readiness |
| `listGamificationRules` | admin/internal evaluator | Program/trigger filters | source truth DTOs | Current rules | historical rule semantics for old awards unless preserved as evidence |
| `getPointLedger` | User/admin UI, support | subject + pagination/filter | source truth DTOs | Authorized point history | mutable balance authority |
| `getPointBalance` | User/admin/reward eligibility | point-account context | projection/derived result | Current available balance as-of checkpoint | independent financial value, cash balance, or prize odds |
| `listChallenges` / `getChallenge` | User/admin | Program/subject/status | truth + participation context | Challenge definition and participant state | source event truth from other Modules |
| `getLeaderboard` | User/admin | Leaderboard ID/page | projection DTO | rank/score as-of checkpoint | point transaction truth |
| `listRewards` / `getReward` | User/admin | Program/status/type | catalog truth DTO | reward configuration/availability facts | consent, hold, tax, provider completion |
| `evaluateRewardRedemptionEligibility` | redemption command/UI preview | User + Reward + context | Module decision | current local eligibility composition | guaranteed future fulfillment or tax approval |
| `getRewardRedemption` | User/admin/downstream composition | redemption ID/subject | source truth DTO | current redemption state/value snapshot | TaxProfile status, hold release authority, provider truth |

### Decision-result pattern

If SH-015 is approved, Module decisions should conform to the canonical decision envelope.

Until then, Module public decisions must still use stable reason codes and return:

- decision: allow / deny / review / remediation;
- reason code(s);
- safe evidence references;
- evaluatedAt;
- policy/config version where applicable;
- next action where applicable.

Never return raw provider errors as business reason codes.

---

## 12. Public Module Interface

### Public commands

- `configureGamificationProgram`
- `configureGamificationRule`
- `transitionGamificationProgram`
- `recordEligibleActivity`
- `appendManualPointAdjustment`
- `joinChallenge`
- `completeChallengeParticipant`
- `configureReward`
- `requestRewardRedemption`
- `transitionRewardRedemption`
- `rebuildGamificationProjection`
- Privacy executor commands defined by SH-095 protocol

### Public queries

- `getGamificationProgram`
- `listGamificationRules`
- `getPointLedger`
- `getPointBalance`
- `listChallenges`
- `getChallenge`
- `getLeaderboard`
- `listRewards`
- `getReward`
- `evaluateRewardRedemptionEligibility`
- `getRewardRedemption`
- subject-data enumeration through SH-096 protocol

### Emitted domain events

Semantic event families:

- `GamificationProgramActivated`
- `GamificationProgramPaused`
- `GamificationProgramEnded`
- `PointLedgerEntryAppended`
- `ChallengeJoined`
- `ChallengeCompleted`
- `RewardRedemptionRequested`
- `RewardRedemptionStatusChanged`
- `RewardRedemptionFulfilled`
- `RewardRedemptionReversed`

Exact event namespace/version naming follows root event standards.

### Privacy executor

This Module implements:

- subject-data enumeration;
- retention-fact evaluation;
- erase/anonymize/export/restrict/retain execution over owned records;
- idempotent result reporting back to Privacy.

It does not create PrivacyRequest/DataErasureJob.

### Provider-facing interfaces

None are currently confirmed.

A `RewardFulfillmentPort` may be introduced only after U-GR-09 identifies an effect/provider owned by this Module. Payment, Tax, Notification, Search, and Track provider integrations remain outside.

---

## 13. Inbound Dependencies

| Owning Module/capability | Public operation/interface | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | SH-001 `resolveAuthenticatedActor` | trusted actor for protected commands | actor ID/type/session assurance | Yes | session/current-user helper |
| Role / Authority | SH-002 `authorizeResourceAction` | protected reads/admin commands | action, resource facts, scope | Yes | role engine/permission booleans |
| Consent & Disclosure | SH-009 / SH-008 | active terms version and proof | type, version, proof ID/status | Yes for configured actions | ConsentLog/version catalog |
| Transaction / Order | versioned Order-completed event/public contract | deterministic `order_completed` trigger | event ID/version, subject, Order ref, occurredAt, safe facts | Rule activation/effect | direct Order repository or Stripe interpretation |
| Review / Dispute | versioned eligible-rating event | `high_rating_received` trigger | event ID/version, subject, Review ref, safe qualification fact | Rule activation/effect | review repository/threshold truth unless event contract defines it |
| Professional Eligibility | versioned profile-completed event/context | `profile_completed` trigger | event ID/version, User/Profile ref, occurredAt | Rule activation/effect | profile lifecycle |
| Admin Review / Compliance Hold | SH-011/SH-012 | block redemption or escalate abuse evidence | hold IDs/reasons/scope/expiry | Yes | local blocked state/hold lifecycle |
| Payment / Payout / Tax | SH-019, SH-118 | tax readiness and reportable reward value | readiness dimensions; source value/currency/date | Yes for tax-sensitive fulfillment | tax profile/provider/reporting |
| Notification | SH-041 | communicate business outcome | recipient IDs, template key, safe variables | No to committed domain truth; may affect communication UX | delivery/provider |
| Audit / Event Ledger | SH-029/030 | material action/sensitive access proof | actor/action/target/safe metadata | No to domain truth; audit policy may require success semantics | AuditEvent/AccessAuditLog storage |
| Observability / Ops | SH-032/033/034/037/038 | trace, logs, failures, queue telemetry | safe operational identifiers | No to business truth | local logger/incident/queue tables |
| Privacy / Data Erasure | SH-095–098 | legal privacy orchestration | target/action, subject, retention decision | May block erasure | local privacy workflow |
| Track Subscription & Entitlement | SH-119 only if approved | deterministic temporary benefit effect | source reward, benefit key/value/interval | Yes for that effect | local entitlement/premium flag |
| Search / affected feature | future approved effect interface | implement `profile_boost` or similar effect | approved grant/effect reference | Yes for that effect | Typesense/Search writes |
| Sweepstakes / Prize | only explicitly approved bridge | future deterministic fact may be consumed by Sweepstakes | bounded event/command facts | Yes for bridge only | PrizeEntry/drawing/odds logic |

### Baseline dependency exclusions

The Module does **not** currently require:

- SH-005 `resolveEntitlement` for ordinary points/rewards;
- Trust Verification readiness;
- Healthcare readiness;
- Job Compliance;
- Search indexing;
- Media access.

If a future program needs those facts, architecture must identify the exact owner interface first.

---

## 14. Outbound Consumers and Effects

### Consumers

- **Payment / Payout / Tax:** consumes recognized reward value through SH-118.
- **Notification:** consumes notification requests after meaningful owner transitions.
- **Audit / Event Ledger:** consumes material action/audit requests.
- **Admin Review / Compliance Hold:** consumes abuse/fraud evidence requests through SH-012.
- **Professional Eligibility / Search / Track:** may consume an approved deterministic reward-effect request, but only after U-GR-09/U-GR-10 are resolved.
- **Sweepstakes / Prize:** may consume an explicitly approved Gamification fact in the future; it owns all PrizeEntry/odds decisions.

### Downstream effects

The Module may request:

- tax value recognition;
- hold creation/review;
- notification delivery;
- audit recording;
- temporary deterministic feature grants once approved;
- projection rebuild within Gamification;
- operational job/failure telemetry.

It must not directly mutate downstream source tables.

---

## 15. Canonical Shared Operations Used

Only operations relevant to this Module are listed. The canonical definitions remain in `context/shared/shared-operations.md`.

### SH-001 — `resolveAuthenticatedActor`
**Classification:** canonical shared capability  
**Owner:** Identity & Access  
**Why used:** establish trusted User/admin actor for protected commands and reads.  
**Invocation:** command/query boundary before Module policy.  
**Local policy:** which Gamification action is being attempted and which subject/resource is involved.  
**Expected result:** typed actor context with required assurance/session facts.  
**Do not build:** `gamificationAuth.ts`, `rewardUserResolver.ts`, `currentGamificationUser.ts`.

### SH-002 — `authorizeResourceAction`
**Classification:** canonical shared capability  
**Owner:** Role / Authority  
**Why used:** authorize self-service and privileged program/rule/point/reward actions.  
**Invocation:** after SH-001, before protected read/write.  
**Local policy:** action vocabulary and resource relationship facts.  
**Expected result:** allow/deny decision with stable reason.  
**Do not build:** `rewardPermissions.ts`, `gamificationRoleGuard.ts`, local role matrix.

### SH-008 — `queryConsentProof`
**Classification:** another Module's public interface  
**Owner:** Consent & Disclosure  
**Why used:** prove required gamification/reward terms version was accepted.  
**Invocation:** reward redemption and any user action configured to require proof.  
**Local policy:** which terms type/version is sufficient.  
**Expected result:** proof ID/type/version/time/validity.  
**Do not build:** `rewardConsentService.ts`, local consent table.

### SH-009 — `resolveActiveConsentVersion`
**Classification:** canonical shared capability  
**Owner:** Consent & Disclosure  
**Why used:** bind Program/Reward configuration to the applicable terms version.  
**Invocation:** configuration/activation.  
**Local policy:** which consent type applies.  
**Do not build:** local terms-version catalog/resolver.

### SH-011 — `evaluateComplianceHold`
**Classification:** another Module's public interface  
**Owner:** Admin Review / Compliance Hold  
**Why used:** stop redemption/fulfillment where applicable.  
**Invocation:** redemption request and before sensitive fulfillment/transition.  
**Local policy:** which hold scopes/reasons block which Gamification actions.  
**Expected result:** applicable hold IDs/safe reasons/scope/expiry.  
**Do not build:** `rewardBlocked.ts`, `gamificationHoldService.ts`, `isBlocked` truth.

### SH-012 — `requestComplianceHold`
**Classification:** another Module's public interface  
**Owner:** Admin Review / Compliance Hold  
**Why used:** escalate points abuse/reward fraud evidence for authoritative review.  
**Invocation:** local abuse-signal detection or admin workflow.  
**Local policy:** evidence threshold and requested scope.  
**Do not build:** local fraud-ban/hold lifecycle.

### SH-014 — `requireStepUpForSensitiveAction`
**Classification:** canonical shared capability  
**Owner:** Identity & Access  
**Why used:** high-risk admin point-value changes and financially sensitive fulfillment if root policy requires it.  
**Invocation:** before privileged mutation.  
**Local policy:** action declared sensitive; no local challenge logic.  
**Do not build:** reward OTP/MFA/passkey flow.

### SH-019 — `evaluateFinancialReadiness`
**Classification:** another Module's public interface  
**Owner:** Payment / Payout / Tax  
**Why used:** determine tax/financial readiness for tax-sensitive reward fulfillment.  
**Invocation:** before owner transition from tax-pending to approved/fulfillable.  
**Local policy:** which reward needs the gate and how result maps to local status.  
**Do not build:** `rewardTaxProfileService.ts`, `taxApproved`.

### SH-029 — `appendAuditEvent`
**Classification:** canonical shared capability  
**Owner:** Audit / Event Ledger  
**Why used:** material admin/configuration/adjustment/fulfillment proof.  
**Invocation:** material mutation and exceptional manual action.  
**Local policy:** safe action name/metadata.  
**Do not build:** `gamificationAudit` storage.

### SH-030 — `recordSensitiveAccess`
**Classification:** canonical shared capability  
**Owner:** Audit / Event Ledger  
**Why used:** sensitive tax/financial reward admin views where root sensitivity policy requires it.  
**Invocation:** protected read after authorization decision.  
**Local policy:** target sensitivity/context.  
**Do not build:** `rewardAccessLog.ts`.

### SH-031 — `appendDomainLifecycleEvent`
**Classification:** shared mechanism / separate truth  
**Owner:** shared persistence mechanism; Gamification owns `PointLedgerEntry` truth  
**Why used:** consistent append-only ledger mechanics.  
**Invocation:** point earn/spend/reversal/expiration/adjustment transaction.  
**Local policy:** point type/source/delta/provenance/reversal semantics.  
**Do not build:** generic ledger merging points with Order/payment/usage records.

### SH-032 / SH-033 / SH-034 — request context, structured logging, telemetry sanitization
**Classification:** platform primitives/capabilities  
**Owner:** Observability / Ops  
**Why used:** correlate commands/events/jobs without leaking sensitive payloads.  
**Invocation:** every request/job/event handler.  
**Local policy:** safe Module dimensions and sensitivity labels.  
**Do not build:** local logger, raw payload dumps, telemetry sanitizer.

### SH-037 / SH-038 — integration failure and queue telemetry
**Classification:** cross-cutting capability  
**Owner:** Observability / Ops / queue infrastructure  
**Why used:** record retry exhaustion, downstream failure, queue state.  
**Invocation:** workers and dependency/provider failures.  
**Local policy:** business state remains valid/explainable; retryability classification.  
**Do not build:** `RewardIntegrationFailure`, `GamificationQueueJob` tables.

### SH-041 — `requestNotification`
**Classification:** canonical shared capability  
**Owner:** Notification  
**Why used:** point/challenge/redemption status communication.  
**Invocation:** after authoritative owner transition commits.  
**Local policy:** trigger, template meaning, safe variables, recipient intent.  
**Do not build:** `rewardEmailService`, `pointsPush`, provider client.

### SH-044 — `executeIdempotentCommand`
**Classification:** platform primitive  
**Owner:** platform application infrastructure  
**Why used:** create/update/transition/redeem commands must replay safely.  
**Invocation:** command boundary before write transaction.  
**Local policy:** semantic command identity and replay result.  
**Do not build:** feature idempotency table/helper.

### SH-045 — `deduplicateDomainEvent`
**Classification:** platform primitive  
**Owner:** platform event infrastructure; consumer owns handler identity  
**Why used:** duplicate source events must not award twice.  
**Invocation:** inbound source-event worker before rule effect.  
**Local policy:** event + handler/rule semantics.  
**Do not build:** `ProcessedGamificationEvent`.

### SH-046 — `publishDomainEvent`
**Classification:** platform primitive  
**Owner:** platform outbox infrastructure  
**Why used:** publish owner facts after authoritative transaction commits.  
**Invocation:** same transaction as state/ledger mutation.  
**Local policy:** event names, payload minimization, emission conditions.  
**Do not build:** `gamificationPublisher`, private event bus/outbox.

### SH-047 / SH-048 — reliable job and retry with backoff
**Classification:** platform primitives  
**Owner:** shared queue infrastructure  
**Why used:** event processing, projection rebuild, tax report retry, approved fulfillment.  
**Invocation:** asynchronous work.  
**Local policy:** payload, idempotency key, retryable/permanent classification, completion meaning.  
**Do not build:** `gamificationQueue`, custom retry loop.

### SH-051 — `acquireAggregateLock`
**Classification:** platform primitive  
**Owner:** shared persistence infrastructure  
**Why used:** serialize conflicting point/redemption/projection actions where required.  
**Invocation:** within transaction around contested resource.  
**Local policy:** lock key/conflicting actions.  
**Do not build:** in-memory points/reward mutex.

### SH-052 — `withOptimisticConcurrency`
**Classification:** platform primitive  
**Owner:** shared persistence infrastructure  
**Why used:** reject stale admin edits/transitions.  
**Invocation:** Program/Rule/Reward edits where expected version strategy is adopted.  
**Local policy:** retry vs conflict.  
**Do not build:** ad hoc updatedAt comparison helpers.

### SH-053 — `transitionLifecycleState`
**Classification:** shared mechanism / separate truth  
**Owner:** shared transition mechanism; Gamification owns transition graph  
**Why used:** consistent lifecycle mutation plumbing.  
**Invocation:** Program, Challenge, Reward, RewardRedemption transitions.  
**Local policy:** all allowed transitions and gates.  
**Do not build:** generic table that owns Gamification semantics.

### SH-056 — `executeAtomicReservation`
**Classification:** shared mechanism / separate truth  
**Owner:** shared database primitive  
**Why used:** prevent point overspend and, after U-GR-08, limited-inventory oversubscription.  
**Invocation:** Reward redemption transaction.  
**Local policy:** point sufficiency, inventory meaning, release/commit behavior.  
**Do not build:** check-then-decrement helper or local lock service.

### SH-095 / SH-096 / SH-097 / SH-098 — Privacy owner protocol
**Classification:** cross-cutting protocol/capability  
**Owner:** Privacy orchestrates; Gamification executes owned-data actions  
**Why used:** enumerate, retain, anonymize, erase/export owned subject data.  
**Invocation:** Privacy-request target execution.  
**Local policy:** record inventory, required retention facts, field mappings.  
**Do not build:** local PrivacyRequest/DataErasureJob workflow.

### SH-115 — `buildAggregateProjection`
**Classification:** shared mechanism / separate truth  
**Owner:** projection owner = Gamification for point balance/leaderboard  
**Why used:** build/rebuild deterministic read models.  
**Invocation:** after ledger changes, challenge completion, backfill/reconciliation.  
**Local policy:** inclusion rules, window, ranking/ties, checkpoint semantics.  
**Do not build:** mutable point-balance authority.

### SH-118 — `reportTaxableValue`
**Classification:** another Module's public interface  
**Owner:** Payment / Payout / Tax  
**Why used:** report recognized reward FMV/value without owning filing truth.  
**Invocation:** approved recognition moment after U-GR-15 is settled.  
**Local policy:** RewardRedemption value snapshot and recognition event.  
**Do not build:** 1099/tax filing service.

### SH-119 — `applyTemporaryFeatureGrant`
**Classification:** proposed cross-cutting public interface  
**Owner:** unresolved between Track Subscription & Entitlement / affected feature  
**Why used:** only for supported deterministic reward effects such as `profile_boost`.  
**Invocation:** after approved redemption/effect decision.  
**Local policy:** why reward was earned and when Gamification considers its effect satisfied.  
**Do not build:** `profileBoost=true`, `premiumReward`, local temporary entitlement.  
**Status:** **Proposed; must not be implemented as confirmed until U-GR-10 is resolved.**

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
|---|---|---|---|---|---|
| `validateProgramConfiguration` | validate timing/terms/activation preconditions | Program candidate + dependency facts | decision/reasons | none | Program semantics are Gamification-owned |
| `validateGamificationRule` | validate trigger, points, rule schema, no-paid-odds constraints | Rule candidate | typed validated rule or denial | none | rule meaning is local |
| `evaluateGamificationRules` | select active rules for one source event | validated event + Programs/Rules | award decisions | none | determines Gamification business effect |
| `derivePointBalance` | sum eligible ledger deltas | point account context + entries | balance breakdown | none | point accounting policy is local |
| `validatePointCorrection` | decide adjustment/reversal legality | actor intent + source ledger entry | correction decision | none | ledger semantics are local |
| `evaluateChallengeParticipation` | decide join/completion under Challenge policy | Challenge + subject + evidence | decision | none | Challenge semantics are local |
| `computeLeaderboardRanking` | calculate rank/ties/window | approved source facts | ranked projection rows | `LeaderboardEntry` | ranking policy is local |
| `validateRewardActivation` | determine whether Reward can become active | Reward + terms/effect/inventory facts | decision | none | catalog policy is local |
| `evaluateRewardRedemptionEligibility` | compose local Reward/points/terms/hold/tax requirements | subject + Reward + dependency decisions | decision/next action | none | redemption eligibility remains local composition |
| `snapshotRewardValue` | preserve historical Reward value on redemption | Reward at request/approval time per approved policy | value/currency | `RewardRedemption` | historical value meaning is local |
| `mapRewardReadinessToStatus` | map tax/hold/effect evidence into allowed local transition | redemption + external decisions | target status or denial | `RewardRedemption` through command | external truth must not own local lifecycle |
| `enforceNoPaidPrizeOddsBoost` | reject Gamification config/effect that influences chance-based odds | Program/Rule/Reward/effect proposal | allow/deny | none | CL-10 joint invariant applied at Gamification boundary |
| `detectGamificationAbuseSignals` | produce local deterministic abuse indicators for review escalation | ledger/redemption activity | transient evidence/request input | none unless existing fields used | Module may detect its own anomalies but does not own a generic fraud platform |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Append-only ledger:** SH-031 mechanics may be reused, but `PointLedgerEntry` stays distinct from `ProfessionalBalanceLedgerEntry`, Order events, subscription usage, or AuditEvent.
2. **Lifecycle plumbing:** SH-053 may implement transition mechanics, but Program/Challenge/Reward/Redemption transition graphs remain Gamification policy.
3. **Idempotency/event inbox:** SH-044/045 are shared; the semantic effect "this source event applied this Gamification rule" is local.
4. **Atomic reservation:** SH-056 is shared; point sufficiency and reward inventory meaning remain local.
5. **Projection engine:** SH-115 is shared; point balance and leaderboard inclusion/rank policy remain local.
6. **Queue/retry:** SH-047/048 are shared; job payload, completion, compensation, and permanent-failure behavior remain local.
7. **Provider status translation:** SH-061 is a provider-adapter pattern only if this Module later owns a reward provider; status mappings remain adapter-local and cannot become a global fulfillment vocabulary.
8. **Privacy protocol:** SH-095–098 are shared; this Module defines its subject-data map and retention facts while Privacy owns orchestration.
9. **Temporary feature grant:** SH-119, if approved, reuses a grant mechanism while Gamification retains RewardRedemption truth and the affected feature retains effect truth.
10. **Decision result:** SH-015 may standardize response shape if approved; it does not centralize reward eligibility policy.

---

## 18. Authentication and Authorization

### Authentication

All protected operations begin with SH-001.

No Module-local session/current-user abstraction is permitted.

### Authorization

All protected reads/mutations use SH-002.

Gamification supplies action vocabulary and resource facts; Role / Authority interprets permission.

### Proposed action vocabulary

Self-service:
- `gamification.points.read_own`
- `gamification.challenge.join`
- `gamification.reward.read`
- `gamification.reward.redeem`
- `gamification.redemption.read_own`

Admin/support:
- `gamification.program.manage`
- `gamification.rule.manage`
- `gamification.challenge.manage`
- `gamification.reward.manage`
- `gamification.points.adjust`
- `gamification.redemption.review`
- `gamification.redemption.transition`
- `gamification.compliance_evidence.read`

Exact capability names must follow the Role / Authority owner's conventions; the semantics above are the required action families.

### Resource ownership/context facts

Gamification can provide:
- whether a PointLedgerEntry/RewardRedemption belongs to the actor's User ID;
- Program/Challenge/Reward identifiers;
- optional ProfessionalProfile contextual linkage;
- requested operation type.

Gamification must not interpret platform/admin role rows itself.

### Step-up

Manual point-value changes, financially/tax-sensitive fulfillment approval, and equivalent high-risk actions are candidates for SH-014 under inherited PR-CL10-09.

The root security owner decides final step-up policy.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying owner | Query/operation | Gamification action gated | Local composition | Result |
|---|---|---|---|---|---|
| Reward/gamification terms proof | Consent & Disclosure | SH-009 / SH-008 | Program/Reward activation and redemption where configured | require exact applicable version; proof is evidence, not permission | allow / consent_required |
| Compliance hold | Admin Review / Compliance Hold | SH-011 | redemption request, approval, fulfillment, reversal as applicable | map active hold scope/reason to local action block | allow / blocked / review |
| Tax/financial readiness | Payment / Payout / Tax | SH-019 | tax-sensitive reward approval/fulfillment | determine whether this Reward requires tax gate; never interpret provider state | allow / pending_tax / blocked/review |
| Taxable value reporting | Payment / Payout / Tax | SH-118 | recognition of reportable Reward value | supply local FMV/value snapshot and approved recognition moment | report accepted/retryable failure |
| Step-up | Identity & Access | SH-014 | high-risk admin point/financial actions | declare action sensitivity; do not own assurance lifecycle | allow / step_up_required |
| Temporary deterministic benefit | SH-119 owner unresolved | SH-119 if approved | profile boost or similar benefit | Gamification owns reason; effect owner applies benefit | fulfilled effect / unsupported |
| Track entitlement | Track Subscription & Entitlement | SH-005 only after explicit ruling | no baseline action currently | ordinary points/rewards are not implicitly plan-gated | unresolved/disabled |
| No-paid-prize-odds | Gamification local + Sweepstakes boundary | local policy; no cross-domain write | all Program/Rule/Reward config and effects | reject any effect intended to improve chance odds | deny |
| Fraud/abuse review | shared owner unresolved; Hold owner confirmed | local signals + SH-012 | suspicious adjustment/redemption | local evidence may request hold; no generic fraud truth | continue / review requested |

No baseline trust-verification, healthcare, or Job-compliance gate is confirmed for this Module.

---

## 20. Provider Integrations

### Current ruling

No external provider integration is currently confirmed as owned by `gamification_rewards`.

Therefore:

- no Stripe client;
- no tax-provider client;
- no email/SMS/push provider;
- no Typesense client for profile boosts;
- no Track billing/provider client;
- no generic gift-card/shipping provider;

belongs in this Module today.

### Future provider requirement

If U-GR-09 assigns a provider-backed Reward effect to this Module, architecture must first define:

```text
Gamification-owned RewardFulfillmentPort
→ provider adapter
→ credentials/secrets held server-side
→ provider call/webhook
→ SH-059 signature verification if webhook
→ SH-060 provider-event dedupe with Module-owned processed-event truth if explicitly approved
→ SH-061 provider status translation
→ SH-062 reconciliation
→ owner transitionRewardRedemption
→ SH-037 operational failure
```

Before that ruling, provider-dependent Reward types remain draft/paused/unfulfillable.

Provider payloads must never become `RewardRedemptionStatus`.

---

## 21. Events and Outbox

### Event contract principles

- events describe facts that already occurred;
- events are emitted transactionally through SH-046;
- payloads are minimized and versioned;
- event envelopes carry event ID, aggregate ID/type, schema version, occurredAt, correlation/causation IDs, and safe subject references;
- consumers must use SH-045 and remain idempotent;
- an event cannot command another Module to mutate hidden state.

### Proposed event families

| Fact | Emission point | Minimum safe payload |
|---|---|---|
| Program activated/paused/ended | same transaction as Program transition | programId, previous/new status, termsVersion ref, occurredAt |
| Point ledger entry appended | same transaction as ledger append | ledgerEntryId, userId, programId?, type/source, point delta, source reference IDs, occurredAt |
| Challenge joined | participant creation | challengeId, userId, participant state |
| Challenge completed | participant completion | challengeId, userId, completedAt |
| Redemption requested | redemption transaction | redemptionId, rewardId, userId, status, value snapshot, point entry refs |
| Redemption status changed | owner transition | redemptionId, previous/new status, evidence refs |
| Redemption fulfilled/reversed | owner transition | redemptionId, reward type, value snapshot, effect reference if safe |

Do not include raw tax data, provider payloads, full rule JSON, arbitrary notes, or secrets.

---

## 22. Background Jobs / Scheduled Work

| Worker | Purpose | Input | Idempotency key | Retryable failures | Permanent/manual failures | Truth updated | Telemetry |
|---|---|---|---|---|---|---|---|
| Source-event worker | evaluate approved source event into point effects | versioned source event | eventId + handlerVersion; business effect also rule-aware | transient DB/queue issues | invalid schema/version, unsupported trigger | `PointLedgerEntry` | SH-038, SH-037 |
| Challenge evaluation worker | evaluate event-driven completion where needed | challenge + event/evidence | challengeId + userId + evidence/event ID | transient reads/writes | invalid participant transition/evidence | `ChallengeParticipant`; points via standard path | SH-038 |
| Projection rebuild worker | rebuild balance/leaderboard | projection scope/version/checkpoint | projection + scope + version | DB/worker failures | invalid projection config | `LeaderboardEntry` / approved projection | lag + SH-038 |
| Point expiration worker | append expirations | eligible point account/lot policy | expiration policy + source entry/period | DB/queue | **architecture blocked until U-GR-05** | `PointLedgerEntry` | SH-038 |
| Tax-value report worker | reliably send recognized value | redemption/value recognition event | redemptionId + recognition version | Tax interface unavailable | invalid valuation/recognition policy | external Tax truth; local status only through owner command | SH-037/038 |
| Reward fulfillment worker | execute approved asynchronous effect | redemption/effect request | redemptionId + effect type/version | approved provider/feature transient error | unsupported effect, manual fulfillment required | external effect + `RewardRedemption` through owner transition | SH-037/038 |
| Privacy executor worker | apply Privacy target instruction if async | privacy target/action | Privacy target/job command ID | transient DB/provider | retention/manual review result | owned personal fields only | SH-038 |

Generic scheduling, queue, retry, heartbeat, and dead-letter mechanics come from SH-047/048.

### Dead-letter behavior

A dead-lettered job must:
- preserve correlation/source IDs;
- record sanitized operational failure;
- leave source truth in a valid state;
- never fabricate a completed point award, projection, or fulfillment;
- remain safe for manual replay after correction.

---

## 23. Concurrency and Idempotency

### Races that must be prevented

1. duplicate source event awarding the same rule twice;
2. same idempotent command executed concurrently;
3. two reward redemptions overspending the same point account;
4. limited reward inventory oversubscription;
5. duplicate challenge completion granting points twice;
6. concurrent Program/Reward lifecycle edits;
7. projection rebuild racing incremental update;
8. duplicate tax-value report or fulfillment result.

### Canonical controls

- SH-044 command idempotency;
- SH-045 event inbox dedupe;
- SH-051 aggregate/database locks where needed;
- SH-052 optimistic concurrency for editable aggregates;
- SH-056 atomic point/inventory reservation;
- database uniqueness such as `(challengeId,userId)` and `(leaderboardId,userId)`;
- one database transaction for authoritative write + outbox.

### Point-award semantic identity

Required semantic invariant:

```text
one authoritative source event
+ one applicable rule semantic identity/version
→ at most one point award effect
```

The exact persistence of rule version/source causation is U-GR-03. Do not create a local processed-event table to bypass SH-045.

### Reward redemption transaction

The transaction must conceptually perform:

```text
validate Reward + local eligibility
→ evaluate external gates outside/at safe boundary
→ acquire point/inventory reservation under approved key
→ re-read authoritative point availability inside transaction
→ create RewardRedemption
→ append PointLedgerEntry(spent) when required
→ commit inventory reservation/update when approved
→ append outbox event
→ commit
```

If any authoritative write fails, no point spend/redemption partial state may remain.

### Lock key

Final point-account lock key depends on U-GR-01. The implementation plan must not hardcode User-only or Program-only accounting scope until that decision is approved.

### Replay result

A repeated idempotency key with the same request fingerprint returns the original success/denial result. A conflicting fingerprint for the same key returns an idempotency conflict.

---

## 24. Media / Storage

No Module-owned `MediaAsset` relationship is confirmed.

Therefore media/storage is not a baseline responsibility.

If a future Reward requires attachments, fulfillment documents, or evidence files:

- Gamification owns the business meaning/reference only;
- Media / File Access owns upload policy, binary validation, malware scanning, object storage, and signed access;
- sensitive reads use SH-030 where required;
- file URLs must not become Reward fulfillment, consent, tax, or audit truth.

Do not add media models solely because `RewardType.physical_prize` exists.

---

## 25. Search / Projection

### Internal projections

Gamification owns:

- derived point balance;
- `LeaderboardEntry`.

Both must be rebuildable through SH-115.

### Global Search

Gamification does not own Typesense or Search projection.

`RewardType.profile_boost` is architecture-blocked until SH-119 ownership/effect contract is approved.

A future approved flow is conceptually:

```text
RewardRedemption approved/fulfilled
→ SH-119 temporary benefit/effect owner
→ affected feature validates benefit
→ Search owner receives any required projection refresh
```

Gamification must not:
- write Typesense;
- write `SearchUpsertEvent`;
- write profile ranking flags;
- create `profileBoost=true`;
- infer Search success from its own redemption status without downstream evidence.

---

## 26. Notification

Gamification owns notification **triggers and message intent**, not delivery.

Potential business triggers:

- points earned where product UX requires notice;
- challenge joined/completed;
- reward redemption requested;
- tax action required;
- redemption approved/blocked;
- fulfillment completed;
- manual adjustment/reversal;
- fraud/abuse review status where safe and policy-approved.

Use SH-041 after authoritative state commits.

Payloads contain:
- recipient User ID;
- template key;
- safe display variables;
- action route/reference;
- sensitivity/priority;
- idempotency key.

Do not include raw TaxProfile fields, provider payloads, arbitrary ledger metadata, or secrets.

Notification failure never changes point/redemption truth.

---

## 27. Audit and Sensitive Access

### Domain history truth

- `PointLedgerEntry` is point history.
- `RewardRedemption` is redemption state.
- lifecycle events/outbox describe domain facts.

### Generic audit

Use SH-029 for:
- Program/Rule/Reward activation, pause, retirement;
- manual point adjustment/reversal;
- exceptional redemption approval/reversal/fulfillment;
- abuse-related hold request;
- material reconciliation repair.

`AuditEvent` does not replace any Module record.

### Sensitive access

Use SH-030 if root sensitivity policy requires logging for:
- tax-linked redemption admin views;
- financially sensitive reward value/fulfillment evidence;
- sensitive provider references introduced later.

No Module-specific access-log table currently exists.

---

## 28. Privacy and Retention

### Subject-data inventory

Through SH-096 enumerate at minimum:

- `PointLedgerEntry` by User;
- `ChallengeParticipant`;
- `LeaderboardEntry`;
- `RewardRedemption`;
- future Module-owned provider references if explicitly introduced.

Program/Rule/Challenge/Leaderboard/Reward configuration is generally not subject-specific in the current schema, though free-text fields must still be reviewed if user-entered personal data can appear.

### Privacy executor

Through SH-095:
- erase where legally/permissibly deletable;
- anonymize/pseudonymize approved personal fields;
- remove from/rebuild projections;
- export owned records;
- retain where required;
- report result/evidence to Privacy.

### Retention evaluation

Through SH-097, this Module returns facts relevant to:
- tax-reportable reward value;
- fraud/points-abuse evidence;
- security/audit requirements;
- legally required fulfillment evidence;
- other approved retention policy.

Privacy records the exemption; Gamification does not.

### Field-level anonymization

Use SH-098 with versioned mappings.

Potential candidates:
- User/profile identifiers in projections that need not be retained;
- free-text `note`/metadata where retention is not required.

Do not anonymize authoritative retained evidence in a way that breaks required relational/legal proof.

### Export contribution

The Module should serialize safe:
- point history;
- challenge participation;
- leaderboard participation where applicable;
- reward redemption history.

Provider-owned tax/notification/payment data is exported by its owner.

---

## 29. Observability

### Structured logging

Every command/event/job includes:
- request/correlation ID;
- Module/operation;
- aggregate IDs;
- event/job ID;
- outcome/reason code;
- retry/attempt state where relevant.

Do not log raw source-event payloads by default.

### Safe metrics

Examples:
- source events received/processed/duplicate/dead-lettered;
- rule evaluation latency;
- point entries appended by type/source (aggregate counts only);
- point-award dedupe rate;
- challenge join/completion counts;
- projection lag/rebuild duration;
- redemption request/deny/conflict counts;
- hold/tax pending counts;
- fulfillment retry/failure counts;
- privacy target success/failure counts.

Avoid User IDs, redemption IDs, or other high-cardinality subject identifiers as metric dimensions.

### Operational failures

Use SH-037 for normalized failures and SH-038 for queue telemetry.

Operational success/failure never substitutes for `PointLedgerEntry` or `RewardRedemption`.

---

## 30. Security Boundaries

1. Validate all command/query payloads server-side.
2. Validate `ruleJson` and `rewardJson` against versioned schemas; never evaluate executable expressions/code.
3. Resolve actor server-side with SH-001.
4. Authorize protected actions with SH-002.
5. Use SH-014 for high-risk actions when root policy requires it.
6. Rate-limit public/self-service challenge and redemption endpoints through root platform controls.
7. Rate limiting does not replace point, challenge, or inventory domain rules.
8. Point spend is protected by database transaction/lock; no in-memory mutex.
9. Limited inventory remains disabled until reservation semantics are approved.
10. Provider secrets never enter Module domain records/logs.
11. Cross-Module payloads are minimized to required facts.
12. `PointLedgerEntry.note` and `metadata` require allowlisted schemas; do not dump arbitrary source payloads.
13. No paid point/reward effect may alter chance-based odds.
14. Unsupported reward effects fail closed.
15. Admin screens must not expose tax/provider sensitive fields beyond public dependency DTOs.
16. All events/jobs carry stable replay protection.
17. No raw Prisma model is exposed as a public contract.

---

## 31. Error / Decision Result Pattern

Public operations return stable Module-level categories. Exact transport mapping follows root standards.

| Category | Meaning | Retry? |
|---|---|---|
| `UNAUTHENTICATED` | no trusted actor | No; authenticate |
| `FORBIDDEN` | actor lacks authority | No |
| `INVALID_INPUT` | malformed payload/config | No until corrected |
| `NOT_FOUND` | target absent or not visible | No |
| `INVALID_STATE` | lifecycle transition/action not allowed | No until state changes |
| `STALE_WRITE` | optimistic concurrency conflict | Re-read/retry explicitly |
| `IDEMPOTENT_REPLAY` | prior identical command/result returned | No additional effect |
| `IDEMPOTENCY_CONFLICT` | key reused for different request | No |
| `SOURCE_EVENT_DUPLICATE` | inbound event already processed | Safe no-op |
| `SOURCE_EVENT_UNSUPPORTED` | event type/version/source contract not approved | Manual/config fix |
| `CONSENT_REQUIRED` | required proof missing/invalid | User remediation |
| `COMPLIANCE_HOLD_BLOCKED` | external hold blocks action | Reevaluate after owner change |
| `TAX_REVIEW_REQUIRED` | external financial/tax gate not satisfied | Reevaluate after owner change |
| `INSUFFICIENT_POINTS` | point sufficiency failed | No until balance changes |
| `REWARD_UNAVAILABLE` | inactive/retired/out-of-window reward | No |
| `INVENTORY_UNAVAILABLE` | approved inventory semantics report no capacity | No until inventory changes |
| `ARCHITECTURE_BLOCKED` | required unresolved contract/ruling not approved | No implementation fallback |
| `UNSUPPORTED_REWARD_EFFECT` | enum type has no approved effect/fulfillment path | No until architecture/support changes |
| `CONFLICT` | database/aggregate concurrency collision | Retry under defined policy |
| `DEPENDENCY_UNAVAILABLE` | canonical owner temporarily unavailable | Usually retryable |
| `RETRY_EXHAUSTED` | durable worker exhausted transient retries | Manual review/incident |
| `MANUAL_REVIEW_REQUIRED` | deterministic policy cannot safely auto-resolve | Review workflow |

Raw provider or database error strings are never public business reason codes.

---

## 32. Testing Architecture

### Domain unit tests

- Program lifecycle and date rules.
- Rule trigger matching and declarative schema validation.
- Rule configuration cannot create chance-based odds.
- Point type/source/delta policy after U-GR-02 approval.
- Balance derivation.
- Adjustment/reversal policy after U-GR-04 approval.
- Challenge lifecycle and participation semantics.
- Leaderboard inclusion/ranking/tie/window logic.
- Reward activation gates by RewardType.
- Reward value snapshot behavior.
- Redemption transition matrix and local gate composition.
- No-pay-to-win safeguards.

### State-transition tests

Every allowed and prohibited Program, Challenge, Reward, RewardRedemption transition.

`ChallengeParticipant` tests enforce only the approved subset.

### Public contract tests

- bounded DTOs;
- stable reason codes;
- event schema versioning;
- no Prisma model leakage;
- external dependency ports accept only minimum facts.

### Database/integration tests

- one source event -> correct ledger effects;
- authoritative write + outbox same transaction;
- composite ChallengeParticipant idempotency;
- Leaderboard unique row behavior;
- RewardRedemption + point spend atomicity;
- value snapshot immutability after Reward edits.

### Authorization tests

- own point/redemption reads;
- admin configuration;
- manual point adjustment;
- redemption review/transition;
- forbidden cross-user access.

### Compliance tests

- required consent version;
- hold blocks applicable action;
- tax-pending cannot fulfill;
- no points/reward effect creates PrizeEntry or odds boost;
- unsupported RewardType cannot silently activate;
- no entitlement-driven odds behavior.

### Idempotency/concurrency tests

- duplicate source event;
- same event handled by two workers;
- repeated command idempotency key;
- conflicting command fingerprint;
- concurrent point-spend redemptions;
- duplicate challenge completion;
- limited inventory after U-GR-08 approval;
- projection rebuild vs incremental update;
- duplicate taxable-value report;
- duplicate fulfillment result.

### Provider adapter tests

Only after a provider is explicitly owned:
- signature verification;
- provider-event dedupe;
- known/unknown mapping;
- out-of-order events;
- reconciliation;
- retry/permanent failure;
- payload isolation.

### Privacy tests

- subject enumeration completeness;
- anonymization field maps;
- retention-required result;
- projection removal/rebuild;
- idempotent privacy instruction replay.

### E2E participation tests

Minimum Module journey:

```text
approved source event
→ point ledger effect
→ balance/leaderboard update
→ eligible Reward
→ atomic redemption
→ hold/tax gates as configured
→ supported fulfillment effect
→ final RewardRedemption state
```

No E2E should directly insert another Module's source truth except controlled fixtures/contracts.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `gamification_rewards` owns deterministic Gamification truth only.
2. Never create or mutate `PrizeEntry`, `PrizeDrawing`, or `PrizeWinning` from Gamification code.
3. Never treat points as sweepstakes tickets or odds weight.
4. Never allow a purchase, subscription, entitlement, or paid reward to improve chance-based odds through this Module.
5. Never let users buy points under the current architecture.
6. `PointLedgerEntry` is point truth.
7. Never create a mutable `pointsBalance` authority.
8. Never update/delete historical point entries to correct ordinary business history.
9. Every earn/spend/reversal/expiration/adjustment must be represented by an append-only ledger effect.
10. Duplicate source delivery must not duplicate a point effect.
11. Never infer another Module's lifecycle fact through direct cross-domain Prisma reads when a public event/query is required.
12. Never trust a client-supplied source event as authoritative.
13. `ruleJson` and `rewardJson` are declarative validated data, never executable code.
14. A rule with unresolved source ownership cannot be production-active.
15. Challenge completion cannot be inferred from leaderboard rank.
16. `LeaderboardEntry` is rebuildable projection, not point truth.
17. Projection failure cannot corrupt or roll back ledger truth.
18. Reward redemption and point spend are atomic.
19. Point sufficiency cannot be check-then-write outside a protected transaction.
20. Limited inventory cannot be production-active until U-GR-08 is resolved and SH-056 integration is tested.
21. Historical `RewardRedemption.valueCents/currency` cannot be rewritten because Reward catalog value changed.
22. External Tax/Hold/Provider Modules cannot set `RewardRedemption.status` directly.
23. `blockedByHoldId` does not transfer Hold ownership.
24. `taxProfileId` does not transfer TaxProfile ownership.
25. `RewardType.cash_bonus` does not authorize a local payment/payout implementation.
26. `RewardType.platform_credit` does not authorize a wallet or local financial ledger.
27. `RewardType.profile_boost` cannot write Search or premium flags directly.
28. Gamification badges must not imply `TrustBadge` verification.
29. Unsupported RewardTypes remain inactive/unfulfillable.
30. Consent proof is queried from Consent & Disclosure; no local acceptance table.
31. ComplianceHold is queried/requested from its owner; no local blocked system.
32. Notification is requested through SH-041; delivery success is not redemption truth.
33. AuditEvent is not point/redemption truth.
34. Operational logs/QueueJob/IntegrationFailure are not point/redemption truth.
35. No Module-local generic idempotency, queue, lock, logger, privacy, or provider infrastructure may be created.
36. No sensitive source/provider payload may be dumped into `metadata`, audit, logs, or events.
37. Privacy requests remain Privacy-owned; this Module only executes its target instructions.
38. Retained tax/fraud evidence must not be erased without an approved Privacy retention decision.
39. Proposed shared operation SH-119 must not be treated as confirmed.
40. Unresolved decisions must fail closed rather than being settled in implementation code.

---

## 34. Prohibited Duplicate Implementations

| Prohibited local implementation | Canonical owner / replacement |
|---|---|
| `gamificationAuth.ts`, `rewardUserResolver.ts`, `currentUser.ts` | SH-001 |
| `rewardPermissions.ts`, `gamificationRoleGuard.ts` | SH-002 |
| `rewardConsentService.ts`, `gamificationTermsRepo.ts`, local Consent table | SH-008/009 |
| `rewardBlocked.ts`, `gamificationHoldService.ts`, local hold flag/table | SH-011/012 |
| local MFA/OTP/step-up flow | SH-014 |
| `rewardTaxCheck.ts`, `reward1099Service.ts`, `taxApproved` | SH-019/118 |
| `gamificationAudit.ts` as audit store | SH-029 |
| `rewardAccessLog.ts` | SH-030 |
| `genericLedger.ts` merging point/payment/order/usage truth | SH-031 mechanism + `PointLedgerEntry` |
| local structured logger/telemetry sanitizer | SH-032/033/034 |
| `GamificationIntegrationFailure`, `GamificationQueueJob` tables | SH-037/038 |
| `rewardEmailService.ts`, `pointsSms.ts`, `gamificationPush.ts` | SH-041 |
| `pointsIdempotency.ts`, local idempotency table | SH-044 |
| `ProcessedGamificationEvent` / `rewardEventDedupe.ts` | SH-045 |
| `gamificationPublisher.ts`, private outbox/event bus | SH-046 |
| `gamificationQueue.ts`, custom retry loop | SH-047/048 |
| in-memory points/reward mutex | SH-051 |
| custom stale-write helper | SH-052 |
| generic lifecycle table that owns statuses | SH-053 + local transition policy |
| reward inventory check-then-decrement helper | SH-056 |
| `pointsBalance` mutable source table/column | SH-115 projection |
| `cl10PrivacyService.ts` owning requests/jobs | SH-095–098 |
| `annualReward1099Summary` or local tax filing table | SH-118 + Payment/Tax |
| `profileBoost=true`, `premiumReward=true`, local entitlement table | SH-119 once approved |
| direct Typesense/Search client for reward boost | affected owner/Search contract after SH-119 |
| local Stripe/tax/notification provider adapter | canonical provider-owning Modules |
| `PrizeEntry` creation from point/reward code | Sweepstakes / Prize interface only after explicit approved bridge |
| generic fraud/risk platform with no owner | unresolved U-GR-12; use local validation + SH-012 escalation |

---

## 35. Unresolved Decisions

### U-GR-01 — Point account scope

Does one point balance belong to:
- User globally;
- User + Program;
- User + ProfessionalProfile;
- another explicit account key?

**Evidence:** `userId` is required across ledger/redemption/leaderboard, while `programId` and `professionalProfileId` are optional/contextual. This strongly suggests User-centered accounting but does not conclusively define spend scope.

**Blocks:** final balance query semantics, point-spend lock key, cross-program redemption.

### U-GR-02 — Point signed-delta convention

What exact sign combinations are valid for `earned`, `spent`, `reversed`, `expired`, and `adjusted`?

**Blocks:** point ledger implementation tests and balance math.

### U-GR-03 — Historical rule/causation proof

How is the exact applied Rule semantic identity/version preserved for an award when `GamificationRule` can change and `PointLedgerEntry` has no `ruleId`/`sourceEventId` fields?

**Constraint:** use SH-045/044 for dedupe; do not invent a local processed-event table.

### U-GR-04 — Reversal linkage

Should a reversed PointLedgerEntry explicitly reference the original entry, and how is double reversal prevented?

**Blocks:** production reversal semantics beyond conservative audited adjustments.

### U-GR-05 — Point expiration

Do points expire? If yes:
- what earns an expiration date;
- FIFO/lot semantics;
- partial spend allocation;
- reversal after expiration;
- worker schedule and proof?

**Blocks:** point-expiration worker.

### U-GR-06 — ChallengeParticipant status vocabulary

Maps to U-CL10-04. Decide whether participant state receives its own enum or intentionally reuses a constrained subset of `ChallengeStatus`.

### U-GR-07 — Challenge progress and `rewardJson`

Is challenge progress binary/event-completion only, or does it require persistent progress/evidence? Does `rewardJson` contain only deterministic point/rule references, or may it define Reward-like benefit truth?

**Blocks:** advanced progress and non-point challenge reward behavior.

### U-GR-08 — Reward inventory semantics

Maps to U-CL10-03. Define whether `Reward.inventory` is cap, remaining stock, or another value and what reservation/release proof exists.

**Blocks:** limited-inventory production activation.

### U-GR-09 — Reward effect/fulfillment contracts

Maps to U-CL10-05. Define authoritative effect path for each `RewardType`.

**Blocks:** activation/final fulfillment of unsupported types.

### U-GR-10 — Temporary benefit grant ownership

Maps to U-CL10-06 / SH-119. Determine owner for `profile_boost` and other deterministic time-bound benefits.

### U-GR-11 — Direct Track entitlement dependency

Maps to U-CL10-07. Which ordinary Gamification actions, if any, are plan-gated?

**Current rule:** do not add SH-005 baseline dependency or premium flags.

### U-GR-12 — Shared fraud/risk capability

Maps to U-CL10-08. No confirmed generic fraud owner/decision record exists.

**Current rule:** owner-local deterministic validation may request SH-012 hold/manual review; do not invent platform fraud truth.

### U-GR-13 — `delivery_on_time` source owner

Maps to U-CL10-10. Identify authoritative owner/event before activating that trigger.

### U-GR-14 — Redemption consent proof linkage

Should `RewardRedemption` snapshot accepted terms version and/or Consent proof ID, or is runtime proof + audit reference sufficient?

**Constraint:** ConsentLog remains externally owned.

### U-GR-15 — Reward taxable-value recognition moment

At which owner event is value reportable: redemption request, approval, fulfillment, actual receipt, or another approved point?

Payment / Payout / Tax must confirm the contract before SH-118 production behavior is enabled.

### U-GR-16 — Blocked/cancelled/reversed compensation

Define:
- path after ComplianceHold release;
- cancellation after point spend;
- inventory release;
- restoring points;
- reversal of supported downstream effects;
- terminal-state correction.

### U-GR-17 — Fulfillment-attempt proof

For provider/manual reward fulfillment, what record preserves attempts, provider refs, idempotency, failure, and reconciliation evidence?

**Do not invent** a model until U-GR-09 settles ownership/provider design.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. `gamification_rewards` owns Programs, Rules, PointLedgerEntry, Challenges, Leaderboards, Rewards, and RewardRedemption.
2. It does not own Sweepstakes / Prize truth.
3. `PointLedgerEntry` is append-only point truth; balance is derived.
4. `LeaderboardEntry` is a rebuildable Gamification projection.
5. Source Modules own source lifecycle facts; Gamification consumes versioned events/public contracts.
6. Rule evaluation and point decisions are Gamification policy.
7. Every point mutation is ledgered; users do not buy points under the current architecture.
8. Reward redemption state remains Gamification truth even when Tax/Holds/providers participate.
9. Consent, Hold, Tax, Notification, Audit, Privacy, Search, Track, and generic infrastructure remain externally owned.
10. Point spend + redemption creation must be atomic.
11. Paid rewards/points/entitlements cannot improve sweepstakes odds.
12. Unsupported reward effects fail closed.
13. Cross-Module Prisma reads are not the default integration contract.
14. Shared mechanisms are reused by SH-### ID and never absorb Module truth.

### Inherited Proposed Rulings

- PR-CL10-03: `ruleJson` is declarative, schema-validated, versioned configuration.
- PR-CL10-04: Program/Challenge transition graph described above.
- PR-CL10-05: explicit RewardRedemption transition matrix; no fulfillment from pending-tax/blocked; correction through reversal/compensation.
- PR-CL10-09: high-risk Gamification admin actions are candidates for central step-up.
- SH-119 remains proposed, not approved.

### Implementation blockers

Production code must not silently resolve U-GR-01 through U-GR-17. Features may proceed around non-applicable blockers, but any feature whose core behavior depends on one must resolve/update architecture first.

---

## 37. Coding-Agent Usage

Before implementing this Module, the coding agent must read, in order:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md`;
5. `context/clusters/incentives-rewards-prize-economy/architecture.md`;
6. `context/clusters/incentives-rewards-prize-economy/build-plan.md`;
7. this `gamification_rewards/module-architecture.md`;
8. this `gamification_rewards/implementation-plan.md`;
9. public-interface sections for direct dependencies, especially:
   - Identity & Access;
   - Role / Authority;
   - Consent & Disclosure;
   - Transaction / Order;
   - Review / Dispute;
   - Professional Eligibility;
   - Payment / Payout / Tax;
   - Admin Review / Compliance Hold;
   - Notification;
   - Audit / Event Ledger;
   - Observability / Ops;
   - Privacy / Data Erasure;
   - Track Subscription & Entitlement and Search only when an approved reward effect requires them;
10. the current progress tracker;
11. current Prisma schema and migrations.

If a dependency context file is unavailable, the agent may use a typed contract fake for tests only when the Cluster build plan permits it. Production integration must target the canonical owner contract.

If repository code differs from this architecture:

- do not create a second pattern;
- identify the conflict;
- preserve source-of-truth ownership;
- prefer canonical Shared Operations/public interfaces;
- update architecture before making a binding new decision;
- never let implementation progress silently settle a Proposed Ruling or Unresolved Decision.
