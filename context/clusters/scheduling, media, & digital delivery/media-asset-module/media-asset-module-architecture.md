# Media / File Access Module Architecture

> **Module ID:** `media_file_access`  
> **Module name:** Media / File Access Module  
> **Module type:** `capability_compliance_support`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Document status:** implementation-grade Module architecture for the Workin Ants MVP  
> **Audience:** coding agents, developers, reviewers, maintainers, security reviewers, and architecture reviewers  
> **Relationship to root architecture:** subordinate to root Workin Ants architecture and project-wide standards. Root ownership and platform rules win if a future explicit root decision conflicts with this file.  
> **Relationship to Cluster architecture:** this file specializes the CL-05 architecture for `media_file_access`. The Cluster coordinates sequencing and cross-Module collaboration; this Module owns only the file/media truth declared here.  
> **Update rule:** update this file whenever a binding Media ownership, lifecycle, public-contract, provider, security, privacy, retention, or contextual-attachment decision changes. Build progress must not silently redefine this architecture.

## Evidence Basis

This architecture is grounded in the current Workin Ants evidence set supplied for this thread:

- Media / File Access Module Architecture Extract;
- current Deep Module Registry;
- Cluster Registry `v2.3-customer-subscription`;
- current Prisma schema;
- Ubiquitous Language / Compliance Inventory;
- Canonical Shared Operations Registry (`SH-001` through `SH-126`);
- CL-05 `architecture.md`;
- CL-05 `build-plan.md`;
- root `project-overview.md`;
- directly relevant owner-boundary evidence for Role / Authority, Privacy / Data Erasure, Healthcare / Regulated Services, Content Moderation & Legal Notice, Transaction / Order, Candidate Application & Resume Privacy, Messaging, Digital Goods Access, and Video Session.

Evidence conflicts are resolved by preserving one source-of-truth owner per lifecycle and by preferring the canonical glossary/shared-operation ownership rule when a historical Module registry claim is broader than the later cross-Module ruling.

---

## 1. Module Header

### Identity

`media_file_access` is the canonical Workin Ants capability for file mechanics, secure upload, object-storage metadata, file safety proof, processed derivatives, generic temporary media access, and short-lived signed object delivery.

It exists inside CL-05 because file delivery is one of the Cluster's delivery substrates, but its services are consumed by Modules across marketplace, hiring, messaging, transactions, moderation, healthcare, privacy, and video.

### Architectural posture

This Module is **not** a generic “attachment business domain.” It is the technical and compliance owner of the file itself.

The binding distinction is:

```text
business Module owns why the file belongs to a business object
→ Media owns whether the file is safe, how it is stored, and how it is temporarily exposed
```

The Ubiquitous Language rule is controlling:

```text
MediaAsset = file truth
contextual join = business meaning owned by the contextual Module
```

---

## 2. Purpose, Goal, and Transformation

### Purpose

Provide one hardened platform boundary for accepting untrusted files, storing them safely, validating/scanning/processing them, representing the resulting file as a canonical `MediaAsset`, and issuing temporary object access only after upstream context has authorized the action.

### Goal

A consumer Module should never need to implement its own R2 client, MIME checker, malware scanner, EXIF scrubber, private-object key generator, generic signed-URL service, or generic MediaAsset lifecycle.

A consumer Module should be able to say:

```text
this actor is allowed to attach/view/download this business resource
→ Media confirms the underlying asset is safe and deliverable
→ Media issues bounded file access or returns a stable denial
```

### What enters

Typical inputs include:

- authenticated actor/system context;
- a `MediaUploadContext`;
- an owner-validated target reference where the upload is contextual;
- original filename and declared MIME metadata as untrusted hints;
- uploaded bytes in quarantine/private storage;
- the active Media upload policy for that context;
- an upstream contextual access decision;
- ComplianceHold decision when applicable;
- Healthcare access/readiness decision when applicable;
- authoritative moderation/legal execution instruction;
- authoritative Privacy instruction and retention result;
- provider results from object storage, scanner, and processing adapters.

### What leaves

Typical outputs include:

- `MediaUploadSession` progress/result;
- canonical `MediaAsset` metadata and lifecycle state;
- `MediaValidationResult` proof;
- `MediaScanResult` proof;
- `MediaProcessingResult` proof;
- safe original/derivative relationships;
- `MediaAccessGrant` temporary access state;
- short-lived signed provider URL;
- `MediaAccessEvent` access/delivery evidence;
- owner-executor acknowledgments for moderation/privacy actions;
- domain events when a committed Media fact requires downstream reaction;
- Audit/Observability requests through canonical shared operations.

### Capability transformation

```text
untrusted upload request
→ authenticated/authorized context
→ active MediaUploadPolicy
→ opaque quarantine object key
→ upload session + private object
→ server-side byte validation
→ malware scan when policy requires
→ metadata scrub / derivative processing when policy requires
→ checksums + immutable proof records
→ MediaAsset.ready
→ optional contextual attachment by contextual owner
→ later contextual access decision
→ Media local readiness/grant checks
→ short-lived signed delivery
→ MediaAccessEvent + sensitive access audit when required
```

### Why this deserves its own Module boundary

File-security rules are cross-cutting, provider-backed, privacy-sensitive, and too security-critical to be recreated by every business Module. At the same time, file mechanics are semantically different from the business reason a file exists. A dedicated Module centralizes the security and storage substrate without absorbing marketplace, hiring, message, transaction, agreement, digital-good, or video policy.

---

## 3. Owned Truth

### 3.1 Schemas / Models owned

#### `MediaAsset`

The canonical Workin Ants record for a stored file or processed derivative.

It owns:

- storage location metadata;
- file-size and MIME metadata;
- checksum;
- upload context;
- technical sensitivity and storage visibility;
- file technical lifecycle;
- freeze/revocation/erasure effects at the file layer;
- original/derivative relationship;
- validation, scan, and processing summary state.

It does **not** own why the file belongs to an Offering, Message, resume, Order, Agreement, download product, or course.

#### `MediaUploadPolicy`

The technical upload-security policy for one `MediaUploadContext`.

It governs:

- maximum byte size;
- allowed MIME types;
- allowed extensions;
- binary inspection requirement;
- malware-scan requirement;
- EXIF scrub requirement;
- public-derivative allowance;
- original-public allowance;
- default bucket class;
- default storage visibility;
- default signed URL TTL.

It is not permission truth and does not authorize a contextual attachment.

#### `MediaUploadSession`

Proof and progress for one upload attempt before/during validation, scanning, processing, and completion.

It records request context and file-intake facts without replacing `MediaAsset` as file truth.

#### `MediaValidationResult`

Proof that a specific technical validation operation passed, failed, or was intentionally skipped under policy.

It records declared vs detected MIME/extension, binary signature evidence, validator implementation/version, and rejection reason.

#### `MediaScanResult`

Proof of malware/security scanning for an uploaded object.

It records scanner/provider/version, provider scan reference when present, threat evidence, normalized scan state, and safe failure detail.

A clean scan does not prove moderation approval, credential validity, or business eligibility.

#### `MediaProcessingResult`

Proof of a technical transformation such as:

- EXIF scrub;
- image resize;
- image compression;
- thumbnail creation;
- PDF metadata scrub;
- filename obfuscation;
- quarantine move;
- promotion to ready;
- public derivative creation.

It may link source and derived `MediaAsset` records.

#### `MediaAccessGrant`

Generic temporary authorization state for delivery of a private `MediaAsset` **after** contextual authorization has already been established.

It owns:

- grant status;
- target reference;
- token/signature hashes where used;
- reason/denial/revocation evidence;
- expiry;
- first-use evidence.

It does not own Order entitlement, resume access policy, message participant policy, Agreement entitlement, DigitalDownload entitlement, or CourseVideo playback entitlement.

#### `MediaAccessEvent`

Append-only Media-domain proof of generic object-access activity such as signed URL issuance/denial, view/download evidence, grant expiry/revocation, blocked access, and provider errors.

It is separate from `AccessAuditLog`, which is generic sensitive-access proof owned by Audit / Event Ledger.

### 3.2 Contextual media joins

The physical Prisma schema currently contains or relates to joins such as:

- `UserMedia`;
- `ProfessionalProfileMedia`;
- `CandidateProfileMedia`;
- `OrganizationMedia`;
- `OfferingMedia`;
- `GigMedia`;
- `JobMedia`;
- `MessageMedia`;
- `JobApplicationMedia`;
- `OrderFile` and other contextual references.

Registry placement does not transfer contextual lifecycle ownership: **the contextual Module owns the business meaning of its join; Media owns the `MediaAsset` mechanics.** CL-03-R020 approves this split for `ProfessionalProfileMedia`: Professional Eligibility owns contextual attach/detach/reorder semantics and authorization; Media owns the referenced asset and generic file mechanics.

### Ruling MFA-PR-01 — contextual join stewardship (split approved by CL-03-R020)

Until root architecture explicitly moves schema/code placement, preserve current schema placement where it already exists, but enforce these semantic rules:

- contextual Module owns creation/deletion policy for the attachment relationship;
- contextual Module owns role/sort/order/business meaning;
- contextual Module owns contextual authorization;
- Media exposes readiness/technical facts and never infers the business relationship;
- `SH-090 attachValidatedMedia` is executed by the contextual owner, not by a generic Media “attach anything” service.

This ruling prevents Media from becoming a god Module while avoiding unnecessary schema movement solely for aesthetics.

### 3.3 Enums / statuses owned

- `MediaUploadContext`
- `MediaStorageVisibility`
- `MediaStorageBucketClass`
- `MediaValidationStatus`
- `MediaScanStatus`
- `MediaProcessingStatus`
- `MediaRejectionReason`
- `MediaAccessGrantStatus`
- `MediaAccessEventType`
- `MediaProcessingActionType`
- `MediaUploadPolicyStatus`
- `MediaAssetStatus`

`DataSensitivity` is consumed heavily by Media but is cross-cutting vocabulary and is not newly claimed by this Module here.

### 3.4 Lifecycles owned

Media owns:

1. Media technical file lifecycle;
2. Media upload-policy lifecycle;
3. Media upload-attempt lifecycle;
4. validation proof lifecycle;
5. malware scan proof lifecycle;
6. processing proof lifecycle;
7. generic Media access-grant lifecycle.

### 3.5 Domain events / ledgers owned

- `MediaAccessEvent` is persistent Media access evidence.
- Media may publish versioned domain events for committed state changes through `SH-046` when another Module has a legitimate asynchronous reaction.

Approved event family for this Module:

- `media.asset.ready`
- `media.asset.rejected`
- `media.asset.failed`
- `media.asset.frozen`
- `media.asset.restored`
- `media.asset.deleted`
- `media.access_grant.issued`
- `media.access_grant.revoked`
- `media.access_grant.expired`

Events are emitted only when an external consumer exists; the database record remains source truth.

### 3.6 Projections owned

Media does not own a search projection.

Media may own internal read models derived directly from Media tables for:

- readiness inspection;
- upload progress;
- safe admin/debug inspection;
- storage reconciliation.

Those read models are rebuildable and never replace source records.

### 3.7 Snapshots / proof owned

Media owns technical proof including:

- byte checksum;
- binary-type detection result;
- scan provider/version/result hash;
- processing input/output checksum;
- metadata/GPS removal proof;
- grant expiry/revocation/first-use evidence;
- signed URL hash rather than durable signed URL value.

A Media checksum is not Agreement legal hash proof unless Transaction / Order explicitly binds it into its own `AgreementDocumentSnapshot` proof.

### 3.8 Policies / invariants owned

Media owns:

- quarantine-first intake;
- technical upload acceptance by context;
- technical file-type validation;
- malware scan requirement execution;
- metadata scrubbing requirement execution;
- storage-bucket and visibility mapping;
- promotion-to-ready rules;
- file-level freeze/revocation enforcement;
- generic Media grant TTL and Media-ready access checks;
- object-storage provider mechanics.

---

## 4. Explicit Non-Ownership

The following responsibilities must never be pulled into `media_file_access` for implementation convenience.

| Adjacent owner | Truth that remains external | Media may do | Media must not do |
| --- | --- | --- | --- |
| Identity & Access | authenticated User/system identity | consume actor context | create local session/current-user/auth helpers |
| Role / Authority | platform/org/participant/ownership permission interpretation | supply Media action/resource facts and consume decision | encode a generic permission engine |
| Marketplace Supply | Offering lifecycle and Offering-media business meaning | return Media readiness; store/serve MediaAsset | decide whether an Offering may own/display media |
| Gig / Demand | Gig lifecycle and Gig-media meaning | store/serve ready media | decide Gig attachment role/eligibility |
| Organization Hiring | Organization/Job lifecycle and logo/job-graphic meaning | store/serve ready media | infer recruiter/org authority or Job publication policy |
| Candidate Application & Resume Privacy | resume/application meaning, resume-specific viewer policy, `ResumeAccessLog` | store/scans/sign underlying file | decide authorized recruiter/application relationship or replace ResumeAccessLog |
| Messaging | Thread participation, Message lifecycle, `MessageMedia` meaning | store/serve attachment | decide Thread participation or message access rules |
| Transaction / Order | Order entitlement, `OrderFile` role, Agreement lifecycle/hash/access-grant truth | store private bytes and sign MediaAsset access when requested | infer paid status, Agreement completion, contract entitlement, or legal hash truth |
| Digital Goods Access | `DigitalDownloadAsset`, `DigitalDownloadGrant`, download usage/license/refund policy | serve underlying ready MediaAsset | issue paid entitlement from MediaAsset alone |
| Video Session | Mux/live-video resource state, course playback grant, provider event lifecycle | provide ready raw source file | own Mux asset/playback/join state |
| Healthcare / Regulated Services | healthcare lane/readiness, data-boundary and admin-access policy | enforce returned block/redact/allow outcome | determine BAA/healthcare eligibility or invent PHI policy |
| Content Moderation & Legal Notice | Report/LegalNotice/ModerationCase/ModerationAction decision truth | execute freeze/public-access/revocation/restore instruction | decide DMCA/DSA/legal validity |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob, DataErasureTarget, DataRetentionExemption | inventory and execute owner-specific erasure/anonymization/provider deletion | create parallel privacy workflow or legal-retention exemption truth |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | request audit writes | replace audit with MediaAccessEvent or write a parallel generic audit ledger |
| Search / Public Visibility | SearchUpsertEvent and Typesense projection truth | request refresh if a Media fact affects public readiness | write Typesense/SearchUpsertEvent directly |
| Notification | Notification and delivery/provider truth | request safe notification when a defined Media business trigger needs one | call email/SMS/push providers directly |
| Observability / Ops | logs, IntegrationFailure, QueueJob telemetry, OpsIncident | supply safe operation context | use operational records as Media lifecycle truth |

### Concrete prohibited ownership shortcuts

Media must not create:

- `isPaid` / `canDownload` / `ownsFile` business truth;
- generic `isBlocked` / `onHold` truth;
- `isHealthcare` User flags;
- resume permission rules;
- message participant rules;
- Agreement signature/tamper policy;
- `DigitalDownloadGrant` or `CourseVideoPlaybackGrant` replacements;
- direct Typesense integration;
- local notification provider clients;
- local privacy-request orchestration;
- a generic `DeliveryService` or `AttachmentService` that interprets every domain.

---

## 5. Module Architecture Principles

1. **MediaAsset is file truth, not business attachment truth.**
2. **Untrusted bytes are quarantined before they are trusted.**
3. **A client-provided filename, extension, or MIME type is never sufficient proof.**
4. **Policy-required validation/scanning/processing must succeed before `MediaAsset.ready`.**
5. **Required malware scanning fails closed.** Scanner outage is not equivalent to `clean`.
6. **Original filenames never become storage keys.**
7. **Private/sensitive/legal/healthcare media is not exposed through permanent public URLs.**
8. **Public images should normally be processed derivatives rather than raw originals.**
9. **Signed delivery is not entitlement.** A contextual owner must authorize the business action before Media issues access.
10. **Generic grant mechanics may be shared; grant truth remains separate by domain.**
11. **`MediaAccessEvent` and `AccessAuditLog` are different proof ledgers.** Write both where policy requires.
12. **Public URL removal is not evidence deletion.** Freeze/restrict access while retaining bytes when instructed.
13. **Product deletion is not privacy erasure.** `MediaAsset.deleted` and `erasedAt`/Privacy instructions have separate meaning.
14. **R2/object-store state is infrastructure, not Workin Ants truth.**
15. **Provider-specific types terminate at adapters.**
16. **Slow scan/processing/deletion work uses durable jobs, not request-bound promises.**
17. **Retry only transient technical failures.** Malware, invalid MIME, denied authorization, legal block, and expired grant are not retryable technical failures.
18. **Every destructive/provider action is idempotent and observable.**
19. **Telemetry is minimized.** Never log raw signed URLs, object contents, PHI, identity-document content, resume text, contract text, or provider secrets.
20. **A context owner can be changed without rewriting Media’s core safety logic.**

---

## 6. Proposed Folder / Code Structure

Use root repository conventions if they differ. This is the intended responsibility map, not permission to create a competing root structure.

```text
src/modules/media-file-access/
├── actions/                     # route/server-action adapters only if root architecture uses them
│   ├── create-media-upload-session.ts
│   ├── complete-media-upload.ts
│   └── request-media-access.ts
├── commands/
│   ├── create-media-upload-session.ts
│   ├── complete-media-upload.ts
│   ├── reject-media-upload.ts
│   ├── promote-media-asset.ts
│   ├── issue-media-access-grant.ts
│   ├── revoke-media-access-grant.ts
│   ├── execute-moderation-instruction.ts
│   └── execute-privacy-instruction.ts
├── queries/
│   ├── get-media-readiness.ts
│   ├── get-media-asset-metadata.ts
│   ├── get-media-upload-status.ts
│   └── get-active-media-upload-policy.ts
├── schemas/
│   ├── command-inputs.ts
│   ├── public-contracts.ts
│   ├── decision-results.ts
│   └── provider-results.ts
├── domain/
│   ├── policies/
│   │   ├── upload-policy.ts
│   │   ├── asset-transition-policy.ts
│   │   ├── access-policy.ts
│   │   ├── storage-class-policy.ts
│   │   └── retry-classification.ts
│   ├── lifecycles/
│   │   ├── media-asset-lifecycle.ts
│   │   ├── upload-session-lifecycle.ts
│   │   └── media-access-grant-lifecycle.ts
│   └── events/
│       ├── media-events.ts
│       └── media-event-payloads.ts
├── services/
│   ├── upload-intake-service.ts
│   ├── media-readiness-service.ts
│   ├── media-processing-service.ts
│   └── media-access-service.ts
├── contracts/
│   ├── public-commands.ts
│   ├── public-queries.ts
│   ├── contextual-access-contract.ts
│   ├── moderation-executor-contract.ts
│   └── privacy-executor-contract.ts
├── providers/
│   ├── object-storage/
│   │   ├── object-storage-port.ts
│   │   └── cloudflare-r2-adapter.ts
│   ├── malware/
│   │   ├── malware-scanner-port.ts
│   │   └── scanner-adapter.ts          # concrete provider added only when selected
│   └── processing/
│       ├── media-processor-port.ts
│       ├── sharp-image-processor.ts
│       └── pdf-metadata-processor.ts   # only when implementation is selected
├── workers/
│   ├── validate-media-upload.ts
│   ├── scan-media-upload.ts
│   ├── process-media-upload.ts
│   ├── promote-media-upload.ts
│   ├── expire-media-access-grants.ts
│   ├── cleanup-media-quarantine.ts
│   └── reconcile-object-storage.ts
├── privacy/
│   ├── enumerate-subject-media.ts
│   ├── evaluate-media-retention.ts
│   └── execute-media-privacy-instruction.ts
├── repositories/
│   ├── media-asset-repository.ts
│   ├── media-upload-repository.ts
│   ├── media-proof-repository.ts
│   └── media-access-repository.ts
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── provider/
    ├── security/
    ├── privacy/
    └── e2e/
```

### Folder constraints

- Do not put contextual attachment repositories under this Module solely because they reference `MediaAsset`.
- Do not create `auth/`, `permissions/`, `queue/`, `audit/`, `notifications/`, `search/`, `crypto/`, or generic `shared/` implementations here. Consume the canonical shared operations.
- `providers/` contains Media-owned adapters only: object storage, malware scanning, and Media processing.
- No Stripe, Cronofy, Mux, Daily/Agora, Typesense, email, SMS, or push provider clients belong here.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery/UI adapters | validate transport input, call public application commands/queries, return safe result | domain authorization logic, direct Prisma access, R2 signing logic |
| Application commands | orchestration of one Media use case, transactions, shared-operation calls | provider SDK details, foreign Module policy |
| Application queries | safe Media facts/readiness/read models | contextual business entitlement inference |
| Domain policy | MediaAsset transition graph, upload policy interpretation, file readiness, grant-local policy, retry classification | Role/Authority, Order, Resume, Message, Agreement, Digital Goods, Healthcare legal policy |
| Repositories/data access | only Media-owned records and necessary same-owner transactional writes | direct repositories for Offering, Order, Message, JobApplication, Privacy, Moderation, Audit |
| Workers | execute Media-owned async validation/scan/process/promotion/cleanup/expiry/reconciliation | generic queue implementation; other Modules’ workflow state |
| Provider adapters | R2/S3-compatible object storage; malware scanner; local/file processing | cross-domain business decisions; unrelated providers |
| Public contracts | stable Media commands/queries/executor protocols | internal provider payloads or Prisma models as public DTOs |
| Privacy executor | enumerate and mutate only Media-owned records/provider objects under Privacy instruction | PrivacyRequest/DataErasureJob lifecycle or legal-retention exemption ownership |
| Tests | owner lifecycle, contracts, security, provider, privacy, integration | testing via direct foreign-table mutation as substitute for public contracts |

---

## 8. Data Model

### 8.1 `MediaAsset`

**Purpose:** canonical stored-file record.

**Key relationships:**

- optional uploader `User`;
- zero or more upload sessions/proof records/access grants/access events;
- self-relation to processed derivatives;
- referenced by contextual joins and delivery Modules.

**Authoritative fields:**

- `storageKey` — unique Workin Ants storage reference;
- `bucket`, `bucketClass`, `storageVisibility` — storage/delivery placement;
- `mimeType`, `declaredMimeType`, `detectedMimeType`;
- `sizeBytes`;
- `checksum`;
- `uploadContext`;
- `dataSensitivity`;
- original/derived metadata;
- `publicUrlRevokedAt`, `frozenAt`, `frozenReason`, `erasedAt`.

**Lifecycle:** `status: MediaAssetStatus`.

**Uniqueness:** `storageKey` is unique.

**Concurrency-sensitive behavior:**

- promotion to ready;
- freeze vs signed access;
- delete/erase vs access issuance;
- restore vs active moderation instruction;
- derivative creation retries.

Use database transactions/row locking or optimistic conflict detection as appropriate. Do not rely on in-memory locks.

**Retention/privacy:**

- object key, original filename, uploader, and metadata may be personal data;
- R2 deletion is required where erasure is allowed;
- legal/financial/Agreement-related media may require retention based on facts supplied by its owner and exemption recorded by Privacy;
- `erasedAt` is legal/privacy effect and is distinct from product `deleted` status.

### 8.2 `MediaUploadPolicy`

**Purpose:** technical upload rules by context.

**Key relationship:** upload sessions refer to the policy used.

**Authoritative fields:** context, status, max size, allowed MIME/extensions, required inspection/scan/scrub, bucket/visibility defaults, signed URL TTL.

**Current schema issue:** `@@unique([context, status])` plus mutable `updatedAt` permits only one row in each status and does not provide immutable historical versions.

### Ruling MFA-PR-02 — version Media upload policies (requirement approved by R009)

R009 makes `SH-080 manageVersionedRules` semantics binding for `MediaUploadPolicy`; the current schema is insufficient and requires a later approved migration before production policy-version behavior is complete:

- activated versions are immutable;
- every upload session resolves one effective policy version;
- later changes create a new version rather than mutating historical policy meaning;
- policy lookup returns the effective active version for context/time;
- schema should support a stable version/effective interval or equivalent immutable version reference.

If the exact root versioning convention is not yet available, Feature 01 may define the public contract and test fixtures while deferring the migration until the shared convention is approved. It must not silently mutate active historical policy rows in production.

### 8.3 `MediaUploadSession`

**Purpose:** one upload attempt and pipeline progress.

**Relationships:** policy, optional `MediaAsset`, uploader, validation/scan/processing results.

**Authoritative fields:** context, target reference, filenames, storage key, detected/declared metadata, checksum, request evidence, rejection/failure reason, pipeline timestamps.

**Current schema issue:** `status` is typed as `MediaAssetStatus`. An upload attempt and stored asset have different lifecycle semantics.

### MFA-PR-03 — dedicated upload-session status (separation required by R010)

R010 requires a dedicated upload-session status representation separate from MediaAsset. The eventual schema must not use `MediaAssetStatus` as the final session vocabulary. The proposed `MediaUploadSessionStatus` representation/graph below is retained for the later schema review; this reconciliation does not perform or select its migration:

```text
initiated
→ uploading
→ uploaded
→ validating
→ scanning        # when required
→ processing      # when required
→ completed

any nonterminal state
→ rejected | failed | cancelled | expired
```

This prevents `MediaAsset.ready`, `frozen`, or `deleted` semantics from being incorrectly reused as upload-attempt state.

Until the migration lands, application code must hide the existing enum leakage behind a typed session-domain contract rather than spreading `MediaAssetStatus` assumptions through consumers.

### 8.4 `MediaValidationResult`

**Purpose:** immutable technical validation proof.

**Lifecycle:** `pending → passed | failed | skipped`.

**Rule:** a terminal result row is not edited into a different conclusion. A rerun creates a new result/provenance entry unless root repository conventions explicitly support append-only attempt versioning another way.

**Retention:** security evidence may need retention independently from user-visible file availability; Privacy controls disposition.

### 8.5 `MediaScanResult`

**Purpose:** immutable malware scan proof.

**Lifecycle:** `pending → clean | suspicious | infected | failed | skipped`.

**Rules:**

- `infected` is a permanent business/security rejection for the current bytes;
- `failed` is a technical failure, not `clean`;
- `suspicious` does not auto-promote;
- `skipped` is allowed only when the resolved policy says scanning is not required.

### 8.6 `MediaProcessingResult`

**Purpose:** proof of one processing action.

**Lifecycle:** `pending → processed | failed | skipped`.

**Important fields:** action type, processor/version, input/output checksum, derivative link, metadata/GPS removal flags.

**Rule:** processing proof describes technical transformation only. It does not confer moderation approval or contextual business eligibility.

### 8.7 `MediaAccessGrant`

**Purpose:** bounded generic MediaAsset delivery grant.

**Authoritative fields:** asset, user, status, target reference, token/signed-URL hashes, reason, denial/revocation reason, expiry, first use.

**Concurrency-sensitive behavior:**

- issue vs duplicate request;
- use vs expiry;
- use vs revocation;
- revocation vs concurrent URL issuance.

Use transaction-safe state validation at request time. Worker-delayed expiry must never make an already-expired grant valid.

### Unresolved MFA-UR-01 — meaning of `used`

Current schema contains `used` plus `firstUsedAt` but no max-use counter. Evidence does not establish whether every generic Media grant is one-time or reusable until expiry.

Binding interim rule:

- do not infer one-time semantics from the enum alone;
- signed access always checks current time and revocation;
- use `firstUsedAt` as evidence where possible;
- do not transition to `used` in a way that invalidates reusable access unless the specific Media access policy explicitly requires one-time use.

A later explicit policy/field decision is required if one-time grants become a supported mode.

### 8.8 `MediaAccessEvent`

**Purpose:** append-only Media-specific access evidence.

**Retention:** may contain request metadata and therefore requires privacy/retention mapping. Do not cascade-delete security evidence without explicit retention analysis.

### Proposed Ruling MFA-PR-04 — destructive cascade review

The current schema uses cascade deletion from `MediaAsset` into Media access records. Before production privacy/product deletion is enabled, review whether access/proof records must be anonymized/retained rather than physically cascaded. Destructive cascade behavior is not accepted merely because Prisma currently permits it.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 `MediaAssetStatus`

Statuses:

```text
uploaded
quarantined
validating
processing
ready
rejected
failed
frozen
deleted
```

### Valid transition policy

```text
uploaded → quarantined
quarantined → validating
validating → processing | ready | rejected | failed
processing → ready | rejected | failed
ready → frozen | deleted
frozen → ready | deleted        # only under authoritative restore/delete instruction
rejected → deleted              # cleanup/product deletion where allowed
failed → deleted                # cleanup/product deletion where allowed
```

Notes:

- A policy requiring scanning may still use `validating`/`processing` as summary states while `MediaScanResult` carries scan-specific truth.
- `ready` is not reachable until every required proof is terminal-success or policy-approved skipped.
- `frozen → ready` requires authoritative restore evidence; Media cannot self-clear a legal/moderation freeze.
- `deleted` is product/file technical deletion state. Privacy erasure additionally follows Privacy instruction and `erasedAt` semantics.

**Transition owner:** Media / File Access only.

**Event/history proof:** proof tables plus Media domain event when an external consumer needs it. Material admin changes may also request `AuditEvent`.

**Prohibited shortcuts:** direct status writes by contextual Modules, “ready” based on upload completion alone, `ready` after required scanner failure, direct restoration without Moderation authority.

### 9.2 `MediaUploadPolicyStatus`

Statuses:

```text
draft → active ↔ paused → retired
          └────────────→ retired
```

Under the R009-approved requirement in MFA-PR-02, an active policy version is immutable; “edit” means create a new draft version and activate it according to `SH-080`.

### 9.3 Upload session lifecycle

See MFA-PR-03. Transition owner is Media application/worker pipeline.

### 9.4 Validation lifecycle

```text
pending → passed | failed | skipped
```

Terminal result rows are evidence and are not rewritten into another outcome.

### 9.5 Scan lifecycle

```text
pending → clean | suspicious | infected | failed | skipped
```

- `clean`: scan requirement satisfied for the tested bytes;
- `suspicious`: remains quarantined pending policy/manual handling;
- `infected`: reject;
- `failed`: technical failure; retry only if classified transient;
- `skipped`: only valid when policy did not require scan.

### 9.6 Processing lifecycle

```text
pending → processed | failed | skipped
```

Each required action must have an acceptable terminal result before promotion.

### 9.7 `MediaAccessGrantStatus`

```text
active → expired | revoked
active → used        # only if an approved one-time-use policy applies
request may terminate as denied
```

**Transition owner:** Media / File Access for `MediaAccessGrant` only.

**Triggers:** issuance, access, explicit revocation, expiry sweep, privacy/moderation/security instruction.

**Concurrency:** request-time status/expiry validation is authoritative even if expiration worker has not yet run.

---

## 10. Commands

### 10.1 `createMediaUploadSession`

**Purpose:** start a bounded upload attempt and return provider-neutral upload instructions.

**Actor/context required:** authenticated actor (`SH-001`), resource action authorization (`SH-002`), owner target validation when a contextual target is supplied (`SH-123`).

**Authoritative inputs:** upload context, target reference, declared filename/MIME/size, idempotency key.

**Preconditions:**

- active/effective upload policy exists;
- action is authorized;
- applicable hold does not block upload;
- target reference is valid when required.

**Writes:** `MediaUploadSession`; provider object intent/reference as allowed.

**Shared operations:** SH-001, SH-002, SH-011 when applicable, SH-044, SH-080, SH-085, SH-123, SH-032, SH-034.

**Events/audit:** normally no broad domain event; material admin/security actions may use SH-029.

**Idempotency:** same semantic key returns the same active/replayable session result unless session is terminal and product policy requires a new attempt.

**Failure modes:** unauthenticated, forbidden, invalid target, no policy, declared size invalid, hold blocked, provider unavailable, idempotency conflict.

### 10.2 `completeMediaUpload`

**Purpose:** acknowledge provider upload completion and trigger the durable validation/scan/process pipeline.

**Inputs:** session ID, provider upload evidence, idempotency key.

**Preconditions:** session exists and is in the expected pre-processing state; object exists under the expected opaque key.

**Writes:** upload session receipt state; creates/links `MediaAsset` if not already created; queues pipeline work.

**Shared operations:** SH-044, SH-047, SH-048, SH-032, SH-037.

**Idempotency:** duplicate completion does not create duplicate semantic assets or duplicate required proof work.

**Failure modes:** missing object, size mismatch, stale session, terminal session, provider failure.

### 10.3 `rejectMediaUpload`

**Purpose:** move an asset/session to a safe rejection state after non-retryable validation/security failure.

**Inputs:** session/asset, stable `MediaRejectionReason`, proof reference.

**Writes:** terminal rejection state/timestamps and proof.

**Shared operations:** SH-053, SH-046 if external consumer reaction is required, SH-029 for material admin/security actions.

**Failure modes:** stale transition/conflict; otherwise deterministic.

### 10.4 `promoteMediaAssetToReady`

**Purpose:** atomically mark a MediaAsset ready only when all required proof has succeeded.

**Preconditions:** effective policy resolved; required validation/scan/processing proof present; no blocking hold/freeze; object in expected storage state.

**Writes:** MediaAsset readiness and promotion evidence.

**Shared operations:** SH-051/052 as needed, SH-053, SH-046.

**Idempotency:** repeat promotion returns already-ready result without duplicate derivatives/events.

### 10.5 `requestMediaAccess`

**Purpose:** the public composite command for authorized generic private MediaAsset access.

**Actor/context:** authenticated actor plus contextual owner decision.

For MessageMedia access, Messaging exposes its owner-specific SH-026 `authorizeContextualResourceAccess` decision bound to the actor, Thread, Message, MediaAsset, and requested action. It returns the contextual allow/deny decision and safe evidence; `ThreadParticipant` or `MessageMedia` facts alone are not authorization. Media consumes that decision through `requestMediaAccess`, independently applies MediaAsset readiness, safety/freeze/erasure, grant, and TTL rules, and owns downstream SH-087 `issueSignedMediaUrl`. Media must not reconstruct Messaging participant/access policy; Messaging must not issue signed URLs or call SH-087 directly.

**Inputs:** asset ID, intended action (`view`/`download` or typed equivalent), contextual authorization decision/evidence, requested TTL bounded by Media policy, target reference, idempotency key.

**Preconditions:**

1. actor resolved;
2. Role / Authority permits the action;
3. contextual owner allows the business action (`SH-026`);
4. applicable ComplianceHold allows action;
5. healthcare access/readiness permits access when applicable;
6. MediaAsset is ready, not frozen, not deleted/erased, and storage visibility/action is compatible;
7. grant policy is satisfied.

**Writes:** `MediaAccessGrant`, `MediaAccessEvent` issuance/denial evidence.

**Shared operations:** SH-001, SH-002, SH-011, SH-020, SH-026, SH-030, SH-044, SH-074, SH-087, SH-088, SH-125.

**Output:** signed URL result with expiry or stable denial.

**Failure modes:** contextual denial, hold block, healthcare block/redaction requirement, not ready, frozen, erased/deleted, expired/revoked grant, provider unavailable.

### 10.6 `revokeMediaAccessGrant`

**Purpose:** revoke a Media-owned temporary grant after an authoritative instruction or owner-local security decision.

**Inputs:** grant ID or typed target scope, authoritative reason/source reference, idempotency key.

**Writes:** MediaAccessGrant status/revocation metadata plus MediaAccessEvent.

**Shared operations:** SH-044, SH-089, SH-125, SH-030 when sensitive.

### 10.7 `executeMediaModerationInstruction`

**Purpose:** implement Media’s handler for `SH-103 executeModerationDecision`.

**Inputs:** authenticated/authorized Moderation action envelope containing case/action IDs, target, action, reason, correlation.

**Allowed effects:** freeze MediaAsset, revoke public exposure, revoke Media grants, preserve evidence, restore file-level exposure under a restore instruction.

**Must not:** determine legal validity or mutate ModerationCase/ModerationAction truth.

### 10.8 `executeMediaPrivacyInstruction`

**Purpose:** implement Media’s handler for `SH-095 executePrivacyInstruction`.

**Allowed effects:** erase/anonymize fields, detach where Media owns relation, revoke grants, delete R2 object, mark erasure effect, retain when Privacy has recorded an exemption, return typed result.

**Must not:** create PrivacyRequest/DataErasureJob/DataRetentionExemption.

---

## 11. Queries / Decisions

### 11.1 `getMediaReadiness`

**Consumers:** Marketplace Supply, Candidate/Resume, Messaging, Order, Digital Goods, Video, Moderation, admin/debug tools.

**Input:** MediaAsset ID and optional required upload context/action.

**Result:** source-truth readiness projection containing at minimum:

- asset ID;
- technical status;
- upload context;
- detected MIME/size;
- validation status;
- scan status;
- processing status;
- storage visibility/bucket class at safe abstraction level;
- frozen/erased/deleted flags as safe decision facts;
- `ready: boolean` convenience derived from owner truth;
- stable reason codes when not ready.

**Consumer must not infer:** contextual ownership, paid entitlement, moderation approval, credential verification, Agreement validity, resume authority.

### 11.2 `getMediaAssetMetadata`

Returns safe file metadata, not a storage secret or permanent access URL.

Raw object keys and public/private provider details are restricted to internal/provider/admin contexts.

### 11.3 `getMediaUploadStatus`

Returns upload-session progress and safe reason codes for the initiating actor or authorized support context.

It does not expose scanner raw payloads, object keys, or sensitive original metadata unnecessarily.

### 11.4 `getActiveMediaUploadPolicy`

Returns the effective policy for an upload context, with only fields needed by the consumer.

Client-facing constraints are hints for UX; server-side validation remains authoritative.

### 11.5 `canMediaAssetBeAttached`

A Media-owned technical decision used by `SH-090` consumers.

**Input:** asset ID + expected `MediaUploadContext`.

**Result:** ready/not-ready plus stable technical reason.

**Must not infer:** whether the contextual owner should create the join.

### 11.6 Privacy queries

- `enumerateSubjectData` implementation for Media;
- `evaluateRetentionRequirement` for facts Media actually owns, while consuming foreign retention facts where necessary through owner interfaces.

---

## 12. Public Module Interface

### Public commands

- `createMediaUploadSession`
- `completeMediaUpload`
- `requestMediaAccess`
- `revokeMediaAccessGrant`
- `executeMediaModerationInstruction` (`SH-103` handler)
- `executeMediaPrivacyInstruction` (`SH-095` handler)

### Public queries

- `getMediaReadiness`
- `getMediaAssetMetadata`
- `getMediaUploadStatus`
- `getActiveMediaUploadPolicy`
- `canMediaAssetBeAttached`
- `enumerateSubjectData` (`SH-096` implementation)
- `evaluateRetentionRequirement` (`SH-097` implementation where Media owns facts)

### Emitted domain events

- `media.asset.ready`
- `media.asset.rejected`
- `media.asset.failed`
- `media.asset.frozen`
- `media.asset.restored`
- `media.asset.deleted`
- `media.access_grant.issued`
- `media.access_grant.revoked`
- `media.access_grant.expired`

Events use the shared outbox and contain only minimal IDs/state/reason references needed by consumers.

### Privacy executor

Implements SH-095/096/097 protocol for Media-owned records and object-storage resources.

### Provider-facing interfaces owned

- `ObjectStoragePort`
- `MalwareScannerPort`
- `MediaProcessorPort`

No provider-specific type crosses these ports into public Module contracts.

---

## 13. Inbound Dependencies

| Owning Module / platform | Interface consumed | Why required | Minimum information | Can block? | Media must not copy |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | establish trusted actor/system context | actor ID, actor type, session assurance context | yes | auth/session helpers |
| Role / Authority | SH-002 `authorizeResourceAction` | determine general scoped authority | action, resource facts, organization/participant/ownership facts supplied by owners | yes | generic permission engine |
| Context owner | SH-003 owner facts when approved; SH-026 contextual resource access | business-specific access/attachment decision | owner-issued decision, target type/ID, reason/evidence refs, expiry/version if relevant | yes | Order/resume/message/Agreement/digital access policy |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | reusable stop sign | target/action, hold IDs/reasons/scope | yes | local `isBlocked` truth |
| Healthcare / Regulated Services | SH-020 `evaluateHealthcareReadiness` or healthcare access decision contract | PHI/data-boundary enforcement | allowed/redacted/blocked/denied, policy/evidence ref | yes | BAA or healthcare policy |
| Target owner | SH-123 `validateOwnedTargetReference` | validate contextual upload/relationship | target ID, status/version, allowed relationship | yes | direct foreign repository |
| Audit / Event Ledger | SH-029/030 | material admin and sensitive access proof | target/action/outcome/sensitivity/request context | no to domain write after decision, but audit failure may require fail-closed for designated high-risk paths | local generic audit ledger |
| Privacy / Data Erasure | SH-095/096/097 protocol | legal privacy orchestration | instruction, target, disposition, retention reference | yes for destructive action | privacy workflow |
| Content Moderation & Legal Notice | SH-103 | authoritative freeze/revoke/restore instruction | case/action ID, target, action, reason, correlation | yes | moderation/legal decisioning |
| Search / Public Visibility | SH-091 request interface only when needed | refresh a search surface affected by file delivery state | source entity type/ID, action/reason/source version | downstream only | Typesense/SearchUpsertEvent writes |
| Notification | SH-041 only for defined user-facing triggers | safe user-facing alert | template key, safe variables, recipient facts via owner | downstream only | email/SMS/push clients |
| Observability / Ops | SH-032/034/037 and queue/health APIs | correlation, safe logs, provider failure visibility | safe IDs/category/provider/retryability | operationally | custom incident/failure system |

---

## 14. Outbound Consumers and Effects

### Marketplace Supply

Consumes `getMediaReadiness`/`canMediaAssetBeAttached` before creating or publishing contextual Offering media. Marketplace remains responsible for Offering attachment semantics and publish policy.

### Candidate Application & Resume Privacy

Consumes Media upload/readiness and signed object delivery. Candidate Module owns resume access authorization and `ResumeAccessLog`.

### Messaging

Consumes Media upload/readiness and signed object delivery. Messaging owns `MessageMedia`, Thread participation, and Message access semantics.

### Transaction / Order

Consumes Media file storage/access mechanics for Order files and archived Agreement documents. Order owns `OrderFile`, Agreement access grants, signature/hash/version truth, and transaction entitlement.

### Digital Goods Access

Consumes ready MediaAsset and SH-087 signed delivery. Digital Goods owns paid download asset/grant/event and download count/expiry policy.

### Video Session

Consumes a ready private MediaAsset as a raw source for provider ingest. Video owns `CourseVideoAsset` and provider lifecycle.

### Trust Verification / Screening

May consume safe validated/scanned identity/license media while retaining credential-verification decision truth.

### Healthcare

Consumes Media target facts and controls access by returning a healthcare decision; Media enforces it.

### Moderation

Targets Media assets but invokes Media through SH-103; it does not directly update Media tables.

### Privacy

Inventories and orchestrates Media subject data through SH-095–097; it does not directly perform R2 mechanics.

### Search

May receive a refresh request when a Media fact materially changes a public source surface. Search reconstructs projection through source-owner interfaces; Media does not supply private URL/token data.

### Notification

May receive a request for specific product-defined events. Media does not send provider messages directly.

---

## 15. Canonical Shared Operations Used

Only operations relevant to this Module are referenced here. The canonical registry remains the full definition.

### SH-001 — `resolveAuthenticatedActor`

- **Owner:** Identity & Access
- **Classification:** canonical shared capability
- **Why used:** uploader/access requester/admin/system executor identity.
- **Invocation:** entry to every protected public command.
- **Local policy:** Media defines the requested Media action/context only.
- **Expected result:** trusted actor context or unauthenticated result.
- **Do not build:** `mediaAuth.ts`, `getCurrentMediaUser.ts`, feature-local session parser.

### SH-002 — `authorizeResourceAction`

- **Owner:** Role / Authority
- **Classification:** canonical shared capability
- **Why used:** general scoped permission check.
- **Invocation:** before upload, admin policy change, access, manual retry, moderation/privacy execution where actor-driven.
- **Local policy:** Media supplies resource/action facts; it does not centralize contextual business entitlement.
- **Do not build:** `mediaPermissions.ts`, `canAdminDownloadFile.ts`, generic `authorizeMedia.ts` policy engine.

### SH-003 — `queryOwnerFacts`

- **Owner:** each source Module
- **Classification:** shared contract / separate implementations; **status proposed in registry**
- **Why used:** obtain minimum contextual relationship facts without direct Prisma reads.
- **Invocation:** only when SH-026 or SH-123 implementation requires owner facts.
- **Local policy:** Media consumes facts; owner controls meaning.
- **Do not build:** universal cross-domain repository.

### SH-011 — `evaluateComplianceHold`

- **Owner:** Admin Review / Compliance Hold
- **Why used:** hold-sensitive upload/access/freeze paths.
- **Invocation:** before an action that policy marks hold-sensitive.
- **Local policy:** mapping of an applicable hold into Media denial/freeze behavior.
- **Do not build:** `mediaBlockFlag`, `mediaHoldService` owning parallel hold truth.

### SH-020 — `evaluateHealthcareReadiness`

- **Owner:** Healthcare / Regulated Services
- **Why used:** enforce healthcare-lane provider/data-boundary restrictions.
- **Invocation:** before sensitive healthcare upload/access or cross-user exposure when the target is healthcare-bound.
- **Local policy:** Media enforces returned decision against file mechanics.
- **Do not build:** `hipaaMediaPolicy.ts` that decides healthcare eligibility.

### SH-026 — `authorizeContextualResourceAccess`

- **Owner:** relevant context owner
- **Classification:** Shared contract; separate implementations
- **Status:** Confirmed
- **Why used:** establish business-context authorization before generic file access.
- **Invocation:** before `requestMediaAccess` issues a grant/URL.
- **Local policy:** Media readiness/grant/TTL/storage checks.
- **Do not build:** generic service inferring Order, resume, message, Agreement, and Digital Goods policy.

### SH-029 — `appendAuditEvent`

- **Owner:** Audit / Event Ledger
- **Why used:** material administrative changes such as policy activation, manual security override, restoration, or destructive operator action when audit policy requires it.
- **Do not build:** `mediaAuditLog` generic ledger.

### SH-030 — `recordSensitiveAccess`

- **Owner:** Audit / Event Ledger
- **Why used:** append protected read/download/issue/deny/block evidence.
- **Invocation:** sensitive Media access paths in addition to MediaAccessEvent.
- **Local policy:** sensitivity classification and safe Media-specific context.
- **Do not build:** duplicate AccessAuditLog service/table.

### SH-032 — `createRequestContext`

- **Owner:** Observability/platform
- **Why used:** correlation across request, jobs, provider calls, audit, and events.
- **Do not build:** Media-only request ID system.

### SH-034 — `sanitizeTelemetryMetadata`

- **Owner:** Observability/Audit policy
- **Why used:** prevent sensitive file/provider data leakage.
- **Local policy:** Media labels sensitive fields and supplies safe allowlist.
- **Do not build:** ad hoc redaction utility that bypasses platform policy.

### SH-037 — `recordIntegrationFailure`

- **Owner:** Observability / Ops
- **Why used:** R2/scanner/processor/worker degradation.
- **Local policy:** Media still writes its own business-relevant failure status.
- **Do not build:** `mediaIntegrationFailures` as competing generic ops truth.

### SH-041 — `requestNotification`

- **Owner:** Notification
- **Why used:** only for explicitly defined user-relevant Media outcomes.
- **Local policy:** event meaning and safe variables.
- **Do not build:** mail/SMS/push clients inside Media.

### SH-044 — `executeIdempotentCommand`

- **Owner:** platform application infrastructure
- **Why used:** upload completion, promotion, grant issuance, revocation, moderation/privacy executor replay.
- **Local policy:** Media semantic command key and replay result.
- **Do not build:** Media-specific idempotency table/framework.

### SH-046 — `publishDomainEvent`

- **Owner:** platform event/outbox infrastructure
- **Why used:** reliable post-commit Media facts.
- **Local policy:** event names, minimal payload, emission conditions.
- **Do not build:** custom Media event bus/outbox.

### SH-047 — `enqueueReliableJob`

- **Owner:** shared queue infrastructure
- **Why used:** validation, scan, process, promotion, expiry, cleanup, privacy deletion, reconciliation.
- **Local policy:** payload and completion meaning.
- **Do not build:** `mediaQueue.ts` framework.

### SH-048 — `executeRetryWithBackoff`

- **Owner:** shared queue/platform
- **Why used:** transient storage/scanner/processor/provider failures.
- **Local policy:** Media classifies retryable vs terminal vs security rejection.
- **Do not build:** custom retry loops/sleep logic.

### SH-051 / SH-052 — aggregate locking / optimistic concurrency

- **Owner:** shared persistence infrastructure
- **Why used:** guard promotion, freeze/restore/delete, grant issue/use/revoke races.
- **Local policy:** Media lock key/conflict semantics.
- **Do not build:** in-memory mutex.

### SH-053 — `transitionLifecycleState`

- **Owner:** shared mechanism; Media owns policy
- **Why used:** reusable transition plumbing.
- **Local policy:** exact MediaAsset/session/grant graphs.
- **Do not build:** generic policy table owning Media semantics.

### SH-055 — `runDeadlineExpiration`

- **Owner:** shared scheduler/queue
- **Why used:** expire MediaAccessGrant and stale upload sessions when lifecycle supports it.
- **Local policy:** expiry eligibility and resulting event.
- **Do not build:** independent scheduler framework.

### SH-070 — `deleteProviderResource`

- **Owner:** provider-owning Module; Media for R2 objects
- **Why used:** authorized R2 deletion/revocation after Privacy/Moderation/security instruction.
- **Local policy:** object deletion mechanics and Media local result.
- **Do not build:** Privacy-owned R2 client or generic cross-provider deleter in Media.

### SH-072 — `hashCanonicalPayload`

- **Owner:** shared cryptography
- **Why used:** safe hashes of normalized proof/provider metadata when needed.
- **Do not build:** local SHA helper.

### SH-074 — `generateSecureToken`

- **Owner:** shared security
- **Why used:** token material when MediaAccessGrant uses a token-bound flow.
- **Do not build:** `randomToken.ts` in Media.

### SH-075 — `encryptSensitiveValue`

- **Owner:** shared security/cryptography
- **Why used:** only if a Media-owned sensitive field requires application-level encryption under root policy.
- **Do not build:** local encryption/key management.

### SH-080 — `manageVersionedRules`

- **Owner:** shared mechanism; Media owns upload-policy meaning
- **Why used:** R009-approved MFA-PR-02 requirement for immutable/effective MediaUploadPolicy versions; exact schema/migration remains a prerequisite.
- **Do not build:** one-off versioning framework.

### SH-082 — `validateUploadedFile`

- **Owner:** Media / File Access
- **Classification:** canonical Media capability
- **Why used:** central file validation for all upload consumers.
- **Invocation:** validation worker.
- **Local policy:** resolved MediaUploadPolicy.
- **Do not build elsewhere:** resume/offering/message/order MIME validators.

### SH-083 — `scanFileForMalware`

- **Owner:** Media / File Access
- **Why used:** one scanner pipeline and proof.
- **Invocation:** scan worker when policy requires.
- **Local policy:** fail-closed requirements and retry classification.
- **Do not build elsewhere:** feature-local ClamAV/provider wrappers.

### SH-084 — `scrubFileMetadata`

- **Owner:** Media / File Access
- **Why used:** EXIF/GPS/PDF metadata removal and derivative proof.
- **Invocation:** processing worker.
- **Local policy:** processing actions by upload context/policy.
- **Do not build elsewhere:** `stripExif`/`sanitizeImage` duplicates.

### SH-085 — `generatePrivateObjectKey`

- **Owner:** Media/storage primitive
- **Why used:** opaque non-user-controlled object keys.
- **Invocation:** upload-session creation.
- **Local policy:** bucket/path/derivative class.
- **Do not build elsewhere:** filename-to-key helpers.

### SH-086 — `calculateChecksum`

- **Owner:** shared hash primitive consumed by Media
- **Why used:** exact-byte integrity and transformation relationships.
- **Invocation:** upload/derivative processing.
- **Local policy:** meaning of checksum as technical integrity only.
- **Do not build:** local checksum implementation.

### SH-087 — `issueSignedMediaUrl`

- **Owner:** Media / File Access
- **Why used:** canonical private object delivery.
- **Invocation:** after all authority/context/readiness/grant checks.
- **Local policy:** asset readiness, bounded TTL, response headers, access evidence.
- **Do not build elsewhere:** R2/S3 presign code in Digital Goods, Resume, Messaging, Order, Marketplace.

### SH-088 — `manageTemporaryAccessGrant`

- **Owner:** shared grant mechanism; Media owns MediaAccessGrant truth
- **Why used:** common grant mechanics without merging schemas.
- **Local policy:** Media grant eligibility/TTL/use semantics.
- **Do not build:** generic `AccessGrant` table replacing domain grants.

### SH-089 — `revokeTemporaryAccessGrant`

- **Owner:** each grant owner using shared primitive
- **Why used:** revoke MediaAccessGrant after authoritative changes.
- **Local policy:** which Media grants are in scope for the instruction.
- **Do not build:** ad hoc direct status updates from other Modules.

### SH-090 — `attachValidatedMedia`

- **Owner:** contextual domain Module; Media owns asset truth
- **Why used:** consumers attach a ready MediaAsset without taking over file mechanics.
- **Invocation:** contextual owner transaction, after Media readiness query.
- **Local Media policy:** return ready/context-compatible technical decision.
- **Do not build in Media:** universal contextual attachment service.

### SH-091 — `requestSearchProjectionRefresh`

- **Owner:** Search / Public Visibility
- **Why used:** only when a Media-owned delivery fact changes a public source surface.
- **Local policy:** Media supplies reason/source reference; Search/source owner decides projection.
- **Do not build:** Typesense client or SearchUpsertEvent writer.

### SH-095 / SH-096 / SH-097 / SH-098 — Privacy protocol

- **Owner:** Privacy orchestrates; Media executes its target behavior.
- **Why used:** inventory, retention facts, erasure/anonymization/provider deletion.
- **Local policy:** Media field mapping and R2 mechanics.
- **Do not build:** Media PrivacyRequest, erasure job, retention exemption system.

### SH-103 — `executeModerationDecision`

- **Owner:** Moderation owns decision; Media executes.
- **Why used:** freeze, public access revocation, grant revocation, restore.
- **Local policy:** exact file-layer effect.
- **Do not build:** DMCA/moderation adjudication.

### SH-123 — `validateOwnedTargetReference`

- **Owner:** contextual target owner
- **Why used:** validate upload/attachment target without direct foreign repository.
- **Do not build:** cross-domain polymorphic Prisma lookup.

### SH-125 — `recordDomainAccessEvent`

- **Owner:** domain owner; Media for MediaAccessEvent
- **Why used:** append Media-specific access proof separate from AccessAuditLog.
- **Do not build:** one universal access-event table.

---

## 16. Module-Internal Operations

These operations contain Media-specific meaning and should remain local even if they use shared primitives.

| Operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `resolveMediaUploadPolicy` | select effective policy for context/time | context, timestamp | policy version | none | upload-security semantics are Media-owned |
| `classifyMediaStorage` | map context/sensitivity/policy to bucket class/visibility | policy, sensitivity, derivative type | storage classification | MediaAsset/session | file-storage classification is Media policy |
| `quarantineUploadedObject` | ensure untrusted bytes stay non-deliverable | session/object ref | quarantined state | session/asset | safety invariant |
| `evaluateMediaProofCompleteness` | determine whether all required technical proof is present | asset, policy, proof rows | ready/not-ready reasons | none | only Media understands its proof requirements |
| `promoteMediaObject` | move/copy provider object into its ready location and update state | asset/session/policy | promoted object result | asset/session/processing result | Media-owned storage lifecycle |
| `createProcessedDerivative` | create safe derivative linked to source | source asset + action spec | derived MediaAsset | MediaAsset/processing result | technical derivative truth |
| `evaluateMediaAccessReadiness` | check Media-only access facts | asset/grant/action/time | allow/deny reason | none | contextual authorization already external |
| `recordMediaAccessEvent` | append Media access evidence | action/grant/asset/context | event | MediaAccessEvent | Media domain ledger |
| `mapMediaProviderFailure` | normalize object-storage/scanner/processor failure into Media-safe category | adapter result | retryable/terminal + reason | owner state where relevant | retry meaning depends on Media operation |
| `reconcileMediaObjectState` | compare MediaAsset/object-store reality and propose safe repair | local/provider facts | discrepancy/repair result | Media records only when safe | Media owns storage relationship |

---

## 17. Shared Mechanism / Separate Truth Rules

### Temporary access grants

Reuse SH-088 mechanics, but retain:

- `MediaAccessGrant` — generic Media file delivery;
- `AgreementAccessGrant` — contract retrieval;
- `DigitalDownloadGrant` — paid download entitlement;
- `CourseVideoPlaybackGrant` — streaming playback;
- `SensitiveActionSession` — security assurance;
- `LocationReveal` — location disclosure.

Do not merge them.

### Access ledgers

Reuse append-only conventions, but retain:

- `MediaAccessEvent` — Media technical access history;
- `ResumeAccessLog` — resume-specific access proof;
- `DigitalDownloadEvent` — digital download proof;
- video playback events — video proof;
- Agreement events/access proof — contract domain;
- `AccessAuditLog` — generic sensitive-access audit.

### Hashing

Use shared SHA/hash primitives. Keep meanings separate:

- Media checksum = file integrity;
- processing checksum = input/output relation;
- Agreement hash = legal document snapshot proof owned by Transaction / Order;
- provider payload hash = integration evidence.

### Lifecycle plumbing

Use SH-053 mechanics. Media owns the actual transition graph and reason vocabulary.

### Provider-event dedupe

Current Media architecture does **not** define a provider webhook or `ProcessedMediaProviderEvent` ledger. Do not create one by analogy. If the selected malware/storage provider later requires callbacks, define a provider-owner dedupe record only after the contract is real.

### Search projection

Media can request refresh but does not own the projection or source entity’s public-readiness policy.

### Workflow runners

Media pipeline jobs may be chained through shared queue/event mechanisms, but no `DeliveryWorkflow` or Cluster-generic saga is introduced. The MediaAsset/session/proof records remain the authoritative local lifecycle.

---

## 18. Authentication and Authorization

### Authenticated actor

All user-triggered upload/access/admin commands begin with SH-001.

System/worker commands use a trusted system actor/service context supplied by the platform rather than bypassing identity/audit context.

### General authority

SH-002 decides general action authority. Media supplies facts such as:

- uploader relation;
- MediaAsset ID;
- target reference supplied by owner;
- action (`upload`, `view`, `download`, `manage_policy`, `manual_retry`, etc.);
- sensitivity where safe/required.

### Contextual authorization

Media does not interpret contextual business relationships. It consumes SH-026 decisions from owners such as:

- Messaging for message attachment access;
- Candidate Application for resume access;
- Transaction / Order for Agreement/Order access;
- Digital Goods for paid download access;
- Marketplace Supply for Offering attachment management.

### Organization / participant context

Organization membership and Thread participation are owner facts interpreted by Role / Authority, not Media joins.

### Admin/support

Admin/support status does not automatically permit sensitive file content access. Admin actions still consume:

- SH-002 authority;
- healthcare policy for healthcare-bound files;
- SH-030 sensitive access auditing;
- step-up if root security policy later designates the action.

### Step-up

No blanket Media-local step-up rule is invented here. Use SH-014 only when the root security matrix explicitly marks a Media action (for example, a highly sensitive admin evidence download or destructive manual privacy retry) as requiring fresh assurance.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying truth owner | Interface consumed | Media action gated | Local composition |
| --- | --- | --- | --- | --- |
| authentication | Identity & Access | SH-001 | all protected commands | require trusted actor/system context |
| general authority | Role / Authority | SH-002 | upload/access/admin command | Media supplies resource facts only |
| contextual business access | contextual owner | SH-026 | private signed delivery | must be allowed before Media grant/URL |
| target eligibility | target owner | SH-123 | contextual upload/attachment | target must exist and permit relationship |
| ComplianceHold | Admin Review / Compliance Hold | SH-011 | configured upload/access/freeze-sensitive actions | active applicable hold maps to safe denial/freeze behavior |
| healthcare lane | Healthcare / Regulated Services | SH-020 / healthcare access decision | healthcare file upload/access/admin view | Media enforces permit/redact/block/deny outcome |
| media readiness | Media | `getMediaReadiness` | contextual attachment and access | validation/scan/processing and asset lifecycle must satisfy Media policy |
| generic grant | Media + SH-088 | MediaAccessGrant | signed URL issuance | active, unexpired, not revoked; one-time semantics only if approved |
| moderation | Content Moderation | SH-103 | public exposure/grants/asset freeze | execute authoritative instruction only |
| privacy/retention | Privacy + source owners | SH-095–097 | erase/delete/anonymize/provider deletion | do not delete retained evidence; return typed result |

Order entitlement, DigitalDownload entitlement, Agreement access, resume access, message access, and course playback entitlement are not composed inside Media.

---

## 20. Provider Integrations

### 20.1 Object storage

**Provider-neutral port:** `ObjectStoragePort`.

Required operations should cover only Media-owned needs, for example:

- create presigned/private upload instruction;
- inspect/head object;
- stream/read bounded bytes for validation;
- put/copy/move object for promotion/derivative;
- delete object;
- create short-lived signed read URL;
- check existence/state for reconciliation.

**Current adapter:** Cloudflare R2 through S3-compatible API.

**Credentials:** server-only secret management. No credentials in domain records, client bundles, logs, or events.

**Webhook:** none required by current evidence. Do not invent webhook processing for R2.

**Status/error translation:** adapter returns Media-neutral result categories; raw SDK errors terminate at adapter.

**Reconciliation:** compare MediaAsset/session state with provider object existence/metadata. Auto-repair only explicitly safe discrepancies; otherwise emit operational discrepancy for review.

**Retry/idempotency:** stable object key + command idempotency. A retry must not create multiple semantic assets.

**Privacy deletion:** implement SH-070 under authorized SH-095/103 instructions.

**Operational failure:** SH-037.

### 20.2 Malware scanner

**Provider-neutral port:** `MalwareScannerPort`.

Required normalized output:

- clean;
- suspicious;
- infected;
- retryable failure;
- terminal failure;
- provider/version/reference/hash evidence.

**Production provider:** unresolved. Test/fake adapter is allowed before provider selection.

**Critical rule:** a policy requiring malware scanning cannot promote to ready while the production scanner is unavailable or not configured.

### 20.3 Media processing

**Port:** `MediaProcessorPort` or narrower processing ports following root conventions.

Current evidence supports:

- `file-type` for binary file detection;
- `sharp` for image processing/EXIF-GPS scrubbing;
- PDF metadata processing when implementation is selected.

Provider/local processor results are normalized into `MediaProcessingResult`.

### 20.4 Providers explicitly prohibited here

Do not add:

- Stripe;
- Cronofy/Nylas;
- Daily/Agora/AWS Chime;
- Mux;
- Typesense;
- email/SMS/push providers;
- verification/background-check providers.

Those belong to their owner Modules.

---

## 21. Events and Outbox

### Domain event rules

Events represent committed Media facts. They are not commands disguised as events.

Example:

```text
media.asset.ready
```

means the MediaAsset passed Media technical readiness. It does **not** mean:

- publish the Offering;
- grant a purchase;
- approve a resume;
- send a notification;
- index a search record.

Consumers decide their own reaction through their owner policy.

### Event envelope expectations

Use SH-046 envelope fields from platform infrastructure, including:

- event ID;
- event type;
- event schema version;
- aggregate type/ID;
- occurredAt;
- correlation ID;
- causation ID when applicable;
- actor/system reference where safe;
- minimal payload.

### Payload minimization

Never put in events:

- raw file bytes;
- raw storage key unless a tightly controlled internal consumer genuinely requires it;
- signed URL/token;
- provider credentials;
- original sensitive filenames by default;
- PHI/resume/contract contents;
- scanner raw payload.

### Transactional outbox

Use SH-046 when a Media database transition and an asynchronous external reaction must be reliable. Write owner truth and outbox record in the same transaction.

### Consumer idempotency

Consumers must deduplicate event effects through SH-045/platform inbox mechanics. Media must not assume exactly-once transport.

---

## 22. Background Jobs / Scheduled Work

### 22.1 Validate upload worker

- **Purpose:** server-side byte/type/size/context validation.
- **Input:** upload session/asset ID.
- **Owner:** Media.
- **Idempotency key:** semantic session + validation attempt/version.
- **Retryable:** temporary storage read failure.
- **Permanent:** MIME/signature/size/policy rejection.
- **Dead-letter:** keep asset non-ready; record IntegrationFailure; manual/replay path if safe.
- **Truth updated:** validation proof + summary status.

### 22.2 Malware scan worker

- **Purpose:** run SH-083.
- **Idempotency key:** asset checksum + scanner policy/version where practical.
- **Retryable:** scanner timeout/unavailability classified transient.
- **Permanent:** infected result; unsupported content if policy defines it terminal.
- **Dead-letter:** remain non-ready; no fail-open.

### 22.3 Processing worker

- **Purpose:** metadata scrub/derivative work.
- **Idempotency key:** source checksum + processing action + processor/policy version.
- **Retryable:** transient object/processor failure.
- **Permanent:** deterministic processing failure under current bytes/policy.
- **Truth updated:** processing proof/derived MediaAsset.

### 22.4 Promotion worker

- **Purpose:** promote only fully proven asset into ready location/state.
- **Idempotency key:** mediaAssetId + policy/proof version.
- **Retryable:** transient object move/copy failure.
- **Permanent:** proof incompleteness is not retried blindly; wait for missing prerequisite or reject/fail.

### 22.5 Media access-grant expiration worker

- **Purpose:** materialize expired status/events for grants past `expiresAt`.
- **Input:** cursor batch by expiry.
- **Owner:** Media.
- **Rule:** request-time expiry check is authoritative even before worker runs.
- **Shared:** SH-055.

### 22.6 Quarantine cleanup worker

- **Purpose:** remove abandoned/rejected/infected/stale provider objects according to approved security/retention rules.
- **Critical constraint:** must not delete retention-locked evidence or execute Privacy erasure outside Privacy instruction where privacy semantics matter.

### 22.7 Object-storage reconciliation worker

- **Purpose:** detect orphaned/missing/misplaced objects and stale local/provider state.
- **Repair:** automatic only when deterministic and safe; otherwise operational discrepancy/manual review.

### Queue rules

All workers use SH-047/048/038 infrastructure. No Media-specific generic queue ledger.

---

## 23. Concurrency and Idempotency

### Races to prevent

1. duplicate upload-session creation from client retry;
2. duplicate upload completion creating multiple assets;
3. simultaneous validation/scan/process attempts writing contradictory summary state;
4. promotion while a new failure/freeze instruction arrives;
5. derivative creation duplicated by retry;
6. grant issue duplicated by retry;
7. URL issuance concurrent with revocation/expiry;
8. asset delete/erase concurrent with access issuance;
9. moderation freeze concurrent with restore/delete;
10. privacy provider deletion invoked twice.

### Lock/resource keys

Use owner-defined keys such as:

- `media-upload-session:{sessionId}`;
- `media-asset:{mediaAssetId}`;
- `media-access-grant:{grantId}`;
- stable privacy/moderation command target + action ID.

These are semantic keys for SH-044/051 infrastructure, not new in-memory lock registries.

### Transaction boundaries

Use a transaction for:

- terminal proof + summary state where they must remain consistent;
- promotion readiness decision + asset state + outbox event;
- grant state validation + access event issuance where atomicity is required;
- revocation state + revocation access event;
- owner-side privacy/moderation state transitions.

Provider side effects cannot participate in the DB transaction. Use idempotency + durable jobs/outbox and reconcile afterward.

### Replay result

Idempotent commands return the original semantic result when the same key/fingerprint is replayed. A mismatched fingerprint under the same key is a conflict.

---

## 24. Media / Storage

This section is central because Media / File Access is the storage owner.

### Business attachment meaning

Media does **not** own the business attachment meaning. See MFA-PR-01 and SH-090.

### Upload context

`MediaUploadContext` is Media-owned technical vocabulary because it selects file-safety/storage rules. It must not become a replacement for contextual business schema.

Current contexts include:

- user avatar;
- professional portfolio image;
- professional government ID;
- professional license document;
- organization logo/job graphic;
- candidate resume/CV/application attachment;
- Offering/Gig/Message/Order media;
- Agreement PDF;
- digital download file;
- course accessibility asset;
- healthcare file;
- admin evidence;
- other.

### Validation

Server-side validation includes size, declared/detected MIME, extension, binary signature, archive/encryption/password protection policy, and upload context.

### Scan

Policy-required malware scanning must complete as clean before promotion.

### Signed access

Short-lived signed URLs are created server-side only through SH-087. The URL itself is an ephemeral credential and must not become durable application truth.

### Public/private status

- default private;
- sensitive/healthcare/legal bucket classes as appropriate;
- public derivatives only where active policy permits;
- raw original public exposure is exceptional and unresolved for broad use.

### Proposed Ruling MFA-PR-05 — raw public originals

For MVP, `allowOriginalPublic` / `public_original` should remain disabled unless a context-specific policy is explicitly approved. Default public display path is private original → processed/scrubbed derivative → `public_processed`.

### Sensitive access logging

MediaAccessEvent always captures Media-specific proof for defined actions. SH-030 is additionally required for access classified sensitive by platform policy.

---

## 25. Search / Projection

Media owns no Typesense/search source-of-truth projection.

A Media change can affect a source entity’s public readiness, for example:

- a required public derivative becomes ready;
- a derivative is frozen or public URL is revoked;
- moderation removes public delivery;
- privacy removes underlying media.

When a refresh is necessary:

```text
Media committed fact
→ SH-091 requestSearchProjectionRefresh
→ Search validates request
→ Search obtains authoritative source projection/readiness from contextual owners
→ Search updates/removes projection
```

Media must not expose private object URLs, raw object keys, grant tokens, PHI, resumes, contracts, or paid delivery URLs to Search.

---

## 26. Notification

Media owns no notification delivery system.

A Media-owned trigger may request Notification only when product behavior explicitly calls for it, for example:

- a user-relevant upload rejection requiring remediation;
- an upload processing failure that the user must act on;
- a security/admin action where policy requires user notice.

Notification request payloads must use safe references and template variables. Do not include raw signed URLs, sensitive filenames, PHI, resume contents, identity-document details, contract text, or scanner payloads.

No email/SMS/push provider client belongs inside this Module.

---

## 27. Audit and Sensitive Access

### Media domain evidence

`MediaAccessEvent` proves Media-specific access/delivery facts.

### Generic AuditEvent

Use SH-029 for important administrative/system actions that require generic audit proof, such as:

- upload-policy activation/retirement;
- manual sensitive retry/override when approved;
- moderation restore execution;
- destructive manual privacy retry.

### AccessAuditLog

Use SH-030 for sensitive access attempts/issuances/downloads/blocks as required by sensitivity policy.

### Separation rule

```text
MediaAccessEvent = Media domain access truth
AccessAuditLog   = generic append-only sensitive access proof
AuditEvent       = generic important action proof
IntegrationFailure = operational failure proof
```

Never collapse these records into one generic log.

---

## 28. Privacy and Retention

### Subject-data inventory

Media may hold:

- uploadedByUserId;
- original/sanitized filenames;
- request IP hash/user agent;
- object keys;
- file metadata and checksums;
- upload-session target references;
- validation/scan/processing proof;
- access-grant user/target/reason metadata;
- MediaAccessEvent request metadata;
- R2 provider objects;
- derivatives.

### Privacy executor

Implement:

- SH-096 `enumerateSubjectData`;
- SH-097 `evaluateRetentionRequirement` for Media-owned facts and referenced owner facts through public interfaces;
- SH-095 `executePrivacyInstruction`;
- SH-098 anonymization mapping where approved;
- SH-070 R2 deletion.

### Erase / anonymize / revoke / retain

- revoke access before destructive deletion where necessary;
- delete R2 object when erasure is permitted;
- remove/anonymize original filenames and request metadata when permitted;
- preserve relational/security/legal evidence only when the Privacy workflow has an approved exemption;
- return `retained` instead of silently deleting when retention applies;
- provider “already absent” is idempotent success where the protocol permits;
- `erasedAt` is distinct from normal product deletion.

### Retention concerns

Particular review is required for:

- Agreement/legal archive MediaAsset;
- identity/license evidence;
- healthcare media;
- security scan evidence;
- access/security evidence.

Media does not determine legal/tax/contract retention law. It supplies facts and executes Privacy’s recorded disposition.

---

## 29. Observability

### Structured logs

Every significant request/worker/provider operation includes:

- request/correlation ID;
- Module operation;
- safe MediaAsset/session/grant ID;
- upload context where safe;
- provider adapter name;
- duration;
- attempt count;
- normalized error category;
- retryability.

### Prohibited telemetry

Do not log:

- raw signed URLs/tokens;
- storage credentials;
- file bytes;
- scanner raw payload;
- original sensitive filenames by default;
- PHI/resume/identity-document/contract contents;
- full user agent/IP if platform policy only permits hash/minimized form.

### IntegrationFailure / SystemEvent

Use SH-037 and Ops-owned records for provider/worker degradation. Business-relevant consequences must also update Media truth.

### Metrics

Useful low-cardinality metrics include:

- upload sessions started/completed/rejected/failed by context class;
- validation failure reason counts;
- malware scan clean/infected/failure counts;
- processing duration/failure counts by action;
- time-to-ready;
- access grants issued/denied/expired/revoked;
- signed URL provider failure rate;
- quarantine backlog age;
- reconciliation discrepancies.

Do not use user IDs/object keys as metric dimensions.

### Health checks

Production health should expose bounded checks for:

- R2 connectivity/permissions;
- scanner health when required for active policies;
- queue backlog/age;
- processor readiness.

Health state is operational, not MediaAsset truth.

---

## 30. Security Boundaries

1. All public inputs use runtime schema validation.
2. All protected actions are server-authorized.
3. Client MIME/extension/filename is untrusted.
4. Binary inspection occurs server-side when policy requires.
5. File-size enforcement occurs server-side/provider-side, not only in UI.
6. Upload bytes stay outside executable/public application directories.
7. Opaque object keys are generated server-side.
8. Sensitive/private files use private/specialized bucket classes.
9. Signed URLs are short-lived and generated server-side only.
10. Default sensitive Media signed URL policy target is 15 minutes unless an approved context-specific policy is shorter/different.
11. Long-lived digital-download TTL belongs to Digital Goods policy/grant, not generic Media defaults.
12. Raw signed URL/token values are never durable business truth.
13. Checksums use the canonical shared crypto primitive.
14. Provider credentials/signing keys remain server-only and managed through platform secret infrastructure.
15. Malware/scanner failure cannot be treated as success.
16. Public originals are exceptional; scrubbed processed derivatives are default.
17. Freeze/revocation checks run at access time.
18. Rate limiting/abuse controls must protect upload initiation, completion, access issuance, and administrative retry endpoints using root platform controls.
19. Telemetry uses safe/redacted metadata.
20. R2 CORS/bucket policy must not permit anonymous access to private/quarantine/sensitive/healthcare/legal buckets.

---

## 31. Error / Decision Result Pattern

Public interfaces return stable application categories rather than leaking Prisma/AWS/scanner exceptions.

### Result shape

A command/query decision should support:

```text
status: ok | denied | conflict | retryable_failure | terminal_failure
code: stable Media reason code
message: safe user/operator message
resourceId?: Media ID
retryAfter?: optional safe hint
evidenceRefs?: safe IDs only
correlationId: request correlation
```

### Stable reason families

Authentication/authority:

- `unauthenticated`
- `forbidden`
- `context_denied`
- `target_not_found`
- `target_not_eligible`
- `hold_blocked`
- `healthcare_blocked`

Upload/policy:

- `upload_policy_not_found`
- `upload_policy_inactive`
- `file_too_large`
- `mime_type_not_allowed`
- `extension_not_allowed`
- `binary_signature_mismatch`
- `archive_not_allowed`
- `encrypted_file_not_allowed`
- `password_protected_file_not_allowed`
- `malware_detected`
- `scan_required_unavailable`
- `metadata_scrub_failed`
- `image_processing_failed`
- `provider_unavailable`

Asset/access:

- `media_not_ready`
- `media_frozen`
- `media_deleted`
- `media_erased`
- `grant_expired`
- `grant_revoked`
- `grant_denied`
- `signed_url_unavailable`
- `stale_transition`
- `idempotency_conflict`

Privacy/moderation:

- `instruction_not_authorized`
- `retained_by_privacy_policy`
- `provider_delete_retryable`
- `provider_delete_terminal`

Consumers must not inspect provider exception strings to decide business behavior.

---

## 32. Testing Architecture

### Domain unit tests

Required for:

- policy resolution;
- MediaAsset transition graph;
- proof-completeness/promotion rules;
- validation rejection mapping;
- scanner result mapping;
- processing requirements;
- access readiness/TTL/freeze rules;
- retry classification.

### State-transition tests

Prove invalid transitions are rejected, including:

- uploaded → ready without required proof;
- infected → ready;
- frozen → ready without restore instruction;
- deleted/erased → signed access;
- expired/revoked grant → URL issuance.

### Public contract tests

For:

- create/complete upload;
- get readiness/metadata/status/policy;
- request access;
- moderation executor;
- privacy executor.

Foreign owner interfaces must be faked by contract rather than foreign Prisma writes.

### Database/integration tests

Prove:

- storageKey uniqueness;
- idempotent completion;
- transactional promotion/event write;
- access issue/revoke/expiry race behavior;
- cascade/retention-safe deletion behavior;
- indexes support expiry/asset/access queries.

### Authorization tests

Cover:

- anonymous denial;
- uploader owner vs unrelated actor;
- contextual owner allow/deny;
- organization/participant cases through Role/Authority contract;
- admin/support does not bypass healthcare/sensitive rules automatically.

### Compliance/security tests

Fixtures for:

- MIME spoofing;
- extension mismatch;
- oversized file;
- path/filename injection;
- archive/encrypted/password-protected rules;
- infected and suspicious scanner results;
- EXIF/GPS removal;
- private bucket anonymous denial;
- signed URL expiry;
- sensitive telemetry leak scan.

### Idempotency/concurrency tests

Parallel/replay tests for:

- upload completion;
- promotion;
- derivative processing;
- access grant issue;
- grant use/revoke/expiry;
- privacy deletion;
- moderation freeze/restore.

### Provider adapter tests

- R2 request/result translation;
- absent object behavior;
- presign TTL/headers;
- scanner normalized results;
- processor exact result mapping;
- transient vs terminal errors;
- reconciliation discrepancies.

### Privacy tests

- enumerate subject data;
- erase object + local metadata where permitted;
- retain when Privacy exemption applies;
- anonymize approved fields;
- duplicate erasure idempotency;
- provider absent is safe replay;
- no parallel PrivacyRequest creation.

### E2E participation tests

At minimum:

1. upload → quarantine → proof → ready;
2. invalid/infected upload → never ready;
3. contextual allow → short-lived signed access;
4. contextual deny → no access;
5. moderation freeze → subsequent access denied;
6. privacy deletion/revocation → subsequent access denied;
7. Digital Goods/Resume/Message test harness consumes Media contract without direct R2 access.

---

## 33. Module Invariants

### Rules coding agents must never violate

1. `MediaAsset` is the canonical Workin Ants file record.
2. Contextual joins do not transfer business lifecycle ownership to Media.
3. No contextual Module may mark `MediaAsset` ready directly.
4. Upload completion alone never means file readiness.
5. Client-reported MIME, extension, and filename are untrusted.
6. Required binary validation must occur against server-read bytes.
7. Required malware scanning must be clean before ready.
8. Scanner failure must never be treated as clean.
9. Infected files must never become ready.
10. Required metadata scrub/processing must succeed before relevant public/cross-user exposure.
11. Original filenames must never become object keys.
12. Private/sensitive/healthcare/legal files must not rely on permanent public URLs.
13. Public images default to processed/scrubbed derivatives.
14. R2/provider object state is infrastructure, not lifecycle truth.
15. A `MediaAsset` reference alone never proves business entitlement.
16. A signed URL never proves business entitlement.
17. `MediaAccessGrant` must remain separate from Agreement, DigitalDownload, CourseVideo, Resume, and Location access truth.
18. Contextual authorization must precede private signed access.
19. Media must not infer Order payment status from Stripe/provider state.
20. Media must not infer resume authorization from OrganizationMember tables directly.
21. Media must not infer message access from ThreadParticipant tables directly.
22. Media must not infer Agreement entitlement or contract validity.
23. Media must not own Mux/live-video provider state.
24. Media must not make moderation/legal adjudications.
25. Public URL revocation/freeze is not evidence deletion.
26. Media must not own PrivacyRequest/DataErasureJob/DataRetentionExemption lifecycles.
27. Product deletion and privacy erasure are distinct.
28. Retention-locked legal/financial evidence must not be deleted by normal cleanup.
29. `MediaAccessEvent` does not replace `AccessAuditLog`.
30. Operational logs/IntegrationFailure do not replace Media status/proof.
31. Provider payloads must terminate at adapters.
32. Provider secrets, raw signed URLs, tokens, file contents, PHI, resume text, identity-document content, and contract text must not enter telemetry.
33. Slow/provider-dependent work must use the shared durable queue.
34. Retryable commands must be idempotent.
35. Distributed concurrency must use database/platform primitives, not in-memory locks.
36. Search projection is external; Media never writes Typesense directly.
37. Notification delivery is external; Media never sends email/SMS/push directly.
38. No generic `AttachmentService`, `FilePermissionService`, or `DeliveryService` may absorb foreign domain policy.
39. If a required architecture question is unresolved, implementation must stop at the approved boundary rather than inventing truth.

---

## 34. Prohibited Duplicate Implementations

Do not generate these inside or adjacent to Media when the canonical operation already exists:

### Authentication / authorization

- `mediaAuth.ts`
- `getCurrentMediaUser.ts`
- `mediaPermissions.ts`
- `authorizeAnyFile.ts`
- `adminCanViewAllFiles.ts`

### Shared reliability

- `mediaIdempotency.ts`
- `mediaQueue.ts`
- `mediaRetry.ts`
- `mediaMutex.ts`
- custom event bus/outbox
- custom request-context generator

### Audit / observability

- `mediaAuditLogService.ts` as generic audit owner
- `mediaIntegrationFailure.ts`
- local Sentry client
- local telemetry redactor

### File mechanics outside canonical Media implementation

Consumers must not independently create:

- `resumeMimeValidator.ts`
- `messageAttachmentValidator.ts`
- `offeringUploadValidator.ts`
- `virusScan.ts` / `clamav.ts` per feature
- `stripExif.ts` per feature
- `r2Client.ts` per consumer
- `s3SignedUrl.ts` per consumer
- `downloadUrlService.ts` per consumer
- `safeFilename.ts` per consumer
- local checksum/SHA helper

### Foreign domain policy inside Media

- `resumeAuthorizationService.ts`
- `messageAttachmentPermissionService.ts`
- `orderFileEntitlement.ts`
- `agreementAccessPolicy.ts`
- `digitalDownloadEntitlement.ts`
- `coursePlaybackPolicy.ts`
- `dmcaDecisionService.ts`
- `privacyRequestService.ts`
- `healthcareEligibilityService.ts`
- `typesenseMediaIndexer.ts`
- email/SMS/push provider clients

---

## 35. Unresolved Decisions

### MFA-UR-01 — `MediaAccessGrant.used` semantics

See Data Model. Determine one-time vs reusable-until-expiry semantics before using `used` as a universal terminal state.

### MFA-UR-02 — production malware scanner

The architecture requires a scanner adapter and fail-closed behavior. Production provider remains unresolved. This blocks production readiness for any active policy requiring malware scanning, but does not block fake adapter/domain implementation.

### MFA-UR-03 — exact schema/code stewardship for contextual joins

Semantic ownership is ruled: contextual Module owns business meaning. Physical repository/folder/schema stewardship remains unresolved for joins historically listed under Media. No migration should be introduced merely to tidy architecture.

### MFA-UR-04 — `DataSensitivity` ownership

Media consumes the enum but the cross-platform owner should be explicit in root architecture. Do not create a Media-specific sensitivity enum in the meantime.

### MFA-UR-05 — application-level encryption requirements

Private R2/storage is required. Whether specific Media fields/object classes require additional application/KMS encryption metadata beyond provider-side encryption must follow root security/provider ADRs.

### MFA-UR-06 — public original media

MFA-PR-05 establishes a safe MVP default, but any allowed `public_original` contexts require explicit approval.

### MFA-UR-07 — policy version schema shape

MFA-PR-02 requires immutable/effective policy versions. Exact shared versioning columns follow root/shared conventions when available.

### MFA-UR-08 — upload-session enum migration timing

R010 requires the lifecycle separation in MFA-PR-03; its exact status representation/migration timing remains for the later schema pass and must align with Cluster/database sequencing.

### MFA-UR-09 — access-proof retention

Finalize which `MediaAccessEvent`, scan, validation, and processing records must be retained/anonymized after MediaAsset erasure before destructive cascade behavior is enabled.

### MFA-UR-10 — provider webhook requirement for scanner

Do not create a Media provider-event dedupe model unless the selected scanner/provider actually requires asynchronous callbacks.

---

## 36. Architecture Decision Summary

The following rulings are binding for Module implementation unless a higher-level architecture file explicitly changes them:

1. `MediaAsset` is file/storage truth.
2. Media owns technical upload policy, upload attempt, validation, scan, processing, generic Media grant, and Media access-event truth.
3. Contextual Modules own the business meaning and authorization of contextual media relationships.
4. `SH-090 attachValidatedMedia` belongs to the contextual owner; Media supplies technical readiness.
5. Media owns object-storage, scanner, and file-processing provider ports.
6. Cloudflare R2 is the current object-storage rail.
7. Production malware scanner provider remains unresolved; required scan paths fail closed.
8. Private signed access requires actor authority + contextual authorization + applicable hold/healthcare gates + Media readiness + valid bounded grant context.
9. Generic Media signed URL default for sensitive files is 15 minutes unless an approved Media/context policy specifies otherwise.
10. Media never becomes paid download, Agreement, resume, message, or course playback entitlement truth.
11. MediaAccessEvent and AccessAuditLog remain separate.
12. Moderation owns decision; Media executes file-level enforcement through SH-103.
13. Privacy owns orchestration/retention exemptions; Media executes owner-specific instructions through SH-095–098 and R2 deletion through SH-070.
14. Search and Notification remain external capabilities.
15. Provider payloads do not escape adapters.
16. Shared queue/idempotency/concurrency/crypto/audit/observability mechanisms are consumed, not rebuilt.
17. Upload policies must move toward immutable versioned rule semantics before production administration.
18. Upload-session lifecycle must be isolated behind a dedicated domain contract and should receive a dedicated enum migration.
19. Public raw originals are disabled by default for MVP; processed public derivatives are preferred.
20. Destructive cascade behavior requires retention/security review before production privacy/delete paths are enabled.

---

## 37. Coding-Agent Usage

Before implementing any Media / File Access feature, an agent must read, in this order:

1. root `project-overview.md`;
2. root `architecture.md` if present;
3. root `code-standards.md`;
4. `context/shared/shared-operations.md`;
5. CL-05 `architecture.md`;
6. CL-05 `build-plan.md`;
7. this `media_file_access/module-architecture.md`;
8. this `media_file_access/implementation-plan.md`;
9. relevant public-interface sections for direct dependency owners, especially Role / Authority, Healthcare, Moderation, Privacy, Audit, Transaction / Order, Candidate Application & Resume Privacy, Messaging, Digital Goods Access, and Video Session;
10. current progress tracker/migrations/provider ADRs.

Before changing ownership or adding a new table/service, the agent must answer:

```text
Which source record owns this truth?
Is there already a canonical SH-### mechanism?
Does this change transfer business meaning from a contextual owner into Media?
Does it change a binding lifecycle/provider/security/privacy decision?
```

If the answer implies a new architecture decision, update architecture first or record the unresolved decision. Do not let implementation silently become architecture.

## WA-R007 — Contextual attachment ownership registry alignment

The registry now lists OfferingMedia, GigMedia, OrganizationMedia and CandidateProfileMedia as referenced by Media rather than owned by Media. Their existing source owners remain Marketplace Supply, Gig Demand, Organization Hiring and Candidate Application respectively. No schema placement/migration changed. This applies the existing contextual-join lifecycle split; it does not create a generic attachment owner or change MediaAsset technical ownership. Shared ProfileStatus vocabulary is an enum-stewardship concern, not a shared profile lifecycle.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


## WA-R020 — Privacy executor identity and truthful completion

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R020 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r020--privacy-executor-identity-and-truthful-completion) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

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
