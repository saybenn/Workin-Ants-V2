# Trust Verification / Screening Module Architecture

> **Module ID:** `trust_verification_screening`  
> **Module name:** Trust Verification / Screening Module  
> **Module type:** `compliance_trust_capability`  
> **Build status:** `mvp_active_legal_gated`  
> **Primary Cluster:** `CL-03 — Professional Supply & Readiness`  
> **Repository target:** `context/modules/trust-verification-screening/module-architecture.md`  
> **Document status:** Implementation-grade Module architecture. Confirmed rulings are binding; Proposed Rulings require approval before schema/API commitment; Unresolved items are non-implementable where stated.

## 1. Module Header

### Intended audience

Coding agents, developers, reviewers, maintainers, architecture reviewers, compliance reviewers, and operators implementing or changing Workin Ants verification and screening behavior.

### Relationship to root architecture

This document is subordinate to the root Workin Ants architecture, project overview, code standards, and Canonical Shared Operations Registry. Root decisions about authentication, authorization, persistence, events, queues, privacy orchestration, audit, observability, media, search, and deployment are inherited rather than redefined here.

The current evidence supplied to this Module task includes the root `project-overview.md`; a current root `architecture.md` or `code-standards.md` was not supplied as a current-conversation artifact. Implementers must still read the repository-current versions before coding.

### Relationship to Cluster architecture

This document specializes `CL-03 — Professional Supply & Readiness` for the `trust_verification_screening` Deep Module. The Cluster architecture is authoritative for cross-Module boundaries and build sequencing. This Module architecture is more specific and authoritative for Trust-owned records, policies, transitions, provider adapters, workers, contracts, and internal behavior.

The Cluster is not an aggregate owner. No `ProfessionalSupplyReadiness` or CL-03 verification repository is created here.

### Update rule

When a binding ownership, lifecycle, public contract, schema, provider, compliance-proof, privacy, or shared-operation decision changes, update this file before or in the same change as implementation. A build task, provider integration, migration, or admin UI may not silently redefine Module architecture.

### Evidence basis

This document is derived from the current:

- Target Module Architecture Extract in this thread;
- Deep Module Registry;
- Cluster Registry v2.3;
- Prisma schema;
- Ubiquitous Language / Compliance Inventory;
- Canonical Shared Operations Architecture / Registry;
- CL-03 `architecture.md`;
- CL-03 `build-plan.md`;
- Workin Ants `project-overview.md`;
- direct boundary evidence for Professional Eligibility, Consent & Disclosure, Taxonomy & Classification, Transaction / Order, Media / File Access, Admin Review / Compliance Hold, Search / Public Visibility, Audit / Event Ledger, Privacy / Data Erasure, Notification, and Observability / Ops.

### Evidence labels

- **Confirmed** — directly established by supplied architecture, schema, registry, glossary, or compliance evidence.
- **Proposed Ruling** — required or strongly supported architecture direction that still needs explicit approval before irreversible schema/API commitment.
- **Unresolved** — evidence establishes the problem but not a safe final design. Affected production behavior stays disabled or constrained.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Trust Verification / Screening owns Workin Ants marketplace and work-platform trust screening: which checks are required, which screening attempt occurred, what canonical result Workin Ants recognizes, which professional credential is current, whether an FCRA adverse-action workflow is in progress, and which TrustBadge projection may be displayed.

It exists so background screening, professional-license verification, DMV/MVR verification, identity-oriented trust checks, child-safety checks, and related high-risk gates do not collapse into `User`, `ProfessionalProfile`, payment KYC, Search ranking, provider payloads, or scattered `isVerified` booleans.

### Goal

For an authorized subject and target context, the Module must be able to answer:

```text
Which verification requirements apply?
Which current Trust-owned evidence satisfies each requirement?
Which evidence is missing, pending, expired, revoked, failed, or under review?
What legally gated workflow must occur before a negative background result can restrict eligibility?
Which safe public trust projection, if any, may be displayed?
```

### What enters

- authenticated User/system actor context;
- Role / Authority decision and owner/context facts;
- `ProfessionalProfile` or `CandidateProfile` identity/context supplied through owner interfaces;
- accepted taxonomy and target facts for category, tag, Offering, Gig, or Job contexts;
- canonical standalone consent proof from Consent & Disclosure;
- verification package configuration and fee policy;
- authoritative screening-fee Order result when a paid check applies;
- provider-hosted collection references and provider events;
- validated private MediaAsset/evidence context when local credential documents are permitted;
- manual reviewer decision/evidence;
- current time/deadline input for expiry and recheck;
- active ComplianceHold facts where an action is hold-sensitive;
- Privacy-owned erase/anonymize/retain/export instructions.

### What leaves

- `VerificationRequirement` truth describing required checks;
- `VerificationCheck` truth describing each screening attempt/result;
- `ProfessionalLicenseCredential` truth describing durable license/credential state;
- `VerificationPackage` and `VerificationPackageItem` configuration and quote facts;
- `FcraAdverseActionWorkflow` state where applicable;
- `TrustBadge` display projection;
- `resolveVerificationRequirements` and `evaluateVerificationReadiness` decisions;
- safe verification evidence summaries for downstream gates;
- versioned domain events and downstream requests for reevaluation, Search refresh, Notification, Audit, Hold, and operational handling;
- provider reconciliation and expiry/recheck work.

### Capability transformation

```text
accepted target/taxonomy context
→ Trust requirement resolution
→ standalone consent + optional chargeable Order gate
→ canonical VerificationCheck created before provider side effect
→ provider/manual evidence verified and translated
→ Trust-owned check/credential state transition
→ FCRA workflow if the result can produce an adverse restriction
→ TrustBadge and readiness projection updated only when supported by current evidence
→ downstream owners re-evaluate their own actions
```

### Why this is a separate Module boundary

Verification has its own legal proof, vendor integration, status vocabulary, expiry, recheck, credential, adverse-action, and public-projection semantics. Those responsibilities are materially different from:

- account authentication and recovery;
- professional selling-readiness composition;
- payout KYC and tax;
- healthcare/BAA readiness;
- Offering/Gig/Job lifecycles;
- Search ranking;
- Media file safety;
- generic holds, audit, notifications, and privacy orchestration.

Keeping Trust separate allows those Modules to consume a stable verification decision without importing provider semantics or becoming co-owners of screening truth.

---

## 3. Owned Truth

### 3.1 Models / records owned

| Record | Plain-English meaning | Ownership status |
| --- | --- | --- |
| `VerificationRequirement` | A rule declaring which verification check is required for a target/context and subject type. | Confirmed |
| `VerificationPackage` | A configured screening bundle, including provider, platform fee, disclosure text, currency, and lifecycle. | Confirmed |
| `VerificationPackageItem` | A check-type/cost line item inside a verification package. | Confirmed |
| `VerificationCheck` | The canonical Workin Ants record for one trust/background/DMV/license/identity screening attempt and result. | Confirmed |
| `VerificationConsent` | Screening-specific consent linkage/context if retained. It must not become generic consent-version proof. | Confirmed record; exact field authority Unresolved U-03 |
| `FcraAdverseActionWorkflow` | The Trust-owned pre-adverse/dispute/final-adverse workflow state attached one-to-one to a check. | Confirmed; production automation legal-gated |
| `ProfessionalLicenseCredential` | The durable professional-license/credential state for a User/ProfessionalProfile. | Confirmed; provenance to check Unresolved U-05 |
| `TrustBadge` | A profile-facing trust display projection derived from current approved Trust evidence. | Confirmed projection |

### 3.2 Enums and controlled vocabulary owned

- `VerificationRequirementTargetType`
  - `taxonomy_category`
  - `taxonomy_tag`
  - `offering`
  - `gig`
  - `job`
- `VerificationSubjectType`
  - `user`
  - `professional_profile`
  - `candidate_profile`
- `VerificationCheckType`
  - `identity`
  - `background`
  - `professional_license`
  - `dmv`
  - `child_safety`
  - `healthcare_credential`
  - `financial_trust`
  - `other`
- `VerificationCheckStatus`
  - `not_started`
  - `consent_required`
  - `pending`
  - `passed`
  - `failed`
  - `needs_review`
  - `expired`
  - `revoked`
  - `cancelled`
- `VerificationVendor`
  - `checkr`
  - `goodhire`
  - `evident_id`
  - `certn`
  - `stripe_identity`
  - `persona`
  - `manual`
  - `other`
- `VerificationPackageType`
  - `identity_verified`
  - `background_checked`
  - `trades_or_driver`
  - `healthcare_or_license`
  - `custom`
- `VerificationPackageStatus`
  - `draft`
  - `active`
  - `paused`
  - `retired`
- `FcraAdverseActionStatus`
  - `not_applicable`
  - `pre_adverse_required`
  - `pre_adverse_sent`
  - `dispute_window`
  - `disputed`
  - `cleared_after_dispute`
  - `final_adverse_sent`
  - `restricted`
  - `cancelled`
- `ProfessionalLicenseStatus`
  - `not_started`
  - `pending`
  - `verified`
  - `failed`
  - `expired`
  - `revoked`
  - `needs_review`
- `TrustBadgeType`
  - `identity_verified`
  - `background_checked`
  - `licensed_professional`
  - `trades_verified`
  - `dmv_checked`
  - `healthcare_verified`
  - `child_safety_checked`
  - `gold_trust_check`
  - `platform_verified`
- `TrustBadgeStatus`
  - `active`
  - `expired`
  - `revoked`
  - `suspended`

The broad `financial_trust`, `healthcare_verified`, `gold_trust_check`, and `platform_verified` vocabulary requires narrow issuance/meaning rules. It may not be used to absorb Payment KYC, Healthcare readiness, or unspecified platform approval.

### 3.3 Lifecycles owned

- requirement activation/deactivation policy;
- verification package lifecycle;
- verification check lifecycle;
- professional-license credential lifecycle;
- FCRA adverse-action workflow lifecycle;
- TrustBadge lifecycle/projection policy;
- check/license expiration and recheck initiation policy.

### 3.4 Source-of-truth hierarchy

1. `VerificationRequirement` says **what is required**.
2. `VerificationCheck` says **what check occurred and its canonical current result**.
3. `ProfessionalLicenseCredential` says **what durable license/credential is currently recognized**.
4. `FcraAdverseActionWorkflow` says **what legally gated adverse-action process state exists**.
5. `TrustBadge` says **what may be displayed**, not whether the underlying check is true.
6. `ConsentLog` from Consent & Disclosure remains the canonical generic versioned acceptance proof; Trust only owns screening-specific linkage/context if `VerificationConsent` is retained.

### 3.5 Domain events / ledgers owned

The supplied Prisma schema does not currently define a Trust-specific lifecycle event ledger or processed-provider-event record.

**Confirmed rule:** `AuditEvent` is not a substitute for Trust domain event truth, and `lastProviderEventId` is not sufficient provider-event dedupe truth.

**Proposed Ruling TV-PR-01:** Trust requires owner-specific processed-provider-event truth before production webhook side effects. It may reuse SH-060 mechanics but must not reuse `ProcessedStripeEvent`, `AuditEvent`, or another Module's provider-event record. This inherits CL-03 PR-09 / U-04.

**Proposed Ruling TV-PR-02:** Trust lifecycle facts that require reliable cross-Module reaction are published through the canonical transactional outbox (SH-046). A separate `VerificationCheckEvent` table should be added only if legal/audit/product requirements require owner-specific immutable lifecycle history beyond the outbox and existing records. Generic `AuditEvent` does not decide this.

### 3.6 Projections owned

- `TrustBadge` is the primary confirmed Trust projection.
- Trust may build a safe source projection DTO for Search or profile display, but Search owns `SearchUpsertEvent`, indexing, ranking, reconciliation, and query surfaces.
- `ProfessionalProfile.verifiedAt`, `verificationExpiresAt`, and `trustScore` are not Trust source truth. If they remain in schema for compatibility, they are non-authoritative derived fields and must not be read to satisfy a gate.

### 3.7 Snapshots / compliance proof owned

- check provider identifiers and canonical status/timestamps;
- check fee/cost snapshots (`vendorCostCents`, `platformFeeCents`, `totalFeeCents`) for the check instance;
- check report summary code where approved and minimized;
- adverse-action workflow timestamps and provider workflow reference;
- license masked/hash identifiers, jurisdiction, provider reference, verification/expiry state;
- badge issuance/expiry/revocation proof.

The exact FCRA notice artifact/version/delivery/retention proof is Unresolved U-06. Production adverse-action automation must not claim compliance until that proof model and transition policy are approved.

### 3.8 Policies / invariants owned

Trust owns:

- requirement applicability and completion policy;
- which check type/vendor/package satisfies which Trust requirement;
- consent sufficiency for initiating a particular screening workflow, while Consent owns acceptance proof;
- canonical provider-to-Trust status mapping;
- manual-review decision policy;
- check and credential expiration/recheck policy;
- TrustBadge issuance/invalidation policy;
- the rule that failed background checks do not directly trigger a business ban when adverse-action handling applies;
- the distinction between Trust screening and payout KYC/account recovery identity proof/Healthcare readiness;
- minimization rules for Trust-specific provider data and evidence exposure.

---

## 4. Explicit Non-Ownership

The following responsibilities must not be implemented as Trust-owned truth or infrastructure.

| Adjacent owner | Trust may consume | Trust must not own or duplicate |
| --- | --- | --- |
| Identity & Access | authenticated/system actor context; step-up if root policy later requires a specific high-risk Trust admin action | User identity, login/session, MFA/passkeys, account recovery, recovery identity proof |
| Role / Authority | authorization decision | platform/org permission interpretation, local `isAdmin`/role engine |
| Consent & Disclosure | active consent version, standalone presentation, canonical `ConsentLog` proof | generic consent catalog, acceptance proof lifecycle, consent booleans/tables |
| Professional Eligibility | `ProfessionalProfile` owner facts and downstream seller-readiness composition | ProfessionalProfile lifecycle, seller activation, publish/respond final composition |
| Candidate Application & Resume Privacy | CandidateProfile/application context | candidate application lifecycle, resume access lifecycle |
| Organization Hiring | Job/organization/request context | Job lifecycle, organization membership, hiring decision |
| Taxonomy & Classification | accepted taxonomy and requirement triggers | taxonomy vocabulary, local category-to-check hardcoding |
| Transaction / Order | chargeable screening Order and authoritative transaction state | screening payment subsystem, Order status, refund lifecycle |
| Payment / Payout / Tax | only indirect transaction/payment rail outcomes when needed through Order | KYC/AML, tax, payout account, payout transfer, Stripe webhook truth |
| Healthcare / Regulated Services | possible credential evidence input/output boundary | BAA, HealthcareComplianceProfile, healthcare data boundary, HIPAA readiness |
| Media / File Access | validated ready MediaAsset and short-lived access | upload validation, malware scan, object storage, presigned/signed URL infrastructure |
| Admin Review / Compliance Hold | active holds; request/release commands | ComplianceHold lifecycle, generic blocked flags |
| Search / Public Visibility | projection refresh command | SearchUpsertEvent, Typesense adapter, ranking execution, search query surfaces |
| Notification | delivery request | SES/SMS/push provider clients, Notification/Delivery lifecycle |
| Audit / Event Ledger | append generic audit/sensitive access proof | generic AuditEvent/AccessAuditLog tables; Trust lifecycle truth in audit logs |
| Privacy / Data Erasure | privacy instructions and retention orchestration | PrivacyRequest/DataErasureJob/DataRetentionExemption lifecycle |
| Observability / Ops | integration-failure/system-event/queue telemetry | operational records as verification truth |

Additional prohibitions:

- no `isVerified`, `backgroundPassed`, `licenseVerified`, `verifiedOnly`, `trustPassed`, or local eligibility boolean as source truth;
- no reuse of `KycVerification` for marketplace screening;
- no use of `VerificationCheck` as payout KYC or account-recovery proof;
- no permanent public URLs for ID/license/background evidence;
- no direct Typesense writes;
- no direct `ComplianceHold.status` writes;
- no direct `Order.status` writes;
- no local provider secrets in database/domain records;
- no raw SSNs or complete background reports in ordinary Workin Ants application tables;
- no automatic employment/seller rejection from an unreviewed provider failure or unknown status.

---

## 5. Module Architecture Principles

1. **VerificationCheck is screening truth. TrustBadge is display.** A badge can never satisfy a requirement by itself.
2. **Requirement resolution is not readiness.** SH-017 answers what is required; SH-018 answers whether current Trust evidence satisfies it.
3. **Consent is canonical elsewhere.** Trust evaluates whether canonical consent proof is sufficient for the current check; it does not own generic proof/versioning.
4. **Provider payload is evidence, not domain state.** All external state is verified, deduplicated, translated, transition-validated, and minimized before affecting Trust records.
5. **Create local check truth before external side effect.** Provider submission must have a canonical local check/correlation record first.
6. **Payment never equals verification.** A paid screening Order permits ordering the check; it does not mark the check passed.
7. **Failed background result is not an automatic ban.** Where FCRA or another approved process applies, the adverse-action workflow must run before final restriction.
8. **Professional license truth is separate from file safety.** A clean MediaAsset is not a verified credential.
9. **Payout KYC is separate.** Same provider technology may be reused behind separate adapters, but records, purpose, consent, status, retention, and policy remain separate.
10. **Healthcare credential verification is not healthcare readiness.** Healthcare owns BAA/HIPAA lane decisions.
11. **Provider-event dedupe is owner-specific truth.** Shared mechanics do not merge Trust, Payment, Calendar, Video, or Healthcare provider-event ledgers.
12. **Public consumers get minimized evidence.** Raw reports, provider payloads, tokens, SSNs, full license numbers, and unnecessary PII never cross public Module contracts.
13. **Expiry invalidates derived state.** An expired/revoked underlying proof must cause readiness and applicable badges to be reevaluated.
14. **Consumers do not reconstruct policy.** Marketplace, Hiring, Search, and Professional Eligibility consume Trust contracts; they do not interpret raw provider status or direct Prisma rows.
15. **Legal-gated paths fail closed.** Unresolved FCRA proof/retention/provider rules stay disabled rather than approximated.
16. **Idempotency prevents effects, not only duplicate rows.** Replayed initiation, webhooks, review commands, expiry jobs, badge issuance, and hold requests must be safe.
17. **Audit and observability remain secondary evidence.** They cannot replace source state or provider-event dedupe truth.
18. **No destructive privacy action without retention decision.** Privacy orchestrates; Trust executes approved owner-specific behavior.

---

## 6. Proposed Folder / Code Structure

The exact repository root is inherited from root Workin Ants architecture. Until a different root convention is binding, use the CL-03 owner-preserving structure:

```text
src/
  modules/
    trust-verification-screening/
      application/
        commands/
        queries/
        services/
      domain/
        policies/
        lifecycles/
        reason-codes/
      contracts/
        public/
        events/
        providers/
        privacy/
      infrastructure/
        repositories/
        providers/
          checkr/
          certn/
          manual/
        persistence/
      workers/
        provider-reconciliation/
        verification-expiry/
        recheck/
        adverse-action-deadline/   # enabled only for approved legal subset
      admin/
        # only if the repository's route/UI conventions place restricted
        # module-owned review surfaces adjacent to the module
      tests/
        unit/
        contract/
        integration/
        authorization/
        provider/
        concurrency/
        privacy/
```

### Folder rules

- `application/commands` coordinates mutations; it does not contain provider SDK types.
- `application/queries` returns owner-safe DTOs/decisions; it does not expose Prisma models directly.
- `domain/policies` owns requirement satisfaction, badge issuance, manual-review, expiry, and transition rules.
- `domain/lifecycles` contains Trust transition graphs/reason validation only; generic transition plumbing comes from SH-053.
- `contracts/public` contains SH-017/018 and other stable Module interfaces.
- `contracts/providers` defines provider-neutral ports and normalized results.
- `infrastructure/providers/<provider>` is the only place provider-specific request/response/status vocabulary may exist.
- `infrastructure/repositories` accesses only Trust-owned records by default. Cross-Module facts come through public contracts.
- `workers` contains Trust-owned business job handlers, not a custom queue framework.
- `contracts/privacy` implements SH-095/096/097 owner protocols; it does not create a privacy workflow.
- generic auth, queues, idempotency, telemetry, crypto, Search, Media, Notification, and Audit infrastructure remain outside this Module.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / route / admin UI | Parse/validate request shape, invoke application service, render safe status/remediation | lifecycle transitions, provider mapping, direct Prisma workflows, permission logic |
| Application commands | Transaction orchestration for one Trust-owned business command; shared-op calls; owner writes; outbox requests | provider SDK semantics, foreign-owner row writes, generic queue/auth/audit infrastructure |
| Application queries | Public DTOs, evidence minimization, Trust decisions | Search ranking, Professional final readiness composition, raw provider reports |
| Domain policies | requirement applicability/completion, check transition rules, manual review, expiry, badge projection, FCRA owner policy once approved | general authorization, generic consent proof, Payment/Healthcare policy |
| Repositories | Trust-owned models, transaction-scoped persistence, owner-specific provider-event truth if approved | universal repository, direct cross-Module Prisma reads as default integration |
| Workers | expiry/recheck/reconciliation/adverse-action deadline business logic | queue engine, generic retry/dead-letter infrastructure |
| Provider ports | normalized screening/credential capabilities and error categories | provider-specific status enum leaking into domain/public contracts |
| Provider adapters | Checkr/Certn/manual provider calls, signature metadata, provider mapping | Trust readiness policy, consumer business actions |
| Public contracts | stable commands/queries/events and reason codes | implementation details, Prisma types, raw vendor payloads |
| Privacy executor | enumerate/execute/retention facts for Trust-owned data/providers | PrivacyRequest orchestration, retention-exemption record lifecycle |

---

## 8. Data Model

### `VerificationRequirement`

**Purpose:** declares that a `VerificationCheckType` applies to a typed target and subject, including currently modeled publish/apply/ranking contexts.

**Key relationships:** optional `VerificationPackage`; many `VerificationCheck` records.

**Authoritative fields:** `targetType`, `targetId`, `subjectType`, `checkType`, `requiredForPublish`, `requiredForApply`, `requiredForRankingBoost`, `vendor`, `validityDays`, `feeCents`, `currency`, `verificationPackageId`, `requiresPaidScreening`, `isActive`, `ruleJson`.

**Lifecycle:** no formal status enum; `isActive` is current activation state.

**Constraints / risks:**

- `targetType + targetId` is polymorphic and has no database foreign key to the external owner. Use SH-123 owner validation rather than a generic polymorphic Prisma lookup.
- current action flags do not cover every possible gate such as Gig response/assignment/booking; do not hide new action semantics in `ruleJson` without an approved contract.
- `ruleJson` must be schema-versioned/validated if used; it cannot become an untyped legal-policy dumping ground.
- destructive deletion after checks depend on a requirement should be avoided; use deactivation unless an approved migration says otherwise.

**Retention/privacy:** requirement policy is generally not personal data, but target IDs and legal/policy versions may need durable history to explain historical checks.

### `VerificationPackage`

**Purpose:** configurable screening bundle with one package-level provider, fee policy, and disclosure text.

**Key relationships:** many items, requirements, and checks.

**Authoritative fields:** `type`, `status`, `name`, `description`, `vendor`, `platformFeeCents`, `currency`, `nonRefundable`, `disclosureText`.

**Concurrency:** activation/pause/retire and item edits must use expected state/locking. Active package edits that would rewrite historical pricing are prohibited; check-level fee fields snapshot the purchased check.

**Unresolved:** package-level `vendor` implies one provider per package. Multi-provider bundle semantics are not established; do not implement mixed-provider packages without an architecture ruling.

### `VerificationPackageItem`

**Purpose:** package line item for a check type and provider cost.

**Authoritative fields:** `checkType`, `label`, `vendorCostCents`, `estimated`, `displayOrder`.

**Rule:** package quote is composed from item costs plus approved platform fee; do not hardcode onboarding bundle prices elsewhere.

### `VerificationConsent`

**Purpose:** supplied schema describes a screening-specific consent linkage for User/subject/check/vendor.

**Key relationships:** `User`, optional canonical `ConsentLog`.

**Current fields:** `userId`, `consentLogId`, `subjectType`, `subjectId`, `checkType`, `vendor`, `acceptedAt`, `ipHash`, `userAgent`.

**Conflict:** `acceptedAt`, `ipHash`, and `userAgent` overlap canonical `ConsentLog` proof fields while Consent & Disclosure is the generic versioned proof owner.

**Unresolved U-03:** whether this record remains and which fields are linkage versus duplicate proof.

**Binding implementation constraint until resolved:**

- `ConsentLog` is the authority for generic acceptance/version proof;
- Trust may persist only the minimum screening linkage approved by the feature/ADR;
- duplicated fields cannot independently establish consent validity;
- no new Trust-specific consent catalog/version lifecycle may be introduced.

### `VerificationCheck`

**Purpose:** canonical screening attempt/result.

**Key relationships:** required `User`; optional ProfessionalProfile, CandidateProfile, requirement, ConsentLog, VerificationPackage, screening-fee Order; optional one-to-one FCRA workflow; many TrustBadges.

**Authoritative fields:** `type`, `status`, `vendor`, provider IDs, summary code, cost snapshots, non-refundable acceptance timestamp, ordered/completed/failed/expiry timestamps and failure reason.

**Sensitive fields:** `reportToken` must be treated as secret/opaque provider access material unless architecture proves otherwise. It must never be returned through normal public DTOs, logs, analytics, or Search.

**Concurrency-sensitive operations:** initiation/recheck, provider callback, manual review, cancellation, expiry/revocation, adverse-action start.

**Current schema gaps:**

- no owner-specific provider-event dedupe ledger;
- no version/CAS field;
- no direct `subjectType` on check;
- no unique active-check constraint;
- `lastProviderEventId` cannot safely prove full dedupe history.

Application code must use transactional expected-state/aggregate-lock semantics. Any new uniqueness/version schema must be approved against legitimate recheck requirements.

### `FcraAdverseActionWorkflow`

**Purpose:** one-to-one legal-gated adverse-action workflow for a `VerificationCheck`.

**Authoritative fields:** `status`, `preAdverseSentAt`, `disputeWindowEndsAt`, `disputedAt`, `finalAdverseSentAt`, `restrictedAt`, `providerWorkflowId`, minimized `notes`.

**Uniqueness:** `verificationCheckId` is unique.

**Legal gap U-06:** current schema does not prove immutable notice artifact/version/content, recipient/delivery proof, or exact legally approved transition/timing rules. Automated production adverse action is blocked until resolved.

### `ProfessionalLicenseCredential`

**Purpose:** durable current license/credential state independent from the individual file and independent from Healthcare lane readiness.

**Authoritative fields:** status, license type/jurisdiction, masked/hash identifier, vendor/provider reference, verified/expiry/failure timestamps.

**Security:** full license identifiers should not be retained unless legally/business-required; use approved shared normalize/hash/encryption primitives. Mask/hash values must not be reversible by accidental logging.

**Unresolved U-05:** there is no explicit relation to the `VerificationCheck` that established/refreshed the credential. Implementers may not invent provenance in `notes`/JSON. A durable provenance claim requires an approved relation or immutable reference contract.

### `TrustBadge`

**Purpose:** safe profile-facing display projection.

**Key relationships:** User, optional ProfessionalProfile or CandidateProfile, optional VerificationCheck.

**Authoritative projection fields:** `type`, `status`, `label`, issued/expiry/revocation timestamps and revoke reason.

**Rule:** a badge is never the source for check completion. Active badge issuance must have approved provenance. When supporting evidence expires/revokes, the badge must be reevaluated and normally expired/suspended/revoked according to Trust policy.

**Unresolved:** exact meaning/issuance for broad types (`gold_trust_check`, `platform_verified`, `healthcare_verified`) must be documented before use.

### Proposed Trust provider-event record

No current Prisma model is binding. If U-04/CL-03 PR-09 is approved, the smallest acceptable owner record should preserve:

- provider;
- provider event ID with uniqueness per provider;
- received/claimed time;
- safe event type;
- payload hash/integrity reference or minimized fingerprint;
- processing status/result/version;
- correlation to Trust check/credential where known;
- failure/retry metadata safe for domain use;
- retention class.

It must not store full sensitive background payloads by default and must not be shared with Payment or Healthcare as their domain truth.

---

## 9. Enums, Statuses, and Lifecycles

The schema confirms vocabulary but not every transition adjacency. The graphs below are **Proposed Module transition rulings** unless the transition is directly compelled by schema/workflow evidence. A feature specification must ratify the exact allowed transitions before coding them.

### 9.1 Verification requirement activation

```text
active (isActive=true)
  └─→ inactive (isActive=false)
       └─→ active only through explicit admin reactivation policy
```

- **Transition owner:** Trust admin/application policy.
- **Trigger:** approved requirement configuration change.
- **History:** requirement changes must emit owner event/audit proof when they can alter readiness.
- **Shortcut prohibited:** deleting a referenced requirement to make a subject appear ready.

### 9.2 Verification package

Proposed graph:

```text
draft → active ↔ paused → retired
  └──────────────→ retired
```

- `retired` is treated as terminal for new purchases/checks.
- historical checks retain package/cost snapshots.
- active package edits must not rewrite historical check fees.
- reactivating `retired` is prohibited unless later approved; create a new/versioned package instead.

### 9.3 Verification check

Proposed minimum graph:

```text
not_started
  ├─→ consent_required
  ├─→ pending
  └─→ cancelled

consent_required
  ├─→ pending
  └─→ cancelled

pending
  ├─→ passed
  ├─→ failed
  ├─→ needs_review
  └─→ cancelled

needs_review
  ├─→ passed
  ├─→ failed
  └─→ cancelled

passed
  ├─→ expired
  └─→ revoked

failed / expired / revoked / cancelled
  └─→ new check/recheck record when policy permits; do not reopen silently
```

Rules:

- `pending` means the canonical Workin Ants check is awaiting provider/manual completion, not that the provider is the source of truth.
- unknown provider status cannot transition to `passed`.
- `failed` background result may trigger FCRA workflow; it does not directly mutate ProfessionalProfile/Job/Offering lifecycle.
- recheck semantics use a new check unless a later approved policy explicitly defines same-row re-verification.
- provider callbacks and manual review must compare current status before transition.
- duplicate/replayed transition returns prior result or no-op evidence, not another effect.

### 9.4 Professional license credential

Proposed minimum graph:

```text
not_started → pending → verified
                    ├─→ failed
                    └─→ needs_review
needs_review → verified | failed
verified → expired | revoked
```

A later successful re-verification may either create a new credential record or refresh the same credential; that exact history/provenance strategy is part of U-05 and must be settled before production claims durable provenance.

### 9.5 TrustBadge

Proposed graph:

```text
active → suspended → active        # only if supporting evidence remains valid
active → expired
active → revoked
suspended → expired | revoked
```

- `expired` and `revoked` are terminal display outcomes for that badge instance.
- issue a new badge instance after new evidence where history matters rather than rewriting a revoked badge back to active.
- badge status changes emit a Trust event and may request Search refresh.

### 9.6 FCRA adverse action

Conceptual legally gated flow:

```text
not_applicable
      ↓ when approved policy determines FCRA adverse process applies
pre_adverse_required
      ↓ approved pre-adverse notice proof
pre_adverse_sent
      ↓
dispute_window
  ├─→ disputed → cleared_after_dispute
  └─→ final_adverse_sent → restricted

any supported pre-final state → cancelled when the case is withdrawn/invalidated under approved policy
```

This is not sufficient implementation authority by itself. U-06 blocks production automation until notice artifact/version/delivery/retention proof, deadlines, dispute semantics, and exact allowed transitions are approved.

### Lifecycle mechanics

Use SH-053 shared transition plumbing, SH-051/052 concurrency, SH-046 event publication, and owner-local graphs/reason codes. No generic status policy table may own Trust transitions.

---

## 10. Commands

The following names describe the stable mutation surface. HTTP/server-action naming may differ, but application semantics must remain owner-correct.

### `createVerificationRequirement`

- **Purpose:** create a Trust requirement against a validated owner target.
- **Actor/context:** authorized admin/system policy actor.
- **Inputs:** target type/ID, subject type, check type, action flags, vendor/package, validity/fee, typed rule configuration.
- **Preconditions:** SH-001/002; SH-123 validates target; package active/compatible if referenced.
- **Writes:** `VerificationRequirement`.
- **Shared operations:** SH-001, SH-002, SH-123, SH-044, SH-046, SH-029.
- **Effects:** requirement-changed event; downstream readiness reevaluation where appropriate.
- **Idempotency:** semantic key based on admin command/request ID; duplicate target/check rule conflicts must be deterministic.
- **Failures:** invalid target, incompatible package/vendor, malformed ruleJson schema, duplicate/conflicting rule, unauthorized actor.

### `updateVerificationRequirement`

Updates allowed mutable rule fields or active state using expected current state. It must not erase historical meaning for checks already created. Material rule-version semantics remain a documentation/ADR concern if current fields cannot preserve sufficient history.

### `createVerificationPackage` / `updateVerificationPackage` / `transitionVerificationPackage`

Own package/item configuration and draft/active/paused/retired transitions. Package pricing comes from item costs plus approved platform fee. Historical check fee snapshots are never recomputed from today's package.

### `linkScreeningConsent`

- **Purpose:** attach canonical consent proof to screening context only if U-03-approved fields exist.
- **Inputs:** ConsentLog proof reference, subject/check/vendor context.
- **Preconditions:** SH-008 confirms correct active proof; optional SH-010 handles presentation before acceptance.
- **Writes:** only approved `VerificationConsent` linkage and/or `VerificationCheck.consentLogId`.
- **Prohibition:** duplicated acceptedAt/IP/user-agent fields cannot establish validity independently from ConsentLog.

### `initiateVerificationCheck`

- **Purpose:** create the canonical check before provider/manual work.
- **Actor/context:** subject, authorized organization/admin/system actor as applicable.
- **Inputs:** canonical subject facts, requirement/package, consent proof, optional screening-fee Order, intended action/recheck context, idempotency key.
- **Preconditions:** actor/authority; requirement applies; consent sufficient; paid screening Order authoritative where required; no conflicting active attempt under approved policy; applicable hold policy.
- **Writes:** `VerificationCheck` with snapshots and initial canonical state.
- **Shared operations:** SH-001/002, SH-008, SH-011 if applicable, SH-044, SH-051/052, SH-053, SH-046, SH-029; SH-107 for paid screening.
- **Effects:** check-started event; provider job may be queued only after local commit.
- **Replay:** same semantic idempotency key returns the existing check/result.

### `createProviderHostedCollectionSession`

Internal/application command through the provider-neutral port. It requires a valid local check and canonical consent/payment state. It never stores raw SSN or provider report in the domain record.

### `submitVerificationCheckToProvider`

Submits a canonical check to the configured adapter. It snapshots provider check/candidate IDs and order timestamp through a transition-safe application service. Provider-specific request/response types stay inside adapters.

### `completeManualVerificationReview`

- restricted reviewer/admin command;
- accepts a canonical decision, safe evidence refs, reason, expected status;
- may transition `pending`/`needs_review` to `passed`/`failed`/`cancelled` only under approved graph;
- writes Trust truth and audit evidence;
- must not execute consumer lifecycle decisions.

### `submitProfessionalLicenseCredential`

Creates/updates pending credential identity/jurisdiction data after target/actor validation. Any document reference must be a ready private MediaAsset through SH-090. Full license number storage is avoided unless approved.

### `completeProfessionalLicenseVerification`

Applies manual/provider evidence to credential state. Durable check provenance is permitted only after U-05 is resolved. The command must not mark Healthcare readiness.

### `issueTrustBadge` / `suspendTrustBadge` / `expireTrustBadge` / `revokeTrustBadge`

Internal/admin-safe projection commands. They require current supporting Trust evidence and idempotent subject/type/provenance policy. Badge changes never modify underlying check truth.

### `startFcraAdverseActionWorkflow`

Creates/advances FCRA workflow only for an approved legal subset. Before U-06, production automation remains disabled; manual/internal records may be created only under an approved feature specification that does not pretend notice proof is complete.

### `recordFcraDispute` / `advanceFcraAdverseAction`

Legal-gated commands preserving dispute/deadline/final-action state. Notification delivery is requested through SH-041; delivery state remains Notification truth.

### `expireVerificationEvidence`

Worker command that expires passed checks/licenses when owner-defined deadlines pass and triggers readiness/badge reevaluation.

### `requestVerificationRecheck`

Creates or queues a new check under current requirement/consent/payment policy. It does not silently reopen expired/failed historical checks.

### `reconcileVerificationProviderState`

Administrative/scheduled repair command using SH-062. It compares provider state to Trust truth, applies only valid owner transitions, and records operational discrepancies without allowing provider state to overwrite history blindly.

---

## 11. Queries / Decisions

### SH-017 `resolveVerificationRequirements`

- **Consumers:** Professional Eligibility, Marketplace Supply, Organization Hiring/Hiring flows, Candidate Application, Trust UI/admin.
- **Input:** canonical subject + target/taxonomy/action context, evaluation time.
- **Result:** applicable requirement IDs, check types, vendor/package expectation where safe, severity/applicability, validity expectations, owner evidence references.
- **Type:** source truth / decision input.
- **Must not infer:** that any requirement is satisfied.

### SH-018 `evaluateVerificationReadiness`

- **Consumers:** Professional Eligibility, Marketplace Supply, Hiring/Job contexts, Search public-readiness composition indirectly.
- **Input:** subject, target/action context, current time, caller context.
- **Result:** Trust-specific allow/deny/review/remediation decision, missing/pending/expired/revoked/failed reason codes, safe evidence IDs, evaluatedAt/policy version as available.
- **Type:** owner decision.
- **Must not infer:** Professional final readiness, payout KYC, Healthcare readiness, Search rank, or business lifecycle mutation.

### `getVerificationCheckStatus`

Returns a minimized authorized check summary: canonical status/type, safe provider label if needed, ordered/completed/expiry timestamps, remediation state, and safe evidence refs. It never returns raw provider payload/report/token.

### `getVerificationHistory`

Restricted subject/admin history with pagination and reason-code redaction appropriate to caller. Sensitive evidence access may require SH-030.

### `getVerificationEvidenceSummary`

Returns the minimum Trust evidence needed by another owner: requirement/check/credential IDs, canonical status, expiry, provenance class, and safe reasons. Consumers must not treat omitted sensitive detail as evidence of absence.

### `quoteVerificationPackage`

Returns package status, itemized safe cost composition, platform fee, total, currency, non-refundable flag, and disclosure reference. It is a quote/configuration result, not an Order/payment record.

### `getProfessionalLicenseStatus`

Returns current durable credential state, type/jurisdiction, verified/expiry timestamps, and safe provenance reference if U-05 is approved. It does not imply Healthcare readiness.

### `getActiveTrustBadges`

Returns current safe display projection only. Consumers must not use it to reconstruct SH-018.

### Stable reason-code families

Owner-specific codes should distinguish at least:

- `requirement_missing`;
- `consent_required`;
- `payment_required`;
- `check_pending`;
- `check_needs_review`;
- `check_failed`;
- `check_expired`;
- `check_revoked`;
- `credential_missing`;
- `credential_pending`;
- `credential_expired`;
- `credential_revoked`;
- `adverse_action_pending`;
- `dependency_unavailable`;
- `policy_unresolved`;
- `unauthorized` / redacted denial at delivery boundary.

Exact public codes are versioned contracts. Do not leak Checkr/Certn status/error strings as public reason codes.

---

## 12. Public Module Interface

### Public commands

- `createVerificationRequirement`
- `updateVerificationRequirement`
- `createVerificationPackage`
- `updateVerificationPackage`
- `transitionVerificationPackage`
- `linkScreeningConsent` — constrained by U-03
- `initiateVerificationCheck`
- `completeManualVerificationReview`
- `submitProfessionalLicenseCredential`
- `completeProfessionalLicenseVerification`
- `recordFcraDispute` / approved FCRA commands — production-gated by U-06
- `revokeTrustBadge` / restricted badge lifecycle commands where needed

### Public queries / decisions

- **SH-017 `resolveVerificationRequirements`**
- **SH-018 `evaluateVerificationReadiness`**
- `getVerificationCheckStatus`
- `getVerificationHistory`
- `getVerificationEvidenceSummary`
- `quoteVerificationPackage`
- `getProfessionalLicenseStatus`
- `getActiveTrustBadges`

### Emitted domain events

Recommended versioned event families:

- `trust.verification_requirement.changed`
- `trust.verification_check.started`
- `trust.verification_check.status_changed`
- `trust.verification_check.passed`
- `trust.verification_check.failed_or_review_required`
- `trust.verification_check.expired`
- `trust.verification_check.revoked`
- `trust.professional_license.status_changed`
- `trust.fcra_adverse_action.status_changed`
- `trust.trust_badge.status_changed`
- `trust.verification_readiness.changed`

Exact event names/payload versions are Module contract decisions settled before implementation. Payloads carry IDs/status/reason/version/correlation only; no raw report or unnecessary PII.

### Privacy executor

Trust implements:

- SH-096 `enumerateSubjectData`;
- SH-097 `evaluateRetentionRequirement`;
- SH-095 `executePrivacyInstruction`;
- SH-070 provider deletion through the provider-owning adapter where permitted;
- SH-098 anonymization primitive with Trust field mapping where approved.

### Provider-facing interfaces

Internal/provider-edge interfaces owned by Trust:

- provider-neutral hosted-collection/session port;
- submit-check port;
- provider webhook adapter entry point;
- provider result/status translation;
- provider reconciliation;
- provider resource deletion under Privacy instruction.

Provider-facing interfaces are not public domain APIs for other Modules.

---

## 13. Inbound Dependencies

| Owning Module / capability | Interface consumed | Why required | Minimum information | May block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | trusted actor/system context | actor ID/type/assurance metadata | yes | auth/session helper |
| Role / Authority | SH-002 `authorizeResourceAction` | subject/admin/reviewer permission | action, target, owner/context facts | yes | role engine / `isAdmin` shortcut |
| Consent & Disclosure | SH-008 `queryConsentProof`, SH-010 `presentStandaloneConsent` | FCRA/license/DMV standalone proof | proof ID/type/version/acceptedAt/validity | yes before protected screening | consent table/version catalog |
| Taxonomy & Classification | SH-022 `resolveTaxonomyRequirements`; SH-123 target validation through owner | determine trigger source/validate polymorphic targets | canonical target IDs, trigger owner/severity | yes | hardcoded compliance categories |
| Professional Eligibility | `getProfessionalProfileContext` / owner facts | Professional subject identity/context | profile ID, User relation, status/safe classification refs | yes for professional check | ProfessionalProfile repository |
| Candidate/Hiring owners | narrow candidate/Job/organization/request context | hiring screening target and actor context | IDs/relationship/permissible workflow facts approved | yes | Job/Application lifecycle |
| Transaction / Order | SH-107 `createChargeableOrder` + authoritative Order query/event | paid screening | Order ID, status, amount/currency/source | yes when fee required | screening checkout/payment system |
| Media / File Access | SH-090 `attachValidatedMedia`; SH-087 `issueSignedMediaUrl` | credential evidence and restricted viewing | ready asset ID/context/sensitivity/access result | yes when document needed | upload/scan/storage/signed URL |
| Admin Review / Compliance Hold | SH-011/012/013 | reusable stop sign | hold IDs/reasons/scope/expiry | context-dependent | local blocked flags/hold table |
| Notification | SH-041 `requestNotification` | user/admin screening/FCRA/expiry communications | recipient, template intent, safe variables, correlation | delivery should not change Trust truth | SES/SMS/push clients |
| Audit / Event Ledger | SH-029/030 | generic action and sensitive access proof | actor/action/target/safe metadata | logging failure policy per root | local audit/access-log tables |
| Observability / Ops | SH-037/038 and telemetry conventions | provider/job failure visibility | operation/provider/safe IDs/result | no business allow; may gate ops retry | IntegrationFailure/SystemEvent truth |
| Search / Public Visibility | SH-091 | public trust projection refresh | source type/ID/version/reason | projection may lag; source truth remains | SearchUpsertEvent/Typesense writes |
| Privacy / Data Erasure | SH-095/096/097 | legal privacy orchestration | subject target/instruction/retention decision | yes for destructive execution | PrivacyRequest/DataErasure workflow |

Direct cross-Module Prisma reads are not the default. If an owner does not yet expose a required interface, the implementation plan may contract-test a stub; it may not create a Trust-owned copy of that owner truth.

---

## 14. Outbound Consumers and Effects

### Professional Eligibility

Consumes SH-017/018 and Trust readiness-change events. It composes Trust with profile, entitlement, Healthcare, Payment, Taxonomy, and Hold facts. Trust never mutates `ProfessionalProfile.status`.

### Marketplace Supply

Consumes requirement/readiness decisions for high-risk Offering publication/context. Marketplace alone transitions `Offering.status`.

### Gig / Demand

Consumes Professional Eligibility final seller gate; may supply Gig context to Trust requirement resolution through owner facts. Trust does not own Gig response/assignment.

### Organization Hiring / Candidate Application

Consumes Trust verification requirements/readiness for supported Job/candidate contexts. Trust does not reject/hire/move application stage.

### Search / Public Visibility

Consumes safe TrustBadge/public trust projection and refresh requests. Search must not inspect raw checks/reports or reconstruct Trust readiness.

### Admin Review / Compliance Hold

Receives Trust evidence and hold requests where approved. Hold state remains external.

### Notification

Receives business/compliance notification requests. Delivery success/failure does not replace FCRA or check state.

### Audit / Observability

Receives safe action/access/technical evidence. Those records are secondary proof and diagnostics.

### Privacy

Dispatches owner-specific instructions; Trust reports executed/retained/failed results and provider deletion outcomes.

### Rule

Trust may request an effect from another owner or emit a fact. It does not update another Module's tables directly.

---

## 15. Canonical Shared Operations Used

| Canonical operation | Class / owner | Why Trust uses it | Invocation point | Trust-local policy | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | Identity / platform capability | trusted actor context | protected command/query/admin entry | requested Trust action/target | typed actor | `verificationAuth.ts`, local current-user helper |
| **SH-002 `authorizeResourceAction`** | Role / Authority | permission decision | before protected read/mutation | Trust relationship/action vocabulary | allow/deny + safe reason | `verificationPermissions.ts`, `isAdmin` checks |
| **SH-008 `queryConsentProof`** | Consent capability | verify canonical standalone proof | before screening start/provider submission | required type/version/context | proof reference + validity | `fcraConsentStore.ts`, Trust consent boolean |
| **SH-010 `presentStandaloneConsent`** | Consent UI/application capability | separate high-risk disclosure | before user acceptance | screening context | versioned presentation/acceptance flow | custom provider checkbox proof |
| **SH-011 `evaluateComplianceHold`** | Hold capability | consume applicable stop signs | hold-sensitive transition/readiness | how hold affects Trust action | applicable holds | `verificationBlocked` flag |
| **SH-012/013 `request/releaseComplianceHold`** | Hold capability | request/release external stop sign | approved FCRA/fraud/review outcome | Trust evidence/reason | hold reference/result | local hold table/direct status write |
| **SH-015 `returnDecisionResult`** | shared contract, separate policy; Proposed | align readiness result shape | SH-018/public decisions | Trust reason/evidence policy | stable decision shape | global generic readiness engine |
| **SH-017 `resolveVerificationRequirements`** | Trust Module public interface | canonical required-check query | downstream requirement resolution | Trust applicability | requirement decision | hardcoded consumer maps |
| **SH-018 `evaluateVerificationReadiness`** | Trust Module public interface | canonical completion/readiness query | seller/hiring/public composition | Trust check/license policy | Trust decision | badge/provider reconstruction |
| **SH-022 `resolveTaxonomyRequirements`** | Taxonomy interface | get accepted trigger source | requirement calculation | Trust turns triggers into its requirements | owner requirement triggers | local category arrays |
| **SH-029 `appendAuditEvent`** | Audit | generic action proof | admin/manual/FCRA/package changes | which actions need proof/minimized fields | audit ref | local generic audit table |
| **SH-030 `recordSensitiveAccess`** | Audit | protected evidence access proof | viewing license/background/private docs | sensitivity/context | access audit ref | custom report-view log |
| **SH-034 `sanitizeTelemetryMetadata`** | Observability/Audit policy | safe logs | before logging diagnostics | Trust sensitive field allowlist | redacted metadata | raw provider payload logging |
| **SH-037 `recordIntegrationFailure`** | Observability | provider failure visibility | provider/job technical failure | classification/correlation | IntegrationFailure ref | provider failure as check truth |
| **SH-038 `recordQueueTelemetry`** | queue/Observability | worker attempt visibility | every Trust worker | completion meaning | telemetry | custom queue ledger as business truth |
| **SH-041 `requestNotification`** | Notification | deliver user/admin alerts | after owner event/decision | trigger/template safe variables | notification request ref | SES/SMS/push client here |
| **SH-044 `executeIdempotentCommand`** | platform primitive | replay-safe mutation | initiation/review/hold/provider-session commands | semantic key/conflict | claimed/replayed result | local idempotency table/map |
| **SH-045 `deduplicateDomainEvent`** | event inbox | idempotent event consumption | readiness propagation handlers | handler identity/local effect | claim result | processed-event boolean |
| **SH-046 `publishDomainEvent`** | outbox | reliable events after commit | authoritative Trust mutation | event name/version/payload | outbox event | emit-after-write without outbox |
| **SH-047 `enqueueReliableJob`** | queue | durable async work | provider processing/reconciliation/expiry | payload and success semantics | durable job ID | Trust queue table/runner |
| **SH-048 `executeRetryWithBackoff`** | shared queue | transient retries | provider/job failure | retryability | bounded retry/dead-letter | infinite custom retry loop |
| **SH-051 `acquireAggregateLock`** | persistence primitive | serialize races | check/credential/badge/FCRA critical command | lock key/actions | lock/transaction | in-memory mutex |
| **SH-052 `withOptimisticConcurrency`** | persistence primitive | stale-write protection | admin/lifecycle updates | conflict policy | CAS result | last-write-wins mutation |
| **SH-053 `transitionLifecycleState`** | shared mechanism/separate policy | state-machine plumbing | check/package/license/badge/FCRA transition | Trust graph/reasons | transition result | generic CL-03 status policy |
| **SH-055 `runDeadlineExpiration`** | scheduler | expiry/deadline worker shell | check/license/FCRA deadline jobs | expiry legal/business rules | batch execution | custom cron truth table |
| **SH-059 `verifyProviderWebhookSignature`** | integration-security shell | authenticate callback | webhook edge | provider secret/algorithm/tolerance | verified envelope / denial | unsigned provider route |
| **SH-060 `deduplicateProviderEvent`** | shared mechanism/separate truth | claim callback once | after signature | Trust provider-event record/result | first/duplicate claim | AuditEvent/lastProviderEventId as dedupe |
| **SH-061 `translateProviderStatus`** | provider adapter pattern | normalize vendor state | after verified/deduped input | Trust status/reason mapping | normalized provider result | global provider enum/public vendor errors |
| **SH-062 `reconcileProviderState`** | shared worker/separate policy | repair missed/divergent state | scheduled/admin recovery | Trust divergence/repair rules | reconciliation result | cross-module provider reconciler truth |
| **SH-070 `deleteProviderResource`** | provider owner | privacy deletion | approved Privacy instruction | Trust retention/provider semantics | delete/not-supported/retained result | Privacy calling Checkr/Certn directly |
| **SH-078 `minimizeAndRedactProviderInput`** | shared serializer | minimize outbound/telemetry data | provider call/logging | Trust required fields | allowlisted payload | whole Prisma object serialization |
| **SH-087 `issueSignedMediaUrl`** | Media | private evidence access | authorized review/provider handoff | Trust contextual entitlement | short-lived URL/grant | local presigned URL helper |
| **SH-090 `attachValidatedMedia`** | contextual owner + Media asset truth | attach ready evidence context | credential/evidence link | Trust business role | attachment result | local upload/scan implementation |
| **SH-091 `requestSearchProjectionRefresh`** | Search | reindex/remove public trust projection | badge/readiness public change | safe source projection | accepted refresh request | direct SearchUpsertEvent/Typesense |
| **SH-094 `buildSourceProjection`** | source owner pattern | build safe Trust public input | before Search refresh | allowlisted TrustBadge/public fields | deterministic source DTO/version | Search reading raw Trust tables |
| **SH-095 `executePrivacyInstruction`** | Privacy protocol | owner privacy execution | Privacy dispatch | Trust erase/anonymize/retain/provider delete | execution outcome | Trust PrivacyRequest workflow |
| **SH-096 `enumerateSubjectData`** | Privacy protocol | list Trust subject data | privacy planning/export/erasure | Trust records/providers | inventory | universal cross-domain repository |
| **SH-097 `evaluateRetentionRequirement`** | data owner + Privacy | provide retention facts | before destructive action | Trust legal/security record meaning | retain/delete facts | local retention-exemption lifecycle |
| **SH-098 `anonymizePersonalFields`** | shared primitive | deterministic anonymization | privacy execution | Trust field mapping | anonymized values | generic eraser owning all domains |
| **SH-107 `createChargeableOrder`** | Transaction / Order | paid screening transaction | before paid provider check | package fee context remains Trust | Order ID/state | Trust checkout/payment table |
| **SH-123 `validateOwnedTargetReference`** | target owner | validate polymorphic target | requirement creation/resolution | allowed target type/action | valid canonical ref | generic polymorphic Prisma lookup |

---

## 16. Module-Internal Operations

These operations contain Trust domain meaning and should remain local rather than becoming platform utilities.

| Local operation | Purpose | Input | Output | Truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `matchRequirementsToContext` | apply Trust requirement rules to owner-validated context | target/taxonomy/action/subject | requirement set | none | verification applicability is Trust policy |
| `evaluateRequirementSatisfaction` | decide whether current checks/credentials satisfy one requirement | requirement + evidence + time | satisfied/blocker/review | none | semantic meaning is Trust-owned |
| `deriveInitialCheckState` | choose `consent_required`, `not_started`, or `pending` based on approved preconditions | requirement/consent/payment/provider mode | initial status | check | Trust lifecycle policy |
| `validateCheckTransition` | enforce Trust state graph/reasons | current + requested transition/source | transition decision | check | lifecycle owner policy |
| `classifyManualReviewDecision` | normalize reviewer decision | evidence refs + reviewer reason | canonical Trust result | check/credential | cannot be genericized without transferring policy |
| `deriveCredentialStateFromEvidence` | map approved license evidence to durable credential state | check/manual/provider evidence | license result | credential | credential semantics are Trust-specific |
| `deriveBadgeProjection` | decide if/which badge may be active | current Trust evidence | badge projection command | TrustBadge | badge semantics are Trust-owned |
| `invalidateDerivedTrustState` | expire/suspend/revoke badge and signal readiness after evidence invalidation | check/license event | projection/event effects | TrustBadge | Trust controls projection provenance |
| `evaluateFcraRouting` | decide whether approved adverse-action workflow is required | background result + legal policy context | FCRA route/review gate | FCRA workflow | legal-gated Trust policy, not provider mapping |
| `buildSafeVerificationEvidence` | minimize evidence for consumer/public/admin audience | Trust records + caller context | DTO | none | exposure policy tied to Trust semantics |
| `classifyVerificationRetryability` | distinguish technical retry from legal/validation/manual outcome | normalized failure | retry/dead-letter/manual-review class | job behavior | Trust-specific provider/business meaning |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Provider-event dedupe:** SH-060 mechanics are shared; Trust processed-provider-event truth is separate from Stripe, Calendar, Video, Healthcare, or Subscription event truth.
2. **State-machine plumbing:** SH-053 is shared; VerificationCheck, license, package, badge, and FCRA graphs remain Trust policy.
3. **Readiness result shape:** SH-015 may standardize envelope if approved; Trust reason codes/evidence and completion policy remain Trust truth.
4. **Audit:** append mechanics are shared; AuditEvent never replaces VerificationCheck/FCRA/credential state.
5. **Media access:** signed URL/access grant mechanics are Media truth; Trust owns why a reviewer/provider may access a verification document.
6. **Hashing/anonymization:** cryptographic mechanics may be shared; jurisdiction-specific license normalization and field retention remain Trust policy.
7. **Outbox/inbox:** delivery mechanics are shared; Trust owns event facts and consumer-local side effects remain consumer truth.
8. **Workflow runner:** shared durable runner may execute steps; Trust owns the verification/adverse-action/recheck objective and never becomes a cluster-wide orchestrator.
9. **Projection:** Search execution is shared/external; TrustBadge and safe Trust source projection remain Trust-derived facts.
10. **Privacy:** orchestration is Privacy-owned; Trust owns execution against Trust records/providers and retention facts.

---

## 18. Authentication and Authorization

- Every human-initiated protected entry begins with SH-001.
- Webhooks/workers use explicit constrained system/service actor context, never a fabricated end-user.
- SH-002 decides who may perform a named Trust action. Trust supplies resource relationship facts and action vocabulary.
- Subject self-service may include viewing own safe check status, starting approved checks, completing hosted collection, and submitting approved credential context.
- Admin/support/reviewer actions require explicit authority for requirement/package management, manual review, reconciliation, badge revocation, and FCRA case handling.
- Organization/hiring-initiated screening requires organization/request context supplied by its owner; the exact employer/permissible-purpose model is Unresolved and must not be inferred solely from CandidateProfile.
- Authorization does not equal verification readiness. A permitted reviewer may view a case that is still failed/pending.
- SH-030 is required for restricted screening/license/report evidence access according to sensitivity policy.
- Step-up is not automatically required for every Trust action by current evidence. If root security policy declares particular high-risk admin/report access step-up-sensitive, use SH-014 rather than a Trust MFA subsystem.

---

## 19. Compliance / Readiness / Entitlement Gates

### Standalone screening consent

- **Truth owner:** Consent & Disclosure.
- **Consumed query:** SH-008; presentation SH-010.
- **Trust action gated:** initiating/submitting FCRA/background/license/DMV screening where required.
- **Local policy:** which ConsentType/version/context is sufficient for the check.
- **Decision:** proceed, `consent_required`, or deny/review.

### Verification requirement trigger

- **Truth owner:** Taxonomy/target owner for accepted context; Trust for VerificationRequirement.
- **Consumed query:** SH-022 + owner facts/SH-123.
- **Trust action:** resolve/create/evaluate requirements.
- **Decision:** applicable requirement set. Trigger does not prove completion.

### Paid screening

- **Truth owner:** Trust owns package/fee configuration; Order owns transaction truth.
- **Consumed interface:** SH-107 plus Order state query/event.
- **Trust action gated:** provider submission when `requiresPaidScreening`.
- **Decision:** paid/authorized enough to order, payment-required, or dependency unavailable.
- **Prohibition:** payment can never return `passed` verification.

### ComplianceHold

- **Truth owner:** Admin Review / Compliance Hold.
- **Consumed query:** SH-011.
- **Trust action gated:** only actions explicitly defined as hold-sensitive.
- **Local policy:** effect on check/review/recheck/hold request.
- **Decision:** proceed, review, or block local action; no local hold flag.

### FCRA adverse-action gate

- **Truth owner:** Trust for FCRA workflow state; Notification for delivery; Hold for stop sign; downstream business owner for its lifecycle.
- **Trust action gated:** final restriction request/hold request or legally meaningful adverse state.
- **Decision:** pre-adverse required, dispute window, disputed, cleared, final action permitted, or policy unresolved.
- **U-06:** production automation disabled until evidence/transition rules are approved.

### Entitlement

No current evidence makes Track entitlement a direct prerequisite to owning or evaluating Trust screening. Professional Eligibility or the relevant action owner handles seller-plan entitlement. Trust must not add `isPremium`/seller-plan checks without an explicit policy ruling.

---

## 20. Provider Integrations

### Provider-neutral port

Trust owns a provider-neutral screening/credential port with capabilities such as:

- create hosted collection/candidate session;
- submit/order a check;
- fetch current check/credential result for reconciliation;
- parse/normalize webhook event;
- delete provider resource under approved privacy instruction.

The port returns normalized Trust-facing data, not provider SDK objects.

### Adapters

Current evidence supports Checkr/Certn-style providers plus `manual`; schema also lists GoodHire, Evident ID, Stripe Identity, Persona, and `other`.

Only enabled/approved provider adapters are implemented. An enum value is not evidence that a production integration must exist.

### Credentials

- provider secrets are server-only configuration;
- never stored in `VerificationCheck`, package, credential, or public DTO;
- secret rotation is a platform/deployment concern.

### Webhook path

```text
raw provider request
→ SH-059 verify signature
→ parse minimal envelope
→ SH-060 claim Trust-owned event record
→ adapter SH-061 translates event/status
→ Trust transition validation
→ authoritative Trust write + SH-046 event
→ downstream requests
→ SH-037 only for operational failure
```

Live webhook side effects remain disabled until U-04 processed-provider-event truth is approved and implemented.

### Status/error translation

- provider success/failure vocabulary maps to `VerificationCheckStatus`, credential status, and Trust reason codes only in the adapter/domain boundary;
- unknown provider state becomes `needs_review`/operationally unresolved according to approved policy, never `passed` by default;
- raw provider error text is not exposed to consumers.

### Reconciliation

SH-062 compares provider state and canonical Trust state, identifies missed/out-of-order callbacks, and applies only legal owner transitions. Reconciliation must be idempotent and cannot rewrite historical result solely because the provider's current object differs.

### Retry

- retry transient network/rate-limit/server failures using SH-048;
- do not retry explicit provider rejection, failed screening, legal denial, invalid consent, cancelled check, or manual-review result as a technical failure;
- exhausted transient failures become visible dead-letter/manual ops work while Trust truth remains canonical.

### Privacy deletion

SH-070 executes provider deletion only under Privacy instruction and Trust retention decision. Provider inability to delete is reported as a privacy execution result; Privacy owns case status.

### Operational failure

Use SH-037 and safe telemetry. IntegrationFailure never sets VerificationCheck `failed` unless Trust domain policy determines the provider outcome itself constitutes that business status.

---

## 21. Events and Outbox

### Emission rules

Emit a domain event after an authoritative committed fact that other owners may need to react to, including:

- requirement materially changed;
- check created or canonical status changed;
- check/credential expired or revoked;
- FCRA workflow changed where consumers are authorized to know;
- TrustBadge projection changed;
- overall Trust verification readiness changed for a subject/target context.

### Outbox

Use SH-046 transactionally with the owner write. Do not emit after commit with best-effort application code when downstream correctness depends on the fact.

### Payload minimization

Events contain:

- event ID/type/version;
- aggregate ID/type and safe subject/target IDs;
- previous/new canonical status where appropriate;
- safe reason code;
- effective/evaluated/occurred time;
- correlation/causation/idempotency IDs;
- source version/policy version where available.

Never include raw report body, SSN, full license number, provider token, full provider webhook, or unnecessary PII.

### Consumer idempotency

Consumers use SH-045/inbox semantics. Replaying `verification_readiness.changed` must not create duplicate Search refreshes, holds, notifications, or business transitions.

### Events are facts, not commands

`verification_check.expired` states what occurred. It does not mean “suspend profile.” Professional Eligibility, Marketplace, Hiring, Search, and Hold owners decide their own reactions through public contracts.

---

## 22. Background Jobs / Scheduled Work

### Verification/check expiry worker

- **Purpose:** find passed/current checks whose `expiresAt` is due and transition them under Trust policy.
- **Input:** time window/batch cursor.
- **Owner:** Trust.
- **Idempotency key:** check ID + expected status + expiry timestamp/policy version.
- **Retryable failures:** database/queue transient failures.
- **Permanent failures:** invalid transition/data inconsistency → quarantine/manual review.
- **Truth updated:** VerificationCheck; derived badges/readiness.
- **Telemetry:** SH-038 with safe IDs/counts/duration.

### License expiry worker

Same pattern for `ProfessionalLicenseCredential.expiresAt`. It never changes Healthcare or ProfessionalProfile truth directly.

### Recheck scheduler

- identifies evidence that must be renewed;
- requests/creates a new idempotent check under current consent/payment/requirement policy;
- does not reopen old historical results;
- manual/legal blockers become review work, not retry storms.

### Provider reconciliation worker

- uses SH-062;
- scans stale/pending provider-backed checks using safe indexed fields;
- compares normalized provider state;
- applies valid transition or creates operational review;
- never copies full provider report into telemetry.

### Provider callback worker

If webhook edge enqueues normalized processing, the durable job references the claimed Trust provider-event record rather than carrying a raw sensitive webhook payload through the queue unless the shared secure mechanism explicitly supports it.

### FCRA deadline worker

Production scheduling is disabled until U-06 resolves deadlines/proof. Once approved, use SH-055; exact deadline semantics remain Trust legal policy.

Generic queue, scheduler, retries, lease, dead-letter, and telemetry come from SH-047/048/055/038.

---

## 23. Concurrency and Idempotency

### Races to prevent

- two simultaneous check initiations for the same intended requirement/recheck;
- user/manual reviewer/provider callback racing to transition one check;
- duplicate/out-of-order provider callbacks;
- expiry job racing a late provider/manual completion;
- two reviewers completing the same manual case;
- badge issuance racing evidence expiry/revocation;
- FCRA workflow steps racing deadline/dispute updates;
- requirement/package edit racing a new check quote/initiation;
- recheck worker and user-initiated recheck duplicating work.

### Lock/resource keys

Use stable DB-backed lock/CAS keys such as:

- `verification-check:{checkId}`;
- `verification-init:{subjectKey}:{requirementId}:{recheckWindowOrIntent}`;
- `verification-package:{packageId}`;
- `professional-license:{credentialId}` or canonical subject/license key;
- `trust-badge:{subjectKey}:{badgeType}`;
- `fcra-adverse:{verificationCheckId}`;
- `verification-provider-event:{provider}:{eventId}`.

These are semantic examples; root shared primitives own the actual key format/API.

### Transaction boundary

For an authoritative mutation, the same database transaction should include:

1. current owner-state read/lock or CAS;
2. transition validation;
3. Trust-owned state write;
4. owner-specific provider-event claim/update when applicable;
5. transactional outbox record for required domain event;
6. idempotency result persistence through SH-044 where supported.

External provider calls normally occur outside the DB transaction after local truth is established; result application occurs in a new idempotent transition transaction.

### Replay semantics

- same command key + same semantic fingerprint → return prior result;
- same key + conflicting fingerprint → stable idempotency conflict;
- same provider event ID → no repeated business effect;
- stale expected status/version → conflict/current state, not last-write-wins;
- duplicate job → no-op/replay-safe result.

No in-memory lock may be relied on for database-owned concurrency.

---

## 24. Media / Storage

### Business meaning owned here

Trust owns the reason a private asset is associated with verification/credential evidence and whether an authorized reviewer/provider may use that evidence.

### File mechanics owned elsewhere

Media / File Access owns `MediaAsset`, upload policy/session, binary validation, malware scan, metadata scrubbing, quarantine, object storage, processing/readiness, access grants, signed URLs, and storage deletion.

### Approved upload contexts

Current evidence specifically names:

- `professional_government_id`;
- `professional_license_document`.

The registry states these files are capped at 5 MB by upload policy, must remain private, and must not be displayed publicly.

### Rules

- attach only ready/validated MediaAsset through SH-090;
- a clean scan is not credential verification;
- use SH-087 for short-lived private access after Trust contextual authorization;
- restricted evidence access uses SH-030 where policy requires;
- prefer vendor-hosted sensitive collection for SSNs and full background data;
- do not store full sensitive ID images unless required and legally reviewed;
- provider/report artifacts do not receive permanent public URLs.

The exact owned join/evidence model between MediaAsset and Trust check/credential is not fully established. Do not invent a generic `verificationFiles` relation without an approved schema ruling.

---

## 25. Search / Projection

### Source truth

VerificationCheck, ProfessionalLicenseCredential, FCRA state, and TrustBadge remain Trust-owned. Search is never the source of verification truth.

### Trust-owned source projection

Trust may build a minimized deterministic projection containing only approved fields such as active badge type/label/status/expiry and safe public-readiness facts. Raw check/provider/FCRA/private evidence stays out.

### Search-owned projection

Search / Public Visibility owns SearchUpsertEvent, Typesense documents, index workers, ranking, reconciliation, and query surfaces.

### Triggers

Potential SH-091 requests occur when:

- a displayed TrustBadge is issued/suspended/expired/revoked;
- Trust verification readiness changes in a way that affects owner-approved public visibility;
- privacy/moderation/hold consequences require source owners to deindex through their own policies.

### Hard boundary

Trust never writes SearchUpsertEvent or calls Typesense. Search must not read Trust private tables to infer readiness.

---

## 26. Notification

Trust owns notification **triggers and safe intent**, including approved:

- screening required/reminder;
- hosted-provider handoff;
- check requires input/review;
- credential expiring/expired;
- recheck required;
- approved pre-adverse/final-adverse workflow notices;
- manual-review outcome;
- remediation availability.

SH-041 owns delivery request. Notification owns email/SMS/push/in-app routing, provider clients, retry, and NotificationDelivery state.

FCRA notice proof may need an immutable legal artifact/delivery relationship beyond ordinary NotificationDelivery; U-06 must decide this. Notification success alone cannot advance FCRA state unless the approved Trust policy explicitly accepts that proof contract.

Payloads use safe IDs/template variables and never contain raw reports, SSNs, full license numbers, report tokens, or unnecessary background details.

---

## 27. Audit and Sensitive Access

### Trust domain history

VerificationCheck/FCRA/credential/badge records and versioned domain events describe Trust business facts. A future owner-specific lifecycle ledger may be added only by ruling.

### Generic AuditEvent

Use SH-029 for important administrative/manual actions, requirement/package changes, FCRA decisions, badge override/revocation, and privacy execution where root policy requires.

AuditEvent does not determine Trust status.

### AccessAuditLog

Use SH-030 for restricted reads/downloads of screening/license/private evidence and related deny/redact decisions where policy requires.

AccessAuditLog does not grant access and does not replace MediaAccessGrant.

### No collapse

Do not create one generic `verificationHistory` table that mixes:

- provider event dedupe;
- domain transitions;
- audit actions;
- sensitive access;
- operational failures.

Each has different semantics and owner.

---

## 28. Privacy and Retention

### Subject-data inventory

Potential personal/sensitive data includes:

- User/Profile/Candidate identifiers and screening relationships;
- check types/status/timestamps/provider references;
- provider candidate/check IDs;
- report summary code and sensitive `reportToken`;
- consent linkage;
- fee/order reference and fee snapshots;
- license type/jurisdiction/masked/hash/provider reference;
- FCRA workflow timestamps/provider reference/notes;
- TrustBadge history;
- provider-side resources;
- contextual MediaAsset references if approved.

### Privacy executor

Trust implements owner handlers for SH-096/097/095:

1. enumerate Trust records/provider resources for the subject;
2. provide retention facts and legal/security dependencies;
3. execute erase/anonymize/detach/provider-delete/retain instruction;
4. report deterministic execution result to Privacy.

### Retention

U-18: exact legal retention periods for verification/adverse-action evidence are unresolved. Therefore:

- destructive production erasure/retention scheduler for legally sensitive Trust records is gated by approved retention policy;
- do not hard-delete FCRA/security proof merely because a Privacy request exists;
- Privacy owns `DataRetentionExemption`; Trust supplies retention facts;
- anonymize nonessential personal fields where approved while preserving required proof relationships.

### Provider deletion

Use SH-070 under Trust adapter. Provider deletion must not be called directly by Privacy. If provider retention/legal policy blocks deletion, report `retained`/`not_supported` through the privacy executor.

### Export contribution

If Privacy requests an export, Trust contributes only the subject-accessible/safe fields approved for export; provider secrets/internal risk metadata remain excluded according to policy.

---

## 29. Observability

### Structured logs

Safe dimensions:

- operation name;
- module = `trust_verification_screening`;
- request/correlation/causation IDs;
- safe check/requirement/package/credential IDs;
- provider enum where safe;
- normalized event type/status class;
- attempt/retry count;
- duration;
- result category;
- job ID;
- HTTP/provider status category without raw body.

### Never log

- SSN;
- raw background report;
- full license number;
- `reportToken`;
- provider secrets/signatures;
- full webhook payload;
- sensitive consent request evidence beyond approved hashes;
- unnecessary PII.

Use SH-034/078 redaction, SH-037 IntegrationFailure, SH-038 worker telemetry, and root metrics/Sentry conventions.

### Metrics

Useful metrics include:

- check initiation count/result by type/provider;
- consent-required rate;
- provider callback signature failure count;
- duplicate/unknown/out-of-order event count;
- provider completion latency;
- pending/stale check count;
- manual-review queue age/count;
- reconciliation success/failure;
- check/license expiry/recheck count;
- badge issuance/invalidation count;
- privacy executor outcomes;
- dead-lettered Trust jobs.

Operational metrics never define business truth.

---

## 30. Security Boundaries

1. Validate all public command/query inputs and provider payloads at the server trust boundary using root-approved runtime validation (project context specifies Zod).
2. Never pass raw provider payloads into domain policy.
3. Verify raw webhook signature before any event claim or domain side effect.
4. Deduplicate provider events before business side effects.
5. Provider secrets are server-only and excluded from logs/client bundles.
6. Prefer vendor-hosted collection for SSN/background report data.
7. Never store full background reports in ordinary application tables.
8. Treat `reportToken` as secret/opaque until explicitly proven safe; encrypt/protect if retention is required.
9. Store license identifiers masked/hashed where full value is not required; use root-approved crypto primitives and key/version management.
10. Private evidence access requires contextual authorization plus Media mechanics and sensitive access proof where required.
11. Rate-limit screening initiation, provider-session creation, manual-review endpoints, sensitive queries, and webhook edges using root mechanisms.
12. Unknown provider event/status fails safely; never defaults to `passed`.
13. Client state is not proof of consent, payment, verification, authorization, or hold clearance.
14. Database concurrency controls protect replay/race-sensitive transitions.
15. Public/search DTOs use allowlists rather than removing fields from broad Prisma objects after serialization.

---

## 31. Error / Decision Result Pattern

Public interfaces return stable owner result categories rather than throwing provider vocabulary across boundaries.

Recommended top-level classes:

- `success`
- `denied`
- `review_required`
- `remediation_required`
- `validation_error`
- `authorization_denied`
- `conflict`
- `dependency_unavailable`
- `temporarily_unavailable`
- `policy_unresolved`
- `not_found`

Readiness decisions additionally carry safe reason codes, evidence refs, evaluatedAt, optional expiresAt/policy version, and safe next action.

Provider errors are normalized internally into categories such as `transient_provider_failure`, `provider_rejected`, `unknown_provider_status`, `invalid_signature`, `duplicate_event`, and `reconciliation_required`. Consumers do not receive raw provider messages.

Forbidden caller responses must not leak sensitive blocker details. A caller may receive a generic denial even when an internal reason exists.

---

## 32. Testing Architecture

### Domain unit tests

- requirement applicability/satisfaction;
- package pricing composition;
- check transition graph;
- license transition graph;
- badge derivation/invalidation;
- manual review classification;
- expiry/recheck policy;
- FCRA routing only for approved legal rules;
- reason-code generation and audience redaction.

### Public contract tests

- SH-017 request/result stability;
- SH-018 decision stability;
- package quote;
- check status/history/evidence DTO minimization;
- license status;
- TrustBadge display contract;
- privacy executor contracts.

### Database/integration tests

- Trust-owned repository boundaries;
- relationship writes;
- package/check cost snapshot behavior;
- one-to-one FCRA relation;
- expiry indexes/query behavior;
- provider event uniqueness if approved;
- transactional owner write + outbox;
- no direct foreign-owner writes.

### Authorization tests

- subject self-service;
- another User denial;
- approved admin/reviewer;
- organization/hiring context where supported;
- system actor worker/webhook capabilities;
- sensitive evidence access and audit.

### Compliance tests

- standalone consent required before protected check;
- payment does not imply pass;
- badge does not satisfy readiness;
- Trust KYC separation;
- Healthcare credential ≠ Healthcare readiness;
- no auto-ban from failed/unknown provider event;
- FCRA paths remain feature-disabled if U-06 incomplete;
- no raw SSN/full report persistence/logging.

### Idempotency/concurrency tests

- duplicate check initiation;
- concurrent manual/provider completion;
- duplicate/out-of-order provider event;
- expiry versus late completion;
- duplicate badge issuance/invalidation;
- recheck/user initiation race;
- FCRA dispute/deadline race once enabled.

### Provider adapter tests

- signature fixtures;
- normalized request/response mapping;
- unknown status/event;
- timeout/rate-limit/retryability;
- dropped-event reconciliation;
- sensitive payload minimization;
- provider resource deletion behavior.

### Privacy tests

- enumeration completeness;
- retention-gated destructive actions;
- anonymization mapping;
- provider deletion command;
- retained/failed outcomes;
- audit proof remains separate.

### E2E participation tests

At minimum:

- professional sees requirement → records standalone consent → starts manual/no-fee check → reviewer completes → SH-018 changes;
- expired verification causes readiness reevaluation and badge invalidation;
- Marketplace/Professional Eligibility consumes SH-018 without direct Trust-table access;
- provider callback path is safely disabled when U-04 unresolved;
- Search receives only safe Trust projection via SH-091;
- privacy orchestration calls Trust executor rather than deleting Trust rows directly.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `VerificationCheck` is the authoritative screening attempt/result; `TrustBadge` is not.
2. `VerificationRequirement` defines required checks; Taxonomy trigger alone does not prove requirement completion.
3. Generic consent/version proof remains `ConsentLog`-owned.
4. No check requiring standalone consent may reach provider submission without canonical proof.
5. A screening fee payment never means the check passed.
6. Trust must not create or mutate Order payment truth directly.
7. Payout `KycVerification` must never be reused as Trust screening truth.
8. Account-recovery identity proof must never be reused as Trust screening truth without an explicit architecture ruling.
9. Healthcare credential verification must never be treated as BAA/HIPAA readiness.
10. A clean/validated file is not a verified license/background result.
11. No raw SSN or complete background report is stored in ordinary Trust application tables.
12. `reportToken` and provider secrets never appear in public DTOs, Search, analytics, or ordinary logs.
13. Provider status/event is verified, deduplicated, translated, and transition-validated before side effects.
14. `lastProviderEventId` alone is never accepted as complete production webhook dedupe truth.
15. Trust does not reuse `ProcessedStripeEvent` or another Module's provider-event ledger.
16. Unknown provider status cannot result in `passed`.
17. Failed background result does not automatically suspend a profile, reject an application, or block a business action when adverse-action process is required.
18. FCRA production automation remains disabled until U-06 is resolved.
19. The exact credential-to-check provenance claim remains disabled until U-05 is resolved.
20. Requirement target references are validated through the target owner; no generic polymorphic direct Prisma lookup becomes a cross-domain repository.
21. Consumers use SH-017/018 or safe owner queries; they do not reconstruct Trust policy from badges/provider fields.
22. Trust never writes SearchUpsertEvent or calls Typesense.
23. Trust never creates local generic hold, audit, notification, privacy, auth, queue, signed-URL, or malware-scan infrastructure.
24. Evidence expiry/revocation causes Trust readiness and applicable badges to be reevaluated.
25. Rechecks preserve historical check truth rather than silently rewriting failed/expired results unless a later approved lifecycle explicitly permits same-row renewal.
26. Lifecycle changes use transaction-safe expected-state/concurrency controls.
27. Retried commands/events/jobs must not repeat business effects.
28. Domain events are facts, not cross-Module commands disguised as events.
29. Privacy orchestration remains Privacy-owned; Trust only executes owner-specific instructions.
30. Destructive erasure/retention behavior for legally sensitive screening records stays gated by approved retention policy.
31. Generic AuditEvent/IntegrationFailure never replaces Trust lifecycle/provider-event truth.
32. Broad badge/check names (`financial_trust`, `healthcare_verified`, `gold_trust_check`, `platform_verified`) remain inert or narrowly documented until their scope is approved.
33. A provider SDK type may not cross from `infrastructure/providers` into public/domain contracts.
34. Public/readiness DTOs are allowlisted and audience-aware.
35. A Cluster or consumer may coordinate Trust; it never becomes co-owner of Trust records.

---

## 34. Prohibited Duplicate Implementations

Do not generate the following inside this Module:

- `verificationAuth.ts`, `trustSession.ts`, `getCurrentVerificationUser.ts` — use SH-001;
- `verificationPermissions.ts`, `canReviewCheck.ts`, local role engine — use SH-002;
- `screeningConsentService.ts`, `fcraConsentStore.ts`, `consentedBoolean` — use SH-008/010 and canonical ConsentLog;
- `verificationBlock.ts`, `backgroundCheckHold.ts`, `isVerificationBlocked` — use SH-011/012/013;
- `screeningCheckout.ts`, `verificationPaymentService.ts`, mini payment/order table — use SH-107/Order owner;
- `verificationAudit.ts`, `backgroundReportAccessLog.ts` as generic ledgers — use SH-029/030;
- `verificationQueue.ts`, `checkrRetryRunner.ts`, cron truth table — use SH-047/048/055;
- `verificationIdempotency.ts`, local idempotency table — use SH-044;
- `verificationMutex.ts`, process-memory lock — use SH-051/052;
- generic state-machine owner table — use SH-053 plumbing with Trust-local graph;
- `webhookAuth.ts`/unsigned webhook route — use SH-059;
- `processedCheckrEvents` implemented as a cross-Module/global provider table — use SH-060 mechanics with Trust-specific truth after U-04;
- `globalProviderStatus.ts` — use SH-061 adapter pattern with Trust enums;
- `verificationProviderReconciler` that owns other Modules — use SH-062 owner-local worker;
- `licenseUploadValidator.ts`, `idDocumentScanner.ts` — use Media file validation;
- `verificationSignedUrl.ts`, `licenseDocumentUrl.ts` — use SH-087;
- local R2/S3/Storage client for verification evidence;
- `verificationIndexer.ts`, `badgeTypesense.ts` — use SH-091/094 and Search owner;
- `sendAdverseEmail.ts`, SES/SMS/push client — use SH-041;
- `deleteVerificationData.ts` as a standalone PrivacyRequest workflow — use SH-095/096/097;
- generic cross-domain `verificationTargetRepository.ts` — use SH-123/owner facts;
- `isVerified`, `backgroundPassed`, `licenseVerified`, `verifiedOnly`, `trustScoreGate`, `stripeReady` helpers as source truth;
- direct Payment KYC, Healthcare, Offering, Gig, Job, Application, Search, Hold, Audit, Notification, or Privacy repositories.

---

## 35. Unresolved Decisions

### U-03 — VerificationConsent proof split

Does `VerificationConsent` remain, and which fields are screening linkage versus duplicated ConsentLog proof? Until resolved, ConsentLog is canonical and Trust writes only approved linkage.

### U-04 — Trust processed-provider-event schema

What exact owner record, statuses, payload fingerprint, correlation fields, and retention are used? Production webhook side effects remain disabled until resolved.

### U-05 — ProfessionalLicenseCredential ↔ VerificationCheck provenance

How does a durable credential reference the check/evidence that established/refreshed it? No hidden JSON/notes convention is allowed.

### U-06 — FCRA notice/delivery/retention proof

What immutable notice artifact/version/content, recipient, delivery proof, dispute timing, final-action proof, and retention rules are required? Automated adverse action remains disabled.

### U-18 — exact Trust retention periods

Exact legal retention durations for verification/adverse-action records are not supplied. Destructive retention scheduling stays gated.

### Provider selection

Checkr and Certn are current expected screening candidates, with other enum/provider possibilities. Exact provider mix by check type/jurisdiction remains provider configuration/contract work; provider-neutral domain ports can proceed.

### Subject/request context

`VerificationCheck` always has `userId` and optional Professional/Candidate IDs but no explicit check-level subjectType. Employer-initiated hiring screening also lacks an explicit Organization/Job/JobApplication/permissible-purpose request aggregate. The supported subject-context invariant and employment request proof must be settled before broad hiring screening production use.

### Requirement action vocabulary

Current requirement booleans cover publish/apply/ranking boost. Gig response, assignment, booking, professional activation, interview advancement, or other contexts are not typed. Do not hide new action policy in unversioned `ruleJson`.

### Broad verification vocabulary

The exact business scope of `identity`, `financial_trust`, `healthcare_credential`, and broad TrustBadge types needs explicit policy to prevent overlap with Identity, Payment, or Healthcare.

### Package provider model

Current package has one provider. Multi-provider package composition is not established.

### Trust evidence Media linkage

The schema does not establish a canonical owned join between a MediaAsset and a specific check/credential. Add one only after an evidence/retention/access ruling.

### `reportToken`

Its exact provider semantics, encryption/retention/rotation, and whether Workin Ants should persist it at all remain unspecified. Treat it as highly sensitive and non-public.

### Domain lifecycle event ledger

A dedicated immutable Trust lifecycle event table is not currently established. Outbox events are required for reliable reactions; add a domain ledger only if product/legal/audit requirements justify it.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Trust Verification / Screening is the sole owner of verification requirements/checks/packages, screening-specific workflow state, professional-license credentials, FCRA adverse-action workflow state, TrustBadge projection, and Trust verification-readiness policy.
2. `VerificationCheck` is screening truth; `TrustBadge` is a derived display projection.
3. Consent & Disclosure owns generic versioned consent proof; Trust only evaluates sufficiency and may own screening linkage.
4. Payment KYC/tax/payout truth is separate from Trust screening even if provider technology overlaps.
5. Healthcare readiness/BAA truth is separate from Trust credential verification.
6. Marketplace, Gig, Job, Application, ProfessionalProfile, Order, ComplianceHold, Search, Media, Notification, Audit, Privacy, and Observability lifecycles remain with their owners.
7. SH-017 and SH-018 are the canonical Trust public requirement/readiness interfaces.
8. Provider adapters remain behind Trust-owned provider-neutral ports; provider payloads never become domain/public types.
9. Webhook signature verification/dedupe/translation/reconciliation reuse canonical shared mechanisms while retaining Trust-specific provider-event truth.
10. Production Trust webhooks require owner-specific processed-provider-event truth; `lastProviderEventId`, AuditEvent, or ProcessedStripeEvent are insufficient substitutes.
11. Raw SSNs/full background reports are not stored in ordinary application tables; vendor-hosted collection is preferred.
12. Failed checks do not directly mutate another Module's business lifecycle.
13. Search is projection and Media owns file mechanics.
14. Generic audit/ops records remain distinct from Trust truth.
15. Privacy orchestration remains Privacy-owned.

### Proposed Rulings carried by this Module

- **TV-PR-01:** owner-specific Trust provider-event truth is required before live webhook side effects, inheriting CL-03 PR-09/U-04.
- **TV-PR-02:** reliable Trust domain events use SH-046 outbox; a separate lifecycle ledger is added only by explicit later ruling.
- **TV-PR-03:** until U-03 is resolved, `VerificationConsent` may be only a safe linkage to canonical ConsentLog and cannot be independent proof.
- **TV-PR-04:** rechecks should preserve historical checks rather than reopening terminal results unless a later approved graph explicitly permits same-row renewal.
- **TV-PR-05:** broad TrustBadge types are not activated until their precise evidence/claim semantics are documented.

### Non-implementable until resolved

- production webhook side effects without U-04;
- durable credential-to-check provenance claims without U-05;
- automated final FCRA adverse-action workflow without U-06;
- destructive legal retention scheduling without U-18;
- unsupported broad employment-screening request/permissible-purpose behavior without a request-context ruling.

---

## 37. Coding-Agent Usage

Before implementing or modifying this Module, an agent must read the repository-current versions of:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md` / Canonical Shared Operations Registry;
5. `context/professional-supply-readiness/architecture.md`;
6. `context/professional-supply-readiness/build-plan.md`;
7. this Module `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. public-interface sections for Identity & Access, Role / Authority, Consent & Disclosure, Taxonomy & Classification, Professional Eligibility, Transaction / Order, Media / File Access, Admin Review / Compliance Hold, Search / Public Visibility, Notification, Audit / Event Ledger, Privacy / Data Erasure, Observability / Ops, and relevant Hiring owners;
10. the current `progress-tracker.md`.

Before coding a numbered Module feature, the agent must also:

- confirm the parent CL-03 feature/milestone and prior Module exit gate;
- identify all Unresolved decisions touched by the feature;
- refuse to invent a resolution in code;
- produce the required feature implementation specification from the Module plan;
- implement only the approved feature slice;
- run the required validation, type, test, migration, contract, security, and workflow checks;
- report completion using the required completion-report template.
