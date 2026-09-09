# Candidate Application & Resume Privacy Module Architecture

> **Module ID:** `candidate_application_resume_privacy`  
> **Module name:** Candidate Application & Resume Privacy Module  
> **Module type:** `domain_compliance_hybrid`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-06 Organization Hiring & Candidate Pipeline`  
> **Repository target:** `context/modules/candidate_application_resume_privacy/module-architecture.md`  
> **Document status:** implementation-grade Module architecture; Proposed Rulings and Unresolved Decisions are explicitly non-binding until approved  
> **Audience:** coding agents, developers, reviewers, maintainers, security/privacy reviewers, and architects  
> **Update rule:** update this file whenever a binding Module ownership boundary, lifecycle rule, public contract, privacy rule, compliance gate, or material schema meaning changes. Build progress must not silently redefine this architecture.

---

## 1. Module Header

This document defines the stable internal architecture of `candidate_application_resume_privacy`.

It is subordinate to the root Workin Ants architecture, source-of-truth rules, code standards, Canonical Shared Operations Architecture, and CL-06 Cluster architecture. It is more specific than the Cluster architecture for behavior that is genuinely internal to this Module, but it cannot override root or confirmed cross-Module ownership.

### Evidence-status vocabulary

- **Confirmed** — directly supported by current Workin Ants registry, schema, glossary/compliance inventory, Canonical Shared Operations, or CL-06 architecture.
- **Reasonable inference** — strongly implied by confirmed workflow/data evidence but not itself an approved lifecycle or schema ruling.
- **Proposed Ruling** — a necessary architectural choice that must be approved before code, migrations, or production behavior depend on it.
- **Unresolved Decision** — evidence establishes a gap or conflict but does not support a safe final choice.

The executable Prisma schema is concrete data-model evidence, but malformed relation placement or fields that conflict with stronger source-of-truth rules are not automatically authoritative business semantics.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own the applicant-side formal-hiring domain: CandidateProfile identity, JobApplication lifecycle, application attachment meaning, non-decisional resume parsing results, contextual resume authorization/proof, application-view facts, and the privacy-safe source projection used for candidate search.

### Goal

Allow a `CandidateProfile` to apply to an Organization-posted `Job` and participate in a recruiter pipeline while preserving four boundaries:

1. candidate identity is not base `User` identity;
2. application truth is not Organization Hiring or Job Interview truth;
3. resume business authorization is not file-storage or signed-URL truth;
4. search and subscription perks remain derived/external policy rather than local booleans.

### Transformation

```text
authenticated User / CandidateProfile
+ Organization Hiring Job facts
+ Role / Authority decision
+ Track entitlement/quota decision
+ Trust Verification readiness when required
+ ComplianceHold decision
+ validated private MediaAsset references
+ application answers / cover letter

→ CandidateProfile state
→ JobApplication state and pipeline state
→ application-media context
→ ResumeParseResult metadata
→ JobApplicationViewEvent evidence when approved
→ contextual resume-access decision
→ ResumeAccessLog proof
→ CandidateSearchProjection
→ domain events / owner requests to Search, Notification, Messaging, Audit, Privacy, and Job Interview
```

### Why this is a separate Module

This Module owns a coherent source-of-truth boundary that combines formal applicant lifecycle with privacy-sensitive resume behavior. Moving it into Organization Hiring would let the hiring entity own candidate truth; moving it into Media would turn file mechanics into hiring authorization; moving it into Search would make projection execution own private source data; moving it into Job Interview would blur application and interview lifecycles. The boundary therefore exists to keep applicant truth and resume-use policy authoritative in one place without absorbing the rails it consumes.

---

## 3. Owned Truth

### Confirmed owned records and meanings

| Record / enum | Ownership | Plain-English meaning |
|---|---|---|
| `CandidateProfile` | Confirmed | The applicant identity attached one-to-one to a base User for formal Jobs. |
| candidate use of `ProfileStatus` | Confirmed use; shared enum definition is external/structural | The lifecycle state of a CandidateProfile. This Module owns what the shared statuses mean for candidates. |
| `JobApplication` | Confirmed | One CandidateProfile's formal application to one Job. |
| `JobApplicationStatus` | Confirmed | Candidate-facing application outcome/state vocabulary. |
| `JobApplicationStage` | Confirmed | Organization-facing internal pipeline vocabulary, but mutations remain owned here. |
| `JobApplicationMedia` | Confirmed | The business-context link between a JobApplication and a MediaAsset. |
| `CandidateProfileMedia` | Confirmed contextual ownership | The business-context link between a CandidateProfile and a MediaAsset; Media still owns file mechanics. |
| `ResumeParseResult` | Confirmed | The normalized result of extracting text/metadata from one application-attached resume asset. It is not a hiring recommendation. |
| `ResumeParseStatus` | Confirmed | Parsing execution status vocabulary. |
| `ResumeAccessLog` | Confirmed | Resume-domain access proof tied to application, media, viewer, organization, and reason. Exact issuance-vs-read semantics remain unresolved. |
| `ResumeAccessReason` | Confirmed | Hiring-purpose vocabulary for resume access: `application_review`, `candidate_search`, `interview_review`, `admin_review`, `other`. |
| `CandidateSearchProjection` | Confirmed | Privacy-safe source projection that Search may consume; it is not raw resume truth and not a Typesense record. |
| `CandidateSearchProjectionStatus` | Confirmed | Source-projection lifecycle vocabulary: `draft`, `active`, `hidden`, `erased`, `disabled`. |

### Proposed owned record

| Record | Ruling |
|---|---|
| `JobApplicationViewEvent` | **Proposed Ruling U-CL06-12:** Candidate Application owns this append-only application-view fact. `JobApplication.viewedAt` and `status=viewed` are summary/first-view projections rather than competing event truth. This is not binding until U-CL06-12 is approved. |

### Contextual taxonomy responsibility

`CandidateCategory` and `CandidateTag` are not treated as unambiguously owned persistence here. Taxonomy & Classification owns controlled vocabulary and classification semantics. Candidate Application owns the business meaning of classifying a CandidateProfile. Exact attach/detach persistence ownership remains **U-CL06-08 unresolved** and must be settled before code placement creates a competing write path.

### Source-of-truth rules

- `CandidateProfile` is applicant identity; `User` is base account identity.
- `JobApplication` is application truth; Organization Hiring may consume it but does not mutate it directly.
- `ResumeParseResult` is parser output truth; it does not decide candidate quality, ranking, screening, or eligibility.
- `ResumeAccessLog` is resume-domain proof; it does not replace `MediaAccessEvent` or `AccessAuditLog`.
- `CandidateSearchProjection` is the source-owned sanitized search input; Typesense is rebuildable external projection.
- Track records are commercial policy/usage truth; this Module does not own local quotas, boosts, or premium state.
- `VerificationCheck` is screening truth; `TrustBadge` is display; CandidateProfile verification-looking fields are not authoritative.

### Module-owned policies and invariants

This Module owns:

- when a CandidateProfile is usable for candidate actions;
- when an application may be created, withdrawn, or transitioned after external gates are composed;
- one-application-per-Job semantics for a CandidateProfile;
- the local meaning of application status and stage;
- which ready/clean MediaAssets may be attached as candidate/application documents;
- when resume parsing may start and what normalized output is allowed to mean;
- contextual resume authorization after Role / Authority and owner facts are supplied;
- privacy shaping of applicant/recruiter reads;
- candidate source-projection allowlists and redaction;
- how this Module executes Privacy instructions against its own records.

---

## 4. Explicit Non-Ownership

This Module must not own or recreate the following.

| Adjacent owner | Truth that remains external | What must not appear here |
|---|---|---|
| Identity & Access | User authentication, sessions, MFA/step-up, account recovery | local current-user/session system, candidate auth table, candidate MFA state |
| Role / Authority | permission interpretation | `canRecruiterViewResume` role engine, local org-role policy, frontend-only permission checks |
| Organization Hiring | Organization, OrganizationMember row/role assignment, Job lifecycle and Job facts | Job writes, Organization membership writes, recruiter-role interpretation |
| Job Compliance | posting rules/checks/findings/disclosure decision | salary/EEOC/fair-chance scanner or Job publication policy |
| Track Subscription & Entitlement | plan, subscription, entitlement, usage event/counter, boost/perk truth | `isPremiumCandidate`, local quota counter, search-boost boolean, application-view entitlement flag |
| Trust Verification / Screening | VerificationRequirement, VerificationCheck, TrustBadge issuance/revocation, adverse-action workflow | `backgroundPassed`, local verification status, trust score as truth |
| Media / File Access | MediaAsset, upload/validation/scan/storage lifecycle, MediaAccessGrant, MediaAccessEvent, signed URL mechanics | R2 client, MIME validator, malware scanner, presigned URL signer, generic access-grant table |
| Search / Public Visibility | SearchUpsertEvent, Typesense adapter, indexing, reconciliation, search query execution | direct Typesense client, SearchUpsertEvent clone, index worker |
| Admin Review / Compliance Hold | reusable ComplianceHold lifecycle | candidate/application `blocked` flags or local hold tables |
| Audit / Event Ledger | generic AuditEvent and AccessAuditLog | second generic audit/access ledger |
| Notification | channel routing, provider delivery, retries | email/SMS/push provider code |
| Messaging | Thread, ThreadParticipant, Message lifecycle | local chat/thread implementation |
| Job Interview | JobInterview lifecycle, interview participants/events where ruled | interview scheduling state, video room state |
| Video Session | JobInterviewVideoRoom and video provider mechanics | Daily/Agora room clients or tokens |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob, DataErasureTarget, DataRetentionExemption, orchestration | local privacy-request workflow or local exemption registry |
| Observability / Ops | IntegrationFailure, SystemEvent, QueueJob operational truth | business lifecycle derived from ops status |
| Taxonomy & Classification | controlled vocabulary and semantic validation | local tag cleaner, taxonomy copy, AI-generated taxonomy truth |

The presence of a foreign key or Prisma relation is not permission to import a neighboring repository or mutate its source tables.

---

## 5. Module Architecture Principles

1. **CandidateProfile is the applicant actor.** Candidate actions do not attach directly to User as applicant truth.
2. **One owner per application lifecycle.** Only this Module changes `JobApplication.status` and `JobApplication.stage`.
3. **External gates stay external.** Track, Trust, Holds, Job/Organization facts, and Role decisions are inputs to Candidate policy, not copied state.
4. **Private resume by default.** Resume/CV assets never use permanent public URLs.
5. **Context before credential.** Candidate authorization must succeed before Media issues a grant or signed URL.
6. **File safety before parse/read.** Resume parsing/display requires a ready and scan-clean MediaAsset.
7. **Parsing is extraction, not decisioning.** No parser output may become an automated recommendation, candidate score, rejection, or ranking decision.
8. **Search receives an allowlisted source projection.** Raw resume text is excluded by default.
9. **Commercial perks are resolved at use time.** No local premium/quota/boost/view-tracking truth.
10. **Application view, resume access, media access, and generic sensitive audit are separate facts.** Shared mechanics do not collapse evidence.
11. **Cross-Module effects are requested.** Search, Notification, Messaging, Audit, Media, Privacy, and Job Interview retain their own writes.
12. **Async work is durable.** Parsing/projection/privacy side effects use canonical queue/idempotency/observability mechanisms.
13. **No permissive fallback.** Missing dependency decisions produce deny/unavailable/review, never silent access or application creation.
14. **Unresolved schema meaning is fenced.** `resumeUrl`, verification-looking CandidateProfile fields, visibility precedence, view semantics, and raw-text retention may not be treated as settled truth before their rulings.

---

## 6. Proposed Folder / Code Structure

Follow root repository conventions if they differ. The Module-specific responsibility map is:

```text
src/modules/candidate-application-resume-privacy/
  domain/
    candidate-profile/
    job-application/
    resume/
    candidate-search/
    errors/
  application/
    commands/
    queries/
    policies/
    orchestration/
  public/
    commands.ts
    queries.ts
    events.ts
    contracts.ts
    privacy.ts
  persistence/
    candidate-profile.repository.ts
    job-application.repository.ts
    resume.repository.ts
    candidate-search-projection.repository.ts
  schemas/
    command-inputs.ts
    query-inputs.ts
    public-dtos.ts
  projections/
    candidate-search-projection.builder.ts
  workers/
    resume-parse.worker.ts
    candidate-projection.worker.ts
    privacy-executor.worker.ts
  parsers/
    resume-parser.port.ts
    pdf-resume-parser.adapter.ts
    docx-resume-parser.adapter.ts   # exact library is an implementation choice
  privacy/
    enumerate-subject-data.ts
    execute-privacy-instruction.ts
    retention-facts.ts
  ui/
    candidate-profile/
    applications/
    recruiter-pipeline/
    resume-access/
    candidate-search-settings/
  tests/
    unit/
    integration/
    contracts/
    authorization/
    concurrency/
    privacy/
    e2e/
```

Do not create `auth/`, `billing/`, `search-provider/`, `storage/`, `notifications/`, `generic-audit/`, or `queue-framework/` folders inside this Module. Shared operations remain in their canonical owners.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / UI | candidate profile forms, application forms/lists, privacy-shaped recruiter pipeline, resume-access controls, candidate search settings when approved | permission policy, signed URL generation, Search indexing, provider delivery |
| Application services | command/query orchestration, dependency calls, transaction boundaries, outbox requests | foreign source writes or provider SDK logic |
| Domain policy | CandidateProfile usability, application invariants, transition policy, resume-context authorization, projection field policy | Track/Trust/Hold/Role policy internals |
| Persistence | Prisma access only for Module-owned records and approved transactional support | neighboring Module repositories or cross-domain write shortcuts |
| Workers | resume parse, source-projection rebuild, Module privacy execution | generic queue infrastructure or Search reconciliation |
| Parser adapters | normalize PDF/DOCX extraction into Module contract | file storage/scanning, hiring recommendation logic |
| Public contracts | stable owner facts, commands, queries, events, privacy executor | universal polymorphic repository |
| Privacy | enumerate/execute candidate-owned data dispositions | PrivacyRequest/DataErasureJob orchestration or exemption lifecycle |

---

## 8. Data Model

### `CandidateProfile`

**Purpose:** applicant identity for formal hiring.

**Key relationships:** one base `User`; many `JobApplication`; candidate media joins; taxonomy joins; JobInterview references; Track/Trust relations are external truth references.

**Authoritative fields:** identity/profile fields such as headline, availability, location context, `status`; candidate ownership is `userId`.

**Constraints:** `userId` is unique, so one User has at most one CandidateProfile in the current schema.

**Concurrency:** profile edits must use optimistic concurrency or equivalent stale-write protection.

**Privacy:** profile fields are subject data. Search exposure is not implied by existence.

**Conflicting fields:** `resumeUrl`, `trustScore`, `verifiedAt`, `verificationExpiresAt`, and `isVisible` have unresolved/direct-projection overlap. See U-CL06-09/10. They must not be treated as authoritative resume or verification truth before resolution.

### `CandidateProfileMedia`

**Purpose:** candidate-profile business attachment context over a MediaAsset.

**Key relationships:** composite key `(candidateProfileId, mediaId)`; Media owns file lifecycle.

**Authoritative fields:** attachment relationship, optional contextual `role`, sort order.

**Privacy:** a join row does not make the MediaAsset public.

### `JobApplication`

**Purpose:** formal application from one CandidateProfile to one Job.

**Authoritative fields:** `jobId`, `candidateProfileId`, cover letter, answers, invited flag, status, stage, lifecycle timestamps.

**Constraints:** `@@unique([jobId, candidateProfileId])` enforces one application per candidate/job pair.

**Concurrency:** submission, withdrawal, status/stage transition, and view-summary writes are conflict-sensitive.

**Retention:** cover letters and answers are personal hiring data. Erasure/retention treatment must be executed under Privacy instructions.

**Structural schema defect:** the current Prisma text places `jobApplicationViewEvents JobApplicationViewEvent[]` after the closing `}` of the model. U-CL06-17 blocks migrations touching this area until corrected/verified.

### `JobApplicationMedia`

**Purpose:** application-specific attachment relationship over a MediaAsset.

**Constraint:** composite primary key `(jobApplicationId, mediaId)`; one optional `ResumeParseResult` relation per attached media pair.

**Privacy:** attachment role is business context; Media remains storage/safety truth.

### `ResumeParseResult`

**Purpose:** normalized extraction result for one application/media pair.

**Authoritative fields:** parse status, parser name/version, extracted text/skills/metadata, failure reason.

**Constraint:** unique `(jobApplicationId, mediaId)`.

**Privacy:** `extractedText` is sensitive resume content. Encryption/retention and post-derivation persistence remain U-CL06-13 unresolved. Raw text is never sent to Search or analytics by default.

### `ResumeAccessLog`

**Purpose:** resume-domain evidence of authorized hiring-context access.

**Authoritative fields:** application/media, viewer, organization, `ResumeAccessReason`, URL expiry metadata, minimized request evidence, created time.

**Append-only expectation:** access proof is not a mutable current-state record.

**Unresolved:** current schema cannot distinguish grant issuance from actual view/download. U-CL06-13 must define exact semantics before compliance-grade production use.

### `CandidateSearchProjection`

**Purpose:** sanitized source projection that Search may index when candidate visibility/privacy permits.

**Fields:** status, skill tags, normalized titles, experience band, state-level location, remote preference, `rawResumeTextIndexed`, generated/erased timestamps.

**Invariant:** `rawResumeTextIndexed=false` by default.

**Unresolved cardinality:** the schema indexes `candidateProfileId` but does not make it unique. It therefore permits multiple projections per CandidateProfile. The architecture must decide whether this is a version-history model or whether only one current active projection may exist. See **U-CARP-01** below.

### `JobApplicationViewEvent` — Proposed owner

**Purpose:** append-only evidence that an authorized organization actor viewed a JobApplication.

**Fields:** application, viewer, organization, viewedAt, IP hash, user agent.

**Structural defect:** current schema also places an `organizations` relation line after the closing model brace. U-CL06-17 must be corrected before migration generation.

**Semantics:** ownership/view-summary relationship remains Proposed Ruling U-CL06-12.

### Candidate taxonomy joins

`CandidateCategory` and `CandidateTag` relate CandidateProfile to controlled taxonomy. Taxonomy owns vocabulary and semantic validation; exact join persistence owner remains U-CL06-08 unresolved.

---

## 9. Enums, Statuses, and Lifecycles

### CandidateProfile lifecycle

Vocabulary:

```text
draft | active | paused | suspended | archived
```

The Module owns candidate-specific interpretation of these shared statuses. The existing evidence does not define a complete transition graph.

**Proposed Ruling — conservative CandidateProfile graph:**

```text
draft → active | archived
active → paused | suspended | archived
paused → active | suspended | archived
suspended → active | archived   # only after the external blocking condition is resolved
archived → terminal             # restore requires an explicit future ruling
```

Do not implement this graph as binding until approved. External Trust or Hold state may gate transitions but does not own them.

### JobApplication status lifecycle

Vocabulary:

```text
submitted | viewed | withdrawn | rejected | accepted_offer | hired
```

Confirmed creation state: `submitted`.

**U-CL06-11 unresolved:** valid transitions, terminal states, reopening/reversal, actor ownership, and timestamp coupling are not finalized. Names that look sequential do not authorize code to assume a linear graph.

### JobApplication stage lifecycle

Vocabulary:

```text
new_ | screen | interview | offer | hired | closed
```

Confirmed creation stage: `new_`.

**U-CL06-11 unresolved:** skip/backtrack behavior, status-stage compatibility, terminal semantics, and event-history requirements must be approved before the full recruiter pipeline is implemented.

### View semantics

**Proposed Ruling U-CL06-12:**

```text
JobApplicationViewEvent = append-only view truth
JobApplication.viewedAt = first-view summary timestamp
JobApplication.status=viewed = candidate-facing summary state when first qualifying organization view occurs
```

A repeated view should append an event without repeatedly rewriting first-view history. This remains non-binding until approved.

### ResumeParseResult lifecycle

Confirmed vocabulary:

```text
pending | processing | completed | failed | skipped
```

Minimum safe progression:

```text
pending → processing → completed | failed
pending → skipped
```

Retry behavior must be idempotent and must not silently erase prior operational failure evidence. Whether a retry mutates the same row from `failed` back to `processing` or records attempt history elsewhere is an implementation/persistence ruling to document before coding if not established by the shared queue system.

### CandidateSearchProjection lifecycle

Vocabulary:

```text
draft | active | hidden | erased | disabled
```

**Proposed lifecycle mechanics:** `draft` may become `active` only after U-CL06-10 visibility/search participation is resolved; `active` may become `hidden` or `disabled`; privacy erasure may move any eligible state to `erased`; `erased` is terminal. Search indexing/removal is a downstream effect, not the lifecycle itself.

### Append-only records

`ResumeAccessLog` has no mutable lifecycle. `JobApplicationViewEvent`, if approved, is also append-only. Generic Audit and Media access records remain separate evidence.

---

## 10. Commands

| Command | Purpose | Actor/context | Preconditions | Writes | Shared/dependency operations | Side effects | Idempotency / failures |
|---|---|---|---|---|---|---|---|
| `createCandidateProfile` | create applicant identity | authenticated User | no existing CandidateProfile for User; valid input | CandidateProfile | `resolveAuthenticatedActor`, authorization/ownership check, `executeIdempotentCommand` | domain event, audit if policy requires | duplicate returns deterministic conflict/existing result |
| `updateCandidateProfile` | update candidate-owned profile fields | candidate owner | valid ownership; expected version | CandidateProfile | actor, `authorizeResourceAction`, `withOptimisticConcurrency` | projection-refresh request only when approved/relevant | stale version = conflict |
| `transitionCandidateProfileStatus` | change candidate lifecycle state | candidate/admin/system as approved | approved transition + gates | CandidateProfile.status | auth/authority, Holds where relevant, `transitionLifecycleState` | event/search effect | illegal transition = domain denial |
| `attachCandidateProfileMedia` | attach ready MediaAsset in candidate context | candidate owner | Media validated/ready; approved context | CandidateProfileMedia | `attachValidatedMedia` / Media facts | parse/projection effects only when applicable | duplicate composite key = existing relationship |
| `attachApplicationMedia` | attach ready asset to one JobApplication | candidate owner or approved workflow | application ownership; Media ready/clean for resume use | JobApplicationMedia | Media validation/access facts | parse job if resume | wrong media/context denied |
| `queueResumeParse` | request durable parse work | system/application service | JobApplicationMedia exists; Media ready and clean | ResumeParseResult pending if needed | `enqueueReliableJob`, idempotency | `resume.parse_requested` | duplicate request does not create duplicate parse truth |
| `submitJobApplication` | create one application and consume permitted quota | candidate owner | usable profile; eligible Job; no duplicate; Hold clear; Track quota; Trust readiness when required; attachments ready | JobApplication + local media links/outbox | Organization facts, `resolveEntitlement`, `consumeMeteredEntitlement`, Trust readiness, Holds, idempotency/concurrency | application event, Notification, optional Messaging | race-safe; partial Track/application outcome must reconcile |
| `withdrawJobApplication` | candidate withdraws application | candidate owner | transition allowed by U-CL06-11 | JobApplication status/timestamp | auth/authority, concurrency | event, Notification, interview reaction via event | stale/terminal state denied |
| `transitionApplicationStage` | recruiter/admin moves pipeline stage | authorized org actor | Job belongs to actor org; transition approved; expected version | JobApplication.stage and related timestamps if ruled | actor, Role/Authority, owner facts, lifecycle helper | event, Notification, Job Interview handoff | stale/illegal transition denied |
| `transitionApplicationStatus` | change candidate-facing outcome | actor allowed by policy | approved transition and relationship | JobApplication.status/timestamps | authority/concurrency | event/Notification | stale/illegal transition denied |
| `recordJobApplicationView` | append view evidence | authorized org read path | U-CL06-12 approved; application belongs to org | JobApplicationViewEvent; summary projection if ruled | authority, idempotency as request semantics require | `application.viewed` event | cross-org denied; repeated view semantics explicit |
| `requestResumeAccessGrant` | orchestrate contextual authorization then Media grant | authorized org/interview/admin context | Candidate resume decision allows; Media ready/clean; reason allowed | ResumeAccessLog only according to U-CL06-13 semantics | `authorizeResourceAction`, local `authorizeContextualResumeAccess`, `manageTemporaryAccessGrant`, `issueSignedMediaUrl`, `recordSensitiveAccess` | access event/audit correlation | no grant before allow; Media failure cannot log false success |
| `transitionCandidateSearchProjectionStatus` | control source-projection visibility | candidate/system/privacy actor | U-CL06-10 approved for activation; valid transition | CandidateSearchProjection | entitlement/Privacy facts as applicable | `requestSearchProjectionRefresh` | Search failure does not roll back source truth |
| `executePrivacyInstruction` | execute one Privacy-owned target instruction against candidate-owned data | scoped Privacy service actor | valid target/envelope; retention facts evaluated | owner records only | Privacy protocol, Media/Search deletion requests, audit/ops | execution result/event | idempotent rerun; never marks completed on partial failure |

The command names are public-contract targets, not permission for Server Actions or route handlers to implement business logic inline.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result type | Consumer must not infer |
|---|---|---|---|---|
| `getCandidateProfile` | candidate UI, Job Interview, approved owners | actor + candidate ID | source truth / privacy-shaped facts | verification readiness or searchability from local fields |
| `listCandidateApplications` | candidate UI | actor + filters/page | source read model | Organization internal pipeline details beyond approved fields |
| `getJobApplicationDetail` | candidate/recruiter/Job Interview | actor + application ID | privacy-shaped source/read model | resume access permission from possession of media ID |
| `listJobApplicants` | Organization Hiring UI | actor + Job ID + page/filter | recruiter-shaped source read model | cross-org authority or signed resume access |
| `evaluateApplicationEligibility` | submit flow, preview UI | candidate + Job + action | decision with reasons/evidence refs | Track/Trust/Hold policy by reading their tables |
| `getResumeParseResult` | candidate UI, projection worker | actor/system + application/media | parser evidence | hiring quality/recommendation |
| `authorizeContextualResumeAccess` | resume access orchestration, Job Interview review | actor, application, media, reason | contextual allow/deny decision | Media grant or signed URL exists |
| `getCandidateSearchProjection` | Search, candidate settings | candidate/version | source projection | raw resume or source profile is searchable automatically |
| `getApplicationViewInsights` | candidate UI | candidate/application + entitlement context | gated event summary/detail | entitlement ownership from view-event existence |
| `getApplicationInterviewContext` | Job Interview | application ID + requester | minimal application/org/candidate facts and interviewability decision/facts | permission to mutate application or resume |
| `enumerateSubjectData` | Privacy | subject + cursor | candidate-owned target inventory | Privacy orchestration or retention exemption creation |

### Decision-result categories

Public decisions should return stable categories such as:

```text
allow | deny | review | unavailable
```

with module-specific reason codes, evidence references, evaluated time, and source versions. The Canonical Shared Operation `returnDecisionResult` is currently a Proposed Ruling; if approved, these decisions should conform to that shared envelope without transferring policy ownership.

Recommended Module reason-code families include `candidate_profile_unusable`, `job_not_accepting_applications`, `duplicate_application`, `application_limit_reached`, `verification_required`, `compliance_hold_active`, `media_not_ready`, `media_scan_not_clean`, `resume_access_not_authorized`, `cross_organization_access_denied`, `invalid_transition`, `stale_version`, `search_visibility_unresolved`, and `dependency_unavailable`.

---

## 12. Public Module Interface

### Public commands

```text
createCandidateProfile
updateCandidateProfile
transitionCandidateProfileStatus
attachCandidateProfileMedia
attachApplicationMedia
submitJobApplication
withdrawJobApplication
transitionApplicationStage
transitionApplicationStatus
recordJobApplicationView                 # only after U-CL06-12 approval
requestResumeAccessGrant
transitionCandidateSearchProjectionStatus
executePrivacyInstruction
```

### Public queries / decisions

```text
getCandidateProfile
listCandidateApplications
getJobApplicationDetail
listJobApplicants
evaluateApplicationEligibility
getResumeParseResult
authorizeContextualResumeAccess
getCandidateSearchProjection
getApplicationViewInsights
getApplicationInterviewContext
enumerateSubjectData
```

### Emitted domain events

```text
candidate_profile.created
candidate_profile.updated
candidate_profile.status_changed
application.submitted
application.withdrawn
application.viewed                 # after U-CL06-12
application.status_changed
application.stage_changed
resume.parse_requested
resume.parse_completed
resume.parse_failed
resume.accessed                    # exact semantics follow U-CL06-13
candidate_projection.changed
candidate_privacy_execution.completed
```

Event schemas must be versioned and payload-minimized. They describe facts; consumers must not treat them as hidden cross-Module write commands.

### Privacy executor

This Module exposes the Privacy-defined `enumerateSubjectData` and `executePrivacyInstruction` protocols for its own records. Privacy remains the sole owner of the request/job/target/exemption lifecycle.

### Provider-facing interface

No external provider webhook or provider-event lifecycle is owned by this Module. Resume parsing libraries are wrapped by the internal `ResumeParserPort`; they are not Workin Ants truth.

---

## 13. Inbound Dependencies

| Owner | Interface / canonical operation consumed | Why required | Minimum data | May block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | `resolveAuthenticatedActor` | trusted User/system actor | actor ID, auth/session assurance, platform role context | yes | current-user helper/auth state |
| Role / Authority | `authorizeResourceAction` | candidate ownership, recruiter/admin actions | action, actor, resource facts | yes | org-role policy |
| Organization Hiring | `getJobApplicationEligibilityContext`, `getOrganizationHiringContext` / owner facts | Job status/visibility/Organization relation | Job ID, org ID, status/version, relationship facts | yes | Job or Organization writes |
| Job Compliance | current publication/compliance decision where application eligibility requires it | ensure application path uses an allowed Job state | decision/evidence refs | yes | compliance scanner/rules |
| Track | `resolveEntitlement`, `consumeMeteredEntitlement` | application quota, view insights, search boost | candidate track actor, entitlement key, usage receipt | yes | quota counters, premium flags |
| Trust Verification | `resolveVerificationRequirements`, `evaluateVerificationReadiness` | verified-only Job gates | target requirements, decision, evidence refs | yes | VerificationCheck/badge inference |
| Holds | `evaluateComplianceHold` | reusable stop sign | target/action, active holds/reasons | yes | local blocked flag |
| Media | `validateUploadedFile`, `scanFileForMalware`, `attachValidatedMedia`, `manageTemporaryAccessGrant`, `issueSignedMediaUrl` | private file safety/access | media ID, readiness/scan facts, access grant result | yes | storage/scanning/signing |
| Search | `requestSearchProjectionRefresh` | index/remove approved candidate projection | source projection ID/version/action | no to source write; yes to external visibility | Typesense client/index truth |
| Audit | `appendAuditEvent`, `recordSensitiveAccess` | generic audit/access proof | actor, action, sensitivity, target refs, outcome | may block according to root security policy | local AuditEvent/AccessAuditLog |
| Notification | `requestNotification` | deliver application/resume lifecycle alerts | event meaning, recipients, safe template data | no to source truth | channel/provider logic |
| Messaging | `ensureContextThread` | optional application conversation context | context ID, participant facts | no to application truth | Thread lifecycle |
| Privacy | privacy target request/result contract | legal access/export/erasure/restriction | target instruction, retention context | yes for destructive action | PrivacyRequest orchestration |
| Observability / Ops | logging/integration/job failure APIs | operational visibility | correlation/request IDs, safe error metadata | no | business status |

---

## 14. Outbound Consumers and Effects

| Consumer | What it may consume | Effect / boundary |
|---|---|---|
| Organization Hiring | applicant list/detail, application status/stage summaries, view events where permitted | renders ATS surfaces; must not mutate JobApplication tables directly |
| Job Interview | application/candidate/org facts, interviewability, resume access decision via this Module | owns JobInterview; may request application-stage change through public command/event only |
| Search | CandidateSearchProjection + source version/visibility | owns SearchUpsertEvent and Typesense; cannot reconstruct raw resume/private policy |
| Media | contextual resume allow decision | issues grant/URL and records MediaAccessEvent; does not decide hiring purpose |
| Audit | resume/application sensitive access facts | records generic AccessAuditLog; does not replace ResumeAccessLog |
| Notification | candidate/application business events + safe payload intent | delivers over channels; delivery state is external |
| Messaging | application context facts | creates/reuses Thread; does not own application state |
| Privacy | target enumeration and execution results | owns orchestration/exemptions; cannot directly rewrite candidate tables |
| Track | qualifying application-use trigger and IDs | owns TrackUsageEvent/Counter; does not own JobApplication |
| Ops | parse/projection/privacy operational failures | records diagnostic state only |

---

## 15. Canonical Shared Operations Used

The current Canonical Shared Operations Architecture uses canonical operation names as identifiers; the supplied current CL-06 source explicitly notes no stable SH-### IDs in that resource. Do not invent IDs.

| Canonical operation | Classification / owner | Why used here | Invocation point | Local policy that remains here | Expected result | Prohibited duplicates |
|---|---|---|---|---|---|---|
| `resolveAuthenticatedActor` | canonical shared capability / Identity | trusted actor | every protected command/query | attempted candidate action | typed actor context | `candidateAuth.ts`, `currentCandidateUser.ts` |
| `authorizeResourceAction` | cross-cutting capability / Role | permission decision | before protected candidate/org/admin action | resource/action facts | allow/deny + reason/evidence | `canRecruiterViewResume.ts`, local org-role engine |
| `queryOwnerFacts` | proposed shared contract / each owner | minimal cross-module facts | Organization/Job/interview relationships | exposed candidate facts | owner-specific DTO | universal repository |
| `resolveEntitlement` | commercial-policy capability / Track | quota/perk/boost | eligibility, view insights, projection boost | effect on candidate action | typed effective entitlement | `isPremiumCandidate`, boost boolean |
| `consumeMeteredEntitlement` | cross-cutting capability / Track | atomic application usage | application commit | what counts as submission | usage receipt/counter evidence | `applicationQuotaCounter` |
| `evaluateComplianceHold` | cross-cutting capability / Holds | stop-sign gate | submit/transition/sensitive actions as applicable | local response to hold | active hold refs/reasons | local blocked flags |
| `resolveVerificationRequirements` | Module public interface / Trust | know required candidate checks | application eligibility | action-specific requirement use | requirement refs | local background-check rule |
| `evaluateVerificationReadiness` | Module public interface / Trust | verified-only decision | submit/advancement | block/allow behavior | readiness decision/evidence | TrustBadge inference |
| `returnDecisionResult` | proposed shared contract | consistent decision envelope | public decisions | reason-code policy | allow/deny/review/unavailable | generic readiness engine |
| `executeIdempotentCommand` | platform primitive | retry-safe mutations | create/submit/access requests | semantic command identity | prior/new result | local idempotency tables/helpers |
| `acquireAggregateLock` | platform primitive | serialize conflict-sensitive actions | quota/submission/transitions | lock key | lock/transaction scope | in-memory mutex |
| `withOptimisticConcurrency` | platform primitive | reject stale updates | profile/application/projection transitions | merge/retry policy | conflict/current version | ad-hoc timestamp checks |
| `transitionLifecycleState` | shared mechanism / separate policy | state-machine plumbing | lifecycle commands | transition graph/invariants | updated owner state | global hiring state machine |
| `publishDomainEvent` | platform event/outbox | reliable integration facts | same source transaction | event names/payloads | outbox record | fire-and-forget events |
| `deduplicateDomainEvent` | platform inbox | consumer replay safety | inbound event handler | handler side effect | processed claim | ad-hoc event booleans |
| `enqueueReliableJob` | platform queue | parse/projection/privacy async work | after authoritative commit | job business meaning | durable job ref | local queue framework |
| `executeRetryWithBackoff` | platform queue/retry | transient retry | worker technical failure | retryability classification | retry/dead-letter result | bespoke retry loops |
| `validateUploadedFile` | Media capability | file safety | upload intake | candidate context eligibility | validation result | local MIME/file-size validator |
| `scanFileForMalware` | Media capability | malware gate | before attach/parse/read | business use after clean result | scan result | resume malware scanner |
| `attachValidatedMedia` | shared contract between context owner + Media | attach ready asset | candidate/application media command | role/context meaning | attachment facts | direct storage mutation |
| `manageTemporaryAccessGrant` | Media/shared grant mechanism | short-lived access | after resume allow decision | resume context/reason | grant with TTL/revocation | local grant table |
| `issueSignedMediaUrl` | Media capability | private file credential | after contextual allow + grant | none beyond resume policy | short-lived URL/credential | `ResumeSignedUrlService` |
| `recordSensitiveAccess` | Audit capability | generic sensitive access proof | resume/admin restricted access | sensitivity/reason supplied here | AccessAuditLog ref | `CandidateAccessAudit` |
| `appendAuditEvent` | Audit capability | significant generic audit | lifecycle/admin/privacy actions | what is auditable | AuditEvent ref | local generic audit table |
| `buildSourceProjection` | shared pattern; source owner implements | sanitized candidate projection | parse/profile/privacy change | allowlisted fields | CandidateSearchProjection | Search reconstructing resume |
| `requestSearchProjectionRefresh` | Search public interface | upsert/remove search doc | source projection change | source inclusion/visibility | accepted refresh request | direct Typesense client |
| `requestNotification` | Notification capability | delivery request | after committed domain fact | event meaning/safe payload | notification request ref | email/SMS/push code |
| `ensureContextThread` | Messaging public interface | application thread | after application commit if workflow enables | context/participant facts | Thread ref | local Thread creation |
| `enumerateSubjectData` | Privacy protocol / data owner implementation | data inventory | privacy request processing | candidate schema map | target inventory | local privacy crawler |
| `executePrivacyInstruction` | Privacy protocol / owner implementation | apply disposition | Privacy worker call | erase/anonymize/retain mapping | target result | local PrivacyRequest workflow |
| `evaluateRetentionRequirement` | Privacy protocol | retention facts | before destructive action | candidate hiring retention facts | required/reason/minimum fields | local exemption table |
| `anonymizePersonalFields` | shared privacy mechanism | safe field scrubbing | approved anonymization | exact field map | anonymization result | global blind scrubber |

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Truth affected | Why local |
|---|---|---|---|---|---|
| `evaluateApplicationEligibility` | compose candidate-owned policy with external Job/Track/Trust/Hold/Media decisions | candidate, Job facts, action | Candidate decision | none | the action-to-gate composition belongs to application policy |
| `evaluateCandidateProfileUsability` | decide whether CandidateProfile state permits an action | profile + action | local decision | none | candidate lifecycle meaning is local |
| `validateApplicationTransition` | enforce U-CL06-11 approved status/stage graph | current state, target, actor facts | allow/deny | none | lifecycle policy is owned here |
| `authorizeContextualResumeAccess` | decide whether a specific resume may be used by this viewer for this reason | actor, application, media, org, reason | allow/deny + evidence refs | none | hiring-purpose authorization is not Media policy |
| `recordResumeAccess` | write resume-domain proof per U-CL06-13 | approved access outcome | ResumeAccessLog ref | ResumeAccessLog | separate domain proof |
| `normalizeResumeParseResult` | map parser/library output into allowed metadata | parser output | normalized extraction | ResumeParseResult | parser meaning and non-decision boundary are local |
| `buildCandidateSearchProjection` | create allowlisted source projection | profile + approved parse metadata | projection | CandidateSearchProjection | Search must not reconstruct private truth |
| `shapeRecruiterApplicationView` | minimize data exposed to authorized org actors | application/candidate facts | recruiter DTO | none | candidate privacy shaping is local |
| `shapeCandidateApplicationView` | expose candidate-facing status without overexposing internal pipeline | application | candidate DTO | none | candidate-facing privacy/product contract is local |
| `reconcileApplicationUsageOutcome` | reconcile Track receipt with application result after retry/partial failure | application/idempotency/usage refs | reconciled result | JobApplication only when local repair is required | cross-owner outcome meaning is application-specific |
| `applyCandidatePrivacyDisposition` | execute approved erase/anonymize/restrict action | Privacy instruction | owner result | candidate-owned records | owner knows relational/privacy invariants |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Lifecycle plumbing vs lifecycle policy:** `transitionLifecycleState` may be shared; CandidateProfile/JobApplication transition graphs remain here.
2. **Application view vs commercial usage:** `JobApplicationViewEvent` records the view; `TrackUsageEvent.application_view_tracked` is commercial usage proof if Track requires it.
3. **Resume access vs media access:** `ResumeAccessLog` records hiring context; `MediaAccessGrant/Event` record generic file mechanics; `AccessAuditLog` records generic sensitive access.
4. **Source projection vs Search projection:** `CandidateSearchProjection` remains Candidate-owned; SearchUpsertEvent/Typesense remain Search-owned.
5. **Parser worker vs queue truth:** `ResumeParseResult` is business/parser state; QueueJob is operational state.
6. **Idempotency mechanism vs command identity:** platform idempotency is shared; this Module defines keys such as submit-application and resume-access request semantics.
7. **Hashing/IP minimization vs evidence meaning:** shared hashing may be used; this Module decides which events require minimized client evidence.
8. **Privacy orchestration vs owner execution:** Privacy owns request/job/exemption; this Module owns candidate-record mutation in response.

---

## 18. Authentication and Authorization

Every protected entry point begins with `resolveAuthenticatedActor`.

### Candidate ownership facts

- CandidateProfile ownership is `CandidateProfile.userId == actor.userId`.
- Candidate application self-service requires the actor to own the application’s CandidateProfile.

### Organization/recruiter facts

For recruiter/admin application operations, this Module supplies or consumes:

```text
JobApplication → Job → Organization
viewer User → OrganizationMember for that Organization
requested action
```

Role / Authority interprets whether the OrganizationMember role permits the action. This Module then applies application/resume-specific policy.

### Resume authorization order

```text
resolveAuthenticatedActor
→ authorizeResourceAction
→ confirm JobApplication belongs to the Organization's Job
→ confirm requested MediaAsset is attached in the approved candidate/application context
→ confirm Media ready + clean
→ validate ResumeAccessReason and local policy
→ optional Organization ATS feature gate only after U-CL06-04 owner resolution
→ local contextual allow decision
→ Media temporary grant / signed URL
→ resume-domain + generic access proof
```

No admin/support broad bypass is assumed. Sensitive support/admin reads must use the same contextual policy plus root step-up/audit requirements where applicable.

RLS is defense in depth and must have parity tests with server authorization decisions.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying owner | Query/operation | Module action gated | Local composition policy |
|---|---|---|---|---|
| Candidate profile state | this Module | local usability decision | submit, edit, search participation | candidate status must permit action |
| Job availability | Organization Hiring | `getJobApplicationEligibilityContext` | submit application | only Jobs in an application-eligible state may accept applications |
| Job posting compliance | Job Compliance / Organization Hiring lifecycle | owner decision/facts | submit when required by Cluster policy | do not recreate compliance rules |
| Application quota | Track | `resolveEntitlement` + `consumeMeteredEntitlement` | application submission | application counts only at the approved commit point |
| Verified-only requirement | Trust Verification | `resolveVerificationRequirements`, `evaluateVerificationReadiness` | submit and/or advancement according to approved policy | do not infer from TrustBadge alone |
| ComplianceHold | Holds | `evaluateComplianceHold` | submit/transition/access where applicable | map active hold to local deny/review; no local blocked flag |
| Media safety | Media | readiness/validation/scan interfaces | attach, parse, resume access | resume requires ready + clean |
| Organization ATS feature access | owner unresolved U-CL06-04 | none until ruling | monetized resume viewer/applicant tracker/candidate search | basic MVP must not invent gate |
| Candidate search participation | local + Track/Search dependencies | U-CL06-10 decision + entitlement | projection activation / boost | no indexing until visibility/privacy semantics are approved |

---

## 20. Provider Integrations

This Module does **not** own an external provider lifecycle, webhook endpoint, webhook signature verification, or provider-event dedupe record.

### Resume parsing libraries

The Module may wrap format-specific extraction libraries behind:

```text
ResumeParserPort
  parse(input: PrivateMediaStream, metadata) → NormalizedResumeExtraction
```

The adapter may use `pdf-parse` for PDF. DOCX support is required by the current resume upload policy, but the exact DOCX library is an implementation-library choice unless root library docs bind one.

Rules:

- file bytes are obtained through Media-approved internal access, not a public URL;
- parser errors are normalized into Module-safe categories;
- raw library/provider objects do not escape the adapter;
- parser output never contains or implies a hiring decision;
- no provider credentials or webhook state are introduced for local parsing libraries;
- operational failures go to shared queue/Ops telemetry.

Direct Cloudflare R2 or Typesense clients are explicitly prohibited here even though the historical Module registry listed those technologies; current cross-Module architecture assigns those mechanics to Media and Search.

---

## 21. Events and Outbox

Owner mutations that matter outside this Module use the canonical transactional outbox.

### Event envelope expectations

Each event includes:

- stable event ID;
- event name and schema version;
- aggregate type/ID;
- aggregate/source version where available;
- occurredAt;
- correlation ID and causation ID;
- minimized actor reference when allowed;
- privacy classification;
- minimal payload required by consumers.

Do not include raw resume text, cover letter bodies, application answers, signed URLs, tokens, or unnecessary PII.

### Emission rules

- emit only after authoritative local write succeeds;
- the outbox write shares the source transaction where supported;
- consumers dedupe with `deduplicateDomainEvent`;
- events describe completed facts, not commands disguised as facts;
- downstream owner commands such as Search refresh or Notification request may be initiated by consumers/workers but remain owner-specific commands.

### Application event ledger question

There is no confirmed `JobApplicationEvent` source ledger in the current schema. U-CL06-11 must decide whether durable application lifecycle provenance requires one. Generic AuditEvent must not be used as a substitute for an owner lifecycle ledger if such a ledger is required.

---

## 22. Background Jobs / Scheduled Work

### Resume parse worker

- **Purpose:** parse ready/clean candidate resume assets.
- **Input:** `jobApplicationId`, `mediaId`, parse request/version.
- **Owner:** this Module.
- **Idempotency key:** stable application/media/parser-version tuple or approved equivalent.
- **Retryable:** transient file retrieval, worker timeout, transient parser errors where safe.
- **Permanent:** unsupported/corrupt content after Media validation, deterministic parser failure.
- **Business truth:** `ResumeParseResult` status/output.
- **Ops truth:** shared QueueJob/IntegrationFailure/SystemEvent where appropriate.
- **Dead letter:** leaves accurate parse state and surfaces operator retry/manual-review path; never marks candidate low quality.

### Candidate projection worker

- **Purpose:** rebuild privacy-safe CandidateSearchProjection after approved profile/parse/privacy/entitlement triggers.
- **Input:** candidate ID, source version/correlation.
- **Idempotency:** source-version + projection purpose.
- **Business truth:** CandidateSearchProjection only.
- **Downstream:** request Search refresh/removal.
- **Failure:** Search outage does not roll back source projection; unknown visibility fails closed to non-indexed.

### Privacy executor worker/handler

- **Purpose:** execute Privacy-owned target instructions against candidate records.
- **Input:** target instruction ID/envelope.
- **Idempotency:** Privacy target ID + instruction version.
- **Business truth:** only candidate-owned records.
- **Downstream:** Media deletion/revocation, Search removal, Audit/Ops requests.
- **Failure:** partial completion is explicit and retryable; retained records require Privacy-owned exemption references.

No custom scheduler or queue framework is created in this Module.

---

## 23. Concurrency and Idempotency

### Duplicate application race

Database invariant: `@@unique([jobId, candidateProfileId])`.

Application submission additionally crosses Track quota. The implementation requires a race-safe protocol using `executeIdempotentCommand`, database uniqueness/transaction semantics, and Track `consumeMeteredEntitlement`.

**Proposed protocol requirement:** application and usage outcomes must share a semantic idempotency key so retries can determine whether quota was consumed for the same logical application. If a truly atomic cross-owner transaction is not supported by root architecture, use explicit saga/reconciliation; do not pre-count locally and hope.

### Application transition race

Use `withOptimisticConcurrency` or approved aggregate locking keyed by JobApplication ID. Stale recruiter/candidate transitions return conflict with current state/version.

### Candidate profile edit race

Use expected version/updatedAt compare-and-set according to root persistence standard.

### Resume parse race

The unique `(jobApplicationId, mediaId)` constraint prevents duplicate parse truth. Worker execution still requires an idempotency claim by application/media/parser version.

### Resume access replay

The contextual authorization is re-evaluated for a new grant request; a reused idempotency key returns the same request result where safe. A short-lived grant remains Media-owned and cannot be extended by replaying local state.

### Projection race

Projection rebuilds must compare source/projection version or generated source marker so an older worker cannot overwrite a newer privacy state. Search refresh requests carry source version.

### No in-memory locks

Distributed concurrency uses database/shared primitives. In-memory mutexes are prohibited for authoritative protection.

---

## 24. Media / Storage

### Business attachment meaning owned here

- CandidateProfile ↔ MediaAsset via `CandidateProfileMedia`.
- JobApplication ↔ MediaAsset via `JobApplicationMedia`.
- Resume/CV business meaning and allowed use belong here.

### File mechanics owned by Media / File Access

- upload session;
- upload policy;
- file-size and binary/MIME validation;
- malware scan;
- quarantine/processing;
- storage bucket/object key;
- MediaAsset status;
- MediaAccessGrant/Event;
- signed URL generation and expiry.

### Resume-specific rules

- use `MediaUploadContext.candidate_resume` or `candidate_cv` as appropriate;
- current evidence caps resume/CV upload at 5 MB;
- allowed resume formats are PDF and DOCX with server-side validation;
- resume file remains private;
- parsing/display/access requires MediaAsset ready and scan-clean;
- `job_application_attachment` may be used for non-resume attachments under Media policy;
- no permanent public resume URL;
- `CandidateProfile.resumeUrl` must not be used as canonical resume access before U-CL06-09 is resolved.

### Sensitive access proof

Resume access may create three distinct records:

```text
ResumeAccessLog          # hiring-context proof, Candidate-owned
MediaAccessEvent         # generic file mechanics, Media-owned
AccessAuditLog           # generic sensitive access, Audit-owned
```

Correlation IDs/evidence references should allow investigators to connect them without merging their meaning.

---

## 25. Search / Projection

### Source truth

CandidateProfile + approved ResumeParseResult metadata + approved privacy/visibility state.

### Module-owned source projection

`CandidateSearchProjection` contains only approved fields, currently including skills, normalized titles, experience band, state-level location, remote preference, and explicit raw-text indexing flag.

### Search-owned projection

Search owns:

- SearchUpsertEvent;
- Typesense document shape/adapters where not source-specific;
- indexing/removal/reconciliation;
- query/ranking execution.

### Triggers

Projection rebuild/refresh may be requested after:

- CandidateProfile approved searchable fields change;
- ResumeParseResult completes or is superseded;
- candidate visibility/search participation changes;
- Privacy restriction/erasure;
- applicable Track boost entitlement changes;
- moderation/hold effects where the approved public-readiness contract requires it.

### Search must not reconstruct

Search must not read raw resume text, infer candidate verification from local fields, infer candidate privacy from profile existence, or rebuild Candidate Application policy from tables.

**U-CL06-10 blocks candidate search activation** until visibility/search-participation precedence and consent/preference requirements are approved.

---

## 26. Notification

This Module owns business notification triggers, not channel delivery.

Potential triggers:

- application submitted;
- application viewed where product/entitlement/privacy policy permits candidate notification;
- status/stage changes where recipient policy permits;
- withdrawal;
- resume parse failure requiring candidate action;
- privacy/search visibility change where user-facing notice is required.

Notification requests contain stable source IDs, safe template parameters, recipient facts or recipient-resolution inputs, and correlation IDs. They must not include raw resume text, full cover letters/answers, signed URLs, or unnecessary sensitive metadata.

Delivery failure never rewrites JobApplication truth.

---

## 27. Audit and Sensitive Access

### Module domain/history truth

- `ResumeAccessLog` — candidate-domain resume access proof.
- `JobApplicationViewEvent` — proposed candidate-domain application-view truth.
- potential future `JobApplicationEvent` — unresolved U-CL06-11; not to be faked with generic AuditEvent.

### Generic AuditEvent

Use `appendAuditEvent` for significant actions required by root policy, such as sensitive admin overrides, destructive privacy execution, or lifecycle actions requiring generic platform audit.

### AccessAuditLog

Use `recordSensitiveAccess` for restricted resume/application reads when policy requires. Use `DataSensitivity.resume` or the current canonical sensitivity value rather than creating a candidate-specific generic audit table.

### Separation rule

A successful resume workflow may need both ResumeAccessLog and AccessAuditLog. One does not eliminate the other. MediaAccessEvent remains separate as file-mechanics evidence.

---

## 28. Privacy and Retention

### Subject-data inventory

At minimum enumerate:

- CandidateProfile and personal fields;
- CandidateProfileMedia joins;
- CandidateCategory/Tag context where owned/executable;
- JobApplication cover letter, answers, status/stage, timestamps;
- JobApplicationMedia joins;
- ResumeParseResult, including `extractedText` and metadata;
- ResumeAccessLog;
- JobApplicationViewEvent if approved;
- CandidateSearchProjection;
- owner references needed to delegate Media/Search cleanup.

### Owner executor behavior

Privacy sends a target instruction. This Module may:

- export permitted candidate data;
- erase owner-held fields/records where allowed;
- anonymize retained relational/hiring history where required;
- restrict candidate visibility/source projection;
- detach Media relationships;
- request Media object/grant deletion or revocation;
- request Search de-index/removal;
- return retained/skipped/failed results with Privacy-owned exemption references.

### Retention

U-CL06-13 must resolve encryption/retention of `ResumeParseResult.extractedText`. Hiring-record retention for applications/access/view events may also require legal/policy decisions. The Module supplies retention facts; Privacy records `DataRetentionExemption`.

Product archive/delete is not legal erasure. Proof that privacy execution occurred must not be casually erased.

---

## 29. Observability

Use canonical structured logging, request/correlation IDs, exception capture, queue telemetry, and Ops failure records.

### Safe dimensions

Allowed examples:

- operation name;
- Module ID;
- status/reason code;
- aggregate type and opaque ID;
- media context (not filename/body);
- parser name/version;
- worker attempt/result;
- dependency name;
- latency;
- retry/dead-letter category.

### Prohibited telemetry payloads

Do not log or send to analytics:

- raw resume text;
- private application answers or full cover letters;
- signed URLs/tokens;
- full filenames when they may contain personal data unless specifically approved;
- raw IP addresses when hashed/minimized evidence is sufficient;
- private provider/storage payloads.

Operational records never become candidate/application lifecycle truth.

---

## 30. Security Boundaries

1. Runtime-validate every command/query input server-side according to root standards.
2. Resolve authenticated actor before protected work.
3. Use Role / Authority for organization-scoped permission interpretation.
4. Validate complete relationship chains; possessing CandidateProfile, Job, application, media, or organization IDs is not authority.
5. Keep resume/CV assets private and short-lived when exposed.
6. Require ready + clean Media state before resume parse/display/access.
7. Do not persist or log signed URL/token secrets.
8. Apply rate limiting to expensive/sensitive reads and access-grant requests using shared platform policy where applicable.
9. Hash/minimize IP evidence using the shared security primitive; do not create `resumeIpHasher`.
10. Exclude raw resume text from analytics and Search by default.
11. Do not treat CandidateProfile verification-looking fields as Trust truth.
12. No support/admin universal resume bypass.
13. Privacy execution uses scoped service authority and idempotent target instructions.
14. RLS and server-side authorization require parity tests.
15. Parser libraries receive only the private file needed for extraction and return normalized data; they do not receive unrelated application data.

---

## 31. Error / Decision Result Pattern

Public interfaces must return domain-safe results rather than leaking Prisma, storage, parser, Search, or provider exceptions.

### Stable categories

```text
validation_error
unauthenticated
unauthorized
not_found
conflict
stale_version
domain_denied
compliance_blocked
entitlement_denied
verification_required
manual_review_required
dependency_unavailable
retryable_failure
permanent_failure
success
```

Each result should carry a stable reason code, safe message key, correlation ID, and evidence/source references where allowed. Internal exceptions may contain richer diagnostic context only in protected logs.

A dependency outage is not a domain denial unless the local policy explicitly fails closed as deny. Where the distinction matters, return `dependency_unavailable`/`review` rather than pretending the candidate failed a business condition.

---

## 32. Testing Architecture

### Domain unit tests

- CandidateProfile usability and approved transitions;
- JobApplication transition matrix after U-CL06-11;
- status/stage timestamp invariants;
- resume-context authorization;
- parser normalization and non-decision constraints;
- CandidateSearchProjection allowlist/visibility logic;
- privacy disposition mapping;
- decision reason codes.

### Public contract tests

- Organization Hiring owner-fact DTO compatibility;
- Track entitlement/quota receipt behavior;
- Trust requirement/readiness decision consumption;
- Media ready/clean/access grant contracts;
- Search refresh/removal contract;
- Audit sensitive-access contract;
- Privacy target request/result contract;
- Job Interview application-context contract.

### Database/integration tests

- one CandidateProfile per User;
- unique `(jobId, candidateProfileId)` application;
- composite media joins;
- unique parse result per application/media;
- expected indexes/query paths;
- transactional outbox coupling;
- schema relation integrity after U-CL06-17 fix.

### Authorization / RLS tests

- candidate cannot read/mutate another candidate’s private records;
- recruiter cannot access another Organization’s applicants;
- applicant detail access does not imply resume access;
- wrong media/application relation denies;
- admin/support access follows explicit policy;
- RLS/server decision parity.

### Compliance/security tests

- verified-only gate cannot be bypassed;
- quota cannot be bypassed;
- Hold cannot be bypassed;
- resume parse/read blocked before ready+clean;
- no permanent public resume URL;
- no raw resume in Search/logs/analytics;
- no automated recommendation from ResumeParseResult;
- required access proof correlation.

### Idempotency/concurrency tests

- simultaneous same-Job applications;
- Track quota race;
- idempotent submit replay;
- stale recruiter transition;
- duplicate parse jobs;
- stale projection worker after privacy hide/erase;
- repeated resume-grant request;
- privacy executor rerun.

### Privacy tests

- subject enumeration completeness;
- export redaction;
- erase/anonymize/retain mapping;
- retained records cite Privacy exemption refs;
- Media deletion delegated;
- Search de-index delegated;
- partial failure remains retryable/visible.

### E2E participation tests

```text
CandidateProfile → private resume → parse → submit application
Recruiter → applicant detail → application view evidence
Recruiter → authorized resume → short-lived Media access + proof
Application → Job Interview owner handoff without direct application writes
Candidate privacy restriction/erasure → projection removal + owner result
```

---

## 33. Module Invariants

### Rules coding agents must never violate

1. `CandidateProfile`, not `User`, is applicant identity.
2. This Module alone mutates CandidateProfile candidate lifecycle state.
3. This Module alone mutates JobApplication status/stage.
4. Organization Hiring and Job Interview may request/read application changes but may not write JobApplication tables directly.
5. One CandidateProfile cannot have duplicate applications to the same Job.
6. Application limits come from Track; no local quota counter or premium boolean.
7. Candidate search boosts and application-view perks come from Track.
8. Verified-only decisions come from Trust Verification; TrustBadge alone is not readiness truth.
9. ComplianceHold is the reusable stop sign; no candidate/application local block table.
10. Resume/CV files remain private MediaAssets.
11. Resume uploads use Media-owned validation and scanning; no local file-safety pipeline.
12. Resume parsing/display/access cannot precede ready + scan-clean Media state.
13. Candidate contextual resume authorization must precede Media grant/signed URL issuance.
14. No permanent public resume URL is an access mechanism.
15. `CandidateProfile.resumeUrl` is not canonical resume truth before U-CL06-09 resolution.
16. `CandidateProfile.trustScore`, `verifiedAt`, and `verificationExpiresAt` are not VerificationCheck truth.
17. Resume parsing is extraction only and never produces automated hiring recommendations or final candidate decisions.
18. Raw resume text is not indexed by default.
19. CandidateSearchProjection remains Candidate-owned source projection; Typesense is Search-owned projection.
20. Search never reconstructs candidate privacy/eligibility from private tables.
21. ResumeAccessLog, MediaAccessEvent, and AccessAuditLog remain separate records with separate meaning.
22. JobApplicationViewEvent and TrackUsageEvent remain separate facts if view events are approved.
23. `viewedAt`/`status=viewed` semantics may not be guessed before U-CL06-12 approval.
24. Full JobApplication transition semantics may not be guessed before U-CL06-11 approval.
25. ResumeAccessLog issuance-vs-read semantics and raw-text retention may not be guessed before U-CL06-13 approval.
26. Candidate search may not be activated before U-CL06-10 is resolved.
27. Taxonomy semantics remain Taxonomy-owned; U-CL06-08 controls join write placement.
28. Search/Notification/Messaging/Audit/Privacy/Media workers may not directly mutate Candidate records except through this Module’s approved interface/executor.
29. Provider/library output does not become candidate quality truth.
30. Every retryable side effect is idempotent and observable.
31. No in-memory lock protects authoritative concurrency.
32. Sensitive telemetry is minimized/redacted.
33. Privacy owns request orchestration; this Module mutates only its own data in response.
34. The U-CL06-17 Prisma relation defect must be resolved before migrations touching JobApplication/ViewEvent.
35. Architecture must be updated before implementation depends on a changed binding decision.

---

## 34. Prohibited Duplicate Implementations

Do not generate these or equivalent local implementations:

```text
candidateAuth.ts
resumeAuth.ts
currentCandidateUser.ts
canRecruiterViewResume.ts
checkRecruiterRole.ts
candidatePermissions.ts
isPremiumCandidate.ts
candidatePlanService.ts
applicationLimitHelper.ts
applicationQuotaCounter.ts
candidateSearchBoost.ts
candidateVerified.ts
backgroundPassed.ts
candidateTrustService.ts
resumeStorageService.ts
resumeUploadValidator.ts
resumeMimeChecker.ts
candidateMalwareScanner.ts
ResumeSignedUrlService.ts
resumeDownloadToken.ts
privateResumeAccessGrant.ts
CandidateAccessAudit.ts
ResumeAuditTable.ts
candidateTypesenseService.ts
resumeSearchIndexer.ts
candidateIndexWorker.ts
candidateEmailService.ts
applicationPushService.ts
CandidateDeleteRequest.ts
resumeErasureWorkflow.ts
candidateQueueFramework.ts
applicationMutex.ts
resumeIpHasher.ts
```

Also prohibited:

- a local SearchUpsertEvent equivalent;
- a second generic access-grant table;
- a generic hiring readiness engine that absorbs Role, Track, Trust, Holds, and Job facts;
- a generic application/interview state machine owning both lifecycles;
- a local PrivacyRequest/DataErasureJob system;
- direct R2/Typesense/provider clients used to bypass Media/Search owners.

---

## 35. Unresolved Decisions

### Inherited CL-06 blockers

- **U-CL06-04 — Organization ATS commercial entitlement.** If resume viewer/applicant tracker/candidate search are monetized for Organizations, ownership and relation to Track must be resolved. Basic MVP must not invent the gate.
- **U-CL06-08 — Classification join persistence.** Resolve attach/detach write owner for CandidateCategory/CandidateTag.
- **U-CL06-09 — Overlapping direct/projection fields.** Decide remove/deprecate/projection semantics for `CandidateProfile.resumeUrl`, `trustScore`, `verifiedAt`, `verificationExpiresAt`.
- **U-CL06-10 — Candidate visibility/search participation.** Define precedence between `CandidateProfile.isVisible` and CandidateSearchProjection status, and whether explicit search participation consent/preferences are required.
- **U-CL06-11 — Application transition/event semantics.** Define legal status/stage transitions, timestamps, terminal behavior, reversal/reopen rules, actors, and whether JobApplicationEvent is required.
- **U-CL06-12 — Application view semantics.** Approve/reject the Proposed Ruling that JobApplicationViewEvent is append-only truth and `viewedAt`/`status=viewed` are summary projections.
- **U-CL06-13 — Resume access semantics and raw text retention.** Define ResumeAccessLog grant-vs-read meaning and encryption/retention of `ResumeParseResult.extractedText`.
- **U-CL06-17 — Prisma structural defect.** Fix/verify relation lines currently outside model braces before affected migrations.

### Module-specific unresolved decisions discovered during consolidation

#### U-CARP-01 — CandidateSearchProjection cardinality/versioning

The schema permits multiple projections per CandidateProfile. Decide whether:

1. exactly one current projection row should exist;
2. multiple immutable/versioned source projections are intentional; or
3. one active row plus historical superseded rows is intended.

Search requires one unambiguous current source/version. This blocks any migration that imposes uniqueness or any implementation that assumes a single row.

#### U-CARP-02 — Resume parse retry evidence

The schema stores one ResumeParseResult per application/media pair but no parse-attempt ledger. Decide whether failed retry history belongs only in shared Queue/Ops records or whether parser attempt provenance must be retained in owner truth. Do not invent an attempt table without approval.

#### U-CARP-03 — Application-media role vocabulary

`CandidateProfileMedia.role` and `JobApplicationMedia.role` are free strings. MediaUploadContext is controlled externally, but the local role vocabulary is not defined. Runtime code must not proliferate ad hoc strings. Approve a local role vocabulary or rely only on external upload context plus explicit DTOs.

---

## 36. Architecture Decision Summary

### Binding rulings

- Candidate Application & Resume Privacy owns CandidateProfile applicant truth and JobApplication lifecycle.
- Candidate status/stage mutation stays here even when Organization Hiring or Job Interview initiates the request.
- Resume business authorization/proof stays here; Media owns file safety/storage/grants/signed URLs.
- ResumeAccessLog, MediaAccessEvent, and AccessAuditLog remain separate truths.
- Resume parsing is non-decisional extraction only.
- CandidateSearchProjection is Candidate-owned source projection; Search owns Typesense/index execution.
- Track owns candidate application limits, boosts, and application-view perks.
- Trust Verification owns verified-only screening truth.
- Role / Authority owns permission interpretation.
- ComplianceHold is the reusable stop sign.
- Privacy owns privacy-request orchestration; this Module exposes owner-local enumeration/execution.
- Notification, Messaging, Audit, Search, Media, and Ops effects are requested through public interfaces/events.
- Direct cross-domain Prisma repository access is not the default integration model.
- The current malformed JobApplication/JobApplicationViewEvent relation placement must be corrected before affected migrations.

### Proposed/non-binding rulings

- JobApplicationViewEvent belongs to this Module and is append-only truth; viewedAt/status=viewed are summaries.
- CandidateProfile conservative transition graph described in Section 9.
- CandidateSearchProjection source status lifecycle described in Section 9.

### Deferred until resolved

U-CL06-04, 08, 09, 10, 11, 12, 13, 17 and U-CARP-01/02/03 must not be silently decided in code.

---

## 37. Coding-Agent Usage

Before implementing or modifying this Module, the coding agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Architecture / Registry;
5. CL-06 `architecture.md`;
6. CL-06 `build-plan.md`;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. public-interface sections for Identity, Role / Authority, Organization Hiring, Job Compliance, Track, Trust Verification, Media, Search, Audit, Notification, Messaging, Privacy, Holds, Ops, and Job Interview as relevant to the feature;
10. current Prisma schema/migrations;
11. decisions resolving any referenced `U-CL06-*` or `U-CARP-*` blocker;
12. progress tracker / current implementation handoff.

Before coding a numbered feature, confirm its Cluster feature link and the prior Module exit gate. If implementation reveals a conflict with a binding ownership/lifecycle rule, stop, record the conflict, update architecture through the approved process, and only then continue. Do not use successful tests as permission to redefine architecture.
