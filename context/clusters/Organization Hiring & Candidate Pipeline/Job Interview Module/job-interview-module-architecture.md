# Job Interview Module Architecture

> **Module ID:** `job_interview`  
> **Module name:** Job Interview Module  
> **Primary Cluster:** CL-06 — Organization Hiring & Candidate Pipeline  
> **Document status:** implementation-grade Module architecture with explicit Proposed Rulings and unresolved blockers  
> **Authority:** subordinate to root Workin Ants architecture and CL-06 architecture; superior to implementation convenience

## 1. Module Header

| Field | Value |
|---|---|
| Module ID | `job_interview` |
| Module name | Job Interview Module |
| Module type | `domain_capability_hybrid` |
| Build status | `mvp_active` |
| Primary Cluster | CL-06 — Organization Hiring & Candidate Pipeline |
| Document status | Implementation-grade context; binding where marked **Binding**; **Proposed Rulings** require explicit acceptance; **Unresolved Decisions** block affected behavior |
| Intended audience | Coding agents, developers, reviewers, maintainers, test authors, and architecture reviewers |
| Relationship to root architecture | Inherits root source-of-truth, security, event, provider, privacy, and shared-operation rules. This document may narrow those rules for Job Interview but may not contradict them. |
| Relationship to Cluster architecture | Implements only the `job_interview` portion of CL-06. The Cluster coordinates sequence and bridges; it does not own Job Interview truth. |
| Relationship to Cluster build plan | The Module implementation plan maps primarily to CL-06 Features 09–15. Module work must not jump ahead of Cluster exit gates. |
| Update rule | Update this architecture before code when a binding ownership, lifecycle, schema, public-interface, provider, privacy, retention, or shared-operation decision changes. Build progress must never silently redefine architecture. |

### Evidence basis

This document is grounded in the current supplied Workin Ants sources:

- `project-overview-v3(20260906-163916).md`;
- `deep modules and schemas(20260906-163900).json`;
- `clusters(20260906-163901).json`;
- `schema(20260906-163901).prisma`;
- `workin_ants_ubiquitous_language_pack_v2_2_full_compliance_schema_module (1)(20260906-163913).docx`;
- `Workin_Ants_Canonical_Shared_Operations_Architecture(20260906-163913).docx`;
- `organization-hiring-candidate-piepline-architecture(3).md`;
- `organization-hiring-candidate-pipeline-build-plan(3).md`;
- the standardized Job Interview Module Architecture Extract produced in this thread.

Root `architecture.md`, root `code-standards.md`, progress tracker, and dependency Module context files were not supplied as standalone files in this turn. Where this document refers to them, coding agents must use the repository versions if present and must not invent missing root rules.

### Evidence conflicts that materially affect this Module

1. The Deep Module Registry confirms `JobInterview` and `JobInterviewEvent` ownership but does **not** assign `JobInterviewParticipant`; the glossary marks participant ownership as unassigned; CL-06 proposes Job Interview ownership. Participant implementation is therefore not yet binding.
2. `JobInterview` stores `externalCalendarProvider` and `externalSyncStatus` using calendar vocabulary owned by Booking & Calendar, while Job Interview explicitly does not own the calendar availability/provider engine. CL-06 U-CL06-16 leaves the broader hiring calendar port unresolved.
3. The Prisma schema stores `externalMeetingUrl`, while Video Infrastructure owns interview-room mechanics and forbids reusable public room links. The permitted meaning and security treatment of `externalMeetingUrl` require an explicit rule before it is used as a credential-bearing meeting link.
4. `JobInterview`/participant/event relations cascade on parent deletion, while `JobInterviewEvent` is supporting append-only evidence. Retention/erasure behavior must be resolved before destructive production paths.
5. CL-06 identifies a Prisma structural defect around `JobApplicationViewEvent`. Although not Job Interview-owned, it may block whole-schema validation/migration generation and must be resolved before affected migrations.

## 2. Purpose, Goal, and Transformation

### Purpose

Own the formal hiring-interview lifecycle attached to a `JobApplication`, including the authoritative interview schedule state, location mode, hiring-context linkage, actor-attributed interview history, and organization/candidate coordination.

### Goal

Turn an interviewable application plus an authorized scheduling decision into a traceable hiring interview that can be consumed safely by the organization, candidate, messaging, notification, video, calendar, audit, privacy, and operations rails without making any of those rails the owner of interview truth.

### What enters

At minimum:

- authenticated actor context from Identity & Access;
- an authorization decision from Role / Authority;
- an interviewable `JobApplication` context from Candidate Application & Resume Privacy;
- the owning `Organization` and candidate relationship facts from their source owners;
- requested interview time range;
- requested `JobInterviewLocationType`;
- display timezone context;
- optional location text or externally supplied meeting reference under approved security rules;
- optional participant intent after U-CL06-14 is resolved;
- idempotency/correlation context from shared platform infrastructure;
- normalized downstream results from Video, Calendar, Messaging, Notification, Privacy, and Ops where relevant.

### What leaves

The Module produces:

- authoritative `JobInterview` state;
- immutable `JobInterviewEvent` domain history;
- participant state after participant ownership is approved;
- public, privacy-shaped interview queries;
- versioned domain events after committed state changes;
- requests to Messaging, Notification, Video, Calendar, Audit, Privacy, and Ops through their public interfaces;
- owner-local responses to application-state changes and privacy instructions.

### Business/capability transformation

```text
interviewable JobApplication
+ authorized hiring/candidate actor
+ proposed/confirmed schedule intent
+ local Job Interview policy
        ↓
JobInterview source truth
+ JobInterviewEvent proof
        ↓
owner-issued domain event / outbox
        ↓
Messaging / Notification / Video / Calendar / Audit / Privacy / Ops handoffs
```

### Why this deserves its own Module boundary

A hiring interview resembles a marketplace Booking technically but carries different business meaning, parent truth, participants, authorization, privacy, and lifecycle consequences. The platform explicitly states `JobInterview` is **not** `Booking`. Sharing timezone, state-machine, provider, queue, or token mechanics does not justify merging their source records or policies.

## 3. Owned Truth

### 3.1 Confirmed owned schemas/models

| Record | Meaning | Ownership status |
|---|---|---|
| `JobInterview` | The authoritative record that a formal hiring interview exists, which application/organization/candidate it belongs to, when it is intended to occur, its location mode, its lifecycle status, and its local downstream-reference state. | **Binding / confirmed** |
| `JobInterviewEvent` | Immutable interview-domain history recording actor type, optional actor ID, prior/next interview status, event name, reason, safe metadata, and timestamp. | **Binding / confirmed** |

### 3.2 Proposed owned schemas/models

| Record | Meaning | Ownership status |
|---|---|---|
| `JobInterviewParticipant` | Interview-local fact that a User participates in one specific hiring interview under a participant role and invitation-response state. | **Proposed Ruling — U-CL06-14** |

**Proposed Ruling:** Job Interview should own `JobInterviewParticipant` because the row is interview-scoped, cascade-bound to `JobInterview`, and describes interview-local participation rather than organization-wide authority or Messaging participation. This ruling must be explicitly accepted before participant mutation code is committed.

### 3.3 Confirmed owned enums/statuses

- `JobInterviewStatus`
  - `draft`
  - `proposed`
  - `scheduled`
  - `rescheduled`
  - `completed`
  - `cancelled`
  - `no_show`
  - `expired`
- `JobInterviewLocationType`
  - `video`
  - `phone`
  - `in_person`
- `JobInterviewEventActor`
  - `system`
  - `candidate`
  - `organization_member`
  - `admin`
  - `webhook`

### 3.4 Proposed owned enums/statuses

- `JobInterviewParticipantRole`
  - `candidate`
  - `interviewer`
  - `coordinator`
  - `observer`
- `JobInterviewParticipantStatus`
  - `invited`
  - `accepted`
  - `declined`
  - `tentative`
  - `no_response`

Ownership of these two enums follows U-CL06-14 and is not binding until approved.

### 3.5 Lifecycles owned

**Binding:** Job Interview alone owns `JobInterview.status` changes.

**Proposed:** if U-CL06-14 is accepted, Job Interview also owns participant invitation/response lifecycle.

The Module does not own `JobApplication.status`, `JobApplication.stage`, `Job.status`, `Thread` lifecycle, `Notification` lifecycle, `JobInterviewVideoRoom` lifecycle, calendar-provider lifecycle, or privacy-request lifecycle.

### 3.6 Source-of-truth records

- `JobInterview` is interview state truth.
- `JobInterviewEvent` is interview-domain event/history truth.
- `JobInterviewParticipant` is participant truth only after proposed ownership is accepted.

No provider object, meeting URL, calendar event, Thread, Notification, AccessAuditLog, or frontend state may override these records.

### 3.7 Domain events / ledgers owned

`JobInterviewEvent` is a domain ledger. The Module owns its vocabulary and when rows are appended. It uses the canonical shared `appendDomainLifecycleEvent` mechanism, but the shared mechanism must not move the ledger into a generic event table.

### 3.8 Projections owned

None confirmed.

Dashboard list/detail DTOs are read models derived from `JobInterview` and permitted dependency facts. They are not independent source projections. Job Interview has no Typesense/Search projection responsibility.

### 3.9 Snapshots / proof owned

- `JobInterviewEvent` is supporting proof of interview lifecycle and actor-attributed changes.
- The schema’s local calendar reference/status fields may represent interview-local attachment state **only if U-CL06-16 confirms this interpretation**.
- Generic `AuditEvent` and `AccessAuditLog` are not owned here.

### 3.10 Policies and invariants owned

Job Interview owns policy for:

- whether a supplied application/organization/candidate tuple is one coherent hiring case;
- interview time-range validity;
- allowed interview lifecycle transitions after U-CL06-15 is resolved for the affected transition set;
- how interview-specific location mode constrains required fields;
- when an interview-domain event must be appended;
- participant assignment/response rules after U-CL06-14;
- reschedule history/cardinality after U-CL06-15;
- how normalized downstream success/failure affects **interview-local** state without absorbing downstream truth;
- how parent application changes affect interview state after the relevant application/interview policy is explicitly approved;
- privacy enumeration and owner-local erase/anonymize/retain behavior after retention rules are approved.

## 4. Explicit Non-Ownership

The Module must not own or recreate the following.

| Adjacent owner | Truth / responsibility that remains outside Job Interview | Concrete duplicate to prohibit |
|---|---|---|
| Identity & Access | User authentication, session validity, step-up challenges, security profile | local auth/session helper, local MFA state |
| Role / Authority | Permission interpretation for organization, participant, platform, and ownership scope | `canRecruiterManageInterview`, raw role-switch authorization engine |
| Organization Hiring | `Organization`, `OrganizationMember` row/role assignment, `Job`, organization hiring lifecycle | local Organization/Job repository writes |
| Candidate Application & Resume Privacy | `CandidateProfile`, `JobApplication.status`, `JobApplication.stage`, resume business authorization, `ResumeAccessLog` | direct application-stage update, local resume signer/log |
| Job Compliance | Job-posting compliance scan, findings, disclosure proof | interview-side compliance scanner |
| Track Subscription & Entitlement | candidate/organization commercial entitlements and usage truth | `premiumInterview`, interview quota/boost booleans |
| Admin Review / Compliance Hold | reusable platform stop-sign lifecycle | local `blocked`, `onHold`, or interview-hold table |
| Messaging | `Thread`, `ThreadParticipant`, `Message`, `MessageMedia` | `InterviewChat`, local thread table |
| Notification | Notification record, channel routing, provider delivery, retries | direct SES/SMS/push dispatch in Job Interview |
| Video Infrastructure | `JobInterviewVideoRoom`, room creation, join credentials, provider status, provider-event dedupe | local Daily/Agora client, permanent room URLs as truth |
| Booking & Calendar / calendar owner | calendar connection, free/busy, provider calls, webhook verification/dedupe, provider-event truth | local Cronofy client, `ProcessedInterviewCalendarEvent` |
| Media / File Access | MediaAsset, file validation/scan, private storage, grants, signed URLs | local presigner, resume storage/access grant |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | local generic audit/access log table |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, orchestration | local GDPR/privacy workflow |
| Observability / Ops | `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident` | treating JobInterviewEvent as the only ops failure record |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense adapter/query/reconciliation | interview indexing client or search truth |
| Booking & Calendar | paid service Booking lifecycle | `InterviewBooking` or Booking-backed hiring interview |

## 5. Module Architecture Principles

1. `JobInterview` is the only source of truth for hiring interview lifecycle.
2. A Job Interview is attached to a `JobApplication`; it is not a paid Booking.
3. The application, organization, and candidate IDs on an interview must resolve to one coherent hiring case.
4. Job Interview never mutates `JobApplication.status` or `JobApplication.stage` directly.
5. Role / Authority decides who may act; Job Interview supplies action names and relationship facts.
6. Provider resources are requested after interview truth commits; provider success does not create interview truth retroactively.
7. Video Infrastructure owns `JobInterviewVideoRoom` and all join-token/provider mechanics.
8. Calendar-provider callbacks are verified/deduplicated by the calendar owner, never by Job Interview.
9. Domain event history (`JobInterviewEvent`) and generic audit/access evidence (`AuditEvent`/`AccessAuditLog`) are distinct.
10. Every state mutation must append appropriate interview-domain history transactionally.
11. Every retryable command is idempotent through the canonical platform primitive.
12. Every conflicting transition uses database-backed concurrency protection; no in-memory locks.
13. External effects use outbox/queue infrastructure and must not be performed as untracked fire-and-forget work.
14. Downstream failure does not silently rewrite truthful interview state.
15. Notification payloads must not contain resume bodies, raw application answers, reusable credentials, or unnecessary location details.
16. Privacy orchestration stays Privacy-owned; Job Interview only enumerates and executes against its own records.
17. Participant management cannot ship until U-CL06-14 is settled.
18. Advanced rescheduling cannot ship until U-CL06-15 is settled.
19. Production calendar sync cannot ship until U-CL06-16 is settled.
20. Any implementation requiring a changed binding decision must update architecture first.

## 6. Proposed Folder / Code Structure

Use the repository’s established Module conventions if they exist. The following is the approved responsibility map for this Module; names may adapt to root standards without moving responsibilities.

```text
src/modules/job-interview/
  domain/
    job-interview-policy.ts
    job-interview-transition-policy.ts
    job-interview-errors.ts
    job-interview-event-names.ts
    participant-policy.ts              # only after U-CL06-14 approval
    reschedule-policy.ts               # only after U-CL06-15 approval

  application/
    commands/
      propose-interview.ts
      schedule-interview.ts
      cancel-interview.ts
      complete-interview.ts
      mark-interview-no-show.ts
      reschedule-interview.ts          # blocked until U-CL06-15
      add-interview-participant.ts     # blocked until U-CL06-14
      remove-interview-participant.ts  # blocked until U-CL06-14
      respond-to-interview-invitation.ts
    queries/
      get-interview.ts
      list-application-interviews.ts
      list-organization-interviews.ts
      list-candidate-interviews.ts
      get-interview-timeline.ts
    handlers/
      handle-application-state-changed.ts
      handle-video-room-result.ts
      handle-calendar-sync-result.ts   # after U-CL06-16
    orchestration/
      interview-collaboration-handoff.ts
      interview-integration-retry.ts

  persistence/
    job-interview-repository.ts
    job-interview-event-repository.ts
    job-interview-participant-repository.ts # only after U-CL06-14

  contracts/
    public-commands.ts
    public-queries.ts
    domain-events.ts
    dependency-ports.ts
    privacy.ts

  events/
    event-payloads.ts
    event-mapper.ts

  workers/
    expire-interview-proposals.ts      # only if expiry policy approved
    reconcile-interview-integrations.ts

  privacy/
    enumerate-interview-subject-data.ts
    execute-interview-privacy-instruction.ts
    interview-retention-policy.ts

  ui/
    components/
    server-actions/
    view-models/

  tests/
    domain/
    contracts/
    persistence/
    integration/
    authorization/
    privacy/
    e2e/
```

### Folder prohibitions

Do **not** create inside this Module:

- `providers/` for Daily, Agora, Cronofy, Nylas, SES, SMS, storage, or search;
- generic `auth/`, `permissions/`, `idempotency/`, `queue/`, `audit/`, or `observability/` infrastructure;
- `media/` storage mechanics;
- direct cross-domain Prisma repositories.

Provider-neutral dependency ports may exist under `contracts/dependency-ports.ts`; concrete provider adapters remain in their canonical owner Modules/integration layer.

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / UI | Interview list/detail/proposal/scheduling/reschedule/participant surfaces permitted by current feature phase; runtime input shaping | authority policy, provider calls, direct Prisma writes, application-stage writes |
| Server actions / route handlers | runtime validation, actor resolution call, command/query dispatch, safe error mapping | workflow truth, raw provider SDK, direct multi-Module writes |
| Application services | command orchestration, transaction entry, dependency-port calls, domain event/outbox requests | dependency lifecycle rules |
| Domain policy | context consistency, time/location rules, interview transition rules, participant/reschedule rules once approved | role interpretation, application lifecycle, provider status mapping |
| Persistence | Job Interview-owned Prisma access only, transactional aggregate/event writes | Organization, JobApplication, Thread, Notification, Video, Audit, Privacy table writes |
| Workers | owner-defined expiry/reconciliation/integration retry behavior using shared queue | generic queue framework, provider webhook receiver |
| Adapters | none owned for external providers; only dependency-client implementations against internal typed ports if root architecture places them here | provider credentials, provider-native domain truth |
| Public contracts | Job Interview commands, queries, domain events, privacy executor | universal polymorphic repository/permission API |

## 8. Data Model

### 8.1 `JobInterview`

**Purpose:** authoritative hiring-interview aggregate root.

**Key relationships:**

- belongs to `JobApplication`;
- references `Organization`;
- references `CandidateProfile`;
- optionally references scheduling `User`;
- self-references predecessor interview for rescheduling;
- owns interview events;
- proposed ownership of participant rows;
- has one Video-owned `JobInterviewVideoRoom` relation;
- may have a Messaging-owned `Thread` relation.

**Authoritative fields:**

- `jobApplicationId`;
- `organizationId`;
- `candidateProfileId`;
- `scheduledByUserId` as actor/context fact, not authority proof;
- `status`;
- `locationType`;
- `startsAt`, `endsAt`;
- `candidateTimezone`, `organizationTimezone` as display/context metadata;
- `locationText` subject to privacy policy;
- `rescheduledFromInterviewId` subject to U-CL06-15;
- terminal timestamps (`cancelledAt`, `completedAt`, `noShowAt`).

**Conditionally authoritative local attachment fields:**

- `externalCalendarEventId`;
- `externalCalendarProvider`;
- `externalSyncStatus`;
- `externalSyncError`.

These fields may be used as local calendar attachment/sync state only after U-CL06-16 confirms the calendar owner boundary. They never become calendar-provider source truth.

**Security-sensitive field:** `externalMeetingUrl`. It must not be treated as a permanent reusable credential. Until a binding rule is approved, provider-generated video access must use Video Infrastructure rather than this field.

**Lifecycle field:** `status`.

**Indexes already evidenced:**

- `jobApplicationId`;
- `(organizationId, status)`;
- `(candidateProfileId, status)`;
- `scheduledByUserId`;
- `(startsAt, endsAt)`;
- `(externalCalendarProvider, externalCalendarEventId)`;
- `externalSyncStatus`.

**Concurrency-sensitive fields:** `status`, `startsAt`, `endsAt`, `rescheduledFromInterviewId`, terminal timestamps, and any local external-sync fields.

**Concurrency note:** current schema has `updatedAt` but no explicit version column. Canonical `withOptimisticConcurrency` supports version or compare-and-set/`updatedAt`. Job Interview must follow the root persistence standard; it must not add a version column silently. Critical transition operations may additionally use `acquireAggregateLock` or conditional updates.

**Retention/privacy concerns:** candidate identity linkage, participant identities, exact location text, timezones, meeting references, scheduling actor, calendar references, and terminal timestamps are personal/hiring data. Cascade deletion must be reconciled with legal retention and append-only proof before destructive production behavior.

### 8.2 `JobInterviewEvent`

**Purpose:** immutable domain history for interview state and important interview-local actions.

**Authoritative fields:**

- `interviewId`;
- `actor`;
- optional `actorId`;
- `fromStatus`, `toStatus`;
- `name`;
- optional `reason`;
- minimized `metadata`;
- `createdAt`.

**Lifecycle:** append-only; rows are not an editable state machine.

**Indexes:** `(interviewId, createdAt)`, `actor`, `name`.

**Risk:** `name` is free text. A stable event-name registry is required before external consumers depend on event naming. Do not place provider payloads, resume text, application bodies, reusable URLs/tokens, or unnecessary personal data in `metadata`.

**Retention:** event history is supporting compliance/audit evidence. Current cascade deletion from `JobInterview` conflicts with “append-only proof” expectations and needs a retention ruling.

### 8.3 `JobInterviewParticipant` — Proposed Ruling

**Purpose:** record interview-local participation and invitation response.

**Key relationships:** composite key `(interviewId, userId)`, belongs to `JobInterview` and `User`.

**Authoritative fields:** `role`, `status`, `invitedAt`, `respondedAt`.

**Uniqueness:** one row per User per interview through composite primary key.

**Unresolved:** removal/revocation semantics, candidate-row invariant, whether observers/coordinators must be OrganizationMembers, and whether a removed participant is deleted or represented by a new status.

Do not add a second invitation/attendee table while U-CL06-14 remains unresolved.

### 8.4 Referenced but not owned records

- `JobApplication`, `CandidateProfile` — Candidate Application & Resume Privacy;
- `Organization`, `OrganizationMember` — Organization Hiring for row truth; Role / Authority for interpretation;
- `Thread`, `ThreadParticipant` — Messaging;
- `Notification`/delivery — Notification;
- `JobInterviewVideoRoom` — Video Infrastructure;
- `AccessAuditLog` — Audit / Event Ledger;
- calendar connection/provider-event records — calendar owner;
- privacy request/job/exemption records — Privacy.

## 9. Enums, Statuses, and Lifecycles

### 9.1 Interview lifecycle

**Owner:** Job Interview.

**Statuses:** `draft`, `proposed`, `scheduled`, `rescheduled`, `completed`, `cancelled`, `no_show`, `expired`.

### Binding lifecycle rules

1. Only Job Interview may mutate `JobInterview.status`.
2. Every successful status transition writes the aggregate and a `JobInterviewEvent` in the same transaction.
3. A consumer may not infer application stage/status from interview status.
4. Provider failure does not implicitly transition interview lifecycle.
5. Terminal timestamp fields must correspond to their terminal outcome when used.
6. A transition must validate the current status under concurrency; stale commands return conflict.
7. `startsAt < endsAt` is required for every interview record.

### U-CL06-15 — transition matrix unresolved

The exact legal transition graph is not yet binding. Advanced rescheduling is explicitly blocked by CL-06 until this is settled.

**Proposed Ruling for architecture review, not implementation without approval:**

```text
draft ──→ proposed ──→ scheduled ──→ completed
  │          │             ├──────→ cancelled
  │          │             ├──────→ no_show
  │          │             └──────→ rescheduled ──→ successor interview
  │          ├────────────→ cancelled
  │          └────────────→ expired
  ├───────────────────────→ cancelled
  └───────────────────────→ expired
```

Optional direct `draft → scheduled` and any reopen rules require explicit approval. `completed`, `cancelled`, `no_show`, and `expired` should be treated as terminal unless a later architecture decision specifies a compensating/successor command. `rescheduled` should represent historical state if the successor model is approved.

### 9.2 Rescheduling

Current schema supports a predecessor reference and a plural successor relation. This alone does not define semantics.

U-CL06-15 must answer:

- mutate current interview versus create successor;
- whether there can be more than one successor;
- which record is “active” after a reschedule;
- how participants, Thread, Video room, calendar reference, and notifications transfer/revoke;
- whether a terminal interview may be rescheduled.

**Proposed Ruling:** prefer a successor interview for reschedule history and limit each predecessor to one effective active successor. This remains non-binding until accepted.

### 9.3 Participant lifecycle — Proposed

Statuses: `invited`, `accepted`, `declined`, `tentative`, `no_response`.

A minimal response interpretation may be:

```text
invited/no_response → accepted | declined | tentative
tentative           → accepted | declined
```

Removal/revocation is not represented by the current enum and must not be invented as hard deletion without U-CL06-14 resolution.

## 10. Commands

The following names are the preferred Module contract names. An explicitly approved equivalent may be used if root conventions require different naming, but ownership and behavior must remain identical.

### 10.1 `proposeInterview`

- **Purpose:** create an interview proposal against an interviewable application.
- **Actor/context:** authenticated actor; organization/candidate relationship facts; Role / Authority decision.
- **Authoritative inputs:** application ID, requested start/end, location type, timezone context, optional safe location/reference data, idempotency key.
- **Preconditions:** application exists and is interviewable; organization/candidate tuple matches; valid time range; actor authorized; applicable holds do not block under approved policy.
- **Writes:** `JobInterview`; `JobInterviewEvent`; outbox entry through shared mechanism.
- **Shared operations:** `resolveAuthenticatedActor`, `authorizeResourceAction`, `queryOwnerFacts`, `executeIdempotentCommand`, concurrency primitive, `appendDomainLifecycleEvent`, `publishDomainEvent`.
- **Effects:** may request Notification only after commit; participant rows only after U-CL06-14.
- **Idempotency:** repeated same semantic command replays original result; conflicting fingerprint returns deterministic conflict.
- **Failures:** unauthenticated, unauthorized, context mismatch, invalid time, invalid transition/policy unresolved, dependency unavailable, conflict.

### 10.2 `scheduleInterview`

- **Purpose:** confirm schedule state for an interview under an approved transition subset.
- **Inputs:** interview ID, expected concurrency token/current state, times/location/timezones, actor, idempotency key.
- **Preconditions:** approved transition; context still valid; actor authorized; time range valid.
- **Writes:** `JobInterview`, event, outbox.
- **Effects:** later features may request Messaging/Notification/Video/Calendar; provider calls never precede source commit.
- **Failure:** downstream integration failure does not roll back truthful scheduled interview unless an explicitly approved business policy says scheduling itself requires that dependency.

### 10.3 `cancelInterview`

- **Purpose:** transition an eligible interview to cancelled.
- **Inputs:** interview ID, actor, reason, expected state/version, idempotency key.
- **Writes:** status, `cancelledAt`, event/outbox.
- **Effects:** requests downstream revocation/update through owner contracts; those failures retry independently.

### 10.4 `completeInterview`

- **Purpose:** record that the hiring interview occurred and completed.
- **Writes:** status, `completedAt`, event/outbox.
- **Must not:** advance application status/stage directly.

### 10.5 `markInterviewNoShow`

- **Purpose:** record approved no-show outcome.
- **Writes:** status, `noShowAt`, event/outbox.
- **Unresolved:** whether absent-party detail belongs in event metadata or a future field. Do not add sensitive free-text payload without architecture.

### 10.6 `rescheduleInterview` — blocked by U-CL06-15

- **Purpose:** preserve deterministic reschedule history while establishing the new intended schedule.
- **Preconditions:** U-CL06-15 approved.
- **Writes:** according to approved mutate/successor model plus event/outbox.
- **Effects:** cancel/update old downstream calendar/video access and request new resources through owner interfaces.
- **Idempotency/concurrency:** one semantic reschedule result under concurrent requests.

### 10.7 `addInterviewParticipant` — blocked by U-CL06-14

- **Purpose:** add one interview-local participant.
- **Preconditions:** participant ownership and assignment rules approved; user eligibility facts resolved from source owners; no duplicate composite key.
- **Writes:** participant row + event/outbox.
- **Must not:** create OrganizationMember or ThreadParticipant directly.

### 10.8 `removeInterviewParticipant` — blocked by U-CL06-14

- **Purpose:** revoke/remove interview-local participation under explicitly approved semantics.
- **Must not:** hard-delete by convenience if evidence/notification/access revocation requirements call for a durable state.

### 10.9 `respondToInterviewInvitation` — participant feature

- **Purpose:** allow invited participant to accept, decline, or tentatively respond.
- **Writes:** participant status/`respondedAt`, interview event/outbox where policy requires.
- **Concurrency:** participant row key is lock resource; repeated same response is idempotent.

### 10.10 `handleApplicationStateChanged`

- **Purpose:** consume a Candidate Application-owned event and apply only the approved owner-local interview effect.
- **Input:** versioned domain event envelope with application ID and changed state facts.
- **Must not:** rewrite application truth.
- **Idempotency:** `deduplicateDomainEvent` before owner-local side effects.
- **Unresolved:** exact withdrawal/rejection/closed/hired effects on active interviews.

### 10.11 Privacy executor commands

`executePrivacyInstruction` is implemented as a Job Interview owner executor under the Privacy-defined protocol, not as a user-facing privacy command. It may erase, anonymize, detach, restrict, or retain only after a Privacy-owned instruction and retention evaluation.

## 11. Queries / Decisions

### `getInterview`

- **Consumers:** candidate/org UI, Video/Calendar context requests, support/admin under authority.
- **Input:** actor + interview ID.
- **Result:** privacy-shaped source truth/read model.
- **Must not infer:** resume permission, video join permission, calendar connection validity, or application outcome.

### `listApplicationInterviews`

- **Consumers:** Candidate Application, organization/candidate UI.
- **Input:** actor + `jobApplicationId` + pagination.
- **Result:** interview source records/read model ordered by schedule/history.
- **Must not infer:** application stage.

### `listOrganizationInterviews`

- **Consumers:** Organization Hiring dashboard.
- **Input:** actor + organization ID + time/status filters + pagination.
- **Result:** privacy-shaped organization interview schedule.
- **Must not infer:** organization authority merely because a row is returned; authorization occurs before query.

### `listCandidateInterviews`

- **Consumers:** candidate dashboard.
- **Input:** actor + candidate profile + filters.
- **Result:** candidate-owned view of interview source truth.

### `getInterviewTimeline`

- **Consumers:** authorized participant/org/admin UI, audit/debug support where allowed.
- **Input:** actor + interview ID.
- **Result:** ordered `JobInterviewEvent` history with metadata filtered by viewer policy.
- **Must not infer:** generic AuditEvent or AccessAuditLog completeness.

### `getInterviewAuthorizationFacts`

This is an owner-facts DTO under canonical `queryOwnerFacts`, not a universal repository. It should expose only minimum identifiers/state needed by Role / Authority, e.g. interview ID, organization ID, candidate profile owner reference where permitted, participant relation if approved, and current status. It does not return raw application/resume content.

### Decision result pattern

Job Interview may return local allow/deny/conflict results for its own policy. It must not create a generic hiring readiness engine. If the shared `returnDecisionResult` envelope is used, the policy owner remains Job Interview for interview-specific decisions.

## 12. Public Module Interface

### Public commands

Binding/core, subject to approved transition subset:

- `proposeInterview`
- `scheduleInterview`
- `cancelInterview`
- `completeInterview`
- `markInterviewNoShow`

Blocked until decisions:

- `rescheduleInterview` — U-CL06-15;
- `addInterviewParticipant` — U-CL06-14;
- `removeInterviewParticipant` — U-CL06-14;
- `respondToInterviewInvitation` — participant ownership/policy portion of U-CL06-14.

### Public queries

- `getInterview`
- `listApplicationInterviews`
- `listOrganizationInterviews`
- `listCandidateInterviews`
- `getInterviewTimeline`
- owner-fact query implementing the canonical `queryOwnerFacts` pattern.

### Emitted domain events

Preferred stable event family:

- `interview.proposed`
- `interview.scheduled`
- `interview.rescheduled`
- `interview.cancelled`
- `interview.completed`
- `interview.no_show`
- `interview.expired`
- `interview.participant_invited`
- `interview.participant_removed` only after removal semantics exist;
- `interview.participant_responded`

Event names are a proposed stable registry because `JobInterviewEvent.name` is currently free text. Consumers must not depend on event names until the registry is approved/versioned.

### Inbound event handlers

- `handleApplicationStateChanged`
- normalized Video room result handler;
- normalized Calendar sync result handler after U-CL06-16;
- privacy executor invocation through Privacy protocol.

### Privacy executor

- `enumerateSubjectData` implementation for Job Interview;
- `executePrivacyInstruction` implementation for Job Interview;
- `evaluateRetentionRequirement` facts for interview data.

### Provider-facing interfaces

None directly owned. Job Interview must not expose raw provider webhooks or provider SDK interfaces.

## 13. Inbound Dependencies

| Owning Module / capability | Public operation/interface consumed | Why required | Minimum information | May block action? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | `resolveAuthenticatedActor` | trusted actor context | actor ID/type/session assurance | yes, protected actions | auth/session logic |
| Role / Authority | `authorizeResourceAction` | organization/candidate/admin permission | action + owner facts + actor | yes | role interpretation |
| Organization Hiring | `getOrganizationHiringContext` or owner-fact DTO | verify organization/job relationship and active hiring context | organization ID, job/application relationship facts, relevant status/version | yes | Organization/Job lifecycle |
| Candidate Application & Resume Privacy | interviewability facts / `getJobApplicationDetail`-grade owner DTO | verify application/candidate/job consistency | application ID, candidate profile ID, job/org IDs, source state/version | yes | application stage/status policy |
| Candidate Application & Resume Privacy | `authorizeContextualResumeAccess` / resume-review contract | interview-related resume review | actor, application, media, reason=`interview_review` | yes for resume access only | ResumeAccessLog/authorization |
| Admin Review / Compliance Hold | `evaluateComplianceHold` | enforce applicable reusable stop sign where Cluster/root policy requires | target/action + hold IDs/reasons | yes when applicable | local hold flags |
| Messaging | `ensureContextThread` | create/retrieve interview conversation | context type `job_interview`, interview ID, approved participant IDs | no to source interview truth; may degrade collaboration | Thread lifecycle |
| Notification | `requestNotification`, recipient contract | alert users after interview facts | recipients/template/safe variables/idempotency | no to source truth; retryable | delivery/provider logic |
| Video Infrastructure | JobInterview room request/join contract; internally uses `invokeVideoProvider` | live video interview | interview ID, time window, participant context | room availability may degrade video experience; does not own interview state | provider rooms/tokens |
| Calendar capability | provider-neutral create/update/cancel/sync contract after U-CL06-16 | external calendar handoff | interview ID, times, safe participant/event fields, idempotency | no to source truth unless future approved policy says otherwise | provider SDK/webhook/dedupe |
| Audit / Event Ledger | `appendAuditEvent`, `recordSensitiveAccess` | generic proof and restricted-access evidence | actor/action/target/outcome/safe metadata | audit failure follows root policy; no silent skip for required evidence | AuditEvent/AccessAuditLog tables |
| Privacy / Data Erasure | privacy target protocol | legal erase/export/restrict workflow | target instruction, subject, retention context | yes for destructive action | PrivacyRequest/DataErasureJob |
| Observability / Ops | `recordIntegrationFailure` | visible technical degradation | provider/operation/source ref/retryability/request ID | no business approval; records failure | IntegrationFailure lifecycle |

### Dependency failure rule

If a required gate is unavailable, return explicit unavailable/deny/retry according to root/Cluster policy. Never fall back to direct cross-domain Prisma access or permissive behavior.

## 14. Outbound Consumers and Effects

| Consumer | What it may consume | Event/effect | Boundary |
|---|---|---|---|
| Organization Hiring | interview schedule/status summaries | proposed/scheduled/completed/cancelled etc. | cannot mutate interview table |
| Candidate Application | interview facts and lifecycle events | may choose to advance application stage through its own command | Job Interview never writes stage/status |
| Role / Authority | minimal owner facts | permission evaluation | Role owns interpretation, not interview truth |
| Messaging | interview context/approved participant IDs | thread creation/update request | Messaging owns Thread/participants |
| Notification | safe event facts/recipients | alert delivery | Notification owns provider attempts |
| Video Infrastructure | interview ID/time/participant context | room create/update/cancel/token requests | Video owns room/provider truth |
| Calendar capability | schedule intent | external event create/update/cancel | calendar owner owns provider truth |
| Audit | significant action/access context | generic audit/access append | audit records are separate proof |
| Privacy | subject-data inventory/executor results | erase/export/restrict orchestration | Privacy owns request/job |
| Ops | source reference and safe diagnostics | integration failure/incident telemetry | operational evidence only |

Downstream owner commands should be published/queued only after the source transaction commits. A worker must never mutate another Module’s tables directly.

## 15. Canonical Shared Operations Used

The supplied Canonical Shared Operations Architecture provides canonical operation names but no SH-### identifiers. Therefore the operation name is the canonical identifier in this document.

| Canonical operation | Classification / owner | Why Job Interview uses it | Invocation point | Local policy that remains Job Interview-owned | Expected result | Prohibited duplicate |
|---|---|---|---|---|---|---|
| `resolveAuthenticatedActor` | Platform capability — Identity & Access | obtain trusted actor | every protected command/query | action being attempted | typed actor context | `getCurrentUser`, feature auth helper |
| `authorizeResourceAction` | Cross-cutting capability — Role / Authority | determine org/candidate/admin permission | after actor resolution, before protected work | action vocabulary + interview relationship facts | typed allow/deny decision | `canRecruiterManageInterview` |
| `queryOwnerFacts` | Shared contract, separate implementations — each source owner | obtain minimum application/org facts without repository coupling | authorization/context validation | which facts Job Interview exposes/needs | small typed DTO | universal cross-domain repository |
| `evaluateComplianceHold` | Cross-cutting capability — Holds | enforce applicable stop signs | before affected sensitive/lifecycle action when policy applies | how applicable hold blocks Job Interview action | hold decision/references | `interviewBlocked` flag/table |
| `appendAuditEvent` | Platform audit capability — Audit | generic action proof where required | after significant approved action | which actions merit generic audit | audit receipt | local AuditEvent |
| `recordSensitiveAccess` | Cross-cutting capability — Audit | proof of restricted interview/resume/video/admin access | sensitive query/grant/join path | sensitivity classification and safe context | access-log receipt | local AccessAuditLog |
| `appendDomainLifecycleEvent` | Shared mechanism / separate truth — shared persistence | append `JobInterviewEvent` with state change | inside owner transaction | event vocabulary/metadata | event row | universal domain-event table |
| `requestNotification` | Platform notification capability — Notification | request user alert | after owner event/outbox | trigger meaning, safe variables | delivery request receipt | SES/SMS/push code |
| `resolveNotificationRecipients` | Shared contract — source owner + Notification | derive interview recipients without Notification owning participant truth | notification orchestration | which interview roles receive which event | user IDs / recipient group | global participant policy in Notification |
| `executeIdempotentCommand` | Platform primitive — application infrastructure | safe command replay | every retryable mutation | semantic command identity/conflict behavior | original/new command result | ad-hoc idempotency table |
| `publishDomainEvent` | Platform primitive — outbox infrastructure | reliable post-commit event | owner transaction/outbox | event name/payload/privacy | durable event envelope | fire-and-forget event bus write |
| `deduplicateDomainEvent` | Platform primitive — event inbox | safe application/provider-normalized event consumption | application-state and normalized result handlers | owner-local side effect | inbox claim/result | custom processed-event table |
| `enqueueReliableJob` | Platform primitive — shared queue | expiry/retry/reconciliation/privacy work | async handoff | payload/completion meaning | durable job receipt | local queue framework |
| `executeRetryWithBackoff` | Platform primitive — queue/platform | retry transient technical failures | worker/provider handoff | retryable vs permanent classification | retry/dead-letter outcome | bespoke retry loop |
| `orchestrateWorkflowSteps` | Shared mechanism / separate workflow truth — workflow owner | coordinate multi-owner interview handoffs if simple outbox receipts are insufficient | collaboration/provider workflow | steps, dependencies, compensation | persisted run/step acknowledgments | generic hiring truth |
| `acquireAggregateLock` | Platform primitive — shared persistence | serialize critical interview transitions | cancel/reschedule/terminal races | lock key/conflicting actions | lock/transaction scope | in-memory mutex |
| `withOptimisticConcurrency` | Platform primitive — shared persistence | reject stale updates | mutable interview/participant operations | retry/merge/conflict policy | updated record or conflict | blind last-write-wins |
| `transitionLifecycleState` | Shared mechanism / separate truth | reusable transition plumbing | each status command | complete Job Interview transition graph | validated transition result | generic state policy table |
| `runDeadlineExpiration` | Cross-cutting scheduler — shared scheduler/queue | expire stale proposals only if expiry policy is approved | scheduled worker | what expires and resulting transition | owner command dispatch | custom cron framework |
| `ensureContextThread` | Module public interface — Messaging | create/retrieve interview Thread | after interview/participant commit | context and participant facts | Thread reference | local chat table |
| `recordIntegrationFailure` | Cross-cutting capability — Observability/Ops | track degraded handoff/provider result | failure handling | business effect remains local | IntegrationFailure ref | JobInterviewEvent as sole ops log |
| `enumerateSubjectData` | Cross-cutting privacy protocol — each data owner | expose interview-held subject data | Privacy inventory step | schema/relationship meaning | target inventory | local privacy request workflow |
| `executePrivacyInstruction` | Cross-cutting privacy protocol — Privacy orchestrates, Job Interview executes | erase/anonymize/restrict/retain own data | Privacy worker callback | field-level owner behavior | target result | local DataErasureJob |
| `evaluateRetentionRequirement` | Cross-cutting privacy protocol — owner facts + Privacy exemption | determine retention before destructive action | privacy executor | interview retention facts | retain/erase/anonymize decision facts | local exemption table |
| `anonymizePersonalFields` | Cross-cutting primitive — owner mapping | apply approved field-level minimization | privacy executor | exact field map | proof/result | global blind scrubber |

### Dependency-owned provider pattern operations

The following are **not implemented in Job Interview**. They are requirements on the provider-owning Module used by Job Interview:

- `invokeVideoProvider` — Video Infrastructure;
- `invokeCalendarProvider` — Booking & Calendar under current canonical registry, subject to U-CL06-16 for hiring use;
- `verifyProviderWebhookSignature`;
- `deduplicateProviderEvent`;
- `translateProviderStatus`;
- `reconcileProviderState`.

Job Interview consumes normalized owner results only.

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
|---|---|---|---|---|---|
| `validateInterviewContext` | prove application/org/candidate tuple is coherent | owner-fact DTOs + proposed IDs | valid context or reason code | none | hiring interview domain invariant |
| `validateInterviewTimeRange` | enforce `startsAt < endsAt` and approved time requirements | timestamps/timezone metadata | normalized/valid schedule facts | none | interview-specific precondition |
| `validateInterviewTransition` | apply Job Interview transition graph | current status + command + actor/context | allowed transition or reason | none | lifecycle policy belongs to owner |
| `deriveInterviewEvent` | construct safe domain event row and outbox payload | command result/context | event data | `JobInterviewEvent` | event semantics are local |
| `validateParticipantAssignment` | ensure candidate/interviewer/coordinator/observer assignment is valid | interview + source facts + requested role | allow/deny | none | participant policy remains interview-specific; blocked pending U-CL06-14 |
| `applyParticipantResponse` | update interview-local response | participant row + response | updated participant | participant record | participant source truth is local if ruling accepted |
| `buildRescheduleChange` | derive predecessor/successor mutation under approved rule | current interview + new schedule | mutation plan | interview(s) | reschedule semantics are domain policy; blocked pending U-CL06-15 |
| `mapApplicationChangeToInterviewEffect` | decide owner-local consequence of parent application change | application event + active interviews | no-op/cancel/restrict/etc. | JobInterview only | preserves separate application/interview truth |
| `buildInterviewRecipientFacts` | derive source-owned recipient group for Notification/Messaging | interview + participants/source facts | User ID/group facts | none | recipient meaning belongs with source context |
| `buildInterviewPrivacyInventory` | enumerate subject-linked interview data | subject ID/cursor | privacy target items | none | source owner knows data meaning |
| `applyInterviewPrivacyDisposition` | execute one approved privacy action | target instruction + retention result | target execution result | interview-owned records | only owner may mutate its records |

## 17. Shared Mechanism / Separate Truth Rules

1. **State-machine plumbing is shared; `JobInterviewStatus` policy is not.** `transitionLifecycleState` may validate/update mechanically but cannot own the graph.
2. **Append mechanics are shared; `JobInterviewEvent` remains Job Interview truth.** Do not merge with BookingEvent, AuditEvent, or provider-event tables.
3. **Idempotency is shared; semantic command identity is local.** The platform stores claim/result mechanics; Job Interview defines what “same command” means.
4. **Concurrency primitives are shared; aggregate conflicts are local.** Lock key is interview ID or participant composite key; no global hiring lock policy.
5. **Outbox/inbox is shared; event meaning is local.** Consumers dedupe independently.
6. **Queue/retry is shared; retryability is local/provider-owned.** Domain denial is not retried as infrastructure failure.
7. **Video room mechanics are shared/Video-owned; JobInterview remains parent truth.** `JobInterviewVideoRoom` does not merge with `JobInterview`.
8. **Calendar provider mechanics are owner-shared; local sync attachment state is separate if U-CL06-16 approves it.** Never create interview-specific provider dedupe truth.
9. **Messaging thread mechanics are Messaging-owned; interview participation remains separate.** `JobInterviewParticipant` does not become `ThreadParticipant` automatically.
10. **Resume access mechanics are Candidate/Media-owned; interview context only supplies `interview_review`.**
11. **Generic access auditing is shared; `JobInterviewEvent` remains domain history.**
12. **Privacy orchestration is shared/Privacy-owned; owner execution remains Job Interview-specific.**

## 18. Authentication and Authorization

### Authenticated actor requirement

All protected commands and non-public queries call `resolveAuthenticatedActor` first. Frontend identity, a participant ID, or an OrganizationMember ID in the request is not trusted actor proof.

### Role / Authority operation

Use `authorizeResourceAction`. Job Interview supplies only minimum relationship facts and a stable action vocabulary such as:

- `interview.propose`;
- `interview.schedule`;
- `interview.reschedule`;
- `interview.cancel`;
- `interview.complete`;
- `interview.mark_no_show`;
- `interview.view`;
- `interview.view_timeline`;
- `interview.participant.add/remove/respond`;
- `interview.resume_review` as contextual input to Candidate Application, not final resume permission.

Exact action names may follow root convention but must be centralized and typed.

### Relationship facts supplied

At minimum where relevant:

- interview → organization;
- interview → job application;
- job application → job → organization;
- interview → candidate profile;
- candidate profile → owning User;
- scheduled actor reference;
- participant relation after U-CL06-14.

### Resource ownership

- Organization members act under organization-scoped authority interpreted by Role / Authority.
- Candidate access is constrained to the linked CandidateProfile/User and approved participant context.
- Interview participant status does not grant organization authority.
- OrganizationMember role does not automatically grant resume access; Candidate Application must authorize the resume context.

### Admin/support

Admin/support actions require platform authority and must not be broad bypasses for sensitive interview/resume/video/location data. Sensitive reads use `recordSensitiveAccess` where policy requires.

### Step-up

No Job Interview-specific step-up requirement is confirmed. If root security policy requires fresh assurance for a sensitive admin/support action, use Identity & Access `requireStepUpForSensitiveAction`; do not add local MFA state.

## 19. Compliance / Readiness / Entitlement Gates

Job Interview has a narrow gate surface.

| Gate | Underlying truth owner | Query consumed | Gated Job Interview action | Local composition | Result |
|---|---|---|---|---|---|
| Authentication | Identity & Access | `resolveAuthenticatedActor` | all protected actions | none beyond requiring actor | actor or unauthenticated |
| Permission | Role / Authority | `authorizeResourceAction` | mutate/view interview | supply interview/org/candidate facts | allow/deny |
| Application interviewability | Candidate Application | source owner facts/query | propose/schedule/reschedule | require coherent eligible application state as approved | allow/deny/unavailable |
| Organization/job context | Organization Hiring | owner facts | org-side interview actions | ensure application belongs to actor org/job | allow/deny |
| ComplianceHold | Holds | `evaluateComplianceHold` | actions designated by Cluster/root | map applicable hold to local denial; no local flag | allow/deny/remediation |
| Resume review | Candidate Application + Media | contextual resume authorization then Media grant | resume access from interview | supply reason `interview_review` | allow/deny/grant ref |
| Video join | Video Infrastructure with Role/context inputs | Video room/join contract | join video interview | supply participant/time context | token/grant/deny |

No direct Track entitlement is confirmed for Job Interview. Do not introduce local interview premium/quota flags. If a future plan gates interview functionality, Track remains policy truth and this architecture must be updated.

Job Interview does not evaluate Job Compliance or Trust Verification directly merely because the parent job/application once used those gates. Candidate Application/Organization Hiring expose the resulting owner facts needed for interviewability.

## 20. Provider Integrations

### Provider ownership ruling

Job Interview owns **no external provider adapter**.

### Video

```text
Job Interview committed state
→ Video Infrastructure public command
→ Video-owned provider-neutral port
→ Daily.co / future adapter
→ verified/deduped/translated provider effects
→ Video-owned JobInterviewVideoRoom
→ normalized result/event
→ Job Interview reacts locally
```

Job Interview must never store or generate provider-native join tokens, secrets, webhook payloads, or dedupe records. The project overview identifies Daily.co for MVP video, but this choice belongs to Video Infrastructure and may not leak into Job Interview contracts.

### Calendar

```text
Job Interview committed schedule
→ architecture-approved calendar owner public command
→ provider-neutral calendar port
→ Cronofy / future adapter
→ verified/deduped/translated provider result
→ calendar-owner truth
→ normalized result
→ Job Interview local sync attachment state if U-CL06-16 approves
```

The canonical shared operations document currently assigns `invokeCalendarProvider` to Booking & Calendar, but CL-06 U-CL06-16 explicitly questions whether that capability is general enough for hiring. Production calendar sync is blocked until the architecture decides this.

### Webhooks

No webhook endpoint belongs in Job Interview. Provider owner must use:

- `verifyProviderWebhookSignature`;
- `deduplicateProviderEvent`;
- `translateProviderStatus`;
- `reconcileProviderState`.

Job Interview consumes only a trusted normalized internal result/event.

### Reconciliation and retry

Provider reconciliation remains provider-owner policy. Job Interview may run an owner-local reconciliation of **handoff receipts/local sync state**, but it cannot call provider APIs directly to repair another Module’s truth.

### Privacy deletion

Provider resource deletion is requested through Video/Calendar/Messaging owners from a Privacy-driven instruction. Job Interview does not directly delete provider rooms/events.

## 21. Events and Outbox

### Event ownership

The Module owns event meaning; platform event/outbox infrastructure owns reliable publication.

### Emission rule

A domain event is emitted only after the corresponding source-of-truth write succeeds. Preferred pattern:

```text
transaction
  update JobInterview
  append JobInterviewEvent
  persist outbox event
commit
→ publisher retries delivery
```

### Event envelope expectations

Use the root event envelope. At minimum the Cluster/shared architecture expects:

- event ID;
- event name/type;
- schema version;
- aggregate type/ID;
- aggregate version or concurrency token when available;
- occurredAt;
- actor type/ID where safe;
- correlation ID;
- causation ID;
- minimized payload;
- privacy/sensitivity classification if supported.

### Payload minimization

Events may include IDs, status changes, schedule timestamps where required, location type, and safe reason codes. They must not contain:

- raw resumes/application answers;
- private message bodies;
- reusable meeting/join tokens;
- raw provider payloads/secrets;
- exact location text unless a specific authorized consumer requires it and root event policy permits;
- unnecessary personal data.

### Consumer idempotency

All consumers use `deduplicateDomainEvent`. Duplicate delivery must not create duplicate notifications, threads, provider rooms, calendar events, or application-stage requests.

### Events are facts, not commands

`interview.scheduled` means the interview was scheduled. It must not be named or shaped as “set application stage to interview.” Candidate Application may react according to its own policy/public command.

## 22. Background Jobs / Scheduled Work

### 22.1 Proposal expiration worker — conditional

**Purpose:** find proposals whose approved expiration deadline has passed and invoke an owner command.

- **Owner:** Job Interview policy; shared scheduler executes.
- **Input:** cursor/batch over eligible interviews.
- **Idempotency key:** interview ID + expiration policy/deadline/version.
- **Retryable failures:** transient database/queue infrastructure.
- **Permanent/domain failures:** interview no longer in expirable state; treat as no-op/conflict, not retry storm.
- **Dead letter:** operational record if technical retries exhaust.
- **Truth updated:** only through normal interview expiration command/transition.
- **Telemetry:** counts, duration, conflicts, retry/dead-letter; no sensitive payloads.

Do not implement until expiration timing/policy is approved.

### 22.2 Interview integration retry/reconciliation worker

**Purpose:** retry owner-issued handoffs or reconcile local handoff receipts without direct provider access.

- **Input:** interview ID, integration type, source event/command ID, attempt state.
- **Idempotency:** source event/command + downstream operation.
- **Retryable:** downstream unavailable/timeout/explicit retryable result.
- **Permanent:** authorization revoked, unsupported operation, invalid destination contract, privacy/retention denial.
- **Dead letter:** create/associate `IntegrationFailure`/ops incident reference; retain truthful interview state.
- **Truth updated:** only approved local integration status/receipt fields, not downstream source records.

### 22.3 Privacy executor work

Job Interview does not schedule the privacy job. Privacy invokes the owner executor. Owner work must be idempotent and return partial/retryable/retained outcomes accurately.

### Queue rule

All jobs use `enqueueReliableJob` and `executeRetryWithBackoff`. Do not create a Module-local cron/queue framework.

## 23. Concurrency and Idempotency

### Races to prevent

- schedule versus cancel;
- complete versus cancel;
- no-show versus complete;
- reschedule versus cancel;
- simultaneous reschedules;
- participant duplicate invitation;
- participant response versus removal/revocation;
- parent application invalidation versus interview scheduling;
- duplicate domain-event handling;
- duplicate downstream room/thread/calendar/notification requests;
- privacy instruction versus active mutation where destructive.

### Aggregate/resource lock keys

- interview lifecycle: `job_interview:{interviewId}`;
- participant mutation: `job_interview_participant:{interviewId}:{userId}` after participant ownership approval;
- reschedule creation may also lock predecessor interview and any approved active-successor constraint.

### Database strategy

Use repository/root-approved implementations of:

- `withOptimisticConcurrency` for stale-edit detection;
- `acquireAggregateLock` or a transactionally equivalent Postgres lock for critical conflicting commands;
- conditional update on expected current status/version/`updatedAt`;
- existing composite participant primary key for duplicate prevention.

Never use process-local mutexes for distributed correctness.

### Reschedule uniqueness gap

Current schema does not enforce at most one successor. If U-CL06-15 approves that invariant, add a database-enforceable constraint/index or an equivalent serializable transaction design through an explicit schema decision. Do not rely only on application checks.

### Idempotency semantics

All externally initiated/retryable commands require `executeIdempotentCommand`.

The semantic fingerprint should include command type, actor, target/interview/application context, and material request fields. Same key + same fingerprint replays the original result. Same key + different fingerprint is a conflict.

### Replay result

Replay returns the original stable public result and must not append another `JobInterviewEvent`, publish another domain event, or reissue duplicate downstream work.

## 24. Media / Storage

Job Interview owns no `MediaAsset` and no file attachment join.

The only direct media-adjacent hiring use evidenced is interview-related resume review:

```text
Job Interview context
→ Candidate Application authorizeContextualResumeAccess(reason=interview_review)
→ Media validates existing ready/private asset and issues temporary grant/signed URL
→ Candidate Application records ResumeAccessLog according to approved semantics
→ Audit may record AccessAuditLog
```

Rules:

- no permanent resume URL in Job Interview;
- no resume file storage or signed URL generation here;
- no MIME/malware validation here;
- no `MediaAccessGrant` creation here;
- resume body/metadata is not copied into interview event metadata.

## 25. Search / Projection

Job Interview has no confirmed Search projection and no Typesense responsibility.

- interview list/detail/timeline are source-backed authorized queries;
- Job Interview does not create or mutate `SearchUpsertEvent` directly;
- Search must not reconstruct interview authority from indexed data;
- if a future protected interview-search projection is introduced, it requires architecture update and a source-owned privacy-shaped projection contract first.

## 26. Notification

### Business triggers

Subject to final product notification matrix, likely triggers include:

- interview proposed;
- interview scheduled;
- interview rescheduled;
- interview cancelled;
- participant invited/response;
- reminder;
- video/calendar integration problem requiring user action;
- interview completed/no-show only when user-facing notification is product-approved.

### Safe payload intent

Job Interview supplies:

- source interview ID;
- recipient group or safe user IDs;
- event/template key;
- safe schedule summary;
- location type;
- action route;
- sensitivity/priority;
- idempotency/correlation key.

It does not supply raw resume/application bodies, private notes, provider payloads, join tokens, or sensitive location text unnecessarily.

Notification owns channel routing, persistence, provider delivery, retries, delivery status, click/open proof, and user/device subscription state.

## 27. Audit and Sensitive Access

### Domain history

`JobInterviewEvent` is interview-domain truth. It records state changes and important interview-local actions.

### Generic audit

Use `appendAuditEvent` only where root/Cluster audit policy requires generic proof. Do not mirror every domain event automatically unless policy says so.

### Sensitive access

Use `recordSensitiveAccess` for restricted interview/admin access where required, especially:

- interview-related resume access path;
- sensitive support/admin interview views;
- video join/token issuance where Video/Audit policy requires it;
- protected location/reference access if classified sensitive.

### Separation

```text
JobInterviewEvent = what happened to interview lifecycle
AccessAuditLog    = who accessed/was denied protected data or credentials
AuditEvent         = generic important platform action proof
IntegrationFailure = technical degradation evidence
```

None replaces another.

## 28. Privacy and Retention

### Subject-data inventory

Job Interview may hold:

- interview IDs linked to candidate application/profile and organization;
- scheduling actor ID;
- participant User IDs and response timestamps if U-CL06-14 is accepted;
- interview schedule/timezones;
- `locationText`;
- `externalMeetingUrl` if retained under approved policy;
- calendar provider/event references and sync error text if U-CL06-16 approves local state;
- cancellation/no-show/completion timestamps;
- event actor IDs, reasons, and metadata.

### Privacy executor

Implement the Privacy-defined `enumerateSubjectData` and `executePrivacyInstruction` contracts for Job Interview-owned data only.

### Possible dispositions

Depending on approved retention policy:

- erase or anonymize optional location text;
- clear or anonymize external meeting/calendar references when no longer required;
- pseudonymize actor/participant references if relational/legal constraints permit;
- minimize event metadata/reasons while preserving required event proof;
- detach or mark source records per approved privacy restriction behavior;
- request linked provider/message/video deletion through their owners;
- retain required hiring/audit proof only when `evaluateRetentionRequirement` supplies the basis and Privacy records `DataRetentionExemption`.

### Retention blockers

The supplied evidence does not define final interview-record retention periods or employment-record legal basis. Destructive production execution is blocked until this is settled.

### Cascade deletion risk

Current Prisma relationships cascade from JobApplication/Organization/CandidateProfile to JobInterview and from JobInterview to events/participants/video relation. This may conflict with retention and append-only evidence. Do not rely on cascade deletion as privacy behavior. Resolve the retention model before destructive migrations/commands.

### Privacy target vocabulary gap

The supplied privacy target enum evidence does not clearly expose a dedicated `job_interview`/participant/event target. Do not silently overload an unrelated target type. Use the Privacy-defined versioned target protocol and update schema/architecture if a dedicated target is required.

## 29. Observability

### Structured logs

Every command/query/worker should carry request/correlation IDs. Safe dimensions may include:

- operation name;
- interview status before/after;
- location type;
- organization/interview IDs as approved identifiers;
- integration type;
- result category;
- retryability;
- attempt number;
- duration.

### Prohibited telemetry

Do not log:

- raw resume text;
- application answers/cover letters;
- meeting/join tokens;
- provider secrets or raw provider payloads;
- unnecessary exact location text;
- private message content;
- full sensitive event metadata.

### Ops records

Use `recordIntegrationFailure` for provider/worker/rail degradation. Use queue telemetry and incident correlation. Operational records never become interview status truth.

### Metrics

Useful module metrics, without inventing product targets:

- propose/schedule/cancel/complete/no-show command result counts;
- invalid-transition/conflict rate;
- downstream handoff lag/failure rate by integration type;
- participant response rate after participant feature exists;
- calendar/video synchronization degradation rate;
- proposal-expiration job lag if implemented;
- privacy-executor failure/retry count;
- authorization denial count without sensitive labels.

## 30. Security Boundaries

1. Runtime-validate every public command/query payload server-side using the root validation standard.
2. Never trust client-supplied organization/application/candidate/interview IDs as proof of relationship.
3. Resolve actor then authorize server-side before protected reads/writes.
4. Use database-backed concurrency and idempotency for every mutable/retryable path.
5. Keep external provider credentials/webhook secrets out of this Module.
6. Reject raw provider callbacks; only consume normalized internal results.
7. Do not store reusable video join tokens in `JobInterview`.
8. Treat `externalMeetingUrl` as sensitive until its permitted semantics are explicitly ruled.
9. Minimize `locationText` exposure and notifications.
10. Do not put resume/application bodies in events, logs, analytics, notifications, or provider metadata.
11. Sensitive admin/support reads require normal authority and any root-mandated access audit/step-up.
12. RLS is defense in depth and must match server Role / Authority semantics.
13. No direct cross-Module Prisma writes.
14. No frontend-only transition, authority, or dependency gating.
15. Provider outage must not trigger permissive bypass.

## 31. Error / Decision Result Pattern

Public interfaces return stable Module-level categories and safe reason codes. Provider-native error strings are never the public contract.

### Stable categories

- `validation_error`
- `unauthenticated`
- `forbidden`
- `not_found`
- `context_mismatch`
- `invalid_transition`
- `conflict`
- `stale_write`
- `dependency_denied`
- `dependency_unavailable`
- `integration_pending`
- `integration_failed`
- `unsupported_until_architecture_decision`
- `privacy_retained`
- `internal_error`

### Suggested interview reason-code namespace

These are interface-level codes, not provider codes:

- `INTERVIEW_APPLICATION_CONTEXT_MISMATCH`
- `INTERVIEW_INVALID_TIME_RANGE`
- `INTERVIEW_ACTION_NOT_AUTHORIZED`
- `INTERVIEW_STATUS_CONFLICT`
- `INTERVIEW_STALE_WRITE`
- `INTERVIEW_APPLICATION_NOT_INTERVIEWABLE`
- `INTERVIEW_PARTICIPANT_POLICY_UNRESOLVED`
- `INTERVIEW_RESCHEDULE_POLICY_UNRESOLVED`
- `INTERVIEW_CALENDAR_OWNER_UNRESOLVED`
- `INTERVIEW_DEPENDENCY_UNAVAILABLE`

Exact code spelling may be aligned to root error conventions, but stable semantics are required.

### Consumer rule

A consumer may branch on documented category/reason code. It must not parse provider messages, database error strings, or free-text event reasons to infer business policy.

## 32. Testing Architecture

### Domain unit tests

- context consistency across application/org/candidate facts;
- time-range validation;
- every approved transition and every illegal transition;
- terminal timestamp invariants;
- location-type policy;
- participant assignment/response after U-CL06-14;
- reschedule policy after U-CL06-15;
- application-change mapping policy;
- event payload minimization.

### State-transition tests

Matrix-test the approved `JobInterviewStatus` graph. No test should encode a transition that architecture has not approved.

### Public contract tests

- command runtime schemas;
- query DTO privacy shaping;
- owner-fact DTO consumed by Role / Authority;
- Candidate Application interviewability contract;
- resume-review delegation;
- Messaging/Notification/Video/Calendar normalized contracts;
- privacy executor envelope.

### Database/integration tests

- aggregate + event atomicity;
- participant composite uniqueness if enabled;
- indexes/query filters;
- cascade/retention behavior under approved policy;
- stale conditional update;
- lock behavior;
- idempotency replay creates one effect/event.

### Authorization tests

- cross-organization denial;
- candidate can only access linked interview;
- participant versus OrganizationMember scope;
- admin/support least privilege;
- RLS/server parity.

### Compliance/audit tests

- required `JobInterviewEvent` on mutation;
- required `AccessAuditLog` on configured sensitive paths;
- AuditEvent remains separate;
- no sensitive payload leakage.

### Idempotency/concurrency tests

- simultaneous schedule/cancel;
- complete/no-show race;
- duplicate proposal/schedule;
- participant duplicate invite/response race;
- concurrent reschedules once approved;
- duplicate inbound event;
- duplicate downstream handoff.

### Provider contract tests

Job Interview itself tests only the normalized owner contract/fixtures. Provider signature/dedupe/translation tests live with Video/Calendar owners. Integration tests prove Job Interview does not bypass them.

### Privacy tests

- complete subject-data enumeration;
- idempotent repeat execution;
- erase/anonymize/retain result correctness;
- retained result includes Privacy-owned exemption reference;
- provider/message/video deletion is delegated;
- no false completion after partial failure.

### E2E participation tests

At minimum:

```text
authorized recruiter
→ interviewable application
→ propose/schedule interview
→ candidate sees interview
→ interview domain event history exists
→ no JobApplication direct mutation
```

After later features:

```text
participant invite/response
→ reschedule
→ thread/notification
→ video room via Video owner
→ resume review via Candidate/Media
→ calendar via calendar owner
→ privacy executor / retention result
```

## 33. Module Invariants

### Rules coding agents must never violate

1. `JobInterview` is hiring interview truth; `Booking` is not.
2. Only Job Interview mutates `JobInterview.status`.
3. Job Interview never mutates `JobApplication.status` or `JobApplication.stage` directly.
4. `JobApplication`, `Organization`, and `CandidateProfile` IDs on an interview must describe one coherent hiring case.
5. `startsAt` must be strictly before `endsAt`.
6. Store absolute interview timestamps as database `DateTime`; timezone strings are context/display metadata, not alternative time truth.
7. Every successful interview lifecycle mutation appends `JobInterviewEvent` transactionally.
8. `JobInterviewEvent` does not replace `AuditEvent` or `AccessAuditLog`.
9. Generic audit/access records do not replace `JobInterviewEvent`.
10. Provider state does not replace `JobInterview` state.
11. Video Infrastructure owns `JobInterviewVideoRoom` and provider room/join mechanics.
12. Job Interview must not call Daily/Agora directly.
13. Job Interview must not create reusable public video/join URLs.
14. Calendar provider ownership/mechanics remain outside Job Interview; production sync waits for U-CL06-16.
15. Job Interview must not create `ProcessedInterviewCalendarEvent`.
16. Provider callbacks must be verified, deduped, and translated by the provider owner before Job Interview consumes them.
17. Participant ownership/removal/candidate invariant remains blocked until U-CL06-14 is approved.
18. Reschedule transition/cardinality remains blocked until U-CL06-15 is approved.
19. Participant row presence is not OrganizationMember authority.
20. OrganizationMember role is not interpreted locally.
21. Interview participation is not automatically Messaging Thread participation.
22. Resume review must go through Candidate Application authorization before Media grant/signing.
23. Job Interview owns no resume file or ResumeAccessLog.
24. Notification delivery belongs to Notification; interview events only request it.
25. Failed notification/thread/video/calendar handoff does not silently roll back truthful interview state.
26. Retryable commands use canonical idempotency.
27. Conflicting mutations use database-backed concurrency; no in-memory locks.
28. Duplicate command replay does not append a second event or issue duplicate downstream effects.
29. Domain events are post-commit facts, not disguised cross-Module commands.
30. Event/log/notification payloads must exclude raw resumes, application answers, tokens, secrets, and unnecessary location data.
31. ComplianceHold, if applicable, is consumed through its owner; no local block flag.
32. No Job Interview-specific Track entitlement exists unless architecture is updated.
33. Privacy / Data Erasure is the sole privacy workflow orchestrator.
34. Job Interview executes privacy instructions only against its own records.
35. Cascade deletion is not a substitute for legal erasure/retention policy.
36. Operational failures are recorded through Ops and never become arbitrary interview status changes.
37. Search is not used as interview truth or authority.
38. Direct cross-Module Prisma writes are prohibited.
39. Unavailable dependencies do not trigger permissive fallback.
40. Any code that requires resolving U-CL06-14, U-CL06-15, U-CL06-16, retention, or `externalMeetingUrl` semantics must stop and surface the blocker unless architecture has been updated.

## 34. Prohibited Duplicate Implementations

Do not generate inside `job_interview`:

- `auth.ts`, `getCurrentUser.ts`, `requireUser.ts`, or other feature-local authenticated-actor resolution;
- `jobInterviewPermissions.ts`, `canRecruiterManageInterview.ts`, or raw OrganizationRole authorization policy duplicating Role / Authority;
- cross-domain `organizationRepository`, `jobApplicationRepository`, or `candidateRepository` writes;
- `InterviewBooking`, Booking wrapper, Booking-backed interview lifecycle;
- `InterviewVideoRoom` duplicate, `jobInterviewDailyClient`, `agoraInterviewService`, local token signer;
- permanent `candidateJoinUrl`/`interviewerJoinUrl` stored as JobInterview truth;
- `cronofyInterviewService`, `nylasInterviewService`, `ProcessedInterviewCalendarEvent`, local webhook verifier/dedupe table;
- direct email/SMS/push provider client or notification retry worker;
- `InterviewThread`, `InterviewMessage`, or custom chat participant table;
- resume presigner, R2/S3 client, MediaAccessGrant writer, ResumeAccessLog writer;
- `InterviewAuditLog` or local generic AccessAuditLog/AuditEvent;
- local `PrivacyRequest`, `DataErasureJob`, retention-exemption table;
- custom queue/retry/dead-letter system;
- custom idempotency-key table if platform infrastructure already owns it;
- in-memory mutex/concurrency guard;
- universal lifecycle state machine/policy table;
- generic hiring readiness engine;
- local `isPremium`, `canInterview`, `isBlocked`, `calendarReady`, `videoReady` truth booleans;
- direct Typesense/SearchUpsertEvent code;
- generic provider-status translator spanning Video/Calendar;
- raw provider payload types in Job Interview domain contracts.

## 35. Unresolved Decisions

### U-JI-01 — Participant ownership/removal/candidate invariant

Derived from U-CL06-14.

Questions:

- Is Job Interview formally the owner of participant row and enums?
- Must every interview have exactly one candidate-role participant in addition to `candidateProfileId`?
- Can interviewers/coordinators/observers be non-OrganizationMembers?
- What does removal mean: delete, revoke state, cancellation, or separate record?
- How is historical participation preserved?

**Blocks:** participant mutation and downstream participant revocation behavior.

### U-JI-02 — Interview transition and reschedule semantics

Derived from U-CL06-15.

Questions:

- Complete legal transition matrix?
- May draft schedule directly?
- Are terminal states reopenable?
- Does reschedule mutate or create successor?
- Max successor cardinality?
- How are downstream resources transferred/revoked?

**Blocks:** advanced transitions/rescheduling and any DB constraint based on active-successor semantics.

### U-JI-03 — Calendar capability ownership for hiring

Derived from U-CL06-16.

Question: Does Booking & Calendar intentionally expose a general calendar provider port to Job Interview, or should calendar integration be separated into a broader shared capability?

**Blocks:** production calendar sync. Does not block provider-independent interview truth.

### U-JI-04 — `externalMeetingUrl` semantics

Determine whether this field is:

- organizer-supplied external meeting reference only;
- a sensitive temporary link;
- legacy/temporary schema to deprecate;
- permitted for non-Workin-Ants video providers.

It must not become a permanent provider credential bypassing Video Infrastructure.

### U-JI-05 — Interview/application synchronization

Define exact effect on interviews when application is withdrawn, rejected, hired, or closed; define whether interview scheduling requests Candidate Application stage advancement or leaves stage fully manual.

### U-JI-06 — Interview retention and cascade deletion

Define retention periods/legal basis, permitted anonymization, event retention, participant retention, and whether cascade delete must be changed.

### U-JI-07 — Privacy target vocabulary

Confirm canonical Privacy target identifiers for interview, participant, and event data rather than overloading unrelated target types.

### U-JI-08 — Concurrency token

Current schema has `updatedAt` but no explicit version. Confirm root strategy for `withOptimisticConcurrency` on JobInterview and public contract token.

### U-JI-09 — Event name registry

Confirm canonical `JobInterviewEvent.name` values/schema version so internal domain history and published domain events cannot drift into stringly typed aliases.

### U-JI-10 — Proposal expiration policy

Define whether proposals expire automatically, after what deadline, and whether `no_response` is a participant deadline projection or manual state.

### U-JI-11 — Sensitive location/phone meeting data

Define treatment of `locationText` and phone/in-person details, including notification redaction and whether Location Safety applies to hiring interviews.

### U-JI-12 — Prisma schema validation blocker

Resolve CL-06 U-CL06-17 before migration generation if the current root schema fails validation due out-of-model relation lines.

## 36. Architecture Decision Summary

### Binding rulings

1. `job_interview` is a `domain_capability_hybrid` in CL-06.
2. Job Interview owns `JobInterview`, `JobInterviewStatus`, `JobInterviewLocationType`, `JobInterviewEvent`, and `JobInterviewEventActor`.
3. `JobInterview` is formal hiring interview truth and is not Booking.
4. Candidate Application owns `JobApplication` status/stage and resume business privacy.
5. Organization Hiring owns Organization/Job/member-row truth; Role / Authority interprets permission.
6. Video Infrastructure owns `JobInterviewVideoRoom` and provider room/join mechanics.
7. Messaging owns Thread/Message truth; Notification owns delivery truth.
8. Audit owns generic `AuditEvent`/`AccessAuditLog`; Job Interview owns its domain ledger.
9. Privacy owns privacy-request/job orchestration; Job Interview executes only against owned data.
10. Provider callbacks and provider status are normalized by provider owners before Job Interview consumes them.
11. Shared operations are consumed; they are not reimplemented locally.
12. Every successful interview lifecycle mutation is authorized, concurrency-safe, idempotent when retryable, and transactionally recorded in `JobInterviewEvent`.
13. Cross-Module writes use public commands/events; direct neighboring Prisma writes are prohibited.

### Proposed rulings requiring explicit acceptance

1. Job Interview owns `JobInterviewParticipant` and participant enums.
2. Rescheduling should use a history-preserving successor model with one effective active successor per predecessor.
3. Stable interview domain event names should use the `interview.*` registry listed in Section 12.

### Unresolved blockers

Participant removal/candidate invariant, exact lifecycle matrix/reschedule semantics, calendar capability ownership, meeting-URL semantics, application/interview synchronization, retention/cascade behavior, privacy target IDs, concurrency token strategy, event-name finalization, proposal expiry, and hiring-location privacy remain unresolved until architecture decisions settle them.

## 37. Coding-Agent Usage

Before implementing or modifying Job Interview, an agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md` if present;
3. root `code-standards.md` if present;
4. Canonical Shared Operations Registry/Architecture;
5. CL-06 `architecture.md`;
6. CL-06 `build-plan.md`;
7. this `job_interview/module-architecture.md`;
8. this `job_interview/implementation-plan.md`;
9. relevant public-interface sections for Identity, Role / Authority, Organization Hiring, Candidate Application & Resume Privacy, Messaging, Notification, Video Infrastructure, Calendar owner, Audit, Privacy, Holds, and Ops;
10. current Prisma schema and migrations;
11. progress tracker / current branch handoff;
12. architecture decisions resolving any U-JI/U-CL06 blocker relevant to the feature.

Before writing code, the agent must confirm:

- the Cluster feature it supports is currently permitted by the Cluster sequence;
- the prior Module feature exit gate passed;
- no unresolved decision is being silently decided by code;
- shared operations already exist or are supplied as versioned fixtures/contracts rather than rebuilt locally;
- any schema change is an approved owner change, invariant, or persistence need rather than convenience duplication.

