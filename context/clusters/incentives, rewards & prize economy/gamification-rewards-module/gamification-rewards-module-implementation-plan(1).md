# Gamification / Rewards Module Implementation Plan

> **Module ID:** `gamification_rewards`  
> **Module:** Gamification / Rewards Module  
> **Primary Cluster:** `CL-10 — Incentives, Rewards & Prize Economy`  
> **Repository target:** `context/clusters/incentives, rewards & prize economy/gamification-rewards-module/gamification-rewards-module-implementation-plan(1).md`\
> **Companion:** [Module architecture](<gamification-rewards-module-architecture(1).md>), [CL-10 architecture](<../incentives-rewards-prize-economy-cluster-architecture.md>), [CL-10 build plan](<../incentives-rewards-prize-economy-cluster-build-plan.md>), context-map routing, Canonical Shared Operations Registry\
> **Plan status:** Implementation-grade Module plan. It is subordinate to the CL-10 Cluster build plan and must not change Cluster sequencing or ownership independently.

---

**Context routing and availability:** Follow [context/context-map.md](<../../../context-map.md>) for authority by concern and actual artifact paths; use [context/project-overview-v3.md](<../../../project-overview-v3.md>) as the overview entry point. Root architecture/build plan, `context/code-standards.md`, and the dedicated progress tracker are unavailable in the current context inventory. References below to those artifacts or their standards are conditional prerequisites, not evidence of an existing global sequence or approval. Do not invent missing root decisions or artifacts.

## Core Principle

Implement Gamification / Rewards through narrow, owner-verifiable slices:

```text
public / observable behavior
→ validated command or query
→ Gamification-owned policy
→ authoritative Gamification write/read
→ canonical shared-operation calls
→ transactional owner event
→ audit / notification / downstream handoff
→ tests
→ explicit exit gate
```

This Module plan is intentionally narrower than the CL-10 build plan.

The Cluster plan coordinates Gamification with Sweepstakes / Prize and neighboring Clusters. This plan defines exactly what must be implemented **inside `gamification_rewards`**, what external contracts it consumes, and what it must never duplicate.

A feature whose architecture blocker is unresolved does not become "done" by inventing a local workaround. Scaffold/test contracts may proceed where explicitly allowed, but the feature exit gate remains failed until the required ruling exists.

---

## Build Rules

1. Follow `context/context-map.md` for concern-specific authority, the canonical Shared Operations registry, and the applicable Cluster/Module architecture and sequencing plans. Root architecture/code standards remain unavailable conditional prerequisites.
2. Build only `gamification_rewards` source truth in this Module.
3. Do not absorb `sweepstakes_prize`, Tax, Hold, Consent, Search, Notification, Track, Privacy, Audit, or provider truth.
4. Cross-Module dependencies use approved public interfaces or versioned events; direct cross-domain Prisma access is not the default.
5. Reuse SH-### operations; if a canonical operation is not implemented, fix/coordinate its canonical owner or use a contract fake where this plan explicitly permits.
6. Every mutation validates inputs server-side and uses SH-001/SH-002 where actor authorization applies.
7. `PointLedgerEntry` remains append-only truth. No mutable point balance authority.
8. Source event replay must not duplicate point effects.
9. Program, Challenge, Reward, and RewardRedemption transitions use owner policy plus SH-053 mechanics.
10. Point spend and RewardRedemption creation are atomic.
11. Limited inventory cannot use check-then-write; it remains disabled until U-GR-08 is resolved.
12. Rule JSON is declarative, typed, schema-versioned configuration and never executable code.
13. Unsupported source triggers remain inactive; `delivery_on_time` is blocked until U-GR-13 resolves.
14. Unsupported RewardTypes remain draft/paused/unfulfillable.
15. No point/reward/entitlement effect may improve chance-based prize odds.
16. Provider details remain behind the explicit provider owner; no provider is invented because an enum exists.
17. Jobs use SH-047/048 and are durable, idempotent, retryable where safe, and observable.
18. Domain events use SH-046; event delivery uses SH-045; neither is replaced by logs.
19. Privacy orchestration remains Privacy-owned; this Module implements SH-095–098 owner protocol only.
20. Audit and operational telemetry are distinct from Module truth.
21. Every numbered feature ends with tests and an exit gate.
22. Do not begin a dependent numbered feature until the prior feature exit gate passes, except contract-fake work explicitly marked parallel-safe.
23. Architecture changes are documented before code depends on them.
24. No feature may "resolve" an Unresolved Decision inside implementation code without an approved architecture update.

---

## Preconditions

### Hard platform prerequisites

The following contracts/mechanisms must exist in production before the dependent feature can be production-enabled:

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-045 `deduplicateDomainEvent` before source-event awards;
- SH-046 `publishDomainEvent`;
- SH-031 append-only domain-ledger mechanism;
- SH-051/052/053/056 persistence concurrency/lifecycle primitives as applicable;
- SH-047/048 durable jobs for asynchronous features;
- current Prisma migrations for the Module-owned records;
- root request/telemetry conventions.

If these are missing, they are canonical-owner/platform prerequisites, not local helper opportunities.

### Hard architecture decisions by feature

| Decision | Required before |
|---|---|
| U-GR-01 point account scope | Feature 03 authoritative point balance/spend semantics |
| U-GR-02 signed point-delta convention | Feature 03 ledger production writes |
| U-GR-03 historical rule/causation evidence | Feature 03 production point awards |
| U-GR-04 reversal linkage policy | Feature 04 production reversal |
| U-GR-06 participant status vocabulary or approved conservative subset | Feature 05 participant transitions |
| U-GR-08 inventory semantics | finite-inventory Reward activation/redemption in Features 07–08 |
| U-GR-09 reward fulfillment/effect contract | Feature 09 for each affected RewardType |
| U-GR-10 SH-119 owner | Feature 09 profile-boost/time-bound benefit |
| U-GR-13 delivery-on-time source owner | activating that Rule trigger |
| U-GR-14 redemption consent linkage requirement | production redemption compliance proof in Feature 08 |
| U-GR-15 taxable-value recognition moment | production SH-118 use in Feature 09 |
| U-GR-16 compensation/reopen rules | cancellation/reversal paths requiring compensation |

### Production provider readiness (CL-10-R007 / CL-10-R013)

This prerequisite applies to every affected production feature exit gate below. SH-009 `resolveActiveConsentVersion` and SH-029 `appendAuditEvent` remain Confirmed, but actual active-version resolution and durable audit proof require their provider architecture blockers to be resolved (Consent U-CL01-08; Audit U-17). Contract fakes can pass isolated contract tests, not production exit gates. Record contract-test readiness separately from production readiness for Consent, Audit, Hold, Tax, and every other required provider capability.

Hold-dependent production behavior additionally requires the Hold owner's approved target/action applicability and safe creation contracts before SH-011/012 integration is production-ready. `blockedByHoldId` is an association/evidence link, never current gate truth. Evaluate through SH-011; dependency unavailable must not become allow. The CL-10 owner performs its own resulting lifecycle transition; do not create a local hold table/evaluator or change the Hold owner's architecture here.

### Dependency interfaces

Production integrations require owner contracts for:

- Identity & Access;
- Role / Authority;
- Consent & Disclosure;
- authoritative source-event owners;
- Payment / Payout / Tax;
- Admin Review / Compliance Hold;
- Notification;
- Audit / Event Ledger;
- Observability / Ops;
- Privacy / Data Erasure.

### Interfaces that may initially be stubbed

For Module tests and early slices:

- Consent SH-008/009 may use a contract fake.
- Hold SH-011/012 may use a contract fake.
- Payment/Tax SH-019/118 may use a contract fake.
- Notification SH-041 may use a contract fake.
- Order/Profile/Review source events may use versioned fixtures until the owner interface is available.

Contract fakes must exactly model the intended public interface and must never become production repositories.

### Providers

No provider is a prerequisite for Features 01–08.

A future reward fulfillment provider is required only after U-GR-09 assigns an approved RewardType effect to this Module.

### Dependencies that do not block early deterministic slices

The following do not block Program/Rule/point/challenge/projection development:

- sweepstakes production legal approval;
- Stripe webhook traffic;
- live tax provider;
- Search/profile-boost effect;
- Track entitlement integration;
- gift-card/shipping/cash provider;
- shared fraud platform.

---

# IMPLEMENTATION PHASES

## Phase 1 — Contracts and Configuration Foundation

### 01 Module Contracts, Policy Skeleton, and Architecture Guards

#### Objective

Establish the Module's code boundary, public DTO/event/privacy contracts, dependency ports, stable error/decision vocabulary, and tests that prohibit cross-domain persistence before business mutations are implemented.

#### Observable Result

- The repository has a single `gamification-rewards` Module boundary following root conventions.
- Public contract types can be imported by tests/consumers without importing Prisma models.
- Dependency ports exist for actor, authority, consent, source events, holds, tax, notification, audit, privacy, and observability.
- A contract test suite rejects provider/Prisma leakage and records unresolved architecture blockers as explicit feature gates.

#### Cluster Build-Plan Link

Supports **CL-10 Feature 01 — Gamification Programs, Rules, and Disclosure Configuration** and establishes the boundary required by CL-10 Features 02–05.

#### Dependencies

- Root project overview/architecture/code standards.
- CL-10 architecture/build plan.
- current Prisma schema.
- Canonical Shared Operations Registry.
- Module architecture.
- No external provider required.

#### In Scope

- Create Module directory structure only for real responsibilities.
- Define bounded public command/query DTOs.
- Define source-event envelope expected by `recordEligibleActivity`.
- Define Gamification event schemas/envelopes according to root event conventions.
- Define dependency ports mapped to SH-### operations.
- Define Module decision/error categories.
- Define privacy owner contract adapter types.
- Define architecture-blocked result for unresolved behavior.
- Add tests that no public contract exports Prisma types or provider payloads.
- Add lint/import-boundary rules if root tooling supports Module boundaries.

#### Out of Scope

- Program writes.
- point writes.
- challenge/reward behavior.
- provider implementations.
- direct dependency Module implementations.
- schema changes to settle unresolved decisions.

#### Module-Owned Data

No new authoritative rows required.

Existing owned model names are referenced by repositories/contracts but not mutated yet.

#### Public Interfaces

Scaffold stable shapes for:

- `getGamificationProgram`;
- `recordEligibleActivity`;
- `getPointLedger`;
- `getPointBalance`;
- `joinChallenge`;
- `getLeaderboard`;
- `requestRewardRedemption`;
- `getRewardRedemption`;
- privacy executor/enumerator.

Exact code names may follow root conventions, but semantics must match Module architecture.

#### Shared Operations Used

- SH-001/002: represent actor/authorization dependency ports; no local auth helper.
- SH-008/009: consent dependency ports; no Consent repository.
- SH-011/012: hold dependency ports; no local blocked state.
- SH-019/118: tax dependency ports; no tax provider/model.
- SH-029/030: audit dependency ports.
- SH-041: notification dependency port.
- SH-044–048: idempotency/event/job abstractions.
- SH-095–098: privacy protocol.
- SH-115: projection contract.

**Prohibited duplicates:** all local substitutes named in Module Architecture §34.

#### Domain Logic

Only contract-level invariants:

- bounded DTOs;
- no Prisma/provider payloads in public APIs;
- no prize/drawing/winner types in Gamification command surface;
- stable `ARCHITECTURE_BLOCKED` result for unresolved production behavior;
- source-event contract requires event ID, type, version, occurredAt, subject/source refs.

#### Authorization / Compliance

No business mutation yet. Contract tests must require SH-001/002 context for protected operations.

#### Database / Transaction Behavior

- Verify current Prisma models/indexes are present in migrations.
- No migration solely for scaffolding.
- Repositories must be scoped to Module-owned tables.
- Add repository-interface tests that cross-domain models are absent.

#### Events / Jobs

- Define event schemas only.
- Do not run workers yet.
- Outbox implementation is platform-owned.

#### Provider Integration

None.

#### UI / Admin Surface

None in this feature.

#### Failure Behavior

- Import boundary violation -> test/lint failure.
- Missing canonical dependency -> contract fake permitted in tests, production adapter remains unbound.
- Unresolved architecture -> explicit blocker, not fallback behavior.

#### Tests

- Type/contract compilation.
- Import-boundary tests.
- Public DTO snapshot/shape tests.
- Error/reason-code tests.
- Event-envelope schema tests.
- Privacy contract shape tests.
- Regression: no Sweepstakes/Tax/Consent/Hold/Notification Prisma model imported by Module repositories.

#### Documentation Updates

- Update Module architecture if root folder conventions conflict with proposed layout.
- Record approved public names if repository conventions change them.
- Add a progress-tracker entry only if a tracker has been established; it is currently unavailable.

#### Acceptance Criteria

- One Module boundary exists.
- Public contracts contain no Prisma or provider-native types.
- Dependency ports reference canonical owners/SH IDs.
- Architecture-blocked conditions are representable.
- Tests enforce non-ownership.

#### Exit Gate

PASS only when typecheck/lint/contract tests pass and a reviewer can verify that a future command cannot reach another Module's Prisma repository through the new Module boundary.

---

### 02 Gamification Programs, Rules, and Disclosure Configuration

#### Objective

Implement owner-controlled Program and Rule configuration/lifecycle with declarative rule validation, terms-version references, authorization, audit, idempotency, and transactional events without awarding points yet.

#### Observable Result

- Authorized admin can create/edit a draft Program.
- Authorized admin can create/edit supported deterministic Rules.
- Rule validation rejects executable/unversioned payloads and chance-odds behavior.
- Program activation/pause/end follows the approved lifecycle and emits one owner event.
- Unsupported triggers cannot silently activate.

#### Cluster Build-Plan Link

Implements the Module portion of **CL-10 Feature 01**.

#### Dependencies

- SH-080 `manageVersionedRules` for immutable effective rule versions; U-GR-03 remains a separate historical-linkage blocker.

- Feature 01.
- `GamificationProgram`, `GamificationRule` and enums.
- SH-001, SH-002, SH-009, SH-008 where preview/proof is relevant, SH-029, SH-044, SH-046, SH-052, SH-053.
- inherited PR-CL10-03 ruleJson ruling.
- approved Program transition graph from Module architecture.

#### In Scope

- Program create/update.
- Rule create/update/activate/deactivate.
- Program lifecycle commands.
- typed/versioned `ruleJson` schema.
- timing validation.
- terms-version reference resolution.
- no-paid-prize-odds validation.
- admin list/detail queries.
- minimal admin configuration surface if root UI conventions permit.
- transactional event/audit integration.

#### Out of Scope

- applying rules to source events;
- PointLedgerEntry;
- challenges;
- rewards;
- user rewards portal;
- sweepstakes;
- tax/provider fulfillment.

#### Module-Owned Data

- `GamificationProgram`
- `GamificationRule`
- `GamificationProgramStatus`
- `GamificationRuleTrigger`

#### Public Interfaces

- `configureGamificationProgram`
- `configureGamificationRule`
- `transitionGamificationProgram`
- `getGamificationProgram`
- `listGamificationRules`

#### Shared Operations Used

**SH-080 — `manageVersionedRules` (Confirmed)**; each policy Module using the shared versioning mechanism. Invoke for Gamification rule versions/effective intervals at configuration and award evaluation. Gamification retains trigger meaning, points, applicability, validation, source qualification, and reward policy. Do not build a separate general versioning framework. Contract tests must prove immutable effective-version resolution; U-GR-03 historical linkage remains unresolved.

**SH-001:** resolve admin actor at command boundary.  
**SH-002:** authorize program/rule management.  
**SH-009:** resolve applicable terms version. Local policy decides which consent type applies.  
**SH-044:** idempotent create/update/transition.  
**SH-052:** stale edit protection where root persistence strategy supports expected versions.  
**SH-053:** lifecycle transition plumbing; transition graph remains local.  
**SH-029:** audit activation/pause/end and material rule changes.  
**SH-046:** transactional Program lifecycle events.

Prohibit local auth, role, consent-version, idempotency, transition, audit, or event-bus helpers.

#### Domain Logic

- Program timing must be coherent.
- `ruleJson` must include/resolve a supported schema version.
- Unknown fields/invalid schema are rejected.
- No expressions/functions/scripts are executed from `ruleJson`.
- Points configuration must satisfy the approved U-GR-02 convention before Rules are production-active; until resolved, draft configuration may persist but activation requiring point semantics remains architecture-blocked.
- `delivery_on_time` Rules remain inactive until U-GR-13.
- Rule cannot target PrizeEntry/PrizeWinning/odds fields.
- Program activation requires all activation-critical Rules to be valid and supported.

#### Authorization / Compliance

- Admin actor via SH-001/002.
- Terms/disclosure version comes from Consent owner.
- No ConsentLog write in this Module.
- Material activation audited.
- No entitlement baseline is introduced.

#### Database / Transaction Behavior

- Program/Rule mutation is transactional.
- Program transition + outbox event are one transaction.
- Rule edits use stale-write protection if expected version/updatedAt convention is approved.
- No new source-of-truth tables.

#### Events / Jobs

Emit:
- Program activated;
- Program paused;
- Program ended;
- material Rule activation/deactivation if root event policy requires it.

No Module worker yet beyond shared outbox dispatch.

#### Provider Integration

None.

#### UI / Admin Surface

Confirmed by registry/Cluster plan: minimal Admin Rewards configuration surface may include:

- Program list/status;
- create/edit Program;
- Rule list/editor;
- trigger selector;
- point value;
- terms-version reference;
- validation/activation errors;
- pause/end controls.

The UI must call owner commands; no direct data mutation.

#### Failure Behavior

- invalid rule/timing -> `INVALID_INPUT`;
- unsupported trigger -> `ARCHITECTURE_BLOCKED` or `SOURCE_EVENT_UNSUPPORTED`;
- missing required terms version -> `CONSENT_REQUIRED`/configuration denial;
- unauthorized -> `FORBIDDEN`;
- stale update -> `STALE_WRITE`;
- outbox dispatch outage after commit -> state remains committed; platform retries dispatch.

#### Tests

- Program lifecycle unit/state tests.
- Rule JSON schema tests.
- executable-payload rejection.
- no-paid-odds regression tests.
- authorization tests.
- SH-009 contract tests.
- integration: Program transition + outbox + audit.
- idempotent repeated transition.
- unsupported delivery-on-time activation denied.

#### Documentation Updates

- Record approved `ruleJson` schemas/versions.
- Update U-GR-02/U-GR-13 if decisions are resolved.
- Progress tracker.

#### Acceptance Criteria

- Draft Program/Rule works through owner services.
- Invalid/declarative violations are denied.
- Lifecycle transitions are enforced server-side.
- Terms version is externally resolved.
- One transition produces one authoritative state change/event/audit effect.
- No points are awarded.

#### Exit Gate

Production source-event behavior requires an approved bilateral producer contract covering event meaning/timing, subject, qualification inputs, and corrections. Unresolved triggers remain inactive, including `delivery_on_time`; no direct cross-domain Prisma reads or polling may substitute (CL-10-R004). Configuration tests must prove SH-080 reuse; they do not resolve U-GR-03 or satisfy actual Consent/Audit production readiness.

PASS when Program/Rule configuration is production-safe for supported triggers, all tests/build checks pass, and unresolved point/source semantics remain explicitly disabled rather than guessed.

---

## Phase 2 — Append-Only Point Truth

### 03 Authoritative Source Events to Exactly-Once Point Ledger

#### Objective

Turn approved authoritative source events into deterministic PointLedgerEntry effects exactly once per applicable Rule semantics.

#### Observable Result

- A versioned `order_completed` fixture/owner event produces the expected ledger effect.
- Delivering the same event repeatedly or concurrently does not duplicate the award.
- A point award can be traced to the source event and Rule semantics using the approved evidence strategy.
- No direct Order/Profile/Review Prisma read is required.

#### Cluster Build-Plan Link

Implements the core of **CL-10 Feature 02 — Source Events to Append-Only Point Ledger**.

#### Dependencies

- SH-080 `manageVersionedRules` for immutable effective rule versions; U-GR-03 remains a separate historical-linkage blocker.

- Features 01–02.
- SH-031, SH-044, SH-045, SH-046, SH-032/033/034, optionally SH-047/048 for async processing.
- approved source contract; `order_completed` is preferred first source because ownership is clear.
- **Architecture gates:** U-GR-01, U-GR-02, U-GR-03 must be resolved before authoritative production point writes.
- U-GR-13 blocks only `delivery_on_time`.

#### In Scope

- source-event validator/consumer;
- Rule selection/evaluation;
- one-effect-per-source-event+Rule semantics;
- PointLedgerEntry append;
- transactional outbox;
- event dedupe and command idempotency;
- point-award event;
- safe provenance metadata under approved schema;
- source event fixtures/contracts for Order first;
- worker integration if event consumption is asynchronous.

#### Out of Scope

- manual adjustments/reversals;
- point expiration;
- challenges except future event plumbing;
- reward redemption;
- cross-domain polling;
- mutable balance cache.

#### Module-Owned Data

- `PointLedgerEntry`
- `PointLedgerEntryType.earned`
- appropriate `PointLedgerEntrySource`
- `GamificationRule` read truth.

#### Public Interfaces

- `recordEligibleActivity`
- Gamification inbound event-handler contract
- `PointLedgerEntryAppended` outbound event

#### Shared Operations Used

**SH-080 — `manageVersionedRules` (Confirmed)**; each policy Module using the shared versioning mechanism. Invoke for Gamification rule versions/effective intervals at configuration and award evaluation. Gamification retains trigger meaning, points, applicability, validation, source qualification, and reward policy. Do not build a separate general versioning framework. Contract tests must prove immutable effective-version resolution; U-GR-03 historical linkage remains unresolved.

**SH-045:** claim source event by event ID + handler/version.  
**SH-044:** protect business command/effect replay.  
**SH-031:** append PointLedgerEntry using shared immutable mechanics.  
**SH-046:** publish point fact from same transaction.  
**SH-032/033/034:** correlation/logging/redaction.  
**SH-047/048/038:** if queue-backed, durable processing/retry/telemetry.  
**SH-037:** permanent dependency/worker failure evidence.

Do not build `ProcessedGamificationEvent`, local outbox, or custom retry queue.

#### Domain Logic

- Validate event ID/type/version before Rule evaluation.
- Match only active Program/Rules effective under the approved timing policy.
- One source event may produce multiple effects only for distinct applicable Rule semantic identities.
- Same source event + same Rule semantic identity must produce at most one effect.
- Required User subject must be present/resolved from trusted source event.
- Optional ProfessionalProfile/Order provenance is stored only as approved IDs.
- U-GR-02 determines signed delta storage.
- U-GR-03 determines how applied Rule version/source event proof is persisted.
- No Rule output may create or mutate PrizeEntry or chance odds.

#### Authorization / Compliance

This is typically system/event context rather than a user command.

- event authenticity derives from platform event infrastructure/owner contract;
- do not accept arbitrary client-generated "order completed" facts;
- no-paid-prize-odds invariant always applies.

#### Database / Transaction Behavior

Required transaction:

```text
dedupe/inbox claim
→ revalidate applicable owner state/config
→ append PointLedgerEntry
→ append outbox event
→ mark inbox/effect completion
→ commit
```

A crash cannot commit the ledger effect without replay-safe completion.

No update/delete of historical ledger rows.

#### Events / Jobs

Inbound:
- approved source Module event.

Outbound:
- PointLedgerEntry appended.

Worker:
- source-event processor through SH-047 if asynchronous.

Idempotency:
- event ID + handler/version;
- business effect includes Rule semantic identity.

#### Provider Integration

None.

#### UI / Admin Surface

None required beyond existing developer/admin inspection if root tooling supports it.

#### Failure Behavior

- duplicate event -> safe no-op/replay;
- malformed/unsupported event -> permanent failure/dead letter, no point write;
- unsupported trigger owner -> architecture-blocked;
- Rule invalid/inactive -> no effect with stable reason;
- DB transaction failure -> no partial effect;
- telemetry failure does not mutate point truth.

#### Tests

- Rule match/non-match.
- One approved event -> correct ledger.
- Duplicate event 2+ times -> one effect.
- Two workers same event -> one effect.
- Multiple distinct Rules -> one effect each.
- transaction crash/retry.
- unsupported event version.
- source event cannot be spoofed through public client route.
- no Sweepstakes record affected.
- outbound event payload minimization.

#### Documentation Updates

- Resolve/document U-GR-01/02/03 before production write code.
- Record approved source event contract/version.
- Update dependency public-interface references if source owner names differ.

#### Acceptance Criteria

- Exactly-once business effect is proven.
- Ledger row is authoritative and append-only.
- Source provenance is explainable under approved U-GR-03 strategy.
- No cross-domain repository dependency.
- Retry/dead-letter behavior observable.

#### Exit Gate

Production source-event behavior requires an approved bilateral producer contract covering event meaning/timing, subject, qualification inputs, and corrections. Unresolved triggers remain inactive, including `delivery_on_time`; no direct cross-domain Prisma reads or polling may substitute (CL-10-R004). Required Audit capability must satisfy the production provider readiness gate.

**FAIL CLOSED** unless U-GR-01, U-GR-02, and U-GR-03 are explicitly resolved in architecture.

After resolution, PASS only when concurrency/idempotency/integration tests demonstrate one point effect per source event+Rule semantics and all standard checks pass.

---

### 04 Point Ledger Queries, Manual Adjustments, Reversals, and Balance Semantics

#### Objective

Expose authorized point history/balance and implement privileged append-only corrections without permitting mutable balance truth.

#### Observable Result

- User/admin can query authorized ledger history.
- `getPointBalance` exactly matches ledger aggregation for fixture histories.
- Authorized admin can add an adjustment.
- Reversal works only under the approved linkage/policy and never edits the original row.
- High-risk correction uses audit and step-up where required.

#### Cluster Build-Plan Link

Completes the Module portion of **CL-10 Feature 02**.

#### Dependencies

- Feature 03.
- SH-001, SH-002, conditional SH-014, SH-029, SH-031, SH-044, SH-046.
- U-GR-01/02 already resolved.
- **U-GR-04 must be resolved before production reversal.**
- U-GR-05 may remain unresolved; point expiration is out of scope until approved.

#### In Scope

- `getPointLedger`;
- `getPointBalance`;
- balance breakdown/as-of semantics;
- manual adjustment command;
- reversal command/path after U-GR-04;
- audit/step-up integration;
- authorized user/admin read surfaces;
- point history admin inspection.

#### Out of Scope

- expiration worker;
- mutable balance projection;
- reward spend;
- tax;
- challenge/leaderboard.

#### Module-Owned Data

- existing `PointLedgerEntry`.

No new balance table/column.

#### Public Interfaces

- `getPointLedger`
- `getPointBalance`
- `appendManualPointAdjustment`

If reversal is exposed separately, exact name follows repository conventions; it remains append-only.

#### Shared Operations Used

**SH-001/002:** authorize subject/admin reads and adjustments.  
**SH-014:** high-risk value adjustment if root policy requires.  
**SH-029:** audit manual adjustment/reversal.  
**SH-031:** append correction entry.  
**SH-044:** idempotent correction.  
**SH-046:** correction point event.  
**SH-115:** not yet required unless an approved cached projection is introduced in Feature 06.

#### Domain Logic

- Balance is computed from ledger under U-GR-01/02.
- Adjustments require explicit reason and actor.
- Reversal references/identifies original effect under U-GR-04.
- No double reversal.
- Original rows are immutable.
- `note`/metadata is bounded and sanitized.
- No monetary/cash interpretation.

#### Authorization / Compliance

- User reads only authorized own point context.
- Admin/support broader reads/actions require SH-002.
- Manual value changes are audit-required.
- SH-014 applies if central security policy requires.
- No correction can create PrizeEntry.

#### Database / Transaction Behavior

- Read queries use indexes by User/time and optional approved account dimensions.
- Adjustment/reversal append is one transaction with outbox.
- Original row is never updated.
- Idempotency replay returns prior entry/result.

#### Events / Jobs

Outbound point-adjusted/reversed event via SH-046.

No new worker.

#### Provider Integration

None.

#### UI / Admin Surface

Where product surface exists:

- user point history/balance;
- admin ledger viewer;
- manual adjustment/reversal form with reason and confirmation.

UI never edits rows directly.

#### Failure Behavior

- unauthorized -> deny;
- step-up required -> remediation;
- invalid amount/type/source -> deny;
- reversal target absent/already reversed -> conflict/invalid state;
- unresolved U-GR-04 -> architecture-blocked;
- balance query lag is not applicable while computed directly from truth.

#### Tests

- ledger pagination/filter.
- balance fixtures.
- negative/positive combinations per U-GR-02.
- adjustment audit/idempotency.
- reversal no mutation.
- double reversal prevention.
- authorization.
- sensitive metadata sanitization.
- no wallet/cash semantics.

#### Documentation Updates

- record U-GR-04 resolution.
- if point expiration is approved later, update Module architecture before adding Feature work.

#### Acceptance Criteria

- balance equals authoritative ledger.
- corrections are append-only.
- user/admin boundaries work.
- duplicate correction does not duplicate effect.
- audit/step-up policy satisfied.

#### Exit Gate

PASS only when U-GR-04 is resolved for production reversal and all ledger/query/correction tests pass. U-GR-05 may remain deferred with expiration disabled.

---

## Phase 3 — Challenges and Rebuildable Projections

### 05 Challenge Participation and Completion

#### Objective

Implement Challenge configuration/participation/completion using owner lifecycle rules and route completion rewards through the standard point Rule pipeline.

#### Observable Result

- Admin can configure an approved Challenge under an active/draft Program.
- User can join an active eligible Challenge exactly once.
- Approved completion evidence moves participant to completed exactly once.
- Completion can trigger the existing `challenge_completed` Gamification rule path.
- Unsupported participant statuses cannot be written.

#### Cluster Build-Plan Link

Implements the Challenge portion of **CL-10 Feature 03 — Challenges, Balance Projection, and Leaderboards**.

#### Dependencies

- Features 02–04.
- `Challenge`, `ChallengeParticipant`, `ChallengeStatus`.
- SH-001, SH-002, SH-044, SH-045 for event-driven completion, SH-046, SH-053.
- **U-GR-06:** participant status vocabulary or explicit conservative subset must be approved.
- U-GR-07 advanced progress/rewardJson may remain deferred if initial challenges are binary completion.

#### In Scope

- Challenge create/update/lifecycle command.
- join command.
- binary/event-backed completion.
- participant list/read.
- challenge-completed internal event.
- integration into Feature 03 point pipeline.
- minimal admin configuration.
- user challenge query/surface if current product UI supports it.

#### Out of Scope

- arbitrary progress engine;
- executable challenge conditions;
- non-point `rewardJson` effects until U-GR-07;
- sweepstakes contests/drawings.

#### Module-Owned Data

- `Challenge`
- `ChallengeParticipant`
- `ChallengeStatus`

#### Public and Module-Internal Application Interfaces

Operations explicitly marked Module-internal below are application interfaces, not cross-Module public contracts. A future external consumer requires a stable contract in Module architecture first (CL-10-R006).

- Module-internal `configureChallenge`
- Module-internal `transitionChallenge`
- `joinChallenge`
- `completeChallengeParticipant`
- `listChallenges`
- `getChallenge`

#### Shared Operations Used

SH-001/002 actor/authorization.  
SH-044 command idempotency.  
SH-045 event dedupe for external completion evidence.  
SH-053 transition mechanics.  
SH-046 owner events.  
SH-029 audit material admin Challenge lifecycle actions if root policy requires.

#### Domain Logic

- Challenge dates/status must permit join/completion.
- `(challengeId,userId)` prevents duplicate participation.
- Only approved participant-status subset can be written.
- Completion writes once and sets `completedAt`.
- Completion point award uses `challenge_completed` through `recordEligibleActivity`; it does not directly append a special duplicate ledger path.
- `rewardJson` is null or restricted to the approved typed contract; no Reward/provider duplication.

#### Authorization / Compliance

- User can join only as permitted subject.
- Admin configuration authorized centrally.
- Challenge cannot be treated as chance drawing.
- No leaderboard rank -> automatic completion unless explicitly approved source evidence says so.

#### Database / Transaction Behavior

- join uses composite PK plus SH-044.
- completion transition is transaction-safe and idempotent.
- completion + outbox same transaction.
- point effect occurs through standard event/rule path and remains separately idempotent.

#### Events / Jobs

- ChallengeJoined.
- ChallengeCompleted.
- Optional evaluation worker for event-driven binary completion through SH-047/048 if asynchronous.

#### Provider Integration

None.

#### UI / Admin Surface

Admin:
- Challenge definition/status/dates;
- safe typed reward rule reference if approved.

User, if in current product surface:
- challenge list/detail;
- joined/completed state.

Do not invent a complex progress dashboard without product evidence.

#### Failure Behavior

- duplicate join -> existing participant.
- inactive/out-of-window -> invalid state.
- unsupported participant state -> architecture/validation denial.
- duplicate completion -> replay/no additional points.
- missing source evidence -> deny/manual review.

#### Tests

- Challenge lifecycle.
- participant allowed states.
- duplicate join.
- duplicate completion.
- completion -> exactly one point-rule effect.
- user/admin authorization.
- no sweepstakes behavior.
- `rewardJson` schema rejection.

#### Documentation Updates

- U-GR-06 resolution.
- U-GR-07 if advanced progress/reward semantics are approved.

#### Acceptance Criteria

- Join/completion truth works independently of projections.
- Completion is idempotent.
- Unsupported participant statuses are impossible through normal services.
- Point award uses existing Rule pipeline.

#### Exit Gate

PASS only after U-GR-06 is approved/implemented. Advanced progress may remain out of scope if U-GR-07 is explicitly deferred and initial Challenge contract is binary/event-backed.

---

### 06 Point Balance Projection and Leaderboards

#### Objective

Implement rebuildable point-balance and Leaderboard projections without changing source truth.

#### Observable Result

- `getPointBalance` may use an approved projection while preserving ledger authority.
- Leaderboard displays deterministic rank/points.
- Full rebuild yields the same result as incremental projection updates.
- Projection loss/corruption can be repaired without changing PointLedgerEntry.

#### Cluster Build-Plan Link

Completes **CL-10 Feature 03**.

#### Dependencies

- Features 03–05.
- `Leaderboard`, `LeaderboardEntry`.
- SH-115, SH-047/048, SH-038, SH-037.
- approved U-GR-01/02 accounting scope/math.

#### In Scope

- Leaderboard definition query/config if not completed in Feature 05.
- projection inclusion/ranking/tie/window policy.
- incremental projection update.
- full rebuild/backfill.
- checkpoint/version/lag reporting through shared projection conventions.
- `getLeaderboard`.
- optional approved point-balance cache/read model only if root architecture supports it.

#### Out of Scope

- Search/Typesense.
- point source mutation.
- sweepstakes odds/ranking.
- profile boost.
- generic analytics dashboard.

#### Module-Owned Data

- `Leaderboard`
- `LeaderboardEntry`
- no new authoritative point data.

#### Public Interfaces

- `getPointBalance`
- `getLeaderboard`
- `rebuildGamificationProjection`

#### Shared Operations Used

**SH-115:** canonical projection mechanism.  
**SH-047/048:** rebuild/update jobs.  
**SH-038/037:** queue/failure telemetry.  
**SH-044:** idempotent admin rebuild request.  
**SH-046:** optional projection-updated owner event only if useful; projection event does not replace source truth.

#### Domain Logic

- inclusion rules use PointLedgerEntry and approved challenge metrics only.
- tie/rank semantics deterministic.
- period window belongs to Leaderboard definition.
- projection version/checkpoint exposed for debugging.
- User/profile display fields are minimized and authorized.
- no rank affects PrizeEntry odds.

#### Authorization / Compliance

- leaderboard visibility follows product/Role policy.
- sensitive/private subject fields excluded.
- user cannot manipulate rank directly.
- projection does not infer external eligibility.

#### Database / Transaction Behavior

- upsert projection rows idempotently.
- respect `@@unique([leaderboardId,userId])`.
- full rebuild can replace projection contents safely without touching source ledger.
- checkpoint update follows SH-115 atomic/reconciliation semantics.

#### Events / Jobs

- incremental projection worker.
- full rebuild worker.
- lag/reconciliation telemetry.

#### Provider Integration

None.

#### UI / Admin Surface

- leaderboard read surface if current product UI includes it;
- admin/dev projection checkpoint/rebuild status.

No Search UI.

#### Failure Behavior

- projection job failure -> source truth intact; retry/rebuild.
- stale projection -> expose lag/as-of, not fabricated freshness.
- rank conflict -> rebuild/reconcile.
- source inconsistency -> fail and surface operational evidence.

#### Tests

- rank/tie/window units.
- incremental vs full rebuild equivalence.
- deleted projection -> rebuild equivalence.
- concurrent update/rebuild.
- authorization/privacy exposure.
- point ledger unchanged.
- no Search/Sweepstakes writes.

#### Documentation Updates

Record ranking/tie/inclusion policy once finalized.

#### Acceptance Criteria

- projection is fully rebuildable.
- balance matches ledger truth.
- leaderboard deterministic.
- projection outage does not block/corrupt point truth.

#### Exit Gate

PASS when rebuild equivalence, lag/failure behavior, concurrency, privacy, and standard build checks all pass.

---

## Phase 4 — Deterministic Reward Economy

### 07 Reward Catalog, Terms, and Activation Gates

#### Objective

Implement Reward catalog lifecycle and activation validation while keeping unsupported effects and unresolved finite inventory safely inactive.

#### Observable Result

- Authorized admin can create/edit draft Rewards.
- Supported configuration can become active under owner lifecycle.
- Unsupported RewardType effect returns an explicit reason and cannot be production-active.
- Finite-inventory Reward remains blocked until U-GR-08.
- Historical existing redemptions are unaffected by later catalog edits.

#### Cluster Build-Plan Link

Implements catalog half of **CL-10 Feature 04 — Reward Catalog and Atomic Redemption Core**.

#### Dependencies

- Features 01–06.
- `Reward`, `RewardType`, `RewardStatus`.
- SH-001/002/009/029/044/052/053.
- U-GR-08 for finite inventory activation.
- U-GR-09 for each effect type.
- U-GR-10 for profile boost.
- U-GR-11 if any plan-gated behavior is proposed.

#### In Scope

- Reward create/update.
- lifecycle transition.
- typed value/currency/pointCost/inventory/terms validation.
- activation support matrix by RewardType.
- terms-version resolution.
- no-paid-prize-odds validation.
- admin Reward catalog UI/query.
- user Reward listing/query with safe availability facts.

#### Out of Scope

- redemption transaction;
- fulfillment;
- cash transfer;
- Search boost;
- platform-credit ledger;
- gift-card/shipping provider;
- sweepstakes.

#### Module-Owned Data

- `Reward`
- `RewardType`
- `RewardStatus`

#### Public and Module-Internal Application Interfaces

Operations explicitly marked Module-internal below are application interfaces, not cross-Module public contracts. A future external consumer requires a stable contract in Module architecture first (CL-10-R006).

- `configureReward`
- Module-internal `transitionReward`
- `listRewards`
- `getReward`

#### Shared Operations Used

SH-001/002 admin authorization.  
SH-009 terms version.  
SH-044 idempotency.  
SH-052 stale edits.  
SH-053 lifecycle plumbing.  
SH-029 material activation/retirement audit.

No SH-005 entitlement check unless U-GR-11 is resolved.

#### Domain Logic

- Reward status transition follows Module architecture.
- pointCost/value/inventory fields pass typed validation.
- activation requires an approved effect contract where the type needs execution.
- finite inventory requires U-GR-08 before activation.
- profile_boost requires U-GR-10/SH-119 approval.
- cash_bonus remains external financial effect; no local payout.
- platform_credit remains unsupported until ledger/effect owner defined.
- badge must not imply TrustBadge verification.
- physical_prize remains deterministic reward, not PrizeWinning.
- Reward never changes sweepstakes odds.

#### Authorization / Compliance

- admin config uses SH-002.
- terms version externally owned.
- activation fail-closed on unsupported/legal/compliance gaps.
- no local premium/entitlement flag.

#### Database / Transaction Behavior

- Reward mutation transactional.
- lifecycle transition + event/audit if material.
- later redemptions snapshot value; catalog update does not rewrite them.

#### Events / Jobs

- Reward activated/paused/retired event if root event policy requires.
- no fulfillment worker yet.

#### Provider Integration

None.

#### UI / Admin Surface

Confirmed admin rewards dashboard slice:
- type/status;
- point cost;
- value/currency;
- inventory field with explicit unresolved/unsupported state where applicable;
- terms version;
- effect support status;
- activation errors.

User Reward listing only if current product surface requires it.

#### Failure Behavior

- unsupported type -> `UNSUPPORTED_REWARD_EFFECT`;
- finite inventory unresolved -> `ARCHITECTURE_BLOCKED`;
- terms missing -> configuration denial;
- stale update -> conflict;
- unauthorized -> forbidden.

#### Tests

- lifecycle.
- activation support matrix.
- no-paid-odds.
- badge != TrustBadge.
- profile boost blocked without SH-119.
- cash/platform credit do not invoke payment/local ledger.
- finite inventory blocked.
- terms version contract.
- value/catalog edit behavior.

#### Documentation Updates

Resolve/update U-GR-08/09/10/11 only through architecture approval.

#### Acceptance Criteria

- Catalog works for draft/configuration.
- Only approved types/configurations activate.
- Unsupported effects fail closed.
- no neighboring truth created.

#### Exit Gate

PASS for catalog/configuration when supported activation paths are correctly enforced. Finite-inventory or unsupported effect types remain explicitly disabled and do not block catalog Feature completion.

---

### 08 Atomic Reward Redemption Core

#### Objective

Implement self-service RewardRedemption creation with consent/hold gates and atomic point spend, without pretending unsupported fulfillment has occurred.

#### Observable Result

- Eligible User requests a supported Reward redemption.
- Required points are spent exactly once.
- RewardRedemption is created exactly once with historical value snapshot.
- Concurrent requests cannot overspend the same point account.
- Consent/hold denial produces no partial redemption/spend.
- Redemption remains in a valid pending state until downstream tax/effect requirements are satisfied.

#### Cluster Build-Plan Link

Completes **CL-10 Feature 04**.

#### Dependencies

- Features 04 and 07.
- SH-001, SH-002, SH-008, SH-011, SH-044, SH-056, SH-031, SH-046.
- U-GR-01/02 already resolved.
- U-GR-08 for finite-inventory Rewards only.
- **U-GR-14 must settle required persisted consent evidence before production redemption is enabled.**
- U-GR-09 determines which Reward types can proceed beyond pending states, but initial redemption core can keep effects pending.

#### In Scope

- reward redemption eligibility composition;
- exact consent proof query;
- hold check;
- point sufficiency;
- atomic spend + redemption;
- value snapshot;
- initial redemption state;
- self/admin safe reads;
- idempotency and concurrency;
- domain event.

#### Out of Scope

- tax readiness/reporting;
- provider fulfillment;
- profile boost execution;
- cash payout;
- platform credit;
- cancellation/reversal compensation beyond approved U-GR-16;
- finite inventory unless U-GR-08 resolved.

#### Module-Owned Data

- `RewardRedemption`
- `PointLedgerEntry` with `source=reward_redemption`
- `Reward` read.

#### Public and Module-Internal Application Interfaces

Operations explicitly marked Module-internal below are application interfaces, not cross-Module public contracts. A future external consumer requires a stable contract in Module architecture first (CL-10-R006).

- `evaluateRewardRedemptionEligibility`
- `requestRewardRedemption`
- `getRewardRedemption`
- Module-internal `listRewardRedemptions` if admin/user product surface requires it.

#### Shared Operations Used

**SH-001/002:** actor/resource authorization.  
**SH-008:** exact terms proof.  
**SH-011:** active hold decision.  
**SH-044:** idempotent redemption command.  
**SH-056:** point/inventory reservation under approved semantics.  
**SH-031:** append point spend.  
**SH-046:** redemption requested event.  
**SH-029:** exceptional/admin redemption actions only; normal self-service need follows root audit policy.

#### Domain Logic

- Reward active and effect support sufficient for redemption to enter a truthful pending state.
- Program active where Reward belongs to a Program and owner policy requires it.
- consent proof matches required version.
- hold does not block request.
- point sufficiency uses U-GR-01 account scope and U-GR-02 delta math.
- `RewardRedemption.valueCents/currency` snapshots approved current Reward value.
- point spend refers to redemption.
- initial state remains `pending_confirmation` unless approved tax classification requires `pending_tax`.
- never mark `fulfilled` in this feature.
- no PrizeEntry or odds effect.

#### Authorization / Compliance

- User redeems only permitted own subject context.
- admin override not part of normal path.
- consent proof externally owned.
- hold state externally owned.
- U-GR-14 decides persistent proof linkage/snapshot requirement.

#### Database / Transaction Behavior

After external gates are evaluated safely, authoritative transaction:

```text
SH-044 claim
→ SH-056 acquire point/inventory reservation
→ re-read Reward/point availability
→ create RewardRedemption
→ append point-spend PointLedgerEntry
→ commit approved inventory effect if applicable
→ append outbox event
→ commit
```

Any failure rolls back all authoritative writes.

#### Events / Jobs

Emit RewardRedemptionRequested.

No fulfillment job yet.

#### Provider Integration

None.

#### UI / Admin Surface

User, if current product surface supports it:
- reward detail/point cost;
- current balance;
- confirmation;
- resulting status/next action.

Admin:
- redemption queue/detail.

No provider/tax UI.

#### Failure Behavior

- insufficient points -> no write;
- duplicate idempotency -> original result;
- concurrent overspend -> one valid winner, others conflict/insufficient;
- consent missing -> no write;
- hold blocked -> no write or approved owner blocked path only if architecture specifies;
- finite inventory unresolved -> architecture-blocked;
- unsupported effect -> cannot promise fulfillment.

#### Tests

- atomic redemption+spend.
- duplicate idempotency.
- two concurrent requests.
- consent/hold contract denials.
- Reward edit after redemption leaves historical value unchanged.
- no fulfilled state.
- no Sweepstakes/Payment/Search/Track writes.
- rollback on failure between redemption and ledger append.

#### Documentation Updates

- record U-GR-14 decision.
- if finite inventory enabled, update U-GR-08 and reservation proof architecture.
- progress tracker.

#### Acceptance Criteria

- one request -> one redemption + one spend.
- no partial effects.
- point overspend race prevented.
- value snapshot stable.
- status truthful/pending.
- external proofs remain source-owned.

#### Exit Gate

Hold-dependent production behavior is BLOCKED until the approved Hold target/action applicability and creation contracts and real provider capability are available; the production provider readiness prerequisite above applies (CL-10-R007). U-GR-01/02/14, U-GR-08 for finite inventory, U-GR-09 for enabled effects, and U-GR-16 for enabled compensation remain unresolved production prerequisites; generic metadata does not establish historical consent proof.

PASS only when U-GR-14 is resolved for production compliance proof, atomicity/concurrency tests pass, and unsupported inventory/effects remain fail-closed.

---

## Phase 5 — Cross-Module Reward Gates and Fulfillment Effects

### 09 Tax, Compliance Hold, Notification, and Approved Reward-Effect Bridges

#### Objective

Connect RewardRedemption to Payment/Tax, ComplianceHold, Notification, and at least the approved deterministic fulfillment/effect contracts without transferring their truth into Gamification.

#### Observable Result

- Tax-sensitive redemption waits in a truthful pending/blocked state until Payment/Tax returns sufficient readiness.
- Active ComplianceHold prevents prohibited transition/fulfillment.
- Recognized reward value is reported once through SH-118 at the approved recognition moment.
- Notification is requested after meaningful owner transitions.
- A RewardType with an approved effect contract can complete through evidence returned to `transitionRewardRedemption`.
- Unsupported RewardTypes remain unfulfillable.

#### Cluster Build-Plan Link

Implements **CL-10 Feature 05 — Reward Tax, Hold, Fulfillment, and Deterministic Benefit Bridges**.

#### Dependencies

- Feature 08.
- SH-019, SH-011/012, SH-118, SH-041, SH-047/048, SH-037/038, SH-029/030.
- U-GR-09 for each effect being enabled.
- U-GR-10 for profile boost/SH-119.
- U-GR-15 for taxable-value recognition.
- U-GR-16 for cancellation/reversal compensation.
- Provider contract only if a provider is explicitly owned.

#### In Scope

- tax readiness composition;
- `pending_tax`/approved/blocked mapping;
- reportTaxableValue job;
- hold request/evaluation;
- notification requests;
- owner transition service;
- effect router that only routes approved RewardTypes;
- approved downstream effect contract(s);
- retry/dead-letter/operational failure;
- minimal admin redemption compliance/fulfillment queue.

#### Out of Scope

- tax provider/filing;
- ComplianceHold lifecycle/release;
- Notification provider;
- Search implementation;
- Track billing;
- unapproved gift-card/shipping/cash/provider;
- generic fulfillment status vocabulary;
- generic fraud platform.

#### Module-Owned Data

- `RewardRedemption`
- existing value/proof reference fields.
- no new provider model unless U-GR-09 explicitly approves it.

#### Public Interfaces

- `transitionRewardRedemption`
- internal `routeRewardEffect`
- downstream SH-019/118/011/012/041
- conditional SH-119
- optional `RewardFulfillmentPort` only if approved.

#### Shared Operations Used

**SH-019:** external financial/tax readiness.  
**SH-011/012:** hold gate/escalation.  
**SH-118:** taxable-value handoff.  
**SH-041:** communication request.  
**SH-047/048:** durable tax/effect jobs.  
**SH-037/038:** operational failure/queue telemetry.  
**SH-029/030:** material admin/fulfillment audit and sensitive reads.  
**SH-119:** only after ownership approval for temporary deterministic benefit.  
**SH-061/062:** only if Gamification becomes explicit provider owner.

#### Domain Logic

- determine whether Reward needs tax gate using approved Reward policy, not hardcoded tax regime.
- map SH-019 result into local transition decision.
- report value through SH-118 once at U-GR-15 recognition moment.
- `cash_bonus`: financial transfer executed by Payment/Payout/Tax; Gamification consumes outcome.
- `profile_boost`: requires approved SH-119 owner/effect; no direct Search write.
- `platform_credit`: disabled until owner ledger/effect defined.
- `badge`: disabled from implying TrustBadge; activation/fulfillment only after badge effect owner defined.
- `gift_card`, `physical_prize`, `other`: require explicit effect/provider/manual proof contract.
- provider/downstream result never directly writes status.
- `fulfilled` only after owner service validates evidence.
- reversal/cancel compensation follows U-GR-16.

#### Authorization / Compliance

- admin transition/fulfillment actions authorized.
- step-up via SH-014 if root policy requires.
- hold rechecked immediately before fulfillment.
- tax readiness rechecked where required.
- no reward effect alters sweepstakes odds.
- sensitive tax/financial view uses SH-030 as required.

#### Database / Transaction Behavior

- each owner transition uses SH-044/053 and optimistic concurrency.
- SH-118 report is idempotent by redemption + recognition version.
- effect request is idempotent by redemption + effect version.
- `fulfilledAt` set only with approved evidence.
- no direct update from callback adapter.

#### Events / Jobs

- tax-value report worker.
- approved effect/fulfillment worker.
- retry/dead-letter.
- RedemptionStatusChanged/Fulfilled/Reversed events.
- notification requests after commit.

#### Provider Integration

Only if U-GR-09 assigns provider ownership:
- provider-neutral port;
- server-side credentials;
- SH-059/060 for webhooks;
- SH-061 translation;
- SH-062 reconciliation;
- normalized evidence only into owner command.

Otherwise no provider code exists here.

#### UI / Admin Surface

Admin redemption queue may show:
- current status;
- safe hold reason/reference;
- tax action required;
- supported/unsupported effect;
- retry/manual-review state.

Do not expose raw TaxProfile/provider payloads.

#### Failure Behavior

- Tax unavailable -> pending state + retry; never auto-approve.
- hold active -> blocked/denied according to transition policy.
- SH-118 failure -> retry, no fabricated tax completion.
- Notification failure -> domain truth unchanged.
- effect provider/downstream failure -> not fulfilled; retry/manual review.
- unknown provider status -> normalized manual review.
- unapproved RewardType -> `UNSUPPORTED_REWARD_EFFECT`.
- SH-119 unresolved -> profile boost remains disabled.

#### Tests

- SH-019 contract mapping.
- active hold blocks fulfillment.
- taxable value reported once.
- duplicate fulfillment result.
- Payment/Tax unavailable.
- Notification failure.
- provider/effect retry if applicable.
- unknown provider status if applicable.
- `fulfilled` only after approved evidence.
- no Search/Track/Payment status owned locally.
- reversal/cancellation tests after U-GR-16.

#### Documentation Updates

- U-GR-09 effect support matrix.
- U-GR-10 if SH-119 approved.
- U-GR-15 recognition moment.
- U-GR-16 compensation behavior.
- provider ownership and dedupe/reconciliation if added.

#### Acceptance Criteria

- external gates influence local decision without transferring truth.
- recognized value handoff exactly once.
- at least one explicitly approved Reward effect can reach `fulfilled`, **or** the feature remains architecture-blocked rather than inventing an effect.
- unsupported types remain safe/inactive.
- failures do not fabricate fulfillment.

#### Exit Gate

Production tax-sensitive fulfillment requires approved tax-specific SH-019 usage with Payment; generic financial readiness is not reward/prize tax clearance. SH-118 reporting requires the source owner's approved recognition point and required subject, value/currency, jurisdiction, source identity, date, valuation evidence, and idempotency contract. Keep unresolved paths disabled (CL-10-R005).

Hold-dependent production behavior is BLOCKED until the approved Hold target/action applicability and creation contracts and real provider capability are available; the production provider readiness prerequisite above applies (CL-10-R007). U-GR-16/17 compensation/fulfillment proof must be approved for each enabled path; fakes prove orchestration tests only.

PASS only when U-GR-15 is resolved and every RewardType enabled for fulfillment has an approved U-GR-09 contract. If no effect contract is approved, the orchestration may be implemented/tested with fakes, but production fulfillment portion remains **FAIL / BLOCKED** and must be reported as such.

---

## Phase 6 — Privacy, Audit, and Operational Completion

### 10 Privacy Executor, Audit Completeness, and Operational Telemetry

#### Objective

Make Gamification a correct participant in Privacy / Data Erasure, Audit, and Observability without creating parallel workflows or operational truth.

#### Observable Result

- Privacy can enumerate Gamification subject data.
- Approved erase/anonymize/retain/export instructions execute idempotently.
- retention-required Reward/ledger records return owner facts rather than being deleted blindly.
- material admin actions have Audit proof.
- workers expose safe queue/failure telemetry.
- logs/metrics pass sensitive-data redaction tests.

#### Cluster Build-Plan Link

Supports **CL-10 Feature 10 — Cross-Cluster Contract Proof** and the Gamification side of CL-10 privacy/audit/ops requirements.

#### Dependencies

- The owner target/executor contract in Module architecture Section 28 (CL-10-R015); unresolved registration/disposition details block their production execution.

- Features 03–09 as applicable.
- SH-095–098.
- SH-029/030.
- SH-032–038.
- Privacy owner contract.
- U-GR-12 generic fraud owner may remain unresolved; no generic fraud platform required.

#### In Scope

- subject-data enumeration.
- privacy action executor.
- retention-fact evaluator.
- anonymization maps.
- export serializer contribution.
- projection removal/rebuild after subject anonymization where applicable.
- audit coverage matrix.
- telemetry fields/metrics.
- worker failure/queue instrumentation.
- privacy/audit/observability tests.

#### Out of Scope

- PrivacyRequest/DataErasureJob UI/lifecycle.
- DataRetentionExemption creation by Gamification.
- generic Ops dashboard.
- generic fraud risk system.
- tax/provider deletion outside this Module.

#### Module-Owned Data

Subject-bearing:
- PointLedgerEntry;
- ChallengeParticipant;
- LeaderboardEntry;
- RewardRedemption;
- future owned provider refs if approved.

Configuration records reviewed for incidental personal free text.

#### Public Interfaces

- SH-096 subject data enumerator implementation.
- SH-095 privacy instruction executor.
- SH-097 retention-facts provider.
- SH-098 field-mapping integration.
- audit/telemetry hooks internal to commands/workers.

#### Shared Operations Used

SH-095/096/097/098 privacy protocol.  
SH-029/030 audit/sensitive access.  
SH-032/033/034 request/log/redaction.  
SH-037/038 failure/queue telemetry.  
SH-047/048 for async privacy work if needed.  
SH-115 to rebuild projections after privacy changes.

#### Domain Logic

- enumerate all subject-linked owned records.
- return supported disposition and retention candidate.
- preserve tax/fraud/security/fulfillment evidence only under approved retention decision.
- anonymize projections/data fields without breaking required retained relations.
- remove/rebuild LeaderboardEntry where privacy outcome requires.
- free-text metadata is minimized and scrubbed where allowed.
- no provider resource deletion is attempted unless this Module owns the provider reference.

#### Authorization / Compliance

Privacy commands arrive from trusted Privacy orchestration, not arbitrary user route.

Audit access remains authorized.

Sensitive tax/financial admin reads use SH-030 if required.

#### Database / Transaction Behavior

- each privacy target execution idempotent.
- bulk operations cursor/batch rather than unbounded transaction.
- retained outcome returns reason/evidence.
- projection rebuild separate from source erasure but correlated.
- no direct PrivacyRequest/DataErasureJob writes.

#### Events / Jobs

- privacy execution job if owner protocol is async.
- projection rebuild after relevant changes.
- failure/dead-letter telemetry.

No new domain event unless Privacy contract requires owner completion event.

#### Provider Integration

None unless future Gamification-owned provider is introduced; then Privacy deletion behavior must be added to its approved adapter.

#### UI / Admin Surface

No Module privacy UI required.

Admin diagnostics may display safe privacy executor/failure status through existing Ops owner surfaces, not a local Ops system.

#### Failure Behavior

- retention required -> return retained disposition, not error.
- transient DB failure -> retry.
- unsupported field mapping -> manual review/fail closed.
- external provider not owned -> return delegated/not-owned result.
- telemetry unavailable -> business/privacy result remains authoritative but operational issue reported per platform policy.

#### Tests

- subject enumeration completeness.
- idempotent erase/anonymize.
- retention result.
- export serializer.
- leaderboard projection privacy behavior.
- audit coverage.
- sensitive access logging where required.
- telemetry redaction.
- no local privacy/ops tables.

#### Documentation Updates

- finalized retention/anonymization mappings.
- any provider privacy behavior.
- progress tracker.

#### Acceptance Criteria

- Privacy can complete its owner protocol without direct Gamification table rewrites.
- retained evidence is not accidentally deleted.
- audit/ops evidence is complete and distinct from domain truth.
- redaction tests pass.

#### Exit Gate

Production Privacy coverage requires the owner-specific Section 28 target contract: approved target registration/identity and source-version strategy; subject-scoped descriptors/serialization; SH-097 facts; approved per-target SH-095/098 actions; canonical retained/skipped/failure/results with idempotency and evidence. Contract tests must reject unsupported owner/target mappings and prove no generic crawler or local Privacy workflow. CL-10-R014 retention dispositions and CL-10-R015 bilateral target details remain unresolved until approved. Required Audit implementation must satisfy the production provider readiness gate.

PASS when Privacy contract tests, audit matrix, worker telemetry, redaction tests, and standard quality checks pass.

---

# MODULE INTEGRATION PHASE

## Phase 7 — Neighbor Contract Proof

### 11 Public-Contract Integration Across Gamification Neighbors

#### Objective

Prove the Module works through public contracts with its major neighboring Modules and canonical shared capabilities without reaching into neighboring source tables.

#### Observable Result

A contract/integration environment can execute the supported deterministic journey:

```text
authoritative Order/Profile/Review event
→ exactly-once point award
→ point query/projection
→ Challenge/Leaderboard effect where configured
→ Reward visibility
→ atomic RewardRedemption
→ Consent/Hold/Tax decisions where configured
→ Notification/Audit requests
→ Privacy enumeration/execution
```

Each dependency can be replaced by a contract fake without changing Gamification domain code.

#### Cluster Build-Plan Link

Implements the Gamification portion of **CL-10 Feature 10 — Cross-Cluster Contract Proof**.

#### Dependencies

- Features 01–10.
- public contracts or production-like contract fakes for Identity, Role, Consent, Order, Review, Professional Eligibility, Payment/Tax, Holds, Notification, Audit, Observability, and Privacy.
- all architecture blockers required by the specific tested behavior must be resolved.

#### In Scope

- provider/consumer contract tests for direct dependencies;
- source-event version compatibility;
- end-to-end owner-service integration with contract fakes;
- verification that public DTOs remain bounded;
- verification that no cross-domain Prisma access is needed;
- notification/audit/tax/hold request integration;
- privacy protocol integration;
- test wiring for conditional reward-effect contract only if approved.

#### Out of Scope

- production stress/race hardening beyond the integration scenarios;
- Sweepstakes / Prize implementation;
- unapproved RewardTypes/providers;
- global Search implementation;
- generic fraud platform;
- new architecture decisions.

#### Module-Owned Data

All current Module-owned records may participate, but no ownership or schema meaning changes.

#### Public Interfaces

Contract-test every interface in Module Architecture §12 that is enabled:

- configuration/lifecycle;
- point event/ledger/balance;
- Challenge;
- Leaderboard;
- Reward catalog/redemption;
- privacy executor;
- emitted owner events.

#### Shared Operations Used

Prove correct consumption of:

- SH-001/002;
- SH-008/009;
- SH-011/012;
- SH-014 where configured;
- SH-019;
- SH-029/030;
- SH-031–034;
- SH-037/038;
- SH-041;
- SH-044–048;
- SH-051–053/056;
- SH-095–098;
- SH-115;
- SH-118;
- SH-119 only if approved.

Integration tests must fail if a local duplicate substitutes for the canonical contract.

#### Domain Logic

Verify boundary behavior:

- source owner emits fact; Gamification decides points;
- external Consent/Hold/Tax decisions are inputs, not local truth;
- RewardRedemption remains owner state;
- Notification/Audit/Observability side effects do not alter domain result;
- Search/Track/Sweepstakes effects remain absent unless explicitly approved;
- no-paid-prize-odds invariant survives all integration paths.

#### Authorization / Compliance

Contract scenarios include:

- own vs other User point/redemption reads;
- admin Program/Rule/Reward configuration;
- manual point adjustment;
- consent-required redemption;
- hold-blocked redemption;
- tax-pending redemption;
- sensitive access audit where root policy requires;
- privacy disposition.

#### Database / Transaction Behavior

Integration tests use the real Gamification repository/database.

Neighbor data enters only through public event/query fixtures/adapters.

Verify authoritative Gamification writes plus outbox transaction boundaries, but reserve deeper contention/stress scenarios for Feature 12.

#### Events / Jobs

- source-event consumer contract;
- outbox consumer contract;
- tax/notification/hold/audit calls;
- privacy owner protocol;
- approved effect job contract if applicable.

#### Provider Integration

No provider test is required unless U-GR-09 explicitly assigns a provider to Gamification.

Payment/Tax/Notification providers remain tested in their owners; Gamification tests their public contract.

#### UI / Admin Surface

Run contract-backed workflow verification for only the admin/user surfaces implemented earlier.

No new UI.

#### Failure Behavior

Verify bounded behavior for:

- dependency unavailable;
- incompatible event version;
- consent missing;
- hold blocked;
- tax review required;
- unsupported Reward effect;
- architecture-blocked behavior.

No raw external error leaks.

#### Tests

- consumer/provider contract tests;
- real Gamification DB + dependency fakes;
- inbound event version tests;
- outbound event schema tests;
- authorization/compliance integration;
- privacy protocol integration;
- no direct Prisma dependency static/import check;
- deterministic activity -> redemption integration path.

#### Documentation Updates

- update dependency interface versions when actual owners differ from fixtures;
- record any legitimate contract change in Module architecture;
- progress tracker.

#### Acceptance Criteria

- Every direct dependency is consumed through a named public contract/SH operation.
- Full supported deterministic flow works without neighboring Prisma access.
- External failure/denial returns stable local result.
- No neighboring truth is copied.

#### Exit Gate

The PASS below establishes isolated Module contract/integration-test readiness only when fakes are used. It cannot satisfy a production Module or Cluster exit gate for unresolved provider capabilities (CL-10-R013).

PASS when all dependency contract tests and the complete supported deterministic integration journey pass against the real Gamification repository with public-interface adapters/fakes only.

---

# MODULE HARDENING PHASE

## Phase 8 — Security, Replay, Concurrency, Reconciliation, and Production Verification

### 12 Gamification Production Hardening

#### Objective

Prove the supported Module subset remains correct under replay, races, stale writes, worker outages, projection loss, privacy actions, dependency/provider failures, migrations, and production-like load.

#### Observable Result

- Duplicate events/commands produce one business effect.
- Concurrent redemption cannot overspend points.
- Projection deletion/rebuild returns identical results.
- Worker retry/dead-letter leaves valid domain state.
- Dependency outage cannot fabricate approval/fulfillment.
- Unsupported inventory/effects remain disabled.
- Production migration and performance smoke checks pass.

#### Cluster Build-Plan Link

Implements the Gamification portion of **CL-10 Feature 11 — CL-10 Production Hardening**.

#### Dependencies

- Feature 11.
- all prior feature exit gates PASS for enabled behavior.
- production-like database/migrations.
- production-like shared operation adapters.
- approved provider adapter only if one is actually enabled.

#### In Scope

- command/event replay;
- source-event race testing;
- point-spend/redemption contention;
- stale Program/Rule/Reward/Redemption transitions;
- projection rebuild/incremental race;
- queue crash/retry/dead-letter/replay;
- tax/hold/notification outages;
- approved provider timeout/unknown status/reconciliation;
- privacy replay/retention;
- audit completeness;
- telemetry redaction;
- migration/backfill safety;
- rate-limit integration where root controls exist;
- performance smoke tests on indexed hot paths;
- final prohibited-duplicate scan.

#### Out of Scope

- implementing unresolved architecture;
- Sweepstakes / Prize hardening;
- selecting a new provider;
- adding a global fraud engine;
- changing Cluster sequencing;
- turning unsupported RewardTypes on to make tests pass.

#### Module-Owned Data

All Module-owned records may participate. No ownership change is permitted.

#### Public Interfaces

Stress/replay every enabled command/query/event/privacy interface.

No new public interface should be required solely for test convenience.

#### Shared Operations Used

Hardening must prove correct use of:

- SH-044 command idempotency;
- SH-045 event dedupe;
- SH-046 outbox;
- SH-047/048 durable job/retry;
- SH-051 aggregate lock;
- SH-052 optimistic concurrency;
- SH-053 lifecycle transitions;
- SH-056 atomic reservation;
- SH-115 projection rebuild;
- SH-037/038 operational failure/queue telemetry;
- all earlier auth/consent/hold/tax/audit/privacy contracts.

#### Domain Logic

Re-verify all invariants under concurrency/failure:

- one source event + Rule semantics -> at most one effect;
- point ledger append-only;
- balance deterministic;
- Challenge completion cannot double-award;
- Reward activation support matrix enforced;
- redemption atomicity;
- downstream owner evidence required before local transition;
- no paid prize odds.

#### Authorization / Compliance

- concurrent/duplicate requests cannot bypass authorization.
- step-up session expiry cannot be bypassed by retry where applicable.
- Consent proof is re-evaluated as architecture requires.
- active/new hold before fulfillment prevents transition.
- tax-pending/blocked cannot become fulfilled.
- sensitive reads generate required SH-030 proof.
- privacy retention rules remain enforced during replay.

#### Database / Transaction Behavior

Required hardening scenarios:

1. Two workers process the same source event simultaneously.
2. Worker crashes after inbox claim but before ledger commit.
3. Worker crashes after business commit but before acknowledgment.
4. Same command idempotency key arrives concurrently.
5. Two Reward redemptions compete for the same point account.
6. Finite inventory race only if U-GR-08 is approved; otherwise verify activation remains denied.
7. Stale Program/Reward update conflicts with newer write.
8. Projection rebuild overlaps incremental updates.
9. Transaction serialization/deadlock retry follows root policy.
10. Backfill/replay does not duplicate point truth.
11. Privacy instruction replay does not erase/alter twice incorrectly.

#### Events / Jobs

- outbox replay and poison-message handling;
- source-event dead-letter/manual replay;
- projection rebuild;
- tax-report retry;
- approved fulfillment retry/reconciliation;
- privacy executor retry;
- queue telemetry completeness.

#### Provider Integration

For each enabled Gamification-owned provider:

- timeout/retry;
- signature verification if webhook;
- provider-event duplicate;
- unknown status;
- out-of-order event;
- reconciliation after missed callback;
- provider payload isolation.

If no provider is approved, verify no provider-dependent Reward can become automatically fulfilled.

#### UI / Admin Surface

Production workflow smoke tests for existing surfaces only:

- Program/Rule/Challenge/Reward admin;
- point ledger/balance;
- leaderboard;
- redemption queue;
- user Reward/redemption surface where implemented.

No new UI.

#### Failure Behavior

Verify stable results for:

- `IDEMPOTENT_REPLAY`;
- `IDEMPOTENCY_CONFLICT`;
- `STALE_WRITE`;
- `CONFLICT`;
- `INSUFFICIENT_POINTS`;
- `CONSENT_REQUIRED`;
- `COMPLIANCE_HOLD_BLOCKED`;
- `TAX_REVIEW_REQUIRED`;
- `DEPENDENCY_UNAVAILABLE`;
- `RETRY_EXHAUSTED`;
- `ARCHITECTURE_BLOCKED`;
- `UNSUPPORTED_REWARD_EFFECT`;
- `MANUAL_REVIEW_REQUIRED`.

No raw provider/database error becomes public API semantics.

#### Tests

1. **Domain regression:** all Module invariants.
2. **State transitions:** every allowed/denied path.
3. **Contract:** no dependency drift.
4. **Database:** rollback, indexes, constraints.
5. **Concurrency:** award and redemption races.
6. **Idempotency:** command/event/tax/effect replay.
7. **Projection:** incremental/full rebuild equivalence under overlap.
8. **Worker:** crash, retry, dead-letter, replay.
9. **Authorization/security:** self/admin/step-up/rate limit.
10. **Compliance:** consent/hold/tax/no-paid-odds.
11. **Privacy:** enumerate/retain/anonymize/replay.
12. **Audit:** action/access coverage.
13. **Observability:** telemetry redaction and low-cardinality metrics.
14. **Provider:** only approved adapters.
15. **Migration/backfill:** forward migration and data reconstruction safety.
16. **Performance smoke:** ledger history/balance, Rule lookup, leaderboard page, redemption transaction contention.
17. **Static architecture:** no prohibited local duplicate/import.

#### Documentation Updates

- finalize resolved U-GR decisions with rationale.
- update Module architecture if a binding rule changed.
- update shared registry only if canonical owner architecture formally changed.
- update progress tracker with test evidence and remaining disabled behavior.

#### Acceptance Criteria

- replay/concurrency cannot duplicate or corrupt value.
- source truth survives projection/worker outages.
- dependency/provider outages fail safely.
- privacy/audit/telemetry boundaries hold.
- migrations/backfills preserve append-only history.
- unsupported behavior remains disabled.
- performance is acceptable under project-defined launch targets once those targets exist.

#### Exit Gate

Actual required Consent/Audit/Hold/Tax and other provider capabilities must satisfy the production provider readiness prerequisite; production-like fakes alone cannot pass this production gate (CL-10-R013).

PASS only when:

- all enabled behavior has passed unit, contract, integration, concurrency, privacy, security, and production-build checks;
- migration/backfill verification passes;
- no unresolved decision is bypassed;
- no prohibited duplicate shared/external responsibility exists;
- a final architecture review confirms this Module still owns only Gamification / Rewards truth.

If a Reward effect remains unsupported, it remains disabled; production hardening may still PASS for the explicitly supported deterministic subset.

---

# MODULE HARDENING CHECKLIST

- [ ] Source-event replay produces one point effect per Rule semantic identity.
- [ ] Command idempotency replays original results.
- [ ] Concurrent redemption cannot overspend points.
- [ ] Finite inventory is disabled or protected by approved U-GR-08 design.
- [ ] Program/Rule/Reward stale writes return explicit conflict.
- [ ] Projection can be deleted and rebuilt to the same result.
- [ ] Worker retry/dead-letter preserves valid domain state.
- [ ] Tax outage does not fabricate approval.
- [ ] Hold outage/active hold does not fabricate fulfillment.
- [ ] Notification outage does not change redemption truth.
- [ ] Approved provider outage does not produce `fulfilled`.
- [ ] Privacy execution is idempotent and retention-aware.
- [ ] Audit and domain truth are distinct.
- [ ] Telemetry contains no prohibited sensitive payload.
- [ ] Unsupported RewardTypes remain inactive/unfulfillable.
- [ ] No `PrizeEntry`/chance-odds behavior exists in this Module.
- [ ] No local auth/consent/hold/tax/notification/queue/idempotency/Search/Track duplicate exists.

---

# PHASE SUMMARY

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Contracts and Configuration Foundation | 01–02 |
| 2 | Append-Only Point Truth | 03–04 |
| 3 | Challenges and Rebuildable Projections | 05–06 |
| 4 | Deterministic Reward Economy | 07–08 |
| 5 | Cross-Module Reward Gates and Fulfillment Effects | 09 |
| 6 | Privacy, Audit, and Operational Completion | 10 |
| 7 | Neighbor Contract Proof | 11 |
| 8 | Security, Replay, Concurrency, Reconciliation, and Production Verification | 12 |
| **Total** |  | **12 features** |

### Cluster alignment

| Module features | CL-10 build-plan feature |
|---|---|
| 01–02 | CL-10 01 — Programs, Rules, Disclosure |
| 03–04 | CL-10 02 — Source Events to Point Ledger |
| 05–06 | CL-10 03 — Challenges, Balance Projection, Leaderboards |
| 07–08 | CL-10 04 — Reward Catalog and Atomic Redemption |
| 09 | CL-10 05 — Reward Tax, Hold, Fulfillment, Benefit Bridges |
| 10 | CL-10 10 — Cross-Cluster Contract Proof |
| 11 | CL-10 10 — Cross-Cluster Contract Proof |
| 12 | CL-10 11 — Production Hardening |

This mapping does not reorder the Cluster plan. It decomposes each Gamification-owned Cluster slice into smaller Module implementation features.

---

# MODULE EXECUTION PATTERN

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read Canonical Shared Operations.
3. Read CL-10 architecture and build plan.
4. Read this Module architecture and implementation plan.
5. Read public-interface sections for direct dependencies.
6. Inspect current Prisma schema and migrations.
7. Confirm the prior Module exit gate.
8. Check Module/Cluster Proposed Rulings and Unresolved Decisions that affect the feature.
9. Write the required feature implementation specification.
10. Implement only the numbered feature plus canonical-owner prerequisite fixes explicitly required.
11. Run typecheck/lint/unit/contract/integration checks applicable to the feature.
12. Verify the full feature workflow, including denial/replay/failure paths.
13. Update progress.
14. Update architecture only when a binding decision legitimately changed.
15. Record unresolved risks and deferred work.
16. Do not advance if the exit gate fails.

---

# REQUIRED FEATURE IMPLEMENTATION SPECIFICATION

Immediately before coding one numbered feature, the coding agent must produce a concise specification containing:

- Objective
- Observable result
- Cluster build-plan link
- Dependencies
- In scope
- Out of scope
- Owned data affected
- Public contracts
- Shared operations consumed by SH-### ID
- Permissions/compliance
- Primary workflow
- Provider integration
- Jobs/events
- Idempotency/concurrency
- Database transaction/constraint behavior
- Error behavior
- Tests
- Acceptance criteria
- Documentation updates
- Unresolved decisions/blockers relevant to this feature

Do not generate all 12 implementation specifications in advance.

---

# REQUIRED COMPLETION REPORT

After implementing each numbered feature, the coding agent must report:

- Feature completed
- Observable result verified
- Files added
- Files changed
- Database changes
- Migrations
- Constraints/indexes added or changed
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused by SH-### ID
- Canonical-owner changes required outside this Module
- Events/outbox handlers added
- Jobs/workers added
- Provider adapter changes, with explicit owner
- Tests added/changed
- Commands run
- Manual/contract verification
- Authorization/compliance verification
- Idempotency/concurrency verification
- Privacy/audit/observability verification where applicable
- Documentation updated
- Assumptions
- Architecture rulings resolved
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result: **PASS / FAIL / BLOCKED**, with evidence

A BLOCKED feature is not complete; it documents that architecture or a canonical owner dependency must be resolved before implementation can safely proceed.

---

# FINAL MODULE QUALITY GATE

Before declaring the Module implementation plan complete in execution, verify:

1. All Gamification source truth has exactly one owner.
2. No Sweepstakes / Prize truth was absorbed.
3. No external Module's source truth was copied locally.
4. Every shared mechanism references its canonical SH-### operation.
5. Point truth remains append-only.
6. Point balance/leaderboards remain rebuildable.
7. Source-event processing is exactly-once in business effect.
8. Commands/queries expose bounded stable contracts.
9. Reward spend/redemption is atomic.
10. Unsupported inventory/effect behavior fails closed.
11. External Tax/Hold/provider results cannot mutate redemption directly.
12. Consent proof remains Consent-owned.
13. Privacy orchestration remains Privacy-owned.
14. Search remains external projection/effect truth.
15. Audit/domain events/observability remain distinct.
16. Every enabled worker is durable/retryable/observable.
17. Concurrency/idempotency tests cover the critical races.
18. No paid prize-odds path exists.
19. Module feature sequencing aligns to CL-10 Features 01–05 and does not reorder the Cluster.
20. Every numbered feature has tests and a concrete exit gate.
21. A coding agent can distinguish safe implementation work from named architecture blockers without inventing behavior.
