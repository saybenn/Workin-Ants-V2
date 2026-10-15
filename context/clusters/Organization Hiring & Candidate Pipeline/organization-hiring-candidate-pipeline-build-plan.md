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
- proposed SH-120 `normalizeJurisdictionContext` (Proposed ruling) owner/interface before jurisdiction-aware production compliance.

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

Feature 01 must expose Organization Hiring's compliance-input snapshot and scoped/cursor rescan-enumeration owner contracts before this feature consumes them. U-CL06-05/07 remain policy blockers; U-CL06-06 is a binding evidence invariant whose persistence design/implementation requires a later approved schema pass. SH-120 `normalizeJurisdictionContext` (Proposed ruling) remains Proposed ruling: production jurisdiction-aware evaluation requires its approved owner/interface. Rule/check persistence, owner-local scanner mechanics and deterministic fixtures with explicitly supplied normalized jurisdiction context may proceed below that gate; raw location strings are not canonical evidence and no local replacement is permitted. Shared proposed scanner/decision/owner-facts APIs require separate approval before cross-platform commitment.

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

PASS only if U-CL06-05/07 are resolved, the binding U-CL06-06 invariant has an approved implemented persistence design, SH-120 `normalizeJurisdictionContext` (Proposed ruling) has an approved owner/interface, and any proposed SH API/schema commitment has separate approval; both Organization source contracts pass consumer tests; identical immutable input and complete applied-rule proof reproduce the result after later Job/rule changes; zero-finding pass records every applied rule; technical failure cannot approve; Job Compliance never owns Job lifecycle; reviewer/admin actions are authorized/audited; all tests/build checks pass.


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

## WA-R009 — Jurisdiction normalization status and ownership

SH-120 is Proposed ruling, not Unresolved. It shares normalization/provenance mechanics while each jurisdiction-dependent owner selects and interprets evidence for its own purpose. Location's geography does not become neutral tax/employment authority; Payment owns tax interpretation and Job Compliance owns employment-jurisdiction interpretation. An owner-specific normalized-input contract may be implemented without adopting a universal jurisdiction DTO. Production use still requires sufficient legal/provider/source evidence and an explicit binding. No local competing universal normalizer or generic legal decision service is authorized.

## WA-R010 — Split compensation stewardship from contract-job meaning

The ownership part of U-CL06-07 / PR-JC-03 is AI_RESOLVED: Organization Hiring owns CompensationPeriod because it owns the offered Job compensation facts. Job Compliance reads and snapshots the same vocabulary; it does not acquire Job source truth or create another enum. Registry ownership is aligned, with no schema/value change.

P03 is APPROVED in WA-R013: fixed-term employment and independent-contractor work are distinct canonical concepts. Ambiguous historical contract values require source clarification; production activation requires the coordinated schema/API/filter change and applicable legal rules. The product choice is closed; implementation and legal evidence are separate prerequisites.


## WA-R013 — Explicit work arrangements (P03)

Product-owner ruling approved 2026-09-29: distinguish **fixed-term employment** and **independent-contractor work** as separate canonical concepts. A generic CONTRACT/contract value must not hide the distinction. This closes the product-meaning portion of U-CL06-07 / CL-06-U007. WA-R010 already assigns CompensationPeriod stewardship to Organization Hiring.

Hiring owns the work-arrangement vocabulary and source selection. The canonical concepts are FIXED_TERM_EMPLOYMENT and INDEPENDENT_CONTRACTOR; exact persisted enum spelling follows schema conventions in the coordinated database pass. Job Compliance consumes the explicit arrangement, preserves it in evaluated input/rule evidence and applies the relevant approved rule set. A selected label is not a legal determination of worker classification. Applicable jurisdictional legal rules remain an external gate.

Search projects the explicit owner-provided concepts and presents distinct filters/labels; it cannot derive them from job title, compensation period, or old contract text. Legacy EmploymentType.contract is ambiguous: preserve historical value, require authorized source clarification before affected republication/re-evaluation, and do not silently map every old row to either new concept. Reindex only after owner correction. Existing unambiguous employment types remain unchanged. Organization contractor Jobs remain Hiring work, not automatically Gigs or Offerings.

Implementation acceptance: distinct create/edit/publication and query/filter paths; exact compliance input and evidence for each concept; ambiguous historical rows blocked from new publication until clarified; no mass inferred backfill; no legal conclusion based only on employer-selected label. Prisma's present enum is implementation reality, not evidence that this ruling has been migrated.


## WA-R017 — Owner facts and decision contracts

**Applied architecture ruling (AI_RESOLVED), 2026-09-30.** The [WA-R017 contract](../../reconciliation/platform-architecture-rulings.md#wa-r017--owner-facts-and-decision-contracts) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

SH-003 is a family of small owner-specific queries, not a mandatory universal DTO. Each query takes authenticated caller/purpose and a typed owner resource reference, exposes only required authorized facts with an owner-issued source token, and distinguishes unavailable/stale from absence or denial. Consumers do not load foreign Prisma records. SH-015 remains a reusable result pattern, not a universal domain enum: carry a decision category, stable owner reason code, evidence/source token and evaluation time; payload variants remain owner-specific. Domain outcomes such as Job Compliance warning/review_required and Healthcare redacted/blocked retain their distinct meaning. An unavailable prerequisite never becomes allow. Exact wire names/runtime schemas are DEFERRED_IMPLEMENTATION_DETAIL inside these constraints and must be fixed in producer/consumer fixtures before parallel integration.

Adopt this interpretation for all references that formerly treated SH-003/015 proposal status as an unconditional blocker on owner-specific interfaces. Neither SH status is promoted. New generic repositories, universal authorization or generic business-policy dispatch are forbidden. Grouped owner-specific contracts do not become interchangeable because their envelopes look similar.


## WA-R021 — Notification recipient and attempt model

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R021 contract](../../reconciliation/platform-architecture-rulings.md#wa-r021--notification-recipient-and-attempt-model) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one logical Notification per resolved User recipient and semantic source intent; channels are deliveries of that notification. Organization is source/context, not an inbox principal. Hiring supplies the authorized recipient set and source-policy version; Notification expands/deduplicates User recipients and snapshots the resolved routing context. Revalidate current sensitive access before including protected payload or dereferencing context; a historical fan-out snapshot grants no future access. Source Modules own recipient eligibility and message meaning; Notification owns safe rendering, channel routing and provider mechanics.

Each delivery attempt has its own immutable attempt identity and correlation to logical notification, recipient, channel, destination generation and semantic send key. Retrying unknown provider outcomes reconciles before resending. Provider acceptance is not confirmed delivery or user interaction. Notification summary separately tracks pending/in-progress, partial success, all required routable deliveries successful, or exhausted failure; dismiss/read state remains independent and never alters source workflow status. The database pass must provide a representation for partial delivery rather than mapping it to total success. Policy may mark a channel optional; that requirement is snapshotted before dispatch, not rewritten to hide failure.

Persist dismissedAt/expiresAt when these actions/policies apply. User interaction is Notification-owned append-only evidence separate from Delivery receipts. Template versions are immutable and schema-validated; source supplies a registered semantic template intent plus allowlisted variables. Generic external channels carry minimal safe summaries/deep links, never raw message bodies, financial/tax documents, exact addresses or regulated data by default. Identity challenge-provider transport stays Identity-owned. Concrete provider selection/configuration and legally sufficient notice delivery remain external prerequisites.

Tradeoff: explicit parent/attempt representation needs schema alignment but avoids multiple inbox items per channel and false completion. Acceptance: organization fan-out dedupe, removed member sensitive access, duplicate send, partial channel failure, expiry/dismissal independence, callback before/after retry, unsupported channel and secret redaction.


## WA-R023 — Sensitive disclosure and audit failure boundaries

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Require a durable sensitive-access audit acceptance before returning exact private location, protected file/playback/join credentials, resumes, healthcare-sensitive fields, tax/identity/Agreement evidence, or sensitive admin exports. If required proof cannot be durably recorded, withhold the protected response and return a retriable unavailable result; never return the secret and log later. Record safe allowed/denied/redacted/blocked/unavailable outcomes under Audit-owned vocabulary without importing Healthcare enums as generic authorization. Include service/system/provider actor attribution and request correlation, not nullable User alone. A denied request must still disclose no target-existence details; audit trouble never changes denial into access.

Privileged irreversible mutations require durable owner decision/history plus atomic audit-outbox intent before committing owner state. If that local durable write fails, roll back the mutation. Later Audit transport failure retries/reconciles; it does not roll back an already executed external financial/legal effect or erase domain evidence. Where a legal action specifically requires pre-action Audit acceptance, its owner contract adds that stricter gate; legal deadlines/recovery remain scoped requirements. Low-risk diagnostics are best effort and never recursively produce infinite failures.

Identity owns fresh action-bound assurance; Role still authorizes the action. Require step-up for security-factor/recovery changes, financial adjudication/movement, privileged permission changes, bulk sensitive evidence export and administrative override/release of protective controls. Existing sessions or admin roles do not substitute. Exact assurance methods/lifetimes and action registration are security implementation policy, with provider capability checked before activation. Ordinary read access is not automatically all step-up; owner-specific policy may require it. Privacy identity verification is a separate statutory proof requirement.

Tradeoff: protected access becomes dependent on durable audit availability; this is preferable to an unprovable sensitive disclosure. Acceptance: audit unavailable before response, durable intent failure before mutation, outbox delivery outage after commit, privileged service actor, retry without duplicate effect, denied-target anti-enumeration and redaction-safe evidence. These rules amend failure/assurance portions only; per-owner legal retention and complete target/action matrices remain separate work.

Duplicate-collapse scope: CL01-HU-006/007/008/012 security portions; CL02-D025/044/056; CL04-U032; CL-05-U007/062; CL-06-U048/055; CL-08-U16 and HU-09/19; CL-09-D016/030/031/032/035/043/046; CL-10-HU031/PR-CL10-09. Unnamed adjacent questions are not closed.

## WA-R030 — Track catalog, enrollment, immutable grants and usage protocol

Classification: AI_RESOLVED_WITH_TRADEOFF. Track remains the commercial-policy owner; Candidate owns applications, Search owns ranking projections, Order owns transaction snapshots and Payment owns financial effects. This resolves technical representation/protocol alternatives; paid cancellation/grace and application quota product policies are explicitly separated below.

Represent free participation as an explicit Track-owned enrollment in a versioned free plan for each activated actor track, not absence of a subscription, a Stripe-created $0 subscription or a consumer-local free flag. Introduce a provider-neutral free enrollment representation; current provider default `stripe` must not label free records. Provision idempotently by User/track/profile identity. At most one current base enrollment selection exists per User/track; pending paid attempts may coexist without becoming current. Exactly one Customer/Candidate/Professional profile binding must match the selected track and User. Enforce typed FK/check constraints, user/profile consistency and current-selection uniqueness in the coordinated migration. Separate Organization ATS subject scope remains WA-R005, never a fourth AccountTrack. Historical enrollment rows remain reconstructible.

TrackPlanPrice is canonical for immutable amount/currency/billing cadence and provider-price correlation. TrackPlan.monthlyPriceCents is a compatibility/display projection and never a second price editor. A paid enrollment binds an immutable plan revision, price revision and applicable Consent proof/presentation; old enrollments and Order quotes never silently read today's edited price. Separate BillingCadence from TrackUsagePeriod. Existing monthly prices remain product truth; no new cadence, trial or price is invented. Activate a new revision only after catalog validation, retain effective intervals and prevent conflicting active revisions for the same selection key. Retiring a plan stops new enrollment, not evidence or previously authorized benefit periods. Accept conservative plan graph draft→active→retired→archived and draft→archived; archived is terminal, later publication is a new revision.

Catalog definitions are immutable typed keys with actor scope, value schema/unit, combination rule, period applicability and consuming capability. At most the designated value field may be populated and its type must equal the definition. Validate integer/money bounds, basis points and versioned JSON schemas; raw JSON is not executable policy. The initial product-backed key meanings are Candidate application allowance (15/month free, unlimited paid), Candidate employer-search boost (0 or 1500 basis points), verified-applicant plan badge and application-view insights; Customer qualifying buyer-fee waiver and early-availability eligibility; Professional commission (1000 or 300 basis points). Exact persisted key spelling is a coordinated contract constant, not a consumer-created alias. Additional unspecified premium features/ATS prices/limits are inactive catalog entries until explicitly defined; enum presence grants no benefit.

Resolve one current base plan revision, then only applicable active grant revisions. Equivalent benefits do not stack automatically. Each grant must declare an approved composition mode: extend duration, add a bounded quota, provide separately scoped value, or no additional effect for an equivalent benefit. Reject ambiguous overlap/configuration before grant activation; do not choose a winner by insertion order or a universal max/sum rule. An explicit replacement identifies the superseded grant with history. A grant never bypasses Role, readiness, Hold or source-owner eligibility. Accept grant graph active→expired/revoked/suspended/consumed; suspended→active only with authorized restoration and current validity, or →expired/revoked. Consumed is one-shot only; expired/revoked/consumed records are terminal. Append Track-owned immutable grant transitions, separate from audit and provider receipts; use a dedicated grant-history record or typed owner event table with equivalent append-only guarantees, not only mutable grant columns.

Track's Billing adapter owns subscription normalization and owner-specific provider receipts. A shared verified Stripe ingress routes by registered integration/account/resource/event purpose to Track or Payment; each owner has an independent effect receipt keyed by owner+provider-account+event ID, so one owner's receipt never suppresses the other's legitimate effect. Neither owner mutates the other's subscription/payment truth. New paid checkout starts incomplete, never default active. Provider confirmation is authenticated evidence bound to the exact attempt/price/subject. Out-of-order callbacks trigger owner reconciliation/version checks, not timestamp-only last-write-wins. Transition, immutable history and outbox commit together. Unknown financial/provider state cannot create paid access. Exact trial/grace/cancellation/downgrade benefits remain product policy, not imported from a provider enum; this ruling does not enable them.

Usage is an owner protocol: versioned period policy supplies a durable period identity/start/end/timezone; subject+track+entitlement+period policy/version identifies the counter across free/paid plan switches. Switching plans or provisioning another record never resets same-period consumption. Keep the counter rebuildable from immutable accepted consumption and compensating events. No destructive monthly reset or consumer-local quota. Semantic key binds source owner, source command/logical action, subject and entitlement; same key/fingerprint returns the same receipt, different payload conflicts. Quantity and policy revision persist with the receipt. A correction references the original event, is authorized by the source/Track policy and can compensate once; withdrawal or a monetary refund is not automatically a usage reversal. The actual monthly boundaries and withdrawal policy still require the product ruling identified in the decision packet.

For Candidate application submission use durable reservation/commit/reconcile, not foreign repositories or a distributed database transaction. Candidate first validates subject/Job eligibility and creates a stable submission intent. Track atomically reserves allowance and returns reservation/period/policy proof. Candidate commits the application once with that reservation, then emits a durable confirmation; Track converts the reservation to consumption idempotently. A duplicate source submission returns the original application/receipt. In-flight reservations reduce remaining capacity. On timeout query the Candidate submission outcome; release only on proven non-commit or owner-confirmed cancellation that prevents later commit. Unknown remains reconcilable, never silently free capacity. Withdrawal after successful commit follows the separately approved quota policy. Background cleanup cannot free a reservation while an application can still commit against it. This protocol is FOUNDATION_CAPABILITY, not full CL-01 maturity.

The approved Candidate subscription boost is non-metered effective ranking metadata, not a billable impression/application event. Search applies a 1.15 multiplier to its nonnegative base relevance/quality score only after all audience/eligibility/privacy filters; zero remains zero and deterministic ties use the normal stable tie-breaker. It is not a guarantee of 15% more views or permission to enter a protected result set. No `candidate_search_boost_applied` usage debit is enabled merely because the enum exists. Bound the projection to Track evidence/version and refresh on effective benefit change; stale or unavailable paid-boost evidence cannot silently confer a bonus. Earned separate boosts require their explicitly approved combination rule.

Fee/commission quotes carry integer basis points, currency, applicable basis identifier/amount, policy/plan/grant revisions and evaluation time. Order freezes the quote at its approved pricing/acceptance boundary. Use checked integer minor-unit arithmetic with deterministic round-half-up for nonnegative fee/commission calculation; sum the persisted rounded line allocations to the total and distribute any explicitly required remainder deterministically by stable line identity. Never use binary floating point or recompute old orders from current rates. Tax's jurisdiction-specific rounding remains Tax policy. A missing approved fee basis/eligibility policy is unavailable, not an invented charge. Payment consumes the Order-authorized monetary result, not a second Track fee calculator.

Required validation before activation: free/paid concurrent selection, wrong profile/actor binding, price revision change, typed value mismatch, ambiguous grants, grant restoration after expiry, duplicate/provider cross-owner event, quota contention/plan switch, crash before/after Candidate commit, unknown reservation outcome, duplicate compensation, stale boost and exact price rounding vectors. Schema/runtime proof remains unperformed at this architecture checkpoint.

## WA-R031 — Authority policy, Customer lifecycle and shared review claims

Classification: AI_RESOLVED_WITH_TRADEOFF. Role interprets authority, Identity/Hiring/Messaging retain role/membership/participant lifecycle. No general admin bypass is created.

Use a versioned code-first Role action/resource policy catalog with explicit owner, accepted actor scopes, minimal owner-facts contract, allowed relationships, freshness/version requirements, sensitive-access proof and step-up obligations. Each protected owner public command/query registers one canonical action before activation; unknown/unregistered action denies. Human-readable action names derive from the owning interface rather than a new generic Cluster service. Roles alone never waive source lifecycle, Hold, commercial, Healthcare or privacy checks. An admin may perform only explicitly registered admin actions; support is limited to authorized support views/intake and attributed on-behalf actions, not role assignment, money movement, restoration or unrestricted evidence access by virtue of support role alone. Financial/adjudication/security operators require the specifically granted action and fresh assurance. Additional access needs a catalog amendment, not `isAdmin` fallback.

Organization matrix: owner may manage membership/administrators, transfer ownership through Hiring's checked workflow, and manage hiring resources; admin may manage ordinary hiring resources and recruiter membership, but cannot replace/remove the owner, self-promote or grant owner authority; recruiter may manage assigned Jobs/applications/interviews subject to Hiring/Candidate/Interview facts, but not organization ownership, membership administration or billing. Member/viewer values remain inactive/deny-by-default until a separately defined action set exists. Current relationship facts are queried from Hiring; removed membership takes effect on the next protected request. Thread membership is Messaging truth, never inferred from having an Organization role. Identity appends immutable UserSecurityEvent/Audit intent for platform-role assignment/revocation in the same mutation transaction; no second Role-owned role table.

Server services enforce Role policy before owner operations. Use handwritten reviewed RLS/SQL implementations where database-side policy applies, with one shared semantic fixture matrix comparing server/RLS allowed and denied cases. Do not generate SQL from arbitrary executable application predicates. Baseline protected domain tables deny direct anonymous/authenticated client CRUD; exposed read models require a separately reviewed allowlist and RLS policy. Server credentials do not eliminate owner checks. Enumerate every table/view/function exposed to API/database roles in the migration review; no unreviewed relation becomes public by default. Add identity-map-aware policies under WA-R027 rather than assuming provider subject equals User.id. This is the parity/coverage method; actual grants/RLS/schema replay stay under database readiness. Keep authorization cache and Role domain events absent at launch; add caching only with proven revocation/version invalidation, and events only for a real consumer.

Return the same safe public response for missing versus unauthorized private targets where existence is sensitive. Preserve distinct internal reason classes unknown_action, insufficient_authority, missing_relationship, stale_or_unavailable_facts, step_up_required and policy_unavailable for diagnostics and authorized UI handling. Never make outage equivalent to allowed. Resource owners choose a purpose-limited safe denial message; internal IDs, evidence and reason details are not automatically public. WA-R023 durability still governs protected disclosure. Concrete owner DTO field sets remain bilateral qualification work; no universal `queryOwnerFacts` DTO is adopted.

CustomerProfile lifecycle: normal idempotent provisioning produces active after Identity eligibility. Optional draft can activate only through Customer validation; self-service active↔paused controls new buyer participation. Customer owner may archive active/paused/draft after checking obligations; archiving stops new buyer actions and retains access needed to fulfill existing Orders, Bookings, disputes, refunds and statutory requests under those owners' current permissions. Archive does not cancel a transaction, discharge debt, erase proof or hide an active restriction. Restoration of archived returns to draft for current eligibility checks; suspension is a separate authorized owner action with reason/history, not a mirrored Hold. Only an authorized owner/moderation restoration with current checks may leave suspended; self-service pause/archive/restore cannot clear it. Privacy deletion/anonymization is its own approved executor path. No automatic status transition on receipt of a generic Hold event.

Persist append-only Customer lifecycle evidence (typed owner event record or retained lifecycle journal) alongside the state change because archive/restoration and obligations now require reconstructible history; outbox dispatch retention alone is insufficient. This specifically supersedes the prior no-dedicated-history-unless-required proposal by supplying the requirement, without requiring a second generic platform ledger. Customer's contextual display fields override account display defaults only within Customer views. Copy defaults once on provisioning with provenance; do not synchronize later edits bidirectionally. Customer remains absent from public discovery; this does not change Candidate/Professional public projections. Customer avatar is an explicit Customer-owned MediaAsset FK/reference with retention-safe deletion and Media validation, not a polymorphic attachment repository. Existing legacy buyer User references backfill through the one-profile-per-User owner resolver; preserve original attribution and quarantine mismatches, never choose by display name/email. Review/Dispute bind the authoritative Order participant identities under WA-R026.

Adopt feature/Module-first logical domain/application/contracts/infrastructure/workers/privacy separation where relevant; adapters/routes are thin. These are ownership boundaries, not permission to reorganize current code or create a generic CL-01 domain service. A Module references another owner's public contract, not foreign repository/entity ownership. Remove obsolete Identity `TrackEntitlement` schema reference: Identity's actual documented dependency is supplying User facts to Track, not reading either entitlement definitions or grants. Do not guess a replacement schema or create the obsolete model.

SH-054 shared work claiming is a persistence capability: claim by work-kind/owner item ID with holder, lease deadline, monotonically increasing fencing token and expected owner version; renew/release/complete compare token. Expired holder cannot commit a decision or acknowledge another holder's work. Manual reviewers obtain Role authority and domain evidence separately; a lease does not approve a case. Review workflow truth remains in the owning Module. Use the shared Postgres transaction/locking layer, not a new generic moderation/recovery case. Capability activation requires concurrent claim, stale holder, renewal failure and crash/reclaim tests. Proposed registry status remains until concrete shared API qualification; technical placement is resolved.

Acceptance: public/client table access denied unless explicitly reviewed; server/RLS parity; stale membership and private-target denial; support cannot escalate; owner transfer cannot lose the final owner; profile archive preserves outstanding obligations; suspension cannot be self-restored; buyer backfill conflict quarantined; stale review lease cannot commit. Per-resource action registration/fixtures, legal retention and actual DB grants remain explicit implementation requirements, not claims of completed runtime validation.

## WA-R032 — Approved subscription benefit periods and Candidate quota (P12/P13)

Binding product-owner ruling, 2026-10-01 America/New_York. Supersedes P12/P13 open alternatives; WA-R030's owner boundaries and durable reservation/history design remain binding.

Cancellation or voluntary downgrade takes effect at the end of the already-paid subscription period. Premium benefits remain active through that paid-through time. Failed renewal creates no unpaid premium grace at launch. Provider retry/recovery may continue, but premium benefits end at the previously paid boundary unless payment is successfully recovered. Later recovery may resume benefits within the valid renewed entitlement period; never fabricate retroactive usage rights. Return to the applicable free-track policy when premium entitlement ends.

Existing purchase, Order, Booking, digital-access and other rights validly acquired while premium are not revoked merely because the subscription ends. Their owning Module/policy determines continuing rights. Subscription change cannot reprice an accepted Order, cancel an accepted Booking or revoke a purchased download by itself. End only the current subscription-derived benefit. No automatic free trials, subscription pauses or automatic prorated cancellation refunds at launch. Refunds follow approved refund policy rather than cancellation implying a refund. Core account/security access is never paid-only.

Track separates provider billing/recovery state from effective benefit intervals. A cancel request records scheduled end plus immutable intent/history; it does not set present benefits to false. Verified payment evidence binds a specific enrollment/price revision and paid interval. Query-time evaluation enforces interval boundaries even if the expiry worker is late. Past-due/retry state alone cannot extend the paid-through interval. A late recovered payment records the valid new interval and observation/activation time; effective resumption starts no earlier than verified recovery and never reauthorizes denied historical actions. Duplicate receipts cannot extend a period twice. Terminal or expired enrollment history is preserved; renewed access is an explicit versioned entitlement selection, not history overwrite. Paused/trial enum values remain unsupported launch transitions. Payment truth, retries and Track entitlement evaluation remain separate owners.

Free Candidate users receive 15 successful application submissions per UTC calendar month. Consume one quota unit only when one logical submission succeeds and is durably accepted into Candidate's application workflow. Failed attempts, retries, duplicate transport and rejected technical writes consume zero. Later Candidate withdrawal, employer rejection or any downstream application outcome does not restore a consumed unit. A proven technical duplicate/error is corrected by an authorized append-only adjustment referencing the original, not by deleting usage history.

Persist successful monthly usage for every Candidate submission, including while Premium is unlimited. The effective unlimited plan bypasses the numeric cap, not usage recording. On return to Free within that UTC month, available allowance is max(0, 15 minus already-recorded successful monthly usage), including Premium-period successes. Plan changes cannot reset counters, duplicate usage or create another 15. Calendar boundaries are half-open [first day 00:00:00 UTC, next first day 00:00:00 UTC); the owning Candidate durable acceptance timestamp selects the month, not the client clock or delayed outbox delivery time. Preserve policy revision, source intent/application, accepted timestamp and consumption identity.

For a submission spanning a month boundary, Track's capacity reservation must cover the month in which Candidate commits acceptance. Candidate must not commit against an expired prior-month authorization: renew/rebind the reservation under the new period, check the current plan/remaining capacity, then durably accept once. Store the resulting period proof with acceptance. At the period boundary, use a server-authoritative time/transaction guard and reconciliation so cleanup cannot release a reservation still eligible to commit. Unknown outcomes remain reserved until reconciled; failed/noncommitted work consumes zero. Successful unlimited submissions still produce idempotent consumption evidence without denying submission for exceeding 15. A late confirmation applies to its proven acceptance month, never the arrival month.

Required implementation checks: cancellation before paid end; failed renewal at boundary; recovery before/after boundary; duplicate recovery; preserved purchased rights; no retroactive authorization; 15/16 simultaneous Free submissions; failed technical writes; duplicate receipt; withdrawal/rejection without credit; Premium submits above 15 with recorded usage; downgrade with zero remaining allowance; period-boundary submission and delayed confirmation. These are acceptance requirements, not claims of runtime execution.

## WA-R033 — Taxonomy semantics, history and AI proposal boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Taxonomy owns canonical term meaning and validation; contextual owners own accepted assignment joins. Join `verified` means an explicitly recorded authorized classification review, never Trust/KYC/Healthcare verification. Mere accepted attachment is not reviewed verification. Do not infer reviewed=true for legacy rows with unknown provenance; preserve them as unknown/unreviewed pending owner correction. Store reviewer/action/evidence/version when review is asserted. AI confidence is nullable integer basis points 0..10000 on the proposal, with model/prompt/output-schema/version provenance; it is model confidence, not calibrated correctness or authority. User/admin-authored assignments have no fabricated confidence. Accepted joins may retain a proposal reference and immutable provenance snapshot, but confidence never becomes a permission gate or competing current score. Legacy Float values are not auto-rescaled without proving their source scale. Candidate-authored tags use TagSource.user with CandidateProfile/User attribution; no new candidate source enum is required.

Adopt no normal hard-delete command for Domain/Category/Tag. Effective activity includes every ancestor's activity; ancestor reactivation does not rewrite child records. New assignments require effective-active terms. Historical accepted assignments retain term/version evidence even if the term later becomes inactive. Existing boolean active/inactive is sufficient for that lifecycle. A Tag must match the target's declared accepted Category at launch; multi-category assignment requires an explicit versioned compatibility policy, not arbitrary cross-category attachment. Parent IDs are immutable through ordinary edits. Exceptional reparent/merge runs require preflight affected-owner enumeration, compatibility review and controlled migration, never foreign join writes.

Persist immutable Taxonomy revisions/change records for labels, hierarchy, activity and represented compliance-trigger facts. Use stable term IDs and monotonically advancing owner revisions; updatedAt plus generic Audit is insufficient for historical interpretation. An alias points to exactly one stable canonical term within the same domain/type/locale normalization scope; alias cycles and conflicting normalized keys reject. Merge creates a durable from/to/version decision and alias/retirement mapping, preserves the source record, and requests each contextual owner to revalidate/repoint its own references with expected versions. Preserve original term/version in historical decision snapshots. Do not declare merge complete until required owner acknowledgments reconcile. No generic cross-owner migration service owns assignments.

Normalize term comparison keys using an explicitly versioned Unicode NFKC plus full case-fold and trimmed/collapsed Unicode whitespace; preserve punctuation and diacritics rather than conflating legally distinct terms. Include normalized locale and parent/type scope. Labels remain original display text. Alias registration is explicit, not automatic semantic synonym generation. Detect collision before creating or upgrading a normalization version; an algorithm change requires a dry-run collision report and owner migration. Slugs are owner-scoped stable public identifiers: use the shared primitive, uniqueness constraints and deterministic collision suffix; label edit does not silently rename an existing slug. Historical redirects/aliases are explicit owner records. Exact approved production seed content is an external reference-data requirement; no invented vocabulary is approved by this mechanism.

Additional license/background/location/Healthcare triggers use a versioned mapping owned by the interpreting requirement owner (Trust, Healthcare, Location or Job Compliance), keyed to Taxonomy term/revision and supported action/jurisdiction. Taxonomy supplies represented facts and change references, not clearance. Absent unsupported mappings do not imply readiness. DataSensitivity vocabulary follows Ubiquitous Language/compliance authority; source owners classify their own data and Healthcare separately owns explicit Healthcare boundaries. No generic scanner/AI inference can clear a sensitivity label.

Adopt the AI owner's two-record design: AiClassificationLog for a run and AiSuggestion for proposals, with append-only transition evidence. Run identity binds target owner/type/id/source version, allowed purpose, requester, model/prompt/normalization/output-schema versions and a semantic command identity. Keep queued→running→completed/failed/cancelled; queued may cancel. Cooperative cancellation prevents any late response from applying, even if provider work cannot be stopped; record late attempt outcome separately. Terminal runs never reopen; rerun is a new explicitly authorized run. Suggestions have unique run+candidateKey, exactly one value shape, and proposed→accepted/rejected/superseded/invalidated. Accepted requires a durable contextual-owner mutation receipt, never provider confidence or reviewer intent alone. Accepted/rejected dispositions are immutable; later assignment changes belong to the contextual owner.

Initial AI targets are ProfessionalProfile, Offering, Organization, Job and CandidateProfile; purposes are taxonomy_suggestion and skill_extraction. Gig AI is deferred because no bilateral target contract is established; ordinary Gig taxonomy assignment still works. Existing active canonical IDs only for taxonomy suggestions. Novel terms remain review-only and cannot be created by accepting an AI suggestion; independent authorized Taxonomy creation follows ordinary validation. Store logical term ID plus immutable term revision/label/path snapshot validated by Taxonomy; no cascading FK from proposal deletion into accepted truth. Keep normalized suggestions, validation result, canonical output hash and minimal provenance, not full raw provider bodies or source text. Provider/legal retention remains external; deleting AI evidence never deletes accepted assignments.

Use immutable code/config prompt versions with hashes at launch; no new database prompt publisher or first-class AiBackfill business model without a real additional lifecycle requirement. Bounded per-target runs and shared queue checkpoints suffice. Source adapters return purpose-limited normalized approved fields; Candidate supplies normalized skills/experience categories, never raw resume/application text at launch. Healthcare-sensitive transmission is disabled until source/Healthcare purpose-specific authorization and qualified provider/BAA evidence exist. No fallback model, region or logging change may silently widen the approved data boundary. Bedrock model/account/region/logging/retention configuration is external activation evidence, not selected by this architecture ruling.

Contextual owner commits accepted assignment and an immutable acceptance receipt/outbox fact atomically after fresh Taxonomy and source-version checks. AI consumes the receipt idempotently to record disposition; a timeout queries the contextual owner receipt rather than repeats the mutation with a new key. This is recoverable choreography over owner truth, not a generic CL-02 saga. Taxonomy admin composition may display proposal evidence and route assignment decisions through the actual context owner; shared review leases use WA-R031 and do not confer approval. No baseline AI→Search proposal feed or end-user classification notification. Broad backfill/configuration/merge and sensitive evidence exports require registered Role actions and fresh step-up under WA-R023/031; low confidence never creates a Hold by itself.

Required implementation checks: confidence source/range, unaudited verified claim, ancestor inactivity, normalization collision, alias cycle, stale assignment/term version, merge owner failure, late cancelled response, disposition-before-mutation rejection, duplicate acceptance receipt and raw/sensitive provider input rejection. Physical migrations, per-target DTO field allowlists, approved seeds, legal retention and provider capability are still separately qualified before activation.

## WA-R034 — Search work, protected transport and completion evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Search remains rebuildable projection. Source owners supply opaque currentness tokens, purpose-limited field allowlists and a currentness query; do not compare arbitrary tokens lexicographically or rely on wall-clock updatedAt alone. Search assigns a monotonic per-target work generation under a target lock and records all relevant source/visibility/Track/Location/Moderation evidence versions. Before writing and before exposing protected results, re-evaluate current source authorization and projection applicability. An older job cannot supersede a newer generation; deletion/restriction tombstones take precedence until current owner evidence explicitly permits publication again. Provider-native conditional writes are not assumed: adapters must prove their serialization/reconciliation behavior, and server query filtering prevents stale provider data from becoming an authority bypass.

Evolve SearchUpsertEvent into Search-owned durable work with request/command identity, typed target/source owner, expected tokens, generation, operation/purpose, pending/processing/completed/failed/superseded state, outcome and attempt/provider correlation. Shared queue leases/retries are separate. pending→processing; processing→completed/failed or pending for technical retry; stale work→superseded with successor correlation. Completed outcomes are upserted/removed/no_op/skipped with explicit reason and confirmed generation. A privacy removal cannot be marked completed from skipped/unavailable source facts. Same request/fingerprint replays the same work/result. Exact Prisma columns/indexes follow coordinated schema ownership, not a second queue.

All Search queries are server-mediated at launch, including public queries. No browser receives privileged or public Typesense credentials. Use independently versioned per-entity public collections with controlled alias cutover after full validated rebuild; protected Candidate collections/credentials are separate and never part of public federated queries or public counts/facets/autocomplete. Admin write credentials remain distinct from scoped server query credentials. Verify actual provider configuration/capabilities before activation; no current provider feature is presumed from these architectural requirements. Schema migration builds a new generation, validates completeness/currentness, then atomically changes the serving configuration; retain rollback generation without restoring revoked projections.

Protected Candidate search composes authenticated actor, current Organization membership/action authority, applicable Organization commercial permission, Candidate owner-approved searchable projection/visibility, applicable Hold/Moderation restrictions and field-level access policy. A result cannot imply permission to open a resume: resume access uses Candidate and Media separately. Search revalidates each returned Candidate's current projection/permission before disclosure; deny/unavailable removes that result rather than returns stale sensitive fields. Suppress provider totals/facets that expose filtered protected populations. Record one durable access batch proof before each protected response with requesting actor/Org/purpose, query fingerprint, permitted result target/version references and outcome; do not log raw sensitive query text. Resume/detail access produces its own required proof. If mandatory proof cannot commit, withhold the response under WA-R023.

Public results also obey current source restrictions; query sanitization and bounded result sizes apply before provider access. Basic relevance plus a stable target-ID tie-breaker is the launch ranking baseline. Advanced trust/recency/featured weighting is deferred versioned tuning, not a new premium benefit. Candidate's approved subscription boost follows WA-R030 (1.15 after eligibility, non-metered); it never changes privacy/eligibility. Generic User and CustomerProfile public indexing stay disabled; reserved enum values do not authorize publication. Search receives accepted source facts only, not raw AI suggestions or AI diagnostic history.

Source enumeration uses opaque stable cursors, snapshot/high-watermark identity, target/source token and explicit end-of-snapshot completeness. Each contextual owner enumerates its own records/joins. Incremental iteration cannot prove an unobserved target is deleted. Orphan removal requires a complete comparable source snapshot or an explicit owner deletion/tombstone receipt; cursor interruption never means empty source. Taxonomy changes request affected-owner enumeration and each source requests refresh through Search; neither Taxonomy nor Search scans foreign joins. Required per-target projection/AI/authority DTO field lists remain owner-specific and need bilateral qualification; the common mechanics do not approve arbitrary fields.

SH-091 returns accepted work identity, not completion. Search exposes a versioned completion receipt/query bound to request/work identity, typed target, requested generation/policy and verified outcome. Privacy/Moderation require removed/no_op-absent proof for their exact instruction; missing/timeout/provider uncertainty remains pending/unavailable. Receipt persists provider acknowledgement and reconciliation observation; tombstone prevents late stale jobs from resurrecting removed content. A superseded work receipt points to its successor, whose qualifying outcome is required before external fulfillment completes. Search never closes Privacy/Moderation's own workflow.

Start reconciliation/maintenance through authorized bounded manual commands; automatic cadence is versioned operational configuration added only with run budgets/coverage evidence. No periodic AI reclassification, end-user notification, query-history analytics store or speculative provider callback is implied. Per-action request/backfill/model cost limits use SH-132 and shared execution with explicit configured budgets and fail posture; never substitute Track commercial metering. No intrinsic Taxonomy cron or extra business-run table is required for normal maintenance. Operational telemetry is minimized and separate from domain completion evidence. Legal retention for subject-linked work/access receipts and actual provider configuration remain external requirements.

Required implementation checks: delayed stale upsert after deletion, provider write uncertainty, current-source denial at query time, protected collection isolation/totals, audit failure, incomplete enumeration, interrupted generation cutover, duplicate refresh, superseded removal receipt and consumer completion correlation. These contracts require adapter and bilateral fixture evidence before parallel-interface promotion; this architecture pass does not execute provider/schema/runtime tests.

## WA-R038 — Trust evidence provenance and screening boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

VerificationConsent remains a screening-context linkage: canonical ConsentLogId, identified User/subject, check type, provider, purpose, requirement/package revision and linked check. Generic acceptedAt/IP/user-agent fields are compatibility evidence only and cannot independently validate consent. New linkage requires canonical consent proof and current applicability checks; migration preserves unknown provenance without inventing consent. Each check has exactly one typed subject consistent with its User and optional Professional/Candidate profile; employer-requested screening additionally requires identified Organization/requester membership, Job/Application context, purpose and approved permissible-purpose evidence. Employer sponsorship is not activated by this technical representation.

Adopt the existing minimum Trust §9 check/package/badge graphs. Terminal checks never reopen; recheck is a new linked attempt with current consent/payment/requirement proof. License credential identity stays stable, but every verification/refresh/revocation creates an immutable evidence revision linked explicitly to its establishing VerificationCheck or authorized manual evidence decision. Current credential projection points to a valid revision; expired/revoked proof is never silently overwritten. Trust owns explicit check/credential-to-Media evidence join records, document kind, evidence revision and retention classification. Media owns bytes/scanning/access. No generic Media ownerType/ownerId joins are introduced.

Trust owns append-only check, credential, package/requirement and badge lifecycle histories with aggregate revision and source evidence, committed with outbox. Its provider effect receipt uses provider/account/eventId/handlerVersion uniqueness, fingerprint, check/credential target, normalized event kind, receivedAt, processing and attempt/recovery status, committed transition/effect refs. Unknown subject/events are quarantined; provider callbacks cannot mark a check passed from an unrecognized state. Short-lived provider report access is fetched on demand through an authorized adapter where supported. If persistence is necessary, reportToken is envelope-encrypted secret material with expiry/key version/rotation and restricted audited access; never public DTO/log/Search. Exact provider capability and retention remain external activation evidence.

Requirement rules are immutable schema-versioned records keyed to supported action, typed subject/target, jurisdiction and accepted classification revision; no free-form JSON policy or new implicit mandatory screening. Supported action vocabulary includes profile activation/publication, Offering publication, Gig response/acceptance, Order participation, Booking participation, Job application and Interview participation only where an explicitly approved requirement policy applies. Optional self-initiated Candidate/Professional screening remains optional; action enum presence does not mandate it. Single provider per package at launch; mixed-provider packages are deferred. Provider selection/check-type/jurisdiction rollout must be evidenced before activation, not inferred from a vendor enum.

Identity checks establish only their named verified identity claim; financial readiness stays Payment-owned; a healthcare credential check establishes that credential only, never BAA or Healthcare lane clearance. Broad platform_verified/gold_trust_check/healthcare_verified badges have no launch issuance or authorization effect without explicit scoped claim definitions; preserve legacy facts without minting misleading composite assurance. Public badge DTOs contain the approved claim label/type, subject profile reference, validity and evidence revision only. A badge never replaces current owner readiness.

FCRA technical evidence must link immutable notice template/version/content hash, identified recipient, approved purpose/check/report revision, delivery attempt and verified delivery outcome, policy/jurisdiction version, legally determined timing anchors, dispute submissions and outcome, final-action authorization and history. Notification delivery receipt is evidence, not a legal conclusion. Exact notice content, channels, required waits, adverse-action transitions and retention remain EXTERNAL_REQUIREMENT; no numeric windows or automated adverse decisions are approved here. Required tests cover consent-link mismatch, recheck history, expired supporting evidence, duplicate/late callback, secret exclusion and subject-context mismatch.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P17

Candidate discovery/search participation is explicit opt-in and off by default. Persist the Candidate-owned participation choice with version, actor and time; no default database visibility boolean or JobApplication submission implies opt-in. Application workflow can expose the Candidate/application to that specific authorized hiring Organization independently of general discovery.

Disabling discovery invalidates future candidate-search exposure immediately at the authoritative query boundary and requests removal through Search/privacy contracts with durable completion evidence. Delayed provider deletion cannot authorize stale result disclosure. Opt-out preserves valid JobApplications and authorized hiring history under their owners. It grants no raw-resume access and does not enable anonymous Candidate indexing.


### P18

Do not automatically expire interview invitations by timer at launch. Organizers cancel, replace or reschedule through Job Interview lifecycle with immutable history. Invitation pending state alone does not prove a currently actionable slot: every new acceptance validates the current invitation/revision and server-authoritative scheduling facts. An already-elapsed interview slot cannot be newly accepted; present a stale-slot outcome and require authorized replacement/rescheduling. This validity check is not an automatic expiration transition and does not invent a deadline. Preserve existing response and schedule history; no_response is not proof of recipient reading.

## WA-R043–047 — Reconciled CL-06 sequence

Apply owner architecture before implementation: membership/history and current source revisions → immutable Compliance evaluation/review and Hiring publication → Candidate application/participation/access evidence → Interview participants and schedule successors → bilateral provider/Search/Moderation/Privacy qualification. Candidate state and interviewability queries precede Interview integration; current Hiring/Role facts precede all recruiter actions. Freeze event names and test retry/revocation with owners before consumer work. No launch expiry worker; no direct terminal reopen or application transition inferred from Interview. Legal/provider/retention and coordinated database gates remain active.


## WA-R066 — Finite Notification source and recipient contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-041 uses the following finite versioned semantic-intent/template registrations. These are architecture contracts, not implemented renderers, selected delivery vendors or proof of delivery. Sources emit an intent only after the corresponding durable owner transition. Every intent binds source owner, typed aggregate ID/revision, immutable semantic intent ID, template key/version, owner-resolved local User recipients, safe authenticated route, sensitivity and event kind. Notification owns channel consent, current endpoint generation, eligible delivery, attempts and receipts. Sources never ask Notification to scan foreign memberships or reconstruct business state.

| Intent/template | Committed source and recipients | Safe additional content |
| --- | --- | --- |
| message.new.v1 | Messaging messaging.message_created.v1; other currently eligible Thread participants selected by Messaging, excluding sender | Thread/Message references only; no message body or attachment URL |
| order.outcome.v1 | Order order.outcome_changed.v1; currently authorized Order participants selected by Order for its source kind | Safe operational outcome code and Order link; no financial consequence implied |
| booking.schedule.v1 | Booking confirmed/rescheduled/cancelled facts; currently authorized affected Booking participants | Safe change kind and authenticated schedule link; no exact address or meeting credential |
| interview.invitation.v1 | Interview invitation/current schedule revision; invited eligible Candidate and authorized Organization participants selected by Interview | Interview reference and safe proposed/scheduled kind |
| interview.schedule.v1 | Interview cancellation/reschedule/replacement; currently authorized affected participants selected by Interview | Safe change kind and authorized predecessor/successor references; no new removed-user notice |
| application.status.v1 | Candidate accepted_offer or withdrawn: current authorized hiring Organization recipients selected by Candidate through Hiring facts; Candidate rejected or hired: the application Candidate User | Application reference and exactly accepted_offer/withdrawn/rejected/hired change code; no view/stage alert or general Candidate exposure |
| privacy.verification_needed.v1 | Privacy durable request transition requiring verification; request subject through Privacy/Identity-authorized route | Request reference and safe action-needed code; no verification secret |
| privacy.outcome.v1 | Privacy accounted terminal outcome; currently authorized request subject/representative | Safe terminal category and link; no restricted exemption evidence or other parties' data |
| privacy.export_ready.v1 | Privacy complete manifest and ready exact Media version/current generation; currently authorized export requester | Request/bundle reference; no signed credential or stored public URL |
| security.notice.v1 | Identity committed security intent; affected local User only | Generic change and authenticated-context link; no OTP, recovery token, precise IP or factor details |
| supply.status.v1 | Professional/Marketplace committed status/remediation intent under R035; owner-resolved Professional User | Generic status/remediation code; no Healthcare/provider/Hold detail |

Candidate registers `candidate.application_status_changed.v1` with eventId, application ID/revision, committed time, semantic command identity, old/new status, authorized actor reference and safe typed Candidate/Organization subject references. This event contains no resume, message, employer notes or protected evidence. The source owner derives notification recipients from current Hiring authority. Only the four listed successful status transitions may create application.status.v1 at launch; application views, recruiter stages and retry transport do not. Candidate acceptance must already satisfy R045 current-offer proof, and withdrawal does not restore quota. Sending a notification never makes an application or Candidate publicly discoverable.

Deduplicate one semantic intent × resolved User; channel attempts are children of that intent. Changed payload under the same fingerprint conflicts. Retries preserve identity. Current protected-context access is rechecked before rendering/dereference; loss of membership suppresses the protected notice. Do not create a removed-user notice without its own approved source policy. Delayed invitation links must recheck P18/current schedule. Notification failure never rolls back source truth. No message bodies, resumes, exact locations, raw provider failures, adjudication evidence or credentials may enter generic variables.

Material proposal changes remain visibly surfaced by Gig's current-revision presentation under P14; a delivered notice is not evidence the latest terms were presented for acceptance. Participant-facing Dispute updates reuse Order conversation under P19, but a Review fact cannot be relabeled as an Order event; any separate Review alert remains disabled until registered. Optional viewed/shortlisted, Location, Interview completion/no-show and other undeclared alerts remain disabled. This finite registration does not provide legally sufficient notice policy. Exact copy, renderer/schema fixtures, provider/account/channel qualification and delivery recovery proof remain activation prerequisites. Existing broad notification suggestions are narrowed by this explicit source/recipient matrix for these intents.

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Hiring and Candidate expose distinct minimized purpose-approved AI source descriptors, stable owner enumeration and atomic contextual assignment receipts; P17 opt-in is not AI-purpose consent. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## WA-R071 — Purpose-specific Location facts and disclosure — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Hiring public geography consumes approved coarse Location fields; Interview meetingLocation/meetingPhone use a distinct participant-purpose policy and durable proof. Recruitment role is not blanket exact access. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## WA-R072 — Hiring compatibility and forward migration stewardship — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Hiring owns JobMedia and Organization/Job history; Candidate owns contextual media joins and application view/access history; Interview owns participants and invitation/response history. Additive/backfill/parity/removal sequence requires proven original identities and preserves history; database D gates activation. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## WA-R073 — Interview access interval and bounded credentials — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Invitation acceptance requires future startsAt under P18; joining accepted current interviews requires startsAt <= serverNow < endsAt. No timer expiry or implicit pre/post grace; new timing policy can change future behavior without rewriting history. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.
