# Video Session Implementation Plan

> **Module ID:** `video_session`  
> **Module:** Video Session Module  
> **Registry alias:** Video Infrastructure Module  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Companion architecture:** `module-architecture.md`  
> **Subordinate plan:** CL-05 `build-plan.md`  
> **Implementation posture:** greenfield MVP planning against current Workin Ants architecture and Prisma evidence; unresolved provider/security/data-model decisions remain explicit gates rather than implementation guesses.

---

## Core Principle

Implement Video Session through narrow, verifiable owner slices:

```text
public / observable video behavior
→ validated Video command or query
→ Video-owned access / lifecycle policy
→ authoritative Video write or read
→ canonical shared-operation calls
→ provider work through Video-owned port
→ Video event / access evidence + platform audit / ops effects
→ tests
→ exit gate
```

Video Session is a capability Module. It does not need a standalone product UI to prove progress. Its primary observable outputs are stable public contracts, persisted Video-owned lifecycles, short-lived credentials, provider adapters, provider-event handling, reconciliation workers, privacy execution results, and safe operational read models.

This plan deliberately does **not** mirror all of CL-05. It implements only `video_session` work required by the Cluster sequence, principally:

- **CL-05 Feature 06** — Course Video Ingest and Signed Playback;
- **CL-05 Feature 11** — Live Booking Video Room and Time-Bounded Join Access;
- **CL-05 Feature 12** — JobInterview Video Delivery Bridge;
- **CL-05 Feature 13** — Entitlement Loss, Moderation, Notification, Hold, and related bridge verification where Video participates;
- **CL-05 Feature 14** — Privacy Target Executors, Retention, and Provider Deletion;
- **CL-05 Feature 15** — Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness.

The Module plan may prepare reusable contracts before those Cluster milestones, but it must not pull dependent Cluster work forward or redefine the Cluster sequence.

---

## Build Rules

1. Follow root Workin Ants architecture, code standards, the Canonical Shared Operations Registry, CL-05 architecture, CL-05 build plan, and `module-architecture.md`.
2. Video Session changes only Video-owned truth: `BookingVideoRoom`, `JobInterviewVideoRoom`, `CourseVideoAsset`, `CourseVideoPlaybackGrant`, `CourseVideoPlaybackEvent`, and `ProcessedVideoProviderEvent` plus their owned enums/status semantics.
3. Booking owns Booking. Job Interview owns JobInterview. Order owns purchase entitlement. Marketplace Supply owns Offering/CourseDetails. Media owns `MediaAsset`. Digital Goods owns license/refund/access-policy evidence. Healthcare owns regulated-lane/BAA decisions.
4. Consume external facts through approved Module public interfaces. Do not introduce direct cross-domain Prisma repositories merely because the records share one database.
5. Reuse canonical `SH-###` operations. If a required operation is not implemented, build against its contract/test double or fix it at its canonical owner. Do not create a Video-local substitute.
6. Provider details stay behind `LiveVideoProviderPort` / `StreamingVideoProviderPort` and the canonical `SH-068 invokeVideoProvider` boundary.
7. Provider payloads are inputs, never Workin Ants domain types or source truth.
8. Provider callbacks are signature-verified before parsing/side effects, deduplicated before mutation, translated to Video vocabulary, and reconciled when callbacks are missed.
9. External side effects are idempotent. A retry must not create duplicate rooms, streaming assets, grants, provider resources, events, or revocations.
10. Temporary credentials are short-lived, server-issued, audience/resource-bound, and never stored or logged as reusable secrets. Durable evidence uses hashes and safe metadata only.
11. `CourseVideoPlaybackGrant`, `MediaAccessGrant`, and `DigitalDownloadGrant` remain separate truths even when they reuse the same grant mechanism.
12. `CourseVideoPlaybackEvent` remains Video domain access evidence; `AccessAuditLog` remains Audit / Event Ledger truth; provider-event dedupe remains `ProcessedVideoProviderEvent` truth.
13. Privacy / Data Erasure owns request/job/target orchestration. Video implements only Video-owned inventory, retention facts, anonymization, grant revocation, and provider-resource execution.
14. Content Moderation & Legal Notice owns moderation/legal decisions. Video executes an approved disable/revoke/delete instruction; it does not adjudicate a takedown.
15. ComplianceHold remains the reusable stop sign. Do not add local `videoBlocked`, `canJoin`, `isSuspendedForVideo`, or similar policy truth.
16. Track Subscription & Entitlement remains plan/feature truth. Do not add `canLiveStream`, `isPremiumVideo`, or provider-plan booleans as current policy truth.
17. Business denials are not retried as technical failures. Provider timeouts, rate limits, and recoverable transport failures may be retried under owner policy.
18. Every numbered feature ends with automated tests, contract/workflow verification, documentation/progress update, and an explicit exit gate.
19. Do not start a later Module feature when the relevant earlier exit gate failed, unless the work is an independent test/contract prerequisite explicitly recorded in progress.
20. An unresolved architecture question is a blocker only for the behavior that depends on it. Implement the safe surrounding contract, record the block, and do not guess.

---

## Preconditions

### Hard platform foundations

The Module requires these root/platform capabilities before production behavior can be considered complete:

- PostgreSQL/Prisma migrations and transactions;
- runtime validation for all public/provider inputs;
- server-authenticated actor context;
- Role / Authority decision interface;
- request/correlation context;
- canonical idempotency storage/runner;
- transactional outbox/domain-event publication;
- durable queue with retry/backoff/dead-letter behavior;
- Postgres-backed locking/optimistic concurrency primitives;
- shared cryptographic token/hash utilities;
- provider secret management and rotation path;
- Audit / Event Ledger interfaces;
- Observability / Ops interfaces for structured logs, failures, metrics, health, and queue telemetry.

If an implementation is not yet present, Video may depend on a contract fake in tests. It must not become the temporary owner of those capabilities.

### Hard Module interfaces by workflow

**Course streaming requires:**

- Media / File Access owner facts proving the source `MediaAsset` is safe and `ready`;
- Marketplace Supply target facts for `CourseDetails` / Offering relationship;
- Transaction / Order `SH-025 authorizeOrderEntitlement` for normal paid playback;
- Digital Goods contextual policy/acceptance decision where that policy applies;
- Healthcare `SH-020 evaluateHealthcareReadiness` for healthcare-sensitive content;
- Audit and Ops interfaces.

**Booking live video requires:**

- Booking & Calendar owner-facts/public contract returning current Booking status, video location type, start/end, participant relationships, overtime grace, and cancellation/reschedule facts;
- applicable Track entitlement decision when the product definition gates live streaming;
- applicable Healthcare decision;
- Booking orchestration public command/acknowledgment behavior from CL-05 Feature 10.

**Interview live video requires:**

- CL-06 Job Interview owner-facts contract for status, time window, candidate/interviewer participants, and organization context;
- Role / Authority organization/participant interpretation;
- same live-provider infrastructure proven for Booking rooms.

**Privacy/moderation hardening requires:**

- Privacy target protocol (`SH-095`–`SH-098` as applicable);
- Moderation execution instruction (`SH-103`);
- canonical provider deletion interface (`SH-070`).

### Provider setup

- **Mux** is the current on-demand course-video target and may be implemented after a test adapter proves the port.
- **Live video** must remain provider-neutral. CL-05 currently proposes **Daily.co** as the MVP adapter because the Project Overview and schema default point there. Production commitment remains blocked until that proposed ruling is approved or replaced.
- Agora and AWS Chime are not additional MVP adapters merely because they appear in historical evidence/enums.

### Schema decisions that may be staged but not silently settled

The following do not prevent contract/unit work, but block dependent production migration/API decisions:

- persisted live-room `roomUrl` / participant join URL fields versus the rule that reusable join links must not become durable truth;
- `CourseVideoAsset.courseDetailsId` relationship shape versus the separate optional `offeringId`;
- whether `CourseVideoPlaybackGrant.status=used` means one-time consumption or first use while still valid;
- whether multiple active grants for the same user/asset/order are permitted;
- whether live token issuance needs a dedicated Video-owned proof record beyond AccessAuditLog/domain-access evidence;
- the exact Video step-up matrix;
- alternate no-Order course access basis.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Video Contracts, Repositories, Lifecycle Policies, and Provider Ports

### Objective

Establish the Module boundary and executable contracts for all Video-owned records without committing unresolved provider or cross-Module policy decisions.

### Observable Result

Tests can create/read Video-owned records through Module repositories and exercise canonical state transitions using typed commands/queries and fake provider ports. No neighboring Module table needs to be read directly, and no external provider client is required yet.

### Cluster Build-Plan Link

Prepares the Video-owned foundation required by CL-05 Features **06**, **11**, and **12**. It must not make those Cluster features appear complete by itself.

### Dependencies

- current Prisma schema and migration baseline;
- root module/folder convention and runtime validation;
- SH-044, SH-051/052/053 contract availability or test doubles;
- owner-facts contract pattern (`SH-003` proposed, `SH-123` confirmed where applicable);
- `module-architecture.md` unresolved-decision register.

### In Scope

- create/confirm `video-session` application/domain/infrastructure/public/test boundaries;
- repository interfaces for all six Video-owned models;
- transition policies for room, asset, grant, and provider-event statuses;
- DTO/result schemas for public commands and queries;
- provider-neutral `LiveVideoProviderPort` and `StreamingVideoProviderPort`;
- discriminated live-room context types for Booking vs JobInterview without merging their source records;
- safe error/decision result vocabulary;
- database indexes/constraints verification report and migration proposal only where evidence is binding;
- test fakes for upstream owner facts and providers.

### Out of Scope

- Mux, Daily, Agora, or Chime production adapters;
- provider webhooks;
- real playback or join credentials;
- Booking or JobInterview lifecycle logic;
- Order entitlement logic;
- schema consolidation into a generic `VideoSession`;
- resolution of URL-storage or CourseVideoAsset FK conflicts without an approved architecture decision.

### Module-Owned Data

- `BookingVideoRoom` and room provider/status enums;
- `JobInterviewVideoRoom` and room provider/status enums;
- `CourseVideoAsset` and provider/status/playback-policy enums;
- `CourseVideoPlaybackGrant` and status enum;
- `CourseVideoPlaybackEvent` and event enum;
- `ProcessedVideoProviderEvent` and provider/status enums.

### Public Interfaces

Define versioned TypeScript contracts for:

- `registerCourseVideoSource`;
- `requestCourseVideoIngest`;
- `getCourseVideoProcessingStatus`;
- `issueCoursePlaybackGrant`;
- `issueCoursePlaybackCredential`;
- `getCoursePlaybackGrantStatus`;
- `provisionBookingVideoRoom`;
- `provisionInterviewVideoRoom`;
- `getBookingVideoRoomStatus`;
- `getInterviewVideoRoomStatus`;
- `issueVideoJoinCredential`;
- `cancelBookingVideoRoom`;
- `cancelInterviewVideoRoom`;
- `applyVideoProviderEvent`;
- `reconcileCourseVideoProviderState`;
- `reconcileLiveVideoProviderState`;
- privacy executor contracts.

The interfaces may initially use fakes. They are not permission to implement neighboring owner queries locally.

### Shared Operations Used

- **SH-044 `executeIdempotentCommand` — platform application infrastructure.** Invocation: command shell for registrations/provisioning. Local policy: semantic idempotency keys. Prohibited duplicate: `videoIdempotencyService.ts` or Video idempotency table.
- **SH-051 `acquireAggregateLock` — shared persistence.** Invocation: high-contention room/grant/asset transitions where needed. Local policy: target lock key and conflict semantics. Prohibited duplicate: in-memory `videoMutex`.
- **SH-052 `withOptimisticConcurrency` — shared persistence.** Invocation: stale mutable transition/update protection. Local policy: retry versus conflict. Prohibited duplicate: ad hoc `updatedAt` last-write-wins logic.
- **SH-053 `transitionLifecycleState` — shared mechanism/separate truth.** Invocation: every owner status mutation. Local policy: Video transition graphs. Prohibited duplicate: generic Video-specific state-machine framework that tries to own all domain statuses.
- **SH-068 `invokeVideoProvider` — Video Session.** Invocation: provider ports only. Local policy: live/on-demand resource mapping. Prohibited duplicate: provider clients in public/application services.
- **SH-123 `validateOwnedTargetReference` — target owner.** Invocation: future external target validation contract. Local policy: which Video command requires which target facts. Prohibited duplicate: direct Marketplace/Booking/Interview Prisma lookups.

### Domain Logic

- current room models remain separate;
- one current schema Booking may own at most one `BookingVideoRoom` because `bookingId` is unique;
- one current schema JobInterview may own at most one `JobInterviewVideoRoom` because `interviewId` is unique;
- provider-native statuses never enter domain services un-translated;
- local lifecycle transitions are explicit and deny stale/invalid transitions;
- Video result DTOs never imply parent lifecycle status;
- public queries return sanitized Video facts, not provider secrets.

### Authorization / Compliance

No user-facing sensitive action is enabled in this feature. Public contracts must nevertheless require actor/system context where the final operation will require it. Admin/system command types must distinguish trusted system execution from browser-supplied actor claims.

### Database / Transaction Behavior

- verify existing unique constraints on Booking/Interview room parent IDs and provider-event `(provider, providerEventId)`;
- verify status/provider/expiry indexes used by later workers;
- introduce no cross-owner foreign-key behavior that transfers lifecycle ownership;
- document, but do not silently fix, the `CourseVideoAsset.courseDetailsId`/`offeringId` ambiguity;
- document, but do not authorize production use of, persisted join URL fields until the security ruling is settled.

### Events / Jobs

Define event envelopes and payload schemas for the Module events already named in `module-architecture.md`, but do not publish them until a source transition exists. Define worker payload schemas for ingest, room provisioning, expiration, and reconciliation without running provider work.

### Provider Integration

Fake/test ports only. Provider DTOs must terminate in infrastructure adapters. The domain layer uses canonical Video types.

### UI / Admin Surface

No product UI. Optional development-only contract harness may render sanitized records/results for testing. It must not become a support/admin product requirement.

### Failure Behavior

- invalid contract: validation error;
- stale transition: `conflict/stale_state`;
- missing upstream interface: dependency unavailable in tests rather than a direct DB fallback;
- unresolved provider decision: configuration/feature disabled, not guessed;
- unsafe migration conflict: fail review, preserve current schema until ruling.

### Tests

- domain transition matrix tests for all Video statuses;
- repository integration tests;
- unique constraint tests;
- public schema/contract tests;
- fake-provider contract tests;
- import-boundary test proving Video does not import Booking/Order/JobInterview repositories or provider SDKs outside infrastructure;
- error/result normalization tests.

### Documentation Updates

- update `module-architecture.md` only if implementation reveals a real binding discrepancy;
- record schema conflicts and provider decision state in progress tracker;
- no Shared Operations Registry changes unless a genuinely missing canonical operation is discovered.

### Acceptance Criteria

- all six Video-owned record families have explicit repository and transition ownership;
- public contracts compile independently of provider SDKs;
- Booking and JobInterview room records remain separate;
- no cross-domain repository is introduced;
- no new generic `VideoSession` table is introduced;
- unresolved schema/provider questions are visible and not encoded as hidden assumptions.

### Exit Gate

Typecheck/lint/unit/integration contract suite passes; every Video-owned lifecycle has a tested transition policy; provider fakes satisfy the Video ports; boundary tests prove no neighboring source-of-truth repository is imported; unresolved decisions are recorded with the exact dependent features they block.

---

# Phase 2 — On-Demand Course Streaming

## 02 Course Video Registration and Provider-Ingest Intent

### Objective

Allow an authorized course creator/admin/system workflow to register a safe source `MediaAsset` as a Video-owned `CourseVideoAsset` and durably request provider ingest without yet depending on a successful Mux callback.

### Observable Result

A ready permitted source MediaAsset can produce exactly one semantic CourseVideoAsset registration for the requested course slot/version and an idempotent ingest job. Unsafe, missing, unauthorized, or held inputs cannot create an ingestable Video asset.

### Cluster Build-Plan Link

Implements the first half of CL-05 Feature **06 — Course Video Ingest and Signed Playback**.

### Dependencies

- Module Feature 01;
- CL-05 Media Feature 01 ready-media contract;
- Marketplace Supply CourseDetails/Offering owner-target facts;
- SH-001/002 auth and authority;
- SH-011 hold check where registration/processing is hold-sensitive;
- shared queue/outbox/idempotency.

### In Scope

- `registerCourseVideoSource` command;
- target validation for CourseDetails/Offering relationship through owner interface;
- Media readiness/context validation through Media public interface;
- create CourseVideoAsset in a safe pre-ingest state;
- enqueue `requestCourseVideoIngest` job through shared queue;
- sanitized creator/admin processing-status query;
- source-registration event/outbox if downstream consumers need the fact.

### Out of Scope

- raw file validation/scanning;
- direct R2 access from Video;
- Mux upload/provider adapter implementation;
- playback grants;
- Digital Goods policy ownership;
- course publication decision;
- accessibility asset lifecycle.

### Module-Owned Data

- `CourseVideoAsset` only, plus owner event/outbox reference if platform infrastructure persists it separately.

### Public Interfaces

- implement `registerCourseVideoSource`;
- implement `getCourseVideoProcessingStatus` for registered/pre-provider states;
- internal `requestCourseVideoIngest` job command.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity & Access.** Invocation: public creator/admin registration. Local policy: course-video action. Prohibited duplicate: `videoAuth.ts`.
- **SH-002 `authorizeResourceAction` — Role / Authority.** Invocation: before registration. Local policy: Video supplies action plus course relationship facts from owner. Prohibited duplicate: `courseVideoPermission.ts`.
- **SH-003 `queryOwnerFacts` — source Module, proposed contract.** Invocation: minimal CourseDetails/Offering facts. Local policy: Video requires target identity/version only. Prohibited duplicate: Marketplace Prisma reads from Video.
- **SH-011 `evaluateComplianceHold` — Admin Review / Compliance Hold.** Invocation: before a hold-sensitive ingest. Local policy: map applicable hold to Video denial. Prohibited duplicate: `videoBlocked` flags.
- **SH-044 `executeIdempotentCommand` — platform.** Invocation: registration. Local policy: semantic key such as course + source asset + logical slot/version. Prohibited duplicate: local idempotency store.
- **SH-046 `publishDomainEvent` — outbox.** Invocation: after committed registration when an event is needed. Local policy: `video.course_asset.registered.v1` payload. Prohibited duplicate: direct event-bus publish before commit.
- **SH-047 `enqueueReliableJob` — queue.** Invocation: ingest request after registration. Local policy: job payload and completion meaning. Prohibited duplicate: `videoIngestQueue.ts` framework.
- **SH-078 `minimizeAndRedactProviderInput` — shared serializer/source policy.** Invocation: prepare future provider request DTO. Local policy: only source/provider fields necessary for ingest. Prohibited duplicate: raw domain object forwarding.
- **SH-123 `validateOwnedTargetReference` — Marketplace/Media owners.** Invocation: course and Media references. Local policy: Video’s accepted target kinds. Prohibited duplicate: local target registry.

### Domain Logic

1. Resolve actor and authorize registration.
2. Validate Course target through Marketplace Supply.
3. Validate source MediaAsset through Media: `ready`, permitted context, not frozen/erased/deleted.
4. Reject attempts to make `MediaAsset` or a storage URL the Video provider truth.
5. Create CourseVideoAsset with canonical Video status and provider intent.
6. Persist no provider secret or reusable source URL.
7. Enqueue ingest only after the Video record commits.
8. Same semantic registration must replay the existing result rather than create duplicate logical assets.

### Authorization / Compliance

- creator/admin authority required;
- healthcare-sensitive course registration may need Healthcare readiness before provider ingest; if readiness is not yet required at registration, the record may remain non-ready/non-active until the provider gate is passed according to approved policy;
- hold applies only through SH-011, not a local blocked field.

### Database / Transaction Behavior

- registration transaction creates the Video asset and transactional outbox/job intent as supported by platform infrastructure;
- define/verify semantic idempotency uniqueness outside ad hoc application memory;
- do not alter CourseDetails or MediaAsset rows;
- if the CourseVideoAsset FK ambiguity prevents a safe insert shape, stop this feature at the contract/migration gate and resolve U-VS schema ruling first.

### Events / Jobs

- `video.course_asset.registered.v1` where downstream readiness surfaces need it;
- enqueue provider ingest job keyed by CourseVideoAsset ID + ingest generation/version;
- retries handled in Feature 03 provider execution.

### Provider Integration

No real provider call yet. The ingest job targets `StreamingVideoProviderPort` so Feature 03 can attach Mux without changing application/domain contracts.

### UI / Admin Surface

No Video-owned product UI. Marketplace/creator surface may consume `getCourseVideoProcessingStatus`. A development status inspector is optional.

### Failure Behavior

- unauthorized/invalid target/source not ready: permanent denial;
- hold/healthcare gate denial: domain denial, not retry;
- duplicate semantic request: replay existing registration;
- queue enqueue failure after committed transaction: outbox/shared queue retry must recover; do not create a second asset;
- unresolved FK relationship: implementation blocked, architecture update required.

### Tests

- Media owner allow/deny contract;
- Marketplace target contract;
- authorization matrix;
- idempotent registration;
- transaction/outbox failure recovery;
- no direct Media/Marketplace write test;
- source URL/secret telemetry redaction test.

### Documentation Updates

Record the final CourseVideoAsset target relationship if the schema ambiguity is resolved. Update architecture before committing a changed FK interpretation.

### Acceptance Criteria

- only an authorized actor with a ready permitted source MediaAsset can register a Video asset;
- duplicate registration cannot create duplicate semantic assets;
- provider work is durable and decoupled from the request transaction;
- Media/Marketplace source records are untouched;
- no raw object URL is persisted as Video business truth.

### Exit Gate

Registration and fake-ingest-intent tests pass; transaction/outbox replay is proven; cross-owner contract tests pass; the CourseVideoAsset relation used by implementation is either already unambiguous or explicitly resolved in architecture/migration evidence.

---

## 03 Mux Adapter, Provider Webhooks, and CourseVideoAsset Lifecycle

### Objective

Implement the Mux on-demand adapter so a registered CourseVideoAsset can move through upload/processing to `ready` or `failed` using verified, deduplicated, translated provider evidence.

### Observable Result

A test/production-configured Mux ingest produces a provider asset once; duplicate callbacks do not duplicate effects; a missed callback can be discovered by reconciliation; consumers observe only canonical CourseVideoAsset status and safe failure information.

### Cluster Build-Plan Link

Completes the provider-processing half of CL-05 Feature **06**.

### Dependencies

- Module Feature 02;
- Mux credentials/configuration for non-fake environments;
- shared webhook raw-body infrastructure;
- SH-059/060/061/062/068;
- Ops failure/telemetry interfaces.

### In Scope

- Mux implementation of `StreamingVideoProviderPort`;
- idempotent provider ingest/create behavior;
- provider IDs/reference persistence allowed by schema;
- webhook route/handler boundary;
- signature verification before parsing/side effects;
- `ProcessedVideoProviderEvent` claim/dedupe;
- explicit Mux-to-Video status/error mapping;
- CourseVideoAsset transition to uploading/processing/ready/failed;
- processing/reconciliation worker;
- safe provider failure reporting.

### Out of Scope

- playback authorization/credential issuance;
- live room providers;
- raw Media storage ownership;
- Digital Goods licensing;
- healthcare legal approval itself;
- Cloudflare Stream/Vimeo adapters unless separately approved.

### Module-Owned Data

- `CourseVideoAsset` provider references/status/timestamps/failure category;
- `ProcessedVideoProviderEvent`;
- `CourseVideoPlaybackEvent` only for provider asset-ready/failed/webhook-received evidence if the approved event semantics require it.

### Public Interfaces

- implement `requestCourseVideoIngest` worker behavior;
- implement `applyVideoProviderEvent` for streaming target types;
- implement `reconcileCourseVideoProviderState`;
- extend `getCourseVideoProcessingStatus` with canonical ready/failure facts.

### Shared Operations Used

- **SH-044 `executeIdempotentCommand` — platform.** Provider create/ingest request identity. Local policy: asset/provider/generation key. Prohibited duplicate: `muxIdempotency.ts` store.
- **SH-047 `enqueueReliableJob` — queue.** Ingest/reconciliation work. Local policy: Video payload. Prohibited duplicate: custom worker infrastructure.
- **SH-048 `executeRetryWithBackoff` — queue/platform.** Retry transport/rate-limit/provider-unavailable failures. Local policy: Mux retry classification. Prohibited duplicate: route-level retry loops.
- **SH-059 `verifyProviderWebhookSignature` — shared security shell.** Verify raw Mux callback. Local policy: Mux algorithm/secret/tolerance. Prohibited duplicate: route-local signature helper.
- **SH-060 `deduplicateProviderEvent` — Video-owned ledger over shared primitive.** Claim `(provider,eventId)` into `ProcessedVideoProviderEvent`. Local policy: target mapping. Prohibited duplicate: `muxWebhookLog` or generic shared provider-event table.
- **SH-061 `translateProviderStatus` — Video adapter.** Map Mux statuses/errors. Local policy: CourseVideoAsset transition. Prohibited duplicate: global provider-status mapper.
- **SH-062 `reconcileProviderState` — Video owner.** Compare Workin Ants Video state with Mux. Local policy: safe auto-repair set. Prohibited duplicate: provider state as truth.
- **SH-068 `invokeVideoProvider` — Video.** Only Mux adapter calls SDK/API. Local policy: source asset mapping. Prohibited duplicate: Mux SDK in Marketplace/Digital Goods/application services.
- **SH-072 `hashCanonicalPayload` — shared security.** Hash webhook payload/evidence where recorded. Local policy: what the hash proves. Prohibited duplicate: `muxHash.ts`.
- **SH-078 `minimizeAndRedactProviderInput` — shared.** Minimize provider DTO and logs. Local policy: allowed fields. Prohibited duplicate: raw Prisma object forwarding.
- **SH-032/034/037 — Observability/Ops.** Correlation, telemetry sanitation, integration-failure record. Local policy: target/operation/failure category. Prohibited duplicate: local Mux error ledger.

### Domain Logic

- an ingest request starts only from a Video-approved state;
- provider creation response is translated before Video state update;
- webhook `ready` can move only an eligible matching asset to `ready`;
- webhook `failed` records canonical failure and does not alter CourseDetails/Offering;
- unknown statuses fail safe and surface Ops evidence rather than invent a transition;
- provider event target/type must be validated against the existing Video asset/provider reference;
- duplicate webhook is no-op/replayed result after dedupe claim;
- reconciliation may repair only discrepancies explicitly declared safe; others become manual/ops discrepancies.

### Authorization / Compliance

Webhook path is provider-authenticated, not end-user authenticated. Manual reconciliation/retry requires system/admin authority and step-up only if root policy later requires it. Healthcare-sensitive course provider activation must fail closed if Healthcare says the provider path is not ready.

### Database / Transaction Behavior

- unique `(provider, providerEventId)` is the dedupe boundary;
- provider event claim and Video mutation must be in the approved transactional pattern so crash/retry cannot double-apply;
- asset transitions use optimistic/aggregate concurrency where competing webhook/reconciliation/admin actions are possible;
- do not persist raw webhook payload if a hash/normalized fields suffice.

### Events / Jobs

- emit `video.course_asset.ready.v1` or `video.course_asset.failed.v1` only after committed Video state change;
- reconciliation scheduled/manual job keyed by provider + cursor/window;
- dead-letter retains Video source status, records IntegrationFailure, and permits safe replay.

### Provider Integration

Mux only for MVP on-demand path. SDK types remain inside adapter. Credentials are server-only and accessed through approved secret management.

### UI / Admin Surface

Marketplace/creator consumer may show status/failure category. Optional support-safe reconciliation view can show provider name/reference suffix, canonical status, timestamps, and correlation ID—not secrets or raw payload.

### Failure Behavior

- invalid signature: reject before side effect;
- duplicate callback: ignored/replayed;
- unknown event/status: `failed/review` operational result without unsafe domain mutation;
- provider timeout: retry idempotently;
- provider says asset missing: reconciliation discrepancy; auto-repair only if approved;
- terminal provider processing failure: Video asset `failed`, external parent lifecycles unchanged.

### Tests

- Mux adapter contract fixtures;
- raw-signature verification;
- duplicate webhook/replay;
- status mapping matrix including unknown value;
- crash-after-dedupe/transaction recovery test;
- reconciliation dry-run and safe repair;
- provider timeout/rate-limit retry;
- redaction/log scrape tests;
- integration test registration → processing → ready/failure.

### Documentation Updates

Record Mux API/version assumptions in library/provider docs as appropriate. Architecture changes only if provider or status semantics become binding differently from current context.

### Acceptance Criteria

- one Video asset produces no duplicate provider resource under retry;
- unsigned/invalid callbacks cannot mutate Video truth;
- duplicate callbacks cause one semantic effect;
- provider states are explicitly translated;
- missed callbacks are discoverable through reconciliation;
- parent Course/Offering records remain untouched.

### Exit Gate

Mux/test adapter, webhook, dedupe, transition, reconciliation, failure, and redaction suites pass; CourseVideoAsset reaches ready/failed through Video-only state transitions; no raw provider payload or secret becomes domain truth.

---

## 04 Order-Gated Playback Grant and Short-Lived Playback Credential

### Objective

Issue paid course playback only after current authoritative entitlement and Video readiness gates pass, using a Video-owned temporary grant and a short-lived provider credential.

### Observable Result

An entitled buyer can obtain a Video playback grant and short-lived signed playback credential for a ready course asset. A non-entitled, refunded, held, healthcare-blocked, expired, revoked, or disabled path receives a stable denial and no credential.

### Cluster Build-Plan Link

Implements the access half of CL-05 Feature **06**.

### Dependencies

- Module Feature 03;
- Transaction / Order SH-025 contract;
- Digital Goods contextual policy/acceptance interface where required;
- Healthcare SH-020 where sensitive;
- Audit SH-030 and Video domain-access evidence SH-125;
- secure token/hash/grant mechanism.

### In Scope

- `evaluateCoursePlaybackReadiness` composition;
- `issueCoursePlaybackGrant`;
- `issueCoursePlaybackCredential`;
- grant status query;
- default 3600-second signed playback TTL unless approved policy overrides it;
- durable hash/evidence instead of raw reusable credential;
- stable denial reason codes;
- current entitlement revalidation at the correct invocation point.

### Out of Scope

- complimentary/admin/test access except explicitly isolated test fixtures;
- subscription entitlement automatically replacing Order purchase entitlement;
- raw video download;
- Digital Goods license/refund policy implementation;
- changing Order state;
- deciding healthcare eligibility.

### Module-Owned Data

- `CourseVideoPlaybackGrant`;
- `CourseVideoPlaybackEvent` for grant/credential issuance or denial according to approved event design;
- CourseVideoAsset read-only within Video.

### Public Interfaces

- implement `issueCoursePlaybackGrant`;
- implement `issueCoursePlaybackCredential`;
- implement `getCoursePlaybackGrantStatus`;
- internal `evaluateCoursePlaybackReadiness` decision result.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity & Access.** Playback caller. Local policy: Video action. Prohibited duplicate: player current-user helper.
- **SH-002 `authorizeResourceAction` — Role / Authority.** General protected action. Local policy: resource/action facts. Prohibited duplicate: `playbackPermission.ts` generic auth engine.
- **SH-011 `evaluateComplianceHold` — Hold owner.** Current applicable holds. Local policy: which Video actions are blocked. Prohibited duplicate: local blocked fields.
- **SH-020 `evaluateHealthcareReadiness` — Healthcare.** Healthcare-sensitive provider/data-boundary readiness. Local policy: Video denies credential if not permitted. Prohibited duplicate: `videoHipaaCheck.ts`.
- **SH-025 `authorizeOrderEntitlement` — Transaction / Order.** Normal paid playback basis. Local policy: exact CourseVideoAsset/Offering mapping and grant duration. Prohibited duplicate: Order/Stripe status reads from Video.
- **SH-026 `authorizeContextualResourceAccess` — relevant context owner.** Additional contextual access where architecture requires it. Local policy: combine external decision with Video readiness. Prohibited duplicate: universal Video business-entitlement service.
- **SH-044 `executeIdempotentCommand` — platform.** Grant issuance. Local policy: semantic grant request identity. Prohibited duplicate: Video idempotency store.
- **SH-074 `generateSecureToken` — shared security.** Local secret material where provider credential requires it. Local policy: resource/audience/TTL claims. Prohibited duplicate: `videoTokenHelper.ts` randomness.
- **SH-072 `hashCanonicalPayload` — shared crypto.** Token/URL evidence hash. Local policy: normalization and retained proof. Prohibited duplicate: local hashing helper.
- **SH-088 `manageTemporaryAccessGrant` — shared mechanism/separate truth.** Grant lifecycle mechanics. Local policy: CourseVideoPlaybackGrant semantics. Prohibited duplicate: generic AccessGrant table.
- **SH-125 `recordDomainAccessEvent` — Video owner.** Append playback issuance/denial evidence. Local policy: Video event type/metadata. Prohibited duplicate: using AccessAuditLog as the only Video event history.
- **SH-030 `recordSensitiveAccess` — Audit.** Required sensitive/healthcare credential issue/denial. Local policy: sensitivity/action classification. Prohibited duplicate: `videoAuditLog.ts`.

### Domain Logic

1. Resolve actor.
2. Load Video asset through Video repository; require `ready` and allowed playback policy.
3. Obtain Order entitlement from Order owner for normal paid path.
4. Obtain applicable Digital Goods contextual facts without interpreting its tables locally.
5. Evaluate hold and Healthcare gates.
6. Create/replay bounded `CourseVideoPlaybackGrant` according to the still-approved grant cardinality/idempotency policy.
7. When credential is requested, recheck current server time, grant status, asset status, and any owner facts that policy requires to be current.
8. Ask StreamingVideoProviderPort for signed credential.
9. Persist only hashes/safe proof metadata, never reusable URL/JWT.
10. Append Video access evidence and required AccessAuditLog separately.

### Authorization / Compliance

- Order entitlement is mandatory for normal paid playback;
- a track live-streaming entitlement does not imply paid course access;
- Healthcare-sensitive playback fails closed on provider/BAA/data-boundary denial;
- exact step-up requirements remain unresolved; do not add local MFA logic;
- denied users receive no provider asset IDs beyond safe public identifiers needed by the client.

### Database / Transaction Behavior

- grant issuance is transaction/idempotency protected;
- if multiple active grants are not yet ruled, implementation must avoid a uniqueness migration that silently decides the question; use semantic idempotency for the request while recording U-VS decision;
- credential issue may update first-use/hash/event in one owner transaction after provider credential generation, with compensation/retry semantics ensuring secrets are not persisted on partial failure;
- server time is authoritative even if expiration worker is delayed.

### Events / Jobs

- `video.course_playback.granted.v1` after grant commit;
- `video.course_playback.denied.v1` only if denial events are approved as durable domain facts, otherwise CourseVideoPlaybackEvent records local denial and generic events stay minimal;
- grant-expiration worker is implemented in Feature 05.

### Provider Integration

Mux signed playback/JWT through StreamingVideoProviderPort. Provider-specific claims and signing types stay inside adapter; application layer receives a safe `credential + expiresAt` response.

### UI / Admin Surface

Buyer player UI remains Marketplace/Digital Goods owned. Video supplies readiness/grant/credential results and safe reason codes such as `not_entitled`, `asset_not_ready`, `grant_expired`, `grant_revoked`, `healthcare_blocked`, `provider_unavailable`.

### Failure Behavior

- entitlement deny: no grant/credential;
- asset not ready/disabled: no grant/credential;
- provider signing temporary failure: retryable delivery failure without falsifying entitlement;
- credential generated but response lost: next request follows idempotency policy and may issue a new short-lived credential without duplicating purchase truth;
- stale/refunded Order on revalidation: deny and route revocation in Feature 05/09.

### Tests

- Order allow/deny/refund contract;
- hold/healthcare gate matrix;
- 60-minute default TTL and configured override boundary;
- token/URL non-persistence/log-scrape tests;
- grant idempotency tests;
- server-time expiry tests;
- sensitive AccessAuditLog + Video event separation;
- E2E fake/Mux: ready asset → entitled user → credential; non-entitled/refunded → deny.

### Documentation Updates

If grant `used` semantics, active-grant cardinality, or alternate access basis becomes binding during implementation, update `module-architecture.md` before changing schema/API behavior.

### Acceptance Criteria

- normal paid playback cannot be granted without SH-025 allow;
- a ready provider asset alone is never sufficient entitlement;
- credentials are short-lived and no reusable secret is durable/logged;
- Video grant/event and AccessAuditLog remain separate evidence;
- healthcare/hold denials fail closed;
- provider failure does not alter Order truth.

### Exit Gate

Contract, entitlement, grant, token-security, audit, and E2E tests pass; entitled users receive only bounded credentials; every denial path proves no credential is returned or persisted.

---

## 05 Playback Evidence, Expiration, Revocation, and Course-Provider Reconciliation

### Objective

Complete the CourseVideoPlaybackGrant lifecycle and make access recoverable/revocable under expiry, refund, moderation, privacy, and provider inconsistency without transferring source ownership.

### Observable Result

Playback starts/completions/errors are Video-evidenced; expired/revoked grants cannot produce credentials; authoritative external revocation instructions remove future access; reconciliation finds provider discrepancies; repeated revocation/expiration is idempotent.

### Cluster Build-Plan Link

Finishes CL-05 Feature **06** and prepares Video participation in CL-05 Features **13–15**.

### Dependencies

- Module Feature 04;
- Order refund/entitlement-change event or query contract;
- Moderation/Privacy instruction contracts may initially be fakes until Features 09/10;
- SH-055, SH-089, SH-062, SH-125, SH-030.

### In Scope

- playback-start/progress/completion/error recording policy;
- `revokeCoursePlaybackGrant`;
- expiration worker;
- provider/playback reconciliation hooks;
- revocation idempotency;
- safe evidence retention;
- consumer event publication after actual Video state changes.

### Out of Scope

- defining refund/dispute policy;
- moderation adjudication;
- Privacy orchestration;
- course-completion/certification business logic;
- analytics warehouse design;
- deciding high-volume progress-event long-term storage strategy beyond the approved minimum.

### Module-Owned Data

- `CourseVideoPlaybackGrant` transition fields;
- `CourseVideoPlaybackEvent`;
- `ProcessedVideoProviderEvent` where callbacks contribute evidence.

### Public Interfaces

- `revokeCoursePlaybackGrant`;
- access-event recording endpoint/handler only if trusted player/provider telemetry is part of current implementation;
- `reconcileCourseVideoProviderState` extended for playback/provider resource discrepancy;
- grant-status query.

### Shared Operations Used

- **SH-055 `runDeadlineExpiration` — shared scheduler.** Invocation: expired active grants. Local policy: exact Video expiration semantics. Prohibited duplicate: Video cron framework.
- **SH-089 `revokeTemporaryAccessGrant` — each grant owner.** Invocation: authoritative refund/moderation/privacy/security instruction. Local policy: Video reason/reference/event. Prohibited duplicate: direct status writes from consumers.
- **SH-044 `executeIdempotentCommand` — platform.** Revocation/access-event identity. Local policy: source instruction/event key. Prohibited duplicate: local replay map.
- **SH-053 `transitionLifecycleState` — shared mechanism.** Grant transition. Local policy: allowed transitions. Prohibited duplicate: route-local status assignment.
- **SH-062 `reconcileProviderState` — Video.** Provider discrepancy. Local policy: safe repair. Prohibited duplicate: treating Mux as source truth.
- **SH-125 `recordDomainAccessEvent` — Video.** Playback events. Local policy: event sampling/required milestones. Prohibited duplicate: generic audit as Video history.
- **SH-030 `recordSensitiveAccess` — Audit.** When sensitive access policy requires. Local policy: sensitivity/action. Prohibited duplicate: `playbackAudit.ts`.
- **SH-046 `publishDomainEvent` — outbox.** Revoked/completed facts as approved. Local policy: minimal payload. Prohibited duplicate: synchronous cross-module mutation.
- **SH-037 `recordIntegrationFailure` — Ops.** Provider/reconciliation failure. Local policy: Video operation reference. Prohibited duplicate: provider failure table in Video.

### Domain Logic

- expired under server time means unusable even before the expiration worker runs;
- revocation is authoritative Video state only after an external owner instruction is validated;
- `used` semantics remain guarded by the unresolved ruling: code must not enforce one-time playback unless architecture explicitly settles it;
- playback completion is access evidence, not course academic/certification completion;
- progress events may be sampled/aggregated only under a documented policy; avoid uncontrolled heartbeat writes;
- reconciliation never reactivates a revoked/expired grant solely because a provider token still works.

### Authorization / Compliance

- user/player telemetry must be bound to the authenticated grant/user or trusted provider event;
- admin manual revoke/retry requires Role / Authority and optional step-up if root policy later says so;
- healthcare-sensitive playback evidence invokes AccessAuditLog as required;
- privacy/moderation source reasons are references, not locally interpreted legal decisions.

### Database / Transaction Behavior

- grant transition and corresponding Video access event occur atomically where both are required;
- expiration sweep batches by indexed `expiresAt` and rechecks state/time in owner command;
- source instruction/event ID forms idempotency key;
- concurrent credential issue vs revoke/expire must serialize or compare-and-set so an invalid grant cannot be reactivated.

### Events / Jobs

- expiration sweep through SH-055;
- `video.course_playback.revoked.v1` after commit;
- optional completion event if a downstream owner contract requires it;
- reconciliation worker remains durable/retryable/dead-letter visible.

### Provider Integration

Provider token invalidation/revocation where supported occurs through StreamingVideoProviderPort/SH-070 or provider-specific approved operation. Lack of provider-side revocation does not allow Video to mark a revoked grant active.

### UI / Admin Surface

Consumer surfaces use safe grant state/reason. Optional support view shows grant status, expiry/revocation source reference, event timestamps, and correlation ID, never credential/token.

### Failure Behavior

- already expired/revoked: idempotent result;
- provider revoke unavailable: local grant remains revoked; retry provider cleanup separately and record IntegrationFailure;
- untrusted playback event: reject;
- progress flood: rate-limit/drop according to approved telemetry policy without corrupting access truth;
- reconciliation unsafe discrepancy: manual/ops issue, no auto-reactivation.

### Tests

- expiration race with credential issue;
- concurrent revoke/issue;
- duplicate refund/moderation instruction;
- playback event authorization;
- provider revocation failure with local state preserved;
- reconciliation no-reactivation invariant;
- audit/event separation;
- progress-volume policy tests once settled.

### Documentation Updates

Settle and document `used` semantics/progress retention only when approved. Record any provider-side revocation limitations in provider docs.

### Acceptance Criteria

- expired/revoked grants never issue credentials;
- external revocation cannot mutate Order/Moderation/Privacy truth from Video;
- provider cleanup failure cannot restore access;
- Video access evidence remains append-only and separate from generic Audit;
- reconciliation is safe and observable.

### Exit Gate

Expiration/revocation/concurrency/reconciliation tests pass; repeated revocation is one semantic effect; an expired/revoked grant is denied under server-time checks even if workers/provider cleanup are delayed.

---

# Phase 3 — Live Booking Delivery

## 06 Booking Video Room Provisioning

### Objective

Provision one Video-owned live room for an eligible confirmed video Booking without allowing Booking to own provider state or Video to own Booking state.

### Observable Result

Booking orchestration can request room creation and receive a stable Video result. Video persists one `BookingVideoRoom` and moves it to `active` or `failed` based on translated provider outcome. Retried requests do not create duplicate rooms/provider resources.

### Cluster Build-Plan Link

Implements the provisioning half of CL-05 Feature **11 — Live Booking Video Room and Time-Bounded Join Access**. Requires the Booking groundwork from Cluster Features 08 and 10.

### Dependencies

- Module Feature 01 and provider reliability mechanics from Feature 03;
- Booking & Calendar owner-facts contract and Feature 10 orchestration command;
- live provider-neutral port;
- approved live-provider decision for production adapter; Daily test/proposed adapter may be used under the explicit proposed ruling;
- Healthcare and Track interfaces where product policy requires them.

### In Scope

- `provisionBookingVideoRoom`;
- Booking owner-facts adapter/contract consumption;
- live room domain policy and transitions;
- live provider create/cancel/status methods behind port;
- idempotent provider provisioning job;
- provider-event target mapping to BookingVideoRoom;
- Booking orchestration acknowledgment result;
- safe room-status query.

### Out of Scope

- Booking confirmation/reschedule lifecycle;
- interval scheduling;
- calendar integration;
- JobInterview room;
- join credential issuance (Feature 07);
- group webinars/broadcasting;
- multiple live provider adapters without approved ADR.

### Module-Owned Data

- `BookingVideoRoom`;
- corresponding provider/status enum usage;
- `ProcessedVideoProviderEvent` for live callbacks.

### Public Interfaces

- implement `provisionBookingVideoRoom`;
- implement `getBookingVideoRoomStatus`;
- implement `cancelBookingVideoRoom` for authoritative parent/security instructions;
- extend `applyVideoProviderEvent`/live reconciliation for Booking room targets.

### Shared Operations Used

- **SH-003 `queryOwnerFacts` — Booking owner, proposed contract.** Invocation: obtain current Booking status/type/time/participants/overtime facts. Local policy: minimum facts required for room provisioning. Prohibited duplicate: Booking Prisma repository inside Video.
- **SH-123 `validateOwnedTargetReference` — Booking.** Validate Booking target/version. Local policy: Video location/type requirements. Prohibited duplicate: local Booking validator.
- **SH-005 `resolveEntitlement` — Track Subscription & Entitlement.** Invocation only when approved product policy gates live streaming. Local policy: what the entitlement changes in Video behavior. Prohibited duplicate: `canLiveStream.ts`.
- **SH-011 `evaluateComplianceHold` — Hold owner.** Applicable stop signs. Local policy: provision denial/cancel behavior. Prohibited duplicate: local hold flag.
- **SH-020 `evaluateHealthcareReadiness` — Healthcare.** Provider/BAA/data-boundary decision. Local policy: Video provider path selection/denial. Prohibited duplicate: local HIPAA readiness logic.
- **SH-025 `authorizeOrderEntitlement` — Order.** Use only if the approved Booking delivery policy requires a current Order gate in addition to confirmed Booking. Local policy: do not expand it by assumption. Prohibited duplicate: payment lookup.
- **SH-044/047/048 — idempotency/queue/retry.** Invocation: room create/cancel. Local policy: semantic room key/retryability. Prohibited duplicate: custom queue/retry/idempotency.
- **SH-059/060/061 — provider webhook verification/dedupe/status translation.** Local truth remains `ProcessedVideoProviderEvent` + `BookingVideoRoom`. Prohibited duplicate: Daily/Agora route helpers.
- **SH-068 `invokeVideoProvider` — Video.** Live provider port. Local policy: Booking room request mapping. Prohibited duplicate: provider client in Booking.
- **SH-037 `recordIntegrationFailure` — Ops.** Provider failures. Local policy: room/operation references. Prohibited duplicate: `videoRoomFailure` table.

### Domain Logic

1. Receive Booking orchestration/system request with Booking ID and idempotency/correlation context.
2. Query current Booking owner facts.
3. Require the parent to be eligible for video room provisioning under the approved Booking contract; do not infer eligibility from provider fields.
4. Evaluate hold, Healthcare, and Track gates only where specified.
5. Create/replay one pending BookingVideoRoom.
6. Call live provider with minimized room/time metadata and stable provider request key.
7. Translate response to canonical `active` or `failed`; do not mutate Booking.
8. Return safe status/room reference to Booking orchestration.
9. Provider callback/reconciliation may update only Video-owned room state.

### Authorization / Compliance

System orchestration commands must be authenticated as trusted system context; manual/admin provisioning requires authority. Healthcare provider route must be approved by Healthcare before creating sensitive room. Provider room ID is never authorization.

### Database / Transaction Behavior

- `bookingId @unique` is the current single-room semantic constraint;
- creation and idempotency claim occur atomically;
- provider request is durable through job/outbox rather than untracked side effect;
- concurrent create/cancel/reschedule signals use aggregate lock/CAS;
- persisted join URL fields must not be populated with reusable secrets until U-VS storage ruling explicitly permits a safe representation.

### Events / Jobs

- provision job;
- `video.booking_room.active.v1` or `video.booking_room.failed.v1` after commit;
- provider callback handling;
- later room expiration/cancel cleanup worker;
- Booking orchestration receives result through its public mechanism, not direct DB mutation.

### Provider Integration

`LiveVideoProviderPort`. A fake adapter must pass first. Daily.co may be the current proposed MVP adapter only after the provider decision is recorded for the implementation environment. Agora/AWS Chime stay deferred.

### UI / Admin Surface

Booking UI owns setup display. Video provides `pending|active|failed|expired|cancelled` plus safe reason. Optional support view excludes room tokens/reusable links.

### Failure Behavior

- Booking not eligible/non-video/cancelled: permanent denial;
- duplicate provision request: same semantic room;
- provider timeout: retry with stable provider key, then reconcile;
- terminal provider failure: room failed, Booking unchanged;
- Healthcare deny: no provider room created;
- provider configured ambiguously: production feature disabled until ADR/ruling.

### Tests

- Booking owner-facts contract;
- eligible/ineligible Booking matrix;
- room unique/idempotency/concurrent provisioning;
- provider create timeout/retry;
- webhook dedupe/status mapping;
- prove no Booking writes/imports;
- healthcare/entitlement gate tests;
- join-secret persistence test ensuring no reusable URLs are stored by default.

### Documentation Updates

Before production adapter enablement, record the approved live provider in root/Cluster/Module context and library docs. If persisted room URL fields are repurposed/removed/encrypted, update architecture and migration notes first.

### Acceptance Criteria

- Booking can request but cannot own provider room state;
- Video can create/update room state but cannot transition Booking;
- one Booking produces one current room under current schema;
- duplicate/retried provider requests do not duplicate provider rooms;
- provider failure is observable and isolated;
- no reusable join link becomes durable truth.

### Exit Gate

Booking→Video contract, idempotency, provider fake/approved adapter, healthcare/hold, callback/dedupe, and no-cross-write tests pass. Production enablement additionally requires the live provider proposed ruling to be approved.

---

## 07 Time-Bounded Booking Join Access

### Objective

Issue participant-specific live join credentials only to authorized Booking participants during the approved join window while preserving Booking as the owner of scheduling facts.

### Observable Result

Buyer/professional participants can obtain a short-lived credential only when the Booking and room are currently eligible. Unrelated users, early/late joins, cancelled/expired rooms, holds, and healthcare denials receive stable denial results and no secret.

### Cluster Build-Plan Link

Completes CL-05 Feature **11**.

### Dependencies

- Module Feature 06;
- Booking owner-facts contract including participants/start/end/overtimeGraceMinutes/current status;
- live provider credential method;
- Role / Authority, Healthcare, Hold, Audit interfaces;
- live access proof decision may remain partially unresolved; implementation must use the currently approved evidence combination without inventing a new table.

### In Scope

- `evaluateLiveJoinReadiness` for Booking context;
- `issueVideoJoinCredential` Booking variant;
- time-window policy based on Booking facts + approved grace;
- participant-scoped provider claims;
- access evidence and sensitive audit;
- rate limiting/abuse boundary as provided by root security mechanisms;
- denied-access reason codes.

### Out of Scope

- Booking participant selection/ownership rules;
- changing Booking time/status;
- permanent join links;
- custom video server;
- JobInterview access;
- deciding whether a service is healthcare-sensitive.

### Module-Owned Data

- `BookingVideoRoom` read/update of access-related safe metadata only where approved;
- Video domain-access proof through existing approved mechanism/event;
- no new live-access table unless U-VS ruling explicitly approves one.

### Public Interfaces

- `issueVideoJoinCredential({context:'booking', bookingId, ...})`;
- `getBookingVideoRoomStatus` safe join readiness metadata without secret.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity.** Required for join request. Local policy: Booking-video action. Prohibited duplicate: `videoCurrentUser`.
- **SH-002 `authorizeResourceAction` — Role / Authority.** Participant/resource action. Local policy: Booking facts supplied from owner. Prohibited duplicate: participant permission engine.
- **SH-003 `queryOwnerFacts` — Booking.** Current participant/time/status facts. Local policy: Video join window. Prohibited duplicate: cached Booking truth in room row as authority.
- **SH-011 `evaluateComplianceHold` — Hold.** Current applicable hold. Local policy: deny join. Prohibited duplicate: local suspend flag.
- **SH-020 `evaluateHealthcareReadiness` — Healthcare.** Current provider/access decision. Local policy: deny or approved provider path. Prohibited duplicate: healthcare flag.
- **SH-026 `authorizeContextualResourceAccess` — Booking/context owner.** Business context allow/deny when required by final owner contract. Local policy: combine with Video resource readiness. Prohibited duplicate: all-domain video authorization service.
- **SH-030 `recordSensitiveAccess` — Audit.** Healthcare/sensitive live-token issue/denial/join evidence. Local policy: action/sensitivity metadata. Prohibited duplicate: `joinAudit.ts`.
- **SH-068 `invokeVideoProvider` — Video.** Provider token issue. Local policy: participant role/room/time claims. Prohibited duplicate: provider SDK in route handler.
- **SH-074 `generateSecureToken` — security.** If local signing/randomness is required. Local policy: TTL/audience/bindings. Prohibited duplicate: custom token RNG.
- **SH-125 `recordDomainAccessEvent` — Video.** Video-specific access evidence when approved. Local policy: action/reason. Prohibited duplicate: collapsing domain proof into AccessAuditLog.
- **SH-032/034 — request context/redaction.** Ensure no token enters logs.

### Domain Logic

- current server time, not client clock, controls join eligibility;
- room must be active and match current Booking provider context;
- Booking owner facts must still say the actor is a valid participant and Booking is joinable;
- join window is calculated from Booking start/end plus only the approved early/overtime policy; overtimeGraceMinutes remains Booking context, not Video scheduling truth;
- credential is participant/room/audience bounded and expires no later than the approved window/TTL;
- credential issuance does not mark Booking completed/started;
- credential issue must not rely on stored `buyerJoinUrl`/`professionalJoinUrl` as reusable truth.

### Authorization / Compliance

- server-side participant authorization every issuance;
- healthcare-sensitive join invokes Healthcare and required AccessAuditLog;
- provider room ID alone cannot establish access;
- exact step-up requirement remains root-policy unresolved; do not create local MFA state;
- rate-limit repeated denied/token requests using root security primitives.

### Database / Transaction Behavior

- if access evidence is persisted, issue/evidence transaction must record only hash/safe metadata;
- concurrent room cancellation/expiry and token issue use lock/CAS/recheck immediately before provider token generation or final issuance;
- no raw credential in database, event payload, job payload, audit metadata, or telemetry.

### Events / Jobs

No long-running job required for normal issuance. Room expiration worker is added in hardening/cleanup. Access events/audit are synchronous/durable according to policy; provider availability failure records IntegrationFailure.

### Provider Integration

Live provider token/join-credential method only. Adapter receives canonical participant role and time bounds; it returns provider credential + expiry without leaking SDK-native object across boundary.

### UI / Admin Surface

Booking UI consumes `canJoin`, safe denial reason, and credential only at the secure request boundary. Video does not own a standalone meeting page unless root UI architecture later assigns one.

### Failure Behavior

- too early/late: deny;
- nonparticipant: deny;
- room pending/failed/expired/cancelled: deny;
- Booking stale/cancelled/rescheduled: deny using current owner facts;
- Healthcare/hold deny: no credential;
- provider unavailable: retry-later result, no fake link;
- audit write failure for a policy requiring audit: fail closed where compliance requires proof.

### Tests

- buyer/professional/nonparticipant matrix;
- early/on-time/grace/late boundary tests with controlled clock;
- concurrent cancel/issue race;
- Booking reschedule stale room access denial;
- healthcare/hold deny;
- provider outage;
- token TTL/audience claims;
- DB/log/event scan for raw credentials;
- E2E confirmed Booking → room → participant join → expiry denial.

### Documentation Updates

If live-access proof model or early-join policy is settled, update Module architecture before schema/event changes.

### Acceptance Criteria

- only current authorized participants in the approved time window receive credentials;
- server time and current parent facts are revalidated;
- no reusable public room link is required;
- sensitive audit/domain evidence is produced separately as approved;
- cancellation/reschedule races fail closed.

### Exit Gate

Authorization/time-window/concurrency/security/audit and E2E tests pass; log/persistence scans find no reusable credential; a stale/cancelled/late Booking can never obtain a valid credential through this Module.

---

# Phase 4 — Cross-Cluster Integration Proof

## 08 JobInterview Video Delivery Bridge

### Objective

Reuse Video’s live-provider mechanics for the hiring lane while keeping `JobInterviewVideoRoom` and JobInterview participant/scheduling truth separate from Booking.

### Observable Result

An eligible JobInterview can receive one Video-owned room. Candidate/interviewer participants can obtain short-lived credentials in the approved interview window. Unrelated users cannot. No Booking record or Booking policy is read/written as a shortcut.

### Cluster Build-Plan Link

Implements CL-05 Feature **12 — JobInterview Video Delivery Bridge**.

### Dependencies

- Module Features 06–07 live-provider infrastructure;
- CL-06 Job Interview public owner-facts interface;
- organization/participant Role / Authority rules;
- same Healthcare/Audit/Provider primitives as applicable.

### In Scope

- `provisionInterviewVideoRoom`;
- `getInterviewVideoRoomStatus`;
- `issueVideoJoinCredential` interview variant;
- `cancelInterviewVideoRoom` from authoritative JobInterview instruction;
- interview-specific participant-role-to-provider-claim mapping;
- provider callbacks/reconciliation targeting `JobInterviewVideoRoom`;
- contract/E2E proof of zero Booking lifecycle coupling.

### Out of Scope

- interview scheduling/rescheduling;
- JobApplication/application stage decisions;
- organization membership lifecycle;
- Booking table/model reuse;
- schema consolidation into generic VideoSession;
- candidate hiring decisions.

### Module-Owned Data

- `JobInterviewVideoRoom`;
- `ProcessedVideoProviderEvent` target mapping;
- approved Video domain access evidence.

### Public Interfaces

- implement `provisionInterviewVideoRoom`;
- implement `getInterviewVideoRoomStatus`;
- extend `issueVideoJoinCredential` discriminated context;
- implement `cancelInterviewVideoRoom`;
- live reconciliation supports interview target.

### Shared Operations Used

- **SH-001/002 — actor/authority.** Invocation: interview join/admin actions. Local policy: interview Video action/claims. Prohibited duplicate: interview-video auth service.
- **SH-003 `queryOwnerFacts` — Job Interview.** Current schedule/status/participants. Local policy: Video room/join window. Prohibited duplicate: CL-06 Prisma reads in Video.
- **SH-123 `validateOwnedTargetReference` — Job Interview.** Target validation. Prohibited duplicate: local hiring target lookup.
- **SH-020 `evaluateHealthcareReadiness` — Healthcare.** Only when interview context triggers a healthcare-sensitive lane. Local policy: access/provider enforcement. Prohibited duplicate: Video healthcare decision.
- **SH-044/068 — idempotent live provider command.** Local policy: interview semantic key/claims. Prohibited duplicate: provider SDK in CL-06 or local queue/idempotency.
- **SH-059/060/061 — provider callback handling.** Local truth remains separate Video provider-event ledger. Prohibited duplicate: interview-specific webhook ledger.
- **SH-030/125 — sensitive audit + Video access evidence.** Local policy: interview target/action. Prohibited duplicate: one generic log as both truths.

### Domain Logic

- JobInterview owner facts, not Booking policy, establish interview time/status/participants;
- provider mechanics are reusable but parent-domain policy adapters are distinct;
- one interview → at most one current room under current schema;
- provider failure never changes JobInterview status;
- room active does not imply interview scheduled/completed;
- cancellation occurs only from parent/system/moderation/privacy instruction.

### Authorization / Compliance

- candidate/interviewer/coordinator/observer roles come from JobInterview/Role Authority, not client claims;
- organization membership is interpreted by Role / Authority;
- healthcare-sensitive access audited where required;
- no Booking buyer/professional assumption is reused.

### Database / Transaction Behavior

- `interviewId @unique` enforces current one-room rule;
- idempotent create and concurrent cancel/issue use same persistence primitives as Booking rooms but separate records/keys;
- no Booking table writes, no BookingSlotLock/BookingEvent usage.

### Events / Jobs

- `video.interview_room.active.v1`, `.failed.v1`, `.cancelled.v1`;
- provider create/cancel/reconciliation jobs reuse shared infrastructure;
- events contain JobInterview target reference only, not hiring decision payload.

### Provider Integration

Same LiveVideoProviderPort/approved adapter as Booking unless an explicit Healthcare/provider decision requires a different path. The port accepts a context-neutral room request after Video maps the interview facts.

### UI / Admin Surface

CL-06 hiring UI owns interview presentation. Video supplies safe status/join contract only. A contract harness suffices before CL-06 UI exists.

### Failure Behavior

- invalid/stale/cancelled interview: deny;
- nonparticipant: deny;
- duplicate room request: replay;
- provider degraded: room pending/failed as Video truth, interview unchanged;
- unauthorized organization member: deny via Role / Authority;
- provider target mismatch: reject and record integration failure.

### Tests

- CL-06 public contract tests;
- candidate/interviewer/coordinator/observer/nonparticipant matrix;
- controlled interview join-window tests;
- provider/dedupe/idempotency tests;
- prove no Booking repository/table mutation/import;
- E2E/contract interview → room → join → cancel/expire.

### Documentation Updates

Update only if CL-06 owner-facts contract or participant role semantics become binding differently from current assumptions.

### Acceptance Criteria

- JobInterview video works through CL-06 public facts;
- provider resource remains Video-owned;
- Booking source records/policies are not used;
- interview status cannot be inferred or changed from room status;
- participant authorization is server-side and current.

### Exit Gate

CL-06 contract suite, participant matrix, provider, idempotency, no-Booking-coupling, security, and E2E tests pass; no generic room schema consolidation was introduced.

---

## 09 External Access-Loss, Hold, Moderation, Notification, and Consumer Bridge Verification

### Objective

Prove Video responds correctly when authoritative external decisions invalidate or degrade access, while never mutating the upstream source truth or taking over Search/Notification/Moderation/Hold lifecycles.

### Observable Result

Refund/entitlement loss, ComplianceHold, moderation disablement, parent cancellation, or other approved authoritative instructions can revoke Video grants/rooms/assets through typed interfaces. Consumers receive Video facts/events; notifications are requested safely; no downstream projection or communication system is implemented locally.

### Cluster Build-Plan Link

Implements Video Session’s portion of CL-05 Feature **13 — Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification**.

### Dependencies

- Module Features 05, 07, 08;
- Order current-entitlement/revocation event contract;
- ComplianceHold interface;
- Moderation `SH-103` execution instruction;
- Notification `SH-041`;
- Search public-readiness/refresh owner path where a Video fact affects a searchable parent; Video does not directly own the Search update policy;
- event inbox/idempotency infrastructure.

### In Scope

- handlers/commands for authoritative Order refund/access loss affecting playback grants;
- hold-aware revalidation and/or revocation where policy requires;
- moderation instruction to disable CourseVideoAsset and revoke affected grants;
- parent Booking/JobInterview cancellation instruction to cancel room;
- domain events announcing Video state changes;
- safe Notification requests for user-relevant failure/revocation where owning workflow specifies a message;
- contract proof that Video does not call Typesense or own SearchUpsertEvent.

### Out of Scope

- deciding whether refund/dispute should occur;
- creating/releasing ComplianceHold;
- adjudicating moderation/legal notice;
- Search indexing/de-indexing logic;
- Notification persistence/delivery/provider logic;
- generic event bus/inbox implementation.

### Module-Owned Data

- `CourseVideoAsset.status=disabled` only from approved Video command semantics;
- affected `CourseVideoPlaybackGrant` revocation;
- `BookingVideoRoom`/`JobInterviewVideoRoom` cancellation;
- Video access/domain events;
- no external source records.

### Public Interfaces

- `revokeCoursePlaybackGrant` / batch-by-asset owner command as architecture permits;
- `cancelBookingVideoRoom`;
- `cancelInterviewVideoRoom`;
- `disableCourseVideoAsset` internal/public command if defined by Module architecture extension;
- event consumers for versioned external owner events;
- safe Video facts query for Marketplace/Digital Goods/Search owner composition.

### Shared Operations Used

- **SH-011 `evaluateComplianceHold` — Hold owner.** Invocation: current access/provision checks or authoritative hold-event reaction. Local policy: which Video action is blocked/revoked. Prohibited duplicate: Video hold table/boolean.
- **SH-025 `authorizeOrderEntitlement` — Order.** Invocation: current playback revalidation. Local policy: revoke/deny Video grant. Prohibited duplicate: Stripe/refund interpretation.
- **SH-045 `deduplicateDomainEvent` — event infrastructure.** Invocation: refund/moderation/parent lifecycle event handlers. Local policy: handler + source event version key. Prohibited duplicate: Video event replay table unless canonical inbox implementation requires it.
- **SH-046 `publishDomainEvent` — outbox.** Invocation: committed Video revoke/cancel/disable facts. Local policy: minimal Video payload. Prohibited duplicate: direct downstream table mutation.
- **SH-041 `requestNotification` — Notification.** Invocation: only approved user-facing Video outcome. Local policy: message meaning/template key variables. Prohibited duplicate: email/SMS/push clients inside Video.
- **SH-089 `revokeTemporaryAccessGrant` — Video grant owner.** Invocation: invalidated playback. Local policy: source reason/evidence. Prohibited duplicate: external module directly updating grant row.
- **SH-103 `executeModerationDecision` — Moderation decision / target-owner execution.** Invocation: approved disable/revoke instruction. Local policy: Video target mutation. Prohibited duplicate: DMCA/moderation policy in Video.
- **SH-030/125 — audit/domain evidence.** Invocation: sensitive revoke/access events as applicable. Prohibited duplicate: mixed audit/domain ledger.
- **SH-037 — integration failure.** Notification/provider cleanup failure is operational, not Video entitlement truth.

### Domain Logic

- external event/command must carry source owner ID/version/reference and be deduplicated;
- Video validates that the source instruction targets the relevant Video resource;
- Order refund/entitlement loss revokes future paid playback but does not rewrite Order;
- moderation may disable provider playback/asset only after approved owner instruction;
- Booking/Interview cancellation cancels only the Video room;
- Notification failure never rolls back a committed Video revocation/cancellation;
- Search changes, if needed, are decided/requested by the source/public-readiness owner; Video publishes facts rather than mutating an index.

### Authorization / Compliance

System event handlers use trusted system context. Manual administrative execution requires Role / Authority and step-up only per root matrix. Holds/Moderation reasons exposed to end users must use safe reason codes, not sensitive internal notes.

### Database / Transaction Behavior

- source event inbox claim + owner transition follows canonical idempotent event pattern;
- batch grant revocation uses deterministic query/lock/order and remains idempotent;
- provider cleanup may be async after local access has been revoked/disabled;
- no distributed transaction with Order/Moderation/Notification/Search.

### Events / Jobs

- outbox Video revoked/cancelled/disabled facts;
- async provider disable/cancel cleanup;
- Notification request after source commit/outbox;
- dead-letter visible through Ops, source Video state remains authoritative.

### Provider Integration

Provider disable/cancel/revoke only through Video adapter/SH-070. Provider cleanup errors are retried separately and cannot reactivate local access.

### UI / Admin Surface

Consumer UIs own messaging. Video supplies stable states/reasons. Support-safe view can show source decision reference and cleanup state without legal notes or provider secrets.

### Failure Behavior

- duplicate external event: no duplicate revoke/cancel;
- stale source event superseded by current owner facts: ignore/reconcile according to version policy;
- provider cleanup fails: keep local revoke/disable/cancel, retry cleanup;
- Notification/Search unavailable: source Video change remains committed; downstream retry belongs to owner rail;
- invalid moderation target/instruction: reject and audit/ops as appropriate.

### Tests

- refund/access-loss contract;
- hold check/revocation matrix;
- moderation instruction and no local adjudication;
- duplicate event inbox;
- parent cancellation room cleanup;
- provider cleanup failure with local denial preserved;
- Notification request payload safety;
- code/import test proving no Typesense, email, SMS, push, moderation-case, or hold repository in Video.

### Documentation Updates

Add any newly approved public command/event names to Module architecture before exposing them. Do not silently infer Search responsibility.

### Acceptance Criteria

- authoritative external access loss produces correct Video state without external table mutation;
- provider cleanup failure cannot restore access;
- Notification/Search rails are called only through their public contracts or owner events;
- no local hold/moderation/refund truth is created;
- event replay causes one semantic effect.

### Exit Gate

Cross-module contract/inbox/revocation/notification/provider-cleanup tests pass; dependency repository/import scan finds no prohibited external implementation; all access-loss paths deny future Video credentials immediately under current Video truth.

---

# Phase 5 — Privacy and Production Hardening

## 10 Privacy Subject Inventory, Retention Facts, Grant Revocation, and Provider Deletion

### Objective

Implement Video Session’s Privacy / Data Erasure target executor so Privacy can inventory and disposition Video-owned records/provider resources without transferring orchestration or retention authority into Video.

### Observable Result

Privacy can ask Video what subject-linked Video data exists and instruct an erase/anonymize/revoke/retain action. Video returns typed execution evidence, revokes access before destructive work where required, deletes provider resources idempotently, and never creates a PrivacyRequest/DataErasureJob itself.

### Cluster Build-Plan Link

Implements Video Session’s portion of CL-05 Feature **14 — Privacy Target Executors, Retention, and Provider Deletion**.

### Dependencies

- Module Features 03, 05, 06–09;
- Privacy SH-095–098 protocol;
- provider deletion SH-070;
- Audit/Ops interfaces;
- approved retention rules/exemptions supplied by Privacy/owner facts.

### In Scope

- `enumerateSubjectData` for Video-owned subject-linked rows;
- `evaluateRetentionRequirement` returning Video-specific facts, not final privacy decision;
- `executePrivacyInstruction` for CourseVideoAsset, playback grants/events, Booking/Interview room records/references, provider resources, dedupe metadata where permitted;
- access revocation before deletion;
- provider resource delete/absent semantics;
- anonymization of permitted personal/request metadata;
- export contribution if Privacy architecture requires Video data in exports;
- idempotent retry and partial-failure results.

### Out of Scope

- Privacy request intake/identity verification;
- DataErasureJob/Target lifecycle;
- deciding legal retention exemption;
- deleting Order/Booking/JobInterview/Media source records;
- search privacy completion aggregation;
- generic anonymization framework ownership.

### Module-Owned Data

Potential subject data includes:

- room participant/access/provider-reference metadata in Video-owned room records;
- CourseVideoAsset creator/provider metadata where personal data exists;
- CourseVideoPlaybackGrant user/order/request metadata;
- CourseVideoPlaybackEvent user/request metadata;
- ProcessedVideoProviderEvent target/payload-hash metadata where subject-linked;
- external Mux/live-provider assets/rooms/logs under Video control.

### Public Interfaces

- `enumerateSubjectData`;
- `evaluateRetentionRequirement`;
- `executePrivacyInstruction`;
- export serializer/contribution if required.

### Shared Operations Used

- **SH-095 `executePrivacyInstruction` — Privacy orchestrates, Video executes.** Invocation: typed target instruction. Local policy: Video row/provider disposition. Prohibited duplicate: `videoPrivacyRequestService.ts`.
- **SH-096 `enumerateSubjectData` — each data owner.** Invocation: Privacy inventory. Local policy: Video record/provider cursor mapping. Prohibited duplicate: Privacy reaching directly into Video Prisma/provider SDK.
- **SH-097 `evaluateRetentionRequirement` — owner facts + Privacy exemption.** Invocation: before destructive action. Local policy: Video facts relevant to retention. Prohibited duplicate: Video legal retention decision.
- **SH-098 `anonymizePersonalFields` — shared primitive/owner mapping.** Invocation: retained Video rows where permitted. Local policy: exact Video field map. Prohibited duplicate: ad hoc string scrubbing.
- **SH-070 `deleteProviderResource` — Video provider owner.** Invocation: Mux/live resource removal. Local policy: provider target/result mapping. Prohibited duplicate: Privacy calling Mux/Daily directly.
- **SH-089 `revokeTemporaryAccessGrant` — Video.** Invocation before/with privacy disposition. Local policy: privacy source reference. Prohibited duplicate: Privacy direct grant update.
- **SH-044/047/048 — idempotent durable deletion.** Local policy: target instruction key/retry classification. Prohibited duplicate: custom erasure queue.
- **SH-030/029 — Audit.** Material destructive/manual actions as required. Prohibited duplicate: Video privacy audit ledger.
- **SH-032/034/037 — Ops.** Correlation/redaction/provider failure. Prohibited duplicate: raw subject/provider payload logs.

### Domain Logic

- inventory is stable/cursorable and identifies owner record + provider resource references without exposing secrets;
- product deletion/status is distinct from privacy erasure/anonymization;
- Privacy supplies/records final retain versus erase instruction; Video returns owner facts and executes it;
- revoke playback/live access before destructive provider deletion when necessary;
- provider `not found` is an idempotent deletion success state when local policy agrees;
- retained evidence is minimized/anonymized only under approved mapping and exemption;
- provider deletion never causes Video to delete parent Booking/Interview/Order/Course/Media rows.

### Authorization / Compliance

Only Privacy-authorized system workflow invokes destructive executor. Manual retry requires approved admin authority and optional step-up per root policy. Provider IDs and subject metadata remain server-only/sanitized.

### Database / Transaction Behavior

- each privacy instruction is idempotency-keyed by Privacy target ID/instruction version;
- local revoke/anonymize/delete transition is transactional per Video aggregate; provider deletion may be an async step with durable result;
- retention preserves referential integrity and minimal proof;
- cascade behavior is explicitly tested before destructive migration/command use.

### Events / Jobs

- privacy execution jobs through shared queue;
- provider deletion/retry;
- optional owner completion fact returned to Privacy rather than a competing Video privacy lifecycle;
- IntegrationFailure on retryable provider failures.

### Provider Integration

Mux and approved live-video provider deletion/revocation through their Video adapters. No provider client in Privacy.

### UI / Admin Surface

No standalone Video privacy UI. Privacy/admin surface consumes typed results. Optional debug execution view is privacy-authorized and redacted.

### Failure Behavior

- provider resource absent: idempotent success/absent result;
- retention required: return `retained` with source reason/evidence reference supplied through protocol;
- provider outage: retryable partial target result; no false `erased` result;
- duplicate instruction: same semantic result;
- unsafe cascade/reference ambiguity: fail and require architecture/migration review.

### Tests

- inventory completeness by subject;
- erase/anonymize/retain matrix;
- provider delete success/absent/retryable/terminal;
- grant revocation before delete;
- duplicate instruction idempotency;
- cascade/referential integrity;
- telemetry redaction;
- prove no PrivacyRequest/DataErasureJob creation;
- end-to-end Privacy harness against Video executor.

### Documentation Updates

Record final Video privacy inventory and retained-field maps. If a new retention requirement appears, update Module/root privacy architecture before code assumes it.

### Acceptance Criteria

- Privacy can inventory Video data through typed contract;
- only Privacy orchestrates lifecycle completion;
- provider deletions are idempotent/retryable;
- access is revoked appropriately before destructive execution;
- retained/anonymized records follow explicit approved mappings;
- no neighboring source record is deleted by Video.

### Exit Gate

Privacy inventory/execution/provider-deletion/retention/idempotency/redaction suites pass; duplicate executor calls are safe; no Video-local privacy orchestration exists.

---

## 11 Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness

### Objective

Harden every launch-critical Video path after course, Booking, interview, guardrail, and privacy flows are proven, without adding new product scope or resolving future architecture by convenience.

### Observable Result

Video delivery remains correct under provider outage, duplicate/missed callbacks, stale parent state, concurrent grant/room mutations, delayed workers, abusive credential requests, privacy retries, and operational recovery. Operators can inspect safe health/reconciliation state without provider secrets or business-truth substitution.

### Cluster Build-Plan Link

Implements Video Session’s portion of CL-05 Feature **15 — Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness**.

### Dependencies

- Module Features 01–10;
- approved production Mux configuration;
- approved live-video provider decision and production configuration for live launch;
- root step-up matrix finalized for any Video-sensitive admin actions;
- production Audit/Ops/queue/outbox/secret-management implementations;
- unresolved Video decisions either resolved or explicitly feature-flagged out of launch.

### In Scope

- scheduled/manual Mux and live-room reconciliation;
- room/grant expiration/cleanup;
- dead-letter and safe admin retry hooks through Ops;
- concurrency review for create/cancel/issue/revoke/expire races;
- webhook replay/security suite;
- endpoint rate limits/abuse controls using root mechanisms;
- credential/secret log-scrape and persistence scanning;
- least-privilege provider scopes and secret rotation verification;
- audit completeness for approved sensitivity matrix;
- health/metrics/SLO-oriented operational visibility;
- database index/constraint tuning;
- clean and realistic-seed migration verification;
- production performance/load tests for launch-critical Video operations.

### Out of Scope

- adding new providers for redundancy;
- group broadcast/webinar features;
- generic incident management UI;
- custom video server;
- generic VideoSession model consolidation;
- new legal/healthcare policy;
- analytics product redesign.

### Module-Owned Data

Review/tune existing Video models only. Any new Video table/column requires a documented owner and architecture justification; hardening alone is not permission to invent lifecycle records.

### Public Interfaces

Harden existing contracts. No new broad public API by default. Authorized system/admin commands may include:

- reconciliation dry-run/repair;
- safe provider retry/replay;
- room/grant cleanup/expiration;
- safe health/readiness diagnostics.

### Shared Operations Used

All earlier SH operations remain applicable, with emphasis on:

- **SH-014 `requireStepUpForSensitiveAction` — Identity & Access.** Invocation: only root-approved manual sensitive Video admin actions. Local policy: declare action/target. Prohibited duplicate: Video MFA flag/session.
- **SH-032 `createRequestContext`, SH-033 `writeStructuredLog`, SH-034 `sanitizeTelemetryMetadata`, SH-035 `captureException`, SH-036 `emitMetric`, SH-037 `recordIntegrationFailure`, SH-038 `recordQueueTelemetry`, SH-039 `checkServiceHealth` — Ops.** Invocation across every provider/job endpoint. Local policy: Video-safe dimensions and health semantics. Prohibited duplicate: local logger/Sentry/metrics/incident systems.
- **SH-044–SH-052 — idempotency/event dedupe/queue/retry/locks/concurrency.** Invocation across all high-risk paths. Local policy: semantic keys, conflict and retry rules. Prohibited duplicate: in-memory locks/custom queues/local idempotency.
- **SH-055 `runDeadlineExpiration` — scheduler.** Room/grant expiry. Local policy: Video expiration semantics. Prohibited duplicate: per-Module cron framework.
- **SH-059–SH-063 — webhook/reconciliation/snapshot pattern.** Local truth: Video provider event/asset/room records. Prohibited duplicate: provider object treated as truth or generic provider-event table.
- **SH-068/070 — Video provider invoke/delete.** Provider calls remain adapter-only. Prohibited duplicate: SDKs outside infrastructure.
- **SH-072/074/078 — cryptography/token/minimization.** Local policy: token claims/evidence. Prohibited duplicate: local crypto/secret helpers.
- **SH-095–SH-098 — privacy/anonymization.** Re-run production coverage; no local orchestration.
- **SH-030/125 — Audit + Video domain access evidence.** Verify completeness and separation.

### Domain Logic

Hardening must prove these invariants under failure:

- provider callbacks are at-least-once but Video effects are once per semantic event;
- missed callbacks can be reconciled without blindly adopting provider state;
- local revoked/expired/disabled/cancelled access cannot be reactivated by provider reconciliation;
- current parent facts and server time are revalidated for credential issue;
- provider outage changes availability/degradation, not upstream business truth;
- dead-letter is operational status, not room/asset/grant truth;
- current launch does not depend on unresolved join-URL persistence, alternate access basis, or unapproved provider behavior;
- no cache/snapshot becomes current authorization truth where revalidation is required.

### Authorization / Compliance

Security review must verify:

- server-only provider credentials;
- least privilege scopes;
- webhook secret rotation path;
- approved step-up coverage;
- RLS/server authorization alignment where applicable;
- Healthcare provider/data-boundary rules;
- AccessAuditLog completeness for healthcare/sensitive token/playback actions;
- moderation/hold/refund revocation coverage;
- privacy executor coverage;
- no reusable credential in logs/events/audit/db;
- safe error reason exposure.

### Database / Transaction Behavior

Review and prove:

- provider-event unique constraint behavior under parallel callbacks;
- booking/interview room one-parent uniqueness;
- grant issue/revoke/expire concurrency strategy;
- idempotency persistence and replay result;
- index coverage for provider/status/expiry/reconciliation queries;
- cascade/delete behavior under privacy;
- migration from clean DB and realistic seeded DB;
- no schema migration silently resolves open architecture questions.

### Events / Jobs

- scheduled Mux reconciliation;
- scheduled live-room reconciliation/cleanup;
- grant expiration;
- dead-letter replay through Ops;
- provider health checks;
- metrics for request latency, provider failure rate, webhook lag, duplicate event count, reconciliation discrepancies, grant/credential denials by safe reason, queue age/dead letters;
- event consumer/outbox replay tests.

### Provider Integration

Production Mux and approved live provider must support:

- bounded timeout;
- retry classification;
- idempotent provider request keys where supported;
- explicit unknown-status handling;
- reconciliation/list/get/delete behavior as required;
- minimized provider inputs;
- secrets rotated without code changes;
- no SDK types outside adapters.

### UI / Admin Surface

Integrate safe Video health/reconciliation status into approved Ops tooling. Show canonical status, provider, safe reference, timestamps, retryability, correlation, discrepancy class. Never expose raw webhook bodies, credentials, join URLs, signed playback URLs, PHI, or unnecessary user data.

### Failure Behavior

Explicitly exercise:

- provider unavailable, degraded, delayed;
- create response lost after provider success;
- missed webhook;
- duplicate/reordered webhook;
- provider resource absent while local active;
- local cancelled/deleted while provider still exists;
- concurrent issue vs revoke/expire;
- concurrent provision vs cancel/reschedule;
- parent owner unavailable during current access revalidation;
- audit service unavailable where compliance requires audit proof;
- Privacy provider delete partially failed;
- Notification unavailable after Video transition;
- dead-letter replay after partial technical side effect;
- reconciliation discrepancy unsafe for auto-repair.

### Tests

- unit transition/policy suite under controlled clock;
- DB parallel-concurrency tests for room/grant/provider-event races;
- webhook signature/replay/order/security tests;
- provider chaos/degradation adapter tests;
- reconciliation dry-run/safe-repair/manual-review tests;
- token/URL/secret persistence and full log-scrape tests;
- authorization/RLS tests required by root architecture;
- healthcare/hold/moderation/refund/privacy end-to-end revocation tests;
- AccessAuditLog completeness tests;
- load tests for credential issuance and webhook processing at expected launch scale;
- migration clean/seeded tests;
- full typecheck/lint/unit/integration/contract/provider/privacy/concurrency/E2E/build suite.

### Documentation Updates

Before marking production-ready:

- resolve/record the live provider decision;
- record final join-credential storage policy;
- resolve any grant-cardinality/`used` semantics required by launch;
- document reconciliation auto-repair matrix;
- document provider secret/rotation and health procedure in library/ops context;
- update progress with production blockers explicitly feature-flagged out if unresolved.

### Acceptance Criteria

- every provider effect is idempotent/reconcilable;
- duplicate provider callbacks produce one business effect;
- missed callbacks are detectable;
- revoked/expired/cancelled/disabled local truth cannot be accidentally reactivated;
- concurrency tests produce deterministic results;
- no reusable tokens/URLs/secrets appear in DB/log/event/audit scans;
- Privacy, Moderation, Hold, refund/entitlement-loss, and Healthcare paths fail safely;
- Ops can see failures/dead letters without becoming Video truth;
- all launch-blocking unresolved decisions are resolved or feature-disabled.

### Exit Gate

Video Session is production-ready only when:

- Mux production adapter/configuration is approved and tested for on-demand launch;
- live-video production adapter is approved and configured for any live feature included in launch;
- reconciliation works for launch providers;
- room/grant/provider-event concurrency and replay tests pass;
- sensitive access audit coverage passes the approved matrix;
- privacy target executor passes end-to-end;
- token/URL/secret scans find no reusable secret leakage;
- provider outage/dead-letter/retry recovery is proven;
- clean and seeded migrations pass;
- typecheck, lint, unit, integration, contract, provider, privacy, concurrency, E2E, and production build all pass;
- every unresolved item that blocks a launch behavior is either resolved by binding architecture decision or explicitly disabled from launch.

---

# Module Integration Phase

The integration proof is distributed across Features **04, 06–10**, but the Module is not considered integrated until the following public-boundary tests pass without direct neighboring Prisma access:

| Boundary | Contract proof | Prohibited shortcut |
| --- | --- | --- |
| Video ↔ Media | ready/permitted source Media facts support registration; unsafe/non-ready source denies | reading `MediaAsset` repository directly from Video; validating/scanning source in Video |
| Video ↔ Marketplace Supply | Course target/version facts validate registration | changing CourseDetails/Offering status from Video |
| Video ↔ Transaction / Order | SH-025 allows/denies paid playback and current revalidation | reading Stripe/payment state or inferring entitlement from `orderId` existence |
| Video ↔ Digital Goods | contextual terms/license/access-policy facts supplement playback where required | implementing DigitalGoodsPolicy in Video |
| Video ↔ Booking & Calendar | Booking owner facts drive room/join window; Booking orchestration receives Video result | changing Booking state or reading Booking repository directly |
| Video ↔ Job Interview | interview owner facts drive room/join; no Booking dependency | treating JobInterview as Booking |
| Video ↔ Healthcare | healthcare provider/data-boundary decision gates access/provider path | BAA/healthcare policy in Video |
| Video ↔ Hold | current hold decision blocks applicable Video action | local blocked flag |
| Video ↔ Moderation | approved execution instruction disables/revokes target | local legal/moderation adjudication |
| Video ↔ Audit | Video event + AccessAuditLog both exist where required | using one ledger as the other |
| Video ↔ Privacy | typed inventory/executor/result | Video-created PrivacyRequest/DataErasureJob |
| Video ↔ Notification | safe notification request after Video fact | SMTP/SMS/push client in Video |
| Video ↔ Ops | failure/health/queue telemetry | local generic incident/failure truth |

Cross-Module integration tests must mock or run the **public contract**, not bypass it with test-only direct database joins that production code cannot use.

---

# Module Hardening Phase

The hardening work is concentrated in Feature **11**, but every earlier feature must already carry local failure tests. Final hardening specifically verifies:

- room create/cancel/join races;
- playback grant issue/use/revoke/expire races;
- provider callback duplication/reordering/missing delivery;
- provider create-success/response-loss ambiguity;
- current owner revalidation when parent state changes;
- durable job retries and dead-letter behavior;
- no provider state promoted to Workin Ants truth during reconciliation;
- healthcare-sensitive access/audit behavior;
- privacy provider deletion and retention paths;
- moderation/refund/hold access removal;
- token/JWT/join/signed URL non-persistence;
- telemetry redaction and low-cardinality metrics;
- database/index/migration behavior under realistic data volume;
- import/boundary scans preventing provider SDKs or neighboring repositories outside approved layers.

---

# Phase Summary

| Phase | Name | Features |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | **01** Video Contracts, Repositories, Lifecycle Policies, and Provider Ports |
| 2 | On-Demand Course Streaming | **02** Course Video Registration and Provider-Ingest Intent; **03** Mux Adapter, Provider Webhooks, and CourseVideoAsset Lifecycle; **04** Order-Gated Playback Grant and Short-Lived Playback Credential; **05** Playback Evidence, Expiration, Revocation, and Course-Provider Reconciliation |
| 3 | Live Booking Delivery | **06** Booking Video Room Provisioning; **07** Time-Bounded Booking Join Access |
| 4 | Cross-Cluster Integration Proof | **08** JobInterview Video Delivery Bridge; **09** External Access-Loss, Hold, Moderation, Notification, and Consumer Bridge Verification |
| 5 | Privacy and Production Hardening | **10** Privacy Subject Inventory, Retention Facts, Grant Revocation, and Provider Deletion; **11** Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness |

**Total numbered features: 11.**

### Cluster alignment summary

| CL-05 milestone | Video Session features |
| --- | --- |
| Feature 06 — Course Video Ingest and Signed Playback | Module Features **02–05** |
| Feature 11 — Live Booking Video Room and Time-Bounded Join Access | Module Features **06–07** |
| Feature 12 — JobInterview Video Delivery Bridge | Module Feature **08** |
| Feature 13 — Entitlement Loss / Moderation / Notification / Hold bridge | Module Feature **09** |
| Feature 14 — Privacy Target Executors / Provider Deletion | Module Feature **10** |
| Feature 15 — Production Hardening | Module Feature **11** |

Module Feature **01** is preparatory source-of-truth/contract work and must be scheduled so it does not contradict the Cluster dependencies that precede Feature 06.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root `context/project-overview.md`.
2. Read root `context/architecture.md` and `context/code-standards.md`.
3. Read `context/shared/shared-operations.md`.
4. Read CL-05 `architecture.md` and `build-plan.md`.
5. Read `video_session/module-architecture.md` and this implementation plan.
6. Read public-interface sections for direct dependencies needed by the feature.
7. Read `context/progress-tracker.md` and confirm the relevant prior Cluster/Module exit gate.
8. Check the Video unresolved-decision register and determine whether any item blocks this feature.
9. Write the concise feature implementation specification below.
10. Implement only the numbered feature.
11. Run the feature-specific typecheck/lint/unit/integration/contract/provider/concurrency/privacy/E2E checks.
12. Verify success, denial, retry, stale, idempotency, and provider-failure paths—not only the happy path.
13. Update progress.
14. Update architecture only when a binding decision legitimately changed.
15. Record assumptions, known failures, remaining risks, unresolved decisions, and deferred work.

Do not start adjacent “helpful” functionality merely because the implementation location is nearby.

---

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise specification containing:

- **Objective** — the one observable result to be produced;
- **Observable result** — user/system behavior proving completion;
- **Cluster Build-Plan link** — exact CL-05 milestone supported;
- **Dependencies** — prior Module features, source-owner interfaces, SH operations, schema/migration prerequisites, provider configuration;
- **In scope** — exact code/data/contracts to implement;
- **Out of scope** — neighboring responsibilities explicitly excluded;
- **Owned data affected** — Video models/enums/events only;
- **Public contracts** — commands/queries/events/executor signatures added or changed;
- **Shared operations consumed** — SH ID/name, owner, invocation point, local policy, prohibited duplicate;
- **Permissions/compliance** — actor, authority, ownership context, hold, entitlement, healthcare, moderation, privacy, audit requirements;
- **Primary workflow** — success path through Video source truth;
- **Provider integration** — port/adapter calls and normalized results, if applicable;
- **Jobs/events** — outbox/inbox/job payload, idempotency, retries, correlation;
- **Idempotency/concurrency** — semantic key, transaction/lock/CAS boundary, replay result;
- **Error behavior** — validation, authorization, stale state, denial, provider retry, terminal failure, manual review;
- **Tests** — exact unit/integration/contract/provider/concurrency/privacy/E2E coverage;
- **Acceptance criteria** — observable pass conditions;
- **Documentation updates** — progress/interface/architecture/shared-operation/library changes required.

Do **not** generate all feature specifications in advance. The plan above is the sequence and binding guardrail; the implementation specification is produced only for the next feature being built.

---

# Required Completion Report

After every numbered feature, the coding agent must report:

- Feature completed;
- Observable result verified;
- Files added;
- Files changed;
- Database changes;
- Migrations/constraints/indexes changed;
- Dependencies added/changed;
- Video public interfaces added/changed;
- Dependency Module contracts consumed;
- Shared operations reused, by `SH-###` ID;
- Events/outbox/inbox handlers added;
- Jobs/workers/schedules added;
- Provider port/adapter changes;
- Tests added/changed;
- Commands run;
- Manual/contract/E2E verification performed;
- Authorization/security/compliance verification;
- Privacy/retention verification where applicable;
- Documentation/progress updated;
- Assumptions;
- Known failures;
- Remaining risks;
- Unresolved decisions encountered;
- Deferred work;
- Exit-gate result: **PASS** or **FAIL**, with every failed criterion named.

A feature is not complete because its happy path works. A failed exit gate remains a failed feature until the criteria pass or an explicit architecture/progress exception is approved.

---

# Final Module Quality Gate

Before declaring Video Session implementation complete for the MVP scope, verify all of the following:

1. Every Video-owned lifecycle has one owner and one transition path.
2. Booking and JobInterview remain separate parent truths and separate current room records.
3. CourseVideoAsset remains provider-streaming truth; MediaAsset remains raw/source-file truth.
4. Order remains purchase entitlement truth; CourseVideoPlaybackGrant remains temporary Video access proof.
5. Digital Goods policy and accessibility truth are not absorbed into Video.
6. Healthcare decides regulated-lane/provider readiness; Video only enforces it.
7. Canonical shared operations are used rather than reimplemented.
8. Provider clients exist only behind Video adapters/ports.
9. Webhooks are verified, deduplicated, translated, and reconcilable.
10. Provider state never directly becomes Workin Ants domain truth.
11. No reusable room/playback token or signed URL is durable/logged.
12. `CourseVideoPlaybackEvent`, `AccessAuditLog`, and `ProcessedVideoProviderEvent` remain distinct evidence.
13. Privacy orchestration remains Privacy-owned; Video executor coverage is complete.
14. Moderation/Hold/Order/parent cancellations remove access through owner interfaces without cross-owner mutation.
15. Current owner facts/server time are revalidated when a credential depends on them.
16. Concurrency/idempotency/replay tests prove one semantic effect.
17. Reconciliation cannot reactivate revoked/expired/cancelled/disabled Video truth.
18. Search and Notification remain downstream rails, not Video implementations.
19. Live provider and any launch-blocking unresolved schema/security decisions are explicitly resolved or feature-disabled.
20. A coding agent can execute each feature without inventing ownership, provider, privacy, security, or lifecycle architecture.
