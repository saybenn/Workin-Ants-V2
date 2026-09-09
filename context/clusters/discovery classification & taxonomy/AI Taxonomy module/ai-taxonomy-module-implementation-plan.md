# AI Taxonomy Implementation Plan

> **Module ID:** `ai_taxonomy`  
> **Module:** AI Taxonomy Module  
> **Primary Cluster:** `CL-02 — Discovery, Classification & Visibility`  
> **Repository target:** `context/modules/ai_taxonomy/implementation-plan.md`  
> **Plan status:** Ordered implementation plan subordinate to root/CL-02 build sequencing; features that depend on Proposed Rulings or Unresolved Decisions are explicitly gated

---

## Core Principle

Implement AI Taxonomy through narrow, verifiable slices:

```text
observable command/query/admin behavior
→ runtime-validated request
→ trusted actor + owner-supplied source context
→ AI Taxonomy policy
→ authoritative AiClassificationLog / AiSuggestion write or read
→ canonical shared-operation calls
→ provider/queue effect where applicable
→ Taxonomy-owned acceptance handoff
→ audit/ops/privacy effects
→ tests
→ exit gate
```

The Module does not need a public consumer UI to be valid. Its primary observable behavior is a durable classification-run lifecycle, validated proposal records, public Module contracts, provider adapter, worker/backfill process, and protected review evidence.

The implementation plan deliberately separates **basic safe AI suggestions** from advanced AI automation. The root Workin Ants build plan places AI suggestions in Phase 4.3 but allows advanced AI taxonomy to be deferred from the compressed first MVP. Therefore the first implementation should prioritize correctness, provenance, explicit human/domain acceptance, and safe provider boundaries over autonomous breadth.

---

## Build Rules

1. Follow root architecture, code standards, Canonical Shared Operations, and CL-02 sequencing.
2. `AiClassificationLog` and `AiSuggestion` are the only proposed AI business records for MVP; do not add generic AI tables by convenience.
3. AI Taxonomy owns proposal/run truth only.
4. Taxonomy & Classification owns accepted terms and accepted entity classification.
5. Search / Public Visibility owns `SearchUpsertEvent`, Typesense, index/de-index, and search APIs.
6. Consume source entities through approved owner public interfaces; never add direct cross-domain repositories.
7. Public commands and provider output are runtime validated.
8. Every protected mutation/query is authenticated/authorized server-side.
9. Provider input is purpose-bound, minimized, redacted, and hashed before inference.
10. Provider details stay behind a provider-neutral port and Bedrock adapter.
11. External effects are idempotent where possible and effectively-once at the domain-effect level.
12. Jobs use canonical durable queue/retry/dead-letter mechanics.
13. Lifecycle transitions use database transactions, shared locking/concurrency primitives, and explicit transition policy.
14. Raw private candidate data, PHI, prompts containing source content, and raw provider responses are not logged.
15. No AI output may implement an automated employment decision.
16. No feature may create direct Search indexing from a generated suggestion.
17. Every numbered feature ends with tests and an exit gate.
18. Every feature must update `progress-tracker.md` after completion.
19. Proposed Rulings are not silently accepted by code. If a feature depends on one, approval/reconciliation is a precondition.
20. Unresolved architecture must be surfaced and can legitimately block production activation.

---

## Preconditions

### Hard platform dependencies before Module implementation begins

- repository/context foundation and canonical quality commands;
- Prisma/Postgres baseline and migration discipline;
- CL-01 authenticated actor and Role / Authority public interfaces;
- CL-09 baseline Audit / Event Ledger and Observability / Ops interfaces required by root sequencing;
- Canonical Shared Operations implementation or stable stubs/contracts for the operations used by the current feature;
- Taxonomy foundation (`TaxonomyDomain`, `TaxonomyCategory`, `TaxonomyTag`, `TagSource`) before semantic AI validation;
- current `schema.prisma` inspected to confirm AI models remain absent before Feature 01 migration work.

### Hard architecture approvals before schema commitment

Feature 01 must not commit Prisma schema until the following architecture choices are approved or revised:

- PR-AI-02 minimal two-model MVP record set;
- proposed run/suggestion lifecycle enums;
- target type and initial supported target set;
- PR-AI-04 taxonomy-reference storage strategy or an explicitly non-FK first version;
- PR-AI-05 confidence representation;
- PR-AI-11 no raw source/raw provider body persistence by default.

### Provider dependencies

The provider port and tests may be built before live credentials exist. Live Bedrock execution requires:

- approved AWS account/credential/secret boundary;
- approved model and region;
- timeout/rate/token budget;
- provider retention/logging configuration appropriate to the data sensitivity used in that environment.

Candidate/private/healthcare production execution remains disabled until the applicable policy questions are resolved.

### Dependency interfaces that may initially be stubbed

Because CL-02 is built before several source Modules become feature-complete, the AI core may use contract fakes for:

- Offering / ProfessionalProfile source DTOs until CL-03 Phase 5;
- Organization / Job source DTOs until CL-06 Phase 8;
- Candidate privacy-safe skill source DTO until CL-06 Phase 8;
- Privacy orchestration callback registration until CL-08 formal Privacy build phase.

A stub is allowed only at the interface boundary. Do not compensate for a missing dependency by reaching into its database table.

### Build-plan sequencing rule

The implementation is intentionally split between:

```text
Root Phase 4.3 — core AI proposal capability
→ Root Phase 5 — Professional/Offering source integration
→ Root Phase 8 — Organization/Job/Candidate source integration
→ Root Phase 10 — formal Privacy orchestration integration
→ Root Phase 12 — production hardening
```

This Module plan does not reorder those root milestones.

---

# Phase 1 — Source-of-Truth and Contract Foundation

## 01 AI Run and Suggestion Schema Foundation

### Objective

Add the approved minimal Prisma source-of-truth foundation for AI classification runs and proposals without adding provider, Taxonomy acceptance, Search, or backfill implementation.

### Observable Result

The database can persist a valid AI run and its proposed suggestions with explicit lifecycle/status, provenance fields, constraints, and history-preserving relationships. Clean migrations apply successfully.

### Cluster Build-Plan Link

Supports root **Phase 4.3 — AI taxonomy suggestions** by supplying the missing `AiClassificationLog` and `AiSuggestion` records named by the Registry/Glossary.

### Dependencies

- root schema/source-of-truth baseline;
- Taxonomy parent tables present;
- approved PR-AI-02, lifecycle enum decisions, confidence representation, taxonomy-reference storage decision;
- current Prisma schema confirmed to contain no previous AI model implementation.

### In Scope

- add approved AI-owned enums;
- add `AiClassificationLog`;
- add `AiSuggestion`;
- add relationships/indexes/check constraints supported by Prisma/Postgres;
- add migration;
- add model-level comments/ownership annotations if project conventions support them;
- add DB helper fixtures/factories for tests.

### Out of Scope

- Bedrock SDK/provider calls;
- public request command;
- queue worker;
- Taxonomy acceptance/rejection implementation;
- Search writes/indexing;
- admin UI;
- `AiBackfill` model;
- prompt database table;
- source-owner adapters;
- raw source or provider-payload persistence.

### Module-Owned Data

- `AiClassificationLog`;
- `AiSuggestion`;
- approved AI-specific enums/statuses.

No external source-of-truth model is modified.

### Public Interfaces

None required yet. Repository-internal types may be generated, but no consumer should query Prisma directly just because models now exist.

### Shared Operations Used

- **SH-053 `transitionLifecycleState`** — shared mechanism; local run/suggestion transition policy will later use it. No duplicate state-machine framework.
- **SH-052 `withOptimisticConcurrency`** — shared persistence primitive if the approved schema includes a version field. Do not hand-roll an alternative concurrency package.

### Domain Logic

Enforce at schema/domain-test level:

- every suggestion belongs to one run;
- every suggestion begins in `proposed`;
- one `candidateKey` cannot be duplicated within the same run;
- confidence is within the approved range;
- controlled-vocabulary and free-text suggestion shapes cannot be mixed incorrectly;
- terminal run/suggestion states are represented by status, not loose booleans;
- provider/model/request references are provenance only;
- no field claims accepted taxonomy truth.

### Authorization / Compliance

No user-facing data path yet. Schema must still avoid introducing fields such as `isHired`, `verified`, `public`, `compliancePassed`, `searchable`, or local privacy/hold flags.

### Database / Transaction Behavior

- migration must be append-only;
- apply from a clean database and representative existing schema;
- use explicit indexes for target/run/status queries;
- no cascade behavior may silently redefine Taxonomy term deletion semantics;
- use database check/unique constraints where Prisma/project conventions support them;
- do not make `providerRequestId` the business primary key.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

- migration conflict or unsupported schema decision blocks feature completion;
- if Taxonomy FK deletion semantics remain unresolved, use the explicitly approved logical-reference design or stop; do not guess a cascade policy;
- invalid constraints must fail at write time rather than normalize silently.

### Tests

- Prisma validation;
- clean migration apply;
- migration on representative existing database;
- valid run insert;
- valid suggestion insert;
- confidence range rejection;
- duplicate candidate key rejection;
- invalid shape/required-field tests;
- relationship/delete-behavior tests;
- no accidental `SearchUpsertEvent` or Taxonomy row mutation.

### Documentation Updates

- mark U-AI-04 and any settled schema questions resolved in `module-architecture.md`;
- update root ownership/schema inventory if required;
- update `progress-tracker.md` with migration name and decisions.

### Acceptance Criteria

- `AiClassificationLog` and `AiSuggestion` exist with approved semantics;
- schema contains no extra generic AI business tables;
- migration is reproducible;
- constraints reject invalid proposal shapes/duplicates;
- source-of-truth ownership remains unambiguous.

### Exit Gate

Run and pass the repository's canonical:

```text
prisma format/validate
migration validation from clean DB
schema/integration tests
typecheck
lint/format checks
```

Do not begin Feature 02 until the migration and architecture decisions are documented.

---

## 02 Public Contracts, Repositories, and Prompt-Version Foundation

### Objective

Create the Module's public command/query contract types, owned repositories, reason-code vocabulary, and immutable prompt/output-contract registry without yet invoking a live model.

### Observable Result

Consumers can compile against explicit AI Taxonomy interfaces, tests can create/read runs through repositories, and a prompt version resolves deterministically to a prompt hash and output-schema version.

### Cluster Build-Plan Link

Supports **Phase 4.3** provider boundary, prompt/version logging, and later admin accept/reject workflow.

### Dependencies

- Feature 01;
- root runtime validation pattern;
- SH-001/002 contracts;
- canonical result/error pattern;
- approved prompt persistence ruling (code/config for MVP unless changed).

### In Scope

- `index.ts` public export boundary;
- command/query DTOs and runtime schemas;
- stable `AI_*` reason codes;
- `AiClassificationLogRepository` and `AiSuggestionRepository` owning only local tables;
- immutable prompt registry keyed by target/purpose/version;
- deterministic prompt hash/output schema version metadata;
- provider-neutral contract type declarations without Bedrock implementation;
- source resolver contract type declaration;
- tests proving internal repository files are not required by consumers.

### Out of Scope

- model invocation;
- queue execution;
- source owner integrations;
- Taxonomy acceptance mutation;
- Search integration;
- admin UI;
- dynamic prompt editor/database.

### Module-Owned Data

Reads/writes Feature 01 models only in repository tests. Prompt definitions remain code/config under current Proposed Ruling and are snapshotted into run fields later.

### Public Interfaces

Define stable type surfaces for:

```text
requestClassificationSuggestions
cancelClassificationRun
enqueueClassificationBackfill
getSuggestionsForTarget
getSuggestionForDecision
getClassificationRun
listSuggestionsForReview
recordSuggestionDisposition   # Proposed integration contract
```

The functions need not all be executable yet; contracts are versioned and validated.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor`** — expected protected-call context.
- **SH-002 `authorizeResourceAction`** — action vocabulary and decision integration contract.
- **SH-032 `createRequestContext`** — correlation DTO expectations.
- **SH-044 `executeIdempotentCommand`** — public command idempotency envelope contract.

Local policy includes AI action names, reason codes, and semantic command identity. Prohibit local `auth.ts`, `permissions.ts`, `idempotency.ts` frameworks.

### Domain Logic

- public DTOs never accept provider-native types;
- `requestClassificationSuggestions` accepts target identity/purpose, not trusted raw source content;
- prompt resolution is target/purpose-specific and immutable by version;
- prompt hash is deterministic;
- output schema version is explicit;
- candidate-purpose contracts carry explicit advisory/non-employment-decision semantics;
- public read DTOs omit raw provider bodies and secrets.

### Authorization / Compliance

Define the proposed Role action vocabulary but do not implement a second permission matrix. Backfill/review/run-detail actions are marked restricted.

### Database / Transaction Behavior

Repository methods:

- operate only on `AiClassificationLog` and `AiSuggestion`;
- require transaction context where a state transition spans both;
- do not accept generic table/model names;
- support expected-version writes for mutable lifecycle rows.

### Events / Jobs

Only contract placeholders/types where required. Do not publish events yet.

### Provider Integration

Only provider-neutral port types; no AWS import.

### UI / Admin Surface

None.

### Failure Behavior

- invalid public DTO → `AI_*` validation code;
- unsupported target/purpose → explicit unsupported result;
- missing prompt version → `AI_CONFIGURATION_UNAVAILABLE`;
- repository not-found/conflict → stable Module error, not Prisma exception leakage.

### Tests

- runtime command/query validation;
- public export contract tests;
- prompt version/hash determinism;
- invalid target/purpose tests;
- repository boundary tests;
- no AWS/Typesense/Taxonomy repository import from public contracts;
- reason-code snapshot/compatibility tests.

### Documentation Updates

- record final public contract names;
- update Role / Authority dependency interface documentation if action vocabulary is accepted;
- update progress tracker.

### Acceptance Criteria

- one explicit public Module boundary exists;
- contracts are provider-neutral and runtime validated;
- repositories access only AI-owned models;
- prompt/output versions are deterministic and immutable;
- no live external effect occurs.

### Exit Gate

Contract/unit/repository tests, typecheck, lint, and architecture boundary check pass. Feature 03 may begin only after contract naming is stable enough for Taxonomy integration.

---

# Phase 2 — Taxonomy-Constrained Validation and Provider Boundary

## 03 Taxonomy Vocabulary Snapshot and Structured Output Validation

### Objective

Build the deterministic path that constrains provider-shaped output to the active Taxonomy vocabulary and converts only valid typed output into proposal inputs.

### Observable Result

Given a trusted source fixture and a model-output fixture, the Module can build a versioned Taxonomy snapshot, strictly parse output, reject unknown/invalid taxonomy references, and produce deterministic proposed-suggestion inputs without a live provider.

### Cluster Build-Plan Link

Directly supports root **Phase 4.3** JSON schema validation and the rule that AI output must be validated before it can become Taxonomy or Search truth.

### Dependencies

- Features 01–02;
- Taxonomy foundation Phase 4.1;
- Taxonomy public tree/read contract;
- SH-023, SH-066, SH-072, SH-077, SH-079.

### In Scope

- load active Taxonomy vocabulary through Taxonomy public query;
- build deterministic minimal vocabulary snapshot;
- compute taxonomy snapshot hash/version reference;
- implement exact provider-output runtime schema(s);
- reject unknown fields;
- validate suggested term IDs/path through Taxonomy;
- normalize allowed controlled-term/free-text output;
- map validated output to `AiSuggestion` creation inputs;
- candidate key generation;
- zero-suggestion valid result support;
- fixture-only orchestration test.

### Out of Scope

- direct Taxonomy Prisma reads/writes;
- new Taxonomy term creation;
- live Bedrock call;
- source entity production adapters;
- accepting/rejecting proposals;
- Search refresh.

### Module-Owned Data

May persist test/integration `AiClassificationLog` and `AiSuggestion` data through repositories. No neighboring source truth changes.

### Public Interfaces

No new external command required. Internal services support the existing request pipeline contracts.

### Shared Operations Used

- **SH-023 `validateTaxonomyAssignment`** — Taxonomy owner validates term/path semantics; local code must not duplicate it.
- **SH-066 `validateStructuredProviderOutput`** — strict parsing; local schema remains AI-owned.
- **SH-079 `normalizeControlledTerm`** — Taxonomy normalization; AI does not invent its own term normalization.
- **SH-077 `buildCanonicalTextSnapshot`** — deterministic snapshot construction.
- **SH-072 `hashCanonicalPayload`** — taxonomy/input snapshot hashes.

### Domain Logic

- accepted output schema is target/purpose specific;
- `domain`, `category`, and `tag` outputs reference existing allowed terms only;
- a category must be semantically compatible with the proposed domain/path according to Taxonomy;
- a tag must meet Taxonomy's current allowed assignment/path rules;
- provider confidence is range checked but not interpreted as acceptance;
- duplicate outputs collapse to deterministic proposal keys before insert;
- invalid output creates no `AiSuggestion` rows;
- skill output remains normalized advisory text and does not create Taxonomy terms.

### Authorization / Compliance

No public actor path is added. Test fixtures must include candidate-use restrictions so validation cannot return hiring-decision-shaped fields.

### Database / Transaction Behavior

For fixture integration:

```text
validate output
→ begin transaction
→ verify run is running/current
→ persist bounded validated output summary
→ insert unique proposed suggestions
→ mark run completed
→ commit
```

Invalid output marks/fails the run only through the approved run policy; never partially insert suggestions.

### Events / Jobs

None required.

### Provider Integration

No live provider. Provider-shaped fixtures exercise the same schemas that the future adapter returns.

### UI / Admin Surface

None.

### Failure Behavior

- malformed JSON/shape → `AI_OUTPUT_INVALID`;
- unknown field → `AI_OUTPUT_INVALID`;
- inactive/missing term → `AI_TAXONOMY_REFERENCE_INVALID`;
- invalid hierarchy/path → same semantic category with safe reason detail;
- Taxonomy temporarily unavailable → retryable dependency result; no suggestion creation.

### Tests

- every output schema success/failure branch;
- unknown-field rejection;
- malformed confidence;
- invalid term ID;
- inactive term;
- invalid path;
- duplicate proposal dedupe;
- zero-result success;
- skill text normalization;
- no Taxonomy write;
- atomic no-partial-suggestion persistence.

### Documentation Updates

- document approved output-schema version names;
- resolve any Taxonomy path/assignment contract changes;
- update progress tracker.

### Acceptance Criteria

- untrusted provider output cannot enter `AiSuggestion` without both structural and semantic validation;
- output is constrained to current controlled vocabulary for taxonomy suggestions;
- Taxonomy remains the semantic owner;
- test fixtures prove deterministic results.

### Exit Gate

All validation/domain/database tests pass; a code review confirms there is no AI-owned taxonomy repository or term creation path.

---

## 04 Foundation Model Port and AWS Bedrock Adapter

### Objective

Implement the provider-neutral foundation-model invocation boundary and the first AWS Bedrock adapter without exposing provider types or trusting provider output.

### Observable Result

The application can call the provider port using a minimized classification request, receive a normalized provider result, map transient/permanent errors consistently, and hand successful structured output to Feature 03 validation.

### Cluster Build-Plan Link

Supports root **Phase 4.3 — AI provider adapter boundary** and prompt/model provenance.

### Dependencies

- Features 02–03;
- SH-065 Proposed Ruling approved for current use;
- SH-061, SH-065, SH-066, SH-078;
- root secrets/config boundary;
- approved Bedrock model/region for non-sensitive development fixtures.

### In Scope

- `FoundationModelProvider` port;
- Bedrock adapter;
- request serialization;
- model key → provider model mapping;
- timeout/abort handling;
- token/output bounds;
- normalized provider request reference;
- error translation;
- safe telemetry hooks;
- fake provider adapter for deterministic tests;
- adapter contract tests.

### Out of Scope

- direct call from browser/server action;
- candidate/private/healthcare production activation before policy approval;
- provider webhook table;
- generic platform AI service for unrelated Modules;
- model-driven tool execution;
- AI agent/autonomous workflow.

### Module-Owned Data

No new model. Provider/model/request references will later be written to `AiClassificationLog` as provenance.

### Public Interfaces

No new consumer-facing command. Provider port is internal to AI Taxonomy/provider infrastructure boundary.

### Shared Operations Used

- **SH-065 `invokeFoundationModel`** — canonical proposed provider-adapter capability; local prompt/output meaning remains AI-owned.
- **SH-061 `translateProviderStatus`** — provider error/result mapping.
- **SH-066 `validateStructuredProviderOutput`** — adapter success is still untrusted until next validation stage.
- **SH-078 `minimizeAndRedactProviderInput`** — mandatory immediately before external call; source owner supplies field policy.
- **SH-032 `createRequestContext`**, **SH-034 `sanitizeTelemetryMetadata`**, **SH-035 `captureException`**, **SH-036 `emitMetric`**, **SH-037 `recordIntegrationFailure`** — telemetry/failure boundary.
- **SH-048 `executeRetryWithBackoff`** — used by worker/application orchestration, not hidden recursive adapter retry loops unless canonical policy permits.

### Domain Logic

- adapter receives only provider-ready DTO, never a Prisma entity;
- prompt definition/version is selected outside the Bedrock transport mapping;
- provider/model provenance is returned in normalized result;
- provider success cannot mark run complete by itself;
- unknown provider status/error maps to explicit unsupported/permanent/review result;
- no provider response can add public fields to output by bypassing Feature 03 schema.

### Authorization / Compliance

Provider adapter has no authorization logic. The caller must already have passed actor/source/sensitivity policy. Tests assert adapter is not exported as a public feature service.

### Database / Transaction Behavior

No DB transaction spans the network call. The worker records `running`, calls provider outside a long DB transaction, then opens a short persistence transaction for validated result.

### Events / Jobs

None new; later worker calls adapter.

### Provider Integration

Provider-specific work is entirely here. No webhook verification/dedup table because no callback flow is confirmed.

### UI / Admin Surface

None.

### Failure Behavior

Normalize at least:

- timeout/network → retryable;
- throttled/capacity → retryable with backoff;
- invalid credentials/config/model → terminal/operator action;
- provider rejection/unsupported request → terminal or review-required according to safe mapping;
- unknown → explicit terminal/review, never success.

No raw AWS exception leaves the adapter.

### Tests

- adapter contract with fake client;
- request field allowlist;
- source/private fields absent;
- timeout;
- throttling;
- auth/config failure;
- unknown provider error;
- provider request ID capture;
- telemetry redaction;
- no AWS types in public/domain contract;
- successful output still fails if Feature 03 schema invalid.

### Documentation Updates

- record model/region/config decisions that are actually approved;
- update provider/library docs as required;
- keep U-AI-02 open for any unresolved retention/sensitive-data configuration;
- progress tracker.

### Acceptance Criteria

- one provider-neutral port exists;
- Bedrock is replaceable without rewriting domain services;
- private/source data is minimized before call;
- provider result never bypasses validation;
- operational failure is visible through canonical Ops.

### Exit Gate

Provider contract/unit tests, typecheck, lint, and a non-sensitive development integration smoke test pass if live credentials are available. Live smoke is not required to fake policy approval for sensitive lanes.

---

# Phase 3 — Durable Classification Execution and Read Surface

## 05 Classification Request Command, Source Resolver Registry, and Durable Worker

### Objective

Make `requestClassificationSuggestions` produce a durable queued run and execute it asynchronously through one registered source resolver, provider port, validation pipeline, and atomic persistence path.

### Observable Result

A caller with an authorized target can request suggestions and receive a run ID. A worker processes the run with a fake or registered source adapter, writes valid proposals, and exposes explicit failed/cancelled/completed state without duplicate effects.

### Cluster Build-Plan Link

Completes the core executable portion of root **Phase 4.3** for AI suggestions, while leaving source-specific adapters to later phases.

### Dependencies

- Features 01–04;
- SH-001/002/003/044/047/048/051/052/053;
- queue infrastructure;
- at least one fake/test source resolver; production source resolvers may remain unregistered until Features 08–10.

### In Scope

- executable `requestClassificationSuggestions`;
- source resolver registry keyed only by approved target type;
- target/source version resolution;
- run semantic idempotency identity;
- create queued run;
- enqueue worker;
- claim/lock and transition to running;
- resolve safe source snapshot;
- build/minimize/hash provider payload;
- invoke provider;
- validate output;
- atomically persist suggestions + completed run;
- retry/permanent failure handling;
- cancellation race handling;
- safe run failure codes;
- queue telemetry.

### Out of Scope

- direct production Offering/Job/Candidate Prisma access;
- Taxonomy acceptance/rejection;
- broad backfill;
- public Search refresh;
- user notifications;
- source-change automatic reclassification events.

### Module-Owned Data

- `AiClassificationLog` creation and lifecycle;
- `AiSuggestion` creation on validated success.

### Public Interfaces

- activate `requestClassificationSuggestions`;
- activate `cancelClassificationRun` if approved;
- source-resolver registration remains internal integration contract.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor`**;
- **SH-002 `authorizeResourceAction`**;
- **SH-003 `queryOwnerFacts`** where owner relationship facts are needed;
- **SH-044 `executeIdempotentCommand`**;
- **SH-047 `enqueueReliableJob`**;
- **SH-048 `executeRetryWithBackoff`**;
- **SH-051 `acquireAggregateLock`**;
- **SH-052 `withOptimisticConcurrency`**;
- **SH-053 `transitionLifecycleState`**;
- **SH-072 `hashCanonicalPayload`**;
- **SH-077 `buildCanonicalTextSnapshot`**;
- **SH-078 `minimizeAndRedactProviderInput`**;
- observability SH-032..038.

Local policy defines run identity, target/purpose support, source resolver selection, retryability, and terminal result.

### Domain Logic

Primary workflow:

```text
validate command
→ resolve actor
→ authorize target/action
→ resolve source adapter + source version
→ resolve taxonomy/prompt/output configuration
→ compute semantic request identity
→ idempotently create/return queued run
→ enqueue run
→ worker claims run and aggregate lock
→ re-resolve source/config if policy requires
→ mark running
→ canonicalize/minimize/hash payload
→ provider call
→ strict output + Taxonomy validation
→ atomically write suggestions + completed run
→ emit safe telemetry
```

Stale source/config handling must be explicit. An old run may finish as failed/superseded/stale according to approved policy; it must not masquerade as current merely because provider returned later.

### Authorization / Compliance

- browser supplies target identity, not trusted source content;
- source resolver is responsible for owner-approved DTO;
- provider call is skipped if source sensitivity/purpose says denied/unavailable;
- candidate/healthcare production source adapters are not registered until their feature gates are complete.

### Database / Transaction Behavior

- short transaction for run creation/idempotency claim;
- no network call inside DB transaction;
- DB-backed aggregate lock around conflicting run effect where required;
- final transaction writes validated output, suggestions, terminal run state, and any approved outbox event;
- retry never partially duplicates suggestions.

### Events / Jobs

- `processClassificationRun` worker implemented through SH-047;
- retries through SH-048;
- dead-letter/terminal failure visible through Ops;
- no domain event required yet unless PR-AI-01 has an approved consumer.

### Provider Integration

Uses Feature 04 port. Fake provider must remain available for deterministic tests.

### UI / Admin Surface

No UI required. Observable via command/query/database integration test.

### Failure Behavior

- authorization/unsupported target: no run/provider call;
- source unavailable: explicit run/request outcome based on whether run was created;
- privacy denied: provider never invoked;
- provider transient: retry bounded;
- provider terminal: run failed;
- invalid output: run failed, zero suggestions;
- DB finalization failure: retry/replay safely without duplicate suggestions;
- cancellation: terminal semantics enforced.

### Tests

- full fake-provider happy path;
- duplicate command replay;
- same idempotency key/different payload conflict;
- concurrent interactive requests;
- worker claim collision;
- source stale before invocation;
- source stale after provider return;
- cancellation vs worker claim;
- transient provider retry;
- terminal provider failure;
- invalid output no suggestions;
- finalization retry no duplicate candidates;
- provider not called on denied source.

### Documentation Updates

- document actual semantic idempotency key fields;
- settle any stale-source transition policy;
- update progress tracker and worker registration docs.

### Acceptance Criteria

- one request produces one durable semantic run effect;
- successful run produces only validated proposed suggestions;
- failure/cancellation is explicit;
- no direct source/Taxonomy/Search database coupling exists;
- queue/provider retries are observable.

### Exit Gate

All worker/idempotency/concurrency/integration tests pass; queue dead-letter behavior is manually verified in a test environment; typecheck/lint/build pass.

---

## 06 Public Queries and Protected AI Review Evidence

### Objective

Expose safe, authorized read interfaces for targets, individual suggestions, run evidence, and review lists, with an optional thin admin review page.

### Observable Result

Authorized consumers can inspect proposals and provenance without direct Prisma access or raw provider/private-data leakage. Unauthorized actors cannot inspect restricted run details.

### Cluster Build-Plan Link

Supports root **Phase 4.3** admin/user review flow and operational reviewability.

### Dependencies

- Feature 05;
- Role / Authority read actions;
- Audit sensitive-access contract if required;
- UI shell/admin route if a screen is built.

### In Scope

- executable `getSuggestionsForTarget`;
- `getSuggestionForDecision`;
- `getClassificationRun`;
- `listSuggestionsForReview` with pagination/filtering;
- safe DTO selectors;
- authorization per query;
- sensitive-output redaction;
- protected admin read page/list if repository UI standards and root admin shell exist;
- clear labels: “AI suggestion”, “not accepted classification”.

### Out of Scope

- accepting/rejecting Taxonomy truth;
- generic Admin Review/Hold case lifecycle;
- public Search result;
- exposing raw provider request/response;
- editing prompt/model configuration.

### Module-Owned Data

Reads `AiClassificationLog` and `AiSuggestion` only.

### Public Interfaces

All four public queries become stable/usable.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor`**;
- **SH-002 `authorizeResourceAction`**;
- **SH-003 `queryOwnerFacts`** where target-owner relationship is needed;
- **SH-030 `recordSensitiveAccess`** when policy requires;
- **SH-032/033/034** for safe request/log context.

### Domain Logic

- proposal status is shown separately from accepted Taxonomy state;
- confidence label includes “model confidence” semantics, not correctness;
- run detail exposes prompt/model/version identifiers, not secret prompt source data unless specifically permitted;
- candidate suggestions include explicit advisory restriction;
- filters do not become new source state.

### Authorization / Compliance

Test matrix includes source owner/editor, unrelated user, admin/support, system. Restricted backfill/run failure metadata is not public.

### Database / Transaction Behavior

- paginated indexed reads;
- avoid N+1 run/suggestion queries;
- no mutation except optional AccessAuditLog external call;
- bounded result sizes.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

If implemented:

- thin table/detail view;
- state badges clearly labeled as AI proposal/run state;
- no Taxonomy join mutation;
- no raw provider JSON dump;
- accessibility/loading/error/empty states per root UI rules.

### Failure Behavior

- unauthorized → denied;
- not found → stable AI code;
- sensitive evidence not allowed → redacted/denied, not partial raw leak;
- dependency owner facts unavailable → unavailable, not authorization bypass.

### Tests

- query authorization matrix;
- pagination/filter tests;
- redaction tests;
- candidate advisory labels/contracts;
- N+1/query-count review where infrastructure supports it;
- UI component/admin route authorization tests if UI added.

### Documentation Updates

- add public query contracts to dependency handout;
- update UI registry only if new components exist;
- progress tracker.

### Acceptance Criteria

- consumers no longer need AI Prisma access;
- protected run/suggestion data is correctly scoped;
- proposal vs accepted truth is unmistakable;
- no raw provider/private payload is exposed.

### Exit Gate

Query/authorization/redaction tests pass; any admin page passes component/E2E route-guard tests; typecheck/lint/build pass.

---

# Phase 4 — Module Integration Phase

This phase proves AI Taxonomy collaborates with its primary neighbors through public contracts. It must not reach into neighboring repositories. Features 08–10 deliberately occur when the corresponding root phases make those source Modules real.

## 07 Taxonomy Acceptance / Rejection Handoff and Search Boundary

### Objective

Complete the AI side of the proposal → Taxonomy decision handshake while proving that Search refresh occurs only from accepted Taxonomy truth.

### Observable Result

Taxonomy can read an AI proposal through `getSuggestionForDecision`, accept or reject it through its own workflow, and communicate the disposition back to AI Taxonomy exactly once. AI records the disposition but never writes the accepted classification or Search queue.

### Cluster Build-Plan Link

Bridges root **Phase 4.3 AI suggestions** to **Phase 4.1/4.2 Taxonomy accepted truth** and **Phase 4.4 Search projection**.

### Dependencies

- Features 01–06;
- Taxonomy accept/reject workflow/public interfaces;
- U-AI-10 resolved: direct application command vs Taxonomy outbox event;
- Search SH-091 available to **Taxonomy**, not AI generation;
- SH-045/046 if event-driven.

### In Scope

AI Taxonomy side:

- stable `getSuggestionForDecision` contract;
- `recordSuggestionDisposition` implementation/event handler;
- idempotent accepted/rejected status transition;
- authoritative Taxonomy decision reference storage;
- contradiction handling;
- integration contract tests proving no AI write to taxonomy/search tables.

Cluster coordination test:

```text
AI proposed suggestion
→ Taxonomy validates current term/path + target rules
→ Taxonomy writes accepted/rejected truth
→ Taxonomy publishes/calls disposition fact
→ AI updates proposal status
→ if accepted classification changed searchable source, Taxonomy calls Search refresh
```

### Out of Scope

- implementing Taxonomy join lifecycle inside AI Taxonomy;
- changing Taxonomy architecture ownership;
- AI-triggered Typesense or `SearchUpsertEvent` write;
- automatic acceptance based on confidence;
- generic human-review case system.

### Module-Owned Data

Updates `AiSuggestion.status`, decision reference/reason/time only.

### Public Interfaces

- `getSuggestionForDecision`;
- `recordSuggestionDisposition` or equivalent approved event consumer.

### Shared Operations Used

- **SH-023 `validateTaxonomyAssignment`** — owned by Taxonomy during decision path;
- **SH-044 `executeIdempotentCommand`** — AI disposition command if direct;
- **SH-045 `deduplicateDomainEvent`** — if event-driven;
- **SH-046 `publishDomainEvent`** — Taxonomy-owned decision event mechanism if selected;
- **SH-052 `withOptimisticConcurrency`** and **SH-053 `transitionLifecycleState`** — AI disposition transition;
- **SH-091 `requestSearchProjectionRefresh`** — asserted as Taxonomy/Search boundary; AI does not call on generation.

### Domain Logic

- only `proposed` can become accepted/rejected;
- identical repeated decision replays;
- accepted then rejected (or inverse) through same decision identity is conflict;
- AI status does not prove which taxonomy join was written; decision reference points to Taxonomy proof;
- Taxonomy term deactivation after acceptance does not let AI reverse accepted business truth.

### Authorization / Compliance

Trusted Module-to-Module/system context for disposition. Human actor authorization belongs to Taxonomy's acceptance workflow, not duplicated in AI.

### Database / Transaction Behavior

AI disposition is one short expected-version transaction. If asynchronous after Taxonomy commit, temporary lag is acceptable; accepted Taxonomy truth remains authoritative.

### Events / Jobs

If event-driven, consumer inbox dedupe is mandatory. No disguised “accept this suggestion” event emitted by AI.

### Provider Integration

None.

### UI / Admin Surface

A composed Taxonomy admin screen may show AI evidence, but the accept/reject control calls Taxonomy. AI UI code must not mutate taxonomy joins.

### Failure Behavior

- Taxonomy decision succeeds but AI disposition update temporarily fails → retry AI consumer; do not roll back accepted Taxonomy truth;
- duplicate decision → replay;
- contradictory decision → conflict/manual investigation;
- suggestion missing → explicit integration failure with decision reference.

### Tests

- accept path;
- reject path;
- duplicate decision event;
- contradictory disposition;
- stale AI version;
- Taxonomy acceptance still authoritative during delayed AI update;
- generated proposal produces no Search event;
- accepted Taxonomy change produces Search refresh through Taxonomy/Search interface;
- no direct Prisma cross-writes.

### Documentation Updates

- settle U-AI-10 and event/command schema;
- update Taxonomy public-interface documentation;
- update Search integration note if canonical contract changes;
- progress tracker.

### Acceptance Criteria

- one-owner-per-lifecycle is proven end-to-end;
- AI proposal disposition mirrors, never replaces, Taxonomy decision;
- Search sees only accepted source change;
- failure is retryable without ambiguous truth.

### Exit Gate

Cross-Module contract/integration tests pass and a code review confirms no AI repository imports Taxonomy/Search Prisma models.

---

## 08 ProfessionalProfile and Offering Source Integration

### Objective

Activate AI classification for ProfessionalProfile and Offering targets through CL-03 owner-approved source DTOs when those Modules reach the required build milestone.

### Observable Result

An authorized Professional/Marketplace workflow can request classification for a real ProfessionalProfile or Offering; AI Taxonomy receives only the owner-approved versioned source snapshot and persists validated proposals.

### Cluster Build-Plan Link

Extends root **Phase 4.3** when **Phase 5 — Professional Supply & Readiness** supplies real source records/interfaces.

### Dependencies

- Feature 05 core pipeline;
- Feature 07 Taxonomy decision contract for complete workflow;
- Professional Eligibility public source interface;
- Marketplace Supply public source interface;
- source Modules built sufficiently in root Phase 5;
- source-specific authorization facts.

### In Scope

AI-side integration adapters that call owner public interfaces for:

- `professional_profile` classification input;
- `offering` classification input;
- source version token;
- allowed public/private fields and sensitivity metadata;
- target owner facts used by Role;
- integration tests using real owner services.

### Out of Scope

- creating/editing ProfessionalProfile or Offering;
- publish/readiness decisions;
- direct AI mutation of `ProfessionalCategory`, `ProfessionalTag`, `OfferingTag` or any Taxonomy join;
- provider input fields not explicitly approved by source owners;
- Search indexing.

### Module-Owned Data

AI run/suggestion records created for these target types.

### Public Interfaces

No new generic command. Existing `requestClassificationSuggestions` becomes available for registered Professional/Offering target types.

### Shared Operations Used

- SH-001/002/003 for actor/authority/owner facts;
- SH-077/078 for canonical/minimized provider payload;
- SH-023/079 for Taxonomy semantics;
- core worker/provider shared operations from Feature 05.

### Domain Logic

- source DTO version controls staleness/idempotency;
- only owner-allowlisted fields enter provider payload;
- publication/readiness fields may influence whether classification is useful, but AI does not own readiness;
- accepted classification still flows through Taxonomy.

### Authorization / Compliance

Professional/source owner Role policy determines who can request/read suggestions for the target. AI does not infer ownership from `requestedByUserId` alone.

### Database / Transaction Behavior

No source-owner transaction is held open during provider call. Source version is rechecked according to stale-result policy before finalization.

### Events / Jobs

Existing classification worker. Automatic source-change events remain out of scope unless an approved event contract is added.

### Provider Integration

Existing port/Bedrock adapter. No source Module calls Bedrock directly.

### UI / Admin Surface

Source UI may offer “suggest classification” using AI public command. It must label proposals and send acceptance through Taxonomy workflow.

### Failure Behavior

- source target not found/private/unavailable → no provider call;
- source version changes → stale result handling, not silent overwrite;
- source DTO violates contract → integration failure/operator action.

### Tests

- real owner-service contract tests;
- authorized vs unrelated actor;
- allowlisted source fields only;
- stale source update during provider execution;
- AI suggestion cannot publish/activate Offering;
- accepted term requires Taxonomy flow;
- no direct source Prisma access.

### Documentation Updates

- add exact owner source DTO contracts to Professional/Marketplace public-interface docs;
- update dependency map/progress tracker.

### Acceptance Criteria

- both target types classify end-to-end through owner interfaces;
- provider sees only approved fields;
- source lifecycle remains external;
- no accepted classification/search write occurs in AI path.

### Exit Gate

Professional/Offering contract tests and at least one controlled end-to-end test pass; root Phase 5 dependency versions are recorded.

---

## 09 Organization and Job Source Integration

### Objective

Activate advisory classification for Organization and Job targets through Organization Hiring owner interfaces without absorbing Job Compliance or hiring decisions.

### Observable Result

Authorized organization workflows can request Organization/Job taxonomy suggestions from real source snapshots, and the resulting proposals remain separate from Job Compliance and publication decisions.

### Cluster Build-Plan Link

Extends root **Phase 4.3** when **Phase 8 — Organization Hiring and Candidate Pipeline** supplies Organization/Job source contracts.

### Dependencies

- Feature 05;
- Feature 07;
- Organization Hiring public source interfaces and Role owner facts;
- Job Compliance boundary documented;
- root Phase 8 source records available.

### In Scope

- AI-side `organization` and `job` source resolvers;
- purpose-specific field allowlists;
- source version/stale handling;
- taxonomy suggestion pipeline;
- explicit guard that output is classification only.

### Out of Scope

- Job create/edit/publish state;
- pay-transparency, EEOC, Fair Chance, or other Job Compliance decisions;
- applicant ranking/selection;
- Organization membership lifecycle;
- direct JobTag/OrganizationTag mutation.

### Module-Owned Data

AI runs/suggestions for Organization/Job targets.

### Public Interfaces

Existing request/query contracts gain activated target support once registry/contract configuration says enabled.

### Shared Operations Used

SH-001/002/003, SH-077/078, SH-023/079, core provider/queue operations.

### Domain Logic

- classification prompt/output cannot include a “compliant/noncompliant”, “good candidate”, or employment decision result;
- a suggested verification-sensitive Category is only a possible Taxonomy trigger after acceptance;
- Job Compliance remains separate and may consume accepted Taxonomy later.

### Authorization / Compliance

Organization Role/owner facts come from Organization Hiring. Job Compliance status is not interpreted by AI Taxonomy unless source owner explicitly withholds or limits input.

### Database / Transaction Behavior

Same source-version and run-finalization rules as Feature 08.

### Events / Jobs

Existing worker; no new Job workflow event consumption unless later approved.

### Provider Integration

Existing provider boundary.

### UI / Admin Surface

Optional classification-suggestion affordance in Job/Organization UI; no compliance badge/decision derived from AI result.

### Failure Behavior

- source unavailable/unauthorized → denied/unavailable;
- job compliance data not approved for provider → excluded, not copied;
- stale Job edit during run → stale handling.

### Tests

- owner-interface contract;
- organization authorization;
- no Job Compliance mutation;
- no automated employment-decision fields in output;
- stale Job source;
- no direct Job/Organization repository access.

### Documentation Updates

Organization Hiring and AI interface docs; progress tracker.

### Acceptance Criteria

Real Organization/Job requests work through owner interfaces, classification remains advisory, and compliance/hiring truth is untouched.

### Exit Gate

Cross-module tests pass with root Phase 8 implementation; review confirms no `evaluateJobCompliance` duplication or AI-driven Job publication.

---

## 10 Candidate Skill / Classification Integration with Privacy Guardrails

### Objective

Activate candidate skill/classification suggestions only through an explicitly privacy-safe Candidate Application & Resume Privacy contract and enforce the prohibition on automated employment decisions.

### Observable Result

A permitted candidate-controlled/internal workflow can request skill/classification suggestions from an owner-approved candidate snapshot; denied/private fields never reach the model, and the output cannot be consumed as a hiring rank/rejection decision.

### Cluster Build-Plan Link

Extends root **Phase 4.3** during **Phase 8 — Candidate Pipeline**, while respecting Candidate Search privacy and later CL-08 Privacy orchestration.

### Dependencies

- Features 05–07;
- Candidate Application & Resume Privacy public source contract;
- U-AI-08 raw-text policy resolved enough for production;
- sensitive-access policy;
- approved provider configuration for candidate data.

### In Scope

- candidate source resolver using owner-approved normalized fields;
- candidate purpose allowlist;
- SH-078 minimization/redaction;
- explicit no-hiring-decision output schema;
- skill suggestion normalization;
- subject-data references for Privacy inventory;
- sensitive access audit where required;
- tests proving provider non-invocation on privacy denial.

### Out of Scope

- resume parsing;
- raw resume storage;
- CandidateSearchProjection generation;
- candidate ranking/boost;
- application stage/rejection/hiring decision;
- employer-facing private resume access;
- direct search projection.

### Module-Owned Data

Candidate-targeted AI runs/suggestions only; these are personal-data inventory targets.

### Public Interfaces

Existing request/query contracts with candidate-specific restriction metadata. No hiring decision API is introduced.

### Shared Operations Used

- SH-001/002/003;
- **SH-030 `recordSensitiveAccess`** where policy requires;
- SH-077/078;
- SH-023/079;
- SH-095/096/097/098 preparation for privacy;
- core provider/queue operations.

### Domain Logic

- prefer normalized/owner-approved skills and profile fields;
- raw resume text is denied unless U-AI-08 explicitly allows exact fields/purpose;
- prompt/output schemas cannot request “fit score”, “hire score”, rejection reason, protected-attribute inference, or selection ranking;
- skill suggestion confidence cannot be used as employer decision score;
- consumer DTO carries advisory-use restriction.

### Authorization / Compliance

- Candidate owner/privacy policy gates source access;
- Role authorizes requester/action;
- candidate data transmission may be `denied` or `unavailable` even when actor is otherwise authorized;
- sensitive AccessAuditLog is distinct from run log.

### Database / Transaction Behavior

- no raw resume text in `AiClassificationLog`;
- output retention/anonymization fields comply with Feature 12 policy;
- subject references are enumerable for Privacy.

### Events / Jobs

Existing classification worker. No automated application workflow events triggered by AI output.

### Provider Integration

Live provider path enabled only for approved candidate-data configuration. Otherwise fake/non-production or disabled path returns explicit restriction.

### UI / Admin Surface

If shown to candidates/admins, label as suggested skills/classification. Do not expose as employer ranking signal.

### Failure Behavior

- privacy denial → no provider call, explicit `AI_PRIVACY_RESTRICTED`;
- sensitive provider configuration unavailable → `AI_CONFIGURATION_UNAVAILABLE`/restricted;
- unsupported raw-text request → validation/policy denial;
- output attempts forbidden employment fields → `AI_OUTPUT_INVALID`.

### Tests

- raw resume field exclusion;
- privacy denial no provider call;
- sensitive access audit call;
- forbidden hiring field output rejected;
- candidate suggestion query authorization;
- Privacy inventory discovery;
- no CandidateSearchProjection write;
- no JobApplication status/stage write.

### Documentation Updates

- settle U-AI-08;
- document exact candidate source DTO and provider data classification;
- update Candidate/Privacy integration docs and progress tracker.

### Acceptance Criteria

Candidate classification works only through approved source data, raw/private data cannot leak by default, and no API/result can be mistaken for an employment decision.

### Exit Gate

Candidate privacy/security/integration tests pass; privacy/security reviewer signoff is recorded for the enabled data shape; typecheck/lint/build pass.

---

# Phase 5 — Backfill and Administrative Operations

## 11 Bounded Classification Backfill and Admin Review Operations

### Objective

Implement restricted, durable, bounded backfill execution across registered source types and complete the practical admin review controls without introducing a generic AI workflow engine or third business model by default.

### Observable Result

An authorized administrator can start a bounded backfill for a supported registered target scope, observe per-run outcomes/failures, cancel eligible runs, and review suggestions. Queue failures and partial completion are visible.

### Cluster Build-Plan Link

Completes the root **Phase 4.3** “worker/backfill process” requirement; can expand as root Phases 5/8 register additional source types.

### Dependencies

- Features 05–10 as applicable to target types;
- at least one owner-provided target enumerator/cursor contract;
- SH-014 decision if step-up is required;
- SH-029 audit;
- SH-047/048 queue/retry;
- PR-AI-10 remains approved: no `AiBackfill` model unless durable product semantics demand it.

### In Scope

- executable `enqueueClassificationBackfill`;
- target-type allowlist;
- bounded owner enumeration interface;
- dry-run/estimate if owner interface supports it without expensive provider calls;
- batch-size/concurrency/rate policy;
- enqueue per-target semantic runs;
- per-target dedupe against current source/config version;
- partial failure reporting through AI runs + queue/Ops records;
- run cancellation where safe;
- protected admin backfill/request/review UI if root admin shell exists;
- audit backfill initiation/cancellation.

### Out of Scope

- arbitrary SQL/table scans;
- “classify everything” unbounded endpoint;
- local QueueJob implementation;
- cron reclassification schedule;
- first-class `AiBackfill` record unless architecture is revised;
- low-confidence automatic Taxonomy acceptance;
- local ComplianceHold workflow.

### Module-Owned Data

Per-target `AiClassificationLog`/`AiSuggestion`. No separate backfill business truth under current ruling.

### Public Interfaces

- `enqueueClassificationBackfill` restricted;
- `cancelClassificationRun` restricted;
- existing review queries.

### Shared Operations Used

- SH-001/002;
- SH-014 conditionally per central step-up policy;
- **SH-029 `appendAuditEvent`**;
- SH-044;
- SH-047/048;
- SH-051;
- SH-038 queue telemetry;
- SH-036 metrics;
- SH-037 integration failure.

### Domain Logic

- backfill scope must be defined by source owner contract, not an AI-built cross-domain query;
- every target still goes through normal source/privacy/taxonomy/provider validation;
- backfill cannot bypass a disabled sensitive target type;
- concurrency is bounded per provider/model/target type;
- already-current semantic runs can be skipped/replayed safely;
- partial completion is expected and visible.

### Authorization / Compliance

Backfill is admin/system only. If central security classifies it as sensitive, SH-014 is mandatory. Candidate/healthcare restrictions apply identically to interactive requests.

### Database / Transaction Behavior

- no giant transaction spanning a backfill;
- per-target run transactions only;
- queue batch/cursor checkpoint is infrastructure/owner contract state, not accepted classification truth;
- target dedupe via idempotency + aggregate keys.

### Events / Jobs

- `processClassificationBackfillBatch`;
- `processClassificationRun` per target;
- dead-letter visible;
- no automatic recurring schedule.

### Provider Integration

Uses existing adapter with rate/concurrency controls. Provider outage pauses/retries safely; it does not mark remaining targets successful.

### UI / Admin Surface

Protected UI may show:

- target type/purpose/scope;
- queued/running/completed/failed counts derived from run/queue records;
- per-run safe error;
- cancel/retry actions where policy permits.

If durable cross-session backfill progress cannot be represented accurately without an `AiBackfill` model, stop and resolve U-AI-14 rather than inventing an unreliable UI projection.

### Failure Behavior

- unsupported/unregistered source → command denied;
- queue/provider outage → retry/visible degradation;
- one target failure → does not fail already-completed targets;
- dead-letter → operator-visible terminal failure;
- rate budget exhausted → pause/unavailable according to approved policy, never busy loop.

### Tests

- admin authorization;
- scope validation;
- bounded batch size;
- duplicate target skip;
- partial failure;
- provider throttle;
- dead-letter;
- candidate/healthcare disabled target cannot be backfilled;
- backfill cannot direct-query source tables;
- audit events for start/cancel.

### Documentation Updates

- document target enumerator contracts;
- resolve U-AI-14 if durable backfill model becomes necessary;
- record rate/concurrency limits once approved;
- UI registry/progress tracker.

### Acceptance Criteria

- backfill is bounded, authorized, idempotent, and observable;
- every target uses the same safe classification pipeline;
- no generic AI workflow/queue source truth is introduced;
- partial failures are recoverable and explicit.

### Exit Gate

Backfill integration/queue/authorization tests pass; controlled staging run demonstrates bounded retries and partial-failure visibility; typecheck/lint/build pass.

---

# Phase 6 — Privacy, Audit, and Operational Completion

## 12 Privacy Executor, Retention, Audit, Sensitive Access, and Ops Integration

### Objective

Complete the Module-side privacy handlers and prove that AI domain provenance, generic audit, sensitive access, and operational failures remain distinct and safely correlated.

### Observable Result

Privacy can enumerate AI-held subject data and issue an idempotent owner instruction; material admin/sensitive actions create the correct external evidence; provider/worker failures appear in Ops without leaking protected data.

### Cluster Build-Plan Link

AI-side privacy design begins in Phase 4 but formal orchestration aligns with root **Phase 10 — Privacy, Location Safety, Moderation, and Legal Workflows**. Audit/Ops integration reinforces the root Phase 3 support rail already required before Phase 4.

### Dependencies

- Features 01–11 as applicable;
- Privacy public protocol available;
- U-AI-03 retention rules resolved enough for destructive/anonymizing actions;
- Audit/Ops shared operations implemented;
- provider deletion decision if any durable provider resource is introduced.

### In Scope

- SH-096 enumerator for AI runs/suggestions by subject/target reference;
- SH-095 execute handler for approved erase/anonymize/restrict/export/detach outcomes;
- SH-097 AI retention-fact evaluation;
- SH-098 field anonymization mapping where appropriate;
- export serializer for AI-owned safe data if Privacy contract requires;
- generic AuditEvent calls for material admin actions;
- AccessAuditLog calls for required sensitive reads/transmissions;
- IntegrationFailure/SystemEvent/Queue telemetry integration completeness;
- telemetry redaction tests;
- health checks/metrics.

### Out of Scope

- creating PrivacyRequest/DataErasureJob/DataRetentionExemption records;
- deleting accepted Taxonomy truth because an AI proposal is erased;
- legal retention policy invention;
- direct provider deletion by Privacy;
- using IntegrationFailure as AI run status;
- using `AiClassificationLog` as generic audit log.

### Module-Owned Data

May erase/anonymize/restrict/export `AiClassificationLog` and `AiSuggestion` according to approved Privacy instruction and retention policy while preserving relational invariants.

### Public Interfaces

Privacy owner handlers:

```text
enumerateSubjectData
executePrivacyInstruction
evaluateRetentionRequirement
```

Existing AI queries honor restricted/erased/anonymized state semantics if the schema/policy requires them.

### Shared Operations Used

- **SH-095 `executePrivacyInstruction`**;
- **SH-096 `enumerateSubjectData`**;
- **SH-097 `evaluateRetentionRequirement`**;
- **SH-098 `anonymizePersonalFields`**;
- **SH-029 `appendAuditEvent`**;
- **SH-030 `recordSensitiveAccess`**;
- SH-032..039 Observability/Ops operations;
- SH-044 idempotency for owner execution.

### Domain Logic

- identify all AI records that actually belong to/describe a subject through explicit mappings, not a global text scan;
- accepted Taxonomy records are returned as external-owner references if relevant, not mutated here;
- personal identifiers can be anonymized while retaining non-personal configuration/run statistics only when policy permits;
- erased/retained outcomes are explicit;
- repeated Privacy instruction returns same result;
- operational telemetry stores safe counts/references only.

### Authorization / Compliance

Privacy orchestration supplies trusted target instruction. AI does not authorize the underlying legal request. Sensitive read/access audit remains separate.

### Database / Transaction Behavior

- execute one owner instruction transactionally at the appropriate target granularity;
- preserve foreign-key/relationship integrity;
- no cascade into Taxonomy/source owner tables;
- retention-exempt result references Privacy-owned exemption, not local flag;
- idempotent repeat yields same disposition.

### Events / Jobs

Privacy orchestration may call handlers asynchronously through its own queue. AI does not create a second Privacy queue. Ops records retryable/terminal failures.

### Provider Integration

If no durable provider resource exists, return provider deletion “not applicable/absent” per approved Privacy contract. If future provider resources exist, delegate deletion through provider owner contract.

### UI / Admin Surface

No new Privacy UI. AI admin UI must reflect redaction/restriction without exposing erased data.

### Failure Behavior

- unresolved retention → `retained/review_required` according to approved Privacy contract, not guessed deletion;
- transient DB/provider dependency → retryable failure;
- relational invariant conflict → terminal/review, no partial erase;
- audit/ops payload sanitizer failure must fail closed for sensitive metadata.

### Tests

- subject-data enumeration;
- no raw content in export beyond approved data;
- erase/anonymize idempotency;
- accepted Taxonomy unaffected;
- retention exemption reference handling;
- sensitive access proof;
- AuditEvent vs run log separation;
- IntegrationFailure vs run state separation;
- telemetry redaction;
- health/metric safe dimensions.

### Documentation Updates

- resolve U-AI-03;
- update Privacy target registry/inventory;
- update retention map and progress tracker;
- document any provider deletion capability.

### Acceptance Criteria

- Privacy can fulfill AI-owned targets without direct table ownership;
- AI data does not escape retention/erasure rules;
- accepted Taxonomy truth is not accidentally deleted;
- audit/access/ops/domain provenance remain distinct;
- logs/metrics are safe.

### Exit Gate

Privacy contract/integration tests, audit/access tests, telemetry redaction tests, typecheck/lint/build all pass. Formal Privacy orchestrator integration is verified when root Phase 10 exists.

---

# Phase 7 — Module Hardening and Production Verification

## 13 Concurrency, Replay, Staleness, Provider Outage, Security, and End-to-End Hardening

### Objective

Prove the complete Module remains correct under concurrency, retries, stale source/taxonomy versions, provider outages, privacy restrictions, and cross-Module timing failures before production activation.

### Observable Result

The core AI classification journey remains deterministic and non-authoritative under stress/failure: no duplicate proposals, no unauthorized provider calls, no stale result silently becoming current, no raw suggestion entering Search, and no provider outage corrupting domain truth.

### Cluster Build-Plan Link

Supports root **Phase 12 — Production Hardening and Launch Readiness**, while verifying CL-02 Phase 4 contracts.

### Dependencies

- all implemented Features 01–12 relevant to enabled target types;
- real/staging provider configuration;
- Taxonomy and Search integration test environments;
- source Module integrations for the targets being launched;
- security/privacy decisions required by those target types.

### In Scope

- race tests;
- replay/idempotency tests;
- stale source/taxonomy/prompt version behavior;
- provider outage/throttle/timeout chaos-style tests;
- retry exhaustion/dead-letter/manual rerun;
- cancellation race;
- Privacy restriction during queued/running work;
- Taxonomy decision vs supersession race;
- telemetry safety review;
- provider credential/security review;
- load/performance tests for review lists/backfill;
- controlled E2E journey through Taxonomy acceptance and Search refresh;
- migration/backfill verification for existing records if schema changed after earlier environments.

### Out of Scope

- advanced autonomous AI taxonomy;
- AI-controlled public visibility/ranking;
- AI-created taxonomy terms;
- new provider fallback not architected;
- unrelated search ranking algorithms;
- expansion into generic platform AI agent capabilities.

### Module-Owned Data

All AI-owned records may be exercised; no new business model should be introduced solely for hardening convenience.

### Public Interfaces

Freeze/verify compatibility of all enabled commands/queries/privacy handlers. Breaking changes require context and dependent Module updates.

### Shared Operations Used

All previously integrated operations, especially:

- SH-044 idempotency;
- SH-045 event dedupe;
- SH-047/048 queue/retry;
- SH-051/052/053 concurrency/state;
- SH-061/065/066 provider boundary;
- SH-072/077/078 provenance/minimization;
- SH-029/030 audit/access;
- SH-032..039 Ops;
- SH-095..098 Privacy;
- SH-091 Search boundary verification.

### Domain Logic

Verify these invariants under real timing:

- latest source/config policy wins only according to approved staleness rules;
- old provider result cannot overwrite current proposal state incorrectly;
- duplicate provider calls have at most one persisted proposal effect per run/candidate key;
- accepted Taxonomy truth survives AI-side retry/Privacy disposition appropriately;
- Search refresh never originates from mere generation;
- candidate output never becomes employment decision/ranking;
- disabled sensitive target type fails before provider call.

### Authorization / Compliance

Run complete access matrix and sensitive-data tests for all enabled targets. Confirm central step-up behavior if U-AI-01 was resolved to require it.

### Database / Transaction Behavior

- contention tests on target-purpose lock;
- expected-version stale updates;
- transaction rollback on partial suggestion insert;
- index/query performance under realistic run/suggestion counts;
- migration verification from previous deployed schema.

### Events / Jobs

- event inbox/outbox replay if enabled;
- queue lease expiration/reclaim;
- dead-letter/manual rerun;
- no exactly-once transport assumptions;
- backfill checkpoint behavior under crash/restart.

### Provider Integration

- staged outage;
- throttling;
- latency/timeout;
- malformed structured output;
- unsupported model/config;
- credential rotation behavior according to platform secret system;
- verify logs contain no source/private payload.

### UI / Admin Surface

If admin/source UI exists:

- stale states refresh correctly;
- no double-submit creates duplicate effects;
- errors use stable safe messages;
- review UI never implies accepted classification before Taxonomy decision;
- accessibility and pagination remain usable at realistic volume.

### Failure Behavior

Production failures must end in one of:

- safe replay/current result;
- retryable queued state;
- explicit failed/cancelled run;
- restricted/unavailable decision;
- dead-letter/operator-visible failure;
- conflict/manual review.

No failure may silently mark a proposal accepted, index content, or expose raw private data.

### Tests

- parallel request load test;
- cancellation/running race;
- Taxonomy disposition/supersession race;
- privacy restriction mid-run;
- source update mid-run;
- taxonomy change mid-run;
- provider outage/throttle/malformed output;
- queue crash/restart/lease reclaim;
- dead-letter + manual rerun;
- audit/access/ops completeness;
- telemetry redaction fuzz tests;
- query/backfill performance tests;
- E2E:

```text
source owner target
→ AI request
→ queued/running/completed run
→ proposed suggestion
→ Taxonomy acceptance/rejection
→ AI disposition update
→ accepted classification only: Search refresh
```

### Documentation Updates

- close/restate all resolved U-AI decisions;
- record launch-enabled target types/purposes/models;
- update library/provider docs;
- update progress tracker with final verification commands/results;
- update root/cluster architecture only for legitimate binding changes.

### Acceptance Criteria

- all Module invariants hold under concurrency/replay/outage tests;
- no direct cross-Module source mutation exists;
- provider/private data boundaries pass security review;
- enabled target types have explicit source/privacy contracts;
- failure modes are operationally visible;
- Search and Taxonomy boundaries are proven end-to-end.

### Exit Gate

Before declaring AI Taxonomy production-ready for a target type:

```text
schema/migration validation passes
typecheck passes
lint/format passes
all AI unit tests pass
all AI DB/integration tests pass
authorization/RLS tests pass where applicable
provider adapter tests pass
worker/idempotency/concurrency tests pass
privacy/audit/access/ops tests pass
cross-Module Taxonomy/Search contract tests pass
enabled-source integration tests pass
critical E2E passes
security/privacy review for enabled data lane is recorded
progress tracker is current
no launch-blocking unresolved decision remains for that target/purpose
```

---

# Phase Summary

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Source-of-Truth and Contract Foundation | 01–02 |
| 2 | Taxonomy-Constrained Validation and Provider Boundary | 03–04 |
| 3 | Durable Classification Execution and Read Surface | 05–06 |
| 4 | Module Integration Phase | 07–10 |
| 5 | Backfill and Administrative Operations | 11 |
| 6 | Privacy, Audit, and Operational Completion | 12 |
| 7 | Module Hardening and Production Verification | 13 |

**Total numbered features: 13**

### Root build sequence alignment

```text
Phase 4.3 core:
  01 → 02 → 03 → 04 → 05 → 06 → 07

Phase 5 source integration:
  08

Phase 8 hiring source integration:
  09 → 10

Phase 4.3 backfill maturity after target sources exist:
  11

Phase 10 formal privacy orchestration:
  12

Phase 12 launch hardening:
  13
```

A coding agent must not pull Features 08–10 forward by directly reading source tables merely because the AI core is ready sooner.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root `project-overview.md` and `architecture.md`.
2. Read root `code-standards.md`.
3. Read the current Canonical Shared Operations Registry.
4. Read CL-02 architecture if present; otherwise the current CL-02 Cluster Registry section and root Phase 4 build plan.
5. Read this Module architecture and implementation plan.
6. Read public-interface sections for every dependency used by the feature.
7. Read current `schema.prisma` and relevant migrations.
8. Confirm the previous feature exit gate and root-phase dependency.
9. Check whether any Proposed Ruling or Unresolved Decision blocks the feature.
10. Write a concise implementation specification for **this feature only**.
11. Implement only the feature's in-scope work.
12. Run the required quality checks.
13. Verify public contracts and one-owner boundaries.
14. Update `progress-tracker.md`.
15. Update architecture only when a binding decision legitimately changed.
16. Record remaining risks/deferred work.

Do not generate all implementation specifications in advance. The specification must reflect the repository state at the moment the feature starts.

---

# Required Feature Implementation Specification

Immediately before coding any numbered feature, the coding agent must produce:

```text
Feature:
Objective:
Observable result:
Cluster/root build-plan link:
Dependencies:
Prior exit gate confirmed:
Proposed rulings/unresolved decisions checked:
In scope:
Out of scope:
Owned data affected:
Public contracts introduced/changed:
Shared operations consumed:
Permissions/compliance:
Primary workflow:
Provider integration:
Jobs/events:
Idempotency/concurrency:
Error behavior:
Tests:
Acceptance criteria:
Documentation updates:
```

Additional AI Taxonomy questions the specification must answer:

```text
Which source Module supplies the target snapshot?
Why are these exact fields permitted for this purpose?
What is the source-version token?
Which taxonomy snapshot/prompt/schema/model version is used?
Can any personal/private/healthcare/candidate data leave Workin Ants?
What prevents provider output from becoming accepted truth?
What prevents Search from indexing the proposal directly?
What is the semantic idempotency key?
What happens if source/taxonomy changes while the model is running?
```

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

```text
Feature completed:
Files added:
Files changed:
Database changes:
Migrations:
Dependencies/packages added:
Module public interfaces added/changed:
Shared operations reused:
Events/jobs added:
Provider adapter changes:
Tests added/changed:
Commands run:
Manual/contract verification:
Cross-Module direct-access audit:
Sensitive-data/telemetry audit:
Documentation updated:
Assumptions:
Known failures:
Remaining risks:
Deferred work:
Unresolved decisions encountered:
Exit-gate result: PASS / FAIL
```

For any provider-related feature, also report:

```text
Provider model/config used for verification:
Credential handling verified:
Raw provider/source payload logging check:
Retry/error mapping verified:
Sensitive data lanes enabled/disabled:
```

For any integration feature, also report:

```text
Owning dependency interface called:
Direct Prisma access to dependency tables: NONE / issue found
Source-of-truth owner verified:
Contract test evidence:
```

---

# Final Quality Check

Before this Module can be treated as implementation-complete for an enabled target/purpose, verify:

1. `AiClassificationLog` and `AiSuggestion` are the only AI-owned business truth introduced unless later architecture explicitly adds more.
2. Taxonomy & Classification remains the only owner of accepted controlled vocabulary/classification semantics.
3. No AI path directly writes Taxonomy joins.
4. No AI path directly writes `SearchUpsertEvent` or Typesense.
5. Raw provider output cannot bypass structured + semantic validation.
6. Source data comes from owner public interfaces.
7. Candidate/private/healthcare provider input is explicitly allowed or blocked; it is never assumed.
8. No candidate output can act as an automated employment decision.
9. Prompt/source/taxonomy/model/output-schema provenance is reproducible.
10. Provider SDK/types remain inside the adapter.
11. Command effects are idempotent and lifecycle transitions are concurrency-safe.
12. Queue work is durable/retryable/observable and dead-letter behavior is tested.
13. Domain run/suggestion truth is distinct from AuditEvent, AccessAuditLog, IntegrationFailure, and QueueJob.
14. Privacy orchestration remains Privacy-owned; AI executes only its target instructions.
15. Erasing an AI proposal does not silently erase accepted Taxonomy truth.
16. Search remains a projection of accepted source truth.
17. Every numbered feature has passed its exit gate before dependent work proceeds.
18. Root/Cluster sequencing has not been silently reordered.
19. No Proposed Ruling was converted into code without an architecture update/approval.
20. A new coding agent can determine ownership, workflow, error behavior, and dependencies without inventing architecture.
