# Organization Hiring Module Implementation Plan

> **Module ID:** `organization_hiring`  
> **Module:** Organization Hiring Module  
> **Primary Cluster:** `CL-06 Organization Hiring & Candidate Pipeline`  
> **Authority:** `organization_hiring/module-architecture.md`  
> **Parent sequencing:** subordinate to CL-06 `build-plan.md`  
> **Purpose:** ordered implementation work inside Organization Hiring only

## Core Principle

Implement Organization Hiring through narrow, verifiable slices:

```text
observable behavior
→ validated command/query
→ Organization Hiring-owned policy
→ authoritative Organization/Member/Job write or read
→ canonical shared-operation calls
→ transactional event/outbox
→ downstream owner request
→ tests
→ exit gate
```

The Module does not implement Candidate Application, Job Compliance, Job Interview, Search, Media, Notification, Messaging, Trust, Hold, Audit, Privacy, or provider lifecycles. It integrates through public contracts.

## Build Rules

1. Follow root architecture/code standards, CL-06 architecture/build plan, and this Module architecture.
2. This Module owns only Organization, OrganizationMember row/role assignment, Organization notification preference facts, Job lifecycle, and approved contextual attachment meaning.
3. Consume neighboring Modules through approved public interfaces/events.
4. Reuse Canonical Shared Operations; do not create local copies.
5. Every mutation uses runtime validation, actor resolution, server-side authorization, and owner invariants.
6. Lifecycle transitions are transaction-safe and concurrency-aware.
7. Cross-Module reads use owner-specific DTOs; direct cross-domain Prisma reads are prohibited by default.
8. External effects are idempotent and occur after source truth is committed.
9. Providers remain behind their canonical owner adapters.
10. Durable async work uses the shared queue/retry/dead-letter infrastructure.
11. Domain denial, compliance decision, dependency failure, and operational failure remain distinct.
12. Search remains projection; Search outage never rewrites truthful source state.
13. Privacy owns privacy-request orchestration.
14. ComplianceHold is the reusable stop sign.
15. Organization ATS commercial access remains unresolved; do not invent a local premium system.
16. Organization verified activation remains unresolved; do not invent `isVerifiedOrganization`.
17. Ownership transfer remains unavailable until `U-CL06-03`.
18. Production Job publication cannot pass until `U-CL06-05/06/07` are resolved.
19. Resolve `U-CL06-17` before migrations touching the affected schema region.
20. Every feature ends with tests and a hard exit gate.
21. A failed exit gate blocks the next sequential Module feature unless architecture/plan is explicitly revised.

## Preconditions

### Hard platform dependencies

Must exist before Feature 01 implementation:

- Prisma/Postgres migration foundation;
- runtime validation standard;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- RLS policy/testing support;
- `executeIdempotentCommand`;
- optimistic concurrency/aggregate locking primitives;
- transactional outbox/event envelope;
- reliable queue client/worker shell;
- structured logging/request/correlation IDs;
- Audit API fixture or implementation.

### Hard cross-Module contracts by feature

- Taxonomy validation contract before Job classification writes.
- Job Compliance public interface before production publication.
- Trust requirement/readiness interface before verified-only publication composition.
- Search refresh interface before public Job handoff.
- Media attachment/readiness interface before organization/job media attachment.
- Notification interface before delivery effects.
- Privacy target protocol before privacy executor completion.

### Interfaces that may initially be contract-stubbed

The following may use strict contract fixtures during early Module features if the real owner Module is not yet implemented:

- Job Compliance;
- Trust Verification;
- Search;
- Media;
- Notification;
- Messaging;
- Audit;
- Holds;
- Privacy.

Fixtures must mimic the approved public contract, not fabricate owner decisions.

### Architecture blockers

- `U-CL06-01/02`: blocks verified Organization activation.
- `U-CL06-03`: blocks ownership transfer.
- `U-CL06-04`: blocks monetized Organization ATS access.
- `U-CL06-05/06/07`: blocks production Job publication.
- `U-CL06-08`: blocks final classification join persistence placement.
- `U-CL06-09`: blocks production use of `Organization.logoUrl` as file truth.
- `U-CL06-17`: blocks affected migrations.

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Organization Hiring Contracts, Schema Verification, and Persistence Boundary

### Objective

Establish a compilable, tested Organization Hiring boundary with validated Module contracts, owner repositories, and verified Organization/Member/Job schema assumptions without implementing public hiring behavior beyond safe reads.

### Observable Result

- The Module can load `Organization`, OrganizationMember, and Job through its own repositories.
- Neighboring Modules can depend on typed public contract definitions instead of Prisma models.
- The Prisma structural defect is either corrected or documented as blocking before affected migration work.
- No cross-domain repository exists.

### Cluster Build-Plan Link

Supports CL-06 Phase 1 / Feature 01, **Organization Membership and Job Draft Workspace**.

### Dependencies

- root architecture/code standards;
- CL-06 architecture/build plan;
- current Prisma schema;
- runtime validation library;
- shared result/error conventions.

### In Scope

- create Module folder structure;
- define public command/query DTOs and errors;
- define `OrganizationHiringContext`;
- define source-version strategy using current `updatedAt` or approved explicit version;
- implement Organization, OrganizationMember, Job and OrganizationNotificationSetting repositories;
- verify indexes/constraints;
- verify `U-CL06-17`;
- add source projection DTO types without Search execution;
- define dependency ports for Identity, Authority, Taxonomy, Job Compliance, Trust, Media, Search, Notification, Messaging, Audit, Holds, Privacy, Ops.

### Out of Scope

- Organization creation UI;
- membership mutation;
- Job publication;
- Organization verification;
- ownership transfer;
- OrganizationFeatureAccess writes;
- Search indexing;
- provider code;
- Candidate/Interview repositories.

### Module-Owned Data

- `Organization`;
- `OrganizationMember`;
- `Job`;
- `OrganizationNotificationSetting`;
- contextual media/classification interfaces only.

### Public Interfaces

Introduce types/signatures for:

- `getOrganization`;
- `listOrganizationsForActor`;
- `listOrganizationMembers`;
- `getOrganizationHiringContext`;
- `getJob`;
- `listOrganizationJobs`;
- `getJobApplicationEligibilityContext`;
- source projection builders;
- command DTOs used by later features;
- privacy executor contract.

### Shared Operations Used

- `queryOwnerFacts` — contract pattern; Organization Hiring supplies its own facts.
- `withOptimisticConcurrency` — shared persistence primitive; local conflict rules.
- `returnDecisionResult` — only for dependency decision port typing where applicable.

**Prohibited duplicates:** generic target repository, local generic decision engine, independent concurrency helper.

### Domain Logic

No lifecycle changes yet. Define and unit-test pure policy signatures for:

- Organization transition validation;
- membership mutation validation;
- Job transition validation;
- Job edit materiality;
- compliance-decision mapping placeholder that fails closed until `U-CL06-05/06/07`.

### Authorization / Compliance

No permission logic is embedded. Repositories accept no assumption that caller is authorized. Authorization belongs to application services.

### Database / Transaction Behavior

- confirm Organization.slug uniqueness;
- confirm OrganizationMember composite PK;
- confirm notification-setting unique key;
- record which mutations will require transactions;
- do not create migrations for unresolved ownership models;
- fix/verify schema structural defects before migration generation.

### Events / Jobs

Define event envelope payload types only. No worker.

### Provider Integration

None.

### UI / Admin Surface

None required.

### Failure Behavior

- schema mismatch blocks feature;
- repository not-found is normalized;
- stale-version contract exists but no mutation uses it yet;
- unresolved schema placement is documented, not guessed.

### Tests

- repository mapping integration tests;
- public DTO serialization tests;
- no Prisma model leakage in public contracts;
- schema constraint assertions;
- compile/typecheck;
- lint/format.

### Documentation Updates

Update this architecture only if schema verification changes a binding ownership/model ruling. Record `U-CL06-17` resolution when settled.

### Acceptance Criteria

- Module compiles with strict public/private boundaries.
- Direct dependency contracts are typed.
- No neighboring repository import exists.
- Schema defects are resolved or feature is blocked.
- Public contracts do not expose provider payloads or Prisma implementation types.

### Exit Gate

PASS only if typecheck/lint/tests pass, repository boundaries are enforced, `U-CL06-17` is resolved for touched models, and no unresolved ownership decision has been encoded as schema truth.

## 02 Draft Organization Creation and Membership Management

### Objective

An authenticated authorized actor can create a draft Organization and manage current membership rows safely, without implementing ownership transfer or verified activation.

### Observable Result

- A User can create a draft Organization through the public command.
- Initial membership facts are persisted atomically.
- Authorized owner/admin behavior can add, change, list, and remove permitted members.
- Unauthorized and cross-organization mutations fail with no writes.

### Cluster Build-Plan Link

Directly implements the Organization/membership portion of CL-06 Feature 01.

### Dependencies

- Feature 01;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `executeIdempotentCommand`;
- `withOptimisticConcurrency`;
- `acquireAggregateLock` where required;
- `publishDomainEvent`;
- `appendAuditEvent`;
- User existence/actor contract.

### In Scope

- `createOrganization`;
- `getOrganization`;
- `listOrganizationsForActor`;
- `addOrganizationMember`;
- `changeOrganizationMemberRole`;
- `removeOrganizationMember`;
- `listOrganizationMembers`;
- minimum Organization profile update;
- Organization/member UI;
- RLS policies/parity tests for these actions;
- membership events and audit effects.

### Out of Scope

- `transferOrganizationOwnership`;
- Organization activation based on verification;
- OrganizationFeatureAccess;
- applicant tracker;
- resume access;
- Job publication.

### Module-Owned Data

- Organization;
- OrganizationMember;
- OrganizationStatus remains `draft` for newly created Organizations unless an already-approved non-verification transition is available.

### Public Interfaces

Implement:

- `createOrganization`;
- `getOrganization`;
- `listOrganizationsForActor`;
- `updateOrganizationProfile`;
- `addOrganizationMember`;
- `changeOrganizationMemberRole`;
- `removeOrganizationMember`;
- `listOrganizationMembers`;
- `getOrganizationHiringContext`.

### Shared Operations Used

**`resolveAuthenticatedActor` — Identity & Access**  
Invocation: every protected command/query.  
Local policy: which Organization action is requested.  
Prohibited: `current-user.ts`.

**`authorizeResourceAction` — Role / Authority**  
Invocation: profile/member mutation and protected reads.  
Local policy: membership facts and action vocabulary.  
Prohibited: `org-permissions.ts`, role string checks in components.

**`executeIdempotentCommand` — platform**  
Invocation: create Organization, add member.  
Local policy: command fingerprint and replay semantics.  
Prohibited: ad-hoc idempotency table.

**`withOptimisticConcurrency` / `acquireAggregateLock` — platform persistence**  
Invocation: role/removal operations affecting owner invariant.  
Local policy: Organization membership aggregate key.  
Prohibited: in-memory lock.

**`publishDomainEvent` — outbox**  
Invocation: same source transaction.  
Local policy: event names/payloads.

**`appendAuditEvent` — Audit**  
Invocation: policy-designated role/removal changes.  
Local policy: auditable action type.

### Domain Logic

- New Organization is `draft`.
- Slug must be unique.
- One membership row per User per Organization.
- OrganizationMember role assignment is source truth; Role / Authority interprets permission.
- Member removal cannot violate the currently approved owner invariant.
- Because `U-CL06-03` is unresolved, ownership transfer is not exposed.
- Do not add invitation/status semantics absent from schema.

### Authorization / Compliance

- Server-side Role / Authority decision before every mutation.
- RLS must deny cross-org access consistently.
- No local verification gate.
- Holds may be consulted for destructive/admin-sensitive transitions if root policy requires, but no local hold state is created.

### Database / Transaction Behavior

**Organization create transaction:**

1. claim idempotency key;
2. insert Organization;
3. insert architecture-approved initial membership facts;
4. write outbox event;
5. commit;
6. request audit/notification after commit as appropriate.

Membership mutation uses compare-and-set/lock if owner invariant spans Organization + membership rows.

### Events / Jobs

Emit:

- `organization.created`;
- `organization.updated`;
- `organization.membership_added`;
- `organization.membership_role_changed`;
- `organization.membership_removed`.

No worker.

### Provider Integration

None.

### UI / Admin Surface

- Organization create/profile screen;
- member list;
- add member by resolved User/contact flow only through approved identity/contact interface;
- role change;
- remove action;
- clear draft status indicator.

Do not expose ownership transfer.

### Failure Behavior

- duplicate slug → deterministic conflict;
- duplicate member → deterministic conflict;
- unauthorized → no writes;
- stale membership/owner aggregate → conflict;
- Audit/Notification downstream failure does not roll back committed source truth unless root transactional policy explicitly requires synchronous proof.

### Tests

- Organization creation;
- idempotent replay;
- slug collision;
- owner/admin/recruiter authorization matrix;
- duplicate member;
- role change;
- owner-protection cases;
- concurrent membership mutations;
- RLS parity;
- event/outbox atomicity;
- UI component and Playwright draft Organization flow.

### Documentation Updates

If `U-CL06-03` is settled during implementation, update architecture before adding ownership transfer.

### Acceptance Criteria

- Draft Organization + membership workflows operate end-to-end.
- No local permission interpreter exists.
- Membership uniqueness is DB-enforced.
- Unauthorized/RLS paths produce no writes.
- Owner-sensitive mutations cannot create an invalid state.

### Exit Gate

PASS only if all unit/integration/RLS/concurrency/UI checks pass, ownership transfer remains absent, and no verified-activation or ATS commercial access shortcut exists.

## 03 Job Draft Lifecycle, Classification, and Private Workspace

### Objective

Authorized Organization members can create, list, view, and edit private Job drafts with validated taxonomy and concurrency protection, but cannot publish them.

### Observable Result

An authorized Organization member can manage Job drafts inside one Organization; draft Jobs never become publicly searchable.

### Cluster Build-Plan Link

Completes the Job-draft portion of CL-06 Feature 01.

### Dependencies

- Features 01–02;
- Taxonomy `validateTaxonomyAssignment`;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- idempotency/concurrency;
- Organization owner-facts interface.

### In Scope

- `createJobDraft`;
- `getJob`;
- `listOrganizationJobs`;
- `updateJobDraft`;
- Job draft UI;
- domain/category assignment;
- contextual Job tags only according to `U-CL06-08` placement;
- job application eligibility context query skeleton;
- Job events;
- no Search refresh.

### Out of Scope

- public Job publication;
- Job Compliance evaluation;
- verified-only readiness;
- Candidate applications;
- applicant tracker;
- JobInterview;
- OrganizationFeatureAccess.

### Module-Owned Data

- Job;
- JobStatus=`draft`;
- JobVisibility intent stored but not sufficient for public visibility;
- EmploymentType;
- compensation business fields subject to `U-CL06-07`;
- Job taxonomy references/context.

### Public Interfaces

Implement:

- `createJobDraft`;
- `getJob`;
- `listOrganizationJobs`;
- `updateJobDraft`;
- `getJobApplicationEligibilityContext`;
- `buildJobSourceProjection` in non-public/test form.

### Shared Operations Used

- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `validateTaxonomyAssignment`;
- `resolveTaxonomyRequirements` for non-owning trigger discovery;
- `executeIdempotentCommand`;
- `withOptimisticConcurrency`;
- `publishDomainEvent`.

**Prohibited:** local taxonomy tables/cleaners, direct Trust decision logic.

### Domain Logic

- create only under existing Organization.
- `draft` is initial status.
- `visibility=public` does not make a draft public.
- Job source version changes on mutation.
- compensation ranges validate numeric/order/currency shape, but legal disclosure semantics remain Job Compliance.
- `EmploymentType.contract` may be stored only according to current schema; production compliance semantics remain blocked by `U-CL06-07`.
- materiality classifier records which future edits require re-review; no publication effect yet.

### Authorization / Compliance

- Organization ownership/role context passes Role / Authority.
- Taxonomy validates canonical IDs/hierarchy.
- No Job Compliance decision is simulated.
- No Trust readiness is inferred.

### Database / Transaction Behavior

- transaction for Job create + outbox;
- compare-and-set for edit;
- indexes on organization/status/visibility and taxonomy are used;
- classification join persistence follows `U-CL06-08`; if unresolved, implement only fields whose ownership is already clear and contract-stub join mutation.

### Events / Jobs

- `job.created`;
- `job.updated`.

No background job.

### Provider Integration

None.

### UI / Admin Surface

- Job list;
- create/edit;
- detail;
- draft badge/non-public message;
- validation feedback.

### Failure Behavior

- cross-org job ID → not found/unauthorized according to root leakage policy;
- stale edit → conflict;
- invalid taxonomy → normalized validation error;
- taxonomy dependency unavailable → explicit dependency error, not arbitrary term acceptance.

### Tests

- CRUD integration;
- role/organization isolation;
- taxonomy contract;
- draft cannot become Search-visible;
- stale edit;
- compensation input validation;
- event/outbox;
- Playwright draft Job flow.

### Documentation Updates

Record `U-CL06-08` or `U-CL06-07` resolution if settled; architecture first.

### Acceptance Criteria

- Jobs remain private/non-public.
- No direct Typesense call exists.
- No compliance scanner exists.
- Cross-org access is denied.
- Taxonomy is consumed through public interface.

### Exit Gate

PASS only if Job draft flow is complete, no Job can enter `open`, no Search refresh is requested from a draft-only path, and all tests/typecheck/lint pass.

# Phase 2 — Organization Presentation and Owner-Side Support Facts

## 04 Organization/Job Media Attachments and Notification Preferences

### Objective

Allow authorized organizations to attach only Media-approved presentation assets and manage organization-owned notification routing preferences without owning Media or Notification delivery.

### Observable Result

- Organization logo/job graphic attachment works only for ready valid assets.
- Organization notification settings can be managed and returned to Notification recipient-resolution flow.
- No raw object-storage or delivery code exists in this Module.

### Cluster Build-Plan Link

Supports CL-06 Feature 01 presentation/organization-management details and prepares Feature 03 effects.

### Dependencies

- Feature 02–03;
- Media public interfaces;
- Notification contract;
- `U-CL06-09` resolution before relying on logoUrl;
- `U-CL06-08` if contextual join placement touches classification/media persistence.

### In Scope

- `attachOrganizationMedia`, detach;
- `attachJobMedia`, detach;
- `updateOrganizationNotificationSetting`;
- `getOrganizationNotificationSettings`;
- local recipient-group facts resolver;
- Organization/job presentation UI using processed derivatives.

### Out of Scope

- upload session internals;
- MIME sniffing;
- malware scan;
- EXIF processing;
- object storage;
- signed URLs;
- Notification/Delivery records;
- email/SMS/push dispatch.

### Module-Owned Data

- OrganizationMedia contextual relation;
- JobMedia contextual relation under approved ruling;
- OrganizationNotificationSetting.

### Public Interfaces

- attachment commands;
- notification setting commands/queries;
- `resolveOrganizationNotificationRecipientFacts`.

### Shared Operations Used

**`attachValidatedMedia` — contextual owner + Media**  
Invocation: after Media readiness.  
Local policy: organization_logo/job_graphic context and business role.  
Prohibited: direct MediaAsset status mutation, storage client.

**`validateUploadedFile`, `scanFileForMalware` — Media**  
Organization Hiring never calls implementation helpers directly; it consumes Media's final readiness/attachment contract.

**`resolveNotificationRecipients` — source owner + Notification contract**  
Invocation: when an Organization business event requests delivery.  
Local policy: `notifyOwners/admins/recruiters`.  
Prohibited: channel fan-out/provider dispatch.

### Domain Logic

- only valid upload contexts are accepted;
- attachment requires ready/processed asset;
- public display uses scrubbed derivative;
- direct `logoUrl` is not treated as independent file truth;
- notification settings are unique by organization/name/channel;
- disabled setting returns no recipients for that intent/channel.

### Authorization / Compliance

- media/settings mutations require org authority.
- no resume/sensitive file access here.

### Database / Transaction Behavior

- contextual join unique composite keys;
- notification setting upsert under unique key;
- source change + outbox if public projection needs refresh.

### Events / Jobs

Possible events:

- `organization.media_changed`;
- `job.media_changed`;
- `organization.notification_setting_changed`.

Search refresh requests happen only when public source state exists.

### Provider Integration

None.

### UI / Admin Surface

- processed Organization logo picker/upload control via Media-owned UI contract;
- Job graphic control;
- notification settings.

### Failure Behavior

- asset not ready/incorrect context → deterministic denial;
- Media unavailable → no join;
- Notification unavailable does not prevent preference write.

### Tests

- wrong context/asset readiness denial;
- processed derivative only;
- join uniqueness;
- setting uniqueness;
- role authorization;
- no storage client dependency;
- projection refresh triggered only when appropriate.

### Documentation Updates

Update architecture if `logoUrl` disposition or contextual join ownership is finalized.

### Acceptance Criteria

No raw upload/storage implementation exists; only ready assets attach; preference facts are source-owned and delivery remains Notification-owned.

### Exit Gate

PASS only if Media/Notification contract tests pass, no duplicate file/delivery helper exists, and public display never depends on unprocessed/raw assets.

# Phase 3 — Controlled Job Publication and Public Projection Handoff

## 05 Job Publication Review Orchestration

### Objective

Implement the owner-side publication workflow that moves a Job into compliance review, binds the exact source version, consumes authoritative Job Compliance/Trust/Hold decisions, and applies only Organization Hiring-owned lifecycle transitions.

### Observable Result

An authorized Organization can request publication and observe pending/review/remediation state. A Job cannot become `open` unless every approved gate passes for the exact source version.

### Cluster Build-Plan Link

Organization Hiring portion of CL-06 Feature 03, **Controlled Job Publication and Search Handoff**.

### Dependencies

- Features 01–04;
- CL-06 Job Compliance Feature 02/public interface;
- Job Compliance `evaluateJobCompliance`;
- Trust `resolveVerificationRequirements` + `evaluateVerificationReadiness`;
- Holds `evaluateComplianceHold`;
- `returnDecisionResult`;
- idempotency/concurrency/outbox;
- **hard blocker:** `U-CL06-05`, `U-CL06-06`, `U-CL06-07` resolved before production allow/open mapping.

### In Scope

- `requestJobPublication`;
- source-version-bound publication receipt;
- pending-compliance transition;
- `applyJobComplianceDecision`;
- local mapping from authoritative decisions to JobStatus;
- material-edit invalidation;
- review/remediation UI state;
- retry-safe compliance request orchestration.

### Out of Scope

- Job Compliance rules/scanners/findings;
- Trust verification records;
- ComplianceHold records;
- Search execution;
- applicant submission;
- Organization verification activation;
- OrganizationFeatureAccess.

### Module-Owned Data

- Job.status;
- Job.visibility;
- Job.complianceStatus only under approved mirror semantics;
- source version/evidence references if schema ruling adds them;
- outbox event.

### Public Interfaces

Implement/complete:

- `requestJobPublication`;
- internal `applyJobComplianceDecision`;
- publication-status query fields in `getJob`;
- source snapshot/query consumed by Job Compliance.

### Shared Operations Used

**`evaluateJobCompliance` — Job Compliance**  
Invocation: after Job is committed to pending review.  
Local policy: mapping result to Job lifecycle.  
Prohibited: scanner/rule engine.

**`resolveVerificationRequirements` / `evaluateVerificationReadiness` — Trust**  
Invocation: publication composition where applicable.  
Local policy: how requirement affects Job publication.  
Prohibited: reading TrustBadge/provider status.

**`evaluateComplianceHold` — Holds**  
Invocation: before opening/publication-sensitive transition.  
Local policy: transition effect.  
Prohibited: local blocked flag.

**`returnDecisionResult` — shared contract**  
Local policy: reason mapping.

**`executeIdempotentCommand`, `withOptimisticConcurrency`, `publishDomainEvent`**  
Protect workflow.

### Domain Logic

- Publication request requires exact expected Job version.
- Job enters `pending_compliance_review` before evaluation.
- Decision for stale source version cannot open Job.
- Job Compliance warning/block/review/failure mappings follow approved `U-CL06-05`.
- Technical `failed` result cannot approve/reject legally.
- Hold/verification approval cannot substitute Job Compliance.
- Material edit after approval invalidates publication according to approved materiality policy.
- `visibility=public` is necessary but not sufficient for public Search.
- Production `open` transition is disabled until blockers are resolved.

### Authorization / Compliance

- organization actor authorized by Role / Authority;
- no client-provided compliance status accepted;
- administrative overrides, if later approved, require audit and Job Compliance owner interface.

### Database / Transaction Behavior

**Request transaction:**

1. authorize and validate expected version;
2. transition Job to pending review;
3. persist source-version binding/workflow receipt;
4. write outbox event;
5. commit.

**Decision application transaction:**

1. dedupe decision event/request;
2. load Job current version;
3. reject stale decision;
4. apply valid local transition;
5. write outbox event;
6. commit.

### Events / Jobs

Emit:

- `job.publication_requested`;
- `job.status_changed`;
- `job.published` only when truly open;
- `job.updated`/review invalidation event as needed.

Use reliable job/retry for compliance request technical failures. Domain denial is not retried as infrastructure failure.

### Provider Integration

None.

### UI / Admin Surface

- publish action;
- pending compliance state;
- warning/remediation/review state;
- Job Compliance report link/embedded owner-provided view;
- resubmit after allowed changes.

### Failure Behavior

- compliance dependency unavailable → Job remains non-public/pending/retriable;
- stale decision → ignore/mark superseded and reevaluate;
- Trust unavailable on required gate → cannot open;
- active hold → cannot open;
- invalid lifecycle → domain error.

### Tests

- draft→pending;
- exact source version binding;
- pass/warn/block/review/failed mapping;
- stale decision;
- publish/edit race;
- active hold;
- verification requirement;
- idempotent replay;
- Job Compliance cannot mutate Job directly;
- no direct scanner implementation.

### Documentation Updates

Record final decisions for `U-CL06-05/06/07` before production path is enabled.

### Acceptance Criteria

- No Job opens from client status mutation.
- No stale compliance decision opens a Job.
- Technical failure cannot approve.
- Organization Hiring owns transition; Job Compliance owns decision.
- Unresolved blockers fail closed.

### Exit Gate

PASS only after `U-CL06-05/06/07` are resolved and encoded in architecture, all decision/transition tests pass, and production publication remains impossible under any missing/unknown gate.

## 06 Search, Notification, Event, and Deadline Effects

### Objective

After authoritative Job/Organization source changes, reliably request Search/Notification effects and close eligible Jobs at approved deadlines without moving downstream ownership into this Module.

### Observable Result

- A truly public-ready Job requests Search indexing.
- Non-public or closed/paused/archived Job changes request Search removal/update.
- Notification requests are generated from committed business facts.
- Search/Notification outages are visible/retriable without corrupting source truth.
- Deadline closure is idempotent if close policy is approved.

### Cluster Build-Plan Link

Completes Organization Hiring responsibilities in CL-06 Feature 03.

### Dependencies

- Feature 05;
- Search `requestSearchProjectionRefresh`;
- `buildSourceProjection`;
- Notification `requestNotification`;
- queue/retry infrastructure;
- `runDeadlineExpiration`;
- Ops telemetry.

### In Scope

- `buildOrganizationSourceProjection`;
- `buildJobSourceProjection`;
- Search refresh/remove request handlers;
- event consumers for relevant Hold/Trust/compliance readiness revocation only through approved contracts;
- notification request handlers;
- close-expired-Jobs worker after close policy is approved;
- retry/dead-letter behavior for downstream requests.

### Out of Scope

- SearchUpsertEvent persistence;
- Typesense;
- Search ranking;
- notification provider/channel retry;
- Compliance/Trust/Hold source mutations.

### Module-Owned Data

- source projection DTOs, not Search records;
- Job.status changes from close worker;
- outbox events.

### Public Interfaces

- source projection queries/builders;
- owner event handlers;
- close-worker command.

### Shared Operations Used

**`requestSearchProjectionRefresh` — Search**  
Invocation: after source commit.  
Local policy: whether source state requests index/update/remove.  
Prohibited: Typesense client/SearchUpsertEvent write.

**`buildSourceProjection` — shared mechanism/source owner**  
Local policy: allowlisted fields.

**`requestNotification` — Notification**  
Invocation: after owner fact committed.  
Local policy: business trigger/template variables.

**`resolveNotificationRecipients` — source owner + Notification**  
Local policy: Organization setting/member group.

**`enqueueReliableJob`, `executeRetryWithBackoff`, `runDeadlineExpiration` — platform**  
Local policy: Job close eligibility and downstream retry classification.

### Domain Logic

- Search request follows, never precedes, truthful source commit.
- Search failure does not change Job from `open` to another status.
- Search refresh carries source version so stale requests can be ignored/reconciled.
- Notification failure does not rewrite Job/Organization state.
- close worker rechecks Job current status/version/deadline before mutation.
- Hold/Trust revocation handling changes local public eligibility only through approved owner policy, then requests Search removal.

### Authorization / Compliance

Worker/system actor context is authenticated as platform/system actor and still uses owner policy.

### Database / Transaction Behavior

- source state + outbox atomic;
- downstream request after commit;
- close worker uses compare-and-set/lock;
- no direct downstream DB transaction.

### Events / Jobs

- Search refresh retry jobs;
- Notification retry is Notification-owned after accepted request; only request transport retry remains source-side if needed;
- close-expired-Jobs scheduled work;
- exhausted request transport retries create Ops failure record.

### Provider Integration

None.

### UI / Admin Surface

- public Job status/indexing state may show source state and downstream-sync diagnostic separately;
- do not present Search sync as Job truth.

### Failure Behavior

- Search down → retry/DLQ/ops; Job remains truthful.
- stale Search request → downstream owner drops/reconciles.
- deadline worker stale → no-op/conflict.
- notification unavailable → operational error/retry.

### Tests

- no indexing before publication;
- de-index/remove triggers;
- Search outage;
- stale projection version;
- public projection allowlist;
- notification safe payload;
- close worker race/idempotency;
- DLQ/ops record.

### Documentation Updates

If deadline policy is newly settled, update architecture before enabling worker.

### Acceptance Criteria

Search remains fully rebuildable from source projections; source truth survives downstream outages; no direct Search/Notification implementation exists.

### Exit Gate

PASS only if Search and Notification contract tests, retry tests, stale-version tests, deadline race tests, and projection privacy tests pass.

# Phase 4 — Module Integration and Hiring Dashboard Contracts

## 07 Hiring Dashboard Composition and Neighboring Owner-Facts Interfaces

### Objective

Expose a useful Organization hiring dashboard by composing Organization Hiring source truth with privacy-shaped summaries from Candidate Application, Job Compliance, and Job Interview through public interfaces only.

### Observable Result

Authorized Organization members can view Organization/Job status, publication/compliance summary, applicant counts/summaries, and interview summaries without Organization Hiring reading or mutating neighboring tables directly.

### Cluster Build-Plan Link

Supports CL-06 Feature 01 dashboard responsibility and integration with Features 02, 06, 09+ as those owner interfaces become available.

### Dependencies

- Features 02–06;
- Candidate Application `listJobApplicants`/summary contract;
- Job Compliance decision/report summary;
- Job Interview list/summary contract;
- Role / Authority;
- optional OrganizationFeatureAccess decision only after `U-CL06-04`.

### In Scope

- `getOrganizationHiringDashboard`;
- owner-facts queries for Candidate/Interview consumption;
- integration adapters that call public Module contracts;
- Organization/job/application/interview status presentation;
- basic non-monetized dashboard.

### Out of Scope

- JobApplication writes;
- resume signed URLs;
- interview mutations;
- monetized ATS gating while unresolved;
- candidate search indexing;
- local copies of applicant/interview tables.

### Module-Owned Data

No new source record required. Optional read-model cache only if root architecture explicitly permits; cache is disposable and not truth.

### Public Interfaces

- `getOrganizationHiringDashboard`;
- `getOrganizationHiringContext`;
- `getJobApplicationEligibilityContext`;
- recipient/relationship facts queries.

### Shared Operations Used

- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `queryOwnerFacts`;
- `resolveEntitlement` only after `U-CL06-04` if Organization access becomes Track-backed;
- `evaluateComplianceHold` if dashboard action availability needs hold context.

### Domain Logic

- dashboard composition does not transfer ownership;
- applicant detail never implies resume permission;
- interview summary never mutates application stage;
- compliance summary links to owner evidence;
- unknown/unavailable dependency state is shown as unavailable, not guessed.

### Authorization / Compliance

- cross-org isolation;
- privacy-shaped applicant/interview DTOs;
- no broad admin bypass;
- no raw resume content.

### Database / Transaction Behavior

Read-only in Organization Hiring. No cross-owner transaction.

### Events / Jobs

None required.

### Provider Integration

None.

### UI / Admin Surface

Organization dashboard:

- Organization state;
- Jobs grouped by lifecycle;
- compliance/publication state;
- applicant count/owner-supplied summary;
- interview count/owner-supplied summary;
- actions routed to owning Module UI/command.

### Failure Behavior

- neighboring Module unavailable → partial dashboard with explicit unavailable section;
- unauthorized → no data;
- stale read model/cache → versioned/freshness indication if cache exists.

### Tests

- contract fixtures;
- no direct Candidate/Interview Prisma imports;
- cross-org authorization;
- partial dependency failure;
- privacy shaping;
- dashboard E2E with fixtures.

### Documentation Updates

If `OrganizationFeatureAccess` becomes binding, update architecture before adding paid gates.

### Acceptance Criteria

Dashboard proves the Module can collaborate across CL-06 without absorbing neighboring truth.

### Exit Gate

PASS only if static/dependency checks confirm no neighboring repositories are imported, cross-org tests pass, and partial failures do not produce fabricated state.

# Phase 5 — Privacy, Audit, and Operational Integration

## 08 Organization Hiring Privacy Executor and Retention Participation

### Objective

Allow Privacy / Data Erasure to enumerate, erase/anonymize, retain, and export Organization Hiring-owned subject data without Organization Hiring owning the privacy-request workflow.

### Observable Result

A Privacy worker can call typed Organization Hiring handlers and receive deterministic per-target results for Organization/member/Job data.

### Cluster Build-Plan Link

Supports CL-06 privacy/hardening requirements and cross-cluster CL-08 integration.

### Dependencies

- Features 01–07;
- Privacy target protocol;
- retention decision interface;
- Audit/Ops;
- current legal/retention policy.

### In Scope

- `enumerateSubjectData`;
- `executePrivacyInstruction`;
- `exportPrivacyContribution`;
- membership/user-reference anonymization/removal rules where approved;
- Organization/Job personal display-field handling;
- Search refresh/remove request after privacy-driven source change;
- audit/ops effects.

### Out of Scope

- PrivacyRequest verification;
- DataErasureJob orchestration;
- retention exemption ownership;
- direct deletion of Media/Search/Notification/Audit records;
- legal-policy invention.

### Module-Owned Data

Organization, OrganizationMember, Job, OrganizationNotificationSetting, contextual joins as applicable.

### Public Interfaces

Privacy executor contract.

### Shared Operations Used

- `enumerateSubjectData`;
- `executePrivacyInstruction`;
- `evaluateRetentionRequirement`;
- `requestSearchProjectionRefresh`;
- `appendAuditEvent`;
- reliable job/ops primitives if cleanup is async.

### Domain Logic

- product archive is not legal erasure;
- legal retention decision is honored;
- removing User reference must not corrupt Organization/Job integrity;
- external owner data is returned as related targets, not mutated directly;
- privacy mutation emits source event/search refresh.

### Authorization / Compliance

Only authenticated/authorized Privacy system actor/worker contract may invoke destructive executor.

### Database / Transaction Behavior

Each local target is transactionally applied and returns a standardized result:

```text
erased | anonymized | retained | skipped | failed
```

No cross-owner transaction.

### Events / Jobs

- privacy-driven source change event;
- Search refresh/remove request;
- optional cleanup job for large local target sets.

### Provider Integration

None.

### UI / Admin Surface

No user UI required; optional admin/ops visibility comes from Privacy/Ops owners.

### Failure Behavior

- missing retention decision → fail closed/manual review where required;
- stale target → idempotent no-op/result;
- dependency failure → target remains retryable.

### Tests

- inventory completeness;
- idempotent replay;
- retention path;
- anonymization integrity;
- Search removal request;
- no direct external table writes;
- audit/log redaction.

### Documentation Updates

Update architecture if legal retention requirements create a new binding local invariant.

### Acceptance Criteria

Privacy can orchestrate Organization Hiring data without direct source writes and without Organization Hiring becoming Privacy owner.

### Exit Gate

PASS only if privacy contract/integration tests pass and destructive operations are idempotent, retention-aware, and source-owner-local.

# Phase 6 — Module Hardening and Production Verification

## 09 Concurrency, Idempotency, Security, RLS, Observability, and Failure-Recovery Hardening

### Objective

Prove Organization Hiring remains correct under retries, concurrency, partial dependency outages, unauthorized access, stale events, and operational failure.

### Observable Result

The Module passes production-grade race, replay, authorization, privacy, projection, and failure-recovery test suites with no source-of-truth corruption.

### Cluster Build-Plan Link

Organization Hiring hardening for CL-06 Phase 4 / production verification and all Organization Hiring-owned portions of Cluster Features 01 and 03.

### Dependencies

- Features 01–08;
- final Cluster blockers for any production path being enabled;
- shared queue/outbox/ops infrastructure.

### In Scope

- race tests and fixes;
- idempotency replay;
- RLS parity;
- event inbox/outbox dedupe;
- stale downstream event handling;
- Search/Notification/Compliance outage behavior;
- safe logging/metrics;
- dead-letter/manual-review behavior;
- source projection rebuild;
- backfill/migration verification;
- performance indexes for Organization/Job list queries.

### Out of Scope

- new business features;
- unresolved Organization verification;
- unresolved ATS billing;
- provider adapters;
- neighboring Module hardening.

### Module-Owned Data

All Organization Hiring-owned records and event semantics.

### Public Interfaces

No new business interface unless hardening exposes a documented health/diagnostic read through Ops.

### Shared Operations Used

- `executeIdempotentCommand`;
- `deduplicateDomainEvent`;
- `publishDomainEvent`;
- `enqueueReliableJob`;
- `executeRetryWithBackoff`;
- `withOptimisticConcurrency`;
- `acquireAggregateLock`;
- `appendAuditEvent`;
- Ops integration.

### Domain Logic

Verify invariants under:

- simultaneous member changes;
- duplicate publication requests;
- publish/edit race;
- compliance decision replay;
- close/manual transition race;
- stale Search refresh;
- privacy command replay.

### Authorization / Compliance

- exhaustive action matrix;
- RLS/server parity;
- no client status writes;
- admin/support restricted according to Role / Authority;
- sensitive data redacted from telemetry.

### Database / Transaction Behavior

- inspect transaction isolation and lock ordering;
- ensure no deadlock-prone inconsistent aggregate lock order;
- verify indexes;
- migration rollback/backfill plan;
- verify outbox atomicity.

### Events / Jobs

- inbox dedupe;
- retry exhaustion → Ops record;
- dead-letter manual-review path;
- no duplicate business effect on replay.

### Provider Integration

None.

### UI / Admin Surface

Only safe operational indicators owned by Organization UI; provider/queue diagnostics remain Ops-owned.

### Failure Behavior

Every failure class is mapped to stable public category and preserves truthful source state.

### Tests

Required:

- domain unit suite;
- integration suite;
- public contract suite;
- RLS/authorization suite;
- concurrency stress tests;
- idempotency replay tests;
- outbox/inbox tests;
- Search/Notification/Compliance failure tests;
- privacy tests;
- migration/backfill tests;
- Playwright Organization + draft Job + publication fixture journey;
- performance smoke tests for organization Job/member lists.

### Documentation Updates

- progress tracker;
- architecture only if binding decision changed;
- dependency interface docs if contract changed;
- record resolved `U-CL06-*` decisions.

### Acceptance Criteria

- no invariant violation under concurrent requests;
- no duplicate side effect under replay;
- no unauthorized cross-org read/write;
- no Search/provider truth leakage;
- no privacy orchestration leakage;
- all production publication blockers explicitly resolved or path remains disabled;
- all telemetry is safe.

### Exit Gate

PASS only if all required quality checks pass, no architecture blocker is silently bypassed, source truth survives dependency outages/replays, and the Module is ready for CL-06 integration verification.

# MODULE INTEGRATION PHASE

The integration work is distributed across Features 05–08 and must be verified as a single Module gate before Organization Hiring is considered complete.

## Required owner-contract proofs

### Identity / Role

- authenticated actor reaches every protected command;
- Role / Authority receives Organization Hiring owner facts;
- server decision and RLS agree;
- no Organization Hiring role interpreter exists.

### Taxonomy

- Job/Organization classification accepts only canonical IDs;
- taxonomy outage does not permit uncontrolled terms;
- requirement triggers remain Taxonomy-owned.

### Job Compliance

- Organization Hiring supplies versioned Job source;
- Job Compliance returns decision/evidence;
- Organization Hiring alone writes Job status;
- stale decision cannot publish;
- technical failure cannot approve.

### Trust Verification / Holds

- verification requirement/readiness and holds can block configured lifecycle action;
- Organization Hiring does not inspect provider/badge/local hold booleans.

### Media

- only ready valid Organization/Job image assets attach;
- no storage/signing/scanning implementation exists here.

### Search

- index/update/remove requested after source commit;
- Search never reconstructs compliance;
- Search outage does not corrupt source state.

### Candidate Application / Job Interview

- dashboard uses public summaries;
- Organization Hiring has no direct application/interview writes;
- Job eligibility context is source-fact-only.

### Notification / Messaging

- business trigger intent and recipient facts are supplied;
- delivery/thread lifecycle remains external.

### Privacy / Audit / Ops

- privacy executor is owner-local;
- generic audit remains Audit-owned;
- operational failures do not overwrite Organization/Job truth.

## Integration Exit Gate

PASS only if contract tests prove every major boundary above and static dependency checks show no forbidden repository/provider imports.

# MODULE HARDENING PHASE

Hardening is complete only after the following are explicitly tested:

- Organization/member aggregate races;
- Job edit/publication races;
- source-version stale decisions;
- idempotent create/publish/member commands;
- event replay/inbox dedupe;
- Search/Notification/Job Compliance outage;
- queue retry exhaustion and DLQ;
- RLS/server authorization parity;
- privacy executor replay/retention;
- projection rebuild from source;
- safe logging and payload redaction;
- migration/backfill behavior;
- indexes and list-query performance;
- unresolved-feature fail-closed behavior.

# PHASE SUMMARY

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Contracts and Source-of-Truth Foundation | 01–03 |
| 2 | Organization Presentation and Owner-Side Support Facts | 04 |
| 3 | Controlled Job Publication and Public Projection Handoff | 05–06 |
| 4 | Module Integration and Hiring Dashboard Contracts | 07 |
| 5 | Privacy, Audit, and Operational Integration | 08 |
| 6 | Module Hardening and Production Verification | 09 |

**Total features: 9**

# MODULE EXECUTION PATTERN

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read Canonical Shared Operations.
3. Read CL-06 architecture and build plan.
4. Read `organization_hiring/module-architecture.md`.
5. Read this implementation plan.
6. Read public-interface sections for direct dependencies used by the feature.
7. Read current Prisma schema/migrations.
8. Read decisions resolving relevant `U-CL06-*`.
9. Confirm the prior feature exit gate.
10. Write the Required Feature Implementation Specification for this feature only.
11. Implement only this feature.
12. Run required quality checks.
13. Verify workflows/contracts.
14. Update progress.
15. Update architecture only when a binding decision legitimately changed.
16. Record unresolved risks.

# REQUIRED FEATURE IMPLEMENTATION SPECIFICATION

Immediately before coding a numbered feature, produce:

- Objective
- Observable result
- Cluster build-plan link
- Dependencies
- In scope
- Out of scope
- Owned data affected
- Public contracts
- Shared operations consumed
- Permissions/compliance
- Primary workflow
- Provider integration
- Jobs/events
- Idempotency/concurrency
- Error behavior
- Tests
- Acceptance criteria
- Documentation updates

Do not generate all feature specifications in advance.

# REQUIRED COMPLETION REPORT

After implementing each numbered feature, report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused
- Events/jobs added
- Provider adapter changes
- Tests added/changed
- Commands run
- Manual/contract verification
- Documentation updated
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

# FINAL MODULE QUALITY CHECK

Before marking Organization Hiring complete, verify:

1. Organization, membership row/role assignment, and Job source truth have one owner.
2. Role / Authority still owns permission interpretation.
3. Job Compliance truth was not absorbed.
4. Candidate/Application/Resume/Interview truth was not absorbed.
5. Every shared operation is consumed rather than duplicated.
6. Cross-Module reads use public interfaces.
7. No provider adapter exists here without an explicit ownership ruling.
8. Audit, domain events, and observability remain distinct.
9. Privacy orchestration remains Privacy-owned.
10. Search remains projection.
11. OrganizationFeatureAccess ownership was not invented.
12. Organization verification ownership was not invented.
13. Production Job publication is enabled only after `U-CL06-05/06/07`.
14. Ownership transfer is absent until `U-CL06-03`.
15. Schema defect `U-CL06-17` is resolved before affected migrations.
16. Every numbered feature passed its tests and exit gate.
17. A coding agent can implement the Module without inventing architecture.
