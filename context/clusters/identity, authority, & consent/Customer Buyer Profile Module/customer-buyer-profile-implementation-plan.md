# Customer / Buyer Profile Module Implementation Plan

> **Module ID:** `customer_buyer_profile`  
> **Module:** Customer / Buyer Profile Module  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/modules/customer_buyer_profile/implementation-plan.md`  
> **Companion architecture:** this Module `module-architecture.md`  
> **Parent plan:** CL-01 `build-plan.md`  
> **Implementation posture:** dependency-first MVP work. This plan narrows CL-01 work into Customer-owned slices and must not independently advance or redefine Cluster sequencing.

---

## Core Principle

Implement Customer / Buyer Profile through narrow, verifiable slices:

```text
public / observable behavior
→ validated Customer command/query
→ Customer-owned policy
→ authoritative CustomerProfile write/read
→ canonical shared-operation calls
→ event/audit/notification/ops effects through owners
→ contract/integration tests
→ explicit exit gate
```

The central implementation law is:

> `CustomerProfile` is buyer actor truth, but it is not authentication truth, commercial entitlement truth, or any downstream business lifecycle.

A feature is not complete merely because a profile row can be created or edited. The implementation must prove that the correct public contract is used, foreign truth is not copied, retries/concurrency are safe, and every unresolved architecture gate remains explicit.

---

## Build Rules

1. Follow root Workin Ants project overview, architecture, code standards, shared operations registry, CL-01 architecture, and CL-01 build plan.
2. This Module writes only its declared source truth: `CustomerProfile` and Customer-owned execution results. It does not acquire downstream tables merely because they reference CustomerProfile.
3. Consume other Modules through approved public interfaces, typed owner-facts DTOs, or explicitly approved controlled DB policy functions. Direct foreign Prisma repositories are not the default.
4. Reuse canonical Shared Operations by permanent `SH-###` ID. If a needed capability is absent, fix/build it in the canonical owner or use an approved contract/test double; do not create a Customer-local substitute.
5. Every external/server mutation validates runtime input, resolves trusted actor/system context, authorizes the action where applicable, and enforces Customer invariants.
6. Customer actor resolution is not generic marketplace eligibility. Do not hide entitlement, payment, hold, consent, readiness, or downstream lifecycle decisions inside `resolveCustomerActor`.
7. `CustomerProfile.userId @unique` is a core concurrency invariant; concurrent provisioning must converge on one row.
8. CustomerProfile provisioning must succeed independently of Track subscription/grant availability.
9. Do not add local premium/fee-waiver/priority/quota/commission/boost fields or services.
10. Do not implement full CustomerProfile status/archive/restore behavior until the governing lifecycle decisions are resolved and architecture is updated.
11. Do not implement automatic User↔CustomerProfile field synchronization while field precedence is unresolved.
12. Media / File Access owns upload, validation, scanning, processing, storage, file lifecycle, and signed URLs. Customer owns only the avatar attachment meaning.
13. CustomerProfile public search/indexing is disabled until a dedicated visibility decision is approved.
14. Privacy owns PrivacyRequest/DataErasureJob/DataErasureTarget/DataRetentionExemption orchestration. Customer implements only Customer-owned inventory/export/disposition execution.
15. Audit, sensitive-access logging, Notification, Observability, ComplianceHold, idempotency, queues, locking, retries, and outbox remain their canonical owners.
16. Every asynchronous Customer operation is durable, idempotent, bounded, retry-classified, correlated, observable, and dead-letter visible.
17. Every lifecycle mutation is transaction-safe; no client state or in-memory lock establishes source truth.
18. Provider details never appear in Customer business contracts. This Module currently owns no provider adapter.
19. Every numbered feature ends with tests, workflow/contract verification, documentation/progress update, and an exit gate.
20. Do not begin a gated feature by guessing the missing ruling. Resolve the architecture decision first or implement only the explicitly safe subset.

---

## Preconditions

### Hard platform dependencies

The repository/platform must provide or expose approved test doubles for:

- Prisma/Postgres and migrations;
- runtime validation at server boundaries;
- request/correlation context;
- SH-044 idempotent command execution;
- SH-045 event dedupe/inbox behavior;
- SH-046 transactional outbox/event publication;
- SH-047/048 durable jobs and retry/dead-letter behavior;
- SH-051/052 concurrency primitives where required;
- structured logging/metrics/exception/failure/queue telemetry;
- generic AuditEvent/AccessAuditLog interfaces;
- Privacy executor protocol;
- Media public contracts.

A missing primitive does not authorize a Customer-local replacement.

### Hard CL-01 dependencies

Before the main Customer slices:

- Identity & Access must expose a trusted User/actor context and a post-provisioning integration boundary.
- Role / Authority must expose SH-002 for protected profile management.
- Current Prisma must contain `CustomerProfile` with unique `userId`.

### Dependencies that may initially be stubbed through public contracts

- Media / File Access for avatar validation/access;
- Audit / Event Ledger;
- Notification;
- Observability / Ops;
- Privacy / Data Erasure;
- Admin Review / Compliance Hold;
- Gig / Demand, Transaction / Order, and Booking & Calendar consumer contracts.

Full neighboring UIs are not required to test these contracts.

### Architecture gates

The following must be resolved before the corresponding production behavior is enabled:

| Gate | Required before |
| --- | --- |
| `U-CL01-01` ProfileStatus enum owner | enum-level schema ownership/migration changes |
| `U-CL01-02` CustomerProfile transition matrix/open-obligation semantics | full status/archive/restore commands |
| `U-CL01-03` final provisioning orchestration timing | final signup event/request wiring; owner command itself can be built first |
| `U-CL01-04` CustomerProfile ID cutover rule | mandatory downstream actor references/backfill enforcement |
| `U-CL01-05` User vs CustomerProfile display/location/avatar precedence | production edits/sync for affected overlapping fields |
| `U-CL01-06` public CustomerProfile visibility | public page or Search projection |
| `U-CL01-07` Review/Dispute actor reference | Review/Dispute schema migration |
| `CBP-U-01` avatar relation shape | schema FK/generalized attachment migration; validation-based UUID attachment can proceed without it |
| `CBP-U-04` Customer privacy disposition/retention map | destructive privacy delete/anonymize behavior |

---

# Phase 1 — Source-of-Truth and Contract Foundation

## 01 CustomerProfile Source-of-Truth Boundary and Public Contracts

### Objective

Establish the Customer Module boundary in code, validate the existing CustomerProfile schema invariants, and introduce the stable public contracts needed before any orchestration or UI depends on buyer actor truth.

### Observable Result

- CustomerProfile persistence is accessible only through the Customer Module repository/service boundary.
- A contract test can construct and validate the `resolveCustomerActor`, `assertCustomerActorConsistency`, provisioning, and safe profile-view request/result shapes.
- No foreign lifecycle repository is imported into Customer code.
- The current one-to-one `userId` uniqueness and source fields are documented and tested against the database.

### Cluster Build-Plan Link

Supports **CL-01 Feature 05 — Customer actor provisioning/resolution** by creating the Module-owned contract/source foundation required for that Cluster slice. It does not independently advance the Cluster beyond Feature 05.

### Dependencies

- current Prisma `CustomerProfile` model and `ProfileStatus` enum;
- root/module folder convention;
- root runtime validation mechanism;
- shared request/result conventions;
- SH-003/SH-004 registry contracts;
- Identity User identifier type/contract.

### In Scope

- create the Customer Module internal directory boundary;
- CustomerProfile-only repository with narrow methods required by planned commands/queries;
- runtime schemas for public Customer inputs/results;
- public contract types for:
  - `resolveCustomerActor`;
  - `assertCustomerActorConsistency`;
  - `provisionDefaultCustomerProfile`;
  - safe `getCustomerProfile`;
- Customer owner-facts DTO compatible with SH-003 if Role requires it;
- database tests for unique User binding and current defaults;
- boundary tests preventing accidental foreign repository ownership.

### Out of Scope

- User provisioning/authentication;
- automatic profile provisioning orchestration;
- metadata edits;
- avatar upload/attachment;
- status transitions;
- Track records or entitlement resolution;
- downstream `customerProfileId` migrations;
- public profile/search;
- privacy destructive execution;
- any provider client.

### Module-Owned Data

- `CustomerProfile` only.
- No new model is planned.
- `ProfileStatus` is read as the current schema vocabulary without claiming enum-definition ownership.

### Public Interfaces

Introduce contract definitions for:

```text
provisionDefaultCustomerProfile
resolveCustomerActor          # SH-004 semantic contract
assertCustomerActorConsistency
getCustomerProfile
queryCustomerOwnerFacts       # SH-003-compatible only if required
```

Do not expose the repository itself as the public Module interface.

### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-003 `queryOwnerFacts` | each source Module | contract shape for minimum Customer facts | which Customer facts are safe/needed | cross-domain generic repository |
| SH-004 `resolveCustomerActor` | Customer / Buyer Profile | public contract defined here, implementation in Feature 02 | Customer actor DTO semantics | consumer-local buyer resolver |
| SH-032 `createRequestContext` | platform/Ops | public service entry contract where root framework supplies context | safe Customer identifiers | local context helper |
| SH-034 `sanitizeTelemetryMetadata` | Ops/Audit policy | contract/log fixtures | Customer PII classification | local sanitizer |

### Domain Logic

- `CustomerProfile.id` is the commercial buyer actor ID.
- `CustomerProfile.userId` binds that actor to exactly one base account User.
- `userId` uniqueness is authoritative at the database layer.
- `resolveCustomerActor` result is intentionally small: identity/status/safe actor metadata only.
- Public contracts must not include Track plan/grant data, payment data, Gig/Order/Booking states, signed avatar URLs, or public-search assumptions.
- If a consumer supplies an expected `customerProfileId`, the public contract must support a mismatch result rather than trusting it.

### Authorization / Compliance

No new end-user mutation is enabled in this feature. Still define contracts so later protected reads/mutations accept trusted actor context and can call SH-002.

Privacy-sensitive fields must be excluded from default actor DTOs.

### Database / Transaction Behavior

- Verify `CustomerProfile.userId @unique` with a database-level test.
- Verify default `status = active` as current executable schema behavior; do not infer a full lifecycle from it.
- Verify `createdAt/updatedAt` behavior.
- No schema migration unless inspection reveals the current uploaded schema differs from the repository; any change requires architecture review.

### Events / Jobs

None implemented. Define no Customer-specific event table.

### Provider Integration

None.

### UI / Admin Surface

None required.

### Failure Behavior

- malformed contract input → validation denial;
- missing profile → explicit `not_found`/`not_provisioned` category;
- User/Profile mismatch → explicit consistency mismatch;
- unknown status value at runtime → fail validation rather than coerce;
- repository/database error → internal safe failure; no raw ORM details leak.

### Tests

- contract schema validation tests;
- repository unit/integration tests;
- unique `userId` database test;
- result minimization tests;
- architectural import/boundary test if repository tooling supports it;
- test confirming no Track/Gig/Order/Booking/Media repository is used.

### Documentation Updates

- update progress tracker with Module Feature 01 status;
- if repository path conventions differ from this architecture, record/update the root/module architecture rather than creating a second pattern;
- do not resolve U-CL01 decisions in code.

### Acceptance Criteria

- CustomerProfile source ownership is represented by one module-local repository boundary;
- public contracts compile and have runtime validation;
- database proves one CustomerProfile per User;
- actor DTO excludes commercial/foreign truth;
- no provider/foreign lifecycle code exists in the Module;
- no new unresolved architecture is silently introduced.

### Exit Gate

Before Feature 02:

- module unit/contract/database tests pass;
- Prisma/schema validation and migration checks pass as applicable;
- typecheck/lint/build pass;
- a reviewer can identify exactly where CustomerProfile reads/writes occur and confirm they do not reach foreign lifecycles;
- progress tracker records Feature 01 complete.

---

## 02 Default CustomerProfile Provisioning, Resolution, and Existing-User Backfill

### Objective

Make every eligible User idempotently resolvable to at most one CustomerProfile through the canonical Customer public interface, including safe recovery/backfill for existing Users.

### Observable Result

- A valid eligible User can receive or idempotently obtain one CustomerProfile.
- A duplicate/replayed provisioning call returns the same profile.
- A downstream test consumer resolves `(userId, customerProfileId)` and proves the pair belongs together.
- Existing Users without profiles can be processed through a resumable Customer-owned backfill.
- Track being unavailable does not prevent CustomerProfile creation.

### Cluster Build-Plan Link

Direct implementation decomposition of **CL-01 Feature 05 — Customer actor provisioning/resolution**.

### Dependencies

- Module Feature 01;
- CL-01 Identity/Authority foundation Features 01–02;
- Identity public User existence/eligibility facts;
- User-provisioned event or explicit post-signup command boundary;
- SH-044/045/046/047/048;
- architecture gate `U-CL01-03` for final production trigger choice.

The owner command and backfill can be implemented before `U-CL01-03`; final signup wiring cannot.

### In Scope

- `provisionDefaultCustomerProfile` application service;
- SH-004 `resolveCustomerActor` implementation;
- `assertCustomerActorConsistency` implementation;
- safe owner/admin `getCustomerProfile` query using existing authority boundary;
- event consumer shell if the approved path is event-based, but production wiring remains gated until U-CL01-03;
- existing-user backfill worker using approved Identity query/stream contract;
- mismatch/conflict reporting;
- idempotency/concurrency behavior.

### Out of Scope

- Customer status lifecycle beyond current initial `active` creation;
- User/Profile metadata synchronization;
- downstream mandatory customerProfileId cutover;
- Track default plan assignment;
- public search;
- commerce history;
- Review/Dispute migration;
- foreign record repair.

### Module-Owned Data

- creates/reads `CustomerProfile` only;
- no Track or downstream business records;
- no new event ledger table.

### Public Interfaces

Implement:

```text
provisionDefaultCustomerProfile({ userId, idempotencyKey, correlationContext })
resolveCustomerActor({ userId, expectedCustomerProfileId? })
assertCustomerActorConsistency({ userId, customerProfileId })
getCustomerProfile({ requester, profileId|userId, purpose })
```

`resolveCustomerActor` remains a query/decision and must not unexpectedly create a profile unless architecture later explicitly merges lookup and provisioning semantics. Provisioning is the explicit command.

### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-004 `resolveCustomerActor` | Customer | downstream resolution | Customer existence/status/consistency | `buyerResolver.ts` elsewhere |
| SH-001 `resolveAuthenticatedActor` | Identity | protected self read/use | actor source only | customer session helper |
| SH-002 `authorizeResourceAction` | Role | protected `getCustomerProfile` | Customer owner facts | customer ACL |
| SH-044 `executeIdempotentCommand` | platform | provisioning per User | semantic key = default CustomerProfile provision for User | local idempotency table |
| SH-045 `deduplicateDomainEvent` | platform | User-provisioned event consumer | consumer/event semantic key | custom inbox table |
| SH-046 `publishDomainEvent` | platform | optional profile-provisioned fact | minimized Customer event | customer event bus |
| SH-047 `enqueueReliableJob` | platform | existing-user backfill batches | batch/item payload | local queue runner |
| SH-048 `executeRetryWithBackoff` | platform | transient backfill/event failure | retryable/terminal classification | hand-rolled retry loop |
| SH-051 `acquireAggregateLock` | platform | only if persistence pattern needs extra serialization | lock by User/profile aggregate | in-memory mutex |
| SH-114 `provisionOneToOneProfile` | shared mechanism / profile owner policy | provisioning plumbing | Customer eligibility/default status/row values | generic ProfileService owning all branches |
| SH-032/033/034/036/037/038 | Ops/platform | request/job telemetry | safe Customer identifiers/reasons | module-local logging/metrics/failure stores |

### Domain Logic

1. Receive trusted User ID from approved Identity/system boundary.
2. Verify the User exists and is eligible according to the minimum Identity fact contract; Customer does not recreate age/auth logic.
3. Execute provisioning through SH-044 using the User-based semantic key.
4. Create `CustomerProfile` with current schema defaults only when no profile exists.
5. If another request wins the race, recover by reading the unique User-bound profile and return it as existing.
6. Never create a second profile for the same User.
7. Never wait for Track enrollment or create Track records.
8. `resolveCustomerActor` returns profile ID, User ID, status, and only safe display metadata.
9. If expected profile ID is supplied, mismatch is a hard denial/conflict result.
10. Backfill never guesses a User/Profile mapping; ambiguous/invariant-breaking items are isolated for manual review.

### Authorization / Compliance

- self-service resolution starts from SH-001 actor context;
- internal post-signup event/command must be trusted system context, not a client-selected arbitrary User ID;
- owner/admin profile read uses SH-002;
- no public profile access;
- no local marketplace permission check;
- no entitlement or payment requirement for profile existence.

### Database / Transaction Behavior

- primary concurrency guarantee: unique `CustomerProfile.userId`;
- command transaction creates/returns one row;
- if outbox profile-provisioned event is required, source write + outbox must be atomic;
- no exactly-once delivery claim: event/job replay must be harmless;
- backfill uses cursor/checkpoint outside the business row but each item uses the same idempotent command;
- no foreign downstream table writes in the backfill.

### Events / Jobs

**Possible inbound:** Identity User-provisioned event, once U-CL01-03 chooses event orchestration.

**Possible outbound:** minimized CustomerProfile-provisioned event through SH-046 if Track/other consumers demonstrably require durable notification.

**Backfill worker:** cursorable, retryable, dead-letter visible, per-item idempotent.

### Provider Integration

None. Identity provider state is consumed only through Identity's Workin Ants contract.

### UI / Admin Surface

A minimal profile/account verification surface is optional if the root application already has an account profile route. It may display safe profile identity/status for debugging/verification. No commerce-history or public profile UI.

### Failure Behavior

- User missing/ineligible → explicit `not_provisioned` result;
- duplicate command/event → return existing profile;
- unique constraint race → recover existing row, not 500/duplicate;
- profile belongs to different User than expected → invariant/consistency failure;
- transient DB/queue failure → retry per shared policy;
- poison backfill item → dead-letter/manual review with safe IDs;
- Track unavailable → no effect on provisioning;
- event publication transient failure after atomic outbox write → dispatcher retries; source row stays committed.

### Tests

- one-to-one uniqueness;
- parallel provisioning stress test;
- provisioning replay/idempotency;
- event replay/inbox dedupe;
- resolver contract positive/not-found/mismatch;
- Track-unavailable test;
- self/admin/other-user profile read authorization;
- existing-user backfill resume/checkpoint;
- poison item isolation;
- source mutation + outbox atomicity if event enabled;
- test proving no Track or foreign lifecycle write.

### Documentation Updates

- if `U-CL01-03` is resolved while implementing, update Module and CL-01 architecture before final production wiring;
- document final orchestration (same request/outbox/worker) and event name/version if enabled;
- update progress tracker and public contract reference.

### Acceptance Criteria

- eligible Users resolve to zero-or-one profile before provisioning and exactly one after successful provisioning;
- duplicate/replayed work cannot create duplicate profiles;
- a mismatched User/Profile pair is rejected;
- provisioning has no Track dependency;
- backfill is resumable and exception-safe;
- consumers can use SH-004 without reading CustomerProfile directly;
- no commercial/foreign truth is added to CustomerProfile.

### Exit Gate

Before Feature 03:

- all Feature 02 unit/contract/database/concurrency/backfill tests pass;
- the CL-01 Feature 05 exit conditions are satisfied for Customer-owned work;
- typecheck/lint/build pass;
- unresolved `U-CL01-03` is either resolved for production wiring or the final orchestration remains explicitly disabled/stubbed;
- progress tracker is current.

---

# Phase 2 — Protected Profile Management and Media Boundary

## 03 Protected Customer Metadata Management and Avatar Attachment

### Objective

Allow authorized self/admin updates of explicitly approved Customer-owned profile fields and Media-backed avatar attachment without importing file mechanics, public visibility, or unresolved field synchronization into the Module.

### Observable Result

- An authorized profile owner can update only fields whose ownership/editability has been explicitly approved.
- Another ordinary User cannot update the profile.
- A validated, ready MediaAsset can be attached as avatar.
- Invalid/unready assets are rejected and no Customer code signs URLs or scans files.
- No public profile/search side effect occurs.

### Cluster Build-Plan Link

Direct decomposition of **CL-01 Feature 06 — CustomerProfile Protected Management and Avatar Boundary**.

### Dependencies

- Module Feature 02;
- CL-01 Role authorization foundation;
- Media public contracts/test double;
- SH-090 contextual attachment contract;
- `U-CL01-05` must be resolved for each overlapping display/location field enabled for editing;
- `CBP-U-01` is not required for validation-based raw UUID attachment, but is required before a schema relation migration.

### In Scope

- runtime-validated metadata patch command;
- field allowlist defined by approved ownership ruling;
- expected-version/optimistic-concurrency behavior;
- SH-002 self/admin permission integration;
- avatar attachment command through Media validation/public contract;
- safe profile view DTO by purpose;
- optional account profile edit surface if the Module genuinely owns one;
- audit/sensitive-access requests where root policy requires;
- optional profile-updated event only when a consumer is identified.

### Out of Scope

- User↔CustomerProfile bidirectional sync;
- exact location reveal or geocoding truth;
- full CustomerProfile status/archive/restore;
- public profile page/directory;
- Search projection;
- Media upload/scanning/storage/presign implementation;
- commerce history;
- Track/premium display truth inside Customer DTO;
- foreign lifecycle mutation.

### Module-Owned Data

Potentially affected `CustomerProfile` fields, only after ownership approval:

```text
displayName
city
state
country
avatarMediaId
updatedAt
```

No new Media model/relation is introduced by default.

### Public Interfaces

```text
updateCustomerProfileIdentity
setCustomerProfileAvatar
getCustomerProfile (purpose-limited view)
```

If root UI requires a separate command to clear avatar, define it as a Customer contextual relation update; it still must not delete the MediaAsset.

### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-001 | Identity | mutation/read entry | trusted actor | local session resolver |
| SH-002 | Role | before profile read/update/avatar | Customer owner/admin action | Customer permissions engine |
| SH-044 | platform | mutation retry safety | semantic profile mutation key | local idempotency |
| SH-052 | persistence | compare-and-swap mutation | expected Customer profile version/timestamp | last-write-wins helper |
| SH-029 | Audit | material admin mutation where required | safe Customer action metadata | Customer audit table |
| SH-030 | Audit | sensitive profile/admin read if policy classifies it | sensitivity/purpose | Customer access log |
| SH-082/083/084 | Media | Media upload/processing side before attachment | Customer requires approved ready asset | avatar scanner/processor |
| SH-087 | Media | display private avatar where required | requester may view profile/avatar context | avatar presign helper |
| SH-090 `attachValidatedMedia` | contextual Customer + Media truth | avatar command | this actor may attach this asset to this profile | profile-owned file lifecycle |
| SH-032–037 | platform/Ops | diagnostics and dependency failure | safe profile IDs/reasons | local logger/metrics/failure store |
| SH-046 | platform outbox | only if a real consumer requires update event | minimized changed categories | local event bus |

### Domain Logic

#### Metadata

- Accept only an explicit allowlisted patch.
- Reject fields whose User-vs-Customer precedence is not yet approved.
- Normalize strings/nullable values according to root standards.
- City/state/country are profile display metadata, not exact LocationReveal or geocoded truth.
- Do not mirror edits onto `User` until a separate synchronization rule is approved.

#### Avatar

1. resolve actor;
2. authorize profile update;
3. send mediaAssetId/context to the approved Media contract;
4. require Media readiness/safety result;
5. validate contextual attachment ownership/use;
6. atomically update `avatarMediaId` with expected profile version;
7. obtain display URL later through Media, not as stored Customer truth.

#### Public visibility

Having `displayName`/location/avatar fields does not make the profile public.

### Authorization / Compliance

- profile owner and approved admin/support roles only;
- admin/support purpose must be action-specific through SH-002;
- sensitive read audit follows root matrix;
- exact/private location data is not accepted into this feature;
- if Media is sensitive/private, Customer does not bypass Media access policy;
- no local hold/Track/consent gate unless a future action-specific policy explicitly requires it.

### Database / Transaction Behavior

- mutation transaction updates CustomerProfile only;
- use expected concurrency token via SH-052;
- avatar write occurs only after valid Media decision; do not partially persist an unvalidated asset;
- if the same valid asset is reattached idempotently, return current state without duplicate side effects;
- do not create an FK relation migration without CBP-U-01 approval.

### Events / Jobs

No background job is required for ordinary metadata edits.

If Media emits an asset-removed/restricted event, a future Customer consumer may suppress/clear the avatar reference using SH-045 replay protection, but only once that cross-owner contract is approved. Do not build speculative event handlers.

### Provider Integration

None. Customer never contacts object storage/image/scanner providers.

### UI / Admin Surface

If account profile UI exists:

- owner edit form for approved fields;
- avatar selection/upload intent routed through Media-owned components/actions;
- loading/error/conflict states;
- no public profile toggle unless later architecture adds one.

An admin/support view must be purpose-limited and authorized.

### Failure Behavior

- invalid patch → validation denial;
- field ownership unresolved/not editable → architecture/policy denial;
- unauthorized actor → authorization denial;
- stale expected version → conflict with safe reload/retry response;
- invalid/unready/unsafe MediaAsset → validation denial;
- Media unavailable → avatar change unavailable; do not attach by UUID anyway;
- profile public-view request → not supported while U-CL01-06 unresolved;
- post-commit notification/audit/ops transient failure → follow owner side-effect policy; never fabricate rollback unless audit atomicity is explicitly required.

### Tests

- owner/admin/other-user authorization matrix;
- runtime validation for each field;
- test each unresolved field is rejected until approved;
- no implicit User field sync;
- optimistic-concurrency conflict;
- avatar valid/unready/missing/wrong-context cases;
- Media timeout/degradation;
- no signed URL/storage/scanner implementation in Customer;
- purpose-limited profile DTO/redaction;
- no Search projection/event;
- audit/access contract where required;
- component/action tests if UI exists.

### Documentation Updates

If `U-CL01-05` is resolved, update both Cluster and Module architecture with:

- field authority;
- copy-on-create/sync policy;
- editable field list.

If CBP-U-01 is resolved into a schema relation, update architecture before the migration.

### Acceptance Criteria

- only authorized actors can mutate approved profile fields;
- unresolved fields do not accidentally become editable;
- avatar cannot bypass Media validation;
- Customer contains no storage/scanner/presign code;
- public visibility remains disabled;
- no automatic User synchronization exists without a ruling;
- stale writes are deterministic conflicts.

### Exit Gate

Before Feature 04 or cross-Cluster cutover work:

- CL-01 Feature 06 Customer-owned exit conditions pass;
- all Feature 03 authorization/Media/concurrency tests pass;
- typecheck/lint/build pass;
- U-CL01-05 status is accurately documented;
- no public Search projection was emitted;
- progress tracker is updated.

---

# Phase 3 — Architecture-Gated CustomerProfile Lifecycle

## 04 CustomerProfile Status, Pause/Suspension, Archive, and Restore

> **Execution gate:** This feature is planned because the Module owns CustomerProfile lifecycle, but it must **not** start production implementation until `U-CL01-01` and `U-CL01-02` are resolved and the CL-01 plan explicitly schedules the gated completion of Customer profile lifecycle work. This feature does not independently move CL-01 sequencing.

### Objective

Implement the approved CustomerProfile-specific lifecycle transition matrix, archive/restore behavior, open-obligation rules, and effects without turning status into a generic ComplianceHold or mutating foreign obligations.

### Observable Result

After architecture approval:

- every supported status transition has one Customer-owned command path;
- invalid/stale transitions are denied deterministically;
- status, timestamps, and Customer event/audit effects remain consistent under concurrency;
- active holds may gate a Customer action where policy says so but do not silently rewrite profile status;
- open Orders/Bookings/Disputes are handled according to owner-fact policy without Customer mutating them.

### Cluster Build-Plan Link

Completes the lifecycle portion intentionally deferred by **CL-01 Feature 06**. It may run only after the Cluster architecture resolves the status matrix and permits this extension; it must complete before any downstream cutover that assumes status semantics.

### Dependencies

- Module Feature 03;
- **required architecture rulings:** U-CL01-01, U-CL01-02;
- owner-facts contracts from Order/Booking/Review-Dispute as required by the approved transition policy;
- SH-002 authorization;
- SH-011 hold decision if specified;
- SH-053 transition mechanism;
- root step-up matrix if sensitive admin lifecycle actions require it.

### In Scope

Only after approval:

- typed transition matrix for CustomerProfile;
- commands for approved state changes;
- archive/restore timestamp rules;
- owner/admin/system actor policy;
- open-obligation fact queries;
- hold composition if applicable;
- optimistic concurrency/lock strategy;
- Customer lifecycle event and Audit/Notification effects required by the policy;
- complete transition tests.

### Out of Scope

- changing the shared ProfileStatus enum unless U-CL01-01 specifically approves a Customer-owned schema change;
- creating/closing Orders, Bookings, Gigs, Reviews, Disputes;
- creating/releasing ComplianceHold;
- deleting the User;
- Privacy request orchestration;
- public Search visibility;
- entitlement/billing changes.

### Module-Owned Data

- `CustomerProfile.status`;
- `CustomerProfile.archivedAt` according to approved invariant;
- possibly `updatedAt` as concurrency evidence;
- no new history model unless architecture separately approves it.

### Public Interfaces

Potential approved commands:

```text
changeCustomerProfileStatus
archiveCustomerProfile
restoreCustomerProfile
```

Exact action names may follow root naming, but all mutations must funnel through one Customer policy service rather than arbitrary status writes.

### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-001 | Identity | protected lifecycle command | actor source | Customer auth |
| SH-002 | Role | lifecycle authorization | who may request each Customer transition | Customer role engine |
| SH-003 | source owners | open-obligation facts if required | minimum facts needed to decide Customer transition | foreign repositories |
| SH-011 | Hold owner | only if approved transition/action is hold-sensitive | relationship between hold and Customer command | local blocked state |
| SH-014 step-up | Identity | only if root security matrix requires | action/target classified sensitive | Customer MFA flow |
| SH-044 | platform | transition idempotency | semantic transition key | local idempotency |
| SH-052 | persistence | expected status/version | Customer conflict policy | last-write-wins |
| SH-053 | shared lifecycle mechanism | state change | Customer transition matrix | generic ProfileService |
| SH-029 | Audit | material status/admin change | safe action/reason metadata | Customer audit table |
| SH-041 | Notification | approved user notice | trigger/safe variables | local notifier |
| SH-046 | outbox | durable lifecycle fact if consumer requires | Customer event schema | event bus |

### Domain Logic

This plan intentionally does **not** invent the matrix. The approved architecture must define:

- every allowed `from → to` transition;
- actor allowed to request each transition;
- whether any transition is terminal;
- restore/reopen rules;
- archive timestamp set/clear/history semantics;
- effect on new buying/posting/booking actions;
- which historical rights remain accessible;
- how open Orders/Bookings/Disputes constrain or survive the transition;
- whether ComplianceHold only gates actions or may be a prerequisite for a specific Customer status command;
- notification/audit requirements.

Once approved, encode this as a pure Customer transition policy and test it exhaustively.

### Authorization / Compliance

- self/admin/system actions are separate permission keys;
- a hold is an external decision, not profile status truth;
- open financial/transactional obligations remain owner truth;
- destructive lifecycle behavior must coordinate with Privacy but not become Privacy orchestration;
- step-up only through Identity if required.

### Database / Transaction Behavior

- read current status + expected version and validate transition inside one transaction;
- write status/timestamp and outbox event atomically where event is required;
- use SH-052 or approved row lock strategy to prevent double/stale transitions;
- retries return prior successful result or conflict, never apply the transition twice;
- no direct foreign writes inside the Customer transaction unless a root architecture explicitly approves a multi-owner transaction (none currently does).

### Events / Jobs

Lifecycle transitions are synchronous owner mutations. Notification/event side effects may be outbox-driven.

No scheduled “auto status” worker is introduced unless later policy explicitly defines one.

### Provider Integration

None.

### UI / Admin Surface

Only if product requirements include lifecycle controls:

- present only allowed actions returned from server policy;
- UI never computes transition legality by itself;
- admin/support reason input where policy requires;
- confirmation/step-up surfaces routed through canonical owners.

### Failure Behavior

- architecture gate unresolved → feature not enabled;
- unsupported transition → stable `unsupported_state`;
- stale current status/version → conflict;
- unauthorized → denial;
- required owner facts unavailable → unavailable/fail closed if policy requires them;
- required hold service unavailable → fail closed/unavailable if hold is mandatory;
- downstream side-effect failure after source commit → retry side effect, not status guess.

### Tests

After architecture approval:

- exhaustive transition matrix positive/negative test;
- self/admin/system authorization matrix;
- concurrent status change race;
- idempotent replay;
- open-obligation scenarios using owner contract fixtures;
- hold-present/absent/unavailable tests if relevant;
- archive timestamp invariant;
- restore/reopen behavior;
- event/outbox atomicity;
- audit/notification contract tests;
- test proving no foreign lifecycle mutation.

### Documentation Updates

**Required before code:** update `module-architecture.md` and CL-01 architecture with the approved matrix and open-obligation rules. If enum ownership changes, update root vocabulary/schema ownership docs too.

After implementation, update progress and public interface docs.

### Acceptance Criteria

- no transition exists in code that is absent from approved architecture;
- every transition is one-owner, authorized, conflict-safe, and test-covered;
- ComplianceHold remains separate truth;
- foreign obligations are read through owner interfaces, not mutated;
- archive/restore timestamps follow one documented invariant;
- audit/domain events are distinct.

### Exit Gate

Feature 04 is complete only when:

- U-CL01-01/U-CL01-02 are resolved and documentation is updated first;
- complete transition/authorization/concurrency tests pass;
- no foreign lifecycle write exists;
- no hold/profile-status mirroring exists;
- typecheck/lint/build pass;
- progress tracker records the resolved architecture and implementation status.

If the gates are still unresolved, this feature remains **planned / not started**, not partially invented.

---

# Phase 4 — Cross-Cluster Customer Actor Contract Proof

## 05 Customer Actor Consumer Contracts and Cutover Support

### Objective

Prove the Customer actor boundary with Gig / Demand, Transaction / Order, and Booking & Calendar and support the approved migration from ambiguous User-only buyer identity to CustomerProfile for new records without taking ownership of destination tables.

### Observable Result

After `U-CL01-04` is approved:

- a test customer can initiate representative Gig/Order/Booking owner commands with one validated CustomerProfile actor;
- mismatched User/Profile pairs are rejected before destination write;
- post-cutover owner contracts can require the approved CustomerProfile reference;
- legacy ambiguous records remain readable under destination migration policy;
- Customer reconciliation reports mismatches but never repairs foreign rows directly.

### Cluster Build-Plan Link

Direct Customer-owned contribution to **CL-01 Feature 13 — Customer Actor Cutover for Customer-Side Business Records** and the corresponding CL-04/CL-05 contract proof.

### Dependencies

- Module Features 02–03; Feature 04 only if the destination policy explicitly depends on approved Customer status semantics;
- **U-CL01-04 resolved** before mandatory cutover enforcement;
- Gig, Order, Booking public create/validation contracts;
- destination-owner migration/backfill plans;
- SH-003 owner-facts contracts where needed;
- shared idempotent job/reconciliation infrastructure.

### In Scope

Inside Customer Module:

- hardened SH-004 resolver and consistency assertion for downstream use;
- explicit consumer contract fixtures/versioned DTOs;
- Customer-owned actor mismatch detection/reporting;
- CustomerProfile existence backfill completion;
- optional owner-coordinated migration support tooling that emits validated mapping facts, not foreign writes;
- contract/integration/E2E tests with Gig/Order/Booking public interfaces;
- performance/index review for Customer's own resolution query.

Outside Customer Module but required as Cluster dependencies:

- destination owners migrate/validate their own `customerProfileId` fields, nullability, and indexes;
- destination owners retain User IDs only where their schema needs account/audit traceability.

### Out of Scope

- Customer repository writes to Gig/GigAssignment/Order/BookingHold/BookingSlotLock/Booking;
- destination schema migration files owned solely from Customer code;
- Review/Dispute direct CustomerProfile FK until U-CL01-07;
- fee-waiver or priority policy;
- payment state;
- public search;
- foreign historical data “fixes” guessed by Customer.

### Module-Owned Data

- CustomerProfile source rows only;
- no new downstream migration truth;
- operational mismatch report may use shared Ops/queue facilities, not a Customer-owned generic incident table.

### Public Interfaces

Prove:

```text
resolveCustomerActor
assertCustomerActorConsistency
getCustomerProfile / owner facts as required
```

with:

- Gig creation/posting interface;
- Order buyer/checkout interface;
- Booking hold/lock/booking interface.

The destination interface receives Customer actor facts; Customer does not wrap or own the destination command.

### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-001 | Identity | user actor setup | account actor | direct auth parsing |
| SH-004 | Customer | every buyer-side owner contract | buyer identity | consumer buyer resolver |
| SH-003 | each owner | minimum facts during cross-owner validation | DTO only | cross-domain repositories |
| SH-002 | Role | destination owner action and any Customer-protected read | Customer supplies owner facts, destination owns action permission context | Customer generic marketplace gate |
| SH-044 | platform | migration/backfill item/reconciliation command | semantic Customer item key | local idempotency |
| SH-047/048 | platform | resumable mapping/backfill work | batch/retry policy | custom queue/retry engine |
| SH-032–038 | Ops/platform | mismatch/worker diagnostics | safe IDs/categories | local migration incident store |
| SH-029 | Audit | authorized manual Customer-owned correction only if required | safe action/reason | local audit |

### Domain Logic

- Customer is authoritative for `User ↔ CustomerProfile` mapping.
- Destination owner is authoritative for whether and where to store the CustomerProfile reference.
- When both IDs are present, they must match before destination mutation.
- New-record cutover rule comes from U-CL01-04; Customer does not decide nullability alone.
- Legacy records that lack a CustomerProfile reference are handled by destination migration policy.
- If a historical record cannot be mapped unambiguously, report exception/manual review; do not infer from display name/email/location.
- Customer status is returned as a fact, but destination owner must not invent Customer status semantics beyond the approved Customer public contract.
- Track effects are obtained separately from Track and snapshotted by destination owner where required.

### Authorization / Compliance

- each destination action separately runs its own SH-002 authorization and other gates;
- Customer resolver does not become a universal `canBuy/canPost/canBook` gate;
- exact location reveal remains Location Safety;
- fee waiver/priority remain Track + Order/Booking policy;
- Review/Dispute remains unchanged until its actor decision is approved.

### Database / Transaction Behavior

Inside Customer:

- resolution query must use unique User index efficiently;
- consistency assertion is read-only;
- backfill remains idempotent by User.

Across owners:

- do not attempt one giant Customer transaction spanning destination tables;
- destination owner writes its record after validating Customer actor contract;
- owner-specific migrations and constraints are reviewed/owned by those Modules;
- migration reconciliation never overwrites newer destination state.

### Events / Jobs

- CustomerProfile backfill/reconciliation continues through SH-047/048;
- no Customer event commands a destination owner to rewrite records blindly;
- owner-coordinated migration may consume stable mapping facts with event/job dedupe.

### Provider Integration

None.

### UI / Admin Surface

No new Customer UI is required. Use existing Gig/Order/Booking surfaces for integration/E2E proof. An operator-safe mismatch report may be surfaced through Ops, with safe identifiers only.

### Failure Behavior

- mismatch → reject destination setup before write and emit safe operational evidence;
- eligible User missing CustomerProfile after approved cutover → provision/retry using Customer command or return recoverable `not_provisioned` according to orchestration policy;
- ambiguous historical mapping → exception/manual review;
- destination owner unavailable → no direct foreign write fallback from Customer;
- Customer unavailable → destination fails safely rather than reconstructing buyer identity from User metadata;
- duplicate mapping/backfill job → harmless/idempotent.

### Tests

- Gig contract with valid/mismatched Customer actor;
- Order contract with valid/mismatched Customer actor;
- Booking hold/lock/booking contract with valid/mismatched actor;
- post-cutover null/actor requirement according to approved destination contracts;
- legacy record compatibility fixtures;
- Customer backfill/reconciliation replay/resume;
- ambiguous mapping manual-review path;
- test Customer code imports no destination repositories;
- Track unavailable does not break Customer resolution itself;
- load/query test for actor resolution hot path;
- cross-Cluster E2E: authenticated User → resolved CustomerProfile → destination owner record.

### Documentation Updates

Before enforcing cutover:

- resolve U-CL01-04 in CL-01 and affected destination architectures;
- document which records require both User and CustomerProfile and why;
- document migration/backfill ownership per destination;
- update public interface versions if DTO requirements change.

### Acceptance Criteria

- all enabled buyer-side consumers use SH-004/public Customer contract rather than direct CustomerProfile reads;
- mismatched pairs are rejected;
- no Customer foreign lifecycle repository/write exists;
- destination owners control their own schema/migrations;
- no ambiguous mapping is guessed;
- new-record actor rule matches the approved cutover architecture.

### Exit Gate

Before Feature 06:

- U-CL01-04 is resolved and documented for every enabled destination;
- Customer-owned contribution to CL-01 Feature 13 contract tests passes;
- Gig/Order/Booking positive and negative contract tests pass;
- backfill/reconciliation is resumable and exception-safe;
- no Customer direct foreign write is required to make integration tests pass;
- typecheck/lint/build pass;
- progress tracker reflects cutover status and remaining destination work.

---

# Phase 5 — Privacy, Audit, Notification, Hold, and Operational Bridges

## 06 Customer Privacy Inventory/Executor and Support-Rail Integration

### Objective

Make CustomerProfile fully participate in Privacy-owned export/erasure/retention execution and canonical Audit/Notification/Hold/Ops support rails without creating parallel workflows or allowing support records to replace Customer truth.

### Observable Result

- A Privacy test harness can enumerate Customer-owned data, request a Customer target disposition, and receive a standardized Customer execution result.
- Retention/exemption instructions are honored without Customer inventing legal policy.
- Avatar reference handling is separated from Media object deletion.
- Required material admin/privacy actions create Audit evidence through the owner.
- Sensitive profile access can create AccessAuditLog where policy requires.
- Operational failures are visible without changing CustomerProfile status.

### Cluster Build-Plan Link

Direct Customer-owned contribution to **CL-01 Feature 15 — Privacy, Holds, Audit, Notification, and Operational Support Bridges**.

### Dependencies

- Module Features 02–05 as applicable;
- Privacy SH-095–098 contracts;
- Audit SH-029/030;
- Notification SH-041;
- Ops SH-032–039;
- Hold SH-011 if an enabled Customer command is hold-sensitive;
- Media privacy/public contract for avatar object effects;
- **CBP-U-04** must be resolved before destructive erase/delete behavior is enabled;
- root sensitive-access/step-up matrix for applicable admin/privacy actions.

### In Scope

- Customer implementation of SH-096 `enumerateSubjectData`;
- Customer export fragment serializer;
- Customer retention-facts response under SH-097;
- Customer implementation of SH-095 `executePrivacyInstruction`;
- approved SH-098 anonymization field mapping;
- avatar reference detach/suppress behavior under instruction;
- call/coordination boundary to Media for separate asset privacy target where required;
- Audit/AccessAudit integration for material/sensitive actions;
- Notification intent for approved profile/privacy lifecycle notices;
- Ops failure/queue telemetry;
- cascade-delete safety tests.

### Out of Scope

- PrivacyRequest/DataErasureJob/DataErasureTarget/DataRetentionExemption lifecycle;
- user-facing privacy request UI;
- legal determination of retention duration/exemption;
- hard-deleting foreign Orders/Gigs/Bookings/Reviews/Disputes;
- MediaAsset object deletion implementation;
- Notification provider delivery;
- Audit/AccessAudit persistence implementation;
- ComplianceHold lifecycle;
- Search removal for CustomerProfile while public indexing remains disabled.

### Module-Owned Data

Customer privacy inventory includes:

```text
CustomerProfile.id
CustomerProfile.userId
status
approved personal display metadata
avatarMediaId reference
createdAt
updatedAt
archivedAt
```

The exact personal-field list must follow the final field-precedence decision.

### Public Interfaces

Implement owner-side protocol contracts:

```text
enumerateSubjectData                # SH-096 Customer implementation
buildCustomerProfileExportFragment  # Privacy export contribution
provideCustomerRetentionFacts       # SH-097-compatible
executeCustomerProfilePrivacyInstruction  # SH-095 implementation
```

The exposed protocol must use Privacy-defined target/result shapes, not a Customer-specific parallel workflow.

### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-095 `executePrivacyInstruction` | Privacy protocol / Customer execution | target executor | Customer field/row disposition | Customer privacy workflow |
| SH-096 `enumerateSubjectData` | Customer under Privacy contract | inventory/export | Customer-owned records only | global data crawler |
| SH-097 `evaluateRetentionRequirement` | owner facts + Privacy exemption | before destructive action | Customer/open-obligation facts | local retention-exemption table |
| SH-098 `anonymizePersonalFields` | shared primitive | anonymization | approved Customer field map | ad hoc scrubber |
| SH-044 | platform | executor idempotency | target/instruction semantic key | local idempotency |
| SH-047/048 | platform | durable privacy retry if async | Customer retry classification | local job runner |
| SH-029 | Audit | destructive/material execution | action/outcome/ref | Customer audit table |
| SH-030 | Audit | sensitive export/admin access | sensitivity/purpose | Customer access log |
| SH-041 | Notification | only approved user-facing notice | safe trigger/variables | Customer mail/SMS |
| SH-011 | Hold owner | only if specific Customer action policy requires | action-specific hold composition | Customer blocked field |
| SH-032–039 | Ops/platform | correlation/log/failure/queue/health | safe IDs/results | local Ops store |
| SH-090 / Media owner privacy contract | Customer/Media split | detach avatar + separate asset target | Customer relation vs Media object | Customer object deletion |

### Domain Logic

#### Inventory/export

- enumerate only Customer-owned data;
- return stable IDs/references and purpose-limited values;
- do not traverse foreign lifecycle records and bundle them as Customer ownership;
- Privacy combines fragments from all owners.

#### Retention

- Customer supplies facts it owns;
- open external obligations are queried from their owners where the approved retention policy needs them;
- Privacy records the exemption/decision;
- Customer returns `retained`/`anonymized`/other standardized result with reference.

#### Erasure/anonymization

- do not hard delete if the approved instruction/exemption requires retention;
- anonymize only the approved Customer field map;
- preserve relational integrity required for retained foreign references;
- clearing `avatarMediaId` does not delete the MediaAsset;
- actual Media deletion is performed by Media under its Privacy target;
- if policy cannot determine safe disposition, return review/retained rather than guessing.

#### Cascade protection

A generic hard-delete of User must not become a shortcut around Customer executor and retention evaluation.

### Authorization / Compliance

- only trusted Privacy workflow context invokes destructive executor;
- manual admin retry requires SH-002 and step-up if root policy says so;
- sensitive exports/access are audited via SH-030;
- no raw personal data in Ops logs;
- hold state does not automatically rewrite CustomerProfile status;
- privacy result is not a Customer-generated final PrivacyRequest completion.

### Database / Transaction Behavior

- each privacy target execution is idempotent;
- mutation of Customer fields/row occurs in an owner transaction;
- audit/outbox atomicity follows root policy; if audit is post-commit durable side effect, failure is retried and does not reverse source state by default;
- anonymization must preserve uniqueness/foreign-key integrity;
- hard-delete path remains disabled until CBP-U-04 and cascade ordering are approved/tested;
- no direct foreign-row delete/update.

### Events / Jobs

- privacy executor may run through SH-047 when Privacy uses durable owner jobs;
- retries use SH-048 and return standardized retryable/terminal results;
- optional Customer privacy-disposition event only if a real consumer requires it;
- no Search deindex event for CustomerProfile under current no-public-indexing rule.

### Provider Integration

None in Customer. Media/provider deletion is delegated to Media/provider owner.

### UI / Admin Surface

No standalone Customer privacy UI. Privacy/admin workflow owns request presentation.

Optional operator/debug view may show safe target/executor outcome references through Privacy/Ops, not raw subject data.

### Failure Behavior

- duplicate executor call → same semantic result/no repeated destructive side effect;
- retention exemption → retained/anonymized result, no silent delete;
- unknown disposition or unresolved CBP-U-04 → review/unsupported, no destructive action;
- Media dependency unavailable for required avatar effect → return partial/retryable according to Privacy protocol; do not claim completion;
- Audit/Notification transient failure after Customer source commit → retry side effect according to owner policy;
- Ops failure never changes Customer status;
- open-obligation owner unavailable when required for retention → fail closed/retryable, not guess.

### Tests

- SH-096 Customer inventory contract;
- export fragment contains Customer-owned fields only;
- foreign Gig/Order/Booking data excluded;
- approved anonymization map;
- retention exemption/retained result;
- duplicate executor replay;
- avatar detach vs Media deletion separation;
- Media unavailable retry/partial path;
- cascade-delete protection from User;
- sensitive access audit;
- Audit/domain truth separation;
- notification ownership test;
- Ops failure does not change CustomerProfile status;
- test no PrivacyRequest/DataErasureJob table is created/owned here.

### Documentation Updates

Before destructive behavior:

- resolve CBP-U-04 in Module/CL-01/Privacy architecture;
- document field-by-field disposition and referential strategy;
- document hard-delete orchestration ordering across User/Customer/foreign records;
- record sensitive-access and step-up matrix if settled.

### Acceptance Criteria

- Privacy can enumerate and execute the Customer target via typed owner interfaces;
- Customer owns only its fragment/execution, not parent privacy lifecycle;
- retention/exemption is respected;
- avatar object deletion stays Media-owned;
- no uncontrolled User cascade bypass exists in production paths;
- required audit/access proof is separate from Customer truth;
- no local Notification/Hold/Ops implementation exists.

### Exit Gate

Before hardening Feature 07:

- Customer contribution to CL-01 Feature 15 passes privacy/support contract tests;
- destructive paths are either architecture-approved and fully tested or remain disabled;
- no local privacy/audit/hold/notification/ops duplicate exists;
- sensitive data logging scan passes;
- typecheck/lint/build pass;
- progress tracker records any retained unresolved privacy decisions.

---

# Phase 6 — Module Hardening and Production Verification

## 07 Customer Actor Reconciliation, Security, Concurrency, Privacy, and Production Hardening

### Objective

Prove the Customer Module is safe under retries, race conditions, legacy migration, dependency degradation, privacy constraints, and production load without adding new product scope or absorbing foreign ownership.

### Observable Result

- concurrent/replayed provisioning and profile mutations preserve all invariants;
- customer actor backfills are resumable and report all unexplained mismatches;
- no production path bypasses Customer/Privacy through cascade deletion;
- dependency outages fail safely;
- public Customer interfaces meet expected latency/query plans;
- operator-safe diagnostics identify Customer backfill/contract failures without leaking PII;
- critical Customer participation E2E journeys pass against production-like infrastructure.

### Cluster Build-Plan Link

Customer-owned portion of **CL-01 Feature 16 — Security, Concurrency, Reconciliation, Backfill, and Production Hardening**. It also verifies the Customer boundaries established in CL-01 Features 05, 06, 13, and 15.

### Dependencies

- exit gates for all production-enabled prior Module features;
- all architecture decisions required by enabled paths resolved;
- production-like Postgres/RLS environment;
- shared queue/outbox/Ops/Audit/Privacy infrastructure;
- production contract versions for Identity/Role/Media and enabled Gig/Order/Booking consumers;
- migration rollback/backfill strategy;
- security/privacy review.

### In Scope

- concurrency stress for provisioning/update/status if enabled;
- idempotency/event replay suite;
- backfill/reconciliation restart and poison-item handling;
- User/Profile/destination mismatch reporting;
- final query/index/performance review;
- RLS/server authorization parity for CustomerProfile;
- privacy/cascade/delete review;
- telemetry redaction and sensitive-access coverage;
- dependency degradation tests;
- event/outbox/queue dead-letter recovery;
- production-safe operator diagnostics through Ops;
- final boundary/import audit;
- migration safety checks.

### Out of Scope

- new public buyer search;
- new Customer plan/pricing system;
- new lifecycle semantics not already approved;
- organization commercial plans;
- new provider choice;
- refactoring Gig/Order/Booking simply to make Customer cleaner;
- Review/Dispute direct CustomerProfile migration unless U-CL01-07 has been separately approved and scheduled.

### Module-Owned Data

Review/tune existing CustomerProfile data only:

- unique `userId`;
- status/index usage;
- `(city,state,country)` index only where legitimate query requires it;
- update/concurrency mechanism;
- archivedAt consistency if lifecycle enabled;
- avatar reference integrity checks;
- retention-safe delete behavior.

Any new column/index must be justified by an owned query/invariant and reviewed through architecture/migration standards.

### Public Interfaces

No new broad API by default. Harden:

- `provisionDefaultCustomerProfile`;
- SH-004 `resolveCustomerActor`;
- `assertCustomerActorConsistency`;
- `getCustomerProfile`;
- metadata/avatar commands;
- enabled status commands;
- SH-095/096/097 Customer privacy implementations;
- admin-safe reconciliation diagnostics if approved.

### Shared Operations Used

Hardening focuses on previously consumed canonical operations, especially:

- SH-001/002/003/004;
- SH-029/030/032–038;
- SH-044–053;
- SH-082–090 for avatar boundary;
- SH-095–098 for privacy;
- SH-114 for provisioning.

Do not create new shared operations merely to make tests convenient.

### Domain Logic

#### Concurrency

- effectively-once provisioning under parallel calls;
- deterministic stale-update conflict;
- if lifecycle enabled, one valid status transition wins and the loser gets conflict;
- no in-memory lock dependence.

#### Reconciliation/backfill

- compare Customer one-to-one truth to approved Identity source and owner-supplied destination references;
- never silently remap a historical foreign record;
- every mismatch categorized: missing CustomerProfile, wrong pair, duplicate-impossible/invariant breach, legacy-null, destination conflict, unknown/manual review;
- replay/restart does not lose or duplicate progress;
- foreign repair is handed to the owner.

#### Security

- every protected path resolves actor and authorizes server-side;
- public DTOs are purpose-limited;
- no provider secrets/storage keys/entitlement payloads leak;
- rate-limit abusive public mutation/read surfaces using root infrastructure.

#### Privacy

- no hard-delete shortcut;
- destructive behavior matches approved disposition;
- logs and operator diagnostics exclude personal values;
- export/access audit coverage verified.

### Authorization / Compliance

Final review must cover:

- self/admin/support action matrix;
- RLS parity with service authorization;
- trusted system/event provisioning caller;
- Privacy executor caller authenticity;
- step-up for any enabled high-risk admin/destructive action;
- sensitive profile access logging;
- ComplianceHold composition only where approved;
- no Customer premium/payment/foreign readiness policy.

### Database / Transaction Behavior

- run migration from clean database and representative pre-Customer/legacy data;
- test unique constraint under load;
- verify query plans for resolver (`userId`) and profile-by-ID reads;
- review all cascades involving User and CustomerProfile;
- validate any accepted downstream migrations are owner-managed and do not require Customer direct writes;
- backfill batch size/checkpoint/retry policy must avoid long unbounded transactions;
- destructive migration requires backup/rollback/verification plan.

### Events / Jobs

- event replay/DLQ re-drive with SH-045/044 idempotency;
- backfill resume after worker crash;
- correlation IDs from request → outbox → job → owner call;
- poison items isolated;
- queue telemetry and IntegrationFailure emitted safely;
- no exactly-once claim; prove effectively-once domain effects.

### Provider Integration

No Customer provider. Simulate dependency failure through public contracts:

- Identity unavailable;
- Role unavailable;
- Media unavailable;
- Privacy/Ops/Audit/Notification unavailable according to side-effect policy;
- Gig/Order/Booking consumer unavailable during integration tests.

Customer must never fall back to direct provider or foreign database access.

### UI / Admin Surface

Production-safe operator diagnostics may expose:

- CustomerProfile backfill counts;
- mismatch categories;
- dead-letter/retry references;
- dependency health references;
- correlation IDs.

They must not expose raw profile PII or become a source-truth editor.

### Failure Behavior

Document/test explicit outcomes for:

- database conflict/serialization failure;
- duplicate command/event;
- missing CustomerProfile after expected provisioning;
- wrong User/Profile pair;
- Identity/Role dependency outage;
- Media outage during avatar change;
- Privacy executor retryable/terminal/retained result;
- Audit/Notification/Ops outage after source mutation;
- dead-lettered backfill/event;
- invalid legacy mapping;
- schema/migration mismatch;
- public profile/search request while disabled.

Each must produce deny, unavailable, retry, conflict, retained, manual review, or eventual side-effect retry. Avoid generic uncontrolled 500 paths for expected business/integration failure classes.

### Tests

- full Customer unit suite;
- public contract suite;
- database integration suite;
- RLS/authorization parity suite;
- parallel provisioning stress;
- optimistic concurrency stress;
- lifecycle transition stress if enabled;
- event replay/dedupe/outbox recovery;
- backfill checkpoint/resume/dead-letter;
- legacy User/Profile/destination reconciliation;
- privacy/retention/cascade suite;
- Media contract/degradation suite;
- Audit/sensitive-access/telemetry-redaction suite;
- performance/load test for SH-004 hot path;
- migration clean DB + representative legacy DB;
- critical E2E:
  - User creation → CustomerProfile provision → resolve;
  - owner profile edit/avatar if enabled;
  - Customer actor → Gig/Order/Booking contract after cutover;
  - Privacy target → Customer result;
- production build.

### Documentation Updates

- update progress tracker with production-readiness state;
- update architecture for any legitimate approved final decision that changed implementation;
- record migration/backfill runbook and reconciliation categories;
- document dependency-degradation behavior and operator remediation;
- ensure shared-operation references match canonical registry IDs.

### Acceptance Criteria

- one CustomerProfile per User holds under concurrency/replay;
- no unexplained Customer actor mismatch remains before a mandatory cutover is declared complete;
- all enabled public contracts have positive/negative integration tests;
- no Customer code owns foreign lifecycles/providers/shared infrastructure;
- privacy destructive paths are approved and safe, or remain disabled;
- RLS/server authorization parity passes;
- telemetry contains no prohibited personal/provider data;
- SH-004 meets launch performance expectations on representative data;
- dead-letter/retry/backfill recovery is demonstrated;
- all required quality checks pass.

### Exit Gate

The Customer / Buyer Profile Module is production-ready only when:

- every unresolved decision affecting an enabled path is resolved and architecture updated;
- all Module Features required by the current Cluster milestone have passed their exit gates;
- canonical shared operations are reused with no prohibited local duplicates;
- CustomerProfile uniqueness/consistency/concurrency invariants hold under stress;
- actor cutover has no unexplained mismatch for the scope declared complete;
- privacy/retention/cascade behavior is explicitly approved and tested;
- Media/avatar boundary is intact;
- public Customer search remains disabled unless a separate approved feature supersedes that ruling;
- authorization/RLS/security review passes;
- unit, contract, integration, migration, privacy, RLS, E2E, load, typecheck, lint, and production build checks pass;
- progress and architecture documents agree with the implementation.

---

# Module Integration Phase

Module Feature 05 is the explicit customer-actor integration phase. Feature 06 adds support-rail integration. Integration tests must prove public contracts rather than foreign repository access.

Minimum integration set:

```text
Identity & Access
  → trusted User / User-provisioned fact
  → Customer provision/resolve

Customer / Buyer Profile
  → SH-004 buyer actor
  → Gig / Demand
  → Transaction / Order
  → Booking & Calendar

Customer profile edit
  → Role authorization
  → Media validation/access for avatar

Privacy / Data Erasure
  → Customer SH-096 inventory
  → Customer SH-095 execution
  → standardized result back to Privacy

Customer material/sensitive action
  → Audit / Notification / Ops through canonical interfaces
```

Contract proof must include negative cases:

- wrong User/Profile pair;
- unauthorized profile edit;
- missing CustomerProfile;
- Media asset unready;
- downstream dependency unavailable;
- privacy retention exemption;
- duplicate event/command.

No integration test should need direct mutation of another Module's internal repository solely to make the Customer workflow pass.

---

# Module Hardening Phase

Feature 07 is the hardening phase. It is not a catch-all for unfinished feature logic.

Hardening covers only approved/current behavior:

- one-to-one provisioning races;
- command/event replay;
- stale writes and status races where lifecycle is enabled;
- RLS/authorization parity;
- privacy/cascade restrictions;
- Media boundary degradation;
- actor backfill/reconciliation;
- event/job dead-letter recovery;
- audit/access proof completeness;
- telemetry redaction;
- query/index performance;
- migration/backfill safety;
- production dependency degradation.

Unresolved public visibility, Review/Dispute direct references, or new commercial features do not become hardening tasks.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Source-of-Truth and Contract Foundation | 01–02 |
| 2 | Protected Profile Management and Media Boundary | 03 |
| 3 | Architecture-Gated CustomerProfile Lifecycle | 04 |
| 4 | Cross-Cluster Customer Actor Contract Proof | 05 |
| 5 | Privacy, Audit, Notification, Hold, and Operational Bridges | 06 |
| 6 | Module Hardening and Production Verification | 07 |

**Total numbered features: 7**

Feature 04 remains explicitly gated until the Cluster architecture resolves its lifecycle decisions. Its presence in this Module plan documents required Customer-owned work; it does not authorize the feature to be implemented out of CL-01 sequence.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root `project-overview.md` and root architecture/standards.
2. Read the Canonical Shared Operations Registry.
3. Read CL-01 `architecture.md` and `build-plan.md`.
4. Read this Module architecture and implementation plan.
5. Read the public-interface sections for direct dependencies named by the feature.
6. Inspect the current Prisma schema/migrations for affected Customer data.
7. Confirm the prior Module feature exit gate and the parent CL-01 milestone permits this work.
8. Confirm every listed architecture gate is resolved or the feature is intentionally limited to its safe subset.
9. Produce the concise Required Feature Implementation Specification below.
10. Implement only that feature.
11. Run the feature's quality checks/tests plus root-required commands.
12. Verify public contracts and negative paths.
13. Inspect changes for foreign ownership/shared-operation duplication.
14. Update progress.
15. Update architecture only when a binding decision legitimately changed and was approved.
16. Record unresolved risks/deferred work.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a short feature-specific specification containing:

- **Objective** — one outcome only.
- **Observable result** — what will be visibly/testably different.
- **Cluster link** — exact parent CL-01 feature/milestone and whether any gate applies.
- **Dependencies** — prior Module features, public owner contracts, schema/migration prerequisites, shared operations.
- **In scope** — concrete files/services/contracts/tests.
- **Out of scope** — neighboring ownership and deferred behavior.
- **Owned data affected** — CustomerProfile fields/events only.
- **Public contracts** — commands/queries/events/privacy interfaces changed.
- **Shared operations consumed** — permanent SH IDs, invocation, local policy, prohibited duplicate.
- **Permissions/compliance** — actor, Role action, hold/step-up/privacy/sensitive-access behavior as applicable.
- **Primary workflow** — step-by-step request → policy → source write/read → effects.
- **Provider integration** — normally “none”; list dependency owner contracts instead.
- **Jobs/events** — idempotency, dedupe, retry/dead-letter/correlation.
- **Idempotency/concurrency** — semantic key, transaction boundary, unique constraint/version/lock strategy.
- **Error behavior** — validation, authorization, not-found, mismatch, conflict, dependency, retryable/terminal.
- **Tests** — exact unit/contract/db/auth/privacy/E2E cases for this slice.
- **Acceptance criteria** — objective, observable checks.
- **Documentation updates** — progress and any architecture changes required before/after implementation.

Do **not** generate implementation specifications for all future features in advance. Generate the specification immediately before the feature is implemented so it reflects current repository state and settled decisions.

---

# Required Completion Report

After each numbered feature, the coding agent must report:

- **Feature completed** — number and name.
- **Files added**.
- **Files changed**.
- **Database changes**.
- **Migrations** — name/status or “none”.
- **Dependencies added** — normally none unless root architecture explicitly approves.
- **Module public interfaces added/changed**.
- **Shared operations reused** — permanent SH IDs.
- **Events/jobs added**.
- **Provider adapter changes** — normally none; identify dependency contract changes instead.
- **Tests added/changed**.
- **Commands run** — typecheck/lint/tests/build/migration checks as applicable.
- **Manual/contract verification**.
- **Documentation updated**.
- **Assumptions**.
- **Known failures**.
- **Remaining risks**.
- **Deferred work**.
- **Exit-gate result** — PASS or FAIL with exact failing condition.

A feature marked complete with a failed exit gate is not complete.

---

# Final Quality Check

Before declaring the Module implementation plan satisfied, verify:

1. `CustomerProfile` has exactly one source owner.
2. `User` remains Identity-owned account truth.
3. No Gig/Order/Booking/Review/Dispute/Track/Media/Privacy lifecycle has been absorbed into Customer.
4. SH-004 is the canonical buyer actor boundary and downstream consumers do not rebuild it.
5. User/Profile consistency is enforced anywhere both identifiers are supplied.
6. Track commercial policy is consumed externally and no local premium truth exists.
7. Order/Booking historical snapshots remain destination-owned.
8. MediaAsset/file mechanics remain Media-owned and avatar attachment uses the canonical boundary.
9. Public CustomerProfile search remains disabled unless a later approved architecture explicitly supersedes it.
10. Privacy orchestration remains Privacy-owned and Customer executes only CustomerProfile data.
11. Audit, domain events, and observability remain distinct.
12. No provider adapter was invented for Customer.
13. All status transitions in production are backed by an approved Customer transition matrix.
14. Every shared operation is consumed rather than duplicated.
15. Every cross-Module read/write uses the approved public owner boundary unless an explicit root exception exists.
16. Concurrency relies on database/shared primitives, not in-memory locks.
17. Backfill/reconciliation is resumable and never guesses ambiguous identity mappings.
18. Destructive cascades cannot bypass Privacy/retention review.
19. Every numbered feature has tests and a passed exit gate before dependent work proceeds.
20. The implementation still matches the parent CL-01 build sequence and does not silently move Cluster milestones.
21. A coding agent can execute the next approved feature without inventing architecture.
