# Gig Demand Architecture

> **Module ID:** `gig_demand`  
> **Module name:** Gig / Demand Module  
> **Primary Cluster:** `CL-04 — Customer Demand, Order & Resolution`  
> **Document status:** Implementation-grade Module architecture. Confirmed rulings are binding; Proposed Rulings require explicit acceptance; unresolved decisions are non-authoritative and may block affected implementation.  
> **Source basis:** Workin Ants project overview, Deep Module Registry, current Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Architecture, CL-04 architecture, CL-04 build plan, and the standardized Gig / Demand Module Architecture Extract.

**Shared Operation status (CL-04-R015/R016):** exact SH IDs/names resolve to the canonical registry. SH-046 publication/outbox is Confirmed. SH-003 `queryOwnerFacts` and SH-015 `returnDecisionResult` remain Proposed ruling: use owner-specific fact/decision DTOs, not binding APIs dependent on those proposals. SH-054, SH-073, and SH-111, wherever referenced, remain Proposed ruling and conditional on separate approval. All other referenced registered operations retain their registry status and owner.

---

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `gig_demand` |
| Module name | Gig / Demand Module |
| Module type | `domain` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-04 — Customer Demand, Order & Resolution` |
| Document status | Implementation-grade; binding only where marked Confirmed or where inherited from root/Cluster architecture |
| Intended audience | Coding agents, application/domain developers, reviewers, migration authors, test authors, maintainers |
| Relationship to root architecture | Root Workin Ants architecture governs platform-wide ownership, security, shared operations, provider boundaries, privacy orchestration, and cross-cutting primitives. This file narrows those rules to Gig / Demand. |
| Relationship to Cluster architecture | CL-04 governs integration sequencing and cross-Module boundaries. This file governs only `gig_demand` source truth, local policy, public interfaces, and internal implementation boundaries. |
| Update rule | Update only when a binding Module decision changes: ownership, lifecycle policy, schema meaning, public contract, gate, event contract, privacy behavior, or concurrency rule. Build progress alone must not redefine architecture. |

### Authority rule

Follow [context/context-map.md](<../../../context-map.md>) authority by concern: Ubiquitous Language owns terminology; approved compliance material owns obligations; Prisma/migrations own persisted structure; the owning Module architecture owns lifecycle/API/invariants; Cluster architecture owns collaboration; Shared Operations owns SH identity/owner/status/boundaries; Cluster and Module plans own their respective sequence. No document class, timestamp, or file depth supplies a global precedence ladder.

### Current decision posture

The following are **not yet binding** and must not be silently implemented:

- database enforcement of the confirmed single-award MVP invariant;
- exact `Gig`, `GigResponse`, and `GigAssignment` transition matrices;
- whether `CustomerProfile` becomes mandatory on all new Gig-domain writes and how legacy User IDs are retained;
- `invite_only` audience authority;
- destructive privacy retention duration;
- whether Gig/Response/Assignment receive a dedicated immutable domain-event ledger in addition to transactional outbox events.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own customer-created paid demand on Workin Ants: the request itself, Professional proposals to that request, and the accepted work relationship that can later become an Order.

### Goal

Produce a durable answer to:

> What did this customer ask for, which Professionals responded, which response was accepted, and what accepted work relationship may be handed to Transaction / Order?

### What enters

- authenticated User/system actor context;
- resolved `CustomerProfile` buyer context for customer-side commands;
- Gig draft content, budget, timing, location context, visibility, classification, tags, and validated media references;
- taxonomy validation and requirement triggers from Taxonomy & Classification;
- ProfessionalProfile context and action-specific readiness decisions from Professional Eligibility;
- ComplianceHold decisions;
- MediaAsset readiness facts from Media / File Access;
- public-safe location projection from Location Safety where public location is exposed;
- moderation/privacy instructions;
- response proposals and accepted commercial terms;
- downstream Order facts/events only when needed to reconcile or reflect the accepted assignment relationship.

### What leaves

- authoritative `Gig` state;
- authoritative `GigResponse` state;
- authoritative `GigAssignment` state;
- Gig-owned contextual `GigTag` and `GigMedia` relationships;
- public queries and minimized owner-fact/source DTOs;
- versioned domain events through the shared transactional outbox;
- requests to Search, Messaging, Notification, Audit, Privacy, and Transaction / Order through owner interfaces;
- a checkout-source DTO for an accepted GigAssignment without exposing Gig / Demand repositories.

### Business transformation

```text
CustomerProfile intent
→ Gig draft
→ validated/open demand
→ Professional responses
→ accepted response
→ GigAssignment accepted-work truth
→ immutable/minimized checkout source
→ Transaction / Order creates Order truth
```

### Why this is a separate Module

Gig demand is not supply, formal hiring, or transaction truth:

- `Gig` is customer demand; `Offering` is Professional supply.
- `GigResponse` is a commercial proposal; `JobApplication` is a hiring application.
- `GigAssignment` is accepted work relationship; `Order` is paid transaction truth.

Those distinctions carry separate actors, statuses, policies, consumers, retention concerns, and concurrency rules. Merging them would transfer lifecycle ownership and make provider/payment state leak into demand truth.

---

## 3. Owned Truth

### 3.1 Models and contextual records

| Record | Meaning | Ownership |
| --- | --- | --- |
| `Gig` | Customer demand request truth: what is requested, classification, commercial range, timing, location context, status, and visibility. | **Owned by Gig / Demand.** |
| `GigResponse` | One ProfessionalProfile's commercial proposal/first-contact response to one Gig. | **Owned by Gig / Demand.** |
| `GigAssignment` | Accepted work relationship between one Gig and a chosen ProfessionalProfile. It is not payment or Order truth. | **Owned by Gig / Demand.** |
| `GigMedia` | Contextual relationship saying a validated `MediaAsset` belongs to a Gig with a Gig-specific role/order. | **Gig / Demand owns contextual meaning; Media / File Access owns file truth/mechanics.** |
| `GigTag` | Contextual relationship saying an accepted taxonomy tag classifies a Gig, including source/confidence metadata. | **Gig / Demand owns attachment context; Taxonomy & Classification owns taxonomy vocabulary/normalization.** |

Historical registries have overlapping `GigMedia`/`GigTag` ownership claims. The binding interpretation follows the shared-schema rule: contextual Module owns business meaning; Media/Taxonomy owners retain underlying mechanics and controlled truth.

### 3.2 Enums and statuses

- `GigStatus`: `draft`, `open`, `paused`, `assigned`, `completed`, `cancelled`, `expired`, `archived`.
- `GigVisibility`: `public`, `private`, `invite_only`.
- `GigResponseStatus`: `submitted`, `viewed`, `shortlisted`, `accepted`, `rejected`, `withdrawn`.
- `GigAssignmentStatus`: `proposed`, `accepted`, `active`, `delivered`, `completed`, `cancelled`, `disputed`.

Gig / Demand owns how these vocabularies are applied to its records. The presence of an enum value does not authorize every transition.

### 3.3 Lifecycles owned

Gig / Demand exclusively owns:

1. Gig lifecycle.
2. Gig visibility lifecycle/policy.
3. GigResponse lifecycle.
4. GigAssignment lifecycle.
5. Gig-specific attachment/tag relationship mutation.

No other Module may directly update these statuses because it owns related truth. External Modules may return gates, submit commands, or publish facts that Gig / Demand consumes.

### 3.4 Domain events and ledgers

The Module owns the **meaning and emission conditions** of Gig/Response/Assignment domain events. The shared platform owns transactional outbox transport.

Current Prisma evidence does **not** define `GigEvent`, `GigResponseEvent`, or `GigAssignmentEvent`. Therefore:

- no dedicated Gig-domain event ledger is currently confirmed;
- generic `AuditEvent` does not become the lifecycle source of truth;
- outbox events describe committed facts and must not substitute for aggregate state;
- adding a dedicated immutable Gig lifecycle ledger requires an explicit schema ruling.

### 3.5 Projections owned

Gig / Demand may own only a **source projection builder** that produces an allowlisted, privacy-safe Gig document input for Search. It does not own `SearchUpsertEvent`, Typesense documents, Search reconciliation, or Search query execution.

### 3.6 Snapshots/proof owned

Confirmed owner-local proof is the aggregate state itself plus contextual join metadata. No separate Gig snapshot schema is confirmed.

`GigAssignment` may contain accepted commercial terms (`agreedPriceCents`, `currency`, `title`, `description`, dates). Those are accepted-work facts, not the Order's final pricing/entitlement/payment snapshot.

### 3.7 Policies and invariants owned

Gig / Demand owns:

- whether a Gig is editable, publishable, pausable, cancellable, expirable, or archivable;
- whether a Gig is accepting responses;
- whether classification/budget/timing values are valid for Gig lifecycle transitions;
- response uniqueness and response-editability policy;
- which customer controls the Gig;
- which Professional controls a response;
- which response may be accepted;
- single-award MVP assignment policy;
- accepted-work transition policy;
- which source fields are exposed in `getGigAssignmentCheckoutSource`;
- what Gig-specific facts are supplied to Role / Authority, Professional Eligibility, Search, Messaging, Privacy, and other owners.

---

## 4. Explicit Non-Ownership

Gig / Demand must not own or recreate the following:

| Adjacent owner | Truth/responsibility that remains external | Prohibited Gig-side shortcut |
| --- | --- | --- |
| Identity & Access | User authentication/session/security lifecycle | `gigAuth.ts`, local current-user/session truth |
| Role / Authority | Generic permission interpretation | local RBAC/permission engine |
| Customer / Buyer Profile | `CustomerProfile` lifecycle and buyer actor resolution | using `User` alone as buyer-domain truth for new flows without approved migration semantics |
| Professional Eligibility | `ProfessionalProfile` lifecycle and action-specific readiness composition | reading verification/KYC/healthcare/entitlement/hold tables to compute `canRespond` |
| Trust Verification / Screening | `VerificationRequirement`, `VerificationCheck`, credentials, adverse-action truth | `gigVerificationService`, `isVerified` flag |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle | `blocked`, `blockedByCompliance`, or Gig-local hold table |
| Taxonomy & Classification | Domain/Category/Tag vocabulary and normalization | copied taxonomy tables, tag cleaner, hard-coded high-risk category map |
| Media / File Access | `MediaAsset`, upload/scan/process/storage/signed URL mechanics | direct R2/S3 client, file scanner, signed URL generator |
| Location Safety | fuzzy-location generation and exact-location reveal policy | local coordinate fuzzing or public exact-location logic |
| Messaging | `Thread`, `ThreadParticipant`, `Message`, messaging access mechanics | custom chat table or direct Thread writes |
| Notification | Notification persistence, templates, provider/channel delivery, retries | direct email/SMS/push clients |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense adapter, index lifecycle, reconciliation | direct Typesense client or local search ledger |
| Transaction / Order | `Order`, `OrderEvent`, agreement/payment/refund transaction truth | creating/updating Order or payment status in Gig services |
| Payment / Payout / Tax | Stripe/payment/refund/payout/KYC/tax/financial ledger/provider-event truth | Stripe SDK/client/webhook handler inside this Module |
| Review / Dispute | `Review` and `Dispute` lifecycles | making `GigAssignment.disputed` the dispute case truth |
| Content Moderation & Legal Notice | Report/LegalNotice/ModerationCase/ModerationAction truth | local moderation case/status system |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob/Target/RetentionExemption orchestration | `gigGdprWorkflow`, local erase-request state machine |
| Audit / Event Ledger | generic `AuditEvent` and `AccessAuditLog` | custom generic audit table |
| Observability / Ops | SystemEvent/IntegrationFailure/QueueJob/OpsIncident and generic telemetry | operational records used as Gig status truth |
| Track Subscription & Entitlement | plan/subscription/grant/usage truth | `isPremiumGig`, local quotas, fee waiver, commission logic |

---

## 5. Module Architecture Principles

1. **Gig is demand truth.** Never model it as Offering or Job.
2. **GigResponse is proposal truth.** Never reuse JobApplication lifecycle or hiring semantics.
3. **GigAssignment is accepted-work truth.** Never make it the payment processor record or Order replacement.
4. **CustomerProfile is the intended buyer-domain actor.** User remains authentication/audit identity.
5. **One response per Professional per Gig is database-enforced.** Revision updates the existing response under approved transition policy.
6. **External readiness is consumed, not reconstructed.** Gig / Demand supplies action context; Professional Eligibility owns the decision.
7. **Classification is externally authoritative.** Gig owns whether classification is required for a transition, not taxonomy vocabulary.
8. **Files remain Media truth.** `GigMedia` is business attachment context only.
9. **Search remains derived.** Publication commits Gig truth before Search succeeds; projection retries independently.
10. **Notifications and threads are effects, not Gig truth.** Their failure must not rewrite a committed Gig transition.
11. **Every retryable commercial command is idempotent.** Acceptance additionally requires database concurrency control.
12. **No in-memory locking for acceptance.** Use canonical DB concurrency primitives.
13. **Outbox events describe facts.** They do not act as cross-Module database commands.
14. **Privacy orchestrates; Gig / Demand executes only its own dispositions.**
15. **Moderation owns the decision; Gig / Demand applies the authorized source-side effect.**
16. **Unresolved lifecycle questions block affected production behavior.** Enum values are not permission to invent transitions.

---

## 6. Proposed Folder / Code Structure

The repository root may differ, but the conceptual ownership should be:

```text
src/modules/gig-demand/
  application/
    commands/
      create-gig-draft.ts
      update-gig-draft.ts
      publish-gig.ts
      pause-gig.ts
      cancel-gig.ts
      archive-gig.ts
      submit-gig-response.ts
      revise-gig-response.ts
      withdraw-gig-response.ts
      mark-gig-response-viewed.ts
      shortlist-gig-response.ts
      reject-gig-response.ts
      accept-gig-response.ts
      transition-gig-assignment.ts
    queries/
      get-gig.ts
      list-customer-gigs.ts
      list-gig-responses-for-poster.ts
      get-professional-gig-response.ts
      get-gig-assignment.ts
      list-professional-gig-assignments.ts
      get-gig-assignment-checkout-source.ts
    services/
      gig-publication-service.ts
      response-acceptance-service.ts
      assignment-order-handoff-service.ts
    contracts/
      dependency-ports.ts
      command-inputs.ts
      decision-results.ts

  domain/
    policies/
      gig-publication-policy.ts
      gig-transition-policy.ts
      gig-response-transition-policy.ts
      gig-assignment-transition-policy.ts
      gig-budget-policy.ts
      gig-audience-policy.ts
    events/
      gig-domain-events.ts
    projections/
      build-gig-search-source.ts

  infrastructure/
    repositories/
      gig-repository.ts
      gig-response-repository.ts
      gig-assignment-repository.ts
    workers/
      expire-gigs-worker.ts
      reconcile-assignment-order-handoff-worker.ts

  public/
    index.ts
    contracts.ts

  privacy/
    enumerate-gig-subject-data.ts
    execute-gig-privacy-instruction.ts
    evaluate-gig-retention.ts

  ui/
    # Only customer/professional Gig surfaces actually required by CL-04 features.

  tests/
    domain/
    contracts/
    integration/
    concurrency/
    privacy/
    e2e/
```

### Folder rules

- Do not create `providers/` inside `gig-demand`; this Module owns no external provider integration.
- Do not create local `auth/`, `authorization/`, `queue/`, `outbox/`, `idempotency/`, `search/`, `media/`, `notification/`, or `messaging/` infrastructure.
- Dependency contracts may be typed in `application/contracts`, but implementations remain in the owning Modules/platform.
- UI exists only for Gig-demand behavior; generic marketplace/search/chat/admin surfaces stay with their owners.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery/UI | Gig draft/edit/view, response form/status, customer response management, assignment view | authentication, Search result engine, messaging UI infrastructure, payment checkout |
| Application services | command orchestration, dependency calls, transaction boundaries, public DTO assembly | underlying external owner policy |
| Domain policy | Gig/Response/Assignment transition rules, Gig publication requirements, local validation, single-award MVP assignment policy | verification, hold, taxonomy, entitlement, payment, location-safety policy |
| Repositories/data access | Prisma access only for Gig-owned records and owner-local joins | arbitrary repositories for CustomerProfile, ProfessionalProfile, Order, ComplianceHold, VerificationCheck, MediaAsset, SearchUpsertEvent |
| Workers | owner-local expiration and assignment→Order handoff reconciliation | generic queue runner, provider reconciliation, Search reconciliation |
| Adapters | None owned | Stripe, Typesense, R2/S3, Checkr/Certn, notification providers |
| Public contracts | Gig commands, queries, checkout-source DTO, privacy executor, source projection builder | direct repository exposure or raw Prisma models as cross-Module API |
| Events | Gig-domain event vocabulary/payload meaning | event transport/outbox implementation or consumer inbox infrastructure |

---

**Confirmed actor semantics (CL-04-R007):** CustomerProfile is required semantic buyer identity for new CL-04 buyer-domain records; User remains authenticated account/audit identity. After CustomerProfile migration, Gig/GigAssignment/Order buyer ownership must not be authorized from User ID alone. A Review author resolves to the Order's buyer CustomerProfile. Dispute opener proof must distinguish customer, professional, and privileged/admin initiation with an unambiguous typed domain actor; this representation requirement does not approve which actors may open a Dispute. Historical backfill, permanent legacy-User reference semantics, and the physical typed-opener schema remain unresolved.

## 8. Data Model

### 8.1 `Gig`

**Purpose:** authoritative customer demand request.

**Key relationships:**

- `posterUserId → User` for current legacy/auth relationship;
- optional `customerProfileId → CustomerProfile`;
- required `domainId → TaxonomyDomain`;
- optional `categoryId → TaxonomyCategory`;
- child responses, assignments, tags, media;
- optional Messaging `Thread` relation.

**Authoritative fields:** title, description, status, visibility, domain/category references, budget range, currency, location fields, `remoteOk`, `dueAt`, `closesAt`.

**Lifecycle field:** `status: GigStatus`, default `draft`.

**Uniqueness/concurrency:** no aggregate version and no single-assignment constraint are currently present. `updatedAt` may support optimistic concurrency if the platform standard explicitly permits it; acceptance should prefer canonical aggregate locking until a version strategy is approved.

**Indexes:** poster, `(status, visibility)`, domain, category, location tuple, remote flag.

**Privacy/retention:** title/description/location may contain personal information. Public output must not expose exact location by default. Draft/unconverted data may be more erasable than accepted terms later frozen into an Order.

**Confirmed CL-04-R007:** new Gig/assignment writes require CustomerProfile as semantic buyer identity. Current nullable fields remain structural evidence; historical backfill and legacy User reference semantics require separate approval before physical enforcement.

### 8.2 `GigResponse`

**Purpose:** one ProfessionalProfile proposal to one Gig.

**Key relationships:**

- `gigId → Gig`;
- `professionalProfileId → ProfessionalProfile`;
- optional `responderUserId → User` as actor/audit relation;
- optional one-to-one `GigAssignment` through `GigAssignment.gigResponseId @unique`;
- optional Messaging Thread.

**Authoritative fields:** message, proposed amount, currency, estimated days, status.

**Uniqueness:** `@@unique([gigId, professionalProfileId])` enforces one row per Professional per Gig.

**Concurrency-sensitive behavior:** simultaneous duplicate submissions must collapse to replay/existing result or deterministic conflict; response acceptance must serialize against response withdrawal/rejection and competing acceptances.

**Privacy:** proposal message may contain personal/commercial data; export/anonymization rules must be owner-defined and coordinated by Privacy.

### 8.3 `GigAssignment`

**Purpose:** accepted work relationship between Gig/customer and Professional.

**Key relationships:**

- `gigId → Gig`;
- optional unique `gigResponseId → GigResponse`;
- `professionalProfileId → ProfessionalProfile`;
- optional `customerProfileId → CustomerProfile`;
- indexed `buyerUserId` with no explicit User relation in current schema;
- optional one-to-one `Order`;
- optional Thread.

**Authoritative fields:** status, accepted-work title/description, agreed price/currency, starts/due/delivered/completed timestamps.

**Current cardinality evidence:** `Gig.assignments GigAssignment[]` plus non-unique `GigAssignment.gigId` permits multiple assignments per Gig.

**Confirmed — CL-04-R002:** MVP Gigs are single-award: many responses, at most one accepted/current winning assignment per Gig. Competing acceptance commands must serialize. Database enforcement design remains a later approved schema/migration task; losing-response treatment, complete transition graphs, completion/dispute synchronization, and invitation authority remain unresolved. `invite_only` stays disabled.

**Privacy/retention:** accepted commercial terms may be retained longer than unconverted Gig content, particularly after an Order is created. Gig / Demand does not decide legal retention exemptions by itself.

### 8.4 `GigMedia`

**Purpose:** contextual attachment linking a Gig to a ready MediaAsset, with role/order metadata.

**Constraint:** composite primary key `(gigId, mediaId)`.

**Boundary:** Gig / Demand may attach/detach/reorder context. Media / File Access owns MediaAsset readiness, scan, processing, storage, deletion mechanics, signed URL, and generic media access proof.

### 8.5 `GigTag`

**Purpose:** contextual taxonomy attachment.

**Fields:** `source`, optional confidence, `verified`, created timestamp.

**Constraint:** composite primary key `(gigId, tagId)`.

**Boundary:** Taxonomy owns the validity/normalization of `TaxonomyTag` and requirement triggers. Gig / Demand owns whether/when the relationship exists for this Gig.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Binding rule

The enum vocabularies are confirmed. The exact transition matrices are **unresolved** in governing CL-04 architecture. Until approved, implementation must not infer transitions merely because statuses exist.

### 9.2 Proposed Ruling — Gig transition matrix

The following is a proposed MVP matrix, not binding until accepted:

```text
draft
  → open
  → cancelled
  → archived

open
  → paused
  → assigned        # only after accepted assignment under approved cardinality
  → cancelled
  → expired         # closesAt reached

paused
  → open
  → cancelled
  → expired

assigned
  → completed       # only after approved assignment/Order completion signal policy
  → cancelled       # only if approved cancellation semantics allow

completed | cancelled | expired
  → archived

archived
  → terminal
```

Prohibited shortcut: Search visibility or moderation action must not directly rewrite the Gig status unless Gig / Demand's transition policy explicitly maps an authorized moderation instruction to a local status/visibility change.

### 9.3 Proposed Ruling — GigResponse transition matrix

```text
submitted
  → viewed
  → shortlisted
  → accepted
  → rejected
  → withdrawn

viewed
  → shortlisted
  → accepted
  → rejected
  → withdrawn

shortlisted
  → accepted
  → rejected
  → withdrawn

accepted | rejected | withdrawn
  → terminal
```

Revision should update the same row and should be permitted only in explicitly approved nonterminal states. Whether viewed/shortlisted responses remain editable is unresolved and must be fixed before production `reviseGigResponse` behavior.

### 9.4 Proposed Ruling — GigAssignment transition matrix

The `proposed` state lacks a confirmed product workflow. Proposed MVP behavior:

- acceptance command creates the assignment directly as `accepted`;
- `proposed` remains unsupported until a distinct pre-acceptance/counteroffer workflow is approved.

Proposed active flow:

```text
accepted
  → active
  → cancelled

active
  → delivered
  → cancelled
  → disputed         # only as relationship-impact projection of Review/Dispute truth

delivered
  → completed
  → disputed

disputed
  → active | delivered | completed | cancelled
    only from an approved Review/Dispute outcome/event

completed | cancelled
  → terminal
```

This matrix remains non-binding pending the CL-04 lifecycle ruling.

### 9.5 Transition owner and triggers

- Transition owner: Gig / Demand only.
- External Modules supply decisions/facts; they do not write statuses.
- Every concurrency-sensitive transition uses SH-053 `transitionLifecycleState` plumbing plus canonical idempotency/concurrency primitives.
- Terminal/reopen rules must be explicit; no frontend-only status changes.
- No dedicated lifecycle ledger is currently confirmed. Significant transitions emit transactional domain events and selected generic audit evidence.

---

## 10. Commands

The commands below are architectural public/application operations, not claims that code already exists.

| Command | Purpose | Actor/context | Preconditions | State written | Shared operations | Effects | Idempotency / failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `createGigDraft` | Create customer demand in draft. | authenticated User + resolved CustomerProfile | valid customer actor; validated basic input | `Gig` | SH-001 `resolveAuthenticatedActor`, SH-004 `resolveCustomerActor`, SH-002 `authorizeResourceAction`, SH-044 `executeIdempotentCommand` | `GigCreated` outbox as needed | retry returns same Gig; invalid customer/validation fails before write |
| `updateGigDraft` | Edit allowed Gig fields. | controlling customer | editable status; expected version where required | `Gig`, `GigTag`, `GigMedia` context as applicable | auth, authority, taxonomy/media interfaces, optimistic concurrency if used | update event/projection request if public state affected | stale write → conflict |
| `publishGig` | Open eligible Gig. | controlling customer | publication policy; taxonomy valid; media ready; hold allows; public-safe location | Gig status/visibility | auth, authority, taxonomy, hold, Media, Location, idempotency, transition, outbox | audit + Search refresh + optional notification | Search failure does not roll back Gig truth |
| `pauseGig` | Stop new response/public availability temporarily. | controlling customer/admin if approved | allowed transition | status | auth, authority, transition, outbox | Search refresh | stale transition conflict |
| `reopenGig` | Return paused Gig to open. | controlling customer | transition approved; deadlines/gates still valid | status | auth, authority, gates, transition | Search refresh | unavailable gate → deny |
| `cancelGig` | End active demand under approved policy. | controlling customer/admin if approved | no prohibited downstream state | status | auth, authority, transition, idempotency | audit, Search refresh, notifications | conflict if assignment/Order policy forbids |
| `archiveGig` | Remove terminal Gig from normal active views. | owner/admin | terminal state | status | auth, authority, transition | Search remove | product archive is not privacy erasure |
| `setGigTags` | Mutate contextual accepted tag relationships. | controlling customer/system-approved taxonomy flow | taxonomy validates assignments | `GigTag` | SH-023 `validateTaxonomyAssignment` | source-change event if public | no local normalization |
| `setGigMedia` | Attach/detach/reorder ready assets. | controlling customer | Media validates target/asset | `GigMedia` | SH-090 `attachValidatedMedia` and Media owner queries | source-change event if public | no file mutation |
| `submitGigResponse` | Create one Professional response. | authenticated Professional actor + ProfessionalProfile | Gig accepts responses; readiness allowed; uniqueness | `GigResponse` | auth, authority, SH-016 `evaluateProfessionalReadiness`, idempotency, outbox | customer notification | duplicate retry must not create second row |
| `reviseGigResponse` | Edit existing response under approved nonterminal policy. | response owner | editable status; readiness recheck if material | same `GigResponse` | auth, authority, concurrency | response-updated event/notification if needed | stale/terminal → conflict |
| `withdrawGigResponse` | Withdraw own response. | response owner | allowed nonterminal transition | status | auth, authority, transition | notification | accepted/terminal → conflict |
| `markGigResponseViewed` | Record customer view-state transition. | controlling customer | submitted response | status | auth, authority, transition | optional event | idempotent if already viewed or later state according to policy |
| `shortlistGigResponse` | Mark preferred response. | controlling customer | allowed state | status | auth, authority, transition | optional notification | terminal → conflict |
| `rejectGigResponse` | Reject response. | controlling customer | allowed state | status | auth, authority, transition | notification | accepted/withdrawn → conflict |
| `acceptGigResponse` | Atomically accept a response and create/replay assignment. | controlling customer | assignment cardinality ruling; Gig/response state; readiness recheck; no blocking hold | response + assignment + Gig state according to approved matrix | auth, customer actor, authority, SH-016 `evaluateProfessionalReadiness`, SH-011 `evaluateComplianceHold`, SH-044 `executeIdempotentCommand`, SH-051 `acquireAggregateLock`, SH-053 `transitionLifecycleState`, SH-046 `publishDomainEvent`, audit | assignment-ready event; thread/notification effects | retry replays same assignment; competing acceptance obeys cardinality exactly |
| `transitionGigAssignment` | Apply owner-local accepted-work transition. | authorized participant/system | approved assignment matrix + contextual external facts | assignment status/timestamps | authority, transition, concurrency, outbox | notifications; Order/Dispute consumers may react | stale transition conflict |
| `executeGigModerationDecision` | Apply an authorized moderation action to Gig-owned state. | signed internal Moderation instruction | validated case/action/target/version | only approved Gig fields/status/visibility | SH-103 `executeModerationDecision`, idempotency, outbox | Search refresh | no local ModerationCase truth |
| `executeGigPrivacyInstruction` | Apply Privacy-directed disposition to Gig-owned data. | Privacy/system actor | approved target instruction + retention result | owner-local data only | SH-095 `executePrivacyInstruction`, SH-097 `evaluateRetentionRequirement`, anonymization primitive | Search deindex/detach effects | idempotent; retained/skipped explicit |

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result type | Meaning | Consumer must not infer |
| --- | --- | --- | --- | --- | --- |
| `getGig` | UI, Messaging context, owner modules | Gig ID + viewer context | source truth/contextual view | authorized Gig facts and safe relationships | Search indexing success; Professional readiness |
| `listCustomerGigs` | customer UI/read model | CustomerProfile + filters | source-truth list | customer-owned Gigs | CustomerProfile lifecycle |
| `listGigResponsesForPoster` | customer UI | Gig + customer actor | contextual source truth | authorized responses with safe Professional summary | raw verification evidence |
| `getProfessionalGigResponse` | Professional UI | Gig + ProfessionalProfile | source truth | Professional's one response | whether response can currently be accepted without fresh readiness |
| `getGigAssignment` | participants, Messaging, Order context | assignment + viewer | source truth | accepted-work facts | Order/payment truth |
| `listProfessionalGigAssignments` | Professional UI | ProfessionalProfile + filters | source truth list | assignments for Professional | payout/payment status |
| `getGigAssignmentCheckoutSource` | Transaction / Order | assignment ID + expected version | minimized immutable/source-version DTO | buyer/customer, seller, accepted commercial terms, source status/version needed for Order creation | ability to mutate Gig; current entitlements; payment state |
| `queryGigOwnerFacts` | Role / Authority and context owners | Gig/response/assignment + actor | owner-fact DTO | controlling customer, response owner, assignment parties, status/version | generic permission result |
| `evaluateGigPublicReadiness` | Search/publication workflow | Gig source version | decision result | Gig-owned part of public readiness: status, visibility, local publication invariants | verification/hold/moderation/location truths not owned here |
| `buildGigSearchSourceProjection` | Search | Gig ID/source version | privacy-safe source projection | allowlisted public fields plus public-safe location references | exact location or private attachments |
| `enumerateGigSubjectData` | Privacy / Data Erasure | subject + cursor | privacy inventory | Gig-domain records and supported dispositions | retention exemption truth outside owner facts |
| `evaluateGigRetentionRequirement` | Privacy | target/context | retention facts | owner evidence about accepted/Order-linked state | final legal exemption record, which Privacy owns |

### Decision result pattern

Policy-facing decisions use an owner-specific decision envelope (`allowed`, `denied`, `warning`, `review_required`, `step_up_required`, `unavailable`) plus Gig-specific reason codes, source version, evaluated time, and safe evidence references.

---

## 12. Public Module Interface

### Public commands

- `createGigDraft`
- `updateGigDraft`
- `publishGig`
- `pauseGig`
- `reopenGig` — only after transition ruling
- `cancelGig`
- `archiveGig`
- `setGigTags`
- `setGigMedia`
- `submitGigResponse`
- `reviseGigResponse` — only for approved editable states
- `withdrawGigResponse`
- `markGigResponseViewed`
- `shortlistGigResponse`
- `rejectGigResponse`
- `acceptGigResponse`
- assignment transition commands once matrix is approved

### Public queries

- `getGig`
- `listCustomerGigs`
- `listGigResponsesForPoster`
- `getProfessionalGigResponse`
- `getGigAssignment`
- `listProfessionalGigAssignments`
- `getGigAssignmentCheckoutSource`
- `queryGigOwnerFacts`
- `evaluateGigPublicReadiness`
- `buildGigSearchSourceProjection`

### Emitted domain events

Event names below are proposed vocabulary; envelope schema version is separate from event name:

- `GigCreated`
- `GigPublished`
- `GigUpdated`
- `GigPaused`
- `GigReopened`
- `GigCancelled`
- `GigExpired`
- `GigArchived`
- `GigResponseSubmitted`
- `GigResponseUpdated`
- `GigResponseViewed`
- `GigResponseShortlisted`
- `GigResponseRejected`
- `GigResponseWithdrawn`
- `GigResponseAccepted`
- `GigAssignmentCreated`
- `GigAssignmentAccepted`
- `GigAssignmentActivated`
- `GigAssignmentDelivered`
- `GigAssignmentCompleted`
- `GigAssignmentCancelled`
- `GigAssignmentDisputeEffectApplied`

Events are facts. Consumers must use their own public commands to mutate their truth.

### Privacy interface

- `enumerateGigSubjectData`
- `evaluateGigRetentionRequirement`
- `executeGigPrivacyInstruction`

### Provider-facing interfaces

None. Gig / Demand owns no provider adapter or webhook endpoint.

---

## 13. Inbound Dependencies

| Owner | Public operation/interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | trusted actor | actor ID/type/security context | Yes | session/user helper |
| Role / Authority | SH-002 `authorizeResourceAction` | authorization | action, resource, owner facts | Yes | generic permission engine |
| Customer / Buyer Profile | SH-004 `resolveCustomerActor` | buyer-domain actor | active CustomerProfile ID + User link/status | Yes | CustomerProfile lifecycle |
| Taxonomy & Classification | SH-023 `validateTaxonomyAssignment`, SH-022 `resolveTaxonomyRequirements` | classification validity/triggers | canonical IDs, validity, requirement refs | Yes for publish/update as local policy requires | taxonomy rules |
| Professional Eligibility | SH-016 `evaluateProfessionalReadiness` | Professional response/acceptance gate | action `respond_to_gig`/approved acceptance action, Professional, Gig context | Yes | raw readiness composition |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | reusable stop sign | target/action + safe reasons | Yes | blocked flags |
| Media / File Access | ready-target validation, SH-090 `attachValidatedMedia`, signed access where viewer needs media | safe attachments | MediaAsset ID/status/context/allowed actions | Yes for attachment/publication | file pipeline |
| Location Safety | SH-028 `applyFuzzyPublicLocation` | public-safe location | approved fuzzy projection/version | Yes where public location is required | coordinate fuzzing |
| Messaging | SH-113 `ensureContextThread` | conversation context | ThreadContextType, context ID, participants | No for core Gig write unless explicitly made synchronous | Thread lifecycle |
| Notification | SH-041 `requestNotification` | user alerts | recipients/template key/safe variables | No for source commit | delivery providers/status |
| Search / Public Visibility | SH-091 `requestSearchProjectionRefresh` | derived discovery | entity/action/reason/source version | No for source commit | SearchUpsertEvent/Typesense |
| Content Moderation | SH-103 `executeModerationDecision` protocol | apply authoritative moderation result | case/action/target/source version | May restrict public behavior | moderation case truth |
| Privacy / Data Erasure | privacy instruction protocol | execute owner data disposition | target/disposition/idempotency/exemption ref | May restrict/delete/anonymize | PrivacyRequest workflow |
| Audit / Event Ledger | SH-029 `appendAuditEvent` | generic significant-action proof | actor/action/target/outcome/safe metadata | Usually no; required audit failure policy follows root standard | generic audit storage |
| Transaction / Order | source conversion acknowledgement/query as needed | assignment→Order handoff/reconciliation | assignment ID/source version/Order ID | No effect on accepted assignment truth if downstream unavailable | Order creation logic |
| Observability / Ops | request context/log/failure interfaces | operations | correlation IDs/safe failure categories | No | SystemEvent/IntegrationFailure logic |

Trust Verification / Screening is normally indirect through Professional Eligibility. Gig / Demand should consume it directly only for a specifically approved requirement-resolution contract not already composed by Professional Eligibility.

---

## 14. Outbound Consumers and Effects

| Consumer | What it may consume | Trigger/effect | Forbidden coupling |
| --- | --- | --- | --- |
| Transaction / Order | `getGigAssignmentCheckoutSource` / assignment-ready event | create exactly one Order under Order rules | direct Gig repository reads or Gig writing Order |
| Professional Eligibility | minimized Gig/response context as action input | evaluate response readiness | Professional Eligibility mutating Gig |
| Search / Public Visibility | source projection + refresh request | index/update/hide/remove Gig | Search reconstructing private fields or status policy |
| Messaging | Gig/Response/Assignment context IDs + participants | create context Thread | Gig creating Thread rows |
| Notification | committed Gig-domain events/recipient facts | deliver alert | Notification status becoming Gig status |
| Payment / Payout / Tax | Order-linked source context only after transaction path requires it | financial context downstream | Gig calling Stripe/payment APIs |
| Review / Dispute | assignment/Order linkage when dispute relationship needs context | may publish dispute effect fact | Dispute direct assignment status write |
| Privacy / Data Erasure | data inventory/executor | erase/anonymize/retain/export | Privacy directly rewriting Gig tables |
| Content Moderation | target summary | moderation review | Moderation direct source DB writes |
| Audit / Ops | safe action/failure metadata | evidence/diagnostics | logs/audit replacing lifecycle truth |

---

## 15. Canonical Shared Operations Used

Use the permanent IDs, canonical owners, and statuses in [Shared Operations](<../../../shared/shared-operations.md>). Confirmed references retain their registered boundaries; proposed references are conditional only.

| Canonical operation | Owner / class | Why Gig / Demand uses it | Invocation point | Local policy that remains here | Expected result | Prohibited duplicate names |
| --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access; platform capability | trusted actor | every protected command | what Gig action is attempted | typed actor context | `requireGigUser`, `gigAuth`, `currentGigUser` |
| SH-002 `authorizeResourceAction` | Role / Authority; cross-cutting capability | server-side permission | protected reads/writes | owner/response/assignment relationship facts | allow/deny decision | `gigPermissions`, `assignmentGuard`, local RBAC |
| SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) | each source Module; shared contract | expose minimal Gig ownership/context facts | Role/Media/Messaging consumers | Gig fact vocabulary | owner-fact DTO | cross-domain repository |
| SH-004 `resolveCustomerActor` | Customer / Buyer Profile; Module public interface | buyer-domain identity | customer Gig commands | Gig requires eligible customer context | CustomerProfile ID/status/source version | `buyerResolver`, User-only buyer helper |
| SH-011 `evaluateComplianceHold` | Admin Review / Compliance Hold | reusable action stop sign | publish, response acceptance, selected assignment transitions | which action/target a hold blocks | safe DecisionResult | local `blocked` flag/service |
| SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite) | shared contract; policy local | consistent decisions | all gate/query surfaces | Gig reason codes and policy | normalized decision envelope | ad hoc booleans |
| SH-016 `evaluateProfessionalReadiness` | Professional Eligibility | response/acceptance gate | submit and accept | Gig supplies action/context only | DecisionResult + safe evidence refs | `professionalCanRespond`, raw verification composer |
| SH-022 `resolveTaxonomyRequirements` | Taxonomy & Classification | requirement triggers | publish/update | whether trigger blocks Gig transition | typed requirements | hard-coded category risk map |
| SH-023 `validateTaxonomyAssignment` | Taxonomy & Classification | canonical classification validation | create/update/publish | whether category/tags are mandatory | normalized IDs/errors | `gigCategoryValidator`, local tag cleaner |
| SH-024 `evaluatePublicReadiness` | shared contract; source/compliance owners | public projection decision | publish/Search source build | Gig-local status/visibility rules | owner decision + version | Search reconstructing Gig policy |
| SH-028 `applyFuzzyPublicLocation` | Location Safety | public-safe location | public projection | what location context Gig wants displayed | fuzzy projection/version | `gigLocationMask`, coordinate randomizer |
| SH-090 `attachValidatedMedia` | contextual Module + Media truth | safe Gig attachment | media attach | role/sort/context semantics | validated join creation | `gigFileScanner`, direct Media writes |
| SH-127 `requestMediaAccess` | Media / File Access | temporary private media delivery | authorized Gig media read | contextual viewer entitlement facts | signed URL/access evidence | `gigPresignedUrl`, R2 client |
| SH-113 `ensureContextThread` | Messaging; Module public interface | idempotent business-context conversation | after approved Gig/response/assignment point | context/participants | Thread ID | `gigChatService`, direct Thread insert |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | generic significant action proof | publish/cancel/accept/admin actions | safe Gig metadata | audit acknowledgement | `gigAuditLog` generic table |
| SH-032 `createRequestContext` | platform/Observability | correlation/causation | request/job entry | safe domain IDs only | propagated context | custom correlation helper |
| SH-033 `writeStructuredLog` | Observability / Ops | operational diagnostics | commands/workers | safe dimensions | log record | direct ad hoc logger stack |
| SH-034 `sanitizeTelemetryMetadata` | Observability/Audit policy | prevent sensitive leakage | logging/audit/event metadata | Gig sensitivity classification | safe metadata | manual scattered redaction |
| SH-037 `recordIntegrationFailure` | Observability / Ops | visible degraded dependency | failed Search/Notification/Order handoff etc. | business state remains unchanged | normalized failure | custom failure table |
| SH-041 `requestNotification` | Notification | user alert | committed lifecycle events | event meaning + recipients | notification request | `gigEmailService`, `gigPush` |
| SH-044 `executeIdempotentCommand` | platform application infrastructure | safe retries | create/respond/accept/transitions | semantic identity/conflict/replay | original result replay | `gigIdempotency`, custom dedupe table |
| SH-045 `deduplicateDomainEvent` | platform event infrastructure | idempotent event consumers | inbound event handlers | handler-specific effect | inbox claim/result | ad hoc processed-event table |
| SH-046 `publishDomainEvent` | platform outbox | reliable committed fact publication | same transaction/outbox as source write | event names/payload privacy | versioned event | fire-and-forget emitter |
| SH-047 `enqueueReliableJob` | shared queue infrastructure | expiration/reconciliation | background work | job payload and business meaning | durable job ID | custom queue |
| SH-048 `executeRetryWithBackoff` | shared queue/platform | retry transient effects | worker dependency calls | retryability classification | success/dead-letter | per-worker retry loop |
| SH-051 `acquireAggregateLock` | shared persistence infrastructure | serialize response acceptance | acceptance/critical transition | lock key `gig:{gigId}` and conflicts | lock/transaction scope | in-memory mutex, bespoke lock table |
| SH-052 `withOptimisticConcurrency` | shared persistence infrastructure | stale update protection | edits/non-locking transitions where approved | retry/merge policy | update/conflict | hand-rolled timestamp compare |
| SH-053 `transitionLifecycleState` | shared mechanism/separate truth | state-machine plumbing | all lifecycle commands | exact Gig/Response/Assignment graph | validated transition | generic policy owning statuses |
| SH-055 `runDeadlineExpiration` | shared scheduler/queue | process `closesAt` | expiration worker | which statuses expire | dispatched owner transition | `gigCron`, scheduler writing status directly |
| SH-091 `requestSearchProjectionRefresh` | Search / Public Visibility | index/update/hide/remove | after committed public-source change | Gig source version/reason | accepted projection request | Typesense client, `SearchUpsertEvent` insert |
| SH-094 `buildSourceProjection` | each source Module; shared pattern | safe Search input | Search query/rebuild | allowlisted Gig fields | source projection + version | Search raw Prisma access |
| SH-095 `executePrivacyInstruction` | Privacy protocol; data owner executes | privacy disposition | Privacy target command | field-level Gig handling | normalized privacy result | `gigGdprWorkflow` |
| SH-096 `enumerateSubjectData` | each data owner | privacy inventory | Privacy discovery | Gig-owned targets | cursorable target list | global DB crawler |
| SH-097 `evaluateRetentionRequirement` | data owner facts + Privacy exemption record | retention determination input | before destructive action | Gig/Order-linked retention facts | required/reason/minimum fields | local retention-exemption table |
| SH-098 `anonymizePersonalFields` | shared primitive; owner mapping | field-level anonymization | approved Privacy instruction | exact Gig field map | anonymization proof/result | global uncontrolled anonymizer |
| SH-103 `executeModerationDecision` | Moderation decision; target owner executes | apply approved source effect | moderation event/command | allowed Gig-side effect | ack/completed/failed result | local moderation case |
| SH-123 `validateOwnedTargetReference` | target owner | safe cross-Module target validation | context joins/commands | Gig relationship eligibility | typed target result | direct cross-domain Prisma read |

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `validateGigDraft` | Validate title/description/budget/timing/basic local invariants. | draft input | normalized validation result | none | Gig-specific semantics |
| `evaluateGigPublicationPolicy` | Compose Gig-owned publication rules with external decisions. | Gig + gate results | DecisionResult | none | action owner decides whether external proofs are sufficient |
| `validateGigBudget` | Validate optional min/max/currency relationship. | budget fields | errors/normalized values | none | Gig commercial request policy |
| `validateGigResponsePolicy` | Determine whether Gig currently accepts a response. | Gig + existing response | decision | none | Gig lifecycle meaning |
| `validateGigResponseTransition` | Apply approved response graph. | current/target state | decision | none | response lifecycle owner |
| `validateGigAssignmentTransition` | Apply approved assignment graph. | current/target + external facts | decision | none | assignment lifecycle owner |
| `buildAcceptedAssignment` | Freeze accepted proposal/customer/professional terms into GigAssignment. | Gig + response + agreed terms | assignment data | `GigAssignment` | accepted-work truth is local |
| `buildGigAssignmentCheckoutSource` | Produce minimal immutable/versioned Order source DTO. | assignment | source DTO | none | Gig owns which facts are authoritative for downstream Order |
| `resolveGigNotificationIntent` | Determine recipients/template intent from a committed Gig event. | domain event | notification request DTO | none | event meaning is Gig-owned; delivery is not |
| `resolveGigThreadContext` | Determine context type and initial participants. | Gig/response/assignment event | Messaging request DTO | none | business context is Gig-owned |
| `resolveGigSearchAction` | Translate committed source change into index/update/hide/remove intent. | Gig state/event | Search request DTO | none | source meaning local, Search execution external |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Lifecycle plumbing:** SH-053 `transitionLifecycleState` may be shared; Gig/Response/Assignment graphs remain Gig truth.
2. **Idempotency:** platform stores command claim/replay; Gig defines semantic command identity and conflict meaning.
3. **Concurrency:** database lock/CAS mechanism is shared; Gig defines acceptance lock key and conflicting commands.
4. **Outbox/inbox:** transport is shared; Gig owns event vocabulary/payload/emission condition; consumers own side effects.
5. **Readiness:** DecisionResult shape is shared; Professional Eligibility owns readiness; Gig owns how the decision gates its command.
6. **Attachments:** Media safety/access is shared capability; `GigMedia` context remains Gig truth.
7. **Taxonomy:** validation/normalization is Taxonomy-owned; `GigTag` relationship remains Gig contextual truth.
8. **Search:** source-projection pattern is shared; Gig builds safe source facts; Search owns index truth and reconciliation.
9. **Privacy:** protocol and orchestration are shared/Privacy-owned; Gig owns how its fields are erased/anonymized/retained when instructed.
10. **Audit:** generic audit rail is shared; Gig statuses and outbox events remain separate business truth.
11. **Temporary access:** MediaAccessGrant remains Media truth; no Gig-specific duplicate grant unless a future Gig-domain entitlement requires a distinct record.

---

## 18. Authentication and Authorization

### Authenticated actor

Every protected command begins with SH-001 `resolveAuthenticatedActor`. Browser/client-provided User IDs are never trusted as actor proof.

### Authority

Use SH-002 `authorizeResourceAction`. Gig / Demand supplies contextual facts such as:

- controlling `customerProfileId` and associated User;
- `posterUserId` during migration/legacy handling;
- response `professionalProfileId` / `responderUserId`;
- assignment customer/professional parties;
- current lifecycle status and source version.

Role / Authority returns permission interpretation. It does not determine business readiness.

### Resource ownership

- customer commands require control of the Gig through approved CustomerProfile semantics;
- Professional response mutations require control of the ProfessionalProfile/response;
- cross-party response management requires the Gig-controlling customer;
- assignment actions require explicit participant/action policy;
- admin/support actions require named authority and must not imply blanket access to private media/message contents.

### Step-up

No Gig-specific step-up requirement is confirmed. If root security policy later marks an admin/financial Gig-adjacent action as sensitive, Gig / Demand calls Identity & Access SH-014 `requireStepUpForSensitiveAction`; it does not implement MFA locally.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying truth owner | Query | Gig action gated | Gig-local policy | Result |
| --- | --- | --- | --- | --- | --- |
| Customer actor | Customer / Buyer Profile | SH-004 `resolveCustomerActor` | create/update/publish/accept | require eligible controlling customer | allow/deny |
| Taxonomy validity | Taxonomy & Classification | SH-023 `validateTaxonomyAssignment` | create/update/publish | decide which classification fields are mandatory | valid/errors |
| Taxonomy requirements | Taxonomy & Classification | SH-022 `resolveTaxonomyRequirements` | publish/response context | include trigger facts in readiness/public policy | requirement refs |
| Professional response readiness | Professional Eligibility | SH-016 `evaluateProfessionalReadiness` | submit response | `respond_to_gig` action | DecisionResult |
| Acceptance readiness recheck | Professional Eligibility | same interface with approved action/context | accept response | fresh evaluation required at acceptance | DecisionResult |
| Compliance hold | Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | publish/accept/selected transitions | map applicable holds to denial | DecisionResult |
| Location safety | Location Safety | SH-028 `applyFuzzyPublicLocation` | public projection | do not expose exact location | safe projection |
| Media readiness | Media / File Access | owner validation/attach interface | attach/publish | required assets must be ready | allow/deny |
| Moderation | Content Moderation | approved action protocol | public/source restriction | apply only authorized effect | action acknowledgement |
| Entitlement | Track Subscription & Entitlement | none confirmed for a Gig-specific MVP feature | none by default | do not invent premium/posting quota policy | N/A until product ruling |

Verified-only/high-risk work is supported through Taxonomy triggers + Professional Eligibility composition. Gig / Demand does not inspect TrustBadge as readiness truth.

---

## 20. Provider Integrations

Gig / Demand owns **no external provider integration**.

Explicitly prohibited inside this Module:

- Stripe/Stripe Connect/Stripe webhook clients;
- Typesense client/index schema/reconciliation;
- Cloudflare R2/S3 storage or signed URL code;
- Checkr/Certn/identity-verification adapters;
- email/SMS/Web Push provider clients;
- geocoding provider adapters;
- provider webhook signature verification or provider-event dedupe records.

Provider failures arrive only as normalized owner-module results/events when Gig behavior needs them. Raw provider statuses never enter Gig-domain policy.

---

## 21. Events and Outbox

### Event rule

Every cross-Module event is written to the canonical transactional outbox in the same source transaction or only after a committed source change according to platform standard. Events contain minimized facts, not private Gig descriptions/messages unless strictly required.

### Required envelope

Use the canonical event envelope: event ID/type/schema version, source Module, aggregate type/ID/version, occurredAt, correlation/causation IDs, actor/system context, privacy classification, minimized payload.

### Proposed event families

- Gig creation/publication/status change.
- GigResponse creation/management/acceptance.
- GigAssignment creation/status change.
- Assignment ready for Order.
- Gig source changed for Search/Notification/Messaging consumers.

### Payload minimization

Typical event payload should contain IDs, status, source version, actor/customer/professional IDs where required, and minimal commercial fields only for an explicitly approved consumer contract. Do not publish exact private location, full response message, private media URLs, provider data, or unrelated personal data.

### Consumer idempotency

Every consumer uses SH-045 `deduplicateDomainEvent`. Gig / Demand does not create ad hoc processed-event tables for ordinary internal domain events.

### Events are not commands

`GigAssignmentAccepted` means acceptance occurred. Transaction / Order may react by invoking its own `createOrderFromGigAssignment` command; the event itself does not authorize direct Order mutation.

---

## 22. Background Jobs / Scheduled Work

### `expireGigs`

- **Purpose:** find open/paused Gigs whose `closesAt` has passed and invoke the owner expiration transition.
- **Owner:** Gig / Demand policy using shared scheduler/queue.
- **Input:** cursor/batch/time cutoff; target Gig IDs or query cursor.
- **Idempotency key:** `gig-expire:{gigId}:{closesAt}` or equivalent canonical semantic key.
- **Retryable failures:** DB transient errors, queue transport failures, Search/Notification downstream effects.
- **Permanent failures:** Gig no longer in an expirable state, invalid target, already terminal.
- **Dead-letter/manual review:** repeated unexpected owner transition failure; record IntegrationFailure/queue telemetry.
- **Business truth updated:** only Gig status through owner command.
- **Telemetry:** attempted/expired/skipped/conflict/failure counts, latency, correlation ID; no private content.

### `reconcileAssignmentOrderHandoff`

- **Purpose:** detect accepted assignments expected to have an Order but missing/unknown handoff completion and re-request Transaction / Order conversion through its public interface.
- **Owner:** Gig / Demand may own source-side reconciliation; Order remains destination truth.
- **Idempotency:** source assignment ID/version is the semantic handoff key; Transaction / Order must independently guarantee one Order per accepted source under its policy.
- **Failure rule:** an accepted assignment remains valid Gig truth if Order is temporarily unavailable; reconciliation must never fabricate an Order ID.
- **Dead-letter:** surface to Ops after bounded retries.

Generic queue mechanics, retries, leases, dead-letter state, and telemetry use SH-047 `enqueueReliableJob`, SH-048 `executeRetryWithBackoff`, and shared worker infrastructure.

---

## 23. Concurrency and Idempotency

### Races to prevent

1. Two Professionals concurrently submitting duplicate response rows for the same Gig/Profile.
2. Customer accepting two competing responses at the same time.
3. Response withdrawal/rejection racing with acceptance.
4. Duplicate acceptance retries creating duplicate assignments/events.
5. Assignment→Order handoff retry creating duplicate Orders.
6. Gig expiration racing with acceptance or publication update.
7. Stale customer edits overwriting a newer status transition.

### Constraints already available

- `GigResponse @@unique([gigId, professionalProfileId])`.
- `GigAssignment.gigResponseId @unique`.
- downstream Order schema provides a unique GigAssignment source relation.

### Missing constraint

Current schema does not enforce the approved single-award MVP invariant. Acceptance must serialize competing commands; the physical database enforcement design remains a separate schema/migration gate.

### Acceptance transaction

Under the confirmed single-award MVP rule, `acceptGigResponse` must:

1. claim command idempotency;
2. lock `gig:{gigId}` or use an approved equivalent serializable/CAS strategy;
3. load Gig and target response under the same consistency boundary;
4. verify controlling customer and states;
5. perform fresh Professional readiness and applicable hold checks before final write;
6. revalidate state after any external call if the lock cannot be held across dependency latency, or structure the command using versioned decision inputs;
7. enforce assignment cardinality;
8. update response + assignment + Gig state atomically;
9. write outbox event atomically;
10. persist idempotency result.

No in-memory mutex is acceptable for database-owned concurrency.

---

## 24. Media / Storage

- `GigMedia` is the only Gig-owned attachment meaning currently confirmed.
- Upload context should use the canonical Gig media context defined by Media / File Access.
- Gig / Demand may request/validate attachment of a ready MediaAsset.
- It must not mark MediaAsset ready, bypass malware/MIME/metadata processing, choose raw storage keys, or create permanent public URLs.
- Public Gig projection may include only Media-approved public/processed references according to Media and Search contracts.
- Private Gig media is delivered through Media signed access after contextual authorization.
- SH-127 `requestMediaAccess` is transport, not Gig entitlement truth.
- Detaching `GigMedia` does not automatically delete `MediaAsset`; Media/privacy/moderation retention rules decide object disposition.

---

## 25. Search / Projection

### Source truth

`Gig` remains source truth.

### Gig-owned source projection

`buildGigSearchSourceProjection` should deterministically expose only allowlisted fields such as:

- Gig ID/source version;
- public title/description excerpt if policy permits;
- status/visibility facts needed by Search;
- canonical taxonomy IDs;
- budget/currency if public policy permits;
- `remoteOk`;
- public-safe fuzzy location projection/reference;
- approved public media references;
- closes/due information when appropriate.

Exact private location and private media must not be included.

### Search-owned behavior

Search / Public Visibility owns:

- `SearchUpsertEvent`;
- Typesense schema/client;
- indexing/hide/remove/restore execution;
- reconciliation/backfill;
- public search queries/ranking.

### Triggers

After committed source changes that affect public discovery, call SH-091 `requestSearchProjectionRefresh` with entity ID, action/reason, source version, requester Module, and idempotency key.

Projection failure does not roll back Gig source truth.

---

## 26. Notification

Gig / Demand owns notification **triggers and business meaning**, not delivery.

Likely trigger intents:

- new response received;
- response viewed/shortlisted if product chooses to notify;
- response rejected/withdrawn;
- response accepted / assignment created;
- Gig paused/cancelled/expired where participants need notice;
- assignment lifecycle change.

Use SH-041 `requestNotification` with:

- recipient User IDs resolved from source relationships;
- template key;
- sensitivity classification;
- minimal variables;
- action route;
- idempotency key tied to source event.

Do not put full proposal messages, exact locations, private media URLs, or sensitive verification reasons in push/email/SMS payloads.

---

## 27. Audit and Sensitive Access

### Domain truth

Gig/Response/Assignment source rows and transactional domain events remain domain truth.

### Generic audit

Use SH-029 `appendAuditEvent` for significant actions such as:

- Gig publication/cancellation/admin correction;
- response acceptance;
- assignment cancellation or admin override;
- privacy/moderation execution where audit policy requires.

### Sensitive access

Ordinary Gig reads are not automatically sensitive-access events. Private/sensitive Media access is audited through Media/Audit rails. If future Gig fields become specially sensitive, use SH-030 `recordSensitiveAccess` rather than creating a local access-log table.

### Separation

AuditEvent is not a Gig lifecycle ledger. Queue/System/IntegrationFailure telemetry is not Gig truth.

---

## 28. Privacy and Retention

### Subject-data inventory

Gig / Demand must enumerate, at minimum:

- Gig title/description/location and timing fields;
- `posterUserId` and `customerProfileId` relationships;
- GigResponse message/proposal/actor fields;
- GigAssignment actor references, accepted terms, timing fields;
- GigTag and GigMedia contextual relationships;
- owner event/outbox references as supported by platform privacy policy.

### Privacy executor

`executeGigPrivacyInstruction` accepts a Privacy-defined target/disposition and returns the canonical privacy target result. It may erase, anonymize, restrict, detach, export, retain, or skip only as authorized.

### Retention

- unconverted draft/cancelled Gig content may be eligible for stronger erasure than accepted/Order-linked commercial records;
- once commercial terms are frozen into Order, Order retention is independently owned by Transaction / Order;
- Gig / Demand supplies retention facts but Privacy owns `DataRetentionExemption` records;
- no retention duration is currently confirmed; destructive purge must wait for approved legal/policy rules.

### Search/media downstream effects

Privacy execution may request Search removal and Media contextual detach/deletion through owner interfaces. Gig / Demand must not delete Typesense/R2 directly.

---

## 29. Observability

Use canonical:

- SH-032 `createRequestContext`;
- SH-033 `writeStructuredLog`;
- SH-034 `sanitizeTelemetryMetadata`;
- SH-035 `captureException` where platform wrapper applies;
- SH-036 `emitMetric`;
- SH-037 `recordIntegrationFailure`;
- shared queue telemetry.

Recommended safe dimensions:

- operation name;
- aggregate type;
- Gig/Response/Assignment ID where permitted;
- status transition names;
- dependency owner;
- decision category/reason code;
- retry count;
- latency;
- request/correlation IDs.

Never log full Gig descriptions if unnecessary, response messages, exact private addresses, signed URLs/tokens, private media metadata, raw verification evidence, provider payloads, or notification content.

Operational failure never changes source truth by itself.

---

## 30. Security Boundaries

1. Validate every mutation server-side with typed/Zod schemas under root code standards.
2. Never trust client actor/customer/professional ownership fields.
3. Require authority decisions for protected reads/writes.
4. Rate-limit Gig creation and response submission using platform policy when available; do not create a separate limiter implementation.
5. Use canonical idempotency for create/respond/accept and retryable transitions.
6. Use DB concurrency controls for acceptance and other conflicting lifecycle changes.
7. Do not store or emit raw provider secrets/status payloads.
8. Do not expose exact location publicly; use Location Safety.
9. Do not expose private media through permanent URLs.
10. Keep notification/event/log payloads minimized.
11. Do not accept `invite_only` behavior until an authoritative audience model exists.
12. Do not use `TrustBadge` or local booleans as verification/readiness proof.

---

## 31. Error / Decision Result Pattern

Public interfaces should return stable categories rather than framework/provider errors.

### Error categories

- `validation_error`
- `unauthenticated`
- `forbidden`
- `not_found`
- `conflict`
- `stale_version`
- `gate_denied`
- `unsupported`
- `dependency_unavailable`
- `retryable_failure`
- `terminal_failure`

### Gig reason-code namespace

Representative stable reason codes may include:

- `GIG_NOT_EDITABLE`
- `GIG_NOT_PUBLISHABLE`
- `GIG_NOT_OPEN_FOR_RESPONSES`
- `GIG_INVITE_ONLY_UNSUPPORTED`
- `GIG_CLASSIFICATION_INVALID`
- `GIG_MEDIA_NOT_READY`
- `GIG_PUBLIC_LOCATION_UNAVAILABLE`
- `GIG_BLOCKED_BY_HOLD`
- `GIG_RESPONSE_ALREADY_EXISTS`
- `GIG_RESPONSE_NOT_EDITABLE`
- `GIG_RESPONSE_NOT_ACCEPTABLE`
- `GIG_PROFESSIONAL_NOT_READY`
- `GIG_ASSIGNMENT_CARDINALITY_CONFLICT`
- `GIG_ASSIGNMENT_TRANSITION_INVALID`
- `GIG_SOURCE_VERSION_STALE`

Provider-specific error strings must never become public domain reason codes.

---

## 32. Testing Architecture

### Domain unit tests

- draft/budget/timing validation;
- publication policy composition;
- each approved Gig transition allowed/forbidden;
- each approved response transition;
- each approved assignment transition;
- source projection allowlist;
- privacy field disposition maps.

### Public contract tests

- SH-004 `resolveCustomerActor` consumption;
- taxonomy validation/requirements;
- SH-016 `evaluateProfessionalReadiness` response gate;
- ComplianceHold decision;
- Media attachment validation;
- Location Safety fuzzy projection;
- Search refresh request;
- Messaging SH-113 `ensureContextThread`;
- Notification request;
- `getGigAssignmentCheckoutSource` consumed by Transaction / Order;
- privacy executor contract.

### Database/integration tests

- `GigResponse` uniqueness;
- `GigAssignment.gigResponseId` uniqueness;
- approved assignment cardinality constraint once ruled;
- atomic acceptance transaction;
- outbox written with source mutation;
- stale update/lock conflicts;
- indexes/query plans for customer lists and open Gig discovery source queries.

### Authorization tests

- wrong customer cannot update/publish/accept;
- wrong Professional cannot revise/withdraw another response;
- unrelated User cannot view private Gig/response details;
- admin/support action requires explicit authority.

### Compliance/readiness tests

- Professional readiness allow/deny/review/unavailable;
- high-risk requirement context passes through owner interface;
- active hold blocks only approved actions;
- no raw verification/hold table reads inside Gig repositories.

### Idempotency/concurrency tests

- duplicate Gig creation key;
- duplicate response submit;
- concurrent duplicate response insert;
- two competing response acceptances;
- response withdrawal versus acceptance race;
- acceptance retry replay;
- expiration versus acceptance;
- assignment→Order handoff retry.

### Privacy tests

- enumerate all Gig-domain subject records;
- erase/anonymize/detach/retain result categories;
- retained accepted terms do not trigger unauthorized destructive delete;
- Search/Media follow-up requests are owner-boundary calls.

### E2E participation

- customer Gig draft → publish;
- eligible Professional → response;
- customer manages responses;
- accepted response → assignment;
- assignment source → exactly one Order through Transaction / Order contract.

No provider adapter tests belong here because this Module owns none.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `Gig`, `GigResponse`, and `GigAssignment` are mutated only through Gig / Demand-owned application/domain operations.
2. `Gig` is never treated as Offering or Job.
3. `GigResponse` is never treated as JobApplication.
4. `GigAssignment` is never treated as Order/payment truth.
5. One ProfessionalProfile has at most one GigResponse row per Gig.
6. A response acceptance must perform a fresh Professional readiness check.
7. Response acceptance must be idempotent and concurrency-safe.
8. Assignment cardinality must match the explicitly approved ruling; current schema permissiveness is not permission to choose.
9. New buyer-domain writes must not silently ignore the CustomerProfile architecture direction; migration semantics must be explicitly approved.
10. `posterUserId`/`buyerUserId` are not a substitute for CustomerProfile commercial truth once CustomerProfile migration is complete.
11. `invite_only` must remain disabled/unsupported until authoritative audience truth exists.
12. Gig / Demand never computes verification readiness from raw `VerificationCheck`, TrustBadge, KYC, tax, healthcare, entitlement, or hold tables.
13. Gig / Demand never creates local compliance block flags.
14. Gig / Demand never writes TaxonomyDomain/Category/Tag truth.
15. `GigTag` does not transfer taxonomy ownership.
16. `GigMedia` does not transfer MediaAsset/file ownership.
17. No direct R2/S3 signed URL or file scanning code belongs here.
18. No direct Typesense/SearchUpsertEvent write belongs here.
19. Search failure cannot erase or roll back a valid committed Gig source transition.
20. No direct email/SMS/push provider call belongs here.
21. No custom chat/thread table belongs here.
22. No Stripe/payment/refund/payout provider call belongs here.
23. Outbox events are facts, not disguised direct writes to neighboring Modules.
24. Audit/observability records never replace Gig-domain state.
25. Product archive/cancel is not privacy erasure.
26. PrivacyRequest/DataErasureJob lifecycle never lives here.
27. ModerationCase/ModerationAction truth never lives here.
28. Exact private location is not emitted in public search/event/notification payloads by default.
29. No in-memory mutex is used for distributed acceptance concurrency.
30. Every unresolved architecture decision is surfaced as a blocker rather than guessed.

---

## 34. Prohibited Duplicate Implementations

Do not generate these or equivalent local responsibilities inside `gig-demand`:

- `gigAuth.ts`, `requireGigUser.ts`, `currentGigUser.ts`;
- `gigPermissions.ts`, `gigRbac.ts`, `assignmentAuthorizationService.ts` as generic permission engines;
- `buyerResolver.ts`, `customerContextHelper.ts` duplicating CustomerProfile resolution;
- `gigEligibilityService.ts`, `professionalCanRespond.ts`, `verificationGate.ts` that compose readiness locally;
- `highRiskGigChecker.ts` with copied verification/category rules;
- `gigBlockService.ts`, `isGigBlocked.ts`, `blockedByCompliance` source flag;
- `gigCategoryValidator.ts` or local tag normalization registry;
- `gigFileScanner.ts`, `gigUploadService.ts`, `gigPresignedUrl.ts`, direct R2/S3 client;
- `gigTypesenseService.ts`, `indexGig.ts`, `gigSearchSync.ts`, direct `SearchUpsertEvent` repository;
- `gigEmailService.ts`, `gigSms.ts`, `gigPush.ts`;
- `gigChatService.ts`, `responseThreadRepository.ts`, custom Thread/Message tables;
- `stripeGigService.ts`, Stripe webhook handlers, payment-status translation;
- `gigIdempotency.ts` or local generic processed-command table;
- in-memory `acceptanceMutex`, `assignmentSemaphore`, custom distributed lock;
- `gigCron.ts` that directly mutates statuses instead of shared scheduler → owner command;
- `gigGdprWorkflow.ts`, local privacy request/erasure lifecycle;
- local moderation case/report system;
- local generic audit/access log;
- `isPremiumGig`, local posting quota/boost/waiver/commission flags unless a future approved Track-owned entitlement explicitly requires a downstream snapshot.

---

## 35. Unresolved Decisions

| Decision | Current evidence | Implementation impact |
| --- | --- | --- |
| Single-award database enforcement | Single-award MVP is confirmed; Prisma permits multiple assignments. | Later enforcement design/migration; remaining acceptance transitions still require approval. |
| Exact Gig transition matrix | Enum exists; no approved graph. | Blocks pause/reopen/assigned/completed automation beyond settled subset. |
| Exact GigResponse transition/edit rules | Enum and uniqueness exist; edit-window rules absent. | Blocks final `reviseGigResponse` state policy. |
| Exact GigAssignment transition semantics | Enum exists; `proposed` and `disputed` meaning unclear. | Blocks full assignment lifecycle. |
| CustomerProfile physical migration | New buyer-domain identity requirement is confirmed; current fields remain nullable. | Historical backfill, physical enforcement, and legacy User reference semantics remain unresolved. |
| `posterUserId` / `buyerUserId` semantics | legacy/auth IDs remain; `buyerUserId` lacks explicit relation on assignment. | Requires schema/migration ruling and audit/reference semantics. |
| `invite_only` authority | enum exists; no invitation/audience record. | `invite_only` must remain unsupported. |
| Completion synchronization | Gig, Assignment, and Order each have completion concepts. | Blocks automatic Gig completion from downstream facts. |
| Dispute effect on assignment | Assignment has `disputed`; Dispute owns case truth. | Need event mapping and restoration semantics. |
| Dedicated Gig lifecycle event ledger | no model exists; outbox + Audit available. | Do not add without architecture approval. |
| Retention durations | legal/privacy obligations recognized; no durations supplied. | Blocks destructive purge/retention expiry logic. |
| Gig-specific Track entitlement | Track is cross-cutting but no Gig-specific key is confirmed. | Do not implement premium/posting limits/boosts. |

---

## 36. Architecture Decision Summary

### Binding confirmed rulings

1. `gig_demand` owns `Gig`, `GigResponse`, `GigAssignment`, their status meaning, and demand-side marketplace policy.
2. `GigMedia`/`GigTag` are contextual joins; Media/Taxonomy retain underlying truth and mechanics.
3. Gig is demand, GigResponse is a commercial proposal, and GigAssignment is accepted work—not Offering, JobApplication, or Order.
4. Order/payment truth remains Transaction / Order and Payment / Payout / Tax.
5. Professional response readiness is consumed from Professional Eligibility.
6. ComplianceHold is consumed from the hold owner; no local blocked flags.
7. Search, Messaging, Notification, Media, Privacy, Audit, Observability, and provider mechanics remain externally owned.
8. Canonical idempotency, concurrency, state-machine plumbing, outbox, queue, logging, and privacy protocols must be reused.
9. Response uniqueness is one ProfessionalProfile per Gig.
10. `invite_only` cannot be implemented until an audience authority exists.

### Confirmed reconciliation rulings

- **Confirmed CL-04-R002 (not a proposal):** at most one accepted/current winning GigAssignment per Gig for MVP; serialize competing acceptance.
- **Confirmed SH-046 (not a proposal):** all cross-Module Gig-domain effects publish through the canonical outbox.

**Confirmed CL-04-R007:** CustomerProfile is required semantic buyer identity for new Gig/assignment records. Historical backfill and permanent legacy User reference semantics remain unresolved.

### Proposed Rulings requiring explicit acceptance

1. **Acceptance concurrency:** use canonical aggregate lock on Gig plus idempotent command result.
2. **Assignment creation:** acceptance creates `GigAssignment.status=accepted` directly; `proposed` remains unsupported until a separate workflow is defined.
3. **Source interface:** Transaction / Order consumes `getGigAssignmentCheckoutSource` instead of reading Gig repositories.

### Still unresolved

The exact transition graphs, completion/dispute synchronization, CustomerProfile backfill details, retention duration, and any Gig-specific entitlement remain unresolved until explicitly ruled.

---

## 37. Coding-Agent Usage

Before implementing or changing this Module, an agent must read in order:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry;
5. CL-04 `architecture.md`;
6. CL-04 `build-plan.md`;
7. this `gig_demand/module-architecture.md`;
8. this `gig_demand/implementation-plan.md`;
9. public-interface sections for direct dependencies, especially Customer / Buyer Profile, Role / Authority, Taxonomy & Classification, Professional Eligibility, Admin Review / Compliance Hold, Media / File Access, Location Safety, Messaging, Notification, Search / Public Visibility, Transaction / Order, Privacy / Data Erasure, Content Moderation, Audit, and Observability;
10. `progress-tracker.md`.

For each numbered feature, the agent must verify that required Proposed Rulings have been explicitly accepted before writing schema or lifecycle behavior that depends on them. If not, stop at the boundary, record the blocker, and implement only the already-settled behavior.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.


## WA-R024 — Financial readiness is action-specific

Class: **AI_RESOLVED_WITH_TRADEOFF** from the approved separation of Identity, optional screening, Professional readiness and financial execution. Preserve the existing Professional identity/KYC baseline; do not equate optional background screening with KYC. Payment's financial decision identifies the named action and the applicable KYC, tax, account and restriction dimensions, rather than exposing one timeless professional-is-financially-ready boolean.

Profile editing/drafting never requires payout readiness. Public activation/publication/Gig response uses the applicable Professional identity, Track, taxonomy/Trust/Healthcare and Hold policies; incomplete payout-account or tax setup alone is not a new universal nonfinancial block unless an explicit applicable requirement demands it. Paid acceptance/checkout must meet Payment's current charge/recipient capability for that flow; payout execution requires current recipient/account/KYC/tax/hold requirements. The purchaser cannot be charged through an unsupported recipient capability merely because a listing is visible. UI shows the owner-provided unavailable transaction state without leaking the seller's private KYC/tax details.

Tradeoff: discoverability and action readiness can differ; each attempted financial action re-evaluates current Payment facts. This avoids silently extending payout-only requirements to every public profile or treating a public listing as financial clearance. Provider/regulatory prerequisites may tighten the financial action and remain EXTERNAL_REQUIREMENT. No legal threshold, automatic KYC approval or alternative sponsorship flow is invented.

This resolves the universal-versus-action-specific architecture in CL03-HD001 / CL-03 U-01 / PE-U01 / Payment UD-01. Implement the action/dimension matrix and owner fixtures before activation; do not treat this as proof that the selected provider permits a particular charge/transfer. Existing settled optional screening and explicit free Track baselines remain binding.

## WA-R029 — Approved digital refund, download and seller-acceptance policies (P09–P11)

Binding product-owner ruling: 2026-10-01 America/New_York (2026-10-02 UTC). Supersedes the open P09–P11 alternatives and contrary conceptual payment/acceptance sequences. WA-R028 continues to govern truthful delivery evidence.

P09: At launch, digital access, grant issuance, streaming and download completion never automatically make a purchase non-refundable. Delivery/access evidence may inform authorized refund/dispute review but never determines the result alone. Apply the applicable product/refund policy, dispute facts and required external/legal rules. An approved refund or revocation triggers only the downstream access consequences specified by the owning Order/Digital Goods policy. Download history alone neither revokes access nor preserves it against an authorized revocation. No automatic `final_after_access` denial is enabled by a stored enum value.

P10: Consume one allowance only when one user-initiated logical download successfully completes with verified delivery. Retries, resumes, range requests, duplicate transport attempts and recovery of the same logical download consume no additional allowance. Failed or unverified delivery consumes zero. A genuinely new user-initiated download after a completed one may consume another allowance only when the applicable product policy actually limits download count. Finite `used` means allowance exhausted; unlimited grants are not exhausted by first use. Completion observation proves delivery, not human reading or legal acceptance.

Digital Goods mints and persists the logical-download identity at explicit user initiation, with actor/asset-version/grant/Order/policy binding. Transport retries cannot mint a new identity. Atomically convert that intent's reservation to one consumption on its first verified completion; a unique consumption reference prevents duplicates. Resumes retain the same identity. A new explicit post-completion initiation is a new logical identity, subject to policy and current authorization. Unverified attempts remain zero-consumption even while their in-flight reservation is reconciled. Bound reservation lifetime through server-side access expiry/revocation and reconcile before releasing capacity; never strand allowance indefinitely or release while an old transfer remains capable of independently completing. Late receipts reconcile to the original identity and cannot charge another allowance. Provider evidence incapable of proving the approved completion event cannot support finite-count consumption; do not substitute URL issuance, elapsed time or client claims. This capability requirement gates that delivery adapter, not P10's product meaning.

P11: For live or seller-performed services, final capture requires seller acceptance. Acceptance is either explicit approval of the specific Order/Gig/service request or valid precommitted acceptance: the seller intentionally configured an approved instant-book/availability/product policy and the frozen requested transaction satisfies all its constraints. A matching accepted Gig award satisfies acceptance; merely publishing a service does not. Published standalone downloads and self-paced digital courses/products may auto-accept because fulfillment requires no later seller performance decision. Payment authorization/holds may precede acceptance where Payment architecture permits; authorization is not final capture. Platform screening has its separate approved source, with no fabricated seller.

Order records immutable acceptance evidence: seller/context, explicit decision or intentional precommit policy identity/version, frozen scope/price/package version, applicability result and timestamp. A precommit must be active and applicable when accepted, scoped to the actual seller/product, and cannot be inferred from a premium flag or open calendar alone. Policy changes do not rewrite already recorded acceptance; material requested scope/price changes require fresh acceptance of the changed terms. Recheck current financial capability, cancellation/hold and payment authorization validity immediately before capture. Payment accepts a uniquely identified Order-authorized capture intent with acceptance proof; retries preserve that effect identity and uncertain outcomes reconcile before any new capture. No capture from stale acceptance for different terms or from mere Booking existence.

Order remains transaction truth and Booking owns individual scheduled sessions. Acceptance is evidence within Order, not a second Order/Booking lifecycle or a separate booking authority. A multi-session package acceptance binds purchased scope; each Booking still uses current eligibility/conflict checks and bounded Order session authorization. Instant booking does not bypass locks, consume nonexistent availability or displace customers. Decline/expiry releases only valid owner reservations/authorizations; any already captured amount follows an independently authorized refund. Numerical response windows remain versioned policy, not invented here.

Implementation acceptance requirements: access/completion cannot auto-deny refund; authorized revocation follows current owner policy; aborted/unverified delivery zero consumption; range/resume/replay one consumption; new post-completion initiation counts only under bounded policy; concurrent last allowance; late receipt reconciliation; explicit versus valid precommitted acceptance; absent/revoked/inapplicable precommit denied; changed terms need new acceptance; Gig acceptance matching; authorization-before-acceptance permitted but capture-before-acceptance denied; capture retries idempotent; Booking conflict rules unchanged. These are required tests, not executed runtime claims.

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


## WA-R039 — Gig acceptance integrity, lifecycle evidence and downstream synchronization

Classification: AI_RESOLVED_WITH_TRADEOFF for technical boundaries; P14/P15 below remain PRODUCT_OWNER_CHOICE. This resolves named Gig alternatives, not the complete commercial transition graph.

Serialize award selection on the Gig aggregate through shared database locking and an expected aggregate revision. In one owner transaction, validate current response revision/status, buyer authority, Professional readiness and restrictions; persist the winning assignment, immutable accepted terms, response acceptance, Gig assignment state, owner history and outbox. The command fingerprint binds the selected response revision, price/currency and scope. A retry with the same key/payload replays the same assignment; changed terms conflict. A concurrent revision, withdrawal or competing acceptance cannot commit against the old expected version. No network/provider effect occurs while holding the award lock.

Enforce at most one current winner in the database with a unique partial index on GigAssignment.gigId where an explicit isCurrentWinner flag is true. This flag is Gig-owned award-slot identity, not a payment/fulfillment status. Set it only in the serialized award transaction; completed and disputed assignments retain their winning slot. Historical cancellation does not automatically release the slot or reopen bidding. A future authorized replacement must atomically retire the old slot and claim the new one under an explicit product policy; this ruling does not authorize re-award. Retain a composite reference/constraint proving that the accepted response belongs to the same Gig and Professional. Keep one-response-per-Gig/Professional uniqueness. Exact column names and forward SQL belong to the integration migration owner; current schema does not yet enforce this design.

Create assignments directly in accepted after the accepted response/terms proof commits. The proposed state remains reserved: no counteroffer or second acceptance lifecycle is introduced. getGigAssignmentCheckoutSource.v1 returns assignmentId, gigId, customerProfileId, buyerUserId attribution, sellerProfessionalProfileId, accepted response revision, immutable scope/price/currency, seller-acceptance evidence reference, source revision and current checkout eligibility. It contains no provider or private location fields. Order validates current source and binds the immutable terms to its own unique logical purchase. Source edits cannot rewrite an existing purchase. P11's seller-acceptance evidence must be present; a buyer action alone cannot fabricate a Professional's acceptance of changed terms.

Gig owns append-only lifecycle and accepted-term revision history for Gig, GigResponse and GigAssignment. Minimum evidence: aggregate type/id and revision, command/fingerprint, actor/context, prior and next status, changed term revision, source decision/evidence references, occurrence time and outbox event identity. Generic Audit and a purgeable outbox cannot replace this history. Response edits, if approved under P14, create a new immutable proposal revision and update the current pointer; they never overwrite the accepted proposal. Retention periods and eligible personal-field disposition remain external Privacy/legal policy.

Order remains transaction/completion truth. Booking session completion and Digital Goods delivery evidence go to Order; they cannot independently complete a multi-session Gig purchase. Gig consumes a versioned Order completion outcome referencing the exact source assignment and frozen purchase: only an owner-confirmed fully completed Order may advance the corresponding assignment/Gig completion projection. A stale/duplicate receipt cannot regress state or emit a new completion award. The assignment's delivered fact is not payment, payout permission or final Order completion. Reward qualification consumes its approved owner fact once, not both a propagated Gig event and its original Order event.

Review/Dispute owns each case/cycle. Gig records the case identity, cycle, source version and prior operational state as relationship-impact evidence. An open dispute may project disputed for an active/delivered assignment under current policy; a later dispute about a completed assignment preserves completed history and records dispute overlay rather than reopening fulfilled work. Case closure alone does not restore or cancel work: apply the specifically authorized current Order/Dispute outcome, rechecking restrictions and expected revision. Never replay capture/refund/payout on entering or leaving disputed. Full post-award cancellation/replacement behavior remains outside this technical mapping and cannot be inferred from enum values.

Pre-award demand supports draft→open/cancelled/archived; open→paused/cancelled/expired; paused→open/cancelled/expired. Publish/resume rechecks current readiness/visibility, and expiry requires its configured closesAt. Acceptance moves open→assigned only through the atomic award command. Completed/cancelled/expired may archive without deleting evidence or obligations. No archived self-reopening or automatic re-award is approved. Assigned cancellation must follow the Order owner's authorized cancellation outcome and any outstanding obligations; local Gig cancellation cannot void a purchase. The remaining response edit and nonwinning-response policy awaits P14/P15 before the complete acceptance transition contract is frozen.

Keep invite_only disabled until a separately approved audience owner and access contract exist. No speculative Gig posting limits, premium gate or boost are introduced: Track keys must come from an approved benefit. CustomerProfile backfill follows WA-R031's one-profile-per-User resolver, original attribution preservation and conflict quarantine; never infer actor identity from names. Legal retention durations remain EXTERNAL_REQUIREMENT, not an invented purge schedule.

Required implementation verification: competing award attempts; revise/withdraw versus acceptance; replay with altered payload; mismatched response/Gig; completed winner retaining its slot; one Order per logical purchase; stale completion; multi-session partial fulfillment; dispute closure without financial replay; immutable proposal and lifecycle history. These are future execution requirements, not runtime tests passed in this reconciliation.

P14: viewed/shortlisted response edit rights are not settled by ownership or concurrency. Recommend allowing revisions in submitted/viewed/shortlisted until acceptance, rejection or withdrawal, with immutable history and acceptance of the exact current revision. Alternative: lock terms once viewed (or shortlisted). Production edit eligibility remains blocked pending the owner.

P15: single-award cardinality does not decide whether other proposals are automatically rejected. Recommend mark remaining nonterminal responses rejected with reason another_response_selected after successful award, preserving history; keep withdrawn/rejected records unchanged. Alternative: retain their statuses as inactive historical proposals, with acceptance disabled while the winner exists. Neither option authorizes cancellation-driven reopening or re-award. Production loser disposition remains blocked pending the owner.


## WA-R040 — P14/P15 approved

 received 2026-10-02. Supersedes WA-R039's open P14/P15 recommendations.

Professionals may revise active submitted, viewed or shortlisted proposals until accepted, rejected or withdrawn. Preserve immutable revisions. Material changes to price, scope, timing, included work or other acceptance-relevant terms must be visibly identified to the Customer. Viewing or shortlisting does not lock the proposal.

Acceptance binds an immutable snapshot of the latest revision actually presented for acceptance. The request carries that presented revision and terms fingerprint; under the Gig award lock compare it with the current proposal revision. If it changed, reject stale acceptance and require presentation of the new terms. Never silently substitute unseen newer terms. Accepted proposal terms cannot be rewritten by proposal editing; changes go through the owning Order/agreement/change workflow.

When a single-award Gig selects its winner, automatically reject other active submitted/viewed/shortlisted proposals with canonical reason ANOTHER_RESPONSE_SELECTED. Preserve records and immutable histories; leave previously terminal responses unchanged. Award, capacity exhaustion, rejection decisions and outbox effects commit under one serialized owner transaction so concurrent edits/submissions/acceptance cannot escape the closed award capacity. Retries reproduce the same effects. Notification delivery occurs after commit and is idempotent per source transition.

Launch capacity remains one. This rule is defined at award-capacity exhaustion; a future explicitly approved multi-award Gig must reject remaining active proposals only when its remaining capacity is exhausted. The launch unique-winner constraint is a launch implementation constraint, not a permanent prohibition on a future approved capacity model. No multi-award feature, re-award or cancellation-driven reopening is activated by this ruling.

Required implementation checks: edit after viewed/shortlisted; visible material-change marker; acceptance of presented current revision; stale presented revision conflict; edit-versus-accept serialization; accepted terms immutable; winner plus loser rejection consistency; concurrent submission after exhaustion denied; replay without duplicate effects; terminal proposal preservation; future capacity-policy test proving rejection is conditional on exhaustion. These are acceptance requirements, not executed runtime evidence.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P16

A Professional may report completion or no-show for an authorized service session. Authorized support may confirm, correct or adjudicate the service-performance state where policy permits; the Customer can contest the report. Preserve immutable report/correction history, reporting actor and authority, occurrence/recorded time, evidence references, affected session and which participant allegedly failed to attend. A correction references the original; it does not erase it. Reported outcome and contested/adjudicated status are distinguishable, so a Professional assertion is never represented as independent support verification.

Completion/no-show status alone must not automatically trigger refund, charge, payout release, forfeiture, review eligibility or any other financial consequence. Order, Payment/Payout, Review/Dispute, Booking and the applicable policy owner each evaluate their owned consequences from current authorized evidence. A single session report never proves full multi-session Order completion. Clock passage does not fabricate a performance report.


## WA-R048 — Order, Agreement and Gig outcome contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Order is the only commercial transition owner. Adopt the following guarded transition contract; status names cannot replace predicates and the older conceptual paid-before-seller sequence is superseded. Creation starts draft from a validated immutable source DTO. A source-specific `agreementRequirement` contains required/not-required, requirement policy revision, and (when required) an approved template key/version; missing requirement evidence blocks checkout rather than defaulting to no Agreement. Marketplace supplies Offering requirements, Gig supplies accepted assignment requirements, and screening uses its approved separate source contract. Order selects the applicable approved requirement; it cannot create legal applicability from an enum.

| Current state | Command/fact and required guard | Result |
| --- | --- | --- |
| draft | immutable source/pricing ready; Agreement required | awaiting_agreement |
| draft / awaiting_agreement | no Agreement required or required execution ready; seller decision still required | awaiting_seller |
| draft / awaiting_agreement / awaiting_seller | required Agreement ready and P11 acceptance proof valid; capture not confirmed | pending_payment |
| pending_payment | Payment confirms exact authorized capture effect for frozen purchase | paid |
| paid | owner verifies current source, required Agreement and retained seller acceptance proof | accepted |
| accepted | authorized fulfillment-start command with current delivery gates | in_progress |
| accepted / in_progress | delivery-kind owner supplies qualifying delivery evidence | delivered |
| delivered | Order evaluates all purchased obligations and applicable completion policy | completed |
| any nonterminal operational state | authorized Order cancellation under applicable policy, with financial obligations separately reconciled | cancelled |

Authorization/hold of funds before acceptance is permitted by Payment architecture, but never advances paid or permits final capture without acceptance. Published digital fulfillment may advance accepted→delivered when the authoritative Digital Goods delivery predicate is satisfied; it cannot skip entitlement, policy or verification. Session completion/no-show reporting under P16 is input evidence only. Neither receipt nor session count alone manufactures an approved completion policy, review eligibility or financial action. For multi-session purchases, the frozen package defines obligations and Order evaluates them all. No timer, cancellation deadline, refund eligibility or seller-decision timeout is invented here.

A durable dispute cycle is an overlay on the last operational state, including completed/cancelled. If the legacy disputed status is exposed, retain that underlying state and case/cycle/source version explicitly. Opening or closing a case never reruns capture, refund, payout or fulfillment. Closure applies only an explicit current authorized disposition: continue the still-valid underlying state; cancel remaining fulfillment when authorized; or apply a verified refund outcome. A partial refund updates cumulative verified refund allocations without automatically cancelling unrefunded obligations. Fully refunded is a monetary outcome only after Payment confirms the full eligible captured amount; continuing access/fulfillment disposition is independently owner-authorized. Completed/cancelled history is never erased or silently reopened; correction is an append-only outcome revision. Refund reversals require a distinct authorized Payment effect, never subtraction by replaying an old event.

Retain one durable Agreement container per Order. Under it, use immutable execution revisions linked by supersedesRevisionId, each binding frozen source/pricing, approved template version, required signer set, exact document snapshot and contextual consent/signature evidence. Existing AgreementDocumentSnapshot.version is document identity, not sufficient by itself to represent execution revision identity. A correction creates a new execution revision with fresh applicable consent/signatures; previous signatures cannot be copied as acceptance. Buyer Customer and seller Professional are the supported marketplace signer roles; candidate/organization-member enum members remain reserved. Screening cannot fabricate a seller signature. Generated→consent_pending/pending_signatures is guarded by its requirements; individual signature receipts progress the revision only for the required signer against the same document; all required signatures and exact-byte finalization produce fully_signed. Void/supersede/archive preserve evidence. Expiry/manual execution remain disabled unless their approved policy/procedure is available. Template draft→active requires approval; active→retired prevents new selection; retired→archived retains historical resolvability. Editing an active template creates a new version.

Order's provider identifiers are correlation-only projections of Payment-owned effects. `stripeTransferId` is read-only legacy correlation, never transfer truth or a dispatch instruction; a collection of Payment operation/effect references represents multiple transfers/refunds. Normalized Agreement signature/document records own proof; buyerSigUrl/professionalSigUrl/pdfMediaId/finalDocumentHash are compatibility mirrors only, checked against authoritative records and never fallback authorization. Database migration must inventory readers, backfill or quarantine conflicts, then remove redundant writers; preserve history, no destructive reset.

Gig post-award outcomes consume this Order contract: accepted assignment→delivered only from matching Order delivered; accepted/delivered→completed only from matching Order completed; accepted/delivered→cancelled only from an authorized matching Order cancellation. A completed assignment retains completion history even if a later financial adjustment/dispute occurs. Gig assigned→completed/cancelled projects the matching terminal assignment; the winner slot remains occupied and no re-award is implied. Partial refunds and Booking reports cannot directly mutate these projections. Reject stale source versions; atomically record event/effect identity and history. A recovered missing event may advance directly to the verified latest outcome while preserving its source lineage, not fabricate intermediate performance.

Verify source-specific Agreement requirements, seller acceptance before capture, conflicting Agreement revisions, old-signature replay, partial package fulfillment, contested no-show, partial/full refund separation, dispute closure without effect replay, cancelled winner retention and out-of-order completion. Physical revision/source/actor constraints and migration replay remain implementation prerequisites.


## WA-R052 — Commerce source events and projection contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Owner events carry immutable eventId, event name/schemaVersion, aggregate ID/revision, occurredAt, causationId/correlationId, safe typed actor reference and minimum immutable outcome evidence. Write owner history and outbox atomically. Consumers retain durable semantic effect identity and last applied source version beyond transport inbox expiry; duplicate aliases cannot repeat effects. Public commands and queries remain distinct from facts.

| Producer contract | Minimum scoped payload | Consumer effect |
| --- | --- | --- |
| order.outcome_changed.v1 | Order ID/revision, source kind/id, frozen purchase revision, operational outcome, dispute cycle reference if relevant, authorized disposition reference | Gig records matching assignment projection; Digital Goods/Booking reevaluate their own current rights; no automatic financial or review action |
| booking.performance_reported.v1 | Booking ID/revision, Order/session authorization ref, completed/no_show allegation, reporting actor, alleged absentee for no-show, evidence ref, contest state | Order records evidence and evaluates policy; never treats allegation as automatic package completion |
| booking.performance_adjudicated.v1 | same identity plus support authority, prior report ref, correction/adjudication outcome and evidence | Order reevaluates; preserve original report and prior decisions |
| booking.confirmed.v1 / rescheduled.v1 / cancelled.v1 | Booking ID/revision, Order/session ref, schedule revision, authorized participant refs, safe reason | Video/calendar/Messaging setup or invalidation through their owners; Notification receives source-directed safe recipient references |
| review.reputation_changed.v1 | Professional ID, source/projection version and changed Review ID/revision; no private comment/evidence | Professional/Search refresh via getProfessionalReputation.v1, apply only current version |

Booking owns BookingEventActor and BookingLocationType vocabularies. Domain actor values distinguish customer/professional/support/system and retain authenticated User attribution where lawful; no free-text role can authorize a transition. Its existing completed/no_show event aliases normalize to performance-report facts, not adjudicated or commercial-completion facts. Existing proposed booking.* / calendar.* names in §12 become the owner event namespace; only the specific registered semantics qualify integration. Existing OrderCreated/OrderCompleted-style aliases normalize at ingress to their owner versioned equivalent with original event identity, never publish duplicate semantic facts. This table is architecture, not evidence of implemented producer/consumer compatibility.

Review owns `getProfessionalReputation.v1`: request Professional ID with caller context and optional known projection version; response ratingAverage (nullable when count=0), ratingCount, source revision, projection revision, asOf and readiness/staleness result. Fractional aggregate is valid under P06. A refresh event invalidates/reloads this query; consumers cannot recompute from private Review rows or mistake missing/unready result for a zero rating. Hidden/removed Reviews withdraw exactly their existing contribution; revision updates do not add a rating count. Bilateral race, tombstone and replay fixtures are required before freeze.

Notification routing remains source-selected and asynchronous: material accepted-term/proposal changes and appointment/case participant-visible changes carry an authorized destination and affected participant references; failure to deliver cannot roll back owner truth. Private adjudication/evidence never enters participant notifications. P19 uses the Order conversation with Booking/case links; those links do not expand access. Optional viewed/shortlisted alerts stay inactive absent an approved trigger/template policy. This identifies source facts; final template/recipient fan-out matrix remains with Notification convergence.

Gamification may qualify Order completion or eligible reputation changes only through its versioned rule catalog and original source event identity; propagated Gig completion is not a second earning fact. Hold consumers evaluate scoped action decisions and preserve restriction provenance; release only triggers reevaluation, never automatic restoration. Moderation commands use authorized target/action/revision plus durable receipt and local owner execution. Exact shared action, assurance, reward rule and Notification contracts still require canonical cross-rail convergence; this owner event contract does not promote adjacent proposed SH operations.


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

This Module adopts its `gig_demand` action/fact row and specifically registered producer/consumer effects in `context/reconciliation/authority-event-contracts.md`. Role interprets the catalog; this owner retains facts and lifecycle. Register each concrete protected port before activation; a grouped port row does not authorize unspecified commands.

Owner action scope: `submitGigResponse / acceptGigResponse / publishGig`. Permitted relationships: own Professional response; owning Customer selection/publication. Required owner facts: Gig owner/revision, proposal latest-presented revision/hash, active status, remaining award capacity, eligibility tokens. Assurance: B; immutable acceptance snapshot required. These facts include typed target, source revision, subject relationship, purpose/action and evaluation time; missing/stale/unavailable facts cannot authorize, and current revisions are checked again at effect. B/S/A have the precise appendix meanings; source services cannot invent human assurance.

No additional domain event is registered for this Module by this ruling; existing explicit command/receipt contracts remain authoritative.

Consumer obligations:

- `taxonomy.policy_changed.v1`: consume only the effect naming this Module — Professional/Marketplace/Hiring/Candidate/Gig/Healthcare/Trust/Search: targeted reevaluation; Job Compliance/Location only for registered requirement mappings.
- `customer.lifecycle_changed.v1`: consume only the effect naming this Module — Order/Gig: reevaluate new participation; existing rights remain owner-governed.
- `order.outcome_changed.v1`: consume only the effect naming this Module — Gig projection; Review eligibility; Booking/Digital access reevaluation; Gamification/Sweepstakes qualification.

Current-fact obligation: professional.readiness_changed.v1 does not substitute for a fresh Professional readiness check before each new protected action.

Each audience receives only its needed fields. Obtain fresh source facts before protected decisions; invalidation is not authority.

Persist source history and outbox intent atomically; use event identity/fingerprint deduplication, source-revision watermarks, tombstones and correction lineage as specified by WA-R069. Delayed facts cannot restore revoked exposure; gaps require owner replay/current snapshot. Registered Hold applicability may prompt current reevaluation only for existing typed targets/actions; release is never automatic restoration or financial execution. Source events cannot substitute for explicit Privacy/Moderation/provider effect commands or WA-R066 notification intents.

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration

Use the WA-R070 versioned source descriptor defined by AI Taxonomy and affected-target enumeration/assignment contract defined by Taxonomy. This owner supplies an opaque current source token, purpose-authorized minimized fields and assignment token, enumerates only its own joins under stable snapshot/cursor semantics, and commits accepted assignment plus immutable receipt/outbox atomically after current Taxonomy/authority/version checks. Same command key with changed fingerprint conflicts. An expired cursor requires restart; incomplete iteration never proves deletion. Extra descriptor fields reject. Routing IDs, actor context and policy metadata do not automatically become provider payload. No direct foreign repository reads or writes are permitted.

Gig participates in contextual taxonomy assignment and affected-target enumeration only. Gig remains unsupported for AI; enumeration cannot enable an AI purpose.

classificationText is a purpose-approved sensitivity-reviewed projection, not unrestricted forwarding of the underlying text. Each target/purpose must be explicitly registered with bounded serializer/output schema; missing authority, unsafe text or unqualified Healthcare context denies processing.


## WA-R074 — Contextual Customer display and Gig participation requirements

This owner adopts its source/consumer obligations in `context/reconciliation/context-query-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.

## WA-R080 — Taxonomy event and enumerator bindings (BF-046/052/072/170)

Expose only enumerateTaxonomyAffectedTargets.v1 for Gig assignments; consume term changes for current revalidation, with no Gig AI activation. The complete typed input/result, currentness, retry, failure, privacy and activation contract in `context/reconciliation/platform-architecture-rulings.md` WA-R080 is incorporated for this owner only. No foreign lifecycle or implementation qualification is implied.

## WA-R081–083 — Gate 4 bridge obligations

This owner adopts the scoped contracts in `context/reconciliation/bridge-contract-bindings.md` and the following reviewed bridge responsibilities. The named owner retains truth; another owner's query/event/receipt does not authorize a local transition. R068/069/075 and existing approved rulings remain binding. These are architecture obligations, with executable/schema/provider qualification still required before activation.

| Family | Role in current boundary | Contract and local obligation |
|---|---|---|
| BF-005 | consumer/composer | getProfessionalProfileContext; evaluateProfessionalReadiness. Track validates typed ownership, not seller readiness for enrollment. Gig and Order request their registered action-specific current decision; no generic ready flag or raw screening facts. |
| BF-006 | consumer/composer | resolveCustomerActor. Provision/resolve one Customer for the authenticated User idempotently; preserve Customer commercial identity and User authentication identity. Unavailable cannot create a consumer-local buyer. |
| BF-009 | consumer/composer | resolveEntitlement; evaluateCandidateSearchBoost; evaluatePriorityScheduling. Typed User/track/action/grant policy only. Candidate boost is non-metered 1.15 after eligibility; Booking priority changes release time only; Order freezes fees/commission. Candidate quota is 15 UTC-month applications including Premium with no withdrawal refund. Unregistered Gig/CL10 perks remain disabled; no paid odds or acquired-rights revocation. |
| BF-010 | Producer/source | requestSearchProjectionRefresh; runSearchReconciliation; reconcileSearchProjection. Source commit precedes durable refresh. Search owns generation/tombstone/provider work and completion receipts. Accepted is not removed; stale jobs cannot resurrect restricted data; current source recheck protects serving. Partial enumeration never proves orphan deletion. Reward feature refresh is conditional on an approved effect, not reward fulfillment proof. |
| BF-011 | consumer/composer | resolveEntitlement; evaluateCandidateSearchBoost; evaluatePriorityScheduling. Typed User/track/action/grant policy only. Candidate boost is non-metered 1.15 after eligibility; Booking priority changes release time only; Order freezes fees/commission. Candidate quota is 15 UTC-month applications including Premium with no withdrawal refund. Unregistered Gig/CL10 perks remain disabled; no paid odds or acquired-rights revocation. |
| BF-017 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-025 | consumer/composer | requestComplianceHold; releaseComplianceHold; typed source readiness queries. Typed primary target/action/scope/source-cause and current assurance are mandatory. Independent causes are not deduplicated together. Release requires owner-specific evidence and current all-hold evaluation; security recovery, legal clearance, refund and payout remain with their owners. Unsupported targets stay inactive. |
| BF-026 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-027 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-033 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-039 | consumer/composer | validateTaxonomyAssignment; normalizeControlledTerm; resolveTaxonomyRequirements. Validate effective-active canonical IDs, category compatibility and immutable term revisions before contextual owner writes its joins. Historical assignments retain provenance after deactivation. Missing requirement mappings are unavailable/review, never no requirements. |
| BF-040 | consumer/composer | validateTaxonomyAssignment; normalizeControlledTerm; resolveTaxonomyRequirements. Validate effective-active canonical IDs, category compatibility and immutable term revisions before contextual owner writes its joins. Historical assignments retain provenance after deactivation. Missing requirement mappings are unavailable/review, never no requirements. |
| BF-041 | consumer/composer | validateTaxonomyAssignment; normalizeControlledTerm; resolveTaxonomyRequirements. Validate effective-active canonical IDs, category compatibility and immutable term revisions before contextual owner writes its joins. Historical assignments retain provenance after deactivation. Missing requirement mappings are unavailable/review, never no requirements. |
| BF-048 | Producer/source | validateOwnedTargetReference; getClassificationSourceDescriptor.v1 where AI applies. Typed owner existence/relationship/currentness is distinct from authorization. AI receives only registered target-purpose descriptors; delivery and rail callers receive bounded target facts. No UUID existence probe, generic repository loader or cross-owner content dump. |
| BF-049 | Producer/source | No supported Gig AI target/purpose. Gig has ordinary controlled taxonomy assignment but no approved AI source DTO or purpose. Unsupported must reject and cannot be enabled by target enum or package grouping. |
| BF-053 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-054 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-055 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-056 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-058 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-063 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-065 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-066 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-067 | Producer/source | Source-approved descriptor/rendition; requestMediaAccess only via authorized context. Search accepts public-safe processed rendition references through source projection. AI launch DTO does not include arbitrary image bytes/URLs or resume content; no direct signing/download extension. Context owner approves any future extracted input. |
| BF-068 | consumer/composer | searchPublicDiscovery. Server-mediated public query over approved source projections; no provider credentials in clients, stale forbidden results filtered. Private Candidate collection, counts and raw source evidence excluded. |
| BF-071 | Producer/source | requestSearchProjectionRefresh; runSearchReconciliation; reconcileSearchProjection. Source commit precedes durable refresh. Search owns generation/tombstone/provider work and completion receipts. Accepted is not removed; stale jobs cannot resurrect restricted data; current source recheck protects serving. Partial enumeration never proves orphan deletion. Reward feature refresh is conditional on an approved effect, not reward fulfillment proof. |
| BF-075 | Producer/source | getGigParticipationRequirements.v1. Fresh Gig revision/classification/response window and capacity support respond_to_gig. No recursion from this query into Professional readiness; no competitor prices/contact/exact location. Missing applicability blocks dependent response. |
| BF-082 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-094 | consumer/composer | requestComplianceHold; releaseComplianceHold; typed source readiness queries. Typed primary target/action/scope/source-cause and current assurance are mandatory. Independent causes are not deduplicated together. Release requires owner-specific evidence and current all-hold evaluation; security recovery, legal clearance, refund and payout remain with their owners. Unsupported targets stay inactive. |
| BF-102 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-110 | consumer/composer | evaluateProfessionalReadiness composing current owner decisions. Professional composes only action-applicable readiness dimensions; Gig/Order still enforce own state/source guards. No consumer-local compliance cache or raw KYC/health query; required unavailable fails closed. |
| BF-113 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-114 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-115 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-116 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-117 | consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-123 | Producer/source | queryGigOwnerFacts; queryOrderParticipantFacts; ensureContextThread. Messaging uses current participants/source applicability; P19 Order conversation receives Booking/case navigation without wider membership. Source relationship facts are not standalone access authorization; no universal Thread admission. |
| BF-129 | consumer/composer | hold.applicability_changed.v1; verification.readiness_changed.v1; current typed decisions. Events invalidate owner decisions, not command restoration. Current target/action/source facts remain required even if event delayed; release does not republish, reopen, disclose or fulfill. No direct Search reading Hold rows. |
| BF-131 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-138 | consumer/composer | resolveEntitlement; evaluateCandidateSearchBoost; evaluatePriorityScheduling. Typed User/track/action/grant policy only. Candidate boost is non-metered 1.15 after eligibility; Booking priority changes release time only; Order freezes fees/commission. Candidate quota is 15 UTC-month applications including Premium with no withdrawal refund. Unregistered Gig/CL10 perks remain disabled; no paid odds or acquired-rights revocation. |
| BF-152 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-153 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-154 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-155 | consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-156 | consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-157 | consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-158 | consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-160 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-162 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-163 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-164 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-171 | consumer/composer | hold.applicability_changed.v1; verification.readiness_changed.v1; current typed decisions. Events invalidate owner decisions, not command restoration. Current target/action/source facts remain required even if event delayed; release does not republish, reopen, disclose or fulfill. No direct Search reading Hold rows. |
| BF-172 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-174 | Producer/source | buildSourceProjection and owner-specific public readiness; requestSearchProjectionRefresh. Source owner composes current gates and emits only allowlisted projection/revision. Professional consumes Review aggregate; Search never calculates ratings or legal clearance. Candidate remains protected opt-in; private checks/proposals/memberships/exact location excluded. Hold release re-evaluates, never republishes directly. |
| BF-175 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-176 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-177 | consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-188 | consumer/composer | hold.applicability_changed.v1; verification.readiness_changed.v1; current typed decisions. Events invalidate owner decisions, not command restoration. Current target/action/source facts remain required even if event delayed; release does not republish, reopen, disclose or fulfill. No direct Search reading Hold rows. |
| BF-203 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-204 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-205 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-210 | consumer/composer | getNotificationDeliveryState; validateNotificationActionRoute. Source receives normalized delivery uncertainty, never legal/domain success. Catalog permits only approved internal/allowlisted HTTPS contextual route with safe refs; opening reauthenticates and reauthorizes at source. No bearer token/file URL/raw destination in generic intent or evidence. |
| BF-211 | consumer/composer | getNotificationDeliveryState; validateNotificationActionRoute. Source receives normalized delivery uncertainty, never legal/domain success. Catalog permits only approved internal/allowlisted HTTPS contextual route with safe refs; opening reauthenticates and reauthorizes at source. No bearer token/file URL/raw destination in generic intent or evidence. |
| BF-218 | Producer/source | getLocationSourceFacts.v1 for registered target/purpose. Source owns exact input and revision; Location owns permitted coarse/reveal output. Candidate P17 plus approved coarse field policy is mandatory for discovery. Unsupported source-purpose or unset precision remains unavailable; no general account address or Search target implies registration. |
| BF-221 | Producer/source | getLocationSourceFacts.v1 for registered target/purpose. Source owns exact input and revision; Location owns permitted coarse/reveal output. Candidate P17 plus approved coarse field policy is mandatory for discovery. Unsupported source-purpose or unset precision remains unavailable; no general account address or Search target implies registration. |
| BF-223 | consumer/composer | Media metadata scrubbing and approved rendition readiness. Public location protection includes EXIF/GPS removal in Media-produced derivatives. Location supplies purpose/sensitivity restrictions, never file rewriting. Missing processing proof denies public rendition; exact metadata never survives through a file shortcut. |
| BF-225 | Producer/source | getLocationSourceFacts.v1 for registered target/purpose. Source owns exact input and revision; Location owns permitted coarse/reveal output. Candidate P17 plus approved coarse field policy is mandatory for discovery. Unsupported source-purpose or unset precision remains unavailable; no general account address or Search target implies registration. |
| BF-230 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-231 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-232 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-236 | Producer/source | requestSearchProjectionRefresh; runSearchReconciliation; reconcileSearchProjection. Source commit precedes durable refresh. Search owns generation/tombstone/provider work and completion receipts. Accepted is not removed; stale jobs cannot resurrect restricted data; current source recheck protects serving. Partial enumeration never proves orphan deletion. Reward feature refresh is conditional on an approved effect, not reward fulfillment proof. |
| BF-237 | consumer/composer | geocodeAddress (Location-owned adapter). Provider-neutral protected address request remains Location-owned; source authorization/minimization precede geocoder, downstream sees approved projection only. Unknown provider/region/KMS/purpose denies activation; no Search/Booking geocoder fallback or persistent provider resource assumption. |
| BF-240 | consumer/composer | queryActiveModerationRestriction. Current typed restriction/case/effect evidence is a required local gate; unavailable cannot restore. Owner executes supported effect and preserves imposed provenance; no consumer re-adjudication or raw legal evidence dump. |
| BF-242 | consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-246 | consumer/composer | requestComplianceHold; releaseComplianceHold; typed source readiness queries. Typed primary target/action/scope/source-cause and current assurance are mandatory. Independent causes are not deduplicated together. Release requires owner-specific evidence and current all-hold evaluation; security recovery, legal clearance, refund and payout remain with their owners. Unsupported targets stay inactive. |
| BF-248 | consumer/composer | requestComplianceHold; releaseComplianceHold; typed source readiness queries. Typed primary target/action/scope/source-cause and current assurance are mandatory. Independent causes are not deduplicated together. Release requires owner-specific evidence and current all-hold evaluation; security recovery, legal clearance, refund and payout remain with their owners. Unsupported targets stay inactive. |
| BF-249 | consumer/composer | queryAuditEvents; querySensitiveAccessHistory. Bounded paginated authorized redacted evidence queries, with proof/step-up where required. Audit is retained evidence, not current source permission or foreign repository expansion; no operator dashboard becomes mutation authority. |
| BF-256 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-257 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-266 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
