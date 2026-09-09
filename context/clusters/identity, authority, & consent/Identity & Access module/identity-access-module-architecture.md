# Identity & Access Module Architecture

> **Module ID:** `identity_access`  
> **Module name:** Identity & Access Module  
> **Module type:** `capability_security`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/modules/identity_access/module-architecture.md`  
> **Document status:** Implementation-grade Module architecture for the current Workin Ants MVP; confirmed rules are binding, Proposed Rulings require approval before dependent production behavior, and Unresolved Decisions must not be guessed in code.  
> **Audience:** coding agents, developers, reviewers, maintainers, security reviewers, privacy reviewers, compliance reviewers, and architecture reviewers.  
> **Relationship to root architecture:** subordinate to root Workin Ants architecture, project overview, code standards, and canonical Shared Operations Registry. Root rulings win if a conflict is confirmed.  
> **Relationship to Cluster architecture:** subordinate to CL-01 architecture for Cluster coordination and sequencing, while remaining authoritative for Identity & Access-local truth and lifecycle behavior.  
> **Update rule:** update this file whenever a binding Identity & Access ownership, lifecycle, public-contract, security, provider, privacy, retention, or concurrency decision changes. Build progress must never silently redefine this architecture.

## Evidence posture

This document is synthesized from the current Identity & Access Module Architecture Extract, Deep Module Registry, Cluster Registry v2.3, Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Registry, CL-01 architecture, CL-01 build plan, root Workin Ants context available to the project, and directly relevant cross-Module boundary evidence.

Terms used below:

- **Confirmed** — directly supported by current supplied architecture, schema, registry, glossary/compliance, or canonical shared-operation evidence.
- **Proposed Ruling** — an implementation-grade decision strongly supported by the evidence but not yet fully settled by all authoritative sources.
- **Unresolved** — the evidence identifies a real decision that must be settled before dependent production behavior is enabled.

---

## 1. Module Header

| Field | Value |
|---|---|
| Module ID | `identity_access` |
| Module name | Identity & Access Module |
| Module type | `capability_security` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-01 — Identity, Authority, Consent & Entitlements` |
| Core question answered | “Which Workin Ants account actor is authenticated, what authentication/security proof exists, and is fresh action-scoped assurance available when required?” |
| Source-of-truth posture | Owns base `User` account identity and Identity-specific security proof; does not own downstream permission, profile, entitlement, payment, or compliance lifecycles |
| Provider posture | External authentication, OTP, WebAuthn, and recovery-verification systems are evidence/transport rails behind Identity-owned adapters; provider state does not replace Workin Ants truth |
| Public boundary | Stable Identity commands/queries and canonical SH-001 / SH-014 contracts; consumers must not read Identity tables directly by default |
| Privacy posture | Identity executes Privacy-authorized operations only against Identity-owned records; Privacy / Data Erasure owns request/job/target orchestration |
| Security posture | Server-authoritative, fail-closed for unresolved high-risk behavior, no raw passwords/OTP/biometrics/provider secrets in domain records |

---

## 2. Purpose, Goal, and Transformation

### Purpose

Identity & Access establishes and preserves the Workin Ants base account identity and the security proof required to recognize a trusted actor. It owns the account-security lifecycles that precede protected platform actions: pre-account age gating, account provisioning, authentication-provider linkage, security posture, passkeys/WebAuthn metadata, step-up challenges, short-lived sensitive-action assurance, account recovery, phone replacement security, structural platform-role rows, and Identity-specific security history.

### Goal

Every protected Workin Ants workflow should be able to begin from one server-trusted actor and, when a sensitive action requires stronger assurance, obtain recent, action/target-scoped proof without reimplementing authentication or MFA inside the consuming Module.

The Module must make these distinctions explicit:

```text
External provider proves/session-authenticates a subject
→ Identity & Access maps that subject to one Workin Ants User
→ Identity & Access returns authenticated actor + safe assurance context
→ Role / Authority decides whether the actor may attempt a resource action
→ if the action is classified sensitive, Identity & Access performs step-up
→ consuming Module performs its own business/compliance gates and mutation
```

### What enters

Typical inputs include:

- anonymous age-band/birth-year and region declarations;
- privacy-minimized IP/device identifiers;
- verified Supabase Auth or equivalent provider session evidence;
- Google/Apple/OAuth provider subject/account references;
- passkey/WebAuthn registration and authentication results;
- OTP verification results;
- requested sensitive-action type and optional target;
- account-recovery initiation information;
- recovery email-token proof;
- normalized recovery identity-verification results;
- request, device, user-agent, correlation, and security-risk context;
- Role / Authority decisions for Identity-owned protected mutations;
- Consent proof when a security workflow requires a versioned disclosure;
- ComplianceHold decisions when an approved security/admin workflow composes a reusable hold;
- Privacy-owned erase/anonymize/export/retain instructions.

### What leaves

The Module may produce:

- a pre-account allowed/blocked/manual-review decision;
- one provisioned Workin Ants `User`;
- structural `UserRole` rows;
- an authenticated actor context;
- linked/revoked/compromised authentication-method state;
- current security-posture facts;
- passkey credential metadata;
- a step-up-required / blocked / recovery-required decision;
- a verified `StepUpChallenge`;
- an active short-lived `SensitiveActionSession`;
- an account-recovery state/result;
- an approved phone-security replacement result;
- Identity-specific `UserSecurityEvent` evidence;
- minimized domain events/outbox messages;
- notification, audit, sensitive-access, hold, privacy, or operational requests through canonical interfaces.

### Business/capability transformation

```text
anonymous or externally authenticated person
→ eligibility and provider proof
→ Workin Ants base account identity
→ linked authentication/security posture
→ authenticated actor context
→ optional fresh step-up assurance
→ recoverable, auditable, privacy-aware account security
```

### Why this is its own Module boundary

Identity & Access deserves a separate boundary because authentication proof has different invariants, providers, attack surfaces, retention needs, and lifecycle semantics from authorization, buyer/seller/candidate profiles, consent, subscriptions, business eligibility, payment, file access, and privacy orchestration. Moving those responsibilities together would create one oversized “auth/access” service with multiple source-of-truth owners and make security proof indistinguishable from business permission.

---

## 3. Owned Truth

### 3.1 Schemas/models owned

The current evidence assigns these models or controlled vocabularies to Identity & Access:

- `User`
- `UserRole`
- `PlatformRole`
- `AgeGateAttempt`
- `AgeGateResult`
- `AgeGateBlock`
- `AuthProviderType`
- `AuthCredentialStatus`
- `UserSecurityTier`
- `StepUpActionType`
- `StepUpChallengeType`
- `StepUpChallengeStatus`
- `StepUpFailureReason`
- `AccountRecoveryStatus`
- `AccountRecoveryReason`
- `AccountRecoveryIdentityProvider`
- `SecurityEventType`
- `UserSecurityProfile`
- `AuthProviderAccount`
- `PasskeyCredential`
- `StepUpChallenge`
- `SensitiveActionSession`
- `AccountRecoveryRequest`
- `UserSecurityEvent`

### 3.2 Significant source-of-truth records

| Record | Plain-English meaning | Authority |
|---|---|---|
| `User` | Base Workin Ants account identity. It answers “which local account is this?” and must not become buyer/seller/candidate/organization/subscription truth. | Confirmed |
| `UserRole` | Structural attachment of a `PlatformRole` to a User. Identity owns the row; Role / Authority interprets what it permits. | Confirmed |
| `AgeGateAttempt` | Evidence that a pre-account age/region decision was evaluated at a point in time. | Confirmed |
| `AgeGateBlock` | Time-bounded pre-account IP/device cooldown evidence after a blocked age/region decision. It is not a post-account ComplianceHold. | Confirmed |
| `UserSecurityProfile` | Current account-security posture summary: tier, phone verification metadata, configured-method summaries, recent assurance timestamps, and local security-lock state. | Confirmed, with projection cautions below |
| `AuthProviderAccount` | Workin Ants record that an external authentication identity/method is linked and its normalized local credential status. | Confirmed |
| `PasskeyCredential` | Metadata/reference record for one passkey/WebAuthn credential. It never contains raw biometric material. | Confirmed |
| `StepUpChallenge` | Short-lived additional-authentication challenge for one sensitive action and optional target. | Confirmed |
| `SensitiveActionSession` | Temporary server-side grant proving recent step-up authentication for one actor/action/optional target. | Confirmed |
| `AccountRecoveryRequest` | Identity-owned recovery workflow for changed phone, lost access, suspicious lockout, unavailable passkey, admin initiation, or other approved recovery reason. | Confirmed |
| `UserSecurityEvent` | Identity-specific security history for auth methods, passkeys, step-up, recovery, phone changes, fallback, and security-profile changes. It is not generic AuditEvent, AccessAuditLog, or an outbox. | Confirmed |

### 3.3 Enums/statuses owned

Confirmed controlled vocabularies currently include:

- `PlatformRole`: `user`, `admin`, `support`
- `AuthProviderType`: `email_password`, `google`, `apple`, `passkey`, `magic_link`, `sso`, `other`
- `AuthCredentialStatus`: `active`, `disabled`, `revoked`, `expired`, `compromised`
- `UserSecurityTier`: `standard`, `elevated`, `high_risk`
- `StepUpActionType`: current financial/security/admin action vocabulary plus `other`
- `StepUpChallengeType`: `sms_otp`, `passkey`, `password`, `password_and_sms`, `email_link`, `identity_provider`, `admin_manual`, `other`
- `StepUpChallengeStatus`: `pending`, `verified`, `failed`, `expired`, `cancelled`, `locked`
- `StepUpFailureReason`: invalid/expired code, max attempts, passkey/hardware/provider failure, user cancellation, risk-policy block, other
- `AccountRecoveryStatus`: `initiated`, `email_sent`, `email_verified`, `identity_verification_pending`, `identity_verified`, `phone_update_pending`, `completed`, `failed`, `expired`, `cancelled`, `manual_review`
- `AccountRecoveryReason`: changed phone, lost phone access, suspicious login lockout, passkey unavailable, admin initiated, other
- `AccountRecoveryIdentityProvider`: `stripe_identity`, `persona`, `manual`, `other`
- `SecurityEventType`: Identity-specific auth/security event vocabulary
- `AgeGateResult`: `allowed`, `blocked_underage`, `blocked_region`, `manual_review`

### 3.4 Lifecycles owned

Identity & Access owns the transition policy for:

1. age-gate evaluation and cooldown;
2. authentication-provider credential state;
3. passkey credential state;
4. local security lock/posture state;
5. step-up challenge state;
6. sensitive-action session validity/revocation;
7. account-recovery state;
8. structural platform-role attachment/removal;
9. Identity-specific security history append.

### 3.5 Domain events/ledgers owned

`UserSecurityEvent` is an Identity-owned append-oriented security history. It is not automatically an integration event bus.

**Proposed Ruling PR-IA-07:** external integration facts such as `identity.user.provisioned`, `identity.recovery.completed`, or `identity.security.credential_compromised` must be published through the canonical outbox using separate versioned event contracts. Consumers must not poll `UserSecurityEvent` as an undocumented bus.

### 3.6 Projections/summaries owned

`UserSecurityProfile.passkeysEnabled`, `smsMfaEnabled`, `lastStepUpAt`, and similar summary fields may support efficient posture reads, but they must not independently become proof that a credential exists or that a sensitive action is currently authorized.

**Proposed Ruling PR-IA-02:** active credential/provider records are authoritative for configured authentication methods; security-profile booleans are maintained summaries.

**Proposed Ruling PR-IA-03:** an action/target-scoped, unexpired, non-revoked `SensitiveActionSession` (or an explicitly approved equivalent passkey-authenticated session proof) is the Workin Ants authorization-assurance proof for a sensitive action. `lastStepUpAt` alone is never sufficient.

### 3.7 Policies/invariants owned

Identity-specific policy owns:

- whether pre-account age eligibility passes;
- age-gate cooldown behavior;
- local mapping of normalized provider identities to Workin Ants User records;
- which linked auth method state is active/revoked/compromised;
- security-tier/local-lock interpretation;
- passkey failure/fallback policy;
- step-up challenge type, TTL, max attempts, fallback, and target binding;
- sensitive-action-session duration/revocation rules;
- recovery transition policy;
- recovery proof chain required before phone replacement;
- security-event vocabulary and safe metadata;
- provider-to-Identity status translation.

---

## 4. Explicit Non-Ownership

Coding agents must not move the following responsibilities into Identity & Access.

| Adjacent owner | Remains owned there | Identity & Access may do | Identity & Access must not do |
|---|---|---|---|
| Role / Authority | Permission interpretation for resource/action/admin/owner/organization/participant scope | Supply authenticated actor and structural platform-role facts; consume `authorizeResourceAction` for Identity-owned mutations | Build generic permission engine, local `isAdmin`/`isOwner`, organization/thread authorization |
| Customer / Buyer Profile | `CustomerProfile` buyer actor identity | Publish/hand off User-provisioned fact | Store buyer lifecycle, commerce history, buyer premium flags |
| Professional Profile / Eligibility | Seller identity/readiness | Supply base User actor | Decide selling readiness or verification |
| Candidate Application/Profile | Applicant identity/application lifecycle | Supply base User actor | Store candidate/applicant state |
| Organization Hiring | Organization membership lifecycle | Supply User actor; consume authority decisions | Own or mutate `OrganizationMember`/`OrganizationRole` |
| Consent & Disclosure | Exact type/version acceptance proof and consent version catalog | Query required proof | Store `hasAcceptedX` security booleans as consent truth |
| Track Subscription & Entitlement | Plan/subscription/grant/usage/commercial policy | Supply User actor | Gate core account security by paid plan, create premium flags, own entitlement |
| Payment / Payout / Tax | Payment, payout, KYC, tax, processor-ledger truth | Provide step-up assurance to sensitive financial actions | Reuse payout KYC as account-recovery truth; mutate payout/tax state |
| Trust Verification / Screening | Marketplace/background/license verification | None except actor context | Reuse VerificationCheck as recovery proof or account credential |
| Admin Review / Compliance Hold | Generic reusable hold lifecycle | Evaluate/request holds only where approved | Turn `lockedUntil` into generic ComplianceHold or create competing block ledger |
| Notification | Notification persistence, recipient/channel delivery, retries, provider delivery state | Request security/recovery notice with safe intent | Build generic email/SMS/push delivery service |
| Audit / Event Ledger | Generic `AuditEvent` and `AccessAuditLog` | Append requests through canonical interfaces | Replace `UserSecurityEvent` with Audit or vice versa |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob/DataErasureTarget orchestration and retention-exemption record | Enumerate and execute approved Identity targets | Create a local privacy request/job system |
| Media / File Access | Upload, validation, scanning, storage, generic access grants, signed URLs | Reference approved avatar/media facts only if ownership is later confirmed | Build file upload/storage/presign helpers |
| Search / Public Visibility | Typesense/search projection execution | Supply source facts only if a future approved User projection exists | Index User/public profile directly |
| Observability / Ops | IntegrationFailure/SystemEvent/queue telemetry/health infrastructure | Emit safe logs/metrics/failures | Use ops records as Identity lifecycle truth |
| Other access-grant owners | MediaAccessGrant, CourseVideoPlaybackGrant, DigitalDownloadGrant, AgreementAccessGrant | Reuse shared temporary-grant mechanics | Merge those grants into SensitiveActionSession |

Other explicit prohibitions:

- no raw password storage;
- no raw biometric storage;
- no plaintext OTP in Postgres;
- no provider secret/session-token storage in Identity domain records;
- no local `Wallet`, payout ledger, KYC, tax, or transaction truth;
- no business-object ownership policy;
- no generic compliance engine;
- no “universal user profile” service.

---

## 5. Module Architecture Principles

1. **User is base account identity only.** Do not add buyer, seller, candidate, organization, subscription, payment, healthcare, or business-lifecycle fields to `User`.
2. **Authentication is not authorization.** Identity proves the actor; Role / Authority decides what the actor may attempt.
3. **Security assurance is scoped.** Fresh assurance must bind to actor, action, optional target, expiry, revocation, and required assurance type.
4. **Provider state is evidence, not Workin Ants truth.** Normalize provider responses before domain policy.
5. **No raw secrets.** Passwords, OTP plaintext, biometric material, provider secrets, bearer tokens, and session secrets stay outside Identity domain persistence and logs.
6. **Summaries never outrank source records.** Security-profile booleans/timestamps must not replace credential/challenge/grant truth.
7. **Recovery is distinct from KYC and marketplace verification.** Account recovery proof exists only to restore account security/access.
8. **Security lock and ComplianceHold are separate truths.** A local security lock protects authentication/security access; a ComplianceHold is a reusable platform stop sign.
9. **UserSecurityEvent, AuditEvent, AccessAuditLog, domain integration events, and telemetry are distinct.**
10. **Cross-Module access uses public interfaces.** Consumers should not query Identity Prisma repositories directly.
11. **Every transition is owner-controlled and transaction-safe.**
12. **Unresolved high-risk behavior fails closed.** No coding agent may fill gaps with permissive defaults.
13. **Shared primitives are reused.** Cryptography, idempotency, queue, outbox, locking, audit, telemetry, provider webhook verification, and privacy orchestration must not be rebuilt locally.
14. **Rate limits are infrastructure; thresholds are Identity policy.** Do not hide business/security threshold decisions in generic middleware.
15. **External events are replay-safe.** Provider callbacks are verified, deduplicated, translated, and then applied through Identity transition services.
16. **Structural roles remain separate from permission policy.** `UserRole` is Identity-owned; Role / Authority owns interpretation.
17. **No hard delete by convenience.** Privacy and retention decisions control destructive handling of personal/security records.
18. **Payload minimization is default.** Consumers receive only actor/security facts they need, never full provider/profile payloads.

---

## 6. Proposed Folder / Code Structure

The root repository's final folder convention controls. Where the root has not yet established an equivalent Workin Ants Module path, the following is **Proposed Ruling PR-IA-01** and follows the Workin Ants Deep Module precedent rather than importing BTLS-specific structure:

```text
src/
  modules/
    identity-access/
      domain/
        policies/
          age-gate-policy.ts
          login-readiness-policy.ts
          credential-policy.ts
          step-up-policy.ts
          recovery-policy.ts
          security-lock-policy.ts
        types/
          actor-context.ts
          security-decisions.ts
      application/
        commands/
          provision-user-after-age-gate.ts
          link-auth-provider-account.ts
          revoke-auth-provider-account.ts
          register-passkey.ts
          revoke-passkey.ts
          verify-step-up-challenge.ts
          initiate-account-recovery.ts
          verify-recovery-email.ts
          apply-recovery-verification.ts
          complete-account-recovery.ts
          assign-platform-role.ts
          remove-platform-role.ts
        queries/
          resolve-authenticated-actor.ts
          evaluate-login-readiness.ts
          get-user-security-posture.ts
          list-authentication-methods.ts
          list-platform-roles.ts
          get-account-recovery-status.ts
        services/
          age-gate-service.ts
          provider-link-service.ts
          step-up-service.ts
          recovery-service.ts
          security-event-service.ts
      contracts/
        public.ts
        events.ts
        privacy.ts
        providers.ts
      infrastructure/
        repositories/
          user-repository.ts
          age-gate-repository.ts
          security-repository.ts
          recovery-repository.ts
        providers/
          auth/
            supabase-auth-adapter.ts
          passkey/
            webauthn-adapter.ts
          otp/
            otp-provider-adapter.ts
          recovery-verification/
            recovery-verification-adapter.ts
      workers/
        expire-step-up-challenges.ts
        expire-recovery-requests.ts
        reconcile-identity-provider-state.ts
      privacy/
        enumerate-identity-subject-data.ts
        execute-identity-privacy-target.ts
      tests/
        domain/
        application/
        contracts/
        providers/

src/
  app/
    ... thin auth/account/security/recovery routes or server-action adapters ...

src/
  platform/
    ... canonical SH-### implementations owned outside this Module ...

tests/
  integration/
    identity-access/
      provisioning.*
      role-contract.*
      passkey-step-up.*
      recovery.*
      provider-callback.*
      privacy.*
      downstream-consumers.*
```

Folder rules:

- Domain policy and application orchestration live with Identity & Access.
- Delivery/UI is thin and never owns security policy.
- Provider-specific SDK types remain inside adapter folders.
- Shared crypto/idempotency/queue/outbox/audit/logging code stays under its canonical owner, not `identity-access/utils`.
- No generic `authService.ts` should become an uncontrolled catch-all.
- `UserSecurityEvent` append logic may have one Identity-owned service; do not create parallel `securityLog`, `authAudit`, and `loginEvent` writers.
- If root code standards choose a different physical path, preserve these logical boundaries rather than copying this tree literally.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / UI | Age gate, sign-in/account shell, security-method management, step-up prompt, recovery status/handoff presentation; validation adapters | Provider/session truth, permission policy, lifecycle transitions, raw secrets |
| Application services | Command/query orchestration, transactions, shared-operation invocation, provider-port calls, event/audit/notification requests | Generic queue/idempotency/audit/notification infrastructure |
| Domain policy | Age eligibility, credential viability, security posture, step-up scope/TTL/attempt/fallback, recovery transition rules, local security lock rules | Organization/resource authorization, business eligibility, commercial entitlement |
| Repositories / data access | Identity-owned Prisma records only | Foreign Module repositories by default; cross-domain joins used as hidden policy |
| Workers | Identity-owned expiration/reconciliation workflows | Generic scheduler/queue implementation, Notification delivery workers, Privacy orchestration |
| Provider adapters | Supabase/Auth, OAuth normalization, WebAuthn/passkey, OTP verification, recovery identity verification | Domain lifecycle authority, raw provider payload propagation |
| Public contracts | Actor DTO, security decisions, Identity commands/queries, versioned domain events, privacy executor, provider ports | Prisma model exposure as writable cross-Module API |
| Privacy executor | Enumerate/export/anonymize/revoke/retain Identity-owned data according to Privacy instruction | Privacy request/job/retention-exemption orchestration |
| Security history | Append `UserSecurityEvent` according to Identity semantics | Generic audit ledger or sensitive data access ledger |

---

## 8. Data Model

### 8.1 `User`

**Purpose:** base Workin Ants account identity.

**Key relationships:** one-to-many roles/provider/passkey/security events; one-to-one security profile; references from most business Modules.

**Authoritative fields:** `id`, account-level email/handle where used, creation/update timestamps, privacy outcome markers already present in schema. The current schema also contains `displayName`, `avatarUrl`, `bio`, `city`, `state`, `country`, and `isPublic`; their final ownership is unresolved.

**Lifecycle/status:** no confirmed general User status enum exists. Do not invent `active/suspended/deleted` account status as a shortcut.

**Uniqueness:** `email` and `handle` are currently unique when present. Provider identity mapping uniqueness is not fully enforced by current `AuthProviderAccount`.

**Concurrency:** provisioning is idempotent and provider-identity mapping must be serialized/uniquely constrained.

**Retention/privacy:** highly referenced across platform. Direct hard deletion is unsafe until Privacy/retention and downstream-reference behavior is approved. Existing privacy marker fields do not transfer privacy workflow ownership.

### 8.2 `UserRole`

**Purpose:** structural platform-role attachment.

**Relationships:** belongs to User; uses `PlatformRole`.

**Authority:** Identity writes the row only after appropriate Role / Authority permission. Role / Authority interprets it.

**Uniqueness:** composite identity `(userId, role)` prevents duplicate identical role attachment.

**Concurrency:** add/remove must be transactional and idempotent.

**Retention/audit:** admin/support changes require generic audit; role history retention/event behavior should be captured by domain/outbox/audit, not by inventing a second role table.

### 8.3 `AgeGateAttempt`

**Purpose:** point-in-time evidence of pre-account age/region evaluation.

**Authoritative fields:** result, region, privacy-minimized identifiers, age band/birth year where permitted, block expiry if applicable, timestamp.

**Lifecycle:** immutable decision record; result does not later transition.

**Privacy:** avoid full DOB unless separately legally approved. Hash identifiers through canonical primitive.

**Gap:** current record does not clearly persist policy/rule version, applied minimum age, jurisdiction rule version, or structured reason.

### 8.4 `AgeGateBlock`

**Purpose:** time-bound pre-account retry cooldown keyed by privacy-minimized IP/device identifiers.

**Authoritative fields:** matching hash(es), reason, `blockedUntil`.

**Lifecycle:** effective while `blockedUntil > now`; expiry may be query-time or worker-cleaned.

**Concurrency:** duplicate/overlapping blocks should not produce inconsistent eligibility.

**Schema gap:** both `ipHash` and `deviceHash` are currently optional.

**Proposed Ruling PR-IA-04:** a persisted block must contain at least one matchable approved identifier. Enforce via application invariant and, where supported by root migration standards, a database check constraint.

### 8.5 `UserSecurityProfile`

**Purpose:** current account-security posture and efficient security summary.

**Authoritative fields:** security tier, encrypted/hashed phone metadata, verification/change timestamps, local lock fields.

**Summary fields:** `passkeysEnabled`, `smsMfaEnabled`, `backupPasswordConfigured`, `lastStepUpAt`, `lastSensitiveActionAt`.

**Lifecycle:** security tier and local lock state can change; exact tier transition policy is unresolved.

**Concurrency:** security mutations must lock or optimistic-check the user/security aggregate.

**Privacy/security:** phone plaintext must not be stored; reversible phone data uses canonical encryption, searchable comparison uses canonical normalized hash.

### 8.6 `AuthProviderAccount`

**Purpose:** normalized Workin Ants linkage to external authentication identity/method.

**Authoritative fields:** User, provider type, provider subject/account reference, verified email metadata, normalized local credential status, linkage/revocation/last-used timestamps.

**Lifecycle:** uses `AuthCredentialStatus`.

**Current constraint gaps:** provider subject/account fields are nullable and provider identity uniqueness is not fully expressed.

**Proposed Ruling PR-IA-05:** every active provider linkage must have one stable provider identity key accepted by that adapter, and the canonical provider identity must be unique to one Workin Ants User. Exact merge/canonical-email behavior remains unresolved and must not be inferred from uniqueness alone.

### 8.7 `PasskeyCredential`

**Purpose:** metadata/reference for one WebAuthn/passkey credential.

**Authoritative fields:** credential hash, provider credential reference, public-key provider reference, device metadata, normalized status, registration/use/failure/revocation timestamps.

**Uniqueness:** `credentialIdHash` is unique.

**Lifecycle:** `AuthCredentialStatus`.

**Security:** no raw biometric material. Credential IDs should be hashed/reference-safe according to provider requirements. Public-key material is provider/reference-managed per current model intent.

**Concurrency:** duplicate registration completion must return existing matching credential or explicit conflict; never duplicate.

### 8.8 `StepUpChallenge`

**Purpose:** ephemeral challenge for additional proof.

**Authoritative fields:** user/security profile, action/challenge type, target, status, provider refs, attempts/max attempts, failure reason, expiry, verified/failed timestamps.

**Lifecycle:** `StepUpChallengeStatus`.

**Security:** `codeHash` exists in schema, but whether OTP challenge secrets may be stored hashed in Postgres or must remain provider/cache-owned is unresolved. Plaintext OTP is prohibited.

**Concurrency:** multiple simultaneous challenges for same subject/action/target require an explicit policy before broad production use.

### 8.9 `SensitiveActionSession`

**Purpose:** temporary action/target-scoped assurance grant after successful step-up.

**Authoritative validity:** correct user, action and target; `expiresAt` in future; `revokedAt` null; challenge/assurance meets policy.

**Lifecycle:** no enum; conceptual states are active → expired or revoked. Expiry may be derived from time.

**Concurrency:** issuance must be tied transactionally/idempotently to verified challenge; no duplicate grant side effects.

**Boundary:** distinct from all business/media/delivery access grants.

### 8.10 `AccountRecoveryRequest`

**Purpose:** changed-phone/lost-access recovery workflow.

**Authoritative fields:** user/security profile, reason/status, hashed email token proof, identity-verification provider/ref/status, old/new phone hashes/encrypted values, verification/phone/completion/cancellation/expiry timestamps, failure reason.

**Lifecycle:** `AccountRecoveryStatus`.

**Concurrency:** parallel active requests and duplicate provider callbacks are high-risk and require explicit locking/dedupe.

**Privacy:** token hashes, phone hashes/encrypted values, provider references, IP/user-agent, and verification metadata require retention classification.

**Provider dedupe gap:** no confirmed Identity-owned processed-provider-event record exists.

**Proposed Ruling PR-IA-06:** if the selected recovery provider delivers callbacks/events, Identity requires provider-event receipt/dedupe truth with a unique provider/event identity, implemented using SH-060. The exact schema name/shape requires approval before migration.

### 8.11 `UserSecurityEvent`

**Purpose:** Identity-specific security history.

**Authoritative fields:** user/security-profile link, `SecurityEventType`, safe target reference, privacy-minimized request/IP/user-agent metadata, request ID, sanitized metadata, timestamp.

**Lifecycle:** append-only event history; never “updated into” a different event.

**Boundary:** not generic audit, AccessAuditLog, queue record, integration failure, or outbox.

**Proposed Ruling PR-IA-08:** material Identity security transitions append a security event in the same transaction as the authoritative state change where practical; corrections use a new event rather than destructive rewrite.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Age gate

```text
request
→ check active cooldown
→ evaluate policy
→ allowed | blocked_underage | blocked_region | manual_review
→ record AgeGateAttempt
→ blocked path may create time-bounded AgeGateBlock
```

`AgeGateAttempt.result` is terminal for that attempt. A later retry is a new attempt, not a mutation of history.

Prohibited shortcut: creating `User` first and “checking age later” when the age gate is active.

### 9.2 Authentication credential state

```text
active
├─→ disabled
├─→ revoked
├─→ expired
└─→ compromised
```

Current schema does not define reactivation semantics. Do not silently change `revoked/compromised` back to `active`; use an approved relink/recovery policy.

Transition owner: Identity & Access.

Triggers: provider link/revoke, provider synchronization, credential expiry, security incident.

History: `UserSecurityEvent` plus generic audit for material admin/security action as required.

### 9.3 Security tier / local lock

`UserSecurityTier` = `standard | elevated | high_risk`.

The exact transition matrix is **Unresolved U-IA-11**. The current `lockedUntil` / `lockReason` fields represent local security lock state and are not ComplianceHold.

Prohibited shortcut: treating `high_risk` or `lockedUntil` as a generic business/compliance suspension.

### 9.4 Passkey credential lifecycle

Uses `AuthCredentialStatus`.

Typical supported flow:

```text
registration challenge outside/domain-temporary state
→ verified provider/WebAuthn response
→ active PasskeyCredential
→ used / failure counters updated
→ revoked | disabled | compromised | expired
```

Repeated passkey failure must trigger approved fallback rather than automatic permanent account lockout.

### 9.5 Step-up challenge lifecycle

Confirmed statuses:

```text
pending
├─→ verified
├─→ failed
├─→ expired
├─→ cancelled
└─→ locked
```

Rules:

- only `pending` may accept new verification proof;
- `verified` is terminal for that challenge;
- failed/expired/cancelled/locked challenges never create new assurance unless policy explicitly creates a new challenge;
- max attempts and TTL are enforced server-side;
- SMS OTP TTL is currently specified as five minutes in Module evidence;
- provider failure does not equal verification success;
- replay of successful verification returns the same semantic result or “already verified”; it does not issue uncontrolled duplicate grants.

### 9.6 Sensitive-action-session lifecycle

Conceptual state:

```text
granted/active
├─→ expired (time-derived)
└─→ revoked
```

Validation checks subject, action, target, assurance, expiry, and revocation every time.

No reversal of revocation. A new step-up creates a new grant.

### 9.7 Recovery lifecycle

Confirmed principal sequence:

```text
initiated
→ email_sent
→ email_verified
→ identity_verification_pending
→ identity_verified
→ phone_update_pending
→ completed
```

Branches:

```text
any approved nonterminal point
├─→ failed
├─→ expired
├─→ cancelled
└─→ manual_review
```

The exact allowed origin/destination matrix for every branch requires implementation policy tests and must not allow skipping required evidence.

Rules:

- recovery email token currently expires in fifteen minutes;
- changed-phone replacement requires approved identity-verification evidence;
- provider success is evidence only; Identity transition service performs the state change;
- `completed`, `failed`, `expired`, and `cancelled` are terminal for that request unless architecture explicitly defines reopen;
- manual review does not itself prove recovery success;
- concurrent recovery requests must follow an approved one-active/supersede/reject rule; currently unresolved.

### 9.8 Platform-role structure

`UserRole` is attached/removed; there is no status lifecycle.

```text
absent → attached → removed
```

Identity owns the row mutation. Role / Authority must approve the action.

### 9.9 UserSecurityEvent

Append-only:

```text
security fact occurs
→ append one immutable event
→ never mutate history to represent a new fact
```

---

## 10. Commands

The command names below define the intended Module boundary. Final function signatures follow root code standards and should use validated DTOs rather than Prisma models.

| Command | Purpose | Actor/context | Preconditions | Writes | Shared operations / effects | Idempotency / failures |
|---|---|---|---|---|---|---|
| `evaluateAgeEligibility` + `recordAgeGateAttempt` | Decide and record pre-account eligibility | Anonymous request context | Valid minimized input; cooldown check | AgeGateAttempt; optional AgeGateBlock | SH-076, SH-032/033/034; rate-limit mechanism | Repeated request is new attempt; block creation deduped as policy requires |
| `provisionUserAfterAgeGate` | Create/link local User after eligibility/provider proof | Provider-authenticated subject | Age allowed; provider identity valid; no conflicting mapping | User, baseline UserSecurityProfile, AuthProviderAccount, default UserRole if approved, security event | SH-044, SH-046, SH-076, SH-032–034 | Replay returns same User; identity conflict fails closed/manual review |
| `linkAuthProviderAccount` | Link an additional auth method | Authenticated User | SH-002 authority; proof of provider account; viable security policy | AuthProviderAccount, security event | SH-002, SH-044, SH-064, SH-029/041 where required | Duplicate matching link returns existing; conflicting owner denied |
| `revokeAuthProviderAccount` | Revoke auth method safely | User/admin context | SH-002; must preserve viable login/recovery path per policy | credential status/revokedAt, security event | SH-002, SH-014 if required, SH-029, SH-041 | Repeated revoke safe; cannot remove last viable method if policy forbids |
| `markAuthCredentialCompromised` | Mark method/passkey compromised and trigger security response | Trusted security/admin/system context | Strong authorization/evidence | credential state, lock/recovery/session-revocation effects, security event | SH-002, SH-029, SH-041, provider session revoke port | Idempotent by credential+incident semantic key |
| `beginPasskeyRegistration` | Create WebAuthn registration challenge/options | Authenticated User | SH-002; account/security readiness | Temporary/provider challenge only | provider port, rate limit, SH-032–034 | Retry semantics provider-specific |
| `completePasskeyRegistration` | Verify response and persist credential metadata | Authenticated User | Matching valid challenge/result | PasskeyCredential, security summary, event | SH-044, SH-072/076 where applicable, SH-029/041 | Duplicate completion returns same credential |
| `revokePasskeyCredential` | Revoke one passkey | User/admin | SH-002; possibly SH-014; recovery/login viability | PasskeyCredential status, event | SH-002, SH-014 conditional, SH-029/041 | Repeated revoke safe |
| `createStepUpChallenge` | Begin extra authentication for action/target | Authenticated actor | Actor authorized to attempt action; action type supported; rate policy | StepUpChallenge | SH-014, SH-044, SH-051/053, provider port | Duplicate active challenge follows unresolved concurrency rule; fail closed until settled |
| `verifyStepUpChallenge` | Apply normalized proof and grant assurance | Same actor/challenge context | Pending, unexpired, attempts remain, proof valid | StepUpChallenge + SensitiveActionSession + security event | SH-014, SH-044, SH-051/053, SH-088, SH-029/041 as required | Replay returns existing grant; invalid/expired/locked fails |
| `cancelStepUpChallenge` | Cancel pending challenge | Actor/admin/system as allowed | Pending | status/cancel timestamp/event | SH-053 | Idempotent |
| `revokeSensitiveActionSession` | Revoke active assurance | Actor/security/admin/system | Correct grant scope | revokedAt/reason + event | SH-089 | Idempotent |
| `initiateAccountRecovery` | Start recovery | Anonymous or authenticated depending reason | Abuse checks; account resolution without enumeration leakage | AccountRecoveryRequest, event | SH-044, SH-049, SH-074/072/076, SH-041 | Duplicate request follows approved concurrency policy |
| `verifyRecoveryEmailToken` | Prove possession of recovery email link/token | Recovery subject | Correct unexpired hashed token | recovery status/timestamps/event | SH-044, SH-053, SH-072/074 | Token replay returns already-verified or denied, never repeats effects |
| `applyRecoveryIdentityVerification` | Apply normalized provider result | Verified provider callback/poll or trusted manual adapter | SH-059/060 if callback; matching request/provider ref | recovery status/evidence/event | SH-059/060/061/062, SH-051/053, SH-037 | Duplicate callback no-op/same result |
| `completeAccountRecovery` | Apply approved phone/access change and complete request | Recovery workflow / authorized actor | Full proof chain, no conflicting request, hold/security policy satisfied | UserSecurityProfile phone/security fields, AccountRecoveryRequest, events | SH-051/053, SH-075/076, SH-011 conditional, SH-029/041, session-revoke provider port | Exactly one completion effect; conflict/stale transition denied |
| `cancelAccountRecovery` | Cancel nonterminal recovery | Authorized subject/admin/system | Nonterminal state | recovery status/event | SH-053 | Idempotent |
| `assignPlatformRole` | Attach structural platform role | Authorized admin/system | SH-002 and step-up if policy requires | UserRole + event/audit | SH-002, SH-014 conditional, SH-029, SH-044 | Composite uniqueness makes replay safe |
| `removePlatformRole` | Remove structural platform role | Authorized admin/system | SH-002; safety checks | UserRole deletion + event/audit | SH-002, SH-014 conditional, SH-029, SH-044 | Repeated remove safe |
| `lockUserSecurityProfile` | Apply Identity local security lock | Trusted security/admin/system | Approved risk evidence | lock fields + event | SH-002 when actor-driven, SH-029/041 | Idempotent/monotonic according to policy |
| `unlockUserSecurityProfile` | Release local security lock | Recovery/expiry/authorized review | Valid release evidence | lock fields + event | SH-002, SH-029 | Stale unlock denied |
| `executeIdentityPrivacyInstruction` | Apply Privacy-selected disposition to Identity records | Trusted Privacy orchestration | Valid Privacy target + retention disposition | Identity-owned records only | SH-095/097/098/070/044 | Idempotent; retained target returns retained result |

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result kind | Result | Consumer must not infer |
|---|---|---|---|---|---|
| `resolveAuthenticatedActor` (SH-001) | Every protected Module | Request/session context | Source-backed actor context | User ID, structural roles/facts required by contract, session assurance/security-safe facts | Resource permission, customer/professional/candidate identity, entitlement, consent, business readiness |
| `evaluateLoginReadiness` | Auth/login shell | User/provider/session context | Readiness decision | ready / step-up / recovery / locked / denied / unavailable + stable reason | That business actions are permitted |
| `getUserSecurityPosture` | Account settings, security/admin consumers | User ID + authorized actor | Source truth + summaries | tier, lock, verified phone metadata, active auth-method summary, recent assurance summary | Current sensitive-action authorization from booleans/timestamps alone |
| `listAuthenticationMethods` | Account security | User | Source truth summary | linked providers/passkeys with safe metadata/status | Provider secret/session token |
| `listPlatformRoles` | Role / Authority, account/admin | User | Structural source truth | PlatformRole[] | What those roles permit |
| `evaluateStepUpRequirement` / SH-014 result | Sensitive action owners | actor, action, optional target, required assurance | Security decision | satisfied with grant evidence / step_up_required / denied / unavailable | Resource authorization or business compliance |
| `validateSensitiveActionAssurance` | Sensitive action owner/SH-014 implementation | actor, action, target, grant | Source-backed assurance | valid/invalid/expired/revoked/wrong-scope | Permission to the resource |
| `getAccountRecoveryStatus` | Recovery UI/admin | recovery ID + safe subject proof | Source truth | status, safe next action, timestamps/reason codes | Provider raw status or identity documents |
| `checkAgeGateCooldown` | Signup | normalized hash context | Source truth/policy | blocked/not blocked + expiry | General User compliance hold |
| `enumerateIdentitySubjectData` (SH-096) | Privacy | subject identity | Privacy inventory | Identity record categories and provider references | Retention disposition; Privacy decides orchestration |

### Stable Identity decision categories

Where SH-015 is adopted, Identity decisions should use stable categories such as:

- `allowed`
- `denied`
- `step_up_required`
- `recovery_required`
- `blocked`
- `manual_review`
- `pending`
- `unavailable`
- `conflict`

Reason codes should be stable, provider-neutral, and safe for the consumer.

---

## 12. Public Module Interface

### 12.1 Public queries

- **SH-001 — `resolveAuthenticatedActor`**
- `evaluateLoginReadiness`
- `getUserSecurityPosture`
- `listAuthenticationMethods`
- `listPlatformRoles`
- `getAccountRecoveryStatus`
- **SH-014 — `requireStepUpForSensitiveAction`** as the preferred consumer-facing assurance contract

### 12.2 Public commands

- `provisionUserAfterAgeGate`
- `linkAuthProviderAccount`
- `revokeAuthProviderAccount`
- `beginPasskeyRegistration`
- `completePasskeyRegistration`
- `revokePasskeyCredential`
- step-up verification/cancel commands behind SH-014
- `initiateAccountRecovery`
- `verifyRecoveryEmailToken`
- provider-result application through trusted adapter entry point
- `cancelAccountRecovery`
- restricted `assignPlatformRole` / `removePlatformRole`
- restricted security-lock commands

### 12.3 Emitted domain events

**Proposed event contracts**, emitted only if an actual consumer needs them:

- `identity.user.provisioned.v1`
- `identity.platform_role.changed.v1`
- `identity.auth_provider.linked.v1`
- `identity.auth_provider.revoked.v1`
- `identity.auth_credential.compromised.v1`
- `identity.passkey.registered.v1`
- `identity.passkey.revoked.v1`
- `identity.step_up.verified.v1`
- `identity.sensitive_action_session.revoked.v1`
- `identity.recovery.manual_review_required.v1`
- `identity.recovery.completed.v1`
- `identity.phone.changed.v1`
- `identity.security_profile.locked.v1`
- `identity.security_profile.unlocked.v1`

These events are integration facts, not a replacement for `UserSecurityEvent`.

### 12.4 Privacy interface

Identity implements:

- SH-096 `enumerateSubjectData`
- an Identity-specific executor under SH-095 `executePrivacyInstruction`
- SH-097 retention-fact contribution
- SH-098 approved anonymization mappings

Privacy owns orchestration.

### 12.5 Provider-facing interfaces

Provider-neutral ports owned here:

- `AuthenticationSessionPort`
- `OAuthIdentityPort` or provider adapters behind the auth port
- `PasskeyPort`
- `OtpVerificationPort`
- `RecoveryIdentityVerificationPort`
- `SessionRevocationPort`

Provider SDK payloads must not appear in public Module contracts.

---

## 13. Inbound Dependencies

| Owning Module / capability | Interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Role / Authority | SH-002 `authorizeResourceAction` | Protect account/security/admin mutations | actor, action, target/owner facts | Yes | permissions engine, `isAdmin`, owner/admin helpers |
| Consent & Disclosure | SH-008 `queryConsentProof`; optionally SH-009 | Security disclosures where required | user, exact consent type/version, proof ref | Yes where policy requires | ConsentLog query/write helpers, local consent booleans |
| Admin Review / Compliance Hold | SH-011; conditional SH-012 | Reusable stop sign/manual-review support where approved | target, active hold/reason category | Yes for configured high-risk action | generic `isBlocked` flags or hold table |
| Audit / Event Ledger | SH-029/030 | Generic admin/security audit and Identity-sensitive reads | actor/action/target/request/safe metadata | Audit failure handling depends on root policy | audit/access ledgers |
| Notification | SH-041 | Security/recovery notices | intent, recipient reference, safe template variables | Usually not domain-transition authority | email/SMS/push delivery |
| Observability / Ops | SH-032–039 | Correlation, logs, exceptions, metrics, failure/health | safe IDs/status/failure class | Operational only | local IntegrationFailure/SystemEvent/queue telemetry |
| Privacy / Data Erasure | SH-095–099 protocol | Authorized erasure/export/anonymization/retention orchestration | target/disposition/retention instruction | Yes for destructive operation | PrivacyRequest/DataErasureJob |
| Shared platform | SH-044–055 selected primitives | Idempotency, events, jobs, locking, transitions, expiry | semantic command/aggregate/job keys | Yes where primitive unavailable | local idempotency/queue/lock/event bus |
| Shared crypto | SH-072/074/075/076 | Hash/token/encryption | purpose/version + sensitive input | Yes | local crypto implementation |
| Shared integration security | SH-059–062 | Provider callback verification/dedupe/status/reconciliation | raw verified signature context, provider event ID, normalized mapping | Yes | webhook security/dedupe shell |
| Shared grant mechanism | SH-088/089 | Temporary-grant plumbing | subject/action/target/expiry/revocation | Yes for assurance | generic grant service that owns all grant records |

### Not an inbound dependency

Track Subscription & Entitlement is not a prerequisite for core authentication/account security. Identity supplies User actor facts to Track; it does not require a paid/free plan to allow basic account security.

---

## 14. Outbound Consumers and Effects

### Major consumers of Identity truth

- Role / Authority
- Consent & Disclosure
- Customer / Buyer Profile
- Track Subscription & Entitlement
- Professional Eligibility
- Organization Hiring
- Candidate Application & Resume Privacy
- Transaction / Order
- Booking / Calendar
- Media / File Access
- Messaging
- Notification
- Admin Review / Compliance Hold
- Payment / Payout / Tax for step-up assurance
- Privacy / Data Erasure

### Effects Identity may request

- publish minimized User/security integration events through SH-046;
- request security/recovery notifications through SH-041;
- request generic audit through SH-029;
- request sensitive Identity data access proof through SH-030 when applicable;
- request/evaluate ComplianceHold only through hold owner;
- enqueue Identity workers through SH-047;
- report provider failures/health through SH-037/039;
- execute provider deletion/revocation through its own adapter under SH-070 for Privacy/security instructions.

### Mutations prohibited across boundaries

Identity must not directly:

- create CustomerProfile/ProfessionalProfile/CandidateProfile;
- mutate OrganizationMember/ThreadParticipant;
- change ConsentLog;
- create/modify Track subscription/grant/usage;
- update Order/payment/payout/tax records;
- write Notification delivery records;
- write AuditEvent/AccessAuditLog directly except through canonical interface;
- mutate Privacy job/target state;
- write Typesense/SearchUpsertEvent directly.

---

## 15. Canonical Shared Operations Used

The canonical Shared Operations Registry is authoritative. Only Identity-relevant operations are listed here.

| ID / operation | Canonical owner / classification | Why Identity uses it / invocation | Local policy that remains Identity-owned | Expected result | Prohibited duplicate |
|---|---|---|---|---|---|
| SH-001 `resolveAuthenticatedActor` | Identity & Access / platform capability | Every protected request | User mapping, local lock/readiness, safe assurance facts | typed actor or unauthenticated/unavailable | `auth.ts`, `session.ts`, `getCurrentUser.ts`, `requireUser.ts` clones |
| SH-002 `authorizeResourceAction` | Role / Authority | Before protected Identity mutation/read | Identity supplies target/ownership facts only | allow/deny/review/step-up obligation | `permissions.ts`, `isAdmin.ts`, `roleGuard.ts` |
| SH-008 `queryConsentProof` | Consent & Disclosure | Before security flow that requires exact disclosure | Which security action requires which consent | exact proof or missing | `consent.ts`, `termsCheck.ts`, `hasAccepted.ts` |
| SH-011 `evaluateComplianceHold` | Admin Review / Hold | Conditional high-risk/security/admin gates | Which Identity action is hold-sensitive | hold decision | local generic blocked flags |
| SH-012 `requestComplianceHold` | Admin Review / Hold | Conditional risk/manual-review escalation | Identity reason/target context | hold reference/result | local hold writer |
| SH-014 `requireStepUpForSensitiveAction` | Identity & Access / platform security capability | After resource authorization, before sensitive mutation | challenge method/TTL/attempt/fallback/scope | assurance satisfied or challenge/deny | feature-local `mfaGuard.ts`, `requireOtp.ts`, `lastMfaAt` checks |
| SH-015 `returnDecisionResult` | Shared contract; policy owner varies | Login/readiness/step-up/recovery response envelope | Identity reason codes/next action | typed stable decision | `canProceed.ts`, custom gate envelopes |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Material admin/security actions | Which Identity action requires generic audit; safe metadata | audit append result | `audit.ts`, `adminAudit.ts`, local AuditEvent table |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Actual sensitive Identity data read, if policy requires | sensitivity/purpose/target | AccessAuditLog result | `accessLog.ts`, `sensitiveAudit.ts` |
| SH-031 `appendDomainLifecycleEvent` | Shared mechanism; Identity owns event truth | Identity security-history append plumbing where applicable | SecurityEventType and metadata | appended owner event | generic audit substitute |
| SH-032 `createRequestContext` | Platform/Observability | Request/job/provider correlation | safe Identity IDs | request/correlation context | local request-context utility |
| SH-033 `writeStructuredLog` | Observability / Ops | Safe execution logs | dimensions/redaction | structured log | local logger |
| SH-034 `sanitizeTelemetryMetadata` | Ops/Audit payload policy | Before logs/audit/provider-error metadata | Identity secret/PII classification | sanitized metadata | ad hoc redaction |
| SH-035 `captureException` | Observability / Ops | Unexpected failures | safe context | exception reference | local error reporter |
| SH-036 `emitMetric` | Observability / Ops | auth/recovery/provider health/latency | metric names/dimensions | metric | local metrics backend |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Provider failures/reconciliation discrepancies | normalized failure class | ops failure record/ref | Identity `IntegrationFailure` table |
| SH-039 `checkServiceHealth` | Observability / Ops | Auth/OTP/recovery provider health | owner-supplied health semantics | healthy/degraded/unavailable | local health framework |
| SH-041 `requestNotification` | Notification | Recovery/security alerts | trigger, urgency, safe variables | accepted notification request | `sendEmail.ts`, `sendSms.ts`, generic notifier |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | Provisioning, provider link, challenge verification, recovery completion | semantic idempotency key/replay response | replay-safe command result | `idempotency.ts`, `once.ts`, command-deduper store |
| SH-046 `publishDomainEvent` | Platform outbox | After committed Identity fact needing consumers | event name/version/payload | durable outbox publication | local event bus/outbox |
| SH-047 `enqueueReliableJob` | Shared queue | Expiry/reconciliation/privacy execution | job payload/idempotency/failure classification | durable job | local queue runner |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform | Retry safe provider/background work | retryable vs terminal policy | bounded retry result | local retry library |
| SH-049 `orchestrateWorkflowSteps` | Workflow owner + shared runner | Recovery multi-step orchestration if needed | recovery state remains Identity-owned | durable step orchestration | generic “identity saga” owning truth |
| SH-050 `reconcileWorkflowStatus` | Workflow owner + shared helper | Recovery/provider reconciliation | Identity expected-vs-observed mapping | reconciliation result | ad hoc repair script as source truth |
| SH-051 `acquireAggregateLock` | Shared persistence | Provider link, challenge, recovery, role mutation races | aggregate key | acquired/conflict | `mutex.ts`, in-memory lock |
| SH-052 `withOptimisticConcurrency` | Shared persistence | Update where version/compare-and-set chosen | expected version semantics | success/conflict | custom version helper |
| SH-053 `transitionLifecycleState` | Shared mechanism; Identity supplies policy | Step-up/recovery/credential transitions | allowed matrix + evidence | transitioned/conflict/invalid transition | generic state machine that owns policy |
| SH-055 `runDeadlineExpiration` | Shared scheduler/queue | Challenge/recovery deadline processing | expiry semantics | expired/no-op | local cron/timeout manager |
| SH-059 `verifyProviderWebhookSignature` | Shared integration-security shell | Recovery/auth provider callbacks where present | provider algorithm adapter/config | verified/rejected | `verifyWebhook.ts`, `signatureVerifier.ts` |
| SH-060 `deduplicateProviderEvent` | Provider owner + shared primitive | Before provider callback side effect | Identity provider-event truth and semantic key | first-seen/replay | `processedEvents.ts`, `webhookLog.ts` generic clone |
| SH-061 `translateProviderStatus` | Provider-owning adapter | Normalize provider results | mapping into Identity statuses | provider-neutral result | central generic mapper outside adapter |
| SH-062 `reconcileProviderState` | Provider-owning Module + shared worker | Detect callback loss/drift | Identity reconciliation policy | repaired/pending/review | local reconciliation framework |
| SH-064 `authorizeExternalProviderConnection` | Provider-owning Module | Link OAuth/auth method | which account/link is allowed | connection decision | provider-specific permission engine |
| SH-070 `deleteProviderResource` | Provider-owning Module | Privacy/security-driven external deletion/revocation | Identity provider-resource meaning | deleted/absent/retained/retryable/terminal | generic provider-delete utility detached from adapter |
| SH-072 `hashCanonicalPayload` | Shared security/crypto | Token/proof integrity where stable digest required | canonical input purpose | hash + version metadata | `hash.ts`, `cryptoUtils.ts` |
| SH-074 `generateSecureToken` | Shared security | Recovery/email bearer proof where local token required | token purpose/TTL/storage treatment | secure token + safe hash workflow | `randomToken.ts` |
| SH-075 `encryptSensitiveValue` | Shared security/crypto | Recoverable phone data | field purpose/key version | ciphertext | `encrypt.ts`, `kms.ts` wrapper |
| SH-076 `normalizeAndHashIdentifier` | Shared security/crypto | Phone/IP/device/provider identifier comparisons | normalization and purpose | versioned hash | `phoneHash.ts`, `ipHash.ts` |
| SH-078 `minimizeAndRedactProviderInput` | Source owner + shared serializer | Provider requests and stored provider metadata | Identity allowed fields | minimized payload | raw provider dump helper |
| SH-088 `manageTemporaryAccessGrant` | Shared grant mechanism; separate truth | SensitiveActionSession mechanics | assurance grant meaning/scope | grant mechanics | one universal AccessGrant table |
| SH-089 `revokeTemporaryAccessGrant` | Each grant owner | Revoke SensitiveActionSession | Identity revocation reason | revoked/no-op | generic cross-domain grant owner |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; Identity executes | Privacy target execution | Identity disposition mapping | standardized result | `deleteUser.ts`, local privacy job |
| SH-096 `enumerateSubjectData` | Each data owner through Privacy contract | Inventory Identity records/provider refs | Identity subject mapping | record categories/refs | schema crawler as policy |
| SH-097 `evaluateRetentionRequirement` | Identity supplies facts; Privacy records exemption | Before destructive privacy action | security/legal retention facts | retain/anonymize/delete eligibility facts | local retention exemption table |
| SH-098 `anonymizePersonalFields` | Shared primitive; owner supplies mapping | Approved anonymization | Identity field mapping | anonymized values/result | blanket null/delete helper |

### Shared operation classification notes

- SH-001 and SH-014 are **Identity-owned canonical shared capabilities** exposed to the rest of the platform.
- SH-002, SH-008, SH-011/012, SH-029/030, SH-041, and SH-095–099 are **other Modules’ public/cross-cutting interfaces** consumed by Identity.
- SH-044–055, SH-072–078 are **platform primitives/shared mechanisms**; Identity supplies domain policy and semantic keys.
- SH-059–062 are **provider-adapter patterns/shared mechanisms with separate Identity provider truth**.
- SH-088/089 are **shared grant mechanics with separate domain records**.

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
|---|---|---|---|---|---|
| `evaluateAgeEligibilityPolicy` | Apply age/region rule | minimized declaration + policy context | AgeGateResult/reason | none directly | Identity owns pre-account eligibility |
| `mapProviderIdentityToUser` | Normalize provider subject to local account mapping | provider-neutral subject | User/mapping decision | User/AuthProviderAccount | Core Identity semantic |
| `evaluateCredentialViability` | Prevent removal of last viable login/recovery route | active methods/security posture | allow/deny | none | Identity security policy |
| `deriveSecurityPosture` | Build safe posture DTO from authoritative records | User/security records | posture | no write or summary update | Identity interpretation |
| `selectStepUpMethod` | Choose permitted challenge method | security posture/action/risk | challenge type | StepUpChallenge on command | Identity assurance policy |
| `validateSensitiveActionSession` | Validate grant scope | actor/action/target/grant | valid/invalid reason | none | Identity assurance semantics |
| `applyPasskeyFallbackPolicy` | Handle repeated passkey failure | credential/challenge history | fallback/lock/recovery decision | challenge/profile/events | Identity security policy |
| `applyRecoveryTransition` | Enforce recovery state machine | current state + normalized evidence | next state | AccountRecoveryRequest | Identity owns lifecycle |
| `replaceVerifiedPhone` | Change encrypted/hash/verification fields after recovery | verified recovery proof | updated security profile | UserSecurityProfile | Identity owns phone security |
| `appendUserSecurityEvent` | Append Identity security history | typed security fact | UserSecurityEvent | UserSecurityEvent | Identity-specific event vocabulary |
| `buildIdentityEventPayload` | Minimize integration event | committed fact | versioned event DTO | no source truth | Identity knows safe domain payload |
| `resolveIdentityPrivacyDisposition` | Map Privacy instruction to Identity records | target + retention facts | owner action plan | Identity records | Data owner must know field meaning |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Temporary grants:** use SH-088/089 mechanics, but `SensitiveActionSession` remains Identity truth. Never reuse it as Media/Video/Download/Agreement entitlement.
2. **Provider event dedupe:** use SH-060 mechanics, but Identity owns only Identity-provider event receipt truth. Payment/Calendar/Video ledgers remain separate.
3. **Lifecycle plumbing:** SH-053 can perform transaction-safe transitions; Identity owns the step-up/recovery transition matrices.
4. **Workflow runner:** SH-049 can execute recovery steps; `AccountRecoveryRequest` remains workflow truth.
5. **Readiness response:** SH-015 may standardize envelope; Identity owns login/step-up/recovery reason semantics.
6. **Hashing/encryption:** shared crypto owns algorithms/key handling; Identity owns field purpose, normalization choice, comparison semantics, TTL, and rotation behavior.
7. **Outbox:** platform owns durable publish mechanism; Identity owns event vocabulary/payload.
8. **Audit:** Audit owns generic ledger; Identity owns `UserSecurityEvent`.
9. **Observability:** Ops owns telemetry; Identity source records remain authoritative.
10. **Privacy:** Privacy owns request/job/exemption; Identity owns execution against Identity records.
11. **Provider snapshots/reconciliation:** shared mechanism may store normalized evidence if approved; provider payload never becomes account truth.
12. **Security profile summaries:** projection-like summary fields can be rebuilt from owner records where possible; they are not independent credential truth.

---

## 18. Authentication and Authorization

### Authentication

All protected platform workflows should begin with SH-001 `resolveAuthenticatedActor`.

The actor context must be server-created from verified provider/session evidence and local User mapping. Client-supplied User IDs, roles, security flags, or “MFA complete” booleans never establish identity.

Active provider session truth appears to remain provider-managed because no local Workin Ants session model is present. Workin Ants owns the local User mapping, provider-link record, security posture, login-readiness policy, and any local assurance grants.

### Authorization

Identity & Access does not interpret platform roles as permissions.

For Identity-owned protected actions:

```text
resolveAuthenticatedActor
→ query Identity target facts
→ SH-002 authorizeResourceAction
→ SH-014 if sensitive
→ apply Identity command
```

Examples requiring Role / Authority:

- view another User’s security posture;
- admin/support security action;
- assign/remove platform role;
- manual recovery review;
- unlock/lock another account when actor-driven;
- revoke another User’s credential.

### Resource ownership

For self-service account-security operations, Identity supplies the fact that `targetUserId == actor.userId`. Role / Authority interprets whether the named action permits self-service.

### Organization/participant context

Identity does not use organization membership or thread participation to establish account identity. If a downstream business action needs those facts, the downstream action owner and Role / Authority compose them.

### Admin/support

Admin/support status is structural `UserRole` data, but privilege interpretation belongs to Role / Authority. High-risk admin security operations are candidates for step-up; the exact matrix is unresolved.

---

## 19. Compliance / Readiness / Entitlement Gates

### Age eligibility

- **Underlying truth owner:** Identity & Access.
- **Action gated:** account provisioning.
- **Decision:** allowed / blocked / manual review.
- **Rule:** no User creation on blocked age-gate path when gate active.

### Login/security readiness

- **Owner:** Identity & Access.
- **Inputs:** provider link, credential state, security tier/lock, recovery state.
- **Action gated:** normal authenticated session use or security fallback.
- **Decision:** ready / step-up / recovery / locked / denied / unavailable.

### Sensitive-action step-up

- **Owner:** Identity & Access for assurance.
- **Consumer:** resource/business action owner.
- **Action gated:** action named by approved `StepUpActionType` or approved cross-module action registry.
- **Composition:** authorization first; step-up does not grant resource permission.

### Consent

- **Underlying truth owner:** Consent & Disclosure.
- **Identity use:** only where a specific security flow requires versioned disclosure.
- **Rule:** consent proof does not prove passkey registration, OTP success, recovery verification, or MFA satisfaction.

### ComplianceHold

- **Owner:** Admin Review / Compliance Hold.
- **Identity use:** approved high-risk/admin/recovery cases only.
- **Rule:** local security lock is not a hold; a hold decision does not automatically mutate UserSecurityProfile unless a separate Identity command is explicitly invoked.

### Entitlement

Core authentication/security is not a paid entitlement. Track Subscription & Entitlement must not gate the ability to protect or recover a basic account.

### Recovery identity verification

- **Owner of recovery truth:** Identity & Access.
- **Provider:** Stripe Identity/Persona/manual adapter as approved.
- **Action gated:** changed-phone/access restoration.
- **Rule:** provider success is evidence; Identity transition owns completion.

---

## 20. Provider Integrations

### 20.1 Authentication/session provider

```text
request/session
→ AuthenticationSessionPort
→ Supabase Auth adapter
→ normalized authenticated subject/session assurance
→ Identity maps to User
→ SH-001 actor result
```

Provider token/session details remain server-side.

### 20.2 OAuth providers

Google/Apple or other OAuth flows remain behind provider-neutral auth/OAuth adapters.

Required:

- state/nonce protections according to provider standards;
- normalized provider subject/account IDs;
- no provider payload types in domain contracts;
- idempotent local linkage;
- explicit conflict/manual-review behavior for ambiguous mapping.

OAuth age-gate sequencing is unresolved; do not allow OAuth account creation to bypass the pre-account gate.

### 20.3 Passkey/WebAuthn

```text
begin registration/authentication
→ PasskeyPort/WebAuthn adapter
→ browser/authenticator/provider ceremony
→ verified normalized result
→ PasskeyCredential / StepUpChallenge transition
```

Never persist raw biometric data. Passkeys prove possession/authentication through WebAuthn; they are not biometric-image storage.

### 20.4 OTP verification

```text
create challenge
→ OtpVerificationPort
→ Twilio Verify or approved equivalent
→ normalized success/failure/expiry result
→ Identity transition
```

No plaintext OTP in Postgres. The current evidence specifies five-minute SMS OTP expiry. Exact `codeHash` storage strategy remains unresolved.

### 20.5 Recovery identity verification

```text
AccountRecoveryRequest reaches identity_verification_pending
→ RecoveryIdentityVerificationPort
→ Stripe Identity / Persona / approved manual adapter
→ verified / failed / review / unavailable result
→ verified callback/poll is authenticated/deduped/translated
→ Identity applies recovery transition
```

No recovery provider may mutate User/phone fields directly.

### 20.6 Provider credentials

Provider API keys/secrets live in server-side environment/secret management according to root standards. They must not be persisted in Identity models, client bundles, logs, analytics, or event payloads.

### 20.7 Webhooks

When a provider uses callbacks:

1. obtain raw body/signature context;
2. SH-059 verify signature before business parsing/effects;
3. SH-060 claim/deduplicate provider event;
4. adapter SH-061 translates provider status;
5. acquire recovery/credential aggregate lock;
6. apply Identity transition;
7. append security history and outbox event;
8. acknowledge provider only after durable handling per adapter contract;
9. reconcile later with SH-062 if callbacks may be lost/out of order.

### 20.8 Reconciliation

Provider reconciliation must compare normalized external evidence to Workin Ants owner state and either:

- confirm consistency;
- apply an idempotent allowed transition;
- leave pending and retry;
- create operational discrepancy;
- route to manual review.

It must never silently rewrite Identity truth from an unknown provider status.

---

## 21. Events and Outbox

### Identity-owned domain/security history

`UserSecurityEvent` records security-specific facts and is not the outbox.

### Integration events

Publish only facts needed by a known consumer. Event payloads should contain:

- event ID/version/type;
- occurred-at;
- aggregate/user reference;
- correlation/request ID;
- minimal changed fact;
- no raw token/OTP/phone/provider secret;
- no raw provider payload.

### Transactional outbox

For a transition that both changes Identity truth and must notify downstream consumers, the source write and SH-046 outbox record should commit atomically where root architecture supports it.

Examples:

```text
User provisioned
→ User + baseline security state commit
→ identity.user.provisioned.v1 outbox
```

```text
Recovery completed
→ AccountRecoveryRequest + UserSecurityProfile commit
→ UserSecurityEvent append
→ identity.recovery.completed.v1 / phone.changed.v1 outbox as needed
```

### Consumer idempotency

Consumers must deduplicate domain events through platform inbox mechanism. Identity does not promise exactly-once delivery.

### Events are not commands

`identity.recovery.completed` means recovery completed. It must not encode “go create X record now” as hidden cross-domain ownership transfer. A consumer chooses how to react under its own policy.

---

## 22. Background Jobs / Scheduled Work

### A. Step-up challenge expiration

- **Purpose:** mark or treat pending challenges past `expiresAt` as expired.
- **Owner:** Identity & Access.
- **Input:** challenge ID/deadline.
- **Idempotency key:** challenge ID + expiry deadline/version.
- **Shared mechanism:** SH-055 + SH-047.
- **Retryable:** transient DB/queue error.
- **Permanent:** challenge absent/already terminal → successful no-op.
- **Truth updated:** StepUpChallenge status/event if physical transition is used.
- **Telemetry:** expiry count, lag, failure.

### B. Recovery expiration

- **Purpose:** expire stale nonterminal recovery requests.
- **Owner:** Identity & Access.
- **Input:** recovery ID/deadline.
- **Idempotency key:** recovery ID + expiry deadline.
- **Shared mechanism:** SH-055/047/053.
- **Truth:** AccountRecoveryRequest status/security event.
- **Retry/dead-letter:** standard shared queue; manual review if repeated operational failure affects active recovery.

### C. Provider reconciliation

- **Purpose:** detect missing/out-of-order provider callbacks or local/provider drift.
- **Owner:** Identity & Access for Identity providers.
- **Input:** provider reference + aggregate ID.
- **Idempotency:** provider+aggregate+reconciliation window.
- **Shared:** SH-062, SH-048, SH-037/038.
- **Truth:** only allowed Identity transition or discrepancy; unknown status routes review.
- **Permanent failure:** provider resource absent/unsupported according to adapter policy.
- **Manual review:** inconsistent identity evidence or unsafe automatic transition.

### D. Privacy target worker

- **Purpose:** execute a Privacy-selected Identity target disposition.
- **Owner:** Identity for data mutation; Privacy for workflow orchestration.
- **Input:** target instruction ID + Identity target.
- **Idempotency:** Privacy target ID.
- **Shared:** SH-095/097/098/047.
- **Truth:** Identity records only; standardized result returned to Privacy.

Generic queue mechanics, retry/backoff, telemetry, and DLQ are platform-owned.

---

## 23. Concurrency and Idempotency

### High-risk races

1. duplicate signup/provisioning;
2. two provider identities racing to link to one/different User;
3. repeated OAuth/provider callbacks;
4. duplicate passkey registration completion;
5. passkey revoke vs use;
6. multiple simultaneous step-up challenges;
7. simultaneous challenge verification attempts;
8. challenge verification vs expiry/cancel;
9. multiple active recovery requests;
10. recovery provider duplicate/out-of-order callbacks;
11. recovery completion vs cancellation/expiry/manual review;
12. phone replacement vs security-profile mutation;
13. platform-role add/remove races;
14. Privacy execution vs account/security mutation.

### Lock/constraint strategy

Use database-backed mechanisms, not in-memory locks.

| Aggregate/race | Suggested lock/constraint |
|---|---|
| User provisioning | provider identity unique constraint + SH-044 idempotency; lock mapping/user aggregate |
| Provider linking | unique provider identity + SH-051 on provider/user |
| Passkey registration | unique `credentialIdHash`; idempotent completion |
| Step-up verification | SH-051 on challenge ID; conditional transition from `pending` |
| Sensitive session issue | same transaction as verified challenge; semantic uniqueness if final policy requires |
| Recovery transition | SH-051 on recovery/User security aggregate; transition compare current status |
| Phone replacement | lock UserSecurityProfile/recovery; single completion transaction |
| Platform role | composite `(userId,role)` + idempotent command |

### Optimistic/pessimistic choice

Use row/aggregate locking for single-consumption transitions (challenge verification, recovery completion) where lost updates are unacceptable. SH-052 may be used for profile/admin updates if an approved version/compare-and-set field exists. Do not invent a fake in-memory mutex.

### Replay semantics

A retried command with the same semantic idempotency key should return:

- the original successful semantic result when safe;
- `already_completed` when the original result cannot be replayed verbatim;
- explicit conflict if the same key is reused with a different canonical payload.

### Provider event idempotency

Provider event ID dedupe is separate from command idempotency. A provider event replay must not repeat phone changes, grant issuance, notifications, or downstream events.

---

## 24. Media / Storage

Identity & Access is not a file-storage Module.

Current `User.avatarUrl` and other public/profile fields create an ownership concern. Until that concern is resolved:

- do not build avatar upload, scanning, object storage, signed URLs, or generic MediaAsset grants inside Identity;
- do not interpret a stored URL as access truth;
- if an account surface needs an avatar, use the approved profile/media owner contract once that ownership is settled;
- no identity document from a recovery provider should be copied into Identity storage unless a separate compliance architecture explicitly requires it;
- recovery provider document retention/deletion remains provider-adapter/privacy policy, not ad hoc Media storage.

---

## 25. Search / Projection

Identity & Access has no confirmed Typesense/public-search projection.

The current `User` schema includes public/profile-like fields (`displayName`, `bio`, location fields, `isPublic`, `avatarUrl`) that conflict with the “User is base account only” principle and profile/search boundaries.

Until ownership is resolved:

- do not create a public User search projection;
- do not call SH-091 merely because `isPublic` exists;
- do not make Search reconstruct authentication/security posture;
- never index security profile, provider linkage, phone, roles beyond explicitly approved public role display, passkeys, recovery, challenge/session, or security-event data.

If a future source projection is approved, Identity supplies only the minimal source projection; Search owns indexing/execution.

---

## 26. Notification

Identity owns business/security triggers, not delivery.

Typical notification intents:

- auth method linked/revoked;
- passkey registered/revoked;
- credential compromised;
- sensitive security settings changed;
- recovery email link;
- recovery initiated/completed/failed/manual review;
- phone changed;
- local security lock/unlock.

Payload rules:

- no OTP plaintext;
- no bearer recovery token in generic logs/events; secure link/token delivery uses the approved Notification/provider contract;
- no full phone number where masked value suffices;
- no raw provider status/document;
- no security secret in template metadata.

Special boundary: an OTP provider such as Twilio Verify may send verification SMS as part of the Identity-owned verification protocol. That does not make Identity the owner of the platform’s generic Notification delivery subsystem.

---

## 27. Audit and Sensitive Access

### `UserSecurityEvent`

Identity-owned security lifecycle history.

Examples:

- auth provider linked/revoked;
- passkey registered/used/failed/revoked;
- step-up challenge created/verified/failed/expired;
- recovery started/email verified/identity verified/completed/failed;
- phone changed;
- backup fallback used;
- security profile updated.

### `AuditEvent`

Generic platform/admin audit via SH-029.

Examples:

- admin changes platform role;
- admin manually reviews recovery;
- admin locks/unlocks another account;
- material security-policy override.

### `AccessAuditLog`

Generic sensitive-access proof via SH-030.

Use when an actor actually reads protected Identity data under the platform sensitivity matrix.

### Critical separation

`sensitive_action_accessed` in `UserSecurityEvent` should prove that Identity assurance was used. The financial/healthcare/file/resume owner records actual sensitive data access through AccessAuditLog. Identity must not claim it knows what downstream protected data was viewed merely because it supplied step-up proof.

---

## 28. Privacy and Retention

### Subject-data inventory

At minimum Identity must enumerate:

- `User` personal/account fields;
- `UserRole` where subject-linked;
- subject-linked AgeGateAttempt records where resolvable;
- `UserSecurityProfile`, including encrypted/hashed phone metadata;
- `AuthProviderAccount`;
- `PasskeyCredential` metadata;
- `StepUpChallenge`;
- `SensitiveActionSession`;
- `AccountRecoveryRequest`;
- `UserSecurityEvent`;
- Identity-owned provider references/resources.

Pre-account age-gate hashes may not always be safely resolvable to a specific person; enumeration must not create a new identifying linkage solely for privacy discovery.

### Privacy executor

```text
Privacy verifies request
→ SH-096 asks Identity to enumerate subject data
→ Identity returns record/provider categories + retention facts
→ Privacy supplies target disposition / exemption
→ SH-095 invokes Identity executor
→ Identity anonymizes/revokes/deletes/retains only its records
→ provider resource deletion through Identity adapter/SH-070 if instructed
→ Identity returns standardized result
→ Privacy records target/job truth
```

### Retention

Exact retention periods for security events, recovery evidence, token hashes, phone hashes, provider references, and age-gate proof are unresolved.

Until approved:

- no production hard-delete path may cascade through Identity security evidence by convenience;
- no “delete user” endpoint should directly cascade through the graph;
- expired tokens/challenges should be rendered unusable immediately even if the record is retained;
- personal fields may be anonymized only through an approved mapping;
- provider deletion/revocation and local retention may differ and must be reported explicitly.

### Export

Identity may contribute a privacy export fragment containing safe user-facing account/security history as approved. Privacy owns the final export artifact and delivery.

---

## 29. Observability

Identity operations must use structured, redacted observability.

Safe dimensions may include:

- operation name;
- module `identity_access`;
- request/correlation ID;
- User ID/internal aggregate ID where approved;
- challenge/recovery/provider adapter type;
- normalized status/failure class;
- retry/attempt count;
- latency;
- queue lag;
- provider health state.

Never log:

- passwords;
- OTP plaintext;
- recovery bearer tokens;
- provider session/access tokens;
- provider API secrets;
- raw biometric/WebAuthn sensitive ceremony data;
- full phone number if unnecessary;
- raw identity-verification documents/provider payload;
- arbitrary `metadata` JSON without sanitization.

Operational records never replace UserSecurityProfile, StepUpChallenge, AccountRecoveryRequest, or UserSecurityEvent.

Health checks should cover auth provider, OTP provider, passkey runtime/provider assumptions where testable, recovery verification provider, queue/outbox, and database reachability without exposing sensitive provider details.

---

## 30. Security Boundaries

1. All external input is runtime-validated; TypeScript types alone are not a trust boundary.
2. Client identity/role/MFA claims are untrusted.
3. Raw passwords are provider-managed; Workin Ants stores no raw password.
4. Raw OTP is never persisted in Postgres.
5. Raw biometric material is never persisted.
6. Provider secrets/session tokens never enter domain tables or client payloads.
7. Recovery tokens are high-entropy, short-lived, one-purpose, and stored only as approved hash/proof.
8. SMS OTP currently has five-minute expiry; recovery email token currently has fifteen-minute expiry unless architecture changes.
9. Hash/encryption uses canonical shared primitives with purpose/versioning.
10. Phone number reversible storage is encrypted; comparison/search value is normalized+hashed.
11. Rate limits apply to age gate, login, provider link, passkey, OTP, and recovery entry points. Thresholds are Identity policy.
12. Unknown provider status fails to explicit unavailable/review/unsupported state.
13. Step-up grant validation checks user/action/target/expiry/revocation every time.
14. `lastStepUpAt` is never a grant.
15. Repeated passkey failure triggers approved fallback, not automatic permanent lockout.
16. OAuth flow may not bypass age-gate sequencing once the final sequencing decision is approved.
17. Provider callbacks are signature-verified and deduped.
18. Security admin actions require Role authorization and step-up where the approved matrix says so.
19. RLS/server policy must protect sensitive Identity tables and remain semantically aligned with Role / Authority.
20. Security-event metadata is schema-limited/sanitized; do not use JSON as a secret dumping ground.
21. Error responses must prevent user/account enumeration where relevant to login/recovery.
22. No in-memory lock is authoritative for database-owned concurrency.

---

## 31. Error / Decision Result Pattern

Public interfaces should return provider-neutral typed failures.

Recommended stable categories:

| Category | Meaning | Example reason codes |
|---|---|---|
| `invalid_input` | Request failed validation | `INVALID_AGE_DECLARATION`, `INVALID_TARGET` |
| `unauthenticated` | No valid actor session | `SESSION_MISSING`, `SESSION_INVALID` |
| `authorization_denied` | Role / Authority denied | `ACTION_NOT_ALLOWED` |
| `age_ineligible` | Age/region prevents account creation | `UNDERAGE`, `REGION_BLOCKED` |
| `blocked` | Local security/cooldown/approved hold blocks | `AGE_COOLDOWN`, `SECURITY_LOCK`, `COMPLIANCE_HOLD` |
| `step_up_required` | More assurance required | `FRESH_ASSURANCE_REQUIRED` |
| `challenge_invalid` | Challenge proof invalid | `INVALID_CODE`, `WRONG_TARGET`, `WRONG_ACTOR` |
| `challenge_expired` | Deadline passed | `CHALLENGE_EXPIRED` |
| `challenge_locked` | Attempts/risk policy prevents verification | `MAX_ATTEMPTS`, `RISK_BLOCK` |
| `assurance_expired` | Sensitive grant no longer valid | `SESSION_EXPIRED`, `SESSION_REVOKED` |
| `recovery_required` | Normal login unavailable; recovery needed | `CREDENTIAL_UNAVAILABLE`, `ACCOUNT_LOCKED` |
| `recovery_pending` | Recovery has not reached completion | `IDENTITY_VERIFICATION_PENDING` |
| `manual_review` | Automatic decision unsafe | `RECOVERY_REVIEW_REQUIRED`, `IDENTITY_CONFLICT` |
| `conflict` | Stale/concurrent/semantic conflict | `PROVIDER_ALREADY_LINKED`, `STALE_TRANSITION` |
| `rate_limited` | Abuse control throttled | `TOO_MANY_ATTEMPTS` |
| `provider_unavailable` | External rail unavailable | `AUTH_PROVIDER_UNAVAILABLE`, `OTP_PROVIDER_UNAVAILABLE`, `RECOVERY_PROVIDER_UNAVAILABLE` |
| `retention_blocked` | Privacy target cannot be destructively handled | `RETENTION_REQUIRED` |
| `internal_error` | Unexpected safe failure | `UNEXPECTED_IDENTITY_ERROR` |

Raw provider error text/codes may be retained in sanitized operational diagnostics but must not leak as public contract semantics.

---

## 32. Testing Architecture

### Domain unit tests

- age/region eligibility matrix;
- cooldown policy;
- credential viability/removal rules;
- security-tier/lock policy once approved;
- step-up method selection;
- challenge transition matrix;
- attempt/TTL/fallback rules;
- SensitiveActionSession scope validation;
- recovery transition matrix;
- phone replacement preconditions;
- security-event metadata minimization.

### State-transition tests

- every allowed/forbidden `StepUpChallengeStatus` transition;
- every approved recovery transition and prohibited shortcut;
- credential status transitions;
- role add/remove idempotency;
- local lock expiry/unlock;
- provider unknown status.

### Public contract tests

- SH-001 actor DTO;
- SH-014 assurance result;
- safe security posture;
- authentication-method list;
- recovery status;
- stable reason codes;
- privacy executor result;
- event schema versions.

### Database/integration tests

- age-gate no User on blocked path;
- provider mapping uniqueness after ruling;
- `AgeGateBlock` matchable identifier constraint after ruling;
- `credentialIdHash` uniqueness;
- composite UserRole uniqueness;
- transaction atomicity for challenge verify + grant;
- recovery completion atomicity;
- security-event append;
- outbox atomicity;
- retention-safe delete protections.

### Authorization/RLS tests

- self vs other User security access;
- admin/support role boundaries;
- role assignment/removal;
- manual recovery review;
- sensitive Identity tables inaccessible cross-user;
- server authorization and RLS parity where direct DB access exists.

### Compliance/security tests

- no raw password/OTP/biometric/provider secret in schema/log fixtures;
- age gate precedes User creation;
- five-minute OTP and fifteen-minute recovery-token behavior under current policy;
- changed-phone recovery requires identity-verification evidence;
- notifications do not count as security proof;
- security lock != ComplianceHold;
- consent proof != security success.

### Idempotency/concurrency tests

- duplicate provisioning;
- provider link races;
- duplicate passkey registration;
- simultaneous challenge verify;
- verify vs expire/cancel;
- duplicate provider callbacks;
- parallel recovery requests according to approved rule;
- completion vs cancellation;
- role mutation races;
- privacy execution replay.

### Provider adapter tests

- auth/session normalization;
- OAuth subject normalization;
- WebAuthn success/failure;
- OTP success/expiry/provider outage;
- recovery provider verified/failed/review/unknown;
- webhook signature valid/invalid;
- event replay;
- out-of-order callback;
- reconciliation.

### Privacy tests

- subject-data enumeration;
- target executor touches Identity records only;
- retention exemption respected;
- provider deletion/revocation result;
- no uncontrolled User cascade;
- anonymization mapping.

### End-to-end participation

At minimum:

1. age-eligible signup → User → authenticated actor;
2. blocked signup → no User;
3. linked passkey → sensitive action requests step-up → verified scoped grant;
4. wrong-target/expired/revoked grant denied;
5. successful recovery proof chain → phone/access update;
6. duplicate recovery callback does not double-complete;
7. downstream Order/Payment/Admin test consumer uses SH-014 without local MFA;
8. Privacy request reaches Identity executor through contract.

---

## 33. Module Invariants

### Rules coding agents must never violate

1. `User` is base account identity only.
2. No blocked age-gate path may create a local User when the gate is active.
3. No raw password may be stored in Workin Ants domain persistence.
4. No plaintext OTP may be stored in Postgres.
5. No raw biometric material may be stored.
6. No provider secret/session/access token may be exposed through public DTOs, domain events, logs, analytics, or audit metadata.
7. Provider state is normalized evidence; Identity transition services own local state.
8. SH-001 is the canonical authenticated actor boundary; feature-local current-user/session helpers are prohibited.
9. Identity owns `UserRole` rows; Role / Authority owns permission interpretation.
10. Identity must call SH-002 for protected Identity mutations that require permission; it must not interpret `PlatformRole` ad hoc.
11. `passkeysEnabled` and `smsMfaEnabled` must not independently prove credential/MFA truth.
12. `lastStepUpAt` must never authorize a sensitive action by itself.
13. Sensitive assurance must be bound to actor, action, optional target, expiry, revocation, and required assurance.
14. SensitiveActionSession must remain separate from Media, Video, Digital Download, Agreement, or other access grants.
15. A provider failure or notification delivery must never create assurance.
16. A recovery identity provider result must never mutate User/phone state directly.
17. Changed-phone recovery must not complete without the approved proof chain.
18. Account recovery must never reuse payout KYC or marketplace VerificationCheck as its source truth.
19. Repeated passkey failure must follow fallback policy rather than permanent accidental lockout.
20. Security lock and ComplianceHold are separate records/meanings.
21. UserSecurityEvent, AuditEvent, AccessAuditLog, outbox events, and observability records must remain separate.
22. Consumers must not poll UserSecurityEvent as an integration bus.
23. Provider callbacks must be authenticated and deduped before side effects.
24. Duplicate provider callbacks must not repeat phone updates, grant creation, events, or notifications.
25. Every concurrency-sensitive transition uses database-backed constraints/locks/conditional updates.
26. No in-memory lock may be relied on for authoritative concurrency.
27. Privacy / Data Erasure owns request/job/target orchestration; Identity implements only its executor.
28. No direct hard-delete User path may bypass retention analysis.
29. Notification owns delivery; Identity owns only security notification intent.
30. Search/public profile projection must remain disabled until User/profile field ownership is resolved.
31. Core account security must not be subscription-gated.
32. Unknown sensitive action/provider status fails closed or to explicit review/unavailable.
33. No unresolved architecture decision may be silently settled in feature code.
34. Cross-Module reads/writes must use approved public interfaces rather than foreign repositories by default.
35. Security-event metadata must be minimized and sanitized.
36. Every public mutation is runtime-validated server-side.
37. Every retryable external effect has an idempotency/reconciliation story.
38. Role changes, recovery completion, credential compromise, and other high-impact security mutations must produce the approved security/audit evidence.
39. Provider adapter SDK types must stop at the adapter boundary.
40. Build progress cannot redefine this Module’s ownership or lifecycles.

---

## 34. Prohibited Duplicate Implementations

Do not generate these Identity-local or feature-local duplicates where the responsibility is canonical/shared/externally owned:

### Authentication/session duplicates

- `auth.ts` in each feature
- `session.ts`
- `getCurrentUser.ts`
- `requireUser.ts`
- `currentUser.ts`
- local Supabase token parser bypassing SH-001
- a second User/account table

### Authorization duplicates

- `permissions.ts`
- `accessControl.ts`
- `isAdmin.ts`
- `isSupport.ts`
- `roleGuard.ts`
- business-owner/organization/thread authorization inside Identity

### Consent/entitlement duplicates

- `consentGuard.ts`
- `termsCheck.ts`
- `hasAccepted.ts`
- `premiumGuard.ts`
- `featureGate.ts`
- any `isPremium`/plan flag on User/SecurityProfile

### Audit/notification/ops duplicates

- `auditService.ts` that owns generic AuditEvent
- `accessLog.ts` that owns AccessAuditLog
- `sendEmail.ts` / `sendSms.ts` generic sender
- Identity-owned Notification/Delivery tables
- Identity-owned `IntegrationFailure`, `SystemEvent`, or queue telemetry tables

### Infrastructure duplicates

- `idempotency.ts` with local store
- `queue.ts`, `retry.ts`, `backgroundTasks.ts` as a second platform queue
- `mutex.ts` / in-memory concurrency guard
- private outbox/event bus
- local webhook signature framework
- local provider-event dedupe framework
- local generic workflow engine

### Crypto duplicates

- `hash.ts`
- `cryptoUtils.ts`
- `tokenHash.ts`
- `ipHash.ts`
- `encrypt.ts`
- `kms.ts`
- local random-token generator

### Privacy duplicates

- `deleteUser.ts` as direct hard-delete workflow
- `eraseAccount.ts`
- `gdprDelete.ts`
- local PrivacyRequest/DataErasureJob
- local retention-exemption table

### Grant duplicates

- one generic `AccessGrant` table replacing SensitiveActionSession and other Modules’ grant records
- feature-local `lastMfaAt`/`mfaSatisfied` booleans used as authorization truth

### Important nuance

One canonical Identity-owned `appendUserSecurityEvent` implementation is required. The prohibition is against parallel writers such as `securityLog.ts`, `authAudit.ts`, and `loginEvent.ts` that independently decide security-event semantics.

---

## 35. Unresolved Decisions

The following must remain explicit. Dependent production behavior must be disabled, constrained to a safe subset, or resolved through architecture before implementation.

| ID | Unresolved decision | Why it matters | Safe interim posture |
|---|---|---|---|
| U-IA-01 | Does `User.id` equal the Supabase auth-user UUID or use a separate UUID mapped by AuthProviderAccount? | Provisioning uniqueness, foreign references, migration | Use one adapter/mapping contract; do not assume equality in cross-Module code |
| U-IA-02 | Exact OAuth age-gate sequencing and state binding | OAuth could create provider/local identity before age eligibility | Do not enable an OAuth path that bypasses age gate |
| U-IA-03 | Provider-account merge, canonical-email, and multi-provider account linking policy | Prevent account takeover/duplicate Users | Conflicts route explicit review; no automatic email-based merge |
| U-IA-04 | Session revocation matrix after compromise, role change, recovery, phone replacement, passkey revoke | Determines security containment | Build SessionRevocationPort/hook; do not invent global behavior |
| U-IA-05 | Is `StepUpActionType` purely Identity-owned or a cross-Module sensitive-action registry? | Avoid repeated migrations and uncontrolled `other` | Support current approved values; unknown action fails closed |
| U-IA-06 | May `StepUpChallenge.codeHash` store a hashed OTP, or must challenge secret state remain provider/cache-managed? | Secret exposure, TTL, operational design | No plaintext OTP; provider-managed challenge preferred until ruling |
| U-IA-07 | Multiple simultaneous step-up challenge policy | Race/replay and UX | Serialize same actor/action/target or fail conflict; exact replacement rule requires approval |
| U-IA-08 | Multiple active recovery request policy | Prevent conflicting phone/access changes | Do not allow ambiguous parallel completion; fail closed |
| U-IA-09 | Identity provider processed-event schema/name for recovery callbacks | SH-060 requires owner-specific dedupe truth | Provider callback activation blocked until approved durable receipt/dedupe truth exists |
| U-IA-10 | Recovery `manual_review` reviewer authority, review record, and relationship to ComplianceHold | Administrative evidence and separation of truths | Manual review state may be surfaced; completion requires approved review contract |
| U-IA-11 | `UserSecurityTier` transition policy | `standard/elevated/high_risk` lacks transition rules | Treat as read/write only through explicitly approved security policy |
| U-IA-12 | Retention periods/dispositions for security/recovery/token/phone/provider evidence | Privacy and legal/security obligations | No destructive hard delete absent Privacy decision |
| U-IA-13 | Ownership of User `displayName`, `avatarUrl`, `bio`, location, `isPublic` fields | Conflicts with profile/media/search boundaries | Do not expand/use for public search; ownership review required |
| U-IA-14 | Exact security-consent categories/version requirements | Avoid Identity inventing consent law/policy | Query Consent only where a named approved requirement exists |
| U-IA-15 | Backup password semantics/provider ownership behind `backupPasswordConfigured` | Raw password prohibited; bool could be misleading | Treat as summary only; no local raw backup password |
| U-IA-16 | Reactivation semantics for revoked/compromised credentials | Security history/attack prevention | Relink/new credential rather than silent state reversal unless approved |
| U-IA-17 | Age-gate proof versioning fields and jurisdiction policy source | Current evidence may be insufficient to reconstruct decision | Preserve current proof; add fields only after architecture/schema ruling |
| U-IA-18 | Exact high-risk admin/security step-up matrix | Consistent protection across Modules | Named sensitive actions fail closed if policy unknown |

### Registry inconsistency to correct

Older registry evidence references `TrackEntitlement`, but the current schema uses `TrackEntitlementDefinition` and `TrackEntitlementGrant`. Identity should not introduce a `TrackEntitlement` model to satisfy stale references.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Identity & Access owns base `User` identity and Identity-specific security lifecycles.
2. `UserRole` / `PlatformRole` are structurally Identity-owned; Role / Authority interprets permissions.
3. Age-gate attempts/blocks are Identity truth and precede User creation when active.
4. UserSecurityProfile, AuthProviderAccount, PasskeyCredential, StepUpChallenge, SensitiveActionSession, AccountRecoveryRequest, and UserSecurityEvent are Identity-owned records.
5. Provider systems are rails/evidence; Workin Ants transition services own local state.
6. No raw passwords, plaintext OTPs, raw biometric material, or provider secrets belong in Identity domain persistence.
7. Sensitive-action assurance is distinct from downstream resource permission and business access grants.
8. Account recovery is distinct from payout KYC and marketplace verification.
9. Notification delivery, generic Audit/AccessAuditLog, Privacy orchestration, ComplianceHold, Ops, Media mechanics, Search execution, and entitlements remain external owners.
10. Canonical SH-### operations are consumed rather than duplicated.
11. UserSecurityEvent is Identity security history, not the generic audit ledger or event bus.
12. Privacy instructions are executed only against Identity-owned data.
13. Core account security is not subscription-gated.
14. Cross-Module consumers use public interfaces instead of Identity Prisma repositories by default.

### Proposed Rulings

- **PR-IA-01:** organize code by the Identity Deep Module boundary using domain/application/contracts/infrastructure/workers/privacy logical layers if root conventions do not already dictate equivalent structure.
- **PR-IA-02:** `passkeysEnabled` / `smsMfaEnabled` are summary/projection fields; active credential/provider evidence is authoritative.
- **PR-IA-03:** SensitiveActionSession (or explicit equivalent provider-authenticated proof under SH-014) is the durable action-scoped assurance; `lastStepUpAt` is summary only.
- **PR-IA-04:** AgeGateBlock must contain at least one usable privacy-minimized matching identifier.
- **PR-IA-05:** an accepted canonical provider identity must map uniquely to one Workin Ants User; ambiguous merge policy remains unresolved.
- **PR-IA-06:** callback-based Identity providers require owner-specific durable provider-event dedupe truth under SH-060 before production side effects.
- **PR-IA-07:** external integration events use canonical outbox contracts and remain distinct from UserSecurityEvent.
- **PR-IA-08:** UserSecurityEvent is append-only security history; corrections append new evidence rather than rewriting history.

### Binding posture for unresolved decisions

If a feature reaches U-IA-01 through U-IA-18, the agent must either:

1. resolve the decision through an approved architecture update before enabling the dependent production behavior; or
2. implement only the noncontroversial boundary/port/test-double/safe subset and keep the risky path disabled or fail-closed.

---

## 37. Coding-Agent Usage

Before implementing or changing Identity & Access, read in this order:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md`;
5. `context/clusters/identity-authority-consent-entitlements/architecture.md`;
6. `context/clusters/identity-authority-consent-entitlements/build-plan.md`;
7. this `identity_access/module-architecture.md`;
8. this `identity_access/implementation-plan.md`;
9. public-interface sections for direct dependencies, especially Role / Authority, Consent & Disclosure, Admin Review / Compliance Hold, Audit / Event Ledger, Notification, Observability / Ops, Privacy / Data Erasure, and downstream sensitive-action consumers such as Transaction / Order and Payment / Payout / Tax;
10. the current progress tracker.

The agent must also inspect the current Prisma schema and migrations before modifying data structures.

If implementation code conflicts with this document:

1. do not create a second pattern;
2. identify whether code, architecture, or evidence is stale;
3. preserve confirmed source-of-truth ownership;
4. stop at any unresolved high-risk boundary;
5. update architecture first when a legitimate binding decision changes;
6. then update implementation plan/progress and code.

Build progress reports implementation state. They do not redefine Identity ownership, security proof, provider boundaries, privacy/retention policy, or canonical Shared Operations.
