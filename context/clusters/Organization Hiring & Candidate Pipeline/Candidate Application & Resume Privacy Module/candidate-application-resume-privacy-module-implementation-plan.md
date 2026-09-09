# Candidate Application & Resume Privacy Module Implementation Plan

> **Module ID:** `candidate_application_resume_privacy`  
> **Module:** Candidate Application & Resume Privacy Module  
> **Primary Cluster:** `CL-06 Organization Hiring & Candidate Pipeline`  
> **Repository target:** `context/modules/candidate_application_resume_privacy/implementation-plan.md`  
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

- authenticated actor context / `resolveAuthenticatedActor`;
- Role / Authority decision interface / `authorizeResourceAction`;
- Prisma migration/transaction layer;
- runtime validation standard;
- canonical idempotency primitive;
- aggregate locking / optimistic concurrency primitive;
- transactional outbox/inbox;
- reliable queue/retry/dead-letter infrastructure;
- structured logging/request/correlation IDs;
- Audit API including `recordSensitiveAccess`;
- RLS infrastructure and policy-test harness.

### Hard cross-Module interfaces by feature

| Dependency | Required for |
|---|---|
| Organization Hiring owner facts / Job eligibility context | application submission, recruiter reads, resume authorization |
| Job Compliance / public Job state contract | production application eligibility where Cluster policy requires it |
| Track `resolveEntitlement` + `consumeMeteredEntitlement` | Feature 05 application quota, Feature 09 perks |
| Trust requirement/readiness API | verified-only application gates |
| ComplianceHold evaluation | application/transition/access gates as approved |
| Media validation/scan/attach/grant/signed URL APIs | Features 02–04 and 08 |
| Search projection refresh/removal contract | Feature 09, privacy integration |
| Notification request contract | application lifecycle effects |
| Messaging `ensureContextThread` | optional application conversation effect |
| Privacy target protocol | Feature 10 |
| Job Interview application-context contract | Feature 10 integration handoff |

### Interfaces that may be contract-stubbed initially

Before the corresponding integration feature, a neighboring owner may be represented by a versioned test fixture if its production implementation does not yet exist. The fixture must match the approved public contract and may not become a Candidate-local substitute implementation.

### Architecture blockers

Production implementation must respect these blockers:

- **U-CL06-08:** CandidateCategory/CandidateTag attach/detach persistence owner.
- **U-CL06-09:** `CandidateProfile.resumeUrl`, `trustScore`, `verifiedAt`, `verificationExpiresAt` semantics.
- **U-CL06-10:** candidate visibility/search participation.
- **U-CL06-11:** JobApplication transition/event semantics.
- **U-CL06-12:** JobApplicationViewEvent/view-summary semantics.
- **U-CL06-13:** ResumeAccessLog semantics and raw extracted-text retention/encryption.
- **U-CL06-17:** malformed Prisma relation placement around JobApplication and JobApplicationViewEvent.
- **U-CL06-04:** Organization ATS commercial entitlement if monetized applicant tracker/resume viewer/candidate search is enabled.
- **U-CARP-01:** CandidateSearchProjection cardinality/versioning.
- **U-CARP-02:** parse retry provenance.
- **U-CARP-03:** candidate/application media-role vocabulary.

A feature may implement safe non-production scaffolding around an unresolved area only when the behavior remains disabled/fail-closed and the unresolved question is not encoded as de facto policy.

---

# Phase 1 — Contract and Source-of-Truth Foundation

## 01 Candidate Module Contracts and Schema Integrity

### Objective

Establish the Candidate Application module boundary in code, stabilize owner-specific public contracts, and make the current Candidate-related Prisma schema structurally valid without silently resolving business-semantic blockers.

### Observable Result

The codebase has a Candidate Application module shell with public command/query/event/privacy contracts, runtime schemas, owner repositories limited to Candidate-owned records, and a Prisma schema that parses/migrates cleanly around `JobApplication` and `JobApplicationViewEvent` after U-CL06-17 verification.

### Cluster Build-Plan Link

Preparatory slice for CL-06 Phase 2 Features **04–08**; directly resolves the technical prerequisite named by **U-CL06-17** before those migrations.

### Dependencies

- root module/folder conventions;
- runtime validation standard;
- Prisma migration tooling;
- canonical shared operation contracts;
- CL-06 public-interface table;
- architecture confirmation for the exact U-CL06-17 relation correction.

### In Scope

- create the Module folder structure required by `module-architecture.md`;
- define public DTOs for CandidateProfile, JobApplication, resume access, projection, view insights, and privacy executor;
- define public command/query names without implementing all business behavior yet;
- define owner repository interfaces that access only Candidate-owned tables;
- verify/fix misplaced `jobApplicationViewEvents` and `organizations` relation lines in Prisma once U-CL06-17 is confirmed as structural defect;
- add schema parsing/migration tests;
- isolate/mark non-authoritative fields (`resumeUrl`, verification-looking fields) in code so no feature uses them as source truth before U-CL06-09;
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
- proposed `JobApplicationViewEvent` mapping only after U-CL06-17 repair, without activating U-CL06-12 semantics.

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
enumerateSubjectData
executePrivacyInstruction
```

No consumer is allowed to import Candidate repositories instead of these contracts.

### Shared Operations Used

- `executeIdempotentCommand` — canonical owner: platform application infrastructure; used for future command contract shape. Do not create `candidateIdempotency.ts`.
- `withOptimisticConcurrency` — canonical owner: shared persistence; establish expected-version DTO pattern. Do not hand-roll stale-update logic.
- `publishDomainEvent` — canonical owner: platform outbox; establish event envelope types. Do not implement fire-and-forget local events.
- `returnDecisionResult` — Proposed shared contract; define compatibility only, do not treat its policy as approved generic readiness truth.

### Domain Logic

- no business transition logic beyond confirmed schema invariants;
- mark CandidateProfile `resumeUrl`, `trustScore`, `verifiedAt`, and `verificationExpiresAt` as forbidden authority fields in services;
- enforce one owner-repository boundary;
- define CandidateProfile→User and JobApplication→CandidateProfile/Job relationship DTOs.

### Authorization / Compliance

No end-user behavior is enabled. Public contracts include actor/action context so later implementations cannot omit authentication/authorization.

### Database / Transaction Behavior

- schema must parse after relation repair;
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

- schema defect unresolved → migration generation remains blocked;
- ambiguous ownership → no code path created;
- contract incompatibility with existing root standards → update context before implementation.

### Tests

- Prisma schema parse/generate/migration dry-run;
- repository ownership lint/import tests if supported;
- public DTO runtime-schema tests;
- no forbidden direct field used as verification/resume authority;
- no cross-module repository import in Candidate module.

### Documentation Updates

- update this Module architecture if U-CL06-17 or any field semantics are formally settled;
- record any new public contract naming decision;
- update progress tracker.

### Acceptance Criteria

- Candidate-related Prisma relations are syntactically/structurally valid;
- all Candidate repositories are owner-local;
- no direct cross-domain write path exists;
- unresolved fields are fenced from authority logic;
- public contracts compile and validate.

### Exit Gate

PASS only if Prisma generation/migration rehearsal succeeds for the repaired area, public contracts/runtime schemas compile, no unresolved business ruling was encoded, no cross-domain repository shortcut exists, and typecheck/lint/unit/schema checks pass.

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
- `resolveAuthenticatedActor`;
- `authorizeResourceAction` / candidate ownership policy;
- Media `validateUploadedFile`, `scanFileForMalware`, `attachValidatedMedia` contracts;
- U-CL06-09 resolved before production uses any overlapping direct/projection fields;
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

- `resolveAuthenticatedActor` — Identity; resolve User actor. Local policy: CandidateProfile belongs to that User. Prohibited duplicate: `currentCandidateUser.ts`.
- `authorizeResourceAction` — Role / Authority; authorize profile actions. Local policy: ownership/resource facts. Prohibited duplicate: local generic permission engine.
- `executeIdempotentCommand` — platform; CandidateProfile creation and media attach commands. Local policy: semantic command key. Prohibited duplicate: local idempotency table.
- `withOptimisticConcurrency` — shared persistence; profile edits. Local policy: stale edit behavior.
- `validateUploadedFile` / `scanFileForMalware` — Media; file safety. Local policy: whether the validated asset may be used as candidate media. Prohibited duplicate: resume/file validator.
- `attachValidatedMedia` — context owner + Media contract; persist CandidateProfileMedia after ready/valid result. Prohibited duplicate: direct storage/object mutation.
- `publishDomainEvent` — outbox; profile/media change events. Local policy: event meaning/payload.

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

If U-CL06-09 or CandidateProfile transition policy is resolved during this feature, update `module-architecture.md` first and record migration/deprecation behavior.

### Acceptance Criteria

- CandidateProfile works as applicant identity;
- one User cannot create duplicate profiles;
- private Media attaches only through Media contract;
- no legacy field authorizes resume/verification behavior;
- unauthorized cross-user access fails.

### Exit Gate

PASS only if candidate identity and private media-context workflows work end-to-end, RLS/server authorization agree, no public resume URL is introduced, no verification truth is duplicated, and typecheck/lint/unit/integration/authorization/E2E checks pass.

---

## 03 Secure Resume Attachment and Parse Request

### Objective

Allow a CandidateProfile/application context to attach a Media-owned private resume/CV and create one durable parse request only after the asset is ready and scan-clean.

### Observable Result

A PDF/DOCX resume uploaded under an approved resume context can be attached and moved to `ResumeParseResult.status=pending`; invalid, non-ready, suspicious, infected, or cross-owned media cannot enter the parse workflow.

### Cluster Build-Plan Link

Supports the first half of CL-06 Feature **04 CandidateProfile and Secure Resume Intake**.

### Dependencies

- Features 01–02;
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

- Media `validateUploadedFile`, `scanFileForMalware`, `attachValidatedMedia` — verify file policy/safety; no local MIME/malware code.
- `executeIdempotentCommand` — one logical attach/parse request.
- `enqueueReliableJob` — durable parse job; no local queue framework.
- `publishDomainEvent` — `resume.parse_requested` after local record exists.

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

Completes CL-06 Feature **04 CandidateProfile and Secure Resume Intake**.

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

- `enqueueReliableJob` — durable worker;
- `executeRetryWithBackoff` — transient retries;
- `executeIdempotentCommand` — retry command if exposed;
- Ops logging/failure APIs — operational state only;
- `publishDomainEvent` — completed/failed facts.

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

# Phase 3 — Application Eligibility, Quota, and Candidate Self-Service

## 05 Atomic Application Eligibility and Submission

### Objective

Allow a CandidateProfile to submit exactly one application to an eligible Job without exceeding Track application limits under concurrent/retried requests.

### Observable Result

The apply flow returns a stable eligibility decision, creates one `JobApplication(status=submitted, stage=new_)` only when all gates pass, consumes the Track allowance exactly once for the logical submission, and produces a durable receipt/event.

### Cluster Build-Plan Link

Implements the Candidate-owned core of CL-06 Feature **05 Atomic Application Eligibility, Quota, and Submission**.

### Dependencies

- Features 01–04 as applicable;
- Organization Hiring `getJobApplicationEligibilityContext`;
- Track `resolveEntitlement` + `consumeMeteredEntitlement`;
- Trust `resolveVerificationRequirements` + `evaluateVerificationReadiness`;
- `evaluateComplianceHold`;
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

- `resolveAuthenticatedActor` — candidate actor.
- `authorizeResourceAction` — candidate owns CandidateProfile/action.
- `evaluateComplianceHold` — stop-sign decision; no local blocked flag.
- `resolveEntitlement` — inspect application allowance.
- `consumeMeteredEntitlement` — atomically consume allowed quantity/usage receipt.
- `resolveVerificationRequirements` / `evaluateVerificationReadiness` — verified-only gate.
- `executeIdempotentCommand` — logical submission identity.
- `acquireAggregateLock` / transaction primitive — application/quota race.
- `publishDomainEvent` — `application.submitted`.
- `requestNotification` — downstream delivery.
- `ensureContextThread` — optional Messaging handoff, never local Thread write.

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
- `transitionLifecycleState` — plumbing only; local withdrawal graph remains Candidate-owned;
- `withOptimisticConcurrency` — stale withdrawal race;
- `publishDomainEvent` — `application.withdrawn`;
- `requestNotification` — safe candidate/org notice.

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
- U-CL06-17 schema repair;
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

- `resolveAuthenticatedActor`;
- `authorizeResourceAction` — org-scope authority;
- owner-facts query from Organization Hiring;
- `transitionLifecycleState` — shared plumbing, Candidate-owned graph;
- `withOptimisticConcurrency` / `acquireAggregateLock` — stale/concurrent pipeline mutations;
- `publishDomainEvent`;
- `appendAuditEvent` when root policy requires;
- `requestNotification`.

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
- Audit `recordSensitiveAccess`;
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

- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- Organization owner facts;
- Media readiness query;
- `manageTemporaryAccessGrant` — Media/shared grant mechanism;
- `issueSignedMediaUrl` — Media;
- `recordSensitiveAccess` — Audit;
- `executeIdempotentCommand` — access request replay;
- shared IP hashing/minimization primitive;
- `appendAuditEvent` where policy requires.

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
- Track `resolveEntitlement`;
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

- `buildSourceProjection` — shared pattern, Candidate local implementation;
- `resolveEntitlement` — Track boost/view perk;
- `requestSearchProjectionRefresh` — Search public interface;
- `enqueueReliableJob` / retry — projection work;
- `publishDomainEvent` / event dedupe;
- Privacy protocols for hide/erase;
- `withOptimisticConcurrency` — projection version race.

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
- optional `ensureContextThread` after application commit;
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

- `queryOwnerFacts` pattern — Candidate exposes minimal owner facts, no universal repository;
- `publishDomainEvent` / `deduplicateDomainEvent`;
- `requestNotification`;
- `ensureContextThread`;
- `recordSensitiveAccess` via resume review path;
- `executeIdempotentCommand` for externally requested owner mutations.

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
- externally requested Candidate command uses idempotency key and expected version.

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
- Privacy `enumerateSubjectData`, `executePrivacyInstruction`, `evaluateRetentionRequirement` protocol;
- Media deletion/revocation contract;
- Search removal contract;
- Audit/Ops;
- U-CL06-13 raw-text retention resolved before destructive production execution;
- approved hiring-record retention rules for records to be retained/anonymized.

### In Scope

- `enumerateSubjectData` implementation;
- `executePrivacyInstruction` implementation;
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

- `enumerateSubjectData`;
- `executePrivacyInstruction`;
- owner retention-facts response;
- export contribution contract.

### Shared Operations Used

- `enumerateSubjectData` — Privacy protocol, local implementation;
- `executePrivacyInstruction` — Privacy protocol, local implementation;
- `evaluateRetentionRequirement` — owner facts + Privacy exemption lifecycle;
- `anonymizePersonalFields` — shared mechanism with Candidate field map;
- `requestSearchProjectionRefresh`/removal — Search;
- Media deletion/revocation owner commands;
- `appendAuditEvent` for destructive execution where required;
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

The Candidate path works with real interfaces or versioned fixtures for Identity, Role, Organization Hiring, Job Compliance, Track, Trust, Holds, Media, Search, Audit, Notification, Messaging, Privacy, Ops, and Job Interview; unavailable neighbors never trigger permissive fallback or direct DB shortcuts.

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
CandidateProfile → private resume → parse → application
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
Job Compliance/public Job state → application availability as required
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
| 2 | Candidate Identity and Secure Resume Intake | 02–04 |
| 3 | Application Eligibility, Quota, and Candidate Self-Service | 05–06 |
| 4 | Recruiter Pipeline and Sensitive Resume Access | 07–08 |
| 5 | Candidate Search Projection and Entitlement-Gated Perks | 09 |
| 6 | Cross-Module Hiring Handoffs | 10 |
| 7 | Privacy, Retention, and Cross-Cluster Contract Proof | 11–12 |
| 8 | Hardening and Production Verification | 13 |

**Total numbered features: 13.**

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
