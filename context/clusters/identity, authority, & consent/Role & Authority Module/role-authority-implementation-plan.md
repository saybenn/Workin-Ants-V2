# Role & Authority Module Implementation Plan

> **Module ID:** `role_authority`  
> **Module:** Role & Authority Module  
> **Primary Cluster:** `CL-01 Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/modules/role_authority/implementation-plan.md`  
> **Companion architecture:** `role_authority/module-architecture.md`  
> **Cluster dependency:** subordinate to `context/clusters/identity-authority-consent-entitlements/build-plan.md`  
> **Implementation posture:** build the canonical permission interpreter and its enforcement/parity layer without absorbing Identity, Organization Hiring, Messaging, business-resource, Audit, healthcare, entitlement, consent, or compliance truth.

---

## Core Principle

Implement Role & Authority through narrow, verifiable slices:

```text
observable protected behavior
→ validated authorization request
→ trusted actor from Identity
→ minimum source-owner authority facts
→ Role-owned policy evaluation
→ typed authorization decision
→ server/RLS enforcement
→ canonical audit/step-up support where required
→ contract / parity / negative tests
→ exit gate
```

The Module does not need a user-facing product surface to be complete. Its primary observable product is the canonical `SH-002 authorizeResourceAction` decision and consistent enforcement of that decision across protected server paths and PostgreSQL RLS where applicable.

The Module implementation must preserve this distinction:

```text
Identity proves who is acting.
Role & Authority decides whether that actor may attempt this protected action.
The source Module supplies relationship truth.
The action-owning Module still owns entitlement, consent, readiness, compliance, contextual access, and lifecycle mutation.
```

---

## Build Rules

1. Follow root Workin Ants architecture, code standards, CL-01 architecture, and the Canonical Shared Operations Registry.
2. This Module owns only the policy truth declared in `module-architecture.md`.
3. Do not create `OrganizationMember`, `OrganizationRole`, or `ThreadParticipant` mutation logic in Role & Authority under PR-CL01-02.
4. Do not create Role repositories for foreign lifecycle records.
5. Consume source-owner facts through approved public interfaces / owner-facts DTOs; direct cross-domain Prisma reads are not the normal integration path.
6. `SH-002 authorizeResourceAction` is the canonical public authorization capability. Scoped convenience functions may only adapt to it.
7. Reuse `SH-001` for actor resolution; never parse sessions or trust browser role claims locally.
8. Reuse `SH-003` owner-facts contracts where approved; do not build a universal polymorphic authority repository.
9. Do not merge entitlement, consent, readiness, holds, healthcare redaction, payment, contextual file access, or business transition policy into Role.
10. Unknown actions/resources/policies fail closed.
11. Missing or unavailable authoritative facts never result in `allowed`.
12. Server authorization and RLS/helper-function enforcement must share one controlled semantic policy specification/test matrix.
13. No generic RBAC persistence is added until `U-CL01-16` is resolved and the Module architecture is updated.
14. Every server trust boundary validates action/resource/context input using root validation standards.
15. Client-provided `userId`, `role`, `isAdmin`, membership, participant, and ownership booleans are never authority proof.
16. Admin/support authority does not imply healthcare, financial, resume, legal-contract, or private-message payload access.
17. Authorization is synchronous. Do not create queues/workers for live permission evaluation.
18. Sensitive-access and audit effects use SH-029/SH-030; Role does not write Audit-owned tables.
19. Step-up assurance uses SH-014; Role does not own MFA/passkey/OTP challenge state.
20. No persistent authorization cache is introduced without explicit invalidation and security architecture.
21. Every numbered feature ends with automated tests, workflow/contract verification, documentation/progress updates, and an explicit exit gate.
22. If a feature reaches an unresolved decision, stop at the approved boundary. Do not settle security policy by implementation convenience.
23. Do not start the next numbered feature until the previous exit gate passes, except for explicitly tracked work in the canonical owner of a dependency.

---

## Preconditions

### Hard platform dependencies

Before production enforcement, the project must provide or approve the canonical contracts for:

- server-side runtime validation;
- request/correlation context;
- Identity & Access actor resolution — SH-001;
- Role & Authority public authorization contract — SH-002, implemented by this plan;
- structured logging and metadata sanitization — SH-032/033/034;
- Audit append and sensitive-access commands — SH-029/030 for affected features;
- PostgreSQL RLS migration/test conventions;
- root error/result conventions;
- test runner and database integration environment.

### Hard Module dependencies

- **Identity & Access:** trusted ActorContext and current `UserRole` / `PlatformRole` facts.
- **Organization Hiring:** read-only organization membership authority facts before organization-scoped production policies.
- **Messaging:** read-only thread participant facts before participant-scoped production policies.
- **Resource owners:** typed owner/participant fact contracts for ownership-scoped policies before each such consumer is enabled.

### Dependencies that may initially be stubbed

Full neighboring workflows do not have to be complete. Contract fakes may stand in for:

- Organization Hiring membership facts;
- Messaging participant facts;
- Transaction / Order participant facts;
- Candidate Application / Resume access context;
- Job Interview participant context;
- Healthcare secondary policy;
- Media contextual access;
- Admin Review / Compliance Hold;
- Audit / Event Ledger;
- step-up assurance.

The fake must implement the canonical contract. It must not cause Role to become the temporary owner of the dependency.

### Architecture decision gates

These decisions must be resolved before the affected production feature crosses the boundary:

- **PR-CL01-02:** organization membership and thread participant ownership split, or implementation stays read-only exactly as described in Cluster architecture.
- **U-CL01-16:** source of authorization policy before broad production RLS bindings are committed.
- **Initial action/resource vocabulary:** approve versioned keys and governance before consumers rely on them.
- **Platform admin/support matrix:** approve action distinctions before production admin/support authorization.
- **Organization role/action matrix:** approve owner/admin/recruiter permissions before production organization actions.
- **SH-015 decision envelope:** approve shared shape or explicitly freeze a compatible Role public contract.
- **U-CL01-15:** step-up action governance before Role emits production step-up obligations for newly classified actions.
- **U-CL01-17:** sensitive access audit matrix and failure semantics before claiming audit completeness.
- **Denial presentation:** root/data-owner rule before final 403/404/redaction behavior is wired broadly.

---

# Phase 1 — Contracts and Authority Policy Foundation

## 01 Canonical Authorization Contract and Module Skeleton

### Objective

Create the Role & Authority code boundary, the typed SH-002 request/result contract, the authorization scope model, and fail-closed dispatch without introducing any foreign repository, permission table, or business policy.

### Observable Result

A protected test harness can submit a trusted actor plus typed action/resource request and receive a deterministic `allowed`, `denied`, `step_up_required`, or `unavailable`-compatible decision envelope. Unknown actions/resources fail closed. No production policy matrix beyond explicitly approved fixture actions is required yet.

### Cluster Build-Plan Link

Supports **CL-01 Feature 02 — Resource Authorization Contract and RLS Parity**. Depends on the actor context produced by CL-01 Feature 01.

### Dependencies

- prior Cluster Feature 01 actor resolver contract;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-003 `queryOwnerFacts` contract pattern — Proposed;
- SH-015 `returnDecisionResult` — Proposed;
- root validation/result conventions;
- `module-architecture.md` ownership rulings.

### In Scope

- `modules/role-authority` logical folder structure;
- typed `AuthorizationActionKey`, `AuthorizationResourceType`, `AuthorizationScope` contract;
- typed `AuthorizationRequest` and `AuthorizationDecision`;
- controlled policy ID/version field shape;
- base `authorizeResourceAction` application service;
- pure scope classifier;
- policy registry/dispatcher interface that requires explicit coverage;
- owner-facts port interfaces without implementations for foreign truth;
- fail-closed unknown action/resource behavior;
- contract and policy-coverage tests.

### Out of Scope

- exact complete platform/admin/support matrix;
- organization role matrix;
- thread or business ownership policy details;
- RLS SQL/helper functions;
- audit writes;
- step-up challenge flow;
- generic RBAC tables;
- business/readiness/entitlement/consent/hold policy;
- public UI.

### Module-Owned Data

No Prisma data.

Module-owned controlled contract artifacts:

- action/resource vocabulary shell;
- scope semantics;
- decision reason namespace shell;
- policy ID/version convention;
- policy coverage registry.

### Public Interfaces

Introduce:

```text
authorizeResourceAction(request) → AuthorizationDecision
```

The stable public result must include at least:

- outcome;
- reason code;
- scope;
- policy identifier/version;
- evaluation timestamp;
- safe optional obligation metadata.

If SH-015 is not yet approved, keep the Role result structurally compatible and mark any divergence in architecture before consumers adopt it.

### Shared Operations Used

#### SH-001 — `resolveAuthenticatedActor`

- **Owner:** Identity & Access.
- **Invocation:** test/server adapter resolves actor before calling SH-002.
- **Local policy:** none; Role trusts the typed actor contract only.
- **Prohibited duplicate:** current-user/session parser.

#### SH-002 — `authorizeResourceAction`

- **Owner:** Role & Authority.
- **Invocation:** implemented by this feature.
- **Local policy:** contract, dispatch, scope, fail-closed behavior.
- **Prohibited duplicate:** secondary `authorizeAction` engine.

#### SH-003 — `queryOwnerFacts`

- **Owner:** each source Module; Proposed shared contract.
- **Invocation:** define ports only; actual integrations occur later.
- **Local policy:** required fact shapes are policy-specific.
- **Prohibited duplicate:** universal cross-domain repository.

#### SH-015 — `returnDecisionResult`

- **Owner:** shared contract; Proposed.
- **Invocation:** result envelope compatibility.
- **Local policy:** Role reason/outcome semantics.
- **Prohibited duplicate:** ad-hoc boolean per consumer.

### Domain Logic

1. Require a trusted actor object at the Role service boundary.
2. Validate action/resource keys against the controlled registry.
3. Classify the action into one explicit authorization scope.
4. Resolve the registered policy handler for that action.
5. If policy/fact requirements are absent or unknown, return fail-closed denial/unavailable.
6. Return only base authority semantics; do not call entitlement/readiness/etc.
7. Every registered action must declare its required scope and fact contract.
8. No default “admin allows everything” rule exists.

### Authorization / Compliance

This feature establishes the authorization capability but does not yet claim complete policy coverage. No sensitive access audit is required for contract-only fixtures unless root test policy says otherwise.

### Database / Transaction Behavior

- no migrations;
- no Role repository;
- no direct Prisma reads;
- no lock/idempotency record;
- pure policy evaluation is replayable.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

No product UI. A test-only/internal contract harness is acceptable. Do not expose a production endpoint that leaks policy internals.

### Failure Behavior

- unknown action → denied/fail closed;
- unknown resource type → denied/fail closed;
- malformed request → validation error before policy;
- missing actor → unauthenticated at the server adapter, not a forged Role actor;
- missing policy handler → policy unavailable/misconfigured, never allow;
- SH-015 unresolved → preserve local compatible contract and record decision rather than invent incompatible shape.

### Tests

- request schema validation;
- action/resource registration;
- scope classifier;
- unknown action/resource negative tests;
- policy coverage registry test;
- result contract snapshot/compatibility tests;
- negative test proving no foreign repository dependency;
- type-level contract tests where project standards support them.

### Documentation Updates

- update Module architecture if action/resource naming convention becomes binding;
- update Shared Operations only if SH-002/SH-015 canonical contract itself changes;
- update progress tracker with Feature 01 status.

### Acceptance Criteria

- SH-002 has one callable public boundary;
- every known fixture action has an explicit policy registration;
- unknown actions fail closed;
- result contains stable scope/reason/policy metadata;
- no Prisma model/migration/repository is added;
- no business gate appears in the policy service;
- no competing authorization API exists.

### Exit Gate

Before Feature 02:

- typecheck/lint/unit/contract checks pass;
- policy coverage test passes;
- unknown-action tests pass;
- code review confirms zero foreign lifecycle repositories;
- public contract is documented;
- any unresolved SH-015 divergence is recorded and does not leak to multiple consumers.

---

## 02 Platform Role Policy and Admin / Support Boundary

### Objective

Implement explicit platform-scoped authority from Identity-owned `UserRole` / `PlatformRole` facts, including a non-superuser distinction between `admin`, `support`, and ordinary users.

### Observable Result

For the initial approved platform action catalog, an authenticated actor receives deterministic decisions based only on trusted Identity role facts. Forged browser role claims have no effect. Support is denied admin-only actions unless the approved matrix explicitly allows them.

### Cluster Build-Plan Link

Supports **CL-01 Feature 02 — Resource Authorization Contract and RLS Parity** and establishes the admin/support policy foundation used by later CL-01 and cross-Cluster features.

### Dependencies

- Module Feature 01;
- Identity actor/role-facts contract;
- current `PlatformRole` vocabulary;
- approved initial platform action catalog;
- approved admin/support action matrix or a deliberately limited fail-closed subset.

### In Scope

- `evaluatePlatformPermission` pure policy;
- platform action policy registry entries;
- explicit user/admin/support matrix for approved actions;
- admin/support workflow-entry semantics;
- stable denial reason codes;
- tests proving no client role spoofing;
- tests proving sensitive-data secondary gates remain external.

### Out of Scope

- changing UserRole rows;
- creating/removing platform roles;
- step-up challenge lifecycle;
- healthcare payload policy;
- financial data policy;
- resume disclosure/business access policy;
- moderation lifecycle;
- organization role policy;
- RLS implementation (Feature 06).

### Module-Owned Data

No persisted data. Owned policy artifacts:

- platform action matrix;
- platform reason codes;
- policy version bump when matrix changes.

### Public Interfaces

No new public engine. Approved platform actions are evaluated through SH-002.

An Identity role-facts input contract may be versioned if actor context does not already include sufficient trusted role facts.

### Shared Operations Used

#### SH-001 — `resolveAuthenticatedActor`

Identity supplies trusted actor. Do not re-query provider sessions.

#### SH-002 — `authorizeResourceAction`

Role evaluates platform scope. Do not add `requireAdmin()` as a second policy system.

#### SH-015 — `returnDecisionResult` if approved

Use stable role-insufficient/missing-policy outcomes; do not expose raw role-table details.

### Domain Logic

1. Actor must be trusted.
2. Platform roles are sourced only from Identity-owned truth.
3. The action key selects the required platform authority.
4. `admin` and `support` are evaluated separately.
5. `user` does not inherit admin/support actions.
6. No global admin wildcard is allowed unless a future explicit architecture ruling approves it.
7. Base platform authority does not bypass target-specific owner/participant/context gates unless the action policy expressly defines an administrative entry path.
8. Administrative entry never itself authorizes healthcare/financial/resume/contract/private-message payload disclosure.

### Authorization / Compliance

Before production implementation, the exact initial admin/support matrix must be approved in architecture or the feature is limited to safe fixture actions. If a sensitive action also requires step-up, Feature 07 will compose Identity assurance; do not implement MFA here.

### Database / Transaction Behavior

No Role writes or migrations. Identity-owned role truth may be supplied in actor context or through an approved read interface. Role must not own a `UserRoleRepository`.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

No product UI. Any dev policy inspector must be non-production or separately admin-authorized and must not expose sensitive target facts.

### Failure Behavior

- no trusted role facts → denied/unavailable;
- unknown platform action → fail closed;
- support attempts admin-only action → denied;
- actor claims admin in request but Identity says user → Identity truth wins;
- Identity facts unavailable → unavailable, not allowed.

### Tests

- complete approved platform matrix unit test;
- ordinary user negative matrix;
- admin/support distinction;
- forged role/request body tests;
- unknown action fail-closed;
- no sensitive-payload bypass test fixtures;
- policy version/reason-code contract test.

### Documentation Updates

- record the approved platform action catalog and admin/support matrix in Module architecture or a governed policy artifact referenced by it;
- update unresolved-decision table if this feature settles part of the matrix;
- update progress tracker.

### Acceptance Criteria

- platform authority derives only from Identity truth;
- approved actions have explicit rules;
- support does not inherit all admin authority;
- no `isAdmin`/`requireAdmin` independent engine exists;
- no data-sensitivity gate is absorbed;
- negative matrix tests pass.

### Exit Gate

- initial platform/admin/support matrix is architecturally approved or production exposure remains limited to approved fixture scope;
- all platform matrix tests pass;
- spoof tests pass;
- no Identity lifecycle writes exist in Role;
- public SH-002 contract remains unchanged or versioned intentionally.

---

## 03 Organization-Scoped Authority Facts and Role Policy

### Objective

Implement organization-scoped permission interpretation using Organization Hiring-owned membership/role facts without transferring membership lifecycle ownership into Role & Authority.

### Observable Result

An actor with an approved role in Organization A can perform only the approved actions in Organization A. The same actor receives no authority in Organization B unless Organization Hiring supplies a valid membership there. Role never creates, updates, or removes `OrganizationMember`.

### Cluster Build-Plan Link

Supports **CL-01 Feature 02** and the later **CL-01 Phase 4 Cross-Cluster Contract Proof** bridge `OrganizationMember owner facts → Role authority`.

### Dependencies

- Module Features 01–02;
- PR-CL01-02 read-only ownership split;
- Organization Hiring owner-facts contract/test fake;
- current `OrganizationRole` vocabulary;
- approved owner/admin/recruiter action matrix for enabled production actions;
- SH-003 owner-facts pattern.

### In Scope

- organization authority facts DTO;
- owner-facts port for Organization Hiring;
- `evaluateOrganizationPermission` pure policy;
- exact target-organization scoping;
- approved role/action matrix;
- organization missing/suspended/unusable fact semantics as provided by owner;
- cross-org isolation tests;
- contract version tests.

### Out of Scope

- Organization creation;
- membership invitation;
- member addition/removal;
- role assignment/change;
- Job lifecycle rules;
- organization commercial feature access/entitlements;
- candidate/application lifecycle;
- direct OrganizationMember Prisma reads in Role production code.

### Module-Owned Data

No persisted data.

Owned policy artifacts:

- organization action matrix;
- policy reason codes and version;
- required owner-facts contract shape from Role's perspective.

### Public Interfaces

No new public engine; SH-002 receives organization-scoped actions.

Inbound owner contract conceptually provides only policy-relevant facts, for example:

```text
organizationId
actorUserId
membership exists / usable
OrganizationRole
optional owner-approved flags required by a specific action
```

Do not standardize fields the owner cannot authoritatively supply.

### Shared Operations Used

#### SH-002 — `authorizeResourceAction`

Canonical entry point for organization actions.

#### SH-003 — `queryOwnerFacts`

- **Owner:** Organization Hiring implementation.
- **Invocation:** Role requests membership facts for the exact organization/action.
- **Local policy:** Role interprets the returned role.
- **Prohibited duplicate:** Role-owned OrganizationMember repository.

#### SH-032/033/034

Use request context and sanitized logging for owner-facts outages and denied decisions; never log full organization/member payloads unnecessarily.

### Domain Logic

1. Action must be registered as organization-scoped.
2. Target organization ID is required and validated.
3. Role requests current membership facts from Organization Hiring.
4. Membership in any other organization is irrelevant.
5. Role interprets only current approved `OrganizationRole` values.
6. Deferred/commented enum values do not receive inferred policy.
7. Unknown/unusable membership state fails closed.
8. Organization feature availability, Track entitlement, Job compliance, and business lifecycle remain separate.

### Authorization / Compliance

The organization role matrix is a required architecture decision. If not yet approved, production actions depending on it remain disabled while contract/pure mechanism tests may proceed.

### Database / Transaction Behavior

- no Role migration for membership;
- no membership lock or mutation;
- no direct foreign Prisma repository;
- action owner re-authorizes close to the mutation boundary;
- future RLS parity is Feature 06.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

None owned.

### Failure Behavior

- no membership → denied;
- insufficient role → denied;
- membership service unavailable → unavailable/fail closed;
- wrong organization → denied regardless of another valid membership;
- unknown role value → denied/misconfiguration;
- membership changes during action → action owner/RLS current-state enforcement controls final mutation.

### Tests

- owner/admin/recruiter approved action matrix;
- cross-org isolation;
- missing membership;
- wrong role;
- unknown role;
- owner-facts outage;
- contract version mismatch;
- negative test proving Role cannot mutate OrganizationMember/OrganizationRole;
- later parity fixtures prepared for Feature 06.

### Documentation Updates

- record approved organization matrix;
- update PR-CL01-02 status if formally accepted;
- document owner-facts DTO version in both Role and Organization Hiring public-interface context;
- update progress tracker.

### Acceptance Criteria

- organization authority is exact-scope;
- Organization Hiring remains lifecycle owner;
- no role value is granted policy by default;
- no direct foreign repository exists;
- all positive and negative organization tests pass.

### Exit Gate

- PR-CL01-02 is approved or code is provably read-only under its proposed split;
- enabled organization action matrix is approved;
- cross-org isolation tests pass;
- mutation-prohibition test passes;
- owner-facts contract is versioned and documented.

---

## 04 Participant and Resource-Ownership Policy Composition

### Objective

Implement participant- and ownership-scoped Role policies using owner-supplied facts, beginning with Messaging thread participation and extending through typed owner contracts for Order/Application/Interview/Profile contexts without building a universal authority repository.

### Observable Result

A thread participant can receive the approved thread base-authority decision while an unrelated user cannot. Resource-owner fixtures can authorize only actors proven by the source Module's typed facts. Admin exceptions are explicit actions, not a global bypass.

### Cluster Build-Plan Link

Supports **CL-01 Feature 02** and prepares the cross-Cluster bridges later proven in CL-01 Phase 4.

### Dependencies

- Features 01–03;
- Messaging participant owner-facts contract;
- PR-CL01-02;
- owner-facts contracts or fixtures for initial business resources;
- approved participant/ownership action vocabulary.

### In Scope

- participant facts port;
- `evaluateThreadParticipantAccess`;
- generic policy interface for typed owner facts without generic data repository;
- `evaluateResourceOwnership`;
- explicit administrative exception path where approved;
- initial domain adapters that map consumer actions to SH-002 while leaving policies central;
- negative tests for unrelated actor/target.

### Out of Scope

- adding/removing thread participants;
- reading/writing messages;
- contextual Media grant/signed URL logic;
- resume business-disclosure policy;
- Order entitlement/business transition;
- JobInterview lifecycle;
- Profile eligibility;
- healthcare payload access;
- creating one polymorphic `ResourceOwnership` table/repository.

### Module-Owned Data

No persisted data. Owned policy contracts:

- participant action policy;
- ownership-policy interface;
- required owner-facts shapes per registered action.

### Public Interfaces

SH-002 remains the public API.

Allowed thin typed adapters may include names such as:

- `authorizeResumeAction`
- `authorizeOrderAction`
- `authorizeInterviewAction`

only if they immediately translate domain action/context into SH-002 and contain **no independent permission matrix**.

### Shared Operations Used

#### SH-002 — `authorizeResourceAction`

All participant/ownership policies route through it.

#### SH-003 — `queryOwnerFacts`

Each source Module implements its facts query. Role defines only minimum contract requirements.

### Domain Logic

**Thread participant:**

1. validate thread action and target;
2. obtain current participant fact from Messaging;
3. allow only if policy grants the participant action;
4. administrative access must use an explicit admin/support action, not fake participant status.

**Resource ownership:**

1. action declares its owner-facts contract;
2. source owner supplies the relevant actor/profile/participant relationships;
3. Role evaluates the relationship required by that action;
4. ownership does not imply readiness/entitlement/status permission;
5. missing/ambiguous owner facts fail closed.

### Authorization / Compliance

- private-message payload access may require additional contextual/sensitive policy after Role;
- resume access requires Resume Privacy/business context after base authority;
- Media access requires SH-026/context owner + Media mechanics after Role;
- admin authority does not bypass healthcare redaction.

### Database / Transaction Behavior

No Role DB writes or foreign repositories. No durable ownership cache. Consumer mutations re-authorize at server boundary.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

- nonparticipant → denied;
- participant source unavailable → unavailable;
- unknown ownership basis → denied;
- multiple contradictory owner facts → unavailable/conflict rather than choose permissive result;
- admin action not explicitly registered → denied;
- consumer attempts to pass `isOwner=true` without owner source → validation/policy denial.

### Tests

- thread participant read/post fixture matrix;
- unrelated user denial;
- explicit admin exception tests if approved;
- owner-fact contract tests for initial resource adapters;
- spoofed owner boolean tests;
- missing/contradictory owner facts;
- negative test proving no ThreadParticipant mutation/repository;
- negative test proving no universal polymorphic repository.

### Documentation Updates

- document each adopted owner-facts contract in dependency interfaces;
- update action vocabulary and policy coverage;
- record unresolved resource-specific facts instead of broadening DTOs ad hoc;
- update progress tracker.

### Acceptance Criteria

- participant/ownership policy executes only from source-owned facts;
- thin adapters do not duplicate policy;
- admin exceptions are explicit;
- contextual business gates remain external;
- all negative tests pass.

### Exit Gate

- Messaging contract is documented/tested;
- at least one ownership-scope contract fixture passes positive/negative tests;
- no foreign lifecycle code is present;
- policy coverage registry includes all enabled participant/ownership actions;
- Feature 01–04 unit/contract suites are green.

---

# Phase 2 — Server Enforcement and RLS Parity

## 05 Canonical Server Guard and Delivery-Adapter Enforcement

### Objective

Make protected Server Actions, Route Handlers, and server application services consume SH-002 through one canonical server-security adapter, with root-approved validation and safe denial translation.

### Observable Result

Representative protected endpoints cannot execute their application service when SH-002 denies or is unavailable. No client component or route-specific helper can bypass authority by supplying role/owner booleans.

### Cluster Build-Plan Link

Directly supports **CL-01 Feature 02 — Resource Authorization Contract and RLS Parity**.

### Dependencies

- Features 01–04;
- root server entry-point and validation conventions;
- root error/result pattern;
- SH-001 actor resolver;
- initial denial presentation ruling or a deliberately neutral server decision mapping pending that ruling.

### In Scope

- canonical `server/security/authority` adapter;
- request validation before policy call;
- actor resolution then SH-002 invocation;
- `enforceAuthorizationDecision` / `assertAuthorized` adapter semantics;
- representative server action/route integrations for each covered scope;
- privacy-safe response mapping according to approved root behavior;
- removal/prevention of feature-local broad permission helpers in covered paths.

### Out of Scope

- rewriting every consumer Module in one feature;
- final cross-Cluster contract integration (Features 09–10);
- RLS SQL (Feature 06);
- UI authorization as security truth;
- business-gate composition beyond representative fixtures.

### Module-Owned Data

None.

### Public Interfaces

No new business interface. SH-002 remains authoritative.

The server guard accepts an SH-002 request or a typed adapter callback and either:

- returns the decision for application composition; or
- stops execution using root-approved denial behavior.

It must not become a second policy engine.

### Shared Operations Used

- SH-001 actor resolution;
- SH-002 Role authorization;
- SH-032 request context;
- SH-033 structured logging;
- SH-034 telemetry sanitization;
- SH-035 exception capture for unexpected policy/dependency failure.

### Domain Logic

1. validate action/resource input;
2. resolve actor server-side;
3. build request from trusted route/resource context;
4. invoke SH-002;
5. on `allowed`, return control to the action-owning application service;
6. on `step_up_required`, return/compose the approved obligation without starting a Role-owned challenge;
7. on denied/unavailable, stop protected work;
8. never execute business mutation and then authorize afterward.

### Authorization / Compliance

Denial presentation may need 403 versus privacy-preserving 404. If not resolved globally, do not invent route-specific behavior; use the approved neutral server error/result until the root/data-owner policy is settled.

### Database / Transaction Behavior

No Role transaction. Protected business mutation remains within the consumer's transaction. Authority must be evaluated immediately before or inside the consumer's approved mutation boundary as root architecture permits.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

UI may hide/disable actions for usability, but the browser never becomes enforcement truth. This feature owns no UI component.

### Failure Behavior

- invalid request → validation error;
- unauthenticated → authentication denial before SH-002;
- denied → stop before business service;
- unavailable → fail safe; do not continue optimistically;
- unexpected exception → safe server error + sanitized exception capture;
- unresolved 403/404 mapping → follow current root behavior and document pending decision.

### Tests

- representative Server Action guard tests;
- Route Handler guard tests;
- ensure application service is not called on denial;
- forged client actor/role/owner input tests;
- allowed path continues to separate business gate fixture;
- step-up required propagation;
- unavailable dependency stops action;
- safe error payload tests;
- no policy duplication in adapter.

### Documentation Updates

- document canonical server guard location/name;
- update consumer integration guidance;
- update denial behavior decision if settled;
- update progress tracker.

### Acceptance Criteria

- one server authority adapter is used for covered endpoints;
- no covered route has independent broad role logic;
- denied/unavailable requests cannot reach business mutation;
- UI state is not treated as enforcement;
- safe errors/logging verified.

### Exit Gate

- server guard integration tests pass;
- representative platform/org/participant/ownership endpoints are covered;
- no route-local `isAdmin`/`isOwner` policy engine remains in covered code;
- denial translation conforms to the approved root rule or remains explicitly deferred without insecure fallback.

---

## 06 RLS Policy Bindings and Server / Database Parity

### Objective

Implement database-side authorization bindings for the approved RLS coverage set and prove that server SH-002 decisions and PostgreSQL RLS/helper functions express the same authority semantics.

### Observable Result

For every protected policy in the Feature 06 coverage set, parity fixtures produce the same allow/deny outcome through the server policy and the database/RLS path. A direct database path cannot gain authority the server would deny.

### Cluster Build-Plan Link

Completes the core requirement of **CL-01 Feature 02 — Resource Authorization Contract and RLS Parity**.

### Dependencies

- Features 01–05;
- **U-CL01-16 resolved** for production implementation;
- root Prisma/migration/RLS convention;
- Identity-approved DB actor/session context;
- approved RLS coverage list;
- coordination with each table-owning Module for policies applied to its tables.

### In Scope

- selected policy source/generation/binding implementation;
- Postgres helper functions / RLS policy bindings as approved;
- parity fixture framework;
- parity tests for platform/org/participant/ownership policies in scope;
- CI policy coverage check;
- safe rollout/migration strategy;
- performance review of policy predicates.

### Out of Scope

- changing foreign lifecycle ownership;
- adding generic permission tables unless U-CL01-16 explicitly selected that architecture;
- business readiness/entitlement RLS masquerading as Role policy;
- using RLS to replace owner-specific business access decisions not owned by Role;
- direct browser CRUD outside root architecture.

### Module-Owned Data

No business data. Infrastructure may include:

- Role-owned semantic policy source or generated bindings as chosen by architecture;
- parity fixtures;
- migration functions/policies coordinated with table owners.

### Public Interfaces

SH-002 remains the application interface.

Database interfaces are controlled RLS/helper functions, not a second public business API.

### Shared Operations Used

- SH-001 semantics for trusted actor identity;
- SH-002 semantic policy;
- SH-003 owner facts where DB-side policy can safely query/derive the equivalent source-owned relationship;
- SH-032/033/034 for migration/test diagnostics only.

Do not create a new shared operation for each SQL predicate.

### Domain Logic

1. A single approved semantic policy source/matrix defines action meaning.
2. Server and RLS implementations derive from or are tested against that same source.
3. RLS never grants an action absent from the action registry.
4. Organization predicates include exact organization scope.
5. Participant predicates include exact context scope.
6. Administrative bypasses are explicit and narrow.
7. Role RLS does not bypass healthcare, sensitive Media, resume, or other owner-specific secondary policy.
8. Any table whose protected access cannot be safely expressed by Role alone must compose the owner-specific RLS/policy rather than broaden Role.

### Authorization / Compliance

- service-role/database maintenance exceptions follow root security rules, not ad-hoc Role bypasses;
- parity is a security exit gate;
- database actor identity cannot come from arbitrary request variables controlled by the client.

### Database / Transaction Behavior

- migrations are reviewed with affected data owners;
- helper functions are stable, security-reviewed, and schema-qualified according to root standards;
- no RLS function performs lifecycle writes;
- indexes needed for membership/participant predicate performance are proposed to the record owner and migrated under approved ownership;
- migration rollback/forward safety is documented.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

- server/RLS mismatch → CI/feature failure; no release;
- policy source cannot generate/bind → fail deployment;
- missing actor DB context → deny by default;
- unsupported action at DB layer → deny;
- performance regression → do not weaken predicate; optimize with owner-approved indexes/design.

### Tests

- server/RLS parity matrix for every covered action;
- cross-org RLS denial;
- participant removed → RLS denial;
- user/admin/support cases where DB path applies;
- direct DB bypass attempts;
- unknown action/function misuse;
- service-role boundary tests per root security policy;
- migration from clean DB and realistic data;
- policy query performance smoke tests.

### Documentation Updates

- resolve and document U-CL01-16;
- document RLS coverage set and semantic-source strategy;
- document table-owner coordination/migrations;
- update Cluster architecture if the chosen policy source is Cluster-significant;
- update progress tracker.

### Acceptance Criteria

- U-CL01-16 is no longer unresolved for implemented scope;
- every covered RLS policy has a server parity fixture;
- no independent SQL permission matrix exists without parity governance;
- no foreign lifecycle ownership moved;
- direct DB paths cannot bypass covered Role authority.

### Exit Gate

- all parity tests pass;
- clean/upgrade migration tests pass;
- RLS security review passes;
- no broad admin/service bypass was added;
- performance is acceptable without weakening policy;
- CL-01 Feature 02 requirements are demonstrably satisfied for the enabled action set.

---

# Phase 3 — Step-Up and Sensitive Access Support

## 07 Step-Up Obligation Composition

### Objective

Integrate Identity-owned fresh-assurance requirements into Role decisions without moving MFA/passkey/OTP challenge state into Role & Authority.

### Observable Result

For an approved sensitive authority action, an actor with sufficient base role/relationship authority but insufficient fresh assurance receives `step_up_required`; after Identity establishes the approved `SensitiveActionSession` or equivalent assurance, SH-002 can return the normal base authority result. Unrelated actions/targets do not inherit that step-up proof.

### Cluster Build-Plan Link

Supports the boundary between **CL-01 Feature 02** and **CL-01 Feature 03 — Security Posture, Passkeys, and Step-Up Assurance**.

### Dependencies

- Features 01–06;
- SH-014 Identity step-up contract;
- **U-CL01-15** governance resolved for actions enabled here;
- approved action-to-assurance matrix;
- Identity assurance facts/result contract.

### In Scope

- Role policy obligation metadata for approved sensitive actions;
- server guard composition with SH-014;
- action/target-scoped assurance checks;
- expiration/revocation response handling from Identity;
- tests proving step-up does not expand base authority.

### Out of Scope

- StepUpChallenge persistence;
- OTP sending/verification;
- passkey provider behavior;
- account recovery;
- security-session revocation policy owned by Identity;
- inventing new StepUpActionType values without governance.

### Module-Owned Data

No persisted data.

Owned policy truth: which approved Role action requires which assurance obligation.

### Public Interfaces

SH-002 result may include `step_up_required` / assurance obligation compatible with the shared decision contract.

SH-014 remains Identity's public security interface.

### Shared Operations Used

#### SH-014 — `requireStepUpForSensitiveAction`

- **Owner:** Identity & Access.
- **Invocation:** after base authority is otherwise sufficient and the action's Role policy requires fresh assurance.
- **Local policy:** action/target requires step-up; Role does not define challenge internals.
- **Prohibited duplicate:** Role-owned MFA session or OTP service.

#### SH-002 — `authorizeResourceAction`

Base authority still determines whether step-up is meaningful. A user without base permission does not gain access merely by completing MFA.

### Domain Logic

1. Evaluate base role/relationship authority.
2. If base authority is denied, return denied; do not offer step-up as a privilege escalation path.
3. If allowed and action policy requires fresh assurance, check approved Identity assurance result.
4. If insufficient, return `step_up_required` with minimized action/target binding.
5. If sufficient, return allowed subject to remaining external business gates.
6. Assurance for one target/action cannot be reused for another unless Identity contract explicitly scopes it that way.

### Authorization / Compliance

Step-up is security proof, not role authority or business readiness. Exact action catalog requires architecture governance before production enablement.

### Database / Transaction Behavior

No Role writes. Identity owns all challenge/session state. Reauthorization occurs after step-up completion.

### Events / Jobs

None in Role. Identity may own security events separately.

### Provider Integration

None in Role; Identity owns passkey/OTP providers.

### UI / Admin Surface

Role owns no challenge UI. Consumer/Identity security shell presents step-up according to Identity design.

### Failure Behavior

- base authority denied → denied, not step-up;
- step-up service unavailable → unavailable/fail safe;
- expired/revoked assurance → step-up required;
- wrong action/target assurance → step-up required/denied;
- unknown sensitive action type → fail closed and architecture review.

### Tests

- base denied + valid MFA still denied;
- base allowed + no fresh assurance → step-up required;
- correct assurance → allowed;
- wrong target/action assurance denied;
- expiry/revocation;
- Identity outage;
- no Role security-state write.

### Documentation Updates

- record approved action-to-step-up matrix and U-CL01-15 resolution;
- update public decision contract if obligation fields become binding;
- update progress tracker.

### Acceptance Criteria

- Role never owns challenge/session state;
- step-up cannot elevate a role/relationship that is otherwise denied;
- assurance is action/target-scoped as approved;
- all negative security tests pass.

### Exit Gate

- U-CL01-15 resolved for enabled actions;
- SH-014 contract tests pass;
- no Role MFA/provider implementation exists;
- decision envelope communicates step-up without leaking secrets;
- server guard reauthorization path is proven.

---

## 08 Sensitive Access Audit Boundary

### Objective

Integrate Role-controlled sensitive/admin access paths with the Audit / Event Ledger through canonical commands, proving Role supplies decision context without owning `AccessAuditLog` or its append-only enforcement.

### Observable Result

For the approved audit matrix, required sensitive/admin access attempts generate the correct Audit-owner command with minimized actor/target/action/decision context. Role contains no direct `AccessAuditLog` insert and no local audit hash-chain implementation.

### Cluster Build-Plan Link

Supports **CL-01 Feature 02**, CL-01 Phase 4 guardrail integration, and **CL-01 Feature 16** audit/access-proof hardening.

### Dependencies

- Features 01–07;
- SH-029 / SH-030 Audit contracts;
- **U-CL01-17 sensitive-access matrix resolved for enabled paths**;
- Audit owner's decision on general access-decision vocabulary / schema compatibility;
- SH-034 telemetry/audit sanitization.

### In Scope

- mapping from approved Role actions/outcomes to SH-029 or SH-030;
- minimized audit request DTO;
- request/correlation IDs;
- allowed/denied audit behavior according to approved matrix;
- failure semantics according to the approved audit policy;
- integration tests with Audit owner/fake;
- explicit prohibition of direct Audit table writes.

### Out of Scope

- `AccessAuditLog` schema ownership;
- hash chaining/immutability implementation;
- retention policy;
- healthcare-specific payload access decision;
- general domain lifecycle events;
- operational logging as substitute for audit.

### Module-Owned Data

None.

### Public Interfaces

No new Role public command.

Outbound interfaces:

- SH-029 `appendAuditEvent`;
- SH-030 `recordSensitiveAccess`.

### Shared Operations Used

#### SH-029 — `appendAuditEvent`

Use for authority/policy/security changes classified by the audit matrix.

#### SH-030 — `recordSensitiveAccess`

Use for access attempts/completions classified as sensitive.

#### SH-032 / SH-034

Request ID and metadata sanitization are mandatory in audit requests.

### Domain Logic

1. SH-002 produces the base authority decision.
2. Action/audit classification determines whether audit is required.
3. Role sends only approved metadata to Audit.
4. Data-owner sensitivity/context is supplied where needed; Role does not infer sensitive payload from arbitrary fields.
5. Audit acknowledgement is not authority truth.
6. Failure behavior follows the explicit approved matrix; mandatory evidence must never be silently skipped.

### Authorization / Compliance

This feature supports “append-only sensitive access audit” compliance but does not claim ownership of the append-only proof. Audit / Event Ledger remains responsible for immutability, chain fields, permissions, and retention.

### Database / Transaction Behavior

No direct Role database writes. If the audit owner requires synchronous append before access completion, the caller follows that canonical contract. If deferred audit is approved for some cases, durability belongs to Audit/platform infrastructure, not a Role queue.

### Events / Jobs

No Role event/job. Audit may internally use its own mechanisms.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

Must be explicitly specified in U-CL01-17 resolution. Possible classes to distinguish:

- mandatory sensitive audit unavailable;
- optional administrative audit unavailable;
- malformed Audit request;
- duplicate request/correlation attempt.

Role must not catch-and-ignore mandatory audit failures.

### Tests

- allowed sensitive action audit;
- denied-attempt audit where matrix requires;
- non-sensitive action does not spam access audit;
- sanitized payload;
- correct request ID/correlation;
- direct Audit table import/write prohibited by architecture test/lint review;
- audit outage behavior per approved matrix;
- healthcare-specific decision remains external.

### Documentation Updates

- resolve U-CL01-17 for enabled scope;
- update Role and Audit public-interface docs if contract changes;
- document access-decision vocabulary handling;
- update progress tracker.

### Acceptance Criteria

- required Role-sensitive paths use canonical Audit commands;
- Role owns no audit schema/repository/hash chain;
- audit payload is minimized and sanitized;
- failure behavior is explicit and tested;
- operational logs are not counted as audit proof.

### Exit Gate

- U-CL01-17 resolved for production-enabled paths;
- Audit integration tests pass;
- direct-write prohibition is verified;
- mandatory evidence cannot be silently lost;
- no healthcare/general decision-vocabulary collision is hidden in Role code.

---

# Phase 4 — Module Integration Proof

## 09 Organization Hiring, Candidate, Job Interview, and Messaging Contract Proof

### Objective

Prove Role & Authority works with its highest-dependency owner-fact Modules through public contracts rather than foreign repositories: Organization Hiring, Candidate Application & Resume Privacy, Job Interview, and Messaging.

### Observable Result

End-to-end contract fixtures prove organization management, candidate/resume base authority, interview base authority, and thread participant access use SH-002 plus owner-supplied facts. Negative cases fail safely, and Role mutates none of the neighboring source records.

### Cluster Build-Plan Link

Supports **CL-01 Phase 4 — Cross-Cluster Contract Proof (Features 13–15)**, especially `OrganizationMember / ThreadParticipant owner facts → Role authority`.

### Dependencies

- Features 01–08;
- Organization Hiring public owner-facts contract;
- Messaging participant facts contract;
- Candidate Application/Resume Privacy context contract;
- Job Interview context contract;
- approved action matrices for the exercised actions;
- contract test environment.

### In Scope

- real or versioned contract-test integrations for Organization Hiring facts;
- Messaging participant integration;
- candidate/application ownership context;
- interview organization/candidate/participant context;
- positive and negative workflows;
- proving secondary privacy/readiness gates remain in owners;
- contract version/error handling.

### Out of Scope

- implementing Hiring, Application, Interview, or Messaging lifecycle features;
- resume file access/signed URL mechanics;
- interview scheduling/video room logic;
- message lifecycle;
- organization membership mutation;
- broad refactor of neighboring Modules.

### Module-Owned Data

No persisted data.

Potentially expands only the approved action/resource vocabulary and Role policy matrix for these consumer actions.

### Public Interfaces

SH-002 unchanged or intentionally versioned.

Inbound owner-facts contracts are exercised with real owner modules when available; otherwise approved contract fixtures.

### Shared Operations Used

- SH-001 actor;
- SH-002 authority;
- SH-003 owner facts;
- SH-014 for any approved sensitive admin action;
- SH-030 where the audit matrix classifies access as sensitive;
- SH-032/033/034 safe correlation/telemetry.

### Domain Logic

Minimum scenarios:

1. **Organization management:** valid membership/role in target org → base authority; same role in different org → deny.
2. **Resume:** authorized organization relationship may pass Role; Resume Privacy still decides business/sensitive access and Media issues file access.
3. **Interview:** candidate/interviewer/org relationship supplies base facts; Job Interview owns schedule/status/join eligibility.
4. **Thread:** participant passes thread action; unrelated actor denied; approved admin entry does not become message-content bypass.

### Authorization / Compliance

- FCRA/resume disclosure policy remains Candidate Application & Resume Privacy/Consent-owned where applicable;
- healthcare-sensitive interview/message paths still require Healthcare policy;
- sensitive access audit follows Feature 08 matrix;
- organization feature entitlement remains separate from role permission.

### Database / Transaction Behavior

No direct cross-domain Prisma access in normal integration path. Contract tests may seed owner tables through their owning fixtures/setup, not through Role production repositories.

### Events / Jobs

None in Role.

### Provider Integration

None.

### UI / Admin Surface

Neighboring Modules own user/admin surfaces. E2E may traverse those surfaces to prove Role participation.

### Failure Behavior

- owner contract timeout → unavailable, not allow;
- stale/unsupported contract version → unavailable/deploy incompatibility;
- membership/participant removed → next authorization denies;
- resume/interview secondary gate denies after Role allows → owner denial controls final action;
- audit step fails where mandatory → follow Feature 08 behavior.

### Tests

- contract tests per owner;
- organization cross-scope matrix;
- resume base-authority + owner-secondary-denial test;
- interview candidate/interviewer/nonparticipant matrix;
- thread participant/nonparticipant/admin-secondary-gate matrix;
- dependency timeout/version mismatch;
- no foreign mutation test;
- E2E or integration journey for at least one organization and one thread path.

### Documentation Updates

- dependency public-interface sections;
- action/resource vocabulary;
- progress tracker;
- architecture only if contract proof settles or changes an unresolved owner-fact decision.

### Acceptance Criteria

- all four neighbors integrate through public contracts;
- no Role test requires Role-owned foreign repository to pass;
- secondary owner policies can deny after Role allows;
- cross-org/thread isolation is proven;
- audit/security boundaries remain intact.

### Exit Gate

- contract suites pass with real owner implementations or approved versioned fixtures;
- no direct foreign repository imports in Role production code;
- positive and negative integration paths are green;
- action vocabulary and owner-fact contracts are documented/versioned.

---

## 10 Transaction, Media, Moderation, Hold, and Healthcare Separation Proof

### Objective

Prove Role & Authority composes correctly with high-risk consumers without becoming transaction entitlement, contextual file access, moderation lifecycle, ComplianceHold truth, or healthcare redaction policy.

### Observable Result

Representative Order, Media, moderation/admin, hold-review, and healthcare-sensitive workflows demonstrate that SH-002 supplies only base actor authority. Each downstream owner can independently deny or constrain the action after Role allows it.

### Cluster Build-Plan Link

Supports **CL-01 Phase 4 — Cross-Cluster Contract Proof (Features 13–15)** and the cross-Cluster authority rail consumed by CL-04, CL-05, and CL-09.

### Dependencies

- Features 01–09;
- Transaction / Order owner-facts contract;
- SH-026 contextual resource access owner contract for applicable Media/etc. flows;
- Media / File Access public access interface;
- Admin Review / Compliance Hold decision interface;
- Content Moderation admin action contract;
- Healthcare admin access/readiness contract;
- Audit integration from Feature 08.

### In Scope

- Order buyer/professional/admin base authority contract proof;
- Media contextual authority composition proof;
- moderation/admin workflow-entry authority;
- ComplianceHold review entry authority while hold lifecycle remains external;
- healthcare admin entry followed by healthcare allow/redact/block/deny;
- sensitive audit proof where required;
- negative tests proving Role allow is not sufficient for final access.

### Out of Scope

- Order lifecycle/payment/refund/dispute logic;
- signed URL generation;
- Media scanning/storage;
- moderation case lifecycle;
- hold creation/release lifecycle;
- healthcare provider/readiness/redaction implementation;
- payment/entitlement/consent logic.

### Module-Owned Data

No persisted data. Only approved policy/action registrations may be added.

### Public Interfaces

SH-002 remains stable.

No `authorizeMediaUrl`, `canRefund`, `canViewPHI`, or similar cross-domain policy becomes a Role source-of-truth operation.

### Shared Operations Used

- SH-001 actor;
- SH-002 authority;
- SH-003 owner facts;
- SH-026 contextual resource access — **external context-owner operation, not absorbed**;
- SH-011 ComplianceHold — external gate where workflow requires it;
- SH-020 Healthcare readiness/access owner interface as applicable — external;
- SH-029/030 audit;
- SH-032/033/034 observability.

### Domain Logic

**Order:** Role evaluates actor/participant authority; Order still evaluates transaction state/entitlement.

**Media:** Role evaluates actor; context owner evaluates business entitlement; Media validates asset/access and issues signed URL.

**Moderation/Hold:** Role permits admin/support workflow entry according to exact action matrix; moderation/hold owner controls case/hold transition.

**Healthcare:** Role permits base admin workflow entry; Healthcare separately returns allow/redact/block/deny for payload.

No consumer may interpret `PlatformRole.admin` as universal sensitive data access.

### Authorization / Compliance

- active ComplianceHold may block a downstream action even if Role allows it;
- healthcare policy may redact/deny after Role allows entry;
- sensitive access audit may be mandatory;
- payment/entitlement/consent gates remain owner-composed.

### Database / Transaction Behavior

Role writes no foreign records. Integration tests seed/operate neighboring truth through owner APIs/fixtures. RLS parity must not create an admin bypass around secondary owner RLS policies.

### Events / Jobs

No Role events/jobs.

### Provider Integration

None.

### UI / Admin Surface

Neighboring Modules own UI. E2E can prove admin/support buttons/actions do not bypass server/secondary gates.

### Failure Behavior

- Role allows but contextual owner denies → final action denied;
- Role denies → no downstream sensitive access attempt;
- Media owner unavailable → no signed access;
- Hold/Healthcare dependency unavailable → workflow fails according to its owner contract, not Role allow;
- support attempts admin-only moderation action → Role denies;
- admin attempts sensitive payload without healthcare authorization → Healthcare denies/redacts.

### Tests

- Order participant matrix + transaction secondary denial;
- Role allow + SH-026 deny for Media;
- Role allow + Media state deny;
- admin/support moderation matrix;
- hold review entry vs hold lifecycle separation;
- healthcare allow/redact/block/deny after identical Role base allow;
- sensitive audit checks;
- no direct Stripe/Media/Healthcare/provider clients in Role;
- E2E representative high-risk flow.

### Documentation Updates

- dependency contract sections;
- audit/healthcare separation examples;
- action matrix as approved;
- progress tracker.

### Acceptance Criteria

- Role allow is demonstrably only one gate;
- no provider or foreign lifecycle implementation appears in Role;
- admin/support cannot bypass sensitive secondary policy;
- Media signed access requires Media/context owner after Role;
- negative integration paths pass.

### Exit Gate

- all high-risk separation tests pass;
- no Role code mutates Order/Media/Hold/Moderation/Healthcare truth;
- no admin superuser bypass is present;
- Audit integration is complete for the enabled sensitive paths;
- CL-01 Phase 4 Role bridges are proven.

---

# Phase 5 — Module Hardening and Production Verification

## 11 Authorization Hardening, Reconciliation, and Production Readiness

### Objective

Harden the complete Role & Authority capability against policy drift, stale facts, spoofing, dependency outages, RLS mismatch, sensitive-data leakage, contract incompatibility, and performance regressions without adding new business ownership.

### Observable Result

Production readiness checks prove that all enabled protected actions use the canonical authority path, server/RLS outcomes match for covered policies, unavailable facts never grant permission, no feature-local broad permission engines remain in audited scope, and sensitive/admin access produces the required Audit evidence without exposing protected payloads.

### Cluster Build-Plan Link

Supports **CL-01 Feature 16 — Hardening and Production Readiness** and closes Role-specific requirements from CL-01 Feature 02 and Phase 4.

### Dependencies

- Features 01–10;
- all production-enabled architecture decisions resolved;
- complete enabled action/resource registry;
- real owner-facts contracts for production consumers;
- real Audit/Identity/Ops integrations;
- approved RLS coverage set;
- production-like database/test environment.

### In Scope

- full action-policy coverage audit;
- server/RLS parity suite in CI;
- privilege-escalation and confused-deputy tests;
- owner-facts outage/degradation tests;
- stale membership/participant/ownership checks;
- admin/support boundary review;
- step-up and audit completeness;
- telemetry redaction review;
- query/predicate performance;
- migration/backfill safety for RLS changes;
- dependency contract compatibility;
- dead code/duplicate permission helper search and removal plan;
- production deployment/checklist.

### Out of Scope

- adding new product actions solely for coverage;
- new permission database without architecture decision;
- new caching system unless performance evidence requires it and architecture approves invalidation;
- refactoring neighboring business lifecycles;
- provider features;
- policy analytics product.

### Module-Owned Data

No new business data.

Review and freeze for release:

- action/resource registry;
- policy IDs/versions;
- role/relationship matrices;
- reason-code contract;
- RLS binding coverage;
- parity fixtures.

### Public Interfaces

Revalidate:

- SH-002 request/result backward compatibility;
- owner-facts contract versions;
- SH-014 obligation integration;
- SH-029/030 audit integration.

Breaking changes require explicit version/migration planning rather than silent edits.

### Shared Operations Used

Revalidate all Role-consumed shared operations:

- SH-001 actor resolution;
- SH-002 authorization;
- SH-003 owner facts;
- SH-014 step-up;
- SH-015 decision envelope if approved;
- SH-029/030 audit;
- SH-032/033/034/035/036 observability.

No alternate hardening helper may bypass these contracts.

### Domain Logic

Production invariants to prove:

1. every enabled protected action has an explicit policy;
2. unknown actions fail closed;
3. every enabled owner-fact dependency has a typed versioned contract;
4. cross-organization/thread/resource isolation holds;
5. support and admin remain explicit, separate authority classes;
6. secondary sensitive/business gates cannot be bypassed by Role allow;
7. revoked/changed authority is reflected on the next protected request;
8. no stale persistent allow cache exists;
9. server and RLS policy versions are compatible;
10. audit/step-up requirements are complete for enabled actions.

### Authorization / Compliance

Security review must include:

- privilege escalation;
- IDOR/resource-scope mistakes;
- admin/support overreach;
- healthcare/financial/resume/private-message separation;
- audit evidence completeness;
- denial target-existence behavior;
- service-role/RLS boundaries;
- action registry governance.

### Database / Transaction Behavior

- verify RLS migrations from clean DB and representative existing data;
- review helper-function permissions/security definer behavior according to root rules;
- verify indexes/predicate performance with owners;
- no cross-domain write permissions introduced for Role;
- no in-memory lock/cache used as authority truth.

### Events / Jobs

None. Verify no accidental authorization event/queue system has appeared.

### Provider Integration

None. Verify no provider SDK dependency has entered Role.

### UI / Admin Surface

No Role product UI required. E2E verifies consumer UI cannot bypass server enforcement and does not expose actions as proof of permission.

### Failure Behavior

Exercise at least:

- Identity unavailable;
- owner-facts service unavailable;
- unsupported contract version;
- malformed owner facts;
- policy registration missing;
- RLS/server mismatch;
- Audit unavailable under mandatory and nonmandatory classes;
- step-up unavailable/expired;
- safe-denial presentation;
- logging/metrics backend failure without permission elevation.

No failure mode may default to allow.

### Tests

- complete policy matrix unit suite;
- public contract tests;
- contract compatibility tests;
- full RLS parity integration suite;
- direct DB bypass tests;
- cross-org/thread/resource isolation;
- spoof/IDOR/privilege-escalation security tests;
- step-up tests;
- sensitive audit tests;
- healthcare/financial/resume/private-message secondary-gate tests;
- telemetry redaction tests;
- dependency outage tests;
- migration tests;
- performance tests for hot authorization paths;
- Playwright/E2E participation in representative protected workflows;
- source scan/code review for prohibited duplicate helper names/patterns.

### Documentation Updates

- resolve every production-blocking Module unresolved decision;
- synchronize Module architecture and implementation plan with actual policy-source/RLS strategy;
- update dependent public-interface docs;
- update Shared Operations only for genuine canonical contract changes;
- update CL-01 architecture/build plan only if Cluster-level assumptions changed;
- update progress tracker and production readiness report.

### Acceptance Criteria

- all production-enabled actions are explicitly registered and covered by tests;
- no owner fact or policy failure grants permission;
- no lifecycle has moved into Role;
- no duplicate broad permission subsystem exists in the reviewed production scope;
- RLS/server parity is green;
- sensitive audit/step-up behavior is complete for enabled actions;
- no protected payload/secret leakage appears in logs;
- performance meets project requirements without permissive caching;
- all production-blocking unresolved decisions are closed or affected actions remain disabled.

### Exit Gate

Role & Authority is production-ready for the enabled scope only when:

- typecheck, lint, unit, contract, integration, RLS, security, audit, privacy/redaction, E2E, and production build checks pass;
- every enabled action has explicit policy and policy-version coverage;
- server/RLS parity passes with no unexplained mismatch;
- no feature-local broad permission helper is needed for covered actions;
- OrganizationMember/OrganizationRole/ThreadParticipant remain externally owned and read-only from Role;
- no generic permission/RBAC table was introduced without approved architecture;
- mandatory sensitive-access evidence cannot be silently skipped;
- step-up cannot elevate denied base authority;
- admin/support cannot bypass sensitive secondary gates;
- dependency outages fail safe;
- documentation and progress tracker match implementation.

---

# Module Integration Phase

Features **09–10** are the explicit Module integration phase.

The minimum public-contract proofs are:

```text
Identity actor + platform roles → Role SH-002
Organization Hiring membership facts → organization authority
Messaging participant facts → thread authority
Candidate/Application facts → base resume/application authority
JobInterview facts → base interview authority
Order participant facts → base order authority
Role authority + SH-026 contextual owner decision → Media access path
Role admin/support authority + Hold owner → compliance-review path
Role admin/support authority + Healthcare owner → sensitive payload decision
Role decision + Audit owner → required access proof
```

The integration phase must prove **composition rather than absorption**. A downstream owner is allowed to deny after Role permits base authority. That is correct behavior, not a conflict.

Integration tests must use public contracts or versioned fixtures. They must not reach into neighboring repositories simply to make a workflow pass.

---

# Module Hardening Phase

Feature **11** is the hardening phase. It must cover only Role & Authority production risk:

- action-policy coverage drift;
- admin/support privilege escalation;
- organization/participant/resource scope isolation;
- stale/revoked owner facts;
- owner-facts dependency outage;
- server/RLS semantic drift;
- service-role/direct DB bypass risk;
- step-up obligation correctness;
- sensitive audit completeness;
- telemetry redaction;
- denial target-existence leakage;
- contract version compatibility;
- migration/RLS rollout safety;
- authorization hot-path performance;
- prohibited duplicate permission helpers.

Hardening must not add a new Role lifecycle, decision ledger, queue, provider adapter, or mutable permission cache.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Contracts and Authority Policy Foundation | 01–04 |
| 2 | Server Enforcement and RLS Parity | 05–06 |
| 3 | Step-Up and Sensitive Access Support | 07–08 |
| 4 | Module Integration Proof | 09–10 |
| 5 | Module Hardening and Production Verification | 11 |

**Total numbered features: 11.**

### Cluster alignment summary

- Module Features 01–06 primarily implement **CL-01 Feature 02 — Resource Authorization Contract and RLS Parity**.
- Module Feature 07 composes with the Identity-owned **CL-01 Feature 03** step-up foundation without taking ownership.
- Module Feature 08 supplies the Role side of CL-01 audit/access-proof requirements.
- Module Features 09–10 implement the Role portion of **CL-01 Phase 4 Cross-Cluster Contract Proof**.
- Module Feature 11 implements the Role portion of **CL-01 Feature 16 Hardening and Production Readiness**.

The Module plan does not reorder the Cluster plan. If the Cluster plan changes sequencing, this Module plan must be reconciled rather than followed independently.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture.
2. Read root code standards.
3. Read the Canonical Shared Operations Registry.
4. Read CL-01 architecture and build plan.
5. Read this Module architecture and implementation plan.
6. Read public-interface sections for all direct dependencies used by the feature.
7. Confirm the prior Module feature exit gate passed.
8. Confirm the referenced Cluster feature/milestone permits this work now.
9. Confirm no unresolved architecture decision blocks the production behavior.
10. Write the concise Required Feature Implementation Specification below.
11. Implement only this numbered feature.
12. Run required quality checks and contract/workflow verification.
13. Update progress; update architecture only when a binding decision legitimately changed; record unresolved risks.

No coding agent may use a feature implementation specification to silently change source-of-truth ownership or Shared Operation ownership.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a feature-specific specification containing:

- **Objective** — one concrete result.
- **Observable result** — what can be tested or observed after the slice.
- **Cluster build-plan link** — exact Cluster feature/milestone supported.
- **Dependencies** — prior Module features, owner interfaces, schema/migration needs, canonical Shared Operations.
- **In scope** — only work required for this slice.
- **Out of scope** — explicit ownership leakage and deferred work.
- **Owned data affected** — normally no Role Prisma records; list controlled policy artifacts and any approved RLS bindings.
- **Public contracts** — SH-002 and dependency contract changes.
- **Shared operations consumed** — permanent SH IDs, invocation points, local policy, prohibited duplicate.
- **Permissions/compliance** — actor, scope, owner facts, step-up/audit requirements, and secondary gates that remain external.
- **Primary workflow** — request → actor → facts → policy → decision → enforcement/support effect.
- **Provider integration** — normally `None`; if not none, stop and verify architecture because Role currently owns no providers.
- **Jobs/events** — normally `None`; any addition requires architecture justification.
- **Idempotency/concurrency** — current-fact evaluation, stale-fact behavior, mutation-boundary reauthorization, RLS parity.
- **Error behavior** — validation, denied, unavailable, misconfigured policy, owner dependency failure, audit/step-up failure if applicable.
- **Tests** — exact unit/contract/RLS/integration/security tests for the feature.
- **Acceptance criteria** — observable, binary checks.
- **Documentation updates** — Module/Cluster/shared/dependency/progress files affected.

Do not generate all feature specifications in advance. The implementation specification must reflect the repository and governing architecture at the moment the feature begins.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed**
- **Cluster build-plan link**
- **Files added**
- **Files changed**
- **Database changes**
- **Migrations**
- **Dependencies added**
- **Module public interfaces added/changed**
- **Owner-facts contracts added/changed**
- **Action/resource/policy vocabulary added/changed**
- **Shared operations reused**
- **RLS/helper-function changes**
- **Events/jobs added**
- **Provider adapter changes**
- **Tests added/changed**
- **Commands run**
- **Manual/contract verification**
- **RLS/server parity result where applicable**
- **Security/negative-path verification**
- **Documentation updated**
- **Assumptions**
- **Known failures**
- **Remaining risks**
- **Deferred work**
- **Unresolved architecture items encountered**
- **Exit-gate result: PASS / FAIL**

A completion report that says “tests pass” without listing the executed checks is insufficient for a security capability.

---

# Final Quality Check

Before considering this Module plan complete or a production scope finished, verify:

1. Role & Authority source truth has exactly one owner: this Module owns policy interpretation, not foreign lifecycles.
2. `UserRole` / `PlatformRole` remain Identity-owned structurally.
3. `OrganizationMember` / `OrganizationRole` remain Organization Hiring-owned under the governing split.
4. `ThreadParticipant` remains Messaging-owned under the governing split.
5. No neighboring lifecycle was absorbed for implementation convenience.
6. SH-002 is the canonical public authority interface.
7. Every owner-fact read uses an approved public contract rather than an unapproved foreign repository.
8. No entitlement, consent, readiness, payment, hold, healthcare, contextual Media, or business-lifecycle rule was reimplemented in Role.
9. Server and RLS policies use one controlled semantic source/matrix and pass parity tests.
10. Unknown/missing policy or facts fail closed.
11. Admin/support permissions are explicit and do not create a sensitive-data superuser.
12. Step-up assurance remains Identity-owned.
13. Audit / AccessAuditLog remains Audit-owned and mandatory proof is not silently skipped.
14. Role contains no external provider client.
15. Authorization contains no background-worker dependency.
16. No persistent mutable allow cache became authority truth.
17. Audit evidence, domain events, and observability remain distinct.
18. Privacy orchestration remains Privacy-owned; no unnecessary Role subject-data store was introduced.
19. No search projection or Media signed-access mechanism was added here.
20. Every numbered feature has automated tests and an explicit exit gate.
21. Module feature order still aligns with the current CL-01 build plan.
22. All production-blocking unresolved decisions are resolved or the affected behavior is explicitly disabled/fail-closed.
23. A coding agent can implement each remaining feature without inventing ownership, policy source, cross-Module persistence, or enforcement semantics.
