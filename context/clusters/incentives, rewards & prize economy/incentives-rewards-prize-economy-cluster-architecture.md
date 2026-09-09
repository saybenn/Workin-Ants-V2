# Incentives, Rewards & Prize Economy Architecture

> **Cluster ID:** `CL-10`  
> **Cluster name:** Incentives, Rewards & Prize Economy  
> **Cluster type:** `feature_ecosystem_prize_compliance_reward_ledger`  
> **Repository target:** `context/clusters/incentives-rewards-prize-economy/architecture.md`  
> **Document status:** Target Cluster architecture derived from the current Workin Ants evidence set; proposed rulings and unresolved decisions are explicitly labeled  
> **Audience:** Coding agents, developers, reviewers, maintainers, compliance reviewers, and architects  
> **Primary Deep Modules:** `gamification_rewards`, `sweepstakes_prize`  
> **Update rule:** Update this file whenever a binding CL-10 architectural decision, Module ownership boundary, public contract, lifecycle rule, compliance gate, or material schema meaning changes.

---

## 1. Document Status and Scope

CL-10 is the controlled implementation context for the Workin Ants incentives ecosystem. It coordinates two Deep Modules:

1. **Gamification / Rewards** — deterministic engagement incentives, points, challenges, leaderboards, rewards, and reward redemption.
2. **Sweepstakes / Prize** — chance-based entry, drawings, winning, prize value tracking, and prize fulfillment state.

This document is subordinate to the root Workin Ants architecture and source-of-truth rules. It explains how the two Modules collaborate with each other and with platform capabilities without taking ownership away from either Module.

**A Cluster is not a lifecycle owner.** CL-10 must never acquire a `ClusterStatus`, generic incentive ledger, generic fulfillment lifecycle, generic winner/redemption record, or generic source-of-truth repository. The Cluster exists for planning, integration, cross-Module invariants, coding-agent context, and end-to-end verification.

The Prisma schema remains executable schema evidence. The Deep Module Registry and Ubiquitous Language define ownership and meaning. The Canonical Shared Operations Registry defines anti-duplication boundaries. This document coordinates those sources for implementation.

### Evidence-status vocabulary

- **Confirmed** — directly established by the Deep Module Registry, Cluster Registry, Prisma schema, Ubiquitous Language / Compliance inventory, Project Overview, or confirmed Shared Operations Registry entry.
- **Reasonable inference** — strongly implied by confirmed records and workflows but not itself a binding schema or lifecycle decision.
- **Proposed Ruling** — an architectural choice required to make implementation safe and coherent where the supplied evidence is incomplete or conflicts. It must be approved before code or schema commits depend on it.
- **Unresolved Decision** — evidence establishes a question or missing contract but does not support a safe final answer. Implementation must not silently decide it.

### Relationship to Module architecture

The Module architecture remains more authoritative for Module-internal behavior. If a future Module architecture conflicts with this file:

1. identify the conflict;
2. preserve already-confirmed source-of-truth ownership;
3. determine whether the Module decision or Cluster coordination rule must change;
4. update the affected context before implementation proceeds.

Build progress must not silently redefine this architecture.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

CL-10 controls the incentive economy around Workin Ants engagement without collapsing deterministic rewards and chance-based prizes into one system.

### Goal

Turn eligible platform activity into **ledgered deterministic value** and legally controlled **chance-based prize participation** while keeping points, rewards, entries, winnings, tax proof, consent proof, subscriptions, payments, holds, notifications, audit evidence, and provider state in their correct source-of-truth Modules.

### Transformation

```text
Authoritative platform activity
+ configured gamification rules
+ versioned disclosure/consent proof
+ reward catalog configuration
+ drawing/rules configuration
+ free/AMOE entry methods
+ authoritative purchase/order facts where configured
+ tax-readiness decisions
+ ComplianceHold decisions

→ deterministic point-ledger entries
→ challenge participation/completion
→ leaderboard and point-balance projections
→ reward redemption outcomes
→ auditable PrizeEntry records
→ secure drawing outcomes
→ PrizeWinning lifecycle state
→ yearly prize-value summaries
→ tax-aware reward/prize fulfillment decisions
→ downstream notifications, audits, and operational telemetry
```

### What CL-10 explicitly does not own

CL-10 does **not** own:

- base `User` identity or authentication;
- platform or organization authorization interpretation;
- `ConsentLog` lifecycle or active consent-version catalog;
- `CustomerProfile`, `ProfessionalProfile`, `CandidateProfile`, or `OrganizationMember` identity truth;
- `Order` or payment lifecycle;
- Stripe webhook receipt/deduplication truth;
- `TaxProfile`, tax filing, tax provider decisions, or tax-reporting submission lifecycle;
- `ComplianceHold` lifecycle or release authority;
- notification delivery state;
- generic `AuditEvent` or `AccessAuditLog` storage;
- `TrackSubscription`, `TrackEntitlementGrant`, or usage-metering truth;
- global Search / Typesense projection execution;
- PrivacyRequest or DataErasureJob orchestration;
- generic queue, retry, idempotency, lock, cryptographic, logging, or telemetry mechanisms;
- legal drafting of sweepstakes official rules;
- provider-native fulfillment truth that belongs to another provider-owning Module.

---

## 3. Module Inventory

| Module ID | Module name | Module type | Purpose | Owned truth | Primary responsibility in CL-10 | Major inbound dependencies | Major outbound consumers |
|---|---|---|---|---|---|---|---|
| `gamification_rewards` | Gamification / Rewards | `feature_compliance` | Govern deterministic engagement incentives without becoming chance-based prize mechanics. | `GamificationProgram`, `GamificationRule`, `PointLedgerEntry`, `Challenge`, `ChallengeParticipant`, `Leaderboard`, `LeaderboardEntry`, `Reward`, `RewardRedemption` and their owned enums/statuses. | Evaluate eligible activity, append point truth, manage challenges and reward catalog/redemptions, build deterministic projections, coordinate disclosure, holds, tax handoff, and reward fulfillment. | Identity & Access; Role / Authority; Consent & Disclosure; Transaction / Order and other source-event Modules; Professional Eligibility; Payment / Payout / Tax; Admin Review / Compliance Hold; Track Subscription & Entitlement only where an approved reward contract requires it. | Sweepstakes / Prize only through explicitly approved interfaces; Payment / Payout / Tax; Notification; Audit / Event Ledger; Professional Eligibility or Search when an approved deterministic benefit affects them. |
| `sweepstakes_prize` | Sweepstakes / Prize | `compliance_feature_ecosystem` | Own chance-based entry, drawing, winning, prize value, and fulfillment-state truth under AMOE/equivalent-odds/tax controls. | `PrizeDrawing`, `SweepstakesEntryMethod`, `PrizeEntry`, `PrizeWinning`, `PrizeTaxYearSummary` and their owned enums/statuses. | Configure legally gated drawings and entry methods, issue auditable entries, freeze eligible population, select winners securely, own winning state and prize FMV, coordinate tax readiness and fulfillment. | Identity & Access; Role / Authority; Consent & Disclosure; authoritative Order/payment outcome facts; Payment / Payout / Tax; Admin Review / Compliance Hold. | Payment / Payout / Tax; Notification; Audit / Event Ledger; Admin Review / Compliance Hold; Transaction / Order where outcome evidence is required. |

### Non-blurring rule

`PointLedgerEntry` is never `PrizeEntry`. `RewardRedemption` is never `PrizeWinning`. `GamificationProgram` is never `PrizeDrawing`. A deterministic reward may create a downstream effect, but it does not become a sweepstakes record unless Sweepstakes / Prize creates its own source truth under an approved, legally reviewed interface.

---

## 4. Cluster Architecture Principles

1. **Deterministic rewards and chance-based prizes remain separate domains.** Points and rewards must not silently become tickets or better odds.
2. **One owner per lifecycle.** Gamification / Rewards owns gamification and redemption transitions. Sweepstakes / Prize owns drawing and winning transitions. CL-10 owns neither.
3. **Point history is append-only truth.** A mutable `pointsBalance` is forbidden as source truth. Any balance is a derived query or projection from `PointLedgerEntry`.
4. **Leaderboard state is a projection.** `LeaderboardEntry` is derived ranking state and must be rebuildable from owner-approved inputs.
5. **Prize entries are their own truth.** An Order, payment, point ledger entry, or consent record may justify an entry but cannot substitute for `PrizeEntry`.
6. **AMOE and equivalent odds are enforced at the Sweepstakes boundary.** If a purchase-triggered path exists, an approved free path must exist where required, and paid entry mechanics must not receive better chance through `weight`, `entriesAwarded`, hidden rule JSON, entitlement, or another indirect mechanism without explicit legal approval.
7. **No paid prize-odds boost through subscriptions or rewards.** `TrackEntitlementGrant`, profile boosts, points, reward redemption, or paid plan status must not increase chance-based odds.
8. **Consent is proof, not permission.** `ConsentLog` proves acceptance; Gamification or Sweepstakes decides whether that proof is sufficient for the current action.
9. **ComplianceHold is the only reusable platform stop sign.** CL-10 may request and consume holds but may not create a parallel blocked-state service or local hold table.
10. **Tax proof remains Payment / Payout / Tax truth.** CL-10 owns value snapshots and its own fulfillment state; it consumes tax readiness and reports recognized value through the tax owner.
11. **Provider state is never CL-10 truth unless CL-10 is explicitly the provider-owning Module.** Stripe state, tax-provider state, notification state, and future fulfillment-provider payloads stay behind their owner’s adapter.
12. **Audit and observability do not replace domain truth.** A log entry cannot prove a point balance, redemption, entry, winning, tax state, or fulfillment state.
13. **Asynchronous execution is durable, idempotent, and observable.** Retries cannot duplicate points, entries, winners, redemptions, taxable-value reports, or fulfillment effects.
14. **Direct cross-Module Prisma reads are not the default integration pattern.** Use owner public interfaces or versioned domain events.
15. **Legal-gated activation is stricter than draft configuration.** Draft records may be created before legal review; production activation, entry issuance, winner selection, and fulfillment must satisfy the required architecture and legal gates.
16. **No generic “incentive service.”** Similar-looking mechanics may reuse canonical primitives, but domain rules remain in the owning Module.

---

## 5. Runtime / Collaboration Topology

### Primary topology

```text
Browser / admin surface / public action / source Module event
                    │
                    ▼
        thin route / server-action adapter
                    │
                    ▼
         owning Module application service
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
 canonical shared ops     owner domain policy
(auth, authz, consent,    (rules, eligibility,
holds, idempotency,       transitions, value,
locks, outbox, jobs,      odds, redemption)
audit, telemetry)
          │                   │
          └─────────┬─────────┘
                    ▼
          owner repository / transaction
                    │
                    ▼
        authoritative Workin Ants records
                    │
             transactional outbox
                    │
                    ▼
      workers / downstream Module consumers
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
 Notification   Payment/Tax     Audit/Ops
 owner          owner           owners
```

### Gamification event flow

```text
Source Module lifecycle change
→ source Module publishes versioned domain event
→ SH-045 consumer dedupe
→ Gamification rule evaluation
→ SH-044 idempotent command
→ append PointLedgerEntry in Gamification transaction
→ SH-046 outbox event
→ projection/reward/challenge consumers
→ SH-029 audit when material/admin-sensitive
→ SH-033/037/038 operational telemetry
```

The Gamification worker must not inspect another Module’s database to decide whether the source event “really happened.” The source Module’s public event or query is authoritative.

### Purchase-triggered sweepstakes entry

**Source conflict:** the Cluster/legacy technology notes mention a Stripe webhook if a purchase creates an entry, while the Sweepstakes Module explicitly does not own Stripe webhook handling and the platform rules keep `ProcessedStripeEvent` with Payment / Payout / Tax.

**Proposed Ruling PR-CL10-01:**

```text
Stripe
→ Payment / Payout / Tax provider adapter and ProcessedStripeEvent
→ Transaction / Order or Payment owner establishes authoritative qualifying outcome
→ versioned owner event / public command
→ Sweepstakes / Prize validates configured purchase-triggered method
→ PrizeEntry(orderId=authoritative Order)
```

Sweepstakes / Prize must **not** expose its own Stripe webhook route, signature verifier, or `ProcessedStripeEvent` table.

### Secure drawing flow

```text
Scheduled/admin drawing trigger
→ authorization / optional step-up
→ acquire aggregate lock
→ close/freeze eligible population
→ verify AMOE/equivalent-odds policy
→ SH-116 secureRandomSelection
→ immutable drawing-run proof  [schema contract unresolved; see U-CL10-02]
→ create PrizeWinning record(s)
→ update PrizeDrawing state
→ transactional outbox
→ tax/hold/notification workflows
```

A notification of winning is downstream communication; it is not the winning record and cannot advance fulfillment by itself.

---

## 6. Folder / Code Organization

The root Workin Ants repository owns the final folder convention through `code-standards.md`. The following is a **Proposed Ruling (PR-CL10-02)** for the domain organization if the root architecture has not already chosen equivalent paths.

```text
src/
  modules/
    gamification-rewards/
      domain/
        policies/
        types/
      application/
        commands/
        queries/
        services/
      contracts/
        public.ts
        events.ts
      infrastructure/
        repositories/
        projections/
        providers/        # only provider adapters actually owned here
      workers/
      admin/              # admin-facing feature composition, if repository conventions allow
      tests/

    sweepstakes-prize/
      domain/
        policies/
        types/
      application/
        commands/
        queries/
        services/
      contracts/
        public.ts
        events.ts
      infrastructure/
        repositories/
        randomness/
        providers/        # only future provider adapters owned here
      workers/
      admin/
      tests/

  platform/
    ... canonical implementations referenced by SH-### IDs ...

  app/
    ... thin routes/server actions/UI adapters following root conventions ...

tests/
  integration/
    cl-10/
      gamification-event-to-points.*
      reward-redemption.*
      sweepstakes-entry.*
      secure-drawing.*
      tax-hold-fulfillment.*
      privacy-contract.*
```

### Folder rules

- Domain and application code lives with the **owning Module**.
- There is no production `src/clusters/cl-10/incentiveService` that owns business truth.
- Cluster-local code is permitted only for coordination that genuinely has no natural Module owner. No such source-truth coordination service is currently confirmed.
- Shared platform folders may contain only approved platform primitives/capabilities represented by the root architecture or Canonical Shared Operations Registry.
- Do not create `shared/rewards`, `shared/prizes`, `shared/ledger`, or `shared/fraud` solely because code appears similar.
- Provider adapters live with their explicit provider-owning Module. Tax and Stripe adapters remain outside CL-10 unless a future reward/prize provider is explicitly assigned to a CL-10 Module.
- Jobs are defined beside the owner workflow but execute through the canonical queue/job infrastructure.
- Public contracts are narrow DTOs/events. They must not expose Prisma models as cross-Module contracts.

---

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
|---|---|---|---|
| Gamification / Rewards | Program/rule policy; point ledger; challenge state; leaderboard projection policy; reward catalog; reward redemption state; reward FMV snapshot when recorded | User/profile identifiers; authoritative source events; Consent proof; holds; tax readiness; notifications; audit; entitlements only through approved deterministic contract | Prize drawings/entries/winnings; TaxProfile; payment/payout execution; subscription truth; generic hold/audit/notification/queue truth |
| Sweepstakes / Prize | Drawing configuration/state; entry methods; PrizeEntry; entry eligibility/odds policy; secure draw policy; PrizeWinning; prize FMV; PrizeTaxYearSummary; fulfillment state | User; Order references/outcome events; Consent proof; holds; tax readiness; notifications; audit | Points/rewards; Order/payment lifecycle; Stripe webhooks; TaxProfile verification; generic hold/audit/notification/queue truth |
| Identity & Access | Authentication/session/security/step-up lifecycle | Resource/action context | Gamification or prize business policy |
| Role / Authority | Permission interpretation | CL-10 relationship/action facts | Reward eligibility, tax readiness, AMOE, prize odds, redemption state |
| Consent & Disclosure | Consent version catalog and `ConsentLog` proof | CL-10-required consent types and context | Reward/prize permission decisions or lifecycle state |
| Transaction / Order | Order transaction truth and qualifying order lifecycle facts | Gamification or Sweepstakes requests/events | Point ledger, PrizeEntry, reward/prize fulfillment state |
| Payment / Payout / Tax | TaxProfile, tax documents, tax reporting/submission truth, Stripe/webhook truth, financial readiness | CL-10 recognized value/FMV and source references | PrizeWinning/RewardRedemption lifecycle or chance policy |
| Track Subscription & Entitlement | Subscription, entitlement grants, usage metering | Reward-earned benefit requests where approved | Point ledger, reward redemption, prize odds, PrizeEntry |
| Admin Review / Compliance Hold | ComplianceHold lifecycle, release, review queue | CL-10 evidence and hold requests | Underlying reward/prize lifecycle or tax truth |
| Notification | Notification and delivery lifecycle | CL-10 notification requests/events | Entry acceptance, winning, redemption, or fulfillment truth |
| Audit / Event Ledger | Generic AuditEvent and AccessAuditLog proof | Safe CL-10 actor/action/target metadata | PointLedgerEntry, PrizeEntry, PrizeWinning, RewardRedemption, outbox/domain truth |
| Observability / Ops | Operational logs, integration/queue failure visibility, incidents/telemetry | Safe request/job/provider metadata | Business lifecycle state or compliance decision |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob orchestration and retention exemption records | CL-10 subject-data inventory and execution results | Direct uncoordinated rewriting of all CL-10 records |
| Search / Public Visibility | Search indexing/projection mechanics | Approved deterministic boost effect from its owner | Point, redemption, prize, or entitlement truth |
| CL-10 Cluster | Cross-Module invariants, integration plan, tests, context | Both Module public contracts | Any lifecycle, ledger, provider event, or generic “incentive” source truth |

---

## 8. Data Ownership

### 8.1 CL-10-owned records and enums

| Record / enum | Owner | Meaning / source-of-truth role | Important constraints |
|---|---|---|---|
| `GamificationProgram` | Gamification / Rewards | Program configuration and lifecycle | `termsVersion` is a reference to disclosure/consent version context, not Consent truth. |
| `GamificationProgramStatus` | Gamification / Rewards | `draft`, `active`, `paused`, `ended`, `archived` | Transitions only through owner service. |
| `GamificationRule` | Gamification / Rewards | Rule mapping eligible activity to deterministic points | `ruleJson` must never contain executable code; see PR-CL10-03. |
| `GamificationRuleTrigger` | Gamification / Rewards | Controlled trigger vocabulary | Source events must be owner-authenticated; trigger enum does not grant cross-Module read permission. |
| `PointLedgerEntry` | Gamification / Rewards | Append-only point value truth | Never update/delete to change balance in normal workflow; use reversal/adjustment entries. |
| `PointLedgerEntryType` | Gamification / Rewards | `earned`, `spent`, `reversed`, `expired`, `adjusted` | Point sign and legal combinations are owner policy. |
| `PointLedgerEntrySource` | Gamification / Rewards | Challenge/milestone/order/review/profile/reward/admin/system provenance | Source enum does not replace source-event ID/dedupe proof. |
| `Challenge` | Gamification / Rewards | Challenge configuration/lifecycle | Uses `ChallengeStatus`. |
| `ChallengeParticipant` | Gamification / Rewards | User participation/completion proof | Current schema reuses `ChallengeStatus`; semantic constraint discussed in U-CL10-04. |
| `Leaderboard` | Gamification / Rewards | Defines a ranking projection window/context | Not point source truth. |
| `LeaderboardEntry` | Gamification / Rewards | Derived ranking projection | Rebuildable; unique per leaderboard/user. |
| `Reward` | Gamification / Rewards | Reward catalog/configuration | `RewardType` effect does not transfer ownership of the target system. |
| `RewardType` | Gamification / Rewards | `badge`, `gift_card`, `cash_bonus`, `profile_boost`, `physical_prize`, `platform_credit`, `other` | Some fulfillment effects are unresolved; enum existence does not mean provider support exists. |
| `RewardStatus` | Gamification / Rewards | `draft`, `active`, `paused`, `retired` | Only activate reward types with an approved fulfillment path. |
| `RewardRedemption` | Gamification / Rewards | User claim/redemption lifecycle and value snapshot | Links to hold and tax profile but does not own either. |
| `RewardRedemptionStatus` | Gamification / Rewards | `pending_confirmation`, `pending_tax`, `approved`, `fulfilled`, `blocked`, `cancelled`, `reversed` | Owner controls transitions; provider result cannot mutate directly. |
| `PrizeDrawing` | Sweepstakes / Prize | Chance-based drawing configuration/lifecycle | AMOE/no-purchase configuration is domain policy; `officialRulesUrl` alone does not establish immutable rule proof. |
| `PrizeDrawingStatus` | Sweepstakes / Prize | `draft`, `active`, `closed`, `drawing`, `completed`, `cancelled` | `drawing` must be lock-protected and single-execution. |
| `SweepstakesEntryMethod` | Sweepstakes / Prize | Configured route by which entries are issued | Free/purchase distinction and equivalent-odds policy are Sweepstakes truth. |
| `SweepstakesEntryMethodType` | Sweepstakes / Prize | `purchase_triggered`, `free_daily_button`, `mail_in`, `admin_adjustment`, `system` | `purchase_triggered` consumes owner-issued Order/payment facts, not Stripe directly. |
| `SweepstakesEntryMethodStatus` | Sweepstakes / Prize | `active`, `paused`, `retired` | Retired method must not issue new entries. |
| `PrizeEntry` | Sweepstakes / Prize | One auditable entry into a drawing | `entryToken` is unique; source-event idempotency still required. `rulesConsentId` currently lacks Prisma relation. |
| `PrizeEntrySource` | Sweepstakes / Prize | `purchase`, `free_daily`, `mail_in`, `admin_adjustment`, `system` | A source value does not itself prove eligibility or consent. |
| `PrizeWinning` | Sweepstakes / Prize | Winner record, FMV snapshot, tax-gate linkage, fulfillment status | Notification/provider state is not winning truth. |
| `PrizeWinningStatus` | Sweepstakes / Prize | `pending_tax`, `pending_confirmation`, `approved`, `fulfilled`, `blocked`, `forfeited`, `cancelled` | Tax or hold owner supplies facts; Sweepstakes chooses its transition. |
| `PrizeTaxYearSummary` | Sweepstakes / Prize | Year/currency aggregate of prize FMV and winning count | Separate from Tax-owned `TaxYearEarningsSummary`; must be rebuildable/reconcilable. |

### 8.2 External records referenced by CL-10

| Record / proof | Owner | CL-10 use | Forbidden inference |
|---|---|---|---|
| `User` | Identity & Access | Actor/recipient identifier | User alone does not imply permission, tax readiness, or reward/prize eligibility. |
| `ProfessionalProfile` | Professional Eligibility | Optional context for point/redemption activity | Gamification does not own profile lifecycle. |
| `Order` | Transaction / Order | Provenance for order-based points or purchase-triggered entries | `Order` is not `PrizeEntry` and payment provider state is not Order truth. |
| `Review` | Review / Dispute | Potential authoritative trigger for high-rating rule | Gamification must consume owner event/query, not direct cross-domain persistence. |
| `ConsentLog` | Consent & Disclosure | Version-specific proof for program/reward/drawing rules | Consent proof does not itself authorize entry/redemption. |
| `TaxProfile` | Payment / Payout / Tax | Link/evidence reference for tax-gated fulfillment | `taxProfileId` on CL-10 records does not transfer TaxProfile ownership. |
| `TaxYearEarningsSummary` | Payment / Payout / Tax | Tax owner’s combined yearly reporting truth | Do not replace with `PrizeTaxYearSummary` or a Gamification local 1099 table. |
| `ComplianceHold` | Admin Review / Compliance Hold | Reusable stop sign linked from redemptions/winnings | `blockedByHoldId` is a reference, not a second hold lifecycle. |
| `TrackEntitlementGrant`, `TrackUsageEvent` | Track Subscription & Entitlement | Only approved deterministic feature/benefit effects | Never drive sweepstakes odds or become local premium fields. |
| `AuditEvent` | Audit / Event Ledger | Generic actor/action proof | Not a reward/prize lifecycle event ledger. |
| `AccessAuditLog` | Audit / Event Ledger | Sensitive winner/tax/admin read proof where required | Does not grant access. |
| `Notification` / delivery records | Notification | Communication outcome | Delivery does not prove redemption/winning fulfillment. |
| `ProcessedStripeEvent` | Payment / Payout / Tax | Upstream provider-event dedupe evidence only | Must not be recreated in Sweepstakes. |
| Privacy request/job/exemption records | Privacy / Data Erasure | Orchestration and retention decisions | CL-10 does not create privacy workflows. |
| Search projection records | Search / Public Visibility | Potential downstream effect of approved profile boost | Search never reconstructs point/reward truth. |
| Observability records | Observability / Ops | Queue/integration/incident visibility | Operational success is not business success. |

### 8.3 Projections and snapshots

- **Point balance:** derived from `PointLedgerEntry`; source truth is the ledger.
- **LeaderboardEntry:** Gamification-owned projection; rebuildable through SH-115.
- **PrizeTaxYearSummary:** Sweepstakes-owned aggregate; rebuildable through SH-117.
- **TaxYearEarningsSummary:** Payment / Payout / Tax-owned combined reporting aggregate; receives source-recognition facts through SH-118.
- **Search/profile boost:** external projection/effect only. Gamification may own why a benefit was earned, not the target feature’s projection truth.

### 8.4 Processed-provider-event records

CL-10 currently owns **no confirmed processed-provider-event table**. `ProcessedStripeEvent` belongs to Payment / Payout / Tax. A future gift-card, prize-shipping, or other fulfillment provider must receive an explicit provider-ownership ruling and domain-specific dedupe design before a CL-10 processed-event record is added.

---

## 9. Lifecycle Ownership

The schema provides the status vocabularies. Some transition graphs are not explicitly defined in the supplied evidence. Those graphs are therefore proposed, not silently assumed.

### 9.1 GamificationProgram lifecycle

- **Owner:** Gamification / Rewards
- **Statuses:** `draft`, `active`, `paused`, `ended`, `archived`
- **Transition authority:** Gamification application service only.
- **Proposed Ruling PR-CL10-04:**

```text
draft → active
active → paused | ended
paused → active | ended
ended → archived
```

`archived` is terminal. Any additional transition requires an architecture change.

Other Modules may react to program activation/ending but cannot mutate status.

### 9.2 Point ledger lifecycle

`PointLedgerEntry` is **not** a mutable lifecycle. It is append-only value truth.

Corrections occur by new entries:

```text
original earned/spent entry
→ reversal entry where required
→ optional corrected/adjusted entry
```

A worker or admin must never rewrite historical `points` to “fix the balance.”

### 9.3 Challenge lifecycle

- **Owner:** Gamification / Rewards
- **Statuses:** `draft`, `active`, `paused`, `completed`, `cancelled`, `archived`
- **Proposed transition graph:**

```text
draft → active | cancelled
active → paused | completed | cancelled
paused → active | completed | cancelled
completed | cancelled → archived
```

`ChallengeParticipant.status` currently reuses `ChallengeStatus`. Until U-CL10-04 is resolved, owner services must reject semantically invalid participant values such as `draft` or `archived` unless an approved participant-state definition explicitly allows them.

### 9.4 Reward lifecycle

- **Owner:** Gamification / Rewards
- **Statuses:** `draft`, `active`, `paused`, `retired`
- **Proposed transition graph:**

```text
draft → active | retired
active → paused | retired
paused → active | retired
```

Activation must fail if the reward type has no approved fulfillment/effect contract.

### 9.5 RewardRedemption lifecycle

- **Owner:** Gamification / Rewards
- **Statuses:** `pending_confirmation`, `pending_tax`, `approved`, `fulfilled`, `blocked`, `cancelled`, `reversed`
- **Other Modules may:** return tax-readiness decisions, create/release holds, perform financial/entitlement/provider effects through owned interfaces, and deliver notifications.
- **Other Modules may not:** set `RewardRedemption.status` directly.

**Proposed Ruling PR-CL10-05:** the owner service must implement an explicit transition matrix. At minimum, fulfillment cannot occur from `pending_tax` or `blocked`; a `fulfilled` redemption cannot be deleted or rewritten to hide fulfillment; a correction uses `reversed` plus compensating point/effect operations where the reward type supports reversal.

The precise reopen path from `blocked` after hold release and the treatment of cancellation after `approved` must be finalized in the Module architecture before implementation.

### 9.6 PrizeDrawing lifecycle

- **Owner:** Sweepstakes / Prize
- **Statuses:** `draft`, `active`, `closed`, `drawing`, `completed`, `cancelled`
- **Proposed Ruling PR-CL10-06:**

```text
draft → active | cancelled
active → closed | cancelled
closed → drawing | cancelled
drawing → completed
```

`drawing` is entered only by a lock-protected drawing command. `completed` and `cancelled` are terminal for ordinary operations. Re-draw policy is unresolved and must not be implemented by reopening a completed drawing without an approved rule.

### 9.7 SweepstakesEntryMethod lifecycle

- **Owner:** Sweepstakes / Prize
- **Statuses:** `active`, `paused`, `retired`
- **Proposed transition graph:** `active ↔ paused`, and `active|paused → retired`; `retired` terminal.

### 9.8 PrizeEntry record behavior

`PrizeEntry` has no status lifecycle. It is an issuance record with eligibility fields.

**Proposed Ruling PR-CL10-07:**

- entry creation is idempotent by business source, not merely `entryToken` uniqueness;
- normal workflows do not delete or overwrite an issued entry to change counts;
- eligibility correction must be auditable;
- once the drawing population is frozen for a run, the selected population cannot be mutated underneath that run;
- any post-freeze correction requires an explicit void/redraw policy, not an ad hoc row edit.

### 9.9 PrizeWinning lifecycle

- **Owner:** Sweepstakes / Prize
- **Statuses:** `pending_tax`, `pending_confirmation`, `approved`, `fulfilled`, `blocked`, `forfeited`, `cancelled`
- **Other Modules may:** return tax facts; create/release holds; notify; audit; perform future provider effects.
- **Other Modules may not:** set winning status directly.

**Proposed Ruling PR-CL10-08:** fulfillment is permitted only from `approved`, after re-checking applicable holds and tax readiness. `fulfilled`, `forfeited`, and `cancelled` are terminal unless a future explicit correction model is approved. A winner message never advances status.

### 9.10 PrizeTaxYearSummary

This is a derived yearly aggregate, not a lifecycle. Sweepstakes owns rebuild and reconciliation from recognized `PrizeWinning` value facts. Payment / Payout / Tax may consume its output but does not mutate it as tax truth.

---

## 10. Public Module Interfaces

The source set establishes ownership but does not provide final TypeScript interface names. The names below are **Proposed interface names**; their semantics are binding once approved, while exact code naming may follow root standards.

### 10.1 Gamification / Rewards interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
|---|---|---|---|---|---|---|---|
| `recordEligibleActivity` | Gamification / Rewards | Internal event consumers from Order, Review, Professional/Profile sources | Evaluate a source event against active gamification rules and append deterministic point entries exactly once. | source event ID/type/version, subject user/profile, occurredAt, source reference, safe event facts | applied rule IDs, ledger entry IDs, no-op/reason | Domain decision + truth references | Rule evaluation, point signs, source dedupe semantics |
| `appendManualPointAdjustment` | Gamification / Rewards | Authorized admin/support workflow | Add an audited adjustment/reversal without mutating history. | actor, user, program?, points, reason, correlation/idempotency key | ledger entry ID, resulting projected balance | Truth + projection | Direct ledger writes or balance mutation |
| `getPointLedger` | Gamification / Rewards | User/admin/consuming UI | Return authorized point history. | subject, cursor/filter | ledger DTOs | Truth | Cross-domain joins or hidden balance mutation |
| `getPointBalance` | Gamification / Rewards | User/admin/eligible feature consumer | Return derived available point balance and projection version/evidence. | subject, program/context | balance, asOf/checkpoint, confidence/lag if projected | Projection | Treat balance as independent truth |
| `joinChallenge` | Gamification / Rewards | User-facing action | Create/confirm ChallengeParticipant where challenge rules permit. | actor, challengeId, profile context, idempotency key | participant state | Truth | Challenge lifecycle ownership |
| `requestRewardRedemption` | Gamification / Rewards | User-facing action | Atomically validate reward, reserve/spend points as required, and create redemption. | actor, rewardId, profile context, required consent proof reference, idempotency key | redemption ID/status, point ledger refs, next required action | Truth + decision | Tax/hold/entitlement truth or point balance mutation |
| `transitionRewardRedemption` | Gamification / Rewards | Owner workers/admin workflows | Move redemption using owner transition rules after external decisions/effects. | redemptionId, requested transition, actor/system context, evidence refs, idempotency key | new status + evidence refs | Truth | Direct status updates from provider callbacks |
| `getRewardRedemption` | Gamification / Rewards | User/admin/downstream tax/notification composition | Read safe redemption state and value snapshot. | authorized subject/redemptionId | safe redemption DTO | Truth | Tax readiness or payment completion |
| `getLeaderboard` | Gamification / Rewards | User/admin UI | Read ranking projection. | leaderboardId, cursor | ranked entries + projection checkpoint | Projection | Point ledger truth or eligibility beyond owner policy |

### 10.2 Sweepstakes / Prize interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
|---|---|---|---|---|---|---|---|
| `configurePrizeDrawing` | Sweepstakes / Prize | Authorized admin | Create/update draft drawing and entry methods under owner validation. | actor, drawing fields, entry-method configuration, policy/rules references | drawing DTO + validation results | Truth | Legal approval or consent proof |
| `activatePrizeDrawing` | Sweepstakes / Prize | Authorized admin | Activate only after timing, rules, consent, AMOE, equivalent-odds, and legal gates pass. | actor, drawingId, approved rules evidence, idempotency key | active drawing or denial reasons | Decision + truth | Consent version catalog or legal drafting |
| `issuePrizeEntry` | Sweepstakes / Prize | Free-entry action, mail/admin workflow, authoritative Order event consumer | Issue exactly the entries allowed by one configured method/source. | drawingId, userId, methodId/source, source event/order ref, consent proof ref, idempotency key | PrizeEntry IDs/tokens or denial | Truth + decision | Order/payment truth, consent truth, or point truth |
| `evaluatePrizeEntryEligibility` | Sweepstakes / Prize | Entry flow/drawing worker/admin review | Determine CL-10-specific eligibility under drawing policy. | drawing/method/user/context facts | eligible flag, reason codes, evidence refs | Decision | Authorization, tax, or hold lifecycle truth |
| `runPrizeDrawing` | Sweepstakes / Prize | Scheduled/authorized worker | Freeze eligible population and select winners securely once. | drawingId, run request ID, actor/system context | run proof ref, winning IDs, final draw state | Truth + evidence | Random selection algorithm implementation outside owner or ad hoc row reads |
| `transitionPrizeWinning` | Sweepstakes / Prize | Owner admin/worker after hold/tax/provider decision | Advance winning state. | winningId, requested transition, evidence refs, idempotency key | new state + next action | Truth | TaxProfile status or hold lifecycle implementation |
| `getPrizeWinning` | Sweepstakes / Prize | Winner/admin/tax/notification composition | Read authorized winning truth. | winningId/subject | safe winning DTO | Truth | Notification or fulfillment provider state |
| `getPrizeTaxYearSummary` | Sweepstakes / Prize | Payment / Payout / Tax, admin reconciliation | Return Sweepstakes-owned yearly prize aggregate. | userId, taxYear, currency | FMV total, count, threshold metadata, checkpoint/rebuild info | Projection/aggregate | Combined tax filing truth |

### 10.3 Source-event contracts consumed by Gamification

The following trigger families are confirmed by `GamificationRuleTrigger`, but their exact source event names are not supplied:

- `profile_completed` — owner event from the profile-owning Module.
- `order_completed` — owner event from Transaction / Order.
- `delivery_on_time` — source owner must be identified by root/Module architecture before activation.
- `high_rating_received` — owner event from Review / Dispute.
- `challenge_completed` — internal Gamification event.
- admin/fraud/system adjustment triggers — owner-internal commands with authorization/audit.

No trigger may be implemented as a cross-domain polling query merely because a source event is not yet available.

---

## 11. Canonical Shared Operations Used by This Cluster

Only CL-10-relevant operations are listed here. The global definitions remain in `context/shared/shared-operations.md`.

### Identity, authority, consent, holds, and financial gates

| ID / operation | Canonical owner | Consuming CL-10 Modules | Reusable mechanism | Local policy that remains in CL-10 | Invocation point | Must not duplicate |
|---|---|---|---|---|---|---|
| **SH-001 `resolveAuthenticatedActor`** | Identity & Access | Both | Trusted actor context | Which reward/prize action requires an authenticated actor | All protected user/admin commands | `gamificationAuth.ts`, `prizeAuth.ts`, local current-user/session helpers |
| **SH-002 `authorizeResourceAction`** | Role / Authority | Both | Typed authorization decision | Action vocabulary and resource relationship facts | Before every protected mutation/read | `rewardPermissions.ts`, `prizeAdminGuard.ts`, local role engine |
| **SH-008 `queryConsentProof`** | Consent & Disclosure | Both | Version-specific proof lookup | Which terms/rules version is sufficient for the action | Program/reward/drawing entry and redemption gates | local Consent tables/checkers |
| **SH-009 `resolveActiveConsentVersion`** | Consent & Disclosure | Both | Effective version resolution | Which consent type the Module requires | Configuration/activation and user acceptance flow | local terms-version resolver |
| **SH-011 `evaluateComplianceHold`** | Admin Review / Compliance Hold | Both | Active hold decision | Which hold scopes block redemption, entry, drawing, winner approval, fulfillment | Before sensitive/fulfillment actions | `rewardBlocked.ts`, `winnerHoldService.ts`, local blocked flags |
| **SH-012 `requestComplianceHold`** | Admin Review / Compliance Hold | Both | Idempotent hold request | Evidence/reason from reward abuse or sweepstakes review | Fraud/compliance/manual review escalation | local hold rows or review stop-state service |
| **SH-014 `requireStepUpForSensitiveAction`** | Identity & Access | Both, for actions classified sensitive | Fresh assurance session | Which CL-10 actions root policy classifies high risk | Before manual point corrections, drawing overrides, or fulfillment approval where policy requires | local MFA prompt/session logic |
| **SH-019 `evaluateFinancialReadiness`** | Payment / Payout / Tax | Both | KYC/tax/payout readiness dimensions | Whether a reward/winning requires tax readiness and how result maps to owner status | Before taxable/reportable fulfillment | `w9Gate.ts`, `prizeTaxCheck.ts`, local tax-approved boolean |

### Audit, observability, idempotency, events, jobs, and concurrency

| ID / operation | Canonical owner | Consumers | Reusable mechanism | Local policy | Invocation point | Must not duplicate |
|---|---|---|---|---|---|---|
| **SH-029 `appendAuditEvent`** | Audit / Event Ledger | Both | Generic append-only audit proof | CL-10 action names, reason codes, safe metadata | Material admin actions and sensitive state changes | `prizeAudit.ts`, `rewardAudit.ts`, generic audit repositories |
| **SH-030 `recordSensitiveAccess`** | Audit / Event Ledger | Both where tax/winner/redemption data is sensitive | AccessAuditLog | Sensitivity classification and target context | Sensitive admin reads/exports where root policy requires | `winnerDataAudit.ts`, local access log |
| **SH-031 `appendDomainLifecycleEvent`** | Shared persistence mechanism; domain keeps truth | Gamification primarily | Append-only ledger/event mechanics | Point types/signs/reversal semantics | `PointLedgerEntry` append transaction | a generic merged platform ledger |
| **SH-032 `createRequestContext`** | Observability/platform | Both | Correlation/request/actor propagation | Safe domain IDs included | Request → outbox → job → downstream call | local correlation ID helper |
| **SH-033 `writeStructuredLog`** | Observability / Ops | Both | Structured operational logger | CL-10 operation labels and safe IDs | All server/worker execution | `sweepstakesLogger.ts`, feature loggers |
| **SH-034 `sanitizeTelemetryMetadata`** | Observability / Ops + Audit payload policy | Both | Redaction/allowlist/truncation | Sensitivity labels | Before logs/audit/failure telemetry | local telemetry sanitizer |
| **SH-037 `recordIntegrationFailure`** | Observability / Ops | Both | Normalized provider/worker failure evidence | Whether business state also changes | Provider/downstream failure after owner state decision | local ops-failure tables |
| **SH-038 `recordQueueTelemetry`** | Observability / Ops/shared queue | Both | Job attempt/retry/dead-letter telemetry | Domain job name and safe source refs | Every CL-10 worker | local QueueJob truth |
| **SH-041 `requestNotification`** | Notification | Both | Delivery request contract | When/why to notify and safe template context | Entry/redemption/winner/tax/fulfillment events | `winnerEmailService.ts`, `rewardPush.ts` |
| **SH-044 `executeIdempotentCommand`** | Platform primitive | Both | Command idempotency record/execution | Semantic key for points, entries, drawings, redemptions, fulfillment | Before every retryable mutation | local idempotency table/helper |
| **SH-045 `deduplicateDomainEvent`** | Platform event infrastructure | Gamification and purchase-entry consumers | Consumer inbox/processed-event mechanism | Whether one source event may cause one effect, one-per-rule, etc. | On inbound owner domain events | `processedGamificationEvent.ts`, `dedupeEntry.ts` |
| **SH-046 `publishDomainEvent`** | Transactional outbox capability | Both | Atomic outbox/event envelope | Event names, aggregate IDs, safe payload | With owner state mutation | `gamificationEventBus.ts`, `prizePublisher.ts` |
| **SH-047 `enqueueReliableJob`** | Shared queue infrastructure | Both | Durable job scheduling/execution | Drawing/projection/aggregation/reconciliation job identity | Async work dispatch | `prizeQueue.ts`, `gamificationQueue.ts` |
| **SH-048 `retryWithBackoff`** | Shared queue/platform | Both | Retry policy/backoff/dead-letter | Which failures are retryable vs terminal | Worker/provider/downstream failures | feature retry loops |
| **SH-051 `acquireAggregateLock`** | Platform/database primitive | Both | DB/advisory/aggregate lock | Lock key and protected aggregate | Drawing execution; competing redemption/inventory operations where needed | in-memory mutex or local lock table |
| **SH-053 `transitionLifecycleState`** | Shared transition mechanism; owner supplies policy | Both | Current-state + allowed-transition enforcement | Each Module’s transition matrix | Every status mutation | generic status service with cross-domain policy |
| **SH-056 `executeAtomicReservation`** | Database/platform concurrency primitive | Gamification / Rewards | Atomic scarce-resource reservation | Point sufficiency and limited-reward policy | Redemption transaction | `rewardBalanceService.ts` or non-transactional check-then-write |

### Privacy, projections, randomness, tax value

| ID / operation | Canonical owner | Consumers | Reusable mechanism | Local policy | Invocation point | Must not duplicate |
|---|---|---|---|---|---|---|
| **SH-095 `executePrivacyInstruction`** | Privacy orchestrates; data owner executes | Both | Owner privacy-target command protocol | Field disposition and owner invariants | Privacy job callback | local PrivacyRequest workflow |
| **SH-096 `enumerateSubjectData`** | Each owner through Privacy interface | Both | Subject-data inventory contract | Which CL-10 records belong to subject | Privacy inventory/export | generic DB crawler |
| **SH-097 `evaluateRetentionRequirement`** | Data owner facts; Privacy records exemption | Both | Retention decision contract | Prize/tax/fraud/reward evidence requirements | Before erasure/anonymization | local retention-exemption table |
| **SH-098 `anonymizePersonalFields`** | Shared primitive; owner supplies map | Both | Versioned field scrubbing | CL-10 permitted anonymization | Privacy execution | global unscoped anonymizer |
| **SH-115 `buildAggregateProjection`** | Projection owner | Gamification / Rewards | Rebuildable aggregate/read model | Point balance and leaderboard inclusion/rank policy | After ledger/challenge events and backfill | ad hoc mutable point-balance truth |
| **SH-116 `secureRandomSelection`** | Sweepstakes / Prize | Sweepstakes / Prize | CSPRNG/unbiased sampling primitive | Population, weights, winner count, redraw/repeat-winner policy | Drawing worker | `Math.random()`, generic raffle utility outside owner |
| **SH-117 `aggregateYearlyReportableValue`** | Each value owner; tax consumes | Sweepstakes; reward value reconciliation as needed | Rebuildable yearly aggregation | Recognition timing and CL-10 source inclusion | Prize winning recognition / reconciliation | merged prize+reward tax cache |
| **SH-118 `reportTaxableValue`** | Payment / Payout / Tax | Both | Tax-owner public value-reporting interface | Source FMV snapshot and recognition event | When reportable value is recognized per owner policy | CL-10 filing/1099 service |

### Conditional / proposed shared operation

**SH-119 `applyTemporaryFeatureGrant`** is a **Proposed Ruling** in the canonical registry. It is required only if a deterministic reward such as `profile_boost` is implemented as a time-bound platform benefit. Gamification owns why the reward was earned; Track Subscription & Entitlement or the affected feature owns the grant/effect according to the final ruling. It must never affect sweepstakes odds. Do not implement `profileBoost=true` or a local premium flag while SH-119 ownership remains unapproved.

### Proposed rule-integrity primitives

If the approved solution for immutable sweepstakes official-rules proof uses canonical text/hashing, reuse **SH-077 `buildCanonicalTextSnapshot`** and **SH-072 `hashCanonicalPayload`**. Do not create a Sweepstakes-only hashing library. The exact rule snapshot schema is unresolved in U-CL10-01.

---

## 12. Cross-Module Data Flows

### Flow A — Order completion awards deterministic points

```text
Transaction / Order commits qualifying completion
→ Transaction / Order publishes authoritative versioned event
→ Gamification worker receives event
→ SH-045 deduplicates event delivery
→ Gamification resolves applicable active rules
→ SH-044 executes rule application idempotently
→ Gamification appends PointLedgerEntry for each valid rule
→ Gamification emits point-ledgered event through SH-046
→ SH-115 refreshes balance/leaderboard/challenge projections as needed
→ SH-029 records material admin/system proof where required
→ Notification may be requested through SH-041
```

Owner of business point decision: **Gamification / Rewards**.  
Owner of Order truth: **Transaction / Order**.

### Flow B — Challenge completion awards points

```text
User joins Challenge
→ Gamification validates challenge/program state and consent
→ ChallengeParticipant truth is created
→ owner event(s) update progress through approved source facts
→ Gamification marks participant completion under owner rules
→ internal challenge_completed trigger is evaluated
→ PointLedgerEntry appended
→ leaderboard/balance projection rebuilt
```

Challenge state must not be inferred from leaderboard rank.

### Flow C — Reward redemption

```text
User requests Reward redemption
→ SH-001 actor
→ SH-002 authorization
→ SH-008 terms/consent proof where required
→ SH-011 applicable hold check
→ Gamification validates Reward status, point cost, inventory/effect support
→ SH-056 atomic reservation / point-spend transaction
→ RewardRedemption created
→ PointLedgerEntry(type=spent, source=reward_redemption) appended if points are spent
→ SH-046 event
→ tax/effect/fulfillment branch
→ owner transitions RewardRedemption only after downstream decision/evidence
→ SH-041 notification
```

A provider or admin screen cannot bypass the atomic point/redemption transaction.

### Flow D — Tax-aware reward fulfillment

```text
RewardRedemption contains owner FMV snapshot where applicable
→ Gamification determines whether tax-readiness check is required by approved policy
→ SH-019 Payment/Tax readiness decision
→ if blocked/review needed: request/consume ComplianceHold and set owner status accordingly
→ if recognized reportable value: SH-118 reportTaxableValue
→ downstream fulfillment/effect through its owner
→ Gamification records resulting redemption transition
→ audit/notification/ops side effects
```

Tax owns filing/threshold/regime truth. Gamification must not hardcode “1099-NEC for every reward.”

### Flow E — Free/AMOE sweepstakes entry

```text
User invokes configured free entry method
→ actor/authz as required
→ Sweepstakes loads PrizeDrawing + entry method through own repository
→ resolve/query required rules consent
→ check drawing timing/status, method status, user limits, eligibility, holds if configured
→ verify free path and equivalent-odds invariant
→ SH-044 idempotent issue command
→ PrizeEntry(source=free_daily or mail_in/system as appropriate)
→ SH-046 event
→ optional SH-041 entry confirmation
```

The free path must not receive a hidden lower `weight` or fewer effective chances than an equivalent paid path unless an explicitly approved legal rule says otherwise.

### Flow F — Purchase-triggered sweepstakes entry

```text
Stripe event
→ Payment / Payout / Tax verifies/deduplicates provider event
→ Order/payment owner establishes qualifying business outcome
→ owner publishes qualifying versioned event with Order reference
→ Sweepstakes consumes event via SH-045
→ Sweepstakes validates active purchase-triggered method and AMOE/equivalent odds
→ SH-044 idempotent entry issuance keyed to drawing + method + authoritative source event/order semantics
→ PrizeEntry(orderId=Order.id, source=purchase)
```

Forbidden: Sweepstakes reads Stripe directly, creates `ProcessedStripeEvent`, or treats provider `payment_intent.succeeded` as PrizeEntry truth.

### Flow G — Secure winner selection

```text
Drawing reaches approved draw condition
→ SH-047 schedules worker or authorized admin starts command
→ SH-001/002 and SH-014 where required
→ SH-051 drawing aggregate lock
→ owner verifies state is closed and no competing run exists
→ freeze eligible entry population
→ enforce allowed weights/equivalent odds
→ SH-116 secureRandomSelection
→ persist immutable drawing-run proof [U-CL10-02]
→ create PrizeWinning snapshot(s)
→ transition PrizeDrawing drawing → completed in owner transaction
→ SH-046 events
→ SH-118/019 tax workflow and SH-041 winner communication downstream
```

### Flow H — Prize fulfillment with tax lock

```text
PrizeWinning pending_confirmation or pending_tax
→ Sweepstakes evaluates applicable holds through SH-011
→ Payment/Tax returns tax readiness through SH-019
→ Sweepstakes maps decision to its own PrizeWinning status
→ if value recognized, update/reconcile PrizeTaxYearSummary via SH-117
→ report value to Tax via SH-118
→ approved fulfillment effect/provider/manual process
→ provider result normalized by the provider-owning adapter if one exists
→ Sweepstakes transitions approved → fulfilled only after authoritative effect evidence
→ Notification/Audit/Ops side effects
```

Tax-blocked prizes must never be marked fulfilled merely because a shipment/message/provider call was attempted.

---

## 13. Cross-Cluster Bridges

| Source Cluster / Module | Destination Cluster / Module | Transfer | Authoritative owner | Interface/event | Forbidden coupling |
|---|---|---|---|---|---|
| CL-04 Transaction / Order | Gamification / Rewards | Completed-order/delivery facts that may award points | Transaction / Order for source event; Gamification for point decision | Versioned domain event → `recordEligibleActivity` | Gamification direct Order lifecycle mutation or polling private repositories |
| CL-04 Transaction / Order / Payment outcome | Sweepstakes / Prize | Qualifying purchase/order fact for configured entry | Order/payment source owner for purchase outcome; Sweepstakes for entry | Owner event → `issuePrizeEntry` | Direct Stripe webhook in Sweepstakes |
| CL-04 Review / Dispute | Gamification / Rewards | High-rating event | Review / Dispute | Versioned owner event | Gamification reading/modifying review internals |
| CL-03 Professional Eligibility | Gamification / Rewards | Profile-completed event/context | Professional Eligibility | Owner event / narrow query | Gamification setting profile status |
| CL-01 Consent & Disclosure | Both | Versioned acceptance proof | Consent & Disclosure | SH-008/009 | Local ConsentLog copies |
| CL-01 Track Subscription & Entitlement | Gamification / affected feature | Approved deterministic benefit/entitlement effect | Track/affected feature per contract | SH-119 if approved; SH-005 only where a defined feature gate exists | Entitlement-driven prize odds; local premium flags |
| CL-09 Admin Review / Compliance Hold | Both | Active/released hold decisions | Admin Review / Compliance Hold | SH-011/012 | Local hold systems |
| CL-03 Payment / Payout / Tax | Both | Tax readiness and reporting handoff | Payment / Payout / Tax | SH-019/118 | CL-10 TaxProfile verification/provider interpretation |
| CL-07 Notification | Both | Message delivery request/status | Notification | SH-041 / notification events | Treating delivery as domain fulfillment |
| CL-09 Audit / Event Ledger | Both | Generic audit/access evidence | Audit / Event Ledger | SH-029/030 | Audit as reward/prize truth |
| CL-09 Observability / Ops | Both | Queue/integration failure telemetry | Observability / Ops | SH-032/033/034/037/038 | QueueJob/IntegrationFailure as domain state |
| CL-08 Privacy / Data Erasure | Both | Enumerate/erase/anonymize/retain instruction | Privacy orchestrates; CL-10 owns record execution | SH-095–098 | Feature-local PrivacyRequest workflow |
| CL-02 Search / Public Visibility | Search/affected feature from Gamification benefit | Approved deterministic profile/search boost effect | Benefit/grant owner and Search projection owner | SH-119 plus Search public contract once approved | Gamification writing Typesense or `SearchUpsertEvent` directly without contract |

---

## 14. Authentication and Authorization

### Authentication

All protected CL-10 operations use **SH-001 `resolveAuthenticatedActor`**. No Module-local session or “current user” helper is allowed.

### Authorization

All protected reads and mutations use **SH-002 `authorizeResourceAction`**. CL-10 supplies:

- the action being attempted;
- target type/id;
- subject relationship facts owned by the target Module;
- whether the action is self-service, admin, support, or system initiated.

Role / Authority interprets permission. It must not absorb reward eligibility, AMOE, tax readiness, hold, or entitlement policy.

### Minimum action vocabulary

Proposed action families:

**Gamification:**
- view own points/redemptions;
- join challenge;
- redeem reward;
- configure program/rule/reward;
- manually adjust/reverse points;
- transition/fulfill/reverse redemption;
- inspect fraud/compliance evidence.

**Sweepstakes:**
- view drawing/own entries/own winnings;
- claim free entry;
- configure/activate/close/cancel drawing;
- configure entry method;
- mark entry eligibility exception;
- start/approve a drawing run;
- approve/forfeit/cancel/fulfill winning;
- inspect sensitive tax/winner evidence.

The exact role-to-capability matrix is not supplied and remains a root Role / Authority decision.

### Step-up

SH-014 is available for high-risk actions. **Proposed Ruling PR-CL10-09:** the root security policy should classify at least manual point-value changes, winner-selection overrides/redraws, and financially/tax-sensitive fulfillment approval for step-up consideration. CL-10 must consume the central assurance session rather than implementing MFA locally.

---

## 15. Compliance and Readiness Composition

### Sweepstakes / AMOE / no purchase necessary

Owner: **Sweepstakes / Prize**.

Activation and entry issuance must verify, where legally required:

- a valid free/AMOE entry method exists;
- the free method is usable during the required period;
- purchase is not the only route;
- effective odds are equivalent across required methods;
- entry limits do not create hidden paid advantage;
- `PrizeEntry.weight`, `entriesAwarded`, and rule configuration cannot secretly increase paid odds;
- applicable official rules/disclosure version is available and consent proof is collected where required.

Legal drafting itself is outside the Module.

### No pay-to-win / no paid prize odds boost

Joint invariant across Gamification / Rewards and Sweepstakes / Prize:

- users must not buy points for the purpose of improving chance-based odds;
- reward redemption cannot grant a better sweepstakes weight or exclusive paid-only chance;
- Track entitlements cannot boost prize odds;
- `profile_boost` may affect a deterministic platform feature only through its approved owner contract;
- if a future points-to-entry bridge is introduced, it requires explicit architecture/legal review and an equivalent free path. The current `PrizeEntrySource` does not model a points source, so no such bridge is part of the current architecture.

### Gamification reward disclosure

Owner: **Gamification / Rewards**, with Consent & Disclosure owning acceptance/version proof.

Programs and rewards must expose the applicable terms version and define:

- how points are earned/spent/reversed/expired/adjusted;
- challenge and leaderboard behavior;
- reward cost/value/availability;
- redemption conditions;
- tax implications where applicable;
- change/retirement behavior.

### Prize tax fulfillment lock

Composition:

```text
Sweepstakes PrizeWinning / PrizeTaxYearSummary value truth
+ Payment/Tax TaxProfile/readiness/reporting truth
+ Admin Review ComplianceHold stop sign
→ Sweepstakes-owned fulfillment decision
```

No single boolean such as `taxApproved` or `canFulfillPrize` becomes shared truth.

### Reward tax readiness

Gamification records reward/redemption value evidence. Payment / Payout / Tax owns TaxProfile and tax reporting. CL-10 may map a tax-readiness result to `pending_tax` or `blocked`, but it must not decide tax regime/filing provider truth itself.

### Verification / professional readiness / healthcare / Job compliance

No baseline CL-10 action is confirmed to require trust verification, healthcare readiness, or Job compliance. If a future reward or drawing eligibility rule references those facts, it must consume the owner’s public readiness interface. CL-10 must not add local verification booleans.

### Entitlements

No entitlement may affect sweepstakes odds. A deterministic reward that grants a platform perk must use the approved Track/feature contract. A direct baseline dependency on `resolveEntitlement` for ordinary points/reward behavior is not confirmed by the Module evidence and must not be invented.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Domain event families

Exact event names and versioning syntax follow root standards. Proposed semantic families:

**Gamification-owned outbound:**
- program activated/paused/ended;
- point entry appended;
- challenge joined/completed;
- reward redemption requested/status changed/fulfilled/reversed.

**Sweepstakes-owned outbound:**
- drawing activated/closed/drawing-started/completed/cancelled;
- prize entry issued/eligibility changed;
- winner selected;
- winning status changed/fulfilled/forfeited;
- prize yearly summary reconciled.

Events are emitted through SH-046 transactionally with the authoritative write. They are not a replacement for the owner tables.

### Required workers

- gamification source-event processor;
- point expiration worker only if expiration policy is later configured and approved;
- challenge/projection evaluator as required by challenge semantics;
- leaderboard/balance projection rebuild worker;
- reward fulfillment/reconciliation worker for approved asynchronous effects;
- drawing close/schedule worker;
- secure drawing worker;
- prize yearly aggregate reconciliation worker;
- tax-value reporting retry/reconciliation worker;
- privacy executor callback worker if Privacy uses async owner targets.

### Retry and idempotency

Every worker:

- uses SH-044 for business command idempotency;
- uses SH-045 for duplicate inbound domain events;
- uses SH-047/048 for durable execution/retry;
- uses SH-038 for queue telemetry;
- records permanent integration failure through SH-037 where appropriate;
- never treats a successful queue attempt as proof that business state changed.

### Concurrency

At minimum:

- point spending + redemption creation must be atomic;
- limited reward inventory must not oversubscribe;
- one drawing cannot have two competing active draw runs;
- per-user entry limits must be race-safe;
- yearly aggregate increments must be idempotent or rebuildable.

Use SH-051/056 and database constraints/transactions. Do not use process-memory locks.

### Dead letters

A dead-lettered job must:

1. preserve source/correlation identifiers;
2. record sanitized operational failure;
3. leave domain state in a valid, explainable state;
4. not fabricate a completed redemption, drawing, winning, or fulfillment;
5. be safe to retry after the underlying issue is corrected.

### Workflow / saga boundaries

A reward or prize fulfillment may span CL-10, Tax, Holds, Notification, and a future fulfillment provider. The **business lifecycle remains with RewardRedemption or PrizeWinning**. Generic workflow orchestration may coordinate execution but cannot become the source of fulfillment status.

---

## 17. Provider Integrations

### 17.1 Stripe / purchase-triggered entries

```text
Payment / Payout / Tax
→ Stripe provider-neutral payment port
→ Stripe adapter
→ Stripe
→ verified/deduplicated ProcessedStripeEvent
→ Payment/Order canonical outcome
→ owner domain event
→ Sweepstakes / Prize entry decision
```

Webhook verification, provider-event dedupe, and Stripe status translation remain Payment / Payout / Tax responsibilities.

### 17.2 Tax provider

```text
Payment / Payout / Tax
→ tax provider-neutral port
→ Stripe Tax / future provider adapter as approved
→ external provider
→ normalized TaxProfile/reporting result
→ SH-019 / SH-118 public contract
→ CL-10 owner transition
```

CL-10 never imports provider tax statuses into `PrizeWinningStatus` or `RewardRedemptionStatus` directly.

### 17.3 Notification provider

Notification owns SES/SMS/push adapters and delivery state. CL-10 only requests notification through SH-041 and reacts to delivery outcomes only if the owner workflow genuinely needs that information.

### 17.4 Future reward/prize fulfillment providers

No specific gift-card, shipping, cash-reward, or prize-fulfillment provider and no provider-dedupe schema are confirmed in the current evidence.

Before introducing one, architecture must define:

```text
Owning CL-10 Module
→ provider-neutral fulfillment port
→ provider adapter
→ provider
→ verified normalized result
→ owner transitionRewardRedemption or transitionPrizeWinning
```

It must also define webhook verification owner, processed-event truth, provider-reference persistence, reconciliation, unknown-status handling, and operational failure reporting.

Provider payload types must not become domain types.

### 17.5 Random selection

Secure random selection is an owner-internal capability using SH-116 over a cryptographically secure randomness primitive. Do not add an external “raffle provider” without an explicit architecture decision.

---

## 18. Search / Projection Boundaries

CL-10 does not own global Search / Public Visibility.

### Internal CL-10 projections

- `LeaderboardEntry` is a Gamification-owned ranking projection.
- point balance is a Gamification-owned derived read model/query.
- `PrizeTaxYearSummary` is a Sweepstakes-owned aggregate.

These use shared projection/aggregation mechanisms without becoming Search documents.

### Profile/search boost rewards

`RewardType.profile_boost` does not authorize Gamification to write Typesense, `SearchUpsertEvent`, or profile ranking fields directly.

If SH-119 is approved:

```text
RewardRedemption fulfilled/approved deterministic benefit
→ approved temporary feature grant/effect owner
→ affected feature determines valid effect
→ Search owner receives reindex/projection request if needed
→ Search indexes only source-owned, privacy/moderation/readiness-safe state
```

Search must never reconstruct point balances, reward eligibility, or prize eligibility from index state.

---

## 19. Media / File Boundaries

No CL-10-owned `MediaAsset` requirement is confirmed in the current schema.

If future official-rules documents, prize evidence, shipment documents, or reward attachments are stored as files:

- Media / File Access owns binary validation, scanning, storage mechanics, and generic signed access;
- Sweepstakes or Gamification owns the business meaning of the attachment and contextual entitlement;
- private/sensitive files use short-lived signed access;
- sensitive reads use SH-030 where required;
- a file URL must not become tax, consent, winning, or fulfillment truth.

`PrizeDrawing.officialRulesUrl` is currently only a URL field. It does not by itself prove an immutable version of the rules that governed a particular entry/drawing run.

---

## 20. Privacy / Retention

Privacy / Data Erasure owns `PrivacyRequest` and `DataErasureJob` orchestration. Both CL-10 Modules must implement Privacy’s owner protocol.

### Gamification / Rewards responsibilities

Through SH-096, enumerate at minimum:

- program-associated subject records where user-specific;
- PointLedgerEntry;
- ChallengeParticipant;
- LeaderboardEntry;
- RewardRedemption;
- provider references owned by Gamification if later introduced.

Through SH-095/097/098, execute approved erase/anonymize/export/retain instructions while preserving legally required ledger, fraud, tax, and fulfillment evidence.

### Sweepstakes / Prize responsibilities

Enumerate at minimum:

- PrizeEntry;
- PrizeWinning;
- PrizeTaxYearSummary;
- subject-linked drawing-run proof once defined;
- provider references owned by Sweepstakes if later introduced.

Prize/tax/legal retention may prevent full deletion. The owner returns retention facts; Privacy records any `DataRetentionExemption`.

### Retention rules

- `deletedAt` semantics are not currently present on these CL-10 models and must not be invented as a privacy substitute.
- Normal business correction does not erase historical ledger/entry/winning proof.
- Personal fields may be anonymized only under an approved mapping that preserves required legal and relational evidence.
- CL-10 does not directly delete Tax-provider or Notification-provider data it does not own; Privacy coordinates the appropriate owner/provider executor.

---

## 21. Audit and Observability

### Audit evidence

Use SH-029 for material actions such as:

- program/rule/reward activation or retirement;
- manual point adjustment/reversal;
- reward fulfillment/reversal approval;
- drawing activation/closure/cancellation;
- manual/admin entry adjustment or eligibility override;
- drawing-run initiation/override/redraw decision;
- winning approval/forfeiture/cancellation/fulfillment;
- hold request reasoning;
- material reconciliation repair.

Use SH-030 for sensitive data access where required by root policy, particularly tax/winner/financially sensitive admin views.

Audit metadata must be minimal and sanitized. Do not store provider secrets, tax documents, payment data, full official-rules content, or unnecessary personal data in audit metadata.

### Domain truth

Audit does not replace:

- PointLedgerEntry;
- RewardRedemption;
- PrizeEntry;
- PrizeWinning;
- PrizeTaxYearSummary;
- the future immutable drawing-run proof.

### Observability

Operational logging must include safe:

- request/correlation IDs;
- Module/operation name;
- aggregate IDs;
- event/job IDs;
- attempt/retry/dead-letter status;
- provider operation and normalized failure class where relevant;
- latency/lag metrics for projections and scheduled drawings.

It must exclude secret tokens, tax identifiers/documents, provider payload dumps, and unnecessary user data.

`IntegrationFailure`, `QueueJob`, or similar observability records named by the architecture may be canonical infrastructure abstractions even if the current Prisma snapshot does not yet contain those exact model names. CL-10 must consume the platform operation, not add local replacements.

---

## 22. Security Boundaries

1. **Server-side validation:** all commands validate payload shape and business invariants server-side; client checks are convenience only.
2. **Server-side authorization:** SH-002 gates protected reads/mutations. URL parameters never establish authority.
3. **Step-up:** consume SH-014 for actions classified sensitive; do not implement local MFA.
4. **Randomness:** winner selection uses SH-116/CSPRNG and unbiased sampling; never `Math.random()`.
5. **Replay protection:** inbound owner events, admin commands, entry issuance, redemptions, drawings, value reports, and fulfillment commands require stable idempotency semantics.
6. **Rate limits:** public/free-entry and redemption endpoints require root-approved rate limiting. Rate limiting does not replace domain entry limits.
7. **Entry limits:** enforce transactionally and race-safely.
8. **Point overspend protection:** point sufficiency and redemption write occur atomically.
9. **Inventory protection:** limited reward inventory cannot be check-then-write without lock/reservation semantics.
10. **Provider secrets:** remain server-side in provider owner adapters.
11. **Webhook authentication:** only provider-owning Modules verify and process provider webhooks.
12. **Sensitive payload minimization:** tax/profile/provider data passed into CL-10 is narrowed to the decision/evidence fields CL-10 needs.
13. **Rules integrity:** production drawing rules must have immutable/versioned evidence before activation; current schema gap is unresolved.
14. **Drawing population integrity:** population must be frozen/proven for a run before random selection.
15. **No hidden odds mutation:** paid plan, points, reward, admin convenience, or provider state cannot alter odds outside explicit Sweepstakes policy and legal review.

---

## 23. Testing Architecture

### Module unit tests

**Gamification / Rewards:**
- rule trigger matching;
- points sign/type/source invariants;
- reversal/adjustment logic;
- balance derivation;
- challenge transitions;
- reward activation gates;
- redemption transition matrix;
- no-pay-to-win safeguards.

**Sweepstakes / Prize:**
- drawing and entry-method transitions;
- AMOE/free path validation;
- equivalent-odds checks;
- per-user/free/paid/max entry-limit policy;
- eligibility behavior;
- winning transition matrix;
- tax/hold fulfillment gates;
- secure selection determinism tests around fixture populations without weakening production randomness.

### Public-interface contract tests

Every interface in Section 10 must have consumer/provider contract tests proving:

- DTO fields remain bounded and versioned;
- owner truth is not leaked as writable cross-domain models;
- denial reason codes are stable enough for consumers;
- retries and duplicate deliveries remain safe.

### Cross-Module integration tests

Required scenarios:

1. one Order-completed source event awards points exactly once despite duplicate delivery;
2. a user cannot redeem the same point balance concurrently twice;
3. an approved free entry and qualifying purchase entry produce separate PrizeEntry truth with equivalent configured odds;
4. duplicate purchase source event does not duplicate PrizeEntry;
5. two drawing workers cannot create competing winners for one run;
6. winner notification failure does not roll back or fabricate PrizeWinning truth;
7. active ComplianceHold prevents prohibited fulfillment while preserving owner state;
8. tax-readiness denial prevents reward/prize fulfillment;
9. recognized CL-10 value reaches Payment/Tax once through SH-118;
10. Privacy orchestration can enumerate and process CL-10 target records without creating a second privacy workflow.

### Provider adapter tests

For any future provider owned by a CL-10 Module:

- signature verification;
- duplicate provider event;
- known/unknown status mapping;
- retryable vs terminal failure;
- out-of-order event handling;
- reconciliation after missed webhook;
- provider payload never written directly as domain state.

Stripe/tax provider tests remain with their provider-owning Modules; CL-10 tests the public contract stubs/consumers.

### Concurrency/idempotency tests

- duplicate source event per rule;
- concurrent point spend;
- concurrent limited reward redemption;
- concurrent free-entry request;
- concurrent purchase-entry event;
- drawing lock collision;
- duplicate drawing command;
- duplicate taxable-value report;
- duplicate fulfillment callback.

### Compliance tests

- no active purchase-only drawing where AMOE is required;
- no paid entry with privileged weight under equivalent-odds policy;
- no entitlement/points/reward boost to chance odds;
- no fulfillment while `pending_tax`/blocked;
- terms/rules proof required when configured;
- admin override audited;
- unsupported reward types cannot be activated silently.

### Privacy/security tests

- self/admin authorization boundaries;
- sensitive access logging where required;
- privacy subject enumeration completeness;
- retention decision preserves mandatory records;
- telemetry redaction fixtures;
- no direct provider secret/payload leakage.

### Critical E2E workflows

At minimum:

- eligible activity → points → reward redemption;
- free entry → entry confirmation → closed drawing → secure winner → tax gate → approved fulfillment;
- purchase outcome → authoritative source event → exactly one purchase-triggered entry while free path remains available;
- admin hold applied during redemption/winning → action blocked → hold release → owner reevaluation.

---

## 24. Invariants

### Rules coding agents must never violate

1. CL-10 never owns a lifecycle; `gamification_rewards` and `sweepstakes_prize` do.
2. Never merge `PointLedgerEntry` and `PrizeEntry` into a generic “ticket/points” record.
3. Never merge `RewardRedemption` and `PrizeWinning` into generic fulfillment truth.
4. Never treat `GamificationProgram` as `PrizeDrawing` or vice versa.
5. Never use a mutable point-balance column as point truth.
6. Never modify/delete historical PointLedgerEntry rows to correct a balance in ordinary business workflow.
7. Never award points twice for the same source event/rule semantics because of retries.
8. Never spend points and create a redemption in separate non-atomic business transactions.
9. Never oversubscribe limited reward inventory through check-then-write logic.
10. Never make purchase the only sweepstakes entry path where AMOE/no-purchase is required.
11. Never let paid entries receive better effective odds through `weight`, `entriesAwarded`, plan status, points, or hidden configuration without explicit approved legal policy.
12. Never let `TrackEntitlementGrant`, premium/subscription status, or a profile boost increase sweepstakes odds.
13. Never create a points-to-PrizeEntry bridge under the current schema without explicit architecture/legal approval.
14. Never process Stripe webhooks inside Sweepstakes / Prize under the current ownership model.
15. Never recreate `ProcessedStripeEvent` in CL-10.
16. Never treat payment-provider state as Order or PrizeEntry truth.
17. Never use `Math.random()` or predictable randomness for winner selection.
18. Never run a drawing against a mutable, unfrozen eligible population.
19. Never run production winner selection without approved immutable drawing-run proof.
20. Never treat winner notification as PrizeWinning creation, confirmation, or fulfillment.
21. Never fulfill a tax-blocked or hold-blocked reward/prize.
22. Never interpret TaxProfile provider fields directly in CL-10; consume Payment/Tax readiness.
23. Never create local `taxApproved`, `canFulfillPrize`, `rewardBlocked`, or `isPremium` truth flags.
24. Never create a local ComplianceHold replacement.
25. Never create local ConsentLog/terms acceptance tables.
26. Never let consent proof replace the Module’s business permission/eligibility decision.
27. Never use AuditEvent as point, entry, redemption, winning, or provider-event truth.
28. Never use operational logs, queue telemetry, or IntegrationFailure as business lifecycle truth.
29. Never access another Module’s Prisma repository as the default integration contract.
30. Never expose Prisma models directly as stable cross-Module DTOs.
31. Never let a provider webhook directly update RewardRedemption or PrizeWinning without the provider-owning adapter and owner command.
32. Never create a generic platform fulfillment-provider status mapping that erases Module-specific policy.
33. Never write Typesense/Search projection state directly from Gamification to implement a profile boost.
34. Never create a separate PrivacyRequest/DataErasureJob workflow inside CL-10.
35. Never erase legally retained prize/tax/fraud evidence without a Privacy-coordinated retention decision.
36. Never log raw tax documents, payment data, secrets, or full provider payloads to audit/telemetry.
37. Never silently invent a reward fulfillment mechanism for an enum value merely because the enum exists.
38. Never silently invent a dedicated ChallengeParticipant lifecycle enum or migrate the schema without resolving U-CL10-04.
39. Never silently create official-rules snapshot or drawing-run models without resolving the named unresolved decisions.
40. Never implement a proposed SH-119 ownership choice as though it were confirmed.

---

## 25. Prohibited Duplicate Implementations

Coding agents must not create the following CL-10-local substitutes when the canonical operation already exists.

| Duplicate implementation to avoid | Use instead |
|---|---|
| `gamificationAuth.ts`, `rewardUserResolver.ts`, `prizeAuth.ts`, `sweepstakesSession.ts` | SH-001 |
| `rewardPermissions.ts`, `pointsAuthorization.ts`, `prizeAdminGuard.ts`, `isSweepstakesAdmin.ts` | SH-002 |
| `rewardConsentService.ts`, `gamificationTermsRepo.ts`, `prizeConsentService.ts`, `rulesCheckbox.ts` | SH-008/009 |
| `rewardBlocked.ts`, `prizeBlocked.ts`, `winnerHoldService.ts`, local hold flags/table | SH-011/012 + `ComplianceHold` owner |
| `prizeTaxCheck.ts`, `w9Gate.ts`, `rewardTaxProfileService.ts` | SH-019 + Payment/Tax public interfaces |
| `prizeAudit.ts`, `rewardAudit.ts`, `sweepstakesLogger.ts` as audit storage | SH-029; SH-033 is operational logging only |
| `winnerDataAudit.ts`, `prizeAccessLog.ts` | SH-030 |
| `genericLedger.ts` that merges points/order/payment/usage ledgers | SH-031 mechanism while preserving `PointLedgerEntry` truth |
| `pointsBalance` mutable truth, `rewardBalanceService.ts` as independent balance authority | SH-115 projection over PointLedgerEntry |
| `rewardEventDedupe.ts`, `processedGamificationEvent.ts`, `dedupeEntry.ts` | SH-045 / platform idempotency mechanisms |
| `gamificationPublisher.ts`, `rewardEventBus.ts`, `prizePublisher.ts` with custom outbox | SH-046 |
| `gamificationQueue.ts`, `prizeQueue.ts`, `drawingWorkerQueue.ts` as separate queue infrastructure | SH-047/048 |
| local in-memory drawing mutex | SH-051/database concurrency primitive |
| local reward inventory check-then-decrement helper | SH-056 |
| `winnerEmailService.ts`, `prizePush.ts`, `rewardNotificationService.ts` | SH-041 |
| `raffleRandom.ts` using ordinary PRNG | SH-116 |
| CL-10 `annual1099Service.ts`, `prizeFilingService.ts` | SH-117/118 + Payment / Payout / Tax |
| `profileBoost=true`, `premiumReward=true`, local temporary entitlement table | SH-119 once approved |
| `cl10PrivacyService.ts` owning privacy requests | SH-095–098 + Privacy owner |
| `processed_stripe_events` copy under Sweepstakes | Payment / Payout / Tax `ProcessedStripeEvent` |
| generic `fraudRiskAssessment` service with no approved owner | Keep unresolved; use owner-local deterministic validation + SH-012 escalation until architecture assigns shared risk ownership |

---

## 26. Deferred / Unresolved Decisions

### U-CL10-01 — Immutable official-rules evidence

- **Question:** What immutable Workin Ants record proves the exact official rules/disclosure text/version that governed an activated PrizeDrawing and its entries?
- **Why unresolved:** `PrizeDrawing` currently stores `officialRulesUrl`, while the architecture requires versioned proof and the Module does not own legal drafting. `PrizeEntry.rulesConsentId` exists but is not a declared Prisma relation to `ConsentLog`.
- **Missing evidence:** approved official-rules snapshot/version model or contract; relationship to Consent version catalog; whether URL + content hash is sufficient; retention requirements.
- **Blocks:** production `activatePrizeDrawing` and legally reliable entry/drawing proof. Draft configuration can proceed.
- **Implementation rule:** do not invent a snapshot table. If approved, reuse SH-077/072 for canonical text/hash mechanics.

### U-CL10-02 — Immutable drawing-run proof schema

- **Question:** Which Module-owned record(s) preserve a frozen eligible population, selection algorithm/version, randomness evidence, winner count, replacement/redraw policy, run identity, and selected winning references?
- **Why unresolved:** SH-116 requires immutable run proof, but current Prisma schema contains `PrizeDrawing`, `PrizeEntry`, and `PrizeWinning` only; no drawing-run record is present.
- **Missing evidence:** approved schema/contract and retention rules.
- **Blocks:** production winner selection. A drawing worker must not run using only transient memory/logs/AuditEvent.

### U-CL10-03 — Reward inventory semantics and reservation proof

- **Question:** Does `Reward.inventory` represent original stock cap, current remaining stock, or another quantity; and what record proves reservation/release for concurrent redemption?
- **Why unresolved:** schema has one `inventory` field and `RewardRedemption`, but no dedicated reservation record or documented semantics.
- **Missing evidence:** Module ruling on stock semantics and cancellation/reversal release behavior.
- **Blocks:** activation of limited-inventory rewards at production scale. Unlimited rewards and catalog configuration are not blocked.
- **Implementation rule:** use SH-056 once semantics are approved; do not invent a second inventory ledger casually.

### U-CL10-04 — ChallengeParticipant status vocabulary

- **Question:** Is reusing `ChallengeStatus` for `ChallengeParticipant.status` intentional, or should participant state have its own enum?
- **Why unresolved:** Prisma reuses values such as `draft`, `paused`, and `archived`, which may not all make semantic sense for a participant.
- **Missing evidence:** Module lifecycle ruling.
- **Blocks:** only participant states beyond the conservative subset. The current service may constrain allowed participant values without schema migration.

### U-CL10-05 — Reward type fulfillment/effect contracts

- **Question:** What authoritative effect/fulfillment contract applies to each `RewardType` (`badge`, `gift_card`, `cash_bonus`, `profile_boost`, `physical_prize`, `platform_credit`, `other`)?
- **Why unresolved:** enum and redemption lifecycle exist, but provider/effect records are not defined for several types.
- **Missing evidence:** provider choices, financial owner interfaces, badge ownership, platform-credit ledger owner, manual fulfillment proof, provider reference/dedupe/reconciliation schema.
- **Blocks:** activation/final fulfillment of unsupported types. Catalog rows may remain `draft`/`paused`.

### U-CL10-06 — SH-119 temporary feature grant ownership

- **Question:** Does Track Subscription & Entitlement or the affected feature own deterministic time-bound grants earned from rewards?
- **Why unresolved:** SH-119 is a Proposed Ruling in the canonical registry.
- **Missing evidence:** approved owner and grant contract.
- **Blocks:** `profile_boost` or similar reward effects that need a temporary platform grant.

### U-CL10-07 — Direct entitlement dependency for ordinary gamification

- **Question:** Which, if any, GamificationProgram/Reward actions are actually gated by commercial Track entitlements?
- **Why unresolved:** the Cluster declares Track Subscription & Entitlement as an inbound rail, but the Module extract does not confirm a direct baseline dependency.
- **Missing evidence:** named entitlement keys and feature policy.
- **Blocks:** only entitlement-gated reward/program behavior. It does not block ordinary deterministic points/rewards.
- **Invariant:** no entitlement can influence chance odds.

### U-CL10-08 — Shared fraud/risk capability ownership

- **Question:** Is there a platform-wide fraud/risk Module/capability for points abuse and sweepstakes entry abuse, and who owns its result truth?
- **Why unresolved:** CL-10 technology notes mention fraud detection, but the Module Registry does not assign a shared fraud capability owner and the canonical registry contains no confirmed generic fraud decision operation.
- **Missing evidence:** owner, decision contract, evidence model, case escalation boundaries.
- **Blocks:** centralized cross-domain fraud scoring. It does not block deterministic owner validation, rate limits, idempotency, or requesting a ComplianceHold for manual review.

### U-CL10-09 — `PrizeEntry.rulesConsentId` relational integrity

- **Question:** Should `rulesConsentId` be an enforced Prisma relation/foreign key to `ConsentLog`, or intentionally remain a loose proof reference?
- **Why unresolved:** field exists as UUID but no Prisma relation is declared.
- **Missing evidence:** schema ownership/rationale and deletion/retention behavior for ConsentLog.
- **Blocks:** schema migration only. Runtime may validate the proof through SH-008 and store the returned proof ID without assuming FK semantics.

### U-CL10-10 — Delivery-on-time source owner

- **Question:** Which Module/event is authoritative for `GamificationRuleTrigger.delivery_on_time`?
- **Why unresolved:** trigger enum exists, but the supplied evidence does not name the source contract.
- **Missing evidence:** owner event/public query and timing semantics.
- **Blocks:** activation of rules using `delivery_on_time`; other trigger types are unaffected.

### U-CL10-11 — Redraw / replacement-winner policy

- **Question:** Under what conditions may a completed/partially completed drawing select a replacement winner, and how is the original run preserved?
- **Why unresolved:** status enum and schema do not express redraw/run generations.
- **Missing evidence:** official rule/legal policy and drawing-run proof model.
- **Blocks:** redraw/replacement functionality. Do not reopen a completed drawing ad hoc.

### U-CL10-12 — Exact legal thresholds and jurisdictions

- **Question:** Which prize/reward reporting thresholds, eligibility jurisdictions, age/geography rules, and claim windows apply?
- **Why unresolved:** these are legal/policy facts; the architecture explicitly is not legal advice and the schema provides configuration fields but not a jurisdiction rule engine for CL-10.
- **Missing evidence:** approved legal/compliance policy and owner rule versions.
- **Blocks:** production launch in affected jurisdictions, not domain scaffolding/tests.


### U-CL10-13 — Observability registry / Prisma record mismatch

- **Question:** Are `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` pending platform models, renamed records, or intentionally external operational abstractions?
- **Why unresolved:** the Observability / Ops module evidence names these as owned operational records, while the supplied `schema.prisma` does not contain models with those exact names.
- **Missing evidence:** current root Observability implementation/migration decision and final persistence names.
- **Blocks:** CL-10 must not assume those exact Prisma repositories when building admin Ops views or failure persistence. It does **not** block consuming SH-037/038 through their canonical interfaces.
- **Implementation rule:** do not create CL-10-local `IntegrationFailure` or `QueueJob` tables to fill the gap. Resolve the platform owner implementation separately.

---

## 27. Architecture Decision Summary

### Confirmed binding rulings

1. CL-10 contains exactly two lifecycle-owning Deep Modules: Gamification / Rewards and Sweepstakes / Prize.
2. Gamification owns programs, rules, point ledger, challenges, leaderboards, rewards, and RewardRedemption.
3. Sweepstakes owns drawings, entry methods, PrizeEntry, PrizeWinning, and PrizeTaxYearSummary.
4. `PointLedgerEntry != PrizeEntry`; `RewardRedemption != PrizeWinning`.
5. Point balance and leaderboard are derived/projection behavior; PointLedgerEntry remains point truth.
6. Sweepstakes must preserve AMOE/no-purchase and no-paid-odds-boost controls.
7. Consent proof remains Consent-owned; action policy remains CL-10 Module-owned.
8. ComplianceHold remains Admin Review-owned and is the reusable stop sign.
9. TaxProfile/reporting/provider truth remains Payment / Payout / Tax-owned.
10. Notification and Audit are downstream/support evidence, not reward/prize truth.
11. Track entitlements remain commercial-policy truth and may not influence prize odds.
12. Privacy orchestrates; each CL-10 Module executes against its own records.
13. Search is not CL-10 truth and profile/search boosts cannot be direct index mutations from Gamification.
14. Canonical SH-### operations are reused rather than reimplemented locally.
15. Provider payloads remain behind provider-owner adapters.

### Proposed rulings requiring approval before dependent implementation

- **PR-CL10-01:** purchase-triggered entries consume authoritative Order/payment-owner events; Sweepstakes owns no Stripe webhook.
- **PR-CL10-02:** code is organized by Deep Module; CL-10 gets no generic source-truth service.
- **PR-CL10-03:** `GamificationRule.ruleJson` is a schema-validated, versioned declarative rules payload; arbitrary executable rules are forbidden.
- **PR-CL10-04 through PR-CL10-08:** conservative lifecycle transition matrices and immutable entry behavior described in Section 9.
- **PR-CL10-09:** high-risk CL-10 admin actions are candidates for central step-up enforcement.

### Binding implementation posture for unresolved items

Unresolved decisions are not invitations to improvise. Features that depend on U-CL10-01 through U-CL10-12 must either:

1. resolve the architecture decision and update this file first; or
2. remain disabled/draft/stubbed in a way that cannot produce unsafe production behavior.

---

## 28. Coding-Agent Usage

Before changing CL-10, an implementation agent must read, in order:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md`;
5. this Cluster `architecture.md`;
6. this Cluster `build-plan.md`;
7. the target Module architecture;
8. the target Module implementation plan;
9. relevant dependency Module public-interface sections, especially Identity & Access, Role / Authority, Consent & Disclosure, Transaction / Order, Payment / Payout / Tax, Track Subscription & Entitlement, Admin Review / Compliance Hold, Notification, Audit / Event Ledger, Observability / Ops, Privacy / Data Erasure, and Search when applicable;
10. the current progress tracker.

Before implementation, the agent must also inspect the current Prisma schema and migrations rather than assuming this document represents the latest executable schema.

If repository code differs from this architecture:

- do not create a second pattern;
- state the conflict;
- preserve source-of-truth ownership;
- prefer the canonical Shared Operation/public interface;
- update architecture before making a binding new decision;
- never let build progress silently settle a Proposed Ruling or Unresolved Decision.
