# Discovery, Classification & Visibility Build Plan

> **Cluster ID:** `CL-02`  
> **Cluster:** Discovery, Classification & Visibility  
> **Repository target:** `context/clusters/discovery classification & taxonomy/discovery-classification-build-plan.md`\
> **Companion architecture:** this Cluster `architecture.md`  
> **Modules:** `taxonomy_classification`, `ai_taxonomy`, `search_public_visibility`  
> **Implementation posture:** greenfield MVP planning against the current Workin Ants architecture and Prisma evidence. Approved contextual join ownership and Search durable-work semantics apply; unresolved AI source schemas/lifecycles, Search physical persistence, candidate-search policy, AI privacy retention, and provider-contract decisions must remain gated rather than being guessed in code.

Current coordination: [Cluster architecture](<discovery-classification-architecture.md>) and [Cluster build plan](<discovery-classification-build-plan.md>). Locate supporting artifacts through [context-map.md](<../../context-map.md>); authority follows concern, not location or age. Root architecture/build-plan files are currently unavailable and do not supply enforceable phases.

---

## Core Principle

Build CL-02 as a sequence of **vertical, testable discovery slices** that preserve the separation between accepted vocabulary, AI proposal truth, and search projection.

```text
usable / observable behavior
→ owning Module domain/application service
→ authoritative database state
→ stable public contract
→ authorization / readiness / privacy gates
→ events / jobs / provider adapters
→ deterministic tests and workflow verification
→ explicit exit gate
```

The implementation sequence deliberately does **not** map one phase to one Module.

The first slice proves that accepted Taxonomy truth can become a Search projection without AI or foreign business entities. AI is then introduced as proposal truth only. Accepted entity classification and broad cross-Cluster discovery are added only after their ownership contracts are resolved.

The governing separation is:

```text
Taxonomy accepts classification truth.
AI records what the model proposed.
Search projects what owners currently allow to be discovered.
```

A capability does not need artificial UI. If a user-facing surface is not appropriate yet, the feature must still produce a concrete API, admin/debug surface, durable owner record, worker result, provider adapter, or contract test that proves the behavior.

---

## Build Rules

1. Follow `context/project-overview-v3.md` (orientation; see context map), root `architecture.md`, root `code-standards.md`, the Canonical Shared Operations Registry, and this Cluster architecture.
2. Do not expand CL-02 into business-object lifecycle ownership, hiring decisions, compliance approval, verification, healthcare, location policy, moderation, privacy orchestration, entitlement policy, or a general AI platform.
3. Do not redesign Deep Module ownership for implementation convenience.
4. Reuse canonical SH operations. If one is missing, implement/fix it in the canonical owner or use its approved contract fake; do not create a CL-02-local substitute.
5. Use canonical operation names where the Shared Operations Registry provides them. Module-extract aliases are not competing APIs.
6. Every protected mutation validates input, resolves an authenticated/system actor, authorizes the action server-side, and enforces owner invariants.
7. Every cross-Module read uses a public interface, owner-facts DTO, or approved projection contract. Direct cross-domain Prisma repositories are not the default.
8. Every lifecycle transition is performed by the owning Module.
9. Taxonomy & Classification is the only owner of canonical Domain/Category/Tag vocabulary and normalization policy.
10. AI Taxonomy must never write accepted taxonomy joins or Search provider state directly.
11. AI output must pass structured validation before it becomes a usable `AiSuggestion`.
12. AI may classify or suggest skills only from owner-approved/minimized inputs; it does not parse private resumes by ownership shortcut and does not make automated employment decisions.
13. Search / Public Visibility is the only CL-02 Module that may write Typesense/provider projection state.
14. Search must be rebuildable from accepted source truth without invoking AI.
15. Search cannot infer business eligibility from ranking, badges, provider state, or local booleans.
16. `CandidateSearchProjection` remains Candidate Application & Resume Privacy truth.
17. Protected candidate Search remains disabled until its organization-authority/privacy/entitlement contract is approved.
18. Track Subscription & Entitlement remains the owner of boost/feature entitlement truth; no local premium or boost flags.
19. Public location must come from Location Safety-approved fuzzy projection.
20. Moderation and Privacy decide; Search executes projection removal/restoration against its own provider state.
21. `ComplianceHold` is the reusable stop sign. Do not create `searchBlocked`, `classificationBlocked`, or `aiBlocked` generic state.
22. Provider payloads never become Workin Ants domain types.
23. Bedrock/model calls remain behind the approved AI Taxonomy provider port. Typesense calls remain behind Search’s provider adapter.
24. Every asynchronous operation is durable, idempotent, retry-classified, correlated, observable, and dead-letter visible.
25. Generic queue attempt/lease/dead-letter metadata stays in shared queue/Ops infrastructure rather than being recreated in `SearchUpsertEvent` or AI records.
26. Audit evidence and operational telemetry are required where applicable, but neither replaces Taxonomy, AI, or Search domain truth.
27. Privacy owns PrivacyRequest/DataErasureJob/DataRetentionExemption orchestration; CL-02 owners implement only their target executors and subject-data enumeration.
28. Hard-delete/merge of taxonomy terms is not implemented until its architecture decision is approved.
29. Taxonomy-join repositories are not implemented until join ownership and join metadata semantics are approved.
30. No production AI source schema is invented from the registry claim alone; resolve `U-CL02-04` before migration.
31. No public `SearchEntityType.user` indexing is enabled without explicit approval.
32. Every numbered feature ends with tests, workflow verification, documentation/progress update, and a concrete exit gate.
33. Do not start the next numbered feature until the prior feature exit gate passes, except for separately tracked canonical-owner prerequisites explicitly identified as parallel.
34. Unresolved architecture is not silently settled in code. Stop, resolve the decision, update architecture, then continue.
35. High-risk unresolved behavior fails closed or remains disabled/stubbed instead of defaulting permissively.

---

## Dependencies and Preconditions

### Root/platform prerequisites

CL-02 assumes these shared mechanisms are available or can be represented by approved contract fakes until their canonical owners are implemented:

- SH-001 authenticated actor context;
- SH-002 authorization;
- SH-003 owner-facts contract where approved;
- SH-011 ComplianceHold evaluation;
- SH-029/030 audit and sensitive-access logging;
- SH-032–040 request context, structured logging, redaction, exception capture, metrics, integration failure, queue telemetry, service health, and incident correlation;
- SH-044 idempotent command execution;
- SH-045 consumer event deduplication;
- SH-046 transactional outbox/domain-event publication;
- SH-047/048 durable jobs and retry/dead-letter execution;
- SH-051/052 concurrency controls;
- SH-053 lifecycle transition plumbing where approved;
- SH-072 hashing and SH-077 canonical text snapshots;
- SH-078 provider-input minimization/redaction;
- SH-095–098 Privacy target execution/enumeration/retention/anonymization protocol.

If any primitive is absent, CL-02 must not create an untracked duplicate. Use the canonical interface and a test implementation while the canonical owner is completed.

### Existing CL-02 schema evidence

The current Prisma schema already contains:

- `TaxonomyDomain`;
- `TaxonomyCategory`;
- `TaxonomyTag`;
- `TagSource`;
- taxonomy category/tag joins;
- `SearchUpsertEvent`;
- `SearchEntityType`;
- external-source models such as Offering, Gig, Job, Organization, ProfessionalProfile, CandidateProfile;
- `CandidateSearchProjection`.

The current Prisma schema **does not** contain:

- `AiSuggestion`;
- `AiClassificationLog`;
- AI-specific statuses/enums.

Do not create placeholder AI tables merely to begin provider integration.

### Upstream / neighboring public contracts

Early CL-02 work can use fixtures/test doubles for neighboring Modules. Full neighboring UI is not required.

Contracts eventually required:

- Marketplace Supply — Offering source projection/public readiness;
- Gig / Demand — Gig source projection/public readiness;
- Organization Hiring — Organization/Job source projection and organization authority facts;
- Candidate Application & Resume Privacy — `CandidateSearchProjection`, privacy/readiness, candidate source snapshot;
- Professional Eligibility — Professional public readiness and source projection;
- Job Compliance — Job public-compliance decision;
- Trust Verification / Screening — verification/public TrustBadge signals;
- Healthcare — healthcare/public and AI-input data-boundary decisions;
- Location Safety — fuzzy public location;
- Content Moderation — moderation target execution;
- Admin Review / Compliance Hold — active hold decision;
- Privacy / Data Erasure — target-executor protocol;
- Track Subscription & Entitlement — candidate-search/boost entitlement;
- Audit / Event Ledger and Observability / Ops.

### Providers that may be stubbed initially

- **AWS Bedrock:** may be a deterministic fake until Feature 05.
- **Typesense:** may be an in-memory/provider fake until Feature 03, but the production provider contract must remain Search-owned.
- Search and AI features must be testable without live provider credentials.

### Dependencies that should not block initial vertical slices

The following do **not** block Feature 01:

- AI schemas;
- live Bedrock;
- Typesense;
- taxonomy-join ownership;
- cross-Cluster source projection contracts;
- protected candidate search;
- final ranking weights;
- taxonomy hard delete/merge.

### Architecture gates that must be resolved before the named feature

| Gate | Must be resolved before | Reason |
|---|---|---|
| `U-CL02-08` physical Search work representation | Production persistence/worker; Feature 02 remains a fake-writer contract harness | CL02-R008 approves durable semantics, not fields/enums or the choice to expand/replace SearchUpsertEvent |
| `U-CL02-09` initial Typesense collection/document strategy | Feature 03 | provider schema cannot be silently invented |
| `U-CL02-04` AI Prisma records/statuses | Feature 04 | AI source truth must exist before provider output is persisted |
| `U-CL02-12` SH-065 implementation placement | Feature 05 production adapter | provider port owner is currently Proposed |
| `U-CL02-02` applicable join metadata semantics | Feature 07 | Ownership is resolved by CL02-R001; metadata meaning remains unresolved |
| CL02-R003 SH-121 handoff; U-CL02-04 exact AI lifecycle and U-CL02-13 events if used | Feature 08 | Owner mutation must succeed before AI acceptance disposition; retries must not duplicate assignments |
| `U-CL02-10` candidate authority/privacy/entitlement contract | Feature 10 | protected candidate search cannot guess access |
| `U-CL02-11` AI retention/privacy policy | Feature 13 production readiness | sensitive AI records require explicit retention behavior |
| `U-CL02-16` User search policy | any User indexing | default remains disabled |

`U-CL02-06`, `U-CL02-07`, `U-CL02-14`, and `U-CL02-15` gate only the specific tag-trigger, destructive taxonomy, Gig-AI, or novel-term behaviors they govern.

---

# Phase 1 — Accepted Vocabulary to Rebuildable Search

The first phase proves CL-02’s fundamental architecture without depending on AI or foreign business lifecycles:

```text
Taxonomy truth
→ Search refresh request
→ owner-safe taxonomy projection
→ Typesense
→ public discovery result
```

## 01 Canonical Taxonomy Catalog and Validation

Build the canonical Domain → Category → Tag catalog, administration workflow, public read contract, normalization, classification validation, and requirement-trigger query using the current Taxonomy-owned records.

### Objective

Make Taxonomy & Classification the only authoritative vocabulary service and provide stable contracts that later AI, Search, and business Modules can consume.

### User-visible / Observable Result

- authorized admin can create/update/activate/deactivate a Domain, Category, or Tag within currently approved lifecycle limits;
- public/internal caller can list the canonical active taxonomy tree;
- caller can validate a proposed Domain/Category/Tag combination;
- caller can resolve the requirement triggers implied by accepted taxonomy;
- invalid hierarchy, inactive term, duplicate slug/name, and unauthorized admin actions are deterministically rejected;
- no Bedrock or Typesense call is needed to prove this feature.

### Owning Module(s)

- **Taxonomy & Classification** — all source truth/mutations in this feature.

### Dependencies

- current Prisma taxonomy models;
- root validation conventions;
- SH-001, SH-002, SH-023, SH-022, SH-029, SH-044, SH-051/052 as needed, SH-079;
- current taxonomy seed definitions if approved.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity & Access.** Admin commands resolve a trusted actor. Local policy: taxonomy read surfaces may be public; mutations are protected. Do not build taxonomy session helpers.
- **SH-002 `authorizeResourceAction` — Role / Authority.** Authorize taxonomy administration. Local policy: action names such as taxonomy.domain.create or taxonomy.tag.deactivate. Do not build a taxonomy role engine.
- **SH-023 `validateTaxonomyAssignment` — Taxonomy.** Implement the canonical hierarchy/active/compatibility decision. Local policy: Taxonomy owns hierarchy and compatibility semantics. Do not build validators in consumers.
- **SH-022 `resolveTaxonomyRequirements` — Taxonomy.** Implement accepted classification → requirement refs. Local policy: trigger mapping only, not satisfaction. Do not build healthcare/verification approval here.
- **SH-079 `normalizeControlledTerm` — Taxonomy policy over shared text primitive.** Normalize terms consistently. Local policy: collision/canonical naming. Do not create independent normalizers.
- **SH-029 `appendAuditEvent` — Audit.** Record material admin changes. Local policy: safe taxonomy action metadata. Do not create a taxonomy audit table.
- **SH-044 `executeIdempotentCommand` — platform.** Protect retryable admin/seed commands. Local policy: semantic command identity. Do not create local idempotency storage.
- **SH-051/052 — shared persistence.** Protect conflicting admin edits when required. Local policy: which term/version conflicts. Do not use in-memory locks.

### Data / Schema

Use:

- `TaxonomyDomain`;
- `TaxonomyCategory`;
- `TaxonomyTag`;
- `TagSource`;
- current uniqueness indexes/relations;
- current category trigger fields.

Do **not** change:

- taxonomy join ownership;
- `verified`/confidence semantics;
- tag-level healthcare/location behavior;
- `DataSensitivity` ownership;
- hard-delete/merge/history semantics.

Admin destructive delete endpoints are out of scope.

### Public Interfaces

Complete/introduce:

- `listTaxonomyTree`;
- `getTaxonomyTerm`;
- SH-023 `validateTaxonomyAssignment`;
- SH-022 `resolveTaxonomyRequirements`;
- create/update/set-active commands for Domain/Category/Tag;
- idempotent `seedTaxonomyCatalog` internal operation.

Names follow repository conventions but semantics must match architecture.

### Logic

- enforce Domain → Category → Tag parentage;
- enforce current uniqueness constraints;
- enforce current active-state rules that are explicitly approved;
- reject creation of uncontrolled terms through consumer Modules;
- return canonical IDs and normalized error/reason codes;
- return trigger references without declaring the trigger satisfied;
- ensure `TagSource.ai` remains provenance vocabulary only.

### UI / Administrative Surface

Minimum taxonomy admin surface:

- tree/list;
- active/inactive state;
- create/edit term;
- approved category policy fields;
- validation error display;
- no hard-delete control.

A simple public taxonomy browser or API explorer is sufficient for observable public reads.

### Authorization / Compliance

- public active-tree read may be anonymous;
- inactive/admin metadata reads and all writes require authority;
- taxonomy trigger fields are not compliance approval;
- no private entity data is needed.

### Events / Jobs / Integrations

- no external provider;
- seed may be a reliable job if dataset size justifies it;
- taxonomy mutation may publish a versioned domain event once `U-CL02-13` is approved;
- Search refresh is introduced in Feature 02, so Feature 01 may record a deferred refresh integration point rather than invent a local queue.

### Failure Behavior

- duplicate/collision → conflict, no partial write;
- invalid parent → validation denial;
- unauthorized → denial;
- concurrent stale edit → explicit conflict;
- audit failure behavior follows root transactional/audit policy; do not silently write a second audit path.

### Tests

- unit: normalization, hierarchy, active checks, trigger mapping;
- integration: Prisma uniqueness/foreign keys;
- authorization contract;
- idempotent seed;
- concurrency/stale-edit test;
- contract: SH-022/023 return stable DTO/reasons;
- negative test proving no compliance completion is inferred.

### Out of Scope

- entity taxonomy join mutations;
- AI;
- Typesense;
- term merge/hard delete;
- tag-level healthcare/location additions;
- candidate provenance changes;
- cross-Cluster source projection.

### Exit Gate

- clean DB migration already contains current Taxonomy records;
- canonical seed runs idempotently;
- admin CRUD within approved non-destructive lifecycle passes authorization and transaction tests;
- SH-022 and SH-023 contract tests pass;
- duplicate/inactive/invalid-hierarchy cases are deterministic;
- no consumer-local taxonomy copy/normalizer exists;
- `U-CL02-07` behaviors remain disabled rather than guessed.

---

## 02 Search Projection Refresh Contract and Work Queue

Establish Search’s canonical refresh command and owner work record before any external search provider write.

### Objective

Make SH-091 the only supported way for source owners to request Search convergence and give Search an observable, idempotent work lifecycle using `SearchUpsertEvent` plus canonical queue infrastructure.

### User-visible / Observable Result

- Taxonomy can request a projection refresh for a taxonomy entity;
- duplicate/retried requests do not create unsafe duplicate provider effects;
- an admin/debug endpoint can show pending/processed Search refresh work;
- a worker can claim a refresh request using a fake provider without direct foreign-table coupling;
- deletion is represented by “refresh to current truth,” not a second local deindex queue, under the approved CL02-R008 semantic boundary, subject to separate persistence design.

### Owning Module(s)

- **Search / Public Visibility** — `SearchUpsertEvent`, Search work semantics.
- shared queue infrastructure — attempt/lease/dead-letter mechanics.

### Dependencies

- Feature 01;
- `SearchUpsertEvent`, `SearchEntityType`;
- approved CL02-R008 durable-work requirements; separate Search persistence design/migration approval before production persistence/worker use;
- SH-044, SH-047, SH-048, SH-032–038;
- Taxonomy SH-094 source-projection and owner-issued SH-024 readiness contracts; Search must not infer readiness from Taxonomy fields. Any parent/effective-activity-dependent behavior remains gated by U-CL02-07.

### Shared Operations Used

- **SH-091 `requestSearchProjectionRefresh` — Search.** Canonical source-owner command. Local policy: Search entity type mapping and reason vocabulary. Do not let callers create SearchUpsertEvent directly.
- **SH-094 `buildSourceProjection` — source owner.** Taxonomy exposes the first owner-safe projection DTO. Local policy: which taxonomy fields are public. Do not let Search import Taxonomy repositories as a general pattern.
- **SH-044 `executeIdempotentCommand` — platform.** Protect duplicate refresh commands. Local policy: semantic entity/reason/coalescing identity.
- **SH-047 `enqueueReliableJob` — shared queue.** Dispatch refresh processing. Local policy: Search payload and completion meaning.
- **SH-048 `executeRetryWithBackoff` — shared queue.** Retry transient worker/provider failures later. Local policy: Search/provider retry classification.
- **SH-032–038 — Ops.** Correlation, logging, metrics, queue telemetry, failure visibility. Do not create a Search queue ledger.
- **SH-045 `deduplicateDomainEvent` — platform.** Used if refresh requests arrive from domain events. Local policy: Search consumer handler identity.

### Data / Schema

Primary:

- `SearchUpsertEvent`;
- `SearchEntityType`.

Under approved CL02-R008, Search owns durable SH-091 request identity/context, source version/currentness, idempotency, requester, action, claimability, completion, retry/operator failure, and stale/superseded outcomes. Generic queue infrastructure owns transport, attempts, backoff, and dead-letter mechanics, not the sole Search currentness/outcome truth.

The current `processed` Boolean is insufficient for the final production lifecycle. Expanding or replacing SearchUpsertEvent is deliberately undecided. Feature 02 remains a fake-writer contract/queue harness; production persistence and workers wait for the separate Search database design and the Module provider gate.

### Public Interfaces

- SH-091 `requestSearchProjectionRefresh`;
- internal `processSearchProjectionRefresh`;
- `inspectSearchProjectionWork` restricted query;
- Taxonomy SH-094 projection implementation.

### Logic

1. validate the complete SH-091 request: `entityType`, `entityId`, `action`, `reason`, `sourceVersion`, `requesterModule`, and `idempotencyKey`;
2. idempotently create a Search-owned refresh event;
3. enqueue work;
4. worker resolves current source projection through owner interface;
5. worker evaluates expected provider presence;
6. until Feature 03, use a fake projection writer;
7. mark event processed only after successful convergence;
8. keep terminal failures visible through Ops/debug.

### UI / Administrative Surface

Minimal Search debug/admin surface:

- entity type;
- entity ID;
- reason;
- created/processed timestamps;
- pending state;
- correlated queue failure/dead-letter reference when available.

No user-facing search UI is required yet.

### Authorization / Compliance

- source Modules invoke through service-to-service actor/context;
- admin inspection requires Search admin/support authority;
- debug output must not expose private source payloads.

### Events / Jobs / Integrations

- reliable worker required;
- no live Typesense yet;
- event consumer dedupe where refresh originates from domain events.

### Failure Behavior

- duplicate request → one safe semantic effect;
- missing/invalid source → expected projection may be absent; do not mark source invalid;
- transient worker failure → retry, event remains unprocessed;
- dead-letter → event remains visible/unresolved; admin can reconcile later;
- authorization failure on admin debug → deny without exposing event details.

### Tests

- SH-091 command contract;
- idempotency;
- queue retry/dead-letter;
- duplicate event delivery;
- missing source;
- worker crash before/after fake write;
- debug redaction;
- proof no direct Typesense/client exists outside Search.

### Out of Scope

- live Typesense;
- business entity types other than taxonomy;
- final ranking;
- candidate search;
- moderation/privacy execution.

### Exit Gate

- CL02-R008 semantic contract is covered by harness tests; physical Search persistence remains a separately approved prerequisite for production;
- all refresh creation passes only through SH-091;
- queue attempt metadata is not duplicated into a local Search queue framework;
- a taxonomy refresh can be created, processed through a fake writer, and inspected;
- duplicate refresh/event delivery is harmless;
- dead-letter work remains observable and is not falsely marked processed.

---

## 03 Taxonomy Search Projection and Public Discovery

Use Taxonomy as CL-02’s first complete source to prove the Search provider boundary and public query path.

### Objective

Project approved active taxonomy terms into Typesense through Search-owned provider code and return them through a public discovery/search contract.

### User-visible / Observable Result

- an active taxonomy term appears in Search after a refresh;
- update changes the provider document;
- deactivation removes/excludes it according to approved public taxonomy policy;
- public search can query approved taxonomy fields/facets;
- Search debug can explain whether the term is indexed/excluded/failed;
- Taxonomy code contains no Typesense calls.

### Owning Module(s)

- Taxonomy owns source term truth;
- Search owns projection, Typesense adapter, query API.

### Dependencies

- Features 01–02;
- `U-CL02-09` initial Search collection/document topology resolved;
- Typesense adapter credentials/config for integration environment or containerized test provider;
- SH-024, SH-092, SH-093, SH-094, SH-115.

### Shared Operations Used

- **SH-024 `evaluatePublicReadiness` — source owner decision, Search composes.** For taxonomy, local policy is active/public term eligibility. Do not create a generic Search readiness policy for all entities.
- **SH-094 `buildSourceProjection` — Taxonomy.** Return safe term DTO + source version. Do not give Search direct repository ownership.
- **SH-115 `buildAggregateProjection` — Search.** Assemble provider document from approved inputs. Local policy: taxonomy Search schema.
- **SH-092 `writeSearchProjection` — Search.** Only Search writes/deletes Typesense. Do not create Taxonomy Typesense helpers.
- **SH-093 `reconcileSearchProjection` — Search.** Compare expected vs provider state. Local policy: taxonomy entity projection.
- **SH-037 `recordIntegrationFailure` / SH-036 metrics.** Provider failure/latency/indexing lag. No Search-specific failure table.
- **SH-044/047/048.** Idempotent queued processing/retry.

### Data / Schema

No new business source table.

Search provider schema must be versioned at the code/contract level and include only approved taxonomy fields.

`SearchUpsertEvent` remains projection work truth.

Do not introduce a durable “SearchTaxonomy” database copy unless an approved projection requirement later demands one; Typesense itself is the derived projection.

### Public Interfaces

- `searchPublicDiscovery` supporting taxonomy result type;
- Search internal document builder;
- SH-092 provider writer;
- `inspectSearchProjection`;
- scheduled/admin reconciliation entry.

### Logic

- fetch current owner-safe term projection;
- evaluate public eligibility;
- build provider document;
- upsert if eligible, delete if not;
- mark Search work processed only after provider convergence;
- query only approved collection/fields/facets/sorts;
- translate provider result to Workin Ants result DTO.

### UI / Administrative Surface

Minimum:

- public/search API response or simple search UI demonstrating taxonomy discovery;
- admin projection inspector;
- no business-entity result cards required yet.

### Authorization / Compliance

- public taxonomy search may be anonymous;
- provider admin/debug is protected;
- no sensitive fields exist in the public provider document.

### Events / Jobs / Integrations

- Typesense adapter;
- refresh worker;
- reconciliation worker;
- scheduled reconciliation may remain admin-triggered initially.

### Failure Behavior

- Typesense down → source taxonomy remains valid; Search returns controlled degraded behavior;
- projection write failure → retry and Ops failure;
- query provider unavailable → safe error/degraded response, not database fallback that bypasses provider policy unless root architecture explicitly permits it;
- stale provider document → reconciliation repairs.

### Tests

- provider contract tests;
- active term upsert;
- deactivated term delete;
- idempotent repeated refresh;
- query allowlist;
- reconciliation of missing/stale/extra doc;
- Search failure does not mutate Taxonomy;
- architecture test/static check proving Typesense client lives only in Search adapter.

### Out of Scope

- Offering/Gig/Job/Profile/Organization projection;
- candidate search;
- AI;
- ranking boosts;
- fuzzy location.

### Exit Gate

- `U-CL02-09` initial provider schema/topology is approved and documented;
- active Taxonomy → Search → Typesense → public query passes end to end;
- deactivation removes/excludes the document;
- provider failure is observable and source truth remains unchanged;
- reconciliation can repair a deliberate mismatch;
- no Typesense dependency exists in Taxonomy.

---

# Phase 2 — Traceable AI Suggestions Without Accepted-Truth Leakage

This phase builds AI proposal/run truth before allowing AI to affect accepted classification.

```text
approved source snapshot + active taxonomy
→ model
→ validated AI run/suggestions
→ reviewable proposal
```

No accepted taxonomy write is allowed in Phase 2.

## 04 AI Classification Source Records and Lifecycle Foundation

Resolve and implement the missing AI Taxonomy source-of-truth records and stable request/query contracts before invoking a live model.

### Objective

Give AI Taxonomy durable, explicit ownership of classification-run and suggestion proposal truth so no one hides AI state inside taxonomy joins, Search records, audit logs, or provider payloads.

### User-visible / Observable Result

- an authorized caller can create a deterministic fake classification run;
- the run records prompt/model/schema-version provenance and a clear outcome;
- validated fake suggestions persist as AI proposal truth;
- suggestions can be queried by target;
- accepted taxonomy remains unchanged;
- admin/Ops can inspect a safe run summary.

### Owning Module(s)

- **AI Taxonomy** — all AI run/suggestion truth.
- Taxonomy supplies read-only vocabulary.

### Dependencies

- Features 01–03;
- `U-CL02-04` explicitly resolved with approved Prisma models/statuses/invariants;
- source target/purpose vocabulary defined for the MVP;
- SH-044, SH-046, SH-047, SH-053 if used, SH-072/077.

### Shared Operations Used

- **SH-001/002.** Protect manual/admin request and run inspection. Local policy: who may request which classification purpose.
- **SH-044 `executeIdempotentCommand`.** Prevent duplicate classification-run creation for same semantic request.
- **SH-046 `publishDomainEvent`.** Publish suggestion/run outcomes if asynchronous consumers require them. AI owns payload meaning.
- **SH-047 `enqueueReliableJob`.** Queue classification work without making QueueJob AI truth.
- **SH-053 `transitionLifecycleState`.** Reuse only if approved run/suggestion status graphs use it. AI supplies transitions.
- **SH-072 `hashCanonicalPayload`.** Hash canonical input/config evidence where approved.
- **SH-077 `buildCanonicalTextSnapshot`.** Deterministic AI classification text snapshot; AI/source owner defines fields.
- **SH-029.** Audit restricted manual backfill/config actions, not every model token.

### Data / Schema

After `U-CL02-04` approval, add the exact approved:

- `AiClassificationLog`;
- `AiSuggestion`;
- AI-specific enums/statuses;
- relations/indexes/uniqueness/idempotency evidence.

Minimum semantic requirements, regardless of exact column names:

**AiClassificationLog must prove:**

- target/context;
- classification purpose;
- provider/model/prompt/schema version;
- canonical input evidence/hash or approved minimized snapshot reference;
- started/completed/failed outcome and timestamps;
- safe provider reference/metadata;
- relation to suggestions.

**AiSuggestion must prove:**

- originating run;
- target/context;
- proposed canonical term or proposed candidate term payload;
- suggestion type;
- AI-owned confidence/provenance;
- current proposal disposition or decision reference according to approved lifecycle;
- timestamps.

Do not use taxonomy join `verified` as AI suggestion status.

### Public Interfaces

- `requestClassificationSuggestions` with fake runner support;
- `getSuggestionsForTarget`;
- `getClassificationRun`;
- `listSuggestionsForReview`;
- internal run/suggestion repositories owned only by AI Taxonomy.

### Logic

- create run from approved classification request;
- canonicalize and hash approved input;
- fake provider returns structured candidate;
- validate against AI output schema;
- persist run then suggestions according to transaction design;
- ensure no accepted taxonomy write;
- support repeat request idempotency;
- keep operational failure separate from run outcome.

### UI / Administrative Surface

Minimum protected AI run/suggestion inspector:

- target ref/type;
- classification purpose;
- model/prompt/schema version;
- run outcome;
- suggestion IDs/term refs/confidence;
- safe error category;
- no raw protected payload unless separately authorized and required.

### Authorization / Compliance

- protected source classification requests require actor/authority or trusted service actor;
- sensitive candidate/healthcare data is not yet sent to a provider;
- no automated employment decision;
- no Search effect from mere suggestion creation.

### Events / Jobs / Integrations

- fake model runner only;
- reliable job and outbox allowed;
- no live Bedrock yet.

### Failure Behavior

- invalid output fake → run failed/invalid according to approved state, no usable suggestion;
- duplicate request → replay existing semantic result;
- unknown target/purpose → reject;
- stale taxonomy IDs → invalid suggestion, not accepted;
- DB failure → no partial accepted taxonomy side effect because none exists.

### Tests

- migration from clean DB;
- lifecycle transition tests;
- idempotency;
- run/suggestion relationship;
- invalid schema;
- no SearchUpsertEvent created by suggestion generation;
- no taxonomy join write;
- AuditEvent not substituted for AiClassificationLog;
- Ops failure not substituted for AI run outcome.

### Out of Scope

- live Bedrock;
- suggestion acceptance/rejection by Taxonomy;
- entity join mutation;
- novel taxonomy term creation;
- candidate private data.

### Exit Gate

- `U-CL02-04` is resolved and architecture/schema documented;
- AI migrations apply cleanly;
- fake run/suggestion flow persists canonical proposal truth;
- no accepted taxonomy or Search write occurs;
- contract/lifecycle/idempotency tests pass;
- admin inspection does not leak protected input.

---

## 05 Structured Foundation-Model Classification

Connect AI Taxonomy to the approved foundation-model provider port with strict input minimization and structured-output validation.

### Objective

Produce real classification suggestions from approved source snapshots while keeping the model provider replaceable and unable to write domain truth.

### User-visible / Observable Result

- an approved classification request can invoke AWS Bedrock (or configured adapter) and produce validated suggestions;
- provider/model/prompt/schema provenance is stored;
- invalid/unparseable output produces a controlled AI run failure and no usable suggestion;
- source text containing prompt-injection-like instructions cannot grant write authority or bypass the schema;
- provider outage is visible in Ops and retry behavior is bounded.

### Owning Module(s)

- AI Taxonomy owns classification policy/run/suggestion truth.
- provider adapter lives behind AI Taxonomy according to approved SH-065 placement.

### Dependencies

- Feature 04;
- `U-CL02-12` approved for production adapter placement;
- active Taxonomy query contract;
- owner-approved source snapshot fixture/contract;
- SH-065, SH-066, SH-078, SH-034–037, SH-048.

### Shared Operations Used

- **SH-065 `invokeFoundationModel` — Proposed canonical provider capability.** AI Taxonomy uses it for classification. Local policy: model, prompt version, classification purpose, timeout. Do not instantiate Bedrock clients in consumers.
- **SH-066 `validateStructuredProviderOutput` — shared validation.** AI Taxonomy owns the JSON/schema contract. Do not trust raw provider JSON.
- **SH-078 `minimizeAndRedactProviderInput`.** Source/privacy owner supplies field policy; shared serializer enforces. Do not build ad hoc redaction.
- **SH-077/072.** Canonicalize/hash provider-bound evidence if approved.
- **SH-048.** Retry transient technical failures only.
- **SH-034–037.** Redact telemetry, capture exception, metrics, integration failures.

### Data / Schema

Use Feature 04 AI records only.

Provider response blobs must not be persisted wholesale unless the approved AI schema/privacy policy explicitly requires them. Prefer:

- normalized output;
- safe provider request/response references;
- model/version;
- validation outcome;
- hashes/diagnostic codes.

### Public Interfaces

No new consumer-facing API beyond Feature 04 request/query contracts.

Internal:

- provider-neutral classification adapter port;
- Bedrock implementation;
- structured response schema/version.

### Logic

1. receive approved classification target/snapshot;
2. load active taxonomy constraints;
3. minimize/redact input;
4. assemble versioned prompt/config;
5. invoke provider with timeout;
6. validate structured result;
7. canonicalize term references/candidates;
8. persist AI run/suggestions;
9. never call Taxonomy mutation or Search write.

### UI / Administrative Surface

Add to AI inspector:

- provider/model version;
- prompt/schema version;
- validation outcome;
- retryable/non-retryable failure category;
- safe latency/token/cost metadata if available and approved.

Do not display protected full prompts by default.

### Authorization / Compliance

- classification purpose determines allowed fields;
- candidate-sensitive input requires Candidate/privacy owner approval;
- healthcare-sensitive input requires Healthcare data-boundary policy;
- no automatic hiring/ranking/rejection;
- no provider call from anonymous unbounded client input.

### Events / Jobs / Integrations

- Bedrock adapter;
- queue worker;
- bounded retries;
- no provider webhook;
- IntegrationFailure + metrics.

### Failure Behavior

- timeout/throttle → retry within bounded policy;
- validation failure → non-usable result, no suggestion;
- provider unknown status → safe failure, no default acceptance;
- redaction policy denies input → fail closed before provider;
- permanent provider rejection → run records failure and Ops evidence.

### Tests

- adapter unit/contract with recorded fixtures or provider mock;
- structured JSON success/failure;
- timeout/throttle retry;
- prompt-injection content treated as data;
- protected-key redaction tests;
- no secrets in logs;
- no direct Taxonomy/Search mutation;
- live sandbox integration test when credentials exist.

### Out of Scope

- suggestion acceptance;
- automatic term creation;
- general content generation;
- recommendations;
- hiring decisions;
- moderation AI.

### Exit Gate

- provider adapter lives only behind approved SH-065 boundary;
- every successful provider result passes SH-066 before persistence;
- prohibited sensitive fields are absent from provider input/logs;
- provider failure/retry is observable;
- model cannot create taxonomy/Search side effects;
- integration and redaction tests pass.

---

## 06 AI Review Queue, Supersession, and Safe Backfill

Make AI suggestions operationally reviewable and batchable without yet converting them to accepted classification.

### Objective

Support bounded review and backfill workflows over AI-owned proposal truth, including stale/superseded handling, while preserving owner boundaries and operational observability.

### User-visible / Observable Result

- authorized admin can filter reviewable suggestions;
- a bounded backfill can request classification for approved targets;
- repeated backfill is idempotent;
- stale suggestions can be marked/superseded according to the approved AI lifecycle;
- low-confidence or conflicting suggestions may be routed for review without automatically creating a ComplianceHold;
- backfill progress/failures are visible.

### Owning Module(s)

- AI Taxonomy — run/suggestion/backfill meaning;
- Admin Review/Hold remains owner of any actual hold.

### Dependencies

Backfill is target-specific, not generalized production completion. Each enabled target requires completed AI persistence and structured provider/output foundations, an owner classification-input contract, sensitivity/minimization policy, SH-123 target validation, and all applicable AP Feature 11/source-integration prerequisites (CL02-R013). Targets missing any prerequisite remain disabled; broader backfill completes only after their mapped integrations.

- Feature 05;
- approved suggestion lifecycle from Feature 04;
- SH-047/048, SH-054 only if reviewer claims are required and approved, SH-011/012 only for explicit hold cases, SH-029/037/038.

### Shared Operations Used

- **SH-047/048.** Reliable batch work and retry. Local policy: target batches, cost/rate limits, staleness.
- **SH-054 `claimWorkItem` — Proposed.** Use only if review assignment/lease is approved. Do not invent a separate review-claim table if shared mechanism is selected.
- **SH-011/012.** Query/request a ComplianceHold only when AI domain policy has evidence for a platform stop sign. Low confidence alone does not automatically equal a hold.
- **SH-029.** Audit backfill start/cancel/material review action.
- **SH-037/038.** Provider/queue operational visibility.
- **SH-044.** Idempotent batch start/request.

### Data / Schema

Use AI-owned records plus canonical queue records.

Do not create:

- a generic CL-02 review-case lifecycle;
- a local ComplianceHold;
- a second AI job ledger.

If review assignment needs durable domain meaning beyond SH-054 mechanics, resolve that architecture before adding a record.

### Public Interfaces

- `listSuggestionsForReview`;
- restricted `enqueueClassificationBackfill`;
- restricted `inspectClassificationBackfill` if owner status exists;
- approved supersede/expire operation according to AI lifecycle.

### Logic

- select only explicitly approved target types;
- use cursor/bounded batches;
- respect provider rate/cost limits;
- skip or supersede suggestions whose source/taxonomy version is stale according to approved rules;
- do not auto-accept high-confidence results;
- allow safe stop/pause between batches.

### UI / Administrative Surface

AI review/backfill admin:

- filters by target/purpose/status/confidence;
- run provenance;
- backfill start/progress/failed count;
- retry/requeue of safe failures;
- no accept/reject classification control until Feature 08 unless it calls the future Taxonomy workflow.

### Authorization / Compliance

- admin/support authority;
- candidate/private classification only where source owner contract permits;
- no bulk export of sensitive inputs through the UI;
- no automated employment outcomes.

### Events / Jobs / Integrations

- queue batching;
- backoff;
- optional event when suggestion becomes reviewable;
- no Search side effects.

### Failure Behavior

- batch partial failure → completed items remain valid; failed items retried/visible;
- provider quota → pause/backoff;
- source no longer eligible for classification → skip with reason;
- review conflict → optimistic conflict, no double disposition.

### Tests

- cursor/batch idempotency;
- pause/retry;
- stale source/taxonomy behavior;
- low-confidence does not create local hold automatically;
- protected target filtering;
- no SearchUpsertEvent from backfill suggestions;
- operational telemetry.

### Out of Scope

- final accepted classification;
- Taxonomy join writes;
- public ranking/recommendations;
- universal admin-review subsystem.

### Exit Gate

- record exactly which targets passed applicable AP/source-owner gates; this feature does not certify generalized multi-target production backfill;

- bounded backfill can run safely and resume without duplicate proposal effects;
- review queue exposes only authorized/minimized data;
- no automatic acceptance or Search write exists;
- provider/queue failures are observable;
- lifecycle/concurrency tests pass.

---

# Phase 3 — Accepted Entity Classification and AI-to-Truth Handoff

Phase 3 follows approved CL02-R001 join ownership and CL02-R003 SH-121 choreography. Applicable join metadata, exact AI lifecycle/schema, and any event vocabulary remain gated; approval of ownership does not approve those details.

## 07 Entity Classification Attachment Ownership and Manual Classification

Implement the one-owner write path for accepted entity classification, proving that Taxonomy validation and contextual entity ownership do not become a generic cross-domain repository.

### Objective

Allow a supported source Module to attach/remove canonical Category/Tag classifications through a single approved lifecycle owner while preserving Taxonomy’s semantic authority.

### User-visible / Observable Result

For at least one representative entity owner:

- an authorized entity classification change calls SH-023;
- accepted canonical term IDs are persisted by the approved join owner;
- invalid/inactive/incompatible terms are rejected;
- the resulting accepted classification can be read and produces SH-022 requirement triggers;
- Search refresh is requested after the authoritative accepted classification changes;
- there is exactly one repository/service that may mutate the representative join.

### Owning Module(s)

- Taxonomy & Classification — validation/semantics;
- contextual entity Module — join create/update/delete/privacy lifecycle under approved CL02-R001;
- Search — projection refresh request truth only.

### Dependencies

- Features 01–06;
- CL02-R001 owner mapping applied; `U-CL02-02` resolved for any exposed join metadata;
- representative source Module public contract;
- SH-023, SH-022, SH-091, SH-123; SH-003 only for approved minimum owner facts; SH-044/051/052.

### Shared Operations Used

- **SH-023.** Taxonomy validates before join write. Local policy: hierarchy/active/compatibility.
- **SH-022.** Taxonomy returns requirement triggers after accepted assignment. Does not assert satisfaction.
- **SH-003 `queryOwnerFacts` — Proposed.** Minimum relationship facts only; not target eligibility. Use confirmed **SH-123 `validateOwnedTargetReference`** through the target owner for existence/version/status and relationship eligibility. No any-entity repository.
- **SH-091.** Source owner requests Search convergence after its accepted classification changes.
- **SH-044/051/052.** Idempotency/concurrency around assignment mutations.
- **SH-029.** Audit material admin overrides when policy requires.

### Data / Schema

Use existing taxonomy joins according to the approved ownership matrix.

Before implementation, document for every join:

- owning Module;
- write repository location;
- allowed creator/remover;
- `source`;
- `confidence`;
- `verified` semantics;
- privacy executor responsibility.

Do not create a generic polymorphic join table to avoid making the decision.

### Public Interfaces

Taxonomy:

- SH-023;
- SH-022.

Representative source owner:

- owner-specific `set/attach/removeClassification` command or equivalent;
- owner-safe accepted-classification query;
- SH-094 projection reflects accepted terms.

Search:

- SH-091 only.

### Logic

- source owner verifies actor/business permission;
- calls Taxonomy validation;
- writes only its owned join/source fields;
- records provenance according to approved semantics;
- resolves triggers for downstream source readiness;
- requests Search refresh;
- does not mark compliance requirements as passed.

### UI / Administrative Surface

Use the representative source owner’s existing classification UI/admin fixture if available. Otherwise provide:

- protected development/admin classification form or contract harness;
- taxonomy selector driven by canonical tree;
- validation error display.

Do not create a Cluster-wide entity editor.

### Authorization / Compliance

- resource owner determines who may classify the entity;
- Taxonomy authorization governs taxonomy-admin changes, not ordinary source classification by itself;
- verification/healthcare requirements remain external gates.

### Events / Jobs / Integrations

- source owner may publish accepted-classification event through SH-046;
- Search refresh through SH-091;
- broad fan-out not required yet.

### Failure Behavior

- stale taxonomy term → reject or revalidate;
- concurrent assignment change → explicit conflict/retry;
- Search refresh failure after source transaction → source classification remains valid; outbox/idempotent refresh eventually repairs;
- external readiness module unavailable → source owner decides whether its own lifecycle action can proceed; no invented Taxonomy fallback.

### Tests

- one repository owner per join;
- classification validation;
- source actor authorization;
- concurrent attach/remove;
- trigger resolution;
- Search refresh requested after accepted change;
- no Taxonomy direct write into foreign entity lifecycle;
- no local taxonomy validator in source owner.

### Out of Scope

- every entity type at once;
- AI acceptance;
- hard-delete/merge;
- unresolved tag trigger additions.

### Exit Gate

- CL02-R001 owner mapping is enforced and applicable `U-CL02-02` metadata semantics are resolved;
- representative accepted classification works end to end;
- static/code review proves only the approved owner mutates the join;
- invalid/inactive assignment is rejected;
- Search refresh is reliable and idempotent;
- no compliance completion is inferred.

---

## 08 AI Suggestion Decision to Accepted Classification to Search

Complete the central CL-02 workflow: AI proposes; Taxonomy decides; the approved assignment owner writes accepted truth; Search refreshes.

### Objective

Turn a reviewable AI proposal into accepted classification only through an explicit Taxonomy-owned decision workflow, while keeping the AI proposal lifecycle and Search projection separate.

### User-visible / Observable Result

- reviewer can inspect an AI suggestion and accept or reject it;
- rejection changes AI proposal disposition only and does not alter accepted taxonomy;
- acceptance revalidates current Taxonomy/source state before writing;
- accepted classification is persisted by its approved owner;
- AI suggestion receives a decision reference/outcome;
- Search refresh occurs only after accepted truth commits;
- replaying the decision does not duplicate joins or Search effects.

### Owning Module(s)

- AI Taxonomy — suggestion record/disposition acknowledgement;
- Taxonomy & Classification — canonical acceptance policy and taxonomy semantics through SH-121; proposal-only rejection remains AI-owned;
- contextual source Module — join write under approved ownership;
- Search — projection refresh.

### Dependencies

- Feature 07;
- confirmed SH-121 `applyAiSuggestion` and approved CL02-R003 choreography;
- approved suggestion status/disposition contract;
- SH-002, SH-023, SH-044, SH-046, SH-051/052, SH-091.

### Shared Operations Used

- **SH-001/002.** Reviewer actor/authority.
- **SH-023.** Revalidate canonical terms at decision time; do not trust stale model output.
- **SH-044.** Idempotent decision command.
- **SH-051/052.** Prevent two reviewers or stale decisions from applying conflicting outcomes.
- **SH-046.** Reliable Taxonomy decision/source classification events when used.
- **SH-091.** Search refresh after accepted truth.
- **SH-029.** Audit material reviewer action.
- **SH-015 `returnDecisionResult` — Proposed shared response contract.** Optional stable review result shape; Taxonomy policy remains local.

### Data / Schema

Uses:

- `AiSuggestion`;
- `AiClassificationLog`;
- approved source taxonomy join/category reference;
- `SearchUpsertEvent`;
- audit/outbox shared records.

Do not store acceptance only in:

- AI status;
- tag join `verified`;
- AuditEvent;
- Search provider document.

### Public Interfaces

- confirmed SH-121 `applyAiSuggestion`;
- AI `recordSuggestionDisposition` after successful accepted mutation;
- representative source classification command;
- SH-091.

SH-121 retains its canonical name and requires suggestion ID/version, target, selected canonical term, reviewer, reason, idempotency key, and audit evidence. Descriptive local names do not replace it. Initial acceptance is restricted to existing canonical IDs; novel proposals remain review-only under U-CL02-15.

### Logic

**Acceptance:**

1. resolve/authorize reviewer;
2. claim/idempotently identify decision;
3. read suggestion through AI interface;
4. verify suggestion still decision-eligible;
5. re-read current taxonomy and target facts;
6. validate selected canonical term(s);
7. commit accepted classification through approved owner;
8. commit Taxonomy decision proof/event;
9. acknowledge AI disposition idempotently;
10. request Search refresh.

**Rejection:**

1. authorize the AI proposal-lifecycle action;
2. AI Taxonomy records the rejection under its approved lifecycle;
3. do not mutate accepted Taxonomy truth, contextual joins, or Search.

Acceptance must not mark AI disposition accepted until the contextual owner's mutation succeeds. Retry with the same suggestion version/idempotency context; a failed AI acknowledgement retries only the missing handoff, without duplicating or reversing accepted classification. Exact lifecycle/status approval remains U-CL02-04.

### UI / Administrative Surface

Review screen:

- safe target summary;
- proposed term(s);
- confidence/provenance;
- model/prompt version;
- current canonical term selector;
- accept/reject with reason;
- conflict/stale state;
- clear distinction between “AI suggestion” and “accepted classification.”

### Authorization / Compliance

- reviewer authority server-side;
- high-risk classification still triggers external verification/healthcare requirements;
- acceptance does not certify a Professional or Job;
- no private source payload exposed beyond reviewer authorization.

### Events / Jobs / Integrations

- Taxonomy/source transactions and outbox;
- AI acknowledgement may be eventual/idempotent if cross-Module transaction is not available;
- Search refresh after source truth;
- retry safe at each step according to approved workflow.

### Failure Behavior

- taxonomy changed since suggestion → stale/review conflict; require revalidation;
- source deleted/ineligible → deny acceptance or handle per source owner;
- AI acknowledgement fails after accepted source write → retry acknowledgement; accepted source truth remains authoritative;
- Search refresh fails → retry; accepted source truth remains authoritative;
- duplicate accept → replay result, no duplicate join.

### Tests

- accept path;
- reject path;
- stale taxonomy;
- concurrent reviewer conflict;
- duplicate command;
- acknowledgement failure/retry;
- Search failure/retry;
- no Search refresh on pure rejection;
- AI status alone never used as accepted truth;
- accepted high-risk tag triggers requirement but not readiness success.

### Out of Scope

- automated high-confidence acceptance;
- all novel canonical-term creation/activation in the initial AI-acceptance path, including reviewer-approved creation; future support remains gated by `U-CL02-15`;
- broad multi-entity backfill acceptance;
- hiring decisions.

### Exit Gate

- `U-CL02-05` is resolved;
- accepted and rejected paths preserve separate owners;
- acceptance produces accepted source classification before Search refresh;
- replay/concurrent decision tests pass;
- no dual-write transaction assumption crosses Module repositories;
- UI clearly distinguishes proposal from accepted truth.

---

# Phase 4 — Cross-Cluster Discovery Integration

This phase proves CL-02’s important inbound/outbound contracts with neighboring Clusters without importing their source truth.

## 09 Public Offering, Gig, Job, Organization, and Professional Discovery

Add the main public business object projections using source-owned Search DTOs and readiness decisions.

### Objective

Make the public marketplace/hiring discovery surfaces project only current, owner-approved source truth for Offerings, Gigs, Jobs, Organizations, and ProfessionalProfiles.

### User-visible / Observable Result

- eligible Offering/Gig/Job/Organization/Professional records appear in public search;
- nonpublic/inactive/noncompliant examples do not;
- Job results expose only approved public fields such as title, organization, fuzzy/public location, and compensation disclosure fields allowed by the owner;
- source changes trigger Search refresh;
- Search can explain exclusion using safe owner decision reasons;
- no Search repository directly owns those business tables.

### Owning Module(s)

- each source Module owns source data/readiness;
- Search owns provider projection/query;
- Taxonomy owns classification/facets.

### Dependencies

- Features 01–08;
- stable SH-094 and SH-024 contracts for each source;
- Professional Eligibility, Job Compliance, Trust/Healthcare as applicable;
- SH-028 fuzzy location;
- Typesense schema additions approved under `U-CL02-09`.

### Shared Operations Used

- **SH-094 `buildSourceProjection` — each source owner.** Search gets only approved DTOs/version. Do not read foreign Prisma tables.
- **SH-024 `evaluatePublicReadiness` — each source/compliance owner.** Search composes decisions; does not centralize policy.
- **SH-016 `evaluateProfessionalReadiness` — Professional Eligibility.** For Professional/Offering public readiness where applicable.
- **SH-021 `evaluateJobCompliance` — Job Compliance.** Search consumes result, does not parse Job law rules.
- **SH-018 `evaluateVerificationReadiness` / approved TrustBadge query.** Only where source readiness policy needs it.
- **SH-020 `evaluateHealthcareReadiness`.** Only where healthcare classification requires it.
- **SH-028.** Fuzzy public location.
- **SH-091/092/115.** Refresh, provider write, projection build.
- **SH-011.** Hold decision where source/public-readiness policy requires it.

### Data / Schema

No foreign source tables move into CL-02.

Search provider documents are derived, versioned schemas by entity type/collection.

`SearchEntityType.user` remains disabled.

### Public Interfaces

Source Modules:

- SH-094 implementations;
- SH-024/readiness implementations;
- source events/SH-091 invocation on relevant changes.

Search:

- `searchPublicDiscovery` multi-entity support;
- per-entity result DTOs;
- facets/filters approved by provider schema.

### Logic

For each entity:

1. load owner DTO;
2. load owner/compliance readiness decisions;
3. if not allowed, delete provider doc;
4. if allowed, enrich with accepted Taxonomy;
5. apply fuzzy public location;
6. apply approved display/ranking metadata;
7. write provider projection;
8. query through safe result mapping.

### UI / Administrative Surface

Public discovery API/UI may now show representative result cards/rows for supported types.

Admin debug shows:

- source version;
- readiness components by safe reason code;
- current provider state;
- last refresh.

### Authorization / Compliance

- public Search itself may be anonymous;
- only public-safe source DTO fields may be indexed;
- Job compliance/Professional readiness/Healthcare/verification/holds stay owner decisions;
- exact coordinates/private data forbidden.

### Events / Jobs / Integrations

- source change events or direct SH-091 calls;
- Search worker;
- Typesense;
- no AI in indexing.

### Failure Behavior

- upstream decision unavailable → fail closed or preserve last-known state only if the owner contract explicitly permits a TTL; do not invent stale-readiness policy;
- missing source → delete projection;
- provider failure → retry/observe;
- taxonomy unavailable → if required to build a safe doc, leave work unresolved rather than index an incomplete unsafe document.

### Tests

Per entity type:

- eligible index;
- inactive/nonpublic remove;
- hold remove;
- Job compliance block remove;
- Professional readiness block remove;
- healthcare/verification trigger behavior via owner decision;
- exact location absent;
- taxonomy facets canonical;
- Search direct-repository import test/code review;
- E2E public query.

### Out of Scope

- candidate protected search;
- ranking experiments beyond approved baseline;
- source lifecycle UI;
- reviews/reputation policy not already exposed by owner.

### Exit Gate

- each supported public entity has an owner SH-094 contract and readiness contract;
- no Search direct Prisma dependency on source owner repositories is required for normal projection;
- blocked/nonpublic examples are absent;
- source changes converge through SH-091;
- field/privacy/fuzzy-location tests pass;
- Search remains rebuildable without AI.

---

## 10 Protected Candidate Search and Entitlement-Aware Boosts

Implement candidate discovery only through Candidate-owned privacy projection, organization authority, and Track entitlement.

### Objective

Allow an authorized Organization actor to search privacy-safe candidate projections while keeping raw resume/application truth and entitlement policy outside Search.

### User-visible / Observable Result

- authorized, entitled organization recruiter can search allowed candidates;
- unauthorized or unentitled actor is denied with a stable reason;
- only Candidate-owned privacy-safe fields are queryable/returned;
- `rawResumeTextIndexed` remains false and raw resume content is absent from provider documents;
- candidate boost metadata changes result ordering only after candidate visibility/privacy readiness passes;
- entitlement change triggers reindex without local premium flags.

### Owning Module(s)

- Candidate Application & Resume Privacy — `CandidateSearchProjection` and privacy truth;
- Organization Hiring — organization membership/authority facts;
- Track Subscription & Entitlement — candidate-search/boost commercial policy;
- Search — protected provider document/query/ranking.

### Dependencies

- Feature 09;
- Feature 11 prerequisite-contract slice and SP Feature 09 enforcement contract/anti-resurrection proof, before this feature exits;
- Candidate projection/privacy eligibility, requester/Organization authority, applicable commercial entitlement, public/protected readiness, and applicable hold/moderation exclusions are available synchronously;
- `U-CL02-10` resolved;
- Candidate projection contract;
- Organization authority contract;
- SH-005 Track entitlement contract;
- Search protected collection/surface topology approved under `U-CL02-09`.

### Shared Operations Used

- **SH-001/002.** Resolve recruiter/admin actor and organization-scoped action. Do not create Search organization roles.
- **SH-003 `queryOwnerFacts` — Proposed.** Organization Hiring supplies minimal membership facts if authorization requires them.
- **SH-005 `resolveEntitlement` — Track.** Resolve candidate-search access/boost. Local Search policy: permitted boost mapping only. Do not store premium booleans.
- **SH-094.** Candidate owner supplies privacy-safe source projection.
- **SH-024.** Candidate owner supplies protected/public readiness decision.
- **SH-091/092.** Candidate projection refresh/write.
- **SH-030 `recordSensitiveAccess`.** Record protected candidate search/access where policy requires.
- **SH-028.** Fuzzy location only.
- **SH-044.** Idempotent refresh.

### Data / Schema

Source truth remains:

- `CandidateSearchProjection` in Candidate Module;
- Track grants/usage in Track Module.

Search provider document may include only approved fields such as normalized skills/titles, experience band, fuzzy location, remote preference, and permitted boost metadata.

Do not persist a second CandidateSearchProjection table in Search.

### Public Interfaces

- `searchCandidatesForOrganization`;
- Candidate SH-094 projection query;
- Candidate protected-readiness/privacy query;
- Track SH-005;
- SH-091 on Candidate/Track change.

### Logic

**Index:**

1. Candidate owner says candidate is searchable on protected surface;
2. build privacy-safe source projection;
3. resolve approved boost entitlement;
4. apply fuzzy location;
5. write protected provider doc.

**Query:**

1. actor/authz organization action;
2. feature entitlement if required;
3. validate filters/sorts;
4. query protected collection;
5. return safe result DTO;
6. record sensitive access as required.

### UI / Administrative Surface

Organization candidate-search UI/API:

- approved filters only;
- no raw resume preview unless a separate Candidate/Media entitlement workflow is invoked after result selection;
- visible entitlement denial/limit state where product UX requires it.

### Authorization / Compliance

- organization-scoped authority required;
- Candidate privacy decision required;
- Track entitlement required where commercial plan controls access/boost;
- search boost cannot bypass candidate privacy;
- no automated hiring/ranking decision beyond search relevance/approved boost; Search results must not be treated as hiring recommendation truth.

### Events / Jobs / Integrations

- Candidate projection changes → SH-091;
- Track boost changes → SH-091;
- Search worker/Typesense;
- access audit.

### Failure Behavior

- Candidate privacy revoked → delete provider doc;
- entitlement expires → query access denied and/or boost removed according to Track contract;
- organization membership revoked → query denied immediately through authority;
- provider unavailable → controlled failure; do not fall back to raw DB candidate scanning;
- stale candidate doc → reconciliation/refresh.

### Tests

- authorized vs unauthorized org actor;
- entitled vs unentitled;
- privacy-visible vs hidden candidate;
- raw resume never indexed;
- exact location absent;
- boost applies only to eligible candidate;
- entitlement removal reindexes;
- access audit;
- no Search write to CandidateSearchProjection;
- no local premium state.

### Out of Scope

- applicant tracking;
- resume parsing;
- resume file access;
- automated shortlist/reject/hire decisions;
- candidate application lifecycle;
- entitlement plan management.

### Exit Gate

- Feature 11 prerequisite-contract slice is complete; later reaction wiring is not a substitute for synchronous permission/enforcement checks;

- `U-CL02-10` is resolved/documented;
- protected search enforces organization authority, Candidate privacy, and Track policy;
- raw resume/application content is absent;
- boost never creates visibility;
- access and reindex tests pass;
- Search remains projection only.

---

## 11 Moderation, Privacy, Holds, Location, and Readiness Reaction Contracts

Prove that authoritative external decisions can remove/restore CL-02 discovery without transferring their lifecycles into Search.

**Approved execution split (CL02-R014):** complete the prerequisite-contract slice after Feature 09 and before Feature 10: Candidate privacy/projection eligibility, Organization/requester authority, applicable entitlement, readiness, and applicable hold/moderation exclusion, including SP Feature 09 contract tests. Later asynchronous deindex/reindex and owner-orchestrator reaction integration may follow Feature 10. U-CL02-10 remains unresolved for exact protected-search composition.

### Objective

Make public/protected Search react correctly to moderation, privacy, holds, readiness, and fuzzy-location changes, and make AI/Search implement Privacy target executors for their own records.

### User-visible / Observable Result

- moderation hide/freeze removes a discoverable entity;
- moderation restore triggers reevaluation rather than blind reindex;
- Privacy erasure/restriction removes Search provider documents and executes against AI-owned records where instructed;
- ComplianceHold can cause exclusion only through the approved readiness/hold policy;
- fuzzy-location change updates projection without exact-coordinate exposure;
- source readiness recovery can restore projection after reevaluation;
- Privacy/Moderation orchestration receives typed execution success/failure.

### Owning Module(s)

- Moderation owns moderation decision;
- Privacy owns privacy workflow/retention-exemption;
- Holds owns hold lifecycle;
- Location Safety owns location policy;
- source/compliance Modules own readiness;
- Search/AI execute against their owned records/provider state.

### Dependencies

- Feature 09 for the prerequisite-contract slice; Feature 10 only for later protected-surface reaction integration;
- SH-095–098;
- SH-103;
- SH-011;
- SH-028;
- Search SH-091/092;
- AI subject-data enumeration.

### Shared Operations Used

- **SH-103 `executeModerationDecision`.** Search executes provider hide/restore effect; Moderation owns decision. Do not build Search moderation cases.
- **SH-095 `executePrivacyInstruction`.** Search/AI execute owner-specific erase/anonymize/restrict actions. Do not build CL-02 PrivacyRequest.
- **SH-096 `enumerateSubjectData`.** Search/AI expose owned subject-linked data.
- **SH-097 `evaluateRetentionRequirement`.** AI/Search supply record facts; Privacy records exemption.
- **SH-098 `anonymizePersonalFields`.** Apply approved anonymization mappings.
- **SH-011 `evaluateComplianceHold`.** Consume platform stop signs; no local flags.
- **SH-028.** Fuzzy location.
- **SH-091/092.** Refresh/delete provider documents.
- **SH-029/030.** Audit sensitive/destructive actions/access where required.
- **SH-037.** Operational failure.

### Data / Schema

No new:

- ModerationCase;
- PrivacyRequest/DataErasureJob;
- ComplianceHold;
- FuzzyLocationCache;
- DataRetentionExemption.

CL-02 effects may alter/delete:

- Search provider docs;
- Search-owned work metadata as permitted;
- AI-owned personal metadata/records according to Privacy instruction and retention ruling.

### Public Interfaces

Search:

- SH-103 target executor;
- SH-095/096 implementations;
- projection refresh.

AI:

- SH-095/096 implementations;
- retention-facts implementation as approved.

Taxonomy join owner:

- Privacy executor according to Feature 07 ownership.

### Logic

- moderation hide → expected Search state absent;
- restore → reevaluate SH-024 before any upsert;
- privacy erase → delete provider doc, then owner-specific records according to instruction;
- hold/readiness change → refresh and compose current decisions;
- location change → refresh using only SH-028 output;
- every external decision reference remains source-owned.

### UI / Administrative Surface

Search debug should show safe exclusion reason categories:

- source_not_public;
- moderation;
- privacy;
- hold/readiness;
- location/projection failure;
- provider failure.

Do not expose sensitive moderation/legal detail publicly.

### Authorization / Compliance

- trusted service-to-service execution;
- admin inspection protected;
- destructive/privacy actions idempotent;
- retention exemptions must be explicit Privacy truth;
- no exact location in Search.

### Events / Jobs / Integrations

- event-driven refreshes;
- privacy target jobs;
- provider delete;
- retries/dead-letter;
- optional backfill after broad moderation/hold changes.

### Failure Behavior

- provider delete failure → Privacy/Moderation target execution returns failure/retryable state; source decision remains authoritative;
- restore while source still blocked elsewhere → remain absent;
- Privacy retention exemption → retain only approved owner data while still deindexing public provider doc when required;
- lost event → reconciliation in Phase 5 must repair.

### Tests

- moderation hide/restore;
- Privacy deindex;
- AI privacy executor;
- hold block/release;
- fuzzy location change;
- exact location absent;
- restore does not bypass another gate;
- provider delete retry;
- execution result reported to orchestrator;
- no local moderation/privacy/hold tables.

### Out of Scope

- moderation case adjudication;
- PrivacyRequest UX;
- hold review;
- exact-location reveal;
- legal retention decision-making.

### Exit Gate

- authoritative external decisions can reliably remove/restore Search through public contracts;
- Privacy can enumerate/execute CL-02 targets without ownership theft;
- exact location/private data stays excluded;
- duplicate events/actions are harmless;
- no local moderation/privacy/hold source truth exists;
- integration tests pass.

---

# Phase 5 — Reconciliation, Privacy, and Production Hardening

Taxonomy-impact enumeration (CL02-R007): Taxonomy identifies changed canonical terms; each contextual entity owner supplies its affected entity IDs. Neither Taxonomy nor Search scans foreign joins. Feature 12 fanout requires those owner contracts and preserves U-CL02-13 for exact event vocabulary/version.

## 12 Search Reconciliation, Backfill, Debug, and Performance

Operationalize Search as a rebuildable projection at scale, with explicit mismatch repair, bounded backfill, debug tooling, and performance safeguards.

### Objective

Ensure Search can recover from lost events, provider drift, schema upgrades, bulk taxonomy changes, and provider degradation without manual database surgery or source-truth corruption.

### User-visible / Observable Result

- authorized admin can inspect expected vs actual projection state;
- a bounded reindex/backfill can rebuild selected entity types;
- reconciliation identifies and repairs missing/stale/extra provider documents;
- indexing lag, queue depth, provider failures, and dead letters are measurable;
- broad taxonomy or entitlement changes can fan out refreshes in controlled batches;
- public search meets approved latency/error targets under representative load.

### Owning Module(s)

- Search / Public Visibility — reconciliation/backfill/debug and provider projection.
- source Modules remain owner of source truth.

### Dependencies

- all prior Search/public integration features;
- SH-093, SH-047/048, SH-036–040, SH-044/045;
- Search provider schema/versioning decision;
- source enumeration contracts for backfill.

### Shared Operations Used

- **SH-093 `reconcileSearchProjection`.** Canonical Search reconciliation. Local policy: expected doc identity/version.
- **SH-047/048.** Batch/retry/dead-letter.
- **SH-044/045.** Idempotent admin/backfill and event dedupe.
- **SH-036/037/038/039/040.** metrics, integration failures, queue telemetry, health, incident correlation.
- **SH-032–035.** request context/log/redaction/exception capture.
- **SH-115.** rebuild provider docs from current approved inputs.

### Data / Schema

No second Search truth store by default.

If performance later requires a durable Search read model beyond Typesense, that is a new architecture decision and must preserve projection semantics.

Backfill cursors/checkpoints should use canonical queue/work infrastructure unless Search-specific durable business meaning is demonstrated.

### Public Interfaces

- restricted `startSearchBackfill`;
- `inspectSearchProjection`;
- SH-093 reconciliation;
- health/readiness check;
- safe metrics/dashboard feeds.

### Logic

- enumerate source IDs through owner contracts, not direct all-domain DB queries unless root architecture explicitly approves controlled batch access;
- coalesce refreshes where safe;
- provider document schema version triggers rebuild;
- reconcile missing expected docs and unexpected stale docs;
- maintain bounded concurrency/rate limits;
- allow pause/resume/cancel of admin backfills through shared job mechanisms.

### UI / Administrative Surface

Search operations dashboard:

- queue lag/depth;
- processed/unprocessed counts;
- provider health;
- per-entity projection status;
- recent failures;
- backfill progress;
- reconciliation mismatch counts;
- safe retry control.

### Authorization / Compliance

- admin/support authority;
- backfill cannot bypass readiness/privacy;
- debug does not expose raw private source payloads;
- rate limits/cost safeguards.

### Events / Jobs / Integrations

- scheduled reconciliation;
- schema-version backfill;
- broad-change fan-out;
- provider health;
- incidents.

### Failure Behavior

- provider outage → pause/backoff and visible degradation;
- source owner unavailable → leave work unresolved, no unsafe stale override;
- backfill partial failure → resumable;
- extra provider doc with no eligible source → delete;
- repeated mismatch → Ops incident.

### Tests

- deliberate missing/stale/extra docs;
- lost event recovery;
- backfill pause/resume/idempotency;
- concurrent live refresh + backfill;
- provider rate-limit handling;
- dead-letter retry/reconcile;
- query/load performance;
- no source mutation during reconcile.

### Out of Scope

- new search product features;
- recommendation engine;
- vector/semantic search unless separately approved;
- unbounded provider-specific optimization.

### Exit Gate

- a clean provider collection can be rebuilt from source contracts;
- lost-event/provider-drift scenarios repair deterministically;
- operations dashboard exposes lag/failure/backfill state;
- backfill/live-update concurrency is safe;
- performance/load targets are recorded and met for MVP baseline;
- no source lifecycle mutation is performed by reconciliation.

---

## 13 Cluster Security, AI Privacy Retention, Audit Completeness, and Production Readiness

Perform final CL-02 hardening across Taxonomy, AI, Search, provider boundaries, privacy, concurrency, and destructive-migration safety.

### Objective

Make CL-02 production-ready without leaving hidden ownership, privacy, provider, security, or recovery gaps.

### User-visible / Observable Result

- taxonomy administration has complete authorization/audit coverage;
- AI personal/sensitive data retention and erasure behavior is explicit and testable;
- provider secrets and sensitive payloads are absent from client/telemetry;
- AI and Search provider degradation is observable and recoverable;
- critical CL-02 workflows pass E2E tests;
- destructive taxonomy changes remain disabled unless explicitly approved/migrated;
- operations have documented runbooks for Search drift, AI failures, and backfills.

### Owning Module(s)

- each CL-02 Module for its own source records/policy;
- Privacy/Audit/Ops for their canonical truths;
- provider owners for their adapters.

### Dependencies

- Features 01–12;
- `U-CL02-11` resolved before sensitive AI production use;
- all production-relevant Proposed Rulings approved;
- root security/privacy/observability standards.

### Shared Operations Used

As applicable across final verification:

- SH-001/002/011;
- SH-029/030;
- SH-032–040;
- SH-044–048;
- SH-051/052;
- SH-065/066;
- SH-078/079;
- SH-091–098;
- SH-103;
- SH-115.

No new duplicate primitive is introduced in hardening.

### Data / Schema

Review:

- taxonomy uniqueness/cascade constraints;
- unresolved destructive cascades;
- AI indexes/retention fields;
- SearchUpsertEvent indexes;
- foreign-key/delete behavior;
- provider document schema versions;
- privacy subject-data indexes needed for execution;
- migration rollback/destructive-change plan.

Any destructive migration requires:

- backup/verification plan;
- backfill;
- source-owner review;
- provider reindex plan where projection is affected;
- explicit architecture update.

### Public Interfaces

Freeze/version the MVP contracts:

- SH-022/023;
- AI request/query/disposition;
- SH-091;
- public Search;
- protected candidate Search;
- debug/backfill;
- Privacy/Moderation target execution.

Breaking changes require versioning/migration according to root standards.

### Logic

Security/privacy review must prove:

- all protected endpoints server-authorized;
- public Search field/facet allowlists;
- no raw resume/PHI/private message leakage;
- provider input minimization;
- provider output validation;
- no model tool authority;
- no direct Typesense calls outside Search;
- no direct Bedrock classification calls outside AI Taxonomy;
- no local premium/hold/readiness truth;
- privacy erasure/restriction end-to-end;
- audit vs Ops vs domain truth separation;
- concurrency/idempotency under retries.

### UI / Administrative Surface

Finalize safe states:

- loading/empty/error/degraded Search;
- taxonomy conflict/validation states;
- AI provider unavailable/invalid output states;
- review stale/conflict state;
- Search index failure/admin recovery state;
- authorization denial without sensitive reason leakage.

### Authorization / Compliance

- permission matrix coverage;
- protected candidate access audit;
- privacy retention/exemption behavior;
- moderation/hold/readiness reaction;
- healthcare/candidate provider-input gates;
- no automated employment decision path.

### Events / Jobs / Integrations

- chaos/degradation tests for Bedrock and Typesense;
- queue retry/dead-letter;
- provider reconciliation;
- alert thresholds for indexing lag/failure;
- privacy target retry.

### Failure Behavior

- every provider/queue failure has a typed owner outcome and Ops evidence;
- repeated permanent failure becomes dead-letter/incident, not infinite retry;
- source truth remains unchanged during provider outage;
- privacy destructive action never reports success until owner/provider effect satisfies the defined target result;
- stale Search results are repaired or explicitly degraded according to approved policy.

### Tests

Required final suite:

- unit tests for all Module invariants;
- public-interface contract tests;
- lifecycle transition tests;
- cross-Module integration;
- Typesense adapter;
- Bedrock adapter;
- idempotency/concurrency;
- Privacy;
- moderation/holds;
- candidate privacy/entitlement;
- telemetry redaction;
- E2E:
  1. taxonomy term → Search;
  2. AI suggestion → review → accepted classification → Search;
  3. public entity index → source hidden → deindex;
  4. Privacy instruction → Search/AI execution;
  5. protected candidate Search allow/deny;
  6. provider outage → recovery/reconcile.

Run repository typecheck, lint, unit/integration tests, production build, and E2E commands defined by root context.

### Out of Scope

- unresolved taxonomy merge/alias features;
- semantic/vector recommendation systems;
- automated candidate ranking/hiring;
- general-purpose AI generation;
- new search monetization;
- new Cluster ownership decisions.

### Exit Gate

- all production-relevant `U-CL02-*` decisions are either resolved or their behaviors remain explicitly disabled;
- no unresolved behavior is permissively active;
- security/privacy review passes;
- provider degradation/recovery tests pass;
- Search rebuild/reconciliation passes;
- Audit/Ops/domain-truth separation is verified;
- no duplicate canonical SH implementation is found;
- critical E2E workflows pass;
- migrations/backfills are reversible or have explicit destructive-change approval;
- context and progress tracker are updated.

---

## AI source-integration coordination (CL02-R015)

| AI Module feature | Cluster coordination | External prerequisites and exit evidence |
| --- | --- | --- |
| AP 08 Professional/Offering integration | Feature 09 | Professional and Offering owners provide versioned, approved classification-input DTOs and target validation; sensitivity/minimization and AP 07 handoff prerequisites pass; record owner contract/integration test evidence. |
| AP 09 Organization/Job integration | Feature 09 | Organization Hiring supplies approved Organization/Job classification inputs and target validation; Job Compliance remains separate; record AP prerequisites and source-version/privacy contract tests. |
| AP 10 Candidate integration | Feature 10 | Candidate owner supplies an explicitly safe AI classification-input contract and target validation, with approved privacy/retention prerequisites; record AP integration evidence separately from protected Search projection evidence. |

These AI inputs are distinct from SH-094 Search projections. Feature 06 backfill may use only targets already meeting applicable AP prerequisites; Feature 12 broader backfill uses the completed mappings above. Cluster completion must name any deferred source integration and must not imply TP Feature 10 internal normalization maintenance is complete. No duplicate Cluster maintenance feature is introduced.

## Cross-Cluster Integration Phase

**Phase 4 is the required Cross-Cluster Integration Phase.**

Its purpose is not to implement CL-03, CL-06, CL-08, CL-09, or CL-01 source truth. It proves that CL-02 can consume their public contracts safely:

```text
source owner truth
→ owner-safe projection/readiness decision
→ CL-02 Search projection
```

The integration phase passes only if:

- source Modules retain their repositories and lifecycle decisions;
- Search uses SH-094/SH-024 or named owner interfaces;
- candidate search uses Candidate/Organization/Track contracts;
- moderation/privacy/hold/location decisions are consumed, not copied;
- Typesense remains Search-owned;
- no neighboring Cluster must expose a raw repository to make the integration work.

---

## Hardening Phase

**Phase 5 is the CL-02 Hardening Phase.**

It covers only CL-02-relevant hardening:

- provider degradation and recovery;
- Search reconciliation/backfill;
- concurrency and idempotency;
- AI input/output security;
- candidate/search privacy;
- AI retention/erasure;
- moderation/hold reaction;
- audit completeness;
- observability and indexing lag;
- query/provider performance;
- destructive taxonomy migration safety;
- production readiness.

It does not add new product scope.

---

## Phase Summary

| Phase | Name | Numbered features |
|---|---|---|
| 1 | Accepted Vocabulary to Rebuildable Search | 01–03 |
| 2 | Traceable AI Suggestions Without Accepted-Truth Leakage | 04–06 |
| 3 | Accepted Entity Classification and AI-to-Truth Handoff | 07–08 |
| 4 | Cross-Cluster Discovery Integration | 09–11 |
| 5 | Reconciliation, Privacy, and Production Hardening | 12–13 |

**Total numbered features: 13**

---

Approved partial ordering: Features 01–09 → Feature 11 prerequisite contracts → Feature 10 → remaining Feature 11 reaction integration → Features 12–13. This explicit split does not weaken SP Feature 10 prerequisites.

## Phase Execution Pattern

Before each numbered feature:

1. Read required context.
2. Confirm the previous exit gate.
3. Check the feature’s `U-CL02-*` architecture gates.
4. Confirm every Proposed Ruling used by the feature is approved.
5. Write the concise feature implementation specification.
6. Confirm schemas, contracts, permissions, shared operations, provider boundaries, and tests.
7. Implement only that feature.
8. Run typecheck/lint/tests/build as applicable.
9. Perform workflow verification.
10. Update progress.
11. Update architecture only if a binding decision legitimately changed.
12. Record risks, assumptions, failures, and deferred work.

If an unresolved architecture gate is encountered, the implementation step is:

```text
stop
→ document the decision required
→ resolve/approve architecture
→ update architecture.md
→ then implement
```

It is never:

```text
guess a convenient schema/API
→ ship it
→ let progress redefine architecture
```

---

## Required Feature Specification

Each numbered feature must later receive a concise implementation specification containing:

- Objective
- Observable result
- Dependencies
- Architecture gates / proposed rulings used
- In scope
- Out of scope
- Owning Module(s)
- Data records affected
- Public interfaces
- Shared operations consumed
- Permissions
- Primary workflow
- UI/admin states if applicable
- Provider integrations
- Jobs/events
- Idempotency/concurrency
- Error/failure behavior
- Tests
- Acceptance criteria
- Documentation updates

Do not pre-write giant implementation specifications for every feature.

Specify the next numbered feature in detail immediately before implementation, using this build plan as the sequencing/ownership authority.

---

## Required Completion Report

After each feature, the coding agent must report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Architecture rulings resolved/used
- Shared operations reused
- Public interfaces added/changed
- Events/jobs added
- Provider adapters added/changed
- Tests added/changed
- Commands run
- Manual/workflow verification
- Documentation updated
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

The completion report must explicitly state if any direct foreign repository access, provider client, local queue, local audit helper, local entitlement flag, or local readiness rule was introduced. The expected answer is normally **none** unless architecture explicitly approved an exception.

