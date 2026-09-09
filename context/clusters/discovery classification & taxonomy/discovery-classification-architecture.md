# Discovery, Classification & Visibility Architecture

> **Cluster ID:** `CL-02`  
> **Cluster name:** Discovery, Classification & Visibility  
> **Cluster type:** `discovery_taxonomy_projection`  
> **Repository target:** `context/clusters/discovery-classification-visibility/architecture.md`  
> **Document status:** Target Cluster architecture for the Workin Ants MVP, grounded in the current Project Overview, Deep Module Registry, Cluster Registry v2.3, Prisma schema, Ubiquitous Language / Compliance Inventory, all three CL-02 Module Architecture Extracts, and the Canonical Shared Operations Registry  
> **Audience:** coding agents, developers, reviewers, maintainers, search/relevance reviewers, privacy reviewers, compliance reviewers, and architecture reviewers  
> **Update rule:** update this file whenever a binding CL-02 ownership, classification, AI, projection, privacy, ranking, provider, lifecycle, or cross-Cluster decision changes. Build progress must not silently redefine this architecture.

This document coordinates the three Deep Modules in CL-02. It does **not** make the Cluster a source-of-truth owner and does **not** transfer any Module lifecycle into a Cluster-level service.

Evidence labels used in this document:

- **Confirmed** — directly supported by the current registry, Prisma schema, glossary/compliance evidence, canonical shared-operation rulings, or repeated Module evidence.
- **Proposed Ruling** — an implementation-grade decision strongly supported by the evidence but not yet cleanly settled across all authoritative sources.
- **Unresolved** — the evidence establishes a real question, conflict, or missing contract and does not support a safe final answer.

---

## 1. Document Status and Scope

CL-02 is the controlled context that connects three different concerns without collapsing them:

```text
Taxonomy & Classification
    owns accepted vocabulary and classification semantics

AI Taxonomy
    owns AI-generated proposal/run truth

Search / Public Visibility
    owns derived discovery projection and search-provider execution
```

The Cluster contains:

1. `taxonomy_classification` — Taxonomy & Classification Module
2. `ai_taxonomy` — AI Taxonomy Module
3. `search_public_visibility` — Search / Public Visibility Module

The Cluster answers a narrow platform question:

```text
How is a platform object classified?
→ if AI helped, what exactly did AI propose and with what provenance?
→ what accepted source truth is allowed to appear in discovery?
→ how is that approved truth projected into search without becoming source truth?
```

This architecture is subordinate to the root Workin Ants architecture. If this file conflicts with a confirmed root ruling, the root ruling controls unless it is explicitly changed.

The Prisma schema remains executable schema evidence. This file explains semantic ownership, lifecycle meaning, projection boundaries, provider boundaries, and collaboration rules that Prisma alone cannot express.

Module-specific architecture remains authoritative for Module-local behavior. This Cluster document coordinates interfaces and sequencing only.

### Evidence conflicts preserved by this document

The current evidence contains several real gaps that must not be hidden:

- the Deep Module Registry broadly assigns taxonomy joins to Taxonomy & Classification, while entity Modules and the glossary claim or imply ownership of some join lifecycles;
- `AiSuggestion` and `AiClassificationLog` are canonical AI Taxonomy truth in the registry/glossary but are absent from the supplied Prisma schema;
- the AI suggestion disposition/acceptance lifecycle is not modeled;
- the exact semantics of `verified` and `confidence` on tag joins are unresolved;
- Taxonomy registry claims for tag-level healthcare/location triggers exceed the current Prisma fields;
- `DataSensitivity` is used across multiple domains without a confirmed evolution owner;
- `SearchUpsertEvent` is intentionally minimal and does not itself express every projection failure/retry state;
- public/protected Typesense collection boundaries and ranking details are not fully specified;
- candidate discovery depends on Candidate-owned privacy projection plus organization authority and Track entitlement, none of which Search may recreate.

These items appear again in **Deferred / Unresolved Decisions** and are explicit implementation gates where necessary.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

Maintain one accepted platform classification vocabulary, produce traceable AI-assisted classification proposals without promoting AI output directly to truth, and project eligible source records into privacy-safe public or explicitly protected discovery surfaces.

### Goal

Allow Workin Ants to answer, for any discoverable object:

```text
What canonical Domain / Category / Tags describe it?
Who or what proposed or attached that classification?
Which compliance or readiness requirements are triggered by that accepted classification?
Is the source object currently allowed on this discovery surface?
Which source-owned facts may be exposed?
What derived search document should exist right now?
```

without allowing Search, AI, or a consuming feature Module to invent classification, readiness, privacy, moderation, location, entitlement, or verification truth.

### What enters CL-02

Typical inputs include:

- approved taxonomy seed definitions;
- administrator taxonomy changes;
- raw user/professional/organization classification wording;
- entity-owner requests to validate a Domain/Category/Tag assignment;
- source-owner snapshots approved for classification;
- active taxonomy vocabulary supplied to AI Taxonomy;
- authorized AI classification requests;
- owner-approved, minimized candidate/profile/job/offering text or structured signals;
- AI model output and provider metadata through the AI provider adapter;
- source lifecycle or visibility changes;
- accepted classification changes;
- Professional Eligibility readiness decisions;
- Job Compliance decisions;
- Trust Verification public signals;
- Healthcare public-readiness decisions when applicable;
- Content Moderation decisions;
- ComplianceHold decisions;
- Privacy erasure/restriction instructions;
- Location Safety fuzzy public-location projections;
- Track entitlement/boost decisions and change events;
- Candidate-owned `CandidateSearchProjection` records for protected candidate discovery;
- search refresh requests from any source owner through the Search public interface.

### What leaves CL-02

CL-02 Modules expose source-owned or derived results such as:

- canonical `TaxonomyDomain`, `TaxonomyCategory`, and `TaxonomyTag` records;
- canonical taxonomy validation and requirement-trigger decisions;
- AI classification-run evidence and suggestion records once the missing AI schema is approved;
- suggestion review candidates and disposition acknowledgements;
- accepted classification references and provenance, with join ownership preserved according to the approved join ruling;
- `SearchUpsertEvent` projection-refresh work truth;
- Typesense or equivalent provider documents derived from approved source truth;
- public discovery query results;
- protected candidate-discovery results where the caller is authorized and entitled;
- confirmed de-index/re-index effects;
- admin/search-debug visibility into indexed, excluded, stale, or failed projection states;
- audit and operational side effects through canonical shared infrastructure.

### Major business/capability transformation

```text
raw or changing platform object
→ canonical taxonomy validation
→ accepted classification truth
→ source/compliance owner public-readiness decisions
→ owner-safe projection data
→ Search-owned provider projection
→ discoverable result

optional AI lane:
owner-approved classification input
→ AI model invocation
→ validated AI proposal/run truth
→ human/domain acceptance by Taxonomy workflow
→ accepted classification truth
→ Search refresh
```

### What CL-02 explicitly does not own

CL-02 does not become source truth for:

- `User`, `CustomerProfile`, `ProfessionalProfile`, `CandidateProfile`, or `Organization` lifecycles;
- Offering, Gig, Job, JobApplication, Order, Booking, Review, Dispute, or interview lifecycles;
- professional selling eligibility;
- Job compliance findings/decision truth;
- verification requirements/check results or license/background-check outcomes;
- healthcare readiness, BAA state, PHI/data-boundary policy, or redaction truth;
- moderation case/action lifecycle;
- `ComplianceHold` lifecycle;
- privacy request/job/retention-exemption lifecycle;
- exact-location reveal or geolocation precision policy;
- Track plan, entitlement, usage, or boost truth;
- generic audit or sensitive-access ledgers;
- generic queue/worker operational truth;
- private resume/application data;
- media/file access mechanics;
- notification delivery;
- provider payloads as Workin Ants domain truth.

---

## 3. Module Inventory

| Module ID | Module name | Module type | Purpose | Owned truth | Primary responsibility in CL-02 | Major inbound dependencies | Major outbound consumers |
|---|---|---|---|---|---|---|---|
| `taxonomy_classification` | Taxonomy & Classification | `capability` | Maintain controlled Domain/Category/Tag vocabulary and accepted classification semantics | `TaxonomyDomain`, `TaxonomyCategory`, `TaxonomyTag`, `TagSource`, hierarchy, normalization policy, term activation, classification validity, classification-trigger interpretation; taxonomy-join lifecycle ownership remains partly unresolved | Define what classifications mean and whether a proposed assignment is canonical/valid | Identity/Role for administration; entity owners; AI Taxonomy; Trust Verification; Healthcare; Search | Search; Marketplace Supply; Gig / Demand; Organization Hiring; Candidate Application; Professional Eligibility; Healthcare; Trust Verification; AI Taxonomy |
| `ai_taxonomy` | AI Taxonomy | `capability` | Produce structured, validated, traceable AI taxonomy/skill suggestions without converting them directly into accepted truth | Conceptually `AiSuggestion` and `AiClassificationLog`; prompt/model version semantics; AI suggestion confidence/provenance; classification-run outcomes | Generate proposals and preserve model-run evidence | Taxonomy vocabulary; source-owner classification snapshots; privacy/healthcare data-boundary decisions; Role/Authority; provider adapter; Ops | Taxonomy; Marketplace Supply; Organization Hiring; Candidate Application; Admin Review; potentially Search diagnostics only after acceptance |
| `search_public_visibility` | Search / Public Visibility | `capability` | Maintain rebuildable, privacy-safe public/protected discovery projections | `SearchUpsertEvent`, `SearchEntityType`, provider document schemas, Typesense adapter behavior, projection execution, de-index/re-index/backfill/debug behavior, public/protected query behavior | Turn owner-approved source truth into search-provider state and discovery results | Source entity owners; Taxonomy; Professional Eligibility; Job Compliance; Candidate Privacy; Trust; Healthcare where applicable; Location Safety; Moderation; Privacy; Holds; Track; Identity/Role; Ops | Public discovery; protected organization candidate search; business surfaces; moderation/privacy workflows; admin/debug |

### Module-boundary clarification

The most important distinction in this Cluster is:

```text
AI proposal truth != accepted taxonomy truth != search projection truth
```

A single object may therefore have three related but non-interchangeable records:

```text
AiSuggestion
    proves what a model proposed

Taxonomy join / accepted classification
    proves what the platform accepted for the entity

Search provider document
    is a rebuildable projection of what may currently be discovered
```

No one of those records may be treated as a substitute for the others.

---

## 4. Cluster Architecture Principles

1. **One owner per lifecycle.** No CL-02 workflow may update another Module’s lifecycle directly merely because the records are used together.
2. **Search is projection.** Typesense documents and query results are never business source truth.
3. **AI suggests; Taxonomy accepts.** Model output never directly creates official taxonomy truth or search visibility.
4. **Accepted taxonomy is controlled vocabulary.** Domain, Category, Tag hierarchy and normalization stay centralized in Taxonomy & Classification.
5. **Classification trigger is not compliance completion.** Taxonomy may state that a classification triggers verification, healthcare, location, license, or sensitivity requirements; the relevant compliance owner determines satisfaction.
6. **Tag provenance is not verification.** `TagSource.ai` proves provenance only. It does not mean the tag is correct, accepted, verified, compliant, or safe.
7. **TrustBadge is display, not verification truth.** Search may consume an approved public TrustBadge signal but must not reconstruct verification from badge presence.
8. **Ranking cannot confer eligibility.** Search boost, relevance, trust signals, or featured state may affect ordering only after public/protected readiness is already satisfied.
9. **Entitlement is not stored locally.** Search consumes Track entitlement/boost truth; no `isPremium`, local boost authorization, or duplicated entitlement table is permitted.
10. **Candidate discovery is protected and privacy-owned upstream.** Search consumes `CandidateSearchProjection`; it does not parse resumes, store raw resume text, or become an ATS.
11. **Location is fuzzy by owner decision.** Public search uses Location Safety-approved fuzzy output only; Search never exposes exact private coordinates.
12. **Moderation decides; Search executes.** Search de-indexes/restores in response to authoritative moderation decisions and never owns the legal/moderation case.
13. **Privacy orchestrates; Search and AI execute against their own data.** CL-02 Modules do not create a parallel PrivacyRequest workflow.
14. **ComplianceHold is the reusable stop sign.** CL-02 consumes hold decisions where applicable; it must not create a competing generic blocked-state system.
15. **Provider payloads are not domain types.** AWS Bedrock/AI responses and Typesense documents stay behind Module-owned adapters.
16. **Provider availability does not define domain state.** An unavailable model or search engine is an operational failure; accepted taxonomy and source records remain authoritative.
17. **Audit and observability stay distinct.** Admin action proof belongs in Audit; provider/queue failures belong in Observability; neither replaces Taxonomy, AI, or Search source records.
18. **Search must be rebuildable without AI.** Reindexing reads accepted source truth. Search may not invoke the model as part of projection reconstruction.
19. **Cross-Module cycles are interface-only.** AI may read Taxonomy and Taxonomy may decide AI suggestions, but no mutual direct repositories or recursive synchronous writes are allowed.
20. **No universal entity repository.** Source entities expose minimum public projection/classification contracts; CL-02 does not gain direct write access to all business tables.
21. **Unresolved semantics fail closed.** If a candidate/public/search/AI use depends on an unresolved privacy or ownership question, the behavior remains disabled or review-only.
22. **Canonical shared operations are reused.** Similar mechanics inside Taxonomy, AI, and Search do not justify local copies of authorization, idempotency, queue, outbox, redaction, privacy, audit, or telemetry infrastructure.

---

## 5. Runtime / Collaboration Topology

### Core request topology

```text
Browser / API / Worker / Domain Event
        │
        ▼
Owning Module public entry point
        │
        ├── SH-001 resolveAuthenticatedActor       when protected
        ├── SH-002 authorizeResourceAction         when protected
        ├── owner-specific validation / policy
        ├── owner repositories only
        └── canonical shared operations
                │
                ├── idempotency / concurrency
                ├── Audit / Observability
                ├── transactional outbox
                └── reliable jobs
```

Cross-Module reads occur through public interfaces or owner-safe projection DTOs, not by importing foreign repositories.

### Taxonomy administration

```text
Authorized administrator
→ Taxonomy application service
→ validate hierarchy / normalization / policy fields
→ Taxonomy-owned transaction
→ TaxonomyDomain / TaxonomyCategory / TaxonomyTag
→ audit event
→ domain event / affected-entity refresh requests
→ Search requestSearchProjectionRefresh
```

### AI suggestion generation

```text
Source Module or authorized admin
→ AI Taxonomy requestClassificationSuggestions
→ source owner supplies approved classification snapshot
→ Taxonomy supplies active vocabulary / canonical IDs
→ privacy / healthcare boundary applied if needed
→ SH-078 minimizeAndRedactProviderInput
→ SH-065 model-provider port
→ AWS Bedrock adapter
→ SH-066 structured-output validation
→ AI-owned run + suggestion records
→ review/query surface
```

No accepted taxonomy write occurs in this generation flow.

### AI suggestion acceptance

The target interaction is:

```text
Authorized reviewer
→ Taxonomy acceptance workflow
→ fetch AI-owned suggestion through AI public query
→ validate current taxonomy and target context
→ accepted taxonomy / attachment mutation by the approved lifecycle owner
→ Taxonomy decision is committed
→ AI receives disposition acknowledgement through public command/event
→ Search receives SH-091 projection refresh only after accepted truth exists
```

The exact attachment owner and suggestion-disposition transaction protocol remain architecture-gated by `U-CL02-01`, `U-CL02-04`, and `U-CL02-05`.

### Search projection

```text
Source change / taxonomy change / moderation / privacy / entitlement change
→ SH-091 requestSearchProjectionRefresh
→ SearchUpsertEvent
→ SH-047 reliable Search worker
→ source owner SH-094 buildSourceProjection
→ SH-024 evaluatePublicReadiness / protected-surface readiness
→ Taxonomy enrichment as needed
→ Location Safety fuzzy projection as needed
→ approved ranking signals / Track boost
→ Search builds provider document
→ SH-092 writeSearchProjection
→ Typesense upsert or delete
→ SearchUpsertEvent processed
→ queue/integration telemetry
```

**Proposed Ruling PR-CL02-03:** interpret `SearchUpsertEvent` as a **refresh-to-current-source-truth request** even though its historical name says “Upsert.” The worker decides at execution time whether the correct provider effect is create/update or delete. This avoids inventing a second de-index queue and keeps retries/attempts in the canonical queue infrastructure rather than duplicating them in Search.

### Thin delivery rule

Route handlers, server actions, admin pages, and workers may invoke owner application services, but they do not own complete workflows or lifecycle transitions.

---

## 6. Folder / Code Organization

The exact root layout remains subordinate to root `code-standards.md`. Within that layout, CL-02 should preserve Module-first ownership.

A compatible structure is:

```text
src/
  modules/
    taxonomy-classification/
      domain/
      application/
      contracts/
      persistence/
      public.ts

    ai-taxonomy/
      domain/
      application/
      contracts/
      persistence/
      providers/
        bedrock/
      workers/
      public.ts

    search-public-visibility/
      domain/
      application/
      contracts/
      persistence/
      providers/
        typesense/
      workers/
      public.ts

  platform/
    ... canonical SH-### primitives only ...

  app/
    ... thin public search, protected search, and admin delivery surfaces ...

tests/
  modules/
  contracts/
  integration/
  e2e/
```

### Module-owned code

**Taxonomy & Classification owns:**

- hierarchy and term invariants;
- taxonomy normalization policy;
- canonical taxonomy queries;
- taxonomy administration commands;
- classification validation;
- requirement-trigger translation;
- approved taxonomy seed data;
- affected-term/assignment calculation;
- no Bedrock client;
- no Typesense client.

**AI Taxonomy owns:**

- AI request policy;
- AI classification input/output schema;
- prompt/model-version selection semantics;
- `AiClassificationLog` and `AiSuggestion` repositories after schema approval;
- Bedrock/provider adapter implementation through the approved provider port;
- suggestion/run query APIs;
- AI backfill worker;
- no accepted taxonomy repository;
- no Search provider client.

**Search / Public Visibility owns:**

- `SearchUpsertEvent` repository;
- `SearchEntityType` interpretation;
- provider document schemas;
- source-projection composition;
- public/protected discovery query APIs;
- Typesense adapter;
- index/reindex/deindex/backfill/reconcile workers;
- search debug tooling;
- no source business repositories.

### Cluster-local coordination

No persistent generic `discovery` or `classification` service is approved.

If coordination is required:

- Taxonomy owns the AI-suggestion acceptance workflow because accepted classification is the result being decided;
- Search owns projection orchestration because search-provider convergence is the result being produced;
- AI owns classification-run orchestration because AI proposal/run truth is the result being produced.

A Cluster-level folder may contain documentation, contract fixtures, or integration tests, but it must not become a fourth business owner.

### Shared platform code

Code may move into shared/platform infrastructure only when it corresponds to:

- a canonical SH operation;
- a genuine platform primitive;
- a provider-neutral infrastructure contract already approved by architecture.

“Used by two Modules” is not enough reason to create a generic shared service.

---

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
|---|---|---|---|
| Taxonomy & Classification | Canonical Domain/Category/Tag vocabulary; hierarchy; normalization policy; term active state; classification validity; trigger interpretation | Entity existence/context; AI suggestions; detailed requirement references; Search refresh interface; Audit/Ops | AI prompts/runs; Typesense; business entity lifecycles; verification completion; healthcare readiness; exact location; entitlements; generic holds |
| AI Taxonomy | AI classification runs; suggestion proposals; confidence/provenance; prompt/model versions; output validation policy | Taxonomy vocabulary; owner-approved source snapshots; privacy/healthcare data-boundary decisions; Role; Audit/Ops | Accepted taxonomy; taxonomy joins; Search execution; raw resume parsing; automated hiring decisions; compliance outcomes |
| Search / Public Visibility | Search refresh queue truth; provider documents; indexing/deindexing; search query behavior; backfill/reconciliation/debug | Owner-safe source projections; public-readiness decisions; taxonomy; fuzzy location; trust display signals; entitlement boosts; moderation/privacy commands | Source entity truth; taxonomy truth; compliance/verification/healthcare/location decisions; raw resumes; entitlement truth |
| Marketplace Supply | Offering lifecycle and Offering-owned public facts | Taxonomy validation; AI suggestions; Search refresh | Taxonomy term lifecycle; AI run truth; Typesense writes |
| Gig / Demand | Gig lifecycle and public facts | Taxonomy validation; Search refresh | Taxonomy term lifecycle; Search provider state |
| Organization Hiring | Organization and Job lifecycle/public facts | Taxonomy validation; AI suggestions; Search refresh | Taxonomy term lifecycle; Job Compliance findings; Search provider state |
| Candidate Application & Resume Privacy | CandidateProfile/Application/resume privacy; `CandidateSearchProjection` | Taxonomy validation; AI suggestions when allowed; Search refresh | Search provider state; Taxonomy terms |
| Professional Eligibility | Professional public-readiness decision | Taxonomy triggers; Search refresh | Taxonomy terms; Search projection |
| Trust Verification / Screening | Verification requirements/checks; TrustBadge truth | Accepted taxonomy | Search ranking/projection |
| Healthcare / Regulated Services | Healthcare readiness/data-boundary truth | Accepted taxonomy | Search projection; Taxonomy acceptance |
| Location Safety | Exact/fuzzy location policy and records | Source context | Search query/index execution |
| Content Moderation | Report/case/action truth | Search execution interface | Typesense mechanics |
| Privacy / Data Erasure | PrivacyRequest/erasure/retention orchestration | CL-02 target executors | Search/AI owner records themselves |
| Track Subscription & Entitlement | entitlement/boost/usage truth | Search surface context | Search ranking execution |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | safe action metadata | Taxonomy/AI/Search domain truth |
| Observability / Ops | `SystemEvent`, `IntegrationFailure`, queue/incident visibility | correlation and safe execution metadata | Taxonomy/AI/Search lifecycle truth |

---

## 8. Data Ownership

### CL-02-owned and directly relevant records

| Record / enum / projection | Owner | Meaning / boundary |
|---|---|---|
| `TaxonomyDomain` | Taxonomy & Classification | Highest controlled classification level; canonical taxonomy truth |
| `TaxonomyCategory` | Taxonomy & Classification | Category within Domain; carries current category-level trigger metadata |
| `TaxonomyTag` | Taxonomy & Classification | Specific controlled term under Category; canonical vocabulary truth |
| `TagSource` | Taxonomy & Classification | Provenance vocabulary for tag attachments; `ai` is provenance only |
| `ProfessionalCategory`, `ProfessionalTag` | **Unresolved lifecycle owner** | Registry assigns Taxonomy; profile/entity ownership rules point toward contextual owner; do not build competing repositories |
| `CandidateCategory`, `CandidateTag` | **Unresolved lifecycle owner** | Glossary explicitly exposes dual-ownership ambiguity |
| `OrganizationCategory`, `OrganizationTag` | **Unresolved lifecycle owner** | Glossary explicitly exposes dual-ownership ambiguity |
| `OfferingTag` | **Unresolved lifecycle owner** | Claimed by both Taxonomy and Marketplace Supply |
| `GigTag` | **Unresolved lifecycle owner** | Claimed by both Taxonomy and Gig / Demand |
| `JobTag` | **Unresolved lifecycle owner** | Assignment ownership requires explicit ruling |
| `AiSuggestion` | AI Taxonomy — conceptual owner | Canonical proposal truth in registry/glossary; **missing from current Prisma** |
| `AiClassificationLog` | AI Taxonomy — conceptual owner | Canonical model-run/provenance truth; **missing from current Prisma** |
| `SearchUpsertEvent` | Search / Public Visibility | Search projection-refresh queue truth; current schema uses `processed`/`processedAt` |
| `SearchEntityType` | Search / Public Visibility | Search target-type vocabulary |
| Typesense document | Search / Public Visibility | External derived projection; rebuildable, never business truth |
| Search collection/document schema | Search / Public Visibility | Provider projection contract; exact collection strategy unresolved |

### Important foreign records consumed by CL-02

| Record | Owner | CL-02 use |
|---|---|---|
| `Offering` | Marketplace Supply | source-safe public projection/classification target |
| `Gig` | Gig / Demand | source-safe public projection/classification target |
| `Job`, `Organization` | Organization Hiring | source-safe public projection/classification target |
| `CandidateProfile`, `CandidateSearchProjection` | Candidate Application & Resume Privacy | protected candidate discovery; Search consumes projection only |
| `ProfessionalProfile` | Professional Eligibility | public profile projection/readiness |
| `JobComplianceCheck` / decision | Job Compliance | whether Job may be public |
| `VerificationRequirement`, `VerificationCheck`, `TrustBadge` | Trust Verification / Screening | requirement truth and approved display/ranking signal |
| `HealthcareComplianceProfile` / data-boundary decision | Healthcare | healthcare readiness and provider-input/public-readiness gates |
| `FuzzyLocationCache`, location precision/reveal records | Location Safety | fuzzy public location; exact location must not enter public index |
| `ComplianceHold` | Admin Review / Compliance Hold | reusable stop sign |
| `ModerationAction` | Content Moderation & Legal Notice | hide/restore/freeze decision |
| `PrivacyRequest`, `DataErasureJob`, `DataRetentionExemption` | Privacy / Data Erasure | orchestration/retention truth |
| `TrackEntitlementGrant`, `TrackUsageEvent` | Track Subscription & Entitlement | search-feature/boost decisions; no local premium state |
| `AuditEvent`, `AccessAuditLog` | Audit / Event Ledger | generic audit and sensitive-access proof |
| `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident` | Observability / Ops | operational failures, indexing lag, worker visibility |

### Current Prisma-specific taxonomy facts

The supplied Prisma schema establishes:

- Domain slug/name global uniqueness;
- Category slug/name uniqueness within Domain;
- Tag slug/name uniqueness within Category;
- `isActive` on Domain, Category, and Tag;
- category-level `verificationRequired`, `requiresHealthcareCompliance`, and `dataSensitivity`;
- tag-level `verificationRequired`;
- tag-join `source`, optional `confidence`, `verified`, and `createdAt`;
- `TagSource` values `user`, `professional`, `organization`, `ai`, `admin`, `system`, while `candidate` is currently commented out.

Those facts are executable schema evidence, not permission to guess the unresolved semantics of `verified`, confidence, candidate provenance, cross-category tags, or tag-level healthcare/location triggers.

### Provider-event records

No CL-02 provider webhook/event-deduplication record is currently confirmed. Bedrock is invoked synchronously/as a queued provider call, and Typesense is written through Search. If a future provider introduces webhook callbacks, provider-event truth must remain with the provider-owning Module and reuse SH-060 mechanics rather than introducing one shared global provider-event table.

---

## 9. Lifecycle Ownership

### 9.1 Taxonomy term lifecycle

**Owner:** Taxonomy & Classification.

Current persisted state is `isActive` rather than a rich enum.

Current minimum lifecycle:

```text
created active/inactive according to command
↔ active / inactive
```

Only Taxonomy may change term state.

**Unresolved:** hard delete, retire, merge, alias, history/versioning, logical cascade from inactive parent, and whether additional lifecycle states are required.

### 9.2 Taxonomy assignment lifecycle

**Owner:** unresolved for entity-specific join rows.

Confirmed facts:

- the accepted classification uses taxonomy joins and/or source entity category references;
- Taxonomy owns term validity and classification semantics;
- contextual entity Modules own their business entity lifecycle;
- duplicate repositories for the same join rows are prohibited.

**PR-CL02-01 — Proposed Ruling:** contextual entity Modules own create/delete lifecycle of their entity-specific taxonomy join rows, while Taxonomy owns validation, canonical IDs, normalization, and classification-trigger semantics. A contextual owner may write an attachment only after `SH-023 validateTaxonomyAssignment` succeeds. Taxonomy must never acquire a generic write repository for all business entities.

This ruling must be approved before join repositories/services are committed.

### 9.3 AI classification-run lifecycle

**Owner:** AI Taxonomy.

A run lifecycle is clearly implied but not yet modeled. Required states include at least queued/processing/completed/failed semantics, but exact enum names and retry/cancel representation are unresolved.

Operational retries remain in shared queue/Ops records. AI run state answers what happened to the classification run, not how many queue attempts occurred.

### 9.4 AI suggestion lifecycle

**Owner of proposal record:** AI Taxonomy.  
**Owner of acceptance decision:** Taxonomy & Classification.

The evidence requires a split:

```text
AI creates proposal truth
→ Taxonomy accepts/rejects for platform classification
→ AI records the disposition/reference on its own proposal
```

The exact status vocabulary and acknowledgement protocol are unresolved.

`AiSuggestion.status=accepted` must never be the only proof of accepted taxonomy; accepted term/attachment truth must exist in the Taxonomy/contextual record.

### 9.5 Search projection-refresh lifecycle

**Owner:** Search / Public Visibility.

Current Prisma state:

```text
processed = false
→ processing occurs through worker infrastructure
→ processed = true + processedAt
```

**PR-CL02-03 — Proposed Ruling:** `SearchUpsertEvent` represents a request to converge the provider projection to **current authoritative source truth**. At processing time:

- eligible/currently public source → upsert/update provider document;
- ineligible/hidden/erased/missing source → delete provider document;
- transient provider failure → leave source work unprocessed and retry through SH-047/048;
- terminal operational failure → remain visibly unresolved through Search debug + Ops dead-letter evidence.

Attempts, leases, and dead-letter metadata belong to generic queue infrastructure, not duplicated Search columns.

### 9.6 Search provider-document lifecycle

**Owner:** Search / Public Visibility as projection owner.

```text
absent
→ indexed
→ updated
→ removed
→ rebuild/reconcile as needed
```

This lifecycle is derived and can be reconstructed. It never changes the source entity’s lifecycle.

### 9.7 CandidateSearchProjection lifecycle

**Owner:** Candidate Application & Resume Privacy, not Search.

Search may index an approved protected-provider document derived from the Candidate-owned projection. Search must not mutate `CandidateSearchProjection.status`, `rawResumeTextIndexed`, erase markers, or source privacy state.

---

## 10. Public Module Interfaces

### Taxonomy & Classification interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
|---|---|---|---|---|---|---|---|
| `listTaxonomyTree` | Taxonomy | UI, AI, Search, source Modules | Read canonical active/all taxonomy tree according to caller scope | filter/scope; includeInactive only when authorized | canonical Domains/Categories/Tags + IDs/active flags/policy metadata | truth | local category maps |
| `getTaxonomyTerm` | Taxonomy | AI, Search, admin, source Modules | Read one canonical term | term type + ID/slug | canonical term | truth | direct foreign term reconstruction |
| **SH-023 `validateTaxonomyAssignment`** | Taxonomy | all classifiable source Modules | Validate hierarchy, active state, and assignment compatibility | entity type/context + Domain/Category/Tag IDs | valid/invalid + normalized canonical IDs/reasons | decision | local tag validators |
| **SH-022 `resolveTaxonomyRequirements`** | Taxonomy | Professional Eligibility, Trust, Healthcare, Search/source owners | Translate accepted classification into triggered requirements | accepted Domain/Category/Tag IDs + context | requirement refs, owners, trigger sources, severity/applicability | decision/requirements | whether requirements are satisfied |
| `create/update/setActive Taxonomy*` | Taxonomy | authorized admins | Administer vocabulary | validated term/policy input + actor/reason | updated canonical term | truth mutation | direct Prisma writes from admin UI |
| `decideAiClassificationSuggestion` | Taxonomy | admin/review workflow; AI | Accept/reject an AI proposal for platform classification | suggestion reference + target + reviewer + selected canonical term(s) | decision reference + resulting accepted classification refs | decision | AI-owned run mutation or Search write |

The final name/shape of `decideAiClassificationSuggestion` is a Proposed Ruling and depends on `U-CL02-01/04/05`.

### AI Taxonomy interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
|---|---|---|---|---|---|---|---|
| `requestClassificationSuggestions` | AI Taxonomy | Marketplace, Hiring, Candidate, admins | Produce structured classification/skill proposals | target ref, owner-approved snapshot/reference, classification purpose | run ID, suggestion IDs/status | proposal/evidence | accepted taxonomy |
| `getSuggestionsForTarget` | AI Taxonomy | Taxonomy, source owner, admin | Read proposals and provenance | target ref + scope | suggestion DTOs + confidence/provenance | truth about proposal | acceptance |
| `getClassificationRun` | AI Taxonomy | authorized admin/Ops | Diagnose one run | run ID | model/prompt version, safe input/output metadata, outcome | evidence | AuditEvent or Ops incident |
| `listSuggestionsForReview` | AI Taxonomy | Taxonomy/admin review | Obtain review candidates | filters/cursor | proposal list | proposal truth | final classification |
| `acknowledgeSuggestionDecision` | AI Taxonomy | Taxonomy workflow | Record that Taxonomy made a decision | suggestion ID + Taxonomy decision ref/outcome | updated proposal disposition | proposal truth | taxonomy mutation |

The last interface and exact lifecycle are blocked on `U-CL02-04/05`.

### Search / Public Visibility interfaces

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
|---|---|---|---|---|---|---|---|
| **SH-091 `requestSearchProjectionRefresh`** | Search | all source/decision owners | Request convergence of provider state to current source truth | entity type + entity ID + reason + idempotency context | refresh-event/work reference | projection request truth | direct Typesense writes |
| `searchPublicDiscovery` | Search | public product surfaces | Search public eligible projections | query, approved filters/facets, paging/sort | safe result DTOs + paging | projection | business lifecycle truth |
| `searchCandidatesForOrganization` | Search | authorized Organization Hiring surfaces | Protected candidate discovery | authenticated org actor/context, query, filters | privacy-safe candidate results | protected projection | raw resume/application truth |
| `inspectSearchProjection` | Search | authorized admins/Ops | Explain indexed/excluded/stale/failed state | entity type + ID | source/projection status, safe reasons, provider metadata | projection/debug evidence | source policy ownership |
| **SH-095 `executePrivacyInstruction`** implementation | Search | Privacy orchestrator | Remove/restrict/anonymize Search-owned provider projection/work records where permitted | Privacy target instruction | typed execution result | execution evidence | PrivacyRequest lifecycle |
| **SH-096 `enumerateSubjectData`** implementation | Search | Privacy | Enumerate Search-owned subject references | subject ID | target refs | inventory | privacy orchestration |
| **SH-103 `executeModerationDecision`** target implementation | Search | Content Moderation | Apply authoritative hide/restore decision to Search projection | moderation action ref + target | deindex/refresh result | execution evidence | moderation decision itself |

### Required source-owner interfaces consumed by Search

Search must consume, not recreate:

- **SH-094 `buildSourceProjection`** — each source Module returns an approved Search-facing DTO;
- **SH-024 `evaluatePublicReadiness`** — each source/compliance owner returns its decision; Search composes;
- **SH-028 `applyFuzzyPublicLocation`** — Location Safety returns fuzzy location;
- **SH-005 `resolveEntitlement`** — Track supplies boost or protected-feature policy;
- Job Compliance, Professional Eligibility, Trust, Healthcare, Moderation, Privacy, and Hold public interfaces as required by entity/surface.

---

## 11. Canonical Shared Operations Used by This Cluster

Only operations materially required by CL-02 are listed here. Their full definitions remain in `context/shared/shared-operations.md`.

| SH ID / operation | Canonical owner | Consuming CL-02 Module(s) | Reusable mechanism / capability | Local policy that remains local | Invocation point | Must not duplicate |
|---|---|---|---|---|---|---|
| SH-001 `resolveAuthenticatedActor` | Identity & Access | all protected admin/AI/search operations | trusted actor resolution | which CL-02 actions are public vs protected | admin/review/protected-search entry | route-local current-user helpers |
| SH-002 `authorizeResourceAction` | Role / Authority | all three | resource/action decision | taxonomy admin actions, AI review/backfill actions, search admin/candidate-search facts | before protected read/mutation | local CL-02 role engines |
| SH-003 `queryOwnerFacts` **Proposed** | source owner | AI, Search, Taxonomy integration | minimum owner relationship facts | exact source DTO | before cross-Module policy/read | universal entity repository |
| SH-005 `resolveEntitlement` | Track Subscription & Entitlement | Search | commercial boost/protected-search entitlement | how Search applies a permitted boost after readiness | ranking/protected candidate query | premium/boost booleans |
| SH-011 `evaluateComplianceHold` | Admin Review / Compliance Hold | Search; Taxonomy/AI where action-specific | reusable stop-sign decision | which CL-02 action is blocked | readiness/review/admin action | `searchBlocked`, `aiBlocked` generic flags |
| SH-022 `resolveTaxonomyRequirements` | Taxonomy & Classification | source/compliance consumers; Search composition where needed | accepted classification → requirement refs | taxonomy trigger rules | after accepted classification | local requirement maps |
| SH-023 `validateTaxonomyAssignment` | Taxonomy & Classification | source owners, AI acceptance workflow | canonical classification validation | hierarchy/compatibility/active semantics | before accepted assignment write | local tag/category validators |
| SH-024 `evaluatePublicReadiness` | source/compliance owner; Search composes | Search | shared decision contract | each owner’s actual readiness policy | before index/update | universal Search eligibility engine |
| SH-028 `applyFuzzyPublicLocation` | Location Safety | Search | approved fuzzy public location | Search filter/display use | projection build | coordinate fuzzers |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | all three | generic audit proof | which admin/sensitive actions require audit | after/with important admin action | local audit tables |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | AI, Search protected candidate/admin surfaces | protected-data access proof | which CL-02 data is sensitive and safe metadata | access to sensitive AI/candidate data | local access logs |
| SH-032–038 request/log/telemetry operations | Observability / Ops | all three | correlation, structured logs, redaction, errors, metrics, integration/queue telemetry | CL-02 operation names and safe dimensions | every request/job/provider path | local loggers/failure ledgers |
| SH-044 `executeIdempotentCommand` | platform application infra | all three | retry-safe command execution | semantic idempotency key per owner action | admin mutations, AI requests, Search refresh | local idempotency stores |
| SH-045 `deduplicateDomainEvent` | platform event infra | AI/Search consumers | consumer inbox dedupe | consumer-side effect identity | event-triggered jobs | local processed-event boilerplate |
| SH-046 `publishDomainEvent` | platform outbox infra | Taxonomy, AI, Search as needed | transactional domain event publication | event names/payload/privacy | after authoritative mutation | private event buses |
| SH-047 `enqueueReliableJob` | shared queue infra | AI, Search, Taxonomy backfills | durable async work | owner payload/completion meaning | provider calls/backfills/indexing | per-module queue systems |
| SH-048 `executeRetryWithBackoff` | shared queue infra | AI, Search | bounded retry | provider-specific retryability | transient Bedrock/Typesense failure | hand-written retry loops |
| SH-051/052 concurrency primitives | shared persistence infra | Taxonomy; AI/Search where needed | locks/CAS | collision/merge/reviewer command policy | conflicting admin/worker mutation | in-memory mutexes |
| SH-053 `transitionLifecycleState` | shared mechanism, owner policy | AI and Taxonomy if richer states approved | state-machine plumbing | exact owner transition graph | lifecycle commands | generic lifecycle policy owner |
| SH-065 `invokeFoundationModel` **Proposed** | AI Taxonomy initially; broader owner unresolved | AI Taxonomy | provider-neutral model invocation | classification prompt/model policy | after safe input build | Bedrock clients in Taxonomy/Search/source Modules |
| SH-066 `validateStructuredProviderOutput` | shared validation primitive | AI Taxonomy | schema-bound provider output validation | AI Taxonomy output schema | immediately after model result | ad hoc parse/JSON trust |
| SH-072 `hashCanonicalPayload` | shared crypto | AI, Search/Taxonomy as needed | deterministic evidence hash | which payload is canonical | input/projection evidence where required | custom hashing helpers |
| SH-077 `buildCanonicalTextSnapshot` | shared text primitive | AI Taxonomy | deterministic text snapshot | owner-approved field selection | before provider input/hash | per-feature canonicalization |
| SH-078 `minimizeAndRedactProviderInput` | shared serializer + source policy | AI Taxonomy | safe provider-bound serialization | source/privacy/healthcare field allowlist | before Bedrock invocation | ad hoc redaction |
| SH-079 `normalizeControlledTerm` | Taxonomy policy over shared text primitive | Taxonomy; AI consumes result | canonical term normalization | collisions/aliases/term policy | taxonomy term input/suggestion matching | `normalizeTag.ts` copies |
| SH-091 `requestSearchProjectionRefresh` | Search | Taxonomy and all source/decision owners | canonical projection refresh command | entity mapping/reason | after source truth changes | direct SearchUpsertEvent writes by consumers or Typesense calls |
| SH-092 `writeSearchProjection` | Search | Search | provider adapter | document/collection schema, index/delete semantics | projection worker | Typesense clients outside Search |
| SH-093 `reconcileSearchProjection` | Search | Search | projection reconciliation | expected provider state | scheduled/admin reconcile | custom reconciliation scripts |
| SH-094 `buildSourceProjection` | each source Module | Search; AI when classification snapshot variant is approved | source-safe projection pattern | exposed fields/version | projection load | Search reading foreign tables |
| SH-095–098 privacy owner protocol | Privacy + record owners | AI, Search, Taxonomy contextual data | enumerate, execute, retain/anonymize protocol | owner fields/retention facts | Privacy fulfillment | CL-02 privacy workflow |
| SH-103 `executeModerationDecision` | Moderation decision; target owner executes | Search | target execution protocol | Search provider effect only | hide/restore/freeze | local moderation decision logic |
| SH-115 `buildAggregateProjection` | projection owner | Search | projection assembly mechanism | Search provider document policy | after owner DTOs/decisions | second source-of-truth projection database |

### Shared capability distinctions

- **Canonical shared capability:** e.g. SH-001, SH-002, SH-029.
- **Platform primitive:** e.g. SH-044, SH-047, SH-051.
- **Shared contract / separate policy:** e.g. SH-024.
- **Shared mechanism / separate truth:** e.g. SH-053 and SH-115.
- **Provider-adapter pattern:** e.g. SH-065/066 for AI and SH-092 for Search.
- **Module public interface:** e.g. SH-022/023 and SH-091.

The Cluster may reference all of these. It may not collapse them into a `cl02SharedService`.

---

## 12. Cross-Module Data Flows

### Flow A — Taxonomy term administration

```text
Admin command
→ Identity resolves actor
→ Role authorizes taxonomy term action
→ Taxonomy validates name/slug/hierarchy/normalization
→ Taxonomy authoritative write
→ AuditEvent
→ domain event/outbox if affected consumers require it
→ Search refresh for taxonomy projection
→ affected source owners may request their own refresh after classification impact is known
```

Owner of authoritative write: Taxonomy.

Hard delete/merge is not enabled until `U-CL02-07` is resolved.

### Flow B — Manual entity classification

```text
Source entity owner receives classification change
→ owner calls Taxonomy SH-023
→ Taxonomy validates canonical active terms and hierarchy
→ approved join owner writes accepted assignment
→ source owner/Taxonomy resolves triggered requirements through SH-022
→ source owner reevaluates its own readiness/lifecycle
→ source owner requests SH-091 Search refresh if public projection may change
```

The assignment write is blocked until `U-CL02-01/02` is resolved.

### Flow C — AI classification suggestion

```text
Source owner or admin requests suggestion
→ AI Taxonomy validates classification purpose
→ source owner supplies approved snapshot
→ Taxonomy supplies active vocabulary
→ privacy/healthcare policy limits data
→ SH-078 provider-input minimization
→ SH-065 provider invocation
→ SH-066 output validation
→ AIClassificationLog authoritative write
→ AiSuggestion authoritative write(s)
→ optional audit/ops effects
→ suggestion becomes reviewable
```

No taxonomy or search write occurs in this flow.

### Flow D — Accept or reject AI suggestion

```text
Reviewer command
→ actor + authorization
→ Taxonomy loads AI proposal through AI public interface
→ Taxonomy revalidates current canonical terms and target context
→ accepted classification write by approved assignment owner OR no write on rejection
→ Taxonomy records decision reference/event
→ AI acknowledges disposition on AiSuggestion
→ Search refresh requested only if accepted source truth changed
```

This flow is gated by `U-CL02-01`, `U-CL02-04`, and `U-CL02-05`.

### Flow E — Source object becomes discoverable

```text
Source lifecycle/readiness change
→ source owner requests SH-091
→ SearchUpsertEvent authoritative write
→ Search worker loads SH-094 source projection
→ composes SH-024 readiness decisions
→ applies fuzzy location / approved taxonomy / approved ranking signals
→ provider document built
→ SH-092 Typesense upsert
→ SearchUpsertEvent processed
→ metrics / queue telemetry
```

Source entity remains authoritative.

### Flow F — Source object becomes ineligible, hidden, erased, or missing

```text
authoritative source/moderation/privacy/hold change
→ SH-091 Search refresh or SH-103/SH-095 target execution
→ Search worker re-reads current decisions
→ expected state = absent
→ SH-092 provider delete
→ SearchUpsertEvent marked processed after successful convergence
→ audit/ops effects as applicable
```

De-indexing is not deletion of the source record.

### Flow G — Candidate protected discovery

```text
Organization user searches candidates
→ SH-001 actor
→ SH-002 organization-scoped authorization
→ Track SH-005 entitlement if candidate search/boost feature is gated
→ Candidate owner supplies CandidateSearchProjection + privacy decision
→ Search queries protected provider collection/surface
→ Search returns privacy-safe fields only
→ sensitive access audit where required
```

Raw resume text and application documents are excluded.

### Flow H — Entitlement boost change

```text
Track entitlement grant changes
→ Track publishes owner event / calls SH-091 for affected search target
→ Search refreshes eligible projection
→ Search applies boost metadata only after public/protected readiness passes
→ provider document changes ranking metadata
```

An entitlement can change ordering or access to a protected feature; it cannot make a nonpublic/noncompliant entity eligible.

### Flow I — Taxonomy requirement composition

```text
accepted Domain/Category/Tags
→ SH-022 resolveTaxonomyRequirements
→ requirement refs to Trust / Healthcare / Location / source owner
→ those owners evaluate satisfaction
→ source lifecycle/readiness owner decides whether action/publication is allowed
→ Search later consumes the resulting SH-024 decision
```

Taxonomy never converts a trigger into a successful compliance result.

---

## 13. Cross-Cluster Bridges

| Source Cluster / Module | Destination | Information / command | Authoritative owner | Interface/event | Forbidden coupling |
|---|---|---|---|---|---|
| CL-03 Marketplace Supply | CL-02 Search | Offering public projection + refresh | Marketplace Supply owns Offering; Search owns projection | SH-094 + SH-024 + SH-091 | Search reading/mutating Offering repository |
| CL-04 Gig / Demand | CL-02 Search | Gig public projection + refresh | Gig / Demand | SH-094 + SH-024 + SH-091 | Search owning Gig visibility lifecycle |
| CL-06 Organization Hiring | CL-02 Search | Organization/Job projection + refresh | Organization Hiring; Job Compliance owns compliance decision | SH-094 + SH-024 + SH-021 + SH-091 | Search implementing Job compliance |
| CL-06 Candidate Application | CL-02 Search | privacy-safe candidate projection | Candidate Application & Resume Privacy | Candidate-owned projection query/SH-094 + SH-091 | raw resume or application reads |
| CL-03 Professional Eligibility | CL-02 Search | Professional public readiness/projection | Professional Eligibility | SH-016/SH-024 + SH-094 + SH-091 | Search reconstructing selling readiness |
| CL-03 Trust Verification | CL-02 Taxonomy/Search | verification requirements and approved display signals | Trust Verification | SH-017/018; public TrustBadge query | badge as verification truth |
| CL-03 Healthcare | CL-02 AI/Search | provider-input/public-readiness boundary | Healthcare | SH-020 / healthcare data-boundary interface | AI/Search deciding PHI policy |
| CL-08 Location Safety | CL-02 Search | fuzzy public location | Location Safety | SH-028 | exact coordinates or local fuzzing |
| CL-08 Privacy | CL-02 AI/Search | erasure/export/restriction instructions | Privacy | SH-095–098 | CL-02 PrivacyRequest workflow |
| CL-09 Moderation | CL-02 Search | hide/restore/freeze decision | Content Moderation | SH-103 + SH-091 | Search moderation case logic |
| CL-09 Holds | CL-02 | active stop-sign decision | Admin Review / Compliance Hold | SH-011 | local blocked booleans |
| CL-01 Track | CL-02 Search | candidate-search access, boost metadata, change event | Track Subscription & Entitlement | SH-005 + SH-091/event | local premium/boost truth |
| CL-09 Audit/Ops | CL-02 | audit/access proof and operational telemetry | Audit/Ops | SH-029/030/032–040 | using logs as lifecycle truth |
| CL-02 Taxonomy | CL-03/04/06 source Modules | canonical validation and requirement triggers | Taxonomy | SH-022/023 | source Module taxonomy copies |
| CL-02 AI | CL-03/06 source Modules | classification suggestions only | AI Taxonomy | request/query interfaces | AI automated business/hiring decisions |
| CL-02 Search | public product surfaces | discovery projection results | Search for projection only | Search query API | treating results as transaction/readiness truth |

### Primary CL-02 → CL-03 bridge

The current Cluster Registry explicitly states:

```text
active compliant supply becomes searchable
```

Search projects approved source truth. It does not own professional eligibility or Offering lifecycle.

---

## 14. Authentication and Authorization

### Public operations

May be anonymous when product requirements allow:

- public taxonomy-tree reads limited to public active terms;
- `searchPublicDiscovery`;
- public result-page hydration from approved projection fields.

Public access never bypasses Search’s field/surface allowlist.

### Protected operations

Require SH-001 and SH-002:

- taxonomy create/update/activate/deactivate;
- taxonomy policy/trigger changes;
- AI manual suggestion requests when source data is protected;
- AI suggestion review/disposition;
- AI run inspection;
- AI backfill controls;
- Search backfill/reconciliation/debug;
- protected candidate search;
- protected search analytics/debug details;
- privacy/moderation execution entry points except trusted service-to-service actors.

### Contextual facts supplied to authorization

Role / Authority interprets:

- platform admin/support role;
- Organization membership/role from Organization Hiring;
- ownership/resource facts from the source Module;
- candidate-search organization context;
- target/resource identifiers.

CL-02 must not copy those relationship rows into local authorization tables.

### Sensitive/admin access

Admin capability does **not** imply unrestricted access to:

- raw resumes;
- private candidate text;
- PHI;
- private messages;
- identity documents;
- provider payloads containing sensitive data.

If a sensitive action is designated for step-up by the owning policy, consume SH-014. The Cluster does not declare all taxonomy/search administration step-up-required by default without a root/security ruling.

---

## 15. Compliance and Readiness Composition

CL-02 is primarily a classification/projection Cluster. It consumes compliance truth rather than absorbing compliance lifecycles.

### Taxonomy-trigger composition

Taxonomy may return:

- verification requirement references;
- healthcare-lane triggers;
- data sensitivity;
- license/background-check triggers;
- location-related requirements once represented;
- severity/applicability metadata.

It does **not** return “verification passed” or “healthcare ready.”

### Search public-readiness composition

Search requires owner decisions before provider projection.

Representative composition:

```text
source lifecycle/public flag
+ source-owner readiness
+ taxonomy accepted classification
+ Job Compliance where Job
+ Professional Eligibility where Professional/Offering path requires it
+ Trust/verification public decision where required
+ Healthcare decision where required
+ active ComplianceHold decision
+ Moderation visibility
+ Privacy restriction/erasure state
+ fuzzy Location Safety projection
= Search index / update / remove action
```

The specific owner policy for each entity remains external and is returned through SH-024 or a named owner interface.

### Consent

`ConsentLog` may be an input to an upstream source/AI/candidate policy, but CL-02 never treats consent proof as direct permission to:

- send candidate data to AI;
- expose a Candidate in search;
- index an Offering/Job;
- bypass privacy or moderation;
- activate a Track feature.

### Track entitlements

Track may govern:

- access to protected candidate search;
- candidate search boost;
- other approved ranking/perk metadata.

It does not govern public eligibility. Search applies entitlement effects only after readiness.

### ComplianceHold

Search evaluates applicable holds when the owner/public-readiness contract requires them. AI/Taxonomy may also be prevented from specific administrative actions by a hold if a domain policy explicitly says so. No CL-02 generic `blocked` schema is created.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Domain events

Exact event names are not yet canonicalized. Candidate event families include:

- taxonomy term created/changed/activated/deactivated;
- accepted classification changed;
- AI classification run completed/failed;
- AI suggestion available;
- Taxonomy suggestion decision made;
- Search projection refresh requested/converged.

These names are **not** binding until event contracts are approved.

### Transactional outbox

Use SH-046 when a CL-02 authoritative mutation must reliably notify downstream consumers.

Examples:

- Taxonomy term trigger change that affects many source records;
- accepted classification change;
- AI suggestion availability if review is asynchronous.

Outbox does not replace `SearchUpsertEvent`; the latter is Search-owned work truth.

### Search refresh queue

- canonical entry: SH-091;
- source record: `SearchUpsertEvent`;
- execution: SH-047 worker;
- retry: SH-048;
- operational attempts/dead letters: Ops/queue infrastructure;
- final provider effect: SH-092;
- reconciliation: SH-093.

### AI jobs

Use reliable jobs for:

- expensive classification requests;
- batch/backfill classification;
- retries after transient provider failures;
- stale/superseded suggestion maintenance if approved.

AI run outcome stays in AI records. Queue attempt truth stays in Ops infrastructure.

### Taxonomy jobs

Potential jobs:

- seed catalog idempotently;
- normalize existing assignments;
- calculate/fan-out affected Search refreshes after broad taxonomy changes;
- future term merge/migration only after `U-CL02-07`.

### Concurrency

Use canonical locking/optimistic concurrency where:

- two admins edit the same taxonomy term;
- a taxonomy term is being deactivated while an assignment is accepted;
- two reviewers decide the same AI suggestion;
- multiple Search refresh events for the same entity arrive;
- backfill and live refresh overlap.

Search must converge to current source truth, so duplicate/stale refresh requests must be harmless.

### Dead-letter behavior

Dead-letter is operational evidence, not a new business status. The owner/debug surface must make unresolved Search/AI work visible and allow safe retry/reconciliation.

### Workflow/saga boundaries

The AI-acceptance sequence is the only meaningful CL-02 cross-Module workflow candidate. Taxonomy owns the acceptance decision. If multi-step acknowledgement requires a durable workflow record, use SH-049 mechanics after the ownership/record decision is approved; do not create a generic Cluster saga by default.

---

## 17. Provider Integrations

### AI provider

```text
AI Taxonomy
→ provider-neutral model invocation port (SH-065, Proposed)
→ AWS Bedrock adapter
→ model provider
→ validated structured output (SH-066)
→ AiClassificationLog / AiSuggestion
```

Rules:

- AI Taxonomy owns provider configuration semantics for classification;
- Taxonomy, Search, Marketplace Supply, Hiring, and Candidate Modules do not instantiate Bedrock clients for this capability;
- source data is minimized/redacted before leaving Workin Ants;
- output is treated as untrusted until schema validation succeeds;
- prompt/source text is data, not executable instructions;
- no model tool may write Taxonomy or Search directly;
- provider model/version is evidence, not business truth;
- no provider webhook is currently required.

`SH-065` ownership is a Proposed Ruling in the canonical registry. Production adapter placement must remain behind the AI Taxonomy interface until the broader AI-infrastructure ownership question is approved.

### Search provider

```text
Search / Public Visibility
→ provider-neutral SearchProjectionProvider / SH-092
→ Typesense adapter
→ Typesense
→ normalized write/delete result
→ Search projection work completion
```

Rules:

- only Search owns Typesense credentials/client;
- Typesense collection/document shape is Search-owned projection policy;
- provider IDs/statuses do not become source entity state;
- unknown provider failures are classified and surfaced through Ops;
- provider absence/degradation never mutates source entities;
- reconciliation uses SH-093.

### Webhook verification and provider-event dedupe

Neither current CL-02 provider requires a confirmed webhook workflow. Therefore CL-02 must not preemptively create provider-event tables. If a future provider callback is introduced:

```text
owner adapter
→ SH-059 signature verification
→ owner-specific processed-provider-event truth using SH-060 mechanics
→ owner domain transition
```

---

## 18. Search / Projection Boundaries

### Projection owner

Search / Public Visibility owns:

- `SearchUpsertEvent`;
- provider collection/document schemas;
- index/delete/reindex/backfill/reconciliation execution;
- public Search API;
- protected candidate Search API;
- ranking/facet/query behavior after eligibility;
- Search debug/admin view.

### Source projection owner

Each source Module owns the safe source DTO through SH-094.

Search must not directly read foreign repositories as its default integration pattern.

### Supported entity vocabulary

The current `SearchEntityType` includes:

- `user`
- `professional_profile`
- `candidate_profile`
- `organization`
- `offering`
- `gig`
- `job`
- `taxonomy`
- `trust_badge`

Presence in the enum does **not** itself authorize public indexing.

In particular:

- a public `user` projection contract is not established and must remain disabled until explicitly approved;
- candidate discovery is protected and must use Candidate-owned privacy projection;
- TrustBadge is display projection only;
- taxonomy can be publicly discoverable as controlled vocabulary if the surface requires it.

### Indexing/de-indexing triggers

At minimum, Search refresh must react to:

- source creation/update/status/visibility changes;
- accepted taxonomy assignment changes;
- taxonomy term changes that materially affect projected fields/facets;
- professional readiness changes;
- Job compliance changes;
- candidate privacy/search projection changes;
- moderation hide/restore;
- privacy erasure/restriction;
- ComplianceHold changes where public readiness is affected;
- fuzzy-location changes;
- TrustBadge/display-signal changes;
- Track search boost/feature changes.

### What Search must never reconstruct

Search must not independently calculate:

- professional selling eligibility;
- Job compliance;
- candidate resume privacy;
- verification completion;
- healthcare readiness;
- exact-location reveal;
- moderation outcome;
- PrivacyRequest outcome;
- Track entitlement;
- accepted taxonomy from AI proposals.

### Ranking rule

Ranking is a projection policy applied only to eligible documents.

A ranking signal may include approved:

- textual relevance;
- taxonomy facets;
- public TrustBadge/display signals;
- Track boost metadata;
- source-defined public featured/quality fields.

Ranking may not create eligibility or expose a protected field.

---

## 19. Media / File Boundaries

CL-02 does not own `MediaAsset` or generic file access.

### AI classification input

AI Taxonomy receives:

- owner-approved structured fields; or
- owner-approved extracted text/snapshots.

It must not:

- request raw resume files from Media directly merely because a candidate is a classification target;
- issue signed URLs;
- bypass Candidate/Media contextual entitlement;
- persist entire private file contents into AI logs by default.

### Search projection

Public Search documents may include source-owner-approved public media references or derived public URLs only when those are already valid public fields.

Search does not:

- issue signed media URLs;
- index private file bodies;
- use an inaccessible MediaAsset as a public field;
- turn a file URL into evidence of entitlement.

If a discovery result later needs private media, the subsequent business/context Module must authorize access through Media / File Access.

---

## 20. Privacy / Retention

### Privacy orchestration

Privacy / Data Erasure owns:

- `PrivacyRequest`;
- `DataErasureJob`;
- `DataErasureTarget`;
- `DataRetentionExemption`;
- export-bundle orchestration.

CL-02 implements owner executors only.

### Taxonomy & Classification privacy responsibilities

Canonical taxonomy vocabulary is generally reference data, but entity-specific taxonomy attachments may contain subject relationships.

The approved join owner must:

- enumerate subject-linked assignments;
- execute erasure/anonymization/removal instructions where permitted;
- supply retention facts to Privacy.

Taxonomy must not invent a retention exemption.

### AI Taxonomy privacy responsibilities

AI records may contain personal or sensitive source-derived data.

AI Taxonomy must:

- enumerate subject-linked `AiSuggestion`/`AiClassificationLog` records;
- minimize provider input and persisted payloads;
- execute Privacy instructions against owned records;
- anonymize allowed personal metadata through SH-098;
- honor retention exemptions recorded by Privacy;
- support external-provider deletion if the selected provider exposes applicable retained resources.

**Unresolved:** exact AI retention period, which prompt/output fields may persist, whether provider-side deletion is required/possible, and how sensitive candidate-derived data is represented. Production retention policy is gated by `U-CL02-11`.

### Search privacy responsibilities

Search must:

- delete provider documents when Privacy instructs de-indexing/erasure;
- enumerate subject-linked Search provider/work references;
- avoid indexing raw resumes/private applications;
- remove or anonymize Search-owned metadata as allowed;
- report execution success/failure back to Privacy.

Deleting a Typesense document does not erase the source record.

### Candidate privacy

`CandidateSearchProjection` remains Candidate-owned. Search treats `rawResumeTextIndexed=false` as an invariant and must not introduce a provider document field containing raw resume text.

---

## 21. Audit and Observability

### Domain truth

Keep owner records:

- Taxonomy terms and accepted assignments;
- AI classification run/suggestion records;
- Search projection-refresh records.

### Generic audit

Use `AuditEvent` for important actor/system actions such as:

- taxonomy term create/change/deactivate;
- material taxonomy trigger change;
- AI suggestion accept/reject review;
- restricted backfill/reconcile invocation;
- sensitive administrative projection override if such a feature is later approved.

Audit does not replace Taxonomy history or AI run truth.

### Sensitive access

Use `AccessAuditLog` through SH-030 for protected data such as:

- restricted candidate search result access where policy requires;
- sensitive AI classification-run inspection;
- protected source snapshots.

### Operational observability

Use structured logs, metrics, `IntegrationFailure`, queue telemetry, and incidents for:

- Bedrock latency/failure/invalid output;
- Typesense latency/failure/degradation;
- indexing lag;
- queue depth/retry/dead-letter;
- search reconciliation mismatch;
- backfill progress;
- source-projection contract failure.

### Correlation

Every provider request, Search refresh, worker run, audit event, and error should carry request/correlation/causation identifiers where supported.

### Redaction

Telemetry must not contain:

- raw resume text;
- PHI;
- identity documents;
- private messages;
- tax/payment secrets;
- provider credentials;
- entire model prompts/outputs if they contain protected data.

Safe hashes, IDs, classifications, status codes, and bounded metadata are preferred.

---

## 22. Security Boundaries

1. Validate every server input at the application boundary.
2. Enforce protected taxonomy/AI/Search administration server-side with SH-001 and SH-002.
3. Keep Bedrock and Typesense credentials server-only in provider adapters.
4. Never expose provider administration credentials to browser code.
5. Treat model output as untrusted data; require SH-066 validation before persistence/use.
6. Treat source text as untrusted model input; it cannot grant tools, change prompt authority, or cause direct writes.
7. Apply SH-078 minimization/redaction before AI provider calls.
8. Restrict candidate search to approved organization context and privacy/entitlement decisions.
9. Use explicit field/facet/sort allowlists for search APIs; do not pass arbitrary user-supplied provider parameters through.
10. Rate-limit public search and expensive AI/backfill endpoints according to root infrastructure policy.
11. Use idempotency for projection refreshes, AI requests, and admin commands where retries are possible.
12. Use database concurrency controls for conflicting taxonomy/review mutations.
13. Never store exact private coordinates in public Search documents.
14. Never store raw resume/application/private file bodies in public or protected Search projection unless a future explicit privacy architecture ruling permits a narrowly defined field; current posture forbids it.
15. No CL-02 operation may bypass a ComplianceHold or moderation/privacy decision by calling Typesense directly.
16. Hash/redact evidence before telemetry where appropriate.
17. Avoid provider-native error bodies in client responses.
18. Search debug/admin output must redact provider secrets and private source payloads.
19. Backfills must have bounded batch size, authorization, idempotency, and pause/abort controls.
20. Any future webhook/callback must use signature verification and replay protection before side effects.

---

## 23. Testing Architecture

### Module unit tests

**Taxonomy:**

- hierarchy validation;
- uniqueness/normalization;
- active/inactive semantics that are approved;
- Domain/Category/Tag compatibility;
- requirement-trigger resolution;
- no readiness completion inference;
- no AI provider calls.

**AI:**

- prompt/input policy;
- source minimization;
- structured output schema;
- confidence/provenance validation;
- run/suggestion lifecycle once approved;
- no direct taxonomy/search mutation;
- candidate-sensitive input denial;
- no automated hiring decision behavior.

**Search:**

- projection composition;
- public/protected field allowlists;
- public-readiness combination;
- fuzzy-location enforcement;
- ranking cannot bypass readiness;
- provider document upsert/delete semantics;
- query filter/facet/sort validation.

### Public-interface contract tests

Required for:

- SH-022/023 Taxonomy contracts;
- AI request/query/disposition contracts;
- SH-091 Search refresh;
- Search public/protected queries;
- SH-094 source projection adapters;
- SH-024 readiness decisions;
- Privacy/Moderation target execution;
- Track boost/entitlement input.

### Lifecycle tests

- Taxonomy activate/deactivate transitions;
- AI run/suggestion transitions after schema approval;
- Search refresh unprocessed→processed convergence;
- duplicate/replayed decisions are idempotent.

### Cross-Module integration tests

- taxonomy change → Search refresh;
- AI suggestion → no accepted classification until Taxonomy decision;
- accepted AI suggestion → accepted assignment → Search refresh;
- source hidden/moderated/held → deindex;
- privacy erasure → provider delete;
- entitlement boost change → ranking metadata change without eligibility change.

### Provider adapter tests

Bedrock:

- request mapping;
- timeout/retry classification;
- invalid JSON/schema;
- unknown/provider error;
- redacted logs.

Typesense:

- collection/document mapping;
- idempotent upsert/delete;
- missing-document delete;
- timeout/retry;
- query allowlist;
- reconciliation.

### Idempotency/concurrency tests

- repeated Search refresh requests;
- duplicate domain events;
- two workers processing same entity;
- two reviewers deciding same AI suggestion;
- concurrent taxonomy edits;
- backfill/live-update overlap.

### Compliance/privacy tests

- raw resume text never enters Search;
- exact location never enters public projection;
- AI private candidate input blocked without owner permission;
- moderation/Privacy decisions remove provider documents;
- Search does not substitute TrustBadge for verification;
- Track boost never exposes ineligible record;
- Audit and Ops records remain distinct.

### Critical E2E Cluster workflows

1. admin creates taxonomy term → public taxonomy query → Search taxonomy projection;
2. manual accepted classification → source refresh → public result facet;
3. AI suggestion generation → review → accepted classification → search update;
4. eligible entity appears → source becomes hidden → entity disappears from search;
5. privacy instruction removes a Search projection;
6. authorized organization performs candidate search using Candidate-owned projection; unauthorized actor is denied.

---

## 24. Invariants

### Rules coding agents must never violate

1. CL-02 is a coordination boundary, not a lifecycle owner.
2. `TaxonomyDomain`, `TaxonomyCategory`, and `TaxonomyTag` remain Taxonomy & Classification truth.
3. Do not build taxonomy join repositories until the join-owner ruling is approved.
4. Do not create two services that both mutate the same taxonomy join.
5. AI output is never accepted taxonomy merely because provider validation succeeded.
6. `AiSuggestion` is proposal truth; it is not `TaxonomyTag`, a join, or a Search document.
7. `AiClassificationLog` is model-run truth; it is not `AuditEvent` or `IntegrationFailure`.
8. AI Taxonomy must not directly mutate accepted taxonomy or Typesense.
9. Taxonomy & Classification must not instantiate a Bedrock client.
10. Search / Public Visibility must not invoke the AI model during indexing/reconciliation.
11. Search documents are rebuildable projections and never source business truth.
12. No source lifecycle transition may be inferred from a search result or missing search document.
13. `SearchUpsertEvent` belongs to Search, not Audit or Observability.
14. Consumers call SH-091; they do not write Typesense directly.
15. Search consumes owner-safe SH-094 projections instead of importing foreign repositories by default.
16. Search consumes owner-issued SH-024 readiness decisions instead of building one universal business-readiness engine.
17. Search ranking/boost cannot make an otherwise ineligible entity public.
18. Track Subscription & Entitlement remains the source of commercial boost/access truth.
19. TrustBadge may be displayed/ranked but does not prove verification completion.
20. Taxonomy triggers compliance requirements but does not approve verification, healthcare, license, location, or employment compliance.
21. `TagSource.ai` is provenance only.
22. The meaning of tag-join `verified` and `confidence` must not be guessed.
23. Candidate search must use Candidate-owned privacy-safe projection truth.
24. Raw resume text, private applications, PHI, private messages, and identity documents must not enter Search provider documents under current architecture.
25. AI may receive sensitive candidate data only when the source/privacy owner explicitly permits the minimized data for that classification purpose.
26. AI classification must not rank, reject, shortlist, or hire candidates.
27. Public location uses Location Safety-approved fuzzy projection only.
28. Moderation owns the moderation decision; Search executes provider removal/restore.
29. Privacy owns PrivacyRequest/erasure orchestration; CL-02 only executes against owned records/projections.
30. `ComplianceHold` is the reusable stop sign; no local generic blocked system.
31. Audit evidence does not replace taxonomy, AI, or Search lifecycle truth.
32. Observability does not replace business/projection truth.
33. Provider status/payloads do not become domain truth.
34. Bedrock and Typesense access stays behind the owning Module adapter.
35. Every asynchronous side effect must be idempotent, retry-classified, observable, and safe under duplicate delivery.
36. A dead-lettered Search job must remain visible as unresolved work; it must not be silently marked processed.
37. Search reconciliation must converge to current source truth, not replay stale event payloads as authority.
38. No generic “any entity” repository may be created to simplify CL-02.
39. Shared operations must be referenced by canonical SH IDs/names rather than reimplemented under local aliases.
40. Unresolved ownership/privacy/legal questions must remain gated rather than receiving permissive defaults.

---

## 25. Prohibited Duplicate Implementations

Coding agents must not create:

- `taxonomyService` inside Marketplace, Hiring, Candidate, Search, or AI that owns a copied category/tag catalog;
- independent `normalizeTag.ts`, `slugifyTaxonomy.ts`, or tag-collision policy outside Taxonomy when SH-079/Taxonomy policy applies;
- `bedrockService.ts` in Taxonomy, Marketplace, Search, or Hiring for taxonomy/classification suggestions;
- multiple Bedrock clients with different prompt/output validation rules for the same AI Taxonomy capability;
- `typesenseService.ts`, `searchIndexer.ts`, `searchSync.ts`, or `deindexEntity.ts` outside Search / Public Visibility;
- direct Typesense writes from Moderation, Privacy, Taxonomy, Track, Marketplace, Hiring, or Candidate Modules;
- a second Search projection queue or module-local `SearchUpsertEvent` replacement;
- a generic `searchEligibilityService` that reproduces Professional Eligibility, Job Compliance, Candidate privacy, verification, healthcare, moderation, hold, or Track policy;
- local `isPremium`, `canBoost`, `isSearchBoosted`, or equivalent commercial-policy booleans;
- local `verificationPassed` logic based on `TrustBadge`;
- Search-owned `CandidateSearchProjection` or resume parser;
- a `rawResumeSearchIndexer`;
- local coordinate fuzzing in Search;
- a CL-02 `PrivacyRequest`/`ErasureJob` subsystem;
- a CL-02 moderation case/decision subsystem;
- a CL-02 generic compliance-block table;
- `aiAuditLog` standing in for `AiClassificationLog` or `AuditEvent`;
- feature-local audit tables or logger wrappers that duplicate SH-029/032–038;
- feature-local idempotency, retry, queue, outbox, or locking frameworks;
- a polymorphic `AnyEntityRepository` giving Taxonomy/Search direct CRUD over Offering/Gig/Job/Profile/Organization records;
- two repositories/services that can mutate the same taxonomy join row.

---

## 26. Deferred / Unresolved Decisions

| ID | Question | Why unresolved | Missing evidence / decision | What it blocks |
|---|---|---|---|---|
| `U-CL02-01` | Who owns create/update/delete lifecycle for each taxonomy join? | Registry and glossary/entity Modules conflict | explicit one-owner ruling per join | join repositories; accepted entity-classification mutation |
| `U-CL02-02` | What do tag-join `verified` and `confidence` mean, and what confidence scale/source is valid? | Prisma fields exist without canonical semantics | Taxonomy semantic ruling | safe use of join metadata; AI confidence snapshot |
| `U-CL02-03` | Should `TagSource.candidate` exist, and what provenance should candidate-authored tags use now? | Prisma comments it out; candidate joins exist | product/taxonomy provenance decision | candidate self-tagging provenance |
| `U-CL02-04` | What exact Prisma models/enums define `AiSuggestion` and `AiClassificationLog`, including run/suggestion statuses? | Canonical records are absent from Prisma | approved AI schema/lifecycle contract | AI persistence, production worker/review |
| `U-CL02-05` | How does Taxonomy accept/reject an AI proposal and AI record disposition without split ownership or a dual write? | final acceptance is Taxonomy-owned while proposal record is AI-owned | workflow/event/command contract + atomicity/idempotency rule | end-to-end AI acceptance |
| `U-CL02-06` | Can Tags independently trigger healthcare, sensitivity, or location rules, and who owns `DataSensitivity` evolution? | registry/glossary exceed current Tag fields; shared enum ownership unclear | schema/policy ruling | tag-level trigger behavior; migrations |
| `U-CL02-07` | What is taxonomy hard-delete, parent-inactive, merge/alias, history/version policy? | current `isActive` and destructive cascades are insufficiently specified | lifecycle/history decision | destructive admin commands; term merge/backfill |
| `U-CL02-08` | Is PR-CL02-03 refresh semantics for current `SearchUpsertEvent` approved, or does Search need richer persistent projection-work state? | current schema is minimal; canonical operation is “refresh” | explicit queue-semantics ruling | production Search worker/debug semantics |
| `U-CL02-09` | What are Typesense collection boundaries, document versions, ranking weights, query facets/sorts, and public vs protected collection topology? | technology named; exact provider schema absent | Search projection/query ADR | provider schema commitment and ranking tuning |
| `U-CL02-10` | What exact Organization authority, Candidate privacy, and Track entitlement contract gates protected candidate search? | source owners are known, composite policy contract is not | CL-01/CL-06 public-interface agreement | production candidate search |
| `U-CL02-11` | What AI-log/suggestion retention, erasure, provider-retention/deletion policy applies to personal/sensitive data? | privacy boundary known; retention/provider behavior not specified | Privacy/legal/provider decision | production AI retention and sensitive classification |
| `U-CL02-12` | Is SH-065 model invocation definitively owned/implemented inside AI Taxonomy or broader AI infrastructure? | canonical shared registry marks it Proposed | architecture approval | long-term provider adapter placement; does not block contract fake |
| `U-CL02-13` | What canonical domain event vocabulary/versioning is required for taxonomy/AI changes? | no event schema is confirmed | event contract ADR | external asynchronous consumers; can use direct SH-091 command in early slices |
| `U-CL02-14` | Are Gigs an AI Taxonomy classification target? | Cluster registry names Gig as inbound; AI Module registry omits Gig | product/module-scope decision | AI Gig suggestion feature only |
| `U-CL02-15` | Can AI propose brand-new taxonomy terms, and what review/normalization path creates them? | AI can output novel phrases but Taxonomy controls vocabulary | Taxonomy/AI review policy | novel-term creation; existing-term suggestions can proceed |
| `U-CL02-16` | Are `SearchEntityType.user` documents ever public, and what User-safe projection would exist? | enum includes `user`; no public User projection policy is established | Identity/privacy/search ruling | User indexing; default remains disabled |

### Decisions that do not block the first vertical slice

The following can remain unresolved while the Cluster proves taxonomy read/admin behavior:

- protected candidate Search topology;
- AI provider live credentials;
- AI novel-term creation;
- Gig AI classification scope;
- final relevance weights.

### Decisions that block production behavior

Do not implement or activate:

- taxonomy join mutation before `U-CL02-01/02`;
- AI persistence/provider production flow before `U-CL02-04`;
- AI acceptance before `U-CL02-01/04/05`;
- tag-level healthcare/location behavior before `U-CL02-06`;
- hard delete/merge before `U-CL02-07`;
- production Search worker before `U-CL02-08` is resolved;
- protected candidate Search before `U-CL02-10`;
- sensitive personal-data AI production use before `U-CL02-11`;
- User indexing before `U-CL02-16`.

---

## 27. Architecture Decision Summary

### Confirmed binding rulings

1. CL-02 coordinates `taxonomy_classification`, `ai_taxonomy`, and `search_public_visibility`; the Cluster itself owns no lifecycle.
2. Taxonomy & Classification owns canonical Domain/Category/Tag vocabulary, hierarchy, normalization policy, accepted classification semantics, and classification-trigger interpretation.
3. AI Taxonomy owns AI proposal/run truth; AI output is never accepted platform truth by itself.
4. Search / Public Visibility owns `SearchUpsertEvent`, `SearchEntityType`, provider projection mechanics, and discovery query behavior.
5. Search is derived projection and must be rebuildable from owner-approved source truth.
6. `CandidateSearchProjection` remains Candidate Application & Resume Privacy truth.
7. Candidate discovery must not index raw resumes/private applications and must honor privacy/organization access.
8. Taxonomy triggers requirements but does not approve compliance.
9. TrustBadge is display/ranking signal only; verification truth remains with Trust Verification.
10. Track owns commercial boost/feature entitlement; Search only applies the resulting allowed effect.
11. Location Safety owns fuzzy/exact location policy.
12. Moderation decides hide/restore; Search executes de-index/re-index.
13. Privacy owns privacy orchestration; AI/Search execute their target effects.
14. Audit and Observability supplement but do not replace CL-02 domain truth.
15. Bedrock and Typesense stay behind owner adapters; provider state is not domain truth.
16. Canonical Shared Operations Registry is binding anti-duplication guidance.

### Proposed rulings requiring approval before dependent implementation

**PR-CL02-01 — Taxonomy join split:** contextual entity Module owns its join-row lifecycle; Taxonomy owns validation/semantics.

**PR-CL02-02 — AI disposition split:** AI owns proposal record transitions; Taxonomy owns the classification acceptance decision and accepted classification mutation; Taxonomy acknowledges its decision to AI through a public contract/event.

**PR-CL02-03 — Search refresh semantics:** `SearchUpsertEvent` is interpreted as “refresh this entity to current source truth,” with provider upsert **or delete** chosen at execution time; generic queue infrastructure owns attempts/retries/dead-letter telemetry.

**PR-CL02-04 — Search source-contract rule:** every searchable source exposes SH-094 plus SH-024/owner readiness instead of granting Search direct foreign repository access. This is strongly supported by the canonical registry and should be treated as the implementation default.

**PR-CL02-05 — AI novel terms:** initial MVP AI acceptance should prefer existing canonical term IDs; model-proposed brand-new terms remain review-only until `U-CL02-15` defines controlled creation, dedupe, hierarchy placement, and activation.

---

## 28. Coding-Agent Usage

Before changing CL-02, an implementation agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. `context/shared/shared-operations.md`;
5. this Cluster `architecture.md`;
6. this Cluster `build-plan.md`;
7. the target Module architecture;
8. the target Module implementation plan;
9. relevant dependency Module public-interface sections;
10. `progress-tracker.md`.

The agent must then:

- identify the authoritative owner of every record it will read or write;
- identify every unresolved `U-CL02-*` decision touched by the feature;
- confirm any Proposed Ruling used by the feature has been approved before committing schema/API semantics;
- list the SH operations consumed;
- verify no duplicate helper/service/provider adapter is being introduced;
- keep foreign source reads behind owner contracts;
- preserve source/proposal/projection distinctions;
- update this architecture only when a binding architecture decision legitimately changes;
- never use progress or implementation convenience to silently change ownership.

