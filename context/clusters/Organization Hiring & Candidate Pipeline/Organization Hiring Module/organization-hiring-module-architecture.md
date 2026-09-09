# Organization Hiring Module Architecture

> **Module ID:** `organization_hiring`  
> **Module name:** Organization Hiring Module  
> **Module type:** `domain`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-06 Organization Hiring & Candidate Pipeline`  
> **Document status:** implementation-grade Module architecture  
> **Audience:** coding agents, developers, reviewers, maintainers  
> **Authority:** subordinate to root Workin Ants architecture and CL-06 architecture; authoritative for implementation inside this Module unless a higher-level binding decision changes  
> **Update rule:** update this file whenever a binding ownership, lifecycle, public-contract, provider, privacy, compliance, or shared-operation decision for this Module changes. Build progress must never silently redefine architecture.

## 1. Module Header

Organization Hiring is the CL-06 source-of-truth owner for the hiring entity and formal Job lifecycle. It owns `Organization`, the `OrganizationMember` row and role assignment, and `Job` business state. Role / Authority interprets permissions; Job Compliance owns posting-compliance findings and decisions; Candidate Application owns applicant/application/resume truth; Job Interview owns interview truth.

This document inherits, rather than repeats, root platform architecture and CL-06 architecture. It is intentionally narrower than the CL-06 Cluster architecture and narrower than the Cluster build plan.

**Relationship to root architecture**

- Root architecture defines global source-of-truth rules, cross-cutting capabilities, provider isolation, privacy orchestration, search-as-projection, and shared-operation ownership.
- This Module must not override those rules locally.

**Relationship to CL-06 architecture**

- CL-06 coordinates Organization Hiring, Job Compliance, Candidate Application & Resume Privacy, and Job Interview.
- CL-06 owns no lifecycle.
- This Module owns only the Organization/Job portion of the CL-06 flow.

**Relationship to CL-06 build plan**

- Cluster Feature 01 establishes Organization membership and Job draft workspace.
- Cluster Feature 03 establishes controlled Job publication and Search handoff.
- This Module implementation plan expands only Organization Hiring work needed to satisfy those Cluster milestones and downstream contracts.

## 2. Purpose, Goal, and Transformation

### Purpose

Own the formal hiring entity and Job business lifecycle without absorbing permission, compliance, candidate, resume, interview, media, search, entitlement, notification, privacy, or provider truth.

### Goal

Transform authenticated hiring intent into:

1. an authoritative `Organization`;
2. authoritative organization membership rows and assigned `OrganizationRole`;
3. a lifecycle-managed `Job`;
4. stable public facts that adjacent Modules can consume through owner interfaces;
5. safe handoffs to Job Compliance, Trust Verification, Search, Media, Notification, Messaging, Audit, Privacy, and Holds.

### What enters

- trusted actor context from Identity & Access;
- authorization decisions from Role / Authority;
- Organization profile fields;
- OrganizationMember add/change/remove intent;
- Job title, description, employment type, location, compensation, taxonomy, visibility and closing intent;
- taxonomy assignment validation;
- Job Compliance decisions and evidence references;
- Trust Verification requirement/readiness decisions;
- ComplianceHold decisions;
- Media readiness for organization/job presentation assets;
- Search refresh acknowledgements;
- Notification/Messaging request acknowledgements;
- Privacy instructions;
- optional Organization commercial-feature decisions only after `U-CL06-04` is resolved.

### What leaves

- authoritative Organization state and versioned facts;
- authoritative membership facts;
- authoritative Job state and public-safe source projection;
- owner-fact DTOs for Role / Authority and neighboring Modules;
- publication requests to Job Compliance;
- Search refresh/remove requests;
- Notification/Messaging requests;
- audit/domain-event effects;
- privacy execution results.

### Business transformation

```text
authenticated actor
→ Organization/member facts
→ authorized Organization action
→ Organization/Job source mutation
→ required external gates
→ Organization Hiring-owned lifecycle decision
→ owner event/outbox
→ downstream owner requests
```

### Why this deserves its own Module

Organization and Job lifecycles are distinct business truths. They are consumed by many Modules but must remain stable even when compliance scanners, search indexing, file processing, notification delivery, verification providers, or applicant workflows are unavailable. A separate Module prevents those rails from becoming accidental owners of hiring entity or Job truth.

## 3. Owned Truth

### 3.1 Confirmed models and records

| Record | Meaning | Ownership |
|---|---|---|
| `Organization` | Formal hiring entity that posts Jobs and manages hiring workflows. It does not sell Offerings. | Confirmed |
| `OrganizationMember` | A User's membership row in one Organization with one assigned OrganizationRole. | Confirmed |
| `OrganizationNotificationSetting` | Organization-owned routing preference for named notification intents by channel and member-role group. | Confirmed |
| `Job` | Formal employment opportunity posted by an Organization. | Confirmed |
| `OrganizationMedia` | Business-context attachment explaining that a ready `MediaAsset` is used by an Organization. Media mechanics remain external. | Contextual meaning confirmed; persistence split follows shared media rule |
| `JobMedia` | Business-context attachment explaining that a ready `MediaAsset` is used by a Job. | Proposed application of the canonical media-join rule |
| `OrganizationCategory`, `OrganizationTag` | Organization-side meaning of accepted taxonomy attachment. | Contextual meaning only; persistence owner unresolved by `U-CL06-08` |
| `JobTag` | Job-side meaning of accepted taxonomy attachment. | Contextual meaning only; persistence owner unresolved by `U-CL06-08` |

### 3.2 Confirmed enums and statuses

| Enum | Meaning |
|---|---|
| `OrganizationStatus` | `draft`, `active`, `suspended`, `archived` |
| `OrganizationRole` | `owner`, `admin`, `recruiter` |
| `JobStatus` | `draft`, `pending_compliance_review`, `flagged_for_review`, `open`, `paused`, `filled`, `closed`, `rejected`, `archived` |
| `JobVisibility` | `public`, `private`, `invite_only` |
| `EmploymentType` | `full_time`, `part_time`, `contract`, `internship`, `temporary` |

`CompensationPeriod` appears on `Job` but its structural owner is unresolved by `U-CL06-07`. This Module may use it only after the architecture ruling confirms the vocabulary.

### 3.3 Lifecycles owned

#### Organization lifecycle

```text
draft
  ├─> active       [activation gate policy; verification portion unresolved]
  ├─> archived
active
  ├─> suspended
  ├─> archived
suspended
  ├─> active       [only after blocking condition is resolved]
  └─> archived
archived
  └─> no automatic reopen; explicit architecture/policy required
```

Organization Hiring alone writes `Organization.status`. External verification or holds may gate a transition but do not own it.

#### Organization membership lifecycle

Current source truth is row presence plus assigned role:

```text
absent
  └─> OrganizationMember(owner|admin|recruiter)
present
  ├─> role changed
  └─> removed
```

No invitation, suspension, acceptance, or membership-status model exists. Do not invent one.

#### Job lifecycle

```text
draft
  └─> pending_compliance_review
pending_compliance_review
  ├─> open
  ├─> flagged_for_review
  ├─> rejected
  └─> draft/needs-change path only if explicitly mapped
flagged_for_review
  ├─> pending_compliance_review
  ├─> rejected
  └─> open only from an approved Job Compliance decision
open
  ├─> paused
  ├─> filled
  ├─> closed
  ├─> pending_compliance_review [material edit invalidates approval]
  └─> archived only through an approved lifecycle path
paused
  ├─> open or pending_compliance_review according to freshness policy
  ├─> filled
  ├─> closed
  └─> archived
filled
  └─> archived or closed only if lifecycle policy explicitly permits
closed
  ├─> pending_compliance_review for reopen if allowed
  └─> archived
rejected
  ├─> draft/pending_compliance_review only if correction/re-review policy allows
  └─> archived
archived
  └─> terminal unless architecture explicitly introduces restoration
```

The exact Job Compliance-to-Job mapping remains blocked by `U-CL06-05`, `U-CL06-06`, and `U-CL06-07` before production publication.

### 3.4 Source-of-truth records

- `Organization` is the hiring-entity truth.
- `OrganizationMember(organizationId, userId, role)` is membership/role-assignment truth.
- `Job` is the formal Job business truth.
- `Job.compensation*` fields are offered-compensation business truth.
- `JobCompensationDisclosure` is **not** owned here; it is Job Compliance evidence/snapshot.
- `Job.complianceStatus`, if retained, is a summary mirror written only from a Job Compliance decision; it is not an independent compliance engine.

### 3.5 Domain events / ledgers

No dedicated `OrganizationEvent` or `JobEvent` model is confirmed in the current schema. This Module therefore owns event **meaning**, but uses the platform transactional outbox for integration events.

Confirmed domain-ledger ownership rule does not require inventing a ledger when one is absent. If later architecture requires replayable Organization/Job lifecycle history, add it only through an explicit architecture update.

### 3.6 Projections owned

- Organization Hiring may build versioned public-safe source projections for Organization and Job.
- It does **not** own `SearchUpsertEvent`, Typesense documents, search adapters, indexers, or search reconciliation.
- The projection builder is source-owner code; Search execution remains Search-owned.

### 3.7 Snapshots / proof owned

This Module owns no compliance-proof snapshot equivalent to `JobComplianceCheck`.
It may persist source version references needed to prove which Organization/Job version a downstream decision applied to, subject to the final schema ruling.

### 3.8 Policies and invariants owned

- Organization lifecycle transition policy.
- OrganizationMember add/change/remove invariants.
- Organization owner consistency invariant, subject to `U-CL06-03`.
- Job lifecycle transition policy.
- Job publication composition policy: Organization Hiring maps external gate decisions into its own lifecycle.
- Job material-edit invalidation policy, coordinated with Job Compliance.
- Job close-time behavior once specified.
- Organization notification preference meaning.
- Business meaning of organization/job media attachments.
- Business meaning of organization/job taxonomy attachments.

## 4. Explicit Non-Ownership

Organization Hiring must not own or duplicate the following.

| Adjacent owner | Remains outside Organization Hiring |
|---|---|
| Identity & Access | Authentication, sessions, MFA/passkeys, step-up assurance, User identity |
| Role / Authority | Permission interpretation, organization-scoped authorization policy, admin/support authority |
| Taxonomy & Classification | Controlled taxonomy vocabulary, hierarchy, normalization, requirement triggers |
| Job Compliance | Rules, scans, findings, compensation-disclosure proof, publication-compliance decision |
| Trust Verification / Screening | `VerificationRequirement`, `VerificationCheck`, TrustBadge, screening/provider workflow |
| Candidate Application & Resume Privacy | CandidateProfile, JobApplication lifecycle, pipeline stages/statuses, resume authorization, parsing, ResumeAccessLog, CandidateSearchProjection |
| Job Interview | JobInterview lifecycle, scheduling state, participant state after ruling, JobInterviewEvent |
| Media / File Access | MediaAsset, upload sessions, MIME/binary validation, malware scanning, EXIF/PDF scrubbing, storage, signed URLs, MediaAccessGrant/Event |
| Search / Public Visibility | SearchUpsertEvent, Typesense, search workers, indexing, de-indexing, query infrastructure |
| Track Subscription & Entitlement | plan, subscription, entitlement, quota, perk, boost, usage truth |
| Admin Review / Compliance Hold | ComplianceHold lifecycle |
| Audit / Event Ledger | AuditEvent, AccessAuditLog |
| Notification | Notification, NotificationDelivery, provider/channel delivery, retries |
| Messaging | Thread, ThreadParticipant, Message, realtime delivery |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob, DataErasureTarget orchestration, retention exemptions |
| Observability / Ops | SystemEvent, IntegrationFailure, QueueJob, OpsIncident |
| Video / Calendar | provider resources and provider event truth |
| Payment / Payout / Tax | KycVerification and financial/KYC truth |

Specific prohibitions:

- Do not create `isVerifiedOrganization`, `canPublishJob`, `isPremiumOrg`, `canViewResume`, or local hold booleans as truth.
- Do not create local salary/EEOC/fair-chance scanners.
- Do not create direct Typesense clients.
- Do not create resume URL/signing helpers.
- Do not create Checkr/Certn clients here unless organization-verification ownership is explicitly ruled into this Module.
- Do not mutate `JobApplication`, `JobInterview`, `Notification`, `Thread`, `VerificationCheck`, `SearchUpsertEvent`, `ComplianceHold`, or Media-owned tables directly.

## 5. Module Architecture Principles

1. Organization and Job are business truth; providers and projections are rails.
2. Organization Hiring owns membership rows; Role / Authority interprets what roles may do.
3. Possession of `organizationId`, `jobId`, or `userId` never proves authority.
4. Organization cannot sell Offerings.
5. Job is formal hiring and is never a Gig or Offering.
6. Job Compliance decides posting compliance; Organization Hiring decides Job lifecycle.
7. Technical Job Compliance failure never means approved or legally rejected.
8. `Job.complianceStatus` cannot become a second compliance engine.
9. Job compensation is business truth; compensation disclosure is separate compliance proof.
10. Trust Verification owns verified-only truth.
11. Compliance approval does not bypass active holds or verification requirements.
12. Search is projection and may lag without changing source truth.
13. Media joins explain business context; Media owns file mechanics.
14. Organization Hiring UI may compose applicant/interview summaries but does not own those records.
15. Organization notification preferences do not transfer delivery ownership.
16. Privacy orchestration remains Privacy-owned.
17. Cross-Module reads use owner public facts interfaces, not neighboring repositories.
18. Cross-Module writes use commands/events, not direct Prisma mutation.
19. All retryable mutations are idempotent.
20. Concurrency protection uses database/platform primitives, not in-memory locks.
21. Unresolved `U-CL06-*` decisions block their affected production behavior.
22. Unresolved Organization verification/ATS access must not become convenience booleans.
23. Sensitive telemetry is minimized and redacted.
24. Architecture changes precede implementation when a binding decision changes.

## 6. Proposed Folder / Code Structure

```text
src/modules/organization-hiring/
  domain/
    organization-lifecycle.ts
    organization-membership-policy.ts
    job-lifecycle.ts
    job-publication-policy.ts
    job-materiality-policy.ts
    notification-preference-policy.ts
    errors.ts
    types.ts

  application/
    commands/
      create-organization.ts
      update-organization-profile.ts
      transition-organization-status.ts
      add-organization-member.ts
      change-organization-member-role.ts
      remove-organization-member.ts
      create-job-draft.ts
      update-job-draft.ts
      request-job-publication.ts
      apply-job-compliance-decision.ts
      pause-job.ts
      mark-job-filled.ts
      close-job.ts
      archive-job.ts
      attach-organization-media.ts
      attach-job-media.ts
      update-organization-notification-setting.ts
    queries/
      get-organization.ts
      list-organizations-for-actor.ts
      list-organization-members.ts
      get-job.ts
      list-organization-jobs.ts
      get-organization-hiring-context.ts
      get-job-application-eligibility-context.ts
      build-organization-source-projection.ts
      build-job-source-projection.ts
      get-organization-notification-settings.ts

  public/
    commands.ts
    queries.ts
    events.ts
    contracts.ts
    privacy.ts

  persistence/
    organization-repository.ts
    organization-member-repository.ts
    job-repository.ts
    organization-notification-setting-repository.ts
    contextual-media-repository.ts
    taxonomy-attachment-repository.ts   # only after U-CL06-08 rules placement
    mappers.ts

  contracts/
    identity.ts
    authority.ts
    taxonomy.ts
    job-compliance.ts
    trust-verification.ts
    media.ts
    search.ts
    notification.ts
    messaging.ts
    audit.ts
    holds.ts
    privacy.ts
    ops.ts

  events/
    event-builders.ts
    event-types.ts

  workers/
    close-expired-jobs.ts               # only after close-time policy is approved
    downstream-retry-handlers.ts        # owner-request retries, not provider clients

  privacy/
    enumerate-subject-data.ts
    execute-privacy-instruction.ts
    export-contribution.ts

  ui/
    organization/
    members/
    jobs/
    hiring-dashboard/

  tests/
    unit/
    integration/
    contract/
    rls/
    concurrency/
    privacy/
    e2e/
```

Do **not** add `providers/` in this Module unless a future binding ruling assigns a provider integration to Organization Hiring.

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| UI / delivery | Organization/member/Job forms, lists, state presentation, dashboard composition | permission decisions, compliance rules, Search/provider clients |
| Application services | command/query orchestration, owner transactions, downstream public-interface calls | neighboring source writes |
| Domain policy | Organization/member/Job invariants and lifecycle policy | generic auth, taxonomy, compliance, verification, hold policy |
| Persistence | Organization, OrganizationMember, Job, org notification preferences, approved contextual joins | neighboring Module repositories |
| Contracts | typed owner facts and dependency ports | provider payload types |
| Events | Organization/Job event vocabulary and minimized payloads | AuditEvent or SearchUpsertEvent truth |
| Workers | owner-specific Job close/retry orchestration | generic queue framework, Search indexer, provider webhook processor |
| Privacy | local enumerate/execute/export handlers | PrivacyRequest orchestration |
| Tests | Module behavior and boundary verification | testing neighboring internals through direct DB shortcuts |

## 8. Data Model

### 8.1 `Organization`

**Purpose:** source record for a hiring entity.

**Key relationships**

- optional `ownerUserId` to User;
- many `OrganizationMember`;
- many `Job`;
- taxonomy attachments;
- media attachments;
- notification settings;
- downstream JobInterview/ResumeAccess relations are references, not ownership.

**Authoritative fields**

- `id`, `slug`, `name`, `description`;
- business display/location fields;
- `status`;
- `ownerUserId` only under the final `U-CL06-03` ruling;
- timestamps.

**Lifecycle field:** `status`.

**Uniqueness:** `slug @unique`.

**Concurrency-sensitive fields**

- `status`;
- `ownerUserId`;
- profile updates whose source version is used by downstream projections;
- ownership transfer if later enabled.

**Retention/privacy**

Organization data may include personal information in name/contact-adjacent fields. Privacy instructions may require anonymization or retention analysis. `archived` is product lifecycle, not legal erasure.

**Schema warning**

The supplied schema contains an apparent out-of-model `jobApplicationViewEvents` relation defect adjacent to `Organization`. Resolve `U-CL06-17` before affected migrations.

### 8.2 `OrganizationMember`

**Purpose:** source membership fact and assigned org role.

**Authoritative fields**

- `organizationId`;
- `userId`;
- `role`;
- `createdAt`.

**Uniqueness:** composite primary key `(organizationId, userId)`.

**Lifecycle:** row presence and role value; no separate status.

**Concurrency-sensitive operations**

- add/remove;
- role changes;
- owner removal/transfer.

**Retention/privacy**

Membership rows link personal account identity to an organization. Privacy erasure must be coordinated with legal/security retention needs.

### 8.3 `OrganizationNotificationSetting`

**Purpose:** express organization-owned notification routing preferences.

**Authoritative fields**

- `organizationId`;
- `name`;
- `channel`;
- `enabled`;
- `notifyOwners`, `notifyAdmins`, `notifyRecruiters`.

**Uniqueness:** `(organizationId, name, channel)`.

**Important boundary:** these are preferences/routing facts, not Notification delivery truth.

### 8.4 `Job`

**Purpose:** source record for formal hiring opportunity.

**Authoritative business fields**

- Organization ownership;
- title/description;
- `status`;
- `visibility`;
- `employmentType`;
- taxonomy IDs;
- location/remote intent;
- compensation business fields;
- `publishedAt`, `closesAt`;
- `updatedAt` as current concurrency/version signal until an explicit version column exists.

**Relationships**

- belongs to Organization;
- references TaxonomyDomain/Category;
- owns contextual Job tags/media meaning;
- consumed by JobApplication;
- evaluated by Job Compliance.

**Uniqueness:** no natural unique constraint beyond `id`; business duplicate policy is not currently defined.

**Concurrency-sensitive fields**

- lifecycle status;
- publication;
- material content used by Job Compliance;
- visibility;
- close time.

**Retention/privacy**

Jobs may need retention for hiring/compliance/legal proof. Product archive is not erasure.

### 8.5 `OrganizationFeatureAccess`

This model exists with unique `(organizationId, featureKey)` and status/expiry fields, but ownership and relation to Track remain **unresolved** by `U-CL06-04`.

Until resolved:

- this Module may read it only through an architecture-approved owner interface if one exists;
- it must not create grant/revoke logic;
- basic non-monetized MVP behavior must not invent an entitlement gate;
- no local `isPremiumOrg` replacement is permitted.

### 8.6 `OrganizationMedia` / `JobMedia`

These joins explain business context only.

- `MediaAsset` readiness, scan, processing, storage, object keys, signed URLs, grants, and access events remain Media-owned.
- Organization Hiring may attach/detach only ready assets through `attachValidatedMedia`-style contracts.
- `Organization.logoUrl` must not become competing file truth; `U-CL06-09` governs whether it is removed, deprecated, or treated as a projection/cache.

### 8.7 Taxonomy joins

Taxonomy owns controlled vocabulary and semantics. Entity Modules own entity lifecycle and contextual meaning. Exact persistence command ownership for OrganizationCategory/Tag and JobTag remains `U-CL06-08`.

## 9. Enums, Statuses, and Lifecycles

### OrganizationStatus

Statuses: `draft`, `active`, `suspended`, `archived`.

**Transition owner:** Organization Hiring.

**Triggers**

- explicit organization management commands;
- administrative action through authorized public command;
- future verification/readiness decisions after `U-CL06-01/02`.

**Terminal:** `archived` by current architecture unless an explicit restoration rule is added.

**Prohibited shortcuts**

- external provider writes;
- frontend direct status mutation;
- local `isVerifiedOrganization` shortcut;
- using ComplianceHold as Organization status truth.

### Organization membership

Role vocabulary: `owner`, `admin`, `recruiter`.

**Transition owner:** Organization Hiring for row/role; Role / Authority for permission interpretation.

**Prohibited shortcuts**

- Role / Authority mutating membership rows;
- UI interpreting role strings independently;
- removing the canonical owner without satisfying `U-CL06-03`.

### JobStatus

Statuses: `draft`, `pending_compliance_review`, `flagged_for_review`, `open`, `paused`, `filled`, `closed`, `rejected`, `archived`.

**Transition owner:** Organization Hiring.

**External triggers**

- Job Compliance decision;
- Trust/Hold changes;
- close-time worker;
- authorized organization action.

**Terminal/reopen rules**

- `archived` is terminal unless explicitly changed.
- `closed`, `rejected`, and `filled` reopen semantics must be explicit and tested; do not assume.
- a materially edited approved/open Job must re-enter compliance review according to the final materiality policy.

**Event/history proof**

- publish a versioned domain event through the transactional outbox for material lifecycle facts.
- generic `AuditEvent` is separate.
- no dedicated JobEvent table is added without architecture approval.

## 10. Commands

The command names below are stable public architecture names unless implementation adopts an explicitly approved equivalent.

### `createOrganization`

- **Purpose:** create a draft hiring entity and initial membership facts.
- **Actor:** authenticated User.
- **Inputs:** validated Organization fields, idempotency key.
- **Preconditions:** actor exists; slug available; owner/membership rule from `U-CL06-03` respected.
- **Writes:** Organization and initial OrganizationMember facts in one transaction.
- **Shared operations:** `resolveAuthenticatedActor`, `authorizeResourceAction` where applicable, `executeIdempotentCommand`, `publishDomainEvent`, `appendAuditEvent`.
- **Idempotency:** required.
- **Failures:** validation error, slug conflict, owner invariant conflict, authorization denial.
- **Out of scope:** verified activation.

### `updateOrganizationProfile`

- **Purpose:** edit allowed Organization business/profile fields.
- **Actor:** authorized Organization member.
- **Preconditions:** Organization exists; authority allows action; optimistic version matches.
- **Writes:** Organization.
- **Effects:** event; Search refresh only if source is currently eligible for a public projection.
- **Failures:** authorization, stale version, invalid taxonomy/media references if included.

### `transitionOrganizationStatus`

- **Purpose:** apply an Organization lifecycle transition.
- **Actor:** authorized owner/admin or approved admin/system actor.
- **Preconditions:** valid transition, authority, applicable hold/verification gates.
- **Writes:** `Organization.status`.
- **Important:** verified activation remains blocked until `U-CL06-01/02`.
- **Effects:** event, Search refresh/remove, Notification/Audit where policy requires.

### `addOrganizationMember`

- **Purpose:** add a User membership row.
- **Inputs:** organizationId, target userId, role, idempotency key.
- **Writes:** OrganizationMember.
- **Preconditions:** actor authority; target User exists; no duplicate membership; owner invariants.
- **Effects:** domain event, audit, optional notification.
- **Failure:** duplicate composite key maps to domain conflict.

### `changeOrganizationMemberRole`

- **Purpose:** mutate assigned OrganizationRole.
- **Preconditions:** authority; membership exists; canonical owner invariant preserved.
- **Writes:** OrganizationMember.role.
- **Concurrency:** optimistic/aggregate lock on Organization membership aggregate.
- **Effects:** domain event, audit; downstream access invalidation is consumer-owned.

### `removeOrganizationMember`

- **Purpose:** remove membership row.
- **Preconditions:** authority; row exists; cannot violate canonical owner rule.
- **Writes:** delete OrganizationMember.
- **Effects:** event/audit; consumers react to revoke access.
- **Ownership transfer:** not exposed until `U-CL06-03`.

### `createJobDraft`

- **Purpose:** create private/non-public Job source truth.
- **Preconditions:** authorized organization actor; valid Organization state; taxonomy assignment valid.
- **Writes:** Job with `status=draft`.
- **Shared operations:** auth, authority, `validateTaxonomyAssignment`, idempotency.
- **Effects:** domain event only; no Search indexing.

### `updateJobDraft`

- **Purpose:** edit Job source fields.
- **Preconditions:** authority; allowed lifecycle; optimistic version.
- **Writes:** Job.
- **Material edit behavior:** if prior compliance approval is invalidated, transition to safe non-public/review state through local policy and request new compliance evaluation.
- **Effects:** event; Search remove/refresh as appropriate.
- **Failure:** stale edit, invalid taxonomy, invalid lifecycle.

### `requestJobPublication`

- **Purpose:** move Job into publication review and request authoritative Job Compliance evaluation.
- **Preconditions:** authorized org actor; Job exists; expected version; required source fields; holds/readiness prechecks where architecture says they apply.
- **Writes:** Job to `pending_compliance_review` and outbox/workflow receipt.
- **Calls:** `evaluateJobCompliance` through Job Compliance public interface.
- **Idempotency:** required.
- **Failure:** compliance unavailable leaves Job non-public.

### `applyJobComplianceDecision`

- **Purpose:** apply a version-bound Job Compliance decision to Job lifecycle.
- **Actor:** internal owner workflow/system, not arbitrary client.
- **Preconditions:** decision applies to exact Job/source version; `U-CL06-05/06/07` resolved.
- **Writes:** Job.status and approved summary mirror fields only.
- **Important:** Job Compliance never writes Job directly.
- **Effects:** domain event, Search refresh/remove, Notification, audit if required.

### `pauseJob`, `markJobFilled`, `closeJob`, `archiveJob`

- **Purpose:** owner-controlled lifecycle mutations.
- **Preconditions:** authority, valid transition, optimistic concurrency.
- **Writes:** Job.status and associated timestamps if architecture defines them.
- **Effects:** Search remove/refresh; events/notifications.
- **Prohibited:** mutating JobApplication outcomes.

### `attachOrganizationMedia`, `attachJobMedia`

- **Purpose:** create contextual attachment after Media says asset is ready and compatible.
- **Calls:** `attachValidatedMedia`.
- **Writes:** contextual join only.
- **Prohibited:** object storage, malware scanning, signed URL creation.

### `updateOrganizationNotificationSetting`

- **Purpose:** mutate org-owned delivery preference facts.
- **Writes:** OrganizationNotificationSetting.
- **Effects:** optional event/audit.
- **Prohibited:** sending email/SMS/push directly.

## 11. Queries / Decisions

### `getOrganization`

- **Consumers:** first-party UI, Job Compliance, Search projection builder, dependent owner contracts.
- **Returns:** source truth or privacy-shaped public view depending on caller.
- **Must not imply:** permission or verification readiness.

### `listOrganizationsForActor`

- **Consumers:** authenticated UI.
- **Returns:** Organizations related to the actor through membership/ownership facts.
- **Must not infer:** role permissions beyond returned role facts.

### `listOrganizationMembers`

- **Consumers:** Organization UI, Role / Authority owner-facts flow.
- **Returns:** membership facts.
- **Must not infer:** authorization; Role / Authority decides.

### `getOrganizationHiringContext`

Minimum owner-facts contract used by Role, Job Compliance, Candidate Application, Job Interview.

Suggested result:

```ts
type OrganizationHiringContext = {
  organizationId: string;
  organizationStatus: OrganizationStatus;
  organizationVersion: string;
  job?: {
    id: string;
    status: JobStatus;
    visibility: JobVisibility;
    organizationId: string;
    sourceVersion: string;
  };
  membership?: {
    userId: string;
    role: OrganizationRole;
  };
};
```

This is facts, not a permission decision.

### `getJob`

Returns authoritative Job facts and source version. Consumers must not infer compliance approval from `status` alone when a compliance evidence reference is required.

### `listOrganizationJobs`

Returns organization-scoped Job summaries after authorization.

### `getJobApplicationEligibilityContext`

Used by Candidate Application. Returns only Organization/Job source facts needed before an application is evaluated:

- organizationId/status;
- jobId/status/visibility;
- application-open facts;
- taxonomy/verification target identifiers;
- source version.

Candidate Application must still evaluate candidate state, Track, Trust, holds, and duplicate application itself.

### `buildOrganizationSourceProjection`

Returns allowlisted, versioned, public-safe Organization source fields for Search. It does not write Search.

### `buildJobSourceProjection`

Returns allowlisted, versioned Job source fields plus owner-owned visibility/lifecycle facts. Search must consume authoritative Job Compliance/public-readiness decisions rather than reconstruct them.

### `getOrganizationNotificationSettings`

Returns source preference facts; Notification owns delivery fan-out and channel mechanics.

## 12. Public Module Interface

### Public commands

- `createOrganization`
- `updateOrganizationProfile`
- `transitionOrganizationStatus`
- `addOrganizationMember`
- `changeOrganizationMemberRole`
- `removeOrganizationMember`
- `createJobDraft`
- `updateJobDraft`
- `requestJobPublication`
- `pauseJob`
- `markJobFilled`
- `closeJob`
- `archiveJob`
- `attachOrganizationMedia`
- `detachOrganizationMedia`
- `attachJobMedia`
- `detachJobMedia`
- `updateOrganizationNotificationSetting`

`transferOrganizationOwnership` is intentionally absent until `U-CL06-03`.

### Internal owner commands

- `applyJobComplianceDecision`
- `applyOrganizationVerificationDecision` only if future architecture assigns the consumption contract here
- `executePrivacyInstruction`
- close-time worker command

### Public queries

- `getOrganization`
- `listOrganizationsForActor`
- `listOrganizationMembers`
- `getOrganizationHiringContext`
- `getJob`
- `listOrganizationJobs`
- `getJobApplicationEligibilityContext`
- `buildOrganizationSourceProjection`
- `buildJobSourceProjection`
- `getOrganizationNotificationSettings`

### Emitted domain events

Event names are owner-defined and use platform outbox infrastructure:

- `organization.created`
- `organization.updated`
- `organization.status_changed`
- `organization.membership_added`
- `organization.membership_role_changed`
- `organization.membership_removed`
- `organization.notification_setting_changed`
- `job.created`
- `job.updated`
- `job.publication_requested`
- `job.status_changed`
- `job.published`
- `job.paused`
- `job.filled`
- `job.closed`
- `job.archived`

Do not emit an event merely to command another owner; use that owner's public command when imperative behavior is required.

### Privacy executor

- `enumerateSubjectData`
- `executePrivacyInstruction`
- `exportPrivacyContribution`

These are consumed by Privacy orchestration and return standardized execution results.

### Provider-facing interfaces

None currently owned.

## 13. Inbound Dependencies

| Owner | Public operation / interface | Why required | Minimum data | Can block? | Must not copy |
|---|---|---|---|---|---|
| Identity & Access | `resolveAuthenticatedActor` | trusted actor | actor IDs, role/security context | Yes | session/auth helpers |
| Role / Authority | `authorizeResourceAction` | permission decision | actor, action, owner-facts | Yes | org-role policy |
| Taxonomy | `validateTaxonomyAssignment`, `resolveTaxonomyRequirements` | accepted classifications and requirement triggers | IDs, active/hierarchy result | Yes for classification-sensitive commands | local taxonomy copies |
| Job Compliance | `evaluateJobCompliance` / decision query | publication decision | Job snapshot/version, rule/evidence refs | Yes | salary/EEOC/fair-chance logic |
| Trust Verification | `resolveVerificationRequirements`, `evaluateVerificationReadiness` | verified-only gates | target IDs, requirement/readiness decision | Yes | VerificationCheck interpretation |
| Holds | `evaluateComplianceHold` | reusable stop sign | target/action, hold refs/reasons | Yes | local block flags |
| Media | file validation/processing, `attachValidatedMedia` | safe organization/job images | media ID, readiness/context | Yes for attachment | storage/scanning/signing |
| Search | `requestSearchProjectionRefresh` | public projection handoff | entity, action, source version | No source rollback; async failure | Typesense clients/indexers |
| Notification | `requestNotification` | deliver alerts | recipients/template/safe variables | No source rollback | delivery code |
| Messaging | `ensureContextThread` where needed | hiring collaboration context | context and participants | No source ownership | Thread mutation |
| Audit | `appendAuditEvent` | generic audit proof | actor/action/target/outcome | root policy-dependent | AuditEvent table/writer |
| Privacy | privacy target envelope/protocol | execute legal instructions | target/action/retention refs | Yes for destructive action | Privacy workflow |
| Ops | logging/failure APIs | operational visibility | correlation, safe error data | No business truth | incident system |
| Track | unresolved Organization feature interface | ATS commercial access if monetized | feature decision | Yes only after U-CL06-04 | local premium state |

## 14. Outbound Consumers and Effects

| Consumer | What it consumes | Contract |
|---|---|---|
| Role / Authority | OrganizationMember and resource relationship facts | `getOrganizationHiringContext` / owner-facts DTO |
| Job Compliance | versioned Job source snapshot | Job query/projection contract |
| Candidate Application | Job/Organization eligibility facts | `getJobApplicationEligibilityContext` |
| Job Interview | Organization/Job ownership context | `getOrganizationHiringContext` |
| Search | public-safe source projection and source events | projection builders + refresh request |
| Notification | recipient facts and business trigger intent | recipient query + `requestNotification` |
| Messaging | context IDs/participants when hiring thread needed | `ensureContextThread` request |
| Privacy | subject-data inventory/executor | privacy handler contract |
| Audit/Ops | event/failure references | shared operations |

Organization Hiring never directly mutates consumer tables.

## 15. Canonical Shared Operations Used

The supplied Canonical Shared Operations Architecture uses canonical operation names as identifiers and does not provide SH-### IDs. These names are the canonical identifiers for this document.

| Canonical operation | Classification | Owner | Why Organization Hiring uses it | Invocation point | Local policy retained | Expected result | Prohibited duplicates |
|---|---|---|---|---|---|---|---|
| `resolveAuthenticatedActor` | platform capability | Identity & Access | trusted actor context | every protected entry | action meaning | typed actor | `current-user.ts`, local session helper |
| `authorizeResourceAction` | cross-cutting capability | Role / Authority | permission decision | before protected command/read | Organization/Job action vocabulary and facts | allow/deny + reasons | `org-permissions.ts`, `canEditJob` |
| `queryOwnerFacts` | shared contract/separate implementations | each source owner | expose minimum ownership facts | cross-module auth/gates | DTO fields | facts only | generic cross-domain repo |
| `evaluateComplianceHold` | cross-cutting capability | Holds | block affected transitions | before public/sensitive transition | effect on local lifecycle | hold decision | `isBlocked`, local hold table |
| `resolveVerificationRequirements` | Module public interface | Trust | know which Job requirements apply | publication/application facts | local action effect | requirement list | job verification helper |
| `evaluateVerificationReadiness` | Module public interface | Trust | know whether required checks pass | publication readiness composition | local lifecycle effect | DecisionResult | badge/provider inference |
| `evaluateJobCompliance` | Module public interface | Job Compliance | posting compliance | publication/re-review | Job lifecycle mapping | pass/warn/block/review + evidence | local scanner |
| `returnDecisionResult` | shared contract/separate policy | varies | stable decision envelope | gates | local reason vocabulary | allow/deny/warning/review/remediation | generic readiness engine |
| `validateTaxonomyAssignment` | Module public interface | Taxonomy | validate IDs/hierarchy | create/update classification | classification mandatory rules | normalized result | tag cleaner/local taxonomy |
| `resolveTaxonomyRequirements` | Module public interface | Taxonomy | discover Trust/compliance triggers | publication | how local action uses trigger | requirement descriptors | hardcoded category rules |
| `executeIdempotentCommand` | platform primitive | platform | prevent duplicate side effects | create/publish/membership commands | semantic command identity | original replay result | ad-hoc idempotency |
| `withOptimisticConcurrency` | platform primitive | shared persistence | reject stale mutations | Organization/Job/member edits | conflict semantics | success/conflict | update timestamp helper variants |
| `acquireAggregateLock` | platform primitive | shared persistence | protect owner/membership aggregate when necessary | owner-sensitive membership mutation | lock key | lock result | in-memory mutex |
| `transitionLifecycleState` | shared mechanism/separate truth | shared mechanics | transition plumbing | Organization/Job status changes | transition matrices | transition result | generic policy table |
| `publishDomainEvent` | platform primitive | event/outbox infra | reliable events | same transaction as source write | event vocabulary/payload | outbox receipt | fire-and-forget bus |
| `deduplicateDomainEvent` | platform primitive | event infra/consumer | safe event handling | inbound owner events | consumer side effect | processed/duplicate | local processed-event hack |
| `enqueueReliableJob` | platform primitive | queue infra | durable Job close/retry work | async owner work | payload/completion | job receipt | local queue |
| `executeRetryWithBackoff` | platform primitive | queue infra | retry technical failures | Search/Notification handoff retries | retryable classification | retry result | custom retry loops |
| `runDeadlineExpiration` | shared scheduler | platform | close Jobs after `closesAt` | scheduled worker | close policy | expiration result | local cron framework |
| `appendAuditEvent` | cross-cutting capability | Audit | generic audit proof | sensitive/admin mutations | auditable action set | audit ref | local audit table |
| `requestNotification` | platform notification capability | Notification | alert humans | after committed source event | business meaning/safe variables | request receipt | email/SMS/push code |
| `resolveNotificationRecipients` | shared contract/separate policy | source owner + Notification | derive owner/admin/recruiter recipients | before delivery request | org preference meaning | user IDs / routing facts | delivery fan-out locally |
| `attachValidatedMedia` | shared contract/separate contextual truth | context owner + Media | attach ready assets | after Media readiness | role/context | attachment result | storage mutation |
| `requestSearchProjectionRefresh` | Module public interface | Search | request index/update/hide/remove | after committed source/readiness change | source lifecycle/visibility | refresh receipt | direct Typesense |
| `buildSourceProjection` | shared mechanism/separate truth | source owner | build allowlisted projection | before Search refresh | fields and version | source DTO | Search reconstructing truth |
| `enumerateSubjectData` | privacy protocol | data owner | inventory subject data | Privacy orchestration | local data mapping | target list | local PrivacyRequest |
| `executePrivacyInstruction` | privacy protocol | data owner | erase/anonymize/retain local data | Privacy worker | local execution semantics | standardized result | direct privacy orchestration |
| `evaluateRetentionRequirement` | privacy/shared policy interface | Privacy + legal/data owner | determine retention | destructive privacy work | record meaning | retain/erase decision | arbitrary deletion |
| `ensureContextThread` | Messaging public interface | Messaging | create/resolve hiring thread if needed | downstream workflow | context facts | thread ref | local chat tables |

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
|---|---|---|---|---|---|
| `validateOrganizationTransition` | enforce OrganizationStatus matrix | current, target, context | local decision | Organization | domain policy |
| `validateMembershipMutation` | preserve membership/owner invariants | actor facts, membership set, mutation | local decision | OrganizationMember | domain policy |
| `validateJobTransition` | enforce JobStatus matrix | current, target, trigger | local decision | Job | domain policy |
| `classifyJobEditMateriality` | determine if edit invalidates compliance/publication | before/after Job source | material/nonmaterial + reasons | Job workflow | Job source semantics |
| `mapComplianceDecisionToJobTransition` | convert authoritative Job Compliance result to local Job lifecycle effect | decision + exact source version | transition/remediation | Job | shared decision shape, local policy |
| `resolveOrganizationNotificationRecipientsLocalFacts` | derive owner/admin/recruiter membership groups | org, setting | user IDs | none | Organization owns preference meaning |
| `buildOrganizationProjection` | construct public-safe source fields | Organization source | projection DTO | none | source-owned field allowlist |
| `buildJobProjection` | construct public-safe Job source fields | Job source + owner decisions refs | projection DTO | none | source-owned field allowlist |
| `closeJobAtDeadline` | apply local close policy | Job, now | close/no-op | Job | lifecycle owner |

## 17. Shared Mechanism / Separate Truth Rules

1. **Lifecycle helper:** state-machine plumbing may be shared; OrganizationStatus and JobStatus policy remain local.
2. **DecisionResult:** response shape may be shared; Job Compliance, Trust, Holds, and Organization lifecycle decisions remain separate.
3. **Outbox:** event mechanics are shared; Organization/Job event names and meanings remain local.
4. **Audit:** append mechanics are shared; AuditEvent does not replace Organization/Job source truth.
5. **Search projection:** projection runner can be shared; source field selection remains Organization Hiring-owned and index execution Search-owned.
6. **Media attachment:** attach mechanics can be shared; OrganizationMedia/JobMedia business meaning stays contextual and MediaAsset truth stays Media-owned.
7. **Privacy executor:** protocol is shared; Organization Hiring alone knows how to mutate its own records.
8. **Concurrency:** lock/version mechanisms are shared; aggregate lock keys and conflict rules remain local.
9. **Notification:** delivery system is shared; hiring event meaning and org recipient-group facts remain local.
10. **Verification readiness:** response contract is shared; Trust Verification owns evidence and policy.

## 18. Authentication and Authorization

### Actor requirement

Every protected operation starts with `resolveAuthenticatedActor`.

### Permission interpretation

Organization Hiring supplies relationship facts; Role / Authority evaluates:

- organization profile management;
- member add/change/remove;
- Job create/edit/publish/pause/close/fill/archive;
- organization notification settings;
- applicant/dashboard contextual access facts.

### Resource facts supplied by this Module

- Organization ownership/status;
- OrganizationMember row and assigned role;
- Job → Organization relation;
- Job status/visibility;
- source version.

### Admin/support

Admin/support status alone does not grant blanket data access. Admin actions must go through Role / Authority and audit policy. Sensitive applicant/resume access remains Candidate/Audit-owned.

### Step-up

No Organization Hiring-specific step-up action is confirmed. Use root `requireStepUpForSensitiveAction` only if root policy later designates ownership transfer, organization verification, or similarly high-risk actions.

## 19. Compliance / Readiness / Entitlement Gates

### Organization activation

- **Underlying truth owner:** unresolved (`U-CL06-01/02`).
- **Action gated:** `draft/suspended → active`.
- **Local policy:** Organization Hiring alone changes status after consuming approved external decision(s).
- **Current rule:** do not implement verified activation or `isVerifiedOrganization`.

### Job publication compliance

- **Truth owner:** Job Compliance.
- **Consumed operation:** `evaluateJobCompliance`.
- **Action gated:** `pending_compliance_review → open` or other final mapping.
- **Local policy:** exact version match; external decision mapped to Job status.
- **Blocked by:** `U-CL06-05/06/07` before production publication.

### Verified-only Job requirement

- **Truth owner:** Trust Verification.
- **Consumed operations:** `resolveVerificationRequirements`, `evaluateVerificationReadiness`.
- **Action gated:** publication and/or application availability according to final requirement policy.
- **Local policy:** Organization Hiring composes returned result; never reads badges/provider states as truth.

### ComplianceHold

- **Truth owner:** Admin Review / Compliance Hold.
- **Consumed:** `evaluateComplianceHold`.
- **Actions:** activation/publication/sensitive transitions where applicable.
- **Local result:** deny/hold transition; never create local blocked flag.

### Organization ATS feature access

- **Truth owner:** unresolved `U-CL06-04`.
- **Current rule:** do not gate basic MVP applicant tracker/resume viewer/candidate search using invented local access truth.
- **If monetized:** implementation is blocked until ownership and relation to Track are approved.

## 20. Provider Integrations

Organization Hiring owns no confirmed external provider adapter.

### Explicit prohibitions

- no Checkr/Certn client;
- no verification webhook;
- no Typesense client;
- no object storage client;
- no email/SMS/push provider;
- no calendar/video provider;
- no provider-event dedupe ledger.

Organization verification notes mention business identity, authorized representative, and Checkr/KYC concepts, but `U-CL06-01/02` explicitly leaves owner/schema/provider-neutral contract unresolved.

## 21. Events and Outbox

### Event rules

- emitted only after source-of-truth transaction commits;
- stored through platform transactional outbox;
- contain aggregate ID, event type, schema version, aggregate/source version, occurredAt, correlation/causation IDs;
- include only minimum safe fields;
- do not contain resume content, applicant sensitive data, provider payloads, or unnecessary personal data;
- consumer idempotency uses `deduplicateDomainEvent`.

### Event families

```text
organization.created
organization.updated
organization.status_changed
organization.membership_added
organization.membership_role_changed
organization.membership_removed
organization.notification_setting_changed

job.created
job.updated
job.publication_requested
job.status_changed
job.published
job.paused
job.filled
job.closed
job.archived
```

Events describe facts. Search refresh, notification delivery, compliance evaluation, and thread creation are imperative owner calls and should not be disguised as domain facts when a command is required.

## 22. Background Jobs / Scheduled Work

### `closeExpiredJobs`

**Purpose:** close Jobs whose approved `closesAt` policy says applications should end.

**Owner:** Organization Hiring.

**Input:** Job ID/source version or query batch.

**Idempotency key:** `job-close:{jobId}:{sourceVersion-or-deadline}`.

**Retryable failures:** transient DB/queue failures, downstream Search/Notification request failures.

**Permanent failures:** Job no longer in closable status; stale source version; invalid deadline data.

**Business truth updated:** Job.status only.

**Telemetry:** safe Job ID, status, correlation ID, retry count; no applicant/resume payload.

**Activation rule:** do not implement until close-time lifecycle semantics are specified.

### Downstream request retries

Search/Notification/Messaging failures may be retried through reliable jobs after source commit. Retry jobs do not own downstream truth and do not rewrite a truthful Job status merely because a rail is unavailable.

## 23. Concurrency and Idempotency

### Races to prevent

- duplicate Organization creation under same idempotency key;
- slug collision;
- duplicate membership add;
- simultaneous owner-sensitive membership mutations;
- stale Organization status transitions;
- simultaneous Job edits;
- publish/edit race;
- duplicate publication requests;
- duplicate application of the same compliance decision;
- Job close worker racing manual pause/close/fill;
- Search retry racing later source version.

### Database protections

- Organization.slug unique;
- OrganizationMember composite PK `(organizationId,userId)`;
- OrganizationNotificationSetting unique `(organizationId,name,channel)`;
- use compare-and-set on `updatedAt` or future explicit aggregate version;
- use aggregate/advisory lock only when a multi-row membership/owner invariant cannot be expressed safely otherwise.

### Transaction boundaries

- Organization create + initial membership facts + outbox;
- membership mutation + owner invariant + outbox/audit request record where transactionally supported;
- Job source mutation + lifecycle state + outbox;
- publication state change + source-version binding + outbox/workflow receipt.

### Idempotency semantics

- same key + same fingerprint returns original result;
- same key + different fingerprint is conflict;
- provider/downstream retry keys are distinct from business command keys;
- replay never repeats side effects.

### No in-memory locking

Distributed invariants must be database/platform-enforced.

## 24. Media / Storage

### Business attachment meaning owned here

- Organization logo/presentation image context.
- Job graphic/presentation image context.

### Media-owned mechanics

- upload session;
- size/type policy;
- MIME/binary validation;
- malware scan;
- EXIF/GPS scrubbing;
- derivatives;
- storage bucket/object keys;
- signed URLs;
- MediaAccessGrant/Event.

### Upload contexts

- `organization_logo`;
- `organization_job_graphic`.

Current registry evidence states organization images are capped at 2MB, image-only, and public display must use processed/scrubbed derivatives.

### Access

Public Organization/Job images should use processed public derivatives after Media readiness. Organization Hiring does not issue signed URLs.

### Direct URL warning

`Organization.logoUrl` may not be used as independent file truth. Resolve `U-CL06-09`.

## 25. Search / Projection

### Source truth

Organization and Job records in this Module.

### Source projections

Organization Hiring builds allowlisted source projection DTOs containing:

- source ID;
- source version;
- public lifecycle/visibility fields;
- approved display/location/classification fields;
- safe media derivative references if approved.

### Search-owned truth

- `SearchUpsertEvent`;
- Typesense collection documents;
- indexing/de-indexing workers;
- backfill/reconciliation;
- public/protected search queries.

### Index triggers

- Organization public-source change;
- Organization status change;
- Job publication/status/visibility change;
- material Job edit;
- taxonomy/media change affecting projection;
- hold/verification/compliance change that changes public readiness.

### Conditions

Search must not reconstruct Job Compliance, Trust, Hold, or privacy policy from raw fields. Organization Hiring supplies source state; owner-issued decision evidence must be consumed according to Search architecture.

## 26. Notification

### Business triggers owned here

- member added/role changed/removed;
- Job publication requested;
- Job becomes open/paused/filled/closed/rejected;
- Organization status changed;
- Job needs correction/review if user-facing notification is approved.

### Safe payload intent

Use IDs, short display labels, template keys, action routes and safe reason codes. Do not send applicant/resume content.

### Ownership split

Organization Hiring owns event meaning and OrganizationNotificationSetting facts.
Notification owns recipient channel preference, persistence, provider delivery, retries, and delivery status.

## 27. Audit and Sensitive Access

### Domain history

Organization/Job domain events are integration/lifecycle facts.

### Generic audit

Use `appendAuditEvent` for policy-designated administrative/sensitive actions such as:

- membership role changes/removal;
- Organization suspension/archive;
- Job administrative override actions if architecture permits;
- future ownership transfer.

### Sensitive access

Resume access is not Organization Hiring proof. Candidate Application owns ResumeAccessLog; Audit owns AccessAuditLog; Media owns MediaAccessEvent.

Do not collapse these records.

## 28. Privacy and Retention

### Subject-data inventory

Potential personal or organization-linked data:

- Organization ownerUserId;
- OrganizationMember user IDs and roles;
- Organization profile fields that may identify individuals;
- Job content that may contain contact details;
- audit/event references;
- notification-setting metadata.

### Privacy executor

Organization Hiring implements owner-local handlers for:

- enumerate subject references;
- anonymize or detach membership where legally/product-safe;
- erase organization-owned personal display data when allowed;
- retain or refuse destructive action when Privacy supplies a valid retention exemption;
- contribute export-safe Organization/member/Job data.

### Retention

- archive is not erasure;
- hiring/compliance records may require legal retention analysis;
- Job Compliance evidence is owned externally and handled by its owner;
- generic Audit proof remains Audit-owned.

## 29. Observability

### Structured logs

Include:

- request/correlation ID;
- command/query name;
- Organization/Job ID;
- actor category/ID where safe;
- source version;
- result category;
- latency;
- dependency owner and normalized error class.

### Metrics

Examples:

- organization create/update success/failure;
- membership mutation conflict/denial;
- Job draft create/update;
- publication request counts;
- compliance decision result counts by safe reason category;
- stale decision conflicts;
- Search refresh lag/failures;
- close worker success/failure.

### Operational records

Use shared IntegrationFailure/SystemEvent/QueueJob/OpsIncident mechanisms through Ops. They never replace Organization or Job status.

### Redaction

Do not log resume text, applicant content, raw provider payloads, tokens, secrets, or unnecessary PII.

## 30. Security Boundaries

- Runtime validation on all public inputs.
- Server-side actor resolution and authorization.
- RLS parity with Role / Authority.
- No client-written status fields.
- No direct provider secrets in Module code.
- No raw file processing here.
- No direct Search credentials/client.
- Payload minimization across events/logs.
- Rate limiting follows platform policy for create/update/publication endpoints.
- Idempotency keys are opaque and not treated as authorization.
- Sensitive identifiers in logs must follow root redaction policy.

## 31. Error / Decision Result Pattern

Public interfaces use stable categories:

```text
validation_error
unauthenticated
unauthorized
not_found
conflict
stale_version
invalid_transition
dependency_unavailable
decision_denied
decision_review_required
decision_remediation_required
temporarily_unavailable
internal_error
```

Decision results use the canonical shared shape:

```ts
type DecisionResult = {
  decision: "allow" | "deny" | "warning" | "review" | "remediation";
  reasonCodes: string[];
  evidenceRefs?: string[];
  warnings?: string[];
  evaluatedAt: string;
  policyVersion?: string;
  sourceVersion?: string;
  expiresAt?: string;
  nextAction?: string;
};
```

Provider errors are translated by provider-owning Modules and must not leak into Organization Hiring public contracts.

## 32. Testing Architecture

### Domain unit tests

- Organization transition matrix.
- membership mutation invariants.
- Job transition matrix.
- material-edit classification.
- compliance-decision-to-Job mapping once ruled.
- notification recipient local-facts policy.
- projection allowlists.

### Public contract tests

- owner-facts DTO stability.
- JobApplication eligibility context.
- Job Compliance port.
- Trust readiness port.
- Search refresh contract.
- Media attachment contract.
- Privacy executor contract.

### Database/integration tests

- slug uniqueness;
- membership composite PK;
- notification setting uniqueness;
- transaction rollback;
- source+outbox atomicity;
- Job update/version conflicts.

### Authorization/RLS tests

- owner/admin/recruiter allowed/denied matrix via Role / Authority;
- cross-organization denial;
- RLS parity;
- no direct client status mutation.

### Compliance tests

- no public Job before authoritative Job Compliance decision;
- technical compliance failure cannot approve;
- stale decision cannot publish;
- holds/verification cannot be bypassed.

### Idempotency/concurrency tests

- duplicate create;
- duplicate membership add;
- publish replay;
- publish/edit race;
- close-worker/manual-action race.

### Privacy tests

- inventory completeness;
- erase/anonymize behavior;
- retention exemption handling;
- exported payload minimization.

### E2E participation tests

- create Organization → manage membership → create/edit draft Job;
- request publication with Job Compliance fixture → open Job → Search refresh fixture;
- Search outage leaves Job source truthful;
- dashboard reads applicant/interview summaries through public interfaces, not direct repositories.

## 33. Module Invariants

**Rules coding agents must never violate**

1. `Organization` is a hiring entity and does not sell Offerings.
2. `Job` is formal hiring; it is not Gig or Offering.
3. Organization Hiring owns `Organization`, OrganizationMember row/role assignment, and Job lifecycle.
4. Role / Authority owns permission interpretation.
5. One `(organizationId,userId)` membership row exists at most once.
6. Owner-sensitive membership mutation must preserve the canonical owner invariant once `U-CL06-03` is resolved.
7. No ownership transfer command is implemented before `U-CL06-03`.
8. Organization verified activation is not implemented before `U-CL06-01/02`.
9. `OrganizationFeatureAccess` ownership is not assumed before `U-CL06-04`.
10. Basic MVP must not invent local ATS premium/entitlement booleans.
11. Job Compliance owns posting compliance findings/decision/proof.
12. Job Compliance never directly writes Job lifecycle.
13. Organization Hiring never implements salary/EEOC/fair-chance scanners.
14. A technical compliance failure never means approved or legally rejected.
15. Public Job publication must bind to the exact evaluated source version.
16. Production publication is blocked until `U-CL06-05/06/07` are resolved.
17. `Job.complianceStatus` is a summary mirror only if retained.
18. Job compensation fields are business truth; JobCompensationDisclosure is separate compliance proof.
19. Trust Verification owns verification requirements/checks/readiness.
20. TrustBadge is never used as verification truth.
21. ComplianceHold is the reusable stop sign; no local blocked table/boolean.
22. Search is derived projection; Organization Hiring never writes Typesense or SearchUpsertEvent.
23. Search failure never rolls back truthful Organization/Job source state.
24. Candidate Application owns JobApplication and resume privacy.
25. Organization Hiring never writes JobApplication status/stage.
26. Job Interview owns interview lifecycle.
27. Organization Hiring dashboard composition does not transfer applicant/interview ownership.
28. MediaAsset mechanics remain Media-owned.
29. Organization/Job media attachments require ready, valid Media assets.
30. `Organization.logoUrl` cannot be independent file truth.
31. Taxonomy owns controlled vocabulary and semantics.
32. Notification owns delivery; Organization Hiring owns only business trigger meaning/preferences.
33. Messaging owns Thread/Message.
34. AuditEvent and AccessAuditLog remain Audit-owned.
35. Privacy owns privacy-request orchestration.
36. Events are emitted from transactional outbox, not fire-and-forget after writes.
37. Retryable business commands use canonical idempotency.
38. Distributed concurrency uses DB/platform primitives, not in-memory locks.
39. Cross-Module reads use public owner-facts contracts.
40. Cross-Module writes use approved commands/events.
41. Provider clients are prohibited here unless a future binding ruling assigns ownership.
42. Sensitive telemetry is minimized/redacted.
43. The Prisma relation defect in `U-CL06-17` must be fixed before affected migrations.
44. Architecture must be updated before code relies on a changed binding decision.

## 34. Prohibited Duplicate Implementations

Do not create inside `organization-hiring`:

- `auth.ts`, `current-user.ts`, `require-user.ts`;
- `org-permissions.ts`, `recruiter-guard.ts`, `canPublishJob.ts`, `canViewResume.ts`;
- `isPremiumOrg`, `org-plan.ts`, local quota/boost/feature flags;
- `job-compliance-validator.ts`, salary/EEOC/fair-chance scanner;
- `verification-helper.ts` that interprets VerificationCheck/TrustBadge;
- local ComplianceHold/block table or boolean;
- `typesense.ts`, direct Search indexer, de-indexer, SearchUpsertEvent writer;
- `resume-storage-service.ts`, presigned URL signer, MIME validator, malware scanner, EXIF scrubber;
- email/SMS/push provider client or retry loop;
- Thread/Message repositories;
- JobApplication mutation service;
- JobInterview mutation service;
- local generic AuditEvent or AccessAuditLog table/writer;
- PrivacyRequest/DataErasureJob workflow;
- Checkr/Certn webhook/client;
- calendar/video provider logic;
- custom queue/retry/dead-letter framework;
- in-memory distributed lock;
- universal readiness engine;
- universal cross-domain repository.

## 35. Unresolved Decisions

### U-CL06-01 — Organization verification owner

Which Module owns business identity and authorized-representative verification? Missing approved model, owner, and provider-neutral contract. Blocks verified Organization activation/restricted hiring.

### U-CL06-02 — Permissible-purpose / FCRA organization certification

Which versioned record proves employment permissible purpose/FCRA certification? `ConsentLog` alone does not establish the organization-specific authorization lifecycle. Blocks production workflows dependent on that proof.

### U-CL06-03 — Canonical Organization owner representation

`Organization.ownerUserId` and owner membership both exist. Define one canonical truth and transfer/removal invariant. Blocks ownership transfer.

### U-CL06-04 — Organization ATS commercial entitlement

Who owns `OrganizationFeatureAccess`, and how does it relate to Track? Blocks monetized applicant tracker/resume viewer/candidate-search gates. Basic non-monetized MVP must not invent the gate.

### U-CL06-05 — Job Compliance effective decision

Define source truth and precedence across latest check, disclosure, Job summary, and ComplianceHold; define warning/failed mapping. Blocks production publication.

### U-CL06-06 — Historical rule-set proof

Define how zero-finding approval records exactly which rules were evaluated after later rule changes. Blocks legal-grade reproducibility.

### U-CL06-07 — `CompensationPeriod` ownership and `EmploymentType.contract`

Resolve structural owner of compensation-period vocabulary and whether `contract` means fixed-term employee or independent contractor. Blocks final employment/compliance semantics.

### U-CL06-08 — Classification join persistence

Taxonomy owns vocabulary/semantics; entity Modules own contextual meaning. Exact attach/detach persistence owner is inconsistent. Blocks code placement, not conceptual ownership.

### U-CL06-09 — Overlapping direct/projection fields

Resolve `Organization.logoUrl` as remove/deprecate/projection. Blocks production use as file truth.

### U-CL06-17 — Prisma structural defect

Verify/fix out-of-model `jobApplicationViewEvents` relation lines before migrations touching affected models.

### Additional Module decision

Decide whether dedicated `OrganizationEvent` or `JobEvent` lifecycle ledgers are required. Current architecture does not require inventing them; platform outbox plus generic audit remains sufficient unless historical/replay requirements demand otherwise.

## 36. Architecture Decision Summary

Binding for this Module:

- Organization Hiring owns `Organization`, OrganizationMember row/role assignment, and `Job` lifecycle.
- Role / Authority owns permission interpretation.
- Organization Hiring owns Organization notification preference meaning.
- Job Compliance owns posting rules/checks/findings/disclosure decision/proof.
- Trust Verification owns verified-only truth.
- Candidate Application owns CandidateProfile, JobApplication, resume privacy/proof, and candidate projection.
- Job Interview owns interview lifecycle.
- Media owns file safety/storage/grants; Organization Hiring owns organization/job attachment meaning.
- Search owns projection execution; Organization Hiring owns source truth and source projection builders.
- Track owns commercial policy; Organization ATS commercial access remains unresolved.
- Holds, Audit, Privacy, Notification, Messaging, and Ops retain their canonical ownership.
- No provider integration is currently owned by this Module.
- Production Organization verification and production Job publication remain blocked by the relevant `U-CL06-*` decisions.
- Unresolved decisions must never be implemented as convenience booleans or permissive defaults.

## 37. Coding-Agent Usage

Before implementing this Module, an agent must read:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry/Architecture;
5. CL-06 `architecture.md`;
6. CL-06 `build-plan.md`;
7. this `module-architecture.md`;
8. this `implementation-plan.md`;
9. relevant direct-dependency public-interface sections:
   - Identity & Access;
   - Role / Authority;
   - Taxonomy & Classification;
   - Job Compliance;
   - Trust Verification;
   - Media / File Access;
   - Search / Public Visibility;
   - Notification;
   - Messaging;
   - Audit / Event Ledger;
   - Admin Review / Compliance Hold;
   - Privacy / Data Erasure;
10. current Prisma schema and migrations;
11. progress tracker;
12. approved decisions resolving every `U-CL06-*` touched by the feature.

Confirm the prior feature exit gate before starting the next feature. Never resolve an Unresolved Decision implicitly in code.
