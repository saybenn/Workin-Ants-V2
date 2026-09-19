# Job Compliance Module Implementation Plan

> **Module ID:** `job_compliance`  
> **Module name:** Job Compliance Module  
> **Primary Cluster:** CL-06 — Organization Hiring & Candidate Pipeline  
> **Authority:** `job_compliance/module-architecture.md`, subordinate to CL-06 `build-plan.md`  
> **Build status:** `mvp_active_legal_gated`

This plan converts the Job Compliance Module architecture into ordered, testable implementation work. It is intentionally narrower than the CL-06 build plan and does not change Cluster sequencing or ownership.

Production Job publication remains blocked until U-CL06-05/07 are approved and the binding U-CL06-06 evidence invariant has an approved implemented persistence design. Jurisdiction-aware production additionally requires an approved owner/interface for unresolved SH-120 `normalizeJurisdictionContext` (Unresolved). Features may be contract-stubbed or implemented below that boundary only where the feature explicitly permits it; no unresolved decision may be silently implemented as permissive behavior.

## Core Principle

Implement Job Compliance as narrow, verifiable owner slices:

```text
public/observable behavior
→ validated command/query
→ Job Compliance-owned policy
→ authoritative Job Compliance write/read
→ canonical shared-operation calls
→ domain event / audit / notification intent
→ tests
→ exit gate
```

A feature does not require artificial UI. Its observable result may be a versioned rule record, a persisted check/finding/disclosure, a stable decision query, a durable worker result, an admin review surface, a privacy executor response, or a cross-Module contract proof.

The Module does **not** become the Job lifecycle owner, Search indexer, candidate-screening service, generic moderation engine, generic rule platform, generic queue, or legal authority.

## Build Rules

The [Shared Operations registry](../../../shared/shared-operations.md) governs permanent IDs, canonical names, owners, classifications and statuses. Registered use points below carry verified IDs/statuses. Proposed ruling entries may support planning and owner-specific interfaces/mechanisms, but cross-platform SH API/schema commitment requires separate explicit approval; any exit gate relying on that shared API must verify approval. Unresolved entries must not be silently implemented or replaced locally. The approved Job Compliance publication envelope does not approve a proposed shared decision envelope.

1. Follow root architecture/code standards, Canonical Shared Operations, CL-06 architecture, CL-06 build plan, and `job_compliance/module-architecture.md`.
2. Job Compliance owns only Job posting rules, checks, findings, compensation-disclosure proof, Job Compliance decision policy, and architecture-approved historical evaluation proof.
3. Organization Hiring owns `Job`, `JobStatus`, `JobVisibility`, offered compensation, and public Job lifecycle.
4. Consume neighboring Modules through public interfaces/events; no direct cross-domain Prisma repository access.
5. Reuse canonical Shared Operations. Do not create local auth, permission, idempotency, queue, retry, lock, hash, text-normalization, scanner-runtime, outbox/inbox, audit, hold, notification, Search, or privacy frameworks.
6. Runtime-validate all external/public inputs.
7. Human mutations and restricted reads are authenticated and authorized server-side.
8. Lifecycle transitions are transaction-safe and reject stale state.
9. Async evaluation/rescan work is durable, idempotent, retry-aware, dead-letter-aware, and observable.
10. Scanner/library failure is operational/technical and never becomes approval or legal rejection.
11. Unknown jurisdiction/rule applicability fails to explicit review/unavailable, never silent pass.
12. Job Compliance decision and Job lifecycle remain separate.
13. Search remains a projection; Organization Hiring performs the Search handoff after applying the decision.
14. Candidate screening/FCRA adverse action remains Trust Verification-owned.
15. `ComplianceHold` remains the reusable stop sign; no local block table/boolean.
16. Generic `AuditEvent` is separate from Job Compliance evidence.
17. Privacy owns privacy-request orchestration and retention exemptions; Job Compliance implements only its owner executor.
18. Matched text and protected-class phrases are minimized/redacted from telemetry, events, analytics, and notifications.
19. Every numbered feature ends with automated tests, workflow/contract verification, documentation/progress updates, and an exit gate.
20. A failed exit gate stops sequential execution until fixed or architecture/build plan is explicitly revised.

## Preconditions

### Hard platform dependencies

These must exist, or a versioned platform fixture must exist where the CL-06 build plan explicitly permits contract stubbing:

- Prisma/PostgreSQL migration and transaction layer;
- runtime validation standard (project evidence identifies Zod in the application stack);
- SH-001 `resolveAuthenticatedActor` (Confirmed);
- SH-002 `authorizeResourceAction` (Confirmed) with RLS/server parity support where applicable;
- SH-044 `executeIdempotentCommand` (Confirmed);
- SH-052 `withOptimisticConcurrency` (Confirmed) and/or SH-051 `acquireAggregateLock` (Confirmed);
- SH-046 `publishDomainEvent` (Confirmed) transactional outbox and consumer inbox dedupe;
- SH-047 `enqueueReliableJob` (Confirmed) and SH-048 `executeRetryWithBackoff` (Confirmed);
- structured logging/request/correlation IDs;
- SH-029 `appendAuditEvent` (Confirmed);
- Privacy target protocol (SH-096 `enumerateSubjectData` (Confirmed), SH-095 `executePrivacyInstruction` (Confirmed), SH-097 `evaluateRetentionRequirement` (Confirmed));
- Canonical text/hash/version/scanner mechanisms required by Cluster Feature 02.

### Hard owner-interface dependencies

- Organization Hiring must expose the dedicated compliance-input snapshot and scoped/cursor rescan-enumeration source contracts before CL-06 Feature 02; Organization Module Feature 03 provides them. The snapshot returns exact source revision/token and required authoritative Job facts; enumeration accepts rule/jurisdiction/effective scope and cursor and returns eligible Job IDs/tokens with pagination.
- Role / Authority must be able to authorize Job Compliance action vocabulary.
- Audit must expose SH-029 `appendAuditEvent` (Confirmed).
- Holds must expose SH-012 `requestComplianceHold` (Confirmed) if the implemented review policy requests holds.
- Notification must expose SH-041 `requestNotification` (Confirmed) for any enabled reviewer/admin notifications.
- Ops must expose the approved safe failure/queue telemetry path.

### Dependencies that may initially be fixtures

- Search may be represented by a versioned contract fixture until Cluster Feature 03 integration is built.
- Notification/Hold/Ops may be fixture-backed for core domain tests if the public contract is frozen and no local replacement is created.
- The shared scanner runtime may initially use a deterministic test implementation; production scanner libraries must remain behind the canonical mechanism.

### Architecture blockers

Before production implementation of the corresponding behavior:

- **U-CL06-05:** approve effective decision/mirror/hold precedence and warning/failed mapping.
- **U-CL06-06:** binding source/rule-set evidence invariant; exact persistence schema and retention details require a later approved database pass, not a new decision about whether proof is required.
- **U-CL06-07:** approve `CompensationPeriod` structural ownership and `EmploymentType.contract` semantics.
- finding-field duplicate semantics must be settled before migrations/code depend on both old/new variants.
- if legal-grade review history requires more than AuditEvent + outbox, approve its schema before review feature completion.

No production publication exit gate may be marked PASS while these remain unresolved.

### Public concurrency prerequisite — CL-06-R020

Public mutation contracts use an owner-issued opaque `expectedConcurrencyToken`. The owner returns the token, atomically compares it through SH-052 `withOptimisticConcurrency` (Confirmed), and rejects stale tokens. Consumers do not assume a universal integer `version` or `updatedAt` field. JobApplication, mutable Job Compliance finding/review, JobInterview and any parent-versus-child token backing remain unresolved where no representation is approved; no version column is ordered here.

# Phase 1 — Rule and Evaluation Proof Foundation

## 01 Versioned Job Compliance Rule Catalog

### Objective

Implement the authoritative `JobComplianceRule` repository, rule lifecycle, runtime validation, and rule applicability service without embedding employment policy into shared infrastructure or neighboring Modules.

### Observable Result

Authorized rule administrators can create draft Job Compliance rules, inspect them, activate a valid immutable version, and retire/disable future applicability. Evaluation code can deterministically resolve the effective rule versions for a supplied normalized context.

### Cluster Build-Plan Link

Supports **CL-06 Feature 02 — Job Compliance Rule, Check, Finding, and Disclosure Evaluation**.

### Dependencies

- current `JobComplianceRule` Prisma model and enums;
- SH-001 `resolveAuthenticatedActor` (Confirmed);
- SH-002 `authorizeResourceAction` (Confirmed);
- SH-080 `manageVersionedRules` (Confirmed);
- SH-044 `executeIdempotentCommand` (Confirmed);
- concurrency primitive;
- SH-029 `appendAuditEvent` (Confirmed);
- SH-046 `publishDomainEvent` (Confirmed);
- normalized jurisdiction DTO contract;
- U-CL06-07 must be resolved before rule semantics depend on `CompensationPeriod` or `EmploymentType.contract` meaning.

### In Scope

- Zod/runtime schemas for rule create/update-draft/activate/retire/disable commands;
- repository methods for Job Compliance-owned rule records only;
- unique `(key,version)` handling;
- draft editing policy;
- activation validation;
- immutable-active-version policy;
- effective-date and jurisdiction/context rule resolution;
- deterministic ordering of resolved rules;
- admin query/list/detail surface contracts;
- audit/event proof for privileged transitions;
- tests for overlap/conflict behavior required by approved policy.

### Out of Scope

- Job evaluation/check creation;
- scanner execution;
- compensation disclosure;
- Job lifecycle mutation;
- a generic cross-platform rule engine;
- external legal-rule provider/feed;
- Search indexing;
- candidate/background screening.

### Module-Owned Data

- `JobComplianceRule`;
- `JobComplianceRuleType`;
- `JobComplianceRuleStatus`;
- rule lifecycle domain events.

### Public Interfaces

Introduce/complete:

- `createJobComplianceRuleDraft` if the product/admin surface needs explicit creation;
- `updateJobComplianceRuleDraft`;
- `publishJobComplianceRuleVersion`;
- `retireJobComplianceRuleVersion`;
- `disableJobComplianceRuleVersion`;
- `getJobComplianceRule`;
- `listJobComplianceRules`;
- internal/public policy query `resolveApplicableJobComplianceRules` through Module application service.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` (Confirmed) — Identity & Access; at every human admin entry; local policy is the attempted rule action; **do not create** `jobComplianceAuth`.
- SH-002 `authorizeResourceAction` (Confirmed) — Role / Authority; authorize rule create/activate/retire/disable; local action names stay Job Compliance-owned; **do not create** local admin-role checks.
- SH-080 `manageVersionedRules` (Confirmed) — shared versioning mechanism; use for immutable/effective-version mechanics; employment rule semantics stay local; **do not create** generic `ruleEngine.ts`.
- SH-044 `executeIdempotentCommand` (Confirmed) — platform; protect activation/retire/disable replay; local semantic key uses rule ID/version/action; **do not create** local idempotency storage.
- SH-052 `withOptimisticConcurrency` (Confirmed) / SH-051 `acquireAggregateLock` (Confirmed) — platform; protect rule transitions and prohibited overlap; local conflict semantics stay local; **do not create** in-memory locks.
- SH-029 `appendAuditEvent` (Confirmed) — Audit; privileged transition proof; rule meaning remains Job Compliance truth; **do not create** local audit table.
- SH-046 `publishDomainEvent` (Confirmed) — event infrastructure; publish rule transition facts; Job Compliance owns event names/payloads; **do not fire-and-forget** directly.

### Domain Logic

- Draft rule versions may be edited until activation.
- Active versions are immutable in policy meaning.
- Material change requires a new `(key,version)`.
- Effective applicability is based on approved jurisdiction/context/effective-date policy.
- Retired/disabled versions remain queryable for historical proof but are excluded from future effective resolution.
- Invalid rule JSON/pattern configuration cannot activate.
- Multiple active versions may not create an ambiguous effective result for the same rule key/scope under the approved overlap policy.
- Rule resolution returns explicit ordered rule references; no consumer parses the database table directly.

### Authorization / Compliance

- Rule mutation requires privileged Role / Authority decision.
- Read access for internal evaluation may use system scope; admin rule detail remains restricted.
- Every activation/retire/disable action is audited.
- No claim is made that a configured rule is legal advice; this is platform policy requiring legal review where applicable.

### Database / Transaction Behavior

- Preserve unique `(key,version)`.
- Activation/retirement/disable uses one transaction with optimistic concurrency/lock on the rule key/scope.
- Audit/outbox behavior must follow the root transaction pattern; no successful response before required durable effects are committed.
- Add indexes/constraints only if required by approved rule-resolution policy and migration review.
- No in-place update of active rule semantics.

### Events / Jobs

Emit:

- `job_compliance.rule_activated`;
- `job_compliance.rule_retired`;
- `job_compliance.rule_disabled`.

No rescan worker is implemented yet; event consumption is Feature 06.

### Provider Integration

None. Rule records are Workin Ants truth. Do not fetch or sync an external legal-rule feed.

### UI / Admin Surface

A restricted admin rule list/detail/editor may be implemented if CL-06 admin tooling exists. UI must clearly distinguish draft, active, retired, disabled, jurisdiction scope, version, and effective dates. It must not expose arbitrary raw JSON editing without validation/guardrails.

### Failure Behavior

- invalid rule config → validation/domain error;
- duplicate key/version → deterministic conflict;
- stale update → conflict;
- unauthorized → no write;
- ambiguous effective scope → activation denied;
- Audit/outbox failure according to root policy prevents falsely reporting committed transition.

### Tests

- rule validation unit tests;
- status transition matrix;
- unique key/version integration test;
- effective-date/jurisdiction resolution tests;
- ambiguous-overlap tests;
- authorization tests;
- idempotent activation replay;
- concurrent activation/retire tests;
- audit/outbox contract tests.

### Documentation Updates

- update Module architecture if U-CL06-07 changes enum ownership/meaning;
- record final rule-overlap semantics if not already binding;
- progress tracker feature status and any migration notes.

### Acceptance Criteria

- only authorized actors mutate rule lifecycle;
- active rule meaning cannot be edited in place;
- deterministic effective-rule query exists;
- historical retired/disabled versions remain readable;
- no generic platform rule engine is created inside this Module;
- privileged transitions have audit/event proof.

### Exit Gate

PASS only if rule lifecycle, applicability, authorization, idempotency, concurrency, audit, outbox, migration, typecheck/lint/unit/integration checks pass and no unresolved U-CL06-07 semantic was silently encoded.

---

## 02 Canonical Job Input and Historical Evaluation Proof

### Objective

Establish the owner-to-owner Job input contract, canonical evaluation input, hashing, source-version staleness guard, and the architecture-approved immutable historical proof required to reproduce a Job Compliance evaluation.

### Observable Result

Given one authoritative Organization Hiring Job source version and one resolved rule set, Job Compliance can construct a deterministic evaluation input and persist/reference enough immutable proof to later identify exactly which source state, jurisdiction, canonicalization version, scanner version, and rules were evaluated—even when there are zero findings.

### Cluster Build-Plan Link

Supports **CL-06 Feature 02** and resolves the reproducibility portion of its exit gate.

### Dependencies

- Feature 01;
- Organization Hiring public Job facts/input contract;
- SH-003 `queryOwnerFacts` (Proposed ruling) pattern;
- SH-120 `normalizeJurisdictionContext` (Unresolved) remains Unresolved: approved owner/interface required for production; deterministic fixtures may supply explicit normalized jurisdiction context below that gate, with no local replacement or raw-string inference;
- SH-077 `buildCanonicalTextSnapshot` (Confirmed);
- SH-072 `hashCanonicalPayload` (Confirmed);
- the binding U-CL06-06 invariant requires a separately approved persistence design before migration/code for its record begins; this reconciliation does not select schema;
- U-CL06-07 resolved for any source fields whose semantic meaning affects canonical input.

### In Scope

- versioned `JobComplianceInputDTO` contract;
- source-version comparison/staleness semantics;
- exact Job Compliance field allowlist for canonical input;
- deterministic canonicalization version identifier;
- canonical snapshot/hash call;
- normalized jurisdiction evidence attachment;
- deterministic applied-rule ordering;
- rule-set fingerprint;
- architecture-approved immutable proof persistence;
- privacy/retention classification of any stored source snapshot/text;
- test vectors proving stable canonicalization/hashing.

### Out of Scope

- final finding classification;
- final DecisionResult precedence;
- Search indexing;
- direct Job reads/writes through Prisma;
- a local text-normalization or crypto utility;
- guessing the U-CL06-06 schema before architecture approves it.

### Module-Owned Data

- architecture-approved historical evaluation proof attached to `JobComplianceCheck` or equivalent;
- no new ownership of `Job`.

### Public Interfaces

- pair/version Organization Hiring's compliance-input snapshot DTO with this consumer; do not freeze a proposed cross-platform SH API;
- consume scoped/cursor rescan enumeration before rule-change worker execution; never enumerate Organization repositories directly;
- internal `buildJobComplianceCanonicalInput`;
- internal `buildJobComplianceEvaluationProof`;
- staleness result used by `request/SH-021 evaluateJobCompliance (Confirmed)`.

### Shared Operations Used

- SH-003 `queryOwnerFacts` (Proposed ruling) — Organization Hiring implementation; fetch minimal authoritative Job/Organization facts; **no cross-domain Prisma repository**.
- SH-120 `normalizeJurisdictionContext` (Unresolved) — shared capability; produce normalized context/evidence; Job Compliance owns rule applicability after normalization; **no local jurisdiction platform service**.
- SH-077 `buildCanonicalTextSnapshot` (Confirmed) — shared primitive; normalize stable ordered text/fields; Job Compliance owns field inclusion; **no `jobTextBuilder` mechanics**.
- SH-072 `hashCanonicalPayload` (Confirmed) — shared crypto primitive; produce source/rule-set fingerprints; Job Compliance owns what each hash proves; **no `sha256.ts`**.
- SH-052 `withOptimisticConcurrency` (Confirmed) — staleness/owner-issued opaque expectedConcurrencyToken for the source revision where owner contract supports it; **no ad-hoc version check scattered in routes**.

### Domain Logic

Canonical input must include every Job surface required by approved policy, not description only. Missing authoritative compensation/benefit field mappings remain unresolved; disclosure evidence is not an originating business source. The input contract must be narrow and explicit. At minimum, current evidence points to title, description, employment type, taxonomy IDs/context, location/city/state/country, remote status, offered compensation range/currency/period, and approved compensation/disclosure text fields where applicable.

A source version is opaque owner truth. Job Compliance stores/returns it but does not define Job version semantics.

If the current Job source version differs from the request’s owner-issued opaque expectedConcurrencyToken, evaluation is stale and must not produce an applicable allowed decision.

Historical proof must cover zero-finding cases. A list of findings is not an applied-rule ledger.

### Authorization / Compliance

The worker/system may read the owner DTO only through the approved public interface. Human-triggered requests are authorized earlier. Stored snapshot/proof is privacy-classified and minimized.

### Database / Transaction Behavior

- in a later approved database pass, implement the persistence design satisfying binding U-CL06-06: exact immutable input snapshot or reconstructible immutable source reference plus hash; complete applied rule identities/versions including zero-finding checks; scanner version, evaluation time and material normalized jurisdiction evidence;
- proof rows are immutable once the check is committed;
- enforce one proof set per check/evaluation identity as approved;
- deterministic applied-rule uniqueness prevents duplicate rule proof;
- no mutable current `Job` content is treated as historical proof after the source changes.

### Events / Jobs

No new worker beyond fixtures/test harness yet. Evaluation events in later features include proof references/hashes, not copied snapshot contents.

### Provider Integration

None.

### UI / Admin Surface

No new UI required. Admin report may later show source/rule version references, never the entire canonical snapshot unless authorization/privacy policy permits it.

### Failure Behavior

- owner facts unavailable → explicit dependency unavailable;
- source version mismatch → `stale_source`;
- jurisdiction cannot be normalized → review/unavailable according to approved policy;
- historical proof architecture absent → `architecture_blocked`, never fallback to hash-only silent pass;
- canonicalization/hash failure → technical failure.

### Tests

- owner DTO contract tests;
- canonical field inclusion tests;
- canonicalization test vectors;
- hash stability tests;
- source-version stale tests;
- zero-finding applied-rule proof test;
- rule-set ordering/fingerprint test;
- privacy/redaction tests for proof payload;
- migration/integration tests for approved proof schema.

### Documentation Updates

- update Module architecture with exact U-CL06-06 schema once approved;
- document canonicalization version and included fields;
- record U-CL06-07 resolution if it affects source DTO;
- progress tracker.

### Acceptance Criteria

- one Job source version produces deterministic canonical input/hash;
- every applied rule version is provable even with zero findings;
- stale source version cannot be applied as current;
- no direct Job repository access exists;
- no custom canonicalization/hash implementation exists in the Module.

### Exit Gate

PASS only if binding U-CL06-06 has an approved implemented persistence design, relevant U-CL06-07 policy is resolved, and jurisdiction-aware production has an approved SH-120 `normalizeJurisdictionContext` (Unresolved) owner/interface; historical proof is reproducible, canonicalization/hash test vectors pass, stale source fails closed, and all contract/migration/typecheck/lint/tests pass.

---

## 03 Compensation Disclosure Evaluation

### Objective

Implement Job Compliance-owned pay-transparency and compensation-disclosure evaluation while preserving Organization Hiring as the owner of offered compensation.

### Observable Result

For an authoritative Job source version and applicable rule set, Job Compliance produces a deterministic `JobCompensationDisclosure` result and structured compensation-related findings with jurisdiction/rule provenance.

### Cluster Build-Plan Link

Supports **CL-06 Feature 02**.

### Dependencies

- Features 01–02;
- approved U-CL06-05 disclosure-to-decision semantics;
- U-CL06-07 compensation-period owner/meaning;
- current `JobCompensationDisclosure` schema;
- shared canonical input/proof.

### In Scope

- `validateJobCompensationDisclosure` domain policy;
- mapping of applicable pay-transparency/benefits rules to disclosure requirements;
- range validation;
- period/currency presence/compatibility checks under approved policy;
- benefits/bonus/commission/equity/tips disclosure checks represented by approved rules;
- remote/location rule treatment;
- one current disclosure proof update tied to evaluation source version;
- salary/benefits/commission-related findings;
- rule/jurisdiction evidence.

### Out of Scope

- editing Job compensation;
- inventing a nationwide legal requirement beyond configured platform/rule policy;
- tax calculation;
- compensation benchmarking;
- candidate offer compensation;
- final Job publication transition.

### Module-Owned Data

- `JobCompensationDisclosure`;
- compensation-related `JobComplianceFinding` entries;
- `JobCompensationDisclosureStatus`.

### Public Interfaces

Internal application/domain interface:

- `validateJobCompensationDisclosure`.

Its result is consumed by SH-021 `evaluateJobCompliance` (Confirmed); no separate cross-Module write API is required.

### Shared Operations Used

- SH-080 `manageVersionedRules` (Confirmed) — applicable pay/benefit rule versions; policy remains Job Compliance-owned; **no hardcoded state-law helpers**.
- SH-072 `hashCanonicalPayload` (Confirmed) — disclosure/source proof where approved; **no local compensation hash helper**.
- SH-015 `returnDecisionResult` (Proposed ruling) later consumes disclosure outcome but does not own disclosure policy.

### Domain Logic

- Business compensation values come from Organization Hiring’s source DTO.
- Disclosure evaluation may snapshot those values for proof but never becomes the editable source.
- Missing/invalid compensation and required benefits/commission fields create structured findings, not inline-only validation strings.
- Each finding includes approved rule key/version, source field, jurisdiction, scanner/policy provenance as applicable.
- `provided_with_warning` must preserve warning evidence.
- exemption requires explicit applicable-rule evidence; do not use an ad-hoc boolean.
- remote roles use approved jurisdiction policy; no guessed nationwide rule.

### Authorization / Compliance

No separate authorization inside pure domain policy. The parent evaluation command is already authorized/system-scoped. Admin edits of disclosure are not allowed as a bypass; corrections occur by editing Job source through Organization Hiring or by authorized review/override where policy permits.

### Database / Transaction Behavior

- preserve one disclosure row per Job via unique `jobId`;
- update disclosure only inside the same evaluation transaction/source-version guard as the check;
- older evaluation cannot overwrite newer source-version disclosure;
- current mutable disclosure is not sufficient historical proof; Feature 02 approved proof must preserve evaluation identity.

### Events / Jobs

No separate event is required for each disclosure field. The evaluation event carries disclosure status/evidence reference. A materially changed disclosure contributing to decision change is reflected in `job_compliance.decision_changed` later.

### Provider Integration

None.

### UI / Admin Surface

No Module-owned organization editor. Compliance report DTO must expose human-safe missing/invalid/warning reasons and remediation field identifiers so Organization Hiring can render corrective guidance.

### Failure Behavior

- missing source data → structured denial/warning/review according to approved rule, not crash;
- unresolved rule/jurisdiction → review/unavailable;
- U-CL06-07 semantic not resolved → architecture blocked;
- stale source → no write/applicable result;
- persistence conflict → deterministic retry/conflict path.

### Tests

- compensation min/max valid/invalid cases;
- missing range;
- currency/period cases under approved policy;
- benefits/commission missing cases;
- remote/location-based rules;
- exempt/not-required cases;
- provided-with-warning case;
- jurisdiction/rule provenance;
- stale overwrite prevention;
- one-row-per-Job integration test;
- proof linkage/history test.

### Documentation Updates

- final disclosure mapping under U-CL06-05;
- `CompensationPeriod` owner/meaning under U-CL06-07;
- progress tracker and migration notes.

### Acceptance Criteria

- offered compensation remains Organization Hiring truth;
- disclosure proof is reproducible and source-version tied;
- required failures create structured findings;
- no hardcoded unversioned jurisdiction rule exists;
- older evaluations cannot overwrite current disclosure.

### Exit Gate

PASS only if U-CL06-05/07 disclosure semantics are approved, all compensation/disclosure cases are covered by deterministic tests, source ownership is preserved, and typecheck/lint/unit/integration checks pass.

# Phase 2 — Findings, Decision, Review, and Public Contracts

## 04 Scanner Match Classification and Effective Job Compliance Decision

### Objective

Implement the Module-owned interpretation layer that converts canonical scanner matches and compensation-disclosure evidence into durable findings and a stable Job Compliance `DecisionResult`.

### Observable Result

The same authoritative source version + rule-set proof + scanner version produces the same structured findings and effective Job Compliance decision, including pass, warning, block, review, and technical unavailable behavior.

### Cluster Build-Plan Link

Supports **CL-06 Feature 02** and the decision portion of **CL-06 Feature 03**.

### Dependencies

- Features 01–03;
- SH-081 `runPatternScanner` (Proposed ruling) canonical mechanism;
- Job Compliance's owner-specific `allowed | denied | warning | review_required | unavailable` contract; proposed SH-015 `returnDecisionResult` (Proposed ruling) requires separate approval before shared API/schema commitment;
- U-CL06-05 approved;
- finding-field duplicate semantics resolved before persistence code depends on duplicate fields.

### In Scope

- `job-scanner-policy` request shaping into shared scanner;
- raw match → `JobComplianceFindingType` mapping;
- severity policy;
- source field and offsets;
- matched-text hash + minimized preview policy;
- neutral suggested replacement mapping;
- review-required conditions;
- `deriveJobComplianceDecision`;
- stable reason-code namespace;
- persistence of check/findings/proof in one evaluation transaction;
- zero-finding pass behavior;
- scanner unknown/error classification.

### Out of Scope

- generic scanner/tokenizer implementation;
- final Job lifecycle mutation;
- moderation findings;
- candidate screening;
- external provider integration;
- human review command (Feature 05).

### Module-Owned Data

- `JobComplianceCheck`;
- `JobComplianceFinding`;
- finding/check enums;
- effective decision policy;
- evaluation domain events built later by worker.

### Public Interfaces

- SH-021 `evaluateJobCompliance` (Confirmed) core application service;
- `DecisionResult` reason-code contract used by later query/command wrappers.

### Shared Operations Used

- SH-081 `runPatternScanner` (Proposed ruling) — shared scanner; invoke after canonical input/rules; Job Compliance owns interpretation; **do not create per-rule scanner runtimes**.
- SH-072 `hashCanonicalPayload` (Confirmed) — matched-text hash/provenance when needed; **no local hash helper**.
- SH-015 `returnDecisionResult` (Proposed ruling) — proposed shared shape only; use the Job Compliance-owned publication envelope pending separate SH approval; Job Compliance owns reason codes/precedence; **no generic readiness engine**.
- SH-052 `withOptimisticConcurrency` (Confirmed) / aggregate lock — protect evaluation commit against stale source/proof conflicts.

### Domain Logic

- Scanner returns raw matches only.
- Classification maps rule/match/context into type, severity, source field, safe preview/hash, suggested remediation.
- `blockingByDefault` is an input to Job Compliance policy, not a universal automatic block if `requiresAdminReview` or other approved semantics say otherwise.
- `requiresAdminReview` and uncertain/unsupported scanner conditions route to `needs_review` / `review_required`.
- Technical scanner error maps to `failed` check and `unavailable` decision after retry policy exhaustion; it does not create a legal finding unless a domain rule explicitly represents missing evaluation.
- Decision follows approved PR-JC-01/U-CL06-05 mapping.
- External `ComplianceHold` is not folded into check status under PR-JC-01; final publication composition occurs in Organization Hiring.

### Authorization / Compliance

Core evaluator is invoked by trusted application/worker after authorization. Decision must remain policy-only; no actor role affects whether a phrase violates a posting rule.

### Database / Transaction Behavior

One evaluation transaction writes:

- historical proof;
- check;
- findings;
- disclosure update from Feature 03;
- outbox records where evaluation is being committed through the worker/application boundary.

Do not create partial check without its required proof unless the terminal `failed` semantics explicitly allow a minimal failure record.

### Events / Jobs

Event builders are introduced but worker emission occurs in Feature 06. Unit tests validate minimized payload composition.

### Provider Integration

None. `compromise`/`natural` are behind shared scanner runtime.

### UI / Admin Surface

No new UI required. Result/report contracts must support safe organization remediation without exposing sensitive scanner internals.

### Failure Behavior

- scanner unsupported/uncertain → review/unavailable according to policy;
- scanner technical exception → retryable technical failure, eventually failed/unavailable;
- invalid rule config detected at runtime → unavailable + Ops, never pass;
- stale source/rule proof → conflict/stale and re-evaluate;
- persistence conflict → safe retry if same semantic request, otherwise conflict.

### Tests

- every current `JobComplianceFindingType` mapping class;
- severity policy;
- all-text-surface coverage;
- offsets/source fields;
- preview redaction/hash;
- pass/warning/block/review decision precedence;
- disclosure + scanner combination cases;
- scanner unknown/error;
- identical input reproducibility;
- zero-finding applied-rule proof;
- no external hold in local decision under approved ruling.

### Documentation Updates

- freeze reason-code namespace and U-CL06-05 mapping;
- document duplicate finding-field cleanup;
- progress tracker.

### Acceptance Criteria

- deterministic findings and decision for identical proof inputs;
- raw scanner output never crosses public boundary unclassified;
- technical failure cannot return allowed/denied;
- warnings/review remain first-class;
- matched text is minimized;
- no candidate/moderation logic is present.

### Exit Gate

PASS only if U-CL06-05 is approved, decision matrix and all current finding classes pass, zero-finding proof exists, scanner failure is non-permissive, and typecheck/lint/unit/integration tests pass.

---

## 05 Human Review, Finding Override, Reports, and Decision Queries

### Objective

Implement the authorized human-review/override lifecycle and stable public Job Compliance read contracts without transferring Job lifecycle or generic audit ownership.

### Observable Result

An authorized reviewer can resolve a `needs_review` check or override a finding with durable reason/audit proof; Organization Hiring and authorized users can query the current decision/report through stable contracts rather than direct Prisma reads.

### Cluster Build-Plan Link

Completes the human/public-interface portion of **CL-06 Feature 02**.

### Dependencies

- Feature 04;
- Role / Authority;
- SH-029 `appendAuditEvent` (Confirmed);
- SH-044 `executeIdempotentCommand` (Confirmed);
- concurrency primitive;
- SH-046 `publishDomainEvent` (Confirmed);
- optional Notification contract;
- decision whether AuditEvent + outbox is sufficient review history.

### In Scope

- `reviewJobComplianceCheck`;
- `overrideJobComplianceFinding`;
- current-decision query;
- compliance-report query;
- applicable-requirements query;
- actor/data shaping;
- stale/superseded review rejection;
- audit/event proof;
- restricted admin review UI/actions if enabled;
- safe organization-facing report shape.

### Out of Scope

- Job status update;
- general Organization dashboard ownership;
- generic admin review platform;
- Notification delivery mechanics;
- candidate/background adverse action;
- local AuditEvent schema.

### Module-Owned Data

- mutable review fields on `JobComplianceCheck`;
- override/resolution fields on `JobComplianceFinding`;
- current effective decision computation;
- review-resolved/decision-changed event meaning.

### Public Interfaces

Introduce/complete:

- `reviewJobComplianceCheck`;
- `overrideJobComplianceFinding`;
- `getJobPublicationComplianceDecision`;
- `getJobComplianceReport`;
- `getApplicableJobComplianceRequirements`.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` (Confirmed) — protected review/report entry; **no local auth**.
- SH-002 `authorizeResourceAction` (Confirmed) — reviewer/admin/org report permissions; **no `canReviewJob` helper**.
- SH-044 `executeIdempotentCommand` (Confirmed) — review/override replay; **no local idempotency**.
- SH-052 `withOptimisticConcurrency` (Confirmed) — reject double/stale review; **no last-write-wins**.
- SH-029 `appendAuditEvent` (Confirmed) — privileged reasoned action proof; **no local audit ledger**.
- SH-046 `publishDomainEvent` (Confirmed) — reliable review/decision facts; **no fire-and-forget events**.
- SH-041 `requestNotification` (Confirmed) — optional review/admin intent only; **no direct provider sender**.
- SH-015 `returnDecisionResult` (Proposed ruling) — proposed shared envelope only; the local publication decision uses `allowed | denied | warning | review_required | unavailable`, with Job Compliance-owned reasons and next-action metadata.

### Domain Logic

- only `needs_review` can be resolved by review unless an explicit re-review command is later approved;
- reviewer may choose only the approved final outcomes;
- finding override preserves original rule/scanner/match provenance;
- reason is mandatory for override;
- old/superseded source version cannot be made current by a late reviewer;
- decision query returns staleness/source-version evidence;
- report query is privacy-shaped by actor scope;
- organization-facing reports expose remediation and safe previews, not private admin notes or full internal rule JSON.

### Authorization / Compliance

- review/override/rule evidence access uses Role / Authority;
- organization members may only read reports for their Organization Jobs under approved actions;
- admin/support broad access is not assumed;
- if root policy later requires step-up for legal override, consume canonical step-up.

### Database / Transaction Behavior

- review/override uses owner-issued opaque expectedConcurrencyToken for the review aggregate; child-versus-parent backing remains unresolved;
- local writes + outbox + required audit behavior are transactionally coordinated according to root patterns;
- double review is deterministic conflict/idempotent replay as appropriate;
- no Job row is written.

### Events / Jobs

Emit:

- `job_compliance.review_resolved`;
- `job_compliance.decision_changed` when effective decision differs.

Notification request may be enqueued after commit for reviewer/admin or delegated organization-facing flow as defined.

### Provider Integration

None.

### UI / Admin Surface

Restricted Job Compliance admin surface may include:

- needs-review queue/detail;
- findings and safe evidence;
- review outcome control;
- override reason input;
- rule/proof references;
- audit/event references.

Organization Job detail UI remains Organization Hiring-owned and consumes the report contract.

### Failure Behavior

- unauthorized → no evidence leak/write;
- stale/superseded check → conflict with re-evaluation guidance;
- already resolved → idempotent replay if same request, otherwise conflict;
- audit/outbox failure → do not report false review completion;
- report dependency unavailable → explicit unavailable, not direct DB fallback.

### Tests

- reviewer authorization matrix;
- cross-organization report denial;
- needs_review transition matrix;
- override preserves original finding;
- mandatory reason;
- double/concurrent review;
- stale source review denial;
- audit/outbox proof;
- decision/report contract snapshots;
- private-note/matched-text redaction.

### Documentation Updates

- if dedicated review-history schema is approved, update architecture first;
- freeze report DTO/version/reason codes;
- progress tracker.

### Acceptance Criteria

- review/override cannot bypass Role / Authority;
- every privileged outcome has durable local proof + generic audit;
- direct Job writes do not exist;
- reports are privacy-shaped;
- current decision has source/rule evidence and staleness semantics.

### Exit Gate

PASS only if reviewer/admin actions are authorized/audited, stale/double review is safe, report/decision contracts are versioned/tested, no Job lifecycle write occurs, and all checks pass.

# Phase 3 — Durable Evaluation, Events, and Publication Handoff

## 06 Idempotent Evaluation Command, Worker, Rescan, and Domain Events

### Objective

Expose the production evaluation request command and execute Job Compliance evaluation/rescan through the canonical durable queue, retry, idempotency, outbox, and observability mechanisms.

### Observable Result

An authorized publication/material-edit/admin/rule-rescan request creates exactly one effective Job Compliance evaluation for a semantic source/rule identity, survives worker retry/crash, records terminal failure visibly, and emits minimized domain events after commit.

### Cluster Build-Plan Link

Completes async execution in **CL-06 Feature 02** and supplies events consumed by **CL-06 Feature 03**.

### Dependencies

- Features 01–05;
- canonical idempotency/queue/retry/outbox/inbox;
- Organization Hiring source DTO;
- Ops telemetry;
- U-CL06-05/07 policy approved and binding U-CL06-06 proof backed by approved implemented persistence before production publication-triggered evaluation.

### In Scope

- `requestJobComplianceEvaluation` public command;
- evaluation job payload/version;
- semantic idempotency key;
- evaluation worker;
- technical retry classification;
- terminal `failed`/unavailable behavior;
- outbox events;
- rule-change affected-Job rescan/backfill worker;
- cursor/checkpoint/dry-run support where required;
- dead-letter/manual recovery surface contract;
- safe operational telemetry.

### Out of Scope

- generic queue/retry framework;
- Organization Hiring Job lifecycle update;
- Search refresh;
- external legal-rule feed;
- Notification delivery implementation.

### Module-Owned Data

- Job Compliance evaluation records from prior features;
- event meaning;
- no `QueueJob` ownership.

### Public Interfaces

- `requestJobComplianceEvaluation`;
- worker handler contract;
- rule-change rescan command/worker internal interface;
- optional admin retry command that reuses canonical job/idempotency semantics.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` (Confirmed) / SH-002 `authorizeResourceAction` (Confirmed) — request entry; **no local auth/role logic**.
- SH-044 `executeIdempotentCommand` (Confirmed) — claim semantic evaluation request; **no local idempotency table**.
- SH-047 `enqueueReliableJob` (Confirmed) — persist work; **no local queue client**.
- SH-048 `executeRetryWithBackoff` (Confirmed) — retry transient failures; **no custom retry loop**.
- SH-045 `deduplicateDomainEvent` (Confirmed) — for rule-change/source events consumed by workers; **no local processed-event table**.
- SH-046 `publishDomainEvent` (Confirmed) — evaluation/rule events; **no direct bus publish**.
- SH-051 `acquireAggregateLock` (Confirmed) — avoid concurrent duplicate evaluation commit; **no in-memory mutex**.
- Ops logging/failure interface — operational visibility only; **no local SystemEvent model**.

### Domain Logic

Evaluation request semantic identity must include Job ID, source version, and the architecture-approved rule-set/canonicalization identity where known. If two requests are equivalent, the second returns the first receipt/result.

Worker flow:

```text
claim job
→ obtain authoritative Job source DTO
→ reject stale owner-issued opaque expectedConcurrencyToken
→ normalize jurisdiction
→ resolve rule set
→ build canonical input/proof
→ run scanner + disclosure policy
→ classify findings + decision
→ atomically persist local truth + outbox
→ complete queue job
```

Retry only technical/dependency failures. Domain denial/block/review is a successful evaluation outcome and is not retried.

Rule-change rescan consumes Organization Hiring's scoped/cursor enumeration, then its exact compliance-input snapshot per eligible Job/source token. It never directly queries Organization repositories or overwrites historical checks; it creates new evaluations for current source revisions.

### Authorization / Compliance

Human request is authorized. Rule-change/system backfill uses scoped system actor. Admin retry cannot alter the original decision directly; it requests a new/replayed evaluation.

### Database / Transaction Behavior

- idempotency claim and result use canonical store;
- evaluation source transaction writes check/findings/disclosure/historical proof/outbox atomically;
- worker crash before commit may replay safely;
- worker crash after commit returns/reconciles existing result;
- aggregate lock/source-version guard prevents older evaluation from superseding newer state.

### Events / Jobs

Emit minimized:

- `job_compliance.evaluated`;
- `job_compliance.decision_changed`;
- `job_compliance.review_required`;
- `job_compliance.evaluation_failed`;
- rule lifecycle events from Feature 01.

Rescan worker consumes rule transition facts/explicit commands using inbox dedupe.

### Provider Integration

None. Shared scanner runtime may use configured libraries internally.

### UI / Admin Surface

Operational/admin surface may show evaluation receipt, status, terminal safe failure category, retry action, and rescan/backfill progress. It must identify source records as truth and not edit outcomes directly.

### Failure Behavior

- transient Organization/scanner/queue dependency → bounded retry;
- stale source → terminal stale outcome requiring new request;
- unresolved jurisdiction/rules → review/unavailable per policy, not infinite retry;
- retry exhaustion → durable failed/unavailable Job Compliance evidence + dead-letter/Ops reference;
- duplicate worker delivery → no duplicate source writes/events.

### Tests

- command idempotency replay;
- duplicate queue delivery;
- worker crash before/after commit;
- transient retry/backoff;
- retry exhaustion;
- stale Job edit during evaluation;
- concurrent same-Job evaluation;
- outbox atomicity;
- event payload minimization/versioning;
- rule-change rescan checkpoint/replay;
- no historical overwrite.

### Documentation Updates

- document semantic idempotency key and event schemas;
- update progress tracker;
- architecture update first if worker introduces a new business state or proof record.

### Acceptance Criteria

- no duplicate effective evaluation for same semantic identity;
- source truth survives worker crash/replay;
- technical failures are visible and non-permissive;
- events are transactional/minimized;
- rescan produces new proof rather than rewriting history;
- no custom queue/retry/idempotency framework exists.

### Exit Gate

PASS only if idempotency, crash replay, retry/dead-letter, stale-source, outbox/inbox, rescan, telemetry-redaction, typecheck/lint/integration/worker tests all pass.

---

## 07 Organization Hiring Publication Decision Handoff

### Objective

Prove the stable owner-to-owner boundary whereby Organization Hiring requests/consumes Job Compliance, applies the authoritative decision to Job lifecycle, and owns the downstream Search/Notification/public-readiness handoff.

### Observable Result

A Job publication request can move from Organization Hiring → Job Compliance evaluation → Organization Hiring decision application without Job Compliance writing Job state or Search state. Stale decisions and unavailable compliance remain non-public.

### Cluster Build-Plan Link

Directly supports **CL-06 Feature 03 — Controlled Job Publication and Search Handoff**.

### Dependencies

- Features 01–06;
- Organization Hiring `requestJobPublication` and owner command equivalent to `applyJobComplianceDecision`;
- approved U-CL06-05 mapping;
- Search contract/fixture;
- Hold/Trust interfaces owned externally;
- Notification contract.

### In Scope

- versioned Job Compliance DecisionResult contract consumed by Organization Hiring;
- source-version check at application boundary;
- `job_compliance.decision_changed` consumer contract proof;
- Organization Hiring fixture/real contract verifying no direct Job write from this Module;
- material-edit invalidation/re-evaluation path;
- decision revocation/review/unavailable path;
- Search/Notification responsibility assertions in contract tests;
- hold-request integration only where Job Compliance-owned review policy requires it.

### Out of Scope

- implementing Organization Hiring internals inside Job Compliance;
- direct Search refresh;
- Trust readiness implementation;
- general public-readiness engine;
- organization verification U-CL06-01/02.

### Module-Owned Data

No new Job Compliance schema required unless a previously approved source/decision reference is needed. This feature primarily freezes contracts and integration behavior.

### Public Interfaces

Exercise/freeze:

- `requestJobComplianceEvaluation`;
- `getJobPublicationComplianceDecision`;
- `job_compliance.decision_changed` event;
- Organization Hiring owner command/query fixtures.

### Shared Operations Used

- SH-046 `publishDomainEvent` (Confirmed) / SH-045 `deduplicateDomainEvent` (Confirmed) — owner-to-owner decision change delivery; **no direct repository coupling**.
- SH-015 `returnDecisionResult` (Proposed ruling) — proposed shared envelope only; Organization consumes Job Compliance's owner contract. `unavailable` and `review_required` are not denial; remediation belongs in reasons/next-action metadata. **No consumer-specific booleans or competing union.**
- SH-012 `requestComplianceHold` (Confirmed) — only when Job Compliance evidence warrants admin stop sign; **no local hold state**.
- SH-041 `requestNotification` (Confirmed) — only Job Compliance-owned admin/review intent; Organization Hiring owns organization-facing publication notification after Job state change.

### Domain Logic

Binding boundary:

```text
Organization Hiring owns publication request + Job source version
→ Job Compliance evaluates that version
→ Job Compliance returns/emits decision
→ Organization Hiring rejects stale decision if Job changed
→ Organization Hiring maps decision to Job.complianceStatus/JobStatus under approved U-CL06-05
→ Organization Hiring composes Holds/Trust/visibility
→ Organization Hiring requests Search refresh/removal
```

Job Compliance does not know whether all non-compliance public-readiness gates passed.

### Authorization / Compliance

Human publication authorization remains Organization Hiring/Role concern. Job Compliance request still validates trusted context but must not reimplement Organization role policy. Compliance approval does not bypass Hold/Trust/Organization gates.

### Database / Transaction Behavior

- no direct Job writes from Job Compliance repository;
- decision carries source version/evidence refs;
- Organization Hiring applies only matching current source version;
- late decision is ignored/requeued, never applied to newer Job.

### Events / Jobs

- `job_compliance.decision_changed` is consumed idempotently;
- material Job edit triggers a new evaluation request through Organization Hiring;
- Search retry belongs Search/Organization handoff, not Job Compliance worker.

### Provider Integration

None.

### UI / Admin Surface

No new Job Compliance product UI required. Organization Hiring may render compliance report/decision via public query.

### Failure Behavior

- Job Compliance unavailable → Job remains non-public/pending through Organization policy;
- stale decision → Organization ignores and requests reevaluation;
- Search unavailable after Job opens → Search/owner retry, no Job Compliance rollback;
- Hold/Trust deny → final publication blocked externally even if Job Compliance allowed;
- consumer event duplicate → inbox dedupe.

### Tests

- draft → publication request → allowed → owner open/public path with fixtures;
- warning path under approved mapping;
- denied/review/unavailable paths;
- Job edit race;
- no direct Job Prisma write from Job Compliance;
- Search not called by Job Compliance;
- Search never reconstructs findings;
- Hold/Trust composition remains external;
- event duplicate/replay.

### Documentation Updates

- freeze U-CL06-05 mapping in both Module and Cluster architecture if approved;
- update dependency public-contract docs and progress tracker.

### Acceptance Criteria

- ownership boundary is enforced in code/import tests;
- stale compliance never opens newer Job source;
- Search handoff remains Organization Hiring-owned;
- compliance allowed does not imply final public readiness;
- unavailable/failed never publishes.

### Exit Gate

PASS only if CL-06 Feature 03 boundary tests prove no Job/Search direct writes from Job Compliance, U-CL06-05 is resolved, stale/edit paths work, and all contract/E2E/build checks pass.

# Phase 4 — Privacy and Cross-Module Contract Proof

## 08 Job Compliance Privacy Executor and Retention Mapping

### Objective

Implement the Privacy-defined owner executor for Job Compliance records so Privacy can enumerate and instruct erase/anonymize/restrict/export/retain behavior without Job Compliance owning the privacy-request workflow.

### Observable Result

Privacy can request a versioned subject-data inventory and disposition against Job Compliance-owned records; Job Compliance returns a canonical result with retained/anonymized/erased/restricted/exported/retryable/terminal outcomes and never creates its own PrivacyRequest/DataErasureJob.

### Cluster Build-Plan Link

Supports **CL-06 Feature 13 — Privacy Executors, Retention, and Search/Media Erasure Handoffs**.

### Dependencies

- Features 01–07 as applicable;
- Privacy target protocol;
- SH-097 `evaluateRetentionRequirement` (Confirmed);
- SH-098 `anonymizePersonalFields` (Confirmed);
- approved retention policy for compliance proof before destructive production execution.

### In Scope

- SH-096 `enumerateSubjectData` (Confirmed) implementation;
- Job Compliance target types/identifiers in the Privacy contract;
- export serializer for subject-related Job Compliance evidence;
- local field-level disposition map;
- reviewer reference anonymize/detach path where permitted;
- matched-text/snippet scrubbing path where permitted;
- retention-required response with evidence for Privacy-owned exemption;
- idempotent rerun and partial failure reporting;
- privacy-safe audit/telemetry.

### Out of Scope

- PrivacyRequest/DataErasureJob orchestration;
- DataRetentionExemption creation inside this Module;
- deleting Organization Hiring Job source;
- Search de-index (no Job Compliance projection exists);
- Media/provider deletion.

### Module-Owned Data

Potentially:

- `JobComplianceCheck.reviewedByUserId`, `summary`;
- `JobComplianceFinding` matched text/preview/override reason;
- `JobCompensationDisclosure` descriptions;
- approved historical evaluation proof;
- rule records only when they contain subject-linked data (normally they do not).

### Public Interfaces

- Job Compliance implementation of SH-096 `enumerateSubjectData` (Confirmed);
- Job Compliance implementation of SH-095 `executePrivacyInstruction` (Confirmed);
- owner-fact response used by SH-097 `evaluateRetentionRequirement` (Confirmed).

### Shared Operations Used

- SH-096 `enumerateSubjectData` (Confirmed) — Privacy-defined protocol; local inventory mapping only; **no local privacy request flow**.
- SH-095 `executePrivacyInstruction` (Confirmed) — Privacy orchestrates, Job Compliance executes owned data mutation; **no cross-owner mutation**.
- SH-097 `evaluateRetentionRequirement` (Confirmed) — return owner facts; Privacy owns exemption record; **no local exemption table**.
- SH-098 `anonymizePersonalFields` (Confirmed) — shared primitive; local field map/invariants; **no global crawler/custom scrubber**.
- SH-029 `appendAuditEvent` (Confirmed) / Ops as root policy requires for destructive/legal action; **no local audit/ops models**.

### Domain Logic

- enumerate direct subject references first, especially reviewer user IDs and approved audit/evaluation subject links;
- do not claim unrelated Organization Job content belongs to the requesting user without owner/context evidence;
- retention is explicit, never assumed from soft delete;
- when retention is not required, scrub personal fields while preserving non-personal compliance provenance if approved;
- raw matched text may be removed while hash/rule/source metadata remains when that satisfies approved policy;
- destructive changes must not make historical proof internally inconsistent.

### Authorization / Compliance

Only Privacy-authorized scoped system actor invokes the executor. A user cannot call destructive executor directly. Every retained result cites the Privacy-owned exemption/result reference once created.

### Database / Transaction Behavior

- executor commands are idempotent by privacy request/job/target key;
- update only Job Compliance-owned rows;
- return accurate partial results; never mark success if a child mutation failed;
- no hard delete of required proof without approved retention decision;
- use transactions for multi-row local target mutation where atomicity is required.

### Events / Jobs

Privacy owns orchestration/job schedule. Job Compliance may emit an owner-local privacy execution fact only if root privacy/event policy requires it. Retry/dead-letter uses shared queue owned by Privacy workflow or canonical platform.

### Provider Integration

None.

### UI / Admin Surface

None required. Privacy/admin UI remains Privacy-owned. Optional operational detail must be access-controlled and redact matched text.

### Failure Behavior

- retention unresolved → retained/pending/manual-review result, not destructive guess;
- partial DB failure → retryable/terminal target result;
- already anonymized/erased → idempotent success-equivalent;
- invalid target not owned → explicit unsupported/invalid target result;
- audit/telemetry must not copy deleted sensitive fields.

### Tests

- subject enumeration completeness for direct fields;
- export shaping;
- anonymize/detach reviewer ID;
- matched-text scrub;
- retention-required response;
- idempotent rerun;
- partial failure;
- no cross-owner write;
- telemetry redaction.

### Documentation Updates

- finalize Job Compliance retention/disposition table once legal/policy decision is approved;
- update Privacy interface docs and progress tracker.

### Acceptance Criteria

- Privacy remains sole orchestrator;
- Job Compliance mutates only owned data;
- retained data is explicit and minimized;
- executor is idempotent and partial-failure safe;
- no local privacy workflow/models exist.

### Exit Gate

PASS only if retention mapping is approved for enabled destructive actions, enumeration/export/disposition/idempotency tests pass, and no Privacy ownership is duplicated.

---

## 09 Cross-Module Job Compliance Contract Proof

### Objective

Prove Job Compliance against all direct neighboring owner contracts using real interfaces where available and versioned fixtures otherwise, with failure-closed behavior and no direct cross-domain repository fallback.

### Observable Result

A contract suite demonstrates that Job Compliance can evaluate, report, review, request holds/audits/notifications, participate in publication, and execute privacy instructions while every neighboring Module retains its source truth.

### Cluster Build-Plan Link

Supports **CL-06 Feature 14 — Cross-Cluster Hiring Contract Proof**.

### Dependencies

- Features 01–08;
- versioned fixtures/real interfaces for Identity, Role / Authority, Organization Hiring, Taxonomy/jurisdiction, Holds, Audit, Notification, Privacy, Search (consumer boundary), Ops;
- all Job Compliance production blockers resolved for production-path tests.

### In Scope

Contract tests for:

- Identity actor context;
- Role / Authority decisions;
- Organization Hiring Job input/source version;
- taxonomy/jurisdiction facts;
- Hold request/evaluation boundary;
- Audit append;
- Notification request;
- outbox/inbox delivery;
- Privacy executor;
- Search/publication non-ownership;
- Ops failure visibility;
- Trust Verification separation assertions.

### Out of Scope

- implementing missing neighboring Module internals;
- replacing unavailable dependencies with direct DB reads;
- new product UI;
- generic CL-06 integration layer owning business truth.

### Module-Owned Data

No ownership changes. Test fixtures use DTOs/events/decision envelopes only.

### Public Interfaces

Freeze/version all Job Compliance public commands, queries, events, privacy executor, and the exact owner DTOs it consumes.

### Shared Operations Used

Exercise the already approved canonical operations; do not invent a new “Job Compliance integration service” solely for tests. Prohibited duplicates remain those listed in Module architecture §34.

### Domain Logic

Every dependency denial/unavailable path must remain explicit:

- unauthenticated → deny;
- unauthorized → deny;
- Organization facts unavailable → unavailable, no direct Prisma fallback;
- stale source → stale/re-evaluate;
- jurisdiction unavailable → review/unavailable;
- scanner technical failure → unavailable;
- Hold request unavailable → review/admin action reflects dependency failure; no local hold;
- Audit required but unavailable → follow root privileged-action policy;
- Notification unavailable → retry delivery without rewriting compliance truth;
- Search unavailable → irrelevant to Job Compliance truth and handled by owner after publication.

### Authorization / Compliance

Contract suite must prove cross-Organization evidence isolation, reviewer/admin restrictions, and absence of candidate-screening/background-check ownership.

### Database / Transaction Behavior

Import/repository boundary tests should fail if Job Compliance imports neighboring Prisma repositories or writes their tables. Verify outbox/inbox and idempotent integration behavior.

### Events / Jobs

Exercise duplicate/out-of-order decision events, evaluation retries, rule rescan, and privacy calls. Consumers must use inbox dedupe where implemented.

### Provider Integration

None owned. Scanner is exercised through canonical interface/fixture.

### UI / Admin Surface

No new UI. Existing admin/report components may be included in contract/E2E tests.

### Failure Behavior

Neighbor unavailable must never trigger permissive bypass, hidden direct DB access, or copied business logic.

### Tests

- public contract compatibility/version tests;
- dependency unavailable/deny tests;
- direct repository import guard/lint test where feasible;
- event replay/duplicate tests;
- organization publication fixture E2E;
- review/override audit fixture;
- hold-request fixture;
- privacy executor fixture;
- Search non-ownership assertions;
- candidate-screening separation assertions.

### Documentation Updates

- freeze interface versions;
- document any fixture substitutions and replacement plan;
- update progress tracker;
- update architecture first if contract reveals ownership mismatch.

### Acceptance Criteria

- every direct dependency is represented by typed public contract/fixture;
- no cross-domain repository access exists;
- unavailable dependency is explicit/non-permissive;
- ownership assertions pass;
- public contract versions are documented.

### Exit Gate

PASS only if the complete Job Compliance contract suite passes with deny/unavailable/duplicate/stale cases and no owner boundary violation exists.

# Phase 5 — Hardening and Production Verification

## 10 Job Compliance Reconciliation, Concurrency, Security, and Production Hardening

### Objective

Harden production-enabled Job Compliance workflows for concurrency, replay, historical reproducibility, privacy, audit completeness, queue failure, backfill/reconciliation, security, telemetry safety, performance, and migration safety.

### Observable Result

Job Compliance can survive duplicate requests, Job edits, rule changes, worker crashes, retry exhaustion, privacy reruns, review races, and deployment/backfill scenarios without losing proof, publishing stale decisions, leaking matched text, or acquiring another Module’s truth.

### Cluster Build-Plan Link

Supports **CL-06 Feature 15 — CL-06 Security, Reconciliation, Backfill, and Production Hardening**.

### Dependencies

- Features 01–09;
- every architecture blocker affecting enabled production behavior resolved;
- production queue/outbox/inbox/observability infrastructure;
- current migrations/indexes.

### In Scope

- Job publish/edit/evaluation race stress tests;
- rule activation/evaluation race;
- review/override race;
- semantic idempotency replay;
- dead-letter/manual recovery;
- rescan/backfill checkpoint and dry-run/restart;
- historical proof verification/rebuild checks;
- disclosure/check consistency reconciliation;
- privacy rerun/retention enforcement;
- audit completeness checks;
- telemetry redaction review;
- query/index performance;
- migration rehearsal and rollback compatibility;
- security/RLS/server authorization parity where relevant;
- operational health/metrics/alerts for evaluation pipeline.

### Out of Scope

- new legal/compliance rule families;
- automated hiring decisions;
- candidate screening;
- organization commercial entitlement;
- new external legal-rule provider;
- new generic infrastructure.

### Module-Owned Data

All Job Compliance-owned models and approved historical proof records. No new business truth should be introduced solely for hardening.

### Public Interfaces

Stabilize/version existing contracts only. Any breaking contract change requires architecture and consumer update first.

### Shared Operations Used

Use existing canonical operations for idempotency, concurrency, events, queue/retry, audit, privacy, Ops, hash/canonicalization, versioning/scanner. Hardening must not introduce local replacements.

### Domain Logic

Reconciliation checks should be able to identify:

- current Job Compliance decision references a stale source version;
- current disclosure does not correspond to current evaluation/source identity;
- applied-rule proof missing or inconsistent;
- duplicate semantic checks from pre-idempotency data;
- rules with ambiguous/invalid effective intervals;
- review-resolved check missing required audit/event proof;
- failed evaluation with no visible Ops/dead-letter reference where policy expects one.

Repair rules must be explicit. Prefer re-evaluation/new proof rather than mutating historical evidence.

### Authorization / Compliance

- least privilege for admin repair/retry tools;
- support/admin evidence access is not broad by default;
- destructive privacy/repair paths require scoped authority;
- matched text remains minimized;
- no sensitive telemetry in logs/metrics/error tracking.

### Database / Transaction Behavior

- rehearse migrations on representative data;
- verify unique/index constraints and query plans;
- use database-backed concurrency only;
- backfills are cursor/checkpoint based and restartable;
- avoid destructive cleanup until data has been migrated and architecture approves deprecation;
- findings duplicate fields are removed/normalized only through an approved migration with compatibility handling.

### Events / Jobs

- verify retry/dead-letter and manual recovery paths;
- replay outbox/inbox safely;
- rescan/backfill can resume from checkpoint;
- reconciliation emits safe operational reports, not new business truth;
- alert on sustained evaluation failure/backlog/review age.

### Provider Integration

No owned provider. Validate scanner library/runtime degradation through canonical scanner interface. No provider webhook tests are required unless architecture later adds an owned provider.

### UI / Admin Surface

Only operational/admin surfaces needed to inspect failed evaluations, rescan/backfill progress, review backlog, and safe reconciliation results. These views are not source truth and must not expose full sensitive text unnecessarily.

### Failure Behavior

- no silent loss;
- no permissive fallback;
- no stale source overwrite;
- no historical proof mutation disguised as repair;
- retry exhaustion remains visible with safe reference;
- partial backfill/reconciliation records checkpoint and resumes safely;
- unresolved corruption goes to manual review/incident rather than guessed repair.

### Tests

- full typecheck/lint/build;
- domain/unit suite;
- DB/integration suite;
- contract suite;
- authorization/RLS parity suite;
- concurrency/load tests for evaluation/review/rule transitions;
- idempotency/replay tests;
- queue crash/dead-letter tests;
- rescan/backfill restart tests;
- privacy/retention tests;
- audit completeness tests;
- telemetry snapshot/redaction tests;
- migration rehearsal;
- query performance tests;
- CL-06 critical E2E: Organization → Job draft → Compliance → Organization publication → Search fixture.

### Documentation Updates

- update architecture if any binding hardening discovery changes source truth/contract;
- update migration/backfill runbook;
- update event/decision contract versions;
- update progress tracker and known-risk register;
- record unresolved legal/policy risks separately from technical completion.

### Acceptance Criteria

- all enabled U-CL06 Job Compliance blockers are resolved;
- no lifecycle has two owners;
- no canonical operation is duplicated;
- historical evaluation proof is reproducible;
- stale publication decisions are impossible under tested races;
- retries/replays do not duplicate business effects;
- privacy/retention executor is rerunnable;
- privileged actions have complete audit proof;
- matched text is absent from unsafe telemetry;
- backfills/reconciliation are restartable and non-destructive by default;
- performance is acceptable for expected MVP evaluation/report workloads.

### Exit Gate

PASS only if the full production suite passes, no unresolved production architecture blocker remains, no cross-Module repository write exists, Job Compliance decision reproducibility is verified, failure/replay/privacy/audit/concurrency invariants hold, and documentation/progress agree with code.

# Module Integration Phase

The explicit integration work is concentrated in Features **07 and 09**. These prove the most important boundaries without transferring ownership.

Minimum owner-contract chain:

```text
Identity actor
→ Role / Authority decision
→ Organization Hiring Job/source-version facts
→ Job Compliance evaluation/decision/proof
→ Organization Hiring applies Job lifecycle/mirror
→ Organization Hiring composes Holds/Trust/visibility
→ Organization Hiring requests Search
```

Supporting Job Compliance contracts:

```text
Taxonomy/jurisdiction facts → Job Compliance rule applicability
Job Compliance review → Audit
Job Compliance review/admin intent → Notification
Job Compliance escalation → ComplianceHold request
Privacy → Job Compliance owner executor
Ops → technical failure visibility only
```

Integration tests use owner public contracts. If an owner is not implemented, use a versioned fixture matching the documented contract. Never import the owner repository as a shortcut.

# Module Hardening Phase

Feature **10** covers only Job Compliance production risks:

- source-version staleness;
- Job publish/edit evaluation race;
- rule activation/rescan race;
- review/override concurrency;
- command/worker replay;
- queue retry/dead-letter;
- historical rule/source proof verification;
- current disclosure/check consistency;
- privacy/retention rerun;
- audit completeness;
- sensitive telemetry redaction;
- backfill/reconciliation;
- index/query performance;
- migration safety.

Hardening must not create a Job Compliance-owned Job lifecycle, Search projection, candidate screening model, general moderation system, generic readiness engine, rule platform, queue, event ledger, or provider-event table.

# Phase Summary

| **Phase** | **Name** | **Features** |
| --------- | -------- | ------------ |
| 1 | Rule and Evaluation Proof Foundation | 01–03 |
| 2 | Findings, Decision, Review, and Public Contracts | 04–05 |
| 3 | Durable Evaluation, Events, and Publication Handoff | 06–07 |
| 4 | Privacy and Cross-Module Contract Proof | 08–09 |
| 5 | Hardening and Production Verification | 10 |

**Total numbered features: 10.**

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read the Canonical Shared Operations Architecture/Registry.
3. Read CL-06 architecture and build plan.
4. Read `job_compliance/module-architecture.md` and this implementation plan.
5. Read public-interface sections for the direct dependencies used by this feature.
6. Read current Prisma schema/migrations and applicable architecture-decision records.
7. Confirm the prior feature exit gate passed.
8. Confirm all `U-CL06-*` blockers relevant to this feature are resolved or the feature explicitly permits a contract fixture/non-production implementation.
9. Write the concise feature implementation specification below.
10. Implement only this feature and approved prerequisite changes in their canonical owners.
11. Run typecheck/lint/unit/integration/contract/migration/build checks required by the feature.
12. Verify denial, stale, duplicate, retry, and privacy behavior where relevant.
13. Update progress.
14. Update architecture first if a binding decision legitimately changes.
15. Record unresolved risks and deferred work.

Do not weaken an exit gate to mark a feature complete.

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise specification containing:

- **Objective**
- **Observable result**
- **Dependencies**
- **In scope**
- **Out of scope**
- **Owned data affected**
- **Public contracts**
- **Shared operations consumed**
- **Permissions/compliance**
- **Primary workflow**
- **Provider integration**
- **Jobs/events**
- **Idempotency/concurrency**
- **Error behavior**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**
- **Architecture decisions resolved or still blocking**

Do not generate all feature specifications in advance. Generate the specification for the next feature immediately before implementation.

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused
- Events/jobs added
- Provider adapter changes
- Tests added/changed
- Commands run
- Manual/contract verification
- Documentation updated
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

The report must explicitly state whether any architecture decision changed. If yes, architecture must already have been updated before the implementation is accepted.

# Final Quality Check

Before declaring the Job Compliance Module implementation complete, verify:

1. Job Compliance source truth has one owner.
2. Organization Hiring Job truth was not absorbed.
3. Candidate screening/FCRA adverse action was not absorbed.
4. General moderation was not absorbed.
5. Every shared operation is consumed rather than duplicated.
6. Shared scanner/version/hash mechanics remain separate from Job Compliance policy truth.
7. Public commands/queries/events are stable and versioned where required.
8. Cross-Module reads use public interfaces rather than neighboring repositories.
9. No provider/library object became business truth.
10. Audit, Job Compliance evidence, domain events, and Ops telemetry remain distinct.
11. Privacy orchestration remains Privacy-owned.
12. Search remains a projection and is not written by Job Compliance.
13. Organization Hiring applies the Job lifecycle decision.
14. Technical scanner failure can never approve/reject a Job.
15. A zero-finding pass proves the applied rule set and source version.
16. Material Job edits invalidate stale decisions.
17. Every numbered feature has passing tests and an exit gate.
18. CL-06 sequencing remains intact.
19. U-CL06-05/07 policy is resolved and binding U-CL06-06 proof has approved implemented persistence before production Job publication.
20. A coding agent can explain which source record owns every write made by this Module.
