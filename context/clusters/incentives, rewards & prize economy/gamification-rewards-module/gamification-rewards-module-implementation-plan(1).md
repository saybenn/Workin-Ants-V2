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
| U-GR-01 resolved by P04 / WA-R015 | Implement User-wide point balance/spend semantics in Feature 03 |
| U-GR-02 signed point-delta convention | Feature 03 ledger production writes |
| U-GR-03 historical rule/causation evidence | Feature 03 production point awards |
| U-GR-04 reversal linkage policy | Feature 04 production reversal |
| U-GR-06 participant status vocabulary or approved conservative subset | Feature 05 participant transitions |
| U-GR-08 inventory semantics | finite-inventory Reward activation/redemption in Features 07–08 |
| U-GR-09 reward fulfillment/effect contract | Feature 09 for each affected RewardType |
| U-GR-10 resolved owner; remaining grant/effect contract | Feature 09 profile-boost/time-bound benefit |
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
- U-GR-05 is resolved by P05 / WA-R015: automatic point expiration is disabled at launch.

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

PASS only when U-GR-04 is resolved for production reversal and all ledger/query/correction tests pass. U-GR-05 is resolved by WA-R015; launch expiration remains disabled.

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
- profile_boost requires U-GR-10/SH-119 effect-contract binding.
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

Hold-dependent production behavior is BLOCKED until the approved Hold target/action applicability and creation contracts and real provider capability are available; the production provider readiness prerequisite above applies (CL-10-R007). U-GR-01/02/14 are resolved by WA-R014/015/019 and require implementation proof. U-GR-08 for finite inventory, U-GR-09 for enabled effects, and U-GR-16 for enabled compensation remain scoped prerequisites; generic metadata does not establish historical consent proof.

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
**SH-119:** Track-owned for temporary deterministic commercial benefits; bind the effect contract before activation.
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
- Missing Track grant/effect execution contract -> profile boost remains disabled; SH-119 ownership is settled.

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
- U-GR-10 ownership is resolved; bind the SH-119 execution contract for enabled effects.
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
- SH-119 for approved reward effects.

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


## WA-R014 — Point ledger arithmetic and historical causation

Class: **AI_RESOLVED** for signed-delta convention, durable causation, reversal linkage and acceptance proof. Does not select spend scope (P04), expiration policy (P05), reward effect or compensation policy.

Gamification owns an append-only signed point ledger. `earned` is strictly positive; `spent` and an authorized `expired` entry are strictly negative; `adjusted` is a nonzero signed delta with authorized reason/evidence. A `reversed` entry refers to one original entry in the same approved account and has exactly its opposite signed value. Ordinary reversal is full, at most once per original, and cannot target another reversal. Partial corrections use an explicitly authorized adjustment with causation rather than pretending to be a full reversal. No zero-value ledger rows or mutation of an original amount. This closes U-GR-02 and the linkage/double-reversal portion of U-GR-04; downstream compensation and insufficiency behavior remain U-GR-16 and cannot be guessed from these signs.

Every award binds the owner source-event identity/version, beneficiary, rule identity and immutable effective rule version (including exact evaluated rule content/hash), evaluation time and semantic effect key. Duplicate delivery through SH-045 or repeated commands through SH-044 cannot create a second effect. Persist award and owner outbox atomically; shared inbox/idempotency infrastructure supplies the mechanism, not a competing Gamification-wide event bus. Historical proof survives mutable rule edits. This resolves U-GR-03's evidence strategy; exact schema fields/indexes are DEFERRED_IMPLEMENTATION_DETAIL in the coordinated database pass.

For terms-dependent redemption, persist the exact accepted terms version/content identity and Consent proof reference bound to that redemption and acceptance context. Runtime lookup of today's active terms or a generic audit event alone is insufficient proof of what was accepted. Consent owns acceptance proof; Gamification owns the redemption's contextual binding. This resolves U-GR-14's proof strategy without choosing retention duration or a cascade-delete behavior.

Implementation acceptance: all sign/type combinations, sum equals available-effect projection under the approved account policy, duplicate event/key returns original effect, conflicting key payload rejected, concurrent reversal yields exactly one opposite entry, cross-account/reversal-of-reversal rejected, rule/terms changes do not rewrite historical proof. P04/P05 are now approved by WA-R015: User-wide accounting, no launch expiration. Implementation and any future-policy prerequisites remain separate. These are architecture requirements, not test execution claims.


## WA-R015 — User-wide points and no launch expiration (P04/P05)

**Binding product-owner ruling, approved 2026-09-30.** One User-wide Workin Ants points balance applies across Gamification/Rewards programs. Programs independently define earning rules and reward eligibility; they do not create separate point currencies or balances. This closes U-GR-01 / P04. Account identity and the atomic spending/ledger lock scope are User ID; optional program/profile references are provenance or eligibility context, never alternate wallets. All program-specific earning events credit the same account; reward eligibility is checked separately from point sufficiency. Cross-program spending uses the same canonical balance and cannot bypass a reward's eligibility conditions.

Points do not automatically function as cash, a Track/commercial entitlement, a purchased sweepstakes entry, or a mechanism for increasing chance-based prize odds. A separately approved conversion to a commercial benefit follows the explicit boundary and owner: Gamification owns redemption, Track owns commercial grants (SH-119), and the affected feature applies the granted benefit. No direct premium flag, implicit currency conversion, or automatic prize-entry creation is permitted.

**No automatic point expiration at launch.** Existing points remain valid unless spent, reversed or otherwise adjusted through an approved ledger operation. This closes U-GR-05 / P05 for launch. The `expired` enum remains reserved; launch commands, scheduled jobs and rules cannot append expiration effects. Program closure, inactivity, tier changes or profile changes do not expire a User's points. A future expiration feature requires explicit approved policy covering applicability, notice, effective dates, existing balances and auditable ledger behavior. Retention of proof is a separate concern and cannot be used to erase spendable value.

Technical application: calculate balance from the append-only owner ledger under WA-R014; serialize spending by User account, enforce sufficient available points atomically, and use immutable idempotent spend proof tied to redemption. Programs remain metadata/eligibility predicates, not lock partitions. Rebuildable balance/leaderboard projections never become source truth. Do not infer existing production balances or run a migration/backfill from this ruling.

Acceptance requirements: earnings from two programs combine into one balance; concurrent redemptions across programs cannot overspend it; reward eligibility can deny redemption despite sufficient points; profile/track changes preserve the account; program closure does not expire points; launch expiration attempts are rejected; replay creates no second spend; approved commercial conversion uses Track and never changes prize odds. These are future implementation tests, not a completion claim.


## WA-R019 — Consent catalog, acceptance causation and buyer provisioning

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R019 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r019--consent-catalog-acceptance-causation-and-buyer-provisioning) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Consent owns an immutable version/content catalog, including consent type, version, exact content or immutable content reference/hash, locale, jurisdiction applicability and effective interval. Existing logs cannot prove an unrecorded presentation. Bind acceptance to the catalog entry and the actual rendered presentation identity/version, subject, action/context and time; preserve an immutable rendering descriptor where composition changes presentation. SH-009 selects applicable content, SH-007 stores acceptance, and SH-008 queries proof. Same acceptance command key/fingerprint replays; a new intentional re-acceptance is a new command/proof, not a uniqueness collision on User+type+version. Current-state eligibility queries use current applicable proof; Orders, screening authorizations, digital terms, redemptions and other historically binding actions preserve their specific proof reference/content-version binding. A generic audit log alone is not that binding.

Withdrawal/decline is recorded separately as an append-only disposition, not by rewriting an earlier acceptance; the consuming policy evaluates its effect. Legal re-consent/material-change obligations and retention periods are external facts. ConsentType.age_gate can prove acknowledgment only; Identity separately evaluates age eligibility. This resolves proof/catalog/retry architecture, not legal sufficiency for every category.

Customer provisioning uses the Customer owner synchronously and idempotently at the first buyer action (SH-004), with durable uniqueness on User. Optional registration-time outbox provisioning can warm the profile but never substitutes for this precondition. Customer aggregate views use the existing SH-126 Customer application facade over authorized owner queries; default to query composition, introducing a durable projection only with a demonstrated query need and invalidation contract. Legacy backfill/deletion awaits the database-evidence gate; User remains authentication identity. Tradeoff: first buyer action depends on Customer availability, but avoids an eventually missing commercial actor and duplicate local provisioning.

## WA-R026 — Approved Review and multi-episode Dispute policy (P06–P08)

**Binding product-owner ruling, 2026-10-01.** Review input is a whole-number 1–5 star rating. Zero and half-star input are invalid; aggregate/reputation values may be fractional. Review owns the rating calculation; Professional and Search consume its versioned result, not separate scales or calculators.

Automatically publish an otherwise eligible Review after completed-Order, buyer-author and applicable safety/moderation checks pass. An author may revise rating or comment. Every proposed revision is immutable history and passes the same applicable checks before becoming the public/reputation-bearing revision. Promotion is atomic against the expected Review version; a delayed check for an older revision cannot supersede a newer one. A rejected/unavailable revision does not overwrite the previously accepted public revision; an active restriction independently controls whether any revision is public. Author editing never restores hidden/removed state or bypasses a restriction. Restoration is an explicitly authorized Review owner/Moderation action. Revisions update the contribution of the same Review; they never add another rating count. Hiding/removal withdraws its contribution; restoration uses the current eligible accepted revision.

The Order's buyer Customer or seller Professional may open a commercial dispute. Authorized support may record one on behalf of an identified participant where policy allows; preserve both actual support actor and represented participant. There is **one durable Dispute case container per Order at launch**, not one dispute episode for the Order's lifetime. Authorized reviewers may reopen that case for new evidence, a correction, or a later episode associated with the same Order, including another session of a multi-session package.

Persist a distinct immutable cycle/episode identity for each review/adjudication/settlement cycle, with opening/reopening reason, initiating/represented actor, relevant Order version, session references where applicable, evidence, decisions and outcomes. The case's current state is a projection of its current cycle; reopening never overwrites prior closed decisions or settlement proof. Serialize cycle creation and adjudication per case. A current pending cycle can receive new evidence; it does not require competing active refund/release decisions. Any concurrency policy must preserve one authoritative current case decision path.

Every financial effect requires valid current owner authorization and an idempotent identity bound to the specific cycle/decision/effect, with prior effects retained for reconciliation. Never key a new valid effect only by case ID, and never mint a fresh identity merely to retry an old effect. Reopening itself cannot replay a previous refund, charge, payout adjustment, settlement or hold-release effect. Order/Payment validate cumulative amounts and remaining authorized source value across all cycles; a new cycle is not permission to exceed the purchased/refundable amount. Dispute decides, Order coordinates transaction effects, Payment executes its rail, and Holds retains its own action-scoped lifecycle.

Opening/appeal windows remain separately versioned product policy; no numerical deadline is introduced. Bind the applicable policy version to each cycle. Product case windows do not redefine statutory/provider rights. Current Prisma's one-case relation is compatible with the container rule but does not supply cycle/revision proof; the coordinated database pass must add that representation before activation.

Acceptance: ratings 0/6/fractions rejected, fractional aggregate allowed; two revisions race without double counting; failed safety check leaves the accepted revision unchanged; hidden/removed edit cannot restore; buyer/seller/support attribution; unrelated actor denied; later-session episode reuses the case with a new cycle; old cycle remains reconstructible; replay of old financial result cannot affect the new cycle; valid new effect has its own authorization and respects cumulative Order limits. These are required implementation checks, not claims of executed feature tests.

Duplicate collapse: CL04-U034/035/036/038/040 and owner §9/§35 product questions; CL04-U039 retains its versioned configuration gate. WA-R022/023 technical proof, financial finality and assurance rules remain binding. Classification: PRODUCT_OWNER_CHOICE — RESOLVED by explicit approval; enforcement/revision/cycle identity details AI_RESOLVED.

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

## WA-R035 — Supply lifecycle, history and source projections

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

This ruling supersedes the proposed/unresolved lifecycle and projection alternatives named below; implementation still requires forward schema coverage and contract fixtures. Professional graph: create→draft; draft→active after current activation readiness; active→paused; paused→active after current readiness; draft/active/paused→suspended only by an authorized source restriction; draft/active/paused→archived by owner-authorized retirement. Archiving a suspended record may record retirement intent but cannot remove the restriction. Archived→draft is an explicit owner restore command, never implicit activation. Suspended→draft requires authorized release of all applicable restriction sources; subsequent activation rechecks readiness. Preserve previously acquired transactions and obligations. Ordinary dependency loss invalidates the affected action/public decision and requests reevaluation, not an automatic Profile status change. Only an explicit source policy may instruct suspension.

Offering graph: draft→active by publish; active→paused; paused→active by resume, each activation requiring current composed gates. Draft/active/paused may enter under_moderation/disabled_by_moderation/disabled_by_dmca only from a valid Moderation decision. Those restriction states may change to another restriction state only with a superseding valid decision. Restriction clearance restores to draft, preserving all other restriction sources; publication is a separate fresh command. Rejected→draft is an explicit correction/resubmission command after the rejecting owner permits it. Draft/active/paused/rejected→archived; archived→draft by explicit restore. Retirement never clears restrictions, destroys Order snapshots or grants a refund. An Offering kind can change in draft only before any Order, delivery or durable external reference; otherwise create a new Offering. isPublic is seller publication intent; effective visibility additionally requires active lifecycle, current SH-024 decision and no applicable restriction. Moderation timestamps are evidence, not independent allow flags.

Adopt immutable owner lifecycle histories for ProfessionalProfile and Offering, with aggregate version, prior/next state, command/source decision identity, actor, timestamp and policy/decision references. Mutations commit history and outbox atomically using expected opaque version plus row serialization for competing transitions; updatedAt alone is not the concurrency token. Publication/activation and seller Order acceptance retain immutable minimized gate decisions/source versions; current actions still reevaluate. Legacy financial/Trust columns remain non-authoritative compatibility projections until a measured reader inventory and forward migration remove them; never backfill authoritative readiness from a legacy boolean.

onboardingCompleteAt is the first successful owner activation after required onboarding facts pass, immutable except an audited data correction. It is not current readiness. ProfileCompleted.v1 may qualify one Gamification rule per profile and rule revision, containing profileId, subject User reference, firstCompletionAt, aggregateVersion, eventId; no raw onboarding facts. Gamification decides awards and source-event dedupe. Reinstatement does not emit another first completion. Dependency changes are owner outbox facts carrying target, changed dimension and source version; Professional/Supply consume idempotently and reevaluate current truth. Do not propagate a copied allow decision indefinitely. Booking availability is not an eligibility prerequisite; a public availability presentation uses Booking's separately authorized query and never changes Professional status.

Public Professional projection allowlist: professionalProfileId, slug, display name, approved biography, accepted active taxonomy IDs/labels/revisions, owner-supplied public avatar rendition reference, Review-owned ratingAverage/ratingCount with reputation version, and SH-131 fuzzy public location when allowed. Public Offering projection: offeringId, professionalProfileId, slug, title, approved summary, kind, accepted taxonomy IDs/labels/revisions, current public pricing summary/currency, approved public rendition references and public delivery/location mode. Each includes sourceVersion and current public-readiness evidence. Exclude User IDs, contact details, exact location, credential documents, provider refs, financial/Healthcare/hold reasons. Search must obtain URLs through approved Media/public rendition rules; no private original URL. Review→Professional transport is an outbox-triggered owner query getProfessionalReputation.v1 returning profileId, ratingAverage, ratingCount, projectionVersion, then a version-checked Professional projection command; stale events trigger current query rather than regress values.

priceFromCents is a rebuildable minimum of currently eligible active pricing options in one currency, not purchase truth. Missing or mixed-currency options produce no priceFrom value, never zero/implicit conversion. Orders bind the selected immutable price/package. isFeatured has no ranking or commercial effect at launch; promotion is deferred pending a separately approved owner policy. Heterogeneous bundle Offering creation remains disabled; this does not disable P02 multi-session packages within supported kinds. No new seller entitlement gates: supported effects remain approved Professional commission terms; unknown keys cannot gate drafting or fabricate quota. SH-016 action keys are activate_profile, public_visibility, publish_offering, respond_to_gig, participate_in_order; payout stays Payment-owned.

Owner status/remediation notifications use committed source-event identity, generic status/remediation template and safe authenticated destination; no sensitive provider/Healthcare/hold details. Notifications do not prove readiness. No generic admin force-ready override: each source owner must authorize and record its own correction, followed by reevaluation. Required verification includes stale-resume versus restriction, archive/restore preserving obligations, projection field exclusion, duplicate first-completion award, and reputation version replay. These are implementation acceptance criteria, not tests already executed.

## WA-R037 — Payment effects, payout reservation and tax evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Payment owns immutable financial operation and attempt history, not just outbox delivery. Every effect has unique owner/sourceType/sourceId/sourceRevision/effectKind/effectOrdinal plus currency, semantic payload hash and original-effect reference for compensation. Reuse with different amount/subject/currency conflicts. Verified provider ingress receipt is separate from Payment and Track effect receipts; route by approved provider object/metadata ownership, never both owners applying the same business effect. Unknown routing is quarantined. Payment receipt fields: provider/account/eventId, eventType, fingerprint, handlerVersion, target operation, receivedAt, processing/attempt/recovery state and committed effect references. No raw secret payload by default; legal retention remains externally supplied.

Balance accounting uses immutable signed minor-unit effects with explicit bucket vectors and per-currency conservation. Earnings credit available (or pending until the approved availability rule); payout reservation moves available -A/reserved +A atomically with request acceptance; reservation release moves reserved -A/available +A only once after known cancellation/failure with no possible pending provider movement; successful payout moves reserved -A/paid +A. Transport retries have zero ledger effect. Provider return/reversal records its actual returned amount as a new linked effect, paid -R/available +R only after verified return and applicable financial restrictions; it never mutates the original payout. Fees/refunds/chargebacks are separate authorized signed effects, never hidden in payout status. Unknown money movement retains reservation and reconciles. Existing one-amount enum records are insufficient to infer these vectors: use an explicit owner allocation/bucket effect structure and forward constraints. This is accounting of processor-held value, not permission to introduce a wallet or new financial product.

At launch each PayoutTransfer belongs to one PayoutRequest; Order references are optional immutable allocation provenance, not a second transfer source. A request supplies an explicit validated active payoutAccountId; no guessed default among multiple accounts. Capture all blocking Hold IDs and decision versions in a separate immutable evaluation snapshot; blockedByHoldId is explanatory only. Reevaluate current holds/account/financial readiness immediately before dispatch. Keep one semantic transfer identity and stable provider idempotency key through network retries. Record each transport attempt separately. A terminal failed transfer never reopens; a new request/transfer after confirmed nonmovement and reservation release requires fresh authorization. Unknown is nonterminal even if transport timed out. No automatic retry of a terminal financially reversed/paid transfer.

Ratify the minimum Payment §9 graphs with these restrictions: KYC rejected/expired/disabled attempts are terminal; new attempt linked to previous evidence. TaxProfile rejected/expired creates a new collection revision, never overwrites submitted documents. One current applicable selector per subject+purpose+jurisdiction/provider scope points explicitly to the accepted evidence; pending new evidence does not silently replace valid current proof, while revocation immediately invalidates it. PayoutAccount disabled is terminal for that account; restriction recovery uses verified current provider evidence. PayoutRequest failed/cancelled/reversed terminal; processing cannot cancel without proven no movement. PayoutTransfer failed/cancelled/reversed terminal. SalesTaxCalculation changed quote requires a new calculation; finalized is immutable, voiding is a separately evidenced provider operation. Tax submission rejected/failed uses a new linked submission revision; transport retries of an unacknowledged submission retain semantic identity. Filed recipient correction creates replacement evidence and a link, preserving prior filing. No enum setter or provider callback bypasses these rules.

Tax subject is a Payment-owned stable subject reference mapped to an identified legal recipient, with explicit User and optional ProfessionalProfile provenance; profile identity is not automatically a separate legal taxpayer. Effective mappings/versioned evidence prevent accidental subject merge. Aggregate key is taxSubjectId + jurisdiction + taxYear + currency + reportingRegime; retain source owner/id/revision/recognition type and unique reversal identity. Prize-owned summaries use the same dimensions and preserve their own source valuation truth. SH-019 supports an explicit tax_fulfillment purpose and tax dimension; no second generic tax-readiness service is needed. Payment owns TaxReportingSubmissionStatus and TaxReportingRecipientStatus. Reporting bundle uniqueness includes regime/jurisdiction/year/currency/submission series/revision; recipients unique within submission by tax subject and applicable form/category. Rule versions, form requirements, recognition dates, thresholds and correction legality remain approved external configuration, never invented constants.

Order binds final calculation ID to exact immutable quote/order revision, currency, line IDs and buyer-tax-location evidence revision. Payment preserves line-level taxable basis, tax, jurisdiction, provider tax code and liability role even for mixed-liability lines. Tax-location provenance includes approved source owner, source/evidence revision, validation method/result and captured/effective time, minimum required location fields; it is not public-location consent. Each authorized refund has immutable line allocations against the original captured quantities/basis/tax and links its own provider refund and tax reversal attempts. Cumulative refunds cannot exceed captured refundable allocation; lock the operation allocation counters and reject mismatched currency. Use deterministic minor-unit residual allocation only within an approved tax/provider allocation policy; do not guess rates or liability. Partial/multiple refund representation requires separate child records, not one overwritten reversalId. Provider unsupported/ambiguous results stay pending/manual review, never fabricated successful tax reversal. Full provider/rule qualification remains external before affected execution.

Required verification: concurrent reservation conservation, duplicate callback/compensation, timeout followed by paid result, multiple holds, account changes before dispatch, line-level cumulative refund cap, subject/jurisdiction separation, replacement filing traceability. No live financial test or migration is claimed by this architecture decision.


## WA-R062 — Reward inventory and fulfillment ownership

**Applied architecture ruling — 2026-10-08.** This scoped amendment supersedes earlier proposed/unresolved labels only for the concerns below. It records architecture, not implemented schema, successful tests, deployment or legal approval.

Gamification owns User-wide point accounting, redemption, challenge evidence and its fulfillment attempt journal; Sweepstakes owns winning and prize fulfillment journal. Preserve WA-R014/015 and P04/P05: one User balance, append-only signed effects with original-source links, no launch expiration, no cash/entitlement/odds implication. Reward inventory denotes configured total stock/cap; available equals cap minus reserved/committed units without counting a reservation twice when committed. Atomically reserve against redemption acceptance under owner lock; concurrent requests cannot oversell. Existing inventory values need explicit migration inventory before reinterpretation. Release a reservation only with durable cancellation/no-delivery proof; unknown effects stay reserved and reconcile.

Fulfillment dispatch records immutable attempt/effect identity, idempotency key, requested quantity/value, actor, policy/version and provider/manual evidence. Commercial benefit execution belongs to Track, financial/tax effects to Payment, physical/manual delivery to an explicitly registered owner adapter. Receipt indicates actual completed effect, not a transport acknowledgment. Unknown outcome reconciles before retry; unsupported RewardType cannot activate. Redemptions never write entitlement or payment truth directly.

Ratify Program draft→active; active→paused/ended; paused→active/ended; ended→archived (terminal). Challenge draft→active/cancelled; active→paused/completed/cancelled; paused→active/completed/cancelled; completed/cancelled→archived. Participant accepts only active→completed/cancelled; no implicit draft/paused/archived participant semantics. Reward draft→active/retired; active→paused/retired; paused→active/retired; retired terminal. Activation validates versioned allowlisted declarative rule schema and supported source/effect contracts; no arbitrary executable rule content. Persistent source evidence proves challenge completion; optional progress projection rebuilds from that evidence. rewardJson references an approved point/rule or supported Reward effect, not independent currency or commercial benefit. Ordinary participation gets no new Premium gate. Owner deterministic validation and scoped Hold/manual review do not create a generic fraud service.

Redemption graph: pending_confirmation→pending_tax when required, or approved only when all current applicable gates pass; pending_tax→approved after clearance. pending_confirmation/pending_tax/approved→blocked on applicable restriction. blocked→pending_confirmation/pending_tax/approved only after authorized current reevaluation, never straight to fulfilled. approved→fulfilled requires actual effect receipt. A prefulfillment cancellation requires applicable owner policy and confirmed no outstanding delivered/unknown effect. approved/fulfilled→reversed requires a supported compensating effect and its receipt; return points/reservation exactly once only after no outstanding benefit or proven compensation. cancelled/reversed are terminal ordinary states; corrections are new linked evidence. Hold release, no-show/completion reports, notification or tax readiness alone never fulfill, compensate or create purchase/review rights (WA-R042).

Qualifying reward input must identify owner source, subject mapping, policy/version, occurrence time and correction/retraction revision. Order supplies qualifying purchase/full-Order outcome; a Booking report is not full-Order completion. delivery_on_time additionally requires source-owned contractual deadline/version and verified delivery timing; absent that basis the trigger stays disabled. Review supplies eligible published rating/version and recipient mapping; Profile supplies completion-policy fact rather than creation event. Apply one source/rule effect with linked compensation on valid correction. Producer fixture/DTO agreement remains required before these cross-owner triggers activate; no Prisma polling or consumer reconstruction substitutes for it.

Implementation sequence: specify owner storage/typed contract and forward migration; implement concurrency-safe owner commands; then wire consumers. Before activation verify replay, stale version, concurrent decisions, denied/unavailable dependencies, evidence retention, and failure/recovery fixtures. Exact physical names and executable tests remain implementation work. No cross-owner direct writes.


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `gamification_rewards` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`recordEligibleActivity / requestRewardRedemption / getPointLedger`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

Apply the appendix's reward qualification matrix for order_completed, qualifying purchase, high_rating_received, profile_completed and delivery_on_time. Deduplicate the logical award by program, rule lineage, trigger, source owner/ID and beneficiary User, independent of transport revision. Corrections reevaluate that same award and use linked idempotent compensation only under the approved correction policy; no silent historical re-award on rule-version change. Missing source proof leaves the trigger disabled/pending, never reconstructed from foreign tables.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.


## WA-R075 — Typed Hold action applicability and source readiness

This owner adopts its source/consumer obligations in `context/reconciliation/hold-action-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.
