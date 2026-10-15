# Professional Eligibility Module Architecture

> **Module ID:** `professional_eligibility`  
> **Module name:** Professional Eligibility Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-architecture.md`

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

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

Root architecture and code standards are missing at the locations recorded in `context/context-map.md`. This document does not invent their repository conventions; apply authority by concern and preserve required unresolved prerequisites rather than substituting another artifact.

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

#### `ProfessionalProfileMedia`

**Approved CL-03-R020:** Professional Eligibility owns the contextual attachment lifecycle, attach/detach/reorder semantics, and authorization to associate a MediaAsset with a ProfessionalProfile. Media / File Access owns the referenced `MediaAsset`, validation, scanning, processing, storage, signed access, and generic validated-attachment mechanics. This ruling establishes ownership; it does not add a new implementation feature or speculative public interface.

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
- `ProfessionalProfileMedia` contextual attach/detach/reorder lifecycle and authorization (CL-03-R020);
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
- `ratingAverage` / `ratingCount` — Professional Eligibility persists derived results supplied by Review / Dispute; Review owns inclusion/calculation;
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
| Review / Dispute | review/dispute lifecycle and reputation truth | consume the approved CL-04-R005 Review aggregate and persist derived Profile rating fields | own review truth or use rating projection as eligibility proof |

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

- `ratingAverage`, `ratingCount` — rebuildable Review-derived projections persisted by Professional Eligibility under CL-04-R005;
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

**Approved reputation handoff (CL-04-R005):** Review / Dispute owns Review inclusion and aggregate calculation. It supplies its owner-issued reputation result/facts for a ProfessionalProfile through the explicit Module contract: target ProfessionalProfile ID, derived ratingAverage/ratingCount, and source/projection version evidence. Professional Eligibility consumes that result, owns writes to its `ProfessionalProfile.ratingAverage`/`ratingCount`, and supplies the resulting Professional projection to Search. Review / Dispute must not mutate the ProfessionalProfile repository. SH-115 supplies shared projection/version/replay mechanics, not Review policy or Profile ownership. Dependency failure leaves Review truth committed and projection work retryable; exact transport/API naming is not newly selected here.

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

**CL-03-R020 resolves PE-U13:** Professional Eligibility owns `ProfessionalProfileMedia` contextual attach/detach/reorder semantics and authorization. Media owns `MediaAsset` and all generic file mechanics; validated attachments reuse SH-090. Ownership approval alone does not schedule a new profile-media implementation feature or approve new public command signatures.

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
| **PE-U13 — RESOLVED by CL-03-R020** | Professional Eligibility owns `ProfessionalProfileMedia` attachment meaning/lifecycle and contextual authorization. | Media owns the referenced `MediaAsset` and generic file mechanics. | No new implementation feature is introduced merely by this ownership ruling. |

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

PE-U01 through PE-U12 remain non-implementable where they affect behavior. PE-U13 is resolved by CL-03-R020 as recorded above. A numbered implementation feature must stop or constrain itself when one of these is a true prerequisite.

---

## 37. Coding-Agent Usage

Before implementing or changing Professional Eligibility, an agent must read, in an order appropriate to the repository:

1. `context/project-overview-v3.md`;
2. root architecture (**missing**; see `context/context-map.md`);
3. root code standards (**missing**; see `context/context-map.md`);
4. `context/shared/shared-operations.md` / Canonical Shared Operations Registry;
5. `context/clusters/professional supply & readiness/professional-supply-readiness-architecture.md`;
6. `context/clusters/professional supply & readiness/professional-supply-readiness-build-plan.md`;
7. `context/clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-architecture.md`;
8. `context/clusters/professional supply & readiness/Professional Eligibility Module/professional-eligbility-module-implementation-plan.md`;
9. the public-interface sections of every direct dependency touched by the feature, especially Identity, Role / Authority, Track Entitlement, Taxonomy, Trust, Healthcare, Payment, Hold, Marketplace, Gig, Order, Search, Privacy, Moderation, Audit, Notification, and Observability as applicable;
10. the progress tracker (**missing**; see `context/context-map.md`).

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


## WA-R022 — Review and Dispute durable adjudication

Class: **AI_RESOLVED**.

New buyer Reviews bind the Order's authoritative CustomerProfile author and ProfessionalProfile target; User is authentication/audit identity. Review owns append-only revision/lifecycle evidence using SH-031, while the current Review record is its present state. This does not authorize user editing or a publication policy: those product choices remain explicit. Professional reputation consumes Review's versioned aggregate (ProfessionalProfile ID, rating sum/count or derived average/count, projection/source version); use an idempotent owner command/public contract, not direct profile writes. Exact transport name is implementation detail; older aggregate versions cannot overwrite newer ones.

Dispute owns immutable case events, adjudication decisions and workflow-step evidence: actor/authority proof, decision/reason/basis/time, amount/currency/basis where applicable, source Order version, semantic command identity and required Hold/Order settlement correlations. Mutable adminNotes is not adjudication or history. Keep authorized notes as append-only records with controlled reason codes and minimized text; corrections reference previous entries. Use an owner version token checked atomically on competing adjudications. Shared execution handles retries; Dispute records whether each required effect is pending, completed or failed.

`resolved_refund`/`resolved_release` represent the committed adjudication outcome, not completed financial movement. `closed` requires all required downstream outcomes confirmed/reconciled, or a durable authorized determination that none apply. Dismissal must state a controlled basis and require no outstanding effects before closure. A failed/refused/timed-out refund does not become closed success; retry/reconciliation stays visible. Financial effects go through Order/Payment and Hold owners with idempotent correlations. This resolves the proof/finality distinction without selecting eligible openers, case multiplicity, deadlines or appeal/reopen product policy.

Database migration must supply owner history and workflow evidence rather than extending generic Audit into a dispute ledger. Review/Event and Dispute/Event names are conceptual owner records, with exact models/FKs/indexes deferred until the coordinated database pass. Acceptance: mutually exclusive adjudications, audit versus domain-proof distinction, downstream timeout, duplicate refund result, stale reputation aggregate and reconstruction after restart.

Duplicate-collapse scope: CL04-U037/041/042/043/045; CL03-HD082; CL-04-R010 persistence strategy; review-author portion of CL-04-R007. Unnamed adjacent questions are not closed.


## WA-R024 — Financial readiness is action-specific

Class: **AI_RESOLVED_WITH_TRADEOFF** from the approved separation of Identity, optional screening, Professional readiness and financial execution. Preserve the existing Professional identity/KYC baseline; do not equate optional background screening with KYC. Payment's financial decision identifies the named action and the applicable KYC, tax, account and restriction dimensions, rather than exposing one timeless professional-is-financially-ready boolean.

Profile editing/drafting never requires payout readiness. Public activation/publication/Gig response uses the applicable Professional identity, Track, taxonomy/Trust/Healthcare and Hold policies; incomplete payout-account or tax setup alone is not a new universal nonfinancial block unless an explicit applicable requirement demands it. Paid acceptance/checkout must meet Payment's current charge/recipient capability for that flow; payout execution requires current recipient/account/KYC/tax/hold requirements. The purchaser cannot be charged through an unsupported recipient capability merely because a listing is visible. UI shows the owner-provided unavailable transaction state without leaking the seller's private KYC/tax details.

Tradeoff: discoverability and action readiness can differ; each attempted financial action re-evaluates current Payment facts. This avoids silently extending payout-only requirements to every public profile or treating a public listing as financial clearance. Provider/regulatory prerequisites may tighten the financial action and remain EXTERNAL_REQUIREMENT. No legal threshold, automatic KYC approval or alternative sponsorship flow is invented.

This resolves the universal-versus-action-specific architecture in CL03-HD001 / CL-03 U-01 / PE-U01 / Payment UD-01. Implement the action/dimension matrix and owner fixtures before activation; do not treat this as proof that the selected provider permits a particular charge/transfer. Existing settled optional screening and explicit free Track baselines remain binding.


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

## WA-R033 — Taxonomy semantics, history and AI proposal boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Taxonomy owns canonical term meaning and validation; contextual owners own accepted assignment joins. Join `verified` means an explicitly recorded authorized classification review, never Trust/KYC/Healthcare verification. Mere accepted attachment is not reviewed verification. Do not infer reviewed=true for legacy rows with unknown provenance; preserve them as unknown/unreviewed pending owner correction. Store reviewer/action/evidence/version when review is asserted. AI confidence is nullable integer basis points 0..10000 on the proposal, with model/prompt/output-schema/version provenance; it is model confidence, not calibrated correctness or authority. User/admin-authored assignments have no fabricated confidence. Accepted joins may retain a proposal reference and immutable provenance snapshot, but confidence never becomes a permission gate or competing current score. Legacy Float values are not auto-rescaled without proving their source scale. Candidate-authored tags use TagSource.user with CandidateProfile/User attribution; no new candidate source enum is required.

Adopt no normal hard-delete command for Domain/Category/Tag. Effective activity includes every ancestor's activity; ancestor reactivation does not rewrite child records. New assignments require effective-active terms. Historical accepted assignments retain term/version evidence even if the term later becomes inactive. Existing boolean active/inactive is sufficient for that lifecycle. A Tag must match the target's declared accepted Category at launch; multi-category assignment requires an explicit versioned compatibility policy, not arbitrary cross-category attachment. Parent IDs are immutable through ordinary edits. Exceptional reparent/merge runs require preflight affected-owner enumeration, compatibility review and controlled migration, never foreign join writes.

Persist immutable Taxonomy revisions/change records for labels, hierarchy, activity and represented compliance-trigger facts. Use stable term IDs and monotonically advancing owner revisions; updatedAt plus generic Audit is insufficient for historical interpretation. An alias points to exactly one stable canonical term within the same domain/type/locale normalization scope; alias cycles and conflicting normalized keys reject. Merge creates a durable from/to/version decision and alias/retirement mapping, preserves the source record, and requests each contextual owner to revalidate/repoint its own references with expected versions. Preserve original term/version in historical decision snapshots. Do not declare merge complete until required owner acknowledgments reconcile. No generic cross-owner migration service owns assignments.

Normalize term comparison keys using an explicitly versioned Unicode NFKC plus full case-fold and trimmed/collapsed Unicode whitespace; preserve punctuation and diacritics rather than conflating legally distinct terms. Include normalized locale and parent/type scope. Labels remain original display text. Alias registration is explicit, not automatic semantic synonym generation. Detect collision before creating or upgrading a normalization version; an algorithm change requires a dry-run collision report and owner migration. Slugs are owner-scoped stable public identifiers: use the shared primitive, uniqueness constraints and deterministic collision suffix; label edit does not silently rename an existing slug. Historical redirects/aliases are explicit owner records. Exact approved production seed content is an external reference-data requirement; no invented vocabulary is approved by this mechanism.

Additional license/background/location/Healthcare triggers use a versioned mapping owned by the interpreting requirement owner (Trust, Healthcare, Location or Job Compliance), keyed to Taxonomy term/revision and supported action/jurisdiction. Taxonomy supplies represented facts and change references, not clearance. Absent unsupported mappings do not imply readiness. DataSensitivity vocabulary follows Ubiquitous Language/compliance authority; source owners classify their own data and Healthcare separately owns explicit Healthcare boundaries. No generic scanner/AI inference can clear a sensitivity label.

Adopt the AI owner's two-record design: AiClassificationLog for a run and AiSuggestion for proposals, with append-only transition evidence. Run identity binds target owner/type/id/source version, allowed purpose, requester, model/prompt/normalization/output-schema versions and a semantic command identity. Keep queued→running→completed/failed/cancelled; queued may cancel. Cooperative cancellation prevents any late response from applying, even if provider work cannot be stopped; record late attempt outcome separately. Terminal runs never reopen; rerun is a new explicitly authorized run. Suggestions have unique run+candidateKey, exactly one value shape, and proposed→accepted/rejected/superseded/invalidated. Accepted requires a durable contextual-owner mutation receipt, never provider confidence or reviewer intent alone. Accepted/rejected dispositions are immutable; later assignment changes belong to the contextual owner.

Initial AI targets are ProfessionalProfile, Offering, Organization, Job and CandidateProfile; purposes are taxonomy_suggestion and skill_extraction. Gig AI is deferred because no bilateral target contract is established; ordinary Gig taxonomy assignment still works. Existing active canonical IDs only for taxonomy suggestions. Novel terms remain review-only and cannot be created by accepting an AI suggestion; independent authorized Taxonomy creation follows ordinary validation. Store logical term ID plus immutable term revision/label/path snapshot validated by Taxonomy; no cascading FK from proposal deletion into accepted truth. Keep normalized suggestions, validation result, canonical output hash and minimal provenance, not full raw provider bodies or source text. Provider/legal retention remains external; deleting AI evidence never deletes accepted assignments.

Use immutable code/config prompt versions with hashes at launch; no new database prompt publisher or first-class AiBackfill business model without a real additional lifecycle requirement. Bounded per-target runs and shared queue checkpoints suffice. Source adapters return purpose-limited normalized approved fields; Candidate supplies normalized skills/experience categories, never raw resume/application text at launch. Healthcare-sensitive transmission is disabled until source/Healthcare purpose-specific authorization and qualified provider/BAA evidence exist. No fallback model, region or logging change may silently widen the approved data boundary. Bedrock model/account/region/logging/retention configuration is external activation evidence, not selected by this architecture ruling.

Contextual owner commits accepted assignment and an immutable acceptance receipt/outbox fact atomically after fresh Taxonomy and source-version checks. AI consumes the receipt idempotently to record disposition; a timeout queries the contextual owner receipt rather than repeats the mutation with a new key. This is recoverable choreography over owner truth, not a generic CL-02 saga. Taxonomy admin composition may display proposal evidence and route assignment decisions through the actual context owner; shared review leases use WA-R031 and do not confer approval. No baseline AI→Search proposal feed or end-user classification notification. Broad backfill/configuration/merge and sensitive evidence exports require registered Role actions and fresh step-up under WA-R023/031; low confidence never creates a Hold by itself.

Required implementation checks: confidence source/range, unaudited verified claim, ancestor inactivity, normalization collision, alias cycle, stale assignment/term version, merge owner failure, late cancelled response, disposition-before-mutation rejection, duplicate acceptance receipt and raw/sensitive provider input rejection. Physical migrations, per-target DTO field allowlists, approved seeds, legal retention and provider capability are still separately qualified before activation.

## WA-R034 — Search work, protected transport and completion evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Search remains rebuildable projection. Source owners supply opaque currentness tokens, purpose-limited field allowlists and a currentness query; do not compare arbitrary tokens lexicographically or rely on wall-clock updatedAt alone. Search assigns a monotonic per-target work generation under a target lock and records all relevant source/visibility/Track/Location/Moderation evidence versions. Before writing and before exposing protected results, re-evaluate current source authorization and projection applicability. An older job cannot supersede a newer generation; deletion/restriction tombstones take precedence until current owner evidence explicitly permits publication again. Provider-native conditional writes are not assumed: adapters must prove their serialization/reconciliation behavior, and server query filtering prevents stale provider data from becoming an authority bypass.

Evolve SearchUpsertEvent into Search-owned durable work with request/command identity, typed target/source owner, expected tokens, generation, operation/purpose, pending/processing/completed/failed/superseded state, outcome and attempt/provider correlation. Shared queue leases/retries are separate. pending→processing; processing→completed/failed or pending for technical retry; stale work→superseded with successor correlation. Completed outcomes are upserted/removed/no_op/skipped with explicit reason and confirmed generation. A privacy removal cannot be marked completed from skipped/unavailable source facts. Same request/fingerprint replays the same work/result. Exact Prisma columns/indexes follow coordinated schema ownership, not a second queue.

All Search queries are server-mediated at launch, including public queries. No browser receives privileged or public Typesense credentials. Use independently versioned per-entity public collections with controlled alias cutover after full validated rebuild; protected Candidate collections/credentials are separate and never part of public federated queries or public counts/facets/autocomplete. Admin write credentials remain distinct from scoped server query credentials. Verify actual provider configuration/capabilities before activation; no current provider feature is presumed from these architectural requirements. Schema migration builds a new generation, validates completeness/currentness, then atomically changes the serving configuration; retain rollback generation without restoring revoked projections.

Protected Candidate search composes authenticated actor, current Organization membership/action authority, applicable Organization commercial permission, Candidate owner-approved searchable projection/visibility, applicable Hold/Moderation restrictions and field-level access policy. A result cannot imply permission to open a resume: resume access uses Candidate and Media separately. Search revalidates each returned Candidate's current projection/permission before disclosure; deny/unavailable removes that result rather than returns stale sensitive fields. Suppress provider totals/facets that expose filtered protected populations. Record one durable access batch proof before each protected response with requesting actor/Org/purpose, query fingerprint, permitted result target/version references and outcome; do not log raw sensitive query text. Resume/detail access produces its own required proof. If mandatory proof cannot commit, withhold the response under WA-R023.

Public results also obey current source restrictions; query sanitization and bounded result sizes apply before provider access. Basic relevance plus a stable target-ID tie-breaker is the launch ranking baseline. Advanced trust/recency/featured weighting is deferred versioned tuning, not a new premium benefit. Candidate's approved subscription boost follows WA-R030 (1.15 after eligibility, non-metered); it never changes privacy/eligibility. Generic User and CustomerProfile public indexing stay disabled; reserved enum values do not authorize publication. Search receives accepted source facts only, not raw AI suggestions or AI diagnostic history.

Source enumeration uses opaque stable cursors, snapshot/high-watermark identity, target/source token and explicit end-of-snapshot completeness. Each contextual owner enumerates its own records/joins. Incremental iteration cannot prove an unobserved target is deleted. Orphan removal requires a complete comparable source snapshot or an explicit owner deletion/tombstone receipt; cursor interruption never means empty source. Taxonomy changes request affected-owner enumeration and each source requests refresh through Search; neither Taxonomy nor Search scans foreign joins. Required per-target projection/AI/authority DTO field lists remain owner-specific and need bilateral qualification; the common mechanics do not approve arbitrary fields.

SH-091 returns accepted work identity, not completion. Search exposes a versioned completion receipt/query bound to request/work identity, typed target, requested generation/policy and verified outcome. Privacy/Moderation require removed/no_op-absent proof for their exact instruction; missing/timeout/provider uncertainty remains pending/unavailable. Receipt persists provider acknowledgement and reconciliation observation; tombstone prevents late stale jobs from resurrecting removed content. A superseded work receipt points to its successor, whose qualifying outcome is required before external fulfillment completes. Search never closes Privacy/Moderation's own workflow.

Start reconciliation/maintenance through authorized bounded manual commands; automatic cadence is versioned operational configuration added only with run budgets/coverage evidence. No periodic AI reclassification, end-user notification, query-history analytics store or speculative provider callback is implied. Per-action request/backfill/model cost limits use SH-132 and shared execution with explicit configured budgets and fail posture; never substitute Track commercial metering. No intrinsic Taxonomy cron or extra business-run table is required for normal maintenance. Operational telemetry is minimized and separate from domain completion evidence. Legal retention for subject-linked work/access receipts and actual provider configuration remain external requirements.

Required implementation checks: delayed stale upsert after deletion, provider write uncertainty, current-source denial at query time, protected collection isolation/totals, audit failure, incomplete enumeration, interrupted generation cutover, duplicate refresh, superseded removal receipt and consumer completion correlation. These contracts require adapter and bilateral fixture evidence before parallel-interface promotion; this architecture pass does not execute provider/schema/runtime tests.

## WA-R035 — Supply lifecycle, history and source projections

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

This ruling supersedes the proposed/unresolved lifecycle and projection alternatives named below; implementation still requires forward schema coverage and contract fixtures. Professional graph: create→draft; draft→active after current activation readiness; active→paused; paused→active after current readiness; draft/active/paused→suspended only by an authorized source restriction; draft/active/paused→archived by owner-authorized retirement. Archiving a suspended record may record retirement intent but cannot remove the restriction. Archived→draft is an explicit owner restore command, never implicit activation. Suspended→draft requires authorized release of all applicable restriction sources; subsequent activation rechecks readiness. Preserve previously acquired transactions and obligations. Ordinary dependency loss invalidates the affected action/public decision and requests reevaluation, not an automatic Profile status change. Only an explicit source policy may instruct suspension.

Offering graph: draft→active by publish; active→paused; paused→active by resume, each activation requiring current composed gates. Draft/active/paused may enter under_moderation/disabled_by_moderation/disabled_by_dmca only from a valid Moderation decision. Those restriction states may change to another restriction state only with a superseding valid decision. Restriction clearance restores to draft, preserving all other restriction sources; publication is a separate fresh command. Rejected→draft is an explicit correction/resubmission command after the rejecting owner permits it. Draft/active/paused/rejected→archived; archived→draft by explicit restore. Retirement never clears restrictions, destroys Order snapshots or grants a refund. An Offering kind can change in draft only before any Order, delivery or durable external reference; otherwise create a new Offering. isPublic is seller publication intent; effective visibility additionally requires active lifecycle, current SH-024 decision and no applicable restriction. Moderation timestamps are evidence, not independent allow flags.

Adopt immutable owner lifecycle histories for ProfessionalProfile and Offering, with aggregate version, prior/next state, command/source decision identity, actor, timestamp and policy/decision references. Mutations commit history and outbox atomically using expected opaque version plus row serialization for competing transitions; updatedAt alone is not the concurrency token. Publication/activation and seller Order acceptance retain immutable minimized gate decisions/source versions; current actions still reevaluate. Legacy financial/Trust columns remain non-authoritative compatibility projections until a measured reader inventory and forward migration remove them; never backfill authoritative readiness from a legacy boolean.

onboardingCompleteAt is the first successful owner activation after required onboarding facts pass, immutable except an audited data correction. It is not current readiness. ProfileCompleted.v1 may qualify one Gamification rule per profile and rule revision, containing profileId, subject User reference, firstCompletionAt, aggregateVersion, eventId; no raw onboarding facts. Gamification decides awards and source-event dedupe. Reinstatement does not emit another first completion. Dependency changes are owner outbox facts carrying target, changed dimension and source version; Professional/Supply consume idempotently and reevaluate current truth. Do not propagate a copied allow decision indefinitely. Booking availability is not an eligibility prerequisite; a public availability presentation uses Booking's separately authorized query and never changes Professional status.

Public Professional projection allowlist: professionalProfileId, slug, display name, approved biography, accepted active taxonomy IDs/labels/revisions, owner-supplied public avatar rendition reference, Review-owned ratingAverage/ratingCount with reputation version, and SH-131 fuzzy public location when allowed. Public Offering projection: offeringId, professionalProfileId, slug, title, approved summary, kind, accepted taxonomy IDs/labels/revisions, current public pricing summary/currency, approved public rendition references and public delivery/location mode. Each includes sourceVersion and current public-readiness evidence. Exclude User IDs, contact details, exact location, credential documents, provider refs, financial/Healthcare/hold reasons. Search must obtain URLs through approved Media/public rendition rules; no private original URL. Review→Professional transport is an outbox-triggered owner query getProfessionalReputation.v1 returning profileId, ratingAverage, ratingCount, projectionVersion, then a version-checked Professional projection command; stale events trigger current query rather than regress values.

priceFromCents is a rebuildable minimum of currently eligible active pricing options in one currency, not purchase truth. Missing or mixed-currency options produce no priceFrom value, never zero/implicit conversion. Orders bind the selected immutable price/package. isFeatured has no ranking or commercial effect at launch; promotion is deferred pending a separately approved owner policy. Heterogeneous bundle Offering creation remains disabled; this does not disable P02 multi-session packages within supported kinds. No new seller entitlement gates: supported effects remain approved Professional commission terms; unknown keys cannot gate drafting or fabricate quota. SH-016 action keys are activate_profile, public_visibility, publish_offering, respond_to_gig, participate_in_order; payout stays Payment-owned.

Owner status/remediation notifications use committed source-event identity, generic status/remediation template and safe authenticated destination; no sensitive provider/Healthcare/hold details. Notifications do not prove readiness. No generic admin force-ready override: each source owner must authorize and record its own correction, followed by reevaluation. Required verification includes stale-resume versus restriction, archive/restore preserving obligations, projection field exclusion, duplicate first-completion award, and reputation version replay. These are implementation acceptance criteria, not tests already executed.

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.

## WA-R037 — Payment effects, payout reservation and tax evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Payment owns immutable financial operation and attempt history, not just outbox delivery. Every effect has unique owner/sourceType/sourceId/sourceRevision/effectKind/effectOrdinal plus currency, semantic payload hash and original-effect reference for compensation. Reuse with different amount/subject/currency conflicts. Verified provider ingress receipt is separate from Payment and Track effect receipts; route by approved provider object/metadata ownership, never both owners applying the same business effect. Unknown routing is quarantined. Payment receipt fields: provider/account/eventId, eventType, fingerprint, handlerVersion, target operation, receivedAt, processing/attempt/recovery state and committed effect references. No raw secret payload by default; legal retention remains externally supplied.

Balance accounting uses immutable signed minor-unit effects with explicit bucket vectors and per-currency conservation. Earnings credit available (or pending until the approved availability rule); payout reservation moves available -A/reserved +A atomically with request acceptance; reservation release moves reserved -A/available +A only once after known cancellation/failure with no possible pending provider movement; successful payout moves reserved -A/paid +A. Transport retries have zero ledger effect. Provider return/reversal records its actual returned amount as a new linked effect, paid -R/available +R only after verified return and applicable financial restrictions; it never mutates the original payout. Fees/refunds/chargebacks are separate authorized signed effects, never hidden in payout status. Unknown money movement retains reservation and reconciles. Existing one-amount enum records are insufficient to infer these vectors: use an explicit owner allocation/bucket effect structure and forward constraints. This is accounting of processor-held value, not permission to introduce a wallet or new financial product.

At launch each PayoutTransfer belongs to one PayoutRequest; Order references are optional immutable allocation provenance, not a second transfer source. A request supplies an explicit validated active payoutAccountId; no guessed default among multiple accounts. Capture all blocking Hold IDs and decision versions in a separate immutable evaluation snapshot; blockedByHoldId is explanatory only. Reevaluate current holds/account/financial readiness immediately before dispatch. Keep one semantic transfer identity and stable provider idempotency key through network retries. Record each transport attempt separately. A terminal failed transfer never reopens; a new request/transfer after confirmed nonmovement and reservation release requires fresh authorization. Unknown is nonterminal even if transport timed out. No automatic retry of a terminal financially reversed/paid transfer.

Ratify the minimum Payment §9 graphs with these restrictions: KYC rejected/expired/disabled attempts are terminal; new attempt linked to previous evidence. TaxProfile rejected/expired creates a new collection revision, never overwrites submitted documents. One current applicable selector per subject+purpose+jurisdiction/provider scope points explicitly to the accepted evidence; pending new evidence does not silently replace valid current proof, while revocation immediately invalidates it. PayoutAccount disabled is terminal for that account; restriction recovery uses verified current provider evidence. PayoutRequest failed/cancelled/reversed terminal; processing cannot cancel without proven no movement. PayoutTransfer failed/cancelled/reversed terminal. SalesTaxCalculation changed quote requires a new calculation; finalized is immutable, voiding is a separately evidenced provider operation. Tax submission rejected/failed uses a new linked submission revision; transport retries of an unacknowledged submission retain semantic identity. Filed recipient correction creates replacement evidence and a link, preserving prior filing. No enum setter or provider callback bypasses these rules.

Tax subject is a Payment-owned stable subject reference mapped to an identified legal recipient, with explicit User and optional ProfessionalProfile provenance; profile identity is not automatically a separate legal taxpayer. Effective mappings/versioned evidence prevent accidental subject merge. Aggregate key is taxSubjectId + jurisdiction + taxYear + currency + reportingRegime; retain source owner/id/revision/recognition type and unique reversal identity. Prize-owned summaries use the same dimensions and preserve their own source valuation truth. SH-019 supports an explicit tax_fulfillment purpose and tax dimension; no second generic tax-readiness service is needed. Payment owns TaxReportingSubmissionStatus and TaxReportingRecipientStatus. Reporting bundle uniqueness includes regime/jurisdiction/year/currency/submission series/revision; recipients unique within submission by tax subject and applicable form/category. Rule versions, form requirements, recognition dates, thresholds and correction legality remain approved external configuration, never invented constants.

Order binds final calculation ID to exact immutable quote/order revision, currency, line IDs and buyer-tax-location evidence revision. Payment preserves line-level taxable basis, tax, jurisdiction, provider tax code and liability role even for mixed-liability lines. Tax-location provenance includes approved source owner, source/evidence revision, validation method/result and captured/effective time, minimum required location fields; it is not public-location consent. Each authorized refund has immutable line allocations against the original captured quantities/basis/tax and links its own provider refund and tax reversal attempts. Cumulative refunds cannot exceed captured refundable allocation; lock the operation allocation counters and reject mismatched currency. Use deterministic minor-unit residual allocation only within an approved tax/provider allocation policy; do not guess rates or liability. Partial/multiple refund representation requires separate child records, not one overwritten reversalId. Provider unsupported/ambiguous results stay pending/manual review, never fabricated successful tax reversal. Full provider/rule qualification remains external before affected execution.

Required verification: concurrent reservation conservation, duplicate callback/compensation, timeout followed by paid result, multiple holds, account changes before dispatch, line-level cumulative refund cap, subject/jurisdiction separation, replacement filing traceability. No live financial test or migration is claimed by this architecture decision.

## WA-R038 — Trust evidence provenance and screening boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

VerificationConsent remains a screening-context linkage: canonical ConsentLogId, identified User/subject, check type, provider, purpose, requirement/package revision and linked check. Generic acceptedAt/IP/user-agent fields are compatibility evidence only and cannot independently validate consent. New linkage requires canonical consent proof and current applicability checks; migration preserves unknown provenance without inventing consent. Each check has exactly one typed subject consistent with its User and optional Professional/Candidate profile; employer-requested screening additionally requires identified Organization/requester membership, Job/Application context, purpose and approved permissible-purpose evidence. Employer sponsorship is not activated by this technical representation.

Adopt the existing minimum Trust §9 check/package/badge graphs. Terminal checks never reopen; recheck is a new linked attempt with current consent/payment/requirement proof. License credential identity stays stable, but every verification/refresh/revocation creates an immutable evidence revision linked explicitly to its establishing VerificationCheck or authorized manual evidence decision. Current credential projection points to a valid revision; expired/revoked proof is never silently overwritten. Trust owns explicit check/credential-to-Media evidence join records, document kind, evidence revision and retention classification. Media owns bytes/scanning/access. No generic Media ownerType/ownerId joins are introduced.

Trust owns append-only check, credential, package/requirement and badge lifecycle histories with aggregate revision and source evidence, committed with outbox. Its provider effect receipt uses provider/account/eventId/handlerVersion uniqueness, fingerprint, check/credential target, normalized event kind, receivedAt, processing and attempt/recovery status, committed transition/effect refs. Unknown subject/events are quarantined; provider callbacks cannot mark a check passed from an unrecognized state. Short-lived provider report access is fetched on demand through an authorized adapter where supported. If persistence is necessary, reportToken is envelope-encrypted secret material with expiry/key version/rotation and restricted audited access; never public DTO/log/Search. Exact provider capability and retention remain external activation evidence.

Requirement rules are immutable schema-versioned records keyed to supported action, typed subject/target, jurisdiction and accepted classification revision; no free-form JSON policy or new implicit mandatory screening. Supported action vocabulary includes profile activation/publication, Offering publication, Gig response/acceptance, Order participation, Booking participation, Job application and Interview participation only where an explicitly approved requirement policy applies. Optional self-initiated Candidate/Professional screening remains optional; action enum presence does not mandate it. Single provider per package at launch; mixed-provider packages are deferred. Provider selection/check-type/jurisdiction rollout must be evidenced before activation, not inferred from a vendor enum.

Identity checks establish only their named verified identity claim; financial readiness stays Payment-owned; a healthcare credential check establishes that credential only, never BAA or Healthcare lane clearance. Broad platform_verified/gold_trust_check/healthcare_verified badges have no launch issuance or authorization effect without explicit scoped claim definitions; preserve legacy facts without minting misleading composite assurance. Public badge DTOs contain the approved claim label/type, subject profile reference, validity and evidence revision only. A badge never replaces current owner readiness.

FCRA technical evidence must link immutable notice template/version/content hash, identified recipient, approved purpose/check/report revision, delivery attempt and verified delivery outcome, policy/jurisdiction version, legally determined timing anchors, dispute submissions and outcome, final-action authorization and history. Notification delivery receipt is evidence, not a legal conclusion. Exact notice content, channels, required waits, adverse-action transitions and retention remain EXTERNAL_REQUIREMENT; no numeric windows or automated adverse decisions are approved here. Required tests cover consent-link mismatch, recheck history, expired supporting evidence, duplicate/late callback, secret exclusion and subject-context mismatch.


## WA-R066 — Finite Notification source and recipient contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-041 uses the following finite versioned semantic-intent/template registrations. These are architecture contracts, not implemented renderers, selected delivery vendors or proof of delivery. Sources emit an intent only after the corresponding durable owner transition. Every intent binds source owner, typed aggregate ID/revision, immutable semantic intent ID, template key/version, owner-resolved local User recipients, safe authenticated route, sensitivity and event kind. Notification owns channel consent, current endpoint generation, eligible delivery, attempts and receipts. Sources never ask Notification to scan foreign memberships or reconstruct business state.

| Intent/template | Committed source and recipients | Safe additional content |
| --- | --- | --- |
| message.new.v1 | Messaging messaging.message_created.v1; other currently eligible Thread participants selected by Messaging, excluding sender | Thread/Message references only; no message body or attachment URL |
| order.outcome.v1 | Order order.outcome_changed.v1; currently authorized Order participants selected by Order for its source kind | Safe operational outcome code and Order link; no financial consequence implied |
| booking.schedule.v1 | Booking confirmed/rescheduled/cancelled facts; currently authorized affected Booking participants | Safe change kind and authenticated schedule link; no exact address or meeting credential |
| interview.invitation.v1 | Interview invitation/current schedule revision; invited eligible Candidate and authorized Organization participants selected by Interview | Interview reference and safe proposed/scheduled kind |
| interview.schedule.v1 | Interview cancellation/reschedule/replacement; currently authorized affected participants selected by Interview | Safe change kind and authorized predecessor/successor references; no new removed-user notice |
| application.status.v1 | Candidate accepted_offer or withdrawn: current authorized hiring Organization recipients selected by Candidate through Hiring facts; Candidate rejected or hired: the application Candidate User | Application reference and exactly accepted_offer/withdrawn/rejected/hired change code; no view/stage alert or general Candidate exposure |
| privacy.verification_needed.v1 | Privacy durable request transition requiring verification; request subject through Privacy/Identity-authorized route | Request reference and safe action-needed code; no verification secret |
| privacy.outcome.v1 | Privacy accounted terminal outcome; currently authorized request subject/representative | Safe terminal category and link; no restricted exemption evidence or other parties' data |
| privacy.export_ready.v1 | Privacy complete manifest and ready exact Media version/current generation; currently authorized export requester | Request/bundle reference; no signed credential or stored public URL |
| security.notice.v1 | Identity committed security intent; affected local User only | Generic change and authenticated-context link; no OTP, recovery token, precise IP or factor details |
| supply.status.v1 | Professional/Marketplace committed status/remediation intent under R035; owner-resolved Professional User | Generic status/remediation code; no Healthcare/provider/Hold detail |

Candidate registers `candidate.application_status_changed.v1` with eventId, application ID/revision, committed time, semantic command identity, old/new status, authorized actor reference and safe typed Candidate/Organization subject references. This event contains no resume, message, employer notes or protected evidence. The source owner derives notification recipients from current Hiring authority. Only the four listed successful status transitions may create application.status.v1 at launch; application views, recruiter stages and retry transport do not. Candidate acceptance must already satisfy R045 current-offer proof, and withdrawal does not restore quota. Sending a notification never makes an application or Candidate publicly discoverable.

Deduplicate one semantic intent × resolved User; channel attempts are children of that intent. Changed payload under the same fingerprint conflicts. Retries preserve identity. Current protected-context access is rechecked before rendering/dereference; loss of membership suppresses the protected notice. Do not create a removed-user notice without its own approved source policy. Delayed invitation links must recheck P18/current schedule. Notification failure never rolls back source truth. No message bodies, resumes, exact locations, raw provider failures, adjudication evidence or credentials may enter generic variables.

Material proposal changes remain visibly surfaced by Gig's current-revision presentation under P14; a delivered notice is not evidence the latest terms were presented for acceptance. Participant-facing Dispute updates reuse Order conversation under P19, but a Review fact cannot be relabeled as an Order event; any separate Review alert remains disabled until registered. Optional viewed/shortlisted, Location, Interview completion/no-show and other undeclared alerts remain disabled. This finite registration does not provide legally sufficient notice policy. Exact copy, renderer/schema fixtures, provider/account/channel qualification and delivery recovery proof remain activation prerequisites. Existing broad notification suggestions are narrowed by this explicit source/recipient matrix for these intents.


## WA-R068 / WA-R069 — Authority facts and committed event obligations

This Module adopts its `professional_eligibility` action/fact row and specifically registered producer/consumer effects in `context/reconciliation/authority-event-contracts.md`. Role interprets the catalog; this owner retains facts and lifecycle. Register each concrete protected port before activation; a grouped port row does not authorize unspecified commands.

Owner action scope: `updateProfessionalProfile / evaluateProfessionalReadiness`. Permitted relationships: profile owner for ordinary edit; registered eligibility caller. Required owner facts: Professional-to-User binding, profile revision, requested readiness purpose, current restriction/readiness tokens. Assurance: ordinary B; no generic Professional Moderation executor registration. These facts include typed target, source revision, subject relationship, purpose/action and evaluation time; missing/stale/unavailable facts cannot authorize, and current revisions are checked again at effect. B/S/A have the precise appendix meanings; source services cannot invent human assurance.

Producer obligations:

- `professional.readiness_changed.v1`: Professional ID, readiness/source revision, changed reason classes. Registered effect: Marketplace/Search: reevaluate publication; Gig/Order: fresh checks before new action.
- `professional.profile_completion_changed.v1`: Professional/User binding, completion policy/version, completed boolean, source revision. Registered effect: Gamification: profile_completed qualification only.

Consumer obligations:

- `track.entitlement_changed.v1`: consume only the effect naming this Module — Professional, Candidate, Marketplace, Video: refresh eligibility; Search: current projection reevaluation; preserve acquired rights.
- `taxonomy.policy_changed.v1`: consume only the effect naming this Module — Professional/Marketplace/Hiring/Healthcare/Trust/Search: targeted reevaluation.
- `payment.financial_readiness_changed.v1`: consume only the effect naming this Module — Professional, Track, Order, Gamification, Sweepstakes: action-specific reevaluation.
- `verification.readiness_changed.v1`: consume only the effect naming this Module — Professional/Healthcare/Hiring where registered requirement applies: reevaluate; no raw report.
- `healthcare.boundary_changed.v1`: consume only the effect naming this Module — Professional/Marketplace/Media/Video/Search: invalidate current grants/projections as applicable.
- `review.reputation_changed.v1`: consume only the effect naming this Module — Professional/Search reputation projection; Gamification high_rating_received; removal/correction retracts qualification.

Each audience receives only its needed fields. Obtain fresh source facts before protected decisions; invalidation is not authority.

Persist source history and outbox intent atomically; use event identity/fingerprint deduplication, source-revision watermarks, tombstones and correction lineage as specified by WA-R069. Delayed facts cannot restore revoked exposure; gaps require owner replay/current snapshot. Registered Hold applicability may prompt current reevaluation only for existing typed targets/actions; release is never automatic restoration or financial execution. Source events cannot substitute for explicit Privacy/Moderation/provider effect commands or WA-R066 notification intents.

Produce professional.profile_completion_changed.v1 only from this owner's versioned completion-policy evaluation with preserved Professional-to-User binding; profile creation/status is insufficient. This authority row does not register a generic Professional Moderation executor; R067 unsupported target/effect combinations remain denied.

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration

Use the WA-R070 versioned source descriptor defined by AI Taxonomy and affected-target enumeration/assignment contract defined by Taxonomy. This owner supplies an opaque current source token, purpose-authorized minimized fields and assignment token, enumerates only its own joins under stable snapshot/cursor semantics, and commits accepted assignment plus immutable receipt/outbox atomically after current Taxonomy/authority/version checks. Same command key with changed fingerprint conflicts. An expired cursor requires restart; incomplete iteration never proves deletion. Extra descriptor fields reject. Routing IDs, actor context and policy metadata do not automatically become provider payload. No direct foreign repository reads or writes are permitted.

For ProfessionalProfile, provider fields are classificationText derived from authorized bio, acceptedCategoryIds and acceptedTagIds. Exclude account/contact/address, licenses/background evidence, transactions and private messages.

classificationText is a purpose-approved sensitivity-reviewed projection, not unrestricted forwarding of the underlying text. Each target/purpose must be explicitly registered with bounded serializer/output schema; missing authority, unsafe text or unqualified Healthcare context denies processing.


## WA-R074 — Contextual Customer display and Gig participation requirements

This owner adopts its source/consumer obligations in `context/reconciliation/context-query-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.


## WA-R075 — Typed Hold action applicability and source readiness

This owner adopts its source/consumer obligations in `context/reconciliation/hold-action-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.
