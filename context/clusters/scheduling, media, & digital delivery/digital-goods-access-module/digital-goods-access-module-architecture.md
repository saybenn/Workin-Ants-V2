# Digital Goods Access Architecture

> **Module ID:** `digital_goods_access`  
> **Module name:** Digital Goods Access Module  
> **Module type:** `domain_capability_compliance_hybrid`  
> **Build status:** `mvp_active_legal_gated`  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Repository target:** `context/clusters/scheduling-media-digital-delivery/modules/digital-goods-access/module-architecture.md`  
> **Document status:** implementation-grade Module architecture for the current Workin Ants MVP evidence  
> **Audience:** coding agents, developers, reviewers, maintainers, architecture reviewers  
> **Update rule:** update this file when a binding Digital Goods ownership, lifecycle, public-interface, legal-policy, retention, security, or cross-Module decision changes. Build progress must not silently redefine this architecture.

This document is subordinate to the root Workin Ants architecture and to the CL-05 Cluster architecture. It narrows those decisions to `digital_goods_access`. It does not duplicate the entire platform architecture and does not transfer source-of-truth ownership from adjacent Modules.

The current CL-05 architecture resolves the historical ownership collision for the core digital-goods records in favor of Digital Goods Access. The older Deep Module collision watchlist remains useful historical evidence, but the Cluster architecture now treats `DigitalGoodsPolicy`, `DigitalDownloadAsset`, `ChildDirectedContentDeclaration`, `MinorPrivacyControl`, and `CourseAccessibilityAsset` as Digital Goods Access truth. The generic `ConsentType` vocabulary and `ConsentLog` lifecycle remain Consent & Disclosure truth.

Structural quality references such as the BTLS architecture/build plan influence rigor and organization only. No BTLS product, provider, tenancy, or domain decision is inherited here.

---

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `digital_goods_access` |
| Module name | Digital Goods Access Module |
| Module type | `domain_capability_compliance_hybrid` |
| Build status | `mvp_active_legal_gated` |
| Primary Cluster | CL-05 — Scheduling, Media & Digital Delivery |
| Root relationship | Inherits global actor, source-of-truth, privacy, audit, observability, search, entitlement, and provider-boundary rules. Root architecture wins if a later explicit conflict is introduced. |
| Cluster relationship | Owns one of the four CL-05 delivery lifecycles. CL-05 coordinates sequence and contracts but owns none of this Module’s records. |
| Production posture | Core schema, contracts, test policy, grant mechanics, and integration plumbing may be built before legal approval. Production activation of legally gated license/refund/child-directed/waiver behavior must fail closed until approved policy versions exist. |

### Evidence basis

This Module architecture is grounded in the current:

- Module Architecture Extract from this thread;
- refreshed Deep Module Registry;
- Cluster Registry v2.3;
- current Prisma schema;
- Ubiquitous Language / Compliance Inventory;
- Canonical Shared Operations Registry (`SH-001`–`SH-126`);
- CL-05 `architecture.md`;
- CL-05 `build-plan.md`;
- Workin Ants `project-overview.md`.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Control the Workin Ants truth and policy required to deliver paid downloadable digital goods, preserve buyer-specific digital-goods terms evidence, revoke or expire access safely, record download-domain evidence, represent child-directed product controls, and track course accessibility assets.

### Goal

Turn an authoritative Offering context plus an authoritative purchase/access basis and a safe `MediaAsset` into **bounded, revocable, auditable digital delivery** without turning storage URLs, provider objects, `Order`, `ConsentLog`, `MediaAsset`, or course-video provider state into Digital Goods truth.

### What enters

Typical inputs are:

- authenticated User/system actor from Identity & Access;
- seller/admin/buyer action authorization from Role / Authority;
- `CustomerProfile` buyer context where commercial actor identity is required;
- `Offering`, `ProductDetails`, `CourseDetails`, and ownership/eligibility facts from Marketplace Supply;
- authoritative `Order` entitlement and refund/dispute effects from Transaction / Order;
- versioned consent proof from Consent & Disclosure;
- safe/ready `MediaAsset` references and signed-object delivery from Media / File Access;
- `CourseVideoAsset` references from Video Session where accessibility assets attach to streamed course content;
- `ComplianceHold` decisions;
- moderation/legal decisions such as disable, restore, or revoke access;
- Privacy-owned erasure/retention instructions;
- Search refresh and Notification interfaces for downstream effects.

### What leaves

The Module produces:

- current `DigitalGoodsPolicy` configuration;
- immutable contextual `DigitalGoodsTermsAcceptance` evidence;
- `DigitalDownloadAsset` delivery records referencing safe Media assets;
- expiring `DigitalDownloadGrant` records;
- append-only `DigitalDownloadEvent` delivery evidence;
- child-directed declarations and product-surface `MinorPrivacyControl` records;
- `CourseAccessibilityAsset` records and readiness decisions;
- stable public query/decision results;
- domain events/outbox records for downstream consumers where needed;
- owner-local execution acknowledgments for moderation and Privacy workflows.

### Business/capability transformation

```text
Offering / Course / Product context
+ actor and authority
+ approved policy/version context
+ safe MediaAsset
+ authoritative Order entitlement (normal purchased path)
+ required contextual consent proof
+ hold/moderation/privacy state
        ↓
Digital Goods local policy + lifecycle validation
        ↓
DigitalDownloadAsset / TermsAcceptance / DigitalDownloadGrant
        ↓
Media-owned short-lived signed object delivery
        ↓
DigitalDownloadEvent + required AccessAuditLog
        ↓
revocation / expiration / downstream projection or notification effects
```

### Why this deserves its own Module boundary

Digital delivery contains domain truth that neither Marketplace Supply nor Media can safely own:

- Marketplace owns **what is sold**; Digital Goods owns **how a digital purchase is governed and delivered**.
- Order owns **whether a transaction currently entitles delivery**; Digital Goods owns **temporary download access and usage state**.
- Media owns **whether the file is safe and how private object access is technically issued**; Digital Goods owns **why this buyer may receive this paid file**.
- Consent owns **generic versioned acceptance proof**; Digital Goods owns **the buyer/Offering/Order-specific digital policy snapshot**.
- Video owns **streaming provider state and playback grants**; Digital Goods owns **commercial digital policy and course accessibility meaning**.

---

## 3. Owned Truth

### 3.1 Models and records

| Record | Meaning | Ownership rule |
| --- | --- | --- |
| `DigitalGoodsPolicy` | Current digital purchase/delivery policy attached one-to-one to an Offering, including license type, refund policy type, version identifiers, delivery TTL defaults, and product-surface control defaults. | Digital Goods truth. It is not Offering truth and not generic Consent truth. |
| `DigitalGoodsTermsAcceptance` | Buyer/User and optional Order-specific evidence that the exact digital terms/refund/license versions presented for an Offering were accepted, with content hash and request evidence. | Digital Goods contextual proof. `ConsentLog` remains generic consent/version proof. |
| `DigitalDownloadAsset` | A downloadable product/course delivery object backed by a safe `MediaAsset`. | Digital Goods delivery truth. `MediaAsset` remains file/storage/safety truth. |
| `DigitalDownloadGrant` | A temporary, buyer/User-specific grant authorizing access to one `DigitalDownloadAsset`, normally derived from an authoritative Order. | Digital Goods temporary-access truth. It is not permanent ownership and not payment truth. |
| `DigitalDownloadEvent` | Append-only digital-delivery evidence for signed URL issuance/denial, download start/completion/failure, grant expiry/revocation, and provider errors. | Digital Goods domain access ledger. It does not replace `AccessAuditLog`. |
| `ChildDirectedContentDeclaration` | Creator/admin declaration and review state concerning whether a digital Offering is child-directed and which product-surface controls must apply. | Digital Goods truth. It is not User age truth or COPPA compliance completion. |
| `MinorPrivacyControl` | Applied/revoked product-surface control projection for tracking cookies, targeted ads, public comments, and behavioral analytics. | Digital Goods projection/control record. It must not become global Privacy truth. |
| `CourseAccessibilityAsset` | Accessibility meaning/status for captions, transcripts, audio description, or descriptive text associated with an Offering/course/video. | Digital Goods truth for accessibility semantics. Media owns the backing file; Video owns course-video state. |

### 3.2 Enums and statuses

Owned enum/status vocabulary:

- `DigitalStorageProvider`
- `DigitalDownloadAssetStatus`
- `DigitalDownloadGrantStatus`
- `DigitalDownloadEventType`
- `DigitalGoodsLicenseType`
- `DigitalGoodsRefundPolicyType`
- `DigitalGoodsTermsAcceptanceStatus`
- `ChildDirectedDeclarationStatus`
- `AccessibilityAssetType`
- `AccessibilityAssetStatus`

Digital Goods **does not own** `ConsentType`, even where digital-specific consent keys are consumed.

### 3.3 Lifecycles owned

- digital-goods policy configuration and version references;
- digital-goods contextual acceptance evidence;
- downloadable asset delivery state;
- paid download grant state and usage;
- download-domain event evidence;
- child-directed declaration/review state;
- minor-privacy-control application/revocation;
- course accessibility asset state.

### 3.4 Domain ledgers and proof

- `DigitalDownloadEvent` is the Module’s append-only delivery/access evidence.
- `DigitalGoodsTermsAcceptance` is the contextual policy snapshot/proof.
- `ChildDirectedContentDeclaration.declarationTextHash` is declaration-integrity evidence, not a generic consent record.
- `DigitalDownloadGrant.tokenHash` and `presignedUrlHash` may prove credential issuance without storing reusable credentials.

### 3.5 Projections owned

`MinorPrivacyControl` is explicitly a projection/control record derived from an authoritative child-directed decision. It may be queried by product surfaces but must not be treated as the legal declaration itself.

No Typesense/search projection is owned here.

### 3.6 Policies and invariants owned

Digital Goods owns:

- which digital policy is currently applicable to an Offering;
- whether a given digital policy version must be accepted for the action;
- whether a `DigitalDownloadAsset` is locally eligible for grant/access;
- grant TTL and max-download policy after upstream entitlement is established;
- grant state validation at access time;
- what digital event is appended for each delivery outcome;
- how an authoritative moderation/refund/privacy instruction maps to Digital Goods local transitions;
- how child-directed declarations map to approved product-surface controls;
- how accessibility records affect Digital Goods readiness.

Digital Goods does **not** own the legal validity of terms, transaction payment state, file safety, moderation decision, general privacy request, or search publication decision.

---

## 4. Explicit Non-Ownership

Coding agents must not move these responsibilities into this Module.

| Adjacent owner | Truth that stays outside Digital Goods | Prohibited Digital Goods substitute |
| --- | --- | --- |
| Identity & Access | authentication/session identity, MFA/passkey challenges, account recovery | `digitalGoodsAuth.ts`, local current-user/session resolver |
| Role / Authority | generic platform/ownership permission interpretation | `isAdmin`, `canManageOffering`, local RBAC tables or permission engine |
| Customer / Buyer Profile | commercial buyer actor identity | local `Buyer`/`Customer` record or buyer-type boolean |
| Track Subscription & Entitlement | plan, entitlement grant, quota/usage-period truth | `isPremium`, `hasDigitalAccess`, local plan flags; only consume a concrete entitlement if explicitly defined |
| Marketplace Supply | `Offering`, `ProductDetails`, `CourseDetails`, `PricingTier`, Offering lifecycle/publish state | shadow Offering/product/course tables or direct lifecycle mutations |
| Transaction / Order | `Order`, `OrderEvent`, transaction/payment/refund/dispute entitlement | local `isPaid`, Stripe reads, payment-provider status as access truth |
| Payment / Payout / Tax | Stripe/Avalara tax calculation/transaction truth | tax calculator, Stripe client, local tax status |
| Media / File Access | `MediaAsset`, upload policy/session, MIME validation, malware scan, metadata scrub, storage object keys, signed object URLs | R2/S3 client, file scanner, MIME sniffer, signed URL helper, object-key generator |
| Video Session | `CourseVideoAsset`, playback grants/events, Mux/provider state | Mux client, playback URL/token generator, local course-video state |
| Consent & Disclosure | `ConsentType`, active consent version catalog, `ConsentLog` | local generic consent table or consent enum fork |
| Content Moderation & Legal Notice | DMCA/legal validity, `ModerationCase`, `ModerationAction`, legal-notice lifecycle | local DMCA adjudication, moderation queue, direct legal decision flags |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle | `blocked`, `suspendedForCompliance`, local hold table |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption` | Digital Goods privacy workflow or local retention-exemption record |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | generic audit/access log tables inside Digital Goods |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense documents/indexing | Typesense client, indexer, local search queue |
| Notification | Notification persistence, template rendering, email/SMS/push delivery | SES/SMS/push client, local notification delivery table |
| Observability / Ops | `IntegrationFailure`, `QueueJob`, `OpsIncident`, generic logs/metrics | operational tables used as download business state |
| Identity age gate | `AgeGateAttempt`, `AgeGateBlock` | product declaration used as User age proof |

### Historical ownership conflicts now resolved by CL-05

The current Module registry/glossary collision watchlist previously showed Marketplace Supply also claiming `DigitalGoodsPolicy`, `DigitalDownloadAsset`, `ChildDirectedContentDeclaration`, `MinorPrivacyControl`, and `CourseAccessibilityAsset`. CL-05 now binds those records to Digital Goods Access. Marketplace Supply owns Offering authoring/publish lifecycle and consumes Digital Goods readiness through public interfaces.

### Consent ownership correction

Historical registry rows that place agreement/e-sign `ConsentType.*` values under Digital Goods are not binding. `ConsentType` belongs to Consent & Disclosure. Agreement execution consent belongs to the Agreement/Transaction workflow. Digital Goods may consume approved digital-specific consent keys and links the resulting `ConsentLog` to `DigitalGoodsTermsAcceptance` where required.

---

## 5. Module Architecture Principles

1. **Order authorizes normal purchased delivery; Digital Goods grants temporary delivery access.** A grant cannot replace Order truth.
2. **MediaAsset is file truth.** A `DigitalDownloadAsset` may snapshot display/delivery metadata, but current file safety/readiness always comes from Media.
3. **Digital Goods authorizes; Media signs.** No R2/S3 presign logic or object-storage SDK belongs in this Module.
4. **No permanent paid-file URLs.** Every private paid download uses a bounded grant and Media-owned short-lived signed access.
5. **Terms evidence is contextual, versioned, and immutable.** New terms versions create new acceptance evidence; historical rows are never rewritten to look current.
6. **Consent is proof, not digital entitlement.** `ConsentLog` cannot by itself authorize a download.
7. **Temporary grant mechanics may be shared; `DigitalDownloadGrant` truth stays separate.** Never merge with `MediaAccessGrant`, `CourseVideoPlaybackGrant`, `AgreementAccessGrant`, or `SensitiveActionSession`.
8. **Grant validity is checked at request time.** Worker lag must never keep an expired/revoked/refunded/disabled path valid.
9. **Bounded usage is database-atomic.** No read-then-write download counter enforcement.
10. **Moderation decides; Digital Goods executes.** `disabled_by_dmca` records the local effect, not the validity of a legal notice.
11. **Privacy orchestrates; Digital Goods executes owner-local disposition.** Product deletion and privacy erasure remain distinct.
12. **Download events and generic access audit are separate evidence.** One must not replace the other.
13. **Child-directed content is a product declaration, not User age truth.** No account-age inference is permitted from the declaration.
14. **Accessibility meaning stays separate from files and video.** Media owns bytes; Video owns streaming state; Digital Goods owns captions/transcript/accessibility meaning.
15. **Search is downstream projection.** Digital Goods requests refresh; it never writes Typesense or `SearchUpsertEvent` directly.
16. **Provider state is not Digital Goods truth.** `DigitalStorageProvider` is delivery metadata; provider clients remain behind Media/Video owners.
17. **Legal-gated behavior fails closed.** Missing approved policy text, child-directed criteria, waiver criteria, or consent mapping cannot be guessed into production behavior.
18. **No direct cross-domain repositories.** `Offering`, `Order`, `MediaAsset`, Consent, Moderation, Privacy, and Search facts come through owner interfaces/events.
19. **Destructive cascades require retention review.** Schema cascade convenience must not erase transaction/consent/access proof that is retention-locked.
20. **Every asynchronous effect is idempotent, correlated, retry-classified, and observable.**

---

## 6. Proposed Folder / Code Structure

Follow the root repository convention if it differs. The following responsibilities are binding even if folder names change.

```text
src/modules/digital-goods-access/
├── application/
│   ├── commands/
│   │   ├── upsert-digital-goods-policy.ts
│   │   ├── record-digital-goods-terms-acceptance.ts
│   │   ├── register-digital-download-asset.ts
│   │   ├── issue-digital-download-grant.ts
│   │   ├── issue-digital-download-access.ts
│   │   ├── revoke-digital-download-grant.ts
│   │   ├── apply-digital-moderation-decision.ts
│   │   ├── declare-child-directed-content.ts
│   │   ├── review-child-directed-declaration.ts
│   │   ├── register-course-accessibility-asset.ts
│   │   └── update-course-accessibility-asset-state.ts
│   ├── queries/
│   │   ├── get-digital-goods-policy.ts
│   │   ├── get-digital-goods-terms-evidence.ts
│   │   ├── get-digital-download-readiness.ts
│   │   ├── list-user-digital-downloads.ts
│   │   ├── get-digital-delivery-evidence.ts
│   │   ├── get-minor-privacy-controls.ts
│   │   └── get-course-accessibility-readiness.ts
│   └── services/
│       ├── digital-download-access-service.ts
│       ├── digital-goods-policy-service.ts
│       └── digital-goods-privacy-executor.ts
├── domain/
│   ├── policies/
│   │   ├── digital-download-eligibility.ts
│   │   ├── digital-grant-usage-policy.ts
│   │   ├── digital-goods-readiness.ts
│   │   ├── child-directed-control-policy.ts
│   │   └── accessibility-readiness-policy.ts
│   ├── transitions/
│   │   ├── digital-download-asset-transition.ts
│   │   ├── digital-download-grant-transition.ts
│   │   ├── digital-terms-acceptance-transition.ts
│   │   ├── child-declaration-transition.ts
│   │   └── accessibility-asset-transition.ts
│   └── events/
│       ├── event-types.ts
│       └── event-payloads.ts
├── contracts/
│   ├── commands.ts
│   ├── queries.ts
│   ├── decisions.ts
│   ├── privacy.ts
│   └── integration-events.ts
├── infrastructure/
│   ├── repositories/
│   │   ├── digital-goods-policy-repository.ts
│   │   ├── digital-download-repository.ts
│   │   ├── child-directed-repository.ts
│   │   └── accessibility-repository.ts
│   └── workers/
│       ├── expire-digital-download-grants.ts
│       ├── revoke-digital-download-grants.ts
│       └── reconcile-digital-download-evidence.ts
├── public/
│   ├── commands.ts
│   ├── queries.ts
│   ├── events.ts
│   └── privacy.ts
├── components/                 # only Module-owned policy/download/control/accessibility UI
│   ├── digital-policy-form.tsx
│   ├── digital-terms-acceptance.tsx
│   ├── digital-download-list.tsx
│   ├── child-directed-declaration.tsx
│   └── course-accessibility-list.tsx
└── tests/
    ├── unit/
    ├── integration/
    ├── contracts/
    ├── concurrency/
    ├── privacy/
    └── e2e/
```

### Folders that must not exist here

Do not create:

- `providers/r2`, `providers/s3`, or a storage SDK wrapper;
- `payments/`, `stripe/`, `tax/`;
- `auth/`, generic `permissions/`, or RBAC infrastructure;
- `consent/` owning `ConsentLog`;
- `search/` owning Typesense or SearchUpsertEvent;
- `notifications/providers/`;
- generic `audit/`, `queue/`, `idempotency/`, `locks/`, `crypto/`, or `shared/access-grant` infrastructure.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery/UI | Digital policy form, terms presentation/acceptance context, buyer download library/action, child-directed declaration/control display, accessibility tracking UI | Payment UI truth, generic consent UI system, Media uploader internals, video player provider auth, generic admin/moderation UI |
| Application services | Command/query orchestration; dependency calls; Digital Goods transaction boundaries; owner event requests | another Module’s lifecycle transition or direct cross-domain Prisma repository |
| Domain policy | policy-version checks, digital asset readiness, grant TTL/usage rules, local moderation mapping, control/readiness composition | legal interpretation, Order entitlement, file safety, generic authorization, privacy-retention exemption truth |
| Repositories/data access | only Digital Goods-owned records and transactional owner-event/outbox hooks permitted by root architecture | `Order`, `Offering`, `MediaAsset`, `ConsentLog`, Moderation, Privacy, Search repositories |
| Workers | grant expiration, bulk revocation, owner-local privacy/reconciliation tasks | generic queue framework, provider storage client, Search worker, Notification delivery worker |
| Provider adapters | none for normal MVP digital downloads | R2/S3, Stripe/Avalara, Mux provider adapters; those remain with Media/Payment/Video |
| Public contracts | Digital Goods commands, queries, decisions, integration events, Privacy executor | generic cross-platform auth/authorization/consent/queue contracts |
| Domain ledgers | `DigitalDownloadEvent` | `AuditEvent`, `AccessAuditLog`, `MediaAccessEvent`, `CourseVideoPlaybackEvent` |

---

## 8. Data Model

### 8.1 `DigitalGoodsPolicy`

**Purpose:** current Offering-level commercial digital-delivery configuration.

**Key relationships:**

- one-to-one with `Offering` via unique `offeringId`;
- one-to-many with `DigitalGoodsTermsAcceptance`;
- one-to-many with `ChildDirectedContentDeclaration`.

**Authoritative fields:**

- `licenseType`;
- `refundPolicyType`;
- `termsVersion`, `refundPolicyVersion`, `licenseVersion`;
- `immediateAccessDisclosureRequired`;
- `singleUserOnly`, `redistributionProhibited`;
- `defaultDownloadTtlHours`, `defaultStreamingTtlMinutes`;
- product-surface defaults: `publicCommentsAllowed`, `trackingCookiesAllowed`, `targetedAdsAllowed`.

**Lifecycle:** no status column. This is the current configuration record. History is preserved through version identifiers and contextual acceptance evidence, not by rewriting old acceptance rows.

**Uniqueness:** `offeringId` is unique.

**Concurrency:** policy edits must use optimistic concurrency (`updatedAt` or a later explicit version column) and reject stale writes.

**Retention:** deleting an Offering currently cascades to this record. Production deletion must be reviewed against retained terms/access evidence before relying on cascade behavior.

**Binding interpretation:** `DigitalGoodsPolicy` is current policy configuration, not the immutable legal-text store. The exact historical text/version must remain reproducible from the approved version source plus the acceptance hash. If the approved Consent/version catalog cannot supply that requirement, architecture must add a specific immutable policy snapshot rather than silently using mutable UI copy.

### 8.2 `DigitalGoodsTermsAcceptance`

**Purpose:** contextual proof that a User accepted the digital terms applicable to an Offering and optionally an Order.

**Authoritative fields:**

- `userId`, optional `orderId`, `offeringId`;
- optional `digitalGoodsPolicyId`, `consentLogId`;
- `status`;
- `termsVersion`, `refundPolicyVersion`, `licenseVersion`;
- `acceptedTextHash`, `checkboxLabel`;
- minimized request evidence `ipHash`, `userAgent`;
- `acceptedAt`, `revokedAt`.

**Lifecycle/status:** `accepted → revoked | voided`. A later re-acceptance or a new version creates a new acceptance record; it does not rewrite the previous row.

**Uniqueness:** no domain uniqueness is currently encoded. Command idempotency must prevent duplicate same-request acceptance while still allowing new version/context rows.

**Concurrency:** acceptance checks the current approved policy/version immediately before insertion. Stale version submissions fail.

**Retention/privacy:** this is consent/transaction-adjacent proof and may require retention. IP/user-agent data should be minimized/anonymized when Privacy permits while preserving required proof.

### 8.3 `DigitalDownloadAsset`

**Purpose:** the downloadable delivery object attached to an Offering and safe `MediaAsset`.

**Authoritative fields:**

- `offeringId`, optional product/course detail relation;
- `mediaAssetId`;
- `status`;
- delivery/display metadata;
- `requiresPurchase`;
- `defaultTtlHours`;
- `maxDownloadsPerGrant`;
- disable/delete metadata.

**Relationship rule:** `mediaAssetId` must point to a Media-owned asset that is ready and compatible with the expected upload context. If product/course relation IDs are supplied, they must be validated through Marketplace owner contracts and must correspond to the same Offering context.

**Snapshot rule:** `fileName`, `fileExtension`, `mimeType`, `fileSizeBytes`, and `provider` are delivery snapshots/convenience metadata. They are not current storage/safety truth. Current access always revalidates through Media.

**Lifecycle/status:** `draft`, `upload_pending`, `ready`, `disabled`, `disabled_by_dmca`, `disabled_by_moderation`, `archived`, `deleted`.

**Concurrency:** transitions serialize on asset ID. Moderation/restoration and archival/deletion must reject stale state.

**Retention:** current Offering relation uses cascade delete, and grants/events cascade through the asset. That is unsafe as a default production-retention assumption. Destructive migration/cascade review is required before production deletion behavior is enabled.

### 8.4 `DigitalDownloadGrant`

**Purpose:** bounded temporary access to one DigitalDownloadAsset.

**Authoritative fields:**

- `digitalDownloadAssetId`, `userId`, optional `orderId`;
- `status`;
- optional `tokenHash`, `presignedUrlHash`;
- `downloadCount`, optional `maxDownloads`;
- deny/revoke reasons;
- request evidence;
- `grantedAt`, first/last use, `expiresAt`, `revokedAt`.

**Normal access basis:** a qualifying authoritative Order through `SH-025 authorizeOrderEntitlement`.

**Optional `orderId`:** schema allows null, but approved non-purchase bases are unresolved. Production complimentary/admin/library access is out of scope until a canonical alternate access-basis taxonomy is approved.

**Concurrency-sensitive fields:** `downloadCount`, `status`, `expiresAt`, `revokedAt`.

**Proposed Ruling — `used` semantics:** when `maxDownloads` is finite, transition to `used` only when the configured allowance is exhausted. If `maxDownloads` is null, ordinary use does not terminally consume the grant; expiry or revocation ends access. This ruling must be confirmed before production if product policy intends different semantics.

**Token uniqueness:** if token-hash lookup is enabled, token hash must be uniqueness-protected before production. An authenticated grant-ID flow may avoid bearer-token lookup entirely.

**Retention:** grant access may be revoked while evidence is retained. Do not hard-delete solely because access ended.

### 8.5 `DigitalDownloadEvent`

**Purpose:** immutable domain evidence for digital download delivery.

**Types:** `presigned_url_issued`, `presigned_url_denied`, `download_started`, `download_completed`, `download_failed`, `grant_expired`, `grant_revoked`, `provider_error`.

**Authoritative relationships:** asset, optional grant, optional user, optional Order, provider, optional provider request ID.

**Append-only rule:** events are not updated to revise history. Corrections append new evidence or use explicit metadata/source references according to owner policy.

**Provider evidence:** `providerRequestId` is correlation evidence, not provider truth. Duplicate event prevention uses command/event idempotency, not a general provider-event ledger unless a future owned callback requires one.

**Retention:** delivery events may support disputes, refund evidence, fraud/security, or compliance; they require retention evaluation before erasure.

### 8.6 `ChildDirectedContentDeclaration`

**Purpose:** preserve creator/admin declaration and review evidence concerning child-directed digital content.

**Authoritative fields:** Offering/policy reference, declaring/reviewing User, `status`, `isChildDirected`, intended age band, applied control booleans, declaration hash, admin note, declaration/review times.

**Current-state concern:** multiple declarations per Offering are permitted. The exact “effective declaration” selection and review criteria are legal-gated and unresolved. Code must not infer “latest row wins” for production without an approved rule.

**Privacy:** age range here describes intended content audience, not the age of any particular User.

### 8.7 `MinorPrivacyControl`

**Purpose:** materialize product-surface restrictions derived from a child-directed declaration.

**Authoritative fields:** declaration/Offering reference, target type/ID, disabled-control booleans, reason, applied/revoked timestamps.

**Projection rule:** controls are derived from the declaration/approved policy. Consumers query the effective controls; they must not infer legal status from the projection.

**Target-type concern:** `targetType` is currently a string. Only server-defined target types may be written. User input must not introduce arbitrary target vocabularies.

### 8.8 `CourseAccessibilityAsset`

**Purpose:** track the accessibility meaning and status of captions, transcripts, audio description, descriptive text, or other accessibility support.

**Relationships:** optional Offering, `CourseDetails`, `CourseVideoAsset`, and backing `MediaAsset`; uploading/reviewing User.

**Authoritative fields:** `type`, `status`, language/label, `isRequired`, `isDefault`, provider reference, failure/review evidence, timing fields.

**Concurrency:** state transitions serialize on accessibility asset ID. Default selection must avoid ambiguous multiple defaults for the same course/type/language once that policy is implemented.

**Retention/privacy:** backing Media is handled by Media Privacy execution. Digital Goods inventories its semantic/accessibility record separately.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Digital goods terms acceptance

```text
accepted
├─→ revoked
└─→ voided
```

- **Transition owner:** Digital Goods Access.
- **Triggers:** explicit approved revocation/void action, legal/product correction, invalidated acceptance.
- **Terminal states:** `revoked`, `voided` for that row.
- **Reopen rule:** never reopen the same row; create a new acceptance for a newly presented version/context.
- **Proof:** immutable acceptance row plus Consent proof reference where required.
- **Prohibited shortcut:** mutable `accepted=true` on User/Order/Offering.

### 9.2 Digital download asset

```text
draft
  └─→ upload_pending
        └─→ ready

ready
  ├─→ disabled
  ├─→ disabled_by_dmca
  ├─→ disabled_by_moderation
  ├─→ archived
  └─→ deleted

disabled* ─→ ready        only after authorized restore + Media revalidation
archived   ─→ ready        only through explicit owner reactivation policy
deleted    ─X              terminal for product lifecycle; retained evidence may remain elsewhere
```

- **Transition owner:** Digital Goods Access.
- **External triggers:** Media readiness, authorized moderation decision, seller/admin archival, Privacy/product deletion instruction.
- **Concurrency:** owner transition under aggregate lock/optimistic version.
- **Proof:** domain event/outbox and AuditEvent for material admin/moderation actions where required.
- **Prohibited shortcut:** setting `ready` because `mediaAssetId` exists.

### 9.3 Digital download grant

```text
             ┌─→ used       finite allowance exhausted (Proposed Ruling)
active ──────┼─→ expired    server time >= expiresAt / expiration transition
             └─→ revoked    authoritative refund/moderation/privacy/security/lifecycle instruction

denied                       creation-time terminal state only if denial is persisted as a grant
```

- **Transition owner:** Digital Goods Access.
- **Current access check:** validates status, current server time, current asset state, usage count, actor binding, and current upstream entitlement where policy requires revalidation.
- **Concurrency:** download allowance consumption is atomic; revocation/use/expiry races return deterministic current-state result.
- **Reopen rule:** never reactivate an expired/revoked/used grant; issue a new authorized grant.
- **Proof:** `DigitalDownloadEvent` plus generic sensitive audit where required.

### 9.4 Child-directed declaration

Schema states:

`not_declared`, `declared_not_child_directed`, `declared_child_directed`, `admin_review_required`, `approved`, `rejected`, `disabled`.

The exact transition graph, automatic-review criteria, effective-declaration selection, and whether some declarations may become effective without admin review remain **Unresolved / legal-gated**. The implementation must support recording declarations and explicit admin review states without inventing approval logic.

### 9.5 Accessibility asset

Safe mechanical graph:

```text
missing
├─→ uploaded
├─→ not_required      only through approved policy/reviewer authority
└─→ waived            only through approved waiver authority

uploaded ─→ processing ─→ ready
                  ├─→ failed
                  └─→ rejected

failed   ─→ processing/uploaded through explicit retry/replacement
rejected ─→ new/replacement review path; never silently ready
```

- **Transition owner:** Digital Goods Access.
- **Backing-file rule:** cannot become `ready` while required Media backing asset is non-ready.
- **Waiver rule:** production waiver authority/criteria are unresolved and fail closed.

---

## 10. Commands

### `upsertDigitalGoodsPolicy`

- **Purpose:** create/update the current Offering digital policy and version references.
- **Actor:** authorized Offering owner/admin.
- **Inputs:** Offering ID, policy fields, legal/version identifiers, expected version/updatedAt, idempotency key.
- **Preconditions:** SH-001, SH-002, SH-123; approved policy/version content for production activation.
- **Writes:** `DigitalGoodsPolicy`.
- **Shared operations:** SH-001, SH-002, SH-044, SH-052, SH-072, SH-123, SH-029 as required.
- **Effects:** optional domain event/search readiness effect if public eligibility changes.
- **Idempotency:** same command key + fingerprint replays result; stale version conflicts.
- **Failures:** unauthorized, target invalid, stale policy, invalid TTL/rule combination, legal policy unavailable.

### `recordDigitalGoodsTermsAcceptance`

- **Purpose:** persist the exact contextual acceptance for a digital purchase/access flow.
- **Actor:** authenticated buyer/User.
- **Inputs:** Offering/optional Order, displayed versions, content hash/checkbox label, required Consent proof, idempotency key.
- **Preconditions:** policy/version still current/applicable; SH-007/008 proof satisfied when required; actor/Order relationship valid.
- **Writes:** immutable `DigitalGoodsTermsAcceptance`.
- **Shared operations:** SH-001, SH-004 where buyer context is needed, SH-007, SH-008, SH-009 where applicable, SH-044, SH-072, SH-025/123 as appropriate.
- **Effects:** domain event only if a downstream workflow needs acceptance fact.
- **Failures:** stale version, missing consent proof, Order/Offering mismatch, unauthorized actor, legal policy unavailable.

### `registerDigitalDownloadAsset`

- **Purpose:** create/update a Digital Goods delivery record around a safe Media asset.
- **Actor:** authorized Offering owner/admin/system workflow.
- **Inputs:** Offering/product/course refs, MediaAsset ID, delivery metadata/policy, idempotency key.
- **Preconditions:** owner target valid; Media ready/appropriate; no forbidden public storage assumption.
- **Writes:** `DigitalDownloadAsset`.
- **Shared operations:** SH-001, SH-002, SH-044, SH-090, SH-123, SH-053.
- **Effects:** readiness-domain event/search refresh where relevant.
- **Failures:** invalid target, Media non-ready, context mismatch, stale asset state.

### `issueDigitalDownloadGrant`

- **Purpose:** create a bounded temporary grant for normal purchased delivery.
- **Actor:** authenticated buyer/User or narrowly scoped system workflow.
- **Inputs:** asset ID, Order ID, actor/buyer context, acceptance evidence, TTL/max uses, idempotency key.
- **Preconditions:** asset ready, Order entitlement allowed, required acceptance satisfied, applicable hold clear, actor relationship valid.
- **Writes:** `DigitalDownloadGrant`.
- **Shared operations:** SH-001, SH-004, SH-011, SH-025, SH-044, SH-074, SH-088, SH-125/046 as needed.
- **Effects:** grant-issued domain event; no storage URL yet unless combined by higher application service.
- **Failures:** Order denied, policy missing, asset unavailable, hold blocked, unsupported non-purchase basis.

### `issueDigitalDownloadAccess`

- **Purpose:** validate current grant and obtain a Media-owned short-lived signed URL.
- **Actor:** authenticated grant owner.
- **Inputs:** grant ID/secure token if enabled, asset ID, request context, idempotency key for the access attempt.
- **Preconditions:** grant active and unexpired; actor binding; asset ready; current Order still qualifies where policy requires; usage available; no applicable hold/moderation block.
- **Writes:** atomic grant usage fields/status and `DigitalDownloadEvent`; generic audit through owner interface.
- **Shared operations:** SH-001, SH-011, SH-025, SH-030, SH-044, SH-051/057, SH-087, SH-088, SH-125, SH-032/034/037.
- **Effects:** returns URL only after Media approves/signs; may publish access fact only if a downstream workflow explicitly needs it.
- **Failures:** expired, revoked, exhausted, wrong actor, asset disabled, Order no longer entitled, Media temporary failure.

### `revokeDigitalDownloadGrant`

- **Purpose:** revoke one or more grants after an authoritative source invalidates access.
- **Actor/context:** authorized owner action or trusted system event from Order/Moderation/Privacy/security.
- **Inputs:** grant/asset/Order target, source reason/reference, idempotency key.
- **Writes:** grant status/revoke metadata and `DigitalDownloadEvent`.
- **Shared operations:** SH-044, SH-045, SH-047/048 for bulk work, SH-089, SH-125, SH-029/030 where applicable.
- **Failures:** stale already-terminal grant returns idempotent result; invalid source reference rejected.

### `applyDigitalModerationDecision`

- **Purpose:** execute an authoritative moderation/legal action against Digital Goods-owned state.
- **Inputs:** moderation action/case ID, target, requested action, actor/system context, idempotency key.
- **Preconditions:** authenticated/verified moderation envelope; target mapping valid.
- **Writes:** asset disable/restore status and affected grants/events.
- **Shared operations:** SH-103, SH-089, SH-044, SH-047/048, SH-091, SH-029/030, SH-041 as configured.
- **Failures:** unsupported action, stale target, partial bulk-revocation failure; source moderation decision remains authoritative.

### `declareChildDirectedContent`

- **Purpose:** record creator declaration without treating it as User-age truth.
- **Actor:** authorized seller/admin.
- **Inputs:** Offering/policy, declaration, intended age range, declaration text hash, idempotency key.
- **Preconditions:** valid Offering target and approved declaration version for production.
- **Writes:** `ChildDirectedContentDeclaration`.
- **Shared operations:** SH-001, SH-002, SH-044, SH-072, SH-123, SH-029 where required.
- **Failures:** invalid target/range/version; legal criteria unavailable prevents unsupported auto-approval.

### `reviewChildDirectedDeclaration`

- **Purpose:** apply an explicitly authorized review outcome.
- **Actor:** authorized admin/reviewer; step-up if later required by root matrix.
- **Writes:** declaration review fields/status and derived control workflow.
- **Shared operations:** SH-002, SH-011, SH-029, SH-041, SH-091, SH-053.
- **Failures:** stale declaration, unauthorized reviewer, unapproved legal criteria.

### `registerCourseAccessibilityAsset`

- **Purpose:** create the accessibility-semantic record around a safe Media asset or required placeholder.
- **Actor:** authorized seller/admin/system workflow.
- **Inputs:** Offering/course/video refs, MediaAsset if supplied, type/language/default/required flags.
- **Preconditions:** valid owner targets; Media ready when a file is attached.
- **Writes:** `CourseAccessibilityAsset`.
- **Shared operations:** SH-001, SH-002, SH-044, SH-090, SH-123.
- **Failures:** target mismatch, invalid file context, duplicate default conflict, unauthorized waiver/review state.

### `updateCourseAccessibilityAssetState`

- **Purpose:** transition accessibility processing/review status.
- **Actor:** owner worker or authorized reviewer.
- **Writes:** accessibility status/evidence.
- **Shared operations:** SH-053, SH-052, SH-029, SH-041/091 where configured.
- **Failures:** invalid transition, stale state, backing Media not ready, waiver criteria unavailable.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Result type | Meaning | Consumer must not infer |
| --- | --- | --- | --- | --- |
| `getDigitalGoodsPolicy` | Marketplace, checkout, Order, seller UI | source truth | current policy configuration/version refs | legal text validity or Offering status |
| `getDigitalGoodsTermsAcceptance` | Order, Dispute, support/compliance | evidence | acceptance status, versions, hash, links | generic consent completeness for unrelated workflows |
| `getDigitalDownloadReadiness` | Marketplace, checkout | readiness decision | whether required download assets are locally ready and why | Media safety details beyond returned evidence; Offering publish truth |
| `evaluateDigitalDownloadEligibility` | grant/access application service | decision | local Digital Goods allow/deny after supplied upstream facts | Order/payment truth or generic authorization |
| `listUserDigitalDownloads` | buyer UI | contextual read model | currently discoverable purchased/authorized download items and local grant state | permanent ownership, payment provider state |
| `getDigitalDeliveryEvidence` | Order, Dispute, support, Privacy/compliance | evidence | acceptance/grant/event evidence with safe references | refund adjudication outcome |
| `getMinorPrivacyControls` | product surfaces | projection | effective Digital Goods control projection for a known target | User age or legal compliance completion |
| `getCourseAccessibilityReadiness` | Marketplace, Video, course UI | readiness decision | required/ready/missing/failed/waived/not-required accessibility facts | course-video provider readiness or general UI accessibility compliance |

### Stable decision reason codes

Public decisions should use stable Module reason codes such as:

- `digital_policy_missing`
- `digital_policy_version_stale`
- `digital_policy_not_production_approved`
- `digital_terms_required`
- `digital_terms_version_mismatch`
- `order_entitlement_denied`
- `unsupported_access_basis`
- `download_asset_not_ready`
- `download_asset_disabled`
- `download_asset_archived`
- `download_grant_expired`
- `download_grant_revoked`
- `download_grant_exhausted`
- `download_grant_actor_mismatch`
- `compliance_hold_blocked`
- `media_access_unavailable`
- `temporary_delivery_failure`
- `child_declaration_review_required`
- `accessibility_asset_missing`
- `accessibility_asset_not_ready`
- `accessibility_waiver_not_approved`
- `stale_write`

Consumers must not branch on provider-native errors.

---

## 12. Public Module Interface

### Public commands

- `upsertDigitalGoodsPolicy`
- `recordDigitalGoodsTermsAcceptance`
- `registerDigitalDownloadAsset`
- `issueDigitalDownloadGrant`
- `issueDigitalDownloadAccess`
- `revokeDigitalDownloadGrant`
- `revokeDigitalDownloadGrantsForAsset`
- `revokeDigitalDownloadGrantsForOrder`
- `applyDigitalModerationDecision`
- `declareChildDirectedContent`
- `reviewChildDirectedDeclaration`
- `registerCourseAccessibilityAsset`
- `updateCourseAccessibilityAssetState`

### Public queries

- `getDigitalGoodsPolicy`
- `getDigitalGoodsTermsAcceptance`
- `getDigitalDownloadReadiness`
- `evaluateDigitalDownloadEligibility`
- `listUserDigitalDownloads`
- `getDigitalDeliveryEvidence`
- `getMinorPrivacyControls`
- `getCourseAccessibilityReadiness`
- `listCourseAccessibilityAssets`

### Emitted domain events

Event names are versioned public facts; payloads contain identifiers and minimal safe facts, never signed URLs/tokens or legal text.

Proposed stable v1 event families:

- `digital_goods.policy.updated.v1`
- `digital_goods.terms.accepted.v1`
- `digital_goods.terms.revoked.v1`
- `digital_goods.download_asset.ready.v1`
- `digital_goods.download_asset.disabled.v1`
- `digital_goods.download_asset.restored.v1`
- `digital_goods.download_grant.issued.v1`
- `digital_goods.download_grant.revoked.v1`
- `digital_goods.download_grant.expired.v1`
- `digital_goods.child_declaration.changed.v1`
- `digital_goods.minor_privacy_controls.changed.v1`
- `digital_goods.accessibility.changed.v1`

`DigitalDownloadEvent` rows are domain access evidence and do not require every row to be broadcast as an integration event.

### Privacy executor

Digital Goods implements:

- `enumerateSubjectData` through SH-096;
- `evaluateRetentionRequirement` through SH-097;
- `executePrivacyInstruction` through SH-095;
- export serialization when Privacy requires it.

Privacy owns request/job/target/exemption truth.

### Provider-facing interfaces

None are owned by Digital Goods for the normal MVP path.

- file signing/storage is Media-owned;
- course playback/provider state is Video-owned;
- payments/tax are Order/Payment-owned.

---

## 13. Inbound Dependencies

| Owner | Public operation / contract consumed | Why required | Minimum facts | May block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | establish trusted actor | actor/user/system identity, session assurance | yes | auth/session parser |
| Role / Authority | SH-002 `authorizeResourceAction` | seller/admin/buyer management/use authorization | action, resource, owner facts | yes | RBAC/ownership engine |
| Customer / Buyer Profile | SH-004 `resolveCustomerActor` | establish buyer context where commercial identity matters | User → CustomerProfile ID/status | yes | buyer identity table |
| Track Subscription & Entitlement | SH-005 only for explicitly defined digital perks | plan-based digital perk if approved | entitlement key/value/evidence | yes if that specific perk is required | generic premium flag |
| Marketplace Supply | SH-123 owner-specific target validation | verify Offering/Product/Course exists and relationship is eligible | IDs, kind/status/version, ownership facts | yes | Offering repository/lifecycle |
| Transaction / Order | SH-025 `authorizeOrderEntitlement` | normal purchased delivery basis | Order state, buyer/item relationship, refund/dispute effects | yes | payment/Order interpretation |
| Consent & Disclosure | SH-007/008/009 | generic versioned proof and active consent version | proof ID/type/version/validity | yes when required | ConsentLog or consent catalog |
| Media / File Access | SH-090 + SH-087 + Media readiness query | attach safe file and issue signed object access | MediaAsset ID/readiness/action/TTL | yes | file validation/storage/signing |
| Video Session | owner facts for `CourseVideoAsset` | accessibility association/readiness context | video asset ID/status/source refs | yes for video-specific relation | Mux/provider logic |
| Admin Review / Compliance Hold | SH-011 | reusable stop sign | applicable hold IDs/reasons/expiry | yes | local blocked flags |
| Content Moderation & Legal Notice | SH-103 | authoritative disable/restore/revoke instruction | action/case ID, target, action type | yes | DMCA/legal decision |
| Privacy / Data Erasure | SH-095–097 protocol | subject inventory, erase/anonymize/revoke/retain execution | target/disposition/retention decision | yes | privacy workflow |
| Audit / Event Ledger | SH-029/030 | generic important-action and sensitive-access proof | safe action/target/decision metadata | no rollback of committed domain truth unless required by policy | audit tables/writer |
| Search / Public Visibility | SH-091 | public projection refresh | entity/action/reason/source version | no; Search retries | Typesense client/queue |
| Notification | SH-041 | user/admin alert request | recipient context/template key/safe variables | no rollback of domain truth | provider dispatch |
| Observability / Ops | SH-032–039 | request context, safe telemetry, failure evidence | correlation, operation, safe dimensions | no business authority | ops ledgers/clients |

### CustomerProfile / User binding — Proposed Ruling

The current schema binds `DigitalGoodsTermsAcceptance` and `DigitalDownloadGrant` to `userId`, while current platform architecture defines `CustomerProfile` as commercial buyer truth. For the MVP, treat:

- `CustomerProfile` as the commercial actor resolved/validated through SH-004 and/or the authoritative Order;
- `User` as the authenticated credential/access principal recorded by the current Digital Goods schema.

Do not add a parallel buyer identity or silently infer CustomerProfile from arbitrary User data. If root actor architecture later requires `customerProfileId` on Digital Goods records, update schema and this document explicitly.

---

## 14. Outbound Consumers and Effects

| Consumer | What it may consume | Trigger/effect | Must not do |
| --- | --- | --- | --- |
| Marketplace Supply | policy existence/version, download readiness, child declaration/control readiness, accessibility readiness | publish/checkout readiness composition | directly mutate Digital Goods records |
| Transaction / Order | terms evidence and delivery evidence | checkout/fulfillment/refund/dispute workflow | infer download state from Media/provider |
| Media / File Access | validated contextual authorization/grant request | issue temporary signed object URL | infer Order entitlement from Digital Goods table alone |
| Video Session | digital policy/accessibility facts | course delivery/presentation integration | make Digital Goods policy decisions |
| Payment / Payout / Tax | digital item classification/policy facts if tax owner requests them | provider tax calculation | use download grant as payment truth |
| Consent & Disclosure | context/version needed for generic consent | record/query generic proof | replace DigitalGoodsTermsAcceptance |
| Content Moderation | execution acknowledgment/current target state | moderation workflow progress | direct Prisma update into Digital Goods |
| Privacy / Data Erasure | inventory, retention facts, execution results | privacy target workflow | directly mutate records outside owner protocol |
| Search / Public Visibility | refresh request only | re-evaluate public Offering projection | reconstruct Digital Goods readiness from raw tables |
| Review / Dispute | `getDigitalDeliveryEvidence` | dispute/refund evidence | adjudicate from provider logs alone |
| Notification | safe trigger intent | deliver buyer/seller/admin alerts | own digital lifecycle |
| Audit/Ops | safe action/failure evidence | compliance/operations visibility | replace DigitalDownloadEvent |

---

## 15. Canonical Shared Operations Used

Only Digital Goods-relevant SH operations are listed. The canonical registry remains authoritative for global definitions.

### SH-001 — `resolveAuthenticatedActor`
- **Owner:** Identity & Access
- **Class:** canonical platform capability
- **Why:** every protected seller/buyer/admin command/query needs trusted actor context.
- **Invocation:** first protected application-service step.
- **Local policy:** what Digital Goods action the actor requests.
- **Expected result:** typed actor/system context.
- **Do not build:** `digitalGoodsAuth.ts`, `currentUser.ts`, session parsing helpers.

### SH-002 — `authorizeResourceAction`
- **Owner:** Role / Authority
- **Class:** canonical cross-cutting capability
- **Why:** policy/asset/declaration/accessibility management requires resource permission.
- **Invocation:** after actor resolution and owner facts.
- **Local policy:** Digital Goods action vocabulary and relationship facts.
- **Expected result:** allow/deny with stable authority evidence.
- **Do not build:** `digitalGoodsPermissions.ts`, `isAdmin.ts`, seller guard engine.

### SH-004 — `resolveCustomerActor`
- **Owner:** Customer / Buyer Profile
- **Class:** another Module public interface
- **Why:** commercial buyer context for purchased access.
- **Invocation:** grant/listing/acceptance flows where buyer identity matters.
- **Local policy:** which Digital Goods record/action uses that customer.
- **Do not build:** `buyerResolver.ts`, local CustomerProfile lookup logic.

### SH-005 — `resolveEntitlement` (conditional)
- **Owner:** Track Subscription & Entitlement
- **Class:** canonical commercial-policy capability
- **Why:** only if an explicit digital-access perk is later defined.
- **Invocation:** before the specifically plan-gated action.
- **Local policy:** effect of that entitlement; normal purchased access remains Order-based.
- **Do not build:** `isPremiumDigital`, `hasDigitalAccess` booleans.

### SH-007 / SH-008 / SH-009 — consent proof/version operations
- **Owner:** Consent & Disclosure
- **Class:** canonical consent capability
- **Why:** versioned generic disclosure proof and active-version resolution.
- **Invocation:** terms presentation/acceptance where approved consent keys require it.
- **Local policy:** buyer/Offering/Order-specific DigitalGoodsTermsAcceptance and whether proof is sufficient.
- **Do not build:** `ConsentLog` clone, consent version catalog, digital consent enum fork.

### SH-011 — `evaluateComplianceHold`
- **Owner:** Admin Review / Compliance Hold
- **Class:** canonical cross-cutting capability
- **Why:** applicable stop signs may block grant/access/admin transitions.
- **Invocation:** before hold-sensitive action and at access revalidation where policy requires.
- **Local policy:** map hold to Digital Goods deny/revoke/freeze behavior.
- **Do not build:** local compliance blocked/suspended flags.

### SH-025 — `authorizeOrderEntitlement`
- **Owner:** Transaction / Order
- **Class:** another Module public interface
- **Why:** normal paid digital delivery depends on authoritative Order state and participant/item relationship.
- **Invocation:** grant issuance and current access revalidation.
- **Local policy:** grant TTL, use limits, and Digital Goods readiness.
- **Do not build:** `isOrderPaid.ts`, Stripe reads, local purchase check.

### SH-029 / SH-030 — audit operations
- **Owner:** Audit / Event Ledger
- **Class:** canonical audit capabilities
- **Why:** material admin actions and protected access may require generic proof.
- **Invocation:** after/beside owner transition or access decision according to audit policy.
- **Local policy:** sensitivity and safe Digital Goods context.
- **Do not build:** local AuditEvent/AccessAuditLog writer or table.

### SH-032 / SH-034 / SH-037 — request context, telemetry sanitization, integration failure
- **Owner:** Observability / Ops
- **Class:** platform/cross-cutting operations
- **Why:** correlate download/access jobs and safely record technical failure.
- **Invocation:** every request/job; before telemetry; on integration failure.
- **Local policy:** safe dimensions and whether a failure changes Digital Goods state.
- **Do not build:** separate logger/failure table.

### SH-041 — `requestNotification`
- **Owner:** Notification
- **Class:** canonical notification capability
- **Why:** configured user/admin outcomes may require notification.
- **Invocation:** after committed source fact/outbox.
- **Local policy:** event meaning, recipient context, safe variables.
- **Do not build:** SES/SMS/push clients or templates here.

### SH-044 — `executeIdempotentCommand`
- **Owner:** platform application infrastructure
- **Class:** platform primitive
- **Why:** terms acceptance, grant issue/revoke, moderation, and privacy work may retry.
- **Invocation:** command boundary before business effect.
- **Local policy:** semantic key/fingerprint and replay behavior.
- **Do not build:** Digital Goods idempotency table/framework.

### SH-045 / SH-046 — domain event inbox/outbox
- **Owner:** platform event infrastructure
- **Class:** platform primitives
- **Why:** consume Order/moderation/refund facts once and publish committed Digital Goods facts reliably.
- **Invocation:** inbound event handler and source transaction commit.
- **Local policy:** event names, payload meaning, consumer side effect.
- **Do not build:** local event bus/outbox/inbox framework.

### SH-047 / SH-048 — reliable jobs and retry
- **Owner:** shared queue/platform infrastructure
- **Class:** platform primitives
- **Why:** expiration, bulk revocation, privacy, and reconciliation need durable work.
- **Invocation:** after committed source fact when work is asynchronous.
- **Local policy:** payload, completion meaning, retryability/permanent failure.
- **Do not build:** `downloadQueue.ts`, custom dead-letter/retry framework.

### SH-051 / SH-052 / SH-053 — concurrency/state transition mechanics
- **Owner:** shared persistence/state-machine infrastructure
- **Class:** shared mechanism / separate truth
- **Why:** serialize grant/asset transitions, reject stale writes, reuse transition plumbing.
- **Invocation:** mutable aggregate commands.
- **Local policy:** lock key, transition graph, stale-write response.
- **Do not build:** in-memory locks or generic lifecycle policy tables.

### SH-055 — `runDeadlineExpiration`
- **Owner:** shared scheduler/queue infrastructure
- **Class:** cross-cutting capability
- **Why:** expire grants whose deadline passed.
- **Invocation:** scheduled cursor batch dispatching owner expiration command.
- **Local policy:** grant expiry transition/event.
- **Do not build:** Digital Goods cron framework.

### SH-057 — `consumeCounterAtomically`
- **Owner:** shared database primitive
- **Class:** platform primitive
- **Why:** enforce `maxDownloads` without race overrun.
- **Invocation:** at the approved usage-consumption point.
- **Local policy:** when usage counts and when grant becomes `used`.
- **Do not build:** read-then-write `downloadCount++` helper.

### SH-072 / SH-074 — canonical hashing and secure token generation
- **Owner:** shared security capability
- **Class:** platform primitives
- **Why:** accepted-text/declaration hashes and optional grant secrets.
- **Invocation:** before storing hashes/token references.
- **Local policy:** canonical input and what hash/token proves.
- **Do not build:** `acceptanceHash.ts`, `downloadToken.ts`, custom crypto.

### SH-087 — `issueSignedMediaUrl`
- **Owner:** Media / File Access
- **Class:** canonical media capability
- **Why:** private object delivery after Digital Goods authorization.
- **Invocation:** final technical-delivery step of `issueDigitalDownloadAccess`.
- **Local policy:** Digital Goods grant/order/usage validity supplied to Media.
- **Expected result:** bounded signed URL + expiry/evidence reference.
- **Do not build:** R2/S3 presigner, permanent URL service.

### SH-088 / SH-089 — temporary grant mechanics and revocation
- **Owner:** shared grant mechanism / each grant owner
- **Class:** shared mechanism / separate truth
- **Why:** reuse issue/validate/expire/revoke mechanics while preserving DigitalDownloadGrant.
- **Invocation:** grant lifecycle commands.
- **Local policy:** Order basis, TTL, max downloads, status/event semantics.
- **Do not build:** universal AccessGrant table; do not reuse MediaAccessGrant or playback grants.

### SH-090 — `attachValidatedMedia`
- **Owner:** contextual owner + Media asset truth
- **Class:** shared contract / separate contextual truth
- **Why:** DigitalDownloadAsset and accessibility records may only reference ready validated Media.
- **Invocation:** asset registration/attachment.
- **Local policy:** digital business meaning and delivery role.
- **Do not build:** file safety validation or direct Media repository access.

### SH-091 — `requestSearchProjectionRefresh`
- **Owner:** Search / Public Visibility
- **Class:** another Module public interface
- **Why:** policy/readiness/moderation/control changes can affect public Offering readiness.
- **Invocation:** after committed relevant change/outbox.
- **Local policy:** why Digital Goods source fact changed.
- **Do not build:** Typesense client, SearchUpsertEvent writer.

### SH-095 / SH-096 / SH-097 — Privacy target protocol
- **Owner:** Privacy orchestrates; Digital Goods executes owner data
- **Class:** cross-cutting protocol
- **Why:** inventory, retention evaluation, erase/anonymize/revoke/retain execution.
- **Invocation:** Privacy-authorized workflow only.
- **Local policy:** Digital Goods data inventory and owner-specific disposition facts.
- **Do not build:** PrivacyRequest/DataErasureJob/retention-exemption lifecycle.

### SH-103 — `executeModerationDecision`
- **Owner:** Moderation decision; target owner execution
- **Class:** cross-cutting protocol
- **Why:** disable/restore assets and revoke grants without transferring legal decision truth.
- **Invocation:** verified Moderation command/event.
- **Local policy:** exact Digital Goods transition and cascade scope.
- **Do not build:** local DMCA/legal adjudication.

### SH-123 — `validateOwnedTargetReference`
- **Owner:** referenced target owner
- **Class:** shared cross-Module contract
- **Why:** Offering/Product/Course/Video relationships must be validated without repository access.
- **Invocation:** before creating/updating cross-owner relations.
- **Local policy:** which relation is valid for Digital Goods.
- **Do not build:** generic cross-domain Prisma lookup.

### SH-125 — `recordDomainAccessEvent`
- **Owner:** Digital Goods for `DigitalDownloadEvent`
- **Class:** shared append-only mechanism / separate truth
- **Why:** append digital-specific delivery evidence independently from generic audit.
- **Invocation:** URL issuance/denial, download outcome, grant expiry/revocation.
- **Local policy:** event type, relationships, provider/request details, safe metadata.
- **Do not build:** use `AuditEvent` as download ledger or merge with MediaAccessEvent.

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output / truth affected | Why local |
| --- | --- | --- | --- | --- |
| `selectEffectiveDigitalPolicy` | choose current applicable DigitalGoodsPolicy for Offering/action | Offering ID, time/context | policy or missing/stale result | policy meaning is Digital Goods domain logic |
| `validatePolicyVersionMatch` | reject stale acceptance submissions | displayed versions + current policy | allow/stale decision | contextual version safety |
| `evaluateDigitalDownloadEligibility` | compose local asset/grant rules around upstream decisions | actor, asset, Order decision, acceptance, hold facts | Digital Goods decision | only this Module knows grant/delivery rules |
| `deriveGrantTerms` | calculate TTL/max use from asset/policy | policy + asset | expiresAt/maxDownloads | Digital Goods delivery policy |
| `validateGrantAtAccessTime` | check state/time/actor/count/upstream entitlement | grant + current context | allow/deny | DigitalDownloadGrant semantics |
| `mapDigitalModerationAction` | map owner-authorized action to local asset/grant transitions | moderation envelope | transition plan | local execution semantics |
| `deriveMinorPrivacyControls` | map approved declaration to product-surface controls | declaration + approved policy | control projection | Digital Goods product-surface policy |
| `evaluateAccessibilityReadiness` | determine missing/ready/waived status for course surface | accessibility records + owner facts | readiness reasons | Digital Goods accessibility semantics |
| `buildDigitalDeliveryEvidence` | assemble safe acceptance/grant/event evidence | Order/asset/grant refs | evidence DTO | this Module owns those facts |
| `buildDigitalPrivacyInventory` | enumerate Module-held subject records | subject ID/cursor | Privacy target inventory | owner knows its records/relations |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Temporary grants:** use SH-088 mechanics, but retain `DigitalDownloadGrant` schema/status/repository/policy.
2. **Domain access evidence:** use SH-125 append-only conventions, but retain `DigitalDownloadEvent` as Digital Goods truth.
3. **Generic audit:** use SH-029/030 in addition to local evidence; never merge ledgers.
4. **State machine plumbing:** SH-053 may validate/apply transitions; the Digital Goods transition graph remains local.
5. **Idempotency:** SH-044 stores/replays command effects; Digital Goods defines semantic command identity.
6. **Counter concurrency:** SH-057 performs the atomic mechanism; Digital Goods defines when a download counts.
7. **Hashing/token generation:** shared cryptography provides algorithms; Digital Goods defines canonical content and purpose.
8. **Search projection:** SH-091 requests work; Search owns its queue/projection.
9. **Privacy:** SH-095–097 define protocol; Digital Goods owns only its executor/inventory facts.
10. **Moderation:** SH-103 carries an authoritative decision; Digital Goods owns target execution.
11. **Provider status:** no generic provider status is Digital Goods truth. Storage/provider details remain with Media.

---

## 18. Authentication and Authorization

### Authentication

All protected user/admin requests begin with SH-001. Background workers use a narrowly scoped system actor/request context. No client-supplied `userId` is trusted as actor identity.

### Authorization

SH-002 interprets permission. Digital Goods supplies/obtains minimum contextual facts:

- Offering ownership/management relationship;
- buyer/User/CustomerProfile relationship to the Order;
- whether admin/support action is allowed for the named resource/action;
- reviewer authority for child-directed/accessibility decisions.

### Resource ownership

- seller/admin policy/asset/declaration actions require Offering-owner facts through Marketplace public contracts;
- buyer access requires the authenticated User plus CustomerProfile/Order participant facts;
- a grant may never be used by merely knowing its ID/token if the actor binding fails.

### Admin/support actions

Platform role alone is insufficient. Admin/support action must include resource-action authorization and, where applicable, hold/moderation/privacy context. Generic support access does not imply permission to view sensitive download evidence or underlying files.

### Step-up

The exact CL-05 step-up matrix is unresolved. If root security policy later marks destructive access revocation, sensitive evidence reads, or privacy retries as high risk, use SH-014. Do not implement a Module-local MFA flag.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying owner | Query/interface | Digital Goods action gated | Local composition |
| --- | --- | --- | --- | --- |
| actor authentication | Identity | SH-001 | all protected actions | actor must be trusted |
| resource permission | Role / Authority | SH-002 | manage policy/assets/declarations/accessibility; use protected download | action/resource allow required |
| buyer identity | Customer Profile | SH-004 | purchased grant/listing | buyer context must match Order/access principal |
| Order entitlement | Transaction / Order | SH-025 | grant issue and current purchased access | qualifying item/participant/refund/dispute must allow action |
| digital terms proof | Consent + Digital Goods | SH-007/008 + local acceptance query | grant/access where required | approved version proof + contextual acceptance required |
| Media readiness | Media | SH-090/readiness + SH-087 | asset registration and signed delivery | asset must be safe/ready; Media signs |
| ComplianceHold | Hold owner | SH-011 | mapped grant/access/admin actions | applicable hold denies or triggers owner-local revocation/freeze |
| moderation/legal | Moderation | SH-103 | disable/restore/revoke | execute only authoritative action; do not adjudicate |
| plan entitlement | Track Entitlement | SH-005 conditional | only explicitly plan-gated digital perk | no effect unless concrete entitlement is defined |
| accessibility readiness | Digital Goods | local query | Marketplace/course readiness input | return facts/reasons; Marketplace decides publish state |
| child-directed controls | Digital Goods + approved legal policy | local declaration/control queries | product-surface behavior/readiness input | fail closed where approval criteria are unresolved |
| Privacy disposition | Privacy + owner facts | SH-095–097 | erase/anonymize/revoke/retain | owner executes; Privacy owns parent workflow/exemption |

---

## 20. Provider Integrations

### Normal MVP provider ownership

Digital Goods Access owns **no direct external provider client** for normal download delivery.

```text
Digital Goods access decision
→ SH-087 Media/File Access signed URL
→ Media provider adapter
→ Cloudflare R2 / approved object storage
```

The current Deep Module Registry lists R2/S3/presigned URL technology under Digital Goods, but the later CL-05 architecture is more specific and binding: Media owns storage/file mechanics and generic signed access.

### Prohibited provider clients here

- Cloudflare R2 / S3 client or presigner;
- Stripe Checkout or Stripe Tax;
- Avalara;
- Mux streaming/playback client;
- email/SMS/push provider.

### `DigitalStorageProvider`

The enum remains Digital Goods vocabulary on asset/event records, but it is not permission to instantiate provider SDKs. Treat it as normalized delivery/provider metadata supplied/verified through owner integration. If `external` storage is later enabled, its authorization/revocation/audit contract must be explicitly designed; it is not automatically supported by the current enum.

---

## 21. Events and Outbox

### Emission rules

Use SH-046 whenever another Module must react after a committed Digital Goods fact. The source transaction changes owner truth and writes the outbox atomically.

Events must include:

- event ID;
- event name/version;
- aggregate type/ID;
- aggregate/source version where available;
- occurredAt;
- request/correlation/causation IDs;
- actor type/ID when safe;
- minimal identifiers/reason codes;
- no signed URL, token, raw legal text, file bytes, or unnecessary PII.

### Consumer idempotency

Inbound Order/refund/moderation/etc. events use SH-045 and a consumer inbox identity. Duplicate delivery must produce one Digital Goods effect.

### Events are facts, not commands

`digital_goods.download_grant.revoked.v1` means the grant was revoked. A command such as “revoke all grants” remains a typed owner command/job request, not a domain event disguised as an imperative.

---

## 22. Background Jobs / Scheduled Work

### `expireDigitalDownloadGrants`

- **Purpose:** dispatch owner expiration for grants whose `expiresAt` passed.
- **Input:** cursor/time window.
- **Owner:** Digital Goods logic over SH-055 scheduler.
- **Idempotency key:** grant ID + expiration transition/version.
- **Retryable:** database transient/queue failure.
- **Permanent:** grant already terminal is idempotent success; invalid data is terminal/manual review.
- **Writes:** `DigitalDownloadGrant.status=expired`, event evidence.
- **Telemetry:** counts, lag, failures without user-agent/token leakage.

### `revokeDigitalDownloadGrants`

- **Purpose:** bulk owner-local revocation for asset/Order/moderation/privacy instruction.
- **Input:** source reference + target scope + reason.
- **Idempotency:** source decision/action ID + target scope.
- **Retry:** partial failures retry per grant/batch safely.
- **Writes:** grant transitions/events; optional downstream notifications.

### `reconcileDigitalDownloadEvidence`

- **Purpose:** optional support reconciliation where Media/provider evidence and Digital Goods access events need correlation.
- **Constraint:** must not treat provider logs as entitlement truth or rewrite immutable history.
- **Use:** only when a concrete production need exists; do not build speculative reconciliation before the delivery mechanism requires it.

### Privacy execution worker

Privacy-target execution may be queued through SH-047. Privacy remains parent workflow owner; Digital Goods reports typed per-target result.

---

## 23. Concurrency and Idempotency

### Races to prevent

- duplicate terms acceptance command;
- stale policy edits;
- duplicate grant issuance for the same semantic request;
- concurrent download requests exceeding `maxDownloads`;
- access racing grant revocation/expiry;
- moderation restore racing delete/archive;
- accessibility/declaration admin review racing seller edits;
- bulk revocation replay;
- Privacy executor replay.

### Lock / transaction rules

| Resource | Strategy |
| --- | --- |
| `DigitalGoodsPolicy` | optimistic concurrency with expected `updatedAt`/version; stale update returns conflict |
| `DigitalDownloadAsset` transition | SH-051 row/aggregate lock or compare-and-set transition |
| `DigitalDownloadGrant` access/use | database transaction + row lock/atomic counter; current time/state rechecked in transaction |
| grant issuance | SH-044 semantic idempotency; add DB uniqueness only after exact semantic uniqueness is approved |
| child declaration review | lock declaration row + stale version check |
| accessibility state | compare-and-set/owner transition |
| inbound events | SH-045 inbox dedupe |

### Replay result

A repeated idempotency key with the same fingerprint returns the original semantic result. Same key with a materially different fingerprint is an idempotency conflict.

### No in-memory locks

Distributed correctness must rely on Postgres/shared persistence primitives, not process memory.

---

## 24. Media / Storage

### Business attachment meaning owned here

- a DigitalDownloadAsset is a paid downloadable delivery object;
- a CourseAccessibilityAsset gives a Media file accessibility meaning.

### File mechanics owned by Media

Digital Goods never performs:

- upload policy evaluation;
- MIME/binary validation;
- malware scan;
- EXIF/PDF metadata scrub;
- bucket/object-key selection;
- object upload/delete;
- generic signed URL generation.

### Upload context

The backing Media asset must have an approved upload context suitable for `digital_download_file` or the relevant course accessibility asset context as defined by Media policy. The exact technical file-policy lookup remains Media-owned.

### Signed access

`issueDigitalDownloadAccess` authorizes the business action, then invokes SH-087. Media re-checks its own readiness/freeze/erasure conditions before signing.

### Sensitive access logging

`DigitalDownloadEvent` records the digital-domain action. SH-030 adds generic `AccessAuditLog` where the audit matrix requires it. Media may also append `MediaAccessEvent`; these records are intentionally separate.

---

## 25. Search / Projection

Digital Goods owns no search index.

Search-relevant source changes may include:

- required digital policy becoming missing/invalid;
- DigitalDownloadAsset readiness/disable/restore;
- child-directed control/readiness changes;
- required accessibility readiness changes.

Digital Goods calls SH-091 with entity ID, action/reason, source version, requester Module, and idempotency key. Search composes this request with Marketplace/source public-readiness rules.

Search must not reconstruct Digital Goods policy by reading its tables directly.

---

## 26. Notification

Digital Goods owns the business trigger meaning, not delivery.

Possible approved triggers:

- material policy/version change requiring user action;
- grant revoked for a user-relevant reason;
- access restored;
- child-directed/admin review outcome;
- accessibility review outcome.

Every notification request uses SH-041 and contains safe variables only. Never send signed URLs, tokens, provider object keys, legal text blobs, IP hashes, or sensitive moderation details in notification payloads.

A Notification failure never rolls back an already committed access revocation or source transition.

---

## 27. Audit and Sensitive Access

### Domain truth

`DigitalDownloadEvent` records digital delivery/access facts.

### Generic AuditEvent

Use SH-029 for important administrative/policy/moderation/privacy actions when the global audit policy requires it.

### Sensitive access

Use SH-030 for issuance/denial/download of protected credentials/data according to the approved access-audit matrix.

### Separation rule

```text
DigitalDownloadEvent = what happened in digital delivery
AccessAuditLog       = protected-access evidence across the platform
AuditEvent           = important actor/system action evidence
IntegrationFailure   = operational failure evidence
```

None substitutes for another.

---

## 28. Privacy and Retention

### Subject-data inventory

Digital Goods may hold subject-linked data in:

- `DigitalGoodsTermsAcceptance`;
- `DigitalDownloadAsset.createdByUserId`;
- `DigitalDownloadGrant`;
- `DigitalDownloadEvent`;
- child-directed declaration/reviewer IDs;
- `CourseAccessibilityAsset` uploader/reviewer IDs;
- IP hash/user-agent evidence;
- related safe provider/request references.

### Privacy executor

Implement SH-096 inventory, SH-097 retention facts, and SH-095 execution.

Possible dispositions by record include:

- revoke access;
- anonymize actor/request metadata where permitted;
- detach optional personal references where relational/legal rules permit;
- delete owner record when not retention-locked;
- retain minimum evidence when Privacy records an approved exemption;
- request Media/provider deletion through the owning Module rather than directly.

### Product deletion vs privacy erasure

`DigitalDownloadAsset.deletedAt` is product lifecycle deletion. It is not legal erasure. Privacy execution is separate.

### Retention-sensitive records

At minimum, evaluate retention for:

- accepted policy/version evidence;
- grant issuance/use/revocation evidence tied to a transaction;
- download events supporting refund/dispute/fraud/security proof;
- moderation/legal execution evidence.

### Cascade warning

The current Prisma relations can cascade Offering → Digital Goods policy/assets and DigitalDownloadAsset → grants/events. Before production deletion is enabled, migration review must prove that ordinary product deletion cannot erase retention-required transaction/consent/access evidence. This is a production blocker, not permission to invent a new retention schema in this Module.

---

## 29. Observability

### Required safe dimensions

Examples:

- operation name;
- asset/grant ID or one-way safe reference;
- status/reason code;
- provider enum when non-sensitive;
- latency/duration;
- retry count;
- queue age;
- request/correlation ID;
- success/denial/failure class.

### Forbidden telemetry

Never log:

- raw signed URLs;
- raw grant tokens;
- file bytes/object keys unless explicitly safe and access-controlled;
- raw legal/consent text;
- full IP/user-agent where minimized/hash form is sufficient;
- private moderation details;
- payment/tax data;
- unnecessary buyer identity.

### Operational records

- use SH-037 for normalized integration failure;
- use shared queue telemetry for workers;
- health checks may report delayed/unavailable dependencies but may not alter grant/asset truth.

---

## 30. Security Boundaries

1. Validate every command/query input server-side.
2. Actor identity comes only from SH-001/system credential, never client `userId`.
3. Authorization is server-side through SH-002 and owner facts.
4. Order entitlement is server-side through SH-025.
5. Never expose permanent public file URLs.
6. Signed URLs are short-lived and are never durable source truth.
7. Store only token/URL hashes when durable credential evidence is needed.
8. Use SH-072/074; do not implement custom cryptography.
9. Grant expiry is validated against server time on every access request.
10. Current asset and required upstream entitlement are revalidated so a stale grant cannot bypass refund/moderation/hold changes.
11. Download limits are transactionally atomic.
12. Media performs safety checks and signing; Digital Goods cannot bypass Media because an asset was previously ready.
13. Telemetry/audit payloads are minimized and sanitized.
14. Bulk moderation/privacy/destructive actions require typed source references and idempotency.
15. Rate limits/abuse controls for access endpoints use shared platform mechanisms when specified by root architecture.
16. `external` storage mode is disabled until an explicit authorization/revocation/audit contract is approved.

---

## 31. Error / Decision Result Pattern

Public interfaces return stable Workin Ants result categories, not raw provider exceptions.

```ts
// Illustrative contract shape, not implementation code.
type DigitalGoodsResult<T> =
  | { ok: true; value: T; evidenceRefs?: string[]; evaluatedAt?: string }
  | {
      ok: false;
      category:
        | 'validation'
        | 'unauthenticated'
        | 'forbidden'
        | 'not_found'
        | 'conflict'
        | 'policy_required'
        | 'entitlement_denied'
        | 'hold_blocked'
        | 'access_denied'
        | 'temporary_failure'
        | 'manual_review_required'
        | 'unsupported';
      reasonCode: string;
      retryable: boolean;
      remediation?: string;
      evidenceRefs?: string[];
    };
```

Rules:

- `temporary_failure` never exposes R2/S3/provider internals to a buyer;
- business denials are not retried as technical failures;
- stale writes return `conflict` with a safe current-version reference;
- legal-gated missing policy returns `policy_required`/manual-review rather than a guessed allow;
- unsupported null-Order access returns `unsupported_access_basis`.

---

## 32. Testing Architecture

### Domain unit tests

- policy version selection/stale submission;
- policy TTL/max-use derivation;
- asset transition graph;
- grant transition graph and server-time expiry;
- finite/unlimited download usage semantics;
- moderation-action mapping;
- child-control derivation using approved test policy;
- accessibility readiness.

### State-transition tests

Every lifecycle owner command tests valid and invalid transitions, reopen/reissue behavior, terminal states, and stale writes.

### Public contract tests

- Marketplace target validation;
- Order entitlement allow/deny/refund/dispute states;
- Consent proof/version lookup;
- Media ready/attach/sign allow/failure;
- Video target facts for accessibility;
- Moderation execution envelope;
- Search/Notification/Audit/Privacy requests.

### Database/integration tests

- policy one-per-Offering constraint;
- immutable acceptance insert/history;
- grant expiry/index queries;
- transactionality of usage count + event;
- retention-safe deletion behavior after migration decision;
- idempotent command replay.

### Authorization tests

- seller manages own Offering policy/assets only;
- buyer uses only own qualifying Order/grant;
- admin/support action requires explicit action authorization;
- wrong actor cannot use grant ID/token;
- no direct provider route bypass.

### Compliance/legal-gate tests

- missing approved policy blocks production activation;
- ConsentLog alone does not grant download;
- child-directed uncertain case cannot auto-approve;
- waiver cannot be applied without approved authority/criteria.

### Concurrency/idempotency tests

- parallel access cannot exceed `maxDownloads`;
- revoke vs access deterministic;
- expiry vs access deterministic;
- duplicate grant issue gives one semantic result;
- duplicate inbound refund/moderation event produces one effect.

### Privacy tests

- subject inventory completeness;
- erase vs anonymize vs retain result;
- retained evidence only when Privacy exemption exists;
- product deletion distinct from privacy erasure;
- no local PrivacyRequest/DataErasureJob created.

### Provider/Media integration tests

Digital Goods has no direct provider adapter tests. It tests the Media public contract and verifies no raw provider type/client leaks into Digital Goods.

### E2E participation tests

- seller configures digital policy → buyer accepts approved version;
- eligible Order → grant → signed download;
- wrong/non-entitled/refunded buyer denied;
- grant exhausted/expired/revoked denied;
- moderation disables access and stale path cannot bypass;
- child declaration/control/readiness flow under test policy;
- course accessibility record attached to ready Media and exposed to course consumer;
- Privacy target execution.

---

## 33. Module Invariants — Rules Coding Agents Must Never Violate

1. `Order` remains normal purchased-entitlement truth; Digital Goods never infers payment from Stripe/provider state.
2. `MediaAsset` remains file/safety/storage truth; Digital Goods never directly validates/scans/signs objects.
3. `DigitalDownloadAsset` is not access authorization by itself.
4. `ProductDetails.fileAssetId` or any file reference alone never grants access.
5. A normal purchased `DigitalDownloadGrant` requires an allowed SH-025 Order decision.
6. Null-Order grants are unsupported until an alternate access-basis architecture is approved.
7. Every access request validates grant status, `expiresAt`, actor binding, asset state, usage limit, and required current upstream entitlement.
8. No permanent public URL is stored or returned for paid/private digital files.
9. Raw grant tokens/signed URLs are never persisted in logs, audit metadata, events, notifications, or domain tables.
10. Download allowance is consumed atomically in the database.
11. Expiration worker lag cannot extend actual access validity.
12. Revoked/expired/used grants are never reopened; issue a new authorized grant.
13. `DigitalDownloadEvent` is append-only and separate from `MediaAccessEvent`, `AccessAuditLog`, and `AuditEvent`.
14. Historical `DigitalGoodsTermsAcceptance` rows are immutable and version-specific.
15. `ConsentLog` remains Consent & Disclosure truth and does not replace DigitalGoodsTermsAcceptance.
16. Agreement/e-sign consent remains distinct from digital product terms acceptance.
17. Digital Goods does not own or fork `ConsentType`.
18. Digital Goods does not own Offering/Product/Course lifecycle.
19. Digital Goods does not own DMCA/legal/moderation adjudication; it executes SH-103 decisions only.
20. Digital Goods does not create generic local `blocked`/hold state; it consumes SH-011.
21. Child-directed declaration does not establish a User’s age.
22. `MinorPrivacyControl` is a derived product-surface control, not general Privacy truth.
23. `CourseAccessibilityAsset` meaning remains separate from `MediaAsset` bytes and `CourseVideoAsset` provider state.
24. No R2/S3, Stripe/Avalara, Mux, email/SMS/push client is instantiated in this Module.
25. Search updates use SH-091; no direct Typesense/SearchUpsertEvent write.
26. Privacy request/job/exemption lifecycles remain Privacy-owned.
27. Retention-required evidence must not disappear because an Offering or asset was product-deleted.
28. Cross-Module facts are obtained through public interfaces/events, not direct foreign repositories by convenience.
29. Every retried mutation/provider-adjacent effect is idempotent.
30. Observability/audit data is minimized and never replaces source truth.
31. Legally gated production behavior fails closed rather than inventing terms, child criteria, waiver criteria, or consent keys.
32. Shared grant/state/crypto/queue mechanics may be reused, but Digital Goods retains its own records and policy.

---

## 34. Prohibited Duplicate Implementations

Do not generate the following inside `digital_goods_access`:

- `digitalGoodsAuth.ts`, `downloadAuth.ts`, `currentUser.ts`;
- `digitalGoodsPermissions.ts`, `sellerGuard.ts`, `isAdmin.ts`;
- `buyerResolver.ts` / duplicate CustomerProfile resolver;
- `isOrderPaid.ts`, `checkPurchase.ts`, Stripe checkout-status reader;
- `premiumDigital.ts`, `hasDigitalAccess.ts`, local plan/entitlement flags;
- generic `consentService.ts`, local ConsentLog, local ConsentType enum/version catalog;
- `r2Service.ts`, `s3Service.ts`, `presignedUrlService.ts`, `downloadUrl.ts`;
- file MIME validator, malware scanner, EXIF/PDF scrubber, private object-key generator;
- Mux/course playback provider adapter;
- generic `AccessGrant`, `TemporaryGrant`, or shared-grant repository replacing `DigitalDownloadGrant`;
- `auditService.ts`, local AccessAuditLog writer, local generic event log;
- `downloadQueue.ts`, custom retry/dead-letter/cron framework;
- custom crypto/hash/token helpers;
- local `PrivacyRequest`, erasure job, retention flag/table;
- local moderation/DMCA queue or adjudication service;
- local Typesense client/indexer/SearchUpsertEvent writer;
- direct email/SMS/push provider calls;
- a universal provider-status mapper;
- in-memory mutexes for grant use/revocation;
- direct cross-domain repositories for Offering, Order, Media, Consent, Search, Privacy, or Moderation.

---

## 35. Unresolved Decisions

These issues must remain visible. Coding agents must not settle them silently.

### 35.1 Exact legal policy content and jurisdiction behavior

Approved license/refund/immediate-access text, policy versions, jurisdiction-specific behavior, and production activation criteria are not supplied. Test policy/version data may exercise mechanics; production legal-gated behavior remains disabled until approved.

### 35.2 Meaning of “final after access”

`DigitalGoodsRefundPolicyType.final_after_access` exists, but the authoritative evidence does not define whether “access” means terms acceptance, signed URL issuance, download start, completed download, or another event. This also affects when download allowance counts and which evidence Review/Dispute may use. **Do not invent the production threshold.**

### 35.3 `DigitalDownloadGrantStatus.used`

This architecture proposes “finite allowance exhausted” semantics. Confirm before production if product design intends one-time-first-use semantics instead.

### 35.4 Approved null-Order access bases

Schema allows `orderId=null`, but complimentary/admin/library/organization access bases are not defined. Normal purchased delivery is unaffected; alternate access stays out of scope.

### 35.5 Digital-goods consent key mapping

Consent & Disclosure owns the vocabulary, but the exact digital-specific `ConsentType` mapping to policy/license/refund/immediate-access flows remains unresolved. Do not reuse Agreement/e-sign keys by convenience.

### 35.6 Child-directed review/current-declaration rules

Exact criteria for `admin_review_required`, `approved`, `rejected`, `disabled`, the effective-declaration selection rule, and downstream control activation remain legal-gated.

### 35.7 Accessibility waiver policy

Who may set `waived`, required evidence/reason, duration, and publication effect are not approved. Production waiver behavior fails closed.

### 35.8 Retention-safe cascade behavior

Current schema cascade paths may erase policy/assets/grants/events when an Offering/asset is deleted. Before production deletion, decide and migrate the retention-safe behavior consistent with Privacy/transaction/legal obligations.

### 35.9 Immutable legal text source

`DigitalGoodsPolicy` stores version identifiers, not an immutable text body. Confirm that the Consent/version catalog or another approved source can reproduce the exact accepted license/refund/immediate-access content. If not, add an explicit immutable snapshot through architecture decision.

### 35.10 CustomerProfile persistence on Digital Goods records

Current schema stores `userId` rather than `customerProfileId`. This document proposes User as access principal plus CustomerProfile/Order as commercial buyer context. A schema change requires explicit root/Cluster decision.

### 35.11 Step-up action matrix

The exact Digital Goods admin/destructive operations requiring SH-014 are not defined by CL-05.

### 35.12 External storage provider mode

`DigitalStorageProvider.external` exists, but the authorization, revocation, audit, privacy, and availability contract is not defined. Disable it for MVP unless separately approved.

---

## 36. Architecture Decision Summary

### Binding rulings

- Digital Goods Access owns `DigitalGoodsPolicy`, `DigitalGoodsTermsAcceptance`, `DigitalDownloadAsset`, `DigitalDownloadGrant`, `DigitalDownloadEvent`, `ChildDirectedContentDeclaration`, `MinorPrivacyControl`, `CourseAccessibilityAsset`, and their Digital Goods-specific enum/lifecycle semantics.
- Consent & Disclosure owns `ConsentType`, active consent versions, and `ConsentLog`.
- Marketplace Supply owns Offering/Product/Course business lifecycle.
- Transaction / Order owns normal purchase entitlement, payment/refund/dispute transaction truth.
- Media / File Access owns file safety, storage, and signed-object access. Digital Goods must call SH-087 rather than sign R2/S3 URLs.
- Video Session owns Mux/course-video provider state and playback grants.
- Digital Goods temporary grants remain separate from every other temporary-grant record.
- DigitalDownloadEvent remains separate from generic audit and Media access evidence.
- Normal purchased access requires SH-025 and revalidation at access time where required.
- Search, Notification, Audit, Moderation, Privacy, and Observability are consumed only through their public/shared interfaces.
- Production legal-gated decisions fail closed when exact legal policy is unresolved.
- The Module implementation sequence is subordinate to CL-05 Features 03, 04, 05, 13, 14, and 15 and depends on CL-05 Media Features 01–02.

### Proposed rulings requiring confirmation before production where noted

- `DigitalDownloadGrantStatus.used` means finite allowance exhausted.
- `User` remains the access principal while CustomerProfile/Order supplies buyer commercial context until root architecture says otherwise.
- `DigitalDownloadAsset` file/provider fields are delivery snapshots, never current Media truth.

---

## 37. Coding-Agent Usage

Before implementing a Digital Goods feature, the coding agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md` if present/current;
3. root `code-standards.md`;
4. `context/shared/shared-operations.md`;
5. CL-05 `architecture.md`;
6. CL-05 `build-plan.md`;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. public-interface sections for Marketplace Supply, Transaction / Order, Media / File Access, Consent & Disclosure, Video Session, Moderation, Privacy, Audit, Search, Notification, and Hold as required by the numbered feature;
10. `progress-tracker.md` and the most recent feature completion report.

Before coding, the agent must also check the unresolved-decision list above. If a feature reaches a blocked legal/architecture decision, implement only the already-approved mechanism/contract, record the block, and do not invent policy.
