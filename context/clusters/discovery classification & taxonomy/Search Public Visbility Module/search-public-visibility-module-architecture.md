# Search / Public Visibility Architecture

> **Module ID:** `search_public_visibility`  
> **Canonical module name:** Search / Public Visibility Module  
> **Module type:** `capability`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-02 — Discovery, Classification & Visibility`  
> **Repository target:** `context/clusters/discovery classification & taxonomy/Search Public Visbility Module/search-public-visibility-module-architecture.md`\
> **Document status:** Implementation-grade Module architecture; governed by context-map.md authority by concern and current CL-02 coordination\
> **Audience:** coding agents, developers, reviewers, maintainers, security/privacy reviewers, search/integration reviewers  
> **Update rule:** update this file only when a binding ownership, contract, lifecycle, provider, privacy, projection, or security decision for this Module changes. Build progress must not silently redefine architecture.

## Evidence posture

This document reconciles the current Search / Public Visibility Module Architecture Extract, Deep Module Registry, Cluster Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Registry, root Workin Ants project/build context, and directly relevant dependency evidence.

The current evidence set confirms that Search owns the search-projection work record, search entity vocabulary, Typesense adapter, projection execution, reconciliation, and query surfaces. It also confirms that Search is **derived projection, not business source truth**.

Two evidence gaps materially affect implementation:

1. The current CL-02 architecture and build plan are linked above and supply collaboration/sequencing evidence under context-map.md.
2. The current Prisma `SearchUpsertEvent` is materially thinner than the confirmed canonical `SH-091 requestSearchProjectionRefresh` contract. The schema only stores `entityType`, `entityId`, optional `reason`, `processed`, `createdAt`, and `processedAt`; the canonical operation requires action/intent, source version, requester Module, and idempotency. The required reconciliation is recorded below as a **Proposed Ruling**, not treated as already implemented.

Evidence labels used below:

- **Confirmed** — directly supported by current registry/schema/glossary/shared-operation evidence.
- **Proposed Ruling** — a concrete implementation-grade resolution strongly supported by the evidence but requiring architecture acceptance before schema/API commitment.
- **Unresolved** — a real question that the evidence does not safely settle.

Current coordination: [Cluster architecture](<../discovery-classification-architecture.md>) and [Cluster build plan](<../discovery-classification-build-plan.md>). Locate supporting artifacts through [context-map.md](<../../../context-map.md>); authority follows concern, not location or age. Root architecture/build-plan files are currently unavailable and do not supply enforceable phases.

---

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `search_public_visibility` |
| Module name | Search / Public Visibility Module |
| Module type | `capability` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-02 — Discovery, Classification & Visibility` |
| Document status | Binding Module context subject to root/Cluster authority |
| Intended audience | Coding agents, developers, reviewers, security/privacy/search maintainers |
| Relationship to root architecture | Inherits global source-of-truth, authorization, privacy, audit, queue, observability, provider-adapter, and testing rules. Search-specific rules here narrow those decisions. |
| Relationship to Cluster architecture | Implements CL-02's projection/public-surface responsibility; Taxonomy owns accepted classification and AI Taxonomy owns proposals. Search must not absorb either. |
| Relationship to Cluster build plan | CL-02 Features 02–03 establish basic Search, 09 integrates public sources, 10 protected Candidate Search, 11 prerequisite/reaction slices, and 12–13 reconciliation/hardening. External owner contracts must exist before production integration. |
| Update rule | Change only for binding architecture changes; implementation progress belongs in progress tracking. |

---

## 2. Purpose, Goal, and Transformation

### Purpose

Maintain privacy-safe, policy-aware, rebuildable search projections for public discovery and explicitly authorized protected discovery.

### Goal

Keep Typesense synchronized with authoritative Workin Ants source truth while ensuring that private, blocked, erased, nonpublic, stale, or noncompliant entities do not become discoverable merely because a search document exists.

### What enters

Search accepts **approved inputs**, not raw ownership:

- a typed projection-refresh request identifying the entity and reason;
- an owner-issued source projection built from allowlisted public/protected fields;
- an owner-issued public/protected-readiness decision with a source version;
- accepted taxonomy identifiers and labels;
- approved fuzzy/public location supplied by Location Safety or included in the owner projection;
- trust-display/ranking signals supplied by Trust Verification / Screening;
- effective candidate-search boost entitlement supplied by Track Subscription & Entitlement;
- moderation enforcement instructions;
- Privacy-owned erasure/restriction instructions;
- ComplianceHold decisions where the search surface is hold-sensitive;
- authenticated actor and authority decisions for protected/admin search operations.

### What leaves

Search produces:

- `SearchUpsertEvent` work truth proving that projection work was requested;
- provider-facing search documents and removals;
- public discovery query results;
- protected candidate-search results when that later feature is enabled;
- search-specific reconciliation/backfill outcomes;
- privacy/moderation execution results for the orchestrating owner;
- safe operational telemetry and generic audit requests where required.

### Capability transformation

```text
source change / enforcement instruction
→ Search-owned projection request
→ owner-safe source projection + owner readiness decision
→ Search composes search-surface eligibility
→ build versioned provider document OR decide removal/no-op
→ write/delete through Typesense adapter
→ mark Search work outcome
→ public/protected query sees only permitted projection
```

### Why this is its own Module boundary

Search has a distinct lifecycle and failure domain from every indexed business object. A provider index may lag, fail, be rebuilt, or be deleted while the source entity remains valid business truth. Centralizing provider schema/versioning, de-index/re-index, reconciliation, privacy filtering, and query behavior prevents every business Module from creating its own Typesense client, ranking rules, retry worker, or visibility cache.

---

## 3. Owned Truth

### Confirmed owned schemas and enums

#### `SearchUpsertEvent`

Plain English: a Search-owned durable record telling the projection system that an entity's search representation must be reconsidered.

Current authoritative Prisma fields:

```text
id
entityType
entityId
reason?
processed
createdAt
processedAt?
```

Current database indexes:

```text
(entityType, entityId, createdAt)
(processed, createdAt)
```

It proves that search projection work was requested and, in the current schema, whether it was marked processed. It does **not** prove the business entity itself is valid, public, compliant, verified, or retained.

#### `SearchEntityType`

Current canonical vocabulary:

```text
user
professional_profile
candidate_profile
organization
offering
gig
job
taxonomy
trust_badge
```

Search owns interpretation of these values for collection routing and provider document identity. The enum does not transfer ownership of the referenced entities.

### Search-owned projection truth

Search owns the **provider representation** of approved source data:

- Typesense collection/document schema definitions;
- collection registry and routing policy;
- provider document identity policy;
- projection schema/version policy;
- query/facet/filter mapping;
- ranking behavior over entities that are already eligible;
- provider upsert/delete execution;
- backfill and reconciliation behavior.

These are Search-owned **derived projections**, not Workin Ants business source records.

### Search-owned policy and invariants

Search owns:

- the rule that only owner-approved fields enter a search document;
- the final composition from owner-issued readiness to `upsert`, `remove`, `exclude`, or `no-op` for a particular search surface;
- public-versus-protected collection/query separation;
- the rule that exact private location never enters public search;
- the rule that raw resumes/application documents never enter search;
- ranking and faceting behavior that cannot override eligibility;
- stale-source/projection-version protection;
- de-index/re-index and reconciliation behavior.

### Not confirmed as owned durable truth

No dedicated Search domain-event ledger, search-access ledger, provider-event dedupe record, projection-snapshot table, or search-result analytics table is confirmed. Do not create one merely for convenience.

---

## 4. Explicit Non-Ownership

| Adjacent owner | Truth that remains outside Search | Search may consume | Search must never duplicate |
| --- | --- | --- | --- |
| Marketplace Supply | `Offering` lifecycle, publication state, offering public fields | `buildSourceProjection`, `evaluatePublicReadiness`, source events | `OfferingStatus`, publication policy, local offering repository |
| Gig / Demand | `Gig` lifecycle/visibility | owner projection/readiness + change event | `GigStatus`, `GigVisibility`, gig publication logic |
| Organization Hiring | `Organization` and `Job` lifecycle/publication facts; organization membership | public-safe source projections, owner facts | Job/org lifecycle, organization-role truth |
| Job Compliance | job compliance findings/decision/proof | owner-issued compliance/readiness decision | local scanner, local compliance boolean, raw finding interpretation |
| Candidate Application & Resume Privacy | `CandidateProfile`, `CandidateSearchProjection`, candidate privacy, application/resume truth | active privacy-safe `CandidateSearchProjection`; candidate-search access facts | raw resume parsing/indexing, candidate privacy lifecycle, ATS behavior |
| Professional Eligibility | `ProfessionalProfile` lifecycle/readiness composition | professional public-readiness decision/projection | professional readiness rules |
| Taxonomy & Classification | accepted Domain/Category/Tag truth and normalization | accepted taxonomy IDs/labels, requirement triggers | taxonomy copies, tag cleaners, accepted classification mutation |
| AI Taxonomy | AI suggestion/run provenance | accepted result only after Taxonomy ownership transition | AI provider/prompt logic, direct AI-to-index publication |
| Trust Verification / Screening | `VerificationCheck`, requirements, credentials, `TrustBadge` truth | approved trust-display/ranking signal | verification status translation/readiness reconstruction |
| Healthcare / Regulated Services | healthcare-lane/data-boundary readiness | owner-issued readiness decision | healthcare policy/PHI logic |
| Location Safety | exact location, fuzzy location generation, location reveal | `applyFuzzyPublicLocation` result | coordinate fuzzing, exact-location decryption |
| Content Moderation & Legal Notice | Reports, LegalNotice, ModerationCase, ModerationAction decision truth | enforcement instruction | moderation decision workflow or legal-notice lifecycle |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob, targets, retention exemptions | privacy instruction | privacy request/job workflow or legal retention decision |
| Admin Review / Compliance Hold | ComplianceHold lifecycle | `evaluateComplianceHold` | local `isBlocked`/`searchBlocked` truth |
| Track Subscription & Entitlement | plan, grant, usage, boost truth | `resolveEntitlement`; conditional metering | local premium/boost booleans or counters |
| Identity & Access | actor/session/security truth | authenticated actor | local auth/session helper |
| Role / Authority | permission interpretation | resource/action authorization | local permission engine |
| Audit / Event Ledger | generic AuditEvent/AccessAuditLog | append/audit requests | generic search audit table |
| Observability / Ops | IntegrationFailure, SystemEvent, queue telemetry, incident truth | logging/failure/metrics operations | search-specific generic failure/incident system |
| Shared queue/event infrastructure | QueueJob, leases, retries, outbox/inbox mechanism | reliable job/event mechanics | independent queue runner/dead-letter framework |

### Critical candidate boundary

`CandidateSearchProjection` remains Candidate Application & Resume Privacy truth. Search may transform an **active, privacy-safe** Candidate-owned projection into a protected Typesense document. Search must never load raw resume text as an indexing fallback.

### Critical user boundary

`SearchEntityType.user` exists in Prisma, but root architecture says `User` is base account identity, not a public profile. **Until a public use case and safe projection contract are explicitly approved, `user` must be treated as non-indexable.** This is an unresolved vocabulary issue, not permission to publish accounts.

---

## 5. Module Architecture Principles

1. **Search is projection, never source truth.**
2. **Owner-approved projection in; provider document out.** Search does not reconstruct a public document by reading arbitrary foreign tables.
3. **Eligibility precedes ranking.** No badge, boost, score, or paid entitlement can make an otherwise ineligible record searchable.
4. **Public and protected discovery are distinct security surfaces.** Candidate search is not an extension of anonymous public search.
5. **Candidate search uses `CandidateSearchProjection` only.** Raw resume/application content is prohibited.
6. **Exact private location is prohibited in public provider documents.** Use Location Safety output.
7. **De-indexing is not deletion of source truth.** Search removes projection only; source owners remain authoritative.
8. **Moderation and Privacy instruct; Search executes.** Search does not decide legal/moderation/privacy entitlement.
9. **Search request truth is distinct from queue telemetry.** `SearchUpsertEvent` remains Search-owned; generic retries/leases/dead-letter mechanics remain shared infrastructure.
10. **Provider details stay behind a Search-owned adapter.** No direct Typesense client in source Modules.
11. **Source version beats arrival order.** An older refresh may not overwrite a newer source projection.
12. **Reconciliation is mandatory architecture, not an emergency script.** The external provider is expected to drift eventually.
13. **Source change delivery must be durable.** Prefer source-owned transactional domain events/outbox over best-effort cross-Module calls when a source mutation and search refresh cannot share an approved transaction.
14. **Search query contracts hide collection topology.** Consumers should not depend on provider collection names.
15. **No universal readiness engine inside Search.** Search composes owner decisions; it does not own professional, job, healthcare, verification, moderation, or hold policies.
16. **Provider errors are operational facts, not eligibility facts.** A provider outage must not mutate business entities to hidden/blocked.
17. **Fail closed for protected discovery.** Unknown candidate authority/privacy/entitlement state returns no protected result.
18. **Backfills cannot bypass current policy.** Rebuilds always re-evaluate current owner projection/readiness.

---

## 6. Proposed Folder / Code Structure

The exact repository prefix must follow the root Workin Ants code standards. The logical ownership shape is:

```text
server/
  modules/
    search-public-visibility/
      application/
        commands/
          request-search-projection-refresh.ts
          run-search-backfill.ts
          run-search-reconciliation.ts
        queries/
          search-public-discovery.ts
          search-candidates-for-organization.ts   # deferred until CL-06 dependency is ready
          inspect-search-projection.ts
        services/
          process-search-projection-work.ts
          compose-search-visibility.ts
          build-search-document.ts
          apply-ranking-signals.ts

      domain/
        policies/
          search-surface-policy.ts
          projection-version-policy.ts
          stale-work-policy.ts
        types/
          search-surface.ts
          search-projection-intent.ts             # if Proposed Ruling is approved
          search-projection-result.ts

      contracts/
        public/
          search-projection-refresh.contract.ts
          public-search.contract.ts
          protected-candidate-search.contract.ts  # deferred
          search-debug.contract.ts
        dependencies/
          source-projection.port.ts
          public-readiness.port.ts
          privacy-executor.contract.ts
          moderation-executor.contract.ts

      schemas/
        request-search-projection.schema.ts
        public-search.schema.ts
        candidate-search.schema.ts                # deferred
        admin-search.schema.ts

      repositories/
        search-upsert-event.repository.ts

      providers/
        search-provider.port.ts
        typesense/
          typesense-search-provider.ts
          collection-registry.ts
          document-schemas/
          error-translation.ts
          health-check.ts

      workers/
        search-projection.worker.ts
        search-backfill.worker.ts
        search-reconciliation.worker.ts

      privacy/
        execute-search-privacy-instruction.ts
        enumerate-search-subject-data.ts

      tests/
        unit/
        contract/
        integration/
        provider/
        privacy/
        e2e/
```

Optional module-specific admin UI may live under the repository's established admin route convention, but it must remain thin and call `inspectSearchProjection`, backfill, or reconciliation commands. Search does not own the generic admin shell.

### Folders intentionally not created

- no `media/` — Search does not own file mechanics;
- no `notifications/` — Search does not own delivery;
- no generic `auth/` or `permissions/` — use Identity/Role operations;
- no independent `queue/` — use shared queue infrastructure;
- no `events/` folder until a real Search domain event contract is approved;
- no `candidate/` repository that reads raw application/resume tables.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / public API | Parse search inputs, pagination/filter allowlists, safe result mapping | eligibility/compliance reconstruction, provider credentials in browser |
| Protected/admin delivery | actor/authority invocation, thin route/action orchestration | organization membership lifecycle, generic admin shell |
| Application commands | `requestSearchProjectionRefresh`, privacy/moderation execution, backfill/reconcile orchestration | direct mutation of source entities |
| Application queries | public discovery, protected candidate search, projection diagnostics | direct cross-domain repositories |
| Domain policy | search-surface composition, ranking after eligibility, stale-work rules | professional/job/privacy/moderation/healthcare truth |
| Repository/data access | `SearchUpsertEvent` only | Offering/Gig/Job/Profile/etc. repositories |
| Workers | Search-specific projection, backfill, reconciliation semantics | generic queue leases/retry/dead-letter engine |
| Provider adapter | Typesense collections, document schema/version, query/write/delete/error translation | business lifecycle/readiness truth |
| Dependency contracts | minimum source projection/readiness DTOs | universal repository over all source Modules |
| Privacy executor | delete/restrict Search-owned provider projection and report outcome | DataErasureJob lifecycle/retention exemption creation |
| Debug/admin | Search-specific projection diagnostics and commands | generic observability incident/failure dashboard |

---

## 8. Data Model

### 8.1 `SearchUpsertEvent`

**Purpose:** durable Search-owned work request for projection reconsideration.

**Key relationships:** polymorphic reference by `entityType + entityId`; no foreign key is currently possible across the heterogeneous entity set.

**Authoritative fields today:**

- `entityType` — Search-owned routing vocabulary;
- `entityId` — referenced source ID;
- `reason` — optional request context, not a policy decision;
- `processed` / `processedAt` — current coarse completion proof;
- `createdAt` — request ordering evidence.

**Lifecycle/status fields today:** `processed: Boolean` only.

**Uniqueness today:** no idempotency unique constraint exists.

**Concurrency-sensitive fields:** `processed`, `processedAt`; work for the same `entityType/entityId` may race because no source-version or unique command identity is stored.

**Retention/privacy concerns:** `entityType/entityId` can link to personal data. The event contains minimal metadata but may be subject to privacy inventory/retention analysis. It must not store raw source content, resumes, exact location, or provider payloads.

### 8.2 `SearchEntityType`

**Purpose:** closed vocabulary used to route projection requests and provider mapping.

**Important semantics:**

| Type | Source owner | Default surface posture |
| --- | --- | --- |
| `professional_profile` | Professional Eligibility / profile owner | public only after owner readiness |
| `candidate_profile` | Candidate Application & Resume Privacy | protected only; source is `CandidateSearchProjection` |
| `organization` | Organization Hiring | public when owner says eligible |
| `offering` | Marketplace Supply | public when owner says eligible |
| `gig` | Gig / Demand | public according to owner visibility/readiness |
| `job` | Organization Hiring + Job Compliance decision | public only after owner-issued publication/compliance readiness |
| `taxonomy` | Taxonomy & Classification | accepted taxonomy only |
| `trust_badge` | Trust Verification / Screening | display/ranking projection only; never verification truth |
| `user` | Identity & Access | **unresolved; default non-indexable** |

### 8.3 Typesense documents

Typesense documents are Search-owned external projections. They are rebuildable, versioned representations derived from owner-approved data. Provider document absence/presence must never be used to infer source lifecycle truth.

### 8.4 Referenced `CandidateSearchProjection`

Search does not own this model. Its current status vocabulary is:

```text
draft
active
hidden
erased
disabled
```

Search may index only the owner-approved projection state. `rawResumeTextIndexed` must never be used as permission to ingest raw resume text; the platform rule is to keep raw resume text out of Search.

### 8.5 Approved durable semantics and unresolved physical representation

**CL02-R008 — Approved semantic requirement:** Search owns durable SH-091 request identity/context, source version/currentness, idempotency, requester identity, action, claimability, successful completion, retry/operator failure, and stale/superseded outcomes. Shared queues own transport, attempts, backoff, and dead-letter mechanics; they are not the sole truth for Search currentness/outcome. The current `processed` Boolean is insufficient for the final production lifecycle.

**PR-SPV-01 — Physical design remains proposed:** expanding SearchUpsertEvent versus another Search-owned representation, exact fields/enums, and migration strategy require a separate database decision. No physical choice is approved by this reconciliation.

Illustrative field names only; not an approved additive schema:

```text
intent              # index | update | hide | remove | restore, or an approved equivalent
sourceVersion       # opaque owner-issued version
requesterModule     # canonical Module ID / system source
idempotencyKey      # unique semantic command identity
workStatus          # pending | processing | completed | failed | superseded, or approved equivalent
projectionVersion?  # Search document schema/version actually applied
outcome?            # upserted | removed | skipped | no_op, or approved equivalent
```

Generic attempt count, lease, heartbeat, next-attempt timestamp, and dead-letter truth should remain in shared queue/Observability infrastructure unless the canonical queue architecture explicitly requires a reference field here.

CL02-R008 approves those semantic requirements. It does not approve the illustrative field names, exact state graph, or an additive-only schema design.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Current confirmed work lifecycle

```text
processed=false
    |
    | worker successfully finishes work
    v
processed=true + processedAt
```

This is the only lifecycle currently represented by Prisma.

### 9.2 Target lifecycle — Proposed Ruling

CL02-R008 requires durable work outcomes, but the following exact state names/graph remain a proposal pending separate persistence/lifecycle detail approval:

```text
pending
  ├─> processing
  │     ├─> completed
  │     ├─> failed          # terminal Search projection failure
  │     └─> pending         # technical retry re-queued by shared runner
  └─> superseded            # a newer authoritative sourceVersion makes work obsolete
```

Rules:

- only the Search projection worker changes Search work status;
- shared queue machinery owns attempt/lease/dead-letter mechanics;
- `completed` may represent `upserted`, `removed`, `skipped`, or `no_op` outcome;
- `failed` is Search projection-work truth, not a business entity status;
- a failed projection must never mutate the source entity to hidden, invalid, or blocked;
- older `sourceVersion` work may be marked `superseded` rather than overwriting a newer document;
- replay of already-completed identical work returns the original completion result/no-op.

### 9.3 Provider projection lifecycle

```text
expected absent
  ↔ expected present at projection version/source version
```

Provider operations are idempotent:

- upsert same document/version → success/no-op;
- delete missing document → success/no-op;
- rebuild always rechecks source policy before creating a document.

### 9.4 Candidate projection lifecycle relationship

Search does not transition `CandidateSearchProjection`. It observes owner-approved state:

```text
CandidateSearchProjection.active
+ protected-search authority
+ any required entitlement
→ eligible to create protected provider projection

anything else
→ provider projection absent/removed
```

---

## 10. Commands

### `requestSearchProjectionRefresh` — **SH-091, Confirmed**

**Purpose:** controlled public command used by source Modules and enforcement workflows to ask Search to index, update, hide, remove, or restore a projection.

**Actor/context:** trusted internal caller; if user/admin initiated, resolve actor and authorize the initiating action before invoking Search. The browser must never directly create `SearchUpsertEvent`.

**Authoritative inputs:**

- `SearchEntityType`;
- entity ID;
- requested intent/action;
- reason code/reference;
- owner-issued source version;
- requester Module;
- idempotency key;
- request/correlation context.

**Preconditions:** supported entity type and intent; canonical requester identity; valid identifier; idempotency fingerprint; no malformed cross-surface request.

**State written:** Search-owned work record; queue job through shared mechanism.

**Shared operations:** SH-044 idempotency, SH-047 reliable job, SH-032 request context, SH-038 queue telemetry.

**Effects:** no direct source mutation; provider work occurs asynchronously unless a specifically approved synchronous enforcement path is required.

**Idempotency:** mandatory. Same semantic key/fingerprint replays accepted work/result; same key with a different fingerprint is conflict.

**Failure modes:** validation error, unsupported entity type, idempotency conflict, persistence failure, queue enqueue failure. Source business truth remains unchanged.

### `executePrivacyInstruction` — **SH-095 executor implementation, Confirmed protocol**

**Purpose:** execute a Privacy-owned instruction against Search-owned provider projections and Search-owned subject-linked metadata where applicable.

**Context:** Privacy provides target/job references and requested disposition.

**Preconditions:** valid Privacy executor contract; target belongs to Search scope; requested action is supported.

**State/effects:** remove/restrict provider docs; optionally queue de-index work; return execution evidence/result. Search does not change `DataErasureJob` itself.

**Idempotency:** deleting an already-absent document is successful/no-op.

**Failure modes:** target invalid, provider unavailable, retryable provider error, unsupported retention disposition.

### `executeModerationDecision` — **SH-103 target-owner executor, Confirmed protocol**

**Purpose:** apply a Moderation-owned hide/remove/restore instruction to Search projections.

**Preconditions:** verified moderation action/target reference through the shared protocol.

**State/effects:** create an idempotent Search refresh/removal request and return enforcement result. Search does not resolve the moderation case.

### `runSearchBackfill` — Module-local admin command

**Purpose:** intentionally rebuild selected Search projections from authoritative owner interfaces.

**Actor/context:** authenticated, authorized admin/support/system actor; step-up only if the root security policy designates the action sensitive.

**Inputs:** entity types, cursor/start point, dry-run flag, target projection version, bounded batch size.

**State/effects:** durable backfill jobs; Typesense writes/deletes; safe repair summary.

**Rules:** current policy must be re-evaluated; no direct bulk copy from foreign tables.

### `runSearchReconciliation` — Module-local admin/system command

**Purpose:** compare expected owner-approved projections with provider state and repair drift through **SH-093**.

**Inputs:** entity type/surface, cursor/checkpoint, dry-run, projection version.

**Rules:** orphan deletion must verify current Privacy/Moderation/public-readiness state before repair.

---

## 11. Queries / Decisions

### `searchPublicDiscovery`

**Consumers:** public discovery pages, public Offering/Gig/Job/Organization/Professional/taxonomy surfaces.

**Input:** query text, allowed public entity types, allowlisted filters/facets, fuzzy/public location filters, pagination, approved sort.

**Result:** normalized search result page whose items identify entity type/ID, display-safe projection fields, result score/ranking metadata only if safe, and pagination metadata.

**Meaning:** provider projection, not source truth.

**Consumer must not infer:** current business lifecycle, authoritative verification, exact location, payment/entitlement, or compliance truth from a hit alone.

### `searchCandidatesForOrganization` — **Proposed public query; deferred activation**

**Consumers:** authorized Organization Hiring experience.

**Input:** authenticated actor, organization context, candidate criteria, bounded filters/pagination.

**Result:** privacy-safe Candidate-owned projection fields only.

**Required gates:** SH-001 actor, SH-002 authority, Candidate owner privacy/access decision, Track entitlement if the feature is subscription-gated, and protected collection policy.

**Consumer must not infer:** resume content, JobApplication state, candidate suitability, hiring recommendation, or background-check truth.

This query belongs to CL-02 Feature 10 and remains disabled until CL-06 owner interfaces, the enforcement prerequisites, and the separately approved protected-search policy exist.

### `inspectSearchProjection`

**Consumers:** authorized admin/debug tooling, privacy/moderation verification, operators.

**Input:** entity type/ID, optional event ID.

**Result:** safe diagnostic view containing Search work status, source/projection versions, current provider presence/version, Search-level exclusion outcome, and references to owner decisions without exposing raw protected content.

**Meaning:** operational/projection evidence.

### `composeSearchVisibilityDecision` — internal decision

**Input:** search surface, owner-issued `evaluatePublicReadiness` result, source projection status/version, required safe location/trust/entitlement signals.

**Result:** `upsert`, `remove`, `exclude`, or `no-op` plus Search-level reason codes.

**Critical boundary:** it does not independently decide professional readiness, job compliance, candidate privacy, healthcare readiness, moderation, or hold status. It consumes those owner decisions.

---

## 12. Public Module Interface

### Public commands

- **SH-091 `requestSearchProjectionRefresh`** — canonical owner-facing projection command.
- **SH-095 `executePrivacyInstruction` implementation** — Search target executor under Privacy orchestration.
- **SH-103 `executeModerationDecision` implementation** — Search target executor under Moderation orchestration.
- `runSearchBackfill` — restricted Search admin/system command.
- `runSearchReconciliation` — restricted Search admin/system command.

### Public queries

- `searchPublicDiscovery` — public search API.
- `searchCandidatesForOrganization` — protected candidate search, deferred until CL-06 readiness.
- `inspectSearchProjection` — restricted admin/debug query.

### Public dependency contracts Search expects source owners to implement

- **SH-094 `buildSourceProjection`** — deterministic, versioned, allowlisted source projection.
- **SH-024 `evaluatePublicReadiness`** — owner-issued public/protected discovery decision with source version and evidence references.
- **SH-003 `queryOwnerFacts`** only when a protected search authority decision needs minimal relationship facts and no more specific confirmed interface exists; note SH-003 remains a Proposed Ruling.

### Emitted domain events

No Search-specific domain event is currently confirmed. Do not create `SearchProjectionUpdatedEvent` merely to mirror worker status. If a real consumer later requires a published fact, add it through SH-046 with an explicit event contract and architecture update.

### Provider-facing interface

**SH-092 `writeSearchProjection`** is the canonical Search provider boundary. Consumers never receive raw Typesense clients.

---

## 13. Inbound Dependencies

The preferred dependency shape is **owner projection + owner readiness**, not Search reading every underlying compliance table directly.

| Owning Module | Interface consumed | Why required | Minimum data | May block projection/query? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Marketplace Supply | SH-094 + SH-024 | Offering source and public readiness | ID, sourceVersion, allowlisted public fields, taxonomy refs, readiness | Yes | Offering lifecycle/publication |
| Gig / Demand | SH-094 + SH-024 | Gig source and visibility | ID, sourceVersion, public-safe gig fields, readiness | Yes | GigStatus/GigVisibility rules |
| Organization Hiring | SH-094 + SH-024; owner facts for candidate access | Organization/Job projections and protected org context | public-safe fields, versions, owner access facts | Yes | org/job/member lifecycle |
| Candidate Application & Resume Privacy | CandidateSearchProjection + SH-094/SH-024 | privacy-safe candidate discovery | active projection ID/version, allowlisted candidate metadata, privacy decision | Yes | resume/application/privacy truth |
| Professional Eligibility | SH-016 and/or owner SH-024 | professional public readiness | decision, reason codes, policy/source version | Yes | readiness composition |
| Job Compliance | SH-021 through source-owner composition where possible | ensure job public feed is compliant | decision/evidence version, not raw findings | Yes | scanner/rules/findings |
| Taxonomy & Classification | SH-022/023 or source projection taxonomy facts | accepted taxonomy/facets | canonical IDs/labels/active state | Yes if source owner says required | taxonomy copies/normalizers |
| Trust Verification / Screening | trust display signal / SH-018 only when needed | display/ranking input, not eligibility shortcut | safe active badge/signal + version | Possibly through source readiness | raw verification/provider status |
| Healthcare / Regulated Services | SH-020 through source owner where possible | regulated visibility boundary | decision + policy version | Yes | PHI/healthcare policy |
| Location Safety | SH-028 | public fuzzy location | approved fuzzy area/coordinates, source version | Yes if public location required | fuzzing/exact location |
| Content Moderation & Legal Notice | SH-103 | hide/remove/restore instruction | target/action/reference/version | Yes | case/legal decision lifecycle |
| Privacy / Data Erasure | SH-095/096 | remove/restrict/export Search-held subject data | target/action/job refs | Yes | privacy orchestration/retention truth |
| Admin Review / Compliance Hold | SH-011 | honor stop signs affecting discovery | hold decision/reason/reference | Yes | local blocked flags |
| Track Subscription & Entitlement | SH-005; SH-006 only if metered semantics are approved | candidate boost/protected feature entitlement | effective entitlement value, version/evidence | For protected feature; ranking only for boost | premium/boost booleans/counters |
| Identity & Access | SH-001 | protected/admin query actor | trusted actor context | Yes | auth/session infrastructure |
| Role / Authority | SH-002 | protected/admin authorization | allow/deny + evidence | Yes | local permission engine |
| Audit / Event Ledger | SH-029/030 | important admin/sensitive access proof | minimized target/action/outcome | No to provider projection itself; may be required to complete admin action | generic audit/access tables |
| Observability / Ops | SH-032–039 | safe tracing, metrics, failures, health | identifiers, operation, safe diagnostics | No business gate; operationally may abort request | failure/incident/queue telemetry system |
| Shared queue infrastructure | SH-047/048/051/052 | durable worker, retry, concurrency | work ID, idempotency, lease/lock/version | Technical | local queue/retry framework |

### Dependency minimization rule

A Search worker should not load `JobComplianceCheck`, `VerificationCheck`, `ComplianceHold`, `TrackEntitlementGrant`, and healthcare records independently if the source owner can return the necessary public-readiness decision. Direct dependency is justified only when the canonical public interface assigns that decision to the external owner and the source owner does not compose it.

---

## 14. Outbound Consumers and Effects

### Consumers of Search query surfaces

- public discovery UI;
- public Offering discovery;
- public Gig discovery;
- public Job discovery;
- public Organization discovery;
- public ProfessionalProfile discovery;
- accepted taxonomy discovery;
- approved trust-badge display where appropriate;
- protected Organization candidate search after CL-06 integration;
- admin/debug tooling.

### Consumers of Search execution results

- Privacy / Data Erasure receives target execution results;
- Content Moderation & Legal Notice receives enforcement results;
- Observability / Ops receives failures/queue/health telemetry;
- Audit / Event Ledger receives manual/admin action proof where required.

### Outbound effects

Search may:

- write/delete provider documents through SH-092;
- enqueue Search-specific work through SH-047;
- record operational failures through SH-037;
- append audit proof through SH-029;
- record sensitive access through SH-030 when the protected/admin surface qualifies;
- return execution acknowledgment to Privacy/Moderation.

Search must not directly mutate another Module's source tables.

---

## 15. Canonical Shared Operations Used

Only operations materially relevant to this Module are listed.

| ID / operation | Classification / owner | Why Search uses it | Invocation point | Search-local policy | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | Platform capability — Identity & Access | protected candidate/admin search | protected entry point | which Search action is being attempted | trusted actor context | `searchAuth.ts`, `getCurrentSearchUser` |
| **SH-002 `authorizeResourceAction`** | Cross-cutting — Role / Authority | authorize org candidate search/admin operations | after actor resolution | Search action/resource vocabulary and owner facts | allow/deny/review | `searchPermissions.ts`, org-role checks in Search |
| **SH-003 `queryOwnerFacts`** | Shared contract, Proposed Ruling — source owner | minimum relationship facts if no stronger interface exists | protected org/admin decision | facts needed for Search action only | owner DTO | universal cross-domain Search repository |
| **SH-005 `resolveEntitlement`** | Commercial-policy capability — Track | candidate boost / protected search entitlement | before applying boost or gated query | how an effective value changes ranking/query access | typed entitlement decision | `isPremiumCandidate`, `searchBoostService` truth |
| **SH-006 `consumeMeteredEntitlement`** | Cross-cutting — Track | only if approved Search usage is genuinely metered | exact business event after feature use | what event counts | immutable usage receipt | local usage counter/Event writer |
| **SH-011 `evaluateComplianceHold`** | Cross-cutting — Hold owner | honor discovery-affecting holds | projection composition where owner contract requires it | map hold to remove/exclude | hold decision | `searchBlocked` flag |
| **SH-015 `returnDecisionResult`** | Shared contract, Proposed Ruling | normalized decision envelope | dependency/composition contracts | Search-specific reason codes only | allow/deny/warning/review envelope | one universal policy engine |
| **SH-024 `evaluatePublicReadiness`** | Shared contract; policy stays with source/compliance owner | decide whether source may appear on a surface | before any upsert/rebuild | compose owner decisions into projection outcome | decision + reason/evidence/source version | local professional/job/candidate readiness recreation |
| **SH-028 `applyFuzzyPublicLocation`** | Location Safety public interface | prevent exact location leakage | source projection/document build | how approved fuzzy fields are filtered/faceted | safe fuzzy location + version | `searchLocationFuzzer.ts` |
| **SH-029 `appendAuditEvent`** | Audit platform capability | manual reindex/deindex/backfill/debug actions as policy requires | admin operation completion | which Search admin actions merit generic audit | AuditEvent reference | `SearchAuditLog` generic table |
| **SH-030 `recordSensitiveAccess`** | Audit cross-cutting | protected candidate/admin data access where designated sensitive | after allowed protected access/denial | sensitivity classification remains source/Search-surface policy | AccessAuditLog reference | local sensitive access table |
| **SH-032 `createRequestContext`** | Platform primitive — Observability | correlation across request/job/provider | every entry/job | safe Search identifiers | request/correlation context | local correlation helper |
| **SH-033 `writeStructuredLog`** | Observability capability | operational diagnostics | commands/queries/workers/provider | safe Search dimensions | structured log | ad hoc logger/client |
| **SH-034 `sanitizeTelemetryMetadata`** | Cross-cutting — Ops/Audit policy | prevent resumes, exact locations, secrets, PII leaking to logs | before telemetry/audit metadata | Search field allowlist | sanitized metadata | custom redaction utility |
| **SH-035 `captureException`** | Observability adapter | capture unexpected Search failures | error boundary/worker/provider | Search operation tags | exception reference | local monitoring client |
| **SH-036 `emitMetric`** | Observability capability | query latency, queue depth, projection lag/failure | query/worker health paths | low-cardinality Search dimensions | metric | direct metrics provider client |
| **SH-037 `recordIntegrationFailure`** | Observability capability | persist Typesense/source-integration failures | provider/worker terminal or significant failure | Search supplies event/entity/collection references | IntegrationFailure | `typesense_errors` table |
| **SH-038 `recordQueueTelemetry`** | Queue/Ops capability | worker attempt/heartbeat/duration/dead letter telemetry | shared worker runner | Search work ID + safe operation | queue telemetry | attempt fields copied as generic queue truth |
| **SH-039 `checkServiceHealth`** | Ops coordinates; Search supplies check | provider/readiness health | health/admin ops | Search provider health semantics | healthy/degraded/unavailable | bespoke health framework |
| **SH-044 `executeIdempotentCommand`** | Platform primitive | prevent duplicate refresh/admin commands | command boundary | semantic key/fingerprint/replay | prior/new result | local idempotency table/helper |
| **SH-047 `enqueueReliableJob`** | Queue primitive | durable projection/backfill/reconcile work | after Search work persistence | payload/completion meaning remains Search-owned | queued work ID | `searchQueue.ts` framework |
| **SH-048 `executeRetryWithBackoff`** | Queue primitive | retry transient provider/source failures | worker wrapper | transient/permanent error classification | retry/terminal result | `typesenseRetry.ts` |
| **SH-051 `acquireAggregateLock`** / **SH-052 `withOptimisticConcurrency`** | Persistence primitives | prevent same-entity races/stale overwrites when needed | worker claim/write | lock key/source-version semantics | safe exclusive/versioned operation | in-memory mutex |
| **SH-091 `requestSearchProjectionRefresh`** | **Search Module public interface** | canonical refresh/deindex request | source/enforcement integration | entity routing, intent mapping, Search work semantics | accepted/replayed Search work | `enqueueProjectionWork`, `deindexEntity` |
| **SH-092 `writeSearchProjection`** | **Search provider adapter** | one Typesense write/delete/query provider boundary | worker/query adapter | collection schemas/ranking/identity | normalized provider result | Typesense clients in source Modules |
| **SH-093 `reconcileSearchProjection`** | **Search internal worker** | detect and repair provider drift | admin/scheduled worker | staleness/orphan/projection-version rules | repair report | per-source Typesense reconciler |
| **SH-094 `buildSourceProjection`** | Source-owned pattern | obtain privacy-safe indexable source data | worker/backfill | Search validates envelope, not source semantics | versioned allowlisted projection | Search building raw source projection itself |
| **SH-095 `executePrivacyInstruction`** | Privacy protocol; Search executes its target | privacy deindex/restrict/delete-provider work | Privacy target execution | Search provider/queue effect only | typed target result | local PrivacyRequest/DataErasureJob workflow |
| **SH-096 `enumerateSubjectData`** | Privacy protocol; each data owner | identify Search-held subject-linked work/provider refs | privacy inventory/export | Search-owned record/provider mapping | paged subject-data inventory | privacy crawler over all tables |
| **SH-103 `executeModerationDecision`** | Moderation protocol; target owner executes | enforce hide/remove/restore | Moderation action | map instruction to Search refresh/removal | typed enforcement result | moderation case logic in Search |

### Shared-operation naming rule

Aliases such as `enqueueSearchProjection`, `enqueueProjectionUpdate`, `enqueueProjectionWork`, `requestSearchProjectionUpdate`, `enqueueSearchProjectionChange`, and `deindexEntity` must not become parallel public services. The canonical interface is **SH-091**.

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `composeSearchVisibilityDecision` | map owner decisions to Search surface action | surface + readiness + source version | upsert/remove/exclude/no-op | none | Search owns final provider projection decision, not source policy |
| `resolveSearchCollection` | route entity/surface to provider collection/schema version | entityType + surface | collection descriptor | none | Search provider topology is Search-owned |
| `buildSearchProjectionDocument` (Search-local SH-115 projection behavior) | transform approved source projection into provider document | SH-094 result + approved signals | versioned provider document | none | provider representation belongs to Search |
| `processSearchProjectionWork` | execute one Search work item | Search work ID | terminal/retry/no-op result | `SearchUpsertEvent` | core Search work lifecycle |
| `applySearchRankingSignals` | attach approved nonauthoritative ranking metadata | eligible document + trust/entitlement signals | ranked document fields | provider document only | Search owns ranking behavior after eligibility |
| `classifySearchProviderError` (local SH-061 mapping) | map provider error to safe retry/permanent category | provider error | normalized Search error | none | adapter-specific translation remains Search-owned |
| `buildReconciliationExpectation` | compute expected provider identity/version from source contracts | source projection/readiness | expected doc descriptor | none | reconciliation semantics are Search-owned |
| `inspectProjectionState` | combine Search work + provider presence/version into debug result | entity/event | diagnostic DTO | none | Search-specific ops surface |

---

## 17. Shared Mechanism / Separate Truth Rules

| Shared mechanism | Shared component | Search truth that remains separate | Rule |
| --- | --- | --- | --- |
| Reliable queue | SH-047/048 + QueueJob/telemetry | `SearchUpsertEvent` projection-work meaning | QueueJob never replaces Search work outcome. |
| Idempotency | SH-044 | Search semantic request identity | Search defines fingerprint and replay semantics. |
| Locking/concurrency | SH-051/052 | entity/source-version ordering | No in-memory lock. |
| Decision envelope | SH-015 if approved | each owner’s readiness rules | Search can compose but not centralize policy. |
| Source projection pattern | SH-094 | each source Module's allowed public/protected data | `CandidateSearchProjection` remains Candidate-owned. |
| Audit | SH-029/030 | Search work/projection state | Audit is generic proof, not Search queue truth. |
| Observability | SH-032–039 | Search business/projection outcome | IntegrationFailure/metrics do not become index eligibility. |
| Privacy protocol | SH-095/096 | Search-owned provider/work records | Privacy owns request/job/target lifecycle. |
| Moderation protocol | SH-103 | Search enforcement effect | Moderation owns decision/case lifecycle. |
| Provider adapter pattern | SH-092 | Search collection/document/ranking policy | One Typesense adapter; source Modules never get client access. |

---

## 18. Authentication and Authorization

### Public search

Anonymous public discovery may be allowed by product design. Anonymous access does not mean unrestricted query construction:

- validate query/filter/sort/pagination server-side or through an approved scoped search-key mechanism;
- limit entity types to approved public surfaces;
- never expose protected candidate collections;
- never accept arbitrary collection names or raw provider filter expressions from the browser.

### Protected candidate search

Required chain:

```text
SH-001 resolveAuthenticatedActor
→ owner facts for organization context
→ SH-002 authorizeResourceAction(search_candidates, organization)
→ Candidate owner privacy/search readiness
→ SH-005 resolveEntitlement if the feature/boost is plan-gated
→ protected Search query
→ SH-030 recordSensitiveAccess only if policy classifies the access as sensitive
```

Search must not infer OrganizationMember authority from client claims.

### Admin/debug operations

`inspectSearchProjection`, manual reindex/deindex, backfill, reconciliation, and provider-debug operations require server-side authorization. Admin status never implies unrestricted access to raw candidate/resume/private source data.

### System/internal callers

SH-091 may be invoked by authenticated system/module context. The requester Module identifier is evidence for routing/audit, not a substitute for trust. Internal service credentials and request context must be resolved by canonical infrastructure.

### Step-up

No Search-specific step-up action is currently confirmed. If the root security matrix designates destructive bulk deindex, protected candidate export-like access, or collection rebuild as sensitive, use SH-014. Search must not invent its own MFA challenge.

---

## 19. Compliance / Readiness / Entitlement Gates

Search's gate composition is intentionally narrow.

| Gate | Underlying truth owner | Query/contract | Search action gated | Local composition result |
| --- | --- | --- | --- | --- |
| Source public/protected readiness | source/compliance owner | SH-024 | all upserts/backfills | deny → absent/remove; allow → continue |
| Professional readiness | Professional Eligibility | SH-016, usually composed into SH-024 | Professional/Offering projection | cannot be recreated from profile fields |
| Job compliance | Job Compliance | SH-021, preferably source-owner composed | Job projection | block/review as owner decision requires |
| Healthcare readiness | Healthcare | SH-020, preferably source-owner composed | regulated entity projection | blocked/redacted decisions honored |
| Verification | Trust Verification | SH-018 or source-owner composition | eligibility/display/ranking as declared | no raw provider/badge inference |
| Moderation | Content Moderation | SH-103 | upsert/remove/restore | enforcement instruction wins over stale projection |
| Privacy | Privacy/Data Erasure + candidate owner | SH-095/024 | all affected docs | restrict/remove and prevent rebuild |
| ComplianceHold | Hold owner | SH-011 | hold-sensitive discovery | remove/exclude while applicable |
| Fuzzy location | Location Safety | SH-028 | public document fields | exact location prohibited |
| Search boost entitlement | Track | SH-005 | ranking metadata only | can reorder eligible candidate, never confer eligibility |
| Candidate protected access | Candidate owner + Role + Track where required | owner privacy decision + SH-002/005 | protected query | fail closed on missing gate |

### Ordering rule

```text
source exists
→ owner projection is valid
→ owner readiness allows surface
→ privacy/moderation/hold constraints allow surface
→ safe location/field minimization
→ THEN trust/entitlement ranking signals
```

A ranking signal is never evaluated as an eligibility override.

---

## 20. Provider Integrations

### Provider owned here

Typesense is the confirmed Search provider.

### Provider-neutral port

**SH-092 `writeSearchProjection`** defines the provider boundary. The port should support the operations Search actually needs:

- ensure/inspect collection schema version;
- upsert one document;
- batch upsert;
- delete one document;
- batch delete where safe;
- execute public/protected query through normalized input;
- fetch document metadata for debug/reconciliation;
- health check;
- normalize errors.

Do not expose raw Typesense SDK types from the Module public API.

### Adapter

The `typesense` adapter owns:

- client construction;
- endpoint/credential handling;
- collection name/alias translation;
- document schema installation/version checks;
- provider filter/sort/query syntax;
- provider error translation;
- batch limits/provider-specific retry hints.

### Credentials

Credentials are server-side secrets. They must never be stored in `SearchUpsertEvent`, logs, client bundles, or public result payloads.

### Webhooks

No Typesense webhook workflow is confirmed. Do not implement webhook verification/dedupe tables for Search unless a provider feature later requires callbacks.

### Provider-event dedupe

Not applicable today. Search work idempotency is driven by Workin Ants `SearchUpsertEvent`, source version, and shared command/job idempotency.

### Status/error translation — SH-061 `translateProviderStatus`

Translate provider errors into stable Search/operational categories such as:

- unavailable/transient;
- timeout/transient;
- schema incompatibility/manual intervention;
- invalid document/permanent until source/mapping changes;
- authorization/configuration/manual intervention;
- not found/delete no-op.

Raw provider error bodies do not cross public interfaces.

### Reconciliation

SH-115 `buildAggregateProjection` identifies Search-owned versioned projection/rebuild behavior; inclusion/ranking and owner-safe input policy remain local. SH-093 is mandatory for drift repair. It must support dry run, cursor/checkpoint, projection version, stale/missing/orphan detection, and privacy/moderation verification before repair.

### Retry and idempotency

Use SH-047/048. Do not implement `typesenseRetry.ts` as an independent retry framework.

### Retention requirements — SH-097 `evaluateRetentionRequirement`

Search supplies retention facts for its owned work/provider references through SH-097 when required; Privacy records exemptions. Return the approved reason/basis, retain-until, minimum fields, permitted anonymization, and source reference. This does not approve retention policy or a field-level anonymization mapping. No generic SH-098 dependency is introduced.

### Privacy deletion

Search executes provider document removal as part of SH-095. A successful provider deletion is not proof that source data was erased.

### Operational failure reporting

Use SH-037 with Search work ID, entity type/ID, collection descriptor, provider operation, retryability, request/correlation ID, and sanitized diagnostics.

---

## 21. Events and Outbox

### `SearchUpsertEvent` is not a generic domain event

It is Search-owned projection-work truth. It must not be merged with `AuditEvent`, `SystemEvent`, or generic QueueJob.

### How source changes should reach Search

Preferred durable pattern when source mutation and Search work cannot share an approved transaction:

```text
source Module authoritative transaction
→ SH-046 publishDomainEvent through transactional outbox
→ Search consumer uses SH-045 dedupe
→ SH-091 requestSearchProjectionRefresh
→ Search work record + SH-047 queue
```

For explicit admin/privacy/moderation commands, the owning workflow may call the Search public interface directly with an idempotency key and correlation reference.

### Search-emitted events

No Search-specific outbound domain event is confirmed. Operational telemetry is sufficient for the initial implementation. If another Module later needs a fact such as “projection removed,” define a minimized versioned event instead of publishing raw provider responses.

### Payload minimization

Source events and Search work payloads should contain IDs, versions, action/reason codes, and safe references—not full source records, raw resumes, exact addresses, private messages, or provider credentials.

---

## 22. Background Jobs / Scheduled Work

### Projection worker

**Purpose:** process one Search-owned work item.

**Input:** Search work ID; worker reloads current work and source contracts.

**Owner:** Search / Public Visibility.

**Idempotency key:** Search work semantic key plus source version; provider document identity/version.

**Retryable failures:** provider timeout/unavailable, transient source-interface outage, queue infrastructure failures.

**Permanent/manual failures:** invalid provider schema mapping, unsupported entity type, malformed source projection, credential/configuration failure after retry classification, unresolved collection version mismatch.

**Dead-letter/manual review:** shared queue marks terminal work visible; Search work records terminal failure; SH-037 records integration failure. Ops owns generic queue dashboard.

**Business truth updated:** Search work outcome only; never source entity.

### Backfill worker

**Purpose:** rebuild selected entity types/surfaces from authoritative source contracts.

**Input:** entity type, cursor/checkpoint, projection version, dry-run, bounded batch.

**Idempotency:** deterministic source version + projection version/document ID.

**Failure behavior:** batch must checkpoint; a single bad entity must not silently stop all remaining work unless policy requires fail-fast.

### Reconciliation worker

**Purpose:** SH-093 provider drift detection/repair.

**Input:** surface/entity type, cursor/checkpoint, dry run, target projection version.

**Schedule:** **Unresolved.** Implement a callable durable worker first; root/ops architecture decides recurring cadence.

### Entitlement/trust/moderation/privacy reactions

Do not create separate Search queues per signal. Every signal funnels into SH-091 and the same Search work lifecycle.

---

## 23. Concurrency and Idempotency

### Races to prevent

1. Two source changes for the same entity arrive out of order.
2. A hide/remove event races with an older update.
3. A privacy erasure races with backfill/reconciliation.
4. Two workers claim the same Search work.
5. A provider write succeeds but the worker crashes before completion is recorded.
6. An idempotent command is retried with a different payload.
7. Collection schema migration runs while ordinary writes use incompatible document shapes.

### Resource/aggregate key

Primary concurrency scope:

```text
search:{surface}:{entityType}:{entityId}
```

Use SH-051/052 or the approved database/queue equivalent. Do not use in-memory locks.

### Source version

The owner supplies an opaque, comparable or equality-checkable source version. Search must not manufacture a version from provider arrival time. If owner versions are not totally ordered, the source contract must expose a way to tell whether the requested snapshot is current before provider write.

### Idempotency semantics

- SH-091 requires an idempotency key and request fingerprint.
- same key + same fingerprint → replay accepted/original result;
- same key + different fingerprint → conflict;
- delete already-absent provider doc → successful no-op;
- upsert same source/projection version → successful no-op;
- stale work → superseded/no-op, never overwrite newer projection.

### Transaction boundary

At minimum, creation/claim of Search-owned work and its Search-state transition must be atomic within Search's own transaction. Queue dispatch uses the canonical reliable job mechanism. Cross-Module source writes should not be wrapped in an ad hoc Search transaction unless root architecture explicitly approves shared transactional participation.

### Crash after provider success

Replay must be safe. On retry, the worker checks source/projection version and provider state, re-upserts idempotently if needed, then records completion. Provider success is not assumed merely because the prior attempt started.

---

## 24. Media / Storage

Search does not own MediaAsset, upload, validation, malware scanning, metadata scrub, buckets, signed URLs, or private-file access.

A source projection may contain an already-approved **public display asset reference/URL** only if the source owner and Media/publication workflow guarantee it is safe for public exposure. Search must not:

- generate signed Media URLs;
- index private attachment URLs;
- index original filenames containing personal data;
- inspect raw media to decide visibility;
- cache private file access credentials in Typesense.

Candidate resume files are never search-document inputs.

---

## 25. Search / Projection

This section states the core source/projection split explicitly.

| Search entity | Source truth | Source projection owner | Search projection | Search must not reconstruct |
| --- | --- | --- | --- | --- |
| Offering | Marketplace Supply | Marketplace Supply | public Typesense document | publication/readiness |
| Gig | Gig / Demand | Gig / Demand | public Typesense document | Gig visibility/lifecycle |
| Job | Organization Hiring, with Job Compliance truth | source owner under SH-094/024 | public Typesense document | compliance findings/decision |
| Organization | Organization Hiring | Organization Hiring | public Typesense document | membership/verification workflow |
| Professional profile | Professional Eligibility/profile owner | source owner | public Typesense document | professional readiness |
| Candidate | Candidate App & Resume Privacy | **CandidateSearchProjection** | protected Typesense document | raw resume/application/privacy lifecycle |
| Taxonomy | Taxonomy & Classification | Taxonomy | public taxonomy document/facet | AI suggestion acceptance |
| Trust badge | Trust Verification | Trust owner | display/ranking projection | VerificationCheck truth |
| User | Identity & Access | **Unresolved** | none by default | public account profile from User fields |

### Indexing triggers

Search refresh must react to the source changes that affect the approved projection or readiness, including:

- source lifecycle/public visibility changes;
- accepted taxonomy changes;
- professional/job/healthcare/verification readiness changes when they affect public readiness;
- candidate projection/privacy changes;
- moderation actions;
- privacy restrictions/erasure;
- ComplianceHold changes that affect discoverability;
- fuzzy public location changes;
- trust-display changes;
- candidate boost entitlement activation/expiration/revocation.

Source Modules trigger SH-091 or publish a domain event consumed by Search. Search does not poll foreign tables as its primary change-detection mechanism.

---

## 26. Notification

Search owns no user-facing notification lifecycle and no email/SMS/push provider.

Default policy:

- projection success/failure is operational telemetry, not an end-user notification;
- if product later requires a notice such as “your profile is no longer discoverable,” the source/business owner should normally own the message meaning and call Notification;
- Search may request an operator notification only if an approved Ops workflow uses SH-041, but generic provider alerts should remain Observability/Ops-owned.

Do not create `SearchEmailService`, `SearchSmsService`, or provider templates inside Search.

---

## 27. Audit and Sensitive Access

### Search domain/work proof

`SearchUpsertEvent` proves Search projection work. It is not a generic audit event.

### Generic audit

Use SH-029 for important admin/system actions where platform policy requires proof, especially:

- manual reindex/deindex;
- bulk backfill/rebuild;
- manual reconciliation repair;
- provider schema/collection migration;
- privileged projection inspection when policy designates it auditable.

### Sensitive access

Public search does not create sensitive-access logs per hit.

For protected candidate search and debug tools, SH-030 is conditional on the platform's sensitivity classification. Candidate resume viewing already has separate Candidate-owned proof; Search must not create a duplicate resume access ledger.

### Operational telemetry

Provider/worker failures go to Observability/Ops, not Audit, unless there is a separate actor/compliance action requiring Audit proof.

---

## 28. Privacy and Retention

### Subject-data inventory

Search may hold subject-linked data in:

- `SearchUpsertEvent.entityType/entityId` and minimized `reason` metadata;
- Typesense documents for public/protected profiles/entities;
- Search-specific backfill/reconciliation checkpoints or diagnostics if they contain subject references.

Search must not store raw resumes, private application documents, exact locations, or unnecessary PII in queue payloads/logs.

### Privacy executor

Implement SH-095 for Search:

- locate relevant public/protected provider documents by stable identity;
- remove/restrict them idempotently;
- prevent backfill/reconciliation from immediately restoring a Privacy-denied source;
- return success, skipped/already absent, retryable failure, terminal failure, or retained/unsupported result according to the shared protocol;
- record provider failure operationally without taking ownership of Privacy workflow state.

### Subject-data enumeration

Implement SH-096 so Privacy can discover Search-owned subject-linked records/provider references without crawling Search internals.

### Retention

**Unresolved:** whether and how long `SearchUpsertEvent` rows referencing an erased subject are retained, anonymized, or deleted. Privacy owns the retention/exemption orchestration; Search supplies facts. Until settled, do not store additional personal content in the event merely to aid debugging.

### Export

If Privacy export requires search projection information, Search contributes a safe representation of its own records/provider state through the Privacy-defined serializer. It does not export foreign source records.

---

## 29. Observability

### Structured logs

Every command/query/worker/provider operation should carry SH-032 request/correlation context and log via SH-033.

Safe dimensions include:

- Search entity type;
- search surface (`public`, protected candidate, admin/debug);
- operation (`refresh`, `upsert`, `delete`, `query`, `backfill`, `reconcile`);
- collection registry key, not secret endpoint;
- projection schema version;
- outcome/retryability;
- queue/work ID;
- correlation/request ID.

Avoid high-cardinality user-entered query text in routine metrics/logs. Do not log raw resume text, exact location, provider API keys, private source JSON, or unredacted candidate data.

### Metrics

At minimum instrument:

- projection work queue depth/age;
- projection lag from `createdAt` to completion;
- successful upserts/removals/no-ops;
- retry/terminal-failure rate;
- provider latency/error rate;
- public/protected query latency and error rate;
- reconciliation drift counts;
- backfill throughput;
- collection schema-version mismatch count.

### Health

Search supplies a provider health check to SH-039. Health degradation must not mutate source entities.

### Failures

Use SH-037 with safe diagnostics. IntegrationFailure/SystemEvent records do not replace Search work state.

---

## 30. Security Boundaries

1. Validate every public/protected/admin input at runtime; TypeScript types alone are not a trust boundary.
2. Never accept raw provider collection names, filter expressions, sort syntax, or API keys from client input.
3. Use allowlisted entity types, filters, facets, and sorts per search surface.
4. Exact private coordinates/address fields are forbidden in public documents.
5. Raw resumes/application documents and raw resume text are forbidden in Search documents and telemetry.
6. Protected candidate search is server-authorized and collection-separated from anonymous public discovery.
7. Provider credentials remain server-side secrets.
8. Search work `reason`/metadata is minimized and schema-validated; do not dump source payloads into JSON/text fields.
9. Backfill/reconciliation/admin commands require server-side authorization and bounded scope.
10. Use platform rate limiting/abuse controls for public search; exact quotas remain a root/platform decision.
11. Query result snippets/highlights must be generated only from allowlisted search fields.
12. A provider document must never expose a field just because the source table has it.
13. Candidate entitlement/boost signals should be categorical/bounded values; avoid exposing subscription internals in public results.
14. Search provider errors are sanitized before crossing public boundaries.

---

## 31. Error / Decision Result Pattern

Public Module interfaces return stable Workin Ants results, never raw Typesense/Prisma errors.

### Command/result categories

Recommended stable categories:

```text
ok
validation_error
unauthenticated
forbidden
not_found
idempotency_conflict
stale_source_version
surface_not_supported
source_not_indexable
dependency_unavailable
provider_unavailable
retry_scheduled
terminal_failure
```

### Search composition reason codes

Search-level reasons may include:

```text
SOURCE_NOT_FOUND
SOURCE_PROJECTION_INACTIVE
PUBLIC_READINESS_DENIED
PROTECTED_SURFACE_FORBIDDEN
PRIVACY_RESTRICTED
MODERATION_RESTRICTED
COMPLIANCE_HOLD_ACTIVE
SAFE_LOCATION_UNAVAILABLE
STALE_SOURCE_VERSION
PROJECTION_SCHEMA_MISMATCH
PROVIDER_UNAVAILABLE
```

Owner-specific reason codes should be preserved as referenced evidence rather than translated into fake Search-owned policy.

### Provider errors

Raw provider message/stack/body is operational-only, sanitized, and never returned to public callers.

---

## 32. Testing Architecture

### Domain unit tests

- visibility composition honors owner decisions and ranking-after-eligibility ordering;
- candidate raw resume fields are impossible to map;
- exact location is rejected/omitted from public documents;
- stale source versions cannot overwrite newer projections;
- entity/surface routing is deterministic;
- SearchEntityType `user` is denied until explicitly enabled.

### State-transition tests

- current `processed=false → true` semantics until schema upgrade;
- target work lifecycle if PR-SPV-01 is adopted;
- failure/retry/superseded behavior;
- repeated completion is idempotent.

### Public contract tests

- SH-091 request validation/idempotency;
- source SH-094 envelope versioning;
- SH-024 decision composition;
- SH-095 privacy target result;
- SH-103 moderation target result;
- public search normalized result envelope;
- protected candidate query contract when enabled.

### Database/integration tests

- SearchUpsertEvent indexes/unique idempotency constraint after migration;
- atomic command/work creation;
- concurrency for same entity/source version;
- crash/replay behavior;
- migration from current boolean lifecycle if upgraded.

### Authorization tests

- anonymous public query allows only public surface;
- candidate/admin queries deny without actor/authority;
- system/module refresh caller cannot spoof requester identity;
- admin cannot bypass candidate privacy.

### Compliance/privacy tests

- moderation hide removes projection and restore re-evaluates readiness;
- privacy erase removes provider doc and prevents reconciliation resurrection;
- exact location never appears;
- job owner denial prevents indexing;
- inactive/hidden/erased CandidateSearchProjection never appears;
- raw resume text fixture causes hard test failure if mapper tries to include it.

### Provider adapter tests

Use a fake adapter for deterministic application tests and adapter-focused integration tests for:

- schema install/version mismatch;
- upsert/delete/no-op;
- query/filter mapping;
- provider timeout/unavailable/error translation;
- batch behavior;
- health check.

### Idempotency/concurrency tests

- same key/same fingerprint replay;
- same key/different fingerprint conflict;
- out-of-order update/hide;
- privacy remove races backfill;
- two worker claims;
- older source version cannot restore hidden/erased projection.

### E2E participation tests

- published eligible Offering → searchable;
- source becomes nonpublic/moderated → disappears;
- public Job only appears after owner compliance readiness;
- fuzzy location shown, exact location absent;
- Track boost reorders only already-eligible candidate results when protected candidate search is eventually enabled.

---

## 33. Module Invariants — Rules Coding Agents Must Never Violate

1. Search is never the authoritative source for an indexed business entity.
2. `SearchUpsertEvent` belongs to Search, not Audit or Observability.
3. Source Modules must use SH-091 or a durable event leading to SH-091; they must not write `SearchUpsertEvent` directly.
4. Source Modules must never instantiate a Typesense client.
5. Search must consume SH-094 owner projections instead of reconstructing public data from arbitrary foreign tables.
6. Search must consume SH-024 owner readiness decisions instead of rebuilding domain/compliance policy.
7. A ranking signal must never grant index eligibility.
8. A paid/boost entitlement must never make a private, erased, blocked, or noncompliant entity visible.
9. `CandidateSearchProjection` remains Candidate-owned.
10. Raw resumes, application documents, and raw resume text must never enter Search provider documents.
11. Protected candidate search must never be exposed through the anonymous public collection/query surface.
12. Exact private location must never enter public Search documents.
13. Search must not perform its own coordinate fuzzing.
14. TrustBadge may be projected; VerificationCheck remains verification truth.
15. Search must not infer verification readiness from a badge.
16. Search must not own Job compliance decisions or findings.
17. Search must not own moderation decisions/cases/notices.
18. Search must not own PrivacyRequest/DataErasureJob/retention-exemption workflow.
19. De-indexing is not source deletion or legal erasure.
20. Search must honor privacy/moderation/hold changes during backfill and reconciliation; rebuild cannot resurrect forbidden data.
21. Provider state/absence is never used to change source business status.
22. Generic queue retry/dead-letter/telemetry remains shared infrastructure; do not duplicate it inside Search.
23. Generic AuditEvent, AccessAuditLog, IntegrationFailure, SystemEvent, and OpsIncident remain external shared truths.
24. Search admin authority is server-side; frontend flags/route visibility are not authorization.
25. Same-entity concurrent work must be version/lock safe; no in-memory mutex is sufficient.
26. The current `user` SearchEntityType is non-indexable until a safe public contract is explicitly ruled in.
27. AI taxonomy suggestions cannot become search truth until Taxonomy accepts them.
28. Candidate boost usage/metering semantics must not be invented by Search; Track owns usage truth.
29. Provider credentials and raw errors never cross public interfaces.
30. Search result fields are allowlisted per surface; source-table availability is not permission to index.

---

## 34. Prohibited Duplicate Implementations

Do not create inside this Module:

- `searchAuth.ts`, `currentSearchUser.ts`, or feature-local session resolution;
- `searchPermissions.ts`, `orgCandidateSearchRoleCheck.ts`, or local role engine;
- `isPremiumCandidate`, `candidateBoostBoolean`, local quota/usage counters;
- `searchComplianceChecker`, `searchJobCompliance`, `searchProfessionalReadiness`;
- `searchLocationFuzzer`, coordinate jitter, exact-location decrypt helpers;
- verification provider/status translators or background-check interpretation;
- candidate resume parser/indexer or raw resume text pipeline;
- privacy request/job/target workflow tables/services;
- moderation case/legal-notice workflow services;
- local generic `SearchAuditLog`, `SearchIntegrationFailure`, `SearchQueueJob`, or `SearchOpsIncident` tables;
- independent retry/dead-letter/lease framework;
- per-entity Typesense clients such as `offeringTypesense.ts`, `jobTypesense.ts`, `candidateTypesense.ts`;
- source-specific Search queues;
- direct repositories for Offering, Gig, Job, Organization, ProfessionalProfile, CandidateProfile, CandidateSearchProjection, Taxonomy, VerificationCheck, ComplianceHold, or TrackEntitlementGrant merely for indexing convenience;
- public permanent URLs or signed file access generation;
- AI suggestion acceptance logic;
- a universal `isSearchable()` helper that silently reimplements every owner policy.

---

## 35. Unresolved Decisions

The following must be settled explicitly rather than guessed during coding:

1. **Search work physical representation:** separately decide whether to expand SearchUpsertEvent or use another Search-owned representation, plus fields/enums/migration satisfying CL02-R008. The existing Boolean is not the final production lifecycle.
2. **Collection topology:** one multi-entity public collection versus per-entity collections/aliases, and exact schema migration strategy.
3. **Protected candidate collection topology:** exact collection/key/query isolation and whether query is always server-mediated.
4. **`SearchEntityType.user`:** remove/deprecate, reserve internally, or define a safe public use case. Default remains non-indexable.
5. **Projection source version shape:** monotonic number, timestamp/version string, content hash, or owner-specific opaque value with currentness query.
6. **Search ranking weights:** only basic MVP ranking is in scope; exact trust/recency/taxonomy/boost weights are not established.
7. **Candidate search boost semantics:** exact Track entitlement key/value, whether boost is simply effective metadata or also metered usage, and when `candidate_search_boost_applied` is recorded.
8. **Organization candidate-search entitlement owner:** the shared-operations unresolved register notes organization commercial entitlement ownership is not fully confirmed. Protected candidate search activation must wait for this decision if org plans are required.
9. **Sensitive-access logging for candidate search:** whether every protected candidate result/query requires SH-030, or only specific detail/access operations.
10. **SearchUpsertEvent privacy retention:** retain, anonymize, or erase subject-linked event metadata after privacy fulfillment.
11. **Reconciliation cadence:** manual/admin only at first versus scheduled frequency.
12. **Public Search API transport:** server route/server component versus approved scoped client-side Typesense key for anonymous public search.
13. **Search-specific outbound events:** no consumer currently proves a need; do not invent until required.
14. **CL-02 dedicated architecture/build-plan alignment:** revalidate this Module when those current artifacts are available.

---

## 36. Architecture Decision Summary

Binding rulings for implementation:

- Search / Public Visibility is the canonical owner of `SearchUpsertEvent`, `SearchEntityType`, Typesense integration, projection execution, reconciliation/backfill, and search query surfaces.
- Search is rebuildable projection only. It does not become Offering, Gig, Job, Organization, Professional, Candidate, Taxonomy, Trust, Privacy, Moderation, Location, Compliance, or Entitlement truth.
- Source Modules provide deterministic, versioned, allowlisted source projections through SH-094 and public/protected readiness through SH-024.
- The only canonical cross-Module refresh command is SH-091 `requestSearchProjectionRefresh`.
- The only canonical Search provider boundary is SH-092 `writeSearchProjection`.
- Search uses one provider adapter/collection registry; no source Module calls Typesense.
- Public search and protected candidate search are different security surfaces.
- Candidate search uses Candidate-owned `CandidateSearchProjection` only and never indexes raw resumes or raw resume text.
- Public Search uses Location Safety-approved fuzzy location and never exact private location.
- Ranking signals apply only after eligibility. TrustBadge/entitlement boosts cannot confer eligibility.
- Privacy and Moderation own decisions/orchestration; Search implements their target-executor effects through SH-095/SH-103.
- Generic queue, idempotency, audit, sensitive-access logging, failures, metrics, and incident management are reused shared mechanisms.
- The current `SearchUpsertEvent.processed` boolean is insufficient for the confirmed canonical refresh contract; CL02-R008 approves durable semantic requirements; production persistence still requires the separate PR-SPV-01 physical design decision.
- `SearchEntityType.user` is fail-closed/non-indexable until explicitly ruled otherwise.
- CL-02 Features 02–03 establish basic public Search. Protected Candidate Search waits for Feature 10 owner/enforcement dependencies and cannot be enabled merely because Typesense exists.

---

## 37. Coding-Agent Usage

Before implementing any numbered feature in this Module, the coding agent must read, in order:

1. `context/project-overview-v3.md` (orientation; see context map);
2. context-map.md notes root architecture is unavailable; use the applicable existing concern owner;
3. repository instructions; referenced code standards are unavailable in context-map.md;
4. `context/shared/shared-operations.md` / Canonical Shared Operations Registry;
5. current CL-02 architecture, if present;
6. current CL-02 build plan, if present;
7. current linked CL-02 build plan and the target feature's actual external prerequisites;
8. this `module-architecture.md`;
9. this Module's `implementation-plan.md`;
10. public-interface sections for direct dependencies used by the feature;
11. current Prisma schema and migrations for `SearchUpsertEvent`, `SearchEntityType`, and any referenced integration contract;
12. current progress tracker.

The agent must then:

- confirm the prior feature exit gate;
- identify any unresolved decision touched by the feature;
- write the required feature implementation specification;
- implement only that feature;
- run contract/unit/integration/security/privacy/provider checks appropriate to the slice;
- update progress and only change architecture when a binding decision actually changes;
- never treat a convenient direct Prisma read or local helper as permission to bypass Module ownership.
