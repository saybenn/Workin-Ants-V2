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

- SH-080 `manageVersionedRules` for immutable MediaUploadPolicy versions. Current schema is insufficient; a later approved schema/migration must support effective versions and stable applied-version evidence before production policy-version behavior is complete. Contract fixtures may precede that migration.

- root auth/authority/runtime validation;
- Prisma/Postgres;
- durable queue;
- Cloudflare R2 adapter or test object-store adapter;
- active seeded MediaUploadPolicy for at least one low-risk and one sensitive test context;
- scanner test adapter if production scanner is not selected.

### Shared Operations Used

- **SH-080 `manageVersionedRules` — Media policy using shared versioning mechanism.** Resolve the effective upload-policy version and preserve its historical meaning; never mutate applied policy history in place.

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
- Media-internal SH-087 `issueSignedMediaUrl` implementation behind public composite `requestMediaAccess`; consumers do not call a second public signer;
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

- production legal-content activation remains blocked until immutable owner-controlled historical text is available: Consent supplies generic Consent-owned disclosures, while Digital Goods owns contextual license/refund/access text unless explicitly classified otherwise. A linked ConsentLog and acceptedTextHash do not alone preserve that content; its persistence/retrieval mechanism remains unresolved.

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

- use/consumption tests exercise explicit test policy only until owner rules are approved; no common CL-05 meaning of `used`, automatic issuance-as-consumption, or production `final_after_access` threshold is inferred.

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
- `updateCourseAccessibilityAssetState` only through Digital Goods owner logic.

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

- Production source-ingest transport remains unresolved. Media must authorize and mediate a bounded handoff; Video owns purpose-minimized provider ingest without direct R2 access or permanent source URLs. Test/fake ingest is permitted while that decision is pending.

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

- fake-adapter proof does not complete the production ingest adapter; its exit remains blocked until the Media-to-Video transport contract is approved.

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
- `completeBooking` / `markBookingNoShow` according to authorized workflow.

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

- Booking `getBookingOwnerFacts` must supply current Booking ID/version or freshness marker, status, scheduled start/end, authorized participants, and `overtimeGraceMinutes`. Video uses that value, never a local default, room-state inference, or direct Booking repository read. SH-003 remains Proposed; this is an owner-query contract.
- Video-owned persistent append-only live-access evidence is a schema prerequisite for the live-delivery exit; the model name/design belongs to a later schema pass.

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
- query current Booking owner facts: ID/version or freshness marker, status/video type, scheduled start/end, authorized participants, overtimeGraceMinutes, and cancellation;
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
- successful and denied live credential issuance persist Video-owned append-only domain evidence (room, parent, actor/participant, action/decision, relevant provider, expiry/window, time/request correlation); SH-030 sensitive audit is supplemental and cannot replace it;
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

- Video-owned persistent append-only live-access evidence, with the same minimum fields as Feature 11, must cover successful and denied Interview credential issuance; its approved schema/migration is a prerequisite, not created by this plan.

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

- Video-owned append-only domain proof covers successful/denied live credential issuance; generic AccessAuditLog alone cannot satisfy this gate.

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
- `executeMediaModerationInstruction`;
- `applyVideoModerationDecision` — Video-owned SH-103 boundary for authorized asset disable/restore, affected grant revocation, other specifically targeted Video-owned transitions, idempotent replay, and acknowledgment/completion/failure evidence;
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
- SH-072 `hashCanonicalPayload`, SH-074 `generateSecureToken`, SH-075 `encryptSensitiveValue`, and SH-078 `minimizeAndRedactProviderInput` for the confirmed hashing/token/encryption/provider-minimization uses above; SH-073 remains Proposed and is not authorized by this feature;
- SH-095–SH-098 privacy/anonymization.

No hardening work may create a duplicate local infrastructure service.

### Data / Schema

Review existing schema and the separately approved future schema prerequisites, including mandatory Video-owned persistent live-access evidence:

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

- live Booking/Interview issuance and denial have persistent Video-owned domain evidence under SH-125, separate from supplemental SH-030;
- destructive cascades are not used as erasure authorization: owners enumerate affected records, supply retention facts, and safely execute Privacy disposition only after the target-specific retention matrix is approved; exact periods/dispositions/FK changes remain unresolved;
- no final grant-consumption, `used`, or `final_after_access` behavior is claimed without the relevant owner/commercial/legal ruling; issuance alone is not automatically consumption;
- terminal `failed` live rooms remain terminal: retry/reconciliation does not authorize reset, `failed → pending`, replacement generations, or duplicate rooms while Video recovery design remains unresolved.

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


## WA-R011 — Approved early-access scheduling (P01)

Product-owner ruling approved 2026-09-29: premium priority affects **when eligible customers may access newly released availability**. It never overrides an existing Booking, displaces a customer, reserves inventory permanently, or bypasses eligibility/conflict rules. This closes U-BC-05 / U-CL01-31 / CL-05-U017's product-effect choice.

Track owns the effective Customer-track benefit and returns eligibility, entitlement/grant evidence, policy version, evaluation time and expiry. Booking owns the release schedule and enforces the resulting access time on both slot queries and hold/confirmation commands. An early-access decision is not a slot reservation. Unavailable entitlement evidence cannot grant early access; ordinary access remains available once general release is reached, subject to normal gates. Existing holds follow their original bounded expiry; premium expiry cannot displace an already confirmed Booking.

Technical ruling: store timezone-independent release instants and a versioned release-window policy. Resolve the benefit against server time when creating a hold, bind evidence to that hold, and recheck normal conversion gates. No quota is consumed by this access-time benefit; SH-006 is not invoked unless a separately approved metered product is later introduced. Do not translate legacy priorityRank into request ordering. Missing release-window configuration disables early release for that availability; it does not invent a duration or disable ordinary booking. Exact window configuration is a launch prerequisite, not another ownership decision.

Implementation acceptance: premium/nonpremium boundary instants; expired/unavailable entitlement; concurrent claims; direct-command bypass attempts; replay of hold creation; no displacement; ordinary access at general release. Schema/API work must represent these facts before activation; this ruling is not implementation evidence.


## WA-R012 — Purchased session allowance and Booking cardinality (P02)

Product-owner ruling approved 2026-09-29: an Order may authorize multiple scheduled sessions **only when the purchased Offering/package explicitly includes them**. Four purchased sessions permit at most four allocated session entitlements, not unlimited Bookings. This closes U-BC-02 / CL-05-U014's product choice. Do not add uniqueness on Booking.orderId.

Supply owns the offered package description. Order validates and snapshots the purchased positive integer session allowance, source/version and applicable fulfillment/cancellation/refund terms; later Offering edits cannot change the purchase. Booking owns each appointment and its conflict, hold and scheduling lifecycle. Neither a paid flag nor counting local Booking rows supplies purchase authorization.

Technical ruling: Order owns durable per-session authorization identities bounded by the purchased allowance. An idempotent reservation command binds Order/session identity to one Booking command intent and reports authorized, exhausted, denied, or unavailable with the Order version. Concurrent attempts cannot reserve the same session twice or exceed the allowance. Booking persists the reservation identity with its local conversion; an outbox acknowledgement confirms attachment. An uncertain cross-owner outcome remains reserved until reconciliation queries Booking's durable result; never release merely on transport timeout. Failed conversion with proven absence can release its reservation idempotently. This is a recoverable workflow, not a cross-owner Prisma transaction.

Rescheduling retains the session authorization through the replacement chain and does not consume another session. A completed, cancelled or no-show appointment does not itself restore allowance or prove full Order completion. Order applies the purchased terms and owner-confirmed session outcomes; refunds and cancellation adjustments are Order decisions through Payment's rail. No automatic equal-price-per-session refund or forfeiture policy is invented. Packages cannot activate without explicit applicable terms. A normal SlotLock converts at most once (U-BC-03); that safety invariant is separate from Order multiplicity.

Implementation acceptance: four-session package permits four distinct authorizations and rejects a concurrent fifth; retry returns the same identity; single-session package remains bounded; reschedule reuses authorization; timeout recovery avoids double release/allocation; source edits do not rewrite terms; partial fulfillment does not finish the whole Order; refund/cancel outcome follows snapshotted terms. Current schema lacks this complete contract; the coordinated database pass must implement it before package activation.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


## WA-R018 — Durable execution, receipts and operational evidence

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R018 contract](../../reconciliation/platform-architecture-rulings.md#wa-r018--durable-execution-receipts-and-operational-evidence) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one platform-owned persistent command-idempotency/inbox/outbox/job mechanism with Postgres transactional persistence in the coordinated database pass. Module application/domain boundaries own effect semantics. A successful owner mutation atomically stores its domain change and outbox record; no transaction is held across provider/network calls. Consumers atomically claim a stable source event plus effect identity and commit their owner effect. Unknown outcomes reconcile before a new business attempt. Same scoped command key plus same canonical fingerprint replays the original result; different fingerprint conflicts. Owner/operation/subject scope is part of the key. At-least-once delivery is assumed; never promise global exactly-once execution.

Provider callbacks use verified provider/account/event identity, payload fingerprint, receipt state and separate effect/attempt state under the provider-owning Module (SH-059/060). A received/claimed record is not proof of completed effect. Duplicates preserve original proof; telemetry records observations. A retry of one semantic effect reuses its downstream idempotency identity. A genuinely new business attempt has a new identity linked to the prior result and cannot silently overwrite history. Booking workflow steps likewise carry a stable run/step/effect key. Exact tables/index names and runner library are implementation details; production runtime evaluation remains a scoped provider/operational gate, not a reason to build Module-local queues.

Adopt Ops-owned Postgres persistence for operational SystemEvent, IntegrationFailure and OpsIncident; QueueJob remains an operational projection of the platform runner, not a second executable queue. SystemEvent is append-only; correction references the original. IntegrationFailure separates occurrence identity from recovery observations; recording the same occurrence replays, another actual attempt creates another occurrence. Incident operator state is open/triaged/mitigated/resolved, with explicit authorized reopening recorded as a new transition; automatic grouping/alerts require versioned configured rules. Ops success/recovery cannot finish a business workflow. Tradeoff: durable local diagnostic queries require migrations/storage; provider dashboards remain secondary. Accept PR-CL09-05 persistence direction without claiming schema deployment or selecting retention periods.

Acceptance: concurrent identical/conflicting keys, crash after receipt and before effect, crash after domain commit and before dispatch, duplicate/out-of-order callback, lease recovery, retry exhaustion and reconciliation. Do not activate a consumer merely because a queue accepted its job.


## WA-R019 — Consent catalog, acceptance causation and buyer provisioning

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R019 contract](../../reconciliation/platform-architecture-rulings.md#wa-r019--consent-catalog-acceptance-causation-and-buyer-provisioning) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Consent owns an immutable version/content catalog, including consent type, version, exact content or immutable content reference/hash, locale, jurisdiction applicability and effective interval. Existing logs cannot prove an unrecorded presentation. Bind acceptance to the catalog entry and the actual rendered presentation identity/version, subject, action/context and time; preserve an immutable rendering descriptor where composition changes presentation. SH-009 selects applicable content, SH-007 stores acceptance, and SH-008 queries proof. Same acceptance command key/fingerprint replays; a new intentional re-acceptance is a new command/proof, not a uniqueness collision on User+type+version. Current-state eligibility queries use current applicable proof; Orders, screening authorizations, digital terms, redemptions and other historically binding actions preserve their specific proof reference/content-version binding. A generic audit log alone is not that binding.

Withdrawal/decline is recorded separately as an append-only disposition, not by rewriting an earlier acceptance; the consuming policy evaluates its effect. Legal re-consent/material-change obligations and retention periods are external facts. ConsentType.age_gate can prove acknowledgment only; Identity separately evaluates age eligibility. This resolves proof/catalog/retry architecture, not legal sufficiency for every category.

Customer provisioning uses the Customer owner synchronously and idempotently at the first buyer action (SH-004), with durable uniqueness on User. Optional registration-time outbox provisioning can warm the profile but never substitutes for this precondition. Customer aggregate views use the existing SH-126 Customer application facade over authorized owner queries; default to query composition, introducing a durable projection only with a demonstrated query need and invalidation contract. Legacy backfill/deletion awaits the database-evidence gate; User remains authentication identity. Tradeoff: first buyer action depends on Customer availability, but avoids an eventually missing commercial actor and duplicate local provisioning.


## WA-R020 — Privacy executor identity and truthful completion

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R020 contract](../../reconciliation/platform-architecture-rulings.md#wa-r020--privacy-executor-identity-and-truthful-completion) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Privacy persists an immutable target descriptor with request identity, owner Module ID, registered owner target kind, opaque source ID/version, permitted action and descriptor/executor schema version. Each owner validates its own reference and field map. Typed child targets may be enumerated separately or included in an explicit versioned parent executor contract listing all covered child kinds; arbitrary `other`, a crawler or assumed cascade never supplies coverage. Deduplicate by request+owner+target-kind+source-id+action+source-version; preserve a new generation when re-evaluation changes an instruction. This is Privacy dispatch metadata, not polymorphic Media ownership.

Persist per-target attempts and final owner receipts independently of queue telemetry. A receipt names target/instruction identity, source version observed, action/outcome, executor version, completion time, evidence reference and any owner retention basis. Correction/restriction are explicit outcomes, never mislabeled deletion. Search acceptance is pending until Search returns its actual required projection outcome; Media artifact readiness similarly requires actual finalize/readiness proof. Retention is complete only when Privacy accepts an evidence-backed lawful exemption, not merely because an owner requested one.

Aggregate completion means every required target has either verified execution or an accepted lawful disposition. Summaries/exports disclose retained or restricted categories and reasons safely; `completed` never means all data was erased. Outstanding/failed targets prevent completed. A lawful fully accounted exemption does not by itself mean technical partial failure. An incomplete export stays pending/retryable or failed; no silent serializer omission or ready download. Any future deliberate partial-export product must explicitly distinguish partial from complete. This chooses correctness over premature delivery.

One request may have multiple execution/artifact generations for retries or refreshes; generations are immutable, correlated and only the current authorized ready artifact is offered. Revoke superseded access. Per-subject conflicting mutations serialize and re-evaluate owner state; do not reject or erase a legal request merely because another exists. Statutory verification, deadlines, restriction entitlement, backup completion wording, retention schedules and final User disposition remain EXTERNAL_REQUIREMENT. Identity markers are projections of Privacy outcomes, not a second rights lifecycle. Exact target enums/schema fields are deferred implementation constrained by this protocol.

Acceptance: restart routing, duplicate targets, changed source version, missing child coverage, failed serializer, lawful exemption versus unproven retention, Search queue acknowledgment versus completion, stale bundle access and concurrent conflicting instructions. No blanket claim of complete privacy coverage is authorized until all owner target/field matrices are reviewed.


## WA-R023 — Sensitive disclosure and audit failure boundaries

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Require a durable sensitive-access audit acceptance before returning exact private location, protected file/playback/join credentials, resumes, healthcare-sensitive fields, tax/identity/Agreement evidence, or sensitive admin exports. If required proof cannot be durably recorded, withhold the protected response and return a retriable unavailable result; never return the secret and log later. Record safe allowed/denied/redacted/blocked/unavailable outcomes under Audit-owned vocabulary without importing Healthcare enums as generic authorization. Include service/system/provider actor attribution and request correlation, not nullable User alone. A denied request must still disclose no target-existence details; audit trouble never changes denial into access.

Privileged irreversible mutations require durable owner decision/history plus atomic audit-outbox intent before committing owner state. If that local durable write fails, roll back the mutation. Later Audit transport failure retries/reconciles; it does not roll back an already executed external financial/legal effect or erase domain evidence. Where a legal action specifically requires pre-action Audit acceptance, its owner contract adds that stricter gate; legal deadlines/recovery remain scoped requirements. Low-risk diagnostics are best effort and never recursively produce infinite failures.

Identity owns fresh action-bound assurance; Role still authorizes the action. Require step-up for security-factor/recovery changes, financial adjudication/movement, privileged permission changes, bulk sensitive evidence export and administrative override/release of protective controls. Existing sessions or admin roles do not substitute. Exact assurance methods/lifetimes and action registration are security implementation policy, with provider capability checked before activation. Ordinary read access is not automatically all step-up; owner-specific policy may require it. Privacy identity verification is a separate statutory proof requirement.

Tradeoff: protected access becomes dependent on durable audit availability; this is preferable to an unprovable sensitive disclosure. Acceptance: audit unavailable before response, durable intent failure before mutation, outbox delivery outage after commit, privileged service actor, retry without duplicate effect, denied-target anti-enumeration and redaction-safe evidence. These rules amend failure/assurance portions only; per-owner legal retention and complete target/action matrices remain separate work.

Duplicate-collapse scope: CL01-HU-006/007/008/012 security portions; CL02-D025/044/056; CL04-U032; CL-05-U007/062; CL-06-U048/055; CL-08-U16 and HU-09/19; CL-09-D016/030/031/032/035/043/046; CL-10-HU031/PR-CL10-09. Unnamed adjacent questions are not closed.


## WA-R025 — Location consumer alignment and reveal evidence

Class: **AI_RESOLVED** from the binding location product ruling and canonical SH-027/028/131. U-08-13/14's product predicate/directionality is settled: exact service location is disclosed only to the authenticated Professional/provider legitimately performing the active in-person service, within its service-performance window. No buyer, Organization, Search or public-map entitlement to another party's exact location is implied. Completion ends that justification; cancellation, refund or dispute masks/revokes it. Rescheduling requires a fresh current decision. Payment, Booking confirmation or a cached flag alone is insufficient authorization.

Source Modules own their protected location facts/references. Booking's exact/fuzzy/precision/reveal fields are non-authoritative scheduling snapshots or compatibility fields; neither Booking nor Order operates a second reveal lifecycle. Location queries current typed participant, service-state, time-window and source-location facts through owners. Missing/stale/inconsistent facts deny disclosure. Each supported service context has a typed identity; an attached Booking and Order must be consistent, not arbitrarily XOR when both legitimately describe the service. A nullable context pair never permits context-free disclosure. Non-Booking source contexts require an explicitly supported service-performance contract; Job/Organization address fields do not automatically qualify.

Location stores current per-viewer/service/source decision plus immutable decision/revocation history using its owned lifecycle and SH-031 mechanism. The semantic current key includes viewer, typed service context and source reference; an owner source/policy token binds the decision. Atomically reject stale Location writes; revoke/expiry wins over a replayed old allow. Replays may reproduce proof identity but must never re-disclose exact data without a current authorization evaluation. Rescheduling updates evidence in the same owner lifecycle rather than creating a parallel reveal flag. WA-R023 requires durable sensitive-access proof before returning exact data. This resolves U-08-11/12/15/16/19 architecture; exact fields/constraints and coordinated migration remain implementation prerequisites.

Fuzzy generation uses a versioned Location policy per supported typed source, stable for the same source/policy generation. Radius/precision and refresh/expiry settings must be explicitly configured and validated before public use. Source/policy changes, privacy removal and expiry invalidate old results. SH-131 returns only current approved projection fields with source/policy version and validity; absent/stale data is unavailable, never exact fallback or read-triggered generation. Consumers use SH-028 only for generation/invalidation commands. The target-kind registry names actual source owners and validators; free-form target strings cannot broaden support. U-08-17/18 policy structure is AI_RESOLVED; numerical deployment settings are deferred configuration, and geocoder/KMS/vendor evidence is externally gated.

Acceptance: wrong viewer or source relation, absent context, Booking/Order mismatch, completed/cancelled/refunded/disputed service, reschedule, stale source/policy and delayed events, duplicate reveal after revocation, audit failure and expired public projection. Exact location remains absent from Search, notification payloads and telemetry. Legal retention/Privacy dispositions are not selected by this ruling.


## WA-R026 — Approved Review and multi-episode Dispute policy (P06–P08)

**Binding product-owner ruling, 2026-10-01.** Review input is a whole-number 1–5 star rating. Zero and half-star input are invalid; aggregate/reputation values may be fractional. Review owns the rating calculation; Professional and Search consume its versioned result, not separate scales or calculators.

Automatically publish an otherwise eligible Review after completed-Order, buyer-author and applicable safety/moderation checks pass. An author may revise rating or comment. Every proposed revision is immutable history and passes the same applicable checks before becoming the public/reputation-bearing revision. Promotion is atomic against the expected Review version; a delayed check for an older revision cannot supersede a newer one. A rejected/unavailable revision does not overwrite the previously accepted public revision; an active restriction independently controls whether any revision is public. Author editing never restores hidden/removed state or bypasses a restriction. Restoration is an explicitly authorized Review owner/Moderation action. Revisions update the contribution of the same Review; they never add another rating count. Hiding/removal withdraws its contribution; restoration uses the current eligible accepted revision.

The Order's buyer Customer or seller Professional may open a commercial dispute. Authorized support may record one on behalf of an identified participant where policy allows; preserve both actual support actor and represented participant. There is **one durable Dispute case container per Order at launch**, not one dispute episode for the Order's lifetime. Authorized reviewers may reopen that case for new evidence, a correction, or a later episode associated with the same Order, including another session of a multi-session package.

Persist a distinct immutable cycle/episode identity for each review/adjudication/settlement cycle, with opening/reopening reason, initiating/represented actor, relevant Order version, session references where applicable, evidence, decisions and outcomes. The case's current state is a projection of its current cycle; reopening never overwrites prior closed decisions or settlement proof. Serialize cycle creation and adjudication per case. A current pending cycle can receive new evidence; it does not require competing active refund/release decisions. Any concurrency policy must preserve one authoritative current case decision path.

Every financial effect requires valid current owner authorization and an idempotent identity bound to the specific cycle/decision/effect, with prior effects retained for reconciliation. Never key a new valid effect only by case ID, and never mint a fresh identity merely to retry an old effect. Reopening itself cannot replay a previous refund, charge, payout adjustment, settlement or hold-release effect. Order/Payment validate cumulative amounts and remaining authorized source value across all cycles; a new cycle is not permission to exceed the purchased/refundable amount. Dispute decides, Order coordinates transaction effects, Payment executes its rail, and Holds retains its own action-scoped lifecycle.

Opening/appeal windows remain separately versioned product policy; no numerical deadline is introduced. Bind the applicable policy version to each cycle. Product case windows do not redefine statutory/provider rights. Current Prisma's one-case relation is compatible with the container rule but does not supply cycle/revision proof; the coordinated database pass must add that representation before activation.

Acceptance: ratings 0/6/fractions rejected, fractional aggregate allowed; two revisions race without double counting; failed safety check leaves the accepted revision unchanged; hidden/removed edit cannot restore; buyer/seller/support attribution; unrelated actor denied; later-session episode reuses the case with a new cycle; old cycle remains reconstructible; replay of old financial result cannot affect the new cycle; valid new effect has its own authorization and respects cumulative Order limits. These are required implementation checks, not claims of executed feature tests.

Duplicate collapse: CL04-U034/035/036/038/040 and owner §9/§35 product questions; CL04-U039 retains its versioned configuration gate. WA-R022/023 technical proof, financial finality and assurance rules remain binding. Classification: PRODUCT_OWNER_CHOICE — RESOLVED by explicit approval; enforcement/revision/cycle identity details AI_RESOLVED.

## WA-R028 — Digital delivery evidence and policy separation

Classification: AI_RESOLVED_WITH_TRADEOFF. Resolves the technical evidence/text-storage boundary while preserving PRODUCT_OWNER_CHOICE P09/P10 for refund finality and allowance consumption. It does not activate either policy.

Digital Goods owns an immutable contextual policy-content revision with Offering/policy identity, locale/jurisdiction applicability, terms/refund/license versions, exact retained content or immutable Media document/version reference, checksum and effective interval. Acceptance binds the precise revision/rendered presentation and contextual Order/User evidence. Do not overwrite accepted content on policy edit or use an unresolvable hash/version as historical proof. Consent owns generic disclosure content/proof separately; neither owner's proof implies the other's requirements passed. Actual legal text, applicable rights and retention remain external activation requirements. This supplies the persistence direction missing from Digital Goods §35.9; exact relational names follow coordinated schema conventions.

Separate grant issuance, download intent, transfer attempt, observed delivery outcome and policy evaluation. Digital Goods owns each immutable logical delivery identity bound to actor, asset version, Order entitlement reference, grant and policy revision. Media owns storage/transport evidence and returns a normalized authenticated receipt correlated to that identity; a browser assertion is untrusted. Video playback progress and byte serving are different observations and cannot silently stand in for Digital Goods delivery. Preserve observed byte/range/completion evidence with adapter capability and timestamps; an adapter that cannot establish completion returns unknown rather than manufactures success. Completion of server delivery never claims the person read or understood the content.

A signed URL or accepted terms is not proof of download completion. Record it as the distinct event it is. Retries/resumptions for the same logical intent retain identity and attempt history; conflicting asset/actor bindings reject. Finite-allowance implementations must account for in-flight reservations under the grant lock so concurrent requests cannot bypass the approved cap; do not release an unknown outcome merely on client timeout. Reconcile durable owner/Media evidence before deciding release/consumption. The exact consumption event is P10, not chosen by this technical protocol. Unknown evidence cannot automatically make a purchase non-refundable. No `used`, URL or playback projection grants Order refund authority.

Expose delivery evidence to Order/Review as a versioned owner query containing logical identity, asset version, accepted policy/proof reference, grant state, observations and their reliability, with minimal actor/context references. Order/Review apply their approved refund/dispute policy and current authorization; Media and Digital Goods do not execute financial refunds or declare legal finality. P08 case reopening may add a new interpretation/decision cycle while retaining the original observations. Corrections append evidence and reevaluate projections; they never rewrite the old observation or repeat an old financial effect.

Acceptance before activation: URL issued without bytes, aborted transfer, range resume, duplicate receipt, unknown completion, concurrent last-allowance requests, changed policy after purchase, stale/revoked Order entitlement and later dispute cycle. These tests establish technical truthfulness; approved P09/P10 behavior and actual provider capabilities remain separate prerequisites.

## WA-R029 — Approved digital refund, download and seller-acceptance policies (P09–P11)

Binding product-owner ruling: 2026-10-01 America/New_York (2026-10-02 UTC). Supersedes the open P09–P11 alternatives and contrary conceptual payment/acceptance sequences. WA-R028 continues to govern truthful delivery evidence.

P09: At launch, digital access, grant issuance, streaming and download completion never automatically make a purchase non-refundable. Delivery/access evidence may inform authorized refund/dispute review but never determines the result alone. Apply the applicable product/refund policy, dispute facts and required external/legal rules. An approved refund or revocation triggers only the downstream access consequences specified by the owning Order/Digital Goods policy. Download history alone neither revokes access nor preserves it against an authorized revocation. No automatic `final_after_access` denial is enabled by a stored enum value.

P10: Consume one allowance only when one user-initiated logical download successfully completes with verified delivery. Retries, resumes, range requests, duplicate transport attempts and recovery of the same logical download consume no additional allowance. Failed or unverified delivery consumes zero. A genuinely new user-initiated download after a completed one may consume another allowance only when the applicable product policy actually limits download count. Finite `used` means allowance exhausted; unlimited grants are not exhausted by first use. Completion observation proves delivery, not human reading or legal acceptance.

Digital Goods mints and persists the logical-download identity at explicit user initiation, with actor/asset-version/grant/Order/policy binding. Transport retries cannot mint a new identity. Atomically convert that intent's reservation to one consumption on its first verified completion; a unique consumption reference prevents duplicates. Resumes retain the same identity. A new explicit post-completion initiation is a new logical identity, subject to policy and current authorization. Unverified attempts remain zero-consumption even while their in-flight reservation is reconciled. Bound reservation lifetime through server-side access expiry/revocation and reconcile before releasing capacity; never strand allowance indefinitely or release while an old transfer remains capable of independently completing. Late receipts reconcile to the original identity and cannot charge another allowance. Provider evidence incapable of proving the approved completion event cannot support finite-count consumption; do not substitute URL issuance, elapsed time or client claims. This capability requirement gates that delivery adapter, not P10's product meaning.

P11: For live or seller-performed services, final capture requires seller acceptance. Acceptance is either explicit approval of the specific Order/Gig/service request or valid precommitted acceptance: the seller intentionally configured an approved instant-book/availability/product policy and the frozen requested transaction satisfies all its constraints. A matching accepted Gig award satisfies acceptance; merely publishing a service does not. Published standalone downloads and self-paced digital courses/products may auto-accept because fulfillment requires no later seller performance decision. Payment authorization/holds may precede acceptance where Payment architecture permits; authorization is not final capture. Platform screening has its separate approved source, with no fabricated seller.

Order records immutable acceptance evidence: seller/context, explicit decision or intentional precommit policy identity/version, frozen scope/price/package version, applicability result and timestamp. A precommit must be active and applicable when accepted, scoped to the actual seller/product, and cannot be inferred from a premium flag or open calendar alone. Policy changes do not rewrite already recorded acceptance; material requested scope/price changes require fresh acceptance of the changed terms. Recheck current financial capability, cancellation/hold and payment authorization validity immediately before capture. Payment accepts a uniquely identified Order-authorized capture intent with acceptance proof; retries preserve that effect identity and uncertain outcomes reconcile before any new capture. No capture from stale acceptance for different terms or from mere Booking existence.

Order remains transaction truth and Booking owns individual scheduled sessions. Acceptance is evidence within Order, not a second Order/Booking lifecycle or a separate booking authority. A multi-session package acceptance binds purchased scope; each Booking still uses current eligibility/conflict checks and bounded Order session authorization. Instant booking does not bypass locks, consume nonexistent availability or displace customers. Decline/expiry releases only valid owner reservations/authorizations; any already captured amount follows an independently authorized refund. Numerical response windows remain versioned policy, not invented here.

Implementation acceptance requirements: access/completion cannot auto-deny refund; authorized revocation follows current owner policy; aborted/unverified delivery zero consumption; range/resume/replay one consumption; new post-completion initiation counts only under bounded policy; concurrent last allowance; late receipt reconciliation; explicit versus valid precommitted acceptance; absent/revoked/inapplicable precommit denied; changed terms need new acceptance; Gig acceptance matching; authorization-before-acceptance permitted but capture-before-acceptance denied; capture retries idempotent; Booking conflict rules unchanged. These are required tests, not executed runtime claims.

## WA-R030 — Track catalog, enrollment, immutable grants and usage protocol

Classification: AI_RESOLVED_WITH_TRADEOFF. Track remains the commercial-policy owner; Candidate owns applications, Search owns ranking projections, Order owns transaction snapshots and Payment owns financial effects. This resolves technical representation/protocol alternatives; paid cancellation/grace and application quota product policies are explicitly separated below.

Represent free participation as an explicit Track-owned enrollment in a versioned free plan for each activated actor track, not absence of a subscription, a Stripe-created $0 subscription or a consumer-local free flag. Introduce a provider-neutral free enrollment representation; current provider default `stripe` must not label free records. Provision idempotently by User/track/profile identity. At most one current base enrollment selection exists per User/track; pending paid attempts may coexist without becoming current. Exactly one Customer/Candidate/Professional profile binding must match the selected track and User. Enforce typed FK/check constraints, user/profile consistency and current-selection uniqueness in the coordinated migration. Separate Organization ATS subject scope remains WA-R005, never a fourth AccountTrack. Historical enrollment rows remain reconstructible.

TrackPlanPrice is canonical for immutable amount/currency/billing cadence and provider-price correlation. TrackPlan.monthlyPriceCents is a compatibility/display projection and never a second price editor. A paid enrollment binds an immutable plan revision, price revision and applicable Consent proof/presentation; old enrollments and Order quotes never silently read today's edited price. Separate BillingCadence from TrackUsagePeriod. Existing monthly prices remain product truth; no new cadence, trial or price is invented. Activate a new revision only after catalog validation, retain effective intervals and prevent conflicting active revisions for the same selection key. Retiring a plan stops new enrollment, not evidence or previously authorized benefit periods. Accept conservative plan graph draft→active→retired→archived and draft→archived; archived is terminal, later publication is a new revision.

Catalog definitions are immutable typed keys with actor scope, value schema/unit, combination rule, period applicability and consuming capability. At most the designated value field may be populated and its type must equal the definition. Validate integer/money bounds, basis points and versioned JSON schemas; raw JSON is not executable policy. The initial product-backed key meanings are Candidate application allowance (15/month free, unlimited paid), Candidate employer-search boost (0 or 1500 basis points), verified-applicant plan badge and application-view insights; Customer qualifying buyer-fee waiver and early-availability eligibility; Professional commission (1000 or 300 basis points). Exact persisted key spelling is a coordinated contract constant, not a consumer-created alias. Additional unspecified premium features/ATS prices/limits are inactive catalog entries until explicitly defined; enum presence grants no benefit.

Resolve one current base plan revision, then only applicable active grant revisions. Equivalent benefits do not stack automatically. Each grant must declare an approved composition mode: extend duration, add a bounded quota, provide separately scoped value, or no additional effect for an equivalent benefit. Reject ambiguous overlap/configuration before grant activation; do not choose a winner by insertion order or a universal max/sum rule. An explicit replacement identifies the superseded grant with history. A grant never bypasses Role, readiness, Hold or source-owner eligibility. Accept grant graph active→expired/revoked/suspended/consumed; suspended→active only with authorized restoration and current validity, or →expired/revoked. Consumed is one-shot only; expired/revoked/consumed records are terminal. Append Track-owned immutable grant transitions, separate from audit and provider receipts; use a dedicated grant-history record or typed owner event table with equivalent append-only guarantees, not only mutable grant columns.

Track's Billing adapter owns subscription normalization and owner-specific provider receipts. A shared verified Stripe ingress routes by registered integration/account/resource/event purpose to Track or Payment; each owner has an independent effect receipt keyed by owner+provider-account+event ID, so one owner's receipt never suppresses the other's legitimate effect. Neither owner mutates the other's subscription/payment truth. New paid checkout starts incomplete, never default active. Provider confirmation is authenticated evidence bound to the exact attempt/price/subject. Out-of-order callbacks trigger owner reconciliation/version checks, not timestamp-only last-write-wins. Transition, immutable history and outbox commit together. Unknown financial/provider state cannot create paid access. Exact trial/grace/cancellation/downgrade benefits remain product policy, not imported from a provider enum; this ruling does not enable them.

Usage is an owner protocol: versioned period policy supplies a durable period identity/start/end/timezone; subject+track+entitlement+period policy/version identifies the counter across free/paid plan switches. Switching plans or provisioning another record never resets same-period consumption. Keep the counter rebuildable from immutable accepted consumption and compensating events. No destructive monthly reset or consumer-local quota. Semantic key binds source owner, source command/logical action, subject and entitlement; same key/fingerprint returns the same receipt, different payload conflicts. Quantity and policy revision persist with the receipt. A correction references the original event, is authorized by the source/Track policy and can compensate once; withdrawal or a monetary refund is not automatically a usage reversal. The actual monthly boundaries and withdrawal policy still require the product ruling identified in the decision packet.

For Candidate application submission use durable reservation/commit/reconcile, not foreign repositories or a distributed database transaction. Candidate first validates subject/Job eligibility and creates a stable submission intent. Track atomically reserves allowance and returns reservation/period/policy proof. Candidate commits the application once with that reservation, then emits a durable confirmation; Track converts the reservation to consumption idempotently. A duplicate source submission returns the original application/receipt. In-flight reservations reduce remaining capacity. On timeout query the Candidate submission outcome; release only on proven non-commit or owner-confirmed cancellation that prevents later commit. Unknown remains reconcilable, never silently free capacity. Withdrawal after successful commit follows the separately approved quota policy. Background cleanup cannot free a reservation while an application can still commit against it. This protocol is FOUNDATION_CAPABILITY, not full CL-01 maturity.

The approved Candidate subscription boost is non-metered effective ranking metadata, not a billable impression/application event. Search applies a 1.15 multiplier to its nonnegative base relevance/quality score only after all audience/eligibility/privacy filters; zero remains zero and deterministic ties use the normal stable tie-breaker. It is not a guarantee of 15% more views or permission to enter a protected result set. No `candidate_search_boost_applied` usage debit is enabled merely because the enum exists. Bound the projection to Track evidence/version and refresh on effective benefit change; stale or unavailable paid-boost evidence cannot silently confer a bonus. Earned separate boosts require their explicitly approved combination rule.

Fee/commission quotes carry integer basis points, currency, applicable basis identifier/amount, policy/plan/grant revisions and evaluation time. Order freezes the quote at its approved pricing/acceptance boundary. Use checked integer minor-unit arithmetic with deterministic round-half-up for nonnegative fee/commission calculation; sum the persisted rounded line allocations to the total and distribute any explicitly required remainder deterministically by stable line identity. Never use binary floating point or recompute old orders from current rates. Tax's jurisdiction-specific rounding remains Tax policy. A missing approved fee basis/eligibility policy is unavailable, not an invented charge. Payment consumes the Order-authorized monetary result, not a second Track fee calculator.

Required validation before activation: free/paid concurrent selection, wrong profile/actor binding, price revision change, typed value mismatch, ambiguous grants, grant restoration after expiry, duplicate/provider cross-owner event, quota contention/plan switch, crash before/after Candidate commit, unknown reservation outcome, duplicate compensation, stale boost and exact price rounding vectors. Schema/runtime proof remains unperformed at this architecture checkpoint.

## WA-R031 — Authority policy, Customer lifecycle and shared review claims

Classification: AI_RESOLVED_WITH_TRADEOFF. Role interprets authority, Identity/Hiring/Messaging retain role/membership/participant lifecycle. No general admin bypass is created.

Use a versioned code-first Role action/resource policy catalog with explicit owner, accepted actor scopes, minimal owner-facts contract, allowed relationships, freshness/version requirements, sensitive-access proof and step-up obligations. Each protected owner public command/query registers one canonical action before activation; unknown/unregistered action denies. Human-readable action names derive from the owning interface rather than a new generic Cluster service. Roles alone never waive source lifecycle, Hold, commercial, Healthcare or privacy checks. An admin may perform only explicitly registered admin actions; support is limited to authorized support views/intake and attributed on-behalf actions, not role assignment, money movement, restoration or unrestricted evidence access by virtue of support role alone. Financial/adjudication/security operators require the specifically granted action and fresh assurance. Additional access needs a catalog amendment, not `isAdmin` fallback.

Organization matrix: owner may manage membership/administrators, transfer ownership through Hiring's checked workflow, and manage hiring resources; admin may manage ordinary hiring resources and recruiter membership, but cannot replace/remove the owner, self-promote or grant owner authority; recruiter may manage assigned Jobs/applications/interviews subject to Hiring/Candidate/Interview facts, but not organization ownership, membership administration or billing. Member/viewer values remain inactive/deny-by-default until a separately defined action set exists. Current relationship facts are queried from Hiring; removed membership takes effect on the next protected request. Thread membership is Messaging truth, never inferred from having an Organization role. Identity appends immutable UserSecurityEvent/Audit intent for platform-role assignment/revocation in the same mutation transaction; no second Role-owned role table.

Server services enforce Role policy before owner operations. Use handwritten reviewed RLS/SQL implementations where database-side policy applies, with one shared semantic fixture matrix comparing server/RLS allowed and denied cases. Do not generate SQL from arbitrary executable application predicates. Baseline protected domain tables deny direct anonymous/authenticated client CRUD; exposed read models require a separately reviewed allowlist and RLS policy. Server credentials do not eliminate owner checks. Enumerate every table/view/function exposed to API/database roles in the migration review; no unreviewed relation becomes public by default. Add identity-map-aware policies under WA-R027 rather than assuming provider subject equals User.id. This is the parity/coverage method; actual grants/RLS/schema replay stay under database readiness. Keep authorization cache and Role domain events absent at launch; add caching only with proven revocation/version invalidation, and events only for a real consumer.

Return the same safe public response for missing versus unauthorized private targets where existence is sensitive. Preserve distinct internal reason classes unknown_action, insufficient_authority, missing_relationship, stale_or_unavailable_facts, step_up_required and policy_unavailable for diagnostics and authorized UI handling. Never make outage equivalent to allowed. Resource owners choose a purpose-limited safe denial message; internal IDs, evidence and reason details are not automatically public. WA-R023 durability still governs protected disclosure. Concrete owner DTO field sets remain bilateral qualification work; no universal `queryOwnerFacts` DTO is adopted.

CustomerProfile lifecycle: normal idempotent provisioning produces active after Identity eligibility. Optional draft can activate only through Customer validation; self-service active↔paused controls new buyer participation. Customer owner may archive active/paused/draft after checking obligations; archiving stops new buyer actions and retains access needed to fulfill existing Orders, Bookings, disputes, refunds and statutory requests under those owners' current permissions. Archive does not cancel a transaction, discharge debt, erase proof or hide an active restriction. Restoration of archived returns to draft for current eligibility checks; suspension is a separate authorized owner action with reason/history, not a mirrored Hold. Only an authorized owner/moderation restoration with current checks may leave suspended; self-service pause/archive/restore cannot clear it. Privacy deletion/anonymization is its own approved executor path. No automatic status transition on receipt of a generic Hold event.

Persist append-only Customer lifecycle evidence (typed owner event record or retained lifecycle journal) alongside the state change because archive/restoration and obligations now require reconstructible history; outbox dispatch retention alone is insufficient. This specifically supersedes the prior no-dedicated-history-unless-required proposal by supplying the requirement, without requiring a second generic platform ledger. Customer's contextual display fields override account display defaults only within Customer views. Copy defaults once on provisioning with provenance; do not synchronize later edits bidirectionally. Customer remains absent from public discovery; this does not change Candidate/Professional public projections. Customer avatar is an explicit Customer-owned MediaAsset FK/reference with retention-safe deletion and Media validation, not a polymorphic attachment repository. Existing legacy buyer User references backfill through the one-profile-per-User owner resolver; preserve original attribution and quarantine mismatches, never choose by display name/email. Review/Dispute bind the authoritative Order participant identities under WA-R026.

Adopt feature/Module-first logical domain/application/contracts/infrastructure/workers/privacy separation where relevant; adapters/routes are thin. These are ownership boundaries, not permission to reorganize current code or create a generic CL-01 domain service. A Module references another owner's public contract, not foreign repository/entity ownership. Remove obsolete Identity `TrackEntitlement` schema reference: Identity's actual documented dependency is supplying User facts to Track, not reading either entitlement definitions or grants. Do not guess a replacement schema or create the obsolete model.

SH-054 shared work claiming is a persistence capability: claim by work-kind/owner item ID with holder, lease deadline, monotonically increasing fencing token and expected owner version; renew/release/complete compare token. Expired holder cannot commit a decision or acknowledge another holder's work. Manual reviewers obtain Role authority and domain evidence separately; a lease does not approve a case. Review workflow truth remains in the owning Module. Use the shared Postgres transaction/locking layer, not a new generic moderation/recovery case. Capability activation requires concurrent claim, stale holder, renewal failure and crash/reclaim tests. Proposed registry status remains until concrete shared API qualification; technical placement is resolved.

Acceptance: public/client table access denied unless explicitly reviewed; server/RLS parity; stale membership and private-target denial; support cannot escalate; owner transfer cannot lose the final owner; profile archive preserves outstanding obligations; suspension cannot be self-restored; buyer backfill conflict quarantined; stale review lease cannot commit. Per-resource action registration/fixtures, legal retention and actual DB grants remain explicit implementation requirements, not claims of completed runtime validation.

## WA-R032 — Approved subscription benefit periods and Candidate quota (P12/P13)

Binding product-owner ruling, 2026-10-01 America/New_York. Supersedes P12/P13 open alternatives; WA-R030's owner boundaries and durable reservation/history design remain binding.

Cancellation or voluntary downgrade takes effect at the end of the already-paid subscription period. Premium benefits remain active through that paid-through time. Failed renewal creates no unpaid premium grace at launch. Provider retry/recovery may continue, but premium benefits end at the previously paid boundary unless payment is successfully recovered. Later recovery may resume benefits within the valid renewed entitlement period; never fabricate retroactive usage rights. Return to the applicable free-track policy when premium entitlement ends.

Existing purchase, Order, Booking, digital-access and other rights validly acquired while premium are not revoked merely because the subscription ends. Their owning Module/policy determines continuing rights. Subscription change cannot reprice an accepted Order, cancel an accepted Booking or revoke a purchased download by itself. End only the current subscription-derived benefit. No automatic free trials, subscription pauses or automatic prorated cancellation refunds at launch. Refunds follow approved refund policy rather than cancellation implying a refund. Core account/security access is never paid-only.

Track separates provider billing/recovery state from effective benefit intervals. A cancel request records scheduled end plus immutable intent/history; it does not set present benefits to false. Verified payment evidence binds a specific enrollment/price revision and paid interval. Query-time evaluation enforces interval boundaries even if the expiry worker is late. Past-due/retry state alone cannot extend the paid-through interval. A late recovered payment records the valid new interval and observation/activation time; effective resumption starts no earlier than verified recovery and never reauthorizes denied historical actions. Duplicate receipts cannot extend a period twice. Terminal or expired enrollment history is preserved; renewed access is an explicit versioned entitlement selection, not history overwrite. Paused/trial enum values remain unsupported launch transitions. Payment truth, retries and Track entitlement evaluation remain separate owners.

Free Candidate users receive 15 successful application submissions per UTC calendar month. Consume one quota unit only when one logical submission succeeds and is durably accepted into Candidate's application workflow. Failed attempts, retries, duplicate transport and rejected technical writes consume zero. Later Candidate withdrawal, employer rejection or any downstream application outcome does not restore a consumed unit. A proven technical duplicate/error is corrected by an authorized append-only adjustment referencing the original, not by deleting usage history.

Persist successful monthly usage for every Candidate submission, including while Premium is unlimited. The effective unlimited plan bypasses the numeric cap, not usage recording. On return to Free within that UTC month, available allowance is max(0, 15 minus already-recorded successful monthly usage), including Premium-period successes. Plan changes cannot reset counters, duplicate usage or create another 15. Calendar boundaries are half-open [first day 00:00:00 UTC, next first day 00:00:00 UTC); the owning Candidate durable acceptance timestamp selects the month, not the client clock or delayed outbox delivery time. Preserve policy revision, source intent/application, accepted timestamp and consumption identity.

For a submission spanning a month boundary, Track's capacity reservation must cover the month in which Candidate commits acceptance. Candidate must not commit against an expired prior-month authorization: renew/rebind the reservation under the new period, check the current plan/remaining capacity, then durably accept once. Store the resulting period proof with acceptance. At the period boundary, use a server-authoritative time/transaction guard and reconciliation so cleanup cannot release a reservation still eligible to commit. Unknown outcomes remain reserved until reconciled; failed/noncommitted work consumes zero. Successful unlimited submissions still produce idempotent consumption evidence without denying submission for exceeding 15. A late confirmation applies to its proven acceptance month, never the arrival month.

Required implementation checks: cancellation before paid end; failed renewal at boundary; recovery before/after boundary; duplicate recovery; preserved purchased rights; no retroactive authorization; 15/16 simultaneous Free submissions; failed technical writes; duplicate receipt; withdrawal/rejection without credit; Premium submits above 15 with recorded usage; downgrade with zero remaining allowance; period-boundary submission and delayed confirmation. These are acceptance requirements, not claims of runtime execution.

## WA-R035 — Supply lifecycle, history and source projections

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

This ruling supersedes the proposed/unresolved lifecycle and projection alternatives named below; implementation still requires forward schema coverage and contract fixtures. Professional graph: create→draft; draft→active after current activation readiness; active→paused; paused→active after current readiness; draft/active/paused→suspended only by an authorized source restriction; draft/active/paused→archived by owner-authorized retirement. Archiving a suspended record may record retirement intent but cannot remove the restriction. Archived→draft is an explicit owner restore command, never implicit activation. Suspended→draft requires authorized release of all applicable restriction sources; subsequent activation rechecks readiness. Preserve previously acquired transactions and obligations. Ordinary dependency loss invalidates the affected action/public decision and requests reevaluation, not an automatic Profile status change. Only an explicit source policy may instruct suspension.

Offering graph: draft→active by publish; active→paused; paused→active by resume, each activation requiring current composed gates. Draft/active/paused may enter under_moderation/disabled_by_moderation/disabled_by_dmca only from a valid Moderation decision. Those restriction states may change to another restriction state only with a superseding valid decision. Restriction clearance restores to draft, preserving all other restriction sources; publication is a separate fresh command. Rejected→draft is an explicit correction/resubmission command after the rejecting owner permits it. Draft/active/paused/rejected→archived; archived→draft by explicit restore. Retirement never clears restrictions, destroys Order snapshots or grants a refund. An Offering kind can change in draft only before any Order, delivery or durable external reference; otherwise create a new Offering. isPublic is seller publication intent; effective visibility additionally requires active lifecycle, current SH-024 decision and no applicable restriction. Moderation timestamps are evidence, not independent allow flags.

Adopt immutable owner lifecycle histories for ProfessionalProfile and Offering, with aggregate version, prior/next state, command/source decision identity, actor, timestamp and policy/decision references. Mutations commit history and outbox atomically using expected opaque version plus row serialization for competing transitions; updatedAt alone is not the concurrency token. Publication/activation and seller Order acceptance retain immutable minimized gate decisions/source versions; current actions still reevaluate. Legacy financial/Trust columns remain non-authoritative compatibility projections until a measured reader inventory and forward migration remove them; never backfill authoritative readiness from a legacy boolean.

onboardingCompleteAt is the first successful owner activation after required onboarding facts pass, immutable except an audited data correction. It is not current readiness. ProfileCompleted.v1 may qualify one Gamification rule per profile and rule revision, containing profileId, subject User reference, firstCompletionAt, aggregateVersion, eventId; no raw onboarding facts. Gamification decides awards and source-event dedupe. Reinstatement does not emit another first completion. Dependency changes are owner outbox facts carrying target, changed dimension and source version; Professional/Supply consume idempotently and reevaluate current truth. Do not propagate a copied allow decision indefinitely. Booking availability is not an eligibility prerequisite; a public availability presentation uses Booking's separately authorized query and never changes Professional status.

Public Professional projection allowlist: professionalProfileId, slug, display name, approved biography, accepted active taxonomy IDs/labels/revisions, owner-supplied public avatar rendition reference, Review-owned ratingAverage/ratingCount with reputation version, and SH-131 fuzzy public location when allowed. Public Offering projection: offeringId, professionalProfileId, slug, title, approved summary, kind, accepted taxonomy IDs/labels/revisions, current public pricing summary/currency, approved public rendition references and public delivery/location mode. Each includes sourceVersion and current public-readiness evidence. Exclude User IDs, contact details, exact location, credential documents, provider refs, financial/Healthcare/hold reasons. Search must obtain URLs through approved Media/public rendition rules; no private original URL. Review→Professional transport is an outbox-triggered owner query getProfessionalReputation.v1 returning profileId, ratingAverage, ratingCount, projectionVersion, then a version-checked Professional projection command; stale events trigger current query rather than regress values.

priceFromCents is a rebuildable minimum of currently eligible active pricing options in one currency, not purchase truth. Missing or mixed-currency options produce no priceFrom value, never zero/implicit conversion. Orders bind the selected immutable price/package. isFeatured has no ranking or commercial effect at launch; promotion is deferred pending a separately approved owner policy. Heterogeneous bundle Offering creation remains disabled; this does not disable P02 multi-session packages within supported kinds. No new seller entitlement gates: supported effects remain approved Professional commission terms; unknown keys cannot gate drafting or fabricate quota. SH-016 action keys are activate_profile, public_visibility, publish_offering, respond_to_gig, participate_in_order; payout stays Payment-owned.

Owner status/remediation notifications use committed source-event identity, generic status/remediation template and safe authenticated destination; no sensitive provider/Healthcare/hold details. Notifications do not prove readiness. No generic admin force-ready override: each source owner must authorize and record its own correction, followed by reevaluation. Required verification includes stale-resume versus restriction, archive/restore preserving obligations, projection field exclusion, duplicate first-completion award, and reputation version replay. These are implementation acceptance criteria, not tests already executed.

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.

## WA-R038 — Trust evidence provenance and screening boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

VerificationConsent remains a screening-context linkage: canonical ConsentLogId, identified User/subject, check type, provider, purpose, requirement/package revision and linked check. Generic acceptedAt/IP/user-agent fields are compatibility evidence only and cannot independently validate consent. New linkage requires canonical consent proof and current applicability checks; migration preserves unknown provenance without inventing consent. Each check has exactly one typed subject consistent with its User and optional Professional/Candidate profile; employer-requested screening additionally requires identified Organization/requester membership, Job/Application context, purpose and approved permissible-purpose evidence. Employer sponsorship is not activated by this technical representation.

Adopt the existing minimum Trust §9 check/package/badge graphs. Terminal checks never reopen; recheck is a new linked attempt with current consent/payment/requirement proof. License credential identity stays stable, but every verification/refresh/revocation creates an immutable evidence revision linked explicitly to its establishing VerificationCheck or authorized manual evidence decision. Current credential projection points to a valid revision; expired/revoked proof is never silently overwritten. Trust owns explicit check/credential-to-Media evidence join records, document kind, evidence revision and retention classification. Media owns bytes/scanning/access. No generic Media ownerType/ownerId joins are introduced.

Trust owns append-only check, credential, package/requirement and badge lifecycle histories with aggregate revision and source evidence, committed with outbox. Its provider effect receipt uses provider/account/eventId/handlerVersion uniqueness, fingerprint, check/credential target, normalized event kind, receivedAt, processing and attempt/recovery status, committed transition/effect refs. Unknown subject/events are quarantined; provider callbacks cannot mark a check passed from an unrecognized state. Short-lived provider report access is fetched on demand through an authorized adapter where supported. If persistence is necessary, reportToken is envelope-encrypted secret material with expiry/key version/rotation and restricted audited access; never public DTO/log/Search. Exact provider capability and retention remain external activation evidence.

Requirement rules are immutable schema-versioned records keyed to supported action, typed subject/target, jurisdiction and accepted classification revision; no free-form JSON policy or new implicit mandatory screening. Supported action vocabulary includes profile activation/publication, Offering publication, Gig response/acceptance, Order participation, Booking participation, Job application and Interview participation only where an explicitly approved requirement policy applies. Optional self-initiated Candidate/Professional screening remains optional; action enum presence does not mandate it. Single provider per package at launch; mixed-provider packages are deferred. Provider selection/check-type/jurisdiction rollout must be evidenced before activation, not inferred from a vendor enum.

Identity checks establish only their named verified identity claim; financial readiness stays Payment-owned; a healthcare credential check establishes that credential only, never BAA or Healthcare lane clearance. Broad platform_verified/gold_trust_check/healthcare_verified badges have no launch issuance or authorization effect without explicit scoped claim definitions; preserve legacy facts without minting misleading composite assurance. Public badge DTOs contain the approved claim label/type, subject profile reference, validity and evidence revision only. A badge never replaces current owner readiness.

FCRA technical evidence must link immutable notice template/version/content hash, identified recipient, approved purpose/check/report revision, delivery attempt and verified delivery outcome, policy/jurisdiction version, legally determined timing anchors, dispute submissions and outcome, final-action authorization and history. Notification delivery receipt is evidence, not a legal conclusion. Exact notice content, channels, required waits, adverse-action transitions and retention remain EXTERNAL_REQUIREMENT; no numeric windows or automated adverse decisions are approved here. Required tests cover consent-link mismatch, recheck history, expired supporting evidence, duplicate/late callback, secret exclusion and subject-context mismatch.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P16

A Professional may report completion or no-show for an authorized service session. Authorized support may confirm, correct or adjudicate the service-performance state where policy permits; the Customer can contest the report. Preserve immutable report/correction history, reporting actor and authority, occurrence/recorded time, evidence references, affected session and which participant allegedly failed to attend. A correction references the original; it does not erase it. Reported outcome and contested/adjudicated status are distinguishable, so a Professional assertion is never represented as independent support verification.

Completion/no-show status alone must not automatically trigger refund, charge, payout release, forfeiture, review eligibility or any other financial consequence. Order, Payment/Payout, Review/Dispute, Booking and the applicable policy owner each evaluate their owned consequences from current authorized evidence. A single session report never proves full multi-session Order completion. Clock passage does not fabricate a performance report.


## WA-R049 — Calendar connections, parent references and Location reads

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Implement the architecture contract below only after the coordinated forward schema and concrete owner/consumer contract tests exist. This is sequencing and acceptance criteria, not implementation-completion evidence.

Booking owns CalendarConnection semantics and provider event mappings through SH-067. Canonical access mode is a controlled enum mapped to allowed operations; freeBusyOnly/metadataReadAllowed/eventWriteAllowed and legacy accessMode text are derived compatibility projections, never independent authority. Effective permission is the intersection of current canonical Consent proof, requested canonical mode, current provider scopes and current Role authority. Conflicting legacy fields block writes until normalized; scope strings alone never establish Consent. Preserve consent version/proof and provider account/calendar identity privately.

Expose `synchronizeContextCalendarEvent.v1` and `cancelContextCalendarEvent.v1` through the Booking-owned Calendar service. Input: authenticated owner service context, typed parent `{kind: booking|job_interview, id, revision}`, canonical connection reference, current schedule `{start,end,timeZone}`, operation idempotency key and owner-issued participant/authority decision references. The service validates the parent through its owner and connection permissions; Interview remains its lifecycle owner and is never converted into Booking. Output: normalized pending/applied/rejected/reconcile_required state, stable mapping ID, parent revision, effect receipt and safe reason. No raw OAuth secret or provider response leaves the adapter. Provider event IDs are private mapping attributes, distinct from Booking/Interview IDs, connection IDs and orchestration IDs. Legacy provider reference fields are read-only correlation projections pending migration.

One mapping per connection/calendar/typed parent is current; record every schedule revision and provider effect receipt. Serializing on that mapping and rejecting stale revisions prevents an old reschedule from overwriting the new one. Cancellation targets the mapped event and revision, including replacement lineage; retries reuse logical effect identity. Ambiguous provider timeout produces reconcile_required and owner provider-state lookup before a second create. Disconnect/revocation disables further writes and invalidates sync readiness; provider deletion acknowledgement is distinct from local disconnect. A provider success never changes Booking or Interview acceptance/performance state. Interview's P18 past-slot guard belongs to Interview even when a calendar entry remains visible.

Booking exact-location data is a non-authorizing cache of Location's versioned source reference. Keep Location-owned record identity/source revision and minimal scheduling metadata, not an independent reveal policy. `getBookingOwnerFacts` supplies Booking id/revision, Order/session authorization reference, current status, start/end, participant references and overtime policy. Location combines fresh facts with its own reveal rules. An unavailable/mismatched Location decision denies exact disclosure; cached exact coordinates/address cannot bypass it. Location revocation or source change invalidates caches and credentials; delayed events require current owner revalidation at use. Exact addresses, provider event payloads and credentials stay out of public events/search.

Verify consent withdrawal versus sync, mismatched legacy modes, replacement/cancel race, ambiguous create response, old provider callback, cross-parent mapping attempts and reveal after cache revocation. Provider capability verification, numerical TTL configuration and forward mapping migration remain required before production.


## WA-R050 — Media stewardship, access evidence and export artifacts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Implement the architecture contract below only after the coordinated forward schema and concrete owner/consumer contract tests exist. This is sequencing and acceptance criteria, not implementation-completion evidence.

Physical code/repository stewardship for contextual attachment joins follows their semantic owner: OrderFile belongs in Transaction / Order; MessageMedia in Messaging; ProfessionalProfileMedia in Professional Eligibility; OfferingMedia in Marketplace Supply; candidate/resume associations in Candidate Application. Any additional explicit association is placed in its parent business owner, not in a generic Media ownership repository. Prisma remains one coordinated schema/migration surface; storage placement is not lifecycle ownership. Media repositories mutate only Media assets, versions, renditions, upload sessions, grants and technical proof. Owners create/detach contextual joins after Media readiness checks; cross-owner cascade deletion is prohibited without Privacy disposition. This settles MFA-UR-03 without requesting cosmetic table migration.

Keep three distinct identities: contextual owner authorization/grant, Media transport grant/token, and actual delivery observation. `requestMediaAccess` receives authenticated actor/service, exact Media version, purpose/action, owner context and current decision proof; Media rechecks safety, sensitivity, expiry and revocation. Agreement document-view/download grants are reusable within bounded validity and current authorization; a renewed grant is a new decision linked to its predecessor. No perpetual renewal or automatic download entitlement follows possession. Issuance alone never marks `used` or completion. For reusable access, first-use is observation evidence, not terminal state; one-time transport policy may consume its own token atomically only when expressly specified, without consuming a Digital Goods logical-download allowance. Old ambiguous `used` values require migration classification and cannot silently deny an otherwise approved reusable flow.

Digital Goods duplicate filename/mime/size/checksum/version fields are immutable purchased/delivered version snapshots only. Current Media availability, safety, quarantine, deletion and access decisions govern each serving attempt; historical snapshot values never authorize bytes. The source identity cannot drift to a new asset version under an old purchase merely because metadata matches.

Privacy export bundle creation uses existing `createMediaUploadSession` with Privacy job/bundle/version context and owner authorization, then uploads through the returned Media-owned bounded mechanism, then `completeMediaUpload`. Completion is asynchronous if validation/scanning/processing remains; `getMediaUploadStatus` and `getMediaReadiness` return finalized version/readiness evidence. Privacy may report artifact-ready only for a private ready version and its complete owner contribution manifest, never merely upload acceptance. Logical key is Privacy job+bundle revision; same key replays session/artifact result, changed bytes conflict or require a new revision. A failed scan prevents distribution; incomplete upload resumes/retries the same session where supported, otherwise supersedes it with recorded lineage. Privacy evaluates export requester/current authority, Media applies SH-127, and sensitive proof follows WA-R023. No public export URL is persisted.

Upload-session state is separate from MediaAsset state: initiated→uploading→uploaded→validating→scanning (when required)→processing (when required)→completed, with failed/rejected/cancelled/expired terminal attempts. Required stages cannot be skipped by provider success. A retry after terminal failure creates a linked new attempt; ready/frozen/deleted are asset states only. Immutable policy revision identity is stored on the attempt; changes do not rewrite historical validation criteria, while current safety can still block serving. Scanner callbacks are required only if a selected provider uses callbacks; when used they pass canonical verification/dedupe/normalization.

Production scanner selection, encryption/key qualification, legal retention and broad public-original exposure remain separately gated; do not infer vendor approval. Verify detached associations retaining shared bytes, concurrent access/revocation, grant renewal, failed download not consuming allowance, stale snapshot quarantine, export failure/retry and policy revision replay before activation.


## WA-R051 — Video generation recovery and controlled delivery

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Implement the architecture contract below only after the coordinated forward schema and concrete owner/consumer contract tests exist. This is sequencing and acceptance criteria, not implementation-completion evidence.

Retain terminal live room generations. Authorized recovery of failed/expired/cancelled infrastructure creates a new monotonically identified generation under the same Booking or JobInterview parent, after current owner readiness/authority permits recovery. It does not reset the terminal generation or the parent lifecycle. Exactly one current generation selector exists per typed parent, changed under aggregate serialization; one provider-create effect identity per generation prevents duplicate rooms on retry. Ambiguous create outcome must reconcile that same generation before another provision. Once a generation is superseded, credentials for it are ineligible and revocation/closure is requested from the adapter. Existing parent-unique room rows require a forward generation representation; no implementation may bypass their constraint by duplicate insert.

`provisionBookingVideoRoom` / `provisionInterviewVideoRoom` bind parent ID/revision, generation, owner readiness proof, authorized participant scope and logical provisioning key; output generation ID/state/effect receipt. `issueVideoJoinCredential` rechecks current parent schedule/status/participant rights and current generation. Validity is bounded by the parent-owned approved join policy and server time; Booking supplies overtimeGraceMinutes, Interview supplies its own current schedule policy. No local early-join/overtime default exists; missing required numerical policy blocks activation of that path. Persistent Video access proof records actor, typed parent/revision, room generation, action, allow/deny reason, policy/decision refs, issuance expiry, request time and provider effect confirmation where present. Domain proof commits before credential disclosure; Audit transport cannot substitute it. Provider membership observation is separate from issuance and from service completion.

For on-demand ingest, Video requests purpose-bound Media access for an exact ready source version through SH-127. Default architectural transport is a bounded server-side transfer coordinated by Media to the qualified StreamingVideoProviderPort upload destination; an adapter may use a short-lived provider-fetch URL only when Media authorizes that purpose and selected provider capability verifies it. Video never reads R2 credentials/keys or exposes permanent source URLs. Retries bind source version/checksum and ingest effect identity; source quarantine/revocation prevents new transfer, and conflicting late callbacks cannot activate superseded content. Provider capability/limits/expiry and sensitive-content qualification remain external gates, not assumed vendor behavior.

Thumbnails use an explicit Media rendition/asset reference owned by the Video presentation relationship. Provider thumbnailUrl is private correlation only. The source owner must approve public-safe rendition eligibility and Media safety before client/Search exposure; no direct provider URL projection. CourseDetails.offeringId remains canonical course identity; any redundant Video offeringId must agree, with mismatches quarantined for migration. isDownloadable remains non-authorizing compatibility metadata and cannot bypass Digital Goods policy.

Playback grants are reusable within approved validity, current Order/Digital Goods entitlement and Video readiness. Multiple independently authorized playback grants may coexist; no single-device/session product restriction is invented. Same logical grant issuance replays; fresh session request can create a new grant. First credential use is evidence, not a terminal used status. Revocation/expiry denies subsequent issuance even if a worker is late; provider credential limits must bound already-issued exposure. Playback is not a logical file download and does not consume P10 allowances. Retain start/completion proof at its correct evidence strength; a client progress callback alone cannot prove verified completion. High-frequency progress is optional sampled/coalesced analytics, off until privacy/volume policy exists, and never required authoritative lifecycle history.

Verify concurrent recovery, old-generation join, unknown provider result, provider-create timeout, cancelled/past parent, fresh participant revocation, quarantined ingest, superseded callback, private thumbnail leak and repeated playback without false consumption. Healthcare vendor approval, live provider choice, retained-proof durations and adapter revocation/TTL capability remain prerequisites.


## WA-R052 — Commerce source events and projection contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Implement the architecture contract below only after the coordinated forward schema and concrete owner/consumer contract tests exist. This is sequencing and acceptance criteria, not implementation-completion evidence.

Owner events carry immutable eventId, event name/schemaVersion, aggregate ID/revision, occurredAt, causationId/correlationId, safe typed actor reference and minimum immutable outcome evidence. Write owner history and outbox atomically. Consumers retain durable semantic effect identity and last applied source version beyond transport inbox expiry; duplicate aliases cannot repeat effects. Public commands and queries remain distinct from facts.

| Producer contract | Minimum scoped payload | Consumer effect |
| --- | --- | --- |
| order.outcome_changed.v1 | Order ID/revision, source kind/id, frozen purchase revision, operational outcome, dispute cycle reference if relevant, authorized disposition reference | Gig records matching assignment projection; Digital Goods/Booking reevaluate their own current rights; no automatic financial or review action |
| booking.performance_reported.v1 | Booking ID/revision, Order/session authorization ref, completed/no_show allegation, reporting actor, alleged absentee for no-show, evidence ref, contest state | Order records evidence and evaluates policy; never treats allegation as automatic package completion |
| booking.performance_adjudicated.v1 | same identity plus support authority, prior report ref, correction/adjudication outcome and evidence | Order reevaluates; preserve original report and prior decisions |
| booking.confirmed.v1 / rescheduled.v1 / cancelled.v1 | Booking ID/revision, Order/session ref, schedule revision, authorized participant refs, safe reason | Video/calendar/Messaging setup or invalidation through their owners; Notification receives source-directed safe recipient references |
| review.reputation_changed.v1 | Professional ID, source/projection version and changed Review ID/revision; no private comment/evidence | Professional/Search refresh via getProfessionalReputation.v1, apply only current version |

Booking owns BookingEventActor and BookingLocationType vocabularies. Domain actor values distinguish customer/professional/support/system and retain authenticated User attribution where lawful; no free-text role can authorize a transition. Its existing completed/no_show event aliases normalize to performance-report facts, not adjudicated or commercial-completion facts. Existing proposed booking.* / calendar.* names in §12 become the owner event namespace; only the specific registered semantics qualify integration. Existing OrderCreated/OrderCompleted-style aliases normalize at ingress to their owner versioned equivalent with original event identity, never publish duplicate semantic facts. This table is architecture, not evidence of implemented producer/consumer compatibility.

Review owns `getProfessionalReputation.v1`: request Professional ID with caller context and optional known projection version; response ratingAverage (nullable when count=0), ratingCount, source revision, projection revision, asOf and readiness/staleness result. Fractional aggregate is valid under P06. A refresh event invalidates/reloads this query; consumers cannot recompute from private Review rows or mistake missing/unready result for a zero rating. Hidden/removed Reviews withdraw exactly their existing contribution; revision updates do not add a rating count. Bilateral race, tombstone and replay fixtures are required before freeze.

Notification routing remains source-selected and asynchronous: material accepted-term/proposal changes and appointment/case participant-visible changes carry an authorized destination and affected participant references; failure to deliver cannot roll back owner truth. Private adjudication/evidence never enters participant notifications. P19 uses the Order conversation with Booking/case links; those links do not expand access. Optional viewed/shortlisted alerts stay inactive absent an approved trigger/template policy. This identifies source facts; final template/recipient fan-out matrix remains with Notification convergence.

Gamification may qualify Order completion or eligible reputation changes only through its versioned rule catalog and original source event identity; propagated Gig completion is not a second earning fact. Hold consumers evaluate scoped action decisions and preserve restriction provenance; release only triggers reevaluation, never automatic restoration. Moderation commands use authorized target/action/revision plus durable receipt and local owner execution. Exact shared action, assurance, reward rule and Notification contracts still require canonical cross-rail convergence; this owner event contract does not promote adjacent proposed SH operations.

## WA-R071 — Purpose-specific Location facts and disclosure — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Booking supplies fresh versioned schedule/participant/performance/source facts to Location; source caches never authorize. Missing active-service evidence denies exact disclosure. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## WA-R072 — Hiring compatibility and forward migration stewardship — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Hiring owns JobMedia association stewardship; Media remains byte/readiness/access owner. Forward compatibility migration is additive, provenance-qualified and integration-owned; no schema change is implied. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## WA-R073 — Interview access interval and bounded credentials — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Interview is the parent authority for Video credentials. Launch join interval is half-open scheduled time, without implicit grace; bound credential expiry to parent/current authority/provider limits and qualify revocation/disconnect separately. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## WA-R081–083 — Integrated bridge sequence

Follow Module owner contracts and the complete bridge inventory before cross-Cluster integration. CONTRACT_ONLY work may establish schemas/fakes; FOUNDATION_CAPABILITY is required before actual effects; executable bilateral and external evidence precede freeze/activation. R081 named queries/receipts, R082 Media invalidation, and R083 disabled optional paths supersede only the corresponding historical open labels. Keep current source checks at action/disclosure boundaries. Do not begin whole-Cluster parallel work, root synthesis or runtime implementation from source-coverage counts alone.
