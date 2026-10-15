# Candidate Application & Resume Privacy Module Implementation Plan

> **Module ID:** `candidate_application_resume_privacy`  
> **Module:** Candidate Application & Resume Privacy Module  
> **Primary Cluster:** `CL-06 Organization Hiring & Candidate Pipeline`  
> **Repository target:** `context/clusters/Organization Hiring & Candidate Pipeline/Candidate Application & Resume Privacy Module/candidate-application-resume-privacy-module-implementation-plan.md`\
> **Authority:** this Module `module-architecture.md`, CL-06 `architecture.md`, and CL-06 `build-plan.md`  
> **Implementation posture:** greenfield/MVP implementation planning against current Workin Ants schema and architecture evidence; unresolved architecture remains disabled or blocked rather than guessed

---

## Core Principle

Implement this Module through narrow, verifiable owner slices:

```text
public / observable behavior
→ runtime-validated command or query
→ Candidate Application-owned policy
→ authoritative Candidate-owned write/read
→ canonical shared-operation calls
→ versioned outbox / audit / notification / search effects
→ contract + domain + integration tests
→ explicit exit gate
```

The Module plan is subordinate to the CL-06 Cluster build plan. It may split a Cluster feature into smaller Candidate-owned implementation slices, but it may not move Cluster sequencing, absorb another Module’s work, or redefine source-of-truth ownership.

A slice with no UI must still leave a concrete observable result: a stable public contract, durable owner record, worker result, projection, privacy execution result, or integration proof.

---

## Build Rules

The [Shared Operations registry](../../../shared/shared-operations.md) governs permanent IDs, canonical names, owners, classifications and statuses. Registered use points below carry verified IDs/statuses. Proposed ruling entries may support planning and owner-specific interfaces/mechanisms, but cross-platform SH API/schema commitment requires separate explicit approval; any exit gate relying on that shared API must verify approval. Unresolved entries must not be silently implemented or replaced locally. The approved Job Compliance publication envelope does not approve a proposed shared decision envelope.

1. Follow root Workin Ants architecture/code standards, Canonical Shared Operations, CL-06 architecture/build plan, and this Module architecture.
2. Implement only Candidate Application & Resume Privacy truth declared by `module-architecture.md`.
3. Consume neighboring Modules through approved public interfaces/events or versioned fixtures; direct cross-domain repository access is not the default.
4. Reuse canonical shared operations. If a required canonical operation is missing, fix/implement it in its canonical owner rather than creating a Candidate-local copy.
5. Every mutation is runtime-validated, authenticated, authorized, and transaction-safe.
6. Every application/resume read validates complete relationship context; IDs alone never prove permission.
7. Lifecycle transitions are performed by this Module’s owner service only.
8. Slow/retryable work uses shared durable queue/retry/dead-letter infrastructure.
9. External effects occur after authoritative source writes and are idempotent/replay-safe.
10. Media, Search, Notification, Messaging, Audit, Privacy, Track, Trust, and Holds retain their source truth.
11. No permanent public resume URL may be introduced.
12. Resume parsing is extraction only; automated hiring recommendation/ranking/rejection is out of scope.
13. Raw resume text is excluded from Search/logs/analytics by default.
14. Application quota/boost/view perks stay Track-owned.
15. Verified-only readiness stays Trust-owned.
16. `ResumeAccessLog`, `MediaAccessEvent`, and `AccessAuditLog` stay separate.
17. Search remains projection; `CandidateSearchProjection` is Candidate-owned source input, Typesense/SearchUpsertEvent are Search-owned.
18. Privacy / Data Erasure owns privacy-request orchestration and exemptions; this Module only enumerates/executes against Candidate-owned data.
19. No unresolved `U-CL06-*` or `U-CARP-*` issue may be silently resolved by implementation.
20. Every numbered feature ends with tests, documentation/progress updates, and a hard exit gate.
21. A failed exit gate stops sequential execution until fixed or architecture/build plan is explicitly revised.

---

## Preconditions

### Hard platform prerequisites

The following must exist before any production Candidate feature is enabled:

- authenticated actor context / SH-001 `resolveAuthenticatedActor` (Confirmed);
- Role / Authority decision interface / SH-002 `authorizeResourceAction` (Confirmed);
- Prisma migration/transaction layer;
- runtime validation standard;
- canonical idempotency primitive;
- aggregate locking / optimistic concurrency primitive;
- transactional outbox/inbox;
- reliable queue/retry/dead-letter infrastructure;
- structured logging/request/correlation IDs;
- Audit API including SH-030 `recordSensitiveAccess` (Confirmed);
- RLS infrastructure and policy-test harness.

### Hard cross-Module interfaces by feature

| Dependency | Required for |
|---|---|
| Organization Hiring owner facts / Job eligibility context | application submission, recruiter reads, resume authorization |
| Organization Hiring application-eligibility context | normal production submission; no direct Candidate → Job Compliance evaluation/read |
| Track SH-005 `resolveEntitlement` (Confirmed) + SH-006 `consumeMeteredEntitlement` (Confirmed) | Feature 05 application quota, Feature 09 perks |
| Trust requirement/readiness API | verified-only application gates |
| ComplianceHold evaluation | application/transition/access gates as approved |
| Media validation/scan/attach/grant/signed URL APIs | Features 02–04 and 08 |
| Search projection refresh/removal contract | Feature 09, privacy integration |
| Notification request contract | application lifecycle effects |
| Messaging SH-113 `ensureContextThread` (Confirmed) | optional application conversation effect |
| Privacy target protocol | Feature 11 |
| Job Interview application-context contract | Feature 10 integration handoff |

### Interfaces that may be contract-stubbed initially

Before the corresponding integration feature, a neighboring owner may be represented by a versioned test fixture if its production implementation does not yet exist. The fixture must match the approved public contract and may not become a Candidate-local substitute implementation.

### Architecture blockers

Production implementation must respect these blockers:

- **U-CL06-08:** CandidateCategory/CandidateTag attach/detach persistence owner.
- **U-CL06-09:** Candidate field non-authority is binding; only later cleanup/deprecation remains undecided.
- **U-CL06-10:** candidate visibility/search participation.
- **U-CL06-11:** JobApplication transition/event semantics.
- **U-CL06-12:** JobApplicationViewEvent/view-summary semantics.
- **U-CL06-13:** ResumeAccessLog semantics and raw extracted-text retention/encryption.
- U-CL06-17's placement claim is retired; R008's semantic relation discrepancy and the project migration-baseline question remain separate.
- **U-CL06-04:** Organization ATS commercial entitlement if monetized applicant tracker/resume viewer/candidate search is enabled.
- **U-CARP-01:** CandidateSearchProjection cardinality/versioning.
- **U-CARP-02:** parse retry provenance.
- **U-CARP-03:** candidate/application media-role vocabulary.

A feature may implement safe non-production scaffolding around an unresolved area only when the behavior remains disabled/fail-closed and the unresolved question is not encoded as de facto policy.

---

**Approved execution order (CL-06-R006):** retain feature IDs but execute 01 → 02 → 05 → 03 → 04 → 06 onward. Application creation and its matching application-media link precede parse requests and worker execution. Upload alone never creates ResumeParseResult.

### Public concurrency prerequisite — CL-06-R020

Public mutation contracts use an owner-issued opaque `expectedConcurrencyToken`. The owner returns the token, atomically compares it through SH-052 `withOptimisticConcurrency` (Confirmed), and rejects stale tokens. Consumers do not assume a universal integer `version` or `updatedAt` field. JobApplication, mutable Job Compliance finding/review, JobInterview and any parent-versus-child token backing remain unresolved where no representation is approved; no version column is ordered here.

# Phase 1 — Contract and Source-of-Truth Foundation

## 01 Candidate Module Contracts and Schema Integrity

### Objective

Establish the Candidate Application module boundary in code, stabilize owner-specific public contracts, and make the current Candidate-related Prisma schema structurally valid without silently resolving business-semantic blockers.

### Observable Result

The codebase has a Candidate Application module shell with public command/query/event/privacy contracts, runtime schemas, owner repositories limited to Candidate-owned records, and a Prisma schema that parses/migrates cleanly around `JobApplication` and `JobApplicationViewEvent` without assuming the retired U-CL06-17 placement defect; overall validation and the project migration baseline still require evidence.

### Cluster Build-Plan Link

Preparatory slice for CL-06 Phase 2 Features **04–08**; checks current schema evidence independently of the retired U-CL06-17 claim; R008 and the project migration baseline are separate database-pass prerequisites.

### Dependencies

- root module/folder conventions;
- runtime validation standard;
- Prisma migration tooling;
- canonical shared operation contracts;
- CL-06 public-interface table;
- current schema validation evidence; no obsolete U-CL06-17 relation-placement repair;

### In Scope

- create the Module folder structure required by `module-architecture.md`;
- define public DTOs for CandidateProfile, JobApplication, resume access, projection, view insights, and privacy executor;
- define public command/query names without implementing all business behavior yet;
- define owner repository interfaces that access only Candidate-owned tables;
- verify current schema without moving relation lines on the basis of retired U-CL06-17; flag the R008 many-to-many relation for a later approved schema pass;
- add schema parsing/migration tests;
- isolate/mark non-authoritative fields (`resumeUrl`, verification-looking fields) in code so no feature uses them as source truth; CL-06-R010 confirms their non-authority;
- preserve unresolved CandidateCategory/Tag write placement rather than creating a repository for them.

### Out of Scope

- CandidateProfile user-facing behavior;
- resume upload/parsing;
- application submission;
- final JobApplication transition matrix;
- candidate search activation;
- deciding U-CL06-09/10/11/12/13/08 or U-CARP-01/02/03.

### Module-Owned Data

- `CandidateProfile` mapping;
- `CandidateProfileMedia` mapping;
- `JobApplication` mapping;
- `JobApplicationMedia` mapping;
- `ResumeParseResult` mapping;
- `ResumeAccessLog` mapping;
- `CandidateSearchProjection` mapping;
- Candidate-owned `JobApplicationViewEvent` with at most one Organization context; do not activate unresolved U-CL06-12 view-summary semantics or use the extra many-to-many relation as truth;

### Public Interfaces

Introduce type-level contracts for:

```text
createCandidateProfile
updateCandidateProfile
transitionCandidateProfileStatus
attachCandidateProfileMedia
attachApplicationMedia
evaluateApplicationEligibility
submitJobApplication
withdrawJobApplication
listCandidateApplications
listJobApplicants
getJobApplicationDetail
transitionApplicationStage
transitionApplicationStatus
authorizeContextualResumeAccess
requestResumeAccessGrant
getResumeParseResult
getCandidateSearchProjection
getApplicationViewInsights
getApplicationInterviewContext
SH-096 enumerateSubjectData (Confirmed)
SH-095 executePrivacyInstruction (Confirmed)
```

No consumer is allowed to import Candidate repositories instead of these contracts.

### Shared Operations Used

- SH-044 `executeIdempotentCommand` (Confirmed) — canonical owner: platform application infrastructure; used for future command contract shape. Do not create `candidateIdempotency.ts`.
- SH-052 `withOptimisticConcurrency` (Confirmed) — canonical owner: shared persistence; establish owner-issued opaque expected-concurrency-token DTO pattern. Do not hand-roll stale-update logic.
- SH-046 `publishDomainEvent` (Confirmed) — canonical owner: platform outbox; establish event envelope types. Do not implement fire-and-forget local events.
- SH-015 `returnDecisionResult` (Proposed ruling) — Proposed shared contract; define compatibility only, do not treat its policy as approved generic readiness truth.

### Domain Logic

- no business transition logic beyond confirmed schema invariants;
- mark CandidateProfile `resumeUrl`, `trustScore`, `verifiedAt`, and `verificationExpiresAt` as forbidden authority fields in services;
- enforce one owner-repository boundary;
- define CandidateProfile→User and JobApplication→CandidateProfile/Job relationship DTOs.

### Authorization / Compliance

No end-user behavior is enabled. Public contracts include actor/action context so later implementations cannot omit authentication/authorization.

### Database / Transaction Behavior

- verify current schema parsing without assuming the retired U-CL06-17 relation-placement defect;
- preserve `CandidateProfile.userId @unique`;
- preserve `JobApplication @@unique([jobId,candidateProfileId])`;
- preserve media composite keys and ResumeParseResult uniqueness;
- do not add CandidateSearchProjection uniqueness until U-CARP-01 is resolved;
- do not add taxonomy-join write constraints that assume U-CL06-08.

### Events / Jobs

Define versioned event schemas/envelopes only; no worker behavior yet.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

- an actual schema-validation failure → report the observed defect and block affected migration generation; do not assume retired U-CL06-17 is the cause;
- ambiguous ownership → no code path created;
- contract incompatibility with existing root standards → update context before implementation.

### Tests

- Prisma schema parse/generate/migration dry-run;
- repository ownership lint/import tests if supported;
- public DTO runtime-schema tests;
- no forbidden direct field used as verification/resume authority;
- no cross-module repository import in Candidate module.

### Documentation Updates

- retain the retired U-CL06-17 status and update architecture only when remaining schema/field semantics are formally settled;
- record any new public contract naming decision;
- update progress tracker.

### Acceptance Criteria

- Candidate-related Prisma relations are syntactically/structurally valid;
- all Candidate repositories are owner-local;
- no direct cross-domain write path exists;
- unresolved fields are fenced from authority logic;
- public contracts compile and validate.

### Exit Gate

PASS only if Prisma generation/migration rehearsal succeeds for the relevant current schema, without assuming a U-CL06-17 repair, public contracts/runtime schemas compile, no unresolved business ruling was encoded, no cross-domain repository shortcut exists, and typecheck/lint/unit/schema checks pass.

---

# Phase 2 — Candidate Identity and Secure Resume Intake

## 02 CandidateProfile Lifecycle and Candidate-Owned Media Context

### Objective

Allow an authenticated User to create and update CandidateProfile applicant identity and attach validated private candidate media without treating legacy resume/verification fields as source truth.

### Observable Result

A User can create one CandidateProfile, edit allowed profile fields, view the profile, and attach/detach approved MediaAssets through Media-owned validation; unauthorized users cannot access or mutate another candidate’s private profile/media.

### Cluster Build-Plan Link

Supports CL-06 Feature **04 CandidateProfile and Secure Resume Intake**.

### Dependencies

- Feature 01;
- SH-001 `resolveAuthenticatedActor` (Confirmed);
- SH-002 `authorizeResourceAction` (Confirmed) / candidate ownership policy;
- Media SH-082 `validateUploadedFile` (Confirmed), SH-083 `scanFileForMalware` (Confirmed), SH-090 `attachValidatedMedia` (Confirmed) contracts;
- enforce confirmed non-authority of resumeUrl/local verification fields; later cleanup/deprecation remains unresolved;
- U-CARP-03 resolved before ad hoc media-role strings become production API vocabulary.

### In Scope

- `createCandidateProfile`;
- `getCandidateProfile`;
- `updateCandidateProfile`;
- candidate-specific ProfileStatus handling only for approved transitions;
- candidate media attachment/detachment context;
- candidate ownership authorization;
- privacy-shaped candidate DTOs;
- profile UI and candidate media status presentation.

### Out of Scope

- application submission;
- resume parsing;
- recruiter access;
- candidate search;
- verification logic;
- taxonomy attach/detach until U-CL06-08 write owner is settled.

### Module-Owned Data

- `CandidateProfile`;
- `CandidateProfileMedia`;
- candidate use of `ProfileStatus`.

### Public Interfaces

- `createCandidateProfile`;
- `getCandidateProfile`;
- `updateCandidateProfile`;
- `transitionCandidateProfileStatus` only for the approved subset;
- `attachCandidateProfileMedia`;
- `detachCandidateProfileMedia` if approved by root command naming.

### Shared Operations Used

CandidateProfile creation uses SH-114 `provisionOneToOneProfile` (Confirmed) for idempotent one-to-one provisioning; Candidate owns opt-in/defaults and lifecycle.

- SH-001 `resolveAuthenticatedActor` (Confirmed) — Identity; resolve User actor. Local policy: CandidateProfile belongs to that User. Prohibited duplicate: `currentCandidateUser.ts`.
- SH-002 `authorizeResourceAction` (Confirmed) — Role / Authority; authorize profile actions. Local policy: ownership/resource facts. Prohibited duplicate: local generic permission engine.
- SH-044 `executeIdempotentCommand` (Confirmed) — platform; CandidateProfile creation and media attach commands. Local policy: semantic command key. Prohibited duplicate: local idempotency table.
- SH-052 `withOptimisticConcurrency` (Confirmed) — shared persistence; profile edits. Local policy: stale edit behavior.
- SH-082 `validateUploadedFile` (Confirmed) / SH-083 `scanFileForMalware` (Confirmed) — Media; file safety. Local policy: whether the validated asset may be used as candidate media. Prohibited duplicate: resume/file validator.
- SH-090 `attachValidatedMedia` (Confirmed) — context owner + Media contract; persist CandidateProfileMedia after ready/valid result. Prohibited duplicate: direct storage/object mutation.
- SH-046 `publishDomainEvent` (Confirmed) — outbox; profile/media change events. Local policy: event meaning/payload.

### Domain Logic

- one User can have at most one CandidateProfile under current schema;
- CandidateProfile is applicant identity and never inherits ProfessionalProfile verification truth;
- profile actions require candidate ownership except explicit admin/support policy;
- `resumeUrl` is not used as canonical attachment/access;
- `trustScore`, `verifiedAt`, `verificationExpiresAt` do not authorize anything;
- candidate media attachment requires an approved MediaAsset state and context;
- profile status transitions use only architecture-approved graph; unapproved transition returns deterministic denial.

### Authorization / Compliance

- authenticated actor required;
- server ownership check required;
- RLS/server parity required;
- private media remains private;
- no step-up requirement is invented unless root security policy binds one for specific admin/destructive actions.

### Database / Transaction Behavior

- CandidateProfile create uses unique `userId` and idempotency;
- profile updates use optimistic concurrency;
- CandidateProfileMedia composite key makes duplicate attachment deterministic;
- profile write + outbox occur transactionally where supported.

### Events / Jobs

Emit minimized events such as:

```text
candidate_profile.created
candidate_profile.updated
candidate_profile.status_changed
candidate_profile.media_attached
candidate_profile.media_detached
```

No background job required yet.

### Provider Integration

None. Media provider/storage is external to this Module.

### UI / Admin Surface

- CandidateProfile create/edit/read;
- private candidate document/media attachment status;
- no public resume URL;
- do not display verification badges based on local CandidateProfile fields.

### Failure Behavior

- duplicate profile → deterministic conflict/existing result per idempotency contract;
- unauthorized actor → no write;
- stale edit → conflict with current version;
- Media not ready/clean/allowed → attachment denied;
- Media dependency unavailable → explicit unavailable/retry, no local storage fallback.

### Tests

- CandidateProfile create/update ownership;
- unique User→CandidateProfile;
- stale profile edit;
- Media attach/detach composite-key behavior;
- private asset behavior;
- forbidden use of resumeUrl/verification-looking fields;
- RLS/server parity;
- component/E2E profile flow.

### Documentation Updates

If the remaining U-CL06-09 cleanup/deprecation question or CandidateProfile transition policy is resolved during this feature, update `module-architecture.md` first and record migration/deprecation behavior. CL-06-R010's field non-authority is already binding.

### Acceptance Criteria

- CandidateProfile works as applicant identity;
- one User cannot create duplicate profiles;
- private Media attaches only through Media contract;
- no legacy field authorizes resume/verification behavior;
- unauthorized cross-user access fails.

### Exit Gate

PASS only if candidate identity and private media-context workflows work end-to-end, RLS/server authorization agree, no public resume URL is introduced, no verification truth is duplicated, and typecheck/lint/unit/integration/authorization/E2E checks pass.

---

# Phase 3 — Application Submission, Post-Submission Parsing, and Candidate Self-Service

## 05 Atomic Application Eligibility and Submission

### Objective

Allow a CandidateProfile to submit exactly one application to an eligible Job without exceeding Track application limits under concurrent/retried requests.

### Observable Result

The apply flow returns a stable eligibility decision, creates one `JobApplication(status=submitted, stage=new_)` only when all gates pass, consumes the Track allowance exactly once for the logical submission, and produces a durable receipt/event.

### Cluster Build-Plan Link

Implements the Candidate-owned core of CL-06 Feature **05 Atomic Application Eligibility, Quota, and Submission**.

### Dependencies

- Features 01–02; parsing Features 03–04 are downstream and are not prerequisites for submission;
- Organization Hiring `getJobApplicationEligibilityContext`;
- Track SH-005 `resolveEntitlement` (Confirmed) + SH-006 `consumeMeteredEntitlement` (Confirmed);
- Trust SH-017 `resolveVerificationRequirements` (Confirmed) + SH-018 `evaluateVerificationReadiness` (Confirmed);
- SH-011 `evaluateComplianceHold` (Confirmed);
- Media attachment readiness;
- U-CL06-11 sufficient to confirm creation/withdraw semantics;
- approved race-safe cross-owner application/Track usage protocol.

### In Scope

- `evaluateApplicationEligibility`;
- `submitJobApplication`;
- application form/receipt;
- duplicate prevention;
- Track usage consumption/reconciliation;
- verified-only gate;
- Hold gate;
- validated attachment links;
- application submitted event;
- Notification request;
- optional Messaging thread request if Cluster workflow enables it.

### Out of Scope

- recruiter pipeline transitions;
- application view events;
- resume viewing;
- candidate search;
- interview creation.

### Module-Owned Data

- `JobApplication`;
- `JobApplicationMedia` relations included in submission only when already validated/approved;
- local outbox facts.

### Public Interfaces

- `evaluateApplicationEligibility`;
- `submitJobApplication`;
- `listCandidateApplications`.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` (Confirmed) — candidate actor.
- SH-002 `authorizeResourceAction` (Confirmed) — candidate owns CandidateProfile/action.
- SH-011 `evaluateComplianceHold` (Confirmed) — stop-sign decision; no local blocked flag.
- SH-005 `resolveEntitlement` (Confirmed) — inspect application allowance.
- SH-006 `consumeMeteredEntitlement` (Confirmed) — atomically consume allowed quantity/usage receipt.
- SH-017 `resolveVerificationRequirements` (Confirmed) / SH-018 `evaluateVerificationReadiness` (Confirmed) — verified-only gate.
- SH-044 `executeIdempotentCommand` (Confirmed) — logical submission identity.
- SH-051 `acquireAggregateLock` (Confirmed) / transaction primitive — application/quota race.
- SH-046 `publishDomainEvent` (Confirmed) — `application.submitted`.
- SH-041 `requestNotification` (Confirmed) — downstream delivery.
- SH-113 `ensureContextThread` (Confirmed) — optional Messaging handoff, never local Thread write.

### Domain Logic

A submission is allowed only if all approved conditions pass:

```text
CandidateProfile usable
AND Job is accepting applications according to Organization Hiring facts
AND no duplicate JobApplication
AND applicable ComplianceHold does not block
AND Track application allowance can be consumed
AND verified-only requirements pass when applicable
AND required attachments are ready/clean
AND request is valid and authorized
```

Normal submission does not independently read or reevaluate Job Compliance. `getJobApplicationEligibilityContext` fails closed unless current authoritative Job state permits applications; later Compliance decisions are applied by Organization Hiring and Candidate consumes Job owner state/events. A future direct dependency needs an explicit new Cluster policy.

The Module defines the business point at which the application counts for Track usage. Track owns the usage event/counter itself.

### Authorization / Compliance

- candidate actor must own CandidateProfile;
- verified-only status comes from Trust, not CandidateProfile fields;
- no local plan/premium flag;
- dependency unavailable fails closed/unavailable rather than bypassing quota/verification.

### Database / Transaction Behavior

- unique `(jobId,candidateProfileId)` is the final duplicate guard;
- semantic idempotency key binds the logical application and Track consume operation;
- if root architecture permits one transaction across owner services, use it only through approved owner participation; otherwise persist/reconcile explicit saga state/result without direct Track table writes;
- local JobApplication/outbox commit is atomic;
- duplicate retry returns prior result/receipt.

### Events / Jobs

- `application.submitted` outbox event;
- Notification/Messaging consumers dedupe;
- reconciliation job only if cross-owner Track/application outcome can be partial.

### Provider Integration

None.

### UI / Admin Surface

- apply form;
- allow/deny/remediation reasons;
- remaining quota if Track contract permits display;
- success receipt/application list.

### Failure Behavior

- validation → no write;
- unauthorized → no write;
- duplicate → existing application/conflict per command semantics;
- quota exhausted → no application;
- Trust/Hold denial → no application;
- Track unavailable → no permissive application;
- partial Track/application outcome → explicit reconciliation path, never silent double-charge/double-consume.

### Tests

- eligibility policy matrix;
- Organization Job-state contract;
- Track allowance/consume contract;
- verified-only Trust contract;
- Hold denial;
- simultaneous duplicate submissions;
- quota boundary concurrency;
- idempotency replay;
- partial cross-owner reconciliation;
- E2E apply flow.

### Documentation Updates

If the cross-owner atomic protocol settles a binding rule, record it in Module architecture and Track/Candidate public contracts.

### Acceptance Criteria

One logical submission creates one JobApplication and one qualifying Track usage receipt at most; all gates are server-side and cannot be bypassed.

### Exit Gate

PASS only if duplicate application and quota overrun are impossible under concurrency/replay, Trust/Hold/Track unavailability cannot bypass gates, application/usage reconciliation is tested, and full unit/integration/contract/E2E checks pass.

---

## 03 Secure Resume Attachment and Parse Request

### Objective

Allow a CandidateProfile/application context to attach a Media-owned private resume/CV and create one durable parse request only after the asset is ready and scan-clean.

### Observable Result

A PDF/DOCX resume uploaded under an approved resume context can be attached and moved to `ResumeParseResult.status=pending`; invalid, non-ready, suspicious, infected, or cross-owned media cannot enter the parse workflow.

### Cluster Build-Plan Link

Supports the post-submission parsing stage of CL-06 Feature **05 Atomic Application Eligibility, Quota, and Submission**, after Module Feature 05 has created the application and matching application-media relationship.

### Dependencies

- Features 01–02 and 05; the JobApplication and matching JobApplicationMedia must exist before parse creation;
- Media upload policy for `candidate_resume` / `candidate_cv`;
- Media readiness/scan query;
- shared queue/idempotency;
- U-CARP-03 if local role vocabulary is exposed.

### In Scope

- `attachApplicationMedia` for resume/CV context;
- Media readiness/scan gating;
- `queueResumeParse` command;
- create/find `ResumeParseResult` for unique application/media pair when JobApplication exists; where candidate-profile-only resume parsing is required before application, do not invent a new schema relation—keep parsing scoped to schema-supported application/media until architecture adds another truth;
- parse-request outbox/job dispatch;
- UI parse-request/status indicator after an application context exists.

### Out of Scope

- parser execution;
- application submission creation if JobApplication does not yet exist;
- new CandidateProfile-level ResumeParseResult schema;
- resume access by recruiters;
- Search.

### Module-Owned Data

- `JobApplicationMedia`;
- `ResumeParseResult` pending state.

### Public Interfaces

- `attachApplicationMedia`;
- `queueResumeParse`;
- `getResumeParseResult`.

### Shared Operations Used

- Media SH-082 `validateUploadedFile` (Confirmed), SH-083 `scanFileForMalware` (Confirmed), SH-090 `attachValidatedMedia` (Confirmed) — verify file policy/safety; no local MIME/malware code.
- SH-044 `executeIdempotentCommand` (Confirmed) — one logical attach/parse request.
- SH-047 `enqueueReliableJob` (Confirmed) — durable parse job; no local queue framework.
- SH-046 `publishDomainEvent` (Confirmed) — `resume.parse_requested` after local record exists.

### Domain Logic

- resume/CV uses approved MediaUploadContext;
- current policy: max 5 MB, PDF/DOCX, server-side validation in Media;
- MediaAsset must be `ready` and scan `clean` before parse request;
- JobApplicationMedia must belong to the same JobApplication/media pair used by ResumeParseResult;
- one ResumeParseResult per `(jobApplicationId, mediaId)`;
- parse request creates no candidate recommendation or score;
- if schema-supported pre-application parsing is desired, architecture must change before coding it.

### Authorization / Compliance

Candidate owns application/profile context. Media safety is mandatory. File names/raw bytes are not logged.

### Database / Transaction Behavior

- insert JobApplicationMedia and ResumeParseResult under appropriate transaction boundaries;
- rely on composite PK and ResumeParseResult unique constraint for replay safety;
- outbox/job dispatch after durable local state;
- duplicate queue request returns existing parse record/job receipt.

### Events / Jobs

- emit `resume.parse_requested`;
- enqueue `resume-parse` job keyed by application/media/parser policy version.

### Provider Integration

None yet.

### UI / Admin Surface

- resume attachment state;
- parse status `pending`;
- safe retry affordance only when worker policy allows;
- no direct storage URL.

### Failure Behavior

- invalid format/size/malware → Media denial and no parse truth;
- media not ready → retryable/unavailable status, no parser job;
- duplicate attach/parse request → existing result;
- queue dispatch failure after source commit → outbox/reliable-job retry, source remains truthful.

### Tests

- PDF/DOCX accepted through Media fixture;
- wrong context/file-size/MIME/scan state denied;
- cross-owned application/media denied;
- one parse result per pair;
- duplicate request idempotent;
- no raw file/log leak;
- outbox/job durability.

### Documentation Updates

If a pre-application resume parse requirement is confirmed, update architecture/schema before adding it.

### Acceptance Criteria

A clean private resume can produce exactly one pending parse truth and durable job; unsafe/unready files cannot; no public URL or local file-safety implementation exists.

### Exit Gate

PASS only if ready+clean gating is enforced server-side, duplicate parse truth is impossible, queue dispatch is durable/idempotent, no local Media mechanism exists, and all integration/security tests pass.

---

## 04 Resume Parsing Worker and Non-Decisional Metadata

### Objective

Execute resume parsing durably and normalize extracted resume content into `ResumeParseResult` without turning parser output into hiring decisions.

### Observable Result

A pending parse job moves through processing to completed/failed/skipped as approved, records parser name/version and normalized metadata, never emits candidate ranking/recommendation, and exposes safe retry/operational failure behavior.

### Cluster Build-Plan Link

Completes the post-submission parsing stage of CL-06 Feature **05**, after Module Features 05 and 03.

### Dependencies

- Feature 03;
- Media internal file-access contract;
- shared queue/retry/Ops;
- `ResumeParserPort`;
- U-CL06-13 resolved before production retention of `extractedText`;
- U-CARP-02 resolved if owner-level parse attempt history is required.

### In Scope

- ResumeParserPort;
- PDF adapter using architecture-approved library (`pdf-parse` is current evidence);
- DOCX adapter with an implementation-selected library behind the same port;
- parse worker;
- parser status transitions;
- normalized skills/metadata extraction pass-through/normalization without recommendation;
- telemetry redaction;
- retry/dead-letter behavior;
- candidate-visible parse status.

### Out of Scope

- AI candidate scoring;
- candidate ranking;
- eligibility decision;
- verification extraction as source truth;
- Search indexing;
- external provider webhook lifecycle.

### Module-Owned Data

`ResumeParseResult`.

### Public Interfaces

- internal worker handler;
- `getResumeParseResult`;
- optional owner command `retryResumeParse` only if approved retry semantics are documented.

### Shared Operations Used

- SH-047 `enqueueReliableJob` (Confirmed) — durable worker;
- SH-048 `executeRetryWithBackoff` (Confirmed) — transient retries;
- SH-044 `executeIdempotentCommand` (Confirmed) — retry command if exposed;
- Ops logging/failure APIs — operational state only;
- SH-046 `publishDomainEvent` (Confirmed) — completed/failed facts.

### Domain Logic

- verify Media is still ready/clean before reading bytes;
- parse only the approved media asset;
- normalize parser output into allowed fields;
- parser/library confidence or extraction errors do not map to candidate quality;
- extracted skills/titles are metadata candidates for later projection, not authoritative taxonomy unless validated through Taxonomy if needed;
- raw text retention follows U-CL06-13; if unresolved in non-production, keep it disabled/minimized rather than guessing retention.

### Authorization / Compliance

Worker uses scoped system authority. Raw text is not logged, analyzed by unrelated services, or returned to unauthorized UI.

### Database / Transaction Behavior

- worker acquires idempotent job claim;
- status update uses expected current state;
- completed write records parser name/version and normalized output;
- failure write records safe failure reason only;
- prior operational attempt evidence remains in shared queue/Ops unless U-CARP-02 introduces approved owner proof.

### Events / Jobs

```text
resume.parse_started       # optional internal event only if useful
resume.parse_completed
resume.parse_failed
```

Events exclude extracted text.

### Provider Integration

No provider webhook. Parser libraries stay behind ResumeParserPort.

### UI / Admin Surface

- parse pending/processing/completed/failed status;
- safe retry when permitted;
- no score/rank/recommendation UI.

### Failure Behavior

- file disappears/not ready → retryable or terminal according to Media state;
- deterministic corrupt document → permanent failure;
- worker timeout/library transient → bounded retry;
- retry exhaustion → accurate `failed` state + Ops/dead-letter reference;
- no fallback to a permissive “parsed enough” state.

### Tests

- PDF/DOCX parser contract fixtures;
- normalized output schema;
- ready+clean recheck;
- parser version recorded;
- idempotent duplicate job;
- retry/permanent failure classification;
- raw text redaction from logs/events;
- assertion that no output field is hiring recommendation/rank/eligibility.

### Documentation Updates

Update raw-text retention/encryption section if U-CL06-13 is approved. Update U-CARP-02 if parse-attempt proof is settled.

### Acceptance Criteria

The parser produces durable extraction evidence only, is retryable/observable, and cannot leak raw text or produce hiring decisions.

### Exit Gate

PASS only if PDF/DOCX fixtures parse through the port, retry/dead-letter behavior is deterministic, no raw text appears in logs/events/Search, no recommendation/ranking output exists, and all worker/integration/security tests pass.

---


## 06 Candidate Application Self-Service and Withdrawal

### Objective

Give candidates privacy-shaped access to their own applications and implement the candidate-owned withdrawal path without exposing recruiter-only internal data or inventing unapproved lifecycle semantics.

### Observable Result

A candidate can list/view their applications, see the candidate-facing status, and withdraw an application only when the U-CL06-11-approved policy allows; downstream consumers receive a durable withdrawal fact.

### Cluster Build-Plan Link

Completes Candidate self-service within CL-06 Feature **05** and prepares CL-06 Feature **06** recruiter pipeline.

### Dependencies

- Feature 05;
- U-CL06-11 approved for withdrawal/terminal behavior;
- Notification contract;
- Job Interview event consumer contract may be fixture-stubbed until its Cluster feature.

### In Scope

- `listCandidateApplications`;
- candidate-shaped `getJobApplicationDetail`;
- `withdrawJobApplication`;
- candidate-facing status/timestamps;
- withdrawal event and Notification request;
- downstream application-state event consumed later by Job Interview.

### Out of Scope

- recruiter pipeline controls;
- application view tracking;
- resume grant;
- refunding/reversing Track usage unless U-CL06-11/Track contract explicitly says withdrawal restores quota;
- interview mutation.

### Module-Owned Data

`JobApplication`.

### Public Interfaces

- `listCandidateApplications`;
- `getJobApplicationDetail` candidate view;
- `withdrawJobApplication`.

### Shared Operations Used

- actor/authority;
- SH-053 `transitionLifecycleState` (Confirmed) — plumbing only; local withdrawal graph remains Candidate-owned;
- SH-052 `withOptimisticConcurrency` (Confirmed) — stale withdrawal race;
- SH-046 `publishDomainEvent` (Confirmed) — `application.withdrawn`;
- SH-041 `requestNotification` (Confirmed) — safe candidate/org notice.

### Domain Logic

- candidate view exposes candidate-facing status and approved Job summary, not unnecessary recruiter-only stage/internal data;
- withdrawal follows the approved transition matrix;
- timestamp updates are consistent with U-CL06-11;
- withdrawal does not directly cancel JobInterview; event informs Job Interview owner;
- Track usage reversal occurs only if Track policy explicitly defines it.

### Authorization / Compliance

Candidate must own CandidateProfile/application. Cross-user reads/writes deny. Privacy shaping applies to response DTO.

### Database / Transaction Behavior

- optimistic concurrency on application;
- status/timestamp/outbox commit atomically;
- repeated same idempotency request returns existing withdrawn result where safe.

### Events / Jobs

`application.withdrawn` event. No Candidate worker required unless a downstream retry/outbox consumer exists.

### Provider Integration

None.

### UI / Admin Surface

Candidate application list/detail and permitted withdrawal action.

### Failure Behavior

- terminal/illegal transition → deterministic domain denial;
- stale status → conflict;
- Notification failure → retry without reverting withdrawal;
- Job Interview unavailable → event remains in outbox; Candidate truth stays withdrawn.

### Tests

- candidate privacy-shaped DTO;
- ownership isolation;
- every approved/denied withdrawal case;
- stale concurrent withdrawal/recruiter transition;
- event/outbox durability;
- downstream Job Interview fixture receives but cannot mutate application.

### Documentation Updates

Update lifecycle section if U-CL06-11 transition matrix is finalized.

### Acceptance Criteria

Candidate self-service is owner-safe, withdrawal obeys approved lifecycle, and downstream failures do not corrupt source state.

### Exit Gate

PASS only if candidate reads expose only approved data, withdrawal transition/timestamps are deterministic, no direct Job Interview mutation exists, and all lifecycle/authorization/contract tests pass.

---

# Phase 4 — Recruiter Pipeline and Sensitive Resume Access

## 07 Recruiter Applicant Reads, View Events, and Pipeline Transitions

### Objective

Allow authorized OrganizationMembers to list/view applicants and mutate JobApplication stage/status only through Candidate Application policy, with append-only application-view evidence under the approved U-CL06-12 semantics.

### Observable Result

An authorized recruiter can see privacy-shaped applicants for their Organization’s Job, a qualifying view produces the approved JobApplicationViewEvent/summary behavior, and legal stage/status transitions succeed while cross-org or stale/illegal transitions fail.

### Cluster Build-Plan Link

Implements CL-06 Feature **06 Recruiter Applicant Views, View Events, and Pipeline State**.

### Dependencies

- Features 05–06;
- Organization Hiring owner facts;
- Role / Authority;
- U-CL06-11 approved transition matrix/event requirements;
- U-CL06-12 approved view semantics;
- valid schema evidence independent of retired U-CL06-17; R008 semantic relation correction remains for a later database pass;
- Notification/Audit contracts as required.

### In Scope

- recruiter-shaped `listJobApplicants`;
- recruiter-shaped `getJobApplicationDetail`;
- `recordJobApplicationView`;
- `transitionApplicationStage`;
- `transitionApplicationStatus`;
- first-view/summary behavior exactly as approved;
- stage/status/timestamp invariants;
- pipeline UI;
- events/notifications.

### Out of Scope

- resume file access;
- candidate search;
- JobInterview creation;
- Organization member-role policy;
- application scoring/ranking.

### Module-Owned Data

- `JobApplication`;
- `JobApplicationViewEvent` after U-CL06-12 approval;
- optional `JobApplicationEvent` only if U-CL06-11 explicitly adds it.

### Public Interfaces

- `listJobApplicants`;
- recruiter `getJobApplicationDetail`;
- `recordJobApplicationView`;
- `transitionApplicationStage`;
- `transitionApplicationStatus`;
- candidate status query remains stable.

### Shared Operations Used

Use SH-076 `normalizeAndHashIdentifier` (Confirmed) for approved IP/identifier evidence; Candidate owns capture policy and view-event meaning.

- SH-001 `resolveAuthenticatedActor` (Confirmed);
- SH-002 `authorizeResourceAction` (Confirmed) — org-scope authority;
- owner-facts query from Organization Hiring;
- SH-053 `transitionLifecycleState` (Confirmed) — shared plumbing, Candidate-owned graph;
- SH-052 `withOptimisticConcurrency` (Confirmed) / SH-051 `acquireAggregateLock` (Confirmed) — stale/concurrent pipeline mutations;
- SH-046 `publishDomainEvent` (Confirmed);
- SH-029 `appendAuditEvent` (Confirmed) when root policy requires;
- SH-041 `requestNotification` (Confirmed).

### Domain Logic

- JobApplication must reference a Job owned by the actor’s Organization;
- recruiter read is privacy-shaped and does not include a signed resume URL;
- one qualifying view appends view truth according to U-CL06-12;
- repeated views append or dedupe exactly as the approved semantics define;
- status and stage are distinct dimensions; every transition and timestamp compatibility is enforced by U-CL06-11 matrix;
- `stage=interview` does not create JobInterview automatically unless a downstream owner workflow is requested separately;
- Organization Hiring and Job Interview never write application fields directly.

### Authorization / Compliance

Cross-org isolation is mandatory. Applicant detail access is not resume access. Sensitive support/admin read path is explicit and audited if required.

### Database / Transaction Behavior

- view event append + summary projection update occur in one local transaction if U-CL06-12 requires both;
- stage/status transition + timestamps + event/outbox atomic;
- optimistic concurrency rejects stale recruiter updates;
- append-only event rows are not updated/deleted by normal pipeline operations.

### Events / Jobs

```text
application.viewed
application.stage_changed
application.status_changed
```

No new background job required.

### Provider Integration

None.

### UI / Admin Surface

- Organization applicant list/detail;
- pipeline stage/status controls;
- candidate-facing status remains distinct;
- no resume document display in this feature.

### Failure Behavior

- cross-org actor → deny/no event;
- illegal transition → domain denial;
- stale update → conflict;
- event/outbox failure prevents commit only according to transaction design; downstream Notification failure retries independently;
- U-CL06-11/12 unresolved → feature remains disabled rather than guessing.

### Tests

- complete approved transition matrix;
- status-stage compatibility/timestamps;
- cross-org isolation;
- view event append/summary behavior;
- repeated view semantics;
- stale concurrent recruiter updates;
- contract test proving Organization Hiring/Job Interview do not write application tables;
- RLS/server parity;
- pipeline UI/E2E.

### Documentation Updates

When U-CL06-11/12 are approved, update Module architecture with binding matrix/semantics before coding.

### Acceptance Criteria

Recruiter pipeline truth is Candidate-owned, cross-org access is impossible, view evidence is append-only as approved, and every transition is deterministic/auditable.

### Exit Gate

PASS only if U-CL06-11/12 are resolved and implemented exactly, no neighboring Module writes JobApplication, cross-org/RLS tests fail closed, stale transitions conflict, and all tests/build checks pass.

---

## 08 Contextual Resume Access and Correlated Sensitive-Access Proof

### Objective

Issue short-lived private resume access only after Candidate Application validates exact application, Organization, media, viewer, and reason, while preserving separate Candidate, Media, and Audit proof.

### Observable Result

An authorized recruiter/interviewer/admin can request a resume for an allowed reason and receive a Media-owned short-lived grant/URL; unauthorized/cross-org/wrong-media access produces no grant; successful access creates the required correlated `ResumeAccessLog`, `MediaAccessEvent`, and `AccessAuditLog` according to approved semantics.

### Cluster Build-Plan Link

Implements CL-06 Feature **07 Contextual Resume Access and Sensitive Access Proof** and supplies the resume-review boundary needed by CL-06 Feature **11**.

### Dependencies

- Feature 07;
- Media temporary-grant/signed URL interfaces;
- Audit SH-030 `recordSensitiveAccess` (Confirmed);
- U-CL06-13 approved access-event semantics;
- U-CL06-04 only if organization resume viewer is monetized;
- Role / Authority and Organization owner facts.

### In Scope

- `authorizeContextualResumeAccess`;
- `requestResumeAccessGrant` orchestration;
- `recordResumeAccess` according to approved semantics;
- reason handling including `application_review`, `candidate_search`, `interview_review`, `admin_review` where allowed;
- correlation/evidence references among Candidate/Media/Audit records;
- expired-link recovery by requesting a new grant, not extending a URL locally;
- resume access UI control.

### Out of Scope

- MediaAccessGrant/Event lifecycle implementation;
- signed URL generation;
- R2/storage client;
- generic document viewer;
- broad admin bypass;
- candidate search activation.

### Module-Owned Data

`ResumeAccessLog` only.

### Public Interfaces

- `authorizeContextualResumeAccess`;
- `requestResumeAccessGrant`;
- internal/public `recordResumeAccess` as appropriate;
- Job Interview consumes the same public access path for `interview_review`.

### Shared Operations Used

Use SH-125 `recordDomainAccessEvent` (Confirmed) for ResumeAccessLog/domain proof append and SH-076 `normalizeAndHashIdentifier` (Confirmed) for approved access metadata. Candidate retains event semantics and authorization.

- SH-001 `resolveAuthenticatedActor` (Confirmed);
- SH-002 `authorizeResourceAction` (Confirmed);
- Organization owner facts;
- Media readiness query;
- SH-088 `manageTemporaryAccessGrant` (Confirmed) — Media/shared grant mechanism;
- SH-127 `requestMediaAccess` (Proposed ruling; approved identity, caller binding required) — Media;
- SH-030 `recordSensitiveAccess` (Confirmed) — Audit;
- SH-044 `executeIdempotentCommand` (Confirmed) — access request replay;
- shared IP hashing/minimization primitive;
- SH-029 `appendAuditEvent` (Confirmed) where policy requires.

Local policy remains: exact application↔Job↔Organization relation, media attachment relation, allowed ResumeAccessReason, and candidate privacy context.

### Domain Logic

Authorization sequence is fixed:

```text
authenticated actor
→ Role / Authority allows named action
→ application belongs to actor Organization's Job or approved candidate-search/interview context
→ media belongs to approved Candidate/Application context
→ Media is ready + scan-clean
→ ResumeAccessReason is allowed
→ optional Organization ATS commercial gate only after U-CL06-04
→ Candidate contextual allow
→ Media grant / signed URL
→ Candidate resume proof + generic sensitive access proof
```

No signed URL may be generated before the Candidate contextual decision.

### Authorization / Compliance

- cross-org isolation mandatory;
- possession of media/app IDs not enough;
- admin/support uses explicit action vocabulary and audit;
- step-up only if root policy requires it for the exact sensitive action;
- TTL comes from Media policy, not Candidate hardcoding;
- private resume never becomes a public static URL.

### Database / Transaction Behavior

- Candidate authorization itself is read-only;
- `ResumeAccessLog` append timing follows U-CL06-13;
- false success is prohibited: Media failure cannot be recorded as a successful resume access;
- correlation IDs/evidence refs connect Candidate/Media/Audit records;
- access log is append-only.

### Events / Jobs

Optional `resume.accessed` domain event only with semantics aligned to U-CL06-13. No provider worker is owned here.

### Provider Integration

None. Media owns storage/provider signing.

### UI / Admin Surface

- resume view/download action;
- expired grant recovery;
- safe denial/remediation message;
- no URL stored in browser-persistent application state beyond what root UI rules permit.

### Failure Behavior

- unauthorized/cross-org/wrong-media → deny, no grant;
- Media unavailable → explicit retryable/unavailable, no false ResumeAccessLog success;
- grant expires → request fresh grant and re-evaluate Candidate context;
- Audit failure follows root security policy; if audit is mandatory for this action, fail closed or surface incomplete access proof exactly as root policy specifies;
- U-CL06-13 unresolved → no compliance-grade production release.

### Tests

- cross-org/wrong-application/wrong-media denial;
- unauthorized role denial;
- not-ready/not-clean Media denial;
- reason-specific authorization;
- signed URL not called before allow;
- expired grant recovery;
- Candidate/Media/Audit correlation;
- no permanent URL persistence;
- sensitive telemetry redaction;
- Job Interview `interview_review` contract.

### Documentation Updates

Update ResumeAccessLog semantics and proof sequence after U-CL06-13 approval. If U-CL06-04 adds a commercial gate, update both Organization/Track/Candidate architecture before enabling it.

### Acceptance Criteria

Every resume credential follows Candidate authorization; every successful access has exactly the required separate proofs; no unauthorized path can obtain a URL/grant.

### Exit Gate

PASS only if U-CL06-13 is resolved, no signed URL precedes Candidate authorization, cross-org/wrong-media access fails, correlated proof is complete, no local Media signer/grant system exists, and all security/contract/E2E tests pass.

---

# Phase 5 — Candidate Search Projection and Entitlement-Gated Perks

## 09 Privacy-Safe Candidate Search Projection and Candidate Perks

### Objective

Build and maintain a privacy-safe CandidateSearchProjection while keeping Search execution and Track-owned boost/application-view perks outside this Module.

### Observable Result

A candidate source projection can be deterministically built from allowlisted profile/parse metadata, activated/hidden/erased only under approved visibility semantics, sent to Search through the canonical refresh contract, and enhanced by Track-owned boost/view-insight decisions without local premium state.

### Cluster Build-Plan Link

Implements CL-06 Feature **08 Candidate Search Projection and Candidate Perks**.

### Dependencies

- Features 04 and 07;
- U-CL06-10 approved visibility/search participation;
- U-CARP-01 approved projection cardinality/versioning;
- Search refresh/removal contract;
- Track SH-005 `resolveEntitlement` (Confirmed);
- U-CL06-12 for application-view insight source semantics;
- Privacy target protocol.

### In Scope

- deterministic `buildCandidateSearchProjection`;
- projection repository/lifecycle;
- `getCandidateSearchProjection`;
- `transitionCandidateSearchProjectionStatus`;
- Search refresh/removal request;
- response to relevant CandidateProfile/ResumeParse/Privacy/Track changes;
- candidate discoverability settings UI if U-CL06-10 approves it;
- `getApplicationViewInsights` gated by Track entitlement.

### Out of Scope

- Typesense client/index schema execution;
- search ranking algorithm;
- local search boost field as entitlement truth;
- automated candidate recommendation/ranking;
- raw resume indexing;
- deciding search consent requirements.

### Module-Owned Data

`CandidateSearchProjection` and its status/source version semantics as approved.

### Public Interfaces

- `buildCandidateSearchProjection` internal/worker;
- `getCandidateSearchProjection` public to Search/candidate UI;
- `transitionCandidateSearchProjectionStatus`;
- `getApplicationViewInsights`;
- event handler for entitlement/privacy/source changes;
- Search refresh/removal request via Search owner.

### Shared Operations Used

- SH-094 `buildSourceProjection` (Confirmed) — shared pattern, Candidate local implementation;
- SH-005 `resolveEntitlement` (Confirmed) — Track boost/view perk;
- SH-091 `requestSearchProjectionRefresh` (Confirmed) — Search public interface;
- SH-047 `enqueueReliableJob` (Confirmed) / retry — projection work;
- SH-046 `publishDomainEvent` (Confirmed) / event dedupe;
- Privacy protocols for hide/erase;
- SH-052 `withOptimisticConcurrency` (Confirmed) — projection version race.

### Domain Logic

- allowlist only approved fields;
- `rawResumeTextIndexed=false` by default and must remain false for MVP unless explicit architecture/legal decision changes it;
- candidate visibility/search participation follows U-CL06-10 exactly;
- candidate boost is resolved from Track and passed as an input/evidence to Search; it is not persisted as Candidate entitlement truth unless architecture explicitly defines a derived snapshot field;
- view insights read Candidate-owned JobApplicationViewEvent truth and are displayed only if Track entitlement permits;
- candidate restriction/erasure must hide/erase source projection and request Search removal;
- Search outage never changes CandidateSearchProjection source truth.

### Authorization / Compliance

- candidate controls only the search participation/settings that U-CL06-10 grants;
- Search reads only sanitized public/protected projection DTO;
- raw resume/private application content excluded;
- no local `isBoosted`, `premium`, or view-tracking-access flag.

### Database / Transaction Behavior

- implement U-CARP-01-approved cardinality/versioning exactly;
- stale worker cannot overwrite newer hidden/erased state;
- projection source change + outbox/refresh request is transactionally coherent;
- Search refresh uses source version/idempotency.

### Events / Jobs

- `candidate_projection.changed`;
- projection build/rebuild worker;
- Search refresh/removal request;
- entitlement-change event handler;
- privacy/status change handler.

### Provider Integration

None. Search owns Typesense.

### UI / Admin Surface

- candidate discoverability/search participation controls only if approved;
- application-view insight surface only when Track entitlement allows;
- safe state for search unavailable/lagging without implying source visibility changed.

### Failure Behavior

- U-CL06-10 unresolved → search remains disabled/non-indexed;
- projection build failure → retry/ops, no stale Search update;
- Search unavailable → source remains correct, refresh retries;
- Track unavailable → perk/boost unavailable; do not assume premium access;
- Privacy erase → removal remains high-priority/retryable and source becomes non-searchable according to approved sequence.

### Tests

- field allowlist;
- raw text absence;
- visibility/status matrix;
- U-CARP-01 current-projection selection;
- stale worker after hide/erase;
- Search contract proves Search does not read raw resume/private tables;
- Track boost reindex behavior;
- view-insight entitlement gate;
- privacy de-index;
- Search outage/retry.

### Documentation Updates

Update visibility/cardinality architecture when U-CL06-10/U-CARP-01 settle. Record any Search DTO version change.

### Acceptance Criteria

Search can rebuild from Candidate-owned sanitized source, privacy/visibility dominates stale workers, Track perks are external truth, and raw resume text never enters Search.

### Exit Gate

PASS only if U-CL06-10 and U-CARP-01 are resolved, projection rebuild/de-index works, Track revocation removes perks/boost effect, Search remains external projection, no raw resume enters Search, and all contract/privacy/concurrency tests pass.

---

# Phase 6 — Cross-Module Hiring Handoffs

## 10 Job Interview, Notification, and Messaging Handoff Contracts

### Objective

Stabilize Candidate Application’s outbound/inbound contracts so Job Interview, Organization Hiring, Notification, and Messaging can participate without direct Candidate database access or lifecycle mutation.

### Observable Result

Job Interview can obtain a minimal application/candidate/organization context and request Candidate-owned stage/status/resume behavior; Organization Hiring can render applicant summaries; application events can request Notification/Messaging effects; no neighbor imports Candidate repositories.

### Cluster Build-Plan Link

Supports CL-06 Features **09–11** from the Candidate Application side and contributes to CL-06 Feature **14 Cross-Cluster Hiring Contract Proof**.

### Dependencies

- Features 06–08;
- Job Interview public contract/fixture;
- Organization Hiring dashboard contract;
- Notification and Messaging owner contracts;
- transactional outbox/inbox/dedupe.

### In Scope

- `getApplicationInterviewContext`;
- Candidate-owned stage/status command usable by Job Interview/Organization Hiring after authority/policy;
- event consumer contract for Job Interview reactions to application withdrawal/rejection/closure;
- resume `interview_review` path reuse;
- applicant-summary DTO for Organization Hiring;
- Notification request payload mapping;
- optional SH-113 `ensureContextThread` (Confirmed) after application commit;
- contract/version tests.

### Out of Scope

- JobInterview creation/scheduling;
- Thread/Message truth;
- Notification delivery;
- video room;
- calendar;
- Organization member mutation.

### Module-Owned Data

No new core schema required. Existing CandidateProfile/JobApplication/ResumeAccessLog may be read/mutated only by their owner services.

### Public Interfaces

- `getApplicationInterviewContext`;
- stable candidate/recruiter applicant DTOs;
- `transitionApplicationStage` / status request contract;
- Candidate resume `interview_review` contract;
- versioned domain events.

### Shared Operations Used

- SH-003 `queryOwnerFacts` (Proposed ruling) pattern — Candidate exposes minimal owner facts, no universal repository;
- SH-046 `publishDomainEvent` (Confirmed) / SH-045 `deduplicateDomainEvent` (Confirmed);
- SH-041 `requestNotification` (Confirmed);
- SH-113 `ensureContextThread` (Confirmed);
- SH-030 `recordSensitiveAccess` (Confirmed) via resume review path;
- SH-044 `executeIdempotentCommand` (Confirmed) for externally requested owner mutations.

### Domain Logic

- Job Interview reads application facts but owns no application fields;
- a request to move application stage can be denied without rewriting interview history;
- Organization Hiring receives privacy-shaped applicant facts only;
- Messaging receives context/participant facts, then owns Thread;
- Notification receives business event meaning and safe template data, then owns delivery;
- resume review always uses Feature 08 path.

### Authorization / Compliance

- each public read/mutation re-authorizes actor/resource context rather than trusting neighbor possession of IDs;
- Job Interview system/organization actor must be authorized for requested Candidate operation;
- sensitive payloads minimized.

### Database / Transaction Behavior

- no cross-domain transaction that directly writes JobInterview/Thread/Notification tables;
- Candidate mutation/outbox atomic;
- consumers dedupe events;
- externally requested Candidate command uses idempotency key and owner-issued opaque expectedConcurrencyToken.

### Events / Jobs

Exercise:

```text
application.submitted
application.withdrawn
application.status_changed
application.stage_changed
resume.accessed
```

Downstream owner retries are independent of Candidate truth.

### Provider Integration

None.

### UI / Admin Surface

No new Candidate product UI beyond existing application/resume surfaces; this is primarily contract integration.

### Failure Behavior

- neighbor unavailable → explicit retry/unavailable, no direct repository fallback;
- Candidate denies requested stage change → caller handles denial, Candidate state unchanged;
- Notification/Messaging failure → retry downstream, source event remains true;
- resume review denial → no Media grant.

### Tests

- Job Interview contract tests proving no direct writes;
- Organization applicant-summary contract;
- event envelope/version/dedupe;
- Notification payload redaction;
- Messaging context contract;
- interview_review resume access proof;
- unavailable dependency tests.

### Documentation Updates

Freeze/version public contracts. Update dependency public-interface docs if field sets or reason codes become binding.

### Acceptance Criteria

Every major CL-06 consumer can participate through typed Candidate contracts/events, and no neighboring repository or lifecycle is absorbed.

### Exit Gate

PASS only if Organization Hiring and Job Interview contain no direct Candidate repository writes, Messaging/Notification effects use owner APIs, interview resume review uses Candidate authorization, event replay is safe, and all contract/integration tests pass.

---

# Phase 7 — Privacy, Retention, and Cross-Cluster Contract Proof

## 11 Candidate Privacy Executor, Retention, and Media/Search Handoffs

### Objective

Allow Privacy / Data Erasure to enumerate and instruct Candidate Application data dispositions while this Module mutates only its own records and delegates Media/Search cleanup to their owners.

### Observable Result

A Privacy target request can enumerate CandidateProfile/application/resume/projection data and execute export, erase, anonymize, restrict, detach, or retain behavior idempotently; Search de-index and Media deletion/revocation are delegated; partial failure remains visible and rerunnable.

### Cluster Build-Plan Link

Implements Candidate-owned portion of CL-06 Feature **13 Privacy Executors, Retention, and Search/Media Erasure Handoffs** and contributes to Feature **14** contract proof.

### Dependencies

- all enabled Candidate features;
- Privacy SH-096 `enumerateSubjectData` (Confirmed), SH-095 `executePrivacyInstruction` (Confirmed), SH-097 `evaluateRetentionRequirement` (Confirmed) protocol;
- Media deletion/revocation contract;
- Search removal contract;
- Audit/Ops;
- U-CL06-13 raw-text retention resolved before destructive production execution;
- approved hiring-record retention rules for records to be retained/anonymized.

### In Scope

- SH-096 `enumerateSubjectData` (Confirmed) implementation;
- SH-095 `executePrivacyInstruction` (Confirmed) implementation;
- candidate data export serializer;
- anonymization/erasure/restriction mappings;
- CandidateSearchProjection hide/erase + Search removal request;
- Candidate media detach + Media deletion/revocation request;
- retention fact evaluation;
- idempotent rerun/partial result;
- privacy integration tests.

### Out of Scope

- PrivacyRequest/DataErasureJob/DataRetentionExemption lifecycle;
- deleting Media objects directly;
- deleting Typesense docs directly;
- legal retention interpretation not supplied by approved policy;
- broad database crawler.

### Module-Owned Data

Potentially all Candidate-owned personal-data records:

- CandidateProfile;
- CandidateProfileMedia;
- JobApplication;
- JobApplicationMedia;
- ResumeParseResult;
- ResumeAccessLog;
- JobApplicationViewEvent if approved;
- CandidateSearchProjection;
- CandidateCategory/Tag only according to U-CL06-08 execution ownership.

### Public Interfaces

- SH-096 `enumerateSubjectData` (Confirmed);
- SH-095 `executePrivacyInstruction` (Confirmed);
- owner retention-facts response;
- export contribution contract.

### Shared Operations Used

- SH-096 `enumerateSubjectData` (Confirmed) — Privacy protocol, local implementation;
- SH-095 `executePrivacyInstruction` (Confirmed) — Privacy protocol, local implementation;
- SH-097 `evaluateRetentionRequirement` (Confirmed) — owner facts + Privacy exemption lifecycle;
- SH-098 `anonymizePersonalFields` (Confirmed) — shared mechanism with Candidate field map;
- SH-091 `requestSearchProjectionRefresh` (Confirmed)/removal — Search;
- Media deletion/revocation owner commands;
- SH-029 `appendAuditEvent` (Confirmed) for destructive execution where required;
- queue/retry/dead-letter/Ops.

### Domain Logic

- product archive is not legal erasure;
- owner records are mutated only according to Privacy instruction and approved retention map;
- retained records minimize/anonymize personal fields where permitted;
- raw extracted resume text follows U-CL06-13 exactly;
- source projection is made non-searchable before/with de-index request according to approved privacy sequence;
- Media relationships can be detached, but actual object deletion remains Media-owned;
- proof of privacy execution is returned, not silently discarded.

### Authorization / Compliance

Scoped Privacy/system actor only. Destructive operations require valid instruction IDs and approved retention facts. No end-user route directly calls owner deletion internals.

### Database / Transaction Behavior

- local owner mutation uses transaction per target/subtarget as approved;
- idempotency key = Privacy target/instruction version;
- retained rows reference Privacy-owned exemption IDs/evidence;
- partial downstream failure does not falsely mark Candidate target complete;
- rerun skips already completed idempotent subeffects safely.

### Events / Jobs

- owner privacy executor may run as durable job;
- Search/Media requests have independent retries;
- completion/partial/failure result returned to Privacy;
- audit/ops recorded separately.

### Provider Integration

None directly.

### UI / Admin Surface

Privacy UI remains Privacy-owned. Candidate module may expose protected operational target details/retry status only if root admin patterns require it.

### Failure Behavior

- retention rule unknown → manual review/blocked destructive action;
- Search/Media unavailable → local privacy source state and pending external effect remain explicit;
- partial failure → retryable target result, not completed;
- audit/ops records never substitute for disposition truth.

### Tests

- complete subject enumeration;
- export redaction;
- erase/anonymize/restrict/retain mapping;
- raw-text retention behavior;
- Search de-index handoff;
- Media deletion/revocation delegation;
- idempotent rerun;
- partial failure/recovery;
- retention exemption references;
- authorization of service actor.

### Documentation Updates

Update Module privacy matrix whenever retention rulings change. Record any new DataErasureTarget type required in Privacy-owned architecture before implementation.

### Acceptance Criteria

Privacy is the sole orchestrator, Candidate mutates only its records, Search/Media effects are delegated, retention is explicit, and reruns/partial failures are safe.

### Exit Gate

PASS only if U-CL06-13/required retention policies are resolved for enabled destructive behavior, subject enumeration is complete, Search and Media delegation work, retained records cite exemptions, reruns are idempotent, partial failures remain visible, and privacy/security tests pass.

---

## 12 Candidate Module Cross-Cluster Contract Proof

### Objective

Prove the complete Candidate Application module against all critical neighboring owner contracts, including denial, unavailable, replay, stale-version, privacy, and concurrency cases, without direct cross-domain repository access.

### Observable Result

The Candidate path works with real interfaces or versioned fixtures for Identity, Role, Organization Hiring, Track, Trust, Holds, Media, Search, Audit, Notification, Messaging, Privacy, Ops, and Job Interview; unavailable neighbors never trigger permissive fallback or direct DB shortcuts.

### Cluster Build-Plan Link

Implements Candidate-owned contribution to CL-06 Feature **14 Cross-Cluster Hiring Contract Proof**.

### Dependencies

Features 01–11 as enabled. Any unimplemented neighbor is represented only by a versioned contract fixture.

### In Scope

- freeze/version public Candidate contracts;
- integration harness for all direct dependencies/consumers;
- critical path contract tests;
- event/outbox/inbox replay tests;
- RLS/authorization parity;
- dependency-unavailable behavior;
- contract compatibility validation.

### Out of Scope

- implementing missing neighbor internals inside Candidate module;
- adding new product features;
- relaxing blockers for test convenience.

### Module-Owned Data

No ownership change or new business schema. Fixtures use owner DTOs/decisions/events only.

### Public Interfaces

Stabilize/version all interfaces introduced by Features 01–11.

### Shared Operations Used

Exercise every already-approved canonical operation used by the Module. Do not invent a new shared operation merely to simplify the test harness.

### Domain Logic

Prove at minimum:

```text
Identity actor → CandidateProfile ownership
Organization Job facts → application eligibility
Track allowance → one application usage
Trust readiness → verified-only gate
Hold → blocked application/access
Media ready/clean → parse + resume access
Application view → Candidate event truth + Track-gated insight
Resume authorization → Media grant + separate Audit proof
Candidate projection → Search refresh/remove
Application events → Notification/Messaging
Application facts → Job Interview without direct writes
Privacy → Candidate executor → Search/Media delegation
Ops → failure visibility only
```

### Authorization / Compliance

Cross-user and cross-Organization isolation are mandatory cases. Dependency unavailable never becomes allow.

### Database / Transaction Behavior

No direct neighbor writes. Candidate transactions/outbox remain owner-local. Fixtures must not expose repository handles.

### Events / Jobs

Exercise outbox/inbox, duplicate event delivery, worker retry/dead-letter, Search refresh, parse retry, privacy execution.

### Provider Integration

No direct provider test beyond parser libraries. Media/Search/etc provider behavior is represented by owner contract fixtures or their real test adapters.

### UI / Admin Surface

No new product UI required.

### Failure Behavior

- neighbor unavailable → explicit unavailable/retry/deny according to local policy;
- stale source version → conflict/re-evaluate;
- duplicate event/request → idempotent result;
- no fallback to direct Prisma or local copy.

### Tests

- full contract suite;
- RLS/server parity;
- idempotency/replay;
- dependency degradation;
- privacy/de-index;
- resume access proof;
- application quota concurrency;
- critical E2E:

```text
CandidateProfile → private resume upload → application + application-media link → parse
Recruiter → applicant detail → view event → pipeline transition
Recruiter/Interview → contextual resume access
Candidate search source projection → Search fixture
Application → Job Interview handoff
Privacy instruction → projection removal + Media delegation
```

### Documentation Updates

Record final contract versions, fixtures, and any resolved architecture decisions. Update progress tracker.

### Acceptance Criteria

No cross-module repository access exists; all owner boundaries are exercised; failures remain explicit; privacy and source truth remain intact.

### Exit Gate

PASS only if every critical neighbor has a typed real/fixture contract, no direct cross-domain repository access/write exists, unavailable dependencies fail closed/explicitly, event replay is safe, and the complete contract/E2E suite passes.

---

# Phase 8 — Hardening and Production Verification

## 13 Candidate Security, Reconciliation, Backfill, and Production Hardening

### Objective

Harden all production-enabled Candidate Application workflows for authorization, concurrency, replay, parser/Search degradation, privacy, access-proof completeness, reconciliation, backfill, performance, and migration safety.

### Observable Result

Candidate application and resume workflows survive duplicate requests, stale writes, worker outages, Search lag, privacy reruns, and dependency degradation without violating source truth or exposing sensitive data; production diagnostics and recovery paths are visible.

### Cluster Build-Plan Link

Implements Candidate-owned portion of CL-06 Feature **15 CL-06 Security, Reconciliation, Backfill, and Production Hardening**.

### Dependencies

All enabled prior Module features; every architecture blocker affecting those production features must be resolved and reflected in architecture.

### In Scope

- RLS/server authorization parity review;
- application quota/duplicate submission stress tests;
- partial Track/application reconciliation;
- stale stage/status transition handling;
- resume parse retry/backfill;
- projection rebuild/de-index reconciliation;
- resume grant/access-audit completeness checks;
- privacy executor rerun/recovery;
- dead-letter/manual recovery tools where root Ops patterns require;
- index/query performance review;
- safe checkpointed backfills;
- migration rehearsal, including deprecated-field cleanup only after U-CL06-09;
- telemetry redaction/security review;
- public contract version stability.

### Out of Scope

- new product features;
- Organization ATS monetization without U-CL06-04;
- automated hiring recommendation/scoring;
- new screening/legal policy;
- generic queue/state machine/readiness/audit framework;
- marketplace workflows.

### Module-Owned Data

Review all Candidate-owned schema/indexes. Do not create a generic hiring source-of-truth or duplicate platform infrastructure.

### Public Interfaces

Stabilize/version existing interfaces. Do not create new ownership solely for hardening.

### Shared Operations Used

- authorization/audit/access;
- idempotency/concurrency;
- queue/retry/dead-letter;
- Search refresh/reconciliation through Search owner;
- Privacy protocol;
- Ops failure visibility;
- owner contract health/replay mechanisms.

### Domain Logic

Hardening scenarios include:

- concurrent same-Job submissions near quota boundary;
- usage consumed but application result temporarily uncertain;
- recruiter stage transition racing candidate withdrawal;
- view event retry/duplicate delivery;
- parser worker crash after status update;
- backfill of parse metadata after parser version change;
- privacy hide/erase racing stale projection rebuild;
- resume grant issued near application/organization permission revocation;
- Search refresh failure after source hide;
- audit/Media proof mismatch detection;
- migration from deprecated direct resume/verification fields after architecture decision.

No hardening mechanism may replace source lifecycle truth.

### Authorization / Compliance

- least privilege;
- support/admin resume access review;
- RLS parity;
- access-proof completeness;
- destructive privacy controls;
- sensitive telemetry review;
- no permanent credentials/URLs;
- no raw resume in logs/analytics/Search.

### Database / Transaction Behavior

- verify indexes for candidate/user, application job/status/stage, application candidate/status, parse status/media, resume access lookup, view-event lookup, projection lookup/status;
- performance improvements must not impose U-CARP-01 uniqueness before its approved resolution;
- backfills are checkpointed, idempotent, dry-run capable where destructive;
- schema migration rehearsed against representative data;
- destructive cleanup waits for architecture/retention approval.

### Events / Jobs

- replay outbox/inbox;
- resume parse retry/backfill;
- candidate projection rebuild/removal;
- privacy rerun;
- reconciliation reports;
- dead-letter/admin recovery.

### Provider Integration

Parser libraries only; degradation/upgrade compatibility tested. Other provider faults are exercised through owner contract fixtures.

### UI / Admin Surface

Only operational surfaces required for:

- failed parse retry/dead-letter;
- candidate Search lag/removal failure visibility;
- privacy target partial failure;
- reconciliation mismatch;
- access-proof investigation if root admin architecture requires it.

These surfaces are not source truth.

### Failure Behavior

No silent loss, permissive fallback, or source-state overwrite. Exhausted failure produces a stable Ops reference and accurate Candidate business state. Unsafe recovery requires manual review rather than fabricated completion.

### Tests

- full typecheck/lint/build;
- domain/unit/integration/contract/E2E;
- RLS/security;
- concurrency/load/idempotency;
- parse retry/backfill;
- Search de-index/rebuild race;
- privacy rerun/retention;
- access proof completeness;
- migration rehearsal;
- query plan/performance tests;
- telemetry redaction tests.

### Documentation Updates

- mark resolved blockers;
- record migrations/backfills;
- update public contract versions;
- update progress tracker and known risks;
- update architecture before any binding rule changes.

### Acceptance Criteria

All production-enabled Candidate workflows satisfy Module invariants under failure/replay/concurrency, privacy and resume boundaries are complete, and operational recovery is observable without duplicate source truth.

### Exit Gate

PASS only if every production-enabled architecture blocker is resolved; no lifecycle has two owners; no canonical operation is duplicated; application quota, recruiter pipeline, resume privacy/access proof, Candidate Search, Privacy execution, RLS, replay/reconciliation, backfill, performance, and critical E2E invariants all pass; documentation/progress agree with code.

---

# Module Integration Phase

Phases 6–7 are the explicit Module integration proof. They are not ownership-transfer phases.

Minimum required boundaries:

```text
Identity actor → Candidate protected action
Candidate owner facts → Role / Authority
Organization Hiring Job facts → application eligibility
Job Compliance decision → Organization Hiring applies Job lifecycle/eligibility → Candidate consumes fail-closed Organization context; no normal direct Compliance read/evaluation
Track allowance → Candidate application submission
Track perk/boost → candidate insight/search effect
Trust readiness → verified-only application gate
ComplianceHold → Candidate action gate
Media safety → candidate/application attachment
Candidate contextual resume decision → Media grant
Candidate resume proof → Audit sensitive-access proof
Candidate source projection → Search refresh/remove
Candidate domain events → Notification/Messaging
Candidate application facts → Job Interview
Privacy → Candidate executor → Search/Media handoff
Ops → diagnostic visibility only
```

Where a neighboring owner is not implemented, use a versioned fixture. Never import the neighbor’s repository into this Module.

---

# Module Hardening Phase

Phase 8 hardens only Candidate Application & Resume Privacy risk:

- CandidateProfile ownership/RLS;
- application quota + duplicate-submission races;
- status/stage transition races;
- application view append/summary correctness;
- contextual resume authorization;
- ResumeAccessLog/MediaAccessEvent/AccessAuditLog completeness;
- parser retry/version/backfill;
- raw-text retention/redaction;
- candidate Search rebuild/de-index privacy race;
- entitlement revocation behavior;
- Privacy rerun/retention;
- outbox/inbox replay;
- queue/dead-letter visibility;
- indexes/query performance;
- schema/migration/backfill safety.

Hardening must not create a generic hiring source-of-truth table, global readiness engine, universal state machine, generic event ledger, custom retry framework, custom Media grant system, local Search indexer, or local privacy workflow.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Contract and Source-of-Truth Foundation | 01 |
| 2 | Candidate Identity and Secure Resume Intake | 02 |
| 3 | Application Submission, Post-Submission Parsing, and Candidate Self-Service | 05 → 03 → 04 → 06 |
| 4 | Recruiter Pipeline and Sensitive Resume Access | 07–08 |
| 5 | Candidate Search Projection and Entitlement-Gated Perks | 09 |
| 6 | Cross-Module Hiring Handoffs | 10 |
| 7 | Privacy, Retention, and Cross-Cluster Contract Proof | 11–12 |
| 8 | Hardening and Production Verification | 13 |

**Total numbered features: 13.** Feature IDs are retained for reference stability. Execution order is **01 → 02 → 05 → 03 → 04 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13**. The prior feature exit gate means the previous feature in this sequence. CL-06 Feature 04 completes upload/profile intake only; CL-06 Feature 05 runs submission first, then the parsing stage.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read the Canonical Shared Operations Architecture.
3. Read CL-06 architecture and build plan.
4. Read this Module architecture and plan.
5. Read public-interface sections for direct dependencies/consumers.
6. Read the current Prisma schema/migrations and relevant resolved `U-CL06-*` / `U-CARP-*` decisions.
7. Confirm the prior Module feature exit gate passed.
8. Confirm the Cluster feature being supported has not moved or been blocked.
9. Produce the Required Feature Implementation Specification below.
10. Implement only that feature plus prerequisite work in its canonical owner where explicitly coordinated.
11. Run required quality checks.
12. Verify the primary workflow plus denial, stale, duplicate, unavailable, retry, and privacy cases.
13. Update progress.
14. Update architecture only when a binding decision legitimately changed.
15. Record unresolved risks/deferred work.

Do not weaken an exit gate in order to mark work complete.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise implementation specification containing:

- **Objective**
- **Observable result**
- **Cluster Build-Plan link**
- **Dependencies**
- **In scope**
- **Out of scope**
- **Owned data affected**
- **Schema/migration/index changes**
- **Public contracts introduced/changed**
- **Shared operations consumed**
- **Permissions / actor / ownership context**
- **Entitlement / verification / hold / privacy gates**
- **Primary workflow**
- **Parser/provider integration if any**
- **Jobs / events / outbox consumers**
- **Idempotency / concurrency key semantics**
- **Error / failure behavior**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**
- **Architecture decisions resolved or still blocking**

Do not pre-write file-by-file implementation specifications for all 13 features. Produce the specification for the next feature immediately before coding it.

---

# Required Completion Report

After implementing each numbered feature, report:

- Feature completed
- Cluster feature/milestone supported
- Files added
- Files changed
- Database changes
- Migrations
- Index/constraint changes
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused
- Cross-Module contracts/fixtures added or changed
- Events/outbox/inbox handlers added
- Jobs/workers added or changed
- Parser adapter changes
- UI/admin surfaces added or changed
- Tests added/changed
- Commands run
- Typecheck/lint/build result
- Manual/contract/E2E verification
- RLS/authorization verification
- Privacy/security verification
- Documentation updated
- Architecture decisions resolved
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result: PASS / FAIL

A FAIL result must name the blocking test/decision and stop sequential execution.

---

# Final Quality Check

Before the Module is considered implementation-ready or before these artifacts are revised, verify:

1. CandidateProfile and JobApplication source truth have exactly one owner.
2. No Organization Hiring, Job Interview, Media, Track, Trust, Search, Privacy, Notification, Messaging, Audit, or Ops truth was absorbed.
3. Every shared operation is consumed rather than duplicated.
4. Shared mechanism / separate truth boundaries are explicit in code and tests.
5. Public commands/queries are the preferred boundary over direct Prisma access.
6. Cross-Module reads use owner-specific contracts/fixtures where appropriate.
7. Resume parser libraries do not become hiring truth.
8. ResumeAccessLog, application view events, generic audit, Media access, and ops telemetry remain distinct.
9. Privacy orchestration remains Privacy-owned.
10. Search remains projection; raw resume text is excluded by default.
11. Track remains quota/boost/view-perk truth.
12. Trust remains screening/readiness truth.
13. Application lifecycle cannot be mutated outside this Module.
14. Contextual resume authorization always precedes Media grant/URL issuance.
15. Implementation features align with CL-06 Features 04–08, 09–11 handoffs, 13–15 integration/hardening sequence.
16. Every numbered feature has tests and a hard exit gate.
17. Every unresolved architecture item blocks only the behavior it actually governs and is never silently guessed.
18. A coding agent can implement the next feature without inventing ownership, lifecycle, provider, privacy, or shared-operation architecture.

## WA-R008 — Media public-access integration

This consumer invokes SH-127 `requestMediaAccess` with its own actor/resource/action-bound contextual authorization and required evidence. Media independently evaluates asset safety, grant, scope, expiry and revocation, then performs SH-087 `issueSignedMediaUrl` internally. The consumer never calls the signer or reads storage directly. SH-127's identity is approved; its registry status remains Proposed ruling for owner-specific integration completion. Bind the caller's exact contextual decision and failure/access-proof semantics before production use. A Media failure must not be recorded as successful file access.


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

## Readiness implementation gates — WA-R045, WA-R046, WA-R047

The corresponding owner architecture sections are binding and supersede earlier U-CL06/U-JI/U-CARP proposal gates only for their named resolved semantics. No implementation is marked complete. Execute in this order:

1. Freeze owner-specific typed commands, queries, event schemas and denied-action fixtures against the binding graphs and evidence rules. Preserve P17/P18 under WA-R042; reject obsolete opt-in/expiry alternatives.
2. Through the single migration owner, add required immutable history, aggregate revisions/current selectors, typed references and retention-safe constraints. Inspect/backfill legacy conflicts without destructive resets; database replay/RLS evidence remains required.
3. Verify concurrency and retry cases: stale revision, duplicate logical command, terminal-state replay, removed authority, stale provider callback and late suppression/restoration. Include current owner revalidation before disclosure and mandatory evidence failure.
4. Qualify bilateral Search, Role, Moderation, Privacy, Media and applicable Calendar/Video/Notification contracts. Test owner effect receipt and unavailable/denied paths; provider receipt is not domain approval.
5. Keep legal/provider-dependent surfaces disabled until named qualification evidence exists. Test parent/child retention before any erasure capability and restrict export field sets.


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


## WA-R067 — Typed moderation execution and normalized receipts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-103 remains the existing cross-cutting execution protocol; no new Shared Operation ID or schema change is authorized. Each instruction carries authorized decision/action ID, case/cycle, typed owner target ID and expected owner revision, approved effect, actor/service authority, purpose/policy/evidence references, semantic effect key and correlation. Owners validate target/action compatibility and current authority before mutation. The following versioned ports name existing owner handlers, not new lifecycle ownership or permission.

| Existing primary target / typed downstream effect | Owner port v1 | Allowed effect and guard |
| --- | --- | --- |
| job, organization | Hiring applyHiringModerationDecision.v1 | Publication suppression/eligible restoration under R047; compliance, lifecycle and all restrictions still apply |
| candidate_profile, with owned current search projection reference | Candidate applyCandidateModerationDecision.v1 | Search-projection suppression/eligible restoration only; current explicit opt-in/readiness required. No application mutation or new Candidate Hold target |
| thread, message | Messaging applyMessagingModerationDecision.v1 | Persistent content restriction/authorized restoration under R054; current membership, sensitivity and all restriction sources still apply |
| media_asset, media_access_grant | Media executeMediaModerationInstruction.v1 | Existing asset freeze, public exposure/grant revocation, evidence preservation and eligible file exposure restoration; source context and safety remain required |
| digital_download_asset, affected owned grant references | Digital Goods applyDigitalModerationDecision.v1 | Disable/restore asset and revoke affected grants; current Order entitlement/Media safety/purchased policy required, no revival of terminal grant |
| course_video_asset, affected owned playback grant references | Video applyVideoModerationDecision.v1 | Disable/restore asset and revoke affected playback grants; current entitlement/safety/provider evidence required |
| review | Review applyReviewModerationDecision.v1 | Existing hide/remove/authorized restoration under R026; restore current eligible accepted revision and adjust original reputation contribution exactly once |
| offering | Marketplace applyOfferingModerationDecision.v1 | Valid moderation restriction/clearance under R035; clearance returns to draft, fresh publish remains separate |

Existing unversioned Media/Digital/Video handler names become aliases of their listed v1 contract and must not create duplicate effects. CandidateSearchProjection, DigitalDownloadGrant and playback-grant references are owner-local downstream effects under existing primary targets, not new ModerationTargetType values. The owner validates their parent/target relationship. Each port returns semantic effect key, source decision/action, target/revision, effect state, safe outcome/retry classification and durable receipt identity. No secret/provider payload or private evidence is returned.

| Local result | Canonical effect state | Required semantics |
| --- | --- | --- |
| accepted/queued | acknowledged | Durable acceptance only; mutation/provider effect not yet proved |
| applied | completed | Exact requested effect durable, resulting owner revision and proof retained |
| restoration applied | restored | New authorized linked restoration completed; original restriction/history untouched |
| already-applied | Original receipt state | Replay exact stored receipt, including pending state; dedupe alone is not completion |
| unsupported/denied/stale conflict | failed with terminal or reevaluate classification | No mutation; conflict requires fresh facts and applicable authorized decision, never silent overwrite |
| known retryable failure | failed with retryable classification | Retry the same semantic effect identity |
| uncertain owner/provider outcome | acknowledged with reconcile_required outcome | Durable unknown-state evidence; reconcile original effect before redispatch, never claim completed/restored |

Multi-owner work retains per-step receipts; Report/Case action_taken requires every required successful effect under R058. Search refresh and provider request acknowledgments do not prove de-indexing or revocation. Restoration is a new effect linked to the original, not an edit of the original receipt. Partial bulk revocation remains incomplete until its target inventory is accounted.

Order/payout reusable stops use Hold's registered typed action/command boundary per CL-09-R007/R059, not direct Moderation writes to Order/Payment. Release triggers current owner reevaluation, never financial execution, content restoration, service completion or review eligibility. Candidate Hold types absent from the typed Hold schema remain disabled. CL-01 has no generic moderation executor under R063: only separately named authorized security/entitlement/Hold/lifecycle commands may act. Enumeration of user or profile targets is not permission. Other target/effect families not listed here must have an existing explicit owner registration before activation; this scoped matrix does not invent their semantics or silently delete their historical proposals. Unsupported combinations return unsupported, with no fallback mutation.

R026 already settles explicitly authorized Review restoration; old unresolved base text is superseded. R042 settles Booking Professional reports, authorized support adjudication and Customer contest, with no automatic consequence; R052 completed/no_show aliases are performance-report facts, not final financial/review truth. These are existing rulings, not new product decisions. Contract adapters/fixtures, typed receipt persistence and coordinated migrations remain implementation qualification.

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration — implementation obligations

Implement the owner’s WA-R070 descriptor/enumerator and assignment receipt before dependent AI/Search/merge work. Test stale source/assignment tokens, forbidden fields/purposes, cursor replay/expiry/interruption and atomic receipt retry/conflict. Bind serializer limits and applicable sensitivity/policy versions; registration is not vendor qualification.

## WA-R071 — Purpose-specific Location facts and disclosure — implementation obligations

Qualify the owner/Location WA-R071 bridge with denied/unavailable/mismatched facts, policy/source change, concurrent revocation versus old allow and bounded response validity. Assert exact fields never enter Search, generic events, Notification or telemetry. Activate only after relevant field serializer, numerical policy and legal/provider evidence qualify.

## WA-R072 — Hiring compatibility and forward migration stewardship — implementation obligations

Submit canonical reference/history constraints before backfill. Reconcile legacy resumeUrl/view relations from proven owner IDs with idempotent receipts and ambiguity report; compare owner reads before cutover. Defer physical tables/indexes to migration integration. Do not baseline, reset, deploy or remove columns while database D provenance/preservation remains unresolved.


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `candidate_application_resume_privacy` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`submitJobApplication / getJobApplicationDetail / requestResumeAccessGrant / recordJobApplicationView`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Qualify Interview lifecycle input only if optional owner-governed stage handling is enabled. Candidate remains the application-stage owner; Interview events never assign a stage directly, and disabled optional automation has no effect.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.

## WA-R078 — Bilateral qualification sequence

Commit the narrow Track command intent with Candidate profile creation and retain retry/reconciliation state; same-month usage never resets. Follow the owner architecture and WA-R078 in `context/reconciliation/platform-architecture-rulings.md`. Qualify its named stale-source, wrong-scope, retry/conflict, unavailable and privacy cases on both sides before activation. External policy/provider and database prerequisites remain separate; no interface is frozen by this appendix.

## WA-R080 — Bilateral qualification sequence

Expose both named enumerators for CandidateProfile; revalidate assignment/discovery generation without enabling discovery or disclosing resumes. Follow the owner architecture and WA-R080 in `context/reconciliation/platform-architecture-rulings.md`. Qualify its named stale-source, wrong-scope, retry/conflict, unavailable and privacy cases on both sides before activation. External policy/provider and database prerequisites remain separate; no interface is frozen by this appendix.
