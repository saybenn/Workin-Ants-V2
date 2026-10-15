# Identity & Access Module Implementation Plan

> **Module ID:** `identity_access`  
> **Module:** Identity & Access Module  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-implementation-plan.md`\
> **Companion architecture:** `module-architecture.md`  
> **Plan status:** Sequential Module implementation plan. It is subordinate to the root Workin Ants architecture, CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-architecture.md`, and CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-build-plan.md`.\
> **Implementation posture:** Build only Identity-owned truth and stable public interfaces. Unresolved security/provider/privacy decisions are architecture gates, not implementation invitations.

---

## Core Principle

Implement Identity & Access through narrow, verifiable slices:

```text
public / observable behavior
→ validated command or query
→ Identity-owned policy
→ authoritative Identity write/read
→ canonical shared-operation calls
→ provider adapter where required
→ UserSecurityEvent / outbox / audit / notification effects
→ tests
→ explicit exit gate
```

Identity & Access is not a generic “everything access-related” subsystem.

The implementation sequence must preserve:

```text
Identity proves who the account actor is.
Role / Authority decides what that actor may attempt.
Identity provides fresh action-scoped security assurance when required.
The downstream Module still owns its business/compliance lifecycle.
```

A feature may be observable through a public contract, persisted lifecycle, provider adapter, worker, account-security surface, privacy executor, or integration test. Do not invent UI merely to make an infrastructure slice appear user-facing.

---

## Build Rules

1. Follow `context/project-overview-v3.md`, root `architecture.md`, root `code-standards.md`, the Canonical Shared Operations Registry, CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-architecture.md`, and CL-01 `context/clusters/identity, authority, & consent/identity-authority-consent-build-plan.md`.
2. Implement only truth declared as Identity-owned in `module-architecture.md`.
3. Do not absorb Role / Authority permission interpretation, Customer/Professional/Candidate profiles, organization membership, consent proof, Track entitlement, payment/payout/tax, KYC, marketplace verification, generic holds, generic audit, Notification delivery, Privacy orchestration, Media mechanics, Search execution, or Ops persistence.
4. Consume other Modules through approved public interfaces or contract fixtures. Direct foreign Prisma repositories are not the default.
5. Reuse canonical SH-### operations. Do not create Identity-local substitutes for idempotency, locks, outbox, queues, crypto, audit, observability, Notification, Privacy workflow, webhook security, or generic provider-event dedupe mechanics.
6. Every external mutation is runtime-validated server-side.
7. Every protected mutation starts from SH-001 `resolveAuthenticatedActor` and uses SH-002 `authorizeResourceAction` when authorization is required.
8. Anonymous operations are explicitly limited to age-gate, authentication entry points, recovery entry points, and verified provider callbacks.
9. Every sensitive action uses SH-014 `requireStepUpForSensitiveAction` rather than local `lastMfaAt` or frontend MFA state.
10. Every lifecycle transition is applied by Identity-owned policy in a transaction-safe manner.
11. Every retryable command is semantically idempotent.
12. Provider SDK payloads/types stop at the adapter boundary.
13. Provider callbacks are verified and deduplicated before Identity state changes.
14. Raw passwords, plaintext OTPs, raw biometric material, provider secrets, bearer recovery tokens, and unnecessary raw provider payloads must never enter Identity domain records/logs/events.
15. `UserSecurityEvent`, generic `AuditEvent`, `AccessAuditLog`, integration events/outbox, and observability records remain distinct.
16. `UserSecurityProfile` summary fields do not replace credential/challenge/grant truth.
17. `SensitiveActionSession` never becomes a generic Media/Video/Download/Agreement access grant.
18. Recovery verification is not payout KYC or marketplace verification.
19. Security lock state is not `ComplianceHold`.
20. Notification intent is Identity-owned; Notification owns generic delivery.
21. Privacy / Data Erasure owns PrivacyRequest/DataErasureJob/DataErasureTarget orchestration; Identity only enumerates and executes its targets.
22. No production User hard-delete may bypass retention review.
23. Generic queue/retry/locking mechanics must be durable, observable, and dead-letter capable through the shared platform.
24. Database-owned races use database constraints, aggregate locks, or conditional updates; never rely on frontend button disabling or in-memory locks.
25. Every numbered feature ends with tests, workflow/contract verification, documentation/progress updates, and an explicit exit gate.
26. Do not start the next numbered feature until the prior exit gate passes, except for separately tracked canonical-owner prerequisites explicitly allowed to run in parallel.
27. When a numbered feature encounters `U-IA-*`, either resolve the architecture decision first or implement only the safe noncontroversial boundary and keep dependent production behavior disabled/fail-closed.
28. Build progress must not silently alter source-of-truth ownership, provider boundaries, lifecycle meaning, or privacy/security policy.

---

## Preconditions

### Hard platform prerequisites

Before the first production mutation that needs them, the project must provide or expose approved contracts/test implementations for:

- Prisma/Postgres migration workflow;
- runtime validation and canonical error/result conventions;
- request/correlation context;
- SH-044 `executeIdempotentCommand`;
- transactional outbox through SH-046;
- consumer inbox/deduplication where Identity consumes events;
- SH-047 reliable job enqueue + retry/DLQ mechanics;
- SH-051 aggregate locking and/or approved transaction isolation;
- canonical crypto/token/hash/encryption operations;
- generic Audit / Event Ledger interface;
- Notification request interface;
- Observability / Ops interfaces;
- Privacy target-executor protocol;
- provider webhook signature-verification shell;
- provider-event dedupe primitive.

If one of these is absent, the Identity feature may depend on a versioned interface/test double, but it must not build an untracked second implementation.

### Identity schema prerequisites

The current Prisma evidence already contains the principal Identity records:

- `User`
- `UserRole`
- age-gate models/enums
- `UserSecurityProfile`
- `AuthProviderAccount`
- `PasskeyCredential`
- `StepUpChallenge`
- `SensitiveActionSession`
- `AccountRecoveryRequest`
- `UserSecurityEvent`
- Identity-owned enums/statuses

Before implementation, inspect the actual current schema and migrations. Do not recreate models because this plan names them.

### Direct dependency interfaces

The following contracts should exist before their first production use; they may initially be represented by versioned contract fakes:

- Role / Authority — SH-002 `authorizeResourceAction`
- Consent & Disclosure — SH-008 `queryConsentProof`, and SH-009 where active version resolution is required
- Admin Review / Compliance Hold — SH-011/012 as configured
- Audit / Event Ledger — SH-029/030
- Notification — SH-041
- Observability / Ops — SH-032–039
- Privacy / Data Erasure — SH-095–099 protocol

### Provider prerequisites

These may be stubbed behind Identity-owned ports for domain/contract tests:

- Supabase Auth or the approved authentication/session provider;
- Google / Apple OAuth where included;
- WebAuthn/passkey runtime/provider integration;
- Twilio Verify or approved OTP provider;
- Stripe Identity, Persona, or approved recovery identity-verification provider.

Real provider credentials are not required for pure policy/contract tests. Production activation requires provider-specific integration verification.

### Architecture gates

The following unresolved items are hard gates for dependent production behavior:

- **U-IA-01:** local User ID vs Supabase auth-user ID mapping.
- **U-IA-02:** OAuth age-gate sequencing.
- **U-IA-03:** provider merge / canonical email / multi-provider linking.
- **U-IA-04:** session revocation matrix.
- **U-IA-05:** sensitive-action vocabulary ownership.
- **U-IA-06:** `StepUpChallenge.codeHash` / OTP challenge secret storage.
- **U-IA-07:** concurrent step-up challenge policy.
- **U-IA-08:** concurrent recovery request policy.
- **U-IA-09:** durable Identity provider-event receipt/dedupe truth.
- **U-IA-10:** recovery manual-review authority/evidence.
- **U-IA-11:** security-tier transition policy.
- **U-IA-12:** retention periods/dispositions.
- **U-IA-13:** ownership of User public/profile fields.
- **U-IA-14:** exact security-consent requirements.
- **U-IA-15:** backup-password semantics.
- **U-IA-16:** credential reactivation policy.
- **U-IA-17:** age-gate policy-version proof.
- **U-IA-18:** exact high-risk admin/security step-up matrix.

A feature may still implement a safe port, DTO, adapter contract, or test fixture before a gate is resolved. It may not enable the unsafe production behavior.

---

# Phase 1 — Account Identity Foundation

## 01 Age-Gated User Provisioning and Actor Resolution

### Objective

Create the canonical account foundation: an eligible person can become exactly one Workin Ants `User`, and subsequent valid authentication/session evidence resolves through SH-001 to one server-trusted actor context.

### Observable Result

- An age/region-eligible signup can create/link one local User.
- An underage/region-blocked request creates no User.
- A repeated equivalent provisioning request returns the same semantic User result rather than creating a duplicate.
- A protected test/account endpoint can return a safe authenticated actor DTO.
- An invalid/expired provider session produces an unauthenticated result.
- The implementation contains no feature-local current-user/session helper competing with SH-001.

### Cluster Build-Plan Link

Supports **CL-01 Feature 01 — Age-Gated User Provisioning and Authenticated Actor Context**.

### Dependencies

- current `User`, `AgeGateAttempt`, `AgeGateBlock`, `AgeGateResult`, `UserSecurityProfile`, `AuthProviderAccount`, and `UserSecurityEvent` schema;
- approved authentication/session port;
- SH-044 idempotency;
- SH-076 identifier normalization/hashing;
- SH-046 outbox;
- SH-032/033/034 request/logging/redaction;
- architecture decision U-IA-01 before final production mapping assumptions;
- U-IA-02 before enabling OAuth signup that could bypass age gating.

### In Scope

- runtime validation for age-gate input;
- age/region policy service;
- cooldown lookup;
- privacy-minimized `AgeGateAttempt` persistence;
- `AgeGateBlock` creation for approved blocked outcomes;
- provider-neutral authentication subject normalization;
- idempotent local User provisioning;
- baseline `UserSecurityProfile` creation;
- initial `AuthProviderAccount` linkage for the authenticated provider;
- Identity-specific security event where required;
- SH-001 `resolveAuthenticatedActor`;
- safe actor DTO and error/result contract;
- optional `identity.user.provisioned.v1` outbox event only if a concrete consumer contract is established.

### Out of Scope

- passkeys;
- step-up/MFA;
- account recovery;
- broad OAuth merge behavior;
- CustomerProfile/ProfessionalProfile/CandidateProfile creation;
- permission interpretation;
- consent acceptance;
- subscriptions/entitlements;
- public User search/profile behavior;
- provider-account auto-merge based on email.

### Module-Owned Data

- `User`
- `AgeGateAttempt`
- `AgeGateBlock`
- `AgeGateResult`
- `UserSecurityProfile`
- `AuthProviderAccount`
- `UserSecurityEvent` where signup/linkage security evidence is required
- proposed Identity User-provisioned domain event

### Public Interfaces

Introduce or complete:

- `resolveAuthenticatedActor` (SH-001)
- `provisionUserAfterAgeGate`
- internal/provider-facing authentication/session port
- minimal safe local User lookup needed by SH-001
- optional `identity.user.provisioned.v1` event contract

Public contracts must return DTOs, not writable Prisma records.

### Shared Operations Used

**SH-044 — `executeIdempotentCommand`**  
Owner: platform application infrastructure.  
Invocation: wrap semantic User provisioning.  
Local policy: idempotency key must represent the provider identity + provisioning intent and reject same-key/different-payload conflicts.  
Prohibited duplicate: `identityIdempotency.ts`, custom provisioning-dedupe table unless the canonical implementation explicitly requires an owner record.

**SH-076 — `normalizeAndHashIdentifier`**  
Owner: shared security/cryptography capability.  
Invocation: approved IP/device identifiers and similar privacy-minimized matching keys.  
Local policy: which identifier is appropriate and normalization purpose.  
Prohibited duplicate: `ipHash.ts`, `deviceHash.ts`, local hashing algorithm.

**SH-046 — `publishDomainEvent`**  
Owner: platform outbox infrastructure.  
Invocation: same transaction as User provisioning when a real downstream consumer requires the event.  
Local policy: Identity event name/version/minimized payload.  
Prohibited duplicate: Identity event bus/private outbox.

**SH-032 / SH-033 / SH-034 — request context, structured logging, telemetry sanitization**  
Owner: platform/Observability.  
Invocation: request/provider/provisioning path.  
Local policy: safe Identity dimensions.  
Prohibited duplicate: local logger/request-context/redaction framework.

### Domain Logic

1. Validate age declaration and jurisdiction/region input.
2. Normalize privacy-minimized cooldown identifiers.
3. Check active age-gate block before provisioning.
4. Apply current Identity age/region policy.
5. Persist the attempt.
6. If blocked, persist an approved time-bound block and terminate before User creation.
7. If allowed, consume only verified provider/session evidence.
8. Normalize the provider subject into the Identity provider contract.
9. Resolve or idempotently create the local User according to the approved mapping policy.
10. Create baseline security profile/provider account in the same authoritative provisioning flow.
11. Append Identity security history where required.
12. Publish only the minimal User-provisioned fact if a downstream owner has a versioned consumer.
13. Return a safe actor/provisioning result.

The Module must not infer account merge solely from matching email until U-IA-03 is settled.

### Authorization / Compliance

- Age gate and initial auth entry are anonymous by design.
- Protected actor resolution trusts provider/server evidence only.
- COPPA-style/pre-account gate precedes User creation where active.
- Do not store full DOB unless a separate approved legal decision requires it.
- No raw password or provider secret in Workin Ants persistence.
- Do not expose whether a different User exists through error details.

### Database / Transaction Behavior

Provisioning should use one transaction boundary for local authoritative state:

```text
claim semantic command
→ validate no conflicting provider mapping
→ create/find User
→ create baseline UserSecurityProfile
→ create/link AuthProviderAccount
→ append required UserSecurityEvent
→ write outbox event if required
→ commit
```

Required constraints/reviews:

- enforce or safely emulate canonical provider identity uniqueness once U-IA-01/U-IA-03 are resolved;
- `AgeGateBlock` must have at least one usable matching identifier before production enforcement under PR-IA-04;
- preserve existing unique email/handle semantics without treating email as the account-linking authority.

### Events / Jobs

Potential event: `identity.user.provisioned.v1`.

No background job is required for the primary happy path.

If age-gate blocks are physically cleaned up, use the shared scheduler/queue rather than making cleanup a prerequisite for enforcement; expiry can be evaluated from `blockedUntil`.

### Provider Integration

Implement `AuthenticationSessionPort` plus a Supabase Auth adapter (or approved auth provider adapter).

The adapter returns:

- normalized provider subject;
- provider type;
- verified email facts if supplied/trusted;
- session/authentication assurance facts allowed by contract;
- no raw token in domain DTO.

OAuth signup remains disabled or routed through the approved age-gate sequence until U-IA-02 is resolved.

### UI / Admin Surface

Where an account shell already exists:

- age-gate/signup entry;
- sign-in;
- safe account identity display;
- development-only actor-context inspection if root standards permit.

Do not add buyer/profile/business UI.

### Failure Behavior

- malformed declaration → `invalid_input`;
- active age cooldown → `age_ineligible` or `blocked` with safe reason;
- underage/region denied → no User;
- provider session invalid → `unauthenticated`;
- provider unavailable → `provider_unavailable`, no partial User-authenticated state;
- equivalent duplicate provisioning → existing semantic result;
- conflicting provider identity → `conflict` / `manual_review`, no automatic merge;
- transaction/outbox failure before commit → no partial authoritative provisioning.

### Tests

- age policy unit matrix;
- block/cooldown tests;
- no-User-on-block integration test;
- actor resolver contract tests;
- invalid/expired provider session tests;
- duplicate provisioning/idempotency tests;
- provider normalization tests;
- provider identity conflict tests;
- `AgeGateBlock` identifier invariant tests;
- telemetry redaction tests;
- migration/constraint test;
- E2E eligible signup → authenticated actor;
- E2E blocked signup → no local User.

### Documentation Updates

- update `module-architecture.md` if U-IA-01/U-IA-02/U-IA-03/U-IA-17 is resolved;
- document SH-001 DTO/version;
- update progress tracker;
- document any schema constraint migration;
- record provider adapter configuration in approved provider documentation.

### Acceptance Criteria

- blocked age-gate path cannot create a User;
- eligible path creates one User under replay;
- SH-001 resolves one local actor for a valid session;
- client User ID/role claims are ignored as identity authority;
- no raw password/provider secret appears in schema/log/event fixtures;
- provider conflict cannot silently merge Users;
- migrations/tests pass from a clean database.

### Exit Gate

Pass before Feature 02:

- typecheck/lint/unit/integration/build pass;
- eligible provisioning and blocked-signup E2E pass;
- replay creates no duplicate User/security profile/provider link;
- SH-001 contract is versioned/documented;
- no local current-user/session duplicate exists;
- unresolved mapping/OAuth decisions are either approved or the relevant production path remains disabled.

---

## 02 Authentication Provider Linkage and Security Posture

### Objective

Allow a User to safely link, inspect, disable/revoke, and evaluate authentication methods without confusing provider metadata or security-profile summary fields with permission or assurance truth.

### Observable Result

- An authenticated User can list linked auth methods through a safe DTO.
- An approved additional provider identity can be linked idempotently.
- A provider method can be revoked without creating an unusable account when Identity policy requires a viable fallback.
- Security posture can be queried without exposing secrets.
- Login readiness can distinguish ready, locally locked, recovery-required, provider-unavailable, and other safe states.
- `passkeysEnabled`, `smsMfaEnabled`, or `lastStepUpAt` are not treated as independent proof.

### Cluster Build-Plan Link

Supports the provider/security foundation of **CL-01 Feature 01** and prepares **CL-01 Feature 03 — Authentication Methods, Passkeys, and Security Posture** and **CL-01 Feature 04 — Sensitive-Action Step-Up and Temporary Security Sessions**.

### Dependencies

- Feature 01 exit gate;
- `AuthProviderAccount`, `AuthCredentialStatus`, `UserSecurityProfile`, `UserSecurityTier`, `UserSecurityEvent`;
- SH-002 authorization;
- SH-044 idempotency;
- SH-064 external-provider connection authorization pattern;
- SH-051 aggregate locking;
- Audit/Notification/Ops contracts;
- U-IA-03 before broad automatic multi-provider linking/merge;
- U-IA-11 before enabling automated security-tier transitions;
- U-IA-15 before implementing backup-password behavior.

### In Scope

- `listAuthenticationMethods`;
- `getUserSecurityPosture`;
- `evaluateLoginReadiness`;
- `linkAuthProviderAccount`;
- `revokeAuthProviderAccount`;
- `markAuthCredentialCompromised` command boundary;
- local security-lock read/apply/release primitives where already supported by approved policy;
- provider-neutral OAuth/account link adapter boundary;
- safe security-event/audit/notification effects;
- summary-field maintenance rules.

### Out of Scope

- passkey/WebAuthn ceremony itself;
- OTP/step-up challenge;
- account recovery;
- general organization/resource authorization;
- provider auto-merge/canonical-email logic;
- automatic UserSecurityTier transitions not approved by architecture;
- backup-password implementation until U-IA-15 is resolved.

### Module-Owned Data

- `AuthProviderAccount`
- `AuthCredentialStatus`
- `UserSecurityProfile`
- `UserSecurityTier`
- `UserSecurityEvent`
- existing User association

### Public Interfaces

- `listAuthenticationMethods`
- `getUserSecurityPosture`
- `evaluateLoginReadiness`
- `linkAuthProviderAccount`
- `revokeAuthProviderAccount`
- restricted `markAuthCredentialCompromised`
- provider-account safe lookup required by SH-001

### Shared Operations Used

**SH-002 — `authorizeResourceAction`**  
Owner: Role / Authority.  
Invocation: link/revoke/view another User/admin security actions.  
Local policy: Identity supplies target User/credential facts and requested action.  
Prohibited duplicate: Identity `isAdmin`, `canManageSecurity`, local permission matrix.

**SH-044 — `executeIdempotentCommand`**  
Invocation: provider link/revoke/compromise mutations.  
Local policy: semantic key includes User/provider identity/action.  
Prohibited duplicate: local command-deduper.

**SH-064 — `authorizeExternalProviderConnection`**  
Owner: provider-owning Module pattern; here Identity.  
Invocation: before completing external auth-method link.  
Local policy: Identity account-linking constraints.  
Prohibited duplicate: provider-specific permission policy embedded in each adapter.

**SH-051 — `acquireAggregateLock`**  
Owner: shared persistence.  
Invocation: provider-link uniqueness, last-viable-method changes.  
Local policy: lock User/provider identity aggregate.  
Prohibited duplicate: in-memory mutex.

**SH-029 / SH-041**  
Owners: Audit / Notification.  
Invocation: material admin/security method changes and security notices.  
Local policy: which changes are material/notify.  
Prohibited duplicate: local audit ledger or generic sender.

### Domain Logic

- Active provider/credential records are authoritative for linked method state.
- Security profile booleans are summaries only.
- Provider link requires proof that the provider account being linked is under the subject’s control.
- The same canonical provider identity must not be linked to two Users.
- Matching email is not enough to merge accounts.
- Revoking a method must evaluate whether an approved viable login/recovery path remains.
- Compromised credentials become unusable immediately and may trigger local security lock/session revocation hooks according to approved policy.
- `UserSecurityTier` changes only through explicit approved policy.
- Provider unknown status maps to safe unavailable/review, never `active` by default.

### Authorization / Compliance

- self-service method management requires self authority through SH-002;
- admin/support mutation requires explicit Role / Authority decision;
- high-impact revoke/compromise/settings changes may require SH-014 after U-IA-18 matrix approval;
- sensitive method metadata is never public;
- notification subscription/device state is not an authentication method.

### Database / Transaction Behavior

- link: lock/claim provider identity → validate no conflicting User → create/link account → update summaries → append security event/audit/outbox as required;
- revoke: lock User/security aggregate → validate viability → transition status/revokedAt → update summaries → event/audit;
- use existing credential status enum; do not add one-off booleans;
- provider identity uniqueness migration requires architecture approval under U-IA-03/PR-IA-05.

### Events / Jobs

Potential minimized events:

- `identity.auth_provider.linked.v1`
- `identity.auth_provider.revoked.v1`
- `identity.auth_credential.compromised.v1`

Provider-state reconciliation is deferred to hardening unless needed earlier by the selected provider.

### Provider Integration

Extend the authentication/OAuth adapter contract to:

- normalize canonical provider subject/account identity;
- separate verified provider evidence from local status;
- expose revoke/disconnect operation if provider supports/needs it;
- hide SDK-specific types.

### UI / Admin Surface

Account security surface may show:

- provider/method type;
- safe device/name metadata;
- status;
- linked/last-used/revoked timestamps;
- “link” / “revoke” actions as authorized.

Do not display raw provider IDs where unnecessary.

### Failure Behavior

- provider identity already belongs to another User → conflict/manual review;
- provider unavailable → no partial link/revoke;
- last viable method removal disallowed → denial with safe reason;
- stale credential status → conflict/idempotent replay;
- unknown provider state → unavailable/review;
- Role service unavailable for required protected mutation → fail closed.

### Tests

- list-method redaction tests;
- provider-link ownership/authorization tests;
- duplicate provider-link/idempotency tests;
- conflicting User mapping test;
- last viable method policy unit tests;
- revoke replay tests;
- compromised credential tests;
- security-summary derivation tests;
- unknown provider status tests;
- RLS/security table access tests;
- audit/notification contract tests.

### Documentation Updates

- resolve/update U-IA-03/U-IA-11/U-IA-15/U-IA-16 as decisions are approved;
- publish safe authentication-method DTO contract;
- document provider identity uniqueness constraints;
- update progress tracker.

### Acceptance Criteria

- methods can be listed without secret leakage;
- duplicate equivalent link cannot duplicate provider account;
- conflicting provider ownership never auto-merges;
- revoked/compromised credentials cannot be treated active;
- summaries do not become source truth;
- protected mutations use SH-002;
- no provider SDK type crosses public boundary.

### Exit Gate

- full Feature 02 tests pass;
- provider link/revoke/compromise flows are idempotent and transaction-safe;
- no automatic account merge is enabled without approved policy;
- no ad hoc authorization helper exists;
- clean build passes.

---

# Phase 2 — Strong Authentication and Action-Scoped Assurance

## 03 Passkey Enrollment, Credential Lifecycle, and Fallback

### Objective

Implement passkey/WebAuthn enrollment and revocation as Identity-owned credential metadata while preserving provider/browser ceremony isolation, strong uniqueness, and safe fallback behavior.

### Observable Result

- An authenticated User can begin and complete passkey registration.
- A successful ceremony creates one `PasskeyCredential`.
- Replayed completion does not create a duplicate credential.
- A passkey can be revoked under approved authority.
- Failed passkey attempts update safe metadata and trigger approved fallback behavior rather than permanent accidental lockout.
- No biometric material is persisted.

### Cluster Build-Plan Link

Implements the passkey portion of **CL-01 Feature 03 — Authentication Methods, Passkeys, and Security Posture**.

### Dependencies

- Features 01–02;
- `PasskeyCredential`, `AuthCredentialStatus`, `UserSecurityProfile`, `UserSecurityEvent`;
- WebAuthn/passkey port;
- SH-002, SH-044, SH-051, SH-053;
- canonical hashing where credential IDs are stored hashed;
- Audit/Notification contracts.

### In Scope

- provider-neutral `PasskeyPort`;
- begin-registration operation;
- complete-registration operation;
- credential metadata persistence;
- credential status/revocation;
- safe last-used/failure-count updates;
- security-profile passkey summary maintenance;
- fallback decision plumbing;
- security events, generic audit where required, notification intent.

### Out of Scope

- general step-up policy/`SensitiveActionSession` issuance;
- recovery lifecycle;
- raw biometric capture/storage;
- business authorization;
- backup-password behavior unresolved by U-IA-15;
- passkey cross-device UX beyond provider-supported contract.

### Module-Owned Data

- `PasskeyCredential`
- `AuthCredentialStatus`
- `UserSecurityProfile` summaries
- `UserSecurityEvent`

### Public Interfaces

- `beginPasskeyRegistration`
- `completePasskeyRegistration`
- `revokePasskeyCredential`
- passkey summary returned through `listAuthenticationMethods`
- internal/provider port for passkey verification

### Shared Operations Used

**SH-002 — `authorizeResourceAction`**  
Invocation: self/admin passkey add/revoke.  
Local policy: target credential/user facts.  
Prohibited duplicate: passkey-specific admin permission engine.

**SH-044 — `executeIdempotentCommand`**  
Invocation: registration completion/revocation.  
Local policy: User + challenge/credential semantic key.  
Prohibited duplicate: passkey completion dedupe table unless canonical pattern requires owner data.

**SH-051 / SH-053 — aggregate locking and lifecycle-transition mechanism**  
Invocation: registration/revoke/use-vs-revoke races.  
Local policy: AuthCredentialStatus transition rules.  
Prohibited duplicate: in-memory credential lock or generic state machine owning policy.

**SH-072 / SH-076 — canonical hash primitives**  
Invocation: credential identifier hash/reference where required.  
Local policy: exact canonical credential representation.  
Prohibited duplicate: custom hash helper.

**SH-029 / SH-041 — Audit / Notification**  
Invocation: material registration/revocation/security alerts.  
Local policy: trigger classification and safe variables.  
Prohibited duplicate: generic security mailer/audit ledger.

### Domain Logic

- Persist only passkey metadata/reference necessary for Identity.
- `credentialIdHash` is unique and is the duplicate-registration guard in the current schema.
- Registration must be bound to the initiating User/challenge.
- An already-registered matching credential returns the existing semantic result or conflict, never a duplicate row.
- Revoked/compromised credentials cannot be used as active proof.
- Reactivation of revoked/compromised credentials is disabled until U-IA-16 is resolved; a new credential is preferred.
- Failure count is evidence, not an automatic permanent account lock.
- Fallback may route to another approved method or recovery according to policy.

### Authorization / Compliance

- self-service add/revoke requires SH-002;
- high-risk revoke/security settings may require SH-014 after matrix approval;
- no raw biometric;
- no raw WebAuthn/provider secret;
- credential metadata visible only to authorized subject/admin;
- generic Notification delivery is external.

### Database / Transaction Behavior

Registration completion transaction:

```text
validate ceremony result
→ claim idempotency key
→ lock User/security aggregate as needed
→ assert credential hash uniqueness
→ create PasskeyCredential
→ update security-profile summary
→ append UserSecurityEvent
→ outbox/audit request where required
→ commit
```

Revoke transaction conditionally updates an active credential and summary.

### Events / Jobs

Potential:

- `identity.passkey.registered.v1`
- `identity.passkey.revoked.v1`

No mandatory scheduled job unless provider/credential expiry policy is later introduced.

### Provider Integration

`PasskeyPort` must isolate:

- registration challenge/options;
- ceremony result verification;
- authentication assertion verification when used for SH-014;
- provider/browser-specific error translation.

Adapter tests must use known WebAuthn fixtures and negative proof cases.

### UI / Admin Surface

Security settings may expose:

- “Add passkey”;
- safe credential/device label;
- registration date/last used;
- status;
- revoke action;
- fallback instructions when unavailable.

No biometric UI/data belongs in server persistence.

### Failure Behavior

- invalid/mismatched ceremony → `challenge_invalid`;
- duplicate existing credential → same semantic result or conflict;
- credential owned by another User → conflict/manual review;
- provider/browser unsupported → safe unavailable;
- provider/WebAuthn error → no credential row;
- stale revoke/use race → conditional conflict;
- repeated failures → approved fallback, not permanent auto-lock.

### Tests

- passkey port fixtures;
- registration binding tests;
- unique credential hash tests;
- idempotent completion tests;
- revoke lifecycle tests;
- use-vs-revoke race tests;
- summary update/rebuild tests;
- fallback policy tests;
- no raw biometric/provider-secret schema/log tests;
- authorization tests;
- E2E add/revoke passkey where runtime permits.

### Documentation Updates

- record any credential-field/security decision;
- update U-IA-16 if reactivation is approved;
- publish PasskeyPort contract;
- update progress tracker.

### Acceptance Criteria

- one verified ceremony produces one active credential;
- replay creates no duplicate;
- revoked credential cannot be accepted;
- summaries agree with authoritative credential records;
- no biometric/secret leakage;
- fallback is deterministic and test-covered.

### Exit Gate

- provider/domain/integration tests pass;
- unique/idempotency behavior is proven;
- no raw biometric material appears in storage/log fixtures;
- no passkey code directly grants downstream resource permission;
- build passes.

---

## 04 Step-Up Challenge and SensitiveActionSession

### Objective

Make SH-014 the canonical action-scoped assurance path: sensitive-action consumers can receive `step_up_required`, complete an approved passkey/OTP challenge, and obtain a short-lived `SensitiveActionSession` valid only for the intended actor/action/target.

### Observable Result

- A protected test consumer gets `step_up_required` when it lacks sufficient assurance.
- Passkey or approved OTP can verify a pending challenge.
- Verification creates a scoped assurance grant.
- Wrong actor/action/target, expired, or revoked grants are denied.
- Duplicate verification does not create uncontrolled duplicate grants/effects.
- Provider failure never creates assurance.
- Challenge expiration/attempt exhaustion is observable.

### Cluster Build-Plan Link

Implements the assurance portion of **CL-01 Feature 04 — Sensitive-Action Step-Up and Temporary Security Sessions**.

### Dependencies

- Features 01–03;
- `StepUpActionType`, `StepUpChallengeType`, `StepUpChallengeStatus`, `StepUpFailureReason`;
- `StepUpChallenge`, `SensitiveActionSession`, `UserSecurityProfile`, `UserSecurityEvent`;
- passkey port;
- OTP provider port;
- SH-014, SH-015, SH-044, SH-051, SH-053, SH-055, SH-088/089;
- canonical crypto/token primitives as needed;
- rate-limit infrastructure;
- U-IA-05, U-IA-06, U-IA-07 for production behavior beyond the safe current subset.

### In Scope

- SH-014 public contract;
- evaluate existing assurance;
- create step-up challenge;
- select approved challenge method;
- verify passkey challenge;
- verify OTP/provider challenge;
- attempt limit/expiry;
- failure reasons;
- grant `SensitiveActionSession`;
- validate grant;
- revoke grant;
- challenge-expiration job where physical transition is needed;
- security event/audit/notification integration.

### Out of Scope

- downstream resource permission/business logic;
- account recovery;
- creating new business access grants;
- frontend-only MFA booleans;
- arbitrary new `StepUpActionType` values without architecture approval;
- plaintext/local OTP storage.

### Module-Owned Data

- `StepUpChallenge`
- `StepUpChallengeStatus`
- `StepUpFailureReason`
- `SensitiveActionSession`
- `UserSecurityProfile` summary timestamps only
- `UserSecurityEvent`

### Public Interfaces

- SH-014 `requireStepUpForSensitiveAction`
- internal/controlled `createStepUpChallenge`
- `verifyStepUpChallenge`
- `cancelStepUpChallenge`
- `validateSensitiveActionAssurance`
- `revokeSensitiveActionSession`
- provider-neutral `OtpVerificationPort`
- passkey authentication assertion path

### Shared Operations Used

**SH-014 — `requireStepUpForSensitiveAction`**  
Owner: Identity & Access.  
Invocation: downstream owner after authorization and before sensitive mutation.  
Local policy: challenge method, TTL, attempts, fallback, grant scope.  
Prohibited duplicate: `mfaGuard.ts`, `requireOtp.ts`, `lastMfaAt` checks in consumers.

**SH-015 — `returnDecisionResult`**  
Owner: shared contract / policy varies.  
Invocation: stable assurance decision envelope.  
Local policy: Identity reason codes/next action.  
Prohibited duplicate: custom decision envelopes per consumer.

**SH-044 — `executeIdempotentCommand`**  
Invocation: challenge creation/verification/revocation.  
Local policy: semantic challenge verification key.  
Prohibited duplicate: challenge-specific generic idempotency store.

**SH-051 / SH-053 — lock and lifecycle transition**  
Invocation: verify/cancel/expire races.  
Local policy: Identity transition matrix.  
Prohibited duplicate: in-memory challenge mutex/generic state owner.

**SH-055 — `runDeadlineExpiration`**  
Invocation: pending challenge expiration.  
Local policy: expiry deadline/status/event semantics.  
Prohibited duplicate: local cron framework.

**SH-088 / SH-089 — temporary grant mechanics**  
Invocation: issue/revoke SensitiveActionSession.  
Local policy: Identity assurance meaning.  
Prohibited duplicate: one universal AccessGrant lifecycle.

**SH-029 / SH-041**  
Invocation: material security audit/notification.  
Local policy: trigger classification.  
Prohibited duplicate: local generic audit/notifier.

### Domain Logic

- Authorization happens before step-up; SH-014 does not grant permission.
- Current supported sensitive action values are bounded by the approved `StepUpActionType`.
- Unknown action fails closed until U-IA-05 is resolved.
- A challenge records actor, action, optional target, challenge type, attempts/max attempts, status, expiry.
- Only `pending` may verify.
- Current SMS OTP policy expires after five minutes unless architecture changes.
- Plaintext OTP is never persisted.
- While U-IA-06 is unresolved, provider-managed OTP challenge state is preferred over adding new local secret storage semantics.
- Successful proof transitions challenge to `verified` and issues the scoped `SensitiveActionSession` transactionally/idempotently.
- Every grant validation checks actor/action/target/expiry/revocation.
- `lastStepUpAt` is updated only as summary/history and never replaces the grant.
- Replayed verification returns original/already-completed result.
- Repeated passkey failure can fall back to approved alternative.
- While U-IA-07 is unresolved, the system must not allow ambiguous competing same-scope challenges to both create effects; serialize or return conflict rather than silently pick a winner.

### Authorization / Compliance

- challenge creation requires authenticated actor and a legitimate sensitive-action request;
- the downstream owner still supplies resource authorization;
- admin/manual challenge modes require explicit Role authorization;
- no sensitive financial action may trust frontend-only MFA;
- no notification delivery constitutes successful verification;
- rate limiting/abuse controls are mandatory.

### Database / Transaction Behavior

Verification transaction:

```text
claim idempotency key
→ lock StepUpChallenge
→ assert pending + unexpired + attempts remain + actor/action/target match
→ apply normalized proof
→ transition verified OR increment/fail/lock
→ on verified create SensitiveActionSession
→ update safe summaries
→ append UserSecurityEvent
→ outbox/audit/notification requests as required
→ commit
```

Expiration is conditional on still-pending state.

### Events / Jobs

- optional `identity.step_up.verified.v1`
- optional `identity.sensitive_action_session.revoked.v1`
- challenge-expiration jobs via SH-055/047 where needed
- queue telemetry through platform Ops

### Provider Integration

- passkey authentication assertion through PasskeyPort;
- OTP through `OtpVerificationPort` (Twilio Verify/equivalent);
- translate provider errors into `invalid`, `expired`, `locked`, `provider_unavailable`, not raw provider error contracts.

### UI / Admin Surface

- step-up prompt;
- method selection only from server-approved methods;
- OTP/passkey continuation;
- safe retry/expiry/locked/fallback states;
- no UI “MFA complete” boolean trusted by the server.

### Failure Behavior

- invalid code/assertion → failure reason/attempt increment;
- expired challenge → `challenge_expired`;
- max attempts → `challenge_locked`;
- wrong actor/action/target → denied;
- provider outage → unavailable, no grant;
- replay → existing semantic result;
- stale verify vs expire/cancel → conditional conflict;
- unknown sensitive action → fail closed;
- grant expired/revoked → `assurance_expired`.

### Tests

- transition matrix unit tests;
- OTP TTL/max-attempt tests;
- passkey step-up tests;
- wrong actor/action/target tests;
- grant expiry/revocation tests;
- verification replay/idempotency tests;
- verify-vs-expire/cancel concurrency tests;
- simultaneous challenge policy tests for approved safe behavior;
- provider outage/unknown result tests;
- notification-not-proof negative test;
- no plaintext OTP/raw secret tests;
- E2E `step_up_required → verified → scoped action succeeds`.

### Documentation Updates

- update U-IA-05/U-IA-06/U-IA-07/U-IA-18 if resolved;
- publish SH-014 DTO/reason codes;
- document OTP/provider configuration;
- update progress tracker.

### Acceptance Criteria

- SH-014 is the only supported cross-Module step-up contract;
- no consumer must read `lastStepUpAt`;
- verified proof is action/target-scoped;
- expired/revoked/wrong-scope grants always deny;
- provider outage never creates a grant;
- all challenge transitions are explicit/tested.

### Exit Gate

- passkey and OTP assurance contract tests pass;
- sensitive-action E2E passes;
- wrong-scope/expired/revoked negative tests pass;
- no local feature MFA helper is required;
- unresolved action/secret/concurrency behavior is explicitly gated;
- clean build passes.

---

# Phase 3 — Account Recovery

## 05 Recovery Initiation and Email Proof

### Objective

Create the first half of the Identity-owned account-recovery workflow: initiate recovery without account enumeration, issue a short-lived recovery email proof through approved delivery, verify that proof idempotently, and expose a safe recovery status.

### Observable Result

- A subject can initiate recovery through a non-enumerating public entry point.
- A recovery request can progress from `initiated` / `email_sent` to `email_verified`.
- Recovery email proof expires after the current fifteen-minute policy window.
- Token replay cannot repeat lifecycle effects.
- A second ambiguous recovery request cannot silently compete with an existing active request.
- Recovery status can be queried safely.

### Cluster Build-Plan Link

Implements the initiation/email-proof portion of **CL-01 Feature 05 — Changed-Phone Account Recovery and Security Event Integrity**.

### Dependencies

- Features 01–04;
- `AccountRecoveryRequest`, recovery enums, `UserSecurityEvent`;
- SH-074 secure token generation;
- SH-072 hashing;
- SH-076 identifier hashing as needed;
- SH-044 idempotency;
- SH-049 workflow mechanics;
- SH-053 lifecycle transitions;
- SH-041 Notification;
- SH-055 expiration;
- abuse/rate-limit infrastructure;
- U-IA-08 for final multiple-active-request policy.

### In Scope

- `initiateAccountRecovery`;
- recovery-account resolution without enumeration leakage;
- recovery request persistence;
- secure email token generation/hash persistence;
- Notification request for secure recovery link;
- `verifyRecoveryEmailToken`;
- status query;
- cancellation and expiration for the initiation/email stage;
- safe failure reasons;
- recovery security events.

### Out of Scope

- external identity-verification provider;
- phone replacement;
- session revocation;
- manual-review completion;
- payout KYC or trust verification;
- direct generic email sending;
- automatic second-request supersede policy not approved by U-IA-08.

### Module-Owned Data

- `AccountRecoveryRequest`
- `AccountRecoveryStatus`
- `AccountRecoveryReason`
- `UserSecurityEvent`

### Public Interfaces

- `initiateAccountRecovery`
- `verifyRecoveryEmailToken`
- `getAccountRecoveryStatus`
- `cancelAccountRecovery`
- controlled expiration operation

### Shared Operations Used

**SH-074 — `generateSecureToken`**  
Owner: shared security capability.  
Invocation: recovery email bearer proof.  
Local policy: purpose, current 15-minute TTL, one-time semantics.  
Prohibited duplicate: `recoveryToken.ts` random generator.

**SH-072 — `hashCanonicalPayload`**  
Invocation: store/compare token proof without plaintext.  
Local policy: token purpose/version.  
Prohibited duplicate: custom token hash.

**SH-044 — `executeIdempotentCommand`**  
Invocation: initiation/token verification/cancellation.  
Local policy: recovery semantic key.  
Prohibited duplicate: local retry ledger.

**SH-049 / SH-053 — workflow/transition mechanics**  
Invocation: advance recovery through approved states.  
Local policy: Identity recovery state machine.  
Prohibited duplicate: generic saga owning recovery.

**SH-041 — `requestNotification`**  
Owner: Notification.  
Invocation: send recovery email intent.  
Local policy: recipient/intent/safe variables and secure link/token handling.  
Prohibited duplicate: generic email sender.

**SH-055 — `runDeadlineExpiration`**  
Invocation: expiration deadline.  
Local policy: which statuses can expire.  
Prohibited duplicate: local scheduler.

### Domain Logic

- Recovery entry point should not reveal whether an account exists beyond approved UX.
- The recovery request represents Workin Ants recovery truth.
- Token is high-entropy, single-purpose, short-lived; plaintext is not stored.
- Current evidence specifies fifteen-minute recovery email token expiry.
- Verification can only apply to the matching nonterminal request.
- Replay after successful verification returns `already_verified`/same semantic result.
- Failed token attempts are rate-limited.
- While U-IA-08 is unresolved, the safe interim behavior is to prevent ambiguous parallel completion: a conflicting active recovery may return a generic “recovery already in progress”/no-op rather than creating a second independently completable workflow.
- Recovery provider/KYC proof is not involved yet.

### Authorization / Compliance

- initiation may be anonymous;
- authenticated recovery initiation may still use normal actor context;
- support/admin initiation requires SH-002 when enabled;
- avoid account/email enumeration;
- secure link content/logging must not expose token;
- Notification delivery status is not recovery proof.

### Database / Transaction Behavior

Initiation:

```text
resolve subject safely
→ claim semantic command / check active-recovery conflict
→ create AccountRecoveryRequest
→ generate/store token hash + expiry
→ append security event
→ write notification/outbox intent
→ commit
```

Token verification:

```text
claim idempotency
→ lock recovery request
→ assert correct state + unexpired
→ compare approved token hash
→ transition email_verified
→ clear/invalidate reusable proof as policy allows
→ append event
→ commit
```

### Events / Jobs

- optional recovery initiated/email verified domain event only if a real consumer exists;
- expiration worker via SH-055/047 if physical expiry transition is required;
- generic notification delivery handled externally.

### Provider Integration

No external identity-verification provider in this feature. Notification is the delivery rail.

### UI / Admin Surface

- recovery initiation;
- generic “check your email” response;
- email-link verification result;
- recovery status;
- expired/failed/cancelled states;
- no raw evidence/admin internals.

### Failure Behavior

- unknown account identifier → same safe initiation UX as known account where anti-enumeration policy requires;
- invalid token → safe invalid result;
- expired token → `recovery_pending`/expired status according to lifecycle;
- duplicate verification → same semantic result;
- Notification unavailable → request remains in valid retry/pending state according to transactional/outbox design; never falsely `email_verified`;
- conflicting active recovery → safe conflict/no duplicate workflow;
- abuse threshold exceeded → rate limited.

### Tests

- anti-enumeration response tests;
- token entropy/hash fixture tests;
- no plaintext token persistence/log tests;
- 15-minute expiry tests;
- transition tests;
- replay/idempotency tests;
- active recovery conflict tests;
- Notification failure/outbox tests;
- rate-limit behavior tests;
- E2E initiation → email proof → `email_verified`.

### Documentation Updates

- update U-IA-08 if final concurrency policy approved;
- document recovery token contract/TTL;
- update progress tracker;
- document Notification intent.

### Acceptance Criteria

- initiation does not expose account existence beyond approved policy;
- token plaintext is absent from persistence/logs;
- token expires per policy;
- replay does not duplicate effects;
- recovery cannot skip directly to external verification/phone replacement;
- competing recovery requests cannot both silently progress to completion.

### Exit Gate

- recovery initiation/email-proof E2E passes;
- anti-enumeration/token-security tests pass;
- no parallel ambiguous workflow is possible in the enabled path;
- build passes.

---

## 06 Recovery Identity Verification, Phone Replacement, and Session-Safety Hook

### Objective

Complete the approved recovery path by treating an external identity-verification provider only as evidence, applying provider results through verified/deduplicated adapters, and changing protected phone/access state only through the Identity transition service and approved session-safety policy.

### Observable Result

When architecture gates are resolved for the enabled path:

- `email_verified` recovery can request identity verification;
- normalized provider result advances to `identity_verified` or safe fail/review state;
- approved recovery moves to `phone_update_pending`;
- phone replacement occurs exactly once through Identity;
- recovery becomes `completed`;
- approved session-revocation hook runs;
- duplicate/out-of-order provider callbacks are harmless.

When a production gate remains unresolved, the implemented contract may safely stop at the last approved state and clearly report the blocker; it may not guess completion semantics.

### Cluster Build-Plan Link

Completes **CL-01 Feature 05 — Changed-Phone Account Recovery and Security Event Integrity**.

### Dependencies

- Feature 05;
- recovery identity-verification port;
- `AccountRecoveryRequest`, `UserSecurityProfile`, `UserSecurityEvent`;
- SH-059/060/061/062 provider mechanisms;
- SH-051/053 concurrency/transition;
- SH-075/076 encryption/hash;
- SH-029/041/037;
- optional SH-011/012 if approved risk/hold policy uses them;
- U-IA-04 session revocation matrix;
- U-IA-09 provider-event dedupe truth for callback-based production activation;
- U-IA-10 manual-review authority/evidence;
- U-IA-12 retention behavior.

### In Scope

- `RecoveryIdentityVerificationPort`;
- request/hand-off to configured provider;
- verified callback/poll entry point;
- provider signature verification;
- provider-event dedupe;
- provider status translation;
- recovery state transitions;
- safe manual-review routing;
- encrypted/hashed new-phone handling;
- phone replacement command;
- recovery completion;
- session-revocation port/hook;
- provider reconciliation;
- security/audit/notification/Ops effects.

### Out of Scope

- payout KYC;
- generic marketplace identity verification;
- storing provider identity documents in Identity;
- global session implementation outside the provider port;
- inventing provider-event schema or manual-review lifecycle without architecture approval;
- generic ComplianceHold lifecycle.

### Module-Owned Data

- `AccountRecoveryRequest`
- recovery enums/status
- `UserSecurityProfile`
- `UserSecurityEvent`
- provider-event dedupe truth only after U-IA-09 schema approval

### Public Interfaces

- request/start recovery identity verification;
- trusted `applyRecoveryIdentityVerification`;
- `completeAccountRecovery`;
- safe manual-review transition interface after U-IA-10 approval;
- `SessionRevocationPort`;
- `RecoveryIdentityVerificationPort`;
- `getAccountRecoveryStatus`.

### Shared Operations Used

**SH-059 — `verifyProviderWebhookSignature`**  
Owner: shared integration-security shell.  
Invocation: before callback parsing/side effects.  
Local policy: provider algorithm/config through adapter.  
Prohibited duplicate: recovery-specific generic signature framework.

**SH-060 — `deduplicateProviderEvent`**  
Owner: provider-owning Module using shared primitive.  
Invocation: after verified signature, before state change.  
Local policy: Identity owner-specific event receipt truth.  
Prohibited duplicate: ad hoc `webhookLog.ts`.

**SH-061 — `translateProviderStatus`**  
Owner: provider adapter.  
Invocation: provider result → Identity normalized verification result.  
Local policy: mapping to recovery states.  
Prohibited duplicate: provider status switch in domain service.

**SH-062 — `reconcileProviderState`**  
Invocation: missing/out-of-order callback/drift.  
Local policy: Identity expected state and safe repairs.  
Prohibited duplicate: one-off repair as source truth.

**SH-051 / SH-053 — locking/lifecycle transition**  
Invocation: provider callback and recovery completion.  
Local policy: recovery transition matrix.  
Prohibited duplicate: in-memory lock or provider-owned lifecycle.

**SH-075 / SH-076 — encryption/hash**  
Invocation: phone values.  
Local policy: recoverable vs comparable representation.  
Prohibited duplicate: local phone encryption/hash.

**SH-029 / SH-041 / SH-037**  
Invocation: material recovery audit, security notifications, provider failure telemetry.  
Local policy: safe trigger/reason data.  
Prohibited duplicate: local audit/notifier/Ops table.

### Domain Logic

- External verification success is necessary evidence only where configured; it never updates User/phone directly.
- Unknown provider status → explicit unsupported/manual review/unavailable.
- Callback is accepted only after signature verification/dedupe.
- Recovery transition must match current state and provider reference.
- Changed-phone flow requires approved verification chain.
- Phone value is stored only in approved encrypted/hash forms.
- `phone_update_pending` is the safe boundary before the actual mutation.
- Phone replacement and recovery completion must be one transaction or a controlled workflow that cannot report `completed` before authoritative phone/security state is committed.
- Session revocation behavior must follow U-IA-04; no global policy is invented here.
- Manual review requires U-IA-10 authority/evidence before it can approve completion.
- Duplicate provider result and duplicate completion command are idempotent.
- Provider reconciliation never changes to a success state on unknown evidence.

### Authorization / Compliance

- callback entry is provider-authenticated, not user-authenticated;
- manual review/admin completion uses SH-002 and SH-014 where approved;
- ComplianceHold is consulted only if named recovery policy requires it;
- identity documents remain provider-side unless separate architecture explicitly approves storage;
- no raw phone/provider payload in logs/audit/event;
- retention handled through Privacy policy.

### Database / Transaction Behavior

Provider callback:

```text
verify signature
→ claim provider event
→ lock recovery request
→ validate provider/request correlation
→ translate result
→ conditional transition
→ append security event
→ outbox/audit/notification as required
→ commit
```

Phone completion:

```text
claim idempotency
→ lock recovery + UserSecurityProfile
→ assert full proof chain / current state
→ encrypt/hash new phone
→ update profile
→ transition recovery completed
→ append security event
→ outbox/audit/notification
→ commit
→ invoke/reconcile session revocation according to approved consistency contract
```

If session revocation must be atomic with provider state but cannot be, document the approved outbox/workflow semantics before enabling completion.

### Events / Jobs

Potential:

- `identity.recovery.manual_review_required.v1`
- `identity.recovery.completed.v1`
- `identity.phone.changed.v1`

Jobs:

- provider reconciliation;
- recovery expiry;
- retry-safe session-revocation effect if architecture approves asynchronous execution.

### Provider Integration

Adapters for Stripe Identity / Persona / approved provider:

- begin verification;
- normalize status;
- verify callback;
- fetch/reconcile status;
- delete provider resource for Privacy where supported.

Production callback side effects remain disabled until U-IA-09 durable dedupe truth exists.

### UI / Admin Surface

- provider handoff/resume state;
- pending/review/failed/expired/cancelled/completed status;
- masked new-phone confirmation where appropriate;
- admin review surface only after authority/evidence contract is approved;
- no provider raw document view in Identity by default.

### Failure Behavior

- provider unavailable → remain valid pending/retryable state;
- invalid signature → reject with no business effect;
- duplicate callback → no-op/same result;
- out-of-order callback → ignore/reconcile/manual review according to current state;
- unknown provider result → manual review/unsupported, never success;
- conflicting recovery completion → stale conflict;
- phone encryption failure → no partial completion;
- session-revocation failure → follow approved consistency/retry contract; never pretend revocation occurred;
- unresolved U-IA-04/U-IA-09/U-IA-10 → production completion/callback/manual review path stays disabled at the relevant boundary.

### Tests

- provider signature fixtures;
- duplicate/out-of-order event tests;
- status translation fixtures;
- callback/reconciliation tests;
- recovery transition tests;
- phone encryption/hash tests;
- completion idempotency tests;
- completion-vs-cancel/expire concurrency tests;
- manual-review authority tests after approval;
- no payout-KYC dependency test;
- no provider-document persistence test;
- session-revocation hook contract tests;
- E2E successful recovery path when gates resolved;
- E2E provider failure/manual-review safe path.

### Documentation Updates

- U-IA-04/U-IA-09/U-IA-10/U-IA-12 must be updated when settled;
- provider adapter and webhook contract documentation;
- recovery state diagram if changed;
- progress tracker;
- operational runbook for reconciliation/manual review.

### Acceptance Criteria

- provider success cannot bypass Identity transition service;
- duplicate callbacks/completion cannot repeat phone changes;
- unknown provider status cannot complete recovery;
- phone values follow canonical crypto;
- payout KYC/marketplace verification are not used as recovery truth;
- session-safety behavior is explicit and testable for every enabled completion path.

### Exit Gate

For a **production-enabled** full recovery path:

- U-IA-04, U-IA-09, and any required U-IA-10 decision are resolved;
- verified/deduped/reconciled callback tests pass;
- successful and failure E2E pass;
- session-revocation contract is proven;
- build passes.

For a **safe scaffold-only** stage, exit may pass only if:

- unsupported completion/callback/manual-review behavior is mechanically disabled/fail-closed;
- the last enabled state and blocker are documented;
- no production route can bypass the blocker.

---

# Phase 4 — Structural Security Administration and Support-Rail Integration

## 07 Structural Platform Roles and Identity Security Administration

### Objective

Implement Identity-owned structural `UserRole` mutations and high-impact account-security administration while proving that Role / Authority remains the only permission interpreter.

### Observable Result

- An authorized administrator can attach/remove a `PlatformRole` through Identity commands.
- Unauthorized self/client role escalation is impossible through public mutation paths.
- Role / Authority can read structural role facts through a stable contract without owning the rows.
- Approved admin security-lock/unlock or credential actions use Role / Authority and step-up where required.
- Material changes produce Identity security history and generic audit separately.

### Cluster Build-Plan Link

Integrates Identity with **CL-01 Feature 02 — Resource Authorization Contract and RLS Parity**, and supports the high-risk administration requirements exercised in **CL-01 Feature 16**.

### Dependencies

- Features 01–06;
- `UserRole`, `PlatformRole`, `UserSecurityProfile`, `UserSecurityEvent`;
- SH-002 Role / Authority;
- SH-014 step-up for actions included in the approved matrix;
- SH-044/051 idempotency/locking;
- SH-029 Audit;
- RLS/server authorization policy foundation;
- U-IA-18 for exact high-risk step-up matrix.

### In Scope

- `listPlatformRoles`;
- `assignPlatformRole`;
- `removePlatformRole`;
- server-side target facts for Role / Authority;
- restricted `lockUserSecurityProfile` / `unlockUserSecurityProfile` if approved;
- approved admin credential compromise/revoke commands;
- generic audit + Identity security event separation;
- role-change integration event if a consumer needs it;
- RLS/server parity tests for Identity-owned tables/commands.

### Out of Scope

- permission interpretation;
- organization membership/roles;
- thread participants;
- business-resource ACLs;
- generic ComplianceHold;
- a second role/permission table;
- unresolved automatic security-tier policy.

### Module-Owned Data

- `UserRole`
- `PlatformRole`
- `UserSecurityProfile` local lock fields
- `UserSecurityEvent`

### Public Interfaces

- `listPlatformRoles`
- `assignPlatformRole`
- `removePlatformRole`
- safe Role / Authority structural-role facts DTO
- authorized local security-lock commands
- optional `identity.platform_role_changed.v1`

### Shared Operations Used

**SH-002 — `authorizeResourceAction`**  
Invocation: every privileged role/security admin mutation.  
Local policy: Identity target facts, not permission policy.  
Prohibited duplicate: `isAdmin`, `adminGuard`, local platform-role interpretation.

**SH-014 — `requireStepUpForSensitiveAction`**  
Invocation: approved high-risk admin/security actions.  
Local policy: Identity-sensitive action mapping after U-IA-18.  
Prohibited duplicate: admin-only MFA helper.

**SH-044 / SH-051**  
Invocation: role add/remove and lock state races.  
Local policy: User/role aggregate key.  
Prohibited duplicate: local lock/idempotency.

**SH-029 — `appendAuditEvent`**  
Invocation: material admin role/security changes.  
Local policy: safe action metadata.  
Prohibited duplicate: Identity generic admin audit table.

**SH-046 — `publishDomainEvent`**  
Invocation: role/security facts that real consumers need.  
Local policy: minimized event.  
Prohibited duplicate: direct consumer mutation.

### Domain Logic

- Identity structurally owns `(userId, PlatformRole)`.
- Role / Authority must approve add/remove.
- Composite uniqueness prevents duplicate role rows.
- Client role claims are ignored.
- Removing a role may trigger approved session-safety effects, but the exact session-revocation matrix is U-IA-04.
- Local security lock protects account/security access and does not become a generic business hold.
- Security-tier transitions are not inferred from role changes.
- Every material administrative security action appends the appropriate Identity security event and generic audit where policy requires.

### Authorization / Compliance

- only approved Role / Authority decisions permit role/security admin mutation;
- support role does not automatically imply admin authority;
- step-up requirements follow centrally approved matrix;
- Admin Review/ComplianceHold remains a separate owner;
- sensitive admin reads may require SH-030.

### Database / Transaction Behavior

- role add uses composite uniqueness + semantic idempotency;
- role remove is idempotent when absent;
- lock/unlock uses conditional current-state update;
- source mutation + security event/outbox should commit together where required;
- RLS must prevent direct unauthorized table mutation.

### Events / Jobs

Potential `identity.platform_role_changed.v1`, local lock/unlock events.

Session revocation effect is invoked only according to approved U-IA-04 policy and may use outbox/retry if the approved consistency model is asynchronous.

### Provider Integration

Session-revocation provider port may be exercised. No new auth provider lifecycle is introduced.

### UI / Admin Surface

A security/admin surface may show:

- safe User identity;
- structural platform roles;
- local security lock status/reason category;
- permitted admin actions.

It must not become a generic organization/business permission editor.

### Failure Behavior

- Role / Authority denial → no mutation;
- step-up missing → `step_up_required`;
- stale role/lock state → idempotent result/conflict;
- provider session-revoke failure → approved retry/operational state, not false claim;
- RLS/server disagreement → exit gate failure;
- unknown high-risk action classification → fail closed.

### Tests

- role add/remove idempotency;
- client role escalation negative tests;
- admin/support/self authorization matrix;
- SH-014 step-up tests for approved admin actions;
- RLS/server parity tests;
- role change concurrency tests;
- local security lock != ComplianceHold tests;
- audit/security-event separation tests;
- session-revocation hook tests if enabled.

### Documentation Updates

- update U-IA-04/U-IA-18 when settled;
- publish structural role facts contract;
- document RLS policy;
- update progress tracker.

### Acceptance Criteria

- no role row can be changed by unapproved actor;
- Role / Authority remains the permission interpreter;
- direct DB mutation is blocked by RLS/policy where applicable;
- generic audit and UserSecurityEvent both preserve their distinct purpose;
- no organization/thread permission truth appears in Identity.

### Exit Gate

- authorization/RLS parity suite passes;
- privilege escalation negative tests pass;
- high-risk enabled actions have approved step-up behavior;
- build passes.

---

## 08 Consent, Hold, Audit, Notification, and Operational Boundary Integration

### Objective

Prove that Identity can compose the platform’s cross-cutting support rails without duplicating them or allowing support records to become security truth.

### Observable Result

- A named Identity security workflow can require an exact Consent proof through Consent & Disclosure where architecture says it is required.
- A configured high-risk Identity action can be blocked by `ComplianceHold` without writing a local generic block flag.
- A material Identity action produces `UserSecurityEvent` and generic `AuditEvent` through separate contracts.
- A sensitive Identity read produces AccessAuditLog where policy requires it.
- Security/recovery notices are requested through Notification only.
- Provider failures appear in Ops without changing Identity lifecycle to a fake failure state.

### Cluster Build-Plan Link

Supports **CL-01 Feature 16 — Privacy, Holds, Audit, Notification, and Operational Support Bridges**. Privacy itself is implemented in Feature 09 below.

### Dependencies

- Features 01–07;
- Consent SH-008/009 where explicitly required;
- Hold SH-011/012;
- Audit SH-029/030;
- Notification SH-041;
- Observability SH-032–039;
- SH-046/047 for durable effects/jobs;
- U-IA-14 for exact security consent categories;
- U-IA-18 for step-up classifications where relevant.

### In Scope

- reusable Identity integration wrappers/ports for external owner contracts;
- one or more concrete Identity workflow integrations proving Consent/Hold/Audit/Notification/Ops composition;
- safe audit/access payload construction;
- notification intent construction;
- provider failure/retry observability;
- health checks for auth/OTP/recovery provider adapters;
- contract tests proving support records do not mutate/replace Identity truth.

### Out of Scope

- Consent version publication;
- generic Hold lifecycle;
- generic Audit/Access storage;
- Notification templates/delivery/provider callbacks;
- Ops incident/failure storage;
- Privacy orchestration;
- universal “canDoEverything” gate combining all systems.

### Module-Owned Data

No new support-rail truth.

Identity may write only its existing owner state/security events while invoking external interfaces.

### Public Interfaces

No new generic cross-cutting public service is required.

May add internal Identity integration ports for:

- consent proof requirement;
- hold decision composition;
- audit/access request construction;
- security notification intent;
- provider health/failure reporting.

### Shared Operations Used

**SH-008 / SH-009 — Consent proof/version**  
Owner: Consent & Disclosure.  
Invocation: only named Identity security flow with approved requirement.  
Local policy: whether that Identity action requires proof.  
Prohibited duplicate: local consent table/boolean/version constant.

**SH-011 / SH-012 — Hold evaluate/request**  
Owner: Admin Review / Compliance Hold.  
Invocation: approved high-risk/manual-review action.  
Local policy: Identity reason/target.  
Prohibited duplicate: `isBlocked`, generic lock-as-hold.

**SH-029 / SH-030 — Audit / sensitive access**  
Owner: Audit / Event Ledger.  
Invocation: material admin/security action and actual sensitive Identity read.  
Local policy: action/sensitivity/purpose.  
Prohibited duplicate: Identity AuditEvent/AccessAuditLog writer/storage.

**SH-041 — `requestNotification`**  
Owner: Notification.  
Invocation: security/recovery intent.  
Local policy: trigger, urgency, safe variables.  
Prohibited duplicate: generic email/SMS/push sender.

**SH-032–039 — Observability / Ops**  
Invocation: request context, logs, redaction, exception, metric, provider failure, queue telemetry, health.  
Local policy: safe Identity dimensions/failure classes.  
Prohibited duplicate: Identity Ops tables/logger/metric backend.

**SH-046 / SH-047 — outbox/job**  
Invocation: durable post-commit effects.  
Local policy: Identity event/job payload.  
Prohibited duplicate: private event bus/queue.

### Domain Logic

- Consent proof and security success are separate.
- Hold decision and local security lock are separate.
- Audit evidence and security history are separate.
- Notification delivery and verification/acknowledgement are separate.
- Ops failure record and business/security lifecycle are separate.
- When an external support dependency is required for a high-risk action and unavailable, follow explicit fail-closed/unavailable policy rather than silently bypassing it.
- Post-commit notification/ops failures do not rewrite a successfully committed Identity transition unless the root architecture explicitly makes a side effect transaction-critical.
- Security-event metadata and all external support payloads are minimized/sanitized.

### Authorization / Compliance

- protected support/admin reads still require SH-002;
- Consent requirements must be named/versioned, not invented ad hoc;
- Hold release remains Hold-owner authority;
- AccessAuditLog is created only through Audit owner;
- sensitive payloads are redacted before audit/log/notification.

### Database / Transaction Behavior

No foreign support table is written directly.

For durable post-commit effects:

```text
Identity authoritative transaction
→ UserSecurityEvent
→ outbox side-effect request(s)
→ commit
→ Notification/Audit/Ops consumer
```

If generic audit must be transaction-atomic for a specific high-risk action, that must be an approved platform architecture decision; do not improvise a local audit table.

### Events / Jobs

Exercise real outbox/job mechanisms for:

- Notification intent;
- provider failure/reconciliation;
- optional downstream Identity integration events.

No new support-rail lifecycle.

### Provider Integration

Health/failure reporting for auth, OTP, passkey, recovery provider adapters.

No provider delivery implementation for generic Notification.

### UI / Admin Surface

Optional internal/admin diagnostics may show:

- safe provider health;
- recovery backlog/count;
- last failure correlation;
- audit/notification references.

It must be read-only/supportive and not become a second source-of-truth editor.

### Failure Behavior

- Consent service unavailable for required proof → unavailable/fail closed;
- Hold service unavailable for required action → unavailable/fail closed;
- Audit/Notification transient failure after committed Identity state → durable retry according to platform semantics;
- Ops failure to record telemetry must not mutate Identity status;
- notification delivery failure must not mark recovery proof successful/failed;
- malformed support payload → fail/repair integration, not domain corruption.

### Tests

- Consent proof vs security proof negative tests;
- Hold vs security-lock separation tests;
- Audit vs UserSecurityEvent separation tests;
- AccessAuditLog tests for sensitive reads;
- Notification-not-proof tests;
- provider failure/domain-state separation tests;
- redaction tests across audit/log/notification;
- required-dependency unavailable behavior;
- outbox retry/idempotency tests;
- health check contract tests.

### Documentation Updates

- update U-IA-14/U-IA-18 if settled;
- record named Identity actions requiring Consent/Hold/Audit/Access/Notification;
- update integration contract docs;
- progress tracker.

### Acceptance Criteria

- no support-rail record replaces Identity source truth;
- no local duplicate Hold/Audit/Notification/Ops system exists;
- required high-risk gates fail safely when unavailable;
- all support payloads are redacted/minimized;
- post-commit side effects are retryable/idempotent.

### Exit Gate

- cross-cutting support contract suite passes;
- negative separation tests pass;
- no direct foreign-table mutation is used;
- build passes.

---

# Phase 5 — Privacy and Retention

## 09 Identity Privacy Executor and Retention-Safe Data Handling

### Objective

Implement Identity’s side of the Privacy / Data Erasure protocol: enumerate Identity-owned subject data and execute only Privacy-authorized erase/anonymize/revoke/retain actions without creating a local privacy workflow or bypassing security/legal retention.

### Observable Result

- A Privacy-owned test request can ask Identity to enumerate relevant subject records/provider references.
- Identity returns standardized retention facts.
- A Privacy target can invoke an idempotent Identity executor.
- Approved fields/resources can be anonymized/revoked/deleted where allowed.
- Retained records remain intact when Privacy supplies a retention disposition/exemption.
- Direct User hard-delete remains unavailable until all required retention rules are approved.

### Cluster Build-Plan Link

Implements Identity’s portion of **CL-01 Feature 16 — Privacy, Holds, Audit, Notification, and Operational Support Bridges**.

### Dependencies

- Features 01–08;
- Privacy protocol SH-095–099;
- SH-070 provider resource deletion;
- SH-044 idempotency;
- SH-047 reliable jobs if async;
- canonical anonymization/crypto;
- U-IA-12 retention periods/dispositions before destructive production behavior;
- U-IA-13 User profile/public-field ownership where export/erase treatment depends on it.

### In Scope

- `enumerateIdentitySubjectData`;
- Identity privacy inventory mapping;
- Identity export fragment;
- Identity-specific SH-095 executor;
- retention fact response;
- approved anonymization mappings;
- provider account/passkey/recovery resource revoke/delete calls where allowed;
- standardized result back to Privacy;
- idempotent retry;
- audit/ops reporting for the execution itself as approved.

### Out of Scope

- Privacy request intake;
- DataErasureJob/DataErasureTarget state;
- retention-exemption persistence;
- final privacy export artifact assembly/delivery;
- blanket User cascade deletion;
- foreign Module data erasure;
- inventing retention periods.

### Module-Owned Data

Potential Identity target categories:

- `User`
- `UserRole`
- `AgeGateAttempt` where subject-linked
- `UserSecurityProfile`
- `AuthProviderAccount`
- `PasskeyCredential`
- `StepUpChallenge`
- `SensitiveActionSession`
- `AccountRecoveryRequest`
- `UserSecurityEvent`
- Identity-owned provider resources/references

`AgeGateBlock`/pre-account hashes require careful treatment because they may not be safely attributable to one known subject.

### Public Interfaces

- SH-096 Identity implementation: `enumerateIdentitySubjectData`
- Identity executor under SH-095
- Identity SH-097 retention-fact response
- export fragment contract
- provider delete/revoke adapter calls under SH-070

### Shared Operations Used

**SH-095 — `executePrivacyInstruction`**  
Owner: Privacy orchestrates; Identity executes.  
Invocation: trusted Privacy target instruction.  
Local policy: mapping of disposition to Identity records.  
Prohibited duplicate: `deleteUser.ts`, local privacy workflow.

**SH-096 — `enumerateSubjectData`**  
Owner: each data owner through Privacy contract.  
Invocation: Privacy inventory.  
Local policy: Identity subject-data mapping.  
Prohibited duplicate: global schema crawler as policy.

**SH-097 — `evaluateRetentionRequirement`**  
Owner: data owner supplies facts; Privacy records exemption.  
Invocation: before destructive action.  
Local policy: security/legal retention facts.  
Prohibited duplicate: Identity retention-exemption table.

**SH-098 — `anonymizePersonalFields`**  
Owner: shared primitive; Identity supplies mapping.  
Invocation: approved anonymization.  
Local policy: which fields preserve necessary evidence.  
Prohibited duplicate: blanket null/delete helper.

**SH-070 — `deleteProviderResource`**  
Owner: provider-owning Module.  
Invocation: provider-side credential/recovery resource action as instructed.  
Local policy: Identity resource/disposition.  
Prohibited duplicate: generic provider cleanup detached from adapter.

**SH-044 / SH-047**  
Invocation: executor replay/reliable async execution.  
Local policy: Privacy target ID as semantic key.  
Prohibited duplicate: local privacy queue/idempotency framework.

### Domain Logic

- Privacy decides request/job/target and records retention exemption.
- Identity knows the meaning of its records and performs the instructed operation.
- Expired/revoked security artifacts may still require retention; “inactive” does not mean “safe to delete.”
- Erasure may mean anonymize, detach, revoke, delete, or retain depending on approved disposition.
- Provider resource deletion and local record retention can differ.
- A retained UserSecurityEvent may require personal metadata minimization rather than deletion.
- Do not create new linkage from pre-account age-gate hashes to a subject merely to make enumeration easier.
- All executor steps are idempotent.

### Authorization / Compliance

- executor accepts only trusted Privacy orchestration identity/context;
- no end-user directly calls the destructive executor;
- retention disposition is authoritative from the Privacy workflow;
- generic audit/access requirements still apply;
- no destructive Consent/Track/other data mutation from Identity.

### Database / Transaction Behavior

Each target operation should:

```text
claim Privacy target idempotency key
→ load only Identity-owned target records
→ verify requested disposition/retention instruction
→ apply transactional anonymize/revoke/delete where possible
→ append approved owner/audit evidence
→ return standardized result
```

Do not rely on existing cascading deletes as the privacy implementation.

### Events / Jobs

- reliable Privacy executor job if orchestrated asynchronously;
- provider deletion/revoke retries via shared queue;
- operational failure visible to Privacy/Ops;
- no local DataErasureJob state.

### Provider Integration

Provider-side revocation/deletion through Identity adapters only.

Unknown provider deletion status returns retry/review/retained result; it does not cause local false success.

### UI / Admin Surface

No Identity-owned privacy request UI required.

Optional admin support can display safe executor result references through Privacy owner.

### Failure Behavior

- retention required → return retained/anonymized disposition, no destructive delete;
- provider deletion transient failure → retryable result to Privacy;
- provider deletion terminal/unsupported → structured result/manual review;
- one Identity target failure → do not guess Privacy job outcome;
- repeated target instruction → same semantic result;
- missing foreign data → no direct foreign cleanup.

### Tests

- subject-data enumeration coverage;
- executor contract tests;
- idempotent replay;
- anonymization mapping;
- retention-exemption behavior;
- provider revoke/delete fixtures;
- cascade-delete protection;
- pre-account hash non-linkage test;
- export fragment redaction;
- negative test proving PrivacyRequest/DataErasureJob are not created here.

### Documentation Updates

- U-IA-12/U-IA-13 when resolved;
- Identity privacy inventory;
- anonymization/retention matrix;
- provider deletion behavior;
- progress tracker.

### Acceptance Criteria

- Privacy can enumerate and execute all enabled Identity targets through contracts;
- Identity touches no foreign Module truth;
- retention prevents unauthorized destruction;
- hard-delete shortcut is absent;
- provider cleanup is adapter-owned and replay-safe;
- no local Privacy workflow exists.

### Exit Gate

- Privacy contract/integration suite passes;
- destructive production behavior is enabled only for approved retention dispositions;
- direct cascade-delete bypass tests fail safely;
- build passes.

---

# Phase 6 — Module Integration Proof

## 10 Cross-Module Actor and Step-Up Contract Proof

### Objective

Prove Identity & Access works as a platform foundation through stable public contracts without downstream Modules reading Identity tables or reimplementing authentication/MFA.

### Observable Result

Contract/integration fixtures prove:

- Role / Authority receives SH-001 actor + structural role facts without owning Identity rows.
- Customer / Buyer Profile or another approved consumer can react to a User-provisioned fact without Identity creating its profile.
- Transaction / Order, Payment / Payout / Tax, or another sensitive-action test consumer can call SH-014 and use the scoped assurance result without reading StepUp tables.
- Consent/Hold/Audit/Notification/Ops/Privacy boundaries operate through public interfaces.
- Dependency denials/outages fail safely.
- No integration test requires direct foreign mutation of Identity internals or direct Identity mutation of foreign data.

### Cluster Build-Plan Link

Supports **CL-01 Phase 4 — Cross-Cluster Contract Proof (Features 14–16)**, especially **Feature 16** for support/privacy bridges, and validates the Identity contracts relied upon by all protected Clusters.

### Dependencies

- Features 01–09;
- versioned public contract fixtures for Role / Authority, Customer / Buyer Profile, at least one sensitive-action consumer such as Transaction / Order or Payment / Payout / Tax, and support rails;
- real outbox/inbox/queue in integration environment where available;
- root contract-versioning conventions.

### In Scope

- SH-001 consumer contract suite;
- structural role facts contract;
- User-provisioned event contract if an actual consumer exists;
- SH-014 consumer contract suite;
- downstream negative behavior for wrong actor/action/target assurance;
- support-rail contract proof;
- provider-unavailable behavior through consumer boundary;
- domain-event delivery/replay proof;
- cross-Module privacy executor proof.

### Out of Scope

- implementing downstream business lifecycles;
- direct downstream repository access;
- new Identity features;
- CustomerProfile creation logic;
- Order/payment mutations;
- general permission policy;
- public Search/media delivery.

### Module-Owned Data

No new source truth is expected.

Existing Identity records may be created through public commands as integration fixtures.

### Public Interfaces

Freeze/version the enabled boundary:

- SH-001 `resolveAuthenticatedActor`
- safe structural role facts
- `getUserSecurityPosture` where approved
- SH-014 `requireStepUpForSensitiveAction`
- recovery/security public commands where external consumers exist
- Identity privacy executor
- versioned integration events

### Shared Operations Used

This feature verifies the SH operations already used rather than creating new ones.

Primary focus:

- SH-001 actor resolution
- SH-002 authority composition
- SH-014 step-up
- SH-029/030 audit/access
- SH-041 Notification
- SH-044/046/047 event/idempotency/job
- SH-095–098 Privacy
- SH-032–039 Observability

For each, tests must prove the canonical implementation/contract is used and no local substitute is required.

### Domain Logic

- SH-001 returns identity facts only.
- Role interprets permission.
- SH-014 returns assurance only.
- Downstream owner combines authorization, assurance, consent/entitlement/readiness/hold/business rules as appropriate.
- Identity events describe facts, not cross-Module commands.
- Downstream events are deduplicated by the consumer.
- SensitiveActionSession internals remain hidden behind SH-014.
- Privacy orchestrates Identity executor.
- No consumer infers provider/session secrets or security internals from public DTOs.

### Authorization / Compliance

Negative contract cases are mandatory:

- wrong User;
- revoked/expired assurance;
- wrong target;
- missing Role authority;
- required hold active;
- provider unavailable;
- sensitive admin action lacking approved step-up;
- privacy target called without trusted orchestration.

### Database / Transaction Behavior

Integration tests use real Identity transactions where possible.

No test may “make it work” by mutating foreign owner tables through Identity repositories or by directly editing Identity tables from the consumer unless the test explicitly verifies database security.

### Events / Jobs

Exercise:

- real outbox/inbox replay where implemented;
- duplicate User-provisioned/security events;
- delayed Notification/Audit effects;
- Privacy job invocation;
- provider reconciliation where applicable.

### Provider Integration

Provider adapters may run against sandbox/fixtures. The consumer sees only normalized Identity results.

### UI / Admin Surface

Playwright/E2E may cover:

- sign in;
- account security;
- sensitive test action requiring step-up;
- recovery;
- approved admin security action.

No artificial cross-module UI is required.

### Failure Behavior

- Identity unavailable → protected consumer cannot infer/authenticate actor;
- Role unavailable → downstream action fails according to Role contract;
- step-up provider unavailable → sensitive action remains unassured/unavailable;
- duplicate Identity event → consumer effect remains once;
- stale contract/event version → explicit compatibility failure/dead-letter, no silent partial mutation;
- Notification/Audit transient failure → source truth remains correct and side effect retries according to platform policy.

### Tests

- SH-001 contract tests across multiple consumers;
- Role structural-role boundary tests;
- User-provisioned event consumer test;
- SH-014 consumer tests for Order/Payment/admin fixture;
- direct StepUp table access negative test at architectural boundary;
- duplicate/out-of-order event tests;
- support-rail contract tests;
- Privacy executor integration;
- RLS/cross-user tests;
- E2E sign-in → sensitive action → step-up → action success;
- E2E recovery where production-enabled.

### Documentation Updates

- version/freeze public Identity contracts;
- update dependency public-interface references;
- record any discovered architecture mismatch before code change;
- update progress tracker.

### Acceptance Criteria

- downstream protected consumers need no local auth/MFA implementation;
- no consumer needs direct Identity Prisma access for supported behavior;
- actor and assurance remain distinct from permission/business truth;
- events are replay-safe;
- negative dependency cases fail safely;
- public contracts are documented/versioned.

### Exit Gate

- all enabled cross-Module positive/negative contract tests pass;
- no direct foreign/Identity repository coupling is required by consumers;
- event replay and failure recovery are proven;
- build/E2E pass.

---

# Phase 7 — Module Hardening and Production Verification

## 11 Provider Replay, Concurrency, Session Safety, Reconciliation, and Production Hardening

### Objective

Prove Identity & Access is safe under production failure modes: provider degradation, retries, callback replay/order changes, concurrent security transitions, session compromise/recovery, privacy retention, database migration, high load, and operational troubleshooting.

### Observable Result

- Duplicate/replayed commands and provider events produce effectively-once Identity effects.
- Concurrent challenge/recovery/provider/role operations preserve invariants.
- Provider outage or unknown state leaves explicit safe lifecycle state.
- Session-revocation behavior is documented and testable for every enabled security transition.
- Reconciliation repairs or surfaces provider drift without guessing.
- Privacy/retention destructive paths are approved and tested.
- RLS and server authorization remain semantically aligned.
- Logs/metrics/audit/notifications contain no prohibited secrets.
- Critical Identity E2E journeys pass against production-like infrastructure.

### Cluster Build-Plan Link

Implements the Identity portion of **CL-01 Feature 17 — Backfills, Reconciliation, and Migration Safety** and **Feature 18 — Security, Privacy, Concurrency, and Production Readiness Hardening**.

### Dependencies

- Features 01–10 exit gates;
- all `U-IA-*` decisions required by production-enabled paths resolved;
- production-like Postgres/RLS;
- provider sandbox/test environments;
- migration/backfill/rollback plan;
- Privacy/security review;
- DLQ/re-drive/health/metrics infrastructure.

### In Scope

- final provider identity uniqueness/merge enforcement;
- final OAuth age-gate enforcement;
- final session-revocation matrix;
- final sensitive-action vocabulary/matrix;
- final OTP secret/challenge storage policy;
- final challenge/recovery concurrency rules;
- provider-event dedupe schema if callbacks enabled;
- recovery manual-review workflow contract if enabled;
- security-tier transition rules if enabled;
- retention behavior;
- provider callback/reconciliation chaos tests;
- migration/backfill/reconciliation;
- performance/load testing for SH-001/SH-014;
- RLS/authorization parity;
- secret/PII scan;
- operational runbooks and health signals.

### Out of Scope

- new product features;
- public User search/profile until U-IA-13 is resolved into explicit architecture;
- organization/business authorization refactors;
- new generic risk/compliance engine;
- changing canonical shared infrastructure ownership;
- refactoring neighboring Modules simply to simplify Identity.

### Module-Owned Data

Review all Identity-owned schema and indexes:

- User/provider mapping;
- UserRole;
- age gate;
- security profile;
- provider account;
- passkey;
- challenge/session;
- recovery;
- security events;
- provider-event dedupe truth if approved.

### Public Interfaces

Freeze/version all production-enabled Identity contracts.

Breaking changes require explicit interface migration rather than silent parameter changes.

### Shared Operations Used

All previously used operations, with hardening focus on:

- SH-044 idempotent command;
- SH-045 domain-event consumer dedupe where Identity consumes events;
- SH-046 outbox;
- SH-047/048 queue/retry;
- SH-051/052 locks/concurrency;
- SH-053 state transition;
- SH-055 deadline expiration;
- SH-059/060/061/062 provider verification/dedupe/translation/reconciliation;
- SH-070 provider deletion;
- SH-072/074/075/076 crypto;
- SH-029/030 audit/access;
- SH-032–039 observability;
- SH-095–098 privacy.

No local substitutes may be introduced during hardening.

### Domain Logic

Hardening must settle and prove:

- exactly one local User per approved provider identity mapping;
- safe multi-provider linking/merge behavior;
- age gate cannot be bypassed by OAuth/provider path;
- active credential summaries reconcile to source records;
- revoked/compromised credentials cannot authenticate;
- challenge single-consumption semantics;
- assurance grant scope/expiry/revocation;
- recovery single-completion semantics;
- provider callback replay/order handling;
- session revocation after every approved compromise/security transition;
- local security lock semantics;
- role mutation safety;
- fail-closed behavior for unavailable required gates;
- retention-safe privacy execution;
- no exactly-once transport claim—only effectively-once effects.

### Authorization / Compliance

Final review:

- admin/support action matrix;
- sensitive-action step-up matrix;
- account enumeration resistance;
- age-gate enforcement;
- Role/RLS parity;
- Consent requirements for security workflows;
- ComplianceHold composition;
- Privacy/retention;
- sensitive-access audit;
- raw-secret/PII/provider-payload redaction;
- provider credential/secret management.

### Database / Transaction Behavior

Review/enforce:

- provider identity uniqueness constraints;
- AgeGateBlock identifier constraint;
- Passkey unique hash;
- UserRole composite uniqueness;
- challenge/recovery transition conditional updates;
- approved one-active challenge/recovery constraints if required;
- provider event unique receipt;
- indexes for SH-001/security/recovery queries;
- append-only security event protections where practical;
- retention-safe delete behavior;
- RLS on sensitive tables.

Every destructive migration requires backup/rollback/verification plan.

### Events / Jobs

- provider reconciliation schedules;
- expiration schedules;
- DLQ re-drive procedures with idempotency;
- backfill checkpoint/resume;
- event/queue/provider lag metrics;
- operational alert thresholds;
- event-version compatibility tests.

### Provider Integration

Chaos/failure verification for:

- Supabase/Auth provider unavailable;
- OAuth errors/conflicts;
- WebAuthn/passkey failure;
- OTP provider timeout/duplicate result;
- recovery provider outage/unknown result/duplicate callback;
- session revocation outage;
- provider deletion/reconciliation.

### UI / Admin Surface

Production-safe support visibility may expose:

- auth-provider health;
- OTP/recovery-provider health;
- recovery manual-review backlog;
- failed/dead-letter jobs;
- provider/reconciliation discrepancies;
- safe correlation IDs;
- account security summary.

It must not expose secrets/raw provider payloads or become a second source-of-truth editor.

### Failure Behavior

Document and test exact product behavior for:

- auth provider unavailable;
- invalid/expired session;
- provider mapping conflict;
- age-policy service/config unavailable;
- passkey provider/browser unavailable;
- OTP provider unavailable;
- challenge serialization conflict;
- recovery provider unavailable;
- unknown/out-of-order callback;
- session-revocation failure;
- Role/Consent/Hold/Audit/Notification/Ops dependency degradation;
- Privacy executor retry/terminal failure;
- database serialization conflict;
- migration/backfill mismatch.

Every case must end in explicit deny, unavailable, retry, pending, conflict, recovery-required, or manual-review behavior. No generic “500 and hope.”

### Tests

- full unit/domain suite;
- public contract suite;
- provider fixture/sandbox suite;
- webhook signature/dedupe/order/reconciliation suite;
- concurrency stress for provisioning/provider link/passkey/challenge/recovery/role;
- session revocation matrix suite;
- RLS/server authorization parity;
- privacy/retention suite;
- migration from clean DB;
- representative legacy/backfill migration;
- backfill restart/reconciliation tests;
- performance/load for SH-001 and SH-014;
- secret/PII logging scan;
- dependency chaos tests;
- critical Playwright/E2E;
- production build.

### Documentation Updates

- resolve/remove every production-relevant `U-IA-*` item;
- update `module-architecture.md` for all binding rulings;
- update public interface docs;
- migration/backfill/runbook docs;
- provider runbooks;
- privacy/retention matrix;
- progress tracker.

### Acceptance Criteria

Identity is production-ready only when:

- no enabled path depends on an unresolved high-risk architecture decision;
- no lifecycle has two owners;
- no local duplicate shared infrastructure exists;
- provider callbacks are authenticated, deduped, translated, reconciled;
- concurrency tests preserve invariants;
- session-revocation behavior is explicit/tested;
- RLS/server parity passes;
- privacy/retention destructive behavior is approved/tested;
- audit/access/notification/observability are complete without replacing domain truth;
- no prohibited secret/PII leakage is found;
- critical E2E journeys pass;
- clean migration and rollback/backfill verification pass.

### Exit Gate

Module production exit requires all of:

- typecheck;
- lint;
- unit tests;
- database/integration tests;
- public contract tests;
- provider tests;
- concurrency/idempotency stress tests;
- RLS/security tests;
- privacy/retention tests;
- E2E tests;
- secret/PII scan;
- production build;
- architecture/plan/progress agreement.

Any failed criterion means the Module hardening gate is **FAIL**, even if the happy path works.

---

# Module Integration Phase

**Phase 6 / Feature 10** is the explicit Identity & Access integration phase.

Its purpose is to prove contracts, not to absorb downstream truth.

Minimum boundaries to prove:

```text
Authentication provider
→ Identity SH-001
→ Role / Authority

Identity User provisioned fact
→ Customer / other approved actor-branch consumer
(without Identity creating the branch)

Role / Authority decision
→ Identity protected security mutation

Sensitive downstream action
→ SH-014 Identity assurance
→ downstream owner keeps resource/business decision

Identity security/recovery effects
→ Notification / Audit / Ops
(without those records replacing Identity truth)

Privacy
→ Identity subject enumeration/executor
(without Identity creating PrivacyRequest/DataErasureJob)
```

Contract tests must prefer public DTOs/interfaces/events over shared database assumptions.

If a neighbor is not yet implemented, use a versioned fixture/fake matching the approved contract. Do not import its internal repository into Identity.

---

# Module Hardening Phase

**Phase 7 / Feature 11** is the Module hardening phase.

It is limited to Identity-relevant production risk:

- account/session security;
- provider identity mapping;
- OAuth age-gate sequencing;
- passkey/OTP/recovery provider degradation;
- session revocation after security changes;
- command/provider-event replay;
- challenge/recovery concurrency;
- provider reconciliation;
- rate limiting/abuse resistance;
- RLS/server parity;
- security-event/audit/access completeness;
- privacy/retention;
- migration/backfill safety;
- query performance for SH-001/SH-014;
- telemetry redaction;
- operational runbooks/health.

Hardening must not introduce:

- a generic platform permission engine;
- a generic compliance engine;
- a second audit ledger;
- a second queue/event bus;
- a new privacy workflow;
- local notification delivery;
- business access grants;
- public User search/profile behavior without an architecture ruling.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Account Identity Foundation | 01–02 |
| 2 | Strong Authentication and Action-Scoped Assurance | 03–04 |
| 3 | Account Recovery | 05–06 |
| 4 | Structural Security Administration and Support-Rail Integration | 07–08 |
| 5 | Privacy and Retention | 09 |
| 6 | Module Integration Proof | 10 |
| 7 | Module Hardening and Production Verification | 11 |

**Total numbered features: 11.**

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture.
2. Read root code standards.
3. Read the Canonical Shared Operations Registry.
4. Read CL-01 architecture and build plan.
5. Read `identity_access/module-architecture.md` and this plan.
6. Read public-interface sections for direct dependencies.
7. Confirm the prior feature exit gate passed.
8. Check all `U-IA-*` decisions relevant to the feature; resolve binding blockers before enabling dependent production behavior.
9. Write the concise implementation specification for this feature.
10. Implement only this feature.
11. Run required quality/contract/workflow checks and verify failure/idempotency paths.
12. Update progress and any public-interface documentation; update architecture only when a binding decision legitimately changed.
13. Record assumptions, known failures, remaining risks, unresolved decisions, deferred work, and explicit exit-gate PASS/FAIL.

Do not begin adjacent “helpful” Identity, Role, Customer, Track, Payment, Privacy, or Notification work merely because the code is nearby.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise specification containing:

- Objective
- Observable result
- Cluster Build-Plan link
- Dependencies
- Architecture decisions required before implementation
- In scope
- Out of scope
- Module-owned data affected
- Enums/statuses/lifecycle transitions affected
- Public contracts
- Shared operations consumed by SH-### ID
- Actor / authority requirements
- Consent / hold / readiness / entitlement gates as applicable
- Primary success workflow
- Provider integration
- UI/admin states if applicable
- Jobs/events/outbox/inbox
- Idempotency/concurrency strategy
- Error/failure/retry/manual-review behavior
- Privacy/retention impact
- Audit/observability requirements
- Tests
- Acceptance criteria
- Documentation/progress updates

Do **not** generate implementation specifications for all 11 features in advance. The specification is written immediately before the next feature so it reflects current architecture, prior exit gates, and any resolved `U-IA-*` decisions.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations and constraints
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused, by SH-### ID
- Dependency Module contracts consumed
- Events/outbox/inbox handlers added
- Jobs/workers/schedules added
- Provider ports/adapters added or changed
- Tests added/changed
- Commands run
- Manual/contract/workflow verification performed
- Security/compliance/privacy verification performed
- Documentation/progress updated
- Architecture decisions resolved/changed
- Assumptions
- Known failures
- Remaining risks
- Unresolved decisions encountered
- Deferred work
- Exit-gate result: **PASS** or **FAIL**, with every failed criterion listed explicitly

A feature is not complete merely because its happy path works.

---

# Final Quality Check

Before treating this Module plan as executable context, verify:

1. Every Identity source-of-truth record has exactly one owner.
2. No neighboring Module truth was absorbed into Identity & Access.
3. SH-001 and SH-014 are exposed as canonical Identity capabilities; all other shared operations are consumed rather than duplicated.
4. Shared mechanism / separate truth boundaries are explicit for grants, lifecycle transitions, provider dedupe, workflows, crypto, audit, events, and Privacy.
5. Identity commands/queries have explicit ownership and bounded inputs/results.
6. Cross-Module reads/writes use public contracts rather than foreign repositories by default.
7. Provider adapters produce evidence and normalized results; they never become account/recovery truth.
8. UserSecurityEvent, generic audit/access, integration events, and observability are distinct.
9. Privacy orchestration remains Privacy-owned.
10. Search remains projection and no public User projection is introduced while U-IA-13 is unresolved.
11. Numbered Module features align with CL-01 Features 01–05 and 16–18 and the Cluster integration sequence without independently reordering Cluster ownership.
12. Every numbered feature specifies tests, acceptance criteria, and an exit gate.
13. A coding agent can implement each slice without inventing security/provider/privacy architecture.

If any item fails, update the architecture/plan before implementation rather than allowing code to become the accidental architecture.


## WA-R018 — Durable execution, receipts and operational evidence

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R018 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r018--durable-execution-receipts-and-operational-evidence) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one platform-owned persistent command-idempotency/inbox/outbox/job mechanism with Postgres transactional persistence in the coordinated database pass. Module application/domain boundaries own effect semantics. A successful owner mutation atomically stores its domain change and outbox record; no transaction is held across provider/network calls. Consumers atomically claim a stable source event plus effect identity and commit their owner effect. Unknown outcomes reconcile before a new business attempt. Same scoped command key plus same canonical fingerprint replays the original result; different fingerprint conflicts. Owner/operation/subject scope is part of the key. At-least-once delivery is assumed; never promise global exactly-once execution.

Provider callbacks use verified provider/account/event identity, payload fingerprint, receipt state and separate effect/attempt state under the provider-owning Module (SH-059/060). A received/claimed record is not proof of completed effect. Duplicates preserve original proof; telemetry records observations. A retry of one semantic effect reuses its downstream idempotency identity. A genuinely new business attempt has a new identity linked to the prior result and cannot silently overwrite history. Booking workflow steps likewise carry a stable run/step/effect key. Exact tables/index names and runner library are implementation details; production runtime evaluation remains a scoped provider/operational gate, not a reason to build Module-local queues.

Adopt Ops-owned Postgres persistence for operational SystemEvent, IntegrationFailure and OpsIncident; QueueJob remains an operational projection of the platform runner, not a second executable queue. SystemEvent is append-only; correction references the original. IntegrationFailure separates occurrence identity from recovery observations; recording the same occurrence replays, another actual attempt creates another occurrence. Incident operator state is open/triaged/mitigated/resolved, with explicit authorized reopening recorded as a new transition; automatic grouping/alerts require versioned configured rules. Ops success/recovery cannot finish a business workflow. Tradeoff: durable local diagnostic queries require migrations/storage; provider dashboards remain secondary. Accept PR-CL09-05 persistence direction without claiming schema deployment or selecting retention periods.

Acceptance: concurrent identical/conflicting keys, crash after receipt and before effect, crash after domain commit and before dispatch, duplicate/out-of-order callback, lease recovery, retry exhaustion and reconciliation. Do not activate a consumer merely because a queue accepted its job.


## WA-R019 — Consent catalog, acceptance causation and buyer provisioning

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R019 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r019--consent-catalog-acceptance-causation-and-buyer-provisioning) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Consent owns an immutable version/content catalog, including consent type, version, exact content or immutable content reference/hash, locale, jurisdiction applicability and effective interval. Existing logs cannot prove an unrecorded presentation. Bind acceptance to the catalog entry and the actual rendered presentation identity/version, subject, action/context and time; preserve an immutable rendering descriptor where composition changes presentation. SH-009 selects applicable content, SH-007 stores acceptance, and SH-008 queries proof. Same acceptance command key/fingerprint replays; a new intentional re-acceptance is a new command/proof, not a uniqueness collision on User+type+version. Current-state eligibility queries use current applicable proof; Orders, screening authorizations, digital terms, redemptions and other historically binding actions preserve their specific proof reference/content-version binding. A generic audit log alone is not that binding.

Withdrawal/decline is recorded separately as an append-only disposition, not by rewriting an earlier acceptance; the consuming policy evaluates its effect. Legal re-consent/material-change obligations and retention periods are external facts. ConsentType.age_gate can prove acknowledgment only; Identity separately evaluates age eligibility. This resolves proof/catalog/retry architecture, not legal sufficiency for every category.

Customer provisioning uses the Customer owner synchronously and idempotently at the first buyer action (SH-004), with durable uniqueness on User. Optional registration-time outbox provisioning can warm the profile but never substitutes for this precondition. Customer aggregate views use the existing SH-126 Customer application facade over authorized owner queries; default to query composition, introducing a durable projection only with a demonstrated query need and invalidation contract. Legacy backfill/deletion awaits the database-evidence gate; User remains authentication identity. Tradeoff: first buyer action depends on Customer availability, but avoids an eventually missing commercial actor and duplicate local provisioning.


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

## WA-R027 — Identity mapping, assurance concurrency and security evidence

Classification: AI_RESOLVED_WITH_TRADEOFF. Applies to Identity and Role contracts; provider capability and legal retention remain scoped external requirements.

Use a stable local Workin Ants User UUID, independent of provider subject. Resolve every authenticated provider subject through an Identity-owned linkage keyed by adapter issuer/tenant plus normalized subject; uniquely bind that identity to one local User. Existing UUIDs are preserved, including any that happen to equal provider UUIDs. Migration must inventory existing bindings and quarantine collisions rather than remap foreign keys or assume equality. RLS resolves the verified provider subject to local actor through the same mapping contract; clients cannot supply their own local actor identity. This accepts PR-IA-05 and resolves U-IA-01 without claiming current nullable/index-only Prisma constraints already enforce it.

User.email is the locally selected verified account contact; AuthProviderAccount.email is provider evidence, not an automatic overwrite source. An explicit email-change flow verifies control of the new address, checks uniqueness under lock, requires action-bound assurance for the existing account, records evidence and notifies the prior verified channel. A changed provider claim alone never changes the canonical contact. Linking requires fresh proof of control of both the current local account and new provider identity; matching email never merges accounts. Conflicts return a non-enumerating review result; no automatic merge or reassignment. Actual account consolidation is unsupported until a separate owner-reviewed migration contract exists.

Age eligibility must precede local User creation. OAuth starts with a short-lived single-use server-bound pre-account attempt carrying nonce/state, intended provider, redirect allowlist and age-policy proof reference. The callback validates provider/state and rechecks proof applicability before atomically consuming the attempt and creating/linking User. A provider-created shadow identity is not a local User or access authorization. Provider auto-provision triggers that bypass this contract must be disabled before OAuth activation. Persist the evaluated policy version, jurisdiction source/version, applicable threshold, decision/reason and evaluated timestamp alongside minimized subject binding. Legal thresholds, eligible regions and proof retention require approved policy; no numerical policy is invented. AgeGateBlock requires at least one usable approved hashed matching identifier (PR-IA-04).

Identity owns StepUpActionType registration and assurance mechanics; each domain owner proposes a namespaced action/target/purpose and Role binds its permission and required assurance. Unknown or unregistered `other` actions cannot authorize sensitive work. Keep OTP verification provider-managed at launch; store provider challenge reference and terminal evidence, not local OTP/hash verification state. A local OTP verifier would require a separate security design. Existing five-minute SMS OTP and fifteen-minute recovery email-token policies are not changed by this ruling. Exact sensitive-action grant TTL/attempt thresholds are versioned security configuration, bounded by actual provider capability and tested before activation.

Allow at most one pending challenge per actor/action/target/purpose. Same command key replays it; a conflicting new request does not silently invalidate another challenge. An explicit authorized replacement cancels the old challenge and invalidates its unconsumed assurance under the same lock. Different independent scopes may coexist; proof cannot cross scopes. Allow at most one nonterminal recovery per User; identical initiation replays and a different initiation returns conflict without exposing account existence. Cancellation followed by a newly authorized initiation creates a new request. Terminal recovery/challenge records are immutable; no reopening them into success. Recovery manual review records reviewer, authority, reason, evidence versions and disposition in Identity-owned security history, and resumes only the next evidence-supported stage. Review approval cannot substitute for required possession/verification proof. ComplianceHold is requested separately only for a registered protective action; it is not recovery truth.

Containment matrix: compromise, completed recovery and verified phone replacement revoke all prior sensitive-action grants and invalidate pre-change sessions via a local security epoch before access can resume. Compromised credentials remain terminal. Revoking a single uncompromised passkey revokes that credential and its dependent grants/sessions; if the provider cannot reliably identify session dependency, invalidate all prior sessions. Privileged role changes invalidate authorization/assurance snapshots; permission removal takes effect on the next protected request regardless of provider session lifetime. Each protected request checks current local epoch/revocation and current Role facts, so provider revocation latency never retains local privilege. Queue and reconcile provider-wide revocation separately, recording failures; do not claim the provider has revoked until it acknowledges.

Security tiers describe account-security risk only: versioned Identity policy may escalate standard→elevated/high_risk or elevated→high_risk on an authenticated incident; de-escalation requires an authorized security review with resolved evidence and a new history entry. A successful ordinary login/OTP does not de-escalate risk or clear a lock. No automatic risk scoring thresholds are invented. Local locks have their own reason/effective window; neither tier nor lock mutates business compliance lifecycles. Credential revoked/compromised states are terminal; create a fresh verified credential/linkage with supersession evidence for subsequent access. `passkeysEnabled`, `smsMfaEnabled`, `backupPasswordConfigured` and `lastStepUpAt` remain summaries; backup password verification belongs to the authentication provider, never local password storage (PR-IA-02/03).

Identity retains account-level display defaults and private account contact/location text; Customer, Candidate, Professional and Organization own their contextual display and publication projections. Generic User.isPublic never authorizes discovery, exact-location disclosure or a profile's visibility. Profile/avatar Media use stays behind the contextual owner and Media validation/access contracts. Accept append-only UserSecurityEvent and versioned transactional outbox separation (PR-IA-07/08). Provider receipt/effect records follow WA-R018; exact table naming is a migration detail, not an unresolved ownership decision. Required security/age/recovery retention and new consent categories remain externally gated; do not infer them from technical fields.

Acceptance before implementation activation: duplicate provider provisioning, conflicting issuer/subject link, equal-email takeover attempt, OAuth callback replay/cross-provider swap, unsupported pre-account trigger, concurrent challenge/recovery initiation, revoked epoch on existing provider session, permission removal with stale authorization cache, manual review lacking required proof and unavailable provider revocation. Test the local containment decision independently from transport success. This amendment supersedes the named U-IA technical alternatives; it does not certify adapter capabilities, migration provenance or legal policy.

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


## WA-R063 — Identity provider qualification, devices and explicit moderation scope

Implementation follows the corresponding applied owner architecture ruling. Required acceptance evidence before activation: all provider age-gate entry routes; wrong-user device revocation; generation invalidation; provider cleanup pending; Notification/session separation; unsupported CL-01 moderation causes no mutation. External legal/provider qualification remains required.


## WA-R066 — Finite Notification source and recipient contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-041 uses the following finite versioned semantic-intent/template registrations. These are architecture contracts, not implemented renderers, selected delivery vendors or proof of delivery. Sources emit an intent only after the corresponding durable owner transition. Every intent binds source owner, typed aggregate ID/revision, immutable semantic intent ID, template key/version, owner-resolved local User recipients, safe authenticated route, sensitivity and event kind. Notification owns channel consent, current endpoint generation, eligible delivery, attempts and receipts. Sources never ask Notification to scan foreign memberships or reconstruct business state.

| Intent/template | Committed source and recipients | Safe additional content |
| --- | --- | --- |
| message.new.v1 | Messaging messaging.message_created.v1; other currently eligible Thread participants selected by Messaging, excluding sender | Thread/Message references only; no message body or attachment URL |
| order.outcome.v1 | Order order.outcome_changed.v1; currently authorized Order participants selected by Order for its source kind | Safe operational outcome code and Order link; no financial consequence implied |
| booking.schedule.v1 | Booking confirmed/rescheduled/cancelled facts; currently authorized affected Booking participants | Safe change kind and authenticated schedule link; no exact address or meeting credential |
| interview.invitation.v1 | Interview invitation/current schedule revision; invited eligible Candidate and authorized Organization participants selected by Interview | Interview reference and safe proposed/scheduled kind |
| interview.schedule.v1 | Interview cancellation/reschedule/replacement; currently authorized affected participants selected by Interview | Safe change kind and authorized predecessor/successor references; no new removed-user notice |
| application.status.v1 | Candidate accepted_offer or withdrawn: current authorized hiring Organization recipients selected by Candidate through Hiring facts; Candidate rejected or hired: the application Candidate User | Application reference and exactly accepted_offer/withdrawn/rejected/hired change code; no view/stage alert or general Candidate exposure |
| privacy.verification_needed.v1 | Privacy durable request transition requiring verification; request subject through Privacy/Identity-authorized route | Request reference and safe action-needed code; no verification secret |
| privacy.outcome.v1 | Privacy accounted terminal outcome; currently authorized request subject/representative | Safe terminal category and link; no restricted exemption evidence or other parties' data |
| privacy.export_ready.v1 | Privacy complete manifest and ready exact Media version/current generation; currently authorized export requester | Request/bundle reference; no signed credential or stored public URL |
| security.notice.v1 | Identity committed security intent; affected local User only | Generic change and authenticated-context link; no OTP, recovery token, precise IP or factor details |
| supply.status.v1 | Professional/Marketplace committed status/remediation intent under R035; owner-resolved Professional User | Generic status/remediation code; no Healthcare/provider/Hold detail |

Candidate registers `candidate.application_status_changed.v1` with eventId, application ID/revision, committed time, semantic command identity, old/new status, authorized actor reference and safe typed Candidate/Organization subject references. This event contains no resume, message, employer notes or protected evidence. The source owner derives notification recipients from current Hiring authority. Only the four listed successful status transitions may create application.status.v1 at launch; application views, recruiter stages and retry transport do not. Candidate acceptance must already satisfy R045 current-offer proof, and withdrawal does not restore quota. Sending a notification never makes an application or Candidate publicly discoverable.

Deduplicate one semantic intent × resolved User; channel attempts are children of that intent. Changed payload under the same fingerprint conflicts. Retries preserve identity. Current protected-context access is rechecked before rendering/dereference; loss of membership suppresses the protected notice. Do not create a removed-user notice without its own approved source policy. Delayed invitation links must recheck P18/current schedule. Notification failure never rolls back source truth. No message bodies, resumes, exact locations, raw provider failures, adjudication evidence or credentials may enter generic variables.

Material proposal changes remain visibly surfaced by Gig's current-revision presentation under P14; a delivered notice is not evidence the latest terms were presented for acceptance. Participant-facing Dispute updates reuse Order conversation under P19, but a Review fact cannot be relabeled as an Order event; any separate Review alert remains disabled until registered. Optional viewed/shortlisted, Location, Interview completion/no-show and other undeclared alerts remain disabled. This finite registration does not provide legally sufficient notice policy. Exact copy, renderer/schema fixtures, provider/account/channel qualification and delivery recovery proof remain activation prerequisites. Existing broad notification suggestions are narrowed by this explicit source/recipient matrix for these intents.


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `identity_access` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`revokeAuthProviderAccount / revokePasskeyCredential; assignPlatformRole / removePlatformRole`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

Platform-role mutation is persisted Identity truth with immutable security evidence and outbox intent; publish identity.platform_role_changed.v1, not a Role-owned stream. The historical identity.platform_role.changed.v1 spelling is an alias, never a second publication. Invalidate bound assurance through the current security generation; no authorization cache is introduced.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.
