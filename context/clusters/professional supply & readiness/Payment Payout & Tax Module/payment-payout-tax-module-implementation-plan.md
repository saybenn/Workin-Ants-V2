# Payment Payout & Tax Module Implementation Plan

> **Module ID:** `payment_payout_tax`  
> **Canonical registry name:** Payment / Payout / Tax Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Architecture dependency:** `context/clusters/professional supply & readiness/Payment Payout & Tax Module/payment-payout-tax-module-architecture.md`\
> **Cluster plan dependency:** `context/clusters/professional supply & readiness/professional-supply-readiness-build-plan.md`\
> **Plan status:** Ordered Module implementation plan; subordinate to Cluster sequencing and architecture

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

## Core Principle

Implement Payment / Payout / Tax through narrow, verifiable vertical slices:

```text
public / observable financial behavior
→ validated command/query
→ authenticated/system actor + authority + step-up where required
→ Payment-owned policy
→ authoritative Payment write/read
→ canonical Shared Operation calls
→ provider / owner-command / event / audit / notification effects
→ tests
→ exit gate
```

A slice does not need a new UI to be real. For this Module, an observable result may be a provider-neutral onboarding contract, SH-019 decision, durable financial ledger effect, payout transfer, sales-tax proof, Order handoff, tax-reporting record, reconciliation worker, Privacy executor, or restricted financial setup/admin surface.

This Module plan is intentionally narrower than the CL-03 build plan. It explains **how Payment's portion** of CL-03 Features 07, 09, 10, 10A, 11, 12, and 13 is implemented. It does not independently reorder Marketplace, Professional Eligibility, Trust, Healthcare, or neighboring Cluster work.

---

## Build Rules

1. Follow root Workin Ants architecture/code/security/data standards, Canonical Shared Operations, CL-03 architecture, and the Module architecture.
2. Implement one numbered Module feature at a time. The next feature does not begin until the current feature's exit gate passes or is explicitly blocked and re-planned.
3. This Module owns only the truth declared in `context/clusters/professional supply & readiness/Payment Payout & Tax Module/payment-payout-tax-module-architecture.md`.
4. Consume ProfessionalProfile, Order, Dispute, Hold, Track, Prize, Reward, Digital Goods, Media, Privacy, Audit, Notification, and Ops through approved public contracts/events.
5. Never write `Order`, `RefundStatus`, `OrderEvent`, `ProfessionalProfile`, Dispute, ComplianceHold, Prize, Reward, Search, Audit, Notification, Privacy, or Media source tables directly from Payment implementation.
6. Reuse canonical Shared Operations by permanent `SH-###` identifier; do not create local aliases with independent semantics.
7. Proposed Shared Operations may guide types but cannot become new platform-wide dependencies until approved. SH-120 remains unresolved and must not be silently built here.
8. Validate every server, worker, webhook, provider, and cross-Module payload at runtime. TypeScript alone is not a trust-boundary validator.
9. Every protected mutation/read uses SH-001/002; sensitive financial operations use SH-014/030 as specified.
10. Every lifecycle mutation validates expected current state and uses DB-safe concurrency/idempotency.
11. Every provider is behind a provider-neutral Payment port; provider SDK types stop at the adapter boundary.
12. Every provider callback is signature-verified, owner-deduplicated, translated, transition-validated, and reconciled.
13. Client success redirects never establish payment, KYC, payout, or tax truth.
14. Every money amount uses integer minor units with explicit currency. Do not use floating-point arithmetic for business money.
15. Processor-held funds remain processor-held. Do not create wallet/escrow/stored-value truth.
16. Professional balance history is append-only. Correction/reversal is a new effect, not mutation of prior economic history.
17. External/source events are effectively-once: source event dedupe + DB uniqueness/transaction boundaries prevent duplicate ledger/tax/transfer effects.
18. Jobs are durable, retry-classified, observable, and dead-letter visible through shared queue/Ops mechanisms.
19. Generic Audit/Access/IntegrationFailure/QueueJob records never replace Payment business/provider-event truth.
20. Privacy remains Privacy-owned. Payment implements only owner-specific enumerate/execute/export/retention/provider-delete behavior.
21. Tax reporting/legal retention/rules are legal-gated. Unsupported or unresolved paths remain disabled or explicit review/manual paths.
22. Sales tax uses approved provider-backed calculation; no custom rate/jurisdiction engine is invented.
23. Refund/partial-refund/tax reversal paths are limited to schema/provider semantics proven by tests; unsupported allocation fails explicitly.
24. Every feature contains exact tests and a concrete exit gate.
25. If implementation reveals a binding ownership/lifecycle/provider/data-model decision, update architecture first or in the same change; do not settle it only in code comments.

---

## Preconditions

### Hard platform dependencies

These must exist, or the feature must have a stable test-double contract without locally rebuilding them:

- Prisma/PostgreSQL through the root data layer;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-011/012/013 ComplianceHold interfaces for hold-sensitive work;
- SH-014 step-up before sensitive financial operations;
- SH-029/030 Audit/sensitive-access interfaces;
- SH-034/037/038 telemetry/Ops interfaces;
- SH-041 Notification request interface before notification-dependent behavior is enabled;
- SH-044 command idempotency;
- SH-045 consumer event inbox/dedupe before source-event projections are enabled;
- SH-046 transactional outbox before downstream correctness relies on Payment events;
- SH-047/048 durable jobs/retry/dead-letter before async provider/reconciliation/reporting workers are production-enabled;
- SH-051/052/053 and SH-056 or root-approved DB concurrency equivalents;
- SH-059/060/061/062 provider callback/reconciliation mechanisms;
- SH-095/096/097 Privacy target protocol before production privacy-compliance completion is claimed.

If a shared dependency is unavailable, create only the local **port/contract test double** needed to implement Payment behavior. Do not create a Payment-owned replacement infrastructure service.

### Hard owner-interface dependencies

- **Professional Eligibility:** `getProfessionalProfileContext` or approved narrow owner-facts equivalent.
- **Transaction / Order:** stable payment/pricing/participant snapshot query and verified payment/refund outcome commands before Features 06–07.
- **Review / Dispute:** narrow approved money-consequence/refund/hold outcome contract before dispute-driven financial effects are enabled.
- **Admin Review / Compliance Hold:** hold query/command interfaces before payout production use.
- **Identity & Access / Role:** sensitive finance authority and step-up.

### Dependencies that may initially be stubbed behind stable contracts

- Notification delivery;
- Prize/Reward SH-118 source producers;
- future non-Stripe KYC/tax/reporting providers;
- Digital Goods item/tax-code context;
- Privacy orchestration while Payment executor tests are built;
- Admin/Ops UI surfaces.

### Provider prerequisites

- Stripe/Stripe Connect/Stripe Tax credentials/configuration in root secret/config infrastructure for enabled production paths.
- Webhook endpoint secret and raw-body signature support.
- Provider test/sandbox environment.
- Provider-neutral ports may be built before every live provider path is enabled.
- Future Avalara/other KYC/tax/reporting providers remain adapter work only after explicit selection.

### Architecture blockers to review before each feature

The Module architecture UD-01 through UD-23 must be checked. Especially:

- UD-04/05 before production webhook ingestion assumptions;
- UD-06/07 before current KYC/tax profile and payout-account selection are generalized;
- UD-09/10/11/12 before balance/payout production;
- UD-13 before expanding payment/chargeback history beyond current schema;
- UD-14/15/20 before automated tax reporting;
- UD-16/17/18/19 before complex sales-tax finalization/refunds;
- UD-03 before destructive Privacy retention behavior.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 — Payment Module Contracts, Validation, and Data-Ownership Baseline

### Objective

Establish the Module's executable boundary—public DTOs, owner repository limits, runtime validation, money/error conventions, lifecycle policy shells, and provider-neutral ports—without performing live provider or money-moving effects.

### Observable Result

- Payment public commands/queries can be imported/tested through stable contracts without exposing Prisma or Stripe SDK types.
- Every planned input boundary has runtime schemas.
- Repositories can access Payment-owned models and reject/avoid direct foreign-domain repository patterns.
- SH-019 response shape and reason namespace are versioned locally enough to support Feature 03.
- Provider ports exist with test doubles and normalized result envelopes.
- Architecture gaps discovered from the current Prisma schema are recorded rather than silently patched.

### Cluster Build-Plan Link

Supports **CL-03 Feature 07 — KYC, Tax Profile, Payout Account, and Financial Readiness** by creating the Payment-owned contract/data foundation. It does not start Cluster Feature 09 or 10 behavior early.

### Dependencies

- Current Prisma schema and migrations.
- Root module/code folder conventions.
- SH-001/002/014/044 contract availability or test doubles.
- Module architecture approved enough to identify owned records and unresolved items.

### In Scope

- Module folder skeleton from architecture Section 6, adapted to actual repository conventions.
- Zod schemas for public command/query inputs and canonical owner/provider result envelopes.
- Payment `Money`/minor-unit validation using root money utilities if they exist; otherwise minimal local value validation without creating a global money framework.
- Public contract types for:
  - SH-019 financial readiness;
  - financial setup summary;
  - payout request/transfer result;
  - Order payment/tax provider result;
  - SH-118 taxable-value intake;
  - Payment Privacy executor.
- Provider-neutral port interfaces for payment, payout, KYC, tax profile, sales tax, tax reporting.
- Repository interfaces/implementations limited to Payment-owned tables.
- Lifecycle transition-policy interfaces without enabling unsupported edges.
- Stable error/result categories and provider-error translation contract.
- Test fixtures/builders with redacted fake financial data.
- Documentation of Prisma gaps that will matter in later features.

### Out of Scope

- live Stripe calls/webhooks;
- KYC/tax/account onboarding writes;
- ledger writes;
- payout requests/transfers;
- sales-tax calculation;
- Order payment/refund execution;
- tax reporting;
- adding speculative `PaymentAttempt`, `Chargeback`, wallet, escrow, or tax-rule models;
- resolving Cluster U-01 timing for publication/profile/Gig actions.

### Module-Owned Data

No new business rows are required. Existing owned models/enums are mapped into repository/domain types. Any schema migration proposed merely for cleanup is deferred unless it is required to enforce an invariant in a later numbered feature.

`TaxReportingSubmissionStatus` and `TaxReportingRecipientStatus` may be treated as Payment-owned in code **only under PT-01**; record the context correction when approved.

### Public Interfaces

Introduce/freeze initial versions of:

- `FinancialReadinessRequest/Result` for SH-019;
- `FinancialSetupSummary`;
- `PayoutRequestCommand/Result` shell;
- `PaymentRailRequest/Result`;
- `SalesTaxCalculationRequest/Result`;
- `ReportTaxableValueRequest/Result` for SH-118;
- `PaymentPrivacyTarget`/execution result adapter to canonical Privacy protocol;
- provider port interfaces and normalized provider result envelope.

No endpoint/server action is considered authoritative merely because a type exists; delivery wiring happens in the owning feature.

### Shared Operations Used

- **SH-001 — Identity & Access:** define actor-context input dependency. Invocation in later delivery handlers. Local policy: Payment action/target. **Do not build:** `financialCurrentUser`.
- **SH-002 — Role / Authority:** define typed action/resource fact contract. **Do not build:** Payment RBAC engine.
- **SH-014 — Identity & Access:** define step-up requirement/result dependency for sensitive commands. **Do not build:** payout MFA.
- **SH-044 — platform idempotency:** define idempotency-key/fingerprint contract for future commands. **Do not build:** Payment idempotency table.
- **SH-053 — shared lifecycle mechanism:** define how Payment-owned transition policy plugs into shared state-machine mechanics; exact edges remain local. **Do not build:** generic Payment status framework.
- **SH-078 — shared minimization:** establish provider outbound-payload adapter point. **Do not build:** raw object serializer.

### Domain Logic

- Define integer minor-unit and currency invariants.
- Define Payment status/result namespaces separate from provider status strings.
- Define SH-019 dimensions as independent facts, not one boolean.
- Define provider error classes: validation, authorization, conflict, requires input, review, retryable provider failure, terminal provider failure, unsupported state, unavailable.
- Define source ownership rules in code-level contracts: Order IDs/versions and ProfessionalProfile IDs are opaque external references resolved through public interfaces.
- Do not create `setStatus` methods; expose transition-specific domain commands/guards.

### Authorization / Compliance

- Contract types support actor/system context but do not hardcode role interpretation.
- Sensitive response types exclude raw bank/tax/KYC/provider payloads.
- SH-019 contract can represent `step_up_required`, `unavailable`, and multiple blocking dimensions.
- `KycVerification` language is payout/financial compliance only; no TrustBadge/VerificationCheck coupling.

### Database / Transaction Behavior

- Repositories access only Payment-owned models.
- Add integration tests that fail if the Payment repository layer imports/queries known foreign models directly, using architectural test conventions if the root project supports them.
- Confirm existing DB constraints: ProcessedStripeEvent PK, PayoutTransfer unique idempotency key, PayoutAccount provider ID uniqueness, TaxYear summary unique key.
- Record missing invariants (ledger source-effect, tax reporting recipient uniqueness, sales-tax finalization selection) as deferred feature blockers, not ad-hoc app checks presented as final safety.

### Events / Jobs

No business event/job required. Event and job contracts may be typed but no source events are emitted solely for contract setup.

### Provider Integration

Provider ports/test doubles only. No live SDK call, webhook, credentials, or provider resource creation.

### UI / Admin Surface

None required. Do not invent a Payment dashboard for this feature.

### Failure Behavior

- Invalid input fixtures produce typed validation errors.
- Unsupported provider/result status is explicit and cannot map to success.
- Cross-domain repository usage discovered during implementation is treated as architecture violation, not an accepted shortcut.
- Missing root shared operation is represented by a port/test double and documented, never replaced by local infrastructure.

### Tests

- unit: money/currency validation, reason-code/decision schemas, provider result validation;
- contract: SH-019/SH-118/provider ports no raw SDK types;
- architectural: repositories limited to Payment-owned records;
- security: DTOs reject raw secret/tax/bank/provider fields where allowlists apply;
- typecheck/lint/build required by root standards.

### Documentation Updates

- Update Module progress tracker.
- If PT-01 is approved, update registry/context ownership for tax-reporting status enums.
- Record any new unresolved schema gaps in Module architecture before relying on them.

### Acceptance Criteria

1. Public Payment contracts compile and validate at runtime.
2. No public contract exports Prisma model or provider SDK object as its API.
3. SH-019 supports separate dimensions and stable safe reason codes.
4. Provider ports are capability-specific and testable with fakes.
5. Repository code is owner-limited; no default cross-domain Prisma repository exists.
6. No live external side effect or speculative business model was added.

### Exit Gate

Feature 01 passes only when typecheck/lint/unit/contract/architecture tests pass and a coding agent can implement onboarding without inventing Payment ownership or provider DTO semantics.

---

## 02 — Verified Stripe Ingress, Provider Translation, and Reconciliation Shell

### Objective

Establish the safe Stripe/Stripe Connect/Stripe Tax ingress and adapter shell—signature verification, Payment-owned event dedupe, normalized translation, idempotent handler dispatch, and reconciliation—without allowing a webhook to become Order or Payment truth by itself.

### Observable Result

- A signed supported Stripe test webhook reaches a Payment handler only after SH-059 verification.
- The first delivery can claim `ProcessedStripeEvent`; a replay cannot repeat the handler effect.
- Provider event/type/status translation returns canonical Payment values or explicit unsupported state.
- A reconciliation runner can query a provider test double/sandbox and compare current provider state with an owner-provided Payment target without direct foreign writes.
- Invalid signature, unknown status, replay, and transient provider failures are observable and safe.

### Cluster Build-Plan Link

Supports **CL-03 Feature 07** provider foundation. The same verified/deduped adapter shell is later reused by Module Features 03, 05, and 07, matching Cluster Features 07, 09, and 10.

### Dependencies

- Module Feature 01.
- SH-059/060/061/062.
- SH-034/037/038 telemetry/Ops.
- SH-044 for replay-prone commands.
- SH-046/047/048 before async provider processing/reconciliation is production-enabled.
- Stripe sandbox/test configuration.
- **UD-04 must receive an explicit feature ruling before production callback side effects are enabled.**
- UD-05 must be respected: Payment must not claim Track/Billing Stripe truth by assumption.

### In Scope

- Stripe adapter boundary and runtime event schemas for only the event families needed by approved Payment features.
- Raw-body signature verification integration through SH-059.
- SH-060 event claim backed by `ProcessedStripeEvent` for Payment-owned Stripe events.
- Mapping registry/version for Payment KYC/account/payout/payment/tax statuses as applicable.
- Unknown event/status classification.
- Provider result envelope with safe references/correlation.
- Shared retry classification integration.
- Reconciliation runner shell with dry-run capability.
- Event routing limited to Payment-owned handlers; other Stripe-using Modules require separate explicit routing/ownership.
- Redacted operational telemetry.

### Out of Scope

- enabling every possible Stripe event;
- Track subscription webhook ownership;
- KYC/tax/payout business transitions beyond test handler seams;
- Order writes;
- payment-attempt/chargeback models not present in architecture;
- live payout execution;
- custom queue/retry framework.

### Module-Owned Data

- `ProcessedStripeEvent`.
- No other business record must be mutated merely to prove ingress; handler integration is completed in later features.

### Public Interfaces

Provider-facing/internal interfaces:

- `handleStripeWebhook(rawBody, headers, context)` delivery adapter;
- provider-event dispatch contract;
- `StripePaymentAdapter` / capability port implementations as needed;
- `reconcileProviderTarget(...)` internal worker contract.

No raw Stripe event object is a public Module interface.

### Shared Operations Used

- **SH-059 — shared integration security:** verify raw body before parse/use. Local policy: Payment endpoint/secret/accepted provider. **Do not build:** bespoke signature utility.
- **SH-060 — provider owner + shared claim primitive:** claim Payment Stripe event once in `ProcessedStripeEvent`. Local policy: which events belong to Payment and when claim commits. **Do not build:** `WebhookLog`/Audit dedupe.
- **SH-061 — provider-adapter contract:** translate Stripe values to Payment enums/results with mapping version. **Do not build:** global ProviderStatus.
- **SH-062 — owner reconciliation:** compare provider and Payment state; safe repair uses Payment commands/foreign owner commands later. **Do not build:** global Stripe sync that patches tables.
- **SH-034 — telemetry sanitization:** redact payload metadata. **Do not build:** raw webhook logger.
- **SH-037 — Observability:** record integration failure without replacing business status.
- **SH-038 — queue telemetry:** instrument reconciliation/async processing.
- **SH-047/048 — shared jobs/retry:** durable retry of safe transient work. **Do not build:** `stripeRetryQueue`.

### Domain Logic

- Provider event is only an input fact after signature verification.
- Payment accepts only an allowlisted event family relevant to its ports.
- Unknown event type may be safely ignored only if explicitly classified as irrelevant; unknown status for a relevant event is unsupported/review, not success.
- Mapping is versioned/tested.
- Provider occurrence time and receipt time are distinct.
- A Payment-local provider callback does not authorize Order transition until a later Payment handler validates the relevant Order/provider result and invokes the Order owner contract.

### Authorization / Compliance

Webhook uses provider-system authentication, not user session authorization. Admin-triggered reconciliation requires SH-001/002 and SH-029 if root policy marks it auditable. Provider payloads are minimized/redacted before logs.

### Database / Transaction Behavior

- `ProcessedStripeEvent.eventId` is the DB uniqueness boundary.
- Feature specification must settle UD-04 with one of the approved-safe patterns. Preferred pattern: claim and Payment-local owner write/outbox commit atomically for synchronous handler effects. If event edge durably enqueues before business handling, the durable work/claim recovery semantics must be explicit rather than losing a claimed event.
- Replay returns duplicate/no-op without running side-effect handler twice.
- Do not mark a foreign owner effect “complete” just because local claim exists; cross-owner commands are idempotent + reconciled.

### Events / Jobs

- Reconciliation job uses SH-047/048/038.
- No domain event is emitted for “webhook received” alone. Domain events occur only when a Payment-owned fact changes in later features.
- Dead-letter exposes provider event/correlation IDs only, not raw payload.

### Provider Integration

Stripe sandbox/test mode. Credentials via root secret infrastructure. Adapter methods accept/return canonical contracts from Feature 01.

### UI / Admin Surface

Optional restricted diagnostic trigger/view only if existing root Ops/admin shell has a place for it. No raw webhook browser is required or permitted by default.

### Failure Behavior

- invalid signature → reject, no claim/no side effect;
- malformed payload → validation rejection + safe telemetry;
- duplicate event → no repeated handler;
- unknown relevant status → explicit unsupported/manual review/ops;
- transient provider query → retryable;
- terminal provider rejection → no blind retry;
- claimed-but-unapplied event under an unresolved recovery pattern → production webhook remains disabled until UD-04 is resolved.

### Tests

- signature valid/invalid/timestamp/replay fixtures;
- concurrent duplicate event claim;
- event routing ownership tests, including a non-Payment Stripe event not being silently absorbed;
- status mapping/version fixtures;
- unknown event/status tests;
- telemetry redaction tests;
- reconciliation dry-run and retry classification;
- provider adapter contract tests with no SDK leakage;
- transaction/recovery tests for the approved UD-04 pattern.

### Documentation Updates

- Record the approved UD-04 claim/recovery ruling in Module architecture.
- If a cross-Module Stripe router is approved, record UD-05 ownership/routing without transferring provider ledgers.
- Document enabled Payment event families and mapping version.

### Acceptance Criteria

1. No unverified callback reaches a Payment handler.
2. Replayed Payment event cannot repeat a side effect.
3. Unknown provider status cannot become a success state.
4. Payment event routing is explicit and does not steal Track/other Module truth.
5. Reconciliation is dry-run capable and owner-command oriented.
6. Sensitive provider payload is absent from logs/audit/queue metadata.

### Exit Gate

Feature 02 passes when provider contract/signature/dedupe/mapping/reconciliation tests pass and either (a) UD-04 has an approved production-safe claim/recovery design, or (b) production callback side effects remain feature-gated off with the limitation documented. Feature 03 cannot claim live callback completion until (a) is true.

---

# Phase 2 — Financial Onboarding and Readiness

## 03 — KYC, Tax Profile, Payout Account, and SH-019 Financial Readiness

### Objective

Implement the CL-03 financial onboarding slice: a Professional can start/resume provider-backed KYC, tax-profile, and payout-account setup; Payment persists canonical states; and consumers receive dimensioned SH-019 financial readiness without reading provider/profile compatibility fields.

### Observable Result

- Authorized professional can initiate/resume KYC, tax-profile, and payout-account onboarding through provider-neutral commands.
- Safe provider-hosted continuation/session data can be returned to the authorized client.
- Provider callbacks/reconciliation update Payment canonical records idempotently.
- Provider requirements are captured in safe `ProviderRequirementSnapshot` records where useful.
- Professional can view a safe financial setup summary.
- SH-019 returns separate KYC, tax-profile, payout-account, restriction, and applicable balance/provider dimensions with safe reason codes.
- Sensitive setup/tax/account views enforce step-up and sensitive-access proof.

### Cluster Build-Plan Link

Implements Payment's portion of **CL-03 Feature 07 — KYC, Tax Profile, Payout Account, and Financial Readiness**. It must satisfy that Cluster feature's boundary before Module Feature 04 begins production balance/payout work.

### Dependencies

- Module Features 01–02.
- Professional Eligibility owner-facts/profile context.
- SH-001/002/014/011/019/030/044/046/055/059/060/061/062/063/078.
- Audit/Observability and Notification contracts.
- Approved Stripe/Connect/KYC/tax-profile provider paths.
- UD-04 production provider claim/recovery resolved for enabled callback path.
- UD-06 current KYC/TaxProfile selection policy must be constrained/approved for this feature.
- UD-07 payout-account selection can remain unresolved if feature only onboards and shows explicit accounts; payout selection is deferred to Feature 05.

### In Scope

- KYC onboarding/start/resume/status.
- Tax profile collection/start/resume/status and provider TaxDocument references.
- Payout account onboarding/status.
- Provider callback/reconciliation handlers for the above.
- Safe provider requirement snapshot capture.
- SH-019 initial dimension logic for setup/readiness actions.
- Safe financial setup summary query.
- Step-up and AccessAuditLog request for sensitive views/actions.
- Requires-input/restricted notification requests as approved.
- Expiry/refresh hooks only where semantics are established.

### Out of Scope

- balance ledger;
- payout request/transfer;
- Order payment/refund state;
- sales-tax calculation;
- tax-year reporting/filing;
- deciding whether financial readiness gates ProfessionalProfile activation/Offering publication/Gig response (UD-01);
- raw KYC/tax/bank document collection/storage;
- Trust screening reuse.

### Module-Owned Data

- `KycVerification` / `KycStatus`;
- `TaxProfile` / `TaxProfileStatus`;
- `TaxDocument` / `TaxDocumentType`;
- `PayoutAccount` / `PayoutAccountStatus`;
- `ProviderRequirementSnapshot`;
- `ProcessedStripeEvent` for enabled Stripe callback dedupe.

### Public Interfaces

Implement/complete:

- `startKycOnboarding`;
- `startTaxProfileCollection`;
- `startPayoutAccountOnboarding`;
- `getFinancialSetupSummary`;
- `getProviderRequirementSnapshot` safe query;
- **SH-019 `evaluateFinancialReadiness`** for current supported action vocabulary;
- internal normalized provider result handlers.

SH-019 action vocabulary must be controlled/versioned. At minimum support a generic financial setup/status action and payout-readiness inputs needed later; do not imply publication timing from this feature.

### Shared Operations Used

- **SH-001 — Identity:** resolve professional actor at entry.
- **SH-002 — Role / Authority:** authorize self/admin setup/read. Local policy: Payment resource/action facts. **No local RBAC.**
- **SH-014 — Identity step-up:** before sensitive balance/tax/account views/mutations according to approved action table. **No local MFA.**
- **SH-011 — Hold:** include applicable financial restriction dimension where action policy requires. **No local block flag.**
- **SH-019 — Payment-owned public interface:** this feature implements dimensioned readiness. Local policy remains Payment.
- **SH-030 — Audit sensitive access:** tax/payout-account/financial detail access proof.
- **SH-044 — platform idempotency:** onboarding/start/resume commands.
- **SH-046 — outbox:** KYC/tax/account status-change events after committed state.
- **SH-055 — shared expiry scheduler:** only for approved expiration semantics.
- **SH-059/060/061/062 — provider callback/reconciliation:** verified, deduped, translated, reconciled.
- **SH-063 — provider snapshot:** safe requirements history.
- **SH-078 — provider minimization:** provider inputs/telemetry.
- **SH-041 — Notification:** approved requires-input/restriction alerts; delivery remains external.
- **SH-034/037/038 — Ops:** safe telemetry/provider failure/job state.

### Domain Logic

- Create Payment-owned record before provider handoff where needed so a callback has a canonical target.
- Resolve current KYC/TaxProfile using only the feature-approved UD-06 policy; reject ambiguity instead of choosing arbitrary latest row.
- Provider status maps to Workin Ants enums through SH-061; unknown status is unsupported/review.
- KYC and Trust Verification are never cross-read as substitutes.
- `PayoutAccount.status`, `chargesEnabled`, and `payoutsEnabled` contribute to account readiness; none alone is the entire SH-019 decision.
- TaxProfile verified status and required document proof contribute to tax dimension; sales tax is not evaluated here.
- SH-019 returns each dimension independently and can return multiple blockers/remediation hints safely.
- `ProfessionalProfile.stripeReady` and `stripeAccountId` are never read as authoritative truth and are not written as gate truth. If a temporary compatibility projection is unavoidable, it must be one-way/deprecated and covered by a regression test showing no readiness read depends on it.

### Authorization / Compliance

- Provider-hosted collection preferred for SSN/TIN/bank/KYC identity inputs.
- Step-up before approved sensitive setup/account/tax views and mutations.
- SH-030 for sensitive access.
- No raw KYC identity documents, tax IDs, bank credentials, or provider secret payloads in ordinary tables/events/logs.
- Admin/support access requires authority + Payment sensitivity policy; role alone is not carte blanche.
- KYC is payout/financial compliance, not a public trust badge.

### Database / Transaction Behavior

- Idempotent onboarding command creates/reuses the intended canonical record under approved selection policy.
- Provider event claim and target state transition follow Feature 02's approved transaction/recovery pattern.
- Use expected-state transition guards; no arbitrary status setter.
- `PayoutAccount(provider,providerAccountId)` uniqueness enforced.
- Requirement snapshots append rather than overwrite history.
- Do not add a guessed “one current KYC/TaxProfile” constraint without resolving UD-06; constrain command behavior transactionally and record ADR if schema enforcement is required.

### Events / Jobs

Proposed owner events, versioned/minimized:

- KYC status changed;
- TaxProfile status changed;
- PayoutAccount status changed.

Jobs:

- provider reconciliation;
- approved expiry/refresh/recheck;
- retry/dead-letter for transient provider work.

Consumers re-query current SH-019 facts; events are not raw provider payloads.

### Provider Integration

- Stripe/Connect or approved configured KYC/tax-profile provider adapter.
- Provider session/client secret is short-lived and only returned to authorized client if provider flow requires it.
- Webhook signature/dedupe/translation/reconciliation mandatory.
- Requirement snapshot fields are allowlisted.

### UI / Admin Surface

Where root product UI exists:

- professional financial setup checklist;
- KYC/tax/account status and safe next action;
- continue/resume provider-hosted onboarding;
- restricted admin case metadata/reconcile action if product context already has an Ops/admin shell.

Do not display raw tax identifiers, bank data, raw provider requirements, or internal risk rules.

### Failure Behavior

- step-up missing/expired → `step_up_required`, no sensitive data/action;
- authority denied → no provider session or data;
- duplicate onboarding command → replay canonical result;
- provider unavailable → canonical local state remains safe/pending, IntegrationFailure recorded, retry/reconciliation available;
- unknown provider state → explicit unsupported/review;
- ambiguous current KYC/TaxProfile → explicit conflict until UD-06 policy resolves;
- restricted payout account → SH-019 account dimension denied/review with safe reason;
- duplicate provider event → no repeated transition/event/notification.

### Tests

- unit: lifecycle guards, SH-019 dimensions/reasons;
- integration: onboarding persistence and uniqueness/current-selection behavior;
- provider: signature/dedupe/mapping/reconciliation/status fixtures;
- authorization: self/admin/unrelated User;
- step-up: valid/expired/wrong action/target;
- SH-030 sensitive access request contract;
- regression: no Trust verification or ProfessionalProfile compatibility field used as Payment readiness truth;
- security: redaction/no raw tax/KYC/bank/provider data in logs/events/notifications;
- concurrency: simultaneous onboarding/start/resume for same intended target;
- failure: provider timeout/unknown/restricted status.

### Documentation Updates

- Freeze exact SH-019 dimensions/action keys/reason-code version in Module public-interface docs.
- Record UD-06 constrained selection/current-record policy if approved.
- Record enabled provider event types/mappings.
- Progress tracker update.

### Acceptance Criteria

1. KYC/TaxProfile/PayoutAccount canonical records—not provider/profile booleans—drive readiness.
2. Enabled provider callbacks are verified/deduplicated/mapped/reconciled.
3. SH-019 returns distinct dimensions with safe evidence/reasons and no opaque `canPayout` truth.
4. Sensitive financial setup access is step-up/authorized/audited as specified.
5. No raw financial credentials/documents or provider payloads leak into normal app data/logs.
6. Duplicate/replayed requests/events do not duplicate canonical effects.
7. Feature does not decide Cluster U-01 publication/profile/Gig timing.

### Exit Gate

Feature 03 passes only when the CL-03 Feature 07 Payment exit conditions are met: provider-backed canonical states are authoritative; SH-019 is dimensioned; sensitive access is protected; compatibility fields are non-authoritative; provider replay/reconciliation tests pass; and all enabled paths pass unit/integration/provider/security/authorization tests.

---

# Phase 3 — Professional Balance and Payout

## 04 — Append-Only Professional Balance Projection

### Objective

Implement the Payment-owned append-only professional balance projection so authoritative Order/refund/dispute/hold-related source effects produce financial entries exactly once and safe available/held/requested/paid totals can be derived without a mutable wallet balance.

### Observable Result

- An eligible authoritative Order economic event can create the intended Payment ledger effect once.
- Replaying the same source event creates no duplicate financial effect.
- Refund/dispute/hold-release source effects can create approved compensating/holding entries without changing the source case.
- Professional balance query derives current totals by profile/currency from ledger entries.
- Historical commission/fee amounts come from immutable Order snapshots, not current Track entitlement.
- Ledger entries cannot be edited through normal application services.
- A reconciliation mode can compare source-owner economic facts to ledger effects and report/repair missing effects safely.

### Cluster Build-Plan Link

Implements the balance-foundation half of **CL-03 Feature 09 — Professional Balance, Payout Request, and Transfer**. It intentionally stops before creating payout requests/transfers.

### Dependencies

- Module Features 01–03.
- Transaction / Order source-event or narrow economic snapshot contract.
- Review / Dispute and ComplianceHold money-consequence contracts where enabled.
- SH-045/046/047/048/051 and root transaction infrastructure.
- **PT-02 / UD-09 durable source-effect identity must be resolved before production projection is enabled.**
- **UD-10 ledger effect/sign/reservation table must be frozen in this feature specification.**
- Order historical commission/fee snapshots must exist for effects that depend on them.

### In Scope

- `ProfessionalBalanceLedgerEntry` append repository/service.
- Durable source-effect dedupe invariant approved under PT-02.
- Explicit effect-policy table for enabled sources and entry types.
- Derived balance projection query by ProfessionalProfile/currency/evaluation time.
- Source events/commands for:
  - eligible Order earning;
  - approved platform fee/commission consequence as represented by Order snapshot;
  - refund economic reversal;
  - dispute/hold economic hold and release where approved;
  - manual financial adjustment only through restricted audited command if product policy requires it.
- Reconciliation/backfill dry-run for enabled source types.
- Payment domain event after ledger effect is recorded.

### Out of Scope

- PayoutRequest/PayoutTransfer creation;
- processor payout execution;
- recalculating pricing/commission from current Track;
- deciding Order completion/refund/dispute outcome;
- Prize/Reward source lifecycle;
- “wallet balance” row/cache as truth;
- enabling ledger entry types whose source/sign/availability policy has not been approved;
- deleting/re-writing prior ledger entries.

### Module-Owned Data

- `ProfessionalBalanceLedgerEntry` / `ProfessionalBalanceLedgerEntryType`.
- No mutable aggregate balance source table.
- If PT-02 requires a new durable source-effect identity column/model, that schema change belongs in this feature **only after architecture approval**.

### Public Interfaces

- `appendProfessionalBalanceEffect` — internal/public-to-approved owner consumers as appropriate, never general client writable;
- `getProfessionalBalanceProjection` — step-up protected professional/admin query;
- approved `getProfessionalBalanceProjection` and `getPayoutHistory` queries for the corresponding ledger/payout views; `getFinancialHistory` is not an approved facade and cannot be an implementation dependency unless Payment architecture first defines its scope, authorization, sensitive-access behavior, and response semantics (CL-03-R007);
- reconciliation/admin command through restricted Ops interface if root product has one.

No consumer receives a `setBalance` interface.

### Shared Operations Used

- **SH-045 — platform consumer inbox:** dedupe inbound Order/refund/dispute domain events. Local policy: handler/effect identity. **Do not build:** local processed-order-event boolean.
- **SH-046 — platform outbox:** emit Payment balance-effect fact after authoritative append. **Do not build:** unreliable event emitter.
- **SH-047/048 — shared jobs/retry:** reconciliation/backfill/source-event processing. Local policy: source fetch retryability and repair action. **Do not build:** balance worker framework.
- **SH-051 — shared DB lock:** serialize any profile/currency operation whose source-effect transaction can race. Local policy: exact lock key. **Do not build:** balance mutex.
- **SH-053 — shared lifecycle plumbing:** not used for immutable ledger rows themselves; may be used only for related mutable owner records. **Do not create:** ledger status lifecycle.
- **SH-109 — snapshot pattern:** consume Order's historical commission/entitlement/price snapshot as immutable input when required. Payment does not own that snapshot.
- **SH-029 — Audit:** restricted manual adjustment/reconciliation command proof where required. **Do not build:** financial audit table.
- **SH-014/030 — Identity/Audit:** sensitive balance/history reads. **Do not build:** custom payout access logger/MFA.
- **SH-034/038 — Ops:** safe reconciliation/job telemetry.

### Domain Logic

Before coding, the feature specification must freeze an **enabled ledger-effect matrix** containing, for each source:

- authoritative source owner/event/decision;
- required snapshot fields;
- ledger entry type(s);
- amount basis (gross, net, commission/fee snapshot, refund amount);
- sign convention;
- currency rule;
- `effectiveAt` and `availableAt` semantics;
- hold/release behavior;
- correction/reversal mapping;
- durable `effectKey` for one source event producing multiple distinct entries.

Rules:

- Sum effects only within one currency; never silently convert currencies.
- An Order event does not authorize Payment to recompute Order pricing.
- A dispute/hold event can create Payment financial consequences only when source-owner contract explicitly authorizes the meaning.
- `metadata` is minimized explanatory context, not a hidden second source-of-truth blob.
- `reward_value` / `prize_value` ledger types remain disabled unless an explicit payout/economic policy says they belong in professional balance; tax reporting alone uses SH-118/TaxYearEarningsSummary instead.
- Adjustment is restricted, reasoned, audited, and append-only.

### Authorization / Compliance

- Source-event workers run as trusted system actors and still validate source owner/version.
- Balance/history UI query: SH-001/002 + SH-014 + SH-030.
- Manual adjustment/reconciliation: restricted authority + step-up if root policy requires + SH-029.
- No raw provider/account/tax details are needed in ledger metadata.

### Database / Transaction Behavior

For an inbound source event:

```text
begin transaction
→ SH-045 / approved durable source-effect claim
→ validate current source snapshot/version when race-sensitive
→ create all intended immutable ledger entries
→ append Payment outbox event if required
commit
```

A unique DB conflict/replayed inbox claim returns the already-applied/no-op result.

Ledger table is insert-only through application services. Tests must prove no ordinary update/delete path exists.

If source owner must be queried outside the local DB transaction, validate event/current owner state before irreversible append and use source version/effect identity so retry cannot double-apply.

### Events / Jobs

- Proposed `payment.balance.effect_recorded.v1` event, minimized.
- Source-event consumer worker.
- Reconciliation/backfill worker with dry-run and affected-source report.
- Reconciliation repair invokes the same idempotent append command; no direct SQL “balance correction” patch.

### Provider Integration

None directly. This feature derives from owner facts, not provider balances. Provider-held balance may be contextual evidence later, but provider balance is never the Workin Ants ledger source.

### UI / Admin Surface

Where financial history UI exists:

- available/held/requested/paid totals per currency;
- safe ledger history categories and dates;
- no “wallet” language;
- no provider internal balance or secret details.

Admin reconciliation view, if existing, shows safe source refs/effect counts, not raw provider payloads.

### Failure Behavior

- duplicate source event/effect → no new ledger entry;
- missing/invalid source snapshot → reject/retry or manual review, never guess amount;
- current Track entitlement differs from historical snapshot → historical snapshot wins;
- currency mismatch → explicit validation/conflict;
- malformed negative/positive effect against approved matrix → reject;
- source owner unavailable → retry; no speculative append;
- reconciliation detects orphan/missing effect → report and optionally repair through same command after validation;
- unresolved source effect type → disabled, not coerced to `adjustment`.

### Tests

- unit: effect matrix/sign/availability and derived balance math;
- integration: append-only persistence and source-effect uniqueness;
- concurrency: duplicate source event delivered simultaneously;
- contract: Order snapshot/history input; no direct Order/Track Prisma read;
- regression: historical commission does not change when current entitlement changes;
- refund/dispute/hold/release effect tests for enabled semantics;
- manual adjustment authorization/audit;
- balance query step-up/sensitive-access proof;
- reconciliation dry-run/repair/replay;
- currency isolation/property tests for arithmetic.

### Documentation Updates

- Record approved PT-02 source-effect schema/invariant.
- Record the exact enabled ledger-effect matrix and sign/availability semantics, resolving the Feature 04 portion of UD-10.
- Add public balance query contract/version.
- Progress tracker update.

### Acceptance Criteria

1. Balance is fully derivable from append-only Payment entries for enabled sources.
2. A source event/effect cannot be applied twice under retry or concurrency.
3. Historical commission/fee comes from Order snapshot, never current Track lookup.
4. Refund/dispute/hold effects preserve source-owner lifecycle boundaries.
5. No mutable wallet/balance source is introduced.
6. Sensitive balance/history access is protected and audited.
7. Reconciliation can identify/repair missing enabled effects through the same idempotent command.

### Exit Gate

Feature 04 passes only when PT-02/UD-09 is durably resolved, the enabled ledger effect/sign/availability matrix is documented, append-only/idempotency/concurrency/reconciliation tests pass, and no source workflow can create a duplicate financial effect or mutable wallet truth.

---

## 05 — Payout Request, Atomic Reservation, Transfer, and Reversal

### Objective

Implement the professional payout path over the append-only balance projection: step-up-protected request, atomic reservation, hold/readiness gating, idempotent provider transfer, canonical paid/failed/reversed outcomes, and reconciliation without overspending or creating a wallet/escrow lifecycle.

### Observable Result

- Professional can request a positive amount in a supported currency from an explicitly resolved active payout account.
- Concurrent payout requests cannot reserve more than current available projected funds.
- A clean approved request can create exactly one intended provider transfer effect.
- Provider callback/reconciliation moves PayoutTransfer/PayoutRequest through approved states and appends corresponding ledger effects.
- Active holds/restrictions can block request/execution with safe reasons.
- Provider transient/terminal/ambiguous failures behave differently and do not duplicate money movement.
- Professional can view payout request/transfer history after step-up.

### Cluster Build-Plan Link

Completes Payment's **CL-03 Feature 09 — Professional Balance, Payout Request, and Transfer** implementation.

### Dependencies

- Module Features 01–04.
- SH-019 from Feature 03.
- Active balance projection/source-effect safety from Feature 04.
- SH-011/014/030/044/046/047/048/051/056/059/060/061/062.
- Payout provider adapter/Stripe Connect configuration.
- **UD-07 payout-account selection must be constrained:** recommended MVP path is explicit `payoutAccountId`; if more than one eligible account and no explicit ID, return conflict rather than choosing first/latest.
- **UD-08 multiple-hold evidence** must have an approved representation or one-FK limitation documented as non-authoritative explanation.
- **UD-10 reservation/release ledger entries** must be finalized.
- **UD-11/12 payout transfer source/retry semantics** must be approved or feature constrained.

### In Scope

- `createPayoutRequest`.
- Payout review/block/approve/cancel transitions supported by approved policy.
- Atomic reserve/release consequences in ledger.
- `executePayoutTransfer` worker/command.
- Provider transfer result callback/reconciliation.
- PayoutRequest/PayoutTransfer status synchronization under owner policy.
- Paid/failed/reversed/cancelled ledger consequences.
- Payout history query.
- Safe notifications/audit/access proof.
- Provider reconciliation and retry/dead-letter.

### Out of Scope

- Order lifecycle/completion;
- dispute adjudication;
- wallet/escrow/custody;
- current subscription commission recalculation;
- arbitrary instant/manual bank payout outside approved provider adapter;
- multiple payout split-routing or multi-account automatic selection without ruling;
- speculative PayoutTransfer attempt child model;
- direct Order-based transfer source unless UD-11 explicitly approves it.

### Module-Owned Data

- `PayoutRequest` / `PayoutRequestStatus`;
- `PayoutTransfer` / `PayoutTransferStatus`;
- `ProfessionalBalanceLedgerEntry` payout-related effects;
- `ProcessedStripeEvent` for Stripe transfer/payout callback dedupe;
- `PayoutAccount` as referenced canonical account.

### Public Interfaces

- `createPayoutRequest`;
- `cancelPayoutRequest` where allowed;
- restricted `reviewPayoutRequest` / approve/block commands if admin/manual review is part of approved product policy;
- `getPayoutHistory`;
- worker/internal `executePayoutTransfer`;
- internal `applyPayoutTransferResult`;
- reconciliation command for authorized Ops.

No public `markPayoutPaid` command exists.

### Shared Operations Used

- **SH-014 — Identity step-up:** mandatory before payout request/balance/account sensitive flow. **No payout MFA clone.**
- **SH-002 — Role / Authority:** self/admin/system action authorization.
- **SH-011 — ComplianceHold:** evaluate request/execution restrictions; local policy maps scopes. **No `payoutBlocked` truth.**
- **SH-019 — Payment:** current payout readiness including KYC/tax/account/balance/restrictions.
- **SH-030 — Audit:** sensitive balance/payout access proof.
- **SH-044 — idempotent command:** payout request and transfer semantic keys.
- **SH-046 — outbox:** payout request/transfer facts.
- **SH-047/048 — queue/retry:** transfer/reconciliation workers.
- **SH-051 — DB lock:** serialize profile+currency payout reservation and critical request transitions.
- **SH-056 — atomic reservation:** reserve available value transactionally; Payment owns sufficiency/release policy.
- **SH-059/060/061/062 — provider:** verify/dedupe/map/reconcile transfer results.
- **SH-029 — generic audit:** admin review/manual adjustment/reconcile actions.
- **SH-041 — Notification:** requested/blocked/paid/failed/reversed messages with safe payload.
- **SH-034/037/038 — Ops:** redacted provider/worker diagnostics.

### Domain Logic

Recommended constrained MVP **Proposed Ruling PT-03** for approval before coding:

1. payout execution is **request-based**; `PayoutRequest` is the authoritative Payment intent and a PayoutTransfer created for it is not independently sourced from an Order;
2. client supplies/chooses an explicit eligible `payoutAccountId`; no implicit first/latest account selection;
3. one semantic transfer intent uses one stable provider idempotency key; technical retry reuses that key;
4. after an explicit terminal business failure, a genuinely new transfer attempt/history strategy requires UD-12 approval rather than silently recycling identifiers;
5. `orderId` on PayoutTransfer, if used, is provenance only unless a later approved direct-order transfer workflow says otherwise.

Payout flow:

```text
request
→ step-up + authority
→ current SH-019 payout readiness
→ SH-011 holds
→ DB lock profile+currency
→ re-derive available funds
→ create PayoutRequest + reservation ledger effect atomically
→ approve/processing under owner policy
→ create PayoutTransfer with unique semantic idempotency key
→ provider transfer
→ verified callback/reconciliation
→ update transfer/request + append paid/failed/release/reversal effects
```

The feature specification must explicitly list the payout-related ledger entry mapping for:

- reservation/requested;
- paid;
- failed/released;
- cancelled/released;
- reversal;
- hold/release if applicable.

No status transition is inferred solely from provider text without SH-061 mapping.

### Authorization / Compliance

- Professional self payout requires own profile relationship, step-up, SH-019, SH-011.
- Admin review cannot bypass KYC/tax/account/hold requirements unless an explicitly approved policy says which gate may be overridden; no generic “admin force paid.”
- Sensitive history/access uses SH-030.
- Provider account/bank credentials remain provider-hosted.
- Payout KYC is not Trust screening.

### Database / Transaction Behavior

Request transaction:

```text
begin
→ acquire profile+currency lock / atomic reservation
→ load current ledger projection under lock
→ validate available >= requested amount
→ create idempotent PayoutRequest
→ append reservation/request ledger effect
→ outbox event
commit
```

Transfer creation uses `PayoutTransfer.idempotencyKey @unique` and expected request state. Provider call may occur after durable transfer intent exists.

Callback/reconciliation transaction validates current transfer state before applying result and append effects. Duplicate provider event/no-op is safe.

Multiple active holds: do not assume `blockedByHoldId` is the complete restriction list; store only approved primary reference if architecture says so and re-query SH-011 for current truth.

### Events / Jobs

Proposed minimized events:

- payout request status changed;
- payout transfer status changed;
- balance effect recorded.

Workers:

- transfer execution;
- transfer reconciliation;
- retry/dead-letter;
- optional blocked-request reevaluation only if approved policy/event contract exists.

### Provider Integration

Stripe Connect/payout adapter or approved provider. Stable provider idempotency key. Map provider transfer/payout/balance transaction refs into PayoutTransfer. Ambiguous timeout requires provider reconciliation before retrying money movement.

### UI / Admin Surface

Professional:

- available projection by currency;
- payout account selection;
- amount entry/validation;
- request confirmation/status/history;
- safe blocked/requires-input reason.

Admin/Ops if existing:

- request/transfer status and safe provider refs;
- reconcile/retry permitted technical actions;
- no raw bank/KYC/tax data;
- no “force paid” shortcut.

### Failure Behavior

- insufficient funds → deny before request/reservation effect;
- concurrent requests → one wins lock/reservation; loser re-evaluates and returns insufficient/conflict as appropriate;
- hold/restriction/expired KYC/tax/account → blocked with safe reason;
- step-up missing → no request;
- duplicate request idempotency → replay original/current canonical request;
- provider transient failure → bounded retry using same safe idempotency key;
- ambiguous provider timeout → reconcile before retry;
- terminal provider failure → failed/review state + release/correction ledger effect under approved matrix;
- provider reversal → transfer/request owner transition + compensating ledger effect;
- duplicate callback → no duplicate transfer/ledger effect;
- unsupported retry semantics under UD-12 → manual review/disabled path, not new hidden attempt.

### Tests

- unit: payout readiness/sufficiency, request/transfer transition graph, payout ledger effects;
- concurrency: many simultaneous payout requests cannot overspend;
- integration: request + reservation atomicity and rollback;
- provider: idempotency, callback replay, timeout/reconciliation, terminal failure, reversal;
- step-up/authority/hold tests;
- SH-030 sensitive access;
- explicit account-selection ambiguity test;
- duplicate source/provider event test;
- history/result redaction;
- regression: no wallet/escrow/mutable balance and no Order state mutation.

### Documentation Updates

- Approve/document PT-03 or alternative UD-11/12 payout strategy.
- Document exact payout ledger effect matrix resolving remaining UD-10 scope.
- Document multiple-hold evidence handling under UD-08.
- Freeze payout command/status/reason contracts.
- Progress tracker update.

### Acceptance Criteria

1. Available funds cannot be overspent under concurrent payout requests.
2. Payout requires step-up, authority, current SH-019, and applicable hold evaluation.
3. Request and transfer are distinct records/lifecycles.
4. Provider retry/replay cannot duplicate money movement or ledger effects.
5. Paid/failed/reversed/cancelled consequences are represented by canonical status + append-only ledger effects.
6. No wallet/escrow source truth exists.
7. No Order/Dispute/Hold foreign lifecycle is mutated.

### Exit Gate

Feature 05 passes when the complete CL-03 Feature 09 exit gate is satisfied: balance remains derivable/append-only, concurrency cannot overspend, duplicate source/provider effects do not duplicate entries/transfers, payout gates are enforced, historical commission uses Order snapshots, provider failure/reversal/reconciliation are tested, and all financial/security/concurrency tests pass.

---

# Phase 4 — Transaction Payment and Sales-Tax Bridge

## 06 — Provider-Backed Sales-Tax Calculation for an Authoritative Order

### Objective

Implement transaction-level sales-tax calculation proof for an existing authoritative Order/pricing snapshot using an approved tax provider, while preserving Order, Offering, Digital Goods, Location, and seller TaxProfile ownership boundaries.

### Observable Result

- Given a valid Order pricing/version and approved buyer tax-location/item tax context, Payment can request a provider-backed tax calculation.
- `SalesTaxCalculation` and `SalesTaxLineItem` preserve the normalized calculation evidence.
- A calculation can be re-run for changed/stale checkout context without rewriting prior finalized evidence.
- Provider unavailability or insufficient location/tax-code evidence fails explicitly rather than guessing tax.
- Seller TaxProfile is not consulted as checkout sales-tax truth.

### Cluster Build-Plan Link

Implements the sales-tax calculation portion of **CL-03 Feature 10 — Payment and Sales-Tax Bridge to Transaction / Order**.

### Dependencies

- Module Features 01–03; Feature 02 provider shell.
- Stable Order payment/pricing/version snapshot query from CL-04.
- Approved item/tax-code input from Order/Offering/Digital Goods owner interfaces.
- Approved buyer tax-location evidence input.
- SalesTaxProvider adapter (Stripe Tax current path).
- SH-044/061/062/078/123.
- **SH-120 remains unresolved and is not a dependency.**
- **UD-16** calculation selection/finalization strategy must be constrained.
- **CL-03-R015 / UD-17:** line-level liability evidence is mandatory when lines can differ; the current schema gap and exact persistence design must be addressed before mixed-liability production.
- **UD-19** location provenance minimum must be approved enough for evidence.

### In Scope

- `calculateSalesTax` command.
- `SalesTaxCalculation` draft/calculated/failed persistence.
- `SalesTaxLineItem` normalized provider results.
- buyer tax-location fields/minimized provenance reference under approved contract.
- item tax-code/provider code consumption through owner facts.
- provider tax result mapping.
- read query for safe calculation evidence.
- dry-run/recalculate path for changed Order version.
- test/provider fixtures for supported item types/jurisdictions.

### Out of Scope

- Order state mutation/payment capture;
- final tax transaction recording (Feature 07);
- custom tax-rate/jurisdiction tables;
- SH-120 platform implementation;
- seller income/1099 TaxProfile logic;
- changing Offering/DigitalGoodsPolicy/PricingTier;
- mixed marketplace-facilitator/seller liability until the required line-level evidence has approved persistence and migration coverage under UD-17;
- partial refund/reversal.

### Module-Owned Data

- `SalesTaxCalculation` / `SalesTaxCalculationStatus`;
- `SalesTaxLineItem` / `SalesTaxLineItemType`;
- `SalesTaxProvider`;
- `SalesTaxLiabilityRole` at currently supported schema granularity.

### Public Interfaces

- `calculateSalesTax`;
- `getSalesTaxEvidenceForOrder` (calculation portion);
- internal `buildSalesTaxRequest` / `applySalesTaxResult`;
- provider `SalesTaxProviderPort`.

### Shared Operations Used

- **SH-044 — idempotent command:** calculation per Order/version/context fingerprint. **No local idempotency table.**
- **SH-061 — provider translation:** tax provider result/status normalization.
- **SH-062 — reconciliation:** supported provider calculation verification where useful.
- **SH-078 — minimization:** outbound buyer/item tax payload and telemetry.
- **SH-123 — target-owner validation:** validate Offering/PricingTier/Digital context references when not already frozen by Order snapshot. **No polymorphic direct Prisma lookup.**
- **SH-003 — Proposed owner-facts DTO pattern:** Order/item/location facts through owners, not generic repository.
- **SH-034/037 — Ops:** provider failure/redaction.
- **SH-046 — outbox:** only if downstream consumers need a Payment tax-calculation fact; no event solely for provider call attempt.

### Domain Logic

- Tax calculation input is bound to exact Order/pricing snapshot/version and buyer tax-location evidence.
- Client-submitted totals/tax are never authoritative.
- Item amount/currency must match authoritative snapshot.
- Provider tax code comes from an approved owner mapping/context; Payment consumes it and records the code used.
- Payment chooses/validates the minimum location evidence required by its tax policy; it does not become public Location owner.
- No silent currency conversion.
- `TaxProfile` is excluded from transaction sales-tax calculation logic except where a separately approved exemption certificate workflow exists; none is established here.
- **CL-03-R015 / UD-17:** Payment must preserve liability evidence per line when lines can differ. Until an approved field or immutable line-linked evidence structure and forward migration provide that proof, only carts with unambiguous supported liability may be enabled; mixed-liability carts fail `unsupported`. Transaction-level liability is not a substitute for line-level proof.
- **Constrained MVP for UD-16:** caller must carry the specific calculation ID and Order version forward. Do not query “latest calculation” as authoritative final tax.

### Authorization / Compliance

- Order owner establishes whether caller/workflow may calculate tax for the checkout; Payment validates the supplied owner contract.
- Buyer location is protected/minimized tax evidence, not Search/public data.
- No raw payment credential needed.
- Tax provider payload/logs use SH-078/034.
- Do not hardcode tax rates/thresholds from memory or local constants.

### Database / Transaction Behavior

- Create calculation row for a semantic calculation intent; line items written transactionally with normalized result.
- Idempotency fingerprint includes Order ID/version, amounts/currency, location evidence version, item/tax-code context version, provider.
- Reuse of same key+fingerprint returns same calculation; changed fingerprint with same key conflicts.
- Do not mark calculation finalized in this feature unless Feature 07's payment/finalization flow is executing.
- Prior calculated/failed rows remain evidence; recalculation creates/uses an explicit new intent rather than mutating a finalized historical record.

### Events / Jobs

- Optional minimized calculation-changed event if a consumer requires it.
- Provider reconciliation only for supported provider calculation API.
- No generic tax scheduler.

### Provider Integration

Stripe Tax or approved adapter. Map provider tax calculation IDs, transaction refs if returned, tax amount/rate/jurisdiction fields into canonical records. Provider-specific nested payload remains adapter-local.

### UI / Admin Surface

Mostly consumed by CL-04 checkout. Payment may expose safe diagnostic evidence in existing admin tooling. Do not build a second checkout UI.

### Failure Behavior

- Order/version stale → conflict; caller refreshes authoritative checkout state;
- missing/invalid tax location → validation/requires input;
- unsupported jurisdiction/item/mixed liability → unsupported;
- provider unavailable → unavailable/retryable according to approved checkout fail/hold policy; never estimated homemade tax;
- provider returns amount mismatch/unknown status → explicit failure/review;
- duplicate calculation command → replay same result;
- owner reference invalid → reject before provider call.

### Tests

- contract: Order snapshot and target-owner reference DTOs;
- unit: input fingerprint, liability constraint, result normalization;
- provider: supported tax fixtures, unknown status, amount mismatch, timeout;
- integration: calculation+line item transaction/idempotency;
- stale Order/version conflict;
- seller TaxProfile separation regression;
- location/telemetry privacy test;
- mixed-liability unsupported test until approved line-level persistence exists; then verify differing line liability remains independently provable (CL-03-R015);
- no custom tax-rate code path test/architecture check.

### Documentation Updates

- Record constrained UD-16 calculation selection strategy.
- Record the CL-03-R015 line-level evidence requirement, UD-17 persistence gap, and supported liability scope.
- Record minimum tax-location provenance under UD-19.
- Document supported SalesTaxProvider/item types/jurisdictions for this feature.
- Progress tracker update.

### Acceptance Criteria

1. Calculation is provider-backed and bound to authoritative Order/version/context.
2. Payment persists normalized calculation/line proof and no foreign source lifecycle.
3. Seller TaxProfile is not sales-tax truth.
4. Unsupported/missing location/liability/provider cases fail explicitly.
5. Repeated semantic calculation is idempotent.
6. No custom tax engine or SH-120 ownership is introduced.

### Exit Gate

Feature 06 passes when supported sales-tax calculation is deterministic/idempotent/provider-tested, stale Order and unsupported liability/location cases fail safely, and the resulting calculation can be handed to Feature 07 without any consumer inferring tax from “latest row” or client totals.

---

## 07 — Payment / Refund Rail, Tax Finalization, and Order Handoff

### Objective

Complete the CL-03 → CL-04 financial bridge: execute the supported provider payment/refund rail for an authoritative Order, finalize/record sales tax, process verified provider events, and command Transaction / Order with normalized outcomes without Payment becoming transaction owner.

### Observable Result

- An existing authoritative Order can prepare/execute the supported provider payment path.
- Verified payment success/failure is sent to Order through its public command, which alone changes Order/OrderEvent.
- The correct SalesTaxCalculation can be finalized and SalesTaxTransaction recorded once.
- An approved SH-108 refund can execute provider refund and record supported sales-tax reversal/refund proof.
- Duplicate Stripe events do not repeat Order commands or tax transactions.
- Missing webhook/ambiguous provider outcome can be reconciled safely.
- Unsupported multi-attempt/chargeback/partial-refund cases are explicit rather than represented with guessed models.

### Cluster Build-Plan Link

Completes Payment's implementation of **CL-03 Feature 10 — Payment and Sales-Tax Bridge to Transaction / Order**.

### Dependencies

- Module Features 01–03 and 06; Feature 02 provider ingress.
- Stable CL-04 Order payment snapshot + verified payment/refund result commands.
- SH-108 refund contract.
- SH-044/046/047/048/059/060/061/062/109/123.
- Approved Stripe payment/Checkout/Tax configuration.
- **UD-13 payment-attempt/refund/chargeback evidence scope must be explicitly resolved or constrained.**
- **UD-18 partial/multiple refund semantics must be constrained.**
- Feature 06's exact calculation ID/Order version binding.

### In Scope

- provider payment intent/session/rail preparation/execution for the current supported Order flow;
- verified payment-result handler;
- `finalizeSalesTaxCalculation`;
- `recordSalesTaxTransaction`;
- Order verified payment outcome command;
- SH-108 Payment-side refund execution;
- supported full/single refund tax reversal/refund recording;
- provider callback/reconciliation for payment/tax/refund effects;
- Payment domain events/ops telemetry;
- safe admin reconciliation trigger where root tooling exists.

### Out of Scope

- Order creation/lifecycle/RefundStatus implementation;
- Agreement lifecycle;
- dispute adjudication;
- arbitrary chargeback lifecycle without UD-13 model/ruling;
- multiple payment attempts/history if current evidence model cannot prove them;
- partial/multiple refund allocation until UD-18 resolved;
- direct Order DB writes;
- custom tax engine;
- Booking/delivery entitlement.

### Module-Owned Data

- `ProcessedStripeEvent`;
- `SalesTaxCalculation` / line items;
- `SalesTaxTransaction`;
- Payment provider references only where current Payment-owned records support them;
- related ledger effects only when an authoritative Order/refund outcome is independently consumed through Feature 04's source-effect path.

**Important gap:** current schema has no generic `PaymentAttempt`, `PaymentCharge`, `RefundAttempt`, or `Chargeback` aggregate. Do not create one silently.

### Public Interfaces

Payment side:

- `prepareOrExecuteOrderPaymentRail`;
- `finalizeSalesTaxCalculation`;
- `getSalesTaxEvidenceForOrder`;
- Payment execution handler for SH-108 refund;
- internal provider payment/refund/tax result handlers;
- restricted reconciliation command.

Consumed Order side:

- authoritative payment/pricing/participant/version snapshot query;
- record verified payment result command;
- record approved refund/provider result command;
- Order-specific conflict/current-state response.

### Shared Operations Used

- **SH-044 — idempotent commands:** provider payment/refund/tax-finalize semantic keys.
- **SH-046 — Payment outbox:** Payment-owned facts only.
- **SH-047/048 — reliable jobs/retry:** provider and cross-owner handoff/reconciliation.
- **SH-059/060/061/062 — provider security/dedupe/mapping/reconciliation:** mandatory for Stripe callbacks.
- **SH-108 — Order/Payment refund boundary:** Order coordinates approved refund; Payment executes provider rail. **Do not build:** Payment RefundStatus/case lifecycle.
- **SH-109 — historical snapshot:** Order stores current point-in-time payment/tax/entitlement decision fields required by transaction history through its owner command. Payment retains its own separate tax evidence.
- **SH-123 — owner target validation:** only when external target/item refs are not already frozen by Order snapshot.
- **SH-034/037/038 — Ops:** safe provider/handoff failure visibility.
- **SH-029 — Audit:** manual reconciliation/refund intervention where required.

### Domain Logic

Before production enablement, choose one of these architecture-approved UD-13 paths:

**Preferred constrained MVP Proposed Ruling PT-04:** for the currently supported single provider payment flow, Payment may execute the provider rail using `ProcessedStripeEvent` for callback dedupe and Payment-owned tax records for tax proof, while Order stores its provider payment references/outcome through its own command. This does **not** claim a durable multi-attempt/chargeback history. Any workflow requiring multiple attempts, payment-attempt audit trail, provider disputes/chargebacks, or granular refund-attempt evidence remains disabled until a first-class Payment model is approved.

Or approve a new Payment-owned provider payment/refund model through architecture before coding it.

Payment success path:

```text
Order snapshot/version
→ validate amount/currency/tax calculation ID
→ provider payment rail with stable idempotency
→ verified provider result (webhook/query/reconcile)
→ finalize correct SalesTaxCalculation if required
→ record SalesTaxTransaction once
→ invoke Order recordVerifiedPaymentResult idempotently
→ Payment outbox/telemetry
```

Refund path:

```text
Order/Dispute approved refund → SH-108
→ Payment validates amount/currency/provider context
→ provider refund idempotently
→ verified/refetched result
→ record supported tax refund/reversal once
→ invoke Order refund-result command
→ source Order/refund event later drives ledger correction through Feature 04
```

Do not append a refund ledger effect merely from provider callback if Order is the authoritative refund outcome source; avoid double counting by defining one source-of-economic-effect path.

### Authorization / Compliance

- Checkout/order authority comes from Order public contract and authenticated/customer workflow as defined by CL-04.
- Payment never trusts client amount, tax, seller, paid flag, or redirect.
- Refund execution requires approved Order/refund source decision and authority context.
- No raw payment credentials stored.
- Tax/location evidence retained under Payment policy.
- Admin reconciliation is authorized/audited; no “force Order paid” control in Payment.

### Database / Transaction Behavior

- Provider event claim is idempotent through `ProcessedStripeEvent`.
- Sales-tax finalization transaction verifies calculation ID + Order ID/version/current supported state.
- `SalesTaxTransaction` recording must be protected against duplicate semantic provider transaction; if current schema lacks provider transaction uniqueness needed for the enabled provider, add an approved DB constraint/migration rather than query-then-insert only.
- Local Payment write/outbox commits atomically where possible.
- Order command is a separately idempotent cross-owner effect with correlation/causation ID and reconciliation when unavailable/conflicting.
- Do not wrap foreign writes in a pretend local transaction.

### Events / Jobs

- Payment sales-tax calculation/transaction changed facts as needed.
- Provider payment/refund/tax callback handlers.
- payment/tax reconciliation worker.
- cross-owner Order handoff retry/reconciliation worker.
- dead-letter with safe provider/Order refs.

### Provider Integration

Stripe/Checkout/PaymentIntent/Tax or approved adapter path. Provider-native object stays in adapter. Stable provider idempotency keys. Verify amount/currency/object association before reporting success to Order.

### UI / Admin Surface

Primary UI belongs to CL-04 checkout/refund workflow. Payment may expose restricted reconciliation metadata only in existing admin/Ops surface. Do not build duplicate checkout/refund case UI in this Module.

### Failure Behavior

- client redirect says success but no verified provider result → remain pending/unverified; do not command Order paid;
- invalid/duplicate webhook → reject/no repeated effect;
- provider tax unavailable before required checkout → approved fail/hold policy, no guessed tax;
- stale Order/version → conflict and reconcile/refresh, no direct patch;
- Order command unavailable after verified provider payment → Payment retains provider/tax evidence, queues/reconciles owner command; does not mutate Order;
- Order command conflict → query current Order and reconcile; quarantine/escalate inconsistent provider result;
- provider refund transient failure → retry safely;
- provider refund terminal failure → return provider rail failure; Order owns transaction/refund status under its policy;
- unsupported partial/multiple refund → `unsupported`, no fake allocation;
- chargeback/provider dispute event without UD-13 model → explicit unsupported/manual review/ops, not mapped to user Dispute automatically.

### Tests

- provider signature/dedupe/payment/refund mapping;
- contract: no direct Order writes; verified payment/refund outcome commands;
- payment amount/currency/Order association validation;
- client redirect spoof regression;
- tax calculation finalization/transaction idempotency;
- duplicate webhook → one Order command/tax transaction;
- missing webhook → reconciliation repairs/handoffs;
- stale Order/version conflict;
- Order command outage/retry/reconciliation;
- full/supported refund tax reversal;
- partial/multi-refund unsupported test until UD-18 resolved;
- chargeback unsupported test until UD-13 resolved;
- telemetry/retention redaction;
- no double ledger refund effect across provider + Order source event.

### Documentation Updates

- Approve/document PT-04 or a first-class provider payment/refund model, resolving current UD-13 scope.
- Document enabled payment/refund provider events.
- Document supported refund/tax-reversal scope under UD-18.
- Freeze Order payment/refund contract versions and correlation semantics.
- Progress tracker update.

### Acceptance Criteria

1. Payment can execute the supported rail without becoming Order owner.
2. All Order/RefundStatus/OrderEvent changes occur through tested Order public commands.
3. Payment sales-tax proof is separate from TaxProfile and bound to correct Order/version.
4. Duplicate provider events do not duplicate Order transitions, tax transactions, or financial effects.
5. Missed provider/Order handoff effects can reconcile safely.
6. Unsupported multi-attempt/chargeback/partial-refund cases are explicit and disabled rather than modeled by guesswork.
7. Client/provider raw state cannot directly mark an Order paid/refunded.

### Exit Gate

Feature 07 passes only when the complete CL-03 Feature 10 exit gate is satisfied: supported payment/tax/refund rails preserve Order ownership; verified provider events are replay-safe; tax proof is Payment-owned; reconciliation works; unsupported partial/refund cases fail explicitly; and provider/contract/integration/security tests pass.

---

# Phase 5 — Tax Reporting and Reportable-Value Intake

## 08 — SH-118 Taxable-Value Intake and Tax-Year Aggregation

### Objective

Implement Payment's canonical tax-reporting intake so approved source Modules can report recognized earnings/prize/reward value idempotently and Payment can maintain reconciled `TaxYearEarningsSummary` records without absorbing source lifecycles or hardcoding filing thresholds.

### Observable Result

- An approved Order/Prize/Reward/source owner can call SH-118 with a recognized value snapshot.
- Replaying the same recognition does not double-count the tax-year summary.
- Tax-year summary values/counts can be rebuilt/reconciled against source recognition facts.
- Source buckets remain distinguishable enough for reporting policy without Payment modifying the source records.
- Unsupported year/jurisdiction/currency/grain cases fail explicitly.
- No one can infer “tax filing required” from a hardcoded threshold merely because aggregation exists.

### Cluster Build-Plan Link

This Module-owned work fulfills the CL-03 architecture's declared **CL-10 Prize / Rewards → Payment SH-118 bridge** and participates in **CL-03 Feature 10A — Taxable-Value Intake and Tax-Reporting Coordination**, after Feature 10's Payment/Order bridge and before final hardening (CL-03-R017). This plan retains Payment's internal implementation sequence; the Cluster plan owns the coordination acceptance point.

### Dependencies

- Module Feature 01 contracts; Feature 04 source-effect/idempotency patterns where useful.
- SH-117/118 and SH-044/045/046/047/048.
- Source-owner public contracts/events for reportable Order earnings, PrizeWinning fair-market-value recognition, Reward recognition, or other approved sources.
- TaxProfile current-subject lookup from Feature 03 for later readiness context; TaxProfile is not required merely to ingest a recognized source value.
- **CL-03-R014 / UD-14:** minimum grain is tax subject + jurisdiction + tax year + currency, with durable source-event uniqueness/reversals. Current Prisma uniqueness is insufficient; exact subject representation and persistence/migration coverage remain prerequisites to production aggregation.
- **UD-15 tax reporting rule source is not required to aggregate value, but is required to set authoritative `reportingRequired`/threshold claims.**

### In Scope

- SH-118 `reportTaxableValue` public command.
- Runtime validation/source-type registry for approved reportable-value producers.
- Source recognition identity/idempotency.
- SH-117 aggregation into `TaxYearEarningsSummary` for the approved grain.
- Separate source-value buckets supported by current schema (`grossEarningsCents`, reward/prize/job buckets as applicable to approved source vocabulary).
- Counts and currency/year handling.
- Reversal/correction intake for a previously recognized source value under an explicit source correction identity.
- Reconciliation/backfill dry-run and repair.
- Tax-year summary query for authorized subject/admin/tax reporting worker.

### Out of Scope

- Prize drawing/winner selection/fulfillment lifecycle;
- Reward/point/redemption lifecycle;
- Order lifecycle/payment truth;
- determining universal tax thresholds/forms/regimes without approved versioned rules;
- filing submissions/recipients (Feature 09);
- currency conversion;
- a universal cross-domain money/value ledger;
- using `ProfessionalBalanceLedgerEntry` as the only source of tax reporting when source owner recognition semantics differ.

### Module-Owned Data

- `TaxYearEarningsSummary`.
- Potential durable tax-intake/source-recognition dedupe evidence if SH-118 cannot rely on a retained shared inbox alone. Any new model/constraint requires architecture approval rather than being invented during implementation.

### Public Interfaces

Implement/freeze:

- **SH-118 `reportTaxableValue`**;
- `getTaxYearEarningsSummary` / tax reporting status read used by Feature 09;
- internal/restricted tax-year reconciliation command.

SH-118 minimum input:

- subject User ID and ProfessionalProfile ID when source contract requires it;
- recognized value in minor units + currency;
- jurisdiction context/evidence reference;
- source Module/type/ID;
- source recognition event/version/date;
- valuation evidence reference for non-cash prize/reward values;
- idempotency key/source effect key;
- correction/reversal reference when applicable.

### Shared Operations Used

- **SH-118 — Payment public interface:** canonical source-to-tax intake. Local policy: allowed source types, subject/year/jurisdiction bucket mapping. **Do not build:** prize/reward logic inside Payment.
- **SH-117 — shared aggregation / separate truth:** source-safe yearly aggregation. Payment owns TaxYearEarningsSummary; source owners keep their own summaries/events. **Do not build:** cross-domain aggregate owner.
- **SH-044 — command idempotency:** direct SH-118 calls.
- **SH-045 — domain-event dedupe:** event-driven recognition producers.
- **SH-046 — Payment outbox:** tax-summary/reporting-requirement facts when they materially change.
- **SH-047/048 — jobs/retry:** reconciliation/backfill.
- **SH-051 — DB lock** or transaction/unique equivalent for concurrent same tax subject/jurisdiction/year/currency summary update.
- **SH-034/038 — telemetry:** safe aggregation job metadata.
- **SH-123 — owner reference validation** where source identity must be checked through owner contract. **No arbitrary polymorphic DB lookup.**

### Domain Logic

- The **source owner** decides that a value exists, its fair-market value/recognized amount, recognition date, and source lifecycle status.
- Payment decides how an accepted source value contributes to tax-year aggregation/reporting buckets.
- Recognition is idempotent. A correction is a new explicit correction/reversal fact linked to the prior source recognition; it must not mutate source owner's historical event.
- No cross-currency summation.
- Tax year is determined by an approved tax/calendar rule; if jurisdiction/time-zone/year-boundary rules are not established, constrain the supported regime rather than infer globally.
- `reportingRequired` and `thresholdMetAt` may be updated only when an approved versioned reporting rule exists. Otherwise aggregation can be complete while requirement state remains `unknown/pending review` under a documented constrained path.
- TaxProfile status does not alter whether a source value was recognized; it affects readiness to file/fulfill later.
- Prize/reward values reported for tax do not automatically become professional payout balance entries.

### Authorization / Compliance

- SH-118 is source-Module/system callable, not a public client arbitrary-value endpoint.
- Source owner identity/reference must be validated.
- Admin manual reportable-value adjustment, if allowed, requires authority, reason/evidence, audit, and explicit correction semantics.
- No raw tax identifiers or source-private payload in the tax intake.
- Valuation evidence is a safe reference, not raw document contents.

### Database / Transaction Behavior

**CL-03-R014:** aggregation must distinguish tax subject + jurisdiction + tax year + currency and preserve durable source-event uniqueness/reversals. Current Prisma unique `(userId, taxYear, currency)` is insufficient and must not be accepted as the final grain or used to discard jurisdiction. UD-14 still requires Payment approval of exact tax-subject representation and persistence design, followed by an approved forward migration before production aggregation is claimed. This reconciliation changes documentation only.

For each recognition:

```text
begin
→ claim source recognition/effect once
→ lock/find approved year-summary key
→ apply deterministic delta to correct source bucket/count
→ update approved requirement fields only if versioned rule is available
→ Payment outbox event if relevant
commit
```

A full reconciliation recomputes expected summary from source-owner recognized facts and compares before repair.

### Events / Jobs

Proposed minimized events:

- tax-year summary changed;
- tax-reporting requirement/threshold changed **only when approved rule semantics exist**.

Jobs:

- tax-year source reconciliation;
- backfill for approved historical source types;
- no filing submission job yet.

### Provider Integration

None required for aggregation itself. Provider tax-reporting APIs are Feature 09.

### UI / Admin Surface

Optional authorized tax-year summary/status read in professional/admin financial surfaces. Do not show raw source private data or make a tax/legal conclusion beyond approved rule state.

### Failure Behavior

- duplicate source recognition → replay/no double count;
- unknown source type → reject;
- invalid source owner/reference → reject;
- correction without prior recognized source → conflict/manual review;
- currency mismatch → reject;
- ambiguous tax-year/jurisdiction/grain under UD-14/15 → unavailable/review, not guessed;
- source owner unavailable during validation/reconcile → retry;
- reconciliation mismatch → report and repair only through idempotent source-effect command after validation.

### Tests

- SH-118 runtime validation and source registry;
- duplicate/concurrent recognition idempotency;
- correction/reversal arithmetic;
- source bucket mapping;
- currency/year boundaries for supported regime;
- no Prize/Reward/Order lifecycle writes;
- reconciliation dry-run/repair;
- CL-03-R014 minimum-grain isolation tests across subjects, jurisdictions, years, and currencies, including duplicate source recognition and reversal replay; unresolved subject/persistence cases remain blocked under UD-14;
- no hardcoded reporting threshold test when rule source absent;
- authorization/audit for manual adjustment if enabled;
- telemetry redaction.

### Documentation Updates

- Record CL-03-R014 minimum semantics and the remaining UD-14 subject-representation/persistence decisions; document migration coverage before production claims.
- Document approved SH-118 source type registry and value-recognition contract.
- Document whether `reportingRequired` remains disabled/pending until Feature 09 rule source.
- Progress tracker update.

### Acceptance Criteria

1. Approved source values enter Payment tax aggregation exactly once.
2. Source lifecycles and valuation meaning remain source-owned.
3. TaxYearEarningsSummary can be reconciled/rebuilt for enabled sources.
4. No currency mixing or silent jurisdiction/grain inference occurs.
5. Reporting-required/threshold fields are not asserted without approved versioned rules.
6. Tax intake does not create payout balance effects unless a separately approved financial source policy says so.

### Exit Gate

Feature 08 passes for its approved scope when SH-118 is contract-tested across at least one representative source owner, aggregation/reversal/reconciliation is idempotent, tax subject/jurisdiction/year/currency separation is proven under CL-03-R014, and no unapproved tax threshold/source lifecycle logic has been introduced. Production aggregation additionally requires approved subject representation and persistence/migration coverage under UD-14; contract-only evidence cannot claim database readiness.

---

## 09 — Tax Reporting Readiness, Submission, Recipients, and CL-10 Tax Fulfillment Gate

### Objective

Implement the legally supported portion of Payment's tax-reporting lifecycle: versioned reporting-rule evaluation, recipient readiness, submission/recipient records, optional provider filing adapter, and safe tax-fulfillment decisions for Prize/Reward consumers—while leaving unsupported jurisdictions/corrections/retention paths disabled.

### Observable Result

Depending on approved production scope:

- Payment can determine whether an aggregated subject/year is reporting-required using an explicit versioned rule source rather than hardcoded assumptions.
- TaxProfile/TaxDocument readiness can block a recipient from filing/approved tax fulfillment with safe reasons.
- A reporting submission can be prepared with deterministic recipient snapshots.
- If a reporting provider/regime is approved, submission/provider callbacks update canonical submission/recipient states idempotently.
- If provider/legal rule is **not** approved, the system exposes draft/manual/review state and the automated path is unreachable.
- Prize/Reward owner can ask Payment for tax fulfillment readiness without Payment changing Prize/Reward truth.

### Cluster Build-Plan Link

Completes the Module's declared tax-reporting / prize-tax responsibility for the approved scope coordinated by **CL-03 Feature 10A** (CL-03-R017). It is subordinate to the Cluster plan: automated filing is not a prerequisite for unrelated CL-03 features if legal/provider decisions are still gated, but **production claims for tax reporting must not exceed the approved Feature 09 scope**.

### Dependencies

- Module Features 03 and 08.
- SH-117/118 source aggregation.
- Privacy/Audit/Notification/Ops contracts.
- Approved versioned tax-reporting rule source resolving **UD-15** for each enabled regime/jurisdiction.
- Approved `TaxReportingSubmissionStatus` / `TaxReportingRecipientStatus` ownership (PT-01).
- **UD-20 correction/replacement filing semantics** before automated corrections are enabled.
- Approved tax-reporting provider adapter/credentials for any automated filing path.
- UD-03 retention policy reviewed for records that provider filing/destructive Privacy affects.

### In Scope

For approved regimes only:

- versioned tax reporting rule resolution/evaluation;
- set/reconcile `reportingRequired` and threshold evidence in year summary;
- TaxProfile/TaxDocument readiness composition for reporting/fulfillment;
- `TaxReportingSubmission` draft/ready/submitted/accepted/rejected/failed lifecycle;
- `TaxReportingRecipient` pending/included/filed/blocked/failed lifecycle;
- deterministic recipient snapshot construction;
- optional provider filing adapter + callback/reconciliation;
- proposed `evaluateTaxFulfillmentReadiness` query for Prize/Reward or use SH-019 with a tax-specific action if that contract is approved;
- safe notifications for action-required/filing result;
- admin/manual review path using approved authority.

### Out of Scope

- tax/legal advice;
- inventing 1099/DAC7/other thresholds/forms from memory;
- unsupported jurisdictions/regimes;
- automated corrected/replacement filings without UD-20;
- Prize/Reward lifecycle/fulfillment mutation;
- Privacy retention-exemption ownership;
- raw tax document binary storage;
- consumer-facing tax form generation unless an approved provider/record contract explicitly includes it.

### Module-Owned Data

- `TaxYearEarningsSummary` reporting-required/regime fields under approved rule;
- `TaxReportingSubmission` / proposed owned `TaxReportingSubmissionStatus`;
- `TaxReportingRecipient` / proposed owned `TaxReportingRecipientStatus`;
- `TaxProfile` / TaxDocument readiness input;
- provider filing references in Payment-owned reporting records.

### Public Interfaces

- `getTaxReportingStatus`;
- `prepareTaxReportingSubmission`;
- `submitTaxReportingSubmission` for approved providers/regimes;
- `reconcileTaxReportingSubmission` restricted/system;
- proposed `evaluateTaxFulfillmentReadiness(subject, sourceContext)` **or** an approved SH-019 action variant;
- existing SH-118 source intake remains unchanged.

The consuming Prize/Reward Module receives a decision/evidence reference, not permission to alter Payment status.

### Shared Operations Used

- **SH-117/118 — aggregation/intake:** source values remain separate owner truth.
- **SH-053 — lifecycle mechanism:** submission/recipient transitions; Payment owns exact graph.
- **SH-044 — command idempotency:** prepare/submit/manual actions.
- **SH-046 — outbox:** reporting/recipient status facts.
- **SH-047/048 — jobs/retry:** filing/reconciliation.
- **SH-059/060/061/062 — provider callback/reconciliation** if provider filing callback path uses Stripe/another signed provider. Owner-specific event truth required; do not assume Stripe event record for non-Stripe provider without an approved dedupe model.
- **SH-041 — Notification:** action-required/submission result.
- **SH-029/030 — Audit/access:** manual filing/admin tax access.
- **SH-095/096/097/070/098 — Privacy/retention/provider deletion:** later execution must respect tax retention.
- **SH-034/037/038 — Ops:** provider/job visibility.

### Domain Logic

Versioned rule contract for each enabled reporting regime must include at least:

- rule ID/version;
- effective year/date range;
- jurisdiction;
- reporting regime/form category;
- threshold/transaction-count conditions if legally applicable;
- subject/category applicability;
- currency/valuation handling assumptions;
- required tax-profile/document state;
- source/value buckets included/excluded;
- filing deadline/configuration where needed;
- legal/compliance provenance/approval reference.

Do not mutate an old summary/submission under a newer rule without explicit reconciliation/version behavior.

Recipient readiness:

```text
year summary says reporting applies under rule version
→ resolve current TaxProfile/required TaxDocument
→ if incomplete: recipient blocked + safe remediation
→ if ready: snapshot reportable amount/count/currency/subject refs
→ submission ready
→ submit through approved provider or manual/legal-reviewed path
→ provider result maps to canonical submission/recipient state
```

Prize/Reward tax fulfillment decision returns only Payment-owned tax blockers/evidence. Prize/Sweepstakes decides its own fulfillment and may use ComplianceHold under its own policy.

### Authorization / Compliance

- Tax profile/reporting data is sensitive; SH-014 where approved sensitive surfaces require it and SH-030 for access.
- Filing/admin actions are restricted and audited.
- Provider filing payload minimized; tax identifiers should be provider-hosted/tokenized where possible.
- Exact retention is legal-gated; do not auto-delete filed tax evidence.
- Do not represent a legal tax obligation as one generic `taxApproved` boolean.

### Database / Transaction Behavior

- Submission preparation snapshots recipients deterministically from approved year-summary/rule version and prevents duplicate recipient inclusion.
- Current schema lacks explicit unique submission version/recipient key; add approved DB constraints/migration if required for enabled production path rather than relying on query-then-insert.
- Provider submission intent is durable before external side effect.
- Callback/reconciliation applies expected-state transition and outbox atomically with local record change where possible.
- Accepted filing proof is immutable historical evidence; correction creates an approved correction/replacement path, never rewrites accepted history.

### Events / Jobs

- reporting requirement changed;
- submission status changed;
- recipient status changed;
- filing worker/reconciliation;
- deadline/action-required reminder only with approved scheduling semantics;
- no generic “tax cron” outside shared queue.

### Provider Integration

Provider-neutral `TaxReportingProviderPort`. If no provider is canonically approved, keep adapter interface + manual/draft path, feature-gate `submit` in production, and report that automated filing is not complete.

For a non-Stripe provider, do **not** reuse `ProcessedStripeEvent`; provider-event dedupe requires an owner-specific record/ruling for that provider.

### UI / Admin Surface

Professional:

- safe year/reporting readiness;
- tax-profile action needed;
- filing/accepted/rejected status where legally/product appropriate.

Admin/legal/Ops:

- submission/recipient safe metadata, rule version, provider refs, retry/reconcile action;
- no raw TIN/SSN/provider sensitive payload.

### Failure Behavior

- no approved rule for regime/year → `policy_unresolved`, automated reporting disabled;
- incomplete TaxProfile/documents → recipient blocked/requires input, source value remains recorded;
- duplicate submission/recipient preparation → replay/no duplicate;
- provider transient → retry;
- provider rejected → canonical rejected/failed + safe reason; no blind resubmission under unknown correction semantics;
- correction requested while UD-20 unresolved → unsupported/manual legal review;
- Privacy deletion conflicts with retention → SH-097 retain facts, Privacy exemption; no destructive deletion;
- Prize/Reward consumer tries to send lifecycle mutation through Payment → contract rejection.

### Tests

- versioned rule fixtures for each enabled regime/year;
- no-rule path disabled;
- threshold/count/value boundary tests from approved fixtures;
- TaxProfile/TaxDocument blocked/ready recipient logic;
- submission/recipient duplicate/concurrency tests;
- provider mapping/callback/reconciliation if enabled;
- correction unsupported test until UD-20 resolved;
- authorization/step-up/access audit;
- Notification payload sensitivity;
- Privacy retention interaction;
- CL-10 contract: tax decision consumed without Payment mutating Prize/Reward truth.

### Documentation Updates

- Record approved rule source/schema and enabled regime versions, resolving UD-15 for scope.
- Record provider selection/enabled filing path.
- Record UD-20 correction semantics if approved; otherwise document production-disabled correction.
- Record tax-fulfillment public decision contract.
- Progress tracker update.

### Acceptance Criteria

1. Every asserted reporting obligation is traceable to an approved versioned rule.
2. TaxProfile/doc readiness and source reportable value remain distinct truths.
3. Submission/recipient state is canonical Payment truth and replay-safe.
4. Automated provider filing is enabled only when provider/rule/dedupe/reconciliation are approved and tested.
5. Prize/Reward consumer receives a Payment decision without lifecycle ownership transfer.
6. Unsupported correction/retention/jurisdiction paths remain explicit and disabled.

### Exit Gate

Feature 09 passes when the enabled tax-reporting scope is rule-versioned, replay-safe, retention-aware, provider-tested where applicable, and all non-enabled legal/provider/correction paths are demonstrably unreachable rather than implicitly “supported.”

---

# Phase 6 — Module Integration and Governance

## 10 — Cross-Module Contract Proof, Privacy, Audit, Notification, and Operational Completion

### Objective

Prove the completed Payment capability collaborates correctly with its most important owners/consumers and complete Payment's Privacy, Audit, sensitive-access, Notification, Hold, and Observability obligations without reaching into neighboring source tables.

### Observable Result

- Professional Eligibility consumes SH-019 through contract tests and never reads Payment/profile compatibility fields.
- Order payment/refund/tax handoff works only through Order public commands.
- Review/Dispute/ComplianceHold effects change Payment money behavior without Payment owning the case/hold.
- Prize/Reward source values enter SH-118 without Payment owning source outcomes.
- Privacy can enumerate and execute Payment-owned targets with retention-aware results.
- Every mandatory sensitive financial access creates the expected SH-030 proof.
- Payment business notifications route through Notification with safe payloads.
- Integration failures/jobs are visible in Ops without becoming Payment status.
- No public Search or foreign direct-Prisma dependency is introduced.

### Cluster Build-Plan Link

This is the Module's explicit **integration phase**, supporting **CL-03 Feature 11 — Readiness Change Propagation and Neighboring-Cluster Integration** and Payment's portion of **CL-03 Feature 12 — Privacy, Moderation/Hold, Audit, Sensitive Access, and Operational Case Completion**.

### Dependencies

- Module Features 01–09 for whichever paths are in current production scope.
- Stable owner contracts for Professional Eligibility, Order, Review/Dispute, Hold, Privacy, Audit, Notification, Ops, and CL-10 sources.
- SH-095/096/097 Privacy protocol.
- Retention policy/UD-03 disposition for destructive paths; unresolved retention may remain a documented blocker with non-destructive executor behavior.
- Media SH-087 only if Payment file attachment workflow actually exists.

### In Scope

Cross-Module contract/integration tests and runtime wiring for:

- Professional Eligibility ↔ SH-019;
- Order ↔ Payment payment/tax/refund rail;
- Review/Dispute/Hold → Payment payout/ledger consequences;
- Prize/Reward → SH-118 and tax fulfillment decision;
- Payment → Notification SH-041;
- Payment → Audit SH-029/030;
- Payment → Ops SH-034/037/038;
- Privacy → Payment SH-096 inventory / SH-097 retention facts / SH-095 execution / SH-070 provider delete / SH-098 anonymization;
- optional Media-protected tax/financial doc access if approved;
- event replay/out-of-order handling across these contracts.

### Out of Scope

- rewriting neighboring Modules;
- generic platform integration/saga framework;
- Search indexing of financial data;
- new provider/product lanes introduced only for integration testing;
- destructive privacy behavior whose retention policy is unresolved;
- unresolved legal paths being declared compliant merely because a stub returns success.

### Module-Owned Data

All implemented Payment-owned records may participate. No new cluster-wide integration table is created. Shared inbox/outbox/job/audit/privacy records remain with platform/owning Modules.

### Public Interfaces

Freeze/version current production-used Payment contracts:

- SH-019;
- onboarding/status queries;
- balance/payout queries and commands;
- Order payment/tax/refund rail contracts;
- SH-118;
- tax reporting/tax fulfillment contracts where enabled;
- Payment Privacy executor;
- Payment event schemas.

Document retry/idempotency/conflict/unavailable behavior and deprecation rules.

### Shared Operations Used

- **SH-001/002/014 — Identity/Authority:** protect all interactive/admin integration paths.
- **SH-011/012/013 — Hold:** canonical stop signs only; no local replacement.
- **SH-019 — Payment:** contract proof with consumers.
- **SH-029/030 — Audit:** required generic action/sensitive-access evidence.
- **SH-034/037/038 — Ops:** safe telemetry/failures/jobs.
- **SH-041 — Notification:** delivery request only.
- **SH-045/046 — inbox/outbox:** replay-safe cross-Module facts.
- **SH-047/048 — async retry:** owner-handoff/reconciliation.
- **SH-070 — provider deletion:** under Privacy instruction.
- **SH-087 — Media signed access:** only if approved Payment document exists.
- **SH-095/096/097/098 — Privacy:** enumerate/retention/execute/anonymize; no Payment PrivacyRequest.
- **SH-108 — refund:** Order coordinates; Payment rail only.
- **SH-117/118 — tax source bridge:** source lifecycle remains external.
- **SH-123 — target owner validation:** no polymorphic foreign DB read.

### Domain Logic

- Every consumed event re-queries current owner truth before an irreversible action when stale event payload could be unsafe.
- Professional Eligibility receives Payment decision facts, not Payment tables.
- A lost financial readiness condition may cause Payment to deny payout; it does not directly deactivate ProfessionalProfile/Offering. Those owners decide their consequences under UD-01/action policy.
- Dispute/Hold source facts create only approved Payment ledger/payout consequences.
- Order refund/payment provider effects and ledger effects have exactly one authoritative source path to prevent double application.
- Privacy retention result distinguishes erasable/anonymizable/retained/provider-deletable records.
- Notification intent is derived from committed Payment fact; delivery state is not business state.
- Ops retry/reconcile invokes owner commands, not status SQL patches.

### Authorization / Compliance

Security matrix must verify:

- professional self access vs unrelated User;
- support/admin authority scope;
- step-up coverage for balance/account/tax/payout actions;
- SH-030 for required allowed/denied/redacted accesses;
- Privacy system actor only for executor calls;
- provider/system actor scopes;
- no raw sensitive data in notifications/events/ops/audit.

### Database / Transaction Behavior

- No new foreign-table joins are accepted as “integration.”
- Local Payment write + outbox remains atomic.
- Inbound source events use shared inbox/dedupe with local effect transaction.
- Foreign owner command failure is retried/reconciled separately; no direct patch.
- Privacy execution is idempotent by Privacy target/job/idempotency key.
- Retained records preserve referential integrity and return exemption/evidence references.

### Events / Jobs

- Contract-test Payment event schemas and inbox replay.
- Reconciliation jobs for provider/Order/ledger/tax/reporting paths.
- Privacy execution may be invoked by Privacy workers but Payment does not own scheduling.
- Notification retries stay Notification-owned.

### Provider Integration

Verify provider resources can be reconciled and, where legally permitted, deleted/revoked through Payment adapter under SH-070. No Privacy direct provider calls.

### UI / Admin Surface

Use existing professional financial and admin/Ops surfaces only. Integration test harness may be non-UI. If UI exists, verify:

- safe blocked/remediation states;
- no raw provider/tax/bank data;
- no force-success controls that bypass owner transitions;
- retry/reconcile actions are authority/audit protected.

### Failure Behavior

- neighbor unavailable → retry/unavailable; no direct DB bypass;
- stale event → current owner query wins;
- duplicate/out-of-order event → one safe local effect or no-op;
- Notification unavailable → Payment fact remains committed; delivery retries externally;
- Audit mandatory write failure → follow root audit failure policy; do not silently claim required proof;
- Privacy destructive instruction with unresolved retention → retained/blocked result, not deletion;
- provider delete unavailable → retryable/retained result to Privacy;
- Search request is not applicable for Payment finance; no finance data indexed.

### Tests

- Professional Eligibility SH-019 contract/E2E;
- Order payment/refund contract proving no direct writes;
- Review/Dispute/Hold money-consequence contract;
- Prize/Reward SH-118 contract;
- event replay/out-of-order tests;
- step-up + SH-030 coverage matrix;
- SH-029 audit action matrix;
- Notification payload sensitivity tests;
- Privacy enumerate/export/anonymize/retain/provider-delete tests;
- TaxDocument retention/cascade regression;
- Ops telemetry redaction and IntegrationFailure/QueueJob separation;
- architecture test preventing foreign Prisma/search/provider-delivery imports.

### Documentation Updates

- Freeze production-used public contract versions/reason codes/event schemas.
- Update Privacy subject-data inventory/retention map.
- Record any retention paths remaining disabled under UD-03.
- Update integration dependency matrix and progress tracker.

### Acceptance Criteria

1. Every major inbound/outbound boundary has a contract test; no integration is accepted merely because a foreign Prisma table is reachable.
2. SH-019, Order payment/refund, Hold/Dispute, and SH-118 preserve source ownership.
3. Sensitive access/step-up/audit coverage is complete for enabled financial surfaces.
4. Privacy can enumerate/execute Payment-owned targets idempotently and safely retain legal-gated records.
5. Notifications and Ops use shared owners and contain no sensitive payload leakage.
6. Event replay/out-of-order behavior cannot duplicate money/tax/provider effects.
7. No public Search or direct Typesense behavior is introduced.

### Exit Gate

Feature 10 passes when the Module integration matrix is green, Payment's CL-03 Feature 11/12 obligations are proven through public contracts, Privacy/Audit/Notification/Ops boundaries are complete for enabled scope, and every unresolved destructive/legal path is explicitly blocked or out of production scope.

---

# Phase 7 — Module Hardening and Production Verification

## 11 — Security, Concurrency, Provider Recovery, Backfill, Retention, and Production Hardening

### Objective

Adversarially harden every enabled Payment workflow for production: races, replay, provider outage/ambiguity, reconciliation, migration/backfill, sensitive-data access, privacy retention, telemetry redaction, performance, and legal-gated path enforcement.

### Observable Result

- Critical financial workflows remain deterministic under duplicate requests, webhook replay/out-of-order delivery, provider outage, and worker retry.
- Payout overspend and duplicate transfer/economic effects are concurrency-tested.
- Operators can dry-run reconciliation/backfills and see dead-lettered work without editing business truth in Ops tables.
- Sensitive data is absent from logs/events/notifications and protected by server authority/step-up/access proof.
- Privacy retention/provider deletion behavior is tested for approved scope.
- Unsupported legal/provider/payment-attempt/partial-refund/tax-correction paths are feature-gated unreachable.
- Production readiness report lists all enabled providers, migrations, unresolved blockers, recovery plans, and passed exit gates.

### Cluster Build-Plan Link

Implements Payment's portion of **CL-03 Feature 13 — Security, Reliability, Reconciliation, Backfill, Compliance, and Production Hardening**.

### Dependencies

- Module Features 01–10 complete for production-enabled scope.
- Root deployment/security/observability/performance standards.
- Current Module + Cluster unresolved-decision registers reviewed.
- Production provider configuration/secrets for enabled adapters.
- Data migration/backfill plans for any approved schema changes from PT-02, tax uniqueness, or other feature rulings.

### In Scope

- concurrency/idempotency stress tests;
- provider replay/out-of-order/timeout/ambiguous result testing;
- reconciliation dry-run/repair for KYC/account/payout/payment/tax/tax reporting;
- ledger and tax-year backfill/rebuild validation;
- sensitive-data redaction audit;
- authorization/step-up/RLS alignment where root architecture uses RLS;
- DB index/constraint review for hot/critical paths;
- dead-letter/manual recovery runbooks;
- privacy retention/provider deletion verification;
- destructive migration/backfill/recovery checks;
- performance/load checks for webhook, balance, payout, reconciliation, tax queries;
- feature flags/configuration that disable unresolved provider/legal cases;
- final public-contract/version freeze/deprecation notes;
- production readiness report.

### Out of Scope

- new product lanes/providers introduced solely during hardening;
- solving unrelated Cluster architecture;
- legal assumptions not supplied by approved policy;
- speculative redesign of Order/Payment models without demonstrated blocker and architecture approval;
- making unsupported chargeback/partial-refund/correction paths “work” with generic adjustment hacks.

### Module-Owned Data

Review all Payment-owned models for:

- indexes on subject/status/provider refs/time scans;
- uniqueness/idempotency constraints;
- append-only protections;
- FK/delete behavior under legal retention;
- payout/account/tax status query performance;
- approved source-effect identity;
- tax calculation/provider transaction uniqueness where enabled;
- reporting submission/recipient uniqueness where automated filing enabled.

Any destructive migration must include inventory, forward migration, backfill, validation report, and recovery/rollback plan. Provider/Search/Ops state cannot be used to reconstruct missing domain truth unless it is explicitly valid source evidence.

### Public Interfaces

Freeze/version all production-used Payment contracts:

- request/response schema versions;
- reason-code namespaces;
- pagination/limits for sensitive history/admin views;
- idempotency keys/fingerprints;
- conflict/unavailable behavior;
- provider retry/reconciliation semantics;
- event schema versions;
- deprecated compatibility fields/aliases.

### Shared Operations Used

Hardening verifies correct use rather than creating alternatives:

- **SH-001/002/014** auth/authority/step-up;
- **SH-011–013** holds;
- **SH-029/030/034/037/038** audit/sensitive access/telemetry/Ops;
- **SH-044/045/046** command/event idempotency and outbox/inbox;
- **SH-047/048** jobs/retry/dead-letter;
- **SH-051/052/053/056** DB concurrency/lifecycle/reservation;
- **SH-055** expiry scheduling where enabled;
- **SH-059–063** provider security/dedupe/mapping/reconciliation/snapshot;
- **SH-070/095–098** Privacy/provider deletion/anonymization;
- **SH-108/109** refund/historical snapshot boundary;
- **SH-117/118** tax source aggregation;
- **SH-123** owner reference validation.

**Do not build** a Payment-owned auth layer, queue, retry system, webhook log, audit store, incident system, privacy workflow, signed-file system, Notification provider, Search client, or generic cross-domain reconciler.

### Domain Logic

Adversarial review includes:

- SH-019 stale/current dimension behavior;
- KYC/TaxProfile current record ambiguity and provider event order;
- payout account restriction changes between request and execution;
- multiple active holds;
- balance availableAt/time-bound effects;
- concurrent request/reservation/release/reversal;
- provider transfer ambiguous outcome;
- Order payment result vs Order command outage/conflict;
- tax calculation stale Order/location/item context;
- duplicate/missing sales-tax transaction;
- SH-118 duplicate/correction/rebuild;
- tax reporting rule version changes and accepted filing immutability;
- Privacy retention/deletion after provider/account status changes;
- admin/manual reconciliation source provenance.

### Authorization / Compliance

Final security review must verify:

- no sensitive route/action relies on UI only;
- step-up binding includes correct actor/action/target/expiry;
- support/admin cannot view raw sensitive data merely by role;
- mandatory access events are generated;
- raw bank/tax/KYC/provider data absent from normal tables/logs/events/notifications;
- provider secrets never enter client or DB business records;
- tax/financial retention paths match approved policy; unresolved retention destroys nothing;
- no custom tax/legal rules were hardcoded outside approved versioned rule fixtures.

### Database / Transaction Behavior

Run stress/verification for:

- simultaneous provider event claims;
- same command idempotency key with same/different fingerprint;
- duplicate source domain event;
- payout profile+currency reservation lock;
- transfer unique idempotency;
- concurrent payout result/reversal;
- sales-tax finalization/recording races;
- tax-year concurrent source intake;
- tax reporting duplicate recipients/submissions if enabled;
- local state + outbox atomicity.

Use database-enforced constraints/locks/serializable transactions, not process memory.

### Events / Jobs

- replay and out-of-order event suites;
- worker lease/retry/dead-letter tests;
- provider reconciliation schedules/admin triggers;
- backfill dry-run + resumability/idempotency;
- no source event/payload reliance after retention if the necessary evidence was not durably snapshotted.

### Provider Integration

For **every live provider/capability**, production readiness report must list:

- credential/config owner;
- signature verification if callbacks exist;
- owner-specific provider-event dedupe truth;
- accepted event types;
- mapping version;
- idempotency-key behavior;
- timeout/retry policy;
- reconciliation endpoint/job;
- provider deletion behavior under Privacy;
- operational health/alerting;
- sandbox/integration test coverage.

A provider path missing one required protection remains disabled.

### UI / Admin Surface

Production financial/admin/Ops views must:

- expose only minimum safe metadata;
- make reconciliation/retry explicit and audited;
- not include “force paid/verified/accepted” shortcuts that bypass domain command policy;
- not show raw webhook/provider/tax/bank data for debugging convenience;
- clearly distinguish pending/requires input/review/provider unavailable/business denied states.

### Failure Behavior

- provider outage → canonical pending/current truth + retry/reconciliation, no false success;
- dead-letter → visible Ops case, business status remains owner truth;
- duplicate/out-of-order event → no repeated irreversible effect;
- failed migration/backfill validation → deployment/feature enablement blocked;
- unresolved architecture/legal decision → production path feature-gated off;
- telemetry redaction failure fixture → test/build fail;
- reconciliation detects irreconcilable amount/account/source mismatch → manual review/incident, no automated patch;
- Privacy destructive path lacks retention ruling → retained/blocked outcome.

### Tests

Required final suite:

- typecheck/lint/build;
- all Module unit/integration/contract/provider/concurrency/security/privacy tests;
- webhook replay/out-of-order fuzz/fixtures;
- payout concurrency/load tests;
- ledger reconciliation/backfill tests;
- payment/Order outage/conflict reconciliation;
- tax calculation/payment/refund supported-path E2E;
- SH-118/tax reporting enabled-scope E2E;
- Privacy retention/provider deletion E2E for approved cases;
- redaction/sensitive-data leak regression across logs/events/notifications/audit;
- migration validation queries;
- performance checks on critical indexes/queries/workers;
- architecture dependency tests preventing foreign direct Prisma/shared-infrastructure duplication.

### Documentation Updates

- Production readiness report.
- Progress tracker with every Module feature PASS/FAIL.
- Provider support matrix.
- Migration/backfill/recovery runbooks.
- Final unresolved decision disposition: `resolved`, `production blocker`, or `explicitly out of production scope`.
- Public contract/version/deprecation docs.
- Privacy/retention support matrix.
- Architecture only if a binding ruling legitimately changed.

### Acceptance Criteria

1. Every live provider path has signature/dedupe/mapping/idempotency/reconciliation/telemetry and Privacy behavior where applicable.
2. No replay/race can duplicate payout, ledger, Order command, sales-tax transaction, or tax-value effect.
3. No production path relies on `stripeReady`, provider/Search/Audit/Ops state as domain truth.
4. Sensitive finance is server-authorized, step-up protected, and access-audited where required.
5. Privacy/retention behavior is tested; unresolved destructive paths are disabled.
6. Backfills/reconciliation are dry-run capable, resumable/idempotent, and source-truth based.
7. Unsupported payment-attempt/chargeback/partial-refund/tax-correction/legal paths are not accidentally reachable.
8. All required tests and production readiness documentation pass.

### Exit Gate

The Payment / Payout / Tax Module is production-ready only when:

1. Module Features 01–10 exit gates remain passing for enabled scope;
2. CL-03 Feature 13 Payment hardening criteria pass;
3. every live provider passes the complete provider support matrix;
4. all critical financial commands/effects are idempotent and concurrency-tested;
5. payout cannot overspend or double-transfer;
6. Order ownership remains intact under provider failure/replay/reconciliation;
7. sensitive data/Privacy/retention controls pass security/compliance tests;
8. every unresolved decision is explicitly `resolved`, `production blocker`, or `out of production scope`;
9. migrations/backfills have validated recovery plans;
10. typecheck, lint, build, unit, integration, contract, provider, concurrency, security, privacy/compliance, and critical E2E suites pass;
11. production readiness report and progress tracker are updated.

---

# Module Integration Phase

**Phase 6 / Feature 10 is the explicit Module integration phase.** It proves Payment collaborates with:

- Professional Eligibility through SH-019;
- Transaction / Order through payment/tax/refund public contracts;
- Review / Dispute and Compliance Hold through source decisions/effects;
- Prize / Rewards through SH-118 and tax-readiness contracts;
- Identity / Role / step-up;
- Audit / sensitive access;
- Notification;
- Privacy;
- Observability / Ops;
- Media only when a real Payment document workflow exists.

Integration is proven through contracts/events and owner commands. Direct foreign Prisma access does not count as integration and fails the exit gate.

---

# Module Hardening Phase

**Phase 7 / Feature 11 is the hardening phase.** It covers only Payment-relevant production concerns:

- state transition races;
- command/provider/source-event idempotency;
- webhook replay/out-of-order behavior;
- payout reservation/overspend prevention;
- ambiguous provider money movement;
- provider outage and reconciliation;
- ledger/tax-year rebuild/backfill;
- sales-tax calculation/finalization/refund integrity;
- tax reporting rule/provider gating;
- security, step-up, sensitive access, and telemetry redaction;
- privacy/retention/provider deletion;
- migrations/indexes/performance;
- unresolved path feature gating;
- final contract/provider support freeze.

It must not introduce new product scope merely to close a checklist.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | 01 Payment Module Contracts, Validation, and Data-Ownership Baseline; 02 Verified Stripe Ingress, Provider Translation, and Reconciliation Shell |
| 2 | Financial Onboarding and Readiness | 03 KYC, Tax Profile, Payout Account, and SH-019 Financial Readiness |
| 3 | Professional Balance and Payout | 04 Append-Only Professional Balance Projection; 05 Payout Request, Atomic Reservation, Transfer, and Reversal |
| 4 | Transaction Payment and Sales-Tax Bridge | 06 Provider-Backed Sales-Tax Calculation for an Authoritative Order; 07 Payment / Refund Rail, Tax Finalization, and Order Handoff |
| 5 | Tax Reporting and Reportable-Value Intake | 08 SH-118 Taxable-Value Intake and Tax-Year Aggregation; 09 Tax Reporting Readiness, Submission, Recipients, and CL-10 Tax Fulfillment Gate |
| 6 | Module Integration and Governance | 10 Cross-Module Contract Proof, Privacy, Audit, Notification, and Operational Completion |
| 7 | Module Hardening and Production Verification | 11 Security, Concurrency, Provider Recovery, Backfill, Retention, and Production Hardening |

**Total numbered Module features: 11**

The Module numbering is local to `payment_payout_tax`. It does not renumber or supersede the CL-03 build plan. Cluster links in each feature determine when the Module slice may be implemented/claimed complete.

---

# Module Execution Pattern

Before implementing each numbered Module feature:

1. Read root project overview.
2. Read root architecture and code/security/data standards.
3. Read Canonical Shared Operations Registry.
4. Read CL-03 architecture and build plan.
5. Read this Module architecture and implementation plan.
6. Read current Prisma schema/migrations for records the feature touches.
7. Read public-interface sections for every direct dependency owner.
8. Review Module/Cluster unresolved decisions affecting the feature.
9. Confirm the prior Module exit gate and relevant Cluster milestone prerequisites.
10. Write the concise **Required Feature Implementation Specification** for only this feature.
11. Confirm source owner, records, contracts, SH operations, permissions, provider path, events/jobs, concurrency/idempotency, tests, and disabled paths.
12. Implement only this feature and approved sub-slices.
13. Run root-required typecheck/lint/build/tests/migrations/checks.
14. Verify happy path plus negative, race, replay, provider-outage, and authorization paths applicable to the feature.
15. Update progress/completion report.
16. Update architecture only when a binding decision legitimately changed.
17. Record unresolved risks, production-disabled paths, migration/backfill needs, and deferred work.

The next numbered feature does not begin until the current exit gate is **PASS**, unless the plan is explicitly amended because an architecture blocker changes sequencing.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise specification for **that feature only** containing:

- **Feature / Cluster link** — Module feature number/name and CL-03 milestone supported.
- **Objective** — exact capability being added.
- **Observable result** — user/admin/worker/consumer behavior that proves completion.
- **Dependencies** — prior Module features, Cluster feature prerequisites, public owner contracts, SH operations, providers, unresolved rulings.
- **In scope** — exact behavior/data/interfaces.
- **Out of scope** — explicit ownership/scope exclusions and disabled unresolved paths.
- **Owned data affected** — Payment models/enums/indexes/migrations/events/projections/snapshots.
- **Public contracts** — commands, queries, events, Privacy/provider ports and versions.
- **Shared operations consumed** — permanent `SH-###`, canonical owner, invocation point, local policy, prohibited duplicate.
- **Permissions/compliance** — actor/system context, authority, profile/Order relationship facts, step-up, holds, tax/legal/privacy gates.
- **Primary workflow** — ordered happy path with owner handoffs.
- **Provider integration** — adapter, credentials/config, signature/dedupe/mapping/idempotency/reconciliation, supported events.
- **Jobs/events** — outbox/inbox, job payload/idempotency, retry/dead-letter, notification/audit/ops effects.
- **Idempotency/concurrency** — semantic command/source/provider key, DB constraint/lock/transaction, replay result.
- **Error behavior** — validation, authority, step-up, conflict/stale state, provider transient/terminal/ambiguous, unsupported/legal-gated, partial completion.
- **UI/admin states** — only if actual product surface exists.
- **Tests** — exact unit/integration/contract/provider/concurrency/security/privacy/E2E categories and critical cases.
- **Acceptance criteria** — concrete pass/fail conditions tied to the exit gate.
- **Documentation updates** — progress plus architecture/contract/shared-operation updates required if a deferred decision is legitimately settled.

Do **not** pre-write giant coding specs for all 11 features. The next feature specification must reflect the actual repository and completion state at implementation time.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed** — Module feature number/name and Cluster link.
- **Files added**.
- **Files changed**.
- **Database changes**.
- **Migrations** — including constraint/index/backfill/rollback notes.
- **Dependencies added/changed**.
- **Module public interfaces added/changed** — names + versions/reason-code changes.
- **Shared Operations reused** — by exact `SH-###`; identify any planned SH dependency still stubbed/unavailable.
- **Events/jobs added/changed** — event schemas, outbox/inbox, job keys, retry/dead-letter behavior.
- **Provider adapter changes** — enabled events, mappings, idempotency, reconciliation, provider configuration; or explicit disabled provider path.
- **Authorization / step-up / hold changes**.
- **Audit / sensitive-access / Notification / Ops changes**.
- **Privacy / retention changes**.
- **Tests added/changed**.
- **Commands run** — typecheck/lint/test/build/migration/validation commands and results.
- **Manual / contract / workflow verification**.
- **Documentation updated**.
- **Assumptions** — only architecture-approved assumptions.
- **Approved Proposed Rulings used**.
- **Unresolved decisions encountered**.
- **Known failures**.
- **Remaining risks**.
- **Deferred work / production-disabled paths**.
- **Exit-gate result:** `PASS` or `FAIL`.
- If `FAIL`, list the exact failed exit-gate criteria and do not claim the feature complete.

---

# Final Module Quality Gate

Before declaring `payment_payout_tax` implementation complete, verify:

1. Every Payment source record/lifecycle has one owner and no foreign truth was absorbed.
2. Order is still transaction truth and every Order/RefundStatus mutation occurs through Order public contracts.
3. SH-019 is dimensioned and no `canPayout`/`stripeReady`/TaxProfile-as-sales-tax shortcut exists.
4. Provider objects are inputs/evidence only; every live callback has signature, owner dedupe, translation, idempotency, reconciliation, and telemetry.
5. `ProcessedStripeEvent`, domain event inbox, financial ledger, Audit, and Ops records remain separate truths.
6. Professional balance is append-only/rebuildable and source effects are durably idempotent.
7. Payout request/transfer are separate, step-up/hold/readiness gated, concurrency-safe, and provider-replay safe.
8. Sales tax is provider-backed, bound to exact Order/version, and separate from seller TaxProfile.
9. Unsupported partial refund/multi-attempt/chargeback/tax-correction paths remain explicit or have approved models/tests.
10. SH-118 tax intake preserves Prize/Reward/Order source ownership and tax aggregation is replay-safe.
11. Automated tax reporting is enabled only for approved versioned rules/provider/dedupe/correction scope.
12. Cross-Module reads/writes use public contracts/events rather than direct foreign Prisma access.
13. Audit, sensitive access, Notification, Privacy, Media, Search, and Ops remain with their canonical owners.
14. Sensitive financial data is absent from logs/events/notifications/public Search and protected by server authority/step-up/access proof.
15. Privacy retention/provider deletion is tested; unresolved destructive paths are disabled.
16. All migrations/backfills/reconciliation have validation and recovery plans.
17. Every Module feature has a PASS completion report for enabled production scope.
18. The relevant CL-03 build-plan exit gates remain passing.
19. Every unresolved architecture item is resolved, a production blocker, or explicitly out of production scope—none is silently bypassed.
20. A coding agent or reviewer can trace every financial effect to authoritative source facts, Payment-owned policy, and durable proof without reconstructing intent from provider/Audit/Ops state.
