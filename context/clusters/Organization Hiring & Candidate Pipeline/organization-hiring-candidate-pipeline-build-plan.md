# Organization, Hiring, & Candidate Pipeline Build Plan

> **Cluster ID:** CL-06  
> **Cluster name:** Organization, Hiring, & Candidate Pipeline  
> **Authority:** [Cluster architecture](organization-hiring-candidate-piepline-architecture.md)\
> **Purpose:** ordered implementation sequence, not an alternative architecture

## Core Principle

Build CL-06 as vertical, observable hiring capabilities:

```text
observable behavior
→ owning application/domain service
→ authoritative owner records
→ public owner contract
→ permissions/compliance/entitlement gates
→ domain event/outbox
→ downstream owner requests
→ tests
→ exit gate
```

Compliance, worker, privacy, and integration features do not need artificial UI, but each slice must produce a concrete public interface, administrative/operational surface, durable record, worker outcome, or contract result.

## Build Rules

The [Shared Operations registry](../../shared/shared-operations.md) governs permanent IDs, canonical names, owners, classifications and statuses. Registered use points below carry verified IDs/statuses. Proposed ruling entries may support planning and owner-specific interfaces/mechanisms, but cross-platform SH API/schema commitment requires separate explicit approval; any exit gate relying on that shared API must verify approval. Unresolved entries must not be silently implemented or replaced locally. The approved Job Compliance publication envelope does not approve a proposed shared decision envelope.

1. Follow root architecture/code standards, this Cluster architecture, and target Module context.
2. Do not expand CL-06 into Gigs, Orders, Bookings, general CRM, or a generic ATS beyond the evidence.
3. Do not redesign Module ownership for convenience.
4. Reuse Canonical Shared Operations instead of rebuilding them.
5. Every mutation uses runtime validation, actor resolution, server-side authorization and owner invariants.
6. Cross-Module reads/writes use public interfaces/events unless an explicitly approved read model exists.
7. Providers stay behind the canonical owner’s adapter.
8. Async work is idempotent, retry-aware, dead-letter-aware and observable.
9. Domain denial, compliance decision, provider failure and operational failure remain distinct.
10. Every numbered feature ends with tests and a hard exit gate.
11. Unresolved architecture is never silently implemented as permissive behavior.
12. Search remains projection.
13. Resume grants follow Candidate Application authorization.
14. Track owns quota/perk/boost truth.
15. Privacy owns privacy-request orchestration.
16. ComplianceHold is the reusable stop sign.
17. Job Interview never writes JobApplication truth and never becomes Booking.
18. The obsolete U-CL06-17 placement claim is retired; do not use the R008 multi-Organization view-event relation as truth, and do not assume the project-level migration baseline is verified.
19. A failed exit gate stops sequential execution until fixed or architecture/build plan is explicitly revised.

## Dependencies and Preconditions

### Platform/shared prerequisites

- actor/session context;
- Role / Authority decision API and RLS parity support;
- Prisma transaction/migration layer;
- runtime validation;
- canonical idempotency;
- optimistic concurrency/aggregate locking with owner-issued opaque `expectedConcurrencyToken`: the owner returns and atomically compares the token and rejects stale writes; no universal integer version or `updatedAt` is assumed. Persisted backing and parent/child token choices remain unresolved per affected aggregate;
- transactional outbox/inbox;
- reliable queue, retries, dead-letter handling;
- structured logging/request IDs;
- Audit and sensitive-access APIs.

### Cross-cluster prerequisites

- CL-01 Identity, Role / Authority, Track;
- CL-02 Taxonomy and Search;
- CL-03 Trust Verification;
- CL-05 Media, Video, and Booking & Calendar via Confirmed SH-067 `invokeCalendarProvider` (Confirmed);
- CL-07 Messaging and Notification;
- CL-08 Privacy;
- CL-09 Holds, Audit and Ops.

### Explicit architecture blockers

Before the affected production feature begins, architecture must resolve:

- U-CL06-01/02 for verified Organization activation;
- U-CL06-03 for ownership transfer;
- U-CL06-04 for monetized Organization ATS access;
- U-CL06-05/07 policy rulings and a later approved persistence implementation of the binding U-CL06-06 historical-proof invariant for production Job publication;
- U-CL06-10/11/12/13 for candidate search/pipeline/access semantics;
- residual U-CL06-14 participant removal/eligibility and U-CL06-15 reschedule policy; Job Interview participant ownership is confirmed;
- residual U-CL06-16 JobInterview-local external event/sync/error-field semantics for persisted calendar integration; Booking & Calendar provider ownership is confirmed;
- unresolved SH-120 `normalizeJurisdictionContext` (Unresolved) owner/interface before jurisdiction-aware production compliance.

External providers may be contract-stubbed before their integration feature. Do not fake their domain decisions.

# Phase 1 — Hiring Entity, Job Draft, and Publication Gate


### 01 Organization Membership and Job Draft Workspace

An authenticated Organization owner/admin can create a draft Organization, manage current membership rows, and create/list/edit private Job drafts; no Job is yet publicly publishable.

#### Objective

An authenticated Organization owner/admin can create a draft Organization, manage current membership rows, and create/list/edit private Job drafts; no Job is yet publicly publishable.

#### User-visible / Observable Result

An authenticated Organization owner/admin can create a draft Organization, manage current membership rows, and create/list/edit private Job drafts; no Job is yet publicly publishable.

#### Owning Module(s)

- **Organization Hiring** owns Organization, membership-row/role-assignment, and Job truth.
- **Role / Authority** remains the permission interpreter.

#### Dependencies

Requires actor resolution, Role / Authority, Taxonomy validation, shared idempotency/concurrency, and the current Organization/Job Prisma models. Ownership transfer is excluded until U-CL06-03 is resolved.

#### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` (Confirmed) — Identity; establish actor context, not business permission.
- SH-002 `authorizeResourceAction` (Confirmed) — Role / Authority; Organization Hiring supplies membership/resource facts.
- SH-003 `queryOwnerFacts` (Proposed ruling) — Organization Hiring; typed DTOs instead of cross-domain repository reads.
- SH-044 `executeIdempotentCommand` (Confirmed) — protect create commands.
- SH-052 `withOptimisticConcurrency` (Confirmed) — protect Job/profile/member edits.
- SH-029 `appendAuditEvent` (Confirmed) — record sensitive member/role changes when policy requires.
- Taxonomy validation interface — validate controlled classifications; do not hardcode taxonomy.
No feature-local auth, role or lock helper may be created.

#### Data / Schema

Use `Organization`, `OrganizationStatus`, `OrganizationMember`, `OrganizationRole`, `Job`, `JobStatus`, `JobVisibility`, `EmploymentType`, and only architecture-approved classification joins. Preserve slug/member uniqueness and Job→Organization ownership. Do not assign `OrganizationFeatureAccess` ownership here.

#### Public Interfaces

Before Feature 02, Organization Hiring exposes the dedicated compliance-input snapshot and scoped/cursor rescan-enumeration contracts defined in its architecture. The latter returns eligible Job IDs and exact source revision/token; neither permits Job Compliance to access Organization Hiring repositories directly. Missing authoritative compensation/benefit sources remain unresolved.

Implement/complete `createOrganization`, `getOrganization`, `listOrganizationsForActor`, `addOrganizationMember`, `changeOrganizationMemberRole`, `removeOrganizationMember`, `listOrganizationMembers`, `createJobDraft`, `getJob`, `listOrganizationJobs`, `updateJobDraft`, and minimal `getOrganizationHiringContext`.

#### Logic

Organization creation writes the architecture-approved owner/membership facts; Job remains `draft`; Job visibility never overrides lifecycle; stale edits are rejected; member removal cannot violate the current owner invariant. Any still-unresolved owner-transfer behavior is not exposed.

#### UI / Administrative Surface

Minimum Organization profile/member management plus Job list/create/edit/detail. Clearly show non-public draft state.

#### Authorization / Compliance

All mutations are server-authorized. RLS and server decisions must agree. Holds may gate sensitive transitions through the canonical hold API; no local blocked flag. Organization verification/activation is not faked.

#### Events / Jobs / Integrations

Owner-domain creation/update events may be published through the outbox if later consumers need them. No Search indexing occurs.

#### Failure Behavior

Duplicate slug/member errors become deterministic domain conflicts; unauthorized requests have no writes; stale versions conflict; Taxonomy unavailability is explicit rather than accepting arbitrary terms.

#### Tests

Unit invariants; integration CRUD; membership role/owner cases; authorization/RLS parity; concurrent Job/member edit tests; relevant component/E2E draft flow.

#### Out of Scope

Organization verification/activation, ownership transfer, public Job publication, applications, resumes, interviews, Organization ATS monetization, Search.

#### Exit Gate

Organization's compliance snapshot and rescan-enumeration provider contracts/fixtures must be available and paired with Job Compliance consumers before Feature 02 starts.

PASS only if authorized Organization/Job draft workflows work end-to-end, unauthorized/RLS paths deny, no local Role policy exists, no Job can become public/searchable, concurrency produces deterministic conflicts, and typecheck/lint/unit/integration/RLS/UI checks pass.


### 02 Job Compliance Rule, Check, Finding, and Disclosure Evaluation

An authorized Job Compliance evaluation produces durable rule-version, check, finding, compensation-disclosure and decision evidence, clearly separating compliance outcome from technical scanner failure.

#### Objective

An authorized Job Compliance evaluation produces durable rule-version, check, finding, compensation-disclosure and decision evidence, clearly separating compliance outcome from technical scanner failure.

#### User-visible / Observable Result

An authorized Job Compliance evaluation produces durable rule-version, check, finding, compensation-disclosure and decision evidence, clearly separating compliance outcome from technical scanner failure.

#### Owning Module(s)

- **Job Compliance** owns rules/checks/findings/disclosure policy.
- **Organization Hiring** remains owner of the evaluated Job.

#### Dependencies

Feature 01 must expose Organization Hiring's compliance-input snapshot and scoped/cursor rescan-enumeration owner contracts before this feature consumes them. U-CL06-05/07 remain policy blockers; U-CL06-06 is a binding evidence invariant whose persistence design/implementation requires a later approved schema pass. SH-120 `normalizeJurisdictionContext` (Unresolved) remains Unresolved: production jurisdiction-aware evaluation requires its approved owner/interface. Rule/check persistence, owner-local scanner mechanics and deterministic fixtures with explicitly supplied normalized jurisdiction context may proceed below that gate; raw location strings are not canonical evidence and no local replacement is permitted. Shared proposed scanner/decision/owner-facts APIs require separate approval before cross-platform commitment.

#### Shared Operations Used

SH-077 `buildCanonicalTextSnapshot` (Confirmed), SH-072 `hashCanonicalPayload` (Confirmed), SH-080 `manageVersionedRules` (Confirmed), SH-081 `runPatternScanner` (Proposed ruling), SH-044 `executeIdempotentCommand` (Confirmed), SH-047 `enqueueReliableJob` (Confirmed), SH-048 `executeRetryWithBackoff` (Confirmed), SH-015 `returnDecisionResult` (Proposed ruling), SH-029 `appendAuditEvent` (Confirmed), SH-012 `requestComplianceHold` (Confirmed) as needed. Scanner/version mechanics are shared; employment policy remains Job Compliance-owned.

#### Data / Schema

Use `JobComplianceRule`, `JobComplianceCheck`, `JobComplianceFinding`, `JobCompensationDisclosure`, owned enums/statuses, and historical proof satisfying the binding U-CL06-06 invariant. Preserve immutable exact input (snapshot or reconstructible immutable source-version reference) plus hash, every applied rule identity/version including zero-finding approvals, scanner version, evaluation time and material normalized jurisdiction input. Current schema is insufficient; schema design/migrations belong to a later approved database pass. Job compensation itself remains Organization-owned; missing authoritative source-field mappings remain unresolved.

#### Public Interfaces

`requestJobComplianceEvaluation`, SH-021 `evaluateJobCompliance` (Confirmed), `getJobPublicationComplianceDecision`, `getJobComplianceReport`, `getApplicableJobComplianceRequirements`, rule publish/retire, review and override commands.

#### Logic

Resolve applicable rules by jurisdiction/effective date; build all relevant Job text/structured surfaces; validate disclosure; scan; classify findings; persist provenance; return the Job Compliance-owned `allowed | denied | warning | review_required | unavailable` response; retain exact source/rule proof. Final precedence remains unresolved; `unavailable` and `review_required` are not denial, and remediation stays in reason/next-action metadata. Unknown/uncertain states go to review/unavailable, never silent pass.

#### UI / Administrative Surface

Job compliance report on Job detail plus restricted admin rule/review/override surface.

#### Authorization / Compliance

Reviewer/rule-admin actions pass Role / Authority and audit. Job Compliance does not own candidate screening/adverse action or general moderation.

#### Events / Jobs / Integrations

Evaluation worker; decision-changed outbox; rule-change rescan/backfill when activated. Retry technical failures only.

#### Failure Behavior

Scanner/provider/library failure is `failed`/operational and cannot approve/reject legally. Stale Job version forces reevaluation. Duplicate evaluation command returns idempotent receipt/result.

#### Tests

Rule resolution, compensation/disclosure, finding classification, decision precedence, historical reproducibility, scanner unknown/failure, reviewer authorization/audit, idempotency/retry, Job snapshot contract.

#### Out of Scope

Job lifecycle mutation, Search writes, candidate screening, generic moderation.

#### Exit Gate

PASS only if U-CL06-05/07 are resolved, the binding U-CL06-06 invariant has an approved implemented persistence design, SH-120 `normalizeJurisdictionContext` (Unresolved) has an approved owner/interface, and any proposed SH API/schema commitment has separate approval; both Organization source contracts pass consumer tests; identical immutable input and complete applied-rule proof reproduce the result after later Job/rule changes; zero-finding pass records every applied rule; technical failure cannot approve; Job Compliance never owns Job lifecycle; reviewer/admin actions are authorized/audited; all tests/build checks pass.


### 03 Controlled Job Publication and Search Handoff

An authorized Organization can request Job publication; Organization Hiring applies the authoritative Job Compliance decision and requests Search only after the Job is truly public-ready.

#### Objective

An authorized Organization can request Job publication; Organization Hiring applies the authoritative Job Compliance decision and requests Search only after the Job is truly public-ready.

#### User-visible / Observable Result

An authorized Organization can request Job publication; Organization Hiring applies the authoritative Job Compliance decision and requests Search only after the Job is truly public-ready.

#### Owning Module(s)

Organization Hiring owns Job lifecycle; Job Compliance owns compliance decision; Search owns projection execution; Trust/Holds own their gates.

#### Dependencies

Features 01–02, resolved compliance mapping, Search contract/fixture, Trust requirement/readiness interface, ComplianceHold.

#### Shared Operations Used

SH-002 `authorizeResourceAction` (Confirmed), SH-011 `evaluateComplianceHold` (Confirmed), SH-021 `evaluateJobCompliance` (Confirmed), Trust requirement/readiness operations, SH-094 `buildSourceProjection` (Confirmed), SH-091 `requestSearchProjectionRefresh` (Confirmed), SH-046 `publishDomainEvent` (Confirmed), SH-041 `requestNotification` (Confirmed), idempotency and concurrency.

#### Data / Schema

`Job.status`, `Job.visibility`, and `Job.complianceStatus` only under approved mirror semantics. Persist source/decision version references as required.

#### Public Interfaces

Complete `requestJobPublication`, owner command equivalent to `applyJobComplianceDecision`, `pauseJob`, `markJobFilled`, `closeJob`, `archiveJob`, public Job projection query and Search refresh/removal contract. Consume Job Compliance's `allowed | denied | warning | review_required | unavailable` envelope; no competing Organization union.

#### Logic

Implement the four manual Job owner commands using existing Organization lifecycle policy, actor/authority checks, concurrency and idempotency. Commit the Job transition before requesting Search refresh/removal. Apply later Compliance changes to Organization-owned application eligibility; Candidate consumes that fail-closed owner state/context and does not perform a second Compliance evaluation/read.

Set pending-review before evaluation; reject stale decision if Job changed; apply explicit compliance→Job mapping; compose hold/verification/public visibility without moving their policy; request Search after source commit; material edits invalidate/re-review according to rule.

#### UI / Administrative Surface

Publish/review state, warnings/needs-changes report, resubmit action and non-public indicator.

#### Authorization / Compliance

Authorized org member only. Compliance approval does not bypass Holds or Trust requirements.

#### Events / Jobs / Integrations

Job/compliance/status outbox events, Search refresh/removal, Notification. Add Job close-time worker only once close policy is specified.

#### Failure Behavior

Search outage never rolls back or rewrites truthful Job state; it queues retry. Compliance unavailable leaves Job non-public. Stale decision re-evaluates. Hold/readiness revocation requests de-index according to source policy.

#### Tests

For pause/fill/close/archive, test authorized and unauthorized actors, allowed/invalid transitions under existing policy, stale/replayed requests, committed owner state before Search effects, and Search outage/retry. Test the exact producer decision vocabulary, especially unavailable versus denial and review-required versus denial.

End-to-end draft→review→open; warning/block/review/failure; publish/edit race; Search no-preapproval contract; hold/Trust composition; E2E with Search fixture.

#### Out of Scope

Organization verification activation until U-CL06-01/02; applications and ATS.

#### Exit Gate

PASS only if all four manual lifecycle commands and their post-commit Search effects meet those tests, the publication response matches the producer-owned envelope, normal Candidate eligibility uses the Job owner context, and no Job is indexed before owner state+allowed compliance, Search never recomputes compliance, Job Compliance never writes Job status directly, edit invalidation and Search retry paths are tested, and all checks pass.

# Phase 2 — Candidate Intake, Private Resume, and Recruiter Pipeline


### 04 CandidateProfile and Secure Resume Intake

A User can create CandidateProfile identity, upload a private resume through Media, and observe Media validation/scanning and permitted candidate/profile attachment.

#### Objective

A User can create CandidateProfile identity, upload a private resume through Media, and observe Media validation/scanning and permitted candidate/profile attachment.

#### User-visible / Observable Result

A User can create CandidateProfile identity, upload a private resume through Media, and observe Media validation/scanning and permitted candidate/profile attachment.

#### Owning Module(s)

Candidate Application owns CandidateProfile and contextual attachment meaning; Media owns file safety/storage. No ResumeParseResult is created in this feature.

#### Dependencies

Media public interfaces and actor/authority; enforce the binding non-authority of resumeUrl and local verification caches. Remaining Candidate policy questions stay gated.

#### Shared Operations Used

Actor/authority; SH-114 `provisionOneToOneProfile` (Confirmed), SH-082 `validateUploadedFile` (Confirmed), SH-083 `scanFileForMalware` (Confirmed), SH-090 `attachValidatedMedia` (Confirmed), and Media retry/ops interfaces. Do not create local storage/MIME/malware helpers.

#### Data / Schema

`CandidateProfile`, `CandidateProfileMedia` plus Media-owned records through APIs. Do not treat `resumeUrl`, `trustScore`, `verifiedAt`, or `verificationExpiresAt` as authority.

#### Public Interfaces

`createCandidateProfile`, `updateCandidateProfile`, candidate status transition, media attach/detach and Media upload/readiness queries.

#### Logic

Require Media validation/scanning and ready+clean state for permitted attachment. Parsing cannot begin until a JobApplication and its matching JobApplicationMedia exist in Feature 05.

#### UI / Administrative Surface

Candidate profile editor, resume upload/status/retry. No permanent public resume URL.

#### Authorization / Compliance

Candidate ownership server-side; resume private by default; Trust truth remains external.

#### Events / Jobs / Integrations

Candidate profile/attachment events and Media-owned upload processing only. No parsing or Search indexing.

#### Failure Behavior

Invalid/malware files are rejected by Media; upload/attachment retries are idempotent and sensitive payloads are redacted from telemetry.

#### Tests

Ownership, one-to-one provisioning/idempotency, private file behavior, ready+clean gate, no pre-application parse record/job, no public URL and privacy/log redaction.

#### Out of Scope

JobApplication, JobApplicationMedia, ResumeParseResult creation/worker execution, recruiter resume access, candidate Search and automated hiring scoring.

#### Exit Gate

PASS only if private upload and permitted profile attachment work through Media, no ResumeParseResult or parse job is produced, resume/local verification fields are not authority, sensitive content is absent from logs, and tests/build pass.


### 05 Atomic Application Eligibility, Quota, and Submission

A CandidateProfile can submit at most one application to an eligible Job without exceeding Track limits under concurrent requests.

#### Objective

A CandidateProfile can submit at most one application to an eligible Job without exceeding Track limits under concurrent requests.

#### User-visible / Observable Result

A CandidateProfile can submit at most one application to an eligible Job without exceeding Track limits under concurrent requests.

#### Owning Module(s)

Candidate Application owns JobApplication; Track owns quota/usage; Organization Hiring owns Job facts; Trust owns verification readiness.

#### Dependencies

Parsing is a strictly post-submission stage: first create/commit JobApplication and its ready/clean JobApplicationMedia; only then implement parse request and worker execution. Submission does not depend on a completed parse. Final raw-text retention/encryption still requires U-CL06-13, and retry evidence/media-role questions remain unresolved.

Features 03–04, Track resolve/consume, Trust readiness, U-CL06-11 sufficient for submission/withdraw semantics, and a defined race-safe cross-owner application+usage protocol.

#### Shared Operations Used

Post-submission parsing uses SH-047 `enqueueReliableJob` (Confirmed), SH-048 `executeRetryWithBackoff` (Confirmed) and Media readiness interfaces; no parser/storage mechanism is introduced locally beyond the owner parser port.

Actor/authority, SH-011 `evaluateComplianceHold` (Confirmed), SH-005 `resolveEntitlement` (Confirmed), SH-006 `consumeMeteredEntitlement` (Confirmed), Trust readiness, idempotency, aggregate/counter locking, domain event, Notification and optional Messaging context.

#### Data / Schema

`JobApplication` with unique `(jobId,candidateProfileId)`, initial `submitted/new_`; TrackUsageEvent/Counter external; ready attachment links.

#### Public Interfaces

`evaluateApplicationEligibility`, `checkCandidateApplicationAllowance`, `submitJobApplication`, `withdrawJobApplication`, `listCandidateApplications`, `attachApplicationMedia`, `queueResumeParse`, `getResumeParseResult`.

#### Logic

Consume Organization Hiring's fail-closed `getJobApplicationEligibilityContext`. No normal direct Candidate → Job Compliance read/evaluation is permitted. After the application/media pair exists, request parsing idempotently and expose non-decisional metadata/status; a parsing failure does not roll back the submitted application or create duplicate quota usage.

Compose CandidateProfile usability, Job application facts, holds, Track quota, verified-only readiness and duplicate constraint. Application and usage outcomes reconcile under retry/concurrency.

#### UI / Administrative Surface

Apply form with allow/deny/remediation/quota feedback, receipt, application list and permitted withdrawal.

#### Authorization / Compliance

Candidate owns profile; verified-only gates consume Trust; no local quota/premium flag.

#### Events / Jobs / Integrations

Application submitted/withdrawn events; Notification; optional context thread; post-submission parse requested/completed/failed events and parse worker.

#### Failure Behavior

Duplicate idempotency returns existing result; unique constraint gives domain conflict; quota exhaustion creates no application; Trust unavailable cannot bypass; partial cross-owner outcome is reconciled.

#### Tests

Prove upload alone cannot create parse work; application/media existence and Media ready+clean gate precede every parse; parser failure/replay is recoverable without application rollback, duplicate parse truth or hiring recommendations. Verify no direct Compliance dependency in submission.

Eligibility unit tests, Track/Trust contracts, simultaneous submissions, idempotency replay, hold/verified-only denial, E2E apply.

#### Out of Scope

Recruiter pipeline, resume view, candidate Search.

#### Exit Gate

PASS only if quota cannot be exceeded under concurrency, duplicate JobApplication is impossible, Track usage and application truth reconcile, verified-only/hold gates cannot be bypassed, post-submission parsing meets its existence/readiness/idempotency/privacy gates, and tests pass.


### 06 Recruiter Applicant Views, View Events, and Pipeline State

Authorized OrganizationMembers can view privacy-shaped applicants and move application status/stage under Candidate Application policy, with application-view proof.

#### Objective

Authorized OrganizationMembers can view privacy-shaped applicants and move application status/stage under Candidate Application policy, with application-view proof.

#### User-visible / Observable Result

Authorized OrganizationMembers can view privacy-shaped applicants and move application status/stage under Candidate Application policy, with application-view proof.

#### Owning Module(s)

Candidate Application owns JobApplication status/stage and JobApplicationViewEvent truth. U-CL06-12 approval gates qualifying-view and view-summary behavior, not ownership.

#### Dependencies

Feature 05, U-CL06-11 transition matrix, U-CL06-12 view semantics, Role / Authority.

#### Shared Operations Used

Use SH-076 `normalizeAndHashIdentifier` (Confirmed) for approved IP/identifier evidence; Candidate retains capture and access-event policy.

Actor/authority, owner-facts query, lifecycle transition mechanism, concurrency, Audit where required, domain events, Notification.

#### Data / Schema

`JobApplication`, Candidate-owned `JobApplicationViewEvent` with at most one Organization context, and viewed/status/stage timestamps only under separately approved summary semantics.

#### Public Interfaces

`listJobApplicants`, `getJobApplicationDetail`, `recordJobApplicationView`, `transitionApplicationStage`, `transitionApplicationStatus`, candidate status query.

#### Logic

Verify Job belongs to actor Organization; shape minimum candidate/application data; append view event; update summary only as ruled; enforce every legal/illegal transition and timestamp invariant.

#### UI / Administrative Surface

Organization applicant list/detail and pipeline controls; candidate-facing status.

#### Authorization / Compliance

Cross-org isolation is mandatory; applicant detail does not authorize resume access.

#### Events / Jobs / Integrations

View/status/stage events and safe Notification requests.

#### Failure Behavior

Cross-org request denies; illegal transition returns deterministic domain error; stale transition conflicts; view-event duplicate behavior follows explicit request semantics.

#### Tests

Transition matrix, cross-org isolation, view append/summary, status-stage timestamp consistency, dashboard contract proving no direct repository access.

#### Out of Scope

Resume access, interviews, candidate Search.

#### Exit Gate

PASS only if Organization Hiring/Job Interview contain no direct JobApplication writes, U-CL06-11/12 semantics are implemented and tested, cross-org access fails, and all checks pass.


### 07 Contextual Resume Access and Sensitive Access Proof

An authorized OrganizationMember can receive short-lived private resume access only after Candidate Application validates the exact application, media, Organization and reason, with domain and generic access proof.

#### Objective

An authorized OrganizationMember can receive short-lived private resume access only after Candidate Application validates the exact application, media, Organization and reason, with domain and generic access proof.

#### User-visible / Observable Result

An authorized OrganizationMember can receive short-lived private resume access only after Candidate Application validates the exact application, media, Organization and reason, with domain and generic access proof.

#### Owning Module(s)

Candidate Application owns authorization and ResumeAccessLog; Media owns grant/URL/MediaAccessEvent; Audit owns AccessAuditLog.

#### Dependencies

Feature 06, U-CL06-13 access-event semantics; U-CL06-04 only if monetized resume-viewer gating is enabled.

#### Shared Operations Used

Use SH-125 `recordDomainAccessEvent` (Confirmed) for ResumeAccessLog append mechanics and SH-076 `normalizeAndHashIdentifier` (Confirmed) for approved access metadata; Candidate retains event meaning and authorization.

Actor/authority, contextual-resource authorization pattern, Media temporary grant/signed URL, SH-030 `recordSensitiveAccess` (Confirmed), idempotency, telemetry redaction.

#### Data / Schema

`ResumeAccessLog`; MediaAccessGrant/Event externally; AccessAuditLog externally. No durable public resume URL.

#### Public Interfaces

`authorizeContextualResumeAccess`, composed `requestResumeAccessGrant`, `recordResumeAccess`.

#### Logic

Require authorized org member + application belongs to org Job + media belongs to application + ready/clean asset + allowed reason + optional org feature gate only when canonical owner exists; then Media access and proof.

#### UI / Administrative Surface

Resume-view action with expired-link recovery and safe denial.

#### Authorization / Compliance

No admin/support broad bypass; short-lived TTL; every successful grant/read follows the ruled proof semantics.

#### Events / Jobs / Integrations

No new provider. Media performs storage/signing.

#### Failure Behavior

Authorization denial issues no grant. Media failure cannot write a false success log. Grant-without-read semantics follow U-CL06-13. Audit failure is surfaced according to root policy.

#### Tests

Cross-org/wrong-media denial, expired grant, successful ResumeAccessLog+Media+Audit correlation, no permanent URL, sensitive log redaction.

#### Out of Scope

Candidate Search, interviews, generic document viewer.

#### Exit Gate

PASS only if no signed URL precedes Candidate authorization, successful access has required domain/generic proof, cross-org/expired access fails, sensitive payloads are absent from logs, and tests pass.


### 08 Candidate Search Projection and Candidate Perks

Candidate Application can build a privacy-safe CandidateSearchProjection for Search while Track remains the owner of candidate boost and application-view insight perks.

#### Objective

Candidate Application can build a privacy-safe CandidateSearchProjection for Search while Track remains the owner of candidate boost and application-view insight perks.

#### User-visible / Observable Result

Candidate Application can build a privacy-safe CandidateSearchProjection for Search while Track remains the owner of candidate boost and application-view insight perks.

#### Owning Module(s)

Candidate Application owns projection content/lifecycle and application view truth; Search owns indexing; Track owns perks.

#### Dependencies

Features 04 and 06, U-CL06-10 visibility/search participation ruling, Search contract and Track entitlement.

#### Shared Operations Used

SH-005 `resolveEntitlement` (Confirmed), SH-094 `buildSourceProjection` (Confirmed), SH-091 `requestSearchProjectionRefresh` (Confirmed), domain event, Privacy target protocol.

#### Data / Schema

`CandidateSearchProjection`; Track grants external; SearchUpsertEvent external. `rawResumeTextIndexed=false` by default.

#### Public Interfaces

Projection build/query/status transition; Search upsert/removal request; Track-gated view-insight query.

#### Logic

Derive allowlisted metadata only; resolve discoverability/privacy; pass boost as Search policy input rather than local truth; entitlement/status/privacy changes request reindex/removal.

#### UI / Administrative Surface

Candidate discoverability state and view-insight surface only if product/privacy ruling permits.

#### Authorization / Compliance

No raw resume; restriction/erasure hides projection; no local boost flag.

#### Events / Jobs / Integrations

Projection worker, Search refresh/removal, Track entitlement-change handler, privacy/status removal handler.

#### Failure Behavior

Search outage does not alter source projection; unknown visibility defaults non-indexed; absent entitlement removes boost/view insight.

#### Tests

Projection allowlist, no raw resume, hide/erase/de-index, entitlement boost reindex, view insight gate, Search not truth.

#### Out of Scope

Search ranking internals and local premium/boost model.

#### Exit Gate

PASS only if U-CL06-10 is resolved, source projection can rebuild Search, raw resume is excluded, entitlement revocation removes perk correctly, privacy de-index passes, and tests/build pass.

# Phase 3 — Hiring Interviews and Collaboration Handoffs


### 09 Core JobInterview Proposal and Scheduling

Authorized hiring actors can create and transition a provider-independent JobInterview against an interviewable JobApplication, with consistent application/organization/candidate context and append-only interview event history.

#### Objective

Authorized hiring actors can create and transition a provider-independent JobInterview against an interviewable JobApplication, with consistent application/organization/candidate context and append-only interview event history.

#### User-visible / Observable Result

Authorized hiring actors can create and transition a provider-independent JobInterview against an interviewable JobApplication, with consistent application/organization/candidate context and append-only interview event history.

#### Owning Module(s)

**Job Interview** owns JobInterview lifecycle and JobInterviewEvent. Candidate Application supplies application facts but keeps application lifecycle ownership.

#### Dependencies

Feature 06; Role / Authority; Candidate Application interviewability facts; the portion of U-CL06-15 needed to define implemented transitions.

#### Shared Operations Used

Actor resolution/authorization; SH-003 `queryOwnerFacts` (Proposed ruling); SH-053 `transitionLifecycleState` (Confirmed); SH-031 `appendDomainLifecycleEvent` (Confirmed); idempotency; optimistic concurrency; Notification may be a contract fixture.

#### Data / Schema

`JobInterview`, `JobInterviewStatus`, `JobInterviewLocationType`, `JobInterviewEvent`. Enforce startsAt < endsAt and consistent application/org/candidate IDs.

#### Public Interfaces

`proposeInterview`, `scheduleInterview`, `cancelInterview`, `completeInterview`, `markInterviewNoShow`, `getInterview`, list-by-application/org/candidate, timeline query.

#### Logic

Validate one hiring case; store absolute timestamps plus display timezone context; enforce the approved transition subset; append JobInterviewEvent for every mutation; do not write JobApplication stage/status.

#### UI / Administrative Surface

Recruiter proposal/scheduling controls; candidate/org interview list/detail; event timeline.

#### Authorization / Compliance

Organization actions use Role / Authority; candidate sees only linked interviews; sensitive support/admin reads follow audit policy.

#### Events / Jobs / Integrations

Interview owner events; optional proposal-expiry worker if expiry policy is approved. Provider integrations remain absent.

#### Failure Behavior

Context mismatch rejects. Concurrent stale transition returns conflict. Notification failure is retriable and cannot invalidate truthful interview state.

#### Tests

Context consistency; transition subset; time/timezone invariant; cross-org/candidate authorization; event append; no JobApplication write; concurrency.

#### Out of Scope

Participant management beyond minimum, reschedule chain, video/calendar provider work, Booking.

#### Exit Gate

PASS only if interview source truth works without providers, every mutation creates domain history, no Booking/application mutation appears, authorization/concurrency tests pass, and all build checks pass.


### 10 Interview Participants, Rescheduling, and Application Synchronization

Interview-local participants can be invited/respond/removed under an approved policy, reschedules preserve deterministic history, and any application-stage effect crosses the Candidate Application public interface.

#### Objective

Interview-local participants can be invited/respond/removed under an approved policy, reschedules preserve deterministic history, and any application-stage effect crosses the Candidate Application public interface.

#### User-visible / Observable Result

Interview-local participants can be invited/respond/removed under an approved policy, reschedules preserve deterministic history, and any application-stage effect crosses the Candidate Application public interface.

#### Owning Module(s)

Job Interview owns interview and, after U-CL06-14 approval, participant truth. Candidate Application remains owner of application stage/status.

#### Dependencies

Feature 09; Job Interview participant row/role/status ownership is confirmed, while U-CL06-14 removal/role eligibility/candidate invariant remains unresolved; U-CL06-15 reschedule semantics/cardinality; Candidate Application stage interface.

#### Shared Operations Used

Actor/authority; lifecycle/event mechanics; idempotency/concurrency; domain outbox; Notification. Shared mechanics do not merge participant/application truth.

#### Data / Schema

`JobInterviewParticipant`, participant role/status enums, `rescheduledFromInterviewId`, JobInterviewEvent. Do not add a competing application/interview join state machine.

#### Public Interfaces

Add/remove participant, respond to invitation, `rescheduleInterview`, `handleApplicationStateChanged`, and a public request/event to Candidate Application for stage transition where policy requires.

#### Logic

Validate participant assignment from candidate/org facts; enforce participant uniqueness; implement the approved candidate-participant invariant; implement one deterministic active reschedule chain; react to withdrawn/rejected/closed application under explicit policy.

#### UI / Administrative Surface

Participant list/invite/response; reschedule flow/history; synchronized application/interview status presentation without merging lifecycles.

#### Authorization / Compliance

Organization member eligibility and candidate identity are server-checked. Removed/revoked participants lose downstream access through owner handlers.

#### Events / Jobs / Integrations

Participant/respond/reschedule owner events; application-change event consumer; Notification requests.

#### Failure Behavior

Duplicate invitations are idempotent; concurrent reschedules conflict safely; a denied Candidate Application stage change is surfaced without rewriting interview history; downstream access revocation retries separately.

#### Tests

Participant uniqueness/role rules, removal semantics, reschedule chain/cardinality, application synchronization contract, concurrent reschedule, revoked participant access.

#### Out of Scope

Calendar provider, video provider internals, Messaging internals.

#### Exit Gate

PASS only if remaining U-CL06-14 participant policy and U-CL06-15 reschedule policy are resolved and followed, confirmed Job Interview participant ownership is preserved, participant removal is unambiguous, reschedule history is deterministic, Job Interview never writes JobApplication directly, and all tests pass.


### 11 Interview Messaging, Notification, Resume Review, and Video Handoffs

A scheduled interview can request a context thread, notifications, interview-related resume access, and a Video Session-owned room without duplicating any downstream lifecycle.

#### Objective

A scheduled interview can request a context thread, notifications, interview-related resume access, and a Video Session-owned room without duplicating any downstream lifecycle.

#### User-visible / Observable Result

A scheduled interview can request a context thread, notifications, interview-related resume access, and a Video Session-owned room without duplicating any downstream lifecycle.

#### Owning Module(s)

Job Interview owns orchestration meaning; Messaging owns Thread/Message; Notification owns delivery; Candidate Application owns resume authorization/proof; Video Session owns JobInterviewVideoRoom/provider room.

#### Dependencies

Features 07 and 10 plus owner public contracts for Messaging, Notification, Candidate resume access, and Video Session.

#### Shared Operations Used

SH-113 `ensureContextThread` (Confirmed); SH-041 `requestNotification` (Confirmed); Candidate resume-access interface; SH-030 `recordSensitiveAccess` (Confirmed); reliable jobs/retries; provider call only through Video owner (SH-068 `invokeVideoProvider` (Confirmed) pattern); integration-failure observability.

#### Data / Schema

No new Thread/Notification/Video source records in Job Interview. JobInterview may retain only approved references/status evidence; Video-owned `JobInterviewVideoRoom` stays external.

#### Public Interfaces

`ensureInterviewThread`; `authorizeInterviewResumeReview` delegation; `requestInterviewVideoRoom`; video-room status handler; notification request operations.

#### Logic

For video location, request room from Video after interview commit; resume review uses Candidate's exact `interview_review` authorization path; safe participant facts create/retrieve Messaging context; owner failures do not corrupt interview state.

#### UI / Administrative Surface

Thread link, resume review action, video join action only when Video grants it, plus visible integration error/retry where appropriate.

#### Authorization / Compliance

Participant/org authorization; resume/video sensitive access audited; notification payloads minimize candidate/resume content.

#### Events / Jobs / Integrations

Messaging, Notification, Video Session contracts; retry/reconciliation job for failed downstream requests. Provider adapter remains Video-owned.

#### Failure Behavior

Video failure leaves interview scheduled but room unavailable/retriable; thread/notification failures retry; resume denial produces no Media grant.

#### Tests

Contract tests for all owners; no duplicate downstream rows; video degradation; resume access proof; sensitive payload redaction; E2E scheduled video interview with fixtures.

#### Out of Scope

Calendar sync; custom chat/video; provider token persistence in JobInterview.

#### Exit Gate

PASS only if CL-06 owns none of the downstream source lifecycles, resume review goes through Candidate authorization, provider/rail failures are observable/retriable, sensitive access is audited, and tests pass.


### 12 Interview Calendar Sync and Reconciliation

JobInterview schedule changes can create/update/cancel an external calendar event through Confirmed Booking & Calendar SH-067 `invokeCalendarProvider` (Confirmed), with normalized results and reconciliation; exact local sync-field meaning remains gated.

#### Objective

JobInterview schedule changes can create/update/cancel an external calendar event through Confirmed Booking & Calendar SH-067 `invokeCalendarProvider` (Confirmed), with normalized results and reconciliation; exact local sync-field meaning remains gated.

#### User-visible / Observable Result

JobInterview schedule changes can create/update/cancel an external calendar event through Confirmed Booking & Calendar SH-067 `invokeCalendarProvider` (Confirmed), with normalized results and reconciliation; exact local sync-field meaning remains gated.

#### Owning Module(s)

Job Interview owns interview schedule. Booking & Calendar owns provider connections, invocation/synchronization, webhook verification/dedupe, adapter calls and provider normalization through Confirmed SH-067 `invokeCalendarProvider` (Confirmed).

#### Dependencies

Feature 10; residual U-CL06-16 local event/sync/error-field semantics approved where used; Confirmed Booking & Calendar port; provider webhook/dedupe/reconciliation infrastructure.

#### Shared Operations Used

SH-067 `invokeCalendarProvider` (Confirmed); SH-059 `verifyProviderWebhookSignature` (Confirmed); SH-060 `deduplicateProviderEvent` (Confirmed); SH-061 `translateProviderStatus` (Confirmed); SH-062 `reconcileProviderState` (Confirmed); reliable jobs/retries; integration failure telemetry. Do not create `ProcessedInterviewCalendarEvent`.

#### Data / Schema

Use JobInterview external calendar reference/sync fields only if U-CL06-16 confirms them as interview-local attachment state. Provider-event ledger stays with calendar owner.

#### Public Interfaces

Request create/update/cancel calendar sync; normalized result handler; reconciliation query/job.

#### Logic

Commit interview schedule first; send idempotent calendar action; owner verifies/dedupes callback; apply normalized result only; reschedule/cancel use same external reference rules; reconciliation detects drift.

#### UI / Administrative Surface

Calendar sync status/error/retry indicator. Raw provider payloads are not normal UI state.

#### Authorization / Compliance

Calendar consent/connection ownership remains external. Send only minimized participant/schedule data.

#### Events / Jobs / Integrations

Calendar provider through owner adapter; webhook processing/reconciliation external to Job Interview; local handler consumes normalized result.

#### Failure Behavior

Provider outage never cancels interview automatically; unknown provider status becomes explicit unsupported/review; duplicate callback has no duplicate side effect; sync retries independently.

#### Tests

Adapter contract, signature/dedupe fixtures, update/reschedule/cancel idempotency, unknown status, provider outage and reconciliation.

#### Out of Scope

Availability-engine redesign, Booking lifecycle, direct Cronofy/Nylas SDK usage inside Job Interview.

#### Exit Gate

PASS only if local sync-field semantics are approved where used, Confirmed Booking & Calendar ownership is respected, no local provider-event dedupe truth exists, callbacks are verified/deduped/normalized by owner, interview truth survives provider outage, reconciliation passes, and all tests/build checks pass.

# Phase 4 — Cross-Cluster Contract Proof and Privacy


### 13 Privacy Executors, Retention, and Search/Media Erasure Handoffs

Privacy can enumerate CL-06 subject data and instruct each owning Module to erase, anonymize, restrict, export, or retain its records while Search/Media/provider effects are delegated to their owners.

#### Objective

Privacy can enumerate CL-06 subject data and instruct each owning Module to erase, anonymize, restrict, export, or retain its records while Search/Media/provider effects are delegated to their owners.

#### User-visible / Observable Result

Privacy can enumerate CL-06 subject data and instruct each owning Module to erase, anonymize, restrict, export, or retain its records while Search/Media/provider effects are delegated to their owners.

#### Owning Module(s)

Privacy owns orchestration; Organization Hiring, Job Compliance, Candidate Application and Job Interview each own mutation of their own records.

#### Dependencies

Candidate/interview features as applicable; Privacy target protocol; U-CL06-13 raw resume retention and approved Organization/Job/interview retention rules before destructive production execution.

#### Shared Operations Used

SH-096 `enumerateSubjectData` (Confirmed); SH-095 `executePrivacyInstruction` (Confirmed); SH-097 `evaluateRetentionRequirement` (Confirmed); SH-098 `anonymizePersonalFields` (Confirmed); Search removal; provider deletion through provider owners; Audit/Ops. No local PrivacyRequest workflow.

#### Data / Schema

Potentially all CL-06 personal-data records. `DataRetentionExemption` remains Privacy-owned. Candidate executor covers CandidateProfile, applications, parse text, resume/view logs and CandidateSearchProjection; other owners cover their records.

#### Public Interfaces

One versioned privacy target executor per CL-06 owner returning the canonical target-result envelope.

#### Logic

Enumerate owner data; apply local erase/anonymize/retain mapping; request Media object deletion and Search de-index where permitted; delegate provider resource deletion; return counts/evidence/exemption IDs; re-run idempotently.

#### UI / Administrative Surface

Privacy/admin UI remains Privacy-owned. CL-06 may expose authorized operational target details only.

#### Authorization / Compliance

Scoped system/service actor; explicit retention exemptions; no destruction of required proof; minimize retained personal data.

#### Events / Jobs / Integrations

Privacy workers, Search/Media/provider deletion requests, retries/dead-letter, completion events/audit.

#### Failure Behavior

Partial failure returns retryable/terminal target result; never falsely mark completed; retained data references exemption; downstream deletion failure remains visible.

#### Tests

Enumeration completeness, erase/anonymize, retention exemption, Search de-index, Media delegation, provider deletion fixture, idempotent rerun, export redaction.

#### Out of Scope

New privacy request/job models or orchestration inside CL-06.

#### Exit Gate

PASS only if Privacy is sole orchestrator, each Module mutates only its truth, candidate Search removal works, retained records cite exemptions, reruns are idempotent, partial failure is visible, and tests pass.


### 14 Cross-Cluster Hiring Contract Proof

The complete CL-06 hiring path is proven against neighboring owner contracts, using real interfaces where implemented and versioned fixtures otherwise, without direct cross-domain repository access.

#### Objective

The complete CL-06 hiring path is proven against neighboring owner contracts, using real interfaces where implemented and versioned fixtures otherwise, without direct cross-domain repository access.

#### User-visible / Observable Result

The complete CL-06 hiring path is proven against neighboring owner contracts, using real interfaces where implemented and versioned fixtures otherwise, without direct cross-domain repository access.

#### Owning Module(s)

All four CL-06 Modules retain their source truth; neighboring Clusters retain theirs.

#### Dependencies

Features 01–13 as enabled. Unimplemented neighboring systems may be contract fixtures, never locally recreated.

#### Shared Operations Used

Exercise all already-approved canonical operations used by the workflow. Do not invent a new shared operation solely to simplify tests.

#### Data / Schema

No ownership moves. Contract fixtures carry owner DTOs, decision envelopes, event envelopes and normalized provider results.

#### Public Interfaces

Freeze/version Organization owner facts, Job Compliance decisions/reports, Candidate application/resume/projection contracts, Job Interview contracts, and neighboring Track/Trust/Media/Search/Privacy/Hold/Audit/Messaging/Notification/Video/Calendar contracts.

#### Logic

Walk critical workflows with unavailable/deny/retry/duplicate/stale-version cases. Confirm each bridge fails closed or explicitly unavailable rather than falling back to direct DB access.

#### UI / Administrative Surface

No new product UI required.

#### Authorization / Compliance

Cross-Organization isolation, candidate privacy, Track/Trust/Hold enforcement and sensitive access proof are mandatory contract cases.

#### Events / Jobs / Integrations

Outbox/inbox, retries/dedupe, Search refresh/de-index, provider fixtures, Privacy target execution.

#### Failure Behavior

Neighbor unavailable → explicit unavailable/retry/deny; never permissive bypass or direct repository fallback.

#### Tests

Contract, integration, RLS, idempotency, privacy, provider degradation, Search de-index, and critical E2E suites.

#### Out of Scope

Implementing missing neighboring Module internals in CL-06.

#### Exit Gate

PASS only if no cross-Module repository write exists, every neighbor dependency has a typed contract/fixture, critical workflows preserve ownership, unavailable dependencies never produce permissive bypass, and the full suite passes.

# Phase 5 — Hardening and Production Readiness


### 15 CL-06 Security, Reconciliation, Backfill, and Production Hardening

All production-enabled hiring workflows are hardened for authorization, concurrency, replay, provider degradation, privacy, reconciliation, backfill, performance and destructive migration safety.

#### Objective

All production-enabled hiring workflows are hardened for authorization, concurrency, replay, provider degradation, privacy, reconciliation, backfill, performance and destructive migration safety.

#### User-visible / Observable Result

All production-enabled hiring workflows are hardened for authorization, concurrency, replay, provider degradation, privacy, reconciliation, backfill, performance and destructive migration safety.

#### Owning Module(s)

All four CL-06 owners plus canonical support Modules, each within its existing boundary.

#### Dependencies

All enabled prior features and every U-CL06 decision that affects those features must be resolved and reflected in architecture.

#### Shared Operations Used

Audit/access, observability, reliable jobs/retries/DLQ, reconciliation, idempotency, concurrency, Privacy, Search reconciliation and provider reconciliation. No new generic CL-06 infrastructure.

#### Data / Schema

Review indexes/constraints on Organization/member/Job/application/interview paths; outbox/inbox and job records in canonical infrastructure; safe checkpointed backfills; migration compatibility; deprecated field cleanup only after rulings.

#### Public Interfaces

Stabilize/version existing public contracts. Do not create new business ownership solely for hardening.

#### Logic

Hardening includes RLS/server parity, ownership/member races, Job publish/edit race, compliance rescan, application quota reconciliation, partial application recovery, resume parse retry/backfill, candidate Search rebuild/de-index, interview integration reconciliation, privacy rerun, dead-letter/admin recovery and retention enforcement.

#### UI / Administrative Surface

Only operational surfaces required for failed compliance jobs, parse retry, Search lag, interview integration failure, privacy-target failure and reconciliation. These views are not source truth.

#### Authorization / Compliance

Least privilege, support/admin review, access-audit completeness, telemetry redaction, destructive privacy review, secret/webhook review.

#### Events / Jobs / Integrations

Retry/dead-letter validation, Search rebuild, compliance rescan, Job close/interview expiry, provider reconciliation, alerting and safe backfills.

#### Failure Behavior

No silent loss, permissive fallback or source-state overwrite. Exhausted failure has an operational reference and accurate source status.

#### Tests

Full typecheck/lint/build; unit/integration/contract/E2E; RLS/security; concurrency/idempotency; privacy; provider degradation; reconciliation/backfill; migration rehearsal; query/load tests.

#### Out of Scope

New product features, Organization commercial plan without U-CL06-04 approval, automated hiring recommendations, new verification/legal policy, marketplace workflows.

#### Exit Gate

PASS only if all production-enabled architecture blockers are resolved; no lifecycle has two owners; no canonical operation is duplicated; publication, quota, resume privacy, candidate Search, interview boundaries, provider dedupe/reconciliation, RLS, privacy, audit and E2E invariants pass; documentation/progress agree with code.


## Cross-Cluster Integration Phase

Phase 4 is the explicit contract-proof phase, not an ownership-transfer phase. Minimum bridges:

```text
Identity actor → all protected CL-06 actions
Organization owner facts → Role / Authority
Job → Job Compliance decision → Organization Hiring lifecycle
Organization/Job projection → Search
Candidate application → Track quota
verified-only candidate gate → Trust Verification
resume attachment/access → Media
Candidate projection + Track boost → Search
Application/Interview events → Notification/Messaging
JobInterview → Video Session
JobInterview schedule policy → Confirmed Booking & Calendar calendar provider boundary; local sync-field semantics remain gated
Privacy → each CL-06 executor
ComplianceHold → action gates
Audit → generic audit/sensitive access proof
Ops → failure visibility only
```

If a neighbor is not implemented, use a versioned fixture. Never pull the neighbor’s source records or repository into CL-06.

## Hardening Phase

Phase 5 covers only CL-06 production risk:

- Organization/member/Job authorization and RLS;
- compliance decision reproducibility and rescan;
- Job publish/edit concurrency;
- application quota and duplicate-submission races;
- resume privacy/access proof;
- parser/Search degradation and reconciliation;
- candidate de-index/privacy;
- interview transition/reschedule concurrency;
- provider degradation/reconciliation;
- replay/idempotency;
- queue/dead-letter visibility;
- retention and audit completeness;
- telemetry redaction;
- indexes/query performance;
- backfill and destructive migration safety.

Hardening must not create a generic hiring source-of-truth table, readiness engine, state machine, event ledger, retry framework or provider-event table.

## Phase Summary

| Phase | Name | Features |
|---|---|---|
| 1 | Hiring Entity, Job Draft, and Publication Gate | 01–03 |
| 2 | Candidate Intake, Private Resume, and Recruiter Pipeline | 04–08 |
| 3 | Hiring Interviews and Collaboration Handoffs | 09–12 |
| 4 | Cross-Cluster Contract Proof and Privacy | 13–14 |
| 5 | Hardening and Production Readiness | 15 |

**Total numbered features: 15.**

## Phase Execution Pattern

Before each numbered feature:

1. Read root/shared/Cluster/target Module/dependency context.
2. Confirm previous exit gate passed.
3. Check relevant `U-CL06-*` blockers.
4. Write the feature implementation specification.
5. Confirm schemas, migrations, public contracts, permissions, shared operations, events/jobs, error semantics and tests.
6. Implement only that feature plus prerequisite changes in their canonical owners.
7. Run typecheck, lint, unit/integration tests, migration checks and build as applicable.
8. Verify the workflow including denial, retry, duplicate, stale-version and privacy paths.
9. Update progress.
10. Update architecture first if a binding decision changed.
11. Record assumptions, risks, unresolved questions and deferred work.

Do not weaken an exit gate to mark a feature complete.

## Required Feature Specification

Immediately before implementation, create a concise specification containing:

- Objective
- Observable result
- Dependencies
- In scope
- Out of scope
- Owning Module
- Data records affected
- Migrations/constraints/indexes affected
- Public interfaces
- Shared operations consumed by canonical name
- Permission/action vocabulary
- Primary workflow
- UI/admin states if applicable
- Provider integrations and explicit provider owner
- Jobs/events/outbox consumers
- Idempotency/concurrency key semantics
- Error/failure behavior
- Tests
- Acceptance criteria
- Documentation/progress updates
- Architecture decisions resolved or still blocking

Do not pre-write giant file-by-file specs for all 15 features. Specify the next feature immediately before coding.

## Required Completion Report

After each feature, report:

- Feature completed
- Observable result verified
- Files added
- Files changed
- Database changes
- Migrations
- Constraints/indexes changed
- Dependencies added
- Shared operations reused by canonical name
- Canonical-owner changes outside CL-06
- Public interfaces added/changed
- Domain events/outbox consumers
- Jobs/workers
- Provider adapters changed, with owner
- Tests added/changed
- Commands run
- Manual/workflow verification
- Authorization/compliance verification
- Idempotency/concurrency verification
- Privacy/audit/observability verification where applicable
- Documentation updated
- Assumptions
- Architecture rulings resolved
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result: **PASS / FAIL**, with evidence

A feature whose exit gate fails is incomplete. Do not begin the next feature until failure is resolved or architecture/build plan is explicitly revised.
