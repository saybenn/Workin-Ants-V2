# Scheduling, Media & Digital Delivery Build Plan

> **Cluster ID:** CL-05  
> **Cluster:** Scheduling, Media & Digital Delivery  
> **Companion architecture:** `architecture.md` in this Cluster context  
> **Project posture:** greenfield MVP architecture planning; current Prisma schema is executable schema evidence  
> **Modules:** `booking_calendar`, `video_session`, `media_file_access`, `digital_goods_access`

---

## Core Principle

Build CL-05 as a sequence of vertical, testable delivery slices while preserving the four Module ownership boundaries.

```text
usable / observable delivery behavior
→ owning Module application service
→ authoritative owner database state
→ owner public contracts
→ authorization / entitlement / compliance gates
→ provider or asynchronous effects through approved adapters
→ domain events / access evidence / audit / observability
→ tests
→ concrete exit gate
```

The Cluster is not built as a generic “delivery engine.” The implementation should make one real delivery behavior work end-to-end, then extend the next workflow using the same canonical shared operations and public interfaces.

A capability does not require artificial UI. Where user-facing UI is not yet appropriate, the slice must expose a real public interface, provider adapter, worker, admin/debug surface, or observable source-of-truth result that can be tested independently.

---

## Build Rules

- Follow root `project-overview.md`, root `architecture.md`, root `code-standards.md`, the Canonical Shared Operations Registry, and this Cluster architecture.
- Do not expand CL-05 into commerce, hiring, privacy orchestration, moderation adjudication, healthcare policy, search ownership, notification delivery, or subscription management.
- Do not redesign Module ownership in the build plan.
- Reuse canonical SH-### operations. If a required shared operation is not yet implemented, depend on its interface/test double; do not create a CL-05-local replacement.
- Every mutation validates input, resolves the authenticated/system actor, and enforces authorization server-side.
- Every cross-Module read uses the source Module’s public interface/owner-facts contract rather than a new direct cross-domain repository.
- Every external provider is isolated behind the provider-owning Module’s port/adapter.
- Provider payloads never become Workin Ants domain types.
- Every provider callback is signature-verified and provider-event-deduplicated before side effects.
- Every asynchronous operation is durable, idempotent, retry-classified, correlated, observable, and dead-letter visible.
- Every source-of-truth transition is performed by its owning Module and appends required domain evidence.
- AuditEvent/AccessAuditLog and Observability records supplement but never replace owner lifecycle/access records.
- Privacy orchestration remains Privacy-owned; CL-05 implements owner target executors only.
- ComplianceHold remains the reusable stop sign; no generic local blocked-state system may be introduced.
- Track Subscription & Entitlement remains commercial policy truth; no local premium/priority/live-streaming booleans may become current policy truth.
- Media owns file mechanics and signed object access; contextual Modules own business entitlement.
- Booking owns paid service scheduling; JobInterview remains CL-06 hiring scheduling.
- Search remains a projection and is updated only through Search public interfaces.
- Every numbered feature ends with automated tests, workflow verification, documentation/progress update, and a concrete exit gate.
- Do not start the next numbered feature until the previous exit gate passes or the progress tracker explicitly records an approved exception.
- Unresolved architecture must not be silently invented. Where a feature reaches an unresolved decision, implement only the noncontroversial interface/mechanism and record the block.

---

## Dependencies and Preconditions

### Root/platform prerequisites

CL-05 assumes the root platform can provide or stub these capabilities through the canonical interfaces:

- PostgreSQL/Prisma migrations and transactions;
- authentication/session actor context;
- Role / Authority decision interface;
- runtime validation;
- request/correlation context;
- transactional outbox/domain event publication;
- durable queue/worker execution;
- idempotency and locking primitives;
- AuditEvent/AccessAuditLog interfaces;
- structured logging/metrics/IntegrationFailure;
- Notification request interface;
- secret management and cryptography primitives.

If those foundations are not implemented when CL-05 begins, use contract fakes in tests and build against the canonical interface. CL-05 must not become the temporary owner of those systems.

### Shared-operation prerequisites

Highest-leverage required operations include:

- SH-001 / SH-002 actor + authorization;
- SH-004 CustomerProfile resolver;
- SH-005 / SH-006 entitlement lookup/usage;
- SH-007 / SH-008 consent proof;
- SH-011 ComplianceHold;
- SH-020 healthcare readiness;
- SH-025 Order entitlement;
- SH-026 contextual resource access;
- SH-027 Location reveal;
- SH-029 / SH-030 audit;
- SH-044–SH-053 reliability/event/workflow primitives;
- SH-055 / SH-057 / SH-058 expiration/counter/interval concurrency;
- SH-059–SH-062 provider callback/reconciliation primitives;
- SH-064 / SH-067 / SH-068 provider connection/calendar/video ports;
- SH-072 / SH-074 / SH-075 cryptography;
- SH-082–SH-090 Media/grant operations;
- SH-091 Search refresh;
- SH-095–SH-097 Privacy target protocol;
- SH-103 Moderation execution;
- SH-109 external-decision snapshot;
- SH-113 Messaging thread;
- SH-123 target validation;
- SH-125 domain access evidence.

### Upstream Cluster dependencies

- **CL-01**: User/auth, authority, CustomerProfile, consent, track entitlement.
- **CL-03**: ProfessionalProfile, Offering/Product/Course facts, healthcare readiness.
- **CL-04**: Order entitlement and Agreement readiness.
- **CL-06**: JobInterview/participant facts for interview video.
- **CL-07**: Messaging/Notification public interfaces.
- **CL-08**: Location Safety and Privacy orchestration.
- **CL-09**: ComplianceHold, Moderation, Audit, Observability.
- **CL-02**: Search projection refresh interface.

### Schema prerequisites

The current Prisma schema already evidences CL-05 records. Before each feature, inspect the repository migrations and database constraints rather than recreating models blindly.

Important database-level requirements that may require explicit SQL migrations even when models exist in Prisma:

- atomic booking interval conflict prevention / exclusion constraint;
- unique provider-event dedupe keys;
- idempotency uniqueness;
- grant/asset indexes needed by expiration/access workers;
- safe cascade behavior and destructive-migration review.

### Provider posture

Providers may be stubbed behind ports until the provider feature is reached.

- Cloudflare R2: current object-storage target.
- Cronofy: current calendar provider target.
- Mux: current on-demand course-video target.
- Live video: provider-neutral port required; Daily.co is the current Proposed MVP adapter pending the architecture decision.
- Malware scanning: adapter required; production provider remains unresolved.

Provider uncertainty must not block owner domain records, contracts, test adapters, or manual/non-provider vertical slices.

---

# Phase 1 — Safe Media Substrate

## 01 Secure Upload to Ready MediaAsset

Create the first real CL-05 vertical slice: an authorized user can upload a file into quarantine and observe it become a safe `MediaAsset.ready` or a specific rejection/failure state.

### Objective

Establish Media / File Access as the single file-safety and object-storage owner for all later CL-05 delivery workflows.

### User-visible / Observable Result

A reusable upload surface or internal development/admin test surface can:

- request an upload for a supported `MediaUploadContext`;
- upload to a private/quarantine object;
- display validation/scanning/processing progress;
- display `ready`, `rejected`, or `failed` result with safe reason codes;
- retrieve MediaAsset metadata without exposing the raw storage key to unauthorized callers.

### Owning Module(s)

- **Primary:** Media / File Access.
- No other Module owns or changes MediaAsset technical readiness.

### Dependencies

- root auth/authority/runtime validation;
- Prisma/Postgres;
- durable queue;
- Cloudflare R2 adapter or test object-store adapter;
- active seeded MediaUploadPolicy for at least one low-risk and one sensitive test context;
- scanner test adapter if production scanner is not selected.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity & Access.** Use to establish uploader. Local policy: MediaUploadContext and policy selection. Do not build `mediaAuth.ts`.
- **SH-002 `authorizeResourceAction` — Role / Authority.** Use before upload-session creation. Local policy: permitted upload action/context. Do not build a Media permission engine.
- **SH-011 `evaluateComplianceHold` — Compliance Hold.** Use where upload/processing action is hold-sensitive. Local policy: map block to rejected/paused action. Do not add generic `isBlocked` fields.
- **SH-044 `executeIdempotentCommand` — platform.** Use for session completion/promotion retries. Local policy: session/object semantic key. Do not build Media-only idempotency storage.
- **SH-047 / SH-048 — shared queue/retry.** Use for validation/scan/processing. Local policy: which failures are retryable. Do not create a custom Media queue framework.
- **SH-072 `hashCanonicalPayload` / SH-086 `calculateChecksum` — security primitives.** Use for bytes/proof. Local policy: what Media checksum proves. Do not add local SHA helpers.
- **SH-082 `validateUploadedFile` — Media.** Canonical file validation pipeline. Do not duplicate validators in future consumer Modules.
- **SH-083 `scanFileForMalware` — Media.** Canonical scanner operation. Required policies fail closed.
- **SH-084 `scrubFileMetadata` — Media.** Use for contexts requiring EXIF/GPS/PDF scrubbing.
- **SH-085 `generatePrivateObjectKey` — Media/storage primitive.** Original file name never becomes object key.
- **SH-032 / SH-034 / SH-037 — request context, telemetry sanitization, integration failure.** Use for all storage/scanner/processing work.

### Data / Schema

Implement/use:

- `MediaUploadPolicy`, `MediaUploadPolicyStatus`;
- `MediaUploadSession`;
- `MediaAsset`, `MediaAssetStatus`;
- `MediaValidationResult`, `MediaValidationStatus`;
- `MediaScanResult`, `MediaScanStatus`;
- `MediaProcessingResult`, `MediaProcessingStatus`, `MediaProcessingActionType`;
- Media upload/storage/rejection enums.

Verify:

- `MediaAsset.storageKey` uniqueness;
- indexes for uploader/status/context;
- quarantine and ready/private bucket policy;
- no public application directory storage.

Do not move contextual business joins in this feature.

### Public Interfaces

Complete or introduce:

- `createMediaUploadSession`;
- `completeMediaUpload`;
- `getMediaReadiness`;
- Media-owned object-storage and scanner/processor ports.

### Logic

1. Resolve actor and authorize upload context.
2. Select one active MediaUploadPolicy.
3. Validate declared size/extension as an early convenience check, but do not trust it as final proof.
4. Generate opaque private/quarantine object key.
5. Create MediaUploadSession and upload instruction.
6. After object completion, read/inspect bytes server-side.
7. Validate size, claimed MIME, detected MIME/binary signature, extension, encrypted/archive rules, and context.
8. Scan when policy requires it.
9. Apply required metadata processing/derivatives.
10. Persist proof records and checksums.
11. Transition MediaAsset to `ready` only after every required gate succeeds.
12. Reject/fail closed with explicit safe reason when required safety work cannot complete.

### UI / Administrative Surface

Minimum:

- reusable upload control;
- progress/state view;
- safe rejection message;
- development/admin policy/result inspector.

Do not build full Marketplace/Candidate/Messaging upload UIs here.

### Authorization / Compliance

- sensitive upload contexts require private/sensitive/healthcare bucket class as policy dictates;
- healthcare policy is consumed, not recreated;
- raw original file metadata must not be exposed broadly;
- active ComplianceHold must be honored when applicable;
- scan-required policy fails closed.

### Events / Jobs / Integrations

- R2 private/quarantine upload;
- background validation/scan/process/promotion jobs;
- provider failures record IntegrationFailure;
- publish `media.ready` / `media.rejected`-style owner event only after Module event names are specified;
- no Search indexing in this feature.

### Failure Behavior

- upload abandoned: session becomes cleanable/expired according to Media policy;
- object missing: retry lookup then fail with provider error;
- binary mismatch/encrypted forbidden archive/malware: reject, do not retry as transient;
- scanner unavailable when required: remain quarantined/failed, never ready;
- processor timeout: retry with backoff; terminal failure remains non-ready;
- duplicate completion: return original semantic result.

### Tests

- unit: policy selection, validation matrix, rejection mapping;
- integration: R2/test-store lifecycle and database state;
- provider: storage/scanner adapter result translation;
- idempotency: duplicate completion does not create duplicate assets/proofs;
- security: browser MIME mismatch, oversized file, malicious extension, filename/path attack, EXIF/GPS fixture;
- privacy: sensitive metadata not logged;
- E2E: upload → ready and upload → rejected.

### Out of Scope

- contextual attachment lifecycle;
- paid download entitlement;
- streaming provider ingest;
- public search projection;
- general moderation decisioning;
- production malware-provider selection if still unresolved.

### Exit Gate

- a supported upload reaches `MediaAsset.ready` only after required validation/scan/process proofs exist;
- an invalid/infected fixture never becomes ready;
- original filename is not used as object key;
- private/quarantine objects cannot be fetched anonymously;
- duplicate completion creates one semantic asset/result;
- queue/provider failures are visible in IntegrationFailure/telemetry without changing source truth incorrectly;
- unit/integration/security/E2E tests pass;
- no contextual Module contains duplicated file-validation/storage logic.

---

## 02 Contextual Media Access and Short-Lived Signed Delivery

Allow an authorized contextual consumer to obtain a short-lived private file URL without transferring business entitlement to Media.

### Objective

Prove the core rule: contextual owner decides **whether** access is permitted; Media decides whether the file is safe/deliverable and **how** temporary object access is issued.

### User-visible / Observable Result

A test contextual resource can request a private file and receive either:

- a short-lived signed URL with explicit expiry; or
- a safe denial reason.

MediaAccessGrant and MediaAccessEvent show the technical access lifecycle, and sensitive access is separately visible in AccessAuditLog when required.

### Owning Module(s)

- **Media / File Access:** MediaAccessGrant, signed URL, MediaAccessEvent.
- **Context owner:** business entitlement decision.
- **Audit / Event Ledger:** AccessAuditLog.

### Dependencies

- Feature 01;
- SH-026 contextual access decision contract from at least one test/upstream owner;
- Audit public interface;
- secure token/hash primitives.

### Shared Operations Used

- SH-001, SH-002 — actor/authority.
- **SH-026 `authorizeContextualResourceAccess` — context owner.** Media receives the decision; it must not reconstruct Order/resume/message/Agreement policy.
- **SH-020 `evaluateHealthcareReadiness` — Healthcare.** Use for healthcare-sensitive file access.
- SH-011 — hold gate.
- **SH-030 `recordSensitiveAccess` — Audit.** Log required allowed/denied sensitive attempts. Do not use MediaAccessEvent as the only generic audit proof.
- **SH-074 `generateSecureToken` — security.** Use where tokenized grant binding is needed.
- **SH-087 `issueSignedMediaUrl` — Media.** Central presign operation; contextual Modules must never presign directly.
- **SH-088 `manageTemporaryAccessGrant` — shared grant mechanics.** Apply to MediaAccessGrant only; do not merge grant schemas.
- **SH-125 `recordDomainAccessEvent` — Media.** Append MediaAccessEvent.
- SH-044 / SH-055 — idempotent issuance and expiry sweep.
- SH-032 / SH-034 / SH-037 — operational context/redaction/failure.

### Data / Schema

- `MediaAccessGrant` and `MediaAccessGrantStatus`;
- `MediaAccessEvent` and `MediaAccessEventType`;
- `MediaAsset.dataSensitivity`, status, freeze/erasure fields;
- no new contextual entitlement table.

### Public Interfaces

- `requestMediaAccess`;
- SH-087 `issueSignedMediaUrl` implementation;
- `revokeMediaAccessGrant` owner command using SH-089 pattern.

### Logic

1. Receive owner-issued contextual authorization decision.
2. Confirm actor/resource consistency and safe target reference.
3. Evaluate applicable hold/healthcare policy.
4. Confirm MediaAsset is `ready`, not frozen, not erased/deleted, and visibility/action is permitted.
5. Create or validate bounded MediaAccessGrant.
6. Issue presigned URL only server-side.
7. Store hash/evidence, never the reusable URL as durable truth.
8. Append MediaAccessEvent.
9. Append AccessAuditLog for sensitive actions.

### UI / Administrative Surface

- reusable private-file open/download action;
- expired/denied states;
- admin/developer grant/access-event inspector.

### Authorization / Compliance

- contextual decision is mandatory;
- healthcare and highly sensitive files honor Healthcare decision;
- sensitive files default to short TTL policy target (current evidence: 15 minutes) unless approved policy states otherwise;
- exact provider object key is not exposed in client APIs;
- step-up is invoked only where root security policy requires it.

### Events / Jobs / Integrations

- R2 presign through Media adapter;
- grant expiration worker;
- revocation command hook;
- IntegrationFailure on storage signing/provider failure;
- optional Notification request only for user-relevant denial/revocation policy, not on every download.

### Failure Behavior

- contextual denial: no grant or URL;
- asset non-ready/frozen/erased: fail closed;
- signing provider outage: preserve grant truth as appropriate but return temporary delivery failure and record IntegrationFailure;
- expired/revoked grant: deny, append domain/sensitive evidence if policy requires;
- duplicate issuance request: idempotent result or a new credential only according to Media policy, never duplicate entitlement truth.

### Tests

- contract: owner allow/deny decisions;
- unit: Media readiness/freeze/expiry rules;
- integration: signed URL TTL and grant persistence;
- healthcare/sensitive access audit tests;
- idempotency/expiry race tests;
- E2E: allow → signed access; deny → no URL.

### Out of Scope

- DigitalDownloadGrant;
- CourseVideoPlaybackGrant;
- Agreement/resume/message policy;
- permanent public URLs.

### Exit Gate

- a contextual owner allow decision can produce bounded private access;
- a denial or unsafe MediaAsset can never produce a signed URL;
- signed URL and secrets are absent from durable logs/domain truth;
- MediaAccessEvent and required AccessAuditLog are separately present;
- contextual test owner can be swapped without changing Media business logic;
- all access/expiry/security tests pass.

---

# Phase 2 — Digital Goods and Course Delivery

## 03 Digital Goods Policy and Versioned Terms Evidence

Create versioned delivery/license/refund policy records and contextual acceptance proof without taking over generic Consent or Agreement truth.

### Objective

Make a digital Offering capable of carrying explicit delivery policy and producing provable per-user/per-order acceptance evidence before access is granted.

### User-visible / Observable Result

A seller/admin can configure a digital-goods policy for an eligible Offering. A buyer can be shown the configured versioned disclosure and, in test/dev mode using approved placeholder content, accept it. The system stores the exact versions/hash/context used.

### Owning Module(s)

- **Digital Goods Access:** DigitalGoodsPolicy and DigitalGoodsTermsAcceptance.
- **Consent & Disclosure:** generic ConsentLog/version proof.
- **Marketplace Supply:** Offering lifecycle/ownership.

### Dependencies

- Offering owner public facts/target-validation interface;
- Consent shared operations;
- approved test policy data;
- legal-gated production content remains a dependency for production enablement, not schema work.

### Shared Operations Used

- SH-001 / SH-002 — actor and seller/admin authority.
- **SH-007 `recordConsentProof` / SH-008 `queryConsentProof` — Consent.** Use when generic consent proof is required. Local Digital Goods policy stays contextual.
- **SH-072 `hashCanonicalPayload` — security.** Hash accepted text/version snapshot. Do not create `acceptanceHash.ts`.
- **SH-123 `validateOwnedTargetReference` — Offering owner.** Confirm eligible Offering reference without direct Marketplace repository access.
- SH-029 — audit material admin policy changes where root audit policy requires.
- SH-044 — idempotent acceptance command.

### Data / Schema

- `DigitalGoodsPolicy`;
- `DigitalGoodsLicenseType`;
- `DigitalGoodsRefundPolicyType`;
- `DigitalGoodsTermsAcceptance`;
- `DigitalGoodsTermsAcceptanceStatus` (`accepted`, `revoked`, `voided`).

Do not create or fork `ConsentType` or `ConsentLog` in Digital Goods.

### Public Interfaces

- `getDigitalGoodsPolicy`;
- `upsertDigitalGoodsPolicy` or version-safe policy command as Module architecture specifies;
- `recordDigitalGoodsTermsAcceptance`;
- `getDigitalGoodsTermsAcceptance`.

### Logic

- require valid Offering ownership/authority;
- store policy versions and defaults;
- acceptance records freeze terms/refund/license versions and accepted text hash;
- link ConsentLog when generic consent is part of the action;
- revocation/voiding rules remain contextual and must be explicit;
- changing policy version must not rewrite historical acceptance proof.

### UI / Administrative Surface

- seller/admin digital-policy settings;
- buyer disclosure/acceptance surface;
- version display;
- clear legal-gate banner in non-production/test policy configurations.

### Authorization / Compliance

- do not invent final legal language;
- do not imply ConsentLog alone grants access;
- production activation of legal-gated terms requires approved policy versions/content;
- general electronic-signature/Agreement consent remains owned by its proper owner.

### Events / Jobs / Integrations

- no external provider required;
- publish policy/acceptance owner events where later workflows depend on them;
- Notification is optional only for material policy change after product policy is specified.

### Failure Behavior

- missing/ineligible Offering: reject;
- stale policy version at acceptance: reject and re-present current approved version;
- duplicate acceptance idempotency key: replay result;
- legal content not approved for production: product access remains gated/feature-flagged; do not fabricate terms.

### Tests

- unit: policy/version invariants;
- contract: Offering target/ownership;
- consent integration: proof linked without duplicate Consent tables;
- acceptance hash/version immutability;
- authorization tests;
- E2E: policy display → acceptance → evidence.

### Out of Scope

- paid file grant;
- tax calculation;
- Agreement signature flow;
- child-directed legal adjudication;
- actual legal copy drafting.

### Exit Gate

- historical acceptance evidence is immutable and version-specific;
- Digital Goods does not own/fork ConsentType/ConsentLog;
- stale/unauthorized acceptance is rejected;
- production legal gate is explicit and cannot be bypassed by missing content;
- policy/acceptance tests pass.

---

## 04 Purchased Digital Download Grant and Controlled Download

Deliver a paid digital file from an authoritative Order through DigitalDownloadGrant and Media signed access.

### Objective

Complete the core paid-download journey without treating MediaAsset, R2, ProductDetails, or payment-provider state as entitlement.

### User-visible / Observable Result

A buyer with an eligible Order can see a purchased download, receive an expiring grant, and download through a short-lived link. A buyer without entitlement, with an expired/revoked grant, or above the max-download limit is denied with a stable reason.

### Owning Module(s)

- **Digital Goods Access:** DigitalDownloadAsset, Grant, Event and access policy.
- **Transaction / Order:** purchase entitlement.
- **Media:** file readiness and signed object delivery.

### Dependencies

- Features 01–03;
- Order SH-025 interface;
- CustomerProfile resolver where buyer actor is required;
- secure Media access interface.

### Shared Operations Used

- SH-001 / SH-002 / SH-004 — actor/authority/customer.
- **SH-025 `authorizeOrderEntitlement` — Order.** Mandatory for normal purchased access. Do not read Stripe or local `paid` boolean.
- **SH-090 `attachValidatedMedia` — Media/context contract.** Register only ready MediaAsset.
- **SH-074 `generateSecureToken` — shared security.** Grant secret material if needed.
- **SH-088 `manageTemporaryAccessGrant` / SH-089 revoke pattern.** Reuse mechanics, keep DigitalDownloadGrant separate.
- **SH-057 `consumeCounterAtomically` — DB primitive.** Enforce max downloads safely.
- **SH-087 `issueSignedMediaUrl` — Media.** Digital Goods does not presign R2 itself.
- **SH-125 `recordDomainAccessEvent` — Digital Goods.** Append DigitalDownloadEvent.
- SH-030 — sensitive access where policy requires.
- SH-044 / SH-055 — idempotent grant issuance and expiry worker.

### Data / Schema

- `DigitalDownloadAsset`, `DigitalDownloadAssetStatus`, `DigitalStorageProvider`;
- `DigitalDownloadGrant`, `DigitalDownloadGrantStatus`;
- `DigitalDownloadEvent`, `DigitalDownloadEventType`;
- indexes on asset/status, user, order, expiry, token hash;
- default TTL from policy/schema: 24 hours unless approved DigitalGoodsPolicy overrides.

### Public Interfaces

- `registerDigitalDownloadAsset`;
- `issueDigitalDownloadGrant`;
- `listUserDigitalDownloads` read model without copying Order truth;
- `issueDigitalDownloadAccess`;
- `revokeDigitalDownloadGrant(s)`.

### Logic

1. Validate DigitalDownloadAsset belongs to eligible Offering context and backing MediaAsset is ready.
2. Resolve buyer/actor and Order entitlement for the exact item/action.
3. Verify required DigitalGoodsTermsAcceptance.
4. Create idempotent grant with TTL and max-download policy.
5. On access, lock/atomically validate status/expiry/count.
6. Ask Media for contextual file access and signed URL.
7. Increment/download usage at the precise policy-defined point.
8. Append DigitalDownloadEvent independently from MediaAccessEvent.
9. Revoke on authoritative refund/moderation/privacy/security instructions later.

### UI / Administrative Surface

- buyer “My downloads” or purchase-delivery surface;
- download state/expiry/remaining uses;
- seller/admin digital asset readiness/status;
- support-safe event view without exposing tokens/URLs.

### Authorization / Compliance

- Order entitlement mandatory for normal purchase flow;
- `ProductDetails.fileAssetId` never authorizes access;
- no permanent public URLs;
- terms acceptance version must be satisfied when policy requires;
- access denial does not expose provider/object details.

### Events / Jobs / Integrations

- grant expiration worker;
- Media signed URL call;
- domain event on grant/revocation if downstream needs it;
- no direct R2 client in Digital Goods;
- no Stripe provider call.

### Failure Behavior

- Order denied/refunded/not qualifying: deny and no new grant;
- asset disabled/non-ready: deny;
- grant exhausted: atomic deny without race overrun;
- Media signing outage: return temporary failure; do not incorrectly consume access unless policy says issuance itself counts;
- duplicate grant request: replay existing semantic grant;
- optional null-order access remains out of scope until its alternate basis is ruled.

### Tests

- Order contract allow/deny/refund states;
- grant lifecycle and 24h default;
- concurrent max-download enforcement;
- Media contract allow/sign failure;
- duplicate grant issuance;
- access event separation;
- E2E paid Order → grant → download and refunded Order → denied/revoked.

### Out of Scope

- complimentary/admin/library access without Order;
- streaming video;
- tax/refund adjudication;
- legal-policy text creation.

### Exit Gate

- only an eligible Order can produce normal purchased access;
- a ready DigitalDownloadAsset still cannot be fetched without a valid grant;
- max-download race test cannot exceed configured maximum;
- DigitalDownloadEvent and MediaAccessEvent remain separate;
- R2 access exists only through Media;
- expired/revoked/refunded paths deny access;
- all contract/concurrency/E2E tests pass.

---

## 05 Child-Directed Controls and Course Accessibility Tracking

Implement the schema-backed control/evidence layer for child-directed digital products and course accessibility assets without inventing legal policy.

### Objective

Make Digital Goods capable of recording declarations, applying defined product-surface privacy controls, and tracking captions/transcripts/accessibility assets separately from raw video state.

### User-visible / Observable Result

A seller/admin can:

- record a child-directed declaration;
- see when admin review is required;
- observe configured tracking/ads/comments/analytics controls;
- attach and track captions/transcripts/audio-description/descriptive assets;
- see accessibility asset readiness independently from CourseVideoAsset readiness.

### Owning Module(s)

- **Digital Goods Access:** declarations, MinorPrivacyControl, CourseAccessibilityAsset.
- **Media:** backing file mechanics.
- **Marketplace Supply/Search/Moderation:** consume resulting public-readiness effects but retain their truth.

### Dependencies

- Feature 01;
- Offering/Course owner target interface;
- Media attach/readiness;
- admin authorization;
- legal policy/criteria may remain feature-flagged.

### Shared Operations Used

- SH-001 / SH-002 — seller/admin actor/authority.
- SH-011 — ComplianceHold where review/activation actions are hold-sensitive.
- SH-090 — attach validated Media for accessibility assets.
- **SH-091 `requestSearchProjectionRefresh` — Search.** Request refresh when approved controls/readiness affect public projection. Do not call Typesense.
- SH-029 — audit admin review/control changes.
- SH-041 — notification for explicit review outcomes if product policy requires.
- SH-123 — validate Offering/Course target references.

### Data / Schema

- `ChildDirectedContentDeclaration`, `ChildDirectedDeclarationStatus`;
- `MinorPrivacyControl`;
- `CourseAccessibilityAsset`, `AccessibilityAssetType`, `AccessibilityAssetStatus`;
- references to Offering/CourseVideoAsset/MediaAsset remain cross-owner references.

### Public Interfaces

- `declareChildDirectedContent`;
- `reviewChildDirectedDeclaration`;
- `getMinorPrivacyControls`;
- `registerCourseAccessibilityAsset`;
- `updateAccessibilityAssetState` only through Digital Goods owner logic.

### Logic

- declaration creates versioned/dated owner evidence;
- child-directed declaration may map to explicit product-surface controls already represented by schema;
- admin-review-required state prevents unsupported automatic approval;
- backing files must be Media-ready;
- accessibility record status is independent from video provider status;
- public readiness change requests Search refresh rather than direct indexing.

### UI / Administrative Surface

- declaration form/status;
- admin review queue/view if root admin surface exists;
- control summary;
- captions/transcript/accessibility list and readiness state.

### Authorization / Compliance

- no automated legal conclusion beyond approved rule configuration;
- do not replace general platform age gate;
- do not claim legal compliance merely because flags are set;
- production criteria/waiver policy remain legal-gated until approved.

### Events / Jobs / Integrations

- Media upload/processing for accessibility files;
- optional Search refresh and Notification requests;
- no new external child-privacy provider.

### Failure Behavior

- uncertain declaration requiring policy decision → `admin_review_required`, not silent approval;
- Media non-ready → accessibility asset cannot become ready;
- Search failure does not roll back Digital Goods truth; record operational failure in Search owner path.

### Tests

- lifecycle transitions for declaration and accessibility asset;
- authorization/admin review;
- Media readiness contract;
- Search request contract;
- legal-gate test preventing unapproved automatic state.

### Out of Scope

- final COPPA/legal interpretation;
- global cookie/advertising infrastructure implementation;
- CourseVideoAsset streaming lifecycle;
- general UI accessibility standard.

### Exit Gate

- declarations and controls are explicit source records, not loose booleans on Offering/User;
- accessibility assets remain separate from CourseVideoAsset and MediaAsset state;
- uncertain/legal-gated cases cannot auto-approve;
- Search is notified only through SH-091;
- tests pass with no invented legal text/rules.

---

## 06 Course Video Ingest and Signed Playback

Turn a safe raw course MediaAsset into a Video-owned streaming asset and provide Order-gated, short-lived playback.

### Objective

Complete the on-demand course delivery path using Video Session for Mux/provider state and signed playback while preserving Digital Goods commercial policy and Order purchase truth.

### User-visible / Observable Result

A course creator/admin can register a ready source video and observe processing to `CourseVideoAsset.ready` or failure. An entitled buyer can play the course through a short-lived signed credential; a non-entitled/expired/revoked user cannot.

### Owning Module(s)

- **Video Session:** CourseVideoAsset, CourseVideoPlaybackGrant/Event, ProcessedVideoProviderEvent.
- **Media:** raw source MediaAsset.
- **Order:** purchase entitlement.
- **Digital Goods:** product/course access terms and accessibility policy.

### Dependencies

- Features 01–03 and preferably Feature 05 for accessibility metadata integration;
- Mux adapter/test adapter;
- provider webhook endpoint foundation;
- Order and Healthcare public interfaces.

### Shared Operations Used

- SH-001 / SH-002 — actor and creator/admin permission.
- SH-025 — Order playback entitlement.
- SH-020 — healthcare readiness if the content/context is in a healthcare lane.
- SH-026 — contextual access where needed.
- SH-044 / SH-047 / SH-048 — idempotent ingest and durable provider work.
- **SH-059 / SH-060 / SH-061 — webhook verification, video-owner dedupe, provider translation.** `ProcessedVideoProviderEvent` remains Video truth.
- **SH-062 `reconcileProviderState` — Video.** Repair missed Mux callbacks safely.
- **SH-068 `invokeVideoProvider` — Video.** Mux adapter is only reachable through Video-owned port.
- SH-074 / SH-088 / SH-089 — secure playback token/grant mechanics.
- SH-125 / SH-030 — CourseVideoPlaybackEvent and required sensitive audit.
- SH-070 — provider resource deletion when authorized by Privacy/Moderation later.
- SH-032 / SH-034 / SH-037 — provider telemetry/failure.

### Data / Schema

- `CourseVideoAsset`, `CourseVideoAssetStatus`, `CourseVideoProvider`, `CourseVideoPlaybackPolicy`;
- `CourseVideoPlaybackGrant`, status;
- `CourseVideoPlaybackEvent`, event type;
- `ProcessedVideoProviderEvent`, provider/status;
- source MediaAsset relation;
- default signed playback TTL: 3600 seconds / 60 minutes from current schema.

### Public Interfaces

- `registerCourseVideoSource`;
- `getCourseVideoProcessingStatus`;
- `issueCoursePlaybackGrant`;
- `issueCoursePlaybackCredential`;
- `applyVideoProviderEvent`;
- `reconcileCourseVideoProviderState`.

### Logic

- accept only ready permitted source MediaAsset;
- create Video-owned asset before/with idempotent provider ingest request;
- minimize provider payload;
- treat provider status as input, translate to canonical Video status;
- verify/dedupe webhook before update;
- playback requires Video asset ready + Order/context entitlement + applicable policy/holds/healthcare;
- issue short-lived signed playback credential; do not store raw reusable URL;
- append playback events separately from Audit.

### UI / Administrative Surface

- creator/admin processing status and failure state;
- buyer course player state: loading, not entitled, access expired, provider unavailable;
- support-safe provider/reconciliation view without secrets.

### Authorization / Compliance

- no public raw `.mp4` URL;
- raw MediaAsset stays private;
- Digital Goods policy/terms and Order entitlement remain external truth;
- healthcare-sensitive content uses approved provider/data boundary;
- live-streaming track entitlement does not automatically grant paid course playback unless its definition explicitly says so.

### Events / Jobs / Integrations

- Mux ingest API;
- Mux webhook;
- processing/reconciliation worker;
- grant expiration;
- provider deletion command hook;
- Notification request for user-relevant processing/access outcomes only as specified.

### Failure Behavior

- Mux timeout: retry idempotently;
- unknown provider status: fail safe and surface operational failure;
- duplicate webhook: ignored via ProcessedVideoProviderEvent;
- missing callback: reconciliation repairs/flags;
- Order denied: no grant;
- expired/revoked grant: no playback credential;
- optional null-order access remains deferred.

### Tests

- source Media readiness contract;
- adapter mapping/webhook signature/dedupe;
- idempotent ingest;
- provider reconciliation;
- Order allow/deny/refund;
- grant expiry/revocation;
- token/secret persistence tests;
- E2E source → processing → ready → entitled playback.

### Out of Scope

- live Booking/Interview video;
- downloadable raw video;
- alternate streaming providers beyond adapter compatibility;
- complimentary/library playback without approved alternate entitlement.

### Exit Gate

- ready Media source produces one Video-owned provider asset through the adapter;
- duplicate ingest/webhooks cannot duplicate effects;
- provider state cannot directly overwrite domain state without translation;
- entitled buyer receives only short-lived playback access;
- non-entitled/refunded/expired path receives no credential;
- raw source/public URL leakage tests pass;
- reconciliation can detect a missed provider transition.

---

# Phase 3 — Conflict-Free Scheduling and Booking Delivery

## 07 Professional Availability, Slot Search, and Atomic Booking Holds

Build manual availability and conflict-free temporary reservations before external calendar integration.

### Objective

Allow a buyer to see bookable service slots and atomically reserve one while checkout/agreement work continues.

### User-visible / Observable Result

A professional can configure recurring availability. A buyer can view UTC-backed slots in their display timezone, select one, and receive a temporary BookingHold. A concurrent request for the same prohibited interval receives a clean `slot_unavailable` conflict.

### Owning Module(s)

- **Booking & Calendar:** AvailabilityRule, BookingHold, BookingSlotLock.
- Track Entitlement owns priority scheduling decision.

### Dependencies

- ProfessionalProfile owner facts;
- CustomerProfile resolver;
- Track Entitlement interface;
- Postgres transaction/locking support;
- no calendar provider required yet.

### Shared Operations Used

- SH-001 / SH-002 / SH-004 — actor/authority/customer.
- SH-005 — priority scheduling decision if applicable.
- SH-006 — metered priority usage only when the defined business event actually counts.
- **SH-058 `acquireIntervalLock` — Booking policy over Postgres.** Do not use in-memory mutexes.
- SH-044 — idempotent hold creation.
- SH-051 — aggregate/resource lock where needed.
- SH-055 — hold/lock expiry sweeps.
- **SH-109 `snapshotExternalDecision` — Booking.** Snapshot priority effect/grant reference when applied.
- SH-123 — Professional/Order target validation as needed.
- SH-032 / SH-037 — correlation/failure.

### Data / Schema

- `AvailabilityRule`, source enum;
- `BookingHold`, status;
- `BookingSlotLock`, status;
- priority snapshot fields already present;
- verify indexes;
- inspect/add database-level overlap exclusion constraint or equivalent atomic conflict enforcement if absent from migrations.

### Public Interfaces

- `upsertAvailabilityRule`;
- `listBookableSlots`;
- `createBookingHold`;
- `releaseBookingHold`;
- expiration owner command.

### Logic

- availability recurrence is interpreted in IANA timezone but emitted/stored as UTC instants;
- current BusyWindow table may be empty/manual at this phase;
- slot search subtracts existing active locks/Bookings and known BusyWindows;
- hold creation always rechecks server-side;
- interval reservation and hold/lock persistence are one atomic effect;
- priority entitlement may alter ranking/selection behavior only according to an approved Booking policy, never by bypassing overlap rules;
- hold/lock expire deterministically.

### UI / Administrative Surface

- professional availability editor;
- buyer slot picker;
- hold countdown/expiration state;
- clear conflict/slot-unavailable feedback.

### Authorization / Compliance

- only authorized professional may manage their availability;
- buyer uses CustomerProfile context;
- no exact private calendar metadata is present yet;
- priority entitlement is external truth and historical effect is snapshotted.

### Events / Jobs / Integrations

- hold/lock expiration job;
- optional hold-created/expired domain event;
- no Cronofy call;
- no Video room creation.

### Failure Behavior

- concurrent conflict: clean conflict, no partial hold;
- stale slot list: server recheck wins;
- duplicate request: replay same semantic hold;
- expired hold cannot convert later;
- queue delay in expiry does not make an already past `expiresAt` grant valid at command time.

### Tests

- recurrence/timezone/DST unit tests;
- database concurrency with parallel conflicting holds;
- priority does not bypass overlap;
- hold/lock expiry race;
- idempotent retry;
- E2E slot view → hold and second-client conflict.

### Out of Scope

- Order payment completion;
- Booking confirmation;
- external calendar sync;
- JobInterview scheduling;
- location reveal;
- live video.

### Exit Gate

- two concurrent prohibited reservations cannot both succeed;
- hold and lock are atomically paired and expire/release cleanly;
- UTC is authoritative and DST tests pass;
- priority decision is resolved externally and only snapshotted locally;
- no provider or payment truth exists in Booking hold state;
- all concurrency/E2E tests pass.

---

## 08 Order-Gated Booking Confirmation and Booking Lifecycle

Convert a valid hold/lock into authoritative Booking only after upstream Order/Agreement readiness passes.

### Objective

Establish Booking as paid live-service scheduling truth independently of calendar/video provider availability.

### User-visible / Observable Result

A buyer/professional can observe Booking confirmation, cancellation, reschedule, completion/no-show states. Confirmation is impossible when the Order/Agreement gate is not satisfied or the hold/lock is invalid.

### Owning Module(s)

- **Booking & Calendar:** Booking and BookingEvent.
- **Order/Agreement:** transaction/legal readiness inputs only.

### Dependencies

- Feature 07;
- Order SH-025;
- Agreement readiness public interface;
- canonical lifecycle/event/idempotency primitives.

### Shared Operations Used

- SH-001 / SH-002 — action authorization.
- SH-011 — applicable hold stop-sign.
- SH-025 — Order entitlement.
- SH-031 — BookingEvent append mechanism.
- SH-044 — idempotent confirmation/cancel/reschedule.
- SH-046 — outbox after committed Booking transition.
- SH-051 / SH-052 — conflict/stale-write protection.
- SH-053 — lifecycle transition plumbing; Booking graph stays local.
- SH-109 — retain priority/other external decision snapshot when historically material.
- SH-027 — only when an in-person flow later requests exact location reveal; confirmation itself does not grant reveal.

### Data / Schema

- `Booking`, `BookingStatus`, `BookingLocationType`;
- `BookingEvent`;
- link to hold/slot lock/order/calendar connection as available;
- location fields must follow the unresolved/proposed Location Safety snapshot boundary.

### Public Interfaces

- `confirmBooking`;
- `getBooking` / owner-facts query;
- `cancelBooking`;
- `rescheduleBooking`;
- `completeBooking` / `markNoShow` according to authorized workflow.

### Logic

- lock BookingHold/SlotLock and re-evaluate expiry/state;
- obtain authoritative Order entitlement and Agreement readiness if required;
- convert hold/lock and create/transition Booking transactionally;
- append BookingEvent with actor/reason;
- use expected version/lock to reject stale conflicts;
- reschedule creates/uses a new interval reservation before final switch and preserves `rescheduledFromBookingId` chain;
- downstream provider effects are emitted, not performed in the same controller.

### UI / Administrative Surface

- Booking detail/status;
- cancel/reschedule controls;
- support-safe BookingEvent timeline;
- no provider-specific fields shown as lifecycle truth.

### Authorization / Compliance

- buyer/professional/support/admin action authorization is explicit;
- ComplianceHold is honored;
- confirmation does not infer payment from Stripe;
- exact location remains hidden unless Location Safety separately authorizes reveal.

### Events / Jobs / Integrations

- transactional BookingEvent and outbox;
- event triggers future orchestration feature but may be consumed by test subscriber now;
- no direct calendar/video/notification provider calls in Booking command.

### Failure Behavior

- Order not entitled/Agreement incomplete: remain appropriate Booking/hold state and return actionable denial;
- expired/released lock: conflict, do not resurrect;
- duplicate confirmation: same Booking result;
- stale reschedule: conflict and preserve original Booking;
- outbox publish delay does not roll back committed Booking truth.

### Tests

- full Booking transition matrix;
- Order/Agreement contract allow/deny;
- confirmation transaction with hold/lock conversion;
- stale/duplicate/reschedule concurrency;
- BookingEvent atomicity;
- E2E hold → confirm, cancel, reschedule.

### Out of Scope

- external calendar connection/writeback;
- video room;
- JobInterview;
- exact-location reveal implementation until location snapshot ruling is approved.

### Exit Gate

- Booking confirmation cannot occur without required authoritative upstream gates;
- one Booking transition owner exists;
- BookingEvent is atomic with transition;
- retry/conflict tests prove no duplicate Booking or lost reservation;
- no direct Stripe/Agreement/provider mutation exists in Booking service;
- complete lifecycle contract tests pass.

---

## 09 Cronofy Calendar Connection and Free/Busy Synchronization

Add external calendar connection and privacy-minimized BusyWindow synchronization without changing Booking source truth.

### Objective

Let a professional connect an external calendar with versioned consent and use normalized free/busy data to block availability.

### User-visible / Observable Result

A professional can connect/disconnect a calendar, see connection/sync health, and observe external busy time disappear from bookable slots without Workin Ants storing unnecessary external event content.

### Owning Module(s)

- **Booking & Calendar:** CalendarConnection, BusyWindow, ProcessedCalendarEvent.
- **Consent:** ConsentLog proof.
- **Cronofy:** provider rail only.

### Dependencies

- Feature 07 slot search;
- Consent SH-007/008;
- Cronofy credentials/config and provider adapter;
- webhook raw-body route infrastructure.

### Shared Operations Used

- SH-001 / SH-002 — professional actor/authority.
- SH-007 / SH-008 — required calendar consent proof.
- **SH-064 `authorizeExternalProviderConnection` — Booking provider connection.** Use state/nonce/redirect allowlist/scopes.
- **SH-067 `invokeCalendarProvider` — Booking.** Cronofy port/adapter.
- SH-059 / SH-060 / SH-061 — verify, dedupe into ProcessedCalendarEvent, translate.
- SH-062 — reconciliation.
- SH-044 / SH-047 / SH-048 — callback/sync idempotency and retry.
- SH-030 — sensitive calendar access audit where policy requires.
- SH-037 / SH-041 — failure visibility and explicit user notifications.

### Data / Schema

- `CalendarConnection` and provider/access/sync/status enums;
- `BusyWindow`, source/provider fields;
- `ProcessedCalendarEvent` and provider-event enums;
- connection scope/access fields;
- confirm unique provider/event dedupe constraint.

### Public Interfaces

- `connectCalendar`;
- `completeCalendarConnection`;
- `disconnectCalendar`;
- `getCalendarConnection`;
- `syncCalendarBusyWindows`;
- `applyCalendarProviderEvent`;
- `reconcileCalendarProviderState`.

### Logic

- query active consent version/proof before provider connection;
- request minimal scopes/access mode, preferring free/busy-only;
- provider callback activates connection only after normalized success;
- webhook signature verified before parse;
- dedupe ProcessedCalendarEvent before BusyWindow/connection changes;
- store interval/provider IDs/version only; do not persist event descriptions/locations/attendees for free-busy sync;
- slot search consumes BusyWindow and automatically reflects sync results;
- disconnect/revoke stops future sync and follows owner transition.

### UI / Administrative Surface

- calendar connect/disconnect/settings;
- provider/access-mode/scope summary;
- last sync and degraded/error state;
- no raw external event content inspector in ordinary UI.

### Authorization / Compliance

- calendar consent proof is mandatory;
- provider scopes are minimized;
- calendar provider credentials remain secrets/provider refs, not client data;
- privacy executor later can disconnect/delete provider references.

### Events / Jobs / Integrations

- Cronofy OAuth/authorization flow;
- Cronofy free/busy/calendar APIs;
- webhook/push notifications;
- periodic reconciliation;
- sync retries/dead-letter.

### Failure Behavior

- invalid/missing consent: no connection;
- callback state/nonce mismatch: reject;
- revoked provider authorization: CalendarConnection reflects owner status, no silent reconnection;
- duplicate webhook: no repeated BusyWindow changes;
- provider outage: retain Workin Ants Booking truth, show degraded sync, retry/reconcile;
- unknown event/status: safe failure + IntegrationFailure.

### Tests

- OAuth state/nonce/redirect;
- consent required;
- signature/dedupe;
- provider status mappings including unknown;
- free/busy minimization assertion (no event text/location/attendees);
- slot search changes after BusyWindow sync;
- disconnect/revoke/reconcile;
- provider contract tests.

### Out of Scope

- Nylas/direct secondary adapter;
- calendar as Booking source truth;
- JobInterview calendar ownership;
- video room.

### Exit Gate

- no CalendarConnection becomes active without required consent/provider success;
- a signed provider event creates/updates BusyWindow exactly once;
- slot search blocks synced busy intervals;
- stored free/busy state contains no unnecessary external event content;
- provider outage/degradation does not corrupt Booking truth;
- reconciliation can detect a missed sync;
- all provider/privacy tests pass.

---

## 10 Booking Orchestration, Calendar Writeback, Thread, Location Check, and Notification Requests

Implement Booking-owned downstream workflow tracking after a Booking transition while preserving each downstream Module’s truth.

### Objective

Turn a confirmed/rescheduled/cancelled Booking into reliable, observable downstream requests without embedding provider or other Module lifecycle logic in Booking.

### User-visible / Observable Result

A confirmed Booking shows delivery setup progress such as calendar sync, thread creation, optional location check, notification request, and later video-room request. Partial failures are visible and retryable without changing downstream truth ownership.

### Owning Module(s)

- **Booking & Calendar:** BookingOrchestrationRun/Step.
- Calendar writeback is Booking’s provider effect.
- Messaging, Notification, Location Safety, Video, Agreement owners retain target truth.

### Dependencies

- Features 08–09;
- shared workflow runner;
- Messaging SH-113;
- Notification SH-041;
- Location Safety SH-027;
- Video command may be stubbed until Feature 11.

### Shared Operations Used

- SH-049 / SH-050 — workflow step runner/aggregation. Booking supplies step graph and partial-completion policy.
- SH-044 / SH-047 / SH-048 — idempotent durable step dispatch/retry.
- SH-067 — calendar writeback.
- SH-113 — ensure context Thread through Messaging.
- SH-027 — location reveal/check interface where required; Booking never self-authorizes exact reveal.
- SH-041 — Notification request; Booking supplies safe variables only.
- SH-046 — outbox/trigger.
- SH-037 / SH-038 — integration and queue telemetry.
- SH-031 — Booking domain event remains separate from orchestration step state.

### Data / Schema

- `BookingOrchestrationRun` / status;
- `BookingOrchestrationStep` / type/status;
- Booking external calendar sync fields/status;
- unique idempotency keys and indexes.

### Public Interfaces

- `startBookingOrchestration`;
- `retryBookingOrchestrationStep` authorized admin/system command;
- `getBookingDeliverySetupStatus` projection;
- downstream adapters use public owner commands only.

### Logic

- create one idempotent run for the triggering Booking version/event;
- determine required steps from Booking location/type/policy, not from provider payload;
- each step carries typed target/request data and a correlation/causation ID;
- writeback create/update/cancel is Booking-owned through Cronofy adapter;
- context thread is created/retrieved through Messaging;
- Notification request is sent through Notification;
- location step requests Location Safety decision/proof only when workflow requires it;
- future video step calls Video public command;
- aggregate run as complete/partial/failed without mutating downstream lifecycle directly.

### UI / Administrative Surface

- Booking detail “delivery setup” status;
- safe per-step state and retry action for authorized support/admin;
- do not surface provider tokens/secrets.

### Authorization / Compliance

- manual retry requires authority and optional step-up per root policy;
- exact location is never exposed as orchestration metadata;
- notification payloads exclude signed URLs/tokens and sensitive location/provider data;
- thread participants come from owner facts, not arbitrary client input.

### Events / Jobs / Integrations

- Cronofy writeback;
- Messaging ensureContextThread;
- Notification request;
- Location Safety request;
- Video request stub/real after Feature 11;
- durable workflow jobs and dead-letter visibility.

### Failure Behavior

- downstream temporary failure: step `retrying`, bounded backoff;
- permanent business denial: step failed/skipped according to Booking policy, not blindly retried;
- one failed noncritical step may produce `partially_completed` only if Booking policy explicitly marks it noncritical;
- calendar writeback failure can set Booking external sync state without changing Booking core confirmation truth incorrectly;
- retry never duplicates Thread, calendar event, Notification effect, or Video room when downstream interface is idempotent.

### Tests

- workflow aggregation matrix;
- idempotent run/step dispatch;
- each downstream contract mocked then integrated;
- partial failure/retry/dead-letter;
- safe metadata/telemetry tests;
- calendar writeback create/update/cancel;
- E2E confirmed Booking → setup run → all available steps complete.

### Out of Scope

- owning Thread/Notification/Location/Video truth;
- generic workflow engine business policy;
- JobInterview workflow.

### Exit Gate

- one Booking trigger produces one semantic orchestration run;
- step retries cannot duplicate downstream effects;
- downstream lifecycle tables are never mutated directly by Booking;
- partial/terminal state is deterministic and observable;
- exact location/provider secrets are absent from workflow payload/logs;
- calendar writeback and Messaging/Notification contract tests pass.

---

## 11 Live Booking Video Room and Time-Bounded Join Access

Deliver confirmed `Booking.locationType=video` through a Video-owned live room and participant-specific short-lived credential.

### Objective

Prove Booking ↔ Video separation in a live end-to-end service workflow.

### User-visible / Observable Result

A confirmed video Booking receives a room setup status. The buyer and professional can join only within the permitted window and only as authorized participants. Expired/cancelled/failed rooms cannot issue valid join credentials.

### Owning Module(s)

- **Video Session:** BookingVideoRoom, provider resource, join credential.
- **Booking & Calendar:** Booking state/time window.

### Dependencies

- Features 08 and 10;
- Video live-provider port;
- current Proposed provider decision: Daily.co MVP adapter, or approved replacement;
- Healthcare and Track Entitlement interfaces where applicable.

### Shared Operations Used

- SH-001 / SH-002 — join actor/authority.
- SH-003/SH-123 owner facts pattern — Booking facts from Booking owner, not direct repository.
- SH-005 — live-streaming entitlement only where product policy requires it.
- SH-020 — healthcare/provider readiness where applicable.
- SH-025 — Order entitlement only where required as an additional current-delivery gate; Booking confirmation alone must not be stretched into unrelated policy.
- SH-044 / SH-047 / SH-048 — room provisioning idempotency/jobs.
- SH-059 / SH-060 / SH-061 — live provider webhook verification/dedupe/translation.
- SH-068 — live video provider port.
- SH-074 — secure join credentials where provider integration requires locally signed tokens.
- SH-030 / SH-125 — sensitive access audit + video domain access evidence.
- SH-070 — authorized provider deletion later.

### Data / Schema

- `BookingVideoRoom`, `BookingVideoProvider`, `BookingVideoRoomStatus`;
- `ProcessedVideoProviderEvent` shared only within Video’s provider-event truth;
- Booking `overtimeGraceMinutes` informs local Video join-window policy but remains Booking context.

### Public Interfaces

- `provisionBookingVideoRoom`;
- `getBookingVideoRoomStatus`;
- `issueVideoJoinCredential`;
- `cancelBookingVideoRoom`;
- provider-event application/reconciliation.

### Logic

- request arrives from Booking orchestration or authorized system command;
- query Booking owner facts: confirmed/video type/start/end/participants/cancellation;
- evaluate healthcare and track gates where applicable;
- create one pending BookingVideoRoom and provider resource idempotently;
- translate result to active/failed;
- join request rechecks actor participant, Booking state, current time window plus approved overtime grace, room status, holds/healthcare;
- issue short-lived participant-scoped credential;
- no reusable public room link becomes business truth.

### UI / Administrative Surface

- Booking video setup state;
- join button only when eligible/time-valid;
- room/provider degraded/failed state;
- support-safe room record view without reusable join secrets.

### Authorization / Compliance

- participant-only access;
- healthcare-sensitive joins use healthcare-capable approved provider path;
- AccessAuditLog for healthcare/sensitive joins;
- provider room identifiers do not grant authorization;
- current live-provider conflict must be resolved/approved before production adapter commitment.

### Events / Jobs / Integrations

- live-video provider room create/cancel;
- provider webhook/dedupe/reconciliation;
- room expiration cleanup;
- Booking orchestration acknowledgment;
- Notification may alert provider failure via SH-041 if policy says so.

### Failure Behavior

- Booking not confirmed/video type: reject room provisioning;
- duplicate request: same room result;
- provider create timeout: retry with provider idempotency key/reconciliation;
- provider failure: Booking remains Booking truth; room `failed` and orchestration shows degraded setup;
- join too early/late/cancelled: deny and audit where required;
- healthcare readiness denies: no credential.

### Tests

- Booking owner-facts contract;
- participant/time-window matrix;
- entitlement/healthcare gates;
- provider adapter + signature/dedupe;
- room provisioning idempotency;
- credential TTL/secret persistence;
- E2E confirmed video Booking → room → buyer/pro join → expiry denial.

### Out of Scope

- JobInterview room (Feature 12);
- group webinars/live broadcasting;
- custom video server;
- alternate provider implementation without approved ADR.

### Exit Gate

- Booking can request but cannot own a room/provider resource;
- Video cannot transition Booking;
- only authorized participants in the valid time window receive credentials;
- duplicate provisioning produces one Video-owned room;
- provider failure is visible without corrupting Booking state;
- sensitive access audit and domain access evidence are both present when required;
- live provider decision is recorded in architecture/progress before production enablement.

---

# Phase 4 — Cross-Cluster Integration Proof

## 12 JobInterview Video Delivery Bridge

Prove that Video Session can serve the CL-06 hiring lane without turning JobInterview into a Booking or reusing Booking scheduling truth.

### Objective

Create and access `JobInterviewVideoRoom` strictly from JobInterview-owned interview/participant facts.

### User-visible / Observable Result

A qualifying JobInterview can receive a Video-owned room. Candidate/interviewer participants can obtain valid join credentials in the authorized window, while unrelated users cannot.

### Owning Module(s)

- **Video Session:** JobInterviewVideoRoom/provider access.
- **Job Interview (CL-06):** interview schedule/status/participants.

### Dependencies

- Feature 11 live-video infrastructure;
- CL-06 JobInterview public owner-facts interface;
- Role / Authority organization/participant interpretation.

### Shared Operations Used

- SH-001 / SH-002 — actor/authority.
- SH-003/SH-123 — minimal owner facts/target validation from JobInterview owner.
- SH-020 — healthcare if interview context triggers it.
- SH-044 / SH-068 — idempotent provider room create.
- SH-059 / SH-060 / SH-061 — provider callback handling.
- SH-030 / SH-125 — join audit/domain evidence.

### Data / Schema

- `JobInterviewVideoRoom`, provider/status enums;
- no Booking, BookingHold, BookingSlotLock, or BookingEvent writes.

### Public Interfaces

- `provisionInterviewVideoRoom`;
- `issueVideoJoinCredential` with interview context adapter;
- `cancelInterviewVideoRoom` after JobInterview owner instruction.

### Logic

- Video validates JobInterview owner-supplied time/status/participant facts;
- participant roles map to provider token claims locally;
- JobInterview status is never inferred from room status;
- one interview → at most one current schema room row;
- provider failures remain Video state/ops evidence.

### UI / Administrative Surface

Owned by CL-06 hiring UI; CL-05 supplies reusable join/status view model/contract only. A development contract test surface is sufficient if CL-06 UI is not yet built.

### Authorization / Compliance

- organization membership/participant authority comes from proper owners;
- no Booking buyer/professional rules reused by assumption;
- sensitive access audited when policy requires.

### Events / Jobs / Integrations

- same live-video port/provider adapter as Feature 11;
- separate target type and Video-owned room record;
- provider webhook maps to correct target.

### Failure Behavior

- invalid/stale interview facts: reject;
- nonparticipant: deny;
- duplicate room request: idempotent;
- provider degraded: JobInterview remains unchanged; room shows failed/pending as Video truth.

### Tests

- public contract with CL-06;
- candidate/interviewer/nonparticipant access matrix;
- prove no Booking table mutation;
- provider/dedupe/idempotency tests;
- E2E/contract: interview → room → join.

### Out of Scope

- interview scheduling/rescheduling;
- candidate decisioning;
- Booking model reuse/consolidation.

### Exit Gate

- JobInterview video works through public CL-06 facts with zero Booking lifecycle coupling;
- provider resource remains Video-owned;
- participant authorization tests pass;
- no generic `VideoSession` schema consolidation was introduced;
- CL-06 contract suite passes.

---

## 13 Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification

Prove that external lifecycle/policy changes can remove or degrade delivery through owner commands without cross-owner mutation.

### Objective

Verify the most important outbound/inbound guardrail contracts across CL-01, CL-02, CL-04, CL-07, and CL-09.

### User-visible / Observable Result

When an authoritative event/decision invalidates access:

- refunded/non-entitled Orders stop qualifying digital/playback access according to owner policy;
- Moderation can disable delivery and revoke affected grants;
- ComplianceHold blocks mapped actions;
- Search receives refresh/removal requests when public readiness changes;
- users receive safe notifications when configured;
- no provider URL/token remains a bypass.

### Owning Module(s)

- CL-05 owners execute their own state changes.
- Order, Moderation, Hold, Search, Notification, and Track Entitlement retain their source truth.

### Dependencies

- Features 02, 04, 06, 08, 11;
- real/test public interfaces from Order, Moderation, Hold, Search, Notification, Track Entitlement;
- domain event inbox/deduplication.

### Shared Operations Used

- SH-005 / SH-006 — entitlement changes/usage where relevant.
- SH-011 — hold decisions.
- SH-025 — current Order entitlement on access.
- SH-045 — dedupe consumed domain events.
- SH-046 — owner events after CL-05 transitions.
- SH-089 — grant revocation pattern.
- SH-091 — Search refresh request.
- **SH-103 `executeModerationDecision` — Moderation decision, owner-local execution.** Do not build local DMCA adjudication.
- SH-041 — Notification request.
- SH-030 / SH-029 — sensitive/generic audit where required.

### Data / Schema

Potentially transitions existing:

- MediaAsset `frozen` / access grants revoked;
- CourseVideoAsset `disabled`/provider deletion or access revoked as instructed;
- CourseVideoPlaybackGrant revoked;
- DigitalDownloadAsset `disabled`, `disabled_by_dmca`, `disabled_by_moderation`;
- DigitalDownloadGrant revoked;
- Booking actions denied by holds/entitlement policy where applicable.

No new generic enforcement/blocked table.

### Public Interfaces

- owner event handlers for Order/refund/dispute access invalidation;
- `applyMediaModerationDecision`;
- `applyVideoModerationDecision`;
- `applyDigitalModerationDecision`;
- grant bulk-revocation owner commands;
- Search refresh request integration.

### Logic

- external decision/event is authenticated/versioned/deduplicated;
- owner maps it to allowed local transitions;
- grant revocation is idempotent and records source reason/reference;
- direct access endpoint always rechecks current required Order/hold state, preventing stale grant bypass where policy requires;
- Search request is issued only for affected public source projection;
- Notification receives safe, non-secret payload;
- Moderation retains action/case lifecycle and execution acknowledgment.

### UI / Administrative Surface

- buyer/provider sees access unavailable/revoked safely;
- support/admin can see source decision reference and CL-05 execution result without being able to invent moderation truth;
- no separate CL-05 moderation queue.

### Authorization / Compliance

- legal/moderation reason originates from Moderation;
- refund/dispute transaction state originates from Order;
- hold originates from ComplianceHold;
- subscription/track entitlement originates from Track Entitlement;
- search remains projection;
- audit data excludes raw content/tokens where not needed.

### Events / Jobs / Integrations

- event inbox/deduplication;
- bulk grant revocation jobs;
- provider disable/delete job only when action requires it;
- Search refresh;
- Notification request;
- reconciliation checks stale active grants after owner decisions.

### Failure Behavior

- one downstream revocation fails: source decision remains authoritative; record retryable/terminal execution failure and continue required independent steps according to owner/moderation workflow;
- Search unavailable: delivery truth still changes; Search owner retries projection work;
- Notification unavailable: no rollback of enforcement;
- duplicate source event/action: no duplicate revocations/provider deletions.

### Tests

- refunded Order denies/revokes purchased access;
- moderation action disables/revokes without direct Moderation Prisma writes;
- ComplianceHold gate across representative Booking/Media/Digital action;
- Search public command only, no Typesense call;
- Notification safe payload;
- event dedupe/idempotent revocation;
- E2E access before decision → decision → access denied.

### Out of Scope

- dispute adjudication;
- DMCA/legal validity determination;
- Search document schema;
- Notification channel implementation;
- subscription plan lifecycle.

### Exit Gate

- authoritative external decisions can reliably remove CL-05 delivery without ownership theft;
- no local generic blocked/moderation/entitlement truth was created;
- stale signed/access paths cannot bypass revalidation rules;
- Search and Notification are called only through public interfaces;
- duplicate events/actions are harmless;
- cross-Cluster contract/E2E tests pass.

---

# Phase 5 — Privacy, Reconciliation, and Production Hardening

## 14 Privacy Target Executors, Retention, and Provider Deletion

Implement CL-05’s side of Privacy-owned erasure/export/retention workflows across Booking, Video, Media, and Digital Goods.

### Objective

Make all four Modules discoverable/executable privacy targets without creating any CL-05 PrivacyRequest or DataErasureJob lifecycle.

### User-visible / Observable Result

A Privacy workflow/test harness can ask each CL-05 Module what data/provider references it holds, apply a disposition, and receive a typed execution result showing erased, anonymized, revoked, deleted-provider, retained, skipped, or failed outcome.

### Owning Module(s)

- **Privacy / Data Erasure:** request/job/target/retention-exemption truth.
- **Each CL-05 Module:** its records/provider effect.

### Dependencies

- all prior relevant Module records/provider adapters;
- Privacy SH-095–097 contracts;
- provider deletion SH-070;
- retention policy facts from Order/legal owners where needed.

### Shared Operations Used

- **SH-095 `executePrivacyInstruction` — Privacy protocol / owner execution.** Each CL-05 Module implements its handler; do not build a CL-05 privacy workflow.
- **SH-096 `enumerateSubjectData` — owner inventory.** Return stable target types/provider refs.
- **SH-097 `evaluateRetentionRequirement` — data owner facts, Privacy exemption.** No local retention-exemption table.
- SH-098 — anonymize fields where approved.
- SH-070 — provider deletion/revocation through provider owner.
- SH-089 — revoke temporary grants.
- SH-044 / SH-047 / SH-048 — idempotent/retryable owner execution.
- SH-029 / SH-030 — audit required destructive/sensitive operations.
- SH-037 — operational failure.

### Data / Schema

No new PrivacyRequest/DataErasureJob/RetentionExemption tables.

Owner effects may include:

- Booking personal/context fields, CalendarConnection, provider refs;
- Video rooms/assets/grants/events/provider resources;
- MediaAsset metadata/object storage/access records;
- DigitalGoodsTermsAcceptance, download grants/events, declarations/controls/accessibility records.

Preserve legal/transaction evidence only when Privacy records an approved retention exemption.

### Public Interfaces

For each CL-05 Module:

- `enumerateSubjectData` implementation;
- `evaluateRetentionRequirement` implementation where the Module owns relevant facts;
- `executePrivacyInstruction` implementation;
- export serializer where required.

### Logic

- inventory is cursorable/stable and identifies provider resources;
- owner distinguishes product deletion from privacy erasure;
- retention decision is supplied/recorded through Privacy protocol;
- revoke access before destructive deletion when needed;
- external provider deletion is idempotent and returns deleted/absent/retained/retryable/terminal result;
- anonymization preserves required relational integrity;
- execution does not delete evidence subject to approved exemption.

### UI / Administrative Surface

No standalone CL-05 privacy UI required. Privacy/admin workflow consumes typed execution results. CL-05 may expose debug/admin execution evidence under Privacy-authorized surface only.

### Authorization / Compliance

- only Privacy-authorized system workflow may invoke destructive target executor;
- step-up if root policy requires for manual destructive retry;
- sensitive provider/object references remain private;
- legal/financial/Agreement retention facts remain with their owners.

### Events / Jobs / Integrations

- R2 object deletion;
- Cronofy connection/resource deletion/disconnect as supported;
- Mux/live-video provider deletion;
- grant revocation;
- durable retry and reconciliation;
- Search refresh/removal requests only through owner/Search interface where privacy effect changes public projection.

### Failure Behavior

- provider object already absent: idempotent `absent/deleted` success semantics as approved;
- retention required: return retained with source reason to Privacy; do not silently delete;
- provider unavailable: retry and return partial/failed target, leaving Privacy parent truth unresolved until its own policy decides;
- duplicate executor invocation: same semantic result/no repeated destructive side effect.

### Tests

- inventory for each Module;
- erasure vs retention exemption;
- anonymization field map;
- provider delete success/absent/retryable/terminal;
- grant revocation;
- prove no CL-05 PrivacyRequest/DataErasureJob creation;
- E2E Privacy test harness across all four owner executors.

### Out of Scope

- Privacy request identity verification;
- Privacy deadline/orchestration status;
- legal determination of retention exemption;
- search/privacy final completion aggregation.

### Exit Gate

- Privacy can enumerate and execute against all four CL-05 owners through typed contracts;
- retained records are preserved only through Privacy exemption flow;
- provider deletions are idempotent/retryable and observable;
- no CL-05 parallel privacy lifecycle exists;
- sensitive data is excluded from telemetry;
- privacy integration tests pass.

---

## 15 Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness

Harden CL-05 as a production delivery subsystem after all source lifecycles and provider paths are proven.

### Objective

Close degradation, reconciliation, concurrency, privacy, security, observability, and performance gaps without adding new product scope.

### User-visible / Observable Result

Users see stable delivery behavior under retries, provider outages, stale sessions, concurrent booking/download attempts, and recovered callbacks. Operators can see provider/queue degradation and safely reconcile without treating operational state as business truth.

### Owning Module(s)

All four CL-05 Modules own their business recovery semantics. Shared platform/Audit/Ops own generic execution/telemetry mechanisms.

### Dependencies

- Features 01–14;
- real production provider configuration for launch-critical providers;
- production scanner selected for scan-required contexts;
- root security/step-up policy finalized enough for sensitive CL-05 actions;
- live-video provider decision approved.

### Shared Operations Used

All feature-specific SH operations continue to apply, with particular emphasis on:

- SH-014 step-up for approved sensitive actions;
- SH-032–SH-039 request/log/metric/exception/failure/queue/health operations;
- SH-044–SH-052 idempotency, event dedupe, queue, retry, locking, optimistic concurrency;
- SH-055–SH-058 expiration/counters/interval locks;
- SH-059–SH-063 webhook/reconciliation/snapshots;
- SH-072–SH-078 cryptography/provider minimization;
- SH-095–SH-098 privacy/anonymization.

No hardening work may create a duplicate local infrastructure service.

### Data / Schema

Review and tune existing schema only:

- booking overlap/exclusion constraint and active-status strategy;
- provider-event unique constraints and hashes;
- idempotency keys;
- expiry indexes for holds/grants;
- provider/status indexes for reconciliation;
- MediaAsset storage/processing indexes;
- access-event query indexes;
- destructive cascade behavior;
- retention-safe deletion paths;
- migration rollback/backup plan.

Any new column/table must have a clear owner and architecture justification.

### Public Interfaces

No new broad public surface by default. Harden:

- provider reconciliation commands;
- health/readiness checks;
- authorized admin retry/replay commands;
- safe operational read models;
- existing Module public contracts under load/error.

### Logic

- scheduled reconciliation compares Workin Ants owner truth with provider state and repairs only explicitly safe discrepancies;
- dead-letter work is recoverable with correlation and idempotent replay;
- rate limits and abuse controls protect upload/token/grant/webhook endpoints;
- all time-bound access checks validate server time at request time, not only worker expiry state;
- all concurrency races have deterministic conflict/result semantics;
- destructive provider/data operations have dry-run or explicit safeguards where applicable;
- no current access decision relies solely on historical snapshot when current revalidation is required.

### UI / Administrative Surface

- CL-05 provider health/degradation summary integrated with Ops, not a competing incident system;
- safe reconciliation/dry-run discrepancy view;
- dead-letter/retry links through approved Ops tooling;
- no raw provider secrets/payload dumping.

### Authorization / Compliance

Security review must verify:

- least privilege provider scopes;
- secret rotation paths;
- step-up matrix implementation;
- RLS/server authorization alignment;
- healthcare file/video provider boundaries;
- exact-location reveal boundary;
- audit completeness for sensitive access;
- Privacy executor coverage;
- moderation/hold revocation coverage;
- telemetry redaction;
- retention/destructive migration safety.

### Events / Jobs / Integrations

- Cronofy reconciliation;
- live-video room reconciliation;
- Mux asset reconciliation;
- R2 orphan/quarantine cleanup and object-state reconciliation;
- scanner health checks;
- grant/hold expiration sweeps;
- queue dead-letter replay;
- provider health checks/metrics.

### Failure Behavior

Explicitly test and document:

- provider unavailable vs degraded vs delayed;
- missed webhook;
- duplicate webhook;
- provider says missing while local resource exists;
- local source says deleted while provider resource remains;
- concurrent cancel/reschedule/confirm;
- concurrent grant use/revoke/expiry;
- scanner unavailable;
- storage presign failure;
- Notification/Search unavailable after source change;
- Privacy target partially failed;
- reconciliation discovers unsafe discrepancy requiring manual review.

### Tests

- load/concurrency tests for slot locking and grant counters;
- property/actor authorization/RLS tests required by root architecture;
- webhook replay/security tests;
- secret/token/URL log-scrape tests;
- chaos/provider degradation tests with adapters;
- reconciliation dry-run/repair tests;
- privacy retention/destructive tests;
- audit completeness tests;
- E2E critical journeys under provider retry/failure;
- migration-from-clean and migration-on-realistic-seed tests;
- production build/typecheck/lint/unit/integration/E2E suite.

### Out of Scope

- new providers solely for redundancy unless separately approved;
- new product delivery modes;
- generic incident management UI;
- architecture redesign for future VideoSession consolidation;
- legal policy expansion.

### Exit Gate

CL-05 is production-ready only when all are true:

- launch provider decisions are recorded and adapters are production-configured;
- scan-required Media policies have a production-capable scanner and fail-closed health behavior;
- calendar/video/storage provider reconciliation can identify missed/inconsistent state without treating provider truth as authoritative;
- booking overlap and grant usage concurrency tests pass under parallel load;
- webhook replay/duplicate tests produce one business effect;
- all critical credentials are short-lived, secrets are server-only, and log/audit scans find no reusable tokens/URLs or prohibited sensitive payloads;
- Privacy target executors and retention paths pass end-to-end;
- moderation/refund/hold revocation paths pass end-to-end;
- sensitive AccessAuditLog coverage is complete for the approved policy matrix;
- dead-letter/retry/IntegrationFailure visibility is proven;
- clean migrations, seeded migrations, typecheck, lint, unit, integration, contract, provider, privacy, concurrency, E2E, and production build all pass;
- all unresolved items that block production are either resolved by binding architecture decision or explicitly feature-flagged out of launch.

---

## Phase Summary

| Phase | Name | Features |
| --- | --- | --- |
| 1 | Safe Media Substrate | **01** Secure Upload to Ready MediaAsset; **02** Contextual Media Access and Short-Lived Signed Delivery |
| 2 | Digital Goods and Course Delivery | **03** Digital Goods Policy and Versioned Terms Evidence; **04** Purchased Digital Download Grant and Controlled Download; **05** Child-Directed Controls and Course Accessibility Tracking; **06** Course Video Ingest and Signed Playback |
| 3 | Conflict-Free Scheduling and Booking Delivery | **07** Professional Availability, Slot Search, and Atomic Booking Holds; **08** Order-Gated Booking Confirmation and Booking Lifecycle; **09** Cronofy Calendar Connection and Free/Busy Synchronization; **10** Booking Orchestration, Calendar Writeback, Thread, Location Check, and Notification Requests; **11** Live Booking Video Room and Time-Bounded Join Access |
| 4 | Cross-Cluster Integration Proof | **12** JobInterview Video Delivery Bridge; **13** Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification |
| 5 | Privacy, Reconciliation, and Production Hardening | **14** Privacy Target Executors, Retention, and Provider Deletion; **15** Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness |

**Total numbered features: 15.**

---

## Phase Execution Pattern

Before each numbered feature:

1. Read required root, Cluster, target Module, dependency Module, Shared Operations, and progress context.
2. Confirm the previous feature exit gate.
3. Check the unresolved-decision register for anything that affects this feature.
4. Write the concise feature implementation specification.
5. Confirm schemas, migration state, owner contracts, permissions, provider ports, SH-### dependencies, failure semantics, and tests.
6. Implement only that feature.
7. Run typecheck, lint, unit, integration/contract tests, and production build as applicable.
8. Perform the feature’s workflow verification, including failure and idempotency paths.
9. Update `progress-tracker.md`.
10. Update architecture only when a legitimate binding decision changed.
11. Record assumptions, risks, unresolved provider/legal decisions, and deferred work.

Do not start adjacent “helpful” features merely because the code is nearby.

---

## Required Feature Specification

Immediately before implementing a numbered feature, create a concise implementation specification containing:

- Objective;
- Observable result;
- Dependencies;
- In scope;
- Out of scope;
- Owning Module(s);
- Data records/enums/indexes/constraints affected;
- public interfaces and owner-facts contracts;
- SH-### shared operations consumed;
- permissions and contextual authority;
- compliance/readiness gates;
- primary success workflow;
- UI/admin/debug states if applicable;
- provider ports/adapters;
- jobs/events/outbox/inbox behavior;
- idempotency/concurrency strategy;
- error/failure/retry/manual-review behavior;
- privacy/retention implications;
- audit/observability requirements;
- unit/integration/contract/provider/concurrency/privacy/E2E tests;
- acceptance criteria;
- documentation/progress updates.

Do **not** pre-write giant implementation specifications for all 15 features. The numbered plan is the sequence and architecture guardrail; the next feature specification supplies implementation-level detail only when that feature is ready to build.

---

## Required Completion Report

After every numbered feature, the coding agent must report:

- Feature completed;
- Files added;
- Files changed;
- Database changes;
- Migrations and database constraints;
- Dependencies added;
- Shared operations reused, by SH-### ID;
- Public interfaces added/changed;
- Dependency Module contracts consumed;
- Events/outbox/inbox handlers added;
- Jobs/workers/schedules added;
- Provider ports/adapters added or changed;
- Tests added/changed;
- Commands run;
- Manual/workflow verification performed;
- Security/compliance/privacy verification performed;
- Documentation/progress updated;
- Assumptions;
- Known failures;
- Remaining risks;
- Unresolved decisions encountered;
- Deferred work;
- Exit-gate result: **PASS** or **FAIL**, with failed criteria listed explicitly.

A feature with a failed exit gate is not complete merely because its happy path works.
