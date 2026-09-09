# Incentives, Rewards & Prize Economy Build Plan

> **Cluster ID:** `CL-10`  
> **Cluster:** Incentives, Rewards & Prize Economy  
> **Repository target:** `context/clusters/incentives-rewards-prize-economy/build-plan.md`  
> **Companion:** this Cluster `architecture.md`, target Module architecture/implementation plans, root Workin Ants context, Canonical Shared Operations Registry  
> **Implementation posture:** Greenfield/MVP planning against the current Prisma and architecture evidence; legal-gated production behavior remains disabled until its named architecture/legal gates are resolved.

---

## Core Principle

Build CL-10 as a sequence of **vertical, testable owner slices**, not as one rewards engine and not as two isolated Module silos.

Each slice should prove real behavior through the owner’s domain/application service and source-of-truth records:

```text
usable / observable behavior
→ owning Module application service
→ authoritative database state
→ stable public contract
→ authorization / consent / compliance gates
→ events / jobs / downstream integrations
→ deterministic tests and workflow verification
→ explicit exit gate
```

A Cluster phase may involve one Module or a narrow collaboration between Modules and neighboring Clusters. That collaboration never transfers source-of-truth ownership.

Draft/configuration capabilities may be built before legal review. **Production activation, chance-based entry, winner selection, tax-sensitive fulfillment, and unsupported reward effects must not be made operational by guessing through unresolved architecture.**

---

## Build Rules

1. Follow the root `architecture.md`, `code-standards.md`, Canonical Shared Operations Registry, and this Cluster architecture.
2. Do not expand CL-10 into payments, subscriptions, tax filing, search, notification delivery, privacy orchestration, or a general fraud platform.
3. Do not redesign Module ownership for implementation convenience.
4. Reuse canonical SH-### operations. If a required shared operation is not implemented yet, implement/fix it in its canonical owner or coordinate that prerequisite; do not create a CL-10 copy.
5. Every mutation validates input, resolves the actor where required, authorizes the action server-side, and enforces owner invariants.
6. Every cross-Module dependency uses a public interface or versioned event. Direct cross-domain Prisma repository access is not the default.
7. Every asynchronous side effect is idempotent, retryable where safe, and observable.
8. Every lifecycle transition is performed by the owning Module’s transition service; downstream Modules/providers return evidence or decisions only.
9. `PointLedgerEntry` remains append-only point truth. No mutable point-balance authority may be introduced.
10. `PrizeEntry` remains separate from point/order/payment records. `PrizeWinning` remains separate from RewardRedemption.
11. A purchase-triggered sweepstakes path must never cause Sweepstakes to own Stripe webhook processing.
12. No reward, subscription, entitlement, or payment may create better chance-based odds without an explicit approved legal/architecture decision.
13. Unsupported `RewardType` effects remain inactive rather than receiving invented fulfillment logic.
14. Provider integrations are isolated behind the explicit provider owner’s adapter. Provider payloads never become CL-10 domain types.
15. Every phase ends with tests, workflow verification, documentation updates, and an exit gate.
16. Do not start the next numbered feature until the previous feature’s exit gate passes, except for independent owner/platform work explicitly identified as a parallel prerequisite.
17. Unresolved architecture is not silently settled in code. Resolve the decision, update architecture, then implement.
18. Legal-gated configurations must fail closed: draft/paused is acceptable; unsafe active production behavior is not.
19. Audit evidence and operational telemetry are both required where applicable, but neither may replace domain truth.
20. Schema migrations must preserve source-of-truth ownership and include rollback/destructive-change analysis.

---

## Dependencies and Preconditions

### Root/platform prerequisites

CL-10 consumes these platform capabilities and must not rebuild them:

- authenticated actor context — SH-001;
- authorization — SH-002;
- versioned Consent proof/version resolution — SH-008/009;
- ComplianceHold query/request — SH-011/012;
- step-up authentication for actions classified sensitive — SH-014;
- Payment/Tax financial readiness — SH-019;
- generic audit/sensitive-access proof — SH-029/030;
- append-only domain-ledger mechanics — SH-031;
- request context, logging, redaction, integration/queue telemetry — SH-032/033/034/037/038;
- Notification request contract — SH-041;
- idempotent commands/event dedupe/transactional outbox — SH-044/045/046;
- durable jobs/retries — SH-047/048;
- database locking/lifecycle transition/atomic reservation — SH-051/053/056;
- Privacy owner protocol — SH-095 through SH-098;
- aggregate projection — SH-115;
- secure random selection — SH-116;
- yearly reportable-value aggregation and Tax handoff — SH-117/118.

If these operations are not yet implemented, CL-10 features may use contract fakes in tests, but production code must depend on the canonical interfaces rather than local substitutes.

### Upstream/neighbor prerequisites

- **Identity & Access / Role & Authority:** actor and permission decisions.
- **Consent & Disclosure:** active terms/rules version and acceptance proof.
- **Transaction / Order:** authoritative order-completed and qualifying purchase outcome events.
- **Review / Dispute:** authoritative high-rating event if the corresponding Gamification rule is enabled.
- **Professional Eligibility:** profile-completed event/context if that trigger is enabled.
- **Payment / Payout / Tax:** tax readiness, value-reporting contract, Stripe webhook ownership.
- **Admin Review / Compliance Hold:** hold query/request/release truth.
- **Notification:** communication request contract.
- **Privacy / Data Erasure:** owner executor protocol.
- **Track Subscription & Entitlement / Search:** only for reward effects that explicitly require them after the relevant architecture ruling.

### Existing source-of-truth records

The current Prisma evidence already defines CL-10’s core records and enums. Before implementation, verify that migrations actually create the current schema and that no later migration changed meanings.

Do not recreate tables simply because the feature begins in this plan.

### Providers that may be stubbed initially

- Tax readiness/value-reporting may use a Payment/Tax contract fake until that Module is production-ready.
- Notification may use a contract fake for workflow tests.
- Reward/prize fulfillment providers are **not selected** and must not be invented. Unsupported provider-dependent reward types remain inactive.
- Secure random selection uses the approved CSPRNG primitive; it is not an external provider dependency.

#### Dependencies that should not block early vertical slices

The following do not block Features 01–03:

- live Stripe webhook traffic;
- live tax provider;
- external reward fulfillment provider;
- Search/profile-boost integration;
- production sweepstakes legal approval.

Features can prove owner behavior with versioned contract fixtures while preserving the final interfaces.

### Architecture blockers that must be resolved at the named feature

- **U-CL10-01:** immutable official-rules evidence — before production drawing activation in Feature 06.
- **U-CL10-02:** immutable drawing-run proof schema — before Feature 08 can run a production drawing.
- **U-CL10-03:** reward inventory semantics — before limited-inventory rewards can be activated in Feature 04.
- **U-CL10-05/06:** specific reward effect/fulfillment and SH-119 ownership — before those reward types are activated in Feature 05.
- **U-CL10-11/12:** redraw and jurisdiction/legal policy — before those behaviors are offered.

---

## Phase 1 — Deterministic Engagement Foundation

Build deterministic gamification first because it can deliver value without introducing chance-based prize risk and because later reward behavior depends on trustworthy point truth.

### 01 Gamification Programs, Rules, and Disclosure Configuration

Create the owner-controlled configuration surface for deterministic gamification without yet awarding points.

#### Objective

An authorized administrator can create and manage `GamificationProgram` and `GamificationRule` records, bind them to versioned terms/disclosure context, validate deterministic rule configuration, and activate only configurations that satisfy owner policy.

#### User-visible / Observable Result

- Admin can create a draft gamification program.
- Admin can configure supported rule triggers and deterministic point values.
- Admin can see validation failures before activation.
- Program/rule queries expose status and terms version without exposing Consent internals.
- A consuming developer can exercise the public contract and receive stable DTOs/denial reasons.

#### Owning Module(s)

- **Business truth:** Gamification / Rewards.
- Consent & Disclosure owns terms-version catalog and acceptance proof.
- Role / Authority owns permission interpretation.

#### Dependencies

- Current Prisma models/enums for `GamificationProgram`, `GamificationRule`, `GamificationProgramStatus`, `GamificationRuleTrigger`.
- SH-001, SH-002, SH-008/009, SH-029, SH-044, SH-046.
- Root validation/error conventions.
- PR-CL10-03 from architecture: `ruleJson` is declarative, versioned, schema-validated configuration, never executable code.

#### Shared Operations Used

- **SH-001 — resolveAuthenticatedActor**; Identity & Access. Resolve admin actor. Local policy: which gamification actions need a user/system actor. Do not rebuild session helpers.
- **SH-002 — authorizeResourceAction**; Role / Authority. Authorize program/rule administration. Local policy: action names and target facts. Do not build a gamification role engine.
- **SH-009 — resolveActiveConsentVersion**; Consent & Disclosure. Resolve applicable gamification terms/disclosure version. Local policy: which consent type applies. Do not build a local version catalog.
- **SH-008 — queryConsentProof**; Consent & Disclosure. Used in test/preview paths that verify user acceptance requirements. Local policy: whether an action requires proof. Do not duplicate ConsentLog.
- **SH-029 — appendAuditEvent**; Audit / Event Ledger. Audit activation/retirement/material rule changes. Local policy: safe action metadata. Do not create `gamificationAudit` storage.
- **SH-044 — executeIdempotentCommand**; platform primitive. Protect create/activation retries. Local policy: semantic command key. Do not create a feature idempotency table.
- **SH-046 — publishDomainEvent**; transactional outbox. Publish program lifecycle events. Local policy: event vocabulary/payload. Do not build a private event bus.

#### Data / Schema

Primary records:

- `GamificationProgram`
- `GamificationRule`

No new balance, ledger, subscription, consent, or audit table is allowed.

`ruleJson` validation must use a typed/versioned schema at the application boundary. The schema version may live inside the JSON payload if no Prisma migration is required; the exact JSON contract belongs in the Module architecture/specification.

#### Public Interfaces

Introduce/complete:

- `configureGamificationProgram`
- `configureGamificationRule`
- `activateGamificationProgram`
- `pauseGamificationProgram`
- `endGamificationProgram`
- `getGamificationProgram`
- `listGamificationRules`

Names may follow repository conventions, but semantics must preserve owner boundaries.

#### Logic

- Validate name, timing, status, points, trigger, and rule payload.
- Reject negative/zero/otherwise invalid point semantics where the target rule does not permit them.
- Reject arbitrary code/functions/expressions in `ruleJson`.
- Require exact terms version when owner policy requires disclosure.
- Enforce proposed lifecycle transitions from architecture.
- Keep rule activation separate from source-event availability: a rule whose source contract is unresolved (`delivery_on_time`) must not activate in production.
- Do not add points yet; this feature configures rules only.

#### UI / Administrative Surface

Minimum admin rewards dashboard slice:

- program list/status;
- create/edit draft program;
- rule list/editor;
- trigger selector from enum;
- points value;
- terms version display/reference;
- validation/activation errors;
- pause/end controls with confirmation.

No full consumer rewards portal is required in this feature.

#### Authorization / Compliance

- Protected admin configuration uses SH-002.
- Gamification reward disclosure version is explicit.
- No rule may purchase or award chance-based odds.
- A rule cannot be configured to mutate `PrizeEntry.weight`, `entriesAwarded`, or entitlement odds.
- Unsupported source triggers fail activation rather than falling back to cross-domain database reads.

#### Events / Jobs / Integrations

- Outbox events for program activation/pause/end and material rule activation/deactivation.
- No background worker is required yet except outbox dispatch.
- Consent is queried through its public interface only.

#### Failure Behavior

- Invalid rule payload → validation denial, no write.
- Unauthorized actor → denial, no write.
- Consent version unavailable → program may remain draft; activation denied if required.
- Outbox dispatch failure after transaction → authoritative program state remains committed; canonical dispatcher retries.
- Unknown trigger/source contract → rule remains inactive with explicit reason.

#### Tests

- Unit: lifecycle transitions, rule payload schema, trigger validation, no-paid-odds invariant.
- Integration: admin mutation + Prisma transaction + audit/outbox.
- Contract: Consent version/proof DTO boundaries.
- Authorization: unauthorized admin actions denied.
- Regression: rule configuration cannot address Sweepstakes-owned fields/contracts.

#### Out of Scope

- awarding points;
- challenge progress;
- leaderboards;
- rewards/redemptions;
- sweepstakes;
- tax fulfillment;
- provider integrations.

#### Exit Gate

Feature 01 is complete only when:

- a clean seeded database can create/read/update a draft program and rules through owner services;
- allowed program transitions are enforced by tests rather than UI convention;
- malformed/unversioned executable-style `ruleJson` is rejected;
- terms version is resolved through Consent-owned interface, not a local catalog;
- an unsupported source trigger cannot be activated silently;
- program activation emits one transactional owner event and one retry-safe audit record;
- typecheck, lint, unit/integration tests, and relevant build checks pass;
- no prize, tax, subscription, auth, consent, or audit truth has been copied into Gamification.

---

### 02 Source Events to Append-Only Point Ledger

Turn authoritative platform activity into exactly-once deterministic point truth.

#### Objective

Gamification can consume approved source Module events, evaluate active rules, append `PointLedgerEntry` records exactly once per business rule semantics, support audited manual adjustments/reversals, and expose ledger/balance queries without creating mutable balance truth.

#### User-visible / Observable Result

- A fixture/real `order_completed` event produces the expected point entry.
- Duplicate delivery of the same event produces no duplicate award.
- Admin can add an authorized adjustment/reversal without editing history.
- User/admin can query point ledger and a derived balance.
- The source event and applied rule can be traced through safe correlation metadata.

#### Owning Module(s)

- **Point decision and PointLedgerEntry:** Gamification / Rewards.
- Source lifecycle facts remain with Transaction / Order, Review / Dispute, Professional Eligibility, or another explicit source owner.

#### Dependencies

- Feature 01.
- `PointLedgerEntry`, `PointLedgerEntryType`, `PointLedgerEntrySource`.
- At least one approved source contract; `order_completed` is the preferred first slice because its source owner is clear.
- SH-031, SH-044, SH-045, SH-046, SH-014, SH-029, SH-032/033/034.

#### Shared Operations Used

- **SH-045 — deduplicateDomainEvent**; platform event infrastructure. Prevent repeat source delivery. Local policy: once per source event + rule/program semantics. Do not create `processedGamificationEvent`.
- **SH-044 — executeIdempotentCommand**; platform primitive. Protect application command retries. Local policy: semantic key. Do not build `pointsIdempotency.ts`.
- **SH-031 — appendDomainLifecycleEvent**; shared append mechanism. Append PointLedgerEntry transactionally. Local policy: point type/source/sign/reversal semantics. Do not merge ledgers.
- **SH-046 — publishDomainEvent**; outbox. Emit point-ledgered effects. Local policy: event payload. Do not build a custom publisher.
- **SH-014 — requireStepUpForSensitiveAction**; Identity & Access where root policy classifies manual value adjustment as sensitive. Do not build local MFA.
- **SH-029 — appendAuditEvent**; audit manual adjustments/reversals and material system corrections. Do not use audit as point truth.
- **SH-032/033/034**; request context/logging/redaction. Preserve traceability without leaking source payloads.

#### Data / Schema

Primary write:

- `PointLedgerEntry`

No `points_balance` source table/column is introduced.

Current schema does not contain explicit `sourceEventId` or a reversal-link column. Event dedupe must therefore use canonical SH-045/044 infrastructure plus safe source/rule references in existing metadata where appropriate. Do not create a local processed-event table merely to compensate.

#### Public Interfaces

- `recordEligibleActivity`
- `appendManualPointAdjustment`
- `getPointLedger`
- `getPointBalance`

Source event contracts must be versioned and owner-defined.

#### Logic

- Consume only authoritative owner events.
- Select active programs/rules applicable at event occurrence time.
- Validate subject identity/profile context.
- Define deterministic rule application count: one event may apply multiple distinct active rules, but the same event/rule effect may not apply twice.
- Append positive/negative values only under legal type/source combinations.
- Reversal/adjustment creates new entries.
- Derive balance from ledger aggregate initially; a cached projection may be introduced in Feature 03 through SH-115 without becoming truth.
- Do not award points for `delivery_on_time` until U-CL10-10 identifies source ownership.

#### UI / Administrative Surface

- Read-only point ledger viewer for user/admin context where product UI exists.
- Admin manual adjustment/reversal form with reason and confirmation.
- Derived balance display labeled as current/as-of projection/query result.

#### Authorization / Compliance

- User can only see permitted own data unless Role / Authority grants broader scope.
- Manual adjustments require explicit authority and audit; step-up if classified by security policy.
- No point award may implicitly grant a PrizeEntry.
- No user-purchased points mechanism is introduced.

#### Events / Jobs / Integrations

- Inbound source events through canonical event infrastructure.
- Outbound point-ledgered event through SH-046.
- Worker can be queue-backed if event dispatch is asynchronous; use SH-047/048 if so.
- No provider adapter.

#### Failure Behavior

- Duplicate event → safe no-op with prior effect reference.
- Source event missing required fields/version → reject/dead-letter with operational failure, no point write.
- Rule changed after source occurrence → use the effective rule semantics defined by Module policy; do not retroactively rewrite prior entries.
- Transaction failure → no partial point/outbox write.
- Audit failure handling follows canonical transaction/operational policy but cannot be “fixed” by altering ledger truth.

#### Tests

- Unit: rule matching, point sign/type/source, reversal math, balance derivation.
- Contract: versioned source event shape.
- Integration: one source event → one-per-rule ledger effect + outbox.
- Idempotency: duplicate same event, replay after crash, same event across two workers.
- Concurrency: concurrent consumers do not double award.
- Authorization: admin adjustments and user reads.
- Compliance: point path cannot create/increase PrizeEntry odds.

#### Out of Scope

- Challenge lifecycle/progress beyond source-event plumbing.
- Reward redemption.
- Sweepstake entries.
- Tax reporting.

#### Exit Gate

- `order_completed` or another approved owner event creates the correct append-only point entry.
- Delivering it 2+ times creates exactly one effect per applicable rule.
- No direct cross-domain Prisma read is required.
- Manual correction creates reversal/adjustment entries; historical point rows remain unchanged.
- Balance query exactly matches ledger aggregation across fixture histories.
- Unauthorized adjustment is denied and audited appropriately.
- Point award cannot mutate Sweepstakes records or entitlement odds.
- failure/retry paths are observable and tests pass.

---

### 03 Challenges, Balance Projection, and Leaderboards

Build the deterministic engagement read models and challenge loop on top of trusted point truth.

#### Objective

Users can join approved challenges, owner events can complete challenge participation under explicit rules, and Gamification can rebuild point-balance/leaderboard projections from authoritative records.

#### User-visible / Observable Result

- An active challenge accepts a permitted participant.
- Completion produces the configured owner effect/point rule exactly once.
- A leaderboard displays ranked users from approved metrics.
- Projection rebuild produces the same result as incremental updates.
- Admin can see projection lag/rebuild status without treating it as domain truth.

#### Owning Module(s)

- Gamification / Rewards owns Challenge, ChallengeParticipant, Leaderboard, LeaderboardEntry, and projection policy.
- Source events used to prove challenge progress remain with their source Modules.

#### Dependencies

- Features 01–02.
- SH-044/045/046/047/048/115.
- U-CL10-04 participant status issue must be handled by the architecture’s conservative service constraint unless a dedicated enum ruling is approved.

#### Shared Operations Used

- **SH-115 — buildAggregateProjection**; projection owner Gamification. Build/rebuild balances/leaderboards. Local policy: included ledger entries, ranking/ties/window. Do not create projection as truth.
- **SH-045/044**; dedupe progress/source effects and commands. Local policy: completion uniqueness.
- **SH-046**; publish challenge/projection owner events where useful.
- **SH-047/048**; durable rebuild/evaluation jobs. Local policy: scheduling/retry safety. Do not create a private worker framework.

#### Data / Schema

- `Challenge`
- `ChallengeParticipant`
- `Leaderboard`
- `LeaderboardEntry`
- `PointLedgerEntry` read source

No new point source-of-truth table.

Until U-CL10-04 is resolved, service-layer participant states must use only the approved conservative subset and reject values that have no defined participant meaning. Do not add a new enum migration silently.

#### Public Interfaces

- `joinChallenge`
- `getChallenge` / `listChallenges`
- owner-internal `applyChallengeProgress` or equivalent event consumer
- `getPointBalance`
- `getLeaderboard`
- admin `rebuildGamificationProjection`

#### Logic

- Challenge must be active and within its configured timing.
- Joining is idempotent by `(challengeId,userId)`.
- Completion is owner-controlled and recorded once.
- Challenge completion may trigger deterministic points through the same Feature 02 rule pipeline.
- Leaderboard source policy must be explicit: ledger points or another approved metric, never arbitrary frontend counts.
- Tie behavior and ranking window belong to Gamification and must be deterministic.
- Projection checkpoints/versioning follow SH-115.

#### UI / Administrative Surface

Where CL-10 user UI is in MVP:

- challenge list/detail/join status;
- point balance;
- point history link;
- leaderboard view.

Admin/developer surface:

- projection version/checkpoint;
- rebuild command;
- lag/error state.

If user UI is not in the current product surface, public queries plus admin/test observable output satisfy this feature.

#### Authorization / Compliance

- Participant actions use actor/authorization context established in earlier features.
- A leaderboard must expose only fields allowed for that public/user context.
- No leaderboard ranking may be repurposed into sweepstakes odds without explicit legal/architecture approval.

#### Events / Jobs / Integrations

- Projection rebuild worker through SH-047/048.
- Challenge completion events may feed Feature 02 rules.
- Optional notification request for challenge completion uses SH-041 only if notification UX is approved; not required for exit.

#### Failure Behavior

- Duplicate join → return existing participation, no duplicate record.
- Duplicate completion event → one completion/point effect.
- Projection update failure → source truth remains correct; lag is observable and full rebuild repairs it.
- Invalid participant status transition → reject; no fallback to raw enum assignment.

#### Tests

- Unit: challenge lifecycle, participation constraints, ranking/tie rules.
- Integration: join/complete/award flow.
- Projection: incremental vs full rebuild equivalence.
- Idempotency: duplicate join/completion.
- Privacy/authz: leaderboard field exposure and own-participant access.
- Regression: projection loss/rebuild does not lose point truth.

#### Out of Scope

- reward catalog/redemption;
- prize drawings;
- subscription boosts;
- cross-platform search ranking.

#### Exit Gate

- Challenge join and completion are owner-validated and idempotent.
- Unsupported `ChallengeParticipant.status` values cannot be written through normal services.
- Leaderboard and balance can be fully rebuilt from authoritative records.
- Rebuild output matches incremental output for deterministic fixtures.
- Projection outage does not block or corrupt PointLedgerEntry truth.
- No Search index or sweepstakes odds are modified.
- tests and standard build checks pass.

---

## Phase 2 — Deterministic Reward Economy

Build redemption only after point truth, concurrency, and projection behavior are proven.

### 04 Reward Catalog and Atomic Redemption Core

Create the deterministic reward catalog and a safe redemption transaction without inventing unsupported fulfillment effects.

#### Objective

Admins can configure Reward records, users can request eligible redemptions, and point spending plus RewardRedemption creation occurs atomically with idempotency and hold/terms gates.

#### User-visible / Observable Result

- Admin can create draft/active/paused/retired rewards subject to activation rules.
- User can request an eligible redemption and receive a persisted redemption status/next action.
- Required point cost is consumed exactly once through PointLedgerEntry.
- Concurrent redemption cannot overspend the same points.
- Unsupported/limited-inventory reward configuration fails closed rather than inventing behavior.

#### Owning Module(s)

- Gamification / Rewards owns Reward and RewardRedemption lifecycle, point-spend policy, reward value snapshot, and activation eligibility.
- Consent owns proof; Hold owner owns hold state.

#### Dependencies

- Features 01–03.
- `Reward`, `RewardStatus`, `RewardType`, `RewardRedemption`, `RewardRedemptionStatus`.
- SH-001/002/008/009/011/044/056/031/046/029.
- U-CL10-03 for limited-inventory activation.
- U-CL10-05 for final effect/fulfillment, but redemption core may be built with unsupported finalization disabled.

#### Shared Operations Used

- **SH-008/009**; resolve/check reward terms proof. Local policy: which reward/version must be accepted. Do not copy ConsentLog.
- **SH-011**; active hold gate. Local policy: which hold reasons block request/approval. Do not create local blocked truth.
- **SH-044**; idempotent redemption request. Local key: actor + reward + request semantic identity.
- **SH-056**; atomic reservation for point sufficiency and, once defined, limited inventory. Local policy: point cost/inventory semantics. Do not check balance then write outside transaction.
- **SH-031**; append point-spend ledger entry. Local policy: `spent`/`reward_redemption` semantics.
- **SH-046**; redemption-request/status events.
- **SH-029**; audit admin reward activation and exceptional redemption adjustments.
- SH-001/002 from prior features continue to gate actor/action.

#### Data / Schema

Writes:

- `Reward`
- `RewardRedemption`
- `PointLedgerEntry`

The redemption snapshots `valueCents`/`currency` where applicable; subsequent Reward edits must not rewrite historical redemption value.

**Inventory:** until U-CL10-03 is resolved, a reward with finite `inventory` must not be activated for production redemption unless the approved concurrency semantics are implemented. Do not silently interpret the field as “remaining stock.”

#### Public Interfaces

- `configureReward`
- `activateReward` / `pauseReward` / `retireReward`
- `listRewards` / `getReward`
- `requestRewardRedemption`
- `getRewardRedemption` / `listRewardRedemptions`

#### Logic

- Reward must be active and program context valid.
- Terms proof must match configured version when required.
- Apply point cost only if configured; zero-point rewards still require explicit eligibility policy.
- Point sufficiency is derived from ledger within an atomic reservation/transaction.
- Create RewardRedemption and point-spend entry atomically.
- On transaction failure, neither persists.
- Assign initial redemption state according to owner policy (`pending_confirmation` or `pending_tax` only after later tax classification; do not infer TaxProfile provider status here).
- Reward type must have an approved path before activation/final fulfillment.

#### UI / Administrative Surface

Admin rewards dashboard:

- reward catalog;
- type/status/value/point cost/inventory/terms version;
- activation validation;
- redemption queue/detail.

User-facing where applicable:

- available rewards;
- point cost/current balance;
- request confirmation;
- redemption status/next action.

#### Authorization / Compliance

- User may redeem only for the permitted subject context.
- Admin exceptional actions require Role / Authority and audit.
- No reward may increase sweepstakes odds.
- `RewardType.profile_boost` cannot be activated as a local boolean.
- `cash_bonus` cannot be treated as completed payment by Gamification.
- `platform_credit` cannot invent a local money/credit ledger.

#### Events / Jobs / Integrations

- Outbox `redemption requested`/status events.
- No provider fulfillment required in this feature.
- Optional Notification request may be added after commit, but delivery is not exit-critical.

#### Failure Behavior

- Insufficient points → denial, no redemption/spend.
- Duplicate request → same existing result/no double spend.
- Concurrent requests → only transactionally permitted redemption(s) win.
- Active hold → denial or owner `blocked` path according to transition policy; preserve hold ID, no local hold creation.
- Unsupported reward type/effect → cannot activate/fulfill; explicit configuration error.
- Limited inventory with unresolved semantics → production activation denied.

#### Tests

- Unit: reward lifecycle/activation, point-cost rules, redemption transitions.
- Integration: redemption + point spend one transaction.
- Concurrency: two requests against same point balance.
- Idempotency: repeated request key.
- Consent/hold contract tests.
- Compliance: profile boost/cash/platform credit cannot bypass owner contracts; no prize odds effect.

#### Out of Scope

- tax reporting/provider fulfillment;
- profile/search boost effect;
- cash transfer;
- platform-credit ledger;
- sweepstakes entry conversion.

#### Exit Gate

- Supported reward configuration can be activated; unsupported types fail closed.
- One redemption request creates one RewardRedemption and exactly one matching point-spend entry when required.
- Concurrent requests cannot overspend points.
- Duplicate request cannot spend twice.
- historical redemption value is stable after Reward catalog edits.
- limited-inventory rewards remain non-production until U-CL10-03 is resolved and tested.
- no payment, tax, entitlement, search, or prize truth has been copied into Gamification.

---

### 05 Reward Tax, Hold, Fulfillment, and Deterministic Benefit Bridges

Connect RewardRedemption to the owner Modules that supply tax, hold, financial, entitlement, or provider effects while keeping redemption truth in Gamification.

#### Objective

A RewardRedemption can move safely from pending state through tax/hold evaluation to an approved supported fulfillment effect and final Gamification status, with unsupported reward types explicitly gated.

#### User-visible / Observable Result

- A tax-sensitive redemption visibly waits in `pending_tax`/blocked state until Payment/Tax readiness is satisfied.
- A ComplianceHold prevents prohibited fulfillment.
- Recognized reward value is reported once to Payment/Tax.
- Supported fulfillment/effect result returns to Gamification and owner status changes once.
- Notification communicates status without becoming truth.
- Unsupported effect types remain unfulfillable with an explicit reason.

#### Owning Module(s)

- **RewardRedemption lifecycle/value snapshot:** Gamification / Rewards.
- **Tax readiness/reporting:** Payment / Payout / Tax.
- **ComplianceHold lifecycle:** Admin Review / Compliance Hold.
- **Notification delivery:** Notification.
- **Temporary benefit grant:** unresolved under SH-119.
- Any fulfillment provider is owned only after explicit architecture assignment.

#### Dependencies

- Feature 04.
- SH-019, SH-011/012, SH-118, SH-041, SH-047/048, SH-037, SH-029/030.
- SH-119 only if its ownership is approved.
- U-CL10-05/06 must be resolved before affected reward types are activated.

#### Shared Operations Used

- **SH-019 — evaluateFinancialReadiness**; Payment/Tax. Get tax readiness dimensions. Local policy: whether reward needs them and owner status mapping. Do not interpret provider state.
- **SH-011/012**; evaluate/request hold. Local policy: reward abuse/tax/fulfillment action mapping. Do not build local hold state.
- **SH-118 — reportTaxableValue**; Payment/Tax. Report recognized reward value idempotently. Local policy: FMV snapshot and recognition moment. Do not create filing logic.
- **SH-041 — requestNotification**; Notification. Request tax action/redemption/fulfillment communication. Local policy: timing/template context. Do not build email/push service.
- **SH-047/048**; durable fulfillment/value-report jobs and retries. Do not build local queue/retry loops.
- **SH-037**; record normalized integration/downstream failures. Do not use failure record as redemption status.
- **SH-029/030**; audit material fulfillment actions and sensitive admin access.
- **SH-119 — applyTemporaryFeatureGrant** only after approval. Gamification owns reward cause; grant/effect owner owns actual benefit. Never alter prize odds.

#### Data / Schema

Primary owner record:

- `RewardRedemption` (`blockedByHoldId`, `taxProfileId`, value snapshot, status/timestamps)

External referenced truth:

- `ComplianceHold`
- `TaxProfile`
- Tax-owned reporting records
- future grant/provider records outside or inside Gamification only after explicit ownership decision.

Do not add `providerStatus` or `taxApproved` to RewardRedemption as a shortcut.

#### Public Interfaces

Complete:

- `transitionRewardRedemption`
- Payment/Tax consumer calls via SH-019/118
- Hold calls via SH-011/012
- `requestNotification`
- conditional `applyTemporaryFeatureGrant` after SH-119 approval
- provider-neutral `RewardFulfillmentPort` only if U-CL10-05 assigns a provider/effect to Gamification and specifies proof persistence.

#### Logic

- Classify whether the redemption’s reward type/value requires tax readiness under approved policy; do not hardcode one tax regime.
- Move to `pending_tax`/blocked as owner policy requires.
- Reevaluate after external owner fact changes rather than letting external owner mutate status.
- Report recognized value once with reward/redemption IDs and valuation evidence.
- For `cash_bonus`, financial movement must be through Payment/Payout/Tax; Gamification records the resulting outcome only.
- For `profile_boost`, use SH-119 only after approval; never write Search/entitlement flags directly.
- For `platform_credit`, do not implement until the owner ledger/effect is identified.
- For physical/gift-card/other provider fulfillment, require approved provider/evidence contract before `fulfilled` is reachable automatically.
- `reversed` requires compensating point/effect semantics defined for that reward type.

#### UI / Administrative Surface

- redemption compliance/fulfillment queue;
- tax action required state;
- active hold reference/safe reason;
- retryable integration failure indicator;
- supported/unsupported fulfillment explanation;
- admin transition controls only where owner policy allows.

Sensitive tax details stay in Payment/Tax interfaces; CL-10 UI displays only minimal readiness/reason data.

#### Authorization / Compliance

- User sees only own redemption status/evidence appropriate for UX.
- Sensitive admin reads may require SH-030.
- Financial/tax-sensitive approval may require SH-014 per root policy.
- Hold release is never performed by Gamification.
- No reward effect may create better sweepstakes odds.

#### Events / Jobs / Integrations

- tax-value reporting job;
- fulfillment/effect job only for supported approved types;
- notification requests after owner transitions;
- retries/dead letters through canonical worker framework;
- provider reconciliation only if a provider owner/adapter exists.

#### Failure Behavior

- Tax service unavailable → leave redemption in valid pending state; retry, do not auto-approve.
- Hold active → fulfillment denied; owner state remains explainable.
- Provider/effect failure → no `fulfilled`; record operational failure and retry/manual review according to approved policy.
- Unknown provider status → normalized failure/manual review; no raw status mapped ad hoc.
- SH-119 unresolved → profile boost remains unsupported, not local flag fallback.

#### Tests

- Unit: status mapping from readiness/hold decisions; supported type routing; reversal invariants.
- Contract: SH-019/118, hold, notification, conditional SH-119.
- Integration: pending_tax → approved → fulfilled only after evidence.
- Idempotency: duplicate taxable-value report/fulfillment result.
- Failure: Payment/Tax unavailable, Notification failure, provider failure.
- Compliance: blocked redemption cannot fulfill; no tax provider interpretation; no odds boost.
- Privacy/sensitive access: minimal data and audit.

#### Out of Scope

- inventing provider choices;
- filing 1099/DAC7 or tax documents;
- direct Stripe transfer/webhook handling;
- implementing Search boost without SH-119/affected-owner contract;
- creating a platform-credit wallet.

#### Exit Gate

- Tax-sensitive redemption cannot fulfill before positive owner-issued readiness.
- Active hold blocks fulfillment without a local blocked truth system.
- Recognized value reaches Payment/Tax once with idempotency/evidence.
- A supported effect can complete and transition RewardRedemption through owner service.
- Unsupported reward types remain non-active/non-fulfillable with explicit reasons.
- Notification/provider failures never fabricate fulfillment.
- no entitlement/search/payment/provider lifecycle is owned by Gamification.
- all relevant tests pass.

---

## Phase 3 — Sweepstakes and Prize Lifecycle

Chance-based behavior is introduced only after deterministic rewards are separated and platform gates are proven.

### 06 Prize Drawing, Entry-Method, AMOE, and Rules Activation Gate

Build draft drawing configuration and make production activation contingent on immutable rules evidence and legal/compliance policy.

#### Objective

An authorized administrator can configure `PrizeDrawing` and `SweepstakesEntryMethod` records; the owner can validate AMOE/no-purchase/equivalent-odds rules and activate a drawing only after approved immutable rules/consent evidence exists.

#### User-visible / Observable Result

- Admin can create/edit a draft drawing and entry methods.
- Configuration clearly shows free vs purchase-triggered routes, entries awarded, odds-equivalent flag, limits, dates, prize FMV/currency, and rules reference.
- Invalid purchase-only/unequal-odds configuration is visibly rejected.
- Production activation fails closed until U-CL10-01 is resolved and required legal/rules proof exists.

#### Owning Module(s)

- Sweepstakes / Prize owns drawing and entry-method truth and activation decision.
- Consent & Disclosure owns versioned acceptance proof.
- Legal drafting/review remains external governance, not a new CL-10 lifecycle.

#### Dependencies

- Phase 1 platform auth/authz/consent/audit patterns.
- `PrizeDrawing`, `SweepstakesEntryMethod`, their enums.
- SH-001/002/008/009/029/044/046.
- **Architecture checkpoint:** U-CL10-01 must be resolved before production activation is complete.
- SH-077/072 if the approved rule-proof design uses canonical snapshot/hash primitives.

#### Shared Operations Used

- **SH-001/002**; actor and admin authorization. Local policy: drawing actions.
- **SH-009/008**; resolve/check applicable sweepstakes rules/disclosure consent. Local policy: which rule version is required.
- **SH-029**; audit activation/cancellation/material configuration actions.
- **SH-044**; idempotent activation/transition commands.
- **SH-046**; drawing lifecycle events.
- **SH-077/072** conditionally; canonical snapshot/hash mechanics if approved. Local policy: canonical fields and what the hash proves. Do not invent a local crypto helper.

#### Data / Schema

- `PrizeDrawing`
- `SweepstakesEntryMethod`

Potential additional rule-proof schema is **not pre-authorized by this plan**. Resolve U-CL10-01, update architecture/Prisma plan, then migrate.

Current fields to validate include:

- `noPurchaseNecessary`
- `amoeEnabled`
- free/paid/max entry limits
- `officialRulesUrl`
- `prizeValueCents`/currency
- `eligibilityJson`
- entry-method `isFree`, `requiresPurchase`, `entriesAwarded`, `oddsEquivalent`.

#### Public Interfaces

- `configurePrizeDrawing`
- `configureSweepstakesEntryMethod`
- `activatePrizeDrawing`
- `pause/retireEntryMethod`
- `closePrizeDrawing`
- `cancelPrizeDrawing`
- `getPrizeDrawing`

#### Logic

- Draft configuration is allowed before legal completion.
- Timing must be coherent (`startsAt`, `endsAt`, `drawsAt`).
- Entry method flags/type combinations are validated.
- If a purchase-triggered method exists, activation requires the legally required free/AMOE path.
- `entriesAwarded`/weight policy cannot create hidden paid odds advantage.
- `eligibilityJson` must be schema-validated/versioned declarative policy if used; no executable code.
- Active method set is frozen/versioned enough to explain issued entries; material post-activation edits require explicit owner policy/audit.
- U-CL10-01 determines immutable official-rules proof before activation.

#### UI / Administrative Surface

Admin sweepstakes configuration:

- drawing list/detail/status;
- dates/prize/FMV/currency;
- official rules evidence/reference status;
- entry-method editor;
- AMOE/free-path validation panel;
- odds-equivalence warning/error;
- activation checklist and legal-gate state;
- close/cancel controls.

#### Authorization / Compliance

- Protected admin mutations through SH-002.
- Activation is compliance-sensitive and audited.
- Legal review/approved rules evidence is a hard production gate.
- No purchase-only activation where prohibited.
- No points/reward/entitlement odds influence.
- No `isSweepstakesAdmin` local helper.

#### Events / Jobs / Integrations

- drawing activated/closed/cancelled owner events.
- optional scheduled close/draw trigger registration through canonical job infrastructure after activation.
- No Stripe webhook.
- No Tax provider call yet.

#### Failure Behavior

- Missing free path/unequal odds → activation denied with structured reasons.
- Missing immutable rule proof → draft persists, production activation denied.
- Consent service unavailable → fail closed for required activation/entry proof.
- Unauthorized activation → denial + appropriate audit/telemetry.
- Outbox failure → canonical retry; owner state remains authoritative.

#### Tests

- Unit: drawing/entry-method lifecycle, timing, AMOE/equivalent odds, limit validation.
- Integration: draft configuration and activation gate.
- Contract: consent/rules proof.
- Compliance: purchase-triggered method cannot be sole required path; paid advantage rejected.
- Authorization/audit tests.
- Architecture test: no Sweepstakes Stripe webhook/ProcessedStripeEvent implementation.

#### Out of Scope

- issuing entries;
- consuming purchase events;
- winner selection;
- prize tax/fulfillment;
- legal drafting.

#### Exit Gate

Feature 06 cannot pass until:

- U-CL10-01 has an approved architecture resolution and any required schema/contract change is documented;
- draft drawing/method CRUD uses owner services and stable DTOs;
- activation requires immutable rules evidence and applicable Consent proof/version;
- configured purchase path cannot activate without required AMOE/free path;
- paid methods cannot receive better effective odds under equivalent-odds policy;
- drawing status transitions are tested and audited;
- no direct Stripe/provider ownership exists in Sweepstakes;
- build/test checks pass.

---

### 07 Idempotent Prize Entry Issuance and Authoritative Purchase Bridge

Issue free, mail/admin/system, and purchase-triggered PrizeEntry records from the correct authoritative sources while enforcing race-safe limits and consent/eligibility.

#### Objective

Each qualifying entry path creates its own auditable PrizeEntry exactly once under the drawing’s configured method and limits, and purchase-triggered entries arrive from an authoritative Order/payment-owner event rather than Stripe.

#### User-visible / Observable Result

- User can use the configured free entry path and see accepted/denied result.
- An authoritative qualifying purchase event creates the configured PrizeEntry count exactly once.
- Duplicate clicks/events do not duplicate entries.
- Admin can inspect entry source/method/eligibility/consent reference without seeing provider internals.
- Per-user/free/paid/max entry limits hold under concurrent requests.

#### Owning Module(s)

- Sweepstakes / Prize owns entry issuance, limits, eligibility, source, weight, and PrizeEntry truth.
- Transaction / Order or Payment owner owns the qualifying purchase fact.
- Consent owns proof.
- ComplianceHold owns stop signs where policy applies.

#### Dependencies

- Feature 06.
- `PrizeEntry`, `PrizeEntrySource`, `SweepstakesEntryMethod`.
- PR-CL10-01 purchase bridge approved.
- SH-008, SH-011, SH-044/045/046, SH-051, SH-041, SH-029.
- U-CL10-09 does not block runtime proof validation but blocks any FK migration decision.

#### Shared Operations Used

- **SH-008**; query exact rules consent proof. Local policy: sufficiency for drawing/method.
- **SH-011**; applicable hold check where entry issuance/drawing eligibility policy uses holds. Local mapping stays Sweepstakes-owned.
- **SH-044**; idempotent free/mail/admin/system command.
- **SH-045**; dedupe authoritative purchase source events. Local policy: one event/order may create configured entries once per drawing/method semantics.
- **SH-051**; aggregate/user-drawing lock where needed for race-safe entry counts.
- **SH-046**; entry-issued/eligibility events.
- **SH-041**; optional entry confirmation notification.
- **SH-029**; audit admin adjustments/eligibility overrides.

#### Data / Schema

Write:

- `PrizeEntry`

Important current evidence:

- `entryToken` is unique but is not sufficient source-event dedupe by itself.
- `orderId` may reference authoritative Order.
- `rulesConsentId` stores proof reference but currently has no Prisma relation to ConsentLog.
- `weight` exists; owner policy must constrain it under equivalent-odds requirements.

No local provider-event table.

#### Public Interfaces

- `issuePrizeEntry`
- `evaluatePrizeEntryEligibility`
- `getUserDrawingEntries`
- `markPrizeEntryIneligible` / approved eligibility correction command
- inbound owner event consumer for qualifying purchase outcomes

#### Logic

**Free entry:**

- verify active drawing/method/time window;
- verify user/consent/eligibility;
- count race-safely against free and max limits;
- create exactly configured entries.

**Purchase entry:**

- consume authoritative owner event through SH-045;
- validate drawing/method exists and active at the relevant event time;
- reference Order ID;
- enforce paid/max limits and equivalent odds;
- issue once per source semantics.

**Mail-in/admin/system:**

- require appropriate authority/workflow proof;
- admin adjustment is audited;
- no method can quietly use higher weight because it is paid/admin-originated.

PrizeEntry corrections follow PR-CL10-07: no casual deletion; eligibility changes are auditable and freeze-aware.

#### UI / Administrative Surface

User-facing where applicable:

- free daily entry action and result;
- own entry count/status summary.

Admin:

- entry list/filter by source/method/user/order;
- eligibility reason;
- safe consent proof reference;
- admin-adjustment form with reason;
- duplicate/limit-denial visibility.

#### Authorization / Compliance

- Free entry action must not require a purchase.
- Equivalent odds enforced at issuance.
- Admin adjustment cannot bypass max/odds/legal policy without explicit reviewed override path.
- No entitlement or points path creates entries in the current architecture.
- Consent proof is verified centrally; Sweepstakes makes the entry decision.

#### Events / Jobs / Integrations

- Transaction / Order/Payment owner event consumer for purchases.
- Outbox entry events.
- Optional notification request.
- Mail-in intake may be an admin operational surface; no new external provider is required.

#### Failure Behavior

- Duplicate free request/source event → existing/no-op result.
- Limit reached → denied with reason, no write.
- Purchase source event arrives before drawing/method is valid → owner policy decides no-op/retry based on event timing; never fabricate provider state.
- Consent missing → denied.
- Hold blocks action → denied/flagged per policy; no local hold creation.
- Concurrent requests → transaction/lock ensures limit is not exceeded.

#### Tests

- Unit: method/source mapping, limits, weight/equivalent odds, eligibility.
- Contract: qualifying purchase event.
- Idempotency: duplicate click/event/admin command.
- Concurrency: simultaneous free entries at limit boundary; simultaneous purchase events.
- Compliance: free path unaffected by purchase; no paid odds boost.
- Authorization/audit: admin adjustments and eligibility changes.
- Regression: no Stripe handler imported/created in Sweepstakes.

#### Out of Scope

- random winner selection;
- redraw;
- tax fulfillment;
- points-to-entry bridge;
- provider payment verification.

#### Exit Gate

- Free entry produces correct PrizeEntry truth without purchase.
- Purchase owner event produces exactly configured entries once and includes Order provenance.
- Duplicate delivery/click cannot exceed counts.
- concurrent entry requests cannot exceed configured limits.
- all active equivalent methods use approved effective odds/weight policy.
- admin/eligibility corrections are audited and freeze-safe.
- no Stripe webhook, provider status mapping, or Payment repository appears in Sweepstakes.
- tests/build checks pass.

---

### 08 Secure Drawing Execution and PrizeWinning Creation

Run a cryptographically secure, concurrency-safe drawing against a frozen eligible population and persist enough immutable domain proof to reproduce/audit what occurred.

#### Objective

A closed PrizeDrawing can transition through one authorized drawing run, select winner(s) through SH-116, create PrizeWinning records, and complete without relying on transient logs or AuditEvent as drawing proof.

#### User-visible / Observable Result

- Admin/worker can start a closed, eligible drawing exactly once.
- A frozen population count/hash/run proof is inspectable by authorized admins.
- Winner records are persisted with prize FMV/currency/tax year snapshot.
- Concurrent worker attempts cannot create competing run outcomes.
- A notification failure cannot change selected winner truth.

#### Owning Module(s)

- Sweepstakes / Prize owns eligible-population policy, random selection policy, immutable run proof, PrizeWinning creation, and PrizeDrawing transition.
- Audit/Observability only record support evidence.

#### Dependencies

- Features 06–07.
- SH-116, SH-051, SH-044, SH-046, SH-047/048, SH-029, SH-014, SH-032/033/034.
- **Hard architecture checkpoint:** U-CL10-02 drawing-run proof schema/contract must be resolved and architecture updated before implementation of production selection.
- U-CL10-11 redraw/replacement policy is not required for initial single run; redraw remains out of scope unless resolved.

#### Shared Operations Used

- **SH-116 — secureRandomSelection**; Sweepstakes owner. Use unbiased CSPRNG over frozen eligible population. Local policy: population/weight/winner count/replacement. Never use `Math.random()`.
- **SH-051 — acquireAggregateLock**; platform/database. Single active drawing run per drawing. Local lock key: drawing/run semantics. Do not use in-memory mutex.
- **SH-044**; idempotent run command.
- **SH-046**; winner/drawing lifecycle events transactionally.
- **SH-047/048**; durable scheduled drawing worker/retries. Local policy distinguishes safe retry before/after committed run.
- **SH-029**; audit run initiation/material admin action.
- **SH-014**; central step-up if root policy requires admin-initiated draw/override assurance.
- **SH-032/033/034**; request context, logs, redaction.

#### Data / Schema

Existing:

- `PrizeDrawing`
- `PrizeEntry`
- `PrizeWinning`

Required additional **drawing-run proof record(s)** depend on U-CL10-02. The implementation specification must use the approved schema name/fields, not invent them from this build plan.

Minimum proof semantics required by architecture:

- drawing ID and run identity;
- frozen eligible population evidence/count and integrity reference;
- selection policy/version;
- winner count/replacement behavior;
- randomness/CSPRNG evidence appropriate to the chosen design;
- selected entry/winner references;
- actor/system/correlation/time;
- immutable completion/result evidence.

#### Public Interfaces

- `runPrizeDrawing`
- `getDrawingRunEvidence` (or approved equivalent)
- `getPrizeWinning`
- owner transition/query for drawing state

#### Logic

- Only `closed` drawing may enter `drawing` through owner service.
- Acquire lock before checking/transitioning run state.
- Resolve the exact eligible entry set and freeze it.
- Reject entries marked ineligible or otherwise excluded by approved policy.
- Enforce weight/equivalent-odds policy against the frozen set.
- Select with SH-116.
- Persist run proof + PrizeWinning(s) + drawing completion/event atomically or through an explicitly recoverable owner workflow that cannot select twice.
- Snapshot prize name/FMV/currency/tax year into PrizeWinning.
- Do not send notifications inside the selection transaction if delivery could cause non-deterministic rollback.

#### UI / Administrative Surface

Authorized admin drawing console:

- closed/ready status;
- eligible count;
- compliance/rules readiness;
- start drawing control where allowed;
- run ID/status/evidence summary;
- selected winning records;
- no redraw button unless U-CL10-11 is resolved.

#### Authorization / Compliance

- Run command requires explicit authority; step-up where root policy requires.
- AMOE/equivalent-odds validation rechecked before freezing population.
- No admin can directly choose a winner through the normal draw path.
- Any legal/admin override path must be separately specified, audited, and must not masquerade as random selection.
- Sensitive winner data access may require SH-030 in later workflow.

#### Events / Jobs / Integrations

- Scheduled drawing job through SH-047/048.
- Outbox events after committed selection.
- Notification requested downstream in Feature 09 or after safe commit.
- No external random provider.

#### Failure Behavior

- Lock conflict → one runner proceeds; others return existing/in-progress outcome.
- Crash before committed run → safe retry without winner duplication.
- Crash after committed run → retry returns committed run; never selects again.
- Invalid/frozen population issue → fail drawing safely; do not create partial winners.
- Notification/Tax downstream outage → selected winner truth remains; downstream workflow retries.
- Missing U-CL10-02 schema → production run unavailable.

#### Tests

- Unit: population eligibility, weighting policy, state transition preconditions.
- Statistical/property tests for selection utility to detect obvious bias while not relying on deterministic production seeds.
- Integration: closed drawing → run proof → PrizeWinning → completed.
- Concurrency: two+ workers start same drawing.
- Idempotency: retry before/after commit.
- Compliance: paid/free equivalent population weighting.
- Security: no predictable PRNG; unauthorized run denied.
- Recovery: downstream notification/tax failure leaves run intact.

#### Out of Scope

- redraw/replacement winner;
- winner claim-window policy unless later approved;
- tax verification/fulfillment;
- provider shipping/payment effects.

#### Exit Gate

- U-CL10-02 is resolved and approved schema/migration is present.
- a drawing cannot enter `drawing` twice concurrently.
- eligible population is frozen/proven before selection.
- SH-116 is the only winner-selection mechanism.
- one completed run yields one immutable run proof set and correct PrizeWinning records.
- crash/retry cannot select a second set of winners.
- Audit/telemetry are support evidence only, not run truth.
- no redraw exists unless separately approved.
- tests/build checks pass.

---

### 09 Prize Tax Summary, Hold Gate, and Fulfillment Lifecycle

Take selected PrizeWinning truth through tax readiness, hold review, yearly prize aggregation, notification, and approved fulfillment without transferring lifecycle ownership.

#### Objective

Sweepstakes can map Payment/Tax and ComplianceHold decisions into its own PrizeWinning lifecycle, maintain/reconcile PrizeTaxYearSummary, report recognized value to Tax, and mark fulfillment only after authoritative evidence.

#### User-visible / Observable Result

- Winner sees an accurate pending-tax/pending-confirmation/approved/fulfilled/blocked/forfeited state.
- Tax-required win cannot fulfill before required tax readiness.
- Admin sees minimal hold/readiness evidence and next action.
- Prize yearly summary totals match recognized winning value.
- Winner notification is sent after winning truth exists and does not change status by delivery alone.

#### Owning Module(s)

- Sweepstakes / Prize: PrizeWinning lifecycle, FMV snapshot, PrizeTaxYearSummary, fulfillment-state decision.
- Payment / Payout / Tax: TaxProfile, reporting threshold/regime/submission/provider truth.
- Admin Review / Compliance Hold: hold lifecycle/release.
- Notification: delivery lifecycle.
- Future fulfillment provider owner: unresolved until explicitly assigned.

#### Dependencies

- Feature 08.
- SH-019, SH-011/012, SH-117/118, SH-041, SH-047/048, SH-037, SH-029/030.
- Approved legal tax/fulfillment rules under U-CL10-12 for production jurisdictions.
- Any future provider effect requires U-CL10-05-equivalent provider ownership for prizes if needed.

#### Shared Operations Used

- **SH-019**; Payment/Tax readiness. Local policy: how result maps to PrizeWinning state. Do not inspect provider state.
- **SH-011/012**; hold gate/request. Local policy: prize action mapping. Hold lifecycle remains external.
- **SH-117 — aggregateYearlyReportableValue**; rebuild/update PrizeTaxYearSummary. Local policy: recognized winning inclusion, currency/year. Do not merge with TaxYearEarningsSummary.
- **SH-118**; report prize value to Payment/Tax. Local policy: FMV snapshot and recognition time.
- **SH-041**; winner/tax/fulfillment notification requests.
- **SH-047/048**; tax/fulfillment/reconciliation jobs.
- **SH-037**; operational provider/downstream failures.
- **SH-029/030**; material fulfillment actions and sensitive access evidence.

#### Data / Schema

Writes:

- `PrizeWinning`
- `PrizeTaxYearSummary`

References:

- `ComplianceHold`
- `TaxProfile`

Tax owner may update its own `TaxYearEarningsSummary`/reporting records from SH-118. Sweepstakes never writes them directly.

No local tax-threshold table unless an approved owner policy explicitly makes a drawing-specific snapshot field necessary; current `taxReportingThresholdCents` is historical snapshot metadata, not the global threshold authority.

#### Public Interfaces

- `transitionPrizeWinning`
- `getPrizeWinning`
- `getPrizeTaxYearSummary`
- owner reconciliation command for yearly summary
- SH-019/118 calls to Payment/Tax
- SH-011/012 calls to Hold owner

#### Logic

- Create/maintain correct initial state after Feature 08 according to approved tax requirement policy.
- Re-check holds and tax readiness immediately before fulfillment.
- `pending_tax` and `blocked` cannot transition to `fulfilled`.
- Payment/Tax readiness result is evidence; Sweepstakes decides its transition.
- Aggregate recognized FMV into PrizeTaxYearSummary idempotently and support full rebuild.
- Report value to Payment/Tax once with source IDs and valuation evidence.
- `approved → fulfilled` only after an approved fulfillment effect/evidence.
- `forfeited`/`cancelled` behavior must follow official rules/legal policy.
- Notification is after authoritative transition and independently retryable.

#### UI / Administrative Surface

Winner-facing where applicable:

- safe prize name/value/status;
- required tax/claim next action;
- fulfillment state.

Admin fulfillment UI:

- winning queue/status;
- rules/run evidence reference;
- minimal tax readiness;
- hold reference/reason;
- approve/forfeit/cancel/fulfill actions where allowed;
- reconciliation/failure indicators.

#### Authorization / Compliance

- Winner/admin authorization through central Role / Authority.
- Sensitive tax/winner data read may use SH-030.
- Fulfillment approval may require step-up per security policy.
- Tax-blocked prizes must not fulfill.
- Hold release remains outside Sweepstakes.
- Exact legal thresholds/jurisdictions are configuration/policy from the tax/legal owner, not hardcoded by a coding agent.

#### Events / Jobs / Integrations

- tax readiness/value reporting jobs;
- yearly summary reconciliation worker;
- notification requests;
- future provider fulfillment only behind approved owner port;
- dead letters surfaced through Observability.

#### Failure Behavior

- Tax service unavailable → retain safe pending state and retry.
- Active hold → block prohibited action, preserve winning truth.
- Notification failure → no change to PrizeWinning.
- Fulfillment provider failure → no `fulfilled`; retry/manual review.
- Aggregate failure → PrizeWinning source truth remains; reconciliation rebuild repairs summary.
- Duplicate tax report → idempotent no double reporting.

#### Tests

- Unit: winning transition matrix, tax/hold mappings, FMV inclusion.
- Integration: winner → pending tax → approved → fulfilled with owner decisions.
- Aggregate: incremental vs full PrizeTaxYearSummary rebuild.
- Contract: Payment/Tax and Hold interfaces.
- Idempotency: taxable report and summary updates.
- Compliance: blocked/pending-tax cannot fulfill; notification not fulfillment.
- Privacy/security: sensitive access and minimized tax data.

#### Out of Scope

- filing tax forms;
- direct tax provider/Stripe processing;
- true cash wallet/escrow;
- redraw/replacement policy;
- unsupported fulfillment provider invention.

#### Exit Gate

- Tax-required win is impossible to fulfill before positive owner-issued readiness.
- active hold blocks fulfillment without local hold truth.
- PrizeTaxYearSummary rebuild equals recognized PrizeWinning source values.
- Payment/Tax receives each recognized prize value once.
- Notification failure does not change winning state.
- `fulfilled` requires owner-approved fulfillment evidence.
- tax/provider records remain outside Sweepstakes ownership.
- tests/build checks pass.

---

## Phase 4 — Cross-Cluster Contract Proof

Replace test doubles with real neighboring Module contracts where available and prove CL-10 behaves as a good platform citizen without importing their source truth.

### 10 Cross-Cluster Integration, Privacy Executor, and Boundary Verification

Prove the Cluster’s important inbound/outbound contracts end-to-end and eliminate accidental direct coupling before hardening.

#### Objective

All production CL-10 workflows use the canonical public interfaces/events for identity, authorization, consent, Order/Review/Profile activity, tax, holds, notifications, privacy, audit/observability, and approved entitlement/search effects.

#### User-visible / Observable Result

- Real Order completion can award points through the event contract.
- Real qualifying purchase outcome can create PrizeEntry without Sweepstakes touching Stripe.
- Real tax/hold decisions drive owner states.
- Notification receives safe CL-10 requests.
- Privacy can enumerate/export/erase/anonymize/retain CL-10-owned subject data through owner executors.
- Integration tests can prove no neighboring Module source truth was copied into CL-10.

#### Owning Module(s)

- Gamification / Rewards and Sweepstakes / Prize retain their respective truth.
- Every neighbor retains its own truth; this feature owns no new lifecycle.

#### Dependencies

- Features 01–09.
- Production-ready or contract-complete neighboring Module interfaces.
- SH-095/096/097/098 for Privacy.
- Conditional SH-119/Track/Search only if approved reward type is included.

#### Shared Operations Used

This feature verifies, rather than reimplements, the SH operations already consumed in earlier features.

Additional focus:

- **SH-095 — executePrivacyInstruction**; Privacy orchestrates, each CL-10 owner executes. Local policy: record disposition. Do not create local privacy jobs.
- **SH-096 — enumerateSubjectData**; enumerate CL-10 subject records/provider refs. Do not use a global schema crawler.
- **SH-097 — evaluateRetentionRequirement**; return reward/prize/tax/fraud retention facts. Privacy records exemptions. Do not create local exemption tables.
- **SH-098 — anonymizePersonalFields**; use approved mapping while preserving necessary truth. Do not implement blanket deletion.
- **SH-119** only if approved for a deterministic temporary benefit; never for prize odds.

#### Data / Schema

No new Cluster-owned tables.

Validate ownership and foreign/reference behavior for:

- User/Profile IDs;
- Order references;
- Consent proof IDs;
- ComplianceHold links;
- TaxProfile links;
- Track entitlement/grant references if approved;
- Privacy retention behavior;
- provider references if any supported reward/prize provider exists.

Any schema fix discovered here must be made in the owning Module and documented before migration.

#### Public Interfaces

Replace fakes with real:

- source owner events for `order_completed`, profile completion, high rating, and qualifying purchase;
- SH-019/118 Payment/Tax;
- SH-011/012 Hold;
- SH-041 Notification;
- Privacy owner protocol;
- conditional Track/Search benefit contract.

#### Logic

- Verify source event versions and consumer compatibility.
- Ensure CL-10 does not enrich missing source facts by direct repository reads.
- Ensure downstream requests carry only needed evidence.
- Implement Privacy subject enumeration and owner action mapping.
- Verify retained records preserve required financial/prize/legal proof while personal fields are minimized where allowed.
- Verify cross-cluster events are idempotent and traceable by correlation ID.

#### UI / Administrative Surface

No artificial consumer UI is required.

Optional internal/admin integration view may expose:

- contract/worker status;
- last successful source event;
- projection lag;
- failed downstream calls;
- privacy executor result summaries.

It must not expose provider secrets or become source truth.

#### Authorization / Compliance

- Every real integration preserves source Module authorization/privacy boundaries.
- Privacy orchestration is Privacy-owned.
- Tax/provider details are minimized.
- No cross-cluster service account receives broader access than needed.
- Track/Search integration cannot affect prize odds.

#### Events / Jobs / Integrations

Exercise real:

- domain event inbox/outbox;
- Order/Profile/Review source events;
- Tax readiness/value handoff;
- Hold decisions;
- Notification delivery requests;
- Privacy executor jobs;
- approved benefit/search effect if in MVP.

#### Failure Behavior

- Neighbor contract unavailable → CL-10 workflow remains in valid pending/no-op state and operational failure is visible.
- Incompatible event version → reject/dead-letter safely; no partial business effect.
- Privacy target failure → return structured failure to Privacy for retry; do not create independent job state.
- Downstream timeout after possible commit → use idempotency/query/reconciliation rather than blindly repeat destructive effects.

#### Tests

- Contract tests against real provider/consumer Modules.
- E2E: Order → points; purchase outcome → PrizeEntry; prize/reward → tax/hold → notification.
- Privacy: enumerate/export/erase/anonymize/retain fixtures.
- Architecture/coupling tests or code review checks for forbidden Prisma imports.
- Security/authz tests across self/admin/system contexts.
- Idempotency across event replay and downstream retry.

#### Out of Scope

- redesigning neighbor Modules;
- adding a generic Cluster orchestration database;
- solving unresolved shared fraud ownership;
- introducing new reward provider types merely to increase coverage.

#### Exit Gate

- All production-enabled CL-10 source events come through explicit owner contracts.
- No Sweepstakes Stripe webhook or Payment repository coupling exists.
- Real Tax/Hold/Notification contracts pass integration tests.
- Privacy can enumerate and execute supported dispositions for both CL-10 Modules.
- Retention exceptions are recorded by Privacy, not CL-10.
- Any enabled entitlement/search reward effect uses approved owner contracts and cannot affect prize odds.
- no direct cross-domain database access remains in normal workflows.
- contract/E2E/build checks pass.

---

## Phase 5 — Security, Reconciliation, and Production Hardening

Hardening does not add new business ownership. It proves the existing architecture survives retries, concurrency, degradation, recovery, privacy, and production load.

### 11 CL-10 Production Hardening and Reconciliation

Harden the full deterministic reward and chance-based prize workflows, backfill/reconcile projections and aggregates, verify audit/observability completeness, and ensure unresolved legal/provider features fail closed.

#### Objective

CL-10 is production-ready for the exact enabled scope, with no known path to duplicate value, overspend points, oversubscribe inventory, duplicate entries/winners, bypass tax/holds, corrupt projections, leak sensitive data, or activate unresolved reward/prize mechanics.

#### User-visible / Observable Result

- Admin sees reliable operational failure/retry/reconciliation state.
- Users do not receive duplicate points, redemptions, entries, or winner notifications from retries.
- Projection/aggregate rebuilds repair drift without rewriting source truth.
- Disabled/legal-gated features are visibly unavailable rather than partially working.
- Production checks demonstrate data/privacy/security boundaries.

#### Owning Module(s)

- Each CL-10 Module hardens its own workflows and records.
- Observability, Audit, Privacy, Tax, Hold, Notification, and provider owners retain their respective support truth.

#### Dependencies

- Feature 10 passed.
- All architecture decisions required by the production-enabled scope are resolved.
- Any unresolved item remains explicitly disabled/draft and documented.

#### Shared Operations Used

Revalidate all consumed canonical operations, with emphasis on:

- SH-032/033/034 — request context, structured logging, redaction;
- SH-037/038 — integration/queue failure visibility;
- SH-044/045 — command/event dedupe;
- SH-047/048 — retries/dead letters;
- SH-051/056 — concurrency;
- SH-095–098 — privacy/retention;
- SH-115/117 — rebuild/reconciliation;
- SH-116 — secure random selection;
- SH-118 — idempotent tax-value reporting.

Do not introduce alternate hardening helpers that bypass these mechanisms.

#### Data / Schema

Review:

- indexes supporting user ledger, active program/rule, challenge, reward/redemption, drawing/entry/winning, yearly summary queries;
- uniqueness/idempotency coverage in platform shared mechanisms;
- foreign/reference integrity including U-CL10-09 outcome;
- drawing-run proof indexes/constraints after U-CL10-02 resolution;
- any approved reward inventory/provider proof schema;
- destructive migration safety and rollback strategy.

No denormalized truth is added solely for performance; use rebuildable projections/caches where required.

#### Public Interfaces

- Freeze/version all production-enabled CL-10 public contracts.
- Define compatibility policy for events and DTOs.
- Add admin reconciliation commands only through owner interfaces:
  - rebuild point balance/leaderboard;
  - reconcile reward redemption/provider effects if applicable;
  - reconcile PrizeTaxYearSummary;
  - re-report missing taxable values idempotently;
  - inspect/retry failed jobs without direct row mutation.

#### Logic

Hardening checklist:

- validate all lifecycle transition matrices;
- validate all command/event idempotency keys;
- concurrency test point spend, inventory, entry limits, and drawing run;
- full projection rebuild from source truth;
- full PrizeTaxYearSummary rebuild;
- tax-value reporting reconciliation;
- provider reconciliation for any actual CL-10-owned provider;
- dead-letter replay procedures;
- stale `drawing`/pending redemption/winning recovery rules;
- rate limits for public free-entry/redemption endpoints;
- privacy export/erasure/retention completeness;
- audit event coverage for privileged actions;
- sensitive access proof for protected admin views;
- telemetry redaction and payload-size checks;
- performance/load test for ledger aggregation, leaderboard queries, entry issuance, and drawing population freeze/selection;
- backup/restore and migration rehearsal for CL-10 tables.

#### UI / Administrative Surface

Internal operations/admin capabilities where useful:

- failed/retryable job list linked to canonical Ops records;
- projection/aggregate lag and last reconciliation;
- drawing run status/evidence summary;
- stuck pending redemption/winning review queue;
- safe integration failure detail;
- disabled-feature/legal-gate explanation.

Do not create an Ops source-of-truth copy inside CL-10.

#### Authorization / Compliance

- Security review all admin actions and step-up classifications.
- Verify public/free-entry endpoints cannot be used to enumerate sensitive user data.
- Verify no entitlement/points/reward purchase path changes prize odds.
- Verify all production drawings have approved rules evidence and legal policy.
- Verify all tax-sensitive fulfillment uses Tax owner decisions.
- Verify privacy retention logic is documented and tested.
- Verify unsupported reward types cannot become active through direct DB/UI manipulation in normal application roles.

#### Events / Jobs / Integrations

- Chaos/degradation tests for queue, Notification, Payment/Tax, Hold, and any actual fulfillment provider.
- Reconciliation jobs dry-run before repair where appropriate.
- Backfills are idempotent, resumable, and observable.
- Provider callbacks are authenticated/deduplicated only by provider owner.
- Dead-letter replay preserves correlation IDs.

#### Failure Behavior

- Partial infrastructure outage → safe pending state and visible retry, never fabricated success.
- Projection drift → rebuild, no source rewrite.
- Tax-report drift → idempotent re-report/reconcile.
- Stale drawing lock/run → owner recovery procedure based on immutable run proof, never a fresh blind rerun.
- Migration failure → rollback/forward-fix plan documented; no destructive automatic production retry.
- Privacy executor failure → retry through Privacy orchestrator.
- Unresolved legal/provider decision → feature remains disabled; production launch scope excludes it.

#### Tests

- Unit regression suite for every owner invariant.
- Integration suite for all public contracts.
- Concurrency/load tests.
- Event/command/provider idempotency tests.
- Retry/dead-letter/reconciliation tests.
- Security/authorization/step-up tests.
- Compliance AMOE/no-paid-odds/tax-hold tests.
- Privacy export/erasure/anonymization/retention tests.
- E2E deterministic rewards flow.
- E2E free and purchase entry → secure draw → tax-aware fulfillment flow.
- Migration/reset/seed tests.

#### Out of Scope

- new reward types/providers not already approved;
- redraw/replacement winner unless U-CL10-11 is resolved;
- generalized fraud/risk platform;
- analytics/search features not required for CL-10 correctness;
- changing neighboring Module ownership.

#### Exit Gate

CL-10 production hardening passes only when:

- all standard typecheck/lint/unit/integration/E2E/build commands pass;
- duplicate/replay/concurrency tests demonstrate no duplicate points, point spend, redemptions, entries, draw runs, winners, taxable-value reports, or fulfillment effects;
- projection and yearly-summary full rebuilds reconcile exactly to authoritative source data;
- all provider/downstream degradation cases leave valid domain states;
- CL-10 consumes canonical SH-037/038 observability interfaces without inventing local Ops tables even if the root Observability persistence naming remains under U-CL10-13;
- all privileged actions have required authorization/audit/step-up behavior;
- privacy target inventory and retention tests pass;
- telemetry redaction tests prove sensitive payloads are excluded;
- no production-enabled feature depends on an unresolved architecture/legal decision;
- any intentionally deferred reward type/drawing behavior is disabled and documented;
- architecture/build-plan/progress tracker reflect the shipped scope.

---

## Cross-Cluster Integration Phase

Phase 4 / Feature 10 is the explicit cross-Cluster integration phase. Its purpose is to **prove contracts, not absorb source truth**.

The minimum bridges that must be real before CL-10 production launch are:

```text
Identity / Role
→ CL-10 actor and authority

Consent & Disclosure
→ exact version/proof

Transaction / Order
→ order-completed point trigger
→ qualifying purchase event for PrizeEntry

Payment / Payout / Tax
→ tax readiness
← recognized reward/prize value

Admin Review / Compliance Hold
→ active hold decisions
← justified hold requests

CL-10
→ Notification request
→ Audit evidence
→ Observability telemetry

Privacy / Data Erasure
→ subject-data instructions
← owner execution/results
```

Conditional Track/Search bridges are included only when a specific approved deterministic reward effect requires them.

---

## Hardening Phase

Phase 5 / Feature 11 is the hardening phase. It is limited to CL-10-relevant production readiness:

- server-side security and privilege review;
- step-up classification;
- rate limits and abuse-resistant public entry/redemption commands;
- point, reward inventory, entry-limit, and drawing concurrency;
- event/job/provider idempotency;
- provider degradation behavior;
- queue retry/dead-letter recovery;
- projection and yearly-value reconciliation;
- safe backfills;
- privacy export/erasure/retention;
- audit completeness;
- observability/telemetry redaction;
- performance/load boundaries;
- schema/index/migration safety;
- enabled-scope legal readiness;
- fail-closed behavior for unresolved reward/prize features.

Hardening does not create a generic risk, tax, provider, or Cluster lifecycle system.

---

## Phase Summary

| Phase | Name | Features | Count |
|---|---|---|---:|
| 1 | Deterministic Engagement Foundation | 01 Programs/Rules/Disclosure; 02 Source Events → Point Ledger; 03 Challenges/Projections/Leaderboards | 3 |
| 2 | Deterministic Reward Economy | 04 Reward Catalog/Atomic Redemption; 05 Tax/Hold/Fulfillment/Benefit Bridges | 2 |
| 3 | Sweepstakes and Prize Lifecycle | 06 Drawing/AMOE/Rules Gate; 07 Entry Issuance/Purchase Bridge; 08 Secure Drawing/Winnings; 09 Prize Tax/Fulfillment | 4 |
| 4 | Cross-Cluster Contract Proof | 10 Integration/Privacy/Boundary Verification | 1 |
| 5 | Security, Reconciliation, and Production Hardening | 11 CL-10 Production Hardening | 1 |
| **Total** |  | **01–11** | **11** |

---

## Phase Execution Pattern

Before each numbered feature:

1. Read the required root, Cluster, target Module, dependency Module, shared-operation, and progress context.
2. Confirm the previous numbered feature’s exit gate passed.
3. Check the Cluster architecture’s Proposed Rulings and Unresolved Decisions for blockers specific to this feature.
4. Write the feature implementation specification at implementation-level detail.
5. Confirm schemas, migrations, public contracts, permission actions, shared operations, events/jobs, error semantics, and tests.
6. Implement **only** that feature and prerequisite changes in their correct canonical owners.
7. Run typecheck, lint, unit/integration tests, migration checks, and production build as applicable.
8. Perform the feature’s workflow verification, including retry/denial/duplicate paths.
9. Update the progress tracker.
10. Update architecture first if a binding decision legitimately changed.
11. Record risks, assumptions, unresolved questions, and deferred work.

A coding agent must not “finish” a feature by weakening an exit gate or making an unresolved behavior silently permissive.

---

## Required Feature Specification

Immediately before implementing each numbered feature, create a concise implementation specification containing:

- Objective
- Observable result
- Dependencies
- In scope
- Out of scope
- Owning Module
- Data records affected
- Migrations/constraints/indexes affected
- Public interfaces
- Shared Operations consumed by SH-### ID
- Permission/action vocabulary
- Primary workflow
- UI/admin states if applicable
- Provider integrations and explicit provider owner
- Jobs/events/outbox consumers
- Idempotency/concurrency key semantics
- Error/failure behavior
- Tests
- Acceptance criteria
- Documentation/progress updates
- Architecture decisions that were resolved or remain blockers

Do **not** pre-write file-by-file giant implementation specifications for all 11 features. This Cluster build plan defines sequencing and boundaries; the detailed implementation specification is written only for the next feature immediately before coding it.

---

## Required Completion Report

After each feature, the coding agent must report:

- Feature completed
- Observable result verified
- Files added
- Files changed
- Database changes
- Migrations
- Constraints/indexes added or changed
- Dependencies added
- Shared Operations reused by SH-### ID
- Canonical-owner changes required outside CL-10
- Public interfaces added/changed
- Domain events/outbox consumers added
- Jobs/workers added
- Provider adapters added/changed, with owner
- Tests added/changed
- Commands run
- Manual/workflow verification
- Authorization/compliance verification
- Idempotency/concurrency verification
- Privacy/audit/observability verification where applicable
- Documentation updated
- Assumptions
- Architecture rulings resolved
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result: **PASS / FAIL**, with evidence

A feature whose exit gate fails is incomplete. The next numbered feature does not begin until the failure is resolved or the architecture/build plan is explicitly revised.
