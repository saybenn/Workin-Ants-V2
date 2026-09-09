# Gig Demand Architecture

> **Module ID:** `gig_demand`  
> **Module name:** Gig / Demand Module  
> **Primary Cluster:** `CL-04 — Customer Demand, Order & Resolution`  
> **Document status:** Implementation-grade Module architecture. Confirmed rulings are binding; Proposed Rulings require explicit acceptance; unresolved decisions are non-authoritative and may block affected implementation.  
> **Source basis:** Workin Ants project overview, Deep Module Registry, current Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Architecture, CL-04 architecture, CL-04 build plan, and the standardized Gig / Demand Module Architecture Extract.

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

When sources conflict, use the current Workin Ants authority order: approved source-of-truth ownership rules and Deep Module Registry, then Cluster architecture/registry, then Prisma structural evidence, then Ubiquitous Language/compliance evidence, then historical Module-extract inference. A newer explicit architecture ruling overrides an older convenience claim.

### Current decision posture

The following are **not yet binding** and must not be silently implemented:

- single-award versus multi-award Gigs;
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
- assignment cardinality policy once explicitly ruled;
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
| Domain policy | Gig/Response/Assignment transition rules, Gig publication requirements, local validation, assignment cardinality once ruled | verification, hold, taxonomy, entitlement, payment, location-safety policy |
| Repositories/data access | Prisma access only for Gig-owned records and owner-local joins | arbitrary repositories for CustomerProfile, ProfessionalProfile, Order, ComplianceHold, VerificationCheck, MediaAsset, SearchUpsertEvent |
| Workers | owner-local expiration and assignment→Order handoff reconciliation | generic queue runner, provider reconciliation, Search reconciliation |
| Adapters | None owned | Stripe, Typesense, R2/S3, Checkr/Certn, notification providers |
| Public contracts | Gig commands, queries, checkout-source DTO, privacy executor, source projection builder | direct repository exposure or raw Prisma models as cross-Module API |
| Events | Gig-domain event vocabulary/payload meaning | event transport/outbox implementation or consumer inbox infrastructure |

---

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

**Proposed Ruling — buyer actor migration:** new Gig writes should require an active `customerProfileId`; `posterUserId` should remain the authenticated User/audit relation during migration. Existing null CustomerProfile rows require backfill/legacy handling before non-null enforcement.

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

**Proposed Ruling — MVP cardinality:** one accepted assignment per Gig for MVP, consistent with the product flow “customer accepts one response.” If accepted, enforce at both policy and database layers, preferably a uniqueness constraint on `gigId` or an equivalent conditional invariant compatible with any future episode model.

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
- Every concurrency-sensitive transition uses `transitionLifecycleState` plumbing plus canonical idempotency/concurrency primitives.
- Terminal/reopen rules must be explicit; no frontend-only status changes.
- No dedicated lifecycle ledger is currently confirmed. Significant transitions emit transactional domain events and selected generic audit evidence.

---

## 10. Commands

The commands below are architectural public/application operations, not claims that code already exists.

| Command | Purpose | Actor/context | Preconditions | State written | Shared operations | Effects | Idempotency / failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `createGigDraft` | Create customer demand in draft. | authenticated User + resolved CustomerProfile | valid customer actor; validated basic input | `Gig` | `resolveAuthenticatedActor`, `resolveCustomerActor`, `authorizeResourceAction`, `executeIdempotentCommand` | `GigCreated` outbox as needed | retry returns same Gig; invalid customer/validation fails before write |
| `updateGigDraft` | Edit allowed Gig fields. | controlling customer | editable status; expected version where required | `Gig`, `GigTag`, `GigMedia` context as applicable | auth, authority, taxonomy/media interfaces, optimistic concurrency if used | update event/projection request if public state affected | stale write → conflict |
| `publishGig` | Open eligible Gig. | controlling customer | publication policy; taxonomy valid; media ready; hold allows; public-safe location | Gig status/visibility | auth, authority, taxonomy, hold, Media, Location, idempotency, transition, outbox | audit + Search refresh + optional notification | Search failure does not roll back Gig truth |
| `pauseGig` | Stop new response/public availability temporarily. | controlling customer/admin if approved | allowed transition | status | auth, authority, transition, outbox | Search refresh | stale transition conflict |
| `reopenGig` | Return paused Gig to open. | controlling customer | transition approved; deadlines/gates still valid | status | auth, authority, gates, transition | Search refresh | unavailable gate → deny |
| `cancelGig` | End active demand under approved policy. | controlling customer/admin if approved | no prohibited downstream state | status | auth, authority, transition, idempotency | audit, Search refresh, notifications | conflict if assignment/Order policy forbids |
| `archiveGig` | Remove terminal Gig from normal active views. | owner/admin | terminal state | status | auth, authority, transition | Search remove | product archive is not privacy erasure |
| `setGigTags` | Mutate contextual accepted tag relationships. | controlling customer/system-approved taxonomy flow | taxonomy validates assignments | `GigTag` | `validateTaxonomyAssignment` | source-change event if public | no local normalization |
| `setGigMedia` | Attach/detach/reorder ready assets. | controlling customer | Media validates target/asset | `GigMedia` | `attachValidatedMedia` and Media owner queries | source-change event if public | no file mutation |
| `submitGigResponse` | Create one Professional response. | authenticated Professional actor + ProfessionalProfile | Gig accepts responses; readiness allowed; uniqueness | `GigResponse` | auth, authority, `evaluateProfessionalReadiness`, idempotency, outbox | customer notification | duplicate retry must not create second row |
| `reviseGigResponse` | Edit existing response under approved nonterminal policy. | response owner | editable status; readiness recheck if material | same `GigResponse` | auth, authority, concurrency | response-updated event/notification if needed | stale/terminal → conflict |
| `withdrawGigResponse` | Withdraw own response. | response owner | allowed nonterminal transition | status | auth, authority, transition | notification | accepted/terminal → conflict |
| `markGigResponseViewed` | Record customer view-state transition. | controlling customer | submitted response | status | auth, authority, transition | optional event | idempotent if already viewed or later state according to policy |
| `shortlistGigResponse` | Mark preferred response. | controlling customer | allowed state | status | auth, authority, transition | optional notification | terminal → conflict |
| `rejectGigResponse` | Reject response. | controlling customer | allowed state | status | auth, authority, transition | notification | accepted/withdrawn → conflict |
| `acceptGigResponse` | Atomically accept a response and create/replay assignment. | controlling customer | assignment cardinality ruling; Gig/response state; readiness recheck; no blocking hold | response + assignment + Gig state according to approved matrix | auth, customer actor, authority, `evaluateProfessionalReadiness`, `evaluateComplianceHold`, `executeIdempotentCommand`, `acquireAggregateLock`, `transitionLifecycleState`, `publishDomainEvent`, audit | assignment-ready event; thread/notification effects | retry replays same assignment; competing acceptance obeys cardinality exactly |
| `transitionGigAssignment` | Apply owner-local accepted-work transition. | authorized participant/system | approved assignment matrix + contextual external facts | assignment status/timestamps | authority, transition, concurrency, outbox | notifications; Order/Dispute consumers may react | stale transition conflict |
| `executeGigModerationDecision` | Apply an authorized moderation action to Gig-owned state. | signed internal Moderation instruction | validated case/action/target/version | only approved Gig fields/status/visibility | `executeModerationDecision`, idempotency, outbox | Search refresh | no local ModerationCase truth |
| `executeGigPrivacyInstruction` | Apply Privacy-directed disposition to Gig-owned data. | Privacy/system actor | approved target instruction + retention result | owner-local data only | `executePrivacyInstruction`, `evaluateRetentionRequirement`, anonymization primitive | Search deindex/detach effects | idempotent; retained/skipped explicit |

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

Policy-facing decisions should use the canonical decision envelope (`allowed`, `denied`, `warning`, `review_required`, `step_up_required`, `unavailable`) plus Gig-specific reason codes, source version, evaluated time, and safe evidence references.

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
| Identity & Access | `resolveAuthenticatedActor` | trusted actor | actor ID/type/security context | Yes | session/user helper |
| Role / Authority | `authorizeResourceAction` | authorization | action, resource, owner facts | Yes | generic permission engine |
| Customer / Buyer Profile | `resolveCustomerActor` | buyer-domain actor | active CustomerProfile ID + User link/status | Yes | CustomerProfile lifecycle |
| Taxonomy & Classification | `validateTaxonomyAssignment`, `resolveTaxonomyRequirements` | classification validity/triggers | canonical IDs, validity, requirement refs | Yes for publish/update as local policy requires | taxonomy rules |
| Professional Eligibility | `evaluateProfessionalReadiness` | Professional response/acceptance gate | action `respond_to_gig`/approved acceptance action, Professional, Gig context | Yes | raw readiness composition |
| Admin Review / Compliance Hold | `evaluateComplianceHold` | reusable stop sign | target/action + safe reasons | Yes | blocked flags |
| Media / File Access | ready-target validation, `attachValidatedMedia`, signed access where viewer needs media | safe attachments | MediaAsset ID/status/context/allowed actions | Yes for attachment/publication | file pipeline |
| Location Safety | `applyFuzzyPublicLocation` | public-safe location | approved fuzzy projection/version | Yes where public location is required | coordinate fuzzing |
| Messaging | `ensureContextThread` | conversation context | ThreadContextType, context ID, participants | No for core Gig write unless explicitly made synchronous | Thread lifecycle |
| Notification | `requestNotification` | user alerts | recipients/template key/safe variables | No for source commit | delivery providers/status |
| Search / Public Visibility | `requestSearchProjectionRefresh` | derived discovery | entity/action/reason/source version | No for source commit | SearchUpsertEvent/Typesense |
| Content Moderation | `executeModerationDecision` protocol | apply authoritative moderation result | case/action/target/source version | May restrict public behavior | moderation case truth |
| Privacy / Data Erasure | privacy instruction protocol | execute owner data disposition | target/disposition/idempotency/exemption ref | May restrict/delete/anonymize | PrivacyRequest workflow |
| Audit / Event Ledger | `appendAuditEvent` | generic significant-action proof | actor/action/target/outcome/safe metadata | Usually no; required audit failure policy follows root standard | generic audit storage |
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

The supplied Canonical Shared Operations Registry standardizes names but does **not** provide permanent `SH-###` identifiers. This document therefore does not invent IDs.

| Canonical operation | Owner / class | Why Gig / Demand uses it | Invocation point | Local policy that remains here | Expected result | Prohibited duplicate names |
| --- | --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Identity & Access; platform capability | trusted actor | every protected command | what Gig action is attempted | typed actor context | `requireGigUser`, `gigAuth`, `currentGigUser` |
| `authorizeResourceAction` | Role / Authority; cross-cutting capability | server-side permission | protected reads/writes | owner/response/assignment relationship facts | allow/deny decision | `gigPermissions`, `assignmentGuard`, local RBAC |
| `queryOwnerFacts` | each source Module; shared contract | expose minimal Gig ownership/context facts | Role/Media/Messaging consumers | Gig fact vocabulary | owner-fact DTO | cross-domain repository |
| `resolveCustomerActor` | Customer / Buyer Profile; Module public interface | buyer-domain identity | customer Gig commands | Gig requires eligible customer context | CustomerProfile ID/status/source version | `buyerResolver`, User-only buyer helper |
| `evaluateComplianceHold` | Admin Review / Compliance Hold | reusable action stop sign | publish, response acceptance, selected assignment transitions | which action/target a hold blocks | safe DecisionResult | local `blocked` flag/service |
| `returnDecisionResult` | shared contract; policy local | consistent decisions | all gate/query surfaces | Gig reason codes and policy | normalized decision envelope | ad hoc booleans |
| `evaluateProfessionalReadiness` | Professional Eligibility | response/acceptance gate | submit and accept | Gig supplies action/context only | DecisionResult + safe evidence refs | `professionalCanRespond`, raw verification composer |
| `resolveTaxonomyRequirements` | Taxonomy & Classification | requirement triggers | publish/update | whether trigger blocks Gig transition | typed requirements | hard-coded category risk map |
| `validateTaxonomyAssignment` | Taxonomy & Classification | canonical classification validation | create/update/publish | whether category/tags are mandatory | normalized IDs/errors | `gigCategoryValidator`, local tag cleaner |
| `evaluatePublicReadiness` | shared contract; source/compliance owners | public projection decision | publish/Search source build | Gig-local status/visibility rules | owner decision + version | Search reconstructing Gig policy |
| `applyFuzzyPublicLocation` | Location Safety | public-safe location | public projection | what location context Gig wants displayed | fuzzy projection/version | `gigLocationMask`, coordinate randomizer |
| `attachValidatedMedia` | contextual Module + Media truth | safe Gig attachment | media attach | role/sort/context semantics | validated join creation | `gigFileScanner`, direct Media writes |
| `issueSignedMediaUrl` | Media / File Access | temporary private media delivery | authorized Gig media read | contextual viewer entitlement facts | signed URL/access evidence | `gigPresignedUrl`, R2 client |
| `ensureContextThread` | Messaging; Module public interface | idempotent business-context conversation | after approved Gig/response/assignment point | context/participants | Thread ID | `gigChatService`, direct Thread insert |
| `appendAuditEvent` | Audit / Event Ledger | generic significant action proof | publish/cancel/accept/admin actions | safe Gig metadata | audit acknowledgement | `gigAuditLog` generic table |
| `createRequestContext` | platform/Observability | correlation/causation | request/job entry | safe domain IDs only | propagated context | custom correlation helper |
| `writeStructuredLog` | Observability / Ops | operational diagnostics | commands/workers | safe dimensions | log record | direct ad hoc logger stack |
| `sanitizeTelemetryMetadata` | Observability/Audit policy | prevent sensitive leakage | logging/audit/event metadata | Gig sensitivity classification | safe metadata | manual scattered redaction |
| `recordIntegrationFailure` | Observability / Ops | visible degraded dependency | failed Search/Notification/Order handoff etc. | business state remains unchanged | normalized failure | custom failure table |
| `requestNotification` | Notification | user alert | committed lifecycle events | event meaning + recipients | notification request | `gigEmailService`, `gigPush` |
| `executeIdempotentCommand` | platform application infrastructure | safe retries | create/respond/accept/transitions | semantic identity/conflict/replay | original result replay | `gigIdempotency`, custom dedupe table |
| `deduplicateDomainEvent` | platform event infrastructure | idempotent event consumers | inbound event handlers | handler-specific effect | inbox claim/result | ad hoc processed-event table |
| `publishDomainEvent` | platform outbox | reliable committed fact publication | same transaction/outbox as source write | event names/payload privacy | versioned event | fire-and-forget emitter |
| `enqueueReliableJob` | shared queue infrastructure | expiration/reconciliation | background work | job payload and business meaning | durable job ID | custom queue |
| `executeRetryWithBackoff` | shared queue/platform | retry transient effects | worker dependency calls | retryability classification | success/dead-letter | per-worker retry loop |
| `acquireAggregateLock` | shared persistence infrastructure | serialize response acceptance | acceptance/critical transition | lock key `gig:{gigId}` and conflicts | lock/transaction scope | in-memory mutex, bespoke lock table |
| `withOptimisticConcurrency` | shared persistence infrastructure | stale update protection | edits/non-locking transitions where approved | retry/merge policy | update/conflict | hand-rolled timestamp compare |
| `transitionLifecycleState` | shared mechanism/separate truth | state-machine plumbing | all lifecycle commands | exact Gig/Response/Assignment graph | validated transition | generic policy owning statuses |
| `runDeadlineExpiration` | shared scheduler/queue | process `closesAt` | expiration worker | which statuses expire | dispatched owner transition | `gigCron`, scheduler writing status directly |
| `requestSearchProjectionRefresh` | Search / Public Visibility | index/update/hide/remove | after committed public-source change | Gig source version/reason | accepted projection request | Typesense client, `SearchUpsertEvent` insert |
| `buildSourceProjection` | each source Module; shared pattern | safe Search input | Search query/rebuild | allowlisted Gig fields | source projection + version | Search raw Prisma access |
| `executePrivacyInstruction` | Privacy protocol; data owner executes | privacy disposition | Privacy target command | field-level Gig handling | normalized privacy result | `gigGdprWorkflow` |
| `enumerateSubjectData` | each data owner | privacy inventory | Privacy discovery | Gig-owned targets | cursorable target list | global DB crawler |
| `evaluateRetentionRequirement` | data owner facts + Privacy exemption record | retention determination input | before destructive action | Gig/Order-linked retention facts | required/reason/minimum fields | local retention-exemption table |
| `anonymizePersonalFields` | shared primitive; owner mapping | field-level anonymization | approved Privacy instruction | exact Gig field map | anonymization proof/result | global uncontrolled anonymizer |
| `executeModerationDecision` | Moderation decision; target owner executes | apply approved source effect | moderation event/command | allowed Gig-side effect | ack/completed/failed result | local moderation case |
| `validateOwnedTargetReference` | target owner | safe cross-Module target validation | context joins/commands | Gig relationship eligibility | typed target result | direct cross-domain Prisma read |

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

1. **Lifecycle plumbing:** `transitionLifecycleState` may be shared; Gig/Response/Assignment graphs remain Gig truth.
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

Every protected command begins with `resolveAuthenticatedActor`. Browser/client-provided User IDs are never trusted as actor proof.

### Authority

Use `authorizeResourceAction`. Gig / Demand supplies contextual facts such as:

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

No Gig-specific step-up requirement is confirmed. If root security policy later marks an admin/financial Gig-adjacent action as sensitive, Gig / Demand calls Identity & Access `requireStepUpForSensitiveAction`; it does not implement MFA locally.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying truth owner | Query | Gig action gated | Gig-local policy | Result |
| --- | --- | --- | --- | --- | --- |
| Customer actor | Customer / Buyer Profile | `resolveCustomerActor` | create/update/publish/accept | require eligible controlling customer | allow/deny |
| Taxonomy validity | Taxonomy & Classification | `validateTaxonomyAssignment` | create/update/publish | decide which classification fields are mandatory | valid/errors |
| Taxonomy requirements | Taxonomy & Classification | `resolveTaxonomyRequirements` | publish/response context | include trigger facts in readiness/public policy | requirement refs |
| Professional response readiness | Professional Eligibility | `evaluateProfessionalReadiness` | submit response | `respond_to_gig` action | DecisionResult |
| Acceptance readiness recheck | Professional Eligibility | same interface with approved action/context | accept response | fresh evaluation required at acceptance | DecisionResult |
| Compliance hold | Admin Review / Compliance Hold | `evaluateComplianceHold` | publish/accept/selected transitions | map applicable holds to denial | DecisionResult |
| Location safety | Location Safety | `applyFuzzyPublicLocation` | public projection | do not expose exact location | safe projection |
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

Every consumer uses `deduplicateDomainEvent`. Gig / Demand does not create ad hoc processed-event tables for ordinary internal domain events.

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

Generic queue mechanics, retries, leases, dead-letter state, and telemetry use `enqueueReliableJob`, `executeRetryWithBackoff`, and shared worker infrastructure.

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

Current schema does not enforce one assignment per Gig. Assignment cardinality is an architecture decision gate.

### Acceptance transaction

Once cardinality is approved, `acceptGigResponse` must:

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
- `issueSignedMediaUrl` is transport, not Gig entitlement truth.
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

After committed source changes that affect public discovery, call `requestSearchProjectionRefresh` with entity ID, action/reason, source version, requester Module, and idempotency key.

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

Use `requestNotification` with:

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

Use `appendAuditEvent` for significant actions such as:

- Gig publication/cancellation/admin correction;
- response acceptance;
- assignment cancellation or admin override;
- privacy/moderation execution where audit policy requires.

### Sensitive access

Ordinary Gig reads are not automatically sensitive-access events. Private/sensitive Media access is audited through Media/Audit rails. If future Gig fields become specially sensitive, use `recordSensitiveAccess` rather than creating a local access-log table.

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

- `createRequestContext`;
- `writeStructuredLog`;
- `sanitizeTelemetryMetadata`;
- `captureException` where platform wrapper applies;
- `emitMetric`;
- `recordIntegrationFailure`;
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

- `resolveCustomerActor` consumption;
- taxonomy validation/requirements;
- `evaluateProfessionalReadiness` response gate;
- ComplianceHold decision;
- Media attachment validation;
- Location Safety fuzzy projection;
- Search refresh request;
- Messaging `ensureContextThread`;
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
10. `posterUserId`/`buyerUserId` are not a substitute for CustomerProfile commercial truth once the migration ruling is accepted.
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
| Single-award vs multi-award Gig | Product flow says customer accepts one response; Prisma permits many assignments; CL-04 explicitly marks unresolved. | Blocks production acceptance/cardinality constraint. Proposed MVP: single-award. |
| Exact Gig transition matrix | Enum exists; no approved graph. | Blocks pause/reopen/assigned/completed automation beyond settled subset. |
| Exact GigResponse transition/edit rules | Enum and uniqueness exist; edit-window rules absent. | Blocks final `reviseGigResponse` state policy. |
| Exact GigAssignment transition semantics | Enum exists; `proposed` and `disputed` meaning unclear. | Blocks full assignment lifecycle. |
| CustomerProfile non-null migration | New architecture says CustomerProfile is buyer truth; schema remains optional. | Blocks destructive/non-null migration; new-write policy needs explicit approval. |
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

### Proposed Rulings requiring explicit acceptance

1. **Single-award MVP:** one accepted GigAssignment per Gig.
2. **Buyer actor migration:** new Gig/assignment writes require CustomerProfile; User IDs remain authentication/audit references during/after migration where useful.
3. **Acceptance concurrency:** use canonical aggregate lock on Gig plus idempotent command result.
4. **Transactional outbox:** all cross-Module Gig-domain effects publish through the canonical outbox.
5. **Assignment creation:** acceptance creates `GigAssignment.status=accepted` directly; `proposed` remains unsupported until a separate workflow is defined.
6. **Source interface:** Transaction / Order consumes `getGigAssignmentCheckoutSource` instead of reading Gig repositories.

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
