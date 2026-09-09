# Taxonomy & Classification Module Implementation Plan

> **Module ID:** `taxonomy_classification`  
> **Module:** Taxonomy & Classification Module  
> **Primary Cluster:** `CL-02 — Discovery, Classification & Visibility`  
> **Repository target:** `context/modules/taxonomy_classification/implementation-plan.md`  
> **Plan status:** implementation-grade Module plan, subordinate to root/Cluster sequencing  
> **Governing architecture:** `taxonomy_classification/module-architecture.md`

This plan converts the Taxonomy & Classification architecture into narrow, independently reviewable implementation work. It does not reassign ownership, change CL-02 sequencing, or resolve architecture questions by implementation convenience.

A dedicated CL-02 `architecture.md` / `build-plan.md` was not located in the supplied project artifacts used for this synthesis. Until one exists, the controlling Cluster-level implementation sequence is the root Workin Ants build-plan **Phase 4 — Taxonomy, AI Suggestions, and Search Projection**, especially slices **4.1 Taxonomy foundation**, **4.2 Entity taxonomy joins**, **4.3 AI taxonomy suggestions**, and **4.4 Search projection**.

---

## Core Principle

Implement the Module through narrow, verifiable slices:

```text
public / observable behavior
→ validated command or query
→ Taxonomy-owned policy
→ authoritative Domain/Category/Tag write or read
→ canonical shared-operation calls
→ event / audit / Search-handoff effects
→ tests
→ exit gate
```

Taxonomy has a genuine administrator surface, but UI is never the source of truth. For contract-only features, the observable result is the public command/query, persisted reference-data change, emitted event, worker result, or integration proof.

---

## Build Rules

1. Follow root architecture, root build plan, code standards, and any later CL-02 architecture/build plan.
2. This Module owns only the truth declared in `module-architecture.md`.
3. Use public owner interfaces for foreign facts; never add direct Prisma repositories for Offering, Gig, Job, CandidateProfile, ProfessionalProfile, Organization, Search, AI, Verification, or Healthcare.
4. Reuse the Canonical Shared Operations by permanent ID.
5. Do not create local auth, authorization, audit, queue, retry, idempotency, concurrency, event, privacy-orchestration, Search, or provider infrastructure.
6. Every mutation is runtime-validated and server-authorized.
7. Domain/Category/Tag lifecycle changes are transaction-safe and idempotent where externally retryable.
8. Search effects are downstream effects; failure to deliver a Search refresh must not corrupt committed taxonomy truth.
9. AI provider details stay entirely outside this Module.
10. Background jobs are durable, bounded, retryable, observable, and use shared queue mechanics.
11. Every numbered feature ends with automated tests and an explicit exit gate.
12. Unresolved architecture must be surfaced and block the affected production mutation rather than being guessed.
13. No production taxonomy join repository is allowed while **U-TAX-01 / PR-TAX-01** remains unresolved.
14. No hard-delete command is allowed for Domain/Category/Tag in MVP under PR-TAX-02.
15. `verified` on tag joins must never be interpreted as Trust Verification success.
16. No feature may hardcode category/tag IDs as a substitute for SH-022/023 policy.

---

## Preconditions

### Hard dependencies before Feature 01

- repository/context foundation from root Phase 0;
- working Prisma/Postgres foundation and migration discipline from root Phase 1;
- current `TaxonomyDomain`, `TaxonomyCategory`, `TaxonomyTag`, and `TagSource` schema available;
- runtime validation standard and common Result/error conventions;
- Canonical Shared Operations contracts for SH-001, SH-002, SH-029, SH-032/033/034, SH-044, SH-046, SH-051/052, SH-079, SH-091, SH-121/122/123;
- test harness for unit/integration/database/authorization tests.

### Hard dependencies before protected admin mutation features

- SH-001 Identity actor resolution;
- SH-002 Role / Authority decision contract;
- SH-029 Audit append contract according to root audit policy;
- SH-044 idempotent command infrastructure;
- SH-046 transactional outbox infrastructure or the root-approved event dispatch equivalent.

These may be represented by contract-complete test doubles during early Module development only if their public interfaces are stable. Production routes may not bypass them.

### Hard dependencies before entity-assignment integration

- **U-TAX-01 / PR-TAX-01 must be resolved**;
- target-owner SH-123 contracts for the entity types being integrated;
- approved semantics for any join metadata that the write contract exposes, especially U-TAX-02 (`verified`) and U-TAX-03 (`confidence`).

### Hard dependencies before AI acceptance integration

- AI Taxonomy public suggestion query/decision contract;
- implemented `AiSuggestion` / `AiClassificationLog` source truth or a formally approved replacement;
- stable suggestion ID/version and target semantics;
- SH-121 contract.

### Hard dependencies before broad Search impact fan-out

- SH-091 Search refresh command;
- Search's accepted `SearchEntityType`/action/source-version contract;
- **U-TAX-08** resolved for affected-entity enumeration ownership.

### Interfaces that may initially be stubbed

- AI Taxonomy suggestion lookup, until AI schemas are built;
- Search SH-091 acknowledgement, until Search worker exists;
- Trust Verification SH-017 detailed requirement bindings, while Feature 04 can still prove Category/Tag trigger semantics;
- contextual target-owner SH-123 interfaces, but only for contract tests — not production join writes.

---

# Implementation Phases

## Phase 1 — Contracts and Source-of-Truth Foundation

### 01 Canonical Taxonomy Contracts and Repository Foundation

#### Objective

Create the stable Module boundary for canonical Domain/Category/Tag reads and writes, runtime validation schemas, repository seams, error codes, and source-truth DTOs without yet exposing full admin lifecycle behavior.

#### Observable Result

A developer can call typed Taxonomy queries against the database, receive stable source-truth DTOs, and prove that the Module has no direct foreign repositories or provider clients. Invalid command/query inputs are rejected at the server boundary.

#### Cluster Build-Plan Link

- Root Phase 1 — schema/source-of-truth baseline.
- Root Phase 4, Slice 4.1 — Taxonomy foundation.

#### Dependencies

- current Prisma schema;
- project validation/error conventions;
- SH-032 request context;
- existing database/test harness.

#### In Scope

- create Module folder boundary;
- public contract DTOs and taxonomy reason-code namespace;
- Zod/runtime schemas for Domain/Category/Tag commands and reads;
- `TaxonomyDomainRepository`, `TaxonomyCategoryRepository`, `TaxonomyTagRepository` using only owned tables;
- `listTaxonomyTree`, `getTaxonomyTerm`, `listActiveTaxonomyVocabulary` read paths;
- explicit no-hard-delete repository API;
- module index/public exports;
- fixtures/factories for taxonomy tests.

#### Out of Scope

- admin UI;
- term mutation commands beyond repository test setup;
- classification join writes;
- AI acceptance;
- Search refresh;
- requirement/readiness composition;
- normalization/backfill worker;
- provider clients.

#### Module-Owned Data

- `TaxonomyDomain` read/write repository seam;
- `TaxonomyCategory` read/write repository seam;
- `TaxonomyTag` read/write repository seam;
- `TagSource` contract representation.

No schema migration is required unless the current executable schema differs from the supplied target. If a mismatch is discovered, stop and document it before migration.

#### Public Interfaces

Introduced:

- `listTaxonomyTree(input)`;
- `getTaxonomyTerm(input)`;
- `listActiveTaxonomyVocabulary(input)`;
- shared DTO/error types used by later SH-022/023 commands.

#### Shared Operations Used

- **SH-032 `createRequestContext` — platform/Ops.** Invocation: server entry/query context. Local policy: none. Prohibited duplicate: local request-ID helper.
- **SH-034 `sanitizeTelemetryMetadata` — Ops/Audit policy.** Invocation: safe query/error metadata. Local policy: taxonomy field allowlist. Prohibited duplicate: taxonomy redaction framework.

#### Domain Logic

- preserve canonical IDs and hierarchy;
- return deterministic display ordering;
- default public vocabulary reads to effective-active terms only;
- inactive/internal reads require a protected query path later;
- never infer verification/healthcare readiness from trigger fields;
- repository methods expose owned tables only.

#### Authorization / Compliance

Public active vocabulary may remain publicly readable only where root/CL-02 policy allows. Feature 01 does not expose admin-only inactive data through public routes. Protected read integration is added with Feature 03/05.

#### Database / Transaction Behavior

- read-only queries use indexed relationships/active fields;
- repository writes used by tests preserve unique constraints;
- no raw hard-delete method exported from Module application layer;
- do not add a generic polymorphic join repository.

#### Events / Jobs

None.

#### Provider Integration

None. Confirm there is no Bedrock or Typesense import.

#### UI / Admin Surface

None.

#### Failure Behavior

- malformed term type/UUID/filter → `INVALID_INPUT`;
- missing term → `NOT_FOUND`;
- database unavailable → project-standard dependency/internal error;
- no fallback to copied static taxonomy data.

#### Tests

- unit: DTO/error mapping and effective-active read filtering fixtures;
- integration: tree parent/child ordering and active filters;
- database: unique constraints and FK relationship smoke tests;
- architecture: import/dependency test proving no foreign repository/provider import;
- contract: stable serialized DTO shape.

#### Documentation Updates

- progress tracker after completion;
- architecture only if executable schema conflicts with documented model.

#### Acceptance Criteria

- canonical terms can be listed/read from owned tables;
- runtime validation rejects malformed input;
- no provider/client/foreign repository exists inside Module;
- no hard-delete application API exists;
- current tests pass.

#### Exit Gate

Run the repository's canonical typecheck/lint/unit/integration commands plus taxonomy contract tests. Feature 02 does not begin until the read boundary, owned repositories, and no-foreign-coupling check pass.

---

### 02 Controlled-Term Normalization and Idempotent Seed Baseline

#### Objective

Establish one canonical normalization path and a safe, repeatable seed/reference-data workflow for Domain/Category/Tag without inventing alias/merge behavior.

#### Observable Result

The same approved seed can run repeatedly without duplicate terms, and raw controlled-term input receives a deterministic normalized candidate/match result through SH-079.

#### Cluster Build-Plan Link

- Root Phase 1, Slice 1.3 — default taxonomy seed data.
- Root Phase 4, Slice 4.1 — tag normalization rules and category/tag seed data.

#### Dependencies

- Feature 01;
- SH-044 `executeIdempotentCommand`;
- SH-079 `normalizeControlledTerm`;
- shared text primitive underlying SH-079;
- approved initial seed data source.

#### In Scope

- Taxonomy-owned normalization policy wrapper;
- normalized candidate/match query;
- deterministic seed loader using canonical IDs/keys or approved stable matching;
- dry-run collision report;
- seed idempotency tests;
- collision reason codes;
- normalization rule version constant/configuration if project standards require it.

#### Out of Scope

- fuzzy AI synonym generation;
- auto-merging duplicate records;
- alias table;
- reparenting;
- broad existing-data backfill;
- feature-local tag cleaners.

#### Module-Owned Data

- Domain/Category/Tag rows created from approved seed definitions.
- No new truth table is introduced solely for seed status.

#### Public Interfaces

- SH-079 `normalizeControlledTerm(input)`;
- maintenance command `seedTaxonomyReferenceData(input)` restricted to setup/admin tooling, not a general public business command.

#### Shared Operations Used

- **SH-079 `normalizeControlledTerm` — Taxonomy policy/shared text primitive.** Invocation: every proposed seed/create value. Local policy: controlled-term normalization/collision semantics. Prohibited duplicate: `slugify.ts`, `tagCleaner.ts` in consumer Modules.
- **SH-044 `executeIdempotentCommand` — platform.** Invocation: seed run/maintenance command. Local policy: seed-version + scope semantic key. Prohibited duplicate: `seedRunTracker` table.
- **SH-033/034 — Ops.** Invocation: safe seed summary logs. Local policy: counts only, not raw sensitive input.

#### Domain Logic

- normalization must be deterministic for the same ruleset;
- seed must not create a new term when a canonical normalized sibling already matches;
- ambiguous collision returns review/conflict rather than auto-merging;
- category seed requires existing/seeded parent Domain;
- tag seed requires existing/seeded parent Category;
- seed does not reactivate an intentionally inactive term unless the seed contract explicitly says so.

#### Authorization / Compliance

Seed maintenance is system/admin-only. Trigger metadata in seed rows is taxonomy trigger truth only; it is not proof downstream gates passed.

#### Database / Transaction Behavior

- each bounded seed unit is transaction-safe;
- database uniqueness is final collision authority;
- idempotent replay returns existing IDs/results;
- no hard delete on seed reconciliation.

#### Events / Jobs

No background job required for initial seed. If seed size later warrants async execution, use SH-047 rather than a custom queue.

#### Provider Integration

None.

#### UI / Admin Surface

None; seed is maintenance/setup behavior.

#### Failure Behavior

- duplicate canonical sibling → existing/review result according seed key;
- ambiguous normalization → `CONFLICT`/review required;
- missing parent → fail seed unit; no orphan child;
- partial large seed → report failed unit and allow idempotent replay.

#### Tests

- normalization unit fixtures for casing/whitespace/punctuation/Unicode rules actually approved;
- repeated seed idempotency;
- sibling collision tests;
- parent dependency tests;
- no destructive reconciliation test;
- authorization/maintenance-entry test if command is exposed through admin tooling.

#### Documentation Updates

If implementation settles U-TAX-06 normalization details, update `module-architecture.md` and canonical Shared Operations documentation in the same architecture change.

#### Acceptance Criteria

- one normalization policy is reused by seed/create flows;
- repeated seed produces no duplicates;
- collisions do not auto-merge;
- consumers need no local normalizer;
- tests pass.

#### Exit Gate

Canonical seed from an empty test database and a second replay both pass with identical logical vocabulary. Typecheck/lint/tests pass before Feature 03.

---

## Phase 2 — Core Taxonomy Lifecycle and Decisions

### 03 Domain, Category, and Tag Administration Commands

#### Objective

Implement authorized, idempotent create/update/activate/deactivate commands for canonical taxonomy terms with stale-write protection, audit, and domain events.

#### Observable Result

An authorized administrator can manage Domain/Category/Tag source truth through server commands; unauthorized, stale, duplicate, inactive-parent, or hard-delete attempts are denied with stable errors.

#### Cluster Build-Plan Link

Root Phase 4, Slice 4.1 — Domain/Category/Tag management and admin taxonomy foundation.

#### Dependencies

- Features 01–02;
- SH-001, SH-002, SH-029, SH-044, SH-046, SH-052, SH-079;
- approved action vocabulary from Module architecture;
- PR-TAX-02 and PR-TAX-03 treated as governing Proposed Rulings unless replaced before coding.

#### In Scope

- `createTaxonomyDomain`;
- `updateTaxonomyDomain`;
- `setTaxonomyDomainActive`;
- `createTaxonomyCategory`;
- `updateTaxonomyCategoryPolicy`;
- `setTaxonomyCategoryActive`;
- `createTaxonomyTag`;
- `updateTaxonomyTag`;
- `setTaxonomyTagActive`;
- effective-active calculation;
- expected-version/`updatedAt` stale edit protection;
- material mutation audit + taxonomy domain events.

#### Out of Scope

- hard delete;
- Category/Tag reparenting (U-TAX-12);
- join writes;
- merge/alias;
- AI acceptance;
- affected-entity Search fan-out.

#### Module-Owned Data

- `TaxonomyDomain`;
- `TaxonomyCategory`;
- `TaxonomyTag`;
- proposed taxonomy event vocabulary via platform outbox; no new event-ledger table.

#### Public Interfaces

All nine administration commands listed above plus protected reads for inactive terms used by admin tools.

#### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity.** Resolve actor. Local: taxonomy admin operation context. Prohibited duplicate: local session helper.
- **SH-002 `authorizeResourceAction` — Role.** Authorize named action. Local: action/target facts. Prohibited duplicate: `taxonomyPermissions`.
- **SH-079 `normalizeControlledTerm` — Taxonomy/shared text.** Normalize create/rename values. Local: collision policy. Prohibited duplicate: local slug/tag cleaner.
- **SH-044 `executeIdempotentCommand` — platform.** Protect retried mutations. Local: command semantic key. Prohibited duplicate: taxonomy idempotency table.
- **SH-052 `withOptimisticConcurrency` — platform persistence.** Reject stale admin writes. Local: expected version semantics. Prohibited duplicate: hand-rolled check-then-update.
- **SH-029 `appendAuditEvent` — Audit.** Material admin proof. Local: safe action metadata. Prohibited duplicate: taxonomy audit table.
- **SH-046 `publishDomainEvent` — outbox.** Emit taxonomy facts. Local: event type/payload. Prohibited duplicate: private event bus.

#### Domain Logic

- create requires canonical uniqueness and active parent for Category/Tag;
- update cannot reparent a Category/Tag in MVP;
- trigger fields are validated as taxonomy metadata, not readiness outcomes;
- deactivation does not delete descendants or joins;
- effective-active follows parent ancestry;
- reactivation requires valid current ancestry and collision-free canonical identity;
- hard delete is not exposed.

#### Authorization / Compliance

- all mutations are authenticated and authorized server-side;
- compliance-trigger field changes are material audit events;
- no `isHealthcareApproved`, `verifiedProfessional`, or other downstream completion truth is written;
- no step-up is added unless root security policy requires it.

#### Database / Transaction Behavior

Per command:

```text
validate input
→ resolve actor/authorize
→ idempotency claim
→ load aggregate / expected version
→ validate mutation + normalization
→ transactionally write source truth + outbox/audit request according platform pattern
→ return source DTO
```

Unique/FK constraints remain final authority. No in-memory lock.

#### Events / Jobs

Emit corresponding `taxonomy.*` fact events via SH-046. Search handoff is implemented deliberately in Feature 06 rather than hidden here.

#### Provider Integration

None.

#### UI / Admin Surface

No full UI yet; commands are observable via tests/admin development harness.

#### Failure Behavior

- unauthorized → `FORBIDDEN`;
- duplicate normalized term → `taxonomy_duplicate_term`;
- inactive/missing parent → `taxonomy_parent_inactive` / `taxonomy_parent_not_found`;
- stale expected version → `STALE_WRITE`;
- attempted reparent → explicit unsupported error;
- attempted hard delete → no command exists / rejected maintenance path.

#### Tests

- unit: transition/mutation policy;
- integration: all nine commands;
- database: uniqueness/FK/stale update;
- authorization: deny without permission;
- idempotency: duplicate command replay;
- audit/event: material action produces correct minimized evidence;
- regression: parent deactivation does not rewrite/delete child rows.

#### Documentation Updates

Update architecture if actual command fields or active-state semantics change. Record U-TAX-11 evidence if implementation shows a dedicated history model is required.

#### Acceptance Criteria

- all canonical term mutations go through Module services;
- no direct UI/repository mutation bypass;
- stale writes cannot silently overwrite newer changes;
- inactive ancestry is enforced for new child creation;
- no hard-delete application command;
- audit/events are distinct from source truth;
- tests pass.

#### Exit Gate

Run mutation/authorization/idempotency/concurrency tests plus standard quality commands. Feature 04 starts only after canonical lifecycle is stable.

---

### 04 Assignment Validation and Taxonomy Requirement Resolution

#### Objective

Implement the two canonical Taxonomy public decision interfaces: SH-023 `validateTaxonomyAssignment` and SH-022 `resolveTaxonomyRequirements`.

#### Observable Result

Any consuming Module can validate a proposed canonical classification and receive stable trigger facts without reading Taxonomy tables directly or mistaking trigger metadata for readiness.

#### Cluster Build-Plan Link

- Root Phase 4, Slice 4.1 — classification rules.
- Root Phase 4, Slice 4.2 — controlled entity taxonomy attachment prerequisite.
- Cross-cluster readiness foundation for later supply/hiring/search phases.

#### Dependencies

- Features 01–03;
- SH-015 common decision envelope;
- SH-017 Trust Verification requirement query where available;
- current modeled Category/Tag trigger fields;
- U-TAX-05 must be represented as unresolved/fail-closed rather than guessed.

#### In Scope

- hierarchy/path validation;
- effective-active validation;
- direct Domain/Category consistency;
- Tag canonical-category validation;
- assignment context DTO and stable reason codes;
- requirement mapping for modeled trigger fields;
- optional Trust requirement binding expansion through SH-017;
- explicit unsupported result for unmodeled location/license/background trigger mappings;
- unit and contract fixtures for consumers.

#### Out of Scope

- persist classification joins;
- decide whether an entity must be classified before its lifecycle transition;
- professional eligibility;
- healthcare readiness;
- verification completion;
- Search/public visibility decision;
- hardcoded location categories.

#### Module-Owned Data

Read-only use of Domain/Category/Tag. No new source record required.

#### Public Interfaces

- **SH-023 `validateTaxonomyAssignment`**;
- **SH-022 `resolveTaxonomyRequirements`**.

#### Shared Operations Used

- **SH-015 `returnDecisionResult` — shared decision envelope.** Invocation: decision response. Local: taxonomy reason codes/policy. Prohibited duplicate: taxonomy-specific generic result framework.
- **SH-017 `resolveVerificationRequirements` — Trust Verification.** Invocation: when detailed Trust-owned binding is required. Local: classification trigger inputs. Prohibited duplicate: direct VerificationRequirement repository.
- **SH-123 `validateOwnedTargetReference` — target owner, optional at orchestration boundary.** Invocation: only if SH-023 input includes target eligibility context that must be owner-confirmed. Local: supported relationship context. Prohibited duplicate: `lookupAnyEntity`.

#### Domain Logic

`validateTaxonomyAssignment` checks:

1. Domain exists and is effective-active;
2. Category, if supplied, exists, is effective-active, and belongs to Domain;
3. every Tag exists and is effective-active;
4. every Tag has a canonical Category;
5. assignment context is supported;
6. if tag-to-primary-category compatibility is not defined for the requested context, return `taxonomy_cross_category_policy_unresolved` rather than allow silently.

`resolveTaxonomyRequirements` initially maps only evidence-supported truth:

- Category `verificationRequired`;
- Category `requiresHealthcareCompliance`;
- Category `dataSensitivity`;
- Tag `verificationRequired`;
- approved Trust-owned requirement bindings returned through SH-017.

It does not claim location/license/background behavior unless a concrete binding model/interface exists.

#### Authorization / Compliance

These are decision/query interfaces. Consumers remain responsible for their own actor/authority and for deciding whether classification is mandatory. Protected metadata may require service/system context according root policy.

#### Database / Transaction Behavior

Read-only, but return source version/timestamps sufficient for a consuming write to detect stale taxonomy when needed. No broad cross-domain transaction is attempted.

#### Events / Jobs

None.

#### Provider Integration

None.

#### UI / Admin Surface

No dedicated UI required. Feature 05 displays decision failures in admin forms.

#### Failure Behavior

- unknown/inactive hierarchy → denied with stable taxonomy code;
- Trust requirement service unavailable → `unavailable`/retryable result for the detailed portion, not false `allowed`;
- unresolved tag compatibility → review/denied according SH-015 policy;
- no provider/raw DB error leakage.

#### Tests

- unit: all hierarchy/effective-active combinations;
- contract: exact SH-023 reason codes/envelope;
- contract: SH-022 trigger owner/severity/source fields;
- integration: category/domain mismatch from actual DB fixtures;
- compliance: trigger does not become readiness completion;
- failure: Trust dependency unavailable/unknown binding;
- regression: `verified=true` join fixture cannot satisfy verification readiness.

#### Documentation Updates

If U-TAX-05 or U-TAX-09 is resolved during implementation, update architecture before expanding the accepted behavior.

#### Acceptance Criteria

- consumers can validate assignments without direct taxonomy Prisma reads;
- consumer can translate modeled classification to owner-specific requirement triggers;
- no readiness completion is inferred;
- unresolved compatibility fails safely;
- stable contract tests pass.

#### Exit Gate

SH-022 and SH-023 contract tests must pass against real Taxonomy source records. No assignment write feature begins until these interfaces are stable.

---

## Phase 3 — Public/Admin Surface

### 05 Taxonomy Administration Surface and Protected Reference-Data Reads

#### Objective

Provide the MVP administrator taxonomy manager as a thin UI over Features 01–04, including hierarchy navigation, term forms, trigger metadata, active-state controls, validation errors, and concurrency-safe edits.

#### Observable Result

An authorized administrator can manage canonical taxonomy through `/admin/settings/reference-data/taxonomy` (or the root-approved equivalent) and immediately observe canonical hierarchy/trigger state without UI-local truth.

#### Cluster Build-Plan Link

Root Phase 4, Slice 4.1 — admin taxonomy manager.

#### Dependencies

- Features 01–04;
- root admin shell from Phase 3;
- SH-001/002;
- root UI/accessibility conventions.

#### In Scope

- admin taxonomy route;
- active/inactive filter;
- Domain/Category/Tag tree;
- create/edit forms;
- Category trigger metadata form;
- Tag verification trigger form;
- activate/deactivate controls with impact warning;
- expected-version field for stale-write detection;
- display of stable command errors;
- read-only diagnostics for effective-active state.

#### Out of Scope

- merge UI;
- reparent UI;
- AI suggestion review UI (Feature 08 integration only if ownership decides where review surface lives);
- generic admin shell;
- business entity classification editors;
- Search debug UI.

#### Module-Owned Data

No new model. UI acts on canonical Domain/Category/Tag.

#### Public Interfaces

Uses existing commands/queries; no direct Prisma or ad hoc route-only API.

#### Shared Operations Used

- **SH-001 / SH-002** at server route/action boundary. Local: taxonomy action/target. Prohibited duplicate: client-side role gate as authority.
- **SH-029** remains command-service responsibility; UI must not append audit independently.
- **SH-032** for request correlation where route/action framework does not already supply it.

#### Domain Logic

No business policy in components. Forms only collect validated input; services decide collisions, parent activity, stale writes, and transitions.

#### Authorization / Compliance

- server guards protect route and mutations;
- hiding a button is UX only, never authorization;
- trigger fields include explanatory labels that they are requirements/triggers, not completed compliance;
- no sensitive Verification/Healthcare payload is displayed.

#### Database / Transaction Behavior

None beyond command services. UI submits expected source version to prevent stale overwrite.

#### Events / Jobs

None directly.

#### Provider Integration

None.

#### UI / Admin Surface

This feature is the UI surface. Must include accessible labels, keyboard-operable hierarchy/actions, confirmation for deactivation, loading/disabled states, and non-destructive error presentation.

#### Failure Behavior

- stale edit → preserve form and show reload/review path;
- duplicate/collision → field-level safe message;
- deactivation conflict/impact warning → no partial UI assumption;
- unauthorized → root access-denied behavior;
- downstream Search handoff failure later remains an ops concern, not “save failed” if source truth committed.

#### Tests

- component: tree navigation/form validation/action states;
- authorization: direct route/action calls without permission fail;
- E2E: create Domain → Category → Tag → edit → deactivate/reactivate;
- stale concurrent editor E2E/integration;
- accessibility smoke tests;
- regression: UI does not contain direct Prisma/provider calls.

#### Documentation Updates

Update UI registry only if Workin Ants root standards require registration at implementation time. Do not copy BTLS UI registry conventions unless Workin Ants has independently adopted them.

#### Acceptance Criteria

- admin can complete core reference-data workflow;
- every mutation delegates to Module command service;
- permission and stale-write behavior is server-enforced;
- no hard-delete/reparent affordance exists;
- tests pass.

#### Exit Gate

Admin E2E plus all Feature 03 mutation tests pass. The UI must demonstrate source-of-truth refresh after mutation before Feature 06.

---

## Phase 4 — Shared-Operation and Search Handoff Integration

### 06 Audit, Domain Event, Idempotency, and Search Refresh Handoff

#### Objective

Complete the canonical side-effect behavior for accepted taxonomy changes: audit material mutations, publish minimized facts, and request Search projection refresh through SH-091 without making Search failure part of taxonomy truth.

#### Observable Result

A taxonomy mutation commits exactly once, produces the expected audit/event evidence, and produces an idempotent Search refresh request; a Search outage leaves taxonomy source truth intact and exposes retryable operational work.

#### Cluster Build-Plan Link

- Root Phase 4, Slice 4.1 — accepted taxonomy changes.
- Root Phase 4, Slice 4.4 — Search projection handoff.

#### Dependencies

- Features 03–05;
- SH-029, SH-044, SH-046, SH-091, SH-094;
- SH-037/047/048 if retrying failed refresh handoff;
- Search contract fixture or real Search Module interface.

#### In Scope

- finalize audit action vocabulary/metadata;
- transactional taxonomy event emission;
- source-versioned SH-091 calls for taxonomy term changes;
- SH-094 taxonomy source projection DTO if Search needs it;
- durable retry of post-commit Search handoff;
- operational visibility for failed handoff;
- no duplicate Search request on command replay.

#### Out of Scope

- Typesense/index worker;
- direct `SearchUpsertEvent` writes;
- affected business-entity fan-out beyond the taxonomy term while U-TAX-08 is unresolved;
- Search ranking/visibility rules.

#### Module-Owned Data

No Search model. Source data remains Domain/Category/Tag; outbox/idempotency records are platform infrastructure, not Module business truth.

#### Public Interfaces

- existing term commands gain finalized side-effect integration;
- SH-094 `buildSourceProjection` if required by Search.

#### Shared Operations Used

- **SH-029 `appendAuditEvent` — Audit.** Material admin proof; no local audit table.
- **SH-044 `executeIdempotentCommand` — platform.** One source mutation/side-effect intent per semantic command.
- **SH-046 `publishDomainEvent` — platform outbox.** Source fact publication.
- **SH-091 `requestSearchProjectionRefresh` — Search.** Request index/update/hide/restore; never direct Search row.
- **SH-094 `buildSourceProjection` — shared pattern/source owner.** Taxonomy safe source DTO.
- **SH-037 `recordIntegrationFailure` — Ops.** Failed Search contract/handoff visibility.
- **SH-047/048 — queue/retry.** Retry post-commit handoff when required. No local retry framework.

#### Domain Logic

- create/update activity changes calculate Search intent from accepted taxonomy change;
- deactivated taxonomy term requests hide/remove behavior according Search contract, not raw Typesense commands;
- reactivated term requests restore/update;
- event payload does not contain a disguised Search command;
- source version accompanies refresh request;
- command replay must not create divergent duplicate source changes.

#### Authorization / Compliance

No new authority beyond source command. Search refresh runs under system/module context and cannot broaden public visibility by itself; Search still composes its visibility policy.

#### Database / Transaction Behavior

Preferred pattern:

```text
source transaction:
  write taxonomy truth
  + persist outbox event / side-effect intent
commit
→ dispatch SH-091
→ retry independently if Search unavailable
```

Do not roll back already-committed valid taxonomy because Typesense/Search is down.

#### Events / Jobs

- SH-046 taxonomy change events;
- optional reliable job for Search handoff retries;
- dead-letter/manual review after retry exhaustion with source IDs/correlation only.

#### Provider Integration

None in Taxonomy. Search provider remains fully behind Search.

#### UI / Admin Surface

Admin UI may display a non-blocking “search refresh pending/failed” operational state only if root admin/ops UX provides it. Do not store a taxonomy `searchSynced` truth flag.

#### Failure Behavior

- Audit/outbox failure inside required atomic source transaction → follow root atomicity policy; do not silently omit required proof.
- Search unavailable after commit → retain source truth, retry, record Ops failure.
- duplicate dispatch → Search idempotency handles request; Taxonomy semantic key remains stable.
- unsupported Search entity/action → surface integration failure, never call Typesense directly.

#### Tests

- integration: command → audit + event + Search request;
- failure injection: Search unavailable after commit;
- idempotency: repeated command and repeated handoff;
- projection contract: SH-094 contains only approved term fields;
- architecture: no `SearchUpsertEvent` repository/import and no Typesense package under Module.

#### Documentation Updates

If Search's actual public contract differs from SH-091 assumptions, update this plan/architecture and Search interface documentation before code changes.

#### Acceptance Criteria

- accepted term mutations produce one logical side-effect set;
- Search outage cannot corrupt or roll back committed taxonomy truth;
- no direct Search DB/provider access exists;
- safe operational failure is visible/retryable;
- tests pass.

#### Exit Gate

Run Search contract/failure/idempotency tests. Feature 07 may not start production joins until U-TAX-01 is resolved regardless of Feature 06 success.

---

## Phase 5 — Cross-Module Workflow Integration

### 07 Entity Classification Contract Proof and Contextual Attachment Integration

#### Objective

Prove that contextual entity owners can attach/remove taxonomy through stable owner contracts and SH-023 without transferring their business lifecycles into Taxonomy.

#### Observable Result

At least one approved contextual owner can classify a real entity through public contracts, invalid/stale taxonomy is rejected, and Taxonomy never reaches into the owner's repository. The same contract pattern is proven for the other supported entity types through contract tests/fixtures.

#### Cluster Build-Plan Link

Root Phase 4, Slice 4.2 — entity taxonomy joins for ProfessionalProfile, CandidateProfile, Organization, Offering, Gig, and Job. Root plan mentions CustomerProfile “where needed”; no Customer taxonomy join exists in current supplied schema, so **do not invent one**.

#### Dependencies

- Features 01–06;
- **hard blocker: U-TAX-01 / PR-TAX-01 resolved**;
- U-TAX-02/03 resolved if assignment contract exposes `verified`/`confidence`;
- SH-123 target-owner contracts;
- contextual owner command/service for the first integrated entity type;
- SH-091 integration on the contextual owner side where Search requires entity refresh.

#### In Scope

If PR-TAX-01 is approved as proposed:

- define shared classification-assignment DTO consumed by contextual owners;
- contextual owner validates its entity/reference through its own repository;
- contextual owner calls SH-023;
- contextual owner writes its own join/direct `domainId`/`categoryId` truth transactionally;
- Taxonomy owns no join repository;
- contract tests for Professional, Candidate, Organization, Offering, Gig, Job shapes;
- direct Domain/Category consistency on Offering/Gig/Job assignment flows.

If architecture instead assigns one or more joins to Taxonomy, stop and update `module-architecture.md` before implementation; then this feature must be rewritten to reflect owner-specific repository and privacy effects.

#### Out of Scope

- adding CustomerProfile taxonomy schema without approved model;
- business publication/activation transitions;
- verification/healthcare approval;
- generic polymorphic “classify anything” DB repository;
- AI suggestion generation.

#### Module-Owned Data

Under PR-TAX-01, Taxonomy writes **no contextual join rows** in this feature. It supplies validation/source facts. Join source truth remains with contextual owners.

#### Public Interfaces

- SH-023 `validateTaxonomyAssignment`;
- SH-123 `validateOwnedTargetReference` where Taxonomy orchestration needs owner facts;
- stable Taxonomy vocabulary queries.

No Taxonomy `attachTagToAnyEntity` command is introduced under PR-TAX-01.

#### Shared Operations Used

- **SH-023 — Taxonomy.** Contextual owner's mandatory validation. Local policy: hierarchy/active/compatibility. Prohibited duplicate: owner-local tag validators.
- **SH-123 — target owner.** Validate target facts if a cross-Module orchestration layer invokes Taxonomy. Prohibited duplicate: foreign repository.
- **SH-015 — decision envelope.** Consistent assignment error result.
- **SH-091 — Search, normally called by contextual owner after its accepted classification mutation.** Prohibited duplicate: Search row/provider write.

#### Domain Logic

- classification owner supplies target lifecycle facts, not Taxonomy;
- Taxonomy validates only canonical classification semantics;
- contextual owner decides whether classification is required and when it may change;
- direct `domainId/categoryId` pair must be internally consistent;
- `TagSource` is explicit at write boundary; no misleading default reliance where actor provenance matters;
- unresolved cross-category Tag combinations fail safely.

#### Authorization / Compliance

Contextual owner handles actor/resource authority through its own service. Taxonomy must not infer organization membership, profile ownership, or business edit permission. Trigger outputs remain separate from readiness.

#### Database / Transaction Behavior

Under PR-TAX-01:

```text
context owner transaction:
  load/lock own entity
  obtain current taxonomy validation/source version
  validate assignment
  write own classification relation/direct fields
  write own outbox/search intent as approved
```

If atomicity between remote/module service calls and DB write cannot be guaranteed, revalidate source version and fail stale rather than treating cached taxonomy as permanent truth.

#### Events / Jobs

Contextual owner emits its own entity classification-changed fact. Taxonomy does not emit an assignment event for a join it does not own.

#### Provider Integration

None.

#### UI / Admin Surface

No generic classification editor is required inside Taxonomy. Contextual entity UI lives with the owning Module; it uses Taxonomy vocabulary queries/picker contracts.

#### Failure Behavior

- U-TAX-01 unresolved → feature remains blocked; no code workaround;
- target missing/ineligible → owner `NOT_FOUND`/forbidden;
- taxonomy invalid/inactive/stale → SH-023 denial;
- cross-category policy unresolved → review/denial;
- join unique conflict → contextual owner handles idempotently;
- Search refresh failure → contextual source truth persists and downstream effect retries.

#### Tests

- contract tests for each supported target type;
- integration with at least one real owner Module contract;
- no direct foreign repository access in Taxonomy;
- domain/category mismatch rejection;
- inactive term rejection;
- provenance explicitness;
- U-TAX-02 regression: `verified` not treated as Trust Verification;
- privacy ownership test consistent with approved join owner.

#### Documentation Updates

**Mandatory:** when U-TAX-01 is finally resolved, update:

- this Module architecture;
- relevant contextual Module architectures;
- Deep Module/ownership registry if necessary;
- Shared Operations documentation if the public assignment contract changes;
- this implementation plan before coding the production write path.

#### Acceptance Criteria

- no ambiguous shared ownership remains in implemented join path;
- one contextual owner can classify through SH-023 end-to-end;
- all supported target contracts have fixtures/tests;
- Taxonomy contains no foreign repositories;
- no new Customer taxonomy model was invented;
- tests pass.

#### Exit Gate

Architecture approval for U-TAX-01 plus passing cross-Module contract/integration tests is required. If approval is absent, mark Feature 07 blocked and proceed only to independent features that do not depend on join ownership.

---

### 08 AI Suggestion Acceptance Through SH-121

#### Objective

Integrate Taxonomy with AI Taxonomy so an approved, versioned AI suggestion can become accepted canonical taxonomy truth without Taxonomy invoking a foundation model or AI writing official taxonomy directly.

#### Observable Result

An authorized reviewer can select an AI suggestion, apply it through SH-121, and observe either a canonical term/approved assignment result or a stable validation conflict. Stale/rejected/superseded suggestions cannot mutate taxonomy.

#### Cluster Build-Plan Link

Root Phase 4, Slice 4.3 — AI taxonomy suggestions and accept/reject flow; rule: AI suggests, Taxonomy owns accepted truth.

#### Dependencies

- Features 02–06;
- Feature 07 only if the suggestion applies an entity join rather than canonical term creation;
- AI Taxonomy source schemas/contracts;
- SH-121;
- SH-123 for target validation where applicable;
- SH-029/044/046/091.

#### In Scope

- AI suggestion lookup contract;
- suggestion/version/staleness validation;
- authorized review/application command;
- canonical collision detection;
- hierarchy/effective-active validation;
- explicit reviewer reason;
- idempotent acceptance;
- audit/event/Search handoff;
- acknowledgement back to AI Taxonomy only through its public contract if required.

#### Out of Scope

- Bedrock invocation;
- prompt/version selection;
- model output parsing;
- AI suggestion generation/backfill;
- generic AI admin platform;
- automated employment decision;
- direct Search indexing.

#### Module-Owned Data

- Domain/Category/Tag mutation if reviewer explicitly approves a new canonical term;
- contextual assignment only if Feature 07 owner ruling explicitly permits the write in that owner.
- No `AiSuggestion`/`AiClassificationLog` write.

#### Public Interfaces

- **SH-121 `applyAiSuggestion`**;
- existing SH-023/079 and source mutation commands internally reused rather than bypassed.

#### Shared Operations Used

- **SH-121 — CL-02 AI↔Taxonomy contract.** Local: final taxonomy normalization/hierarchy/mutation. Prohibited duplicate: `acceptSuggestion.ts` that bypasses contract.
- **SH-079 — normalization.** Canonicalize proposed text.
- **SH-023 — assignment validity** where target classification is applied.
- **SH-123 — target owner facts** where applicable.
- **SH-001/002 — actor/authority** for reviewer.
- **SH-044 — idempotency.** Suggestion version + chosen mutation + reviewer command key.
- **SH-029 — audit.** Material AI acceptance/rejection override proof according policy.
- **SH-046 — domain event.** Accepted taxonomy fact.
- **SH-091 — Search refresh** after accepted source truth changes.

#### Domain Logic

- suggestion existence/version/provenance is confirmed by AI owner;
- stale/superseded/rejected suggestion cannot be applied;
- `TagSource.ai` records provenance where an accepted assignment is created, but does not bypass validation;
- if normalized term already exists, acceptance may resolve to existing canonical ID rather than create duplicate;
- if proposed parent/path is invalid or inactive, reject/review;
- no automatic acceptance solely from confidence score.

#### Authorization / Compliance

- reviewer/system actor must be authorized;
- AI output cannot make employment decisions;
- no sensitive candidate content is imported into Taxonomy acceptance payload beyond IDs/safe classification values;
- `verified` is not set as credential proof.

#### Database / Transaction Behavior

Use idempotent command transaction for the Taxonomy-owned mutation. AI source remains external; use suggestion version/hash/reference to prevent stale replay. Do not try to make a distributed DB transaction with AI Taxonomy.

#### Events / Jobs

- source taxonomy event on accepted mutation;
- no AI generation job;
- Search handoff via existing reliable mechanism.

#### Provider Integration

None. Confirm no SH-065/Bedrock call from Taxonomy.

#### UI / Admin Surface

If the review UI is hosted in Taxonomy admin, it must read AI suggestions through AI's public query and submit SH-121. If Admin Review or AI Taxonomy owns the final review queue UI, Taxonomy exposes the command only. Avoid duplicate review queues.

#### Failure Behavior

- AI service unavailable → no mutation; `DEPENDENCY_UNAVAILABLE`;
- suggestion stale/superseded → `taxonomy_ai_suggestion_stale`;
- canonical collision → reuse/review according policy, never duplicate;
- target invalid → no assignment;
- Search failure after accepted mutation → source truth remains; retry downstream effect.

#### Tests

- contract with AI Taxonomy fixtures;
- stale/superseded/rejected suggestion tests;
- duplicate canonical term acceptance;
- authorization;
- idempotency/replay;
- no provider import;
- Search/audit/event effects;
- candidate-data minimization regression.

#### Documentation Updates

If AI Taxonomy's actual schema/status vocabulary differs from the expected contract, update both Module architectures/contracts before integration.

#### Acceptance Criteria

- AI cannot write accepted taxonomy directly;
- Taxonomy cannot call model provider;
- one approved suggestion produces one accepted mutation;
- stale/duplicate suggestions are safe;
- tests pass.

#### Exit Gate

AI↔Taxonomy contract test suite and an end-to-end approved-suggestion fixture pass. No direct AI/Search table mutation is present.

---

### 09 CL-02 Search and Neighbor Contract Integration Proof

#### Objective

Prove Taxonomy behaves as a correct CL-02 source Module with real or contract-complete AI Taxonomy and Search interfaces, and prove representative downstream consumers use SH-022/023 rather than direct Taxonomy-table policy reconstruction.

#### Observable Result

A taxonomy change, an AI-accepted classification, and a consuming Module validation/readiness flow can execute through public contracts while Search remains rebuildable projection and consumers retain their own lifecycle truth.

#### Cluster Build-Plan Link

Root Phase 4 overall integration: 4.1 → 4.3 → 4.4, plus prerequisites for later Phase 5–8 consumers.

#### Dependencies

- Features 04, 06, 08;
- Feature 07 if entity attachment is part of the integration journey;
- Search SH-091/094 contract;
- AI SH-121 contract;
- at least one representative consumer of SH-022/023.

#### In Scope

- contract tests with Search and AI;
- one representative downstream requirement consumer (for example Professional Eligibility or Marketplace Supply) using SH-022;
- one contextual assignment consumer using SH-023 if Feature 07 is unblocked;
- Search source projection build and refresh acknowledgement;
- boundary/import checks.

#### Out of Scope

- implementing Search indexing internals;
- implementing Professional Eligibility/Marketplace business lifecycle;
- implementing AI generation;
- broad end-to-end marketplace user journey.

#### Module-Owned Data

No new source model.

#### Public Interfaces

Verifies:

- SH-022;
- SH-023;
- SH-079;
- SH-091 interaction;
- SH-094;
- SH-121.

#### Shared Operations Used

This feature verifies rather than reimplements the Shared Operations already introduced. Focus on SH-022/023/091/094/121/123 and SH-045 consumer event dedupe where an event contract is used.

#### Domain Logic

- Search indexes accepted source truth only;
- AI suggestions remain non-public until accepted;
- downstream consumer receives trigger facts, then performs its own readiness decision;
- no consumer copies a hardcoded trigger map;
- source projection is rebuildable from Taxonomy records.

#### Authorization / Compliance

Representative downstream workflow must prove authorization and compliance remain separate. A valid classification is not sufficient to activate/publish a regulated entity.

#### Database / Transaction Behavior

No cross-Module transaction. Source owners commit their own truth and integrate through idempotent commands/events.

#### Events / Jobs

- verify taxonomy event consumer idempotency if used;
- verify Search refresh retry does not duplicate business effects.

#### Provider Integration

No provider integration inside Taxonomy. Search/AI provider substitutions remain invisible behind their interfaces.

#### UI / Admin Surface

Optional admin diagnostic links only; no new UI required for exit.

#### Failure Behavior

- Search down → Taxonomy remains correct;
- AI down → only AI acceptance unavailable, manual taxonomy remains functional;
- consumer readiness owner down → trigger result can still exist, but consumer action handles unavailable readiness;
- contract version mismatch → fail visibly; no fallback direct DB access.

#### Tests

- contract version tests;
- integration: manual taxonomy change → SH-091;
- integration: AI suggestion → SH-121 → accepted term → SH-091;
- integration: accepted taxonomy → SH-022 → downstream owner query;
- source projection rebuild fixture;
- architecture/dependency graph test for forbidden direct imports.

#### Documentation Updates

Update public interface docs when real neighbor contracts are locked. If a dedicated CL-02 architecture/build plan now exists, reconcile this Module plan before continuing.

#### Acceptance Criteria

- CL-02 boundaries work without direct database coupling;
- Search remains projection;
- AI remains suggestion owner;
- downstream lifecycle remains with consumer;
- tests pass.

#### Exit Gate

All CL-02 contract/integration tests pass with provider clients mocked behind their owning Modules, not inside Taxonomy.

---

## Phase 6 — Durable Maintenance Work

### 10 Taxonomy Normalization / Backfill Worker

#### Objective

Provide a durable, dry-run-first maintenance worker to detect and, only when safe, repair normalization inconsistencies without automatic destructive merge behavior.

#### Observable Result

An authorized maintenance run can scan a bounded taxonomy scope, report canonical collisions/inconsistencies, safely apply non-destructive approved corrections, retry transient failures, and dead-letter ambiguous records for manual review.

#### Cluster Build-Plan Link

Root Phase 4, Slice 4.1 — tag normalization worker / reference-data maintenance.

#### Dependencies

- Features 02–06;
- SH-047/048/038/044/051/052;
- finalized normalization rule version from U-TAX-06;
- no SH-122 merge execution unless U-TAX-07 has separately been approved.

#### In Scope

- maintenance command to enqueue bounded scan;
- dry-run report;
- normalization-rule version;
- deterministic work payload;
- non-destructive correction path for approved display/slug normalization where collision-free;
- collision/manual-review reporting;
- queue telemetry/retry/dead-letter;
- idempotent replay.

#### Out of Scope

- automatic duplicate merge;
- automatic Category/Tag reparenting;
- direct foreign join migration;
- Search indexing implementation;
- AI generation.

#### Module-Owned Data

May update canonical Domain/Category/Tag only under existing mutation policy. QueueJob/ops records remain shared operational truth.

#### Public Interfaces

Restricted maintenance command, for example `requestTaxonomyNormalizationRun`, plus status available through Ops/queue tooling rather than a new taxonomy job table unless a Module-specific durable run record is explicitly required later.

#### Shared Operations Used

- **SH-047 `enqueueReliableJob` — shared queue.** Local: scope/payload/completion. Prohibited duplicate: taxonomy queue client.
- **SH-048 `executeRetryWithBackoff` — shared queue.** Local: retry classification. Prohibited duplicate: backoff helper.
- **SH-038 `recordQueueTelemetry` — Ops.** Local: safe counts/rule version.
- **SH-044 `executeIdempotentCommand` — platform.** Prevent duplicate maintenance effects.
- **SH-051/052 — concurrency.** Lock/compare before applying corrections.
- **SH-029/046/091** when an actual canonical term correction occurs.

#### Domain Logic

- dry-run is the default for new ruleset/version;
- only collision-free, policy-approved transformations can auto-apply;
- ambiguous canonical collision → manual review, never implicit SH-122 merge;
- stale record since scan → re-evaluate or skip;
- source mutation reuses normal command/domain policy, not raw worker updates.

#### Authorization / Compliance

Only authorized admin/system maintenance actor may enqueue execute mode. Trigger metadata changes are not part of normalization unless separately requested through normal Category/Tag command.

#### Database / Transaction Behavior

- bounded batches;
- per-term transaction/expected version;
- no long cross-system transaction;
- deterministic idempotency key: operation + ruleset version + scope + term/version where appropriate.

#### Events / Jobs

This feature owns the worker's business completion meaning but uses shared queue mechanics. Retry transient DB/integration failures. Permanent policy/collision errors dead-letter/manual-review with safe reason codes.

#### Provider Integration

None.

#### UI / Admin Surface

Optional maintenance trigger/dry-run report in admin reference-data tools; not required if ops tooling exposes the run safely.

#### Failure Behavior

- collision → manual review, not retry loop;
- stale term → re-read and re-evaluate;
- transient DB → retry;
- retry exhaustion → dead-letter/Ops incident candidate;
- partial run → completed items remain idempotent; rerun resumes safely.

#### Tests

- worker unit policy;
- dry-run vs execute fixtures;
- collision/manual-review;
- retry classification/dead-letter;
- idempotent rerun;
- concurrency with admin edit;
- Search/audit effects only for applied source changes.

#### Documentation Updates

If the worker requires a durable Taxonomy-owned run model rather than shared QueueJob visibility, that is an architecture change and must be documented before migration.

#### Acceptance Criteria

- normalization maintenance is durable/retryable/observable;
- no automatic merge/reparent occurs;
- dry-run and execute share the same decision logic;
- source mutations use normal policy and effects;
- tests pass.

#### Exit Gate

A fixture with clean records, safe normalizations, collisions, stale edits, and transient failures completes with correct outcomes and no duplicate effects.

---

### 11 Canonical Merge Capability — Conditional Architecture-Gated Feature

#### Objective

Implement SH-122 `mergeCanonicalRecord` only after U-TAX-07 establishes alias/history/retirement semantics and U-TAX-01/U-TAX-08 establish reference migration and Search impact ownership.

#### Observable Result

If approved, an administrator can dry-run and execute a compatible canonical term merge with full impact counts, concurrency control, idempotency, audit, reconciliation, and preserved references/history. If the architecture decisions are not approved, this feature remains explicitly **BLOCKED** and no substitute deletion/rename workflow is built.

#### Cluster Build-Plan Link

Supports Taxonomy foundation quality but is not required by the root Phase 4 MVP acceptance criteria. It is therefore subordinate/conditional and must not delay earlier MVP slices if merge is deferred.

#### Dependencies

- Features 03, 06, 10;
- **U-TAX-07 resolved**;
- **U-TAX-01 resolved**;
- **U-TAX-08 resolved**;
- SH-122, SH-051, SH-044, SH-047/048, SH-029/046/091;
- approved alias/history schema if required.

#### In Scope

Only when approved:

- compatible source/target validation;
- dry-run impact plan;
- reference migration through the correct owner interfaces/repositories;
- canonical target selection;
- source post-merge state according approved lifecycle;
- audit/events/Search refresh;
- reconciliation/rollback plan;
- dead-letter/manual review.

#### Out of Scope

- generic cross-domain merges;
- hard deletion as merge substitute;
- merging across incompatible hierarchy without explicit policy;
- foreign repository mutation through Taxonomy if contextual owners own joins.

#### Module-Owned Data

Depends on approved U-TAX-07 schema. Do not create alias/merge/history models speculatively.

#### Public Interfaces

- SH-122 internal/admin maintenance operation only after approval;
- no broad public user command.

#### Shared Operations Used

- **SH-122 `mergeCanonicalRecord` — Taxonomy Proposed shared op.** Local: taxonomy merge compatibility/provenance. Prohibited duplicate: `mergeAnyEntity`.
- **SH-051 `acquireAggregateLock`** on source/target/hierarchy keys.
- **SH-044** idempotency.
- **SH-047/048** durable migration work if multi-batch.
- **SH-029/046/091** proof/events/search effects.
- **SH-123** owner interface if contextual references must be migrated by their owners.

#### Domain Logic

Must be defined by the approved U-TAX-07 ruling. At minimum no merge can lose provenance or silently change a target to a term in an incompatible hierarchy.

#### Authorization / Compliance

High-impact admin action. Use SH-001/002; consume SH-014 only if root security policy classifies it as step-up-required. Compliance-trigger changes caused by merge must be auditable and downstream consumers refreshed.

#### Database / Transaction Behavior

Use database locks and bounded transactional migration. Do not hold one giant cross-Module transaction. Cross-owner reference migrations require resumable owner commands and reconciliation.

#### Events / Jobs

Durable migration worker if approved. Terminal policy mismatch goes to manual review; transient technical failures retry.

#### Provider Integration

None.

#### UI / Admin Surface

Only after architecture/schema is approved: impact preview, typed confirmation, progress, failure/reconciliation visibility. No “delete duplicate” shortcut.

#### Failure Behavior

- architecture decision missing → feature blocked;
- incompatible hierarchy → reject;
- active concurrent edit → conflict/retry;
- partial owner migration → resumable/reconcile; never declare completed early;
- Search failure → retry after source/reference migration remains correct.

#### Tests

If enabled:

- dry-run impact accuracy;
- concurrent merge/edit;
- idempotent resume;
- reference counts before/after;
- provenance/history preservation;
- partial failure/reconciliation;
- Search/audit/event effects;
- no hard-delete loss.

#### Documentation Updates

Mandatory architecture/schema/ownership updates before any implementation. The completion report must name the decision IDs resolved.

#### Acceptance Criteria

Either:

1. feature is explicitly marked blocked/deferred with no unsafe substitute; **or**
2. approved merge policy is implemented with complete tests and reference reconciliation.

#### Exit Gate

No production merge command exists unless U-TAX-07/U-TAX-01/U-TAX-08 are resolved and every merge safety test passes.

---

## Phase 7 — Privacy, Compliance, and Boundary Verification

### 12 Privacy Executor, Retention, and Compliance Boundary Proof

#### Objective

Register the Module correctly with Privacy and prove that taxonomy trigger evidence, generic audit, and subject-data handling remain separate from downstream compliance/readiness truth.

#### Observable Result

Privacy can enumerate/execute instructions against records Taxonomy actually owns, canonical reference terms are retained/deactivated according approved policy, and compliance tests prove Taxonomy cannot satisfy verification/healthcare readiness by itself.

#### Cluster Build-Plan Link

Cross-cutting support for root Privacy/Location phase and the compliance gates consumed by later Professional Supply, Hiring, and Search phases. This does not change root sequencing; production Privacy integration may be activated when the root privacy rail is available.

#### Dependencies

- Features 04, 07 if joins are implemented;
- SH-095/096/097/098;
- Privacy owner protocol;
- approved U-TAX-01 ownership;
- Trust/Healthcare public readiness interfaces for boundary tests where available.

#### In Scope

- subject-data inventory for Taxonomy-owned records;
- SH-096 enumeration handler;
- SH-095 executor result contract;
- SH-097 retention fact handler;
- SH-098 only if an approved owned personal field requires anonymization;
- tests proving reference terms are not indiscriminately erased;
- tests proving contextual join privacy goes to approved owner;
- compliance boundary integration tests.

#### Out of Scope

- PrivacyRequest/DataErasureJob orchestration;
- global schema crawling;
- legal retention adjudication;
- healthcare/verification readiness implementation;
- sensitive-access system unless future Taxonomy payload becomes sensitive.

#### Module-Owned Data

Usually canonical terms only. If PR-TAX-01 assigns joins to contextual owners, Taxonomy has little/no direct person-subject data. If the final ruling assigns joins here, this feature must be expanded before production.

#### Public Interfaces

- SH-096 `enumerateSubjectData` implementation for Taxonomy;
- SH-095 `executePrivacyInstruction` target handler;
- SH-097 retention facts;
- SH-098 anonymization invocation only where applicable.

#### Shared Operations Used

- **SH-095 — Privacy orchestrates; Taxonomy executes owned target action.** Local: record disposition. Prohibited duplicate: local privacy job.
- **SH-096 — enumerate owned subject data.** Local: taxonomy inventory. Prohibited duplicate: generic DB crawler.
- **SH-097 — retention facts.** Local: reference/historical dependency facts. Prohibited duplicate: retention exemption table.
- **SH-098 — shared anonymization mechanism.** Local: approved field mapping. Prohibited duplicate: blanket null/delete helper.
- **SH-029 / SH-030** remain separate generic proof interfaces as required by root privacy/audit policy.

#### Domain Logic

- canonical terms are platform reference data, not user-owned profile fields;
- do not erase a canonical Tag because a privacy subject once used it;
- remove/anonymize only subject relationships actually owned here and only per approved instruction/retention decision;
- requirement triggers remain taxonomy facts after unrelated user erasure if still valid reference data;
- audit records are handled by Audit owner, not deleted by Taxonomy executor.

#### Authorization / Compliance

Privacy instruction is trusted only through Privacy's authenticated/orchestrated target protocol. No user endpoint may call internal erasure methods directly. Compliance boundary tests must prove trigger ≠ completion.

#### Database / Transaction Behavior

Owner-specific privacy operations are idempotent. Return typed `erased/anonymized/retained/detached/skipped/retryable_failure/terminal_failure` result according canonical Privacy envelope. Do not mutate foreign records.

#### Events / Jobs

Privacy owns orchestration/job. Taxonomy may publish a domain event if an owned relationship is actually detached and downstream Search needs refresh, using existing outbox/Search handoff.

#### Provider Integration

None.

#### UI / Admin Surface

None required.

#### Failure Behavior

- unknown privacy target → typed skipped/not-owned result;
- retention requirement → return retained fact/reference, not local exemption creation;
- contextual join owned elsewhere → return not-owned/route ownership as protocol allows;
- transient DB → retryable failure;
- unsupported disposition → terminal/review result.

#### Tests

- privacy inventory;
- idempotent executor;
- reference term retention;
- contextual join owner routing;
- compliance: verification/healthcare trigger does not pass readiness;
- audit separation;
- Search refresh only when an owned source relationship change warrants it.

#### Documentation Updates

If final U-TAX-01 changes privacy ownership, update architecture and privacy inventory before implementation. Record retention assumptions settled in U-TAX-11 if applicable.

#### Acceptance Criteria

- Privacy owns orchestration;
- Taxonomy executor touches only owned records;
- reference vocabulary is not erased as personal data by default;
- compliance/readiness boundaries are proven in tests;
- tests pass.

#### Exit Gate

Privacy contract tests and compliance boundary tests pass with no direct Privacy/Trust/Healthcare repository access.

---

# Module Integration Phase

Features 07–09 collectively form the mandatory Module integration phase. The minimum integration proof before Taxonomy is considered usable by the platform is:

```text
real/contract-complete target owner
→ SH-023 classification validation
→ approved contextual classification write by its owner
→ SH-022 trigger resolution
→ downstream owner readiness query where required
→ source-owner Search refresh through SH-091
```

and:

```text
AI Taxonomy AiSuggestion
→ authorized SH-121 apply
→ Taxonomy canonical validation/mutation
→ Taxonomy event/audit
→ Search refresh request
→ Search reads SH-094 source projection
```

No integration test may “simplify” this by directly writing neighboring tables.

---

## Phase 8 — Hardening and Production Verification

### 13 Concurrency, Replay, Security, Performance, and Production Hardening

#### Objective

Prove the completed Taxonomy Module remains correct under concurrency, retries, stale consumers, large vocabulary reads, worker failures, Search/AI outages, privacy execution, and hostile/invalid input before declaring the Module production-ready for downstream features.

#### Observable Result

The Module passes a production-oriented test matrix; source truth remains correct during failure injection; no prohibited duplicate infrastructure or direct cross-Module coupling is present; and unresolved decisions are either resolved or explicitly block only the affected optional capability.

#### Cluster Build-Plan Link

Root Phase 4 acceptance/hardening and root Phase 12 production hardening. This feature does not accelerate or skip root launch gates.

#### Dependencies

- Features 01–10 and 12;
- Feature 11 only if merge was approved;
- production-grade shared operations;
- real or contract-complete Search/AI/Role/Identity/Ops interfaces;
- finalized progress tracker and architecture-dependency scan.

#### In Scope

- concurrent create/rename/update/deactivate tests;
- idempotency/replay tests for every externally retryable command;
- stale `updatedAt`/source-version tests;
- Search outage and retry exhaustion;
- AI outage/stale suggestion;
- queue replay/partial worker failure;
- authorization bypass attempts;
- runtime validation fuzz/negative cases;
- large taxonomy-tree query/index analysis;
- N+1/query-count checks;
- event/audit payload minimization;
- privacy executor failure/replay;
- dependency/import scan;
- migration/backfill rehearsal from clean and realistic fixture DB;
- unresolved-decision gate report.

#### Out of Scope

- new domain capabilities;
- adding merge just to satisfy hardening if Feature 11 is deferred;
- expanding taxonomy to moderation/search ranking/recommendations/general AI;
- resolving legal/compliance policy without authoritative evidence.

#### Module-Owned Data

No new business model expected. Any schema change discovered during hardening requires architecture review and its own migration scope.

#### Public Interfaces

All current Taxonomy public commands/queries must remain backward-compatible within the approved versioning policy. No “hardening-only” bypass APIs.

#### Shared Operations Used

Verify all previously used operations rather than adding private alternatives. Focus:

- SH-044 replay;
- SH-051/052 concurrency;
- SH-046/045 event reliability;
- SH-047/048 worker retry/dead-letter;
- SH-029 audit completeness;
- SH-032–038 telemetry safety;
- SH-091/094 Search outage/rebuild behavior;
- SH-095–098 privacy idempotency;
- SH-121 AI boundary;
- SH-123 cross-Module target access.

#### Domain Logic

- database constraints win races;
- stale data never silently overwrites newer source truth;
- ambiguous/unresolved policy never defaults to “allowed”;
- source truth remains reconstructable independently of Search;
- manual taxonomy functions remain usable if AI is unavailable;
- a failed Search projection cannot become a taxonomy status;
- effective-active semantics are deterministic at scale.

#### Authorization / Compliance

- direct server action/API calls without UI must be denied correctly;
- inactive/private admin data cannot leak through public vocabulary query;
- telemetry/audit contains no unnecessary foreign sensitive data;
- trigger/readiness separation holds across all integration fixtures.

#### Database / Transaction Behavior

- clean database migration + seed rehearsal;
- index/query-plan check for active hierarchy and tag lookup;
- contention tests around unique normalized sibling creation;
- no long-running lock across external Module calls;
- worker batches bounded and restartable;
- rollback behavior verified for failed source transactions.

#### Events / Jobs

- duplicate outbox delivery produces one consumer effect;
- retry exhaustion visible in Ops/dead-letter;
- backfill replay safe;
- source events include schema/source version and correlation.

#### Provider Integration

Taxonomy must still have zero provider client. Failure tests use owning Module interfaces, not Bedrock/Typesense mocks imported into Taxonomy.

#### UI / Admin Surface

- admin performance with realistic hierarchy size;
- stale edit/duplicate conflict UX;
- deactivation confirmation/impact display;
- no destructive hidden path.

#### Failure Behavior

Every failure maps to a stable safe category. Unknown/unsupported cross-Module/provider values are surfaced as unavailable/review rather than silently mapped. Failed operational effects are observable without overwriting business truth.

#### Tests

- unit full suite;
- integration/database full suite;
- authorization/security negative suite;
- concurrency/idempotency/replay suite;
- worker retry/dead-letter suite;
- Search/AI outage suite;
- privacy suite;
- E2E admin suite;
- migration/seed-from-empty suite;
- performance/query-count checks;
- architecture dependency scan.

#### Documentation Updates

- progress tracker;
- resolved U-TAX decisions in architecture;
- Shared Operations registry only if a canonical contract legitimately changed;
- relevant dependency interface docs;
- no speculative future features.

#### Acceptance Criteria

- all source truth has one approved owner;
- no direct foreign table/provider access exists;
- concurrent/replayed commands are safe;
- Search/AI outages cannot corrupt taxonomy;
- privacy/audit/observability remain separate;
- admin workflow is server-authorized and accessible;
- migration/seed rehearsal passes;
- every unresolved decision is listed with its blocked capability;
- standard project checks pass.

#### Exit Gate

The Module is production-ready for the approved MVP scope only when:

1. canonical typecheck/lint/format/build commands pass;
2. all Module unit/integration/auth/concurrency/privacy/E2E tests pass;
3. clean migration + seed succeeds twice idempotently;
4. Search/AI outage tests preserve taxonomy source truth;
5. dependency scan finds no prohibited provider/foreign repository/local shared-infrastructure duplication;
6. U-TAX-01 is resolved before any production join integration is marked complete;
7. optional blocked features such as merge remain disabled rather than partially implemented.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | 01 Canonical Taxonomy Contracts and Repository Foundation; 02 Controlled-Term Normalization and Idempotent Seed Baseline |
| 2 | Core Taxonomy Lifecycle and Decisions | 03 Domain, Category, and Tag Administration Commands; 04 Assignment Validation and Taxonomy Requirement Resolution |
| 3 | Public/Admin Surface | 05 Taxonomy Administration Surface and Protected Reference-Data Reads |
| 4 | Shared-Operation and Search Handoff Integration | 06 Audit, Domain Event, Idempotency, and Search Refresh Handoff |
| 5 | Cross-Module Workflow Integration | 07 Entity Classification Contract Proof and Contextual Attachment Integration; 08 AI Suggestion Acceptance Through SH-121; 09 CL-02 Search and Neighbor Contract Integration Proof |
| 6 | Durable Maintenance Work | 10 Taxonomy Normalization / Backfill Worker; 11 Canonical Merge Capability — Conditional Architecture-Gated Feature |
| 7 | Privacy, Compliance, and Boundary Verification | 12 Privacy Executor, Retention, and Compliance Boundary Proof |
| 8 | Hardening and Production Verification | 13 Concurrency, Replay, Security, Performance, and Production Hardening |

**Total numbered features: 13**  
**Production-critical MVP core:** 01–10, 12–13, with Feature 07 gated by join-ownership resolution.  
**Conditional/deferred:** Feature 11 unless SH-122/U-TAX-07 is approved.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture.
2. Read root code standards.
3. Read the Canonical Shared Operations Registry/Architecture.
4. Read CL-02 architecture/build plan if they now exist; otherwise read Cluster Registry CL-02 and root build-plan Phase 4.
5. Read this Module architecture and implementation plan.
6. Read public-interface sections for direct dependencies used by the feature.
7. Check the current status of U-TAX-01 through U-TAX-12.
8. Confirm the previous feature's exit gate.
9. Produce the required feature implementation specification below.
10. Implement only that feature.
11. Run required quality checks and feature-specific tests.
12. Verify public contracts rather than reaching into neighboring DB tables.
13. Update `progress-tracker.md`.
14. Update architecture only when a binding decision legitimately changed.
15. Record unresolved risks, blocked decisions, and deferred work.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise implementation specification containing:

- **Feature:** exact number/name.
- **Objective:** one result.
- **Observable result:** what becomes testable/visible.
- **Dependencies:** prior feature exit gates, dependency interfaces, Shared Operations, schema prerequisites.
- **In scope:** exact files/behaviors to implement.
- **Out of scope:** neighboring responsibilities explicitly excluded.
- **Owned data affected:** Taxonomy models/enums/events/projections only.
- **Public contracts:** commands, queries, events, executor interfaces.
- **Shared operations consumed:** permanent IDs and invocation points.
- **Permissions/compliance:** actor/authority/trigger/readiness/privacy requirements.
- **Primary workflow:** ordered command/query flow.
- **Provider integration:** normally `none` for Taxonomy; if non-none, stop and reconcile architecture.
- **Jobs/events:** durable work and fact events.
- **Idempotency/concurrency:** keys, transactions, locks/version checks.
- **Error behavior:** stable result/reason codes.
- **Tests:** exact unit/integration/auth/concurrency/E2E categories.
- **Acceptance criteria:** concrete observable requirements.
- **Documentation updates:** files changed only if decisions/contracts changed.

Do **not** generate all later feature specifications in advance. The feature specification must reflect the repository and architecture state immediately before that feature begins.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed**
- **Files added**
- **Files changed**
- **Database changes**
- **Migrations**
- **Dependencies added**
- **Module public interfaces added/changed**
- **Shared Operations reused**
- **Events/jobs added**
- **Provider adapter changes** — expected to be `none` for this Module; explain any exception as an architecture issue
- **Tests added/changed**
- **Commands run**
- **Manual/contract verification**
- **Documentation updated**
- **Assumptions**
- **Known failures**
- **Remaining risks**
- **Deferred work**
- **Unresolved decision status** — U-TAX IDs relevant to the feature
- **Exit-gate result** — PASS / FAIL / BLOCKED, with evidence

A feature is not complete because code exists. It is complete only after its exit gate passes or it is explicitly marked **BLOCKED** by an unresolved governing decision.

---

# Final Quality Check for This Plan

Before treating this plan as executable context, verify:

1. Canonical Domain/Category/Tag source truth has exactly one owner.
2. Join ownership conflict is not silently hidden; Feature 07 is gated by U-TAX-01.
3. AI suggestion truth remains AI-owned and accepted taxonomy remains Taxonomy-owned.
4. Search remains projection and SH-091/094 are the only Taxonomy/Search boundary described.
5. Every shared operation is consumed rather than duplicated.
6. Shared mechanism / separate truth boundaries are explicit for audit, events, jobs, concurrency, decisions, projections, and privacy.
7. Cross-Module reads use public owner interfaces.
8. No provider adapter has been imported into Taxonomy.
9. Compliance triggers remain separate from verification/healthcare/readiness completion.
10. Privacy orchestration remains Privacy-owned.
11. The sequence aligns with root Phase 4 rather than inventing a competing Cluster roadmap.
12. Every numbered feature includes tests, acceptance criteria, and an exit gate.
13. Conditional merge behavior is blocked until architecture supports it.
14. A coding agent can implement the approved features without inventing ownership or shared infrastructure.
