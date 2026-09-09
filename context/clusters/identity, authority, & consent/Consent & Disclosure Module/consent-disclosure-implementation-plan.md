# Consent & Disclosure Module Implementation Plan

> **Module ID:** `consent_disclosure`  
> **Module:** Consent & Disclosure Module  
> **Primary Cluster:** `CL-01 — Identity, Authority, Consent & Entitlements`  
> **Repository target:** `context/modules/consent_disclosure/implementation-plan.md`  
> **Companion:** `module-architecture.md`, CL-01 `architecture.md`, CL-01 `build-plan.md`, root Workin Ants context, Canonical Shared Operations Registry  
> **Implementation posture:** implement the current `ConsentLog` proof capability first; production consent-version catalog, withdrawal/re-consent, durable uniqueness, and destructive retention behavior remain architecture-gated rather than guessed in code.

---

## Core Principle

Implement Consent & Disclosure through narrow, verifiable slices:

```text
observable proof behavior
→ validated command/query
→ Consent-owned policy
→ authoritative ConsentLog write/read
→ canonical shared-operation calls
→ optional event/audit/notification effects
→ contract/integration tests
→ explicit exit gate
```

The Module does not need a large standalone UI. Its primary observable results are public commands/queries and durable proof. UI is required only for the reusable standalone-consent presentation capability and any explicitly approved self/admin history surface.

This plan is subordinate to the CL-01 build plan. It does not change Cluster sequencing, introduce a new consent lifecycle, or settle U-CL01 architecture gates by implementation convention.

---

## Build Rules

1. Follow root Workin Ants architecture, code standards, CL-01 architecture/build plan, and this Module architecture.
2. Implement only Consent-owned proof/versioning responsibilities.
3. Do not absorb authentication, authorization, verification, calendar, notification, agreement, digital-goods, healthcare, subscription, rewards/prizes, privacy orchestration, audit storage, search, or provider lifecycle truth.
4. Consume other Modules through approved public interfaces; do not import their repositories to make a slice easier.
5. Reuse canonical SH-### operations. If a shared primitive is not implemented, use its approved interface/test double or fix its canonical owner; do not create a Consent copy.
6. Every mutation has runtime validation, trusted actor resolution when applicable, server-side authorization for privileged operations, and transaction-safe writes.
7. `ConsentLog` is historical accepted proof. Do not add status booleans or mutate proof rows for ordinary product behavior.
8. Exact type/version matching is mandatory unless an approved future Consent policy explicitly defines compatibility.
9. Command retries use SH-044. Do not add a permanent uniqueness constraint until U-CL01-10 is resolved.
10. Raw IP addresses are never persisted in ConsentLog; SH-076 supplies privacy-safe hashing where evidence is approved.
11. Provider details stay outside this Module. There are no Consent-owned provider adapters in the current plan.
12. Cross-Module effects happen through public contracts or versioned events; Consent never writes another Module’s state.
13. Async effects, if introduced, use shared outbox/queue/retry mechanisms and remain idempotent/observable.
14. Privacy orchestration stays Privacy-owned. Consent implements only subject enumeration, retention facts, and owner execution.
15. No destructive Consent/User retention migration is enabled until U-CL01-11 is resolved.
16. No withdrawal/revocation/decline/re-consent lifecycle is implemented until U-CL01-09 is resolved.
17. No persistent active-version catalog schema is implemented until U-CL01-08 is resolved and `module-architecture.md`/CL-01 architecture are updated.
18. Every numbered feature ends with exact tests, documentation/progress update, and an exit gate.
19. Do not begin the next dependent feature while the previous exit gate is failing.
20. Unresolved architecture is surfaced, not silently settled in code.

---

## Preconditions

### Hard dependencies for Features 01–04

The following must exist as real implementations or approved stable contracts/test doubles:

- PostgreSQL/Prisma foundation with current `ConsentLog`, `ConsentType`, and `User` relationship;
- project runtime validation standard;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction` for privileged history access;
- SH-044 `executeIdempotentCommand`;
- SH-076 `normalizeAndHashIdentifier`;
- SH-032/033/034 request context/logging/sanitization;
- current CL-01 authority/RLS conventions sufficient to protect Consent tables and public interfaces.

### Architecture gates

These are hard gates only for the features that depend on them:

- **U-CL01-08** — must be resolved before Feature 05 persistent active-version catalog implementation.
- **U-CL01-09** — must be resolved before any withdrawal/revocation/re-consent state or command is added.
- **U-CL01-10** — must be resolved before final production database uniqueness/idempotency constraints are frozen in Feature 08.
- **U-CL01-11** — must be resolved before destructive privacy execution or retention-safe FK/cascade migration is enabled in Features 07–08.
- **U-CL01-17** — must be resolved before final sensitive-access audit matrix is declared complete.
- **U-CL01-25 / U-CD-01** — consumer-specific historical binding must be resolved before production Track/other consumer schemas are tightened around `consentLogId`.

### Dependencies that may initially be stubbed by contract

Full neighboring products do not block core Consent proof implementation. Approved contract fixtures/test doubles may stand in for:

- Trust Verification / Screening;
- Booking & Calendar;
- Notification;
- Transaction / Order;
- Digital Goods Access;
- Healthcare / Regulated Services;
- Track Subscription & Entitlement;
- Sweepstakes / Prize;
- Gamification / Rewards;
- Privacy / Data Erasure;
- Audit / Event Ledger and Observability / Ops.

A stub may prove a public boundary. It may not import or recreate the neighbor’s source model/lifecycle inside Consent.

### Provider setup

No external provider credentials are required for the core Module. Real provider integration belongs to consumer/provider-owning Modules and is intentionally outside this plan.

---

# Phase 1 — Proof Contracts and Source-of-Truth Foundation

## 01 Consent Module Boundary, Runtime Contracts, and Repository Foundation

Create the implementation boundary around the current `ConsentLog`/`ConsentType` source truth without introducing any missing versioning or withdrawal lifecycle.

### Objective

Make the Module’s ownership, runtime request/result schemas, repository boundary, and current Prisma invariants explicit enough that subsequent commands and queries cannot fall into direct cross-domain database access.

### Observable Result

- Tests can instantiate a Consent-owned repository/service boundary and read/write only `ConsentLog` through it.
- Public request/result contracts reject malformed types, blank versions, untrusted metadata, and unsupported fields.
- Consumers have a typed contract target rather than a reason to import `prisma.consentLog`.
- A schema review report confirms that no Consent status/withdrawal/version-catalog model is being invented in this feature.

### Cluster Build-Plan Link

Supports **CL-01 Phase 2 / Feature 07 — Version-Specific Consent Acceptance and Proof Query** and the Cluster requirement that public contracts replace direct foreign Prisma access.

### Dependencies

- current Prisma `ConsentLog`/`ConsentType`;
- root code standards and runtime validation;
- CL-01 authority/RLS rules;
- Canonical Shared Operations Registry.

### In Scope

- establish the feature-first Consent code boundary described in `module-architecture.md` CD-PR-01;
- define runtime schemas for `recordConsentProof`, `queryConsentProof`, and consent-history filtering/results;
- define public proof DTOs that exclude `ipHash`/`userAgent` by default;
- create Consent-owned repository methods needed by Features 02–03;
- document current indexes/relations and migration posture;
- add module-level architecture tests/import-boundary tests if the repository supports them;
- define stable domain error/result categories consistent with root standards.

### Out of Scope

- persistent consent-version catalog;
- current-version resolution;
- standalone UI;
- withdrawal/revocation/re-consent;
- permanent acceptance uniqueness constraint;
- Privacy destructive behavior;
- consumer-domain writes;
- provider clients or webhooks.

### Module-Owned Data

- reads current `ConsentLog` and `ConsentType` definitions;
- no required schema change in this feature;
- no new lifecycle/event/projection/snapshot model.

### Public Interfaces

Define contract shapes for:

- SH-007 `recordConsentProof`;
- SH-008 `queryConsentProof`;
- `listUserConsentHistory`.

The feature may expose test-only or internal repository methods, but those are not public cross-Module contracts.

### Shared Operations Used

- **SH-032 `createRequestContext` — platform:** establish correlation contract for public operations. Local policy: Consent operation names/IDs. **Prohibited duplicate:** `consentRequestContext.ts`.
- **SH-034 `sanitizeTelemetryMetadata` — Observability/Ops:** define safe logging envelope. Local policy: Consent-specific redaction. **Prohibited duplicate:** Consent redaction framework.
- SH-001/002/044/076 are declared as dependencies and mocked/contract-tested here; their actual workflow invocation is completed in Features 02–03.

### Domain Logic

- version is a required nonblank identifier, not a “latest” alias;
- public proof DTO never returns raw request evidence;
- `ConsentType` comes from the canonical enum, not a consumer-specific string union;
- existence of a ConsentLog is accepted proof only; no status inference is allowed;
- normal repository API exposes insert/read/list but no generic update/delete product method.

### Authorization / Compliance

- repository methods are not direct browser APIs;
- public delivery surfaces must later enforce actor/authority before repository access;
- direct consumer imports are treated as an architecture violation;
- `ConsentType.age_gate` receives no eligibility semantics here.

### Database / Transaction Behavior

- use current indexes and relations;
- do not add `@@unique([userId,type,version])`;
- do not alter `onDelete: Cascade` in this feature because U-CL01-11 is unresolved;
- no transaction beyond ordinary repository test setup is required yet.

### Events / Jobs

None. No event or worker is justified by this foundation slice.

### Provider Integration

Not applicable. No provider code may be added.

### UI / Admin Surface

None.

### Failure Behavior

- malformed request/result schema → validation error;
- unsupported enum value → validation error;
- repository unexpectedly receives an update/delete operation → test/design failure;
- unresolved schema question → recorded architecture gate, not migration guess.

### Tests

- runtime schema valid/invalid cases;
- proof DTO redaction test;
- repository insert/read/list integration test;
- import-boundary test or review proving consumers do not get a public Prisma repository;
- test proving no update lifecycle API exists for ConsentLog;
- Prisma migration/schema smoke test;
- RLS/table-access baseline test if RLS is already enforced at this stage.

### Documentation Updates

- update progress tracker with Feature 01 completion;
- update `module-architecture.md` only if the real repository structure forces an approved binding change;
- record any discrepancy between current migrations and the documented ConsentLog shape.

### Acceptance Criteria

- all public request/result contracts are runtime-validated;
- safe proof DTO contains only approved fields;
- one Consent-owned repository boundary exists;
- no new Consent status/version/withdrawal schema was created;
- no direct foreign repository dependency was introduced.

### Exit Gate

Pass only when schema/runtime/contract tests, typecheck/lint/build checks applicable to the repo, and the ownership review pass. Feature 02 may not begin if the repository boundary still permits consumer code to bypass the canonical command path by design.

---

## 02 Version-Specific Consent Acceptance Command

Implement SH-007 against current `ConsentLog` with trusted actor identity, server-owned evidence metadata, and command-level idempotency.

### Objective

A signed-in User can explicitly accept one exact consent type/version and receive durable proof without retries creating uncontrolled duplicate side effects.

### Observable Result

- An authenticated User submits an exact type/version acceptance and receives a `consentLogId`, type, version, and `acceptedAt`.
- The row is persisted with the authenticated User ID, server time, and approved hashed request evidence.
- Replaying the same semantic command returns the existing command result according to SH-044 behavior.
- Consent acceptance does not activate any consumer feature.

### Cluster Build-Plan Link

Direct implementation of **CL-01 Phase 2 / Feature 07 — Version-Specific Consent Acceptance and Proof Query**.

### Dependencies

- Feature 01 exit gate;
- SH-001 actor resolver;
- SH-044 idempotent command primitive;
- SH-076 request-identifier hashing;
- SH-032/034 request context/sanitization;
- current ConsentLog schema.

### In Scope

- implement SH-007 `recordConsentProof` application command;
- derive User subject from SH-001 for ordinary self acceptance;
- validate exact type/version and explicit acceptance intent;
- capture server time;
- hash raw IP/request identifier through SH-076 when policy says it is collected;
- copy only approved user-agent evidence to ConsentLog;
- use SH-044 around the mutation;
- return a safe proof result;
- optionally prepare a transaction hook for future SH-046 event publication without requiring an event now.

### Out of Scope

- active version lookup;
- consumer-supplied “latest” version resolution;
- decline/withdraw/revoke behavior;
- permanent DB uniqueness constraint;
- provider callbacks;
- consumer state transitions;
- general audit event for every acceptance unless the Audit policy explicitly requires it.

### Module-Owned Data

Writes `ConsentLog` only.

No enum addition is required unless a separately approved product feature adds a new `ConsentType`; such an enum change is not bundled into this feature.

### Public Interfaces

- SH-007 `recordConsentProof` becomes implemented/stable for current schema.

Recommended semantic result:

```text
proofId
userId (only where contract requires it)
type
version
acceptedAt
replayed: boolean or equivalent idempotency metadata if root standard exposes it
```

Do not expose `ipHash`/`userAgent` in the ordinary result.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor` — Identity:** resolve accepting User. Local policy: self acceptance only unless future explicit system path approved. **Do not build:** `consentAuth.ts`.
- **SH-044 `executeIdempotentCommand` — platform:** retry safety. Local policy: semantic acceptance key while U-CL01-10 remains unresolved. **Do not build:** `consentIdempotency.ts` or a Consent idempotency table.
- **SH-076 `normalizeAndHashIdentifier` — shared security:** hash IP/request evidence. Local policy: whether/which evidence is required. **Do not build:** `hashIp.ts`.
- **SH-032 / SH-034 — request context/sanitization:** correlation and safe telemetry. **Do not build:** local context/redaction framework.
- **SH-029 `appendAuditEvent` — Audit:** only if the approved Audit matrix requires a separate material event. Local policy: safe IDs/action. **Do not build:** Consent audit ledger.

### Domain Logic

1. resolve actor;
2. validate `ConsentType`, exact version, and explicit acceptance;
3. reject client attempts to choose another self-acceptance subject;
4. establish idempotency context;
5. derive trusted evidence metadata;
6. insert ConsentLog in the command transaction;
7. return safe proof;
8. perform optional supporting effects through canonical interfaces only.

A generic Terms acceptance cannot be silently substituted for a different type such as `fcra_background_check` or `electronic_signature_consent`.

### Authorization / Compliance

- authenticated actor required for account-bound proof;
- User subject mismatch is forbidden;
- no proof created from passive page view;
- no consumer action can be made successful solely by this command;
- FCRA/e-sign/calendar/etc. standalone presentation requirement is not bypassed merely because SH-007 can accept any valid type.

### Database / Transaction Behavior

- one source transaction inserts ConsentLog;
- if an event is later approved, source row + outbox entry must commit atomically;
- no in-memory lock;
- SH-044 replay semantics protect retries;
- no new unique constraint until U-CL01-10;
- preserve current relations/indexes.

### Events / Jobs

No event is required for Feature 02. If a real durable consumer is already approved, use SH-046 inside the source transaction with a minimized, versioned event contract; otherwise query-first remains the default.

No worker.

### Provider Integration

Not applicable.

### UI / Admin Surface

No full UI required. A developer/test harness or the later Feature 04 presentation shell may call this command.

### Failure Behavior

- unauthenticated → `UNAUTHENTICATED`;
- subject spoof → `FORBIDDEN`;
- invalid type/blank version/no explicit acceptance → `VALIDATION_ERROR`;
- same idempotency key + same semantic request → replay prior success;
- same key + materially different request → `IDEMPOTENCY_CONFLICT` according to platform contract;
- hashing primitive unavailable when required → fail command rather than store raw IP;
- database failure → no proof result and no fabricated consumer effect.

### Tests

- successful exact acceptance;
- accepted User equals SH-001 actor;
- other-user spoof denied;
- invalid enum/blank version denied;
- raw IP never stored or logged;
- hashed evidence test vector/integration through SH-076;
- optional/no-IP behavior where collection not required;
- same-key replay test;
- same-key/different-payload conflict test;
- simultaneous replay test;
- proof result redaction;
- test that no consumer record changes after acceptance;
- transaction rollback test.

### Documentation Updates

- progress tracker;
- public-interface documentation for SH-007;
- if actual SH-044 semantics force a decision about U-CL01-10, stop and update architecture rather than implicitly choosing permanent uniqueness.

### Acceptance Criteria

- exact User/type/version/acceptedAt are persisted;
- approved request evidence is privacy-safe;
- command retries are bounded/idempotent;
- no consumer lifecycle changes;
- no permanent uniqueness decision is smuggled into the migration.

### Exit Gate

Feature 02 passes when SH-007 contract/integration/idempotency/security tests pass and code review confirms no raw IP, direct foreign writes, or local idempotency implementation. Feature 03 may then expose reads against this proof.

---

## 03 Exact Proof Query and Authorized Consent History

Implement SH-008 and safe self/admin history so all consumers can stop querying ConsentLog directly.

### Objective

Provide one authoritative exact-version proof query plus a privacy-safe history query, with Role / Authority controlling privileged access.

### Observable Result

- A consumer asks for User + ConsentType + required version and receives `PROOF_FOUND` with proof reference or a stable negative result.
- A User can read their own safe consent history.
- An authorized admin/support actor can read another User’s permitted history; unauthorized actors cannot.
- Wrong versions never fall back to an older/other accepted version.

### Cluster Build-Plan Link

Completes the read side of **CL-01 Phase 2 / Feature 07**.

### Dependencies

- Features 01–02;
- SH-001;
- SH-002;
- Audit SH-030 only if U-CL01-17 or an approved interim matrix requires it;
- current ConsentLog indexes/RLS.

### In Scope

- implement SH-008 exact proof query;
- optionally support proof-by-ID lookup within the same public contract where useful;
- implement paginated/filterable `listUserConsentHistory`;
- enforce self vs privileged subject access;
- redact request evidence by default;
- define stable negative reason codes;
- add query plan/index tests.

### Out of Scope

- “latest accepted” as a substitute for exact required version;
- active-version catalog;
- broad compliance reporting/export warehouse;
- exposing IP hash/user agent in normal UI;
- consumer business decisions;
- `AccessAuditLog` policy beyond approved U-CL01-17 ruling.

### Module-Owned Data

Reads `ConsentLog`; no schema mutation required unless query-plan evidence later justifies an index change. Any index migration remains Consent-owned and must be measured.

### Public Interfaces

- SH-008 `queryConsentProof`;
- `listUserConsentHistory`;
- optional authorized internal/admin `listConsentAcceptancesByVersion` only if a concrete compliance/admin use case exists; do not create it merely for completeness.

### Shared Operations Used

- **SH-001 — Identity:** self actor context.
- **SH-002 — Role / Authority:** privileged history/query authorization. Local policy: Consent supplies action + subject facts. **Do not build:** `consentHistoryPermissions.ts`.
- **SH-030 — Audit / Event Ledger:** sensitive access only if policy requires. **Do not build:** local access log.
- **SH-032/033/034/036 — Ops:** safe correlation, logging, latency/error metrics.

### Domain Logic

- exact User + type + required version match is the canonical positive proof condition for current schema;
- if multiple historical rows exist for the same type/version, return the proof selected by documented query semantics (normally one valid accepted proof/reference) without pretending duplication is a status lifecycle;
- negative query does not create state;
- `terms:v1` does not satisfy `fcra_background_check:v1`;
- proof existence does not imply consumer action allowed.

### Authorization / Compliance

- consumer server-to-server/internal calls must be authenticated/authorized according to root service boundary;
- self history is self-only;
- other-user history uses SH-002;
- sensitive evidence fields stay hidden unless a separately authorized query exists;
- U-CL01-17 remains visible as the final access-audit completeness gate.

### Database / Transaction Behavior

Read-only queries. Use indexes for `[userId,type,acceptedAt]` and `[type,version]` plus selective filters. No table scan should become the default for hot exact-proof queries.

If query analysis shows a composite index is necessary, add a narrowly justified migration owned by Consent; do not invent uniqueness.

### Events / Jobs

None.

### Provider Integration

Not applicable.

### UI / Admin Surface

Optional minimal self-history page and/or admin history view may consume the queries. If the Cluster has no UI shell yet, contract tests are sufficient. The view must not become a source-truth editor.

### Failure Behavior

- wrong/missing version → typed negative result, not fallback;
- unauthorized subject → `FORBIDDEN` without revealing whether proof exists;
- malformed filters → validation error;
- database unavailable → `DEPENDENCY_UNAVAILABLE`/internal failure with correlation ID;
- access-audit failure follows Audit policy; do not silently broaden access.

### Tests

- exact proof found;
- wrong-version negative;
- wrong-type negative;
- proof-by-ID safe result if supported;
- multiple historical rows behavior;
- self history pagination/filtering;
- other-user denial;
- authorized admin/support access;
- evidence-field redaction;
- U-CL01-17 instrumentation fixture if applicable;
- query/index plan/performance smoke test;
- test proving consumer cannot infer downstream status from result shape.

### Documentation Updates

- publish SH-008 contract details;
- document history authorization action names;
- update progress tracker;
- record any approved index change.

### Acceptance Criteria

- all enabled consumers can use SH-008 instead of direct ConsentLog queries;
- exact matching is deterministic;
- safe history access is server-authorized;
- request evidence is not exposed by ordinary DTOs;
- query performance is acceptable for the expected hot path.

### Exit Gate

Feature 03 passes when contract, authorization/RLS, negative-version, redaction, and performance tests pass. Core current-schema Consent proof is then usable independently of the missing version catalog.

---

# Phase 2 — Standalone Presentation and Version Governance

## 04 Reusable Standalone Consent Presentation with Explicit Version Descriptor

Build the canonical standalone presentation shell without pretending the missing active-version catalog exists.

### Objective

Allow high-risk consumer workflows to present one trusted exact disclosure/version separately, collect explicit acceptance, and route the result through SH-007.

### Observable Result

- A consumer passes a trusted server-created presentation descriptor containing exact type, version, and approved content/content reference.
- The user sees a dedicated accessible disclosure surface and must affirmatively accept before SH-007 is called.
- Cancel/decline leaves no false ConsentLog acceptance.
- The shell works for representative screening, calendar, electronic-signature, healthcare, and push disclosure fixtures without embedding their provider logic.

### Cluster Build-Plan Link

Supports **CL-01 Feature 07** minimal reusable acceptance surface and prepares **Feature 08 — Consent Version Catalog and Standalone Consent Presentation**.

### Dependencies

- Features 02–03;
- SH-010 contract;
- approved UI/accessibility standards;
- a trusted server source for the explicit descriptor in test/consumer integration.

### In Scope

- reusable standalone presentation component/application boundary;
- descriptor runtime schema: consent type, exact version, safe content/content reference, title/labels/accessibility fields as approved;
- explicit accept action that calls SH-007;
- explicit cancel/not-accepted result;
- display the exact version to the user;
- consumer context/correlation that is not persisted as generic Consent truth unless architecture says so;
- component/interaction accessibility tests.

### Out of Scope

- hard-coded consumer version constants as a permanent solution;
- persistent catalog or “latest” version lookup;
- recording decline/withdrawal as domain truth;
- browser notification permission prompts;
- Cronofy/screening/e-sign/Stripe handoffs;
- consumer workflow state transitions;
- legal copy authorship inside code.

### Module-Owned Data

No new model. Successful acceptance writes ConsentLog through Feature 02. Cancel/decline writes no new Consent-owned state under the current schema.

### Public Interfaces

- SH-010 `presentStandaloneConsent` application/UI contract;
- calls SH-007 for acceptance;
- may return `{accepted: false, reason: USER_CANCELLED}` as transient UI result, but that is not stored decline proof.

### Shared Operations Used

- **SH-010 `presentStandaloneConsent` — Consent:** this feature implements the reusable shell. Local policy: exact descriptor and affirmative action.
- **SH-007 — Consent:** acceptance write.
- **SH-001 — Identity:** accepting actor via command boundary.
- **SH-034 — telemetry sanitization:** do not log disclosure text/user action payloads unnecessarily.

SH-009 is deliberately **not** implemented in this feature.

### Domain Logic

- component renders the descriptor it was given; it does not calculate a version from consumer state;
- acceptance only after the user can access the disclosure content and performs an affirmative action;
- general Terms presentation cannot silently satisfy a standalone descriptor of another type;
- cancellation produces no proof;
- one shell supports multiple ConsentTypes while consumers retain their own pre/post workflow logic.

### Authorization / Compliance

- account-bound acceptance goes through SH-001 via SH-007;
- representative high-risk consent categories must be testable as standalone;
- accessibility and clear affirmative action are part of the presentation contract;
- legal copy/version correctness is supplied from trusted server configuration until Feature 05 is available.

### Database / Transaction Behavior

Only the SH-007 transaction on successful acceptance. No UI-generated timestamp/IP hash is authoritative.

### Events / Jobs

None.

### Provider Integration

None. Consumer/provider handoff occurs after this shell returns proof, in the consumer Module.

### UI / Admin Surface

This feature is the Module’s primary reusable UI surface. It must be composable by other Workin Ants workflows and must not import their provider SDKs or repositories.

### Failure Behavior

- malformed descriptor → validation failure; no presentation/acceptance;
- unsupported type/version → fail before write;
- acceptance command failure → show retry-safe failure state; never imply consent recorded;
- user cancels → return not accepted; no proof;
- consumer provider failure after proof → consumer handles it; Consent proof remains historically true.

### Tests

- component renders type/version/content correctly;
- keyboard/accessibility tests;
- explicit acceptance calls SH-007 once/replay-safe;
- cancel/close does not write ConsentLog;
- generic terms fixture cannot satisfy FCRA fixture;
- consumer context is not copied into unrelated Consent fields;
- no provider SDK/import test;
- E2E fixture: FCRA presentation → proof only, no VerificationCheck creation;
- E2E fixture: push disclosure → proof only, browser permission unchanged.

### Documentation Updates

- public SH-010 component/application contract;
- integration instructions for consumer Modules;
- progress tracker.

### Acceptance Criteria

- one reusable shell serves approved standalone cases;
- exact type/version is visible and submitted;
- no false proof on cancel;
- no consumer/provider lifecycle ownership leaks into Consent.

### Exit Gate

Feature 04 passes when interaction, accessibility, contract, acceptance, cancellation, and ownership-boundary tests pass. Consumers may use explicit trusted version descriptors while Feature 05 remains architecture-gated.

---

## 05 Persistent Consent Version Catalog, Active-Version Resolution, and Governed Presentation

**ARCHITECTURE GATE:** do not implement this feature until U-CL01-08 is resolved and the accepted model, applicability dimensions, publication authority, immutability rules, and re-consent metadata are recorded in CL-01 and Module architecture. If U-CL01-09 affects initial publication/re-consent semantics, resolve the required portion before activation.

### Objective

Replace trusted ad hoc version descriptors with authoritative Consent-owned version catalog truth so consumers can ask SH-009 which exact version applies now and SH-010 can present that version consistently.

### Observable Result

After the architecture gate is resolved:

- a privileged catalog path can create/publish versions according to the approved lifecycle;
- SH-009 resolves exactly one applicable version for a supported context;
- future/not-yet-effective or superseded versions are not silently served;
- published content/version meaning is immutable;
- SH-010 can source its descriptor from SH-009 rather than consumer hard-coded constants;
- acceptance proof can be traced to the exact published version/content hash required by the approved design.

### Cluster Build-Plan Link

Direct implementation of **CL-01 Phase 2 / Feature 08 — Consent Version Catalog and Standalone Consent Presentation**.

### Dependencies

- Features 01–04;
- **resolved U-CL01-08** and updated architecture;
- relevant part of U-CL01-09 for material change/re-consent;
- SH-009, SH-010;
- SH-080 versioning mechanism;
- SH-072 hashing if the approved schema uses content hashes;
- SH-002 for catalog administration;
- SH-014 only if root security policy requires step-up for publish/retire;
- migration/seed strategy.

### In Scope

Only after architecture approval:

- implement the exact approved Consent-owned catalog model(s)/enum(s)/constraints;
- implement approved create/publish/retire/supersede operations and authorization;
- implement SH-009;
- integrate SH-010 with SH-009;
- implement content canonicalization/hash using shared primitives if approved;
- seed/migrate initial versions using approved source material;
- enforce immutable published meaning;
- add catalog history/admin visibility only as required.

### Out of Scope

- inventing model/status names before approval;
- legal copy drafting;
- consumer lifecycle transitions;
- automatic re-consent notification if U-CL01-09 does not define it;
- withdrawal lifecycle;
- provider integrations;
- global policy engine replacing SH-080.

### Module-Owned Data

The exact model names/fields are **TBD by U-CL01-08**. The approved design must, at minimum, be able to represent the semantic requirements recorded in `module-architecture.md`: type/document identity, immutable version, content/reference, applicability/effective semantics, publication state, and any approved content hash/material-change metadata.

Do not proceed if a coding agent still has to invent these fields.

### Public Interfaces

- SH-009 `resolveActiveConsentVersion`;
- SH-010 upgraded to fetch/verify the authoritative descriptor;
- approved catalog administration commands/queries named by the architecture ruling;
- SH-007/008 remain unchanged proof boundary unless an explicit version reference is added by approved migration.

### Shared Operations Used

- **SH-009 — Consent:** active-version resolution.
- **SH-010 — Consent:** governed presentation.
- **SH-080 `manageVersionedRules` — shared mechanism:** immutable/effective version mechanics. Local policy: Consent applicability/re-consent meaning. **Do not build:** a parallel generic Consent version framework.
- **SH-072 `hashCanonicalPayload` — shared security:** approved content integrity digest. Local policy: canonical content/meaning. **Do not build:** local hash helper.
- **SH-002 — Role:** catalog admin authorization. **Do not build:** catalog permission engine.
- **SH-014 — Identity step-up:** conditional if root policy classifies publishing as sensitive.
- **SH-029 — Audit:** approved publish/retire/admin actions.
- **SH-046 — outbox:** version-change event only if a durable consumer requirement is approved.
- **SH-041 — Notification:** only when an approved re-consent policy requires user notice; no direct sender.

### Domain Logic

The exact transition graph comes from the architecture ruling, not this plan. Regardless of chosen schema:

- published meaning is immutable;
- changes produce a new version;
- SH-009 returns a deterministic applicable version or typed failure;
- a future version is not active early;
- conflicting simultaneous versions for the same applicability scope are prevented by database/policy constraints;
- a resolved active version is not equivalent to accepted proof;
- material-change/re-consent outcome follows approved policy, not “version string changed therefore always require” by default.

### Authorization / Compliance

- catalog mutation is privileged via SH-002;
- publish/retire/audit requirements follow approved policy;
- if jurisdiction/locale are supported, missing/ambiguous applicability fails closed rather than selecting arbitrary content;
- high-risk standalone requirement remains Consent-owned;
- content provenance must be reviewable without exposing unrelated PII.

### Database / Transaction Behavior

- migration only after architecture approval;
- approved uniqueness/effective-interval constraints must prevent ambiguous active versions;
- publish/supersede operations are transaction-safe;
- use optimistic concurrency/aggregate locking shared primitives only if the accepted design requires them;
- no in-memory lock;
- published records are not updated in-place for content changes.

### Events / Jobs

Optional and policy-driven:

- version-published/superseded event via SH-046 if durable consumers need it;
- a re-consent targeting job is **not** added unless U-CL01-09 defines its behavior and ownership;
- any job uses the shared queue/retry/DLQ infrastructure.

### Provider Integration

Not applicable.

### UI / Admin Surface

- SH-010 presentation now uses authoritative catalog result;
- minimal restricted catalog administration/history only if MVP requires in-app management; otherwise migration/seed administration is acceptable according to approved architecture;
- admin surface never edits a published version in-place.

### Failure Behavior

- architecture gate unresolved → feature remains unimplemented/disabled;
- no applicable version → `ACTIVE_VERSION_UNAVAILABLE`, consumer must not fall back to hard-coded content;
- ambiguous version configuration → fail closed and emit safe ops signal;
- stale admin mutation → conflict;
- hash mismatch/integrity issue → do not present/publish as valid;
- audit/notification outage after source commit → source catalog truth remains correct; retry support effect according to canonical infrastructure.

### Tests

After gate resolution:

- migration from clean DB;
- seed idempotency;
- exactly-one-applicable-version constraints;
- future/effective/superseded resolution;
- immutable published content/version;
- locale/jurisdiction fixtures only if adopted;
- content-hash test vectors if adopted;
- concurrent publish conflict;
- catalog admin authorization/step-up as applicable;
- SH-009 contract;
- SH-010 obtains the exact SH-009 descriptor;
- acceptance → proof trace to exact catalog version;
- no hard-coded consumer version fallback;
- failure/health telemetry redaction.

### Documentation Updates

**Mandatory before coding:** update CL-01 architecture and `module-architecture.md` with the resolved U-CL01-08 schema/lifecycle/public commands, plus any resolved U-CL01-09 material-change rule.

After implementation, update public interface docs, migration/seed docs, progress tracker, and any shared-operation integration notes.

### Acceptance Criteria

- the coding agent did not invent the schema in the feature branch;
- SH-009 has authoritative persistent truth;
- consumers no longer own active version constants for enabled flows;
- published meaning is immutable;
- SH-010/SH-007 preserve exact traceability;
- ambiguous/missing configuration fails closed.

### Exit Gate

Feature 05 cannot pass unless the architecture gate was resolved first. After implementation, migration, catalog constraints, authorization, SH-009/010 contract, integrity, concurrency, and presentation E2E tests must all pass.

---

# Phase 3 — Module Integration Proof

## 06 Cross-Module Consent Consumer Contract Proof

Prove that the major consumer classes use Consent public interfaces and preserve shared mechanism / separate truth boundaries.

### Objective

Demonstrate that representative security, verification, calendar, notification, agreement, digital-goods, healthcare, subscription, and rewards consumers can obtain or retain Consent proof without direct ConsentLog access and without Consent mutating their lifecycles.

### Observable Result

Contract/integration tests show representative workflows:

```text
consumer determines required consent
→ SH-009 or trusted descriptor identifies exact version
→ SH-010 presents when standalone
→ SH-007 records proof
→ consumer receives SH-008 result / consentLogId
→ consumer writes only its own contextual truth
```

Each test can point to one owner for every resulting record.

### Cluster Build-Plan Link

Supports **CL-01 Phase 4 — Cross-Cluster Contract Proof (Features 13–15)** and specifically the Cluster rule that consumers use owner public interfaces rather than importing CL-01 source repositories.

Feature 06 may proceed before Feature 05 for consumers that supply a trusted explicit version descriptor; production flows requiring authoritative current-version resolution remain gated until Feature 05.

### Dependencies

- Features 02–04;
- Feature 05 for any production flow that must resolve active version dynamically;
- versioned contract fixtures or real public interfaces for target consumers;
- U-CD-01 / U-CL01-25 resolution only where a consumer schema is being tightened around an immutable proof reference.

### In Scope

Prove representative boundaries for:

- Identity/security disclosures;
- Trust Verification / Screening (`VerificationConsent`/`VerificationCheck`);
- Booking & Calendar (`CalendarConnection`);
- Notification (`NotificationSubscription`/browser permission distinction);
- Transaction / Order (`AgreementElectronicConsent`);
- Digital Goods (`DigitalGoodsTermsAcceptance`);
- Healthcare (`BaaAgreement`/readiness distinction);
- Track Subscription & Entitlement;
- Sweepstakes / Prize and Gamification / Rewards.

Not every consumer needs a full E2E UI in this Module feature. Contract fixtures are acceptable when the neighbor is not built.

### Out of Scope

- implementing consumer Modules;
- migrating every consumer to a required `consentLogId` before U-CD-01 is resolved;
- provider integration;
- consumer eligibility/readiness decisions;
- payment/subscription/calendar/screening state machines;
- Search projection.

### Module-Owned Data

Consent writes/reads ConsentLog only. Consumer tests may create foreign fixtures through their owner interfaces/test harnesses, never through Consent production repositories.

No cross-domain model becomes Consent-owned.

### Public Interfaces

Verify:

- SH-007;
- SH-008;
- SH-010;
- SH-009 for Feature-05-enabled flows;
- consumer-side proof-reference/requirement contracts as defined by their owners.

### Shared Operations Used

Primarily the Consent public operations already implemented:

- **SH-007 / SH-008 / SH-009 / SH-010**.
- **SH-001 / SH-002** remain enforcement dependencies.
- **SH-046** only if a chosen consumer integration explicitly uses a durable Consent event; query/reference integration is preferred otherwise.

Do not introduce new shared operations merely to make the test harness convenient.

### Domain Logic

Boundary assertions:

- security disclosure proof does not prove MFA/passkey/recovery success;
- FCRA/license/DMV proof does not create or pass a VerificationCheck;
- calendar proof does not create/activate CalendarConnection;
- push proof does not grant browser permission or create NotificationSubscription;
- agreement proof does not sign/execute AgreementElectronicConsent;
- digital-goods proof does not grant downloads/playback;
- healthcare proof does not execute BaaAgreement or mark healthcare ready;
- subscription proof does not activate TrackSubscription or entitlement;
- sweepstakes/reward proof does not create entries/points/rewards.

### Authorization / Compliance

- consumer must name the required type/version according to its policy;
- Consent does not override Role/Hold/entitlement/readiness gates;
- FCRA/e-sign/high-risk flows use standalone presentation where approved;
- no consumer can accept on behalf of a User by directly calling a repository;
- sensitive consumer context remains in the consumer record, not ConsentLog.

### Database / Transaction Behavior

Cross-Module tests use separate owner transactions/contracts. There is no distributed transaction that makes Consent and consumer state one owner.

If a consumer requires a proof before its command, it may:

1. obtain proof first, then execute its own transaction; or
2. use an approved orchestration/command design preserving owner boundaries.

Do not create a shared “consent + consumer” transaction repository spanning both domains.

### Events / Jobs

Only exercise existing approved event contracts. Consumer failures after Consent acceptance do not roll back historical truth unless an architecture explicitly defines a compensation record; no such generic compensation exists today.

### Provider Integration

Provider interaction remains entirely in consumer/provider-owning Module tests. Consent tests may use provider-owner fixtures but contain no provider SDK/client.

### UI / Admin Surface

No new Consent UI beyond Feature 04/05. Consumer UIs own their placement of the shared presentation shell.

### Failure Behavior

- missing proof → consumer receives typed negative and owns denial UX/state;
- Consent available but consumer unavailable → proof remains valid historical truth; consumer retries its own action;
- consumer provider fails after proof → Consent remains unchanged;
- consumer tries direct ConsentLog write/read → architecture/contract test failure;
- unresolved consumer proof-binding rule → keep that integration fixture-only/disabled rather than invent a schema FK.

### Tests

At minimum:

- Identity security disclosure boundary test;
- VerificationConsent relation/reference test and no VerificationCheck transition from Consent;
- CalendarConnection reference test and no provider connection creation from Consent;
- push/browser permission separation test;
- AgreementElectronicConsent separate lifecycle test;
- DigitalGoodsTermsAcceptance separate lifecycle test;
- BaaAgreement/healthcare separation test;
- TrackSubscription no-activation test;
- Sweepstakes/Gamification no-business-effect test;
- direct foreign Prisma access/import regression test where tooling permits;
- proof ID/current-query mode fixtures documenting U-CD-01 choices already approved.

### Documentation Updates

- update each implemented consumer integration contract/reference docs;
- record unresolved consumer binding cases under U-CD-01/U-CL01-25 rather than silently deciding them;
- progress tracker.

### Acceptance Criteria

- representative consumers use public Consent interfaces;
- no consumer lifecycle is owned or mutated by Consent;
- contextual records remain separate truth;
- no provider client enters Consent;
- any production current-version flow uses Feature 05 rather than a hard-coded fallback.

### Exit Gate

Feature 06 passes when all enabled representative contract/integration tests pass and an ownership review finds no direct foreign writes, provider leakage, or generic consent duplication.

---

# Phase 4 — Privacy, Audit, Notification, and Operational Support

## 07 Privacy Target Executor and Support-Rail Integration

Implement Consent’s side of Privacy, Audit, Notification, and Observability without creating any of those systems locally.

### Objective

Make Consent proof safely discoverable/exportable by Privacy, support approved audit/sensitive-access requirements, and produce operational/user-notification requests through canonical owners while preserving ConsentLog as source truth.

### Observable Result

- Privacy can enumerate Consent-owned data for a User and receive a typed inventory/export fragment.
- Privacy can invoke a Consent target executor and receive a typed result.
- If destructive disposition depends on unresolved retention, the executor returns a safe blocked/retention-required outcome rather than deleting proof.
- Approved privileged operations emit generic Audit/AccessAudit evidence through the Audit owner.
- Future approved re-consent notices call Notification rather than email/SMS/push directly.
- Ops can observe failures without a Consent-specific failure table.

### Cluster Build-Plan Link

Directly supports **CL-01 Feature 15 — Privacy, Holds, Audit, Notification, and Operational Support Bridges**. Consent does not need a local ComplianceHold integration merely to satisfy this feature; holds remain relevant to consumer actions and Admin Review.

### Dependencies

- Features 01–06 as applicable;
- SH-095/096/097/098 Privacy protocol;
- SH-029/030 Audit interfaces;
- SH-041 Notification interface;
- SH-032/033/034/036/037 Ops;
- U-CL01-11 before destructive delete/anonymize is enabled;
- U-CL01-17 before declaring sensitive-access coverage final.

### In Scope

- Consent implementation of SH-096 subject-data enumeration;
- export-safe serializer for Consent proof;
- Consent retention-fact response via SH-097;
- SH-095 executor dispatch/result for approved dispositions;
- non-destructive `RETENTION_DECISION_REQUIRED` behavior while U-CL01-11 is open;
- SH-029 audit for approved material admin/catalog/privacy operations;
- SH-030 for approved sensitive history access once policy is known;
- SH-041 request integration for approved version/re-consent notices;
- structured logs/metrics/integration failure reporting.

### Out of Scope

- PrivacyRequest/DataErasureJob/DataErasureTarget creation or scheduling;
- local DataRetentionExemption table;
- deciding legal retention without approved policy;
- destructive User/Consent cascade migration while U-CL01-11 is unresolved;
- email/SMS/push implementation;
- generic AuditEvent/AccessAuditLog persistence;
- generic Ops dashboard/system tables;
- ComplianceHold lifecycle.

### Module-Owned Data

- ConsentLog subject-data inventory/export;
- future version-catalog personal data, if any, is generally configuration rather than subject data and must be classified after Feature 05 design;
- no Privacy/Audit/Notification/Ops models become Consent-owned.

### Public Interfaces

- SH-096 Consent implementation;
- SH-097 Consent facts implementation;
- SH-095 Consent executor;
- export fragment contract if Privacy architecture requires it;
- existing Consent queries remain unchanged.

### Shared Operations Used

- **SH-095 `executePrivacyInstruction` — Privacy protocol:** Consent executes only its records. Local policy: field disposition after approved retention rule. **Do not build:** Consent privacy workflow.
- **SH-096 `enumerateSubjectData` — Privacy protocol:** enumerate ConsentLog targets. **Do not build:** schema crawler/global inventory.
- **SH-097 `evaluateRetentionRequirement` — data owner facts/Privacy exemption:** Consent supplies proof purpose/facts; Privacy owns exemption. **Do not build:** local exemption state.
- **SH-098 `anonymizePersonalFields` — shared primitive:** only after approved field map. **Do not build:** blanket delete/anonymizer.
- **SH-029 / SH-030 — Audit:** generic action/sensitive-read evidence. **Do not build:** Consent audit/access tables.
- **SH-041 — Notification:** safe intent only. **Do not build:** mail/SMS/push sender.
- **SH-032/033/034/036/037 — Ops:** correlation/logging/redaction/metrics/failure. **Do not build:** Consent ops records.
- **SH-044 — idempotency:** privacy executor command replay safety where target execution mutates data.

### Domain Logic

- subject enumeration is stable/paginated according to Privacy contract;
- export omits or appropriately labels sensitive request evidence unless Privacy export policy explicitly includes it;
- product deletion is not equivalent to privacy erasure;
- until U-CL01-11 is resolved, Consent does not physically delete evidence that may be retention-exempt;
- after U-CL01-11, executor follows the approved retain/anonymize/delete field map and preserves referential integrity;
- Audit/Notification/Ops failure never rewrites Consent proof into a false state.

### Authorization / Compliance

- only Privacy-authorized system workflow may invoke destructive executor behavior;
- privileged manual retry uses SH-002 and SH-014 only if root policy requires;
- self/admin history access remains Feature 03 authority policy;
- access-audit completeness remains gated by U-CL01-17;
- telemetry and audit payloads are minimized.

### Database / Transaction Behavior

Before U-CL01-11 resolution:

- no destructive schema/FK migration;
- executor may read/inventory/export and return `RETENTION_DECISION_REQUIRED` for deletion/anonymization requests that cannot safely be decided.

After resolution:

- owner mutation is transactional and idempotent;
- retention-safe FK/pseudonymization/deletion behavior uses the approved migration;
- no blind cascade deletion;
- consumer FK effects are tested.

### Events / Jobs

- Privacy owns parent jobs/scheduling;
- Consent target execution may run in shared worker infrastructure but owns no job lifecycle;
- Notification request is an external support effect;
- no re-consent bulk worker unless U-CL01-09 defines it.

### Provider Integration

Not applicable.

### UI / Admin Surface

No Consent privacy-request UI. Optional admin diagnostics may show target/result references through Privacy/Ops owner surfaces. Consent history UI remains read-only.

### Failure Behavior

- retention policy unresolved → structured blocked result, no destructive change;
- approved retention exemption → return retained result with safe owner facts/reference;
- duplicate executor call → same effective result through SH-044;
- Audit/Notification unavailable after source action → source truth stays correct; support effect retries/records failure according to owner policy;
- telemetry sanitizer failure → fail closed on sensitive logging rather than log raw payload.

### Tests

- subject inventory/pagination;
- export-safe field mapping;
- prove no local PrivacyRequest/DataErasureJob/RetentionExemption creation;
- unresolved-retention destructive request returns blocked result;
- after U-CL01-11: retain/anonymize/delete tests and FK integrity;
- executor idempotency;
- audit event safe payload;
- sensitive access audit fixture after U-CL01-17;
- Notification request safe variables/no provider calls;
- Ops telemetry redaction;
- no Consent-specific IntegrationFailure table.

### Documentation Updates

- before enabling destructive behavior, update architecture with U-CL01-11 ruling and exact field/FK disposition;
- update U-CL01-17 status when access-audit matrix is approved;
- document Privacy target types/results;
- progress tracker.

### Acceptance Criteria

- Privacy can enumerate/export Consent data through an owner interface;
- destructive behavior never guesses retention;
- audit/access/notification/ops use canonical owners;
- no local privacy/audit/notification/ops lifecycle is introduced.

### Exit Gate

Feature 07 passes for non-destructive MVP behavior when enumeration/export/blocked-retention/support-rail tests pass. It passes for destructive production behavior only after U-CL01-11 is resolved, architecture updated, migration verified, and retention/privacy tests pass.

---

# Phase 5 — Security, Concurrency, Retention, and Production Hardening

## 08 Consent Production Hardening and Contract Freeze

Resolve production-blocking Consent architecture decisions, enforce accepted constraints, stress idempotency/concurrency, verify privacy/retention safety, and freeze versioned public contracts.

### Objective

Make the enabled Consent & Disclosure scope production-safe without using hardening as a place to invent unfinished product semantics.

### Observable Result

- acceptance/query/presentation/catalog paths have stable versioned contracts;
- duplicate/replay/concurrent acceptance behavior is deterministic under the resolved U-CL01-10 policy;
- active-version catalog cannot resolve ambiguous/stale content if Feature 05 is enabled;
- User/privacy deletion cannot destroy required Consent proof under the resolved U-CL01-11 policy;
- privileged history/catalog/privacy actions satisfy final auth/RLS/audit requirements;
- operators can diagnose failures through canonical Ops surfaces;
- no unresolved decision is required by a production-enabled path.

### Cluster Build-Plan Link

Directly supports **CL-01 Feature 16 — Hardening and Production Readiness** for Consent-specific risk.

### Dependencies

- all prior enabled features;
- **resolved U-CL01-10** before final idempotency/uniqueness schema freeze;
- **resolved U-CL01-11** before destructive retention path launch;
- U-CL01-08/09 resolved for any production-enabled catalog/re-consent behavior;
- U-CL01-17 resolved for final sensitive-access coverage;
- production-like Postgres/RLS environment;
- migration/backfill/rollback strategy.

### In Scope

- implement the approved U-CL01-10 durable replay/uniqueness strategy;
- run concurrency/load tests for acceptance and catalog publishing if enabled;
- implement approved U-CL01-11 retention-safe FK/anonymization/delete changes;
- validate RLS/server-authorization parity;
- verify all Consumer integrations avoid direct Consent repositories;
- validate data minimization/logging/audit payloads;
- performance/index review for SH-007/008/history/SH-009 hot paths;
- migration/backfill safety;
- reconcile malformed/legacy ConsentLog data using an approved repair plan, never ad hoc silent rewrites;
- contract version/freeze documentation;
- health/operational runbook for catalog misconfiguration and proof failures.

### Out of Scope

- new ConsentTypes solely for future product ideas;
- new withdrawal/re-consent policy not already approved;
- new provider integration;
- legal copy authoring;
- refactoring consumer lifecycles into Consent;
- generalized compliance engine;
- Search/public indexing.

### Module-Owned Data

Review/finalize as applicable:

- `ConsentLog` indexes/constraints;
- retention-safe User relationship/FK behavior after U-CL01-11;
- approved catalog models/constraints after Feature 05;
- no generic event/audit/ops table.

Any destructive migration requires data audit, backup/rollback, representative backfill, and verification query plan.

### Public Interfaces

Freeze/version the enabled contracts:

- SH-007;
- SH-008;
- SH-009 if Feature 05 enabled;
- SH-010;
- `listUserConsentHistory`;
- SH-095/096/097 privacy implementations.

Breaking changes require an interface migration plan rather than silent signature changes.

### Shared Operations Used

Hardening verifies all previously consumed canonical operations rather than creating new substitutes, especially:

- SH-001 / SH-002;
- SH-007–010;
- SH-029 / SH-030;
- SH-032–037;
- SH-041;
- SH-044 / SH-046;
- SH-072 / SH-076 / SH-080;
- SH-095–098.

If accepted DB concurrency policy needs shared locks/optimistic concurrency, use SH-051/SH-052 according to the architecture ruling rather than an in-memory lock.

### Domain Logic

Hardening must prove:

- accepted historical proof cannot be altered by normal business commands;
- exact version matching remains deterministic;
- idempotency replay and intentional later acceptance are distinguishable according to U-CL01-10;
- catalog ambiguity/missing content fails closed;
- privacy disposition follows U-CL01-11 exactly;
- no support-system outage fabricates proof or downstream success;
- no enabled consumer uses a generic Terms proof for a distinct required type;
- no production behavior depends on unresolved U-CD/U-CL01 decision.

### Authorization / Compliance

Final review includes:

- self vs admin/support history matrix;
- catalog admin matrix if enabled;
- privacy executor system authority;
- step-up requirements if root policy applies;
- RLS/server-policy parity;
- U-CL01-17 sensitive-access matrix;
- standalone consent coverage for enabled high-risk workflows;
- telemetry/PII redaction;
- retention matrix implementation.

### Database / Transaction Behavior

- acceptance transaction + SH-044 replay behavior stress-tested;
- accepted U-CL01-10 constraints migrated safely;
- accepted U-CL01-11 FK/retention changes migrated safely;
- catalog effective/version constraints stress-tested if enabled;
- no in-memory concurrency authority;
- reconciliation/backfill never rewrites a valid newer record blindly;
- migration can be applied from clean DB and representative legacy data.

### Events / Jobs

If Consent events/jobs exist in enabled scope:

- event outbox replay/dedupe tests;
- queue retry/dead-letter handling;
- no exactly-once claim — prove effectively-once effects;
- re-consent notification target behavior only if U-CL01-09 approved it;
- Privacy job ownership remains external.

If no Consent event/job is required, do not add one for hardening symmetry.

### Provider Integration

Not applicable. Add a regression check that Consent has no Stripe/Cronofy/screening/e-sign/push provider client or webhook route.

### UI / Admin Surface

Production-safe surfaces may include:

- user consent history;
- approved admin history;
- catalog administration/history if Feature 05 requires UI;
- operator-safe diagnostics for catalog misconfiguration/correlation IDs.

No surface may become a second source-truth editor for ConsentLog.

### Failure Behavior

Document and test production behavior for:

- Identity actor resolver unavailable;
- Role authority unavailable for privileged read;
- idempotency store unavailable;
- database serialization/conflict;
- hashing primitive unavailable;
- active version missing/ambiguous/corrupt;
- Audit/Notification/Ops unavailable after source commit;
- Privacy executor retryable/terminal failure;
- retention exemption/decision conflict;
- legacy malformed proof row;
- incompatible consumer contract version.

Each case must produce a defined deny/retry/unavailable/retained/manual-review result rather than a generic “500 and hope.”

### Tests

- full domain unit suite;
- public contract suite;
- authorization/RLS parity suite;
- acceptance concurrency stress test;
- idempotency replay + intentional re-acceptance suite after U-CL01-10;
- catalog concurrent publish/effective-resolution stress tests if enabled;
- retention/privacy destructive-path tests after U-CL01-11;
- migration clean DB + representative legacy data;
- rollback/forward-fix rehearsal for destructive migration;
- proof query load/performance tests;
- audit/sensitive-access completeness tests;
- telemetry PII/log scan;
- consumer contract regression suite;
- critical E2E standalone proof workflows;
- production build/typecheck/lint/test commands.

### Documentation Updates

- close/rescope every resolved U-CL01/U-CD item used by production behavior;
- update `module-architecture.md` with accepted constraints/lifecycle decisions;
- update CL-01 architecture if a Cluster-level binding decision changed;
- freeze public interface versions;
- document migration/backfill/rollback and ops runbooks;
- progress tracker and completion report.

### Acceptance Criteria

- every production-enabled Consent behavior has resolved architecture;
- no duplicate generic consent implementation exists in consumers;
- replay/concurrency invariants hold;
- retention/privacy destructive behavior is explicitly approved and tested;
- RLS/server authorization and audit requirements are complete;
- telemetry contains no prohibited sensitive data;
- no provider ownership leakage exists;
- all critical consumer E2E/contract tests pass.

### Exit Gate

The Module is production-ready only when:

- all applicable typecheck/lint/unit/integration/authorization/RLS/privacy/concurrency/E2E/build checks pass;
- U-CL01-10 and U-CL01-11 are resolved for the enabled production paths;
- U-CL01-08/U-CL01-09 are resolved for any enabled catalog/re-consent behavior;
- no normal code path mutates historical ConsentLog proof;
- no direct consumer ConsentLog repository use remains;
- idempotency/concurrency tests produce no unexplained duplicate effects;
- retention-safe migration/backfill is verified;
- architecture, implementation plan, public contract docs, and progress tracker agree with shipped behavior.

---

## Module Integration Phase

**Phase 3 / Feature 06** is the explicit Module integration phase. Its purpose is contract proof, not lifecycle transfer.

The minimum representative bridges are:

```text
Identity & Access
→ trusted accepting actor

Role / Authority
→ privileged consent-history/catalog authority

Consent & Disclosure
→ exact type/version proof

Trust Verification
← FCRA/license/DMV proof reference

Booking & Calendar
← calendar authorization proof

Notification
← push/PWA disclosure proof; browser permission remains Notification/browser truth

Transaction / Order
← electronic records/signature/agreement disclosure proof

Digital Goods Access
← terms/refund/license/declaration proof

Healthcare
← disclosure proof; BAA/readiness remain Healthcare truth

Track Subscription & Entitlement
← subscription/billing/plan/commission/fee-waiver proof

Sweepstakes / Gamification
← rules/reward terms proof

Privacy / Audit / Ops
↔ owner executor and support evidence only
```

Where a neighbor is not implemented, use versioned contract fixtures. Do not bring its Prisma model/repository into Consent production code.

---

## Module Hardening Phase

**Phase 5 / Feature 08** is limited to Consent-specific production risk:

- exact-proof integrity;
- acceptance replay/idempotency;
- concurrent acceptance;
- version-catalog conflict/integrity if enabled;
- RLS/authorization parity;
- privileged access auditing;
- evidence minimization;
- privacy/retention and cascade safety;
- migration/backfill safety;
- telemetry redaction;
- consumer contract drift;
- performance of proof/history/version queries.

Hardening must not introduce provider clients, a generic compliance state machine, a local privacy job system, a generic event ledger, or unfinished withdrawal/re-consent behavior.

---

## Phase Summary

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Proof Contracts and Source-of-Truth Foundation | 01–03 |
| 2 | Standalone Presentation and Version Governance | 04–05 |
| 3 | Module Integration Proof | 06 |
| 4 | Privacy, Audit, Notification, and Operational Support | 07 |
| 5 | Security, Concurrency, Retention, and Production Hardening | 08 |

**Total numbered features: 8.**

---

## Module Execution Pattern

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read the Canonical Shared Operations Registry.
3. Read CL-01 architecture and build plan.
4. Read `consent_disclosure/module-architecture.md` and this plan.
5. Read public-interface sections for direct dependencies/consumers touched by the feature.
6. Inspect the current Prisma schema and migrations.
7. Confirm the prior numbered feature exit gate passed.
8. Confirm no unresolved architecture item blocks the feature’s production behavior.
9. Write the concise implementation specification for **this feature only**.
10. Implement only the numbered feature.
11. Run required quality checks.
12. Verify public contracts/workflows without foreign database ownership.
13. Update progress.
14. Update architecture only when a binding decision legitimately changed and was approved.
15. Record unresolved risks, assumptions, known failures, and deferred work.
16. Mark the feature exit gate pass/fail before starting the next dependent feature.

---

## Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise specification containing:

- Objective
- Observable result
- Cluster build-plan link
- Dependencies
- Architecture decisions required before implementation
- In scope
- Out of scope
- Owned data affected
- Public contracts
- Shared operations consumed
- Permissions / compliance
- Primary workflow
- Provider integration
- Jobs / events
- Idempotency / concurrency
- Error behavior
- Tests
- Acceptance criteria
- Documentation updates

Do **not** generate all eight feature specifications in advance. The next feature’s specification must reflect the current codebase, prior exit gates, and any newly resolved architecture decision.

---

## Required Completion Report

After implementing each numbered feature, the coding agent must report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused
- Events/jobs added
- Provider adapter changes
- Tests added/changed
- Commands run
- Manual/contract verification
- Documentation updated
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

For this Module, the report must explicitly state whether the feature touched any of U-CL01-08, U-CL01-09, U-CL01-10, U-CL01-11, U-CL01-17, U-CL01-25, or U-CD-01 through U-CD-03, and whether architecture was updated before implementation.

---

## Final Quality Check

Before declaring this Module plan satisfied, verify all of the following:

1. `ConsentLog` and `ConsentType` have exactly one owner.
2. No neighboring Module truth was absorbed into Consent.
3. Consumers use SH-007/SH-008 rather than duplicate generic proof storage/query logic.
4. `VerificationConsent`, `AgreementElectronicConsent`, `DigitalGoodsTermsAcceptance`, `CalendarConnection`, `NotificationSubscription`, `BaaAgreement`, `TrackSubscription`, and Identity age/security records remain separate truth.
5. No persistent version-catalog schema was invented before U-CL01-08 resolution.
6. No withdrawal/revocation/re-consent state was invented before U-CL01-09 resolution.
7. Final idempotency/uniqueness semantics were not guessed around U-CL01-10.
8. Privacy orchestration remains Privacy-owned and cascade/retention behavior is resolved before destructive launch.
9. Authentication and authorization are consumed through SH-001/SH-002.
10. Hashing/idempotency/audit/notification/observability infrastructure is reused rather than copied.
11. Consent owns no provider adapter or webhook.
12. Audit, domain proof, and observability remain distinct.
13. No public Search projection was invented for Consent proof.
14. Every numbered feature has concrete tests and an exit gate.
15. Cross-Module integration tests use public contracts rather than foreign database tables.
16. A coding agent can execute every **unblocked** feature without inventing architecture; gated features explicitly tell the agent to stop until the ruling exists.
