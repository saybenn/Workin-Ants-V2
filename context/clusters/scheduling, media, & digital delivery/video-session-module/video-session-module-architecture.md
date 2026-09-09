# Video Session Architecture

> **Module ID:** `video_session`  
> **Canonical working name:** Video Session Module  
> **Registry alias:** Video Infrastructure Module  
> **Module type:** `capability`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Repository target:** `context/clusters/scheduling-media-digital-delivery/modules/video-session/module-architecture.md`  
> **Document status:** Implementation-grade Module architecture derived from the current Workin Ants Module extract, registries, Prisma schema, Ubiquitous Language / Compliance evidence, Canonical Shared Operations Registry, and CL-05 architecture/build plan. Proposed rulings and unresolved decisions are explicit.  
> **Audience:** coding agents, developers, reviewers, maintainers, security/privacy reviewers, and architecture reviewers  
> **Update rule:** update this file whenever a binding Video Session ownership, lifecycle, public contract, provider, security, privacy, or data-model decision changes. Build progress must not silently redefine this architecture.

## Evidence Status Vocabulary

- **Confirmed** — directly established by the current Workin Ants registries, schema, glossary/compliance evidence, Module extract, Shared Operations Registry, or CL-05 architecture.
- **Reasonable inference** — required by confirmed workflows but not itself a settled schema/API decision.
- **Proposed Ruling** — implementation-grade decision strongly supported by the evidence but requiring architecture approval before code/schema commits depend on it.
- **Unresolved** — the current evidence conflicts or is insufficient. Implementation must not silently decide it.

---

## 1. Module Header

### Relationship to root architecture

Video Session is subordinate to the root Workin Ants architecture. Root rules on source-of-truth ownership, authentication, authorization, privacy, audit, observability, provider isolation, and commercial entitlement remain controlling.

This Module does not become a local substitute for root services merely because video delivery needs authentication, access control, queues, idempotency, cryptography, auditing, provider security, privacy execution, or notification.

### Relationship to CL-05 architecture

CL-05 coordinates `booking_calendar`, `video_session`, `media_file_access`, and `digital_goods_access`. The Cluster does not own Video Session records. This file is authoritative for Video-local lifecycle and interface rules while remaining subordinate to binding root and Cluster decisions.

The CL-05 architecture establishes these binding boundaries:

- Video Session owns live-room and on-demand streaming-provider resource truth.
- Booking & Calendar owns `Booking` and booking orchestration truth.
- Job Interview owns `JobInterview` and participant/scheduling truth.
- Media / File Access owns raw/source file safety, storage, and `MediaAsset` truth.
- Transaction / Order owns purchase entitlement.
- Digital Goods Access owns digital-goods license/refund/terms/access policy outside the streaming mechanics owned here.
- Healthcare / Regulated Services owns healthcare-lane readiness and BAA/provider approval.
- Audit / Event Ledger owns generic `AuditEvent` and `AccessAuditLog`.
- Privacy / Data Erasure owns privacy-request orchestration and retention exemptions.
- Provider state is input/evidence; Workin Ants Video records remain authoritative Video state.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Provide one Workin Ants capability boundary for live video room mechanics and on-demand course-streaming mechanics without absorbing the parent business lifecycles that decide why the video exists or who is commercially entitled to it.

### Goal

Convert authoritative upstream context into secure, short-lived, provider-backed video delivery while preserving Workin Ants-owned room, streaming asset, playback-grant, playback-event, and provider-event-dedupe truth.

### What enters

Typical inputs are:

- authenticated actor context;
- Role / Authority decisions;
- Booking owner facts for a confirmed video Booking;
- JobInterview owner facts and participant roles;
- `Order` entitlement for purchased course playback;
- `CourseDetails` / Offering target facts;
- a Media-owned ready source `MediaAsset` for course-video ingest;
- Digital Goods policy/terms facts where the course delivery policy requires them;
- Track Subscription & Entitlement decisions where live-streaming entitlement is applicable;
- Healthcare readiness/data-boundary/provider-approval decisions where a healthcare lane applies;
- ComplianceHold decisions;
- Moderation/legal execution instructions;
- Privacy execution instructions;
- verified external provider callbacks;
- system/admin retry or reconciliation commands.

### What leaves

Typical outputs are:

- `BookingVideoRoom` state;
- `JobInterviewVideoRoom` state;
- short-lived participant-specific live join credentials;
- `CourseVideoAsset` provider-ingest/processing/readiness state;
- `CourseVideoPlaybackGrant` state;
- short-lived signed playback credentials;
- append-only `CourseVideoPlaybackEvent` evidence;
- `ProcessedVideoProviderEvent` dedupe evidence;
- Video-owned domain events/outbox messages;
- sensitive-access audit requests;
- integration-failure/telemetry requests;
- provider-resource deletion/revocation results for Privacy or Moderation.

### Capability transformation

```text
authoritative parent context / purchase entitlement / ready media
+ authentication and authorization
+ applicable hold / healthcare / entitlement gates
→ Video-local readiness policy
→ Video-owned room / provider asset / playback-grant truth
→ provider work through Video-owned ports
→ verified + deduplicated + translated provider response
→ short-lived credential when allowed
→ Video domain access/lifecycle evidence
→ audit / notification / ops / privacy acknowledgments through public interfaces
```

### Why this deserves its own Module boundary

Live room providers and course-streaming providers share security, provider-event, access-token, reconciliation, and operational patterns, but they must not be implemented independently inside Booking, Job Interview, Marketplace Supply, or Digital Goods. A dedicated capability Module prevents provider leakage while keeping parent business truth in the correct owners.

The boundary also preserves a crucial distinction:

```text
Parent Module decides why a session or video is relevant.
Video Session decides how the provider-backed video resource is provisioned and securely accessed.
```

---

## 3. Owned Truth

### 3.1 Models owned

| Record | Meaning | Ownership status |
| --- | --- | --- |
| `BookingVideoRoom` | Workin Ants record for the live provider room attached one-to-one to a Booking. | Confirmed |
| `JobInterviewVideoRoom` | Workin Ants record for the live provider room attached one-to-one to a JobInterview. | Confirmed |
| `CourseVideoAsset` | Workin Ants streaming-provider asset record for an on-demand course video. | Confirmed |
| `CourseVideoPlaybackGrant` | Temporary, user-scoped Workin Ants playback authorization after external entitlement and local video checks pass. | Confirmed |
| `CourseVideoPlaybackEvent` | Append-only Video-specific access/provider delivery evidence for course playback. | Confirmed |
| `ProcessedVideoProviderEvent` | Video-provider webhook/event dedupe and processing proof. | Confirmed |

### 3.2 Enums/status vocabularies owned

- `BookingVideoProvider`
- `BookingVideoRoomStatus`
- `JobInterviewVideoProvider`
- `JobInterviewVideoRoomStatus`
- `CourseVideoProvider`
- `CourseVideoAssetStatus`
- `CourseVideoPlaybackPolicy`
- `CourseVideoPlaybackGrantStatus`
- `CourseVideoPlaybackEventType`
- `VideoProviderEventProvider`
- `VideoProviderEventStatus`

### 3.3 Lifecycles owned

Video Session is the only Module allowed to transition:

- `BookingVideoRoom.status`;
- `JobInterviewVideoRoom.status`;
- `CourseVideoAsset.status`;
- `CourseVideoPlaybackGrant.status`;
- `ProcessedVideoProviderEvent.status`;
- Video-owned provider references and failure/readiness metadata associated with those records.

`CourseVideoPlaybackEvent` is append-only evidence, not a mutable lifecycle.

### 3.4 Source-of-truth records

- `BookingVideoRoom` is live Booking-room truth. Provider room state is not the Workin Ants source of truth.
- `JobInterviewVideoRoom` is live interview-room truth. `JobInterview` remains the hiring lifecycle source of truth.
- `CourseVideoAsset` is on-demand provider-asset truth. `MediaAsset` remains raw/source file truth and `CourseDetails` remains course business structure truth.
- `CourseVideoPlaybackGrant` is temporary stream-access truth. `Order` remains purchase entitlement truth.
- `ProcessedVideoProviderEvent` is Video provider-event dedupe truth. It must never be merged with `ProcessedCalendarEvent`, `ProcessedStripeEvent`, or generic audit records.

### 3.5 Domain events / ledgers owned

`CourseVideoPlaybackEvent` is Video-owned domain access evidence. It is distinct from:

- `AccessAuditLog` — generic sensitive-access proof owned by Audit / Event Ledger;
- `AuditEvent` — generic material action proof;
- `ProcessedVideoProviderEvent` — provider callback dedupe proof;
- operational logs/metrics/IntegrationFailure — execution diagnostics.

Live-room-specific domain access evidence beyond generic AccessAuditLog is **not fully represented by the current schema**. See Unresolved Decisions.

### 3.6 Projections owned

No public-search projection is owned here.

Safe read models may be derived for:

- room setup status;
- course-video processing status;
- playback-grant status;
- provider reconciliation status for authorized support/admin tooling.

These are views over Video-owned truth, not new authoritative tables unless later architecture explicitly establishes one.

### 3.7 Snapshots / proof owned

Video-owned proof includes:

- provider IDs and canonical provider status attached to Video records;
- `tokenHash` and `playbackUrlHash` on `CourseVideoPlaybackGrant` when used;
- `payloadHash` on `ProcessedVideoProviderEvent` when supplied;
- timestamps for grant, first use, expiry, revocation, processing, readiness, and failure;
- course playback progress/completion/error evidence where recorded.

Video must not persist reusable playback credentials as durable truth.

### 3.8 Policies / invariants owned

Video Session owns the local policy for:

- mapping a valid Booking or JobInterview context to a provider-room request;
- selecting the configured Video provider from approved provider configuration;
- mapping participant context to provider claims/roles;
- calculating live join credential bounds from source-owner timing facts;
- mapping provider-native status/error output to Video-owned statuses;
- deciding when a Video record is locally ready to issue a credential;
- applying temporary playback-grant expiry/revocation mechanics to `CourseVideoPlaybackGrant`;
- deciding which provider discrepancies are safe to reconcile automatically;
- classifying provider failures as retryable, terminal, or manual-review-required;
- defining the semantic idempotency key for Video commands.

Video does **not** own the external facts consumed by those policies.

---

## 4. Explicit Non-Ownership

Video Session must not own or recreate the following.

| Adjacent owner | Truth that remains external | Prohibited Video behavior |
| --- | --- | --- |
| Identity & Access | User authentication/session/security truth | Do not create `videoAuth.ts`, local current-user/session systems, or provider-room identity as authentication. |
| Role / Authority | Platform/org/participant permission interpretation | Do not build a generic `videoParticipantGuard` permission engine. |
| Booking & Calendar | Booking scheduling, status, participants, start/end, overtime grace, cancellation/reschedule, Booking orchestration | Do not transition `Booking`; do not use provider room status to mark Booking complete/cancelled. |
| Job Interview | Interview lifecycle, time, candidate/interviewer/coordinator/observer context | Do not turn JobInterview into Booking; do not mutate JobInterview status. |
| Transaction / Order | Purchase/transaction entitlement and refund/dispute effects | Do not infer payment from Stripe/provider state or local `isPaid` flags. |
| Marketplace Supply | Offering/CourseDetails business structure and publication lifecycle | Do not make `CourseVideoAsset` the course curriculum or Offering lifecycle. |
| Media / File Access | `MediaAsset`, raw source object, upload validation, malware scan, quarantine, object storage, signed object access | Do not instantiate R2/S3 clients here; do not build video-specific file validation or malware scanning. |
| Digital Goods Access | digital-goods license/refund/terms policy, `DigitalGoodsTermsAcceptance`, accessibility tracking | Do not make `CourseVideoPlaybackPolicy` a substitute for digital-goods commercial policy. |
| Track Subscription & Entitlement | plan, subscription, grant, usage truth | Do not create `canLiveStream`, `videoPremium`, or similar current-policy booleans. |
| Healthcare / Regulated Services | healthcare sensitivity, BAA/provider approval, healthcare readiness/access policy | Do not decide that a service/video is HIPAA-ready. |
| Admin Review / Compliance Hold | reusable stop-sign lifecycle | Do not add generic local `blocked`, `onHold`, or `videoHold` truth. |
| Content Moderation & Legal Notice | moderation/legal validity and case/action lifecycle | Do not adjudicate DMCA/legal notices; execute approved Video-local effects only. |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | Do not replace Video domain evidence with generic audit or build `videoAuditLog.ts`. |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob/Target/RetentionExemption orchestration | Do not create a Video privacy workflow. Implement owner target execution only. |
| Notification | Notification and delivery mechanics | Do not call email/SMS/push providers from Video. |
| Observability / Ops | generic logs, metrics, IntegrationFailure/QueueJob/OpsIncident semantics | Do not create a competing Video incident or queue ledger. |
| Search / Public Visibility | Typesense/SearchUpsertEvent and public projection | Do not call Typesense directly or reconstruct public readiness. |

### Additional explicit non-ownership

Video Session does not own:

- payment state;
- hiring decisions;
- calendar availability;
- course enrollment/curriculum structure;
- raw course `.mp4` delivery;
- downloadable file entitlement;
- course accessibility asset lifecycle;
- generic temporary access-grant schema;
- generic workflow/saga truth.

---

## 5. Module Architecture Principles

1. **Parent truth remains parent truth.** Booking and JobInterview request/consume video; Video never becomes scheduling truth.
2. **Video resource truth stays here.** Provider room/asset state is translated into Video-owned records before other Modules consume it.
3. **Signed delivery is not entitlement.** A provider credential may be issued only after authoritative external entitlement and Video-local readiness both pass.
4. **Live and on-demand are separate lifecycles.** Shared provider/security mechanics do not make a live room the same domain object as a course-streaming asset.
5. **Booking and interview rooms remain separate current source records.** No generic `VideoSession` table may be introduced without a binding architecture change.
6. **Provider calls terminate at Video adapters.** Booking, Job Interview, Marketplace Supply, and Digital Goods do not import Daily/Agora/Mux clients.
7. **Provider callbacks are untrusted until verified and deduplicated.** Signature verification precedes parsing/side effects; dedupe precedes domain mutation.
8. **Provider-native statuses never leak into domain consumers.** Adapters translate into Video-owned statuses and stable result categories.
9. **Credentials are temporary.** Reusable room URLs, signed playback URLs, access tokens, and secrets are not durable entitlement truth.
10. **Raw source video remains Media-owned.** Video consumes a safe source reference/controlled ingest path; it does not own R2 object mechanics.
11. **Healthcare is a gate, not Video policy.** Healthcare-sensitive delivery requires an owner-issued healthcare/provider decision.
12. **Order is purchase truth.** Paid playback requires `authorizeOrderEntitlement` unless a separately approved alternate access basis exists.
13. **Track entitlement is conditional input only.** Live-streaming entitlement is checked only where product policy says it applies; it never automatically grants paid playback.
14. **Domain evidence, audit, and observability remain distinct.** Each is recorded for its own purpose.
15. **Every external effect is idempotent and reconcilable.** A retry must not create a duplicate provider resource or duplicate Workin Ants semantic effect.
16. **Privacy and moderation instruct; Video executes.** Their source lifecycles remain external.
17. **Unknown or conflicting provider state fails safe.** Reconciliation may repair only explicitly safe discrepancies.
18. **Server time controls time-bound access.** Worker lag does not extend an expired room/grant.

---

## 6. Proposed Folder / Code Structure

The exact repository root must follow root `architecture.md` and `code-standards.md`. The following is the Module-local responsibility shape; it must be adapted to the root convention rather than creating a competing repository pattern.

```text
src/modules/video-session/
├── application/
│   ├── commands/
│   │   ├── register-course-video-source.ts
│   │   ├── request-course-video-ingest.ts
│   │   ├── issue-course-playback-grant.ts
│   │   ├── issue-course-playback-credential.ts
│   │   ├── revoke-course-playback-grant.ts
│   │   ├── provision-booking-video-room.ts
│   │   ├── provision-interview-video-room.ts
│   │   ├── issue-video-join-credential.ts
│   │   ├── cancel-video-room.ts
│   │   └── apply-video-provider-event.ts
│   ├── queries/
│   │   ├── get-course-video-processing-status.ts
│   │   ├── get-course-playback-grant-status.ts
│   │   ├── get-booking-video-room-status.ts
│   │   └── get-interview-video-room-status.ts
│   └── services/
│       ├── course-video-service.ts
│       ├── live-room-service.ts
│       └── provider-event-service.ts
├── domain/
│   ├── policies/
│   │   ├── course-playback-policy.ts
│   │   ├── live-join-window-policy.ts
│   │   ├── provider-selection-policy.ts
│   │   └── provider-reconciliation-policy.ts
│   ├── transitions/
│   │   ├── course-video-asset-transitions.ts
│   │   ├── playback-grant-transitions.ts
│   │   └── live-room-transitions.ts
│   ├── events/
│   │   └── video-domain-events.ts
│   └── result-codes.ts
├── contracts/
│   ├── booking-owner-facts.ts
│   ├── interview-owner-facts.ts
│   ├── course-target-facts.ts
│   ├── media-source-facts.ts
│   ├── video-provider-port.ts
│   ├── live-video-provider-port.ts
│   ├── streaming-video-provider-port.ts
│   └── privacy-executor.ts
├── infrastructure/
│   ├── repositories/
│   │   ├── booking-video-room-repository.ts
│   │   ├── interview-video-room-repository.ts
│   │   ├── course-video-asset-repository.ts
│   │   ├── playback-grant-repository.ts
│   │   ├── playback-event-repository.ts
│   │   └── processed-provider-event-repository.ts
│   ├── providers/
│   │   ├── live/
│   │   │   └── daily-adapter.ts            # only after Proposed Ruling is approved
│   │   └── streaming/
│   │       └── mux-adapter.ts
│   └── workers/
│       ├── course-video-ingest-worker.ts
│       ├── video-provider-event-worker.ts
│       ├── playback-grant-expiration-worker.ts
│       ├── live-room-expiration-worker.ts
│       └── video-provider-reconciliation-worker.ts
├── privacy/
│   ├── enumerate-video-subject-data.ts
│   ├── evaluate-video-retention.ts
│   └── execute-video-privacy-instruction.ts
├── public/
│   ├── commands.ts
│   ├── queries.ts
│   ├── events.ts
│   └── contracts.ts
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    ├── provider/
    ├── privacy/
    ├── concurrency/
    └── e2e/
```

### Folder rules

- `providers/` contains provider translation and provider-specific API types. Provider DTOs must not escape into `domain/` or `public/`.
- `repositories/` access only Video-owned records. Cross-Module facts come through contracts/public interfaces, not imported repositories.
- `privacy/` implements the Video side of the canonical Privacy protocol; it must not own PrivacyRequest/DataErasureJob truth.
- no Module-local generic queue, logger, cryptography, idempotency, webhook-security, audit, notification, or authorization framework is allowed.
- no `shared/video-utils` dumping ground is allowed. Local reusable logic must retain a named Video responsibility.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery/UI integration | Safe Video status DTOs and credential-request entry points consumed by owning UI Modules | Booking/course/hiring UI lifecycle, payment UI, provider secrets |
| Application commands | Validate request, call external owner gates, enforce Video policy, transition Video truth, enqueue provider work | External owner lifecycle transitions |
| Application queries | Read sanitized Video-owned facts | Cross-domain repository joins that reconstruct external policy |
| Domain policy | Video readiness, live join-window, provider selection/mapping, grant expiry/revocation semantics | Order entitlement, healthcare eligibility, organization permission interpretation, digital-goods terms policy |
| Transition services | Video-owned lifecycle graphs | Generic cross-domain state machine policy |
| Repositories | CRUD/locking for Video-owned Prisma models | `Booking`, `JobInterview`, `Order`, `MediaAsset`, `CourseDetails`, `ComplianceHold`, `AccessAuditLog` repositories |
| Workers | Video-specific provider work, expiry, reconciliation | Generic queue/retry system or another Module’s workflow |
| Provider adapters | Daily/Mux or future provider API translation | Workin Ants business truth or authorization policy |
| Public contracts | Stable commands, queries, events, privacy executor | Provider-native payloads/types |
| Privacy executor | Enumerate/erase/anonymize/revoke Video-owned records/resources | Privacy request orchestration/retention-exemption lifecycle |
| Tests | Prove Video policy and cross-Module contracts | Bypassing public interfaces merely for test convenience |

---

## 8. Data Model

### 8.1 `BookingVideoRoom`

**Purpose:** Workin Ants provider-room state for one Booking.

**Key relationships**

- `bookingId` → `Booking.id`.
- `bookingId` is unique: current schema permits at most one room row per Booking.

**Authoritative fields**

- `provider` — canonical Video provider selection, default currently `daily`.
- `status` — Video room lifecycle state.
- `providerRoomId` — external provider reference, not authorization.
- `startsAt`, `endsAt`, `expiresAt` — Video copy/context used to bind provider access. Booking remains authoritative scheduling context.
- `failedAt`, `failureReason` — Video failure state/evidence.

**Sensitive/conflicting fields**

- `roomUrl`, `buyerJoinUrl`, `professionalJoinUrl` exist in Prisma.
- Current architecture forbids reusable public room links as durable truth.
- **Unresolved:** these fields must be removed, encrypted/opaque, or constrained to non-reusable provider references before production reliance. Code must not assume they may safely hold reusable credentials.

**Indexes/concurrency**

- unique `bookingId` is the core duplicate-room database guard;
- indexes on provider/status, providerRoomId, expiresAt support workers/reconciliation;
- provisioning must still use SH-044 idempotency because provider creation occurs outside the database.

**Retention/privacy**

- provider IDs, failure metadata, and join/access context are subject data/operational evidence;
- Privacy may instruct provider deletion and local anonymization/deletion subject to external retention facts;
- provider secrets must never be persisted here.

### 8.2 `JobInterviewVideoRoom`

**Purpose:** Workin Ants provider-room state for one JobInterview.

**Key relationships**

- `interviewId` → `JobInterview.id`;
- `interviewId` is unique.

**Authoritative fields** mirror BookingVideoRoom for provider resource state.

**Sensitive/conflicting fields**

- `roomUrl`, `candidateJoinUrl`, `interviewerJoinUrl` present the same durable-credential conflict as BookingVideoRoom.

**Concurrency**

- unique `interviewId` + idempotent command/provider key prevent duplicate room resources.

**Retention/privacy**

- candidate/interviewer access context may be sensitive; no raw resume/interview content belongs here;
- Privacy executor owns Video-side deletion/anonymization only.

### 8.3 `CourseVideoAsset`

**Purpose:** Workin Ants state for one provider-hosted/processed on-demand course video.

**Key relationships**

- `courseDetailsId` → current Prisma relation to `CourseDetails.offeringId`;
- optional `offeringId` duplicates/overlaps the business reference concept;
- optional `sourceMediaAssetId` → Media-owned raw source;
- optional `createdByUserId` → User;
- one-to-many playback grants/events;
- one-to-many `CourseAccessibilityAsset` references, whose lifecycle remains Digital Goods-owned.

**Authoritative fields**

- `provider`, default `mux`;
- `status`, default `upload_pending`;
- `playbackPolicy`, default `signed`;
- provider asset/upload/playback references;
- provider-derived media metadata such as duration/aspect ratio/max resolution;
- `signedUrlTtlSeconds`, current default `3600`;
- processing/readiness/failure/deletion timestamps.

**Boundary-sensitive fields**

- `requiresPurchase` is a Video-local delivery configuration but may not override Order/Digital Goods entitlement truth.
- `isDownloadable` must not become downloadable-file entitlement; Digital Goods owns download policy/grants.
- `thumbnailUrl` must not become a durable private source-media URL.

**Schema conflict**

- `courseDetailsId` relation plus optional `offeringId` can diverge.
- **Unresolved:** establish one canonical cross-Module reference rule before migration/API reliance.

**Retention/privacy**

- delete provider asset only from authorized provider-resource deletion commands;
- raw MediaAsset deletion remains Media-owned;
- course/public business retention remains Marketplace/Digital Goods-owned.

### 8.4 `CourseVideoPlaybackGrant`

**Purpose:** temporary proof that one User may access one CourseVideoAsset under a named access basis.

**Key relationships**

- required CourseVideoAsset;
- required User;
- optional Order.

**Authoritative fields**

- `status`;
- provider/providerPlaybackId reference;
- token/playback URL hashes only;
- reason/deniedReason;
- minimized request evidence (`ipHash`, `userAgent`);
- `grantedAt`, `firstUsedAt`, `expiresAt`, `revokedAt`, `revokeReason`.

**Concurrency-sensitive concerns**

- no current uniqueness constraint prevents multiple active grants for the same user/asset/order;
- grant issuance must use SH-044 and transaction/lock policy;
- whether multiple active grants are valid is **Unresolved**.

**Lifecycle ambiguity**

- `used` exists, but current evidence does not establish whether grants are one-time or reusable until expiry.
- `active` is the only status that is unquestionably credential-eligible; exact `used` semantics require a decision.

### 8.5 `CourseVideoPlaybackEvent`

**Purpose:** append-only Video-specific streaming access/provider evidence.

**Important fields**

- asset/grant/user/order references;
- event `type`;
- provider/providerEventId;
- progress/duration;
- minimized request evidence;
- structured `metadata`.

**Rules**

- append-only;
- metadata must be schema-validated and sanitized;
- do not persist raw tokens, URLs, PHI, provider payloads, or unnecessary personal data;
- playback progress volume/retention policy is **Unresolved**.

### 8.6 `ProcessedVideoProviderEvent`

**Purpose:** exactly-once claim/processing proof for provider callbacks.

**Authoritative fields**

- `provider`, `providerEventId`, `status`;
- target type/id;
- normalized event type;
- payload hash;
- received/processed/failed timestamps and safe failure reason.

**Uniqueness**

- `@@unique([provider, providerEventId])` is binding dedupe evidence.

**Rules**

- verify webhook before claim;
- claim before domain side effects;
- provider payload itself is not persisted as business truth;
- `targetType` is currently a free string and requires controlled vocabulary in code/contracts.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 BookingVideoRoom

```text
pending
  ├─→ active
  ├─→ failed
  └─→ cancelled

active
  ├─→ expired
  └─→ cancelled
```

**Transition owner:** Video Session.

**Triggers:** room provision request/provider result; parent cancellation instruction; expiration worker; authorized privacy/moderation/security effect.

**Terminal behavior:** `expired` and `cancelled` do not issue credentials. `failed` does not issue credentials.

**Recovery:** whether a failed/current one-to-one room row returns to `pending` for re-provisioning or is replaced through an explicit reset is **Unresolved**. Do not invent a hidden retry transition.

**Concurrency:** `bookingId` uniqueness + SH-044 provider-command idempotency.

### 9.2 JobInterviewVideoRoom

Same provider-resource state vocabulary as BookingVideoRoom, but policy consumes JobInterview facts rather than Booking facts.

```text
pending → active | failed | cancelled
active  → expired | cancelled
```

Do not share Booking participant policy by assumption.

### 9.3 CourseVideoAsset

Current intended progression:

```text
draft
  → upload_pending
  → uploading
  → processing
  → ready

upload_pending/uploading/processing
  → failed

ready
  → disabled | archived | deleted
```

**Authorized restore/retry rules:**

- failed → upload_pending may be allowed only through explicit owner retry policy;
- disabled → ready may be allowed only after authoritative restore instruction and provider verification;
- archived/deleted reopen semantics are not established and must not be invented.

**Provider callbacks:** cannot transition the record until SH-059/060/061 complete.

### 9.4 CourseVideoPlaybackGrant

Current status vocabulary:

```text
active → expired | revoked | used

[denied] = explicit denied access proof if the command design persists denied grants
```

**Binding access rule:** only a currently allowed, non-expired, non-revoked grant may produce a playback credential.

**Unresolved:** whether `used` is terminal/single-use or merely first-use evidence. Until settled, do not introduce one-time semantics that conflict with course playback expectations.

### 9.5 ProcessedVideoProviderEvent

```text
received → processed | failed
replayed existing event → ignored_duplicate semantics/result
```

The unique provider/event key is authoritative. Duplicate callbacks must not repeat side effects.

### Prohibited lifecycle shortcuts

- provider success may not mutate Booking/JobInterview/Order/CourseDetails status;
- audit/log records may not be used in place of Video status;
- expired credentials may not remain valid because an expiry worker is delayed;
- client-side clocks may not authorize join/playback;
- unknown provider status may not be coerced to `ready`/`active`.

---

## 10. Commands

### `registerCourseVideoSource`

**Purpose:** create the Video-owned CourseVideoAsset against an eligible course and safe source media.

**Actor/context:** authorized course creator/admin/system actor.

**Authoritative inputs:** Course target reference/version; Media source reference/readiness; desired display metadata; requested provider/policy if allowed; idempotency key.

**Preconditions:** target exists and is eligible; Media source is ready/permitted; actor authorized; hold/healthcare policy applied where relevant.

**Writes:** `CourseVideoAsset` only.

**Shared operations:** SH-001, SH-002, SH-003/SH-123, SH-011 as applicable, SH-044, SH-046 when downstream ingest is asynchronous.

**Effects:** enqueue ingest; optionally publish registered event.

**Idempotency:** semantic key should bind course target + source MediaAsset + requested logical slot/version as defined by local policy.

**Failure modes:** invalid target, unauthorized, source not ready, hold, duplicate conflicting registration, stale target, persistence failure.

### `requestCourseVideoIngest`

**Purpose:** begin/retry provider ingest for a registered asset.

**Preconditions:** asset in an ingest-eligible state; safe Media source still available; provider configured.

**Writes:** Video asset ingest/provider reference/status through owner transition service.

**Shared operations:** SH-044, SH-047, SH-048, SH-068, SH-078, SH-037.

**Idempotency:** stable asset/provider ingest key; provider timeout must not create duplicate provider assets.

### `applyVideoProviderEvent`

**Purpose:** apply one verified provider callback to the appropriate Video-owned target.

**Inputs:** raw verified envelope after SH-059; provider event ID; normalized event details; correlation context.

**Writes:** `ProcessedVideoProviderEvent` and the affected Video record in the safe owner transaction pattern.

**Shared operations:** SH-059, SH-060, SH-061, SH-072, SH-053, SH-037.

**Failure modes:** invalid signature, duplicate, unknown event/status, target not found, stale transition, provider mismatch.

### `issueCoursePlaybackGrant`

**Purpose:** produce temporary Video access proof after authoritative purchase/context gates pass.

**Actor/context:** authenticated user; exact CourseVideoAsset; order or separately approved alternate basis.

**Preconditions:** asset ready; playback policy permits requested path; Order/context entitlement allows; Digital Goods conditions satisfied where required; hold/healthcare gates pass.

**Writes:** `CourseVideoPlaybackGrant`; optionally denial/access event according to approved design.

**Shared operations:** SH-001, SH-002, SH-011, SH-020 as applicable, SH-025, SH-026 as applicable, SH-044, SH-088, SH-125, SH-030 when sensitive.

**Idempotency:** same semantic access request should not multiply business entitlement or provider secrets.

### `issueCoursePlaybackCredential`

**Purpose:** return a short-lived provider-bound playback credential for an eligible grant.

**Preconditions:** current grant valid under server time; asset ready; current Order/hold/healthcare revalidation where policy requires; provider configured.

**Writes:** token/url hashes and Video playback event as approved; no reusable raw credential persisted.

**Shared operations:** SH-068, SH-074 where locally generated secret material is needed, SH-072, SH-125, SH-030.

### `revokeCoursePlaybackGrant`

**Purpose:** stop future playback after refund, moderation, privacy, security, or owner lifecycle change.

**Inputs:** grant/target; authoritative source instruction; reason/reference; idempotency key.

**Writes:** grant revocation state/event.

**Shared operations:** SH-089, SH-044, SH-125, SH-046.

### `provisionBookingVideoRoom`

**Purpose:** create or return the Video-owned provider room for an eligible confirmed video Booking.

**Context:** Booking owner facts are authoritative.

**Preconditions:** Booking confirmed/eligible, location type video, time/participants known, relevant entitlement/healthcare/hold gates pass, provider configured.

**Writes:** `BookingVideoRoom` and provider references/status.

**Shared operations:** SH-003/SH-123, SH-005 where applicable, SH-011, SH-020, SH-025 only if required by approved delivery policy, SH-044, SH-047/048, SH-068.

**Failure modes:** stale/non-video Booking, provider unavailable, healthcare not ready, hold, idempotency conflict.

### `provisionInterviewVideoRoom`

Same provider mechanism as Booking room provisioning but consumes JobInterview owner facts and participant roles. It must not read or write Booking tables.

### `issueVideoJoinCredential`

**Purpose:** issue participant-specific live access for either a Booking room or JobInterview room using a discriminated context contract.

**Preconditions:** actor authorized; parent owner facts currently permit access; room active; current server time inside approved join window; holds/healthcare pass.

**Writes:** no reusable credential truth. Required Video-domain access proof remains subject to the unresolved live-access-proof model; AccessAuditLog is requested where applicable.

**Shared operations:** SH-001, SH-002, SH-003, SH-020, SH-026, SH-030, SH-068, SH-074, SH-125 where the approved domain proof exists.

### `cancelVideoRoom`

**Purpose:** cancel/revoke a live provider resource after authoritative parent/moderation/privacy/security instruction.

**Writes:** Video room status and provider state only.

**Shared operations:** SH-044, SH-068/SH-070, SH-046, SH-037.

### `reconcileCourseVideoProviderState` / `reconcileLiveVideoProviderState`

**Purpose:** compare Video truth with provider state and safely repair only approved discrepancies.

**Shared operations:** SH-062, SH-047/048, SH-037.

**Rule:** provider is not promoted to source truth during reconciliation.

### `executeVideoPrivacyInstruction`

**Purpose:** execute a Privacy-owned target disposition against Video-owned rows and provider resources.

**Shared operations:** SH-095, SH-097, SH-098, SH-070, SH-089.

**Rule:** never create or complete PrivacyRequest/DataErasureJob locally.

---

## 11. Queries / Decisions

### `getCourseVideoProcessingStatus`

- **Consumers:** Marketplace Supply, Digital Goods, creator/admin/support surfaces.
- **Input:** CourseVideoAsset ID or approved course reference.
- **Result:** sanitized Video source truth: canonical status, safe provider name, readiness/failure category, timestamps, safe media metadata.
- **Type:** source truth/read model.
- **Consumer must not infer:** Offering publication eligibility, purchase entitlement, legal/compliance readiness.

### `getCoursePlaybackGrantStatus`

- **Consumers:** Digital Goods/player delivery surfaces, support.
- **Input:** actor + grant/asset context.
- **Result:** status, expiresAt, first-use/revocation facts, safe reason codes.
- **Type:** source truth/contextual facts.
- **Consumer must not infer:** Order paid state or permanent ownership.

### `getBookingVideoRoomStatus`

- **Consumers:** Booking & Calendar, Booking UI through its owner surface, support.
- **Result:** room status, safe provider identity, setup/failure state, starts/ends/expires context.
- **Consumer must not infer:** Booking status from room status.

### `getInterviewVideoRoomStatus`

Same shape but tied to JobInterview context. It must not return or imply Booking facts.

### `evaluateCoursePlaybackReadiness` — internal/public decision as needed

**Inputs:** asset, actor, entitlement decision, hold/healthcare/digital-policy facts.

**Result:** stable `allow | deny | retry_later | review` decision plus reason code/evidence references.

**Type:** Video-local composition decision over external facts.

**Must not infer:** external owner truth from copied rows or provider objects.

### `evaluateLiveJoinReadiness` — internal decision

**Inputs:** room, current server time, source-owner facts, actor authorization, hold/healthcare result.

**Result:** allowed/denied with credential bounds and stable reason code.

**Local ownership:** time-window/resource-readiness composition only.

---

## 12. Public Module Interface

Public contracts are the preferred boundary. Consumers must not import Video repositories or provider adapters.

### Public commands

- `registerCourseVideoSource`
- `requestCourseVideoIngest`
- `issueCoursePlaybackGrant`
- `issueCoursePlaybackCredential`
- `revokeCoursePlaybackGrant`
- `provisionBookingVideoRoom`
- `provisionInterviewVideoRoom`
- `issueVideoJoinCredential`
- `cancelBookingVideoRoom`
- `cancelInterviewVideoRoom`
- `applyVideoProviderEvent` — internal/provider-facing application boundary
- `reconcileCourseVideoProviderState` — authorized system/admin command
- `reconcileLiveVideoProviderState` — authorized system/admin command

### Public queries

- `getCourseVideoProcessingStatus`
- `getCoursePlaybackGrantStatus`
- `getBookingVideoRoomStatus`
- `getInterviewVideoRoomStatus`

### Emitted domain events

Exact envelope follows SH-046. Initial Module-owned event names are:

- `video.course_asset.registered.v1`
- `video.course_asset.ready.v1`
- `video.course_asset.failed.v1`
- `video.course_playback.granted.v1`
- `video.course_playback.denied.v1`
- `video.course_playback.revoked.v1`
- `video.booking_room.active.v1`
- `video.booking_room.failed.v1`
- `video.booking_room.cancelled.v1`
- `video.interview_room.active.v1`
- `video.interview_room.failed.v1`
- `video.interview_room.cancelled.v1`

Events state facts that already occurred. They do not command Booking, JobInterview, Order, Marketplace, or Digital Goods to mutate their truth.

### Privacy executor

- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- export serializer/contribution where Privacy requests it

### Provider-facing interfaces

- `LiveVideoProviderPort`
- `StreamingVideoProviderPort`
- provider webhook verifier adapter implementations under SH-059
- provider status translators under SH-061
- provider deletion methods under SH-070

`SH-068 invokeVideoProvider` is the canonical Video provider interface boundary. Provider clients are not public Module API.

---

## 13. Inbound Dependencies

| Owning Module / platform | Public operation consumed | Why required | Minimum information | Can block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | Identify user/admin/system actor | actor ID/type/session assurance | Yes | auth/session helpers |
| Role / Authority | SH-002 `authorizeResourceAction` | Authorize creator/admin/join/retry actions | actor, action, target facts/scope | Yes | role interpretation |
| Booking & Calendar | SH-003 `queryOwnerFacts` / owner-specific Booking facts; SH-123 target validation | Provision/join/cancel Booking room | booking ID/version/status/location type/start/end/overtime/participants | Yes | Booking repository/status logic |
| Job Interview | owner-specific SH-003/SH-123 facts | Provision/join/cancel interview room | interview ID/version/status/time/participants/roles | Yes | hiring lifecycle/participant policy |
| Transaction / Order | SH-025 `authorizeOrderEntitlement` | Purchased course playback | order ID/state, participant, qualifying item, refund/dispute effects, evidence | Yes | payment/order checks |
| Marketplace Supply | SH-123 / owner facts for CourseDetails | Validate course target/reference | course/Offering ID, owner/status/version, relationship eligibility | Yes | course lifecycle |
| Media / File Access | ready-source/readiness public contract | Safely ingest source video | MediaAsset ID, ready/frozen/deleted state, safe provider-ingest access/reference | Yes | R2, scan, MIME, malware logic |
| Digital Goods Access | contextual access/policy facts | Enforce required terms/license/delivery policy without owning it | policy/acceptance facts needed for playback action | Yes when policy requires | terms/refund/license truth |
| Track Subscription & Entitlement | SH-005 `resolveEntitlement` | Gate live streaming where configured | actor/profile, entitlement key, effective decision/evidence | Conditional | premium flags |
| Healthcare / Regulated Services | SH-020 `evaluateHealthcareReadiness` | Gate healthcare-sensitive provider path/access | target, provider, BAA/data-boundary decision/version | Yes | HIPAA/BAA policy |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | Reusable stop-sign check | target/action, hold IDs/reasons/expiry | Yes | local blocked state |
| Audit / Event Ledger | SH-030 `recordSensitiveAccess` | Generic sensitive-access proof | actor, action, target, sensitivity, decision, request context | No for business truth; audit failure handling follows root policy | local access audit table |
| Notification | SH-041 `requestNotification` | User/operator notification when defined by source policy | recipient refs/template key/safe variables | No to Video truth by default | email/SMS/push clients |
| Observability / Ops | SH-032/034/037 and platform logging/metrics | Trace provider/worker failures safely | safe target/provider/operation/correlation | No | local incident/failure systems |
| Privacy / Data Erasure | SH-095–099 protocol | Execute approved privacy target | target/disposition/exemption references | Yes for destructive action | privacy request orchestration |
| Content Moderation & Legal Notice | SH-103 `executeModerationDecision` envelope | Disable/restore/revoke Video access after authoritative decision | case/action IDs, target, action, reason/reference | Yes | DMCA/legal adjudication |

### Dependency rule

If a dependency public interface does not yet exist, Video may build against its typed contract/test double. It must not temporarily import the source Module’s repository and convert that shortcut into architecture.

---

## 14. Outbound Consumers and Effects

### Booking & Calendar

Consumes:

- room setup status;
- room active/failed/cancelled events;
- safe setup diagnostic facts.

Booking may update its `BookingOrchestrationStep` acknowledgment based on the Video command result. It must not directly mutate `BookingVideoRoom`.

### Job Interview

Consumes:

- interview-room status;
- active/failed/cancelled events;
- join credential command for authorized participant flows.

It must not reuse Booking tables or provider clients.

### Marketplace Supply / Digital Goods

Consume:

- course-video processing readiness;
- ready/failed/disabled events;
- playback access command/query.

They retain course product/publication/license/refund/access-policy truth.

### Healthcare / Regulated Services

May consume safe evidence that Video provider resources/access were created or denied for a healthcare-sensitive target. Healthcare does not become Video provider-resource owner.

### Audit / Observability

Receive:

- sensitive-access requests;
- generic administrative audit requests where policy requires;
- normalized integration failures, metrics, and safe telemetry.

### Privacy / Moderation

Receive typed execution acknowledgments for provider deletion, revocation, disablement, restoration, anonymization, or retention.

### Notification

Receives only business-trigger intent and safe template variables. No raw join/playback credential belongs in asynchronous notification payloads unless a separately approved secure-delivery design exists.

---

## 15. Canonical Shared Operations Used

Only the operations below are part of Video Session’s expected architecture. The global registry remains authoritative for their full definition.

### SH-001 — `resolveAuthenticatedActor`

- **Classification:** canonical shared capability.
- **Owner:** Identity & Access.
- **Why used:** all user/admin token, grant, room, retry, and read actions require trusted actor context.
- **Invocation:** first protected application boundary.
- **Local policy:** requested Video action and target.
- **Expected result:** trusted typed actor or authentication denial.
- **Do not build:** `videoAuth.ts`, `getVideoUser.ts`, provider-room identity as auth.

### SH-002 — `authorizeResourceAction`

- **Classification:** canonical shared capability.
- **Owner:** Role / Authority.
- **Why used:** creator/admin/support and contextual participant actions require server-side authorization.
- **Invocation:** after actor resolution and before protected mutation/read/credential issue.
- **Local policy:** Video action vocabulary and Video-owned relationship facts; parent owner supplies parent facts.
- **Do not build:** standalone `videoParticipantGuard.ts`, organization-role parser.

### SH-003 — `queryOwnerFacts` — Proposed Ruling

- **Classification:** shared contract / separate implementations.
- **Owner:** each source Module.
- **Why used:** Booking, JobInterview, CourseDetails, and related owner facts must cross boundaries without direct repositories.
- **Invocation:** provisioning/access commands.
- **Local policy:** which minimum fields Video requires.
- **Do not build:** universal cross-domain repository.

### SH-005 — `resolveEntitlement`

- **Classification:** canonical commercial-policy capability.
- **Owner:** Track Subscription & Entitlement.
- **Why used:** live-streaming entitlement where an approved product/track rule requires it.
- **Invocation:** before applicable live room/access action.
- **Local policy:** which Video action consumes the entitlement and whether historical evidence must be retained.
- **Do not build:** `canLiveStream.ts`, `videoPremiumCheck.ts`.

### SH-011 — `evaluateComplianceHold`

- **Classification:** canonical shared capability.
- **Owner:** Admin Review / Compliance Hold.
- **Why used:** active holds may block grant issuance, room access, provider mutations, or administrative actions.
- **Invocation:** immediately before the hold-sensitive owner action.
- **Local policy:** mapping hold decision to Video denial/revocation behavior.
- **Do not build:** `videoHoldService.ts`, local generic blocked columns.

### SH-020 — `evaluateHealthcareReadiness`

- **Classification:** another Module’s public interface.
- **Owner:** Healthcare / Regulated Services.
- **Why used:** healthcare-sensitive live or streaming access requires approved provider/BAA/data-boundary decision.
- **Invocation:** provider selection/provisioning and credential issuance when healthcare context applies.
- **Local policy:** enforce the returned decision against selected Video operation.
- **Do not build:** `videoHipaaCheck.ts`, provider BAA booleans.

### SH-025 — `authorizeOrderEntitlement`

- **Classification:** another Module’s public interface.
- **Owner:** Transaction / Order.
- **Why used:** normal paid course playback must be based on authoritative Order entitlement.
- **Invocation:** playback grant and current-access revalidation where policy requires.
- **Local policy:** map qualifying order item/action to the exact CourseVideoAsset.
- **Do not build:** `isOrderPaid.ts`, Stripe reads, local purchase checker.

### SH-026 — `authorizeContextualResourceAccess`

- **Classification:** shared contract / separate policy.
- **Owner:** relevant context owner.
- **Why used:** parent/context owner must supply business-context access facts before Video emits credentials.
- **Invocation:** join/playback access composition.
- **Local policy:** Video readiness/time/room/grant rules remain local.
- **Do not build:** generic service that infers every context itself.

### SH-030 — `recordSensitiveAccess`

- **Classification:** canonical shared capability.
- **Owner:** Audit / Event Ledger.
- **Why used:** healthcare/sensitive video joins, credential issuance/denial, and other policy-defined access must create generic sensitive-access proof.
- **Invocation:** after a final access decision/credential issuance as required by audit policy.
- **Local policy:** sensitivity/action/target metadata.
- **Do not build:** `videoAuditLog.ts`, `joinAudit.ts`.

### SH-032 — `createRequestContext`

- **Classification:** platform primitive.
- **Owner:** Observability/platform.
- **Why used:** correlate API, job, provider, event, audit, and reconciliation work.
- **Invocation:** request/job entry.
- **Local policy:** safe target/operation labels only.
- **Do not build:** Video-specific correlation IDs.

### SH-034 — `sanitizeTelemetryMetadata`

- **Classification:** canonical cross-cutting capability.
- **Owner:** Observability / Ops + Audit payload policy.
- **Why used:** prevent tokens, URLs, PHI, provider payloads, and unnecessary PII from logs/audit metadata.
- **Invocation:** before telemetry/audit serialization.
- **Local policy:** Video sensitivity labels/allowlist.
- **Do not build:** ad hoc provider payload logging sanitizer.

### SH-037 — `recordIntegrationFailure`

- **Classification:** canonical cross-cutting capability.
- **Owner:** Observability / Ops.
- **Why used:** provider/worker failure evidence without replacing Video status.
- **Invocation:** normalized provider/worker terminal or material degraded failure.
- **Local policy:** safe Video target, operation, retryability, canonical Video outcome.
- **Do not build:** `muxFailureTable`, `videoIncidentService`.

### SH-041 — `requestNotification`

- **Classification:** canonical shared capability.
- **Owner:** Notification.
- **Why used:** user/operator notification only where a Video/domain workflow explicitly requires one.
- **Invocation:** after committed Video fact/event.
- **Local policy:** trigger meaning and safe variables.
- **Do not build:** video email/SMS/push providers.

### SH-044 — `executeIdempotentCommand`

- **Classification:** platform primitive.
- **Owner:** platform application infrastructure.
- **Why used:** provider creation, grant issuance, revocation, deletion, and retry commands must yield one semantic effect.
- **Invocation:** mutation boundary before provider/domain effect.
- **Local policy:** semantic key, request fingerprint, conflict/replay semantics.
- **Do not build:** `muxIdempotency.ts`, `createRoomOnce.ts` storage.

### SH-046 — `publishDomainEvent`

- **Classification:** platform primitive.
- **Owner:** event/outbox infrastructure.
- **Why used:** publish committed Video facts reliably.
- **Invocation:** same source transaction/outbox boundary as owner mutation.
- **Local policy:** Video event name/version/payload/privacy.
- **Do not build:** fire-and-forget provider/domain event emitter.

### SH-047 — `enqueueReliableJob`

- **Classification:** platform primitive.
- **Owner:** shared queue infrastructure.
- **Why used:** ingest, provider provisioning, expiration, deletion, and reconciliation require durable async work.
- **Invocation:** after committed intent/outbox when work is slow/provider-dependent.
- **Local policy:** job payload and completion meaning.
- **Do not build:** `muxQueue.ts`, `videoQueue.ts` framework.

### SH-048 — `executeRetryWithBackoff`

- **Classification:** platform primitive.
- **Owner:** shared queue/platform infrastructure.
- **Why used:** transient provider errors.
- **Invocation:** owner worker around retryable adapter calls.
- **Local policy:** retryable vs terminal error classification.
- **Do not build:** local `retry.ts` framework.

### SH-051 / SH-052 / SH-053 — locking, optimistic concurrency, lifecycle transition plumbing

- **Classification:** platform/shared mechanisms with separate Video policy.
- **Owners:** shared persistence infrastructure / lifecycle owner policy.
- **Why used:** grant/revocation/room/asset races and stale transitions.
- **Invocation:** owner mutation transaction.
- **Local policy:** lock key, expected version, Video transition graph.
- **Do not build:** in-memory mutexes or generic Video-owned state-machine infrastructure that is reusable platform plumbing.

### SH-055 — `runDeadlineExpiration`

- **Classification:** shared scheduler capability.
- **Owner:** shared scheduler/queue infrastructure.
- **Why used:** expire playback grants and live rooms.
- **Invocation:** scheduled batch dispatch to Video owner commands.
- **Local policy:** expiry criteria and owner transition.
- **Do not build:** Video-specific cron framework.

### SH-059 — `verifyProviderWebhookSignature`

- **Classification:** provider-adapter contract.
- **Owner:** shared security shell; adapter supplies algorithm.
- **Why used:** authenticate Mux/Daily/future callbacks.
- **Invocation:** raw webhook boundary before parse/side effect.
- **Local policy:** provider secret/algorithm/tolerance/accepted events.
- **Do not build:** route-local signature utility.

### SH-060 — `deduplicateProviderEvent`

- **Classification:** shared mechanism / separate truth.
- **Owner:** Video Session using shared primitive.
- **Why used:** prevent duplicate callbacks.
- **Invocation:** after verification and before domain mutation.
- **Local policy:** `ProcessedVideoProviderEvent` schema and target mapping.
- **Do not build:** generic processed-provider-event business table.

### SH-061 — `translateProviderStatus`

- **Classification:** provider-adapter pattern.
- **Owner:** Video provider adapter.
- **Why used:** provider-native statuses/errors cannot leak into Video domain.
- **Invocation:** provider response/webhook normalization.
- **Local policy:** provider-to-Video status mapping and unknown-status behavior.
- **Do not build:** platform-wide global status mapper.

### SH-062 — `reconcileProviderState`

- **Classification:** shared mechanism / separate policy.
- **Owner:** Video Session using shared worker framework.
- **Why used:** missed callbacks/partial provider effects.
- **Invocation:** scheduled/manual reconciliation.
- **Local policy:** safe discrepancy repair matrix.
- **Do not build:** provider state as source truth.

### SH-068 — `invokeVideoProvider`

- **Classification:** Module provider interface.
- **Owner:** Video Session.
- **Why used:** canonical provider-neutral boundary for rooms, assets, and credentials.
- **Invocation:** Video workers/services only.
- **Local policy:** live/on-demand resource mapping, token claims, provider selection.
- **Expected contract:** normalized success/failure/provider reference; no provider DTO leakage.
- **Do not build:** Daily/Agora/Mux calls from Booking, Job Interview, Digital Goods, or Marketplace.

### SH-070 — `deleteProviderResource`

- **Classification:** provider-adapter contract.
- **Owner:** provider-owning Module (Video here).
- **Why used:** execute Privacy/Moderation/security deletion/revocation.
- **Invocation:** authorized owner target executor.
- **Local policy:** resulting Video status and safe retained evidence.
- **Do not build:** Privacy directly calling Mux/Daily.

### SH-072 — `hashCanonicalPayload`

- **Classification:** platform cryptography primitive.
- **Owner:** shared security.
- **Why used:** payload/token/url evidence where a stable digest is needed.
- **Invocation:** before persistence of proof hash.
- **Local policy:** canonical inputs and what the hash proves.
- **Do not build:** `hashVideoUrl.ts`, local SHA helpers.

### SH-074 — `generateSecureToken`

- **Classification:** platform security primitive.
- **Owner:** shared security.
- **Why used:** locally generated short-lived secret material if provider contract requires it.
- **Invocation:** credential/grant issuance.
- **Local policy:** TTL, actor/target binding, usage/revocation.
- **Do not build:** custom random token generator.

### SH-078 — `minimizeAndRedactProviderInput`

- **Classification:** canonical cross-cutting capability.
- **Owner:** source-data owner supplies policy; shared serializer enforces.
- **Why used:** only minimum purpose-bound fields may be sent to video providers.
- **Invocation:** immediately before provider call.
- **Local policy:** Video provider allowlist for each operation/sensitivity lane.
- **Do not build:** raw domain-object forwarding.

### SH-088 — `manageTemporaryAccessGrant`

- **Classification:** shared mechanism / separate truth.
- **Owner:** shared grant mechanism; Video owns CourseVideoPlaybackGrant policy/record.
- **Why used:** standard issue/validate/expire/deny/use/revoke plumbing.
- **Invocation:** playback grant lifecycle.
- **Local policy:** CourseVideoPlaybackGrant semantics.
- **Do not build:** generic `TemporaryGrant` table or reuse Media/DigitalDownload grants.

### SH-089 — `revokeTemporaryAccessGrant`

- **Classification:** shared command pattern / separate owner transition.
- **Owner:** Video for Video grant.
- **Why used:** refund/moderation/privacy/security/lifecycle revocation.
- **Invocation:** authoritative revocation instruction.
- **Local policy:** affected grants and resulting Video event.
- **Do not build:** cross-domain grant updater.

### SH-095 / SH-096 / SH-097 / SH-098 — Privacy owner-executor protocol

- **Classification:** canonical cross-cutting protocol and shared anonymization primitive.
- **Owner:** Privacy orchestrates; Video executes its records.
- **Why used:** inventory/export/retention/execution for rooms/assets/grants/events/provider refs.
- **Invocation:** Privacy-owned target workflow.
- **Local policy:** Video data inventory, field anonymization, provider deletion, grant revocation, safe retained evidence.
- **Do not build:** `videoPrivacyRequest`, `videoErasureJob`, local retention-exemption table.

### SH-103 — `executeModerationDecision`

- **Classification:** cross-cutting protocol.
- **Owner:** Moderation owns decision; Video executes.
- **Why used:** disable/restore course playback, revoke grants, or remove provider resource after authoritative action.
- **Invocation:** signed/authorized moderation envelope.
- **Local policy:** mapping to Video transitions/provider calls.
- **Do not build:** DMCA/legal adjudication in Video.

### SH-123 — `validateOwnedTargetReference`

- **Classification:** shared contract / separate implementations.
- **Owner:** target owner.
- **Why used:** validate Booking/JobInterview/CourseDetails/Media references without direct source repositories.
- **Invocation:** command boundary before cross-owner relationship creation.
- **Local policy:** relationship type required by Video.
- **Do not build:** cross-domain Prisma existence checker.

### SH-125 — `recordDomainAccessEvent`

- **Classification:** shared append-only mechanism / separate truth.
- **Owner:** Video for Video-specific access evidence.
- **Why used:** playback access/progress/completion evidence and any approved live-access evidence.
- **Invocation:** after domain access decision/effect.
- **Local policy:** Video action/reason/provider/context fields.
- **Do not build:** generic `deliveryLog` replacing Video-specific evidence.

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `selectVideoProvider` | Select approved provider for live or streaming operation | operation/context/healthcare decision/config | provider key or denial | none | provider choice is Video capability policy |
| `calculateLiveJoinWindow` | Convert owner scheduling facts into credential-valid interval | start/end/overtime/provider constraints | notBefore/expiresAt | none | only Video knows credential window mechanics |
| `mapParticipantToProviderClaims` | Translate buyer/professional/candidate/interviewer facts into provider-scoped claims | context role + target | provider-neutral claim set | none | Video provider access semantics |
| `evaluateCourseAssetReadiness` | Determine whether asset state can issue playback | asset + current gates | decision/reason | none | Video resource readiness |
| `evaluatePlaybackGrantValidity` | Check grant status/expiry/target binding | grant + server time + actor | decision/reason | none | grant lifecycle is Video-owned |
| `translateVideoProviderEventTarget` | Map provider event to Booking room/interview room/course asset | provider event references | typed Video target | none | target mapping stays in provider owner |
| `classifyVideoProviderFailure` | Mark failure retryable/terminal/manual | normalized adapter error | failure class | none | provider operation semantics local |
| `applyCourseVideoProviderTransition` | Apply safe canonical asset transition | current asset + normalized provider result | updated asset | CourseVideoAsset | lifecycle owner only |
| `applyLiveRoomProviderTransition` | Apply safe canonical room transition | room + provider result | updated room | room record | lifecycle owner only |
| `buildSafeVideoStatusView` | Return sanitized status without secrets | Video record | public DTO | none | protects provider/security boundary |
| `buildVideoPrivacyDisposition` | Map Privacy instruction to local record/provider actions | target + retention result | executor plan | Video records/provider | owner knows local schema/resources |

---

## 17. Shared Mechanism / Separate Truth Rules

### Temporary access grants

Use SH-088 mechanics, but keep:

- `CourseVideoPlaybackGrant` separate from `MediaAccessGrant`;
- separate from `DigitalDownloadGrant`;
- separate from `AgreementAccessGrant`;
- separate from `SensitiveActionSession`.

No generic `AccessGrant` table may replace these truths.

### Provider-event dedupe

Use SH-060 implementation pattern while retaining `ProcessedVideoProviderEvent` as Video truth. Never merge it with Stripe/calendar/verification webhook ledgers.

### Lifecycle plumbing

SH-053 may provide transition validation/update hooks. The Video transition graph remains here; there is no generic database table that owns all statuses.

### Hashing/tokens

Use SH-072/074. Video defines the purpose, bindings, TTL, and evidence meaning. Shared cryptography does not own Video access policy.

### Reconciliation

SH-062 provides worker shape. Video defines which discrepancies are safe to repair, which require failure state, and which require manual review.

### Domain access evidence

Use SH-125 append-only pattern. `CourseVideoPlaybackEvent` remains Video truth. Generic AccessAuditLog remains separate.

### Live room mechanism

Booking and JobInterview rooms should share internal provider/credential mechanics where the policy is actually common, but they remain separate records with separate parent facts and authorization adapters.

---

## 18. Authentication and Authorization

### Actor requirement

All protected user/admin commands and credential issuance require SH-001 actor resolution. System workers use a typed system actor/service context according to root architecture.

### Role / Authority

SH-002 interprets permission. Video supplies the requested action and Video resource facts; source Modules supply parent-context facts.

### Resource ownership/context

**Course creator/admin actions** require course/Offering owner facts from Marketplace Supply and authority decision.

**Booking join** requires:

- Booking owner facts identifying buyer/professional participants;
- current Booking status/type/time facts;
- SH-002 authorization/contextual decision;
- Video room readiness/time-window policy.

**JobInterview join** requires:

- JobInterview participant facts/roles from CL-06;
- organization/participant authority from the appropriate owner/Role Module;
- Video room readiness/time-window policy.

### Admin/support

Admin/support does not imply unrestricted provider credential or healthcare access. Sensitive support diagnostics must be sanitized and may require healthcare policy, AccessAuditLog, and root step-up policy.

### Step-up

The exact CL-05 Video step-up matrix is unresolved. Do not add ad hoc MFA checks. If a Video action is later designated sensitive, consume SH-014 through Identity & Access.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Truth owner | Operation consumed | Video action gated | Video-local composition | Result |
| --- | --- | --- | --- | --- | --- |
| Authentication | Identity & Access | SH-001 | all protected actions | none beyond action context | actor or deny |
| Authorization | Role / Authority + source facts | SH-002 | create/status/join/admin actions | Video target/action vocabulary | allow/deny |
| Compliance hold | Admin Review / Compliance Hold | SH-011 | grant issue, join, provider mutation where mapped | map hold to deny/revoke/defer | allow/deny |
| Purchase entitlement | Transaction / Order | SH-025 | normal paid course playback | asset/order item mapping + Video readiness | allow/deny |
| Contextual resource access | context owner | SH-026 | joins/playback where owner-specific business context applies | room/grant/time policy | allow/deny |
| Track entitlement | Track Subscription & Entitlement | SH-005 | live streaming only where product policy requires | determine whether the specific operation consumes perk | allowed/not entitled |
| Healthcare readiness | Healthcare / Regulated Services | SH-020 | healthcare-sensitive room/streaming provider and access | enforce provider/access outcome | permitted/blocked/redacted/review |
| Digital goods terms/policy | Digital Goods Access / Consent where relevant | owner public facts / consent proof | course playback where required | combine external policy proof with Video readiness | allow/deny |
| Moderation/legal | Content Moderation | SH-103 execution instruction | asset disable/restore/provider resource access | map action to Video transition | acknowledged/completed/failed |
| Privacy/retention | Privacy + data owner facts | SH-095–098 | revoke/delete/anonymize/retain | local disposition only | typed executor result |

### Gate ordering

For credential issuance, perform cheap trust/authorization checks before provider calls. No provider credential should be created before all required current gates pass.

---

## 20. Provider Integrations

### 20.1 Provider-neutral ports

`SH-068 invokeVideoProvider` is implemented as two distinct ports:

```text
LiveVideoProviderPort
- createRoom
- cancelRoom
- issueParticipantCredential
- getRoomState
- deleteRoomOrLogs where supported

StreamingVideoProviderPort
- createUploadOrIngest
- getAssetState
- issuePlaybackCredential
- disablePlayback
- restorePlayback where supported
- deleteAsset
```

Provider-specific DTOs remain adapter-private.

### 20.2 On-demand provider — Mux

**Binding current target:** Mux is the current MVP on-demand course-video provider.

Required adapter behavior:

- idempotent ingest/create request where provider permits;
- normalized asset/upload/playback references;
- signed playback credential generation;
- webhook signature verification through SH-059;
- event dedupe through `ProcessedVideoProviderEvent`/SH-060;
- explicit status/error translation through SH-061;
- reconciliation through SH-062;
- provider resource deletion through SH-070;
- payload minimization through SH-078;
- no raw source `.mp4` public URL.

### 20.3 Live provider — proposed Daily.co MVP adapter

The schema defaults both live room provider enums to `daily`, and the current Project Overview names Daily.co for MVP. The Module extract also names Agora and older evidence mentions AWS Chime.

**Proposed Ruling:**

- build `LiveVideoProviderPort` now;
- use a test adapter until production provider commitment is needed;
- after explicit architecture approval, implement Daily.co as the MVP live adapter;
- do not implement Agora/AWS Chime in the same MVP slice solely because enum/registry evidence mentions them.

### 20.4 Credentials

- provider API credentials and signing keys are server-only;
- no provider secret belongs in Prisma domain records;
- access credentials are short-lived and actor/target/purpose bound where provider supports it;
- durable proof stores hash/reference only where required;
- never log raw join/playback credentials.

### 20.5 Webhook pipeline

```text
raw request bytes
→ SH-059 verifyProviderWebhookSignature
→ parse validated provider envelope
→ SH-060 claim ProcessedVideoProviderEvent
→ SH-061 translateProviderStatus/event
→ resolve Video target
→ apply Video-owned transition + evidence
→ mark processed
→ SH-046 publish resulting Video fact if needed
```

A signature failure or duplicate event has no Video side effect.

### 20.6 Reconciliation

Scheduled/manual reconciliation:

1. select stale/pending/failed-retryable Video records;
2. query provider through adapter;
3. normalize state;
4. compare with Workin Ants Video truth;
5. dry-run/report discrepancy where required;
6. execute only explicitly safe repair commands;
7. record IntegrationFailure/manual review for unsafe discrepancies.

### 20.7 Privacy deletion

Privacy/Moderation never call Mux/Daily directly. Video receives an authorized instruction, performs provider deletion/revocation, updates Video-local state as permitted, and returns a typed result.

---

## 21. Events and Outbox

### Event envelope

All emitted events use SH-046 with:

- globally unique event ID;
- event name + schema version;
- source Module `video_session`;
- aggregate type/ID;
- aggregate version or updatedAt/version evidence where available;
- occurredAt;
- correlation ID;
- causation ID/source command/event;
- safe minimal payload.

### Event payload rules

Do not include:

- join credentials;
- signed playback URLs/tokens;
- provider secrets;
- raw provider webhook payloads;
- PHI/private course content;
- unnecessary IP/user-agent detail.

### Outbox rule

When a committed Video state change requires downstream reaction, persist the Video state change and outbox record in the same owner transaction where root infrastructure permits. Provider side effects are coordinated through intent + durable jobs rather than untracked fire-and-forget calls.

### Consumer idempotency

Consumers use SH-045/event inbox infrastructure. Video events do not guarantee that a consumer has processed the fact exactly once; they guarantee reliable publication with idempotent consumer expectations.

### Events are facts, not commands

`video.booking_room.active.v1` means the Video room became active. It does not command Booking to mark itself confirmed.

---

## 22. Background Jobs / Scheduled Work

| Worker | Purpose | Input/owner | Idempotency key | Retryable | Permanent/manual | Truth updated | Telemetry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Course video ingest worker | create/continue provider ingest | CourseVideoAsset | asset + provider + ingest generation | timeout/5xx/rate limit | invalid source/config/unsupported provider | CourseVideoAsset | provider/op/attempt/correlation |
| Video provider event worker | apply verified callback if async dispatch is used | ProcessedVideoProviderEvent | provider + event ID | transient DB/provider lookup | invalid mapping/unsafe transition | provider event + target | dedupe/latency/failure |
| Playback grant expiration worker | expire due grants | grant IDs/cursor | grant + expiry generation | DB transient | invalid state handled deterministically | CourseVideoPlaybackGrant | count/age/failure |
| Live room expiration worker | expire/cancel provider access after deadline | room IDs/cursor | room + expiry generation | provider transient for cleanup | unsafe discrepancy/manual review | room state + provider cleanup evidence | count/provider failure |
| Provider reconciliation worker | detect/repair missed callbacks/partial effects | stale records/provider refs | target + reconciliation window/version | technical provider failure | unsafe discrepancy | Video target when safe | discrepancy counts/repair |
| Privacy provider deletion worker | delete/revoke external Video resource | Privacy target | privacy target ID + provider resource | provider transient | retention/unsupported/manual | Video local effect + typed Privacy result | safe deletion outcome |

Generic queue mechanics use SH-047/048/038. No local Video queue framework.

---

## 23. Concurrency and Idempotency

### Primary races

1. duplicate course ingest requests creating duplicate Mux assets;
2. duplicate Booking/Interview room requests creating multiple provider rooms;
3. webhook replay or callback/request race changing the same asset/room twice;
4. grant issuance retries creating multiple active grants;
5. grant use vs expiry vs revocation;
6. room cancellation/expiry vs credential issue;
7. moderation/privacy revocation vs new credential issue;
8. reconciliation vs live webhook/command transition.

### Lock/identity keys

- Booking room aggregate: `booking:{bookingId}`;
- Interview room aggregate: `job-interview:{interviewId}`;
- Course asset aggregate: `course-video-asset:{id}`;
- Playback grant aggregate: `course-playback-grant:{id}`;
- provider event claim: `(provider, providerEventId)` unique key;
- ingest semantic command: asset/provider/ingest generation;
- room provision semantic command: parent target + provider configuration generation.

### Database strategy

- use existing unique constraints first;
- use SH-051 row/advisory locks or transaction serialization for conflicting owner mutations;
- use SH-052 optimistic concurrency where repository/version conventions support it;
- never use in-memory mutexes as distributed correctness mechanisms.

### Command idempotency

A replay with the same semantic key/fingerprint returns the original semantic result. A reuse of the same key with conflicting material input returns an idempotency conflict rather than silently performing a second action.

### Provider idempotency

Use provider-supported idempotency/passthrough fields where available, but provider idempotency never replaces Workin Ants SH-044/database uniqueness.

---

## 24. Media / Storage

### Source media

Course-video ingest consumes a ready, permitted Media-owned `MediaAsset`. Video does not run upload validation, malware scanning, MIME checks, EXIF scrubbing, or raw-object storage.

### Provider ingest handoff

The exact Media-to-provider source handoff must use a Media public interface that reveals only what the provider ingest operation needs. Video must not import the R2 storage repository or generate R2 presigned URLs directly.

**Unresolved:** whether the handoff is a short-lived Media-issued source URL, server-side stream, provider upload destination, or another approved mechanism.

### Public/private status

- raw source files remain private;
- paid/private course playback uses short-lived provider credentials;
- no raw `.mp4` URL is a public delivery mechanism;
- provider thumbnail exposure must follow the unresolved thumbnail/public-safety ruling.

### Accessibility assets

`CourseAccessibilityAsset` is related to CourseVideoAsset but is owned by Digital Goods Access. Video may return safe linkage/readiness references; it must not transition accessibility status.

---

## 25. Search / Projection

Video Session owns no Typesense/Search projection and does not write `SearchUpsertEvent`.

`CourseVideoAsset.ready/failed/disabled` may be an input to Marketplace/Digital Goods public-readiness policy. Video should expose source facts or emit domain events; the owning public-readiness workflow decides whether SH-091 Search refresh is required.

Search must not reconstruct Video readiness from provider APIs.

---

## 26. Notification

Video defines only trigger intent where appropriate, for example:

- course video processing failed and requires creator action;
- live room provisioning failed before a confirmed Booking;
- support/admin reconciliation requires attention.

Notification owns templates, channels, persistence, retry, and delivery.

Notification payloads must never contain reusable provider secrets or raw signed credentials. If a user needs to join/play, the notification links back to an authenticated Workin Ants route that re-evaluates access and issues a fresh credential.

---

## 27. Audit and Sensitive Access

### Video domain evidence

- `CourseVideoPlaybackEvent` records Video-specific playback facts.
- `ProcessedVideoProviderEvent` records provider-event dedupe/processing facts.
- room status fields record live provider-resource lifecycle.

### Generic AuditEvent

Use SH-029 for material administrative actions when root audit policy requires it, such as authorized manual reconciliation, provider resource deletion, or sensitive restore/retry.

### AccessAuditLog

Use SH-030 for healthcare/sensitive access and other approved credential issuance/denial actions.

### Separation rule

```text
Video lifecycle/access record = what happened in Video truth
AuditEvent = generic material action proof
AccessAuditLog = sensitive-access proof
IntegrationFailure/log/metric = operational diagnosis
```

None replaces another.

### Live access evidence gap

The schema has `AccessAuditAction.live_video_token_issued`, but no Video-owned live grant/access event model equivalent to `CourseVideoPlaybackEvent`. This is unresolved and must be settled before claiming complete Video-specific live-access proof.

---

## 28. Privacy and Retention

### Subject-data inventory

Video may hold:

- Booking/Interview provider-room references and timing context;
- CourseVideoAsset provider/source references and media metadata;
- CourseVideoPlaybackGrant user/order/IP-hash/user-agent/time evidence;
- CourseVideoPlaybackEvent access/progress metadata;
- ProcessedVideoProviderEvent target/provider/hash/failure metadata;
- provider resources/log references where available.

### Privacy executor

Video implements SH-095/096/097/098 contracts. Privacy owns request verification, target orchestration, completion, and exemption records.

### Typical dispositions

- revoke active playback access before destructive cleanup when required;
- delete provider room/asset/log resource where provider supports it and Privacy instructs it;
- delete/anonymize local user-linked access fields where permitted;
- preserve minimum security/legal evidence only when an authoritative retention fact is supplied and Privacy records the exemption;
- return typed `deleted | absent | anonymized | retained | skipped | retryable_failure | terminal_failure` result.

### Retention

Video does not decide contract/tax/dispute/legal retention. It supplies Video-specific facts and obeys the Privacy-owned exemption result.

### Export

Video contributes sanitized Video-owned user data through the Privacy export protocol. It must not export provider secrets or raw webhook payloads.

---

## 29. Observability

### Structured dimensions

Allowed dimensions should include only safe values such as:

- module `video_session`;
- operation;
- target type + opaque ID;
- provider name;
- canonical Video status;
- normalized error category;
- attempt number;
- duration;
- request/correlation ID;
- reconciliation discrepancy category.

### Prohibited telemetry

Never log:

- join/playback token;
- signed URL;
- provider API secret/signature secret;
- raw webhook body by default;
- PHI/private course content;
- exact personal data not required for diagnosis.

### IntegrationFailure

Use SH-037 rather than creating a local failure table. If current root persistence names differ or are not yet implemented, consume the canonical interface/test double; do not fill the gap with Video-owned operational tables.

### Health

Provider health/readiness checks are operational and do not change Video business status by themselves. Provider degradation may cause a command to return retryable failure and may record Video failure state only when the owner policy says the business effect failed.

---

## 30. Security Boundaries

1. Validate all route/action/job/provider input with approved runtime schemas.
2. Resolve authenticated actor server-side; never trust client user IDs as authority.
3. Authorize protected actions server-side.
4. Keep provider API credentials/signing keys server-only.
5. Verify provider callbacks on raw bytes before parsing.
6. Deduplicate verified callbacks before side effects.
7. Use SH-072/074 rather than local cryptography/randomness.
8. Never persist/log reusable join or playback credentials as durable truth.
9. Bind credentials to actor/target/purpose/expiry where provider permits.
10. Use server time for expiry/join-window checks.
11. Rate-limit credential issuance/provider webhook/public routes according to root platform policy.
12. Minimize provider payloads through SH-078.
13. Raw course source media stays private and Media-owned.
14. A providerRoomId/providerPlaybackId is a reference, not authorization.
15. Unknown provider event/status fails safe.
16. Healthcare-sensitive access must pass Healthcare owner decision before credential issuance.
17. Sensitive access evidence must not leak the secret it proves was issued.
18. Destructive provider deletion requires authorized source instruction and idempotent result handling.
19. Support/admin diagnostics expose sanitized state only.
20. No custom video server is built for MVP.

---

## 31. Error / Decision Result Pattern

Public interfaces return stable Video results rather than raw provider exceptions.

```ts
VideoResult<T> =
  | { ok: true; value: T; correlationId: string }
  | {
      ok: false;
      category: VideoErrorCategory;
      reasonCode: string;
      retryable: boolean;
      correlationId: string;
      evidenceRefs?: string[];
    };
```

### Stable categories

- `validation_denied`
- `unauthenticated`
- `unauthorized`
- `owner_context_invalid`
- `entitlement_denied`
- `compliance_hold_active`
- `healthcare_not_ready`
- `resource_not_ready`
- `outside_access_window`
- `grant_expired`
- `grant_revoked`
- `stale_transition`
- `idempotency_conflict`
- `provider_retryable_failure`
- `provider_terminal_failure`
- `provider_state_conflict`
- `privacy_retained`
- `manual_review_required`
- `internal_failure`

Provider error strings/codes may be attached only in server-side safe diagnostics, not as public reason codes.

---

## 32. Testing Architecture

### Domain unit tests

- live join-window calculation including early/late/overtime boundaries;
- room/asset/grant transition legality;
- provider selection policy;
- provider failure classification;
- playback readiness composition;
- privacy disposition mapping;
- stable result/reason-code mapping.

### Public contract tests

- Video ↔ Booking owner facts;
- Video ↔ JobInterview owner facts;
- Video ↔ Order entitlement;
- Video ↔ Media readiness/source handoff;
- Video ↔ Marketplace/Course target validation;
- Video ↔ Digital Goods policy facts where required;
- Video ↔ Healthcare readiness;
- Video ↔ Track Entitlement where applicable;
- Video ↔ Audit / Notification / Ops;
- Video ↔ Privacy and Moderation executor protocols.

### Database/integration tests

- one room per Booking/interview;
- provider-event `(provider,eventId)` uniqueness;
- status/expiry indexes support worker queries;
- transaction rollback on invalid transition;
- grant issuance/revocation/expiry race behavior;
- cascade behavior reviewed for parent deletion and privacy safety.

### Authorization tests

- buyer/professional/other user Booking join matrix;
- candidate/interviewer/coordinator/observer/nonparticipant interview matrix according to source owner facts;
- creator/admin/support course asset actions;
- support/admin healthcare redaction/denial behavior.

### Compliance tests

- hold blocks mapped action without local blocked flag;
- healthcare denial prevents provider credential;
- normal non-healthcare video does not require healthcare path merely because healthcare exists elsewhere;
- Order denial/refund/dispute effect prevents normal paid playback when owner decision says so.

### Idempotency/concurrency tests

- duplicate room provisioning creates one semantic room/provider resource;
- duplicate ingest creates one semantic provider asset;
- duplicate webhook creates one side effect;
- grant issue/revoke/expiry races are deterministic;
- cancellation vs join credential cannot leak access after cancellation;
- reconciliation vs webhook is safe.

### Provider adapter tests

Use synthetic/recorded fixtures:

- signature pass/fail;
- known/unknown status mapping;
- timeout/rate-limit/5xx vs terminal errors;
- provider not-found deletion;
- missed callback reconciliation;
- no provider DTO leaks into public contract.

### Privacy tests

- inventory returns all Video target types;
- delete vs anonymize vs retained;
- provider already-absent is idempotent success where approved;
- retryable deletion failure returns typed partial failure;
- no Video-created PrivacyRequest/DataErasureJob.

### E2E participation tests

1. ready MediaAsset → CourseVideoAsset processing → ready → eligible Order → short-lived playback → expiry/revocation denial;
2. confirmed video Booking → room → buyer/pro join → outside-window denial;
3. qualifying JobInterview → room → authorized participant join → unrelated user denial;
4. moderation/refund/privacy effect revokes subsequent access;
5. missed/duplicate provider callback does not corrupt Video truth.

---

## 33. Module Invariants

### Rules coding agents must never violate

1. Only Video Session changes `BookingVideoRoom`, `JobInterviewVideoRoom`, `CourseVideoAsset`, and `CourseVideoPlaybackGrant` lifecycle state.
2. Video Session never transitions `Booking`, `JobInterview`, `Order`, `Offering`, `CourseDetails`, `MediaAsset`, `DigitalGoodsTermsAcceptance`, `ComplianceHold`, or healthcare records.
3. Booking and JobInterview never call live-video provider SDKs directly.
4. Marketplace Supply and Digital Goods never call Mux/streaming provider SDKs directly.
5. `BookingVideoRoom` is not Booking truth.
6. `JobInterviewVideoRoom` is not JobInterview truth.
7. `CourseVideoAsset` is not `MediaAsset` and is not CourseDetails truth.
8. `CourseVideoPlaybackGrant` is not Order/purchase truth.
9. Live rooms and course streaming remain separate lifecycle families.
10. Booking and JobInterview room records remain separate for the MVP unless architecture is explicitly changed.
11. A provider ID/URL/token never grants access by itself.
12. Reusable public live-room links are prohibited.
13. Paid/private course video may not expose a permanent public playback URL or raw `.mp4` URL.
14. Signed playback defaults to the schema’s 3600-second TTL unless approved policy overrides it.
15. Server time, not client time or worker state, controls expiration/access windows.
16. Provider callbacks are verified before parsing/side effects and deduplicated before mutation.
17. `ProcessedVideoProviderEvent` remains separate Video dedupe truth.
18. Unknown provider statuses fail safe.
19. Provider-native payloads/types terminate inside adapters.
20. Provider state does not replace Workin Ants Video state during reconciliation.
21. All provider-dependent mutations are idempotent and retry-classified.
22. Raw source media remains Media-owned and private.
23. Video does not build file validation, malware scanning, R2 signing, or object-storage infrastructure.
24. Normal paid course playback uses Order entitlement; null-order access remains unavailable until an alternate basis is approved.
25. Track entitlement may gate approved live-streaming perks but cannot independently grant purchased course playback.
26. Healthcare-sensitive video requires Healthcare-owned readiness/provider decision; Video cannot self-approve it.
27. ComplianceHold is consumed through SH-011; no local generic blocked truth.
28. Moderation/legal validity remains Moderation-owned; Video only executes approved action.
29. Privacy request/job/exemption lifecycle remains Privacy-owned.
30. AccessAuditLog is separate from Video domain access evidence.
31. Operational logs/IntegrationFailure are separate from Video business status.
32. Raw tokens, signed URLs, secrets, PHI, and unnecessary provider payloads are prohibited from telemetry.
33. `CourseAccessibilityAsset` lifecycle remains Digital Goods-owned.
34. `CourseVideoAsset.isDownloadable` may not authorize download delivery.
35. Search/public readiness is not reconstructed inside Video.
36. Notification providers are never called directly by Video.
37. No custom video server is built for MVP.
38. In-memory locks are not correctness mechanisms for distributed provider/grant races.
39. Provider deletion/revocation is authorized, idempotent, and returns typed evidence.
40. An unresolved architecture item may not be silently settled inside a feature branch.

---

## 34. Prohibited Duplicate Implementations

Coding agents must not create:

- `videoAuth.ts`, `getVideoUser.ts`, `requireVideoUser.ts` — use SH-001;
- `videoParticipantGuard.ts` as an independent permission engine — use SH-002 plus owner facts;
- `bookingVideoPermission.ts` that reconstructs Booking authority;
- `interviewVideoPermission.ts` that reconstructs JobInterview/organization authority;
- `videoPremiumCheck.ts`, `canLiveStream.ts`, `subscriptionVideoGate.ts` — use SH-005;
- `videoHoldService.ts`, generic local `blocked`/`onHold` state — use SH-011;
- `videoHipaaCheck.ts`, `dailyBaaReady.ts`, `muxHipaaReady.ts` as healthcare truth — use SH-020;
- `isOrderPaid.ts`, `coursePurchaseService.ts`, Stripe reads — use SH-025;
- `videoAuditLog.ts`, `joinAudit.ts`, local AccessAuditLog table — use SH-029/030;
- `muxQueue.ts`, `dailyQueue.ts`, `videoRetry.ts`, custom dead-letter framework — use SH-047/048;
- local idempotency store — use SH-044;
- in-memory room/grant locks — use SH-051/052 and database constraints;
- `webhookAuthUtil.ts` or route-local provider signature logic — use SH-059;
- generic provider-event business table replacing `ProcessedVideoProviderEvent` — use SH-060 mechanics with separate truth;
- central platform provider-status map for video — use SH-061 inside Video adapters;
- Daily/Agora/Mux clients in Booking, Job Interview, Marketplace, or Digital Goods — use SH-068;
- `hashVideoUrl.ts`, `muxTokenHash.ts`, custom random token functions — use SH-072/074;
- raw-domain-object provider serialization — use SH-078;
- `videoFileValidator.ts`, `muxUploadScanner.ts`, R2/S3 source client — consume Media public interfaces;
- generic `TemporaryGrant`/`AccessGrant` replacing `CourseVideoPlaybackGrant` — use SH-088 mechanics only;
- cross-domain grant revoker that writes Video rows directly — use Video owner command/SH-089;
- `videoPrivacyService.ts` that owns PrivacyRequest/DataErasureJob — implement SH-095–098 executor only;
- DMCA/legal decision logic — consume SH-103 instruction;
- `typesenseVideoSync.ts` — Search remains external;
- `sendVideoEmail.ts`, `videoSms.ts`, direct push client — use SH-041;
- `deliveryLog.ts` replacing CourseVideoPlaybackEvent/live evidence — use SH-125 owner-specific evidence;
- generic `VideoSession` Prisma model replacing Booking/Interview room rows without an approved architecture change.

---

## 35. Unresolved Decisions

### U-VS-01 — Canonical Module name

**Question:** Is the canonical documentation/code name “Video Session Module” or “Video Infrastructure Module”?  
**Evidence conflict:** glossary uses Video Session; Deep Module Registry/Cluster frequently use Video Infrastructure / Video Session.  
**Current handling:** use folder/module ID `video_session`; this document uses Video Session with registry alias.  
**Blocks:** final naming cleanup only, not domain implementation.

### U-VS-02 — Binding MVP live provider

**Question:** Is Daily.co formally approved as the MVP live provider?  
**Evidence:** Prisma defaults and current Project Overview point to Daily.co; older Module evidence also names Agora/AWS Chime.  
**Proposed Ruling:** provider-neutral port + Daily adapter; Agora/Chime deferred.  
**Blocks:** production live adapter commitment, not port/domain/test-adapter work.

### U-VS-03 — Persisted live `roomUrl/*JoinUrl` fields

**Question:** remove them, encrypt/store opaque non-reusable references, or constrain them to provider metadata that cannot authorize?  
**Conflict:** schema contains durable URL fields; architecture prohibits reusable public links and durable credentials.  
**Blocks:** production live credential persistence design.

### U-VS-04 — Live Video domain access proof

**Question:** is AccessAuditLog sufficient, or does Video need a dedicated live token/access grant/event record analogous to CourseVideoPlaybackEvent?  
**Evidence:** `AccessAuditAction.live_video_token_issued` exists, but no Video-owned live access ledger is present.  
**Blocks:** claim of complete Video-specific live access proof; does not block secure ephemeral credential issuance if generic audit is accepted temporarily.

### U-VS-05 — CourseVideoAsset course/Offering foreign-key shape

**Question:** why does `courseDetailsId` reference `CourseDetails.offeringId` while `offeringId` also exists? Which field is canonical?  
**Blocks:** migration/API contract finalization for course-video registration.

### U-VS-06 — `CourseVideoAsset.isDownloadable`

**Question:** is it presentation/config metadata only, or should the field be removed/moved behind Digital Goods policy?  
**Binding boundary:** it cannot grant download entitlement.  
**Blocks:** using the field for product behavior.

### U-VS-07 — `thumbnailUrl` ownership/security

**Question:** is this a public-safe provider thumbnail, a temporary URL, or a Media derivative reference?  
**Blocks:** direct client exposure of the field.

### U-VS-08 — Playback grant `used` semantics

**Question:** one-time credential/grant, first-use marker with continued validity, or terminal state?  
**Blocks:** exact transition/use-count implementation.

### U-VS-09 — Multiple active playback grants

**Question:** may one user/order/asset have multiple concurrent active grants?  
**Evidence:** no uniqueness constraint settles it.  
**Blocks:** final grant issuance concurrency policy/index.

### U-VS-10 — Playback progress event volume/retention

**Question:** record every progress callback, sample milestones, or maintain a separate analytics projection?  
**Blocks:** high-volume player telemetry implementation, not start/completion evidence.

### U-VS-11 — Live-room retry/re-provision transition

**Question:** when a one-to-one room row is `failed`, may it return to `pending`, or is a generation/reset field/model required?  
**Blocks:** retry implementation after terminal provider create failure.

### U-VS-12 — Exact live credential timing policy

**Question:** what early-join allowance and exact token TTL apply before Booking/JobInterview start, beyond the confirmed bound of parent start/end and Booking `overtimeGraceMinutes`?  
**Blocks:** final join-window constants. Use configurable policy/test defaults only after architecture approval.

### U-VS-13 — Alternate non-Order course playback basis

**Question:** which admin/test/complimentary/library access modes justify nullable `orderId`?  
**Binding current rule:** normal purchased playback requires SH-025 Order entitlement.  
**Blocks:** non-purchase playback modes.

### U-VS-14 — Media-to-Mux ingest handoff

**Question:** which Media public contract supplies a bounded source stream/reference without exposing R2 mechanics?  
**Blocks:** production source-ingest transport; test adapter/contract can be built first.

### U-VS-15 — Healthcare-sensitive on-demand provider approval

**Question:** is Mux approved under the required healthcare/vendor/legal posture for healthcare-sensitive course content?  
**Blocks:** healthcare-sensitive on-demand production playback only. Non-healthcare course streaming remains unaffected.

### U-VS-16 — CL-05 Video step-up matrix

**Question:** which sensitive Video admin/provider/access actions require SH-014 fresh assurance?  
**Blocks:** final step-up enforcement for those actions, not ordinary authorization.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. `video_session` is a CL-05 capability Module that owns provider-backed video delivery truth, not parent business lifecycles.
2. `BookingVideoRoom` and `JobInterviewVideoRoom` are Video-owned and remain separate current source records.
3. `CourseVideoAsset`, `CourseVideoPlaybackGrant`, `CourseVideoPlaybackEvent`, and `ProcessedVideoProviderEvent` are Video-owned.
4. Booking & Calendar owns Booking state and Booking orchestration; Video only returns room results/events.
5. Job Interview owns interview schedule/status/participants; Video only owns provider room/access mechanics.
6. Marketplace Supply owns CourseDetails/Offering business structure.
7. Media / File Access owns raw source files, R2/object mechanics, validation, scanning, and file safety.
8. Transaction / Order owns purchase entitlement.
9. Digital Goods owns license/refund/terms/access policy and accessibility tracking outside streaming mechanics.
10. Healthcare owns healthcare readiness/BAA/provider approval.
11. Track Subscription & Entitlement owns live-streaming plan/perk truth.
12. ComplianceHold remains the generic stop sign.
13. Video provider operations use SH-068 behind provider-neutral live/streaming ports.
14. Mux is the current MVP on-demand course-streaming provider target.
15. Provider callbacks are verified, deduplicated in `ProcessedVideoProviderEvent`, translated, and reconciled before Video state changes.
16. Paid/private playback and live access use short-lived credentials; reusable public links are prohibited.
17. Course signed playback defaults to 3600 seconds unless approved policy overrides it.
18. Temporary grant mechanics may be shared, but `CourseVideoPlaybackGrant` remains separate truth.
19. Privacy orchestrates; Video executes against its records/providers.
20. Moderation decides; Video executes disable/revoke/delete effects.
21. Video domain evidence, generic audit, and operational telemetry remain distinct.
22. No direct provider SDK use is allowed in Booking, Job Interview, Marketplace, or Digital Goods.
23. No generic `VideoSession` consolidation is approved for MVP.

### Proposed rulings requiring approval before dependent production work

- Daily.co is the MVP live adapter behind `LiveVideoProviderPort`; Agora/AWS Chime are deferred.
- live URL fields should not persist reusable credentials and must be removed, protected, or semantically constrained before production use.
- owner-facts DTOs should be the default Booking/JobInterview/Course/Media integration path under SH-003/SH-123.

### Decisions explicitly deferred

All items in Section 35 remain unresolved until architecture evidence or an approved ADR settles them.

---

## 37. Coding-Agent Usage

Before implementing or modifying Video Session, read in this order:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md`;
5. CL-05 `architecture.md`;
6. CL-05 `build-plan.md`;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. relevant dependency public-interface sections, especially Booking & Calendar, Job Interview, Transaction / Order, Marketplace Supply, Media / File Access, Digital Goods Access, Track Subscription & Entitlement, Healthcare, Compliance Hold, Privacy, Moderation, Audit/Ops, and Notification;
10. `context/progress-tracker.md`.

Before coding a feature, the agent must answer:

- Which Video-owned record/lifecycle changes?
- Which external owner facts/gates are required?
- Which SH-### operations are consumed?
- Which source-owner public interface replaces a direct Prisma read?
- Which provider port/adapter owns the external call?
- What is the semantic idempotency key?
- What is the database lock/concurrency boundary?
- What Video-specific event/access proof is appended?
- What generic audit/ops proof is additionally required?
- Does the feature touch any unresolved item in Section 35?

If the implementation requires silently deciding an unresolved item, stop that portion of the feature, record the blocker, and update architecture only after a legitimate decision is made.
