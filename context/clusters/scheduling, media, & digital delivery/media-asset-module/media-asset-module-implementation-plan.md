# Media / File Access Module Implementation Plan

> **Module ID:** `media_file_access`  
> **Module:** Media / File Access Module  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Companion Module architecture:** `module-architecture.md`  
> **Parent Cluster plan:** CL-05 `build-plan.md`  
> **Plan status:** implementation-grade Module plan for the Workin Ants MVP  
> **Scope rule:** this plan implements only Media / File Access-owned truth and owner-specific integration work. It does not independently resequence CL-05 or absorb adjacent Module responsibilities.

---

## Core Principle

Implement Media / File Access through narrow, verifiable slices that turn untrusted bytes into safe `MediaAsset` truth and then expose those bytes only through bounded, contextual, short-lived delivery.

```text
public / observable behavior
→ validated Media command/query
→ canonical actor + authority + contextual decision
→ Media-owned policy
→ authoritative Media write/read
→ shared-operation calls
→ durable worker/provider effect where required
→ Media domain evidence + shared audit/ops effects
→ tests
→ exit gate
```

The Module must prove two independent things:

1. **File safety:** an uploaded object cannot become `MediaAsset.ready` until every policy-required validation, scan, and processing gate passes.
2. **File access:** a technically ready file still cannot be exposed until the contextual owner authorizes the business action and Media verifies its own local delivery conditions.

The implementation sequence follows the parent CL-05 plan rather than creating a second roadmap. Media is the primary owner for Cluster Features **01** and **02**, then participates as an owner executor in Cluster Features **13**, **14**, and **15**.

---

## Build Rules

1. Follow root `project-overview.md`, root `architecture.md`, root `code-standards.md`, the Canonical Shared Operations Registry, CL-05 architecture, CL-05 build plan, and `module-architecture.md`.
2. `MediaAsset` is file truth. Contextual join records explain business meaning and remain semantically owned by the contextual Module.
3. Do not create a generic attachment/business-entitlement system inside Media.
4. Consume authentication through SH-001 and authorization through SH-002. Do not create Media-local generic auth infrastructure.
5. Consume contextual access through owner public contracts such as SH-026. Do not infer Order, Agreement, resume, Message, Job, Gig, Offering, or digital purchase entitlement from foreign tables.
6. Reuse canonical SH-### operations. If a shared implementation is not yet available, build against its interface/test fake rather than introducing a Module-local replacement.
7. Every mutation must be runtime validated, server authorized, idempotent where retry is possible, and transaction-safe for Media-owned state.
8. Provider details terminate at Media-owned ports/adapters. Provider payloads must not leak into application/domain contracts.
9. Cloudflare R2 is the current object-storage rail. Contextual Modules must never instantiate their own R2 clients or presign Media objects directly.
10. Malware scanning is required by policy where configured. A required scan fails closed. The production scanner provider remains unresolved until explicitly selected.
11. Original filenames never become object keys. Private/sensitive objects are not exposed through permanent public URLs.
12. Public images should use processed derivatives. Raw-original public exposure is disabled by default for the MVP unless an explicitly approved policy later permits it.
13. Slow/provider-dependent operations use SH-047 durable jobs and SH-048 retry policy. Long request-bound processing pipelines are prohibited.
14. Media domain evidence, generic AuditEvent/AccessAuditLog, and Observability records remain distinct.
15. Privacy / Data Erasure owns privacy request/job/target/retention orchestration. Media implements only its owner inventory, retention-fact contribution, and target executor.
16. Content Moderation & Legal Notice owns moderation/legal decisions. Media executes file-level freeze, public URL revocation, grant revocation, restoration, or deletion after an authorized instruction.
17. Search remains projection. Media may request SH-091 refresh; it must not write Typesense or SearchUpsertEvent directly when the Search command owns that action.
18. Generic temporary-grant mechanics may be reused through SH-088, but `MediaAccessGrant` remains distinct from `AgreementAccessGrant`, `DigitalDownloadGrant`, and `CourseVideoPlaybackGrant`.
19. Never treat `MediaAccessEvent` as a substitute for `AccessAuditLog` when sensitive-access policy requires both.
20. Unresolved architecture must be surfaced. A coding agent must not silently settle join stewardship, scanner provider, grant one-time semantics, retention periods, or encryption/KMS policy by implementation convenience.
21. Every numbered feature ends with automated tests, documented verification, progress update, and a concrete exit gate.
22. Do not begin the next feature until the prior exit gate passes or the project progress tracker records an approved exception.

---

## Preconditions

### Hard platform dependencies

These capabilities must exist as real implementations or approved canonical interfaces before production completion:

- PostgreSQL and Prisma migrations/transactions;
- runtime schema validation under root code standards;
- SH-001 authenticated actor resolution;
- SH-002 server-side resource authorization;
- SH-011 ComplianceHold evaluation;
- SH-026 contextual resource-access decision contract for real consumers;
- SH-030 sensitive access audit for sensitive files;
- SH-032 request/correlation context;
- SH-034 telemetry sanitization;
- SH-037 IntegrationFailure reporting;
- SH-044 idempotent command execution;
- SH-046 transactional outbox/domain-event publication where asynchronous consumers exist;
- SH-047 durable job execution and SH-048 retry/backoff;
- SH-051/052 database concurrency primitives where races exist;
- SH-070 provider-resource deletion contract;
- SH-072/074/086 shared cryptographic primitives;
- SH-095–098 Privacy target protocol;
- SH-103 Moderation target-execution protocol;
- object-storage secret management and server-only credential loading.

### Hard Module/data dependencies

Before Media implementation proceeds beyond contract scaffolding:

- current Media Prisma models/enums must be inspected against actual migrations;
- `MediaAsset.storageKey` uniqueness must exist in the database;
- indexes needed for upload status, grants, expiry, and provider/storage lookup must be verified;
- destructive cascade behavior for `MediaAccessGrant` and `MediaAccessEvent` must be reviewed before production erasure/cleanup is enabled;
- at least one active `MediaUploadPolicy` for a low-risk test context and one sensitive test context must be seedable;
- contextual owners must be able to validate target references through SH-123 or owner-specific public contracts before production attachment/access.

### Dependencies that may initially be stubbed behind contracts

The parent CL-05 plan explicitly allows contract fakes rather than temporary ownership. Media may initially use test doubles for:

- R2/object storage while domain contracts and repository rules are being tested, provided the port exactly matches the approved Media contract;
- malware scanner while the production provider is unresolved;
- Healthcare readiness (SH-020) in non-healthcare test slices;
- contextual owner authorization (SH-026) using an explicit fake owner contract;
- Audit / Observability sinks;
- Search refresh (SH-091);
- Privacy and Moderation command callers.

A fake is never permission to create a new source of truth or a replacement service inside Media.

### Approved requirements and remaining proposed-ruling prerequisites

R009 requires immutable/effective MediaUploadPolicy versions through SH-080 with stable evidence of the exact applied version. Current schema is insufficient; a later approved schema/migration is a prerequisite to production policy-version behavior. R010 requires a distinct upload-session status representation; until its later migration, Media-owned typed mapping isolates legacy MediaAssetStatus storage and consumers must not depend on that coupling. Contract fixtures may precede these migrations.

The following architecture items remain Proposed Rulings in `module-architecture.md` and must be resolved or implemented as explicitly provisional before their migration/API commitment:

- retention-safe replacement for unsafe cascade deletion of access/security evidence where required;
- default prohibition on `public_original` for MVP;
- contextual join schema/code stewardship while preserving contextual semantic ownership.

---

# Phase 1 — Contracts and Secure Upload Intake

This phase supplies the Module-local contracts and the first half of CL-05 Feature 01. It creates no business attachment semantics and no contextual entitlement rules.

## 01 Media Contracts, Lifecycle Isolation, and Policy-Version Foundation

### Objective

Establish the implementation boundary, typed public contracts, repository interfaces, Media lifecycle rules, and version-safe upload-policy semantics before provider code or workers are allowed to mutate Media state.

### Observable Result

A test harness can:

- create and query an approved upload-policy version;
- validate a `createMediaUploadSession` request against a typed contract;
- exercise MediaAsset and upload-session transition rules without a real object-storage provider;
- query a stable `MediaReadinessResult` shape;
- prove that active policy evidence used by an upload cannot be silently rewritten later.

### Cluster Build-Plan Link

Supports **CL-05 Feature 01 — Secure Upload to Ready MediaAsset**, specifically the source-of-truth and contract foundation required before quarantine/provider work begins.

### Dependencies

- current Prisma schema and migration history;
- `module-architecture.md` lifecycle rulings;
- root validation/error conventions;
- SH-015 decision-result contract if implemented/approved for shared result envelopes;
- SH-080 versioned-rule mechanism;
- SH-123 target-validation contract shape for later contextual calls.

### In Scope

- define public DTOs and stable reason-code enums for Media commands/queries;
- define `MediaReadinessResult` and `MediaUploadStatusResult`;
- define application repository boundaries for Media-owned models only;
- define transition policies for `MediaAsset`, validation, scan, processing, grant, and policy states;
- implement or migrate to version-safe `MediaUploadPolicy` behavior consistent with SH-080;
- prepare the R010-required dedicated upload-session status representation for later schema review; until the approved migration, isolate legacy session-state storage behind Media-owned typed mapping and record the migration prerequisite;
- verify and document existing indexes/constraints instead of recreating schema blindly;
- define owner/provider ports without provider SDK types.

### Out of Scope

- R2 SDK integration;
- byte upload;
- file scanning or processing;
- contextual attachment creation;
- signed file access;
- search, notification, privacy, or moderation effects;
- production scanner selection.

### Module-Owned Data

- `MediaUploadPolicy` / `MediaUploadPolicyStatus`;
- `MediaUploadSession` and, if approved, dedicated upload-session status enum;
- `MediaAsset` / `MediaAssetStatus` transition policy only;
- validation/scan/processing/grant/event model repository contracts without operational behavior yet.

### Public Interfaces

Introduce stable types/contracts for:

- `createMediaUploadSession`;
- `completeMediaUpload`;
- `getMediaReadiness`;
- `getMediaUploadStatus`;
- `getMediaAssetMetadata`;
- `getActiveMediaUploadPolicy`;
- `canMediaAssetBeAttached`;
- `requestMediaAccess` and `revokeMediaAccessGrant` signatures for later features;
- `ObjectStoragePort`, `MalwareScannerPort`, `MediaProcessorPort`.

No interface may return a provider-native object or raw object-storage secret.

### Shared Operations Used

#### SH-080 — `manageVersionedRules`

- **Owner:** each policy Module using the shared versioning mechanism.
- **Invocation:** upload-policy creation/activation/retirement.
- **Local policy:** Media owns which upload rules exist for each `MediaUploadContext`, their fields, and when one becomes applicable.
- **Prohibited duplicate:** `mediaPolicyVersioner.ts`, mutable active-policy overwrites, ad hoc “current policy” booleans.

#### SH-053 — `transitionLifecycleState`

- **Owner:** shared state-machine mechanism; Media supplies lifecycle policy.
- **Invocation:** all Media-owned transitions defined in this feature and executed in later features.
- **Local policy:** valid MediaAsset/session/grant transition graphs and invariants.
- **Prohibited duplicate:** generic `mediaStateMachineFramework.ts` that becomes a second platform lifecycle engine.

#### SH-015 — `returnDecisionResult`

- **Owner:** shared contract; policy owner varies. **Status: Proposed ruling.**
- **Invocation:** stable readiness/access decision results if available.
- **Local policy:** Media reason codes and evidence references.
- **Prohibited duplicate:** bespoke untyped `{ ok, error }` shapes that force consumers to parse strings.

### Domain Logic

- activated upload-policy versions are immutable historical evidence;
- a new policy change creates a new version/effective record rather than editing the rules that governed an existing upload;
- exactly one applicable active/effective policy may be selected for a `MediaUploadContext` at a point in time;
- MediaAsset transition validation is owner-local and cannot be bypassed by repository callers;
- upload-session lifecycle must describe an upload attempt, not pretend that the session itself is the asset;
- readiness results distinguish `pending`, `ready`, `rejected`, `failed`, `frozen`, `deleted/erased`, and policy/security denial states without exposing storage implementation details.

### Authorization / Compliance

No protected mutation is exposed directly in this feature; the contracts must nevertheless require actor/system context where future execution will require it. Policy administration must be designed for SH-001/002 enforcement rather than frontend role checks.

The schema review must preserve the compliance meanings of:

- validation proof;
- scan proof;
- processing proof;
- short-lived access proof;
- product deletion versus privacy erasure.

### Database / Transaction Behavior

- inspect existing migration constraints and do not infer that Prisma declarations alone are deployed;
- `MediaAsset.storageKey` uniqueness must be database-enforced;
- policy activation/versioning must be atomic so two “current” policies cannot race into an ambiguous state;
- if a new policy-version field/table or `MediaUploadSessionStatus` is introduced, migration must be additive/backfillable and preserve existing rows;
- no destructive cascade change is made without explicit migration review and test coverage.

### Events / Jobs

No production event or worker is required. Define only event contract names/envelopes needed later; do not publish empty placeholder events.

### Provider Integration

None. Provider ports are interface-only in this feature.

### UI / Admin Surface

No user UI required. A developer test harness or existing admin/debug surface may display policy/version/readiness data, but this feature must not invent a new admin product surface.

### Failure Behavior

- ambiguous active policy: fail closed with `media_policy_ambiguous`;
- missing active policy: `media_policy_not_found`;
- stale policy mutation attempt: conflict;
- invalid lifecycle transition: stable conflict/invalid-state result;
- unapproved Proposed Ruling needed for schema commitment: stop migration work, preserve interface isolation, record architecture block.

### Tests

- policy-version selection by context/effective time;
- attempt to mutate activated historical policy is rejected;
- concurrent activation cannot create two effective policies for same context/time;
- exhaustive MediaAsset transition matrix;
- upload-session transition matrix for the approved model;
- readiness result contract snapshots;
- repository boundary test proving no foreign-domain repository import is required;
- migration-from-clean and migration-on-seeded-data tests for any schema change.

### Documentation Updates

- preserve the R009 immutable policy-version and R010 separate session-status requirements; document the later approved schema/migration design without reopening those requirements;
- record migration decision in project ADR/progress tracker if the repository uses ADRs;
- do not modify CL-05 sequence.

### Acceptance Criteria

- typed public contracts exist and compile independently of provider SDKs;
- policy history cannot be silently rewritten;
- lifecycle transitions are centralized in Media policy code;
- session lifecycle is either safely separated from MediaAsset lifecycle or explicitly isolated behind an unresolved migration boundary;
- no contextual join ownership is absorbed into Media.

### Exit Gate

Before Feature 02 starts:

- typecheck/lint/unit tests pass;
- migration tests pass if schema changed;
- policy selection/versioning tests pass;
- lifecycle transition tests pass;
- the public contract layer contains no provider-native types and no direct foreign-domain Prisma repository dependencies;
- any unresolved migration ruling is explicitly recorded rather than silently decided.

---

## 02 Quarantine Upload Intake and R2 Object Storage

### Objective

Implement the authoritative upload-session creation, opaque object-key generation, private/quarantine storage handoff, and upload-completion claim that precede file validation.

### Observable Result

An authorized test actor can request an upload for a supported `MediaUploadContext`, receive a bounded presigned upload instruction for private/quarantine storage, upload an object, and complete the upload into a Media-owned quarantined state without the object being considered safe or ready.

### Cluster Build-Plan Link

Implements the intake/storage portion of **CL-05 Feature 01 — Secure Upload to Ready MediaAsset**.

### Dependencies

- Feature 01;
- SH-001 and SH-002 implementations or approved fakes;
- SH-011 where the chosen upload action is hold-sensitive;
- SH-044 idempotency;
- SH-085 object-key generation;
- SH-123 target validation for contextual upload contexts;
- R2 credentials in server-only secret management;
- R2-compatible `ObjectStoragePort` test adapter and production adapter.

### In Scope

- `createMediaUploadSession` command implementation;
- early request validation for filename, declared type, declared size, context, target reference, and actor;
- select effective `MediaUploadPolicy`;
- generate opaque object/storage key;
- create session and safe upload instruction;
- R2 S3-compatible presigned upload through `ObjectStoragePort`;
- `completeMediaUpload` command to confirm provider object existence/metadata;
- create/link `MediaAsset` in quarantined/non-ready state according to approved lifecycle;
- enqueue downstream processing rather than performing full scan/process in request path;
- abandoned upload cleanup eligibility metadata.

### Out of Scope

- final MIME/signature validation;
- malware scan;
- EXIF/PDF processing;
- `MediaAsset.ready` transition;
- contextual join creation;
- signed read/download URLs;
- public derivative exposure.

### Module-Owned Data

- `MediaUploadSession`;
- initial/quarantined `MediaAsset`;
- selected `MediaUploadPolicy` reference/version evidence;
- storage metadata needed to locate the private object.

### Public Interfaces

Implement:

- `createMediaUploadSession(input, actorContext)`;
- `completeMediaUpload(input, actorOrSystemContext)`;
- `getMediaUploadStatus(sessionId, actorContext)`.

Implement provider interface:

- `ObjectStoragePort.createPresignedUpload`;
- `ObjectStoragePort.headObject`;
- `ObjectStoragePort.copyOrMoveObject` only if required by quarantine design;
- `ObjectStoragePort.deleteObject` contract for later cleanup/privacy features.

### Shared Operations Used

#### SH-001 — `resolveAuthenticatedActor`

- **Owner:** Identity & Access.
- **Invocation:** before session creation or user-triggered completion.
- **Local policy:** Media interprets requested upload context; Identity only establishes actor truth.
- **Prohibited duplicate:** `mediaAuth.ts`, `getCurrentMediaUser.ts`.

#### SH-002 — `authorizeResourceAction`

- **Owner:** Role / Authority.
- **Invocation:** before protected upload/session actions.
- **Local policy:** Media supplies the action vocabulary and minimum owner/context facts.
- **Prohibited duplicate:** `canUploadMedia.ts` as a generic authority engine.

#### SH-011 — `evaluateComplianceHold`

- **Owner:** Admin Review / Compliance Hold.
- **Invocation:** before hold-sensitive upload or processing initiation.
- **Local policy:** Media maps an applicable hold to upload denial or processing prevention.
- **Prohibited duplicate:** `MediaAsset.isBlocked`, `mediaHoldService.ts`.

#### SH-044 — `executeIdempotentCommand`

- **Owner:** platform application infrastructure.
- **Invocation:** session creation/completion where clients or workers may retry.
- **Local policy:** semantic command key combines actor/context/target/upload intent as specified by Media.
- **Prohibited duplicate:** `mediaIdempotencyTable`, in-memory request dedupe.

#### SH-080 — `manageVersionedRules`

- **Owner:** shared versioning mechanism; Media owns rule meaning.
- **Invocation:** select exact policy version/effective rules governing upload.
- **Local policy:** upload context mapping and rule fields.
- **Prohibited duplicate:** copying policy fields into frontend constants as current truth.

#### SH-085 — `generatePrivateObjectKey`

- **Owner:** Media / File Access / storage primitive.
- **Invocation:** before upload instruction is created.
- **Local policy:** bucket class/path partition and object-purpose semantics.
- **Prohibited duplicate:** original-filename path generation, `safeFilenameAsKey.ts`.

#### SH-123 — `validateOwnedTargetReference`

- **Owner:** contextual target owner through shared contract.
- **Invocation:** when upload context references an Offering, JobApplication, Message, Order, etc.
- **Local policy:** Media only confirms target reference validity/allowed upload context; contextual owner retains business semantics.
- **Prohibited duplicate:** direct foreign Prisma lookup repositories inside Media.

#### SH-032 / SH-034 / SH-037

- **Owners:** Observability / Ops.
- **Invocation:** all provider operations and failures.
- **Local policy:** Media supplies safe object/session IDs and normalized operation names.
- **Prohibited duplicate:** raw SDK payload logging, `mediaIntegrationFailures` table.

### Domain Logic

1. Resolve actor.
2. Validate command input.
3. Validate contextual target through owner contract when needed.
4. Authorize resource action.
5. Evaluate applicable hold.
6. Select exact upload-policy version.
7. Apply early declared-size/extension checks only as fast rejection; they do not prove file safety.
8. Generate opaque key and private/quarantine storage target.
9. Persist upload session before returning a presigned instruction.
10. On completion, use provider `headObject`/equivalent to confirm object exists and collect normalized metadata.
11. Reject obvious size/provider mismatch according to policy.
12. Create/link quarantined MediaAsset and enqueue the validation pipeline.
13. Never mark the asset ready in the request path.

### Authorization / Compliance

- server authorization is required even if the client hides upload controls;
- sensitive contexts map to sensitive/healthcare/legal/private bucket classes according to policy;
- raw storage key is server-side metadata and must not be exposed to unauthorized clients;
- original filenames may be retained only as minimized metadata needed for UX/compliance and are never storage identity;
- R2 object is private/quarantined by default.

### Database / Transaction Behavior

- session creation and semantic idempotency claim occur atomically;
- selected policy version/reference is persisted with the session so later workers evaluate the same rules;
- completion creates or links exactly one semantic MediaAsset per completed upload session;
- duplicate completion replays prior result and must not create duplicate assets or queue fan-out;
- `storageKey` uniqueness is enforced by database constraint;
- queue/outbox enqueue should be transactionally coupled to completion state if the root queue/outbox architecture permits.

### Events / Jobs

- enqueue `media.validate-upload` (logical name; final job naming follows code standards) through SH-047 after successful completion;
- abandoned-session expiration/cleanup can be scheduled once session expiry policy exists;
- no `media.asset.ready` event yet.

### Provider Integration

**Port:** `ObjectStoragePort`  
**Production adapter:** Cloudflare R2 via S3-compatible SDK.  
**Credentials:** server-only environment/secret manager.  
**Webhook:** none required for the current R2 upload design. Do not invent provider-event dedupe.  
**Status translation:** normalize upload/presign/head/delete errors into Media provider error categories.  
**Idempotency:** stable object/session keys; provider request IDs where supported.  
**Privacy deletion:** implemented through the same port later, not a second R2 client.

### UI / Admin Surface

No full product upload UI is required. A reusable upload control or existing developer/admin test surface may exercise the public contract and display `created/uploading/quarantined/failed` state. Marketplace, Candidate, Messaging, and other contextual UIs remain outside this Module plan.

### Failure Behavior

- unauthorized target/action: deny before presign;
- missing policy: fail closed;
- hold blocks action: no session/provider instruction;
- provider presign failure: no false “uploaded” state; record IntegrationFailure;
- object missing at completion: retryable provider lookup according to policy, then failed session if exhausted;
- oversized object discovered after upload: reject/quarantine and proceed to cleanup policy; never ready;
- duplicate completion: replay original result;
- abandoned session: eventually expire/cleanup, not silently become failed asset truth.

### Tests

- command validation for every supported upload context category;
- actor/authority allow and deny;
- contextual target fake allow/deny;
- object key path traversal/original filename attack;
- presign scope/TTL/bucket tests;
- R2 adapter contract tests using test store/emulator/fake;
- storage key uniqueness;
- duplicate session creation/completion idempotency;
- object missing/provider timeout classification;
- private/quarantine object cannot be anonymously fetched;
- telemetry log-scrape proves no signed URL, secret, or raw sensitive payload is logged.

### Documentation Updates

- record actual R2 adapter package/configuration in library/provider docs if not already present;
- update Module architecture only if object-storage or policy-version contract changes;
- update progress tracker with Feature 02 gate result.

### Acceptance Criteria

- an authorized actor obtains only a bounded upload instruction;
- storage identity is opaque and independent of original filename;
- completed uploads become quarantined/non-ready Media state;
- no provider result can directly mark the file ready;
- repeated completion creates one semantic asset and one downstream processing intent;
- no contextual Module repository was imported to validate target ownership.

### Exit Gate

Before Feature 03 starts:

- an end-to-end test uploads a fixture to the test/R2 adapter and observes a quarantined MediaAsset;
- unauthorized/contextually invalid uploads never receive usable presigned instructions;
- original filename is not the object key;
- private/quarantine object access is not anonymous;
- duplicate completion is idempotent;
- queue request exists for the processing pipeline;
- provider failures are normalized and observable;
- typecheck/lint/unit/integration/security tests pass.

---
# Phase 2 — File Safety Pipeline and Ready Media Truth

This phase completes CL-05 Feature 01. It turns quarantined bytes into explicit validation, scan, processing, derivative, and readiness proof.

## 03 File Validation, Checksum, Malware Scan, and Processing Pipeline

### Objective

Execute the policy-driven security pipeline against exact uploaded bytes and persist explicit proof for validation, scanning, and required transformations without allowing any failed or unresolved required step to become ready.

### Observable Result

A quarantined upload proceeds through observable validation, scan, and processing states. Safe fixtures produce passed/clean/processed proof. Invalid, infected, forbidden, or unprocessable fixtures produce stable rejection/failure evidence and remain non-ready.

### Cluster Build-Plan Link

Implements the security-processing core of **CL-05 Feature 01 — Secure Upload to Ready MediaAsset**.

### Dependencies

- Features 01–02;
- SH-047 durable jobs and SH-048 retry/backoff;
- SH-082 validation;
- SH-083 malware scan;
- SH-084 metadata scrub;
- SH-086 checksum;
- `file-type` or approved binary-signature detector;
- `sharp` for supported image transformations;
- `MalwareScannerPort` test adapter; production adapter may remain unresolved until hardening;
- `MediaProcessorPort` implementations for approved actions.

### In Scope

- validation worker/service;
- server-side actual-byte size verification;
- detected MIME/extension/binary signature inspection;
- archive/encryption/password-protected rules when determinable;
- checksum calculation;
- malware scanner invocation when required;
- scan result normalization;
- EXIF/GPS scrub for policy-required images;
- PDF metadata scrub only if a proven processor is available under current library standards; otherwise keep the action unsupported/failing closed rather than inventing it;
- image resize/compress/thumbnail actions where policy requires;
- `MediaValidationResult`, `MediaScanResult`, and `MediaProcessingResult` persistence;
- MediaAsset/session aggregate status updates to reflect work in progress or terminal rejection/failure;
- retry classification and operational failure reporting.

### Out of Scope

- `ready` promotion until Feature 04 composes all required proof;
- contextual attachment;
- signed read/download access;
- moderation/legal content analysis;
- professional/license verification;
- AI content classification;
- production malware-provider selection if not yet approved.

### Module-Owned Data

- `MediaValidationResult` / `MediaValidationStatus`;
- `MediaScanResult` / `MediaScanStatus`;
- `MediaProcessingResult` / `MediaProcessingStatus` / `MediaProcessingActionType`;
- `MediaAsset.validationStatus`, `scanStatus`, `processingStatus`, detection metadata, checksum, rejection fields, scrub timestamps;
- upload-session processing state.

### Public Interfaces

No broad new external public API is required. Complete internal owner services used by `completeMediaUpload`/workers:

- `validateMediaAsset`;
- `scanMediaAsset`;
- `processMediaAsset`;
- `recordMediaPipelineFailure`;
- `getMediaUploadStatus` reflects current proof states.

The canonical shared-operation names remain the architectural references even if internal function naming follows repository standards.

### Shared Operations Used

#### SH-082 — `validateUploadedFile`

- **Owner:** Media / File Access.
- **Invocation:** first worker stage after upload completion.
- **Local policy:** exact policy fields, context-specific MIME/extensions/size/archive/encryption rules, rejection mapping.
- **Prohibited duplicate:** `resumeFileValidator.ts`, `messageMimeValidator.ts`, `offeringUploadValidator.ts`, separate per-feature file validation services.

#### SH-083 — `scanFileForMalware`

- **Owner:** Media / File Access.
- **Invocation:** after binary validation when policy requires scanning.
- **Local policy:** whether scan is required, fail-closed behavior, suspicious/infected handling, accepted scanner result mapping.
- **Prohibited duplicate:** `virusScan.ts` in consumer Modules or “virusFree” booleans.

#### SH-084 — `scrubFileMetadata`

- **Owner:** Media / File Access.
- **Invocation:** after validation/scan, before cross-user/public exposure when policy requires processing.
- **Local policy:** required action list by upload context/policy and whether derivative replaces public-facing original.
- **Prohibited duplicate:** `stripExif.ts`, `removeGps.ts`, `sanitizeResumePdf.ts` in feature Modules.

#### SH-086 — `calculateChecksum`

- **Owner:** shared hash primitive consumed by Media.
- **Invocation:** original-byte integrity and processing input/output proof.
- **Local policy:** what Media checksum means; it does not become Agreement legal hash proof.
- **Prohibited duplicate:** local SHA-256 helpers or contract-hash logic in Media.

#### SH-047 — `enqueueReliableJob`

- **Owner:** shared queue infrastructure.
- **Invocation:** validation/scan/process stages and chained work.
- **Local policy:** payload contains only Media identifiers/policy version, stage, and safe correlation metadata.
- **Prohibited duplicate:** custom Media queue tables/runner.

#### SH-048 — `executeRetryWithBackoff`

- **Owner:** shared queue/platform infrastructure.
- **Invocation:** scanner/processor/storage transient failures.
- **Local policy:** Media classifies business rejection versus transient provider failure.
- **Prohibited duplicate:** ad hoc recursive retries or unbounded worker retry loops.

#### SH-053 — `transitionLifecycleState`

- **Owner:** shared mechanism; Media owns transition policy.
- **Invocation:** move asset/session between quarantined/validating/processing/rejected/failed stages.
- **Local policy:** Media lifecycle graph and terminal-state semantics.
- **Prohibited duplicate:** direct arbitrary `status` updates from workers.

#### SH-032 / SH-034 / SH-037

- **Owner:** Observability / Ops.
- **Invocation:** every worker/provider stage.
- **Local policy:** safe file/session identifiers and normalized error classifications.
- **Prohibited duplicate:** raw scanner payload logging or a Media-specific integration-failure ledger.

### Domain Logic

1. Lock or otherwise protect the MediaAsset/session aggregate against duplicate stage execution.
2. Read the exact persisted policy version that governed the upload.
3. Fetch/stream exact quarantined bytes through `ObjectStoragePort`; do not trust browser-declared metadata.
4. Calculate authoritative size/checksum.
5. Detect file type/signature and compare declared/allowed values.
6. Reject prohibited archive/encryption/password-protected cases according to policy.
7. Persist one validation result for the attempt/stage with normalized evidence.
8. If required validation fails, mark asset/session rejected with `MediaRejectionReason`; do not scan/process as if safe unless security cleanup policy requires it.
9. If scan is required, invoke scanner through `MalwareScannerPort`.
10. `infected` is a business/security rejection, not a retryable technical failure.
11. `suspicious` follows explicit local policy; if no approved auto-safe interpretation exists, fail closed and retain quarantined/non-ready state for review/cleanup.
12. Scanner unavailable/error is retryable only according to configured technical policy. Required scanning never becomes `skipped` merely because the provider is unavailable.
13. Execute required processing actions and persist one result per action.
14. Metadata scrub failure for a required action prevents readiness.
15. Never conflate clean scan with content moderation, professional verification, or business entitlement.

### Authorization / Compliance

Worker execution uses trusted system actor/request context, not user privilege escalation. Upload authorization was established at intake, but processing must still honor an authoritative freeze/hold instruction if the architecture requires processing to stop.

Compliance proof must establish:

- hard size enforcement;
- binary MIME/signature inspection;
- scan result where required;
- filename/storage-key separation;
- metadata/GPS scrub where required;
- quarantine until readiness composition succeeds.

### Database / Transaction Behavior

- each stage claims work idempotently so duplicate jobs do not duplicate proof/effects;
- result insertion and aggregate stage/status update occur in one transaction where practical;
- duplicate stage completion returns existing result for same semantic attempt/version;
- proof rows should be append-oriented; correction creates a new result/re-run rather than mutating historical scan outcome without trace;
- reject/fail transitions must guard against stale workers overwriting a later frozen/deleted/erased state;
- use row/version locking or SH-052 compare-and-set where concurrent workers can race.

### Events / Jobs

Recommended durable stages:

```text
validate-upload
→ scan-upload (when required)
→ process-upload (when required)
→ evaluate-media-promotion
```

Job names are logical; code naming follows root standards.

- each job has stable idempotency key based on session/asset/stage/policy version or processing action;
- retry technical failures only;
- terminal technical failure records Media-owned failed state plus SH-037 IntegrationFailure;
- dead-letter remains Ops state and does not replace Media failure truth.

### Provider Integration

**Binary validation:** local library through Media validator, no provider truth.  
**Image processing:** `sharp` behind `MediaProcessorPort` or a narrow local processor implementation.  
**Malware:** provider-neutral `MalwareScannerPort`; production provider unresolved.  
**Credentials:** scanner secrets remain server-only.  
**Webhook:** not required unless the selected scanner later requires asynchronous callbacks. Do not create `ProcessedMediaProviderEvent` in advance.  
**Translation:** provider statuses/errors normalize to `MediaScanStatus` plus retryability; unknown success-like states fail closed.

### UI / Admin Surface

No user UI required. Existing upload status UI/test harness may display safe states such as validating, scanning, processing, rejected, failed. Do not expose threat signatures, scanner payloads, raw filenames, or sensitive metadata to ordinary users.

### Failure Behavior

- MIME/signature mismatch: `rejected`, non-retryable;
- oversized file: `rejected`, non-retryable;
- forbidden encrypted/password file: `rejected`, non-retryable;
- malware infected: `rejected`, non-retryable, quarantine/cleanup according to policy;
- suspicious with no approved auto-safe policy: fail closed/quarantine;
- scanner unavailable: retry; after exhaustion remain non-ready/failed and record IntegrationFailure;
- processor timeout: retry bounded; terminal failure remains non-ready;
- stale worker after deletion/freeze: no resurrection; return stale/no-op conflict;
- unexpected provider status: fail closed and record normalized failure.

### Tests

- full allowed/denied MIME-extension-signature matrix;
- oversized and truncated binary fixtures;
- archive/encryption/password-protected fixtures where detection supported;
- checksum deterministic tests;
- infected/suspicious/clean scanner adapter contracts;
- required scanner unavailable never produces ready/skipped-success;
- EXIF GPS fixture proves removal;
- image derivative processing tests;
- required processing failure prevents promotion;
- duplicate/replayed jobs create no duplicate semantic effects;
- stale-worker concurrency tests;
- telemetry sanitization and no raw scanner payload test;
- worker dead-letter records Ops failure while Media truth remains explicit.

### Documentation Updates

- if production scanner is selected during this feature, record adapter/provider decision in Module architecture and library docs;
- if PDF metadata scrub is unavailable for MVP contexts, document which active policies may safely omit it rather than silently marking it skipped;
- update progress tracker.

### Acceptance Criteria

- every required technical safety gate has explicit proof;
- browser-declared MIME/extension cannot override detected binary truth;
- infected/invalid files cannot reach ready;
- scanner/processor outages cannot be mistaken for safe outcomes;
- no contextual business logic appears in validation/scanner code;
- retries are idempotent and stale jobs cannot resurrect terminal assets.

### Exit Gate

Before Feature 04 starts:

- test fixtures cover clean, mismatch, oversized, infected, suspicious, scanner-error, scrub-success, and scrub-failure paths;
- all required proof rows and aggregate statuses are correct;
- no required failed/skipped stage can be interpreted as ready;
- worker retries/dead-letter behavior is observable;
- security/privacy log-scrape tests pass;
- typecheck/lint/unit/integration/worker tests pass.

---

## 04 Promotion to Ready, Processed Derivatives, and Readiness Queries

### Objective

Compose the completed safety proof into the one authoritative `MediaAsset.ready` decision, create approved processed derivatives, and expose stable readiness/metadata queries that downstream Modules can consume without direct Prisma reads.

### Observable Result

A safe upload transitions exactly once to `MediaAsset.ready`; required public-safe or thumbnail derivatives are related to their source asset; consumers can query readiness and safe metadata without learning provider object details or reinterpreting scan/processing tables themselves.

### Cluster Build-Plan Link

Completes **CL-05 Feature 01 — Secure Upload to Ready MediaAsset** and establishes the Media dependency used by later CL-05 Features 04–06 and cross-Cluster resume/message/verification workflows.

### Dependencies

- Features 01–03;
- all required validation/scan/processing proof;
- SH-046 transactional outbox if ready/rejected events have consumers;
- SH-051/052 concurrency control;
- SH-053 transition lifecycle;
- SH-090 contextual attach contract;
- object storage copy/move and processed derivative support.

### In Scope

- deterministic readiness composition policy;
- `promoteMediaAssetToReady` internal owner operation;
- move/copy from quarantine to approved private/processed storage if storage topology requires it;
- create/process derivative `MediaAsset` records with `sourceMediaAssetId` relationships;
- enforce storage visibility/bucket class rules;
- implement `getMediaReadiness`, `getMediaAssetMetadata`, `getMediaUploadStatus`, `getActiveMediaUploadPolicy`, and `canMediaAssetBeAttached`;
- emit finalized Media asset lifecycle events only where a downstream contract exists;
- safe rejection/failure query responses;
- attachment readiness contract used by SH-090 without Media creating contextual joins.

### Out of Scope

- creating `OfferingMedia`, `MessageMedia`, `JobApplicationMedia`, `OrderFile`, or other contextual joins;
- purchase entitlement;
- signed private access;
- Search indexing;
- content moderation decisioning.

### Module-Owned Data

- final `MediaAsset.status`, readiness timestamps, storage visibility/bucket class, checksum/detected metadata;
- derivative `MediaAsset` rows and processing link evidence;
- no contextual attachment truth.

### Public Interfaces

Implement/stabilize:

- `getMediaReadiness(mediaAssetId)`;
- `getMediaAssetMetadata(mediaAssetId, callerContext)`;
- `getMediaUploadStatus(uploadSessionId)`;
- `getActiveMediaUploadPolicy(context)`;
- `canMediaAssetBeAttached(mediaAssetId, attachmentPurpose)`;
- Media side of SH-090 `attachValidatedMedia` contract: return readiness/evidence; contextual owner performs its own association mutation.

### Shared Operations Used

#### SH-051 — `acquireAggregateLock`

- **Owner:** shared persistence infrastructure.
- **Invocation:** promotion when concurrent/replayed workers could act on the same asset.
- **Local policy:** MediaAsset is the lock resource and determines conflicting transitions.
- **Prohibited duplicate:** in-memory asset mutexes.

#### SH-052 — `withOptimisticConcurrency`

- **Owner:** shared persistence infrastructure.
- **Invocation:** queries/commands that compare current aggregate version or updatedAt where root conventions use optimistic concurrency.
- **Local policy:** stale promotion/rejection behavior.
- **Prohibited duplicate:** silent last-write-wins on terminal state.

#### SH-053 — `transitionLifecycleState`

- **Owner:** shared mechanism; Media supplies policy.
- **Invocation:** `processing/quarantined → ready`, rejection/failure finalization, derivative transitions.
- **Local policy:** all readiness invariants.
- **Prohibited duplicate:** direct status assignment from adapter code.

#### SH-046 — `publishDomainEvent`

- **Owner:** platform event/outbox infrastructure.
- **Invocation:** transactionally after ready/rejected/failed/frozen facts when real consumers are registered.
- **Local policy:** Media event names, minimal payload, aggregate/version, emission condition.
- **Prohibited duplicate:** provider callback directly invoking consumer Modules or fire-and-forget events before commit.

#### SH-090 — `attachValidatedMedia`

- **Owner:** contextual domain Module; Media owns asset truth.
- **Invocation:** downstream owner requests proof that asset may be attached.
- **Local policy:** Media returns technical attachability/readiness only.
- **Prohibited duplicate:** `attachMediaToAnything()` generic repository or Media mutation of foreign join rows as business truth.

#### SH-125 — `recordDomainAccessEvent`

- **Owner:** each domain using shared append mechanism.
- **Invocation:** not required for simple metadata query; reserved for domain access events in later access feature.
- **Local policy:** MediaAccessEvent semantics remain Media-owned.
- **Prohibited duplicate:** using AuditEvent to represent Media lifecycle/access history.

### Domain Logic

Promotion decision requires, for the governing policy version:

- object exists in expected storage class;
- validation is `passed` when required;
- scan is `clean` when required;
- every required processing action is `processed`;
- checksums/integrity evidence are present as required;
- no rejection reason exists;
- asset is not frozen/deleted/erased;
- no applicable current instruction blocks promotion.

Public/private rules:

- default ready asset may remain private even when technically ready;
- `ready` means safe for the permitted context, not public or entitled;
- raw originals are not exposed publicly by default;
- public-facing image use should reference `public_processed` derivative when policy permits;
- `publicUrl` may exist only for intentionally public processed assets under approved policy and must never be the generic private-file access mechanism.

### Authorization / Compliance

Metadata/readiness queries must apply SH-001/002 or trusted internal caller policy according to root route/interface classification. Public consumer contracts return only data necessary for downstream decisions.

A contextual owner must not infer credential/trust/moderation approval from Media readiness. `ready` proves the file pipeline, not the business workflow.

### Database / Transaction Behavior

- promotion uses a lock/compare-and-set so one worker owns the transition;
- promotion status update and outbox event are one transaction when an event is required;
- derivative creation is idempotent by semantic source/action/policy key so retries do not multiply thumbnails/public derivatives;
- source/derivative relationship integrity must be enforced;
- moving provider storage before database commit requires compensation/reconciliation design; prefer a workflow where the database can safely retry or reconcile provider movement;
- queries do not mutate readiness.

### Events / Jobs

Define and publish only when consumers exist:

- `media.asset.ready`;
- `media.asset.rejected`;
- `media.asset.failed`.

Minimal event payload:

- event ID/version;
- mediaAssetId;
- uploadContext;
- status;
- source version/updatedAt;
- safe reason code when applicable;
- correlation/causation IDs.

Do not emit original filename, object key, signed URL, threat payload, or sensitive content.

### Provider Integration

- use `ObjectStoragePort` for quarantine-to-ready movement/copy and derivative persistence;
- use processor output already created through Feature 03;
- provider state is reconciled to Media source truth; R2 object metadata does not become readiness truth.

### UI / Admin Surface

Existing upload/test surfaces may display ready/rejected/failed and derivative availability. No new product UI required.

### Failure Behavior

- missing required proof: remain non-ready and return `media_pipeline_incomplete`;
- provider move/copy failure: retry; do not set ready if the authoritative storage location is unavailable;
- duplicate promotion: replay ready result;
- stale promotion after freeze/delete/erase: denied/no-op, never resurrect;
- derivative failure when derivative is required: source may remain non-public/non-ready for that policy; do not expose raw original as fallback unless explicitly permitted;
- event publication failure after transaction: outbox retries without reversing ready truth.

### Tests

- readiness composition matrix across optional/required validation/scan/process rules;
- promotion race with duplicate workers;
- freeze/delete versus promotion race;
- derivative idempotency;
- public processed derivative versus raw original rule;
- query contract tests for safe metadata and reason codes;
- downstream SH-090 fake proves contextual Module can attach only a technically attachable asset without direct Media table reads;
- outbox atomicity/replay test;
- R2 move/copy retry/reconciliation test.

### Documentation Updates

- register final Media event names/payload versions in Module architecture once implemented;
- update shared-operation registry only if an actual canonical contract changes, not for local code naming;
- update progress tracker and CL-05 Feature 01 evidence.

### Acceptance Criteria

- only complete policy-required proof can produce `MediaAsset.ready`;
- readiness is not public visibility or business entitlement;
- processed derivatives are linked and retry-safe;
- contextual owners can consume readiness through a stable public contract;
- Media does not create or own contextual join semantics;
- ready/rejected/failed events, if enabled, are transactionally reliable and payload-minimized.

### Exit Gate

CL-05 Feature 01 is complete for Media only when:

- safe fixture upload reaches `MediaAsset.ready` with complete proof;
- invalid/infected/required-processing-failure fixture never becomes ready;
- public derivative tests prove raw-original fallback is not automatic;
- downstream attachability contract works without direct Prisma access;
- duplicate/stale promotion cannot produce inconsistent state;
- outbox/provider reconciliation tests pass;
- all Feature 01 unit/integration/security/E2E tests pass.

---
# Phase 3 — Contextual Access and Short-Lived Delivery

This phase implements CL-05 Feature 02. It proves that Media can expose a private asset without becoming the owner of the business reason for access.

## 05 Contextual Media Access Grant and Signed Delivery

### Objective

Issue a bounded `MediaAccessGrant` and short-lived signed object URL only after an authenticated actor, Role / Authority, contextual owner, ComplianceHold, healthcare policy where applicable, and Media local readiness all permit the requested action.

### Observable Result

A contextual test owner can supply an allow/deny decision for a private MediaAsset. An allowed request receives a bounded access result with explicit expiry; a denied/unsafe request receives a stable reason and no usable object credential. `MediaAccessGrant` and `MediaAccessEvent` preserve Media technical access evidence, while `AccessAuditLog` separately records sensitive access when required.

### Cluster Build-Plan Link

Implements the primary path of **CL-05 Feature 02 — Contextual Media Access and Short-Lived Signed Delivery**.

### Dependencies

- Features 01–04;
- SH-001 authenticated actor;
- SH-002 authority;
- at least one owner implementation/fake of SH-026 contextual resource access;
- SH-011 ComplianceHold;
- SH-020 Healthcare readiness for healthcare-sensitive fixtures;
- SH-030 sensitive-access audit;
- SH-074 secure token generation where token-bound grant proof is used;
- SH-087 signed URL;
- SH-088 grant mechanics;
- SH-125 Media domain access event;
- R2 object-storage adapter.

### In Scope

- `requestMediaAccess` public command/application service;
- contextual access-decision validation;
- local Media access policy;
- grant creation/denial evidence;
- short-lived R2 signed URL through Media only;
- signed URL hash/token hash persistence where used;
- `MediaAccessEvent` for issuance/denial/view/download or supported access semantics;
- `AccessAuditLog` request for policy-required sensitive actions;
- stable denial/result codes;
- default sensitive TTL target of 15 minutes unless approved policy/context requires a shorter bounded value.

### Out of Scope

- deciding whether an Order is paid;
- deciding whether a recruiter may view a resume;
- Thread/message participant policy;
- Agreement access rules/hash verification;
- DigitalDownloadGrant or CourseVideoPlaybackGrant;
- permanent public/private URLs;
- business download-count policy.

### Module-Owned Data

- `MediaAccessGrant` / `MediaAccessGrantStatus`;
- `MediaAccessEvent` / `MediaAccessEventType`;
- MediaAsset local access fields/state;
- token/signed-URL hashes and request metadata permitted by privacy policy.

### Public Interfaces

Implement:

- `requestMediaAccess({ mediaAssetId, action, contextDecision, requestedTtl?, idempotencyKey }, actor)`;
- internal `issueSignedMediaUrlForGrant(grantId)` as SH-087 implementation;
- `getMediaAccessGrant` for authorized support/debug or owner workflows if required;
- safe access result shape with `allowed`, reason code, expiry, grant reference, and credential only in the immediate authorized response.

Consumers must not infer business entitlement from `MediaAccessGrant.status` alone.

For MessageMedia access, Messaging exposes its owner-specific SH-026 `authorizeContextualResourceAccess` decision bound to the actor, Thread, Message, MediaAsset, and requested action. It returns the contextual allow/deny decision and safe evidence; `ThreadParticipant` or `MessageMedia` facts alone are not authorization. Media consumes that decision through `requestMediaAccess`, independently applies MediaAsset readiness, safety/freeze/erasure, grant, and TTL rules, and owns downstream SH-087 `issueSignedMediaUrl`. Media must not reconstruct Messaging participant/access policy; Messaging must not issue signed URLs or call SH-087 directly.

### Shared Operations Used

#### SH-001 — `resolveAuthenticatedActor`

- **Owner:** Identity & Access.
- **Invocation:** start of user access request.
- **Local policy:** none beyond requiring actor for the requested Media action.
- **Prohibited duplicate:** `mediaCurrentUser.ts`.

#### SH-002 — `authorizeResourceAction`

- **Owner:** Role / Authority.
- **Invocation:** before granting Media-level file action.
- **Local policy:** Media provides asset/resource facts and action vocabulary; Role / Authority interprets scope.
- **Prohibited duplicate:** generic `canDownloadFile()` authority engine.

#### SH-026 — `authorizeContextualResourceAccess`

- **Owner:** relevant context owner.
- **Invocation:** mandatory before Media issues contextual private access.
- **Local policy:** Media validates the decision's target/action binding and then applies file readiness/technical policy.
- **Prohibited duplicate:** Order/resume/message/Agreement/digital-goods entitlement reconstruction inside Media.

#### SH-011 — `evaluateComplianceHold`

- **Owner:** Admin Review / Compliance Hold.
- **Invocation:** after contextual eligibility, before grant issuance when action/target is hold-sensitive.
- **Local policy:** Media maps applicable hold to `access_blocked`/denial without creating local generic hold truth.
- **Prohibited duplicate:** `mediaBlocked`, `fileHold` table/boolean.

#### SH-020 — `evaluateHealthcareReadiness`

- **Owner:** Healthcare / Regulated Services.
- **Invocation:** healthcare-sensitive Media access.
- **Local policy:** Media enforces allow/redact/block/deny outcome as applicable to file exposure; it does not classify the user as healthcare-enabled.
- **Prohibited duplicate:** `hipaaFileGuard.ts` that recreates Healthcare policy.

#### SH-030 — `recordSensitiveAccess`

- **Owner:** Audit / Event Ledger.
- **Invocation:** allowed/denied sensitive file issuance/download actions according to audit policy.
- **Local policy:** Media supplies sensitivity, MediaAsset/grant reference, action, decision, and safe context.
- **Prohibited duplicate:** treating `MediaAccessEvent` as the platform sensitive audit ledger.

#### SH-074 — `generateSecureToken`

- **Owner:** shared security capability.
- **Invocation:** generate any bearer secret/token material required for a grant; persist hash only.
- **Local policy:** token purpose, binding, TTL.
- **Prohibited duplicate:** `crypto.randomBytes` helpers scattered inside access code when canonical primitive exists.

#### SH-087 — `issueSignedMediaUrl`

- **Owner:** Media / File Access.
- **Invocation:** after all gates and active grant validation.
- **Local policy:** action, storage headers, maximum TTL, object state, public/private restrictions.
- **Prohibited duplicate:** R2 presign calls in Digital Goods, Candidate, Messaging, Order, Marketplace, or Trust Verification.

#### SH-088 — `manageTemporaryAccessGrant`

- **Owner:** shared grant mechanism; each domain owns its record.
- **Invocation:** create/check/use MediaAccessGrant lifecycle.
- **Local policy:** MediaAccessGrant fields, validity, allowed action, expiry, revocation, current-use semantics.
- **Prohibited duplicate:** one universal `AccessGrant` table or custom Media-only generic grant framework.

#### SH-125 — `recordDomainAccessEvent`

- **Owner:** each domain using shared append mechanism.
- **Invocation:** append `MediaAccessEvent` after issuance/denial/view/download/revocation/expiry according to Media policy.
- **Local policy:** Media access-event vocabulary.
- **Prohibited duplicate:** writing generic AuditEvent instead of MediaAccessEvent.

#### SH-044 / SH-032 / SH-034 / SH-037

- **Invocation:** idempotent access issuance, correlation, redaction, provider signing failures.
- **Prohibited duplicate:** local idempotency store, unsafe access logs, raw R2 error leakage.

### Domain Logic

Access flow:

```text
actor
→ authority decision
→ contextual-owner decision bound to target/action
→ hold + healthcare gates when applicable
→ MediaAsset exists and is ready
→ not frozen/deleted/erased/revoked-public-only mismatch
→ storage visibility/action is compatible
→ grant created or validated
→ TTL bounded by Media policy/context
→ R2 signed URL generated server-side
→ URL hash/token hash evidence persisted
→ MediaAccessEvent appended
→ AccessAuditLog requested when sensitivity policy requires
→ credential returned only in current authorized response
```

Additional rules:

- a signed URL is a delivery credential, not entitlement truth;
- provider object key may be used server-side but is not returned as business metadata;
- `MediaStorageVisibility.private` requires signed delivery;
- `internal_only` must not become ordinary cross-user access;
- `public_processed` may be exposed only according to approved public policy and contextual/public-surface rules;
- `public_original` remains disabled by default for MVP;
- current evidence suggests 900 seconds / 15 minutes as default sensitive generic Media TTL. Do not hard-code a consumer-specific TTL outside Media policy.

### Authorization / Compliance

- user-triggered access requires SH-001/002;
- contextual owner decision is mandatory even if the caller possesses mediaAssetId;
- healthcare-sensitive files require Healthcare decision before payload exposure;
- admin/support authority does not automatically grant healthcare/resume/contract/private-message content access;
- sensitive allow and deny attempts are audited under SH-030 when policy requires;
- credentials are server-generated, short-lived, and omitted from logs/analytics.

### Database / Transaction Behavior

- idempotent grant issuance must not create multiple semantic active grants for the same idempotency request;
- grant creation and MediaAccessEvent issuance evidence should be transactionally consistent where the URL can be generated after commit; if URL generation fails, record provider error without falsely claiming successful issuance;
- if signing must occur before recording `signed_url_issued`, only append the success event after provider success;
- signed URL itself is not persisted; only hash/reference may be stored;
- validate `expiresAt` at request time even if expiration worker has not yet changed status;
- use compare-and-set/row lock where issuance races with revoke/delete/freeze.

### Events / Jobs

- append `MediaAccessEvent.signed_url_issued` or `signed_url_denied`;
- append `file_viewed` / `file_downloaded` only at the actual application-observable point supported by the delivery path; do not claim a completed download merely because a URL was issued;
- no generic integration event is required for every read;
- SH-030 audit may be synchronous or durable according to root audit guarantees, but access-sensitive proof must meet the root audit contract.

### Provider Integration

**Port:** `ObjectStoragePort.createPresignedRead`.  
**Provider:** Cloudflare R2.  
**Credentials:** server-only.  
**Webhook:** none.  
**Status/error translation:** normalize missing object, permission, rate-limit, timeout, and provider availability failures.  
**Reconciliation:** object-state reconciliation comes in Feature 09.  
**Privacy:** signed URL query/token material is never logged or persisted in plaintext.

### UI / Admin Surface

No standalone Media UI required. Consumer Modules render their own “view/download” affordances. Media may expose a safe developer/admin grant inspector under an existing authorized admin surface, showing status/reason/expiry but never raw bearer tokens or signed URLs.

### Failure Behavior

- unauthenticated/unauthorized: deny before provider call;
- contextual denial: no grant/URL;
- hold/healthcare denial: no grant/URL; record required evidence;
- asset pending/rejected/failed/frozen/deleted/erased: deny with stable Media reason;
- expired grant: deny based on server time even if status row still says active;
- R2 signing outage: return temporary delivery failure, record IntegrationFailure, do not append successful-issued event;
- object unexpectedly missing: provider failure/reconciliation signal, no URL;
- duplicate request with same idempotency key: replay semantic grant/result without multiplying business effects.

### Tests

- contract allow/deny with fake contextual owner;
- MessageMedia contract validates Messaging decision binding to actor/Thread/Message/MediaAsset/action; facts-only, denied, or unavailable decisions cannot issue a grant/URL;
- authority allow/deny;
- hold and healthcare allow/deny/redact/block paths as applicable;
- ready/non-ready/frozen/deleted/erased matrix;
- private/internal/public processed/public original policy tests;
- signed TTL bounded at policy maximum;
- signed URL never stored/logged plaintext;
- R2 presign adapter failure translation;
- grant issuance idempotency;
- freeze/revoke race during issuance;
- MediaAccessEvent and AccessAuditLog both exist where policy requires and are semantically distinct;
- E2E/test harness: owner allow → URL; owner deny → no URL.

### Documentation Updates

- record final access decision/result reason-code vocabulary in Module architecture if it changes;
- update library docs with R2 read-signing behavior if necessary;
- update progress tracker and CL-05 Feature 02 evidence.

### Acceptance Criteria

- a MediaAsset ID alone can never produce private access;
- contextual owner authorization remains external truth;
- all Media local readiness gates are rechecked at access time;
- sensitive access has the required dual Media/Audit evidence;
- no consumer Module needs an R2 presigning helper;
- no raw signed URL or secret appears in durable logs/records.

### Exit Gate

Before Feature 06 starts:

- allow/deny access contract tests pass;
- sensitive/healthcare denial tests pass;
- provider signing failure does not create false success evidence;
- URL/token log-scrape tests pass;
- idempotent/revocation race tests pass;
- E2E/test harness proves contextual owner can be swapped without changing Media entitlement logic;
- typecheck/lint/unit/integration/security tests pass.

---

## 06 Grant Revocation, Expiry, Access Evidence, and Race Safety

### Objective

Complete the `MediaAccessGrant` lifecycle with revocation, expiration, safe replay, concurrent access protection, and durable Media/Audit evidence without inventing domain-specific usage semantics that belong to other grant types.

### Observable Result

Active Media grants can expire or be revoked deterministically. Access attempts racing with revoke/expiry/freeze are resolved consistently. Support/debug queries show safe grant/event history. Expired/revoked grants cannot generate new signed credentials.

### Cluster Build-Plan Link

Completes **CL-05 Feature 02 — Contextual Media Access and Short-Lived Signed Delivery** and provides Media prerequisites for **CL-05 Feature 13 — Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification**.

### Dependencies

- Feature 05;
- SH-055 deadline expiration;
- SH-089 temporary grant revocation;
- SH-051/052 concurrency;
- SH-030 sensitive audit;
- SH-125 domain access event;
- root scheduled worker infrastructure.

### In Scope

- `revokeMediaAccessGrant` owner command;
- grant expiration owner command/worker;
- access-time expiry check independent of worker lag;
- `grant_expired`, `grant_revoked`, `access_blocked`, `provider_error` MediaAccessEvent handling;
- grant/event read models for authorized support/owners;
- concurrency behavior for issue/use/revoke/expire/freeze/delete races;
- safe cleanup eligibility for expired credential evidence according to retention policy;
- explicit preservation of unresolved `used` semantics.

### Out of Scope

- defining DigitalDownload max-use/count semantics;
- defining Agreement one-time access semantics;
- defining CourseVideo playback grant semantics;
- automatic business entitlement revocation based on foreign-domain table reads;
- final retention period for access events if not approved.

### Module-Owned Data

- `MediaAccessGrant.status`, `expiresAt`, `revokedAt`, `revokeReason`, `firstUsedAt`;
- `MediaAccessEvent` append history;
- no generic access ledger beyond Media.

### Public Interfaces

- `revokeMediaAccessGrant({ grantId, reason, sourceReference, idempotencyKey }, actorOrSystem)`;
- internal `expireMediaAccessGrant(grantId, now)`;
- authorized `getMediaAccessHistory(mediaAssetId or grantId)` if required for support/compliance;
- later Moderation/Privacy handlers invoke these owner commands rather than directly updating grant rows.

### Shared Operations Used

#### SH-089 — `revokeTemporaryAccessGrant`

- **Owner:** each grant owner using shared primitive.
- **Invocation:** Media grant revocation.
- **Local policy:** which Media instruction/source may revoke, reason mapping, event/audit requirements.
- **Prohibited duplicate:** generic “revoke every grant in every domain” table/service.

#### SH-055 — `runDeadlineExpiration`

- **Owner:** shared scheduler/queue infrastructure.
- **Invocation:** find grants whose `expiresAt` passed and dispatch owner expiration command.
- **Local policy:** Media expiry transition and evidence.
- **Prohibited duplicate:** Media-specific cron framework.

#### SH-051 / SH-052 — locking/concurrency

- **Owner:** shared persistence infrastructure.
- **Invocation:** concurrent issue/use/revoke/expire/freeze/delete.
- **Local policy:** grant/asset lock keys and conflict precedence.
- **Prohibited duplicate:** process-local mutexes.

#### SH-030 — `recordSensitiveAccess`

- **Owner:** Audit / Event Ledger.
- **Invocation:** sensitive denied/revoked access attempts when required.
- **Local policy:** Media action and target references.
- **Prohibited duplicate:** using Media event history as the only sensitive audit.

#### SH-125 — `recordDomainAccessEvent`

- **Owner:** Media for `MediaAccessEvent` meaning using shared append mechanism.
- **Invocation:** revocation/expiry/block/provider failure.
- **Local policy:** event type/reason metadata.
- **Prohibited duplicate:** mutable grant “lastEvent” as replacement for event history.

#### SH-044 / SH-047 / SH-048

- **Invocation:** idempotent revocation and durable expiry worker.
- **Local policy:** duplicate revocation/expiration are safe no-ops/replay.
- **Prohibited duplicate:** custom scheduler/idempotency infrastructure.

### Domain Logic

- `expiresAt <= now` means the grant is not valid even if the scheduled expiration job is delayed;
- revocation takes precedence over new issuance from that same grant;
- frozen/deleted/erased asset makes grant unusable regardless of grant row state;
- expiration and revocation append separate Media access evidence;
- repeated revoke/expire commands do not rewrite original evidence or generate duplicate notifications/events;
- `used` status/`firstUsedAt` is **not** generalized into one-use semantics until the unresolved grant-use policy is approved. A coding agent must not assume that all generic Media grants become invalid after first URL issuance or first fetch;
- domain-specific download limits belong to Digital Goods and use separate grant truth.

### Authorization / Compliance

- user revocation, system revocation, Moderation instruction, and Privacy instruction require distinct trusted invocation paths/authority evidence;
- support/admin must not gain read access merely because they can inspect grant metadata;
- revoke/expire metadata must exclude secrets and sensitive content.

### Database / Transaction Behavior

- revocation uses conditional update from currently revocable state and appends event atomically;
- expiration worker claims batches deterministically and invokes owner command idempotently;
- revoke versus expire race returns one final valid terminal status according to explicit precedence while preserving meaningful evidence; do not flip terminal states repeatedly;
- grant validity is recomputed from status + time + asset state in the access command transaction;
- cascade-deletion behavior is not relied upon as the retention design; Feature 08/09 reviews evidence preservation.

### Events / Jobs

- scheduled expiry via SH-055 + SH-047;
- optional Module event `media.access_grant.revoked` / `.expired` only if external consumers need it; `MediaAccessEvent` is always the local domain evidence;
- retry only technical worker failures, not already-expired/revoked outcomes.

### Provider Integration

No provider call is required to “revoke” an already-issued R2 presigned URL unless the provider architecture supports a practical object-level invalidation mechanism. Therefore short TTL is part of the security boundary. When asset-wide urgent revocation is required, Feature 07 may move/disable the object/public surface or otherwise apply provider-level enforcement through Media.

### UI / Admin Surface

No user UI required. Existing support/admin tooling may display grant state and safe event history. It must not display raw token hashes when unnecessary or any signed URL.

### Failure Behavior

- repeated revoke: idempotent replay;
- expire already revoked: no resurrection/status flip;
- access racing revoke: database/transaction rule deterministically denies or completes based on the committed ordering;
- worker delayed: access-time check still denies expired grant;
- provider credential already issued before revocation: cannot be assumed instantly invalid; bounded TTL and asset-level enforcement are the mitigation;
- unresolved `used` semantics reached by feature request: block that behavior and record architecture decision requirement.

### Tests

- expiration at exact boundary with clock-controlled tests;
- delayed expiration worker but access-time denial;
- revoke versus access concurrency;
- revoke versus expiry race;
- freeze/delete versus grant use race;
- idempotent repeated revocation;
- event append uniqueness/ordering;
- sensitive denial Audit integration;
- prove generic Media grant does not enforce DigitalDownload-style max-count policy;
- worker batching/retry/dead-letter tests.

### Documentation Updates

- if one-time/reusable Media grant semantics are approved, update Module architecture before implementing them;
- record expiration worker schedule and operational ownership in provider/ops docs;
- update progress tracker and mark Media portion of CL-05 Feature 02 complete.

### Acceptance Criteria

- expired/revoked grants cannot produce new credentials;
- server-time validity does not depend on worker timing;
- concurrent terminal transitions are deterministic and cannot resurrect access;
- Media and Audit evidence remain distinct;
- generic grant mechanics do not absorb Digital Goods/Agreement/Video semantics.

### Exit Gate

CL-05 Feature 02 is complete for Media when:

- grant issue/expiry/revoke paths pass unit/integration/concurrency tests;
- access is denied after expiry even with delayed cron;
- race tests show no credential issuance after committed revoke/freeze/delete;
- no one-time-use semantics were invented without approval;
- no signed URLs/tokens leak to logs;
- all contract/E2E access tests pass.

---
# Phase 4 — Cross-Module Enforcement and Privacy Integration

This phase does not create new Media business truth. It proves that authoritative decisions from Moderation, Healthcare, ComplianceHold, Search, and Privacy can be enforced through Media's public boundary without those Modules mutating Media tables directly.

## 07 Moderation, Hold, Healthcare, Public Exposure, and Search Bridge

### Objective

Implement the Media-owned execution path for file freeze, public URL removal/restoration, access-grant revocation, healthcare-sensitive enforcement, and search-refresh requests after authoritative external decisions.

### Observable Result

An authorized Moderation instruction can freeze or restore a MediaAsset and remove or restore approved public delivery; an active hold or Healthcare denial blocks applicable access; Search receives a refresh request when a Media-owned public-delivery fact changes. No external Module directly updates Media rows or R2 state.

### Cluster Build-Plan Link

Implements the Media portion of **CL-05 Feature 13 — Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification**.

### Dependencies

- Features 01–06;
- SH-011 ComplianceHold;
- SH-020 Healthcare readiness;
- SH-089 grant revocation;
- SH-091 Search refresh;
- SH-103 Moderation execution;
- SH-041 Notification only for explicitly defined user-facing effects;
- SH-046 outbox for reliable downstream requests where required;
- Search/Moderation/Healthcare contract fakes or real interfaces.

### In Scope

- `executeMediaModerationInstruction` public target-executor command;
- file-level freeze/unfreeze/restore transition policy;
- public URL revocation/provider exposure removal;
- revoke MediaAccessGrant sets when the authoritative instruction requires it;
- prevent new access/promotion while frozen;
- healthcare decision enforcement in access path and authorized admin/support tooling;
- hold decision mapping for upload/promotion/access actions;
- SH-091 Search refresh request after public-safe Media state changes that can affect source/public projection;
- safe audit/domain event evidence for administrative enforcement;
- optional Notification request only when an approved workflow says a user should be notified.

### Out of Scope

- validating DMCA/DSA/legal notices;
- opening or resolving ModerationCase;
- creating/releasing ComplianceHold truth;
- deciding Healthcare compliance/BAA state;
- writing SearchUpsertEvent or Typesense;
- deciding whether an Offering/Profile/Job is public;
- generic entitlement-loss logic from Orders/Digital Goods/Video.

### Module-Owned Data

- `MediaAsset.status=frozen` and freeze/revocation/restoration fields permitted by schema;
- `MediaAsset.publicUrlRevokedAt` and provider-exposure state;
- MediaAccessGrant revocation effects;
- MediaAccessEvent enforcement evidence;
- no ModerationCase, ComplianceHold, HealthcareDataBoundary, or SearchUpsertEvent truth.

### Public Interfaces

Implement/stabilize:

- `executeMediaModerationInstruction(instruction, systemContext)`;
- `freezeMediaAsset(mediaAssetId, sourceDecision)`;
- `revokeMediaPublicExposure(mediaAssetId, sourceDecision)`;
- `restoreMediaAssetAccess(mediaAssetId, sourceDecision)`;
- Media owner acknowledgment result containing executed/not-applicable/retryable/terminal status and evidence references;
- access/readiness queries reflect current freeze/public revocation state.

### Shared Operations Used

#### SH-103 — `executeModerationDecision`

- **Owner:** Content Moderation owns decision; each target owner executes.
- **Invocation:** Moderation sends typed instruction to Media.
- **Local policy:** translate the approved instruction into MediaAsset/grant/provider effects without re-adjudicating the case.
- **Prohibited duplicate:** `mediaModerationCase`, `dmcaDecisionService.ts`, direct Moderation repository mutation of Media tables.

#### SH-011 — `evaluateComplianceHold`

- **Owner:** Admin Review / Compliance Hold.
- **Invocation:** upload, promotion, and access actions where a hold applies.
- **Local policy:** mapping to deny/freeze/stop behavior.
- **Prohibited duplicate:** `isOnHold` Media flags as generic platform truth.

#### SH-020 — `evaluateHealthcareReadiness`

- **Owner:** Healthcare / Regulated Services.
- **Invocation:** healthcare-sensitive file access/admin exposure.
- **Local policy:** enforce returned allow/redact/block/deny as applicable to file delivery/metadata response.
- **Prohibited duplicate:** healthcare classification/BAA rules inside Media.

#### SH-089 — `revokeTemporaryAccessGrant`

- **Owner:** Media as grant owner using shared primitive.
- **Invocation:** moderation/hold/security instruction requiring existing Media grants to stop.
- **Local policy:** batch target selection and reason evidence.
- **Prohibited duplicate:** generic cross-domain grant revoker.

#### SH-091 — `requestSearchProjectionRefresh`

- **Owner:** Search / Public Visibility.
- **Invocation:** after public derivative exposure or revocation changes in a way that may affect source projection.
- **Local policy:** Media supplies source/asset fact reference; Search/source owners reconstruct approved public projection.
- **Prohibited duplicate:** `typesenseMediaSync.ts`, direct SearchUpsertEvent creation if Search command owns it.

#### SH-029 / SH-030 / SH-125

- **Owners:** Audit/Event Ledger and Media domain evidence.
- **Invocation:** material administrative action, sensitive access, Media access-event history.
- **Local policy:** minimize metadata; do not duplicate source decision text/payload.
- **Prohibited duplicate:** one generic Media “audit everything” table.

#### SH-041 — `requestNotification`

- **Owner:** Notification.
- **Invocation:** only after a product/legal workflow explicitly requires a user alert.
- **Local policy:** Media supplies safe trigger/route references, not provider delivery.
- **Prohibited duplicate:** direct SES/SMS/push call from Media.

#### SH-046 / SH-044 / SH-051

- **Invocation:** reliable downstream refresh/notification and idempotent, concurrency-safe target execution.
- **Prohibited duplicate:** fire-and-forget enforcement and local workflow runner.

### Domain Logic

- Moderation instruction is an input fact, not a Media legal decision;
- freeze prevents ordinary access and promotion but preserves evidence/object according to instruction/retention policy;
- public URL removal is not deletion;
- restoration requires an authoritative restoration instruction and must not infer that a case is resolved from time passing;
- restore must not make a rejected/infected/deleted/erased file ready or public;
- active hold/Healthcare denial is re-evaluated at access time where applicable;
- revocation of Media grants affects only MediaAccessGrant truth. DigitalDownload/Agreement/Video owners revoke their own grants separately;
- Search refresh is requested after Media-owned public delivery state changes, but Media does not decide final search visibility.

### Authorization / Compliance

- only trusted Moderation/Privacy/system interfaces may invoke enforcement commands;
- admin/support execution paths use SH-001/002 and SH-014 step-up only if root sensitive-action matrix requires it;
- healthcare policy can block payload access even for authorized support roles;
- evidence preservation may conflict with deletion; Privacy/retention flow decides destructive disposition later.

### Database / Transaction Behavior

- source moderation instruction ID + target ID should form an idempotent execution identity;
- freeze/revoke state changes and local domain evidence are one transaction;
- outbox for Search/Notification is written transactionally with source Media change when those effects are required;
- batch grant revocation is idempotent and cannot revive terminal grants;
- restore uses compare-and-set/current state and authoritative source reference;
- do not overwrite prior freeze reason/source evidence with an unrelated request without audit trail.

### Events / Jobs

Potential owner events:

- `media.asset.frozen`;
- `media.asset.restored`;
- `media.public_access.revoked`.

Use SH-046 only where consumers need them. Search refresh and Notification requests may be outbox-backed. Large grant revocation sets may run through SH-047 worker using the source decision as idempotency/correlation key.

### Provider Integration

R2/public delivery enforcement may require:

- moving/copying/removing a public derivative;
- changing object availability/bucket exposure;
- invalidating a delivery path supported by the selected serving design.

Provider mechanics remain behind `ObjectStoragePort`. A private presigned URL already issued may remain valid until its short TTL; urgent response therefore also relies on short-lived credentials and asset-level future denial.

### UI / Admin Surface

No new moderation UI. Existing Moderation/admin surfaces invoke Media through the target executor and display returned execution status/evidence. Media may expose safe technical status to authorized support.

### Failure Behavior

- invalid/unrecognized instruction: reject without state mutation;
- duplicate instruction: replay execution result;
- R2 public-exposure revocation failure: Media remains frozen/blocked locally, record IntegrationFailure, retry provider effect;
- Search unavailable: Media truth remains committed; outbox/retry request later;
- Notification unavailable: source truth remains committed; Notification retries independently;
- restoration while asset rejected/infected/deleted/erased: deny/terminal not-restorable;
- Healthcare/hold dependency unavailable for sensitive access: fail closed according to root policy rather than assume allow.

### Tests

- Moderation contract fake → freeze/public revoke;
- duplicate moderation instruction idempotency;
- direct external repository mutation is not needed;
- freeze prevents promotion/access;
- restore does not resurrect invalid/deleted/erased asset;
- grant batch revocation;
- active hold blocks configured Media actions;
- Healthcare deny blocks payload while preserving safe metadata if policy permits;
- Search refresh requested exactly once per semantic public-state change;
- direct Typesense/SearchUpsertEvent access absent from Media imports;
- provider public-revocation failure retry while local freeze remains enforced;
- audit/domain/ops evidence separation.

### Documentation Updates

- record final Moderation instruction contract/reason mapping if it settles a deferred interface detail;
- update Search integration docs only if SH-091 contract changes;
- update progress tracker with Media portion of CL-05 Feature 13.

### Acceptance Criteria

- Moderation/hold/Healthcare decisions are consumed, not recreated;
- no external Module writes Media tables directly;
- file can be frozen/publicly hidden while evidence remains stored;
- Search is notified through SH-091 only;
- Notification delivery is not implemented inside Media;
- existing grants and future access are correctly blocked/revoked according to instruction.

### Exit Gate

Before Feature 08 starts:

- moderation freeze/revoke/restore contract tests pass;
- hold/Healthcare access tests pass;
- provider failure cannot expose a locally frozen asset through a new Media credential;
- Search integration proves no direct Typesense write;
- idempotency/outbox/audit tests pass;
- no new local legal/hold/healthcare truth exists.

---

## 08 Privacy Inventory, Retention, Erasure, and R2 Deletion

### Objective

Implement Media's owner-specific Privacy protocol: enumerate subject-related Media data, supply Media retention facts, revoke access, anonymize approved personal fields, delete R2/provider resources when instructed, and report idempotent execution results without owning the Privacy workflow.

### Observable Result

A Privacy test harness can enumerate a subject's Media assets/upload/access/proof records, issue an authorized erase/anonymize/retain instruction, and receive a deterministic execution result. Erasable R2 objects disappear, grants are revoked, retained legal/security evidence is preserved only when Privacy supplies/records an approved exemption, and the parent Privacy workflow remains external.

### Cluster Build-Plan Link

Implements the Media portion of **CL-05 Feature 14 — Privacy Target Executors, Retention, and Provider Deletion**.

### Dependencies

- Features 01–07;
- SH-095 execute Privacy instruction;
- SH-096 subject-data enumeration;
- SH-097 retention requirement protocol;
- SH-098 anonymization;
- SH-070 provider deletion;
- SH-089 grant revocation;
- SH-029/030 audit where required;
- object storage delete/head adapter;
- Privacy contract fake or implementation.

### In Scope

- `enumerateMediaSubjectData`;
- `evaluateMediaRetentionFacts` for Media-owned evidence/object facts;
- `executeMediaPrivacyInstruction`;
- grant revocation before destructive exposure changes when required;
- delete R2/private/public derivative objects when authorized;
- mark/record erasure effects distinctly from normal product deletion;
- anonymize original filename/request metadata or other approved personal fields while preserving relational integrity;
- return deleted/absent/anonymized/retained/retryable/terminal results;
- safe export serialization of Media-owned metadata when Privacy requests contribution;
- destructive-cascade review/test.

### Out of Scope

- creating `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, or `DataRetentionExemption`;
- verifying Privacy requester identity;
- deciding legal retention exemption;
- deleting Agreement/Order truth;
- deleting contextual joins owned by other Modules;
- Search privacy completion aggregation.

### Module-Owned Data

Privacy inventory may include:

- `MediaAsset` and derivatives;
- `MediaUploadSession`;
- `MediaValidationResult`;
- `MediaScanResult`;
- `MediaProcessingResult`;
- `MediaAccessGrant`;
- `MediaAccessEvent`;
- provider object references/storage keys;
- upload/request metadata such as original filename/IP hash/user-agent only to the extent it remains stored and subject to policy.

### Public Interfaces

Implement Privacy protocol handlers:

- `enumerateSubjectData(subject, cursor)` — SH-096 implementation;
- `evaluateRetentionRequirement(target)` — Media facts contribution to SH-097;
- `executePrivacyInstruction(target, disposition, privacyContext)` — SH-095 implementation;
- optional `serializeMediaForPrivacyExport(target)` where Privacy export architecture requires it.

### Shared Operations Used

#### SH-095 — `executePrivacyInstruction`

- **Owner:** Privacy orchestrates; Media executes its own targets.
- **Invocation:** authoritative erase/anonymize/revoke/retain instruction.
- **Local policy:** Media maps target/disposition to file/grant/proof/provider operations.
- **Prohibited duplicate:** `MediaPrivacyRequest`, `MediaErasureJob`, local GDPR workflow.

#### SH-096 — `enumerateSubjectData`

- **Owner:** each data owner through Privacy-defined interface.
- **Invocation:** inventory assets/proofs/provider refs related to subject.
- **Local policy:** Media determines which Media-owned records/refs belong in inventory.
- **Prohibited duplicate:** Privacy directly querying every Media table as its own repository.

#### SH-097 — `evaluateRetentionRequirement`

- **Owner:** data owner supplies facts; Privacy records exemption.
- **Invocation:** before destructive instruction when Media knows facts such as legal-archive storage or security evidence purpose.
- **Local policy:** Media reports facts, not legal conclusion.
- **Prohibited duplicate:** `mediaLegalHold`, `keepForever`, local retention-exemption table.

#### SH-098 — `anonymizePersonalFields`

- **Owner:** shared primitive; Media supplies mapping.
- **Invocation:** retained records whose personal fields may be minimized.
- **Local policy:** approved Media field map and referential integrity.
- **Prohibited duplicate:** ad hoc irreversible string replacement without documented mapping.

#### SH-070 — `deleteProviderResource`

- **Owner:** provider-owning Module; Media owns R2 resource deletion.
- **Invocation:** delete underlying R2 object/public derivative when Privacy instructs and retention permits.
- **Local policy:** storage-key/provider mapping and idempotent absent-as-success semantics.
- **Prohibited duplicate:** Privacy or contextual Module creating an R2 client.

#### SH-089 — `revokeTemporaryAccessGrant`

- **Owner:** Media for MediaAccessGrant.
- **Invocation:** before/with destructive Privacy action where continued access must stop.
- **Local policy:** grant target selection and reason.
- **Prohibited duplicate:** direct grant status mutation from Privacy repository.

#### SH-044 / SH-047 / SH-048 / SH-029 / SH-030 / SH-037

- **Invocation:** idempotent target execution, provider retries, audit, operational failure.
- **Local policy:** destructive action classification and safe metadata.
- **Prohibited duplicate:** Media-only privacy retry/audit infrastructure.

### Domain Logic

Privacy execution order where applicable:

```text
validate trusted Privacy instruction
→ re-check target current state
→ evaluate supplied/recorded retention disposition
→ revoke future Media access
→ anonymize permitted personal metadata
→ delete provider objects/derivatives if disposition allows
→ update Media erasure/deletion state according to approved semantics
→ preserve retained proof/object only when instructed
→ append required audit/domain evidence
→ return deterministic executor result to Privacy
```

Rules:

- product deletion is not privacy erasure;
- erasing `MediaAsset` database metadata without deleting R2 object is incomplete when object deletion is allowed;
- deleting R2 object while leaving unnecessary original filenames/request metadata may also be incomplete;
- retained contract/security evidence must be minimized where permitted but not destroyed against an approved exemption;
- contextual attachment owner handles its own join/business record erasure; Media handles file/proof/storage truth;
- provider object already absent is normally idempotent success/absent, not a fatal error;
- Privacy parent completion is not decided by Media.

### Authorization / Compliance

- destructive executor accepts only a trusted Privacy workflow/system context, not ordinary user route input;
- manual admin retry may require SH-014 if root step-up matrix says so;
- sensitive object keys/provider refs are not returned to ordinary users;
- `AccessAuditLog` retention belongs to Audit policy; Media must not delete generic audit proof through its own executor;
- scan/security proof retention may require Privacy exemption; Media only supplies facts.

### Database / Transaction Behavior

- each Privacy target instruction has stable idempotency identity from Privacy target/instruction ID;
- revoke/anonymize/local-state changes are transactionally consistent; external object deletion is coordinated as idempotent provider work with result recorded back to Privacy;
- if R2 deletion succeeds and database transaction later fails, reconciliation must converge safely rather than recreate the object;
- if database marks erasure pending and provider fails, keep parent target unresolved/retryable; do not claim completed erasure;
- cascade behavior must be explicitly tested so deleting MediaAsset does not accidentally destroy retention-required access/security proof without Privacy/Audit policy;
- retained records use approved anonymization, not hard delete.

### Events / Jobs

- provider deletion may use durable job for retryable R2 outage;
- optional `media.asset.erased` event only if architecture registers consumers; do not expose subject data in payload;
- grant revocation events/evidence follow Feature 06;
- operational failure goes to SH-037, parent Privacy target remains source of fulfillment status externally.

### Provider Integration

**Provider:** R2 through `ObjectStoragePort.deleteObject/headObject`.  
**Idempotency:** object absent is safe final result; repeated delete does not fail privacy completion.  
**Retry:** timeout/rate-limit/provider unavailable are retryable; permission/configuration errors may be terminal/manual review.  
**Reconciliation:** Feature 09 detects local/provider discrepancies.  
**Public derivatives:** delete/revoke all Media-owned derived objects included by instruction.  
**No provider webhook required.**

### UI / Admin Surface

No standalone Media privacy UI. Privacy/Admin workflow displays target execution status. Media may expose an authorized technical execution inspector through existing Ops tooling only.

### Failure Behavior

- retention disposition says retain: do not delete; return retained with source reference;
- provider object absent: idempotent success/absent;
- provider unavailable: retryable result, parent Privacy flow remains unresolved;
- permission/config error: terminal/manual review + IntegrationFailure;
- duplicate instruction: replay same semantic result;
- contextual join still exists after Media deletion: report only Media completion; contextual owner remains responsible for its target;
- attempt to invoke from ordinary user route: authorization denial.

### Tests

- cursorable subject-data inventory;
- inventory includes derivatives/provider refs without leaking them to unauthorized caller;
- delete versus retain disposition;
- anonymization field-map tests;
- original filename/privacy metadata cleanup;
- R2 delete success/absent/retryable/terminal;
- grant revocation before/with deletion;
- duplicate instruction idempotency;
- crash/retry between provider deletion and DB update;
- cascade-retention tests for grants/events/proof;
- prove no PrivacyRequest/DataErasureJob/DataRetentionExemption table created in Media;
- integration harness with Privacy fake across retained and erased targets.

### Documentation Updates

- if cascade behavior requires schema migration, update Module architecture/ADR with retention justification;
- document Media subject-data inventory and anonymization map in privacy/data inventory docs;
- update progress tracker and CL-05 Feature 14 evidence.

### Acceptance Criteria

- Privacy can enumerate and execute Media-owned targets through typed contracts;
- erasure removes R2 bytes when allowed, not just database pointers;
- retention occurs only through the Privacy retention protocol;
- no local Privacy lifecycle exists;
- duplicate/provider-partial executions are recoverable and idempotent;
- access is revoked before a supposedly erased file can be newly delivered.

### Exit Gate

Before Feature 09 starts:

- Privacy inventory/executor contract tests pass;
- R2 deletion success/absent/retry/manual paths pass;
- retention/cascade/anonymization tests pass;
- no Media-local Privacy workflow tables/services exist;
- sensitive telemetry audit passes;
- the Media owner result can participate in the parent CL-05 Feature 14 Privacy harness.

---

# Phase 5 — Media Hardening and Production Verification

## 09 Media Reconciliation, Cleanup, Security, Concurrency, and Production Readiness

### Objective

Close Media-specific production gaps in provider reconciliation, quarantine/orphan cleanup, scanner health, concurrency, security, rate limiting, retention safety, audit completeness, telemetry, migration behavior, and performance without adding new product scope.

### Observable Result

Media remains correct under duplicate requests/jobs, provider outages, stale workers, missing R2 objects, orphaned R2 objects, scanner degradation, grant races, moderation/privacy races, and operational replay. Operators can detect and safely reconcile discrepancies without treating Ops state as Media truth.

### Cluster Build-Plan Link

Implements the Media portion of **CL-05 Feature 15 — Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness**.

### Dependencies

- Features 01–08;
- production R2 configuration;
- production-capable malware scanner selected for every launch context whose active policy requires scanning;
- SH-032–039 Observability capabilities;
- SH-044–052 reliability/concurrency primitives;
- SH-055 expiration;
- SH-062 provider reconciliation pattern;
- SH-070 deletion;
- root rate-limit/security standards;
- final enough step-up matrix for manual destructive/admin actions.

### In Scope

- R2 local-versus-provider reconciliation;
- orphan/quarantine/abandoned-upload cleanup;
- missing-object discrepancy detection;
- safe dry-run reconciliation report;
- scanner/provider health check and fail-closed readiness behavior;
- dead-letter replay/retry commands through Ops infrastructure;
- rate limits/abuse controls for upload-session, completion, and signed-access endpoints;
- final concurrency review across promotion/access/revoke/freeze/delete/privacy;
- audit completeness review;
- telemetry/log/metric safety;
- data/index query tuning;
- migration-from-clean and realistic-seed verification;
- retention/destructive migration review;
- backup/rollback operational notes where root standards require them;
- production launch checks for R2 and scanner.

### Out of Scope

- new object-storage provider solely for redundancy;
- new malware providers beyond the approved production adapter;
- generic incident management UI;
- future content fingerprinting unless SH-106 is separately resolved;
- digital-goods, video, resume, message, or Agreement business policy;
- redesigning contextual join ownership.

### Module-Owned Data

Review/tune only existing Media-owned truth unless a clear production defect requires a justified migration:

- MediaAsset/provider mapping and indexes;
- upload/session status/indexes;
- validation/scan/processing evidence indexes;
- grant expiry/token/access-event indexes;
- erasure/freeze/public-revocation fields;
- any new reconciliation cursor/checkpoint must be operational or clearly Media-owned, not a generic queue/incident replacement.

### Public Interfaces

No new broad consumer API by default. Harden:

- existing upload/access/readiness commands and queries;
- authorized `reconcileMediaStorage` command/run interface for Ops;
- `checkMediaProviderHealth` implementation registered through SH-039;
- safe admin retry/replay entry points that dispatch canonical owner commands rather than mutating rows.

### Shared Operations Used

#### SH-062 — `reconcileProviderState`

- **Owner:** each provider-owning Module using shared worker framework.
- **Invocation:** compare MediaAsset/object expectations with R2 state and scanner/processor where applicable.
- **Local policy:** which discrepancies are safe to auto-repair versus manual review.
- **Prohibited duplicate:** a generic provider reconciliation system that mutates non-Media Modules.

#### SH-039 — `checkServiceHealth`

- **Owner:** Observability / Ops coordinates; Media supplies check.
- **Invocation:** R2/scanner processing readiness checks.
- **Local policy:** what degraded/unavailable means for upload/read access and fail-closed scan behavior.
- **Prohibited duplicate:** Media-specific health dashboard truth.

#### SH-032–038 — request/log/redaction/exception/metric/failure/queue telemetry

- **Owner:** Observability / Ops.
- **Invocation:** all Media requests/workers/provider operations.
- **Local policy:** approved low-cardinality Media dimensions and normalized operations.
- **Prohibited duplicate:** raw debug payload storage, second Sentry/logger/metrics client.

#### SH-044–052 — idempotency, event dedupe, queues, retries, locks, optimistic concurrency

- **Owner:** shared platform infrastructure.
- **Invocation:** harden every retry/race path.
- **Local policy:** Media command identity, lock keys, retry classification, stale-result semantics.
- **Prohibited duplicate:** local infra substitutes.

#### SH-055 — `runDeadlineExpiration`

- **Invocation:** expired grant/session cleanup.
- **Local policy:** Media owner transitions and cleanup eligibility.
- **Prohibited duplicate:** separate cron runner.

#### SH-070 / SH-082–089 / SH-095–098 / SH-103

- **Invocation:** verify provider deletion, Media safety/access operations, Privacy, Moderation all compose under failure/replay.
- **Prohibited duplicate:** hardening-only alternative code paths that bypass canonical commands.

### Domain Logic

Reconciliation classes:

1. **Local asset expects object; provider object exists:** healthy.
2. **Local non-deleted asset expects object; provider object missing:** discrepancy. Do not fabricate object; block access, create IntegrationFailure, and classify repair/manual action.
3. **Local deleted/erased asset; provider object exists:** cleanup/privacy discrepancy; delete if authorized by existing instruction or surface for manual/privacy follow-up rather than inventing a new legal basis.
4. **Provider orphan object with no Media record:** quarantine/report and delete only according to approved orphan policy/age; avoid deleting newly uploaded in-flight objects.
5. **Stale quarantined/abandoned session:** cleanup only after expiration and no active worker/valid completion.
6. **Scanner unhealthy and active policy requires scanning:** new required-scan assets cannot reach ready; health state is operational, not a MediaScanResult substitute.

Performance rules:

- signed-access command should avoid loading unnecessary proof history once readiness summary/current state is sufficient;
- grant expiration and cleanup use indexed cursor batches;
- reconciliation uses bounded pages/cursors and dry-run mode;
- no high-cardinality user IDs/file names in metrics;
- large files stream; do not load whole file into memory when libraries/provider APIs allow bounded streaming.

### Authorization / Compliance

Security review must verify:

- R2/scanner credentials least privilege and server-only;
- upload and access endpoints rate limited under root policy;
- presigned upload/read URLs have bounded scopes/TTL;
- path traversal and content-type confusion remain blocked;
- sensitive healthcare/legal/identity/resume files never become public through fallback logic;
- support/admin cannot bypass contextual/Healthcare decisions;
- Privacy and Moderation executor authorization is system-bound;
- no secrets/signed URLs/raw provider payloads in logs, metrics, error monitoring, audit metadata, analytics;
- AccessAuditLog coverage is complete for policy-required sensitive access;
- destructive migrations/cascade rules preserve approved retention evidence.

### Database / Transaction Behavior

- verify all critical indexes against deployed DB, not only Prisma source;
- use database constraints/row locks/CAS for races; no in-memory lock correctness;
- reconcile/cleanup commands are idempotent and checkpointed/cursorable;
- migration rollback/forward strategy is tested for new session/policy/cascade changes;
- background cleanup must avoid long transactions across large batches;
- support retry invokes domain commands and cannot set status directly.

### Events / Jobs

Module-owned workers to production-harden:

- upload validation/scan/processing/promotion;
- abandoned upload/session cleanup;
- expired MediaAccessGrant processing;
- R2 object-state reconciliation;
- quarantine/orphan cleanup;
- Privacy R2 deletion retries;
- Moderation public-exposure revocation retries.

Every worker requires:

- stable idempotency key;
- request/correlation context;
- lease/heartbeat through shared queue;
- bounded retry classification;
- visible dead-letter state;
- owner business-state update when terminal failure changes Media outcome;
- safe manual replay path.

### Provider Integration

#### Cloudflare R2

- production credentials/scopes verified;
- bucket classes mapped to approved private/quarantine/public-processed design;
- presign upload/read TTL and headers tested;
- object head/copy/move/delete behaviors normalized;
- reconciliation and orphan cleanup verified;
- provider outage drills performed with adapter fault injection.

#### Malware scanner

Production readiness requires a selected adapter for every scan-required launch context. The final adapter must define:

- request/stream limits;
- timeout;
- retryable/terminal errors;
- clean/suspicious/infected/failed mapping;
- scanner version/reference evidence;
- health check;
- privacy/data handling terms appropriate to uploaded data;
- callback verification/dedupe only if the chosen provider uses asynchronous callbacks.

No scan-required policy can launch with a fake scanner.

#### `file-type` / `sharp` / processors

- pinned/approved versions under dependency standards;
- malformed input tests;
- memory/CPU limits for large images;
- unsupported format behavior fails closed where processing is required.

### UI / Admin Surface

Integrate with existing Ops/admin tooling only:

- provider health/degradation summary;
- safe reconciliation dry-run discrepancy list;
- dead-letter/retry links;
- MediaAsset/session/grant technical status lookup;
- no raw provider payload, signed URL, token, object contents, or unnecessary sensitive filename display.

### Failure Behavior

Explicitly test/document:

- R2 unavailable/degraded/delayed;
- scanner unavailable/degraded;
- object missing unexpectedly;
- orphan object discovered;
- processor timeout/repeated crash;
- duplicate job/command;
- stale job after freeze/delete/erasure;
- concurrent grant issue/revoke/expire;
- public-revocation provider failure;
- Privacy provider deletion partial failure;
- Search/Notification unavailable after Media state change;
- dead-letter replay;
- migration on realistic seeded data;
- reconciliation discovers unsafe ambiguity requiring manual review.

Unsafe discrepancies must stop automatic repair and surface a safe manual-review result rather than guessing.

### Tests

- load/concurrency tests for upload completion, promotion, and grant access/revoke;
- adapter chaos/fault-injection tests;
- scanner health/fail-closed tests;
- R2 reconciliation dry-run and repair tests;
- orphan/quarantine cleanup age/in-flight safety tests;
- endpoint abuse/rate-limit tests;
- authorization/RLS tests required by root architecture;
- token/URL/secret log-scrape tests across logger/Sentry/metrics/audit;
- audit completeness tests for sensitive file actions;
- Privacy retention/destructive tests;
- moderation enforcement replay tests;
- clean database migration and realistic-seed migration tests;
- query/index performance checks for readiness/grant expiry/access history;
- production build/typecheck/lint/unit/integration/E2E suite.

### Documentation Updates

Before declaring production readiness:

- record production malware scanner selection/ADR;
- record final R2 bucket/retention/encryption posture;
- update Module architecture for any approved session status/policy version/cascade changes;
- document reconciliation auto-repair versus manual-review matrix;
- update security/privacy data inventory;
- update progress tracker and CL-05 Feature 15 evidence.

### Acceptance Criteria

- all launch scan-required contexts use a production-capable scanner and fail closed when unhealthy;
- R2/object discrepancies are detectable and recoverable without making provider state business truth;
- all known races have database-backed deterministic semantics;
- destructive/privacy/moderation replay is idempotent;
- sensitive access audit coverage is verified;
- telemetry is free of prohibited secrets/content;
- no contextual Module duplicates Media storage/validation/signing services;
- migration and realistic-seed verification pass.

### Exit Gate

Media / File Access is production-ready only when all are true:

- Features 01–08 exit gates remain green under the production configuration;
- R2 and scanner health checks pass;
- required scanner provider is recorded and configured;
- reconciliation dry-run finds no unexplained launch-blocking discrepancies;
- concurrency/idempotency/chaos/privacy/moderation/audit/security tests pass;
- no raw private object, signed URL, access token, provider secret, PHI, resume contents, identity document contents, contract text, or unnecessary personal metadata appears in telemetry;
- clean and realistic-seed migrations pass;
- final typecheck/lint/unit/integration/E2E/build checks pass;
- remaining unresolved architecture items are explicitly documented and do not undermine launch safety.

---

# Module Integration Phase

The Media Module integration proof is distributed across Features 04–08 but must be reviewed as one boundary suite before production readiness.

## Required contract/integration proofs

### Contextual attachment owner → Media

```text
context owner validates its business attachment
→ SH-090 attachValidatedMedia
→ Media returns technical readiness/attachability
→ context owner writes its own join/business record
```

Required tests:

- Offering-style context can attach a ready asset but Media never writes Offering lifecycle truth;
- Candidate/resume-style context can require `candidate_resume` policy and retain resume-specific access outside Media;
- Message-style context retains Thread participant policy outside Media;
- Order/Agreement-style context retains transaction/contract roles outside Media;
- Digital Goods registers only a ready MediaAsset and later uses Media signed delivery without moving DigitalDownloadGrant truth into Media;
- Video receives a ready private source asset without moving `CourseVideoAsset` provider lifecycle into Media.

### Contextual access owner → Media

```text
context owner: SH-026 allow/deny
→ Media: local readiness + hold + healthcare gates
→ MediaAccessGrant
→ SH-087 signed object delivery
→ MediaAccessEvent
→ SH-030 AccessAuditLog when sensitive
```

Required tests:

- swapping fake Order/resume/message contextual owners does not change Media entitlement logic;
- contextual denial never creates a usable credential;
- Media denial can occur even after contextual allow when asset is unsafe/frozen/erased;
- consumer cannot bypass Media with direct R2 access.

### Moderation → Media

```text
Moderation decision truth
→ SH-103 target instruction
→ Media freeze/revoke/restore/provider effect
→ acknowledgment
```

Required tests:

- Moderation does not mutate Media repository;
- Media does not create ModerationCase/LegalNotice truth;
- provider failure is retryable while local freeze continues to block new delivery.

### Privacy → Media

```text
PrivacyRequest/DataErasureTarget truth
→ SH-096 inventory / SH-097 retention facts
→ SH-095 instruction
→ Media grant/object/metadata execution
→ result returned to Privacy
```

Required tests:

- Media owns only its target execution;
- retention exemption remains Privacy-owned;
- R2 bytes are actually deleted when allowed;
- contextual owner records remain that owner's responsibility.

### Audit / Ops

Required tests:

- `MediaAccessEvent` and `AccessAuditLog` are both present when policy requires and cannot substitute for one another;
- `IntegrationFailure`/queue dead-letter can diagnose a failed scanner/R2 operation but never becomes MediaAsset status truth;
- correlation IDs propagate through upload → job → provider → audit/outbox.

## Integration Exit Gate

- all direct dependency contract suites pass against fakes or real implementations;
- no integration test reaches into a neighboring Module's Prisma repository to manufacture the decision being tested, except fixture setup explicitly isolated from production code;
- no neighboring Module imports the R2/scanner/signing implementation directly;
- every cross-Module failure has a stable owner/result boundary;
- the CL-05 critical workflow `safe upload → ready MediaAsset → authorized short-lived download` passes end-to-end.

---

# Module Hardening Phase

Feature 09 is the implementation slice; this section defines the final review lens applied across all completed features.

## State-transition races

Verify at minimum:

- validation worker versus delete/freeze;
- scan worker versus delete/freeze;
- processing/promotion versus moderation freeze;
- promotion versus Privacy erasure;
- signed issuance versus grant revoke/expiry;
- signed issuance versus MediaAsset freeze/delete/erase;
- provider cleanup versus upload completion;
- restore versus terminal rejected/infected/deleted/erased state.

Every race must resolve through database state/transactions/locks or compare-and-set semantics, never process-local memory.

## Idempotency and replay

Replay tests must cover:

- create/complete upload session;
- every worker stage;
- derivative generation;
- promotion;
- access grant issuance;
- revoke/expire;
- moderation instruction;
- privacy instruction/provider deletion;
- reconciliation repair.

Replay must return the original semantic result or an explicit stable no-op/conflict. It must never duplicate assets, proofs, grants, derivatives, or external provider effects.

## Provider outage and reconciliation

For R2/scanner/processors:

- classify transient versus terminal;
- preserve Media truth during outage;
- record IntegrationFailure;
- expose queue/dead-letter state;
- support safe retry/reconcile;
- never infer success from provider timeout;
- never make a required-scan asset ready when scanner is unhealthy.

## Security

Verify:

- strict server input validation;
- opaque object keys;
- no executable/public upload directories;
- binary type validation;
- required malware scan;
- required metadata/GPS scrub;
- bounded presign scope/TTL;
- secrets/token hashes handled according to cryptographic standards;
- rate limits on upload/access endpoints;
- least privilege provider credentials;
- no public fallback for private/sensitive content;
- admin/support least privilege plus Healthcare policy.

## Sensitive-data access

Sensitive Media contexts include identity documents, professional license documents, resumes/CVs, healthcare files, legal/Agreement files, private messages/order files where policy marks them sensitive.

Required review:

- access authorization belongs to the context owner;
- SH-030 audit coverage exists where required;
- telemetry/analytics omit content and sensitive metadata;
- signed credentials are ephemeral;
- support tools expose only minimum safe metadata.

## Privacy and retention

Verify:

- product deletion and legal erasure remain distinct;
- R2 deletion participates in erasure;
- original filenames/IP/user-agent metadata are handled by data inventory/anonymization policy;
- access/security proof is not accidentally removed by cascade;
- retained legal/security evidence is preserved only through approved Privacy exemption flow;
- provider reconciliation does not recreate erased content.

## Audit completeness

Create a policy matrix mapping Media actions to:

- MediaAsset/proof state;
- MediaAccessEvent when applicable;
- AuditEvent when materially administrative;
- AccessAuditLog when sensitive;
- IntegrationFailure/metrics/logs when operational.

No single record type should be used for all four purposes.

## Telemetry safety

Automated tests should reject telemetry containing:

- signed URL query strings;
- raw access tokens;
- provider credentials;
- raw file bytes;
- PHI;
- resume text;
- identity/license document contents;
- Agreement/contract text;
- malware scan raw payload when sensitive;
- unnecessary original filenames or exact user-agent/IP data outside approved hashed/minimized fields.

## Backfill/migration behavior

If session status, policy versioning, or cascade rules are migrated:

- provide deterministic backfill mapping;
- test partially processed existing records;
- test rollback/forward strategy where required;
- do not reinterpret historical proof to fit the new policy version;
- verify all seeded contexts resolve exactly one policy.

## Performance

- stream large objects;
- batch expiration/reconciliation with cursors;
- index `storageKey`, upload status/context, grant expiry/status, asset/status, and access-event lookup patterns;
- keep signed-access hot path bounded to current asset/grant/context decisions rather than loading full scan history;
- cap concurrency for CPU-heavy processing;
- measure queue age and provider latency through shared metrics.

---

# Phase Summary

| Phase | Name | Features |
| --- | --- | --- |
| 1 | Contracts and Secure Upload Intake | 01–02 |
| 2 | File Safety Pipeline and Ready Media Truth | 03–04 |
| 3 | Contextual Access and Short-Lived Delivery | 05–06 |
| 4 | Cross-Module Enforcement and Privacy Integration | 07–08 |
| 5 | Media Hardening and Production Verification | 09 |

**Total numbered Module features: 9**

### Parent CL-05 mapping

| Media feature | Parent CL-05 feature / milestone |
| --- | --- |
| 01–04 | CL-05 Feature 01 — Secure Upload to Ready MediaAsset |
| 05–06 | CL-05 Feature 02 — Contextual Media Access and Short-Lived Signed Delivery |
| 07 | CL-05 Feature 13 — Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification |
| 08 | CL-05 Feature 14 — Privacy Target Executors, Retention, and Provider Deletion |
| 09 | CL-05 Feature 15 — Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness |

The Cluster plan remains authoritative for when these slices occur relative to Digital Goods, Video, Booking, and other CL-05 work.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root `project-overview.md`.
2. Read root `architecture.md` and `code-standards.md`.
3. Read `context/shared/shared-operations.md` and verify every SH-ID used by the feature is still current.
4. Read CL-05 `architecture.md` and `build-plan.md`.
5. Read `media_file_access/module-architecture.md` and this plan.
6. Read the public-interface sections for every direct dependency used in this feature.
7. Confirm the prior numbered feature exit gate is green or the progress tracker records an approved exception.
8. Reinspect actual Prisma schema **and deployed migration/constraint state** for affected Media records.
9. Produce the required feature implementation specification below.
10. Implement only the current feature.
11. Run the exact unit/contract/integration/security/concurrency/provider tests required by the feature.
12. Verify cross-Module behavior through public interfaces rather than production direct-table access.
13. Update progress tracker and implementation evidence.
14. Update `module-architecture.md` only when a binding architectural decision legitimately changed or a Proposed Ruling was approved.
15. Update CL-05/root architecture only if the binding Cluster/root contract actually changed; implementation progress alone is not architecture.
16. Record unresolved risks instead of guessing.

---

# Required Feature Implementation Specification

Immediately before coding any numbered feature, the coding agent must produce a concise, feature-specific specification containing:

- **Feature:** number and name.
- **Objective:** one concrete result.
- **Observable result:** what can be tested/seen when done.
- **Cluster build-plan link:** parent CL-05 feature/milestone.
- **Dependencies:** prior Media feature gates, owner public interfaces, SH-IDs, schema/provider prerequisites.
- **In scope:** exact files/services/contracts/migrations/workers being added or changed.
- **Out of scope:** neighboring truth explicitly excluded.
- **Owned data affected:** Media models/enums/events/proof records only.
- **Public contracts:** commands/queries/events/executors introduced or changed.
- **Shared operations consumed:** SH-ID, owner, invocation, local policy, prohibited duplicate.
- **Permissions/compliance:** actor, authority, contextual decision, hold, Healthcare, sensitive audit, Privacy/Moderation where relevant.
- **Primary workflow:** numbered happy-path sequence.
- **Provider integration:** port, adapter, secrets, normalization, retries, reconciliation, or `none`.
- **Jobs/events:** durable work, idempotency key, retry/dead-letter, event/outbox behavior.
- **Idempotency/concurrency:** semantic command key, lock/resource key, transaction boundary, replay result.
- **Error behavior:** validation, denial, conflict, stale transition, provider failure, manual review.
- **Tests:** exact test files/categories/critical fixtures.
- **Acceptance criteria:** observable conditions.
- **Documentation updates:** architecture/ADR/shared registry/progress only when actually required.

Do **not** generate all nine implementation specifications in advance. Generate the specification immediately before the feature being implemented so it reflects the repository's actual current state.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed:** number/name.
- **Files added.**
- **Files changed.**
- **Database changes.**
- **Migrations:** name and what constraint/data change they perform.
- **Dependencies added/changed:** packages/provider SDKs and why.
- **Module public interfaces added/changed.**
- **Shared operations reused:** SH-IDs and concrete integration points.
- **Events/jobs added:** names, owner, idempotency/retry behavior.
- **Provider adapter changes.**
- **Tests added/changed:** unit, contract, DB/integration, authorization, security, privacy, concurrency, provider, E2E as applicable.
- **Commands run:** typecheck, lint, test targets, migration checks, build/E2E commands.
- **Manual/contract verification:** exact workflow and observed result.
- **Documentation updated.**
- **Assumptions:** only unavoidable implementation assumptions, clearly marked.
- **Known failures.**
- **Remaining risks.**
- **Deferred work:** must name the owning future feature/Module where known.
- **Exit-gate result:** pass/fail with evidence.

A feature is not complete merely because code compiles. Its exit gate must be demonstrably green.

---

# Final Module Quality Gate

Before `media_file_access` is treated as implementation-complete for the MVP, verify all of the following:

1. `MediaAsset` is the one canonical file/storage truth.
2. Contextual Modules retain the business meaning of Offering/Gig/Job/Message/profile/resume/Order/Agreement/digital attachments.
3. Media owns technical upload policy, validation, scan, processing, derivatives, generic Media grants, and signed object access only.
4. No neighboring Module owns or directly mutates Media lifecycle state.
5. No consumer duplicates R2 access, file validation, malware scanning, metadata scrub, private key generation, checksum logic, or generic Media signed URL generation.
6. SH-001/002/011/020/026/030/044/047/048/051/052/053/055/070/072/074/080/082–090/091/095–098/103/123/125 are consumed where applicable rather than copied.
7. Every scan-required policy fails closed.
8. `MediaAsset.ready` requires complete applicable proof and never means “business approved.”
9. A signed URL is never treated as durable entitlement truth.
10. MediaAccessGrant remains separate from AgreementAccessGrant, DigitalDownloadGrant, CourseVideoPlaybackGrant, SensitiveActionSession, and LocationReveal.
11. MediaAccessEvent, AccessAuditLog, AuditEvent, and IntegrationFailure remain separate evidence classes.
12. Privacy owns PrivacyRequest/DataErasureJob/DataErasureTarget/DataRetentionExemption orchestration.
13. Moderation owns legal/moderation decision truth; Media only executes file effects.
14. Healthcare owns healthcare readiness/access policy; Media only enforces returned decisions.
15. Search owns projection; Media uses SH-091 and never writes Typesense directly.
16. Notification owns delivery; Media only requests notifications when an approved trigger exists.
17. R2/provider state never replaces Media source truth.
18. Provider/worker retries are idempotent, bounded, correlated, observable, and dead-letter visible.
19. Database-backed concurrency prevents stale workers or grant races from resurrecting access.
20. Product deletion remains distinct from privacy erasure.
21. R2 bytes are deleted when an authorized Privacy instruction requires deletion and retention does not block it.
22. Access/security evidence survives or is anonymized according to approved retention policy rather than accidental cascade behavior.
23. Raw-original public exposure remains disabled by default unless architecture explicitly approves a context.
24. No sensitive payload, signed URL, token, provider secret, PHI, resume text, identity-document content, or contract text leaks to telemetry.
25. Production scanner selection is recorded for launch contexts requiring malware scan.
26. All Module feature exit gates pass.
27. The parent CL-05 integration and production-readiness gates that depend on Media also pass.
28. Remaining unresolved decisions are documented and do not require a coding agent to invent architecture during implementation.

