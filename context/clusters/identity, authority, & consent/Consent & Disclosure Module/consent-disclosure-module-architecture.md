# Consent & Disclosure Module Architecture

> **Module ID:** `consent_disclosure`  
> **Module name:** Consent & Disclosure Module  
> **Module type:** `compliance`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/clusters/identity, authority, & consent/Consent & Disclosure Module/consent-disclosure-module-architecture.md`\
> **Document status:** implementation-grade Module architecture grounded in the current Workin Ants registries, Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Registry, CL-01 architecture, and CL-01 build plan  
> **Audience:** coding agents, developers, reviewers, security reviewers, privacy/compliance reviewers, and maintainers  
> **Update rule:** update this file whenever a binding Consent & Disclosure ownership, proof, versioning, retention, authorization, privacy, event, or public-contract decision changes. Build progress must not silently redefine this architecture.

Evidence labels used in this file:

- **Confirmed** — directly supported by the current Workin Ants registry, schema, glossary/compliance evidence, canonical shared-operation registry, or CL-01 architecture.
- **Proposed Ruling** — a necessary implementation-grade decision strongly supported by evidence but not yet fully settled by authoritative sources.
- **Unresolved** — a real architecture question that must be decided before dependent production behavior is implemented.

---

## 1. Module Header

Consent & Disclosure is the CL-01 proof owner for version-specific acceptance of agreements, disclosures, authorizations, and consent text. It is subordinate to the root Workin Ants architecture and to the CL-01 Cluster architecture. The Cluster coordinates when other Modules need consent proof; it does not own `ConsentLog`, `ConsentType`, or any Consent lifecycle.

The current executable source evidence is the Prisma schema. This document explains the semantic ownership and contracts that Prisma alone cannot express. If current code or migrations conflict with a confirmed ruling here, the conflict must be surfaced rather than normalized silently.

The BTLS architecture/build-plan documents are used only as a rigor and document-structure reference. No BTLS domain, provider, tenancy, library, or product assumption is authoritative here.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Preserve durable, version-specific proof that a `User` explicitly accepted a particular consent, disclosure, authorization, agreement notice, or terms version.

### Goal

Allow any consuming Module to ask a narrow question — **“Does the required exact proof exist, and what record proves it?”** — without letting Consent & Disclosure take ownership of the feature, eligibility decision, provider connection, subscription, agreement execution, verification outcome, or other business lifecycle unlocked by that proof.

### What enters

Typical inputs are:

- an authenticated Workin Ants actor resolved by Identity & Access;
- a `ConsentType`;
- the exact version presented to the User;
- an explicit acceptance action;
- trusted request context such as server time, request/correlation ID, IP address for privacy-safe hashing, and user agent where collection is approved;
- optional consumer/workflow context used only for correlation or for the consumer to retain its own proof reference;
- once the missing version-catalog architecture is resolved, the active consent-version definition applicable to type, locale, jurisdiction, and effective time.

### What leaves

The Module produces:

- an authoritative `ConsentLog` record;
- a stable proof result containing the proof ID, type, version, and `acceptedAt`;
- proof/history queries that prevent direct foreign Prisma access;
- a reusable standalone-consent presentation capability;
- once U-CL01-13 is resolved, an active-version resolution capability;
- Privacy-owner-compatible subject-data enumeration and target execution for Consent-owned records;
- audit, notification, event, and observability requests through canonical shared interfaces when applicable.

### Capability transformation

```text
trusted User actor
+ exact consent type/version
+ explicit acceptance
+ minimized request evidence
        ↓
validated, idempotent acceptance command
        ↓
ConsentLog proof
        ↓
version-specific proof query / proof reference
        ↓
consumer decides its own business action
```

### Why this is a separate Module boundary

Consent proof is reused across identity/security, verification, calendar, notifications, agreements, digital goods, healthcare, subscriptions, sweepstakes, and rewards. Centralizing the proof and versioning policy prevents a proliferation of `hasAcceptedTerms` booleans and one-off consent tables while still preserving contextual records owned by those domains.

---

## 3. Owned Truth

### 3.1 Schemas / models owned

| Record | Ownership | Plain-English meaning |
|---|---|---|
| `ConsentLog` | **Confirmed** | Immutable-style evidence that one User accepted one exact consent/disclosure type and version at a particular time, with minimized request evidence. |
| Persistent consent-version catalog | **Capability ownership confirmed; schema unresolved** | The authoritative source for which consent text/version applies now. No Prisma model currently exists; U-CL01-13 must be resolved before a production schema is introduced. |

### 3.2 Enums / statuses owned

`ConsentType` is **Confirmed** as Consent & Disclosure-owned controlled vocabulary. The current Prisma enum contains:

`terms`, `privacy_policy`, `cookies`, `marketing`, `age_gate`, `calendar_sync`, `sweepstakes_rules`, `gamification_terms`, `reward_redemption_terms`, `healthcare_baa`, `fcra_background_check`, `license_verification`, `dmv_check`, `passkey_login`, `sms_mfa`, `sensitive_financial_access`, `account_recovery_identity_verification`, `phone_number_update`, `digital_goods_terms`, `digital_goods_refund_policy`, `digital_goods_license`, `child_directed_content_declaration`, `course_accessibility_disclosure`, `electronic_records_consent`, `electronic_signature_consent`, `agreement_execution_consent`, `manual_signature_opt_out`, `calendar_free_busy_access`, `calendar_writeback_access`, `calendar_disconnect_notice`, `web_push_notifications`, `pwa_install_guidance`, `subscription_terms`, `recurring_billing_authorization`, `plan_change_terms`, `commission_terms`, and `buyer_fee_waiver_terms`.

The historical Module Registry enumerates only a subset. The current Prisma enum and CL-01 evidence are stronger structural evidence; the registry list is stale/incomplete, not evidence that the omitted values moved to consumer ownership.

There is **no current ConsentLog status enum**. A `ConsentLog` is completed acceptance proof; it is not pending, declined, withdrawn, revoked, expired, or superseded state.

### 3.3 Lifecycles owned

**Current confirmed lifecycle:** creation and preservation of accepted proof.

```text
not recorded
   │ explicit acceptance of exact type/version
   ▼
ConsentLog created
   ▼
terminal historical proof
```

There is no approved mutation transition from a `ConsentLog` to revoked/withdrawn/superseded. If revocable-current-state behavior is required, it must preserve acceptance history and must not be invented until U-CL01-16 is resolved.

The future consent-document/version lifecycle is owned in principle by Consent & Disclosure, but its states, transitions, schema, publishing authority, and re-consent semantics remain gated by U-CL01-13 and U-CL01-16.

### 3.4 Source-of-truth fields

Current `ConsentLog` authoritative fields are:

- `id` — proof identity;
- `userId` — accepting Workin Ants User;
- `type` — `ConsentType`;
- `version` — exact version accepted;
- `acceptedAt` — acceptance time;
- `ipHash` — optional privacy-safe request evidence;
- `userAgent` — optional request evidence;
- `createdAt` — persistence timestamp.

### 3.5 Domain events / ledgers owned

No Consent-specific persisted event-ledger model is currently confirmed. `ConsentLog` is proof truth and must not be turned into a generic event log. Generic `AuditEvent` and `AccessAuditLog` remain Audit / Event Ledger truth.

Formal event names such as `ConsentProofRecorded`, `ConsentVersionPublished`, or `ConsentWithdrawn` are **not binding yet**. If durable event consumers are required, the event contract must be approved and published through SH-046 rather than creating a local event bus.

### 3.6 Projections owned

No search or public projection is currently owned by this Module. Consent history is a query over source truth, not a separate search projection.

### 3.7 Snapshots / proof owned

`ConsentLog` is the generic versioned acceptance proof. Consumers may retain an immutable `consentLogId` or a consumer-owned contextual snapshot when historical meaning must be frozen. That consumer record remains separate truth.

### 3.8 Policies / invariants owned

Consent & Disclosure owns:

- exact type/version matching semantics;
- what constitutes an explicit acceptance command;
- which `ConsentType` values require standalone presentation, once the policy is fully codified;
- active-version applicability and material-change/re-consent policy once U-CL01-13/U-CL01-16 are resolved;
- Consent-specific evidence minimization rules;
- what fields are safe to return in self/admin history queries;
- Consent-owned privacy disposition mapping after U-CL01-15 is resolved.

---

## 4. Explicit Non-Ownership

Consent & Disclosure must not own or duplicate the following:

| Adjacent owner | Truth that remains outside Consent & Disclosure |
|---|---|
| Identity & Access | authentication, sessions, `User`, passkey registration/authentication result, SMS MFA result, step-up result, account recovery state, age eligibility state |
| Role / Authority | platform/admin/resource permission interpretation |
| Trust Verification / Screening | `VerificationConsent` subject/check context, `VerificationCheck`, screening result, adverse-action lifecycle, licenses, trust badges |
| Booking & Calendar | `CalendarConnection`, provider authorization/connection state, calendar scopes, provider callbacks, disconnect lifecycle |
| Notification | browser/device permission, `NotificationSubscription`, endpoint/provider state, notification persistence and delivery |
| Transaction / Order | `Agreement`, `AgreementElectronicConsent`, signature/execution/manual-opt-out lifecycle, transaction truth, contract document/hash lifecycle |
| Digital Goods Access | `DigitalGoodsTermsAcceptance` contextual lifecycle, purchased access, download/playback grants |
| Healthcare / Regulated Services | `BaaAgreement`, HealthcareComplianceProfile, healthcare readiness, PHI boundary/redaction state |
| Track Subscription & Entitlement | plan, subscription, recurring-billing provider state, entitlements, usage, fee-waiver/commission policy |
| Sweepstakes / Prize | entries, odds, drawings, winnings, fulfillment, tax coordination |
| Gamification / Rewards | programs, point ledgers, challenges, rewards, redemptions |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob, DataErasureTarget, retention-exemption orchestration |
| Audit / Event Ledger | generic AuditEvent and AccessAuditLog truth |
| Observability / Ops | IntegrationFailure, SystemEvent, queue/health/incident truth |
| Search / Public Visibility | Typesense/search projection execution |
| Media / File Access | upload, storage, scan, signed URL, generic file access mechanics |

The registry’s historical “Privacy request workflow” technology label is specifically rejected as an ownership implication. Consent participates as a data owner/executor only.

---

## 5. Module Architecture Principles

1. **Consent is proof, not permission.** A positive proof result never means the downstream action is otherwise allowed.
2. **Exact version means exact version.** A proof for version `v1` does not satisfy a consumer requiring `v2` unless an approved Consent-owned policy explicitly says it does.
3. **No generic acceptance booleans.** Do not add `acceptedTerms`, `hasConsent`, or feature-local consent flags as source truth.
4. **`ConsentLog` is historical proof.** Normal product code does not edit a proof row after creation.
5. **Explicit acceptance only.** Merely viewing a page, provider callback, browser permission, or downstream success does not create ConsentLog proof.
6. **High-risk disclosures remain separable.** FCRA/screening, electronic-signature, recovery verification, calendar authorization, healthcare, and push-related disclosures must not be satisfied only by general Terms when the policy requires standalone presentation.
7. **Contextual consent records remain contextual truth.** `VerificationConsent`, `AgreementElectronicConsent`, and `DigitalGoodsTermsAcceptance` may coexist because they capture domain-specific state, not because they own generic version proof.
8. **Consumers call the public interface.** Direct foreign inserts or proof queries against `ConsentLog` are prohibited outside approved migrations/reporting tooling.
9. **The User identity comes from Identity.** Browser/client input must not be trusted to choose the accepting `userId` for a self-acceptance command.
10. **Evidence is minimized.** Raw IP addresses are not stored in `ConsentLog`; hashing uses the canonical security primitive and raw request evidence is not copied into logs/events.
11. **Version content is immutable after publication.** This becomes binding for the future catalog once U-CL01-13 is resolved; content changes create a new version rather than rewriting historical meaning.
12. **Privacy orchestration is external.** Consent executes an instruction against its records; it never creates its own erasure job system.
13. **Support records do not replace proof.** Audit and observability may describe an operation but do not substitute for a valid `ConsentLog`.
14. **Unresolved legal semantics fail closed.** Withdrawal, re-consent, retention, decline proof, and destructive erasure are not guessed in implementation.

---

## 6. Proposed Folder / Code Structure

**Proposed Ruling CD-PR-01:** preserve a feature-first module boundary. Exact repository roots must follow the actual Workin Ants code standards; this layout describes responsibilities, not a mandate to create empty directories.

```text
src/modules/consent-disclosure/
├── actions/                 # thin first-party delivery adapters, only if the repo uses Server Actions here
├── commands/
│   └── record-consent-proof.*
├── queries/
│   ├── query-consent-proof.*
│   └── list-consent-history.*
├── schemas/                 # runtime request/result validation for this Module boundary
├── domain/
│   ├── proof-policy.*
│   └── standalone-policy.*
├── repositories/
│   └── consent-log-repository.*
├── contracts/               # public DTOs/interfaces; no foreign repositories
├── components/              # reusable consent presentation only when UI is required
├── privacy/                 # Consent implementation of Privacy-defined executor/enumeration contracts
├── events/                  # event payload definitions only if a formal event contract is approved
└── tests/
```

After U-CL01-13 is resolved, add only the code areas actually required for the accepted version-catalog design, for example a catalog repository/policy. Do **not** create `providers/` because this Module owns no external provider integration. Do **not** create a `workers/` directory unless an approved Consent-owned asynchronous responsibility exists.

Shared authentication, authorization, idempotency, hashing, audit, queue, notification, privacy orchestration, and observability code stays in its canonical owner.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / UI | validated acceptance/history endpoints and reusable standalone presentation shell | session parsing, provider authorization, consumer workflow transitions |
| Application commands | orchestration of `recordConsentProof` and future catalog commands after architecture approval | generic idempotency storage, foreign-domain mutations |
| Application queries | `queryConsentProof`, consent history, future active-version lookup | consumer eligibility/business decisions |
| Domain policy | exact version matching, acceptance evidence rules, standalone policy, future re-consent policy | Role permission policy, billing/verification/calendar policy |
| Repository / data access | Consent-owned `ConsentLog` reads/inserts; future Consent catalog only after approval | Verification/Order/Calendar/Track repositories |
| Contracts | stable proof/version/history DTOs and reason codes | provider-native types, foreign model types as public contracts |
| Events | minimized Consent fact events if formally approved | event bus/outbox mechanics, disguised commands to consumers |
| Privacy executor | enumerate and execute Privacy-issued instructions against Consent-owned records | PrivacyRequest/DataErasureJob orchestration or retention-exemption lifecycle |
| Workers | none confirmed today | custom queue framework or consumer workflow jobs |
| Provider adapters | none | Stripe, Cronofy, screening, browser-permission, e-sign, email/SMS/push clients |

---

## 8. Data Model

### 8.1 `ConsentLog`

**Purpose:** authoritative version-specific acceptance proof.

**Key relationships:**

- belongs to `User` through `userId`;
- may be referenced by `CalendarConnection`;
- may be referenced by `VerificationConsent` and `VerificationCheck`;
- may be referenced by `DigitalGoodsTermsAcceptance`;
- may be referenced by `AgreementElectronicConsent`.

These relations allow consumers to freeze proof references; they do not transfer ownership of those consumer records to Consent.

**Authoritative fields:** `id`, `userId`, `type`, `version`, `acceptedAt`, `ipHash`, `userAgent`, `createdAt`.

**Lifecycle/status fields:** none. Existence means accepted proof.

**Current indexes:** by `[userId, type, acceptedAt]` and `[type, version]`.

**Uniqueness / idempotency:** no database uniqueness currently distinguishes retry duplicates from intentional re-acceptance. U-CL01-14 is a production architecture gate. SH-044 must protect command retries in the interim without falsely claiming permanent database uniqueness semantics.

**Concurrency-sensitive behavior:** duplicate simultaneous acceptance requests for the same semantic command. The accepted idempotency key policy must distinguish replay from a later independent acceptance.

**Retention/privacy:** current `User → ConsentLog` relation uses `onDelete: Cascade`, while the privacy vocabulary contains a `consent_proof` retention-exemption reason. This is an explicit architecture conflict. No destructive migration or production hard-delete behavior may be implemented until U-CL01-15 resolves retention, pseudonymization, and referential behavior.

### 8.2 `ConsentType`

**Purpose:** controlled vocabulary identifying the meaning of the proof.

Consumer Modules may define which type they require for their action; they must not introduce a parallel generic consent enum.

### 8.3 Required future version-catalog truth — schema unresolved

SH-009 and CL-01 confirm that Consent owns active-version resolution, but no current Prisma model persists that truth. **Do not invent a model name or migration in feature code.** U-CL01-13 must first settle at minimum:

- stable document/type identity;
- immutable version identifier;
- controlled content or content reference;
- canonical content hash when required;
- effective/supersession semantics;
- publication state and publishing authority;
- locale and jurisdiction applicability if supported;
- standalone-presentation requirement if persisted;
- material-change/re-consent metadata;
- retention and audit requirements.

`ConsentLog` must not be overloaded to become the content catalog.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Consent proof lifecycle

There is one current transition:

```text
NO_PROOF_FOR_THIS_ACCEPTANCE
        │ explicit, validated acceptance
        ▼
CONSENT_LOG_CREATED
        │
        └── terminal historical evidence
```

**Transition owner:** Consent & Disclosure.

**Trigger:** successful `recordConsentProof` command by the accepting User/system context allowed by policy.

**Terminal state:** the historical proof row remains evidence. It is not mutated into “withdrawn.”

**Reversal/reopen:** none in the current schema. Privacy-authorized erasure/anonymization/retention is a separate data-rights effect, not a normal lifecycle reversal.

**Concurrency expectation:** semantic retries must return the same command result after U-CL01-14 policy is applied; independent later acceptance may need a distinct history row.

**Event/history proof:** the row itself is proof. Audit/Event records are supplemental.

**Prohibited shortcuts:** no insertion by a consumer Module; no marking proof accepted based on provider/browser state; no mutation of version after insertion.

### 9.2 Withdrawal / revocation / decline / re-consent

**Unresolved:** U-CL01-16. No status values or transition graph may be introduced here until policy is approved per ConsentType or policy family.

### 9.3 Consent-version catalog lifecycle

**Unresolved:** U-CL01-13. The Module owns the capability, but the actual status vocabulary and transitions are not defined by current evidence. Do not invent `draft/published/retired` schema merely because such states are common.

---

## 10. Commands

### 10.1 `recordConsentProof` — SH-007

**Purpose:** persist exact accepted version proof.

**Actor/context required:** authenticated User for account-bound proof; trusted request context. Any non-user/system acceptance path must be separately authorized and explicitly supported by architecture rather than inferred.

**Authoritative inputs:**

- actor from SH-001, not client-selected `userId` for self acceptance;
- validated `ConsentType`;
- exact version string;
- explicit acceptance intent;
- trusted request metadata from server context.

`acceptedAt`, raw IP, and hash generation are server-controlled. A client does not authoritatively provide them.

**Preconditions:** supported type, nonblank version, actor matches subject, explicit acceptance, command idempotency context available.

**State written:** one `ConsentLog` proof for the semantic acceptance.

**Shared operations consumed:** SH-001, SH-044, SH-076, SH-032, SH-034; SH-029 only for material/admin-required audit; SH-046 only if a formal durable event consumer exists.

**Effects:** optional minimized event/audit request after the source write; no consumer lifecycle mutation.

**Idempotency:** mandatory at the command boundary. Final semantic uniqueness remains gated by U-CL01-14.

**Failure modes:** invalid type/version, unauthenticated actor, subject mismatch, idempotency conflict, database failure, unavailable canonical security primitive.

### 10.2 Future catalog publish/change command — gated

Consent & Disclosure is the probable/Cluster-confirmed owner of version publication, but command names, statuses, approval authority, and persistence are not binding until U-CL01-13 is resolved. A coding agent must stop rather than create `publishConsentVersion` from convention.

### 10.3 Withdrawal command — prohibited until resolved

No `withdrawConsent` / `revokeConsent` command is approved today. U-CL01-16 must first decide which types are revocable and how current state is represented while preserving history.

---

## 11. Queries / Decisions

### 11.1 `queryConsentProof` — SH-008

**Consumers:** all workflows requiring exact proof.

**Input:** subject User ID from trusted server context or approved owner facts, `ConsentType`, required exact version; optionally proof ID for direct evidence lookup.

**Result:** a typed response such as accepted/not accepted plus, when accepted, `consentLogId`, type, version, and `acceptedAt`. Request evidence fields are not returned by default.

**Kind:** source-truth proof decision.

**Stable reasons:** `PROOF_FOUND`, `PROOF_NOT_FOUND`, `VERSION_NOT_ACCEPTED`, `INVALID_REQUIREMENT` are suitable contract categories; exact code vocabulary may follow root result standards.

**Consumer must not infer:** authorization, provider state, eligibility, subscription status, agreement execution, verification success, browser permission, healthcare readiness, or downstream legal sufficiency.

### 11.2 `listUserConsentHistory`

**Consumers:** User self-service and authorized support/admin/compliance review.

**Input:** subject User, optional type/date filters, pagination.

**Result:** ordered proof records with safe fields. IP hash and user agent are excluded by default and exposed only if a separately approved sensitive-access use case requires them.

**Kind:** source-truth history.

### 11.3 `resolveActiveConsentVersion` — SH-009

**Consumers:** every presentation workflow.

**Input:** consent type, effective time, and only those locale/jurisdiction/context facts adopted by U-CL01-13.

**Result:** exact active version plus controlled presentation metadata and content/content reference.

**Status:** public capability confirmed; production implementation blocked by U-CL01-13.

**Consumer must not infer:** that the User accepted that version. It must call SH-008 or obtain SH-007 proof after presentation.

### 11.4 Standalone presentation decision

The Module owns whether its configured consent must be presented separately. The exact persistence mechanism is part of U-CL01-13. A consumer may supply workflow context, but it may not quietly downgrade a Consent-required standalone disclosure into general Terms.

---

## 12. Public Module Interface

### Confirmed public commands

- **SH-007 `recordConsentProof`** — canonical generic acceptance command.

### Confirmed public queries

- **SH-008 `queryConsentProof`** — canonical exact-proof lookup.
- `listUserConsentHistory` — module query for self/admin review, authorization-gated.

### Confirmed capability, implementation-gated

- **SH-009 `resolveActiveConsentVersion`** — owner confirmed, persistence blocked by U-CL01-13.
- **SH-010 `presentStandaloneConsent`** — reusable application/UI capability. Before SH-009 is production-ready, it may accept a trusted server-supplied exact presentation descriptor without inventing a catalog.

### Privacy executor

- **SH-096 `enumerateSubjectData`** implementation for Consent-owned records.
- **SH-097 `evaluateRetentionRequirement`** Consent-owned facts supplied to Privacy.
- **SH-095 `executePrivacyInstruction`** implementation against Consent-owned records, with destructive behavior gated by U-CL01-15.
- SH-098 shared anonymization primitive when an approved field mapping exists.

### Emitted domain events

No event name is currently binding. Prefer source queries unless a consumer has a durable asynchronous requirement. Any formal event must be versioned, minimized, and emitted through SH-046 after the source transaction.

### Provider-facing interfaces

None. This Module owns no provider integration.

---

## 13. Inbound Dependencies

| Owning Module / platform | Interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | SH-001 `resolveAuthenticatedActor` | establish accepting User and trusted actor context | User ID, actor assurance/context | yes | session parser, current-user helper, auth provider logic |
| Role / Authority | SH-002 `authorizeResourceAction` | protect admin/support history and future catalog administration | actor, action, resource/subject facts | yes | `consentAdminGuard`, local admin role logic |
| Platform application infrastructure | SH-044 `executeIdempotentCommand` | prevent retry duplicates | semantic command key and operation result | yes for mutation | Consent-only idempotency store |
| Shared security | SH-076 `normalizeAndHashIdentifier` | create stable privacy-safe IP/request evidence | raw value only in trusted boundary, purpose/version | yes if evidence required | `hashIp.ts`, local crypto/HMAC |
| Shared security | SH-072 `hashCanonicalPayload` | future consent-content integrity hash after catalog decision | canonical content bytes/fields + purpose | only where catalog requires | local SHA helper |
| Shared versioning | SH-080 `manageVersionedRules` | future immutable effective-dated consent catalog mechanics | accepted catalog record + Consent policy | gated | generic local version framework |
| Audit / Event Ledger | SH-029 / SH-030 | material action audit and policy-required sensitive history access | safe IDs, action, actor, correlation | usually no for source proof; may block privileged access by policy | local audit table/logger |
| Observability / Ops | SH-032/033/034/036/037 | request correlation, safe logs/metrics/failure reporting | safe dimensions only | no business success fabrication | local telemetry framework |
| Notification | SH-041 `requestNotification` | future re-consent/version-change notice | notification intent + safe variables | no change to proof truth | mail/SMS/push sender |
| Privacy / Data Erasure | SH-095/096/097 | privacy orchestration and target execution | subject, instruction, retention context | destructive action blocked when retention unresolved | privacy jobs/exemption tables |

The Module may also consume narrow plan/workflow context from a consumer owner when needed to choose a disclosure version, but such context must arrive through that owner’s public contract; Consent must not import its repository.

---

## 14. Outbound Consumers and Effects

Major consumers include:

- **Identity & Access:** passkey, SMS MFA, sensitive financial access, recovery identity verification, and phone-update disclosure proof;
- **Trust Verification / Screening:** standalone FCRA/license/DMV proof while retaining `VerificationConsent` and check lifecycle;
- **Booking & Calendar:** calendar sync/free-busy/writeback/disconnect disclosure proof while retaining `CalendarConnection`;
- **Notification:** web-push/PWA disclosure proof while retaining browser permission and subscription state;
- **Transaction / Order:** electronic records/signature/agreement-execution/manual-opt-out disclosure proof while retaining `AgreementElectronicConsent` and Agreement lifecycle;
- **Digital Goods Access:** terms/refund/license/declaration/accessibility proof while retaining `DigitalGoodsTermsAcceptance` and delivery truth;
- **Healthcare / Regulated Services:** disclosure proof while retaining `BaaAgreement` and healthcare readiness;
- **Track Subscription & Entitlement:** subscription terms, recurring billing, plan change, commission, and buyer fee-waiver proof while retaining commercial lifecycle truth;
- **Sweepstakes / Prize and Gamification / Rewards:** rules/terms/reward proof while retaining entries/draws/points/rewards;
- **Admin Review / Compliance Hold:** read-only evidence for review; the hold lifecycle remains external;
- **Privacy / Data Erasure:** data inventory/export/retention execution through the privacy protocol.

Consent & Disclosure must not mutate these consumers’ records directly. Where a contextual record stores a `consentLogId`, the consumer’s command owns that write.

---

## 15. Canonical Shared Operations Used

Only operations materially relevant to this Module are listed here. The Canonical Shared Operations Registry remains authoritative for full definitions.

### SH-001 — `resolveAuthenticatedActor`

- **Classification:** canonical platform capability.
- **Owner:** Identity & Access.
- **Meaning:** resolve a valid session/system credential to trusted Workin Ants actor context.
- **Why used:** establish who is accepting or administering consent.
- **Invocation:** before account-bound acceptance and protected history/catalog operations.
- **Local policy:** which Consent action requires self vs privileged authority.
- **Expected result:** typed actor/User context.
- **Do not build:** `consentAuth.ts`, `getCurrentUser.ts`, route-local session parser.

### SH-002 — `authorizeResourceAction`

- **Classification:** canonical cross-cutting capability.
- **Owner:** Role / Authority.
- **Meaning:** decide whether an actor may perform a named protected action.
- **Why used:** admin/support history and any future catalog administration.
- **Invocation:** after actor resolution, before privileged read/mutation.
- **Local policy:** Consent supplies action vocabulary and subject/resource facts.
- **Expected result:** allow/deny decision with stable reason.
- **Do not build:** `consentAdminGuard.ts`, `canViewConsents.ts`, `isAdmin.ts`.

### SH-007 — `recordConsentProof`

- **Classification:** canonical platform consent capability.
- **Owner:** Consent & Disclosure.
- **Meaning:** persist exact version acceptance evidence.
- **Why used:** this is the Module’s primary public mutation.
- **Invocation:** after validated explicit acceptance.
- **Local policy:** proof fields, type/version rules, evidence minimization.
- **Expected result:** authoritative proof reference.
- **Do not build:** per-feature terms/calendar/FCRA/subscription consent repositories.

### SH-008 — `queryConsentProof`

- **Classification:** canonical platform consent capability.
- **Owner:** Consent & Disclosure.
- **Meaning:** answer whether required exact proof exists.
- **Why used:** all consumers should use this instead of direct `ConsentLog` access.
- **Invocation:** consumer gate or evidence lookup.
- **Local policy:** exact matching and safe result fields.
- **Expected result:** accepted/not accepted + proof reference/evidence.
- **Do not build:** `hasAcceptedTerms.ts`, `checkCalendarConsent.ts`, `billingConsentCheck.ts`.

### SH-009 — `resolveActiveConsentVersion`

- **Classification:** cross-cutting capability.
- **Owner:** Consent & Disclosure.
- **Meaning:** select currently applicable consent/disclosure version.
- **Why used:** eliminate consumer hard-coded version constants.
- **Invocation:** before presentation.
- **Local policy:** applicability, material change, supersession, re-consent.
- **Expected result:** exact active version descriptor.
- **Do not build:** `currentTerms.ts`, `termsVersionService.ts` inside consumer Modules.
- **Gate:** U-CL01-13.

### SH-010 — `presentStandaloneConsent`

- **Classification:** cross-cutting UI/application capability.
- **Owner:** Consent & Disclosure.
- **Meaning:** present high-risk disclosure separately and submit acceptance through SH-007.
- **Why used:** consistent evidence and accessibility.
- **Invocation:** consumer workflow immediately before the protected handoff when standalone proof is required.
- **Local policy:** Consent presentation rules; consumer supplies workflow context.
- **Expected result:** presented descriptor + acceptance proof or explicit non-acceptance outcome.
- **Do not build:** `FcraConsentModal`, `CalendarConsentModal`, `PushConsentModal` each with independent proof logic.

### SH-029 — `appendAuditEvent`

- **Classification:** platform audit capability.
- **Owner:** Audit / Event Ledger.
- **Meaning:** append generic audit evidence for material actions.
- **Why used:** approved admin/catalog/privacy-sensitive operations.
- **Invocation:** after or transactionally correlated with source operation according to Audit contract.
- **Local policy:** Consent action name and safe IDs only.
- **Expected result:** audit acknowledgement/reference.
- **Do not build:** `consentAuditService.ts`, local audit table.

### SH-030 — `recordSensitiveAccess`

- **Classification:** cross-cutting audit capability.
- **Owner:** Audit / Event Ledger.
- **Meaning:** record access to sensitive information when policy requires it.
- **Why used:** privileged history/evidence reads only if the Consent sensitive-access audit decision classifies them as sensitive.
- **Invocation:** authorized sensitive read.
- **Local policy:** what fields/operation count as sensitive.
- **Expected result:** access-audit proof.
- **Do not build:** `consentAccessLog`.

### SH-032 / SH-033 / SH-034 — request context, structured logging, telemetry sanitization

- **Classification:** platform primitives/capabilities.
- **Owner:** Observability / platform infrastructure.
- **Why used:** correlation and safe operations diagnostics.
- **Local policy:** never log raw IP, consent text, tokens, or unneeded user-agent data.
- **Do not build:** Consent logger/context/redaction frameworks.

### SH-036 / SH-037 — metrics and integration failure

- **Classification:** Observability capabilities.
- **Owner:** Observability / Ops.
- **Why used:** track acceptance/query/catalog failures without changing business truth.
- **Local policy:** low-cardinality type/reason/status dimensions; no sensitive payloads.
- **Do not build:** Consent ops tables.

### SH-041 — `requestNotification`

- **Classification:** platform notification capability.
- **Owner:** Notification.
- **Why used:** only when approved version/re-consent policy requires a notice.
- **Invocation:** after the relevant Consent source change is committed.
- **Local policy:** reason and required version; Notification owns channels/delivery.
- **Do not build:** `sendConsentEmail.ts`, `termsNotifier.ts`, push/SMS providers.

### SH-044 — `executeIdempotentCommand`

- **Classification:** platform primitive.
- **Owner:** platform application infrastructure.
- **Why used:** retry-safe acceptance and privileged catalog/privacy mutations.
- **Invocation:** command boundary before source write.
- **Local policy:** semantic key and replay result, subject to U-CL01-14.
- **Do not build:** `consentIdempotency.ts`, custom idempotency table.

### SH-046 — `publishDomainEvent`

- **Classification:** platform event/outbox primitive.
- **Owner:** platform event infrastructure.
- **Why used:** only for approved durable Consent fact events.
- **Invocation:** transactionally after source state is committed.
- **Local policy:** event name/version/minimized payload.
- **Do not build:** `consentEventBus.ts`, `consentQueue.ts`.

### SH-072 — `hashCanonicalPayload`

- **Classification:** platform security primitive.
- **Owner:** shared security/cryptography.
- **Why used:** future content hash/integrity proof if U-CL01-13 requires it.
- **Invocation:** canonical consent-content creation/publishing.
- **Local policy:** canonical fields and what the hash proves.
- **Do not build:** local SHA/HMAC helpers.

### SH-076 — `normalizeAndHashIdentifier`

- **Classification:** platform security primitive.
- **Owner:** shared security/cryptography.
- **Why used:** privacy-safe IP/request evidence.
- **Invocation:** trusted server request boundary before `ConsentLog` insert.
- **Local policy:** whether IP evidence is necessary and retained for the consent type.
- **Do not build:** `hashIp.ts`, `consentIpHasher.ts`.

### SH-080 — `manageVersionedRules`

- **Classification:** shared mechanism / separate policy.
- **Owner:** each policy Module using the shared versioning mechanism.
- **Why used:** future immutable effective-dated consent catalog mechanics.
- **Invocation:** only after U-CL01-13 approves persistence/status semantics.
- **Local policy:** Consent version meaning, applicability, standalone and re-consent policy.
- **Do not build:** an unrelated Consent-only generic version engine.

### SH-095 / SH-096 / SH-097 / SH-098 — privacy owner protocol

- **Classification:** cross-cutting privacy protocol/capability.
- **Owner:** Privacy orchestrates; Consent owns execution against its records; shared primitive for approved anonymization.
- **Why used:** inventory/export/erase/anonymize/retain Consent data without moving Privacy lifecycle into this Module.
- **Invocation:** Privacy-authorized target execution.
- **Local policy:** Consent field disposition and retention facts after U-CL01-15.
- **Expected result:** typed target execution result.
- **Do not build:** `gdprConsentWorker.ts`, `ConsentPrivacyRequest`, local retention-exemption table.

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Truth affected | Why local |
|---|---|---|---|---|---|
| validateConsentAcceptance | enforce type/version/explicit-intent rules before SH-007 write | actor, type, version, acceptance payload | validated acceptance intent or domain error | none | Consent defines what constitutes valid proof creation |
| buildConsentProofResult | expose only safe proof fields | ConsentLog | public proof DTO | none | prevents request evidence leakage |
| matchExactConsentVersion | determine whether a proof satisfies an exact requirement | proof + required type/version | match/no-match + reason | none | core Consent semantics |
| classifyStandaloneRequirement | determine standalone presentation requirement | consent type + approved context | standalone/general result | none | Consent policy, not consumer UI preference; persistence is partly gated by U-CL01-13 |
| filterConsentHistory | apply self/admin field-redaction rules | actor/subject/filter | safe history page | none | Consent knows proof sensitivity while Role decides authority |
| mapConsentPrivacyDisposition | map Privacy instruction to allowable Consent-owned effects | instruction + approved retention facts | local execution plan | ConsentLog only | record-owner responsibility; destructive paths gated by U-CL01-15 |

Do not turn these into generic platform utilities.

---

## 17. Shared Mechanism / Separate Truth Rules

| Shared mechanism | Consent truth | Separate domain truth that must remain separate |
|---|---|---|
| generic versioned proof | `ConsentLog` | `VerificationConsent` subject/check context |
| generic versioned proof | `ConsentLog` | `AgreementElectronicConsent` agreement-specific status/manual opt-out/execution context |
| generic versioned proof | `ConsentLog` | `DigitalGoodsTermsAcceptance` purchase/delivery-context status and hashes |
| disclosure proof | `ConsentLog.healthcare_baa` or related type | `BaaAgreement` signed/executed BAA lifecycle |
| disclosure proof | calendar-related ConsentType | `CalendarConnection` provider/link lifecycle |
| disclosure proof | `web_push_notifications` | browser permission and `NotificationSubscription` state |
| commercial terms proof | subscription-related ConsentTypes | `TrackSubscription`, plan/entitlement/usage truth |
| age-related acknowledgment | `ConsentType.age_gate`, if used for disclosure | `AgeGateAttempt`, `AgeGateBlock`, eligibility decision owned by Identity |
| shared idempotency | SH-044 | Consent acceptance semantics remain Consent-owned |
| shared versioning | SH-080 | Consent version content/applicability policy remains Consent-owned |
| shared hashing | SH-072/076 | what an IP/content hash proves remains Consent-specific |
| shared privacy workflow | SH-095–098 | Privacy job/exemption truth remains Privacy-owned; Consent executes only its records |

Rule: **do not remove a contextual domain record merely because it references `ConsentLog`.** Remove duplication only when the second record duplicates generic acceptance proof and owns no distinct lifecycle/context.

---

## 18. Authentication and Authorization

- Account-bound acceptance requires SH-001 authenticated actor resolution.
- The self-acceptance command derives the accepting User from trusted actor context. A client-supplied `userId` cannot make another User accept.
- User self-history access is constrained to the current User unless a separate authority result permits another subject.
- Admin/support/compliance history access uses SH-002; no role checks are hard-coded inside Consent.
- Any future consent-version administration also uses SH-002 and, if root security policy classifies it as sensitive, SH-014 step-up. That classification is not invented here.
- Consent supplies resource facts such as consent type/version/subject ID; Role / Authority decides permission.
- Organization membership or participant context is not normally part of generic Consent proof unless an approved consumer context requires it. If needed, the source owner supplies those facts through its public interface.
- Generic authorization infrastructure must not be added to this Module.

---

## 19. Compliance / Readiness / Entitlement Gates

Consent & Disclosure is itself usually **a gate supplier**, not a gate composer.

| Underlying truth owner | Query | Target action | Consent-local composition | Result |
|---|---|---|---|---|
| Identity & Access | SH-001 actor context | record account-bound proof | subject must equal accepting actor | accept command may proceed |
| Role / Authority | SH-002 | history/catalog administration | Consent supplies action/resource facts | allow/deny privileged operation |
| Consent & Disclosure | SH-008 | consumer-owned protected action | consumer names required type/version | proof found/not found; consumer decides action |
| Consent & Disclosure | SH-009 | present current disclosure | Consent resolves exact version | version descriptor; not proof |

This Module does **not** compose professional readiness, healthcare readiness, entitlement, payment, ComplianceHold, or verification success to decide consumer workflows. The consumer owns that gate chain.

---

## 20. Provider Integrations

This Module owns **no direct external provider integration**.

Specifically prohibited here:

- Cronofy/calendar OAuth clients or webhooks;
- screening/FCRA provider clients or webhook processors;
- Stripe Billing/Checkout/provider state;
- browser notification permission API state as domain truth;
- push/SMS/email delivery providers;
- e-signature provider lifecycle;
- healthcare provider integrations;
- identity-verification provider state.

A provider-owning Module may require a Consent proof before it begins its provider flow. It calls SH-008 and/or receives a `consentLogId`; Consent never authorizes the provider connection itself.

---

## 21. Events and Outbox

### Current binding position

No Consent event name is yet required as source truth. Consumers should query SH-008 unless there is a real asynchronous need.

### If formal events are approved

Use SH-046 and a transactional outbox. Event payloads must include only necessary facts such as:

- event ID/version;
- consentLogId;
- User ID only if required by consumer contract;
- consent type/version;
- acceptedAt;
- correlation/causation IDs.

Do not include raw IP, raw user agent, full consent text, or unrelated actor data.

Potential event concepts (`proof_recorded`, `version_published`, `version_superseded`, `withdrawal_recorded`) are **Proposed / unresolved**, not permission to implement all of them.

Events describe facts. They must not encode commands such as “activate calendar,” “start screening,” “enable subscription,” or “grant download.” Those actions remain consumer-owned.

---

## 22. Background Jobs / Scheduled Work

No Consent-owned background worker is currently required for the core acceptance/proof path.

Possible future work is gated:

- re-consent targeting/notification after a material version change — depends on U-CL01-13/U-CL01-16 and must call Notification rather than deliver itself;
- privacy target execution — Privacy owns orchestration; Consent implements its executor and may run under shared queue infrastructure when instructed;
- catalog integrity/reconciliation — only if the accepted version model requires it.

Any approved worker must use the shared queue/retry/dead-letter infrastructure. A Consent-specific queue framework is prohibited.

---

## 23. Concurrency and Idempotency

### Acceptance race

Two retries of the same semantic acceptance must not create uncontrolled duplicate proof. Use SH-044. U-CL01-14 must define the durable semantic key/uniqueness policy before final production constraints are introduced.

**Likely aggregate/resource key:** accepting User + consent type + version + semantic acceptance intent/idempotency key. This is not yet a database uniqueness ruling.

**Transaction boundary:** create `ConsentLog` and any required transactional outbox entry atomically. Audit/notification failures must not fabricate or erase source proof.

**Replay result:** same semantic command returns the already-created proof result; a deliberately new later acceptance may create a separate historical proof if policy permits.

### Version-catalog race

Publishing/superseding versions is blocked until U-CL01-13 defines constraints. When implemented, use database constraints/optimistic concurrency or aggregate locking from shared primitives rather than in-memory locks.

### Prohibited

- in-memory mutexes;
- `findFirst` then unguarded insert as the sole retry protection;
- arbitrary `@@unique([userId,type,version])` added without resolving intentional re-acceptance semantics.

---

## 24. Media / Storage

No file/media workflow is currently part of Consent & Disclosure source truth.

If a future consent document is stored as a file, Media / File Access still owns object storage, validation, scanning, signed access, and deletion mechanics. Consent may own only the business reference and version/hash meaning after an architecture ruling.

No MediaAsset model or signed-URL helper should be created here.

---

## 25. Search / Projection

Consent proof is private compliance evidence and is not a public Search projection.

- No Typesense document is owned here.
- No SearchUpsertEvent should be emitted merely because a User accepted terms.
- Search must not reconstruct consent proof from other projections.
- If a future public feature’s readiness changes because its consumer reacts to Consent, that consumer/source owner requests its own Search projection update.

---

## 26. Notification

Consent owns the **business trigger intent**, not delivery.

Examples of future valid intents include:

- material terms version requires re-consent;
- a required consent is missing before a workflow resumes;
- a legally required disclosure version changed.

Use SH-041 with safe variables such as consent type, required version, deadline/effective date if approved, and navigation intent. Do not send email/SMS/push directly and do not store delivery state in Consent.

Base proof recording does not require a notification by default.

---

## 27. Audit and Sensitive Access

Three truths stay distinct:

1. **`ConsentLog`** — domain proof that acceptance occurred.
2. **`AuditEvent`** — generic audit evidence about material operations, owned by Audit / Event Ledger.
3. **`AccessAuditLog`** — sensitive-access proof, also Audit-owned.

Do not log every acceptance as a substitute for `ConsentLog`. Do not copy `ipHash`, raw user agent, or full consent text into generic audit payloads unless an explicitly approved audit matrix requires a minimized field.

Consent sensitive-access audit decision must determine which admin/support history reads require SH-030. Self-history reads do not become “sensitive access” automatically merely because the model is compliance-related.

---

## 28. Privacy and Retention

### Subject-data inventory

Consent-owned personal/linked data includes:

- `ConsentLog.userId`;
- `type`, `version`, `acceptedAt`, `createdAt` linked to a User;
- `ipHash`;
- `userAgent`;
- relational references from consumer records to `ConsentLog`.

### Privacy executor responsibilities

Consent implements:

- SH-096 subject-data enumeration;
- export-safe serialization of Consent-owned proof where required;
- SH-097 retention facts owned by Consent;
- SH-095 execution against Consent-owned data after Privacy issues an instruction;
- SH-098 anonymization only using an approved field map.

### Retention conflict / hard gate

Current cascade deletion can remove `ConsentLog` when `User` is deleted, while the privacy vocabulary explicitly recognizes `consent_proof` as a retention-exemption reason. U-CL01-15 must settle:

- minimum/maximum retention by consent category or legal purpose;
- whether retained proof keeps a User FK, pseudonymous subject key, or other identity reference;
- what happens to `ipHash` and `userAgent`;
- relational behavior for consumer references;
- export behavior;
- when physical deletion is permitted.

Until resolved, destructive Consent erasure/hard-delete migrations remain disabled. Privacy may still enumerate/export and return a structured “retention decision required” result rather than guessing.

Privacy / Data Erasure owns the request/job/target/exemption lifecycle throughout.

---

## 29. Observability

Use canonical request context and telemetry.

### Structured logs

Safe dimensions may include:

- operation name;
- consent type;
- result/reason code;
- correlation ID;
- duration;
- database conflict/retry count;
- catalog state category after a catalog exists.

Do not log:

- raw IP addresses;
- full user-agent strings unless an approved secure diagnostic path requires them;
- consent text;
- cookies/session tokens;
- provider secrets;
- full request payloads;
- unnecessary User identifiers in metrics.

### Metrics / health

Useful metrics include acceptance success/failure rate, query latency, idempotency replay count, catalog-resolution failure count, privacy executor failures, and unauthorized admin-read attempts. Health checks may verify that an active-version catalog is internally consistent after that capability exists.

Operational records never replace `ConsentLog` or future version-catalog truth.

---

## 30. Security Boundaries

- Validate every server/external trust-boundary payload using the project runtime validation standard.
- Derive authenticated User from SH-001, not browser-provided identity.
- Enforce SH-002 on privileged reads/mutations.
- Reject unknown `ConsentType`, blank/oversized version identifiers, malformed filters, and untrusted metadata.
- Use SH-076 for IP/request identifier hashing. No raw IP storage in ConsentLog.
- Use SH-072 for content integrity only after canonical input is defined; never hand-roll hashes.
- Treat user agent and IP hash as potentially identifying metadata; minimize exposure.
- Rate-limit abusive public acceptance/query surfaces using root/platform controls if exposed to browsers.
- Never expose ConsentLog request evidence in ordinary public proof DTOs.
- Do not accept consent on behalf of another User without an explicit, separately authorized architecture path.
- No provider credentials or webhooks exist in this Module.
- No temporary secret/token mechanism is required by the core proof flow.

---

## 31. Error / Decision Result Pattern

Public interfaces should use stable domain categories rather than leaking Prisma or provider errors.

Recommended result categories:

- `OK` / `PROOF_FOUND`;
- `PROOF_NOT_FOUND`;
- `VERSION_NOT_ACCEPTED`;
- `VALIDATION_ERROR`;
- `UNAUTHENTICATED`;
- `FORBIDDEN`;
- `IDEMPOTENCY_CONFLICT`;
- `CONCURRENT_MODIFICATION` for future catalog mutations;
- `ACTIVE_VERSION_UNAVAILABLE` when SH-009 cannot resolve an applicable version;
- `ARCHITECTURE_GATED` for behavior blocked by unresolved U-CL01 decisions in non-production/admin tooling;
- `RETENTION_BLOCKED` / `RETENTION_DECISION_REQUIRED` for Privacy execution;
- `DEPENDENCY_UNAVAILABLE` when a required canonical platform dependency fails;
- `INTERNAL_FAILURE` with correlation ID only.

Do not expose database stack traces, SQL errors, raw cryptography failures, or consumer/provider-native status values.

---

## 32. Testing Architecture

### Domain unit tests

- exact type/version matching;
- standalone policy fixtures for approved types;
- proof DTO redaction;
- evidence-minimization mapping;
- future active-version applicability only after U-CL01-13.

### State / lifecycle tests

- explicit acceptance creates proof once per semantic command;
- historical proof cannot be mutated by normal product commands;
- no invented revoke/withdraw transition exists before U-CL01-16.

### Public contract tests

- SH-007 request/result contract;
- SH-008 exact proof lookup;
- safe consent history pagination/redaction;
- SH-009/010 once version catalog is approved;
- Privacy SH-095/096/097 implementation.

### Database / integration tests

- Prisma relation behavior;
- current indexes/query plans;
- transaction with idempotency and optional outbox;
- consumer proof-reference integrity without foreign writes;
- clean migration tests for any accepted catalog/retention change.

### Authorization / RLS tests

- self acceptance;
- other-user spoof attempt denied;
- self history vs other-user history;
- admin/support allow/deny matrix;
- direct table access/RLS parity according to root policy.

### Compliance tests

- generic Terms cannot satisfy FCRA/e-sign/calendar/etc. exact standalone requirement;
- browser permission state does not create proof;
- proof does not cause verification/calendar/subscription/agreement transition;
- `age_gate` proof cannot replace Identity age eligibility.

### Idempotency / concurrency tests

- duplicate request replay;
- simultaneous same-key acceptance;
- different independent acceptance keys preserve intended history after U-CL01-14;
- catalog publish race tests after U-CL01-13.

### Privacy tests

- subject enumeration;
- export field minimization;
- retention decision path;
- no destructive cascade enabled until U-CL01-15;
- anonymization/deletion only according to approved mapping.

### E2E participation tests

Representative flows should prove Consent boundaries with at least:

- standalone screening disclosure → ConsentLog proof → Trust Verification receives proof reference, but no screening result is created by Consent;
- calendar disclosure → proof → Booking owns connection state;
- electronic-signature disclosure → proof → Order owns AgreementElectronicConsent;
- subscription terms proof → Track owns enrollment state;
- push disclosure → proof while browser permission remains independent.

---

## 33. Module Invariants

**Rules coding agents must never violate:**

1. `ConsentLog` and `ConsentType` have exactly one owner: Consent & Disclosure.
2. `ConsentLog` proves acceptance only; it never proves downstream authorization, eligibility, readiness, provider state, or success.
3. The exact required consent version must be matched; “some version accepted” is not sufficient by default.
4. An accepting User is derived from trusted actor context for self acceptance; the client cannot nominate another User.
5. Only explicit acceptance creates `ConsentLog` proof.
6. Normal product code does not edit a `ConsentLog` after creation.
7. No `hasAcceptedTerms` or other feature-local generic consent boolean may become source truth.
8. No consumer Module inserts or mutates ConsentLog directly through its own repository.
9. Contextual records such as VerificationConsent, AgreementElectronicConsent, and DigitalGoodsTermsAcceptance remain separate truth.
10. Browser notification permission and NotificationSubscription state are not ConsentLog truth.
11. Calendar connection/provider state is not ConsentLog truth.
12. Screening results/adverse action are not ConsentLog truth.
13. Agreement/signature/manual-opt-out lifecycle is not ConsentLog truth.
14. BaaAgreement/healthcare readiness is not ConsentLog truth.
15. Track subscription/entitlement/billing state is not ConsentLog truth.
16. Age eligibility is not inferred from `ConsentType.age_gate`.
17. Raw IP addresses are never stored in ConsentLog or telemetry.
18. Shared idempotency, hashing, authorization, audit, notification, privacy, and observability mechanisms are consumed, not recreated.
19. No persistent consent-version schema may be invented before U-CL01-13 is resolved and architecture updated.
20. No withdraw/revoke/decline/re-consent lifecycle may be invented before U-CL01-16 is resolved.
21. No permanent database uniqueness rule may collapse intentional re-acceptance history before U-CL01-14 is resolved.
22. No destructive User/Consent delete path may bypass U-CL01-15 retention analysis.
23. Privacy orchestration remains Privacy-owned.
24. Audit and observability records supplement but never replace Consent proof.
25. Consent owns no provider webhook/client.
26. Events, if added, describe facts and never command another Module’s lifecycle.

---

## 34. Prohibited Duplicate Implementations

Do not create inside this Module or consumer Modules:

### Authentication / authorization duplicates

- `consentAuth.ts`
- `getCurrentUser.ts`
- `requireUser.ts`
- `consentAdminGuard.ts`
- `canViewConsents.ts`
- `isAdmin.ts`

### Consent proof duplicates

- `termsConsentService.ts`
- `calendarConsentService.ts`
- `pushConsentService.ts`
- `fcraConsentService.ts`
- `subscriptionConsentService.ts`
- feature-specific generic `Consent` tables
- `hasAcceptedTerms` / `hasConsent` source booleans
- consumer-owned direct ConsentLog repositories

### Versioning / hashing duplicates

- `currentTerms.ts` hard-coded per feature once SH-009 is available
- consumer `policyVersion.ts` / `termsVersionService.ts`
- `hashIp.ts`
- `consentIpHasher.ts`
- local SHA/HMAC utility
- Consent-only generic version-engine framework competing with SH-080

### Infrastructure duplicates

- `consentIdempotency.ts` or local idempotency table
- `consentEventBus.ts` / `consentQueue.ts`
- custom outbox/inbox
- custom retry/DLQ framework
- `consentAuditService.ts` / local audit table
- Consent-specific telemetry/IntegrationFailure tables
- `sendConsentEmail.ts`, SMS/push/email provider clients
- `gdprConsentWorker.ts`, local PrivacyRequest/DataErasureJob/retention-exemption tables
- any `ComplianceHold` clone

### Provider ownership violations

- Cronofy OAuth/webhook code
- screening provider callbacks
- Stripe Billing webhooks
- browser permission state store
- e-sign provider workflow

---

## 35. Unresolved Decisions

| ID | Decision | Why unresolved | Blocks |
|---|---|---|---|
| U-CL01-13 | What is the persistent consent-version catalog schema and applicability model? | SH-009 capability is confirmed but Prisma has no version/content model | production active-version resolution, catalog administration, re-consent lifecycle |
| U-CL01-16 | Which consent types support withdrawal, revocation, decline proof, or re-consent and how is current state represented? | ConsentLog models acceptance only | withdrawal commands/events/current-state query |
| U-CL01-14 | What is ConsentLog semantic idempotency/uniqueness policy? | no uniqueness constraint; retries must be deduped without erasing intentional re-acceptance history | final DB constraints and replay semantics |
| U-CL01-15 | What is ConsentLog retention and User-erasure behavior? | `onDelete: Cascade` conflicts with `consent_proof` retention exemption | destructive privacy paths and retention-safe schema migration |
| Consent sensitive-access audit decision | Which Consent history/admin reads require AccessAuditLog? | platform sensitive-access matrix not fully enumerated | final SH-030 instrumentation matrix |
| U-CL01-28 | How are subscription terms/recurring-billing consent immutably bound to enrollment/change? | Track consumer context exists but proof reference/snapshot policy is incomplete | production Track enrollment/change integration, not generic proof recording |
| U-CD-01 | When must a consumer store explicit `consentLogId` versus only query current proof? | some current models reference ConsentLog; others do not | consumer-specific historical proof contracts |
| U-CD-02 | Is version + content hash sufficient presentation proof, or is a separate presentation evidence record required? | current schema proves acceptance, not rendered presentation details | final catalog/presentation evidence design |
| U-CD-03 | Does `ConsentType.age_gate` represent only a disclosure acknowledgment? | Identity owns age eligibility and schema contains the enum value | any use of age_gate as a Consent proof type |

Implementation rule: if a numbered feature reaches one of these questions, the agent must update architecture with an approved ruling first or keep the dependent behavior disabled/stubbed/fail-closed.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. `consent_disclosure` is the Consent & Disclosure Module in CL-01, type `compliance`, status `mvp_active`.
2. Consent & Disclosure owns `ConsentLog` and `ConsentType`.
3. `ConsentLog` is source truth for exact versioned acceptance proof.
4. No ConsentLog lifecycle status exists today; the row is completed historical acceptance evidence.
5. Consent proof is not downstream permission, readiness, provider state, or compliance outcome.
6. SH-007 and SH-008 are the canonical write/read boundary for generic consent proof.
7. SH-009 and SH-010 are Consent-owned capabilities; persistent active-version implementation remains gated by U-CL01-13.
8. Consumer-specific contextual records remain owned by their domain Modules.
9. Identity owns authentication and age eligibility; Role owns permission interpretation.
10. Privacy owns privacy-request/job/retention-exemption orchestration; Consent is a target executor only.
11. Audit owns AuditEvent/AccessAuditLog; Notification owns delivery; Observability owns ops truth.
12. Consent owns no external provider integration.
13. Shared idempotency, hashing, outbox, versioning mechanics, authorization, audit, notification, privacy, and telemetry are reused rather than duplicated.
14. Destructive retention behavior is gated because current cascade deletion conflicts with consent-proof retention vocabulary.

### Proposed rulings

- **CD-PR-01:** organize implementation behind a dedicated feature-first `consent-disclosure` boundary and expose public contracts rather than direct cross-domain Prisma access.
- **CD-PR-02:** treat `ConsentLog` as append-only historical proof in ordinary product flows; any privacy-authorized destructive/anonymizing change is a separate data-rights execution path governed by U-CL01-15.
- **CD-PR-03:** consumers that need historical frozen context should store the proof ID/result in their own source record; current-state gates should query SH-008. Exact per-consumer binding remains U-CD-01.
- **CD-PR-04:** default to query-first integration; add Consent domain events only where a durable asynchronous consumer requirement exists.

### Conservative implementation posture

- no persistent version model is invented;
- no withdrawal/revocation state is invented;
- no destructive cascade migration is enabled;
- no global uniqueness constraint is added solely by convention;
- no provider code enters this Module;
- no consumer lifecycle is mutated from Consent.

---

## 37. Coding-Agent Usage

Before implementing or changing this Module, the coding agent must read, in order:

1. root `context/project-overview-v3.md`;
2. root `context/architecture.md` (**currently missing**; see `context/context-map.md`);
3. root `context/code-standards.md` (**currently missing**; see `context/context-map.md`);
4. `context/shared/shared-operations.md`;
5. CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-architecture.md`;
6. CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-build-plan.md`;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. relevant dependency/consumer public-interface sections, especially Identity & Access, Role / Authority, Privacy / Data Erasure, Audit / Event Ledger, Notification, Trust Verification / Screening, Booking & Calendar, Transaction / Order, Digital Goods Access, Track Subscription & Entitlement, Healthcare / Regulated Services, Sweepstakes / Prize, and Gamification / Rewards;
10. `progress-tracker.md` (**currently missing**; see `context/context-map.md`);
11. current Prisma schema and migrations.

Before coding a feature, the agent must confirm that none of U-CL01-13, U-CL01-16, U-CL01-14, U-CL01-15, Consent sensitive-access audit decision, U-CL01-28, or U-CD-01 through U-CD-03 blocks that feature’s production behavior.

If repository code differs from this architecture, the agent must record the conflict, preserve confirmed source-of-truth ownership, and update architecture first if a binding decision legitimately changed. Build progress may report implementation status; it may not redefine Consent ownership, proof meaning, retention policy, or shared-operation ownership.
