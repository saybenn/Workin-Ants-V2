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
- Resolve U-CL01-29 application-limit semantics before production quota bridge, U-CL01-30 fee/commission snapshot rules before live Order pricing, and implement approved WA-R011 early-access semantics before live Booking priority.
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


## WA-R011 — Approved early-access scheduling (P01)

Product-owner ruling approved 2026-09-29: premium priority affects **when eligible customers may access newly released availability**. It never overrides an existing Booking, displaces a customer, reserves inventory permanently, or bypasses eligibility/conflict rules. This closes U-BC-05 / U-CL01-31 / CL-05-U017's product-effect choice.

Track owns the effective Customer-track benefit and returns eligibility, entitlement/grant evidence, policy version, evaluation time and expiry. Booking owns the release schedule and enforces the resulting access time on both slot queries and hold/confirmation commands. An early-access decision is not a slot reservation. Unavailable entitlement evidence cannot grant early access; ordinary access remains available once general release is reached, subject to normal gates. Existing holds follow their original bounded expiry; premium expiry cannot displace an already confirmed Booking.

Technical ruling: store timezone-independent release instants and a versioned release-window policy. Resolve the benefit against server time when creating a hold, bind evidence to that hold, and recheck normal conversion gates. No quota is consumed by this access-time benefit; SH-006 is not invoked unless a separately approved metered product is later introduced. Do not translate legacy priorityRank into request ordering. Missing release-window configuration disables early release for that availability; it does not invent a duration or disable ordinary booking. Exact window configuration is a launch prerequisite, not another ownership decision.

Implementation acceptance: premium/nonpremium boundary instants; expired/unavailable entitlement; concurrent claims; direct-command bypass attempts; replay of hold creation; no displacement; ordinary access at general release. Schema/API work must represent these facts before activation; this ruling is not implementation evidence.


## WA-R015 — User-wide points and no launch expiration (P04/P05)

**Binding product-owner ruling, approved 2026-09-30.** One User-wide Workin Ants points balance applies across Gamification/Rewards programs. Programs independently define earning rules and reward eligibility; they do not create separate point currencies or balances. This closes U-GR-01 / P04. Account identity and the atomic spending/ledger lock scope are User ID; optional program/profile references are provenance or eligibility context, never alternate wallets. All program-specific earning events credit the same account; reward eligibility is checked separately from point sufficiency. Cross-program spending uses the same canonical balance and cannot bypass a reward's eligibility conditions.

Points do not automatically function as cash, a Track/commercial entitlement, a purchased sweepstakes entry, or a mechanism for increasing chance-based prize odds. A separately approved conversion to a commercial benefit follows the explicit boundary and owner: Gamification owns redemption, Track owns commercial grants (SH-119), and the affected feature applies the granted benefit. No direct premium flag, implicit currency conversion, or automatic prize-entry creation is permitted.

**No automatic point expiration at launch.** Existing points remain valid unless spent, reversed or otherwise adjusted through an approved ledger operation. This closes U-GR-05 / P05 for launch. The `expired` enum remains reserved; launch commands, scheduled jobs and rules cannot append expiration effects. Program closure, inactivity, tier changes or profile changes do not expire a User's points. A future expiration feature requires explicit approved policy covering applicability, notice, effective dates, existing balances and auditable ledger behavior. Retention of proof is a separate concern and cannot be used to erase spendable value.

Technical application: calculate balance from the append-only owner ledger under WA-R014; serialize spending by User account, enforce sufficient available points atomically, and use immutable idempotent spend proof tied to redemption. Programs remain metadata/eligibility predicates, not lock partitions. Rebuildable balance/leaderboard projections never become source truth. Do not infer existing production balances or run a migration/backfill from this ruling.

Acceptance requirements: earnings from two programs combine into one balance; concurrent redemptions across programs cannot overspend it; reward eligibility can deny redemption despite sufficient points; profile/track changes preserve the account; program closure does not expire points; launch expiration attempts are rejected; replay creates no second spend; approved commercial conversion uses Track and never changes prize odds. These are future implementation tests, not a completion claim.


## WA-R017 — Owner facts and decision contracts

**Applied architecture ruling (AI_RESOLVED), 2026-09-30.** The [WA-R017 contract](../../reconciliation/platform-architecture-rulings.md#wa-r017--owner-facts-and-decision-contracts) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

SH-003 is a family of small owner-specific queries, not a mandatory universal DTO. Each query takes authenticated caller/purpose and a typed owner resource reference, exposes only required authorized facts with an owner-issued source token, and distinguishes unavailable/stale from absence or denial. Consumers do not load foreign Prisma records. SH-015 remains a reusable result pattern, not a universal domain enum: carry a decision category, stable owner reason code, evidence/source token and evaluation time; payload variants remain owner-specific. Domain outcomes such as Job Compliance warning/review_required and Healthcare redacted/blocked retain their distinct meaning. An unavailable prerequisite never becomes allow. Exact wire names/runtime schemas are DEFERRED_IMPLEMENTATION_DETAIL inside these constraints and must be fixed in producer/consumer fixtures before parallel integration.

Adopt this interpretation for all references that formerly treated SH-003/015 proposal status as an unconditional blocker on owner-specific interfaces. Neither SH status is promoted. New generic repositories, universal authorization or generic business-policy dispatch are forbidden. Grouped owner-specific contracts do not become interchangeable because their envelopes look similar.


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

## WA-R028 — Digital delivery evidence and policy separation

Classification: AI_RESOLVED_WITH_TRADEOFF. Resolves the technical evidence/text-storage boundary while preserving PRODUCT_OWNER_CHOICE P09/P10 for refund finality and allowance consumption. It does not activate either policy.

Digital Goods owns an immutable contextual policy-content revision with Offering/policy identity, locale/jurisdiction applicability, terms/refund/license versions, exact retained content or immutable Media document/version reference, checksum and effective interval. Acceptance binds the precise revision/rendered presentation and contextual Order/User evidence. Do not overwrite accepted content on policy edit or use an unresolvable hash/version as historical proof. Consent owns generic disclosure content/proof separately; neither owner's proof implies the other's requirements passed. Actual legal text, applicable rights and retention remain external activation requirements. This supplies the persistence direction missing from Digital Goods §35.9; exact relational names follow coordinated schema conventions.

Separate grant issuance, download intent, transfer attempt, observed delivery outcome and policy evaluation. Digital Goods owns each immutable logical delivery identity bound to actor, asset version, Order entitlement reference, grant and policy revision. Media owns storage/transport evidence and returns a normalized authenticated receipt correlated to that identity; a browser assertion is untrusted. Video playback progress and byte serving are different observations and cannot silently stand in for Digital Goods delivery. Preserve observed byte/range/completion evidence with adapter capability and timestamps; an adapter that cannot establish completion returns unknown rather than manufactures success. Completion of server delivery never claims the person read or understood the content.

A signed URL or accepted terms is not proof of download completion. Record it as the distinct event it is. Retries/resumptions for the same logical intent retain identity and attempt history; conflicting asset/actor bindings reject. Finite-allowance implementations must account for in-flight reservations under the grant lock so concurrent requests cannot bypass the approved cap; do not release an unknown outcome merely on client timeout. Reconcile durable owner/Media evidence before deciding release/consumption. The exact consumption event is P10, not chosen by this technical protocol. Unknown evidence cannot automatically make a purchase non-refundable. No `used`, URL or playback projection grants Order refund authority.

Expose delivery evidence to Order/Review as a versioned owner query containing logical identity, asset version, accepted policy/proof reference, grant state, observations and their reliability, with minimal actor/context references. Order/Review apply their approved refund/dispute policy and current authorization; Media and Digital Goods do not execute financial refunds or declare legal finality. P08 case reopening may add a new interpretation/decision cycle while retaining the original observations. Corrections append evidence and reevaluate projections; they never rewrite the old observation or repeat an old financial effect.

Acceptance before activation: URL issued without bytes, aborted transfer, range resume, duplicate receipt, unknown completion, concurrent last-allowance requests, changed policy after purchase, stale/revoked Order entitlement and later dispute cycle. These tests establish technical truthfulness; approved P09/P10 behavior and actual provider capabilities remain separate prerequisites.

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

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.

## WA-R037 — Payment effects, payout reservation and tax evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Payment owns immutable financial operation and attempt history, not just outbox delivery. Every effect has unique owner/sourceType/sourceId/sourceRevision/effectKind/effectOrdinal plus currency, semantic payload hash and original-effect reference for compensation. Reuse with different amount/subject/currency conflicts. Verified provider ingress receipt is separate from Payment and Track effect receipts; route by approved provider object/metadata ownership, never both owners applying the same business effect. Unknown routing is quarantined. Payment receipt fields: provider/account/eventId, eventType, fingerprint, handlerVersion, target operation, receivedAt, processing/attempt/recovery state and committed effect references. No raw secret payload by default; legal retention remains externally supplied.

Balance accounting uses immutable signed minor-unit effects with explicit bucket vectors and per-currency conservation. Earnings credit available (or pending until the approved availability rule); payout reservation moves available -A/reserved +A atomically with request acceptance; reservation release moves reserved -A/available +A only once after known cancellation/failure with no possible pending provider movement; successful payout moves reserved -A/paid +A. Transport retries have zero ledger effect. Provider return/reversal records its actual returned amount as a new linked effect, paid -R/available +R only after verified return and applicable financial restrictions; it never mutates the original payout. Fees/refunds/chargebacks are separate authorized signed effects, never hidden in payout status. Unknown money movement retains reservation and reconciles. Existing one-amount enum records are insufficient to infer these vectors: use an explicit owner allocation/bucket effect structure and forward constraints. This is accounting of processor-held value, not permission to introduce a wallet or new financial product.

At launch each PayoutTransfer belongs to one PayoutRequest; Order references are optional immutable allocation provenance, not a second transfer source. A request supplies an explicit validated active payoutAccountId; no guessed default among multiple accounts. Capture all blocking Hold IDs and decision versions in a separate immutable evaluation snapshot; blockedByHoldId is explanatory only. Reevaluate current holds/account/financial readiness immediately before dispatch. Keep one semantic transfer identity and stable provider idempotency key through network retries. Record each transport attempt separately. A terminal failed transfer never reopens; a new request/transfer after confirmed nonmovement and reservation release requires fresh authorization. Unknown is nonterminal even if transport timed out. No automatic retry of a terminal financially reversed/paid transfer.

Ratify the minimum Payment §9 graphs with these restrictions: KYC rejected/expired/disabled attempts are terminal; new attempt linked to previous evidence. TaxProfile rejected/expired creates a new collection revision, never overwrites submitted documents. One current applicable selector per subject+purpose+jurisdiction/provider scope points explicitly to the accepted evidence; pending new evidence does not silently replace valid current proof, while revocation immediately invalidates it. PayoutAccount disabled is terminal for that account; restriction recovery uses verified current provider evidence. PayoutRequest failed/cancelled/reversed terminal; processing cannot cancel without proven no movement. PayoutTransfer failed/cancelled/reversed terminal. SalesTaxCalculation changed quote requires a new calculation; finalized is immutable, voiding is a separately evidenced provider operation. Tax submission rejected/failed uses a new linked submission revision; transport retries of an unacknowledged submission retain semantic identity. Filed recipient correction creates replacement evidence and a link, preserving prior filing. No enum setter or provider callback bypasses these rules.

Tax subject is a Payment-owned stable subject reference mapped to an identified legal recipient, with explicit User and optional ProfessionalProfile provenance; profile identity is not automatically a separate legal taxpayer. Effective mappings/versioned evidence prevent accidental subject merge. Aggregate key is taxSubjectId + jurisdiction + taxYear + currency + reportingRegime; retain source owner/id/revision/recognition type and unique reversal identity. Prize-owned summaries use the same dimensions and preserve their own source valuation truth. SH-019 supports an explicit tax_fulfillment purpose and tax dimension; no second generic tax-readiness service is needed. Payment owns TaxReportingSubmissionStatus and TaxReportingRecipientStatus. Reporting bundle uniqueness includes regime/jurisdiction/year/currency/submission series/revision; recipients unique within submission by tax subject and applicable form/category. Rule versions, form requirements, recognition dates, thresholds and correction legality remain approved external configuration, never invented constants.

Order binds final calculation ID to exact immutable quote/order revision, currency, line IDs and buyer-tax-location evidence revision. Payment preserves line-level taxable basis, tax, jurisdiction, provider tax code and liability role even for mixed-liability lines. Tax-location provenance includes approved source owner, source/evidence revision, validation method/result and captured/effective time, minimum required location fields; it is not public-location consent. Each authorized refund has immutable line allocations against the original captured quantities/basis/tax and links its own provider refund and tax reversal attempts. Cumulative refunds cannot exceed captured refundable allocation; lock the operation allocation counters and reject mismatched currency. Use deterministic minor-unit residual allocation only within an approved tax/provider allocation policy; do not guess rates or liability. Partial/multiple refund representation requires separate child records, not one overwritten reversalId. Provider unsupported/ambiguous results stay pending/manual review, never fabricated successful tax reversal. Full provider/rule qualification remains external before affected execution.

Required verification: concurrent reservation conservation, duplicate callback/compensation, timeout followed by paid result, multiple holds, account changes before dispatch, line-level cumulative refund cap, subject/jurisdiction separation, replacement filing traceability. No live financial test or migration is claimed by this architecture decision.

## WA-R038 — Trust evidence provenance and screening boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

VerificationConsent remains a screening-context linkage: canonical ConsentLogId, identified User/subject, check type, provider, purpose, requirement/package revision and linked check. Generic acceptedAt/IP/user-agent fields are compatibility evidence only and cannot independently validate consent. New linkage requires canonical consent proof and current applicability checks; migration preserves unknown provenance without inventing consent. Each check has exactly one typed subject consistent with its User and optional Professional/Candidate profile; employer-requested screening additionally requires identified Organization/requester membership, Job/Application context, purpose and approved permissible-purpose evidence. Employer sponsorship is not activated by this technical representation.

Adopt the existing minimum Trust §9 check/package/badge graphs. Terminal checks never reopen; recheck is a new linked attempt with current consent/payment/requirement proof. License credential identity stays stable, but every verification/refresh/revocation creates an immutable evidence revision linked explicitly to its establishing VerificationCheck or authorized manual evidence decision. Current credential projection points to a valid revision; expired/revoked proof is never silently overwritten. Trust owns explicit check/credential-to-Media evidence join records, document kind, evidence revision and retention classification. Media owns bytes/scanning/access. No generic Media ownerType/ownerId joins are introduced.

Trust owns append-only check, credential, package/requirement and badge lifecycle histories with aggregate revision and source evidence, committed with outbox. Its provider effect receipt uses provider/account/eventId/handlerVersion uniqueness, fingerprint, check/credential target, normalized event kind, receivedAt, processing and attempt/recovery status, committed transition/effect refs. Unknown subject/events are quarantined; provider callbacks cannot mark a check passed from an unrecognized state. Short-lived provider report access is fetched on demand through an authorized adapter where supported. If persistence is necessary, reportToken is envelope-encrypted secret material with expiry/key version/rotation and restricted audited access; never public DTO/log/Search. Exact provider capability and retention remain external activation evidence.

Requirement rules are immutable schema-versioned records keyed to supported action, typed subject/target, jurisdiction and accepted classification revision; no free-form JSON policy or new implicit mandatory screening. Supported action vocabulary includes profile activation/publication, Offering publication, Gig response/acceptance, Order participation, Booking participation, Job application and Interview participation only where an explicitly approved requirement policy applies. Optional self-initiated Candidate/Professional screening remains optional; action enum presence does not mandate it. Single provider per package at launch; mixed-provider packages are deferred. Provider selection/check-type/jurisdiction rollout must be evidenced before activation, not inferred from a vendor enum.

Identity checks establish only their named verified identity claim; financial readiness stays Payment-owned; a healthcare credential check establishes that credential only, never BAA or Healthcare lane clearance. Broad platform_verified/gold_trust_check/healthcare_verified badges have no launch issuance or authorization effect without explicit scoped claim definitions; preserve legacy facts without minting misleading composite assurance. Public badge DTOs contain the approved claim label/type, subject profile reference, validity and evidence revision only. A badge never replaces current owner readiness.

FCRA technical evidence must link immutable notice template/version/content hash, identified recipient, approved purpose/check/report revision, delivery attempt and verified delivery outcome, policy/jurisdiction version, legally determined timing anchors, dispute submissions and outcome, final-action authorization and history. Notification delivery receipt is evidence, not a legal conclusion. Exact notice content, channels, required waits, adverse-action transitions and retention remain EXTERNAL_REQUIREMENT; no numeric windows or automated adverse decisions are approved here. Required tests cover consent-link mismatch, recheck history, expired supporting evidence, duplicate/late callback, secret exclusion and subject-context mismatch.
