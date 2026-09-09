# Professional Eligibility Module Implementation Plan

> **Module ID:** `professional_eligibility`  
> **Module name:** Professional Eligibility Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/professional_eligibility/implementation-plan.md`  
> **Architecture dependency:** `context/professional_eligibility/module-architecture.md`  
> **Plan status:** Ordered Module implementation roadmap; subordinate to the CL-03 `build-plan.md`

## Core Principle

Implement Professional Eligibility through narrow, verifiable slices that preserve the Module's two responsibilities:

1. own `ProfessionalProfile` source truth and lifecycle; and
2. compose source-owner facts into action-specific professional readiness without duplicating those facts.

For every slice, prefer:

```text
public / observable behavior
→ validated command or query
→ Professional Eligibility-owned policy
→ authoritative ProfessionalProfile write/read when needed
→ canonical Shared Operations / owner-module interfaces
→ reliable event / audit / Search / Notification effects when needed
→ tests
→ exit gate
```

This Module has no provider integration and does not need artificial UI. A valid vertical slice may terminate in a public command/query, a persisted ProfessionalProfile transition, a worker result, a Search refresh request, a privacy executor response, or a contract test proving a neighboring Module boundary.

The Module plan is intentionally narrower than CL-03's build plan. It implements only the Professional Eligibility portions of Cluster features and must not independently reorder or absorb Trust, Marketplace, Payment, Healthcare, Search, Gig, Order, Privacy, Moderation, Audit, or Notification work.

---

## Build Rules

1. Follow the root Workin Ants architecture, project overview, code standards, Canonical Shared Operations Registry, CL-03 architecture, and CL-03 build plan.
2. This Module owns only `ProfessionalProfile`, its lifecycle, professional action-readiness policy, professional public-readiness policy, safe source projection input, and owner-specific privacy execution.
3. Never add a second source of truth for verification, healthcare, KYC/tax/payout, subscription entitlements, holds, Offerings, Gigs, Orders, Search, privacy requests, moderation cases, audit, or notification delivery.
4. Consume other Modules through approved public interfaces or versioned events; direct foreign Prisma repositories are not the default integration pattern.
5. Reuse canonical Shared Operations by their permanent `SH-###` identifiers. Do not introduce local aliases with competing semantics.
6. A Proposed Shared Operation may guide shape but must not become a platform-wide implementation dependency until approved.
7. Validate all server/action/worker inputs at runtime; TypeScript types alone are not validation.
8. Resolve authenticated/system actor and server-side authority before protected mutations or restricted reads.
9. ProfessionalProfile lifecycle transitions use explicit commands and owner policy; no generic public `setStatus` path.
10. Lifecycle mutations are transaction-safe and reject stale commands. Use root-approved SH-051/052/053 mechanics, not in-memory locks.
11. Creation and replay-prone mutations use SH-044 idempotency.
12. Required domain events use SH-046 transactional outbox semantics; best-effort emit-after-write is prohibited.
13. Event consumers use SH-045 and current source truth; duplicate/out-of-order delivery must not duplicate side effects.
14. Readiness is evaluated from current source-owner truth; do not create `ProfessionalReadiness`, `canSell`, or a hidden cache as authority.
15. `stripeReady`, `stripeAccountId`, `verifiedAt`, `verificationExpiresAt`, `trustScore`, `ratingAverage`, and `ratingCount` cannot satisfy a gate.
16. A required dependency outage or unresolved policy fails to a safe non-allow result; it never defaults to allow.
17. Financial readiness is used for activation/publication/respond only after PE-U01/CL-03 U-01 settles the requested action.
18. Search remains a projection. Use SH-094/091; never write `SearchUpsertEvent` or call Typesense here.
19. Privacy remains Privacy-owned. Implement only SH-095/096/097 owner-side behavior.
20. Moderation remains source-decision owner. Use SH-103 for target execution; do not create local moderation case truth.
21. Audit/Observability records are evidence/diagnostics, not ProfessionalProfile or readiness truth.
22. No Stripe, screening, BAA/e-sign, Search, email/SMS/push, or other provider client/webhook is introduced in this Module.
23. Every numbered feature ends with exact tests and an exit gate. The next feature does not begin until the previous exit gate is passing or the plan explicitly records an approved exception.
24. If a numbered feature reaches an Unresolved Decision that is a real prerequisite, stop, document it, and either obtain an architecture ruling or keep the affected path disabled.
25. A progress update cannot redefine architecture. Update `module-architecture.md` first when a binding decision changes.

---

## Preconditions

### Hard dependencies before Feature 01

The repository must provide, or the Cluster/root plan must have an approved implementation path for:

- Prisma/PostgreSQL access through the root-approved data layer;
- current `ProfessionalProfile` and `ProfileStatus` schema;
- database uniqueness for `ProfessionalProfile.userId` and `ProfessionalProfile.slug`;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- root-approved concurrency primitives such as SH-051/052/053;
- SH-046 transactional domain-event/outbox support before reliable lifecycle events are claimed;
- root-approved runtime input validation;
- request/correlation context and safe structured logging.

Feature 01 must not create local substitutes if one of these is incomplete. It may define/contract-test the call boundary and remain blocked on the canonical implementation.

### Hard architecture decisions before enabling lifecycle transitions

- PE-U03 must be resolved for every status adjacency the implementation enables.
- PE-U06 must be reconciled with the root concurrency standard before choosing a permanent aggregate-version strategy or adding a schema column.

The safe fallback is to implement profile creation/update/context and keep unsupported transitions explicitly disabled rather than guess.

### Dependencies required by Feature 02 readiness

The following owner interfaces are required for production readiness composition:

- SH-005 Track Entitlement;
- SH-011 ComplianceHold evaluation;
- SH-017/018 Trust requirement/readiness;
- SH-019 Payment financial readiness;
- SH-020 Healthcare readiness;
- SH-022 Taxonomy requirement triggers.

Trust/Healthcare/Payment may initially be represented by contract test doubles while their Module implementations are still being built, exactly as the CL-03 build plan allows. A test double must implement the source-owner public contract and must not become local persistence or production truth.

### Dependencies required by Features 03–05

- SH-024 professional public-readiness contract;
- SH-094 source projection mechanism;
- SH-091 Search refresh interface;
- owner-specific Marketplace, Gig, and Order target-context queries/contracts;
- SH-045 event inbox dedupe;
- SH-047/048 reliable job/retry/dead-letter infrastructure;
- SH-041 Notification request if enabled for a specific trigger.

These may be stubbed behind the exact owner contract during earlier features. Production integration cannot be claimed until the real owner interface is contract-tested.

### Dependencies required by Feature 06

- SH-103 moderation target-execution contract;
- SH-029 generic audit;
- SH-011 current hold query;
- approved ProfessionalProfile suspension/reinstatement transition policy.

No generic manual “force allow/force active” override may be invented if the external source-decision model is incomplete.

### Dependencies required by Feature 07

- SH-095/096/097 Privacy protocol;
- SH-098 anonymization primitive where applicable;
- legal/Privacy retention decision path for any destructive action being enabled;
- SH-091 Search removal/refresh after privacy source change.

### Provider setup

None belongs to this Module. Provider readiness is a dependency concern of Trust, Healthcare, Payment, Search, Notification, or other provider-owning Modules.

### Cluster sequencing relationship

This plan touches only these CL-03 milestones:

- Cluster Feature 01 — Professional Profile Foundation;
- Cluster Feature 03 — Professional Readiness Composition Contract;
- Cluster Feature 08 — Offering Publication and Public Professional Supply, only the Professional Eligibility side;
- Cluster Feature 11 — Readiness Change Propagation and Neighboring-Cluster Integration;
- Cluster Feature 12 — Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion;
- Cluster Feature 13 — CL-03 hardening.

It does not independently implement Cluster Features 02, 04–07, 09–10 or their owner Modules.

---

# Phase 1 — ProfessionalProfile Source-of-Truth Foundation

## 01 — Professional Profile Foundation

### Objective

Implement the authoritative `ProfessionalProfile` boundary so an authenticated User can idempotently obtain at most one seller profile, safely read/update allowed ProfessionalProfile fields, and invoke only the subset of lifecycle transitions explicitly approved for this feature.

### Observable Result

When complete:

- an authenticated User can create or retrieve their one ProfessionalProfile;
- concurrent create attempts cannot produce duplicate seller identities;
- the profile starts in `draft`;
- allowed profile fields can be updated through Professional Eligibility;
- `getProfessionalProfileContext` returns a minimized owner DTO rather than the Prisma model;
- unsupported or unresolved status transitions return a stable error/decision instead of writing arbitrary enum values;
- every enabled lifecycle transition is owner-controlled, authorized, concurrency-safe, and event-backed.

### Cluster Build-Plan Link

Primary support: **CL-03 Feature 01 — Professional Profile Foundation**.

This Module feature is the Professional Eligibility implementation of that Cluster slice. It does not implement Offering work from Cluster Feature 02 or readiness composition from Cluster Feature 03.

### Dependencies

- Module architecture Sections 8–10 and PE-U03/PE-U06;
- `ProfessionalProfile` / `ProfileStatus` Prisma schema;
- SH-001 Identity actor context;
- SH-002 Role / Authority;
- SH-044 idempotent command;
- SH-051/052/053 root-approved concurrency/state-machine primitives;
- SH-046 transactional outbox;
- SH-114 one-to-one profile provisioning mechanism;
- root runtime validation and request/correlation context.

### In Scope

- public request/response schemas for profile create/update/context;
- ProfessionalProfile repository restricted to owned persistence;
- one-to-one provisioning using database uniqueness + SH-114/044;
- explicit mutable-field policy;
- slug normalization only if a root/shared canonical slug mechanism already exists; otherwise validate shape and uniqueness without inventing a new global normalizer;
- safe `getProfessionalProfileContext` DTO;
- lifecycle command framework with expected-state/concurrency checks;
- only the transition subset approved by the Feature 01 transition table;
- ProfessionalProfile created/status-changed event mapping and outbox;
- relevant Search refresh hook contract may be declared but public projection behavior waits for Feature 03;
- tests for uniqueness, ownership, validation, stale writes, and event atomicity.

### Out of Scope

- Trust/Healthcare/Payment/Entitlement readiness composition;
- enabling activation/resume if their gate policy is not yet approved;
- Offerings, GigResponses, Orders, payouts, KYC, BAA, verification, TrustBadge;
- Search provider/index implementation;
- profile media lifecycle;
- CandidateProfile lifecycle;
- privacy erasure execution;
- generic audit infrastructure;
- removing legacy compatibility fields unless an explicitly approved migration is necessary for this feature.

### Module-Owned Data

Affected:

- `ProfessionalProfile`;
- `ProfileStatus` only as used by ProfessionalProfile;
- ProfessionalProfile domain-event semantics.

Important field rules:

- `userId` unique is one-to-one seller identity enforcement;
- `slug` unique is a database conflict boundary;
- `status` defaults `draft`;
- `stripeReady`, `stripeAccountId`, `verifiedAt`, `verificationExpiresAt`, `trustScore` are not gate truth;
- `ratingAverage`/`ratingCount` are derived projections only;
- `onboardingCompleteAt` remains behaviorally inert unless PE-U07 is resolved.

### Public Interfaces

Introduce/complete:

- `createProfessionalProfile`;
- `updateProfessionalProfile`;
- `getProfessionalProfileContext`;
- explicit lifecycle command interfaces for only the transitions approved in this feature;
- event contracts for ProfessionalProfile created and enabled status changes.

Do **not** expose:

- `setProfessionalStatus(status)`;
- raw `getProfessionalProfileWithAllRelations`;
- a `canSell` property;
- any foreign readiness state in the context DTO.

### Shared Operations Used

#### SH-001 `resolveAuthenticatedActor`

- **Owner:** Identity & Access.
- **Invocation:** every user/admin profile command/query entry point.
- **Local policy:** which ProfessionalProfile action is requested.
- **Prohibited duplicate:** `professional-auth.ts`, current-user/session helper that becomes a second actor source.

#### SH-002 `authorizeResourceAction`

- **Owner:** Role / Authority.
- **Invocation:** after resolving actor, before owner mutation/restricted context read.
- **Local policy:** profile relationship and action facts.
- **Prohibited duplicate:** seller role engine or admin bypass.

#### SH-044 `executeIdempotentCommand`

- **Owner:** platform application infrastructure.
- **Invocation:** provisioning and replay-prone lifecycle commands.
- **Local policy:** command fingerprint and conflict behavior.
- **Prohibited duplicate:** local idempotency table/map.

#### SH-051/052/053 concurrency/lifecycle mechanics

- **Owner:** shared persistence/mechanism.
- **Invocation:** mutation transaction.
- **Local policy:** ProfessionalProfile conflict set, expected state, allowed transition graph.
- **Prohibited duplicate:** in-memory lock or generic status engine that owns policy.

#### SH-046 `publishDomainEvent`

- **Owner:** platform outbox.
- **Invocation:** in the authoritative mutation transaction.
- **Local policy:** ProfessionalProfile event family/payload/version.
- **Prohibited duplicate:** best-effort post-commit emit.

#### SH-114 `provisionOneToOneProfile`

- **Owner:** shared provisioning mechanism; profile owner retains truth.
- **Invocation:** create command.
- **Local policy:** ProfessionalProfile defaults/field validation.
- **Prohibited duplicate:** generic seller/profile table or duplicated one-to-one creation utility.

### Domain Logic

- one User maps to at most one ProfessionalProfile;
- create is idempotent: the same semantic request returns the canonical profile rather than a duplicate;
- profile starts `draft` by schema default;
- only explicitly listed mutable fields may change;
- immutable identifiers/foreign owner truth cannot be patched through a generic object spread;
- status is changed only by an explicit lifecycle command;
- transition code must reference an approved table; unknown/unsupported adjacency returns `POLICY_UNRESOLVED` or `CONFLICT` as appropriate;
- `active` never implies all seller actions are allowed;
- legacy compatibility fields cannot be populated as a shortcut for later features;
- context DTO reveals only minimum owner facts necessary for the caller contract.

### Authorization / Compliance

- ordinary create/update requires authenticated User ownership;
- admin/support actions require SH-002, not role-name checks in this Module;
- no Trust/KYC/Healthcare completion is required merely to persist a draft profile;
- profile archive/suspension is not privacy erasure;
- no organization role creates implicit control of a ProfessionalProfile;
- client-provided `userId`, `status`, or ownership flags are untrusted.

### Database / Transaction Behavior

#### Provisioning

```text
resolve actor
→ validate input
→ SH-044 claim semantic create command
→ transaction
   → attempt/load one ProfessionalProfile by unique userId
   → enforce/resolve slug uniqueness
   → create only if absent
   → append required outbox event if created
→ commit
→ return canonical profile result
```

Concurrent create must be safe even when both requests pass an initial read. Database uniqueness is the final invariant, and duplicate-key recovery must resolve to the canonical row rather than return an opaque server error where the semantic request is equivalent.

#### Updates / transitions

- use root-approved row lock/CAS;
- require expected current status for status transitions;
- require expected `updatedAt` or another approved concurrency token for general edits until PE-U06 is settled;
- never use last-write-wins for critical lifecycle changes;
- source write and outbox append commit atomically.

### Events / Jobs

Events:

- ProfessionalProfile created;
- status changed for every enabled lifecycle transition.

No Module-owned worker is required yet.

Event publication failure is handled by transactional outbox/retry. Do not roll back a committed profile through an ad-hoc compensating status merely because a downstream consumer is temporarily unavailable.

### Provider Integration

None. Any provider code discovered or proposed in this feature is a scope violation.

### UI / Admin Surface

Only if an existing onboarding/profile surface is in the product scope:

- create/start professional profile;
- edit approved profile fields;
- display current lifecycle status;
- avoid a single misleading “verified”/“ready” badge.

No new admin dashboard is required solely to complete this feature.

### Failure Behavior

- unauthenticated: `UNAUTHENTICATED`, no DB write;
- unauthorized target: `FORBIDDEN` with no information leak;
- invalid profile fields: `VALIDATION_ERROR`;
- slug already held by another profile: stable conflict/validation result;
- duplicate create with equivalent semantic request: return canonical existing result;
- duplicate idempotency key with different payload: `CONFLICT`;
- stale update/transition: `CONFLICT` with safe current-state metadata if permitted;
- unresolved transition: `POLICY_UNRESOLVED`, no status write;
- DB/outbox failure before transaction commit: rollback;
- downstream consumer unavailable after committed outbox: retry asynchronously; profile truth remains committed.

### Tests

Required:

- unit: input/mutable-field policy;
- unit: every approved/denied Feature 01 transition;
- database integration: `userId` one-to-one and slug uniqueness;
- concurrency: simultaneous create for one User;
- concurrency: stale edit and conflicting transition;
- idempotency: same key/same input and same key/different input;
- authorization: owner, other User, approved admin/system cases;
- contract: `getProfessionalProfileContext` does not expose foreign relations/compatibility gate fields;
- outbox integration: create/status write and event publication are atomic;
- regression: no code path reads or writes compatibility fields as readiness truth;
- privacy semantic regression: archive is not erasure.

### Documentation Updates

If implementation resolves any portion of PE-U03 or PE-U06:

- update `module-architecture.md` lifecycle/concurrency sections;
- update the exact public command contract;
- update CL-03 architecture only if the decision changes a Cluster boundary;
- update progress tracker.

Do not mark `onboardingCompleteAt` or compatibility fields authoritative without a separate architecture update.

### Acceptance Criteria

1. One User cannot acquire two ProfessionalProfiles under concurrent requests.
2. The canonical profile can be retrieved idempotently after replay.
3. All enabled profile mutations are runtime-validated, authorized, and owner-only.
4. No generic status setter exists.
5. No unsupported lifecycle transition can be forced through route/server-action input.
6. `getProfessionalProfileContext` is sufficient for downstream contract tests without direct ProfessionalProfile repository access.
7. Compatibility fields do not satisfy or encode readiness.
8. Source write + event outbox behavior is reliable and transactionally safe.
9. All required unit/integration/concurrency/authorization/contract tests pass.

### Exit Gate

Before Feature 02 begins:

- root-required typecheck/lint/build checks pass;
- Feature 01 test suite passes;
- one-to-one/concurrency test proves no duplicate profile under race;
- public context DTO is contract-tested;
- enabled transition subset has an explicit documented table;
- unsupported transitions are explicitly disabled/non-allow;
- no foreign repository or provider dependency exists in the Module;
- progress tracker records Feature 01 complete and any remaining PE-U03/PE-U06 limitations.

---

# Phase 2 — Professional Readiness Decisions

## 02 — Professional Readiness Composition Contract

### Objective

Implement SH-016 `evaluateProfessionalReadiness` as the single Professional Eligibility decision boundary for approved seller actions, composing current profile, entitlement, taxonomy, verification, healthcare, financial, and hold facts without persisting a second readiness source.

### Observable Result

A caller can ask whether a ProfessionalProfile may perform one controlled action and receive a deterministic, audience-safe decision showing blocking/remediation categories and source evidence references.

For approved policies, the decision changes as source owners change. For unresolved policies such as PE-U01, the result is explicitly `review`/`unavailable` rather than guessed.

Activation/resume commands may now invoke this current decision before changing ProfessionalProfile state when their lifecycle transitions are otherwise approved.

### Cluster Build-Plan Link

Primary support: **CL-03 Feature 03 — Professional Readiness Composition Contract**.

Also completes the Professional-side readiness dependency needed by later CL-03 Feature 08 publication and Feature 11 integration.

### Dependencies

- Feature 01 exit gate;
- SH-005 Track Entitlement;
- SH-011 ComplianceHold;
- SH-017/018 Trust;
- SH-019 Payment;
- SH-020 Healthcare;
- SH-022 Taxonomy requirements;
- SH-001/002 for authorized decision access;
- PE-U01 action-specific financial timing;
- PE-U05 exact entitlement key mapping;
- dependency public contracts from their owning Module architecture or CL-03 approved contract.

Trust/Healthcare/Payment implementations may be contract stubs during early build, but no production completion is claimed until real owner contracts pass.

### In Scope

- controlled v1 ProfessionalAction type/enum for approved action names;
- owner-specific readiness decision schema aligned with SH-015 principles without making SH-015 a platform dependency while Proposed;
- `get`/validate target context contracts needed by each action;
- action-to-gate policy table;
- profile lifecycle dimension;
- entitlement dimension;
- hold dimension;
- taxonomy requirement resolution;
- conditional Trust and Healthcare calls;
- conditional Payment call only where explicitly approved;
- stable normalized reason catalog and safe evidence-reference structure;
- dependency-unavailable classification;
- audience-aware reason redaction;
- activation/resume current-readiness check where those transitions are approved;
- unit/contract/failure/security tests.

### Out of Scope

- creating readiness persistence/cache as authority;
- provider integrations;
- mutating Offering/Gig/Order;
- Search indexing;
- automatic status change when a dependency later becomes not-ready;
- payout authorization/execution;
- manual override system;
- resolving PE-U01 by implementation convenience.

### Module-Owned Data

No new source model is introduced.

Affected owned truth only when an approved lifecycle command uses the decision:

- `ProfessionalProfile.status` for activate/resume.

Owned non-persisted policy/contracts:

- ProfessionalAction vocabulary;
- action-to-gate matrix;
- ProfessionalReadinessDecision response;
- reason-code vocabulary;
- policy version identifier.

### Public Interfaces

Introduce/freeze:

- **SH-016 `evaluateProfessionalReadiness`**;
- controlled action vocabulary;
- versioned decision response;
- safe source evidence reference shape.

Update, when approved:

- `activateProfessionalProfile` to require a fresh `activate_profile` allow result;
- `resumeProfessionalProfile` to require the appropriate current readiness result before returning to active.

Do not create separate externally authoritative `authorizeOfferingPublish`, `authorizeGigResponse`, or `canParticipateInOrder` engines. Consumers use SH-016 with the controlled action/context.

### Shared Operations Used

#### SH-005 `resolveEntitlement`

- **Owner:** Track Subscription & Entitlement.
- **Invocation:** action policy says professional-track entitlement is relevant.
- **Local policy:** action → entitlement key/value requirement.
- **Prohibited duplicate:** `isPremium`, `sellerPlan`, `professionalCanSell`.

#### SH-011 `evaluateComplianceHold`

- **Owner:** Admin Review / Compliance Hold.
- **Invocation:** action-sensitive stop-sign evaluation.
- **Local policy:** which hold scopes/reason classes block which ProfessionalAction.
- **Prohibited duplicate:** `profile.blocked`, local hold service.

#### SH-017 / SH-018

- **Owner:** Trust Verification / Screening.
- **Invocation:** taxonomy/target context indicates verification/license/background requirements.
- **Local policy:** when the professional action requires the returned Trust decision.
- **Prohibited duplicate:** direct VerificationCheck/TrustBadge queries or local verification boolean.

#### SH-019 `evaluateFinancialReadiness`

- **Owner:** Payment / Payout / Tax.
- **Invocation:** **only** for a ProfessionalAction whose financial timing is approved.
- **Local policy:** action → required financial dimensions.
- **Prohibited duplicate:** `stripeReady`, `canPayout`, KYC/tax/account reconstruction.

#### SH-020 `evaluateHealthcareReadiness`

- **Owner:** Healthcare / Regulated Services.
- **Invocation:** taxonomy/target context triggers healthcare lane.
- **Local policy:** action interpretation only.
- **Prohibited duplicate:** local healthcare/BAA boolean.

#### SH-022 `resolveTaxonomyRequirements`

- **Owner:** Taxonomy & Classification.
- **Invocation:** before Trust/Healthcare composition where classification drives requirements.
- **Local policy:** how triggered requirements enter this action.
- **Prohibited duplicate:** hardcoded high-risk/healthcare category arrays.

#### SH-015 `returnDecisionResult` — Proposed only

- **Owner:** proposed shared contract.
- **Invocation:** shape alignment only until approved.
- **Local policy:** all action/gate/reason semantics.
- **Prohibited duplicate:** prematurely declaring a universal platform decision schema.

#### SH-029 `appendAuditEvent`

- **Owner:** Audit / Event Ledger.
- **Invocation:** high-impact lifecycle actions that execute after an allow decision, not every pure readiness query unless policy requires decision proof.
- **Local policy:** safe action/evidence metadata.
- **Prohibited duplicate:** readiness decision ledger hidden in Audit.

### Domain Logic

#### Controlled action set

Feature specification must freeze the v1 serialization for the approved subset of:

- activation;
- public professional visibility;
- Offering publication;
- Gig response;
- seller-side Order participation.

No free-form action key from the client.

#### Composition algorithm

```text
validate caller + target/action contract
→ load current ProfessionalProfile owner facts
→ reject non-operational lifecycle state for requested action
→ resolve action entitlement if required
→ evaluate active ComplianceHold for target/action
→ resolve taxonomy-triggered requirements
→ evaluate Trust only if required
→ evaluate Healthcare only if required
→ evaluate Payment only if this action's financial policy is approved and requires it
→ normalize all source decisions to Professional Eligibility reason codes
→ redact details by caller audience
→ return allow / deny / review / unavailable + source/policy versions
```

#### Result rules

- deterministic denial from any required blocking dimension prevents `allow`;
- dependency `review` propagates as review unless another deterministic denial already controls the overall decision;
- required dependency unavailable prevents `allow`;
- unresolved policy prevents `allow`;
- multiple safe blockers should be returned where doing so helps remediation without leaking sensitive information;
- source evidence IDs are references, not copied source records;
- the consumer still owns its local lifecycle preconditions even after a Professional allow decision.

#### Compatibility-field regression rule

The composer must have no branch reading:

- `ProfessionalProfile.stripeReady`;
- `stripeAccountId`;
- `verifiedAt`;
- `verificationExpiresAt`;
- `trustScore`;
- `ratingAverage`/`ratingCount` as eligibility truth;
- TrustBadge alone.

### Authorization / Compliance

- caller must be authorized to ask for the profile/target decision;
- generic public callers must not receive private blocker detail;
- onboarding/profile owner may receive safe remediation categories but not raw source-owner evidence;
- admin/support does not automatically receive raw screening/healthcare/financial information;
- ConsentLog is not queried here as generic permission proof; Trust/Healthcare own whether their consent proof is sufficient;
- unresolved PE-U01 produces non-allow, never an implicit “financial not required” choice unless product policy explicitly approves that outcome.

### Database / Transaction Behavior

Pure SH-016 evaluation normally performs no Module-owned write.

If activation/resume executes after an allow result:

1. evaluate external dependencies as freshly as practical and retain their source/version references;
2. begin ProfessionalProfile mutation transaction;
3. re-check expected current profile status/concurrency token;
4. apply the approved local transition;
5. append outbox event;
6. commit.

Do not attempt a distributed transaction across Trust/Healthcare/Payment/Track/Hold databases. The decision carries source versions; dependency-change events later trigger reevaluation. A foreign action owner should call SH-016 immediately before its own mutation and retain any approved decision snapshot only in its own lifecycle if root architecture requires it.

### Events / Jobs

Normal readiness query emits no business event.

Activation/resume that changes profile state emits the standard ProfessionalProfile status-changed event.

Dependency-change reevaluation jobs are deferred to Feature 05.

### Provider Integration

None. Contract test fixtures may simulate normalized owner decisions but must not simulate raw Stripe/Checkr/BAA provider payloads inside this Module.

### UI / Admin Surface

If an onboarding/readiness summary already exists, it may render only safe dimensions such as:

- Profile;
- Selling access;
- Verification;
- Healthcare;
- Financial setup;
- Holds/review.

It must not show one universal “Verified” badge or expose raw source-owner data.

No separate UI is required for feature completion; SH-016 contract behavior is sufficient observable output.

### Failure Behavior

- invalid action/context: `VALIDATION_ERROR` or target invalid result;
- unauthorized caller: `FORBIDDEN` without evidence leakage;
- profile archived/nonexistent: deterministic non-allow/not-found according to caller contract;
- entitlement/hold/Trust/Healthcare/Payment deterministic block: `deny` with safe normalized reason;
- source owner returns review: `review`;
- required dependency timeout/unavailable: `unavailable`, retryable metadata where safe;
- action policy unresolved: `unavailable`/`review` with `policy.unresolved` class;
- inconsistent source versions/malformed contract: fail closed and record safe operational diagnostic;
- activation/resume stale state after readiness evaluation: `CONFLICT`, no profile write.

### Tests

- unit: full action-to-gate matrix for every approved action;
- unit: decision precedence (`deny`, `review`, `unavailable`, `allow`);
- unit: multiple-blocker normalization;
- unit: audience-specific reason redaction;
- contract: SH-005, 011, 017/018, 019, 020, 022 adapters;
- contract: SH-016 request/response/action serialization;
- integration: no foreign writes/direct foreign repository imports;
- failure: each owner unavailable/timeout/malformed response;
- compliance: unresolved PE-U01 non-allow behavior;
- regression: compatibility booleans/TrustBadge cannot satisfy gate;
- lifecycle integration: activation/resume re-check current profile state and fail stale;
- observability: logs contain safe normalized dependency/result categories only.

### Documentation Updates

If this feature settles:

- PE-U01 for any action;
- PE-U05 entitlement keys;
- exact ProfessionalAction serialization;
- final decision/reason-code contract;

update `module-architecture.md` Sections 11, 19, 31, and 35 before or with code.

If SH-015 is approved globally, update the Module contract to reference the canonical envelope rather than maintaining a merely aligned owner-local shape.

### Acceptance Criteria

1. SH-016 is the only authoritative Professional Eligibility seller-action decision surface.
2. Every approved action has a documented gate matrix and deterministic tests.
3. Every unresolved action policy returns non-allow and is test-covered.
4. All external facts come from owner interfaces, not direct foreign tables.
5. No readiness source table/boolean/cache is authoritative.
6. Source dependency failure cannot result in `allow`.
7. Decision detail is caller-safe and provider-neutral.
8. Activation/resume, when enabled, require current SH-016 allow and concurrency-safe owner transition.
9. All contract/unit/failure/security/integration tests pass.

### Exit Gate

Before Feature 03 begins:

- SH-016 request/response v1 is contract-frozen for approved actions;
- action-to-gate matrix tests pass;
- unresolved PE-U01 cases are explicitly represented and cannot accidentally allow;
- no compatibility field or foreign direct read appears in readiness code;
- source-owner failure tests prove fail-safe behavior;
- activation/resume enabled paths use SH-016 and owner transaction guards;
- root quality commands pass;
- progress tracker records any action still production-disabled.

---

# Phase 3 — Public Visibility and Consumer Contracts

## 03 — Professional Public Readiness and Search Source Projection

### Objective

Implement the ProfessionalProfile side of public visibility: Professional Eligibility decides whether a profile may appear in a public discovery surface, builds a minimal safe source projection, and requests Search refresh without owning Search storage or reconstructing Search internals.

### Observable Result

- Search can request/receive an owner-issued professional public-readiness result;
- a safe ProfessionalProfile source projection can be rebuilt deterministically from source truth;
- a non-public/suspended/archived or otherwise not-ready profile results in a Search hide/remove/refresh request rather than a direct index write;
- lifecycle/profile-public-field changes can request Search refresh reliably;
- financial/verification/healthcare/hold/provider internals never appear in the profile source projection.

### Cluster Build-Plan Link

Supports the ProfessionalProfile/public-readiness portion of **CL-03 Feature 08 — Offering Publication and Public Professional Supply** and establishes contracts used by **Feature 11 — Readiness Change Propagation**.

It does not implement Marketplace's Offering publication transition or Search's index worker.

### Dependencies

- Feature 02 exit gate;
- SH-024 `evaluatePublicReadiness`;
- SH-094 `buildSourceProjection`;
- SH-091 `requestSearchProjectionRefresh`;
- Search public contract;
- PE-U08 public field allowlist/location treatment;
- SH-046/outbox for reliable lifecycle-driven projection effects.

### In Scope

- professional-specific SH-024 implementation;
- exact public-readiness decision inputs and safe reasons;
- v1 public ProfessionalProfile source-projection schema/allowlist;
- deterministic source version included with projection/refresh;
- Search refresh requests after relevant committed profile changes;
- Search removal/hide/restore behavior as requests, not direct writes;
- tests proving omitted sensitive/foreign fields;
- retry-safe Search request integration.

### Out of Scope

- Typesense collection/schema/index/query/ranking code;
- `SearchUpsertEvent` repository;
- Offering source projection;
- TrustBadge projection ownership;
- exact/fuzzy geolocation implementation owned by Location Safety if later needed;
- profile media/file mechanics;
- paid boosts/featured behavior;
- Search privacy orchestration beyond requesting the owner-approved projection effect.

### Module-Owned Data

No new persisted source model.

Read:

- `ProfessionalProfile` owner fields and status;
- current SH-016/SH-024-required source-owner decisions.

Derived only:

- Professional public source projection DTO;
- public-readiness decision.

Search-owned `SearchUpsertEvent` must not be added to this repository.

### Public Interfaces

Introduce/freeze:

- Professional implementation of SH-024 `evaluatePublicReadiness`;
- `buildProfessionalSourceProjection` implementing SH-094;
- Search refresh integration using SH-091.

The source projection contract must be versioned independently from the Prisma model.

### Shared Operations Used

#### SH-024 `evaluatePublicReadiness`

- **Owner:** source/compliance owner; Search composes.
- **Invocation:** before public source projection is considered visible.
- **Local policy:** ProfessionalProfile lifecycle + professional public-readiness dimensions.
- **Prohibited duplicate:** Search evaluating professional eligibility itself.

#### SH-094 `buildSourceProjection`

- **Owner:** each source Module using shared deterministic projection pattern.
- **Invocation:** Search refresh/backfill asks for current safe source document.
- **Local policy:** exact ProfessionalProfile field allowlist and source version.
- **Prohibited duplicate:** generic serializer of full Prisma row.

#### SH-091 `requestSearchProjectionRefresh`

- **Owner:** Search / Public Visibility.
- **Invocation:** after relevant profile/source public-readiness change.
- **Local policy:** reason/action/source version supplied.
- **Prohibited duplicate:** direct `SearchUpsertEvent` insert or Typesense API call.

#### SH-046

- **Owner:** transactional outbox.
- **Invocation:** reliable lifecycle/source change effects.
- **Local policy:** event/refresh trigger semantics.
- **Prohibited duplicate:** best-effort Search call inside DB transaction.

### Domain Logic

- public readiness is not identical to `status=active`;
- `archived` and `suspended` are non-public under the conservative current model unless an explicit future surface says otherwise;
- any additional entitlement/verification/healthcare/hold requirements come through the approved Professional public-readiness policy, not Search;
- Payment financial details are not public projection fields and must not leak into Search;
- TrustBadge/verification may be separate Search inputs from Trust; Professional source projection does not copy raw Trust records;
- source projection is allowlisted, not denylisted;
- projection includes a source version/evaluated time sufficient for Search to reject stale refresh work;
- if PE-U08 is unresolved, production indexing remains disabled until a minimal field list is approved.

### Authorization / Compliance

- internal Search projection request runs under approved system context;
- public source builder must not expose `userId` or private relationship IDs unless the Search contract explicitly approves a public-safe reference;
- no private blocker detail in Search document;
- public location must follow root/Location Safety policy if precise location ever enters scope;
- Search removal after privacy/moderation is projection behavior, not source deletion.

### Database / Transaction Behavior

No Search state is written here.

For a profile mutation that changes public projection:

```text
transaction:
  write ProfessionalProfile
  append owner domain event/outbox effect
commit
→ reliable handler/build source projection
→ SH-091 request refresh/remove/restore
```

A Search outage must not roll back the already-committed ProfessionalProfile change.

### Events / Jobs

- use existing profile lifecycle events as projection triggers;
- projection-relevant profile field changes may request Search refresh through outbox/reliable effect;
- Search owns its own queue/index worker;
- Feature 05 will add external dependency-change reevaluation triggers.

### Provider Integration

None. Typesense is Search-owned and prohibited here.

### UI / Admin Surface

No Module-owned UI required.

Existing profile/onboarding UI may show a safe public-visibility state/reasons if it consumes SH-024. It must not expose Search queue/provider internals.

### Failure Behavior

- public policy unresolved: no public projection; stable review/unavailable result;
- source projection validation failure: fail closed, record operational diagnostic, no index request with partial data;
- Search request unavailable: retry through reliable mechanism; source profile remains committed;
- stale Search request/source version: Search reconciles/rejects per its contract; this Module can rebuild current source projection;
- privacy/moderation indicates non-public: request remove/hide even if profile row remains.

### Tests

- unit: public-readiness matrix;
- unit: projection allowlist and field redaction;
- contract: SH-024 response;
- contract: SH-094 projection schema/version;
- contract: SH-091 request action/reason/source version;
- regression: no KYC/tax/payout, raw verification, healthcare, hold, moderation notes, provider refs, or compatibility gate fields in projection;
- integration: committed profile state survives Search outage;
- replay: repeated refresh request is idempotent downstream;
- backfill: current source projection can be rebuilt without reading Search as truth.

### Documentation Updates

Resolve/document PE-U08 before production indexing. Update:

- Module architecture Section 25 with exact field allowlist/public surfaces;
- Search dependency public-interface documentation;
- progress tracker.

If location behavior introduces Location Safety dependency, add it through an architecture update before code.

### Acceptance Criteria

1. Professional Eligibility, not Search, returns the ProfessionalProfile public-readiness decision.
2. Search source DTO is explicit, versioned, and smaller than the Prisma model.
3. No sensitive/foreign gate internals appear in source projection.
4. Search refresh uses SH-091 only.
5. Search failure cannot corrupt/rollback ProfessionalProfile truth.
6. Non-public outcomes produce projection remove/hide/refresh behavior without deleting source truth.
7. Projection can be rebuilt from current source truth and current owner decisions.
8. All public-readiness/projection/contract tests pass.

### Exit Gate

Before Feature 04 begins:

- PE-U08 field allowlist is approved for the enabled public surface;
- SH-024 and SH-094 are contract-tested;
- no direct Search repository/provider dependency exists;
- lifecycle/profile public changes produce reliable SH-091 requests;
- sensitive field leakage tests pass;
- Search outage/replay tests pass;
- root quality checks pass.

---

## 04 — Marketplace, Gig, and Order Professional Gate Integration

### Objective

Prove that Marketplace Supply, Gig / Demand, and Transaction / Order can consume SH-016 for their seller actions using owner-supplied target context, while Professional Eligibility neither reads their tables directly nor performs their lifecycle mutations.

### Observable Result

- Marketplace can ask for `publish_offering` readiness using an authoritative Offering context and receive a Professional Eligibility decision;
- Gig can ask for `respond_to_gig` readiness using authoritative Gig requirement context;
- Order can ask for `participate_in_order` readiness using authoritative seller/transaction context;
- stale/invalid target context is rejected;
- an SH-016 allow never itself writes Offering, GigResponse, or Order state;
- U-01-sensitive publication/respond paths remain production-disabled until their financial timing is approved.

### Cluster Build-Plan Link

Supports:

- **CL-03 Feature 08 — Offering Publication and Public Professional Supply**, Professional Eligibility side only;
- **CL-03 Feature 11 — Readiness Change Propagation and Neighboring-Cluster Integration**, synchronous contract proof for Marketplace/Gig/Order.

### Dependencies

- Features 02–03 exit gates;
- Marketplace owner context/publication contract;
- Gig owner response-context contract;
- Order owner seller-participation context contract;
- SH-003 owner-fact pattern if approved, otherwise explicit owner-specific context queries;
- SH-016;
- PE-U01 financial timing for publish/respond and any Order participation dimension;
- dependency source version/target validation semantics.

### In Scope

- target-context request schemas for the three ProfessionalActions;
- narrow dependency adapters/ports owned by Professional Eligibility but implemented against source-owner public contracts;
- source version and ownership validation;
- anti-confused-deputy checks;
- SH-016 composition using supplied current target facts;
- contract tests with each consumer/owner;
- negative tests proving no direct foreign writes/repositories;
- documentation of what consumer still must validate/mutate locally.

### Out of Scope

- Marketplace Offering publication/status implementation;
- GigResponse creation/assignment;
- Order lifecycle/payment/agreement/refund implementation;
- Payment provider execution;
- Search Offering projection;
- digital delivery/media/booking;
- resolving consumer Module internal invariants;
- adding a generic cross-domain target repository.

### Module-Owned Data

No new persisted data.

ProfessionalProfile may be read during each decision. Target context is ephemeral source-owner input/reference and must not be persisted as a new Professional Eligibility aggregate.

### Public Interfaces

SH-016 now supports production contract variants for:

- `publish_offering`;
- `respond_to_gig`;
- `participate_in_order`.

Each action context must include or resolve:

- target ID/type;
- ProfessionalProfile ID expected by the target owner;
- source version/currentness token;
- canonical taxonomy/regulated requirement references needed for the gate;
- only the target-owner facts necessary for Professional Eligibility.

Do not expose internal owner DTOs as a universal `TargetContext` bag with arbitrary JSON.

### Shared Operations Used

#### SH-003 `queryOwnerFacts` — Proposed

- **Owner:** source-owner shared pattern.
- **Invocation:** only if approved and implemented by the relevant owner.
- **Local policy:** exact minimum target facts requested.
- **Prohibited duplicate:** generic Prisma cross-domain resolver.

If SH-003 remains Proposed, use explicit Marketplace/Gig/Order public queries with the same narrowness principle.

#### SH-016

- **Owner:** Professional Eligibility.
- **Invocation:** consumer pre-mutation gate.
- **Local policy:** seller action composition.
- **Prohibited duplicate:** consumer-local seller readiness engine.

#### SH-005/011/017/018/019/020/022

Consumed inside SH-016 according to Feature 02's approved action policy. Consumer Modules do not call and recombine them merely to imitate Professional Eligibility.

### Domain Logic

#### `publish_offering`

Professional Eligibility answers only seller readiness. Marketplace remains responsible for:

- Offering ownership;
- Offering current status/version;
- shape/pricing/classification/media/delivery local validity;
- publication transition;
- Offering Search projection.

If PE-U01 is unresolved for publication, Professional Eligibility returns policy-unresolved/non-allow.

#### `respond_to_gig`

Gig supplies authoritative target requirements/context. Professional Eligibility answers whether the seller identity meets current professional gates. Gig remains responsible for:

- Gig openness/status;
- response limits/duplicate response rules;
- response creation;
- assignment lifecycle.

#### `participate_in_order`

Order supplies authoritative seller/transaction context. Professional Eligibility answers current seller operational eligibility only. Order owns transaction state and historical snapshots; Payment owns financial rails.

#### Stale context

A decision is not valid against a different target version. Consumer must provide the source version expected by its mutation. Professional Eligibility must not fetch a stale cached target and silently authorize a newer object.

### Authorization / Compliance

- consumer/system caller must be authorized to ask about the target;
- ProfessionalProfile must match target owner/seller relationship supplied by the source owner;
- private Gig/Order facts are not echoed into generic reason responses;
- financial/healthcare/verification evidence remains normalized and minimized;
- allow decision never replaces consumer's own authorization or local compliance checks.

### Database / Transaction Behavior

Professional Eligibility performs no foreign write.

Typical synchronous contract:

```text
consumer validates its target/current version
→ consumer calls SH-016 with owner-issued target context/version
→ Professional Eligibility resolves current professional/dependency facts
→ returns decision + source versions/evidence refs
→ consumer re-checks its target version and local invariants
→ consumer performs its own transaction if allowed
```

No distributed transaction is introduced. If the consuming lifecycle needs historical proof of the external decision, the **consumer owner** uses the root-approved snapshot mechanism (for example SH-109) according to its architecture.

### Events / Jobs

No new Module worker required. Consumer lifecycle events remain consumer-owned.

A successful foreign mutation may later produce events that affect Professional Eligibility, but this feature does not subscribe to them unless required by Feature 05.

### Provider Integration

None.

### UI / Admin Surface

No Professional Eligibility-owned UI required.

Consumer UI may display SH-016 safe blockers. Professional Eligibility must not dictate Marketplace/Gig/Order interface layout.

### Failure Behavior

- target not found/not controlled by profile: deterministic deny/invalid target;
- target context stale: conflict/unavailable requiring consumer refresh;
- required owner interface unavailable: non-allow/retryable;
- PE-U01 unresolved: policy-unresolved non-allow;
- caller unauthorized: forbidden without target/sensitive evidence leak;
- SH-016 allow but consumer local state changes before mutation: consumer rejects on its own version/transition check;
- dependency deny after a prior allow: next action reevaluates current state; no cached allow is authoritative.

### Tests

- Marketplace contract test: SH-016 called with approved Offering context, no Offering direct read/write;
- Gig contract test: canonical Gig requirement context, no GigResponse write;
- Order contract test: seller context, no Order write;
- stale target version tests for all three;
- wrong ProfessionalProfile/target ownership tests;
- U-01 unresolved tests for publish/respond;
- regression: consumer cannot pass `verified=true`, `stripeReady=true`, or similar shortcut to bypass owner checks;
- static/dependency test: no imports from foreign repository/infrastructure packages;
- E2E contract slice where available: blocked → source owner remediates → SH-016 allow → consumer performs its own mutation.

### Documentation Updates

For each real owner contract integrated:

- record exact public query/DTO name in Module architecture Section 13;
- update dependency Module public-interface documentation if jointly agreed;
- resolve/document PE-U01 for any production-enabled action;
- update progress tracker.

### Acceptance Criteria

1. Marketplace/Gig/Order can gate their seller action through SH-016 without direct ProfessionalProfile DB access beyond approved owner contract.
2. Professional Eligibility consumes target context without taking target lifecycle ownership.
3. No foreign source table is mutated by this Module.
4. Stale/invalid target contexts fail safely.
5. Consumers cannot bypass gates by supplying local booleans.
6. Production-enabled publish/respond paths have an explicit financial-timing ruling.
7. Contract and negative-coupling tests pass.

### Exit Gate

Before Feature 05 begins:

- all enabled consumer actions have contract-tested source-owner context;
- no direct foreign repositories exist in the implementation dependency graph;
- U-01-dependent production paths are either explicitly resolved or disabled;
- consumer action owner remains sole lifecycle writer in integration tests;
- source version/stale context tests pass;
- root quality checks pass.

---

# Phase 4 — Module Integration and Readiness Change Propagation

## 05 — Dependency-Change Reevaluation and Downstream Effects

### Objective

Make Professional Eligibility react safely and idempotently when source-owner facts change, reevaluate affected professional/public actions from current truth, and request only the downstream effects it owns without creating a readiness database or automatic cross-domain mutations.

### Observable Result

- relevant Trust, Healthcare, Track Entitlement, ComplianceHold, Taxonomy, and approved Payment changes can trigger ProfessionalProfile readiness/public-readiness reevaluation;
- duplicate/out-of-order source events do not duplicate effects;
- affected public ProfessionalProfiles can request Search reindex/deindex through SH-091;
- approved notifications may be requested through SH-041;
- dependency outage results in retry/dead-letter visibility rather than false allow;
- no automatic ProfessionalProfile status change occurs from dependency loss unless PE-U04 is explicitly resolved to require one.

### Cluster Build-Plan Link

This is the Professional Eligibility implementation of **CL-03 Feature 11 — Readiness Change Propagation and Neighboring-Cluster Integration**.

### Dependencies

- Features 02–04 exit gates;
- versioned source-domain events from each dependency actually wired;
- SH-045 event dedupe;
- SH-047 reliable job;
- SH-048 retry/backoff;
- SH-038 queue telemetry;
- SH-037 operational failure recording;
- SH-091 Search refresh;
- SH-041 Notification if trigger approved;
- PE-U04 automatic lifecycle-consequence policy;
- PE-U11 notification policy.

### In Scope

- event-to-affected-professional resolver for supported source event families;
- event inbox/dedupe integration;
- durable reevaluation job payload;
- current-state SH-016/024 reevaluation;
- Search refresh/remove/restore request based on current public readiness;
- optional safe notification request for explicitly approved triggers;
- retry/permanent-failure classification;
- dead-letter/ops visibility;
- replay/out-of-order/current-state tests;
- source version/correlation propagation.

### Out of Scope

- creating `ProfessionalReadiness` persistence;
- changing Trust/Healthcare/Payment/Track/Hold/Taxonomy truth;
- writing Search state;
- automatic Offering/Gig/Order mutations;
- automatic ProfessionalProfile pause/suspend solely because a dependency event arrived unless PE-U04 is approved;
- generic event bus/queue infrastructure;
- provider webhooks.

### Module-Owned Data

Ordinarily no ProfessionalProfile source write is required.

The worker reads:

- current `ProfessionalProfile`;
- current source-owner decisions through public contracts.

It produces:

- derived current readiness/public-readiness;
- downstream Search/Notification requests.

No local event inbox/job table is Module truth; those are shared platform/Observability mechanics.

### Public Interfaces

Internal/worker contracts:

- `handleProfessionalReadinessDependencyEvent`;
- `reevaluateProfessionalPublicReadiness`;
- affected-profile resolver per supported source event contract.

No new consumer-facing seller decision API is introduced; SH-016 and SH-024 remain authoritative.

### Shared Operations Used

#### SH-045 `deduplicateDomainEvent`

- **Owner:** platform event inbox.
- **Invocation:** before event-driven side effects.
- **Local policy:** handler/version identity.
- **Prohibited duplicate:** `processedEvent` flag on ProfessionalProfile.

#### SH-047 `enqueueReliableJob`

- **Owner:** shared queue.
- **Invocation:** source event creates reevaluation work when not safe/small enough synchronously.
- **Local policy:** payload and completion semantics.
- **Prohibited duplicate:** local queue table/runner.

#### SH-048 `executeRetryWithBackoff`

- **Owner:** shared queue/platform.
- **Invocation:** transient owner/Search/Notification failure.
- **Local policy:** retryable versus permanent classification.
- **Prohibited duplicate:** custom infinite retry loop.

#### SH-038 / SH-037

- **Owner:** Observability / Ops.
- **Invocation:** worker attempts/failures/dead letters.
- **Local policy:** safe operation/result context.
- **Prohibited duplicate:** operational records as readiness truth.

#### SH-016 / SH-024

- **Owner:** Professional Eligibility.
- **Invocation:** compute current state after event.
- **Local policy:** unchanged from Features 02/03.
- **Prohibited duplicate:** event-specific eligibility logic.

#### SH-091

- **Owner:** Search.
- **Invocation:** public readiness/source projection may have changed.
- **Local policy:** reason/source version.
- **Prohibited duplicate:** direct Search write.

#### SH-041

- **Owner:** Notification.
- **Invocation:** only approved user/admin notification trigger.
- **Local policy:** safe template variables.
- **Prohibited duplicate:** direct messaging provider.

### Domain Logic

1. Validate event envelope/version/source.
2. Deduplicate by event ID + handler version.
3. Resolve affected ProfessionalProfile ID using source-owner event facts/public lookup; never generic cross-domain Prisma.
4. Load current ProfessionalProfile.
5. Re-evaluate only actions/public surface potentially affected by that source change.
6. Current owner truth wins over event order; event payload is a trigger/correlation input, not necessarily the latest business state.
7. If current public readiness may differ, request Search refresh idempotently. It is acceptable to refresh when the document is unchanged.
8. Request notification only if a product policy trigger is explicitly approved and safe.
9. Do not persist a readiness result solely to detect changes.
10. Do not auto-transition ProfessionalProfile unless PE-U04 is resolved and the transition itself uses the normal lifecycle command policy.

### Authorization / Compliance

- workers run under constrained system capability;
- event payload must not grant authority to mutate profile state;
- source-owner event IDs/versions are validated;
- sensitive dependency details are not logged or forwarded;
- Search/Notification receives only safe source/decision metadata;
- event replay cannot reopen or resuspend a profile via stale state.

### Database / Transaction Behavior

- SH-045 inbox claim and any local side effect that must be exactly-once should use root-approved transaction semantics;
- there is no ProfessionalProfile write in the default reevaluation path;
- Search/Notification requests use reliable async/idempotency keys based on source event + profile + effect type/handler version;
- if PE-U04 later adds lifecycle transition, it must call the ordinary owner command with expected current state rather than update directly from the event handler.

### Events / Jobs

Worker: `professional-readiness-reevaluation`.

Suggested durable payload fields:

- source event ID/type/version;
- source Module;
- ProfessionalProfile ID or typed target reference;
- handler version;
- correlation ID;
- emittedAt/receivedAt.

Retryable:

- dependency query timeout;
- Search request outage;
- Notification request outage;
- transient DB/network error.

Permanent:

- unsupported event version;
- invalid target reference;
- malformed required source contract.

Dead-letter after root-configured retry exhaustion; operator tooling belongs to Ops.

### Provider Integration

None. Provider-owning Modules must translate provider callbacks into canonical source state/events before this worker sees them.

### UI / Admin Surface

No business UI required.

Ops may surface queue/dead-letter metadata through the shared Ops surface. Do not create a Professional Eligibility raw event viewer containing sensitive source payloads.

### Failure Behavior

- duplicate event: return replay/already-processed result with no duplicate effects;
- out-of-order event: read current source truth; do not roll back to event payload state;
- dependency unavailable: retry; no allow/visibility assumption;
- Search unavailable: retry Search request; no profile source mutation;
- Notification unavailable: retry/record failure; no profile source rollback;
- unresolvable target: permanent failure/ops evidence according to contract;
- retry exhaustion: dead-letter visible; do not write a fake “readiness failed” lifecycle state.

### Tests

- contract tests for each supported source event family;
- duplicate event replay;
- out-of-order event with newer current source state;
- current-state reevaluation rather than payload-state assumption;
- dependency timeout/retry/dead-letter;
- Search refresh idempotency;
- Notification duplicate suppression through its request/idempotency contract;
- regression: no readiness table created;
- regression: no automatic lifecycle mutation when PE-U04 unresolved;
- telemetry redaction tests;
- correlation propagation tests.

### Documentation Updates

When wiring a new source event:

- record exact event family/version in dependency interface docs;
- update Module architecture Section 22 only if worker behavior changes materially;
- resolve PE-U04 before enabling any automatic profile transition;
- resolve PE-U11 before enabling a new notification trigger;
- update progress tracker and integration matrix.

### Acceptance Criteria

1. Every wired dependency event is deduplicated.
2. Current source truth wins over event delivery order.
3. Search refresh is requested through SH-091 only.
4. No readiness source table/cache is introduced.
5. No automatic status transition occurs without explicit lifecycle policy.
6. Dependency/Search/Notification transient failures are retryable and operationally visible.
7. Retry exhaustion is dead-letter visible without corrupting business truth.
8. Replay/out-of-order/telemetry tests pass.

### Exit Gate

Before Feature 06 begins:

- event inbox + worker replay tests pass;
- supported dependency event contracts are versioned/documented;
- no provider/raw source payload enters the worker contract;
- Search refresh path is retry-safe;
- PE-U04 remains enforced as disabled unless explicitly resolved;
- queue/dead-letter telemetry is visible through shared Ops;
- root quality checks pass.

---

# Phase 5 — Governance, Moderation, Audit, and Privacy

## 06 — Moderation / Hold Enforcement and Audit Integration

### Objective

Implement the owner-side ProfessionalProfile consequence of validated moderation/hold decisions and complete high-impact lifecycle audit behavior without creating local moderation, hold, or audit truth.

### Observable Result

- an approved moderation decision targeting a ProfessionalProfile can be executed idempotently through the Professional Eligibility boundary;
- unauthorized/stale/revoked source decisions cannot change profile state;
- a suspension/reinstatement transition, when approved by PE-U03, records source-decision provenance and emits the normal profile lifecycle event;
- public Search refresh/removal follows the committed profile effect;
- generic high-impact audit evidence is appended through SH-029;
- a ComplianceHold is evaluated through SH-011 and never copied into a local blocked flag.

### Cluster Build-Plan Link

Professional Eligibility portion of **CL-03 Feature 12 — Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion**.

Privacy execution itself is separated into Module Feature 07.

### Dependencies

- Features 01–05 exit gates;
- SH-103 Moderation target execution;
- SH-011 current hold evaluation;
- SH-029 Audit;
- SH-091 Search refresh;
- SH-041 Notification only for approved suspension/reinstatement messages;
- approved suspension/reinstatement/archival transition table under PE-U03;
- PE-U12 manual override policy remains prohibited unless resolved.

### In Scope

- `executeProfessionalModerationDecision` public command;
- validation of moderation decision ID/version/target/effect;
- source-decision-to-profile-transition mapping;
- owner-side suspension/provenance update where approved;
- reinstatement only under an approved source-cleared policy;
- hold-sensitive lifecycle/readiness checks through SH-011;
- SH-029 audit evidence for high-impact lifecycle actions;
- Search refresh after public lifecycle consequence;
- safe Notification request if approved;
- idempotency/concurrency tests for source decisions.

### Out of Scope

- Report/LegalNotice/ModerationCase/ModerationAction lifecycle;
- creating/releasing `ComplianceHold` unless a separate source-owner workflow explicitly instructs it;
- generic admin “block seller” flag;
- manual `forceAllow`, `forceActive`, or `forceVerified` override;
- raw moderation evidence viewer;
- Search provider execution;
- Privacy request handling;
- provider webhooks.

### Module-Owned Data

Potential writes:

- `ProfessionalProfile.status`;
- `suspendedForModerationAt` as local provenance timestamp only when an approved moderation-triggered suspension occurs;
- normal `updatedAt`.

No local moderation/hold/audit table is introduced.

### Public Interfaces

Introduce/complete:

- `executeProfessionalModerationDecision`;
- `reinstateProfessionalProfile` only after exact source-clearance and target-state rules are approved;
- safe lifecycle status query remains `getProfessionalProfileContext`.

Moderation uses a typed target-execution contract, not direct repository access.

### Shared Operations Used

#### SH-103 `executeModerationDecision`

- **Owner:** Moderation decision; target owner executes.
- **Invocation:** before any moderation-driven ProfessionalProfile transition.
- **Local policy:** supported effect → ProfessionalProfile transition.
- **Prohibited duplicate:** Professional Eligibility moderation case/decision workflow.

#### SH-011 `evaluateComplianceHold`

- **Owner:** Hold.
- **Invocation:** lifecycle/readiness action when hold-sensitive.
- **Local policy:** consequence for requested ProfessionalProfile action.
- **Prohibited duplicate:** `blocked` flag/local hold table.

#### SH-029 `appendAuditEvent`

- **Owner:** Audit / Event Ledger.
- **Invocation:** suspension, reinstatement, archive, privileged transition.
- **Local policy:** safe actor/target/outcome/source decision metadata.
- **Prohibited duplicate:** local generic audit log.

#### SH-044 / 051 / 052 / 053 / 046

- **Owner:** shared platform mechanisms.
- **Invocation:** source-decision command transaction.
- **Local policy:** idempotency fingerprint, expected state, transition mapping, event payload.
- **Prohibited duplicate:** process locks, status writes outside owner command, best-effort events.

#### SH-091 / SH-041

- **Owner:** Search / Notification.
- **Invocation:** after committed lifecycle consequence.
- **Local policy:** projection reason and safe user-message trigger.
- **Prohibited duplicate:** direct provider calls.

### Domain Logic

- source moderation decision must identify the ProfessionalProfile target and requested approved effect;
- Professional Eligibility validates that the effect is supported and the decision is current;
- the source decision is evidence/provenance, not Professional Eligibility-owned moderation truth;
- suspension must not be represented as a copied local hold when an active hold exists;
- hold state may block actions without necessarily forcing `status=suspended` unless PE-U04/transition policy says so;
- reinstatement does not automatically mean `active`; exact target state and whether readiness must be rechecked are PE-U03 concerns;
- if reinstatement target is active, Feature 02 SH-016 must allow current required action;
- stale resume/reinstate cannot overwrite a newer moderation suspension.

### Authorization / Compliance

- caller/system context must be authorized to execute the source decision;
- ordinary profile owner cannot clear platform suspension without an approved source-release path;
- support/admin role alone is insufficient to invent source decision or override hold;
- audit metadata must not include private moderation evidence;
- public/readiness reason codes use safe categories, not legal case detail.

### Database / Transaction Behavior

```text
validate source decision contract
→ SH-044 idempotency claim
→ acquire/CAS ProfessionalProfile current state
→ verify expected source decision/version + target
→ map to approved local transition
→ write profile status/provenance
→ append owner outbox event
→ commit
→ request Audit/Search/Notification through reliable owner interfaces
```

If audit or Search delivery fails after the profile commit, retry the downstream effect. Do not silently revert the source lifecycle transition unless the source decision itself is reversed through a new approved command.

### Events / Jobs

Events:

- standard ProfessionalProfile status-changed event with source decision reference.

No separate `ProfessionalModerationEvent` source truth is required.

Search/Notification effects may be outbox-driven jobs.

### Provider Integration

None.

### UI / Admin Surface

No new universal moderation UI.

Existing Moderation/Admin tooling may invoke the Professional Eligibility target command and display only:

- target profile ID/status;
- execution result;
- safe source decision reference;
- conflict/remediation state.

Raw moderation evidence remains with Moderation.

### Failure Behavior

- invalid/unknown source decision: reject, no profile mutation;
- decision target mismatch: reject and audit/ops as appropriate;
- decision revoked/stale: conflict/review;
- unsupported effect/transition: `POLICY_UNRESOLVED`/validation denial;
- duplicate decision execution: replay canonical result;
- concurrent owner resume versus suspension: DB conflict/lock ensures one valid ordering; stale command loses;
- hold still active during attempted reinstatement: deny under approved policy;
- Search/Notification/Audit transient outage: retry downstream; source profile remains committed;
- audit payload validation failure: do not leak unsafe metadata; record operational failure and retry safe audit request according to root policy.

### Tests

- SH-103 source decision contract;
- authorized/unauthorized system/admin execution;
- duplicate moderation decision idempotency;
- stale/revoked/wrong-target decision;
- suspend versus resume concurrency;
- reinstatement source-clearance and current-readiness checks where enabled;
- ComplianceHold evaluation without local flag;
- audit metadata minimization;
- Search refresh/removal after suspension;
- notification safe payload if enabled;
- regression: no ModerationCase/ComplianceHold/AuditEvent repository in this Module.

### Documentation Updates

If Feature 06 settles PE-U03 suspension/reinstatement or PE-U04 hold/dependency-to-status mapping:

- update Module architecture lifecycle and unresolved table;
- update public moderation target contract;
- update CL-03 architecture only if the change alters Cluster collaboration;
- update progress tracker.

### Acceptance Criteria

1. Professional Eligibility is the only writer of profile suspension/reinstatement state.
2. Moderation remains source-decision owner.
3. Duplicate/stale source decisions cannot repeat or overwrite lifecycle effects.
4. Holds are consumed through SH-011, not copied.
5. High-impact lifecycle actions request SH-029 audit with safe metadata.
6. Search/Notification effects use owner interfaces and do not control source truth.
7. No generic override path exists.
8. All authorization/idempotency/concurrency/audit tests pass.

### Exit Gate

Before Feature 07 begins:

- enabled suspension/reinstatement transitions have explicit approved adjacency/source rules;
- SH-103 integration tests pass;
- no local moderation/hold/audit source schema exists;
- stale/duplicate/concurrent decision tests pass;
- audit payload redaction tests pass;
- Search projection consequence is retry-safe;
- root quality checks pass.

---

## 07 — ProfessionalProfile Privacy Executor and Retention Handoff

### Objective

Implement Professional Eligibility's owner-side contribution to privacy access/export/erase/anonymize/restrict workflows while leaving Privacy / Data Erasure in control of request lifecycle, legal retention, orchestration, and cross-service completion.

### Observable Result

- Privacy can enumerate all Professional Eligibility-owned subject data;
- Privacy can dispatch a typed instruction against a ProfessionalProfile;
- the Module can deterministically anonymize/retain permitted owned fields under an approved disposition;
- legally or structurally retained profile linkage is preserved when required;
- unresolved destructive retention returns an explicit blocked/review result rather than hard-deleting;
- Search removal/refresh is requested after source privacy changes;
- replay does not repeat destructive effects.

### Cluster Build-Plan Link

Professional Eligibility privacy portion of **CL-03 Feature 12 — Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion**.

### Dependencies

- Feature 06 exit gate;
- SH-095 `executePrivacyInstruction`;
- SH-096 `enumerateSubjectData`;
- SH-097 `evaluateRetentionRequirement`;
- SH-098 `anonymizePersonalFields` where approved;
- Privacy owner contracts and retention decisions;
- SH-091 Search refresh/removal;
- SH-044 idempotency;
- PE-U09 exact retention/anonymization map.

### In Scope

- ProfessionalProfile subject-data inventory;
- safe export contribution for owned fields;
- target validation;
- typed field disposition plan;
- anonymization of approved profile personal fields;
- preserve/retain result when legal/commercial relationships require it;
- Search projection removal/refresh request after privacy source effect;
- idempotent replay and partial-failure handling;
- privacy tests proving no foreign record deletion.

### Out of Scope

- `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, export bundle lifecycle;
- deciding legal retention period by guess;
- deleting/anonymizing Orders, Offerings, Gigs, Reviews, Trust, Healthcare, Payment, Media, Audit, Search records directly;
- provider deletion (none owned here);
- treating profile archive as privacy completion;
- changing User authentication identity directly.

### Module-Owned Data

Target:

- `ProfessionalProfile` row and owner-controlled personal/profile fields.

Inventory must classify:

- direct personal profile fields;
- lifecycle/structural identifiers;
- derived/compatibility fields physically present;
- foreign relationship references that Privacy needs to route to other owners;
- Search projection target reference.

No privacy orchestration table is added.

### Public Interfaces

Implement/complete:

- SH-096 Professional Eligibility data enumeration;
- SH-097 Professional Eligibility retention-fact contribution;
- SH-095 target execution result;
- optional safe export DTO used by Privacy.

The execution result must clearly distinguish:

- erased/anonymized;
- retained under supplied/recorded exemption;
- no-op/already applied;
- blocked pending retention decision;
- failed/retryable.

### Shared Operations Used

#### SH-096 `enumerateSubjectData`

- **Owner:** each data owner under Privacy protocol.
- **Invocation:** privacy discovery/export/erasure planning.
- **Local policy:** which ProfessionalProfile fields/record IDs are owned here.
- **Prohibited duplicate:** generic cross-domain subject repository.

#### SH-097 `evaluateRetentionRequirement`

- **Owner:** owner supplies facts; Privacy owns exemption/decision record.
- **Invocation:** before destructive execution.
- **Local policy:** ProfessionalProfile relationships/field business meaning.
- **Prohibited duplicate:** local retention-exemption lifecycle.

#### SH-095 `executePrivacyInstruction`

- **Owner:** Privacy orchestrates; Professional Eligibility executes owner data.
- **Invocation:** typed privacy target dispatch.
- **Local policy:** field-level disposition and owner transaction.
- **Prohibited duplicate:** `professionalPrivacyRequest` workflow.

#### SH-098 `anonymizePersonalFields`

- **Owner:** shared anonymization primitive with owner mapping.
- **Invocation:** approved anonymize instruction.
- **Local policy:** which ProfessionalProfile fields receive which deterministic-safe treatment.
- **Prohibited duplicate:** one global generic eraser controlling all domains.

#### SH-044 / SH-091

- **Owner:** platform idempotency / Search.
- **Invocation:** replay-safe target execution and projection removal.
- **Local policy:** privacy target fingerprint and Search reason/source version.
- **Prohibited duplicate:** local privacy dedupe table, direct Search write.

### Domain Logic

- verify target ProfessionalProfile belongs to the privacy subject/instruction;
- enumerate only this Module's data but expose foreign owner references for orchestration routing where contract permits;
- do not treat `onDelete: Cascade` as the privacy workflow;
- if retained Orders/financial/compliance records require profile identity linkage, preserve the minimal structural record/ID per Privacy's approved disposition;
- anonymize approved profile copy/location fields deterministically;
- derived rating/compatibility fields follow explicit field disposition, not convenience;
- archive status alone is not erasure proof;
- after public personal data is anonymized/removed, request Search removal/refresh;
- if PE-U09 retention is not settled for a destructive path, return blocked/review and perform no destructive guess.

### Authorization / Compliance

- only Privacy's approved system/worker capability may execute the target instruction;
- ordinary owner/admin route cannot call privacy executor as a shortcut to delete retained business records;
- Privacy provides or references retention decision/exemption context;
- audit proof of privacy action uses global Privacy/Audit policy and must not reveal erased data;
- this Module does not decide legal retention independently.

### Database / Transaction Behavior

```text
validate privacy instruction + target ownership
→ SH-044 idempotency claim
→ obtain/validate retention decision context
→ transaction
   → lock/CAS ProfessionalProfile
   → apply only approved owner-field disposition
   → append source event/outbox if public/source facts materially change
→ commit
→ request Search removal/refresh
→ return deterministic execution result to Privacy
```

Do not delete foreign rows in the transaction.

If Search request fails after source anonymization, retry Search independently; do not restore personal data solely because projection cleanup is delayed.

### Events / Jobs

- privacy orchestration job is Privacy-owned;
- this Module may emit a minimized profile-updated/status event only if the approved source event contract requires consumers to react;
- Search projection cleanup request is reliable/idempotent;
- no Module-owned scheduled privacy worker.

### Provider Integration

None. Any provider resource references encountered belong to their actual owner and must be returned/routed to Privacy rather than deleted here.

### UI / Admin Surface

None required. Privacy/admin UI belongs to the Privacy orchestration surface.

Support tools may display only target execution disposition/status, not the erased profile payload.

### Failure Behavior

- target mismatch: deterministic reject;
- retention decision missing/unresolved: blocked/review, no destructive write;
- referenced retained relationship prevents hard delete: return retention-required rather than force cascade;
- duplicate instruction: canonical no-op/replay result;
- DB failure before commit: rollback;
- Search outage after commit: retry projection cleanup;
- partial cross-service privacy failure: report only this Module's target result; Privacy owns global job state/retry.

### Tests

- complete owned-field inventory snapshot test;
- privacy subject/target ownership validation;
- anonymization mapping fixtures;
- retention-required no-delete path;
- replay/idempotency;
- transaction rollback on failure;
- no foreign repository/delete imports;
- archive ≠ erasure regression;
- Search removal/refresh after approved privacy effect;
- sensitive telemetry/log redaction;
- export contribution contains only owner data and approved identifiers.

### Documentation Updates

If PE-U09 is resolved:

- update Module architecture Section 28 with exact field disposition/retention rules;
- update Privacy integration contract;
- document any schema migration required to support legal retention/anonymization;
- update progress tracker.

A new `erasedAt`/tombstone/version field must not be added without root/Privacy architecture approval.

### Acceptance Criteria

1. Privacy can enumerate Professional Eligibility-owned subject data without scanning foreign tables through this Module.
2. Destructive actions are retention-gated.
3. Approved anonymization touches only Professional Eligibility-owned fields.
4. No foreign source record is deleted/rewritten.
5. Archive is not reported as privacy erasure.
6. Search projection cleanup is requested reliably after source privacy effects.
7. Replay is deterministic and safe.
8. Privacy/integration/redaction tests pass.

### Exit Gate

Before Feature 08 begins:

- SH-095/096/097 contract tests pass;
- every enabled destructive/anonymization field has an approved disposition;
- unresolved retention paths are explicitly blocked;
- no foreign delete/mutation exists;
- Search cleanup replay/outage tests pass;
- privacy inventory/export tests pass;
- root quality checks pass.

---

# Phase 6 — Module Hardening and Production Verification

## 08 — Professional Eligibility Security, Concurrency, Replay, Migration, and Contract Hardening

### Objective

Prove the complete Professional Eligibility implementation remains correct under concurrency, retries, dependency outages, stale events, privacy/moderation interactions, Search failure, schema/backfill changes, and hostile input; then freeze the production public contracts and disabled unresolved paths.

### Observable Result

- all Module features remain deterministic under retries/races/outages;
- no gate path depends on compatibility booleans or foreign direct reads;
- public contracts have stable versions/reason-code semantics;
- operators can diagnose dependency/queue/Search failures through shared Ops without raw sensitive data;
- migrations/backfills are dry-run/recoverable where needed;
- unresolved action/lifecycle/privacy policies are explicitly disabled/configured, not accidentally reachable;
- production readiness report lists every passed exit gate and remaining production blocker.

### Cluster Build-Plan Link

Professional Eligibility portion of **CL-03 Feature 13 — CL-03 Security, Reliability, Reconciliation, Backfill, Compliance, and Production Hardening**.

### Dependencies

- Features 01–07 complete;
- root security/deployment/observability standards;
- current CL-03 and Module unresolved-decision registers reviewed;
- real dependency public interfaces for all production-enabled ProfessionalActions;
- shared idempotency/event/job/concurrency/Search/Privacy/Audit/Ops mechanisms live in the production stack.

### In Scope

- adversarial review of every public command/query/worker;
- concurrency/race test matrix;
- idempotency/replay/out-of-order event test matrix;
- dependency outage/fail-safe behavior;
- reason-code/field-level information leakage review;
- compatibility-field read/write inventory and removal from gate paths;
- query/index/performance review for ProfessionalProfile paths;
- public contract freeze/versioning/deprecation policy;
- projection rebuild/backfill verification;
- privacy/moderation/hold interaction testing;
- telemetry redaction and correlation checks;
- migration/backfill safety for any approved schema changes;
- final production blocker classification for every unresolved decision;
- production readiness report/progress update.

### Out of Scope

- solving unrelated Trust/Healthcare/Payment provider architecture;
- creating new providers/product lanes during hardening;
- implementing unresolved legal/compliance policy merely to make tests green;
- broad root architecture redesign;
- Marketplace/Gig/Order internal feature work;
- removing compatibility fields destructively without migration approval;
- introducing a readiness snapshot source table.

### Module-Owned Data

Review/harden:

- `ProfessionalProfile` unique constraints/indexes;
- status/concurrency behavior;
- compatibility fields and any one-way deprecation/backfill strategy;
- source event/version metadata supported by root outbox;
- source projection versioning;
- privacy field disposition mappings.

No new source model should be added solely for observability, retries, Search, or readiness caching.

### Public Interfaces

Freeze/version:

- `createProfessionalProfile`;
- `updateProfessionalProfile`;
- `getProfessionalProfileContext`;
- enabled lifecycle commands;
- SH-016 ProfessionalAction request/decision;
- SH-024 public-readiness decision;
- SH-094 Professional source projection;
- SH-103 moderation target execution;
- SH-095/096/097 privacy executor contracts;
- ProfessionalProfile domain-event payloads.

Document:

- request/response versioning;
- stable reason codes;
- retry/idempotency semantics;
- expected-state/concurrency requirements;
- `POLICY_UNRESOLVED` behavior;
- deprecation handling for legacy fields/aliases;
- consumer responsibilities after an allow decision.

### Shared Operations Used

Hardening verifies correct use of, but does not reimplement:

- SH-001/002 authentication/authorization;
- SH-005/011/017/018/019/020/022 readiness inputs;
- SH-024 public readiness;
- SH-029/034/037/038 audit/telemetry/Ops;
- SH-041 Notification requests;
- SH-044/045/046 idempotency/inbox/outbox;
- SH-047/048 durable jobs/retry;
- SH-051/052/053 concurrency/lifecycle mechanics;
- SH-091/094 Search boundary;
- SH-095–098 Privacy execution;
- SH-103 Moderation target execution;
- SH-114 one-to-one provisioning.

**Prohibited:** any Professional Eligibility-wide replacement queue, webhook log, audit table, auth layer, Search client, privacy workflow, incident system, or readiness cache.

### Domain Logic

Perform adversarial review of:

1. one-to-one ProfessionalProfile provisioning;
2. slug/update concurrency;
3. every enabled lifecycle adjacency;
4. activation/resume freshness;
5. SH-016 action-to-gate completeness;
6. PE-U01 unresolved financial timing enforcement;
7. target-context staleness for Marketplace/Gig/Order;
8. dependency loss while a profile is active;
9. moderation/hold interaction and source provenance;
10. privacy anonymization versus retained commercial/compliance references;
11. public Search projection allowlist and deindex/reindex behavior;
12. duplicate/out-of-order dependency events;
13. notification/audit/Search outage after source commit;
14. consumer misuse of old allow decisions;
15. any code path reading compatibility fields;
16. any public contract accidentally serializing raw Prisma relations.

### Authorization / Compliance

Security review must prove:

- all protected boundaries invoke SH-001/002;
- system workers use constrained capabilities;
- no role-name-only admin bypass exists;
- readiness reason details are audience-aware;
- no raw sensitive source-owner payload is logged/evented/indexed/notified;
- financial/healthcare/verification presence cannot be enumerated by unauthorized callers;
- no `forceAllow`/`forceActive` override exists unless a new architecture ruling establishes it;
- Privacy destructive actions remain retention-gated;
- Moderation source decisions are validated before target effect.

### Database / Transaction Behavior

Review:

- uniqueness and index plans for `userId`, `slug`, status and key profile lookup paths;
- chosen SH-051/052 concurrency mechanism and stale-write behavior;
- transaction + outbox atomicity;
- idempotency key uniqueness/result retention according to root standards;
- safe migration of any approved version field or compatibility-field removal;
- backfill/rebuild plans that use ProfessionalProfile/source-owner truth, never Search as source;
- cascade/delete behavior under Privacy/legal retention.

Any destructive migration requires:

- data inventory;
- forward migration;
- dry-run/backfill plan;
- validation query/report;
- rollback or recoverability plan;
- explicit production gate.

### Events / Jobs

Harden:

- outbox replay;
- event consumer dedupe;
- out-of-order dependency events;
- reevaluation job lease/retry/dead-letter;
- Search request replay;
- correlation propagation;
- event schema version handling.

A stale/unknown event version must fail safely rather than be coerced into a current business transition.

### Provider Integration

None. Hardening must verify no provider package/secret/webhook route has leaked into this Module.

### UI / Admin Surface

If any existing profile/readiness/admin UI consumes this Module:

- verify it does not treat display state as authority;
- verify it handles deny/review/unavailable/conflict explicitly;
- verify it does not expose raw source-owner blocker details;
- verify stale client state cannot bypass server transition checks.

Do not build debugging screens that reveal raw Trust/Healthcare/Payment/Moderation data.

### Failure Behavior

Production behavior must be explicit for:

- Identity/Authority outage;
- entitlement/hold/taxonomy/Trust/Healthcare/Payment dependency outage;
- database timeout/deadlock;
- stale lifecycle command;
- duplicate idempotency key conflict;
- outbox publisher delay;
- event replay/out-of-order version;
- queue retry exhaustion/dead letter;
- Search outage;
- Notification outage;
- audit request failure;
- Privacy partial completion;
- moderation source decision reversal/staleness;
- projection schema mismatch;
- migration/backfill partial failure.

No failure path may default to `allow`, silently drop a required source effect, or mutate foreign truth as a repair shortcut.

### Tests

Final suite includes:

- all Features 01–07 tests;
- randomized/property-like transition and decision matrix tests where root tooling supports them;
- create/update/status race tests;
- moderation versus owner action races;
- idempotency replay with process restart semantics;
- duplicate/out-of-order dependency event tests;
- dependency timeout/circuit/degradation tests;
- reason-code information-leak tests;
- Search projection schema/redaction/backfill tests;
- privacy retention/anonymization/replay tests;
- static dependency/import checks preventing foreign repositories/provider clients;
- migration/backfill dry-run and validation tests for any schema change;
- performance tests for profile lookup and readiness fan-out at expected scale;
- E2E seller flow: create → blocked readiness → remediation → action allow → consumer-owned mutation → dependency loss → public refresh/deny → remediation/recovery;
- root-required typecheck, lint, unit, integration, contract, security/privacy, and build checks.

### Documentation Updates

Before production sign-off:

- update Module architecture decisions/unresolved table;
- update exact public contract/reason-code documentation;
- update dependency interface matrix;
- update migration/backfill/runbook docs if any;
- update CL-03 progress/build-plan status without changing architecture semantics;
- produce final production-readiness report;
- classify every PE-Uxx as **resolved**, **production blocker**, or **explicitly out of production scope**.

### Acceptance Criteria

1. Features 01–07 exit gates remain passing in the integrated build.
2. No production gate path reads compatibility booleans/projections as authority.
3. No direct foreign repository or provider client exists in Professional Eligibility.
4. Every critical mutation is idempotent and race-tested.
5. Every production-enabled action has an approved gate matrix and stable reason codes.
6. Required dependency failure cannot result in allow.
7. Search projection can be rebuilt/removed/restored from source truth through owner contracts.
8. Privacy execution and retention behavior are tested; unresolved destructive paths are disabled.
9. Moderation/hold target effects preserve source ownership and provenance.
10. Logs/events/audit/Search/Notification pass sensitive-data redaction tests.
11. Any migration/backfill has dry-run, validation, and recovery plan.
12. All unresolved decisions are explicitly dispositioned for production scope.
13. Root quality/test/build checks pass.

### Exit Gate

Professional Eligibility is production-ready only when:

- all eight Module feature exit gates pass;
- linked CL-03 milestones accept the Module public contracts;
- every production-enabled consumer uses SH-016 rather than rebuilding eligibility;
- no disabled unresolved path is reachable by normal route/worker/event input;
- concurrency/idempotency/replay/dependency-outage/privacy/Search tests pass;
- contract versions and reason-code catalog are frozen/documented;
- production readiness report and progress tracker are updated;
- no known architecture violation remains open.

---

# Module Integration Phase

**Phase 4 / Feature 05 is the explicit event-driven Module integration phase**, while Phase 3 / Feature 04 proves the synchronous consumer contracts.

Together they must prove Professional Eligibility collaborates correctly with its major neighbors without owning their records:

- **Track Subscription & Entitlement:** SH-005 source decision is consumed, never copied;
- **Taxonomy & Classification:** requirements are resolved through SH-022, never hardcoded;
- **Trust:** SH-017/018 drives verification dimension, TrustBadge does not become truth;
- **Healthcare:** SH-020 drives regulated-lane readiness, no local healthcare flag;
- **Payment:** SH-019 supplies financial dimensions, compatibility Stripe fields are ignored;
- **ComplianceHold:** SH-011 drives stop-sign decisions, no local block flag;
- **Marketplace:** SH-016 authorizes seller side of publication; Marketplace alone transitions Offering;
- **Gig / Demand:** SH-016 authorizes seller response; Gig alone creates/changes responses;
- **Transaction / Order:** SH-016 supplies current seller participation decision; Order remains transaction truth;
- **Search:** SH-024/094/091 provide public decision/source input/refresh request; Search owns projection execution;
- **Notification:** SH-041 receives safe intent only;
- **Moderation:** SH-103 source decision is executed only against local profile truth;
- **Privacy:** SH-095/096/097 orchestrates owner-side privacy execution;
- **Audit/Ops:** SH-029/034/037/038 record evidence/diagnostics, not business truth.

No integration is considered proven merely because a foreign Prisma relation can be queried. Contract/integration tests must exercise the public boundary and assert that the foreign owner's table is not written by Professional Eligibility.

---

# Module Hardening Phase

**Phase 6 / Feature 08 is the Module hardening phase.** It is intentionally limited to Professional Eligibility-relevant production concerns:

- one-to-one provisioning races;
- lifecycle transition races;
- action-to-gate completeness;
- stale target context;
- idempotency and replay;
- dependency outages;
- event ordering and dead letters;
- Search projection consistency/rebuild;
- moderation/hold provenance;
- privacy/retention correctness;
- compatibility-field deprecation safety;
- telemetry/reason-detail privacy;
- contract/version stability;
- migration/backfill safety;
- performance of ProfessionalProfile/readiness paths.

It must not become a pretext to redesign Trust, Payment, Healthcare, Search, Marketplace, Gig, Order, Privacy, or platform infrastructure.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | ProfessionalProfile Source-of-Truth Foundation | 01 Professional Profile Foundation |
| 2 | Professional Readiness Decisions | 02 Professional Readiness Composition Contract |
| 3 | Public Visibility and Consumer Contracts | 03 Professional Public Readiness and Search Source Projection; 04 Marketplace, Gig, and Order Professional Gate Integration |
| 4 | Module Integration and Readiness Change Propagation | 05 Dependency-Change Reevaluation and Downstream Effects |
| 5 | Governance, Moderation, Audit, and Privacy | 06 Moderation / Hold Enforcement and Audit Integration; 07 ProfessionalProfile Privacy Executor and Retention Handoff |
| 6 | Module Hardening and Production Verification | 08 Professional Eligibility Security, Concurrency, Replay, Migration, and Contract Hardening |

**Total numbered Module features: 8**

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture.
2. Read root code standards.
3. Read the Canonical Shared Operations Registry.
4. Read CL-03 architecture and build plan.
5. Read this Module architecture and implementation plan.
6. Read public-interface sections for every direct dependency touched by the feature.
7. Confirm the prior Module feature exit gate passed.
8. Confirm the linked CL-03 feature/milestone is at the correct point in Cluster sequencing.
9. Check PE-U01–PE-U13 and Cluster unresolved decisions for blockers.
10. Write a concise implementation specification for **only this numbered feature**.
11. List every owner record read/written and every SH operation used.
12. Implement only the feature and approved sub-slices.
13. Run root-required typecheck, lint, unit, integration, contract, migration, build, security/privacy, and other applicable checks.
14. Verify the primary workflow and negative/failure/concurrency paths.
15. Verify no foreign repository/provider/shared-operation duplicate was introduced.
16. Update progress.
17. Update architecture only when a binding decision legitimately changed.
18. Record assumptions, disabled paths, known failures, unresolved risks, and exit-gate result.

A feature is not complete because the happy path works. Its explicit failure, replay, authorization, ownership, and exit-gate conditions must also pass.

---

# Required Feature Implementation Specification

Immediately before coding any numbered feature, the coding agent must produce a concise feature-specific specification containing:

- **Feature:** number and name;
- **Cluster Build-Plan Link:** exact CL-03 feature/milestone supported;
- **Objective:** exact new capability;
- **Observable result:** what a user/admin/worker/consumer can verify;
- **Dependencies:** prior Module features, source-owner contracts, Shared Operations, schema/migrations, unresolved rulings;
- **In scope:** exact files/behavior/records for this feature;
- **Out of scope:** neighboring responsibilities explicitly excluded;
- **Owned data affected:** ProfessionalProfile fields/status/events/projections, if any;
- **Public contracts:** commands, queries, decisions, events, privacy/worker contracts introduced or changed;
- **Shared Operations consumed:** SH ID/name, owner, invocation point, local policy, prohibited duplicate;
- **Permissions / compliance:** actor, authority, ownership, entitlement, holds, verification, healthcare, financial, moderation/privacy constraints as applicable;
- **Primary workflow:** ordered behavior from entry to observable result;
- **Provider integration:** expected to be `none` for this Module; any exception requires architecture update;
- **Jobs / events:** outbox/inbox/job effects, retry/dead-letter/correlation rules;
- **Idempotency / concurrency:** semantic key, lock/CAS resource, stale/replay behavior;
- **Error behavior:** validation, authority, conflict, dependency unavailable, policy unresolved, partial completion;
- **Tests:** exact unit/integration/contract/authorization/concurrency/privacy/E2E categories required;
- **Acceptance criteria:** concrete pass conditions;
- **Documentation updates:** architecture/interfaces/progress/rulings affected.

Do **not** generate implementation specifications for all future features in advance. The feature specification should be written immediately before that feature is implemented so it can reflect the current repository, settled decisions, and prior exit gate.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed** — number/name and scope actually delivered;
- **Cluster build-plan link** — milestone supported;
- **Files added**;
- **Files changed**;
- **Database changes**;
- **Migrations** — added/applied/validated/none;
- **Dependencies added** — packages/services/contracts; explain why;
- **Module public interfaces added/changed**;
- **Shared Operations reused** — list SH IDs and confirm no duplicate was created;
- **Events/jobs added**;
- **Provider adapter changes** — normally `none`; any non-none result requires architecture review;
- **Tests added/changed**;
- **Commands run** — root-required typecheck/lint/test/build/migration/security commands;
- **Manual / contract verification**;
- **Documentation updated**;
- **Assumptions**;
- **Known failures**;
- **Remaining risks**;
- **Deferred work**;
- **Unresolved decisions encountered**;
- **Production-disabled paths**;
- **Exit-gate result** — pass/fail with evidence.

A completion report must explicitly call out any direct foreign table access, compatibility-field use, skipped canonical Shared Operation, disabled test, or changed ownership assumption. Such items are architecture exceptions, not routine implementation notes.

---

# Final Quality Check

Before treating this Module plan as executable context or marking Professional Eligibility complete, verify:

1. `ProfessionalProfile` has exactly one lifecycle owner: Professional Eligibility.
2. CandidateProfile lifecycle has not been absorbed because `ProfileStatus` is shared.
3. No Trust, Healthcare, Payment, Entitlement, Hold, Marketplace, Gig, Order, Search, Privacy, Moderation, Audit, Notification, Media, or provider truth was copied into this Module.
4. SH-016 is the stable professional action-readiness boundary.
5. Every enabled ProfessionalAction has an explicit gate matrix.
6. PE-U01 and other unresolved policies are not silently guessed.
7. `stripeReady`, `stripeAccountId`, verification summary fields, `trustScore`, rating projections, and TrustBadge cannot bypass owner decisions.
8. No `ProfessionalReadiness`, `canSell`, generic `blocked`, or equivalent source table/boolean was introduced.
9. Commands and lifecycle transitions have clear owner authorization, idempotency, expected-state, and transaction semantics.
10. Cross-Module reads use public owner contracts rather than direct foreign repositories by default.
11. No provider adapter/client/webhook exists in Professional Eligibility.
12. Search remains a projection and is invoked through SH-091/094/024.
13. Domain events, audit, and observability remain distinct.
14. Privacy orchestration remains Privacy-owned; Professional Eligibility implements only owner-side executor behavior.
15. Moderation/Hold remain source decision/stop-sign owners; target lifecycle consequence stays local.
16. Every numbered feature has tests, acceptance criteria, and an exit gate.
17. The Module integration phase proves contracts rather than shared-table convenience.
18. The hardening phase covers concurrency, replay, outages, privacy, redaction, migration/backfill, and contract stability without redesigning neighboring Modules.
19. Every production-disabled unresolved path is explicit and test-protected.
20. A coding agent can implement the next feature without inventing architecture.
