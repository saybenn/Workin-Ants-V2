# Role & Authority Module Architecture

> **Module ID:** `role_authority`  
> **Module name:** Role & Authority Module (`Role / Authority Module` in the current registry)  
> **Module type:** `capability_security`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-01 Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/modules/role_authority/module-architecture.md`  
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

The historical Deep Module Registry lists `OrganizationMember`, `OrganizationRole`, and `ThreadParticipant` as Role / Authority-owned. Stronger shared-schema ownership rules and the CL-01 architecture place organization membership lifecycle with Organization Hiring and thread participation lifecycle with Messaging. This file adopts **Proposed Ruling PR-CL01-02** as the implementation boundary:

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

No `Permission`, `RolePermission`, `ResourcePermission`, `AuthorizationDecision`, or generic RBAC table is currently evidenced. Do not add one merely because it is convenient. A persisted policy model may be introduced only after unresolved policy-source decision `U-CL01-16` is settled.

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

There is currently no confirmed persisted authorization-policy record. The owned source truth is the **approved authority policy specification** and its versioned action/resource/role interpretation. The physical source of that policy — code-first, generated configuration, SQL-first, or another controlled source — is unresolved under `U-CL01-16`.

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
| `OrganizationMember` | Organization Hiring — Proposed Ruling | Membership fact scoped to one organization | Composite organization/user scope prevents cross-org authority inference |
| `OrganizationRole` | Organization Hiring — Proposed Ruling | Current role values such as owner/admin/recruiter | Role interprets; deferred values must not be activated here |
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

**Unresolved `U-CL01-16`:** choose the controlled source of authorization policy before production RLS breadth is committed. Options may include code-first with generated SQL bindings, generated configuration, SQL-first with generated TypeScript contract, or another architecture-approved model. Do not introduce administratively editable RBAC tables unless the product actually requires runtime-configurable policy.

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

The existence of policy identifiers/versions is required for traceability, but the physical versioning mechanism is unresolved until `U-CL01-16` is settled. Policy changes must be reviewed, tested against the authorization matrix, and deployed atomically enough that server/RLS semantics cannot intentionally diverge.

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
- **Failure:** handling is part of unresolved `U-CL01-17`; production-sensitive paths must not silently skip mandatory evidence.

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

If an action is centrally classified as sensitive, Role may return a step-up obligation or invoke the approved Identity operation through its application service. Exact action governance remains subject to `U-CL01-15`.

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

### Unresolved audit matrix — `U-CL01-17`

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

After `U-CL01-17` is resolved:

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
16. No generic RBAC tables are added until `U-CL01-16` is resolved and architecture updated.
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
| U-CL01-16 policy source | No persisted policy model; server + RLS both required | Code-first, generated config, SQL-first, or another controlled single source | Broad production RLS implementation and final policy code layout |
| Action vocabulary | Examples exist, full catalog does not | Approve versioned action/resource key inventory and governance | Production policy coverage |
| Platform admin/support matrix | Roles exist, exact actions absent | Define explicit user/admin/support permissions | Production admin/support routes |
| Organization role matrix | owner/admin/recruiter exist; exact actions absent | Define approved action matrix; decide status of deferred member/viewer values | Production org actions |
| Owner-facts DTOs | Need is confirmed, exact contracts vary | Define per-owner minimal facts and versions | Each consumer integration |
| SH-015 decision envelope | Proposed shared contract | Approve exact shared shape or define Role-compatible stable contract | Cross-gate result standardization |
| Denial presentation | 403/404/redaction/domain denial not universal | Root/data-owner rule for target-existence protection | HTTP/UI translation, not pure policy evaluation |
| U-CL01-15 step-up action governance | Sensitive action enum exists elsewhere | Define extension/governance and Role obligation matrix | Step-up-required production actions |
| U-CL01-17 sensitive access audit matrix | AccessAuditLog exists; exact required actions absent | Determine which allowed/denied attempts require SH-030 vs SH-029/logging and failure semantics | Audit completeness |
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

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. `context/shared/shared-operations.md`;
5. `context/clusters/identity-authority-consent-entitlements/architecture.md`;
6. `context/clusters/identity-authority-consent-entitlements/build-plan.md`;
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
