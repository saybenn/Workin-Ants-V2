# AI Taxonomy Architecture

> **Module ID:** `ai_taxonomy`  
> **Module name:** AI Taxonomy Module  
> **Module type:** `capability`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-02 — Discovery, Classification & Visibility`  
> **Repository target:** `context/clusters/discovery classification & taxonomy/AI Taxonomy module/ai-taxonomy-module-architecture.md`\
> **Document status:** Implementation-grade Module architecture derived from the current Workin Ants evidence set; Proposed Rulings and Unresolved Decisions are explicitly labeled  
> **Audience:** Coding agents, developers, reviewers, maintainers, architects, security/privacy reviewers, and administrators responsible for classification workflows

Current coordination: [Cluster architecture](<../discovery-classification-architecture.md>) and [Cluster build plan](<../discovery-classification-build-plan.md>). Locate supporting artifacts through [context-map.md](<../../../context-map.md>); authority follows concern, not location or age. Root architecture/build-plan files are currently unavailable and do not supply enforceable phases.

---

## 1. Module Header

### Relationship to root architecture

This document owns AI Module concerns under context-map.md; Prisma owns current structure, Shared Operations owns canonical contracts, and CL-02 owns collaboration. Root architecture is currently unavailable. It may not redefine authentication, authorization, taxonomy ownership, search ownership, privacy orchestration, audit, observability, or generic provider infrastructure.

### Relationship to Cluster architecture

`ai_taxonomy` belongs to **CL-02 — Discovery, Classification & Visibility**, beside:

- `taxonomy_classification` — accepted controlled-vocabulary and classification truth;
- `search_public_visibility` — public/authorized search projection truth and provider execution.

The current CL-02 architecture and build plan are linked above. Module ownership/lifecycle and Cluster collaboration/sequence retain their separate authorities under context-map.md.

### Update rule

Update this file whenever a binding decision changes any of the following:

- `AiSuggestion` or `AiClassificationLog` meaning or lifecycle;
- supported AI classification target types or purposes;
- prompt/version or model-run provenance rules;
- provider adapter ownership;
- SH-121 acceptance handoff and AI-owned proposal disposition;
- candidate/privacy/healthcare provider-input policy;
- backfill ownership or persistence;
- public Module commands, queries, events, or Privacy executor contracts;
- a Canonical Shared Operation used by this Module;
- any Unresolved Decision is formally settled.

### Evidence status vocabulary

- **Confirmed** — directly established by current Workin Ants source evidence.
- **Reasonable inference** — required or strongly implied by confirmed responsibilities and boundaries.
- **Proposed Ruling** — a concrete architecture choice needed for safe implementation, but not yet established by stronger supplied evidence.
- **Unresolved Decision** — evidence establishes a real question but does not support a safe final answer.

### Primary evidence basis

This architecture reconciles the current:

- AI Taxonomy Module Architecture Extract;
- Deep Module Registry;
- Cluster Registry `v2.3-customer-subscription`;
- current `schema.prisma`;
- Ubiquitous Language / Compliance Inventory;
- Canonical Shared Operations Architecture / Registry;
- root Workin Ants project overview and build plan;
- Taxonomy & Classification Module architecture extract;
- Search / Public Visibility Module architecture extract.

A key evidence conflict is intentional and must remain visible: the Registry and Ubiquitous Language assign `AiSuggestion` and `AiClassificationLog` to this Module, while the current Prisma schema explicitly omits AI classification behavior and contains neither model. Conceptual ownership is confirmed; executable schema is not yet implemented.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Produce structured, validated, traceable AI-generated classification and skill suggestions for Workin Ants entities **without making those suggestions accepted platform truth**.

### Goal

Reduce manual classification effort and improve consistency while preserving:

- Taxonomy & Classification as the owner of accepted controlled vocabulary and accepted classification;
- source Modules as owners of their entity data and visibility/lifecycle state;
- privacy and sensitive-data restrictions;
- human/domain acceptance where required;
- provider provenance and reproducibility;
- a strict prohibition on automated employment decisions.

### What enters

The Module may receive only the minimum approved information required for a supported classification purpose:

1. target identity (`targetType`, `targetId`);
2. an owner-supplied, purpose-bound source snapshot or DTO;
3. a stable source-version token;
4. active Taxonomy vocabulary and semantic validation through Taxonomy public interfaces;
5. the active immutable prompt/output-contract version;
6. provider/model configuration;
7. authenticated actor/system context where the request is protected;
8. privacy/healthcare/sensitivity decisions when applicable.

The browser or arbitrary caller must not supply raw trusted classification source content as a substitute for the owning Module's source DTO.

### What leaves

The Module produces:

- `AiClassificationLog` run provenance and outcome;
- validated `AiSuggestion` proposals;
- confidence/provenance metadata;
- safe failure outcomes and operational references;
- review-readable evidence;
- optional versioned domain events if and only if an approved consumer contract requires them.

It does **not** produce accepted taxonomy joins, verification success, public visibility, candidate ranking, employment decisions, or search documents.

### Capability transformation

```text
owner-approved source facts
+ active controlled vocabulary
+ immutable prompt/output contract
+ provider/model configuration
+ privacy/sensitivity gates
        ↓
minimum provider payload
        ↓
foundation-model inference
        ↓
strict structured-output validation
        ↓
Taxonomy semantic validation
        ↓
AiClassificationLog + proposed AiSuggestion records
        ↓
SH-121 acceptance workflow; AI-owned proposal-only rejection
        ↓
accepted Taxonomy truth
        ↓
Search-owned projection refresh when applicable
```

### Why this deserves its own Module boundary

AI output has its own provenance, failure modes, versioning, provider costs, confidence semantics, asynchronous backfill behavior, and privacy risks. Those concerns should not contaminate Taxonomy truth or be duplicated in Marketplace, Hiring, Candidate, or Search code. The boundary allows provider and prompt mechanics to evolve while keeping accepted classification deterministic and separately owned.

---

## 3. Owned Truth

### Confirmed conceptual source-of-truth records

| Record | Meaning | Ownership status |
|---|---|---|
| `AiClassificationLog` | One AI classification run: target, source/configuration provenance, prompt/model version, validated output or safe failure, timing, and run status. | **Confirmed conceptual owner; absent from current Prisma schema.** |
| `AiSuggestion` | One validated AI-proposed domain/category/tag/skill result that is not accepted truth until another owner acts. | **Confirmed conceptual owner; absent from current Prisma schema.** |

### Plain-English meaning

**`AiClassificationLog`** answers: *What exactly did the AI classification capability attempt, against which source/configuration versions, using which provider/model/prompt/output contract, and what safe result occurred?*

It is domain provenance. It is **not** `AuditEvent`, `IntegrationFailure`, a provider log, or accepted Taxonomy truth.

**`AiSuggestion`** answers: *What classification or skill did a validated AI run propose for this target, with what confidence and provenance, and what later disposition did the accepted-classification owner communicate?*

It is proposal truth. It is **not** `TaxonomyTag`, `TaxonomyCategory`, a taxonomy join, a search document, or verification proof.

### Owned policies and invariants

The Module owns:

- which supported AI classification purposes exist;
- which validated output shapes correspond to those purposes;
- prompt wording and immutable prompt-version semantics for taxonomy/classification prompts;
- provider-output schema and semantic validation after provider parsing;
- confidence representation and interpretation **once approved**;
- classification-run status policy;
- suggestion proposal/disposition status policy **once approved**;
- deduplication identity for one classification request/run;
- when a proposed suggestion becomes stale, superseded, or invalidated on the AI side;
- bounded retry policy categories for AI inference, layered over shared retry mechanics;
- backfill batching/order policy for AI-owned work;
- candidate/employment output restrictions local to this capability: outputs are advisory classification/skill proposals, never hiring decisions.

### Owned snapshots/proof

The Module may own immutable references/hashes that prove which configuration a run used, including:

- source version or source snapshot hash;
- minimized provider-input hash;
- taxonomy vocabulary snapshot hash/version token;
- prompt key/version/hash;
- output-schema version;
- provider/model identifiers;
- provider request reference where safe;
- validated structured output snapshot where retention policy permits.

These snapshots prove **AI-run context**, not accepted Taxonomy or business/compliance state.

### Domain events/ledgers

No dedicated AI domain-event schema is confirmed in the current evidence. `AiClassificationLog` is the run/provenance record, not a generic append-only event ledger.

**Proposed Ruling PR-AI-01:** If asynchronous consumers require events, the Module may emit minimized, versioned facts such as `ai_taxonomy.classification_completed` or `ai_taxonomy.suggestions_created` through canonical `publishDomainEvent`. Event creation is deferred until a concrete consumer contract exists; event tables must not replace `AiClassificationLog` or `AiSuggestion`.

### Projections

The Module owns **no public search projection** and no Typesense document. A read-optimized admin list derived from `AiSuggestion` may exist, but it is not a separate source-of-truth model unless a later performance requirement justifies one.

---

## 4. Explicit Non-Ownership

This Module must not own or recreate the following.

| Adjacent owner | Responsibility that remains outside AI Taxonomy | Prohibited shortcut inside AI Taxonomy |
|---|---|---|
| Taxonomy & Classification | `TaxonomyDomain`, `TaxonomyCategory`, `TaxonomyTag`, `TagSource`, accepted vocabulary, accepted category/tag assignments, normalization semantics, compliance-trigger semantics | Writing taxonomy terms/joins directly; treating `TagSource.ai` as acceptance |
| Search / Public Visibility | `SearchUpsertEvent`, `SearchEntityType`, Typesense adapter, indexing/de-indexing, public/authorized search APIs, projection reconciliation | `typesenseService.ts`, direct `SearchUpsertEvent` writes, indexing raw suggestions |
| Marketplace Supply | `Offering` lifecycle and source fields | Direct Offering mutation or duplicate offering repository |
| Professional Eligibility | `ProfessionalProfile` lifecycle/readiness | AI-owned profile status/readiness flags |
| Organization Hiring | `Organization`, `Job`, organization membership and job lifecycle | Direct Job/Organization mutation; automated hiring decision state |
| Candidate Application & Resume Privacy | Candidate-controlled application/resume privacy, parsed resume truth, candidate search projection | Raw resume repository, resume parsing duplication, candidate ranking/rejection from AI output |
| Trust Verification / Screening | `VerificationRequirement`, `VerificationCheck`, credentials, verification outcome | AI-owned `isVerified`, passing/failing a requirement from a suggestion |
| Healthcare / Regulated Services | healthcare sensitivity/readiness/BAA/data-boundary policy | Local HIPAA boolean or provider-transmission rule invented here |
| Role / Authority | permission interpretation | `canRunAi`, local role tables, client-side-only admin checks |
| Identity & Access | authenticated actor/session/step-up truth | local auth/session helper or local MFA state |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob lifecycle, orchestration, retention exemption records | `gdprService`, direct platform-wide erase workflow |
| Admin Review / Compliance Hold | generic review stop-sign/hold truth | local `blocked`, `needsReview`, or `ComplianceHold` clone |
| Audit / Event Ledger | generic `AuditEvent` and `AccessAuditLog` | `auditLogger` or using `AiClassificationLog` as generic audit proof |
| Observability / Ops | `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident`, generic telemetry | local operational failure ledger or queue truth |
| Shared queue/platform infrastructure | retries, leases, dead-letter mechanics, idempotency framework | local queue framework, in-memory retry scheduler, local idempotency table |

### Specific non-ownership rules

1. AI Taxonomy may **suggest** a high-risk/verification-sensitive category. Only accepted Taxonomy classification can trigger a requirement, and Trust Verification owns whether that requirement is satisfied.
2. AI Taxonomy may **suggest** candidate skills. It must never decide whether to reject, rank, select, interview, offer, hire, or compensate a candidate.
3. AI may record acceptance only after successful SH-121 accepted mutation by the contextual entity owner. Rejection/expiry/cancellation/supersession without accepted mutation remain AI proposal-lifecycle concerns and do not mutate Taxonomy, contextual joins, or Search (CL02-R003). Exact AI lifecycle/schema remains unapproved under U-CL02-04.
4. AI Taxonomy must not request a public search refresh merely because a suggestion was generated.
5. AI Taxonomy must not create uncontrolled taxonomy terms from provider prose.
6. AI Taxonomy must not send raw private candidate data, PHI, or other sensitive source data because it is convenient.

---

## 5. Module Architecture Principles

1. **AI proposes; Taxonomy decides.** No provider output becomes accepted classification through this Module alone.
2. **Provider output is untrusted input.** JSON-looking output is not usable until schema and semantic validation pass.
3. **Source owners decide what may leave their boundary.** AI Taxonomy receives purpose-bound DTOs; it does not crawl neighboring tables.
4. **Minimum data leaves Workin Ants.** Provider input is allowlisted and minimized again before invocation.
5. **No raw-resume default.** Candidate skill/classification should prefer privacy-safe normalized facts supplied by Candidate Application & Resume Privacy; raw resume text requires an explicit approved contract.
6. **Reproducibility is mandatory.** Every completed run identifies source, taxonomy, prompt, output-schema, provider/model, and input-hash context sufficiently to explain which configuration produced the proposal.
7. **Prompt definitions are code/config, not ad hoc truth.** Unless a later architecture decision introduces a prompt registry model, prompt versions are immutable deployable artifacts and `AiClassificationLog` records their key/version/hash.
8. **Provider adapters are replaceable; domain meaning is not.** Business code must not import AWS SDK/Bedrock types outside the adapter.
9. **One run does not equal one accepted result.** A run can yield zero, one, or many proposals, all initially non-authoritative.
10. **Failures remain explicit.** Invalid output, unsupported targets, privacy denial, provider timeout, and retry exhaustion are distinct outcomes.
11. **Backfills are bounded.** A backfill is not permission to scan arbitrary tables or send every field to a provider.
12. **Search remains downstream of accepted truth.** Taxonomy acceptance, not AI generation, is the normal trigger for Search projection refresh.
13. **No provider state as platform truth.** Provider request IDs are provenance references only.
14. **No hidden employment automation.** A skill suggestion cannot be repurposed into ranking/selection by changing a caller name or UI label.
15. **Unresolved architecture blocks unsafe activation.** A missing provider-retention, healthcare, or candidate-data ruling must produce `unavailable`/disabled behavior rather than a guessed implementation.

---

## 6. Proposed Folder / Code Structure

The Module should live under the repository's Module boundary, for example:

```text
server/modules/ai-taxonomy/
├── index.ts                         # explicit public exports only
├── contracts/
│   ├── commands.ts                  # public command DTOs/results
│   ├── queries.ts                   # public query DTOs/results
│   ├── source-resolver.ts           # owner-supplied safe-source contract
│   ├── provider.ts                  # provider-neutral foundation-model port
│   └── privacy.ts                   # Privacy target handler contracts
├── schemas/
│   ├── command-schemas.ts           # runtime validation for public inputs
│   ├── provider-output-schemas.ts   # exact structured model-output contracts
│   └── source-snapshot-schemas.ts   # module-side validation of owner DTOs
├── domain/
│   ├── run-policy.ts                # run transitions, terminal rules
│   ├── suggestion-policy.ts         # suggestion lifecycle and supersession
│   ├── confidence-policy.ts         # approved confidence semantics
│   ├── prompt-registry.ts           # immutable taxonomy prompt definitions
│   ├── reason-codes.ts              # stable public failure/decision codes
│   └── employment-use-policy.ts     # explicit non-decision restrictions
├── commands/
│   ├── request-classification-suggestions.ts
│   ├── enqueue-classification-backfill.ts
│   ├── cancel-classification-run.ts
│   └── record-suggestion-disposition.ts
├── queries/
│   ├── get-suggestions-for-target.ts
│   ├── get-suggestion-for-decision.ts
│   ├── get-classification-run.ts
│   └── list-suggestions-for-review.ts
├── services/
│   ├── classification-orchestrator.ts
│   ├── taxonomy-snapshot-service.ts
│   ├── source-resolver-registry.ts
│   ├── provider-payload-builder.ts
│   └── suggestion-mapper.ts
├── repositories/
│   ├── ai-classification-log-repository.ts
│   └── ai-suggestion-repository.ts
├── providers/
│   ├── foundation-model-provider.ts
│   └── bedrock-foundation-model-adapter.ts
├── workers/
│   ├── process-classification-run.ts
│   └── process-classification-backfill-batch.ts
├── privacy/
│   ├── enumerate-subject-data.ts
│   ├── execute-privacy-instruction.ts
│   └── evaluate-retention-requirement.ts
└── tests/
    ├── domain/
    ├── contracts/
    ├── integration/
    ├── providers/
    └── workers/
```

If an admin UI is implemented, it should be a thin protected route/screen in the repository's established admin UI structure, for example:

```text
app/admin/taxonomy/ai-suggestions/
components/ai-taxonomy/
```

The UI may render AI-owned run/suggestion evidence and call public commands/queries. Acceptance controls invoke confirmed SH-121; proposal-only rejection invokes AI-owned lifecycle behavior. The screen must not mutate taxonomy joins directly.

### Folders intentionally absent

Do not create Module-local generic folders such as:

- `auth/`;
- `audit/`;
- `queue/`;
- `search/`;
- `privacy-orchestrator/`;
- `observability/`;
- generic `ai/` or `llm/` shared infrastructure.

Those mechanisms have external canonical owners.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / admin UI | Rendering suggestion/run evidence, request/backfill forms, loading/error states | permission policy, Taxonomy acceptance truth, provider calls, direct Prisma writes |
| Public commands | Validation, orchestration entry, idempotency identity, local preconditions | generic auth, source-owner lifecycle mutation, Search indexing |
| Public queries | Safe read DTOs, redaction, pagination, reason codes | raw provider payload exposure, cross-module aggregate queries |
| Application services | Classification orchestration across approved ports | direct cross-domain repositories, provider SDK types outside adapter |
| Domain policy | Run/suggestion state rules, prompt/output semantics, confidence/use restrictions | Taxonomy acceptance semantics, verification/healthcare/privacy truth |
| Repositories | CRUD/transaction behavior for `AiClassificationLog` and `AiSuggestion` only | Taxonomy joins, source entities, AuditEvent, IntegrationFailure, QueueJob |
| Workers | Process one AI-owned work item/backfill batch using shared queue | queue implementation, global scheduler, unrelated workflow orchestration |
| Provider adapter | Bedrock request/response mapping and safe provider errors | prompt/business policy, accepted taxonomy, provider state as domain truth |
| Contracts | Stable Module API, source resolver, provider port, Privacy handler | universal cross-domain repository or generic AI platform API |
| Privacy handlers | Enumerate/execute/export/retention behavior for AI-owned records | PrivacyRequest/DataErasureJob orchestration |

---

## 8. Data Model

### Current executable-schema status

The current Prisma schema includes Taxonomy records, taxonomy joins, `TagSource.ai`, `SearchEntityType`, and `SearchUpsertEvent`, but intentionally omits AI classification behavior. There is no `AiSuggestion`, `AiClassificationLog`, or AI-specific lifecycle enum in the current schema.

The Registry/Glossary ownership assignment therefore cannot be implemented until a schema decision and migration are approved.

### Proposed Ruling PR-AI-02 — minimal MVP AI schema

Add exactly two Module-owned records for the first implementation: `AiClassificationLog` and `AiSuggestion`. Do **not** create a generic `AiRun`, `AiMessage`, `AiPrompt`, `AiBackfill`, or platform-wide AI table without separate architecture approval.

#### `AiClassificationLog` — proposed fields and meaning

| Field / group | Purpose |
|---|---|
| `id` | Stable run identifier. |
| `targetType`, `targetId` | Logical Workin Ants target. Target type is Module-owned AI classification vocabulary, not SearchEntityType reuse by assumption. |
| `purpose` | Taxonomy suggestion vs skill extraction or another explicitly approved AI purpose. |
| `status` | AI run lifecycle. |
| `requestedByUserId?` | Actor/audit reference when a human initiated the run; not authorization truth. |
| `sourceVersion` | Owner-supplied stable version token or deterministic snapshot identifier. |
| `inputHash` | Hash of the exact minimized provider payload/canonical bytes, not raw source content. |
| `taxonomySnapshotHash` | Proof of which active controlled-vocabulary snapshot was used. |
| `promptKey`, `promptVersion`, `promptHash` | Immutable prompt identity and content proof. |
| `outputSchemaVersion` | Exact structured-output contract expected. |
| `providerKey`, `modelKey` | Provider/model provenance. |
| `providerRequestId?` | Safe external request reference, if provided. |
| `validatedOutput?` | Strictly validated structured result snapshot, subject to privacy/retention policy. No raw provider body by default. |
| `failureCode?` | Stable safe domain/provider failure category. |
| `correlationId` | End-to-end request/job trace. |
| `startedAt`, `completedAt`, `createdAt`, `updatedAt` | Run timing. |
| `version` | Optimistic-concurrency token if approved by root data standards. |

Important relationships:

- one `AiClassificationLog` may have many `AiSuggestion` rows;
- the target remains owned by its source Module;
- `requestedByUserId` is a reference, not a copied User lifecycle;
- taxonomy/model/prompt references are provenance, not ownership transfers.

Suggested indexes:

- `(targetType, targetId, createdAt)`;
- `(status, createdAt)`;
- `(purpose, createdAt)`;
- `providerRequestId` where useful;
- `correlationId`.

Retention/privacy concerns:

- raw source text is not stored by default;
- `validatedOutput` may still contain personal data and must be part of Privacy inventory;
- provider request IDs and actor IDs are personal/operational metadata subject to retention rules;
- deleting an AI run must never silently delete accepted Taxonomy truth.

#### `AiSuggestion` — proposed fields and meaning

| Field / group | Purpose |
|---|---|
| `id` | Stable proposal identifier. |
| `classificationLogId` | Run that generated the proposal. |
| `suggestionType` | Domain, Category, Tag, Skill, or another explicitly approved type. |
| `candidateKey` | Deterministic per-run proposal identity for dedupe. |
| `suggestedTermType?`, `suggestedTermId?` | Logical reference to an existing Taxonomy term for controlled-vocabulary suggestions. |
| `suggestedText?` | Normalized text only for an allowed free-text suggestion type such as skill extraction. |
| `confidence` | Approved normalized model-confidence representation. |
| `status` | Proposal/disposition lifecycle. |
| `decisionReference?` | Reference to authoritative Taxonomy decision/event, not a duplicate accepted-classification record. |
| `decisionReasonCode?` | Safe owner-supplied disposition reason where contract allows. |
| `decidedAt?` | Time authoritative owner communicated disposition. |
| `createdAt`, `updatedAt` | Proposal timing. |
| `version` | Concurrency token where required. |

Constraints:

- `candidateKey` should be unique within one `classificationLogId`;
- confidence must be range constrained after its representation is approved;
- controlled-vocabulary suggestions reference only valid existing terms in the first safe MVP;
- exactly one value shape is valid for each `suggestionType`;
- status begins `proposed`; provider output cannot create `accepted`;
- a later Taxonomy decision may update disposition only through the Module interface/event consumer.

### Proposed Ruling PR-AI-03 — no AI-created taxonomy terms in MVP

For the first implementation, domain/category/tag suggestions must select from existing active Taxonomy IDs. The provider may not create a new canonical term, synonym, alias, or hierarchy node. Skill extraction may return normalized free text because skill suggestions are explicitly part of this Module's responsibility, but those strings are not automatically Taxonomy terms.

### Proposed Ruling PR-AI-04 — taxonomy-reference storage

Because Taxonomy hard-delete/merge policy is unresolved, AI Taxonomy must not silently impose a destructive foreign-key behavior on Taxonomy records. Before migration, decide whether `suggestedTermId` is:

1. a logical UUID reference validated through Taxonomy with a snapshot of canonical label/path; or
2. an FK using a deletion behavior explicitly approved by Taxonomy.

Until that is settled, do not add an FK whose cascade/restrict semantics redefine Taxonomy lifecycle.

### Proposed Ruling PR-AI-05 — confidence representation

Use one explicit normalized confidence representation and document its meaning as **model confidence only**, never correctness, verification, or public-readiness probability. A recommended implementation is integer basis points `0..10000` for deterministic threshold comparisons. This remains proposed until reconciled with existing taxonomy-join `confidence Float?` semantics.

---

## 9. Enums, Statuses, and Lifecycles

No AI-specific enums exist in the current Prisma schema. The following are Proposed Rulings required before schema implementation.

### Proposed `AiClassificationTargetType`

Initial evidence-supported target candidates:

```text
professional_profile
offering
organization
job
candidate_profile
```

`gig` is **Unresolved**: the CL-02 Cluster Registry lists Gig / Demand as inbound to the Cluster, while the AI Taxonomy Registry entry does not list `Gig` among referenced schemas/consumers. Do not add Gig support silently.

### Proposed `AiClassificationPurpose`

```text
taxonomy_suggestion
skill_extraction
```

Additional AI purposes require architecture review. This Module is not a generic AI capability surface.

### Proposed `AiClassificationRunStatus`

```text
queued
running
completed
failed
cancelled
```

State diagram:

```text
queued ──→ running ──→ completed
  │           │
  │           ├──────→ failed
  │           │
  └──────────→ cancelled
              ↑
     running may cancel only through approved cooperative/best-effort path
```

Rules:

- `queued → running`: worker owns transition after durable claim.
- `running → completed`: only after provider output is structurally and semantically validated and run/suggestions commit successfully.
- `running → failed`: terminal after permanent validation/provider failure or retry exhaustion.
- `queued → cancelled`: authorized admin/system cancellation before execution.
- `running → cancelled`: only if the provider/work can actually be stopped or safely abandoned; provider response arriving later must not be applied blindly.
- terminal states do not reopen. A manual rerun creates a new `AiClassificationLog`.
- technical retry attempts are queue/provider mechanics within the run; they do not create a false new business run unless the idempotency policy requires it.

### Proposed `AiSuggestionType`

```text
domain
category
tag
skill
```

### Proposed `AiSuggestionStatus`

```text
proposed
accepted
rejected
superseded
invalidated
```

State diagram:

```text
                   ┌──→ accepted
proposed ──────────┼──→ rejected
   │               ├──→ superseded
   └───────────────└──→ invalidated
```

Rules:

- `proposed` is the only creation state.
- acceptance reflects successful SH-121 owner mutation; rejection without accepted mutation is AI-owned proposal disposition. These proposed status names/transition details still require U-CL02-04 approval.
- `superseded` is AI-owned stale-proposal handling when a newer equivalent run makes an undecided proposal obsolete.
- `invalidated` is used when a proposal cannot remain valid, for example the referenced term is no longer valid and no accepted decision exists.
- `accepted`/`rejected` are terminal AI disposition records; AI Taxonomy must not reverse the accepted classification. If accepted truth later changes, that is a Taxonomy canonical-term or contextual entity-owner assignment lifecycle/action and may produce a new AI-side annotation/event if required.
- no provider response may directly set `accepted`.

### Event/history proof

- run lifecycle proof: `AiClassificationLog` current state plus timestamps and immutable provenance;
- suggestion disposition proof: `AiSuggestion.status` + authoritative decision reference;
- generic administrator action proof: `AuditEvent` through SH-029;
- sensitive source access proof: `AccessAuditLog` through SH-030 where required;
- operational retry/failure proof: Observability/Queue records, not AI domain rows alone.

---

## 10. Commands

### `requestClassificationSuggestions`

**Purpose:** Request one AI classification run for a supported target/purpose.

**Actor/context:** authenticated actor or trusted system actor; caller must be authorized for the named AI action and target context.

**Authoritative inputs:** target type/ID, purpose, optional caller idempotency key. The command must resolve the trusted source snapshot from the owning Module; raw client-provided source text is not authoritative.

**Preconditions:**

- supported target/purpose;
- source resolver exists and returns an approved current snapshot;
- actor authorized;
- sensitivity/provider-transmission policy allows the purpose;
- active Taxonomy vocabulary can be resolved;
- prompt/output contract is available.

**State written:** new `AiClassificationLog` in `queued`; no suggestion until worker validation succeeds.

**Shared operations:** SH-001, SH-002, SH-123 for target eligibility; SH-003 only for approved minimum owner facts; SH-044, SH-047, SH-072, SH-077, SH-078, SH-032.

**Effects:** queue work; audit only if policy marks request material/sensitive; no search update.

**Idempotency:** semantic key should include target, purpose, source version/hash, prompt version, output-schema version, taxonomy snapshot version/hash, and caller idempotency scope. Replaying the same semantic command returns the original run/result where safe.

**Failure modes:** unsupported target, unauthorized, owner snapshot unavailable, privacy/sensitivity denied, duplicate/conflicting active run, queue unavailable, configuration unavailable.

### `enqueueClassificationBackfill`

**Purpose:** Start bounded AI suggestion generation over an authorized set of source records.

**Actor/context:** restricted administrator/system actor.

**Authoritative inputs:** registered target type, bounded owner-supplied scope/cursor, purpose, dry-run flag where supported, idempotency key.

**Preconditions:** authorization; target source enumerator registered; provider/config healthy enough to start; batch/rate policy approved.

**State written:** no generic AI backfill source-of-truth record in the proposed MVP. Each processed target creates its own `AiClassificationLog`; queue infrastructure owns operational work records.

**Shared operations:** SH-001, SH-002, SH-014 if central step-up policy requires it, SH-029, SH-044, SH-047, SH-048, SH-038.

**Effects:** audit backfill initiation; enqueue bounded batches; operational metrics.

**Idempotency:** same backfill scope/version/idempotency key must not enqueue duplicate target effects.

**Failure modes:** scope unsupported, source cursor stale, provider throttling, retry exhaustion, partial batch failure. Partial completion must be visible; failures must not mark unprocessed targets completed.

### `cancelClassificationRun`

**Purpose:** Prevent a queued run from executing or mark cooperative cancellation for running work.

**Actor/context:** authorized administrator/system owner.

**Authoritative inputs:** run ID, expected version, reason.

**Preconditions:** run is cancellable; caller authorized.

**State written:** run `cancelled` only through valid transition.

**Shared operations:** SH-002, SH-044, SH-052, SH-053, SH-029.

**Idempotency:** repeated cancellation returns the same terminal state.

**Failure modes:** not found, already terminal, stale version, provider work already irreversibly completed.

### `recordSuggestionDisposition` — **Proposed public/internal integration command**

**Purpose:** record acceptance on AI-owned proposal truth after SH-121 validation and successful accepted mutation by its owner. Proposal-only rejection remains an AI lifecycle concern, not a Taxonomy decision.

**Actor/context:** trusted Taxonomy workflow/event consumer, not arbitrary UI.

**Authoritative inputs:** suggestion ID/version, idempotency context, successful accepted-mutation/decision reference, decision time, optional safe reason code; preserve canonical SH-121 inputs at its acceptance boundary.

**Preconditions:** approved AI lifecycle permits disposition; decision source is trusted/idempotent and accepted mutation has succeeded. Proposed exact statuses remain gated by U-CL02-04.

**State written:** `AiSuggestion.status`, decision reference/reason/time only. It must not write Taxonomy joins.

**Shared operations:** SH-045 if event-driven, SH-044, SH-052, SH-053.

**Effects:** no Search refresh from this command. The owner whose accepted source truth changed requests SH-091. A failed mutation cannot be marked accepted; failed acknowledgement retries without repeating or reversing the accepted mutation.

**Idempotency:** same authoritative decision replays safely; contradictory disposition returns conflict/manual review.

**Failure modes:** suggestion not found, already decided, contradictory duplicate, stale/invalid proposal.

---

## 11. Queries / Decisions

### `getSuggestionsForTarget`

- **Consumers:** source owner/editor workflows, Taxonomy, authorized admin surfaces.
- **Input:** target type/ID; optional purpose/status filters; pagination.
- **Result:** AI proposal records with safe provenance and use restrictions.
- **Returns:** AI-owned source truth.
- **Must not infer:** accepted taxonomy, verification, readiness, public visibility, or hiring suitability.

### `getSuggestionForDecision`

- **Consumers:** SH-121 acceptance workflow.
- **Input:** suggestion ID.
- **Result:** immutable proposal detail, target reference, suggested existing term or skill text, confidence, run provenance summary, current AI status.
- **Returns:** decision evidence, not accepted classification.
- **Must not infer:** that the proposal is currently valid for attachment without Taxonomy validating active vocabulary/path and target context.

### `getClassificationRun`

- **Consumers:** authorized admins, Observability support tooling, source workflow debugging.
- **Input:** run ID.
- **Result:** safe run provenance/status, configuration identifiers, validated output summary, safe failure code.
- **Returns:** source run evidence.
- **Must not infer:** AuditEvent completeness, provider billing truth, or accepted taxonomy.

### `listSuggestionsForReview`

- **Consumers:** protected admin/review UI.
- **Input:** status/type/target/purpose/confidence/date filters and pagination.
- **Result:** review queue DTO derived from AI-owned records.
- **Returns:** proposal/evidence read model.
- **Must not infer:** ownership of generic Admin Review/Compliance Hold lifecycle.

### Stable reason-code namespace

Public results should use stable categories such as:

```text
AI_TARGET_UNSUPPORTED
AI_SOURCE_UNAVAILABLE
AI_SOURCE_STALE
AI_INPUT_NOT_ALLOWED
AI_PRIVACY_RESTRICTED
AI_HEALTHCARE_RESTRICTED
AI_CONFIGURATION_UNAVAILABLE
AI_PROVIDER_UNAVAILABLE
AI_PROVIDER_THROTTLED
AI_PROVIDER_TIMEOUT
AI_PROVIDER_PERMANENT_FAILURE
AI_OUTPUT_INVALID
AI_TAXONOMY_REFERENCE_INVALID
AI_RUN_CONFLICT
AI_RUN_NOT_FOUND
AI_RUN_ALREADY_TERMINAL
AI_SUGGESTION_NOT_FOUND
AI_SUGGESTION_ALREADY_DECIDED
AI_DISPOSITION_CONFLICT
AI_REVIEW_REQUIRED
```

Provider-specific strings must not escape as public reason codes.

---

## 12. Public Module Interface

The stable boundary should be exported from `server/modules/ai-taxonomy/index.ts` (or repository-equivalent) rather than exposing repositories/Prisma models to consumers.

### Public commands

```text
requestClassificationSuggestions
cancelClassificationRun
enqueueClassificationBackfill            # restricted
recordSuggestionDisposition               # Proposed integration command / event handler
```

### Public queries

```text
getSuggestionsForTarget
getSuggestionForDecision
getClassificationRun
listSuggestionsForReview                  # restricted
```

### Emitted domain events

None are confirmed. If a consumer requires asynchronous facts, Proposed Ruling PR-AI-01 permits minimized versioned events through SH-046 only after the contract is approved.

### Privacy executor

The Module must implement Privacy-defined owner handlers:

```text
enumerateSubjectData
executePrivacyInstruction
evaluateRetentionRequirement
```

The exact repository registration mechanism is owned by Privacy/platform integration, not by this Module.

### Provider-facing interface

**Proposed Ruling PR-AI-06:** expose a provider-neutral `FoundationModelProvider` port inside the Module/provider boundary. The first adapter target is AWS Bedrock. Other Modules must not import the Bedrock adapter directly merely because it exists here; broader AI infrastructure ownership remains unresolved in canonical SH-065.

---

## 13. Inbound Dependencies

| Owning Module / capability | Interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | SH-001 `resolveAuthenticatedActor` | establish trusted caller/system context | actor ID/type/session assurances | yes | session/current-user helper |
| Role / Authority | SH-002 `authorizeResourceAction` | authorize request/review/backfill/config access | action, resource, owner facts | yes | roles/permission matrix |
| Source entity owner | owner-specific safe classification-source DTO; SH-003 `queryOwnerFacts` only for minimum relationship facts | obtain authoritative target content/version without cross-domain repository access | target ID, safe fields, source version, sensitivity/purpose metadata | yes | direct cross-module Prisma reads |
| Taxonomy & Classification | active taxonomy tree/query; SH-023 `validateTaxonomyAssignment`; SH-079 normalization where needed | constrain output to accepted vocabulary and validate IDs/path | active term IDs, hierarchy, trigger metadata needed for semantics, taxonomy snapshot token | yes | Taxonomy tables/repository/normalizer |
| Candidate Application & Resume Privacy | privacy-safe candidate skill/classification source DTO | candidate skill suggestions without raw resume leakage or employment decision | normalized/allowed skills/text, source version, privacy restrictions | yes | resume parser, raw resume store, candidate search projection |
| Healthcare / Regulated Services | approved sensitivity/provider-use decision where healthcare-sensitive source may be involved | prevent unapproved external transmission | allowed/denied/review-required plus evidence/version | yes | local HIPAA/provider policy |
| Privacy / Data Erasure | SH-095/096/097 protocols | privacy fulfillment for AI-held personal data | target instruction, subject ID, disposition, retention evidence | yes for privacy execution | PrivacyRequest/DataErasureJob workflow |
| Audit / Event Ledger | SH-029/030 | generic admin/sensitive evidence | actor/action/target/safe metadata | no for ordinary run unless audit is mandatory; audit failure handling follows root policy | local audit tables |
| Observability / Ops | SH-032..039 | correlation, logs, metrics, provider/queue failure visibility | safe identifiers/status/error categories | operationally may block provider activation/health gate | IntegrationFailure/SystemEvent/QueueJob clones |
| Shared queue/platform infrastructure | SH-044..053 | durable async work, retries, locks, state transitions | semantic key, payload, lease/retry policy | yes | local queue/idempotency/lock framework |
| Foundation model provider | SH-065 through adapter | inference | minimized prompt/input/schema, request context | yes | provider SDK use outside adapter |

### Source-owner contract rule

Confirmed **SH-123 `validateOwnedTargetReference`** is used wherever AI validates target existence/status/version or relationship eligibility. The target owner supplies that result and not-found/forbidden distinctions. Proposed SH-003 minimum owner facts do not substitute for SH-123; the richer owner-approved classification-input DTO remains a separate contract.


A Registry entry under `schemasReferenced` is **not permission for direct Prisma access**. Rich classification input must come from an owner-approved DTO/query. SH-003 `queryOwnerFacts` is only for minimal relationship/ownership facts and must not become a universal polymorphic data repository.

---

## 14. Outbound Consumers and Effects

### Taxonomy & Classification

Confirmed SH-121 `applyAiSuggestion` is the canonical acceptance workflow: suggestion ID/version, target, selected canonical term, reviewer, reason, idempotency key, and audit evidence. Taxonomy owns canonical acceptance policy; the classified entity owner persists its assignment under CL02-R001. AI records acceptance only after mutation success; retries preserve the same version/idempotency context. Proposal-only rejection remains AI-owned. Local descriptive flow names do not replace SH-121.

### Marketplace Supply / Professional workflows

May request/read suggestions for Offerings or ProfessionalProfiles once their source-resolver integration exists. They may display advisory suggestions but must not treat them as accepted classification until Taxonomy truth changes.

### Organization Hiring

May request/read Job or Organization classification suggestions once integrated. AI output cannot substitute for Job Compliance or hiring decisions.

### Candidate Application & Resume Privacy

May request/read skill/classification suggestions using an explicitly privacy-safe source contract. Outputs may assist candidate-controlled taxonomy/skill editing but not employer ranking/selection.

### Admin Review / Compliance Hold

May inspect low-confidence, invalid, or failed AI runs. AI Taxonomy does not create a local generic hold lifecycle. Low confidence alone must not automatically create a `ComplianceHold` without a separately approved policy.

### Search / Public Visibility

The Deep Module Registry lists Search as a consumer, but the stronger canonical rule is that Search projects accepted source truth. Therefore:

**Proposed Ruling PR-AI-07:** public Search must not consume raw/unaccepted `AiSuggestion` as index truth. Search may consume AI records only for restricted diagnostics if a specific admin contract is approved. Accepted classification changes should cause **Taxonomy**, not AI generation, to call SH-091 `requestSearchProjectionRefresh`.

### Operational effects

The Module may:

- record `IntegrationFailure` for provider/worker failures;
- emit metrics/logs;
- append generic audit/sensitive-access evidence where policy requires;
- enqueue/retry AI-owned work.

It must not mutate another Module's source tables directly.

---

## 15. Canonical Shared Operations Used

The current canonical registry supplies IDs. Operations marked Proposed remain Proposed at platform level even if this Module depends on them.

| Canonical operation | Meaning / owner / class | Why AI Taxonomy uses it | Invocation point | AI-local policy retained | Expected result | Prohibited duplicate |
|---|---|---|---|---|---|---|
| **SH-001 `resolveAuthenticatedActor`** | Trusted Workin Ants actor context — Identity & Access — confirmed platform capability | protected request/review/backfill entry | before protected command/query | which AI actions require authentication | typed trusted actor/system context | `currentUser.ts`, `requireUser.ts` |
| **SH-002 `authorizeResourceAction`** | Named resource/action authorization — Role / Authority — confirmed | request/review/backfill/cancel access | after actor resolution | AI action vocabulary and resource facts | allowed/denied decision | `permissions.ts`, `adminGuard.ts`, `canRunAi.ts` |
| **SH-003 `queryOwnerFacts`** | minimum owner/relationship facts — source Module — **Proposed** shared contract | permission/source-context checks without repository coupling | before owner-sensitive requests | exact facts needed for AI target | small owner-specific DTO | universal cross-domain repository |
| **SH-023 `validateTaxonomyAssignment`** | validate proposed classification against Taxonomy — Taxonomy — confirmed public interface | semantic validation of provider term IDs/path | after structured output parse, before suggestion creation | provider output schema and confidence policy | valid/invalid + reason/evidence | local taxonomy validator/repository |
| **SH-029 `appendAuditEvent`** | generic material action proof — Audit — confirmed | backfill start/cancel, sensitive admin/config actions | after authoritative command result | which AI actions are audit-worthy | audit reference | `auditLogger.ts`, `activityLog.ts` |
| **SH-030 `recordSensitiveAccess`** | sensitive read/access proof — Audit — confirmed | only when source/run data is classified sensitive | at sensitive read/provider-source access boundary | AI target/data sensitivity context | access-log reference | `aiAccessLog.ts` |
| **SH-032 `createRequestContext`** | correlation/request context — Observability — confirmed | trace request → job → provider → DB | command/worker entry | safe AI dimensions | correlation/request identifiers | local request-ID generator |
| **SH-033 `writeStructuredLog`** | structured operational logging — Observability — confirmed | run/worker/provider operations | throughout safe operational path | event names/dimensions | log emission | `aiLogger.ts` framework clone |
| **SH-034 `sanitizeTelemetryMetadata`** | redact/allowlist telemetry — Observability/Audit policy — confirmed | prevent prompts/source/private output in logs | before logs/exceptions/failure records | AI-specific safe field allowlist | sanitized metadata | ad hoc `safeLogPayload` helpers |
| **SH-035 `captureException`** | exception diagnostics — Observability — confirmed | unexpected provider/worker defects | catch boundary | safe AI references | exception reference | direct provider stack dumps to user |
| **SH-036 `emitMetric`** | operational metrics — Observability — confirmed | latency, completion, invalid output, retries | after run/provider/job milestones | metric names/dimensions | metric emission | module-local metrics backend |
| **SH-037 `recordIntegrationFailure`** | provider/worker operational failure — Observability — confirmed | visible Bedrock/queue failures | on operationally relevant failure | run ID, provider category, safe reason | IntegrationFailure/SystemEvent reference | `providerFailureService.ts`, local failure table |
| **SH-038 `recordQueueTelemetry`** | queue health/attempt telemetry — Ops/queue infra — confirmed | backfill/run worker visibility | claim/retry/dead-letter | AI work type/target safe labels | telemetry only | AI-owned QueueJob clone |
| **SH-039 `checkServiceHealth`** | coordinated health check — Ops — confirmed | expose AI provider/worker readiness | health/admin diagnostics | what constitutes AI degraded/unavailable | normalized health result | custom health dashboard backend |
| **SH-044 `executeIdempotentCommand`** | one business effect per semantic retry — platform — confirmed | request, cancel, disposition, backfill start | command boundary | semantic key/replay conflict rules | original/replayed result | `idempotency.ts`, local command-key table |
| **SH-045 `deduplicateDomainEvent`** | inbox/effect dedupe — event infra — confirmed | if Taxonomy disposition is event-driven | before applying Taxonomy event | handler/version and contradiction policy | claimed/replayed event result | `processedAiEvents` generic table |
| **SH-046 `publishDomainEvent`** | transactional outbox event — platform — confirmed | only when approved consumers need AI facts | same transaction as AI source write | AI event names/payload privacy | outbox acknowledgment | custom event table/publisher |
| **SH-047 `enqueueReliableJob`** | durable async work — shared queue — confirmed | classification runs/backfill batches | after queued run/backfill command | payload, batch size, business completion | job acknowledgment | `queue.ts`, `backfillQueue.ts` |
| **SH-048 `executeRetryWithBackoff`** | bounded transient retry — shared queue/platform — confirmed | provider/timeouts/throttle | worker/provider call | retryable vs permanent AI error classification, max attempts | success/retry/dead-letter outcome | `retryService.ts` |
| **SH-051 `acquireAggregateLock`** | database-backed aggregate/resource lock — shared persistence — confirmed | prevent conflicting current runs/dispositions | target-purpose or suggestion transition | lock key and conflict semantics | acquired/busy | `classificationLock.ts`, in-memory mutex |
| **SH-052 `withOptimisticConcurrency`** | expected-version write guard — shared persistence — confirmed | cancel/disposition/state updates | mutation transaction | stale-write result semantics | updated/conflict | hand-rolled version checks |
| **SH-053 `transitionLifecycleState`** | shared state-machine plumbing, separate truth — confirmed | run/suggestion transitions | within owner transaction | valid transition matrix | transition result | generic AI status setter |
| **SH-061 `translateProviderStatus`** | provider-native → canonical adapter result — provider adapter — confirmed | normalize Bedrock errors/results | inside Bedrock adapter | mapping table and unsupported behavior | normalized provider result | provider error switches in domain service |
| **SH-065 `invokeFoundationModel`** | foundation-model invocation — AI Taxonomy initially, broader owner unresolved — **Proposed** provider-adapter capability | model inference | provider boundary | prompt, taxonomy semantics, token limits, confidence/output meaning | normalized provider result | `aiService.ts`, `bedrockService.ts`, `llmClient.ts` outside canonical port |
| **SH-066 `validateStructuredProviderOutput`** | strict structured output parse — shared validation primitive — confirmed | reject malformed/extra/untrusted provider JSON | immediately after provider result | exact AI schema, referenced IDs, semantic confidence rules | typed validated output or typed validation failure | `parseModelOutput.ts`, generic schema validator clone |
| **SH-072 `hashCanonicalPayload`** | stable cryptographic digest — shared security — confirmed | input/provenance/idempotency hashes | after canonical/minimized snapshot | what AI input hash proves and purpose/version | digest + algorithm/version | `hash.ts`, local crypto |
| **SH-077 `buildCanonicalTextSnapshot`** | deterministic canonical text/fields — shared mechanism — confirmed | stable source/provider input snapshots | before hashing/provider payload | fields included and canonicalization version | canonical bytes/text + version | local whitespace/hash serializer |
| **SH-078 `minimizeAndRedactProviderInput`** | minimum purpose-bound external payload — source policy + shared serializer — confirmed | prevent unnecessary private/sensitive provider data | immediately before provider call | target/purpose allowlist; source owner remains policy authority | validated provider DTO + safe telemetry copy | raw domain-object forwarding, `piiFilter.ts` policy clone |
| **SH-079 `normalizeControlledTerm`** | canonical controlled-term normalization — Taxonomy policy — confirmed | normalize suggested term/text before matching | mapping/semantic validation | AI output restrictions only | normalized candidate/match input | AI-owned taxonomy normalizer |
| **SH-095 `executePrivacyInstruction`** | owner executes Privacy instruction — confirmed protocol | erase/anonymize/restrict/export AI records | Privacy job callback | exact AI field mapping and accepted-truth separation | typed privacy result | `gdprService.ts`, PrivacyRequest clone |
| **SH-096 `enumerateSubjectData`** | enumerate owner-held subject data — confirmed | Privacy inventory | Privacy discovery phase | how AI records map to subject/targets | target list/cursor | global table crawler |
| **SH-097 `evaluateRetentionRequirement`** | owner supplies retention facts; Privacy records exemption — confirmed | decide retain/anonymize eligibility | before destructive privacy action | AI evidence/contract need; no invented legal basis | required/not required + basis/reference | local exemption workflow |
| **SH-098 `anonymizePersonalFields`** | shared field-level anonymization primitive — confirmed | preserve permitted run proof while removing personal fields | privacy executor | AI field map/invariants | anonymization proof | hand-written global scrubber |
| **SH-091 `requestSearchProjectionRefresh`** | Search-owned controlled refresh command — confirmed | **boundary only in current AI flow** | normally invoked by Taxonomy after accepted truth changes, not by suggestion generation | rule that raw AI proposal never qualifies | Search request acknowledgment when a legitimate source owner calls | direct SearchUpsertEvent/Typesense write |

### Canonical operations explicitly not implied

- SH-005 `resolveEntitlement` is **not** currently an AI-taxonomy gate. Track entitlement is a CL-02 input for search boosts, not evidence that AI classification itself is premium-gated.
- SH-011 `evaluateComplianceHold` is **not** a confirmed generation gate. A source owner may withhold/deny source input based on its own action composition, but AI Taxonomy must not invent a generic hold check for every run.
- SH-059/060 provider webhook verification/deduplication do not apply to the current synchronous/request-response foundation-model path. Do not create a fake provider-event ledger without a real callback contract.

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Truth affected | Why local |
|---|---|---|---|---|---|
| `resolvePromptDefinition` | resolve immutable prompt key/version for target/purpose | target type, purpose, environment/config version | prompt definition + hash + output schema version | none directly; snapshotted in run | prompt semantics are AI Taxonomy policy |
| `buildTaxonomyVocabularySnapshot` | produce deterministic vocabulary context allowed for model | active Taxonomy query result | minimized vocabulary DTO + snapshot hash | none | run reproducibility; does not own Taxonomy records |
| `resolveClassificationSource` | call registered owner adapter for safe source DTO | target type/ID, purpose, actor/system context | source version + safe fields + sensitivity metadata | none | target-routing policy belongs to this capability; data still owner-supplied |
| `buildClassificationProviderPayload` | compose prompt context from approved source + taxonomy + schema | safe source snapshot, vocabulary, prompt | provider-neutral request | none | exact classification meaning and token budget are AI policy |
| `mapValidatedOutputToSuggestions` | turn typed provider output into proposal candidates | validated output, taxonomy validation results | proposed `AiSuggestion` inputs | `AiSuggestion` on commit | proposal semantics are Module-owned |
| `computeSuggestionCandidateKey` | dedupe equivalent outputs within a run | type + canonical term/text | deterministic key | uniqueness | suggestion identity is local truth |
| `classifyRunFailure` | map normalized technical/validation result to domain run outcome | provider/validation error | retryable/permanent/review code | run status after orchestration | business meaning of failure is local; retry mechanism remains shared |
| `supersedeStaleProposals` | mark undecided older equivalent proposals obsolete after approved newer run | target/purpose/source/config versions | superseded count | `AiSuggestion.status` | AI owns proposal staleness, not accepted taxonomy |
| `enforceEmploymentUseRestriction` | assert candidate skill outputs cannot be exposed as hiring decision/ranking result | purpose + consumer contract | allowed/denied/restricted result | none | explicit module non-ownership guard |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Lifecycle machinery is shared; run/suggestion status truth is local.** SH-053 can perform safe transitions, but only AI Taxonomy defines the transition matrix.
2. **Queue mechanics are shared; classification work meaning is local.** `QueueJob` does not prove that an AI run completed. `AiClassificationLog` does.
3. **Idempotency is shared; semantic identity is local.** The platform claims/replays commands; AI Taxonomy defines which source/configuration versions make two requests the same business request.
4. **Hashing is shared; AI input hash meaning is local.** `inputHash` proves exact minimized classification bytes/version, not Media checksum, Consent proof, or Agreement integrity.
5. **Provider adapter shape is shared; mapping/prompt/output meaning is local.** Bedrock transport is not Taxonomy policy.
6. **Audit mechanism is shared; AI provenance remains separate.** `AuditEvent` cannot replace `AiClassificationLog`, and the run log cannot replace an audit entry.
7. **Privacy orchestration is shared; AI field-level disposition remains owner-executed.** Privacy does not update AI tables directly.
8. **Search refresh mechanism is Search-owned; AI proposals remain separate truth.** No projection event makes a suggestion accepted.
9. **Owner-fact contract is shared; source content stays separately owned.** Do not turn `queryOwnerFacts` into a global entity repository.
10. **Validated-output plumbing is shared; exact AI schema remains local.** `validateStructuredProviderOutput` cannot decide which taxonomy IDs or skill formats are semantically permitted.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

Protected human-initiated operations begin with SH-001 `resolveAuthenticatedActor`. Background workers use a trusted system actor/request context established by platform infrastructure.

### Role / Authority use

Use SH-002 `authorizeResourceAction` for actions such as:

```text
ai_taxonomy.suggestion.request
ai_taxonomy.suggestion.read
ai_taxonomy.run.read
ai_taxonomy.backfill.start
ai_taxonomy.run.cancel
ai_taxonomy.review.read
```

The exact action vocabulary should be approved with Role / Authority rather than inferred from route names.

### Contextual facts supplied by AI Taxonomy

AI Taxonomy supplies only what Role needs about AI-owned resources:

- run/suggestion ID;
- target type/ID;
- requester ID where relevant;
- whether the operation is review/backfill/admin scope;
- sensitivity classification if already established.

Ownership/relationship facts about Offering, Job, Organization, CandidateProfile, or ProfessionalProfile come from their owners.

### Resource ownership

- source entity ownership is external;
- `AiClassificationLog` and `AiSuggestion` are Module-owned records whose read/action authorization can depend on source-owner facts;
- a user does not gain edit rights over a proposal merely because the proposal targets their entity unless Role/source-owner policy says so.

### Admin/support actions

Backfills, run cancellation, private run inspection, and any future prompt/configuration administration are restricted server-side. The UI is not an authority boundary.

### Step-up

**Unresolved Decision U-AI-01:** The central sensitive-action/step-up matrix does not explicitly classify AI backfill or prompt/model configuration. If root security policy later marks either as sensitive, consume SH-014 `requireStepUpForSensitiveAction`. Do not create local MFA/step-up rules.

---

## 19. Compliance / Readiness / Entitlement Gates

### Verified-only / high-risk service gate

- **Underlying truth owners:** Taxonomy for accepted trigger classification; Trust Verification for requirements/results.
- **AI action:** generate a possible classification suggestion.
- **AI local policy:** a suggestion may identify a category/tag that *could* become a trigger if accepted.
- **Result:** AI output is supporting evidence only; it cannot block/publish/verify an entity.

### Candidate privacy / employment restriction

- **Underlying truth owner:** Candidate Application & Resume Privacy for candidate source/privacy; hiring owners for hiring workflows.
- **AI action:** skill/classification suggestion.
- **Gate:** source owner must return an allowed purpose-bound DTO; otherwise deny/unavailable.
- **Local composition:** prohibit output contracts whose meaning is reject/rank/select/hire/compensate.
- **Result:** advisory skill/classification proposal only.

### Healthcare-sensitive data

- **Underlying truth owner:** Healthcare / Regulated Services plus source owner.
- **AI action:** provider-bound classification on healthcare-sensitive source.
- **Gate:** an approved provider-transmission decision/contract must allow the exact purpose/data set.
- **Result:** allowed, denied, or review-required; AI Taxonomy does not infer the policy itself.

### Track entitlement

No current evidence requires an entitlement check to request AI Taxonomy. Do not add `aiPremium`, per-plan classification limits, or usage counters inside this Module without a later Track Entitlement decision.

### ComplianceHold

No universal AI generation hold gate is confirmed. A held source workflow may deny a classification source DTO through its owner policy. Low confidence or invalid AI output is not itself a reason to invent a local hold.

---

## 20. Provider Integrations

### Provider-neutral port

**Proposed Ruling PR-AI-08:** Define `FoundationModelProvider` with provider-neutral request/result types. Domain/application services depend on the port, not AWS SDK types.

A normalized request should include, at minimum:

- request/correlation ID;
- model selection key;
- immutable prompt version/hash;
- minimized source/taxonomy payload;
- structured output schema/version;
- token/output limits;
- timeout/retry classification hints that do not leak business policy to the provider.

### Adapter

The current provider target is **AWS Bedrock** behind `bedrock-foundation-model-adapter.ts`.

The adapter owns:

- Bedrock SDK calls;
- provider request format;
- model identifier mapping;
- timeout handling;
- provider-native error translation via SH-061;
- normalized provider request reference;
- safe provider telemetry.

It must not own:

- target/source authorization;
- Taxonomy acceptance;
- prompt business meaning;
- candidate privacy policy;
- confidence semantics;
- suggestion lifecycle.

### Credentials

Credentials belong in root-approved server secret/configuration infrastructure. Never persist them in `AiClassificationLog`, prompt config, browser state, or logs.

### Webhooks / event dedupe

No foundation-model webhook/callback flow is confirmed. Therefore:

- no `ProcessedAiProviderEvent` table is currently justified;
- SH-059/060 are not used for ordinary Bedrock inference;
- if a future asynchronous provider callback is adopted, webhook verification/dedupe must be designed before activation.

### Status/error translation

Provider errors map to canonical safe categories such as timeout, throttled, unavailable, validation/unsupported, authentication/configuration, and permanent failure. Unknown provider values must fail explicitly; never map unknown to success.

### Reconciliation

There is no durable external provider resource whose state must be reconciled for ordinary inference. Workin Ants run/suggestion records remain truth. A retry/re-run is not “provider reconciliation.”

### Retry and idempotency

- retries are bounded through SH-048;
- model calls may be at-least-once under network ambiguity;
- duplicate provider calls must not create duplicate `AiSuggestion` effects because run-level idempotency, candidate keys, and owner transactions dedupe persistence;
- provider cost/rate policy remains AI/provider-specific.

### Privacy deletion

**Unresolved Decision U-AI-02:** The supplied architecture does not specify Bedrock model/region/retention settings or whether any durable provider-side artifact needs deletion. Before sensitive/candidate/healthcare production use, select and document an approved configuration. If a provider resource becomes durable, deletion must use the provider-owner contract such as SH-070 where applicable.

---

## 21. Events and Outbox

### Confirmed event posture

No AI-specific event names or schemas are confirmed.

### Proposed event use

If a downstream consumer needs asynchronous notification, publish facts only after the AI-owned transaction commits, for example:

```text
ai_taxonomy.classification_completed
ai_taxonomy.classification_failed
ai_taxonomy.suggestions_created
```

These are **Proposed** names, not binding contracts.

### Emission rules

- event payloads contain run/suggestion IDs, target reference, purpose, safe status, source/config version references, and no raw source text/provider response;
- use SH-046 transactional outbox;
- include aggregate version, correlation ID, causation ID, schema version, and privacy classification;
- consumer effects are deduplicated with SH-045;
- an event states that an AI fact occurred; it does not command Taxonomy to accept or Search to index.

### Taxonomy disposition inbound event

**CL02-R003 approved choreography:** accepted mutation must succeed before AI `recordSuggestionDisposition`; a delayed acknowledgement retries without duplicating or reversing accepted truth. No Taxonomy/contextual-owner code directly updates AI tables. Proposal-only rejection remains AI-owned. PR-AI-09 transport preference remains proposed; direct command versus outbox delivery and exact event vocabulary/version are not selected here (U-AI-10 / U-CL02-13).

---

## 22. Background Jobs / Scheduled Work

### `processClassificationRun`

- **Purpose:** execute one queued AI run.
- **Input:** `AiClassificationLog.id` plus correlation/idempotency context.
- **Owner:** AI Taxonomy; queue mechanics shared.
- **Idempotency key:** run ID + worker version; domain dedupe also checks run status/version.
- **Retryable:** provider timeout, throttling, transient provider/network failure, temporary source/taxonomy unavailability where retry is safe.
- **Permanent:** unsupported target, privacy denial, invalid source contract, invalid provider output after configured attempts, invalid taxonomy IDs/path, configuration error requiring operator action.
- **Dead-letter/manual review:** run becomes failed only according to policy; queue terminal failure recorded through Ops. Manual rerun creates a new run unless replay can safely continue the same run.
- **Business truth updated:** `AiClassificationLog`; `AiSuggestion` on successful validated result.
- **Telemetry:** provider latency, run duration, retry count, invalid-output count, suggestions count, safe target type/purpose.

### `processClassificationBackfillBatch`

- **Purpose:** enumerate a bounded owner-approved batch and request per-target runs.
- **Input:** target type, owner cursor/scope, purpose, backfill invocation identity.
- **Owner:** AI Taxonomy orchestration; source owner supplies enumeration contract; queue shared.
- **Idempotency key:** backfill invocation + target ID + source version + purpose.
- **Retryable:** transient enumeration/queue/provider conditions.
- **Permanent:** invalid scope, unauthorized source, unsupported target, privacy restriction.
- **Dead-letter:** visible operational failure; do not mark remaining scope completed.
- **Business truth updated:** per-target AI run records only in MVP.

### Backfill source truth

**Proposed Ruling PR-AI-10:** Do not introduce `AiBackfill` as a third business model for MVP unless users need durable pause/resume/progress/cancel semantics independent of Queue/Ops records. If those semantics become required, create a separate architecture decision before adding the model.

### Scheduled work

No periodic AI schedule is confirmed. Do not add cron-based reclassification simply because a worker exists. Reclassification triggers should come from explicit requests, approved source-change events, Taxonomy changes, or a separately approved maintenance policy.

---

## 23. Concurrency and Idempotency

### Races to prevent

1. two identical classification requests for the same target/source/configuration create duplicate active runs;
2. backfill and interactive request process the same target/version simultaneously;
3. Taxonomy acceptance and AI supersession race on the same proposal;
4. an older provider result completes after a newer source version and is incorrectly treated as current;
5. retry persistence creates duplicate proposals;
6. cancel and worker-start race;
7. privacy erasure/restriction races with provider invocation or suggestion persistence.

### Aggregate/resource lock key

Recommended owner-defined key:

```text
ai_taxonomy:{targetType}:{targetId}:{purpose}:{sourceVersion}:{promptVersion}:{taxonomySnapshotHash}
```

The exact key can be shortened/hashed through shared primitives. Do not use an in-memory mutex.

### Unique constraints

At minimum:

- unique `candidateKey` within one run;
- command idempotency through SH-044;
- any active-run uniqueness constraint must be designed carefully because terminal history must remain insertable.

### Transaction boundaries

Successful run completion should atomically:

1. verify run is still applicable/running;
2. verify source/config version staleness policy;
3. persist validated output summary;
4. create deduplicated proposed suggestions;
5. transition run to completed;
6. write any required outbox event in the same transaction.

Operational logs/metrics can occur outside that transaction and do not replace it.

### Optimistic/pessimistic strategy

- SH-051 aggregate lock for conflicting target-purpose run creation/processing where necessary;
- SH-052 expected-version concurrency for run cancellation and suggestion disposition;
- database unique/check constraints for immutable proposal identity/ranges;
- never rely only on frontend disabled buttons.

### Replay result

A replay with the same semantic command identity returns the original run/result if still valid. If caller payload differs under the same key, return conflict rather than silently merging.

---

## 24. Media / Storage

No business attachment or file workflow is owned by AI Taxonomy in the current evidence.

Rules:

- do not upload prompt files, raw resumes, or source documents into a Module-local bucket;
- if future AI classification consumes a document, the source/document remains owned by its domain + Media/File Access mechanics;
- AI Taxonomy receives only an authorized extracted/minimized DTO;
- signed URLs, scanning, MIME validation, EXIF scrubbing, and MediaAsset access remain Media-owned;
- no permanent provider URL is stored as AI source truth.

---

## 25. Search / Projection

### Source truth

- AI proposal truth: `AiSuggestion`;
- accepted classification truth: Taxonomy records/joins;
- projection-work truth: Search-owned `SearchUpsertEvent`;
- provider projection: Search-owned Typesense documents.

### Indexing trigger

Generating or validating an AI suggestion **does not** qualify as a public indexing trigger.

When Taxonomy accepts a suggestion and changes accepted classification, Taxonomy should call SH-091 `requestSearchProjectionRefresh` through Search's public interface.

### Visibility/readiness/privacy

Search composes its own public-readiness policy from source owners and guardrails. AI Taxonomy neither decides public visibility nor supplies raw private fields to Search.

### What Search must not reconstruct

Search must not:

- infer accepted classification from `AiSuggestion.status=proposed`;
- index raw `validatedOutput`;
- infer candidate search visibility from skill suggestions;
- interpret provider confidence as ranking eligibility.

### AI-owned projection

No public projection. If an admin dashboard requires a list/read model, it should derive from AI source records or use a clearly non-authoritative cache.

---

## 26. Notification

No end-user AI Taxonomy notification trigger is confirmed.

Current policy:

- request/review flows are available through protected UI/query surfaces;
- worker/provider failures are operationally visible through Observability/Ops;
- do not send email/SMS/push directly from AI Taxonomy.

If a later requirement adds backfill-completion or review-needed notifications, the Module supplies the business trigger and safe template variables to SH-041 `requestNotification`; Notification owns persistence, channel routing, providers, delivery attempts, and recipient preferences.

---

## 27. Audit and Sensitive Access

### AI domain evidence

`AiClassificationLog` proves AI run/provenance state. `AiSuggestion` proves AI proposal/disposition state.

### Generic audit evidence

Use SH-029 `appendAuditEvent` for material administrative actions such as:

- starting/cancelling a broad backfill;
- changing an active prompt/model configuration if runtime configuration is later introduced;
- privileged manual repair/override of AI-owned run/suggestion state;
- other central policy-designated administrative actions.

### Sensitive access

Use SH-030 `recordSensitiveAccess` when a policy-classified sensitive source/run is viewed or transmitted and AccessAuditLog proof is required.

### Separation rules

- `AiClassificationLog` is not `AuditEvent`;
- provider request logs are not `AiClassificationLog`;
- `IntegrationFailure` is not evidence that the classification itself failed unless the AI run also records the domain outcome;
- `AccessAuditLog` proves access, not proposal correctness.

---

## 28. Privacy and Retention

### Subject-data inventory

AI-owned records may contain or reference:

- source entity IDs tied to a person;
- requester User ID;
- source version/hash;
- skill or classification suggestions about a person;
- validated structured model output;
- provider request/correlation references;
- timestamps and safe decision reasons.

Raw source text is prohibited from persistent AI storage by default under Proposed Ruling PR-AI-11.

### Privacy target executor

Implement:

- SH-096 `enumerateSubjectData`;
- SH-095 `executePrivacyInstruction`;
- SH-097 `evaluateRetentionRequirement`;
- SH-098 `anonymizePersonalFields` where appropriate.

Supported results should follow the canonical Privacy target-result envelope: erased, anonymized, retained, restricted, exported, detached, skipped, retryable failure, or terminal failure as applicable.

### Critical accepted-truth separation

Erasing/anonymizing an AI proposal does **not** automatically erase an accepted Taxonomy term or entity classification. Once Taxonomy accepted and attached a classification, that is separately owned truth and Privacy must target it through its owner if required.

### Provider resources

No durable provider resource is confirmed for ordinary inference. If future provider configuration creates one, provider deletion/revocation must be delegated through the provider owner, not executed by Privacy directly.

### Retention

**Unresolved Decision U-AI-03:** No AI-specific legal/contractual retention period is supplied. Do not invent one. Before production, define:

- retention for run logs;
- retention for rejected/superseded suggestions;
- whether validated output is retained and for how long;
- whether provider request references are retained;
- minimum provenance needed after accepted classification.

Until resolved, minimize persisted personal content and design field-level anonymization.

---

## 29. Observability

### Structured logs

Safe log dimensions may include:

```text
module=ai_taxonomy
runId
suggestionId where needed
targetType
targetId only if policy allows
purpose
runStatus
providerKey
modelKey or safe alias
promptVersion
outputSchemaVersion
retryAttempt
failureCode
correlationId
```

Do not log:

- raw source text;
- raw resume text;
- PHI;
- private candidate data;
- full prompts when they contain source content;
- raw provider responses;
- secrets/credentials;
- sensitive free-form admin notes.

### Metrics

Useful operational metrics:

- run queue latency;
- provider latency;
- total run duration;
- completion/failure/cancel counts;
- provider throttle/timeout count;
- invalid structured-output count;
- invalid Taxonomy-reference count;
- suggestions per run by safe type;
- retry count;
- backfill throughput/dead-letter count;
- stale-source suppression count.

### IntegrationFailure / SystemEvent

Record provider, worker, queue, and configuration failures when operationally relevant. Reference AI run IDs; never copy raw private data into Ops records.

### Health checks

Expose normalized health for:

- foundation-model adapter configuration/connectivity as safely testable;
- queue worker availability;
- required prompt/output schemas loaded;
- Taxonomy dependency reachable.

A health endpoint does not execute paid/sensitive classification on every probe.

---

## 30. Security Boundaries

1. Validate all public command/query inputs at runtime with project-standard validation.
2. Treat provider output as hostile/untrusted until SH-066 and Taxonomy semantic validation succeed.
3. Reject unknown provider fields unless the approved output schema explicitly permits them.
4. Allow only supported target types and purposes; do not accept arbitrary table/model names.
5. Resolve source content from trusted owner interfaces; never trust a browser-provided source blob as authoritative.
6. Minimize/redact provider input using SH-078 and source-owner policy.
7. Separate untrusted source text from instruction/control segments in prompt construction; source content must not be able to redefine the output contract or system rules.
8. Constrain controlled-vocabulary suggestions to existing approved term IDs in MVP.
9. Store provider credentials only in approved secret infrastructure.
10. Never log raw provider response/source text where it may contain personal/sensitive data.
11. Use SH-072 for canonical cryptographic hashes; do not write local crypto.
12. Enforce bounded request size/token budgets and provider rate/cost limits at the adapter/application boundary.
13. Use database locks/constraints for concurrency; never in-memory-only locks.
14. Do not expose private `AiClassificationLog.validatedOutput` to general users by default.
15. Candidate outputs carry explicit advisory/non-employment-decision semantics in contracts and tests.
16. Any healthcare-sensitive provider transmission remains disabled until its exact policy/provider configuration is approved.

---

## 31. Error / Decision Result Pattern

Public Module interfaces return predictable owner-specific results and never raw provider exceptions.

Recommended shape:

```text
success:
  ok: true
  data: <typed result>

failure:
  ok: false
  error:
    code: <stable AI_* reason code>
    message: <human-safe explanation>
    retryable: <boolean>
    remediation?: <safe next action>
    evidenceRefs?: <non-sensitive references>
```

Where a policy decision is involved, align with the canonical decision envelope when adopted:

```text
allowed | denied | warning | review_required | step_up_required | unavailable
```

### Categories

- validation/input denial;
- authorization denial;
- source unavailable/stale;
- privacy/sensitivity denial;
- configuration unavailable;
- conflict/stale version;
- provider retryable failure;
- provider permanent/unsupported failure;
- structured-output invalid;
- Taxonomy semantic invalid;
- terminal worker failure/manual review.

Provider status codes, SDK exceptions, model refusal strings, and stack traces must remain internal.

---

## 32. Testing Architecture

### Domain unit tests

- run transition matrix;
- suggestion transition matrix;
- terminal-state rules;
- supersession/invalidation rules;
- confidence-range/meaning rules;
- candidate employment-use restrictions;
- candidate-key/dedupe rules;
- prompt key/version/hash resolution.

### Public contract tests

- command/query runtime validation;
- stable reason codes;
- raw source content cannot be supplied as trusted target input;
- private provider/output fields are not exposed;
- Taxonomy consumer can read proposal evidence without direct DB access.

### Database/integration tests

- migrations from clean DB;
- indexes/check constraints;
- run + suggestions commit atomically;
- candidateKey uniqueness;
- terminal-state update conflicts;
- no write path to Taxonomy/Search tables.

### Authorization tests

- requester vs unrelated user vs admin/system;
- backfill restricted;
- private run details restricted;
- source-owner facts used through public interface.

### Compliance/privacy tests

- candidate raw resume is not sent/stored by default;
- sensitive/healthcare denied path does not call provider;
- accepted AI proposal erasure does not silently delete Taxonomy truth;
- Privacy enumerate/execute idempotency;
- sensitive access logging when policy requires.

### Idempotency/concurrency tests

- repeated request returns same semantic run/effect;
- interactive/backfill collision;
- cancel vs worker claim;
- older source result cannot overwrite newer/current state;
- duplicate Taxonomy disposition event produces one AI transition;
- contradictory disposition returns conflict.

### Provider adapter tests

- Bedrock request serialization contract;
- timeout/throttle/auth/config/error translation;
- unknown provider result fails explicitly;
- no provider SDK types leak past port;
- telemetry redaction;
- deterministic structured-output fixture validation.

### Worker tests

- claim, retry, dead-letter behavior;
- permanent validation failure does not retry indefinitely;
- provider retry does not duplicate suggestions;
- partial backfill failure preserves per-target truth.

### Cross-Module integration tests

- Taxonomy vocabulary → provider validation → proposal only;
- Taxonomy acceptance changes Taxonomy truth and later records AI disposition;
- Search refresh occurs from accepted Taxonomy workflow, not AI generation;
- source owners provide safe DTOs without direct AI repository access;
- candidate path never produces hiring decision output.

### E2E participation

When UI and source modules exist:

```text
authorized actor requests suggestions
→ queued run visible
→ validated proposals appear
→ SH-121 accepts through Taxonomy validation and contextual owner mutation; AI handles proposal-only rejection
→ AI proposal disposition updates
→ accepted classification triggers Search refresh through Search owner
```

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `AiSuggestion` is proposal truth, never accepted Taxonomy truth by itself.
2. `AiClassificationLog` is AI run provenance, never generic audit or provider log truth.
3. AI Taxonomy never writes `TaxonomyDomain`, `TaxonomyCategory`, `TaxonomyTag`, or taxonomy join rows directly.
4. AI Taxonomy never writes `SearchUpsertEvent` or Typesense directly.
5. Search never indexes a raw/unaccepted AI suggestion as public classification truth.
6. A provider response is never trusted without strict structured validation and Taxonomy semantic validation.
7. Provider output cannot create a new canonical taxonomy term in MVP.
8. `TagSource.ai` means provenance, not acceptance.
9. AI confidence is not verification, compliance readiness, public visibility, hiring suitability, or correctness probability.
10. Candidate skill/classification output cannot reject, rank, select, interview, offer, hire, or determine compensation.
11. Raw candidate resume/private data is not sent to a provider unless an explicit owner/privacy contract authorizes the exact purpose and fields.
12. Healthcare-sensitive provider transmission is disabled unless the owning policy explicitly permits it.
13. Source entity data is obtained through owner public interfaces, not cross-domain Prisma repositories.
14. Raw source content is not persisted in AI run records by default.
15. Raw provider responses are not persisted or logged by default; only validated/minimized output may be stored according to retention policy.
16. Every run records enough version/hash provenance to identify the source/configuration context used.
17. Prompt/model/provider details stay behind the provider/prompt boundaries; no Bedrock SDK types in domain/public contracts.
18. Generic queue, retry, idempotency, crypto, audit, observability, Privacy, and authorization systems are consumed, not recreated.
19. Backfills operate only over owner-approved scopes and registered source resolvers.
20. Run/suggestion status transitions are transaction-safe and cannot be changed by generic status setters.
21. Retried work cannot create duplicate suggestion effects.
22. Privacy execution against AI records cannot silently mutate another Module's truth.
23. Low confidence or provider failure does not automatically create a ComplianceHold unless a separate owner policy is approved.
24. Track subscriptions/entitlements are not inferred as AI-taxonomy permissions without explicit Track policy.
25. Unresolved architecture cannot be settled by implementation convenience.

---

## 34. Prohibited Duplicate Implementations

Do not generate these as independent responsibilities inside `ai_taxonomy`:

```text
auth.ts
currentUser.ts
permissions.ts
adminGuard.ts
canRunAi.ts
roleService.ts

aiService.ts                 # generic catch-all provider/domain service
llmClient.ts                 # if it bypasses SH-065/provider port
bedrockService.ts            # as a globally callable service outside adapter
modelProvider.ts             # duplicate provider abstraction outside canonical port

schemaValidator.ts           # generic validation framework clone
parseModelOutput.ts          # generic parser that bypasses SH-066

queue.ts
backfillQueue.ts
retryService.ts
jobRunner.ts
idempotency.ts
dedupe.ts
classificationLock.ts
mutex.ts

hash.ts
crypto.ts
piiFilter.ts                 # if it recreates source-owner privacy policy
redact.ts                    # generic shared serializer clone

searchIndexer.ts
typesenseService.ts
reindex.ts
searchEvent.ts               # direct SearchUpsertEvent writer

audit.ts
auditLogger.ts
activityLog.ts
aiAccessLog.ts               # generic sensitive-access ledger clone

errorLogger.ts
providerFailureService.ts
integrationFailure.ts
opsEvent.ts

gdprService.ts
eraseAiDataWorkflow.ts       # platform Privacy orchestration clone
privacyRequestService.ts

resumeParser.ts
candidateRanker.ts
hiringDecisionService.ts
verificationService.ts
healthcarePolicy.ts
taxonomyRepository.ts        # external Taxonomy truth clone
```

Narrow Module-local files may have similar technical words only when they clearly implement the local policy/adapter described in this architecture and do not duplicate the canonical capability.

---

## 35. Unresolved Decisions

### U-AI-01 — step-up matrix

Are broad AI backfills, prompt/model configuration changes, or sensitive run inspection centrally classified as step-up-required actions?

### U-AI-02 — Bedrock configuration and provider retention

Which Bedrock model(s), region, account boundary, data-retention settings, model-invocation logging settings, and fallback policy are approved for each sensitivity lane?

### U-AI-03 — retention durations

How long are completed/failed runs, rejected/superseded suggestions, validated outputs, and provider request references retained?

### U-AI-04 — exact Prisma schema

The two conceptual models are absent. Proposed fields/enums in Sections 8–9 require explicit approval before migration.

### U-AI-05 — Gig support

CL-02 lists Gig / Demand inbound, but the AI Taxonomy registry does not reference `Gig`. Is Gig an MVP target, later target, or excluded?

### U-AI-06 — confidence semantics

Should confidence use basis points, `0..1` float, categorical bands, or provider-specific calibrated values? How, if at all, does it map to existing taxonomy-join `confidence Float?`?

### U-AI-07 — source DTO contracts

Exact safe source fields/version tokens for Offering, ProfessionalProfile, Organization, Job, CandidateProfile, and any future Gig are not defined.

### U-AI-08 — candidate raw-text use

May any raw resume/application text ever be sent to the foundation-model provider, or must AI Taxonomy be restricted to owner-normalized fields/skills?

### U-AI-09 — healthcare-sensitive model use

What exact owner decision permits or prohibits provider-bound AI processing of healthcare-sensitive content?

### U-AI-10 — Taxonomy disposition handoff

Will Taxonomy call `recordSuggestionDisposition` directly through a shared transaction-aware application service or emit a versioned outbox event? Exact event/schema is not confirmed.

### U-AI-11 — taxonomy reference persistence

Logical UUID + snapshot vs FK relationship depends on Taxonomy hard-delete/merge policy.

### U-AI-12 — prompt management persistence

Are prompt templates immutable code/config artifacts only, or is a database-backed prompt registry/admin publisher required later?

### U-AI-13 — validated-output persistence

Should `AiClassificationLog` retain the full **validated structured** output, only a hash + normalized suggestions, or a bounded diagnostic subset?

### U-AI-14 — durable backfill lifecycle

Does product/admin UX require a first-class `AiBackfill` model for pause/resume/progress/cancel/history beyond queue/run records?

### U-AI-15 — event inventory

Which consumers need `classification_completed`, `suggestions_created`, or failure events rather than queries/queue state?

### U-AI-16 — Search diagnostic consumption

Does Search need any restricted diagnostic access to AI proposals, or should its dependency be entirely through accepted Taxonomy and source records?

### U-AI-17 — dynamic rate/cost limits

What per-target/model/backfill request limits and budgets apply, and which platform rate-limiting mechanism implements them?

### U-AI-18 — admin review composition

Should AI proposal evidence render inside Taxonomy admin UI, a shared Admin Review shell, or an AI-specific route that delegates decisions to Taxonomy?

---

## 36. Architecture Decision Summary

### Binding confirmed rulings

1. `ai_taxonomy` is a `capability`, `mvp_active`, in CL-02.
2. The Module owns AI classification/tag/category/skill **suggestions**, prompt/version logging, output validation, confidence/provenance metadata, and backfill suggestion workflows.
3. Conceptual source records are `AiClassificationLog` and `AiSuggestion`; they are currently absent from Prisma.
4. Taxonomy & Classification owns official taxonomy truth and final acceptance.
5. Search / Public Visibility owns search projection, `SearchUpsertEvent`, and Typesense execution.
6. AI output must be validated before domain use.
7. Sensitive/private candidate data must not be sent unless necessary and allowed.
8. AI Taxonomy must not implement automated employment decisions.
9. Generic authorization, queues, retries, idempotency, hashing, audit, observability, Privacy orchestration, and Search projection mechanics come from canonical owners.
10. Provider objects/results do not become accepted Workin Ants truth.

### Proposed Rulings requiring explicit approval before dependent schema/API commitment

- **PR-AI-01:** add AI events only when an approved consumer exists; use canonical outbox.
- **PR-AI-02:** MVP adds only `AiClassificationLog` and `AiSuggestion` as AI business records.
- **PR-AI-03:** MVP controlled-vocabulary output selects existing active terms only; no AI-created canonical terms.
- **PR-AI-04:** decide logical taxonomy reference vs FK only after Taxonomy deletion/merge semantics are approved.
- **PR-AI-05:** normalize confidence with one documented representation; basis points are the recommended candidate.
- **PR-AI-06:** use provider-neutral `FoundationModelProvider`; current adapter is Bedrock.
- **PR-AI-07:** public Search does not consume raw AI proposals; Taxonomy requests Search refresh after accepted truth changes.
- **PR-AI-08:** keep Bedrock details inside the provider adapter and SH-065 boundary.
- **PR-AI-09:** prefer Taxonomy-owned outbox fact to synchronize AI disposition, avoiding direct cross-Module table writes.
- **PR-AI-10:** no first-class `AiBackfill` model for MVP unless durable product semantics require it.
- **PR-AI-11:** do not persist raw source text/raw provider bodies in AI records by default.

### Binding posture for unresolved items

An implementation that depends on U-AI-01 through U-AI-18 must either:

1. resolve the architecture decision and update this file before implementation; or
2. remain disabled/stubbed/unavailable in a way that cannot silently create unsafe production behavior.

---

## 37. Coding-Agent Usage

Before implementing or modifying `ai_taxonomy`, an agent must read, in order:

1. root `context/project-overview-v3.md`;
2. context-map.md authority by concern; root architecture is unavailable;
3. repository instructions; the referenced code-standards document is unavailable;
4. `context/shared/shared-operations.md` / current Canonical Shared Operations Registry;
5. current linked CL-02 architecture;
6. current linked CL-02 build plan;
7. this `module-architecture.md`;
8. this Module's `implementation-plan.md`;
9. relevant dependency public-interface sections, especially Taxonomy & Classification, Search / Public Visibility, Identity & Access, Role / Authority, source entity owners, Candidate Application & Resume Privacy, Healthcare / Regulated Services, Privacy / Data Erasure, Audit / Event Ledger, and Observability / Ops;
10. available implementation/exit evidence; the referenced progress tracker is unavailable;
11. current `schema.prisma` and migrations;
12. provider/library documentation for Bedrock only when implementing the adapter.

Before coding, the agent must answer:

```text
Which AI-owned record is being changed?
Is this proposal truth or accepted Taxonomy truth?
Which source owner supplies the classification input?
Which fields are allowed to leave Workin Ants?
Which Taxonomy interface validates the output?
Which Canonical Shared Operations are consumed?
What is the idempotency/concurrency key?
Does the work touch candidate/private/healthcare data?
Does Search need any effect, and if so, is Taxonomy the correct caller?
Which audit/ops/privacy records are supplementary?
Does this feature depend on an unresolved decision?
```

If repository code conflicts with this architecture:

- do not create a second pattern;
- state the conflict;
- preserve confirmed source-of-truth ownership;
- prefer canonical shared operations/public interfaces;
- update architecture only after a legitimate decision;
- never let implementation convenience convert a Proposed Ruling into silent fact.
