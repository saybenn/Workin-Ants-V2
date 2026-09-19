# Digital Goods Access Implementation Plan

> **Module ID:** `digital_goods_access`  
> **Module:** Digital Goods Access Module  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Companion architecture:** `module-architecture.md` in this Module context  
> **Cluster sequencing authority:** CL-05 `build-plan.md`  
> **Implementation posture:** greenfield/MVP planning against current Prisma and architecture evidence; legal-gated production behavior stays disabled until its named policy decisions are approved.

This plan is narrower than the CL-05 build plan. It defines exactly what is built **inside Digital Goods Access**, which neighboring public interfaces are consumed, and which responsibilities must never be copied locally.

It does not independently change CL-05 sequencing. Module features below are mapped to the Cluster features they support.

---

## Core Principle

Implement Digital Goods Access through narrow, verifiable owner slices:

```text
public / observable digital-goods behavior
→ validated Module command or query
→ Digital Goods-owned policy
→ authoritative Digital Goods write/read
→ canonical SH operations and neighboring public interfaces
→ domain access/event proof
→ downstream audit/search/notification/privacy effects
→ tests
→ exit gate
```

A feature may expose UI where CL-05 already establishes a genuine Digital Goods surface, such as policy configuration, buyer terms acceptance, purchased downloads, child-directed declarations, or accessibility tracking. Do not invent unrelated UI merely to make an internal capability visible.

No feature may make R2/S3, Stripe, Mux, ConsentLog, Order, Search, Audit, or Privacy truth local to Digital Goods.

---

## Build Rules

1. Follow root architecture/standards, CL-05 architecture/build plan, the Canonical Shared Operations Registry, and `module-architecture.md`.
2. Digital Goods owns only the records and policy declared in Module architecture.
3. Consume adjacent truth through public interfaces/events; direct cross-domain Prisma access is not the default.
4. Reuse SH-### operations. If a canonical operation is not implemented, use its contract/test fake or coordinate implementation in its canonical owner; do not create a Module-local substitute.
5. Every mutation is runtime-validated, actor-resolved where applicable, server-authorized, and idempotent where retries are possible.
6. Every lifecycle transition is performed through Digital Goods owner policy in a transaction-safe way.
7. Order remains normal purchased-entitlement truth. Never read Stripe/provider state as delivery entitlement.
8. Media owns file safety/storage/signed URL mechanics. Digital Goods must not instantiate R2/S3 clients or presign URLs.
9. Consent & Disclosure owns generic consent/version proof and its disclosure text. Digital Goods owns contextual digital-goods terms and acceptance evidence; their historical-text persistence/retrieval mechanism remains unresolved.
10. Temporary grant mechanics may be shared, but `DigitalDownloadGrant` must not merge with Media, Video, Agreement, or security grants.
11. Download usage limits are database-atomic; in-memory locks and read-then-write counters are prohibited.
12. Time-bound access checks server time at request time; expiration-worker delay never extends access.
13. External enforcement facts such as refunds, moderation actions, holds, and Privacy dispositions are authenticated/versioned/deduplicated and mapped to local transitions.
14. Search and Notification are downstream interfaces. Their failure never rolls back already committed Digital Goods truth unless root architecture explicitly says otherwise.
15. Domain event/access evidence, generic audit, and observability remain separate.
16. Privacy orchestration remains Privacy-owned; this Module implements only inventory/retention facts/execution against owner records.
17. Legal-gated rules fail closed. Do not invent license/refund text, child-directed review criteria, accessibility waiver criteria, or consent-key mapping.
18. Every numbered feature ends with automated tests, workflow/contract verification, documentation/progress update, and an explicit exit gate.
19. Do not begin the next feature until the current exit gate passes or progress context records an approved exception.
20. If implementation reveals a binding architectural conflict, stop that disputed sub-scope, update architecture through an explicit decision, then continue.

---

## Preconditions

### Hard platform dependencies

These must exist as production interfaces or stable contract fakes before the relevant feature can pass its exit gate:

- Prisma/PostgreSQL migration/transaction support;
- SH-001 authenticated actor;
- SH-002 resource authorization;
- runtime validation and root request context;
- SH-044 idempotent command framework;
- SH-046 transactional outbox where cross-Module reaction is required;
- SH-047/048 durable queue/retry framework;
- SH-029/030 Audit interfaces;
- SH-032/034/037 Observability interfaces;
- shared cryptography SH-072/074;
- database concurrency primitives SH-051/052/057.

If the platform implementation is not yet present, tests may use contract fakes that exactly match the canonical SH interface. Digital Goods must not temporarily become the platform owner.

### Hard neighboring dependencies by Cluster sequence

**Before Module Feature 03/04/05 paid delivery can be complete:**

- CL-05 Feature 01: Media can produce a safe `MediaAsset.ready`;
- CL-05 Feature 02: Media exposes composite `requestMediaAccess`, invoking SH-087 internally and returning a short-lived credential or typed denial; no second public signing call;
- Marketplace Supply exposes Offering/Product/Course owner validation/facts;
- Transaction / Order exposes SH-025 `authorizeOrderEntitlement`;
- Consent & Disclosure exposes required proof/version interfaces.

**Before moderation/invalidation bridge:**

- Moderation exposes SH-103 command/envelope;
- Hold exposes SH-011;
- Search exposes SH-091;
- Notification exposes SH-041;
- platform event inbox supports SH-045.

**Before Privacy phase:**

- Privacy protocol SH-095–097 is available;
- applicable retention-owner facts are available;
- Media can execute its own provider/object privacy effects.

### Dependencies that may initially be stubbed

- Search refresh;
- Notification request;
- Audit/Observability transports;
- Moderation and Privacy owner interfaces;
- Video owner-facts query for accessibility linkage;
- Track entitlement interface, because no concrete Digital Goods plan perk is currently required for normal purchased access.

### Legal/policy preconditions

The following are **not** required to build schema/contracts/test-policy mechanics, but are required before the associated production behavior can be enabled:

- approved digital license/refund/immediate-access content and version mapping;
- exact `final_after_access` threshold;
- child-directed review/effective-declaration criteria;
- accessibility waiver authority/criteria;
- final digital-goods ConsentType mapping;
- approved null-Order alternate access bases;
- retention-safe deletion/cascade decision;
- final sensitive-action step-up matrix.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Module Contracts, Schema Guardrails, and Ownership Enforcement

### Objective

Establish the Digital Goods Module boundary in code and tests before implementing user workflows, with repositories restricted to Module-owned records and public contracts defined for all required neighbors.

### Observable Result

The repository has a compile-time/test-enforced `digital-goods-access` Module boundary with:

- owned record repositories and transition contracts;
- public command/query DTOs;
- dependency ports for Marketplace, Order, Consent, Media, Video, Hold, Audit, Search, Notification, Moderation, and Privacy;
- stable Digital Goods decision/error reason vocabulary;
- schema/constraint review documenting current risks and migrations required before later features.

No real buyer download flow is enabled yet.

### Cluster Build-Plan Link

Supports **CL-05 Feature 03 — Digital Goods Policy and Versioned Terms Evidence** and establishes prerequisites for CL-05 Features 04–05, 13–15.

### Dependencies

- root module/folder convention;
- current Prisma schema;
- Canonical Shared Operations Registry;
- Module architecture;
- CL-05 architecture/build plan.

### In Scope

- create Module folder boundaries following root convention;
- define public contracts and internal domain types;
- create Digital Goods repositories for owned models only;
- define owner transition policy interfaces;
- define stable reason codes/result pattern;
- implement dependency-port test doubles/contracts;
- inspect current schema indexes, cascades, and uniqueness gaps;
- establish architecture tests/lint rules preventing forbidden provider/cross-domain imports;
- document unresolved migration decisions instead of silently changing schema.

### Out of Scope

- real policy UI;
- buyer terms acceptance;
- grant issuance;
- signed download access;
- child-directed production policy;
- accessibility workflow;
- provider clients;
- cross-Module event handling.

### Module-Owned Data

No behavior-changing migration is required solely to create structure. Repositories cover:

- `DigitalGoodsPolicy`;
- `DigitalGoodsTermsAcceptance`;
- `DigitalDownloadAsset`;
- `DigitalDownloadGrant`;
- `DigitalDownloadEvent`;
- `ChildDirectedContentDeclaration`;
- `MinorPrivacyControl`;
- `CourseAccessibilityAsset`.

Review and record:

- Offering/asset cascade risks;
- absence of explicit command idempotency columns (canonical SH-044 should cover this);
- token-hash uniqueness requirement if token lookup is later enabled;
- no current effective-declaration uniqueness rule;
- targetType free-string risk on MinorPrivacyControl;
- indexes for expiry/event evidence.

### Public Interfaces

Introduce stable TypeScript contracts for:

**Commands:**

- `upsertDigitalGoodsPolicy`;
- `recordDigitalGoodsTermsAcceptance`;
- `registerDigitalDownloadAsset`;
- `issueDigitalDownloadGrant`;
- `issueDigitalDownloadAccess`;
- `revokeDigitalDownloadGrant`;
- `applyDigitalModerationDecision`;
- child/accessibility commands;
- Privacy executor contracts.

**Queries:**

- policy;
- acceptance evidence;
- download readiness;
- download eligibility;
- Digital Goods-owned SH-026 `authorizeContextualResourceAccess` playback/file decision (allow/deny, safe reason, applicable policy/acceptance evidence, freshness/expiry, delivery constraints);
- buyer downloads;
- delivery evidence;
- privacy controls;
- accessibility readiness.

Only contracts/fakes are required in this feature.

### Shared Operations Used

- **SH-001 / SH-002:** dependency contract definitions; no local auth/RBAC helper.
- **SH-025:** Order entitlement port.
- **SH-044:** command idempotency contract.
- **SH-046 / SH-047:** outbox/job contracts.
- **SH-051 / SH-052 / SH-053 / SH-057:** transition/concurrency contracts.
- **SH-087:** Media-internal signing behind `requestMediaAccess`; **SH-090:** Digital Goods/contextual-owner attachment using Media readiness.
- **SH-095–097:** Privacy protocol types.
- **SH-103:** Moderation execution envelope.
- **SH-123:** owner target validation contract.
- **SH-125:** domain access event append contract.

**Prohibited duplicates:** local auth, RBAC, idempotency, queue, lock, Media signing, Privacy workflow, Moderation decision engine.

### Domain Logic

- codify the ownership/non-ownership rules from Module architecture;
- define lifecycle transition tables without implementing every command;
- define safe error categories and reason codes;
- prohibit direct provider status/errors in public DTOs;
- define the normal purchased-access basis as Order-backed and mark null-Order basis unsupported.

### Authorization / Compliance

- all future protected commands require actor/authority contracts;
- policy and legal-gated commands include `policy_not_production_approved`/`manual_review_required` result capability;
- no generic ConsentType is declared inside the Module.

### Database / Transaction Behavior

- no destructive cascade change without an approved migration decision;
- repository tests prove only Module-owned Prisma models are imported by owner repositories;
- define transaction seams for policy update, acceptance insert, grant issuance, usage/event append, and revocation.

### Events / Jobs

Define event envelope and planned v1 event names from Module architecture. No production event handler required yet.

### Provider Integration

None. Add an import-boundary test proving no `@aws-sdk/*`, R2, Stripe, Avalara, Mux, email/SMS/push SDK is imported by Digital Goods.

### UI / Admin Surface

None.

### Failure Behavior

- invalid architecture import fails test/build;
- unresolved schema/legal decision is recorded and remains blocked;
- missing dependency implementation uses explicit test fake in non-production test context, never silent fallback.

### Tests

- module boundary/import tests;
- contract type tests;
- repository ownership tests;
- lifecycle table unit tests;
- stable reason-code tests;
- Prisma schema smoke tests/index introspection where feasible;
- test proving no local ConsentType/provider/auth/queue implementation.

### Documentation Updates

- record any newly discovered schema mismatch in Module architecture unresolved section;
- update progress tracker with dependency availability;
- no shared-operation registry change unless a genuinely missing canonical operation is discovered.

### Acceptance Criteria

- Digital Goods code cannot directly import neighboring repositories/provider SDKs;
- public contracts compile and can be faked independently;
- owned records have one repository/service owner path;
- normal purchased access is explicitly Order-based;
- legal/unresolved issues are represented as blockers, not assumptions;
- no new source-of-truth table is invented.

### Exit Gate

Pass:

- typecheck;
- lint/architecture-boundary tests;
- unit tests for transition/reason contracts;
- Prisma validation/migration inspection;
- manual review of prohibited imports and ownership map.

Do not begin Feature 02 until the boundary test suite passes.

---

## 02 Digital Goods Policy and Versioned Terms Evidence

### Objective

Implement the Digital Goods policy and contextual acceptance slice so a valid digital Offering can carry versioned license/refund/access policy and preserve immutable buyer acceptance evidence.

### Observable Result

Using approved test policy content:

- an authorized seller/admin can create/update the current `DigitalGoodsPolicy`;
- a buyer can retrieve the applicable policy/version presentation context;
- a buyer can accept the exact displayed version;
- `DigitalGoodsTermsAcceptance` preserves versions/hash/context;
- stale version submission is rejected;
- historical acceptance does not change when the current policy changes.

Production legal text remains feature-gated until approved.

### Cluster Build-Plan Link

Directly implements the Digital Goods-owned portion of **CL-05 Feature 03**.

### Dependencies

- Feature 01;
- Marketplace target/owner facts through SH-123;
- SH-001/002;
- Consent SH-007/008 and SH-009 if active-version catalog is used;
- SH-044 idempotency;
- SH-072 hashing;
- approved test policy/version fixtures.

### In Scope

- `upsertDigitalGoodsPolicy`;
- `getDigitalGoodsPolicy`;
- policy validation and stale-write protection;
- version-specific buyer disclosure DTO;
- `recordDigitalGoodsTermsAcceptance`;
- `getDigitalGoodsTermsAcceptance` / evidence query;
- immutable historical acceptance behavior;
- production legal gate;
- seller/admin policy form and buyer terms-acceptance surface if root UI structure is ready.

### Out of Scope

- download asset/grant/access;
- refund adjudication;
- sales-tax calculation;
- Agreement signature/e-sign lifecycle;
- child-directed approval criteria;
- actual legal drafting.

### Module-Owned Data

- `DigitalGoodsPolicy`;
- `DigitalGoodsTermsAcceptance`;
- Digital Goods license/refund/acceptance enums.

### Public Interfaces

Implement Digital Goods-owned SH-026 `authorizeContextualResourceAccess` for course playback using the Module’s existing policy/acceptance rules. Return allow/deny, safe reason, applicable evidence references, freshness/expiry where applicable, and owner-defined playback constraints. Video consumes this alongside SH-025 and its own readiness/authority/healthcare/hold gates; no Video-side policy-row interpretation is permitted. Production legal-content policy remains gated as described below.

Implement:

- `upsertDigitalGoodsPolicy`;
- `getDigitalGoodsPolicy`;
- `buildDigitalPolicyPresentation` as an application/query helper if needed;
- `recordDigitalGoodsTermsAcceptance`;
- `getDigitalGoodsTermsAcceptance`;
- `getDigitalGoodsTermsEvidence`.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor`** — seller/buyer actor.
- **SH-002 `authorizeResourceAction`** — Offering policy management.
- **SH-004 `resolveCustomerActor`** — buyer context where required.
- **SH-007/008 `recordConsentProof` / `queryConsentProof`** — generic proof where approved mapping requires it.
- **SH-009 `resolveActiveConsentVersion`** — only if the Digital Goods disclosure uses the canonical Consent version catalog.
- **SH-044 `executeIdempotentCommand`** — acceptance and policy mutation retry safety.
- **SH-052 `withOptimisticConcurrency`** — stale policy edits.
- **SH-072 `hashCanonicalPayload`** — accepted/presented content hash.
- **SH-123 `validateOwnedTargetReference`** — validate Offering and ownership facts.
- **SH-029 `appendAuditEvent`** — material admin policy changes where required.

**Local policy:** which policy/version applies, which contextual evidence Digital Goods stores, and whether the generic proof is sufficient for this digital action.

**Prohibited duplicates:** consent tables/version catalog, hash helper, Offering repository, permission engine.

### Domain Logic

1. Resolve actor and authorize policy management/acceptance action.
2. Validate Offering kind/context through Marketplace owner interface.
3. Validate TTL values and policy enum combinations.
4. Use optimistic concurrency for policy updates.
5. For presentation, resolve the approved current legal/disclosure versions; production fails closed if approval is absent.
6. Hash the canonical presented content/policy snapshot.
7. On acceptance, re-resolve current applicable versions and reject stale display submissions.
8. Record generic Consent proof only where the approved mapping requires it.
9. Insert a new `DigitalGoodsTermsAcceptance`; never overwrite older evidence.
10. A revoked/voided acceptance is not reactivated; a new acceptance row is created after re-presentation.

### Authorization / Compliance

- seller policy management requires resource authorization;
- buyer acceptance must match authenticated User and relevant Order/Offering context if Order already exists;
- ConsentLog alone is never access permission;
- Agreement/e-sign consent remains out of scope;
- unapproved production text/version returns `digital_policy_not_production_approved`.

### Database / Transaction Behavior

- one current policy per Offering enforced by existing unique `offeringId`;
- policy update uses expected `updatedAt`/version check;
- acceptance insert and any same-workflow Digital Goods owner event/outbox write are transactional;
- same idempotency key/fingerprint replays the acceptance result;
- multiple legitimate acceptance rows across versions/Orders are allowed.

### Events / Jobs

Emit only if consumers require them:

- `digital_goods.policy.updated.v1` after committed policy change;
- `digital_goods.terms.accepted.v1` after committed acceptance;
- revocation event after explicit future revocation command.

No background job required.

### Provider Integration

None.

### UI / Admin Surface

If UI foundation exists:

- seller/admin policy form with version identifiers, policy enums, TTL fields, and legal-gate status;
- buyer disclosure with exact displayed version IDs;
- clear stale-policy refresh behavior;
- no misleading “legally approved” state without actual approval metadata/context.

### Failure Behavior

- Offering missing/ineligible → `not_found`/validation denial;
- unauthorized actor → forbidden;
- stale policy edit → conflict;
- stale buyer version → `digital_policy_version_stale`, re-present current version;
- missing required Consent proof → `digital_terms_required`/proof required;
- legal policy unavailable → fail closed, not default text.

### Tests

- playback SH-026 contract covers allow/deny, safe reasons, applicable evidence/freshness/expiry and delivery constraints without granting Video ownership of Digital Goods rules;

- policy validation/unit tests;
- optimistic concurrency/stale edit;
- Offering owner contract allow/deny;
- Consent contract linked without duplicate consent table;
- canonical hash test vector;
- duplicate acceptance idempotency;
- old acceptance immutability after policy update;
- stale presented version rejection;
- production legal-gate test;
- authorization tests;
- E2E test policy display → acceptance → evidence query.

### Documentation Updates

Keep ConsentType mapping and the Digital Goods historical-text persistence/retrieval mechanism unresolved until their owners approve them. Record any later owner-approved contract change in the affected architecture before merging behavior; this CL-05 pass does not change Consent architecture.

### Acceptance Criteria

- policy source truth is one Digital Goods record per Offering;
- historical acceptance stores exact version identifiers and hash/context;
- changing current policy cannot mutate old acceptance;
- no generic consent lifecycle is implemented here;
- stale/unauthorized acceptance is impossible;
- production legal gate is explicit.

### Exit Gate

Production legal-content activation is blocked until immutable owner-controlled historical content exists. Consent’s catalog supplies generic Consent-owned disclosures; Digital Goods owns contextual license/refund/access text unless explicitly classified otherwise. A ConsentLog link or acceptedTextHash alone is insufficient. The Digital Goods persistence/retrieval mechanism remains unresolved.


Pass typecheck, lint, unit, database integration, contract, authorization, and E2E policy/acceptance tests. Confirm no download grant/access code was added early.

---

# Phase 2 — Core Download Lifecycle and Public Delivery

## 03 Download Asset Registration and Readiness

### Objective

Implement DigitalDownloadAsset as the Digital Goods delivery record around a safe MediaAsset and expose a stable readiness decision to Marketplace/checkout consumers.

### Observable Result

An authorized seller/admin can attach a Media-ready asset to an eligible Offering/product/course and observe a DigitalDownloadAsset reach `ready`; a non-ready/invalid Media asset cannot become delivery-ready.

### Cluster Build-Plan Link

Supports **CL-05 Feature 04 — Purchased Digital Download Grant and Controlled Download** and consumes Media work from CL-05 Features 01–02.

### Dependencies

- Features 01–02;
- CL-05 Media Feature 01 complete or contract-equivalent;
- Marketplace SH-123 target validation;
- Media readiness query; Digital Goods owns contextual SH-090 `attachValidatedMedia`;
- SH-001/002/044/052/053.

### In Scope

- `registerDigitalDownloadAsset`;
- asset lifecycle transition service;
- asset readiness query;
- seller/admin asset status surface;
- disable/archive/delete owner commands that are non-moderation business actions where already approved;
- file/provider metadata treated as snapshot only.

### Out of Scope

- signed download URL;
- paid grant;
- R2/S3 SDK;
- Media upload/scanning;
- moderation adjudication;
- Search index implementation.

### Module-Owned Data

- `DigitalDownloadAsset`;
- `DigitalDownloadAssetStatus`;
- `DigitalStorageProvider` metadata.

### Public Interfaces

Implement:

- `registerDigitalDownloadAsset`;
- `getDigitalDownloadAsset` if a source-truth read is needed;
- `getDigitalDownloadReadiness`;
- explicit owner transition commands for archive/delete/restore only where architecture permits.

### Shared Operations Used

- SH-001/002 — actor/permission;
- SH-044 — registration idempotency;
- SH-052/053 — stale-write/transition mechanics;
- **SH-090 `attachValidatedMedia` — contextual owner (Digital Goods here).** Validate attachment meaning using Media-owned readiness/file truth;
- **SH-123** — Offering/Product/Course references;
- SH-029 — material admin transition audit;
- SH-046/091 — downstream readiness event/search refresh when a committed change affects public readiness.

**Prohibited duplicate:** file readiness/scanner/presigner or Marketplace lifecycle logic.

### Domain Logic

- Offering is mandatory; optional Product/Course refs must be owner-validated and consistent with Offering context;
- a Media reference is mandatory and must be ready/approved for the expected context;
- `fileName`, MIME, size, provider are copied only as delivery snapshot if needed; never used to bypass Media current readiness;
- `ready` means Digital Goods local asset is configured and Media dependency passed at transition time;
- access still re-checks Media later;
- restore from disabled states requires authorized source plus fresh Media readiness;
- `deleted` is terminal for product lifecycle, but retained grant/event evidence must follow retention policy rather than cascade blindly.

### Authorization / Compliance

- only Offering owner/admin manages delivery asset;
- no client-supplied provider/storage path accepted;
- DMCA/moderation-specific disable states are reserved for SH-103 execution, not seller-selected reasons.

### Database / Transaction Behavior

- asset creation + owner transition event/outbox transactionally persisted where downstream effect is needed;
- lock/compare-and-set on status transitions;
- verify indexes on Offering/status, MediaAsset, provider/status, deletedAt;
- do not change cascade behavior in this feature without approved retention decision.

### Events / Jobs

Possible:

- `digital_goods.download_asset.ready.v1`;
- `digital_goods.download_asset.disabled.v1`;
- `digital_goods.download_asset.restored.v1`.

No provider job here.

### Provider Integration

None. Provider enum metadata is not a direct provider client.

### UI / Admin Surface

- seller/admin asset status/readiness;
- safe reason when Media dependency is non-ready;
- no raw object key/provider URL.

### Failure Behavior

- invalid Offering/Product/Course relationship → validation denial;
- Media non-ready → `download_asset_not_ready`;
- duplicate registration → idempotent replay;
- stale transition → conflict;
- attempted DMCA state without Moderation envelope → forbidden/invalid transition.

### Tests

- target relationship contract tests;
- Media ready/non-ready tests;
- asset transition graph;
- idempotent creation;
- stale transition race;
- snapshot-vs-current-Media test proving snapshot fields do not authorize access;
- import test proving no storage SDK;
- E2E seller attaches ready Media → DigitalDownloadAsset ready.

### Documentation Updates

If a schema check/constraint is required for product/course relation integrity, document and migrate only after architecture approval.

### Acceptance Criteria

- only owner-validated ready Media becomes ready DigitalDownloadAsset;
- no permanent/public URL is created;
- asset status has one owner;
- Marketplace can consume readiness without direct Digital Goods table access.

### Exit Gate

All asset lifecycle, dependency contract, authorization, and E2E readiness tests pass; Media provider code remains outside Digital Goods.

---

## 04 Purchased Grant Issuance and Buyer Download Library

### Objective

Create normal purchased `DigitalDownloadGrant` truth from an authoritative qualifying Order and expose a buyer download-library read model without copying Order/payment truth.

### Observable Result

A buyer with a qualifying Order and required terms acceptance can receive one idempotent bounded grant and see the purchased item in a buyer digital-download list. A non-entitled/refunded/wrong buyer receives no grant.

### Cluster Build-Plan Link

Directly implements the grant-issuance portion of **CL-05 Feature 04**.

### Dependencies

- Features 02–03;
- SH-004 Customer actor;
- SH-025 Order entitlement;
- SH-011 Hold if applicable;
- SH-044/074/088;
- approved decision on exact policy values required for TTL/max use; default 24h may be used where current schema/policy supplies it.

### In Scope

- `issueDigitalDownloadGrant`;
- `listUserDigitalDownloads`;
- grant source/reference validation;
- grant TTL/max-download derivation;
- idempotency/replay;
- grant-issued event/evidence;
- unsupported null-Order denial.

### Out of Scope

- signed URL issuance;
- download counter consumption;
- complimentary/admin/library access;
- refund adjudication;
- storage/provider code.

### Module-Owned Data

- `DigitalDownloadGrant`;
- `DigitalDownloadGrantStatus`;
- optionally `DigitalDownloadEvent` for grant issue only if the event vocabulary later adds/uses a corresponding domain event; current event enum does not have `grant_issued`, so integration event may carry issuance fact without fabricating a DigitalDownloadEvent type.

### Public Interfaces

Implement:

- `issueDigitalDownloadGrant`;
- `listUserDigitalDownloads`;
- `getDigitalDownloadGrantState` internal/public only if required by consumer contract.

### Shared Operations Used

- SH-001 — authenticated User;
- SH-004 — CustomerProfile buyer context;
- SH-011 — applicable hold;
- **SH-025 — Order entitlement**;
- SH-044 — idempotent issuance;
- SH-074 — optional secure grant token;
- **SH-088 — grant mechanics**;
- SH-046 — `digital_goods.download_grant.issued.v1` if required;
- SH-032/034 — safe correlation/telemetry.

**Local policy:** policy/asset/acceptance readiness, TTL, max downloads, grant binding.

**Prohibited duplicate:** Order repository/payment checks, local CustomerProfile resolver, universal grant table.

### Domain Logic

1. Resolve actor/User and commercial CustomerProfile.
2. Load Digital Goods asset/policy/acceptance through owner repositories.
3. Re-check asset local readiness.
4. Call SH-025 for the exact Order/item/action.
5. Reject null Order for normal purchased path.
6. Validate required terms acceptance matches the applicable policy version.
7. Evaluate applicable hold.
8. Derive `expiresAt` from asset/policy (current default 24 hours unless approved policy overrides).
9. Derive finite/unlimited max usage.
10. Issue one semantic grant through SH-044.
11. Store only token hash if a bearer token is actually used.
12. Buyer library composes Digital Goods grant/asset state with minimal owner facts; it does not cache payment/provider truth as authoritative Digital Goods state.

### Authorization / Compliance

- authenticated User must match Order/customer relationship returned by Order/Customer interfaces;
- a valid grant is not created on denial merely to represent the denial unless a later explicit policy requires a denied-grant proof record;
- terms proof is contextual and must match versions;
- no Track entitlement is checked unless a concrete digital perk is approved.

### Database / Transaction Behavior

- issuance transaction writes grant + outbox fact if emitted;
- semantic idempotency key should include buyer/User, asset, Order, applicable policy/acceptance context, and operation purpose as defined in feature spec;
- do not invent a unique DB constraint until the intended reissue/multiple-grant policy is explicit;
- if token-hash lookup is enabled, add uniqueness protection before production through an approved migration.

### Events / Jobs

- `digital_goods.download_grant.issued.v1` outbox fact if downstream Notification/fulfillment needs it;
- expiration handled in later worker/hardening feature, but `expiresAt` is authoritative immediately.

### Provider Integration

None.

### UI / Admin Surface

- buyer “My downloads” list: title, grant availability, expiry/remaining uses where safe;
- no raw storage URL/token;
- seller/support read model may show grant status only through authorized surface.

### Failure Behavior

- Order denied/refunded/not qualifying → `order_entitlement_denied`, no new grant;
- wrong actor/customer → forbidden;
- policy/terms mismatch → terms/policy denial;
- asset non-ready/disabled → access denied;
- unsupported `orderId=null` → `unsupported_access_basis`;
- duplicate issue → replay existing semantic result.

### Tests

- Order contract state matrix;
- CustomerProfile/User relationship;
- terms required/matching/missing/stale;
- hold gate;
- 24-hour default and override derivation;
- idempotent duplicate issue;
- wrong actor/no Order/refunded denial;
- library query does not read Stripe/provider state;
- no raw token persisted/logged;
- E2E eligible Order → grant listed.

### Documentation Updates

If product approves alternate access basis or reissue semantics, update Module architecture before expanding command behavior.

### Acceptance Criteria

- only an SH-025-eligible normal purchase can create a normal grant;
- grant is bounded by `expiresAt` immediately;
- duplicate issuance is harmless;
- buyer library exposes no permanent URL and does not copy payment truth;
- no null-Order path is accidentally enabled.

### Exit Gate

Order/Customer/terms/hold contract tests, grant DB integration tests, idempotency tests, and buyer-library E2E pass.

---

## 05 Controlled Download Access, Usage, Expiration, and Domain Evidence

### Objective

Complete the actual buyer download path by revalidating the grant and upstream entitlement, atomically enforcing usage, invoking Media for short-lived signed access, and recording Digital Goods evidence.

### Observable Result

An eligible buyer can request access and receive a short-lived Media-owned signed URL. Expired, revoked, exhausted, wrong-actor, disabled-asset, refunded, or otherwise non-entitled paths produce stable denials and never return a usable URL.

### Cluster Build-Plan Link

Completes the core behavior of **CL-05 Feature 04**.

### Dependencies

- Feature 04;
- CL-05 Media Feature 02 / composite `requestMediaAccess` (SH-087 remains Media-internal);
- SH-025 current entitlement;
- SH-030 audit interface;
- SH-051/057/088/125;
- decision on the production usage-consumption point remains unresolved for `final_after_access`; test policy must make the point explicit.

### In Scope

- `issueDigitalDownloadAccess`;
- grant access-time validation;
- Media signed URL call;
- atomic usage counter/status;
- `DigitalDownloadEvent` append for issued/denied/start/completed/failed/expiry/revocation as applicable;
- grant expiration worker;
- single/bulk revoke owner commands;
- support-safe delivery evidence query.

### Out of Scope

- storage client/presigning;
- determining whether a refund should be granted;
- legal definition of `final_after_access`;
- generic AuditEvent/AccessAuditLog ownership;
- non-purchase access basis.

### Module-Owned Data

- `DigitalDownloadGrant` usage/status/timestamps;
- `DigitalDownloadEvent` append-only evidence;
- no direct Media mutation.

### Public Interfaces

Implement:

- `issueDigitalDownloadAccess`;
- `revokeDigitalDownloadGrant`;
- `revokeDigitalDownloadGrantsForAsset`;
- `revokeDigitalDownloadGrantsForOrder`;
- `getDigitalDeliveryEvidence`;
- owner expiration command invoked by worker.

### Shared Operations Used

- SH-001 — actor;
- SH-011 — hold recheck where mapped;
- SH-025 — current Order entitlement;
- SH-030 — sensitive access evidence where policy requires;
- SH-032/034/037 — request context/safe failure telemetry;
- SH-044 — request/revoke idempotency;
- SH-051 — grant lock;
- **SH-055 — expiration scheduler**;
- **SH-057 — atomic usage counter**;
- **SH-026 `authorizeContextualResourceAccess` — Digital Goods context.** Supply business authorization/grant evidence to Media;
- **SH-087 `issueSignedMediaUrl` — Media-internal capability**, consumed through public composite `requestMediaAccess`;
- SH-088/089 — validate/revoke shared grant mechanics;
- **SH-125 — append DigitalDownloadEvent**;
- SH-047/048 — bulk revocation/expiration work.

**Prohibited duplicate:** presigner, download counter helper using non-atomic read/write, separate audit ledger, Digital Goods cron framework.

### Domain Logic

#### Access workflow

1. Resolve authenticated actor.
2. Lock/read grant and validate actor binding.
3. Check `expiresAt` against server time regardless of stored status.
4. Validate current grant status and finite usage remaining.
5. Validate DigitalDownloadAsset current local state.
6. Revalidate SH-025 Order entitlement for normal purchased path.
7. Evaluate applicable hold.
8. Call Media `requestMediaAccess` with the Digital Goods SH-026 decision and grant evidence; Media revalidates safety/freeze/erasure and its grant/proof requirements, invokes SH-087 internally, and returns a short-lived credential or typed denial.
9. At the **approved consumption point**, atomically increment bounded usage and, under the proposed rule, set `used` when finite allowance is exhausted.
10. Store only signed URL hash/evidence if needed; never raw URL.
11. Append DigitalDownloadEvent and required generic sensitive access audit.
12. Return signed URL + expiry only after all required gates pass.

#### Important unresolved threshold

Until product/legal architecture defines what counts as “access” for `final_after_access`, production code must not silently use URL issuance, start, or completion as the legal refund threshold. Tests may use an explicit test-policy consumption event to prove mechanics.

#### Expiration

- worker scans by `expiresAt` using SH-055;
- owner transition to `expired` is idempotent;
- a grant past `expiresAt` is invalid even before worker writes status.

#### Revocation

- source reference/reason mandatory;
- revocation under lock wins deterministically against later access;
- already terminal grants return idempotent outcome;
- append `grant_revoked` event.

### Authorization / Compliance

- possession of grant ID/token is insufficient without actor binding;
- current Order revalidation prevents stale grant bypass after refund/dispute outcome where SH-025 denies;
- hold/moderation effects are enforced;
- signed URL and provider identifiers are minimized in response/logging;
- AccessAuditLog used according to approved sensitivity matrix.

### Database / Transaction Behavior

- grant state/counter/event transaction boundary must be explicit in the feature spec according to the approved consumption point;
- SH-057 prevents over-consumption under parallel calls;
- access vs revoke vs expire uses row lock or compare-and-set with deterministic terminal-state precedence;
- DigitalDownloadEvent append is transactionally tied to the local business effect it proves where feasible;
- provider signing failure must not consume usage unless the approved policy explicitly defines attempted issuance as consumption.

### Events / Jobs

- grant expiration worker;
- bulk revocation worker;
- optional outbox facts for grant revoked/expired;
- no provider webhook/event dedupe ledger owned here for R2 signing.

### Provider Integration

Digital Goods calls only Media’s public composite `requestMediaAccess`; SH-087 signing stays internal to Media. Test credential/typed-denial, replay, proof references, and provider-failure behavior through that contract using a fake and real Media integration environment when available.

### UI / Admin Surface

- buyer Download action with safe expired/revoked/exhausted/temporarily unavailable states;
- remaining uses/expiry where product UI allows;
- support-safe evidence viewer without URL/token.

### Failure Behavior

- wrong actor → forbidden;
- expired → stable denial + owner expiration transition/event may be performed idempotently;
- revoked/used/exhausted → denial;
- Order denied → denial and optionally schedule/source-referenced revocation according to policy;
- Media non-ready/frozen/erased → denial;
- Media presign outage → `temporary_delivery_failure`, record SH-037, do not incorrectly consume use;
- concurrent final allowance → one succeeds, losers receive exhausted/conflict result;
- audit/notification failure does not expose a URL before required security/audit guarantees if policy marks audit as mandatory; otherwise follow root failure policy.

### Tests

- access success contract + signed URL TTL;
- wrong actor;
- grant expired by server time before worker;
- revoked/disabled/refunded denial;
- parallel max-download test proving no overrun;
- access/revoke race;
- access/expiry race;
- Media signing failure without unwanted counter consumption;
- no raw signed URL/token in DB/log/audit scans;
- DigitalDownloadEvent vs MediaAccessEvent vs AccessAuditLog separation;
- expiration worker idempotency;
- E2E Order → grant → signed download and Order refund/denial → no access.

### Documentation Updates

When the authoritative “access consumed” threshold is approved, update Module architecture, feature spec, refund-evidence contract, and tests before enabling production `final_after_access` behavior.

### Acceptance Criteria

- no invalid grant path can return a signed URL;
- no parallel request exceeds max usage;
- provider signing exists only behind Media;
- worker delay cannot extend validity;
- domain event evidence is complete and separate from generic audit;
- provider outage does not corrupt usage truth.

### Exit Gate

All contract, database concurrency, security-log, worker, and E2E download tests pass. The unresolved legal threshold remains explicitly gated if not approved.

---

# Phase 3 — Child-Directed Controls and Accessibility

## 06 Child-Directed Declaration and Minor Privacy Controls

### Objective

Implement the schema-backed declaration/control mechanics without inventing legal approval criteria or treating product declarations as User-age truth.

### Observable Result

Using approved test rules:

- an authorized seller/admin can submit a declaration;
- an uncertain/review-required case can enter `admin_review_required`;
- an authorized reviewer can record an explicit approved/rejected/disabled result only when the configured legal/test policy permits it;
- product surfaces can query effective `MinorPrivacyControl` records;
- controls can be applied/revoked idempotently and trigger Search/Notification effects through owner interfaces.

### Cluster Build-Plan Link

Implements the child-directed portion of **CL-05 Feature 05**.

### Dependencies

- Features 01–02;
- Marketplace target validation;
- SH-001/002/011/029/041/072/091/123;
- approved test declaration policy;
- production legal criteria may remain unavailable.

### In Scope

- `declareChildDirectedContent`;
- declaration query/read model;
- explicit review command;
- local projection `MinorPrivacyControl`;
- effective control query for known product surface;
- Search refresh and Notification requests where configured;
- audit of admin review/change.

### Out of Scope

- general platform age gate;
- global cookie/ad infrastructure implementation;
- automatic legal adjudication;
- production criteria not supplied;
- global PrivacyRequest workflow.

### Module-Owned Data

- `ChildDirectedContentDeclaration`;
- `MinorPrivacyControl`;
- related status enum.

### Public Interfaces

Implement:

- `declareChildDirectedContent`;
- `getChildDirectedDeclaration` / current-status query that does **not** guess effective state beyond approved rules;
- `reviewChildDirectedDeclaration`;
- `getMinorPrivacyControls`;
- internal `deriveMinorPrivacyControls`.

### Shared Operations Used

- SH-001/002 — actor/authority;
- SH-011 — hold where review/action is hold-sensitive;
- SH-029 — review/control audit;
- SH-041 — review outcome notification if approved;
- SH-044 — declaration/review idempotency;
- SH-052/053 — stale transition mechanics;
- SH-072 — declaration content hash;
- SH-091 — Search refresh;
- SH-123 — Offering target validation.

**Prohibited duplicate:** age-gate system, generic privacy/cookie engine, moderation queue, Search client.

### Domain Logic

- validate intended age range sanity without making legal conclusion;
- hash the declaration/version text;
- one submission creates immutable declaration evidence plus mutable review state as schema permits;
- do not use “latest row wins” for production effective status unless approved policy explicitly defines it;
- any uncertainty enters `admin_review_required` under approved rules rather than auto-approval;
- only an explicit effective/approved decision may project product-surface controls;
- projection sets/clears tracking cookies, targeted ads, public comments, behavioral analytics according to approved policy;
- `MinorPrivacyControl` target types are server-controlled constants, not arbitrary request strings.

### Authorization / Compliance

- seller can declare only for owned Offering;
- reviewer/admin must pass explicit resource action authorization;
- declaration never proves User age/COPPA compliance completion;
- production approval criteria absent → no automatic `approved`;
- no raw sensitive data in notes/search/notification payloads.

### Database / Transaction Behavior

- declaration/review uses optimistic concurrency/row lock;
- control projection update and declaration state/event should be transactionally consistent where possible;
- prevent duplicate active projections for the same approved declaration/target through command idempotency; add DB uniqueness only when exact target vocabulary/effective-state rule is approved.

### Events / Jobs

Potential outbox:

- `digital_goods.child_declaration.changed.v1`;
- `digital_goods.minor_privacy_controls.changed.v1`.

Search refresh and Notification are asynchronous downstream requests.

### Provider Integration

None.

### UI / Admin Surface

- seller declaration form/status;
- admin review surface only if root admin framework exists;
- product-control summary;
- clear “review required/not production approved” state.

### Failure Behavior

- invalid target → validation/not found;
- seller unauthorized → forbidden;
- stale review → conflict;
- legal/test criteria unavailable → `manual_review_required`/blocked auto-decision;
- Search/Notification outage → source truth still commits; downstream owner retries and SH-037 records failure where appropriate.

### Tests

- declaration validation/hash;
- seller authorization;
- review stale-write/authority;
- test-policy review-required path;
- no unapproved auto-approval;
- control projection apply/revoke idempotency;
- Search request contract, no Typesense direct call;
- Notification payload safety;
- test proving product declaration cannot satisfy User age gate;
- E2E declaration → review/control projection under test policy.

### Documentation Updates

When production legal criteria/effective-declaration rule is approved, update Module architecture before enabling automatic mappings.

### Acceptance Criteria

- declarations/controls are explicit records, not Offering/User booleans;
- uncertain cases cannot silently approve;
- effective controls are queryable without consumers reading raw declaration tables;
- User age truth remains separate;
- Search/Notification integration uses public interfaces only.

### Exit Gate

All declaration/control authorization, policy-gate, projection, contract, and E2E tests pass. Production automatic approval remains disabled if criteria are unresolved.

---

## 07 Course Accessibility Asset Tracking and Readiness

### Objective

Implement Digital Goods accessibility-semantic records and readiness decisions while keeping Media file truth and Video streaming truth outside the Module.

### Observable Result

An authorized seller/admin can create/attach caption, transcript, audio-description, or descriptive-text records, observe their lifecycle, and expose a readiness result to Marketplace/Video/course UI. A required asset cannot become ready when its backing Media file is non-ready.

### Cluster Build-Plan Link

Implements the accessibility portion of **CL-05 Feature 05** and supplies Digital Goods facts consumed by CL-05 Feature 06 Course Video delivery.

### Dependencies

- Feature 03 / Media ready substrate;
- Marketplace Offering/Course facts;
- Media readiness; Digital Goods owns contextual SH-090 attachment;
- Video `getCourseVideoProcessingStatus` owner-validated relationship facts when `courseVideoAssetId` is used: canonical courseDetailsId identifies CourseDetails.offeringId / the owning Offering, and any present redundant offeringId must equal it;
- SH-001/002/044/052/053/123;
- waiver authority remains unresolved for production.

### In Scope

- `registerCourseAccessibilityAsset`;
- accessibility lifecycle transition service;
- list/query/readiness;
- required/default/language validation;
- Media and optional Video relation validation;
- seller/admin status UI;
- review evidence for rejection/waiver/not-required only when authority/policy exists.

### Out of Scope

- caption/transcript file parsing/generation unless another approved Module/provider owns it;
- Media upload/processing internals;
- CourseVideoAsset processing/playback;
- general app accessibility standards;
- automatic legal waiver.

### Module-Owned Data

- `CourseAccessibilityAsset`;
- `AccessibilityAssetType`;
- `AccessibilityAssetStatus`.

### Public Interfaces

Implement:

- `registerCourseAccessibilityAsset`;
- `updateCourseAccessibilityAssetState`;
- `listCourseAccessibilityAssets`;
- `getCourseAccessibilityReadiness`.

### Shared Operations Used

- SH-001/002 — actor/authority;
- SH-044 — idempotent registration/state commands;
- SH-052/053 — transition/stale-write mechanics;
- SH-090 `attachValidatedMedia` — Digital Goods/contextual-owner attachment using Media readiness;
- SH-123 — Offering/Course/Video target validation;
- SH-029 — review/waiver audit if approved;
- SH-041/091 — outcome notification/search refresh where product policy requires.

**Prohibited duplicate:** Media validator/storage, Mux/video processing state, generic UI accessibility engine.

### Domain Logic

- record type/language/required/default semantics;
- attached Media must be ready before accessibility record reaches `ready`;
- before attaching `courseVideoAssetId`, verify its expected course/Offering through Video’s owner-validated `getCourseVideoProcessingStatus` facts; never query the Video repository or accept divergent redundant offeringId;
- readiness reports required assets missing/processing/failed/rejected/ready and approved waiver/not-required states;
- only one default per approved scope/type/language should be effective; exact DB constraint may be added once scope semantics are confirmed;
- `waived` and `not_required` require explicit authority/policy and cannot be self-selected by ordinary seller if production criteria are unresolved.

### Authorization / Compliance

- seller/admin may manage records only for eligible owned course context;
- reviewer-only transitions require explicit authorization;
- production waiver fails closed until approved criteria/authority exist;
- accessibility support record does not itself prove the entire course/app meets accessibility law.

### Database / Transaction Behavior

- register/update under idempotency;
- state transition compare-and-set;
- relation validation before insert;
- no direct update of Media/Video state;
- record + outbox/Search refresh transactionally committed if readiness affects public projection.

### Events / Jobs

- `digital_goods.accessibility.changed.v1` where downstream consumers need update;
- no provider worker required unless a later approved accessibility processor is introduced through its proper owner.

### Provider Integration

None owned by Digital Goods.

### UI / Admin Surface

- accessibility asset list by type/language/status;
- required/default indicators;
- safe failure/review note display to authorized users;
- upload action delegates to Media uploader.

### Failure Behavior

- invalid Offering/Course/Video relation → validation denial;
- Media non-ready → cannot transition ready;
- unauthorized waiver/review → forbidden/manual-review required;
- stale update → conflict;
- Search/Notification outage does not alter source truth.

### Tests

- type/status transition graph;
- relation contracts with Marketplace/Media/Video;
- required readiness calculation;
- non-ready Media cannot produce ready accessibility asset;
- default conflict test;
- waiver policy blocked when not approved;
- Search/Notification contract tests;
- E2E ready Media caption/transcript → accessibility ready → readiness query.

### Documentation Updates

When waiver/default-scope criteria are finalized, update Module architecture and DB constraint strategy.

### Acceptance Criteria

- accessibility semantics are Digital Goods truth;
- bytes remain Media truth;
- streaming remains Video truth;
- readiness is stable and explainable;
- unapproved waiver path cannot activate.

### Exit Gate

Unit, dependency contract, DB transition, authorization, and E2E accessibility tests pass.

---

# Phase 4 — Module Integration and Guardrail Effects

## 08 Core Neighbor Contract Verification

### Objective

Prove Digital Goods works through public contracts with Marketplace Supply, Transaction / Order, Media / File Access, Consent & Disclosure, and Video Session without direct foreign repositories or provider leakage.

### Observable Result

A contract/integration harness can execute the principal journeys using real or production-faithful Module interfaces:

- Offering policy/readiness consumed by Marketplace;
- terms evidence linked to Consent proof;
- qualifying Order creates grant;
- Media signs delivery only after Digital Goods authorization;
- accessibility record can reference a Video-owned CourseVideoAsset without taking over Video state;
- each owner can be replaced by a contract fake without changing Digital Goods domain logic.

### Cluster Build-Plan Link

Consolidates Digital Goods integration proof across **CL-05 Features 03–06** without re-sequencing them.

### Dependencies

- Features 02–07;
- neighboring public interfaces sufficiently implemented;
- shared-operation contracts stable.

### In Scope

- contract test suite for all core neighbors;
- interface compatibility/schema version tests;
- direct-repository/provider import scan;
- end-to-end paid download path across Order + Media;
- Marketplace readiness consumer test;
- Video accessibility reference test.

### Out of Scope

- moderation/refund-event invalidation bridge beyond current access revalidation;
- Privacy orchestration;
- provider chaos/reconciliation;
- new product features.

### Module-Owned Data

Existing records only. No new schema by default.

### Public Interfaces

Harden and version the interfaces built in Features 02–07. No new broad public interface unless a real consumer gap is demonstrated.

### Shared Operations Used

- SH-004, SH-007/008, SH-025, SH-026 `authorizeContextualResourceAccess` (Digital Goods playback/file decision), SH-087 (Media-internal through requestMediaAccess), SH-090 (contextual owner), SH-123;
- SH-044/046 where commands/events are part of contract proof;
- SH-032 correlation in cross-Module test harness.

### Domain Logic

No new domain policy. This feature proves existing policy remains in the correct owner when integrated.

### Authorization / Compliance

- contract tests include actor/owner/buyer mismatch;
- Consent proof cannot replace Digital Goods acceptance;
- Order allow cannot bypass Digital Goods asset/grant policy;
- ready DigitalDownloadAsset cannot bypass Media revalidation/signing;
- accessibility record cannot mutate Video source state.

### Database / Transaction Behavior

Cross-Module tests use public interfaces. Direct test fixtures may seed foreign owner records through owner test factories, not by making Digital Goods repositories responsible for them.

### Events / Jobs

Verify outbox envelope and downstream consumer expectations without forcing every domain access row into an integration event.

### Provider Integration

No provider client in Digital Goods. A real Media integration may ultimately exercise R2 through Media only.

### UI / Admin Surface

No new surface; verify existing policy/download/accessibility UI against real contract responses if present.

### Failure Behavior

- dependency temporary failure returns stable Digital Goods category;
- dependency business denial preserves source owner reason/evidence but does not expose internal provider status;
- contract version mismatch fails test/build before production.

### Tests

- Marketplace contract;
- Order contract;
- Consent contract;
- Media readiness/signing contract;
- Video owner-facts contract;
- cross-Module E2E purchased download;
- import/layer test proving no foreign repository/provider client;
- stable reason-code mapping tests.

### Documentation Updates

Update dependency interface docs if real contracts differ from planning names. Do not change owner semantics without architecture update.

### Acceptance Criteria

- all core neighbors are consumed through typed public interfaces;
- no owner logic is reconstructed inside Digital Goods;
- the full paid download journey works across Module boundaries;
- providers remain invisible to Digital Goods domain/application code.

### Exit Gate

Core neighbor contract suite and principal cross-Module E2E pass with zero prohibited imports.

---

## 09 Entitlement Loss, Refund, Moderation, Hold, Search, and Notification Bridge

### Objective

Prove authoritative external state changes remove/degrade Digital Goods access through owner-local commands/events without cross-owner mutation.

### Observable Result

After an authoritative refund/non-entitlement, moderation action, or applicable ComplianceHold:

- current access denies;
- affected grants are revoked when owner policy requires;
- DigitalDownloadAsset enters the correct disabled state for moderation action;
- Search receives refresh/removal request if public readiness changed;
- Notification receives safe user/admin intent when configured;
- duplicate source events/actions are harmless.

### Cluster Build-Plan Link

Implements the Digital Goods portion of **CL-05 Feature 13 — Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification**.

### Dependencies

- Features 05 and 08;
- SH-011 Hold;
- SH-025 Order entitlement and authoritative Order/refund events;
- SH-045/046 event infrastructure;
- SH-089 grant revocation;
- SH-103 Moderation;
- SH-091 Search;
- SH-041 Notification;
- SH-029/030 Audit.

### In Scope

- inbound event handlers for Order/refund/dispute access invalidation where Transaction / Order publishes them;
- `applyDigitalModerationDecision`;
- bulk revocation by Order/asset/source decision;
- current SH-025 revalidation at access endpoint;
- hold gate mapping;
- Search refresh requests;
- safe Notification requests;
- event inbox dedupe;
- support execution acknowledgment/read model.

### Out of Scope

- refund/dispute adjudication;
- DMCA/legal validity;
- ComplianceHold lifecycle;
- Search document schema/indexer;
- Notification delivery/templates beyond request contract;
- Track plan lifecycle.

### Module-Owned Data

Potential transitions:

- `DigitalDownloadAsset.status` to `disabled`, `disabled_by_dmca`, `disabled_by_moderation`, or restored `ready` after authorized decision + Media recheck;
- `DigitalDownloadGrant.status` to `revoked`;
- `DigitalDownloadEvent` revocation/denial evidence.

### Public Interfaces

- `applyDigitalModerationDecision`;
- `revokeDigitalDownloadGrantsForOrder`;
- `revokeDigitalDownloadGrantsForAsset`;
- inbound owner event handlers;
- execution acknowledgment DTO for Moderation.

### Shared Operations Used

- SH-011 — hold;
- SH-025 — current Order entitlement;
- **SH-045 — consumed event dedupe**;
- SH-046 — Digital Goods transition events;
- SH-047/048 — bulk revocation jobs;
- SH-089 — grant revocation pattern;
- **SH-091 — Search refresh**;
- **SH-103 — Moderation decision execution**;
- SH-041 — Notification request;
- SH-029/030 — audit;
- SH-032/034/037 — safe operational failure/correlation.

**Prohibited duplicate:** local refund/moderation/hold/search/notification truth.

### Domain Logic

- authenticate/version/dedupe incoming event/action;
- map source fact to an allowed local Digital Goods transition;
- source reason/reference is stored on revocation/disable evidence;
- revalidation at the download endpoint prevents a stale active grant bypass even if async revocation is delayed;
- moderation-specific status may only be set from authorized SH-103 action;
- restore requires explicit Moderation restore + Media current readiness;
- Search refresh is requested only for relevant Offering public readiness;
- Notification is non-authoritative side effect.

### Authorization / Compliance

- moderation reason originates from Moderation;
- refund/transaction state originates from Order;
- hold originates from Hold owner;
- admin/support cannot invent an enforcement reason outside approved command path;
- audit metadata contains source refs/reason codes, not raw legal notice text.

### Database / Transaction Behavior

- source event inbox claim + local transition should be transactionally consistent according to SH-045 pattern;
- asset transition + outbox fact transactional;
- bulk grant revocation can be batched, idempotent by source decision ID + grant target;
- partial job failure records retryable/terminal outcome without undoing authoritative source decision.

### Events / Jobs

- Order/refund/dispute consumer handlers;
- bulk grant revocation jobs;
- Digital Goods disabled/restored/grant-revoked outbox facts;
- Search/Notification downstream requests.

### Provider Integration

No direct provider delete/signing. If moderation requires Media object-level action, request/consume Media owner interface separately; Digital Goods does not mutate R2.

### UI / Admin Surface

- buyer sees safe unavailable/revoked status;
- seller sees disabled/moderation state without unsupported legal detail;
- support can see source action reference and local execution state through authorized view.

### Failure Behavior

- one grant revocation fails → retry that batch; current access still revalidates source entitlement/asset state;
- Search unavailable → source enforcement remains committed;
- Notification unavailable → source enforcement remains committed;
- duplicate event/action → no duplicate transition/provider effect;
- Moderation restore while Media unsafe → local asset remains non-ready/disabled with safe failure evidence.

### Tests

- refunded Order denies current access and triggers/reconciles revocation;
- duplicate refund event one effect;
- SH-103 DMCA action → disabled_by_dmca + grant revocation;
- unauthorized local attempt to set DMCA status fails;
- hold blocks representative access;
- Search contract only, no Typesense call;
- Notification safe payload;
- stale signed/access path cannot bypass revalidation;
- E2E access before external decision → decision → denied.

### Documentation Updates

If Transaction / Order event names or Moderation action taxonomy become binding, document them in public interface sections and event schema registry.

### Acceptance Criteria

- external authoritative decisions reliably remove access without ownership theft;
- stale grants cannot bypass current revalidation;
- duplicate events/actions are harmless;
- Search/Notification are public-interface-only effects;
- no local generic blocked/refund/moderation truth is introduced.

### Exit Gate

Cross-Cluster contract, idempotency, revocation, Search/Notification, audit, and E2E invalidation tests pass.

---

# Phase 5 — Privacy and Production Hardening

## 10 Privacy Inventory, Retention Facts, and Target Execution

### Objective

Implement Digital Goods’ side of Privacy-owned workflows so Privacy can enumerate, retain, anonymize, revoke, erase, or export Digital Goods data through typed owner contracts.

### Observable Result

A Privacy test harness can:

- enumerate all Digital Goods records associated with a subject;
- receive supported dispositions and retention candidates;
- execute a typed disposition;
- observe revoked/anonymized/deleted/retained/skipped/failed results;
- preserve retention-required transaction/consent/access evidence only through the Privacy exemption path.

### Cluster Build-Plan Link

Implements the Digital Goods portion of **CL-05 Feature 14 — Privacy Target Executors, Retention, and Provider Deletion**.

### Dependencies

- Features 02–09;
- SH-095–097 Privacy protocol;
- SH-089 grant revocation;
- SH-044/047/048;
- Audit/Observability;
- retention facts from Order/legal owners where needed;
- Media executes object/provider deletion for backing files.

### In Scope

- `enumerateSubjectData` implementation;
- `evaluateRetentionRequirement` owner facts;
- `executePrivacyInstruction`;
- safe export serializer contribution if Privacy requires it;
- grant revocation before destructive removal where needed;
- anonymization of eligible actor/request metadata;
- retention/cascade verification;
- idempotent execution and result evidence.

### Out of Scope

- PrivacyRequest identity verification;
- PrivacyRequest/DataErasureJob/Target lifecycle;
- creation of DataRetentionExemption;
- legal determination of tax/payment/contract retention;
- direct R2/provider deletion;
- Search privacy parent completion aggregation.

### Module-Owned Data

Inventory at minimum:

- `DigitalGoodsTermsAcceptance`;
- `DigitalDownloadAsset.createdByUserId` where subject-linked;
- `DigitalDownloadGrant`;
- `DigitalDownloadEvent`;
- `ChildDirectedContentDeclaration` actor refs;
- `MinorPrivacyControl` if directly subject-linked through declaration/Offering;
- `CourseAccessibilityAsset` uploader/reviewer refs.

### Public Interfaces

Implement:

- SH-096 owner inventory;
- SH-097 owner retention facts;
- SH-095 owner execution;
- export serializer/query if requested by Privacy.

### Shared Operations Used

- **SH-095 `executePrivacyInstruction`**;
- **SH-096 `enumerateSubjectData`**;
- **SH-097 `evaluateRetentionRequirement`**;
- SH-089 grant revocation;
- SH-044/047/048 idempotent/retryable execution;
- SH-029/030 destructive/sensitive audit;
- SH-032/034/037 safe telemetry/failure;
- SH-091 if a resulting public-readiness effect requires Search refresh;
- Media owner privacy interface for backing-object/provider effects.

**Prohibited duplicate:** local PrivacyRequest/erasure job/retention flag, direct Media provider deletion.

### Domain Logic

- inventory uses stable target types/cursors and describes supported disposition;
- distinguish product deletion from privacy erasure;
- revoke active access before deleting/anonymizing where necessary;
- retention facts state what Digital Goods evidence may need to remain and why, but Privacy records the exemption;
- anonymization preserves relational integrity and minimum required evidence;
- direct hard delete is prohibited when an approved retention disposition says retain;
- retained records expose only permitted minimum subject data after anonymization;
- Privacy executor is replay-safe.

### Authorization / Compliance

- only Privacy-authorized system workflow invokes destructive executor;
- manual retry uses explicit admin authorization and SH-014 if root policy later requires it;
- provider/object references remain private;
- IP/user-agent evidence minimized when retention does not require it;
- legal/payment/dispute retention conclusions from their owning domains are not reinterpreted locally.

### Database / Transaction Behavior

- each target execution has a clear transaction boundary;
- bulk subject work may be queued but each target result is idempotent;
- cascade deletion is disabled/avoided where it could bypass retention decisions;
- if migration is required to prevent cascade destruction, this feature cannot pass production exit gate until the migration is approved and tested.

### Events / Jobs

- Privacy execution jobs through shared queue;
- grant revocation;
- downstream Search refresh after permitted source change;
- no local Privacy parent event lifecycle.

### Provider Integration

None directly. Media owns backing object deletion; Video owns video provider deletion. Digital Goods reports its own semantic record disposition.

### UI / Admin Surface

No standalone Digital Goods Privacy UI. Privacy/admin owner surface consumes typed results. Optional debug evidence is Privacy-authorized only.

### Failure Behavior

- retention required → `retained` result with source reason, no silent delete;
- already absent → idempotent success semantics;
- partial batch failure → target-level retry/failed result, Privacy parent decides completion;
- Media provider deletion unavailable → Digital Goods does not claim object deletion; owner result remains partial according to Privacy protocol;
- duplicate instruction → same semantic result.

### Tests

- subject inventory completeness;
- terms/grant/event retention cases;
- anonymization mapping;
- active grant revocation;
- retained record only through Privacy exemption scenario;
- prove no local PrivacyRequest/DataErasureJob created;
- cascade/destructive migration tests;
- provider owner handoff contract;
- telemetry redaction;
- E2E Privacy harness → enumerate → execute → result.

### Documentation Updates

Any retention-safe schema migration or approved retention rule must update Module architecture and root/Privacy documentation.

### Acceptance Criteria

- Privacy can discover and act on all Digital Goods subject data through typed contracts;
- no parallel privacy lifecycle exists;
- retained records are retained only through approved exemption flow;
- object/provider deletion ownership remains outside Digital Goods;
- destructive cascades cannot bypass retention decisions.

### Exit Gate

Privacy contract/integration tests, retention/anonymization tests, cascade safety tests, audit/telemetry scans, and end-to-end Privacy harness pass.

---

## 11 Concurrency, Security, Audit, Performance, and Production Verification

### Objective

Harden Digital Goods for production under retries, concurrent access, stale grants, provider/Media failure, missed external invalidation, privacy constraints, and operational degradation without adding new product scope.

### Observable Result

Digital Goods behaves deterministically under load and failure:

- parallel downloads cannot exceed limits;
- access/revoke/expiry races resolve safely;
- missed async revocation cannot create a bypass because current entitlement is revalidated;
- Media outage returns safe temporary failure without corrupting usage truth;
- operators see safe failure/queue metrics;
- Privacy/retention and moderation paths remain correct;
- no reusable credential/sensitive payload leaks into logs/audit/notifications.

### Cluster Build-Plan Link

Implements the Digital Goods portion of **CL-05 Feature 15 — Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness**.

### Dependencies

- Features 01–10;
- production-capable Media signing/storage path;
- root security policy sufficiently final for Digital Goods sensitive actions;
- production legal decisions resolved or feature-flagged out of launch;
- real Audit/Observability/queue implementation;
- realistic seeded database/migration environment.

### In Scope

- load/concurrency testing;
- grant expiry/revocation sweeps;
- event inbox/outbox replay testing;
- rate/abuse protection through shared platform mechanisms if root architecture specifies them;
- safe operational metrics/logs/health checks;
- audit completeness review;
- migration/cascade/retention review;
- performance/index tuning;
- reconciliation for Digital Goods source effects where a concrete gap exists;
- production feature flags for unresolved legal/alternate-access behavior;
- final contract/E2E launch suite.

### Out of Scope

- new storage/payment/video providers;
- generic incident management UI;
- new access bases;
- new legal policy;
- architectural redesign unrelated to identified production risk.

### Module-Owned Data

Review/tune only existing Digital Goods models unless a documented production blocker requires a migration.

Key database concerns:

- grant expiry index;
- asset/status indexes;
- event query indexes;
- token-hash uniqueness if token lookup enabled;
- active/effective declaration control queries;
- retention-safe cascades;
- any proven idempotency/semantic uniqueness constraint.

### Public Interfaces

No new broad product interface by default. Harden:

- existing commands/queries under timeout/retry/load;
- authorized operational retry/replay where root Ops tooling provides it;
- health/readiness contributions.

### Shared Operations Used

Emphasize:

- SH-014 if approved step-up matrix requires it;
- SH-029/030 audit;
- SH-032–039 observability/health;
- SH-044–052 idempotency/event/queue/locking/concurrency;
- SH-055/057 expiration/counter;
- SH-072/074 crypto;
- SH-087–090 Media/grant contracts;
- SH-095–097 Privacy;
- SH-103 Moderation;
- SH-125 domain access event.

No hardening task may create a local substitute for these operations.

### Domain Logic

- access decisions never rely solely on stored `status=active`; check current time and required upstream facts;
- reconciliation repairs only Digital Goods facts that are safe to repair automatically;
- dead-letter state is operational, not grant/asset truth;
- unknown/unsafe discrepancy escalates through Ops/manual review rather than guessing;
- feature flags disable unresolved null-Order, legal-policy, child-auto-approval, accessibility-waiver, and external-storage behavior;
- all output reason codes remain stable under dependency errors.

### Authorization / Compliance

Security review verifies:

- actor/authority at every protected entry point;
- no grant ID/token bearer bypass;
- current Order/hold/moderation revalidation policy;
- least-privilege dependency calls;
- sensitive/admin step-up where approved;
- audit completeness for signed URL issuance/denial/download/revocation per policy;
- Privacy executor coverage;
- legal feature gates cannot be bypassed by environment/UI state.

### Database / Transaction Behavior

Stress-test:

- parallel final download count;
- grant access vs revoke;
- access vs expiry;
- duplicate issuance;
- duplicate terms acceptance;
- duplicate moderation/refund event;
- stale policy edit;
- cascade/product deletion with retention fixture;
- transaction rollback after Media temporary failure at each defined boundary.

Use Postgres/shared primitives only.

### Events / Jobs

- grant expiration sweep lag/throughput;
- bulk revocation replay/dead-letter;
- outbox publish retry;
- inbound event inbox replay;
- safe admin retry using existing idempotency.

### Provider Integration

Digital Goods tests Media provider degradation through Media’s public interface. It never directly reconciles R2/S3. If a delivery evidence mismatch exists, reconciliation compares Digital Goods event/grant truth to Media-provided safe evidence rather than provider payloads.

### UI / Admin Surface

- stable buyer failure states under dependency outage;
- support-safe event/grant view;
- Ops health/retry links through shared Ops UI if present;
- no raw provider payload/token dump.

### Failure Behavior

Explicitly test:

- Media unavailable/degraded/delayed;
- Search/Notification unavailable after source change;
- Order interface timeout vs business denial;
- expired grant before expiration worker;
- duplicate/reordered external event;
- dead-letter bulk revocation;
- Privacy partial failure;
- audit/telemetry sink failure according to root policy;
- retention migration rollback;
- unresolved legal feature accidentally enabled.

### Tests

- load/concurrency grant counter tests;
- authorization/RLS tests required by root architecture;
- idempotency/replay tests;
- log/audit/notification credential-leak scan;
- chaos/degradation tests using dependency adapters;
- outbox/inbox retry tests;
- Privacy retention/destructive tests;
- moderation/refund invalidation end-to-end;
- clean migration + realistic seeded migration tests;
- typecheck/lint/unit/integration/contract/concurrency/privacy/E2E/production build.

### Documentation Updates

- resolve/remove only those unresolved items actually decided;
- record production feature flags for still-deferred behavior;
- update progress tracker and final Module completion report;
- update SH registry only if implementation reveals a true canonical contract change.

### Acceptance Criteria

Digital Goods is production-ready only when:

- normal purchased download path has no entitlement/storage bypass;
- concurrency tests prove max use cannot be exceeded;
- current-time expiry and current entitlement checks prevent stale access;
- duplicate/reordered events/commands produce one semantic effect;
- no raw signed URL/token or prohibited sensitive payload appears in logs, audit metadata, notifications, or persisted domain evidence;
- Privacy/retention and moderation/refund paths pass end-to-end;
- destructive cascades are retention-safe;
- legal-gated unresolved behavior is resolved or disabled from launch;
- dependency outages are visible without corrupting source truth;
- all required quality suites pass.

### Exit Gate

Run and pass:

- production typecheck/lint/build;
- full unit suite;
- DB/integration suite;
- public contract suite;
- concurrency/load suite;
- idempotency/replay suite;
- privacy/retention suite;
- security credential-log scan;
- cross-Module E2E paid download, invalidation, and Privacy journeys;
- migration-from-clean and realistic-seed migration validation.

Any unresolved item that can enable unsafe production behavior must be explicitly feature-flagged out or resolved by binding architecture decision before this exit gate may pass.

---

# Module Integration Phase — Contract Proof Matrix

The Module integration requirement is satisfied across Features 08–09. The final contract suite must prove the following without direct foreign database access:

| Neighbor | Contract proof required |
| --- | --- |
| Marketplace Supply | Offering/Product/Course target/ownership validation and consumption of Digital Goods readiness |
| Transaction / Order | SH-025 normal purchased access allow/deny/refund/dispute effects |
| Customer / Buyer Profile | authenticated User resolves to correct buyer context for qualifying Order |
| Consent & Disclosure | generic proof/version linkage without replacing DigitalGoodsTermsAcceptance |
| Media / File Access | Media readiness + composite requestMediaAccess (SH-087 internal); Digital Goods owns contextual SH-090 attachment; no local provider code |
| Video Session | Video owner validates canonical course/Offering relationship for accessibility; Digital Goods supplies SH-026 playback permission; no repository reads/provider leakage or Video-side policy interpretation |
| Compliance Hold | SH-011 mapped denial without local hold truth |
| Moderation | SH-103 action → owner-local disable/restore/revoke + acknowledgment |
| Search | SH-091 only; no Typesense/SearchUpsertEvent direct writes |
| Notification | SH-041 safe request; delivery failure does not roll back source truth |
| Audit / Event Ledger | DigitalDownloadEvent remains separate from AuditEvent/AccessAuditLog |
| Privacy | SH-095–097 inventory/retention/execution without local Privacy lifecycle |
| Observability / Ops | failures/queue/health recorded operationally without becoming Digital Goods status |

---

# Module Hardening Phase — Required Production Checks

Feature 11 must explicitly verify these Digital Goods-specific hardening areas:

- grant issuance idempotency;
- grant counter race safety;
- access/revoke/expiry race safety;
- server-time expiry independent of worker timing;
- current Order/hold/asset revalidation;
- stale policy/version acceptance;
- source-event dedupe/reorder;
- Media signing outage and recovery;
- no direct provider imports;
- no token/URL/log leakage;
- retention-safe product deletion/cascades;
- Privacy inventory completeness;
- moderation/refund revocation coverage;
- audit-event separation/completeness;
- legal feature-gate enforcement;
- performance of buyer library, active grant lookup, expiry sweep, delivery-evidence queries;
- migration/backfill behavior if a retention/token/effective-state constraint is added.

---

## Phase Summary

| Phase | Name | Features |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | **01** Module Contracts, Schema Guardrails, and Ownership Enforcement; **02** Digital Goods Policy and Versioned Terms Evidence |
| 2 | Core Download Lifecycle and Public Delivery | **03** Download Asset Registration and Readiness; **04** Purchased Grant Issuance and Buyer Download Library; **05** Controlled Download Access, Usage, Expiration, and Domain Evidence |
| 3 | Child-Directed Controls and Accessibility | **06** Child-Directed Declaration and Minor Privacy Controls; **07** Course Accessibility Asset Tracking and Readiness |
| 4 | Module Integration and Guardrail Effects | **08** Core Neighbor Contract Verification; **09** Entitlement Loss, Refund, Moderation, Hold, Search, and Notification Bridge |
| 5 | Privacy and Production Hardening | **10** Privacy Inventory, Retention Facts, and Target Execution; **11** Concurrency, Security, Audit, Performance, and Production Verification |

**Total numbered Module features: 11.**

### Cluster mapping

| Module feature | CL-05 feature(s) supported |
| --- | --- |
| 01 | foundation for 03–05, 13–15 |
| 02 | CL-05 03 |
| 03 | CL-05 04, depends on CL-05 01 |
| 04 | CL-05 04 |
| 05 | CL-05 04, depends on CL-05 02 |
| 06 | CL-05 05 |
| 07 | CL-05 05; consumed by CL-05 06 |
| 08 | integration proof across CL-05 03–06 |
| 09 | CL-05 13 |
| 10 | CL-05 14 |
| 11 | CL-05 15 |

The Module plan must not cause Digital Goods Feature 02–07 to run ahead of the relevant CL-05 prerequisite or global dependency simply because the local code is ready.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture/standards.
2. Read the Canonical Shared Operations Registry.
3. Read CL-05 architecture and build plan.
4. Read Digital Goods `module-architecture.md` and this plan.
5. Read public-interface sections for the direct dependencies named by the feature.
6. Read `progress-tracker.md` and the prior feature completion report.
7. Confirm the previous Module exit gate and relevant CL-05 prerequisite exit gate.
8. Check Module architecture unresolved decisions for any issue touched by the feature.
9. Write the concise Required Feature Implementation Specification below.
10. Implement only the numbered feature.
11. Run the required quality checks and failure-path verification.
12. Verify public contracts rather than inspecting neighboring tables directly.
13. Update progress.
14. Update architecture only when a binding decision legitimately changes.
15. Record unresolved risks/deferred legal/provider work.

Do not start adjacent “helpful” work because files or schemas are nearby.

---

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise specification containing:

- **Feature:** number and name;
- **Objective:** one result;
- **Observable result:** what will work/be visible/testable;
- **Cluster build-plan link:** exact CL-05 feature/milestone;
- **Dependencies:** prior Module features, CL-05 prerequisites, owner public interfaces, SH operations, providers if any;
- **In scope:** explicit files/behavior for this feature only;
- **Out of scope:** neighboring responsibilities and deferred decisions;
- **Owned data affected:** models/enums/events/projections/snapshots;
- **Public contracts:** commands, queries, events, Privacy/executor contracts;
- **Shared operations consumed:** SH ID, owner, invocation, local policy, prohibited duplicate;
- **Permissions/compliance:** actor, authority, buyer/owner context, consent, Order entitlement, hold, moderation, Privacy/legal gates;
- **Primary workflow:** success path from validated entry to source truth/effects;
- **Provider integration:** owner port only; “none” where not applicable;
- **Jobs/events:** outbox/inbox, queue, retry, dead-letter, correlation;
- **Idempotency/concurrency:** semantic key, transaction, lock/counter/stale-write behavior;
- **Error behavior:** validation, authorization, conflict, denial, temporary failure, retry/manual review;
- **Privacy/retention:** relevant subject fields/disposition;
- **Audit/observability:** domain evidence vs generic audit vs safe telemetry;
- **Tests:** exact unit/integration/contract/concurrency/privacy/E2E categories;
- **Acceptance criteria:** observable binary requirements;
- **Documentation updates:** only documents affected by a real decision/contract change.

Do **not** generate specifications for all 11 features in advance. The plan above is the durable sequence; the feature specification is created when that feature is the active work item.

---

# Required Completion Report

After implementing each feature, the coding agent must report:

- Feature completed;
- Observable result verified;
- Files added;
- Files changed;
- Database changes;
- Migrations/constraints/indexes added or changed;
- Dependencies added;
- Module public interfaces added/changed;
- Dependency Module contracts consumed;
- Shared operations reused, by SH-### ID;
- Events/outbox/inbox handlers added;
- Jobs/workers/schedules added;
- Provider adapter changes (**should normally be none inside Digital Goods**);
- Tests added/changed;
- Commands run;
- Manual/contract/E2E verification performed;
- Documentation updated;
- Assumptions made;
- Known failures;
- Remaining architecture/legal risks;
- Deferred work;
- Cluster prerequisite/sequence status;
- Exit-gate result: PASS / BLOCKED / APPROVED EXCEPTION.

If blocked, state the exact unresolved decision or dependency and do not describe the feature as complete.

---

# Final Quality Check

Before treating this Module plan as implementation-ready, verify:

1. Every Digital Goods lifecycle has one owner.
2. Marketplace Offering truth was not absorbed.
3. Order/payment/refund truth was not absorbed.
4. Media file/storage/signing truth was not absorbed.
5. Video streaming/provider truth was not absorbed.
6. Generic ConsentType/ConsentLog truth was not absorbed.
7. Every shared operation is referenced by SH ID rather than duplicated.
8. Temporary grant mechanics remain shared while DigitalDownloadGrant stays separate truth.
9. DigitalDownloadEvent, generic audit, and observability remain distinct.
10. Cross-Module reads/commands use public interfaces/events.
11. Search remains projection and Notification remains delivery rail.
12. Privacy orchestration and retention exemptions remain Privacy-owned.
13. Legal-gated decisions are explicit blockers/feature flags rather than guessed behavior.
14. CL-05 Features 01–02 are respected as prerequisites to the corresponding digital download work.
15. Module Features 02–07 align with CL-05 Features 03–05 rather than creating a parallel Cluster plan.
16. Integration proof covers Marketplace, Order, Consent, Media, Video, Hold, Moderation, Search, Notification, Audit, Privacy, and Ops where relevant.
17. Concurrency/idempotency rules use database/shared primitives, not in-memory shortcuts.
18. Every numbered feature contains tests and a concrete exit gate.
19. A coding agent can implement each feature without inventing architecture.
20. Any remaining unresolved decision is visible in `module-architecture.md` and cannot silently activate in production.
