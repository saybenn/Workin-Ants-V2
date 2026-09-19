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
| `CompensationPeriod` | **Unresolved structural owner** |
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
| SH-087 `issueSignedMediaUrl` (Confirmed), SH-088 `manageTemporaryAccessGrant` (Confirmed) | temporary private access | Media / File Access; Shared grant mechanism; each domain owns its record | Candidate | grant/signed URL | resume authorization | after candidate decision | local resume signer |
| SH-090 `attachValidatedMedia` (Confirmed) | attach ready asset to context | Contextual domain Module; Media owns asset truth | Organization/Candidate | attachment contract | role/meaning | after media readiness | storage mutation shortcut |
| SH-091 `requestSearchProjectionRefresh` (Confirmed) | enqueue search update/remove | Search / Public Visibility | Organization/Candidate; compliance effects | Search public API | source inclusion | source/readiness change | direct Typesense |
| SH-094 `buildSourceProjection` (Confirmed) | owner-built sanitized projection | Each source Module | Organization/Candidate | projection pattern | fields/privacy | before Search refresh | Search reconstructing truth |
| SH-096 `enumerateSubjectData` (Confirmed), SH-095 `executePrivacyInstruction` (Confirmed), SH-097 `evaluateRetentionRequirement` (Confirmed) | privacy target protocol | Each data-owning Module through Privacy-defined interface; Privacy orchestrates; each data owner executes; Data owner supplies facts; Privacy records exemption | all four | request/result contract | local erase/retain mapping | Privacy worker | local PrivacyRequest flow |
| SH-113 `ensureContextThread` (Confirmed) | context-bound thread | Messaging | Candidate, Interview | Messaging API | participant/context facts | application/interview | Thread ownership |
| SH-067 `invokeCalendarProvider` (Confirmed) | provider-neutral calendar call | Booking & Calendar | Job Interview | adapter | interview meaning | after source commit | direct Cronofy call |
| SH-120 `normalizeJurisdictionContext` (Unresolved) | normalized jurisdiction DTO/evidence | Shared commerce/location capability ownership unresolved | Job Compliance | shared normalization | rule applicability | production jurisdiction-aware evaluation; approved owner/interface required | local normalizer replacing unresolved shared capability |
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

Resolve structural owner of compensation-period vocabulary and whether `contract` means fixed-term employee or independent contractor. **Blocks final employment/compliance semantics.**

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
