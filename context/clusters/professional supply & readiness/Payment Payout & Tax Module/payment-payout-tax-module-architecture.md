# Payment Payout & Tax Module Architecture

> **Module ID:** `payment_payout_tax`  
> **Canonical registry name:** Payment / Payout / Tax Module  
> **Primary Cluster:** CL-03 — Professional Supply & Readiness  
> **Primary bridge:** CL-04 — Customer Demand, Order & Resolution  
> **Repository target:** `context/clusters/professional supply & readiness/Payment Payout & Tax Module/payment-payout-tax-module-architecture.md`

**Repository context (CL-03-R021):** Read [context/context-map.md](<../../../context-map.md>) for authority by concern and verified artifact locations, [context/project-overview-v3.md](<../../../project-overview-v3.md>) for orientation, and [context/shared/shared-operations.md](<../../../shared/shared-operations.md>) for canonical operations. Root architecture, root build plan, code standards, and the progress tracker are missing; references to those prerequisites do not assert availability or authorize a substitute/global precedence rule.

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `payment_payout_tax` |
| Module name | Payment / Payout / Tax Module |
| Module type | `capability_compliance` |
| Build status | `mvp_active_legal_gated` |
| Primary Cluster | CL-03 — Professional Supply & Readiness |
| Secondary bridge | CL-04 — Customer Demand, Order & Resolution |
| Document status | Implementation-grade Module architecture. Confirmed evidence is binding; Proposed Rulings require approval before schema/API commitment; Unresolved items must not be invented. |
| Intended audience | Coding agents, developers, reviewers, maintainers, security/compliance reviewers, and architecture reviewers implementing this Module. |
| Relationship to root architecture | Subordinate to the root Workin Ants architecture, project overview, code standards, and shared platform contracts. This document specializes those rules only for this Module and must not recreate global infrastructure. |
| Relationship to Cluster architecture | Subordinate to CL-03 architecture and build sequencing. This file is more specific about Payment-owned data, policy, provider rails, and internal implementation boundaries, but it may not contradict the Cluster's cross-Module ownership rulings. |
| Update rule | Change this file before or with any binding change to owned truth, lifecycle policy, public interface, provider boundary, compliance rule, concurrency invariant, or Shared Operation use. A progress update or implementation shortcut must never silently redefine this architecture. |

### Evidence basis

This architecture was derived from the supplied Workin Ants project overview, Deep Module Registry, Cluster Registry, current Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Architecture, CL-03 architecture, and CL-03 build plan. Where those sources differ, this document preserves the stronger source-of-truth boundary rather than averaging conflicting claims.

### Evidence classification

- **Confirmed** — supported directly by the supplied registries, schema, glossary/compliance pack, Shared Operations registry, or CL-03 architecture/build plan.
- **Proposed Ruling** — a concrete implementation decision needed to make the existing model safe or executable, but not yet established by the supplied authoritative evidence.
- **Unresolved** — evidence exposes a real question but does not establish one safe answer. A coding agent must constrain or disable the affected path rather than choose silently.

---

## 2. Purpose, Goal, and Transformation

### Purpose

The Payment / Payout / Tax Module owns Workin Ants' financial-compliance and processor-facing truth: payout KYC, tax-profile and tax-reporting readiness, payout accounts, professional balance projection, payout requests and transfers, Stripe-event deduplication, payment/provider rail evidence, and transaction-level sales-tax proof.

It exists so the rest of Workin Ants can ask a single financial owner for trustworthy financial facts without reading provider objects, compatibility booleans, mutable “wallet” values, or tax-provider payloads directly.

### Goal

For any supported financial action, the Module must be able to answer and execute only its own portion of the workflow:

```text
Who is the professional/subject?
→ what financial action is requested?
→ what KYC, tax-profile, payout-account, balance, hold, and step-up facts apply?
→ is the action financially ready?
→ if a provider rail is required, execute it idempotently
→ persist Payment-owned proof
→ command the owning business Module when another lifecycle must change
→ emit minimized financial facts for downstream consumers
```

### What enters

- authenticated User/system actor context;
- Role / Authority decisions and owner relationship facts;
- ProfessionalProfile identity/context from Professional Eligibility;
- authoritative Order pricing, participant, entitlement/commission snapshots, and payment/refund context from Transaction / Order;
- Review / Dispute outcomes and ComplianceHold decisions that affect money movement without transferring dispute/hold ownership;
- source-recognized taxable/reportable value from Prize, Rewards, Orders, or other approved owners;
- buyer tax-location evidence and item/tax-code context from the owning checkout/Offering/Digital Goods boundaries;
- provider callbacks and reconciliation results from Stripe / Stripe Connect / Stripe Tax or future approved adapters;
- Privacy-owned erase/anonymize/export/retain instructions;
- admin/system commands that are explicitly authorized and, where required, step-up protected.

### What leaves

- canonical KYC, tax-profile, payout-account, payout-request, payout-transfer, tax-reporting, and sales-tax states;
- `evaluateFinancialReadiness` decisions with separate dimensions and stable Payment-owned reasons;
- safe financial setup/history views;
- append-only professional balance effects and derived available/held/requested/paid projections;
- provider-normalized payment, payout, KYC, tax, and sales-tax evidence;
- commands to Transaction / Order when verified provider results must change transaction truth;
- reportable-value intake and tax-reporting state for Prize/Rewards/other source owners;
- Payment-owned domain events through the canonical outbox;
- Notification, Audit, sensitive-access, Privacy, and Observability requests through their owners.

### Business / capability transformation

```text
external provider state + source-owner commercial facts
→ verified / deduplicated / normalized financial evidence
→ Payment-owned canonical lifecycle state and financial projection
→ action-specific financial readiness or processor execution result
→ downstream owner command/event without ownership theft
```

### Why this is a distinct Module boundary

The Module combines high-risk financial compliance and processor integration that must evolve independently from Order, Professional, Dispute, Prize, Rewards, and Search lifecycles. It owns provider semantics, payout controls, tax reporting, and financial proof, while explicitly **not** owning the commercial transaction itself. Keeping this boundary prevents a provider object or “Stripe ready” flag from becoming transaction, identity, or eligibility truth.

---

## 3. Owned Truth

### 3.1 Confirmed owned models and enums

The current registry and Prisma evidence place the following truth in this Module:

| Record / enum | Plain-English meaning | Ownership meaning |
| --- | --- | --- |
| `ProcessedStripeEvent` | A Stripe event ID already claimed by Payment processing. | Stripe callback dedupe truth for Payment-owned Stripe effects; not audit or business lifecycle history. |
| `KycVerification` / `KycStatus` | Payout/financial identity verification for a User / ProfessionalProfile. | Financial KYC truth. It is separate from Trust `VerificationCheck`. |
| `TaxProfile` / `TaxProfileStatus` | Tax identity/readiness for payouts, reporting, prizes, or rewards. | Seller/recipient tax readiness; not transaction sales-tax truth. |
| `TaxDocument` / `TaxDocumentType` | Provider/document reference for tax forms such as W-9/W-8 variants. | Tax-document readiness/provenance; not a generic file-storage record. |
| `TaxYearEarningsSummary` | Year-level reportable-value summary. | Payment-owned tax-reporting aggregation/projection, distinct from prize/reward source records. |
| `TaxReportingSubmission` / `TaxReportingRegime` | A filing/reporting bundle for a tax regime, jurisdiction, and year. | Tax filing lifecycle truth. |
| `TaxReportingRecipient` | A subject included or blocked in a reporting submission. | Per-recipient filing inclusion/status truth. |
| `PayoutAccount` / `PayoutAccountStatus` | External processor account used to receive professional funds. | Canonical payout-account readiness; provider account status is translated into this vocabulary. |
| `ProviderRequirementSnapshot` | Point-in-time provider KYC/payout requirement state. | Immutable explanation/evidence snapshot, not an active hold. |
| `ProfessionalBalanceLedgerEntry` / `ProfessionalBalanceLedgerEntryType` | Append-only accounting effects for available/held/released/requested/paid professional funds. | Internal financial projection over processor-held funds; never a custodial wallet or escrow balance. |
| `PayoutRequest` / `PayoutRequestStatus` | Professional intent to request payout of processor-held available funds. | Payout-request lifecycle truth. |
| `PayoutTransfer` / `PayoutTransferStatus` | Attempted/completed/reversed processor movement to the professional. | Transfer-execution lifecycle truth; not Order truth. |
| `SalesTaxCalculation` / `SalesTaxCalculationStatus` | Provider-backed checkout/order sales-tax calculation proof. | Transaction-level tax-calculation truth. |
| `SalesTaxLineItem` / `SalesTaxLineItemType` | Tax line-level calculation/evidence for a purchased item. | Sales-tax line proof; Marketplace/Digital Goods may supply context but do not own this record. |
| `SalesTaxTransaction` / `SalesTaxTransactionStatus` | Provider-backed recorded/reversed/refunded tax transaction for an Order. | Tax transaction lifecycle truth. |
| `SalesTaxProvider` | Canonical provider vocabulary for sales-tax calculation/recording. | Adapter-selection vocabulary, not a provider object's status. |
| `SalesTaxLiabilityRole` | Who is responsible for collection/remittance for supported tax proof. | Marketplace-facilitator/seller/not-collected/exempt/unknown liability classification. |

### 3.2 Enum ownership gaps surfaced by schema

`TaxReportingSubmission.status` and `TaxReportingRecipient.status` use `TaxReportingSubmissionStatus` and `TaxReportingRecipientStatus` in Prisma, but those two enum names were omitted from the Module registry's explicit owned-schema list.

**Proposed Ruling PT-01:** because both enums exist solely to govern Payment-owned tax-reporting records, they are owned by `payment_payout_tax` unless a root enum-governance ruling says otherwise. Implementations may use the current Prisma enums, but should record the ownership correction in the registry/context when approved.

### 3.3 Owned lifecycles

The Module owns lifecycle policy for:

- KYC verification;
- tax-profile readiness;
- payout-account readiness;
- payout requests;
- payout transfers;
- tax-reporting submissions;
- tax-reporting recipients;
- sales-tax calculations;
- sales-tax transactions.

`ProfessionalBalanceLedgerEntry`, `ProviderRequirementSnapshot`, and `ProcessedStripeEvent` are evidence/ledger records rather than mutable business lifecycles.

### 3.4 Owned source-of-truth records

- canonical financial KYC state;
- canonical tax-profile/document readiness;
- canonical provider payout-account state;
- canonical payout request/transfer state;
- Payment's append-only professional balance effects;
- Stripe provider-event claim/dedupe evidence for Payment workflows;
- provider requirement snapshots;
- yearly tax-reporting summary/filing state;
- transaction sales-tax calculation, line, liability, transaction, and reversal/refund evidence.

### 3.5 Owned decisions and policies

- **SH-019 `evaluateFinancialReadiness`** policy and reason namespace;
- which Payment-owned dimensions are required for a Payment-owned action such as payout;
- payout sufficiency/reservation/release policy;
- how source Order/refund/dispute/hold effects translate into financial ledger effects;
- provider status translation into Payment enums;
- retryability classification for Payment provider operations;
- sales-tax evidence selection and calculation/finalization/reversal policy for supported checkout flows;
- tax-profile/document requirements and reporting-readiness evaluation, subject to legal-gated rules;
- reportable-value intake normalization and yearly aggregation;
- provider reconciliation rules for Payment-owned truth;
- Payment-specific Privacy retention/anonymization/deletion execution policy, subject to Privacy-owned orchestration and legal retention rulings.

### 3.6 Owned projections and snapshots

- `ProfessionalBalanceLedgerEntry` is a financial accounting projection/history over source commercial effects and processor-held funds; derived totals are rebuildable from entries.
- `TaxYearEarningsSummary` is a year-level reporting projection/aggregation, not source prize/reward/Order truth.
- `ProviderRequirementSnapshot` is immutable explanatory provider evidence.
- Safe financial setup/history DTOs are read projections, never separate authoritative state.

### 3.7 Domain events / ledgers owned

The Module owns the semantic meaning of Payment domain events and its financial/provider ledgers. Generic outbox/inbox, AuditEvent, AccessAuditLog, IntegrationFailure, QueueJob, and SystemEvent remain externally owned shared mechanics/truth.

---

## 4. Explicit Non-Ownership

This Module must not absorb adjacent lifecycle truth for implementation convenience.

| Adjacent owner | Truth that remains external | What Payment may do | What Payment must never do |
| --- | --- | --- | --- |
| Transaction / Order | `Order`, `OrderStatus`, `RefundStatus`, `OrderEvent`, agreements, participants, transaction pricing snapshots | Read narrow authoritative Order facts; execute processor/tax rail; return verified normalized payment/refund result through Order commands | Directly update `Order.status`, `RefundStatus`, `OrderEvent`, agreement state, or create a competing payment-order lifecycle |
| Professional Eligibility | `ProfessionalProfile` identity/status and seller-action readiness composition | Read profile context; supply SH-019 financial dimensions | Treat `stripeReady`, `stripeAccountId`, profile verification summaries, or profile status as Payment truth; mutate profile lifecycle |
| Track Subscription & Entitlement | Current plan/commission/fee-waiver/benefit truth | Consume immutable historical commission/fee snapshots already owned by Order where needed | Recalculate historical commission from current entitlement; create local seller-plan or commission-policy booleans |
| Marketplace Supply | `Offering`, `PricingTier`, Offering lifecycle and purchase item shape | Consume immutable item/tax-code/price context through approved owner contracts | Create/update Offerings or PricingTiers; own product/course lifecycle |
| Digital Goods Access | Digital-goods policy, download asset/grant/access lifecycle | Consume approved digital tax-code/item context | Create download grants, file access, product-delivery policy, or digital-goods lifecycle |
| Gig / Demand | Gig, response, assignment lifecycles | Consume an Order that originated from a GigAssignment when supplied by Order | Read/mutate Gig tables as Payment truth |
| Review / Dispute | Dispute case, evidence, adjudication, review lifecycle | Consume dispute outcome/hold/refund command and record money consequences | Resolve dispute cases; create competing dispute statuses |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle | Evaluate/request/release through canonical interfaces where Payment policy requires | Add `isBlocked`/`payoutBlocked` source flags that replace hold truth; directly change hold state |
| Identity & Access | MFA/passkey/step-up session/challenge lifecycle | Require step-up for sensitive financial actions | Build payout-specific MFA, store MFA truth, or interpret provider security state locally |
| Role / Authority | Generic permission interpretation | Supply Payment relationship/action facts to authorization | Build a Payment RBAC engine or frontend-only permission system |
| Trust Verification / Screening | Background checks, licenses, TrustBadge, VerificationCheck | Remain separate; no reuse for payout KYC | Treat screening verification as KYC truth or vice versa |
| Healthcare | Healthcare lane/BAA/boundary/access policy | No financial truth transfer | Infer healthcare compliance from Payment records or own healthcare decisions |
| Sweepstakes / Prize | Prize entry/drawing/winning/fulfillment lifecycle | Receive recognized taxable value; return tax readiness/facts | Draw prizes, decide winners, or mutate PrizeWinning lifecycle |
| Gamification / Rewards | Point/reward/redemption lifecycle and fair-market-value recognition | Receive reportable value | Own reward logic or point ledger |
| Media / File Access | Upload, validation, malware scan, object storage, signed URLs, MediaAsset lifecycle | Request protected access if an approved Payment business attachment exists | Store raw file mechanics, presign URLs, scan files, expose permanent private URLs |
| Notification | Notification persistence/delivery/channel/provider lifecycle | Request a safe business notification | Call SES/SMS/push provider directly or treat delivery as financial truth |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | Append generic audit/access proof | Reuse AuditEvent as payout, Stripe, ledger, or tax lifecycle truth |
| Observability / Ops | IntegrationFailure/SystemEvent/QueueJob/OpsIncident | Record diagnostics and queue telemetry | Treat operational failure/queue state as KYC, payout, tax, or provider-event truth |
| Privacy / Data Erasure | PrivacyRequest, DataErasureJob, retention exemptions, cross-service orchestration | Enumerate/execute/export Payment-owned subject data and provider resources | Build a Payment privacy-request lifecycle or self-create retention exemptions |
| Search / Public Visibility | SearchUpsertEvent, Typesense/query/index reconciliation | Normally no public Payment projection; emit readiness facts to actual source owners | Put tax/KYC/payout information in public Search; write Typesense/SearchUpsertEvent directly |

### Strong transaction boundary

**Order is transaction truth.** Stripe and other processors are rails. A successful provider callback may allow Payment to command Order to record a verified payment/refund outcome; it does not make `ProcessedStripeEvent`, `PayoutTransfer`, or a Stripe object the Order lifecycle.

### Strong funds boundary

**Processor-held funds are not a Workin Ants wallet or escrow.** The professional balance ledger is an accounting projection over processor-held funds and source events. Do not create `Wallet`, `WalletBalance`, `Escrow`, `StoredValue`, or an equivalent mutable custodial balance model without a later explicit legal/architecture ruling.

---

## 5. Module Architecture Principles

1. **Financial truth is canonical Workin Ants state, not raw provider state.** Provider callbacks are verified, deduplicated, translated, and transition-validated before updating Payment records.
2. **Order remains transaction owner.** Payment executes rails; Order owns transaction lifecycle, RefundStatus, and OrderEvent.
3. **KYC is not Trust verification.** Financial identity verification and marketplace screening are separate records, policies, providers, and reason codes.
4. **Tax-profile readiness is not sales tax.** Seller/recipient tax identity/reporting is distinct from transaction-level tax calculation and liability.
5. **No wallet/escrow source truth.** Professional balance is append-only projection over processor-held money and domain effects.
6. **Payout request is intent; payout transfer is execution.** A requested payout does not mean money moved.
7. **Payment authorization/capture is not payout authorization.** Payout requires current Payment readiness, hold evaluation, authority, and step-up.
8. **Historical finance uses historical snapshots.** Do not recalculate settled commission/fee policy from today's Track entitlement.
9. **Shared mechanisms do not merge truth.** Stripe dedupe, domain-event dedupe, audit, queue, and ledger plumbing remain separate records with separate meanings.
10. **Sensitive finance is server-gated.** Step-up, authorization, and sensitive-access proof occur server-side; UI hiding is insufficient.
11. **Provider details stay behind ports/adapters.** Domain/application code consumes canonical result shapes, not Stripe SDK objects.
12. **No custom tax engine.** Use approved provider-backed tax calculation/rule inputs; unresolved jurisdictions or unsupported cases fail explicitly rather than being guessed.
13. **Legal-gated paths remain gated.** Retention periods, filing thresholds, form/regime rules, and unsupported partial-refund semantics cannot be invented by coding agents.
14. **Cross-Module interaction uses public contracts.** Direct Prisma reads into Order, Professional, Dispute, Prize, Rewards, Track, or Digital Goods are not the default integration pattern.
15. **Every external effect is effectively-once.** Use canonical command idempotency, provider-event dedupe, consumer inboxes, DB constraints, and reconciliation.
16. **Financial correction is append/reverse, not history rewrite.** Where an economic effect must be corrected, append compensating evidence and update only lifecycle records whose policy explicitly permits mutation.
17. **Observability is diagnostic only.** `IntegrationFailure`, `QueueJob`, logs, metrics, and incidents never replace Payment source truth.

---

## 6. Proposed Folder / Code Structure

This is a **Proposed Ruling** for Module-local placement. It must yield to a more specific root repository convention if one exists.

```text
src/modules/payment-payout-tax/
  application/
    commands/
    queries/
    orchestration/
  domain/
    policies/
    lifecycles/
    services/
    money/
  contracts/
    public/
    events/
    providers/
    privacy/
  schemas/
    commands/
    providers/
  infrastructure/
    repositories/
    providers/
      stripe/
      sales-tax/
      kyc/
      tax-reporting/
  workers/
  privacy/
  tests/
    unit/
    integration/
    contract/
    provider/
    concurrency/
    privacy/
```

### Placement rules

- `application/commands/` — use cases that validate, authorize, invoke local domain policy, write Payment-owned state, and call shared operations.
- `application/queries/` — SH-019 and safe financial reads; no foreign aggregate reconstruction.
- `application/orchestration/` — Payment-owned multi-step workflows such as payout execution or payment/tax-to-Order handoff. It may coordinate, but does not own another Module's lifecycle.
- `domain/policies/` — readiness composition, tax/payout eligibility, source-effect rules, provider mapping-independent policy.
- `domain/lifecycles/` — owner transition graphs and guards. Do not create one global status engine.
- `domain/services/` — pure financial transformations such as balance projection and tax/reporting calculations that are genuinely Payment policy.
- `domain/money/` — integer minor-unit/currency invariants and signed ledger-effect rules. Do not introduce a new money framework if root already provides one.
- `contracts/public/` — stable Module commands/queries consumed by other Modules.
- `contracts/events/` — versioned minimized Payment event DTOs.
- `contracts/providers/` — provider-neutral ports and canonical provider-result envelopes.
- `contracts/privacy/` — Payment implementation of Privacy target protocols.
- `schemas/` — Zod validation for server/provider boundaries. Domain enums remain Prisma/domain truth; provider payload schemas are adapter-local.
- `infrastructure/repositories/` — Prisma data access for **Payment-owned tables only**.
- `infrastructure/providers/` — Stripe/Stripe Connect/Stripe Tax and future approved adapters. Shared webhook/retry/security plumbing remains outside this Module.
- `workers/` — owner jobs such as payout transfer execution, reconciliation, tax aggregation/reporting, and expiry/refresh.
- `privacy/` — subject-data inventory, retention mapping, provider-delete adapter calls, export/anonymization execution.
- `tests/` — Module-local tests grouped by responsibility.

### Delivery/UI placement

No standalone Payment UI framework is created here. Professional financial setup, tax dashboard, payout history, and restricted admin views may exist only where the root application routing/UI architecture provides them. Delivery handlers/server actions must be thin adapters into the Module's public application contracts. Do not duplicate policy in React components or route handlers.

### Shared code that must remain outside this folder

Authentication, RBAC, step-up, ComplianceHold, command idempotency store, transaction/outbox/inbox, queue runner, retry framework, generic lifecycle helper, generic audit/access log writer, telemetry, cryptography, Media signed URLs, Search client, Notification provider, and Privacy orchestration.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / UI | Parse safe user intent; call public commands/queries; render safe Payment result states | KYC/tax/payout policy, provider SDK calls, direct Prisma, permission shortcuts |
| Application commands | Use-case orchestration, validation, actor/authority/step-up invocation, transaction boundaries, external owner commands | Generic auth/queue/audit infrastructure; foreign aggregate mutation |
| Application queries | Safe source truth/projection reads and SH-019 composition | Provider object interpretation in callers; direct foreign-table joins for convenience |
| Domain policy | Financial readiness, payout sufficiency, ledger effect meaning, tax/reporting policy, lifecycle guards | Role interpretation, ComplianceHold lifecycle, Order state policy, Prize/Reward/Dispute policy |
| Repositories | Payment-owned Prisma persistence, row locking/version checks as approved | Cross-domain repositories or generic `targetType/targetId` Prisma access |
| Workers | Payment-owned provider reconciliation, payout execution, tax aggregation/reporting, expiry/refresh | Generic queue/retry/dead-letter mechanics; foreign lifecycle writes |
| Provider adapters | Stripe/Connect/Tax/KYC/reporting API translation, provider-specific status mapping and idempotency inputs | Workin Ants business truth, readiness policy, Order lifecycle |
| Public contracts | Stable Payment-owned commands, queries, events, Privacy executor | Leaking provider SDK types/raw payloads or exposing generic platform infrastructure |
| Privacy executor | Enumerate/export/anonymize/retain/delete Payment-owned data/resources under Privacy instruction | PrivacyRequest lifecycle, exemption lifecycle, global deadline/orchestration |

---

## 8. Data Model

### 8.1 `ProcessedStripeEvent`

**Purpose:** owner-specific claim that a Stripe event has been seen/claimed for Payment processing.

**Authoritative fields:** `eventId` primary key, `type`, `receivedAt`.

**Relationships:** none required by current schema; affected aggregate correlation is currently implicit in provider payload/application processing.

**Uniqueness:** `eventId` primary key provides one claim per Stripe event ID.

**Concurrency:** event claim must be atomic. Duplicate concurrent webhook deliveries must converge on one effect.

**Retention/privacy:** retain long enough to prevent unsafe replay and support financial/provider reconciliation; exact legal/operational retention is unresolved.

**Important limitation:** current schema has no processed/failed/attempt state. See Unresolved Decision UD-04.

### 8.2 `KycVerification`

**Purpose:** canonical payout/financial identity verification state.

**Relationships:** required `User`; optional `ProfessionalProfile`.

**Authoritative fields:** provider/reference IDs, `status`, `verifiedAt`, `expiresAt`, `failureReason`, last provider event reference.

**Lifecycle:** `KycStatus`.

**Indexes:** subject/status and provider/reference lookup.

**Concurrency:** current/latest record selection and duplicate onboarding attempts require owner transaction policy; schema has no explicit “one current KYC row” constraint.

**Retention/privacy:** highly sensitive financial-compliance metadata. Prefer provider-hosted identity collection; do not persist raw SSN/identity documents in ordinary fields.

### 8.3 `TaxProfile`

**Purpose:** canonical tax identity/readiness for payouts/reporting/prize/reward tax requirements.

**Relationships:** required User; optional ProfessionalProfile; owns TaxDocument references; referenced by prize/reward/tax workflows.

**Authoritative fields:** status, countries, provider/reference, verified timestamp.

**Lifecycle:** `TaxProfileStatus`.

**Concurrency:** schema does not identify one current/applicable tax profile per subject/jurisdiction. See UD-06.

**Retention/privacy:** tax data is sensitive and commonly legally retained. Destructive deletion is legal-gated.

### 8.4 `TaxDocument`

**Purpose:** tax-form/document provenance attached to TaxProfile.

**Authoritative fields:** `type`, provider/document reference, submitted/verified timestamps.

**Deletion:** current Prisma relation cascades from TaxProfile. Privacy/destructive deletion must not rely on cascade where retention applies.

**Media boundary:** this is not raw binary file truth. If an approved workflow stores an actual file, Media owns storage/access mechanics.

### 8.5 `TaxYearEarningsSummary`

**Purpose:** year-level reportable-value aggregation used for tax reporting readiness and filing preparation.

**Authoritative fields:** tax year, reportable value buckets, payout/transaction counts, currency, jurisdiction, reporting regime, reporting-required/threshold metadata.

**Uniqueness:** current Prisma unique constraint is `(userId, taxYear, currency)`.

**Concurrency:** updates must be source-event idempotent and transactional. Reconciliation must be able to rebuild from source-recognized values.

**Approved CL-03-R014:** the minimum aggregation semantics are tax subject + jurisdiction + tax year + currency, with durable source-event uniqueness and reversal handling under SH-117/118. Current Prisma uniqueness `(userId, taxYear, currency)` is insufficient; jurisdiction must not be discarded. The exact tax-subject representation, including any ProfessionalProfile dimension, and the forward persistence/migration design remain Payment-owned open decisions under UD-14. No schema change is made by this documentation ruling.

### 8.6 `TaxReportingSubmission`

**Purpose:** one tax filing/reporting submission bundle for a regime, jurisdiction, and year.

**Authoritative fields:** tax year, jurisdiction, regime, status, provider submission reference, submitted/accepted/failed timestamps and failure reason.

**Lifecycle:** `TaxReportingSubmissionStatus`.

**Concurrency/uniqueness:** current schema does not define a unique submission version key. Corrected/replacement filing semantics are unresolved.

### 8.7 `TaxReportingRecipient`

**Purpose:** per-recipient inclusion/filing state inside a submission.

**Authoritative fields:** submission/subject refs, reportable amount/count, currency, status, provider recipient reference.

**Lifecycle:** `TaxReportingRecipientStatus`.

**Concurrency:** current schema lacks an explicit unique `(submission, subject)` invariant; feature implementation must not silently allow duplicate recipient rows.

### 8.8 `PayoutAccount`

**Purpose:** canonical external payout-account readiness for a ProfessionalProfile.

**Authoritative fields:** profile, provider/provider account ID, status, charges/payouts enabled, provider requirements summary.

**Uniqueness:** `(provider, providerAccountId)` unique.

**Concurrency:** multiple accounts may exist for one ProfessionalProfile; no primary/default account field exists. See UD-07.

**Retention/privacy:** do not store raw bank/account credentials. Provider references and safe requirement summaries only.

### 8.9 `ProviderRequirementSnapshot`

**Purpose:** immutable snapshot explaining provider onboarding/KYC/payout requirements at a point in time.

**Authoritative fields:** payout account, provider, requirements JSON, captured timestamp.

**Policy:** snapshot only allowlisted provider requirements needed for support/explanation; no raw secret/identity payload.

### 8.10 `ProfessionalBalanceLedgerEntry`

**Purpose:** append-only accounting effect used to derive professional available/held/requested/paid projections.

**Relationships:** ProfessionalProfile; optional User, Order, PayoutRequest, PayoutTransfer.

**Authoritative fields:** type, signed amount in minor units, currency, source references, `availableAt`, `effectiveAt`, minimized metadata.

**Concurrency:** duplicate source events must not create duplicate effects. Current schema has no explicit unique source-effect key. See PT-02/UD-09.

**Mutation rule:** entries are immutable after creation. Corrections use compensating entries.

**Retention:** financial/accounting proof may require long retention; exact period legal-gated.

### 8.11 `PayoutRequest`

**Purpose:** professional request to withdraw available processor-held funds.

**Authoritative fields:** subject/account, amount/currency, status, timestamps, block/failure metadata.

**Lifecycle:** `PayoutRequestStatus`.

**Concurrency:** creation must atomically prevent overspending across concurrent requests. Current schema has no idempotency key and only one `blockedByHoldId` reference. Use canonical idempotency/reservation/lock mechanisms and resolve schema gaps before production.

### 8.12 `PayoutTransfer`

**Purpose:** processor transfer/payout execution record.

**Authoritative fields:** request/account/profile/order context, amount/currency/fee, provider references, `idempotencyKey`, status, failure/block timestamps/reasons.

**Uniqueness:** `idempotencyKey` is unique.

**Concurrency:** one semantic transfer attempt/effect per idempotency key. Retry semantics must not duplicate provider movement.

**Important ambiguity:** optional `payoutRequestId` and `orderId` allow request-based and order-linked transfer shapes without defining authoritative source granularity. See UD-11.

### 8.13 `SalesTaxCalculation`

**Purpose:** provider-backed tax calculation proof for checkout/order context.

**Authoritative fields:** Order/User refs, provider/status/liability role, provider calculation/transaction refs, buyer location fields, currency and taxable/tax/total amounts, timestamps, safe metadata.

**Lifecycle:** `SalesTaxCalculationStatus`.

**Concurrency:** calculations/finalization must bind to the exact Order pricing/version used. Current schema does not enforce one finalized current calculation per Order. See UD-16.

**Privacy:** buyer location is tax evidence, not public location. Store minimum required precision/provenance.

### 8.14 `SalesTaxLineItem`

**Purpose:** tax calculation evidence per purchased item.

**Authoritative fields:** calculation, optional Offering/PricingTier refs, item type, provider tax code, amount/tax/rate/jurisdiction evidence.

**Ownership:** Payment owns this record even when Marketplace or Digital Goods supplies source item context.

**Approved CL-03-R015 / schema gap:** Payment must preserve line-level liability evidence wherever liability can differ between lines; transaction-level liability cannot prove mixed-liability items. Current Prisma lacks `SalesTaxLineItem.liabilityRole`. A field or another immutable line-linked evidence structure requires later persistence design and a forward migration; UD-17 retains that design gap, not a choice to discard line-level evidence. Unsupported mixed-liability flows remain disabled.

### 8.15 `SalesTaxTransaction`

**Purpose:** recorded/reversed/refunded provider tax transaction attached to an authoritative Order.

**Authoritative fields:** Order/calculation/User refs, provider/status/liability, provider transaction/reversal refs, taxable/tax amounts, timestamps, safe failure/metadata.

**Lifecycle:** `SalesTaxTransactionStatus`.

**Concurrency:** duplicate provider events/refund commands must not duplicate tax transactions or reversals.

**Schema limitation:** one reversal reference and aggregate amounts do not establish partial/multiple refund allocation semantics. See UD-18.

---

## 9. Enums, Statuses, and Lifecycles

### Lifecycle rule

The enum vocabularies are Confirmed by Prisma. **The complete legal transition adjacency is not fully established by the supplied evidence.** Therefore no public `setStatus(status)` operation is allowed. Each feature must implement only the transitions explicitly approved in its feature specification. The tables below distinguish confirmed vocabulary from proposed minimum transition graphs.

### 9.1 KYC — `KycStatus`

Confirmed statuses:

```text
not_started → pending → requires_input / approved / rejected
requires_input → pending
approved → expired / disabled
pending → disabled
```

Additional reopen/retry edges are **Unresolved**.

- Transition owner: Payment domain/application service after authorized start/resume or verified provider result.
- Terminality: `approved` is current-success, not permanently terminal; `rejected`, `expired`, `disabled` require explicit owner policy for new attempt vs same-row reopening.
- Proof: provider reference, last event reference, timestamps; Payment domain event/outbox for meaningful status change.
- Prohibited shortcut: caller-provided KYC status, Trust Verification status, or `ProfessionalProfile.stripeReady`.

### 9.2 Tax profile — `TaxProfileStatus`

Confirmed statuses: `not_started`, `requested`, `submitted`, `verified`, `rejected`, `expired`.

Proposed minimum progression:

```text
not_started → requested → submitted → verified / rejected
verified → expired
rejected / expired → [new or resumed collection path: unresolved]
```

The exact “current profile” and re-submission strategy is unresolved.

### 9.3 Payout account — `PayoutAccountStatus`

Confirmed statuses: `not_started`, `onboarding`, `pending_review`, `active`, `restricted`, `disabled`.

Proposed minimum progression:

```text
not_started → onboarding → pending_review / active / restricted
pending_review → active / restricted / disabled
active → restricted / disabled
restricted → pending_review / active / disabled
```

Only provider-normalized/owner-approved transitions may occur. `chargesEnabled` and `payoutsEnabled` are contextual provider facts; neither alone replaces status/readiness policy.

### 9.4 Payout request — `PayoutRequestStatus`

Confirmed statuses: `requested`, `pending_review`, `blocked`, `approved`, `processing`, `paid`, `failed`, `cancelled`, `reversed`.

Proposed minimum graph:

```text
requested → pending_review / blocked / approved / cancelled
pending_review → blocked / approved / cancelled
blocked → pending_review / approved / cancelled      [only after source restriction clears]
approved → processing / cancelled
processing → paid / failed
paid → reversed                                     [only on actual provider/financial reversal]
failed → [retry/new-transfer semantics unresolved]
```

A payout request cannot become `paid` merely because it was approved.

### 9.5 Payout transfer — `PayoutTransferStatus`

Confirmed statuses: `pending`, `blocked`, `processing`, `paid`, `failed`, `reversed`, `cancelled`.

Proposed minimum graph:

```text
pending → blocked / processing / cancelled
blocked → pending / cancelled                       [after explicit reevaluation]
processing → paid / failed
paid → reversed
failed → [new attempt or controlled retry: unresolved]
```

Provider retry must preserve exactly-one money movement even when the local attempt is repeated.

### 9.6 Tax reporting submission — `TaxReportingSubmissionStatus`

Confirmed statuses: `draft`, `ready`, `submitted`, `accepted`, `rejected`, `failed`.

Proposed minimum graph:

```text
draft → ready
ready → submitted
submitted → accepted / rejected / failed
rejected / failed → [corrected replacement or resubmission: unresolved]
```

`accepted` is terminal for that submission artifact; a correction should not rewrite historical accepted filing proof.

### 9.7 Tax reporting recipient — `TaxReportingRecipientStatus`

Confirmed statuses: `pending`, `included`, `filed`, `corrected`, `blocked`, `failed`.

Proposed minimum graph:

```text
pending → included / blocked / failed
included → filed / blocked / failed
filed → corrected
blocked → pending / included                         [only after tax requirement remediation]
failed → [retry/correction semantics unresolved]
```

### 9.8 Sales-tax calculation — `SalesTaxCalculationStatus`

Confirmed statuses: `draft`, `calculated`, `finalized`, `voided`, `failed`.

Proposed minimum graph:

```text
draft → calculated / failed
calculated → finalized / voided / failed
finalized → voided                                  [only where provider/Order semantics allow]
```

A new calculation should normally be created for changed Order pricing/location rather than mutating historical finalized evidence.

### 9.9 Sales-tax transaction — `SalesTaxTransactionStatus`

Confirmed statuses: `pending`, `recorded`, `reversed`, `refunded`, `failed`.

Proposed minimum graph:

```text
pending → recorded / failed
recorded → reversed / refunded
```

Partial/multiple reversal/refund semantics are unresolved and must be constrained to provider/schema-supported cases.

### 9.10 Immutable evidence records

- `ProcessedStripeEvent` — append/claim once; no business status lifecycle.
- `ProviderRequirementSnapshot` — append immutable snapshot.
- `ProfessionalBalanceLedgerEntry` — append immutable financial effect; corrections are new entries.

---

## 10. Commands

The names below are the preferred Module-level commands. Provider adapter methods remain internal and are not alternate public business APIs.

### 10.1 `startKycOnboarding`

- **Purpose:** create/resume Payment-owned KYC workflow before provider handoff.
- **Actor/context:** authenticated professional or authorized admin/system; profile relationship validated; step-up when required by current Identity policy.
- **Inputs:** ProfessionalProfile ID, subject User ID from owner facts, provider/flow context, idempotency key.
- **Preconditions:** authority; supported provider; no conflicting active attempt under approved cardinality rule.
- **Writes:** `KycVerification` and safe provider references.
- **Shared operations:** SH-001, SH-002, SH-044, SH-078; SH-014/030 for sensitive surfaces; SH-046 on meaningful state changes.
- **Idempotency:** same semantic onboarding request replays canonical result.
- **Failure:** unauthorized, conflicting attempt, provider unavailable, unsupported provider state.

### 10.2 `startTaxProfileCollection`

Same boundary as KYC, but writes `TaxProfile`/`TaxDocument` references. It does not calculate checkout sales tax and never stores raw tax identifiers unless a later approved secure path requires them.

### 10.3 `startPayoutAccountOnboarding`

Creates/resumes `PayoutAccount`, invokes provider-neutral Connect/payout account adapter, captures requirement snapshots as needed, and never writes `ProfessionalProfile.stripeAccountId/stripeReady` as authoritative truth.

### 10.4 `processPaymentProviderEvent`

- **Purpose:** apply a verified provider callback to Payment-owned records and, when required, invoke another owner's public command.
- **Context:** provider system actor; raw body/signature at webhook edge.
- **Preconditions:** SH-059 signature verification; SH-060 provider-event claim; supported event/type/mapping.
- **Writes:** `ProcessedStripeEvent` claim plus target Payment-owned state/evidence; outbox events.
- **External effect:** idempotent Order command only after normalized verified payment/refund result.
- **Failure:** duplicate → no repeated effect; unknown type → safe ignore/ops classification if truly irrelevant; unknown status → explicit unsupported/review; cross-owner command conflict → reconciliation, not direct DB patch.

### 10.5 `appendProfessionalBalanceEffect`

- **Purpose:** append one immutable financial effect from an authoritative source event/decision.
- **Inputs:** profile, currency, signed amount, effect type, source owner/type/ID/event ID, effective/available time, references.
- **Preconditions:** source validated; effect type/sign/rules valid; source-effect not previously applied.
- **Writes:** `ProfessionalBalanceLedgerEntry` only.
- **Shared operations:** SH-045 for consumed domain event, SH-044 where command-based, SH-051/056 for conflicting reservations, SH-046 after local effect if downstream reaction required.
- **Failure:** duplicate source effect returns prior result/no-op; invalid money/currency/source rejected.

### 10.6 `createPayoutRequest`

- **Purpose:** record payout intent and reserve eligible projected funds.
- **Actor/context:** professional; SH-014 step-up mandatory; SH-002 authority; SH-011 holds; SH-019 payout readiness.
- **Inputs:** profile, selected account under approved selection rule, amount/currency, idempotency key.
- **Preconditions:** positive minor-unit amount; sufficient available balance; supported currency; no blocking hold/restriction; active payout account; KYC/tax requirements per payout policy.
- **Writes:** `PayoutRequest` plus reservation/ledger effect as approved, atomically under profile+currency lock.
- **Events:** payout request created/blocked/approved facts; SH-041 notification where approved; SH-029 audit for high-impact/admin actions.
- **Failure:** insufficient funds, stale balance, hold, step-up missing, invalid account, concurrency conflict.

### 10.7 `executePayoutTransfer`

- **Purpose:** execute provider-mediated transfer for an approved request.
- **Context:** trusted worker/system actor.
- **Inputs:** payout request, transfer idempotency key, approved amount/currency/account.
- **Preconditions:** request still executable; re-check hold/readiness when policy requires; no existing equivalent transfer.
- **Writes:** `PayoutTransfer`, request state, append-only ledger consequences.
- **Provider:** payout port; SH-048 retry for transient failures; SH-062 reconciliation.
- **Failure:** provider terminal rejection → canonical failed/review state; ambiguous timeout → reconcile before retrying money movement.

### 10.8 `applyPayoutTransferResult`

Applies normalized provider callback/reconciliation result to `PayoutTransfer`, `PayoutRequest`, and compensating ledger effects according to owner transition policy. It must never mutate Order or Dispute state.

### 10.9 `calculateSalesTax`

- **Purpose:** obtain provider-backed tax calculation for a specific authoritative Order/pricing snapshot.
- **Inputs:** Order ID/version or immutable checkout snapshot, buyer tax-location evidence, line items/tax codes through owner contracts, currency, idempotency key.
- **Preconditions:** Order facts current and authorized; provider supported; sufficient location evidence.
- **Writes:** `SalesTaxCalculation` + `SalesTaxLineItem`.
- **Shared operations:** SH-044, SH-078, SH-123 where owner reference validation is required; SH-120 must not be assumed while unresolved.
- **Failure:** provider unavailable/unsupported jurisdiction → explicit unavailable; no local guessed tax.

### 10.10 `finalizeSalesTaxCalculation` / `voidSalesTaxCalculation`

Finalize or void provider-backed calculation against the exact Order version. Stale Order/version is a conflict. Historical finalized tax evidence is not silently rewritten.

### 10.11 `prepareOrExecuteOrderPaymentRail`

- **Purpose:** prepare/execute provider payment for an existing authoritative Order.
- **Inputs:** Order-owned payment snapshot, amount/currency/tax evidence, idempotency/correlation.
- **Writes:** Payment/provider evidence only.
- **External command:** normalized verified payment result to Transaction / Order.
- **Prohibition:** Payment does not create arbitrary Order status transitions and does not trust client success redirects.

### 10.12 `executeOrderRefundRail`

Called through the approved SH-108 refund coordination boundary. Order owns RefundStatus/adjudicated transaction decision; Payment executes provider refund and records Payment/tax consequences. Unsupported partial-refund allocation fails explicitly.

### 10.13 `recordSalesTaxTransaction` / `reverseSalesTaxTransaction`

Persist provider-backed tax transaction/reversal/refund proof once. Reversal/refund commands must link the originating calculation/Order and remain idempotent.

### 10.14 SH-118 `reportTaxableValue`

- **Purpose:** ingest a source owner's recognized reportable prize/reward/earning value without taking source lifecycle ownership.
- **Inputs:** subject, value/currency, jurisdiction, source type/ID, recognition date, valuation evidence, idempotency.
- **Writes:** Payment tax aggregation/reporting truth, not source record.
- **Shared mechanism:** SH-117 aggregation.
- **Failure:** duplicate recognition does not double count; unsupported jurisdiction/regime remains pending/review/unavailable per approved tax policy.

### 10.15 `prepareTaxReportingSubmission`

Build `TaxReportingSubmission` and recipient set from authoritative year summaries and current required tax-profile readiness under versioned legal policy. No hardcoded universal threshold/form assumption.

### 10.16 `submitTaxReportingSubmission` / `applyTaxReportingProviderResult`

Provider/reporting-adapter operations that transition only supported filing states. Automated filing remains production-gated until jurisdiction/regime rules and provider contracts are approved.

### 10.17 Privacy executor commands

Implement SH-095/096/097 protocol and SH-070 provider deletion under Privacy instruction. They may erase/anonymize/export/retain only Payment-owned data, respecting retention exemptions created by Privacy.

---

## 11. Queries / Decisions

### 11.1 SH-019 `evaluateFinancialReadiness`

**Consumers:** Professional Eligibility, Payment payout workflows, CL-10 tax/fulfillment consumers where applicable, admin/support tooling through authorized application services.

**Input:** ProfessionalProfile/subject reference, requested financial action, optional amount/currency, evaluation time/context.

**Result:** a Payment-owned decision with separate dimensions, for example:

```text
kyc
 tax_profile
 payout_account
 available_balance        (only when relevant)
 financial_restrictions   (Payment-local + applicable ComplianceHold inputs)
 provider_availability    (when action requires live provider execution)
```

Each dimension returns safe status, applicability, blocking/warning reason codes, evidence references, evaluatedAt, and remediation/next-action where approved.

**Stable owner reason-code families:**

- `kyc_not_started`, `kyc_pending`, `kyc_requires_input`, `kyc_rejected`, `kyc_expired`, `kyc_disabled`;
- `tax_profile_not_started`, `tax_profile_pending`, `tax_profile_rejected`, `tax_profile_expired`;
- `payout_account_missing`, `payout_account_onboarding`, `payout_account_pending_review`, `payout_account_restricted`, `payout_account_disabled`, `payouts_not_enabled`;
- `active_compliance_hold`;
- `insufficient_available_balance`;
- `unsupported_currency`;
- `step_up_required` where the requested Payment action itself requires fresh assurance;
- `provider_unavailable` / `provider_state_unsupported`;
- `policy_unresolved` for deliberately disabled legal-gated paths.

Exact codes/versioning must be frozen in the implementing feature contract.

**Consumer must not infer:** one opaque `canPayout`, Stripe account status, Trust verification, Order state, or action timing outside Payment ownership. Professional Eligibility still decides whether financial readiness is required for profile activation/publication/Gig response under unresolved Cluster policy U-01.

### 11.2 `getFinancialSetupSummary`

Returns safe KYC/tax-profile/payout-account state and next steps for the professional. Source truth/projection read; sensitive fields redacted. Step-up and SH-030 apply according to data shown.

### 11.3 `getProfessionalBalanceProjection`

Returns derived available/held/requested/paid totals by profile/currency and optional ledger history. It must be derivable from ledger entries and must not expose a mutable balance row as source truth.

### 11.4 `getPayoutHistory`

Returns safe PayoutRequest/PayoutTransfer history. Caller must not infer Order completion/refund/dispute truth from this view.

### 11.5 `getProviderRequirementSnapshot`

Returns latest or historical safe provider requirement snapshot for authorized professional/admin use. Caller must not treat snapshot presence as ComplianceHold or readiness truth.

### 11.6 `getTaxReportingStatus`

Returns year summary, reporting requirement state, filing submission/recipient status, and safe remediation. It does not expose provider tax IDs/raw tax documents.

### 11.7 `evaluateTaxFulfillmentReadiness`

**Proposed Module public query.** Returns whether Payment-owned tax-profile/reporting facts block a Prize/Reward fulfillment context. Prize/Sweepstakes remains owner of whether fulfillment proceeds and of the prize lifecycle.

### 11.8 `getSalesTaxEvidenceForOrder`

Returns provider-backed calculation/transaction proof for an authorized Order consumer. It does not return or change Order state.

---

## 12. Public Module Interface

### Public commands

- `startKycOnboarding`
- `startTaxProfileCollection`
- `startPayoutAccountOnboarding`
- `createPayoutRequest`
- approved admin/system payout review commands, scoped to Payment-owned status only
- `calculateSalesTax`
- `finalizeSalesTaxCalculation`
- `voidSalesTaxCalculation`
- `prepareOrExecuteOrderPaymentRail`
- Payment-side execution of SH-108 `requestOrderRefund`
- `recordSalesTaxTransaction` / supported reversal/refund operation
- SH-118 `reportTaxableValue`
- tax-reporting preparation/submission commands when legal/provider scope is approved
- SH-095 Privacy executor entry point(s)

### Public queries

- **SH-019 `evaluateFinancialReadiness`**
- `getFinancialSetupSummary`
- `getProfessionalBalanceProjection`
- `getPayoutHistory`
- `getProviderRequirementSnapshot`
- `getTaxReportingStatus`
- `getSalesTaxEvidenceForOrder`
- proposed `evaluateTaxFulfillmentReadiness`

### Emitted domain events

Exact event names are a **Proposed Ruling** until a feature specification freezes them. Event families should include:

- KYC status/readiness changed;
- TaxProfile status/readiness changed;
- PayoutAccount status/readiness changed;
- balance effect recorded;
- payout request status changed;
- payout transfer status changed;
- sales-tax calculation finalized/voided/failed;
- sales-tax transaction recorded/reversed/refunded;
- tax-year reporting requirement changed/threshold met;
- tax-reporting submission/recipient status changed.

### Privacy executor

Payment implements the canonical Privacy target protocol for its records and provider resources. It never receives ownership of PrivacyRequest/DataErasureJob.

### Provider-facing interfaces

Provider-neutral ports owned inside this Module:

- `PaymentRailPort`
- `PayoutProviderPort`
- `KycProviderPort`
- `TaxProfileProviderPort`
- `SalesTaxProviderPort`
- `TaxReportingProviderPort`

One Stripe adapter may implement multiple ports, but the contracts remain distinct so provider SDK types and one provider's combined API do not collapse separate Workin Ants lifecycles.


---

## 13. Inbound Dependencies

Payment consumes only the minimum facts/interfaces needed to execute Payment policy.

| Owning Module / capability | Interface consumed | Why required | Minimum information | Can block Payment action? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | Establish trusted actor/system context | actor ID/type, assurance context, request context | Yes — unauthenticated protected action | current-user/session helpers |
| Role / Authority | SH-002 `authorizeResourceAction` | Authorize financial read/mutation | action, target, owner relationship facts, decision | Yes | Payment RBAC/isAdmin engine |
| Identity & Access | SH-014 `requireStepUpForSensitiveAction` | Fresh assurance for sensitive balance/tax/payout operations | actor, action, target, required assurance | Yes | payout MFA/challenge/session state |
| Professional Eligibility | `getProfessionalProfileContext` or approved owner-facts query | Resolve seller identity/relationship and safe profile state | profile ID, owning User link where permitted, status/context version | Yes for invalid/nonexistent/unauthorized profile; profile status effects remain action-specific | direct ProfessionalProfile repository, `stripeReady` truth |
| Transaction / Order | authoritative payment/pricing/participant snapshot; verified payment/refund result commands | Payment/tax rail must bind to transaction truth | Order ID/version, amount/currency, seller/buyer context, pricing/commission/fee snapshots, agreement/payment eligibility facts required by contract | Yes for payment/tax execution | Order state machine, RefundStatus, OrderEvent, current Track recomputation |
| Transaction / Order | SH-108 refund coordination | Execute provider refund after approved Order decision | amount/currency, reason/source decision, Order version, idempotency/correlation | Yes | local refund adjudication/lifecycle |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold` | Reusable stop signs for payout/tax fulfillment and approved financial actions | target/action, applicable hold IDs/scopes/reasons/expiry | Yes | payoutBlocked/isHeld source flag |
| Admin Review / Compliance Hold | SH-012/013 when Payment evidence justifies requesting/releasing a hold | Ask owner to create/release canonical hold | target, reason, source evidence, scope, actor, idempotency | May block downstream action after owner decision | direct hold writes or Payment hold table |
| Review / Dispute | narrow dispute outcome/refund/financial consequence event/contract | Apply money effect without owning dispute | Order/dispute ID, outcome/version, authorized refund or financial-hold consequence | Yes for affected payout where policy maps it to Payment consequence | dispute status/evidence/adjudication |
| Track Subscription & Entitlement | primarily immutable Order-owned historical snapshots; SH-005 only if a current Payment-owned action explicitly needs current entitlement | Correct fees/commission without historical drift | snapshot rate/value/grant reference from Order; current entitlement only when explicitly approved | Depends on action | commission/premium/waiver booleans |
| Marketplace Supply / Digital Goods owner | approved item/tax-code context through Order or target-owner interface | Sales-tax line classification | item type, canonical source ref, tax code/evidence version | Yes if required tax data missing | Offering/Product/Course lifecycle or tax-code ownership outside approved contract |
| Location/checkout evidence owner | approved buyer tax-location facts | Sales-tax jurisdiction input | country/region/postal/city only as required, evidence source/version | Yes if tax provider needs it | public location, coordinate fuzzing, generic jurisdiction owner |
| Sweepstakes / Prize | SH-118 input / source recognition fact | Include recognized prize value in tax reporting | subject, value/currency, jurisdiction, winning/source ID, recognition date, valuation evidence | Tax intake may reject invalid input, but does not change prize lifecycle | PrizeWinning/drawing/fulfillment lifecycle |
| Gamification / Rewards | SH-118 input / source recognition fact | Include recognized reward value in tax reporting | subject, value/currency, source ID/date/evidence | Same | reward/redemption/point rules |
| Media / File Access | SH-087 only when an approved tax/financial document is stored as MediaAsset | Secure private file access | MediaAsset ID, ready/clean state, contextual entitlement | Yes for file view | upload/scan/storage/signed URLs |
| Privacy / Data Erasure | SH-095/096/097 instruction protocol | Fulfill subject requests across Payment-owned truth | target instruction, subject, disposition, exemption references | Yes for destructive action pending retention | privacy request/orchestration/exemption lifecycle |
| Audit / Event Ledger | SH-029/030 | Generic action/access proof | safe action/target/outcome/request context | Audit failure handling per root policy; must not silently bypass mandatory proof | AuditEvent/AccessAuditLog tables/writers |
| Notification | SH-041 | Deliver business messages | intent, recipient reference, safe template variables/sensitivity | No business truth mutation; delivery may retry | SES/SMS/push clients |
| Observability / Ops | SH-034/037/038 and root telemetry | Diagnose integration/jobs safely | safe IDs, operation, provider correlation, failure class | No business-policy block by itself | IntegrationFailure/QueueJob as business status |

### Dependency availability policy

For an irreversible or money-moving action, an unavailable required owner interface fails closed or returns an explicit `unavailable`/retryable result. Payment must not bypass a missing Order/Hold/Authority/step-up/public-owner contract with a direct cross-domain Prisma query.

---

## 14. Outbound Consumers and Effects

### Major consumers

| Consumer | Payment truth consumed | Allowed reaction | Forbidden reaction |
| --- | --- | --- | --- |
| Professional Eligibility | SH-019 financial readiness dimensions | Include Payment result in action-specific seller readiness according to its own timing policy | Read Stripe/KYC/TaxProfile/PayoutAccount tables directly or reduce to `stripeReady` |
| Transaction / Order | normalized verified payment/refund evidence; sales-tax result/evidence | Record Order/RefundStatus/OrderEvent through Order-owned commands | Treat Payment row as Order lifecycle or let Payment write Order tables |
| Sweepstakes / Prize | tax-profile/tax-fulfillment readiness, tax reporting state | Hold/release fulfillment under Prize policy and canonical holds | Let Payment select winner or mutate PrizeWinning lifecycle |
| Gamification / Rewards | tax readiness/reporting facts | Enforce reward fulfillment/reporting policy | Let Payment own RewardRedemption/PointLedgerEntry |
| Admin Review / Compliance Hold | payout/tax case evidence and Payment decisions | Review/request hold/release through owner interfaces | Directly rewrite Payment state outside authorized Payment command |
| Review / Dispute | payout/financial consequence facts where required | Display/respond within dispute workflow | Infer complete payment/refund truth from payout transfer |
| Observability / Ops | safe failure/health/job metadata | Diagnose/retry/reconcile through authorized operations | Treat incident/queue rows as financial status |
| Notification | safe event intent | Deliver notification | Determine payout/tax state from delivery success |
| Privacy | subject inventory/execution/export results | Coordinate legal request | Directly delete provider resources or Payment rows |

### Outbound effects

Payment may:

- call Order public commands with verified provider payment/refund results;
- request Notification delivery;
- append Audit/sensitive-access evidence;
- request/create/release ComplianceHold only through canonical Hold commands where Payment policy produces a justified source condition;
- emit Payment domain events through SH-046;
- enqueue Payment-owned workers through SH-047;
- report operational failures through Observability;
- return Privacy execution results to Privacy;
- expose SH-019 and SH-118 public contracts.

Payment must **not** mutate another Module's source truth directly merely because the same database is available.

---

## 15. Canonical Shared Operations Used

Only operations materially relevant to this Module are listed. The canonical registry remains the source for full shared semantics.

| Canonical operation | Meaning / owner / classification | Why Payment uses it | Invocation point | Payment-local policy | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | Resolve trusted actor. Identity & Access; platform capability. | Every protected financial entry point needs trusted actor context. | Command/query edge. | Which Payment action/target is requested. | typed actor/system context | `payoutAuth.ts`, `currentFinancialUser.ts` |
| **SH-002 `authorizeResourceAction`** | Permission interpretation. Role / Authority; cross-cutting. | Protect own/profile/admin/Order-context reads and mutations. | After validation/actor, before sensitive data or write. | Payment action vocabulary and relationship facts. | allow/deny with authority evidence | local RBAC/isAdmin/owner middleware |
| **SH-003 `queryOwnerFacts`** — **Proposed Ruling** | Small source-owner DTO pattern. | Read narrow Professional/Order/Dispute/item facts without direct repositories. | Cross-owner read. | Exact DTOs needed by Payment. | owner-versioned facts | universal `crossModuleRepository.ts` |
| **SH-011 `evaluateComplianceHold`** | Return applicable reusable stop signs. Admin Review / Compliance Hold. | Payout and approved tax/financial actions can be blocked by canonical holds. | SH-019/payout before reservation/execution; recheck before transfer where policy says. | Which hold scopes block which Payment actions and how represented locally. | hold IDs/scope/safe reasons/expiry | `payoutBlockedService.ts`, local blocked flag |
| **SH-012 `requestComplianceHold`** | Ask Hold owner to create stop sign. | Payment may surface risk/compliance source evidence requiring a hold. | Approved risk/compliance workflow only. | Payment evidence/reason/source. | canonical hold ref/decision | Payment hold table |
| **SH-013 `releaseComplianceHold`** | Ask Hold owner to release. | Payment may indicate its source condition is resolved. | After Payment source remediation. | Whether Payment condition permits requesting release. | release outcome | direct hold status write |
| **SH-014 `requireStepUpForSensitiveAction`** | Fresh MFA/passkey assurance. Identity & Access. | Balance, payout account, tax dashboard/profile, payout request, account changes are high risk. | Before sensitive result/read/mutation. | Which Payment actions require which assurance level. | valid SensitiveActionSession/step-up-required result | payout MFA/session/challenge code |
| **SH-019 `evaluateFinancialReadiness`** | Dimensioned financial readiness. **Owned by Payment; Module public interface.** | Canonical answer for KYC/tax/account/balance/restriction facts. | Professional readiness, payout, CL-10 tax gates. | Exact financial decision policy/reason codes. | dimensioned decision + evidence refs | `canPayout`, `stripeReadyService` |
| **SH-029 `appendAuditEvent`** | Generic important-action proof. Audit / Event Ledger. | High-impact admin/manual payout/tax/reconciliation actions. | After/with approved action per audit contract. | Which Payment actions require generic audit, safe metadata. | append acknowledgment/evidence ref | `FinancialAuditLog`, local generic audit table |
| **SH-030 `recordSensitiveAccess`** | Sensitive read/credential access proof. Audit / Event Ledger. | Tax, payout account, balance, financial document/provider-dashboard access. | On permitted/denied/redacted sensitive access as required. | financial sensitivity/action/target context. | AccessAuditLog evidence | `PayoutAccessLog`, `TaxViewLog` |
| **SH-031 `appendDomainLifecycleEvent`** | Shared append-only domain-event persistence mechanism; separate truth. | Only if a Payment-owned lifecycle event ledger is later approved/needed. | Same transaction as owned state transition. | Payment event meaning/schema. | owner-specific immutable event | reusing AuditEvent as lifecycle truth |
| **SH-034 `sanitizeTelemetryMetadata`** | Remove payment/secrets/personal data from telemetry. Observability/Audit policy. | All sensitive/provider paths. | Before logs/audit/exception/job metadata. | Payment sensitivity labels/allowlists. | safe metadata | raw Stripe/tax payload logging |
| **SH-037 `recordIntegrationFailure`** | Record operational provider/integration failure. Observability / Ops. | Provider outage/timeouts/degradation need diagnostic proof. | On operational failure after domain response determined. | Whether business lifecycle changes separately. | IntegrationFailure/ops ref | provider-error table as business state |
| **SH-038 `recordQueueTelemetry`** | Record attempts/retries/dead-letter. Observability/queue. | Payout/reconciliation/reporting workers. | Every reliable worker attempt. | Payment job completion/failure meaning. | operational attempt telemetry | custom Payment queue ledger |
| **SH-041 `requestNotification`** | Ask Notification owner to deliver. | Requires-input/restricted/payout paid/failed/tax reporting alerts. | After committed Payment fact. | trigger and safe variables. | notification request ref | direct SES/SMS/push |
| **SH-044 `executeIdempotentCommand`** | Effectively-once command result. Platform primitive. | Onboarding, payout, payment, refund, tax/reporting commands. | Application command boundary. | semantic key/fingerprint/conflict/replay result. | claimed/replayed/conflict + result | Payment-local idempotency store |
| **SH-045 `deduplicateDomainEvent`** | Consumer inbox dedupe. Platform event infrastructure. | Prevent repeated Order/refund/dispute/prize/reward effects in Payment projections. | Before source-event side effect. | handler + source event/effect identity. | first/replay claim | processed-order-event boolean/table |
| **SH-046 `publishDomainEvent`** | Transactional outbox publication. Platform event infrastructure. | Publish Payment facts reliably after owned writes. | Same transaction as authoritative Payment mutation where supported. | event name/version/payload and emission rule. | durable outbox event | fire-and-forget `emit()` |
| **SH-047 `enqueueReliableJob`** | Durable job with lease/retry/dead-letter. Shared queue. | Provider processing, reconciliation, payout, tax aggregation/reporting. | After durable intent/outbox or scheduled trigger. | job payload/idempotency/business completion. | durable job ref | module queue/cron table |
| **SH-048 `executeRetryWithBackoff`** | Bounded transient retry. Shared queue/platform. | Provider/transient failures. | Worker/adapter failure. | retryability by Payment operation/provider. | retry/dead-letter decision | custom infinite retry loop |
| **SH-051 `acquireAggregateLock`** | DB-backed serialization. Shared persistence. | Payout/balance reservation and race-sensitive finalization. | Inside DB transaction before conflicting mutation. | lock key, e.g. profile+currency/request/calculation. | acquired/conflict/timeout | in-memory mutex |
| **SH-052 `withOptimisticConcurrency`** | Compare-and-set/version conflict. Shared persistence. | Where Payment mutable aggregate has version support or equivalent expected-state check. | Lifecycle mutation. | stale-state conflict/merge policy. | updated/conflict | last-write-wins status mutation |
| **SH-053 `transitionLifecycleState`** | Shared state-machine plumbing; owner keeps graph. | Apply approved KYC/tax/account/payout/reporting/tax transitions. | Domain/application transition. | legal edges, guards, reasons, event. | resulting canonical state/conflict | generic platform Payment status policy |
| **SH-055 `runDeadlineExpiration`** | Scheduler invokes owner expiry. Shared scheduler/queue. | KYC/tax/provider requirement/reporting expiry where approved. | Scheduled worker. | what expires and resulting owner transition. | processed/ignored/failed counts | custom cron truth table |
| **SH-056 `executeAtomicReservation`** | Reserve scarce value atomically. Shared DB primitive. | Prevent concurrent payout overspend. | PayoutRequest transaction. | available-funds calculation, reservation/release entries. | reservation success/conflict | wallet lock/reserved-balance mutable row |
| **SH-059 `verifyProviderWebhookSignature`** | Authenticate provider callback. Shared integration security. | Mandatory before provider event use. | Raw webhook edge. | Stripe/provider secret/config and accepted endpoint. | verified provider event envelope / rejection | `verifyStripeWebhook.ts` clone |
| **SH-060 `deduplicateProviderEvent`** | Claim provider event once; provider owner keeps truth. | Prevent duplicate Stripe side effects. | Immediately after signature, before side effect. | Payment's `ProcessedStripeEvent` semantics and event applicability. | first/duplicate claim | AuditEvent/WebhookLog as dedupe |
| **SH-061 `translateProviderStatus`** | Map provider status to owner enums. Provider-adapter contract. | Keep canonical KYC/account/payout/tax vocab stable. | Adapter after verified/deduped callback/query. | Mapping tables/version and unknown-state behavior. | canonical status/result + mapping metadata | global ProviderStatus enum |
| **SH-062 `reconcileProviderState`** | Detect/repair divergence. Provider owner using shared worker framework. | Recover missed webhook/ambiguous provider effects. | Scheduled/admin recovery. | compare fields, safe repair vs escalation. | reconciled/no-op/manual-review/failure | global Stripe sync that edits foreign truth |
| **SH-063 `captureProviderSnapshot`** | Owner-specific provider state snapshot. | Explain payout/KYC requirements safely. | After provider account requirement update/reconcile. | allowlisted fields/retention. | ProviderRequirementSnapshot | generic provider snapshot truth |
| **SH-070 `deleteProviderResource`** | Provider resource deletion/revocation after authorized Privacy/lifecycle command. | Execute approved external deletion while respecting retention/provider capability. | Privacy executor. | retain/delete semantics and local aftermath. | deleted/absent/retained/retryable/terminal | Privacy calling Stripe directly |
| **SH-078 `minimizeAndRedactProviderInput`** | Minimum purpose-bound provider payload. | Prevent sensitive leakage to providers/logging. | Before provider call/telemetry serialization. | required fields/purpose/sensitivity. | validated minimized payload | serializing domain object wholesale |
| **SH-087 `issueSignedMediaUrl`** | Media-owned short-lived private URL. | Only if approved Payment contextual docs are MediaAsset-backed. | Protected document view. | Payment business entitlement/sensitivity. | short-lived URL/grant evidence | local presign/S3/R2 helpers |
| **SH-095 `executePrivacyInstruction`** | Execute Privacy-owned disposition against owner data. | Payment privacy fulfillment. | Privacy dispatch. | field/provider/retention handling. | typed execution result | Payment PrivacyRequest workflow |
| **SH-096 `enumerateSubjectData`** | List Payment-owned subject data. | Privacy inventory/export/planning. | Privacy request orchestration. | Payment record/provider scope. | target list/counts/safe refs | generic cross-domain scan |
| **SH-097 `evaluateRetentionRequirement`** | Supply retention facts; Privacy owns exemption. | Prevent illegal destructive financial/tax deletion. | Before destructive instruction. | Payment record class/legal reason/known period. | retain/erasable facts + evidence | local exemption flag/table |
| **SH-098 `anonymizePersonalFields`** | Shared deterministic anonymization mechanics; owner mapping. | Minimize permitted Payment personal metadata. | Approved privacy action. | exact fields/retention meaning. | anonymized field result | universal blind eraser |
| **SH-108 `requestOrderRefund`** | Order coordinates refund; Payment executes rail. | Preserve RefundStatus/Order ownership. | Approved refund flow. | provider execution/result/economic/tax effects. | correlated refund result | Payment-owned refund case/status lifecycle |
| **SH-109 `snapshotExternalDecision`** | Persist external decision at historical lifecycle owner. | Preserve commission/entitlement/tax decision where history requires. | Transaction creation/settlement policy snapshot. | Which decision/fields are historically required. | immutable snapshot at consuming owner | re-read today's plan/price for old Order |
| **SH-117 `aggregateYearlyReportableValue`** | Source-event-safe yearly aggregation; separate truths. | Build TaxYearEarningsSummary without stealing source domains. | SH-118/source event intake. | Payment tax buckets/regime/jurisdiction rules. | updated/reconciled summary | cross-domain tax ownership |
| **SH-118 `reportTaxableValue`** | Canonical tax-reporting intake owned by Payment. | Prize/Reward/earning owners report recognized value. | After source recognition event. | tax subject/year/jurisdiction aggregation and filing policy. | accepted/replayed/rejected tax intake result | Payment prize/reward logic |
| **SH-120 `normalizeJurisdictionContext`** — **Unresolved** | Proposed shared jurisdiction normalization; owner unresolved. | Potential future input normalizer for tax. | **Do not depend on now.** | Payment keeps tax evidence/selection policy until root ruling. | none until approved | locally declaring SH-120 canonical or building universal jurisdiction service |
| **SH-123 `validateOwnedTargetReference`** | Target owner validates external reference. | Validate polymorphic/context source refs when needed. | Before persisting reference/using tax context. | Which target types Payment accepts. | valid target facts/ref version | arbitrary target-type Prisma lookup |

### Shared-operation status rule

- Confirmed SH operations may be implementation dependencies.
- Proposed SH operations such as SH-003 and the shared decision envelope may guide DTO shape but must not become new platform schema/API authority until approved.
- Unresolved SH-120 is explicitly **not** an implementation dependency.

---

## 16. Module-Internal Operations

These operations remain local because sharing them would transfer Payment policy or truth.

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `composeFinancialReadiness` | Build SH-019 dimensions/reasons from Payment records + approved external hold/step-up facts | action, subject, KYC/tax/account/balance/hold facts | Payment decision | none | Financial policy is Payment-owned. |
| `deriveProfessionalBalance` | Sum/classify ledger entries by availability/effect | entries, time, currency | available/held/requested/paid projection | none | Ledger type/sign/availability semantics are Payment policy. |
| `validateLedgerEffect` | Enforce effect type, sign, source, currency, availability rules | proposed ledger effect | valid effect/error | ledger write | Prevents generic ledger helper from owning financial meaning. |
| `mapSourceEffectToLedgerEntries` | Convert authoritative Order/refund/dispute/payout event into one or more Payment effects | source event/decision snapshot | proposed ledger entries | ledger | Economic consequence mapping belongs to Payment. |
| `evaluatePayoutSufficiency` | Decide amount can be reserved/transferred | profile/currency/derived balance/request | allow/block + amount context | none | Funds availability/release policy is local. |
| `selectPayoutAccount` | Resolve approved account under explicit selection rule | profile, requested account, current accounts | account/refusal | none | Multi-account policy is Payment-specific and currently unresolved in full. |
| `translatePaymentProviderResult` | Interpret Payment-specific provider operation | normalized adapter result | Payment command input | target Payment record | Provider mapping is owner-specific even though shell is shared. |
| `buildSalesTaxRequest` | Construct tax-provider request from Order/location/item evidence | owner snapshots | minimized provider tax request | none | Tax evidence and provider-code interpretation are Payment policy. |
| `applySalesTaxResult` | Convert normalized provider calculation into Payment tax records | provider result + Order snapshot | calculation/lines | sales-tax truth | Liability/calculation semantics belong here. |
| `determineTaxReportingRequirement` | Evaluate approved regime/year/jurisdiction reporting rules | yearly summary, TaxProfile, versioned rule set | required/blocked/ready decision | summary/submission state as approved | Tax reporting policy is not a generic threshold utility. |
| `buildTaxReportingRecipient` | Freeze recipient filing snapshot | year summary/tax profile/rule version | recipient row data | recipient | Filing snapshot meaning belongs to Payment. |
| `reconcilePaymentAggregate` | Compare provider vs canonical Payment state and issue safe owner commands | aggregate/provider state | repaired/no-op/escalated | Payment records + owner commands | Repair policy must preserve Payment/Order ownership. |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Provider event dedupe:** reuse SH-060 claim mechanics; Payment keeps `ProcessedStripeEvent`. Trust/Calendar/Video/Track keep their own provider-event truths. Never create one universal “processed provider event” table by inference.
2. **Domain event dedupe:** SH-045 consumer inbox prevents duplicate Order/Dispute/Prize/Reward effects. It is separate from `ProcessedStripeEvent` because source domain events and provider callbacks are different evidence.
3. **Append-only ledgers:** shared append-only persistence conventions may be reused, but `ProfessionalBalanceLedgerEntry`, `PointLedgerEntry`, `OrderEvent`, and `AuditEvent` remain different truths with different policy.
4. **Readiness response:** SH-019 may align with the proposed shared decision envelope, but Payment's reason namespace, dimensions, evidence, and action semantics remain Payment-owned.
5. **Provider snapshots:** SH-063 mechanics may be shared; `ProviderRequirementSnapshot` remains Payment evidence and cannot become generic provider truth.
6. **Lifecycle state machine:** SH-053 handles transition plumbing; Payment owns every graph/guard/reason for its enums.
7. **Concurrency:** SH-051/052/056 provide DB mechanisms; Payment defines lock key, sufficiency, reservation, conflict, and replay behavior.
8. **Yearly aggregation:** SH-117 provides source-event/reconciliation mechanics; `TaxYearEarningsSummary`, `PrizeTaxYearSummary`, and reward/source summaries remain separate truths.
9. **Privacy anonymization:** SH-098 supplies mechanics; Payment decides fields, legal retention, provider consequences under Privacy instruction.
10. **Historical snapshots:** SH-109 supplies pattern; the lifecycle owner that needs historical proof owns the snapshot. Payment must not centralize Order's commission/entitlement history.
11. **Audit:** generic action/access audit is separate from financial ledger, payout history, provider event claim, tax filing proof, and domain events.
12. **Observability:** IntegrationFailure/SystemEvent/QueueJob are operational; they never substitute for a failed/restricted/pending Payment status.

---

## 18. Authentication and Authorization

### Authenticated actor

Every user-initiated protected command/query begins with SH-001. System workers/webhooks use an approved system/provider actor context and request/correlation IDs; they do not impersonate a User.

### Authority

SH-002 interprets permissions. Payment supplies action/relationship facts such as:

- subject User ID;
- ProfessionalProfile ID and owner relationship from Professional owner facts;
- Order participant context from Order owner facts;
- whether the operation is self-service, admin/support, or system-provider processing;
- target Payment record and permitted action vocabulary.

Example Payment action vocabulary should be typed/versioned, not free-form client strings:

```text
financial_setup.read
kyc.start
tax_profile.read
tax_profile.manage
payout_account.read
payout_account.manage
balance.read
payout_request.create
payout_request.review
payout_transfer.reconcile
sales_tax.read
sales_tax.reconcile
tax_reporting.read
tax_reporting.manage
```

Exact authority mapping remains Role / Authority-owned.

### Resource ownership

- A Professional self-service action must resolve profile ownership from Professional Eligibility rather than trusting a client-provided User/profile pair.
- Order payment/tax context must come from Order's public snapshot/query and include participant/amount/version facts sufficient for Payment's operation.
- Admin/support authority does not automatically grant access to raw financial data; Payment still enforces sensitivity/step-up/audit policy.

### Step-up

At minimum, supplied evidence requires fresh step-up before showing/using:

- processor-held balance;
- payout account details;
- tax profile/tax dashboard;
- payout request flow;
- payout-account changes.

Any expansion of step-up coverage is Payment action policy plus Identity security policy; Payment does not implement challenges/sessions.

### Sensitive access proof

When required, SH-030 records allowed/denied/redacted/credential-issued access with `DataSensitivity.financial` or the canonical sensitivity classification. The access log is not the financial record itself.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Underlying truth owner | Payment action gated | Local composition | Result |
| --- | --- | --- | --- | --- |
| KYC / AML payout gating | **Payment** (`KycVerification`, PayoutAccount/provider evidence) | receive/payout actions; other timing only if separately approved | SH-019 maps current KYC dimension to action | allowed/blocked/requires input/review |
| Tax-profile readiness | **Payment** (`TaxProfile`, TaxDocument) | payout/reporting/prize/reward tax requirements as approved | separate dimension; never sales-tax substitute | dimension/reason/evidence |
| Payout-account readiness | **Payment** | payout | active/enabled/account requirement policy | dimension/reason |
| Available balance | **Payment** ledger projection | payout amount | current profile+currency projection minus held/reserved consequences | sufficient/insufficient |
| ComplianceHold | Admin Review / Compliance Hold | payout and approved financial/tax fulfillment actions | SH-011; Payment maps applicable scope to local action | block/review/allow |
| Step-up assurance | Identity & Access | sensitive read/mutation, payout request | SH-014 before sensitive result/action | assurance or step_up_required |
| Order transaction eligibility | Transaction / Order | payment/refund/tax execution | consume Order version/snapshot/public command | proceed/conflict/deny |
| Dispute/refund source decision | Review / Dispute + Order | ledger/payout/refund money effect | consume approved outcome; map economic consequence | append/hold/reverse/no-op |
| Historical commission/fee | Order snapshot, originally Track policy | ledger earning/net effect | use immutable Order snapshot | amount/effect only |
| Prize/Reward source recognition | Prize/Rewards owner | SH-118 tax intake | validate source identity/value evidence only | accepted/replay/rejected |

### U-01 boundary

Whether full KYC/tax/payout-account readiness is required before **ProfessionalProfile activation, Offering publication, or Gig response** remains a CL-03 Unresolved Decision. Payment exposes facts; Professional Eligibility/Marketplace/Gig action owners must not let Payment silently decide their timing.

---

## 20. Provider Integrations

### 20.1 Provider-neutral ports

The Module owns ports for distinct financial capabilities:

```text
PaymentRailPort
PayoutProviderPort
KycProviderPort
TaxProfileProviderPort
SalesTaxProviderPort
TaxReportingProviderPort
```

A Stripe adapter can satisfy several ports, but domain/application services only consume the relevant port contract.

### 20.2 Current provider posture

Supplied evidence establishes Stripe, Stripe Connect, Stripe webhooks, Stripe Tax/Checkout automatic tax, with possible future tax/KYC alternatives such as Avalara or other approved providers. Provider selection beyond the established Stripe path remains adapter/configuration policy and is not domain truth.

### 20.3 Credentials

Credentials/secrets remain in root-approved secret/configuration infrastructure. They must never be stored in Payment business tables, logs, events, or client bundles.

### 20.4 Webhook pipeline

```text
raw provider request
→ SH-059 verify signature using raw body
→ validate event envelope/schema
→ SH-060 claim event in owner-specific dedupe truth
→ SH-061 translate supported provider value/status
→ load current Payment aggregate and validate transition
→ Payment-owned authoritative write + outbox
→ if Order truth must change, invoke idempotent Order public command
→ record only safe operational telemetry
```

No client redirect or unverified webhook may mark a payment, payout, KYC, tax, or Order state successful.

### 20.5 Provider event dedupe

`ProcessedStripeEvent.eventId` is Payment's current Stripe claim truth. See UD-04 for incomplete claim-processing-state semantics and UD-05 for cross-Stripe-domain routing scope.

### 20.6 Status/error translation

Provider-native strings/errors never escape as business API contracts. SH-061 adapters return canonical Payment status/result, retryability, safe error category, provider reference, mapping version, and correlation context. Unknown status must produce explicit unsupported/review behavior, not a guessed mapping.

### 20.7 Retry

- retry transport/timeouts/rate-limit/approved transient provider failures with SH-048;
- never blindly retry an irreversible money movement after an ambiguous timeout without idempotency/reconciliation;
- legal denial, insufficient funds, invalid input, hold denial, explicit provider rejection, or unsupported status are not “network retries.”

### 20.8 Reconciliation

SH-062 compares canonical Payment state to provider state and may:

- no-op when aligned;
- apply a missing Payment-owned transition idempotently;
- re-issue an idempotent Order owner command for a verified result;
- append a missing financial/tax effect only after source-effect dedupe;
- mark for manual review/incident when divergence cannot be safely repaired.

It must never patch Order rows directly.

### 20.9 Provider deletion

Under Privacy instruction and retention policy, Payment invokes SH-070 through its provider adapter. Result states include deleted, absent, retained, retryable failure, terminal failure. Privacy remains orchestration owner.

### 20.10 Operational failure reporting

Use SH-037 IntegrationFailure/ops telemetry. Provider failure does not replace KYC/PayoutTransfer/TaxProfile/SalesTax state; owner lifecycle changes only where Payment policy explicitly defines the effect.

---

## 21. Events and Outbox

### Domain event families

The following names are **Proposed Rulings** and should be frozen/versioned by the implementing feature, not treated as already canonical:

```text
payment.kyc.status_changed.v1
payment.tax_profile.status_changed.v1
payment.payout_account.status_changed.v1
payment.balance.effect_recorded.v1
payment.payout_request.status_changed.v1
payment.payout_transfer.status_changed.v1
payment.sales_tax.calculation_changed.v1
payment.sales_tax.transaction_changed.v1
payment.tax_reporting.requirement_changed.v1
payment.tax_reporting.submission_changed.v1
payment.tax_reporting.recipient_changed.v1
```

### Event emission

- Emit only after the corresponding Payment-owned fact exists.
- Use SH-046 transactional outbox with local DB write where possible.
- Do not emit “please update Order” disguised as a domain event. When Payment requires an Order mutation, call the approved Order command; events describe the Payment fact that occurred.

### Payload minimization

Minimum event envelope follows canonical shared event requirements:

- event ID/type/schema version;
- source Module;
- aggregate type/ID/version or owner sequence if available;
- occurredAt;
- correlation/causation IDs;
- safe actor/system context;
- privacy classification;
- minimized changed fact/reason category.

Never emit raw provider payloads, tax identifiers, bank details, raw requirements JSON, full failure text, documents, or secrets.

### Aggregate/version expectation

Many current Payment models lack an explicit `version` field. Until a schema version is approved, event payload should carry an immutable source state reference/timestamp/provider event/ref sufficient for consumers to re-query current truth; consumers must not treat an old event payload as current state in race-sensitive workflows.

### Consumer idempotency

Consumers use SH-045/inbox. Payment also uses SH-045 for inbound Order/Dispute/Prize/Reward events. Exactly-once transport is not assumed; business effects must be effectively-once.

---

## 22. Background Jobs / Scheduled Work

Generic queue, lease, retry, dead-letter, and telemetry mechanics use SH-047/048/038. Payment owns job meaning only.

| Worker | Purpose | Input | Idempotency key | Retryable failures | Permanent/manual-review | Business truth updated | Telemetry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `payment-provider-event-worker` | Apply verified event asynchronously if webhook edge only claims/enqueues | provider event ID/ref | provider+event ID+handler version | transient DB/provider-owner command outage | unknown event/status, invariant conflict | Payment target state; Order command if required | SH-038 + correlation |
| `payment-provider-reconciliation-worker` | Detect missed/divergent Stripe/Connect/Tax effects | provider/account/time cursor | provider+target+window/run | provider/API transient | irreconcilable divergence | Payment state via same commands | SH-037/038 |
| `payout-transfer-worker` | Execute approved payout transfer | payout request/transfer ID | transfer idempotency key | transient provider, safe retry | terminal provider reject, ambiguous unreconciled result | PayoutTransfer/Request + ledger | SH-038 |
| `payout-reconciliation-worker` | Repair transfer result after timeout/missed callback | transfer ID/provider ref | transfer+reconcile version | provider/API transient | mismatched amount/account or unsupported state | PayoutTransfer/Request/ledger through owner commands | SH-037/038 |
| `financial-source-effect-worker` | Apply Order/refund/dispute source effects to ledger | source domain event ID | handler+event/effect key | source owner unavailable/DB transient | invalid source snapshot | ledger entries | SH-045/038 |
| `tax-year-aggregation-worker` | Reconcile reportable yearly totals | tax subject/jurisdiction/year/currency/source window | tax subject+jurisdiction+year+currency+run/version | source query transient | unresolved subject representation/persistence/rule conflict | TaxYearEarningsSummary | SH-038 |
| `tax-reporting-preparation-worker` | Identify ready/blocked reporting recipients under approved rules | year/regime/jurisdiction | reporting run/version | source/provider transient | missing legal rule/profile data | submission/recipient drafts | SH-038 |
| `tax-reporting-submission-worker` | Submit approved filing bundle | submission ID | provider+submission+version | safe provider transient | rejection/legal/provider unsupported | TaxReportingSubmission/Recipients | SH-037/038 |
| `sales-tax-payment-reconciliation-worker` | Reconcile tax/payment proof with provider and Order command effects | Order/provider refs | order+provider+window/version | provider/Order unavailable | inconsistent immutable amount/version | Payment tax state; Order command only | SH-037/038 |
| `financial-expiry-refresh-worker` | Apply approved expiry/refresh policy to KYC/tax/account facts | target/time | target+deadline+policy version | transient DB/provider | unresolved expiry/reopen semantics | Payment lifecycle through SH-053 | SH-055/038 |

### Dead-letter behavior

Dead-lettered jobs remain operational evidence, not business truth. An operator may invoke an authorized retry/reconciliation command, but must not manually “mark paid/verified” in queue tooling to clear an incident.

---

## 23. Concurrency and Idempotency

### 23.1 Provider callbacks

- Lock/claim: `ProcessedStripeEvent.eventId` unique primary key.
- Signature verification precedes claim.
- Duplicate claim produces no repeated business effect.
- If claim and Payment write can be in one DB transaction, do so.
- Cross-Module Order command cannot be made transactional with Payment DB state by pretending a distributed transaction exists; use stable idempotency/correlation plus reconciliation.

### 23.2 Ledger source effects

Current `ProfessionalBalanceLedgerEntry` lacks a source-effect uniqueness constraint.

**Proposed Ruling PT-02:** before production source-event projection, define a durable source-effect identity sufficient to prove that one authoritative Order/refund/dispute/payout event produces each intended ledger effect once. This may be a dedicated unique `(sourceModule, sourceEventId, effectKey)` field/model or an approved inbox+transaction invariant that remains durable when operational inbox retention changes. Do not rely on “query then insert” without a DB-enforced conflict boundary.

### 23.3 Payout reservation

Preferred lock key:

```text
professionalProfileId + currency
```

using SH-051 and SH-056 or an equivalent root-approved serializable DB transaction.

Transaction should:

1. re-derive available funds from authoritative ledger state at transaction time;
2. evaluate current conflicting reservations/held effects;
3. validate requested amount;
4. create PayoutRequest;
5. append reservation/request ledger effect under the same atomic boundary if that is the approved ledger model;
6. commit once.

No in-memory lock or mutable cached balance is sufficient.

### 23.4 Payout transfer

`PayoutTransfer.idempotencyKey` is unique. The semantic key must bind request/account/amount/currency/provider operation. Provider idempotency key must be stable across retry of the same intended transfer and different for a genuinely new attempt under approved retry semantics.

### 23.5 Sales tax

- Calculation/finalization binds to exact Order/pricing version and buyer tax-location evidence.
- Duplicate calculate/finalize commands replay safely.
- Finalization and tax transaction recording must prevent duplicate provider transaction evidence.
- Current schema lacks strong “one finalized calculation per Order/version” and provider transaction uniqueness; see UD-16/UD-18.

### 23.6 Tax reporting

- SH-118 input is idempotent by source recognition identity.
- Year summary aggregation uses source-event uniqueness + transaction.
- Recipient/submission generation must prevent duplicate subject inclusion.
- Current schema gaps must be resolved before automated production filing.

### 23.7 Optimistic/pessimistic strategy

Use database row/advisory locks, serializable transactions, unique constraints, or expected-state compare-and-set as appropriate. Models without a version field may use locked current-status validation rather than inventing an application-only version. No distributed in-memory mutex is allowed for financial invariants.

### 23.8 Replay result

Every idempotent public command returns the canonical original/current safe result for the same semantic request. A reused key with materially different fingerprint returns conflict, not a second effect.

---

## 24. Media / Storage

### Business attachment meaning

The current Payment schema primarily stores provider references (`providerDocId`, provider IDs) rather than Payment-owned Media joins. Therefore a generic tax/KYC file library is **not** part of this Module by default.

### If an approved Payment file workflow is introduced

- `MediaAsset` remains file/storage/scanning truth.
- Payment owns only business meaning/entitlement of a contextual tax/financial document reference.
- Upload must use Media's validated upload context and allowed type/size/sensitivity policy.
- Private asset must be READY/clean before use.
- Access uses SH-087 signed Media URL mechanics.
- Sensitive view uses SH-014/SH-002/SH-030 as required.
- No permanent public URL.
- No raw original filename as object key.

### Prohibited

`taxFileStorage.ts`, `kycPresign.ts`, local malware scanner, S3/R2 client, permanent provider document URL, or raw SSN/bank credential attachment without an explicit legal/security architecture ruling.

---

## 25. Search / Projection

Payment financial truth is generally **not public search content**.

- There is no Payment-owned `SearchUpsertEvent`.
- Payment never calls Typesense directly.
- Payment does not expose raw KYC/tax/payout state in Search documents.
- A Payment readiness change may cause Professional Eligibility/Marketplace to reevaluate an action/public-readiness decision. That source owner decides whether its public source projection changes and, if so, requests Search refresh.
- Search must not reconstruct financial readiness from `stripeReady`, provider IDs, KYC rows, or payout account flags.

Any future public financial-derived badge requires an explicit product/privacy/source-owner ruling and a safe owner projection; it cannot emerge from ad-hoc indexing.

---

## 26. Notification

Payment owns **why** a notification should occur; Notification owns delivery.

Potential approved triggers:

- KYC requires input / KYC restriction changed;
- tax profile/document requires input;
- payout account requires action/restricted;
- payout request received/blocked/approved/processing;
- payout transfer paid/failed/reversed;
- tax reporting action required or filing accepted/rejected;
- provider onboarding session/action requiring user continuation.

Payload intent contains only safe identifiers and human-safe remediation category. Never include SSN/tax ID/bank details, raw provider requirement arrays, sensitive failure payload, full financial balance unless specifically approved for the delivery channel, or provider dashboard secrets.

Use SH-041. Delivery failure does not roll back Payment truth unless an explicit legal workflow says notification delivery itself is a condition; such a condition is not established for this Module by current evidence.

---

## 27. Audit and Sensitive Access

### Domain truth vs audit

- `ProcessedStripeEvent` = provider-event dedupe truth.
- `ProfessionalBalanceLedgerEntry` = financial accounting effect truth.
- Payout/Tax/KYC records = business/compliance lifecycle truth.
- Payment domain events = source-owner change facts.
- `AuditEvent` = generic action proof.
- `AccessAuditLog` = sensitive data access proof.
- `IntegrationFailure/SystemEvent/QueueJob` = operational diagnostics.

These are never interchangeable.

### SH-029 audit candidates

At minimum, architecture should consider audit for:

- manual/admin KYC/tax/payout status interventions that are explicitly allowed;
- payout request approval/block/cancellation/manual adjustment;
- manual balance adjustment/correction entry;
- manual reconciliation action;
- tax reporting submission/correction/retry initiated by admin/system under material authority;
- provider resource deletion/retention decision execution;
- high-impact configuration/rule/provider changes where root policy requires audit.

### SH-030 sensitive access candidates

- balance/history view;
- payout-account view/update;
- tax profile/dashboard/document reference view;
- provider requirement/detail view if sensitive;
- protected financial document URL issuance/view;
- denied/redacted admin/support access.

Audit metadata is schema-validated, minimized, and correlation-aware. Never put raw provider payloads or tax/bank identifiers in audit metadata.

---

## 28. Privacy and Retention

### Subject-data inventory

Payment must enumerate at least:

- `KycVerification`;
- `TaxProfile` and `TaxDocument`;
- `PayoutAccount` and `ProviderRequirementSnapshot`;
- `ProfessionalBalanceLedgerEntry`;
- `PayoutRequest` and `PayoutTransfer`;
- `TaxYearEarningsSummary`;
- `TaxReportingSubmission` and `TaxReportingRecipient`;
- `SalesTaxCalculation`, `SalesTaxLineItem`, `SalesTaxTransaction`;
- Payment-held provider references and provider resources;
- Payment domain-event payloads if they contain subject-identifying data;
- any approved Payment contextual Media references.

### Privacy target executor

Payment registers SH-096 enumeration and SH-095 execution/export handlers. Privacy owns request verification, deadlines, dispatch, aggregation, export bundle, completion, and `DataRetentionExemption`.

### Erase/anonymize/revoke/retain behavior

- Erase or anonymize nonessential personal metadata where the Privacy instruction allows it.
- Do not destructively erase financial/tax/fraud/dispute evidence that has an approved retention requirement.
- Use SH-097 to return retention facts; Privacy records the exemption.
- Use SH-098 for approved deterministic anonymization mechanics.
- Use SH-070 for provider resource deletion/revocation when legally permitted and provider-supported.
- If a Payment document is Media-backed, use Media deletion/access mechanisms; Payment does not delete storage objects directly.

### Legal retention

Exact retention durations for KYC/tax/payout proof are **Unresolved U-18**. Therefore:

- destructive privacy deletion for affected retained records is production-gated until legal policy is supplied;
- do not encode invented “7-year” or similar universal values;
- product archive/status changes are not privacy erasure;
- provider deletion must respect the same retention decision.

### TaxDocument cascade concern

Current Prisma cascades TaxDocument deletion with TaxProfile. Privacy execution must not blindly delete TaxProfile if TaxDocument must be retained. A retention-safe deletion/anonymization plan must be explicitly verified before destructive operations.

### Export contribution

Export only user-understandable, safe Payment data required by Privacy policy. Do not expose internal provider secrets, risk rules, webhook payloads, or third-party data that the user is not entitled to receive.

---

## 29. Observability

### Structured logs

Every Payment command/worker/provider operation should carry:

- request ID / correlation ID / causation ID when applicable;
- operation name and version;
- safe target IDs (Payment record IDs, Order ID where permitted);
- provider name and safe provider request/event reference;
- attempt number, latency, result category, retryability;
- worker/job ID where applicable;
- environment/release metadata through shared telemetry.

### Safe dimensions

Allowed by default: internal UUIDs, enum/result categories, currency code, provider name, status transition names, counts, durations, retry/dead-letter category.

Do not log:

- raw webhook body;
- payment method data;
- bank/routing/account numbers;
- SSN/TIN/EIN or raw tax identity;
- raw KYC documents/images;
- provider secrets/signatures;
- full `requirementsDue`/provider requirements without redacted schema;
- exact buyer address unless explicitly necessary in a protected audit/evidence record;
- full provider error bodies.

### Operational records

- SH-037 IntegrationFailure for provider/integration degradation;
- SH-038 QueueJob/attempt telemetry for workers;
- shared metrics for webhook duplicates, provider errors, reconciliation drift, payout latency/failure/reversal, ledger projection mismatches, tax calc failures, reporting jobs;
- health checks for configured adapters without exposing secrets.

Operational records never substitute for canonical Payment statuses.

---

## 30. Security Boundaries

1. **Server-side validation:** Zod/schema validation at every user/server/provider trust boundary. TypeScript types alone are not runtime validation.
2. **Raw webhook verification:** provider signature uses raw body before JSON is trusted.
3. **Provider-hosted sensitive collection:** prefer Stripe/provider-hosted onboarding for identity, tax, and bank data; do not collect/store raw secrets merely for convenience.
4. **Step-up:** require SH-014 before defined sensitive reads/mutations.
5. **Authorization:** SH-002 server enforcement; UI hiding never grants permission.
6. **Sensitive access logging:** SH-030 where required by financial sensitivity.
7. **Credential isolation:** provider API keys/webhook secrets stay in root secret manager/config; never database/business DTO/client/log.
8. **Payload minimization:** SH-078 before provider calls and SH-034 before telemetry.
9. **Money representation:** integer minor units + explicit ISO currency. No floating-point money arithmetic.
10. **Provider error isolation:** convert to safe category; raw provider exceptions do not leak to clients.
11. **Idempotency:** public write keys cannot be used to create a materially different command silently.
12. **Concurrency:** DB-backed locks/constraints; no in-memory financial mutex.
13. **Rate limiting:** sensitive/high-risk endpoints use root-approved rate-limit/abuse controls where required; Payment does not create a parallel rate-limit framework.
14. **Temporary onboarding secrets:** provider session/client secrets are short-lived, purpose-bound, returned only to authorized clients, never persisted/logged unless provider contract explicitly requires a safe reference.
15. **Document safety:** any binary artifact uses Media; no local financial-document storage pipeline.
16. **No public finance projection:** KYC/tax/payout data is excluded from public Search and generic client telemetry.

---

## 31. Error / Decision Result Pattern

### Public error categories

Payment interfaces should use stable, provider-neutral categories:

```text
validation_error
authentication_required
authorization_denied
step_up_required
not_found
conflict
stale_state
blocked
insufficient_funds
requires_input
review_required
unsupported
provider_unavailable
retryable_failure
terminal_failure
unavailable
```

The exact TypeScript/Zod contract is fixed by the implementing feature.

### Financial decision envelope

SH-019 may align with SH-015's proposed common decision shape without making SH-015 a hard platform dependency until approved:

- `decision`: allowed / denied / warning / review_required / step_up_required / unavailable;
- Payment-owned stable reason codes;
- blocking vs warning distinction;
- safe evidence references;
- evaluatedAt;
- Payment policy version/source versions where available;
- recheck/expiry time if meaningful;
- retryability;
- safe next action/remediation.

### Provider errors

Never return a raw Stripe error, provider requirement payload, provider-native status, or SDK exception as public contract. Adapter returns safe category + provider reference/correlation; operational details go to redacted telemetry.

### Conflict semantics

A stale Order/version, status transition, payout reservation, or idempotency fingerprint returns explicit conflict. Do not silently rebase an irreversible money operation on new facts.

---

## 32. Testing Architecture

### Domain unit tests

- SH-019 dimension composition and reason-code exposure;
- lifecycle transition guards for every implemented edge;
- ledger sign/type/availability math and correction rules;
- payout sufficiency/reservation/release logic;
- sales-tax calculation result validation/liability handling;
- tax reporting requirement/aggregation rules for approved rule fixtures;
- provider mapping unknown/unsupported values;
- safe notification/audit/telemetry payload builders.

### Database / integration tests

- `ProcessedStripeEvent` concurrent duplicate claim;
- payout lock/reservation prevents overspend;
- `PayoutTransfer.idempotencyKey` uniqueness/replay;
- ledger source-effect dedupe invariant once approved;
- transactional owner write + outbox;
- tax calculation/finalization/reversal persistence;
- yearly aggregation idempotency;
- recipient/submission duplicate protections once approved;
- retention-safe relational behavior for Payment records.

### Public contract tests

- SH-019 response dimensions/reason stability/no provider leakage;
- SH-118 input/replay/result;
- Order payment/refund command DTOs prove no direct Order write;
- ProfessionalProfile owner-facts contract;
- ComplianceHold/step-up/audit integrations;
- Privacy executor result contract.

### Authorization/security tests

- owner vs unrelated User vs support/admin roles through SH-002;
- step-up required/expired/wrong-action/wrong-target;
- sensitive access creates SH-030 evidence where mandatory;
- webhook invalid signature, wrong secret, stale timestamp/replay;
- provider payload validation rejects unexpected/unsafe data;
- no secret/raw tax/bank/provider payload in logs/events/notifications.

### Provider adapter tests

- Stripe/Connect/Tax mapping fixtures;
- signature/dedupe/translation ordering;
- transient vs terminal retry classification;
- provider idempotency key reuse;
- timeout/ambiguous transfer → reconciliation before retry;
- reconciliation after missed webhook/out-of-order event;
- unknown provider state fails safe.

### Privacy/compliance tests

- enumeration covers all Payment-owned subject records;
- retention blocks destructive erase when exemption required;
- anonymization preserves required financial referential integrity;
- provider deletion obeys retention/capability;
- TaxDocument cascade cannot bypass retention policy;
- no hardcoded universal tax threshold/form unless approved rule fixture/version says so.

### E2E participation tests

1. financial onboarding → KYC/tax/payout account → SH-019 readiness;
2. completed/eligible Order source effect → one ledger earning → balance view;
3. concurrent payout requests cannot overspend → one valid transfer execution;
4. verified payment/tax provider result → Payment proof → Order owner command → no direct Order write;
5. duplicate webhook → no duplicate Order command/ledger/tax transaction;
6. dispute/refund/hold consequence → Payment money effect without Payment owning case;
7. Prize/Reward reportable value → one tax summary effect without lifecycle theft;
8. Privacy instruction → retention-aware Payment executor result;
9. provider outage/recovery → retries/reconciliation/dead-letter without false business success.

---

## 33. Module Invariants

### Rules coding agents must never violate

1. `payment_payout_tax` is the sole owner of its KYC, tax-profile, payout-account, payout, financial-ledger, tax-reporting, sales-tax, and Payment Stripe-event truth.
2. Order remains paid transaction truth; Payment must never directly mutate `Order.status`, `RefundStatus`, `OrderEvent`, or Agreement lifecycle.
3. A provider object, webhook, client redirect, or provider dashboard is not Workin Ants business truth until verified, deduplicated, translated, and applied by owner policy.
4. `ProcessedStripeEvent` is provider-event dedupe truth, not AuditEvent, OrderEvent, QueueJob, or general Stripe business history.
5. Do not process the same provider event twice into duplicate business effects.
6. Financial KYC (`KycVerification`) is separate from Trust `VerificationCheck`/TrustBadge.
7. `TaxProfile`/TaxDocument readiness is separate from transaction sales tax.
8. `ProfessionalProfile.stripeReady`, `stripeAccountId`, verification summary fields, or similar compatibility fields are non-authoritative for Payment gates.
9. Never create or rely on `canPayout`, `taxApproved`, `isKycVerified`, `walletBalance`, or equivalent source booleans.
10. Processor-held funds are not Workin Ants wallet, escrow, stored value, or cash custody.
11. `ProfessionalBalanceLedgerEntry` is append-only; correcting economic history requires compensating entries, not mutation/deletion of prior effects.
12. Derived available/held/requested/paid totals must be reconstructible from Payment-owned ledger/evidence and approved source snapshots.
13. One authoritative source effect must not create duplicate ledger entries under retry/replay.
14. Historical seller commission/fee effects use the immutable Order snapshot; never recalculate an old Order from current Track entitlement.
15. `PayoutRequest` is withdrawal intent; `PayoutTransfer` is execution. Approval is not payment.
16. Payment authorization/capture is not payout authorization.
17. Payout creation/execution must use current Payment readiness, applicable ComplianceHold decision, authority, and required step-up.
18. Concurrent payout requests must not overspend the same available funds.
19. No in-memory lock may protect a financial invariant owned by the database.
20. A transfer retry must not create duplicate processor money movement; ambiguous provider outcomes reconcile before unsafe retry.
21. Payment never owns Dispute case lifecycle. It only records approved money consequences.
22. Payment never owns Prize/Reward source lifecycle. It only consumes recognized reportable value and owns tax reporting.
23. Payment never owns Offering/Product/Course/DigitalGoodsPolicy lifecycle merely because tax needs item context.
24. Marketplace/Digital Goods do not own `SalesTaxLineItem`; they supply source context through owner contracts.
25. Sales tax must use approved provider-backed calculation/evidence; do not implement a homemade jurisdiction/rate engine.
26. SH-120 jurisdiction normalization is unresolved and must not be silently implemented as canonical platform infrastructure here.
27. Buyer tax-location evidence is private tax input; it is not public location/search data.
28. Finalized sales-tax proof must bind to the correct Order/pricing/version; stale context is a conflict.
29. Unsupported partial/multiple tax refund allocation must fail explicitly rather than inventing arithmetic/evidence.
30. Refund adjudication/RefundStatus remains Order/Dispute-owned; Payment executes the provider rail only through approved contract.
31. KYC/tax/bank/payment credentials and secrets must not be stored in ordinary application fields or logs.
32. Sensitive financial reads/mutations require server authorization and step-up/access proof where specified.
33. UI visibility is not authorization or step-up proof.
34. Generic AuditEvent/AccessAuditLog remain Audit-owned and never replace Payment source truth.
35. IntegrationFailure/SystemEvent/QueueJob remain Ops-owned and never replace Payment state.
36. Notification delivery remains Notification-owned; no direct SES/SMS/push provider in this Module.
37. Media upload/scanning/signed URLs remain Media-owned; no local financial file pipeline.
38. Search remains a projection and Payment financial data is not public Search truth.
39. Privacy / Data Erasure owns request/orchestration/exemptions; Payment only enumerates/executes/exports its own targets/providers.
40. Exact financial/tax retention periods are unresolved; destructive paths must remain blocked or retention-safe until approved.
41. Cross-Module reads use public owner interfaces/approved narrow DTOs; a generic foreign-table repository is prohibited.
42. Confirmed Shared Operations are reused by SH ID rather than reimplemented under Payment-specific aliases.
43. Provider adapters never become domain truth and never expose raw SDK types through public Module contracts.
44. Unknown provider values fail safe to unsupported/review, never silently map to success.
45. Event payloads are minimized and factual; they are not disguised cross-Module commands.
46. Every replay-prone command/provider/source event must have a durable idempotency/dedupe boundary.
47. Tax reporting thresholds/forms/regimes must be versioned policy inputs; never hardcode one universal threshold/form based on assumption.
48. A coding agent must not invent payment-attempt, chargeback, tax-correction, payout-account-selection, KYC cardinality, or partial-refund semantics that the current evidence has not settled.

---

## 34. Prohibited Duplicate Implementations

Do not add independent files/services with these responsibilities inside this Module:

| Prohibited implementation / likely name | Canonical owner / replacement |
| --- | --- |
| `payoutAuth.ts`, `paymentPermissions.ts`, `financialIsAdmin.ts`, `canViewPayout.ts` | SH-001 + SH-002 with Payment owner facts |
| `payoutMfa.ts`, `taxMfa.ts`, `financialOtp.ts`, `verifySensitiveSession.ts` | SH-014 Identity step-up |
| `payoutBlockedService.ts`, `isHeld.ts`, `financialHold.ts`, local blocked flag | SH-011/012/013 ComplianceHold; local consequence only |
| `canPayout.ts`, `stripeReadyService.ts`, `taxApproved.ts` | SH-019 dimensioned readiness + canonical records |
| `stripeWebhookVerifier.ts`, `verifyStripeWebhook.ts` clone | SH-059 shared integration security + adapter config |
| `WebhookLog` / `stripeLog` as dedupe | SH-060 + `ProcessedStripeEvent` |
| global `ProviderStatus` / `providerStateUtils.ts` | SH-061 + Payment-owned enums/mappings |
| `stripeSync.ts` that directly repairs Order/other Modules | SH-062 Payment reconciliation + owner commands |
| `paymentRetryQueue.ts`, `stripeRetry.ts`, `paymentDeadLetter.ts` | SH-047/048 shared queue/retry/dead-letter |
| `balanceMutex.ts`, in-memory payout lock | SH-051/056 + DB constraints/transactions |
| mutable `Wallet`, `Escrow`, `ProfessionalBalance` source row | append-only `ProfessionalBalanceLedgerEntry` + derived query |
| generic `ledgerService.ts` used for points/audit/order events | Payment-local financial ledger policy over shared append mechanics; other ledgers remain separate truth |
| `FinancialAuditLog`, `PayoutAccessLog`, `TaxViewLog` as generic audit systems | SH-029/030 Audit/Event Ledger |
| `PaymentIntegrationFailure`, `StripeIncident` as business state | Observability SH-037/038 |
| `sendPayoutEmail.ts`, `sendTaxSms.ts`, SES/Twilio/FCM clients | SH-041 Notification |
| `taxFileStorage.ts`, `kycPresign.ts`, local R2/S3/scanner | Media / File Access + SH-087 if needed |
| `paymentPrivacyRequest.ts`, `eraseFinancialUser.ts` orchestration | SH-095/096/097 + Privacy owner; Payment executor only |
| `paymentRetentionExemption` table/flag | Privacy-owned DataRetentionExemption; SH-097 supplies facts |
| `customTaxCalculator.ts`, local state/rate tables guessed from jurisdiction | approved SalesTaxProvider adapter/rules; unresolved SH-120 not locally claimed |
| `OrderPaymentStatus` / Payment-owned refund case lifecycle replacing Order | Order public commands + SH-108 |
| `currentCommissionService.ts` for settled Order | Order historical snapshot / SH-109 pattern |
| Prize/Reward tax lifecycle copy | SH-118 intake; source Module remains owner |
| `SearchPaymentIndex.ts`, Typesense client, `SearchUpsertEvent` writer | no public Payment index; source owner/Search boundaries |
| one generic `CL03ProviderAdapter` | Payment-local capability-specific ports; shared provider shell outside Module |

---

## 35. Unresolved Decisions

These are binding blockers/constraints. Coding agents must not choose answers silently.

| ID | Question | Evidence/conflict | Blocks / permitted interim behavior |
| --- | --- | --- | --- |
| **UD-01 / CL-03 U-01** | Must full KYC/tax/payout-account readiness precede ProfessionalProfile activation, Offering publication, Gig response, or only money receipt/payout? | Cluster evidence says relevant financial readiness but does not set timing. | Blocks final external action-to-gate matrix. Payment may implement SH-019 and payout gates; action owners decide timing only after approval. |
| **UD-02 / CL-03 U-17** | What is the final fate of `ProfessionalProfile.stripeAccountId`, `stripeReady`, verification timestamps/trust score? | They overlap Payment/Trust source records. | Schema cleanup only. Treat as non-authoritative compatibility/projection fields now. |
| **UD-03 / CL-03 U-18** | Exact legal retention periods for KYC/tax/payout/payment/tax-reporting evidence? | Compliance inventory identifies duties but not complete durations. | Destructive privacy deletion/retention scheduler. Preserve under Privacy exemptions until policy. |
| **UD-04** | What are `ProcessedStripeEvent` claim/processing/recovery semantics? | Current record has only eventId/type/receivedAt; no processed/failed/result state. | Before robust async webhook production, approve transaction/claim strategy. Safe interim: claim and local effect atomically where possible; cross-owner effects idempotent + reconcile. |
| **UD-05** | Is `ProcessedStripeEvent` Payment-domain Stripe dedupe only or a platform-wide Stripe ingress claim shared with Track Billing? | Canonical shared rules require provider-/Module-specific truth; multiple Stripe-using domains may exist. | Do not let Payment steal Track subscription event truth. Route/claim architecture must be explicit before shared Stripe ingress consolidation. |
| **UD-06** | What is KYC/TaxProfile cardinality and “current applicable record” selection? | Prisma permits multiple subject records; no active/current unique rule. | Onboarding/reverification concurrency and readiness query. Feature must approve selection/new-attempt policy before production. |
| **UD-07** | Can a ProfessionalProfile have multiple payout accounts, and how is primary/default selection determined? | Prisma allows many; no primary field. | Payout account selection. Interim may require explicit account ID and reject ambiguity; do not guess first/latest. |
| **UD-08** | How should multiple simultaneous ComplianceHolds be represented on one PayoutRequest/Transfer when schema has one `blockedByHoldId`? | Hold query can return multiple applicable holds. | Do not treat one FK as complete hold truth. Decide whether it is primary explanatory ref plus external hold query or add association/evidence. |
| **UD-09** | What durable unique source-effect key guarantees ledger idempotency? | Ledger schema has no source event/effect unique constraint. | Production source-event ledger projection. PT-02 must be resolved in schema/inbox retention contract. |
| **UD-10** | Are PayoutRequest reservations represented only by ledger effects, and what exact release/correction entries apply to failed/cancelled/reversed requests? | Enum has relevant entry types but complete sign/availability rules are not documented. | Final payout ledger policy; feature specification must freeze entries/signs. |
| **UD-11** | Is a PayoutTransfer one transfer per request, per Order, or may both be authoritative sources? | Both `payoutRequestId` and `orderId` optional. | Transfer creation invariant and reconciliation. No arbitrary mixed source strategy. |
| **UD-12** | After provider failure, is retry the same PayoutTransfer, a new PayoutTransfer, or a child attempt record? | No attempt model; transfer has mutable provider refs/status. | Retry/history semantics. Must preserve no-duplicate-money invariant; do not invent child model without ruling. |
| **UD-13** | Does Payment need first-class payment attempt/charge/refund/chargeback records beyond Order refs + ProcessedStripeEvent + sales-tax records? | Module owns processor rail/proof, but current registry/schema has no generic payment-attempt/charge/refund-attempt/chargeback aggregate. | Multi-attempt payment history, chargeback/provider-dispute proof, detailed refund rail history. MVP must constrain to current supported evidence or approve new models. |
| **UD-14 — partially resolved by CL-03-R014** | Minimum grain is tax subject + jurisdiction + tax year + currency, with source-event uniqueness/reversals. Exact tax-subject representation and persistence design remain open. | Current unique `(userId,taxYear,currency)` is insufficient and cannot discard jurisdiction. | Production aggregation requires approved subject representation and persistence/migration coverage for the minimum grain; no schema change in this pass. |
| **UD-15** | What versioned tax reporting rule source owns thresholds/forms/regimes and effective dates? | Compliance says do not hardcode thresholds/one form; no complete rule schema is established. | Automated “reporting required”, filing preparation/submission. Manual/legal-reviewed configuration only until approved. |
| **UD-16** | How is one authoritative/final SalesTaxCalculation selected for an Order/version? | Multiple calculations allowed; no unique final current constraint/version snapshot field. | Concurrent/recalculated checkout finalization. Must bind explicitly to Order version and approved calc ID. |
| **UD-17 — evidence requirement resolved by CL-03-R015** | Payment must preserve line-level liability evidence when lines can differ. Exact persistence design remains open. | Prisma line item lacks liabilityRole; calculation/transaction liability cannot prove mixed-liability lines. | Mixed-liability production requires an approved field or immutable line-linked structure and forward migration; no schema change in this pass. |
| **UD-18** | How are partial/multiple refunds and tax reversals represented? | SalesTaxTransaction has aggregate amount + one reversal ref; Cluster plan says unsupported cases must fail rather than invent allocation. | Partial/multi-refund production flows. Constrain to supported full/single cases until schema/provider semantics approved. |
| **UD-19** | What buyer tax-location provenance must be stored? | Calculation stores location fields but not explicit evidence-source/version relationship. | Audit-reproducible jurisdiction proof. Feature may store minimized metadata only if approved; do not invent public/geolocation ownership. |
| **UD-20** | How are tax-reporting corrections/replacement submissions chained/versioned? | Submission/recipient statuses include corrected/rejected but no explicit prior/subsequent submission relation. | Automated corrections/re-filings. Keep unsupported correction automation disabled. |
| **UD-21** | What provider is approved for future non-Stripe KYC/tax/reporting paths? | Registry lists possible/future providers but no canonical selection. | Adapter activation only; provider-neutral domain ports may proceed. |
| **UD-22** | How does paid screening fit OrderSourceType if Trust creates a chargeable Order? | OrderSourceType currently centers Offering/GigAssignment while SH-107 includes paid platform workflows. | Trust screening fee flow, not core Payment payout. Payment must not alter Order model; escalate to Order architecture. |
| **UD-23** | Are Payment domain event names/aggregate versions persisted in a dedicated owner event ledger or only canonical outbox? | No Payment-specific event model is listed. | Event history/query semantics. Outbox can publish facts; do not invent lifecycle ledger unless consumer/audit requirement approves one. |

---

## 36. Architecture Decision Summary

### Confirmed binding rulings

1. Payment / Payout / Tax is a CL-03 capability/compliance Module with a strong CL-04 financial bridge.
2. It owns payout KYC, tax profile/documents/reporting, payout accounts/requests/transfers, professional financial ledger projection, Payment Stripe-event dedupe, provider requirement snapshots, and sales-tax proof.
3. Order remains transaction truth; Payment executes processor/tax/refund rails and reports verified normalized results through Order public interfaces.
4. Processor-held money is not a Workin Ants wallet or escrow.
5. Financial KYC is separate from Trust verification.
6. Tax-profile/reporting readiness is separate from transaction sales tax.
7. SH-019 `evaluateFinancialReadiness` is Payment's canonical public readiness decision and returns separate dimensions rather than one boolean.
8. `ComplianceHold` remains the reusable stop sign; Payment does not create generic blocked flags.
9. Sensitive financial actions use Identity step-up plus Role authorization and Audit sensitive-access proof where required.
10. Provider events are verified, Payment-deduplicated, translated, transition-validated, and reconciled; raw provider state is never domain truth.
11. Financial ledger effects are append-only and must be source-event idempotent; correction uses compensating effects.
12. Payout request and payout transfer are separate lifecycles.
13. Sales tax is provider-backed; Payment owns SalesTaxCalculation/LineItem/Transaction while source item/Order truth remains external.
14. Prize/Reward/other sources report recognized taxable value through SH-118; Payment owns tax aggregation/reporting, not source lifecycle.
15. Generic auth, holds, audit, access logs, queue/retry, notifications, media, privacy orchestration, Search, and observability remain with canonical owners.
16. Direct cross-Module Prisma access is not the default integration mechanism.
17. Unsupported or unresolved legal/provider/partial-refund paths must fail closed or remain disabled.

### Proposed Rulings requiring approval before dependent commitment

- **PT-01:** `TaxReportingSubmissionStatus` and `TaxReportingRecipientStatus` belong to Payment unless root enum governance says otherwise.
- **PT-02:** establish a durable database-backed source-effect identity for `ProfessionalBalanceLedgerEntry` before production event projection.
- Module-local folder structure and initial provider-port split in Section 6/20.
- Owner-specific Payment event names in Section 21.
- Proposed minimum lifecycle transition graphs in Section 9; implementing features must approve exact edges before enabling them.
- Proposed `evaluateTaxFulfillmentReadiness` public query if CL-10 needs a tax-specific decision beyond SH-019.

### Non-rulings preserved as unresolved

Section 35 preserves the remaining UD-01 through UD-23 decisions. CL-03-R014 fixes the minimum aggregation semantics in UD-14; CL-03-R015 fixes the line-level evidence requirement in UD-17. Their exact persistence designs remain open. All other unresolved decisions remain unchanged; this architecture does not fill them with guessed implementation.

---

## 37. Coding-Agent Usage

Before implementing any numbered feature in this Module, the coding agent must read, in order appropriate to repository conventions:

1. `context/project-overview-v3.md`;
2. root Workin Ants architecture;
3. root code/security/data standards;
4. Canonical Shared Operations Registry / `context/shared/shared-operations.md`;
5. CL-03 `context/clusters/professional supply & readiness/professional-supply-readiness-architecture.md`;
6. CL-03 `context/clusters/professional supply & readiness/professional-supply-readiness-build-plan.md`;
7. this `context/clusters/professional supply & readiness/Payment Payout & Tax Module/payment-payout-tax-module-architecture.md`;
8. this Module's `context/clusters/professional supply & readiness/Payment Payout & Tax Module/payment-payout-tax-module-implementation-plan.md`;
9. current Prisma schema/migrations for every Payment-owned record touched;
10. public-interface sections for direct dependencies, especially Identity/Role, Professional Eligibility, Transaction / Order, Compliance Hold, Review / Dispute, Track Entitlement, Prize/Rewards, Privacy, Audit, Notification, Observability, Media when used;
11. the progress tracker (**missing**; see `context/context-map.md`) and any available prior feature completion report, without treating the latter as an equivalent tracker;
12. the Unresolved Decisions table in this document and the Cluster architecture.

Before coding, the agent must identify which assertions are Confirmed, Proposed Rulings already approved, or still Unresolved. If the feature depends on an unresolved item, the agent must either:

- obtain/record an approved architecture ruling;
- constrain the feature to the supported path;
- or leave that path disabled and report the blocker.

The implementation must never silently create new financial truth, provider-event truth, tax policy, retention rules, foreign lifecycle writes, or shared infrastructure merely to make a feature appear complete.
