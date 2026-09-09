# Job Compliance Module Architecture

> **Module ID:** `job_compliance`  
> **Module name:** Job Compliance Module  
> **Primary Cluster:** CL-06 — Organization Hiring & Candidate Pipeline  
> **Document status:** implementation-grade Module architecture with explicit production blockers  
> **Authority:** subordinate to root Workin Ants architecture and CL-06 architecture; superior to Module implementation progress

This document defines what the Job Compliance Module owns, what it may transform, the stable interfaces it exposes, the dependencies it may consume, and the responsibilities it must never absorb. It is intentionally narrower than the CL-06 architecture.

The current evidence set establishes the Module boundary but leaves three production-publication decisions unresolved: **U-CL06-05 effective decision semantics, U-CL06-06 historical rule-set/source proof, and U-CL06-07 `CompensationPeriod` / `EmploymentType.contract` semantics**. Those decisions are explicitly carried below and must not be silently resolved in code.

## 1. Module Header

| Field | Value |
|---|---|
| Module ID | `job_compliance` |
| Module name | Job Compliance Module |
| Module type | `compliance` |
| Build status | `mvp_active_legal_gated` |
| Primary Cluster | CL-06 — Organization Hiring & Candidate Pipeline |
| Document status | Implementation-grade architecture; production publication remains blocked by U-CL06-05/06/07 |
| Intended audience | Coding agents, developers, reviewers, maintainers, compliance reviewers, and CL-06 integrators |
| Relationship to root architecture | Root architecture owns platform-wide lifecycle, security, privacy, provider, event, and source-of-truth rules. This file may specialize those rules only for Job Compliance. |
| Relationship to Cluster architecture | CL-06 owns coordination and sequencing only. This Module owns Job Compliance truth and policy. Cluster decisions remain superior where they constrain cross-Module boundaries. |
| Update rule | Update this architecture before implementation whenever a binding ownership, lifecycle, schema, public-contract, privacy, event, or shared-operation decision changes. Build progress must not redefine architecture. |

### Evidence basis

This file is derived from the current Workin Ants project overview, Deep Module Registry, current Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Architecture, CL-06 architecture, CL-06 build plan, and the earlier standardized Job Compliance Module Architecture Extract.

The BTLS architecture/build-plan material is used only as a structural and specificity benchmark: explicit boundaries, concrete code placement, vertical slices, testable exit gates, and completion reporting. No BTLS domain concepts or provider choices are imported here.

## 2. Purpose, Goal, and Transformation

### Purpose

Evaluate a formal `Job` posting against versioned, jurisdiction-aware employment-posting policy before that Job is allowed to proceed through public publication, and preserve durable evidence explaining what was evaluated and why the resulting compliance decision was reached.

### Goal

Produce one authoritative Job Compliance decision that Organization Hiring can consume without recreating salary-disclosure, EEOC-language, Fair Chance, salary-history, benefits-disclosure, or related posting rules.

The Module must support:

- deterministic evaluation of all relevant Job text and structured fields;
- jurisdiction/effective-date rule resolution;
- pay-transparency and compensation-disclosure proof;
- structured findings with rule/scanner provenance;
- warning, blocking, and human-review outcomes;
- human review and reasoned override without deleting original evidence;
- durable rule-version/source-version proof;
- asynchronous retry of technical failures without converting those failures into legal/business decisions.

### What enters

- an authenticated or trusted system actor context;
- a Job identifier and expected source version, or an Organization Hiring-issued authoritative Job compliance input DTO;
- Organization/Job relationship facts exposed through Organization Hiring’s public interface;
- Job text and structured fields that are in scope for posting compliance;
- compensation facts owned by Organization Hiring;
- normalized jurisdiction context or enough source facts to resolve it through the canonical shared mechanism;
- applicable taxonomy/context facts when they affect which rules apply;
- active Job Compliance rule versions;
- reviewer/admin action context for rule management, review, or override.

### What leaves

- a durable `JobComplianceCheck`;
- zero or more `JobComplianceFinding` records;
- a current `JobCompensationDisclosure` proof record;
- the architecture-approved historical source/rule-set proof required by U-CL06-06;
- a stable `DecisionResult` containing decision, reason codes, warnings, evidence references, policy/source versions, remediation, and retryability;
- Job Compliance domain events through the canonical outbox;
- audit requests for privileged human actions;
- optional ComplianceHold requests for administrative stop-sign cases;
- notification intent for review/admin workflow when appropriate.

### Business/capability transformation

```text
Organization Hiring-owned Job facts
+ normalized jurisdiction/context
+ active versioned Job Compliance rules
+ shared canonicalization/hash/scanner mechanics
        ↓
Job Compliance interpretation
        ↓
check + findings + disclosure proof + historical evaluation proof
        ↓
Job Compliance DecisionResult
        ↓
Organization Hiring applies its own Job lifecycle policy
        ↓
Search/Notification/other downstream effects occur through their owners
```

### Why this is a separate Module

Job posting compliance has independent legal/policy meaning, versioning, evidence, review, and reproducibility requirements. Those concerns would overload Organization Hiring if embedded there and would be dangerous if reconstructed by Search, Moderation, or candidate-screening code. The Module boundary preserves the core distinction:

> **Job Compliance checks the posting. Organization Hiring owns the Job. Trust Verification checks people/credentials. Search projects approved source truth.**

## 3. Owned Truth

### 3.1 Owned models

| Record | Meaning | Ownership ruling |
|---|---|---|
| `JobComplianceRule` | One immutable/versioned employment-posting rule configuration scoped by type, jurisdiction/context, effective dates, and review/blocking defaults. | Job Compliance owns rule meaning, version lifecycle, and policy semantics. |
| `JobComplianceCheck` | One durable evaluation/review result for a particular Job source state. | Job Compliance owns the check outcome and review metadata. |
| `JobComplianceFinding` | One structured compliance issue/warning discovered during a check, with source-field, rule, scanner, jurisdiction, and match provenance. | Job Compliance owns finding type, severity, interpretation, resolution, and override meaning. |
| `JobCompensationDisclosure` | Current Job-attached compliance proof describing whether compensation/benefit disclosure satisfies the applicable posting rule. | Job Compliance owns disclosure evaluation/proof; Organization Hiring owns offered compensation business truth. |

### 3.2 Owned enums and status semantics

**Confirmed Job Compliance-owned vocabulary:**

- `JobComplianceCheckStatus`
- `JobComplianceFindingType`
- `JobComplianceSeverity`
- `JobComplianceRuleType`
- `JobComplianceRuleStatus`
- `JobCompensationDisclosureStatus`

**Split or unresolved vocabulary:**

- `JobComplianceStatus` is stored on Organization Hiring-owned `Job`. The CL-06 architecture proposes that this field is an Organization Hiring-owned summary mirror written only from the Job Compliance decision. Job Compliance owns the semantics of the decision it returns; it must not directly mutate `Job.complianceStatus` unless a later explicit owner command says otherwise.
- `CompensationPeriod` is claimed historically by Job Compliance but is used as core `Job` compensation vocabulary. U-CL06-07 remains unresolved. This Module must consume the canonical value and must not create a second compensation-period enum.
- `EmploymentType` belongs to Organization Hiring. The meaning of `EmploymentType.contract` remains unresolved under U-CL06-07 and must not be reinterpreted locally.

### 3.3 Lifecycles owned

- Job Compliance rule version lifecycle.
- Job Compliance check evaluation/review lifecycle.
- Job Compliance finding resolution/override lifecycle.
- Job compensation disclosure evaluation lifecycle.

The Module **does not** own `JobStatus`, `JobVisibility`, Job publication timestamps, Search projection state, `ComplianceHold`, or Trust Verification state.

### 3.4 Source-of-truth records

- **Rule truth:** `JobComplianceRule`.
- **Evaluation truth:** `JobComplianceCheck`.
- **Finding/provenance truth:** `JobComplianceFinding`.
- **Current compensation-disclosure proof:** `JobCompensationDisclosure`.
- **Effective public decision:** returned by Job Compliance from its own current evidence; exact source/precedence remains U-CL06-05 until approved.
- **Historical evaluation proof:** required but current Prisma does not yet provide sufficient legal-grade source/rule-set reproducibility for a zero-finding check. U-CL06-06 must settle the exact record/field design.

### 3.5 Domain events and ledgers owned

There is no current Job Compliance domain-event ledger model in Prisma. Job Compliance therefore owns **event meaning**, while the canonical platform outbox owns delivery mechanics.

Expected event family:

- `job_compliance.evaluated`
- `job_compliance.decision_changed`
- `job_compliance.review_required`
- `job_compliance.review_resolved`
- `job_compliance.evaluation_failed`
- `job_compliance.rule_activated`
- `job_compliance.rule_retired`
- `job_compliance.rule_disabled`

These are integration facts, not replacements for `JobComplianceCheck`, findings, disclosure proof, or generic `AuditEvent`.

### 3.6 Projections owned

No public/Search projection is owned here.

A current effective-decision view may be computed by Job Compliance from owned proof, but Search/Typesense remains Search-owned and `Job.complianceStatus` remains an Organization Hiring mirror under the current Proposed Ruling.

### 3.7 Snapshots and proof owned

Confirmed proof includes:

- `checkedTextHash`;
- scanner name/version;
- finding source field;
- matched-text hash and minimized preview;
- rule key/version on findings;
- finding jurisdiction;
- compensation disclosure rule key/version and jurisdiction;
- reviewer identity/time where present.

**Missing binding proof:** exact source-version and full applied-rule-set proof for a zero-finding evaluation. A production implementation may not invent this schema. See PR-JC-02 and U-CL06-06.

### 3.8 Policies and invariants owned

Job Compliance owns:

- which Job fields/surfaces are evaluated;
- how active rule versions are applied to a posting;
- how raw scanner matches become domain findings;
- which finding types/severities produce pass, warning, block, or review;
- pay-transparency/disclosure evaluation;
- when human review is required;
- how an authorized override affects the Job Compliance decision;
- reason-code semantics returned to consumers;
- when a compliance-originated administrative hold should be requested rather than creating a local block flag.

## 4. Explicit Non-Ownership

Job Compliance must not own or implement the following neighboring truth.

| Adjacent owner | Responsibility that remains outside Job Compliance |
|---|---|
| Identity & Access | User authentication, session resolution, MFA/passkey challenges, step-up sessions. |
| Role / Authority | Interpretation of organization/admin/support permissions. Job Compliance supplies action/resource facts only. |
| Organization Hiring | `Organization`, `OrganizationMember`, `OrganizationRole` assignment, `Job`, `JobStatus`, `JobVisibility`, offered compensation, Job publication lifecycle, and the final source-state transition. |
| Taxonomy & Classification | Canonical domain/category/tag vocabulary and taxonomy semantics. |
| Trust Verification / Screening | `VerificationRequirement`, `VerificationCheck`, candidate/person screening, professional credentials, FCRA adverse-action workflow, badges, and verification provider integration. |
| Candidate Application & Resume Privacy | CandidateProfile, JobApplication, resumes, parsing, resume access, candidate search projection, and hiring-pipeline state. |
| Content Moderation & Legal Notice | General content moderation, reports, legal notices, ModerationCase, and moderation actions. Similar scanner mechanics do not merge these truths. |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and reusable stop-sign truth. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense writes, indexing/de-indexing, reconciliation, and Search query surfaces. |
| Notification | Notification persistence, templates registry implementation, recipient/channel delivery, provider callbacks, retries, and delivery truth. |
| Audit / Event Ledger | Generic `AuditEvent` and `AccessAuditLog`. |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, export workflow, and privacy orchestration. |
| Observability / Ops | `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident`, generic logs/metrics/incident workflow. |
| Shared platform infrastructure | Generic idempotency, locks, queues, retries, outbox/inbox, cryptography, canonical text mechanics, and generic scanner runtime. |

Concrete prohibitions:

- Do not write `Job.status`, `Job.visibility`, `publishedAt`, or other general Job lifecycle fields directly.
- Do not put salary/EEOC/Fair Chance validators in Organization Hiring or Search; conversely, do not pull Job repository ownership into this Module.
- Do not screen candidates or store background-check provider results here.
- Do not create a `jobBlocked`/`isCompliant` boolean or local hold table.
- Do not create a direct Typesense client.
- Do not send email/SMS/push directly.
- Do not create a generic platform rule engine owned by Job Compliance.
- Do not create a second text normalizer, hash utility, queue framework, idempotency store, or scanner runtime.
- Do not treat `compromise` or `natural` output as legal truth.

## 5. Module Architecture Principles

1. **Posting compliance is separate from Job lifecycle.** Job Compliance returns a decision; Organization Hiring mutates Job lifecycle.
2. **Posting compliance is separate from candidate screening.** Fair Chance language checks do not make this Module the FCRA background-check owner.
3. **Rules are versioned policy, not code-only conditionals.** Production behavior must be reproducible from explicit rule versions and source proof.
4. **All relevant Job surfaces are evaluated.** Do not scan `description` only when title, location, compensation fields, benefits/commission text, or other structured fields affect policy.
5. **Technical failure is not a compliance outcome.** Scanner/runtime failure maps to explicit unavailable/failed state and keeps publication non-permissive.
6. **Warnings and review are first-class.** The Module must not collapse every non-pass into a generic block.
7. **NLP is evidence generation, not legal adjudication.** Raw matches require Module-owned interpretation and may require human review.
8. **Evidence survives policy changes.** Active rule edits do not rewrite historical check meaning; new policy is a new version.
9. **Source edits invalidate stale decisions.** A result tied to an older Job source version may not be applied to the new Job state.
10. **Shared mechanisms do not absorb employment policy.** Canonicalization, hashing, scanner runtime, version plumbing, queueing, and DecisionResult shape are reusable; employment rule semantics remain local.
11. **ComplianceHold is an external stop sign.** Routine Job Compliance block/review is represented by Job Compliance decision; an administrative hold is requested only when the reusable platform hold lifecycle is appropriate.
12. **Search consumes owner decisions.** Search never reconstructs Job Compliance from findings, text, or stale mirrored fields.
13. **Privileged human changes are auditable.** Rule activation/retirement, review resolution, and overrides use the generic Audit interface in addition to Module proof.
14. **Telemetry is minimized.** Protected-class phrases and matched text are not copied into logs, analytics, event payloads, or notification bodies unless explicitly necessary and approved.
15. **Unresolved legal/architecture semantics fail closed.** Unknown jurisdiction, missing approved rule-set proof, or unresolved production mapping cannot silently pass.

## 6. Proposed Folder / Code Structure

The CL-06 architecture proposes a Module-local structure under `src/modules/job-compliance`. The implementation should remain close to this shape:

```text
src/modules/job-compliance/
  domain/
    decision-result.ts
    reason-codes.ts
    rule-applicability.ts
    disclosure-policy.ts
    finding-policy.ts
    review-policy.ts
    invariants.ts

  application/
    commands/
      request-job-compliance-evaluation.ts
      review-job-compliance-check.ts
      override-job-compliance-finding.ts
      publish-job-compliance-rule-version.ts
      retire-job-compliance-rule-version.ts
      disable-job-compliance-rule-version.ts
    queries/
      get-job-publication-compliance-decision.ts
      get-job-compliance-report.ts
      get-applicable-job-compliance-requirements.ts
    services/
      evaluate-job-compliance.ts
      resolve-applicable-job-compliance-rules.ts
      validate-job-compensation-disclosure.ts
      classify-job-compliance-findings.ts

  public/
    contracts.ts
    commands.ts
    queries.ts
    events.ts
    privacy.ts
    validation/
      command-schemas.ts
      query-schemas.ts

  persistence/
    job-compliance-repository.ts
    prisma-job-compliance-repository.ts
    mappers.ts

  scanners/
    job-scanner-policy.ts
    scanner-match-mapper.ts

  events/
    event-builders.ts

  jobs/
    evaluate-job-compliance.worker.ts
    rescan-affected-jobs.worker.ts

  admin/
    actions/
    queries/
    components/

  privacy/
    enumerate-job-compliance-subject-data.ts
    execute-job-compliance-privacy-instruction.ts
    retention-map.ts

  tests/
    unit/
    contract/
    integration/
    authorization/
    compliance/
    concurrency/
    privacy/
```

Rules:

- `scanners/` contains Job Compliance interpretation/mapping only. The generic tokenizer/pattern engine is the canonical `runPatternScanner` mechanism outside this Module.
- `persistence/` may access only Job Compliance-owned tables. Organization Hiring data is obtained through its public owner-facts/input interface.
- `admin/` is restricted to the rule/review/override surface genuinely owned by Job Compliance. The Organization Job detail/publication UI remains Organization Hiring-owned.
- Do not create a `providers/` folder unless a future architecture decision gives Job Compliance ownership of an external provider integration. `compromise` and `natural` are libraries behind shared scanner mechanics, not provider truth.
- Shared platform primitives remain under platform/shared infrastructure, not copied into this Module.

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / admin UI | Rule administration, review/override interaction, compliance evidence presentation for privileged users. | General Organization/Job editor, Job publication lifecycle UI, Search UI, notification delivery UI. |
| Public actions / contracts | Runtime-validated Module commands/queries/events/privacy executor contracts. | Cross-domain repositories or provider payload types. |
| Application services | Command orchestration, Job Compliance evaluation flow, review flow, rule lifecycle commands, privacy executor coordination. | Organization Hiring lifecycle transitions, Search writes, generic workflow engine. |
| Domain policy | Rule applicability, finding classification, disclosure policy, decision precedence, reason codes, review/override semantics. | Auth policy, Trust Verification readiness, general moderation policy, candidate screening. |
| Persistence | CRUD/query for Job Compliance-owned models and architecture-approved proof records. | `Job`, `Organization`, `ComplianceHold`, Search, Audit, Notification, Privacy tables. |
| Workers | Evaluation execution and rule-change rescan/backfill using shared queue/retry primitives. | Generic queue framework or Job lifecycle worker. |
| Scanner mapping | Translate raw canonical scanner matches into employment-policy findings. | Tokenizer/pattern runtime, legal provider client, moderation findings. |
| Events | Event names, minimized payloads, emission conditions. | Outbox/inbox infrastructure and generic audit truth. |
| Privacy executor | Enumerate and mutate Job Compliance-owned subject data under Privacy instruction. | PrivacyRequest orchestration, DataRetentionExemption lifecycle. |

## 8. Data Model

### 8.1 `JobComplianceRule`

**Purpose:** versioned policy configuration for one employment-posting rule.

**Key relationships:** no direct FK to checks/findings in the current schema. Historical linkage is denormalized through `ruleKey`/`ruleVersion` on findings and disclosure.

**Authoritative fields:**

- `type`
- `status`
- `key`
- `version`
- `jurisdictionCountry/state/city`
- `blockingByDefault`
- `requiresAdminReview`
- `patternJson`
- `neutralSuggestionJson`
- `effectiveAt`
- `retiredAt`

**Lifecycle field:** `status`.

**Constraints/indexes:**

- unique `(key, version)`;
- indexes on `(type,status)`, jurisdiction tuple, and `effectiveAt`.

**Concurrency concerns:** rule activation/retirement/disable must prevent conflicting mutation of the same version and should prevent an invalid overlapping effective-version set for the same rule key/scope. Exact overlap constraint is not present in Prisma and must be enforced through the approved versioning policy/transaction.

**Retention/privacy:** rule configuration normally contains policy, not subject data. Admin author identity is not represented in the current schema; generic AuditEvent must capture privileged changes.

### 8.2 `JobComplianceCheck`

**Purpose:** durable outcome of one compliance evaluation or review resolution for a Job source state.

**Key relationships:** belongs to `Job`; has many `JobComplianceFinding`; optional reviewer `User`.

**Authoritative fields:**

- `jobId`
- `status`
- `scannerName`
- `scannerVersion`
- `checkedTextHash`
- `summary`
- `reviewedByUserId`
- `reviewedAt`

**Lifecycle field:** `status`.

**Indexes:** `(jobId,createdAt)`, `status`, `reviewedByUserId`.

**Concurrency concerns:**

- evaluation must be tied to an opaque Organization Hiring `sourceVersion`/expected version;
- stale results may not supersede a result for a newer Job source version;
- duplicate semantic evaluations must be idempotent;
- review resolution against an already superseded or already resolved check must return conflict.

**Retention/privacy:** reviewer identity and summary may be personal/sensitive. Raw matched Job text should not be copied into `summary`.

**Current proof gap:** the schema does not record the full applied rule set or an authoritative Job source version. `checkedTextHash` alone cannot prove which rules were evaluated in a zero-finding result. U-CL06-06 blocks production-grade reproducibility.

### 8.3 `JobComplianceFinding`

**Purpose:** structured evidence for one compliance issue, warning, or review trigger.

**Authoritative fields:**

- `type`
- `severity`
- source-field identity;
- match offsets where applicable;
- matched-text hash;
- minimized snippet preview;
- rule key/version;
- scanner name/version;
- jurisdiction;
- suggested replacement;
- override/resolution fields.

**Current schema duplication requiring cleanup or explicit semantics:**

- `fieldName` and `sourceField`;
- `matchedText` and `matchedSnippetPreview`;
- `suggestedText` and `suggestedReplacement`.

No implementation may arbitrarily choose different meanings for these duplicates. The first migration touching these fields must either document the distinction or consolidate them through an architecture-approved migration.

**Lifecycle/resolution fields:** `adminOverride`, `adminOverrideReason`, `resolvedAt`.

**Indexes:** `checkId`, `(type,severity)`.

**Concurrency concerns:** override/resolution is a privileged write against one finding/check version and must reject stale/double resolution.

**Retention/privacy:** matched text can contain protected-class or other sensitive language. Prefer hash + minimal preview over full text. Full text must not enter logs/events/analytics. Any retention of `matchedText` requires explicit privacy/retention policy.

### 8.4 `JobCompensationDisclosure`

**Purpose:** current Job-attached compliance proof for compensation and related disclosure requirements.

**Key relationship:** one-to-one with `Job` through unique `jobId`.

**Authoritative compliance fields:**

- `status`
- jurisdiction tuple;
- `ruleKey`/`ruleVersion`;
- evaluated compensation range/currency/period snapshot;
- benefits/bonus/commission/equity/tips descriptions;
- `remoteRole`;
- `locationBasedRule`;
- `checkedAt`.

**Lifecycle field:** `status`.

**Constraints/indexes:** unique `jobId`; indexes on status, jurisdiction, rule key/version.

**Concurrency concerns:** update must be tied to the same source version/check being evaluated; an older evaluation may not overwrite a newer disclosure result.

**Retention/privacy:** disclosure descriptions are organization-authored Job content and may contain names/contact details accidentally. Minimize and treat as subject data when Privacy identifies it.

**Boundary:** `Job.compensationMinCents`, `Job.compensationMaxCents`, `Job.currency`, and the canonical compensation-period value are Organization Hiring business truth. The disclosure record is compliance proof/snapshot, not a second editable compensation source.

### 8.5 Referenced but not owned: `Job`

Job Compliance consumes the minimum Job facts required for evaluation through Organization Hiring’s public contract. It must not import a Job repository directly.

Important fields currently relevant to evaluation include title, description, employment type, domain/category, location/city/state/country, remote flag, compensation range/currency/period, and source-state/version context. Exact included fields are governed by the Job Compliance canonicalization policy.

### 8.6 Required historical proof not yet modeled

**U-CL06-06 is blocking.** Before production implementation, architecture must define a Job Compliance-owned immutable evaluation proof sufficient to answer:

- exactly which Job source version/snapshot was evaluated;
- which canonicalization version was used;
- which jurisdiction context was used;
- every rule key/version evaluated, including a zero-finding pass;
- scanner/runtime version;
- a stable rule-set/input fingerprint;
- the compensation-disclosure input/result tied to that evaluation.

The exact schema must be approved before migration. Do not invent a hidden JSON blob or infer history from current mutable records.

## 9. Enums, Statuses, and Lifecycles

### 9.1 Job Compliance rule lifecycle

Statuses:

```text
draft → active → retired
   └────→ disabled
active ─→ disabled
```

Rules:

- `draft` may be edited by authorized rule administrators.
- activation makes the version effective according to `effectiveAt` and policy scope.
- an `active` rule version is immutable in meaning; material policy changes require a new `(key,version)`.
- `retired` means intentionally superseded/ended for future evaluation.
- `disabled` means not eligible for future evaluation because it was administratively disabled.
- historical checks continue to reference the original version even after retirement/disable.
- retired/disabled versions are treated as terminal for policy meaning; reactivation should create/activate a new version unless architecture explicitly permits re-enable.
- all privileged transitions append generic audit proof and emit the appropriate Module event.

### 9.2 Job Compliance check lifecycle

Statuses:

```text
completed evaluation
  ├─ passed
  ├─ warning
  ├─ blocked
  ├─ needs_review ──authorized review──> passed | warning | blocked
  └─ failed
```

Rules:

- queue `pending/running/retrying` state is operational `QueueJob` truth, not `JobComplianceCheckStatus`.
- a completed automated evaluation writes a durable outcome.
- `failed` means the evaluation could not produce a trustworthy compliance result after the applicable technical failure policy; it is never equivalent to approved or rejected.
- `needs_review` may transition only through an authorized review command.
- `passed`, `warning`, `blocked`, and `failed` are terminal for that check instance.
- re-evaluation creates a new check/evaluation proof for the new source/rule set; it does not reset old evidence.
- current schema permits in-place review resolution but does not itself preserve the original status transition history. Audit/event proof is therefore mandatory; if legal review requires a dedicated immutable review record, architecture must add it before implementation.

### 9.3 Finding resolution lifecycle

Current fields imply:

```text
open/unresolved
  ├─ resolved without override
  └─ admin override + reason + resolvedAt
```

Rules:

- findings are never deleted merely because an override occurred;
- an override changes how the decision interprets the finding, not what the scanner originally observed;
- override requires authorized actor, reason, audit event, and review event;
- double override/double resolution is a stale/conflict case;
- original rule/scanner/match provenance remains intact.

### 9.4 Compensation-disclosure lifecycle

Statuses:

```text
not_required
required_missing
provided
provided_with_warning
exempt
blocked
```

This record is a current evaluated proof, not an independent Job lifecycle. Re-evaluation may move between statuses as Job compensation content or applicable rules change.

**Proposed mapping under PR-JC-01:**

- `provided`, `not_required`, `exempt` do not independently block;
- `provided_with_warning` contributes warning;
- `required_missing`, `blocked` contribute denial/block;
- any unresolved jurisdiction/rule requirement contributes review/unavailable rather than silent pass.

This mapping becomes binding only when U-CL06-05 is approved.

### 9.5 `JobComplianceStatus` summary vocabulary

Current values:

```text
not_checked | pending_review | approved | rejected | needs_changes
```

Under the CL-06 Proposed Ruling, this is an Organization Hiring-owned mirror of Job Compliance outcome. Job Compliance must return a stable decision; Organization Hiring maps that decision into its field and Job lifecycle. Job Compliance must not treat `Job.complianceStatus` as an independent policy source.

## 10. Commands

### 10.1 `requestJobComplianceEvaluation`

**Purpose:** idempotently request evaluation of a specific Job source version.

**Actor/context required:** authenticated authorized organization actor, platform/admin actor, or trusted Organization Hiring/system actor. The command must preserve originating actor/correlation context even when executed asynchronously.

**Authoritative inputs:**

- `jobId`;
- `expectedSourceVersion` (opaque owner version, current implementation may use owner-issued `updatedAt` until a dedicated version exists);
- trigger reason: publication request, material edit, rule-change rescan, admin rescan, or equivalent approved vocabulary;
- idempotency key;
- correlation/causation IDs.

**Preconditions:**

- actor resolved;
- requested action authorized;
- Organization Hiring confirms Job exists and is eligible to be evaluated;
- production evaluation requires U-CL06-05/06/07 resolution.

**State written:** canonical idempotency receipt and durable queue work; Module source records are written by evaluation worker/service, not by a route handler.

**Shared operations:** `resolveAuthenticatedActor`, `authorizeResourceAction`, `executeIdempotentCommand`, `enqueueReliableJob`.

**Effects:** evaluation job; optional `job_compliance.evaluation_requested` is not required as a domain event because the request itself is a command. If recorded, it must be an operational/workflow fact, not an outcome.

**Idempotency:** same semantic key returns the existing evaluation receipt/result.

**Failure modes:** validation error, authorization denial, Job not found, stale source version, unresolved architecture gate, queue unavailable.

### 10.2 `reviewJobComplianceCheck`

**Purpose:** resolve a `needs_review` check into an approved warning/pass or block result under Job Compliance policy.

**Actor/context:** authorized compliance reviewer/admin through Role / Authority.

**Inputs:** check ID, expected check version/updatedAt, review outcome, reason, optional finding-level resolutions, idempotency key.

**Preconditions:** check is current enough for review, status is `needs_review`, Job source has not invalidated the check according to source-version policy.

**State written:** reviewed fields/check status; finding resolution fields if part of the command.

**Shared operations:** actor/authority, idempotency, optimistic concurrency, `appendAuditEvent`, `publishDomainEvent`, optional `requestNotification`.

**Events:** `job_compliance.review_resolved`; `job_compliance.decision_changed` if effective decision changes.

**Failure modes:** unauthorized, already resolved, superseded/stale source, invalid review outcome, audit/outbox transaction failure.

### 10.3 `overrideJobComplianceFinding`

**Purpose:** record a reasoned authorized override without deleting the original finding.

**Actor/context:** privileged reviewer/admin.

**Inputs:** finding ID, expected version/context, override reason, desired resolution effect, idempotency key.

**Preconditions:** finding belongs to reviewable/current check; actor authorized; reason required.

**State written:** `adminOverride`, `adminOverrideReason`, `resolvedAt`, related check decision as allowed by review policy.

**Shared operations:** actor/authority, idempotency, concurrency, `appendAuditEvent`, `publishDomainEvent`.

**Failure modes:** stale/already resolved finding, invalid target state, unauthorized, superseded check.

### 10.4 `publishJobComplianceRuleVersion`

**Purpose:** activate an approved Job Compliance rule version.

**Actor/context:** privileged rule administrator.

**Inputs:** rule ID/key/version, effective date, expected rule version, idempotency key.

**Preconditions:** rule is draft; rule config validates; version is unique; effective-version policy has no prohibited overlap.

**State written:** rule status/effective fields.

**Shared operations:** `manageVersionedRules`, actor/authority, idempotency, concurrency, audit, outbox.

**Events/jobs:** `job_compliance.rule_activated`; enqueue affected-Job rescan only according to approved rescan policy.

**Failure modes:** invalid config, overlap/conflict, unauthorized, stale rule version, unresolved jurisdiction semantics.

### 10.5 `retireJobComplianceRuleVersion`

**Purpose:** end future applicability of an active rule version while preserving historical proof.

**Actor/context:** privileged rule administrator.

**Inputs:** rule ID, retirement effective time, reason, idempotency key.

**State written:** status/`retiredAt`.

**Effects:** audit, `job_compliance.rule_retired`, optional affected-Job rescan.

**Prohibition:** never rewrite historical checks/findings to the replacement rule version.

### 10.6 `disableJobComplianceRuleVersion`

**Purpose:** administratively disable a rule version from future use when retirement semantics are not appropriate.

**Actor/context:** privileged rule administrator.

**Inputs/state/effects:** same shared mechanics as retirement, with explicit disable reason in audit/event evidence.

**Prohibition:** disabling a rule cannot silently reclassify historical decisions.

## 11. Queries / Decisions

### 11.1 `evaluateJobCompliance`

**Consumers:** evaluation worker, Organization Hiring integration, contract tests.

**Input:** authoritative `JobComplianceInputDTO` with source version, canonical Job facts, normalized jurisdiction/context, trigger, and rule-resolution context.

**Result:** shared `DecisionResult` plus check/evidence references.

**Returns:** Job Compliance decision/evidence, not Job lifecycle.

**Stable decision values:** `allowed`, `warning`, `denied`, `review_required`, `unavailable`.

**Consumer must not infer:** `JobStatus`, Search eligibility, Trust Verification readiness, active holds, or candidate eligibility from this result alone.

### 11.2 `getJobPublicationComplianceDecision`

**Consumers:** Organization Hiring, authorized admin/review surfaces, Search only as an owner decision input where the Search contract requires it.

**Input:** `jobId`, optional expected source version.

**Result:** current effective Job Compliance `DecisionResult`, check ID, disclosure status, evidence refs, source/rule-set versions/fingerprint, evaluatedAt, and staleness indicator.

**Returns:** decision, not a Search projection.

**Must not infer:** a consumer may not treat an old allowed decision as valid after source version changes.

### 11.3 `getJobComplianceReport`

**Consumers:** authorized Organization Hiring UI, compliance reviewers/admins.

**Input:** actor context + Job/check ID.

**Result:** privacy-shaped rule/check/finding/disclosure evidence, review/override history references, and current decision.

**Returns:** evidence/read model.

**Must not infer:** possession of a Job/check ID does not grant permission; report access is separately authorized.

### 11.4 `getApplicableJobComplianceRequirements`

**Consumers:** Job editor guidance, compliance admin tooling, tests.

**Input:** normalized jurisdiction/context + relevant Job classification/employment facts.

**Result:** currently applicable Job Compliance rule keys/versions, required disclosure categories, review flags, and evidence references.

**Returns:** policy context; not a guarantee that a specific Job passes.

### 11.5 Stable reason-code namespace

The Module should expose owner-specific reason codes, not raw scanner/provider/library errors. Minimum categories:

- `JOB_COMPLIANCE_ALLOWED`
- `JOB_COMPLIANCE_ALLOWED_WITH_WARNING`
- `JOB_COMPLIANCE_BLOCKING_FINDING`
- `JOB_COMPLIANCE_REVIEW_REQUIRED`
- `JOB_COMPLIANCE_DISCLOSURE_REQUIRED_MISSING`
- `JOB_COMPLIANCE_DISCLOSURE_BLOCKED`
- `JOB_COMPLIANCE_JURISDICTION_UNRESOLVED`
- `JOB_COMPLIANCE_RULESET_UNAVAILABLE`
- `JOB_COMPLIANCE_STALE_SOURCE`
- `JOB_COMPLIANCE_SCANNER_FAILED`
- `JOB_COMPLIANCE_SUPERSEDED_CHECK`

Exact final vocabulary should be frozen in the public contract and versioned.

## 12. Public Module Interface

Other Modules should consume the following boundary instead of reading Job Compliance tables directly.

### Public commands

- `requestJobComplianceEvaluation`
- `reviewJobComplianceCheck`
- `overrideJobComplianceFinding`
- `publishJobComplianceRuleVersion`
- `retireJobComplianceRuleVersion`
- `disableJobComplianceRuleVersion`

### Public queries / decisions

- `evaluateJobCompliance`
- `getJobPublicationComplianceDecision`
- `getJobComplianceReport`
- `getApplicableJobComplianceRequirements`

### Emitted domain events

- `job_compliance.evaluated`
- `job_compliance.decision_changed`
- `job_compliance.review_required`
- `job_compliance.review_resolved`
- `job_compliance.evaluation_failed`
- `job_compliance.rule_activated`
- `job_compliance.rule_retired`
- `job_compliance.rule_disabled`

### Privacy executor

- `enumerateSubjectData` implementation for Job Compliance-owned records
- `executePrivacyInstruction` implementation for Job Compliance-owned records
- owner facts for `evaluateRetentionRequirement`

### Provider-facing interfaces

None owned at present. The scanner consumes shared scanner mechanics, not an external provider API owned by Job Compliance.

## 13. Inbound Dependencies

| Owning Module / capability | Public operation/interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | `resolveAuthenticatedActor` | establish trusted human/system actor | actor ID, actor type, assurance/session context | Yes for protected human actions | auth/session helpers |
| Role / Authority | `authorizeResourceAction` | authorize evaluation request, report read, review, override, rule admin | action, resource IDs, Organization owner facts, actor | Yes | org/admin role interpretation |
| Organization Hiring | `getOrganizationHiringContext` or approved Job Compliance input contract | authoritative Job/Organization facts and opaque source version | Job ID, org ID, status, version, text/structured fields required for compliance | Yes if missing/stale/ineligible | Job repository, Job lifecycle policy |
| Taxonomy & Classification | `resolveTaxonomyRequirements` / `validateTaxonomyAssignment` where rule applicability depends on taxonomy | accepted classification/context facts | canonical IDs and relevant requirement triggers | May force review/unavailable if required context cannot be resolved | taxonomy copies/hardcoded terms |
| Shared jurisdiction capability | `normalizeJurisdictionContext` (currently unresolved owner) | normalize country/state/city/remote evidence | normalized jurisdiction DTO + evidence/confidence | Yes for jurisdiction-dependent production rules | local geo normalization library as policy truth |
| Admin Review / Compliance Hold | `requestComplianceHold`, optionally `evaluateComplianceHold` for review context | request reusable admin stop sign when needed | target, reason, evidence refs, scope | Hold may block final publication, but final hold composition belongs Organization Hiring | local blocked table |
| Audit / Event Ledger | `appendAuditEvent` | privileged rule/review/override proof | actor, action, target, evidence refs, reason, correlation | Audit transaction policy may fail the privileged action | local AuditEvent |
| Notification | `requestNotification` only for Job Compliance-owned admin/review intent | alert reviewers/admins without owning delivery | safe template intent, recipients/recipient facts, Job/check IDs | Delivery failure must not rewrite compliance truth | email/SMS/push code |
| Privacy / Data Erasure | privacy target request/result protocol | execute legal instruction on owned records | subject/target/disposition, privacy IDs, idempotency | Yes for destructive action safety | PrivacyRequest/DataErasureJob |
| Observability / Ops | structured logging, queue telemetry, operational-failure interface | surface scanner/worker failures | correlation ID, safe error category, source refs | No business decision ownership | SystemEvent/IntegrationFailure tables |
| Shared platform | idempotency, queue/retry, outbox/inbox, locks/concurrency, canonical text/hash, versioning, scanner | durable/replay-safe execution | operation-specific payloads | Yes when unavailable; fail explicitly | local infrastructure copies |

### Trust Verification boundary

Job Compliance may need to know that a Job category/target has a verified-only requirement for report/context purposes, but it **does not evaluate candidate/person verification readiness**. The final Job publication composition may consume Trust requirements/readiness in Organization Hiring. Job Compliance must not import `VerificationCheck` rows or infer screening state.

## 14. Outbound Consumers and Effects

### Organization Hiring

Primary consumer. It receives Job Compliance decision/evidence and alone decides the corresponding `JobStatus` / `Job.complianceStatus` mirror update under the approved mapping.

Relevant event: `job_compliance.decision_changed`.

Job Compliance must not mutate Job rows directly.

### Search / Public Visibility

Search may consume owner-issued Job Compliance decision as one input to public readiness, but Organization Hiring remains the source owner responsible for requesting Job Search refresh/removal after applying the Job lifecycle decision.

Job Compliance does not write Typesense or `SearchUpsertEvent`.

### Admin Review / Compliance Hold

Admin/Hold workflows may consume `review_required`, findings, or evidence references. Job Compliance may request a hold for an administrative stop sign; Hold owns hold lifecycle.

### Notification

Job Compliance may request reviewer/admin notifications for review-required, rule-change, or review-resolution workflows. Organization Hiring should request organization-facing publication outcome notifications after applying the decision to Job state.

### Audit / Event Ledger

Privileged rule/review/override actions append generic audit proof. Automated evaluation proof remains primarily in Job Compliance records/events rather than a generic audit log.

### Observability / Ops

Consumes technical worker/scanner failure telemetry only. Ops records never become compliance decision truth.

## 15. Canonical Shared Operations Used

The supplied Canonical Shared Operations Architecture uses canonical operation names rather than SH-### identifiers. Those lowerCamelCase names are the identifiers used here.

| Canonical operation | Classification / owner | Why Job Compliance uses it | Invocation point | Local policy that remains Job Compliance-owned | Expected result | Prohibited duplicate names |
|---|---|---|---|---|---|---|
| `resolveAuthenticatedActor` | Platform capability — Identity & Access | trusted actor context | public human command/query entry | what Job Compliance action is attempted | typed actor context | `getCurrentUser`, `jobComplianceAuth`, `requireUser` |
| `authorizeResourceAction` | Cross-cutting capability — Role / Authority | reviewer/admin/org action authorization | before protected command/report read | action vocabulary + resource facts | typed allow/deny decision | `canReviewJob`, `canManageComplianceRules`, `jobPermission` |
| `queryOwnerFacts` | Shared contract; source owner implementation | obtain minimal Job/Organization facts | evaluation and authorization | which Job fields compliance needs | owner DTO with source version | cross-domain Prisma repository |
| `normalizeJurisdictionContext` | Cross-cutting capability — owner unresolved | jurisdiction-dependent rule input | before rule resolution | which jurisdiction evidence is sufficient | normalized jurisdiction DTO or validation failure | `stateRuleResolver`, local address normalizer |
| `buildCanonicalTextSnapshot` | Cross-cutting primitive | deterministic evaluation input | before hash/scanner | included Job fields and canonicalization version | normalized ordered snapshot | `jobTextBuilder`, `normalizeJobText` |
| `hashCanonicalPayload` | Platform cryptographic primitive | source/rule-set integrity and provenance | after canonicalization | what the hash proves | stable digest + purpose/version | `jobHash`, `sha256Helper` |
| `manageVersionedRules` | Shared mechanism; separate policy | version lifecycle/effective resolution | rule admin and evaluation | employment rule meaning, jurisdiction, severity | effective rule versions / transition result | generic Job Compliance rule engine |
| `runPatternScanner` | Shared scanner mechanism; policy owner unresolved | raw deterministic match generation | evaluation | employment interpretation/severity/decision | raw structured matches, offsets, scanner version | `eeocScanner`, `salaryScanner`, `nlpService` runtime |
| `returnDecisionResult` | Shared contract; separate policy | stable decision envelope | public decision queries | Job Compliance reason codes and precedence | allowed/denied/warning/review/unavailable + evidence | universal readiness engine |
| `executeIdempotentCommand` | Platform primitive | replay-safe commands | request, review, override, rule lifecycle | semantic key and replay result | claimed/existing result | local idempotency table/helper |
| `enqueueReliableJob` | Platform queue primitive | durable evaluation/rescan work | request and rule activation | job payload/meaning | durable job receipt | local queue client/framework |
| `executeRetryWithBackoff` | Platform queue primitive | retry transient scanner/dependency failures | worker | retryable vs permanent/review classification | retry/dead-letter outcome | custom retry loop |
| `acquireAggregateLock` / `withOptimisticConcurrency` | Platform persistence primitives | prevent stale/double updates | rule review/evaluation application | aggregate key/conflict semantics | lock/CAS result | in-memory mutex/ad-hoc lock table |
| `publishDomainEvent` | Platform outbox primitive | reliable owner event publication | source transaction | event names/payload/emission condition | outbox record/event ID | fire-and-forget event bus call |
| `deduplicateDomainEvent` | Platform inbox primitive | exactly-once domain effect at consumers/workers | event consumer | handler semantics | inbox claim/result | local processed-event table |
| `appendAuditEvent` | Audit capability | privileged action proof | rule/review/override/hold request | what action is auditable | AuditEvent reference | `jobAudit`, local audit table |
| `requestComplianceHold` | Hold capability | create reusable admin stop sign where policy calls for it | review/escalation | when compliance warrants hold request | hold command result | `jobComplianceBlock`, local hold flag |
| `requestNotification` | Notification capability | reviewer/admin notification intent | after committed owner event | safe message intent | notification request result | direct SES/SMS/push sender |
| `enumerateSubjectData` | Privacy protocol | declare owned subject data | Privacy fulfillment | local inventory mapping | stable target enumeration | local privacy workflow |
| `executePrivacyInstruction` | Privacy protocol | erase/anonymize/restrict/export/retain owned records | Privacy worker call | Job Compliance record mutation | standard privacy target result | local DataErasureJob |
| `evaluateRetentionRequirement` | Privacy protocol | determine whether proof must remain | before destructive mutation | compliance proof facts/minimum fields | retain decision facts for Privacy exemption | local retention-exemption table |
| `anonymizePersonalFields` | Cross-cutting privacy capability | scrub personal fields while preserving proof | approved privacy disposition | field map/invariants | anonymization result | custom global scrubber |

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
|---|---|---|---|---|---|
| `resolveApplicableJobComplianceRules` | select employment rules that apply to the source context | normalized jurisdiction, effective date, Job context | ordered applied-rule set | none directly | employment rule applicability is domain policy |
| `buildJobComplianceCanonicalInput` | define exactly which Job/compensation fields enter canonicalization | owner DTO | canonicalization field map | none | field inclusion carries Job Compliance meaning even though canonicalization mechanics are shared |
| `validateJobCompensationDisclosure` | evaluate pay/benefit disclosure | Job compensation facts, jurisdiction, rules | disclosure result + candidate findings | disclosure/check/finding | employment disclosure semantics are local |
| `classifyJobComplianceFinding` | translate raw scanner match into domain finding | raw match + rule/context | finding DTO | finding | severity/legal meaning cannot be generic scanner behavior |
| `deriveJobComplianceDecision` | combine local check/finding/disclosure evidence into DecisionResult | check/finding/disclosure proof | decision/reasons | decision view; may drive check review result | Job Compliance policy only |
| `determineJobComplianceReviewRequirement` | decide whether uncertainty needs human review | findings/rules/scanner confidence/context | yes/no + reason | check status | human review policy is local |
| `applyJobComplianceReviewResolution` | apply authorized review/override to local evidence | current check/findings + reviewer resolution | updated local evidence + decision | check/finding | review semantics remain local |
| `buildJobComplianceReport` | privacy-shape evidence for consumers | local records + actor scope | report DTO | none | exposure of compliance evidence is local |
| `identifyJobsAffectedByRuleChange` | derive rescan criteria from rule scope without owning Jobs | activated/retired rule | owner query criteria | none | affected-rule logic is local; actual Job facts come from Organization interface |

## 17. Shared Mechanism / Separate Truth Rules

1. **Versioning:** `manageVersionedRules` supplies immutable/effective-date mechanics; `JobComplianceRule` remains Job Compliance truth.
2. **Scanner:** `runPatternScanner` supplies tokenization/pattern matching; `JobComplianceFinding` type/severity/legal meaning remains Job Compliance truth.
3. **Canonicalization/hash:** shared primitives normalize/hash; the included Job fields and what the digest proves remain Job Compliance policy.
4. **DecisionResult:** result shape is shared; Job Compliance reason codes and decision precedence remain local.
5. **Idempotency:** shared claim/replay storage is platform truth; the semantic identity of an evaluation/review/rule command is Job Compliance-defined.
6. **Lifecycle plumbing:** shared state-transition helpers may validate generic mechanics; rule/check/finding transition graphs remain local.
7. **Events:** outbox/inbox mechanics are shared; Job Compliance owns event vocabulary and emission conditions.
8. **Audit:** AuditEvent is generic proof; JobComplianceCheck/Finding/Disclosure remain domain proof.
9. **Holds:** hold command/query mechanics are shared; Job Compliance owns why it requests a hold, Hold Module owns whether/how the hold exists.
10. **Privacy:** Privacy owns request orchestration/exemption records; Job Compliance owns how its fields are enumerated and safely mutated.

## 18. Authentication and Authorization

### Authenticated actor requirement

All human-facing mutations and non-public evidence reads begin with `resolveAuthenticatedActor`. Workers use a scoped trusted system actor/capability and carry original correlation/actor context when available.

### Role / Authority operations

Use `authorizeResourceAction`; do not hardcode organization or platform roles in route/actions.

Recommended Module action vocabulary for Role / Authority mapping:

- `job_compliance.evaluate.request`
- `job_compliance.report.read`
- `job_compliance.review.resolve`
- `job_compliance.finding.override`
- `job_compliance.rule.create`
- `job_compliance.rule.activate`
- `job_compliance.rule.retire`
- `job_compliance.rule.disable`

The action names belong to the resource owner; Role / Authority owns which roles/actors may perform them.

### Contextual facts supplied/consumed

Job Compliance consumes:

- Job → Organization relationship;
- Job source version;
- source lifecycle facts needed to decide whether an evaluation is meaningful;
- actor → Organization relationship facts for organization-requested evaluation/report viewing.

### Admin/support actions

Rule management, review, override, and broad compliance evidence access are privileged. There is no broad support/admin bypass simply because an ID is known.

### Step-up

No Job Compliance-specific step-up requirement is confirmed. If root security policy later classifies rule activation or legal override as step-up-sensitive, consume `requireStepUpForSensitiveAction`; do not create a local MFA flag.

## 19. Compliance / Readiness / Entitlement Gates

### Gate: Job posting compliance

- **Underlying truth owner:** Job Compliance.
- **Public query:** `evaluateJobCompliance` / `getJobPublicationComplianceDecision`.
- **Action gated:** Organization Hiring public Job publication.
- **Local composition:** Job Compliance evaluates only posting compliance evidence.
- **Result:** `DecisionResult`.

### Gate: reusable ComplianceHold

- **Underlying truth owner:** Admin Review / Compliance Hold.
- **Operation:** `evaluateComplianceHold` belongs to the final action owner, normally Organization Hiring for publication.
- **Job Compliance use:** may request a hold when a compliance review requires an administrative stop sign.
- **Resulting decision:** a hold may block publication but must not be encoded as `JobComplianceCheck.status` unless the Job Compliance evidence independently supports that status.

### Gate: Trust Verification requirement/readiness

- **Underlying truth owner:** Trust Verification / Screening.
- **Action gated:** verified-only/high-risk hiring behavior as defined by Organization Hiring/Trust policy.
- **Job Compliance role:** supporting posting evidence only; it does not evaluate candidate/person verification.

### Gate: entitlements

No candidate or professional Track entitlement is part of core Job Compliance evaluation. If a future organization commercial entitlement gates an advanced compliance-review feature, that remains unresolved under U-CL06-04 and must not be implemented as a local flag.

## 20. Provider Integrations

Job Compliance currently owns **no external provider integration**.

`compromise` and `natural` are implementation libraries for text analysis/scanning, not legal authorities and not Workin Ants source-of-truth providers. Their execution should sit behind the canonical `runPatternScanner` mechanism.

Required boundary:

```text
Job Compliance canonical input
→ shared scanner runtime
→ raw matches + offsets + scanner version
→ Job Compliance finding classification
→ Job Compliance check/findings/disclosure
```

Rules:

- no webhooks;
- no provider-event dedupe table;
- no external provider credentials in this Module;
- unknown scanner output maps to explicit unsupported/review/failure, never silent pass;
- scanner library errors are safe operational categories, not public reason strings;
- if a future jurisdiction/legal-rules provider is approved, architecture must first define the provider-neutral port, owner, status translation, reconciliation, privacy/deletion behavior, and whether Job Compliance owns the adapter.

## 21. Events and Outbox

### Event envelope

Use the canonical event envelope:

- event ID/type/schema version;
- source Module;
- aggregate type/ID/version;
- occurredAt;
- correlation/causation IDs;
- actor/system context;
- privacy classification;
- minimized payload.

### Emission rules

- emit only after source-of-truth transaction commits through the transactional outbox;
- do not put full Job description, matched text, private notes, or rule JSON in event payloads;
- include evidence references rather than copying findings;
- consumer side effects use transactional inbox dedupe.

### Event definitions

`job_compliance.evaluated`
- emitted after a durable evaluation record is committed;
- payload: job ID, source version, check ID, decision, reason-code summary, warning/block counts, disclosure status, rule-set proof ref/hash, evaluatedAt.

`job_compliance.decision_changed`
- emitted only when effective Job Compliance decision for the relevant Job source state changes;
- consumed primarily by Organization Hiring.

`job_compliance.review_required`
- emitted when evaluation cannot be finalized automatically and human review is required.

`job_compliance.review_resolved`
- emitted after authorized review/override commits.

`job_compliance.evaluation_failed`
- emitted after terminal technical failure is durably represented as `failed`/unavailable; operational details remain in Ops.

`job_compliance.rule_activated|retired|disabled`
- emitted after corresponding rule transition; may trigger rescan orchestration.

### Events are not commands

`job_compliance.decision_changed` states that a decision changed. It does not directly command Search to index or Organization Hiring to set a particular JobStatus. Consumers apply their own policy through their owner interfaces.

## 22. Background Jobs / Scheduled Work

### 22.1 Evaluation worker

**Purpose:** execute requested compliance evaluation durably.

**Input:** job ID, expected source version, trigger, idempotency/correlation IDs.

**Owner:** Job Compliance; queue mechanics shared.

**Idempotency key:** semantic key based on Job ID + source version + architecture-approved rule-set/canonicalization identity + trigger class. Exact fingerprint cannot be final until U-CL06-06.

**Retryable failures:** transient queue/dependency/scanner-runtime errors.

**Permanent/manual-review failures:** invalid Job input, unsupported/unresolved jurisdiction, invalid rule configuration, architecture-blocked rule semantics, unsafe scanner result.

**Business truth updated:** JobComplianceCheck, findings, disclosure, historical proof.

**Dead-letter/manual review:** terminal technical exhaustion creates explicit failed/unavailable proof and Ops reference; it does not approve or reject the Job.

**Telemetry:** job/check IDs, source version, durations, counts, safe error categories; no raw matched text.

### 22.2 Rule-change rescan/backfill worker

**Purpose:** re-evaluate Jobs affected by a newly activated, retired, or disabled rule according to explicit policy.

**Input:** rule key/version/scope + cursor/checkpoint.

**Owner:** Job Compliance for affected-rule semantics; Organization Hiring exposes Job source facts/query boundary; queue mechanics shared.

**Idempotency:** rule transition ID + Job source version.

**Retry:** technical failures only.

**Permanent failure:** source no longer eligible, unsupported context, unresolved architecture.

**Business truth:** new checks/evidence only. Never rewrite historical checks.

**Operational behavior:** checkpointed, resumable, observable, supports dry-run/report before mass production changes when policy requires.

### No periodic legal-rule scheduler is confirmed

Do not invent an external rule-feed poller or scheduled legal-update fetcher. Rule activation occurs through explicit admin/version lifecycle until architecture defines another source.

## 23. Concurrency and Idempotency

### Races to prevent

1. Job is materially edited while an evaluation is running.
2. Two identical publication/evaluation requests arrive concurrently.
3. Rule version is activated/retired while a check is resolving the applied set.
4. Two reviewers resolve the same check/finding concurrently.
5. Older evaluation result attempts to overwrite a newer disclosure/effective decision.
6. Rule-change backfill and user-triggered evaluation run against the same Job source version.

### Aggregate/resource keys

- evaluation: `job-compliance:evaluation:{jobId}:{sourceVersion}`;
- check review: `job-compliance:check:{checkId}`;
- finding override: `job-compliance:finding:{findingId}`;
- rule transition: `job-compliance:rule:{ruleKey}` or rule ID as appropriate.

These are semantic keys for shared locking/idempotency, not new database tables.

### Transaction boundaries

Evaluation commit should atomically persist:

- check;
- findings;
- compensation disclosure update tied to the same evaluation/source version;
- architecture-approved historical evaluation proof;
- owner domain event outbox entries.

Privileged review/override should atomically persist:

- local check/finding changes;
- outbox event;
- audit request/record according to the canonical audit transaction pattern.

### Strategy

- use `executeIdempotentCommand` for command replay;
- use `withOptimisticConcurrency` on mutable rule/check/finding/disclosure records;
- use `acquireAggregateLock` or database transaction/advisory lock for conflicting evaluation/rule operations when optimistic control is insufficient;
- do not use in-memory mutexes.

### Replay result

A replay with the same semantic request must return the original receipt/result or an equivalent stable reference, not create duplicate checks, findings, audits, holds, notifications, or events.

## 24. Media / Storage

Job Compliance owns no MediaAsset, attachment context, upload policy, signed URL, or file-storage lifecycle.

If future compliance evidence includes uploaded legal documents, architecture must first assign contextual ownership and Media integration. Do not add file upload/storage code to this Module based solely on convenience.

## 25. Search / Projection

### Source truth

Job Compliance source truth is the rule/check/finding/disclosure/evaluation-proof set.

### Module-owned projection

None.

### Search-owned projection

Search owns `SearchUpsertEvent`, Typesense documents, workers, reconciliation, and query APIs.

### Indexing trigger

The canonical flow is:

```text
Job Compliance decision changes
→ Organization Hiring consumes decision
→ Organization Hiring applies Job lifecycle/mirror
→ Organization Hiring evaluates remaining public-readiness gates
→ Organization Hiring requests Search refresh/removal
```

Job Compliance must not call Typesense directly.

### Search must not reconstruct

Search may not decide compliance by:

- counting findings;
- reading `JobComplianceCheck.status` directly;
- parsing Job text itself;
- interpreting rule JSON;
- trusting a stale `Job.complianceStatus` without source/decision version context.

It consumes the authoritative owner decision/public-readiness contract.

## 26. Notification

Job Compliance owns only business notification **triggers/intent** that arise from Job Compliance-owned events.

Appropriate examples:

- compliance review required;
- reviewer assignment/escalation where the review workflow requires notification;
- privileged rule activation/disable notice if product policy requires it;
- review resolution notification to authorized internal/admin actors.

Organization-facing publication success/failure/needs-changes notifications should normally be requested by Organization Hiring after it applies the Job Compliance decision to Job lifecycle.

Payloads must contain safe Job/check references and high-level reason/remediation categories. Do not include full matched text, protected-class phrases, rule JSON, or private review notes in push/SMS/email payloads.

Notification owns delivery mechanics and failure truth.

## 27. Audit and Sensitive Access

### Module domain proof

- `JobComplianceCheck`
- `JobComplianceFinding`
- `JobCompensationDisclosure`
- historical rule/source evaluation proof required by U-CL06-06

These records explain the Job Compliance decision.

### Generic AuditEvent

Use `appendAuditEvent` for privileged human actions such as:

- rule create/activate/retire/disable;
- manual review resolution;
- finding override;
- administrative hold request/release request initiated by this Module;
- access to particularly sensitive admin evidence if root policy classifies it as auditable.

### AccessAuditLog

No Job Compliance-specific sensitive-access action is currently confirmed. If matched-text/report access is classified as sensitive under root policy, use `recordSensitiveAccess`; do not create a local access log.

### Separation rule

AuditEvent does not replace Job Compliance evidence. A JobComplianceFinding does not replace AuditEvent for privileged override. Ops logs replace neither.

## 28. Privacy and Retention

### Subject-data inventory

Potential personal data in Job Compliance-owned records includes:

- `reviewedByUserId`;
- review/override reasons if they contain names or personal commentary;
- `matchedText` / snippet previews that may incidentally contain personal data;
- compensation/benefit descriptions that may accidentally contain personal details;
- timestamps and actor-linked Audit references.

`JobComplianceRule` normally contains policy configuration rather than subject data.

### Privacy executor

Job Compliance must implement the Privacy-defined `enumerateSubjectData` and `executePrivacyInstruction` contracts for its own records only.

### Retention

The supplied evidence does not define a final legal retention period for Job Compliance proof. Therefore:

- do not hard-delete compliance proof by default;
- call/participate in `evaluateRetentionRequirement`;
- Privacy owns any `DataRetentionExemption` record;
- retained data must be minimized to the least fields required by the approved basis.

### Proposed local disposition mapping

Subject to retention approval:

- reviewer user reference may be detached/anonymized when no longer required;
- raw matched text / preview may be scrubbed while preserving matched-text hash, rule/version, jurisdiction, type/severity, and non-personal evidence when that satisfies the approved retention basis;
- rule configuration is retained as policy history unless separately governed;
- checks/findings/disclosure may be retained, anonymized, restricted, or erased only under the approved Privacy instruction and retention decision.

### Export contribution

Return privacy-safe, comprehensible Job Compliance evidence related to the subject when Privacy requests export. Do not include unrelated organization or other actors’ private information.

## 29. Observability

Use the canonical request/correlation context and shared observability stack.

### Structured log dimensions

Safe dimensions may include:

- module = `job_compliance`;
- command/query/worker name;
- Job ID/check ID/rule key/version where not sensitive;
- source version/hash reference;
- decision category;
- finding counts by type/severity;
- duration;
- retry count;
- safe error category;
- correlation/request ID.

### Prohibited telemetry

Do not log or emit to analytics:

- full Job description solely for debugging;
- full matched text;
- protected-class phrases beyond an approved minimal preview;
- private review notes;
- secrets/tokens;
- raw provider/library payloads;
- unnecessary user data.

### Operational records

Scanner/queue/dependency failures may create/reference `SystemEvent`, `IntegrationFailure`, `QueueJob`, or incident records through Ops-owned interfaces. These records never change the compliance outcome by themselves.

### Metrics

Recommended metrics:

- evaluations requested/completed by outcome;
- warning/block/review rate;
- scanner technical failure rate;
- queue latency and evaluation duration;
- stale-source rejection rate;
- review queue age;
- rule-version rescan backlog/completion;
- decision-change count after material edit/rule change.

## 30. Security Boundaries

1. Runtime-validate all public command/query payloads with the platform’s approved validation approach.
2. Never trust client-supplied Job/Organization IDs as authority proof.
3. Use owner-issued source version and Job facts through Organization Hiring’s public interface.
4. Use Role / Authority for all human mutations and restricted evidence reads.
5. Keep rule administration and review server-side.
6. Use canonical hashing; do not build custom cryptography.
7. Minimize matched text; prefer hash + approved preview.
8. Do not expose rule JSON or private review notes unnecessarily to organization users.
9. Use idempotency for retryable commands and workers.
10. Use database-backed concurrency primitives; no in-memory locks.
11. Scanner libraries receive only the canonicalized fields necessary for the evaluation.
12. Technical scanner errors must be sanitized before crossing the Module public boundary.
13. No provider/webhook secrets exist here unless future architecture explicitly adds an owned provider.
14. Rate-limit externally reachable evaluation/report endpoints through platform controls where abuse could create excessive scanner/queue work.
15. Unresolved jurisdiction/rule semantics fail to review/unavailable, never allowed.

## 31. Error / Decision Result Pattern

### Command/query error categories

Use stable categories such as:

- `validation_error`
- `unauthenticated`
- `unauthorized`
- `not_found`
- `conflict`
- `stale_source`
- `invalid_transition`
- `architecture_blocked`
- `dependency_unavailable`
- `retryable_failure`
- `terminal_failure`

### DecisionResult

Use the canonical shared decision envelope:

```text
decision:
  allowed | denied | warning | review_required | unavailable
reasonCodes:
  Job Compliance-owned stable codes
humanSafeExplanation:
  optional safe summary
warnings:
  structured safe warnings
evidenceRefs:
  check/finding/disclosure/rule-set references
evaluatedAt:
  timestamp
policyVersion / ruleSetVersion:
  explicit proof reference
sourceVersion:
  owner-issued source version
retryable:
  boolean
nextAction / remediation:
  safe machine-readable guidance
```

Do not return raw `compromise`/`natural` errors, stack traces, rule JSON, or matched text in the generic decision envelope.

## 32. Testing Architecture

### Domain unit tests

- rule applicability by jurisdiction/effective date/context;
- pay-transparency/disclosure mapping;
- finding type/severity classification;
- review-required policy;
- decision precedence;
- reason-code stability;
- stale/superseded decision behavior;
- matched-text minimization.

### Lifecycle/state tests

- rule draft/active/retired/disabled matrix;
- needs_review → final check transitions;
- terminal check behavior;
- finding override/resolution behavior;
- disclosure status transitions.

### Public contract tests

- `evaluateJobCompliance` DecisionResult shape;
- Organization Hiring Job input/source-version DTO;
- report privacy shaping;
- event envelope versions;
- Privacy target result contract.

### Database/integration tests

- unique rule key/version;
- check/findings transaction;
- one disclosure per Job;
- stale evaluation cannot overwrite newer disclosure;
- approved historical rule/source proof once U-CL06-06 is resolved;
- outbox atomicity.

### Authorization tests

- organization actor evaluation/report access;
- privileged review/override/rule admin;
- cross-organization denial;
- worker/system actor scope;
- RLS/server authorization parity where applicable.

### Compliance tests

At minimum:

- compensation missing/invalid;
- benefits/commission disclosure cases represented by current finding vocabulary;
- salary-history language;
- Fair Chance/criminal-history language;
- age/gender/race-national-origin/disability/religion-related rule cases;
- immigration/citizenship wording;
- protected-class and overly broad proxy findings;
- uncertain scanner match routes to review;
- zero-finding pass records all applied rules after U-CL06-06 resolution;
- identical source+rule versions reproduce the same result.

### Idempotency/concurrency tests

- duplicate evaluation request;
- simultaneous evaluation workers;
- Job edit during evaluation;
- review/override race;
- rule transition during evaluation;
- backfill versus user-triggered evaluation.

### Worker tests

- retryable scanner/dependency failure;
- permanent invalid-input failure;
- retry exhaustion and dead-letter visibility;
- checkpointed rule-change rescan;
- replay after worker crash.

### Privacy tests

- subject enumeration;
- anonymize/detach reviewer identity when instructed/allowed;
- matched-text scrubbing under approved policy;
- retention-required result references Privacy-owned exemption;
- idempotent privacy rerun;
- no false completion after partial failure.

### Cross-Module integration tests

- no Job becomes publicly searchable before Organization Hiring has applied an allowed Job Compliance decision;
- Job Compliance never writes Job lifecycle directly;
- material Job edit makes old decision stale;
- Search cannot reconstruct compliance locally;
- ComplianceHold stays externally owned;
- Trust Verification/candidate screening remains separate.

### E2E participation

Critical CL-06 journey participation:

```text
Organization Job draft
→ publication request
→ Job Compliance evaluation/review if needed
→ Organization Hiring applies decision
→ public Job only when remaining gates pass
```

## 33. Module Invariants

### Rules coding agents must never violate

1. Job Compliance owns posting rules/checks/findings/disclosure policy; it does not own the Job lifecycle.
2. Job Compliance never directly sets `Job.status`, `Job.visibility`, or Search projection state.
3. Job Compensation business truth remains Organization Hiring-owned; disclosure is compliance proof.
4. `Job.complianceStatus`, if retained, is not an independent Job Compliance policy engine.
5. `CompensationPeriod` is not duplicated; its structural owner remains blocked by U-CL06-07 until ruled.
6. Candidate screening, `VerificationCheck`, and FCRA adverse action never move into this Module.
7. General moderation findings/cases never move into this Module merely because text scanning is similar.
8. Every production evaluation is tied to an authoritative Job source version.
9. Every production decision is tied to the exact applied rule set; zero-finding pass still has rule proof.
10. Active rule meaning is immutable; policy change creates a new version.
11. All relevant Job text/structured surfaces required by policy are included in canonical input.
12. Technical scanner/runtime failure never means approved or legally rejected.
13. Unknown jurisdiction/rule applicability never silently passes.
14. Raw scanner matches are not final legal decisions; Job Compliance classifies them.
15. `needs_review` is first-class and only an authorized reviewer resolves it.
16. Override never deletes original finding/provenance.
17. Privileged review/override/rule transitions are authorized and audited.
18. Matched text is minimized and excluded from normal logs/events/notifications.
19. Generic idempotency, queue, retry, locking, hashing, canonicalization, scanner, outbox/inbox, audit, notification, hold, and privacy infrastructure are consumed, not rebuilt.
20. Search consumes a decision; it does not count findings or parse Job text to infer compliance.
21. Routine compliance block/review is not implemented as a local ComplianceHold clone.
22. Old evaluations may not overwrite evidence/decision for a newer Job source version.
23. Retried commands/workers do not duplicate checks, findings, events, audits, holds, or notifications.
24. Privacy owns privacy orchestration and retention exemption records; this Module mutates only its own records.
25. Ops records are diagnostic, not compliance source truth.
26. No external legal/provider integration is introduced without an architecture update.
27. Production Job publication does not proceed until U-CL06-05/06/07 are resolved and reflected in architecture.

## 34. Prohibited Duplicate Implementations

Do not create any of the following inside `src/modules/job-compliance`:

- `authHelper.ts`, `getCurrentUser.ts`, `requireUser.ts`, `jobComplianceAuth.ts`;
- `canPublishJob.ts`, `canReviewJob.ts`, `orgJobGuard.ts`, local role matrices;
- `jobRepository.ts` that writes Organization Hiring-owned `Job` rows;
- `complianceHold.ts`, `jobBlocked.ts`, `jobBlockService.ts`, or local blocked/hold tables;
- `typesenseJobService.ts`, `jobIndexer.ts`, direct Typesense client, local `SearchUpsertEvent`;
- `sendComplianceEmail.ts`, SES/SMS/push clients, notification retry code;
- `auditLogger.ts`, local `AuditEvent`/`AccessAuditLog` models;
- `privacyRequestService.ts`, local erasure-job/exemption models;
- `queue.ts`, `retry.ts`, `deadLetter.ts`, or local QueueJob system;
- `idempotency.ts`, local idempotency table;
- `mutex.ts`, in-memory locks, local generic lock table;
- `sha256.ts`, `jobHash.ts`, local crypto helper;
- `textNormalizer.ts`, `jobTextBuilder.ts` implementing canonicalization mechanics;
- `eeocScanner.ts`, `fairChanceScanner.ts`, `salaryScanner.ts` as independent scanner runtimes bypassing `runPatternScanner`;
- a generic `ruleEngine.ts` that owns non-Job policy;
- a universal `complianceGate.ts`/`hiringReadinessEngine.ts` that absorbs Hold/Trust/Authority/Search policy;
- candidate background-check or Checkr/Certn clients;
- ModerationCase/Report logic;
- permanent copied Job text solely for debugging;
- a provider webhook/dedupe table without an approved provider owner decision.

## 35. Unresolved Decisions

### U-CL06-05 — Job Compliance effective decision

**Question:** what is the binding source/precedence across Job Compliance check, compensation disclosure, Job summary mirror, and ComplianceHold; how do warning and failed map?

**Blocks:** production Job publication.

**Proposed Ruling PR-JC-01:**

1. Job Compliance effective decision is derived only from current owned Job Compliance evidence for the authoritative Job source version: check + findings + disclosure + approved review/override.
2. `ComplianceHold` is a separate final publication gate owned/evaluated outside Job Compliance, normally by Organization Hiring; Job Compliance may request a hold but does not fold hold truth into its check status.
3. `Job.complianceStatus` is an Organization Hiring-owned summary mirror of the returned decision, not a source for Job Compliance policy.
4. `passed` → `allowed` when disclosure is non-blocking.
5. `warning` → `warning`/allowed-with-warning when no blocking/review condition exists.
6. `blocked` → `denied`.
7. `needs_review` → `review_required`.
8. `failed` → `unavailable`, never approved/rejected.
9. `required_missing`/`blocked` disclosure contributes denial; `provided_with_warning` contributes warning; unresolved jurisdiction contributes review/unavailable.

This proposal is not binding until approved and reflected in CL-06/root context.

### U-CL06-06 — Historical rule-set/source proof

**Question:** how does a zero-finding result prove which rules and exact source state were evaluated after later changes?

**Blocks:** legal-grade reproducibility and Cluster Feature 02 exit gate.

**Proposed Ruling PR-JC-02:** Job Compliance should own immutable evaluation proof attached to each check, sufficient to preserve source version/canonical input identity, canonicalization version, normalized jurisdiction context, every applied rule key/version, rule-set fingerprint, scanner version, and compensation-disclosure evaluation identity. The exact schema may be a check-attached snapshot plus applied-rule rows or an equivalent normalized design. The model/field names, retention, and whether exact canonical text is stored or referenced must be explicitly approved before migration.

### U-CL06-07 — `CompensationPeriod` ownership and `EmploymentType.contract`

**Question:** who structurally owns compensation-period vocabulary and what does `contract` mean?

**Blocks:** final employment/compliance semantics.

**Proposed Ruling PR-JC-03:** because compensation period is part of the Organization Hiring-owned Job offer and Job Compliance merely evaluates/snapshots it, Organization Hiring should be the structural owner of `CompensationPeriod`; Job Compliance consumes the canonical enum and copies the value into compliance proof. `EmploymentType.contract` must remain opaque until its employment-law/business meaning is separately approved.

### Finding-field duplication

`fieldName` vs `sourceField`, `matchedText` vs `matchedSnippetPreview`, and `suggestedText` vs `suggestedReplacement` require a schema cleanup/semantic ruling before new code relies on both variants.

### Review history proof

Current schema has mutable review/override fields but no dedicated immutable Job Compliance review/event record. Decide whether generic AuditEvent + domain outbox is sufficient for legal-grade review history or whether a Module-owned immutable review/event record is required.

### Retention periods

No final Job Compliance proof-retention schedule is supplied. Privacy disposition must remain retention-policy driven.

### Jurisdiction capability owner

`normalizeJurisdictionContext` is canonical but its platform owner is unresolved. Job Compliance must consume the approved shared interface rather than become its de facto platform owner.

## 36. Architecture Decision Summary

### Binding rulings

- Job Compliance is the source owner for Job posting rules, checks, findings, compensation-disclosure proof, and posting-compliance policy.
- Organization Hiring owns `Job` lifecycle and offered compensation truth.
- Job Compliance returns a decision; it does not directly publish, open, close, reject, pause, or index Jobs.
- Search owns projection execution and must not reconstruct Job Compliance.
- Trust Verification owns person/candidate screening and FCRA adverse-action truth.
- Content Moderation owns general moderation truth.
- ComplianceHold is externally owned reusable stop-sign truth.
- Audit owns generic audit; Job Compliance records remain domain evidence.
- Privacy owns privacy orchestration; Job Compliance implements an owner executor only.
- Scanner libraries are not legal authority or source truth.
- Canonical text/hash/scanner/version/idempotency/queue/retry/concurrency/event mechanisms are shared and must not be duplicated.
- Technical evaluation failure is not an approval or legal rejection.
- Production Job publication is blocked until U-CL06-05/06/07 are resolved.

### Proposed rulings awaiting approval

- PR-JC-01 effective decision/mirror/hold separation and warning/failed mapping.
- PR-JC-02 immutable historical evaluation proof requirement and shape category.
- PR-JC-03 Organization Hiring as structural owner of `CompensationPeriod`.

## 37. Coding-Agent Usage

Before implementing any Job Compliance feature, the coding agent must read, in order:

1. root `project-overview.md`;
2. root Workin Ants `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry / Architecture;
5. CL-06 `architecture.md`;
6. CL-06 `build-plan.md`;
7. this `job_compliance/module-architecture.md`;
8. `job_compliance/implementation-plan.md`;
9. public-interface sections for Organization Hiring, Role / Authority, Taxonomy, Holds, Audit, Notification, Privacy, Search, and Ops as relevant to the feature;
10. progress tracker;
11. current Prisma schema/migrations;
12. the architecture decision records resolving U-CL06-05/06/07 and any later blockers relevant to the feature.

Before coding, confirm the prior numbered feature’s exit gate and write the required feature implementation specification. If implementation discovers a binding ownership/schema/lifecycle/public-contract change, stop and update architecture before continuing.
