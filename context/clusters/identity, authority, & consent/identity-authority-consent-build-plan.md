# Identity, Authority, Consent & Entitlements Build Plan

> **Cluster ID:** `CL-01`  
> **Cluster:** Identity, Authority, Consent & Entitlements  
> **Repository target:** `context/clusters/identity, authority, & consent/identity-authority-consent-build-plan.md`\
> **Companion architecture:** this Cluster `architecture.md`  
> **Modules:** `identity_access`, `role_authority`, `consent_disclosure`, `customer_buyer_profile`, `track_subscription_entitlement`  
> **Implementation posture:** greenfield MVP planning against the current Workin Ants architecture and Prisma evidence. Unresolved security, consent-retention, customer-actor cutover, and commercial-policy decisions remain gated rather than being guessed in code.

---

## Core Principle

Build CL-01 as a sequence of **vertical, testable foundation slices** that prove one real source-owned behavior at a time:

```text
usable / observable behavior
→ owning domain/application service
→ authoritative database state
→ stable public contract
→ permissions / consent / hold / entitlement gates
→ provider or asynchronous effects through approved adapters
→ domain events / audit / observability as applicable
→ tests
→ explicit exit gate
```

CL-01 is not implemented as one broad `auth`, `access`, `identity`, or `policy` service. Every slice preserves the distinctions established in the Cluster architecture:

```text
Identity proves who the account actor is.
Role interprets what the actor may attempt.
Customer resolves buyer actor identity.
Consent proves exact accepted disclosure/version.
Track owns commercial plan/entitlement/usage policy.
The downstream action owner still owns its business lifecycle.
```

A capability does not need artificial UI to qualify as a vertical slice. Where no UI is appropriate, the feature must still produce a concrete public interface, worker, administrative/debug surface, migration result, or observable source-of-truth state with tests and an exit gate.

Foundation work is allowed only when later features genuinely depend on it. Canonical shared infrastructure belongs to its canonical owner and may be consumed through approved interfaces or test doubles if that owner is not implemented yet.

---

## Build Rules

1. Follow `context/project-overview-v3.md`, root `architecture.md`, root `code-standards.md`, the Canonical Shared Operations Registry, and this Cluster `architecture.md`.
2. Do not expand CL-01 into marketplace transaction ownership, organization membership ownership, messaging participant ownership, payment/payout/tax ownership, privacy orchestration, file mechanics, search execution, notification delivery, or generic compliance workflow ownership.
3. Do not redesign Deep Module ownership for implementation convenience.
4. Reuse canonical shared operations. If one is missing, implement/fix it in its canonical owner or depend on its approved contract/test double; do not create a CL-01-local substitute.
5. Use permanent SH IDs and canonical operation names from `context/shared/shared-operations.md`. Registry owner/status/boundaries remain authoritative: Proposed ruling entries, including SH-003/SH-015 and any referenced proposed primitives, require explicit architecture approval before schema/API commitment. Extract-local aliases must not become competing public APIs.
6. Every mutation validates input, resolves the authenticated/system actor when required, authorizes the action server-side, and enforces the owning Module's invariants.
7. Anonymous operations are limited to explicitly allowed entry points such as age-gate evaluation and provider callbacks.
8. Every cross-Module read uses a public owner interface, owner-facts DTO, event, or explicitly approved controlled database policy function. Direct foreign Prisma repositories are not the default.
9. Every lifecycle transition is performed by its owning Module.
10. Role / Authority does not mutate `OrganizationMember`, `OrganizationRole`, or `ThreadParticipant` under PR-CL01-02.
11. `UserRole` and `PlatformRole` remain structurally Identity-owned; Role interprets them.
12. Consent proof never becomes downstream permission, provider-state, or lifecycle truth.
13. Track Subscription & Entitlement is the only current commercial policy rail. No local premium, fee-waiver, commission, priority, quota, or boost truth may be created elsewhere.
14. `TrackUsageEvent` is immutable usage proof; `TrackUsageCounter` remains a rebuildable projection.
15. Every external provider is isolated behind the provider-owning Module's port/adapter.
16. Provider payloads never become Workin Ants domain types.
17. Every provider callback is authenticated/signature-verified and replay/dedupe-protected before business side effects.
18. Every asynchronous operation is durable, idempotent, retry-classified, correlated, observable, and dead-letter visible.
19. Generic `AuditEvent`/`AccessAuditLog` and Observability records supplement but never replace owner domain records.
20. Privacy owns `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, and retention-exemption orchestration; CL-01 owners implement only their target executors and subject-data enumeration.
21. `ComplianceHold` remains the reusable platform stop sign. Do not create generic local blocked-state systems.
22. Media / File Access owns upload, validation, scanning, storage, generic media access, and signed URLs. Customer owns only the avatar/business attachment meaning.
23. Search remains projection. Track requests reindexing; it does not write search-provider truth directly. CustomerProfile public indexing stays disabled until explicitly approved.
24. Every numbered feature ends with automated tests, workflow verification, documentation/progress update, and a concrete exit gate.
25. Do not start the next numbered feature until the previous exit gate passes, except for separately tracked canonical-owner prerequisites explicitly identified as parallel work.
26. Unresolved architecture is not silently settled in code. Resolve the decision, update architecture, then implement dependent behavior.
27. High-risk unresolved behavior fails closed or remains disabled/stubbed rather than defaulting permissively.
28. No production hard-delete path may bypass Privacy/retention rules for User, security, consent, customer, or subscription evidence.

---

## Dependencies and Preconditions

### Root / platform prerequisites

CL-01 assumes the root platform can provide, or can be represented by approved test doubles until implemented:

- runtime request validation and typed boundary schemas;
- request/correlation context;
- SH-044 `executeIdempotentCommand`;
- transactional outbox and consumer-inbox semantics;
- SH-047 `enqueueReliableJob` plus retry/backoff and dead-letter mechanics;
- database-backed aggregate locking/concurrency primitives;
- canonical token/hash/encryption helpers;
- structured logging, exception capture, metrics, `IntegrationFailure`, `SystemEvent`, and queue telemetry;
- generic `AuditEvent` and `AccessAuditLog` interfaces;
- Notification request interface;
- ComplianceHold decision interface;
- Privacy target-executor protocol;
- provider-webhook signature verification and dedupe shell.

If a prerequisite is absent, CL-01 must not create an untracked duplicate. The feature may use an interface/test implementation while the canonical owner is completed.

### Existing CL-01 schema evidence

The current Prisma schema contains the major source records needed for the Cluster:

- Identity/security: `User`, `UserRole`, age-gate records, security profile, provider account, passkey, step-up, sensitive-action session, recovery, security events;
- Consent: `ConsentLog`, `ConsentType`;
- Customer: `CustomerProfile`;
- Track: plan, price, entitlement definition/mapping, subscription, grants, usage events/counters, subscription events.

Database-prerequisite verification remains **unsatisfied**: the checked-in migration evidence does not establish coverage of the current CL-01 Prisma inventory. Migration provenance or approved database-state evidence must be verified separately; schema model presence is not proof of deployment or reproducible migration coverage (CL01-R010).

This plan may add constraints, indexes, fields, or source records only when this Cluster architecture explicitly permits the decision or a named unresolved decision is resolved first.

### Neighboring Module prerequisites

Stable contracts are needed from the following owners; their full product implementations do not need to exist first:

- Admin Review / Compliance Hold — SH-011 `evaluateComplianceHold` and hold-management commands;
- Audit / Event Ledger — audit/access append commands;
- Observability / Ops — structured operational reporting;
- Privacy / Data Erasure — target-executor protocol;
- Media / File Access — attachment validation and signed-access contracts;
- Notification — notification-request contract;
- Organization Hiring — membership/role fact contract for authorization;
- Messaging — participant fact contract for authorization;
- Search / Public Visibility — projection-refresh contract;
- Transaction / Order, Booking & Calendar, Candidate Application, Professional Eligibility, Video/Digital Delivery — consumer contracts required in the cross-Cluster phase.

If a neighboring Cluster is not yet built, use versioned contract fixtures or test doubles. Do not import the neighbor's lifecycle/repository into CL-01.

### Provider prerequisites

The following may be stubbed behind owner ports during domain/contract work:

- Supabase Auth;
- Google / Apple OAuth;
- WebAuthn/passkey runtime/provider behavior;
- Twilio Verify or approved equivalent OTP provider;
- Stripe Identity or Persona for recovery verification;
- Stripe Billing / Checkout / Customer Portal.

Provider credentials are not required for pure domain/contract tests. Live provider activation requires provider-specific integration tests, webhook security, reconciliation, and environment configuration.

### Architecture gates

Named `U-CL01-*` decisions from `architecture.md` are binding gates. In particular:

- Identity provider mapping/email/session/recovery/security-retention decisions must be resolved before production behavior that depends on them.
- Role policy-source and RLS-parity decisions must be resolved before broad production authorization surfaces.
- CustomerProfile transition/provisioning/cutover/public-visibility decisions must be resolved before production cutover or public indexing.
- Consent version-catalog, idempotency, withdrawal/re-consent, and retention decisions must be resolved before production active-version orchestration.
- Track free-plan representation, catalog/effective-date policy, grant precedence, typed value constraints, usage-period semantics, subscription transition table, consent binding, provider-event truth, plan revision, and retention decisions must be resolved before production paid subscription behavior.

---

## Phase 1 — Trusted Account and Authority Foundation

### 01 Age-Gated User Provisioning and Authenticated Actor Context

Create the first trust slice: an eligible person becomes one Workin Ants `User`, authenticates through the approved identity boundary, and protected server code resolves one trusted actor context.

### Objective

Make `User` and SH-001 `resolveAuthenticatedActor` the single server-authoritative account identity foundation while enforcing the pre-account age gate and provider boundary.

### User-visible / Observable Result

- An eligible signup can authenticate and produces one local `User`.
- An ineligible or blocked age-gate path does not create a `User`.
- A protected account/debug surface can return a safe authenticated actor context.
- Replaying the same provisioning intent does not create duplicate User rows.

### Owning Module(s)

- **Identity & Access** owns all source truth and transitions in this feature.

### Dependencies

- Current `User`, age-gate, `AuthProviderAccount`, `UserSecurityProfile`, and security-event schema.
- Provider-neutral auth port backed initially by Supabase Auth.
- Request context, idempotency, outbox/event, and audit/observability contracts.
- Resolve U-CL01-01/U-CL01-02/U-CL01-03 before enabling ambiguous provider-link or account-merge cases; U-CL01-05 governs age-gate proof provenance. Simple one-provider provisioning may proceed fail-closed.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` — Identity owner; resolves verified provider/system credentials to typed Workin Ants actor context. Local policy: User/provider mapping and assurance fields. Do not rebuild route-local current-user helpers.
- SH-044 `executeIdempotentCommand` — platform primitive; protects provisioning. Local policy: semantic key is provider identity + provisioning intent. Do not create Identity-specific generic idempotency storage.
- SH-076 `normalizeAndHashIdentifier` — shared crypto/privacy primitive for age-gate/rate-limit comparison keys. Do not create local hashing algorithms.
- SH-031 `appendDomainLifecycleEvent` — append Identity-owned security/lifecycle evidence transactionally with the source change.
- SH-046 `publishDomainEvent` — publish minimized User/security integration events through the transactional outbox where consumers require them. Publication does not replace owner history, and history does not prove publication.
- SH-029 `appendAuditEvent` and structured Ops primitives — security-relevant administrative actions and safe diagnostics only; neither replaces Identity domain state.

### Data / Schema

- `User`, `AgeGateAttempt`, `AgeGateBlock`, `AgeGateResult`, `AuthProviderAccount`, `UserSecurityProfile`, and relevant `UserSecurityEvent` records.
- Enforce one canonical local mapping per accepted provider subject according to the approved mapping decision.
- `AgeGateBlock` must retain only approved privacy-minimized blocking identifiers and policy evidence.
- No raw password, provider secret, biometric image, or raw OTP may be added to Prisma.

### Public Interfaces

- `provisionUserAfterAgeGate`.
- SH-001 `resolveAuthenticatedActor`.
- Safe account/security summary query needed by self/admin callers.
- Minimized `UserProvisioned` integration event only if another Module has an explicit consumer.

### Logic

- Evaluate and persist age eligibility before local User creation when the age gate applies.
- Accept only provider-verified identity/session input; never trust browser-supplied provider claims.
- Idempotently create/link the local User and baseline security profile.
- Resolve subsequent valid sessions to one typed local actor with assurance context.
- Return explicit conflict/manual-review results for ambiguous provider linking rather than merging accounts automatically.

### UI / Administrative Surface

- Signup/age-gate and login entry where the root application exposes them.
- Safe account identity display.
- Development-only actor-context inspector may exist behind nonproduction/admin controls.

### Authorization / Compliance

- Anonymous access is limited to age-gate/signup/auth entry points.
- COPPA-style age gate precedes User creation when active.
- Do not store full DOB unless a separate legal decision approves it.
- Self/admin account reads become governed by Feature 02 authorization once that feature exists.

### Events / Jobs / Integrations

- Supabase Auth adapter and optional Google/Apple OAuth adapters behind one provider-neutral port.
- User-provisioned outbox event only when consumed.
- Provider/session errors are operational failures, not fake User statuses.

### Failure Behavior

- Invalid/expired provider session → unauthenticated result.
- Blocked age gate → no User creation.
- Duplicate provisioning → return prior semantic result.
- Provider mapping conflict → conflict/manual review; never silent merge.
- Provider unavailable → safe unavailable/retry result; no partial authenticated domain state.

### Tests

- Age-gate unit tests and no-User-on-block database test.
- Actor resolver contract tests.
- Provisioning idempotency/unique-mapping concurrency tests.
- Provider adapter normalization tests.
- Telemetry/secret redaction tests.
- E2E eligible signup/login/protected account read.

### Out of Scope

- Permission interpretation.
- Passkeys/MFA/step-up.
- Recovery.
- CustomerProfile provisioning.
- Consent acceptance.
- Track plan/subscription behavior.

### Exit Gate

- Ineligible signup cannot create a User.
- Eligible provisioning creates exactly one User under replay/concurrency.
- SH-001 `resolveAuthenticatedActor` returns a typed local actor for valid sessions and none for invalid sessions.
- No feature-local current-user helper or raw credential storage exists.
- Typecheck, lint, unit/integration tests, and production build pass; context/progress is updated.


---

### 02 Resource Authorization Contract and RLS Parity

Create the reusable authority slice that turns authenticated actor + source-owner facts + action vocabulary into a stable server-side permission decision.

### Objective

Make SH-002 `authorizeResourceAction` the single permission interpreter while preserving ownership of organization membership, thread participation, and resource relationships in their source Modules.

### User-visible / Observable Result

- Protected test routes/actions return stable allow/deny/review/step-up results with reason codes.
- Admin/support/user platform-role behavior is server-enforced.
- An organization role in one organization grants no authority in another.
- Thread/resource access uses owner-supplied facts without Role acquiring the foreign lifecycle.
- RLS/database-policy fixtures and server policy return the same result for covered rules.

### Owning Module(s)

- **Role / Authority** owns permission interpretation, action vocabulary, and policy behavior.
- **Identity & Access** continues to own structural `UserRole` / `PlatformRole` rows.
- Organization Hiring, Messaging, and resource owners retain their own lifecycle facts.

### Dependencies

- Feature 01 actor context.
- `UserRole` / `PlatformRole` schema.
- PR-CL01-02 owner split and typed owner-facts contracts/test fixtures.
- Root RLS/Postgres helper-function convention.
- Resolve U-CL01-10 before enabling policy paths whose server/RLS source cannot be kept in parity.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` — consumes Identity actor context; Role does not parse sessions.
- SH-002 `authorizeResourceAction` — implemented by Role as the canonical capability. Local policy: action/resource matrix and reason semantics. Do not build feature-specific authorization services.
- SH-003 `queryOwnerFacts` (Proposed ruling) — shared contract/separate owner implementations. Local policy remains with each source owner. Do not build a universal polymorphic repository.
- SH-030 `recordSensitiveAccess` / SH-029 `appendAuditEvent` — Audit-owned proof for policy-defined sensitive reads/admin actions; Role does not own audit ledgers.

### Data / Schema

- No generic authorization source-of-truth table is introduced by default.
- Read structural `UserRole`/`PlatformRole` and owner-fact DTOs only.
- RLS/helper functions may be added only according to root security migration standards.
- Role repositories must not mutate OrganizationMember, OrganizationRole, ThreadParticipant, Order, JobApplication, or other foreign lifecycle records.

### Public Interfaces

- SH-002 `authorizeResourceAction`.
- Typed action/resource vocabulary and stable decision envelope.
- Owner-facts DTO contracts for platform, organization, participant, ownership, and administrator scopes.

### Logic

- Require authenticated actor unless the action is explicitly anonymous.
- Request only the facts needed for the policy.
- Evaluate explicit policy and reason codes; unknown actions fail closed.
- Do not embed consent, Track entitlement, professional readiness, payment, healthcare, or hold truth into Role policy unless the action owner explicitly composes those separate decisions outside Role.

### UI / Administrative Surface

- No public UI required.
- Optional nonproduction/admin policy inspector must redact source-owner data and remain authorization-protected.

### Authorization / Compliance

- Client claims cannot establish platform/admin/support roles.
- Organization and participant scope is resource-specific, not global.
- Positive authorization means 'may attempt'; it is not downstream business eligibility.

### Events / Jobs / Integrations

- No business lifecycle events required.
- Denied/sensitive decisions may emit safe audit/operational evidence under explicit policy.

### Failure Behavior

- Missing owner facts → deny/unavailable; never assume ownership.
- Unknown action/resource → fail closed.
- Owner-facts service unavailable → unavailable/retryable, not allowed.
- RLS/server mismatch → feature fails exit gate.

### Tests

- Pure policy unit matrix.
- Action-vocabulary and decision-envelope contract tests.
- Organization cross-scope isolation and participant tests.
- Admin/support boundary tests.
- Server-vs-RLS parity integration tests.
- Negative architecture test that Role cannot import/write foreign repositories.

### Out of Scope

- Organization membership lifecycle.
- Thread participant lifecycle.
- Consent/entitlement/readiness/hold composition.
- A persistent generic authorization-decision ledger.

### Exit Gate

- Every covered protected test action uses SH-002 `authorizeResourceAction`.
- No competing `isAdmin`, `isOwner`, organization-role, or participant authorization helper is needed for covered paths.
- Foreign owner records remain read-only to Role.
- RLS/server parity passes and unknown policies fail closed.
- Typecheck/lint/tests/build pass and documentation reflects the approved policy source.


---

### 03 Authentication Methods, Passkeys, and Security Posture

Implement provider-neutral authentication-method management and passkey/WebAuthn lifecycle without storing raw credentials or biometrics.

### Objective

Let a User securely register, list, revoke, compromise, or use approved authentication methods while `UserSecurityProfile`, `AuthProviderAccount`, and `PasskeyCredential` remain the Workin Ants security truth.

### User-visible / Observable Result

- A signed-in User can list safe authentication-method metadata.
- Eligible users can register/authenticate with passkeys and revoke a credential.
- Compromised/revoked provider accounts and passkeys are reflected in security posture.
- Raw biometric material and provider secrets are never visible or stored by application domain code.

### Owning Module(s)

- **Identity & Access** owns provider-link, passkey, and security-posture truth.

### Dependencies

- Features 01–02.
- WebAuthn/passkey provider/runtime and provider-neutral credential port.
- Approved security-event and audit/notification contracts.
- Resolve U-CL01-03/U-CL01-06 where provider-account/passkey relationship semantics or fallback rules affect live behavior.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` and SH-002 `authorizeResourceAction` — self/admin method management gates.
- SH-074 `generateSecureToken` — shared security primitive if registration/challenge correlation needs a Workin Ants-generated secret; domain-specific TTL/binding remains Identity policy.
- SH-044 `executeIdempotentCommand` — method registration/revocation replay protection.
- SH-029 `appendAuditEvent` / SH-030 `recordSensitiveAccess` — admin or sensitive method inspection/action proof according to policy.
- SH-041 `requestNotification` — request security-change notices; Identity does not deliver email/SMS/push.

### Data / Schema

- `AuthProviderAccount`, `PasskeyCredential`, `UserSecurityProfile`, `UserSecurityEvent`.
- Store provider subject/credential references, credential IDs/public metadata allowed by WebAuthn design, status, timestamps, and safe device labels only.
- Never store raw password, fingerprint/face image, biometric template, OTP, recovery secret, or provider private key.

### Public Interfaces

- `listAuthenticationMethods`.
- `linkAuthenticationMethod` / provider-neutral callback application command.
- `registerPasskey`, `authenticatePasskey`, `revokePasskey`.
- `markAuthenticationMethodCompromised`.
- `getUserSecurityPosture`.

### Logic

- Provider adapters normalize verified results into provider-neutral security facts.
- Method lifecycle changes update the owning records and relevant security summary transactionally.
- Security summary fields are projections of underlying method state and must remain reconcilable.
- Revocation/compromise never silently deletes forensic security history.

### UI / Administrative Surface

- Account security page: linked methods, passkeys, safe timestamps/statuses, add/revoke actions.
- Admin/support view only for explicitly authorized safe metadata.

### Authorization / Compliance

- Self-service method changes require the authenticated owner and any approved assurance prerequisites.
- Administrative action uses Role policy and audit.
- Passkey UX must not imply Workin Ants stores biometric data.

### Events / Jobs / Integrations

- WebAuthn/passkey adapter and auth-provider adapters.
- Security method change domain events if consumers require session invalidation/notifications.
- Notification request for material security changes.

### Failure Behavior

- Provider registration/auth failure → no local success state.
- Duplicate callback/registration → prior idempotent result.
- Revoked/compromised method → cannot authenticate through that method.
- Provider unavailable → unavailable/retry result; do not mark method active.

### Tests

- Passkey lifecycle unit/integration tests with provider fixtures.
- Security-profile reconciliation tests.
- Revoked/compromised method denial tests.
- Authorization and audit tests.
- Secret/biometric non-storage and telemetry redaction tests.
- E2E account security method flow where provider test support exists.

### Out of Scope

- Step-up action grants.
- Changed-phone recovery.
- Business permissions or entitlements.
- Raw provider SDK types outside the adapter.

### Exit Gate

- Authentication method/passkey lifecycle is provider-neutral outside infrastructure adapters.
- Security posture is reconciled from owner records.
- No raw credential/biometric/secret storage exists.
- Unauthorized method access is denied and sensitive admin actions are audited.
- Provider, unit, integration, typecheck/lint/build checks pass.


---

### 04 Sensitive-Action Step-Up and Temporary Security Sessions

Implement short-lived, action/target-scoped step-up proof so sensitive workflows never rely on a stale global MFA timestamp.

### Objective

Create and verify `StepUpChallenge` and `SensitiveActionSession` as Identity-owned security proof that downstream actions can require without inventing payout/order-specific MFA systems.

### User-visible / Observable Result

- A protected test action can return `step_up_required` and complete after successful challenge verification.
- A successful challenge grants only the approved action/target for the approved TTL.
- Expired, consumed, mismatched, or replayed grants are denied.
- Failure/lockout behavior is visible in security state and safe operational diagnostics.

### Owning Module(s)

- **Identity & Access** owns challenge/session lifecycle; downstream Modules only request/consume the security proof.

### Dependencies

- Features 01–03.
- `StepUpChallenge`, `SensitiveActionSession`, `StepUpActionType`, status/failure enums.
- OTP/passkey provider adapter.
- Resolve U-CL01-07 for final action vocabulary/TTL/attempt/reuse policy before production-sensitive consumers enable the gate.

### Shared Operations Used

- SH-014 `requireStepUpForSensitiveAction` — Identity-owned canonical gate. Local policy: action/target/TTL/assurance matrix. Do not build payout-specific or subscription-specific OTP services.
- SH-001 `resolveAuthenticatedActor` / SH-002 `authorizeResourceAction` — actor and permission precede step-up.
- SH-044 `executeIdempotentCommand` — challenge creation/verification replay safety.
- SH-041 `requestNotification` — security alert intent only.
- SH-029 `appendAuditEvent` and Ops primitives — sensitive admin/security changes and provider failures.

### Data / Schema

- `StepUpChallenge`, `SensitiveActionSession`, `UserSecurityProfile`, `UserSecurityEvent`.
- Challenge secrets/OTPs are never stored in recoverable plaintext.
- Sessions bind to user, action, target/context where required, expiry, assurance/challenge reference, and revocation/consumption semantics.

### Public Interfaces

- `evaluateStepUpRequirement`.
- `createStepUpChallenge`.
- `verifyStepUpChallenge`.
- SH-014 `requireStepUpForSensitiveAction` / `authorizeSensitiveAction`.
- `revokeSensitiveActionSession` where policy requires.

### Logic

- Determine whether the named sensitive action needs stronger assurance.
- Create one bounded challenge with rate/attempt controls.
- On verified provider result, create short-lived scoped session/grant.
- Validate scope/TTL/revocation/consumption atomically when the sensitive action uses it.
- Never treat `lastStepUpAt` alone as sufficient proof.

### UI / Administrative Surface

- Step-up prompt embedded only in workflows that require it.
- Security page may show safe recent challenge/session history without exposing secrets.

### Authorization / Compliance

- Base resource authorization occurs before issuing step-up.
- Step-up proves recent assurance; it does not grant business permission by itself.
- Rate limit and lockout behavior follows Identity security policy.

### Events / Jobs / Integrations

- OTP/passkey challenge provider.
- Challenge/session expiry may use shared reliable jobs.
- Security notification requests and operational failure records.

### Failure Behavior

- Wrong/expired challenge → denied and attempt policy applied.
- Provider timeout → retry/unavailable; no grant.
- Replay of consumed/nonreusable session → denied.
- Target/action mismatch → denied.
- Excess failed attempts → approved lock/review behavior, not ad hoc local block.

### Tests

- State-transition unit tests.
- TTL, target/action binding, replay, rate-limit, and concurrent consumption tests.
- Provider adapter tests.
- Authorization-before-step-up tests.
- E2E sensitive-action challenge flow using test provider.

### Out of Scope

- Payment/payout business eligibility.
- Subscription status.
- Generic ComplianceHold.
- Provider-specific OTP logic outside Identity adapter.

### Exit Gate

- At least one protected test action can require and consume scoped step-up proof.
- Expired/replayed/wrong-scope grants cannot authorize the test action.
- No consumer Module owns an MFA/OTP truth table or local security boolean.
- Concurrency and provider tests pass; final production action matrix remains gated until U-CL01-07 is resolved.


---

### 05 Changed-Phone Account Recovery and Security Event Integrity

Implement the Identity-owned recovery lifecycle and provider boundary for a user who cannot use the prior phone, while preserving complete security history.

### Objective

Provide a controlled changed-phone/account-recovery path that verifies identity through an approved provider and changes Identity-owned contact/security state only through the recovery transition service.

### User-visible / Observable Result

- A user can initiate recovery, complete approved identity verification, and either complete, fail, cancel, expire, or enter manual review.
- Duplicate provider callbacks cannot complete recovery twice.
- A successful phone change invalidates/revises affected security state according to policy.
- Security history clearly distinguishes recovery-domain events from generic audit/observability.

### Owning Module(s)

- **Identity & Access** owns `AccountRecoveryRequest` and all resulting Identity/security transitions.

### Dependencies

- Features 01–04.
- Stripe Identity or Persona provider-neutral recovery port.
- Recovery status/reason/provider enums and `UserSecurityEvent`.
- Consent proof contract may be fixture-backed here; live proof-gated recovery activation waits Features 08–09 where required.
- Resolve U-CL01-08/U-CL01-09 for final callback-dedupe record, manual review, phone-replacement, and retention policy before production activation.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` / SH-002 `authorizeResourceAction` where a logged-in recovery actor exists; recovery-token/provider callback paths use their explicit security boundary.
- SH-008 `queryConsentProof` — exact recovery disclosure proof where policy requires; Consent remains proof owner.
- SH-059 `verifyProviderWebhookSignature` — shared webhook shell; no recovery-local signature utility.
- SH-060 `deduplicateProviderEvent` — shared mechanism with Identity-owned processed-event truth once U-CL01-08 is resolved.
- SH-061 `translateProviderStatus` — Identity recovery adapter maps provider result to domain-neutral recovery result.
- SH-044 `executeIdempotentCommand`, SH-041 `requestNotification`, SH-029 `appendAuditEvent`, SH-037 `recordIntegrationFailure` — reuse canonical mechanics.

### Data / Schema

- `AccountRecoveryRequest`, `AccountRecoveryStatus`, reasons/providers, `UserSecurityProfile`, `AuthProviderAccount`, `PasskeyCredential` as affected, `UserSecurityEvent`.
- Provider verification ID/reference may be stored; raw identity document/biometric payload must not be copied into Identity domain records.
- Processed provider-event truth must be owner-specific even when dedupe mechanics are shared.

### Public Interfaces

- `initiateAccountRecovery`.
- `getAccountRecoveryStatus`.
- `cancelAccountRecovery`.
- Internal verified-provider result application command.
- `completeAccountRecovery` / manual-review command once policy approves it.

### Logic

- Create one bounded recovery request with purpose and expiry.
- Send minimized input to the recovery provider.
- Verify/dedupe callback before mapping provider result.
- Apply only legal state transitions; provider success does not bypass local policy.
- On completion, atomically update approved phone/security facts, revoke or re-evaluate affected security sessions/methods, and append security history.

### UI / Administrative Surface

- Recovery initiation/status/verification return flow.
- Manual-review administrative surface only if the final review owner/policy is approved.
- Never display provider raw identity artifacts.

### Authorization / Compliance

- Recovery entry points use purpose-bound tokens/provider sessions and strict rate limits.
- Normal logged-in recovery actions still use Role authorization.
- Consent proof, if required, is queried from Consent and does not prove identity-provider success.
- Sensitive administrative review is audited.

### Events / Jobs / Integrations

- Recovery identity-verification adapter and callback route.
- Expiry/reconciliation worker through shared queue.
- Security-change notification requests.
- Ops failure records for provider/webhook/reconciliation problems.

### Failure Behavior

- Forged callback → reject with zero domain side effects.
- Duplicate callback → prior result.
- Provider success for an expired/cancelled request → ignored/reviewed according to transition policy.
- Provider unavailable → recovery remains pending/retryable; never auto-complete.
- Ambiguous/manual-review result → explicit review state, not a generic ComplianceHold substitute.

### Tests

- Recovery transition matrix tests.
- Signature, dedupe, replay, out-of-order callback tests.
- Phone/security mutation integration tests.
- Privacy/minimized-provider-input tests.
- Security event vs Audit/Ops separation tests.
- E2E recovery with provider fixtures.

### Out of Scope

- General KYC or payout verification.
- Trust screening.
- Privacy request orchestration.
- Generic manual-review/hold lifecycle.

### Exit Gate

- Recovery can only complete through verified, deduped provider input and approved transition rules.
- Replay/forgery cannot duplicate or bypass completion.
- Successful recovery leaves coherent security state and immutable security history.
- No raw recovery-provider sensitive payload is persisted or logged.
- Live production activation remains off until U-CL01-08/U-CL01-09 and any required consent/retention decisions are resolved.


---

## Phase 2 — Buyer Actor and Consent Proof

### 06 Default CustomerProfile Provisioning and Buyer Actor Resolution

Create the customer-side actor branch so consumer marketplace workflows can resolve a buyer identity without overloading `User`.

### Objective

Make `CustomerProfile` the source-owned buyer actor and provide idempotent provisioning/resolution from an authenticated User.

### User-visible / Observable Result

- An eligible User can obtain exactly one `CustomerProfile`.
- SH-004 `resolveCustomerActor` returns the buyer actor or an explicit unavailable/ineligible result.
- Repeated User-provisioned events or commands do not create duplicate profiles.
- Downstream contract fixtures can consume `customerProfileId` without reading CustomerProfile tables directly.

### Owning Module(s)

- **Customer / Buyer Profile** owns CustomerProfile provisioning and buyer actor truth; Identity owns only the base User.

### Dependencies

- Features 01–02.
- `CustomerProfile` with unique `userId`.
- User-provisioned event or on-demand provisioning trigger.
- Resolve U-CL01-18 before final production provisioning wiring and U-CL01-21 before enabling lifecycle states beyond the conservative existing path; U-CL01-19 controls full downstream cutover, not basic profile creation.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` — Identity supplies User actor.
- SH-002 `authorizeResourceAction` — Customer self/admin actions.
- SH-004 `resolveCustomerActor` — Customer-owned canonical public interface; consumers must not recreate buyer identity.
- SH-044 `executeIdempotentCommand` — provisioning replay safety.
- SH-046 `publishDomainEvent` — publish minimized CustomerProfile-created/status integration events through the outbox where consumers require them. Any separately approved Customer lifecycle-history requirement uses SH-031 `appendDomainLifecycleEvent`; neither operation substitutes for the other, and this feature does not approve a new Customer history model.
- SH-011 `evaluateComplianceHold` only for actions explicitly gated by a hold; Customer does not own generic blocked truth.

### Data / Schema

- `CustomerProfile`; unique `userId` invariant.
- Use `ProfileStatus` according to approved Customer transition policy; do not infer ownership of the shared enum from convenience.
- Do not copy subscription, order, gig, booking, verification, or privacy lifecycle fields into CustomerProfile.

### Public Interfaces

- `provisionCustomerProfile`.
- SH-004 `resolveCustomerActor`.
- `getCustomerProfile` safe owner/admin view.
- Minimized `CustomerProfileCreated` event if consumers need asynchronous reaction.

### Logic

- Provision on approved trigger or on first customer action, idempotently.
- Ensure exactly one CustomerProfile per User.
- Return actor identity as a typed Customer contract, not a broad Prisma record.
- Do not make User fields buyer-domain truth after consumer cutover.

### UI / Administrative Surface

- Minimal customer profile/account shell may display buyer profile state.
- No public directory/search surface.

### Authorization / Compliance

- Self reads/provisioning use actor identity plus Role policy.
- Admin/support behavior is explicit and audited where sensitive.
- Profile creation does not imply entitlement, seller readiness, or business authorization.

### Events / Jobs / Integrations

- Consume minimized User-provisioned event if event-driven provisioning is selected.
- Emit CustomerProfile-created event/outbox only if consumers require it.
- No external provider required.

### Failure Behavior

- Duplicate trigger → existing profile returned.
- Missing/invalid User → no profile.
- Concurrent provisioning → unique constraint + idempotent replay resolves to one profile.
- Unresolved status/cutover case → fail closed rather than invent transition.

### Tests

- One-to-one database/concurrency tests.
- SH-004 `resolveCustomerActor` contract tests.
- Authorization tests.
- User event replay tests.
- Negative test proving no Customer code writes User auth fields or Track state.

### Out of Scope

- Public search/visibility.
- Buyer Orders/Gigs/Bookings themselves.
- Subscriptions/entitlements.
- Profile transition semantics not yet approved.

### Exit Gate

- Exactly one CustomerProfile can exist per User under concurrent/replayed provisioning.
- SH-004 `resolveCustomerActor` is usable by contract fixtures without direct Customer table reads.
- No consumer lifecycle is copied into CustomerProfile.
- No public search projection is emitted.
- Tests/typecheck/lint/build pass and U-CL01-18/U-CL01-19/U-CL01-21 gates remain explicit.


---

### 07 CustomerProfile Maintenance, Status-Safe Access, and Media Boundary

Implement authorized CustomerProfile editing and avatar attachment while keeping lifecycle, location, MediaAsset, and public-visibility boundaries explicit.

### Objective

Allow safe CustomerProfile maintenance without turning Customer into an auth, file-storage, exact-location, or public-search Module.

### User-visible / Observable Result

- An owner/admin can edit approved customer display/profile fields.
- Avatar assignment is rejected unless Media confirms the asset is valid and attachable.
- Unauthorized or stale writes are rejected.
- Private/admin views redact fields according to policy and no public profile directory exists.

### Owning Module(s)

- **Customer / Buyer Profile** owns profile fields and avatar business relation.
- **Media / File Access** retains file validation/storage/signed-access mechanics.
- Location Safety retains exact-location truth; Search retains projection mechanics.

### Dependencies

- Feature 06 and Feature 02.
- Media attachment validation/safe-access contract.
- Resolve U-CL01-22/U-CL01-21 for display-field precedence and status semantics before enabling disputed fields/transitions.
- U-CL01-22/public visibility remains unresolved; public search stays disabled.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` and SH-002 `authorizeResourceAction` — owner/admin edit/read gates.
- SH-044 `executeIdempotentCommand` — mutation replay safety where external retries are possible.
- SH-029 `appendAuditEvent` / SH-030 `recordSensitiveAccess` — sensitive admin reads/changes as policy requires.
- SH-011 `evaluateComplianceHold` only for specifically approved blocked profile actions; do not create local generic block flags.

### Data / Schema

- `CustomerProfile` approved editable fields, `avatarMediaId`, status/archive fields only according to approved matrix.
- No direct ownership of `MediaAsset`; UUID/reference validity is checked through Media.
- Coarse display location may remain profile presentation data; exact location/reveal proof must not be introduced here.

### Public Interfaces

- `updateCustomerProfile`.
- `setCustomerProfileAvatar` / `clearCustomerProfileAvatar`.
- Safe owner/admin profile selectors.
- Media attachment validation contract consumption.

### Logic

- Validate allowlisted fields, normalization, length, expected version/concurrency policy.
- Check Media readiness/ownership/attachability before persisting avatar relation.
- Use Customer status transition service only for explicitly approved transitions.
- Never synchronize duplicated User/Customer display fields implicitly until precedence policy is approved.

### UI / Administrative Surface

- Customer profile edit form.
- Avatar upload/select flow routes through Media mechanics.
- Safe self/admin view.
- No public profile search or directory.

### Authorization / Compliance

- Owner/admin policy via Role.
- Sensitive admin reads request access audit where required.
- Public field exposure is not assumed from presence in CustomerProfile.
- Exact location remains separately gated.

### Events / Jobs / Integrations

- Customer profile-updated/status event only when a consumer requires it.
- Media removal/restriction event may cause Customer to clear/suppress avatar relation.
- No Customer-owned file processing job.

### Failure Behavior

- Unauthorized edit → denied.
- Stale expected version → conflict.
- Invalid/unready MediaAsset → validation denial.
- Media unavailable → avatar change unavailable; independent profile mutation behavior follows explicit transaction design.
- Unresolved public/status behavior → not supported/fail closed.

### Tests

- Owner/admin/other-user access matrix.
- Field validation and optimistic/concurrency tests.
- Media contract tests and no-direct-storage test.
- Location/private-field redaction tests.
- Negative search-indexing test.

### Out of Scope

- Public profile/search.
- Media scanning/storage/presigning.
- User↔CustomerProfile automatic field synchronization.
- Order/history aggregation.
- Unapproved status transitions.

### Exit Gate

- Approved fields are editable only by authorized actors.
- Avatar attachment cannot bypass Media validation and Customer contains no file scanner/storage/signed-URL implementation.
- No public Search projection is emitted.
- Unresolved display/status precedence is documented rather than silently implemented.
- Tests/typecheck/lint/build pass.


---

### 08 Exact Version Consent Acceptance and Proof Query

Implement the current-schema consent foundation: durable acceptance of an exact `ConsentType` + version and one canonical proof query.

### Objective

Make `ConsentLog` the durable exact-version acceptance proof and eliminate feature-local consent booleans/tables for supported consent types.

### User-visible / Observable Result

- A signed-in User can accept an explicitly supplied consent type/version.
- A consumer can query whether that exact required version was accepted and receives a proof reference/evidence summary.
- Missing/wrong versions fail cleanly.
- Retries do not create uncontrolled duplicate acceptance rows under the approved command-idempotency behavior.

### Owning Module(s)

- **Consent & Disclosure** owns `ConsentLog` acceptance proof; consumers own the downstream action for which proof is requested.

### Dependencies

- Features 01–02.
- `ConsentLog`, `ConsentType`.
- Canonical request metadata hashing/sanitization.
- Resolve U-CL01-14 before relying on a database-level uniqueness rule; command idempotency may protect the initial slice without inventing a schema uniqueness contract.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` and SH-002 `authorizeResourceAction` — acceptance/history/admin access gates.
- SH-007 `recordConsentProof` — Consent-owned canonical command. Local policy: exact type/version/evidence fields. Do not build feature-local consent write services.
- SH-008 `queryConsentProof` — Consent-owned canonical query. Local policy: exact accepted type/version semantics. Do not build feature-local consent booleans or proof queries.
- SH-044 `executeIdempotentCommand` — acceptance replay protection.
- SH-076 `normalizeAndHashIdentifier` — request evidence where an approved privacy-minimized hash is required.
- SH-029 `appendAuditEvent` only for material admin operations; ConsentLog remains the acceptance proof.

### Data / Schema

- `ConsentLog`: userId, type, version, acceptedAt, privacy-minimized request evidence such as ipHash/userAgent under policy.
- `ConsentType` remains the controlled vocabulary.
- No generic `accepted=true` field is added to User/Profile/subscription records.
- Do not add content/version-catalog fields here until Feature 09 resolves the catalog architecture.

### Public Interfaces

- SH-007 `recordConsentProof`.
- SH-008 `queryConsentProof`.
- Authorized consent-history query with safe pagination.

### Logic

- Accept only an explicit controlled consent type and nonempty version.
- Record immutable acceptance proof with minimized provenance.
- Query by subject + type + required version; do not treat acceptance of an older/different version as current.
- Return proof/evidence, not a downstream permission decision.

### UI / Administrative Surface

- Reusable consent acceptance surface may render supplied version/text reference.
- Account consent-history view may show safe type/version/acceptedAt metadata.
- No browser/device permission UI is treated as ConsentLog truth unless a specific domain contract says so.

### Authorization / Compliance

- User accepts only for self except explicit legal/admin migrations.
- History/admin access goes through Role and sensitive-access policy.
- Consent does not bypass Role, hold, entitlement, readiness, or provider-state gates.

### Events / Jobs / Integrations

- Consent-recorded domain/integration event only where a consumer explicitly requires re-evaluation.
- No external provider required.
- Notification request only for policy-defined disclosure events.

### Failure Behavior

- Unknown type/version → validation denial.
- Unauthenticated actor → denied.
- Duplicate retry → prior semantic success/no uncontrolled duplicate.
- Storage failure → no claimed proof.
- Query for absent/wrong version → explicit not-accepted result.

### Tests

- Acceptance validation/idempotency tests.
- Exact version query contract tests.
- Wrong-version/no-proof negatives.
- Authorization/history-access tests.
- Evidence minimization/redaction tests.
- Negative test proving consumer permission is not returned by Consent.

### Out of Scope

- Active consent text/version catalog.
- Withdrawal/re-consent policy.
- Subscription/verification/calendar/provider lifecycle.
- Browser push/browser permission truth.

### Exit Gate

- Exact type/version acceptance produces durable ConsentLog proof.
- SH-008 `queryConsentProof` is the canonical consumer path and wrong/missing versions cannot pass.
- No new local consent booleans/tables are introduced.
- Command replay is safe under the approved current decision.
- Tests/typecheck/lint/build pass.


---

### 09 Consent Version Catalog, Standalone Presentation, and Retention Contract

Complete the consent capability needed for production version resolution, standalone disclosure presentation, and re-consent signaling while preserving retention gates. The Consent Privacy owner/executor bridge is implemented with Feature 16.

### Objective

Give Consent a persistent, versioned disclosure catalog and retention-aware presentation/proof behavior without letting it own downstream permission or Privacy orchestration.

### User-visible / Observable Result

- A consumer can resolve the active version for a consent type/context and present the exact approved text/metadata.
- Changing the active version does not mutate historical ConsentLog proof.
- Consumers can detect that a newer required version lacks acceptance.

### Owning Module(s)

- **Consent & Disclosure** owns disclosure-version catalog and acceptance proof.
- **Privacy / Data Erasure** owns request/job/target/exemption orchestration.
- Consumer Modules still own whether the proof is required for their action.

### Dependencies

- Feature 08.
- Resolve U-CL01-13, U-CL01-16, and U-CL01-17 where required by enabled active-version/re-consent/proof-binding behavior. U-CL01-15 remains the destructive-retention blocker; the executor is coordinated in Feature 16.
- Notification contract for approved re-consent requests. Privacy target-executor integration belongs to Feature 16.

### Shared Operations Used

- SH-009 `resolveActiveConsentVersion` — Consent-owned canonical query over approved version catalog. Do not let consumers hardcode active versions.
- SH-010 `presentStandaloneConsent` — Consent-owned presentation contract; consumers may embed it without copying text/version policy.
- SH-008 `queryConsentProof` / SH-007 `recordConsentProof` — exact proof mechanisms from Feature 08.
- SH-080 `manageVersionedRules` — shared versioning mechanism if used for immutable effective intervals; Consent policy/text remains Consent-owned.
- SH-041 `requestNotification` — re-consent/disclosure notification intent only.

### Data / Schema

- Add the approved immutable consent-version/content record from U-CL01-13 with type, version, content/hash/reference, status/effective interval, locale/jurisdiction/context as required, provenance, and retirement semantics.
- Historical `ConsentLog` rows remain immutable proof and reference the exact version logically or relationally according to the approved design.
- Resolve `onDelete: Cascade`/retention behavior before destructive Privacy execution.
- No downstream feature status is copied into Consent.

### Public Interfaces

- SH-009 `resolveActiveConsentVersion`.
- SH-010 `presentStandaloneConsent`.
- `listConsentVersions` admin query.
- `publishConsentVersion` / `retireConsentVersion` under approved policy.

### Logic

- Publish immutable version records; do not edit accepted disclosure content in place.
- Resolve active version deterministically by type/context/effective date.
- Compare required version with exact acceptance proof; a new version creates a missing-proof condition, not automatic acceptance.

### UI / Administrative Surface

- Standalone disclosure page/sheet and acceptance surface.
- Restricted admin version catalog/publish/retire UI if required.
- Account consent history/re-consent prompt driven by public interfaces.

### Authorization / Compliance

- Publish/retire is admin-authorized and audited.
- Consumer action owner decides whether proof is mandatory.
- Privacy deletion/anonymization occurs only through Privacy-owned target instruction and retention decision.
- Consent proof itself never grants organization/resource/business access.

### Events / Jobs / Integrations

- Consent-version-published/re-consent-needed events if consumers require re-evaluation.
- Notification requests for required re-consent.

### Failure Behavior

- No active version → unavailable/fail closed for workflows that require one.
- Overlapping active intervals or duplicate version → constraint/validation failure.
- Notification failure → consent truth remains correct; delivery retries independently.

### Tests

- Version effective-date resolution tests.
- Immutable historical content/proof tests.
- Re-consent detection tests.
- Admin authorization/audit tests.
- Catalog changes preserve retained historical proof; Privacy executor/retention/cascade integration tests belong to Feature 16.
- Contract tests proving consumers cannot infer permission from Consent.

### Out of Scope

- Feature-specific contextual consent records owned elsewhere.
- Provider authorization state.
- Privacy request orchestration and Consent subject-data enumeration/execution implementation (the owner executor is delivered in Feature 16).
- Notification delivery mechanics.

### Exit Gate

- Active version can be resolved and presented without consumer hardcoding.
- Historical proof remains immutable across catalog changes.
- Re-consent need is detectable without changing downstream lifecycle truth.
- All U-CL01-13/U-CL01-16/U-CL01-17 decisions required by enabled behavior are resolved and tests/build pass. U-CL01-15 still blocks destructive behavior; this exit does not require the Feature 16 executor.


---

## Phase 3 — Commercial Track Policy Rail

### 10 Track Catalog and Free-Track Foundation

Establish the source-owned commercial catalog and deterministic baseline track state for customer, candidate, and professional actors without enabling unresolved paid-provider behavior.

### Objective

Make Track plan, pricing, and entitlement definitions an admin-controlled source of commercial policy and establish the approved representation of baseline/free track access.

### User-visible / Observable Result

- Authorized administrators can create/read approved Track plan and entitlement catalog records under immutable/effective-date rules.
- A customer/candidate/professional actor can resolve which baseline plan/catalog applies without a feature-local premium flag.
- Invalid mixed-track or malformed typed entitlement definitions are rejected.
- Paid-provider side effects remain disabled until later architecture gates are satisfied.

### Owning Module(s)

- **Track Subscription & Entitlement** owns Track catalog, plan pricing, entitlement definitions/mappings, and baseline track policy.

### Dependencies

- Features 01–02; Feature 06 for customer actor fixtures; candidate/professional actor contracts may be fixtures.
- `TrackPlan`, `TrackPlanPrice`, `TrackEntitlementDefinition`, `TrackPlanEntitlement` and related enums.
- Resolve U-CL01-24 and U-CL01-26 before production catalog activation where free-plan representation or value typing depends on them; U-CL01-27 is required for mutable live plan revision policy.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` and SH-002 `authorizeResourceAction` — admin catalog mutation and safe read gates.
- SH-080 `manageVersionedRules` — shared versioning mechanism if adopted for immutable/effective catalog versions; Track owns commercial meaning.
- SH-044 `executeIdempotentCommand` — admin mutation replay safety.
- SH-029 `appendAuditEvent` — material catalog publication/retirement proof; audit is not plan truth.
- SH-031 `appendDomainLifecycleEvent` — Track-owned plan/catalog lifecycle history when the domain requires it.

### Data / Schema

- `TrackPlan`, `TrackPlanStatus`, `TrackBillingModel`, `TrackPlanPrice`, `TrackBillingProvider`.
- `TrackEntitlementDefinition`, value-type enum, and `TrackPlanEntitlement`.
- Add/adjust constraints only after approved decisions: unique keys/scopes, effective intervals, exactly one valid typed value representation, immutable published version behavior.
- Do not add `premium` or feature-specific booleans to CustomerProfile/CandidateProfile/ProfessionalProfile.

### Public Interfaces

- `listTrackPlans` / `getTrackPlan` safe query.
- `resolveBaselineTrackPlan`.
- `assignDefaultFreeTrack` — Track-owned, implemented by Track plan slice 02A only after the existing free-representation gate is resolved.
- Admin `createTrackPlanVersion`, `publishTrackPlanVersion`, `retireTrackPlanVersion` or approved equivalents.
- `getEntitlementDefinition` / catalog query.

### Logic

- Validate plan track, billing model, price/provider compatibility, and entitlement value type.
- Keep draft/published/retired semantics explicit; do not overwrite historical published commercial terms in place.
- Resolve baseline/free access according to U-CL01-24 rather than inventing implicit absence semantics.
- Coordinate Track implementation slice 02A for `assignDefaultFreeTrack` after the approved actor-created handoff. The slice covers trigger integration, replay/concurrency safety, tests, and its production exit; profile provisioning does not depend on Track assignment. U-CL01-24 and any applicable integrity/precedence/history decisions remain unresolved gates.
- Separate catalog definition from actor subscription/grant state.

### UI / Administrative Surface

- Restricted admin catalog view/editor where an admin surface exists.
- Account-facing plan listing may read public-safe catalog fields only.
- No checkout UI in this feature.

### Authorization / Compliance

- Catalog mutations require explicit admin authority and audit.
- Catalog read exposure is allowlisted and does not reveal provider secrets/internal configuration.
- Plan existence never overrides holds, consent, readiness, or destination permissions.

### Events / Jobs / Integrations

- Plan/catalog published/retired event only when consumers need cache/re-evaluation.
- No live billing provider call.
- Optional catalog backfill/revalidation job uses shared queue if migration requires it.

### Failure Behavior

- Invalid typed value/billing-model combination → validation denial.
- Conflicting active version/effective interval → constraint failure.
- Unresolved free-plan semantics → no silent default; keep affected actor resolution unavailable.
- Audit/notification side-effect failure does not mutate catalog result after committed source truth; retry via outbox where required.

### Tests

- Catalog domain validation tests.
- Typed entitlement value and effective-date tests.
- Admin authorization/audit tests.
- Migration/constraint tests.
- Negative scans for local premium flags in covered consumers.
- Contract tests for baseline plan resolution.

### Out of Scope

- Paid subscription lifecycle.
- Actor-specific manual grants.
- Metered usage.
- Order/Booking/Application business snapshots.

### Exit Gate

- Approved catalog records can be created/read only through Track interfaces.
- Baseline/free-track behavior is explicit for enabled tracks and no local premium boolean is introduced. Claiming production default assignment requires Track slice 02A's approved handoff, idempotency/concurrency tests, and exit gate; unresolved representation keeps assignment disabled.
- Published commercial terms obey the approved mutability/version rule.
- Invalid typed entitlement representations fail.
- Required U-CL01-24/26/27 decisions for enabled behavior are resolved; tests/typecheck/lint/build pass.


---

### 11 Effective Entitlement Resolution and Grant Materialization

Implement the canonical Track decision that resolves plan mappings and explicit grants into one effective entitlement result with deterministic evidence and precedence.

### Objective

Make SH-005 `resolveEntitlement` the only source for current feature/quota/waiver/boost/commission/priority/perk policy across customer, candidate, and professional tracks.

### User-visible / Observable Result

- A consumer fixture can ask for an entitlement key for an actor/track/context and receive a typed effective value, reason, effective window, and evidence references.
- Manual/comped/subscription-derived grants are visible according to approved precedence.
- Expired/suspended/revoked grants do not remain effective.
- Changing Track truth can emit a re-evaluation/projection event without mutating consumer business records.

### Owning Module(s)

- **Track Subscription & Entitlement** owns current entitlement decision and grant truth; consumers own the business consequence.

### Dependencies

- Feature 10.
- `TrackEntitlementGrant`, definition/mapping records, profile/track linkage.
- Resolve U-CL01-26 grant precedence and typed-value constraints before production resolution across competing sources; U-CL01-25 governs actor/profile and active-subscription constraints.
- ComplianceHold contract for any explicitly hold-gated Track administrative action.

### Shared Operations Used

- SH-005 `resolveEntitlement` — Track-owned canonical commercial-policy query. Local policy: precedence/effective-date/value semantics. Do not create local entitlement evaluators in consumers.
- SH-044 `executeIdempotentCommand` — grant creation/revocation replay protection.
- SH-002 `authorizeResourceAction` — admin/self actions around grants where permitted.
- SH-011 `evaluateComplianceHold` — only for approved Track actions; a hold does not become grant status.
- SH-031 `appendDomainLifecycleEvent` and SH-029 `appendAuditEvent` — Track grant history vs generic administrative audit remain separate.
- SH-091 `requestSearchProjectionRefresh` / Search public interface when an effective boost changes; Track never writes the search index.

### Data / Schema

- `TrackEntitlementGrant`, status/source/effective dates; Track plan entitlement mappings and definitions.
- Enforce profile/track consistency in application and database where approved.
- Store evidence/source references and reason codes sufficient to explain the effective decision.
- Do not persist consumer-specific historical business snapshots in Track.

### Public Interfaces

- SH-005 `resolveEntitlement`.
- `listEffectiveEntitlements` where a bounded account summary is needed.
- `grantEntitlement`, `revokeEntitlement`, `suspendEntitlement` admin/manual operations under policy.
- `resolveTrackPolicySnapshot` only if consumers need a typed bundle rather than repeated per-key calls.

### Logic

- Validate actor/profile belongs to the requested AccountTrack.
- Gather active plan mapping plus explicit grants.
- Apply deterministic approved precedence and effective windows.
- Return typed decision/value + reason/evidence; do not perform the consumer action.
- Emit change events only when effective policy changes or a consumer explicitly needs invalidation.

### UI / Administrative Surface

- Account plan/entitlement summary may display current effective benefits.
- Restricted admin grant inspection/manual grant surface.
- Destination UIs remain responsible for their own denial/availability presentation.

### Authorization / Compliance

- Self may query only own safe entitlement summary; admin grant mutations require Role authorization and audit.
- Entitlement does not override ComplianceHold, consent, professional/candidate readiness, or destination authorization.
- Manual grants must have explicit reason/source/expiry as required by policy.

### Events / Jobs / Integrations

- Track entitlement/grant change domain events.
- Search refresh request for search-boost changes.
- Notification requests for policy-defined grant/subscription changes.
- No direct Typesense, Booking, Order, or Application writes.

### Failure Behavior

- Unknown entitlement key/type → explicit unsupported result.
- Ambiguous competing grants while precedence unresolved → fail closed/review, not arbitrary selection.
- Expired/revoked grant → not effective.
- Search/notification failure → Track truth remains committed; side effect retries independently.

### Tests

- Precedence/effective-window unit matrix.
- Typed output contract tests.
- Profile/track consistency tests.
- Concurrent grant mutation/idempotency tests.
- Search refresh ownership test.
- Negative consumer scan: no local premium/waiver/boost truth for covered bridges.

### Out of Scope

- Metered consumption.
- Paid subscription provider processing.
- Order/Booking/Application lifecycle or historical snapshots.
- Search execution.

### Exit Gate

- SH-005 `resolveEntitlement` deterministically returns typed value, reason, and evidence for all enabled keys.
- Expired/revoked/inconsistent grants cannot resolve as active.
- No enabled consumer needs a local entitlement evaluator or premium boolean.
- Search change is requested, never executed, by Track.
- U-CL01-26 decisions required by enabled precedence/value behavior and U-CL01-25 decisions required by enabled actor/subscription constraints are resolved and tests/build pass.


---

### 12 Atomic Metered Entitlement Usage and Counter Projection

Implement immutable usage proof plus an atomically enforced rebuildable counter for limited entitlements such as candidate application quotas.

### Objective

Make SH-006 `consumeMeteredEntitlement` the single atomic mechanism for limited commercial entitlement usage while letting the source business Module decide when its event actually counts.

### User-visible / Observable Result

- A consumer fixture can atomically attempt to consume a quota and receive permitted/denied + usage receipt.
- Concurrent attempts cannot exceed the approved limit.
- Retrying the same business event returns the same semantic result and does not double-count.
- Usage counters can be rebuilt from immutable events and reconcile to the same total.

### Owning Module(s)

- **Track Subscription & Entitlement** owns usage periods, `TrackUsageEvent`, `TrackUsageCounter`, and consumption receipt.
- The consumer Module owns the source business event and defines the commit point at which usage counts.

### Dependencies

- Features 10–11.
- `TrackUsageEvent`, `TrackUsageCounter`, usage type/period enums.
- Database-backed locking/idempotency primitives.
- Resolve U-CL01-29 application-limit period/timezone/refund/reversal semantics before production candidate application metering.

### Shared Operations Used

- SH-006 `consumeMeteredEntitlement` — Track canonical capability; local policy: period/limit/reversal rules. Do not build feature-specific counters.
- SH-044 `executeIdempotentCommand` — keyed by consumer business event + entitlement consumption intent.
- SH-051 `acquireAggregateLock` or approved DB concurrency primitive — lock the entitlement/subject/period aggregate; do not use in-memory locks.
- SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` — counter rebuild/reconciliation jobs only.
- SH-031 `appendDomainLifecycleEvent` — immutable usage event is Track truth; generic AuditEvent remains separate.

### Data / Schema

- `TrackUsageEvent` is append-only immutable usage proof with idempotency/business reference.
- `TrackUsageCounter` is a projection with approved unique aggregate key.
- Add missing unique/idempotency constraints and period key semantics only after U-CL01-29 is settled.
- Counter must be rebuildable by replaying source usage events; do not make the mutable counter sole truth.

### Public Interfaces

- SH-006 `consumeMeteredEntitlement`.
- `getMeteredEntitlementUsage`.
- `rebuildUsageCounter` / reconciliation worker contract.
- Optional reversal/adjustment command only after refund/reversal policy is approved; never mutate/delete original usage proof.

### Logic

- Resolve current entitlement/limit for the subject and period.
- Within one transaction/lock, check prior idempotent receipt, current aggregate usage, and requested quantity.
- If permitted, append immutable usage event and update/recompute counter projection.
- Return receipt with period, quantity, resulting usage, limit, and evidence.
- Consumer commits its own business event according to an explicit transaction/saga contract; Track does not create JobApplication/Order/etc.

### UI / Administrative Surface

- No CL-01 UI required beyond optional account/admin usage summary.
- Consumer UI owns quota-denial/business-state presentation.

### Authorization / Compliance

- Consumer-to-Track command is a trusted internal contract tied to authenticated/authorized source workflow.
- Admin adjustments require explicit authority/audit.
- Quota entitlement never grants underlying business permission by itself.

### Events / Jobs / Integrations

- Usage-consumed event only if a consumer/projection needs it.
- Scheduled/triggered counter reconciliation through shared queue.
- Operational discrepancy reporting through Ops.

### Failure Behavior

- Limit exceeded → deterministic denial with no usage event.
- Duplicate idempotency key → return prior receipt.
- Concurrent last-slot attempts → at most approved quantity succeeds.
- Projection update failure inside transaction → rollback; replay safe.
- Reconciliation mismatch → Ops alert/repair report; immutable events remain truth.

### Tests

- High-contention concurrency tests.
- Idempotency/replay tests.
- Period-boundary and timezone tests after policy approval.
- Counter rebuild/reconciliation tests.
- Consumer contract test proving source business Module controls count point.
- Negative test proving counters are not stored in consumer feature tables.

### Out of Scope

- Candidate application lifecycle.
- Refund/reversal behavior until approved.
- Paid subscription state transition.
- Generic analytics counters.

### Exit Gate

- Concurrent consumption cannot exceed the configured limit.
- Same business event cannot double-count under retry.
- `TrackUsageCounter` rebuilds exactly from immutable TrackUsageEvent evidence.
- No consumer owns a competing quota counter.
- U-CL01-29 required period/reversal semantics are resolved for any production-enabled usage type; tests/build pass.


---

### 13 Paid Track Subscription Lifecycle and Stripe Billing Adapter

Implement paid enrollment/change/cancel and verified Stripe Billing event processing only after the Track lifecycle, consent, provider-dedupe, and retention decisions are explicitly approved.

### Objective

Turn verified provider billing results into authoritative `TrackSubscription` and grant transitions without turning Stripe into Workin Ants commercial truth or moving general financial ownership into Track.

### User-visible / Observable Result

- An authorized user can initiate approved plan checkout/change/cancel.
- Redirect/success UI does not activate a subscription without owner-approved provider/domain confirmation.
- A verified, deduped provider event changes TrackSubscription only through the Track transition service.
- Forged, duplicate, unknown, and out-of-order provider events cannot silently corrupt subscription/grant state.
- Current entitlement results change consistently with the approved subscription transition.

### Owning Module(s)

- **Track Subscription & Entitlement** owns subscription/grant lifecycle and Stripe Billing subscription status translation under PR-CL01-04.
- Payment / Payout / Tax retains general Order payment, money movement, payout, tax, processor ledger, and financial readiness truth.
- Shared provider-webhook infrastructure owns generic verification/dedupe mechanisms, not Track event truth.

### Dependencies

- Features 08–12.
- Mandatory gates before live domain mutation: U-CL01-24 through U-CL01-28, U-CL01-32, plus any billing-retention/consent binding decisions named in architecture.
- Stripe Billing/Checkout/Portal provider-neutral port.
- Consent proof, hold, step-up, notification, audit, Ops, Search contracts.
- Provider adapter can be tested before these gates; live callback-to-domain transition must remain disabled until they are resolved.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` and SH-002 `authorizeResourceAction` — subscriber/admin action gates.
- SH-008 `queryConsentProof` / SH-009 `resolveActiveConsentVersion` — exact subscription/recurring-billing/plan-change proof where required; Track does not own consent proof.
- SH-014 `requireStepUpForSensitiveAction` — only for approved subscription actions requiring recent assurance.
- SH-011 `evaluateComplianceHold` — block/review relevant plan actions according to policy.
- SH-064 `authorizeExternalProviderConnection` — Confirmed; provider-owning Module boundary for hosted checkout/portal initiation, including state/nonce, redirect allowlists, scoped permissions, callback validation, and provider-reference lifecycle. Track retains plan/price selection, commercial eligibility, provider-specific translation, and subscription policy.
- SH-059 `verifyProviderWebhookSignature` — shared ingress shell; do not build Track-local signature utility.
- SH-060 `deduplicateProviderEvent` — shared mechanism + Track-specific processed-event truth.
- SH-061 `translateProviderStatus` — Track adapter maps provider states to approved domain transition inputs.
- SH-044 `executeIdempotentCommand` / DB aggregate lock — concurrent command/provider safety.
- SH-041 `requestNotification`, SH-029 `appendAuditEvent`, SH-037 `recordIntegrationFailure`, SH-047 `enqueueReliableJob` — canonical support effects/reconciliation.

### Data / Schema

- `TrackSubscription`, `TrackSubscriptionStatus`, `TrackEntitlementGrant`, `TrackSubscriptionEvent`.
- Plan/price/provider references and immutable consent proof reference/snapshot according to approved binding.
- Owner-specific processed Stripe Billing event record from U-CL01-28; generic Payment `ProcessedStripeEvent` must not be commandeered without an explicit shared partition ruling.
- Approved active-subscription uniqueness, plan revision/effective history, and grant materialization semantics.

### Public Interfaces

- `startTrackSubscriptionCheckout`.
- `changeTrackSubscriptionPlan`.
- `cancelTrackSubscription`.
- `getCurrentTrackSubscription`.
- Internal `applyVerifiedBillingEvent`.
- `reconcileTrackSubscriptionWithProvider` worker/admin command.
- Manual/comped grants remain separate explicit grant operations.

### Logic

- Validate target actor/track/plan and required consent before creating provider session.
- Provider session creation is an infrastructure result only; local subscription status changes via approved commands/events.
- Verify signature before parsing side effects; dedupe event before transition.
- Translate provider status through versioned adapter mapping; unknown values fail closed.
- Lock subscription aggregate, apply approved transition matrix, materialize/revoke/suspend grants, append `TrackSubscriptionEvent`, then publish outbox.
- Do not retroactively rewrite usage history or consumer historical business snapshots on downgrade/cancel.

### UI / Administrative Surface

- Plan selection/checkout initiation and subscription status/account page.
- Cancel/change actions with exact required terms.
- Safe past-due/incomplete/paused/cancelled states.
- Restricted provider/reconciliation inspection using safe references only.

### Authorization / Compliance

- User mutates only own track/profile subscription unless admin policy permits.
- Exact subscription terms/recurring billing/plan-change consent checked at approved points.
- Step-up/holds composed separately where required.
- Billing retention policy must be explicit before destructive privacy actions.

### Events / Jobs / Integrations

- Stripe Billing/Checkout/Portal adapter and webhook route.
- Subscription reconciliation worker and grant-expiration/effective-date jobs.
- Track subscription/grant domain events.
- Search refresh request when an effective candidate boost changes.
- Notification requests and audit/Ops effects through their owners.

### Failure Behavior

- Forged signature → reject with zero side effects.
- Duplicate event → prior idempotent result.
- Out-of-order event → transition/version policy handles or routes to review; never blind overwrite.
- Unknown provider status → unsupported/review; no invented domain status.
- Consent missing → checkout/change denied where required.
- Provider/local partial mismatch → reconciliation workflow; provider dashboard is not silently copied as truth.
- Notification/Search failure after Track commit → Track remains correct and side effect retries via outbox/queue.

### Tests

- Full approved subscription transition matrix.
- Signature/dedupe/replay/out-of-order provider tests.
- Consent/step-up/hold composition tests.
- Concurrent checkout/change/cancel tests.
- Grant materialization/revocation and entitlement-result tests.
- Provider reconciliation tests.
- Privacy retention fixture tests.
- E2E checkout/callback/account-status flow in provider sandbox/test mode.

### Out of Scope

- Order payments, payouts, taxes, KYC, refunds/chargebacks unrelated to subscription billing.
- Consumer business lifecycles or historical fee/commission snapshots.
- Organization subscription model unless separately approved.

### Exit Gate

- All mandatory subscription U-CL01 architecture gates used by live behavior are resolved and reflected in `architecture.md`.
- Track owns all TrackSubscription transitions through its approved user/admin commands, provider events, expiration processing, and reconciliation. Provider-originated transitions require verified/deduped provider input through SH-059/SH-060; that requirement does not make provider input the sole lifecycle trigger.
- Provider success page alone cannot activate a subscription.
- Track-specific processed-event truth is explicit and replay-safe.
- General financial ownership remains outside Track.
- Transition/provider/consent/concurrency/E2E tests plus typecheck/lint/build pass.


---

## Phase 4 — Cross-Cluster Contract Proof

### 14 Customer Actor Cutover Contracts for Commerce and Delivery

Prove that customer-side business Modules can use `CustomerProfile` as buyer actor truth through stable contracts without pulling Gig, Order, Booking, or delivery lifecycles into CL-01.

### Objective

Validate the CustomerProfile bridge to customer-demand, transaction, scheduling, media/delivery, messaging/presentation, and privacy consumers and define the migration/cutover behavior for legacy User-based buyer references.

### User-visible / Observable Result

- Contract fixtures for Gig/Order/Booking/Digital/Video can resolve the buyer through SH-004 `resolveCustomerActor`.
- New approved consumer records use `customerProfileId` according to the resolved cutover policy.
- Legacy references can be backfilled/reconciled without changing source business lifecycle ownership.
- CustomerProfile deletion/archive cannot silently destroy foreign business obligations.

### Owning Module(s)

- **Customer / Buyer Profile** owns buyer actor identity and its migration mapping.
- Destination Modules own Gig, Order, Booking, digital/video grant, messaging, review/dispute, and other business records.

### Dependencies

- Features 06–07.
- Destination public-interface/contract fixtures.
- Resolve U-CL01-19 before enforcing production cutover/backfill; U-CL01-21 governs Customer status behavior.
- Privacy and retention fact contracts for destructive scenarios.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor`, SH-002 `authorizeResourceAction`, SH-004 `resolveCustomerActor` — canonical actor/permission/buyer identity composition.
- SH-003 `queryOwnerFacts` (Proposed ruling) — destination owners return minimal obligation/participant facts; Customer must not query foreign repositories directly.
- SH-044 `executeIdempotentCommand` — backfill/cutover command replay protection.
- SH-047 `enqueueReliableJob` / retry primitives — large backfill/reconciliation only.
- SH-096 `enumerateSubjectData` / Privacy contract — Customer contributes its own records, not foreign lifecycle records.

### Data / Schema

- `CustomerProfile` plus approved foreign-key/reference additions in destination schemas owned by those destination Modules.
- Backfill mapping/progress is operational migration evidence, not a new Customer source-of-truth lifecycle.
- Retain User ID only where destination owner explicitly needs authentication/audit traceability; do not continue treating it as buyer-domain truth after cutover.
- No cascade from CustomerProfile should delete Order/Gig/Booking obligations unless destination architecture explicitly says so.

### Public Interfaces

- SH-004 `resolveCustomerActor` consumer contract.
- Customer-to-destination buyer-context DTO.
- Destination-specific owner-facts queries needed for safe archive/privacy decisions.
- Backfill/reconciliation report contract.

### Logic

- Resolve buyer identity centrally.
- Backfill legacy buyer references deterministically and idempotently according to approved mapping.
- Verify referential consistency without rewriting destination status/history.
- Preserve destination-owned historical actor snapshots where required.
- Do not auto-provision/mutate downstream business objects from Customer.

### UI / Administrative Surface

- No new CL-01 business UI required.
- Migration/admin reconciliation report may display counts/mismatches behind admin authority.
- Destination UIs adopt customer actor identifiers through their own features.

### Authorization / Compliance

- All bridge reads remain scoped to the destination action and actor.
- Customer actor identity does not imply permission to read/modify foreign business records.
- Sensitive migration/admin inspection is audited.

### Events / Jobs / Integrations

- CustomerProfile-created/status events may drive non-authoritative consumer reactions.
- Backfill/reconciliation jobs use shared queue.
- No destination lifecycle event is emitted by Customer on behalf of the destination.

### Failure Behavior

- Unmapped/ambiguous legacy User → explicit mismatch/manual remediation; never invent CustomerProfile mapping.
- Destination unavailable during backfill → retry/checkpoint; Customer truth remains unchanged.
- Foreign obligation blocks archive/erasure → return owner fact/retention outcome, not a local invented business status.
- Partial migration → resumable idempotent checkpoint/report.

### Tests

- Contract tests with Gig/Order/Booking/Digital/Video fixtures.
- Backfill idempotency and mismatch tests.
- Referential/cascade safety tests.
- Authorization boundary tests.
- Privacy/retention interaction tests.
- Negative test proving Customer cannot mutate destination lifecycle status.

### Out of Scope

- Implementation of destination full workflows.
- Public Customer search.
- Organization buyer identity.
- Rewriting historical destination events.

### Exit Gate

- Every enabled customer-side destination resolves buyer identity through the approved Customer contract.
- No destination requires a direct Customer repository read.
- Legacy migration/backfill is deterministic, resumable, and has zero unexplained mismatches for the approved scope.
- No foreign lifecycle ownership or destructive cascade has moved into Customer.
- U-CL01-19 is resolved before enforced production cutover; contract tests pass.


---

### 15 Track Consumer Policy Bridges and Historical Snapshot Boundaries

Prove the commercial policy rail across Order, Booking, Candidate Application, Professional Eligibility, Search, Video, and Digital Goods while keeping each destination's historical/business truth local.

### Objective

Validate current Track decisions and metered usage at real consumer boundaries and ensure consumers persist only the historical evidence/snapshot they own.

### User-visible / Observable Result

- Order fixtures can obtain buyer-fee/professional-commission policy and write their own historical snapshot.
- Booking fixtures can obtain priority policy without Track changing Booking status.
- Candidate Application fixtures atomically consume application quota and trigger Search refresh for boost changes without local counters/boost booleans.
- Professional Eligibility can compose current entitlement with its own readiness facts.
- Video/Digital fixtures resolve commercial entitlement without Track owning room/download access-grant lifecycle.

### Owning Module(s)

- **Track Subscription & Entitlement** owns current policy and usage proof.
- Order, Booking, Candidate Application, Professional Eligibility, Search, Video, and Digital Goods retain their own business/projection/access truth.

### Dependencies

- Features 10–13 as applicable.
- Destination public contract fixtures.
- Resolve U-CL01-29 application-limit semantics before production quota bridge, U-CL01-30 fee/commission snapshot rules before live Order pricing, and U-CL01-31 priority scheduling semantics before live Booking priority.
- Search projection-refresh public interface.

### Shared Operations Used

- SH-005 `resolveEntitlement` — current commercial decision for all nonmetered keys.
- SH-006 `consumeMeteredEntitlement` — atomic limited-use proof; destination decides when the source event counts.
- SH-001 `resolveAuthenticatedActor` / SH-002 `authorizeResourceAction` remain destination action gates; Track result never substitutes them.
- SH-091 `requestSearchProjectionRefresh` or Search public interface — request refresh only after boost truth changes; no direct index write.
- SH-044 `executeIdempotentCommand` — destination snapshot/consumption integration where retries cross Module boundaries.

### Data / Schema

- Track records remain Track-owned.
- Order persists approved immutable fee/commission/waiver evidence on Order-owned records.
- Booking persists only Booking-owned priority/result evidence if needed.
- Candidate Application persists its own application state; Track stores usage event/counter only.
- Search stores projection event/document; Track stores boost/grant truth.
- Video/Digital owners store their domain-specific grants; Track stores only commercial entitlement.

### Public Interfaces

- Typed Order commercial-policy quote/snapshot input.
- `evaluatePriorityScheduling` or typed entitlement result for Booking.
- Candidate application quota consume contract.
- Candidate search boost entitlement/refresh contract.
- `evaluateProfessionalSellingEntitlement` or SH-005 `resolveEntitlement` composition contract.
- `authorizeLiveStreaming` / generic digital entitlement query where approved, returning commercial decision only.

### Logic

- Destination supplies business context and asks Track for current policy.
- Track returns decision/evidence; destination decides and writes its own business state/snapshot.
- Later plan changes never retroactively recalculate historical destination records unless the destination architecture explicitly defines a new adjustment event.
- Metered consumer defines the exact business commit/count point.
- Search refresh occurs because source boost truth changed, but Search owns index execution.

### UI / Administrative Surface

- No central CL-01 consumer UI.
- Destination UIs display their own business result; account plan UI may display current Track policy separately.

### Authorization / Compliance

- Each destination still performs Role, hold, consent, readiness, and other action-specific gates.
- Entitlement never overrides safety/compliance/business eligibility.
- Historical snapshots must preserve reason/evidence needed for auditability without copying mutable Track state wholesale.

### Events / Jobs / Integrations

- Track entitlement/subscription/grant change events for cache/projection invalidation.
- Search refresh requests for boost changes.
- Destination outbox events remain destination-owned.
- No Track direct calls to Typesense, Booking provider, payment processor for Order, Video provider, or Media storage.

### Failure Behavior

- Track unavailable → destination fails/defers according to criticality; never fall back to stale local premium boolean.
- Entitlement denied → destination owns denial UX/business result.
- Destination snapshot transaction fails → destination retries; Track does not write its table.
- Search refresh fails → Track truth remains correct; Search retry/reconciliation handles projection.
- Quota race → Track atomic consume result controls count; destination must honor the receipt.

### Tests

- Order snapshot non-retroactivity contract.
- Booking priority boundary tests after U-CL01-31.
- Candidate concurrent quota consume integration.
- Search boost refresh ownership test.
- Professional readiness composition boundary.
- Video/Digital domain-grant separation tests.
- Repository/code scan for local premium/waiver/commission/quota/boost flags in enabled consumers.

### Out of Scope

- Destination full lifecycle implementations.
- Organization subscription track.
- Search ranking algorithm.
- Payment/payout/tax financial state.

### Exit Gate

- Every production-enabled consumer policy has a resolved architecture decision.
- Consumers use Track interfaces rather than direct Track tables/local flags.
- Historical snapshots remain destination-owned and non-retroactive under current-plan changes.
- Search owns index execution and Video/Digital owners retain grant lifecycle.
- All enabled bridge contract/integration tests pass.


---

### 16 Privacy, Holds, Audit, Notification, and Operational Support Bridges

Prove CL-01's cross-cutting support rails without duplicating them or allowing support records to replace Identity, Consent, Customer, or Track truth.

### Objective

Complete the major support contracts needed for legal/privacy execution, generic stopping, sensitive-access proof, user communications, and operational diagnosis.

### User-visible / Observable Result

- A Privacy-owned test job can enumerate and execute Identity, Consent, Customer, and Track targets independently.
- A ComplianceHold can block an approved CL-01 action without a local generic blocked flag.
- Material admin actions create `AuditEvent`; sensitive reads create `AccessAuditLog` where policy requires.
- Security/subscription/profile/consent notifications are requested through Notification only.
- Provider/worker failures appear in Ops while owner domain status remains unchanged unless the owner transition itself failed/succeeded.

### Owning Module(s)

- Each CL-01 data owner owns its own privacy executor and source records.
- Privacy, Admin Review/Compliance Hold, Audit/Event Ledger, Notification, and Observability/Ops retain their platform lifecycles.

### Dependencies

- Features 01–15.
- Privacy, Hold, Audit, Notification, and Ops public contracts.
- Resolve U-CL01-09, U-CL01-15, U-CL01-23, U-CL01-32 and other owner-specific retention decisions before destructive production behavior.

### Shared Operations Used

- SH-096 `enumerateSubjectData` — each CL-01 data owner implements the Privacy-defined inventory contract.
- SH-095 `executePrivacyInstruction` — each owner executes only its records; Privacy orchestrates.
- SH-097 `evaluateRetentionRequirement` / SH-098 `anonymizePersonalFields` — shared protocol/primitive with owner-specific retention facts/field maps.
- SH-011 `evaluateComplianceHold` — Hold-owned stop-sign decision; no CL-01 generic blocked table.
- SH-029 `appendAuditEvent` / SH-030 `recordSensitiveAccess` — Audit-owned ledgers.
- SH-041 `requestNotification` — Notification-owned delivery request.
- SH-037 `recordIntegrationFailure`, structured logging, SH-047 `enqueueReliableJob`, retry/dead-letter primitives — Ops/platform mechanisms, not domain truth.

### Data / Schema

- Identity, Consent, Customer, and Track records remain with their owners.
- `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, `AuditEvent`, `AccessAuditLog`, Notification records, `IntegrationFailure`, `SystemEvent`, `QueueJob`, and `ComplianceHold` remain outside CL-01 ownership.
- Define owner-specific privacy target types/serializers/retention candidates; do not create a CL-01 aggregate privacy table.

### Public Interfaces

- Identity/Consent/Customer/Track implementations of SH-096 `enumerateSubjectData` and SH-095 `executePrivacyInstruction`.
- Owner-specific retention fact query/result.
- Hold evaluation inputs for relevant actions.
- Audit/access event requests with safe metadata.
- Notification semantic request payloads.
- Ops integration-failure/system-event reporting.

### Logic

- Privacy discovers/assigns target; owner validates instruction and retention decision; owner executes idempotently; owner returns standardized result; Privacy records target/job completion.
- Hold decision is composed before applicable owner action; lifecycle status remains owner-specific and distinct.
- Audit/access writes happen after/beside relevant action without becoming lifecycle truth.
- Notification gets semantic/minimized intent, not entire source records.
- Operational failure records diagnose provider/job issues and never substitute for domain status.

### UI / Administrative Surface

- Privacy/admin/support surfaces remain with their owning Modules.
- CL-01 account pages may link to privacy/security/subscription history but must consume public queries.
- No duplicate CL-01 'operations dashboard' source of truth.

### Authorization / Compliance

- Privacy target execution accepts only authenticated/authorized Privacy-owned instructions.
- Sensitive admin reads/actions require Role authorization and access/audit proof according to policy.
- Hold placement/release remains Hold owner authority.
- Telemetry/audit payloads are minimized and redacted.

### Events / Jobs / Integrations

- Privacy target jobs, notification delivery, audit writes, and Ops alerts use their owners' queues/events.
- CL-01 owner domain events may trigger support effects through outbox.
- Failed support effects retry independently and do not roll back already-committed owner truth unless the transaction contract explicitly requires atomicity.

### Failure Behavior

- Retention decision missing → destructive privacy action retained/deferred, never guessed.
- Hold service unavailable for a mandatory gate → action unavailable/fail closed.
- Audit/access write failure for a legally mandatory synchronous proof → follow root policy; otherwise reliable outbox/retry.
- Notification failure → owner truth remains valid.
- Ops unavailable → log/fallback according to root standards; never rewrite domain status.

### Tests

- Privacy inventory/execution/retention tests per owner.
- Hold gating tests proving no local generic blocked flag.
- Audit vs domain-event separation tests.
- Sensitive-access logging tests.
- Notification contract tests with redaction.
- Ops failure/domain-status separation tests.
- Retry/idempotency tests for asynchronous support effects.

### Out of Scope

- Privacy workflow orchestration/UI.
- Hold lifecycle management.
- Notification provider delivery.
- Audit/Observability storage ownership.
- Legal retention durations not resolved in architecture.

### Exit Gate

- Privacy can execute each enabled CL-01 owner through a standard contract without direct table orchestration.
- Consent Module Feature 07 supplies its SH-096 enumeration, SH-097 retention facts, and SH-095 executor here. It returns a non-destructive retention-required result while U-CL01-15 is unresolved; destructive execution remains blocked, and no User deletion may silently destroy required Consent proof.
- Mandatory hold gates fail closed and no local generic blocked system exists.
- Audit/access/notification/Ops effects are routed through their canonical owners.
- Domain truth remains correct when support effects retry/fail.
- All destructive retention decisions required by enabled behavior are resolved and integration tests pass.


---

## Phase 5 — Reconciliation and Production Hardening

### 17 Backfills, Reconciliation, and Migration Safety

Build repeatable reconciliation for actor/profile mappings, security/provider summaries, Track usage/subscription state, and cross-Cluster cutovers before production migration.

### Objective

Ensure existing/seeded data can be migrated and continuously checked against CL-01 invariants without creating new source truth or destructive one-shot scripts.

### User-visible / Observable Result

- Admin/operator can run dry-run reconciliation reports for User↔provider, User↔CustomerProfile, passkey/security summary, Track usage counters, subscription/provider references, and approved consumer cutovers.
- Backfills are checkpointed, idempotent, resumable, and produce explicit mismatch reports.
- Re-running a completed backfill does not duplicate source records/events.
- Destructive corrections require an approved repair plan and authority rather than silent mutation.

### Owning Module(s)

- Each CL-01 Module owns repair of its own source records.
- Observability/Ops owns operational run visibility; migration tooling is not a new domain owner.

### Dependencies

- Features 01–16.
- Resolved U-CL01-18/U-CL01-19 for Customer provisioning/cutover migrations.
- Resolved Track uniqueness/period/provider decisions for any Track backfill being executed.
- Root migration, queue, audit, and backup/rollback standards.

### Shared Operations Used

- SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` — durable batch/checkpoint mechanics.
- SH-044 `executeIdempotentCommand` — repair/backfill item idempotency.
- SH-003 `queryOwnerFacts` (Proposed ruling) — compare source-owner facts through contracts where cross-Module evidence is needed.
- SH-029 `appendAuditEvent` — authorized repair actions.
- SH-037 `recordIntegrationFailure` / structured Ops primitives — mismatch/failure telemetry.
- SH-006 `consumeMeteredEntitlement` counter rebuild logic is reused; do not invent a separate usage repair algorithm.

### Data / Schema

- Checkpoint/report records are operational or migration evidence according to root conventions, not business lifecycle truth.
- Repair only owner-held records through owner application services.
- Use database constraints/index validation before and after migrations.
- Never disable referential/security constraints permanently to force migration success.

### Public Interfaces

- Owner-specific `reconcileIdentityMapping`, `reconcileSecurityPosture`, `reconcileCustomerProfiles`, `rebuildUsageCounters`, `reconcileTrackSubscriptions` workers/commands as warranted.
- Cross-Cluster customer cutover reconciliation report.
- Dry-run and bounded repair commands separated from report-only mode.

### Logic

- Scan by deterministic cursor/checkpoint.
- Compare authoritative records to approved invariants/provider-safe references.
- Classify mismatch as auto-repairable, manual review, blocked by unresolved architecture, or provider reconciliation required.
- Execute only approved idempotent owner repair.
- Produce before/after counts and unresolved mismatch report.

### UI / Administrative Surface

- Restricted migration/reconciliation report surface or CLI/admin output.
- Dry-run is default for destructive/high-risk repair modes.
- No end-user UI required.

### Authorization / Compliance

- Repair commands require explicit admin/system authority.
- Sensitive identifiers are masked/minimized in reports.
- Every destructive repair is audited and respects Privacy/retention.

### Events / Jobs / Integrations

- Batch jobs via shared queue with checkpoints/retries/DLQ.
- Provider reconciliation through owner adapters only.
- Repair domain events emitted only when an actual owner lifecycle change requires them.

### Failure Behavior

- Worker crash → resume from checkpoint.
- Unknown mismatch → report/manual review; no guessed fix.
- Provider unavailable → defer provider reconciliation without overwriting local truth.
- Partial repair → idempotent rerun and explicit report.
- Constraint violation → stop affected batch and surface evidence.

### Tests

- Dry-run vs apply tests.
- Checkpoint/resume/idempotency tests.
- Migration against representative legacy fixtures.
- Constraint safety/rollback tests.
- Counter rebuild and Customer cutover reconciliation tests.
- Secret/PII redaction tests.

### Out of Scope

- General platform data migration framework beyond required shared primitives.
- Automatic repair of unresolved architecture conflicts.
- Rewriting foreign Module lifecycles.

### Exit Gate

- Every required production migration has a dry-run report, rollback/repair strategy, and idempotent execution path.
- Approved backfills complete with zero unexplained mismatches.
- Usage counters reconcile to immutable events and actor/profile mappings satisfy approved cardinality.
- No repair script bypasses owner services, authorization, audit, or retention rules.
- Migration/reconciliation test suite passes.


---

### 18 Security, Privacy, Concurrency, and Production Readiness Hardening

Perform the final CL-01 production hardening pass across authentication, authorization, provider degradation, replay, privacy, audit, observability, performance, and destructive-change safety.

### Objective

Demonstrate that every production-enabled CL-01 path satisfies the Cluster architecture under adversarial, concurrent, degraded-provider, privacy, and operational conditions.

### User-visible / Observable Result

- Critical E2E workflows succeed in production-like environments and negative security journeys fail safely.
- Provider outages/replays do not create incorrect Identity or Track domain state.
- Authorization/RLS parity holds across covered resources.
- Privacy/retention paths produce approved outcomes without accidental data loss.
- Operational dashboards/logs identify failures without exposing secrets or substituting for domain truth.

### Owning Module(s)

- All five CL-01 Modules for their own source behavior.
- Root platform/Audit/Ops/Privacy/Hold/Notification owners for their shared mechanisms.
- No new Cluster-level source owner is introduced during hardening.

### Dependencies

- Features 01–17.
- All `U-CL01-*` decisions required by production-enabled behavior resolved and reflected in `architecture.md`.
- Production-like provider sandboxes/test credentials and deployment/security standards.
- Backups, migration rollback, incident, and monitoring procedures.

### Shared Operations Used

- Exercise rather than reimplement all canonical operations used by CL-01: actor resolution, authorization, step-up, consent, entitlement/metering, holds, idempotency, locks, outbox/queue, webhook verification/dedupe/status translation, audit/access, notifications, privacy, crypto, and Ops.
- Any defect in a shared operation is fixed in its canonical owner; hardening must not fork a CL-01 copy.

### Data / Schema

- Verify database constraints/indexes for provider mapping, one-to-one CustomerProfile, Track profile/track consistency, active subscription/cardinality rules, event idempotency, and usage aggregation.
- Verify retention/deletion cascades for User/security/Consent/Customer/Track against approved privacy policy.
- Review destructive migrations with staged rollout/backfill/rollback.
- Verify no search projection, audit log, queue record, or provider cache is treated as CL-01 source truth.

### Public Interfaces

- Freeze/stabilize versioned CL-01 public contracts used by neighboring Modules.
- Document decision/error envelopes and retry semantics.
- Health/reconciliation endpoints remain operational surfaces, not business APIs.

### Logic

- Threat-model authentication/session, privilege escalation, confused-deputy, replay, race, provider spoofing, account-recovery, consent replay, quota, and subscription transitions.
- Run concurrency stress for provisioning, step-up consumption, grant changes, metered usage, and subscription events.
- Verify fail-closed behavior for mandatory dependencies.
- Benchmark hot actor/authority/consent/entitlement queries and add owner-approved indexes for observed query plans.

### UI / Administrative Surface

- Production account/security/customer/consent/subscription surfaces show safe loading/error/degraded states.
- Admin/reconciliation screens enforce authority and redact provider/security details.
- Accessibility and responsive behavior are verified for any CL-01-owned UI.

### Authorization / Compliance

- RLS and server policy parity; no client-only protection.
- Secrets isolated to server/provider adapter environment.
- Rate limits on age gate, auth, step-up, recovery, consent abuse vectors, and provider ingress as appropriate.
- Sensitive reads/actions audited per final matrix.
- Privacy and retention destructive paths explicitly approved/tested.

### Events / Jobs / Integrations

- Exercise outbox/inbox, queue retries, DLQ, reconciliation, provider webhooks, notification requests, Search refresh requests, and Ops alerts under failure.
- Verify event schema minimization/versioning and consumer idempotency.
- Run provider reconciliation after injected partial failures.

### Failure Behavior

- No required dependency may fall back to permissive defaults.
- Provider timeout/outage yields explicit degraded/unavailable state while owner truth remains coherent.
- Retry exhaustion enters dead-letter/manual operational path with correlation evidence.
- Unknown provider/event/action/entitlement values fail closed.
- Destructive migration/privacy failure stops safely and is recoverable.

### Tests

- Full Module unit/state-transition suites.
- Public-interface contract suites.
- Authorization/RLS and security penetration-style negative tests.
- Provider signature/dedupe/replay/degradation/reconciliation tests.
- Concurrency/idempotency stress tests.
- Privacy/retention/destructive migration tests.
- Audit/access/observability redaction/completeness tests.
- Critical E2E journeys: signup/auth, authorization denial, passkey/security, step-up, recovery, customer actor, exact consent, entitlement/metered usage, subscription lifecycle, cross-Cluster bridge fixtures.
- Production build, typecheck, lint, migration validation, and performance checks.

### Out of Scope

- New product features.
- Organization commercial track unless separately approved.
- Public CustomerProfile search unless architecture changes.
- Refactoring neighboring Modules solely to make CL-01 cleaner.

### Exit Gate

- Every production-enabled unresolved architecture item has been resolved and architecture updated.
- No lifecycle has two owners in code/migrations and no canonical shared operation has a CL-01 duplicate.
- Provider callbacks are authenticated, deduped, translated, idempotent, and reconciled.
- No raw credential/biometric/provider-secret leakage is found.
- RLS/server parity and concurrent metering/subscription/security invariants pass.
- Privacy/retention destructive paths and migration rollback are approved/tested.
- Audit and observability are complete without replacing domain truth.
- All critical E2E, unit, integration, provider, privacy, RLS, concurrency, typecheck, lint, and production build checks pass.
- Progress tracker, architecture, and build plan agree with implemented state.


---

## Cross-Cluster Integration Phase

**Phase 4 is the explicit Cross-Cluster Integration Phase.** Its purpose is contract proof, not ownership transfer.

The minimum bridges to prove before CL-01 may be called integrated are:

```text
Identity actor → every protected Cluster
Role decision ← source-owner facts from Organization Hiring / Messaging / business owners
Customer actor → Gig / Order / Booking / Digital / Video
Track fee/commission policy → Order-owned historical snapshot
Track priority policy → Booking-owned result
Track application quota → Candidate Application lifecycle + Track usage proof
Track candidate boost → Search projection refresh
Track professional entitlement → Professional Eligibility composition
Track live/digital entitlement → Video/Digital owners without grant theft
Privacy → Identity / Consent / Customer / Track executors
ComplianceHold → relevant CL-01 action gate
Audit / Notification / Ops → support effects only
```

If a neighboring Cluster is not implemented yet, use versioned contract fixtures/test doubles. Do not copy its source records, Prisma repositories, provider integrations, or transition logic into CL-01 simply to make the integration test executable.

---

## Hardening Phase

**Phase 5 is the explicit hardening phase.** It is limited to CL-01 production risk:

- actor/session security and provider-account reconciliation;
- authorization/RLS parity;
- passkey/OTP/recovery provider degradation;
- replay/idempotency;
- aggregate locking and concurrency;
- consent version integrity and retention;
- CustomerProfile/backfill/cutover reconciliation;
- Track catalog/grant/subscription/usage invariants;
- Stripe Billing verification/dedupe/out-of-order handling/reconciliation;
- usage counter rebuilds;
- Privacy target execution and destructive-change safety;
- audit/sensitive-access completeness;
- notification/search side-effect reliability;
- operational observability and redaction;
- query/index performance for actor/authority/consent/entitlement hot paths;
- destructive migration safety and rollback;
- production readiness.

Hardening must not introduce a generic CL-01 state machine, retry system, event ledger, policy database, privacy workflow, or administrative source-of-truth table.

---

## Phase Summary

| Phase | Name | Features |
|---|---|---|
| 1 | Trusted Account and Authority Foundation | 01–05 |
| 2 | Buyer Actor and Consent Proof | 06–09 |
| 3 | Commercial Track Policy Rail | 10–13 |
| 4 | Cross-Cluster Contract Proof | 14–16 |
| 5 | Reconciliation and Production Hardening | 17–18 |

**Total numbered features: 18.**

---

## Phase Execution Pattern

Before each numbered feature:

1. Read required root, shared, Cluster, target Module, and dependency context.
2. Confirm the previous numbered feature's exit gate passed, unless the work is an explicitly tracked independent canonical-owner prerequisite.
3. Confirm no unresolved `U-CL01-*` item blocks this feature's production behavior.
4. Write the concise feature implementation specification described below.
5. Confirm schemas, ownership, public contracts, authorization/compliance gates, shared operations, migrations, and tests.
6. Implement only that numbered feature.
7. Run typecheck, lint, relevant unit/integration/contract/provider/privacy/RLS/E2E tests, and production build as applicable.
8. Perform the feature's workflow/manual verification and compare results to the exit gate.
9. Update progress; update architecture first if a legitimate binding architectural decision changed.
10. Record assumptions, risks, known failures, deferred work, and the exit-gate result before beginning the next feature.

A failed exit gate stops sequential progress. Do not redefine the gate or ownership in the progress tracker to make implementation appear complete.

---

## Required Feature Specification

Immediately before implementing a numbered feature, the coding agent must create a concise implementation specification containing:

- Objective
- Observable result
- Dependencies
- In scope
- Out of scope
- Owning Module
- Data records affected
- Public interfaces
- Shared operations consumed
- Permissions
- Primary workflow
- UI/admin states if applicable
- Provider integrations
- Jobs/events
- Idempotency/concurrency
- Error/failure behavior
- Tests
- Acceptance criteria
- Documentation updates

Do **not** pre-write giant implementation specifications for every remaining feature. The build plan defines sequence and exit conditions; the implementation specification converts only the next feature into concrete file/schema/test work immediately before implementation.

---

## Required Completion Report

After each numbered feature, the coding agent must report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Shared operations reused
- Public interfaces added/changed
- Events/jobs added
- Tests added/changed
- Commands run
- Manual/workflow verification
- Documentation updated
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

If the exit gate does not pass, the report must say so explicitly. A partial feature must not be marked complete merely because code was written.

---

## Final Build-Plan Invariants

1. This plan implements the Cluster architecture; it does not override it.
2. No feature may move a source record or lifecycle to another Module for sequencing convenience.
3. No feature may recreate a canonical shared operation under a local alias.
4. No feature may use a provider dashboard, webhook payload, audit row, queue record, search document, or cached UI state as source business truth.
5. No feature may use consent proof as authorization or entitlement.
6. No feature may use entitlement as business eligibility or resource authority.
7. No feature may create a local generic blocked state instead of using ComplianceHold where a reusable stop sign is required.
8. No feature may make Privacy orchestrate by directly rewriting every CL-01 table; owner executors remain responsible for their records.
9. No feature may make CL-01 own Media, Search, Notification, Audit, Observability, or neighboring business lifecycles.
10. No phase may pass while a production-enabled high-risk unresolved architecture decision remains silently encoded in implementation.
