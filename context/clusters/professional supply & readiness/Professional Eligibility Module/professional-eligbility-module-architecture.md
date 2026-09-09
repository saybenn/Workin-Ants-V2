# Professional Eligibility Module Architecture

> **Module ID:** `professional_eligibility`  
> **Module name:** Professional Eligibility Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/professional_eligibility/module-architecture.md`

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `professional_eligibility` |
| Module name | Professional Eligibility Module |
| Module type | `compliance_domain_gate` |
| Build status | `mvp_active` |
| Primary Cluster | CL-03 — Professional Supply & Readiness |
| Document status | Implementation-grade Module architecture. **Confirmed** rulings are binding; **Proposed Rulings** require approval before dependent schema/API commitment; **Unresolved** items must not be invented in code. |
| Intended audience | Coding agents, developers, reviewers, maintainers, architecture reviewers, and test authors implementing or changing this Module. |
| Relationship to root architecture | Subordinate to root Workin Ants architecture, project overview, code standards, persistence, security, event, job, privacy, Search, audit, and observability decisions. Root decisions win when they conflict. |
| Relationship to Cluster architecture | Specializes CL-03 for the internal truth, policies, interfaces, and implementation boundaries of Professional Eligibility. It must not redefine CL-03 sequencing or steal another CL-03 Module's truth. |
| Update rule | Update this file before or in the same change as any binding change to ProfessionalProfile ownership, lifecycle, action-to-gate policy, public contracts, privacy behavior, Search projection input, or shared-operation usage. Progress updates must not silently change architecture. |

### Evidence basis and precedence

This document synthesizes the current Target Module Architecture Extract with the supplied Workin Ants project overview, Deep Module Registry, Cluster Registry, Prisma schema, Ubiquitous Language / Compliance inventory, Canonical Shared Operations Architecture, CL-03 architecture, and CL-03 build plan.

When those sources differ, use the following discipline:

1. preserve the current root and Cluster ownership rules;
2. treat executable Prisma structure as evidence of available persistence, not automatic evidence of semantic ownership;
3. prefer the current Ubiquitous Language and Canonical Shared Operations Registry over older convenience patterns;
4. preserve an external Module's source truth even when `ProfessionalProfile` has a relation or legacy summary field pointing to it;
5. mark necessary implementation decisions as **Proposed Rulings** instead of presenting inference as fact;
6. leave genuinely unsettled product/compliance questions **Unresolved** and keep affected production paths disabled.

The root `context/architecture.md` and `context/code-standards.md` were not supplied as complete files in this thread. This document therefore does not invent their exact repository conventions. Any later root rule that conflicts with a proposed placement or mechanism here supersedes the proposal.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Professional Eligibility owns the platform's **professional seller identity** and the **composition policy that answers whether that ProfessionalProfile may perform a named seller action**.

It exists so Workin Ants does not collapse seller identity, verification, healthcare, financial readiness, subscription entitlements, holds, Offerings, Gigs, Orders, and Search visibility into one `User` row or a collection of local booleans.

### Goal

Provide one stable source for:

- the lifecycle of a `ProfessionalProfile`;
- safe professional context facts required by neighboring Modules;
- action-specific professional readiness decisions;
- professional public-readiness decisions;
- owner-controlled consequences of external moderation/hold decisions on the ProfessionalProfile lifecycle;
- safe source projection input for Search;
- privacy execution against Professional Eligibility-owned data.

### What enters

- authenticated actor/system context from Identity & Access;
- resource/action authorization from Role / Authority;
- `ProfessionalProfile` creation/update inputs;
- accepted taxonomy context and taxonomy-triggered requirements from Taxonomy & Classification;
- professional-track entitlement decisions from Track Subscription & Entitlement;
- verification requirements/readiness from Trust Verification / Screening;
- healthcare readiness from Healthcare / Regulated Services;
- financial-readiness dimensions from Payment / Payout / Tax when the requested action's policy requires them;
- current `ComplianceHold` decisions;
- owner-supplied target context from Marketplace Supply, Gig / Demand, and Transaction / Order when evaluating those actions;
- moderation decisions that target a ProfessionalProfile;
- Privacy-owned enumerate/erase/anonymize/retain instructions;
- dependency-change domain events used to trigger reevaluation.

### What leaves

- authoritative `ProfessionalProfile` state;
- safe ProfessionalProfile context DTOs;
- structured action-specific readiness decisions through SH-016 `evaluateProfessionalReadiness`;
- professional public-readiness decisions through SH-024 `evaluatePublicReadiness`;
- safe source projection input for Search through SH-094 `buildSourceProjection`;
- versioned ProfessionalProfile domain events;
- Search refresh requests through SH-091;
- Notification requests through SH-041 when product policy requires them;
- generic audit requests through SH-029;
- privacy execution/enumeration results through SH-095/096/097;
- operational diagnostics through Observability-owned mechanisms.

### Business transformation

```text
Authenticated User wants to act as a seller
→ create or load the User's one ProfessionalProfile
→ Professional Eligibility owns that profile's lifecycle
→ consumer asks whether the profile may perform a named action
→ Professional Eligibility obtains only the necessary source-owner facts
→ it composes profile + entitlement + taxonomy + verification + healthcare + hold
  + only the financial dimensions explicitly required for that action
→ it returns one structured allow/deny/review/unavailable decision
→ the action-owning Module performs its own mutation
→ Professional Eligibility never takes ownership of that neighboring lifecycle
```

### Why this deserves its own Module boundary

The Module owns a distinct identity branch (`ProfessionalProfile`) and a distinct policy question: **may this seller identity perform this seller action now?** Neither belongs to authentication, Marketplace Supply, Trust, Payment, Healthcare, Search, Gig, or Order. Keeping this boundary prevents every consumer from reconstructing seller eligibility differently and prevents compliance providers from becoming seller lifecycle truth.

---

## 3. Owned Truth

### 3.1 Schemas / models owned

#### `ProfessionalProfile`

**Plain-English meaning:** the seller identity attached one-to-one to a `User`. A User does not sell directly; the ProfessionalProfile is the actor that creates Offerings, responds to Gigs, and participates seller-side in Orders after the applicable gates pass.

Professional Eligibility is the sole business owner of ordinary `ProfessionalProfile` creation, profile-field mutation, and profile lifecycle transitions.

### 3.2 Enums / statuses owned

#### `ProfileStatus` as applied to `ProfessionalProfile`

Current values:

- `draft`
- `active`
- `paused`
- `suspended`
- `archived`

The enum is also used by `CandidateProfile`. Current evidence therefore supports **separate lifecycle authority over a shared vocabulary** rather than moving Candidate lifecycle into this Module. See Proposed Ruling PE-PR-01 and Unresolved Decision PE-U02.

### 3.3 Lifecycles owned

- `ProfessionalProfile.status` lifecycle;
- the local meaning of profile status transitions, including which commands are permitted and what owner-side effects occur;
- the local consequence of an approved external moderation decision when that decision requires a profile transition.

Professional Eligibility does **not** own the lifecycle that produced the external decision.

### 3.4 Source-of-truth records

- `ProfessionalProfile.id` identifies the seller actor;
- `ProfessionalProfile.userId` binds that seller actor to one User;
- `ProfessionalProfile.status` is ProfessionalProfile lifecycle truth;
- profile-owned editable presentation/contact/location fields on `ProfessionalProfile` are source facts for the professional profile, subject to privacy and public-projection policy.

### 3.5 Domain events / ledgers owned

Professional Eligibility owns the **meaning** of ProfessionalProfile lifecycle events. Expected event families are:

- ProfessionalProfile created;
- ProfessionalProfile status changed;
- optionally, projection-relevant ProfessionalProfile fields changed when a consumer contract proves the need.

Exact wire names and versions are public-contract decisions and must be versioned. This Module currently has no approved dedicated lifecycle-event table. Generic `AuditEvent` is not a replacement for domain events; the shared transactional outbox is the publication mechanism.

### 3.6 Projections owned

Professional Eligibility may build a **safe source projection DTO** for a ProfessionalProfile through SH-094. That DTO is derived from current source truth and approved public-readiness decisions.

It does **not** own the persisted Search projection, `SearchUpsertEvent`, Typesense document, Search ranking state, or Search backfill state.

### 3.7 Snapshots / proof owned

No persisted `ProfessionalReadiness`, `EligibilitySnapshot`, `canSell`, or universal eligibility-decision source table is owned in MVP.

Readiness is evaluated from current owner truth. If a future legal/business requirement demands an immutable eligibility-decision snapshot, that requires a separate architecture ruling identifying owner, retention, and snapshot semantics. Generic audit rows must not be mistaken for that proof.

### 3.8 Policies / invariants owned

Professional Eligibility owns:

- the one-User-to-one-ProfessionalProfile rule at the business boundary;
- profile mutable/immutable field policy;
- the ProfessionalProfile transition graph once approved;
- action vocabulary for professional readiness;
- action-to-gate composition policy;
- mapping of dependency decisions into Professional Eligibility reason codes;
- professional public-readiness policy;
- safe reason-detail exposure by caller context;
- safe ProfessionalProfile source-projection allowlist;
- what an external hold/moderation decision means for the local profile lifecycle;
- local privacy field mapping for ProfessionalProfile under Privacy-owned instructions.

### 3.9 Fields present on `ProfessionalProfile` that are not authoritative gate truth

The current schema includes several overlapping/legacy fields. They remain non-authoritative unless a later approved migration gives them a new explicit role:

- `stripeReady` — must not be financial-readiness truth;
- `stripeAccountId` — must not replace Payment-owned `PayoutAccount` provider truth;
- `verifiedAt` / `verificationExpiresAt` — must not replace Trust-owned verification records;
- `trustScore` — has no approved formula/owner/version and must not gate seller actions;
- `ratingAverage` / `ratingCount` — derived Review projections only if retained;
- `onboardingCompleteAt` — present in the owned row, but its precise business semantics are unresolved and it must not substitute for readiness;
- `suspendedForModerationAt` — may serve only as local transition provenance/metadata after an external moderation decision; the moderation decision remains externally owned.

---

## 4. Explicit Non-Ownership

Professional Eligibility must not create convenient duplicates of the following responsibilities.

| Adjacent owner | Responsibility that remains there | Professional Eligibility may do | Professional Eligibility must not do |
| --- | --- | --- | --- |
| Identity & Access | `User`, authentication, sessions, security posture, MFA/passkeys, step-up lifecycle | consume authenticated actor/system context | create a seller login/session system, password/MFA helpers, or duplicate User identity |
| Role / Authority | permission interpretation | supply ProfessionalProfile relationship/action facts and consume authorization | own generic roles/capabilities or infer permission from UI state |
| Track Subscription & Entitlement | plans, subscriptions, entitlement grants, usage truth | ask whether a professional action is entitled | store `isPremium`, `sellerPlan`, `canSell`, commission booleans, or recreate plan logic |
| Taxonomy & Classification | taxonomy vocabulary, assignment validity, requirement triggers; taxonomy join semantics per root rules | consume accepted classifications and requirement triggers | hardcode compliance categories/tags or mutate canonical taxonomy vocabulary |
| Trust Verification / Screening | verification requirements/checks, screening, licenses, FCRA workflow, TrustBadge | consume SH-017/018 decisions | read TrustBadge as truth, duplicate verification statuses, run screening providers/webhooks |
| Healthcare / Regulated Services | healthcare lane, BAA, healthcare boundaries, healthcare payload policy | consume SH-020 | store `isHealthcareProvider`, duplicate BAA/healthcare state, implement PHI policy engine |
| Payment / Payout / Tax | KYC, tax, payout accounts, ledger, payout requests/transfers, financial readiness, Stripe/provider event truth | consume SH-019 when action policy requires it | implement KYC/tax/payout, read `stripeReady` as truth, call Stripe/Connect, own payouts |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and release decisions | consume hold decisions; request actions only through approved interface if a future policy requires | create `professionalBlocked`, local hold table, or release holds directly |
| Marketplace Supply | `Offering` aggregate/lifecycle and publication mutation | return `publish_offering` readiness | write `Offering.status`, pricing, details, media joins, or publication state |
| Gig / Demand | `Gig`, `GigResponse`, assignment lifecycle | return `respond_to_gig` readiness using Gig-owned target context | create/update GigResponse or infer Gig rules from direct Prisma reads |
| Transaction / Order | `Order` transaction lifecycle | return seller participation readiness using Order-owned context | write Order state, payment/refund outcome, agreements, or snapshots |
| Search / Public Visibility | `SearchUpsertEvent`, search document/index execution, query surface | build safe source input and request refresh | call Typesense, write Search queues, use Search state as truth |
| Media / File Access | `MediaAsset`, upload/scan/processing/private access/signed URL mechanics | reference approved media only if a future profile-media owner contract requires it | build upload, storage, scan, signed URL, or media-access infrastructure |
| Notification | notification subscriptions, attempts, providers, delivery | request a notification | call email/SMS/push providers directly |
| Audit / Event Ledger | generic `AuditEvent`, `AccessAuditLog` | append safe audit requests | create generic module-local audit tables or use audit as lifecycle truth |
| Observability / Ops | logs, metrics, IntegrationFailure, QueueJob, OpsIncident | emit safe operational metadata | use ops state as professional truth or create a module-specific incident/queue system |
| Privacy / Data Erasure | PrivacyRequest/DataErasure orchestration, retention exemptions, export bundle lifecycle | enumerate and execute instructions against owned data | create a ProfessionalProfile privacy-request workflow or decide legal retention alone |
| Content Moderation & Legal Notice | reports, legal notices, moderation cases/actions | execute an approved target decision against ProfessionalProfile through SH-103 | create moderation cases, determine legal takedown outcome, or own evidence preservation lifecycle |
| Review / Dispute | review/dispute lifecycle and reputation truth | consume only explicitly approved reputation projections if needed | own review truth or use rating projection as eligibility proof |

A foreign key or Prisma relation does not transfer ownership.

---

## 5. Module Architecture Principles

1. **Seller identity is `ProfessionalProfile`, not `User`.** Every seller-side domain operation must resolve the ProfessionalProfile actor branch explicitly.
2. **One owner per lifecycle.** Only Professional Eligibility transitions `ProfessionalProfile.status`.
3. **Readiness is composition, not a second database.** The Module evaluates current owner truth; it does not clone Trust, Healthcare, Payment, Entitlement, Taxonomy, or Hold state into a parallel readiness record.
4. **Readiness is action-specific.** `active`, `verified`, `stripeReady`, or any single boolean cannot answer all seller actions.
5. **The action owner still mutates its own object.** Professional Eligibility authorizes `publish_offering`, `respond_to_gig`, or seller Order participation; Marketplace, Gig, and Order remain the mutation owners.
6. **Source-owner interfaces replace direct foreign Prisma reads.** The Module requests narrow facts/decisions from each owner.
7. **Failure of a required dependency never becomes implicit allow.** Required gate dependency failure produces a safe non-allow result.
8. **Unresolved policy never becomes implicit policy.** An unresolved action-to-gate rule returns a stable review/unavailable result until approved.
9. **Reason codes are stable and audience-aware.** Consumers receive enough information to act without exposing raw screening, healthcare, financial, or moderation detail.
10. **Compatibility fields cannot satisfy a gate.** Legacy summary fields may be read only for migration/diagnostic compatibility, never for authorization/readiness.
11. **Search receives source decisions; it does not reconstruct eligibility.** Professional Eligibility builds safe public source input and requests projection work.
12. **Holds remain external stop signs.** The Module maps an active hold to its own action decision or lifecycle consequence without creating a local generic block system.
13. **Moderation decision and target execution are separate.** Moderation owns why; Professional Eligibility owns only the resulting ProfessionalProfile transition when instructed.
14. **Privacy request and data-owner execution are separate.** Privacy orchestrates; this Module modifies only its owned fields/record under a typed instruction.
15. **Domain events, audit, and observability are distinct.** Events describe source facts, audit proves actions/access, and Ops diagnoses execution.
16. **No provider client belongs here.** This Module consumes normalized provider-owner decisions only.
17. **Concurrency is database-backed.** Use approved lock/CAS/idempotency primitives; never rely on in-memory locks or frontend sequencing.
18. **A public contract must reveal less than the underlying schema.** Foreign relations and legacy fields are not automatically part of `getProfessionalProfileContext` or Search projection DTOs.

---

## 6. Proposed Folder / Code Structure

The Cluster architecture proposes `src/modules/professional-eligibility/`. The exact repository root is subordinate to root code standards. Within that Module boundary, use only folders with real responsibilities:

```text
src/
  modules/
    professional-eligibility/
      application/
        commands/
          create-professional-profile.*
          update-professional-profile.*
          transition-professional-profile.*
          execute-professional-moderation-decision.*
        queries/
          get-professional-profile-context.*
          evaluate-professional-readiness.*
          evaluate-professional-public-readiness.*
        services/
          professional-readiness-composer.*
          professional-source-projection-builder.*

      domain/
        profile/
          professional-profile-policy.*
          profile-transition-policy.*
        readiness/
          professional-action.*
          professional-readiness-policy.*
          professional-reason-codes.*
        projection/
          professional-public-field-policy.*

      contracts/
        public/
          commands.*
          queries.*
          decisions.*
          events.*
        dependencies/
          entitlement-port.*
          taxonomy-requirements-port.*
          verification-readiness-port.*
          healthcare-readiness-port.*
          financial-readiness-port.*
          compliance-hold-port.*
          target-context-ports.*

      infrastructure/
        repositories/
          professional-profile-repository.*
        events/
          professional-profile-event-mapper.*

      workers/
        professional-readiness-reevaluation-worker.*

      privacy/
        professional-profile-data-inventory.*
        professional-profile-privacy-executor.*

      tests/
        unit/
        integration/
        contracts/
        authorization/
        concurrency/
        privacy/
```

### Placement rules

- `domain/` contains owner policy and pure decision logic; no Prisma, providers, Search client, queue client, or email client.
- `application/` orchestrates commands/queries and invokes dependency interfaces/shared operations.
- `contracts/public/` contains the stable Module boundary that other Modules consume.
- `contracts/dependencies/` contains narrow ports for externally owned facts. It does not define foreign truth.
- `infrastructure/repositories/` may read/write only Professional Eligibility-owned persistence by default.
- `workers/` contains only owner-specific reaction logic; queue leasing/retry/dead-letter implementation remains shared platform infrastructure.
- `privacy/` is a data-owner executor, not a PrivacyRequest workflow.
- no `providers/` folder is appropriate for this Module in the current architecture;
- no generic `auth/`, `audit/`, `search/`, `notifications/`, `media/`, `payments/`, `verification/`, `healthcare/`, or `queues/` infrastructure should appear here.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / UI | Thin request translation, validation handoff, rendering of safe profile/readiness responses when an existing product surface calls the Module. | Business transition policy, permission interpretation, direct Prisma, dependency reconstruction, provider calls. |
| Application commands | Command orchestration, owner-record transaction boundary, shared-operation calls, downstream effect requests. | Foreign lifecycle mutation, provider semantics, generic infrastructure. |
| Application queries | Safe profile context, readiness/public-readiness orchestration, source projection build. | Raw cross-domain aggregation or universal compliance dashboard query. |
| Domain profile policy | Mutable field policy, profile lifecycle rules, local status meanings. | Identity, Moderation case, Hold, Trust, Healthcare, Payment lifecycles. |
| Domain readiness policy | Professional action vocabulary, action-to-gate matrix, reason normalization, dependency composition. | Underlying gate truth or provider status interpretation. |
| Repository / data access | `ProfessionalProfile` persistence and owner-safe transaction/CAS operations. | Direct repositories for VerificationCheck, HealthcareComplianceProfile, KYC, TaxProfile, PayoutAccount, Offering, Gig, Order, SearchUpsertEvent, ComplianceHold. |
| Dependency contracts | Minimum source-owner facts/decision shapes needed to compose readiness. | Foreign data models copied wholesale or a generic cross-domain repository. |
| Events | ProfessionalProfile event semantics and payload mapping. | Outbox storage implementation or another Module's event meaning. |
| Workers | Reevaluate affected professional actions after dependency events and request owner-safe downstream effects. | Generic queue runner, Search mutation, automatic foreign lifecycle mutation. |
| Privacy executor | Enumerate/modify owned ProfessionalProfile data under Privacy instruction. | PrivacyRequest lifecycle, legal-retention exemption records, cross-service deletion orchestration. |
| Provider adapters | None. | Stripe, screening, BAA/e-sign, Typesense, email/SMS/push, or other provider clients/webhooks. |

---

## 8. Data Model

### 8.1 `ProfessionalProfile`

#### Purpose

Represents the seller identity branch attached to one base User.

#### Key relationships

- belongs one-to-one to `User` through unique `userId`;
- is referenced by Marketplace Offerings;
- is referenced by Gig responses/assignments;
- is referenced seller-side by Orders;
- has taxonomy category/tag relationships;
- is referenced by Trust, Healthcare, Payment, Hold, Review, and other owner records;
- may have profile-media relations in the schema, but profile-media ownership is not established by the target Module registry and is not introduced by this plan.

These relations are navigation/integrity evidence. They do not authorize this repository to mutate the related owner records.

#### Authoritative fields

The following categories are authoritative for Professional Eligibility, subject to field-level policy:

- identity: `id`, `userId`;
- public/profile identity: `slug`, `headline`, `bio`, `websiteUrl`;
- profile location facts: `city`, `state`, `country`;
- lifecycle: `status`;
- timestamps: `createdAt`, `updatedAt`;
- `defaultCurrency` may be treated as a professional preference if required by product behavior, but must never substitute for Payment/Order currency truth;
- `suspendedForModerationAt` may be local lifecycle provenance only after an approved moderation action.

#### Non-authoritative / derived fields

- `ratingAverage`, `ratingCount` — rebuildable Review projections if retained;
- `stripeAccountId`, `stripeReady` — compatibility only, not Payment truth;
- `verifiedAt`, `verificationExpiresAt`, `trustScore` — compatibility/projection only, not Trust truth;
- `onboardingCompleteAt` — exact semantics unresolved; do not use as `canSell` or readiness proof.

#### Lifecycle/status field

`status: ProfileStatus`, default `draft`.

#### Uniqueness constraints

- `userId` is unique: database-level one User → at most one ProfessionalProfile;
- `slug` is unique.

The creation command must still be idempotent and concurrency-safe; uniqueness errors are not an application design by themselves.

#### Concurrency-sensitive fields

- `status` transitions;
- mutable profile fields when simultaneous edits occur;
- unique `slug` changes;
- one-to-one provisioning under concurrent create attempts.

The current schema has no explicit aggregate `version` field. Use root-approved DB locking/CAS mechanics and an expected-state token until/unless an explicit version migration is approved. See PE-U06.

#### Retention / privacy concerns

`ProfessionalProfile` contains personal profile copy and is heavily referenced by commercial/compliance records. Product archive is not legal erasure. The Privacy executor must support field-level anonymization/retention instructions and must not rely on raw cascading deletion from `User` to satisfy a privacy request. Exact retention/anonymization mappings remain subject to Privacy/legal policy.

### 8.2 No Module-owned readiness table

There is intentionally no authoritative `ProfessionalReadiness`, `ProfessionalEligibility`, `canSell`, or global gate-result model in MVP.

The decision is reconstructed from current source-owner interfaces for the requested action. Any cache must be explicitly rebuildable, versioned by its sources, and non-authoritative.

### 8.3 Taxonomy classification records

`ProfessionalCategory` and `ProfessionalTag` exist in the Prisma model graph, but current taxonomy ownership rules place controlled vocabulary and classification semantics with Taxonomy & Classification. Professional Eligibility may require classification context and may call Taxonomy's approved assignment/validation interface; it must not silently claim these joins as its own data model simply because they relate to ProfessionalProfile.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 `ProfileStatus`

| Status | Current meaning for ProfessionalProfile | Notes |
| --- | --- | --- |
| `draft` | Seller profile exists but is not operating as an active professional. | Confirmed default in Prisma. Full activation prerequisites are action-policy dependent. |
| `active` | ProfessionalProfile is in an operating lifecycle state. | Does not by itself prove every action is allowed. Readiness must still be evaluated for the requested action. |
| `paused` | Professional has temporarily stopped ordinary seller availability/operation under owner policy. | Exact commands/automatic effects require transition policy approval. |
| `suspended` | Platform-enforced restriction of the ProfessionalProfile under an approved source decision/policy. | Must not be used as a generic copy of every ComplianceHold. |
| `archived` | ProfessionalProfile is retired from ordinary operation. | Reopen behavior is not approved; treat as non-operational until an explicit ruling exists. |

### 9.2 Confirmed lifecycle facts

- profile creation results in `draft` by schema default;
- only Professional Eligibility may write `ProfessionalProfile.status`;
- status is not equivalent to Trust, Healthcare, Payment, or Entitlement readiness;
- lifecycle mutation must use explicit commands and policy, never a public `setStatus(status)` method;
- current readiness must be reevaluated for readiness-sensitive transitions such as activation/resume once the action matrix is approved;
- a moderation/hold source decision does not become owned by this lifecycle merely because it causes a transition.

### 9.3 Transition graph status

The source set names likely lifecycle commands but does not establish a complete, approved adjacency table, reinstatement target, archive reversibility, or whether specific dependency failures automatically transition an already-active profile.

The following is therefore a **Proposed Ruling**, not a binding transition graph:

```text
create
  → draft

draft
  ── activate (current readiness must allow) ──> active

active
  ── pause ──> paused

paused
  ── resume (current readiness must allow) ──> active

draft / active / paused
  ── approved moderation/admin enforcement ──> suspended

suspended
  ── reinstate ──> [target state unresolved]

eligible source states
  ── archive ──> archived

archived
  ── no reopen path is approved
```

### 9.4 Transition owner

Professional Eligibility application/domain policy is the transition authority. An external source such as Moderation can instruct an effect through a typed public command, but it does not write the row.

### 9.5 Triggers

Possible triggers include:

- professional explicit action: create, update, pause, resume, archive;
- readiness-approved activation/resume;
- approved moderation decision execution;
- approved admin/support action under Role / Authority and source-decision rules;
- Privacy instruction is **not** an ordinary lifecycle trigger and must not be implemented as archive-only erasure.

### 9.6 Terminal/reopen rules

`archived` should be treated as non-operational and non-allow for seller actions. Whether it is permanently terminal or can be restored is **Unresolved**.

### 9.7 Concurrency expectations

- status changes are transaction-safe;
- caller supplies expected current state and/or root-approved concurrency token;
- stale transitions return `conflict`, not last-write-wins;
- moderation/suspension cannot be overwritten by a stale resume/activation;
- idempotent replay returns the original successful transition result when semantically identical.

### 9.8 Event/history proof

Successful lifecycle changes emit a transactional owner event and may append generic Audit proof for high-impact actions. Audit is not the lifecycle event ledger. If immutable full transition history is later required as a Module-owned record, it needs an architecture ruling.

### 9.9 Prohibited shortcuts

- direct `status` assignment from routes/components;
- generic `setProfessionalStatus` public API;
- using `active` as the complete seller authorization decision;
- auto-suspending from a provider webhook in this Module;
- direct external Module writes to the profile row;
- using `suspendedForModerationAt` without validating the source moderation decision.

---

## 10. Commands

The names below are Module public/application command names, not necessarily HTTP route names.

| Command | Purpose | Actor / context | Authoritative inputs | Preconditions | State written | Shared operations consumed | Events / audit / notification | Idempotency | Primary failure modes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `createProfessionalProfile` | Provision the User's one seller identity. | Authenticated User or approved system/admin context. | actor, user target if administrative, allowed initial fields, idempotency key. | actor authorized; User exists; one-to-one rule; valid unique slug/input. | new `ProfessionalProfile`, default `draft`. | SH-001, SH-002, SH-044, SH-114, SH-046. | Profile-created event; audit only where root/product policy requires. | Required; concurrent duplicates converge on one canonical profile/result. | validation, forbidden, slug conflict, duplicate semantic conflict, persistence failure. |
| `updateProfessionalProfile` | Change ProfessionalProfile-owned editable fields. | Profile owner or approved admin. | profileId, patch, expected concurrency state. | actor authorized; profile exists; field allowed; lifecycle permits edit; slug unique. | owner fields only. | SH-001, SH-002, SH-052 or root concurrency equivalent, SH-046 when consumers need projection refresh. | Optional projection-relevant event; SH-091 may be requested after committed public-field changes; audit by policy. | Replayed semantic command produces one effective result where SH-044 is used. | validation, forbidden, not found, slug conflict, stale edit. |
| `activateProfessionalProfile` | Move a profile into active operation. | Owner/admin under approved policy. | profileId, target/action context, expected status, idempotency key. | transition graph approved; current SH-016 activation decision allows; no stale state. | `status=active` and only approved local lifecycle metadata. | SH-001, SH-002, SH-016 internally as owner decision, SH-044, SH-051/052/053, SH-046, SH-029, SH-091/041 as effects. | status-changed event; audit; Search refresh; notification if approved. | Required. | policy unresolved, readiness denied/review, dependency unavailable, conflict, forbidden. |
| `pauseProfessionalProfile` | Voluntarily or administratively pause operation under approved policy. | Owner/admin. | profileId, reason category if required, expected state. | transition allowed; actor authority; no stale state. | `status=paused`. | SH-001, SH-002, SH-044, SH-051/052/053, SH-046, SH-029, SH-091. | status event; audit where required; deindex/refresh. | Required for replay-prone command. | invalid transition, forbidden, conflict. |
| `resumeProfessionalProfile` | Return a paused profile to active after checking current gates. | Owner/admin. | profileId, expected state, action context, idempotency key. | transition allowed; current resume/activation readiness allows. | `status=active`. | SH-001, SH-002, SH-016, SH-044, SH-051/052/053, SH-046, SH-029, SH-091. | status event; audit; Search refresh. | Required. | policy unresolved, readiness denied, dependency unavailable, conflict. |
| `executeProfessionalModerationDecision` | Apply an externally owned moderation decision to the ProfessionalProfile lifecycle. | Approved system/admin capability with source decision reference. | moderation decision ID/version, target profileId, requested effect, reason code, idempotency key. | SH-103 decision valid for target/effect; transition mapping approved; no stale/revoked source decision. | local profile status/provenance only. | SH-002/system auth, SH-103, SH-044, SH-051/052/053, SH-046, SH-029, SH-091, SH-041 if approved. | status event + source decision ref; audit; Search/notification effects. | Required by source decision/version. | invalid target, stale/revoked decision, unsupported effect, conflict. |
| `reinstateProfessionalProfile` | Reverse a prior suspension only after approved source remediation/release policy. | Authorized system/admin; owner self-service only if explicitly approved. | profileId, source decision/release proof, expected state. | reinstatement target and source rules approved; source hold/moderation conditions cleared; current readiness if target becomes active. | status to approved target. | SH-002, SH-011/013 or SH-103 as applicable, SH-016 if active target, SH-044, SH-051/052/053, SH-046, SH-029, SH-091. | status event; audit; Search refresh. | Required. | unresolved target-state policy, source not cleared, readiness denied, conflict. |
| `archiveProfessionalProfile` | Retire a profile from ordinary seller operation. | Owner/admin under approved lifecycle policy. | profileId, expected state, reason category. | source-state transition approved; actor authorized. | `status=archived`. | SH-001, SH-002, SH-044, SH-051/052/053, SH-046, SH-029, SH-091. | status event; audit; Search removal/refresh. | Required. | invalid source state, forbidden, conflict. |
| `executeProfessionalPrivacyInstruction` | Apply a Privacy-owned erase/anonymize/retain instruction to this Module's fields. | Privacy worker/system context. | typed Privacy target instruction, retention decision context, idempotency key. | target belongs to this Module; retention/legal disposition approved; instruction authorized. | only owner fields allowed by instruction; may preserve structural record. | SH-095, SH-097, SH-098, SH-044, SH-046 if source facts change, SH-091. | privacy result returned to orchestrator; safe audit handled per Privacy/Audit policy. | Required. | retention unresolved, conflicting retained relationships, invalid target, partial external dependency failure. |

### Command rule

No command may directly update `Offering`, `GigResponse`, `Order`, `ComplianceHold`, Trust, Healthcare, Payment, Search, Audit, Notification, or Privacy source tables.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result | Kind | Stable reason codes | Consumer must not infer |
| --- | --- | --- | --- | --- | --- | --- |
| `getProfessionalProfileContext` | Marketplace, Trust, Healthcare, Payment, Hold, Gig, Order, internal UI/application | profileId or actor-owned profile reference; requesting context | minimum safe owner facts: profile ID, permitted User relationship reference, lifecycle status, approved classification/public facts/version metadata | Source truth DTO | not generally needed beyond not-found/forbidden | foreign compliance status, payout readiness, Search visibility, or raw relations |
| `evaluateProfessionalReadiness` (SH-016) | Marketplace, Gig, Order, Search/public-readiness composition, onboarding | profileId, controlled professional action, owner-supplied target context, evaluation time/caller context | decision class, safe blockers/warnings, owner evidence refs, policy/source versions, evaluatedAt | Readiness decision | yes; Module-owned normalized codes | that one gate result authorizes the foreign lifecycle mutation; consumer must still enforce its own local rules |
| `evaluateProfessionalPublicReadiness` (SH-024 implementation for professional source) | Search, profile public surface, projection worker | profileId, public surface/context, evaluation time | allow/deny/review/unavailable plus safe reasons and source version | Public-readiness decision | yes | that Search is source truth or that public readiness permits Marketplace/Gig/Order mutations |
| `buildProfessionalSourceProjection` (SH-094) | Search refresh bridge | profileId, approved surface/version | allowlisted ProfessionalProfile source fields + source version/readiness reference | Rebuildable source projection | n/a | raw User/compliance/provider/hold/private fields from omitted data |
| `enumerateProfessionalSubjectData` (SH-096) | Privacy | subject User/profile ID | owned record IDs/field categories/projection/provider refs (none provider-owned here) | Privacy inventory | deterministic disposition categories | that enumeration itself authorizes deletion |
| `evaluateProfessionalRetentionRequirement` (SH-097 contribution) | Privacy | target record/field classes + legal/business context | owner retention facts/constraints; no exemption lifecycle | Retention facts | safe retention reason IDs | final legal disposition; Privacy records the exemption/decision |

### Initial professional action vocabulary

**Proposed Ruling PE-PR-05:** the v1 controlled action vocabulary should be limited to the seller actions already established by the Cluster architecture/build plan:

- `activate_profile`;
- `public_visibility`;
- `publish_offering`;
- `respond_to_gig`;
- `participate_in_order`.

The exact serialized keys must be fixed in the contract feature and versioned. Free-form client strings are prohibited.

`request_payout` is not a Professional Eligibility action. Payment owns payout financial readiness and execution.

### Decision result shape

SH-015 `returnDecisionResult` is still a Proposed shared contract. Until it becomes canonical, Professional Eligibility may define an owner-specific response aligned to the same principles without creating a platform-wide dependency.

Suggested owner-specific fields:

- `decision`: `allow | deny | review | unavailable`;
- `reasons[]`: stable code, blocking flag, source owner, safe evidence references, optional safe remediation key;
- `warnings[]`: non-blocking safe notices;
- `evaluatedAt`;
- `policyVersion`;
- `sourceVersions` / source decision versions where supplied;
- optional retryability metadata for `unavailable`.

Raw provider codes/reports, PHI, tax identifiers, and confidential hold/moderation detail are never part of the generic decision result.

---

## 12. Public Module Interface

Other Modules should prefer this interface over direct Prisma access to Professional Eligibility-owned rows.

### Public commands

- `createProfessionalProfile`
- `updateProfessionalProfile`
- explicit owner lifecycle commands once their transition policies are approved:
  - `activateProfessionalProfile`
  - `pauseProfessionalProfile`
  - `resumeProfessionalProfile`
  - `reinstateProfessionalProfile`
  - `archiveProfessionalProfile`
- `executeProfessionalModerationDecision` for SH-103 target execution
- privacy executor entry point for SH-095

There is no public generic `setProfessionalStatus` command.

### Public queries / decisions

- `getProfessionalProfileContext`
- SH-016 `evaluateProfessionalReadiness`
- SH-024 `evaluatePublicReadiness` for ProfessionalProfile public visibility
- SH-094 `buildSourceProjection` for ProfessionalProfile
- SH-096 `enumerateSubjectData`
- SH-097 `evaluateRetentionRequirement`

### Emitted domain events

Stable event families:

- ProfessionalProfile created;
- ProfessionalProfile status changed.

Projection-relevant generic update events may be added only when a consumer need and payload contract are established.

**No `ProfessionalReadinessChanged` source event is assumed in MVP.** Since readiness is not persisted as source truth, a dependency-change handler may simply reevaluate current state and request a Search refresh. A true “changed” event requires a defined comparison/snapshot contract. See PE-PR-08.

### Privacy executor

Professional Eligibility implements its own typed enumerate/execute/retention contribution. Privacy remains orchestrator and owner of request/job/exemption truth.

### Provider-facing interfaces

None. Provider callbacks and provider credentials are explicitly outside this Module.

---

## 13. Inbound Dependencies

| Owning Module | Public operation / interface consumed | Why required | Minimum information needed | May block action? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | establish who is acting | actor ID/type, authenticated/system assurance, safe session context | yes for protected operations | auth/session/User security system |
| Role / Authority | SH-002 `authorizeResourceAction` | decide whether actor may invoke a profile/readiness operation | actor, action, resource relation facts | yes | roles/capability engine |
| Track Subscription & Entitlement | SH-005 `resolveEntitlement` | establish professional selling feature access/limits where action policy requires | subject/track, entitlement key, value/status/effective interval/source version | yes | plan/subscription/entitlement tables and premium flags |
| Taxonomy & Classification | SH-022 `resolveTaxonomyRequirements`; SH-023 assignment validation when applicable | determine which compliance requirements are triggered by accepted classification | canonical category/tag IDs, active/accepted state, requirement triggers/version | yes when classification/trigger required | hardcoded category compliance arrays, taxonomy truth |
| Trust Verification / Screening | SH-017 `resolveVerificationRequirements`; SH-018 `evaluateVerificationReadiness` | establish required/current verification and credential readiness | subject, target/action context; decision, safe reason/evidence IDs, expiry/source version | yes when triggered | VerificationCheck/License/TrustBadge truth or provider mapping |
| Healthcare / Regulated Services | SH-020 `evaluateHealthcareReadiness` | establish healthcare/BAA lane readiness when context is healthcare-sensitive | subject + target context; decision, safe reasons/evidence IDs/version | yes when triggered | HealthcareComplianceProfile/BAA/boundary policy |
| Payment / Payout / Tax | SH-019 `evaluateFinancialReadiness` | establish financial dimensions only for actions whose policy explicitly requires them | professional ID/action context; dimensioned KYC/tax/account/hold/restriction result | yes when action matrix requires | KYC/tax/payout tables, Stripe flags, provider mapping |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | reusable stop-sign check | profile/target/action, active hold IDs/scopes/reasons safe for caller | yes | local blocked flag or hold lifecycle |
| Marketplace Supply | owner-specific Offering eligibility context query; exact dependency interface verified against Marketplace Module | evaluate `publish_offering` using immutable/safe Offering context | Offering ID, owner professional ID, taxonomy/healthcare/verification trigger refs, source version, local publication readiness facts | yes if context invalid/missing | Offering repository/lifecycle |
| Gig / Demand | owner-specific Gig response context query | evaluate `respond_to_gig` | Gig ID, requirement/taxonomy/regulated context, source version | yes | Gig/GigResponse repository/lifecycle |
| Transaction / Order | owner-specific seller participation context query | evaluate `participate_in_order` | Order ID, seller ProfessionalProfile ID, relevant requirement/state snapshot, source version | yes | Order lifecycle/payment truth |
| Content Moderation & Legal Notice | SH-103 `executeModerationDecision` source decision contract | execute an approved profile restriction/restoration effect | decision ID/version, target, effect, source reason class | yes for lifecycle consequence | ModerationCase/Action lifecycle |
| Privacy / Data Erasure | SH-095/096/097 protocol | execute subject data work without owning privacy workflow | subject/target, requested disposition, retention context, request/job correlation | yes for destructive action | PrivacyRequest/DataErasureJob/exemption truth |

### Dependency failure rule

A required dependency that is unavailable, stale, malformed, or cannot establish current truth produces a safe non-allow / retryable result. This Module never assumes “probably eligible.”

---

## 14. Outbound Consumers and Effects

### Consumers of ProfessionalProfile source truth

- Marketplace Supply — professional identity/status context before Offering operations;
- Gig / Demand — professional actor/readiness before a response;
- Transaction / Order — seller identity/readiness context;
- Payment / Payout / Tax — seller identity reference for financial records;
- Trust — subject context for professional verification;
- Healthcare — professional context for regulated lane;
- Search / Public Visibility — approved public ProfessionalProfile source projection and public-readiness decision;
- Admin Review / Compliance Hold — target identity/context;
- Privacy — owned-data inventory/execution;
- Review / Dispute and other consumer Modules only through narrow source-owner contracts when needed.

### Events consumers may react to

- ProfessionalProfile created;
- ProfessionalProfile status changed.

A consumer must re-read current owner truth or use versioned event payloads; events do not grant permission to mutate the profile.

### Downstream projection requests

Professional Eligibility requests Search refresh through SH-091 after relevant committed changes or dependency-driven public-readiness reevaluation. Search owns queuing, provider execution, retries, index document lifecycle, and de-index/re-index mechanics.

### Notification requests

Possible triggers include profile activation, suspension, reinstatement, archive, or remediation-needed changes when product policy explicitly requires them. Notification owns delivery and subscription mechanics.

### Audit requests

High-impact lifecycle/admin actions should append generic proof through SH-029. Audit metadata includes only safe actor/action/target/outcome/source-decision references.

### Workflow handoffs

- readiness allow is returned to the action owner; Professional Eligibility does not execute Offering/Gig/Order mutations;
- moderation target execution is a typed source-decision handoff;
- privacy target execution is a Privacy-orchestrated handoff;
- Search refresh is a projection request, not a direct write.

---

## 15. Canonical Shared Operations Used

Only operations relevant to Professional Eligibility are listed here. Proposed operations may guide shape but cannot become hard platform dependencies until approved.

| Canonical operation | Plain-English meaning | Canonical owner / classification | Why this Module uses it | Invocation point | Local policy that remains here | Expected result | Prohibited local duplicates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | Establish authenticated User/system actor context. | Identity & Access; canonical capability | every protected entry point requires trusted actor context | command/query boundary | none beyond required action context | ActorContext or unauthenticated result | `professionalAuth.ts`, `getCurrentUser.ts`, seller session helpers |
| **SH-002 `authorizeResourceAction`** | Determine whether actor may invoke an action on a resource. | Role / Authority; canonical capability | profile commands and privileged decision access | after actor resolution, before mutation/sensitive query | resource relationship facts/action vocabulary | allow/deny authority decision | seller role engine, `canEditProfessional.ts`, admin guard clones |
| **SH-003 `queryOwnerFacts`** — **Proposed** | Read minimum source-owner facts. | shared contract; separate owner implementations | pattern for Marketplace/Gig/Order context without direct DB reads | when an approved owner-specific context query exists | exact facts this Module requests | minimal owner DTO + source version | generic cross-domain repository |
| **SH-005 `resolveEntitlement`** | Resolve track entitlement value/effective status. | Track Subscription & Entitlement | selling access or action-specific commercial gate | readiness composition | which action requires which entitlement key/value | typed entitlement decision/value/version | `isPremium`, `sellerPlan`, `canSell` flags |
| **SH-011 `evaluateComplianceHold`** | Determine whether active holds block target/action. | Admin Review / Compliance Hold | reusable stop sign in readiness/lifecycle | readiness or hold-sensitive transition | mapping hold scope/reason to local action/lifecycle effect | active blocking holds + safe evidence | `professionalBlocked`, local hold table/service |
| **SH-015 `returnDecisionResult`** — **Proposed** | Common decision envelope. | shared contract/separate policy | align readiness responses without inventing incompatible shapes | contract design only until approved | professional action/gate/reason semantics | canonical envelope if approved | global local `ReadinessDecision` authority before approval |
| **SH-016 `evaluateProfessionalReadiness`** | Determine whether a ProfessionalProfile may perform named seller action. | **Professional Eligibility public interface; canonical confirmed** | this is the Module's core public decision | consumer action gate | entire action-to-gate composition, reason normalization | action decision with evidence/source versions | consumer-built `canProfessional...` engines |
| **SH-017 `resolveVerificationRequirements`** | Return applicable verification requirements. | Trust public interface | identify Trust requirements for professional action | readiness composition | whether/when action invokes Trust, not Trust requirement semantics | requirement descriptors/IDs/version | hardcoded background/license maps |
| **SH-018 `evaluateVerificationReadiness`** | Determine whether required checks/credentials are current. | Trust public interface | verification dimension of readiness | after taxonomy/target requirements resolved | how Trust result maps to professional decision | allow/deny/review + safe evidence | `isVerified.ts`, TrustBadge interpretation |
| **SH-019 `evaluateFinancialReadiness`** | Return dimensioned financial readiness. | Payment / Payout / Tax public interface | financial dimension for approved actions | only when action matrix requires it | whether the requested professional action needs which dimensions | KYC/tax/account/hold/restriction decision dimensions | `stripeReady.ts`, `canPayout.ts`, KYC logic |
| **SH-020 `evaluateHealthcareReadiness`** | Determine healthcare/BAA/boundary readiness. | Healthcare public interface | regulated lane gate | only when context triggers healthcare | whether action requires healthcare result | safe decision/evidence/version | `isHealthcareProvider.ts`, local HIPAA gate |
| **SH-022 `resolveTaxonomyRequirements`** | Convert accepted classification into requirement triggers. | Taxonomy & Classification | know which Trust/Healthcare requirements apply | readiness composition | action interpretation of triggers | canonical trigger set/version | hardcoded category/tag gate arrays |
| **SH-023 `validateTaxonomyAssignment`** | Validate canonical classification assignment. | Taxonomy & Classification | profile classification update only if an approved Professional assignment workflow calls it | before accepting classification context | whether classification is required for profile transition | validated assignment/result | taxonomy copies/normalizers |
| **SH-024 `evaluatePublicReadiness`** | Decide whether source truth may appear in a discovery surface. | source/compliance owner; Search composes; shared contract/separate policy | ProfessionalProfile public visibility | Search/public surface decision | Professional-specific public readiness | public allow/deny/review + source version | Search reconstructing professional compliance |
| **SH-029 `appendAuditEvent`** | Append generic proof of an important action. | Audit / Event Ledger | high-impact profile/admin lifecycle actions | after/with successful owner action according to root transaction policy | which actions require audit and safe metadata | append-only audit reference | `professionalAudit.ts`, generic local audit log |
| **SH-034 `sanitizeTelemetryMetadata`** | Remove secrets/sensitive data from telemetry. | Observability/Ops + Audit payload policy | readiness may touch sensitive source decisions | before logging/audit diagnostics | sensitivity labels/reason detail | safe metadata | raw dependency/provider payload logging |
| **SH-037 `recordIntegrationFailure`** | Record normalized integration/dependency failure. | Observability / Ops | source-owner dependency or downstream request failures | failure boundary | business meaning remains local; Ops gets technical metadata | operational failure reference | local failure table used as business truth |
| **SH-038 `recordQueueTelemetry`** | Record worker attempt/retry/dead-letter telemetry. | Observability / queue infrastructure | dependency-change reevaluation worker | each worker attempt | completion meaning/retry classification | queue telemetry | module-local queue ledger |
| **SH-041 `requestNotification`** | Ask Notification to deliver a business alert. | Notification | lifecycle/remediation messages | after approved source event/decision | trigger and safe template variables | notification request receipt | direct email/SMS/push clients |
| **SH-044 `executeIdempotentCommand`** | Guarantee one business effect for retries. | platform application infrastructure | profile provisioning and replay-prone mutations | command entry/transaction | semantic command identity/conflict semantics | original or single committed result | local idempotency map/table |
| **SH-045 `deduplicateDomainEvent`** | Prevent consumed event replay from repeating effects. | platform event inbox | readiness dependency-change event handling | worker/event consumer | handler identity and downstream effect | claim/replay result | `processedProfessionalEvent` boolean |
| **SH-046 `publishDomainEvent`** | Reliably publish versioned source event after commit. | platform transactional outbox | lifecycle events | authoritative mutation transaction | event family/payload/version | outbox append/receipt | ad-hoc emit-after-write/event bus wrapper |
| **SH-047 `enqueueReliableJob`** | Persist async work with retry/dead-letter. | shared queue | reevaluation/projection effect processing when async | dependency-change handling | payload/business completion criteria | durable job | local queue table/runner |
| **SH-048 `executeRetryWithBackoff`** | Retry transient failures with bounded policy. | shared platform/queue | source-owner/Search/Notification transient failures | worker execution | retryability classification | retry/dead-letter outcome | custom infinite retry loop |
| **SH-051 `acquireAggregateLock`** | Serialize conflicting mutations on one aggregate. | shared persistence | lifecycle/moderation races where locking is selected | transaction boundary | lock key/conflicting actions | DB-backed lock | in-memory mutex |
| **SH-052 `withOptimisticConcurrency`** | Reject stale writes via expected version/CAS. | shared persistence | profile edit/lifecycle concurrency where CAS selected | owner mutation | conflict/merge policy | success or stale conflict | last-write-wins updates |
| **SH-053 `transitionLifecycleState`** | Reuse state-machine mechanics while owner retains graph. | shared mechanism/separate truth | ProfessionalProfile status transitions | lifecycle commands | legal graph, reasons, side effects | validated transition result | generic CL-03 status policy |
| **SH-091 `requestSearchProjectionRefresh`** | Ask Search to index/update/hide/remove/restore. | Search / Public Visibility | public profile projection effects | after committed source/public-readiness change | when ProfessionalProfile should request refresh | Search request receipt/idempotency | Typesense client, direct SearchUpsertEvent writes |
| **SH-094 `buildSourceProjection`** | Build deterministic safe source input for Search. | each source owner | ProfessionalProfile Search input | before SH-091/index worker read | field allowlist/public readiness | source projection + version | Search reading raw profile/compliance tables |
| **SH-095 `executePrivacyInstruction`** | Execute Privacy-owned instruction on owner data. | Privacy orchestrates; data owner executes | privacy fulfillment | Privacy dispatch | field disposition on ProfessionalProfile | deterministic target result | local privacy workflow |
| **SH-096 `enumerateSubjectData`** | Enumerate subject data owned by a Module. | each data owner | Privacy inventory/export | Privacy planning | Professional-owned records/fields | inventory result | generic cross-domain repository |
| **SH-097 `evaluateRetentionRequirement`** | Supply owner retention facts while Privacy records exemption. | data owner + Privacy | prevent illegal/destructive erasure | before destructive action | which profile relationships/fields require retention consideration | retention facts | local retention-exemption table |
| **SH-098 `anonymizePersonalFields`** | Apply shared anonymization mechanics with owner field mapping. | shared primitive; owner policy | privacy execution | approved anonymize instruction | exact ProfessionalProfile field mapping | deterministic anonymized values/result | one generic eraser across domains |
| **SH-103 `executeModerationDecision`** | Target owner applies externally owned moderation decision. | Moderation decision; target owner execution | suspend/restrict/restore ProfessionalProfile when instructed | moderation command | local lifecycle consequence | validated effect/source decision context | local moderation case/workflow |
| **SH-114 `provisionOneToOneProfile`** | Reuse one-to-one profile provisioning mechanics. | shared mechanism; each profile owner retains truth | safe User→ProfessionalProfile creation | create command | Professional defaults/unique rule | canonical existing/new profile result | generic profile table/lifecycle |

### Classification summary

- canonical shared capabilities: SH-001, 002, 005, 011, 029, 034, 037, 041;
- platform primitives/mechanisms: SH-044, 045, 046, 047, 048, 051, 052, 053;
- shared contract / separate policy: SH-015 Proposed, SH-024, SH-094;
- another Module's public interface: SH-017, 018, 019, 020, 022, 023, 091;
- Module's own canonical public interface: SH-016;
- shared mechanism / separate truth: SH-098, SH-114;
- source-decision / target-execution contract: SH-103;
- privacy orchestration protocol: SH-095/096/097.

---

## 16. Module-Internal Operations

These operations remain local because they encode Professional Eligibility-specific policy rather than reusable platform mechanics.

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `validateProfessionalProfilePatch` | enforce mutable field/value policy | actor context, current profile, patch | normalized accepted patch or errors | ProfessionalProfile | profile-specific field semantics |
| `resolveProfessionalActionPolicy` | map controlled action to required gate dimensions | professional action, target context/version, policy version | ordered gate plan | none | this is the Module's core policy |
| `composeProfessionalReadiness` | combine source-owner decisions into one professional result | profile state + entitlement/taxonomy/Trust/Healthcare/Payment/Hold results | normalized decision/reasons/source versions | none | only Professional Eligibility defines seller action composition |
| `normalizeProfessionalReasonCodes` | map dependency outcomes to stable audience-safe reasons | source owner decision + caller audience | Module reason codes / redacted detail | none | prevents provider/domain leakage and stabilizes consumers |
| `evaluateProfileLifecycleDimension` | determine whether current profile status blocks requested action | profile status + action | dimension result | none | profile lifecycle is owned here |
| `buildProfessionalPublicSourceProjection` | build allowlisted profile-only public source DTO | current profile + public-readiness result | projection DTO | none; derived | Search must not inspect raw schema |
| `mapModerationEffectToProfileTransition` | translate validated external moderation effect into owner lifecycle command | source decision/effect + current profile | allowed transition or unsupported result | ProfessionalProfile when command proceeds | target owner owns consequence, not source case |
| `mapPrivacyInstructionToProfessionalFields` | decide owner-field anonymize/retain/delete behavior under approved privacy instruction | target instruction + retention result | field disposition plan | ProfessionalProfile | owner knows its fields; Privacy owns orchestration |
| `classifyReadinessDependencyFailure` | distinguish retryable dependency outage from deterministic denial | dependency error/contract result | unavailable/retryable/operational diagnostic | none | action decision must fail safely without exposing technical details |

No local operation may become a hidden duplicate of authentication, authorization, verification, healthcare, payment, Search, Privacy, Audit, Notification, or queue infrastructure.

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Profile provisioning:** SH-114 may provide one-to-one/idempotent mechanics, but `ProfessionalProfile` remains separate truth from Candidate/Customer profiles.
2. **Lifecycle state machine:** SH-053 may provide transition plumbing, but Professional Eligibility owns `ProfileStatus` use, adjacency, reasons, and effects for ProfessionalProfile.
3. **Concurrency:** SH-051/052 provide DB lock/CAS mechanics; this Module owns which profile commands conflict and what stale result means.
4. **Idempotency:** SH-044 stores/coordinates command replay; Professional Eligibility defines semantic identity and replay result for each command.
5. **Domain events:** SH-046 publishes reliably; Professional Eligibility owns event meaning/payload version. Outbox rows are transport evidence, not profile truth.
6. **Readiness response:** SH-015 may later standardize the envelope; Professional Eligibility retains its action/gate/reason policy.
7. **Public readiness:** SH-024 standardizes a decision boundary; Professional Eligibility owns the professional-specific decision.
8. **Source projection:** SH-094 provides deterministic projection conventions; Professional Eligibility owns its source-field allowlist. Search owns persisted index state.
9. **Privacy:** SH-095–098 provide protocol/mechanics; Professional Eligibility owns field meaning while Privacy owns the request, orchestration, and exemption record.
10. **Moderation enforcement:** SH-103 standardizes source-decision execution; Moderation owns the case/decision, Professional Eligibility owns the target transition.
11. **Audit:** SH-029 stores generic proof; the profile lifecycle remains `ProfessionalProfile.status` plus its domain events.
12. **Observability:** shared logs/failures/queue telemetry describe execution, never seller eligibility truth.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

- every end-user/admin protected entry point resolves SH-001 `resolveAuthenticatedActor`;
- workers and internal event handlers use an approved system/service actor context rather than fabricating an end-user identity;
- the base `User` account is not automatically the ProfessionalProfile seller actor.

### Role / Authority use

SH-002 `authorizeResourceAction` is invoked for profile mutations and restricted reads. Professional Eligibility supplies only the resource relationship facts necessary to decide:

- is the actor the User attached to this ProfessionalProfile?
- is this an approved platform/admin/support action?
- which named Professional Eligibility command/query is being attempted?
- is there an approved source decision/system capability for a moderation/privacy effect?

### Resource ownership

Ordinary self-service commands require the authenticated User to control the targeted ProfessionalProfile. Do not trust client-provided `userId` or profile ownership.

### Organization / participant context

ProfessionalProfile is User-scoped seller identity. Organization membership is not a generic bypass for professional actions. If a future organization-managed professional workflow is introduced, it requires an explicit authority contract rather than reusing OrganizationRole implicitly.

### Admin / support actions

- admin/support status alone does not authorize arbitrary lifecycle mutation;
- source-sensitive actions such as moderation enforcement require the validated source decision/effect and authority;
- support tools should receive safe profile/readiness context, not raw Trust/Healthcare/Payment evidence;
- manual override semantics are **Unresolved** unless a source Module provides an approved decision/override path.

### Step-up

No current evidence establishes mandatory step-up for ordinary professional profile management or readiness queries. This Module must not invent a local MFA flow. If root security later classifies an admin/profile action as sensitive, invoke Identity's SH-014 rather than implementing step-up here.

---

## 19. Compliance / Readiness / Entitlement Gates

Professional Eligibility owns only the **composition** of gates for its professional actions.

| Professional action | Underlying truth owners | Queries consumed | Local composition policy | Result |
| --- | --- | --- | --- | --- |
| Create/edit draft profile | Identity, Authority, local profile invariants; entitlement only if later product policy explicitly gates drafting | SH-001/002; optional SH-005 if approved | drafting must not require full verification/healthcare/KYC merely because later actions do | mutation allow/deny; no seller-readiness claim |
| Activate profile | Professional Eligibility + Track + Taxonomy + Trust + Healthcare + Hold; financial timing unresolved | SH-005, 011, 017/018, 020, 022; SH-019 only after policy approval | compose required dimensions for `activate_profile`; never use summary booleans | SH-016 decision, then owner lifecycle command if allow |
| Public professional visibility | Professional Eligibility plus the source/compliance dimensions explicitly approved for public surface | SH-024 over local status/readiness; source owners as required | public display policy is separate from generic `active`; protect sensitive reason detail | public readiness decision + source projection eligibility |
| Publish Offering | Marketplace owns Offering-local checks; Professional Eligibility owns seller gate; Track/Trust/Healthcare/Hold and possibly Payment supply dimensions | Marketplace context + SH-005/011/017/018/020/022; SH-019 timing per U-01 | return `publish_offering` seller decision; Marketplace alone publishes | SH-016 decision |
| Respond to Gig | Gig owns Gig requirements/context; Professional Eligibility owns seller gate; Trust/Healthcare/Hold/Entitlement apply when triggered | Gig context + SH-005/011/017/018/020/022; SH-019 timing per U-01 | return `respond_to_gig`; do not create GigResponse | SH-016 decision |
| Participate seller-side in Order | Order owns transaction context; Professional Eligibility owns seller operational gate; financial execution remains Payment | Order context + approved current gate interfaces | ensure seller profile can perform requested participation without taking Order/payment truth | SH-016 decision |
| Request/receive payout | Payment / Payout / Tax | SH-019 and Payment's own payout command path | **not a Professional Eligibility-owned action**; this Module may be a consumer/source identity only | Payment decision/execution |

### Gate ordering

A recommended safe evaluation order is:

```text
valid target / profile exists
→ caller authorized to ask
→ profile lifecycle dimension
→ entitlement
→ ComplianceHold
→ taxonomy-triggered requirements
→ Trust when required
→ Healthcare when required
→ Payment only when the action policy explicitly requires a financial dimension
→ normalize reasons + public-safe evidence
```

Ordering is an implementation optimization and security measure; it must not change the semantic result. Evaluation may stop early only when doing so does not hide useful safe remediation or leak sensitive existence information.

### U-01 financial timing

The Cluster explicitly leaves unresolved whether full KYC/tax/payout-account readiness is required before activation, Offering publication, Gig response, or only later money actions. Professional Eligibility must return a stable policy-unresolved/review result for an action whose required financial dimension has not been approved rather than guessing.

---

## 20. Provider Integrations

Professional Eligibility owns **no provider integration** in the current architecture.

### Evidence conflict resolved

The older Deep Module Registry lists technologies such as Stripe Connect, Stripe Identity/Persona, tax providers, and a webhook processor under Professional Eligibility. That technology list conflicts with the stronger current CL-03 ownership model and Canonical Shared Operations boundary: Payment owns KYC/tax/payout provider integrations, Trust owns screening/license providers, Healthcare owns BAA/regulated-service provider integrations, and Search owns its provider. The technology list is therefore treated as historical/adjacency evidence, **not** as permission to place provider clients or webhook truth in Professional Eligibility.

Therefore this Module must not contain:

- Stripe / Stripe Connect / Stripe Tax clients or webhooks;
- Checkr, Certn, license verification, background-screening clients/webhooks;
- healthcare BAA/e-sign provider clients/webhooks;
- Typesense clients;
- email/SMS/push provider clients;
- provider credentials/secrets;
- provider-event dedupe tables;
- provider status translation logic;
- provider reconciliation workers.

It consumes normalized source-owner interfaces and domain events after those provider owners have verified, deduplicated, translated, and persisted provider effects.

A provider failure that reaches Professional Eligibility is represented only as an owner decision unavailable/retryable condition or a safe source-domain status. Raw provider errors are never exposed to consumers.

---

## 21. Events and Outbox

### Module-owned event families

#### `ProfessionalProfileCreated`

Emitted after the one authoritative ProfessionalProfile record is successfully created.

Minimum payload principles:

- profile ID;
- User ID only if consumer contract genuinely requires it and disclosure is approved;
- lifecycle status;
- source/aggregate version metadata available under root standard;
- occurredAt;
- correlation/request ID;
- no bio/contact/payment/verification/healthcare payload dump.

#### `ProfessionalProfileStatusChanged`

Emitted after a successful status transition.

Minimum payload principles:

- profile ID;
- previous status;
- new status;
- transition reason category;
- source decision reference when the transition executes external moderation/hold policy;
- occurredAt;
- aggregate/source version;
- correlation ID.

### Projection-relevant field updates

A separate update event should be added only if a concrete consumer requires it. Search refresh may also be requested transactionally/outbox-backed as a downstream effect without creating a broad “profile changed” event containing arbitrary fields.

### Readiness events

Because readiness is evaluated from current owner truth rather than stored as a Professional Eligibility aggregate, the Module must not claim that `ProfessionalReadinessChanged` is a fact unless it has a defined prior/current comparison contract. **Proposed Ruling PE-PR-08:** dependency events should trigger current reevaluation and affected Search refresh/notification without introducing a readiness source record or false “changed” event.

### Transactional outbox

Use SH-046. The owner state write and required outbox append commit atomically. Do not emit after write with best-effort process memory.

### Payload minimization

Events contain IDs, controlled enums/reason classes, source versions, and safe correlation references. They do not carry raw verification reports, healthcare detail, tax/KYC state, provider payloads, or hidden hold notes.

### Consumer idempotency

Consumers must deduplicate events through SH-045. A replay must not duplicate Search requests, notifications, or downstream lifecycle effects.

### Events are facts, not disguised commands

`ProfessionalProfileStatusChanged` says what occurred. A command such as “suspend this Offering” belongs to the target owner's public interface, not an event name masquerading as cross-Module imperative control.

---

## 22. Background Jobs / Scheduled Work

### 22.1 `professional-readiness-reevaluation` worker

**Purpose:** react to relevant dependency-source events and reevaluate only the affected ProfessionalProfile action/public-readiness context.

**Typical input sources:** Trust verification/credential changes, Healthcare readiness/BAA changes, entitlement changes, hold changes, taxonomy requirement changes, and Payment readiness changes when the affected action's policy uses financial readiness.

**Owner:** Professional Eligibility owns the reevaluation business logic; shared platform owns queue leasing/retry/dead-letter mechanics.

**Input:** source event ID/version, source owner/type, affected ProfessionalProfile ID or resolvable target reference, correlation ID, handler version.

**Idempotency key:** source event ID + handler/version + affected professional target, through SH-045/047.

**Retryable failures:** temporary owner-interface outage, Search/Notification request outage, transient DB/network failure.

**Permanent failures:** malformed/unsupported event version, target definitively not owned/not found after approved tombstone handling, invalid source contract. Permanent failures are recorded operationally and do not mutate seller truth to “safe looking” state.

**Dead-letter / manual review:** retry exhaustion becomes queue/ops-visible through shared mechanisms; no local `failedReadiness` status is added.

**Business truth updated:** ordinarily none. The worker computes current readiness and may request Search refresh/Notification. An automatic ProfessionalProfile lifecycle transition after a dependency loss is **not approved** unless a specific local policy ruling establishes it.

**Operational telemetry:** safe source event ID, profile ID, handler version, duration/result category, retry count, dependency name, correlation ID. No raw source-owner sensitive payloads.

### 22.2 Scheduled work

No Module-owned periodic cron/scheduler is currently required. Trust/Healthcare/Payment own their own expiry/provider reconciliation jobs. Professional Eligibility reacts to their normalized events.

A future reconciliation/backfill of public-readiness projection may use the shared job framework, but Search remains projection owner and the Module must rebuild from ProfessionalProfile/current owner decisions, not from Search state.

---

## 23. Concurrency and Idempotency

### Races to prevent

1. simultaneous ProfessionalProfile creation for one User;
2. simultaneous slug assignment/update;
3. profile activation versus moderation suspension;
4. pause/resume versus archive;
5. stale profile edit overwriting newer lifecycle/projection-relevant fields;
6. duplicate moderation decision execution;
7. duplicate Privacy instruction execution;
8. duplicate/out-of-order dependency events causing repeated Search/Notification effects;
9. readiness result evaluated against stale target context during a foreign Module mutation.

### Aggregate / resource key

Primary aggregate lock/CAS key: `ProfessionalProfile.id`. Provisioning additionally conflicts on `User.id`; slug uniqueness conflicts on canonical slug value.

### Database constraints

- unique `ProfessionalProfile.userId`;
- unique `ProfessionalProfile.slug`;
- foreign-key integrity as established by Prisma;
- additional constraints only through approved schema changes.

### Transaction boundary

For a profile mutation, one transaction must cover:

```text
load/lock or CAS current ProfessionalProfile
→ validate current state and source decision/readiness preconditions
→ write owner state
→ append required transactional outbox record
→ commit
```

Audit/Search/Notification effects may be requested through outbox/reliable jobs when they cannot safely participate in the database transaction.

### Lock / optimistic strategy

The root-approved shared primitives are SH-051 and SH-052. Current schema lacks an explicit aggregate version field.

**Proposed implementation direction:**

- use expected current status for lifecycle commands;
- use an expected `updatedAt`/root-approved concurrency token for general edits if root standards allow;
- use DB row locking for races where source-decision execution must serialize;
- do not add a new `version` column without an approved migration/architecture decision.

Exact choice is PE-U06.

### Command idempotency

Use SH-044 for creation and replay-prone lifecycle/admin/privacy commands. Semantic fingerprint must include target, command type, source decision/version where applicable, and material requested state.

### Replay result

- exact replay returns the original successful result or an equivalent canonical current result;
- same idempotency key with different semantic input returns deterministic conflict;
- duplicate source event does not repeat Search/Notification/lifecycle effects;
- stale command never overwrites a newer source transition.

---

## 24. Media / Storage

Professional Eligibility currently owns no file/media mechanics and no provider storage.

`ProfessionalProfile` may be related to profile media in the wider schema, but the target registry does not establish `ProfessionalProfileMedia` as this Module's owned schema. Therefore this Module plan does not introduce a profile-media lifecycle.

If future profile media is implemented:

- Media / File Access owns `MediaAsset`, upload policy/session, file validation/scanning/processing, private storage, signed URLs, access grants, and file deletion mechanics;
- the owning contextual Module must be explicitly established before creating a profile-media join command here;
- Professional Eligibility may contribute profile ownership/readiness context but must not write object storage or issue signed URLs;
- sensitive verification/license/BAA documents remain Trust/Healthcare + Media concerns, not Professional Eligibility attachments.

No media worker, bucket, scan service, presigned URL helper, or public file URL is permitted in this Module.

---

## 25. Search / Projection

### Source truth

`ProfessionalProfile` is seller identity/lifecycle truth. Search is derived.

### Module-owned source projection

Professional Eligibility implements SH-094 for an allowlisted ProfessionalProfile source projection. The projection must be deterministic from source facts and current professional public-readiness policy.

The public projection must not automatically serialize the Prisma model. At minimum it must exclude:

- `userId` unless an explicitly approved Search contract needs a public-safe actor reference;
- `stripeAccountId`, `stripeReady`;
- KYC/tax/payout state;
- raw Trust/verification/credential state;
- healthcare/BAA internals;
- ComplianceHold details;
- moderation case details;
- provider references;
- private/audit/ops metadata.

Review-derived rating fields may be included only as approved rebuildable public projections, not as Professional Eligibility source truth.

### Search-owned projection

Search / Public Visibility owns:

- `SearchUpsertEvent`;
- Typesense collection/schema/document lifecycle;
- index worker/backfill/reconcile;
- search query/ranking/facets;
- de-index/re-index execution.

### Indexing triggers

Professional Eligibility should request SH-091 refresh/remove/restore after:

- relevant ProfessionalProfile lifecycle changes;
- public projection field changes;
- privacy/moderation effects that change public display;
- dependency events that may change professional public readiness.

A dependency-driven reevaluation may safely request refresh even if the outcome did not materially change; Search can idempotently reconcile current source projection. This avoids inventing a readiness source record solely to detect deltas.

### Visibility / readiness / privacy conditions

Search must receive an owner-issued public-readiness result/source version. Search must not reconstruct eligibility from `ProfileStatus`, TrustBadge, or copied flags alone.

Privacy or moderation Search removal is a projection effect; it is not deletion of `ProfessionalProfile` source truth.

### Search outage behavior

If a committed profile transition requires a Search refresh and Search is unavailable, retry the projection request through reliable async infrastructure. Do not roll back the authoritative profile transition solely because Search is temporarily unavailable.

---

## 26. Notification

Professional Eligibility defines **business triggers and safe intent**, not delivery mechanics.

Potential notification triggers, subject to product policy:

- profile activated;
- profile paused;
- profile suspended because an approved source decision was executed;
- profile reinstated;
- profile archived;
- a readiness reevaluation exposes a new remediation category that product policy says should alert the professional.

Safe payload intent:

- ProfessionalProfile ID;
- lifecycle state or safe remediation category;
- source workflow reference only if the recipient is entitled to it;
- template key/version;
- safe deep-link target;
- correlation ID.

Never include raw background-screening findings, PHI, tax/KYC details, payout provider errors, or private moderation notes in a generic notification request.

Use SH-041. Notification delivery failure does not roll back ProfessionalProfile source truth; retry/ops visibility belongs to Notification/shared queue infrastructure.

---

## 27. Audit and Sensitive Access

### Domain event / lifecycle truth

`ProfessionalProfile.status` plus versioned ProfessionalProfile domain events describe the business lifecycle. A future dedicated owner event ledger would require explicit approval.

### Generic `AuditEvent`

Use SH-029 for high-impact evidence such as:

- activation;
- suspension/reinstatement;
- archive;
- privileged admin lifecycle action;
- execution of an external moderation decision;
- approved override if overrides are ever introduced.

Audit metadata must include only safe actor/action/target/outcome/source-decision IDs and correlation context.

### `AccessAuditLog`

Ordinary public profile reads and standard readiness responses do not automatically require sensitive-access logging. Trust, Healthcare, and Payment own sensitive evidence and should record access at their boundaries.

If Professional Eligibility later exposes a restricted admin query containing protected readiness evidence, use SH-030 according to sensitivity policy; do not create a custom access log.

### Distinctions that must remain explicit

- `AuditEvent` ≠ ProfessionalProfile lifecycle truth;
- `AuditEvent` ≠ domain-event outbox;
- `AccessAuditLog` ≠ authorization;
- `IntegrationFailure`/logs ≠ eligibility decision;
- Search history ≠ lifecycle proof.

---

## 28. Privacy and Retention

Privacy / Data Erasure owns request intake, identity verification for privacy requests, orchestration, export bundles, erasure jobs, target status, and retention exemptions.

Professional Eligibility contributes a data-owner executor.

### Subject-data inventory

At minimum enumerate:

- `ProfessionalProfile` record ID;
- owner User reference;
- profile copy fields (`slug`, `headline`, `bio`, `websiteUrl`);
- location profile fields (`city`, `state`, `country`);
- lifecycle status/timestamps;
- compatibility/derived fields that physically reside on the row;
- references to dependent owner records only as relationship identifiers necessary for Privacy orchestration, not as data this Module erases directly;
- Search projection target reference so Privacy can coordinate projection removal through Search.

### Erase / anonymize / revoke / retain behavior

- archive is not legal erasure;
- erase/anonymize only under SH-095 instruction and approved retention decision;
- use SH-098 for deterministic anonymization mechanics where appropriate;
- do not directly erase Trust, Healthcare, Payment, Order, Review, Gig, Offering, Search, Audit, or Media records;
- preserve structural ProfessionalProfile linkage when legally retained commercial/compliance records require it and Privacy records the appropriate exemption/decision;
- request Search removal after source privacy effects;
- do not rely on raw cascade deletion from `User` as the legal privacy workflow.

### Records requiring retention analysis

ProfessionalProfile is referenced by Orders, payout/tax records, verification, healthcare, holds, reviews, disputes, and other potentially retained records. Exact retention duration and whether IDs/status metadata must remain are not established in the supplied evidence.

### Provider resources

None are owned here. Privacy must dispatch provider-resource deletion to the actual provider-owning Module where allowed.

### Export contribution

SH-096 can provide Professional Eligibility-owned profile data to Privacy's export process. Privacy owns final bundle assembly and delivery.

### Destructive-path rule

If retention/legal disposition is unresolved, do not hard-delete. Return a blocked/review/retention-required execution result to Privacy rather than guessing.

---

## 29. Observability

### Structured logs

Use root/Observability logging with safe fields such as:

- operation name;
- ProfessionalProfile ID;
- professional action key;
- decision class;
- normalized reason category count, not raw sensitive evidence;
- dependency name and safe result class;
- duration;
- request/correlation ID;
- event/job ID;
- retry/attempt number;
- lifecycle previous/new status for safe owner transitions.

### Safe dimensions

Useful metrics may include:

- profile create/update/transition success/conflict counts;
- readiness decision counts by action and high-level decision category;
- dependency-unavailable rate by owner Module;
- reevaluation job latency/retry/dead-letter counts;
- Search refresh request failures;
- stale transition conflicts.

Do not use high-cardinality raw personal data or sensitive source reason text as metric dimensions.

### `IntegrationFailure` / `SystemEvent`

Use Observability-owned operational records for dependency/downstream technical failures. They do not change profile/readiness truth.

### Request / correlation IDs

Propagate correlation context through source-owner calls, jobs, outbox events, audit requests, Search requests, and Notification requests.

### Redaction

Use SH-034. Never log:

- raw screening reports or license numbers;
- PHI/BAA data;
- KYC/tax identifiers;
- payout/payment credentials;
- raw provider payloads;
- private moderation notes;
- secrets/tokens;
- arbitrary serialized dependency DTOs.

### Health checks

This Module does not need a provider-specific health endpoint. Platform/Observability may expose service-level health. Readiness dependency degradation should be measurable through dependency call outcomes and queue telemetry.

---

## 30. Security Boundaries

1. Validate every command/query boundary with the root-approved runtime schema validator; TypeScript types alone are not trust-boundary validation.
2. Resolve actor and authorization server-side; client ownership claims are untrusted.
3. Never accept a client-provided readiness boolean, verification result, healthcare result, financial result, entitlement, hold-clearance flag, or Search visibility flag as proof.
4. Use owner-source contracts and source versions for target context.
5. Prevent confused-deputy behavior: a consumer may ask for readiness only for a target/action it is authorized to reference.
6. Minimize decision details by caller context; unauthorized callers must not learn whether a user has a background check, healthcare lane, tax restriction, or private hold.
7. Do not store provider credentials, webhooks, raw identity documents, PHI, tax IDs, or payment credentials here.
8. Do not introduce local encryption/key management. Use root/shared primitives when approved data handling requires them.
9. Do not expose `userId` or foreign compliance relations through public Search DTOs by default.
10. Use database uniqueness/CAS/locks, not frontend sequencing, for race safety.
11. Use platform rate limiting/abuse controls at the appropriate boundary if readiness queries become abuse-sensitive; do not build a second module-local rate-limiter infrastructure.
12. Privacy/system workers use constrained service capabilities and typed target instructions.
13. External moderation decisions must be validated by source ID/version/target before a local transition.
14. Safe error responses do not leak provider or sensitive source-owner error text.

---

## 31. Error / Decision Result Pattern

### Command/query error categories

Public interfaces should normalize errors into stable categories rather than leak Prisma/provider/internal exceptions:

- `UNAUTHENTICATED`
- `FORBIDDEN`
- `VALIDATION_ERROR`
- `NOT_FOUND`
- `CONFLICT`
- `POLICY_UNRESOLVED`
- `DEPENDENCY_UNAVAILABLE`
- `RETRYABLE_FAILURE`
- `INTERNAL_FAILURE`

### Readiness decision categories

Owner-specific v1 decision shape should distinguish:

- `allow` — all currently required professional dimensions passed;
- `deny` — deterministic blocking policy/source truth exists;
- `review` — manual/policy review is required or a source owner returned review;
- `unavailable` — required current truth cannot be established safely or the policy is unresolved.

### Reason-code principles

Reason codes are:

- controlled by Professional Eligibility for its decision surface;
- stable enough for consumers to map remediation UX;
- namespaced by semantic domain rather than provider;
- safe for the authorized audience;
- allowed to carry source evidence IDs/versions but not raw evidence.

Illustrative categories, not yet the frozen code catalog:

- `profile.not_active`
- `profile.archived`
- `profile.transition_conflict`
- `entitlement.missing`
- `hold.blocking`
- `verification.not_ready`
- `healthcare.not_ready`
- `financial.not_ready`
- `financial.policy_unresolved`
- `target.invalid_or_stale`
- `dependency.unavailable`
- `policy.unresolved`

### Provider errors

Provider-specific errors never cross this interface directly because this Module owns no providers. Source-owner modules translate them before Professional Eligibility sees the result.

---

## 32. Testing Architecture

### Domain unit tests

- profile mutable-field policy;
- status/action lifecycle dimension;
- action-to-gate matrix;
- dependency result composition;
- reason normalization and audience redaction;
- public-readiness policy;
- source-projection allowlist;
- moderation effect mapping;
- privacy field mapping.

### State-transition tests

- every approved transition and prohibited adjacency;
- current-state precondition;
- activation/resume readiness gating;
- suspension/restoration source-decision requirements;
- archived behavior;
- stale/concurrent transition rejection.

### Public contract tests

- `getProfessionalProfileContext` field minimization;
- SH-016 request/action/result versioning;
- SH-024 public-readiness result;
- SH-094 projection schema;
- privacy executor protocol;
- event payload compatibility.

### Database / integration tests

- one profile per User under concurrent create;
- slug uniqueness;
- owner-only writes;
- CAS/lock transaction behavior;
- outbox atomicity;
- no direct writes to foreign owner tables;
- compatibility fields never satisfy gates.

### Authorization tests

- owner;
- other authenticated User;
- admin/support permitted and non-permitted cases;
- system actor for moderation/privacy/event handlers;
- no client-supplied ownership bypass.

### Compliance tests

- TrustBadge cannot satisfy verification by itself;
- `stripeReady` cannot satisfy financial readiness;
- healthcare flag/summary cannot replace SH-020;
- active profile does not bypass action-specific gates;
- unresolved U-01 path fails non-allow;
- hold use goes through SH-011;
- sensitive reason redaction.

### Idempotency / concurrency tests

- simultaneous profile provision;
- repeated idempotency key with same/different input;
- activate/resume versus suspend;
- archive versus edit;
- duplicate moderation decision;
- duplicate Privacy instruction;
- duplicate/out-of-order dependency events.

### Provider adapter tests

None inside this Module. Contract tests should simulate normalized Trust/Healthcare/Payment owner responses, including provider-degraded states.

### Privacy tests

- inventory completeness for owned fields;
- archive ≠ erasure;
- anonymization mapping;
- retention-required path;
- no foreign record deletion;
- Search removal request after approved privacy effect;
- replay/partial failure behavior.

### Search/projection tests

- allowlisted source DTO only;
- private/financial/healthcare/verification/hold fields absent;
- public-readiness deny causes remove/hide request, not source deletion;
- Search outage does not corrupt profile truth;
- backfill can rebuild from source truth/current owner decisions.

### E2E participation tests

At Cluster integration stage:

- User creates ProfessionalProfile;
- blocked readiness exposes safe remediation;
- dependencies become ready;
- `publish_offering` or `respond_to_gig` decision changes accordingly;
- action owner mutates its own lifecycle;
- Search public profile refresh follows owner public-readiness;
- hold/moderation/privacy change produces correct non-duplicated effects.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. A `User` does not sell directly; seller activity is anchored to a `ProfessionalProfile`.
2. One User may have at most one `ProfessionalProfile` under the current model.
3. Professional Eligibility is the only ordinary writer of `ProfessionalProfile.status`.
4. No public `setProfessionalStatus(status)` bypass may exist.
5. `ProfileStatus.active` is not a universal `canSell` truth.
6. Professional readiness is action-specific and current-state based.
7. No authoritative `canSell`, `isVerified`, `isHealthcareProvider`, `stripeReady`, `canPayout`, or `professionalBlocked` shortcut may be introduced.
8. `ProfessionalProfile.stripeReady` and `stripeAccountId` never satisfy a gate.
9. `verifiedAt`, `verificationExpiresAt`, `trustScore`, and TrustBadge never replace Trust-owned verification truth.
10. `ratingAverage`/`ratingCount` never become verification or eligibility truth.
11. Trust, Healthcare, Payment, Entitlement, Taxonomy, Hold, Marketplace, Gig, Order, Search, Privacy, Audit, Notification, and Moderation source records remain externally owned.
12. Foreign Prisma relations do not authorize direct cross-Module writes.
13. SH-016 is the preferred professional action-readiness boundary; consumers must not rebuild its policy.
14. Required dependency failure cannot default to allow.
15. Unresolved policy cannot default to allow or silently choose a gate matrix.
16. Financial readiness is invoked for activation/publication/respond only after U-01 or successor policy explicitly settles that action.
17. Marketplace alone changes Offering lifecycle; Gig alone changes Gig/GigResponse lifecycle; Order alone changes Order lifecycle.
18. `ComplianceHold` remains the reusable stop sign; no local generic hold model/flag is created.
19. Moderation owns the source decision; this Module only executes the approved target effect.
20. Search is a projection; this Module never writes `SearchUpsertEvent` or calls Typesense directly.
21. Search removal is not source deletion.
22. Privacy owns request/orchestration/retention-exemption truth; archive is not erasure.
23. Audit and Ops records never replace ProfessionalProfile lifecycle or readiness source decisions.
24. This Module owns no external provider client, credential, webhook, dedupe ledger, or provider status translation.
25. Lifecycle changes and required outbox publication are transaction-safe.
26. Critical commands use canonical idempotency/concurrency primitives, not process memory.
27. A stale lifecycle command must return conflict rather than overwrite newer state.
28. Event consumers must be replay-safe and current-state-aware.
29. Public/readiness contracts expose only safe minimum fields and reason details.
30. No raw screening, PHI, tax/KYC, payout, moderation-note, or provider payload data enters logs/events/Search/Notification through this Module.
31. A future readiness cache is rebuildable projection only unless a new architecture ruling explicitly makes a snapshot authoritative proof.
32. CandidateProfile lifecycle remains outside Professional Eligibility even while `ProfileStatus` vocabulary is shared.

---

## 34. Prohibited Duplicate Implementations

Do not generate these or equivalent local responsibilities inside `professional-eligibility`:

| Prohibited helper/service/model pattern | Use instead |
| --- | --- |
| `professional-auth.ts`, `get-current-user.ts`, `seller-session.ts` | SH-001 Identity actor context |
| `seller-permission.ts`, `admin-guard.ts`, `can-edit-professional.ts` as a role engine | SH-002 Role / Authority; local code may only package owner facts |
| `seller-plan.service.ts`, `is-premium.ts`, `can-sell-plan.ts` | SH-005 Track entitlement |
| `professional-hold.ts`, `is-blocked.ts`, `compliance-blocker.ts`, local `blocked` field | SH-011 ComplianceHold |
| `is-verified.ts`, `professional-verification.service.ts`, TrustBadge gate | SH-017/018 Trust interfaces |
| `stripe-ready.ts`, `can-payout.ts`, `kyc-gate.ts`, `payout-readiness.ts` | SH-019 Payment interface |
| `is-healthcare-provider.ts`, `hipaa-gate.ts`, `baa-ready.ts` | SH-020 Healthcare interface |
| hardcoded high-risk category/tag arrays | SH-022 Taxonomy requirements |
| `ProfessionalReadiness` / `EligibilitySnapshot` / `CanSell` source table in MVP | current owner truth + SH-016; future snapshot only by architecture ruling |
| generic cluster-wide `ReadinessStatus` lifecycle | owner-specific action decision; source states remain separate |
| direct `offering.repository.ts`, `gig.repository.ts`, `order.repository.ts` in this Module | source-owner public context queries/contracts |
| `typesense.ts`, `professional-indexer.ts`, `search-upsert.repository.ts` | SH-091 + SH-094; Search owns execution |
| `professional-audit.ts` as generic audit storage | SH-029 Audit interface |
| `professional-access-log.ts` | SH-030 if sensitive access is introduced |
| `professional-notifier.ts` that calls SES/SMS/push | SH-041 Notification request |
| `idempotency.ts`, `once.ts`, local idempotency table | SH-044 |
| local `event-bus.ts` / best-effort emit-after-write | SH-046 transactional outbox |
| local `queue.ts`, `worker-jobs` source table, custom retry loop | SH-047/048 + Queue/Ops infrastructure |
| in-memory `profile-lock.ts` | SH-051/052 DB concurrency primitives |
| generic `lifecycle-engine.ts` that owns other Module graphs | SH-053 mechanics + local ProfessionalProfile policy only |
| `stripe-webhook.ts`, `checkr-webhook.ts`, `baa-webhook.ts`, `eligibility-webhook.ts` | provider-owning Modules; none belong here |
| generic `WebhookLog` or `ProcessedProviderEvent` in Professional Eligibility | provider owners' SH-060 truth |
| `professional-privacy-request.ts`, `profile-erasure-workflow.ts`, local retention exemption table | SH-095/096/097 Privacy protocol |
| local `ModerationCase`/`ProfessionalModerationDecision` truth | Moderation + SH-103 target execution |
| file upload, R2/S3, scan, presigned URL helpers | Media / File Access |
| mutable professional wallet/balance | Payment-owned ledger and payout system |

A thin adapter may wrap a canonical operation for dependency injection/testing, but it must preserve the canonical contract and must not create competing semantics or persistence.

---

## 35. Unresolved Decisions

| ID | Question | Why unresolved | Blocks / implementation behavior |
| --- | --- | --- | --- |
| **PE-U01** | When exactly must full financial readiness (KYC/tax/payout account) be satisfied for `activate_profile`, `publish_offering`, and `respond_to_gig` versus only receipt/payout? | CL-03 U-01 explicitly leaves timing unsettled. | Final action-to-gate matrix. Affected action returns policy-unresolved/non-allow until approved. |
| **PE-U02** | Final ownership/governance of shared `ProfileStatus` enum used by ProfessionalProfile and CandidateProfile. | Registry names Professional Eligibility; glossary says shared enum with separate lifecycle use. | Enum relocation/split only. Does not transfer Candidate lifecycle or block ProfessionalProfile status ownership. |
| **PE-U03** | Exact ProfessionalProfile legal transition adjacency, archive source states/reopen policy, and suspension reinstatement target. | Enum values and command families exist, but no complete transition table is supplied. | Lifecycle commands beyond creation/default must not enable unsupported transitions until feature-spec ruling is approved. |
| **PE-U04** | Should loss of a readiness dependency automatically transition an already-active profile, or only deny affected actions/public visibility? | Cluster architecture says action-specific readiness and warns against automatic mutation without owner policy. | Dependency-change worker must reevaluate/request projection refresh, not auto-transition, until settled. |
| **PE-U05** | Exact professional entitlement keys/values required for profile activation, public visibility, Offering publish, Gig response, and Order participation. | Commercial-policy truth exists, but concrete key mapping is not supplied here. | Gate mapping must use configured/approved keys; no invented string keys. |
| **PE-U06** | Exact aggregate concurrency token strategy for `ProfessionalProfile` (explicit version field vs `updatedAt`/status CAS vs row lock combinations). | Prisma has no version field; root code standard is not supplied. | Use root-approved SH-051/052 pattern; no schema addition or last-write-wins assumption without approval. |
| **PE-U07** | What exactly does `ProfessionalProfile.onboardingCompleteAt` mean and who sets it? | Field exists but current architecture rejects global readiness booleans and does not define this timestamp. | Do not gate actions or set it automatically until semantics are documented. |
| **PE-U08** | Final public ProfessionalProfile projection allowlist and location treatment, including whether additional Location Safety processing is required for any future precise location fields. | Search boundary is clear, exact field contract is not supplied. | Feature 03 must freeze a minimal allowlist before production indexing. |
| **PE-U09** | Exact privacy retention/anonymization behavior for ProfessionalProfile identity/status and relationships to retained Orders, tax, Trust, healthcare, disputes, and audit evidence. | Privacy ownership is clear; legal retention durations/dispositions are not. | Destructive erase paths remain blocked/review when retention is unresolved. |
| **PE-U10** | Is immutable historical proof of an eligibility decision required for any seller action? | CL-03 PR-10 says no new readiness source table in MVP; future legal/business evidence needs are not settled. | No eligibility snapshot source table now. Add only through a later architecture ruling. |
| **PE-U11** | Exact notification triggers and detail granularity for readiness/suspension/remediation. | Notification rail exists; product messaging policy not supplied. | Only lifecycle notifications explicitly approved in feature spec should be enabled. |
| **PE-U12** | Are any manual admin/support readiness overrides allowed, and if so which owner provides the source override decision? | Current architecture has holds/moderation/admin review but no universal eligibility override. | No generic `forceAllow` / `forceActive` path may be implemented. |
| **PE-U13** | Ownership and lifecycle of `ProfessionalProfileMedia` if profile media is brought into scope. | Prisma relation exists but target Module registry does not list the join as owned truth. | No profile-media command in this Module until owner is established. |

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Professional Eligibility owns `ProfessionalProfile` and its lifecycle.
2. A `User` cannot sell directly; ProfessionalProfile is seller actor truth.
3. Professional Eligibility owns professional action-readiness composition through SH-016.
4. Readiness is action-specific and composed from current source-owner truth.
5. Trust, Healthcare, Payment, Track Entitlement, Taxonomy, and ComplianceHold remain independent source owners.
6. Marketplace owns Offering lifecycle, Gig owns Gig/GigResponse lifecycle, and Order owns transaction lifecycle; Professional Eligibility only returns their seller gate.
7. Search is downstream projection; Professional Eligibility builds safe source input and requests refresh but never writes Search state/provider documents.
8. `stripeReady`, `stripeAccountId`, verification summary timestamps, `trustScore`, and ratings on ProfessionalProfile cannot become gate truth.
9. No authoritative ProfessionalReadiness/canSell source table is introduced in MVP.
10. Provider clients/webhooks/dedupe do not belong in this Module.
11. ComplianceHold remains the reusable stop sign; no local generic block state is introduced.
12. Privacy orchestrates; Professional Eligibility enumerates/executes only its owned data under typed instructions.
13. Moderation owns the source decision; Professional Eligibility owns only the target profile transition.
14. Audit/observability are evidence/diagnostics, not lifecycle or readiness truth.
15. Cross-Module collaboration uses public owner contracts/events rather than direct foreign repositories by default.
16. Canonical Shared Operations are consumed by permanent ID and must not be duplicated.

### Proposed Rulings carried by this Module

- **PE-PR-01:** keep shared `ProfileStatus` vocabulary for now; Professional Eligibility exclusively controls ProfessionalProfile transitions while Candidate owner controls CandidateProfile transitions.
- **PE-PR-02:** ProfessionalProfile compatibility fields remain non-authoritative and should be deprecated/migrated separately rather than used for gates.
- **PE-PR-03:** `ratingAverage`/`ratingCount` remain rebuildable Review projections only.
- **PE-PR-04:** readiness is evaluated from current owner truth; no persisted eligibility source table in MVP.
- **PE-PR-05:** initial SH-016 action vocabulary is limited to activation, public visibility, Offering publish, Gig response, and seller-side Order participation.
- **PE-PR-06:** `suspendedForModerationAt` is local provenance only after a validated external decision, never moderation truth.
- **PE-PR-07:** use root-approved SH-051/052 concurrency with expected current state; do not add a version column merely for convenience without approval.
- **PE-PR-08:** do not emit a source-truth `ProfessionalReadinessChanged` event until a comparison/snapshot contract exists; dependency events trigger current reevaluation and idempotent downstream refresh instead.
- **PE-PR-09:** Professional Eligibility owns the safe ProfessionalProfile source-projection builder; Search owns persistence/indexing.

### Decisions that remain unresolved

PE-U01 through PE-U13 remain non-implementable where they affect behavior. A numbered implementation feature must stop or constrain itself when one of these is a true prerequisite.

---

## 37. Coding-Agent Usage

Before implementing or changing Professional Eligibility, an agent must read, in an order appropriate to the repository:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md` / Canonical Shared Operations Registry;
5. `context/professional-supply-readiness/architecture.md`;
6. `context/professional-supply-readiness/build-plan.md`;
7. `context/professional_eligibility/module-architecture.md`;
8. `context/professional_eligibility/implementation-plan.md`;
9. the public-interface sections of every direct dependency touched by the feature, especially Identity, Role / Authority, Track Entitlement, Taxonomy, Trust, Healthcare, Payment, Hold, Marketplace, Gig, Order, Search, Privacy, Moderation, Audit, Notification, and Observability as applicable;
10. the current progress tracker.

The agent must then:

- identify the exact numbered Module feature being implemented;
- identify its linked CL-03 build-plan feature/milestone;
- confirm the prior Module exit gate passed;
- list every source record being read or written and its owner;
- map every shared operation to its canonical `SH-###` ID;
- inspect the Unresolved Decisions table for blockers;
- refuse direct foreign repository access unless an explicit approved architecture exception exists;
- produce the required feature implementation specification before coding;
- implement only that feature/slice;
- run required typecheck/lint/tests/migrations/build/contract checks;
- verify negative/failure/concurrency paths;
- update progress and affected public-interface documentation;
- update this architecture only when a binding architectural decision legitimately changes;
- record assumptions, disabled paths, unresolved risks, and exit-gate result.

A coding agent must never use convenience, an existing Prisma relation, or a legacy summary field as permission to silently redefine Module ownership.
