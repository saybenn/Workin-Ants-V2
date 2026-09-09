# Transaction / Order Module Implementation Plan

> **Module ID:** `transaction_order`  
> **Module:** Transaction / Order Module  
> **Primary Cluster:** CL-04 — Customer Demand, Order & Resolution  
> **Plan status:** Sequential Module implementation plan subordinate to the CL-04 `build-plan.md`  
> **Architecture authority:** `module-architecture.md` governs Module-local ownership and invariants; CL-04/root architecture governs broader sequencing and cross-cutting boundaries.

---

## Core Principle

Implement Transaction / Order through narrow, verifiable slices:

```text
public/observable behavior
→ validated command/query
→ Transaction / Order-owned policy
→ authoritative Order/Agreement write or read
→ canonical shared-operation calls
→ event/audit/notification effects
→ tests
→ exit gate
```

A feature is complete only when source truth, public contracts, transaction boundaries, external-owner interactions, failure behavior, and tests agree.

The Module plan does not re-sequence CL-04. It decomposes the Transaction / Order-owned work inside CL-04 Features 04–09, the Transaction / Order participation required by CL-04 Feature 12, and the Module-specific proof required by CL-04 Features 13–14.

---

## Build Rules

1. Follow root architecture, root standards, CL-04 architecture, CL-04 build plan, and `module-architecture.md`.
2. Implement only Transaction / Order-owned truth.
3. Consume Gig / Demand, Marketplace Supply, Customer / Buyer Profile, Track, Payment, Consent, Media, Booking, Review / Dispute, Holds, Privacy, Audit, Notification, and Observability through approved public interfaces.
4. Reuse canonical shared operations; do not create local copies of authentication, authorization, entitlement, idempotency, concurrency, outbox, queue, hashing, signed access, audit, notification, privacy, or telemetry mechanisms.
5. Validate every mutation payload server-side.
6. Resolve trusted actor/context server-side; never trust client ownership, price, payment status, or Agreement completion.
7. Every retryable commercial mutation is idempotent.
8. Every concurrency-sensitive lifecycle mutation uses a database/platform concurrency primitive.
9. Order/Agreement state changes and their domain lifecycle events are transactionally atomic.
10. External effects are published after authoritative commit, preferably through the canonical transactional outbox.
11. Raw Stripe/payment provider webhooks never enter Transaction / Order domain services.
12. Provider-specific Agreement renderer/e-sign details remain behind ports/adapters if adopted.
13. Finalized Agreement bytes/snapshots are immutable.
14. Media / File Access owns storage/file safety/signed transport.
15. Privacy / Data Erasure owns legal orchestration; this Module implements only its local target executor.
16. Each numbered feature ends with automated tests and an explicit exit gate.
17. If an unresolved architecture decision blocks a feature, stop at that boundary and record the decision required. Do not invent the rule.
18. Do not use the hardening phase to complete feature logic that should have been implemented earlier.

---

## Preconditions

### Hard platform dependencies

Must exist before the first production mutation that relies on them:

- Prisma/Postgres migration workflow;
- strict TypeScript/validation conventions;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- canonical `executeIdempotentCommand`;
- canonical database concurrency primitive (`acquireAggregateLock` and/or `withOptimisticConcurrency`);
- `appendDomainLifecycleEvent` convention;
- transactional outbox / `publishDomainEvent`;
- request/correlation context;
- structured logging and telemetry redaction;
- Audit / Event Ledger public commands.

These may be contract-stubbed in isolated unit tests, but production feature exit gates require the real shared primitives where the feature uses them.

### Hard Module dependencies by phase

| Dependency | Required by | Minimum required public contract |
| --- | --- | --- |
| Customer / Buyer Profile | Features 01–10 | `resolveCustomerActor` / owner facts. |
| Marketplace Supply | Features 01–03, 06–07 | immutable Offering checkout source DTO with source version, seller, amount/pricing tier, delivery/agreement facts. |
| Gig / Demand | Features 01, 09 | `getGigAssignmentCheckoutSource`; CL-04 Feature 03 must have passed before production GigAssignment conversion. |
| Professional Eligibility | selected Features 01, 06–07 | `evaluateProfessionalReadiness` for approved Order action contexts. |
| Track Subscription & Entitlement | Feature 03 onward | `resolveEntitlement`, optional `consumeMeteredEntitlement`. |
| Consent & Disclosure | Feature 04 onward | `queryConsentProof`, active consent version if needed. |
| Media / File Access | Features 05, 07, 10 | ready asset facts, contextual attachment validation, `issueSignedMediaUrl`. |
| Payment / Payout / Tax | Feature 06 onward | provider-neutral payment/refund initiation and normalized result contracts. |
| Admin Review / Compliance Hold | Features 06–10 | `evaluateComplianceHold`; no local hold truth. |
| Booking/delivery Modules | Feature 07 onward | public facts/entitlement consumers only. |
| Review / Dispute | Feature 08 onward | dispute transaction-effect/settlement contracts; CL-04 Features 11–12 must exist before full production settlement proof. |
| Privacy / Data Erasure | Feature 10 | canonical target request/result contract and retention-exemption references. |

### Architecture decisions required before affected production work

1. CustomerProfile nullability/backfill and legacy `buyerUserId` semantics — blocks final production Order schema constraint.
2. Exact Order transition matrix by source/delivery kind — blocks full production mutation set in Features 06–07.
3. Commercial pricing freeze point — blocks Feature 03 production behavior.
4. Order source XOR database enforcement — blocks Feature 01 exit gate.
5. Fee-field semantics — blocks Feature 03 final arithmetic contract.
6. Agreement supersession model — blocks advanced supersession in Feature 04/05; basic single Agreement execution can proceed if supersession is explicitly deferred.
7. Agreement legacy field cleanup — does not block basic normalized implementation if compatibility fields are treated as non-authoritative.
8. Manual-signature workflow details — block production manual completion beyond recording opt-out.
9. AgreementAccessGrant TTL/use policy — blocks Feature 05 production issue/access behavior.
10. Step-up action matrix — blocks exact enforcement only where root policy requires it.
11. Refund/dispute Order transition semantics — blocks Feature 08 production settlement behavior.
12. Retention durations/dispositions — block destructive privacy/purge behavior in Feature 10.

Providers may be stubbed behind ports while owner-domain behavior is built. Provider selection does not authorize bypassing owner contracts.

---

# Phase 1 — Order Source-of-Truth Foundation

## 01 Order Source Integrity and Public Contracts

### Objective

Establish the stable Transaction / Order boundary: source DTOs, participant facts, input/result contracts, database source-integrity rules, and public read contracts required before money/agreement behavior is added.

### Observable Result

A test caller can validate an Offering or accepted GigAssignment source DTO, prove that exactly one source is represented, resolve buyer/seller identities through owner contracts, and receive typed validation/authorization/unsupported errors without creating payment/agreement state.

### Cluster Build-Plan Link

Supports **CL-04 Feature 04 — Order Aggregate and Source Contracts**.

### Dependencies

- root validation/code standards;
- Customer / Buyer Profile contract;
- Marketplace Supply checkout source DTO;
- Gig / Demand `getGigAssignmentCheckoutSource` DTO;
- ProfessionalProfile owner facts as required;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- Prisma migration workflow;
- explicit source-XOR ruling;
- CustomerProfile migration ruling for final production constraint.

### In Scope

- Transaction / Order public contract package;
- source DTO schemas and version fields;
- `validateOrderSourceInvariant` policy;
- `resolveOrderParticipants` policy/service;
- stable error/reason codes;
- Order repository interface limited to Module-owned data;
- database source constraint/index migration after ruling;
- CustomerProfile relation/backfill migration only after ruling;
- query DTO shapes for `getOrder`, `listOrdersForActor`, `getOrderTimeline`;
- contract fixtures for Offering and GigAssignment sources.

### Out of Scope

- actual Order creation mutation;
- pricing snapshot;
- Track entitlements;
- payment;
- Agreement;
- Booking/delivery;
- Review/Dispute;
- Stripe/provider clients;
- neighboring Module repositories.

### Module-Owned Data

- `OrderSourceType`;
- Order source fields/relations and indexes;
- public source contract types;
- no OrderEvent write yet except migration/fixture validation.

### Public Interfaces

Introduce/version:

- `OfferingOrderSourceDTO`;
- `GigAssignmentOrderSourceDTO`;
- `OrderParticipantFactsDTO`;
- `OrderPublicDTO`/summary/timeline contract shells;
- `validateOrderSourceInvariant` internal policy;
- `queryOrderParticipantFacts` contract shell.

### Shared Operations Used

- **`resolveAuthenticatedActor` — Identity & Access:** used by source validation entry points that are user-driven; local policy identifies requested Order action; prohibit `orderAuth.ts`.
- **`authorizeResourceAction` — Role / Authority:** used for source/participant access; local policy supplies buyer/seller/source relationship facts; prohibit local RBAC.
- **`resolveCustomerActor` — Customer / Buyer Profile:** resolves buyer domain identity; prohibit User-only buyer inference.
- **`returnDecisionResult` — shared contract/separate policy:** standardize validation/unsupported/deny result shape; Order-specific reasons remain local.
- **`createRequestContext` — platform:** propagate request/correlation IDs; prohibit local correlation helper.

### Domain Logic

- `sourceType=offering` requires an approved Offering source and no GigAssignment source.
- `sourceType=gig_assignment` requires an accepted GigAssignment source and no Offering source.
- buyer/seller IDs are taken from trusted owner DTOs, not arbitrary client fields.
- CustomerProfile is treated as buyer-domain identity for new behavior; exact DB nullability waits for the migration ruling.
- the source DTO includes a version/status marker sufficient to detect stale conversion.
- GigAssignment remains external truth even when referenced by foreign key.
- Offering lifecycle is never mutated by this Module.

### Authorization / Compliance

- actor must be authenticated for user-driven source actions;
- buyer/system workflow may request Order creation context only through authorized source relationship;
- seller cannot claim arbitrary source ownership;
- admin/support access requires explicit authority decision;
- no readiness/hold/payment gate is implemented yet except contract placeholders.

### Database / Transaction Behavior

- add/verify indexes on source and participant lookup paths;
- after architecture approval, add DB check enforcing source XOR/type consistency;
- preserve unique `gigAssignmentId`;
- do not make a destructive CustomerProfile migration without backfill and rollback plan;
- no in-memory source lock.

### Events / Jobs

None required beyond test contract fixtures. No outbox event until actual Order creation in Feature 02.

### Provider Integration

None.

### UI / Admin Surface

No dedicated UI is required. Existing or future Order UI may consume DTOs after Feature 02.

### Failure Behavior

- invalid source shape → `validation_error`;
- source-type mismatch → `source_not_eligible`/`invalid_source_combination`;
- source version stale → `stale_version`;
- buyer/seller relationship unresolved → deterministic denial/unavailable;
- unresolved CustomerProfile migration during final schema step → `unsupported_until_ruling`, not a guessed constraint.

### Tests

- source DTO validation;
- XOR/type policy unit tests;
- wrong-source-type tests;
- CustomerProfile resolution contract tests;
- seller/buyer spoof tests;
- database constraint migration test once approved;
- unique GigAssignment behavior;
- no cross-Module Prisma repository import test/lint rule where available.

### Documentation Updates

If source-XOR or CustomerProfile migration rulings are approved, update Module architecture Section 8/23/35 and CL-04 architecture unresolved register before migration merges.

### Acceptance Criteria

- source DTOs are versioned and owner-minimal;
- invalid source combinations are rejected consistently;
- buyer/seller facts come only from owner contracts;
- no neighboring table mutation is required;
- final schema constraint reflects an explicit architecture ruling.

### Exit Gate

Before Feature 02:

- typecheck/lint/unit/contract tests pass;
- source DTO contract fixtures pass for Offering and GigAssignment;
- database source rule is either approved+tested or the feature is explicitly blocked from production creation;
- CustomerProfile migration decision is documented;
- no direct Gig/Offering/Track/Payment repository dependency exists.

---

## 02 Atomic Order Creation and Timeline

### Objective

Create authoritative Order truth exactly once from either approved source and append the initial OrderEvent/outbox fact atomically.

### Observable Result

`createOrderFromOffering` and `createOrderFromGigAssignment` create/replay one Order with trusted participant/source facts. Callers can retrieve Order and timeline through public queries.

### Cluster Build-Plan Link

Completes Transaction / Order-owned work for **CL-04 Feature 04**.

### Dependencies

- Feature 01 exit gate;
- canonical idempotency;
- approved DB concurrency primitive;
- `appendDomainLifecycleEvent`;
- transactional outbox / `publishDomainEvent`;
- source owner DTOs;
- CustomerProfile decision for production writes.

### In Scope

- `createOrderFromOffering`;
- `createOrderFromGigAssignment`;
- initial Order row construction;
- initial `OrderEvent`;
- OrderCreated outbox event;
- `getOrder`, `listOrdersForActor`, `getOrderTimeline`;
- participant-scoped read authorization;
- replay/existing result for duplicate GigAssignment conversion;
- initial aggregate transaction tests.

### Out of Scope

- fee waiver/commission;
- payment references;
- Agreement;
- seller acceptance/fulfillment transitions;
- Thread creation mechanics;
- Notification delivery.

### Module-Owned Data

- `Order`;
- `OrderEvent`;
- creation event vocabulary/registry entry;
- no Track/Payment-owned rows.

### Public Interfaces

- `createOrderFromOffering(command)`;
- `createOrderFromGigAssignment(command)`;
- `getOrder(query)`;
- `listOrdersForActor(query)`;
- `getOrderTimeline(query)`;
- `queryOrderParticipantFacts(query)`.

### Shared Operations Used

- **`resolveAuthenticatedActor`** at user-driven create/read boundary; no local session helper.
- **`authorizeResourceAction`** for create/read; Order supplies relationship facts.
- **`executeIdempotentCommand`** wraps semantic creation; local key/fingerprint defines source and buyer.
- **`acquireAggregateLock` / `withOptimisticConcurrency`** serializes source conversion where needed; no in-memory mutex.
- **`appendDomainLifecycleEvent`** writes initial OrderEvent in same DB transaction.
- **`publishDomainEvent`** writes OrderCreated to transactional outbox.
- **`appendAuditEvent`** only for admin/system exceptional creation if audit policy requires; never replaces OrderEvent.
- **`createRequestContext`/`writeStructuredLog`** for safe correlation/ops.

### Domain Logic

1. validate command and idempotency fingerprint;
2. resolve authenticated/system actor;
3. resolve CustomerProfile/source owner facts;
4. authorize create;
5. revalidate source version/status;
6. acquire appropriate source/aggregate concurrency control;
7. create Order with one valid source and trusted buyer/seller IDs;
8. append initial OrderEvent;
9. write OrderCreated outbox event;
10. commit;
11. return stable Order result.

No price/entitlement snapshot is frozen unless the approved freeze point is creation; if that ruling selects creation, Feature 03 logic must be invoked atomically or Feature 02 cannot be released independently in production.

### Authorization / Compliance

- CustomerProfile relationship required for buyer-driven creation under approved migration policy;
- seller facts are owner-provided;
- admin/system creation must use explicit action keys and actor/system identity;
- do not treat Professional readiness as implicitly satisfied unless the source contract guarantees the applicable readiness and architecture accepts that guarantee.

### Database / Transaction Behavior

- Order + initial OrderEvent + outbox in one transaction;
- unique GigAssignment conversion handled as idempotent existing/replay or deterministic conflict;
- no network/provider calls inside transaction;
- preserve source version/evidence in approved snapshot/metadata shape;
- OrderEvent insert-only.

### Events / Jobs

Emit `OrderCreated` after commit via outbox. Event contains minimal source type/ID, aggregate ID/version, buyer/seller references permitted by privacy policy, and correlation/causation IDs. It does not contain full source text or provider data.

### Provider Integration

None.

### UI / Admin Surface

Minimal Order detail/timeline read surface may be wired if CL-04 UI expects it. Do not build checkout/payment UI yet.

### Failure Behavior

- source disappeared/stale → no Order;
- duplicate same command → replay existing Order;
- duplicate key with changed fingerprint → idempotency conflict;
- concurrency collision → retryable/stale conflict according to platform primitive;
- outbox persistence failure → transaction rolls back;
- downstream consumers unavailable → committed Order remains truth; outbox retries.

### Tests

- Offering source create;
- GigAssignment source create;
- duplicate GigAssignment conversion;
- idempotency replay/conflict;
- OrderEvent/outbox atomicity;
- participant authorization/read scoping;
- no raw source client facts accepted;
- transaction rollback on event/outbox failure;
- source-owner contract failure.

### Documentation Updates

Add/confirm OrderCreated event schema/version. If creation semantics settle source snapshot or CustomerProfile behavior, update architecture first.

### Acceptance Criteria

- both approved source types create authoritative Order through public contracts;
- one accepted GigAssignment cannot create two Orders;
- initial OrderEvent always accompanies Order creation;
- OrderCreated is reliably publishable after commit;
- readers do not require direct neighboring repositories.

### Exit Gate

- all Feature 01–02 tests pass;
- migration checks pass;
- contract tests with both source owners pass;
- duplicate/concurrency test passes;
- no pricing/payment/agreement behavior is accidentally implemented.

---

# Phase 2 — Commercial Snapshot

## 03 Pricing, Fee-Waiver, and Commission Snapshot

### Objective

Resolve Track-owned commercial policy and freeze the historical buyer fee and Professional commission effect on the Order at the explicitly approved freeze point.

### Observable Result

An Order exposes a deterministic, explainable frozen commercial snapshot. Later plan/subscription/grant changes do not change that Order.

### Cluster Build-Plan Link

Implements **CL-04 Feature 05 — Commercial Pricing and Entitlement Snapshot**.

### Dependencies

- Feature 02;
- explicit pricing-freeze ruling;
- explicit fee-field definitions/rounding rules;
- Track `resolveEntitlement` and optional `consumeMeteredEntitlement`;
- Offering/GigAssignment base commercial source facts;
- canonical idempotency/concurrency.

### In Scope

- `resolveAndSnapshotOrderPricing`;
- `composeOrderCommercialSnapshot`;
- typed pricing snapshot schema/version;
- buyer platform fee amount/waiver result;
- seller commission BPS/amount;
- source subscription/grant evidence refs;
- deterministic arithmetic/rounding;
- snapshot-read inclusion in Order/payment-requirements DTO;
- Track usage receipt correlation if policy says the action is metered at this point.

### Out of Scope

- current Track plan truth storage;
- subscription lifecycle;
- Stripe/payment fees;
- sales-tax calculation;
- payout ledger/proceeds execution;
- provider application-fee semantics unless explicitly ruled to be part of the commercial snapshot.

### Module-Owned Data

- Order pricing fields;
- `pricingSnapshotJson` as versioned historical evidence if retained by architecture;
- OrderEvent/outbox facts for pricing freeze;
- no TrackUsageEvent rows written locally.

### Public Interfaces

- `resolveAndSnapshotOrderPricing(command)`;
- `getOrderPaymentRequirements(query)` updated with frozen commercial facts;
- optional `recordOrderCommercialUsage` orchestration calling Track owner.

### Shared Operations Used

- **`resolveEntitlement` — Track:** buyer fee waiver and seller commission; local policy maps values to frozen Order fields; prohibit local premium/commission helpers.
- **`consumeMeteredEntitlement` — Track:** only if approved perk usage counts at freeze/checkout; local policy defines counting event; prohibit local counters.
- **`executeIdempotentCommand`** prevents double freeze/usage;
- **`withOptimisticConcurrency`/lock** prevents two different snapshots winning;
- **`appendDomainLifecycleEvent`** records snapshot fact;
- **`publishDomainEvent`** emits pricing-ready/frozen fact if downstream consumption requires it;
- **`returnDecisionResult`** for Track unavailable/deny remediation.

### Domain Logic

- source base amount/currency comes from immutable owner source facts;
- buyer fee waiver comes only from Track decision;
- seller commission rate comes only from Track decision;
- local deterministic calculation produces frozen cents/BPS values;
- snapshot records calculation version, source version, entitlement grant references, effective result, and safe reason/evidence;
- no later entitlement change mutates historical snapshot;
- if Track is unavailable before freeze, do not silently grant premium or silently choose an unapproved default;
- if the approved freeze point is Order creation, this command must be integrated atomically into Feature 02's create transaction before production release.

### Authorization / Compliance

- caller cannot supply effective waiver/commission values as authority;
- Track result affects commercial calculation only; it does not confer Order authorization;
- sensitive plan metadata is not exposed beyond explanation needed by Order UI/support.

### Database / Transaction Behavior

- snapshot write guarded so it occurs once per approved snapshot version;
- if re-pricing before freeze is allowed, architecture must define it; otherwise treat existing frozen snapshot as immutable;
- add indexes on Track evidence IDs only if operational queries justify them;
- do not add foreign keys to Track references until that architectural choice is explicit;
- arithmetic uses integers/BPS, never floating-point money.

### Events / Jobs

- optional `OrderPricingFrozen` outbox event;
- Track usage call uses its own idempotency key correlated to Order and entitlement/action;
- no background job required for basic freeze.

### Provider Integration

None. Processor fee and sales-tax provider logic remain Payment-owned.

### UI / Admin Surface

Checkout/Order price breakdown may show base amount, buyer platform fee/waiver, seller commission explanation where appropriate, and safe reason labels. Do not show internal entitlement internals or processor secrets.

### Failure Behavior

- Track unavailable → `dependency_unavailable` or approved fallback only;
- invalid entitlement type/value → validation/manual review;
- rounding overflow/negative amount → validation failure;
- concurrent snapshot → one wins, other replays/conflicts;
- duplicate usage call → Track returns idempotent receipt;
- later plan change → no Order mutation.

### Tests

- waiver on/off;
- multiple commission BPS values;
- currency/minor-unit rounding;
- exact integer calculations;
- future Track change leaves Order unchanged;
- snapshot version/provenance;
- idempotent freeze;
- concurrent different snapshot attempt rejected;
- Track unavailable/invalid decision;
- no local Track write.

### Documentation Updates

Before production implementation, record approved freeze point and fee-field definitions in `module-architecture.md` and CL-04 architecture if they resolve deferred decisions.

### Acceptance Criteria

- historical Order fully explains the frozen commercial result without reading current plan state;
- Track remains the only policy/usage owner;
- calculation is deterministic and tested;
- downstream Payment receives frozen commercial facts, not current entitlement lookups.

### Exit Gate

- approved freeze-point ruling is recorded;
- all pricing tests pass;
- changing Track fixture after freeze does not alter returned historical Order;
- no premium/commission policy exists inside Transaction / Order beyond mapping external decisions to frozen values.

---

# Phase 3 — Agreement Execution and Contract Proof

## 04 Agreement Template and Execution State

### Objective

Implement versioned Agreement templates and Order-specific agreement execution state through consent/manual-opt-out and signer progress without final PDF/hash delivery mechanics.

### Observable Result

An eligible Order can instantiate a versioned Agreement; authorized signers can satisfy required generic consent linkage, record Agreement-specific electronic consent or manual opt-out, and complete signer state with immutable event history.

### Cluster Build-Plan Link

Implements **CL-04 Feature 06 — Agreement Template and Order-Specific Agreement**.

### Dependencies

- Features 01–03;
- Consent & Disclosure `queryConsentProof`;
- authority;
- template governance ruling;
- decision on whether advanced supersession is deferred or schema is changed;
- canonical idempotency/concurrency/event/outbox/audit.

### In Scope

- AgreementTemplate create/activate/retire/read;
- `instantiateAgreementForOrder`;
- Agreement-specific consent records;
- manual opt-out recording only to the extent workflow is approved;
- signer record/request state;
- `recordAgreementSignature` for local/provider-neutral verified evidence;
- AgreementEvent append-only history;
- `getAgreementPackage`;
- template/version immutability rules;
- signer authorization/role checks;
- compatibility fields treated as non-authoritative.

### Out of Scope

- final PDF rendering;
- document snapshot/hash;
- Media signed retrieval;
- e-sign provider implementation unless separately selected;
- Payment;
- advanced supersession if `orderId @unique` conflict remains unresolved;
- legal drafting/content approval beyond approved template input.

### Module-Owned Data

- `AgreementTemplate` + status;
- `Agreement` + status/requirements;
- `AgreementElectronicConsent`;
- `AgreementSignature`;
- `AgreementEvent`;
- relevant enums.

### Public Interfaces

- `createAgreementTemplate`;
- `activateAgreementTemplate`;
- `retireAgreementTemplate`;
- `instantiateAgreementForOrder`;
- `recordAgreementElectronicConsent`;
- `recordManualSignatureOptOut`;
- `requestAgreementSignatures`;
- `recordAgreementSignature`;
- `getAgreementPackage`;
- `evaluateAgreementExecutionReadiness` internal/public decision as needed.

### Shared Operations Used

- **`resolveAuthenticatedActor` / `authorizeResourceAction`** for admin template and signer actions; prohibit local RBAC.
- **`queryConsentProof` — Consent:** validates generic versioned proof; local Agreement consent remains separate.
- **`resolveActiveConsentVersion`** if active disclosure version must be selected; no local version catalog.
- **`executeIdempotentCommand`** for instantiation/consent/signature requests/completion.
- **`withOptimisticConcurrency`/lock** for Agreement/signer races.
- **`transitionLifecycleState`** supplies plumbing; Agreement graph remains local.
- **`appendDomainLifecycleEvent`** writes AgreementEvent transactionally.
- **`appendAuditEvent`** for template activation/retirement and privileged actions.
- **`recordSensitiveAccess`** for signature/manual-opt-out evidence when policy requires.
- **`publishDomainEvent` / `requestNotification`** after commit.

### Domain Logic

- template `(key, version)` is immutable historical identity;
- only active approved template can instantiate a production Agreement;
- Order captures template ID/key/version;
- generic ConsentLog proof must match expected User/type/version; it does not mark Agreement signed;
- AgreementElectronicConsent records contextual decision and disclosure hash/version;
- manual opt-out can be recorded only when template/policy allows it;
- required signer roles derive from the Agreement/template policy, not from arbitrary client list;
- signature command binds signer identity/role and verified execution evidence;
- significant execution changes append AgreementEvent;
- `buyerSigUrl`/`professionalSigUrl` are not authoritative proof;
- candidate/organization signer use is disabled/unsupported until explicitly approved for Order agreements.

### Authorization / Compliance

- admin template commands use explicit Role / Authority action keys;
- signer may act only for their required role/identity;
- electronic signature cannot proceed without required generic disclosure proof and Agreement-specific contextual consent;
- manual opt-out path is retained where approved;
- do not store raw biometric data;
- IP/user-agent/session evidence is minimized and stored only according to approved evidence policy.

### Database / Transaction Behavior

- unique template key/version enforced;
- Agreement creation obeys current one-per-Order unique constraint until supersession ruling changes schema;
- consent/signature update + AgreementEvent in same transaction;
- signer concurrency is protected;
- no provider/network call inside core transaction;
- do not mutate active template content in place.

### Events / Jobs

Agreement event/outbox families: instantiated, consent requested/granted/declined, manual path selected, signature requested/completed/declined. Notification is requested asynchronously after commit.

### Provider Integration

No provider-specific e-sign implementation required. If a normalized provider callback is used in tests, it must enter through the same `recordAgreementSignature`-style command contract.

### UI / Admin Surface

- minimal Agreement template admin create/activate/retire surface if CL-04 product requires it;
- signer consent/signature progress;
- participant Agreement status view;
- manual opt-out UI only where the operational workflow has been approved.

### Failure Behavior

- inactive/unknown template → validation denial;
- duplicate Agreement → existing/idempotent result or conflict;
- wrong disclosure version → consent denial;
- missing generic consent → `agreement_not_ready`/consent required;
- signer role mismatch → authorization denial;
- duplicate signature → replay;
- concurrent decline/sign → stale transition conflict;
- supersession request while unresolved → `unsupported_until_ruling`.

### Tests

- template uniqueness/version immutability;
- activation/retirement authority;
- Agreement one-per-Order behavior;
- ConsentLog vs AgreementElectronicConsent separation;
- wrong consent type/version/user;
- manual opt-out availability;
- signer role/identity authorization;
- duplicate signature idempotency;
- consent/signature concurrency;
- AgreementEvent atomicity;
- notification/outbox after commit.

### Documentation Updates

If template governance, signer-role scope, manual workflow, or supersession is settled, update Module architecture before broadening implementation.

### Acceptance Criteria

- Agreement-specific execution state is independently auditable from generic ConsentLog;
- signers cannot bypass consent/role requirements;
- template history is preserved;
- every significant execution mutation has AgreementEvent;
- advanced supersession is not faked through compatibility fields.

### Exit Gate

- all Agreement execution tests pass;
- no finalized document/hash logic is required to prove the execution-state slice;
- no provider-specific payload enters core contracts;
- unresolved supersession/manual completion paths remain explicitly bounded.

---

## 05 Agreement Document Finalization and Secure Access

### Objective

Render/finalize immutable Agreement documents, bind SHA-256 proof to exact archived bytes, and expose short-lived contextual contract access through Media-owned transport.

### Observable Result

A fully execution-ready Agreement can produce an immutable versioned `AgreementDocumentSnapshot`. An authorized participant can receive a short-lived access path; unauthorized/expired/revoked access fails and is audited. Re-hashing archived bytes detects mismatch.

### Cluster Build-Plan Link

Implements **CL-04 Feature 07 — Agreement Document Finalization and Secure Access**.

### Dependencies

- Feature 04;
- Media / File Access ready/private asset and signed-access contracts;
- canonical queue/retry;
- canonical `calculateChecksum` SHA-256 primitive;
- `generateSecureToken`/temporary grant mechanics;
- `recordSensitiveAccess`;
- AgreementAccessGrant TTL/use ruling;
- renderer choice/port implementation only as needed.

### In Scope

- AgreementDocumentRenderer port;
- render input built only from frozen Order/Agreement/template/signature facts;
- durable render/finalization worker;
- Media private-object handoff;
- `AgreementDocumentSnapshot` versioning;
- exact-byte SHA-256 hash binding/verification;
- `finalizeAgreementDocument`;
- `verifyAgreementDocumentHash`;
- AgreementAccessGrant issue/use/revoke/expire;
- Media signed URL request after contextual grant;
- sensitive access audit;
- optional AgreementEvent hash-chain use only if canonical ruling is approved.

### Out of Scope

- generic Media upload/storage implementation;
- permanent public URLs;
- privacy destruction of retention-locked proof;
- Payment;
- external e-sign provider as source truth;
- custom cryptography.

### Module-Owned Data

- `AgreementDocumentSnapshot`;
- `AgreementAccessGrant`;
- Agreement finalization/archive/hash fields where retained;
- AgreementEvent document/access events.

### Public Interfaces

- `generateAgreementDocument`;
- `recordAgreementDocumentSnapshot`;
- `finalizeAgreementDocument`;
- `verifyAgreementDocumentHash`;
- `issueAgreementAccessGrant`;
- `revokeAgreementAccessGrant`;
- `getAgreementPackage` updated with safe snapshot/access metadata.

### Shared Operations Used

- **`enqueueReliableJob` / `executeRetryWithBackoff`:** renderer/finalization/verification/expiration jobs; local completion semantics remain Agreement-owned; prohibit custom queue/retry loop.
- **`calculateChecksum`:** SHA-256 exact bytes; local policy binds checksum to legal document snapshot; prohibit local SHA helper.
- **`hashChainRecords`:** use only if approved; Agreement defines canonical fields/partition; do not assume proposed ruling is binding.
- **`generateSecureToken`:** grant secret creation; no weak/random local token helper.
- **`manageTemporaryAccessGrant` / `revokeTemporaryAccessGrant`:** shared status/TTL/token plumbing; `AgreementAccessGrant` stays separate truth.
- **`issueSignedMediaUrl` — Media:** actual transport URL after local contextual grant; prohibit R2/S3 presign code here.
- **`recordSensitiveAccess`:** agreement view/download/hash/access denial evidence.
- **`appendDomainLifecycleEvent` / `publishDomainEvent` / `appendAuditEvent`:** document and access lifecycle evidence/effects.
- **`createRequestContext`, `writeStructuredLog`, `sanitizeTelemetryMetadata`, `recordIntegrationFailure`:** safe worker/provider observability.

### Domain Logic

1. verify Agreement execution readiness;
2. freeze deterministic render input/version;
3. enqueue idempotent render job;
4. render bytes through selected renderer adapter;
5. store private bytes through Media owner;
6. compute checksum from exact bytes that are archived;
7. create immutable snapshot with unique `(agreementId, version)`;
8. verify required execution state and finalize Agreement/snapshot;
9. append AgreementEvent/outbox;
10. for retrieval, authorize actor/context → create AgreementAccessGrant → call Media signed-access API → audit issuance/access;
11. expiry/revoke never deletes the legal snapshot.

No finalized snapshot bytes or hash are overwritten in place.

### Authorization / Compliance

- participant/admin/support access is explicit and contextual;
- sensitive access is audited;
- permanent public contract URLs prohibited;
- retention lock prevents unauthorized destructive delete;
- no full document text in logs/events;
- grant tokens stored only as hashes/protected form;
- step-up is delegated to Identity if root policy requires it.

### Database / Transaction Behavior

- unique `(agreementId, version)` enforced;
- document snapshot insert + AgreementEvent/outbox atomic after Media object exists and checksum is known;
- avoid holding DB transaction during renderer/storage network calls; use durable orchestration/idempotent command boundary;
- reconciliation must handle Media object created but snapshot write failed;
- grant use/revoke/expire uses row/version locking as appropriate;
- finalized snapshot row is append/version only, not updated to new bytes/hash.

### Events / Jobs

- render/finalization worker;
- grant-expiration worker via `runDeadlineExpiration`;
- hash-verification/reconciliation worker;
- events: document generated/finalized/archived, hash verified/tamper detected, access issued/viewed/downloaded/denied/revoked/expired.

### Provider Integration

Renderer adapter may be Puppeteer/PDFKit/external/manual only through the domain port. Credentials/config remain outside domain code. Media owns storage provider credentials.

### UI / Admin Surface

- authorized view/download action;
- safe document version/hash verification state;
- admin/support access only through explicit authority and audit;
- no raw object key/provider URL displayed as permanent truth.

### Failure Behavior

- render timeout/transient error → retry;
- invalid deterministic input → terminal/manual review;
- Media upload succeeds but snapshot fails → reconciliation cleans/reattaches according to Media/Agreement policy;
- checksum mismatch → `tamper_check_failed`/manual review; never overwrite expected hash;
- expired/revoked grant → denial + access audit;
- Media unavailable during retrieval → grant remains domain truth but URL issuance fails retryably;
- retry exhaustion → dead-letter + IntegrationFailure/operator path.

### Tests

- exact-byte SHA-256 fixture;
- deterministic render input;
- immutable versioning;
- unique version race;
- render job idempotency;
- Media success/failure/reconciliation;
- authorized/unauthorized access;
- grant use/revoke/expiry race;
- signed URL boundary;
- sensitive access metadata redaction;
- hash mismatch behavior;
- no permanent URL persistence.

### Documentation Updates

Record approved grant TTL/use semantics, renderer choice if architecture-relevant, and hash-chain ruling if adopted.

### Acceptance Criteria

- exact archived bytes can be reproducibly verified;
- finalized snapshot cannot be edited in place;
- AgreementAccessGrant and Media signed transport remain distinct;
- all sensitive access is denied/allowed through explicit policy and audited;
- worker retries do not duplicate snapshots/events.

### Exit Gate

- all document/access/worker tests pass;
- grant policy is approved for production;
- no direct object-storage/signing code exists in Transaction / Order;
- hash verification reproduces known fixture hash and detects mutation;
- operator can see dead-lettered document work safely.

---

# Phase 4 — Payment and Fulfillment Transaction State

## 06 Payment Boundary and Verified Payment Application

### Objective

Connect Order to Payment / Payout / Tax through provider-neutral contracts and apply verified payment results to Order exactly once without making Transaction / Order a Stripe integration owner.

### Observable Result

An eligible Order exposes payment requirements, initiates Payment-owned checkout through a public contract, and transitions from a trusted normalized payment result. Duplicate provider callbacks produce one semantic Order effect.

### Cluster Build-Plan Link

Implements **CL-04 Feature 08 — Payment Initiation and Verified Order Payment**.

### Dependencies

- Features 01–05 as applicable;
- approved Order transition matrix for payment states;
- Payment public initiation/result contracts;
- `evaluateComplianceHold`;
- Agreement gate behavior;
- canonical idempotency/concurrency/outbox.

### In Scope

- `evaluateOrderPrePaymentGates`;
- `getOrderPaymentRequirements` final contract;
- `requestOrderPayment` orchestration to Payment owner;
- `applyPaymentConfirmationToOrder`;
- `applyPaymentFailureToOrder`;
- provider-correlation field write policy only as explicitly approved;
- paid timestamp/status/event/outbox;
- conflicting normalized outcome handling/reconciliation path.

### Out of Scope

- Stripe SDK;
- webhook signature verification;
- `ProcessedStripeEvent`;
- sales-tax provider logic;
- payment capture/refund provider execution;
- payout/KYC/tax/ledger;
- dispute adjudication.

### Module-Owned Data

- Order payment-facing state/status/timestamps;
- approved provider-correlation fields as references only;
- `OrderEvent`;
- payment-effect outbox events.

### Public Interfaces

- `evaluateOrderPrePaymentGates`;
- `getOrderPaymentRequirements`;
- `requestOrderPayment`;
- `applyPaymentConfirmationToOrder`;
- `applyPaymentFailureToOrder`.

### Shared Operations Used

- **`resolveAuthenticatedActor` / `authorizeResourceAction`** for buyer payment initiation.
- **`evaluateComplianceHold`** before payment action; local mapping decides which holds block.
- **`evaluateProfessionalReadiness`** only where approved source/action requires it; do not reconstruct raw readiness.
- **`executeIdempotentCommand`** for payment initiation/application.
- **`acquireAggregateLock`/`withOptimisticConcurrency`** for state races.
- **`transitionLifecycleState`** for approved Order graph.
- **`appendDomainLifecycleEvent` / `publishDomainEvent`** for verified payment effect.
- **`createRequestContext` / `recordIntegrationFailure`** for Payment dependency degradation.
- **`requestNotification`** for user-facing success/failure state after commit.

### Domain Logic

Pre-payment gate composes:

- valid/frozen source and commercial snapshot;
- Agreement readiness when required;
- CustomerProfile/authority;
- applicable Professional readiness if architecture requires recheck;
- active ComplianceHold results;
- current Order state/version.

Payment initiation sends only frozen amount/currency and approved tax/source context to Payment. Payment returns a provider-neutral result. Only the normalized verified result can change Order payment state.

Raw provider `succeeded`, `requires_action`, or other statuses must never appear as core Order API vocabulary.

### Authorization / Compliance

- buyer/system action authorized;
- no client success redirect as proof;
- step-up only through Identity if root action matrix requires it;
- payment secrets/provider tokens never persisted in Order event metadata;
- hold gate is action-specific and returns safe reasons.

### Database / Transaction Behavior

- normalized result application is idempotent;
- Order transition + paidAt/reference fields + OrderEvent + outbox are atomic;
- provider network call occurs outside the authoritative write transaction;
- stale/conflicting result is not blindly retried into a different state;
- provider-correlation fields are indexed only as approved references.

### Events / Jobs

- `OrderPaymentConfirmed`/payment-failed fact after commit;
- reconciliation work may be queued for conflicting/missing effects;
- Payment owner handles webhook/provider retry/dedupe.

### Provider Integration

None directly. The Payment module is the integration boundary. Transaction / Order tests consume normalized Payment fixtures.

### UI / Admin Surface

- checkout/payment readiness state;
- recoverable failure/retry path;
- no display of provider secrets;
- admin diagnostics show normalized references/reason categories only.

### Failure Behavior

- Payment dependency timeout → Order remains pre-payment truth;
- duplicate normalized success → replay/no duplicate OrderEvent;
- success then conflicting failure → manual review/reconciliation, no blind rollback;
- browser redirect spoof → ignored as proof;
- hold active → deny new payment action;
- outbox consumer failure → paid Order remains committed truth.

### Tests

- pre-payment gate combinations;
- agreement required/not ready;
- hold allow/deny;
- normalized payment success;
- duplicate success;
- conflicting outcome;
- stale aggregate version;
- provider outage;
- client redirect spoof;
- no ProcessedStripeEvent/direct Stripe import;
- event/outbox atomicity.

### Documentation Updates

If payment reference ownership or exact payment transition semantics are settled, update architecture before code depends on them.

### Acceptance Criteria

- raw Stripe payload never enters Transaction / Order domain code;
- one verified financial event creates one Order business effect;
- Order remains coherent when Payment is degraded;
- payment requirement DTO is provider-neutral and based on frozen Order facts.

### Exit Gate

- all normalized Payment contract tests pass;
- duplicate/replay/conflict tests pass;
- no direct provider client/webhook/dedupe exists here;
- approved payment-state transition rules are documented and enforced.

---

## 07 Fulfillment, Delivery Entitlement, and Completion

### Objective

Implement the approved post-payment Order lifecycle and expose the canonical Order decision used by Booking, Media, Digital Goods, and Video to determine whether a requested delivery action is transactionally permitted.

### Observable Result

Participants can progress an Order through applicable seller/fulfillment states. CL-05 consumers can call `authorizeOrderEntitlement` and receive a stable decision without reading Stripe/payment tables.

### Cluster Build-Plan Link

Implements **CL-04 Feature 09 — Order Fulfillment, Delivery Entitlement, and Completion**.

### Dependencies

- Feature 06;
- approved source/delivery-kind Order transition matrix;
- Professional readiness query where applicable;
- ComplianceHold;
- Media ready attachment interface;
- Booking/delivery public contracts/fixtures;
- canonical idempotency/concurrency/events.

### In Scope

- `acceptOrder` if applicable;
- `startOrderFulfillment`;
- `recordOrderDelivery`;
- `completeOrder`;
- `cancelOrder`;
- `authorizeOrderEntitlement`;
- `attachOrderFile`;
- participant Order progress DTO;
- Order completion event contract;
- source/delivery-kind-specific gating encoded only from approved matrix.

### Out of Scope

- Booking lifecycle;
- video room/playback grant;
- digital download grant;
- Media storage/signed access;
- payout execution;
- Review/Dispute lifecycle;
- unapproved universal seller-acceptance semantics.

### Module-Owned Data

- Order status/timestamps;
- OrderEvent;
- `OrderFile` context;
- Order entitlement decision contract;
- no downstream grant rows.

### Public Interfaces

- `acceptOrder`;
- `startOrderFulfillment`;
- `recordOrderDelivery`;
- `completeOrder`;
- `cancelOrder`;
- `authorizeOrderEntitlement`;
- `attachOrderFile`;
- `getOrder`/summary updated with fulfillment state.

### Shared Operations Used

- **`authorizeResourceAction`** for participant mutations.
- **`evaluateProfessionalReadiness`** at exact approved action checkpoints.
- **`evaluateComplianceHold`** for action-specific block behavior.
- **`attachValidatedMedia` — Media/context contract:** OrderFile creation only; no file mechanics.
- **`executeIdempotentCommand`** on completion/delivery/cancel and other retryable commands.
- **`transitionLifecycleState`** for approved source-specific graph.
- **`acquireAggregateLock`/`withOptimisticConcurrency`** for conflicting transitions.
- **`appendDomainLifecycleEvent` / `publishDomainEvent`** for fulfillment facts.
- **`requestNotification`** after commit.

### Domain Logic

- transition legality depends on approved Order source/delivery-kind graph;
- `awaiting_seller` is used only where approved;
- downstream service/digital delivery state never becomes Order truth automatically without approved completion evidence;
- `authorizeOrderEntitlement` evaluates current Order status, participant relationship, refund/dispute effect, and applicable hold, and returns only transaction entitlement;
- delivery module owns its own grant/usage/revocation rules;
- cancellation after payment does not assert refund occurred;
- completion is the authoritative transaction completion fact used by payout/review/reward consumers, but the exact trigger criteria must be approved.

### Authorization / Compliance

- buyer/seller/admin action scopes explicit;
- hold checks action-specific;
- attachment uses Media readiness and contextual authorization;
- no broad admin file access;
- sensitive/healthcare Order context may require external healthcare/access decisions where applicable; do not reconstruct them locally.

### Database / Transaction Behavior

- transition + timestamp + OrderEvent + outbox atomic;
- attachment creation transactionally links only ready MediaAsset facts validated by Media contract;
- stale versions return conflict;
- completion/cancellation/dispute races serialized;
- no external delivery/provider call inside transaction.

### Events / Jobs

- OrderAccepted/Started/Delivered/Completed/Cancelled facts;
- completion is consumed by Payment/Payout/Tax, Review/Dispute, rewards, Notification, and delivery owners according to their own policies;
- no owner-specific downstream rows are written here.

### Provider Integration

None.

### UI / Admin Surface

Participant Order progress/actions and minimal OrderFile context. Do not invent Booking/video/download management UI under Transaction / Order.

### Failure Behavior

- invalid/stale transition → stable conflict;
- downstream delivery unavailable → do not falsely transition to delivered/completed;
- duplicate completion → replay;
- hold becomes active → block applicable action;
- cancellation requires financial follow-up → return/emit approved handoff, not fake refund;
- Media asset not ready → attachment denied.

### Tests

- every allowed/forbidden transition in approved matrix;
- source/delivery-kind differences;
- participant authorization;
- Professional readiness recheck if required;
- hold allow/deny;
- Order entitlement decisions across paid/refunded/disputed/cancelled/completed states;
- wrong participant access;
- OrderFile Media boundary;
- completion idempotency/concurrency;
- downstream event contract tests.

### Documentation Updates

The exact transition/completion semantics must be recorded in architecture before this feature can pass production exit gate.

### Acceptance Criteria

- Order lifecycle is explicit and source/delivery aware;
- CL-05 can authorize delivery from one public Order decision without reading Payment/provider internals;
- downstream grants/lifecycles remain outside this Module;
- completion is deterministic and evented.

### Exit Gate

- approved transition matrix exists and all transition tests pass;
- Order entitlement positive/negative contract fixtures pass for CL-05 consumers;
- no Booking/Video/Digital/Media truth is written directly;
- completion and cancellation races are proven safe.

---

# Phase 5 — Settlement Participation After Review / Dispute

## 08 Refund and Dispute Transaction Effects

### Objective

Implement only the Transaction / Order-owned part of commercial resolution: apply dispute state and normalized refund/settlement effects while keeping adjudication, provider execution, payout, and hold lifecycles with their owners.

### Observable Result

Review / Dispute and Payment can drive Transaction / Order through public provider-neutral commands. The system can distinguish dispute decision, Order refund attachment, provider refund execution, and hold state.

### Cluster Build-Plan Link

Supports the Transaction / Order portion of **CL-04 Feature 12 — Dispute Adjudication, Refund/Release, and Closure**. This Module feature must not be treated as available before CL-04 Features 11–12 define the Review / Dispute contracts and lifecycle semantics.

### Dependencies

- Feature 07;
- CL-04 Feature 11 dispute intake contract;
- CL-04 Feature 12 adjudication/settlement contract;
- explicit Order `disputed`/refund transition semantics;
- Payment normalized refund result contract;
- Hold owner contract;
- canonical workflow/idempotency/concurrency/event mechanisms.

### In Scope

- `enterOrderDisputeState`;
- `applyRefundOutcomeToOrder`;
- `resolveOrderDisputeState`;
- `getOrderSettlementFacts`;
- Order/RefundStatus transaction effects;
- normalized settlement workflow participation;
- event/outbox facts;
- reconciliation of missing Order effect from already-authoritative external owner result.

### Out of Scope

- creating/resolving Dispute;
- deciding refund vs release;
- Stripe refund API;
- payout/ledger release;
- creating/releasing ComplianceHold;
- moderation/legal adjudication;
- chargeback lifecycle unless Payment introduces it separately.

### Module-Owned Data

- `Order.status` effect;
- `Order.refundStatus`;
- OrderEvent/outbox settlement facts;
- no Dispute/Payment/Hold records.

### Public Interfaces

- `enterOrderDisputeState`;
- `applyRefundOutcomeToOrder`;
- `resolveOrderDisputeState`;
- `getOrderSettlementFacts`.

### Shared Operations Used

- **`executeIdempotentCommand`** for all external-result applications.
- **`acquireAggregateLock`/`withOptimisticConcurrency`** for dispute/refund/completion races.
- **`transitionLifecycleState`** with approved Order matrix.
- **`orchestrateWorkflowSteps`** only if a durable settlement coordinator is explicitly owned/needed; shared runner does not own Dispute/Payment/Hold truth.
- **`deduplicateDomainEvent`** for event-driven result handlers.
- **`appendDomainLifecycleEvent` / `publishDomainEvent`** for Order effect.
- **`appendAuditEvent`** for high-risk admin correction if present.
- **`recordIntegrationFailure`** for settlement coordination failures.

### Domain Logic

- Dispute open may request Order transaction effect but does not create hold/refund;
- Review / Dispute adjudication result is accepted only from its public contract/event with version/correlation;
- Payment refund execution result is accepted only as normalized verified result;
- partial/full/denied refund maps to approved `RefundStatus` and Order transition rules;
- settlement release may restore/complete an Order only under explicit transition policy;
- hold release remains Hold-owned;
- partial failure retains each owner's existing truth and queues/reconciles missing downstream effects rather than fabricating success.

### Authorization / Compliance

- user actors do not directly submit provider settlement results;
- admin corrections use explicit authority and audit;
- step-up only if root policy requires it;
- sensitive dispute evidence is not carried in Order events; use stable refs/reason codes only.

### Database / Transaction Behavior

- Order/refund effect + OrderEvent/outbox atomic;
- duplicates replay;
- concurrent completion/cancel/refund/dispute commands serialized or version-checked;
- no long transaction across Payment/Hold/Dispute network calls;
- reconciliation never overwrites a newer aggregate version.

### Events / Jobs

- dispute transaction-effect applied;
- refund requested/effect changed/refunded/denied facts as approved;
- durable settlement/reconciliation worker if cross-owner step fails;
- dead-letter/manual review for irreconcilable conflicting owner outcomes.

### Provider Integration

None directly. Payment owns refund provider interaction.

### UI / Admin Surface

Order detail may show transaction-facing disputed/refund state. Dispute adjudication UI remains Review / Dispute. Provider refund details remain Payment-owned.

### Failure Behavior

- Dispute resolved but Payment refund fails → Order reflects only verified effect; workflow remains pending/retryable outside fake success;
- duplicate refund result → replay;
- conflicting result → manual review;
- hold release failure → does not change local hold truth;
- Review/Dispute unavailable → no direct Dispute table fallback;
- stale Order version → conflict/reconcile.

### Tests

- dispute-open Order effect;
- refund partial/full/denied mappings after ruling;
- duplicate settlement event;
- concurrent completion/refund/dispute;
- Payment contract success/failure/retry;
- Review/Dispute contract tests;
- hold separation;
- no direct Stripe/Dispute/Hold repository write;
- event/audit completeness.

### Documentation Updates

Update architecture when exact `disputed` exit paths, partial refund semantics, and settlement-finality rules are approved.

### Acceptance Criteria

- system can identify which owner controls adjudication, financial execution, Order effect, and hold;
- one owner result produces one Transaction / Order effect;
- partial failures are recoverable without duplicate money effects;
- no local Dispute/Hold/Payment truth appears.

### Exit Gate

- CL-04 Features 11–12 contracts are approved and available;
- Order settlement transition tests pass;
- Payment/Dispute/Hold contract tests pass;
- no direct provider or foreign repository mutation exists;
- reconciliation can safely retry missing Order effects.

---

# Phase 6 — Module Integration Proof

## 09 Cross-Module Contract Integration

### Objective

Prove Transaction / Order works with its direct neighboring owner interfaces without cross-domain repository assumptions.

### Observable Result

End-to-end Module contract journeys pass using real or contract-test owner implementations, including negative paths and dependency degradation.

### Cluster Build-Plan Link

Transaction / Order participation in **CL-04 Feature 13 — Cross-Cluster Contract Proof**.

### Dependencies

- Features 01–08;
- CL-04 Features 01–12 as needed for full Gig/Dispute journeys;
- dependency contract fixtures/real test adapters;
- real outbox/inbox/queue runner in integration environment.

### In Scope

Prove these boundaries:

- CustomerProfile → Order create/read;
- Offering → Order source;
- GigAssignment → Order source;
- Professional Eligibility → selected Order gate;
- Track → pricing snapshot and usage receipt;
- Consent → Agreement contextual proof;
- Media → OrderFile/document/signed access;
- Payment → payment/refund Order outcomes;
- Hold → payment/fulfillment/access denial;
- Order → Booking/Media/Digital/Video entitlement;
- Review/Dispute → disputed/refund settlement effect;
- Order events → Notification/Messaging/Payout/Review/Rewards consumers;
- Privacy → Transaction / Order executor.

### Out of Scope

- implementing neighboring source truth;
- replacing owner fixtures with direct DB manipulation;
- new product features or provider choices.

### Module-Owned Data

No ownership changes. Migrations discovered by contract proof require architecture review, not silent test-only workarounds.

### Public Interfaces

All public commands/queries/events from Module architecture Section 12 are contract-tested and versioned.

### Shared Operations Used

All canonical operations exercised by the workflows. No new shared operation may be introduced solely to make tests pass. Especially verify:

- auth/authority/customer actor;
- idempotency/concurrency;
- outbox/inbox;
- entitlement/consent/hold/readiness;
- Media access;
- audit/access audit;
- request context/telemetry;
- Privacy executor contract.

### Domain Logic

Run owner-boundary scenarios, including:

1. Offering source → Order → pricing snapshot.
2. accepted GigAssignment → exactly one Order.
3. agreement-required Order cannot enter payment until execution readiness passes.
4. Payment normalized success → exactly one paid effect.
5. Order entitlement → CL-05 delivery allow/deny.
6. completed Order → Review eligibility consumer receives correct facts.
7. dispute open/resolution → correct Order effects without direct Hold/Payment mutation.
8. Privacy target → local executor returns correct retained/anonymized/revoked result.

### Authorization / Compliance

Negative-path contract tests are mandatory:

- wrong CustomerProfile;
- wrong ProfessionalProfile;
- unauthorized admin/support contract access;
- active hold;
- invalid/expired entitlement;
- missing consent;
- private/non-ready Media;
- stale source/version;
- retention-restricted privacy operation.

### Database / Transaction Behavior

- use real Postgres transactions/constraints for integration tests where feasible;
- outbox/inbox uses real semantics;
- no test directly inserts neighboring internal records except through dedicated fixture builders that represent owner public contracts and do not become production repository coupling;
- verify query plans for primary Order/Agreement reads if dataset fixture is large enough.

### Events / Jobs

Use real outbox/inbox/queue runner. Simulate duplicate event, delayed event, dead-letter/retry, and out-of-order owner result where relevant. Prove consumer idempotency.

### Provider Integration

Payment provider itself may remain stubbed behind Payment owner; Transaction / Order receives normalized contract. Renderer/Media integrations use test adapters/real test environment according to their owning ports.

### UI / Admin Surface

Run Playwright for genuine Transaction / Order-owned surfaces if present:

- Offering/GigAssignment Order detail;
- agreement-required checkout/progress;
- private agreement access;
- participant fulfillment progress.

Do not add UI solely for integration proof.

### Failure Behavior

- dependency timeout → stable unavailable/retry result;
- duplicate event → one effect;
- stale DTO/source version → conflict;
- outbox/inbox failure → retry without source-truth corruption;
- dead-letter → visible operational state;
- owner denial → local command does not bypass it.

### Tests

- public contract tests for every direct owner;
- integration journeys listed above;
- E2E where UI exists;
- negative authorization/compliance cases;
- event ordering/replay;
- queue retry/dead-letter;
- no-cross-repository architecture test.

### Documentation Updates

If integration exposes an incomplete contract, update owner/public-interface docs and architecture through normal decision process; do not add a hidden repository dependency.

### Acceptance Criteria

- no Transaction / Order integration test needs neighboring internal Prisma repositories;
- all critical owner contracts have positive and negative tests;
- retry/dedupe/outbox paths are proven;
- Module emits/consumes provider-neutral DTOs only.

### Exit Gate

- all contract/integration/E2E suites pass;
- no unresolved direct-owner interface required by production remains implicit;
- event and job replay paths pass;
- architecture boundary static review finds no ownership leakage.

---

# Phase 7 — Privacy, Reconciliation, and Production Hardening

## 10 Privacy Executor, Reconciliation, Security, and Production Readiness

### Objective

Make Transaction / Order safe under privacy requests, retention constraints, provider/dependency outages, replay, concurrency, migration/backfill, and production operations.

### Observable Result

Privacy jobs can enumerate and execute approved Transaction / Order targets; operators can diagnose/reconcile stuck Order/Agreement effects; destructive changes are retention-safe; replay/concurrency/provider degradation tests pass.

### Cluster Build-Plan Link

Transaction / Order portion of **CL-04 Feature 14 — Security, Privacy, Reconciliation, and Production Readiness**.

### Dependencies

- Feature 09;
- approved retention rules for destructive behavior;
- Privacy target contract;
- production dependency/provider contracts;
- shared observability/queue/retry/audit/security primitives;
- migration/backfill tooling.

### In Scope

- `enumerateOrderPrivacyData`;
- `executeOrderPrivacyTarget`;
- anonymize/detach/revoke/retain behavior for local records under explicit instruction;
- Agreement access-grant revocation during privacy/security/lifecycle events;
- Order/payment/refund local-effect reconciliation through owner contracts;
- agreement Media/snapshot reconciliation;
- dead-letter/operator-safe retry diagnostics;
- indexes/query plans;
- migration/backfill validation and rollback strategy;
- security review of auth/authority/step-up integration;
- audit/access-audit completeness;
- telemetry redaction;
- load/performance tests on hot queries;
- production-like event replay.

### Out of Scope

- creating PrivacyRequest/DataErasure jobs;
- inventing retention durations;
- direct provider repair by SQL/Stripe API;
- new pricing models;
- new Agreement provider choices;
- new dispute policy;
- new product features.

### Module-Owned Data

All Transaction / Order-owned records may be enumerated. Destructive changes are limited to the disposition supplied by Privacy and approved retention policy.

### Public Interfaces

- `enumerateOrderPrivacyData`;
- `executeOrderPrivacyTarget`;
- owner-safe reconciliation commands/diagnostic queries;
- health-check contribution for Transaction / Order dependencies;
- no generic direct-SQL repair API.

### Shared Operations Used

- **canonical privacy target result contract** — Privacy owns orchestration; local executor returns erased/anonymized/retained/revoked/etc.
- **`revokeTemporaryAccessGrant`** — revoke AgreementAccessGrant when instructed.
- **`enqueueReliableJob` / `executeRetryWithBackoff`** — backfills/reconciliation/privacy local work.
- **`deduplicateDomainEvent` / `executeIdempotentCommand`** — replay-safe repair.
- **`createRequestContext`, `writeStructuredLog`, `sanitizeTelemetryMetadata`, `captureException`, `emitMetric`, `recordIntegrationFailure`, `recordQueueTelemetry`, `checkServiceHealth`** — production ops.
- **`appendAuditEvent` / `recordSensitiveAccess`** — privileged repair/privacy/access evidence.
- **`calculateChecksum`** — integrity re-verification where required.
- **`requireStepUpForSensitiveAction`** only for actions specified by root security policy; no local MFA flags.

### Domain Logic

Privacy executor inventory must cover:

- Order participant/text/provider-reference fields;
- OrderEvent;
- OrderFile context;
- Agreement;
- AgreementElectronicConsent;
- AgreementSignature metadata;
- AgreementDocumentSnapshot;
- AgreementEvent;
- AgreementAccessGrant.

For each target, execute only the requested disposition. If a retention exemption applies, return `retained` with exemption reference and do not destroy proof.

Reconciliation may:

- detect accepted GigAssignment missing Order and call idempotent creation through public source contract;
- detect Payment-confirmed/refund result missing local Order effect through Payment reconciliation facts and invoke the correct idempotent Order command;
- detect Agreement Media object/snapshot mismatch and safely repair/retry according to owner contracts;
- verify Agreement hash proof;
- recover dead-lettered local jobs/outbox effects without bypassing current aggregate version.

Reconciliation must never overwrite newer domain truth.

### Authorization / Compliance

- Privacy/system executor authenticates through trusted internal context;
- retained contract/payment/tax/dispute/fraud/signature proof is preserved when instructed;
- admin/operator diagnostics expose safe metadata only;
- privileged manual repair requires explicit authority, audit, and step-up if root policy says so;
- Search/public deindexing, Media deletion, and provider deletion are requested through owners rather than performed directly;
- telemetry is allowlisted/redacted.

### Database / Transaction Behavior

- privacy/reconciliation commands are idempotent;
- cursor-based backfills are resumable;
- batch operations use bounded transactions and current-version checks;
- destructive migrations require data audit, backfill, validation, rollback plan;
- verify indexes for Order by status/source/buyer/seller/payment refs and Agreement by status/template/hash/archive/expiry according to real queries;
- no direct SQL product repair endpoint.

### Events / Jobs

- privacy local executor jobs as invoked by Privacy orchestration;
- reconciliation/backfill workers with cursor, rate limit, retry, dead-letter, correlation;
- grant expiration/integrity verification workers;
- operational metrics for retries, conflicts, dead letters, Order creation/payment-effect lag, Agreement finalization/access failures;
- domain event emitted only when business truth actually changes.

### Provider Integration

No direct Payment provider integration. Renderer/Media adapters retain their existing ports. Reconciliation with providers is performed by provider-owning Modules; Transaction / Order consumes normalized discrepancy/result contracts.

### UI / Admin Surface

Minimal operator diagnostics may show:

- aggregate ID/status/version;
- stuck workflow/job category;
- safe dependency/error category;
- correlation/request ID;
- retry/manual-review action through owner command.

Never show full contracts, signatures, private URLs, tokens, payment secrets, or raw provider payload.

### Failure Behavior

- retention exemption blocks destructive action → `retained`, not failure;
- poison item → dead-letter/manual review, not infinite retry;
- stale reconciliation target → skip/re-evaluate, never overwrite newer state;
- provider owner unavailable → degraded/retry, never fabricate success;
- privacy target unsupported because retention policy unresolved → explicit blocker;
- partial Media/provider deletion → report retryable/terminal result through privacy contract;
- audit/telemetry failure follows root policy but does not silently corrupt source truth.

### Tests

- privacy inventory completeness;
- anonymize/detach/revoke/retain fixtures;
- retention exemption enforcement;
- idempotent privacy replay;
- reconciliation idempotency;
- stale-version repair protection;
- backfill resume after interruption;
- Agreement hash reconciliation;
- grant expiration/revocation;
- security/authorization review tests;
- step-up integration where required;
- telemetry secret/redaction fixtures;
- audit/access-audit completeness;
- query plan/performance tests;
- destructive migration dry-run/backfill/rollback tests;
- production-like event/webhook normalized-result replay;
- full critical Playwright journeys.

### Documentation Updates

- update retention rules only after approved legal/product decision;
- update architecture for any changed provider/reference or privacy disposition semantics;
- update progress tracker with migration/backfill state and remaining operational risks.

### Acceptance Criteria

- Privacy can fully enumerate Transaction / Order-owned data through a supported executor;
- destructive actions respect retention exemptions;
- provider/dependency outage does not fabricate Order/Agreement success;
- reconciliation is idempotent and version-safe;
- operator can identify and remediate stuck owner-local workflows through supported commands;
- no high-severity ownership/security/privacy finding remains;
- telemetry contains no prohibited sensitive payloads.

### Exit Gate

Before declaring the Module production-ready:

- all unit/contract/integration/concurrency/privacy/security/E2E suites pass;
- full CL-04 Feature 14 exit gate passes for Transaction / Order;
- migration/backfill/rollback plans are verified;
- privacy inventory is complete;
- provider degradation/replay/reconciliation are demonstrated safely;
- no unresolved retention decision is bypassed by destructive implementation;
- final architecture/static review confirms no neighboring source truth was absorbed.

---

# Module Integration Phase

Feature 09 is the explicit Module integration phase. It proves Transaction / Order works through public owner contracts rather than shared-database convenience.

Minimum proof matrix:

```text
Customer / Buyer Profile → buyer actor facts
Marketplace Supply → Offering checkout source
Gig / Demand → accepted assignment checkout source
Professional Eligibility → selected seller readiness decisions
Track Subscription & Entitlement → fee/commission decisions + usage receipts
Consent & Disclosure → generic consent proof
Admin Review / Compliance Hold → reusable stop-sign decisions
Payment / Payout / Tax → provider-neutral payment/refund outcomes
Media / File Access → ready asset + private signed transport
Transaction / Order → authoritative Order/Agreement truth
Booking / Digital Goods / Video ← Order entitlement decision
Review / Dispute ↔ dispute/settlement transaction effects
Notification / Messaging ← committed domain facts
Audit / Observability ← safe evidence/telemetry
Privacy / Data Erasure → target executor instructions
```

Contract tests must exercise both success and denial/degradation paths.

---

# Module Hardening Phase

Feature 10 covers only Transaction / Order hardening:

- Order source and transition races;
- pricing-freeze race/replay;
- payment/refund result replay/conflicts;
- Agreement signature/finalization races;
- document integrity/hash mismatch;
- AgreementAccessGrant use/revoke/expire races;
- dependency/provider degradation;
- owner-safe reconciliation;
- privacy/retention execution;
- audit/access-audit completeness;
- telemetry safety;
- migration/backfill behavior;
- hot-query performance.

It must not be used to postpone unimplemented core lifecycle or agreement behavior.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Order Source-of-Truth Foundation | 01–02 |
| 2 | Commercial Snapshot | 03 |
| 3 | Agreement Execution and Contract Proof | 04–05 |
| 4 | Payment and Fulfillment Transaction State | 06–07 |
| 5 | Settlement Participation After Review / Dispute | 08 |
| 6 | Module Integration Proof | 09 |
| 7 | Privacy, Reconciliation, and Production Hardening | 10 |

**Total numbered Module features: 10**

### CL-04 build-plan alignment

| Module feature | CL-04 milestone |
| --- | --- |
| 01–02 | Feature 04 — Order Aggregate and Source Contracts |
| 03 | Feature 05 — Commercial Pricing and Entitlement Snapshot |
| 04 | Feature 06 — Agreement Template and Order-Specific Agreement |
| 05 | Feature 07 — Agreement Document Finalization and Secure Access |
| 06 | Feature 08 — Payment Initiation and Verified Order Payment |
| 07 | Feature 09 — Order Fulfillment, Delivery Entitlement, and Completion |
| 08 | Transaction / Order portion of Feature 12 — Dispute Adjudication, Refund/Release, and Closure |
| 09 | Feature 13 — Cross-Cluster Contract Proof |
| 10 | Feature 14 — Security, Privacy, Reconciliation, and Production Readiness |

This mapping is binding for sequence. Feature 08 cannot leap ahead of CL-04 Review / Dispute Features 10–12 merely because Transaction / Order code is ready.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and architecture.
2. Read root code standards.
3. Read Canonical Shared Operations Architecture/Registry.
4. Read CL-04 architecture and build plan.
5. Read Transaction / Order `module-architecture.md` and this plan.
6. Read public-interface sections for direct dependencies used by the feature.
7. Confirm the prior Module exit gate and the corresponding CL-04 sequencing gate.
8. Confirm every unresolved decision required by the feature has an approved ruling.
9. Produce the Required Feature Implementation Specification below.
10. Implement only the numbered feature.
11. Run required typecheck/lint/format/unit/contract/integration/migration/build checks applicable to that feature.
12. Verify owner contracts and failure paths.
13. Update progress tracker.
14. Update architecture only when a binding decision legitimately changed and was approved.
15. Record unresolved risks/deferred work.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise specification containing:

- **Objective** — one result only.
- **Observable result** — what can be seen/tested after implementation.
- **Cluster build-plan link** — exact CL-04 feature/milestone.
- **Dependencies** — prior Module features, owner interfaces, shared operations, schemas/migrations, providers.
- **In scope** — exact work allowed.
- **Out of scope** — neighboring responsibilities explicitly prohibited.
- **Owned data affected** — models/enums/events/snapshots.
- **Public contracts** — commands, queries, events, executor changes.
- **Shared operations consumed** — canonical names/owners/invocation/local policy/prohibited duplicate.
- **Permissions/compliance** — actor, authority, CustomerProfile/ProfessionalProfile context, consent, entitlement, readiness, hold, step-up, privacy.
- **Primary workflow** — ordered command/query path.
- **Provider integration** — only if this Module owns/uses a port in the feature.
- **Jobs/events** — outbox/inbox/queue/retries/dead-letter/correlation.
- **Idempotency/concurrency** — semantic key, aggregate/lock key, transaction boundary, replay result.
- **Error behavior** — stable reason/error categories and dependency degradation.
- **Tests** — exact test categories and critical cases.
- **Acceptance criteria** — observable requirements.
- **Documentation updates** — architecture/contracts/progress changes if a deferred decision was legitimately settled.

Do not generate all feature specifications in advance. The numbered feature entry in this plan is the implementation boundary, not a substitute for the just-in-time specification.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- Feature completed;
- CL-04 milestone supported;
- Files added;
- Files changed;
- Database changes;
- Migrations;
- Dependencies added;
- Module public interfaces added/changed;
- Shared operations reused;
- Prohibited duplicates checked/avoided;
- Events/outbox/inbox/jobs added;
- Provider adapter changes;
- Tests added/changed;
- Commands run;
- Typecheck/lint/format/build result;
- Database/migration verification;
- Manual/contract/E2E verification;
- Documentation updated;
- Assumptions;
- Approved architecture decisions consumed;
- Known failures;
- Remaining risks;
- Deferred work;
- Exit-gate result: **PASS / BLOCKED / FAIL**;
- If blocked: exact unresolved architecture decision or external dependency.

A feature with a failed or blocked exit gate is not complete and must not be represented as complete in the progress tracker.

---

# Final Quality Check

Before treating these Module files as implementation context, verify:

1. Order and Agreement source truth have exactly one owner: Transaction / Order.
2. No Gig/Offering/Track/Payment/Booking/Review/Dispute/Hold/Media/Privacy truth has been absorbed.
3. Track current policy remains external; historical transaction effects are snapshotted only on Order.
4. CustomerProfile and ProfessionalProfile identity boundaries are explicit.
5. Shared operations are consumed rather than recreated.
6. Shared mechanism/separate truth rules are explicit for events, grants, hashing, provider dedupe, state-machine plumbing, workflow runners, and queues.
7. Public commands/queries are stable enough to replace cross-Module direct Prisma reads.
8. Payment providers remain behind Payment / Payout / Tax.
9. Agreement document storage/signed URLs remain behind Media / File Access.
10. Audit, OrderEvent, AgreementEvent, and observability remain distinct.
11. Privacy orchestration remains Privacy-owned.
12. Search remains a projection and is not required for private Order truth.
13. Each numbered feature maps to the CL-04 build sequence.
14. Every numbered feature contains tests, acceptance criteria, and an exit gate.
15. Features stop at unresolved decisions rather than inventing architecture.
16. A coding agent can implement the plan without creating a generic commerce service or provider-owned truth inside this Module.
