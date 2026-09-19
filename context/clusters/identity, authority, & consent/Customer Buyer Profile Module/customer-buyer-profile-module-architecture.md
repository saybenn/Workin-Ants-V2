# Customer / Buyer Profile Module Architecture

> **Module ID:** `customer_buyer_profile`  
> **Module name:** Customer / Buyer Profile Module  
> **Module type:** `domain_actor_profile`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-module-architecture.md`\
> **Document status:** Implementation-grade target Module architecture for the Workin Ants MVP  
> **Audience:** coding agents, developers, reviewers, maintainers, security/privacy reviewers, and architecture reviewers

Evidence labels used below:

- **Confirmed** — directly supported by the current Deep Module Registry, Cluster Registry, Prisma schema, Cluster architecture/build plan, Canonical Shared Operations Registry, or repeated Module evidence.
- **Proposed Ruling** — an implementation-grade ruling strongly supported by the evidence but not yet fully settled by all authoritative sources.
- **Unresolved** — a real architecture question that must not be guessed in code.

---

## 1. Module Header

### Relationship to root architecture

This file is subordinate to the Workin Ants root architecture, project overview, code standards, and global build plan. Root decisions control platform-wide technology, repository conventions, validation, security, database, observability, and delivery mechanics.

This file may narrow those decisions for `customer_buyer_profile`; it may not redefine them.

### Relationship to CL-01 architecture

This Module is one of five Deep Modules in CL-01. CL-01 coordinates identity, authority, consent, buyer actor identity, and commercial entitlement policy but does not become a source-of-truth owner. The Customer / Buyer Profile Module remains the sole owner of `CustomerProfile` buyer-actor truth.

The current Cluster architecture establishes these binding boundaries:

```text
Identity & Access proves who the User is.
Role / Authority interprets what that actor may attempt.
Customer / Buyer Profile resolves the buyer actor branch.
Consent & Disclosure proves exact accepted disclosure/version.
Track Subscription & Entitlement owns commercial plan/perk/quota truth.
The downstream business Module still owns its own lifecycle.
```

### Update rule

Update this file whenever a binding decision changes CustomerProfile ownership, lifecycle semantics, provisioning, public contracts, privacy disposition, avatar/media boundary, public visibility, downstream actor cutover, or source-field precedence.

Implementation progress must not silently redefine this architecture. If implementation reveals a real architecture change, update the governing architecture first, then continue.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Create and maintain the default buyer/customer actor identity that branches one-to-one from a base `User`, so customer-side marketplace activity can refer to a stable commercial actor without overloading account/authentication identity.

### Goal

Ensure every eligible Workin Ants User can operate through one `CustomerProfile` while keeping authentication, authority, Track subscription/entitlement policy, Gigs, Orders, Bookings, reviews/disputes, delivery access, payments, location reveal, media mechanics, privacy orchestration, search, and notification delivery in their owning Modules.

### What enters

The Module may receive:

- a valid Workin Ants `User` identity or User-provisioned domain event from Identity & Access;
- an authenticated actor context from Identity & Access;
- an optional expected `customerProfileId` supplied by a downstream customer-side workflow;
- validated owner/admin profile-edit commands;
- references to MediaAssets for avatar attachment after Media validation;
- Privacy-owned target instructions for CustomerProfile export/anonymization/erasure/archive execution;
- owner facts or status references required only to protect Customer-owned transitions;
- existing CustomerProfile rows during backfill/reconciliation.

### What leaves

The Module exposes:

- one authoritative `CustomerProfile` for an eligible User;
- canonical buyer actor resolution through `SH-004 resolveCustomerActor`;
- a User/CustomerProfile consistency decision;
- safe owner/admin profile views;
- approved Customer-owned metadata updates;
- the contextual relationship “this validated MediaAsset is this CustomerProfile's avatar”;
- CustomerProfile-specific lifecycle results once the lifecycle matrix is approved;
- Customer-owned privacy inventory/export/execution results;
- minimized domain events when durable downstream notification is required;
- reconciliation/backfill outcomes for CustomerProfile actor migration.

### Business transformation

```text
eligible User account
→ Customer-owned one-to-one profile provisioning
→ stable CustomerProfile buyer actor
→ validated actor/profile consistency
→ downstream business owner receives buyer identity
```

For protected profile management:

```text
authenticated actor
→ Role authorization
→ Customer-owned field/status policy
→ Media validation if avatar changes
→ authoritative CustomerProfile mutation
→ optional event/audit/notification effects through canonical owners
```

### Why this deserves its own Module boundary

`User` is account identity, not buyer-domain identity. Customer behavior also must not be conflated with Professional, Candidate, or Organization authority. A dedicated buyer actor lets Gigs, Orders, Bookings, delivery, and commercial entitlement consumers refer to a stable customer identity while preserving clean lifecycle ownership elsewhere.

---

## 3. Owned Truth

### 3.1 Schemas/models owned

| Record | Ownership | Plain-English meaning |
| --- | --- | --- |
| `CustomerProfile` | **Confirmed source truth** | The one-to-one buyer/customer actor branch attached to a Workin Ants `User`. It identifies who is acting as the customer in customer-side marketplace flows. |

### 3.2 Enums/statuses owned

`CustomerProfile.status` currently uses the Prisma enum `ProfileStatus` with values:

```text
draft
active
paused
suspended
archived
```

The Module **owns the meaning and transition policy of these values when applied to `CustomerProfile`** under CL-01 Proposed Ruling `PR-CL01-03`.

The ownership of the shared `ProfileStatus` enum definition itself is **Unresolved (`U-CL01-20`)** because the current registry and glossary conflict. Coding agents must not claim the enum definition for this Module or migrate it merely to make ownership cleaner.

### 3.3 Lifecycles owned

- CustomerProfile existence/provisioning lifecycle.
- CustomerProfile-specific status lifecycle, **but production transitions beyond initial `active` creation remain architecture-gated by `U-CL01-21`**.
- CustomerProfile archive/restore semantics, once the transition matrix is approved.

### 3.4 Source-of-truth records

`CustomerProfile` is authoritative for:

- stable `customerProfileId`;
- one-to-one `userId` binding;
- CustomerProfile status as applied to the buyer actor;
- Customer-owned display metadata once field precedence is settled;
- avatar business-reference meaning (`avatarMediaId`), not file truth;
- coarse CustomerProfile city/state/country metadata, subject to the unresolved User-vs-profile precedence rule;
- `createdAt`, `updatedAt`, and `archivedAt` as profile record facts.

### 3.5 Domain events/ledgers owned

No dedicated persisted CustomerProfile lifecycle ledger is confirmed in the current Prisma schema.

The Module may emit minimized owner events through the canonical outbox when consumers require durable delivery. Candidate event semantics include:

- CustomerProfile provisioned;
- CustomerProfile metadata updated;
- CustomerProfile status changed;
- CustomerProfile archived/restored;
- CustomerProfile privacy disposition applied.

**Proposed Ruling CBP-PR-01:** these are integration/domain facts emitted by the Customer owner through `SH-046 publishDomainEvent`; they do not justify creating a new `CustomerProfileEvent` table unless a later architecture decision establishes a durable owner-specific history requirement.

### 3.6 Projections owned

The registry historically lists a “customer-facing commerce history projection.” Current shared-operations synthesis separately flags the canonical owner of a cross-Module customer aggregate read model as unresolved.

Therefore:

- no durable Customer commerce-history projection is currently owned by this Module;
- no copied Gig/Order/Booking/Review/Dispute status may be stored on `CustomerProfile`;
- a future read model may compose owner interfaces under an approved projection owner, but that decision is **Unresolved**.

### 3.7 Snapshots/proof owned

This Module owns no fee-waiver, priority-scheduling, paid-order, payment, download, playback, consent, verification, or location-reveal snapshot.

It may return actor-consistency proof/decision data showing that a `userId` and `customerProfileId` belong together.

### 3.8 Policies/invariants owned

Customer / Buyer Profile owns:

- one CustomerProfile per User;
- CustomerProfile provisioning eligibility after a valid User exists;
- User/Profile consistency rules;
- which CustomerProfile fields are editable by self/admin after precedence decisions are approved;
- avatar attachment context after Media validates the asset;
- CustomerProfile-specific status transitions once `U-CL01-21` is resolved;
- Customer-owned privacy field mapping and execution behavior under Privacy instructions.

---

## 4. Explicit Non-Ownership

The Module must not own or duplicate the following:

| Adjacent owner | Responsibility that remains outside Customer / Buyer Profile |
| --- | --- |
| Identity & Access | `User`, authentication, provider accounts, sessions, passwords, passkeys, MFA/step-up, account recovery, base security posture. |
| Role / Authority | Generic authorization, platform/organization/participant permissions, owner/admin permission interpretation. |
| Consent & Disclosure | `ConsentLog`, active consent versions, consent acceptance proof and re-consent policy. |
| Track Subscription & Entitlement | Plans, prices, subscriptions, grants, typed entitlements, usage events/counters, premium/fee-waiver/priority policy, billing-provider events. |
| Gig / Demand | Gig, response/assignment, customer demand lifecycle, expiration and assignment truth. |
| Transaction / Order | Order lifecycle, agreements, fee snapshots, refunds, transaction status, historical buyer fee-waiver snapshot. |
| Booking & Calendar | Holds, slot locks, Booking status, priority rank/snapshot, calendar/provider state, scheduling truth. |
| Payment / Payout / Tax | Card/payment method, processor Customer, payment, payout, tax, KYC, financial ledger truth. |
| Digital Goods Access | Download assets/grants/events and delivery entitlement. |
| Video Infrastructure | Course playback/video access grants, video provider state. |
| Media / File Access | MediaAsset lifecycle, upload, validation, malware scan, metadata scrub, storage keys, public/private mechanics, signed URLs. |
| Location Safety | Exact-location encryption/decryption, reveal policy/evidence, fuzzy public coordinate generation. |
| Messaging | Thread/participant/message lifecycle. |
| Notification | Notification persistence, template rendering, channel delivery/retries. |
| Search / Public Visibility | SearchUpsertEvent, search document, provider index, public search execution. CustomerProfile indexing is currently disabled. |
| Review / Dispute | Review and Dispute lifecycle. Direct CustomerProfile references remain unresolved. |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob, DataErasureTarget, DataRetentionExemption, deadline/orchestration/final bundle lifecycle. |
| Admin Review / Compliance Hold | ComplianceHold lifecycle and generic platform stop-sign semantics. |
| Audit / Event Ledger | Generic AuditEvent and AccessAuditLog. |
| Observability / Ops | IntegrationFailure, SystemEvent, QueueJob/incident truth, generic logs/metrics/health. |
| Professional Eligibility | ProfessionalProfile/selling readiness. |
| Candidate Application & Resume Privacy | CandidateProfile/application/resume privacy lifecycle. |
| Organization Hiring | Organization and OrganizationMember/Role lifecycle. |

Concrete prohibitions:

- no `isPremium`, `isHiveClub`, `hasPriorityBooking`, `feeWaived`, `canBuy`, or generic `blocked` fields on CustomerProfile;
- no Stripe Customer/card/payment identifiers treated as CustomerProfile truth;
- no copied Gig/Order/Booking status or balance fields;
- no customer-local auth or permission engine;
- no file scanner/storage/presign implementation;
- no Typesense/search client;
- no PrivacyRequest/erasure-job implementation;
- no generic audit/notification/ops store.

---

## 5. Module Architecture Principles

1. **CustomerProfile is buyer actor truth; User remains account identity.**
2. **One User may have at most one CustomerProfile.** The database uniqueness on `CustomerProfile.userId` is the hard invariant.
3. **Provisioning never depends on Track enrollment.** A buyer actor can exist even if a free/paid Track representation is unavailable or not yet materialized.
4. **Actor resolution is identity context, not marketplace eligibility.** `resolveCustomerActor` must not silently perform entitlement, payment, consent, readiness, or generic hold decisions.
5. **User/Profile consistency is mandatory wherever both IDs are supplied.** Never trust two IDs independently.
6. **Downstream Modules own their records.** Customer provides actor identity; it does not create/mutate Gig, Order, Booking, Review, Dispute, or access-grant truth.
7. **Commercial policy never lives on CustomerProfile.** Use Track public interfaces.
8. **Historical commercial effects stay with the consumer.** Order fee-waiver and Booking priority results are consumer-owned snapshots.
9. **MediaAsset is file truth.** Customer owns only avatar attachment meaning.
10. **Public visibility is fail-closed.** No public CustomerProfile search/index/page is enabled until `U-CL01-22` is resolved and the Cluster/root architecture is updated.
11. **Privacy orchestrates; Customer executes.** The Module handles only its own fields/reference effects.
12. **Status is not a ComplianceHold.** `suspended` or other profile status cannot become a mirror of a platform hold without an explicit approved rule.
13. **No broad generic ProfileService.** Shared profile plumbing may be reused, but CustomerProfile rules stay in this Module.
14. **Cross-Module reads use owner contracts.** Direct foreign repositories are not the default integration path.
15. **High-risk unresolved behavior fails closed.** Do not improvise public visibility, status transitions, destructive erasure, actor cutover, or field synchronization.

---

## 6. Proposed Folder / Code Structure

The absolute repository root must follow the root Workin Ants code convention. The following relative Module boundary is binding regardless of whether the repository places Modules under `src/features`, `server/modules`, or another root-approved container.

```text
<module-root>/customer-buyer-profile/
├── actions/                 # thin first-party UI/server entry points, only if the root app uses actions
├── commands/                # provisioning, metadata/avatar, gated status, privacy execution commands
├── queries/                 # resolveCustomerActor, getCustomerProfile, owner-facts/privacy inventory reads
├── schemas/                 # runtime request/command/query validation schemas
├── domain/
│   ├── policies/            # Customer-specific consistency, editability, lifecycle policy
│   └── results/             # stable decision/result categories
├── repositories/            # CustomerProfile-only persistence access
├── services/                # application orchestration that coordinates Customer truth + approved owner interfaces
├── contracts/               # public Customer DTOs/ports and dependency ports
├── events/                  # Customer-owned event payload definitions/handlers; no generic outbox implementation
├── workers/                 # CustomerProfile backfill/reconciliation consumers only
├── privacy/                 # SH-095/096/097 Customer implementations and export fragment mapping
├── components/              # only genuine account/profile UI owned by this Module
└── tests/                   # unit, contract, db/integration, authorization, privacy, concurrency
```

Do **not** add a `providers/` folder unless a future approved Customer-specific external provider is introduced. None is currently owned.

Do not place shared auth, audit, queue, media, search, notification, privacy orchestration, or generic idempotency infrastructure inside this Module.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery/UI | Customer account/profile presentation, profile edit/Avatar intent forms if product UI exists | Authentication UI, Media upload implementation, public search directory, commerce dashboard lifecycle logic |
| Actions/entry points | Runtime validation, actor/context handoff, delegation to application service | Full workflow logic, direct Prisma, local permission decisions |
| Application services | Coordinate Customer commands/queries and approved shared/owner operations | Foreign lifecycle mutations, generic infrastructure |
| Domain policy | User/Profile consistency, profile field policy, Customer-specific lifecycle rules | Track entitlement, Order/Booking readiness, generic Role permission policy, hold lifecycle |
| Repository/data access | `CustomerProfile` reads/writes only | Gig/Order/Booking/Review/Dispute/Track/Media tables |
| Workers | Existing-user CustomerProfile backfill, Customer-owned reconciliation, incoming event handling | Generic queue runner, foreign actor-reference migration writes |
| Adapters | None currently | Auth, Stripe, storage, Search, notification provider clients |
| Contracts | Customer public interfaces and minimal dependency ports | Provider payload types, universal cross-domain repository |
| Privacy | Customer-owned inventory/export/disposition execution | PrivacyRequest/DataErasureJob orchestration or retention-exemption truth |

---

## 8. Data Model

### 8.1 `CustomerProfile`

**Purpose:** one-to-one buyer/customer identity attached to a base User.

**Key relationships:**

- required `userId` → `User` with a unique constraint;
- source relations from customer-side Gigs, GigAssignments, Orders, BookingHolds, BookingSlotLocks, and Bookings;
- Track subscriptions/grants/usage records may reference CustomerProfile, but Track owns those records;
- `avatarMediaId` is currently a raw UUID reference without an explicit Prisma relation to `MediaAsset`.

**Authoritative fields:**

- `id` — stable CustomerProfile identity;
- `userId` — owning account identity binding;
- `status` — CustomerProfile status value, with Customer-specific policy;
- `displayName`, `city`, `state`, `country` — profile metadata, but edit/synchronization precedence with duplicated `User` fields is unresolved;
- `avatarMediaId` — contextual avatar reference only;
- `createdAt`, `updatedAt`, `archivedAt` — profile record timing facts.

**Lifecycle/status fields:** `status`, `archivedAt`.

**Uniqueness constraints:** `userId` is unique. This is the primary database-enforced one-to-one invariant.

**Indexes:** current schema includes status and `(city, state, country)` indexes. Downstream business records may need their own `customerProfileId` indexes, but those are owned by the respective destination Modules.

**Concurrency-sensitive fields:**

- provisioning by `userId`;
- metadata/avatar mutation under concurrent edits;
- future status/archive/restore transitions.

**Retention/privacy concerns:**

- display/location metadata is personal data;
- avatar reference may point to personal media;
- current User relation uses cascade deletion, which can bypass Customer/Privacy execution if User hard-delete is used indiscriminately;
- production hard-delete must therefore be restricted to the approved Privacy/account lifecycle path.

### 8.2 Foreign customer-side references

The current schema contains both User and nullable CustomerProfile references on several customer-side records. Those dual IDs are migration evidence, not permission for indefinite ambiguity.

The Customer Module owns only the consistency rule. The destination Modules own the fields, nullability migrations, indexes, and business lifecycle.

### 8.3 Review/Dispute

Current Review/Dispute models still use User/Order-based actor references. Whether they should receive direct CustomerProfile references is `Review/Dispute direct CustomerProfile reference decision`; do not add them from this Module plan.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Provisioning lifecycle

The confirmed minimum lifecycle is:

```text
eligible User exists
→ no CustomerProfile
→ provisionDefaultCustomerProfile
→ exactly one CustomerProfile exists (current schema default: active)
```

Replay/concurrent provisioning must converge on the same row.

There is no supported second CustomerProfile for the same User.

### 9.2 `ProfileStatus` values applied to CustomerProfile

Current values:

```text
draft | active | paused | suspended | archived
```

**Transition owner:** Customer / Buyer Profile for CustomerProfile-specific transition policy.

**Valid transitions:** **Unresolved (`U-CL01-21`)**.

**Triggers:** owner/admin commands, and potentially privacy/archive instructions after policy approval. A ComplianceHold does not automatically transition status unless a separate Customer command/policy explicitly says so.

**Terminal states:** unresolved.

**Reversal/reopen rules:** unresolved.

**Concurrency expectations:** once status commands are enabled, every transition must compare expected state/version and update atomically. No read-then-write without conflict protection.

**Event/history proof:** generic AuditEvent may record material admin/status actions, and Customer may emit an outbox fact. A dedicated CustomerProfile event table is not currently approved.

**Prohibited shortcuts:**

- no code path may invent a transition matrix;
- no `status = suspended` mirror of ComplianceHold;
- no archive/delete behavior inferred solely from enum names;
- no downstream Module may change CustomerProfile status directly.

### 9.3 Architecture gate

Production `changeCustomerProfileStatus`, `archiveCustomerProfile`, and `restoreCustomerProfile` commands remain disabled until `U-CL01-20`/`U-CL01-21` and the open-obligation semantics are resolved in architecture.

---

## 10. Commands

### `provisionDefaultCustomerProfile`

- **Purpose:** idempotently ensure one CustomerProfile exists for an eligible User.
- **Actor/context:** trusted Identity/system event or authorized internal post-signup call; not arbitrary client-selected User IDs.
- **Inputs:** `userId`, semantic idempotency key/correlation context.
- **Preconditions:** User exists and is eligible; no conflicting profile binding.
- **Writes:** `CustomerProfile` only.
- **Shared operations:** SH-044, SH-114, SH-046 where event needed; SH-045 if consuming a User-provisioned event.
- **Effects:** optional minimized CustomerProfile-provisioned event; audit only if policy marks provisioning as material.
- **Idempotency:** duplicate command/event returns the same profile rather than creating a second row.
- **Failures:** User missing/ineligible, invariant conflict, database conflict, retryable infrastructure failure.

### `updateCustomerProfileIdentity`

- **Purpose:** mutate only approved Customer-owned display/coarse-location fields.
- **Actor/context:** authenticated owner or authorized admin/support actor.
- **Inputs:** profile ID, allowlisted patch, expected version/timestamp, reason for admin change where policy requires.
- **Preconditions:** SH-001 actor resolution, SH-002 authorization, `U-CL01-22` field-precedence ruling for each editable field.
- **Writes:** CustomerProfile fields only.
- **Shared operations:** SH-001, SH-002, SH-044, SH-052, SH-029 where material.
- **Effects:** optional profile-updated event/notification request when product policy requires.
- **Idempotency:** repeated same semantic mutation does not multiply side effects.
- **Failures:** validation, authorization, stale version, unresolved field ownership.

### `setCustomerProfileAvatar`

- **Purpose:** attach a safe MediaAsset as the CustomerProfile avatar.
- **Actor/context:** owner/admin with profile-update authority.
- **Inputs:** profile ID, `mediaAssetId`, expected version.
- **Preconditions:** actor authorization; Media confirms asset validity/readiness; Customer confirms contextual attachment.
- **Writes:** `avatarMediaId` only.
- **Shared operations:** SH-090 `attachValidatedMedia`; Media operations SH-082/083/084 as owned by Media where required; SH-087 only for display access, never for attachment write itself.
- **Effects:** optional update event/audit.
- **Idempotency:** attaching the same approved asset is safe.
- **Failures:** invalid/unready asset, Media unavailable, authorization failure, stale version.

### `changeCustomerProfileStatus`

- **Status:** architecture-gated.
- **Purpose:** apply one approved CustomerProfile state transition.
- **Preconditions:** `U-CL01-20` and `U-CL01-21` resolved, open-obligation policy approved, authorization/step-up if required.
- **Writes:** `status` and any approved lifecycle timestamps in one transaction.
- **Shared operations:** SH-053 lifecycle transition mechanism, SH-052 concurrency, SH-029 audit, SH-046 event as required.
- **Failure:** unsupported transition must return a stable conflict/denial; never “force” status.

### `archiveCustomerProfile` / `restoreCustomerProfile`

These remain explicit lifecycle commands, not aliases for deletion. Their state/timestamp semantics are gated by the approved transition matrix and privacy/open-obligation rules.

### Customer privacy executor command

- **Purpose:** execute a Privacy-owned instruction against CustomerProfile-owned data only.
- **Actor/context:** trusted Privacy workflow context.
- **Inputs:** privacy target/instruction, subject/profile reference, idempotency key, approved retention-exemption reference if any.
- **Writes:** only CustomerProfile-owned fields/row disposition allowed by the approved instruction.
- **Shared operations:** SH-095, SH-097, SH-098, SH-044; audit/ops as required.
- **Effects:** return standardized owner result to Privacy; Media handling is a separate owner target/call.
- **Failure:** retained, anonymized, skipped, retryable, terminal, or conflict according to Privacy protocol; never invent the parent privacy state.

---

## 11. Queries / Decisions

### `resolveCustomerActor` — SH-004

- **Consumers:** Gig, Order, Booking, Track, Digital Goods, Video, and other buyer-side consumers.
- **Input:** authenticated/trusted `userId`, optional expected `customerProfileId`.
- **Result:** source truth DTO containing `customerProfileId`, `userId`, current CustomerProfile status, and only safe actor metadata needed by the consumer.
- **Type:** source truth / actor context.
- **Must not infer:** subscription, premium status, fee waiver, priority scheduling, payment status, generic authorization, hold clearance, or downstream lifecycle eligibility.

### `assertCustomerActorConsistency`

- **Consumers:** customer-side record creators and migration/reconciliation code.
- **Input:** `userId`, `customerProfileId`.
- **Result:** validated pair or stable mismatch/not-found reason.
- **Type:** decision/evidence.
- **Must not infer:** whether the downstream action itself is allowed.

### `getCustomerProfile`

- **Consumers:** profile owner, authorized support/admin, internal account UI.
- **Input:** requester actor, profile ID/user ID, view purpose.
- **Result:** purpose-limited CustomerProfile DTO.
- **Type:** source truth with presentation filtering.
- **Must not infer:** public discoverability or Media signed URL.

### Customer owner facts query

If Role or another owner requires minimal relationship facts, expose a narrow SH-003-compatible owner-facts DTO rather than direct foreign Prisma access. Example facts may include `customerProfileId`, `userId`, status, and whether requester is the owning User; no Track/commercial facts are embedded.

### Privacy inventory/export query

Implements SH-096 and returns only Customer-owned subject data/references. It must not traverse and serialize foreign Gigs/Orders/Bookings as if Customer owns them.

### Deferred queries

- Customer public profile view — disabled until `U-CL01-22`.
- Customer commerce-history aggregate — owner unresolved; do not implement as a Customer source projection yet.

---

## 12. Public Module Interface

### Public commands

- `provisionDefaultCustomerProfile`
- `updateCustomerProfileIdentity` — only for fields approved by `U-CL01-22` resolution
- `setCustomerProfileAvatar`
- `changeCustomerProfileStatus` — disabled until lifecycle architecture gate resolves
- `archiveCustomerProfile` — disabled until lifecycle architecture gate resolves
- `restoreCustomerProfile` — disabled until lifecycle architecture gate resolves
- Customer implementation of SH-095 `executePrivacyInstruction`

### Public queries

- **SH-004 `resolveCustomerActor`**
- `assertCustomerActorConsistency`
- `getCustomerProfile`
- Customer implementation of **SH-003 `queryOwnerFacts`** when minimum Customer facts are needed
- Customer implementation of **SH-096 `enumerateSubjectData`**
- Customer retention-fact implementation of **SH-097 `evaluateRetentionRequirement`** where Customer is the fact owner
- Customer export fragment query under the Privacy contract

### Emitted domain events

Only when a concrete consumer need exists:

- profile provisioned;
- profile metadata/avatar updated;
- approved status/archive/restore fact;
- privacy disposition fact if useful to downstream owner workflows.

All are delivered through SH-046; event names/payload schemas must be versioned and minimized before code commitment.

### Privacy executor

Customer owns the executor for CustomerProfile data. Privacy owns orchestration and final target state.

### Provider-facing interfaces

None.

---

## 13. Inbound Dependencies

| Owner | Interface / operation | Why required | Minimum information | May block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` + User-provisioned fact | trusted User identity and post-signup trigger | user ID, actor/security context, event ID | Yes for protected actions | session/auth helpers, User lifecycle |
| Role / Authority | SH-002 `authorizeResourceAction` | owner/admin/support protection | actor, action, resource, Customer owner facts | Yes | permission engine, role tables |
| Media / File Access | SH-090 + Media readiness interfaces; SH-087 for display access | safe avatar relation and URL | media ID, readiness/safety/ownership-compatible facts | Yes for avatar change | upload, scan, storage, presign |
| Privacy / Data Erasure | SH-095 protocol + target instruction | legal/privacy execution | target, disposition, retention ref, idempotency/correlation | Yes for destructive action | PrivacyRequest/job/target lifecycle |
| Audit / Event Ledger | SH-029 / SH-030 | generic proof for material admin/sensitive access | safe action/target/outcome metadata | Usually side effect; policy may require atomicity | audit/access tables |
| Notification | SH-041 | user-facing profile/security notice when policy requires | notification intent, recipient ref, safe variables | No for source mutation unless explicit policy says otherwise | templates/provider delivery |
| Observability / Ops | SH-032–038 | request correlation, logs, metrics, failures, queue telemetry | safe IDs/reason codes | No | log/metric/failure stores |
| Admin Review / Compliance Hold | SH-011 when an approved Customer action is hold-sensitive | reusable stop sign | target/action | Yes where policy requires | local blocked flags/hold lifecycle |
| Track Subscription & Entitlement | usually consumed by downstream business owner, not by Customer core | commercial policy context when a Customer-owned UI or future command explicitly requires it | customer actor + entitlement key | Only for that explicit action | plan/grant/usage truth |

Customer provisioning and actor resolution must not be blocked by Track unavailability.

---

## 14. Outbound Consumers and Effects

### Consumers of Customer source truth

- Gig / Demand uses CustomerProfile as customer/poster actor after approved cutover.
- Transaction / Order uses CustomerProfile as buyer actor after approved cutover.
- Booking & Calendar uses CustomerProfile as buyer/scheduling actor after approved cutover.
- Track binds customer-track commercial policy to the Customer actor without transferring profile ownership.
- Digital Goods and Video may resolve the Customer actor for buyer delivery context.
- Media uses Customer context only to support avatar/business attachment access.
- Messaging/Notification may use safe display context, not Customer lifecycle ownership.
- Privacy enumerates/executes Customer targets through Customer interfaces.
- Review/Dispute may consume Customer actor context, but direct FK migration is unresolved.

### Effects

- Domain event publication is an integration signal only.
- Notification is requested through Notification; Customer never sends email/SMS/push directly.
- Audit/access proof is requested through Audit.
- Search projection is currently **not requested** for CustomerProfile because public indexing is disabled.
- Privacy effects are returned to Privacy; Customer does not mark PrivacyRequest/DataErasureTarget itself.

No outbound effect authorizes Customer to mutate another Module’s truth.

---

## 15. Canonical Shared Operations Used

Only operations materially relevant to this Module are listed.

| ID / operation | Classification / owner | Why Customer uses it | Invocation point | Customer-local policy | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | Canonical capability — Identity & Access | trusted account actor | every protected entry | which Customer action is requested | typed User actor context | `customerAuth.ts`, `buyerSessionService.ts`, route-local current-user helper |
| **SH-002 `authorizeResourceAction`** | Cross-cutting capability — Role / Authority | protect self/admin reads/mutations | before protected profile query/command | Customer owner facts + action vocabulary | allow/deny/step-up/review decision | `customerPermissions.ts`, `buyerAcl.ts` |
| **SH-003 `queryOwnerFacts`** | Shared contract / separate implementation — each owner | expose minimum Customer relationship facts | Role/downstream policy lookup | exact Customer fact DTO | minimal immutable owner facts | universal polymorphic repository |
| **SH-004 `resolveCustomerActor`** | Module public interface — Customer / Buyer Profile | canonical User → buyer actor resolution | downstream buyer-side setup | one-to-one binding/status/safe actor metadata | Customer actor truth | `buyerResolver.ts`, `customerContext.ts` in every consumer |
| **SH-011 `evaluateComplianceHold`** | Canonical capability — Admin Review / Compliance Hold | stop an explicitly hold-sensitive Customer command | only where Customer action policy requires | which Customer action/target is hold-sensitive | active hold decision | `customerBlocked.ts`, `isSuspendedForX` |
| **SH-029 `appendAuditEvent`** | Platform audit — Audit / Event Ledger | material admin/status/privacy proof | after/with approved material action | Customer action names + safe metadata | audit reference | `customerAuditService.ts` |
| **SH-030 `recordSensitiveAccess`** | Cross-cutting — Audit / Event Ledger | sensitive profile/admin access if classified | protected read/export/credential issuance | sensitivity and context | access audit proof | `customerAccessLog.ts` |
| **SH-032 `createRequestContext`** | Platform primitive | correlation | request/job entry | safe Customer IDs only | request/correlation context | local correlation helper |
| **SH-033 `writeStructuredLog`** | Platform capability — Ops | operational diagnostics | server/worker path | safe operation/reason fields | structured log | `customerLogger.ts` |
| **SH-034 `sanitizeTelemetryMetadata`** | Cross-cutting — Ops/Audit policy | remove PII/secrets | before logs/audit/failure metadata | sensitivity labels | safe metadata | local sanitizer |
| **SH-035 `captureException`** | Provider adapter — Ops | central exception monitoring | unexpected failure | safe Customer operation context | monitoring reference | local monitoring client |
| **SH-036 `emitMetric`** | Platform capability — Ops | profile/backfill/contract health | command/query/worker metrics | metric names/dimensions | metric emission | local metrics client |
| **SH-037 `recordIntegrationFailure`** | Cross-cutting — Ops | dependency/worker failure evidence | Media/Privacy/event/queue failure | whether Customer truth changed | operational failure ref | local failure table |
| **SH-038 `recordQueueTelemetry`** | Cross-cutting — Ops/queue | backfill/event-worker visibility | async processing | Customer job labels | queue telemetry | local queue dashboard truth |
| **SH-041 `requestNotification`** | Platform capability — Notification | request approved user notice | after approved lifecycle/admin events | trigger and safe variables | notification request ref | customer email/SMS/push service |
| **SH-044 `executeIdempotentCommand`** | Platform primitive | retry-safe provisioning/mutations/privacy | command boundary | semantic Customer command key | previous/new result | `customerIdempotency.ts` |
| **SH-045 `deduplicateDomainEvent`** | Platform primitive | replay-safe User-provisioned/media event consumption | event handler | Customer consumer inbox key | first/replay result | custom processed-event table unless owner-approved |
| **SH-046 `publishDomainEvent`** | Platform outbox primitive | reliable Customer event emission | same transaction as source mutation when required | event schema/payload | outbox/event reference | `customerEventBus.ts` |
| **SH-047 `enqueueReliableJob`** | Platform queue primitive | backfill/reconciliation/privacy retry work | async handoff | job payload/semantic key | durable job ref | customer queue runner |
| **SH-048 `executeRetryWithBackoff`** | Platform primitive | bounded retry | worker dependency failure | retryable vs terminal classification | retry/dead-letter result | local retry loop |
| **SH-051 `acquireAggregateLock`** | Platform persistence primitive | optional serialization of race-prone Customer mutations | only where DB uniqueness/upsert is insufficient | lock key = Customer/User aggregate | lock execution result | in-memory mutex |
| **SH-052 `withOptimisticConcurrency`** | Platform persistence primitive | prevent lost profile updates/status changes | metadata/status mutation | expected version/timestamp | success/conflict | ad hoc stale-write handling |
| **SH-053 `transitionLifecycleState`** | Shared mechanism / separate truth | implement approved CustomerProfile transition matrix | status command after U-CL01-21 | Customer transition policy | valid transition/result | generic profile lifecycle service |
| **SH-082/083/084** | Media capabilities — Media / File Access | validation/scan/scrub as Media requires | avatar upload pipeline, not Customer implementation | Customer only requires a ready attachable asset | Media safety result | avatar validator/scanner |
| **SH-087 `issueSignedMediaUrl`** | Media capability | display private avatar when needed | profile rendering | whether requester may view avatar context | short-lived Media access result | `customerAvatarPresign.ts` |
| **SH-090 `attachValidatedMedia`** | Shared contract / separate contextual truth | attach validated MediaAsset as avatar | avatar command | actor may attach this asset to this profile | contextual attachment decision/write | profile-local file lifecycle |
| **SH-095 `executePrivacyInstruction`** | Privacy protocol / owner execution | perform Customer target disposition | Privacy target command | Customer field/row disposition | standardized owner result | `customerGdprWorkflow.ts` |
| **SH-096 `enumerateSubjectData`** | Privacy protocol | inventory Customer-owned subject data | Privacy discovery/export | Customer-only inventory | stable target refs/metadata | cross-domain export crawler |
| **SH-097 `evaluateRetentionRequirement`** | Privacy protocol | supply Customer retention facts while Privacy owns exemption | before destructive action | Customer/open-obligation facts obtained from owners | retention facts/result | local retention-exemption table |
| **SH-098 `anonymizePersonalFields`** | Shared primitive | apply approved anonymization map | Privacy instruction | Customer field map | anonymized fields | ad hoc scrubbing helper |
| **SH-114 `provisionOneToOneProfile`** | Shared mechanism / separate truth | reuse one-to-one provisioning plumbing | default profile provisioning | Customer eligibility/defaults | one CustomerProfile | generic `profileFactory` owning all profiles |

### Deferred, not currently invoked

- **SH-091 `requestSearchProjectionRefresh`** and **SH-094 `buildSourceProjection`** are not used for CustomerProfile while `U-CL01-22` / PR-CL01-05 keeps public Customer indexing disabled.
- **SH-005 `resolveEntitlement`** is normally consumed by the downstream business action owner. Customer must not wrap it into a local premium service merely because the Customer actor is the subject.

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `normalizeCustomerProfilePatch` | validate/normalize only approved Customer fields | profile patch | normalized patch/errors | none | Customer owns semantics of its metadata |
| `assertCustomerProfileBelongsToUser` | enforce one-to-one pair consistency | userId, profileId | validated pair/denial | none | core Customer invariant |
| `buildCustomerActorDto` | minimize public actor result | CustomerProfile | safe actor DTO | none | prevents consumers from overreading profile data |
| `applyCustomerStatusPolicy` | validate approved transition | current/target/context | transition decision | status after approval | lifecycle is Customer-owned |
| `mapCustomerPrivacyFields` | define Customer-owned subject/export/anonymization fields | CustomerProfile | privacy field map/result | profile fields under instruction | only owner can define semantic field disposition |
| `classifyCustomerWorkerFailure` | separate retryable/terminal Customer processing failures | operation/error category | retry class/reason | none | domain-specific retry meaning atop shared queue |

These operations must not grow into generic auth, entitlement, media, privacy, audit, or cross-domain repositories.

---

## 17. Shared Mechanism / Separate Truth Rules

- **One-to-one provisioning:** reuse SH-114; CustomerProfile remains Customer truth. Candidate/Professional profiles remain their owners.
- **Idempotency:** reuse SH-044; semantic Customer command identity stays local.
- **Lifecycle state machine:** reuse SH-053; Customer supplies its own transition matrix after approval.
- **Outbox/events:** reuse SH-046; Customer event semantics remain local, and no generic event log replaces source truth.
- **Queues/retries:** reuse SH-047/048; Customer worker progress is operational, not profile status.
- **Concurrency:** reuse SH-051/052 plus database uniqueness; no in-memory locking.
- **Media:** reuse Media safety/access mechanics; only `avatarMediaId` relationship meaning is Customer truth.
- **Privacy:** reuse SH-095–098; Customer executes its data while Privacy owns request/job/target/exemption truth.
- **Aggregate projection:** if a customer commerce history view is later approved, use SH-115 only after projection ownership is settled; never copy foreign lifecycle state onto CustomerProfile.
- **Commercial snapshots:** downstream Order/Booking own fee/priority snapshots; Customer owns neither the snapshot nor current Track policy.

---

## 18. Authentication and Authorization

### Authentication

All protected Customer queries/commands require SH-001 except trusted internal/system calls such as the post-User provisioning event or Privacy executor. System calls must carry verifiable internal context and correlation/idempotency metadata; they are not “anonymous” shortcuts.

### Authorization

Use SH-002. Customer supplies minimum owner facts such as:

- profile ID;
- owning `userId`;
- current profile status if the permission policy needs it;
- requested Customer action;
- sensitivity/purpose classification.

Role / Authority interprets permission. Customer must not build generic self/admin/role helpers.

### Resource ownership

The primary self-ownership relationship is:

```text
CustomerProfile.userId == authenticated User.id
```

An expected `customerProfileId` is never accepted as proof by itself.

### Organization/participant context

CustomerProfile is not an OrganizationMember or thread-participant authority record. If a Customer action also involves organization/thread participation, the corresponding owner supplies those facts separately.

### Admin/support actions

Admin/support profile reads/changes must:

- resolve the authenticated actor;
- pass SH-002 for the specific action;
- use purpose-limited fields;
- produce generic audit and sensitive-access proof where root policy requires;
- never become an unrestricted “edit any profile” bypass.

### Step-up

No Customer-specific step-up requirement is confirmed. If root security policy later classifies destructive privacy retries, suspension, archive, or high-risk admin profile operations as sensitive, use Identity's canonical step-up capability rather than a Customer MFA flow.

---

## 19. Compliance / Readiness / Entitlement Gates

### Customer actor existence

- **Underlying truth owner:** Customer / Buyer Profile.
- **Query:** SH-004.
- **Gated action:** downstream customer-side business setup.
- **Decision:** valid CustomerProfile actor or explicit not-provisioned/mismatch result.

### ComplianceHold

- **Underlying truth owner:** Admin Review / Compliance Hold.
- **Query:** SH-011.
- **Gated Customer action:** only actions explicitly classified hold-sensitive by approved policy.
- **Local composition:** a hold may deny/defer the Customer command; it does not rewrite CustomerProfile status automatically.

### Track entitlement

- **Underlying truth owner:** Track Subscription & Entitlement.
- **Query:** SH-005 or specialized Track policy query.
- **Gated action:** normally Gig/Order/Booking/delivery owner actions, not actor resolution itself.
- **Local composition:** Customer does not persist the result as profile truth.

### Consent

No generic CustomerProfile existence/edit command currently requires a Module-owned consent gate. If a future profile-publication or subscription-related Customer action requires exact consent, Consent owns proof and Customer only composes the decision for its own action.

### Privacy

Privacy target execution is not a “readiness” decision. Privacy owns instruction/exemption truth; Customer executes its own disposition.

---

## 20. Provider Integrations

This Module owns **no external provider integration**.

Specifically prohibited inside Customer / Buyer Profile:

- Supabase/Auth provider client for authentication;
- Stripe Billing/Customer/payment client;
- R2/S3/storage client;
- malware scanner/image processor;
- Typesense/search provider client;
- email/SMS/push provider client;
- geocoding/location-reveal provider client.

All provider-dependent work must enter through the public interface of the provider-owning Module.

---

## 21. Events and Outbox

### Customer-owned events

Emit only facts that occurred in Customer truth. Possible event categories are provisioning, approved metadata/avatar changes, approved lifecycle transitions, and privacy disposition.

### Emission rule

If an event is required for durable downstream reaction, write the Customer source mutation and SH-046 outbox record in the same transaction or root-approved atomic pattern.

### Payload minimization

Prefer:

- event ID/type/version;
- customerProfileId;
- userId only when necessary;
- previous/new status only for status event;
- changed-field categories, not raw personal values;
- correlation/request ID;
- occurredAt.

Do not publish raw profile text/location, Media URLs, Track data, or foreign lifecycle state unless a specific consumer contract requires and permits it.

### Consumer idempotency

Consumers must deduplicate by event ID/semantic source. Customer event handlers likewise use SH-045 for incoming events.

### Events are not commands

“CustomerProfileUpdated” may tell consumers a fact changed. It must not encode “create an Order” or “suspend a Booking” as a disguised cross-Module command.

---

## 22. Background Jobs / Scheduled Work

### Existing-user CustomerProfile backfill

- **Purpose:** ensure eligible pre-existing Users can obtain CustomerProfile records.
- **Input:** cursor/batch of eligible User IDs from an approved Identity source contract.
- **Owner:** Customer / Buyer Profile for profile creation; Identity remains User owner.
- **Idempotency key:** per-User provisioning semantic key.
- **Retryable failures:** transient DB/queue/dependency issues.
- **Permanent failures:** invalid/missing User, contradictory mapping requiring manual review.
- **Dead-letter/manual review:** poison items are isolated with safe identifiers and correlation IDs.
- **Truth updated:** CustomerProfile only.
- **Telemetry:** processed/created/existing/conflict/retry/terminal counts; no raw PII.

### Customer actor reconciliation

- **Purpose:** detect zero/multiple/mismatched buyer actor conditions without directly mutating foreign lifecycle records.
- **Input:** CustomerProfile/User facts plus owner-supplied downstream references during approved migration.
- **Owner:** Customer for Customer consistency report; each destination owner repairs its own rows.
- **Behavior:** report mismatch; never guess mapping.

No scheduler-specific truth is owned here. Queue/retry/dead-letter mechanics use shared infrastructure.

---

## 23. Concurrency and Idempotency

### Provisioning race

**Resource key:** `User.id` / semantic key `customer-profile:provision:<userId>`.

**Database guarantee:** `CustomerProfile.userId @unique`.

**Transaction strategy:** use an idempotent command and database upsert/insert-with-conflict-safe recovery. SH-051 may serialize if the chosen persistence pattern needs it, but uniqueness is the primary hard invariant.

**Replay result:** return the existing profile with a stable `existing`/`created` disposition.

### Metadata/avatar update race

Use SH-052 with an expected version token. The current schema has `updatedAt` but no explicit numeric version. Until root/database policy selects another version strategy, an expected `updatedAt`-style compare-and-swap is acceptable only if the implementation can guarantee precision/correctness; otherwise an approved schema version column is required before enabling concurrent writes.

### Status race

No production status mutation until `U-CL01-21` is resolved. Once enabled, current status/version must be checked atomically in the owner transaction.

### Backfill replay

Every batch item is independently idempotent. Checkpoints may be replayed without duplicate profile creation.

### No in-memory locks

Database-owned concurrency must never rely on process-local mutexes.

---

## 24. Media / Storage

### Business attachment meaning owned here

`avatarMediaId` means: “this validated MediaAsset is currently selected as this CustomerProfile's avatar.”

### File mechanics owned by Media / File Access

Media owns:

- upload/session lifecycle;
- file size/type/signature validation;
- malware scan;
- metadata scrub/processing;
- storage object key and provider state;
- MediaAsset lifecycle/readiness;
- private/public storage rules;
- signed URL issuance and generic access evidence.

### Upload context

Customer may initiate an avatar-use context, but the actual upload path goes through Media.

### Validation

Customer avatar attachment requires a Media result demonstrating the asset is attachable/ready under Media policy. Customer must not trust browser MIME/type or a raw UUID.

### Signed access

Display access uses Media's SH-087. Customer never returns a permanent private storage URL.

### Unresolved relation

`avatarMediaId` is currently not an explicit Prisma relation to MediaAsset. Do not create an FK/polymorphic relation until the architecture decision is approved. Until then, every attachment mutation validates the UUID through Media.

---

## 25. Search / Projection

### Current ruling

CustomerProfile public search/indexing is disabled under CL-01 `PR-CL01-05` until `U-CL01-22` resolves:

- legitimate public product need;
- visibility lifecycle;
- approved public field set;
- moderation/privacy/location behavior;
- search entity type/document schema;
- removal/reindex triggers.

### Source truth

CustomerProfile remains source truth regardless of whether a future public projection exists.

### Current implementation prohibition

- no Customer search projection builder;
- no SH-091 projection refresh request;
- no Typesense client;
- no public profile route inferred from display fields.

If public indexing is approved later, Search owns index execution and Customer may own only its approved source projection via SH-094.

---

## 26. Notification

Customer owns business trigger intent only.

Potential future triggers include:

- admin-driven status/archive changes when policy requires notice;
- material privacy/profile changes when user notice is required.

Normal provisioning or metadata edits do not automatically imply a notification.

Use SH-041 with a recipient reference and safe template variables. Notification owns template rendering, channel choice, retries, delivery records, and provider callbacks.

Do not implement email/SMS/push clients here.

---

## 27. Audit and Sensitive Access

### Domain truth

CustomerProfile and any future Customer-specific lifecycle event/outbox fact remain domain truth.

### Generic AuditEvent

Use SH-029 for material actions such as:

- admin status/archive/restore change once enabled;
- authorized manual migration/reconciliation correction of Customer-owned data;
- destructive/anonymizing Privacy executor actions where policy requires proof.

Normal self-service profile edits need audit only if root policy requires it; do not use audit as a substitute for source state.

### AccessAuditLog

Use SH-030 when profile/admin/export reads are classified sensitive. Customer defines sensitivity/context; Audit owns the log.

### Separation

Do not create `CustomerAuditLog`, `CustomerAccessLog`, or treat structured logs as compliance proof.

---

## 28. Privacy and Retention

### Customer subject-data inventory

Customer-owned personal data includes at minimum:

- CustomerProfile ID and User linkage;
- displayName;
- avatarMediaId reference;
- city/state/country profile metadata;
- status/archive timestamps when tied to subject account behavior;
- created/updated timestamps.

Foreign Gigs/Orders/Bookings/Reviews/Disputes are not Customer-owned export content; Privacy queries those owners independently.

### Privacy interfaces

Customer implements:

- SH-096 subject-data enumeration;
- Customer export fragment;
- SH-097 retention-fact response where Customer owns the fact;
- SH-095 idempotent instruction executor;
- SH-098-approved field anonymization mapping when applicable.

### Erase/anonymize/revoke/retain behavior

The exact hard-delete-vs-anonymize-vs-archive policy is not fully established. Therefore destructive behavior must follow the Privacy instruction and approved retention decisions; if necessary facts remain unresolved, return a retained/review-required result rather than inventing deletion.

### Open obligations

Open Orders, disputes, Bookings, and other obligations are queried from their owners. Customer must not delete or mutate them. Those facts may constrain whether a CustomerProfile row can be physically removed while preserving referential integrity/retention.

### Avatar

Customer may clear/detach `avatarMediaId` under the approved instruction. Media owns deletion/anonymization of the actual MediaAsset/object through its own Privacy target.

### Cascade safety

Because current User → CustomerProfile relation can cascade on User deletion, production User hard-delete must be restricted to the approved account/Privacy orchestration. A generic User delete must not erase CustomerProfile before its executor/retention checks run.

---

## 29. Observability

Use canonical request/log/metric/failure/queue operations.

### Structured log dimensions

Allowed examples:

- operation;
- customerProfileId;
- userId only when necessary and policy-approved;
- status category;
- result/reason code;
- created-vs-existing disposition;
- batch/job ID;
- correlation/request ID;
- dependency name/category.

Avoid raw display name, avatar URL/object key, exact address/location, auth tokens, entitlement/provider payloads, or privacy contents.

### Metrics

Useful metrics include:

- provision created/existing/conflict rate;
- actor-resolution not-found/mismatch rate;
- backfill progress and exception count;
- profile update conflict rate;
- Media attachment rejection/dependency failure rate;
- Privacy executor retry/retained/terminal counts.

### Operational records

IntegrationFailure/SystemEvent/queue telemetry diagnose failures. They never set CustomerProfile status or prove a business lifecycle transition.

---

## 30. Security Boundaries

- Validate every external/server boundary with the root-approved runtime validation mechanism.
- Never accept `userId`/`customerProfileId` from the client as proof of ownership.
- Authorize server-side through SH-002.
- Minimize profile DTOs by purpose.
- Treat display/location/avatar data as personal information for logging/export/redaction purposes.
- Never expose private storage object keys or reusable signed URLs as durable CustomerProfile fields.
- Never store card/payment/provider secrets here.
- Do not trust browser-provided file type or readiness.
- Do not enable public profile/search from the existence of display fields alone.
- Restrict destructive Privacy execution to trusted Privacy workflow context.
- Apply root rate limits to exposed profile mutation/read endpoints where applicable.
- Use step-up only through Identity if root policy classifies an action as sensitive.

---

## 31. Error / Decision Result Pattern

Public interfaces should return stable categories and safe reason codes rather than raw ORM/provider exceptions.

Recommended categories:

```text
success
not_found
not_provisioned
validation_denied
authorization_denied
consistency_mismatch
conflict
unsupported_state
architecture_gate_unresolved
dependency_unavailable
privacy_retained
retryable_failure
terminal_failure
```

Examples of safe Customer-specific reason semantics:

- Customer profile does not exist for User;
- expected profile does not belong to User;
- requested field is not editable under current ownership policy;
- public profile view is disabled;
- avatar asset is not attachable/ready;
- stale update conflict;
- lifecycle transition is not enabled/approved.

Provider/ORM errors stay internal. If the shared `SH-015 returnDecisionResult` contract is formally approved, Customer should conform to it rather than create a competing result envelope.

---

## 32. Testing Architecture

### Domain unit tests

- one-to-one consistency policy;
- safe actor DTO minimization;
- editable-field allowlist/normalization;
- avatar contextual attachment policy;
- future status transition matrix after approval;
- privacy field mapping.

### State-transition tests

- provisioning no-profile → exactly-one-profile;
- duplicate/replayed provisioning;
- future full status matrix positive/negative tests before status commands enable.

### Public contract tests

- SH-004 resolver;
- consistency assertion;
- safe profile query;
- metadata/avatar commands;
- SH-095/096/097 Customer implementations.

### Database/integration tests

- unique `userId` concurrency;
- transaction rollback;
- optimistic concurrency;
- migration/backfill restart;
- cascade-delete safety guard.

### Authorization tests

- self owner;
- other User denial;
- authorized admin/support;
- unauthorized admin-like actor;
- trusted system/Privacy caller boundaries.

### Compliance/privacy tests

- no Track premium fields;
- no local hold truth;
- export contains Customer-owned fields only;
- retention instruction respected;
- avatar detachment vs Media deletion separation;
- destructive cascade path cannot bypass Privacy.

### Idempotency/concurrency tests

- parallel profile provisioning;
- event replay;
- same avatar/metadata command replay;
- stale concurrent update conflict;
- backfill checkpoint/resume.

### Provider adapter tests

None owned. Use contract tests against Media/Identity/Privacy test doubles and their public interfaces.

### E2E participation tests

- account creation → CustomerProfile provisioning/resolution;
- profile edit/avatar flow if UI exists;
- Customer actor → Gig/Order/Booking owner contract after cutover;
- Privacy test harness → Customer target result.

---

## 33. Module Invariants

**Rules coding agents must never violate:**

1. `CustomerProfile` has exactly one owning Module: Customer / Buyer Profile.
2. A User may have at most one CustomerProfile.
3. CustomerProfile is buyer/customer actor truth; User remains account/auth identity.
4. A supplied `userId` and `customerProfileId` must be proven to match before downstream use.
5. CustomerProfile provisioning does not require Track subscription/grant existence.
6. No `isPremium`, `isHiveClub`, fee-waiver, priority, quota, commission, or boost truth may be stored on CustomerProfile.
7. Order and Booking own historical commercial/priority snapshots.
8. Customer does not mutate Gig, Order, Booking, Review, Dispute, delivery-grant, or payment truth.
9. Customer does not own auth/session/passkey/MFA/recovery logic.
10. Customer does not own generic permission logic.
11. CustomerProfile status is not a mirror of ComplianceHold.
12. Full CustomerProfile status transitions remain disabled until `U-CL01-21` is resolved.
13. The shared `ProfileStatus` enum definition must not be claimed/migrated by this Module until `U-CL01-20` resolves.
14. User↔CustomerProfile metadata must not be bidirectionally synchronized until `U-CL01-22` resolves field precedence.
15. `avatarMediaId` does not make Customer the MediaAsset owner.
16. Avatar attachment cannot bypass Media readiness/safety validation.
17. Customer never generates signed media URLs directly.
18. Public CustomerProfile indexing/search is disabled until `U-CL01-22` is resolved.
19. Customer never writes Typesense/SearchUpsertEvent directly.
20. Customer does not create PrivacyRequest/DataErasureJob/DataErasureTarget/DataRetentionExemption.
21. Privacy instructions affect only Customer-owned data; foreign obligations remain with their owners.
22. Production User hard-delete must not cascade away CustomerProfile before approved Privacy/retention execution.
23. Customer commerce history must not be copied into CustomerProfile as lifecycle truth.
24. Review/Dispute direct CustomerProfile references must not be added until `Review/Dispute direct CustomerProfile reference decision` resolves.
25. Generic AuditEvent/AccessAuditLog and Ops records never replace Customer source truth.
26. Shared idempotency, event, queue, locking, media, audit, privacy, and notification mechanisms are reused, never rebuilt locally.
27. No external provider client belongs in this Module under the current architecture.
28. High-risk unresolved behavior fails closed or remains unavailable; coding agents do not invent policy.

---

## 34. Prohibited Duplicate Implementations

Do not generate these or semantic equivalents inside this Module:

```text
customerAuth.ts
buyerSessionService.ts
currentCustomerUser.ts
customerPermissions.ts
buyerAuthorization.ts
profileAcl.ts
customerHoldService.ts
customerBlocked.ts
customerPremiumService.ts
hiveClubService.ts
buyerPerks.ts
customerEntitlementHelper.ts
customerUsageTracker.ts
customerAuditService.ts
buyerEventLogger.ts
customerAccessLog.ts
customerEmailService.ts
buyerPushService.ts
profileNotifier.ts
customerGdprWorkflow.ts
customerPrivacyOrchestrator.ts
customerAvatarUpload.ts
buyerFileValidator.ts
profileImageScanner.ts
customerAvatarPresign.ts
buyerSearchIndexer.ts
customerTypesense.ts
profileSearchSync.ts
customerEventBus.ts
buyerQueue.ts
customerIdempotencyStore.ts
profileFactory.ts            # if it owns multiple profile lifecycles
customerHistoryStore.ts      # copied foreign lifecycle truth
customerPaymentMethod.ts
stripeCustomerService.ts
```

Also prohibited:

- direct Prisma repositories for Gig/Order/Booking/Track/Media/Review/Dispute inside Customer;
- generic profile lifecycle service owning Customer/Professional/Candidate together;
- local outbox, queue runner, retry engine, lock manager, logger, metrics client, or audit table.

---

## 35. Unresolved Decisions

These are implementation gates, not invitations to improvise.

| ID | Decision | Blocks / consequence |
| --- | --- | --- |
| **U-CL01-20** | Who owns the shared `ProfileStatus` enum definition? | enum-level schema ownership/comment changes; does not remove Customer transition ownership for its record |
| **U-CL01-21** | Exact CustomerProfile transition matrix for draft/active/paused/suspended/archived, actor rights, terminal/reopen rules, and open-obligation effects | production status/archive/restore commands |
| **U-CL01-18** | Final provisioning trigger: same request, outbox consumer, or worker? | final signup orchestration; standalone idempotent provision command can be built now |
| **U-CL01-19** | When is `customerProfileId` mandatory for new Gig/Order/Booking-side records? | downstream cutover, nullability/index migrations, backfill enforcement |
| **U-CL01-22** | Which source is authoritative for duplicated User vs CustomerProfile display/location/avatar data? | field editing/sync/copy-on-create behavior |
| **U-CL01-22** | Are CustomerProfiles publicly discoverable, and what fields/visibility/moderation/privacy rules apply? | any public profile/search projection |
| **Review/Dispute direct CustomerProfile reference decision** | Should Review/Dispute store direct CustomerProfile references? | Review/Dispute schema migrations only |
| **CBP-U-01** | Does `avatarMediaId` remain validated UUID reference, become FK, or use a generalized attachment model? | schema relation migration; attachment command can use Media validation without changing schema |
| **CBP-U-02** | Does Customer need durable lifecycle history beyond outbox/audit, and if so what record owns it? | any new CustomerProfile event table |
| **CBP-U-03** | Who owns the cross-Module customer commerce-history aggregate/read model? | durable aggregate/query implementation |
| **CBP-U-04** | Exact CustomerProfile privacy disposition/retention map, including when row deletion is allowed vs anonymize/archive/retain | destructive SH-095 execution |
| **CBP-U-05** | Which Customer admin/support reads qualify as sensitive access and which actions require step-up? | SH-030/Identity step-up policy matrix |

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Customer / Buyer Profile owns `CustomerProfile` buyer actor truth.
2. `User` remains Identity-owned account/auth truth.
3. CustomerProfile is one-to-one with User and `userId` uniqueness must be enforced.
4. Customer actor provisioning is independent of Track subscription availability.
5. `resolveCustomerActor` is the canonical downstream buyer actor interface.
6. Consumers must not recreate buyer resolution from User fields or direct CustomerProfile table reads.
7. CustomerProfile-specific lifecycle policy belongs to Customer; the shared enum-definition owner remains unresolved.
8. Track alone owns current commercial plan/subscription/grant/usage policy.
9. Customer owns only avatar relationship meaning; Media owns file truth/mechanics.
10. Privacy owns request/job/target/exemption orchestration; Customer implements owner inventory/export/execution.
11. Search is projection and CustomerProfile public indexing remains disabled until approved.
12. Audit, Notification, Ops, Hold, and shared platform mechanisms remain with their canonical owners.
13. Downstream Gig/Order/Booking/Review/Dispute lifecycles remain with their owners.
14. Shared operations are consumed by permanent SH IDs and not reimplemented locally.

### Proposed rulings carried forward

- **PR-CL01-03:** Customer owns CustomerProfile transition policy even if ProfileStatus remains a shared vocabulary.
- **PR-CL01-05:** CustomerProfile public indexing remains disabled pending a dedicated visibility decision.
- **CBP-PR-01:** use outbox/domain events for Customer integration facts; do not create a dedicated lifecycle-event table without a separate requirement.

### Conservative implementation posture

- build provisioning/resolution first;
- build only approved metadata/avatar edits;
- keep full status transitions gated;
- keep public profile/search disabled;
- keep Review/Dispute direct actor migration deferred;
- prevent destructive privacy behavior until retention/disposition is approved;
- never use Customer as a shortcut around foreign owner contracts.

---

## 37. Coding-Agent Usage

Before implementing or changing this Module, read in order:

1. root `context/project-overview-v3.md`;
2. root `context/architecture.md` (**currently missing**; see `context/context-map.md`);
3. root `context/code-standards.md` (**currently missing**; see `context/context-map.md`);
4. `context/shared/shared-operations.md`;
5. CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-architecture.md`;
6. CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-build-plan.md`;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. relevant dependency public-interface sections, especially Identity & Access, Role / Authority, Media / File Access, Privacy / Data Erasure, Audit / Event Ledger, Admin Review / Compliance Hold, Track Subscription & Entitlement, Gig / Demand, Transaction / Order, and Booking & Calendar;
10. `progress-tracker.md` (**currently missing**; see `context/context-map.md`);
11. the current Prisma schema and migrations before any data-structure change.

If code, schema comments, registry text, or context files conflict:

1. identify the conflict;
2. apply the documented evidence/authority order;
3. do not silently normalize architecture to existing code;
4. resolve/update the binding architecture if the decision legitimately changes;
5. then implement the approved state.
