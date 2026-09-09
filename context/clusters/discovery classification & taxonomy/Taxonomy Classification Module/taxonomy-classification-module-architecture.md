# Taxonomy & Classification Module Architecture

> **Module ID:** `taxonomy_classification`  
> **Module name:** Taxonomy & Classification Module  
> **Module type:** `capability`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-02 — Discovery, Classification & Visibility`  
> **Repository target:** `context/modules/taxonomy_classification/module-architecture.md`  
> **Document status:** implementation-grade target architecture, subordinate to root and CL-02 architecture  
> **Audience:** coding agents, developers, reviewers, maintainers, security/compliance reviewers, and architecture reviewers  
> **Update rule:** update this file only when a binding taxonomy ownership, lifecycle, public-contract, trigger-policy, privacy, search-handoff, or cross-Module decision changes. Build progress must not silently redefine this architecture.

## Evidence and ruling legend

This architecture is grounded in the supplied Workin Ants Project Overview, Deep Module Registry, Cluster Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Architecture, the prior Taxonomy & Classification Module Architecture Extract, and the directly dependent AI Taxonomy and Search / Public Visibility extracts. The root Workin Ants build plan places this Module in Phase 4, **Taxonomy, AI Suggestions, and Search Projection**.

A dedicated CL-02 `architecture.md` / `build-plan.md` was not located among the supplied or available project artifacts during this synthesis. Therefore this Module inherits CL-02 decisions directly from the Cluster Registry and root build-plan Phase 4 until a dedicated CL-02 pair exists. If a later CL-02 architecture conflicts with this document, the stronger root/Cluster ruling controls and this file must be reconciled.

Labels used below:

- **Confirmed** — directly supported by current schema, registry, glossary/compliance evidence, canonical Shared Operations, or repeated Module evidence.
- **Proposed Ruling** — required to make implementation safe and coherent, strongly supported by evidence, but not yet established as final across all sources.
- **Unresolved** — the evidence establishes a real conflict or missing decision and implementation must not guess.

---

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `taxonomy_classification` |
| Module name | Taxonomy & Classification Module |
| Module type | `capability` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-02 — Discovery, Classification & Visibility` |
| Document status | Target Module architecture for MVP implementation |
| Intended audience | Coding agents, developers, reviewers, maintainers, security/compliance reviewers |
| Relationship to root architecture | Subordinate; root architecture controls platform-wide ownership, infrastructure, security, privacy, and shared-operation rules |
| Relationship to Cluster architecture | Subordinate to CL-02. Until a dedicated CL-02 architecture is available, Cluster Registry + root build-plan Phase 4 are the governing CL-02 coordination evidence |
| Update rule | Change only for a binding architecture decision; progress or implementation convenience is not an architecture change |

---

## 2. Purpose, Goal, and Transformation

### Purpose

Maintain the controlled Workin Ants **Domain → Category → Tag** vocabulary and the semantic rules by which platform entities are classified against that vocabulary.

### Goal

Produce consistent, accepted, reusable classification truth that Search, Marketplace Supply, Gig / Demand, Organization Hiring, Candidate Application, Professional Eligibility, Healthcare, Trust Verification, and AI-assisted classification workflows can consume without inventing local tags, local category hierarchies, or local compliance-trigger logic.

### What enters

- administrator requests to create, edit, activate, or deactivate controlled terms;
- raw term text requiring canonical normalization;
- entity classification facts supplied through owner interfaces;
- requests to validate a Domain/Category/Tag assignment;
- requests to translate accepted classification into requirement triggers;
- approved AI suggestion references from AI Taxonomy;
- seed/reference-data definitions;
- backfill/normalization work requests;
- search-refresh intent after accepted taxonomy truth changes.

### What leaves

- canonical `TaxonomyDomain`, `TaxonomyCategory`, and `TaxonomyTag` records;
- active taxonomy trees and term details;
- normalized controlled-term results;
- validated classification paths and stable validation reason codes;
- classification-trigger / requirement results that identify the owning downstream Module without claiming downstream readiness;
- accepted AI-to-taxonomy mutations through SH-121;
- versioned/minimized taxonomy domain events where needed;
- controlled requests to Search via SH-091;
- audit and operational effects through canonical shared interfaces.

### Capability transformation

```text
raw or proposed classification
→ canonical normalization
→ hierarchy/active-status validation
→ accepted taxonomy truth
→ validated entity-assignment semantics
→ downstream requirement trigger facts
→ search-refresh/event handoff
```

### Why this is its own Module boundary

Controlled vocabulary and classification semantics are reused across otherwise independent business domains. If Marketplace, Hiring, Gigs, Search, Healthcare, Verification, or AI each owned their own tag cleaners, category trees, or trigger rules, Workin Ants would immediately acquire conflicting classification truth. This Module therefore owns the canonical vocabulary and classification policy while deliberately not owning the business lifecycles that consume it.

---

## 3. Owned Truth

### 3.1 Confirmed canonical source truth

| Record / policy | Ownership | Plain-English meaning |
| --- | --- | --- |
| `TaxonomyDomain` | **Confirmed** | Highest-level controlled classification — the broad aisle in which Categories live. |
| `TaxonomyCategory` | **Confirmed** | Middle classification level inside one Domain. It can carry classification-trigger metadata such as verification, healthcare sensitivity, and data sensitivity. |
| `TaxonomyTag` | **Confirmed** | Lowest, most-specific controlled term under one Category. |
| `TagSource` | **Confirmed** | Provenance vocabulary describing who or what supplied a tag assignment (`user`, `professional`, `organization`, `ai`, `admin`, `system`; candidate provenance remains unresolved). |
| Taxonomy hierarchy | **Confirmed** | Category-to-Domain and Tag-to-Category relationships and their validity. |
| Canonical naming / normalization policy | **Confirmed responsibility** | The rules that prevent equivalent casing, punctuation, whitespace, Unicode, or spelling forms from producing uncontrolled vocabulary sprawl. Exact versioned rules are an implementation decision. |
| Classification validity policy | **Confirmed** | Whether a proposed Domain/Category/Tag path is canonical, active, hierarchical, and compatible with the supported assignment context. |
| Classification-trigger interpretation | **Confirmed** | Translation from accepted classification metadata to requirement *triggers*. Taxonomy does not decide whether the downstream requirement is satisfied. |
| Taxonomy administration policy | **Confirmed** | Which taxonomy fields may change and what safe effects a term activation/deactivation/update has. |

### 3.2 Join records — ownership conflict

The Deep Module Registry claims these records for Taxonomy:

- `ProfessionalCategory`
- `ProfessionalTag`
- `CandidateCategory`
- `CandidateTag`
- `OrganizationCategory`
- `OrganizationTag`
- `OfferingTag`
- `GigTag`
- `JobTag`

However, the Ubiquitous Language / shared-schema rules also state that Taxonomy owns **controlled vocabulary and classification semantics while entity Modules own the lifecycle of the entity using the join**, and several contextual Modules also claim their corresponding joins.

**Proposed Ruling PR-TAX-01 — contextual join lifecycle:** the contextual entity owner should own create/remove lifecycle and repository access for its classification join rows, while every assignment must use Taxonomy's public validation policy (SH-023) and canonical `TagSource` semantics. This avoids Taxonomy becoming a cross-domain repository for ProfessionalProfile, CandidateProfile, Organization, Offering, Gig, and Job lifecycles.

This ruling is strongly supported but not yet fully reconciled with the Registry's schema-ownership list. **No production join repository or assignment command may be implemented until PR-TAX-01 is approved or replaced.** The Module may implement SH-023 and owner-facing classification contracts first.

### 3.3 Enums and statuses

- **Owned:** `TagSource` semantic vocabulary.
- **Not a dedicated lifecycle enum:** Domain, Category, and Tag currently use `isActive: Boolean`.
- Tag joins currently contain `verified: Boolean` and `confidence: Float?`; their complete semantics are **not defined**.
- `DataSensitivity` is consumed by `TaxonomyCategory` but its semantic owner is not conclusively established by the supplied taxonomy evidence. Taxonomy must not claim platform-wide ownership of that enum merely because it stores a value.

### 3.4 Source-of-truth records

- Vocabulary truth: Domain / Category / Tag records.
- Hierarchy truth: `TaxonomyCategory.domainId`, `TaxonomyTag.categoryId`.
- Trigger truth: fields actually modeled on Category/Tag plus approved requirement bindings elsewhere.
- Classification attachment truth: the applicable join record plus direct `domainId` / `categoryId` on entities that model those fields, with join-row owner subject to PR-TAX-01.
- Tag provenance: join `source`, `confidence`, `verified`, `createdAt`, but `verified`/`confidence` interpretation remains constrained by Section 35.

### 3.5 Domain events / ledgers

No taxonomy-specific change ledger exists in the supplied Prisma schema. Generic `AuditEvent` is not taxonomy truth. If taxonomy change events are needed, they use SH-046 transactional outbox infrastructure; no new generic taxonomy audit table is implied.

### 3.6 Projections and snapshots

- Taxonomy owns no Typesense/search projection.
- Search owns `SearchUpsertEvent` and search-provider documents.
- Taxonomy may expose SH-094 `buildSourceProjection` for a safe taxonomy term projection if Search requires it.
- Historical consumers snapshot taxonomy inputs through their own records/patterns (for example SH-109/SH-110). Taxonomy does not become a universal historical-decision ledger.

### 3.7 Module-owned invariants

1. A Category belongs to exactly one Domain.
2. A Tag belongs to exactly one Category.
3. Domain name and slug are globally unique under current schema.
4. Category name/slug are unique within a Domain.
5. Tag name/slug are unique within a Category.
6. New accepted classifications cannot use an effectively inactive path.
7. When a target stores both `domainId` and `categoryId`, the Category must belong to that Domain.
8. AI provenance is not acceptance, verification, or readiness proof.
9. Trigger metadata means “this classification requires another check,” not “the check passed.”
10. Taxonomy does not write Search, Verification, Healthcare, Location, or business-lifecycle truth directly.

---

## 4. Explicit Non-Ownership

This Module must not own or recreate:

| Adjacent owner | Responsibility that stays outside Taxonomy |
| --- | --- |
| **AI Taxonomy** | Bedrock/foundation-model calls, prompt/model versions, `AiSuggestion`, `AiClassificationLog`, confidence-generation logic, backfill suggestion generation. |
| **Search / Public Visibility** | `SearchUpsertEvent`, Typesense client, index schemas, ranking, public/private visibility policy, indexing/de-indexing workers, search reconciliation/backfill. |
| **Marketplace Supply** | Offering lifecycle, publish state, pricing, supply readiness, and—subject to PR-TAX-01—Offering classification-join lifecycle. |
| **Gig / Demand** | Gig lifecycle and—subject to PR-TAX-01—Gig classification-join lifecycle. |
| **Organization Hiring** | Organization and Job lifecycle, organization membership, Job publication, and contextual organization/job assignment lifecycle. |
| **Candidate Application & Resume Privacy** | CandidateProfile/application/resume lifecycle, candidate privacy, and contextual candidate classification attachment lifecycle. |
| **Professional Eligibility** | ProfessionalProfile lifecycle/readiness and professional selling eligibility. |
| **Trust Verification / Screening** | `VerificationRequirement`, `VerificationCheck`, credential/license/background-check truth, verification readiness, adverse-action workflows. |
| **Healthcare / Regulated Services** | `HealthcareComplianceProfile`, BAA/provider readiness, healthcare data boundaries, healthcare readiness. |
| **Location Safety** | exact/fuzzy location, reveal policy, location readiness. |
| **Role / Authority** | permission interpretation and reusable authorization infrastructure. |
| **Identity & Access** | authentication/session/actor truth. |
| **Audit / Event Ledger** | generic `AuditEvent` and `AccessAuditLog`. |
| **Privacy / Data Erasure** | privacy request/job orchestration, retention exemption lifecycle, cross-service erasure completion. |
| **Observability / Ops** | `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident`, generic logging/metrics/incident truth. |
| **Notification** | delivery persistence, recipients/channels, provider dispatch. No notification need is currently confirmed for normal taxonomy administration. |

Taxonomy must also never become a generic “compliance engine.” It identifies classification triggers; the action-owning Module composes actual readiness decisions.

---

## 5. Module Architecture Principles

1. **Accepted vocabulary is centralized.** Consumers use canonical IDs and Taxonomy contracts, not feature-local strings or copied lookup tables.
2. **Classification validation precedes contextual attachment.** No owner may persist a new taxonomy assignment without SH-023 semantics.
3. **Business lifecycle remains external.** Taxonomy can say a classification is valid; it cannot publish an Offering, activate a Professional, approve a Job, or allow a Gig.
4. **Triggers are not approvals.** `verificationRequired`, `requiresHealthcareCompliance`, and sensitivity values are inputs to downstream gates.
5. **No direct provider clients.** Bedrock belongs behind AI Taxonomy/shared AI adapter; Typesense belongs behind Search.
6. **No hard delete through normal Module commands.** See PR-TAX-02 in Section 9.
7. **Effective activity follows ancestry.** See PR-TAX-03.
8. **No silent join ownership.** PR-TAX-01 must be settled before assignment repositories are built.
9. **No ambiguous `verified` interpretation.** It must never mean `VerificationCheck` passed.
10. **No cross-Module Prisma repository shortcuts.** Cross-Module target facts use SH-123 or the owner’s public interface.
11. **Search refresh is a command to Search, never a write to `SearchUpsertEvent`.**
12. **Shared infrastructure remains shared.** Idempotency, locking, queue, audit, logging, events, and privacy orchestration are consumed by ID.

---

## 6. Proposed Folder / Code Structure

Use the root Workin Ants server/module convention. If the repository later standardizes a `src/` prefix, preserve these boundaries under that prefix rather than changing ownership.

```text
server/modules/taxonomy-classification/
├── contracts/
│   ├── taxonomy-public.types.ts
│   ├── taxonomy-errors.ts
│   ├── taxonomy-events.ts
│   └── taxonomy-owner-facts.ts
├── schemas/
│   ├── taxonomy-command.schemas.ts
│   └── taxonomy-query.schemas.ts
├── commands/
│   ├── domain.commands.ts
│   ├── category.commands.ts
│   ├── tag.commands.ts
│   └── apply-ai-suggestion.command.ts
├── queries/
│   ├── taxonomy-tree.query.ts
│   ├── taxonomy-term.query.ts
│   ├── taxonomy-vocabulary.query.ts
│   ├── validate-taxonomy-assignment.query.ts
│   └── resolve-taxonomy-requirements.query.ts
├── domain/
│   ├── normalization.ts
│   ├── hierarchy.ts
│   ├── effective-activity.ts
│   └── requirement-triggers.ts
├── policies/
│   ├── taxonomy-admin.policy.ts
│   ├── assignment-compatibility.policy.ts
│   └── term-mutation.policy.ts
├── repositories/
│   ├── taxonomy-domain.repository.ts
│   ├── taxonomy-category.repository.ts
│   └── taxonomy-tag.repository.ts
├── services/
│   ├── taxonomy-management.service.ts
│   └── taxonomy-classification.service.ts
├── events/
│   └── taxonomy-event-builder.ts
├── workers/
│   ├── normalize-taxonomy.worker.ts
│   └── taxonomy-impact-refresh.worker.ts   # only after fan-out policy is settled
├── privacy/
│   └── taxonomy-privacy-executor.ts        # only if owner inventory requires it
└── index.ts

app/admin/settings/reference-data/taxonomy/
├── page.tsx
├── loading.tsx
└── _components/
    ├── taxonomy-tree.tsx
    ├── taxonomy-term-form.tsx
    └── taxonomy-status-control.tsx

tests/modules/taxonomy-classification/
tests/integration/taxonomy-classification/
```

### Folder constraints

- Do **not** create `providers/`; this Module owns no external provider.
- Do **not** create `search/`, `typesense/`, `bedrock/`, `auth/`, `permissions/`, `audit/`, or `queue/` infrastructure under this Module.
- Do **not** create classification-join repositories until PR-TAX-01 is resolved.
- The admin route is a thin delivery surface. It delegates to Module commands/queries and never embeds taxonomy policy in React components or route handlers.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / admin UI | Forms, hierarchy browser, command invocation, safe errors | business rules, direct Prisma writes, role interpretation, search/AI provider calls |
| Application services | orchestration of taxonomy commands/queries and shared-operation calls | generic auth/idempotency/queue/audit implementations |
| Domain policy | hierarchy, effective-active, normalization, mutation policy, assignment compatibility, requirement trigger interpretation | healthcare/verification readiness, business lifecycle decisions |
| Repositories | only Domain/Category/Tag source-truth persistence; joins only if PR-TAX-01 later assigns them here | repositories for Offering/Gig/Job/Profile/Organization or Search/Ai tables |
| Workers | taxonomy normalization/backfill and approved impact enumeration | generic queue mechanics, AI generation, Search indexing |
| Adapters | none required for external providers | Bedrock, Typesense, healthcare, verification, or notification provider clients |
| Contracts | stable taxonomy public DTOs, reason codes, source-projection DTO | foreign Module internal models/provider payloads |
| Privacy | execute owner-specific Privacy instructions only for records actually owned here | privacy request orchestration or global data discovery |

---

## 8. Data Model

### `TaxonomyDomain`

**Purpose:** top-level canonical classification.

**Authoritative fields:** `id`, `name`, `slug`, `description`, `displayOrder`, `isActive`, timestamps.

**Important relationships:** parent of Categories; referenced by Offerings, Gigs, Jobs.

**Constraints:** `name` unique; `slug` unique; indexed `isActive`.

**Concurrency:** create/update conflicts can race on name/slug and ordering; database uniqueness is authoritative. Admin edits should use SH-052 with expected `updatedAt` until a dedicated version column is approved.

**Retention/privacy:** reference data is not person-subject data by design. Normal administrative deletion is prohibited; historical business records may depend on IDs.

### `TaxonomyCategory`

**Purpose:** controlled classification inside one Domain and source of modeled classification-trigger metadata.

**Authoritative fields:** `domainId`, `name`, `slug`, `description`, `icon`, `displayOrder`, `isActive`, `verificationRequired`, `requiresHealthcareCompliance`, `dataSensitivity`, timestamps.

**Constraints:** unique `(domainId, slug)` and `(domainId, name)`; parent FK currently cascades on hard Domain delete.

**Concurrency:** sibling uniqueness and parent lifecycle changes are transaction-sensitive.

**Retention/privacy:** same reference-data rule as Domain. Hard deletion could erase child Tags and classifications and is therefore not an application command.

### `TaxonomyTag`

**Purpose:** most-specific controlled classification under one Category.

**Authoritative fields:** `categoryId`, `name`, `slug`, `description`, `displayOrder`, `isActive`, `verificationRequired`, timestamps.

**Constraints:** unique `(categoryId, slug)` and `(categoryId, name)`; parent FK currently cascades on Category hard delete.

**Important mismatch:** current schema does **not** model healthcare or `dataSensitivity` on Tag even though registry prose says Category or Tag may trigger a wider family of requirements. The implementation must only return triggers supported by actual fields/bindings.

### Taxonomy category joins

`ProfessionalCategory`, `CandidateCategory`, `OrganizationCategory` are composite-key relationships to a Category. Their exact repository/lifecycle owner is unresolved under PR-TAX-01.

### Taxonomy tag joins

`ProfessionalTag`, `CandidateTag`, `OrganizationTag`, `OfferingTag`, `GigTag`, and `JobTag` use composite target/tag keys and record:

- `source: TagSource`;
- `confidence: Float?`;
- `verified: Boolean`;
- `createdAt`.

**Critical semantic constraint:** `verified` must not be exposed or interpreted as credential/license/background-check verification. `VerificationCheck` remains Trust Verification truth.

### Direct Domain/Category references

Offering, Gig, and Job each have required `domainId` and optional `categoryId`. Current relational constraints do not guarantee that the selected Category belongs to the selected Domain. SH-023 must enforce this invariant on writes and publication/readiness checks.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Domain / Category / Tag lifecycle

Current schema supports only active/inactive state:

```text
create
  ↓
active ⇄ inactive
```

There is no confirmed draft, retired, merged, or archived enum.

**Transition owner:** Taxonomy & Classification for Domain/Category/Tag.

**Triggers:** authorized admin commands; approved normalization/merge workflow where later supported.

**Terminal states:** none in current boolean lifecycle.

**Reversal:** inactive → active is allowed only if parent hierarchy remains valid and uniqueness/collision policy is satisfied.

**Proposed Ruling PR-TAX-02 — no normal hard delete:** normal application services SHALL NOT expose Domain/Category/Tag hard-delete commands in MVP. Deactivation preserves referential and compliance-trigger history. The existing Prisma cascade is a database capability for exceptional migration/erasure administration, not a product lifecycle.

**Proposed Ruling PR-TAX-03 — effective activity:**

```text
Domain effectiveActive = Domain.isActive
Category effectiveActive = Category.isActive && Domain.isActive
Tag effectiveActive = Tag.isActive && Category.isActive && Domain.isActive
```

A child can remain physically `isActive=true` while an ancestor is inactive, but it is not eligible for new accepted assignments until ancestry is effective-active. Reactivating an ancestor restores eligibility without rewriting each child.

### 9.2 Classification attachment lifecycle

No standalone status enum exists. A join row means the accepted attachment exists. Removal means the row is removed by the owning contextual Module, subject to PR-TAX-01.

`TagSource.ai` is provenance only. An AI suggestion is not attached merely because an AI record exists.

### 9.3 `verified` and `confidence`

- `verified` semantics are **Unresolved U-TAX-02**. It cannot mean Trust Verification success.
- `confidence` semantics/range by source are **Unresolved U-TAX-03**. Do not let generic user/admin writers invent scores.
- Until resolved, new public assignment contracts must either omit these fields or accept them only through an explicitly approved source-specific contract.

### 9.4 Prohibited shortcuts

- no `isCategoryValid` or `isHealthcareApproved` booleans stored on consumers as taxonomy truth;
- no hardcoded category IDs in feature code for compliance behavior;
- no `verified=true` to bypass SH-018 / Trust Verification;
- no direct update of an entity's `domainId`/`categoryId` without SH-023 validation.

---

## 10. Commands

### `createTaxonomyDomain`

- **Purpose:** create a canonical top-level Domain.
- **Actor/context:** authenticated admin/system actor via SH-001; authorized via SH-002.
- **Inputs:** name, optional requested slug, description, display order, idempotency key.
- **Preconditions:** normalized value valid; no canonical collision; reserved/slug policy satisfied.
- **Writes:** `TaxonomyDomain`.
- **Shared operations:** SH-079, SH-044, SH-029, SH-046; SH-124 only if the approved generic slug helper is adopted.
- **Effects:** audit; domain event; SH-091 if taxonomy terms are indexed.
- **Idempotency:** semantic key must replay the original created Domain.
- **Failures:** invalid term, duplicate/collision, unauthorized, stale dependency, DB conflict.

### `updateTaxonomyDomain`

Updates presentation/order/canonical fields permitted by policy. Uses SH-052 for stale edits, SH-029 for material change, SH-046, and SH-091. It must not silently rewrite child or business records.

### `setTaxonomyDomainActive`

Sets `isActive`. Deactivation changes effective activity for descendants without bulk rewriting them. It must report impact and trigger approved search/event fan-out. Hard deletion is out of scope.

### `createTaxonomyCategory`

- requires an effective-active parent Domain;
- normalizes canonical text;
- validates modeled trigger metadata;
- writes one Category inside a transaction;
- audits material compliance-trigger fields.

### `updateTaxonomyCategoryPolicy`

Changes permitted Category presentation or trigger metadata. Because verification/healthcare/sensitivity changes can affect downstream readiness/search, the command must publish a minimized taxonomy fact and request approved Search refresh. It does not mutate `HealthcareComplianceProfile` or `VerificationRequirement` directly.

### `setTaxonomyCategoryActive`

Sets Category `isActive`; does not cascade writes to Tags. Effective inactivity is derived. Any impacted entity refresh fan-out follows Section 25 and U-TAX-08.

### `createTaxonomyTag`

Creates canonical Tag under an effective-active Category after normalization and sibling collision checks.

### `updateTaxonomyTag`

Updates allowed Tag fields. Trigger changes are audited and may require downstream projection refresh.

### `setTaxonomyTagActive`

Activates/deactivates one Tag. Deactivation prevents new accepted assignments but does not erase historical joins automatically.

### SH-121 `applyAiSuggestion`

- **Purpose:** convert an administrator-approved AI suggestion into accepted taxonomy truth.
- **Actor/context:** authenticated/authorized reviewer or approved system workflow.
- **Authoritative inputs:** AI suggestion ID/version, target, selected canonical term or proposed new term, reviewer, reason, idempotency key.
- **Preconditions:** AI Taxonomy confirms suggestion/version/provenance; target owner confirms target if an assignment is involved; taxonomy normalization/hierarchy/active rules pass.
- **Writes:** canonical term only when explicitly approved; assignment only after PR-TAX-01 identifies its owner.
- **Shared operations:** SH-121, SH-123, SH-079, SH-023, SH-044, SH-029, SH-046, SH-091.
- **Failure modes:** stale/superseded suggestion, invalid target, canonical collision, inactive hierarchy, unresolved join ownership, duplicate request.
- **Boundary:** Taxonomy never calls Bedrock or writes `AiSuggestion`/`AiClassificationLog`.

### SH-122 `mergeCanonicalRecord` — proposed, not yet production-approved

Only for taxonomy terms after a merge/alias/history policy is approved. It requires SH-051, idempotency, reference migration, compatibility validation, impact counts, rollback/reconciliation, and preserved provenance. No generic `mergeAnyEntity` helper is allowed.

---

## 11. Queries / Decisions

### `listTaxonomyTree`

- **Consumers:** admin UI, Marketplace, Hiring, Gigs, AI Taxonomy, Search, other classification pickers.
- **Input:** active-only flag, optional Domain/Category scope, locale if later supported.
- **Result:** ordered canonical tree with IDs, names/slugs, parent IDs, effective-active state, safe trigger metadata.
- **Truth type:** source truth.
- **Consumer must not infer:** downstream healthcare/verification readiness.

### `getTaxonomyTerm`

Returns one canonical term with parent chain and safe trigger metadata. Inactive terms may require protected/admin query scope.

### `listActiveTaxonomyVocabulary`

Version/snapshot-friendly read for AI Taxonomy and other controlled consumers. It exposes canonical IDs and active hierarchy; it must not expose private consumer data or provider configuration.

### SH-023 `validateTaxonomyAssignment`

- **Consumers:** contextual entity owners before assigning/changing Domain/Category/Tag.
- **Input:** target type/id or owner-provided classification context, Domain ID, Category ID, Tag IDs, requested operation, source.
- **Result:** decision envelope with canonical IDs, effective-active facts, normalized errors, warnings, and source version.
- **Truth type:** taxonomy decision over source truth.
- **Stable reason codes:** at minimum `taxonomy_unknown_domain`, `taxonomy_inactive_domain`, `taxonomy_unknown_category`, `taxonomy_category_not_in_domain`, `taxonomy_inactive_category`, `taxonomy_unknown_tag`, `taxonomy_inactive_tag`, `taxonomy_assignment_incompatible`, `taxonomy_cross_category_policy_unresolved`.
- **Consumer must not infer:** that business publication/eligibility is allowed merely because taxonomy is valid.

### SH-022 `resolveTaxonomyRequirements`

- **Consumers:** Professional Eligibility, Marketplace Supply, Gig / Demand, Organization Hiring, Candidate Application, Search readiness composition, Healthcare/Verification integrations.
- **Input:** accepted canonical Domain/Category/Tag IDs and context.
- **Result:** requirement identifiers/families, owning Module, trigger source, severity/applicability, policy/source version.
- **Truth type:** requirement-trigger decision, not readiness.
- **Modeled initial trigger facts:** Category `verificationRequired`; Category `requiresHealthcareCompliance`; Category `dataSensitivity`; Tag `verificationRequired`; plus approved Trust-owned requirement bindings exposed through a public contract.
- **Consumer must not infer:** `VerificationCheck` passed, healthcare profile is verified, BAA exists, location reveal is allowed, or professional is eligible.

### SH-079 `normalizeControlledTerm`

Returns a canonicalized candidate/match result using Taxonomy policy over the shared text primitive. It may suggest existing terms but does not create them.

### SH-094 `buildSourceProjection`

If Search requires a safe Taxonomy entity projection, this query returns only public/approved term fields and a source version. Search still owns final document schema and execution.

---

## 12. Public Module Interface

### Public commands

- `createTaxonomyDomain`
- `updateTaxonomyDomain`
- `setTaxonomyDomainActive`
- `createTaxonomyCategory`
- `updateTaxonomyCategoryPolicy`
- `setTaxonomyCategoryActive`
- `createTaxonomyTag`
- `updateTaxonomyTag`
- `setTaxonomyTagActive`
- **SH-121 `applyAiSuggestion`**
- assignment commands: **not exposed until PR-TAX-01 is resolved**.

### Public queries

- `listTaxonomyTree`
- `getTaxonomyTerm`
- `listActiveTaxonomyVocabulary`
- **SH-023 `validateTaxonomyAssignment`**
- **SH-022 `resolveTaxonomyRequirements`**
- **SH-079 `normalizeControlledTerm`**
- **SH-094 `buildSourceProjection`**, if Search contract requires it.

### Emitted facts / events

**Proposed event vocabulary:**

- `taxonomy.domain.created`
- `taxonomy.domain.updated`
- `taxonomy.domain.activity_changed`
- `taxonomy.category.created`
- `taxonomy.category.updated`
- `taxonomy.category.activity_changed`
- `taxonomy.tag.created`
- `taxonomy.tag.updated`
- `taxonomy.tag.activity_changed`
- `taxonomy.ai_suggestion_applied`

These are facts, not instructions. Search work uses SH-091 rather than a disguised `please_index` event.

### Privacy executor

The Module must register an SH-095-compatible owner executor only for data it actually owns. Canonical term records are reference data and normally do not identify a privacy subject. Join-row privacy handling depends on PR-TAX-01. See Section 28.

### Provider-facing interfaces

None. Taxonomy owns no external provider.

---

## 13. Inbound Dependencies

| Owning Module / capability | Interface consumed | Why needed | Minimum facts | Can block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | admin/reviewer identity | actor ID/type/security context | yes | session/current-user helpers |
| Role / Authority | SH-002 `authorizeResourceAction` | protect admin commands and restricted reads | action, target, owner facts | yes | role tables/permission matrix |
| Target entity owners | SH-123 `validateOwnedTargetReference` / owner-facts DTO | validate cross-Module target before classification | target ID/type, version/status, relationship context | yes | foreign repositories or polymorphic DB lookup |
| AI Taxonomy | suggestion query/decision contract used by SH-121 | prove suggestion/version/provenance | suggestion ID/version, proposed values, target, provenance status | yes for AI acceptance | Bedrock, prompts, run logs |
| Trust Verification | SH-017 `resolveVerificationRequirements` where detailed bindings are required | resolve Trust-owned verification requirement IDs bound to taxonomy | term IDs / scope | yes for detailed requirement result | VerificationRequirement/Check repositories |
| Shared application infrastructure | SH-044/046/047/048/051/052 | reliable writes, events, jobs, concurrency | semantic keys / payloads | yes | local frameworks |
| Audit / Event Ledger | SH-029 | material admin proof | action, actor, target, safe metadata | audit failure handling per platform policy | taxonomyAudit table/helper |
| Search / Public Visibility | SH-091 | request derived projection changes | entity type/id/action/reason/source version | should not roll back committed taxonomy truth after downstream failure; retry via outbox/job | SearchUpsertEvent/Typesense |
| Observability / Ops | SH-032/033/034/036/037/038 | request correlation, safe logs/metrics/failure visibility | IDs, categories, correlation | no business ownership | SystemEvent/IntegrationFailure implementations |
| Privacy / Data Erasure | SH-095/096/097/098 protocol | execute subject-data instructions if applicable | privacy job/target/instruction | yes for privacy executor action | PrivacyRequest/DataErasureJob lifecycle |

No healthcare provider or location provider dependency belongs inside Taxonomy. Those Modules consume trigger facts and own their own readiness.

---

## 14. Outbound Consumers and Effects

### Consumers of taxonomy source truth

- Search / Public Visibility;
- Marketplace Supply;
- Gig / Demand;
- Organization Hiring;
- Candidate Application & Resume Privacy;
- Professional Eligibility;
- Healthcare / Regulated Services;
- Trust Verification / Screening;
- AI Taxonomy.

### Effects

- Source truth changes can publish taxonomy fact events via SH-046.
- Search refresh is requested through SH-091.
- Material admin changes append SH-029 audit proof.
- Worker/integration failures use Ops interfaces.
- No direct mutation of downstream readiness or business status occurs.

### Cross-Module mutation rule

Taxonomy never mutates Offering, Gig, Job, CandidateProfile, ProfessionalProfile, Organization, `VerificationCheck`, `HealthcareComplianceProfile`, `SearchUpsertEvent`, or Privacy workflow records through direct Prisma access. Any permitted cross-Module effect goes through an approved command/interface.

---

## 15. Canonical Shared Operations Used

| ID / name | Classification / owner | Why Taxonomy uses it | Invocation point | Local policy retained here | Expected result | Prohibited duplicates |
| --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | canonical capability — Identity & Access | establish admin/reviewer/system actor | protected commands/admin reads | which operations require actor | typed actor context | `taxonomyAuth.ts`, `getCurrentUser.ts` |
| **SH-002 `authorizeResourceAction`** | canonical capability — Role / Authority | authorize taxonomy administration/review | after actor resolution | taxonomy action vocabulary + target facts | allow/deny/step-up/review decision | `taxonomyPermissions.ts`, `adminGuard.ts` |
| **SH-015 `returnDecisionResult`** | shared contract / separate policy | consistent SH-022/023 decisions | query boundary | taxonomy reason-code namespace | common decision envelope | `taxonomyReadinessResult.ts` fork |
| **SH-017 `resolveVerificationRequirements`** | another Module's public interface — Trust Verification | resolve detailed Trust-owned requirements when bound to classification | SH-022 composition | which classification triggers request expansion | requirement facts, not results | `verificationGate.ts`, direct VerificationRequirement query |
| **SH-022 `resolveTaxonomyRequirements`** | **Taxonomy-owned public interface** | canonical trigger translation | consumer readiness/publication checks | taxonomy trigger semantics | requirement owner/source/severity/applicability | `taxonomyCompliance.ts`, feature-local trigger maps |
| **SH-023 `validateTaxonomyAssignment`** | **Taxonomy-owned public interface** | enforce canonical hierarchy/active/compatibility | every contextual classification mutation | assignment semantics | canonical IDs + stable errors | `validateClassificationPath.ts` in every feature |
| **SH-029 `appendAuditEvent`** | Audit / Event Ledger | material admin action proof | successful or denied sensitive admin actions per root policy | safe taxonomy action metadata | audit acknowledgement/reference | `taxonomyAudit.ts`, `auditLogger.ts` |
| **SH-032 `createRequestContext`** | platform/Ops primitive | correlation | entry points/workers | none | request/correlation context | local request ID generator |
| **SH-033 `writeStructuredLog`** | Observability / Ops | safe logs | commands, workers, contract failures | safe dimensions | structured log | local logger stack |
| **SH-034 `sanitizeTelemetryMetadata`** | Observability/Audit policy | prevent sensitive/oversized telemetry | before logs/audit/ops payload | taxonomy-safe field allowlist | sanitized metadata | custom redaction helpers |
| **SH-036 `emitMetric`** | Observability / Ops | measure command/validation/worker health | service/workers | metric names/dimensions | metric acknowledgement | local metrics client |
| **SH-037 `recordIntegrationFailure`** | Observability / Ops | surface Search/AI-contract/worker integration failures | failed external-Module handoff | taxonomy reference/error category | ops failure reference | `taxonomyIntegrationFailure.ts` |
| **SH-038 `recordQueueTelemetry`** | queue/Ops | worker visibility | normalization/backfill workers | work type/result dimensions | telemetry | private worker dashboard state |
| **SH-044 `executeIdempotentCommand`** | platform primitive | one effect per retried command | create/update/apply-AI jobs | semantic command identity/replay | original result replay | `taxonomyIdempotency.ts` |
| **SH-045 `deduplicateDomainEvent`** | platform event inbox | consume a source event once if event-driven fan-out is added | event consumer | event/handler semantic effect | dedupe acknowledgement | `processedTaxonomyEvent` generic table |
| **SH-046 `publishDomainEvent`** | platform outbox | reliable taxonomy facts | same transaction as source mutation | event names/payload/minimization | durable outbox record | custom event bus/outbox |
| **SH-047 `enqueueReliableJob`** | shared queue | durable normalization/backfill/impact work | post-commit worker dispatch | payload/completion meaning | queued work ref | `taxonomyQueue.ts` |
| **SH-048 `executeRetryWithBackoff`** | shared queue/platform | retry transient work | worker execution | retryable vs terminal errors | retry/dead-letter result | `retry.ts`, `taxonomyRetryWorker.ts` |
| **SH-051 `acquireAggregateLock`** | persistence primitive | serialize merge/high-impact mutations | merge, hierarchy-sensitive bulk operations | lock key/conflict policy | acquired/conflict | in-memory mutex, `taxonomyLock.ts` |
| **SH-052 `withOptimisticConcurrency`** | persistence primitive | stale admin edit protection | updates | expected version/`updatedAt` semantics | success/stale conflict | local compare-and-save helper |
| **SH-053 `transitionLifecycleState`** | shared mechanism / separate truth | consistent active/inactive transition plumbing if adopted | activity commands | allowed taxonomy transition/effects | transitioned state | generic local state machine engine |
| **SH-079 `normalizeControlledTerm`** | **Taxonomy policy over shared text primitive** | canonical controlled-term normalization | create/update/import/AI acceptance | normalization/collision policy | canonical candidate/matches | `slugify.ts`, `tagCleaner.ts`, `skillNormalizer.ts` |
| **SH-091 `requestSearchProjectionRefresh`** | Search public interface | request index/update/hide/remove/restore | accepted taxonomy change | which change warrants refresh, source version | Search-owned request acknowledgement | `typesenseIndexer.ts`, direct SearchUpsertEvent write |
| **SH-094 `buildSourceProjection`** | shared pattern; source owner | expose safe taxonomy source DTO to Search | Search indexing read | safe term fields/version | projection DTO | Search reading taxonomy Prisma directly |
| **SH-095 `executePrivacyInstruction`** | Privacy orchestration / owner executor | apply an owner-specific privacy action if taxonomy owns subject data | privacy target call | disposition for owned records | privacy target result | local privacy job |
| **SH-096 `enumerateSubjectData`** | owner participation in Privacy | report owned subject records | privacy inventory | Taxonomy subject-data definition | record/provider refs | global schema crawler |
| **SH-097 `evaluateRetentionRequirement`** | shared contract / owner facts | tell Privacy whether taxonomy-owned record must be retained | privacy execution | taxonomy retention facts | retention decision facts | local exemption table |
| **SH-098 `anonymizePersonalFields`** | shared mechanism | apply approved anonymization if future owned records contain personal fields | privacy execution | field mapping | anonymized record result | blanket deletion helper |
| **SH-121 `applyAiSuggestion`** | CL-02 public workflow — AI Taxonomy + Taxonomy | convert approved suggestion to accepted truth | reviewer/system acceptance | normalization/hierarchy/final mutation | accepted taxonomy result | `bedrockTaxonomyService.ts`, `acceptSuggestion.ts` bypass |
| **SH-122 `mergeCanonicalRecord`** | Taxonomy internal reusable op — **Proposed** | merge duplicate/retired controlled terms | approved migration/admin workflow | compatibility, target, provenance | merge result/counts | generic merge service |
| **SH-123 `validateOwnedTargetReference`** | target-owner interface | validate foreign target existence/context | any classification association workflow | accepted target types/relationship rules | typed owner facts | `lookupAnyEntity.ts`, foreign Prisma |
| **SH-124 `generateUniqueSlug`** | cross-cutting primitive — Proposed | optional reserved-word/collision-safe slug generation | create/rename when approved | taxonomy slug policy | unique slug/collision | duplicate slug utilities |

---

## 16. Module-Internal Operations

### `computeEffectiveActivity`

- **Input:** Domain/Category/Tag chain.
- **Output:** effective-active state and blocking ancestor.
- **Truth affected:** none.
- **Why local:** taxonomy-specific interpretation of hierarchy activity.

### `validateHierarchyPath`

Ensures Category belongs to Domain and Tag belongs to its canonical Category. Used by SH-023.

### `detectCanonicalCollision`

Uses SH-079 normalized text plus database uniqueness to find an existing canonical sibling. It does not perform fuzzy AI classification.

### `buildTaxonomyImpactSet`

**Conditional operation.** Determines which taxonomy terms and, once join ownership/fan-out is settled, which classified entity IDs are affected by a term change. It returns IDs only; it does not write Search.

### `mapClassificationTriggers`

Maps implemented Category/Tag metadata and approved external requirement bindings to SH-022 requirement results.

### `validateTermMutation`

Protects parent validity, immutable identity constraints, trigger metadata, deactivation behavior, and collision policy before repository writes.

---

## 17. Shared Mechanism / Separate Truth Rules

- **Audit:** use SH-029; `AuditEvent` never replaces Domain/Category/Tag truth or a future taxonomy event history.
- **Lifecycle transitions:** SH-053 may provide transition plumbing; Taxonomy owns active/inactive policy.
- **Concurrency:** SH-051/052 supply DB mechanisms; Taxonomy defines lock keys and conflicts.
- **Idempotency:** SH-044 stores/replays command identity; Taxonomy defines semantic identity.
- **Jobs:** SH-047/048 provide durability/retry; Taxonomy owns normalization/backfill completion meaning.
- **Events:** SH-046 provides outbox; Taxonomy owns event vocabulary/payload meaning.
- **Search projection:** SH-091/094 share mechanism/contracts; Taxonomy truth and Search documents remain separate.
- **Readiness envelope:** SH-015 shapes decisions; Taxonomy owns only assignment validity and trigger policy.
- **Privacy:** Privacy owns request/job orchestration; Taxonomy executes only its owned target instructions.
- **Historical snapshots:** consuming Modules own snapshots of taxonomy inputs used for their historical business/compliance decisions.

---

## 18. Authentication and Authorization

### Authentication

Protected taxonomy administration uses SH-001. Public active-vocabulary reads may be anonymous only if root/CL-02 public-read policy allows it; inactive/internal metadata reads remain protected.

### Authorization

Use SH-002 for:

- create/update Domain;
- activate/deactivate Domain;
- create/update Category and compliance-trigger metadata;
- activate/deactivate Category;
- create/update Tag;
- activate/deactivate Tag;
- review/apply AI suggestion;
- initiate backfill/normalization/merge;
- view inactive/admin-only taxonomy metadata.

Taxonomy supplies action and target facts. Role / Authority decides permission. No Module-local role engine is allowed.

### Proposed action vocabulary

- `taxonomy.domain.create`
- `taxonomy.domain.update`
- `taxonomy.domain.set_active`
- `taxonomy.category.create`
- `taxonomy.category.update`
- `taxonomy.category.set_active`
- `taxonomy.tag.create`
- `taxonomy.tag.update`
- `taxonomy.tag.set_active`
- `taxonomy.ai_suggestion.apply`
- `taxonomy.maintenance.run`
- `taxonomy.merge.execute` — only after SH-122 policy approval.

### Resource ownership / org context

Canonical taxonomy is platform reference data, not owned by an Organization or Profile. Contextual classification writes belong to their contextual Module under PR-TAX-01 and use that owner's authorization facts.

### Step-up

No taxonomy-specific step-up requirement is confirmed. Do not invent MFA. If the root security matrix later classifies high-impact merges or compliance-trigger changes as sensitive, consume SH-014 rather than creating local step-up logic.

---

## 19. Compliance / Readiness / Entitlement Gates

### Taxonomy is a trigger source, not a readiness owner

| Gate family | Underlying truth owner | Taxonomy input | Taxonomy output | Action owner responsibility |
| --- | --- | --- | --- | --- |
| Verification / license / screening | Trust Verification / Screening | `verificationRequired`, accepted term IDs, approved requirement binding | SH-022 requirement trigger + SH-017 references | consumer calls verification readiness and decides its action |
| Healthcare | Healthcare / Regulated Services | Category `requiresHealthcareCompliance`, sensitivity | healthcare-lane trigger | consumer calls healthcare readiness; Taxonomy never reads BAA/provider state directly |
| Data sensitivity | governing sensitivity owner / Healthcare where applicable | Category `dataSensitivity` | sensitivity fact/trigger | consumer applies its own data-boundary/access policy |
| Location | Location Safety | **no complete taxonomy location binding exists** | none until approved representation exists | no feature may hardcode location-trigger category lists |
| Professional eligibility | Professional Eligibility | accepted taxonomy + requirement triggers | no eligibility result | Professional Eligibility composes readiness |
| Entitlement | Track Subscription & Entitlement | none for canonical taxonomy administration | none | Taxonomy does not gate canonical term truth on premium plans |

**Prohibited:** a universal `taxonomyCanPublish()` or `taxonomyCompliancePassed` result.

---

## 20. Provider Integrations

This Module owns **no provider integration**.

Explicit prohibitions:

- no AWS Bedrock client, model configuration, prompt template, or model-run persistence;
- no Typesense client, collection schema, indexing worker, or direct search write;
- no healthcare/vendor, verification/vendor, geocoding, notification, or storage provider clients.

AI Taxonomy uses SH-065/provider infrastructure. Search owns its provider adapter. Taxonomy communicates through public contracts only.

---

## 21. Events and Outbox

### Emission rule

A taxonomy event is emitted only after a source-of-truth change commits, using SH-046 transactional outbox in the same transaction boundary where supported.

### Event envelope

Use the canonical event envelope: event ID/type/schema version, source Module, aggregate type/ID/version, occurredAt, correlation/causation, actor/system context, privacy classification, minimized payload.

### Payload minimization

Prefer IDs, term type, changed field categories, effective-active state, source version, and reason code. Avoid dumping full descriptions or foreign entity data into event payloads.

### Consumer idempotency

Consumers use SH-045 transactional inbox semantics. Taxonomy never assumes exactly-once transport.

### Events are facts

`taxonomy.tag.activity_changed` describes what happened. A Search refresh is explicitly requested through SH-091; do not encode a hidden command inside the event name/payload.

---

## 22. Background Jobs / Scheduled Work

### `normalize-taxonomy` worker

- **Purpose:** bounded review/backfill of canonical normalization inconsistencies.
- **Input:** scoped term IDs/range, normalization-rule version, dry-run/execute mode, idempotency key.
- **Owner:** Taxonomy & Classification.
- **Idempotency key:** rule version + scope + operation mode.
- **Retryable:** transient DB/queue/integration failures.
- **Permanent/manual review:** canonical collision, ambiguous merge, unsupported hierarchy, unresolved join migration.
- **Business truth:** may update a term only under approved mutation rules; otherwise produces review output.
- **Telemetry:** SH-038, safe counts, duration, collision counts.

### `taxonomy-impact-refresh` worker — conditional

If one taxonomy change affects many search projections, a worker may enumerate approved impact IDs and call SH-091 in bounded batches. **U-TAX-08 must be resolved first** because join ownership determines who can enumerate classified entity IDs.

### SH-122 merge worker — conditional

No production merge worker until merge/alias/history semantics are approved. It must use SH-051, SH-044, SH-047/048, dry-run impact preview, reconciliation, and manual-review dead-letter behavior.

### Scheduling

No recurring schedule is intrinsically required by Taxonomy. Root/ops scheduling may trigger approved maintenance jobs; generic scheduler mechanics remain shared.

---

## 23. Concurrency and Idempotency

### Races to prevent

- two admins creating equivalent Domain/Category/Tag siblings;
- concurrent rename causing slug/name collision;
- stale admin edit overwriting new trigger metadata;
- deactivate/reactivate while another command attaches a term;
- AI suggestion acceptance racing with manual creation of the same canonical term;
- merge/backfill racing with term edits or assignments;
- duplicate search-refresh fan-out from retries.

### Strategy

- database unique constraints are authoritative for canonical name/slug identity;
- SH-044 wraps externally retryable commands;
- SH-052 protects admin updates using an approved version token; current `updatedAt` can be used until a dedicated version field is approved;
- SH-051 is required for merge/high-impact mutable aggregates;
- use database transactions, not process-local locks;
- owner assignment commands must validate taxonomy inside or immediately before their own transaction and re-check source version when staleness matters.

### Replay result

A repeated idempotency key with the same fingerprint returns the original success/failure result according to platform policy; the same key with a conflicting fingerprint is rejected.

---

## 24. Media / Storage

Not applicable. Taxonomy owns no `MediaAsset`, file upload, signed URL, scan, or storage lifecycle. An icon field on Category is not permission to create storage infrastructure. If taxonomy visuals later use media, Media / File Access owns bytes and Taxonomy would own only a contextual reference if explicitly modeled.

---

## 25. Search / Projection

### Source truth

Domain/Category/Tag are Taxonomy truth. Search is derived.

### Search-owned truth

- `SearchUpsertEvent`;
- `SearchEntityType` projection vocabulary as defined by Search;
- Typesense documents/collections;
- indexing/de-indexing/reconciliation/backfill.

### Taxonomy-owned source projection

If needed, SH-094 exposes a safe term DTO containing canonical ID/type/name/slug/parent/effective-active/approved facet metadata/source version. It is rebuildable from taxonomy source truth.

### Indexing triggers

Accepted create/update/activity changes may call SH-091 for the taxonomy term itself. Changes that alter classifications, trigger metadata, or facet labels may also require affected entity refresh.

**Unresolved U-TAX-08 — search fan-out ownership:** the system does not yet establish whether Taxonomy or each contextual join owner enumerates affected entity IDs after a Category/Tag change. Until settled:

- Taxonomy may request refresh for its own taxonomy entity;
- contextual join owners must request refresh when they change their own entity classification;
- no Module may directly write `SearchUpsertEvent`;
- no Taxonomy worker may scan foreign business tables as a shortcut.

### What Search must not reconstruct

Search must not infer hierarchy/active rules, taxonomy requirement semantics, or accept AI suggestions on its own. It consumes source facts/contracts.

---

## 26. Notification

No business requirement currently establishes routine user notification for taxonomy changes. Therefore no Notification workflow is part of the Module baseline.

If a future product requirement needs administrator alerts or downstream owner notification, Taxonomy provides the triggering fact and safe variables through SH-041; Notification owns templates, routing, persistence, provider dispatch, retries, and delivery status.

---

## 27. Audit and Sensitive Access

- **Taxonomy domain truth:** Domain/Category/Tag records and any approved taxonomy domain events.
- **Generic audit:** SH-029 `AuditEvent` records material administrative actions such as compliance-trigger changes, deactivation, AI acceptance, backfill execution, or merge.
- **Sensitive access:** SH-030 only if a taxonomy workflow later reads sensitive payloads. Canonical taxonomy terms are not intrinsically sensitive.
- **AccessAuditLog:** never substitute for taxonomy history.
- **Observability:** operational logs/failures remain separate from both taxonomy truth and audit proof.

---

## 28. Privacy and Retention

### Subject-data inventory

Canonical Domain/Category/Tag records are platform reference data and should not contain privacy-subject personal data. Their descriptions/names must not be used as a free-form place to store personal information.

Tag/category joins can reference ProfessionalProfile, CandidateProfile, Organization, Offering, Gig, or Job. Whether person-scoped joins are Taxonomy-owned is tied to PR-TAX-01.

### Privacy executor behavior

- Privacy / Data Erasure owns `PrivacyRequest`, jobs, ordering, deadlines, and exemptions.
- Taxonomy participates through SH-095/096/097/098 only for records it owns.
- If PR-TAX-01 assigns person-scoped joins to contextual owners, Taxonomy's subject enumeration normally returns no person-owned join rows; those contextual Modules execute detachment/anonymization as appropriate.
- If join ownership remains Taxonomy-owned, this architecture must be updated with explicit detach/retain/anonymize behavior before production privacy erasure is enabled.

### Retention

Canonical terms should generally be retained/deactivated rather than deleted because historical records and compliance decisions may refer to stable IDs. Any legal retention/erasure exception is evaluated through Privacy's policy flow; this Module does not invent retention exemption records.

### Export

Reference vocabulary may be included as explanatory context in a user's export by the export owner, but canonical taxonomy reference data is not itself the user's personal data.

---

## 29. Observability

Use the platform stack:

- SH-032 request/correlation context;
- SH-033 structured logs;
- SH-034 telemetry sanitization;
- SH-036 metrics;
- SH-037 integration failure for failed cross-Module handoffs where operationally relevant;
- SH-038 queue telemetry for workers.

### Safe dimensions

Examples: operation name, term type, term ID, active-state transition, result category, reason code, worker scope size, normalization-rule version, correlation ID. Avoid logging full descriptions, raw foreign entity payloads, candidate/resume content, provider responses, secrets, or sensitive compliance evidence.

Operational records never become taxonomy source truth.

---

## 30. Security Boundaries

1. Validate all command/query inputs at server trust boundaries using the project runtime-validation standard.
2. Admin mutations are server-authorized through SH-001/002.
3. Cross-Module target facts use SH-123, never client-supplied ownership assertions alone.
4. Do not accept arbitrary `TagSource` strings; validate the canonical enum.
5. Do not expose `verified` as security/compliance proof.
6. No SQL/Prisma dynamic table lookup based on user-supplied target type.
7. No Bedrock/Typesense credentials in this Module.
8. Normalize controlled text before collision checks; database constraints remain final authority.
9. Rate-limit/admin-throttle bulk taxonomy maintenance through shared infrastructure where root policy requires.
10. Event/log/audit payloads are minimized and sanitized.

---

## 31. Error / Decision Result Pattern

Public commands return the root project Result/error shape. Public decisions SH-022/023 use SH-015's common decision envelope where available.

### Stable categories

- `UNAUTHENTICATED`
- `FORBIDDEN`
- `INVALID_INPUT`
- `NOT_FOUND`
- `CONFLICT`
- `STALE_WRITE`
- `DEPENDENCY_UNAVAILABLE`
- `REVIEW_REQUIRED`
- `INTERNAL_ERROR`

### Taxonomy reason-code namespace

- `taxonomy_duplicate_term`
- `taxonomy_slug_collision`
- `taxonomy_parent_not_found`
- `taxonomy_parent_inactive`
- `taxonomy_unknown_domain`
- `taxonomy_inactive_domain`
- `taxonomy_unknown_category`
- `taxonomy_category_not_in_domain`
- `taxonomy_inactive_category`
- `taxonomy_unknown_tag`
- `taxonomy_inactive_tag`
- `taxonomy_assignment_incompatible`
- `taxonomy_cross_category_policy_unresolved`
- `taxonomy_ai_suggestion_stale`
- `taxonomy_ai_suggestion_invalid`
- `taxonomy_join_ownership_unresolved`
- `taxonomy_merge_policy_unresolved`

Never leak raw Prisma errors, provider errors, or foreign Module internals to consumers.

---

## 32. Testing Architecture

### Domain unit tests

- normalization and canonical-match rules;
- hierarchy validation;
- effective-active ancestry;
- category/domain consistency;
- requirement-trigger mapping;
- mutation policy and reason codes.

### State-transition tests

- active → inactive → active for Domain/Category/Tag;
- ancestor inactivity behavior;
- prohibited hard-delete service path;
- stale edit conflicts.

### Public contract tests

- SH-022 result envelope and reason codes;
- SH-023 assignment validation contract;
- list/get/vocabulary DTO stability;
- SH-121 AI acceptance boundary;
- SH-094 source-projection contract.

### Database/integration tests

- unique names/slugs;
- FK hierarchy;
- category belongs to supplied Domain at service boundary;
- idempotent create/update;
- optimistic concurrency;
- transaction rollback if audit/event/search-outbox preparation fails according to root atomicity policy;
- no direct foreign repository use.

### Authorization tests

Every protected mutation and inactive/admin read must prove SH-001/002 usage. UI state alone is never sufficient.

### Compliance tests

- verification trigger does not produce verification-success truth;
- healthcare trigger does not produce healthcare-readiness truth;
- `verified` tag flag cannot satisfy Trust Verification;
- unsupported location trigger fails safely rather than using hardcoded category lists.

### Idempotency/concurrency tests

- duplicate create requests;
- simultaneous normalized-equivalent term creation;
- stale updates;
- AI/manual creation race;
- merge/backfill lock tests if those features are enabled.

### Privacy tests

- subject inventory contains only records this Module actually owns;
- canonical terms are preserved as reference data unless an explicit privacy/legal instruction applies;
- contextual joins are handled by the approved owner after PR-TAX-01.

### E2E participation

Admin taxonomy manager: create Domain → Category → Tag → edit trigger metadata → deactivate/reactivate → verify public vocabulary behavior and Search refresh request contract.

---

## 33. Module Invariants — Rules Coding Agents Must Never Violate

1. `TaxonomyDomain`, `TaxonomyCategory`, and `TaxonomyTag` are the canonical accepted vocabulary.
2. AI output never becomes accepted taxonomy truth without SH-121 and Taxonomy validation.
3. Search is projection; Taxonomy never writes `SearchUpsertEvent` or calls Typesense directly.
4. A Category must belong to its selected Domain before an entity can persist that classification.
5. A Tag must belong to its canonical Category; whether it must match an entity's primary Category remains an explicit policy decision, never an ad hoc feature rule.
6. Inactive or effectively inactive terms cannot be used for new accepted assignments.
7. `TagSource.ai` is provenance only.
8. Tag-join `verified` never means a `VerificationCheck` passed.
9. Taxonomy requirement triggers never mean healthcare, license, background check, or eligibility completion.
10. Taxonomy must not query or mutate foreign business lifecycles through direct Prisma repositories.
11. Join-row lifecycle must not be implemented until PR-TAX-01 is settled.
12. Normal product code does not hard-delete Domain/Category/Tag records.
13. Parent deactivation does not require destructive child deletion or row rewriting; effective activity is derived under PR-TAX-03.
14. Normalization logic exists once through SH-079; consumers do not fork `slugify/tagCleaner/skillNormalizer` implementations.
15. Authorization exists once through SH-002; no `taxonomyAdminRole` shortcuts.
16. Audit, domain events, and observability are three different concerns.
17. Generic queue/idempotency/locking/event infrastructure is never rebuilt inside the Module.
18. Taxonomy owns no Bedrock or Typesense provider adapter.
19. Consumer snapshots of taxonomy values remain the consumer's historical-decision truth.
20. Unsupported/ambiguous classification policy fails closed or returns review/unresolved; it is never guessed from UI conventions.

---

## 34. Prohibited Duplicate Implementations

Do not create these inside `taxonomy_classification`:

- `auth-helper.ts`, `taxonomyAuth.ts`, `getCurrentUser.ts`;
- `taxonomyPermissions.ts`, `adminGuard.ts`, `canManageTags.ts`;
- generic `slugify.ts`, `normalizeTag.ts`, `tagCleaner.ts`, `skillNormalizer.ts` outside SH-079 policy;
- `lookupAnyEntity.ts`, `polymorphicEntityRepository.ts`, foreign entity repositories;
- `taxonomyAudit.ts`, `auditLogger.ts`, `taxonomyHistoryLogger.ts` as replacement for SH-029;
- `typesenseIndexer.ts`, `searchSync.ts`, `taxonomySearchWorker.ts` that performs Search execution;
- `bedrockTaxonomyService.ts`, `aiTagService.ts`, prompt/model/provider clients;
- `idempotency.ts`, `jobDeduper.ts`, `taxonomyJobLock.ts`, process-local mutexes;
- `queue.ts`, `retry.ts`, `backoff.ts`, generic dead-letter framework;
- `readinessService.ts`, `complianceChecker.ts`, `healthcareGate.ts`, `verificationGate.ts` that claims downstream readiness;
- local `PrivacyRequest`, erasure job, retention exemption, audit, access-log, notification-delivery, or ops tables;
- generic cross-domain `mergeService.ts`.

---

## 35. Unresolved Decisions

### U-TAX-01 — taxonomy join-row lifecycle ownership

Registry claims Taxonomy ownership while glossary/contextual Modules also claim or imply ownership. Resolve before implementing assignment repositories/commands. **PR-TAX-01 proposes contextual ownership + mandatory SH-023 validation.**

### U-TAX-02 — tag-join `verified` meaning

Define whether this is classification-review acceptance, provenance validation, legacy field, or something else. It must not mean Trust Verification success. Consider rename/schema evolution rather than perpetuating ambiguity.

### U-TAX-03 — `confidence` semantics

Define eligible sources, scale/range, provenance, persistence purpose, and whether confidence belongs on accepted joins or only AI suggestion records.

### U-TAX-04 — candidate provenance

`TagSource.candidate` is commented out while `CandidateTag` exists. Decide whether candidate-applied tags use `user`, add `candidate`, or use another explicit actor rule.

### U-TAX-05 — cross-category Tag compatibility

Current schema permits a Tag from any Category to be attached to a target. Decide whether tags must match the target's primary Category, may span Categories, or use a typed compatibility policy. Until resolved, SH-023 returns `taxonomy_cross_category_policy_unresolved` for unsupported combinations rather than allowing feature-specific guesses.

### U-TAX-06 — controlled-term normalization rules/versioning

Specify Unicode normalization, case folding, punctuation/whitespace policy, canonical slug transformation, alias/synonym behavior, locale handling, and migration/version strategy. SH-079 owns the policy; no consumer may invent one.

### U-TAX-07 — merge/alias/history model

No alias, retired/merged status, merge record, or taxonomy change ledger exists. SH-122 is Proposed only. Resolve before destructive canonical merges.

### U-TAX-08 — search refresh fan-out ownership

When a Category/Tag change affects many classified entities, decide whether the contextual join owners enumerate impacted entity IDs, Taxonomy exposes an approved impact query, or Search consumes a taxonomy-change event and queries owner contracts. Direct foreign table scans are prohibited.

### U-TAX-09 — location/license/background trigger representation

Registry says taxonomy can trigger location, license, and background requirements, but current Taxonomy fields directly model only verification, healthcare (Category), and sensitivity (Category). Define owner-bound requirement mappings before claiming additional trigger coverage.

### U-TAX-10 — `DataSensitivity` semantic owner

Taxonomy stores a Category value but supplied evidence does not conclusively assign platform-wide enum evolution to Taxonomy. Confirm owner before changing enum values/meaning.

### U-TAX-11 — taxonomy-specific history/versioning

Determine whether `updatedAt` + AuditEvent + outbox events are sufficient for MVP or whether a dedicated immutable taxonomy version/change record is required, particularly for compliance-trigger policy changes.

### U-TAX-12 — admin reparenting

Moving a Category to another Domain or Tag to another Category could invalidate many business classifications. No approved reparent command exists. Treat parent IDs as non-editable through normal admin updates until an explicit migration policy is approved.

---

## 36. Architecture Decision Summary

Binding for implementation unless a stronger root/Cluster ruling supersedes it:

1. Taxonomy & Classification owns canonical Domain/Category/Tag vocabulary, hierarchy, `TagSource` semantics, normalization policy, classification validity, and trigger interpretation.
2. Search owns all Search projection truth and provider execution; Taxonomy uses SH-091/094.
3. AI Taxonomy owns AI suggestion/run truth and provider behavior; accepted mutation crosses SH-121 into Taxonomy.
4. Taxonomy triggers verification/healthcare/sensitivity requirements but never marks them complete.
5. Domain/Category/Tag use the current active/inactive lifecycle; normal hard delete is prohibited under PR-TAX-02.
6. Effective activity follows ancestry under PR-TAX-03.
7. Join-row ownership remains the principal blocker. PR-TAX-01 proposes contextual Module ownership with Taxonomy SH-023 validation.
8. `verified` on joins must not be interpreted as Verification truth; `confidence` and candidate provenance remain unresolved.
9. Cross-Module data access uses owner interfaces/SH-123, not foreign repositories.
10. Audit, events, jobs, idempotency, concurrency, observability, privacy orchestration, and Search refresh use canonical shared operations rather than local copies.
11. No external provider adapter belongs inside this Module.
12. Unresolved policy fails closed/review-required; coding agents must not invent it.

---

## 37. Coding-Agent Usage

Before implementing any numbered Taxonomy feature, the coding agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root code standards;
4. Canonical Shared Operations Registry / Architecture;
5. CL-02 architecture, if one now exists; otherwise Cluster Registry CL-02 section;
6. CL-02 build plan, if one now exists; otherwise root build-plan Phase 4;
7. this `module-architecture.md`;
8. this Module's `implementation-plan.md`;
9. public-interface sections for direct dependencies, especially Identity, Role, AI Taxonomy, Search, Trust Verification, and contextual entity owners relevant to the feature;
10. current `progress-tracker.md`.

The agent must also confirm the current status of U-TAX-01 through U-TAX-12 before implementing any feature that depends on them. A missing decision is not permission to create a convenient local architecture.
