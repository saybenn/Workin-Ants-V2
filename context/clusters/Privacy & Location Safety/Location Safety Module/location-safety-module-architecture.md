# Location Safety Module Architecture

> **Module ID:** `location_safety`  
> **Module name:** Location Safety Module  
> **Module type:** `compliance`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** CL-08 Privacy & Location Safety  
> **Document status:** Implementation-grade Module architecture; decision-gated where evidence remains unresolved  
> **Intended audience:** Coding agents, developers, reviewers, maintainers, compliance/security reviewers, and future architecture agents  
> **Relationship to root architecture:** Root Workin Ants architecture and project-wide code standards are currently missing; their future roles do not substitute for existing concern-specific authority. This file narrows platform rules to Location Safety; it does not redefine platform-wide identity, authorization, audit, search, privacy, queue, crypto, or observability ownership.<br>
> **Relationship to Cluster architecture:** Subordinate to `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`. The Cluster coordinates Location Safety with Privacy / Data Erasure but owns no lifecycle or schema. This file is authoritative for Location Safety-local implementation boundaries once its rulings are consistent with stronger root/Cluster evidence.<br>
> **Update rule:** Update this file whenever a binding Location Safety ownership, lifecycle, public-interface, security, retention, or provider-boundary decision changes. Build progress must not silently redefine this architecture.

## Source Basis and Evidence Reconciliation

This Module architecture is grounded in the current Workin Ants evidence set:

- the standardized Location Safety Module Architecture Extract already produced in this thread;
- Deep Module Registry / refreshed module JSON;
- Cluster Registry `v2.3-customer-subscription`;
- current `schema.prisma`;
- Ubiquitous Language / Compliance Inventory;
- Canonical Shared Operations Architecture;
- CL-08 Privacy & Location Safety `architecture.md`;
- CL-08 Privacy & Location Safety `build-plan.md`;
- root Workin Ants project overview;
- dependency ownership evidence present in those sources.

Material reconciliation carried forward from CL-08:

1. Location Safety owns exact-location reveal policy and `LocationReveal` truth. Booking's fuzzy/exact-location compliance participation is valid supporting Booking/gate proof, not a competing ownership assignment. Preserve that supporting mapping; Booking must not independently implement reveal policy.
2. `Booking.locationPrecision`, `Booking.locationRevealStatus`, `Booking.fuzzyLat`, and `Booking.fuzzyLng` physically duplicate Location Safety-owned concepts. Their final semantic status is unresolved. CL-08 Proposed Ruling PR-08-02 treats them as non-authoritative compatibility/snapshot fields pending explicit approval; this Module must not silently promote them to truth.
3. `Booking.exactAddressEncrypted` is physically stored on a Booking-owned record, while the historical Location Safety registry claim includes "Exact/private location storage rules." The binding interpretation is **policy ownership, not automatic record ownership**: source Modules own source location facts; Location Safety owns precision, safe-public transformation, and exact-reveal policy. Canonical exact-location ownership outside Booking remains unresolved.
4. The Canonical Shared Operations Registry confirms `SH-027 resolveLocationReveal` and `SH-028 applyFuzzyPublicLocation` as Location Safety public interfaces. Shared auth, authorization, audit, idempotency, concurrency, crypto, jobs, search projection, and observability mechanisms remain outside this Module.
5. Production fuzzy radius/stability/expiry rules, reveal predicate/directionality/revocation, reveal uniqueness/context constraints, retention, geocoder choice, and crypto implementation remain explicit decision gates. Coding agents must not invent them.

**Shared Operation status:** References use permanent IDs and canonical names from `context/shared/shared-operations.md`; that registry controls owner, classification, status, and reusable boundary. SH-003 queryOwnerFacts remains **Proposed ruling** and is not an unconditional prerequisite or an approved universal DTO/API. Adoption requires separate Shared Operations approval before API/schema commitment. Existing source-owner-specific public queries may be consumed within their approved contracts; direct cross-domain Prisma/repository reads remain prohibited. SH-069 geocodeAddress remains **Proposed ruling** wherever referenced; this pass does not approve it.

### Current context paths and missing artifact roles

Read `context/context-map.md` first for authority by concern, then the existing artifacts relevant to the feature:

- Overview: `context/project-overview-v3.md`.
- Shared Operations: `context/shared/shared-operations.md`.
- Cluster architecture: `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`.
- Cluster build plan: `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`.
- Module architecture: `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md`.
- Module implementation plan: `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-implementation-plan.md`.

Root/repository-root and context-root `architecture.md`, `build-plan.md`, `code-standards.md`, and dedicated `progress-tracker.md` are currently **missing**. References to those global artifacts below describe future roles, not loadable files or current authority. Do not create local substitutes or infer global approval. Apply existing concern owners through the context map; stop work that needs a missing global decision. Until a dedicated tracker is available, report progress/blockers in the task completion report; progress does not approve architecture.

---

## 1. Module Header

| Field | Value |
|---|---|
| Module ID | `location_safety` |
| Module name | Location Safety Module |
| Module type | `compliance` |
| Build status | `mvp_active` |
| Primary Cluster | CL-08 Privacy & Location Safety |
| Compliance responsibility | Fuzzy geolocation / exact location reveal |
| Primary proof schemas | `FuzzyLocationCache`, `LocationReveal`, `LocationPrecision`, `LocationRevealStatus` |
| Document status | Implementation-grade with explicit unresolved decision gates |
| Root relationship | Inherits platform-wide architecture and code standards |
| Cluster relationship | Implements the Location Safety half of CL-08; Cluster coordinates but owns no truth |
| Update rule | Architecture changes first; implementation/progress may not silently redefine ownership or policy |

---

## 2. Purpose, Goal, and Transformation

### Purpose

Location Safety prevents exact or sensitive location information from becoming a public-discovery artifact while still allowing Workin Ants to support location-aware discovery and controlled exact-location disclosure.

It owns two related but separate transformations:

```text
private source location
→ Location Safety precision/fuzzing policy
→ safe public fuzzy projection
```

and:

```text
viewer + Booking/Order/source context
→ fresh authority and owner-fact gates
→ Location Safety reveal policy
→ deny
or
→ viewer/context LocationReveal proof + protected exact-value return
```

### Goal

The Module must make these questions answerable without consumer-side reconstruction:

1. What location precision may this target expose publicly?
2. What fuzzy location payload is safe for Search or map/public presentation?
3. May this specific viewer receive the exact private location in this specific business context now?
4. Has that reveal been eligible, revealed, or revoked?
5. What Location Safety records must be refreshed, invalidated, retained, anonymized, or erased after source/privacy changes?

### What enters

Depending on the operation:

- a supported target type and target ID;
- source-owner supplied protected location facts or a protected location reference;
- source version or equivalent freshness evidence when available;
- an authenticated viewer/actor for protected operations;
- Booking facts supplied by Booking & Calendar;
- Order facts supplied by Transaction / Order;
- authority decisions supplied by Role / Authority;
- active ComplianceHold facts only when an approved reveal policy says they apply;
- a privacy instruction supplied through Privacy / Data Erasure;
- policy configuration approved for the target type;
- a geocoder result through a provider-neutral adapter if coordinates must be derived;
- request/correlation context and idempotency identity.

### What leaves

- a public-safe fuzzy location projection;
- `FuzzyLocationCache` source-backed projection state;
- an allow/deny reveal decision with safe reason/context;
- `LocationReveal` viewer/context proof;
- exact location only on the protected allow path;
- reveal revocation state;
- a request to Search to refresh or remove its projection;
- sensitive-access and generic audit requests to Audit / Event Ledger;
- operational failure signals to Observability / Ops;
- typed privacy executor results to Privacy / Data Erasure;
- optional domain events only after root event-contract approval.

### Capability transformation

Location Safety converts **location risk and contextual business facts** into **safe precision, safe public projection, and controlled disclosure state**. It does not own the business object whose location is being protected.

### Why this deserves its own Module boundary

Location precision and exact disclosure are cross-domain safety rules used by marketplace supply, Gigs, Booking, Orders, Hiring, Search, and other surfaces. If those consumers independently implemented coordinate fuzzing or reveal predicates, Workin Ants would have inconsistent public-location leakage risk and multiple competing reveal truths. Centralizing the domain policy in this Module preserves one safety owner without taking over source record lifecycles.

---

## 3. Owned Truth

### Owned models and enums

| Record / enum | Meaning | Ownership |
|---|---|---|
| `FuzzyLocationCache` | The current Location Safety-owned safe fuzzy projection for one `targetType + targetId`. It is derived public-location truth, not exact-location truth. | Confirmed |
| `LocationReveal` | Viewer/context-specific Location Safety proof that exact-location access is hidden, eligible, revealed, or revoked. | Confirmed |
| `LocationPrecision` | Controlled location-exposure vocabulary: `public_fuzzy`, `approximate`, `exact_after_booking`, `exact_private`. | Confirmed |
| `LocationRevealStatus` | Controlled reveal-state vocabulary: `hidden`, `eligible`, `revealed`, `revoked`. | Confirmed |

### Lifecycles owned

Location Safety owns:

- fuzzy projection creation/replacement/invalidation behavior;
- fuzzy projection freshness/expiry behavior once policy is approved;
- exact-location reveal state;
- exact-location revocation state;
- the Location Safety response to relevant source/gate changes.

### Source-of-truth records

**`FuzzyLocationCache`** is authoritative for the Location Safety-approved fuzzy projection. Search/provider documents are downstream rebuildable projections.

**`LocationReveal`** is authoritative for Location Safety reveal state. It is not replaced by Booking fields, an `AccessAuditLog`, an `AuditEvent`, frontend state, or a provider object.

### Domain events / ledgers owned

No dedicated Location Safety lifecycle-event ledger model is currently present in Prisma.

Potential domain events are proposed by CL-08 but are not yet binding root event contracts:

- `location.public_projection.updated`
- `location.public_projection.invalidated`
- `location.reveal.eligible`
- `location.revealed`
- `location.reveal.revoked`

Until registered in the root event contract, code must not assume these event names are authoritative.

### Projections owned

Location Safety owns `FuzzyLocationCache` as its own derived source projection.

It does **not** own:

- Typesense/search documents;
- map-provider state;
- Booking's duplicated location fields;
- a generic "public location" table outside `FuzzyLocationCache`.

### Snapshots and proof owned

`LocationReveal` is domain-specific reveal proof. It stores current/historical reveal metadata including viewer, context identifiers, status, timestamps, reason, IP hash, and user agent.

The Module currently owns no separate reveal-history ledger beyond `LocationReveal` rows.

### Policies and invariants owned

Location Safety owns:

- public versus protected location precision interpretation;
- coordinate-fuzzing policy;
- target support for fuzzy projection;
- exact-location reveal composition policy;
- reveal state-transition policy;
- revocation policy;
- which Location Safety records are sensitive;
- which safe metadata is passed to Search/Audit/Ops;
- how Location Safety executes a Privacy instruction against its own records, subject to Privacy-owned orchestration and approved retention rules.

---

## 4. Explicit Non-Ownership

Location Safety must not absorb adjacent truth merely because that truth affects location.

| Adjacent owner | Remains owned there | Location Safety may consume |
|---|---|---|
| Identity & Access | User identity, authentication, session/security assurance, step-up lifecycle | authenticated actor and step-up result if later required |
| Role / Authority | platform/org/participant/ownership permission interpretation | allow/deny authority decision |
| Booking & Calendar | Booking lifecycle, location collection on Booking, scheduling state, participant/schedule facts, calendar provider state | minimal Booking gate/source-location DTO |
| Transaction / Order | Order lifecycle, paid/refund/cancel/dispute transaction truth, participant relationship | minimal transaction gate DTO |
| Customer / Buyer Profile | CustomerProfile identity | referenced participant facts through owner interfaces |
| Professional Eligibility | ProfessionalProfile lifecycle/readiness | referenced source/participant facts |
| Marketplace Supply | Offering and ServiceDetails lifecycle | source-location applicability/facts where supported |
| Gig / Demand | Gig/GigAssignment lifecycle | source-location applicability/facts where supported |
| Organization Hiring | Organization/Job lifecycle | source-location applicability/facts where supported |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense adapters, indexing/de-indexing, search query surface, reconciliation | Location Safety sends safe projection refresh requests |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog`, `AccessAuditAction` vocabulary | append generic/sensitive-access proof |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and reason vocabulary | active hold decision when approved policy applies |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, retention exemption and export orchestration | privacy executor instruction |
| Media / File Access | file bytes, R2/object mechanics, validation/scanning, EXIF/GPS scrubbing, signed URLs, `MediaAccessGrant` | at most semantic location sensitivity policy |
| Notification | Notification and delivery lifecycle, channel/provider mechanics | future request only if a binding business trigger is approved |
| Observability / Ops | structured operational logs, `IntegrationFailure`, QueueJob/ops incident truth | safe operational telemetry |
| Shared security/platform | encryption, keyed hashing, rate limiting, idempotency, queueing, transaction/outbox plumbing, aggregate locking | canonical shared operations |

### Concrete "does not own" boundary

Do not implement inside Location Safety:

- general address forms or address-book/profile editing;
- routing, directions, travel distance, logistics, dispatch, service-area computation;
- Booking status transitions;
- Order status/payment/refund/dispute transitions;
- Typesense/search indexing code;
- map UI/rendering or map tile/client ownership;
- Media EXIF/GPS metadata processors;
- generic authorization middleware;
- generic audit logs;
- generic compliance-hold flags;
- a second privacy request workflow;
- generic crypto/HMAC helpers;
- a private queue framework;
- a generic temporary access-grant system replacing `LocationReveal`.

---

## 5. Module Architecture Principles

1. **Source location remains source-owned.** Location Safety consumes source facts; it does not take ownership of Offering, Gig, Job, Organization, Booking, Order, profile, or other source lifecycles.
2. **Exact and fuzzy location are different truths.** `FuzzyLocationCache` must never be treated as exact-location storage.
3. **Public consumers receive only Location Safety-approved safe payloads.** They do not receive exact data to fuzz locally.
4. **Reveal is a fresh server-side decision.** Cached UI state or prior `eligible` display state is never sufficient by itself to return exact location.
5. **General authority is an input, not reveal truth.** Role / Authority may say the actor can request an action; Location Safety still owns the contextual safety decision.
6. **Paid state is an input, not reveal truth.** Order/Booking state cannot independently authorize exact location.
7. **One reveal truth.** `LocationReveal` is authoritative; Booking's duplicate reveal field must not become a second lifecycle owner.
8. **Audit is separate proof.** `AccessAuditLog` records protected access; it does not replace `LocationReveal`.
9. **Search is downstream projection.** Location Safety owns safe source projection; Search owns index mechanics.
10. **Fail closed on uncertainty.** Missing source facts, stale gate facts, unconfigured policy, crypto failure, or unresolved target support must not produce exact/publicly unsafe location.
11. **No policy by provider.** Geocoder/map/provider output is input or rendering infrastructure, not domain truth.
12. **Reuse shared infrastructure.** Idempotency, locks, queues, hashing, encryption, audit, event transport, telemetry, and rate limiting are canonical shared operations.
13. **Privacy orchestration stays Privacy-owned.** Location Safety only enumerates and disposes its own records under the standard executor contract.
14. **Decision gates are real blockers.** Production values for radius, reveal predicate, directionality, revocation, retention, or context uniqueness cannot be guessed for implementation convenience.
15. **Exact location is payload-minimized.** It must not be included in Search, analytics, domain events, ordinary logs, notifications, or diagnostic surfaces.

---

## 6. Proposed Folder / Code Structure

Follow root `code-standards.md` if its naming convention differs, while preserving these ownership boundaries.

```text
src/modules/location-safety/
├── application/
│   ├── commands/
│   │   ├── apply-fuzzy-public-location.ts
│   │   ├── refresh-fuzzy-location-projection.ts
│   │   ├── invalidate-fuzzy-location-projection.ts
│   │   ├── resolve-location-reveal.ts
│   │   └── revoke-location-reveal.ts
│   ├── queries/
│   │   ├── get-public-location-projection.ts
│   │   ├── get-location-reveal-status.ts
│   │   └── list-location-reveal-history.ts
│   └── services/
│       ├── location-projection-service.ts
│       └── location-reveal-service.ts
├── domain/
│   ├── precision/
│   │   ├── precision-policy.ts
│   │   ├── fuzzy-location-policy.ts
│   │   └── supported-location-targets.ts
│   ├── reveal/
│   │   ├── reveal-policy.ts
│   │   ├── reveal-transitions.ts
│   │   └── reveal-reason-codes.ts
│   └── types/
│       ├── location-target.ts
│       ├── public-location-result.ts
│       └── location-reveal-result.ts
├── contracts/
│   ├── public.ts
│   ├── owner-facts.ts
│   ├── privacy-executor.ts
│   └── geocoding-port.ts
├── infrastructure/
│   ├── repositories/
│   │   ├── fuzzy-location-cache-repository.ts
│   │   └── location-reveal-repository.ts
│   └── geocoding/
│       └── adapters/                 # only after provider/ownership approval
├── events/
│   ├── handlers/                    # only approved inbound domain events
│   └── contracts/                   # only root-registered Location events
├── workers/
│   ├── fuzzy-projection-refresh-worker.ts
│   ├── fuzzy-projection-expiry-worker.ts
│   └── reveal-reconciliation-worker.ts
├── privacy/
│   └── location-privacy-executor.ts
├── admin/
│   └── diagnostics/                 # bounded safe diagnostics only if root admin patterns allow
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── concurrency/
    ├── privacy/
    └── e2e/
```

### Folder rules

- Do not create a general `components/` or customer-facing map UI directory here unless a later UI ownership decision explicitly places a Location Safety-owned surface in this Module.
- Protected Booking/Order "show exact location" UI belongs to the consuming workflow surface and must call Location Safety's public interface.
- `infrastructure/geocoding/adapters` remains empty/stubbed until geocoder adapter ownership/provider choice is approved.
- Generic shared operations must not be copied under `services/`, `utils/`, or `helpers/`.
- No `search/`, `audit/`, `auth/`, `crypto/`, `notifications/`, or generic `queue/` subsystem belongs inside the Module.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / consuming UI boundary | Safe DTOs and actions used by public/protected consumers; bounded admin diagnostics if approved | map rendering, Booking page lifecycle, Order page lifecycle, generic admin authorization |
| Application services | Command/query orchestration, owner-fact calls, local transaction boundaries, downstream shared-operation calls | source Module lifecycle mutation, provider business truth, generic workflow platform |
| Domain precision policy | target support, allowed precision, fuzzing policy, safe public payload | Search ranking, source visibility lifecycle, map UI |
| Domain reveal policy | reveal composition, local reason codes, transition/revocation rules once approved | Role permission interpretation, Order/Booking lifecycle interpretation outside owner DTOs |
| Repositories | `FuzzyLocationCache` and `LocationReveal` persistence only | direct cross-Module repositories for Booking, Order, Search, User, etc. |
| Workers | Location-owned refresh/expiry/re-evaluation work | generic queue/lease/retry system; neighboring Module workers |
| Geocoding adapter | provider-neutral address-to-coordinate call if ownership is approved | map display, source-of-truth storage, provider-wide infrastructure |
| Contracts | stable Location public APIs, owner-fact input shapes, privacy executor implementation | universal cross-domain repository or universal access engine |
| Privacy executor | enumerate/disposition Location Safety records under Privacy instruction | `PrivacyRequest`, `DataErasureJob`, retention exemption lifecycle |
| Events | root-registered Location facts and handlers | ad hoc event transport or disguised commands |

---

## 8. Data Model

### `FuzzyLocationCache`

**Purpose:** Store one Location Safety-approved fuzzy public projection for a supported source target.

**Fields with architectural meaning:**

- `id` — cache record identity.
- `targetType` — source target vocabulary. Currently an unrestricted `String`; broad production vocabulary is unresolved.
- `targetId` — source target UUID.
- `fuzzyLat` / `fuzzyLng` — safe projected coordinates.
- `radiusMeters` — safety/approximation radius used for the projection.
- `generatedAt` — generation timestamp.
- `expiresAt` — optional expiration timestamp.

**Key relationships:** No Prisma FK relation to the source target. Target validation must go through the source owner.

**Uniqueness:** `@@unique([targetType, targetId])` enforces one current cache row per target pair.

**Indexes:** `@@index([expiresAt])` supports expiry/reconciliation scans.

**Concurrency-sensitive behavior:** Concurrent refreshes must not produce source-version regression or conflicting replacements. Shared aggregate lock or optimistic concurrency is required. Current schema does not contain `sourceVersion` or `policyVersion`, so version-aware production behavior remains partly decision-gated.

**Retention/privacy:** Fuzzy data remains personal/location-derived data. Expiry does not automatically equal legal erasure. Retention and erasure policy is unresolved under U-08-21.

### `LocationReveal`

**Purpose:** Record viewer/context-specific Location Safety reveal state and proof.

**Fields with architectural meaning:**

- `id` — reveal record identity.
- `bookingId` — optional Booking-shaped context reference.
- `orderId` — optional Order-shaped context reference.
- `viewerUserId` — User requesting/receiving access.
- `status` — Location Safety reveal state.
- `revealedAt` — timestamp of exact disclosure when applicable.
- `revokedAt` — timestamp of revocation when applicable.
- `reason` — safe domain reason/context; must not contain exact address or uncontrolled sensitive text.
- `ipHash` — non-plaintext request evidence when policy requires it.
- `userAgent` — request metadata; personal-data minimization/retention applies.
- `createdAt` — record creation timestamp.

**Key relationships:** The current schema exposes UUID fields but no demonstrated Prisma relations to Booking, Order, or User. Referential-integrity strategy is unresolved.

**Indexes:**

- `[bookingId, status]`
- `[orderId, status]`
- `[viewerUserId, createdAt]`

**Uniqueness:** No uniqueness constraint currently prevents multiple conflicting current rows for the same viewer/context.

**Concurrency-sensitive behavior:** Reveal, re-reveal, revoke, and source/gate changes can race. U-08-19 must settle current-row/history semantics before production exact reveal.

**Retention/privacy:** The record contains personal and safety proof. U-08-21 must settle retention, anonymization, and erasure behavior.

### External duplicate/snapshot fields on `Booking`

Current Booking schema includes:

- `locationPrecision`
- `locationRevealStatus`
- `exactAddressEncrypted`
- `fuzzyLat`
- `fuzzyLng`

These fields are **not Module-owned merely because they use Location Safety enums**.

**Proposed Ruling PR-08-02:** treat `Booking.locationPrecision`, `Booking.locationRevealStatus`, `Booking.fuzzyLat`, and `Booking.fuzzyLng` as non-authoritative compatibility/snapshot fields pending reconciliation. `Booking.exactAddressEncrypted` remains physically Booking-owned source data unless a later explicit ruling changes record ownership.

No Location Safety code may directly mutate these fields as its own truth without an approved Booking public command and architecture update.

---

## 9. Enums, Statuses, and Lifecycles

### `LocationPrecision`

Current values:

```text
public_fuzzy
approximate
exact_after_booking
exact_private
```

This enum is Location Safety-owned vocabulary describing permitted exposure semantics.

A consumer must not interpret a value as permission to bypass Location Safety. For example, `exact_after_booking` does not mean "Booking is confirmed, therefore return exact address"; exact reveal still requires `SH-027 resolveLocationReveal`.

### Fuzzy projection lifecycle

No status enum exists. The conceptual lifecycle is:

```text
unsupported/unconfigured
        │
source target + approved policy
        ▼
generated/current
        │
source change / policy change / expiry / privacy restriction
        ├──────────────► refreshed/replaced
        └──────────────► invalidated/unavailable
```

**Transition owner:** Location Safety.

**Triggers:** source-location changes, approved target/policy changes, explicit invalidation, expiry, privacy/source-visibility changes.

**Terminal state:** None inherently. A target may later become eligible again and receive a new projection.

**Concurrency:** one target pair must not have conflicting current cache rows; unique constraint plus shared DB concurrency mechanism.

**Proof/history:** Current schema preserves only the current cache row, not a full projection history ledger.

**Decision gate:** Radius, algorithm stability, source/policy versioning, expiry, and regeneration behavior are unresolved under U-08-17/U-08-18.

### `LocationRevealStatus`

Current values:

```text
hidden
eligible
revealed
revoked
```

The vocabulary strongly suggests:

```text
hidden
  ↓
eligible
  ↓
revealed
  ↓
revoked
```

However, **this is not yet a binding transition matrix**. U-08-12 through U-08-16 and U-08-19 must settle context, eligibility predicate, directionality, revocation, audit boundary, and current-row/history semantics.

### Reveal lifecycle requirements

Once approved, implementation must define:

- legal transitions;
- whether `eligible` is persisted or can be computed;
- whether repeated reveal updates one row or appends history;
- whether `revoked` may ever return to eligible/revealed or requires a new authorization cycle/new row;
- timestamp consistency (`revealed` implies `revealedAt`, `revoked` implies `revokedAt`);
- source/gate version recorded with a reveal;
- concurrency winner for reveal vs revoke;
- audit ordering/criticality.

**Prohibited shortcut:** Do not use `Booking.locationRevealStatus` or a frontend boolean as the lifecycle state machine.

---

## 10. Commands

### `SH-028 applyFuzzyPublicLocation`

**Purpose:** Produce/persist the safe public projection for a supported target.

**Actor/context:** May be invoked by a source Module/system workflow; public consumers should normally read via `getPublicLocationProjection`.

**Authoritative inputs:**

- validated target identity;
- source-owner location facts or protected reference;
- source version if available;
- configured Location Safety policy.

**Preconditions:**

- target type is explicitly supported;
- target reference is valid through owner interface;
- an approved policy exists for production use;
- exact input is available only in protected server context.

**State written:** `FuzzyLocationCache`.

**Shared operations:** `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)`, `SH-123 validateOwnedTargetReference`, `SH-044 executeIdempotentCommand`, DB concurrency primitive, optional `SH-069 geocodeAddress (Proposed ruling; adoption gated)`, `SH-091 requestSearchProjectionRefresh`, observability.

**Effects:** Search refresh request after successful Location commit; optional proposed domain event after root registration.

**Idempotency:** Semantic key should include target + source version + policy version when those concepts are available. Same semantic request replays prior result.

**Failure modes:** unsupported target, policy not configured, missing/stale source facts, geocoder failure, concurrency conflict, persistence failure, Search refresh pending.

### `refreshFuzzyLocationProjection`

**Purpose:** Recompute an existing projection after source/policy/freshness change.

**Actor/context:** system/source event/admin diagnostic action with explicit authority.

**State written:** atomically replaces current `FuzzyLocationCache`.

**Preconditions:** same safety requirements as initial application; no stale source-version regression.

**Effects:** Search refresh request; safe operational telemetry.

### `invalidateFuzzyLocationProjection`

**Purpose:** Make the Location Safety public projection unavailable after source deletion/hide/privacy restriction or unsupported state.

**Actor/context:** source owner event/system workflow/authorized administrative action.

**State written:** current cache row removed or otherwise made unavailable according to approved repository behavior.

**Effects:** Search de-index/refresh request.

**Idempotency:** repeated invalidation is a successful no-op/replay.

### `SH-027 resolveLocationReveal`

**Purpose:** Make the authoritative exact-location disclosure decision and, on the approved allow path, create/update `LocationReveal` proof and return exact location through a protected response.

**Status:** Decision-gated for production.

**Actor/context required:** authenticated viewer; contextual authority; Booking/Order/source owner facts; purpose; request context.

**Authoritative inputs:** fresh owner DTOs, source location reference/value through owner boundary, Local reveal policy, applicable hold decision if approved.

**Preconditions:** U-08-10 through U-08-16 and U-08-19/U-08-20 decisions required for production.

**State written:** `LocationReveal`.

**Shared operations:** `SH-001 resolveAuthenticatedActor`, `SH-002 authorizeResourceAction`, `SH-026 authorizeContextualResourceAccess`, `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)`, optional `SH-011 evaluateComplianceHold`, `SH-075 encryptSensitiveValue`/approved decrypt boundary, `SH-076 normalizeAndHashIdentifier`, `SH-044 executeIdempotentCommand`, aggregate lock/CAS, `SH-030 recordSensitiveAccess`, `SH-029 appendAuditEvent`, observability.

**Effects:** exact location returned only on fresh allow; audit/access proof according to approved criticality; optional proposed domain event.

**Idempotency:** duplicate request with same semantic identity must not create duplicate reveal effects.

**Failure modes:** unauthenticated, unauthorized, stale owner facts, not eligible, policy unresolved, context invalid, crypto unavailable, audit failure per policy, concurrency conflict.

### `revokeLocationReveal`

**Purpose:** Prevent subsequent exact-location retrieval for a previously eligible/revealed viewer/context.

**Status:** Decision-gated until revocation and context rules are approved.

**Actor/context:** approved system source event or explicitly authorized admin/workflow.

**State written:** `LocationReveal.status`, `revokedAt`, safe reason metadata under the approved model.

**Effects:** audit/domain event as approved.

**Idempotency:** repeated same revocation is a replay/no-op.

**Failure modes:** record/context missing, stale version, illegal transition, authority denial, concurrency conflict.

### Privacy executor mutation through `SH-095 executePrivacyInstruction`

**Purpose:** Execute an approved Privacy instruction against Location Safety-owned records.

**Actor/context:** system instruction from Privacy / Data Erasure with request/target/idempotency context.

**State written:** `FuzzyLocationCache` and/or `LocationReveal` according to approved erase/anonymize/retain behavior.

**Decision gate:** U-08-21/U-08-23.

**Must not do:** change PrivacyRequest/DataErasureTarget lifecycle directly or decide the final retention exemption record.

---

## 11. Queries / Decisions

### `getPublicLocationProjection`

**Consumers:** Search / Public Visibility; marketplace/public surfaces; map presentation.

**Input:** supported target type + target ID.

**Result:** safe fuzzy coordinates/area, radius, precision, generated/expiry metadata, source/policy version if later modeled.

**Result type:** Location Safety projection.

**Consumers must not infer:** exact coordinates, source address, reveal eligibility, source visibility beyond the safe projection contract.

### `SH-027 resolveLocationReveal`

This is both a decision and, on the approved allow path, a domain mutation.

**Consumers:** Booking, Order, protected workflow UI.

**Result:** allow/deny, permitted precision, safe reason codes, reveal ID/state, expiry/revocation context if approved, and exact value only on protected allow response.

**Consumers must not infer:** "paid" means allowed; "Booking confirmed" means allowed; `eligible` means exact value may be cached; `LocationReveal` replaces generic audit.

### `getLocationRevealStatus`

**Consumers:** Booking/Order UI; authorized support/compliance.

**Input:** viewer + approved context key.

**Result:** Location Safety truth without the exact location.

**Consumers must not infer:** current exact source value, ability to bypass fresh disclosure check, generic audit history.

### `listLocationRevealHistory`

**Consumers:** explicitly authorized support/compliance.

**Input:** safe filters plus actor context.

**Result:** reveal metadata only; exact address/coordinates excluded.

**Result type:** Location Safety domain proof/history view, not `AccessAuditLog`.

### `classifyLocationPrecision` (internal decision)

**Input:** supported target/business context and approved policy.

**Result:** `LocationPrecision` plus safe reason/policy evidence.

**Consumers must not infer:** source lifecycle or Search visibility.

### Decision result shape

Until root error/result conventions provide a stricter shape, Location Safety responses should support stable categories such as:

```text
allow | deny | unavailable | conflict | retryable_failure
```

with:

- safe reason code;
- evaluated timestamp;
- policy/source version when available;
- evidence references without raw sensitive payloads;
- optional next action/remediation.

Do not expose provider error strings or exact location in denial/error metadata.

---

## 12. Public Module Interface

### Public commands

```text
applyFuzzyPublicLocation # SH-028 applyFuzzyPublicLocation
refreshFuzzyLocationProjection
invalidateFuzzyLocationProjection
resolveLocationReveal            # production decision-gated # SH-027 resolveLocationReveal
revokeLocationReveal             # production decision-gated
```

### Public queries

```text
getPublicLocationProjection
getLocationRevealStatus
listLocationRevealHistory
```

### Privacy executor

Location Safety implements the Privacy-owned executor protocol:

```text
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
```

It does not own the protocol lifecycle or `PrivacyRequest`.

### Emitted domain events

No Location event is binding until registered in the root event contract.

Proposed CL-08 family:

```text
location.public_projection.updated
location.public_projection.invalidated
location.reveal.eligible
location.revealed
location.reveal.revoked
```

### Provider-facing interface

If geocoder adapter ownership is approved:

```text
GeocodingPort.geocodeAddress(...) # SH-069 geocodeAddress (Proposed ruling; adoption gated)
```

The port returns normalized coordinates/confidence/error categories. It does not expose provider objects as Workin Ants truth.

### Preferred integration boundary

Other Modules must consume these interfaces instead of directly reading/writing `FuzzyLocationCache` or `LocationReveal` where doing so would require Location Safety policy interpretation.

---

## 13. Inbound Dependencies

Booking, Order, and other source owners supply facts through approved public interfaces; Location Safety owns the reveal decision. The protected source-location DTO, freshness/version requirements, failure semantics, and event coverage remain unresolved. Neither SH-025 authorizeOrderEntitlement nor Proposed SH-003 queryOwnerFacts supplies an approved complete reveal-input contract.

| Owning Module/capability | Interface consumed | Why required | Minimum facts | May block action? | Must not be copied locally |
|---|---|---|---|---|---|
| Identity & Access | `SH-001 resolveAuthenticatedActor` | trusted viewer/system actor | actor ID, security context | Yes for protected operations | current-user/session helpers |
| Role / Authority | `SH-002 authorizeResourceAction` | permission interpretation | action + resource relationship context | Yes | location-specific generic permission engine |
| Booking & Calendar | owner-specific `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` / Booking location-gate DTO | Booking participant, state, in-person mode, source location reference/version, time/reschedule/cancel facts | only facts required by reveal policy | Yes for Booking-based reveal | direct Booking Prisma reads or Booking lifecycle logic |
| Transaction / Order | owner-specific `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)`, `SH-025 authorizeOrderEntitlement` only for its approved Order entitlement purpose; it is not exact-location-reveal authorization | participant/transaction/refund/cancel/dispute facts | minimal Order gate DTO | Yes | payment/refund/order policy |
| Source Modules | `SH-123 validateOwnedTargetReference` + source-location facts | fuzzy target validation and protected source input | target, source version, protected location reference/value | Yes | source lifecycle or a universal location table |
| Admin Review / Compliance Hold | `SH-011 evaluateComplianceHold` only if approved reveal policy uses it | reusable stop signs | hold ID/scope/status/reason | Potentially | local `revealBlocked` flags |
| Search / Public Visibility | `SH-091 requestSearchProjectionRefresh` | update/remove downstream Search projection | target, safe projection/version, reason | No to Location truth; may leave downstream pending | direct SearchUpsertEvent writes, Typesense |
| Audit / Event Ledger | `SH-030 recordSensitiveAccess`, `SH-029 appendAuditEvent` | generic proof | actor, action, target, decision, safe metadata | Exact reveal criticality unresolved | local audit tables |
| Privacy / Data Erasure | executor instruction contract | legal/request orchestration | subject/target/action/request/idempotency | Yes to privacy action | PrivacyRequest/job lifecycle |
| Shared crypto | `SH-075 encryptSensitiveValue`, approved decrypt operation, `SH-076 normalizeAndHashIdentifier` | reversible sensitive storage/access and non-plaintext evidence | value/context or identifier | Yes; failure must fail closed | AES/HMAC helpers |
| Shared jobs/events | `SH-047 enqueueReliableJob`, `SH-046 publishDomainEvent`, `SH-045 deduplicateDomainEvent`, `SH-055 runDeadlineExpiration` | durable async/replay-safe work | typed payload/idempotency/correlation | No direct domain permission | local queue/event framework |
| Shared persistence | `SH-044 executeIdempotentCommand`, `SH-051 acquireAggregateLock` / `SH-052 withOptimisticConcurrency` | retry/concurrency correctness | semantic key/resource version | Yes on conflicts | in-memory locks/local idempotency store |
| Observability / Ops | request context/log/failure operations | safe operational evidence | correlation + safe dimensions | No to domain eligibility | business truth in logs |
| Geocoder | provider-neutral port if approved | address→coordinate input when source lacks coordinates | minimized address/location input | Yes for that projection attempt | provider client in Search/Booking |

---

## 14. Outbound Consumers and Effects

### Search / Public Visibility

Consumes:

- `getPublicLocationProjection`;
- or a safe projection payload resulting from `SH-028 applyFuzzyPublicLocation`.

Reacts to:

- refresh/invalidation requests;
- proposed projection events if approved.

Location Safety must not write Search tables/indexes directly.

### Booking & Calendar

Consumes:

- `SH-027 resolveLocationReveal`;
- `getLocationRevealStatus`;
- `revokeLocationReveal` through approved workflows.

Booking may sequence a reveal check but may not implement Location Safety's reveal predicate.

### Transaction / Order

May consume reveal status/decision where its protected workflow requires exact-location access. It remains transaction truth and may not mutate `LocationReveal`.

### Marketplace Supply / Gig Demand / Organization Hiring

May consume Location Safety public projection/precision for supported source targets. They remain owners of the source object and must not calculate their own fuzzy coordinates.

### Audit / Event Ledger

Receives sanitized generic audit/sensitive-access requests. It owns append-only audit truth.

### Privacy / Data Erasure

Receives Location Safety executor enumeration/retention/disposition results. It owns request/job/target/exemption aggregation.

### Observability / Ops

Receives safe structured failures/metrics/correlation. Operational evidence does not alter Location Safety status.

### Notification

No binding Location Safety notification trigger is currently established. If future product policy requires a reveal/revocation notification, Location Safety owns the business cause and sends a safe `SH-041 requestNotification`; Notification owns delivery. Exact location must never be included in notification payloads.

---

## 15. Canonical Shared Operations Used

The canonical registry supplies permanent SH IDs. Only operations consumed here are listed; Proposed references remain adoption-gated.

| Canonical operation | Owner / classification | Why used | Invocation point | Location policy that remains local | Expected result | Prohibited local duplicate |
|---|---|---|---|---|---|---|
| `SH-001 resolveAuthenticatedActor` | Identity & Access; Platform capability | establish trusted viewer/system actor | every protected command/query | requested Location action | typed actor context | `locationCurrentUser`, `geoAuth` |
| `SH-002 authorizeResourceAction` | Role / Authority; Cross-cutting capability | permission interpretation | before protected reveal/history/admin action | reveal safety predicate | allow/deny authority result | `locationPermissionService` |
| `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` | Each source Module; Shared contract; separate implementations | get minimal Booking/Order/source facts | before projection/reveal | which facts Location needs | owner DTO + version/evidence | cross-domain Prisma repository |
| `SH-123 validateOwnedTargetReference` | Target owner; Shared contract; separate implementations | ensure target exists and is valid | before cache/privacy/reveal target use | supported target policy | validated target ref | direct cross-module existence checks |
| `SH-026 authorizeContextualResourceAccess` | Relevant context owner; Shared contract; separate implementations | normalize contextual access decision input | exact-reveal composition | Location's final reveal rule | typed contextual decision | universal entitlement engine |
| `SH-011 evaluateComplianceHold` | Admin Review / Compliance Hold; Cross-cutting capability | consume reusable stop signs when approved | reveal/reconciliation if policy applies | whether/how hold affects reveal | applicable holds | `revealBlocked` boolean |
| `SH-044 executeIdempotentCommand` | Platform application infrastructure; Platform primitive | prevent duplicate projection/reveal/revoke effects | every retryable mutation | semantic idempotency key | replay/original result or conflict | `location-idempotency.ts` |
| `SH-051 acquireAggregateLock` / `SH-052 withOptimisticConcurrency` | Shared persistence infrastructure; Platform primitive | serialize conflicting current-state writes | cache replace; reveal/revoke | aggregate key/conflict policy | lock/version result | in-memory mutex |
| `SH-053 transitionLifecycleState` | Shared mechanism; lifecycle owner supplies policy; Shared mechanism; separate truth | state-machine plumbing | reveal transition | legal Location transitions | validated transition | generic global policy table |
| `SH-046 publishDomainEvent` | Platform event/outbox infrastructure; Platform primitive | reliable post-commit fact publication | after approved Location commit | event name/payload | outbox acknowledgement | direct fire-and-forget emitter |
| `SH-045 deduplicateDomainEvent` | Platform event infrastructure; consumer owns inbox; Platform primitive | prevent duplicate event side effects | source/gate handlers | handler outcome | inbox/dedupe result | per-worker dedupe store |
| `SH-047 enqueueReliableJob` | Shared queue infrastructure; Platform primitive | durable refresh/reconciliation/privacy work | async operations | business payload/terminal meaning | queued job ref | `locationQueue` |
| `SH-055 runDeadlineExpiration` | Shared scheduler/queue infrastructure; Cross-cutting capability | process `expiresAt`/scheduled reevaluation | fuzzy expiry | expiry semantics | cursor/job execution | custom cron framework |
| `SH-075 encryptSensitiveValue` | Shared security/cryptography capability; Platform primitive | exact sensitive value storage/decryption boundary | source storage/read where applicable | when decrypt is permitted | encrypted/decrypted value or safe failure | `addressCrypto`, local AES |
| `SH-076 normalizeAndHashIdentifier` | Shared security/cryptography capability; Platform primitive | non-plaintext IP/request evidence | reveal proof | necessity/retention | keyed normalized hash | `location-ip-hash.ts` |
| `SH-029 appendAuditEvent` | Audit / Event Ledger; Platform audit capability | important action proof | reveal/revoke/admin action | safe metadata meaning | audit acknowledgement | `LocationAuditEvent` table |
| `SH-030 recordSensitiveAccess` | Audit / Event Ledger; Cross-cutting capability | protected access proof | exact reveal, sensitive history access if policy requires | sensitivity/decision context | AccessAuditLog acknowledgement | `LocationAccessLog` |
| `SH-091 requestSearchProjectionRefresh` | Search / Public Visibility; Module public interface | update/remove Search projection | after cache commit/invalidation | safe fuzzy payload/reason | Search command acknowledgement | direct Typesense/SearchUpsertEvent |
| `SH-069 geocodeAddress (Proposed ruling; adoption gated)` | Location Safety adapter ownership proposed; Provider-adapter capability | obtain coordinates when source lacks them | before fuzzy policy | privacy minimization/fuzzing | normalized provider result | map SDK calls in business Modules |
| `SH-096 enumerateSubjectData` | Each data-owning Module through Privacy-defined interface; Cross-cutting protocol | expose Location records to Privacy | privacy inventory | Location subject mapping | stable target descriptors | separate privacy crawler |
| `SH-097 evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption; Cross-cutting protocol | provide Location retention facts | before privacy disposition | Location safety/security retention input | typed retention facts | Location-owned exemption table |
| `SH-095 executePrivacyInstruction` | Privacy orchestrates; each data owner executes; Cross-cutting protocol | mutate own records under Privacy instruction | privacy execution | Location erase/anonymize/retain behavior | typed disposition | local PrivacyRequest workflow |
| `SH-032 createRequestContext` / `SH-033 writeStructuredLog` / `SH-034 sanitizeTelemetryMetadata` / `SH-037 recordIntegrationFailure` | Per-operation owner in the canonical registry; Per-operation classification in the canonical registry | correlate and observe safely | all paths | what Location metadata is safe | request ID/log/failure reference | ad hoc sensitive logging |

### Canonical operations owned by this Module

`SH-027 resolveLocationReveal` and `SH-028 applyFuzzyPublicLocation` are confirmed canonical **Location Safety public interfaces**. They are reusable by other Modules but remain Location Safety policy/truth, not neutral platform helpers.

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Truth affected | Why local |
|---|---|---|---|---|---|
| `classifyLocationPrecision` | apply Location precision policy | target/business context + approved policy | `LocationPrecision` + reason | none | domain meaning belongs only to Location Safety |
| `fuzzCoordinates` | transform protected coordinate into approved fuzzy projection | exact coordinate + policy | fuzzy coordinate/radius | feeds `FuzzyLocationCache` | consumer-side reuse would duplicate safety policy |
| `buildPublicLocationPayload` | ensure projection DTO cannot leak exact fields | cache + precision | safe public DTO | none | safety-specific serialization boundary |
| `validateFuzzyProjectionFreshness` | determine if cache may be reused | cache + source/policy version when available | current/stale/unavailable | none | Location cache semantics |
| `upsertFuzzyLocationProjection` | atomically create/replace current cache | projection + target | cache row | `FuzzyLocationCache` | owner-local persistence |
| `validateRevealTransition` | enforce approved Location reveal transition graph | current/requsted state + context | transition decision | `LocationReveal` when applied | domain lifecycle policy |
| `composeLocationRevealDecision` | compose authority/owner facts/holds with local policy | viewer + gate facts + policy | allow/deny + safe reasons | none until applied | only Location owns final reveal decision |
| `buildLocationRevealProof` | create minimized reveal metadata | allow path + request context | persistence input | `LocationReveal` | domain proof schema |
| `evaluateRevealRevocation` | decide whether source/gate change invalidates a reveal | current reveal + fresh owner facts | revoke/keep decision | none until command applies | Location owns revocation policy |
| `redactLocationTelemetry` | identify fields prohibited from operational metadata | operation metadata | safe metadata | none | Module-specific sensitive-field knowledge; uses canonical sanitizer mechanism |

---

## 17. Shared Mechanism / Separate Truth Rules

Common temporary reveal mechanics consume `SH-088 manageTemporaryAccessGrant`; revocation mechanics consume `SH-089 revokeTemporaryAccessGrant`. Location Safety supplies the approved policy and performs its own transitions/evidence. `LocationReveal` remains separate from `MediaAccessGrant` and all other grant truth; unresolved reveal/revocation policies remain gated.

### Audit ledger

Reuse `SH-029 appendAuditEvent` and `SH-030 recordSensitiveAccess`.

Separate truth:

```text
LocationReveal = Location Safety reveal lifecycle/proof
AccessAuditLog = generic sensitive-access evidence
AuditEvent = generic important-action evidence
```

None replaces another.

### Access-grant mechanism

LocationReveal may resemble MediaAccessGrant, DigitalDownloadGrant, CourseVideoPlaybackGrant, or AgreementAccessGrant.

Shared mechanism may include:

- transition helpers;
- expiry/revocation plumbing;
- decision-result shape;
- idempotency/concurrency.

Separate truth:

- `LocationReveal` remains its own model and policy.
- Do not reuse another domain's grant row as exact-location truth.

### Lifecycle state-machine plumbing

Shared transition infrastructure may be reused. The Location Safety transition graph and reason semantics remain local.

### Hashing/encryption

Shared crypto implementation is mandatory. Location decides:

- what exact data requires reversible encryption;
- when decryption is allowed;
- what request metadata is necessary.

### Projections

Shared indexing/event mechanics may be reused. Separate truth:

```text
FuzzyLocationCache = Location Safety safe projection source
Search document = Search-owned downstream projection
```

### Workflow runners/jobs

Shared queue/workflow plumbing may execute Location operations. Queue status never becomes LocationReveal or FuzzyLocationCache truth.

### Provider adapter pattern

A geocoder may follow a shared adapter contract, but provider-specific output never becomes source truth. Location Safety retains normalization/fuzzing policy.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

Protected operations require canonical `SH-001 resolveAuthenticatedActor`:

- `SH-027 resolveLocationReveal`;
- `revokeLocationReveal` when human/admin initiated;
- `getLocationRevealStatus` where not scoped to the current actor by a protected workflow;
- `listLocationRevealHistory`;
- manual projection diagnostics/mutations;
- Privacy executor administration where applicable.

Anonymous callers may consume only public-safe projection reads that cannot select exact precision.

### Role / Authority

Use `SH-002 authorizeResourceAction`.

Location Safety supplies contextual facts such as:

- viewer ID;
- approved Booking/Order/resource relationship facts;
- action vocabulary;
- reveal/history target;
- admin/support request context.

Role / Authority answers permission scope. It does not answer the final safety reveal question.

### Resource ownership / participant context

Booking and Order owners must supply participant facts through narrow public DTOs. Location Safety must not infer organization/customer/professional relationship by directly reading neighboring tables.

### Admin/support actions

Admin/support role is not blanket permission to view exact location or reveal history.

At minimum:

- history views require explicit capability;
- manual revocation requires explicit capability;
- viewing exact location as admin requires a distinct approved policy path;
- diagnostics should show safe identifiers/metadata only.

### Step-up

`SH-014 requireStepUpForSensitiveAction` exists canonically, but current evidence does not establish that every exact-location reveal requires step-up. Do not require or omit step-up based on guesswork. If root security policy later requires it, consume Identity's shared capability.

---

## 19. Compliance / Readiness / Entitlement Gates

### Gate: public fuzzy projection

**Underlying truth owners:** source target owner; Location Safety policy.

**Consumed facts:** valid target, protected source location/reference, source version, approved target/policy configuration.

**Module action gated:** creation/return of fuzzy public projection.

**Local composition:** Location Safety determines safe precision/fuzzy output. Source visibility/readiness remains source/Search composition, not Location Safety lifecycle.

**Decision:** projection available / unavailable / unsupported / policy not configured.

### Gate: exact location reveal

**Underlying truth owners:**

- Identity & Access — authenticated actor;
- Role / Authority — general permission;
- Booking & Calendar — Booking facts;
- Transaction / Order — Order facts;
- Admin Review / Compliance Hold — hold truth if approved;
- source Module — exact-location fact/reference;
- Location Safety — final reveal policy.

**Module action gated:** exact-location disclosure.

**Local composition:** only Location Safety decides whether all relevant inputs satisfy the reveal policy.

**Decision:** allow/deny plus permitted precision and reveal proof.

**Important:** Paid state, consent, Track entitlement, or Booking status alone is insufficient.

### Gate: Privacy instruction

**Underlying truth owner:** Privacy / Data Erasure owns request/job/instruction; source owner supplies retention facts.

**Module action gated:** erase/anonymize/retain Location Safety records.

**Local composition:** Location Safety decides how its fields can be safely transformed while Privacy records final target/exemption result.

**Decision gate:** U-08-21/U-08-23.

### Entitlements

No current evidence establishes any Track entitlement that grants exact-location authority. Location Safety must not add premium/plan gates or bypasses.

---

## 20. Provider Integrations

### Geocoding ownership

The current Canonical Shared Operations Architecture proposes Location Safety adapter ownership for `SH-069 geocodeAddress (Proposed ruling; adoption gated)`. Provider choice is intentionally unresolved.

This is a **Proposed Ruling**, not permission to select a provider ad hoc.

### Provider-neutral port

If approved:

```text
GeocodingPort
- geocodeAddress(minimizedProtectedAddress, locale/context?) # SH-069 geocodeAddress (Proposed ruling; adoption gated)
→ success(normalized coordinates, confidence, providerReference?)
or safe normalized failure
```

The port must not return provider-specific types to domain policy.

### Adapter responsibilities

- provider request mapping;
- credential use through approved secret management;
- timeouts;
- retry classification;
- rate-limit translation;
- response normalization;
- provider error redaction;
- safe operational failure reporting.

### Domain responsibilities that remain outside adapter

- target support;
- precision classification;
- fuzzing radius/stability;
- cache lifecycle;
- reveal policy;
- exact-location storage ownership;
- privacy retention.

### Webhooks and provider-event dedupe

No current geocoder webhook lifecycle is evidenced. Do not create a provider-event dedupe table unless a selected provider actually requires callback processing and architecture is updated.

### Reconciliation

Geocoder response reconciliation is not Workin Ants source-of-truth reconciliation. Source Modules remain authoritative for source location. If a provider result is missing/ambiguous, the projection attempt fails or remains pending according to approved policy.

### Privacy deletion

Location Safety must not create provider deletion obligations unless the selected provider persists user-specific resources. If such resources exist, update architecture with explicit retention/deletion contract.

### Operational failure

Use canonical `SH-037 recordIntegrationFailure`. Provider outage must not cause exact-location leakage or unsafe fallback.

---

## 21. Events and Outbox

### Current event status

No Location Safety event model is currently present in Prisma.

The CL-08 event family is a Proposed Ruling and must be registered in root event contracts before production use.

### Proposed facts

```text
location.public_projection.updated
location.public_projection.invalidated
location.reveal.eligible
location.revealed
location.reveal.revoked
```

### Emission rules

If approved:

- emit only after the owning Location transaction commits;
- use canonical transactional outbox;
- include aggregate/target ID, event version, source/policy version where modeled, correlation/causation IDs, and safe reason codes;
- never include exact address, exact coordinates, raw IP, full user agent unless explicitly required and approved;
- consumers must deduplicate via canonical inbox/dedupe mechanism.

### Events are facts, not commands

`location.revealed` means disclosure occurred. It must not instruct Booking to transition status.

`location.public_projection.updated` means Location Safety projection changed. Search may react, but Location Safety should still use the explicit Search command/contract where the architecture requires a guaranteed projection request.

---

## 22. Background Jobs / Scheduled Work

### Fuzzy projection refresh worker

**Purpose:** process source-location/policy change work asynchronously when needed.

**Input:** target, source version, policy version if available, correlation, semantic idempotency key.

**Owner:** Location Safety.

**Idempotency key:** conceptually `targetType + targetId + sourceVersion + policyVersion`; final shape follows approved version model.

**Retryable failures:** source owner timeout, geocoder timeout, Search command transport failure after Location commit.

**Permanent failures:** unsupported target, invalid source, policy not configured.

**Truth updated:** `FuzzyLocationCache`.

**Telemetry:** safe target type, outcome, retry count, latency; no exact input.

### Fuzzy projection expiry worker

**Purpose:** process cache rows with `expiresAt`.

**Input:** cache ID/target and current time.

**Mechanism:** canonical `SH-055 runDeadlineExpiration` + reliable job.

**Decision gate:** production expiry/regeneration semantics U-08-17.

### Reveal reconciliation worker

**Purpose:** re-evaluate affected reveals after approved Booking/Order/source-location/hold/time events.

**Input:** deduplicated source event + affected context.

**Truth updated:** `LocationReveal`.

**Decision gate:** U-08-15 and event-contract approval.

**Failure handling:** transient owner-fact failures retry; permanent unsafe ambiguity must fail closed or enter manual review according to approved policy.

### Privacy executor worker

**Purpose:** execute Privacy instruction asynchronously when required.

**Input:** Privacy request/target/action/idempotency context.

**Truth updated:** only Location Safety-owned rows.

**Decision gate:** U-08-21/U-08-23.

### Dead-letter/manual review

Generic dead-letter mechanics belong to shared queue/Ops. Location Safety must expose enough safe context to diagnose a failed projection/reconciliation without storing exact location in the queue payload.

---

## 23. Concurrency and Idempotency

### Fuzzy projection races

Races:

- two source-change events refresh the same target;
- old source version arrives after new version;
- refresh races invalidation/privacy erasure;
- expiry races explicit refresh.

**Aggregate key:** `targetType + targetId`.

**Database invariant:** unique `[targetType, targetId]`.

**Strategy:** use canonical aggregate lock or optimistic concurrency. Do not use in-memory mutexes.

**Decision gap:** current schema lacks source/policy version columns. Production last-writer semantics must not be guessed.

### Reveal races

Races:

- reveal vs revoke;
- duplicate reveal;
- source location changes during reveal;
- Booking/Order state changes during reveal;
- two workers reevaluate same reveal.

**Aggregate key:** cannot be finalized until U-08-12/U-08-19 establish the context/current-row model.

**Strategy:** canonical DB lock/CAS with one transaction around reveal-state write. Exact data must not be returned if the approved state transition did not commit.

### Idempotency

Every mutation must define:

- semantic request key;
- input fingerprint;
- replay result;
- conflict behavior when the same key is reused with different inputs.

No Module-local idempotency database may be created.

---

## 24. Media / Storage

Location Safety owns no file bytes or upload pipeline.

### File location metadata

EXIF/GPS extraction/scrubbing is Media / File Access responsibility.

Location Safety may define semantic rules such as "this target's location must not be publicly exposed," but it must not:

- parse EXIF;
- run `sharp`;
- scan files;
- promote MediaAsset status;
- issue signed Media URLs.

### Exact address storage

Current schema physically stores `Booking.exactAddressEncrypted` on Booking.

Location Safety owns storage/exposure **policy**, but exact record ownership outside Booking is unresolved. Reversible encryption must use canonical shared crypto.

No plaintext exact address may be persisted in a Location Safety convenience table unless a later approved schema explicitly makes that record Location-owned.

---

## 25. Search / Projection

### Source truth

- source Module owns exact/source location facts;
- Location Safety owns `FuzzyLocationCache`;
- Search owns `SearchUpsertEvent` and provider index documents.

### Indexing triggers

At minimum, integration should support:

- fuzzy projection created/refreshed;
- fuzzy projection invalidated;
- source location changed;
- source hidden/deleted;
- privacy erasure/restriction requiring public removal;
- source visibility/readiness/moderation changes routed through source owner.

### Search contract

Location Safety sends only:

- target identity;
- safe fuzzy coordinates/area;
- radius;
- permitted precision;
- freshness/source version if approved;
- safe reason/correlation.

Search must not receive exact coordinates to perform its own fuzzing.

### Reconstruction prohibition

Search may not infer exact location from:

- historical fuzzy projections;
- Booking duplicate fields;
- map-provider data;
- direct source-table joins.

Search remains rebuildable projection.

---

## 26. Notification

No current Location Safety source establishes a mandatory notification lifecycle.

If later product policy requires a user notification for:

- reveal;
- revocation;
- safety-critical denial;
- source-location change affecting an active booking;

then:

1. Location Safety owns the business trigger and safe meaning.
2. It calls canonical `SH-041 requestNotification`.
3. Notification owns channel routing, provider integration, retry, and delivery truth.
4. Notification payload must never contain the exact address/coordinates unless a separate explicit security architecture permits that channel—which current evidence does not.

Do not create email/SMS/push provider code in this Module.

---

## 27. Audit and Sensitive Access

### Location domain proof

`LocationReveal` records Location Safety reveal state and contextual proof.

### Generic audit

Audit / Event Ledger owns:

- `AuditEvent`;
- `AccessAuditLog`;
- `AccessAuditAction.location_revealed`.

Use `SH-029 appendAuditEvent` for important actions/transitions and `SH-030 recordSensitiveAccess` for protected access/reveal evidence according to canonical audit policy.

### Separation

```text
LocationReveal.status = can/has this viewer/context reveal under Location policy?
AccessAuditLog = what sensitive access action occurred?
AuditEvent = what important actor/system action occurred?
IntegrationFailure = what operational dependency failed?
```

Do not collapse these records.

### Audit failure decision gate

U-08-16 must decide whether successful `SH-030 recordSensitiveAccess` is required before exact data may be returned. Until approved, production exact reveal remains blocked.

---

## 28. Privacy and Retention

### Subject-data inventory

Location Safety must be able to enumerate:

- `FuzzyLocationCache` rows linked to subject-owned/sensitive targets through owner mapping;
- `LocationReveal` rows where the subject is viewer and/or is linked through Booking/Order/source context according to approved inventory policy.

### Privacy executor

Implement the standard contracts:

```text
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
```

### Potential dispositions

Depending on approved retention policy:

- delete fuzzy cache;
- invalidate fuzzy cache and request Search removal;
- anonymize personal request metadata on `LocationReveal`;
- erase a reveal record;
- retain a reveal record for documented safety/security/legal reason;
- return `retained` facts to Privacy so Privacy can create `DataRetentionExemption`.

### Decision gates

- U-08-21: Location Safety retention matrix.
- U-08-23 / PR-08-05: explicit Location Safety `DataErasureTargetType` values.

Until resolved, production erasure of Location Safety records must not be guessed.

### Export contribution

Current evidence does not define a specific user-facing location export schema. If Privacy requests export contribution, Location Safety should serialize only the approved subject-visible Location Safety records through the Privacy executor/export contract; exact third-party location data must not be exposed merely because the requester appears in a reveal record.

### Provider resources

No persistent geocoder resource is currently established. If a selected provider stores persistent user-specific artifacts, architecture must be updated.

---

## 29. Observability

Use canonical:

- `SH-032 createRequestContext`;
- `SH-033 writeStructuredLog`;
- `SH-034 sanitizeTelemetryMetadata`;
- `SH-037 recordIntegrationFailure`;
- `SH-036 emitMetric` for operational counters/timings;
- `SH-038 recordQueueTelemetry` for queue/worker execution;
- root incident correlation.

### Safe dimensions

Examples:

- operation name;
- target type;
- safe/hashed target reference if root policy requires;
- reveal status/decision category;
- policy configured/unconfigured;
- source version presence;
- provider name;
- retry count;
- latency;
- correlation/request ID;
- Search refresh pending/success/failure;
- worker outcome.

### Prohibited telemetry

Never emit:

- plaintext exact address;
- exact source coordinates;
- raw geocoding request payload;
- raw IP address when hash is sufficient;
- unrestricted user-agent string if not necessary;
- exact location in analytics;
- signed URLs, credentials, API keys, session material;
- raw Booking/Order payloads.

Operational records never replace `FuzzyLocationCache` or `LocationReveal`.

---

## 30. Security Boundaries

1. Validate all public command/query payloads server-side.
2. Protected commands require canonical authenticated actor resolution.
3. Authorization occurs server-side.
4. Public consumers cannot request an arbitrary precision level.
5. Exact location is never returned through public projection endpoints.
6. Exact location must be re-gated at disclosure time.
7. Use canonical encryption/decryption for reversible sensitive data.
8. Use canonical keyed hashing for IP/request evidence.
9. Never log plaintext exact address/coordinates.
10. Never put exact location in Search, analytics, ordinary events, or notifications.
11. Use canonical idempotency and DB concurrency controls.
12. Geocoding credentials remain in approved secret management.
13. Geocoder request payload uses `SH-078 minimizeAndRedactProviderInput` with source-owner policy and only the fields required for its approved purpose.
14. No client-side reveal predicate is authoritative.
15. Admin/support access is capability-gated and not blanket permission.
16. Rate limits use the root shared mechanism; no Location-only limiter framework.
17. Source target references are validated through the owner.
18. On crypto/key/provider uncertainty, exact reveal fails closed.
19. On stale owner facts, exact reveal fails closed.
20. A public map provider receives fuzzy coordinates only for public rendering.

---

## 31. Error / Decision Result Pattern

Location Safety interfaces must return stable, provider-neutral categories consistent with root error conventions.

Recommended module categories:

```text
validation_error
unauthenticated
forbidden
not_found
unsupported_target
policy_not_configured
owner_facts_unavailable
stale_source
not_eligible
revoked
idempotency_conflict
concurrency_conflict
crypto_unavailable
provider_unavailable
projection_refresh_pending
privacy_action_unsupported
retention_required
internal_failure
```

Decision responses should carry:

- high-level category;
- safe reason code;
- `evaluatedAt`;
- retryable flag where appropriate;
- correlation/request ID;
- source/policy version when modeled;
- safe evidence references.

### Rules

- Do not leak provider error bodies.
- Do not include exact location in errors.
- Do not return a generic boolean where a denial reason/version is needed for deterministic integration.
- A Search refresh failure after Location commit should normally surface as downstream/pending, not roll back Location truth.
- Exact reveal operational failures must never fall back to plaintext or a stale cached exact value.

---

## 32. Testing Architecture

### Domain unit tests

- `LocationPrecision` classification;
- fuzzy policy behavior with explicit nonproduction fixtures;
- public payload minimization;
- unsupported/unconfigured policy behavior;
- reveal decision composition once approved;
- reveal transition matrix once approved;
- revocation policy once approved;
- cache freshness/invalidation.

### Public contract tests

- `SH-028 applyFuzzyPublicLocation`;
- `getPublicLocationProjection`;
- `SH-027 resolveLocationReveal`;
- `getLocationRevealStatus`;
- `revokeLocationReveal`;
- `listLocationRevealHistory`;
- Privacy executor contracts;
- Booking/Order/source owner fact DTOs;
- Search refresh;
- Audit operations.

### Database/integration tests

- unique fuzzy cache per target;
- concurrent refresh;
- invalidation;
- cache expiry scans;
- reveal persistence/constraints once approved;
- timestamp consistency;
- privacy disposition;
- no direct cross-Module writes.

### Authorization tests

- anonymous public safe projection only;
- cross-user reveal denial;
- participant/owner scope;
- support/admin history access;
- manual revocation authority;
- no admin blanket exact-location access.

### Compliance/privacy tests

- exact never in public Search payload;
- exact never in logs/analytics/events/notification payload;
- LocationReveal separate from AccessAuditLog;
- retention result returned to Privacy rather than local exemption creation;
- privacy erasure removes public projection when approved;
- retained proof behavior once approved.

### Idempotency/concurrency tests

- duplicate fuzzy refresh;
- refresh vs invalidation;
- stale source version;
- duplicate reveal;
- reveal vs revoke;
- duplicate source event;
- duplicate Privacy instruction.

### Provider adapter tests

If geocoder is activated:

- request minimization;
- success normalization;
- no-result/ambiguous output;
- timeout;
- rate limit;
- transient/terminal error translation;
- credential/log redaction.

### E2E participation tests

1. Supported public target appears only with fuzzy location.
2. Unsupported/unconfigured target remains unavailable.
3. Search refresh receives fuzzy payload only.
4. Authorized exact reveal succeeds only after approved gate.
5. Unauthorized/ineligible reveal returns no exact data.
6. Revocation blocks subsequent exact access.
7. Source/gate change produces approved refresh/revoke behavior.
8. Privacy instruction removes/anonymizes/retains Location records according to approved policy.

Decision-gated E2E tests remain disabled until the corresponding architecture decisions are approved.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `FuzzyLocationCache` and `LocationReveal` are Location Safety-owned truth.
2. The Cluster does not own Location Safety truth.
3. Source Modules continue to own exact/source location facts and source object lifecycles.
4. `FuzzyLocationCache` is not exact-location truth.
5. Search must never calculate its own fuzzy coordinates from exact coordinates.
6. Public Search/map payloads must never include exact private location.
7. `LocationReveal` is not `AccessAuditLog` or `AuditEvent`.
8. Booking may trigger a reveal check but does not own reveal policy.
9. Order payment/paid state alone does not authorize exact location.
10. General Role / Authority permission alone does not authorize exact location.
11. Consent alone does not authorize exact location.
12. Track entitlement alone does not authorize exact location.
13. Exact location is returned only after a fresh server-side Location Safety allow decision.
14. Cached UI eligibility never authorizes exact data.
15. Revoked or no-longer-eligible context must not continue returning exact location once the approved revocation policy applies.
16. `Booking.locationRevealStatus` must not become authoritative reveal truth.
17. `Booking.fuzzyLat/fuzzyLng` must not silently replace `FuzzyLocationCache`.
18. No direct cross-Module Prisma read may reinterpret Booking/Order/source lifecycle when an owner interface is required.
19. No Location Safety code directly writes SearchUpsertEvent or Typesense.
20. No Location Safety code creates generic AuditEvent/AccessAuditLog tables.
21. No Location Safety code creates a local ComplianceHold substitute.
22. No Location Safety code creates generic encryption/HMAC helpers.
23. No Location Safety code creates local idempotency/queue/locking infrastructure.
24. No exact address or coordinate may appear in ordinary logs, analytics, public events, notifications, or Search.
25. Geocoder/map providers are not Workin Ants source truth.
26. EXIF/GPS file scrubbing remains Media-owned.
27. Privacy / Data Erasure owns privacy request/job/exemption orchestration.
28. Location Safety privacy executor mutates only Location-owned records.
29. A retained Location record must return owner retention facts so Privacy can record the exemption; Location Safety must not create its own retention-exemption lifecycle.
30. Unresolved U-08 safety/retention/provider decisions must not be filled in by coding agents.

---

## 34. Prohibited Duplicate Implementations

Do not create inside this Module:

### Authentication / authorization duplicates

- `location-auth.ts`
- `geo-auth.service.ts`
- `location-current-user.ts`
- `location-permission.ts`
- `canRevealAddress.ts` as a replacement for canonical Role / Authority + Location reveal policy
- custom admin role guards

### Cross-domain data access duplicates

- `booking-location-repository.ts` that queries Booking tables directly
- `order-location-repository.ts`
- `global-location-target-repository.ts`
- universal target lookup/Prisma repository

### Audit duplicates

- `LocationAccessLog`
- `AddressRevealAudit`
- `GeoAccessEvent` as generic audit
- local `location-audit-log.ts` replacing canonical Audit operations

### Search/map duplicates

- Search-side `randomizeCoordinates`
- Search-side `fuzzLocation`
- `geoMask`
- direct Typesense client
- direct `SearchUpsertEvent` writes
- map provider treated as exact-location database

### Crypto/security duplicates

- `location-encryption.ts`
- `address-crypto.ts`
- local AES wrappers
- local HMAC/IP hash helpers
- Location-specific rate-limit framework

### Concurrency/jobs duplicates

- `location-idempotency.ts`
- `reveal-dedupe.service.ts`
- `location-lock.ts`
- in-memory reveal mutex
- `location-queue.ts`
- custom retry/dead-letter scheduler

### Lifecycle/truth duplicates

- second exact-location reveal table
- generic `isLocationRevealed` source boolean
- Booking-owned reveal policy service
- Order-owned reveal policy service
- generic temporary access table replacing `LocationReveal`
- Location-owned PrivacyRequest/DataErasureJob
- local `revealBlocked`/`locationBlocked` stop flags

### Media duplicates

- EXIF parser/scrubber
- file scan pipeline
- signed URL generator

---

## 35. Unresolved Decisions

The following Location Safety decisions remain unresolved and block the specified production work.

| ID | Question | Current evidence | Blocks |
|---|---|---|---|
| U-08-10 | What is the canonical exact-location owner outside Booking? | no dedicated exact-location model exists for other source types | non-Booking exact reveal |
| U-08-11 | What is the semantic status of Booking's exact/fuzzy/reveal fields? | physical schema duplicates Location concepts | production reveal migration/synchronization |
| U-08-12 | Must `LocationReveal` require Booking, Order, or exactly one? | both IDs nullable; no relations/constraint | reveal persistence |
| U-08-13 | What exact predicate permits reveal? | paid/confirmed/agreement/hold/dispute/participant/time rules unsettled | exact reveal |
| U-08-14 | Who may see whose exact location? | directionality undefined | exact reveal |
| U-08-15 | What events revoke reveal? | cancel/refund/dispute/reschedule/location/hold/time may differ | revocation automation |
| U-08-16 | Must audit proof commit before exact data returns? | fail-open/fail-closed audit boundary undecided | exact reveal transaction boundary |
| U-08-17 | What radius/stability/expiry/regeneration/algorithm rules apply by target type? | cache fields exist but policy does not | production fuzzy policy |
| U-08-18 | What controlled target vocabulary validates `targetType`? | `targetType` is unrestricted String | broad production target support |
| U-08-19 | What uniqueness/current-state/history model prevents conflicting LocationReveal rows? | no unique constraint or event model | concurrency-safe reveal |
| U-08-20 | Which geocoder and KMS/key-management implementation are selected? | provider/security implementation deferred | production provider/crypto integration |
| U-08-21 | How long are reveal metadata and fuzzy caches retained/erased? | safety proof may need retention while containing personal data | production Location privacy executor |
| U-08-23 | Should explicit Location Safety values be added to `DataErasureTargetType`? | current enum requires `other` | first-class production privacy target execution |

### Proposed Rulings not yet approved

- **PR-08-02:** Booking duplicate precision/fuzzy/reveal fields are non-authoritative snapshots/compatibility fields.
- **PR-08-03:** CL-08 domain event family including Location events.
- **PR-08-05:** explicit Location Safety Privacy target types.
- **Geocoding ownership proposal:** Location Safety owns the provider adapter for canonical `SH-069 geocodeAddress (Proposed ruling; adoption gated)`.

No implementation may treat these as approved solely because they appear in Cluster context.

---

## 36. Architecture Decision Summary

### Binding rulings

1. Location Safety owns `FuzzyLocationCache`, `LocationReveal`, `LocationPrecision`, and `LocationRevealStatus`.
2. Location Safety owns coordinate-fuzzing policy, public-location precision policy, exact-reveal policy, and reveal/revocation lifecycle.
3. Source Modules own source/exact location facts and their business lifecycles.
4. Booking and Order supply gate facts but do not own exact-reveal truth.
5. Search consumes only Location Safety-approved safe projection and owns all search/index mechanics.
6. `LocationReveal` remains separate from `AccessAuditLog` and `AuditEvent`.
7. Generic auth, authority, audit, crypto, hashing, idempotency, locking, queueing, events, and observability must use canonical shared operations.
8. Privacy / Data Erasure owns privacy orchestration; Location Safety implements only its owner-local executor.
9. Media owns file mechanics and EXIF/GPS handling.
10. Public consumers may not reconstruct exact location.
11. Provider objects/results never become Location Safety source truth.
12. Exact reveal and production fuzzy policy remain disabled wherever unresolved U-08 decisions are required.

### Decision-gated implementation posture

Agents may build:

- typed contracts;
- repository boundaries;
- safe public projection mechanics using explicitly labeled nonproduction policy fixtures;
- public payload minimization;
- supported-target fail-closed behavior;
- shared-operation integration;
- disabled provider adapters;
- safe status/history reads;
- contract tests and observability.

Agents may not invent:

- production radius/stability values;
- reveal predicate/directionality;
- revocation triggers;
- reveal context/uniqueness;
- retention periods;
- audit fail-open/fail-closed behavior;
- exact-location source ownership;
- geocoder/KMS provider choice.

---

## 37. Coding-Agent Usage

Before implementing or changing Location Safety, the coding agent must read, in order:

1. `context/project-overview-v3.md`.
2. Root architecture is currently missing; stop at any required global decision gap.
3. Root code standards are currently missing; do not invent replacement standards.
4. Canonical Shared Operations Registry.
5. CL-08 Privacy & Location Safety `architecture.md`.
6. CL-08 Privacy & Location Safety `build-plan.md`.
7. This `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md`.
8. This `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-implementation-plan.md`.
9. Relevant public-interface sections for:
   - Identity & Access;
   - Role / Authority;
   - Booking & Calendar;
   - Transaction / Order;
   - Search / Public Visibility;
   - Audit / Event Ledger;
   - Privacy / Data Erasure;
   - Admin Review / Compliance Hold where applicable;
   - source Modules whose location is being projected.
10. Dedicated progress tracker is currently missing; use the task completion report for progress/blockers.

Before exact-location implementation, the agent must additionally verify that U-08-10 through U-08-16, U-08-19, and required portions of U-08-20 are approved.

Before production fuzzy-policy activation, verify U-08-17/U-08-18 and any geocoder decision required by U-08-20.

Before production privacy disposition, verify U-08-21/U-08-23.

If a required dependency interface or architecture decision is absent, stop at that boundary and record the blocker. Do not replace missing architecture with direct Prisma access, a local boolean, a provider SDK shortcut, or guessed policy.
