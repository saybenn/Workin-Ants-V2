# Role & Authority Module Architecture

> **Module ID:** `role_authority`  
> **Module name:** Role & Authority Module (`Role / Authority Module` in the current registry)  
> **Module type:** `capability_security`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-01 Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/clusters/identity, authority, & consent/Role & Authority Module/role-authority-module-architecture.md`\
> **Document status:** implementation-grade target architecture; confirmed rulings are binding, proposed rulings require approval before the dependent implementation is committed  
> **Audience:** coding agents, developers, security reviewers, database/RLS reviewers, maintainers, compliance reviewers, and architecture reviewers  
> **Update rule:** update this file whenever a binding authority-policy, ownership, action-vocabulary, decision-contract, RLS-parity, audit, or cross-Module boundary changes. Build progress must not silently redefine this architecture.

This document is subordinate to the root Workin Ants architecture and the `CL-01` Cluster architecture. It narrows those decisions to the `role_authority` Deep Module. It does not make CL-01 a source-of-truth owner and it does not import BTLS-specific product concepts, tenancy, providers, or workflows.

Evidence posture used here:

- **Confirmed** — directly supported by the current Workin Ants registry, glossary/compliance pack, Prisma evidence, Cluster architecture/build plan, project overview, or canonical Shared Operations registry.
- **Proposed Ruling** — a necessary implementation-grade interpretation strongly supported by the evidence but not yet fully ratified.
- **Unresolved** — a real decision that must be settled before affected production behavior is implemented.

---

## 1. Module Header

| Field | Value |
|---|---|
| Module ID | `role_authority` |
| Module name | Role & Authority Module |
| Registry alias | Role / Authority Module |
| Module type | `capability_security` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-01 Identity, Authority, Consent & Entitlements` |
| Core capability | Interpret trusted authority facts and return server-enforced resource/action authorization decisions |
| Persistence posture | No unconflicted Role & Authority business-lifecycle model is currently confirmed |
| Canonical shared capability owned | `SH-002 authorizeResourceAction` |
| Root relationship | Inherits root runtime, validation, database, RLS, security, testing, and module-boundary rules; root rulings control on conflict |
| Cluster relationship | Implements the permission-interpretation part of CL-01; does not absorb Identity, Consent, Customer, or Track truth |
| Update rule | Architecture changes precede implementation when policy ownership, policy source, decision shape, or RLS semantics change |

### Governing evidence conflict

The historical Deep Module Registry lists `OrganizationMember`, `OrganizationRole`, and `ThreadParticipant` as Role / Authority-owned. Stronger shared-schema ownership rules and the CL-01 architecture place organization membership lifecycle with Organization Hiring and thread participation lifecycle with Messaging. PR-CL01-02 is **confirmed** by SH-002 and readiness ruling WA-R001 (2026-09-29). The implementation boundary is:

- Organization Hiring owns `OrganizationMember` creation, role assignment, suspension/removal, and the `OrganizationRole` vocabulary attached to that lifecycle.
- Messaging owns `ThreadParticipant` creation/removal and participation lifecycle.
- Role & Authority owns permission interpretation of those facts.
- No Role & Authority repository may mutate those records.

Until PR-CL01-02 is formally accepted or amended, only the read-only facts split and pure policy layer may be implemented; no membership or participant mutation belongs here.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Interpret trusted identity, role, membership, participant, and ownership facts to determine whether an authenticated Workin Ants actor may attempt a named action on a protected resource.

### Goal

Provide one reusable, server-enforced authorization capability so every protected Module receives a stable decision without recreating platform-role checks, organization-role matrices, thread-participant checks, admin/support boundaries, or ownership logic in feature-local helpers.

### Inputs

Typical inputs are:

- trusted actor context from Identity & Access;
- a typed action key;
- a typed resource descriptor and target identifier;
- the authorization scope required by that action;
- structural `UserRole` / `PlatformRole` facts owned by Identity & Access;
- organization membership facts owned by Organization Hiring;
- thread-participant facts owned by Messaging;
- minimal owner/participant facts supplied by the resource-owning Module;
- optional target sensitivity or administrative context when policy requires it;
- request/correlation context for safe audit and observability.

### Outputs

The Module returns a typed authorization decision containing at minimum:

- whether authority is granted;
- stable decision/reason code;
- evaluated scope;
- policy identifier/version or equivalent controlled policy reference;
- evaluated target/action identifiers in minimized form;
- optional obligation such as `step_up_required` only when a centrally approved authority policy requires it;
- safe `unavailable` semantics when authoritative facts cannot be obtained.

The decision must not assert that consent, entitlement, payment, healthcare, readiness, moderation, or another business gate has passed.

### Transformation

```text
trusted authenticated actor
+ named action
+ protected resource descriptor
+ minimum source-owner authority facts
+ Role & Authority policy
→ classified authorization scope
→ explicit policy evaluation
→ stable authorization decision
→ optional audit / step-up obligation through canonical owners
```

### Why this is a distinct Module boundary

Authorization is cross-cutting policy truth whose semantics must remain consistent across server entry points and PostgreSQL RLS. It deserves a separate Module because duplicating role/participant/ownership checks in each feature creates privilege drift, while placing the business lifecycles here would create a different kind of ownership violation. The boundary is therefore **shared interpretation, separate source truth**.

---

## 3. Owned Truth

Role & Authority owns **policy truth and decision semantics**, not the lifecycle records from which authority facts are derived.

### 3.1 Schemas / models owned

**Confirmed persisted Prisma models owned by this Module: none.**

No `Permission`, `RolePermission`, `ResourcePermission`, `AuthorizationDecision`, or generic RBAC table is currently evidenced. Do not add one merely because it is convenient. A persisted policy model may be introduced only after unresolved policy-source decision `U-CL01-10` is settled.

### 3.2 Controlled vocabulary owned

The Module owns the semantics and governance of:

- typed authorization action keys;
- resource types as they participate in authorization;
- `AuthorizationScope` semantics: `platform`, `organization`, `participant`, `ownership`;
- decision reason-code namespace;
- policy identifiers / versions;
- admin/support authority boundaries;
- permission matrices that interpret externally owned role or relationship facts.

These are code/config contract vocabularies unless the future policy-source ruling explicitly chooses persistence.

### 3.3 Enums and statuses owned

No persisted lifecycle enum/status is confirmed.

Consumed vocabularies include:

- `PlatformRole` — structurally Identity & Access-owned; current values include `user`, `admin`, `support`.
- `OrganizationRole` — lifecycle vocabulary attached to Organization Hiring-owned membership; current active values include `owner`, `admin`, `recruiter`; commented/deferred values must not be activated here.

The Module may define TypeScript contract unions for authorization scope and decision categories without claiming ownership of another Module's database enum.

### 3.4 Lifecycles owned

No business-record lifecycle is owned.

Role & Authority does not own creation, activation, suspension, removal, archive, payment, application, interview, booking, thread, moderation, or compliance lifecycles.

### 3.5 Source-of-truth records

There is currently no confirmed persisted authorization-policy record. The owned source truth is the **approved authority policy specification** and its versioned action/resource/role interpretation. The physical source of that policy — code-first, generated configuration, SQL-first, or another controlled source — is unresolved under `U-CL01-10`.

Until that decision is resolved:

- pure policy contracts and test matrices may be implemented;
- no generic RBAC schema may be created;
- broad production RLS policy rollout must remain gated by the parity/source decision.

### 3.6 Domain events / ledgers owned

None confirmed.

Authorization decisions are synchronous evaluations, not a business lifecycle ledger. `AccessAuditLog` and generic `AuditEvent` remain Audit / Event Ledger truth.

### 3.7 Projections owned

None confirmed.

Role & Authority must not create a search index, reporting materialization, or mutable authorization cache as business truth.

### 3.8 Snapshots / proof owned

No subject-owned authorization snapshot is currently required. Consumer Modules may store historical snapshots of decisions they need for their own records, but those snapshots belong to the consumer's lifecycle.

### 3.9 Policies / invariants owned

Role & Authority owns:

- platform-role permission interpretation;
- organization-role permission interpretation;
- participant-access interpretation;
- resource-ownership interpretation;
- admin/support entry boundaries;
- unknown-action fail-closed policy;
- minimal owner-facts requirements per action;
- policy decision reason semantics;
- server guard semantics for `SH-002`;
- semantic parity between server authorization and RLS/helper-function enforcement.

---

## 4. Explicit Non-Ownership

Role & Authority must not own or recreate the following:

| Owner | Truth that remains outside Role & Authority | What Role & Authority may consume |
|---|---|---|
| Identity & Access | `User`, `UserRole`, `PlatformRole`, authentication/session lifecycle, MFA/passkeys, recovery, `SensitiveActionSession` | Trusted actor context, structural platform-role facts, step-up result |
| Organization Hiring | `Organization`, `OrganizationMember`, `OrganizationRole`, membership creation/removal/role assignment, Job lifecycle | Minimal organization membership/role facts |
| Messaging | `Thread`, `ThreadParticipant`, participant add/remove lifecycle, Messages | Minimal thread-participant facts |
| Customer / Buyer Profile | `CustomerProfile` buyer identity and profile lifecycle | Buyer ownership facts when a resource policy needs them |
| Professional modules | `ProfessionalProfile`, readiness/eligibility/verification truth | Minimum ownership facts; Role does not decide selling readiness |
| Candidate Application & Resume Privacy | `CandidateProfile`, `JobApplication`, resume access business context/proof | Minimal applicant/organization relationship facts for base authority |
| Job Interview | `JobInterview` schedule/status/participants | Minimal interview relationship facts |
| Transaction / Order | `Order`, agreement, review/dispute/transaction lifecycles | Buyer/seller/participant facts needed for base authority |
| Track Subscription & Entitlement | Plans, subscriptions, entitlement grants, quotas, fee waivers, boosts, commission/priority policy | Nothing by default inside authorization; workflow composes Track separately |
| Consent & Disclosure | `ConsentLog` and consent-version proof | Nothing by default inside role permission; workflow composes Consent separately |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle | A hold decision is a separate gate after authority |
| Healthcare / Regulated Services | Healthcare readiness and admin payload allow/redact/block/deny policy | Base Role decision may allow admin workflow entry only |
| Media / File Access | `MediaAsset`, storage/scanning, signed URLs, access grants | Media may consume Role decision plus context-owner access decision |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog`, append-only enforcement | `appendAuditEvent` / `recordSensitiveAccess` commands |
| Privacy / Data Erasure | Privacy request/job/target orchestration and retention exemptions | No privacy orchestration; likely no Role-owned subject data executor today |
| Observability / Ops | logs, `IntegrationFailure`, `SystemEvent`, metrics | canonical logging/telemetry operations |
| Search / Public Visibility | Typesense/search projections | No Role search truth |
| Notification | notification records, provider delivery | No notification delivery inside authorization |

Authorization means **who may attempt** a protected action. It does not mean **whether the complete business action is currently allowed**.

---

## 5. Module Architecture Principles

1. **Authentication precedes authorization.** Role & Authority never parses provider sessions or trusts client-supplied actor IDs.
2. **One public authority capability.** Consumers use `SH-002 authorizeResourceAction`; aliases do not become competing public APIs.
3. **Facts stay with their owners.** Role & Authority reads owner facts through typed contracts; it does not acquire foreign repositories or mutate foreign lifecycles.
4. **Authority is not readiness.** Positive authority never implies consent, entitlement, compliance, payment, healthcare, moderation, or feature availability.
5. **Organization scope is exact.** A role in Organization A confers no authority in Organization B.
6. **Participant scope is exact.** Thread participation applies only to the specified thread unless an explicit administrative policy says otherwise.
7. **Ownership is contextual.** `User` identity alone does not prove buyer, seller, candidate, applicant, interviewer, organization, or resource ownership.
8. **Admin is not superuser.** Admin/support authority does not automatically reveal healthcare, financial, resume, contract, or private-message payloads.
9. **Unknown policy fails closed.** Unknown action/resource keys are never treated as allowed.
10. **Unavailable facts are not permission.** If an authoritative fact source cannot be consulted, return a safe unavailable/deny result rather than infer ownership.
11. **Server and RLS semantics must agree.** One controlled policy specification/test matrix governs both enforcement paths.
12. **No generic RBAC database by default.** Persistence requires an approved architecture decision.
13. **Authorization remains synchronous.** No queue or worker is required for the decision path.
14. **Audit is supporting proof.** Role requests canonical audit records where policy requires them; it does not own the ledger.
15. **Side effects are minimized.** A normal authorization query should be read-only except for explicitly required audit/security support calls.
16. **No permissive cache.** Cached authority facts are not introduced without explicit invalidation semantics and security review.

---

## 6. Proposed Folder / Code Structure

The exact repository prefix follows root Workin Ants code standards. The logical ownership shape is:

```text
<application-root>/
  modules/
    role-authority/
      application/
        authorize-resource-action.service.ts
      domain/
        policies/
          platform-policy.ts
          organization-policy.ts
          participant-policy.ts
          ownership-policy.ts
          admin-support-policy.ts
        action-vocabulary/
          actions.ts
          resources.ts
          scopes.ts
        decisions/
          authorization-decision.ts
          reason-codes.ts
      contracts/
        authority-facts.ts
        authorization-request.ts
        authorization-result.ts
      infrastructure/
        rls-policy-bindings/
          policy-bindings.sql-or-generator
          parity-fixtures.ts
      tests/
        policy/
        contracts/
        rls-parity/
        integration/

  server/
    security/
      authority/
        authorize-resource-action.ts
        enforce-authorization-decision.ts

  contracts/
    shared-decision-envelope/   # only if SH-015 is approved here by root/shared context
```

### Folder rules

- Do not create `repositories/` unless Role & Authority later receives a confirmed owned persisted model. Today it should not have repositories for `UserRole`, `OrganizationMember`, `ThreadParticipant`, `Order`, `JobApplication`, or other foreign records.
- `policies/` contains pure interpretation logic; it must not make provider calls or write foreign state.
- `contracts/` defines the Role-facing minimum facts DTOs and the stable public decision contract.
- `infrastructure/rls-policy-bindings/` exists only to keep database enforcement semantically aligned with Role policy. It is not permission to own another Module's table lifecycle.
- No `workers/`, `providers/`, `media/`, or `components/` directory is warranted by current evidence.
- A development-only policy inspection route may live outside the Module under approved server/admin tooling; it is not Module UI truth.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
|---|---|---|
| Delivery / server adapter | Validate request shape, call actor resolver, invoke authorization service, translate decision using root-approved denial behavior | Session parsing, business workflow, provider access, foreign DB reads |
| Application service | Orchestrate actor + owner-facts + policy evaluation; request step-up/audit when explicitly required | Business eligibility, lifecycle transition, notification delivery |
| Domain policy | Action/scope/role/relationship interpretation and stable reason codes | Persistence, network/provider calls, audit writes |
| Contracts | Typed request/result, owner-facts DTOs, action/resource vocabulary | Full foreign aggregates, provider payloads |
| Data access | No owned business repository currently; RLS binding may consume approved helper views/functions | Foreign lifecycle repositories or direct cross-domain Prisma reads |
| RLS bindings | Database-side enforcement semantics and parity fixtures | Independent policy rules that drift from server semantics |
| Workers | None | Authorization background execution |
| Provider adapters | None | Auth provider, billing, healthcare, media, messaging, or other provider clients |
| Tests | Policy matrix, contract, cross-scope isolation, RLS parity, negative ownership tests | Fixtures that mutate foreign lifecycles through Role production code |

---

## 8. Data Model

### 8.1 Role & Authority-owned Prisma data

**None confirmed.**

This is intentional. A capability can own authoritative policy without owning a mutable business aggregate.

### 8.2 Important externally owned records consumed

| Record / enum | Owner | Meaning to Role & Authority | Important constraints / usage |
|---|---|---|---|
| `User` | Identity & Access | Base account actor identity | Actor must come from trusted Identity context, not request input |
| `UserRole` | Identity & Access | Structural attachment of `PlatformRole` to User | Current schema uses composite identity by user + role; Role only interprets |
| `PlatformRole` | Identity & Access | `user`, `admin`, `support` vocabulary | Role owns action mapping, not enum lifecycle |
| `OrganizationMember` | Organization Hiring — Confirmed (WA-R001) | Membership fact scoped to one organization | Composite organization/user scope prevents cross-org authority inference |
| `OrganizationRole` | Organization Hiring — Confirmed (WA-R001) | Current role values such as owner/admin/recruiter | Role interprets; deferred values must not be activated here |
| `ThreadParticipant` | Messaging — Proposed Ruling | Participation fact for one thread | Composite thread/user fact; Role never adds/removes participant |
| `CustomerProfile` | Customer / Buyer Profile | Buyer identity/ownership context | User and customer actor are not interchangeable assumptions |
| `ProfessionalProfile` | Professional domain owner | Seller/profile ownership context | Does not imply professional readiness |
| `CandidateProfile` | Candidate owner | Candidate identity/ownership context | Does not imply application entitlement or resume disclosure |
| `JobApplication` | Candidate Application & Resume Privacy | Applicant/organization relationship context | Role needs minimum facts, not full application lifecycle |
| `JobInterview` | Job Interview | Interview participant/organization context | Role does not own interview state |
| `Order` | Transaction / Order | Buyer/seller/participant context | Role does not own order status or entitlement |
| `AccessAuditLog` | Audit / Event Ledger | Supporting sensitive-access proof | Role invokes audit interface; never inserts directly |

### 8.3 Persisted policy model

No policy, permission, resource, action, or role-to-permission schema is present in current evidence.

**Unresolved `U-CL01-10`:** choose the controlled source of authorization policy before production RLS breadth is committed. Options may include code-first with generated SQL bindings, generated configuration, SQL-first with generated TypeScript contract, or another architecture-approved model. Do not introduce administratively editable RBAC tables unless the product actually requires runtime-configurable policy.

### 8.4 Retention / privacy concerns

Because no subject-owned Role record is confirmed, there is no independent Role subject-data retention lifecycle today. Audit records, owner facts, and identity records retain under their own Modules. Any future decision cache or persisted policy-evaluation record would require a new privacy/retention ruling before introduction.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Authorization scope

Role & Authority owns this controlled contract concept:

```text
platform
organization
participant
ownership
```

Administrative/support actions are interpreted under platform authority plus target/context policy; `admin` is not a separate lifecycle scope.

### 9.2 Decision categories

The CL-01 build plan permits stable decision results such as:

```text
allowed
denied
step_up_required
unavailable
```

`warning` or `review_required` must not be introduced in Role policy merely because the shared decision envelope can express them. Use them only after a concrete Role policy requires those semantics.

`SH-015 returnDecisionResult` is a **Proposed Ruling** for the shared envelope. Role's contract should remain compatible with it without depending on unapproved semantics.

### 9.3 Decision lifecycle

An authorization decision is a point-in-time evaluation, not a durable lifecycle.

```text
request
→ resolve actor
→ obtain minimum authority facts
→ evaluate policy
→ return decision
→ discard except for consumer history/audit where separately required
```

A consumer must not treat an old decision as a permanent grant. For protected mutations, authority is checked at the server mutation boundary using current facts.

### 9.4 Policy lifecycle

The existence of policy identifiers/versions is required for traceability, but the physical versioning mechanism is unresolved until `U-CL01-10` is settled. Policy changes must be reviewed, tested against the authorization matrix, and deployed atomically enough that server/RLS semantics cannot intentionally diverge.

### 9.5 Prohibited lifecycle shortcuts

- Do not create `AuthorizationDecision.status` rows.
- Do not turn an `allowed` decision into a reusable access token.
- Do not persist `isAdmin`, `canManage`, `isOwner`, or similar derived booleans on business records.
- Do not use an audit row as active permission truth.

---

## 10. Commands

### Public Module-owned mutations

**None confirmed.**

Role & Authority is primarily a synchronous decision capability. Policy administration, role assignment, membership changes, participant changes, and audit writes are not current Role-owned commands.

### Outbound commands invoked by Role application services

#### `requireStepUpForSensitiveAction` — external, SH-014

- **Purpose:** obtain fresh assurance for an action centrally classified as sensitive.
- **Actor/context:** authenticated actor + action/target context.
- **Authoritative input:** Role's approved step-up obligation plus Identity context.
- **State written:** Identity-owned challenge/session state only.
- **Failure:** return `step_up_required` or deny/unavailable according to the approved security contract; Role never creates its own MFA state.

#### `recordSensitiveAccess` / `appendAuditEvent` — external, SH-030 / SH-029

- **Purpose:** request append-only evidence for sensitive/admin access where the audit matrix requires it.
- **State written:** Audit / Event Ledger only.
- **Idempotency:** owned by the canonical audit operation and caller request/correlation semantics.
- **Failure:** handling is part of unresolved `Role sensitive-access audit decision`; production-sensitive paths must not silently skip mandatory evidence.

---

## 11. Queries / Decisions

### `authorizeResourceAction` — canonical public decision, SH-002

- **Consumers:** every protected workflow.
- **Input:** trusted actor context, typed action, typed resource descriptor/ID, and owner-facts references or facts required by that policy.
- **Result:** authorization decision with allowed/denied state, scope, stable reason, policy reference/version, evaluated timestamp, and optional approved obligation.
- **Returns:** policy decision, not source-owner business truth.
- **Must not infer:** entitlement, consent, professional readiness, payment success, healthcare payload access, ComplianceHold clearance, Media signed access, or business lifecycle transition validity.

### Internal decision functions

These are implementation details of SH-002, not competing public APIs:

- `classifyAuthorizationScope`
- `evaluatePlatformPermission`
- `evaluateOrganizationPermission`
- `evaluateThreadParticipantAccess`
- `evaluateResourceOwnership`
- `evaluateAdminSupportBoundary`
- `verifyAuthorizationPolicyCoverage`

Scoped names such as `authorizeResumeAccess`, `authorizeOrderParticipantAction`, or `authorizeModerationAction` may exist only as thin typed adapters that translate domain-specific action/context into `authorizeResourceAction`; they must not become independent policy engines.

### Stable reason-code behavior

The exact catalog is unresolved, but the contract must distinguish at least these classes without leaking sensitive target existence:

- unknown action/resource;
- missing or insufficient platform authority;
- organization membership missing/insufficient;
- participant relationship missing;
- ownership relationship missing;
- owner facts unavailable/stale;
- step-up required;
- policy unavailable/misconfigured.

The exact string identifiers are approved as part of the initial action/reason vocabulary feature and then treated as public contract.

---

## 12. Public Module Interface

### Public commands

None currently owned.

### Public queries

```text
authorizeResourceAction(request) → AuthorizationDecision
```

Preferred request shape, conceptually:

```text
actor: trusted ActorContext
 action: AuthorizationActionKey
 resource: { type, id?, scope identifiers }
 ownerFacts: minimum owner-specific facts or resolver reference
 requestContext: correlation/request metadata
```

Preferred result shape, conceptually:

```text
outcome
reasonCode
scope
policyId
policyVersion
evaluatedAt
optional obligation / safe metadata
```

### Server enforcement interface

`enforceAuthorizationDecision` / `assertAuthorized` may exist at the shared server-security adapter, but it is an enforcement adapter for SH-002, not a separate source of policy truth.

### Owner-facts contracts

Role & Authority defines what facts a given policy requires, while the source Module supplies those facts through `SH-003 queryOwnerFacts` or another approved owner-specific interface. Examples:

- Organization Hiring: `{ organizationId, userId, role, membershipIsUsable }` only if each field is source-owned and policy-relevant.
- Messaging: `{ threadId, userId, isParticipant }` or equivalent source-owned fact.
- Order/Application/Interview owners: minimum actor/participant IDs and relevant context facts, not the whole aggregate.

The exact DTOs are versioned contracts with the owning Module.

### Emitted domain events

None by default.

### Privacy executor

None currently required because no subject-owned Role lifecycle data is confirmed.

### Provider-facing interfaces

None.

---

## 13. Inbound Dependencies

| Owning Module / capability | Public operation / interface | Why required | Minimum information | Can block? | Must not copy locally |
|---|---|---|---|---|---|
| Identity & Access | SH-001 `resolveAuthenticatedActor` | Establish trusted actor | User ID, system/user actor type, approved assurance context, structural platform role facts or role-facts reference | Yes | session parsing, current-user helper, role-row lifecycle |
| Identity & Access | Platform-role facts interface | Interpret `PlatformRole` | actor + current platform roles | Yes | `UserRole` repository/role mutation |
| Organization Hiring | SH-003 owner-specific membership facts — Proposed | Organization-scoped permission | target organization, actor membership and role | Yes | OrganizationMember repository or role assignment |
| Messaging | SH-003 owner-specific participant facts — Proposed | Thread participant access | target thread + participant fact | Yes | ThreadParticipant repository/mutation |
| Resource-owning Modules | SH-003 owner-specific facts | Ownership/participant decisions | only relationship fields required by action | Yes | foreign aggregate repositories or lifecycle rules |
| Identity & Access | SH-014 step-up | Fresh assurance where authority policy explicitly requires it | actor, action, target, current assurance | Yes | MFA/passkey/OTP logic |
| Audit / Event Ledger | SH-029 / SH-030 | Required audit/access proof | actor, target, action, decision, sensitivity, request ID | Potentially, according to audit policy | AccessAuditLog writer or hash chain |
| Observability / Ops | SH-032/033/034 and related ops | Trace safe authorization failures and health | request/correlation IDs, safe reason/scope metadata | No for ordinary logging; health may indicate degraded dependency | logger/redaction subsystem |

### Dependency rule

If a source-owner facts interface is unavailable, use a contract fixture/test double during development. Do not bypass the boundary with direct cross-domain Prisma reads in normal production code.

---

## 14. Outbound Consumers and Effects

### Major consumers

- Organization Hiring
- Candidate Application & Resume Privacy
- Job Interview
- Transaction / Order
- Messaging
- Media / File Access
- Booking / Calendar and Video when participant/owner authority is needed
- Admin Review / Compliance Hold
- Content Moderation & Legal Notice
- Healthcare administrative entry paths
- other protected Modules that need platform, organization, participant, or ownership authority

### Consumer rule

Consumers obtain a Role decision and then continue their own gate chain. Role & Authority never mutates the consumer's lifecycle.

Typical composition:

```text
resolve authenticated actor
→ authorizeResourceAction
→ consumer-specific entitlement / consent / readiness / hold / healthcare / contextual access checks
→ consumer validates lifecycle preconditions
→ consumer owns mutation
```

### Events and downstream effects

Role does not emit business events by default. Operational logs and audit requests are support effects, not cross-Module commands disguised as events.

---

## 15. Canonical Shared Operations Used

Only operations materially relevant to this Module are listed.

### SH-001 — `resolveAuthenticatedActor`

- **Classification:** canonical platform capability.
- **Owner:** Identity & Access.
- **Plain-English meaning:** resolve provider/session evidence into trusted Workin Ants actor context.
- **Why Role uses it:** authorization cannot trust client actor claims.
- **Invocation point:** before every protected `authorizeResourceAction` evaluation.
- **Local policy:** Role interprets the trusted actor; it does not decide how authentication succeeded.
- **Expected result:** trusted actor context or unauthenticated result.
- **Prohibited duplicates:** `requireAuthenticatedActor`, `getCurrentUser`, `currentUser`, `parseSession`, `getAuthenticatedActorContext` inside Role.

### SH-002 — `authorizeResourceAction`

- **Classification:** canonical shared capability; **owned and implemented here**.
- **Owner:** Role & Authority.
- **Plain-English meaning:** decide whether an authenticated actor may perform a named action on a protected resource in platform, organization, participant, or ownership scope.
- **Invocation point:** every protected server mutation/read before the action-owning Module proceeds.
- **Local policy:** action/resource vocabulary, role/relationship interpretation, reason codes, admin/support boundary, server/RLS semantic policy.
- **Expected result:** typed authorization decision.
- **Prohibited duplicates:** `authorizeAction`, `authorizeDomainAction`, `authorizeScopedAction`, `isAdmin`, `isOwner`, `canManageX`, feature permission services that recreate policy.

### SH-003 — `queryOwnerFacts`

- **Classification:** shared contract / separate implementations; **Proposed Ruling**.
- **Owner:** each source Module.
- **Why Role uses it:** obtain minimum membership/participant/ownership facts without taking lifecycle ownership.
- **Invocation point:** after scope/action classification identifies required facts.
- **Local policy:** Role defines the minimal fact requirement; source owner defines how its truth is read.
- **Expected result:** small owner-specific DTO or unavailable/not-found result.
- **Prohibited duplicates:** universal polymorphic authority repository, direct cross-domain Prisma reads, Role repositories for OrganizationMember/ThreadParticipant/Order/etc.

### SH-014 — `requireStepUpForSensitiveAction`

- **Classification:** platform security capability.
- **Owner:** Identity & Access.
- **Why Role uses it:** some centrally approved authority actions may require fresh assurance.
- **Invocation point:** after base authority recognizes a step-up obligation and before protected action continues.
- **Local policy:** only the action-to-obligation classification; Identity owns challenge/session state.
- **Expected result:** sufficient assurance or step-up-required/failed result.
- **Prohibited duplicates:** `roleMfaGuard`, `adminOtp`, `authorityStepUpSession`.

### SH-015 — `returnDecisionResult`

- **Classification:** shared contract / separate policy; **Proposed Ruling**.
- **Owner:** shared contract; policy owner varies.
- **Why Role uses it:** keep decision envelopes predictable across gate capabilities.
- **Invocation point:** public authorization result serialization.
- **Local policy:** Role's outcome/reason/scope semantics.
- **Expected result:** stable decision envelope with policy/evidence metadata where applicable.
- **Prohibited duplicates:** ad-hoc booleans, incompatible `PermissionResult` / `AccessResult` / `GuardResult` shapes per consumer.

### SH-029 — `appendAuditEvent`

- **Classification:** canonical platform audit capability.
- **Owner:** Audit / Event Ledger.
- **Why Role uses it:** record administrative permission/policy changes or authority-relevant security actions if the audit policy requires them.
- **Invocation point:** only on audit-classified actions.
- **Local policy:** safe action/target metadata supplied by Role.
- **Expected result:** audit append acknowledgement/reference.
- **Prohibited duplicates:** `roleAuditLog`, `adminAuthorizationHistory` as a competing ledger.

### SH-030 — `recordSensitiveAccess`

- **Classification:** cross-cutting capability.
- **Owner:** Audit / Event Ledger.
- **Why Role uses it:** append required sensitive access proof for authority-controlled access paths.
- **Invocation point:** according to the approved sensitive-access matrix.
- **Local policy:** Role supplies the base authority decision; the data owner supplies sensitivity/context where needed.
- **Expected result:** append-only access proof reference.
- **Prohibited duplicates:** direct `AccessAuditLog` writes, local hash-chain logic.

### SH-032 — `createRequestContext`

- **Classification:** platform primitive.
- **Owner:** Observability / platform infrastructure.
- **Why Role uses it:** correlate decisions, owner-fact calls, RLS tests, and audit effects.
- **Prohibited duplicates:** Role-specific request-ID generator/context store.

### SH-033 — `writeStructuredLog`

- **Classification:** platform capability.
- **Owner:** Observability / Ops.
- **Why Role uses it:** safe diagnostic logging for denied/unavailable/misconfigured decisions.
- **Prohibited duplicates:** custom authority logger.

### SH-034 — `sanitizeTelemetryMetadata`

- **Classification:** cross-cutting capability.
- **Owner:** Observability / Ops and audit payload policy.
- **Why Role uses it:** prevent protected payloads/owner facts from leaking into logs/audit metadata.
- **Prohibited duplicates:** ad-hoc redaction regexes inside Role.

### SH-035 / SH-036 — `captureException` / `emitMetric`

- **Classification:** Observability capabilities.
- **Owner:** Observability / Ops.
- **Why Role uses them:** capture policy/config/dependency failures and measure latency/decision health without storing business truth.
- **Prohibited duplicates:** authority-specific exception pipeline or metrics backend.

---

## 16. Module-Internal Operations

These remain internal because exposing them would create multiple policy entry points.

### `classifyAuthorizationScope`

- **Purpose:** map action/resource contract to `platform`, `organization`, `participant`, or `ownership` evaluation.
- **Input:** action key + resource descriptor.
- **Output:** scope + required fact contract.
- **Truth affected:** none.
- **Why local:** it is part of Role policy dispatch.

### `evaluatePlatformPermission`

- **Purpose:** interpret Identity-owned platform role facts for a named action.
- **Input:** actor roles + action.
- **Output:** decision fragment.
- **Truth affected:** none.

### `evaluateOrganizationPermission`

- **Purpose:** interpret Organization Hiring-owned membership/role facts in the exact target organization.
- **Input:** membership facts + action.
- **Output:** decision fragment.
- **Truth affected:** none.

### `evaluateThreadParticipantAccess`

- **Purpose:** interpret Messaging-owned participant facts for thread actions.
- **Input:** thread participant facts + action + explicitly approved admin context if applicable.
- **Output:** decision fragment.
- **Truth affected:** none.

### `evaluateResourceOwnership`

- **Purpose:** compare actor against resource-owner supplied facts.
- **Input:** typed owner facts + action.
- **Output:** decision fragment and ownership basis code.
- **Truth affected:** none.

### `evaluateAdminSupportBoundary`

- **Purpose:** distinguish admin/support entry permissions without treating either as universal data access.
- **Input:** platform role facts + admin/support action.
- **Output:** base authority decision.
- **Truth affected:** none.

### `verifyAuthorizationPolicyCoverage`

- **Purpose:** fail build/tests when a registered action lacks an explicit policy or parity fixture.
- **Input:** action registry + policy registry + RLS coverage registry.
- **Output:** coverage report/test failure.
- **Truth affected:** none.

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Authentication mechanism / authority policy:** Identity resolves actor; Role interprets permission.
2. **Organization membership truth / permission matrix:** Organization Hiring owns membership; Role interprets it.
3. **Thread participation truth / participant access:** Messaging owns participation; Role interprets it.
4. **Business ownership truth / authority:** resource owner supplies owner facts; Role interprets only what the action requires.
5. **RLS mechanism / Module lifecycle:** RLS may enforce Role semantics on foreign-owned tables, but that does not transfer those tables' lifecycle ownership.
6. **Decision envelope / separate policies:** SH-015 may standardize shape; Role reason semantics remain Role-owned while entitlement/readiness/healthcare policies remain separate.
7. **Audit append mechanism / audit truth:** Role requests an audit; Audit owns the row, hash/immutability, retention, and ledger semantics.
8. **Step-up mechanism / authority obligation:** Role may classify an action as requiring step-up; Identity owns challenge/session proof.
9. **Contextual resource access:** `SH-026 authorizeContextualResourceAccess` remains with the relevant context owner. Media, Video, Resume Privacy, Location Safety, or Agreement access should compose Role authority plus owner-specific contextual access; Role must not absorb SH-026 into SH-002.
10. **No generic authorization cache:** if a future cache is introduced, it is a derived performance mechanism with explicit invalidation; it can never become permission source truth.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

Every protected Role evaluation requires `SH-001 resolveAuthenticatedActor`. Anonymous authorization is not a Role feature; anonymous business reads must be explicitly designed by the resource-owning Module.

### Actor trust boundary

- Actor User/system identity is server-created.
- Client-provided `userId`, `role`, `organizationRole`, `isAdmin`, or `isOwner` values are untrusted input.
- Platform role facts come only from Identity-owned truth.

### Scope rules

**Platform:** interpret `PlatformRole` for the named platform/admin/support action.

**Organization:** require membership facts for the exact organization and interpret current `OrganizationRole`. Never infer authority from membership in another organization.

**Participant:** require source-owned participant facts for the exact context, such as a thread.

**Ownership:** use typed facts from the resource owner; do not reconstruct ownership from arbitrary foreign fields.

### Admin/support

Role owns entry authority boundaries. It does not grant blanket payload access. Healthcare, financial, resume, legal contract, and private-message content may require additional owner policies and sensitive-access proof.

### Step-up

If an action is centrally classified as sensitive, Role may return a step-up obligation or invoke the approved Identity operation through its application service. Exact action governance remains subject to `U-CL01-07`.

### No local generic authorization infrastructure elsewhere

Consumers must not introduce their own broad `isAdmin`, `hasRole`, `isOrgOwner`, `isParticipant`, or `isOwner` systems for actions covered by SH-002.

---

## 19. Compliance / Readiness / Entitlement Gates

Role & Authority is one gate in a larger gate chain.

| Gate | Underlying truth owner | Relation to Role | Role action |
|---|---|---|---|
| Authentication | Identity & Access | prerequisite | consume actor context |
| Step-up assurance | Identity & Access | optional security obligation | classify/consume approved step-up operation |
| Track entitlement | Track Subscription & Entitlement | separate commercial gate | do not interpret plan/subscription truth |
| Consent proof | Consent & Disclosure | separate legal/product gate | do not treat consent as role permission |
| Professional readiness | Professional Eligibility | separate business/compliance gate | do not infer from ProfessionalProfile ownership |
| Verification | Trust Verification / Screening | separate evidence/readiness gate | no verification truth here |
| Financial readiness | Payment / Payout / Tax | separate financial gate | no `canPayout`/payment policy here |
| Healthcare readiness/redaction | Healthcare / Regulated Services | separate high-sensitivity gate | only base workflow-entry authority |
| Job compliance | Job Compliance | separate hiring gate | no job-compliance policy here |
| ComplianceHold | Admin Review / Compliance Hold | reusable stop sign | consumer composes hold decision after/beside Role |
| Contextual resource access | relevant context owner, SH-026 | separate business entitlement | Role provides base actor permission only |

Typical protected workflow:

```text
SH-001 actor
→ SH-002 Role authority
→ SH-014 step-up if required
→ entitlement / consent / readiness / hold / contextual owner gates as applicable
→ action-owning Module lifecycle preconditions
→ action-owning Module mutation/read
```

---

## 20. Provider Integrations

Role & Authority owns **no external provider integration**.

Explicit prohibitions:

- no Supabase Auth session/provider client inside Role policy;
- no Stripe/Billing/Payments clients;
- no Twilio/MFA provider client;
- no healthcare provider client;
- no Media storage/signed-URL provider;
- no search, notification, calendar, video, or identity-verification provider.

Supabase **RLS/Postgres policy enforcement** is database enforcement, not an external provider integration owned by this Module. Identity establishes the trusted database/session actor context according to root architecture.

---

## 21. Events and Outbox

### Module-owned domain events

None confirmed or required for MVP authorization.

Authorization is synchronous and point-in-time. Emitting `AuthorizationAllowed` or `AuthorizationDenied` domain events by default would turn access evaluation into noisy event truth and is not justified.

### Policy changes

If a future distributed cache or policy propagation model requires `AuthorityPolicyChanged`, that decision must first settle policy persistence/version ownership and event consumers. Do not invent it now.

### Audit/observability distinction

Audit events and logs are support effects requested through their owners. They are not Role domain events.

### Outbox

No Role-owned transactional outbox write is currently required because Role owns no authoritative mutation in the decision path.

---

## 22. Background Jobs / Scheduled Work

No authorization worker or schedule is justified.

The permission decision must remain synchronous at the protected request/database boundary.

If future policy analytics, cache rebuilds, or audit processing become asynchronous, they belong to the relevant owner and must not delay or replace the authoritative decision path.

Generic queue mechanics must never be introduced into Role merely to evaluate permission.

---

## 23. Concurrency and Idempotency

### Authorization query semantics

`authorizeResourceAction` is read-only and naturally replayable. It does not need an idempotency ledger.

### Principal races

1. **Role changed after facts were read.** A protected mutation must authorize at the server mutation boundary using current facts; do not authorize once in the browser and reuse indefinitely.
2. **Organization membership changed concurrently.** Role does not lock foreign membership. The action owner must perform authorization sufficiently close to its mutation and rely on database/RLS enforcement where the route is exposed to direct DB access.
3. **Thread participation revoked concurrently.** RLS/server authorization must use current participant truth; cached allow results are unsafe without explicit invalidation.
4. **Resource ownership changed.** Owner-facts contracts must describe current authoritative relationships; stale owner facts yield conflict/unavailable/denial according to policy, never implicit allow.
5. **Policy version changed.** A decision identifies policy version; server and RLS deployment must not intentionally operate under incompatible policy versions.

### Locking

Role must not invent in-memory locks. It owns no mutable aggregate requiring a database lock. Foreign lifecycle owners handle their own transactional concurrency.

### Replay result

Replaying the same authorization request against unchanged facts/policy should return semantically equivalent results. Replaying after facts/policy change is expected to return the current decision.

---

## 24. Media / Storage

Role & Authority owns no MediaAsset, upload, scanning, object-storage, signed-URL, or access-grant mechanics.

For protected media:

```text
actor
→ Role authority
→ business context owner access decision (SH-026 where applicable)
→ Media / File Access validation and signed access
→ sensitive access audit where required
```

Role must not issue URLs or infer file sensitivity from filenames/paths.

---

## 25. Search / Projection

Role & Authority owns no search projection.

Permission policy must not be reconstructed from Search/Typesense documents. Search can consume source-approved public visibility facts, but a search hit never proves authorization for protected source data.

No indexing trigger is required for ordinary Role decisions.

---

## 26. Notification

Role & Authority owns no Notification records or provider delivery.

Ordinary authorization allow/deny decisions do not generate notifications.

If a future security policy requires notifying a user of high-risk administrative access or permission changes, the action owner or Identity/Audit security workflow requests Notification through the canonical interface. Role must not send email/SMS/push directly.

---

## 27. Audit and Sensitive Access

### Distinct records

- **Role policy decision:** ephemeral authorization result owned semantically by Role.
- **AuditEvent:** generic append-only audit record owned by Audit / Event Ledger.
- **AccessAuditLog:** sensitive access proof owned by Audit / Event Ledger.
- **Domain lifecycle event:** belongs to the business Module whose lifecycle changed.
- **Operational log:** Observability evidence, not audit proof.

### Role responsibility

Role supplies safe authority context to SH-029/SH-030 when the approved audit matrix requires it.

### Unresolved audit matrix — `Role sensitive-access audit decision`

Architecture must still decide:

- which allowed decisions require `AccessAuditLog`;
- which denied attempts require access audit versus ordinary security logging;
- which actions use `AuditEvent` instead;
- whether mandatory audit append failure fails closed or permits deferred evidence;
- how general authorization decisions map to the current `AccessAuditLog` schema, which presently references a healthcare-specific access-decision vocabulary.

Role must not solve these by changing Audit-owned schema unilaterally.

---

## 28. Privacy and Retention

### Subject-data inventory

No Role-owned subject lifecycle records are currently confirmed.

Role may transiently process:

- actor ID;
- organization/thread/resource IDs;
- role/relationship facts;
- decision reason/scope;
- sensitivity category.

These inputs must not be persisted locally by default.

### Privacy executor

No Role privacy target executor is currently required. Privacy orchestration remains Privacy / Data Erasure-owned. Identity, Organization Hiring, Messaging, Audit, and resource Modules handle their own records.

### Retention

- policy source/config follows architecture/change-control retention, not user erasure semantics;
- Audit-owned access proof follows Audit/Privacy retention rules;
- logs follow Ops retention and redaction policies;
- future authorization-decision persistence requires an architecture update and privacy inventory before implementation.

### Export

Role contributes no independent user export dataset unless future persisted policy-evaluation records are approved.

---

## 29. Observability

Required operational signals:

- authorization decision latency;
- owner-facts dependency latency/failure by owner and contract version;
- unknown action/resource attempts;
- policy coverage gaps/misconfiguration;
- server/RLS parity test failures in CI;
- denied/unavailable rates by safe action family and scope;
- step-up-required rate where applicable;
- audit append dependency failure where applicable.

Safe dimensions:

- action key;
- resource type, not sensitive payload;
- authorization scope;
- reason code;
- policy version;
- consumer Module;
- request/correlation ID;
- dependency name.

Never log:

- resume contents;
- message text;
- contract content;
- healthcare payloads;
- financial payloads;
- access tokens/session secrets;
- full owner-facts DTOs unless each field is explicitly approved for telemetry.

Use canonical request context, structured logging, metadata sanitization, exception capture, and metrics operations.

---

## 30. Security Boundaries

1. Validate action/resource request shape at every server trust boundary.
2. Reject unknown action/resource keys before policy evaluation.
3. Never accept role/ownership booleans from the browser as authority facts.
4. Resolve actor server-side through Identity.
5. Fetch/receive owner facts only from their source Module contracts.
6. Minimize facts; avoid pulling entire foreign aggregates.
7. Fail closed on missing/ambiguous policy.
8. Treat source-owner dependency failure as `unavailable`/deny, never allow.
9. Preserve exact organization/thread/resource scope to prevent confused-deputy access.
10. Ensure support is not implicitly admin and admin is not implicit sensitive-payload access.
11. Keep RLS and server semantics under one policy test specification.
12. Do not expose policy internals or target-existence details in denial messages when root privacy rules require non-disclosure.
13. Never store provider credentials or temporary secrets in Role.
14. Apply rate limiting only through root/shared infrastructure where abuse policy requires it; do not invent a local limiter.
15. Sanitize all audit/log metadata.

---

## 31. Error / Decision Result Pattern

The public API returns a typed decision rather than throwing raw permission/provider errors to consumers.

Conceptual categories:

| Category | Meaning | Consumer behavior |
|---|---|---|
| `allowed` | Role authority is satisfied | Continue to remaining owner/compliance/business gates |
| `denied` | Current authoritative facts/policy do not grant authority | Stop; translate using root-approved denial behavior |
| `step_up_required` | Base role/relationship authority may be sufficient but fresh Identity assurance is required | Invoke SH-014; re-evaluate as required |
| `unavailable` | Required policy or owner facts could not be safely evaluated | Fail safe; retry only where appropriate |

Every result should include a stable `reasonCode`, `scope`, and `policyId/policyVersion` (or equivalent controlled reference). `evaluatedAt` supports traceability but does not make the decision reusable forever.

### HTTP / not-found mapping

Whether a denial becomes HTTP 403, privacy-preserving 404, redacted output, or domain-specific denial is **not fully resolved**. Role returns policy semantics; the root/server adapter and data-owning Module apply the approved presentation rule. Healthcare redaction always remains Healthcare-owned.

### Raw errors

Dependency exceptions are converted to `unavailable` plus safe telemetry. Never leak SQL/RLS/provider/internal stack details through the public decision.

---

## 32. Testing Architecture

### Domain unit tests

- platform role/action matrix;
- organization role/action matrix after approved;
- participant actions;
- ownership predicates;
- admin vs support boundaries;
- unknown action/resource fail-closed;
- minimum owner-facts requirements;
- step-up obligation classification where approved.

### Contract tests

- SH-002 request/result schema;
- action/resource vocabulary stability;
- reason-code stability;
- SH-003 owner-facts DTO versions;
- SH-015 compatibility if approved.

### Database / RLS integration tests

- server decision and RLS/helper-function parity for every RLS-protected policy in scope;
- cross-organization isolation;
- revoked/missing membership denial;
- removed participant denial;
- direct DB access cannot bypass server semantics where RLS is expected to protect the table;
- policy functions do not mutate foreign lifecycle data.

### Authorization negative tests

- forged client `isAdmin`/role ignored;
- actor ID spoof ignored;
- role in wrong organization denied;
- unrelated thread user denied;
- wrong owner/candidate/professional denied;
- admin/support cannot bypass healthcare/financial/resume/private-message secondary gates;
- owner-facts outage never grants access.

### Compliance / audit tests

After `Role sensitive-access audit decision` is resolved:

- required sensitive access appends through Audit owner;
- no direct AccessAuditLog write exists in Role;
- audit payload is minimized/sanitized;
- mandatory-audit failure follows approved fail behavior.

### Concurrency tests

- membership/participant revocation reflected on next authorization;
- no stale application cache grants access;
- policy version change does not leave server/RLS intentionally mismatched.

### Provider adapter tests

None inside Role.

### Privacy tests

- no foreign payload or owner-facts dump enters logs;
- no unauthorized decision persistence exists;
- denial messages obey privacy-safe mapping once approved.

### E2E participation tests

Role participates in critical flows owned elsewhere: organization job management, resume view, interview action, thread read/post, order access, media-context access, moderation/admin entry, and sensitive data workflows.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `SH-002 authorizeResourceAction` is the canonical public authority capability.
2. Identity & Access, not Role, authenticates the actor.
3. Client claims never establish actor identity, platform role, organization role, participation, or ownership.
4. `UserRole` and `PlatformRole` remain structurally Identity-owned.
5. `OrganizationMember` and `OrganizationRole` remain Organization Hiring lifecycle truth under PR-CL01-02; Role never mutates them.
6. `ThreadParticipant` remains Messaging lifecycle truth under PR-CL01-02; Role never mutates it.
7. Role must not create repositories for another Module's lifecycle records merely to evaluate authority.
8. Every organization decision is scoped to the exact target organization.
9. Every participant decision is scoped to the exact target context.
10. Ownership must come from the resource owner, not inferred from naming conventions or client IDs.
11. An `allowed` Role decision does not mean entitlement, consent, readiness, hold, payment, healthcare, or business lifecycle gates passed.
12. Admin/support authority never grants automatic healthcare, financial, resume, legal-contract, or private-message payload access.
13. Unknown action/resource/policy fails closed.
14. Missing owner facts never become an implicit allow.
15. Server policy and RLS semantics must have parity tests from one controlled policy specification/matrix.
16. No generic RBAC tables are added until `U-CL01-10` is resolved and architecture updated.
17. No feature-local `isAdmin`, `isSupport`, `isOrgOwner`, `isRecruiter`, `isThreadParticipant`, `isOwner`, or equivalent policy engine may replace SH-002.
18. `AccessAuditLog` remains Audit / Event Ledger-owned; Role only invokes canonical audit operations.
19. Step-up state remains Identity-owned.
20. Role owns no provider client.
21. Authorization remains synchronous; no background worker decides live access.
22. No persistent allow cache may become source truth.
23. Role must not emit business lifecycle events on behalf of consumers.
24. Logs/audit metadata must be minimized and sanitized.
25. Role must not directly issue signed media URLs or contextual access grants.
26. Search output cannot prove authorization.
27. A decision is point-in-time; protected mutations re-authorize at the authoritative server boundary.
28. If a required architectural decision is unresolved, affected production behavior remains disabled/fail-closed rather than guessed.

---

## 34. Prohibited Duplicate Implementations

Do not generate the following inside Role as competing shared mechanisms, and do not permit consumers to recreate them for covered actions:

### Authentication duplicates

- `currentUser.ts`
- `getAuthenticatedUser.ts`
- `requireAuthenticatedActor.ts`
- `sessionAuth.ts`
- provider-session parsers

### Competing permission APIs / helpers

- `authorizeAction` as a second public engine
- `authorizeDomainAction`
- `authorizeScopedAction`
- `authorizeBusinessAction`
- `isAdmin`
- `isSupport`
- `hasPlatformRole`
- `requireAdmin`
- `adminGuard` with independent policy
- `isOrganizationOwner`
- `isOrganizationAdmin`
- `isRecruiter`
- `canManageOrganization`
- `canManageJob`
- `isThreadParticipant`
- `canReadThread`
- `canPostMessage`
- `canViewResume`
- `canAccessOrder`
- `isResourceOwner`
- generic feature-local `permissions.ts` matrices

Thin adapters are allowed only when they translate a domain action into SH-002 without duplicating policy.

### Foreign truth duplicates

- Role-owned `OrganizationMemberRepository`
- Role-owned `ThreadParticipantRepository`
- local premium/entitlement flags
- consent checks presented as role permission
- professional-readiness checks
- healthcare redaction policy
- Media signed-URL authorization
- contextual resource entitlement that belongs to SH-026 owner

### Audit / infrastructure duplicates

- direct `AccessAuditLog` writer
- Role audit hash chain
- Role-specific request context/logger/redactor
- Role-specific idempotency/event/queue subsystem
- independent RLS membership predicates that do not share the semantic policy source/test matrix

---

## 35. Unresolved Decisions

| ID / Topic | Current evidence | Required decision | Blocks |
|---|---|---|---|
| PR-CL01-02 ownership split | Registry conflicts with glossary/Cluster architecture | Formally accept or amend Organization Hiring/Messaging lifecycle ownership | Any Role mutation of membership/participant records; current plan assumes read-only split |
| U-CL01-10 policy source | No persisted policy model; server + RLS both required | Code-first, generated config, SQL-first, or another controlled single source | Broad production RLS implementation and final policy code layout |
| Action vocabulary | Examples exist, full catalog does not | Approve versioned action/resource key inventory and governance | Production policy coverage |
| Platform admin/support matrix | Roles exist, exact actions absent | Define explicit user/admin/support permissions | Production admin/support routes |
| Organization role matrix | owner/admin/recruiter exist; exact actions absent | Define approved action matrix; decide status of deferred member/viewer values | Production org actions |
| Owner-facts DTOs | Need is confirmed, exact contracts vary | Define per-owner minimal facts and versions | Each consumer integration |
| SH-015 decision envelope | Proposed shared contract | Approve exact shared shape or define Role-compatible stable contract | Cross-gate result standardization |
| Denial presentation | 403/404/redaction/domain denial not universal | Root/data-owner rule for target-existence protection | HTTP/UI translation, not pure policy evaluation |
| U-CL01-07 step-up action governance | Sensitive action enum exists elsewhere | Define extension/governance and Role obligation matrix | Step-up-required production actions |
| Role sensitive-access audit decision | AccessAuditLog exists; exact required actions absent | Determine which allowed/denied attempts require SH-030 vs SH-029/logging and failure semantics | Audit completeness |
| AccessAuditLog decision vocabulary | Current schema couples `accessDecision` to healthcare vocabulary | Audit owner must decide whether general decision vocabulary is needed | Generic Role-sensitive access evidence |
| RLS coverage set | RLS technology confirmed, table/action coverage incomplete | Enumerate which protected tables/actions require DB-side Role parity | Production direct DB/RLS exposure |
| Policy cache | No need currently evidenced | Keep absent unless performance requires explicit invalidation design | Nothing for MVP; must not be invented |
| Authorization events | No event contract evidenced | Keep absent unless distributed policy propagation later requires it | Nothing for MVP |

### Binding posture for unresolved decisions

When implementation reaches one of these boundaries, either:

1. approve a ruling and update architecture before implementation; or
2. implement only the noncontroversial contract/mechanism and keep affected production behavior disabled or fail-closed.

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Role & Authority remains an active `capability_security` Module in CL-01.
2. Its core ownership is permission interpretation and server-side resource/action authorization.
3. `SH-002 authorizeResourceAction` is its canonical public capability.
4. Identity & Access owns authentication and structural `UserRole` / `PlatformRole`; Role interprets them.
5. Role owns no unconflicted business-lifecycle Prisma model today.
6. Role owns typed action/resource/scope policy, reason semantics, permission matrices, server guard semantics, and RLS semantic parity.
7. Authorization is separate from entitlement, consent, readiness, compliance, holds, payment, healthcare redaction, and business lifecycle policy.
8. `AccessAuditLog` and generic audit truth remain Audit / Event Ledger-owned.
9. Role has no provider integration, no background authorization worker, no search projection, no Media/storage truth, and no notification delivery truth.
10. Authorization is point-in-time and fail-closed for unknown/missing policy or facts.
11. Server and RLS decisions require parity tests.
12. Canonical Shared Operations must be reused instead of local substitutes.

### Proposed rulings carried forward

- **PR-CL01-02:** Organization Hiring owns organization membership/role lifecycle; Messaging owns ThreadParticipant lifecycle; Role only interprets.
- **Policy directory posture:** feature/Module-first code with no foreign repositories or generic CL-01 permission service.
- **SH-015 compatibility:** Role public decisions should be compatible with the shared decision envelope if/when it is approved.

### Explicitly deferred

- persisted policy source;
- exact action/resource catalog;
- exact admin/support and organization matrices;
- exact audit matrix;
- denial presentation semantics;
- policy-change events/caching unless a real requirement appears.

---

## 37. Coding-Agent Usage

Before implementing or modifying Role & Authority, the coding agent must read, in order:

1. `context/project-overview-v3.md`;
2. root `architecture.md` (**currently missing**; see `context/context-map.md`);
3. root `code-standards.md` (**currently missing**; see `context/context-map.md`);
4. `context/shared/shared-operations.md`;
5. `context/clusters/identity, authority, & consent/identity-authority-consent-architecture.md`;
6. `context/clusters/identity, authority, & consent/identity-authority-consent-build-plan.md`;
7. this `role_authority/module-architecture.md`;
8. this `role_authority/implementation-plan.md`;
9. public-interface sections for Identity & Access, Organization Hiring, Messaging, Transaction / Order, Candidate Application & Resume Privacy, Job Interview, Audit / Event Ledger, Healthcare, Media / File Access, and any other direct consumer/fact owner involved in the feature;
10. the project progress tracker.

Before writing code, the agent must confirm:

- which Cluster feature/milestone the work supports;
- that the previous Module feature exit gate passed;
- that no unresolved architecture item blocks production behavior;
- that no foreign lifecycle repository or feature-local permission engine is being introduced;
- that SH-002 is the public authorization boundary;
- that RLS changes, if any, have an approved semantic-source/parity strategy.

If repository implementation conflicts with this architecture, the agent must state the conflict and seek/update the governing architecture rather than silently preserving or inventing a competing pattern.


## WA-R017 — Owner facts and decision contracts

**Applied architecture ruling (AI_RESOLVED), 2026-09-30.** The [WA-R017 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r017--owner-facts-and-decision-contracts) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

SH-003 is a family of small owner-specific queries, not a mandatory universal DTO. Each query takes authenticated caller/purpose and a typed owner resource reference, exposes only required authorized facts with an owner-issued source token, and distinguishes unavailable/stale from absence or denial. Consumers do not load foreign Prisma records. SH-015 remains a reusable result pattern, not a universal domain enum: carry a decision category, stable owner reason code, evidence/source token and evaluation time; payload variants remain owner-specific. Domain outcomes such as Job Compliance warning/review_required and Healthcare redacted/blocked retain their distinct meaning. An unavailable prerequisite never becomes allow. Exact wire names/runtime schemas are DEFERRED_IMPLEMENTATION_DETAIL inside these constraints and must be fixed in producer/consumer fixtures before parallel integration.

Adopt this interpretation for all references that formerly treated SH-003/015 proposal status as an unconditional blocker on owner-specific interfaces. Neither SH status is promoted. New generic repositories, universal authorization or generic business-policy dispatch are forbidden. Grouped owner-specific contracts do not become interchangeable because their envelopes look similar.


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

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.


## WA-R064 — Source-qualified authority, event and cryptographic contracts

Role owns versioned action/resource catalog governance and permission decisions; each source owner owns the facts and command semantics. Catalog entries identify the existing public port, supported actor relationships, immutable facts schema/version, source freshness token, purpose, assurance class, required consent/evidence and explicit negative cases. Missing registration or required facts denies; permission is not inferred from enum presence or platform role. Wire field spelling may be deferred only after the semantic fields and owner port are identified.

For CL-01 self session revocation the facts are Identity User/session ownership, current security generation and registration status; platform revocation additionally needs a specifically granted security action and action-bound assurance. Role assignment/revocation requires current granting actor authority, target User, role scope, expected assignment revision and fresh assurance; support role alone is insufficient. Consent acceptance binds resolved subject, immutable catalog/disclosure revision and context/purpose; Consent returns proof identity/applicability and never establishes age eligibility or screening permissible purpose. Track entitlement reads bind User/actor track, benefit/action, effective interval, current grant/subscription policy revision and usage where relevant; payment status alone is insufficient. Customer self reads/edits require User ownership and profile revision; sensitive support disclosure additionally binds approved purpose and audited field scope. These entries define semantics for the named ports only, not a declaration that every platform action has been inventoried.

CL-01 committed change facts must distinguish Identity security-generation/session invalidation and Identity-owned platform-role assignment revision, Consent proof/disposition revision, Track entitlement/usage revision and Customer lifecycle/visibility revision. Include semantic event identity, source owner/typed aggregate reference, immutable source revision, effective time and schema version; no credential, disclosure text, raw identity evidence or payment secret. Identity-owned platform-role/security changes require fresh current-fact evaluation; launch has no Role-owned event stream or authorization cache under WA-R031. Consent consumers re-evaluate applicable proof; Track consumers re-evaluate eligibility/quota; Customer consumers re-query current relationship/visibility. Facts request invalidation/re-evaluation, never instruct consumers to invent permission or reverse existing purchase rights. Exact event names, subscriber registry, out-of-order/tombstone behavior and source-specific payload fixtures remain bilateral qualification work where not already defined by a narrower owner ruling.

SH-073 remains shared security/cryptography machinery, with separate owner-scoped chains. Evidence owner selects ordered canonical record input/version and stores chain identity, sequence, predecessor and entry hash atomically with its retained record; verifier detects a broken sequence/hash and returns evidence without repairing history. No universal chain, external anchor, or tamper-proof claim follows. An anchor would require an explicit external requirement and qualified adapter. Root placement/sequencing of shared rails remains a later readiness dependency, not established by this ruling.


## WA-R065 — Shared sensitivity policy governance and Healthcare applicability

Role & Authority owns the versioned platform security classification-to-access policy catalog as part of its existing authorization-policy concern; it does not own source records, clinical decisions or retention law. DataSensitivity remains the shared vocabulary: normal, sensitive, healthcare, financial, identity_document, resume, legal_contract and private_message. These are categories, not a numeric ranking, and normal does not mean public. Source owners declare field/attachment context and purposes; Healthcare owns whether healthcare-sensitive obligations apply. Payment, Identity, Candidate, Agreement and Messaging respectively establish their own financial, identity, resume, contract and message context. Media never invents a competing classification or decides clinical applicability from a file extension.

Each catalog entry binds category plus purpose to approved actor/relationship predicates, allowed response fields, required sensitive-access evidence, transport/storage controls and provider qualification requirements. All categories require authenticated transport and access-controlled encrypted storage; the sensitive categories additionally require purpose-limited disclosure and WA-R023 durable sensitive-access proof. Credentials, raw report tokens and protected identity/tax material require the shared envelope-encryption/secret-handling mechanism; healthcare handling additionally requires current Healthcare-approved provider/account/configuration coverage. Public publication is a separately authorized source projection, never an implication of normal. Shared security/cryptography owns mechanisms and key references, not a second sensitivity lifecycle.

Where multiple contexts apply, combine applicable restrictions and require every applicable policy; do not downgrade by choosing one enum value. If the current scalar schema cannot preserve all required context, source owner retains explicit contextual evidence and denies an affected disclosure until the adapter can enforce the intersection. Unknown classification, missing purpose, unsupported provider coverage or unqualified key handling cannot fall back to normal. Classification corrections produce a new source/policy revision and invalidate stale grants/projections. Classification alone establishes neither lawful collection nor consent nor retention: source owner/Consent/Privacy/Healthcare retain those separate decisions, and absent legal/provider evidence remains external qualification.


## WA-R068 / WA-R069 — Authority facts and committed event obligations

This Module adopts its `role_authority` action/fact row and specifically registered producer/consumer effects in `context/reconciliation/authority-event-contracts.md`. Role interprets the catalog; this owner retains facts and lifecycle. Register each concrete protected port before activation; a grouped port row does not authorize unspecified commands.

Owner action scope: `authorizeResourceAction / evaluateOrganizationPermission`. Permitted relationships: authenticated actor or registered service scope; no role-only bypass. Required owner facts: action key/version, typed target, actor epoch, explicit grants, source owner fact tokens, purpose. Assurance: Decision only; evaluates action requirement. These facts include typed target, source revision, subject relationship, purpose/action and evaluation time; missing/stale/unavailable facts cannot authorize, and current revisions are checked again at effect. B/S/A have the precise appendix meanings; source services cannot invent human assurance.

No additional domain event is registered for this Module by this ruling; existing explicit command/receipt contracts remain authoritative.

Current-fact obligation (not an event subscription): Identity invalidates assurance on `identity.platform_role_changed.v1`; Role evaluates fresh Identity assignments on each protected request. No Role-owned stream, subscriber cache or event-derived authority.

Each audience receives only its needed fields. Obtain fresh source facts before protected decisions; invalidation is not authority.

Persist source history and outbox intent atomically; use event identity/fingerprint deduplication, source-revision watermarks, tombstones and correction lineage as specified by WA-R069. Delayed facts cannot restore revoked exposure; gaps require owner replay/current snapshot. Registered Hold applicability may prompt current reevaluation only for existing typed targets/actions; release is never automatic restoration or financial execution. Source events cannot substitute for explicit Privacy/Moderation/provider effect commands or WA-R066 notification intents.

WA-R031 governs: launch has neither a Role-owned event stream nor an authorization cache. Identity supplies persisted platform-role assignment facts. R064 references to Role assignment changes mean Identity assignment revision, and references to cache invalidation mean fresh current-fact evaluation at launch. Govern the action catalog and policy interpretation without owning assignments or source lifecycles.

## WA-R081–083 — Gate 4 bridge obligations

This owner adopts the scoped contracts in `context/reconciliation/bridge-contract-bindings.md` and the following reviewed bridge responsibilities. The named owner retains truth; another owner's query/event/receipt does not authorize a local transition. R068/069/075 and existing approved rulings remain binding. These are architecture obligations, with executable/schema/provider qualification still required before activation.

| Family | Role in current boundary | Contract and local obligation |
|---|---|---|
| BF-026 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-027 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-033 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-063 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-065 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-066 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-083 | Producer/source | evaluateHealthcareVendorReadiness; resolveEffectiveHealthcareBoundary; sensitivity field policy. Enforce every applicable category/purpose and exact ancestry before serialization/provider call. Messaging applies current restriction/mask; Notification only approved channel-safe variables and no PHI/body. Unenforceable redaction/unknown provider coverage denies; urgency/admin role cannot bypass. |
| BF-084 | Producer/source | evaluateHealthcareVendorReadiness; resolveEffectiveHealthcareBoundary; sensitivity field policy. Enforce every applicable category/purpose and exact ancestry before serialization/provider call. Messaging applies current restriction/mask; Notification only approved channel-safe variables and no PHI/body. Unenforceable redaction/unknown provider coverage denies; urgency/admin role cannot bypass. |
| BF-102 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-131 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-160 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-162 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-163 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-164 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-183 | consumer/composer | R068 owner facts; R069 membership/application/interview changes; ensureContextThread. Current Organization membership is necessary for named hiring actions but not universal Thread access. Messaging rechecks context/participants and revokes audience; Role reads owner facts directly, with no speculative replicated membership event cache. |
| BF-196 | Producer/source | evaluateHealthcareVendorReadiness; resolveEffectiveHealthcareBoundary; sensitivity field policy. Enforce every applicable category/purpose and exact ancestry before serialization/provider call. Messaging applies current restriction/mask; Notification only approved channel-safe variables and no PHI/body. Unenforceable redaction/unknown provider coverage denies; urgency/admin role cannot bypass. |
| BF-203 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-204 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-205 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-210 | consumer/composer | getNotificationDeliveryState; validateNotificationActionRoute. Source receives normalized delivery uncertainty, never legal/domain success. Catalog permits only approved internal/allowlisted HTTPS contextual route with safe refs; opening reauthenticates and reauthorizes at source. No bearer token/file URL/raw destination in generic intent or evidence. |
| BF-211 | consumer/composer | getNotificationDeliveryState; validateNotificationActionRoute. Source receives normalized delivery uncertainty, never legal/domain success. Catalog permits only approved internal/allowlisted HTTPS contextual route with safe refs; opening reauthenticates and reauthorizes at source. No bearer token/file URL/raw destination in generic intent or evidence. |
| BF-230 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-231 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-232 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-234 | Producer/source | SH-132 rate-limit policy and shared validation/error transport. Role governs named action/purpose policy; shared runtime enforces bounded request/error/rate mechanics. Sensitive endpoints use non-enumerating external errors with restricted internal diagnostics. Missing enabled-action budget/assurance policy denies activation; no invented limits or feature-local limiter. |
| BF-249 | consumer/composer | queryAuditEvents; querySensitiveAccessHistory. Bounded paginated authorized redacted evidence queries, with proof/step-up where required. Audit is retained evidence, not current source permission or foreign repository expansion; no operator dashboard becomes mutation authority. |
| BF-256 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-257 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-266 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
