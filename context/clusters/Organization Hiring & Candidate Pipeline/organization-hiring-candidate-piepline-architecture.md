# Organization, Hiring, & Candidate Pipeline Architecture

> **Cluster ID:** CL-06  
> **Cluster type:** `hiring_domain_candidate_privacy_job_compliance`  
> **Status:** implementation-grade cluster architecture  
> **Authority:** root Workin Ants architecture and confirmed Module ownership remain superior; Proposed Rulings and Unresolved Decisions below are not silently binding.

## 1. Document Status and Scope

CL-06 coordinates formal hiring across four Deep Modules:

- `organization_hiring`
- `job_compliance`
- `candidate_application_resume_privacy`
- `job_interview`

The Cluster is a planning, integration, and controlled-context boundary. It **does not own any Module lifecycle**. Organization/Job, Job Compliance, application/resume, and interview truth remain owned by their Deep Modules.

This document sits below root Workin Ants architecture and above Module implementation plans. If a binding source-of-truth, lifecycle, public-contract, provider, privacy, or shared-operation decision changes, update architecture before implementation proceeds. Build progress must never redefine architecture silently.

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

Turn formal hiring intent into compliant Jobs, private applications, controlled resume access, candidate pipeline state, and scheduled interviews without collapsing identity, permission, compliance, file, search, entitlement, or provider truth.

### Goal

A healthy CL-06 flow answers:

```text
Which Organization is hiring?
Which authorized OrganizationMember is acting?
Which Job owns the formal opportunity?
Has Job Compliance approved public publication?
Which CandidateProfile is applying?
Does Track permit this application/perk?
Does Trust Verification satisfy verified-only gates?
Who may see this application/resume?
Which Module owns the interview?
Which downstream rails are being requested rather than duplicated?
```

### Inputs

Authenticated actor context; Organization/profile/member commands; Job content, compensation, taxonomy and visibility intent; jurisdiction/rule context; candidate profile/application intent; entitlement and verification decisions; private MediaAsset references; hold state; interview scheduling intent; provider-normalized results; Privacy instructions.

### Outputs

Authoritative Organization/Job state; compliance checks/findings/disclosure proof; CandidateProfile/JobApplication state; private attachment context; resume parse/access proof; CandidateSearchProjection; JobInterview/participant/event state; owner-issued events/commands to Search, Media, Notification, Messaging, Video, Calendar, Audit, Privacy, Holds, and Ops.

### Explicit non-ownership

CL-06 does not own authentication, permission interpretation, Track policy, generic consent proof, taxonomy vocabulary, Trust Verification, Media mechanics, Typesense/SearchUpsertEvent, ComplianceHold, AuditEvent/AccessAuditLog, notification delivery, messaging lifecycle, video-room truth, PrivacyRequest orchestration, general calendar provider truth, or marketplace Gigs/Offerings/Orders/Bookings.

## 3. Module Inventory

| Module ID | Module name | Type | Purpose | Owned truth | Primary CL-06 responsibility | Major inbound dependencies | Major outbound consumers |
|---|---|---|---|---|---|---|---|
| `organization_hiring` | Organization Hiring | domain | Own hiring entity, membership rows and formal Job lifecycle | `Organization`, `OrganizationStatus`, `OrganizationMember`, role assignment, `Job`, `JobStatus`, `JobVisibility`, employment-type use, org notification preferences | Create/manage Organizations and Jobs; expose owner facts; apply compliance decisions to Job lifecycle | Identity, Role/Authority, Taxonomy, Job Compliance, Trust, Media, Holds | Candidate Application, Job Compliance, Job Interview, Search, Notification |
| `job_compliance` | Job Compliance | compliance | Evaluate Job postings under versioned jurisdiction-aware rules | `JobComplianceRule`, `JobComplianceCheck`, `JobComplianceFinding`, `JobCompensationDisclosure` and posting-compliance policy | Produce durable publication decision/evidence without owning Job lifecycle | Organization Hiring, authority, taxonomy/jurisdiction, Holds, shared scanner/versioning | Organization Hiring, Search, Admin Review, Audit, Notification |
| `candidate_application_resume_privacy` | Candidate Application & Resume Privacy | domain/compliance hybrid | Own applicant identity, applications, resume meaning/access, parsing and candidate source projection | `CandidateProfile`, `JobApplication`, status/stage, application media, `ResumeParseResult`, `ResumeAccessLog`, `CandidateSearchProjection`; `JobApplicationViewEvent` | Submit/manage applications, enforce quota/verified gates, protect resumes, expose applicant/recruiter views | Identity, authority, Organization Hiring eligibility context, Track, Trust, Media, Holds | Organization dashboard, Job Interview, Search, Privacy, Audit |
| `job_interview` | Job Interview | domain/capability hybrid | Own formal interview lifecycle attached to JobApplication | `JobInterview`, status/location, `JobInterviewEvent`, `JobInterviewParticipant` and participant role/status | Propose/schedule/reschedule/coordinate interviews while delegating provider rails | Identity, authority, Organization Hiring, Candidate Application, Video, Calendar, Messaging, Notification | hiring dashboards and support rails |

## 4. Cluster Architecture Principles

1. One owner per lifecycle.
2. Organization Hiring owns OrganizationMember row/role assignment; Role / Authority interprets permission.
3. Job lifecycle and Job Compliance lifecycle are separate.
4. CandidateProfile, not User, is applicant identity.
5. JobApplication status/stage are not JobInterview state.
6. Resume business authorization is Candidate Application truth; Media owns grant/signed-URL mechanics.
7. `ResumeAccessLog`, `MediaAccessEvent`, and `AccessAuditLog` remain separate proofs.
8. Search is projection. CandidateSearchProjection is source-owned; Typesense is disposable.
9. Track is commercial entitlement truth; no local premium/quota/boost booleans.
10. `ComplianceHold` is the reusable stop sign.
11. Job posting compliance and candidate/background screening remain separate.
12. `JobInterview` is not `Booking`.
13. Domain event truth and generic audit truth remain separate.
14. Provider state is never Workin Ants domain truth.
15. Privacy owns privacy-request orchestration; source Modules execute against their own records.
16. Shared mechanisms do not transfer record, policy, or lifecycle ownership.

## 5. Runtime / Collaboration Topology

```text
Browser / Server Action / Route Handler / Worker
        ↓
SH-001 resolveAuthenticatedActor (Confirmed)
        ↓
SH-002 authorizeResourceAction (Confirmed)
        ↓
Owning CL-06 application service
   ├─ local domain policy
   ├─ local repository / transaction
   └─ public dependency ports
        ├─ Track / Trust / Holds
        ├─ Media / Search
        ├─ Messaging / Notification
        ├─ Video / Calendar
        └─ Audit / Privacy / Ops
        ↓
authoritative owner write
        ↓
transactional outbox
        ↓
reliable worker / inbox dedupe
        ↓
downstream owner command
```

No browser component, route handler, worker, or provider callback owns a complete business workflow by itself. Cross-Module writes use public commands/events. Direct cross-domain Prisma access is not the default integration model.

## 6. Folder / Code Organization

```text
src/
  modules/
    organization-hiring/{domain,application,public,persistence,policies,events,jobs,ui,tests}
    job-compliance/{domain,application,public,persistence,policies,scanners,events,jobs,admin,tests}
    candidate-application-resume-privacy/{domain,application,public,persistence,projections,jobs,ui,tests}
    job-interview/{domain,application,public,persistence,events,jobs,ui,tests}
  integrations/
    calendar/{ports,adapters}
    video/{ports,adapters}
    verification/{ports,adapters}
    media/{ports}
    search/{ports}
  platform/
    security/
    authority/
    idempotency/
    concurrency/
    events/
    queue/
    crypto/
    observability/
context/
  clusters/Organization Hiring & Candidate Pipeline/
```

Rules:

- Module repositories are not imported by neighboring Modules as a shortcut.
- Cluster-local coordination is allowed only when it is truly multi-Module and owns no lifecycle.
- Do not create a generic `shared/` dumping ground.
- Shared code must correspond to an approved shared operation/platform primitive.
- Provider payload types stay in adapters.

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
|---|---|---|---|
| Organization Hiring | Organization/member rows/Job lifecycle, org notification prefs, contextual org/job media meaning | actor, authority, taxonomy, Job Compliance decision, Trust requirements, Media readiness, Holds, application/interview summaries | permission interpretation, compliance findings/rules, application/resume/interview lifecycle, Search execution |
| Job Compliance | versioned rules, checks, findings, disclosure proof, posting-compliance policy | Job snapshot, jurisdiction/taxonomy context, holds, admin authority, audit/notification/search commands | Job lifecycle, candidate screening, general moderation, Search |
| Candidate Application | CandidateProfile, JobApplication status/stage, resume business meaning/access proof, candidate projection | Job facts, Track quota/perks, Trust readiness, Media grants, Search, Holds | Job creation/compliance scan, MediaAsset mechanics, Typesense, VerificationCheck, interview lifecycle |
| Job Interview | interview lifecycle/schedule intent/event ledger and participant lifecycle | application facts, org authority, resume access, video/calendar/messaging/notification | Booking, application status/stage, resume privacy, room/provider truth |
| Role / Authority | permission interpretation | owner-fact DTOs | membership/application/interview/compliance lifecycle |
| Track | entitlement and usage truth | usage trigger | JobApplication/Candidate projection truth |
| Media | asset safety/storage/grants/signed URLs | contextual authorization | resume business permission |
| Search | SearchUpsertEvent/Typesense/reconciliation/query | source projections/readiness | source lifecycle/compliance/privacy reconstruction |
| Privacy | request/job orchestration and retention exemptions | owner executors | direct CL-06 source writes |
| Holds | ComplianceHold lifecycle | CL-06 evidence | local lifecycle states |
| Audit | AuditEvent/AccessAuditLog | domain references | domain ledgers/access proof |
| Notification | channel delivery | safe business event | hiring lifecycle |
| Messaging | threads/messages | hiring context | application/interview lifecycle |
| Video Session | JobInterviewVideoRoom/provider room | interview schedule | JobInterview lifecycle |
| Booking & Calendar | provider connection/invocation/synchronization/event normalization through SH-067 `invokeCalendarProvider` (Confirmed) | interview schedule intent | JobInterview lifecycle |

## 8. Data Ownership

| Record / enum | Owner / ruling |
|---|---|
| `Organization`, `OrganizationStatus` | Organization Hiring |
| `OrganizationMember`, assigned `OrganizationRole` | Organization Hiring; Role/Authority interprets |
| `OrganizationNotificationSetting` | Organization Hiring |
| `OrganizationFeatureAccess` + key/status | **Unresolved** |
| `OrganizationCategory/Tag` | Taxonomy semantics + Organization contextual meaning; persistence command owner unresolved |
| `OrganizationMedia` | Organization Hiring contextual meaning; Media mechanics |
| `Job`, `JobStatus`, `JobVisibility`, `EmploymentType` | Organization Hiring |
| `CompensationPeriod` | Organization Hiring — WA-R010 |
| `JobTag` | Taxonomy semantics + Job contextual meaning; persistence command owner unresolved |
| `JobMedia` | **Proposed:** Organization Hiring contextual meaning; Media mechanics |
| `JobComplianceRule` and rule enums | Job Compliance |
| `JobComplianceCheck` and status | Job Compliance |
| `JobComplianceFinding` and type/severity | Job Compliance |
| `JobCompensationDisclosure` | Job Compliance proof/snapshot, not offered-compensation truth |
| `Job.complianceStatus` | **Proposed:** Organization Hiring-owned summary mirror written only from Job Compliance decision |
| `CandidateProfile` | Candidate Application |
| `ProfileStatus` | shared enum; candidate-specific use owned by Candidate Application |
| `CandidateCategory/Tag` | Taxonomy semantics + Candidate contextual meaning; persistence command owner unresolved |
| `CandidateProfileMedia` | Candidate contextual meaning; Media mechanics |
| `JobApplication`, status/stage | Candidate Application |
| `JobApplicationMedia` | Candidate Application |
| `JobApplicationViewEvent` | Candidate Application; one event has at most one Organization context |
| `ResumeParseResult` | Candidate Application |
| `ResumeAccessLog` | Candidate Application |
| `CandidateSearchProjection` | Candidate Application source projection |
| `JobInterview`, status/location | Job Interview |
| `JobInterviewParticipant`, role/status | Job Interview; removal and role eligibility remain unresolved |
| `JobInterviewEvent` | Job Interview domain event truth |
| `JobInterviewVideoRoom` | Video Session |
| `SearchUpsertEvent` | Search |
| `TrackUsageEvent/Counter` | Track |
| `MediaAccessGrant/Event` | Media |
| `AuditEvent/AccessAuditLog` | Audit |
| `ComplianceHold` | Admin Review / Compliance Hold |
| Privacy request/job/exemption records | Privacy |

**Schema discrepancy (CL-06-R008):** `JobApplicationViewEvent.organizationId` is its single optional Organization context. One event SHALL NOT belong to multiple Organizations. The additional `organizations Organization[]` / `Organization.jobApplicationView` many-to-many relation has no approved domain meaning and must not be used as source truth; it is flagged for removal in a later schema pass unless distinct evidence establishes another relationship. U-CL06-17 is retired as written because the referenced fields are inside model braces; this does not certify overall schema validity or resolve the project-level migration baseline.

## 9. Lifecycle Ownership

### Organization

Owner: Organization Hiring. Statuses: `draft`, `active`, `suspended`, `archived`. Only Organization Hiring transitions status. Verification/holds may gate transitions but do not own them.

### Organization membership

Owner: Organization Hiring. Current schema represents membership by row presence plus `owner|admin|recruiter`. No invitation/suspension status exists. Do not invent one without architecture.

### Job

Owner: Organization Hiring. Statuses:

```text
draft
pending_compliance_review
flagged_for_review
open
paused
filled
closed
rejected
archived
```

Job Compliance supplies a decision; Organization Hiring maps it to Job lifecycle.

### Job Compliance rule

Owner: Job Compliance. `draft|active|retired|disabled`.

### Job Compliance check

Owner: Job Compliance. `passed|warning|blocked|needs_review|failed`.

Job-level summary vocabulary: `not_checked|pending_review|approved|rejected|needs_changes`.

**Proposed Ruling:** check/finding/disclosure truth produces the effective decision; `Job.complianceStatus` is a summary mirror. `failed` is technical failure, never automatic approval/rejection.

### Compensation disclosure

Owner: Job Compliance. `not_required|required_missing|provided|provided_with_warning|exempt|blocked`. Job compensation itself remains Organization Hiring business truth.

### CandidateProfile

Owner: Candidate Application. `draft|active|paused|suspended|archived`.

### JobApplication

Owner: Candidate Application.

Candidate-facing status:

```text
submitted | viewed | withdrawn | rejected | accepted_offer | hired
```

Organization-facing stage:

```text
new_ | screen | interview | offer | hired | closed
```

Job Interview may request/react to changes but never writes them directly.

### ResumeParseResult

Owner: Candidate Application. `pending|processing|completed|failed|skipped`.

### CandidateSearchProjection

Owner: Candidate Application. `draft|active|hidden|erased|disabled`.

### JobInterview

Owner: Job Interview. `draft|proposed|scheduled|rescheduled|completed|cancelled|no_show|expired`.

### Interview participant

Owner: Job Interview, including `JobInterviewParticipantRole` and `JobInterviewParticipantStatus`. `invited|accepted|declined|tentative|no_response`. Removal/revocation and role eligibility remain unresolved.

Exact application transition matrix, view summary semantics, participant removal and reschedule semantics remain unresolved below.


## 10. Public Module Interfaces

Prefer these owner-specific contracts to direct repository reads. Names are canonical architecture names unless a target Module later adopts an explicitly approved equivalent.

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
|---|---|---|---|---|---|---|---|
| `getOrganizationHiringContext` | Organization Hiring | Role, Candidate Application, Job Interview | minimal org/job ownership and lifecycle facts | org/job ID + requester context | IDs, status, version, relationship facts | truth/facts | permission policy |
| `createOrganization`, `updateOrganizationProfile` | Organization Hiring | first-party UI/admin | create/manage hiring entity | actor + validated fields | Organization + version | truth | verification readiness |
| `addOrganizationMember`, `changeOrganizationMemberRole`, `removeOrganizationMember` | Organization Hiring | org admin UI | mutate membership facts | actor, org, target user, role | membership result/version | truth | authority semantics |
| `createJobDraft`, `updateJobDraft` | Organization Hiring | hiring UI | create/edit formal Job | actor, org/job, validated fields | Job + version | truth | compliance approval |
| `requestJobPublication` | Organization Hiring | hiring UI | place Job into compliance review | actor, Job, owner-issued opaque expectedConcurrencyToken, idempotency key | review receipt | workflow state | compliance rules |
| `getJobApplicationEligibilityContext` | Organization Hiring | Candidate Application | expose Job/Org facts needed before apply | Job ID | status/visibility/owner facts/version | truth/facts | candidate entitlement/verification |
| `requestJobComplianceEvaluation` / SH-021 `evaluateJobCompliance` (Confirmed) | Job Compliance | Organization Hiring | run posting evaluation | Job ID+version or canonical snapshot, trigger, actor/system | check ref + DecisionResult | decision/evidence | local rule recreation |
| `getJobPublicationComplianceDecision` | Job Compliance | Organization Hiring, Search/admin | current effective decision | Job ID/version | decision, reasons, warnings, evidence refs, policy/source version | decision | raw-rule reconstruction |
| `getJobComplianceReport` | Job Compliance | authorized org/admin | detailed findings/provenance | Job ID + actor | checks/findings/disclosure/rule refs | evidence | permission from possession |
| `createCandidateProfile`, `updateCandidateProfile` | Candidate Application | candidate UI | own applicant identity | actor + profile fields | CandidateProfile | truth | Trust verification from local fields |
| `evaluateApplicationEligibility` | Candidate Application | submit flow | compose Job, Track, Trust, hold and profile facts | actor, CandidateProfile ID, Job ID | DecisionResult + refs | decision | Track/Trust/Job policy |
| `submitJobApplication` | Candidate Application | candidate UI | race-safe one-application submission | actor, job, candidate, answers, attachments, idempotency key | JobApplication + usage receipts | truth/workflow | local quota truth |
| `transitionApplicationStage`, `transitionApplicationStatus` | Candidate Application | authorized org/candidate/admin | mutate application lifecycle | actor, application, target, reason/version | updated application | truth | direct DB mutation elsewhere |
| `listJobApplicants`, `getJobApplicationDetail` | Candidate Application | Organization Hiring UI | privacy-shaped applicant views | actor, job/application, pagination | shaped application DTO | truth/read model | resume access permission |
| `authorizeContextualResumeAccess` | Candidate Application | recruiter/interview flow | decide whether one resume may be accessed for a reason | actor, app, media, reason | allow/deny + evidence refs | decision | signed URL issuance |
| `recordResumeAccess` | Candidate Application | resume access orchestration | append resume-domain access proof | access result, actor, app, media, reason, metadata | ResumeAccessLog ref | evidence | generic audit truth |
| `getCandidateSearchProjection` | Candidate Application | Search | return sanitized source projection | CandidateProfile ID/version | projection DTO + visibility state | projection | raw resume/eligibility |
| `proposeInterview`, `scheduleInterview`, `rescheduleInterview` | Job Interview | hiring/candidate UI | own interview schedule state | actor, application facts, times, location, participants | JobInterview + version | truth | application stage mutation |
| `respondToInterviewInvitation` | Job Interview | participant UI | update participant response | actor, interview, response | participant state | truth | messaging/calendar state |
| `getInterview` / list queries | Job Interview | candidate/org dashboard | authorized interview read | actor + target | privacy-shaped interview DTO | truth/read model | resume permission |
| `handleApplicationStateChanged` | Job Interview | Candidate Application event consumer | react to parent application change | event envelope | owner-local effects/ack | owner-local result | application ownership |
| SH-095 `executePrivacyInstruction` (Confirmed) | each CL-06 owner | Privacy | execute legal instruction against owner data | target envelope | standard target result | execution/evidence | Privacy orchestration |

### Publication and source contracts — CL-06-R004/R005/R021

Job Compliance owns the publication response vocabulary: `allowed | denied | warning | review_required | unavailable`. Organization Hiring consumes that contract without a competing union. `unavailable` is evaluation/dependency unavailability, not denial; `review_required` is not denial. Remediation is reason/next-action metadata. This local contract does not approve proposed SH-015 `returnDecisionResult` (Proposed ruling); final publication precedence and Job-state mapping remain U-CL06-05/07.

Organization Hiring exposes two distinct public source-query contracts (descriptive contract labels, not new SH operations):

- **Compliance input snapshot:** takes a Job identifier and source-revision/concurrency context; returns the exact source revision/token and all Organization-owned Job facts required for evaluation, including authoritative taxonomy, location and business-compensation references.
- **Compliance rescan enumeration:** takes rule/jurisdiction/effective-scope criteria and a cursor; returns eligible Job IDs with their source revision/token and pagination cursor.

Job Compliance consumes those owner contracts before evaluation/rescan and never queries Organization repositories directly. Disclosure evidence is not an originating source for Job business facts. Required compensation/benefit field mappings without an authoritative Organization-owned source remain unresolved.

Normal application submission follows Job Compliance decision → Organization Hiring lifecycle/application eligibility → Candidate Application. `getJobApplicationEligibilityContext` fails closed unless authoritative current Job state permits applications. Candidate does not independently read or reevaluate Job Compliance in this flow. Later Compliance changes are applied by Organization Hiring; Candidate reacts to Job owner state/events. Any future direct Candidate → Compliance dependency requires a new explicit Cluster policy.

### Public concurrency contract — CL-06-R020

Cross-Module mutation requests use an owner-issued opaque `expectedConcurrencyToken`. The owner returns the token, atomically compares it through SH-052 `withOptimisticConcurrency` (Confirmed), and rejects stale tokens. A universal integer version or `updatedAt` field is not assumed. JobApplication, mutable Compliance finding/review, JobInterview and parent-versus-child token backing remain unresolved where not already approved.

## 11. Canonical Shared Operations Used by This Cluster

The [Shared Operations registry](../../shared/shared-operations.md) governs permanent IDs, canonical names, owners, classifications and statuses. Registered use points below carry verified IDs/statuses. Proposed ruling entries may support planning and owner-specific interfaces/mechanisms, but cross-platform SH API/schema commitment requires separate explicit approval; any exit gate relying on that shared API must verify approval. Unresolved entries must not be silently implemented or replaced locally. The approved Job Compliance publication envelope does not approve a proposed shared decision envelope.

| Canonical operation | Meaning | Canonical owner | CL-06 consumers | Reusable mechanism | Local policy remains | Invocation point | Must not be duplicated |
|---|---|---|---|---|---|---|---|
| SH-001 `resolveAuthenticatedActor` (Confirmed) | trusted actor context | Identity & Access | all four | session/request resolution | attempted hiring action | every protected entry | feature-local current-user helper |
| SH-002 `authorizeResourceAction` (Confirmed) | permission decision | Role / Authority | all four | typed decision/RLS semantics | action vocabulary + owner facts | before protected action | local org-role policy |
| SH-003 `queryOwnerFacts` (Proposed ruling) | minimum relationship facts | Each source Module | all four | DTO contract pattern | exposed facts | cross-module auth/gates | universal cross-domain repository |
| SH-005 `resolveEntitlement` (Confirmed) | effective perk/limit/boost | Track Subscription & Entitlement | Candidate Application; org only after ruling | typed lookup | business effect | gated feature read | premium/boost booleans |
| SH-006 `consumeMeteredEntitlement` (Confirmed) | atomically consume quota and record proof | Track Subscription & Entitlement | Candidate Application | immutable usage + atomic counter | when application counts | application commit | local application counter |
| SH-011 `evaluateComplianceHold` (Confirmed) | active reusable stop signs | Admin Review / Compliance Hold | all four | hold query | effect on owner lifecycle | before sensitive/public transition | local blocked flags |
| SH-012 `requestComplianceHold` (Confirmed), SH-013 `releaseComplianceHold` (Confirmed) | create/release authoritative hold | Admin Review / Compliance Hold | Job Compliance and others | idempotent hold command | evidence/reason/scope | review paths | CL-06 hold tables |
| SH-021 `evaluateJobCompliance` (Confirmed) | authoritative posting decision | Job Compliance | Organization Hiring, Search | Module public interface | employment rule policy | publication/edit | compliance logic elsewhere |
| SH-017 `resolveVerificationRequirements` (Confirmed), SH-018 `evaluateVerificationReadiness` (Confirmed) | requirement/readiness decision | Trust Verification / Screening | Organization Hiring, Candidate Application | Module public interfaces | action-specific composition | verified-only gates | badge/provider inference |
| SH-015 `returnDecisionResult` (Proposed ruling) | common allow/deny/warning/review envelope | Shared contract; policy owner varies | decision owners | response shape | policy and reason codes | gate interfaces | generic readiness engine |
| SH-029 `appendAuditEvent` (Confirmed) | generic audit proof | Audit / Event Ledger | all four | append-only ledger | auditable action | after significant action | local AuditEvent |
| SH-030 `recordSensitiveAccess` (Confirmed) | generic sensitive access proof | Audit / Event Ledger | Candidate, Interview/admin | access audit | sensitivity/reason | resume/interview access | local AccessAuditLog |
| SH-031 `appendDomainLifecycleEvent` (Confirmed) | shared insert mechanics for domain ledgers | Shared persistence mechanism; each domain owns truth | Job Interview; future explicit ledgers | append mechanics | domain vocabulary | owner transition | universal domain-event table |
| SH-041 `requestNotification` (Confirmed) | request delivery | Notification | all four | delivery command | event meaning/safe payload | after owner event | email/SMS/push implementation |
| SH-043 `resolveNotificationRecipients` (Confirmed) | source recipient facts + channel routing | Source context owner plus Notification | Organization/Interview/Application | contract | org preference meaning | before request | global org policy in Notification |
| SH-044 `executeIdempotentCommand` (Confirmed) | prevent duplicate side effects | Platform application infrastructure | retryable mutations | idempotency claim/result | command semantics | mutation boundary | ad-hoc idempotency |
| SH-046 `publishDomainEvent` (Confirmed), SH-045 `deduplicateDomainEvent` (Confirmed) | outbox/inbox event delivery | Platform event/outbox infrastructure; Platform event infrastructure; consumer owns inbox | all four | event mechanics | event meaning | after commit / before consume | fire-and-forget |
| SH-047 `enqueueReliableJob` (Confirmed), SH-048 `executeRetryWithBackoff` (Confirmed) | durable background work | Shared queue infrastructure; Shared queue/platform infrastructure | compliance, parsing, projection, expiry, integrations | queue/retry/DLQ | retryability/compensation | async work | local queue framework |
| SH-049 `orchestrateWorkflowSteps` (Confirmed) | saga runner | Workflow-owning Module using shared runner | publication/application/interview | runner | steps/compensation | multi-owner flow | generic hiring truth |
| SH-051 `acquireAggregateLock` (Confirmed), SH-052 `withOptimisticConcurrency` (Confirmed) | concurrency protection | Shared persistence infrastructure | all four | lock/version mechanism | aggregate invariant | mutation | ad-hoc lock tables |
| SH-053 `transitionLifecycleState` (Confirmed) | state transition mechanics | Shared mechanism; lifecycle owner supplies policy | all four | helper | transition matrix | owner mutation | global state machine |
| SH-055 `runDeadlineExpiration` (Confirmed) | scheduled expiry/closure | Shared scheduler/queue infrastructure | Organization Hiring, Job Interview | scheduler | Job close/interview expiry | worker | custom cron framework |
| SH-077 `buildCanonicalTextSnapshot` (Confirmed), SH-072 `hashCanonicalPayload` (Confirmed) | deterministic compliance input | Shared text canonicalization mechanism; Shared security/cryptography capability | Job Compliance | canonicalization/hash | included Job fields | before check | duplicate hash/text utilities |
| SH-080 `manageVersionedRules` (Confirmed), SH-081 `runPatternScanner` (Proposed ruling) | rule/scanner mechanics | Each policy Module using shared versioning mechanism; Shared scanner mechanism; policy owner unresolved | Job Compliance | effective-date/scanner runtime | employment rules/severity | compliance evaluation | generic policy truth |
| SH-082 `validateUploadedFile` (Confirmed), SH-083 `scanFileForMalware` (Confirmed) | file safety | Media / File Access | Organization/Candidate | media pipeline | business attachment context | upload | local MIME/malware code |
| SH-127 `requestMediaAccess` (Proposed ruling; caller binding required), SH-088 `manageTemporaryAccessGrant` (Confirmed) | temporary private access | Media / File Access; Shared grant mechanism; each domain owns its record | Candidate | grant/signed URL | resume authorization | after candidate decision | local resume signer |
| SH-090 `attachValidatedMedia` (Confirmed) | attach ready asset to context | Contextual domain Module; Media owns asset truth | Organization/Candidate | attachment contract | role/meaning | after media readiness | storage mutation shortcut |
| SH-091 `requestSearchProjectionRefresh` (Confirmed) | enqueue search update/remove | Search / Public Visibility | Organization/Candidate; compliance effects | Search public API | source inclusion | source/readiness change | direct Typesense |
| SH-094 `buildSourceProjection` (Confirmed) | owner-built sanitized projection | Each source Module | Organization/Candidate | projection pattern | fields/privacy | before Search refresh | Search reconstructing truth |
| SH-096 `enumerateSubjectData` (Confirmed), SH-095 `executePrivacyInstruction` (Confirmed), SH-097 `evaluateRetentionRequirement` (Confirmed) | privacy target protocol | Each data-owning Module through Privacy-defined interface; Privacy orchestrates; each data owner executes; Data owner supplies facts; Privacy records exemption | all four | request/result contract | local erase/retain mapping | Privacy worker | local PrivacyRequest flow |
| SH-113 `ensureContextThread` (Confirmed) | context-bound thread | Messaging | Candidate, Interview | Messaging API | participant/context facts | application/interview | Thread ownership |
| SH-067 `invokeCalendarProvider` (Confirmed) | provider-neutral calendar call | Booking & Calendar | Job Interview | adapter | interview meaning | after source commit | direct Cronofy call |
| SH-120 `normalizeJurisdictionContext` (Proposed ruling) | normalized jurisdiction DTO/evidence | Shared normalization mechanism; each jurisdiction-dependent owner retains evidence interpretation | Job Compliance | shared normalization | rule applicability | production jurisdiction-aware evaluation; approved owner/interface required | local normalizer replacing the shared normalization mechanism |
| SH-114 `provisionOneToOneProfile` (Confirmed) | idempotent one-to-one profile creation | Each profile Module using shared provisioning mechanism | Candidate Application | provisioning | candidate opt-in/defaults/lifecycle | CandidateProfile creation | local duplicate provisioning mechanism |
| SH-125 `recordDomainAccessEvent` (Confirmed) | domain access proof append | Domain owner | Candidate Application | shared append-only mechanism | ResumeAccessLog meaning | approved resume access outcome | generic audit replacing resume proof |
| SH-076 `normalizeAndHashIdentifier` (Confirmed) | sensitive identifier normalization/hashing | Shared security/cryptography capability | Candidate Application | hashing | captured identifiers and evidence policy | access metadata preparation | local identifier hash utility |
| SH-068 `invokeVideoProvider` (Confirmed) | provider-neutral video call | Video Infrastructure | Job Interview | adapter | interview room need | video interview | direct Daily call |

Classification matters: platform primitive ≠ domain public interface; shared response contract ≠ shared policy; shared mechanics ≠ shared truth.

## 12. Cross-Module Data Flows

### Organization creation

```text
actor
→ Identity
→ Organization Hiring validates
→ Organization write + canonical owner/membership facts
→ Role/Authority facts available
→ audit/event effects
→ organization verification readiness (UNRESOLVED owner)
→ Organization Hiring alone activates when permitted
```

### Job draft → public Job

```text
authorized OrganizationMember
→ Organization Hiring Job draft/edit
→ Taxonomy validation
→ ready Media attachment if any
→ requestJobPublication(owner-issued opaque Job expectedConcurrencyToken)
→ Job = pending_compliance_review
→ Job Compliance canonical snapshot + applicable rules
→ check + findings + disclosure proof
→ Job Compliance DecisionResult
→ Organization Hiring applies result to Job lifecycle/mirror
→ if public-ready: Search refresh
→ Notification/Audit/Ops effects
```

Scanner failure keeps Job non-public and produces retry/ops evidence. It is neither approval nor legal rejection.

### Material Job edit

```text
authorized edit
→ Organization Hiring writes source change
→ materiality rule says prior approval invalid
→ safe non-public/review state
→ new compliance evaluation
→ apply new decision
→ Search refresh/removal
```

### Application submission

```text
CandidateProfile actor
→ fail-closed application eligibility context from Organization Hiring
→ Hold gate
→ Track quota resolve/consume
→ Trust readiness if verified-only
→ unique (jobId,candidateProfileId)
→ idempotent JobApplication write
→ attach only ready/clean Media
→ resume parse job if applicable
→ notification/thread/event effects
```

The Track usage and application outcome require a defined race-safe/idempotent protocol.

### Resume parse → candidate projection

```text
JobApplication + matching JobApplicationMedia exist
→ Media ready + clean
→ parse worker
→ ResumeParseResult
→ approved metadata derivation
→ CandidateSearchProjection
→ candidate visibility/privacy gate
→ Track boost read
→ Search refresh
```

Raw resume text is excluded from Search by default.

### Recruiter application view

```text
org actor
→ Role/Authority using Organization facts
→ Candidate Application confirms app belongs to org Job
→ privacy-shaped detail
→ JobApplicationViewEvent
→ viewedAt/status summary per ruled semantics
→ optional Track-gated candidate view insights
```

### Resume view

```text
org actor
→ Role/Authority
→ Candidate Application app/org/media/reason check
→ optional OrganizationFeatureAccess only after owner ruling
→ Media readiness
→ Candidate contextual allow
→ Media grant/signed URL
→ ResumeAccessLog
→ AccessAuditLog + MediaAccessEvent
```

### Application → interview

```text
authorized recruiter
→ Candidate Application says interviewable
→ Job Interview validates application/org/candidate consistency
→ JobInterview + JobInterviewEvent
→ optional request to Candidate Application to advance stage
→ Messaging/Notification
→ Video/Calendar requests from committed interview state
```

Job Interview never writes application stage/status directly.

## 13. Cross-Cluster Bridges

| Source | Destination | Transfer | Authoritative owner | Interface/event | Forbidden coupling |
|---|---|---|---|---|---|
| CL-01 Identity | CL-06 | actor/security assurance | Identity | actor/step-up operations | CL-06 auth tables |
| CL-01 Role | CL-06 | permission decision | Role / Authority | authorization + owner facts | local role interpretation |
| CL-01 Track | Candidate | quota/perks/boost | Track | resolve/consume | local premium/counter |
| CL-02 Taxonomy | Org/Job/Candidate/Compliance | accepted terms/triggers | Taxonomy | validation/requirements | hardcoded category semantics |
| CL-02 Search | Org/Job/Candidate | projection execution/query | Search | refresh/query | direct Typesense |
| CL-03 Trust | Org/Candidate | requirements/readiness | Trust Verification | requirement/readiness | badge/provider truth inference |
| CL-05 Media | Org/Candidate | private files/grants | Media | media APIs | local storage/signing |
| CL-05 Video | Interview | room/token | Video Session | video API | room truth in Interview |
| CL-05 calendar | Interview | calendar writeback/result | calendar owner | provider-neutral port | provider payload domain types |
| CL-07 Messaging | Candidate/Interview | context thread | Messaging | SH-113 ensureContextThread (Confirmed) | Thread truth |
| CL-07 Notification | all CL-06 | delivery | Notification | SH-041 requestNotification (Confirmed) | channel delivery |
| CL-08 Privacy | all CL-06 | erase/export/restrict instruction | Privacy orchestrates; owners execute | target protocol | direct Privacy DB writes |
| CL-09 Holds | all CL-06 | stop sign | Holds | evaluate/request/release | local block system |
| CL-09 Audit | all CL-06 | audit/access evidence | Audit | append/record | domain ledger replacement |
| CL-09 Ops | all CL-06 | operational diagnostics | Ops | log/failure/metrics | business-state replacement |

## 14. Authentication and Authorization

Every protected flow starts with SH-001 `resolveAuthenticatedActor` (Confirmed). Role / Authority interprets permissions; CL-06 supplies the minimum relationship facts:

- OrganizationMember role assignment;
- Job → Organization ownership;
- JobApplication → Job → Organization;
- CandidateProfile → User ownership;
- JobInterview → application/org/candidate;
- participant identity/role where relevant.

Sensitive/admin actions include ownership/member changes, organization suspension/archive, compliance rule activation/override, resume access, sensitive support/admin reads, and destructive privacy execution. Use step-up when root policy requires it.

RLS is defense in depth. RLS predicates must match server Role / Authority semantics rather than implement a contradictory second permission system.

## 15. Compliance and Readiness Composition

### Job publication

Compose actor + authority + Organization/Job state + Holds + taxonomy/jurisdiction + Job Compliance decision + applicable Trust requirement + visibility. Organization Hiring owns the resulting lifecycle.

### Candidate application

Compose CandidateProfile state + Job application facts + Track allowance/quota + Trust readiness for verified-only Jobs + Holds + Media attachment readiness.

### Resume access

Compose authority + application→Organization ownership + declared access reason + Media readiness + optional organization feature gate **only after owner resolution** + Candidate authorization + Media grant + ResumeAccessLog + generic access audit.

### Organization verification

Registry notes make legal business identity, authorized representative, permissible purpose and related verification MVP concerns, but no confirmed owner/schema exists. Do not introduce `isVerifiedOrganization`. See U-CL06-01/02.

## 16. Events, Queues, Jobs, and Workflow Orchestration

Use transactional outbox/inbox. Event payloads are minimized, versioned, correlated and privacy-classified. Audit events are not domain integration events.

Likely event families:

```text
organization.created / status_changed / membership_changed
job.created / materially_updated / publication_requested / status_changed / closed
job_compliance.evaluation_requested / decision_changed / review_required / evaluation_failed / rule_activated
application.submitted / viewed / status_changed / stage_changed / withdrawn
resume.parse_requested / completed / failed / accessed
candidate_projection.changed
interview.proposed / scheduled / rescheduled / cancelled / completed / no_show / expired
interview.participant_responded
```

Required/likely workers:

- Job Compliance evaluation;
- compliance rescan/backfill after rule change;
- Job close-time worker;
- resume parser;
- candidate projection worker/removal worker;
- interview proposal expiry;
- interview integration retry/reconciliation;
- Privacy target executors.

Retry only technical/provider failures. Domain denial is not retryable infrastructure failure. Exhausted retries produce observable ops records while source state remains accurate.

Concurrency protection is required for ownership/member role changes, Job publish/edit races, application quota+duplicate submission, application transitions, interview reschedule/cancel, participant responses.

## 17. Provider Integrations

### Organization verification

Owner and schema are unresolved. Required future pattern:

```text
verification owner
→ provider-neutral port
→ Checkr/selected adapter
→ verified + deduped callback/result
→ normalized result
→ verification-owner state
→ Organization Hiring consumes readiness
```

No Checkr object becomes `Organization` truth.

### Job Compliance scanner

`compromise` and `natural` are libraries, not legal authorities.

```text
Job Compliance
→ canonical Job snapshot
→ versioned rule set
→ scanner runtime
→ raw matches
→ Job Compliance classification
→ checks/findings/disclosure
→ review where uncertain
```

Unknown/uncertain values never silently pass.

### Resume parser

Parser output is normalized into ResumeParseResult. Failure is parser/ops state, not candidate quality or hiring recommendation.

### Calendar

```text
Job Interview
→ provider-neutral calendar port
→ calendar owner
→ Cronofy/other adapter
→ verified/deduped normalized result
→ local interview sync attachment state if ruled
```

### Video

```text
Job Interview
→ Video Session
→ video adapter
→ normalized room result
→ JobInterviewVideoRoom (Video-owned)
→ Interview reacts to readiness/failure
```

Provider tokens/payloads remain outside JobInterview truth.

## 18. Search / Projection Boundaries

Organization Hiring remains source truth for Organization/Job. Search receives projection only when source lifecycle, Job Compliance, Holds, privacy/moderation, verification and visibility allow public exposure.

Candidate Application owns CandidateSearchProjection. Search may index approved metadata such as skills, normalized titles, experience band, coarse location and remote preference. Raw resume text is not indexed by default.

De-index triggers include Organization suspended/archived, Job paused/closed/rejected/archived, compliance approval revoked, applicable hold, CandidateProfile/search participation disabled, CandidateSearchProjection hidden/erased/disabled, privacy erasure/restriction, moderation action, or other ruled public-readiness change.

Search never reconstructs compliance/privacy/eligibility from stale index fields.


## 19. Media / File Boundaries

Contextual business meaning and file mechanics are intentionally split.

| Context record | Contextual owner | File/mechanics owner |
|---|---|---|
| `OrganizationMedia` | Organization Hiring | Media / File Access |
| `JobMedia` | **Proposed:** Organization Hiring | Media / File Access |
| `CandidateProfileMedia` | Candidate Application | Media / File Access |
| `JobApplicationMedia` | Candidate Application | Media / File Access |

Media owns `MediaAsset`, upload policy/session, MIME/type validation, malware scanning, image processing/EXIF-GPS scrubbing, private storage, temporary grants, signed URLs, and generic media-access events.

Resume rules:

- use candidate resume/CV upload context;
- evidenced format policy is PDF/DOCX;
- evidenced size limit is 5 MB;
- private storage only;
- no permanent public URL;
- no parsing/display before ready + clean scan;
- contextual authorization precedes grant issuance.

`CandidateProfile.resumeUrl` conflicts with this architecture and must be removed, deprecated, or explicitly defined as a non-authoritative projection before production use.

## 20. Privacy / Retention

Privacy / Data Erasure owns `PrivacyRequest`, `DataErasureJob`, target orchestration, export bundling, and `DataRetentionExemption`. Each CL-06 source owner implements enumeration and execution only for its own data.

### Organization Hiring executor

Enumerate and handle Organization personal/contact fields where subject-linked, membership rows, Jobs, organization notification settings, and contextual media joins. Retain/anonymize hiring records where legal/compliance obligations require it.

### Job Compliance executor

Enumerate checks, findings, reviewer metadata, disclosure records, matched previews/hashes, and rule-application proof. Compliance/legal retention may apply.

### Candidate Application executor

Enumerate CandidateProfile, applications, answers/cover letters, attachment relations, ResumeParseResult including extracted text, ResumeAccessLog, JobApplicationViewEvent, CandidateSearchProjection, and candidate media joins. Request Media object deletion and Search removal where allowed.

### Job Interview executor

Enumerate interviews, participants, event metadata, local provider references, and delegate linked message/video/provider deletion to their owners.

Rules:

- product archive/delete is not legal erasure;
- owner supplies retention facts; Privacy records exemptions;
- retained proof should be minimized/anonymized where permitted;
- provider deletion is requested through provider owner;
- re-running an instruction is idempotent;
- proof that erasure/execution occurred is not casually destroyed.

Unresolved retention includes raw `ResumeParseResult.extractedText`, Organization/Job records, and interview history.

## 21. Audit and Observability

### Audit

Use generic SH-029 `appendAuditEvent` (Confirmed) for significant changes such as organization ownership/member-role changes, Job publication/rejection, compliance rule activation/retirement, human review/override, and sensitive privacy execution.

Use SH-030 `recordSensitiveAccess` (Confirmed) for resume and other restricted application/interview access as required.

`ResumeAccessLog` and `JobInterviewEvent` remain domain truth even when generic Audit/Access records also exist.

### Observability

Use request/correlation IDs, structured logs, metrics, queue telemetry, exception capture, integration failure records, and incident correlation.

Telemetry must redact raw resume text, private application answers unless essential, protected-class matched text beyond approved preview/hash, secrets/tokens, provider payloads, and unnecessary exact personal data.

Operational records never replace Job/Application/Interview/Compliance status.

## 22. Security Boundaries

1. Runtime-validate every external/request payload server-side.
2. Resolve authenticated actor and server-side authorization for every mutation and sensitive query.
3. Validate relationship facts; never trust client-supplied Organization/Job/Application/Interview IDs as proof.
4. Keep resumes and application attachments private.
5. Issue short-lived grants/URLs only after contextual authorization.
6. Exclude raw resume text from analytics/logs/search by default.
7. Keep provider secrets/webhook signing keys server-side.
8. Verify, dedupe, translate, and replay-protect provider callbacks.
9. Use idempotency on retryable side-effecting commands.
10. Use concurrency controls on ownership, publication, quota, pipeline, and interview transitions.
11. Minimize Job Compliance matched-text evidence.
12. Use safe notification templates instead of raw application/resume bodies.
13. `CandidateProfile.trustScore`, `verifiedAt`, and `verificationExpiresAt`, if retained, are non-authoritative caches/projections only. They cannot supply Trust truth or gate verified workflows (CL-06-R010).
14. No support/admin broad bypass of resume privacy.
15. RLS and server authorization must have parity tests.

## 23. Testing Architecture

### Unit tests

Test owner lifecycle transitions, domain invariants, decision reason codes, redaction/data shaping, material Job edit invalidation, resume authorization, and interview context consistency.

### Public-interface contract tests

Prove:

- Organization owner-fact DTO compatibility with Role / Authority;
- Job Compliance DecisionResult semantics;
- Track quota/entitlement contract;
- Trust readiness contract;
- Media grant/access contract;
- Search projection contract;
- Privacy executor result contract;
- Video/calendar normalized result contracts.

### Lifecycle tests

Matrix-test Organization, Job, Job Compliance rule/check/disclosure, CandidateProfile, JobApplication status+stage, ResumeParseResult, CandidateSearchProjection, JobInterview, and participant states.

### Cross-Module integration tests

At minimum:

1. no Job becomes publicly searchable before allowed Job Compliance decision;
2. material Job edit invalidates/rechecks approval as ruled;
3. concurrent applications respect unique Job constraint and Track quota;
4. recruiter cannot view another Organization’s applicants/resumes;
5. signed resume access never precedes contextual authorization;
6. successful resume access records domain + generic proof;
7. raw resume text never enters Search projection by default;
8. Job Interview cannot mutate JobApplication directly;
9. parent application invalidation produces the ruled interview effect;
10. privacy instruction hides/removes candidate projection and delegates Media deletion.

### Provider / concurrency / E2E

Provider tests cover signature, dedupe, unknown-status translation, reconciliation and unavailable states. Concurrency tests cover ownership/member changes, publish/edit, application quota, duplicate parse, interview reschedule/cancel and duplicate callbacks.

Critical E2E:

```text
Organization → Job draft → Compliance → public Job
CandidateProfile → private resume → application
Recruiter → applicant detail → authorized resume
Application → interview → participant response → provider handoffs
Privacy instruction → candidate de-index / owner executor result
```

## 24. Invariants

### Rules coding agents must never violate

1. CL-06 is not a source-of-truth owner.
2. Organization Hiring alone mutates Organization and general Job lifecycle.
3. Job Compliance alone owns posting rules/checks/findings/disclosure policy.
4. Candidate Application alone mutates CandidateProfile and JobApplication lifecycle.
5. Job Interview alone mutates JobInterview lifecycle.
6. OrganizationMember row/role assignment is Organization Hiring truth; Role / Authority interprets.
7. Possession of IDs never proves authority.
8. Job Compliance must not screen candidates or own FCRA adverse-action screening truth.
9. Public Job publication/indexing requires the authoritative compliance decision.
10. Technical scan failure never means approved or legally rejected.
11. `Job.complianceStatus`, if retained, is not an independent policy engine.
12. Job compensation is business truth; disclosure is separate compliance proof.
13. CandidateProfile, not User, is applicant identity.
14. One CandidateProfile cannot have duplicate applications to the same Job.
15. Application limits come from Track.
16. Candidate boosts/view perks come from Track.
17. TrustBadge is display; Trust Verification readiness is truth.
18. Resume files remain private MediaAssets.
19. Candidate Application authorizes resume access before Media grant/URL issuance.
20. ResumeAccessLog, MediaAccessEvent, and AccessAuditLog remain separate.
21. Resume parsing never produces automated hiring recommendations.
22. Raw resume text is not indexed by default.
23. CandidateSearchProjection remains source-owned; Typesense is projection.
24. Search never decides compliance/privacy/eligibility.
25. JobApplication status/stage remain Candidate Application truth.
26. Job Interview may request but never directly write application stage/status.
27. JobInterview is not Booking.
28. Video Session owns interview room mechanics.
29. Provider payloads do not become domain types.
30. Provider failure is operational evidence, not arbitrary lifecycle overwrite.
31. ComplianceHold is the reusable stop sign.
32. AuditEvent/AccessAuditLog do not replace domain ledgers/access proof.
33. Privacy owns privacy orchestration; CL-06 owners execute locally.
34. Search, Privacy, Notification, Moderation or orchestration workers may not directly mutate another owner’s tables.
35. Shared scanner/version/hash/queue/grant mechanics do not move policy ownership.
36. Provider-event dedupe may share mechanics but retains provider/domain-specific truth.
37. Sensitive telemetry must be minimized/redacted.
38. Do not use the unexplained multi-Organization view-event relation as source truth; schema correction and migration-baseline verification belong to a later database pass.
39. Unresolved Organization verification/ATS entitlement questions may not become convenience booleans.
40. Architecture must be updated before implementation relies on a changed binding decision.

## 25. Prohibited Duplicate Implementations

Do not create:

- feature-local auth/current-user helpers duplicating SH-001 `resolveAuthenticatedActor` (Confirmed);
- `canRecruiterViewResume`, `canPublishJob`, or org-role helpers that reimplement Role / Authority;
- local candidate plan/quota/boost tables or booleans;
- local Job/Application block tables duplicating ComplianceHold;
- salary/EEOC/fair-chance validators inside Organization Hiring/Search;
- a generic Job Compliance rule engine that owns unrelated policy;
- duplicate canonical text/hash infrastructure;
- `resumeStorageService`, local presigned URL signer, MIME validator, or malware scanner;
- permanent resume URLs as access mechanism;
- a second generic access-grant table;
- direct Typesense clients/index writers in Organization/Candidate modules;
- a local SearchUpsertEvent equivalent;
- Notification delivery/channel retry code;
- local generic AuditEvent/AccessAuditLog;
- JobApplication mutation logic inside Organization Hiring/Job Interview;
- Booking-backed interview lifecycle;
- local video-room provider logic;
- `ProcessedInterviewCalendarEvent` merely to bypass calendar owner;
- local PrivacyRequest/DataErasureJob orchestration;
- a generic “hiring readiness engine” absorbing Job Compliance, Trust, Track, Holds and Authority.

## 26. Deferred / Unresolved Decisions

### U-CL06-01 — Organization verification owner

**Question:** Which Module owns business identity and authorized-representative verification?  
**Why unresolved:** MVP notes require it, but no authoritative schema/owner exists.  
**Missing:** approved verification model, owner, provider-neutral contract.  
**Blocks:** verified Organization activation/restricted hiring.

### U-CL06-02 — Permissible-purpose / FCRA organization certification

**Question:** Which versioned record proves employment permissible purpose/FCRA certification?  
**Why unresolved:** ConsentLog proves acceptance but does not by itself establish the organization-specific authorization lifecycle.  
**Blocks:** production workflows legally dependent on that certification.

### U-CL06-03 — Canonical Organization owner representation

`Organization.ownerUserId` and owner membership both exist. Define one canonical truth and transfer/removal invariant. **Blocks ownership transfer.**

### U-CL06-04 — Organization ATS commercial entitlement

Who owns `OrganizationFeatureAccess`, and how does it relate to Track? Shared Operations explicitly marks Organization commercial entitlement unresolved. **Blocks monetized applicant tracker/resume viewer/candidate-search gates.** Basic non-monetized MVP must not invent the gate.

### U-CL06-05 — Job Compliance effective decision

Define source truth and precedence across latest check, disclosure, Job summary and ComplianceHold; define warning/failed mapping. **Blocks production publication.**

### U-CL06-06 — Historical rule-set proof

**Resolved evidence invariant (CL-06-R007):** every production-grade evaluation preserves immutable exact evaluated-input proof (canonical snapshot or immutable reconstructible source-version reference) plus its hash, and the complete identities/versions of every applied rule, including zero-finding approvals. Scanner version, evaluation time and material normalized jurisdiction input remain traceable after Job/rule edits. Persistence design, retention details and schema/migrations require a later approved pass; production cannot claim this invariant is implemented by the current schema alone.

### U-CL06-07 — `CompensationPeriod` ownership and `EmploymentType.contract`

Compensation-period vocabulary stewardship is resolved to Organization Hiring by WA-R010. P03 is approved by WA-R013: fixed-term employment and independent-contractor work are distinct concepts. **Schema conversion, legacy clarification and legal-rule evidence remain prerequisites.**

### U-CL06-08 — Classification join persistence

Taxonomy owns vocabulary/semantics and entity Modules own context, but exact attach/detach persistence owner is inconsistent. **Blocks code placement, not conceptual ownership.**

### U-CL06-09 — Overlapping direct/projection fields

**Resolved Candidate authority (CL-06-R010):** `CandidateProfile.resumeUrl` is not canonical resume truth; MediaAsset plus Candidate attachment/access context supply that truth. `trustScore`, `verifiedAt` and `verificationExpiresAt`, if retained, are non-authoritative caches/projections and cannot gate verified workflows. Remove/deprecate/retain cleanup remains for a later pass. `Organization.logoUrl` remains non-authoritative file data with its existing cleanup question preserved.

### U-CL06-10 — Candidate visibility/search participation

Define precedence between `CandidateProfile.isVisible` and CandidateSearchProjection status and whether explicit discoverability consent/preferences are required. **Blocks candidate search activation.**

### U-CL06-11 — Application transition/event semantics

Define legal status/stage transitions, timestamps, terminal behavior, and whether a JobApplicationEvent ledger is required. **Blocks full recruiter pipeline.**

### U-CL06-12 — Application view semantics

**Confirmed ownership (CL-06-R010):** Candidate Application owns JobApplicationViewEvent application-view truth, with at most one Organization context (CL-06-R008). **Still unresolved:** precise event qualification and `viewedAt`/`status=viewed` summary semantics; the proposed append/first-view projection behavior is not approved by the ownership ruling.

### U-CL06-13 — Resume access semantics and raw text retention

Define whether ResumeAccessLog means grant issuance, actual read, or both; define encryption/retention of `ResumeParseResult.extractedText`. **Blocks compliance-grade production evidence/retention.**

### U-CL06-14 — Interview participant ownership/removal

**Confirmed ownership (CL-06-R012):** Job Interview owns `JobInterviewParticipant`, `JobInterviewParticipantRole` and `JobInterviewParticipantStatus`. Removal/revocation, exact role eligibility and candidate participant invariants remain unresolved and continue gating participant behavior.

### U-CL06-15 — Interview transition/reschedule policy

Define transition matrix, mutate-vs-successor reschedule semantics and successor cardinality. **Blocks advanced rescheduling.**

### U-CL06-16 — Calendar capability ownership for hiring

**Owner resolved (CL-06-R013):** Confirmed SH-067 `invokeCalendarProvider` (Confirmed) is owned by Booking & Calendar, including connections, invocation, synchronization, webhook verification/dedupe and normalization. Job Interview owns schedule policy and supplies context; no second provider owner is permitted. Only exact JobInterview-local external event/sync/error-field meaning remains unresolved.

### U-CL06-17 — Retired placement claim

CL-06-R018 retires the obsolete field-placement blocker: the referenced relation fields are inside model braces. Overall schema validity is not certified. The R008 many-to-many meaning discrepancy and R009 project-level migration-baseline question remain separate.

## 27. Architecture Decision Summary

Binding:

- CL-06 coordinates four Deep Modules and owns no lifecycle.
- Organization Hiring owns Organization, OrganizationMember row/role assignment and Job lifecycle.
- Role / Authority owns permission interpretation.
- Job Compliance owns posting rules/checks/findings/disclosure policy and returns a decision.
- Candidate Application owns CandidateProfile, JobApplication status/stage, resume business authorization/proof and CandidateSearchProjection.
- Job Interview owns JobInterview, JobInterviewEvent, JobInterviewParticipant and participant role/status enums; remaining participant policies stay unresolved.
- Media owns file safety/storage/grants; contextual Modules own attachment meaning/business access.
- Search owns indexing; source owners own projection inputs/readiness.
- Track owns application limits, boosts and candidate perks.
- Trust Verification owns verification truth.
- Holds, Audit, Privacy, Notification, Messaging, Video and Ops retain their existing ownership.
- JobInterview is never implemented as Booking.
- Provider data is normalized behind owner adapters.
- Section 26 blockers must be resolved before their affected production behavior.

## 28. Coding-Agent Usage

Before changing CL-06, read:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry/Architecture;
5. this Cluster `architecture.md`;
6. this Cluster `build-plan.md`;
7. target Module `module-architecture.md`;
8. target Module `implementation-plan.md`;
9. relevant dependency Module public-interface sections;
10. progress tracker;
11. current Prisma schema/migrations;
12. architecture decisions resolving any relevant `U-CL06-*`.

Confirm the previous feature exit gate before starting the next feature. Never resolve an Unresolved Decision implicitly in code.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.

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

## WA-R043–047 — Integrated CL-06 owner contracts

These applied owner rulings supersede earlier unresolved/proposed statements only for the same concerns. Hiring owns business verification evidence, membership/owner transfer, Job history and contextual joins (WA-R043). Compliance owns reproducible input/rule/check/review evidence; Hiring alone publishes from a current qualified decision (WA-R044). Candidate owns opt-in projection state, application graph/history, view/resume evidence and parser attempt lineage (WA-R045). Interview owns invitation responses/revocation and successor scheduling, never application stages or provider mechanics (WA-R046). Each owner implements its constrained Moderation/Privacy adapter and registered sensitive-action facts (WA-R047).

P17/P18 under WA-R042 settle discovery default-off and no timer expiration while rejecting acceptance of past slots. Participant-facing service Order conversations under P19 do not replace hiring interview/applicant context. Cross-Cluster consumers must qualify typed contracts before activation. Root rails, forward schema/history constraints, legal rule/retention content, provider capabilities and exact event/DTO fixtures remain scoped prerequisites, not production-readiness claims.


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

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration

Hiring and Candidate expose distinct minimized purpose-approved AI source descriptors, stable owner enumeration and atomic contextual assignment receipts; P17 opt-in is not AI-purpose consent.

## WA-R071 — Purpose-specific Location facts and disclosure

Hiring public geography consumes approved coarse Location fields; Interview meetingLocation/meetingPhone use a distinct participant-purpose policy and durable proof. Recruitment role is not blanket exact access.

## WA-R072 — Hiring compatibility and forward migration stewardship

Hiring owns JobMedia and Organization/Job history; Candidate owns contextual media joins and application view/access history; Interview owns participants and invitation/response history. Additive/backfill/parity/removal sequence requires proven original identities and preserves history; database D gates activation.

## WA-R073 — Interview access interval and bounded credentials

Invitation acceptance requires future startsAt under P18; joining accepted current interviews requires startsAt <= serverNow < endsAt. No timer expiry or implicit pre/post grace; new timing policy can change future behavior without rewriting history.

## Domain bridge integration — 2026-10-15

Apply WA-R078; WA-R080 from `context/reconciliation/platform-architecture-rulings.md` only to this Cluster's named owner/consumer boundaries. The affected Module architectures incorporate the typed contracts. R077 assigns private checkout tax evidence to Order and tax interpretation to Payment; R078 uses the existing Track command with durable owner intents; R079 keeps optional reverse prize display disabled; R080 binds owner enumerators and scoped Taxonomy recipients. No cross-Cluster repository access, generic tax-location authority, duplicate actor stream or AI Gig scope is introduced. Untouched concerns retain their existing owners. Review evidence is `context/reconciliation/bridge-review-domain.json`; seven families reviewed does not complete Gate 4.

## WA-R081–083 — Gate 4 bridge obligations

Coordinate the Module-owned contracts in `context/reconciliation/bridge-contract-bindings.md` and the complete inventory. Source facts, semantic commands and completion receipts are separate. Optional disabled paths do not become Cluster prerequisites. Retain all existing P01–P19, permanent SH identities, source lifecycles and external gates. No contract is frozen.

Reviewed directional families touching this Cluster: BF-009, BF-010, BF-011, BF-015, BF-017, BF-025, BF-026, BF-027, BF-033, BF-036, BF-038, BF-039, BF-040, BF-041, BF-042, BF-043, BF-045, BF-048, BF-050, BF-053, BF-054, BF-055, BF-056, BF-058, BF-063, BF-065, BF-066, BF-067, BF-068, BF-069, BF-071, BF-082, BF-089, BF-090, BF-093, BF-094, BF-100, BF-102, BF-105, BF-113, BF-114, BF-115, BF-116, BF-117, BF-129, BF-131, BF-136, BF-138, BF-146, BF-147, BF-152, BF-153, BF-154, BF-155, BF-156, BF-157, BF-158, BF-159, BF-160, BF-162, BF-163, BF-164, BF-167, BF-168, BF-169, BF-171, BF-172, BF-173, BF-174, BF-175, BF-176, BF-177, BF-178, BF-179, BF-180, BF-181, BF-182, BF-183, BF-186, BF-188, BF-191, BF-192, BF-203, BF-204, BF-205, BF-210, BF-211, BF-218, BF-221, BF-222, BF-223, BF-224, BF-225, BF-229, BF-230, BF-231, BF-232, BF-235, BF-236, BF-237, BF-240, BF-242, BF-246, BF-248, BF-249, BF-256, BF-257, BF-266.

Integrate current R068/069/075; Media invalidation uses R082 only for registered Customer/Candidate subscribers. Privacy field/action fixtures remain required despite source enumeration reconciliation. Cluster sequencing must use contract/foundation dependencies, not whole neighboring-Cluster completion.


## WA-R085–087 — Platform convergence

Current platform reconciliation covers `candidate_application_resume_privacy`, `job_compliance`, `job_interview`, `organization_hiring`. Module owners retain all lifecycles and source facts. R085 separates terminating fact inputs from composed permissions, readiness, credential issuance and Hold release; R086 locates one shared execution capability and bootstrap dependencies; R087 routes Organization commercial schema responsibility to Track without enabling monetized ATS.

Coordinate required ports and semantic fixtures before actual adapters; do not require complete upstream Clusters from a contract edge. Source commits precede outbox delivery and downstream projection/Notification/provider setup. Recovery reuses stable effect identity and cannot infer completion from acknowledgment, telemetry or a read model. The platform dependency graph records typed edges and critical cycle dispositions; action-specific external gates remain scoped.

Root architecture synthesis is conditional on the recorded Gate 5 exit and Gate 6 posture confirmation. A root build plan, runtime choice, database migration, interface freeze and parallel implementation lanes remain later prerequisites. No such implementation approval is made by this coordination appendix.
