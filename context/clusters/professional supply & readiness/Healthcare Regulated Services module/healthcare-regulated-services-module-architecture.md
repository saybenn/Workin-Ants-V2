# Healthcare / Regulated Services Module Architecture

> **Module ID:** `healthcare_regulated_services`  
> **Module name:** Healthcare / Regulated Services Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/clusters/professional supply & readiness/Healthcare Regulated Services module/healthcare-regulated-services-module-architecture.md`\
> **Document status:** Implementation-grade Module architecture; binding where marked **Confirmed**, planning-only where marked **Proposed Ruling**, and non-implementable where marked **Unresolved**

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `healthcare_regulated_services` |
| Module name | Healthcare / Regulated Services Module |
| Module type | `compliance` |
| Build status | `mvp_active_legal_gated` |
| Primary Cluster | CL-03 — Professional Supply & Readiness |
| Document status | Implementation-grade Module architecture |
| Intended audience | Coding agents, developers, reviewers, maintainers, architecture reviewers, and compliance reviewers |
| Relationship to root architecture | Subordinate to root Workin Ants architecture, project overview, code standards, shared operations, and platform security/data rules. It specializes those decisions for healthcare-sensitive behavior only. |
| Relationship to Cluster architecture | Subordinate to the CL-03 architecture for cross-Module collaboration and to the CL-03 build plan for sequence. This file is more authoritative for this Module's internal truth, transitions, local policy, and public contracts. |
| Update rule | A change to owned truth, lifecycle semantics, public contracts, provider proof, healthcare policy, retention, or a binding unresolved ruling must update this file before or with implementation. Build progress must not silently redefine it. |

### Evidence status terminology

- **Confirmed** — directly supported by the current Module Registry, Cluster Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Architecture, CL-03 architecture, or CL-03 build plan.
- **Proposed Ruling** — a strongly supported implementation decision that is not yet canonical. It must be approved before code or schema depends on it.
- **Unresolved** — the supplied evidence does not establish a safe answer. Unsupported behavior remains disabled or explicitly unavailable.

### Evidence basis

This document is grounded in the current Workin Ants Project Overview, Ubiquitous Language Pack v2.2 / Compliance Inventory, Deep Module Registry, Cluster Registry v2.3, Prisma schema, Canonical Shared Operations Architecture, CL-03 Professional Supply & Readiness architecture, CL-03 build plan, and the prior standardized Module Architecture Extract for this Module.

## 2. Purpose, Goal, and Transformation

### Purpose

Own the healthcare-specific compliance lane that determines whether a `ProfessionalProfile`, `Offering`, or supported downstream target may participate in healthcare-sensitive behavior, and how healthcare-sensitive payloads may be exposed to authorized administrators/support actors.

Healthcare is **not** a User type and is **not** a platform-wide mode. The lane is triggered from canonical taxonomy, Offering, professional, or explicit healthcare-boundary context.

### Goal

Make these questions answerable from authoritative Workin Ants records rather than provider objects, UI booleans, or scattered consumer logic:

```text
Does healthcare handling apply to this professional/action/target?
Which BAA evidence currently supports the lane?
Is the healthcare lane ready for this action and provider context?
Is this exact target healthcare-sensitive?
After general authorization succeeds, may this payload be returned as-is,
redacted, or blocked?
What source evidence explains the decision?
```

### What enters

- authenticated actor or trusted system context;
- Role / Authority decision and resource-owner relationship facts;
- `ProfessionalProfile` context from Professional Eligibility;
- accepted taxonomy healthcare/sensitivity requirements from Taxonomy & Classification;
- `Offering` eligibility context from Marketplace Supply;
- supported target identity/context from the owning Module for Orders, Bookings, Threads, Messages, MediaAssets, and video/delivery records;
- versioned `ConsentLog` proof when a healthcare workflow requires it;
- `ComplianceHold` decisions when an action is hold-sensitive;
- ready private `MediaAsset` references for BAA/evidence documents;
- normalized BAA/e-sign provider results when a provider path is approved;
- provider capability/readiness facts from the owner of video/media delivery mechanics;
- Privacy-owned erase/export/retention instructions.

### What leaves

- authoritative healthcare profile state;
- authoritative BAA lifecycle state and references to approved evidence;
- explicit healthcare-sensitive target boundaries;
- exact-target healthcare admin payload policy;
- **SH-020 `evaluateHealthcareReadiness`** decisions;
- healthcare admin-access decisions and redaction/block instructions;
- versioned healthcare domain events through the shared transactional outbox;
- requests to Audit, Notification, Compliance Hold, Media, Privacy, Search/source owners, and Observability through their public interfaces;
- provider-neutral reconciliation results and owner-specific provider-event proof only when the corresponding architecture rulings are approved.

### Capability transformation

```text
canonical professional / taxonomy / Offering / target context
+ healthcare-owned profile, BAA, boundary, and admin policy truth
+ required external proof through owner interfaces
→ healthcare applicability
→ healthcare readiness decision
→ healthcare access decision / handling instruction
→ owner event and required audit evidence
→ downstream owners enforce the result without copying healthcare policy
```

### Why this deserves its own Module boundary

Healthcare rules have distinct compliance meaning, evidence, provider constraints, sensitive-data handling, access-policy semantics, and legal gating. Folding them into Professional Eligibility, Marketplace Supply, Media, Messaging, Video, Audit, or Role / Authority would scatter one policy across several lifecycles. Conversely, making Healthcare own those surrounding lifecycles would overload the Module. The correct boundary is: **Healthcare owns healthcare truth and policy; adjacent owners provide context and enforce their own mechanics.**

## 3. Owned Truth

### 3.1 Models and records owned

| Record | Meaning in plain English | Ownership status |
| --- | --- | --- |
| `HealthcareComplianceProfile` | One ProfessionalProfile's healthcare-lane compliance record and current healthcare readiness summary. | Confirmed |
| `BaaAgreement` | One BAA execution record supporting a healthcare compliance profile. It is agreement-execution truth, not generic consent proof. | Confirmed |
| `HealthcareDataBoundary` | An explicit statement that a supported target belongs to or contains healthcare-sensitive data. | Confirmed |
| `HealthcareAdminAccessPolicy` | The healthcare-specific payload treatment for an exact target after general actor authorization has already succeeded. | Confirmed |

### 3.2 Enums/status vocabularies owned

- `HealthcareComplianceStatus`
- `BaaAgreementStatus`
- `HealthcareDataBoundaryTargetType`
- `HealthcareAdminAccessMode`
- `HealthcareAccessDecision`

`DataSensitivity` is referenced but its generic ownership remains **Unresolved (U-12)**. This Module owns the specific healthcare boundary semantics; it must not claim the whole generic sensitivity vocabulary by implication.

### 3.3 Lifecycles owned

- `HealthcareComplianceProfile.status` transition policy.
- `BaaAgreement.status` transition policy.
- Creation and authoritative meaning of exact `HealthcareDataBoundary` rows.
- Creation/update and authoritative meaning of exact-target `HealthcareAdminAccessPolicy` rows.

The current schema does **not** provide a safe retirement/history lifecycle for `HealthcareDataBoundary` or a version/effective-history lifecycle for `HealthcareAdminAccessPolicy`; those remain constrained by U-09/U-10.

### 3.4 Source-of-truth records

- Whether a ProfessionalProfile is in the healthcare lane and its current healthcare summary: `HealthcareComplianceProfile`.
- BAA execution state: `BaaAgreement`.
- Whether an exact supported target is explicitly healthcare-sensitive: `HealthcareDataBoundary(targetType, targetId)`.
- Current exact-target healthcare admin payload mode: `HealthcareAdminAccessPolicy(targetType, targetId)`.

### 3.5 Domain events / ledgers owned

No dedicated healthcare event table exists in the supplied Prisma schema. The Module owns the **meaning and versioning** of its domain events, while **SH-046 `publishDomainEvent`** owns transactional publication mechanics.

Expected event families are defined in Section 21. `AuditEvent` and `AccessAuditLog` are not the Module's domain event ledger.

### 3.6 Projections owned

The Module owns no Search engine projection. Healthcare readiness may contribute to owner-built public projections, but Search / Public Visibility owns `SearchUpsertEvent`, Typesense execution, reconciliation, and query surfaces.

A `HealthcareComplianceProfile` summary is healthcare source truth, not a Search projection. Any future cached decision result must be explicitly marked derived and rebuildable.

### 3.7 Snapshots/proof owned

Confirmed healthcare proof consists of the four owned records above. `AccessAuditLog` is supporting proof owned by Audit / Event Ledger.

**Unresolved:** current `BaaAgreement` is not sufficient to establish the complete immutable legal evidence package for executed BAAs. U-07 must decide parties/signers/countersigners, immutable document/version/hash evidence, and related retention semantics before production BAA automation or a final legal-compliance claim.

### 3.8 Policies and invariants owned

This Module owns:

- when canonical context requires the healthcare lane;
- how healthcare-owned evidence affects **SH-020**;
- BAA transition policy and its effect on healthcare readiness;
- the meaning of a healthcare data boundary;
- the healthcare-specific admin payload mode and decision;
- healthcare vendor-readiness policy for a requested use case, based on provider capability facts supplied through owner interfaces;
- which healthcare changes are material enough to emit readiness/boundary/policy events;
- healthcare-specific redaction/block requirements, while the resource owner performs actual payload delivery/redaction mechanics.

## 4. Explicit Non-Ownership

This Module must not own or recreate the following:

| Adjacent owner | Responsibility that stays outside Healthcare |
| --- | --- |
| Identity & Access | User identity, sessions, passkeys/MFA, step-up challenges, security lifecycle. |
| Role / Authority | Generic platform/org/participant/ownership permission interpretation. Admin/support role alone never bypasses Healthcare policy. |
| Consent & Disclosure | `ConsentLog`, active consent versions, generic acceptance proof, standalone consent rendering. BAA execution is separate Healthcare truth. |
| Professional Eligibility | `ProfessionalProfile` lifecycle and final action-specific professional readiness composition. |
| Taxonomy & Classification | Taxonomy vocabulary, accepted category/tag assignment, and requirement-trigger semantics. Taxonomy may trigger Healthcare; it does not complete Healthcare. |
| Marketplace Supply | `Offering` lifecycle, Offering shape, pricing, and publication mutation. Healthcare returns a gate; Marketplace changes `Offering.status`. |
| Trust Verification / Screening | Professional licenses, background checks, screening requirements, `VerificationCheck`, `ProfessionalLicenseCredential`, `TrustBadge`. |
| Transaction / Order | `Order` and Order event truth. A healthcare boundary on an Order does not grant Healthcare ownership of Order status. |
| Booking & Calendar | Booking lifecycle, calendar state, slot mechanics. |
| Messaging | `Thread`, `Message`, participant and message lifecycle. Healthcare supplies handling policy only. |
| Video Session | Video rooms, tokens, course assets/playback grants, provider-session lifecycle, video provider-event truth. |
| Media / File Access | Upload validation, malware scanning, object storage, `MediaAsset`, `MediaAccessGrant`, signed URLs, deletion mechanics. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense clients/indexers, public query projection. |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and generic review stop-sign state. |
| Audit / Event Ledger | Generic `AuditEvent` and `AccessAuditLog` persistence, hash-chain/access-audit mechanics. |
| Notification | Email/SMS/push/provider delivery, notification subscription and delivery truth. |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, target orchestration, retention-exemption records. Healthcare only executes instructions against its own truth. |
| Observability / Ops | `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident`, log/metric/error infrastructure. |
| Legal/compliance counsel | Legal drafting of BAA text, legal sufficiency, retention-period determination, or provider contract approval. |

Prohibited convenience shortcuts include `User.isHealthcareProvider`, `healthcareUserFlag`, `hipaaBoolean`, local healthcare audit tables, local signed-URL services, local video-token services, local role engines, and consumer-specific copies of healthcare policy.

## 5. Module Architecture Principles

1. **Healthcare is contextual.** Never make every User or every Professional traverse healthcare infrastructure.
2. **BAA truth is separate from profile summary.** `BaaAgreement` owns agreement execution; `HealthcareComplianceProfile` may summarize readiness but cannot replace BAA evidence.
3. **Consent is proof, not BAA truth.** `ConsentLog` can prove accepted healthcare disclosure/version; it does not mean a BAA is signed or verified.
4. **General authorization precedes healthcare payload policy.** Do not process or reveal healthcare details to a caller who is not authorized to act on the target in the first place.
5. **Resource owners enforce mechanics.** Healthcare returns allow/redact/block semantics; Media, Messaging, Video, and other resource owners enforce their own read/delivery mechanics.
6. **Explicit boundary beats generic inference.** `HealthcareDataBoundary` is the healthcare-specific source. Generic `DataSensitivity.healthcare` alone is insufficient healthcare proof.
7. **No cross-domain polymorphic repository.** Validate target existence/context through the target owner's public facts interface or SH-123, not arbitrary Prisma table switching.
8. **Provider state is evidence input.** The BAA/e-sign provider never becomes Workin Ants source truth.
9. **Production webhook processing requires owner-specific dedupe truth.** Never reuse `ProcessedStripeEvent`, `ProcessedVideoProviderEvent`, `AuditEvent`, or a last-event field as Healthcare's complete dedupe ledger.
10. **Audit is evidence, not domain state.** A successful `AccessAuditLog` row does not make an access decision valid; it records a decision already made.
11. **Search remains downstream.** Healthcare must not write Typesense or `SearchUpsertEvent` directly unless the Search public command explicitly owns that write.
12. **Privacy orchestrates; Healthcare executes.** Destructive handling is blocked when retention is unresolved.
13. **Unsupported lifecycle behavior fails explicitly.** Do not hard-delete a boundary to simulate retirement or overwrite policy history when the architecture has not approved those semantics.
14. **All provider/queue/event work is replay-safe.** Retries must not duplicate BAA transitions, notifications, holds, or downstream effects.
15. **PHI is minimized everywhere.** No raw healthcare payloads, private message bodies, BAA document text, or provider payloads in logs, analytics, audit metadata, notification payloads, or event bodies unless explicitly approved and necessary.

## 6. Proposed Folder / Code Structure

The exact repository root remains a root-architecture decision. Within the approved Module root, use an owner-preserving structure equivalent to:

```text
src/modules/healthcare-regulated-services/
  actions/
    # framework-facing mutation entry points only when the app architecture uses actions
  queries/
    # framework-facing query entry points only when needed
  application/
    healthcare-application-service.ts
    baa-application-service.ts
    healthcare-boundary-application-service.ts
    healthcare-admin-access-application-service.ts
  domain/
    healthcare-readiness-policy.ts
    healthcare-requirement-policy.ts
    healthcare-profile-transitions.ts
    baa-transitions.ts
    healthcare-admin-access-policy.ts
    healthcare-vendor-readiness-policy.ts
    reason-codes.ts
  contracts/
    healthcare-public-contracts.ts
    healthcare-owner-facts.ts
    healthcare-events.ts
    healthcare-privacy-contracts.ts
  repositories/
    healthcare-compliance-profile.repository.ts
    baa-agreement.repository.ts
    healthcare-data-boundary.repository.ts
    healthcare-admin-access-policy.repository.ts
  providers/
    baa-provider.port.ts
    adapters/
      # only an approved BAA/e-sign provider adapter belongs here
  workers/
    baa-expiration.worker.ts
    baa-reconciliation.worker.ts
    # provider-event worker only after U-07/U-08 are resolved
  privacy/
    enumerate-healthcare-subject-data.ts
    execute-healthcare-privacy-instruction.ts
    healthcare-retention-facts.ts
  components/
    # only if a real professional/admin healthcare surface is approved
  tests/
    unit/
    integration/
    contracts/
    providers/
    security/
    privacy/
    concurrency/
```

### Folder rules

- Do not create `auth/`, generic `permissions/`, `audit/`, `queue/`, `storage/`, `search/`, `notifications/`, `privacy-workflow/`, or generic `webhooks/` infrastructure inside this Module.
- A provider adapter lives here only when Healthcare owns the external relationship and domain translation.
- Consumer-specific redaction implementations remain with the resource owner. Healthcare exposes a decision/redaction contract, not a copy of every resource's serializer.
- Repositories may access only Healthcare-owned tables. Cross-Module facts are obtained through contracts.
- If `components/` is unused, omit it. Do not invent UI solely to justify the Module.

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / actions / route handlers | Input parsing, request DTO mapping, actor/system-context handoff, response serialization. | Business transitions, direct Prisma mutation, provider SDK semantics, generic authorization logic. |
| Application services | Command/query orchestration within Healthcare; transaction boundaries; dependency calls; owner-event/audit/notification requests. | Another Module's lifecycle or generic workflow infrastructure. |
| Domain policy | Healthcare applicability, readiness, BAA transition rules, boundary semantics, healthcare admin-access decisions, vendor-readiness policy. | Role/RBAC, taxonomy assignment validity, professional readiness composition, Media/Video mechanics. |
| Repositories / data access | Healthcare-owned four models and approved Healthcare-owned provider-event proof if later added. | `ProfessionalProfile`, `Offering`, `Order`, `Booking`, `Message`, `MediaAsset`, Search, Audit, Privacy, or provider-owned business truth. |
| Workers | BAA expiry/reconciliation/provider processing when enabled; owner-safe batched reevaluation. | Generic queue runner, Search worker, Media processor, Notification delivery worker. |
| Provider adapters | Provider authentication, request/response mapping, provider status translation, provider-specific reconciliation/deletion where applicable. | Domain truth, consumer resource mechanics, generic cross-provider status vocabulary. |
| Public contracts | Healthcare commands, queries/decisions, owner events, privacy executor, provider-neutral BAA port. | Generic cross-domain repositories or a universal readiness engine. |
| UI / admin surface | Safe healthcare status/next-action display and metadata-only administration where approved. | PHI-rich general admin console, raw provider payload viewer, generic moderation/hold UI. |

## 8. Data Model

### `HealthcareComplianceProfile`

**Purpose:** one-to-one healthcare lane record for a `ProfessionalProfile`.

**Key relationships:**
- unique `professionalProfileId` references Professional Eligibility-owned `ProfessionalProfile`;
- one profile may have many `BaaAgreement` rows.

**Authoritative fields:**
- `status`;
- `declaredHealthcareAt`;
- `verifiedAt` where the approved transition policy uses it;
- `rejectedReason` for profile-level rejection only.

**Lifecycle field:** `status: HealthcareComplianceStatus`.

**Uniqueness:** exactly one healthcare profile per ProfessionalProfile is enforced by `@unique(professionalProfileId)`.

**Concurrency-sensitive behavior:** concurrent lane declaration/provisioning and conflicting status transitions must be idempotent/serialized.

**Retention/privacy:** healthcare status is sensitive compliance data. Exact deletion/retention periods are not established; Privacy fulfillment must not destructively guess.

**Important caveat:** `lockedHealthcareFlag` exists but its canonical meaning is **Unresolved**. It must not become an authorization, hold, or general healthcare truth shortcut until defined.

### `BaaAgreement`

**Purpose:** authoritative BAA execution lifecycle record tied to a HealthcareComplianceProfile.

**Key relationships:**
- belongs to `HealthcareComplianceProfile`;
- has provider/reference fields;
- has `documentMediaId` as a UUID reference but the current Prisma model does not establish an explicit `MediaAsset` relation.

**Authoritative fields:**
- `status`;
- provider identity/reference when a provider path exists;
- lifecycle timestamps: `sentAt`, `signedAt`, `verifiedAt`, `revokedAt`, `expiresAt`;
- evidence reference after U-07 is resolved.

**Lifecycle field:** `status: BaaAgreementStatus`.

**Indexes:** profile/status, provider/reference, expiration.

**Concurrency-sensitive behavior:** webhook/manual/admin transitions may race; commands require expected state/version or an aggregate lock plus idempotency.

**Retention/privacy:** likely retention-sensitive legal/compliance proof. `onDelete: Cascade` from HealthcareComplianceProfile is a material risk until U-18 and BAA retention are resolved. Production erasure must not assume cascade deletion is legally acceptable.

**Current proof gaps:** parties/signers, immutable document/version/hash semantics, rejection reason/evidence, and canonical effective/current BAA selection are not fully established.

### `HealthcareDataBoundary`

**Purpose:** explicit healthcare-sensitive classification for one supported target.

**Key fields:**
- `targetType`;
- `targetId`;
- `sensitivity` defaulting to `healthcare`;
- optional `reason`;
- `createdAt`.

**Uniqueness:** one row per `(targetType, targetId)`.

**Supported target types:** professional profile, Offering, Order, Booking, Thread, Message, MediaAsset, booking video room, job-interview video room, course video asset, course playback grant.

**Concurrency-sensitive behavior:** duplicate marks must converge on one row; target existence must be owner-validated before write.

**Retention/privacy:** the boundary itself is sensitive metadata. The schema has no retirement/status/history fields, so hard deletion must not be used as a guessed retirement mechanism.

### `HealthcareAdminAccessPolicy`

**Purpose:** current exact-target healthcare payload treatment after general authorization.

**Authoritative fields:**
- `targetType`;
- `targetId`;
- `mode`;
- `reason`;
- timestamps.

**Uniqueness:** one current row per `(targetType, targetId)`.

**Concurrency-sensitive behavior:** concurrent policy updates must use optimistic concurrency/expected state or a lock.

**Retention/privacy:** the current mutable record does not preserve policy history/effective periods. Audit-reproducible historical policy and parent/child precedence remain U-10.

### Cross-Module references are not ownership

A Healthcare row may identify a ProfessionalProfile, Offering, Order, Booking, Thread, Message, MediaAsset, or video/delivery resource. That reference permits a typed contract relationship; it does not permit Healthcare to mutate the referenced owner's lifecycle.

## 9. Enums, Statuses, and Lifecycles

### 9.1 HealthcareComplianceProfile

Current status vocabulary:

```text
not_applicable
pending_baa
baa_sent
baa_signed
verified
rejected
suspended
```

**Confirmed ownership:** Healthcare controls transitions on its profile row.

**Proposed Ruling PR-HC-01:** `baa_sent` and `baa_signed` are summary states derived only from the effective BAA's owner state. They must never become an independent second BAA lifecycle. If future schema evolution removes these summary states, BAA remains authoritative.

**Unresolved:** complete adjacency, whether `rejected` may reopen, suspension restoration rules, and exact effect of `lockedHealthcareFlag`.

A safe initial state-machine constraint is therefore:

```text
not_applicable
  → pending_baa                 only when healthcare lane declaration/applicability is approved

pending_baa
  → baa_sent                    only from effective BAA truth
  → rejected                    only through an approved profile-level rejection command
  → suspended                   only through an approved healthcare restriction policy

baa_sent
  → baa_signed                  only from effective BAA truth
  → rejected / suspended        only through approved transition policy

baa_signed
  → verified                    only after the additional healthcare verification policy passes
  → rejected / suspended        only through approved transition policy

verified
  → suspended                   when healthcare-owned readiness becomes invalid and suspension semantics are approved

suspended / rejected
  → ?                           UNRESOLVED; no generic restore/reopen implementation until approved
```

This is not permission to implement every illustrated arrow; the feature specification must cite the approved transition table.

### 9.2 BaaAgreement

Current status vocabulary:

```text
draft
sent
signed
verified
rejected
revoked
expired
```

**Confirmed:** BAA lifecycle belongs here, not ConsentLog or Transaction Agreement.

**Unresolved U-07:** legal proof shape and parties/signatures.

**Unresolved U-HC-01:** selection of the effective/current BAA when multiple rows exist. Do not use “latest row wins” without an approved rule.

**Proposed Ruling PR-HC-02:** before any BAA mutation command is enabled, define an explicit transition matrix with actor/source permissions and idempotency behavior. A candidate safe direction is `draft → sent → signed → verified` with `rejected`, `revoked`, and `expired` as controlled exception/terminal states, but exact reopen/reissue semantics remain unresolved.

### 9.3 HealthcareDataBoundary

Current schema represents **presence of an explicit boundary**, not a full lifecycle.

Supported implementation now:

```text
no explicit row
  → mark exact validated target
  → explicit boundary exists
```

Not supported without U-09:

- clear/retire;
- inherited propagation;
- parent-child weakening/strengthening;
- historical reconstruction of a removed boundary.

A duplicate exact mark is idempotent; a conflicting target classification must return conflict/review rather than delete/recreate silently.

### 9.4 HealthcareAdminAccessPolicy

Modes:

```text
allow
redact_payload
block_payload
```

Access-decision vocabulary:

```text
allowed
redacted
blocked
denied
```

Current supported scope may be limited to one exact target and current policy only.

**Unresolved U-10:** version/effective history and parent-child precedence.

**Unresolved U-11:** canonical distinction between `blocked` and `denied`.

**Proposed Ruling PR-HC-03:** general Role / Authority denial should terminate before Healthcare policy evaluation. Until U-11 is settled, public Healthcare access contracts must not expose ambiguous `denied` semantics to cross-Module consumers; they may use a narrower exact-target result (`allowed | redacted | blocked`) after general authorization.

### Lifecycle proof requirements

- Domain state changes emit owner events through SH-046.
- Sensitive access creates SH-030 evidence when required.
- Generic AuditEvent may prove an admin/system action but never replaces lifecycle truth.
- Provider callbacks are not domain events until signature verification, owner-specific dedupe, translation, transition validation, and state application succeed.

### Prohibited lifecycle shortcuts

- direct `status = ...` setters exposed to consumers;
- deriving BAA state from provider status on read;
- deriving healthcare verification from `ProfessionalLicenseCredential`, `TrustBadge`, or `DataSensitivity` alone;
- using `ComplianceHold` as the healthcare source reason;
- hard deleting a boundary to represent a transition not modeled by the schema.

## 10. Commands

| Command | Purpose | Actor / context | Preconditions | State written | Shared operations | Effects | Idempotency / failure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `declareHealthcareLane` | Provision or activate healthcare lane intent for a ProfessionalProfile. | Authenticated professional/admin/system as policy allows; owner facts. | ProfessionalProfile exists; actor authorized; canonical context permits declaration; expected current state. | `HealthcareComplianceProfile`; declaration timestamp/status. | SH-001, SH-002, SH-044, SH-046; SH-022 where context requires. | Profile event; audit if high-impact; optional Notification request. | Duplicate semantic request replays same result. Concurrent creation must respect unique profile key. |
| `transitionHealthcareComplianceProfile` via named owner commands | Apply only approved profile lifecycle transitions. | Authorized owner/admin/system source. | Expected state/version; local transition policy; any required BAA/hold/context evidence. | Profile status/timestamps/reason. | SH-002, SH-044, SH-051/052/053, SH-046, SH-029 as required. | Status event/readiness event. | Stale transition returns conflict; no arbitrary status setter. |
| `createBaaAgreement` | Create a BAA workflow record for an approved healthcare profile. | Authorized professional/admin/system workflow. | Healthcare lane exists; BAA policy says a new agreement may be created; effective-BAA rule approved before multiple-current ambiguity is introduced. | `BaaAgreement(draft)`. | SH-001/002, SH-044, SH-046. | BAA-created event. | Idempotent by semantic command key; duplicate active/effective agreement policy depends on U-HC-01. |
| `recordBaaSent` | Record provider-neutral/manual evidence that the BAA was sent. | Authorized admin/system/provider worker. | Approved `draft → sent` transition and required evidence. | BAA status/`sentAt`; profile summary only through BAA-derived rule. | SH-044, SH-053, SH-046, SH-029. | BAA status/readiness event; Notification request where approved. | Replay returns existing result; contradictory state conflicts. |
| `applyBaaSignedResult` | Apply normalized signed evidence without treating provider object as truth. | Provider worker or restricted manual workflow. | Approved transition, evidence reference, legal proof path supported. | BAA status/`signedAt`; summary effect. | SH-044, SH-053, SH-046, SH-029; provider shell if applicable. | Event/readiness reevaluation. | Automated path disabled until U-07/U-08; manual path must not claim complete e-sign proof. |
| `verifyBaaAgreement` | Mark BAA verification complete under the approved Healthcare policy. | Restricted reviewer/system. | Signed evidence present and approved proof requirements satisfied. | BAA `verified`; `verifiedAt`; profile summary/readiness. | SH-002, SH-044, SH-053, SH-046, SH-029. | BAA/profile/readiness events. | Stale/missing proof returns non-success. |
| `rejectBaaAgreement` | Record approved BAA rejection. | Restricted reviewer/system. | Transition and rejection-evidence shape approved. | BAA rejected state; related profile summary. | SH-002, SH-044, SH-053, SH-046, SH-029. | Event; remediation Notification if approved. | Current schema lacks BAA-specific rejection reason; do not silently misuse profile rejection reason. |
| `revokeBaaAgreement` | Revoke a previously applicable BAA. | Restricted reviewer/system/provider-normalized result. | Approved revocation policy and evidence. | `status=revoked`, `revokedAt`; healthcare readiness reevaluation. | SH-002, SH-044, SH-053, SH-046, SH-029. | Readiness event; optional hold/notification request. | Idempotent; never direct-update ProfessionalProfile/Offering. |
| `expireBaaAgreement` | Apply an approved expiry transition. | System worker/manual admin. | `expiresAt` due; effective BAA semantics settled for affected path. | BAA `expired`; readiness reevaluation. | SH-044, SH-055, SH-046. | Event, notification/remediation request. | Repeated expiry is no-op/replay. |
| `markHealthcareDataBoundary` | Explicitly mark a validated supported target as healthcare-sensitive. | Authorized owner/admin/system workflow. | Target owner validates target type/ID and context; no conflicting row. | `HealthcareDataBoundary`. | SH-002 as actor applies, SH-044, SH-046, SH-123, SH-029 where required. | Boundary event; downstream resource owners may reevaluate handling. | Duplicate same mark returns existing row; invalid target writes nothing. |
| `setHealthcareAdminAccessPolicy` | Set current exact-target allow/redact/block policy in the currently supported scope. | Authorized admin/compliance actor. | General authorization; target validated; exact-target scope explicitly accepted; U-10 limitations acknowledged. | `HealthcareAdminAccessPolicy`. | SH-001/002, SH-044, SH-052, SH-046, SH-029, SH-123. | Policy-changed event. | Stale update conflicts. No inherited/history claim. |
| `requestHealthcareComplianceHold` | Ask Hold owner to create a reusable platform stop sign when approved healthcare policy requires it. | Healthcare system/admin workflow. | Local healthcare source condition exists and approved mapping says hold is required. | No Healthcare hold row; Hold Module writes `ComplianceHold`. | SH-012. | Hold-owner outcome; Healthcare may emit fact. | Request is idempotent; Healthcare must not create `isBlocked`. |
| `requestHealthcareNotification` | Ask Notification to deliver an approved remediation/status notice. | Healthcare workflow. | Event is approved for notification; payload is PHI-minimized. | No Notification row locally. | SH-041, SH-034. | Notification owner handles delivery. | Duplicate notification request uses canonical event/idempotency key. |

Commands that clear/retire boundaries, implement inherited boundary propagation, or claim historical policy mutation are **not public commands** until U-09/U-10 are resolved.

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result class | Stable result | Consumer must not infer |
| --- | --- | --- | --- | --- | --- |
| `getHealthcareComplianceContext` | Professional UI, Professional Eligibility, Marketplace, Admin Review | `professionalProfileId`, authorized request context | Source truth / evidence summary | profile status, safe current BAA reference if determinable, exact boundary refs safe for caller, timestamps/reasons safe for audience | Raw PHI/provider payload; general professional eligibility; license verification. |
| **SH-020 `evaluateHealthcareReadiness`** | Professional Eligibility, Marketplace, source owners deciding public/delivery actions | profile/target/action/provider context | Decision | permitted/non-permitted handling, stable reason codes, evidence refs, evaluatedAt, policy/source versions where available | Role authorization; final Offering/Profile/Order/Booking mutation; BAA/provider state reconstruction. |
| `evaluateHealthcareRequirement` | Professional Eligibility/Marketplace/internal commands | canonical taxonomy/Offering/profile/explicit-boundary context | Contextual decision | healthcare lane required/not required/unsupported with trigger references | That requirement is satisfied. |
| `getCurrentBaaContext` | Healthcare UI/admin/readiness | healthcare profile | Source truth/evidence | approved effective BAA or explicit `unresolved_multiple_candidates` result | “Latest updated row” means current. |
| `getHealthcareDataBoundary` | Resource owners | exact supported target | Source truth | explicit boundary or none | Inherited sensitivity unless U-09 is approved. |
| `resolveEffectiveHealthcareBoundary` | Media, Messaging, Video, Booking/Order access middleware | owner-validated target reference | Truth/decision | **initially exact-target only**; later may include inheritance source once U-09 is approved | Arbitrary cross-table target traversal or generic DataSensitivity truth. |
| `getHealthcareAdminAccessPolicy` | Resource owner/admin tooling | exact target | Source truth | current exact policy or documented default behavior for the supported feature spec | Historical policy version or parent/child precedence until U-10. |
| `evaluateHealthcareAdminAccess` | Media/Messaging/Video/admin resource read layers | already-authorized actor context, target, requested access | Decision | allowed/redacted/blocked semantics and safe instructions; evidence/policy ref | General RBAC permission, resource entitlement, signed URL/token issuance. |
| `evaluateHealthcareVendorReadiness` | Professional Eligibility/Marketplace/Video or internal readiness | use case + provider capability reference | Decision | approved/not-approved/review with reason/evidence | Provider room/token state or legal contract facts not supplied by the owner. |
| `listHealthcareComplianceCases` | Restricted admin surface | filters/pagination | Metadata projection over owner truth | safe identifiers/status/next action only | PHI, raw BAA text, provider payload. |

### Stable decision/reason-code guidance

Public decisions should use typed, versioned reason codes rather than free-text provider messages. Initial categories may include:

```text
healthcare_not_required
healthcare_profile_missing
healthcare_profile_pending
baa_required
baa_pending
baa_not_verified
baa_expired
baa_revoked
healthcare_profile_rejected
healthcare_profile_suspended
explicit_boundary_missing
provider_not_approved
provider_readiness_unavailable
admin_payload_redaction_required
admin_payload_blocked
policy_unresolved
retention_policy_unresolved
dependency_unavailable
unsupported_operation
stale_state
```

The exact enum is a Module contract decision and must remain free of provider names. U-11 must be resolved before relying on `blocked` versus `denied` as a universal cross-Module distinction.

## 12. Public Module Interface

### Public commands

- `declareHealthcareLane`
- named HealthcareComplianceProfile transition commands defined by the approved state machine
- `createBaaAgreement`
- `recordBaaSent`
- `applyBaaSignedResult`
- `verifyBaaAgreement`
- `rejectBaaAgreement`
- `revokeBaaAgreement`
- `expireBaaAgreement`
- `markHealthcareDataBoundary`
- `setHealthcareAdminAccessPolicy`
- Healthcare owner-specific Privacy executor entry points

### Public queries / decisions

- **SH-020 `evaluateHealthcareReadiness`**
- `getHealthcareComplianceContext`
- `evaluateHealthcareRequirement`
- `getCurrentBaaContext`
- `getHealthcareDataBoundary`
- `resolveEffectiveHealthcareBoundary` within supported semantics
- `getHealthcareAdminAccessPolicy`
- `evaluateHealthcareAdminAccess`
- `evaluateHealthcareVendorReadiness`
- restricted `listHealthcareComplianceCases`

### Emitted domain events

- `HealthcareComplianceProfileChanged.v1`
- `BaaAgreementChanged.v1`
- `HealthcareDataBoundaryMarked.v1`
- `HealthcareAdminAccessPolicyChanged.v1`
- `HealthcareReadinessChanged.v1`

Exact names/versions must be fixed in the feature specification before first external consumer dependency. Event payloads contain identifiers, statuses/decisions, source versions, reason codes, and correlation IDs — not PHI.

### Privacy executor

Healthcare implements the owner side of SH-095/096/097/098:

- enumerate subject-owned healthcare records;
- return retention facts and provider/media references;
- execute approved erase/anonymize/retain instructions;
- never create or transition `PrivacyRequest`, `DataErasureJob`, or `DataRetentionExemption` itself.

### Provider-facing interface

If provider automation is enabled, Healthcare owns a provider-neutral BAA/e-sign port such as:

```text
BaaProviderPort
- createOrSendAgreement(...)
- fetchAgreementState(...)
- parseAndVerifyWebhookEnvelope(... adapter-specific wrapper around SH-059 ...)
- mapProviderStatus(...)
- revokeOrVoidAgreement(...) when supported
- deleteOrAnonymizeProviderResource(...) when legally/contractually supported
```

Provider-specific DTOs must not leak into the public Module contract.

## 13. Inbound Dependencies

| Owning Module / capability | Public operation/interface consumed | Why required | Minimum information | May block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | Trusted actor context. | actor/user/system ID, assurance metadata safe for action | Yes | current-user/auth/session helper |
| Role / Authority | SH-002 `authorizeResourceAction` | General permission before healthcare policy. | action, target, owner/relationship facts | Yes | healthcare RBAC/isAdmin logic |
| Consent & Disclosure | SH-008 `queryConsentProof`; SH-010 only where UI needs standalone consent | Required healthcare disclosure/version proof where policy specifies. | proof ID/type/version/acceptedAt/validity | Yes when required | Healthcare generic consent table |
| Taxonomy & Classification | SH-022 `resolveTaxonomyRequirements`; owner facts | Determine canonical healthcare trigger. | requirement owner/type, trigger source/version | Yes for action if healthcare is required | hardcoded healthcare category list |
| Professional Eligibility | `getProfessionalProfileContext`; SH-016 only if Healthcare itself needs composed professional result for a specific approved workflow | Identify professional and status context. | profile ID/status/version, safe owner facts | Context-dependent | direct ProfessionalProfile repository or seller readiness engine |
| Marketplace Supply | `getOfferingEligibilityContext` | Determine Offering healthcare trigger/use case. | Offering ID/version, professional ID, kind, taxonomy refs, sensitivity/delivery facts | Context-dependent | direct Offering repository/status mutation |
| Trust Verification / Screening | SH-018 only if a Healthcare-owned policy explicitly requires Trust evidence | Keep license/screening truth separate. | decision/evidence refs only | Only when explicitly approved | license/background-check reconstruction |
| Admin Review / Compliance Hold | SH-011/012/013 | Evaluate/request/release reusable stop signs. | target/action/hold IDs/scope/reason refs | Yes where mapped | local generic blocked flag |
| Media / File Access | ready MediaAsset facts, SH-087 signed access, SH-090 contextual attachment as applicable | Store/access BAA or healthcare evidence privately. | asset ID, readiness, sensitivity/access result | Yes for file operations | R2 client, scan, MIME, signed URL service |
| Resource owners | SH-123 `validateOwnedTargetReference` / owner-specific facts | Validate polymorphic boundary/policy targets. | target existence/type/version and minimum parent/context facts | Yes | generic cross-domain target repository |
| Audit / Event Ledger | SH-029, SH-030 | Record generic action proof and sensitive access. | actor/action/target/outcome/safe metadata | Critical where required | local audit/access log table |
| Notification | SH-041 `requestNotification` | Deliver status/remediation messages. | template/event key + safe IDs/data | No to domain mutation unless product policy says critical | SES/SMS/push provider clients |
| Privacy / Data Erasure | SH-095/096/097/098 protocol | Fulfill legal requests against Healthcare-owned records. | target instruction, retention decision, subject scope | Yes for destructive operation | PrivacyRequest workflow |
| Observability / Ops | SH-034/037/038 and request context | Safe logs/failure/queue telemetry. | correlation IDs, operation/provider/category, safe status | No to domain truth | Sentry/logger/IntegrationFailure clone |
| Search / Public Visibility | SH-091 only when Healthcare is the approved source requester; otherwise source-owner reacts to Healthcare event | Rebuild/remove public projection after readiness change. | entity ref/source version/reason | Projection only | Typesense/indexer/SearchUpsertEvent direct writes |

### Dependency rule

No inbound dependency grants direct Prisma access. Tests must prove the Module can be run against dependency contract doubles without importing foreign repositories.

## 14. Outbound Consumers and Effects

| Consumer | What it consumes | Expected reaction | Healthcare must not do |
| --- | --- | --- | --- |
| Professional Eligibility | SH-020 result and Healthcare readiness events | Compose action-specific seller readiness. | Transition `ProfessionalProfile`. |
| Marketplace Supply | Healthcare result through Professional Eligibility and/or approved public-readiness input | Permit/block Offering publication and react to readiness changes. | Transition `Offering.status` or write Search state. |
| Transaction / Order | Boundary/readiness facts when healthcare-sensitive Order context applies | Preserve Order truth while invoking healthcare-sensitive delivery/access gates. | Transition Order lifecycle. |
| Booking & Calendar | Boundary/vendor-readiness facts | Gate healthcare-sensitive booking delivery path. | Own booking/calendar state. |
| Video Session | Effective boundary + vendor/readiness/admin-access decision | Create/deny room/playback/token under Video-owned mechanics; audit access. | Create rooms/tokens or process video provider events. |
| Media / File Access | Effective boundary + healthcare access decision | Issue or deny signed access, enforce sensitive handling, record access through canonical audit. | Generate URLs/store files. |
| Messaging | Effective boundary + healthcare admin-access decision | Redact/block message payload before release. | Read/write message body directly as policy enforcement. |
| Search / Public Visibility | Owner-issued source projection/readiness inputs and downstream refresh request | Index/update/remove derived public documents. | Treat Search as healthcare source truth. |
| Audit / Event Ledger | Access/action evidence requests | Persist `AuditEvent`/`AccessAuditLog`. | Store a second generic audit ledger. |
| Admin Review / Compliance Hold | Safe compliance evidence and hold requests | Create/review/release Hold under its lifecycle. | Write Hold status. |
| Notification | Safe event/notification request | Deliver channel-specific communication. | Call delivery providers. |
| Privacy / Data Erasure | owner executor and retention facts | Orchestrate target execution and record exemptions. | Own privacy request lifecycle. |

### Search/projection effect rule

**Proposed Ruling PR-HC-04:** Healthcare should normally emit `HealthcareReadinessChanged`; the owner of the public source (`ProfessionalProfile` or `Offering`) reevaluates its own public readiness/projection and then invokes SH-091. This avoids Healthcare commanding Search for another Module's source lifecycle. Direct SH-091 use from Healthcare is limited to an explicitly Healthcare-owned projection, of which none is currently defined.

## 15. Canonical Shared Operations Used

Only confirmed/necessary operations are binding dependencies. Proposed shared contracts remain proposals until approved by the canonical registry.

| ID / operation | Classification / owner | Why Healthcare uses it | Invocation point | Local policy retained here | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Canonical shared capability — Identity & Access | Establish trusted actor context. | Protected command/query entry. | Which healthcare action is requested. | typed actor/system context | `healthcareAuth.ts`, `getCurrentUser.ts` |
| SH-002 `authorizeResourceAction` | Cross-cutting capability — Role / Authority | Decide general permission before Healthcare payload policy. | Before protected profile/BAA/boundary/policy/admin-access action. | Healthcare action/resource facts. | allow/deny authority decision | `healthcarePermissions.ts`, `isHealthcareAdmin` |
| SH-008 `queryConsentProof` | Platform consent capability — Consent & Disclosure | Verify required disclosure/version proof. | BAA/healthcare action precondition where approved. | Whether the proof is sufficient for the healthcare action. | proof ref/type/version/validity | `healthcareConsent.repository.ts` |
| SH-010 `presentStandaloneConsent` | Cross-cutting UI/application capability — Consent | Render high-risk disclosure where required. | Professional/admin BAA flow UI boundary. | Healthcare workflow context. | accepted proof via Consent owner | local consent renderer/table |
| SH-011 `evaluateComplianceHold` | Cross-cutting capability — Hold | Apply reusable stop sign to hold-sensitive action. | Readiness/transition when policy maps a hold. | Effect of applicable hold on Healthcare action. | hold refs/scope/reasons | `healthcareBlocked`, `isSuspendedByHold` |
| SH-012 `requestComplianceHold` | Cross-cutting capability — Hold | Ask owner to create a platform stop sign. | Approved healthcare failure/revocation workflow. | Whether condition warrants a hold. | authoritative Hold result | local hold table |
| SH-013 `releaseComplianceHold` | Cross-cutting capability — Hold | Ask owner to release a Healthcare-sourced hold. | Source condition resolved. | Whether local evidence permits request. | Hold release outcome | direct Hold update |
| SH-020 `evaluateHealthcareReadiness` | **Module public interface — Healthcare** | Canonical healthcare decision consumed by others. | Public application service. | Entire healthcare readiness policy. | typed decision + reasons/evidence/policy version | parallel `isHipaaReady` helpers |
| SH-022 `resolveTaxonomyRequirements` | Module public interface — Taxonomy | Discover canonical healthcare trigger. | Requirement evaluation/readiness. | Whether trigger is satisfied. | requirement identifiers + trigger/version | healthcare category arrays |
| SH-029 `appendAuditEvent` | Platform audit capability — Audit | Generic proof of significant admin/lifecycle action where required. | Policy/boundary/BAA admin mutation. | Which healthcare action merits audit and safe metadata. | audit acknowledgement/reference | `healthcareAuditLog` |
| SH-030 `recordSensitiveAccess` | Cross-cutting capability — Audit | Prove healthcare view/redaction/block/signed evidence access. | Protected payload/evidence access. | sensitivity/decision/context. | AccessAuditLog acknowledgement/ref | custom PHI access log |
| SH-034 `sanitizeTelemetryMetadata` | Cross-cutting capability — Ops/Audit | Remove PHI/secrets before logs/audit/telemetry. | Before telemetry/audit payload. | Which local fields are sensitive. | safe metadata | local regex-only PHI sanitizer as authority |
| SH-037 `recordIntegrationFailure` | Observability capability — Ops | Surface provider/integration failure. | Provider/webhook/reconciliation failure. | Healthcare operation/provider category and safe correlation. | operational record | domain status as Ops failure |
| SH-044 `executeIdempotentCommand` | Platform primitive | Guarantee one business effect per semantic command. | All replay-prone Healthcare mutations. | fingerprint, replay/conflict semantics. | claimed/replayed result | local idempotency map/table |
| SH-045 `deduplicateDomainEvent` | Platform event inbox | Prevent repeated upstream owner event from duplicating effects. | Event consumer path. | Event-to-healthcare effect. | first/replay result | per-consumer ad hoc event flags |
| SH-046 `publishDomainEvent` | Platform event/outbox | Publish owner facts transactionally. | Same transaction as authoritative mutation. | event name/version/payload. | durable outbox record | emit-after-write without outbox |
| SH-047 `enqueueReliableJob` | Shared queue capability | Schedule provider reconciliation/expiry/reevaluation work. | Worker enqueue point. | job business payload/completion. | durable job | Healthcare queue table/runner |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform | Retry transient external work. | Worker execution. | retryable vs permanent classification. | retry/dead-letter outcome | local retry loop framework |
| SH-051 `acquireAggregateLock` | Shared persistence mechanism | Serialize high-risk aggregate transition where pessimistic locking is selected. | Conflicting BAA/profile operations. | lock key and critical section. | lock-scoped execution | in-memory mutex |
| SH-052 `withOptimisticConcurrency` | Shared persistence mechanism | Reject stale policy/profile/BAA mutation. | Version/expected-state command. | conflict semantics. | applied/conflict result | last-write-wins update |
| SH-053 `transitionLifecycleState` | Shared mechanism / separate truth | Reuse state-machine plumbing. | Profile/BAA transition service. | Healthcare transition graph and reasons. | transition result | generic service owning Healthcare policy |
| SH-055 `runDeadlineExpiration` | Shared scheduler mechanism | Execute due BAA expiry. | Expiration worker. | What expires and resulting Healthcare effects. | due-work execution result | Module cron framework |
| SH-059 `verifyProviderWebhookSignature` | Provider-adapter contract | Authenticate BAA provider callback. | Raw webhook before parse/side effects. | selected provider verification config. | verified envelope/failure | unverified callback route |
| SH-060 `deduplicateProviderEvent` | Shared mechanism / separate provider truth | Prevent provider event replay. | After signature verification, before state effects. | Healthcare-owned event key/result record. | first/replay claim | reuse Stripe/Video processed event tables |
| SH-061 `translateProviderStatus` | Provider-adapter contract | Map provider states into BAA domain input. | Adapter boundary. | BAA-specific mapping. | canonical normalized result | global provider status mapper |
| SH-062 `reconcileProviderState` | Provider-adapter contract | Repair missed/stuck provider state. | Scheduled/manual reconciliation. | Healthcare discrepancy/transition policy. | normalized reconciliation result | provider object as truth |
| SH-070 `deleteProviderResource` | Provider/privacy contract | Execute provider-side deletion where allowed. | Privacy fulfillment. | healthcare retention/legal decision remains external input. | deletion/anonymization result | Privacy module direct provider SDK |
| SH-078 `minimizeAndRedactProviderInput` | Provider/privacy security capability | Send only approved minimum to provider and telemetry. | Before provider request/logging. | healthcare necessary fields. | minimized DTO | provider payload dump |
| SH-087 `issueSignedMediaUrl` | Media public capability | Access private BAA/evidence file after Healthcare entitlement decision. | Evidence viewing. | Whether actor/context may receive access. | short-lived signed access | local R2 presign |
| SH-090 `attachValidatedMedia` | Shared contextual contract — Media mechanics remain Media-owned | Associate a ready MediaAsset to healthcare evidence/context where approved. | BAA/evidence attachment. | healthcare business meaning. | validated ready asset/context link | scan/upload pipeline |
| SH-095 `executePrivacyInstruction` | Privacy protocol / owner executor | Apply an approved privacy instruction to Healthcare truth. | Privacy worker callback. | field/record disposition. | execution result/evidence | local PrivacyRequest workflow |
| SH-096 `enumerateSubjectData` | Privacy protocol | Enumerate Healthcare-owned subject data. | Privacy planning/export. | Healthcare inventory. | typed target inventory | global cross-table scan |
| SH-097 `evaluateRetentionRequirement` | Shared contract / separate policy facts | Tell Privacy whether Healthcare record may be erased now. | Privacy planning. | Healthcare/legal facts; exact duration may be unresolved. | retain/erase/review facts | local retention boolean |
| SH-098 `anonymizePersonalFields` | Shared mechanism / separate mappings | Apply approved minimization where hard delete is blocked. | Privacy execution. | field mapping and retained proof. | anonymization result | ad hoc blanket nulling |
| SH-091 `requestSearchProjectionRefresh` | Search public interface | Request source projection refresh only when Healthcare is approved requester for the source. | Downstream public-readiness effect. | Why healthcare changed. | accepted projection request | Typesense client/SearchUpsertEvent direct write |
| SH-123 `validateOwnedTargetReference` | Shared contract / target-owner implementation | Validate polymorphic target references safely. | Boundary/policy command. | Which Healthcare target types are supported. | target valid/context/version | cross-domain Prisma switch repository |

### Shared contract caution

`returnDecisionResult` / SH-015 is a **Proposed Ruling** in the canonical registry. Healthcare may align its TypeScript result shape with it, but must not make SH-015 a mandatory platform dependency or persist a universal decision table until approved.

## 16. Module-Internal Operations

These operations contain healthcare domain meaning and therefore remain local even when they use shared infrastructure.

| Operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `evaluateHealthcareRequirement` | Decide whether healthcare handling applies. | Taxonomy requirement facts, Offering/profile context, explicit boundary. | required/not-required/unsupported + trigger refs. | None | Determining healthcare applicability is Healthcare policy. |
| `deriveHealthcareProfileSummaryFromBaa` | Derive allowed profile summary movement from effective BAA truth. | Current profile, approved effective BAA, policy version. | proposed profile summary transition or no change. | `HealthcareComplianceProfile` when applied by command. | Prevents BAA summary duplication from becoming independent truth. |
| `selectEffectiveBaaAgreement` | Select the BAA whose evidence governs current readiness. | BAA set + policy/time. | BAA ref or explicit ambiguity. | None | Domain meaning is Healthcare-specific; rule remains unresolved until approved. |
| `validateHealthcareProfileTransition` | Validate one profile status transition. | current state, requested transition, source, evidence. | allowed/conflict + reason. | None until application service applies it. | Lifecycle policy belongs to Healthcare. |
| `validateBaaTransition` | Validate one BAA transition. | current state, normalized source, evidence, time. | allowed/conflict + reason. | None until applied. | Provider status alone cannot decide Workin Ants state. |
| `resolveExactHealthcareBoundary` | Resolve current explicit exact-target boundary. | validated target reference. | boundary or none. | None | Healthcare owns boundary semantics. |
| `evaluateHealthcareAdminPolicy` | Produce exact-target payload treatment after general authorization. | target, policy, boundary, requested operation. | allowed/redacted/blocked + handling instructions. | None | Healthcare-specific access policy. |
| `evaluateHealthcareVendorReadiness` | Determine whether a provider path is acceptable for a healthcare use case. | use case, provider capability/legal configuration facts, required BAA context. | permit/block/review + reason/evidence. | None | Healthcare decides healthcare acceptability; provider owner supplies capability facts. |
| `buildHealthcareReadinessDecision` | Compose healthcare-owned evidence into SH-020 result. | applicability, profile, BAA, boundary, provider policy, holds where mapped. | healthcare readiness result. | None | This is the Module's primary public decision. |
| `buildHealthcareEventPayload` | Produce minimized, versioned owner event payload. | aggregate change + request context. | safe domain event. | Outbox through SH-046. | Event meaning belongs to source owner. |
| `enumerateHealthcareSubjectData` | List Healthcare-owned privacy targets. | privacy subject/context. | typed target list and references. | None | Each data owner must understand its own records. |
| `resolveHealthcareRetentionFacts` | Return known retention facts or unresolved status. | record type/evidence/legal policy version. | erase/retain/review facts. | None | Healthcare provides record facts but does not invent legal duration. |

## 17. Shared Mechanism / Separate Truth Rules

| Mechanism | Reuse | Separate Healthcare truth that must remain local |
| --- | --- | --- |
| Lifecycle state-machine plumbing | SH-053 | `HealthcareComplianceStatus` and `BaaAgreementStatus` transition graphs, actor/source rules, and reasons. |
| Idempotency | SH-044 | Semantic identity of each BAA/profile/boundary/policy command and replay result. |
| Locking / optimistic concurrency | SH-051/052 | Which Healthcare aggregate/resource must be locked and what conflict means. |
| Domain event outbox | SH-046 | Healthcare event names, versions, payload schema, and emission conditions. |
| Event inbox/dedupe | SH-045 | What a consumed event means to Healthcare. |
| Provider webhook signature verification | SH-059 | Selected BAA provider algorithm/configuration and accepted event types. |
| Provider-event dedupe | SH-060 | Healthcare-specific processed-provider-event record and retention; must not reuse another Module's ledger. |
| Provider status translation | SH-061 | Mapping from the BAA/e-sign provider into Healthcare BAA transition inputs. |
| Provider reconciliation | SH-062 | Which discrepancies are repairable, which require review, and which domain transition results. |
| Queue/retry/dead letter | SH-047/048 | BAA expiry/reconciliation/provider work payload and business completion semantics. |
| Immutable document hashing/snapshot mechanics | Shared crypto/snapshot mechanisms if approved | BAA-specific parties, document identity, version, hash, signatures, effective state, retention. Transaction `AgreementDocumentSnapshot` is not BAA truth. |
| Sensitive access ledger | SH-030 / Audit-owned `AccessAuditLog` | Healthcare sensitivity, healthcare decision, target context, and access requirement. |
| File storage/signed URL | Media SH-087/090 | BAA/evidence business meaning and Healthcare access entitlement. |
| Readiness response shape | SH-015 if approved | Healthcare policy, reason codes, evidence, and policy version. |
| Search projection runner | SH-091/Search | Healthcare/source public-readiness facts; Search inclusion/execution remains Search-owned. |
| Privacy workflow | SH-095–098 | Healthcare record inventory, field mappings, and retention facts. |

## 18. Authentication and Authorization

### Authenticated actor requirement

All actor-initiated protected operations begin with SH-001 `resolveAuthenticatedActor`. Trusted system workers use the root-approved system-actor/service context; they do not forge a User.

### Role / Authority boundary

SH-002 `authorizeResourceAction` answers whether an actor may attempt a named action on the target. Healthcare supplies the action vocabulary and the minimum relationship facts available from the resource owner. Role / Authority owns permission interpretation.

Typical Healthcare actions include:

```text
healthcare.profile.declare
healthcare.profile.review
healthcare.baa.create
healthcare.baa.review
healthcare.boundary.mark
healthcare.admin_policy.manage
healthcare.evidence.view
healthcare.case.view
```

Exact action names must match the Role / Authority contract and code standards.

### Contextual authorization order

For an admin/support payload read:

```text
1. resolveAuthenticatedActor
2. authorizeResourceAction on the resource owner/context
3. resolve contextual resource entitlement if the resource owner requires it
4. resolveEffectiveHealthcareBoundary
5. evaluateHealthcareAdminAccess
6. resource owner enforces allow/redact/block before payload leaves the server
7. recordSensitiveAccess with the actual decision/outcome
```

A client-side hide/show rule is never sufficient.

### Resource ownership and participant context

Healthcare does not infer Order participants, Booking participants, Thread participants, Media ownership, or video-room participants. Those facts come from the source owner through a narrow interface / SH-123 validation path.

### Admin/support actions

Admin/support identity is not automatic healthcare access. Restricted case lists should be metadata-minimized. BAA/evidence file access and payload reads must satisfy general authorization, healthcare policy, and SH-030 audit requirements.

### Step-up

The supplied evidence confirms SH-014 as the platform primitive for high-risk sensitive actions but does not establish a blanket rule that every Healthcare operation requires step-up. **Unresolved U-HC-07:** which BAA document, policy-management, or PHI administration actions require fresh step-up assurance. Until root/security policy settles this, do not invent a Module-wide MFA rule; consume SH-014 for any action the approved security matrix marks sensitive.

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying truth owner | Query consumed | Healthcare action gated | Local composition | Result |
| --- | --- | --- | --- | --- | --- |
| Actor authentication | Identity & Access | SH-001 | Every protected actor command/query | Requires trusted actor before Healthcare work | actor/system context or stop |
| General permission | Role / Authority | SH-002 | BAA/profile/boundary/policy/admin access | Healthcare supplies resource/action facts | allowed or stop before healthcare payload processing |
| Healthcare trigger | Taxonomy + source context | SH-022 plus owner context | Lane declaration/readiness/public/delivery checks | Healthcare interprets canonical trigger and explicit boundary | required/not required/unsupported |
| Healthcare consent/disclosure | Consent & Disclosure | SH-008 | Only healthcare actions whose approved policy requires proof | Healthcare decides sufficiency for this action | proof accepted/missing/invalid |
| Healthcare profile | Healthcare | local query | SH-020 and local transitions | Evaluate current owned status | ready/pending/rejected/suspended dimension |
| BAA | Healthcare | local effective BAA query | healthcare readiness and provider/delivery activation | BAA truth separate from profile summary | satisfied/pending/missing/expired/revoked/ambiguous |
| Explicit target boundary | Healthcare | local boundary query | healthcare-sensitive data access | Exact boundary semantics now; inheritance only after U-09 | boundary/no boundary/unsupported |
| Provider readiness | Provider owner + Healthcare | capability fact + local policy | Healthcare-sensitive live/video/e-sign path | Healthcare decides healthcare suitability | approved/block/review/unavailable |
| ComplianceHold | Admin Review / Compliance Hold | SH-011 | Only actions mapped as hold-sensitive | Hold remains external stop-sign truth | allow/block with hold refs |
| Professional readiness | Professional Eligibility | SH-016 | Not generally a Healthcare-owned prerequisite; used only where a Healthcare workflow explicitly needs composed seller state | Healthcare must not recreate it | owner decision |
| Verification/license | Trust | SH-018 if explicitly required | Only a healthcare policy expressly requiring Trust evidence | Trust remains source truth | owner decision |
| Track entitlement | Track Subscription & Entitlement | SH-005 if a healthcare feature is explicitly plan-gated in future | Only the specific entitlement-gated feature | Entitlement is commercial policy, not healthcare truth | owner decision |

### Critical distinction

Healthcare's SH-020 is **one input** to Professional Eligibility's SH-016. Healthcare must not become the final seller-readiness composer, and Professional Eligibility must not reconstruct BAA/boundary/provider policy from Healthcare tables.

## 20. Provider Integrations

### Current provider status

A BAA/e-sign provider is contemplated but **not canonically selected**. Daily/Agora/Mux references in planning materials describe candidate delivery/provider paths and legal-review constraints, not permission for Healthcare to instantiate those provider SDKs. Video Session owns video mechanics.

### Provider-neutral port

Healthcare may define a BAA/e-sign port before a concrete provider is selected. The port exposes Workin Ants business needs, not provider DTOs.

### Adapter responsibilities

An approved adapter may own:

- provider request mapping;
- provider credential usage;
- webhook envelope parsing;
- provider-specific signature parameters used through SH-059;
- provider event identity extraction;
- provider status mapping through SH-061;
- provider error classification;
- fetch/reconciliation calls;
- provider-side revoke/delete actions where supported and approved.

### Credential rules

- Credentials are server-side secrets managed by the root secret/config mechanism.
- Never persist secrets in Healthcare domain tables.
- Never log authorization headers, webhook secrets, raw signatures beyond the safe verification metadata approved by Ops.

### Webhook path

Production path, only after U-07/U-08 are resolved:

```text
raw webhook
→ SH-059 verifyProviderWebhookSignature
→ extract provider event ID
→ SH-060 claim owner-specific Healthcare provider event
→ adapter maps provider result through SH-061
→ validate BaaAgreement transition
→ authoritative BAA/profile write + SH-046 event in transaction
→ mark provider event processed with safe result
→ downstream reactions are replay-safe
```

No side effect may occur before signature verification and event claim.

### Provider-event dedupe truth

**Confirmed need, unresolved schema:** Healthcare needs its own processed-provider-event truth before automated BAA callbacks. It must not reuse `ProcessedStripeEvent`, `ProcessedCalendarEvent`, `ProcessedVideoProviderEvent`, `AuditEvent`, `QueueJob`, or `providerReferenceId` alone.

### Reconciliation

SH-062 is used to reconcile provider state after missed callbacks or ambiguous failures. Reconciliation may repair Workin Ants state only by passing the same transition policy as normal callbacks. Unknown provider states fail safe and become operationally visible.

### Retry and idempotency

Network/provider errors may retry through SH-047/048. Domain commands remain SH-044 idempotent. Provider create/send requests need a provider idempotency/reference strategy where supported.

### Privacy deletion

Provider-side erasure/anonymization uses SH-070 only after Privacy supplies an approved instruction and Healthcare retention facts permit the action. Retention-sensitive BAA proof is never deleted by a generic “delete user” path.

### Operational failures

Use SH-037 with sanitized metadata. `IntegrationFailure` never replaces `BaaAgreement.status`.

### Provider integrations Healthcare does not own

Healthcare must not instantiate or operate:

- Daily/Agora room/token clients;
- Mux upload/playback clients;
- Cloudflare R2 object client for general file mechanics;
- Search/Typesense clients;
- email/SMS/push providers.

It evaluates healthcare suitability or contextual access and calls the owning Module.

## 21. Events and Outbox

### Event rules

- Events describe facts that already occurred; they are not disguised commands.
- The source write and outbox append use SH-046 transactionally.
- Payloads are versioned, schema-validated, PHI-minimized, and include correlation/request IDs where safe.
- Consumers use SH-045 or their canonical inbox/dedupe mechanism.
- Replayed or out-of-order events must not duplicate downstream effects.

### Module-owned event families

#### `HealthcareComplianceProfileChanged.v1`

Emitted after an approved profile state/meaningful healthcare summary mutation.

Minimum safe payload:

```text
healthcareComplianceProfileId
professionalProfileId
previousStatus
newStatus
reasonCode
sourceType
sourceReferenceId?        # safe, non-provider-secret reference
effectiveAt
aggregateVersion/sourceVersion
correlationId
```

No BAA document content or PHI.

#### `BaaAgreementChanged.v1`

Emitted after an approved BAA lifecycle transition.

```text
baaAgreementId
healthcareComplianceProfileId
previousStatus
newStatus
reasonCode
expiresAt?                # if safe/relevant
aggregateVersion/sourceVersion
correlationId
```

Provider payload is not included.

#### `HealthcareDataBoundaryMarked.v1`

```text
boundaryId
targetType
targetId
sensitivity
reasonCode?               # controlled/safe, not PHI narrative
sourceVersion
correlationId
```

#### `HealthcareAdminAccessPolicyChanged.v1`

```text
policyId
targetType
targetId
previousMode?
newMode
reasonCode?
sourceVersion
correlationId
```

#### `HealthcareReadinessChanged.v1`

Emitted only when a source mutation changes an externally meaningful healthcare readiness dimension.

```text
professionalProfileId
targetType?
targetId?
previousDecisionClass?
newDecisionClass
reasonCodes[]
evidenceRefs[]             # safe IDs only
policyVersion
sourceVersions
correlationId
```

This event tells consumers to reevaluate; it does not instruct Marketplace to set `Offering.status` or Search to delete an index document.

### Event history versus Audit

A future Healthcare domain event history table would be Module-owned if explicitly added. The current architecture does not authorize one. SH-046 outbox and AuditEvent serve separate infrastructure/evidence purposes and must not be treated as Healthcare's historical source ledger by accident.

## 22. Background Jobs / Scheduled Work

### `baaExpirationWorker`

- **Purpose:** find due BAA agreements with approved expiry semantics and apply `expireBaaAgreement` idempotently.
- **Owner:** Healthcare; queue/scheduler mechanics are shared.
- **Input:** BAA ID, expected status/version, due timestamp, policy version.
- **Idempotency key:** `baa-expire:<baaAgreementId>:<effectiveDueAt>` or root-approved equivalent.
- **Retryable failures:** transient database/queue/dependency failures.
- **Permanent failures:** invalid transition, unresolved effective-BAA policy, record no longer due.
- **Dead letter/manual review:** persistent unexpected transition/evidence inconsistency becomes operationally visible; do not force status.
- **Truth updated:** `BaaAgreement`; profile summary/readiness only through approved local policy.
- **Telemetry:** IDs/status/reason only; no PHI/document/provider payload.

### `baaProviderEventWorker`

Only enabled after U-07/U-08 and provider selection.

- verifies/uses already verified envelope according to route architecture;
- claims owner-specific provider event via SH-060;
- translates provider state;
- applies idempotent BAA transition;
- publishes owner events;
- records operational failure separately.

### `baaReconciliationWorker`

Only enabled for an approved provider adapter.

- **Purpose:** reconcile missed/stuck provider state.
- **Input:** BAA ID/provider reference/correlation.
- **Idempotency:** one repair effect per source/provider version.
- **Retry:** provider/network errors retry; unknown state/manual mismatch goes to review/dead-letter.
- **Truth:** Healthcare BAA state changes only through transition policy.

### Boundary propagation worker

**Not implementable until U-09.** Current schema supports exact marking/query, not inferred propagation/retirement. Do not create a worker that guesses parent-child inheritance.

### Policy-history worker

None. Policy history is a data-model decision, not something a worker can reconstruct from current mutable rows.

## 23. Concurrency and Idempotency

### Races to prevent

- two actors concurrently declaring the same healthcare profile;
- manual and provider BAA transitions racing;
- duplicate webhook deliveries;
- expiry racing with provider signed/verified event;
- revoke racing with verify;
- concurrent exact-boundary creation;
- concurrent admin-policy updates;
- privacy deletion racing with BAA/provider transition;
- downstream consumer replay causing duplicate hold/notification/Search effects.

### Lock / resource keys

Recommended keys, using the root primitive rather than in-memory locks:

```text
healthcare-profile:<professionalProfileId>
baa-agreement:<baaAgreementId>
healthcare-boundary:<targetType>:<targetId>
healthcare-admin-policy:<targetType>:<targetId>
```

### Database constraints

- `HealthcareComplianceProfile.professionalProfileId` unique.
- `HealthcareDataBoundary(targetType,targetId)` unique.
- `HealthcareAdminAccessPolicy(targetType,targetId)` unique.
- Provider-event uniqueness must be added only after U-08 defines the owner-specific schema.

### Transaction boundaries

An authoritative Healthcare mutation and its required owner-event outbox record commit atomically. When profile summary changes because a BAA changes, BAA + profile summary + outbox should commit in one local transaction when they are in the same database boundary.

Cross-Module commands do not participate in distributed database transactions. Use durable events/commands and idempotent consumers.

### Optimistic vs pessimistic strategy

- Prefer optimistic expected-state/version checks for ordinary user/admin edits where a version source exists or can be safely established.
- Use SH-051 aggregate lock/transaction row lock for high-risk transition races when optimistic state alone cannot safely serialize the effect.
- Do not invent process-memory mutexes.

### Replay semantics

Same idempotency key + same semantic fingerprint returns the original success/no-op result. Same key + materially different request returns deterministic conflict. Replayed provider/domain events return already-processed outcome and do not repeat side effects.

## 24. Media / Storage

### Business meaning owned here

A BAA/evidence attachment may have healthcare business meaning and an approved relationship to a `BaaAgreement`. Healthcare owns that contextual meaning and whether the evidence may be used for readiness.

### Mechanics owned elsewhere

Media / File Access owns:

- upload session;
- MIME/binary validation;
- malware scan;
- metadata scrubbing;
- object key/bucket selection;
- storage provider client;
- MediaAsset lifecycle;
- signed access URLs / MediaAccessGrant;
- object deletion.

### Upload context

If a BAA/evidence upload context is not already a canonical Media profile, Healthcare must request an architecture addition through Media rather than creating a private uploader. Media determines safe file types/limits and private storage behavior.

### `documentMediaId`

The current BAA model stores a UUID but no explicit Prisma relation. **Unresolved U-HC-05:** whether this becomes a direct `MediaAsset` relation or is superseded by an immutable BAA document snapshot/evidence record after U-07.

### Signed access

BAA/evidence access requires:

```text
general authorization
+ Healthcare contextual access decision
+ Media-owned file entitlement/mechanics
→ SH-087 short-lived access
→ SH-030 sensitive access proof where required
```

Permanent public URLs are prohibited.

## 25. Search / Projection

Healthcare source truth consists of the four owner models and SH-020 decisions. Search is a rebuildable projection.

### Indexing triggers

Healthcare status/BAA/readiness changes can make a Professional or Offering no longer publicly eligible. Healthcare emits owner facts; the source owner reevaluates its own public state and invokes SH-091 according to PR-HC-04 and the CL-03 integration contract.

### Search must not reconstruct

Search must not derive healthcare eligibility from:

- `Offering.requiresHealthcareCompliance` alone;
- `HealthcareComplianceProfile.status` alone without the owner decision contract when provider/BAA context matters;
- TrustBadge/license state;
- provider state;
- `DataSensitivity.healthcare` alone;
- absence/presence of a Search document.

### PHI boundary

Raw PHI, healthcare-sensitive messages/files, BAA document contents, exact private healthcare details, and access-policy reasons are not Search fields.

## 26. Notification

Healthcare owns business triggers and safe intent; Notification owns channel/template/provider/delivery mechanics.

Candidate notification triggers, only when product/compliance policy approves them:

- BAA action required;
- BAA sent;
- BAA signed but verification pending;
- BAA verified;
- BAA rejected/revoked/expired;
- healthcare profile requires remediation;
- healthcare profile suspended/restored after an approved rule;
- provider workflow requires input;
- admin review outcome safe for user delivery.

### Payload rule

Notifications may include safe identifiers, status category, next action, and destination route. Do not include PHI, raw BAA text, provider response payload, private message content, or sensitive rejection narrative.

Use SH-041. Never call SES/SMS/Web Push/FCM/other delivery providers from Healthcare.

## 27. Audit and Sensitive Access

### Domain truth

Healthcare-owned models and events represent healthcare business truth.

### Generic AuditEvent

Use SH-029 for important actor/system actions such as healthcare profile review, BAA verification/revocation, boundary marking, or policy changes when the root audit policy requires it. AuditEvent is not BAA/profile state.

### Sensitive access

Use SH-030 for healthcare-sensitive access including, where policy requires:

- viewing or issuing access to private BAA evidence;
- admin/support healthcare payload view;
- redacted view;
- blocked view/attempt;
- healthcare-sensitive message/file/video access;
- course playback access when healthcare-sensitive and the policy requires proof.

The resource owner may be the caller that records the final actual access outcome; Healthcare supplies the decision and sensitivity context. The system must avoid double-recording one logical access unless the audit contract intentionally distinguishes policy check from actual resource issuance.

### AccessAuditLog boundary

`AccessAuditLog` is Audit-owned despite containing `HealthcareAccessDecision`. Healthcare owns the meaning of its decision vocabulary; Audit owns persistence/hash-chain/access-event mechanics. Enum/schema evolution requires a stable cross-Module contract.

## 28. Privacy and Retention

### Subject-data inventory

Healthcare contributes at least:

- `HealthcareComplianceProfile` by ProfessionalProfile/User lineage;
- `BaaAgreement` rows;
- `HealthcareDataBoundary` rows whose target relates to the subject;
- `HealthcareAdminAccessPolicy` rows whose target relates to the subject;
- Healthcare-owned processed provider events if later added;
- provider references/resources;
- MediaAsset references used as BAA/evidence, without owning the asset;
- owner-event references where privacy policy applies.

### Privacy executor

Implement SH-096 enumeration, SH-097 retention facts, SH-095 execution, and SH-098 anonymization mappings as appropriate.

### Behavior categories

- **Erase:** delete Healthcare data only when Privacy instructs it and retention permits.
- **Anonymize:** remove nonessential personal identifiers when retained proof can remain meaningful.
- **Revoke:** revoke provider/resource access when ordinary lifecycle/retention policy calls for it; revocation is not a substitute for erasure.
- **Retain:** preserve records when an approved retention exemption applies; return evidence/reason to Privacy.
- **Review:** when exact legal retention is unresolved, do not destructively delete. Return `retention_policy_unresolved` / manual-review disposition.

### BAA cascade risk

Current Prisma cascade from profile to BAA must not be treated as the approved privacy behavior. U-18 and U-07 must be settled before destructive production deletion of retained BAA proof.

### Export contribution

If Privacy supports export, Healthcare returns a minimized, user-appropriate representation of its owned records. Do not export internal provider secrets, other users' data, access-control internals, or raw admin-only evidence merely because it exists.

## 29. Observability

### Structured logs

Use the canonical logger/request context. Useful safe dimensions include:

```text
module=healthcare_regulated_services
operation
aggregateType
aggregateId
statusBefore/statusAfter
reasonCode
providerKind             # generic/configured provider identifier if approved
jobType
retryCount
requestId/correlationId
outcome
```

Never log PHI, BAA document text, private message bodies, raw provider payloads, secrets, access tokens, webhook bodies, or private file URLs.

### IntegrationFailure / SystemEvent

Provider timeouts, webhook verification failures, reconciliation mismatches, queue exhaustion, and unavailable dependencies may be recorded through Observability. These records diagnose execution and never substitute for `BaaAgreement` or healthcare profile state.

### Metrics

Relevant metrics may include:

- SH-020 decision count by safe decision/reason category;
- BAA status transition count;
- BAA expiry due/completed/failure count;
- provider webhook verified/rejected/duplicate count when enabled;
- reconciliation mismatch count;
- healthcare access decision count by allowed/redacted/blocked category;
- SH-030 audit failure count;
- queue retry/dead-letter count;
- dependency-unavailable count and latency.

Metrics must not use target names/medical details or arbitrary free text.

## 30. Security Boundaries

1. Validate every command/query payload server-side with the root validation standard (Zod where current code standards require it).
2. Treat all IDs and target-type combinations as untrusted; validate supported target type and target existence through owner interfaces.
3. Reject direct client-supplied provider status as authoritative input.
4. Provider secrets stay server-side and out of database domain records/logs.
5. Webhook signature verification occurs on the raw body before domain side effects.
6. Provider events are deduplicated before mutation.
7. Use private Media storage and short-lived access; never permanent public BAA/PHI URLs.
8. Redaction occurs before payload serialization/return, not by hiding fields in the browser.
9. Do not persist raw PHI in audit, event, notification, telemetry, or provider-event metadata unless explicitly required and approved.
10. Do not write custom cryptography. Use approved hash/HMAC/encryption primitives if U-07 requires immutable evidence hashes.
11. Rate limit externally reachable provider/webhook/admin endpoints according to root security standards.
12. Temporary provider/session tokens are never stored as durable healthcare truth and are returned only to the authorized caller when required.
13. Exact policy reasons should be controlled/minimized; free-text reasons may themselves contain sensitive information.
14. Any feature requiring step-up must use SH-014, never a Healthcare-local OTP/MFA implementation.

## 31. Error / Decision Result Pattern

### Public error categories

Healthcare public interfaces should distinguish:

- `validation_error` — malformed/unsupported input;
- `unauthenticated` — no trusted actor when required;
- `unauthorized` — Role / Authority denies the operation;
- `not_found` — source target/profile/record not found or not visible to caller;
- `conflict` — stale/invalid lifecycle transition or optimistic concurrency failure;
- `policy_blocked` — Healthcare policy says the requested action cannot proceed;
- `redaction_required` — caller may proceed only with specified reduced payload;
- `consent_required` — required Consent proof is absent/invalid;
- `dependency_unavailable` — source owner/provider/shared capability temporarily unavailable;
- `provider_failure` — provider operation failed after safe translation;
- `unsupported_operation` — architecture intentionally does not support the requested path yet;
- `manual_review_required` — evidence cannot be resolved automatically;
- `retention_policy_unresolved` — destructive privacy action cannot be safely executed;
- `internal_error` — unexpected failure with correlation ID and no sensitive detail.

### Decision result

SH-020 should return a stable, audience-safe structure equivalent to:

```text
decision
reasonCodes[]
evidenceRefs[]
policyVersion
evaluatedAt
expiresAt? / validUntil?        # only when meaning is established
warnings[]?
nextActions[]?                  # safe remediation identifiers, not free-form legal advice
sourceVersions
```

Do not leak raw provider errors. Map them into stable categories and preserve provider detail only in sanitized operational evidence.

## 32. Testing Architecture

### Domain unit tests

- healthcare requirement trigger composition;
- SH-020 readiness matrix;
- profile transition guards;
- BAA transition guards;
- BAA-to-profile summary derivation;
- exact boundary resolution;
- exact admin-policy decision;
- vendor-readiness policy;
- reason-code safety.

### State-transition tests

For every enabled profile/BAA transition:

- permitted predecessor;
- forbidden predecessor;
- actor/source permission;
- duplicate replay;
- stale expected state;
- terminal/exception behavior;
- event emission exactly once.

### Public contract tests

- SH-020 input/output compatibility;
- `getHealthcareComplianceContext` minimization;
- owner target validation contract;
- `evaluateHealthcareAdminAccess` semantics;
- event payload versions;
- privacy executor contracts.

### Database/integration tests

- one HealthcareComplianceProfile per ProfessionalProfile;
- unique exact boundary;
- unique exact admin policy;
- local multi-record transaction (BAA/profile/outbox);
- rollback on failed invariant;
- no direct writes to foreign Module tables;
- provider-event uniqueness when U-08 schema is approved.

### Authorization tests

- owner/professional/admin/support/system cases;
- unauthorized caller stops before healthcare detail leakage;
- Role decision and Healthcare access decision are independent;
- step-up scenarios for actions once approved.

### Compliance/security tests

- no `User.isHealthcareProvider` behavior;
- `DataSensitivity` alone cannot satisfy healthcare boundary/readiness;
- no PHI in event/log/notification/audit metadata fixtures;
- redaction occurs server-side before payload leaves resource owner;
- required accesses create SH-030 proof;
- permanent public healthcare file URL cannot be issued.

### Idempotency/concurrency tests

- concurrent lane creation;
- duplicate BAA command;
- verify/revoke race;
- expiry/provider-event race;
- duplicate boundary mark;
- concurrent policy update;
- provider webhook replay/out-of-order when enabled.

### Provider adapter tests

When a provider is enabled:

- raw signature acceptance/rejection;
- duplicate event claim;
- unknown provider status;
- mapping tests;
- retryable/permanent error classification;
- reconciliation;
- minimized provider input;
- provider deletion where supported.

### Privacy tests

- subject enumeration;
- retained/review/erase/anonymize dispositions;
- unresolved retention blocks destructive action;
- Media/provider deletion delegated to owner;
- export minimization.

### E2E participation tests

- healthcare-sensitive Offering publish attempt is blocked until Healthcare/other CL-03 gates pass;
- non-healthcare Offering does not traverse unnecessary BAA workflow;
- healthcare-sensitive admin message/file/video view is redacted/blocked as returned by Healthcare and audited;
- healthcare readiness change causes source-owner public readiness reevaluation without Healthcare mutating the foreign record.

## 33. Module Invariants

**Rules coding agents must never violate:**

1. Healthcare is a contextual lane, never a User type or blanket platform mode.
2. `HealthcareComplianceProfile`, `BaaAgreement`, `HealthcareDataBoundary`, and `HealthcareAdminAccessPolicy` are the only confirmed Healthcare-owned source models in the current schema.
3. `BaaAgreement` is BAA execution truth; `ConsentLog`, Transaction `Agreement`, provider state, and profile summary cannot replace it.
4. Healthcare may summarize BAA progress on its profile only through an approved BAA-derived rule; duplicated summary state may never drift independently.
5. Professional license/background-screening truth remains Trust-owned.
6. ProfessionalProfile lifecycle and final seller readiness composition remain Professional Eligibility-owned.
7. Offering lifecycle remains Marketplace-owned.
8. Generic authorization remains Role / Authority-owned; admin role alone never grants PHI access.
9. General authorization must succeed before a Healthcare payload decision is evaluated for that actor/resource.
10. `HealthcareDataBoundary` is more specific than generic `DataSensitivity`; generic sensitivity alone cannot stand in for the boundary.
11. A polymorphic healthcare target is validated through its owner; never through a universal cross-domain Prisma repository.
12. Boundary clearing/retirement/inheritance is disabled until U-09 is approved.
13. Historical/inherited admin access policy claims are disabled until U-10 is approved.
14. Do not rely on `HealthcareAccessDecision.blocked` versus `denied` across Modules until U-11 is resolved.
15. `lockedHealthcareFlag` is inert as a policy source until its meaning is approved.
16. A BAA/e-sign provider is a rail/evidence source, never Workin Ants truth.
17. Automated BAA webhook side effects are disabled until U-07/U-08 and owner-specific provider dedupe truth are approved.
18. Never reuse another provider Module's processed-event table.
19. Healthcare owns no generic file storage, signed URLs, messaging, video rooms/tokens, Search, Notification delivery, Privacy orchestration, or generic Audit/Ops systems.
20. Every required healthcare-sensitive actual access must produce canonical access proof; Audit storage remains Audit-owned.
21. PHI/private evidence must not appear in telemetry, analytics, event payloads, notification payloads, or unapproved audit metadata.
22. Search is projection and cannot reconstruct Healthcare policy.
23. ComplianceHold is the reusable stop sign; do not add local generic blocked flags.
24. Owner mutations and owner-event outbox writes are transactionally coupled where downstream correctness depends on them.
25. All replay-prone commands/provider events/jobs are idempotent.
26. Concurrency is enforced with database constraints/transactions/shared locks, never process-memory locks.
27. Privacy destructive behavior is blocked when retention is unresolved.
28. Current Prisma cascade behavior is not proof of approved legal deletion semantics.
29. No provider SDK type may leak into the public Healthcare contract.
30. Unresolved architecture remains unavailable/review, never guessed into production behavior.

## 34. Prohibited Duplicate Implementations

Do **not** generate any of these inside `healthcare_regulated_services`:

- `healthcareAuth.ts`, `currentUser.ts`, or local session resolver — use SH-001.
- `healthcarePermissions.ts`, `isHealthcareAdmin`, generic RBAC middleware — use SH-002.
- `healthcareConsent.ts` or generic BAA-consent table replacing ConsentLog — use SH-008/010; retain BAA truth separately.
- `healthcareHold.ts`, `isBlocked`, generic suspension flag replacing ComplianceHold — use SH-011/012/013.
- a universal `readiness.service.ts` that owns Professional/Trust/Payment/Healthcare policy — Healthcare owns only SH-020.
- local `audit_log`, `phi_access_log`, generic append-only audit writer — use SH-029/030.
- using `AuditEvent` as BAA/provider/domain transition truth.
- local `queue.ts`, retry framework, dead-letter table, scheduler — use SH-047/048/055.
- local idempotency table/helper — use SH-044.
- in-memory locks for profile/BAA/policy transitions — use root concurrency primitives.
- local R2/S3 client, MIME sniffer, malware scanner, object-key generator, signed URL generator — Media owns mechanics.
- a Healthcare-owned video room/token client or `ProcessedVideoProviderEvent` writer — Video Session owns it.
- a Typesense client, SearchUpsertEvent repository, indexer, or de-index worker — Search owns it.
- a local email/SMS/push provider integration — Notification owns delivery.
- a Healthcare `PrivacyRequest` or erasure-job engine — Privacy owns orchestration.
- a generic provider-status mapper spanning BAA, payment, video, calendar, or verification.
- reuse of `ProcessedStripeEvent`, `ProcessedCalendarEvent`, or `ProcessedVideoProviderEvent` for BAA callbacks.
- `hipaaFlag`, `healthcareUser`, `isHealthcareProvider`, `baaAccepted`, `canViewPhi` booleans as source truth.
- generic cross-domain `findTargetByTypeAndId` repositories.
- custom crypto/hash implementation for BAA evidence.
- raw provider payload storage as a substitute for canonical BAA evidence.

## 35. Unresolved Decisions

These are implementation constraints, not invitations to guess.

| ID | Decision | Why unresolved / impact |
| --- | --- | --- |
| U-07 | Which parties/signers/countersigners and immutable document/version/hash proof must `BaaAgreement` preserve? | Current model is insufficient for full execution proof. Blocks production BAA automation/final legal-compliance claim. |
| U-08 | Which BAA/e-sign provider is selected and what Healthcare-owned processed-provider-event schema proves callback dedupe? | No canonical provider/dedupe record. Blocks automated production webhook effects. |
| U-09 | How is `HealthcareDataBoundary` retired/cleared and how does inherited propagation work? | Current model is presence/absence only. Blocks clear/propagation automation. |
| U-10 | How is `HealthcareAdminAccessPolicy` versioned/effective and how do parent/child policies interact? | Current model is one mutable exact-target row. Blocks historical/inherited policy claims. |
| U-11 | Canonical distinction between `HealthcareAccessDecision.blocked` and `denied`. | Current vocabulary is ambiguous across auth/policy layers. Blocks universal decision semantics. |
| U-12 | Owner/derivation semantics for generic `DataSensitivity`. | Multiple Modules reference it; Healthcare boundary is more specific. Blocks generic sensitivity automation, not explicit healthcare boundaries. |
| U-18 | Exact retention periods for healthcare/BAA proof. | Compliance pack does not establish durations. Blocks destructive deletion and production retention scheduler. |
| U-HC-01 | How is one effective/current BAA selected when a profile has multiple `BaaAgreement` rows? | Schema allows many; no current/active uniqueness field. Readiness must not use arbitrary “latest wins.” |
| U-HC-02 | Complete `HealthcareComplianceProfile` transition graph, including restore/reopen rules. | Enum exists without full legal/domain adjacency. |
| U-HC-03 | Complete `BaaAgreement` transition graph, rejection evidence, reissue/reopen semantics. | Enum/timestamps do not establish all transitions. |
| U-HC-04 | Meaning and authority of `lockedHealthcareFlag`. | Loose boolean is not defined strongly enough to gate actions. Must remain inert. |
| U-HC-05 | Whether `BaaAgreement.documentMediaId` becomes a Prisma `MediaAsset` relation or a dedicated immutable BAA evidence/snapshot record. | Current UUID has no relation; U-07 may require richer proof. |
| U-HC-06 | Canonical source of healthcare provider-capability/BAA readiness facts for video/e-sign/storage use cases. | Healthcare decides suitability but must not own provider mechanics. Avoid provider-name allowlists in random code. |
| U-HC-07 | Which Healthcare admin/BAA evidence operations require SH-014 step-up. | Root/security evidence establishes the primitive but not the Healthcare action matrix. |
| U-HC-08 | Redaction instruction schema/field-mask contract resource owners must enforce. | `redact_payload` exists but the exact portable instruction format is not established. |

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. `healthcare_regulated_services` is a CL-03 compliance Module with build status `mvp_active_legal_gated`.
2. It owns `HealthcareComplianceProfile`, `BaaAgreement`, `HealthcareDataBoundary`, `HealthcareAdminAccessPolicy`, and the five named healthcare enums.
3. Healthcare is a contextual lane, not a User type.
4. BAA execution truth is separate from ConsentLog, Transaction Agreement, Trust verification, and provider objects.
5. SH-020 `evaluateHealthcareReadiness` is the canonical public Healthcare decision interface.
6. Professional Eligibility remains the final composer of professional action readiness; Marketplace remains owner of Offering lifecycle.
7. Role / Authority owns general permission; Healthcare owns post-authorization healthcare payload policy.
8. Media, Messaging, Video, Search, Audit, Notification, Privacy, Hold, and Ops retain their own mechanics and source truth.
9. Exact healthcare boundary marking/query is implementable now after owner target validation.
10. Exact current admin policy can be implemented only within the explicitly limited current/exact-target semantics; historical/inherited claims are blocked by U-10.
11. Automated BAA provider callbacks are not production-ready until U-07/U-08 are resolved; a constrained manual/provider-neutral path may proceed without pretending legal completeness.
12. Every cross-Module read uses an owner public contract, not direct foreign Prisma access as the default integration pattern.
13. All owner events use transactional publication; generic Audit/Ops records do not replace domain truth.
14. Privacy orchestration remains Privacy-owned; destructive behavior stays blocked where retention is unresolved.

### Proposed Rulings requiring approval before dependent implementation

- **PR-HC-01:** Healthcare profile BAA-progress states are derived summary only; BAA is authoritative.
- **PR-HC-02:** enable BAA mutation commands only against an explicit transition matrix and approved effective-BAA selection rule.
- **PR-HC-03:** general authorization denial occurs before Healthcare policy; until U-11, cross-Module admin payload decision narrows to allowed/redacted/blocked after authorization.
- **PR-HC-04:** Healthcare emits readiness facts; Professional Eligibility/Marketplace/source owners request Search refresh for their own public projections.

## 37. Coding-Agent Usage

Before implementing any Healthcare feature, the coding agent must read, in this order unless the repository defines a stricter one:

1. `context/project-overview-v3.md`;
2. root architecture (**missing**; see `context/context-map.md`);
3. root code standards (**missing**; see `context/context-map.md`);
4. Canonical Shared Operations Registry (`context/shared/shared-operations.md`);
5. CL-03 `context/clusters/professional supply & readiness/professional-supply-readiness-architecture.md`;
6. CL-03 `context/clusters/professional supply & readiness/professional-supply-readiness-build-plan.md`;
7. this `context/clusters/professional supply & readiness/Healthcare Regulated Services module/healthcare-regulated-services-module-architecture.md`;
8. this Module's `context/clusters/professional supply & readiness/Healthcare Regulated Services module/healthcare-regulated-services-module-implementation-plan.md`;
9. public-interface sections for direct dependencies used by the current feature, especially Identity & Access, Role / Authority, Consent & Disclosure, Taxonomy, Professional Eligibility, Marketplace Supply, Media / File Access, Audit / Event Ledger, Privacy / Data Erasure, Notification, Admin Review / Compliance Hold, Search, and Video Session as applicable;
10. progress tracker (**missing**; see `context/context-map.md`) and any approved ADR/ruling that resolves U-07–U-18 or U-HC-* items.

The agent must then:

- verify the current numbered feature and prior exit gate;
- produce the required feature implementation specification before coding;
- implement only the feature's approved scope;
- stop and report a blocker when an unresolved ruling is required;
- never satisfy a dependency by creating a local duplicate;
- update architecture only when a binding decision legitimately changes, never merely because implementation was convenient.
