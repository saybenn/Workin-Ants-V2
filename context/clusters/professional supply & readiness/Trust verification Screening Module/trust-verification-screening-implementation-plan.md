# Trust Verification / Screening Module Implementation Plan

> **Module ID:** `trust_verification_screening`  
> **Module name:** Trust Verification / Screening Module  
> **Module type:** `compliance_trust_capability`  
> **Build status:** `mvp_active_legal_gated`  
> **Primary Cluster:** `CL-03 — Professional Supply & Readiness`  
> **Repository target:** `context/modules/trust-verification-screening/implementation-plan.md`  
> **Architecture dependency:** this Module `module-architecture.md` and `context/professional-supply-readiness/architecture.md`  
> **Plan status:** Ordered Module implementation roadmap; subordinate to the CL-03 `build-plan.md`; it does not redefine Cluster sequencing or architecture.

---

## Core Principle

Implement Trust Verification / Screening through narrow, owner-preserving, verifiable slices:

```text
public / observable behavior
→ validated command or query
→ Trust-owned policy
→ authoritative Trust write/read
→ canonical shared-operation calls
→ event / audit / notification / projection effects
→ tests
→ explicit exit gate
```

A valid slice may terminate in a stable Trust public command/query, a restricted admin surface, a provider-normalized lifecycle transition, a worker result, or a privacy executor. Do not invent UI merely to make an infrastructure/compliance capability look vertical.

The implementation must preserve:

```text
VerificationCheck / ProfessionalLicenseCredential = Trust truth
TrustBadge = display projection
provider state = evidence input
ConsentLog = generic acceptance proof
ComplianceHold = external reusable stop sign
Search = downstream projection
```

No feature may make a legal-gated or architecture-unresolved path operational by inventing missing proof, policy, or schema.

## Build Rules

1. Follow the repository-current root architecture, code standards, Canonical Shared Operations Registry, CL-03 architecture/build plan, this Module architecture, and this plan.
2. Trust owns only declared verification truth. It must not absorb `ProfessionalProfile`, `CandidateProfile`, `Offering`, `Gig`, `Job`, `JobApplication`, `Order`, `ConsentLog`, `ComplianceHold`, `MediaAsset`, Search, Notification, Audit, Privacy, or Observability lifecycles.
3. Cross-Module facts come through approved public interfaces or versioned events, not direct foreign Prisma reads by default.
4. Reuse canonical `SH-###` operations. Missing shared capability is fixed/implemented at its canonical owner, never copied into Trust.
5. Every browser/server, webhook, admin, and worker trust boundary is runtime validated; TypeScript types alone are insufficient.
6. Protected mutations resolve an authenticated or approved system actor and authorize the named resource action server-side.
7. Trust lifecycle transitions are explicit, transition-validated, and transaction-safe. No generic `setStatus` public command.
8. Provider details remain behind Trust-owned provider-neutral ports and provider-specific adapters.
9. A provider event may change Trust only after signature verification, Trust-owned dedupe, translation, and transition validation.
10. `VerificationCheck.lastProviderEventId`, `AuditEvent`, and Payment's `ProcessedStripeEvent` are not complete Trust provider-event dedupe truth.
11. Provider side effects are idempotent, and the canonical Trust check exists before an outbound screening side effect where correlation requires it.
12. Generic jobs, retries, deadlines, locks, audit, media, notification, Search, privacy, and observability stay external shared capabilities.
13. `TrustBadge` is never readiness truth.
14. Consent & Disclosure owns generic versioned proof; Trust decides whether that proof is sufficient for the check.
15. Screening fees use Transaction / Order; payment never marks verification passed.
16. Do not store raw SSNs or full background reports in ordinary application tables. Prefer vendor-hosted sensitive collection.
17. Local ID/license evidence uses Media / File Access; a clean file is not a verified credential.
18. A failed background check does not directly suspend/reject another Module's record. Use approved FCRA/hold/owner workflows.
19. Search is projection. Trust requests refresh; it does not write Search queue/index state directly.
20. Privacy owns privacy-rights orchestration; Trust only executes against its own data/provider resources.
21. Audit and observability records do not substitute for Trust lifecycle/provider-event truth.
22. Async work has stable idempotency/correlation, retry classification, terminal/dead-letter behavior, and safe telemetry.
23. Each numbered feature must pass its exit gate before the next dependent feature starts.
24. Unresolved decisions produce explicit unavailable/review/disabled behavior rather than guessed implementation.
25. If implementation settles a Proposed Ruling or Unresolved decision, update architecture before or in the same change.

## Preconditions

### Hard platform dependencies

Before production use of the behavior that depends on them, the repository must provide:

- approved Prisma/PostgreSQL access and migration workflow;
- root runtime-validation convention;
- **SH-001 `resolveAuthenticatedActor`**;
- **SH-002 `authorizeResourceAction`**;
- **SH-044 `executeIdempotentCommand`** or root-approved equivalent;
- root-approved DB concurrency primitives;
- **SH-046 `publishDomainEvent`** / transactional outbox before async correctness is claimed;
- **SH-029 `appendAuditEvent`** and **SH-030 `recordSensitiveAccess`**;
- safe structured logging/operational failure boundary.

### Hard public-interface dependencies by feature

- Consent: **SH-008 `queryConsentProof`**, **SH-010 `presentStandaloneConsent`**.
- Taxonomy/target facts: **SH-022 `resolveTaxonomyRequirements`**, **SH-123 `validateOwnedTargetReference`** where approved.
- Subject/context owners: narrow ProfessionalProfile/CandidateProfile/Job/Application context interfaces as needed.
- Order: **SH-107 `createChargeableOrder`** and authoritative fee/payment facts when paid screening is enabled.
- Media: **SH-090** validated contextual asset and **SH-087** signed access before local document evidence is enabled.
- Holds: **SH-011/012/013**.
- Notification: **SH-041** before automated delivery requests are enabled.
- Search: **SH-091** before public Trust projection refresh is enabled.
- Privacy: **SH-095/096/097/098** before production privacy fulfillment is claimed.
- Jobs: **SH-047/048/055** before expiry/recheck/reconciliation workers are enabled.
- Provider callbacks: **SH-059/060/061/062** plus approved Trust provider-event truth before live webhook side effects.

### Existing Trust source records

Use the existing Prisma records rather than parallel aggregates:

`VerificationRequirement`, `VerificationConsent`, `VerificationPackage`, `VerificationPackageItem`, `VerificationCheck`, `FcraAdverseActionWorkflow`, `ProfessionalLicenseCredential`, and `TrustBadge` plus their owned enums/statuses.

### Legal / architecture gates

Keep visible throughout implementation:

- **U-03:** `VerificationConsent` vs `ConsentLog` proof split.
- **U-04:** Trust processed-provider-event schema.
- **U-05:** credential ↔ check provenance.
- **U-06:** FCRA notice/delivery/retention proof and final transition rules.
- **U-18:** exact Trust retention periods.
- employer/Organization/Job/Application/permissible-purpose screening request context.
- requirement action vocabulary beyond publish/apply/ranking boost.
- broad `VerificationCheckType` / `TrustBadgeType` semantics.
- mixed-provider package support.
- Trust evidence Media linkage.
- `reportToken` semantics/protection/retention.

### Interfaces that may initially be stubbed

Professional/Candidate safe context, Offering/Gig/Job target facts, Order fee result, Media readiness/access, Notification, Search refresh, Privacy instruction, and Audit/Ops sinks may be strict test doubles while their owners are incomplete. The stub must match the owner contract and must not become a permanent Trust-owned implementation.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 — Module Contracts, Validation, Repository, and Lifecycle Foundation

### Objective

Establish runtime schemas, Trust public/internal contracts, owner repositories, stable result/reason categories, and explicit lifecycle-policy entry points without enabling live provider workflows.

### Observable Result

- Commands/queries accept validated inputs and return stable owner-specific results.
- Only Trust repositories mutate Trust-owned tables through Module application services.
- Invalid status jumps are rejected by lifecycle policy.
- Public contracts do not expose Prisma rows or provider SDK objects.
- Validation, authorization, conflict, dependency-unavailable, review-required, and legal-gated results are distinguishable.

### Cluster Build-Plan Link

Supports **CL-03 Feature 04 — Verification Requirements, Consent, Packages, and Manual Check Path**.

### Dependencies

Current Trust schema/enums; root validation/data/transaction conventions; SH-001, SH-002, SH-044, SH-046 contracts; Module architecture sections on folders, lifecycles, contracts, concurrency, errors, and invariants.

### In Scope

- runtime schemas for public commands/queries/provider-neutral inputs;
- Trust repository interfaces and Prisma implementations;
- lifecycle policy services for packages, checks, credentials, badges, FCRA;
- stable error/result and Trust reason-code namespace;
- safe internal/public DTOs;
- root transaction/idempotency composition;
- test fixtures/builders;
- only already-approved indexes/constraints.

### Out of Scope

Requirement/package workflows, check initiation, provider calls/webhooks, FCRA automation, local Media workflow, Search projection, privacy execution, provider-event schema, or unresolved transition migrations.

### Module-Owned Data

All current Trust models may be read/written in repository tests; no new aggregate is introduced.

### Public Interfaces

Define shapes for SH-017, SH-018, check initiation/manual review/status, requirement/package admin, safe credential/badge queries, provider-neutral ports, Trust privacy executor, and versioned domain events. Enable behavior only in later features.

### Shared Operations Used

- **SH-001 — Identity & Access:** protected entry actor resolution. Local policy: Trust action/target. Prohibited duplicate: `verificationAuth.ts`/current-user helper.
- **SH-002 — Role / Authority:** protected resource authorization. Local policy: Trust resource facts/action vocabulary. Prohibited duplicate: local role engine/`isAdmin` shortcut.
- **SH-044 — platform idempotency:** command contract. Local policy: semantic identity/replay. Prohibited duplicate: Trust idempotency store.
- **SH-046 — event/outbox:** domain-fact publication. Local policy: Trust event payload/version. Prohibited duplicate: fire-and-forget emitter.
- **SH-053 — shared lifecycle plumbing, separate policy:** transition mechanics if available. Local policy: all Trust transition graphs. Prohibited duplicate: global provider/Trust state engine.

### Domain Logic

`VerificationCheck` is screening truth; `TrustBadge` is projection. Provider statuses are adapter inputs. `VerificationConsent` is constrained by U-03. Terminal checks preserve history; recheck should create a new attempt unless a later approved ruling changes that rule.

### Authorization / Compliance

Contracts distinguish subject, reviewer/admin, worker/system, and provider-callback contexts. Generic DTOs exclude raw reports, SSNs, tokens, and unnecessary provider data.

### Database / Transaction Behavior

Repository writes use owner application transactions. No in-memory locks. Do not invent an active-check uniqueness constraint, provider-event table, or credential-check relation while their semantics remain unresolved.

### Events / Jobs

Define event contracts such as requirement changed, check created/status changed, credential status changed, badge changed, and FCRA status changed. No worker is enabled.

### Provider Integration

Define provider-neutral ports and normalized error/result envelopes only. Provider SDK types remain adapter-local.

### UI / Admin Surface

None required.

### Failure Behavior

Invalid input fails before DB access; unauthorized access returns minimized denial; invalid transition returns conflict; unsupported policy returns unavailable/review; repository failure is operational, not fabricated domain truth.

### Tests

Unit validation/lifecycle tests; public-contract serialization tests; repository integration/transaction tests; sensitive-field non-leakage; regression that badge/provider status cannot satisfy readiness.

### Documentation Updates

Update architecture only if a binding contract/transition decision legitimately changes; record final file paths if root standards differ from proposed folder structure.

### Acceptance Criteria

All enabled entry points are runtime validated; public contracts hide Prisma/provider objects; transitions are policy-controlled; unresolved schema issues remain unresolved; unit/contract/integration tests pass.

### Exit Gate

Feature 01 passes when later features can use a validated, owner-preserving Trust foundation without bypassing lifecycle or enabling provider/legal-gated behavior.

---

## 02 — Verification Requirement and Package Configuration

### Objective

Allow authorized administrators to configure verification requirements and screening packages without hardcoded target/check/pricing policy in consumers.

### Observable Result

Requirements and packages can be created/maintained; package totals derive from items plus platform fee; invalid targets/config cannot activate; inactive/retired configuration is excluded from normal active reads.

### Cluster Build-Plan Link

Implements the configuration portion of **CL-03 Feature 04**.

### Dependencies

Feature 01; SH-001/002/022/123/044/046/029; current requirement/package/item schema.

### In Scope

Requirement CRUD/activation; package draft/update/activate/pause/retire; item add/update/remove/reorder; package quote; server validation; target reference validation; safe existing `ruleJson` use without hidden new action semantics; config events.

### Out of Scope

Readiness/satisfaction, check initiation, consent, Order/payment, provider submission, mixed-provider packages, new action vocabulary hidden in JSON, Search.

### Module-Owned Data

`VerificationRequirement`, `VerificationPackage`, `VerificationPackageItem`, and related Trust enums/statuses.

### Public Interfaces

Requirement admin commands, package lifecycle/item commands, `getVerificationPackageQuote`, and safe admin reads.

### Shared Operations Used

- **SH-001/002:** admin actor/authorization; local policy = Trust config action; prohibit local admin-role helpers.
- **SH-022:** canonical taxonomy trigger context; local policy = Trust requirement record; prohibit hardcoded category maps.
- **SH-123:** owner target validation; local policy = requirement applicability; prohibit generic foreign Prisma lookup.
- **SH-044:** mutation idempotency; local semantic fingerprint; prohibit local idempotency table.
- **SH-046:** reliable config change events; Trust payload/version; prohibit untracked callbacks.
- **SH-029:** audit high-impact admin config changes; Trust action/reason; prohibit local generic audit table.

### Domain Logic

Requirement existence declares applicability, not completion. Current typed action flags are publish/apply/ranking boost only. `validityDays` does not itself change status. Package price is data-driven integer currency math. Current package model is single-provider; multi-provider composition remains unsupported. Retired package history is preserved.

### Authorization / Compliance

Configuration mutation is restricted. Consumer quote reads are minimized. Disclosure text is configuration, not consent proof.

### Database / Transaction Behavior

Preserve package/item referential integrity/order; activation validates complete configuration; stale status returns conflict; prefer pause/retire over deleting historically referenced config.

### Events / Jobs

Requirement/package change events as needed. No scheduled job.

### Provider Integration

None; vendor is configuration only.

### UI / Admin Surface

If admin tooling is in scope: requirement manager, package/item editor, calculated total, explicit warnings for unsupported actions/targets. No generic raw-JSON rules editor as the main policy surface.

### Failure Behavior

Invalid target/config → no write/activation; unsupported action → explicit unavailable; stale state → conflict; duplicate mutation → idempotent replay; required dependency outage → fail closed for activation.

### Tests

Unit price/status/action rules; integration persistence/references; authorization; target/quote contracts; concurrency/idempotency; regression against hardcoded totals/readiness inference.

### Documentation Updates

Record any newly approved action/target/package semantics; architecture update precedes multi-provider support.

### Acceptance Criteria

Owner-correct configuration and deterministic quote exist; consumers need no local rules/pricing copy; unsupported composition is explicit; tests pass.

### Exit Gate

Feature 02 passes when requirements/packages are safely configurable and no configuration record is treated as proof of completed verification.

---

## 03 — Consent-Gated Check Initiation and Manual Review

### Objective

Create the first complete verification-attempt path: consent and optional fee prerequisites → idempotent `VerificationCheck` → authorized manual review, without a live screening provider.

### Observable Result

Missing required consent produces a consent-required result; no-fee/manual checks can be initiated and completed; paid screening uses Order or remains explicitly unavailable; duplicate initiation does not create duplicate semantic attempts.

### Cluster Build-Plan Link

Completes the manual/check-initiation portion of **CL-03 Feature 04**.

### Dependencies

Features 01–02; SH-001/002/008/010/044/046/051; SH-107 if paid path enabled; subject owner context; U-03 constraint.

### In Scope

Consent sufficiency; canonical ConsentLog query; constrained `VerificationConsent` linkage; idempotent initiation; canonical check creation before side effects; optional screening-fee Order reference; supported manual review; safe status query; events/audit.

### Out of Scope

Live provider callback, provider-event schema, credential provenance, badge issuance, expiry worker, FCRA automation, broad employer screening request model, raw reports/SSNs.

### Module-Owned Data

`VerificationCheck`, approved `VerificationConsent` linkage, references to requirement/package/ConsentLog/optional Order, safe lifecycle/timestamps/reason fields.

### Public Interfaces

`initiateVerificationCheck`, `completeManualVerificationReview`, `getVerificationCheckStatus`, approved pre-terminal cancel command, and fee-prerequisite/quote read.

### Shared Operations Used

- **SH-001/002:** actor and subject/reviewer authorization; prohibit Trust auth/reviewer role engine.
- **SH-008/010:** canonical consent proof/standalone presentation; Trust policy selects required type/version/vendor/purpose; prohibit `fcraConsentStore` or checkbox-as-proof.
- **SH-107:** chargeable Order; Trust supplies package quote/disclosure; prohibit screening checkout/payment truth.
- **SH-044:** check/manual command idempotency; Trust semantic identity; prohibit `createCheckOnce` store.
- **SH-051/root DB lock:** prevent duplicate active attempt under approved semantics; prohibit in-memory mutex.
- **SH-046:** check events/outbox; prohibit direct downstream callbacks.
- **SH-029:** manual reviewer audit; prohibit generic review audit table.

### Domain Logic

A requirement must be validated as applicable. Missing consent blocks progression. Payment success is only a prerequisite. Create the canonical check before provider side effects. Duplicate active attempts are prevented transactionally without inventing a permanent uniqueness rule that would break rechecks. Manual results require explicit authority/reason/evidence. Terminal history remains immutable in meaning.

### Authorization / Compliance

Standalone consent is mandatory where required, especially FCRA. Reviewer authority is explicit. Subject views are minimized. A failed background result does not restrict another Module here. No SSN/full report persistence.

### Database / Transaction Behavior

Initiation validates current config/prerequisites, claims semantic attempt, writes check/references/outbox atomically. Manual completion uses expected state/version. Same idempotency key replays; key/input mismatch conflicts. Never mutate ConsentLog or Order rows.

### Events / Jobs

Check created/status changed events; no provider/expiry worker yet.

### Provider Integration

Manual/stub provider only.

### UI / Admin Surface

Onboarding requirement/check status, Consent-owned standalone handoff, Order-owned fee handoff, restricted manual-review queue. No raw report viewer.

### Failure Behavior

Missing consent/fee/state prevents side effect; unauthorized reviewer denied; stale status conflicts; duplicate initiation replays; unsupported check/manual path unavailable; outbox retries after commit.

### Tests

Consent/fee/manual policy unit tests; Consent/Order contracts; DB integration; authorization; idempotency/concurrency; compliance; regression payment ≠ pass and badge irrelevant.

### Documentation Updates

If implementation needs a concrete `VerificationConsent` authority split, stop and resolve U-03 first.

### Acceptance Criteria

Manual/no-fee path works end to end; paid path uses Order or is disabled; consent is owner-correct; duplicate attempts are safe; reviewer action is auditable; tests pass.

### Exit Gate

Feature 03 passes when a supported manual verification can be initiated/completed without provider integration and without expanding U-03 or creating a payment/consent duplicate.

---

# Phase 2 — Public Requirement and Readiness Decisions

## 04 — SH-017 Verification Requirement Resolution

### Objective

Given a supported subject/target/action context, return the active Trust requirements that apply without asserting satisfaction.

### Observable Result

Consumers call SH-017 rather than reading `VerificationRequirement`; result has safe requirement/trigger/currentness metadata; unsupported contexts return explicit unresolved/unavailable results.

### Cluster Build-Plan Link

Implements the SH-017 portion of **CL-03 Feature 04**.

### Dependencies

Features 01–03; requirement config; SH-022/123; subject/target owner facts; SH-001/002; current action vocabulary limits.

### In Scope

SH-017 query, action/subject/target applicability policy, active filtering, deterministic merge/dedupe, safe trigger/evidence references, contract tests for approved professional/marketplace/hiring contexts.

### Out of Scope

Check status/readiness, badges, target lifecycle mutation, new action flags without ruling, Search/provider inference, consumer repository access.

### Module-Owned Data

Read `VerificationRequirement` and safe package/config references only.

### Public Interfaces

**SH-017 `resolveVerificationRequirements`** is canonical. Internal resolver remains private.

### Shared Operations Used

- **SH-017:** implemented here; Trust applicability/reason policy; prohibit consumer `getRequiredChecks` copies.
- **SH-022:** taxonomy triggers; Trust maps to active requirements; prohibit category-name conditionals.
- **SH-123:** validate target references; prohibit generic foreign repository.
- **SH-001/002:** protected/context-sensitive access; prohibit local auth.
- **SH-034:** safe telemetry; prohibit raw target/provider logging.

### Domain Logic

Resolution answers what is required, never whether completed. Only active rules participate. Overlapping triggers resolve deterministically. Unsupported actions beyond current typed flags fail explicit. Broad check types are only returned where documented; do not overlap Payment/Healthcare. Consumers never interpret provider state.

### Authorization / Compliance

Return only minimum requirement facts; no subject result/report detail. Unsupported employment screening context fails closed.

### Database / Transaction Behavior

Read-only under consistent query semantics. Add indexes only for approved query needs.

### Events / Jobs

None; config changes already emit owner events.

### Provider Integration

None.

### UI / Admin Surface

Consumer UIs may show requirement/remediation labels; no new generic UI required.

### Failure Behavior

Invalid target, dependency outage, unsupported action/subject, or malformed config yields safe non-allow/unavailable/review result and ops diagnostic where appropriate.

### Tests

Applicability/merge unit tests; SH-017 contract; real DB config integration; dependency failure; security; regression resolution ≠ completion.

### Documentation Updates

Any newly supported action first updates architecture/action vocabulary/contract.

### Acceptance Criteria

Supported consumers can resolve deterministic requirements without Trust DB access; unsupported contexts fail explicitly; no satisfaction logic leaks in; tests pass.

### Exit Gate

Feature 04 passes when SH-017 is the only supported external requirement boundary for current Trust contexts.

---

## 05 — SH-018 Verification Readiness and Safe Evidence Queries

### Objective

Let consumers ask whether SH-017 requirements are currently satisfied from Trust truth without inspecting checks, credentials, badges, or provider state directly.

### Observable Result

SH-018 distinguishes satisfied, missing, pending, failed, needs-review, expired, revoked, cancelled, and policy-unresolved cases with safe evidence references. Subjects/admins can read minimized status summaries. Badge never satisfies readiness.

### Cluster Build-Plan Link

Completes the Trust decision portion of **CL-03 Feature 04** and supplies Trust input to CL-03 Professional Readiness composition.

### Dependencies

Feature 04; Feature 03 manual checks; current-time/expiry semantics; SH-015 may guide but is only Proposed; authorization/sensitive-access interfaces.

### In Scope

SH-018; requirement-to-evidence matching; currentness evaluation; stable Trust reason codes; safe evidence refs; check/subject/credential/badge summary queries; caller-sensitive redaction.

### Out of Scope

Provider callbacks, badge automation, Professional Eligibility composition, healthcare/financial readiness, Search ranking, FCRA final restriction, persistent `verificationReady` source record.

### Module-Owned Data

Read requirements, checks, approved credential evidence, badge only for display queries, and FCRA state only where approved policy affects evidence usability.

### Public Interfaces

**SH-018 `evaluateVerificationReadiness`**, safe check/subject/credential summaries, and active badge display projection query.

### Shared Operations Used

- **SH-018:** implemented here; Trust satisfaction/reason policy; prohibit `isVerified`, `backgroundPassed`, consumer matrices.
- **SH-017:** canonical requirement source; prohibit second resolver.
- **SH-002:** access to status/evidence summaries; prohibit local authz.
- **SH-030:** sensitive evidence access proof; prohibit `verificationEvidenceLog` duplicate.
- **SH-034:** telemetry redaction; prohibit provider/report object logs.

### Domain Logic

Evaluate as of explicit time. Expired/currentness rules apply even to previously passed checks. Failed/review/expired/revoked/missing evidence cannot be overridden by badge. Credential satisfaction requires an approved mapping/provenance; respect U-05. Aggregate multiple requirements with per-requirement reasons rather than one opaque boolean. Consumers must not infer seller/job eligibility from a Trust pass.

### Authorization / Compliance

Subject views show safe status/remediation only; admin/support detail depends on authority/sensitivity; deny responses avoid leaking background information; no raw report/provider payload.

### Database / Transaction Behavior

Read-only, indexed by subject/status/expiry as needed. No readiness cache/source table.

### Events / Jobs

None new.

### Provider Integration

None required; normalized canonical state only.

### UI / Admin Surface

Verification checklist/status and restricted admin metadata may consume these queries; badge display is explicitly projection.

### Failure Behavior

Dependency unavailable → unavailable/retryable, never allow; inconsistent evidence → review/fail-safe; unsupported mapping → policy-unresolved; unauthorized → minimized denial.

### Tests

All check statuses; expiry boundary; multi-requirement aggregation; SH-018 contract; DB evidence integration; redaction; badge/KYC/Healthcare separation; dependency failures.

### Documentation Updates

Document any approved new requirement/evidence mapping before code treats it as truth.

### Acceptance Criteria

SH-018 derives only from Trust truth plus approved owner context; deterministic reasoned results; no readiness boolean/source table; safe reads; tests pass.

### Exit Gate

Feature 05 passes when SH-017/018 provide a complete contract-testable Trust requirement/readiness boundary for the manual/no-live-provider MVP path.


---

# Phase 3 — Provider, Credential, Expiry, and Trust Projection

## 06 — Provider-Neutral Ports, Hosted Collection, and Safe Submission

### Objective

Allow a configured Trust adapter to create vendor-hosted collection/session context and submit an eligible canonical `VerificationCheck` idempotently, while live callback mutation stays gated by U-04.

### Observable Result

A supported provider can receive an outbound screening request; sensitive collection is provider-hosted where supported; provider IDs are stored only as correlation facts; repeated submission does not order duplicate checks; provider objects/statuses do not become public/domain truth.

### Cluster Build-Plan Link

Begins the provider portion of **CL-03 Feature 05 — Verification Providers, Credentials, Expiry, Trust Projection, and FCRA Boundary**.

### Dependencies

Features 01–05; selected provider credentials/configuration; SH-001/002/008/044/047/048/078/037 and Order prerequisite where needed; SH-059–062 contracts for later inbound work; U-04 remains a hard callback gate.

### In Scope

Provider-neutral `ScreeningProviderPort`; Checkr/Certn-style adapter shells for actually selected providers; hosted collection/session creation; provider submission command; outbound canonical mapping; safe provider correlation persistence; normalized retryable/permanent errors; idempotent submission/retry; configuration health checks.

### Out of Scope

Live webhook state mutation without U-04; unapproved provider-event table; automated adverse action; full report storage; provider SDK objects in public DTOs; mixed-provider packages; provider-specific business status enums; unresolved `reportToken` persistence.

### Module-Owned Data

`VerificationCheck` provider/correlation fields and approved package/vendor configuration. `reportToken` remains unused unless architecture settles its protection/retention semantics.

### Public Interfaces

`createVerificationCollectionSession`, `submitVerificationCheckToProvider`, provider-neutral submit/fetch/reconcile/cancel port methods where supported, and a minimized provider-submission status result.

### Shared Operations Used

- **SH-001/002:** authorize submission; Trust policy = who may order this check; prohibit provider-specific auth guards.
- **SH-008:** revalidate required consent immediately before side effect; prohibit provider consent flags as authority.
- **SH-107:** authoritative paid-screening prerequisite when needed; prohibit provider checkout/payment truth.
- **SH-044:** hosted-session/submission idempotency; Trust owns semantic provider-operation key; prohibit local submission lock table.
- **SH-047/048:** durable retry/backoff for technical provider errors; prohibit ad-hoc timers.
- **SH-078 `minimizeAndRedactProviderInput`:** provider payload/log minimization; Trust allowlist remains local; prohibit raw payload logger.
- **SH-037 `recordIntegrationFailure`:** normalized operational failure; Trust safe correlation remains local; prohibit integration failure as check lifecycle truth.

### Domain Logic

Immediately before provider side effect, re-check expected check state, current consent, fee Order if required, provider config, and any approved hold prerequisite. Canonical check exists first. Provider ID is correlation only. Unknown/ambiguous response never marks passed. If provider acceptance succeeds but local acknowledgement is lost, recovery uses provider idempotency/reconciliation rather than blindly submitting a second check.

### Authorization / Compliance

Only the subject or explicitly approved workflow/admin may initiate. Broad employer screening remains disabled until request/permissible-purpose context is approved. Credentials/secrets are server-only. Prefer vendor-hosted SSN/background collection. Expose only short-lived provider handoff information required by the subject flow.

### Database / Transaction Behavior

Claim local provider-operation intent/idempotency before the external call without holding a long DB transaction. Post-call persistence uses expected state and does not overwrite newer terminal state. Repeated calls reuse the provider/idempotency identity supported by the adapter.

### Events / Jobs

Submission requested/accepted/failure facts as appropriate; durable retry for transient failure. No callback-driven status transition unless Feature 07 and U-04 permit it.

### Provider Integration

Adapter implements configuration validation, hosted collection/session where supported, check submission, normalized response/errors, state fetch/reconciliation, and cancel/delete only when supported. SDK types/secrets stay adapter-local.

### UI / Admin Surface

Subject may be handed to provider-hosted collection and see canonical pending/remediation state. Ops may see provider name, safe correlation ID, canonical status, and normalized failure category—not raw request/report payload.

### Failure Behavior

Consent/fee/state invalid → no call. Timeout before known acceptance → retry only under provider idempotency semantics. Accepted-but-local-write-lost → reconciliation, not blind resubmission. Unsupported provider/check type → configuration error. Unknown status → pending/review plus ops signal. U-04 unresolved → callback mutation impossible.

### Tests

Provider adapter contract mocks; prerequisite/error-classification units; local-check-before-side-effect integration; idempotency/timeout scenarios; secret/redaction tests; provider-status separation regression; feature-gate test that callback side effects remain disabled under U-04.

### Documentation Updates

Document actual enabled provider/configuration and provider-specific idempotency constraints. Provider substitution that changes business semantics requires architecture review.

### Acceptance Criteria

Outbound provider workflow is adapter-isolated and idempotent; prerequisites are revalidated; canonical check exists first; no SSN/full report storage; callback mutation remains gated; tests pass.

### Exit Gate

Feature 06 passes when outbound screening can be exercised safely in mock/sandbox or approved live submission while no unapproved callback side effect exists.

---

## 07 — Verified Provider Events and Reconciliation

### Objective

Process provider results idempotently only after signature verification, Trust-owned event dedupe, provider-status translation, and Trust transition validation; provide safe reconciliation for missed/stuck results.

### Observable Result

If U-04 is approved, signed callbacks claim once, duplicates do nothing, canonical statuses update safely, out-of-order/unknown events do not regress state, and reconciliation repairs missed events. If U-04 is unresolved, live callback side effects are provably disabled while safe provider inspection/reconciliation remains constrained.

### Cluster Build-Plan Link

Implements the inbound/reconciliation portion of **CL-03 Feature 05**.

### Dependencies

Feature 06; SH-059/060/061/062/046/047/048/037/038/078; provider webhook credentials; **U-04 approval for live callback side effects and event-record schema/retention**.

### In Scope

With U-04 approved: smallest approved Trust processed-provider-event record/migration, verified webhook adapter, atomic claim/dedupe, translation, check transition, processing outcome/version/correlation, outbox event, reconciliation worker/admin command. Always: safe unknown/out-of-order handling, reconciliation contract, telemetry, disabled-mode tests.

### Out of Scope

`ProcessedStripeEvent`, AuditEvent as dedupe, `lastProviderEventId` as complete dedupe, indefinite raw webhook bodies, direct Professional/Offering/Job/Application mutation, automatic final adverse action.

### Module-Owned Data

`VerificationCheck` transitions and, only after U-04, Trust-specific processed-provider-event truth with approved uniqueness/integrity/correlation fields.

### Public Interfaces

Provider webhook route delegates to `processVerificationProviderEvent`; `reconcileVerificationProviderCheck`; restricted retry/reprocess where approved; safe ops processing query; versioned check status-change event.

### Shared Operations Used

- **SH-059 `verifyProviderWebhookSignature`:** first callback step; adapter-specific algorithm/secret/tolerance local; prohibit custom unverified webhook path.
- **SH-060 `deduplicateProviderEvent`:** shared mechanics + Trust event truth; prohibit `lastProviderEventId`, AuditEvent, ProcessedStripeEvent.
- **SH-061 `translateProviderStatus`:** adapter mapping to Trust status/reason; prohibit global provider status enum.
- **SH-062 `reconcileProviderState`:** shared repair mechanics, Trust transition policy; prohibit global provider sync truth.
- **SH-046:** outbox after canonical transition; prohibit direct downstream side effects in route.
- **SH-047/048:** retry/dead-letter; only technical errors retry; prohibit bespoke webhook daemon.
- **SH-037/038:** ops failure/queue telemetry; prohibit operational rows as verification state.
- **SH-078:** minimize persisted/logged provider event; prohibit raw report/body persistence by default.

### Domain Logic

Mandatory order:

```text
callback
→ verify signature
→ parse/minimize envelope
→ claim Trust provider event
→ translate provider state
→ load canonical check
→ validate provider correlation + transition freshness
→ write Trust state
→ mark event processing result
→ outbox domain event
```

Duplicate event replays/no-ops; unknown status never passes; stale event never regresses newer terminal state; reconciliation applies the same transition policy; legal/provider rejection is not treated as retryable network failure.

### Authorization / Compliance

Webhook uses constrained system context. Admin reconciliation requires authority and sensitive-access logging where appropriate. No raw report/identity payload in generic logs or ordinary DB fields.

### Database / Transaction Behavior

If U-04 approved: provider+event identity unique (or approved equivalent), event claim/Trust transition/processing result/outbox transactionally coordinated, optimistic/current-state checks prevent regression, only approved minimal integrity hash/reference stored. Without U-04, no substitute schema is invented.

### Events / Jobs

Durable event processing/reconciliation worker if architecture chooses queue handoff; dead-letter/manual recovery; emit status-change only after authoritative write.

### Provider Integration

Adapter extracts signature metadata/event ID/type/minimal fields, maps canonical status, and fetches current provider state for reconciliation. Provider objects do not cross the adapter.

### UI / Admin Surface

Restricted ops view may show check ID, provider, safe external correlation, canonical state, processing/reconciliation outcome, and authorized retry/reconcile. No raw webhook/report viewer.

### Failure Behavior

Invalid signature → reject/no state. Duplicate → no repeated effects. Unknown event/status → safe ignore/review + diagnostic. Out-of-order → no regression. Transient failure → retry. Permanent mapping/validation → dead-letter/manual review. U-04 unresolved → side-effect path disabled.

### Tests

Signature, duplicate replay, out-of-order, unknown status, provider mapping, dedupe race, reconciliation idempotency, redaction, and disabled-mode tests.

### Documentation Updates

When U-04 is resolved, update Module/CL-03 architecture with exact Trust event model, uniqueness, retention, and processing semantics before/with migration.

### Acceptance Criteria

No callback bypasses SH-059/060/061/Trust transition policy; replay/order is safe; reconciliation is observable; no foreign lifecycle is changed; U-04 is resolved or callback mutation is disabled; tests pass.

### Exit Gate

Feature 07 passes when inbound processing is either production-safe under approved U-04 truth or provably disabled while the Module remains operable. An endpoint alone is not completion.

---

## 08 — Professional License Credential Lifecycle and Provenance Boundary

### Objective

Implement durable license/credential state with protected identifiers and Media-owned evidence while refusing to claim check-to-credential provenance until U-05 is resolved.

### Observable Result

A professional can submit allowed credential metadata; authorized reviewer/provider paths can set supported credential outcomes; full license number is not publicly exposed; private evidence uses Media; expired/revoked credential stops satisfying approved SH-018 requirements; unapproved provenance-dependent verification remains disabled.

### Cluster Build-Plan Link

Implements the credential portion of **CL-03 Feature 05**.

### Dependencies

Features 01–07 as applicable; SH-001/002/029/030/044/046/051/053/087/090; root-approved hashing/HMAC/encryption primitive; U-05; Trust evidence Media-link ruling if a dedicated relation is required.

### In Scope

Credential create/update-before-verification, supported review/verification/failure/revoke commands, masked/protected identifier handling, provider reference correlation, safe summary query, Media contextual access when existing interfaces allow, explicit provenance gate.

### Out of Scope

Raw ID/document storage in Trust, upload/scan/signed URL mechanics, “clean file = verified”, unapproved credential-check FK, BAA/Healthcare readiness, broad unapproved employment credential policy.

### Module-Owned Data

`ProfessionalLicenseCredential`, `ProfessionalLicenseStatus`, safe provider/timestamp/expiry/failure fields, masked/protected license identifier fields.

### Public Interfaces

`submitProfessionalLicenseCredential`, pending update, `completeProfessionalLicenseReview`, expire/revoke commands, safe credential summary, optional contextual evidence-access wrapper delegating to Media.

### Shared Operations Used

- **SH-001/002:** subject/reviewer authorization; prohibit credential-local auth engine.
- **SH-090:** accept only validated Media evidence; Trust owns credential meaning; prohibit local file pipeline.
- **SH-087:** signed evidence access; Trust supplies contextual entitlement; prohibit presigned URL helper.
- **SH-030:** sensitive evidence access proof; prohibit duplicate license-view access ledger.
- **SH-029:** admin credential action audit; prohibit generic credential audit store.
- **SH-044/051/053:** idempotency/concurrency/lifecycle mechanics; Trust owns aggregate key/graph; prohibit in-memory locks/generic status setter.
- **SH-046:** credential status events; prohibit direct downstream writes.

### Domain Logic

Credential record is truth. Provider/file result is evidence. `verified` requires approved path and required provenance. If U-05 is unresolved, no code may claim a specific `VerificationCheck` established/refreshed the credential unless a separate explicitly approved evidence contract permits it. Normalize/protect identifiers using root shared crypto. Expired/revoked never satisfies readiness. Negative credential state does not directly suspend ProfessionalProfile.

### Authorization / Compliance

Subject edits only approved pre-verification fields. Only authorized reviewer/system/provider path can mark verified/failed/revoked. Evidence access requires Role/Authority + Trust context + Media and SH-030. Public DTOs expose masked identifier only.

### Database / Transaction Behavior

Expected-state/version or DB lock for transitions. Do not invent uniqueness by license hash/jurisdiction without fraud/identity policy. Status + outbox/audit coordinated. No new Media join or check relation before ruling.

### Events / Jobs

Credential status-change event. Expiry worker is Feature 09. Provider reconciliation optional through existing adapter.

### Provider Integration

Adapter returns normalized credential evidence/reference; never writes credential rows directly.

### UI / Admin Surface

Professional credential submission/status; restricted reviewer evidence metadata; masked identifier; pending/review/expired/remediation states.

### Failure Behavior

Invalid jurisdiction/type, unready Media, unauthorized access, missing provenance, provider outage, or stale state yield explicit validation/review/denied/retry/conflict results; no fabricated verified status.

### Tests

Lifecycle/identifier policy; DB transitions; Media access contracts; sensitive access; concurrent reviewer/provider result; regressions “Media clean != verified” and “provider state != truth”; U-05 gate.

### Documentation Updates

Resolve/update architecture before adding credential-check provenance or Trust-specific Media evidence relation.

### Acceptance Criteria

Credential state is durable/owner-correct; sensitive data is protected; provenance is not invented; expired/revoked affects readiness; tests pass.

### Exit Gate

Feature 08 passes when supported credential lifecycle works without ownership leakage and unapproved provenance-dependent verification remains disabled.

---

## 09 — Expiry, Recheck, and TrustBadge Projection

### Objective

Make verification currentness durable over time, schedule rechecks safely, and maintain badges only as projections of approved current evidence.

### Observable Result

Passed checks/verified credentials expire at approved boundaries; SH-018 updates accordingly; recheck work is not duplicated; supported badges issue/suspend/expire/revoke only when evidence supports the claim; badge changes request Search refresh.

### Cluster Build-Plan Link

Implements expiry/recheck/Trust projection portion of **CL-03 Feature 05**.

### Dependencies

Features 05 and 08; SH-044/045/046/047/048/055/091/041/029; explicit evidence semantics for every badge type activated.

### In Scope

Check/credential expiry policy/commands, recheck scheduling, supported badge lifecycle/rebuild, source-evidence validation, readiness/badge events, Search refresh and safe Notification requests.

### Out of Scope

Badge as readiness truth, unresolved broad badge types, Search indexing/ranking, Notification delivery, generic scheduler, foreign lifecycle mutation.

### Module-Owned Data

Check/credential status/expiry fields and `TrustBadge` projection fields. No readiness cache.

### Public Interfaces

Expire check/credential, request recheck, revoke credential, rebuild badges, active badge projection query, internal badge issue/suspend/expire/revoke commands.

### Shared Operations Used

- **SH-055:** deadline-expiry mechanics; Trust owns deadlines/transitions; prohibit custom cron state updater.
- **SH-047/048:** reliable jobs/backoff; Trust owns job identity/retry classification; prohibit local queue engine.
- **SH-044:** idempotent recheck/badge actions; prohibit once-only helper store.
- **SH-045:** domain-event dedupe; Trust owns reaction identity; prohibit last-event field hacks.
- **SH-046:** owner events/outbox; prohibit Search/Notification before commit.
- **SH-091:** Search refresh request; Trust supplies safe projection identity; prohibit Typesense/index queue write.
- **SH-041:** Notification request; Trust supplies business trigger/safe payload; prohibit direct delivery provider.
- **SH-029:** audit manual revoke/suspend; prohibit badge audit table.

### Domain Logic

Expiry uses explicit clock and owner validity policy. Historical evidence remains. Recheck creates a new attempt under TV-PR-04. A badge type activates only after its claim/evidence mapping is documented. Badge follows evidence but never feeds SH-018. Re-established evidence may reissue/reactivate under approved history policy. Search request occurs after committed Trust state.

### Authorization / Compliance

Workers use constrained system context. Manual revoke/suspend is authorized/audited. Notifications and public badge fields omit sensitive failure/report detail.

### Database / Transaction Behavior

Expiry scans indexed `expiresAt`/status; transitions are stale-safe/idempotent; recheck job key is deterministic by subject/requirement-or-check type/time window; badge write and outbox align transactionally; downstream effects retry after commit.

### Events / Jobs

Expiry worker, recheck/remediation job, badge rebuild/repair, readiness/badge events. Retry technical failures only.

### Provider Integration

A recheck may submit through Feature 06 after prerequisites are revalidated; expiry itself never calls provider directly.

### UI / Admin Surface

Subject sees expiring/expired/remediation; supported badges display through safe projection; admin can invoke approved repair/rebuild. Search diagnostics remain Search-owned.

### Failure Behavior

Duplicate job no-ops; Search/Notification outage does not roll back Trust truth; ambiguous badge evidence withholds/suspends; failed new recheck leaves prior history intact.

### Tests

Time boundary, concurrent expiry/revoke, recheck idempotency, badge mapping, Search/Notification contracts, event replay, badge-not-readiness regression, public projection allowlist.

### Documentation Updates

Document each badge claim/evidence mapping before activation and update architecture before same-row renewal/recheck semantics change.

### Acceptance Criteria

Currentness changes deterministically; SH-018 reflects expiry/revoke; recheck preserves history; only approved badges activate; downstream owner contracts used; tests pass.

### Exit Gate

Feature 09 passes when expiry/recheck/badge projection remains correct under time, retries, and downstream outages without making badge source truth.


---

# Phase 4 — FCRA / Adverse-Action Legal Boundary

## 10 — FCRA Adverse-Action Workflow Boundary

### Objective

Route a background result that may cause adverse consequence into `FcraAdverseActionWorkflow` instead of immediate ban/rejection, implementing only the process/proof that has been legally and architecturally approved.

### Observable Result

A qualifying check can enter the FCRA workflow; authorized reviewers see safe current state/next action; any approved reusable restriction is requested through ComplianceHold; U-06-dependent notice/deadline/final-adverse automation is either fully supported by approved proof or unreachable by configuration/tests.

### Cluster Build-Plan Link

Implements the FCRA boundary portion of **CL-03 Feature 05**.

### Dependencies

Features 05–09; U-06 for production notice/delivery/final-action automation; Consent from Feature 03; SH-008/010/011/012/013/029/030/041/046; SH-055 only after exact dispute-window semantics are approved; approved request/permissible-purpose context for employment screening.

### In Scope

Initialize FCRA workflow for approved qualifying background contexts; restricted manual/admin transitions for approved states; dispute receipt/clearance to the degree current proof supports; safe workflow query; Notification request hooks only for approved versioned notices; Hold request/release after approved source decision; explicit feature gates for unresolved automation.

### Out of Scope

Legal interpretation of criminal records; auto-final adverse from `failed`; direct Professional/Job/Application status mutation; Notification delivery truth inside Trust; invented notice artifact/version/retention; generic appeals/moderation lifecycle; broad employer screening without request/purpose proof.

### Module-Owned Data

`FcraAdverseActionWorkflow` / `FcraAdverseActionStatus`, one-to-one check reference, and only approved timestamps/provider correlation/notes. ConsentLog, Notification/Delivery, and ComplianceHold remain external truth.

### Public Interfaces

Approved subset of `startFcraAdverseActionWorkflow`, dispute receipt/clearance, cancellation, safe status query, and final-adverse request/record commands only after U-06. Do not use names such as `mark...Sent` until the delivery/proof contract justifies that semantic claim.

### Shared Operations Used

- **SH-008/010:** prove/present standalone screening consent; Trust decides sufficiency; prohibit local generic consent authority.
- **SH-041:** request approved adverse-action notification; Trust owns trigger/deadline/template/version intent, Notification owns delivery; prohibit direct email/SMS and treating Notification state as FCRA state.
- **SH-012:** request external ComplianceHold only after approved Trust source decision; prohibit `failedCheckBan`/`verificationBlocked`.
- **SH-013:** request Hold release after source condition clears; prohibit direct hold mutation.
- **SH-011:** evaluate existing holds where FCRA action policy needs it; prohibit local block flag.
- **SH-055:** deadline mechanism only after legal timing approved; Trust owns deadline policy; prohibit hardcoded cron window.
- **SH-029/030:** admin action/sensitive evidence proof; prohibit FCRA workflow truth in generic audit.
- **SH-046:** FCRA status events/outbox; prohibit direct foreign lifecycle writes.

### Domain Logic

Conceptual sequence remains gated by U-06:

```text
qualifying result
→ pre_adverse_required
→ approved notice request + verified proof semantics
→ dispute window
→ disputed OR approved deadline completion
→ cleared_after_dispute OR approved final-adverse path
→ restriction only after approved final source decision
```

`VerificationCheck.failed` is not final adverse action. Trust workflow, Notification delivery, ComplianceHold, and downstream owner lifecycle are separate truths. A dispute can alter the outcome without rewriting the original check. No legal deadline or notice proof is inferred from `notes` or provider UI state.

### Authorization / Compliance

Only approved compliance reviewers/system workflows transition FCRA state. Sensitive access is minimized/logged. Approved notices use Notification-owned delivery/version contracts. Unsupported jurisdiction/workflow or employer-purpose context stays disabled.

### Database / Transaction Behavior

Current unique check→workflow relation is preserved. Transitions use expected state/version. Workflow status/timestamps/outbox/audit intent are coordinated transactionally. Notification/Hold are reliable post-commit effects. Any new proof schema requires architecture update first.

### Events / Jobs

FCRA status-changed event; approved deadline job only after U-06; Notification and Hold requests through reliable outbox/commands; delivery/job failure goes to manual review/dead-letter rather than auto-advance legal state.

### Provider Integration

Provider adverse-action workflow ID is correlation only. Provider workflow does not replace Workin Ants FCRA state/proof.

### UI / Admin Surface

Restricted compliance UI may show safe check summary, FCRA state, approved notice/deadline/proof references, allowed actions, and external Hold reference. No default raw background report viewer.

### Failure Behavior

U-06 unresolved → automated notices/final restriction disabled. Notification outage cannot falsely advance “sent/delivered” state. Deadline worker failure creates visible ops/manual review. Unauthorized review denied. Stale dispute/action conflicts. Hold failure retries externally; Trust does not create a local substitute.

### Tests

Approved lifecycle transitions; compliance regression `failed != final adverse`; Notification delivery-boundary contracts; Hold request/release; approved deadline/time tests; auth/sensitive-access; idempotency/concurrency; U-06 feature-gate tests.

### Documentation Updates

When U-06 is resolved, update Module architecture/compliance proof/Notification contract/retention and schema before enabling automated behavior.

### Acceptance Criteria

Negative screening cannot bypass FCRA boundary into direct adverse lifecycle mutation; workflow/delivery/Hold/foreign state remain separate; unsupported automation stays disabled; approved path is auditable/deterministic; tests pass.

### Exit Gate

Feature 10 passes when Trust safely owns the adverse-action process boundary and prevents illegal shortcuts. Production automated final adverse action may intentionally remain disabled until U-06 is resolved.

---

# Phase 5 — Module Integration

## 11 — Cross-Module Contract Integration and Readiness-Change Propagation

### Objective

Prove Trust works with Professional Eligibility, Marketplace/Hiring contexts, Order-paid screening, Media, Search, Notification, Hold, Audit, Privacy, and Ops entirely through public contracts/events.

### Observable Result

Professional Eligibility consumes SH-017/018 without Trust DB reads; Marketplace and supported Hiring contexts use Trust decisions while retaining lifecycle ownership; paid screening references Order truth; credential files use Media; badge/readiness changes request Search/Notification effects; holds/audit/ops remain externally owned; event replay causes no duplicate downstream effects.

### Cluster Build-Plan Link

Implements the Trust portion of **CL-03 Feature 11 — Readiness Change Propagation / Cross-Module Integration**.

### Dependencies

Features 01–10; Professional Eligibility SH-016 consumer; Taxonomy/Order/Media/Search/Notification/Hold/Audit/Ops contracts; approved Hiring context; SH-045 for event dedupe where event-driven reactions apply.

### In Scope

Contract tests for direct dependencies; real-Trust-DB integration scenarios with dependency test doubles/services; readiness-change event propagation; Search refresh after safe public projection changes; approved Notification requests; Order fee handling; Media evidence access; Hold request/release; safe Trust source projection inputs.

### Out of Scope

Foreign table writes; Professional Eligibility composition implementation; Search ranking/index worker; payment/refund lifecycle; file storage; Hiring lifecycle; broad employment screening without request/permissible-purpose ruling.

### Module-Owned Data

All Trust source records remain owner truth. No integration shadow tables/foreign status snapshots are added merely for convenience.

### Public Interfaces

Freeze/contract-test SH-017, SH-018, check initiation/status/manual review, credential/badge safe queries, Trust domain events, privacy executor, and provider reconcile/webhook contract where enabled.

### Shared Operations Used

- **SH-016 — Professional Eligibility:** integration proves Trust is an input to seller readiness, not owner. Prohibit `professionalCanSell` in Trust.
- **SH-022/123 — Taxonomy/target owners:** canonical context; prohibit target/table copies.
- **SH-107 — Order:** paid screening; prohibit Trust checkout/payment/order lifecycle.
- **SH-090/087 — Media:** validated private evidence/access; prohibit storage/signing mechanics.
- **SH-091 — Search:** projection refresh; prohibit Typesense/Search queue writes.
- **SH-041 — Notification:** delivery request; prohibit direct provider delivery.
- **SH-011/012/013 — Hold:** evaluate/request/release; prohibit local blocked flags.
- **SH-029/030 — Audit:** admin/sensitive proof; prohibit generic logs as audit.
- **SH-037/038 — Ops:** integration/job diagnostics; prohibit ops state as check truth.
- **SH-045 — event inbox dedupe:** idempotent cross-Module reaction; prohibit ad-hoc processed flags on business records.

### Domain Logic

Required workflows:

1. **Professional publication:** owner asks SH-017/018; Trust returns verification decision; Professional/Marketplace decides its action.
2. **Paid screening:** Trust quote → Order-owned transaction → authoritative prerequisite → Trust check/provider flow. Payment never means pass.
3. **Credential evidence:** Trust owns credential meaning; Media owns file safety/access; reviewer/provider changes only Trust credential.
4. **Expiry propagation:** Trust evidence expires → SH-018 changes + domain event → downstream owners re-evaluate; Trust does not mutate them.
5. **Adverse consequence:** Trust/FCRA source decision → approved Hold request → downstream owner reacts to decision/Hold.
6. **Search:** Trust supplies safe badge/source facts and asks Search to refresh; Search owns index/ranking.

### Authorization / Compliance

Each boundary authorizes independently. A consumer allowed to ask readiness is not automatically allowed raw evidence. Sensitive reason codes are audience-filtered. KYC/Healthcare remain distinct. Unsupported employment screening stays gated.

### Database / Transaction Behavior

No distributed/cross-owner write transaction. Trust commit + outbox is atomic locally. Downstream effects are eventually consistent and idempotent; consumers dedupe repeated events.

### Events / Jobs

Contract/integration tests cover check/credential/badge events, Search refresh, Notification request, downstream re-evaluation trigger, Hold request/release, and duplicate replay.

### Provider Integration

Provider adapters stay inside Trust. No consumer receives SDK objects or calls a screening provider through private adapter details.

### UI / Admin Surface

No new generic UI. Existing onboarding/admin/search surfaces may participate in E2E proof.

### Failure Behavior

Owner dependency outage fails safely; Search/Notification outage does not rollback Trust state; repeated event does not duplicate effect; stale consumers re-evaluate current SH-018; unsupported Hiring context returns unavailable/review.

### Tests

Direct dependency contract tests; real Trust persistence + test-double integration; E2E high-risk professional requirement→consent/check→readiness→publication participation; paid screening; credential expiry; badge refresh; event replay; no-foreign-write/no-direct-read regression; audience redaction.

### Documentation Updates

Update versioned interface docs only when a contract legitimately changes; record new approved Hiring context before enabling it.

### Acceptance Criteria

All major boundaries are contract-tested; no foreign DB access is required; replay/outage behavior is deterministic; ownership remains intact; tests pass.

### Exit Gate

Feature 11 passes when Trust participates in its principal CL-03/cross-cluster workflows solely through approved public contracts/events with no ownership leakage.

---

# Phase 6 — Privacy, Audit, Sensitive Access, and Operational Governance

## 12 — Privacy Executor, Retention Gates, Audit, Sensitive Access, and Observability

### Objective

Make Trust governable in production: enumerate/export/erase/anonymize/retain owner data under Privacy instructions, audit sensitive/admin access, and surface safe provider/job failures while U-18-gated destructive retention remains disabled.

### Observable Result

Privacy gets typed Trust data inventory/execution results; permitted erase/anonymize/provider-delete actions are idempotent; retained records return explicit retention-required outcomes; sensitive evidence access uses AccessAuditLog; provider/jobs are observable; telemetry excludes SSNs/full reports/tokens/secrets.

### Cluster Build-Plan Link

Implements the Trust portion of **CL-03 Feature 12 — Privacy / Moderation / Audit / Sensitive Access / Ops integration**.

### Dependencies

Features 01–11; SH-029/030/034/037/038/070/095/096/097/098; U-18 exact retention; U-06 FCRA retention proof; provider deletion capabilities where applicable.

### In Scope

Subject-data enumeration, export contribution, owner-specific privacy execution, retention evaluation/result, provider resource deletion through adapter, sensitive access logs, admin audit, structured logs/metrics/health, redaction policy, dead-letter/manual review visibility.

### Out of Scope

PrivacyRequest/DataErasureJob ownership, guessing retention periods, deleting required FCRA/legal proof, AuditEvent as check/provider history, raw reports for debugging, generic incident system.

### Module-Owned Data

Privacy targets include `VerificationConsent` linkage, `VerificationCheck`, FCRA workflow, credentials, badges, approved Trust provider-event truth if any, and provider resource references. Requirements/packages are generally configuration unless subject-specific data exists.

### Public Interfaces

SH-096 participation (`enumerateVerificationSubjectData`), SH-095 execution (`executeVerificationPrivacyInstruction`), SH-097 retention result, export contribution DTO, SH-070 provider deletion adapter method, safe authorized ops/reconciliation metadata query.

### Shared Operations Used

- **SH-095:** Privacy-owned orchestration → Trust execution; local record/provider semantics; prohibit Trust PrivacyRequest workflow.
- **SH-096:** subject-data enumeration; Trust categories local; prohibit generic cross-domain scanner.
- **SH-097:** retention decision contract; Trust data/legal meaning local, exact duration gated; prohibit ad-hoc delete-after-days.
- **SH-098:** shared anonymization mechanics; Trust field map local; prohibit universal cross-domain eraser.
- **SH-070:** provider deletion contract; Trust provider/legal policy local; prohibit Privacy directly calling provider.
- **SH-029:** generic audit for admin/compliance action; prohibit Trust generic audit store.
- **SH-030:** sensitive-access evidence; prohibit duplicate access ledger.
- **SH-034:** telemetry sanitization; prohibit serialization of raw domain/provider objects.
- **SH-037/038:** provider/job ops visibility; prohibit failure record as check status.

### Domain Logic

Product deletion, privacy erasure, and legal retention are distinct. Trust returns execution evidence to Privacy; Privacy owns workflow state. Where retention applies, preserve minimum required proof and anonymize nonessential fields only when approved. Public badges may revoke/deindex while legally retained source records remain. Provider deletion happens only where legally/provider-supported. Never erase `VerificationConsent` in a way that destroys Consent-owned proof without owner/legal instruction. Ops state never substitutes for domain state.

### Authorization / Compliance

Executor accepts only authorized Privacy/system instructions. Export excludes secrets/tokens/full reports where policy does not authorize them. Sensitive views require purpose + SH-030. U-18/U-06 fail closed on destructive operations.

### Database / Transaction Behavior

Privacy execution is idempotent/replayable; retained rows preserve references/proof; anonymization uses shared deterministic mechanics where required; destructive cascades reviewed before production; provider deletion is durable external work coordinated by approved privacy protocol.

### Events / Jobs

Privacy owner may orchestrate jobs; provider deletion retries technical failures; badge/public visibility removal requests Search refresh; ops failures recorded externally; no independent Trust retention scheduler before U-18.

### Provider Integration

Delete/anonymize/cancel provider resource only through adapter and only if supported/legally allowed. Return safe outcome/reference; never expose credentials/tokens to Privacy.

### UI / Admin Surface

No Trust privacy-request UI. Restricted ops may show safe execution/retention/provider-deletion status. Any evidence viewer invokes SH-030.

### Failure Behavior

Retention unresolved/required → retained/review, not guessed deletion. Provider deletion unavailable → retryable or retained-not-supported. Partial erase → explicit partial failure. Unauthorized sensitive view → deny/audit. Sensitive telemetry serialization is treated as a defect/test failure.

### Tests

Enumeration/export; erase/anonymize/retain idempotency; U-18/U-06 gates; provider deletion; sensitive-access audit; logging redaction; ops-vs-domain separation; Search/public removal request where relevant.

### Documentation Updates

When retention periods become approved, update architecture/retention policy before enabling destructive schedule. Document provider deletion limitations.

### Acceptance Criteria

Privacy can orchestrate without owning Trust records; sensitive/admin proof is correct; telemetry is safe; unresolved retention cannot destroy data; provider privacy work is adapter-isolated; tests pass.

### Exit Gate

Feature 12 passes when Trust is privacy/audit/ops-integrated for its enabled scope and every retention-uncertain destructive action remains explicitly gated.

---

# Phase 7 — Module Hardening and Production Verification

## 13 — Security, Concurrency, Replay, Reconciliation, Backfill, and Production Readiness

### Objective

Prove all enabled Trust behavior remains correct under races, retries, provider outages, event replay, stale state, sensitive access, migration/backfill, and unresolved legal/provider gates.

### Observable Result

Duplicate commands/events/jobs do not duplicate business effects; stale provider events cannot regress state; outages are recoverable/visible; expiry/recheck/badge projection replay safely; sensitive data cannot leak; privacy gates fail closed; backfills are dry-run/idempotent; production-readiness report lists every enabled and disabled capability.

### Cluster Build-Plan Link

Implements the Trust portion of **CL-03 Feature 13 — Hardening and Production Verification**.

### Dependencies

Features 01–12 for enabled scope; root security/deployment/observability standards; current unresolved register; provider sandbox/live test environment where approved; migration/rollback process.

### In Scope

Concurrency/race review; idempotency/replay; outage/reconciliation drills; permission/sensitive-access adversarial tests; payload/log/Search/Notification redaction; query/index/performance review; migration/backfill/rebuild plans; dry-run repair tools; public contract version freeze/deprecation; feature gates for unresolved U-/scope items; final production-readiness report.

### Out of Scope

Resolving law by code, building CL-03-wide shared infrastructure, silently enabling broad employment screening/badge/check semantics, or altering another Module's ownership for convenience.

### Module-Owned Data

Review all Trust models and approved provider-event record if any. Add indexes/constraints only for approved invariants/measured query paths.

### Public Interfaces

Freeze/version SH-017, SH-018, check commands/queries, provider submit/event/reconcile, credential commands/queries, badge projection, supported FCRA commands/query, privacy executor, and Trust events. Document retry/idempotency/conflict/unavailable/review/deprecation semantics.

### Shared Operations Used

Hardening verifies, rather than duplicates:

- SH-001/002 authentication/authority;
- SH-008/010 consent;
- SH-011/012/013 holds;
- SH-029/030/034/037/038 audit/access/telemetry/ops;
- SH-041 notification;
- SH-044/045/046 idempotency/inbox/outbox;
- SH-047/048 jobs/retry/dead-letter;
- SH-051/052/053 concurrency/lifecycle mechanics;
- SH-055 deadlines;
- SH-059–062 provider callback/reconciliation;
- SH-078 provider minimization;
- SH-087/090 Media;
- SH-091 Search;
- SH-095–098 Privacy;
- SH-107 Order;
- SH-123 target validation.

Trust retains only local policy. Prohibit any Trust replacement auth, role engine, consent store, hold table, checkout, storage client, Search client, queue/idempotency framework, webhook framework, audit/access ledger, privacy workflow, or generic provider-state service.

### Domain Logic

Adversarial cases must include duplicate active attempt vs intentional recheck; consent/fee changes before submission; provider accepted-but-response-lost; duplicate/out-of-order callback; reconciliation against newer state; simultaneous manual/provider decision; expiry concurrent with completion/recheck; credential revoke vs badge rebuild; FCRA dispute vs deadline; Hold failure; Search/Notification outage; privacy execution vs callback; unauthorized support access; unsupported actions/badges/checks accidentally reachable.

### Authorization / Compliance

Every protected route/action/query uses server-side actor/authority; system scopes are narrow; sensitive evidence requires contextual access + SH-030; no `reportToken`, secret, raw PII/report in browser/public DTO/log/Search/Notification; webhook signature required when callbacks enabled; FCRA/retention gates fail closed; no `isVerified`, `backgroundPassed`, or `failedCheckBan` truth.

### Database / Transaction Behavior

Review indexes for requirement resolution, subject/status, provider IDs, expiry, credentials, badges, FCRA deadlines; approved unique provider-event claims; expected-version/locks; state+outbox/event-claim transactions; retention-sensitive cascades; backfill consistency; rollback/recovery. Never rebuild domain truth from Search/provider alone.

### Events / Jobs

Replay Trust domain/provider events where enabled; rerun expiry/recheck/reconcile jobs; prove dead-letter/manual recovery; verify downstream dedupe. Metrics/logs include only safe provider/operation/result/retry/correlation dimensions.

### Provider Integration

Sandbox/live contract verification for enabled adapters; secret/config health; throttling/rate limits; timeout/retry/reconcile; unknown-state alerting; provider deletion; no adapter types in domain/public API.

### UI / Admin Surface

Minimum production tooling for pending/manual review, safe provider/reconcile state, authorized retry/rebuild, permitted credential/FCRA view, and explicit unresolved/gated capability status. No raw report/webhook/token viewer.

### Failure Behavior

Public/internal classification must distinguish validation, authorization, prerequisite missing, conflict/stale, legal/policy gated, review required, provider retryable/permanent, dependency unavailable, dead-letter/manual intervention, and internal operational failure. Raw provider errors do not become public API.

### Tests

Domain lifecycle; SH-017/018 contracts; DB integration; authorization/RLS where root uses it; consent/FCRA compliance; idempotency; race/concurrency; provider signature/dedupe/mapping/reconcile/outage; job retry/dead-letter/replay; Media/sensitive access; Privacy/retention; Search/Notification/Hold contracts; logging/redaction; migration/backfill/rebuild; enabled E2E professional verification; full root-required typecheck/lint/format/test suite.

### Documentation Updates

Update Module architecture for actual settled decisions; this plan only for legitimate sequencing changes; Cluster docs for Cluster-level changes; Shared Ops only if canonical contract changes; provider runbook/config; progress tracker; production blocker register.

### Acceptance Criteria

Enabled flows are race/idempotency/replay safe; outages recover visibly; contracts are stable/versioned; sensitive data stays out of public/telemetry surfaces; legal-gated paths are approved+tested or disabled; migrations have validation/recovery; no prohibited duplicate infrastructure; quality gates pass.

### Exit Gate

Feature 13 passes only when the enabled Trust production scope passes the hardening suite and the readiness report explicitly lists still-disabled legal/architecture paths. A constrained production scope may be ready while U-04/U-05/U-06/U-18 or employment-screening questions remain unresolved, but those capabilities may not be represented as complete.

---

# Module Integration Phase

Feature 11 is the formal integration phase. It must prove these boundaries through public contracts rather than neighboring database tables:

| Boundary | Contract to prove | Trust owns | Neighbor keeps |
| --- | --- | --- | --- |
| Professional Eligibility | SH-017/018 consumed by SH-016 composition | requirement/readiness truth | professional action composition/profile lifecycle |
| Taxonomy | SH-022 / validated target context | Trust requirement/satisfaction | vocabulary/trigger semantics |
| Transaction / Order | SH-107 + authoritative fee result | package/check state | Order/payment truth |
| Marketplace Supply | SH-017/018 for Offering | verification decision | Offering lifecycle/publication |
| Hiring / Candidate | SH-017/018 only for approved contexts | verification decision | Job/Application/Candidate lifecycle and request/permissible-purpose context |
| Media / File Access | SH-090/087 | credential/evidence business meaning | upload/scan/storage/signed URL |
| Compliance Hold | SH-011/012/013 | source verification evidence/reason | Hold lifecycle |
| Search | SH-091 + safe source projection | TrustBadge/source claim | SearchUpsertEvent/index/ranking/query |
| Notification | SH-041 | business trigger/safe context | delivery mechanics |
| Audit / Event Ledger | SH-029/030 | Trust action/evidence meaning | generic audit/access ledgers |
| Privacy | SH-095/096/097 | execution against Trust records | PrivacyRequest/jobs/retention orchestration |
| Observability | SH-037/038 | safe operational context | integration/system/incident records |

Integration is successful only when consumers can use Trust without encoding private provider statuses or private Trust schema assumptions.

# Module Hardening Phase

Feature 13 is formal hardening, but hardening is cumulative. Before corresponding behavior is considered complete, test:

- state races: manual/provider result, expiry/provider result, badge rebuild/revoke, FCRA dispute/deadline;
- command/provider/event/job idempotency and replay;
- provider timeout, accepted-but-response-lost, degradation, unknown state;
- reconciliation of stale pending/missed webhook/local-provider mismatch;
- server validation/authz/system scopes/webhook security/rate limits where root policy requires;
- SSN/report prohibition, protected license identifiers, `reportToken` gate, Media privacy, AccessAuditLog, telemetry redaction;
- Privacy export/erase/anonymize/retain/provider deletion and U-18/U-06 gates;
- audit completeness without audit becoming lifecycle truth;
- safe logs/metrics with no signed URLs/secrets/consent bodies/sensitive notes;
- dry-run/idempotent source-truth-based migration/backfill/rebuild with validation/rollback;
- performance for SH-017/018, expiry scans, provider lookup, admin pagination.

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| Phase 1 | Contracts and Source-of-Truth Foundation | 01–03 |
| Phase 2 | Public Requirement and Readiness Decisions | 04–05 |
| Phase 3 | Provider, Credential, Expiry, and Trust Projection | 06–09 |
| Phase 4 | FCRA / Adverse-Action Legal Boundary | 10 |
| Phase 5 | Module Integration | 11 |
| Phase 6 | Privacy, Audit, Sensitive Access, and Operational Governance | 12 |
| Phase 7 | Module Hardening and Production Verification | 13 |

**Total numbered features: 13.**

### Cluster sequence alignment

```text
CL-03 Feature 04 ← Module Features 01–05
CL-03 Feature 05 ← Module Features 06–10
CL-03 Feature 11 ← Module Feature 11
CL-03 Feature 12 ← Module Feature 12
CL-03 Feature 13 ← Module Feature 13
```

This mapping does not reorder CL-03. If the Cluster build plan changes a prerequisite or milestone, this Module plan must follow it.

# Module Execution Pattern

Before each numbered feature:

1. Read root project overview.
2. Read root architecture and code standards.
3. Read Canonical Shared Operations.
4. Read CL-03 architecture and build plan.
5. Read this Module architecture and plan.
6. Read public-interface sections for all direct dependencies.
7. Read current progress tracker.
8. Confirm the prior feature exit gate.
9. Identify every Proposed Ruling/Unresolved decision touched.
10. Produce the Required Feature Implementation Specification for this feature only.
11. Implement only this feature plus necessary fixes in canonical dependency owners.
12. Run root-required validation/typecheck/lint/format/tests and feature-specific checks.
13. Verify observable workflow/contracts.
14. Update progress/documentation.
15. Update architecture only when a binding decision legitimately changes.
16. Record unresolved risks/disabled paths.
17. Do not begin the next dependent feature until the exit gate passes.

# Required Feature Implementation Specification

Immediately before coding a numbered feature, report:

- Feature number/name;
- Objective;
- Observable result;
- Cluster build-plan link;
- Dependencies;
- Unresolved decisions touched and their disabled/constrained/approved state;
- In scope;
- Out of scope;
- Owned data affected;
- Public contracts;
- Shared operations consumed with canonical ID, invocation, local policy, and prohibited duplicate;
- Permissions/compliance;
- Primary workflow;
- Provider integration or `none`;
- Jobs/events;
- Idempotency/concurrency;
- Error behavior;
- Tests;
- Acceptance criteria;
- Documentation updates.

Do not generate all future feature specifications in advance; each specification must reflect repository state immediately before coding.

# Required Completion Report

After each numbered feature, report:

- Feature completed and exit-gate result;
- Files added;
- Files changed;
- Database changes;
- Migrations and verification/rollback notes;
- Dependencies added/changed;
- Module public interfaces added/changed;
- Shared operations reused;
- Events/jobs added/changed;
- Provider adapter changes;
- Tests added/changed;
- Commands run;
- Manual/contract verification;
- Documentation updated;
- Explicitly approved architecture decisions settled;
- Assumptions that did not become architecture;
- Known failures;
- Remaining risks;
- Deferred work mapped to later feature or unresolved decision;
- Disabled paths, especially U-04/U-05/U-06/U-18/employment-screening gates;
- Exit-gate evidence.

A feature is not complete merely because files exist. Its behavior, ownership boundary, tests, and exit gate must be verified.

# Final Module Quality Gate

Before this implementation plan is considered executed, verify:

1. `VerificationCheck` remains screening attempt/result truth.
2. `ProfessionalLicenseCredential` remains durable credential truth.
3. `TrustBadge` remains projection and never readiness proof.
4. Consent & Disclosure remains generic consent-proof owner.
5. Order remains screening-fee transaction truth.
6. Payment KYC/tax remains distinct from Trust.
7. Healthcare/BAA remains distinct from Trust.
8. Professional/Marketplace/Gig/Job/Application/Candidate lifecycles remain with their owners.
9. ComplianceHold remains the external reusable stop sign.
10. Media owns upload/validation/storage/signed access.
11. Search owns indexing/ranking/projection execution.
12. Notification owns delivery.
13. Audit, Trust domain events, provider-event truth, and Observability remain separate.
14. Privacy remains orchestration owner.
15. Provider SDK objects/statuses do not become domain/public truth.
16. Live callbacks use signature verification + Trust event dedupe + translation + transition validation, or remain disabled.
17. Failed background checks cannot directly cause unreviewed adverse lifecycle action.
18. Raw SSNs/full reports are absent from ordinary tables/logs/Search/Notification/public DTOs.
19. Every numbered feature has passed its tests/exit gate for enabled scope.
20. U-03/U-04/U-05/U-06/U-18 and other unresolved scope questions are resolved in architecture or visibly disabled/constrained.
21. No prohibited shared-infrastructure duplicate exists in Trust.
22. Every Trust write traces to one owner service, every external fact to one owner interface, and every downstream effect to one canonical operation/event.

