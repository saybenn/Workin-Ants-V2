# Track Subscription & Entitlement Architecture

> **Module ID:** `track_subscription_entitlement`  
> **Module name:** Track Subscription & Entitlement  
> **Module type:** `commercial_policy_capability`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/modules/track_subscription_entitlement/module-architecture.md`  
> **Document status:** implementation-grade Module architecture; subordinate to root Workin Ants architecture and the CL-01 architecture  
> **Audience:** coding agents, developers, reviewers, maintainers, security reviewers, privacy reviewers, compliance reviewers, and architecture reviewers  
> **Update rule:** update this file whenever a binding ownership, lifecycle, entitlement, usage-metering, provider, privacy, retention, or public-contract decision for this Module changes. Build progress must not silently redefine this architecture.

This document narrows the CL-01 architecture to the `track_subscription_entitlement` Deep Module. It defines what this Module owns and exposes; it does not make CL-01 a source-of-truth owner and it does not copy the full platform architecture.

Evidence posture used throughout:

- **Confirmed** — supported by the current Deep Module Registry, Cluster Registry, Prisma schema, Canonical Shared Operations Registry, CL-01 architecture/build plan, or repeated Module-extract evidence.
- **Proposed Ruling** — a necessary implementation-grade decision strongly supported by current architecture but not yet fully ratified by all evidence.
- **Unresolved** — the evidence identifies a material question but does not support a safe final decision. Production behavior that depends on it remains disabled, fixture-only, or fail-closed until resolved.

---

## 1. Module Header

| Field | Value |
|---|---|
| Module ID | `track_subscription_entitlement` |
| Module name | Track Subscription & Entitlement |
| Module type | `commercial_policy_capability` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-01 — Identity, Authority, Consent & Entitlements` |
| Document status | Binding Module context for implementation, subject to unresolved gates listed in Section 35 |
| Intended audience | Coding agents, developers, reviewers, maintainers, security/privacy/compliance reviewers |
| Relationship to root architecture | Subordinate. Root ownership, security, provider, privacy, data, and code standards control when they conflict with this file. |
| Relationship to Cluster architecture | Narrows CL-01’s commercial-policy rail into Module-local truth, interfaces, workflows, and implementation constraints. It must not change CL-01 sequencing or absorb neighboring Module lifecycles. |
| Update rule | Change only when an architectural decision changes; feature progress alone does not justify changing ownership or lifecycle rules. |

### Evidence conflicts already resolved at this boundary

1. **Track schema ownership vs historical Transaction / Order claims.** Older registry/extract material associated some Track records with Transaction / Order. Current CL-01 architecture and Canonical Shared Operations make Track Subscription & Entitlement the current commercial-policy owner. `Order` may snapshot Track decisions, but must not own or mutate `TrackSubscription`, `TrackEntitlementGrant`, `TrackUsageEvent`, or `TrackUsageCounter`.
2. **Provider-event dedupe vs Payment’s `ProcessedStripeEvent`.** Older glossary material treats `ProcessedStripeEvent` as Payment / Payout / Tax truth. Current shared-operations architecture requires shared dedupe mechanics with provider-owning, domain-specific processed-event truth. The exact subscription-billing processed-event record is still unresolved (`U-CL01-22`). Do not reuse Payment’s record automatically and do not treat `TrackSubscriptionEvent` as sufficient dedupe proof.
3. **“Monthly usage reset worker” vs immutable usage proof.** Older cluster technology lists mention a monthly reset worker. Current CL-01 build-plan rules are stronger: `TrackUsageEvent` is immutable and counters are period projections. A new period/counter may begin, but historical usage proof must never be destructively reset.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own the commercial policy layer for Workin Ants’ current account tracks — `customer`, `candidate`, and `professional` — including plan definitions, subscription enrollment state, entitlement grants, typed entitlement values, quota/usage accounting, commercial perks, fee waivers, boosts, priority policy, and commission policy.

This Module exists to prevent commercial-state pollution across `User`, `CustomerProfile`, `CandidateProfile`, `ProfessionalProfile`, Order, Booking, Search, and other feature records.

### Goal

Permit one `User` to hold independent commercial plan states across multiple actor tracks while every consuming Module can obtain one source-owned answer to questions such as:

```text
Does this Customer track have a buyer-fee waiver?
How many candidate applications remain in this period?
What candidate search boost is effective now?
What professional commission rate applies?
Does this professional track include live streaming?
Does this customer track receive priority scheduling?
What plan/grant evidence supports the answer?
```

without creating local `isPremium`, local quota counters, local fee-waiver truth, or local commission truth.

### What enters

- authenticated actor context and system/admin actor context;
- `CustomerProfile`, `CandidateProfile`, or `ProfessionalProfile` identity/binding facts from their owning Modules;
- plan catalog configuration;
- price/provider references;
- entitlement definitions and typed values;
- consent proof references for subscription/plan-change actions;
- verified provider billing events after shared webhook security;
- admin/manual/comped grant commands;
- ComplianceHold decisions where commercial actions are gated;
- usage-consumption requests from authoritative business workflows;
- Privacy-owned data instructions;
- expiration/reconciliation work;
- downstream requests for current commercial policy.

### What leaves

- source-owned plan and price records;
- authoritative Workin Ants subscription state;
- active/suspended/revoked/expired/consumed entitlement grants;
- typed current-entitlement decisions with evidence references and stable reasons;
- atomic metering receipts;
- immutable usage events;
- rebuildable usage counters;
- subscription lifecycle history;
- provider reconciliation results;
- public policy DTOs used by Order, Booking, Candidate Application, Search, Professional Eligibility, Video, Digital Goods, and other consumers;
- minimized domain events and downstream requests to Search, Notification, Audit, Privacy, and Observability owners.

### Capability transformation

```text
plan configuration
+ actor-track binding
+ provider/manual subscription or grant evidence
+ effective-date/precedence policy
+ optional usage history
        ↓
Workin Ants commercial policy truth
        ↓
typed entitlement / quota / waiver / boost / commission / priority decision
        ↓
consumer applies that decision inside its own business lifecycle
```

### Why this is a separate Module

Commercial policy changes independently from authentication, actor profiles, business transactions, booking, search, and delivery. A plan change must not require schema changes across every consumer, and a historical Order must not change merely because the current subscription changes. This Module therefore owns **current commercial policy** while consumers own **historical business snapshots and business action truth**.

---

## 3. Owned Truth

### 3.1 Schemas / models owned

| Record | Plain-English meaning | Ownership |
|---|---|---|
| `TrackPlan` | A named commercial package for one account track. | Confirmed |
| `TrackPlanPrice` | A provider-linked price option or commercial price reference for a TrackPlan. | Confirmed |
| `TrackEntitlementDefinition` | Canonical vocabulary for a feature, quota, waiver, boost, rate, priority, or perk and its value type. | Confirmed |
| `TrackPlanEntitlement` | The typed entitlement value a plan provides. | Confirmed |
| `TrackSubscription` | Workin Ants’ current enrollment/subscription state for one User/track/profile context. Provider references are evidence/rail references, not the domain authority by themselves. | Confirmed |
| `TrackEntitlementGrant` | A currently effective or historically relevant grant of one entitlement to a User/track/profile context, optionally sourced from a subscription, plan, manual/comped action, or temporary source. | Confirmed |
| `TrackUsageEvent` | Immutable proof that a metered entitlement was consumed for a defined business event. | Confirmed policy |
| `TrackUsageCounter` | Rebuildable period projection used for efficient allowance checks. | Confirmed |
| `TrackSubscriptionEvent` | Append-only Track-owned history of subscription/plan lifecycle facts. It is not a provider-event dedupe ledger. | Confirmed record; clarified boundary |

### 3.2 Enums / statuses owned

- `AccountTrack`
- `TrackPlanStatus`
- `TrackBillingModel`
- `TrackBillingProvider`
- `TrackSubscriptionStatus`
- `TrackEntitlementValueType`
- `TrackEntitlementGrantStatus`
- `TrackUsageEventType`
- `TrackUsagePeriod`

### 3.3 Lifecycles owned

- TrackPlan lifecycle.
- TrackSubscription lifecycle.
- TrackEntitlementGrant lifecycle.
- Track usage proof append lifecycle.
- Track usage-counter projection lifecycle.
- TrackSubscriptionEvent append lifecycle.
- Track-specific provider billing state translation, if `PR-CL01-04` is ratified.

### 3.4 Source-of-truth records

- **Plan truth:** `TrackPlan` + active/relevant `TrackPlanPrice` + `TrackPlanEntitlement`.
- **Entitlement vocabulary truth:** `TrackEntitlementDefinition`.
- **Enrollment truth:** `TrackSubscription`.
- **Current grant truth:** `TrackEntitlementGrant`, interpreted through effective-date/status/precedence policy.
- **Usage proof:** `TrackUsageEvent`.
- **Usage projection:** `TrackUsageCounter`.
- **Subscription history:** `TrackSubscriptionEvent`.

### 3.5 Domain events / ledgers owned

`TrackSubscriptionEvent` is the Module-owned lifecycle ledger. Additional integration events may be published through the platform outbox, but the outbox is not Module truth.

Conceptual event families this Module may emit after source commits:

- `TrackPlanPublished` / `TrackPlanRetired`;
- `TrackSubscriptionChanged`;
- `TrackEntitlementGrantChanged`;
- `TrackEntitlementValueChanged`;
- `TrackMeteredEntitlementConsumed`;
- `TrackUsageLimitReached`.

**Proposed Ruling:** event names and exact versioned envelopes may be finalized during implementation, but payload meaning must remain limited to facts that occurred. They must not be disguised commands to another Module.

### 3.6 Projections owned

- `TrackUsageCounter` is the principal Module-owned projection.
- A current Track access summary DTO may be computed/read-model output; unless separately persisted, it is not source truth.
- Candidate search documents, Order pricing snapshots, Booking priority records, and delivery grants are **not** Track projections.

### 3.7 Snapshots / proof owned

Track owns evidence references returned with current policy decisions: source plan, subscription, grant, entitlement definition, effective value, evaluation time, expiry/recheck time, and reason code. It does **not** own the downstream historical snapshot that an Order or Booking chooses to persist.

### 3.8 Policies and invariants owned

- track applicability;
- plan lifecycle and catalog validity;
- entitlement key/value compatibility;
- grant status/effective-time validity;
- grant precedence once `U-CL01-20` is resolved;
- subscription-to-grant materialization policy;
- quota period and accounting policy once the relevant unresolved item is resolved;
- typed current entitlement resolution;
- usage-counter derivation;
- provider-to-Track status mapping when provider integration is active;
- downgrade/cancel effects on current grants while preserving historical usage;
- commercial quote policy returned to Order, without owning Order pricing history.

---

## 4. Explicit Non-Ownership

This Module must not own or duplicate the following.

| Adjacent owner | Truth that remains there | Track boundary |
|---|---|---|
| Identity & Access | User authentication, session state, passkeys, MFA, step-up challenge/session lifecycle | Consume actor/step-up interfaces; never create `subscriptionAuth.ts` or a local session resolver. |
| Role / Authority | Permission interpretation and admin/support action authorization | Supply Track resource facts/action names; do not create a Track-specific general role engine. |
| Consent & Disclosure | Consent type/version catalog and `ConsentLog` acceptance proof | Query proof; never create subscription-specific consent tables as a replacement. |
| Customer / Buyer Profile | `CustomerProfile` lifecycle and buyer actor identity | Validate binding through public interface; do not update CustomerProfile status. |
| Candidate Application & Resume Privacy / Candidate owner | Candidate actor/application lifecycle and application-view truth | Track accounts quota/boost policy; it does not create JobApplication or candidate-view records. |
| Professional Eligibility | Professional readiness composition | Track returns commercial entitlement facts; it does not decide verification/healthcare/financial readiness. |
| Marketplace Supply | Offering/PricingTier lifecycle | Track may gate premium commercial capabilities; it does not publish/retire Offerings. |
| Gig / Demand | Gig/response/assignment lifecycle | Track may return plan-specific response capability; it does not mutate Gig state. |
| Transaction / Order | Order, Agreement, transaction status, historical pricing/fee/commission snapshots | Return current commercial quote/evidence; Order persists its own snapshot via the approved snapshot pattern. |
| Payment / Payout / Tax | Payment success, processor payment ledger, payouts, tax, financial readiness | Track Billing is subscription policy only under PR-CL01-04. Do not create payout/tax/payment-ledger truth here. |
| Booking & Calendar | Booking/hold/slot lifecycle and priority scheduling application | Return priority policy; Booking decides scheduling and persists its own historical/action truth. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense documents, indexing/deindexing and search queries | Request refresh through SH-091; never call Typesense directly. |
| Video Infrastructure | Video rooms/provider assets/playback/live access-grant lifecycle | Return live-stream entitlement only. |
| Digital Goods Access | download/playback grant lifecycle | Return Track perk context only. |
| Notification | notification persistence, templates, routing and delivery | Request delivery via SH-041. |
| Audit / Event Ledger | generic `AuditEvent` and `AccessAuditLog` | Track owns lifecycle history; generic audit remains separate support evidence. |
| Observability / Ops | logs, metrics, `IntegrationFailure`, `QueueJob`, incidents | Track owns business state even when an operational failure is recorded. |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, retention-exemption orchestration/export bundle | Implement Track target inventory/execution only. |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle | Query hold or request/release through owner; no generic `isBlocked` truth. |
| Media / File Access | upload, scan, file storage, signed URL, MediaAsset lifecycle | This Module currently owns no file attachment semantics. |
| Organization Hiring | organization ATS feature-access model until `U-CL01-30` is resolved | Do not silently add `organization` to `AccountTrack`. |

### Specific anti-theft rules

- Do not store Order IDs as Track’s transaction lifecycle.
- Do not turn `TrackUsageEvent.targetId` into ownership of the target object.
- Do not treat a provider customer/subscription/price ID as Workin Ants source truth.
- Do not treat `TrackSubscriptionEvent.providerEventId` as a substitute for the unresolved processed-provider-event record.
- Do not create local current-policy fields in consumers to “cache” Track truth unless architecture explicitly defines a cache/projection with invalidation and non-authoritative semantics.

---

## 5. Module Architecture Principles

1. **One commercial-policy owner.** Track Subscription & Entitlement is the only current commercial-plan/entitlement/usage source for customer/candidate/professional tracks.
2. **Current policy vs historical business truth.** Track answers what applies now or at an explicitly supplied evaluation instant. Consumers own historical snapshots used by their lifecycles.
3. **Actor-track binding is explicit.** A track decision is scoped to a `User` plus the correct actor profile where the schema requires one.
4. **No local premium booleans.** `isPremium`, `isPro`, `hasPriority`, `feeWaived`, `searchBoosted`, `commissionRate`, and equivalent feature-local current-policy truth are prohibited.
5. **Typed entitlement values.** Every entitlement definition declares one value type; mappings and grants must carry exactly the compatible value representation once `U-CL01-24` is resolved.
6. **Usage proof is append-only.** Ordinary correction does not update/delete `TrackUsageEvent`; reconciliation rebuilds projections or uses an explicitly approved reversal/adjustment model.
7. **Counters are projections.** `TrackUsageCounter` may be dropped/rebuilt without losing usage truth.
8. **Provider events are untrusted until verified.** Signature verification precedes parsing/side effects; dedupe and status translation precede domain transition.
9. **Provider state is not domain state.** Stripe Billing is a rail. Redirect success pages and provider dashboards do not directly establish Track access.
10. **Shared mechanisms stay shared.** Idempotency, locks, queueing, retries, audit, notification, webhook verification, provider-event dedupe mechanics, privacy orchestration, and Search execution are consumed through canonical operations.
11. **Unresolved policy fails closed.** Missing entitlement catalog, precedence, transition, retention, or snapshot rules are architecture blockers, not implementation improvisation opportunities.
12. **Downgrade preserves history.** Removing current access must not rewrite prior usage, Order snapshots, or historical subscription events.
13. **Source-owner reads are narrow.** Use owner DTOs/public queries for profile existence/binding and downstream context; no generic cross-domain Prisma repository.
14. **Effects follow source commits.** Search refresh, Notification, and other asynchronous side effects use the transactional outbox/queue pattern and may retry without rolling back already-committed Track truth.
15. **Business failures and operational failures differ.** A denied entitlement is a domain decision; a Stripe timeout is an operational failure; neither substitutes for the other.

---

## 6. Proposed Folder / Code Structure

**Proposed Ruling:** organize one feature boundary for this Module rather than a generic CL-01 service. Adapt the root repository’s established feature-directory convention without changing ownership.

```text
src/
└── features/
    └── track-subscription-entitlement/
        ├── actions/
        │   ├── plan-actions.ts
        │   ├── subscription-actions.ts
        │   └── grant-actions.ts
        ├── queries/
        │   ├── plan-queries.ts
        │   ├── subscription-queries.ts
        │   └── entitlement-queries.ts
        ├── commands/
        │   ├── plan-commands.ts
        │   ├── subscription-commands.ts
        │   ├── grant-commands.ts
        │   └── metering-commands.ts
        ├── schemas/
        │   ├── plan-inputs.ts
        │   ├── subscription-inputs.ts
        │   ├── grant-inputs.ts
        │   └── entitlement-inputs.ts
        ├── domain/
        │   ├── plan-policy.ts
        │   ├── entitlement-value.ts
        │   ├── entitlement-resolution.ts
        │   ├── grant-policy.ts
        │   ├── subscription-transition.ts
        │   └── usage-period-policy.ts
        ├── services/
        │   ├── plan-service.ts
        │   ├── entitlement-service.ts
        │   ├── subscription-service.ts
        │   ├── grant-service.ts
        │   └── metering-service.ts
        ├── repositories/
        │   ├── track-plan-repository.ts
        │   ├── track-subscription-repository.ts
        │   ├── track-grant-repository.ts
        │   └── track-usage-repository.ts
        ├── contracts/
        │   ├── public-commands.ts
        │   ├── public-queries.ts
        │   ├── decision-results.ts
        │   ├── billing-provider.ts
        │   └── events.ts
        ├── providers/
        │   └── stripe-billing-adapter.ts
        ├── workers/
        │   ├── expire-track-access.ts
        │   ├── rebuild-usage-counters.ts
        │   └── reconcile-billing-state.ts
        ├── privacy/
        │   ├── enumerate-subject-data.ts
        │   └── execute-privacy-instruction.ts
        └── tests/
            ├── unit/
            ├── contract/
            ├── integration/
            ├── provider/
            ├── privacy/
            └── concurrency/
```

### Structure rules

- `components/` is omitted by default. This Module may later expose a small account-plan/admin UI, but UI is not a prerequisite for core capability.
- `providers/stripe-billing-adapter.ts` is permitted only after `PR-CL01-04` is ratified and the provider lifecycle blockers are resolved.
- Shared idempotency, queue, retry, audit, notification, logging, lock, webhook-verification, and privacy-orchestration code must remain outside this Module.
- Repositories may access only Track-owned tables by default. Foreign-owner reads use public interfaces/contracts.
- `domain/subscription-transition.ts` must not invent the production transition graph while `U-CL01-21` remains unresolved.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / UI / actions | Runtime input parsing; transport mapping; invoking application service; safe result mapping | Business policy, direct Prisma workflows, provider status interpretation |
| Application services | Command/query orchestration; transaction boundaries; calling shared operations; Track-owned side-effect scheduling | Generic auth/authorization/queue/retry infrastructure; foreign lifecycle mutation |
| Domain policy | Track plan rules; typed entitlement interpretation; grant precedence; usage-period semantics; subscription transition policy after approved decisions | Role policy, consent proof lifecycle, Order/Booking/Search rules |
| Repositories / data access | Track-owned tables and owner-specific consistency checks | Generic cross-domain repositories; direct mutation of profiles, Order, Booking, Search, Payment |
| Workers | Track expiration, counter rebuild, subscription reconciliation orchestration | Generic scheduler/queue engine; Privacy orchestration |
| Provider adapter | Stripe Billing/Checkout/Portal request/response translation and Track-specific status mapping when approved | Payment/Payout/Tax ledger, provider secret management framework, generic webhook security |
| Contracts | Stable public Track commands/queries/events and provider-neutral DTOs | Provider SDK types in domain contracts; universal permission/decision engine |
| Privacy executor | Enumerate and execute Track-owned targets | PrivacyRequest/DataErasureJob lifecycle or retention-exemption truth |
| Tests | Domain/contract/provider/concurrency/privacy verification | Tests that reach into neighboring tables as a substitute for public contracts |

---

## 8. Data Model

The Prisma schema is executable evidence. This section documents meaning, ownership, and known implementation constraints rather than repeating the schema verbatim.

### 8.1 `TrackPlan`

**Purpose:** canonical commercial package for one `AccountTrack`.

**Key relationships:** prices, plan-entitlement mappings, subscriptions, subscription events.

**Authoritative fields:** `track`, `key`, `name`, `status`, `billingModel`, description/display metadata. `monthlyPriceCents` exists but overlaps with `TrackPlanPrice.amountCents`.

**Lifecycle/status:** `TrackPlanStatus`.

**Current uniqueness:** `@@unique([track, key])`.

**Concurrency-sensitive behavior:** activation/retirement and mutation of a live plan can change current policy for many actors. Use optimistic concurrency or aggregate locking for material transitions.

**Retention/privacy:** plan catalog is generally non-personal; historical plan interpretation may require retention after retirement.

**Unresolved:** `U-CL01-23` must settle plan revision/effective-date history. The current mutable row alone does not guarantee historical interpretation.

### 8.2 `TrackPlanPrice`

**Purpose:** provider-linked pricing option for a plan.

**Authoritative fields:** provider, provider price/product IDs, amount, currency, interval, active flag.

**Relationships:** belongs to TrackPlan.

**Current indexes:** plan/active and provider/providerPriceId. No uniqueness currently guarantees one provider price reference.

**Key concern:** `interval` currently uses `TrackUsagePeriod`, which includes values such as `once`, `daily`, `rolling_30_day`; billing cadence and entitlement-usage period are conceptually different vocabularies. Do not expand this enum coupling without an architecture decision.

**Key concern:** `TrackPlan.monthlyPriceCents` and `TrackPlanPrice.amountCents` may encode the same price. Production code must not treat both as independent truth. This is unresolved and must be normalized before live catalog mutation.

### 8.3 `TrackEntitlementDefinition`

**Purpose:** stable key and value-type definition for one commercial capability.

**Authoritative fields:** `key`, `label`, `valueType`, optional track scope, active flag.

**Uniqueness:** `key` globally unique.

**Rule:** the exact production key catalog is blocked by `U-CL01-19`. Test fixtures may use explicitly labeled non-production keys.

### 8.4 `TrackPlanEntitlement`

**Purpose:** typed value a plan grants for an entitlement.

**Authoritative fields:** plan, entitlement, valueType, one value field, optional usage period.

**Uniqueness:** one mapping per `[planId, entitlementId]`.

**Critical constraint gap:** the schema permits multiple value fields or a `valueType` that disagrees with the entitlement definition. `U-CL01-24` must define application/DB constraints before production writes.

### 8.5 `TrackSubscription`

**Purpose:** Workin Ants source record for one actor track’s enrollment/subscription state.

**Authoritative fields:** User, plan, track, profile binding, status, current/trial/cancel/end dates; provider fields are mirrored references.

**Relationships:** User, plan, optional customer/candidate/professional profile, grants, usage, counters, events.

**Current lifecycle default risk:** `status @default(active)` can incorrectly make a newly created paid subscription active before provider confirmation.

**Current provider default risk:** `provider @default(stripe)` can mislabel free/manual/comped records.

**Constraint gaps:**

- no database check guarantees exactly the correct profile ID for the selected track;
- no unique constraint guarantees one relevant active subscription per actor track;
- no constraint guarantees `userId` matches the selected profile’s User;
- provider subscription ID is indexed but not unique;
- free-plan representation is unresolved (`U-CL01-18`).

These are implementation blockers for production state mutation, not reasons to encode ad hoc checks in consumers.

### 8.6 `TrackEntitlementGrant`

**Purpose:** current/historical entitlement grant.

**Authoritative fields:** actor/track/profile binding, entitlement, status, typed value, effective dates, optional source subscription/plan/event references.

**Lifecycle:** `TrackEntitlementGrantStatus`.

**Constraint gaps:** same actor/profile binding and typed-value issues as subscription/mapping. `sourcePlanId` and `sourceEventId` are scalar references in the current schema without explicit Prisma relations; code must not infer referential integrity that the schema does not provide.

**Precedence:** unresolved `U-CL01-20`.

### 8.7 `TrackUsageEvent`

**Purpose:** append-only proof of a metered entitlement use.

**Authoritative fields:** actor/track/profile, event type, source subscription/grant/entitlement, target reference, quantity, occurredAt, safe metadata.

**Immutability:** policy-level invariant; implementation must enforce insert-only behavior in services/repositories.

**Critical idempotency gap:** no explicit semantic idempotency key or uniqueness exists. SH-006 requires semantic idempotency. Schema changes may be needed once the exact command-key design is approved.

**Target reference:** `targetType`/`targetId` is evidence only; it does not transfer ownership of the target.

### 8.8 `TrackUsageCounter`

**Purpose:** efficient current-period projection over usage events.

**Authoritative fields:** entitlement/actor/period bounds, used and limit quantities.

**Current uniqueness:** `[entitlementId, track, userId, periodStart, periodEnd]`.

**Projection rule:** must be rebuildable from TrackUsageEvent according to approved period/reversal policy.

**Concurrency:** counter update is race-sensitive; SH-006/SH-057 require an atomic transaction.

**Potential issue:** uniqueness does not include profile ID, subscription ID, or grant ID. Whether one User can maintain distinct same-entitlement counters across multiple same-track contexts needs validation against actor architecture.

### 8.9 `TrackSubscriptionEvent`

**Purpose:** append-only Track domain history for plan/subscription transitions.

**Authoritative fields:** subscription/plan/user references, event name, from/to status, optional provider/provider event ID, safe metadata, timestamp.

**Boundary:** `providerEventId` is indexed, not unique. Therefore this table is not sufficient proof of provider-event dedupe under SH-060. `U-CL01-22` must resolve the owner-specific processed-event record/schema.

**Retention:** likely subject to billing-history retention; exact duration/anonymization is blocked by `U-CL01-29`.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Account track

```text
customer
candidate
professional
```

These are current account tracks. `organization` must not be added until `U-CL01-30` is resolved.

### 9.2 TrackPlan lifecycle

Statuses:

```text
draft
active
retired
archived
```

**Confirmed:** the lifecycle and statuses are Track-owned.

**Proposed Ruling — conservative transition graph:**

```text
draft ──activate──> active ──retire──> retired ──archive──> archived
  └────────────────────────────archive abandoned draft────────────────> archived
```

Rules:

- only Track administration commands transition state;
- active plans are enrollment-eligible only if all required catalog constraints pass;
- retirement stops new enrollment but must not corrupt historical subscriptions;
- archived is terminal unless architecture explicitly approves restoration;
- direct `draft → active` must fail if unresolved production catalog/value/version rules are not satisfied;
- live plan mutation must respect `U-CL01-23`.

### 9.3 TrackSubscription lifecycle

Statuses:

```text
active
trialing
past_due
cancelled
expired
paused
incomplete
incomplete_expired
```

**Transition graph:** **Unresolved — `U-CL01-21`.**

No implementation may infer Stripe’s native transition graph or use the enum declaration order as policy. Required decisions include:

- initial state for paid enrollment;
- `trialing → active`;
- `active ↔ past_due`;
- pause/resume;
- cancel-at-period-end vs immediate cancel;
- `cancelled` vs `expired`;
- `incomplete → active` and `incomplete → incomplete_expired`;
- downgrade effective time;
- grace-period semantics;
- out-of-order provider event handling;
- whether any status is terminal and under what reconciliation conditions.

Transition owner: Track Subscription & Entitlement.

Trigger classes: authorized user/admin commands, verified provider events, expiration worker, reconciliation.

Event proof: every material status transition appends TrackSubscriptionEvent transactionally with the source change; generic AuditEvent is additional evidence, not a replacement.

### 9.4 TrackEntitlementGrant lifecycle

Statuses:

```text
active
expired
revoked
suspended
consumed
```

**Proposed Ruling — conservative transition policy:**

```text
active ──expire──> expired
active ──revoke──> revoked
active ──suspend──> suspended ──restore──> active
active ──consume one-shot──> consumed
suspended ──expire──> expired
suspended ──revoke──> revoked
```

- `expired`, `revoked`, and `consumed` are terminal for that grant record.
- Restoration creates no historical rewrite; if policy requires a materially new grant, create a new grant instead.
- `consumed` is valid only for one-shot semantics.
- Subscription downgrade/cancel acts through Track-owned grant policy.
- Grant precedence across overlapping active grants remains blocked by `U-CL01-20`.

### 9.5 Usage lifecycle

`TrackUsageEvent` has no mutable lifecycle. It is append-only proof.

```text
authorized business event
→ atomic allowance decision
→ immutable TrackUsageEvent
→ TrackUsageCounter projection update
```

No destructive “monthly reset” is allowed. Period rollover selects or creates the new projection period; old events/counters remain historical evidence subject to retention policy.

### 9.6 Usage counter lifecycle

```text
derive period bounds
→ create/read counter
→ atomically increment on accepted use
→ reconcile/rebuild from events
→ retain/expire according to retention policy
```

Counter mismatch is an operational reconciliation condition, not permission to rewrite events.

### 9.7 Subscription-event ledger

Append only:

```text
source transition transaction
→ TrackSubscriptionEvent append
→ outbox event if external consumers require it
```

No update-in-place and no use as generic provider dedupe.

---

## 10. Commands

The names below define public/module-owned mutation responsibilities. They are interface contracts, not implementation code.

### 10.1 `seedTrackCatalog`

- **Purpose:** idempotently create approved plan/entitlement reference data.
- **Actor/context:** trusted deployment/admin system actor.
- **Inputs:** versioned seed manifest.
- **Preconditions:** production catalog decisions approved; keys/types valid.
- **Writes:** plans, prices, entitlement definitions/mappings.
- **Shared operations:** SH-044 idempotency; SH-029 audit for material admin runs where applicable.
- **Effects:** optional plan publication events after source commit.
- **Idempotency:** seed version + stable natural keys.
- **Failure modes:** unresolved production key/value/history decision; partial manifest rejected transactionally or per explicit batch policy.

### 10.2 `createTrackPlan` / `updateDraftTrackPlan`

- **Purpose:** create or edit a draft plan.
- **Actor:** authenticated authorized administrator.
- **Inputs:** track/key/name/billing model and approved catalog metadata.
- **Writes:** TrackPlan.
- **Shared operations:** SH-001, SH-002, SH-044, SH-029.
- **Failure:** duplicate `[track,key]`, invalid billing configuration, stale version.

### 10.3 `configureTrackPlanPrice`

- **Purpose:** manage a provider-neutral price reference.
- **Actor:** authorized admin.
- **Preconditions:** price-source ambiguity resolved before production.
- **Writes:** TrackPlanPrice.
- **Failure:** unsupported provider/currency/interval; duplicate provider reference according to future approved constraint.

### 10.4 `defineTrackEntitlement` / `configurePlanEntitlement`

- **Purpose:** define canonical entitlement vocabulary and map typed values to plans.
- **Actor:** authorized admin.
- **Preconditions:** `U-CL01-19` and `U-CL01-24` for production.
- **Writes:** TrackEntitlementDefinition, TrackPlanEntitlement.
- **Failure:** value-type mismatch, inactive/unknown entitlement, wrong track applicability.

### 10.5 `activateTrackPlan`, `retireTrackPlan`, `archiveTrackPlan`

- **Purpose:** execute TrackPlan lifecycle.
- **Actor:** authorized admin; step-up if platform policy later requires.
- **Preconditions:** valid transition; complete/approved catalog; safe historical plan policy.
- **Writes:** TrackPlan status; Track lifecycle history/event as approved.
- **Shared operations:** SH-002, SH-029, SH-044, SH-051/052/053 where needed, SH-046.
- **Idempotency:** plan ID + requested transition + expected version.
- **Failure:** stale/invalid transition, unresolved plan-history rule.

### 10.6 `assignDefaultFreeTrack`

- **Purpose:** provision default commercial access when a track actor is created.
- **Status:** **Blocked for production by `U-CL01-18`.**
- **Actor/context:** trusted system event/command.
- **Writes:** either TrackSubscription, grants, or both — unresolved.
- **Rule:** profile provisioning must not depend on a Track record existing; Track may react after actor creation.

### 10.7 `createManualEntitlementGrant`, `suspendEntitlementGrant`, `restoreEntitlementGrant`, `revokeEntitlementGrant`

- **Purpose:** explicit Track-owned manual/comped/admin grant lifecycle.
- **Actor:** authorized admin/system; high-risk actions may require step-up.
- **Preconditions:** entitlement exists; actor-track binding valid; hold policy permits.
- **Writes:** TrackEntitlementGrant.
- **Shared operations:** SH-001/002/011/014/029/044/051/053/046.
- **Failure:** invalid binding, precedence unresolved for conflicting grant, stale state.
- **Rule:** never edit usage history to simulate grant revocation.

### 10.8 `consumeMeteredEntitlement` — SH-006

- **Purpose:** atomically confirm allowance and record accepted usage.
- **Actor/context:** trusted business workflow or authorized system actor; end user cannot arbitrarily self-increment.
- **Inputs:** actor-track, entitlement key, quantity, semantic idempotency key, target evidence, occurredAt.
- **Preconditions:** effective entitlement resolved; period policy defined; quantity positive; business owner has decided the event counts.
- **Writes:** TrackUsageEvent and TrackUsageCounter in one transaction.
- **Shared operations:** SH-005, SH-044, SH-051 or SH-057, SH-031 if mechanism used for event persistence, SH-046 where external event needed.
- **Idempotency:** same semantic business use returns the same receipt without a second event.
- **Failure:** limit exceeded, duplicate with mismatched fingerprint, unresolved period policy, concurrency conflict.

### 10.9 `startTrackSubscriptionCheckout`

- **Purpose:** initiate paid enrollment through the Track-owned billing adapter if PR-CL01-04 is ratified.
- **Production gate:** U-CL01-18/20/21/22/23/25/29 and PR-CL01-04.
- **Actor:** authenticated owner of the target track/profile.
- **Inputs:** plan/price ID, actor track/profile, consent proof references, return context.
- **Preconditions:** plan active, price active, authority, consent, hold/step-up policy.
- **Writes:** any local pending/incomplete source state only as defined by the approved transition design; never marks active because checkout session exists.
- **Effects:** provider session creation.
- **Failure:** consent missing, provider unavailable, duplicate command, plan changed.

### 10.10 `changeTrackSubscriptionPlan`, `cancelTrackSubscription`, `openTrackBillingPortal`

Same provider/lifecycle gates as checkout. These commands:

- do not copy Stripe status into domain fields without translation;
- do not modify Payment/Payout/Tax ledgers;
- append Track lifecycle evidence only when Workin Ants source state changes;
- are idempotent by subscription + requested intent + request key.

### 10.11 `applyTrackBillingProviderEvent` — internal

- **Purpose:** turn an authenticated/deduped provider event into a Track transition.
- **Actor:** trusted provider endpoint/system context, not a browser actor.
- **Inputs:** normalized verified event envelope.
- **Preconditions:** SH-059 verified raw callback; SH-060 unique claim; SH-061 recognized mapping.
- **Writes:** TrackSubscription, grants, TrackSubscriptionEvent, processed-provider-event truth once U-CL01-22 is resolved.
- **Effects:** outbox events, Notification request, Search refresh when boost changes.
- **Failure:** forged/duplicate/out-of-order/unknown event, unresolved transition.

### 10.12 `reconcileTrackBillingState`

- **Purpose:** compare source Track state with provider state and repair missed/inconsistent effects according to owner policy.
- **Shared operations:** SH-062, SH-047/048, SH-037/038, SH-029 when admin-triggered.
- **Rule:** reconciliation cannot invent a transition not permitted by the approved transition table.

### 10.13 `expireTrackAccess`

- **Purpose:** expire subscriptions/grants whose approved deadlines are past.
- **Context:** scheduled worker using SH-055 and owner commands.
- **Writes:** Track source lifecycle + events.
- **Rule:** expiration is idempotent and does not delete historical usage.

### 10.14 `rebuildTrackUsageCounters`

- **Purpose:** recreate TrackUsageCounter from immutable events.
- **Shared operations:** SH-115 projection mechanism, SH-047/048, SH-038.
- **Writes:** only projection rows.
- **Rule:** mismatch produces operational telemetry; no mutation of source events.

### 10.15 `executePrivacyInstruction` — Track implementation of SH-095

- **Purpose:** execute a Privacy-owned instruction against Track-owned records.
- **Actor/context:** Privacy-authorized system workflow.
- **Inputs:** target/disposition/correlation and approved retention result.
- **Preconditions:** SH-097 retention evaluation where needed.
- **Writes:** approved erase/anonymize/revoke/retain effects only.
- **Rule:** never create PrivacyRequest/DataErasureJob locally.

---

## 11. Queries / Decisions

### 11.1 `listTrackPlans`

- **Consumers:** account/plan selection UI, Consent presentation, admin/catalog tools.
- **Input:** track, visibility/status context, optional locale/display context.
- **Result:** safe plan/price/entitlement presentation DTO.
- **Type:** source-truth read with presentation shaping.
- **Consumer must not infer:** active subscription, entitlement, or consent from plan availability.

### 11.2 `getCurrentTrackSubscription`

- **Consumers:** account settings, billing UI, admin support, Track internal resolution.
- **Input:** User + AccountTrack + actor profile context.
- **Result:** current source subscription DTO and provider-neutral references/status.
- **Consumer must not infer:** provider payment success beyond the Track status meaning.

### 11.3 `resolveEntitlement` — SH-005

- **Consumers:** all commercial-policy consumers.
- **Input:** actor track/profile, typed entitlement key, evaluation instant/context.
- **Result:** typed effective value, decision/reason, evidence refs, evaluatedAt, expires/recheckAt.
- **Type:** authoritative current commercial-policy decision.
- **Stable reason families:** `GRANTED`, `NO_GRANT`, `INACTIVE_PLAN`, `GRANT_SUSPENDED`, `GRANT_EXPIRED`, `TRACK_MISMATCH`, `HOLD_BLOCKED`, `CONFIGURATION_UNRESOLVED`, `UNSUPPORTED_VALUE`.
- **Consumer must not infer:** broader business readiness, Order eligibility, Booking availability, or historical policy.

### 11.4 `resolveTrackAccessSummary`

- **Consumers:** account/admin presentation.
- **Input:** actor track.
- **Result:** collection of resolved entitlements and usage summaries.
- **Type:** derived read model.
- **Rule:** must call the same resolution policy as SH-005; it is not a competing resolver.

### 11.5 `checkUsageAllowance`

- **Consumers:** preflight UI/business workflows.
- **Input:** actor/entitlement/quantity/evaluation instant.
- **Result:** allowed/denied, limit, used, remaining, period bounds.
- **Type:** contextual decision/read.
- **Rule:** non-consuming preflight is advisory; authoritative enforcement is SH-006 in the business transaction path.

### 11.6 `quoteOrderTrackPolicy`

- **Consumers:** Transaction / Order.
- **Input:** buyer CustomerProfile context, professional context, order-policy context, evaluation instant.
- **Result:** fee-waiver and professional commission decisions plus source evidence/version.
- **Type:** contextual commercial decision.
- **Consumer must not infer:** Order pricing history from future Track queries. Order must persist its own approved snapshot.
- **Blocked details:** `U-CL01-27` rounding/basis-point/snapshot payload rules.

### 11.7 `evaluatePriorityScheduling`

- **Consumer:** Booking & Calendar.
- **Input:** Customer track/profile and scheduling context.
- **Result:** priority rank/class and evidence; optional metering requirement if approved.
- **Blocked details:** `U-CL01-28`.
- **Consumer must not infer:** slot availability or booking ownership.

### 11.8 `evaluateCandidateSearchBoost`

- **Consumers:** Candidate Application/Profile and Search.
- **Input:** CandidateProfile/track, evaluation instant.
- **Result:** boost value and evidence.
- **Effect:** changes may cause SH-091 request to Search.
- **Consumer must not infer:** public-readiness, privacy, moderation, or Search document state.

### 11.9 `evaluateProfessionalSellingEntitlement`

- **Consumer:** Professional Eligibility / Marketplace Supply.
- **Input:** ProfessionalProfile/track and named commercial capability.
- **Result:** commercial entitlement facts.
- **Consumer must not infer:** verification, healthcare, financial readiness or Offering publishability.

### 11.10 `authorizeLiveStreaming` / other narrow capability wrappers

Allowed only as typed wrappers over SH-005 when they add a stable consumer contract. They must not reimplement resolution or create feature-local source truth.

### 11.11 `enumerateSubjectData` — SH-096 implementation

Returns stable Track-owned privacy target inventory and provider references to Privacy. It is not a general admin query.

---

## 12. Public Module Interface

### Public commands

- SH-006 `consumeMeteredEntitlement`
- `startTrackSubscriptionCheckout` — gated
- `changeTrackSubscriptionPlan` — gated
- `cancelTrackSubscription` — gated
- `openTrackBillingPortal` — gated
- authorized plan/price/entitlement administration commands
- authorized manual/comped grant lifecycle commands
- `executePrivacyInstruction` as the Track executor under SH-095

### Public queries

- SH-005 `resolveEntitlement`
- `listTrackPlans`
- `getCurrentTrackSubscription`
- `resolveTrackAccessSummary`
- `checkUsageAllowance`
- `quoteOrderTrackPolicy`
- `evaluatePriorityScheduling`
- `evaluateCandidateSearchBoost`
- `evaluateProfessionalSellingEntitlement`
- narrow capability wrappers such as `authorizeLiveStreaming` only when they add contract value
- `enumerateSubjectData` under SH-096

### Emitted domain/integration events

Versioned factual events after source commits, through SH-046:

- plan published/retired;
- subscription changed;
- entitlement grant/effective value changed;
- metered entitlement consumed/limit reached where downstream action is justified.

### Privacy executor

- SH-095 Track target executor
- SH-096 subject-data enumeration
- SH-097 retention-fact contribution
- SH-098 anonymization primitive where approved

### Provider-facing interfaces

Under PR-CL01-04:

- provider-neutral `TrackBillingProviderPort`;
- Stripe Billing/Checkout/Portal adapter;
- provider callback application entry point after SH-059/060/061;
- reconciliation through SH-062.

### Preferred access rule

Other Modules must use these contracts rather than direct Prisma access to Track tables. Direct Track table reads from consumers require an explicit architecture exception.

---

## 13. Inbound Dependencies

| Owning Module / platform | Interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | SH-001 `resolveAuthenticatedActor` | Establish user/admin actor for protected commands | user ID, actor type, assurance context | Yes | session/current-user helper |
| Identity & Access | SH-014 `requireStepUpForSensitiveAction` | High-risk admin/billing changes if policy requires | actor, action, target, assurance | Yes | MFA/passkey challenge |
| Role / Authority | SH-002 `authorizeResourceAction` | Plan/subscription/grant admin and self-service authorization | action + Track target facts | Yes | Track role engine |
| Customer / Buyer Profile | SH-004 `resolveCustomerActor` | Bind customer track | User→CustomerProfile | Yes for customer-track operation | CustomerProfile provisioning logic |
| Candidate/Profile owner | SH-003 owner facts | Validate candidate binding | profile ID, User ID, status | Yes | candidate repository |
| Professional Profile / Eligibility | SH-003 owner facts; SH-016 where readiness is separately needed | Validate professional binding; keep commercial vs readiness separate | profile ID/User ID, optional readiness decision | Sometimes | professional lifecycle/readiness logic |
| Consent & Disclosure | SH-008 `queryConsentProof`, SH-009 active version | Subscription terms, recurring billing, plan change | proof ID/version/acceptedAt/validity | Yes for actions requiring consent | ConsentLog/service |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | Prevent blocked commercial actions | target/action/hold refs | Yes | `isBlocked` |
| Audit | SH-029 `appendAuditEvent` | Material admin/subscription actions | actor/action/target/outcome/safe metadata | No to source truth after commit unless audit is mandated transactional gate | Track audit table |
| Notification | SH-041 `requestNotification` | Subscription/grant lifecycle communications | recipient refs, template key, safe variables | No after source commit | email/SMS provider |
| Search | SH-091 `requestSearchProjectionRefresh` | Candidate boost change | entity ID/type/reason/source version | No after source commit | Typesense client |
| Privacy | SH-095–098 protocol | Privacy target execution/retention/anonymization | target/disposition/correlation/retention | Yes for destructive action | privacy workflow |
| Observability / Ops | SH-032–039 | Safe logs, metrics, integration failures, health | safe refs, provider/operation/retryability | No | local logger/failure table |
| Platform reliability | SH-044–055, SH-057 | Idempotency, outbox, jobs, retries, locks, lifecycle plumbing, deadline execution, atomic counters | semantic keys and Track policy | Yes where required | local infra |
| Shared integration security | SH-059–063 | Webhook verification, provider dedupe, mapping, reconciliation/snapshot mechanics | raw request or normalized provider event | Yes | local generic webhook/dedupe/retry system |
| Consuming domain snapshot owner | SH-109 pattern is executed by consumer, not Track | Historical business decisions | Track returns source evidence only | N/A | Track-owned Order/Booking snapshot |

---

## 14. Outbound Consumers and Effects

### Consumers of Track truth

- Customer / Buyer Profile presentation
- Candidate Application & Resume Privacy
- Professional Eligibility
- Marketplace Supply
- Gig / Demand
- Transaction / Order
- Booking & Calendar
- Search / Public Visibility
- Video Infrastructure
- Digital Goods Access
- Payment / Payout / Tax presentation where needed
- Consent & Disclosure plan-context presentation
- Admin Review / Compliance Hold
- Privacy / Data Erasure
- Notification
- Observability / Ops

### Downstream effects

- Candidate boost changes request SH-091 Search refresh.
- Subscription/grant changes may request SH-041 Notification.
- Material actions request SH-029 Audit.
- Provider/workers use Ops interfaces for failures/health.
- Privacy invokes Track executor; Track reports result back rather than changing Privacy parent status.
- Order receives a quote/evidence package and uses SH-109 to persist its own historical snapshot.
- Booking consumes priority policy and owns any booking/slot/priority application record.
- Candidate Application calls SH-006 only when its authoritative business event counts.
- Video/Digital consumers receive entitlement decisions but issue their own access grants.

### Mutation rule

Track must not mutate another Module’s source truth directly. Cross-Module effects occur only through approved commands/events/interfaces.

---

## 15. Canonical Shared Operations Used

Only operations materially relevant to this Module are listed.

### SH-001 — `resolveAuthenticatedActor`

- **Meaning:** trusted server actor resolution.
- **Owner:** Identity & Access.
- **Classification:** canonical shared capability / platform capability.
- **Why used:** all protected plan/subscription/grant/admin commands.
- **Invocation:** delivery boundary before application service.
- **Local policy:** which Track action is requested and which actor-track target is involved.
- **Expected result:** typed Workin Ants actor context.
- **Do not build:** `getCurrentUser.ts`, `subscriptionAuth.ts`, `requireTrackUser.ts`.

### SH-002 — `authorizeResourceAction`

- **Owner:** Role / Authority.
- **Classification:** canonical shared capability.
- **Why:** authorize plan administration, self-service subscription changes, manual grants.
- **Invocation:** after actor resolution, before mutation.
- **Local policy:** Track action vocabulary and target facts.
- **Result:** allow/deny/reason/authority evidence.
- **Do not build:** `trackPermissions.ts`, `entitlementAdminAuth.ts`.

### SH-003 — `queryOwnerFacts`

- **Owner:** each source Module.
- **Classification:** shared contract / separate implementations; proposed ruling.
- **Why:** validate Customer/Candidate/Professional profile binding.
- **Local policy:** which owner facts Track needs.
- **Result:** minimal owner DTO.
- **Do not build:** `profileRepository.ts` that queries all profile tables directly.

### SH-004 — `resolveCustomerActor`

- **Owner:** Customer / Buyer Profile.
- **Classification:** another Module’s public interface.
- **Why:** bind customer-track operations.
- **Do not build:** CustomerProfile provisioning or buyer identity logic.

### SH-005 — `resolveEntitlement`

- **Owner:** this Module.
- **Classification:** platform commercial-policy capability.
- **Why:** canonical current policy resolver.
- **Invocation:** consumer read/gate; internally before metering.
- **Local policy:** typed values, effective dates, grant precedence, evidence.
- **Result:** current typed entitlement decision.
- **Do not build elsewhere:** `premiumGate.ts`, `featureAccess.ts`, `commissionCalculator.ts`, `feeWaiverService.ts`.

### SH-006 — `consumeMeteredEntitlement`

- **Owner:** this Module.
- **Classification:** cross-cutting capability.
- **Why:** authoritative quota enforcement and immutable usage proof.
- **Invocation:** consumer’s authoritative business mutation path.
- **Local policy:** period, limit, quantity, idempotency semantics, reversal policy.
- **Result:** accepted usage receipt or deterministic denial.
- **Do not build elsewhere:** `quotaManager.ts`, `applicationLimit.ts`, `recordUsageEvent.ts`.

### SH-008 / SH-009 — consent proof/version

- **Owner:** Consent & Disclosure.
- **Classification:** canonical consent capabilities.
- **Why:** bind subscription terms, recurring billing, plan changes.
- **Local policy:** which proof is required at which Track action.
- **Do not build:** `subscriptionConsent.ts`, `billingTermsStore.ts`.

### SH-011 — `evaluateComplianceHold`

- **Owner:** Admin Review / Compliance Hold.
- **Classification:** canonical shared capability.
- **Why:** block/review relevant Track actions without local blocked flags.
- **Do not build:** `subscriptionHold.ts`, `isTrackBlocked.ts`.

### SH-014 — `requireStepUpForSensitiveAction`

- **Owner:** Identity & Access.
- **Classification:** platform security capability.
- **Why:** high-risk billing/admin/manual grant actions if approved by action matrix.
- **Do not build:** Track MFA/passkey challenge.

### SH-015 — `returnDecisionResult`

- **Owner:** shared contract; policy owner varies.
- **Classification:** shared contract / separate policy; proposed.
- **Why:** normalize allow/deny/review/remediation shapes for public decisions.
- **Local policy:** Track reason codes/evidence.
- **Do not build:** a universal decision engine owning Track rules.

### SH-029 — `appendAuditEvent`

- **Owner:** Audit / Event Ledger.
- **Classification:** platform audit capability.
- **Why:** material plan/subscription/grant/admin operations.
- **Local policy:** safe Track action metadata.
- **Do not build:** `trackAudit.ts`, `subscriptionAuditEvent` generic audit clone.

### SH-031 — `appendDomainLifecycleEvent`

- **Owner:** shared persistence mechanism; Track owns its event truth.
- **Classification:** shared mechanism / separate truth.
- **Why:** insert-only TrackSubscriptionEvent and any approved grant history pattern.
- **Local policy:** Track event names/from-to state/evidence.
- **Do not build:** generic Track event framework separate from platform mechanism.

### SH-032–SH-039 — request context, logging, telemetry, failures, health

- **Owner:** Observability / Ops / platform.
- **Classification:** shared infrastructure.
- **Why:** provider, worker, reconciliation and API diagnostics.
- **Local policy:** safe dimensions such as track, operation, provider, reason family.
- **Do not build:** local logger, IntegrationFailure clone, QueueJob clone.

### SH-041 — `requestNotification`

- **Owner:** Notification.
- **Classification:** platform notification capability.
- **Why:** subscription/grant/usage lifecycle alerts.
- **Local policy:** trigger meaning and safe variables.
- **Do not build:** Stripe email handler, `sendSubscriptionEmail.ts`.

### SH-044 — `executeIdempotentCommand`

- **Owner:** platform application infrastructure.
- **Classification:** platform primitive.
- **Why:** plan/admin commands, provider-derived commands, usage, privacy.
- **Local policy:** semantic command identity and replay result.
- **Do not build:** Track idempotency table/framework unless the shared primitive’s storage contract explicitly locates a record here.

### SH-045 / SH-046 — event inbox/outbox

- **Owner:** platform event infrastructure.
- **Classification:** platform primitives.
- **Why:** consume external domain events safely and publish Track facts reliably.
- **Local policy:** Track event schemas and consumer effect.
- **Do not build:** private event bus/outbox.

### SH-047 / SH-048 — reliable jobs / retry

- **Owner:** shared queue infrastructure.
- **Classification:** platform primitives.
- **Why:** expiration, reconciliation, counter rebuild.
- **Local policy:** payload, retryability, business completion.
- **Do not build:** `trackQueue.ts`, `subscriptionRetry.ts`.

### SH-051 / SH-052 / SH-053 — concurrency/lifecycle plumbing

- **Owner:** shared persistence mechanism.
- **Classification:** platform/shared mechanism.
- **Why:** prevent conflicting subscription/grant/plan updates and stale transitions.
- **Local policy:** lock key and valid transitions.
- **Do not build:** in-memory mutex/state-machine infrastructure.

### SH-055 — `runDeadlineExpiration`

- **Owner:** shared scheduler/queue.
- **Classification:** cross-cutting capability.
- **Why:** dispatch owner-defined expiration for subscriptions/grants.
- **Local policy:** what expiry means and transition command.
- **Do not build:** standalone cron engine.

### SH-057 — `consumeCounterAtomically`

- **Owner:** shared database primitive.
- **Classification:** platform primitive.
- **Why:** lower-level counter update used by SH-006 implementation when appropriate.
- **Local policy:** Track period/limit/reversal semantics.
- **Do not build:** custom distributed counter.

### SH-059 — `verifyProviderWebhookSignature`

- **Owner:** shared integration-security shell; adapter supplies Stripe algorithm.
- **Classification:** provider-adapter contract.
- **Why:** authenticate raw Stripe Billing callbacks.
- **Local policy:** accepted endpoint/events/tolerance.
- **Do not build:** `verifyStripeSignature.ts` outside canonical provider implementation.

### SH-060 — `deduplicateProviderEvent`

- **Owner:** provider-owning Module using shared primitive.
- **Classification:** shared mechanism / separate truth.
- **Why:** exactly-one domain effect per provider event.
- **Local policy:** subscription-billing processed-event record and result.
- **Do not build:** reuse Payment’s `ProcessedStripeEvent` without ruling or use TrackSubscriptionEvent as dedupe.
- **Architecture gate:** U-CL01-22.

### SH-061 — `translateProviderStatus`

- **Owner:** provider-owning adapter.
- **Classification:** provider-adapter contract.
- **Why:** map Stripe Billing states/errors to Track vocabulary.
- **Local policy:** explicit mapping version and unknown handling.
- **Do not build:** scattered `switch(stripeStatus)` logic.

### SH-062 / SH-063 — reconcile/capture provider state

- **Owner:** provider-owning Module using shared mechanisms.
- **Classification:** shared mechanism / separate policy and provider snapshot mechanism.
- **Why:** repair missed callbacks and preserve normalized reconciliation evidence if required.
- **Local policy:** which differences are repairable and which require review.
- **Do not build:** generic Track provider state store that becomes domain truth.

### SH-072 — `hashCanonicalPayload`

- **Owner:** shared crypto capability.
- **Classification:** platform primitive.
- **Why:** fingerprints for idempotency/provider payload verification or versioned catalog snapshots if architecture requires.
- **Do not build:** local hashing canonicalization.

### SH-080 — `manageVersionedRules`

- **Owner:** each policy Module over shared versioning mechanism.
- **Classification:** shared mechanism / separate policy.
- **Why:** likely support for plan/policy versioning once U-CL01-23 is resolved.
- **Local policy:** Track revision/effective semantics.
- **Do not build:** a generic plan versioning system before the decision.

### SH-091 — `requestSearchProjectionRefresh`

- **Owner:** Search / Public Visibility.
- **Classification:** another Module’s public interface.
- **Why:** candidate search boost changes.
- **Local policy:** when a Track change warrants refresh and source evidence/version.
- **Do not build:** `typesenseSync.ts`, direct `SearchUpsertEvent` writes.

### SH-095 / SH-096 / SH-097 / SH-098 — Privacy protocol

- **Owner:** Privacy orchestrates; Track executes its truth.
- **Classification:** cross-cutting protocol.
- **Why:** subject inventory, Track-target execution, retention facts, approved anonymization.
- **Local policy:** which Track fields can be erased/anonymized/revoked/retained.
- **Do not build:** `privacyRequestService.ts`, local retention-exemption table.

### SH-109 — `snapshotExternalDecision`

- **Owner:** consuming domain owner.
- **Classification:** shared snapshot pattern / separate truth.
- **Why:** Order/Booking consumers preserve Track decision history.
- **Track role:** return sufficient evidence; do not write the consumer snapshot.
- **Do not build:** `TrackOrderSnapshot` as duplicate Order truth.

### SH-115 — `buildAggregateProjection`

- **Owner:** projection owner.
- **Classification:** shared projection mechanism / separate policy.
- **Why:** rebuild TrackUsageCounter.
- **Local policy:** event filtering, period grouping, projection version.
- **Do not build:** generic projection framework inside Track.

### SH-119 — `applyTemporaryFeatureGrant`

- **Status:** proposed ruling; ownership partly unresolved.
- **Why relevant:** future deterministic temporary boosts may need a Track grant.
- **Rule:** do not implement until ownership is resolved. Never use it as justification for arbitrary local feature flags.

---

## 16. Module-Internal Operations

These remain local because they encode Track-specific business semantics.

| Operation | Purpose | Input | Output | Source truth affected | Why local |
|---|---|---|---|---|---|
| `validateTrackActorBinding` | Prove track/profile/User consistency | user, track, profile refs | valid/invalid binding facts | none | Track schema has multi-profile attachment and needs owner-specific invariant |
| `validateTypedEntitlementValue` | Enforce entitlement-definition/value compatibility | definition + supplied value | normalized typed value/denial | mappings/grants on write | Track-specific value semantics |
| `resolveGrantPrecedence` | Choose effective grant source | candidate grants/subscription/plan | winning value/evidence | none | Core commercial policy; blocked by U-CL01-20 |
| `materializeSubscriptionGrants` | Create/update grants from approved subscription policy | subscription + plan mappings | grant changes | TrackEntitlementGrant | Track owns subscription→grant policy |
| `applySubscriptionTransition` | Apply approved TrackSubscription transition | current state + trigger | new state/history/effects | subscription/events/grants | Track lifecycle owner; blocked by U-CL01-21 |
| `deriveUsagePeriodBounds` | Calculate quota window | period policy + instant/context | periodStart/periodEnd | none | Track quota semantics; some cases blocked by U-CL01-26 |
| `buildTrackUsageReceipt` | Return canonical accepted use evidence | usage event + counter | receipt | none | Track owns quota accounting result |
| `quoteOrderTrackPolicy` | Compose buyer fee/seller commission decisions | actor contexts + policy instant | quote/evidence | none | Track owns current commercial quote; snapshot remains Order-owned |
| `classifyTrackBillingEvent` | Decide which normalized provider event can affect Track | provider event | Track trigger/ignored/review | none | Subscription-provider mapping belongs with Track adapter under PR-CL01-04 |
| `determineGrantExpiryEffects` | Decide what current access changes at deadline/downgrade | grant/subscription context | expiration/revoke/suspend actions | grant/subscription | Track owns current access lifecycle |
| `serializeTrackPrivacyTarget` | Convert Track record into Privacy executor/export response | Track record + disposition | safe execution/export DTO | Track fields when disposition applied | Record-owner privacy semantics |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Lifecycle state machine:** SH-053 may provide transition plumbing; Track owns plan/subscription/grant transition graphs.
2. **Domain event ledger:** SH-031 provides append-only mechanics; `TrackSubscriptionEvent` remains Track truth.
3. **Provider dedupe:** SH-060 provides claim mechanics; the Track subscription processed-event record remains separate from Payment/Calendar/Video records.
4. **Idempotency:** SH-044 provides command mechanism; Track defines semantic identity and replay outcome.
5. **Counters:** SH-057 provides atomic counter mechanics; Track owns period/limit/receipt semantics and TrackUsageEvent proof.
6. **Projections:** SH-115 provides projection mechanics; TrackUsageCounter remains Track projection. Search documents remain Search projection.
7. **Snapshots:** SH-109 provides snapshot pattern; Order/Booking own their snapshots. Track returns decision evidence.
8. **Access grants:** TrackEntitlementGrant is commercial access only. It must never merge with `SensitiveActionSession`, `MediaAccessGrant`, `DigitalDownloadGrant`, `CourseVideoPlaybackGrant`, agreement grants, or video-room grants.
9. **Privacy execution:** SH-095 supplies protocol; Track owns only effects on Track records. Privacy owns parent request/job/target workflow.
10. **Audit:** SH-029 is generic action proof; TrackSubscriptionEvent is domain history; neither replaces the other.
11. **Operational failures:** IntegrationFailure/QueueJob diagnose execution; Track records own commercial state.
12. **Provider snapshots:** reconciliation evidence may be captured separately, but it must not override TrackSubscription except through approved transition policy.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

Protected user/admin commands start with SH-001. Provider callbacks use authenticated provider endpoint semantics instead of a user session. Trusted background workers use a typed system actor/context.

### Role / Authority

Use SH-002 for:

- plan/price/entitlement catalog administration;
- manual grant creation/revocation/suspension/restoration;
- viewing another user’s subscription/grant details;
- support/admin reconciliation actions;
- self-service subscription mutations where resource ownership facts are required.

Track supplies:

- Track resource ID/type;
- User/track/profile binding;
- requested action;
- whether the actor is acting on self or another subject;
- any safe state needed by Role policy.

### Resource ownership

A User may self-manage only the track/profile that resolves to that User and only actions allowed by Role/Track policy. An admin role does not automatically bypass consent, hold, privacy, or step-up requirements.

### Organization context

Not currently a Track. Do not infer organization commercial rights from AccountTrack.

### Admin / support actions

Manual grants, plan publication, reconciliation, provider inspection and destructive corrections require explicit server authority. Support access should return safe provider references and minimal personal information.

### Step-up

Use SH-014 if root/CL-01 action matrix designates an operation high risk. Track must not implement its own MFA state.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Truth owner | Query | Track action gated | Local composition policy | Result |
|---|---|---|---|---|---|
| Authentication | Identity | SH-001 | all protected commands | Track identifies action/target | actor or unauthenticated |
| Authorization | Role | SH-002 | admin/self-service mutations | Track target facts | allow/deny |
| Subscription terms / recurring billing | Consent | SH-008/009 | paid enrollment, relevant plan change | exact required proof per Track action; blocked by U-CL01-25 | proceed / consent required |
| Step-up | Identity | SH-014 | high-risk billing/admin actions if approved | action matrix external; Track supplies target | assured / step-up required |
| ComplianceHold | Hold owner | SH-011 | enrollment/change/grant/use where hold policy applies | map returned hold to Track operation | proceed / blocked / review |
| Actor profile validity | profile owner | SH-003 / SH-004 | Track binding and current decision | correct track→profile mapping | valid / mismatch |
| Entitlement | this Module | SH-005 | consumer commercial gate | Track current policy | granted/denied/value |
| Usage limit | this Module | SH-006 | metered business action | period/limit/accounting | receipt/limit exceeded |
| Professional readiness | Professional Eligibility | SH-016 | **not a Track entitlement condition by default** | consumer composes separately | readiness result |

**Rule:** Track must not collapse consent, Role, hold, professional readiness, or commercial entitlement into one opaque “canProceed” record.

---

## 20. Provider Integrations

### Ownership posture

**Proposed Ruling inherited from `PR-CL01-04`:** Track Subscription & Entitlement owns the Stripe Billing subscription adapter and Track-specific status translation; Payment / Payout / Tax retains general payment, payout, processor-ledger, and tax truth.

Paid production integration remains gated by U-CL01-18/20/21/22/23/25/29.

### Provider-neutral port

A `TrackBillingProviderPort` should expose only Track-needed operations, for example:

- create checkout/enrollment session;
- request plan change/cancellation/portal session as approved;
- fetch provider subscription state for reconciliation;
- parse/normalize verified billing event;
- return provider-neutral references and errors.

Domain services must not import Stripe SDK types.

### Adapter

Stripe-specific code lives under the adapter:

- Checkout/Billing/Customer Portal calls;
- Stripe status mapping;
- Stripe event type mapping;
- provider reference extraction;
- retryability classification.

### Credentials

Use platform secret/config management. Never persist Stripe secrets in Track tables, logs, audit metadata, or domain events.

### Webhook verification

SH-059 validates raw body/signature/timestamp before trusted parse or side effects.

### Provider-event dedupe truth

SH-060 mechanics are mandatory. Exact Track processed-event schema is unresolved U-CL01-22. Requirements once resolved:

- unique `(provider, providerEventId)`;
- payload fingerprint where appropriate;
- claimed/processed result;
- correlation/request context;
- one transaction around claim + domain application or an equally safe effectively-once design;
- no reuse of Payment’s provider-event record without architecture ruling.

### Status/error translation

SH-061 adapter mapping must be explicit and versioned. Unknown statuses fail to `unsupported/review` or equivalent approved result; never default to `active`.

### Reconciliation

SH-062 compares provider state and Track source state. Only Track transition policy can repair Track source state.

### Retry

SH-047/048. Retry only transient technical failures; business rejection, invalid signature, unknown transition and missing consent are not blind-retry conditions.

### Idempotency

Provider event ID and command semantic keys prevent duplicate effects. Redirects/browser retries cannot activate access.

### Privacy deletion

Provider resource deletion or customer/subscription detachment, if legally/technically supported, occurs only under Privacy-approved instruction and provider-owner interface. Billing retention may require retaining provider references; U-CL01-29 controls.

### Operational failure reporting

SH-037 records provider degradation without changing Track source truth by itself.

---

## 21. Events and Outbox

### Module-owned domain facts

At minimum, external consumers need fact families for:

- plan activation/retirement where policy consumers cache catalog data;
- subscription status/plan change;
- entitlement grant/effective-value change;
- usage consumption or limit reached only when a consumer has a legitimate need.

### Emission point

Publish through SH-046 from a transactional outbox after the Track source transaction commits. `TrackSubscriptionEvent` should be appended in the same source transaction for subscription lifecycle history.

### Payload minimization

Events should carry:

- event ID/version/type;
- aggregate ID and aggregate version when available;
- actor track and profile reference only as necessary;
- entitlement key/value only when safe and needed;
- changed status/value/effective time;
- source/evidence IDs;
- correlation/causation IDs.

Do not include:

- raw provider payloads;
- provider secrets;
- consent document contents;
- unnecessary personal data;
- full plan metadata blobs.

### Consumer idempotency

Consumers use SH-045. Track does not guarantee “exactly once”; it guarantees a stable fact event and effectively-once source mutation.

### Events are not commands

`TrackEntitlementGrantChanged` may cause Search to refresh, but the Search effect should be expressed through Search’s approved command/interface or a documented event consumer contract. The event does not give Track ownership of Search.

---

## 22. Background Jobs / Scheduled Work

### 22.1 Expiration dispatcher

- **Purpose:** find grants/subscriptions past an approved effective deadline and invoke Track owner commands.
- **Input:** cursor/window/time.
- **Owner:** Track policy over SH-055/SH-047.
- **Idempotency key:** record ID + expected deadline + transition intent.
- **Retryable:** DB/queue transient failure.
- **Permanent:** invalid state/architecture configuration; route to review.
- **Business truth updated:** TrackSubscription/TrackEntitlementGrant and TrackSubscriptionEvent as applicable.
- **Telemetry:** processed, skipped, conflict, failure counts; no user PII dimensions.

### 22.2 Usage counter rebuild

- **Purpose:** rebuild `TrackUsageCounter` from immutable events.
- **Input:** actor/entitlement/period range or repair cursor.
- **Owner:** Track projection policy over SH-115.
- **Idempotency:** projection version + range.
- **Failure:** source inconsistency/configuration error produces ops signal; events remain unchanged.
- **Business truth:** no source truth updated; only projection.

### 22.3 Billing reconciliation

- **Purpose:** detect missed/out-of-order provider effects.
- **Input:** subscription/provider reference cursor.
- **Owner:** Track under PR-CL01-04 using SH-062.
- **Idempotency:** subscription/provider snapshot/version.
- **Retryable:** provider/network timeout.
- **Permanent/manual review:** unknown status, unresolvable identity, policy conflict.
- **Business truth:** only through approved Track transition command.
- **Telemetry:** lag, mismatch, repaired, review-required counts.

### 22.4 Provider callback work

May be applied synchronously after verification/dedupe or queued through SH-047. If queued, the provider-event claim must prevent duplicate business effects and the worker must be replay-safe.

### 22.5 Catalog seeding

A seed script/command is not a recurring worker. It must be idempotent and version-aware.

---

## 23. Concurrency and Idempotency

### Races to prevent

1. two concurrent metered uses exceeding a quota;
2. duplicate business requests recording two usage events;
3. user plan change racing provider webhook;
4. cancel/change requests racing each other;
5. out-of-order provider events overwriting newer state;
6. manual grant revoke/restore racing expiration;
7. plan retirement racing new enrollment;
8. counter rebuild racing live metering;
9. privacy disposition racing subscription/provider update;
10. duplicate provider callback.

### Lock keys / transaction boundaries

- Metering: `(entitlementId, track, userId, periodStart, periodEnd)` plus semantic use idempotency.
- Subscription mutation: subscription ID or actor-track active-subscription identity once the uniqueness design is resolved.
- Grant transition: grant ID.
- Plan transition: plan ID + expected version.
- Provider event: `(provider, eventId)` claim.
- Privacy executor: target ID + instruction/disposition semantic key.

### Strategy

- Prefer database transaction + row/advisory lock or atomic update.
- Use SH-051/057 for pessimistic/atomic hot paths.
- Use SH-052 for stale admin/catalog changes where optimistic concurrency fits.
- Never use in-memory locks for database-owned state.

### Replay semantics

- same idempotency key + same request fingerprint → return original result;
- same key + different fingerprint → conflict;
- duplicate provider event → prior processed result/no second domain effect;
- already-terminal expiration/revoke command → idempotent current result;
- counter rebuild → deterministic projection for the same source/version.

---

## 24. Media / Storage

This Module currently owns no business attachment or media semantics.

- Do not create `TrackFile`, subscription invoice uploads, local provider document blobs, or MediaAsset mechanics.
- If future plan/legal artifacts require files, Media / File Access owns upload/scan/storage/signed access; the relevant legal/business owner retains contextual meaning.
- Provider webhook raw bodies must not be stored as ad hoc files.

---

## 25. Search / Projection

### Source truth

Candidate boost entitlement and its effective value are Track truth.

### Track-owned projection

`TrackUsageCounter` only. Candidate search documents are not Track-owned.

### Search-owned projection

Search / Public Visibility owns SearchUpsertEvent/Typesense/indexing/query behavior.

### Trigger

When an effective candidate search-boost value changes, Track may call SH-091 with:

- CandidateProfile/source entity reference;
- reason `track_entitlement_changed` or equivalent safe reason;
- Track source/evidence version;
- correlation ID.

### Conditions

Search still composes privacy, public readiness, moderation, verification, and source projection. A Track boost must not force an otherwise non-public candidate into Search.

### What Search must not reconstruct

Search must not infer plan tier or boost from TrackPlan names or raw Track tables. It consumes Track’s public decision/source projection contract.

---

## 26. Notification

Track defines business triggers such as:

- subscription activated/changed/cancelled/past-due as approved;
- grant suspended/revoked/expired;
- quota warning/limit reached if product policy requires;
- reconciliation/manual-review communication if user-facing.

Track supplies safe intent:

- recipient User ID;
- template/event key;
- track/plan display label if safe;
- effective date;
- action route;
- idempotency key.

Notification owns template rendering, email/SMS/push providers, delivery state, retries, preferences and channel routing. No `sendSubscriptionEmail.ts` belongs here.

---

## 27. Audit and Sensitive Access

Keep four evidence classes distinct:

1. **Track domain history:** `TrackSubscriptionEvent` and TrackUsageEvent.
2. **Generic AuditEvent:** SH-029 for administrator/material actions.
3. **Sensitive AccessAuditLog:** SH-030 only where viewing provider/billing/commercial details is classified sensitive by platform policy.
4. **Operational records:** IntegrationFailure/QueueJob/logs/metrics.

Examples:

- subscription status change: TrackSubscriptionEvent + optional AuditEvent;
- manual comped grant: Track grant state + AuditEvent;
- provider timeout: IntegrationFailure, no fake Track status;
- admin reads provider customer/subscription reference: AccessAuditLog if sensitivity policy requires.

---

## 28. Privacy and Retention

### Subject-data inventory

Track may contain:

- `userId`;
- customer/candidate/professional profile IDs;
- provider customer/subscription references;
- subscription dates/status;
- grant records;
- usage events and target references;
- usage counters;
- subscription event history;
- safe metadata potentially containing personal context.

### Privacy executor

Implement SH-095/096. Track reports:

- target types/IDs;
- record relationships;
- provider resources/references;
- erasable/anonymizable/revocable/retention-candidate fields;
- result status.

### Behavior classes

- **Revoke:** current grants/access where privacy instruction requires.
- **Anonymize:** personal identifiers/metadata according to approved mapping while preserving retained commercial evidence.
- **Erase:** only when retention policy permits.
- **Retain:** only when Privacy records/recognizes approved retention requirement.
- **Export:** serialize Track-owned records into Privacy’s export workflow; Track does not create export bundle storage itself.

### Billing retention

`U-CL01-29` is a production blocker for destructive Track privacy behavior. Until resolved:

- do not hard-delete billing/subscription event evidence;
- do not invent a retention duration;
- do not retain extra personal data “just in case”;
- use Privacy’s retention protocol to make the final disposition explicit.

### Provider resources

Deletion/detachment uses provider-owner adapter under Privacy instruction where technically/legal appropriate. Provider references may remain if retention requires.

---

## 29. Observability

### Structured logs

Use SH-032/033 with:

- operation name;
- track;
- plan/subscription/grant IDs as safe opaque refs;
- provider name;
- reason category;
- retry count;
- correlation/causation IDs;
- duration/result.

### Safe dimensions

Avoid user email/name, raw provider customer data, consent content, metadata blobs, or raw webhook payloads.

### Operational records

- SH-037 IntegrationFailure for provider/reconciliation failure.
- SH-038 queue telemetry for expiration/rebuild/reconcile jobs.
- SH-039 health checks for billing adapter/reconciliation lag if operationally needed.
- SH-036 metrics for entitlement resolution latency, quota conflict rate, provider event lag, reconciliation mismatch, dead letters.

Operational records never replace Track source truth.

---

## 30. Security Boundaries

1. Validate all server/admin/provider inputs at runtime.
2. Never trust browser-supplied `userId`, profile ownership, current plan, price amount, entitlement value, or subscription status.
3. Resolve actor server-side and authorize target actions.
4. Provider callback uses raw-body signature verification before trusted parse.
5. Provider secrets remain in secret management and adapter configuration only.
6. Provider SDK objects/types do not cross into domain contracts.
7. Sensitive provider references are not logged or exposed to ordinary clients unless required.
8. Idempotency and replay protection are mandatory on state-changing/provider paths.
9. Rate-limit abuse-prone checkout, portal, manual grant and provider endpoint paths through root platform facilities.
10. Metadata fields are schema-limited/allowlisted; never use arbitrary JSON as an escape hatch for source truth.
11. Entitlement values must be type-validated before persistence and again when read if legacy data may predate constraints.
12. Cross-track/profile mismatch fails closed.
13. A failed Search/Notification/Audit side effect after source commit does not roll back Track truth; the side effect retries.
14. No temporary token/secret should be persisted in plan/subscription/grant metadata.

---

## 31. Error / Decision Result Pattern

Public policy queries should use a stable typed result, compatible with SH-015 if ratified:

```text
decision: allow | deny | warning | review | unavailable
reasonCode: stable machine-readable code
messageKey: optional safe presentation key
evidenceRefs: source-owned opaque references
evaluatedAt
expiresAt / recheckAt: optional
policyVersion / mappingVersion: when applicable
```

Command errors are distinct from policy denials.

Stable error categories:

- `UNAUTHENTICATED`
- `FORBIDDEN`
- `NOT_FOUND`
- `VALIDATION_ERROR`
- `TRACK_PROFILE_MISMATCH`
- `INVALID_TRANSITION`
- `STALE_VERSION`
- `CONSENT_REQUIRED`
- `HOLD_BLOCKED`
- `ENTITLEMENT_DENIED`
- `USAGE_LIMIT_EXCEEDED`
- `IDEMPOTENCY_CONFLICT`
- `CONFIGURATION_UNRESOLVED`
- `PROVIDER_UNAVAILABLE`
- `PROVIDER_EVENT_INVALID`
- `PROVIDER_EVENT_DUPLICATE`
- `PROVIDER_STATUS_UNSUPPORTED`
- `RECONCILIATION_REVIEW_REQUIRED`
- `PRIVACY_RETENTION_REQUIRED`
- `RETRYABLE_FAILURE`

Provider-native error strings/codes may be logged safely in adapter diagnostics but are not public Track reason codes.

---

## 32. Testing Architecture

### Domain unit tests

- plan lifecycle;
- typed entitlement value validation;
- track/profile binding;
- grant effective-date/status evaluation;
- grant precedence once approved;
- usage period boundary derivation;
- subscription transition table once approved;
- provider status mapping.

### State-transition tests

- every permitted/forbidden TrackPlan transition;
- every approved TrackSubscription transition;
- grant suspend/restore/revoke/expire/consume behavior;
- expiry idempotency.

### Public contract tests

- SH-005 typed decision/evidence contract;
- SH-006 metering receipt/denial/replay contract;
- list/current subscription DTOs;
- Order policy quote contract;
- Booking priority contract;
- Candidate boost contract;
- Privacy executor contract.

### Database / integration tests

- uniqueness and foreign-key behavior;
- profile/user/track invariant enforcement;
- typed-value DB checks once added;
- active-subscription uniqueness once approved;
- usage event + counter one-transaction behavior;
- domain event/outbox transactional behavior.

### Authorization tests

- self vs another user;
- admin/support capability boundaries;
- manual grant/plan administration;
- step-up enforcement where configured.

### Compliance tests

- consent required for paid enrollment/change;
- hold block/review;
- buyer fee and commission snapshot evidence;
- no downstream feature infers entitlement from plan name.

### Idempotency / concurrency tests

- N concurrent uses at quota boundary never exceed limit;
- duplicate semantic usage creates one TrackUsageEvent;
- duplicate provider callback one effect;
- plan change vs provider event conflict;
- expiration vs revoke;
- counter rebuild during live usage.

### Provider adapter tests

- valid/invalid signatures through SH-059 contract;
- known/unknown status mapping;
- out-of-order event behavior;
- provider timeout/retry classification;
- reconciliation;
- no redirect-as-authority.

### Privacy tests

- subject enumeration;
- retention required;
- anonymization mapping;
- export contribution;
- duplicate privacy instruction;
- provider deletion/detachment;
- no local PrivacyRequest/DataErasureJob.

### E2E participation tests

- current entitlement used by a consumer without direct Track Prisma access;
- Candidate application limit;
- candidate boost → Search refresh request;
- Order quote → Order-owned snapshot;
- Booking priority decision;
- paid subscription event → current entitlement change;
- privacy instruction → Track result.

---

## 33. Module Invariants

### Rules coding agents must never violate

1. Track Subscription & Entitlement is the sole current commercial-policy source for customer/candidate/professional tracks.
2. `User`, CustomerProfile, CandidateProfile, ProfessionalProfile, Order, Booking, Search, Video, and Digital Goods must not acquire current Track policy booleans as source truth.
3. A Track decision must be bound to the correct User, AccountTrack, and actor profile.
4. `customer` maps to CustomerProfile, `candidate` to CandidateProfile, and `professional` to ProfessionalProfile where profile-scoped context is required.
5. `organization` is not an AccountTrack until `U-CL01-30` is resolved.
6. `TrackPlan`, `TrackSubscription`, `TrackEntitlementGrant`, `TrackUsageEvent`, `TrackUsageCounter`, and `TrackSubscriptionEvent` remain Track-owned.
7. Order may snapshot Track decisions but never mutate Track source records.
8. Booking may apply priority but never own Track priority entitlement truth.
9. Search may project boost but never reconstruct it from plan names or raw Track tables.
10. `TrackUsageEvent` is immutable ordinary usage proof.
11. `TrackUsageCounter` is rebuildable projection and must not become the only usage truth.
12. Metered consumption is atomic and semantically idempotent.
13. The business-event owner decides whether an event counts; Track decides quota accounting once asked to consume.
14. A non-consuming allowance check is not authoritative enforcement.
15. Typed entitlement values must agree with definition value type.
16. Unknown or invalid typed values fail closed.
17. Provider redirects do not activate subscriptions.
18. Provider callbacks must be signature-verified, deduped, translated, and transition-validated before changing Track state.
19. Unknown provider statuses never default to active/success.
20. Payment success, payout, tax, and processor ledger truth do not move into Track.
21. TrackSubscriptionEvent is domain history, not provider-event dedupe truth.
22. Provider-event dedupe truth stays separate for each provider-owning domain.
23. A subscription downgrade/cancel cannot erase prior usage events or consumer snapshots.
24. Grant precedence must not be guessed while U-CL01-20 is unresolved.
25. Subscription transitions must not be guessed while U-CL01-21 is unresolved.
26. Production entitlement keys must not be invented while U-CL01-19 is unresolved.
27. Paid production enrollment must not proceed until consent binding and provider-event record decisions are resolved.
28. Plan mutation must preserve historical interpretation once plans are live.
29. ComplianceHold remains an external reusable stop sign; no local generic blocked flag.
30. ConsentLog remains Consent-owned and does not itself grant entitlement.
31. Generic AuditEvent and operational logs never replace Track domain events.
32. Notification failure does not rewrite committed Track truth.
33. Search refresh failure does not rewrite committed Track truth.
34. Privacy orchestration remains Privacy-owned.
35. Destructive Track privacy behavior must obey approved billing retention.
36. Track owns no Media/file mechanics.
37. Shared idempotency, locks, queues, retries, provider security and telemetry must be reused, not rebuilt.
38. No direct foreign lifecycle mutation is permitted for implementation convenience.
39. No provider SDK type may become a public Track domain contract.
40. Unresolved architecture must be surfaced and gated, never silently filled in by code.

---

## 34. Prohibited Duplicate Implementations

Do not create these inside or beside the Module as substitutes for canonical owners:

- `trackAuth.ts`
- `subscriptionAuth.ts`
- `getCurrentUser.ts`
- `trackPermissions.ts`
- `entitlementAdminPermissions.ts`
- `subscriptionConsentService.ts`
- `billingConsent.ts`
- `trackComplianceHold.ts`
- `isSubscriptionBlocked.ts`
- `audit.ts`
- `subscriptionAuditService.ts`
- `sendSubscriptionEmail.ts`
- `notificationHelper.ts`
- `idempotency.ts`
- `trackIdempotencyStore.ts`
- `quotaManager.ts`
- `applicationLimitService.ts` outside the SH-006 implementation
- `atomicUsageCounter.ts` that bypasses SH-057
- `trackQueue.ts`
- `subscriptionRetry.ts`
- `webhookUtils.ts`
- `verifyStripe.ts`
- `processedStripeEvent.ts` copied from Payment
- `stripeStatusMapper.ts` scattered outside the Track adapter
- direct Typesense client / `reindexCandidate.ts`
- local `SearchUpsertEvent` repository
- `privacyRequestService.ts`
- `trackErasureJob.ts` as a Privacy workflow
- local retention-exemption table
- Track-owned Order pricing snapshot table
- Track-owned Booking priority state
- Track-owned JobApplication record/counter
- Track-owned video/download access grants
- generic `IntegrationFailure`, `QueueJob`, or incident tables
- feature-local `isPremium`, `isPro`, `hasPriority`, `feeWaived`, `commissionRate`, `applicationLimit`, `searchBoost` current-policy fields.

---

## 35. Unresolved Decisions

These are binding implementation gates inherited from CL-01 or identified by current schema evidence.

| ID | Question | Why unresolved | Blocks |
|---|---|---|---|
| `U-CL01-18` | How is a default/free plan represented: TrackSubscription, direct grants, or both? | Registry expects default free assignment; schema/provider defaults do not settle semantics. | production free-plan provisioning and free↔paid transitions |
| `U-CL01-19` | What are the exact production entitlement keys, types and track applicability? | Registry names examples but no approved canonical production catalog. | production seed/catalog activation |
| `U-CL01-20` | What is grant precedence across paid, free, comped/manual, temporary grants? | Multiple active sources can overlap; no deterministic winner policy supplied. | production SH-005 effective resolution |
| `U-CL01-21` | What is the exact TrackSubscription transition graph? | Enum exists; trial, grace, pause, cancel, downgrade and provider ordering semantics are absent. | paid lifecycle/provider side effects |
| `U-CL01-22` | What owner-specific processed Stripe Billing event record is used? | SH-060 requires separate provider-event truth; TrackSubscriptionEvent is not unique dedupe proof; Payment’s record belongs to another domain. | live webhook side effects |
| `U-CL01-23` | What is plan revision/effective-date history? | Current TrackPlan is mutable and lacks immutable revision/effective model. | safe live plan changes/historical interpretation |
| `U-CL01-24` | How are typed entitlement values constrained? | Current schema permits mismatched/multiple value columns. | production mapping/grant mutations |
| `U-CL01-25` | How are subscription/recurring-billing/plan-change consents immutably bound? | Consent proof owner is known; Track schema has no settled binding/snapshot. | production paid enrollment/change |
| `U-CL01-26` | What are candidate application-limit period, timezone and refund/reversal semantics? | UsagePeriod exists but product policy is missing. | candidate quota integration |
| `U-CL01-27` | What are buyer-fee/seller-commission rounding, basis-point and snapshot rules? | Entitlement value types exist; transaction computation rules do not. | final `quoteOrderTrackPolicy`/Order integration |
| `U-CL01-28` | What does priority scheduling rank mean and does use consume quota? | Track entitlement exists; Booking semantics absent. | final Booking integration |
| `U-CL01-29` | What billing/subscription evidence must be retained/anonymized and for how long? | Legal/privacy duration and field policy absent. | destructive privacy paths |
| `U-CL01-30` | Does organization commercial access remain a separate model or become another AccountTrack? | Shared-ops registry explicitly leaves owner unresolved. | future org plans; does not block current three tracks |
| `U-TSE-01` | Which price field is canonical after catalog activation: TrackPlan.monthlyPriceCents or TrackPlanPrice.amountCents? | Current schema stores both without reconciliation rule. | production price mutation/plan presentation |
| `U-TSE-02` | Should billing cadence have a dedicated enum instead of TrackUsagePeriod? | Current interval field overloads quota-period vocabulary. | schema hardening before broader billing cadence support |
| `U-TSE-03` | What DB constraints enforce exact profile binding and one active subscription per actor track? | Application invariant is confirmed but schema does not enforce it. | production subscription/grant creation |
| `U-TSE-04` | What persistent semantic idempotency reference is stored for TrackUsageEvent? | SH-006 requires replay safety; current event schema has no key. | production metering |
| `U-TSE-05` | Is a separate grant-history event record required beyond TrackSubscriptionEvent/Audit? | Grant status has mutable fields; current schema lacks explicit grant event ledger. | auditability standard for manual/suspend/revoke flows; core grant source truth can be planned but history design must be settled before high-risk admin launch |

### Implementation posture

For any unresolved item, a coding agent must either:

1. obtain an architecture ruling and update this file/CL-01 architecture as required; or
2. implement only noncontroversial interfaces/mechanisms with production behavior disabled, fixture-only, or fail-closed.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. This Module owns the current commercial plan/subscription/entitlement/usage policy for customer, candidate and professional account tracks.
2. It owns the nine Track models and nine Track enums listed in Section 3.
3. It implements canonical SH-005 `resolveEntitlement` and SH-006 `consumeMeteredEntitlement`.
4. Consumers use public interfaces instead of direct Track Prisma access.
5. TrackUsageEvent is immutable usage proof; TrackUsageCounter is a rebuildable projection.
6. Order/Booking/other consumers own historical snapshots and business lifecycles.
7. No feature-local premium/quota/waiver/boost/commission/priority truth may be introduced.
8. Authentication, Role, Consent, holds, Audit, Notification, Privacy, Search and Ops remain external owners.
9. Provider state is an external rail; verified/deduped/translated events are required before Track transitions.
10. TrackSubscriptionEvent is Track lifecycle history, not provider-event dedupe truth.
11. Privacy orchestrates; Track implements its target executor.
12. Search remains projection; candidate boost changes use SH-091.
13. Shared reliability/security/provider mechanisms are reused by permanent SH IDs.

### Proposed rulings

- `PR-TSE-01`: code is organized under one Track feature boundary with explicit domain/application/provider/privacy subareas; no generic CL-01 policy service.
- `PR-TSE-02`: adopt CL-01 PR-04 — Track owns Stripe Billing subscription adapter/status translation while Payment/Payout/Tax retains general financial truth.
- `PR-TSE-03`: conservative TrackPlan and TrackEntitlementGrant transition graphs in Section 9 become implementation defaults once reviewed.
- `PR-TSE-04`: counter rebuild uses SH-115 over TrackUsageEvent and never destructive resets.
- `PR-TSE-05`: provider callback processing keeps lifecycle history, provider-event dedupe proof, generic audit and operational failure evidence as four separate records/mechanisms.

### Binding conservative posture

- paid subscription activation is not production-enabled until all mandatory provider/lifecycle/consent/retention gates are resolved;
- production entitlement catalog and precedence are not guessed;
- destructive privacy paths are not enabled without retention ruling;
- schema gaps must be fixed by explicit migration/architecture decision rather than compensated with duplicated consumer state.

---

## 37. Coding-Agent Usage

Before implementing or modifying this Module, an agent must read, in order:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md`;
5. `context/clusters/identity-authority-consent-entitlements/architecture.md`;
6. `context/clusters/identity-authority-consent-entitlements/build-plan.md`;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. relevant dependency public-interface sections, especially Identity & Access, Role / Authority, Consent & Disclosure, Customer / Buyer Profile, Professional Eligibility, Candidate Application & Resume Privacy, Transaction / Order, Booking & Calendar, Search / Public Visibility, Notification, Audit / Event Ledger, Admin Review / Compliance Hold, Privacy / Data Erasure, Observability / Ops, and Payment / Payout / Tax provider-boundary material;
10. current `context/progress-tracker.md`.

Before coding a numbered Module feature, confirm:

- its corresponding CL-01 build-plan feature is allowed to proceed;
- all architecture gates named by that feature are resolved or intentionally fixture-only/fail-closed;
- the prior Module feature exit gate passed;
- no new SH operation is being invented when a canonical one already exists.
