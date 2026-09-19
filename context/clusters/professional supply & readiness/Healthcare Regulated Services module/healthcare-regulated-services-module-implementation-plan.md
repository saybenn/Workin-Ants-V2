# Healthcare / Regulated Services Module Implementation Plan

> **Module ID:** `healthcare_regulated_services`  
> **Module name:** Healthcare / Regulated Services Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Repository target:** `context/clusters/professional supply & readiness/Healthcare Regulated Services module/healthcare-regulated-services-module-implementation-plan.md`\
> **Architecture dependency:** `context/clusters/professional supply & readiness/Healthcare Regulated Services module/healthcare-regulated-services-module-architecture.md`\
> **Cluster sequence dependency:** `context/clusters/professional supply & readiness/professional-supply-readiness-build-plan.md`\
> **Plan status:** Ordered Module implementation roadmap; subordinate to root and Cluster architecture

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

## Core Principle

Implement Healthcare through narrow, owner-preserving, verifiable slices:

```text
public / observable behavior
→ validated command or query
→ Healthcare-owned domain policy
→ authoritative Healthcare write/read
→ canonical shared-operation calls
→ owner event / audit / notification / provider effect
→ tests
→ exit gate
```

The Module does not need artificial UI. A valid vertical slice may terminate in SH-020, a persisted Healthcare lifecycle, a restricted admin decision, a provider-neutral adapter contract, a worker result, a privacy executor, or a cross-Module contract test.

This Module plan narrows **CL-03 Feature 06 — Healthcare Lane, BAA, Data Boundaries, and Admin Payload Policy**, then participates in CL-03 Feature 11 integration, Feature 12 governance/privacy, and Feature 13 hardening. It must not independently reorder or redefine the Cluster plan.

## Build Rules

1. Follow root Workin Ants architecture, code standards, Canonical Shared Operations, CL-03 architecture, and the Module architecture.
2. Healthcare owns only `HealthcareComplianceProfile`, `BaaAgreement`, `HealthcareDataBoundary`, `HealthcareAdminAccessPolicy`, healthcare-owned policy/events, and any later explicitly approved Healthcare provider-event record.
3. Consume foreign truth through public contracts; do not import foreign repositories as the default integration pattern.
4. Reuse canonical SH operations by ID. Do not create local auth, authorization, audit, queue, idempotency, storage, Search, Notification, Privacy, or hold systems.
5. All external inputs are validated server-side.
6. Every mutation resolves actor/system context as required, authorizes through the owner boundary, validates expected owner state, and uses transaction-safe concurrency/idempotency semantics.
7. Provider details stay behind a Healthcare-owned provider-neutral BAA/e-sign port and approved adapter.
8. Provider callbacks are not enabled for production side effects until signature verification, owner-specific dedupe truth, status translation, legal proof requirements, and reconciliation are all satisfied.
9. Domain/provider/job side effects are idempotent and replay-safe.
10. A `HealthcareComplianceProfile` summary must not become a second BAA lifecycle.
11. Resource owners enforce Media/Message/Video/Booking/Order mechanics. Healthcare returns policy/decision only.
12. Search remains projection; Healthcare never calls Typesense or writes Search queue rows directly.
13. Privacy remains Privacy-owned; Healthcare implements only owner-specific enumeration/execution/retention facts.
14. `ComplianceHold` remains the reusable stop sign; no local generic blocked flag is introduced.
15. Generic Audit/Ops records never replace Healthcare source truth or provider-event truth.
16. Unresolved architecture is surfaced as an explicit unsupported/review result. Never infer the missing legal/provider/lifecycle answer.
17. Every numbered feature ends with required tests and an exit gate. Do not start the next feature until the prior gate passes.
18. If a feature settles a binding unresolved decision, update Module and Cluster architecture before or in the same change as implementation.
19. Do not add a production claim of HIPAA/HITECH/BAA legal completeness from architecture evidence alone; legal-gated paths remain gated until required rulings/review exist.
20. Do not add a UI unless a real professional/admin workflow requires it; APIs, decisions, workers, and contract tests are acceptable observable results.

## Preconditions

### Hard platform dependencies

These must exist before a production path relies on them. A feature may contract-test against a stub only when the dependency is not yet live and no source ownership is copied locally.

- root Prisma/PostgreSQL data access and transaction conventions;
- Zod/server validation conventions from code standards;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-046 `publishDomainEvent` transactional outbox before downstream correctness depends on an event;
- root concurrency primitives / SH-051/052/053 as used by the feature;
- SH-029/030 Audit interfaces before production admin/sensitive access is claimed;
- SH-034 safe telemetry before provider/admin sensitive paths are enabled.

### Hard owner-interface dependencies for CL-03 Feature 06

- Professional Eligibility Feature 01 `getProfessionalProfileContext` or equivalent owner facts contract;
- Marketplace Supply Feature 02 `getOfferingEligibilityContext` where Offering context is evaluated;
- CL-03 Cluster Feature 03 / Professional Eligibility local Feature 02 readiness composition consuming SH-020, or a stable contract double for it (CL-03-R022);
- Taxonomy SH-022 `resolveTaxonomyRequirements`;
- Consent SH-008 where a healthcare disclosure/consent proof is required by the approved feature path;
- SH-123 target-owner validation before writing polymorphic boundaries/policies;
- Media safe ready-asset/signed-access interface for BAA/evidence files that the feature exposes;
- Audit SH-030 for access decisions that must create proof.

### Hard dependencies before later features

- SH-047/048 and SH-055 before scheduled BAA expiry/reconciliation is production-enabled;
- SH-059/060/061/062 before live provider callback/reconciliation;
- Healthcare-owned provider-event schema approved by U-08 before live webhook side effects;
- U-07 immutable BAA proof/legal semantics before final production e-sign claim;
- Privacy SH-095/096/097/098 before production privacy fulfillment is claimed;
- Notification SH-041 before actual cross-channel notices are enabled;
- source-owner/Search SH-091 contract before public projection changes are integrated.

### Dependencies that may initially be stubbed behind contracts

- BAA/e-sign provider: manual/provider-neutral BAA path may proceed; live callback remains disabled.
- Search: source-owner event/refresh contract may be stubbed until CL-03 Feature 11.
- Notification: event intent may be contract-tested before provider delivery exists.
- Video/Media/Messaging/Booking resource owners: owner-fact/handling interfaces may be test doubles until cross-cluster integration phase.
- Privacy: executor contract may be written before the cross-cluster orchestrator is live, but production privacy claims wait for integration.

### Architecture blockers carried into this plan

- U-07 — immutable BAA parties/signers/document/version/hash proof.
- U-08 — BAA provider selection + Healthcare-owned provider-event dedupe truth.
- U-09 — boundary retirement/clear/inheritance.
- U-10 — access-policy version/history/precedence.
- U-11 — `blocked` versus `denied` semantics.
- U-12 — generic `DataSensitivity` ownership/derivation.
- U-18 — exact healthcare/BAA retention periods.
- U-HC-01 — effective/current BAA selection.
- U-HC-02/U-HC-03 — complete profile and BAA transition graphs.
- U-HC-04 — `lockedHealthcareFlag` meaning.
- U-HC-05 — BAA document relation/snapshot design.
- U-HC-06 — provider capability facts source.
- U-HC-07 — Healthcare step-up matrix.
- U-HC-08 — redaction instruction contract.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 — Healthcare Contracts, Repositories, and Ownership Guardrails

### Objective

Create the Module's typed internal/public boundaries and owner-only persistence layer so later Healthcare behavior can be built without cross-Module Prisma access or shared-operation duplication.

### Observable Result

- The repository exposes typed Healthcare contracts for profile context, SH-020, BAA lifecycle commands, exact boundary/policy operations, owner events, and Privacy executor participation.
- Healthcare repositories read/write only the four confirmed Healthcare-owned models.
- Dependency ports exist for Professional Eligibility, Marketplace Supply, Taxonomy, Consent, Media, Audit, Hold, Notification, Privacy, Search/source owners, Ops, and target-owner validation without implementing those owners.
- A contract test fails if a Healthcare repository attempts to become a generic cross-domain repository.

### Cluster Build-Plan Link

Supports **CL-03 Feature 06** prerequisites and establishes the boundary required by Feature 06's public interfaces. It does not complete Feature 06 by itself.

### Dependencies

- Module architecture accepted.
- Current Prisma schema available.
- Root folder/code standards.
- Canonical Shared Operations Registry.
- CL-03 Feature 01/02 public owner-facts contracts may initially be interface stubs.

### In Scope

- Module folder structure actually needed for application/domain/contracts/repositories/tests.
- Zod input schemas for externally reachable Healthcare command/query DTOs.
- Repository interfaces and Prisma implementations for:
  - `HealthcareComplianceProfile`;
  - `BaaAgreement`;
  - `HealthcareDataBoundary`;
  - `HealthcareAdminAccessPolicy`.
- Typed target reference based on `HealthcareDataBoundaryTargetType`.
- Public SH-020 contract type and stable base error/decision categories.
- Dependency port interfaces, not implementations, for foreign owners.
- Healthcare event schema definitions with version fields, without yet emitting every event.
- Test fixtures with synthetic/non-PHI data.

### Out of Scope

- Healthcare lane business transitions;
- BAA legal/e-sign implementation;
- provider adapter/webhook;
- boundary retirement/inheritance;
- admin policy version history;
- actual Search/Notification/Privacy integration;
- UI;
- any new owner schema not approved by architecture.

### Module-Owned Data

No new source-of-truth model. The four Healthcare models and owned enums are declared in Prisma; that does not establish deployability from checked-in migrations. Apply the CL-03-R016 migration-baseline prerequisite. Additional feature-specific index/constraint changes require architecture-compatible review; this reconciliation makes no migration change.

### Public Interfaces

Define typed signatures for:

- `getHealthcareComplianceContext`;
- SH-020 `evaluateHealthcareReadiness`;
- `declareHealthcareLane`;
- BAA lifecycle commands as **declared but feature-gated** until Feature 03;
- `markHealthcareDataBoundary`;
- `getHealthcareDataBoundary`;
- `resolveEffectiveHealthcareBoundary` with current exact-target-only capability;
- `setHealthcareAdminAccessPolicy`;
- `getHealthcareAdminAccessPolicy`;
- `evaluateHealthcareAdminAccess`;
- privacy executor contract.

Do not expose a generic `setHealthcareStatus(status)`.

### Shared Operations Used

- **SH-001 / Identity & Access:** define actor-context dependency at public entry points. Local policy: action name/required actor. Prohibited duplicate: `healthcareAuth.ts`.
- **SH-002 / Role & Authority:** define authorization dependency. Local policy: Healthcare resource/action facts. Prohibited duplicate: local RBAC.
- **SH-020 / Healthcare:** define the canonical readiness contract this Module owns.
- **SH-044 / platform:** establish idempotency contract for future commands. Local policy: command fingerprint. Prohibited duplicate: local idempotency table.
- **SH-046 / platform:** establish owner-event publisher port. Local policy: Healthcare event schema. Prohibited duplicate: local emit-after-write bus.
- **SH-123 / target owners:** establish validated target-reference contract. Local policy: supported Healthcare target types. Prohibited duplicate: generic cross-domain repository.

### Domain Logic

- No business decision beyond validation of enum/target shapes.
- Public result types must separate validation/auth/conflict/policy/dependency errors.
- `DataSensitivity` is treated as referenced vocabulary, not owned truth.
- `lockedHealthcareFlag` is surfaced only as an existing database field in repository mapping if required; no policy may read it.
- `documentMediaId` is treated as opaque Media reference until U-HC-05 is resolved.

### Authorization / Compliance

- No public protected handler may bypass SH-001/002 dependency contracts.
- Test DTOs/events/log fixtures contain no PHI.
- Do not imply legal sufficiency of BAA records from current fields.

### Database / Transaction Behavior

- Repositories enforce owner-only table access.
- Use current unique constraints as invariants.
- No cross-Module joins in repository methods.
- Repository methods that later participate in multi-row transitions accept a transaction context per root data-layer standard.

### Events / Jobs

Define event schemas; no background workers required.

### Provider Integration

None. Define no concrete provider client.

### UI / Admin Surface

None.

### Failure Behavior

- Unsupported target type: validation error before DB access.
- Foreign target data required: dependency contract invocation; do not fall back to Prisma.
- Unknown SH-020 reason: compile/test failure rather than free-form provider text.

### Tests

- unit: Zod/request contracts and reason-code schemas;
- repository integration: owner models only, uniqueness/error mapping;
- architecture guard test or import-boundary lint: no foreign Module repository/Prisma model access in Healthcare repositories;
- contract compile tests for SH-020 and target validation;
- telemetry fixture tests reject prohibited PHI-like payload fields where the root test utilities support it.

### Documentation Updates

- Record exact public type names in Module architecture if implementation naming differs.
- Do not resolve U-* items merely by choosing a code shape.

### Acceptance Criteria

1. All four owner repositories exist and are test-covered.
2. Foreign facts are represented only as dependency contracts.
3. SH-020 has a typed provider-neutral/public-safe result shape.
4. No generic status setter, generic target repository, local auth/RBAC/audit/queue/Search/storage service exists.
5. Architecture/import-boundary tests pass.

### Exit Gate

Run the repository's typecheck/lint/test commands plus Healthcare contract/repository tests. Feature 02 may begin only when the Module can be instantiated in tests with dependency doubles and no direct foreign data access.

---

## 02 — Healthcare Lane Declaration and Baseline SH-020 Readiness

### Objective

Implement one-to-one healthcare lane declaration and a baseline Healthcare-owned readiness decision that correctly distinguishes non-healthcare, missing/pending profile, and explicitly supported healthcare states without inventing BAA/provider semantics.

### Observable Result

- An authorized professional/admin/system workflow can idempotently create or obtain one `HealthcareComplianceProfile` for a ProfessionalProfile.
- Healthcare applicability is resolved from canonical Taxonomy/Offering/profile/explicit-boundary context rather than a User flag.
- SH-020 returns deterministic current decisions for supported baseline states.
- A non-healthcare context does not force BAA/provider workflows.

### Cluster Build-Plan Link

Implements the first half of **CL-03 Feature 06**: healthcare-sensitive context identification, HealthcareComplianceProfile existence, and the base SH-020 boundary consumed by CL-03 Feature 03.

### Dependencies

- Module Feature 01.
- CL-03 Feature 01 ProfessionalProfile context.
- CL-03 Feature 02 Offering eligibility context where Offering action is evaluated.
- SH-022 Taxonomy requirements.
- SH-001/002.
- SH-044/046.
- U-HC-02 transition graph may remain unresolved because this feature implements only supported creation/declaration baseline and no restore/reopen behavior.

### In Scope

- `evaluateHealthcareRequirement` for canonical supported triggers.
- `declareHealthcareLane` with one-to-one provisioning.
- `getHealthcareComplianceContext` safe summary.
- baseline SH-020 implementation using:
  - requirement applicability;
  - current Healthcare profile status;
  - exact boundary when the requested action requires it;
  - BAA placeholder dimension that reports missing/pending/unsupported without guessing effective BAA rules.
- `HealthcareComplianceProfileChanged.v1` and `HealthcareReadinessChanged.v1` emission for supported state changes.

### Out of Scope

- arbitrary profile status transitions;
- BAA lifecycle mutations;
- provider calls;
- boundary inheritance/clear;
- admin policy;
- final public Offering transition;
- Search refresh;
- Trust/KYC/Payment composition;
- `lockedHealthcareFlag` behavior.

### Module-Owned Data

- `HealthcareComplianceProfile`.
- `HealthcareComplianceStatus` only for supported initial states.
- owner event payloads.

### Public Interfaces

Implement:

- `declareHealthcareLane`;
- `getHealthcareComplianceContext`;
- `evaluateHealthcareRequirement`;
- SH-020 baseline `evaluateHealthcareReadiness`.

### Shared Operations Used

- **SH-001 / Identity:** actor resolution before actor-initiated declaration/query.
- **SH-002 / Role:** authorize declaration/readiness visibility.
- **SH-022 / Taxonomy:** obtain healthcare requirement triggers. Local policy: whether those triggers make the requested Healthcare action applicable. Prohibited duplicate: hardcoded category list.
- **SH-044 / platform:** idempotent lane declaration. Local key: ProfessionalProfile + declaration intent/version.
- **SH-046 / platform:** transactional profile/readiness events. Prohibited duplicate: local event bus.
- **SH-123 / target owner:** validate exact target when explicit boundary is part of readiness input.
- **SH-034 / Ops:** sanitize telemetry around readiness decisions.

### Domain Logic

- Healthcare applicability is true only from approved canonical trigger context or explicit boundary semantics.
- No `User.isHealthcareProvider` or equivalent lookup exists.
- If healthcare is not required, SH-020 may return a safe `healthcare_not_required` permitted dimension without creating a BAA.
- If healthcare is required and no profile exists, return `healthcare_profile_missing`/remediation without auto-creating unless the caller explicitly invokes declaration.
- Declaration creates one profile idempotently; concurrent declarations converge on the unique row.
- Baseline SH-020 cannot claim BAA readiness until Feature 03 and U-HC-01/03 decisions support the requested path.
- `not_applicable` is not silently converted to verified.

### Authorization / Compliance

- General permission required for declaration and nonpublic healthcare context.
- Healthcare reason codes shown to a caller are audience-safe; do not leak private regulatory details to an unauthorized caller.
- No PHI/provider data is required for declaration.

### Database / Transaction Behavior

- Unique `professionalProfileId` enforces one profile per ProfessionalProfile.
- Provision through SH-044 plus DB unique constraint.
- Profile creation + outbox event commit in one transaction.
- Concurrent duplicate create returns canonical existing/new result, not an unhandled unique error.

### Events / Jobs

- emit profile created/changed and readiness changed when externally meaningful;
- no worker required.

### Provider Integration

None.

### UI / Admin Surface

Only if the existing professional onboarding surface needs it:

- healthcare lane declaration/control;
- current status and safe next action;
- no claim that user is “HIPAA certified” or globally a healthcare user.

### Failure Behavior

- taxonomy/source owner unavailable: SH-020 returns dependency-unavailable/non-allow for healthcare-sensitive action rather than guessing;
- unsupported trigger combination: `policy_unresolved`/unsupported;
- duplicate declaration: replay canonical profile;
- unauthorized caller: stop before healthcare detail.

### Tests

- unit: requirement trigger matrix and baseline SH-020;
- integration: one profile per ProfessionalProfile under concurrent creates;
- contract: Taxonomy/Professional/Offering owner facts and SH-020 result;
- authorization: self/admin/unauthorized;
- regression: no User healthcare flag, TrustBadge, license, or DataSensitivity-only gate;
- event: transaction/outbox exactly once.

### Documentation Updates

If the feature fixes an approved declaration status transition or reason-code vocabulary, record it in Module architecture Section 9/31.

### Acceptance Criteria

1. One ProfessionalProfile cannot acquire duplicate HealthcareComplianceProfiles under concurrency.
2. Healthcare applicability uses canonical context, not User flags or local category maps.
3. SH-020 returns deterministic supported baseline decisions and explicit unresolved/unsupported outcomes for unimplemented BAA/provider behavior.
4. Healthcare writes no ProfessionalProfile/Offering/Search/Audit/Notification source rows directly.
5. Events are transactional and PHI-minimized.

### Exit Gate

All unit/integration/contract/authorization/concurrency tests pass, and CL-03 Professional Eligibility can contract-test SH-020 without reading Healthcare tables directly.

---

# Phase 2 — Core Healthcare Lifecycles and Access Policy

## 03 — BAA Manual / Provider-Neutral Lifecycle and Profile Summary

### Objective

Implement the BAA lifecycle that can be safely supported without a live provider, while preserving `BaaAgreement` as execution truth and preventing `HealthcareComplianceProfile` from becoming a duplicate agreement lifecycle.

### Observable Result

- A permitted workflow can create a BAA record and apply only architecture-approved manual/provider-neutral transitions.
- The current Healthcare profile summary changes only as a consequence of approved BAA truth and Healthcare verification policy.
- SH-020 incorporates BAA evidence for the supported path.
- Unsupported legal/provider transitions fail explicitly rather than being approximated.

### Cluster Build-Plan Link

Implements the BAA and healthcare-profile portion of **CL-03 Feature 06**. Production e-sign automation remains gated exactly as the Cluster plan permits.

### Dependencies

- Module Features 01–02.
- SH-001/002, SH-008 where required, SH-029, SH-044, SH-046, SH-051/052/053.
- Media ready-asset interface if the approved manual path attaches evidence.
- **Required architecture approval before enabling ambiguous behavior:** U-HC-01 effective/current BAA rule and U-HC-03 transition matrix for the subset implemented.
- U-07 may remain unresolved only if the feature is explicitly labeled manual/provider-neutral and does not claim complete production e-sign/legal proof.

### In Scope

- `createBaaAgreement`.
- Approved subset of:
  - `recordBaaSent`;
  - `applyBaaSignedResult` for a controlled manual/provider-neutral evidence path;
  - `verifyBaaAgreement`;
  - `rejectBaaAgreement` only if rejection proof is adequately defined;
  - `revokeBaaAgreement`;
  - `expireBaaAgreement` command, with scheduling deferred to Feature 06.
- `getCurrentBaaContext` using the approved effective-BAA selection rule.
- `deriveHealthcareProfileSummaryFromBaa`.
- SH-020 BAA dimension.
- BAA/profile owner events and required audit requests.

### Out of Scope

- live provider SDK/webhook;
- provider-event dedupe schema unless U-08 is approved during this feature and Cluster architecture is updated accordingly;
- legal drafting of BAA text;
- pretending current `documentMediaId` alone proves immutable execution;
- boundary/policy work;
- Search/Notification delivery integration beyond event intent;
- unapproved restore/reopen/reissue transitions.

### Module-Owned Data

- `BaaAgreement`;
- `HealthcareComplianceProfile` summary fields/status as approved;
- `BaaAgreementStatus` and `HealthcareComplianceStatus` transition behavior;
- `BaaAgreementChanged.v1` / `HealthcareReadinessChanged.v1`.

### Public Interfaces

Implement only approved named commands:

- `createBaaAgreement`;
- `recordBaaSent`;
- `applyBaaSignedResult`;
- `verifyBaaAgreement`;
- `rejectBaaAgreement` if evidence model supports it;
- `revokeBaaAgreement`;
- `expireBaaAgreement`;
- `getCurrentBaaContext`.

Never expose `setBaaStatus`.

### Shared Operations Used

- **SH-001 / Identity:** actor context for professional/admin commands.
- **SH-002 / Role:** authorize BAA action. Local policy: BAA/profile relationship and named action. Prohibited duplicate: BAA admin role helper.
- **SH-008 / Consent:** query required healthcare disclosure/version proof where the approved transition policy requires it. Local policy: sufficiency. Prohibited duplicate: generic consent fields on BAA.
- **SH-029 / Audit:** append significant manual/reviewer action proof. Local policy: action/event metadata. Prohibited duplicate: BAA audit table.
- **SH-044 / platform:** command replay protection. Local policy: semantic identity per BAA/action/evidence version.
- **SH-046 / platform:** transactional BAA/profile/readiness event publication.
- **SH-051/052/053 / persistence/state machine:** serialize/validate transitions. Local policy: transition graph/evidence.
- **SH-087/090 / Media:** private evidence access/attachment if approved. Local policy: business meaning and access entitlement. Prohibited duplicate: R2/signed URL pipeline.
- **SH-034 / Ops:** safe audit/telemetry metadata.

### Domain Logic

- `BaaAgreement` is the only agreement execution truth.
- The profile may summarize BAA progress only through PR-HC-01; no independent “mark profile baa_signed” command exists.
- Multiple BAA rows require the approved U-HC-01 selection rule. If the system cannot determine one effective BAA, SH-020 returns `policy_unresolved`/manual review rather than choosing by recency.
- A BAA provider reference is evidence metadata; it does not drive state on read.
- Every transition validates current BAA status and expected source/evidence.
- `verified` means the Workin Ants Healthcare verification policy has accepted the BAA proof; it is not merely the provider's “signed” flag.
- `expired`/`revoked` causes readiness reevaluation; it does not directly suspend `ProfessionalProfile` or `Offering`.
- If `rejected` needs a BAA-specific reason and the schema cannot preserve it adequately, leave that transition disabled pending schema ruling rather than write the reason into `HealthcareComplianceProfile.rejectedReason` as a substitute.

### Authorization / Compliance

- Professional/admin paths use SH-002.
- Any standalone healthcare consent is SH-008 proof and remains separate.
- Manual evidence must not expose PHI or legal document contents to unauthorized support actors.
- Do not claim legal completeness until U-07 is resolved.

### Database / Transaction Behavior

- BAA transition + derived profile summary + outbox events should commit in one Healthcare-local transaction.
- Use expected current status and SH-051/052 as needed to prevent verify/revoke/expire races.
- Current indexes on profile/status and provider/reference are used; no “latest” query becomes authoritative unless U-HC-01 explicitly chooses it.
- If U-07 adds an immutable evidence/snapshot model, migration must be approved before implementation.

### Events / Jobs

- emit BAA change and readiness/profile summary events;
- no scheduled worker yet;
- an expiry command can be directly tested with a supplied effective time.

### Provider Integration

None beyond a provider-neutral normalized input DTO that does not require an SDK. A manual/admin pathway may apply an approved normalized result with evidence reference.

### UI / Admin Surface

If current product scope includes healthcare onboarding:

- show current BAA status and safe next action;
- restricted manual reviewer can apply only named approved actions;
- do not render raw provider payload or imply “HIPAA compliant” solely from one status.

### Failure Behavior

- ambiguous current BAA: `manual_review_required`/`policy_unresolved`;
- invalid transition: conflict, no write;
- stale transition: conflict with current status/version;
- missing required consent/evidence: explicit blocker;
- Media evidence unavailable: do not mark verified;
- unsupported legal proof path: `unsupported_operation`;
- outbox failure inside transaction: domain mutation does not commit without durable event where event correctness is required.

### Tests

- unit: approved transition table, effective BAA selection, profile summary derivation, SH-020 BAA reasons;
- integration: BAA/profile/outbox transaction;
- concurrency: verify vs revoke, sign vs expire, duplicate commands;
- authorization: professional/reviewer/admin/unauthorized cases;
- compliance: ConsentLog not BAA truth; Agreement/Trust provider truth not used;
- Media contract if evidence attachment is used;
- unsupported U-07/U-08 paths return explicit unavailable results.

### Documentation Updates

- Record the approved effective-BAA rule and exact transition table in Module architecture.
- If U-07 is resolved, update proof/retention sections before enabling corresponding code.

### Acceptance Criteria

1. BAA commands are named and transition-validated; no generic status setter exists.
2. Profile BAA-progress summary cannot be changed independently of BAA truth.
3. SH-020 returns BAA-based reasons/evidence for the supported path.
4. Multiple BAA ambiguity is handled by approved rule or explicit review, never recency guesswork.
5. Manual/provider-neutral path does not claim production e-sign completeness.
6. Concurrency/idempotency tests prove one effective transition per command/evidence event.

### Exit Gate

All transition, transaction, authorization, concurrency, SH-020, and evidence-boundary tests pass. Architecture reflects any U-HC-01/U-HC-03 rulings used by the code. Live provider callbacks remain disabled.

---

## 04 — Exact Healthcare Data Boundaries and Safe Target Validation

### Objective

Implement explicit marking and exact-target querying of healthcare-sensitive resources using owner-validated target references, while refusing unapproved clear/retire/inheritance behavior.

### Observable Result

- An authorized workflow can mark a supported, existing target as healthcare-sensitive exactly once.
- Resource owners can query whether an exact target has a Healthcare boundary.
- Invalid/stale target references cannot create orphan healthcare boundaries through the public path.
- Boundary clear/retirement/inheritance requests fail explicitly until U-09 is resolved.

### Cluster Build-Plan Link

Implements the explicit HealthcareDataBoundary portion of **CL-03 Feature 06** and satisfies its requirement that supported boundaries are owner-validated.

### Dependencies

- Module Features 01–03.
- SH-002, SH-044, SH-046, SH-123.
- Owner-facts contracts for each supported target type actually enabled in MVP.
- U-09 remains unresolved; feature scope is exact marking/query only.

### In Scope

- `markHealthcareDataBoundary`.
- `getHealthcareDataBoundary`.
- `resolveEffectiveHealthcareBoundary` implemented as exact-target resolution only and explicitly reporting capability/version.
- target-type registry that maps each allowed `HealthcareDataBoundaryTargetType` to an owner validation contract; no direct foreign Prisma access.
- duplicate mark idempotency.
- boundary-marked owner event.
- optional reason code, sanitized/controlled.

### Out of Scope

- clearing/deleting a boundary;
- inferred propagation from Offering → Order → Booking → Thread/Message/Media/Video;
- parent-child precedence;
- cross-domain generic DataSensitivity derivation;
- automatic creation from every source event;
- resource-owner enforcement of access mechanics.

### Module-Owned Data

- `HealthcareDataBoundary`;
- `HealthcareDataBoundaryTargetType`;
- `HealthcareDataBoundaryMarked.v1`.

### Public Interfaces

- `markHealthcareDataBoundary`;
- `getHealthcareDataBoundary`;
- `resolveEffectiveHealthcareBoundary` with an explicit `resolutionMode: exact_target` or equivalent contract field so consumers cannot assume inheritance exists.

Do not publish `clearHealthcareDataBoundary` yet.

### Shared Operations Used

- **SH-002 / Role:** authorization for actor-initiated marking. Local policy: who may mark which contextual target. Prohibited duplicate: boundary role helper.
- **SH-044 / platform:** idempotent exact mark.
- **SH-046 / platform:** boundary event.
- **SH-123 / target owner:** validate target existence/type/version/context. Local policy: which target types Healthcare supports. Prohibited duplicate: `findAnyTarget` repository.
- **SH-029 / Audit:** admin/system evidence if root audit policy requires boundary changes to be audited.
- **SH-034 / Ops:** sanitize reason/telemetry.

### Domain Logic

- A boundary row is explicit healthcare sensitivity truth for the exact target.
- `sensitivity` defaults to `healthcare`; generic DataSensitivity does not replace the boundary.
- Before write, the target owner confirms the target exists and returns only the minimum stable facts required.
- A repeated identical mark returns the existing boundary.
- A conflicting request that tries to reinterpret an existing row without an approved lifecycle returns conflict/review.
- `resolveEffectiveHealthcareBoundary` must document that “effective” currently means “explicit exact target” only. The name does not grant permission to infer parent relationships.

### Authorization / Compliance

- Caller must be authorized to mark the source context.
- Boundary reason text must be controlled/minimized; do not store clinical details.
- Exact healthcare-sensitive metadata itself is treated as sensitive.

### Database / Transaction Behavior

- rely on `@@unique([targetType, targetId])`;
- owner target validation happens before insert; tolerate race where target deletion occurs after validation by returning safe conflict/ops evidence, not creating a universal FK system;
- boundary write + outbox event commit transactionally;
- no foreign table mutation.

### Events / Jobs

- emit `HealthcareDataBoundaryMarked.v1`;
- no propagation worker;
- no clear/retire worker.

### Provider Integration

None.

### UI / Admin Surface

No general UI required. If restricted tooling exists, show exact target type/ID, current boundary status, safe reason category, created timestamp; do not expose PHI payload.

### Failure Behavior

- target invalid/not found: no write;
- target owner unavailable: dependency-unavailable, no write;
- duplicate: replay existing boundary;
- clear/inheritance request: unsupported operation with U-09 reference in internal diagnostics;
- generic sensitivity-only request: reject/require explicit Healthcare boundary command.

### Tests

- unit: supported target registry and exact resolution semantics;
- integration: unique boundary/idempotency;
- contract: SH-123 validation for each enabled target type;
- architecture: no direct foreign Prisma lookup;
- security: reason/telemetry minimization;
- negative: clear, inherited resolution, unsupported target type fail explicitly.

### Documentation Updates

Update the supported target-type list if MVP enables only a subset of the enum. Do not pretend all enum values have operational owner contracts if they do not.

### Acceptance Criteria

1. Exact valid targets can be marked once and queried reliably.
2. Every write uses target-owner validation.
3. No boundary clear/propagation/inheritance exists while U-09 remains unresolved.
4. `DataSensitivity` alone cannot satisfy the Healthcare boundary query.
5. Boundary changes emit one minimized owner event.

### Exit Gate

All exact-boundary, target-contract, idempotency, negative unsupported-behavior, and architecture-boundary tests pass.

---

## 05 — Exact-Target Admin Payload Policy and Sensitive Access Decision

### Objective

Implement the currently supportable exact-target healthcare admin payload policy and access decision after general authorization, with server-enforceable redaction/block instructions and mandatory sensitive-access proof integration.

### Observable Result

- An authorized healthcare/compliance admin can set/read the current exact-target access mode where the feature scope permits it.
- An already-authorized resource owner can ask Healthcare whether an exact healthcare-sensitive payload is allowed, must be redacted, or must be blocked.
- The consumer receives a typed handling instruction without raw PHI.
- Required allowed/redacted/blocked accesses create canonical SH-030 evidence.
- Parent/child inheritance and historical policy reproduction remain unavailable until U-10.

### Cluster Build-Plan Link

Completes the admin payload-policy portion of **CL-03 Feature 06** and the Cluster exit requirement that Role authorization and healthcare payload policy are distinct and tested.

### Dependencies

- Module Features 01–04.
- SH-001/002, SH-029/030, SH-044, SH-046, SH-052, SH-123.
- Resource-owner handling contract test double.
- U-10 unresolved: feature is exact current policy only.
- U-11 unresolved: use PR-HC-03 narrowed semantics after general auth.
- U-HC-08 redaction instruction shape must be approved for any reusable cross-resource field mask; otherwise return only a coarse `redaction_required` policy token and require consumer-specific approved contract.

### In Scope

- `setHealthcareAdminAccessPolicy` for exact target.
- `getHealthcareAdminAccessPolicy`.
- `evaluateHealthcareAdminAccess` after authorization.
- exact boundary lookup as a Healthcare input.
- stable result with allowed/redacted/blocked semantics in the supported post-auth contract.
- access-policy changed owner event.
- audit request for policy mutation and sensitive access decision/outcome.
- metadata-only restricted compliance case query where useful.

### Out of Scope

- generic Role/RBAC;
- parent/child policy inheritance;
- policy version history/effective date reconstruction;
- client-side-only redaction;
- resource payload fetching from Healthcare;
- Messaging/Media/Video serialization logic;
- global `denied` semantics until U-11;
- generic admin review queue.

### Module-Owned Data

- `HealthcareAdminAccessPolicy`;
- `HealthcareAdminAccessMode`;
- Healthcare-specific access decision policy;
- `HealthcareAdminAccessPolicyChanged.v1`.

### Public Interfaces

- `setHealthcareAdminAccessPolicy`;
- `getHealthcareAdminAccessPolicy`;
- `evaluateHealthcareAdminAccess`;
- restricted `listHealthcareComplianceCases` if the real admin workflow requires it.

The public access contract must state that it is invoked **after** general authorization. It must not become a substitute for SH-002.

### Shared Operations Used

- **SH-001 / Identity:** admin/support actor resolution.
- **SH-002 / Role:** general permission before policy mutation/access evaluation. Local policy: healthcare action/target facts. Prohibited duplicate: `adminCanViewPhi` helper.
- **SH-029 / Audit:** policy mutation evidence.
- **SH-030 / Audit:** actual sensitive access/redaction/block evidence. Local policy: sensitivity/Healthcare decision/target facts. Prohibited duplicate: local access log.
- **SH-044 / platform:** idempotent policy mutation.
- **SH-046 / platform:** policy event publication.
- **SH-052 / persistence:** stale concurrent policy-update detection.
- **SH-123 / owner:** validate target before policy creation/update.
- **SH-034 / Ops:** safe metadata.

### Domain Logic

- SH-002 denies unauthorized actors before Healthcare receives/uses PHI payload.
- Healthcare determines policy from exact boundary + current exact policy + supported default semantics fixed by the feature specification.
- `redact_payload` returns a typed handling requirement; the consumer resource owner constructs a reduced payload before serialization.
- `block_payload` prevents payload issuance while allowing safe metadata/status if the consumer contract permits it.
- Until U-11, Role denial is represented outside the Healthcare decision and Healthcare's post-auth result is limited to `allowed | redacted | blocked`.
- Do not infer parent policy or weaken a parent restriction because inheritance is unresolved.
- Do not return raw reason text to broad consumers; use safe reason code/policy reference.

### Authorization / Compliance

- policy management requires the approved high-trust Role action;
- U-HC-07 determines whether step-up is also required; if unresolved, do not invent it;
- every actual healthcare-sensitive access that policy requires to be logged invokes SH-030;
- a policy check without actual payload issuance may be distinguishable from actual access according to Audit contract; avoid double logging by feature spec.

### Database / Transaction Behavior

- unique exact policy per `(targetType,targetId)`;
- target validation before write;
- policy update uses expected `updatedAt`/version or root optimistic concurrency mechanism;
- policy mutation + outbox event in one transaction;
- no historical snapshot claimed from overwritten row.

### Events / Jobs

- emit policy changed event;
- no worker.

### Provider Integration

None.

### UI / Admin Surface

If approved:

- metadata-only healthcare case list;
- exact-target policy editor with `allow`, `redact_payload`, `block_payload`;
- warning that policy is current exact-target scope only while U-10 remains unresolved;
- no raw PHI preview required to set a policy.

### Failure Behavior

- unauthorized: stop before healthcare details;
- invalid/stale target: no policy write;
- stale policy update: conflict;
- no supported policy/default semantics: `policy_unresolved` rather than allow;
- consumer asks for inherited policy: unsupported;
- audit failure on an action requiring synchronous access proof: follow root critical-audit policy; never silently issue sensitive payload.

### Tests

- unit: exact policy decision matrix;
- authorization: Role gate occurs before Healthcare policy details;
- contract: consumer receives only typed handling instruction;
- integration: exact policy uniqueness/update concurrency;
- audit: allowed/redacted/blocked actual access produces required SH-030 request;
- security: server-side redaction contract, no raw payload in logs/events;
- negative: inherited/historical request unavailable.

### Documentation Updates

Document the exact current-policy default and approved redaction contract. If U-10/U-11/U-HC-08 are resolved, update architecture before broadening behavior.

### Acceptance Criteria

1. Role authorization and Healthcare policy are separate, ordered gates.
2. Exact policy can be managed only by authorized actors.
3. Healthcare returns server-enforceable allow/redact/block handling, not a UI-only flag.
4. Required sensitive access creates canonical AccessAuditLog requests without local audit storage.
5. U-10/U-11 limitations are enforced by code/tests.

### Exit Gate

All policy, authorization-order, concurrency, sensitive-access, redaction-contract, and unsupported-scope tests pass. At this point the non-provider core of CL-03 Feature 06 is functionally demonstrable.

---

# Phase 3 — Provider, Expiry, and Worker Boundary

## 06 — BAA Expiry, Provider-Neutral Port, and Gated Provider Automation

### Objective

Complete the worker/provider boundary required by CL-03 Feature 06 without enabling unsafe provider automation: implement expiry/retry/reconciliation plumbing where semantics are approved, define the BAA provider-neutral port, and enable live callbacks only if U-07/U-08 have been explicitly resolved.

### Observable Result

- Due BAAs can be expired idempotently under the approved BAA transition policy.
- Healthcare has a provider-neutral BAA/e-sign port with no provider SDK types in public Module contracts.
- If no provider is approved, provider commands/routes are disabled with an explicit unsupported result while manual/provider-neutral Feature 03 remains usable.
- If a provider and Healthcare-owned processed-event schema are approved, callbacks are signature-verified, deduplicated, translated, transition-validated, replay-safe, reconcilable, and observable.

### Cluster Build-Plan Link

Finishes the provider/worker portion of **CL-03 Feature 06**. The Cluster's Feature 06 exit gate explicitly permits automated callbacks to remain disabled when U-07/U-08 are unresolved, provided no fake dedupe/proof is introduced.

### Dependencies

- Module Features 01–05.
- SH-047/048/055.
- SH-034/037/038.
- SH-059/060/061/062 only for enabled provider path.
- SH-078.
- U-HC-01/U-HC-03 effective BAA and expiry transition semantics for scheduled expiry.
- U-07/U-08 before live provider callback side effects.
- root secrets/configuration conventions.

### In Scope

Always in scope:

- `BaaProviderPort` provider-neutral contract;
- BAA expiry worker and deterministic clock handling if expiry transition is approved;
- job payload/version/idempotency definitions;
- safe provider-disabled behavior;
- operational telemetry for expiry/provider-unavailable/reconciliation attempts.

Conditionally in scope only after U-07/U-08 approval:

- concrete selected provider adapter;
- Healthcare-owned processed-provider-event schema/migration;
- webhook route/worker;
- signature verification;
- provider-event dedupe;
- status translation;
- reconciliation worker;
- provider-side revoke/delete capability where approved.

### Out of Scope

- selecting a provider by coding convenience;
- inventing signer/legal proof fields without approved U-07 ruling;
- reusing another Module's provider-event ledger;
- video provider SDKs;
- Media storage implementation;
- generic queue/retry framework;
- downstream source-owner/Search integration beyond Healthcare events.

### Module-Owned Data

Always:
- `BaaAgreement` expiry/provider reference fields;
- BAA/readiness owner events.

Only after U-08 approval:
- the smallest approved Healthcare-specific processed-provider-event record and status vocabulary, if the approved ruling requires one.

### Public Interfaces

- internal/scheduled `expireBaaAgreement` invocation;
- provider-neutral `BaaProviderPort`;
- restricted reconciliation command if a provider is enabled;
- provider webhook endpoint is infrastructure-facing, not a public business command.

### Shared Operations Used

- **SH-044 / platform:** idempotent BAA/domain application command.
- **SH-046 / platform:** owner event publication.
- **SH-047 / queue:** durable expiry/provider/reconciliation jobs. Local policy: job payload/business completion. Prohibited duplicate: Healthcare job table.
- **SH-048 / queue:** retry/backoff. Local policy: provider/network retry classes. Prohibited duplicate: custom retry loop framework.
- **SH-055 / scheduler:** deadline expiration runner. Local policy: BAA due semantics. Prohibited duplicate: Healthcare cron framework.
- **SH-059 / provider shell:** raw callback signature verification. Local policy: provider secret/algorithm/tolerance. Prohibited duplicate: unsigned route.
- **SH-060 / provider shell:** dedupe mechanics using Healthcare-owned event truth. Local policy: provider event key/result. Prohibited duplicate: `ProcessedStripeEvent`, `ProcessedVideoProviderEvent`, `lastEventId` as complete ledger.
- **SH-061 / provider shell:** translate provider status. Local policy: BAA mappings. Prohibited duplicate: global status mapper.
- **SH-062 / provider shell:** reconcile provider state. Local policy: Healthcare discrepancy and transition semantics.
- **SH-078 / provider security:** minimize outbound/inbound provider metadata. Local policy: required BAA fields.
- **SH-037/038 / Ops:** integration/queue telemetry. Prohibited duplicate: using Ops rows as BAA state.
- **SH-070 / provider/privacy:** provider deletion only after Privacy instruction/retention approval.

### Domain Logic

#### Expiry

- A BAA is considered due only according to the approved `expiresAt` semantics and effective/current BAA rule.
- Worker re-reads authoritative BAA state inside execution; the queued expected status is not truth.
- Already expired/revoked/replaced/not-due records replay as no-op or safe stale result.
- Expiry applies the same transition guard as manual command and reevaluates profile summary/SH-020.

#### Provider-disabled mode

- No webhook endpoint with side effects is exposed, or it returns an explicit disabled response according to routing/security standards.
- No provider name/status is hardcoded into BAA domain policy.
- Manual/provider-neutral state remains available only within Feature 03's approved limits.

#### Provider-enabled mode

- Signature validation occurs before JSON-derived domain effects.
- Event ID is claimed before applying side effects.
- Provider status maps to a normalized domain input, not directly to database enum assignment.
- Unknown provider status results in operational review/failure, not implicit allow.
- Domain transition + profile summary + outbox event are local transactional truth.
- Processed-event result records that the event was applied/ignored/failed according to approved schema.
- Reconciliation uses the same normalization/transition rules and does not overwrite by “provider wins.”

### Authorization / Compliance

- webhook uses provider authentication, not a forged User actor;
- manual reconciliation/admin trigger uses SH-001/002 and SH-029 as required;
- no raw webhook/provider payload is emitted to logs/audit/events;
- provider legal/BAA capability must be approved outside code before activation;
- production e-sign completeness remains blocked unless U-07 is resolved.

### Database / Transaction Behavior

- expiry transition uses aggregate lock/expected status as required;
- if provider-event record exists, provider-event claim uniqueness must be database-enforced;
- provider event claim and BAA mutation are coordinated so retry cannot duplicate business effect; exact transaction structure follows canonical SH-060 implementation;
- domain state + outbox event commit atomically;
- no update to foreign Module tables.

### Events / Jobs

- BAA expiry job;
- provider event job if enabled;
- reconciliation job if enabled;
- dead-letter/manual review after retry exhaustion;
- BAA/readiness events emitted once per authoritative change.

### Provider Integration

See domain logic above. Provider-specific types stay in `providers/adapters/<provider>/` and are translated at the adapter boundary.

### UI / Admin Surface

Optional restricted operations view may show:

- BAA ID/status;
- provider integration state category;
- last reconciliation time/outcome;
- retry/dead-letter reference;
- safe next action.

It must not expose raw callback bodies or signed document contents.

### Failure Behavior

- provider not selected: explicit unsupported, no fake state;
- invalid signature: reject, no domain write, record safe operational evidence;
- duplicate event: replay/ignore safely;
- unknown provider state: no guessed transition; operational review;
- provider outage: retain current canonical state, retry/reconcile;
- transition conflict after provider event: record safe mismatch/review, never force provider state;
- retry exhaustion: dead-letter/manual review, domain state remains authoritative;
- U-07/U-08 unresolved: callback automation disabled.

### Tests

Always:
- expiry due/not-due/replay/stale tests;
- job idempotency and retry classification;
- provider-neutral port compile/contract tests;
- provider-disabled behavior;
- telemetry redaction.

When enabled:
- valid/invalid signature;
- duplicate provider event;
- out-of-order event;
- unknown status;
- translation matrix;
- transition conflict;
- reconciliation repair/no-op/review;
- provider outage/retry/dead-letter;
- processed-event uniqueness;
- no provider DTO leakage outside adapter.

### Documentation Updates

If U-07/U-08 are resolved, update Module architecture, CL-03 architecture unresolved register, provider documentation, schema ownership, and retention/privacy sections before live activation.

### Acceptance Criteria

1. BAA expiry is idempotent and transition-safe for the approved semantics.
2. A provider-neutral port exists with no provider types in public Healthcare contracts.
3. If U-07/U-08 are unresolved, live provider callback effects are unreachable/disabled and tested as such.
4. If enabled, callbacks satisfy signature → owner dedupe → translation → transition validation → transactional write/event → replay-safe downstream sequence.
5. No other Module's processed-provider-event table is reused.
6. Provider/queue failures are operationally visible without replacing BAA truth.

### Exit Gate

CL-03 **Feature 06** is considered satisfied for this Module only when Module Features 01–06 remain passing and the Cluster Feature 06 seven-point exit gate is demonstrated: SH-020 is owner-derived; healthcare is contextual; Role and Healthcare policy are separate; supported boundaries/policies are owner-validated and audited; provider automation is either fully safe or disabled; unsupported boundary/history behavior fails explicitly; all enabled paths pass compliance/security tests.

---

# Phase 4 — Module Integration and Cross-Cluster Contract Proof

## 07 — Professional Eligibility, Marketplace, and Public-Readiness Integration

### Objective

Prove Healthcare participates correctly in seller/publication readiness without owning ProfessionalProfile or Offering lifecycle and without commanding Search as source truth.

### Observable Result

- Professional Eligibility consumes SH-020 for healthcare-sensitive actions and treats it as one readiness dimension.
- Marketplace Supply receives the composed professional/publication decision and remains sole owner of `Offering.status`.
- Healthcare readiness changes trigger source-owner reevaluation through events/contracts.
- Public Search refresh is requested by the approved source owner; Healthcare does not mutate Search state or foreign records.
- Non-healthcare actions do not acquire unnecessary Healthcare blockers.

### Cluster Build-Plan Link

Participates in **CL-03 Feature 11 — Readiness Change Propagation and Neighboring-Cluster Integration** and verifies the Healthcare part of the publication workflow defined earlier by CL-03 Features 03/08.

### Dependencies

- Module Features 01–06.
- CL-03 Feature 03 SH-016 Professional readiness composition.
- Marketplace publication/public-readiness contracts.
- Search SH-091 contract through source owner.
- SH-045/046 event reliability.
- SH-024 public-readiness shared contract where approved.
- PR-HC-04 source-owner Search-refresh ruling approved or equivalent Cluster ruling.

### In Scope

- contract tests: Professional Eligibility → SH-020;
- contract tests: Marketplace/public readiness consumes Professional Eligibility/Healthcare result without raw Healthcare DB reads;
- Healthcare readiness event consumption path by source owner;
- replay/out-of-order tests for readiness changes;
- Search refresh contract assertion at source-owner boundary;
- safe source/evidence version propagation.

### Out of Scope

- implementing Professional Eligibility composition policy;
- implementing Offering transition;
- implementing SearchUpsertEvent/Typesense;
- determining non-healthcare Trust/Payment/Entitlement gates;
- creating a Healthcare public projection of another Module's entity;
- direct Search calls unless architecture explicitly assigns Healthcare as source owner for a Healthcare-owned projection.

### Module-Owned Data

No new model. Existing Healthcare truth and `HealthcareReadinessChanged.v1` are used.

### Public Interfaces

- SH-020 stable contract;
- `HealthcareReadinessChanged.v1`;
- safe `getHealthcareComplianceContext` evidence query for authorized consumers if needed.

### Shared Operations Used

- **SH-020 / Healthcare:** source decision being integrated.
- **SH-016 / Professional Eligibility:** final seller action composition; Healthcare consumes only for integration proof, does not implement it.
- **SH-024 / source compliance contract:** public readiness shape where approved. Local Healthcare policy remains SH-020.
- **SH-045 / platform:** consumer event dedupe.
- **SH-046 / platform:** Healthcare readiness event source.
- **SH-091 / Search:** invoked by source owner according to PR-HC-04. Prohibited duplicate: Healthcare Typesense/indexer code.
- **SH-034 / Ops:** safe integration telemetry.

### Domain Logic

- Healthcare decides only healthcare readiness.
- Professional Eligibility decides action-specific professional readiness.
- Marketplace decides whether its Offering-local invariants plus composed readiness permit its status transition.
- Search indexes only owner-approved source projection.
- A Healthcare event is a fact requiring reevaluation, not a command to set `Offering.active`/`paused` or delete an index.
- Dependency unavailable for a healthcare-required publication fails safely; non-healthcare publication should not call a provider/BAA path unnecessarily.

### Authorization / Compliance

- Consumer queries expose only safe healthcare reason/evidence refs appropriate to the caller.
- Search/public projection receives no PHI, BAA document data, admin policy reason text, or private boundary details beyond the approved public-readiness signal.

### Database / Transaction Behavior

- No foreign DB write from Healthcare.
- Event consumers are idempotent.
- A replayed readiness event cannot duplicate source transition or Search request due to consumer idempotency/source state checks.

### Events / Jobs

- Healthcare emits readiness fact.
- Professional/Marketplace source owner consumes and reevaluates.
- source owner requests SH-091 if its public projection changes.
- no Healthcare Search worker.

### Provider Integration

None beyond current Healthcare readiness state.

### UI / Admin Surface

No new UI required. Existing seller/Offering readiness surfaces may display Healthcare as one safe blocker/remediation category.

### Failure Behavior

- Healthcare dependency unavailable: Professional Eligibility returns dependency-unavailable/non-allow for healthcare-required action;
- stale Healthcare event: source owner checks current source versions/state before effect;
- Search unavailable: source owner/Search job retries; Healthcare truth remains unchanged;
- unauthorized readiness caller: no sensitive blocker detail leakage.

### Tests

- cross-Module contract: SH-020 → SH-016;
- cross-Module contract: SH-016/Healthcare → Marketplace publication decision;
- architecture test: no foreign Prisma read/write;
- event replay/out-of-order;
- Search request emitted by approved source owner, not Healthcare;
- non-healthcare flow bypasses unnecessary BAA/provider gate;
- public payload contains no PHI.

### Documentation Updates

Record any finalized public-readiness event/source-owner contract and source version fields.

### Acceptance Criteria

1. Professional Eligibility consumes SH-020 as an owner decision, not Healthcare tables.
2. Marketplace alone mutates Offering lifecycle.
3. Healthcare readiness changes cause reevaluation without cross-Module writes.
4. Search is refreshed through the source-owner/Search interface only.
5. Non-healthcare supply is not unnecessarily gated by BAA/provider workflow.

### Exit Gate

Contract/integration/event-replay/Search-boundary tests pass with no direct cross-Module persistence coupling.

---

## 08 — Resource-Owner Enforcement for Media, Messaging, Video, Booking, and Order Contexts

### Objective

Prove that Healthcare boundary/admin-access decisions can protect healthcare-sensitive resources while each resource Module retains mechanics and lifecycle ownership.

### Observable Result

For each resource owner included in current MVP scope:

- owner validates target/context;
- general authorization occurs first;
- owner asks Healthcare for exact boundary/admin access decision;
- allowed/redacted/blocked handling is enforced server-side before payload/token/URL issuance;
- required SH-030 proof is recorded;
- Healthcare never reads or writes the resource payload/lifecycle directly.

### Cluster Build-Plan Link

Primary Healthcare participation in **CL-03 Feature 11 cross-cluster integration**, bridging CL-05 Media/Video/Booking and CL-07 Messaging, with CL-04 Order context as applicable.

### Dependencies

- Module Features 01–07.
- Feature 04 exact boundary and Feature 05 admin policy.
- approved owner contracts for the subset of:
  - Media / File Access;
  - Messaging;
  - Video Session;
  - Booking & Calendar;
  - Transaction / Order.
- SH-002 general authority;
- SH-030 sensitive access;
- SH-087 signed media URL where file access is tested;
- Video/session token public interfaces from Video owner;
- U-09/U-10 limitations remain exact-target unless resolved.
- U-HC-08 redaction instruction contract approved for each consumer path.

### In Scope

- contract adapters/DTOs between Healthcare and each enabled owner;
- exact-target boundary query/decision integration;
- `evaluateHealthcareAdminAccess` enforcement path;
- audit proof orchestration with actual outcome;
- vendor-readiness decision contract for healthcare-sensitive video where provider capability facts exist;
- BAA evidence file access flow through Media;
- integration tests proving no raw payload is returned before healthcare policy.

### Out of Scope

- Message lifecycle/content storage;
- MediaAsset upload/scan/storage implementation;
- video room/token creation implementation;
- Booking/Order lifecycle mutation;
- inferred boundary propagation;
- provider clients belonging to those Modules;
- broad UI rewrite.

### Module-Owned Data

No new source model. Uses boundaries, admin policies, SH-020/vendor-readiness policy, Healthcare events.

### Public Interfaces

- `resolveEffectiveHealthcareBoundary` (exact-target semantics unless U-09 resolved);
- `evaluateHealthcareAdminAccess`;
- `evaluateHealthcareVendorReadiness`;
- `getHealthcareComplianceContext` for safe evidence when needed.

### Shared Operations Used

- **SH-002 / Role:** general permission in owner/route path. Prohibited duplicate: Healthcare role engine.
- **SH-030 / Audit:** actual sensitive access evidence. Local Healthcare context: sensitivity/decision; resource owner reports actual issuance/view outcome.
- **SH-087 / Media:** short-lived private evidence/file access. Local policy: Healthcare allows contextual access. Prohibited duplicate: presigner.
- **SH-090 / Media contextual attachment:** if BAA/evidence context is attached. Prohibited duplicate: Media processing.
- **SH-123 / target owner:** validate contextual target.
- **SH-034 / Ops:** telemetry minimization.
- **SH-044 / platform:** idempotency for replay-prone access-grant/decision commands where the owner contract requires it.

### Domain Logic

#### Media

```text
actor → owner auth → Healthcare boundary/policy → Media entitlement/mechanics → signed URL → SH-030 actual access proof
```

Healthcare never generates the URL or reads the object.

#### Messaging

```text
actor → Thread/Message authority → Healthcare exact boundary/policy
→ Messaging serializer omits/redacts/blocks payload server-side
→ SH-030 actual access result
```

Healthcare never stores or returns the message body.

#### Video

```text
actor/context → Video/Booking entitlement → Healthcare boundary + vendor readiness
→ Video issues/denies room/token/playback through its provider
→ SH-030 when required
```

Healthcare never creates provider rooms/tokens or uses `ProcessedVideoProviderEvent`.

#### Booking / Order

Healthcare consumes only owner facts required to decide context. Booking/Order remain the lifecycle owners and may request Healthcare decisions before healthcare-sensitive delivery/access actions.

### Authorization / Compliance

- general auth always precedes healthcare policy;
- admin/support cannot bypass healthcare policy based on role;
- redaction must occur server-side before payload leaves owner;
- access proof contains safe metadata only;
- provider capability must be owner-supplied and healthcare-approved; do not hardcode Daily/Agora/Mux allowlists in consumer code.

### Database / Transaction Behavior

- Healthcare does not write resource-owner tables.
- Access decision query is side-effect free except explicit audit request made by actual resource-access orchestration according to contract.
- Resource owner transaction/entitlement behavior remains its responsibility.

### Events / Jobs

No new Healthcare worker. Resource owners may react to boundary/readiness events using SH-045 dedupe.

### Provider Integration

None owned here beyond Healthcare provider-readiness evaluation of owner-supplied capability facts.

### UI / Admin Surface

Existing admin/resource views should render:

- redacted fields absent/replaced server-side;
- blocked payload with safe explanation/next action;
- no client receipt of hidden raw PHI.

### Failure Behavior

- Healthcare dependency unavailable on a sensitive access path: fail closed/no payload issuance;
- audit-required SH-030 unavailable: follow root critical-access-audit policy; do not silently deliver if proof is mandatory;
- redaction contract unsupported: block/review, not full payload;
- target owner mismatch: no access/boundary assumption;
- vendor readiness unavailable: no healthcare-sensitive video activation if policy requires approval.

### Tests

For each enabled resource owner:

- contract test for target facts;
- authorization-before-healthcare ordering;
- allowed path;
- redacted path proves raw sensitive field never reaches serialized response;
- blocked path;
- SH-030 exactly-once/logical-access behavior;
- dependency unavailable fails safely;
- no cross-Module DB writes;
- provider-mechanics separation for Video/Media.

### Documentation Updates

Record the exact consumer handling/redaction contract and which enum target types have real MVP owner integrations. Unintegrated enum values remain unsupported, not assumed.

### Acceptance Criteria

1. Every enabled healthcare-sensitive resource path enforces Healthcare decision server-side.
2. General permission, contextual entitlement, Healthcare policy, and resource mechanics remain separate gates.
3. Healthcare never owns Media/Message/Video/Booking/Order mechanics.
4. Required actual accesses produce canonical sensitive-access evidence.
5. Unavailable/unsupported policy fails closed without raw payload leakage.

### Exit Gate

All enabled cross-Module contract/security/access-audit tests pass, including at least one redaction and one block scenario with proof that raw payload was never returned to the client.

---

# Phase 5 — Governance, Privacy, Audit, and Retention Integration

## 09 — Privacy Executor, Retention, Audit, Notification, and Operational Completion

### Objective

Complete Healthcare's owner-specific participation in Privacy, Audit, Notification, Compliance Hold, and Observability without absorbing those guardrail lifecycles, and ensure unresolved retention never causes destructive deletion by guess.

### Observable Result

- Privacy can enumerate Healthcare subject data, receive Healthcare retention facts, and execute approved erase/anonymize/retain instructions through the canonical protocol.
- Healthcare-sensitive admin/evidence access produces canonical access proof where required.
- Important BAA/profile/boundary/policy actions request generic audit proof according to policy.
- Approved status/remediation events request Notification through SH-041 with safe payloads.
- Provider/job failures are visible through Ops without changing Healthcare domain truth.
- Records whose exact retention rule is unresolved return review/retention-pending rather than being destructively deleted.

### Cluster Build-Plan Link

Healthcare portion of **CL-03 Feature 12 — Privacy, Moderation, Audit, Sensitive Access, and Operational Case Completion**.

### Dependencies

- Module Features 01–08.
- SH-095/096/097/098 Privacy protocol.
- SH-070 provider deletion where applicable.
- SH-029/030 Audit.
- SH-041 Notification.
- SH-011/012/013 Hold for approved stop-sign integration.
- SH-034/037/038 Ops.
- Media deletion/access owner interface.
- U-18 exact retention periods may remain unresolved; destructive path must remain blocked/review.
- U-07 retention implications for BAA proof.

### In Scope

- `enumerateHealthcareSubjectData`.
- `resolveHealthcareRetentionFacts`.
- `executeHealthcarePrivacyInstruction`.
- approved anonymization mappings.
- handoff to Media for file deletion where allowed.
- handoff to provider adapter for provider deletion/anonymization where allowed.
- explicit retained/review result when retention is unresolved.
- audit integration for significant owner changes/access.
- notification requests for approved safe events.
- ComplianceHold request/release integration only for approved Healthcare source conditions.
- safe operational diagnostics and dead-letter/manual-review references.

### Out of Scope

- PrivacyRequest intake/status/UI;
- DataErasureJob/DataRetentionExemption ownership;
- legal retention-duration invention;
- direct deletion of Media objects by Healthcare;
- generic moderation/case workflow;
- generic Audit/AccessAuditLog repository;
- Notification provider/channel implementation;
- Ops incident lifecycle implementation.

### Module-Owned Data

Potentially affected:

- `HealthcareComplianceProfile`;
- `BaaAgreement`;
- `HealthcareDataBoundary`;
- `HealthcareAdminAccessPolicy`;
- approved Healthcare provider-event proof if later added;
- owner events produced by privacy-safe changes.

No Privacy/Audit/Notification/Hold/Ops source rows are owned here.

### Public Interfaces

- SH-096 owner implementation `enumerateHealthcareSubjectData`;
- SH-097 owner facts `resolveHealthcareRetentionFacts`;
- SH-095 owner executor `executeHealthcarePrivacyInstruction`;
- SH-098 owner field mapping as applicable;
- safe export contribution query if root Privacy contract includes export;
- existing Healthcare decision/command interfaces remain unchanged.

### Shared Operations Used

- **SH-095 / Privacy:** execute orchestrator instruction. Local policy: Healthcare record disposition. Prohibited duplicate: local privacy workflow.
- **SH-096 / Privacy:** enumerate Healthcare subject data. Local policy: subject relationships/target refs. Prohibited duplicate: Privacy scanning Healthcare tables directly as universal owner.
- **SH-097 / Privacy:** return retention facts. Local policy: record/evidence facts; legal periods may be unresolved. Prohibited duplicate: `retainForever` boolean.
- **SH-098 / shared privacy mechanism:** anonymize approved fields. Local policy: Healthcare mapping and retained evidence.
- **SH-070 / provider owner:** provider-side deletion/anonymization. Local policy: whether Privacy instruction/retention permits it.
- **SH-029 / Audit:** generic action proof.
- **SH-030 / Audit:** sensitive access proof.
- **SH-041 / Notification:** deliver status/remediation notice. Local policy: trigger/safe message intent. Prohibited duplicate: email/SMS client.
- **SH-011/012/013 / Hold:** evaluate/request/release reusable stop sign. Local policy: healthcare source condition. Prohibited duplicate: local blocked state.
- **SH-034 / Ops:** sanitize metadata.
- **SH-037/038 / Ops:** provider/integration/queue failure visibility. Prohibited duplicate: using Ops status as business state.
- **SH-087/Media deletion contracts:** Healthcare never deletes private object directly.

### Domain Logic

#### Privacy enumeration

Return stable identifiers and record classes, not full PHI/document contents. Include cross-owner references required for Privacy orchestration, such as MediaAsset/provider resource references, while identifying their owners.

#### Retention

- If approved policy says erase: execute only the Healthcare-owned part and delegate Media/provider deletion.
- If approved policy says anonymize: remove approved personal fields while preserving required compliance proof and referential integrity.
- If approved exemption says retain: return retain status/reason/evidence to Privacy; do not create DataRetentionExemption locally.
- If legal retention is unresolved: return `retention_policy_unresolved` / review. Never interpret Prisma cascade as legal permission.

#### Audit

- SH-029 records important actions according to root/feature policy.
- SH-030 records sensitive access actual outcome where required.
- Audit failure handling follows root critical-audit policy; required access proof may be fail-closed.
- Audit rows do not replace BAA/profile/boundary/policy truth.

#### Notification

Healthcare emits/request safe lifecycle/remediation intent. Notification decides delivery channels/providers/templates. No PHI or raw legal text.

#### Holds

Healthcare requests a hold only when a local source condition and approved mapping justify it. The Hold owner owns creation/status/release. A revoked/expired BAA does not automatically imply a new generic local `blocked` flag.

### Authorization / Compliance

- Privacy executor is invoked only by trusted Privacy/system context under root service authorization.
- admin exports/access remain subject to SH-002 and Healthcare policy.
- retained evidence stays private and access-audited as applicable.
- erasure/anonymization does not silently destroy required legal/compliance proof.

### Database / Transaction Behavior

- Each Privacy target execution is idempotent and records a stable result back to Privacy through its contract.
- Use row/aggregate locks if privacy mutation races with BAA/provider transition.
- Cross-owner deletion is not a distributed DB transaction; use durable orchestration and idempotent results.
- If a record is retained, ordinary foreign references remain valid or are anonymized according to approved design.

### Events / Jobs

- privacy execution may emit Healthcare owner events if business-visible truth changes;
- provider deletion uses reliable job/retry if asynchronous;
- Media deletion delegated to Media;
- Notification requests may originate from owner events or application orchestration;
- dead-letter behavior visible in Ops.

### Provider Integration

If a provider resource exists and retention permits deletion/anonymization, call the adapter through SH-070. Provider deletion failure is retryable/operational; it does not change local retention disposition to “deleted.”

### UI / Admin Surface

No Privacy request UI. Restricted Healthcare admin views may display safe retention/review state or inability to delete, without legal free-text details not approved for display.

### Failure Behavior

- retention unresolved: `retention_policy_unresolved`, no destructive action;
- provider deletion transient failure: retry/record Ops failure; local status remains accurate;
- Media deletion unavailable: report partial target execution to Privacy according to canonical protocol, do not fake completion;
- audit-required access proof unavailable: fail according to root critical-audit policy;
- stale privacy instruction after source changed: return conflict/current target facts for orchestrator reevaluation;
- hold/notification dependency failure: domain truth remains authoritative; durable request retry according to owner protocol.

### Tests

- privacy subject enumeration by ProfessionalProfile/User lineage;
- retained/review/erase/anonymize dispositions;
- U-18 unresolved path prevents hard delete;
- BAA cascade regression: production executor does not blindly cascade-delete retained BAA proof;
- Media/provider deletion delegation and retry;
- SH-029/030 invocation and payload minimization;
- hold request/release idempotency for approved conditions;
- Notification request contains no PHI;
- Ops failure record does not change Healthcare status;
- concurrent privacy vs BAA transition safety.

### Documentation Updates

- If legal retention periods or U-07 proof retention are approved, update Module architecture Section 28 and the Cluster unresolved register.
- Document exact privacy target mappings and anonymization fields.

### Acceptance Criteria

1. Privacy can enumerate and execute Healthcare targets without direct ownership of Healthcare tables.
2. Unresolved retention never causes destructive deletion.
3. Media/provider deletion is delegated through owner interfaces.
4. Required sensitive accesses and important actions create canonical Audit requests.
5. Notification and Hold are consumed, not copied.
6. Ops failures remain diagnostic only.

### Exit Gate

Privacy, retention, audit, notification, hold, provider-deletion, telemetry-redaction, and concurrency tests pass. Every destructive path is either backed by approved retention policy or explicitly blocked/review.

---

# Phase 6 — Module Hardening and Production Verification

## 10 — Healthcare Security, Replay, Concurrency, Reconciliation, and Production Hardening

### Objective

Harden every enabled Healthcare path against stale state, concurrent actions, replay, provider outage, sensitive-data leakage, privacy/retention mistakes, cross-Module coupling, and unresolved legal paths before production activation.

### Observable Result

- All enabled Healthcare commands remain deterministic under retries and concurrency.
- Provider-disabled/enabled configurations are explicit and safe.
- Operators can see failed/retry/dead-letter/reconciliation states without treating Ops as domain truth.
- Sensitive access is authorization-layered, server-redacted, and audited.
- Backfills/migrations are dry-run/recoverable where needed.
- Every unresolved U-* item is classified as resolved, production blocker, or explicitly excluded from production scope.
- Final Module readiness report proves CL-03 Feature 06/11/12/13 participation and all Module exit gates.

### Cluster Build-Plan Link

Healthcare portion of **CL-03 Feature 13 — CL-03 Security, Reliability, Reconciliation, Backfill, Compliance, and Production Hardening**.

### Dependencies

- Module Features 01–09 complete.
- Root deployment/security/observability standards.
- Current unresolved decision register reviewed.
- Real dependency interfaces available for all production-enabled paths.
- Live provider credentials/config only if provider automation passed Feature 06 requirements.

### In Scope

- authorization/RLS/server-handler alignment for Healthcare-owned records/routes;
- end-to-end Zod validation coverage;
- command idempotency/replay tests;
- transition/concurrency stress tests;
- provider replay/out-of-order/outage/reconciliation tests if enabled;
- expiry scheduler reliability;
- event outbox/inbox replay behavior;
- audit completeness and fail-closed behavior where mandated;
- telemetry/analytics redaction;
- privacy/retention production checks;
- schema migration/backfill dry run if any Healthcare migrations were approved;
- indexing/query performance on Healthcare-owned access patterns;
- boundary/policy target-owner validation under stale/deleted targets;
- feature-gate/config enforcement for legal/provider-disabled paths;
- production readiness report and progress-tracker update.

### Out of Scope

- adding new provider/product lanes solely during hardening;
- resolving legal questions by implementation guess;
- redesigning CL-03 sequencing;
- generic platform infrastructure replacement;
- implementing U-09/U-10 broad semantics unless architecture was already updated/approved.

### Module-Owned Data

All Healthcare-owned models/events and any approved provider-event record. No new source truth merely for hardening.

### Public Interfaces

All production-enabled Module public contracts are frozen/versioned for the release. Breaking changes require architecture/consumer updates.

### Shared Operations Used

Hardening verifies, rather than recreates:

- SH-001/002 authentication/authority;
- SH-008/011–013 consent/holds as applicable;
- SH-020 Healthcare readiness;
- SH-029/030 audit/access proof;
- SH-034/037/038 observability;
- SH-044/045/046 idempotency/event reliability;
- SH-047/048/051/052/053/055 jobs/concurrency/lifecycle;
- SH-059–062 provider shell where enabled;
- SH-070/078 provider privacy/security;
- SH-087/090 Media boundary;
- SH-091 Search boundary through source owner;
- SH-095–098 Privacy protocol;
- SH-123 target-owner validation.

Any discovery of a local duplicate is a hardening failure, not a reason to preserve it.

### Domain Logic

- Re-run the full SH-020 matrix against production-enabled actions/context.
- Verify every status mutation enters through a named command/transition policy.
- Verify BAA/profile summary cannot drift.
- Verify no boundary clear/inheritance or policy-history behavior is reachable unless resolved.
- Verify `lockedHealthcareFlag` remains unused as policy truth until resolved.
- Verify every provider state must pass adapter normalization/transition validation.
- Verify any cache/read model is rebuildable and not authoritative.

### Authorization / Compliance

- penetration-style authorization tests for cross-user/profile/target access;
- admin/support role never bypasses Healthcare policy;
- step-up enforced only for approved action matrix and through SH-014;
- PHI/private evidence absent from logs/analytics/events/notifications;
- private Media access short-lived and access-audited where required;
- legal-gated paths feature/config disabled when unresolved.

### Database / Transaction Behavior

- race tests for all critical aggregates/resources;
- transaction rollback/outbox atomicity tests;
- unique constraint behavior under load;
- approved provider-event dedupe uniqueness;
- migration/backfill scripts idempotent and dry-run capable;
- no cascade deletion of retention-sensitive BAA proof through production Privacy path without approved policy;
- query plans/indexes reviewed for profile lookup, BAA status/expiry, exact boundary, exact policy.

### Events / Jobs

- outbox retry and duplicate publish;
- consumer inbox replay/out-of-order;
- expiry job lease/retry/dead-letter;
- provider reconciliation/dead-letter if enabled;
- correlation/request IDs maintained across async hops;
- jobs use minimized payloads, not PHI/document blobs.

### Provider Integration

For every live provider:

- credential rotation/config verified;
- signature verification tested with raw-body handling;
- event dedupe tested;
- mapping table/version reviewed;
- unknown status fails safe;
- outage/timeouts retry appropriately;
- reconciliation can detect missed callbacks;
- provider data minimization reviewed;
- deletion/anonymization behavior documented/tested if in production privacy scope.

If these cannot be proven, provider automation remains disabled.

### UI / Admin Surface

Where UI exists:

- error/blocked/redacted states are accessible and do not leak PHI;
- no UI claims unsupported legal/provider completeness;
- retry/manual-review instructions map to real supported actions;
- client never receives raw data merely to hide it visually.

### Failure Behavior

- any dependency uncertainty on sensitive path fails closed or returns explicit dependency-unavailable according to contract;
- dead-lettered provider/job work cannot silently mark business completion;
- audit-required failure follows root policy;
- unresolved legal path returns unavailable/review;
- migration mismatch aborts deployment rather than approximating data;
- stale Search/public projection is repaired through source-owner/Search reconciliation without changing Healthcare truth.

### Tests

Required final suites:

- typecheck;
- lint/format;
- Healthcare domain unit suite;
- repository/database integration suite;
- lifecycle/state transition suite;
- authorization/RLS suite;
- SH-020/public contract suite;
- cross-Module contract suite;
- sensitive-access/redaction suite;
- idempotency/concurrency suite;
- event replay/out-of-order suite;
- jobs/expiry/dead-letter suite;
- provider adapter/webhook/reconciliation suite if enabled;
- Privacy/retention suite;
- telemetry/notification redaction suite;
- critical E2E journeys for healthcare-sensitive and non-healthcare flows.

### Documentation Updates

- update Module architecture for every resolved binding decision;
- update CL-03 architecture/build plan only when Cluster-level decision/sequence genuinely changes;
- update provider/library docs for enabled adapter;
- update progress tracker;
- write production readiness report with unresolved blocker disposition and rollback/backfill plan.

### Acceptance Criteria

1. All Module Features 01–09 exit gates remain passing.
2. No production path uses a healthcare User flag, generic sensitivity alone, provider object, Search/Audit/Ops row, or neighboring lifecycle as Healthcare truth.
3. All production-enabled mutations are authorized, validated, idempotent, and concurrency-tested.
4. Every production-enabled provider callback is verified, owner-deduped, translated, reconciled, retryable, and observable — or provider automation is disabled.
5. Sensitive payload handling is server-enforced and audit-complete where required.
6. Privacy/retention behavior is explicit; unresolved destructive actions are disabled.
7. No shared-operation duplicate implementation exists in the Module.
8. No direct foreign repository/table mutation is used for integration.
9. Event/job/provider payloads and telemetry contain no prohibited PHI/secrets.
10. Every unresolved decision is resolved, a production blocker, or explicitly out of production scope.

### Exit Gate

The Module is production-ready only when all required repository commands and CI quality checks pass, all production-enabled critical E2E journeys pass, the unresolved-decision disposition is reviewed, and the Healthcare production readiness/completion report is attached to the progress tracker. A live provider or destructive retention path cannot be waived through this exit gate without the corresponding architecture/legal ruling.

---

# Module Integration Phase

**Phase 4 / Features 07–08 are the explicit Module integration phase.** They prove public contracts rather than database reach-through.

The minimum integration matrix is:

| Boundary | Contract proof required |
| --- | --- |
| Healthcare → Professional Eligibility | SH-020 decision is consumed as one readiness dimension; Healthcare does not own SH-016 composition. |
| Healthcare → Marketplace Supply | Healthcare blocks/allows only through readiness contract; Marketplace alone mutates Offering. |
| Healthcare readiness → Search | Healthcare emits source fact; approved source owner requests SH-091; Search remains projection. |
| Resource owner → Healthcare | Target owner validates exact target/context before Healthcare boundary/policy decision. |
| Healthcare → Media | Healthcare contextual entitlement + Media-owned file mechanics/signed access. |
| Healthcare → Messaging | Healthcare handling instruction + Messaging-owned server-side serialization/redaction. |
| Healthcare → Video | Healthcare boundary/vendor-readiness decision + Video-owned room/token/provider mechanics. |
| Healthcare → Booking/Order | Healthcare consumes owner facts only; Booking/Order lifecycle remains owner-controlled. |
| Healthcare → Audit | SH-029/030 requests with safe metadata; Audit remains proof owner. |

No integration is accepted merely because the Healthcare service can query a neighboring Prisma model.

# Module Hardening Phase

**Phase 6 / Feature 10 is the hardening phase.** It specifically covers:

- state-transition races;
- command/provider/event replay;
- provider outage and reconciliation;
- BAA expiry worker behavior;
- target/reference staleness;
- server-side redaction and access audit;
- privacy/retention and cascade-deletion risk;
- telemetry/notification/event payload safety;
- migration/backfill/recovery;
- query/index performance;
- legal/provider feature gates;
- final public contract/version stability.

Hardening must not add an architecture concept whose only justification is “production convenience.”

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | 01 Healthcare Contracts, Repositories, and Ownership Guardrails; 02 Healthcare Lane Declaration and Baseline SH-020 Readiness |
| 2 | Core Healthcare Lifecycles and Access Policy | 03 BAA Manual / Provider-Neutral Lifecycle and Profile Summary; 04 Exact Healthcare Data Boundaries and Safe Target Validation; 05 Exact-Target Admin Payload Policy and Sensitive Access Decision |
| 3 | Provider, Expiry, and Worker Boundary | 06 BAA Expiry, Provider-Neutral Port, and Gated Provider Automation |
| 4 | Module Integration and Cross-Cluster Contract Proof | 07 Professional Eligibility, Marketplace, and Public-Readiness Integration; 08 Resource-Owner Enforcement for Media, Messaging, Video, Booking, and Order Contexts |
| 5 | Governance, Privacy, Audit, and Retention Integration | 09 Privacy Executor, Retention, Audit, Notification, and Operational Completion |
| 6 | Module Hardening and Production Verification | 10 Healthcare Security, Replay, Concurrency, Reconciliation, and Production Hardening |

**Total numbered features: 10.**

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture.
2. Read root code standards.
3. Read Canonical Shared Operations Registry/Architecture.
4. Read CL-03 architecture and build plan.
5. Read this Module architecture and implementation plan.
6. Read public-interface sections for every direct dependency used by the feature.
7. Check `context/context-map.md`: the progress tracker is missing; read available approved ADR/rulings for U-07–U-18 and U-HC-* without substituting them for the tracker.
8. Confirm the prior numbered feature exit gate is passing.
9. Produce one concise Feature Implementation Specification using the required template below.
10. Implement only the current feature.
11. Run the feature's required unit/integration/contract/security/concurrency checks.
12. Verify no neighboring source truth or canonical SH operation was duplicated.
13. Verify public/observable result end to end.
14. Update progress tracker.
15. Update architecture only if an approved binding decision changed.
16. Record unresolved risks/blockers instead of inventing behavior.
17. Do not start the next feature until the current exit gate is explicitly reported as passing.

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce **only that feature's** implementation specification containing:

## Objective

The one concrete result this feature must leave working.

## Observable Result

The behavior a developer/user/admin/worker/consumer can verify when complete.

## Dependencies

- prior Module features;
- direct owner public interfaces;
- canonical SH operations by ID/name;
- schema/migration prerequisites;
- provider/configuration prerequisites;
- unresolved rulings that block any subpath.

## In Scope

Exact commands/queries/policies/repositories/workers/contracts included.

## Out of Scope

Neighboring responsibilities and unresolved behavior explicitly excluded.

## Owned Data Affected

Healthcare models/enums/events/snapshots/provider-event proof affected.

## Public Contracts

Commands, queries/decisions, events, privacy executor, or provider-neutral port changed.

## Shared Operations Consumed

For every SH dependency:

- ID/name;
- canonical owner;
- invocation point;
- Healthcare-local policy;
- prohibited duplicate implementation.

## Permissions / Compliance

- actor/system context;
- SH-002 action/resource;
- consent proof if any;
- healthcare trigger/boundary/readiness;
- hold interaction if any;
- sensitive access/audit requirement;
- step-up if approved;
- legal/provider feature gate.

## Primary Workflow

A short ordered flow from entry → validation/authority → Healthcare policy → authoritative read/write → shared operations → event/audit/notification effects.

## Provider Integration

Provider-neutral port/adapter behavior or explicit `None / disabled` statement.

## Jobs / Events

Event names/versions, outbox, worker/job payload, idempotency key, retry/dead-letter behavior.

## Idempotency / Concurrency

Semantic idempotency key, aggregate/resource lock key, expected-state/version behavior, replay result.

## Error Behavior

Validation/auth/conflict/policy/dependency/provider/review/unsupported outcomes and what must not leak.

## Tests

Exact unit/integration/contract/security/concurrency/provider/privacy/E2E tests required by the feature.

## Acceptance Criteria

Concrete observable conditions.

## Documentation Updates

Which architecture/interface/progress files change if an approved decision was settled.

Do **not** generate specifications for future numbered features in advance.

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed:** number and name.
- **Files added:** exact paths.
- **Files changed:** exact paths.
- **Database changes:** models/fields/indexes/constraints changed, or `none`.
- **Migrations:** migration name/path and purpose, or `none`.
- **Dependencies added:** package/config/provider dependency changes, or `none`.
- **Module public interfaces added/changed:** commands, queries, events, privacy/provider contracts.
- **Shared operations reused:** SH IDs/names and call sites.
- **Events/jobs added:** names/versions/job keys/schedules.
- **Provider adapter changes:** adapter/port/webhook/reconciliation changes, or `none/disabled`.
- **Tests added/changed:** exact suites/files and what they prove.
- **Commands run:** typecheck/lint/test/migration/contract/E2E commands and results.
- **Manual/contract verification:** observable flows exercised.
- **Documentation updated:** architecture/plan/progress/ADR/interface docs.
- **Assumptions:** only evidence-supported implementation assumptions.
- **Known failures:** anything not passing.
- **Remaining risks:** including security/legal/provider/retention risk.
- **Deferred work:** explicitly mapped to later feature or unresolved decision.
- **Exit-gate result:** `PASS` or `BLOCKED`, with each gate condition accounted for.

A completion report may not call an unresolved path “complete” merely because it was omitted. It must state whether the path is disabled/out of production scope or blocks the next feature.

# Final Quality Check

Before treating these context files as implementation-ready and before closing Module Feature 10, verify:

1. Every Healthcare source truth has exactly one owner.
2. No neighboring Module truth was absorbed into Healthcare.
3. SH-020 is Healthcare-owned while Professional Eligibility retains final seller readiness composition.
4. `BaaAgreement` is separate from ConsentLog, Transaction Agreement, Trust verification, and provider state.
5. Healthcare profile BAA summary cannot drift independently of BAA truth.
6. Every canonical shared operation is consumed rather than duplicated.
7. Shared mechanism / separate truth boundaries are explicit for events, provider dedupe, lifecycle machinery, audit, file access, snapshots, Privacy, and Search.
8. Commands and queries have clear owner and failure semantics.
9. Cross-Module reads use public owner interfaces / SH-123 rather than direct foreign repositories.
10. Provider adapters do not become business truth and provider DTOs do not leak into public contracts.
11. Live provider automation is impossible until U-07/U-08 requirements are satisfied.
12. General authorization and Healthcare payload policy are separate gates in the correct order.
13. Redaction/blocking is enforced server-side by the resource owner before payload issuance.
14. Audit, domain events, provider-event proof, and observability are distinct.
15. Privacy orchestration remains Privacy-owned and destructive retention-uncertain paths fail safely.
16. Search remains a downstream projection; Healthcare does not call Typesense or own Search queue state.
17. Boundary retirement/inheritance remains disabled until U-09; policy history/precedence remains limited until U-10.
18. `blocked`/`denied`, `DataSensitivity`, `lockedHealthcareFlag`, effective BAA selection, and BAA evidence gaps are not silently guessed.
19. Every numbered feature aligns to CL-03 Feature 06, 11, 12, or 13 without changing Cluster order.
20. Every numbered feature has tests, acceptance criteria, and an exit gate.
21. A coding agent can execute the plan without inventing architecture or legal/provider semantics.
