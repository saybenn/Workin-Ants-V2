# Moderation, Holds, Audit & Ops Architecture

## 1. Document Status and Scope

| Item | Value |
| --- | --- |
| Cluster ID | `CL-09` |
| Cluster name | Moderation, Holds, Audit & Ops |
| Cluster type | `governance_compliance_stop_sign_audit_observability` |
| Document status | Implementation-grade Cluster architecture synthesized from current Workin Ants evidence |
| Intended audience | Coding agents, developers, reviewers, maintainers, compliance reviewers, and architecture owners |
| Primary role | Coordinate the four CL-09 Deep Modules and their public contracts without taking ownership of their lifecycles |

This document is subordinate to the root Workin Ants architecture and source-of-truth rules. It explains how CL-09 Modules collaborate; it does **not** create a new Cluster-owned business domain and does **not** transfer lifecycle ownership away from a Deep Module.

The Deep Module architectures remain authoritative for Module-local meaning. The Prisma schema remains the executable schema evidence for models, enums, indexes, and relations. The Canonical Shared Operations Architecture is binding anti-duplication guidance for shared mechanisms and public capabilities.

### Evidence status used in this document

| Label | Meaning |
| --- | --- |
| **Confirmed** | Directly supported by current Workin Ants registries, Prisma, Ubiquitous Language / Compliance evidence, Module extracts, or confirmed Canonical Shared Operations. |
| **Proposed Ruling** | A concrete architecture decision needed to make implementation coherent, but not yet established as source authority. It must be explicitly accepted before implementation treats it as binding. |
| **Unresolved** | Current evidence conflicts or does not define enough detail to choose safely. Coding agents must not invent the answer. |

### Update rule

Update this file when a binding architecture decision changes any of the following: lifecycle ownership, schema meaning, public Module contracts, shared-operation ownership, provider boundaries, retention behavior, cross-Cluster bridge semantics, or a previously unresolved CL-09 decision. Build progress must not silently redefine this architecture.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

CL-09 is the platform control tower for four distinct kinds of governance truth:

1. moderation and legal-review truth;
2. reusable platform stop-sign truth;
3. generic audit and sensitive-access proof;
4. operational failure and incident visibility.

### Goal

Stop actions that must stop, preserve evidence that must survive review, route human or legal review to the correct owner, record actor/action/access proof, and make technical degradation visible without turning CL-09 into the owner of every business object it observes or affects.

### Transformation

```text
Reports / legal notices / risk signals / hold requests
Sensitive access outcomes / important actions
Provider or worker failures / queue transitions / request context
        |
        v
CL-09 owner-specific validation and policy
        |
        +--> Content Moderation & Legal Notice
        |      -> Report / LegalNotice / ModerationCase / ModerationAction
        |      -> owner-targeted enforcement requests and restoration requests
        |
        +--> Admin Review / Compliance Hold
        |      -> ComplianceHold stop sign
        |      -> allow/block decision for consuming workflow
        |
        +--> Audit / Event Ledger
        |      -> AuditEvent / AccessAuditLog evidence
        |
        +--> Observability / Ops
               -> operational events, normalized failures, queue visibility,
                  health state, incident grouping, diagnostics

Outputs then flow through owner interfaces to Search, Media, Payment,
Messaging, Notification, Digital Goods, Video, Marketplace, Hiring,
Privacy, and other Modules without CL-09 directly taking their state.
```

### CL-09 explicitly does not own

- authentication or session identity;
- permission interpretation;
- business lifecycles such as `Order`, `Booking`, `Job`, `Offering`, `Gig`, `Message`, `PayoutTransfer`, `DigitalDownloadGrant`, or `CourseVideoPlaybackGrant`;
- provider-event deduplication owned by provider-integrating Modules;
- Typesense/search projection execution;
- Cloudflare R2/file mechanics;
- payment, payout, KYC, tax, healthcare, verification, or job-compliance source facts;
- notification delivery;
- privacy-request orchestration or retention-exemption truth;
- track subscription or entitlement policy;
- legal advice or automated legal decisioning.

---

## 3. Module Inventory

| Module ID | Module name | Type | Purpose | Owned truth | Primary responsibility in CL-09 | Major inbound dependencies | Major outbound consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `content_moderation_legal_notice` | Content Moderation & Legal Notice Module | `compliance_ops` | Convert reports and formal notices into traceable review and moderation/legal actions. | `Report`, `LegalNotice`, `ModerationCase`, `ModerationAction` and their owned vocabularies. | Intake, legal/moderation case lifecycle, adjudication, content freeze/hide/restore decisions, legal/admin workflow, downstream enforcement orchestration. | Identity, Role / Authority, target owners, Media, Search, Hold, Audit, Notification, Privacy. | Search, Media, Messaging, Marketplace Supply, Gig Demand, Organization Hiring, Hold, Digital Goods, Video, affected target owners. |
| `admin_review_compliance_hold` | Admin Review / Compliance Hold Module | `ops_compliance` | Provide the reusable platform stop sign and its release proof. | `ComplianceHold`, `ComplianceHoldReason`, `ComplianceHoldStatus`. | Create/evaluate/release holds, expose active blocking decisions, route manual review and escalation without owning the underlying compliance fact. | Identity, Role / Authority, Payment, Verification, Job Compliance, Moderation, Dispute, Healthcare, Prize, Rewards, Audit, Notification, Privacy. | Payment/Payout, Professional Eligibility, Job Compliance, Moderation, Review/Dispute, Healthcare, Sweepstakes, Rewards, candidate/resume workflows. |
| `audit_event_ledger` | Audit / Event Ledger Module | `capability_ops_compliance_support` | Preserve generic actor/action proof and sensitive-access proof. | `AuditEvent`, `AccessAuditLog`, `AccessAuditAction`; claimed but absent `AuditEventType` and `AuditEventActor`. | Append-only audit evidence, access evidence, restricted audit queries, audit-viewer support, integrity support. | Identity, Role / Authority, request context, domain access decisions, Privacy. | All compliance-sensitive Modules, admin/compliance tooling, transaction, booking, hiring, payment, media, holds, moderation. |
| `observability_ops` | Observability / Ops Module | `ops_capability` | Make technical failures, queues, provider degradation, lag, health, and incidents visible. | Registry/glossary claim `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident`; all four are absent from current Prisma. | Request correlation, structured logs, error capture, metrics, normalized integration failure visibility, queue telemetry, health, incident grouping, ops dashboards. | All Modules and shared runtime; owner-emitted operational signals; Sentry/logging/metrics/queue infrastructure; Audit, Notification, Privacy. | All Modules, admin/support tooling, incident responders, integration owners, Privacy. |

---

## 4. Cluster Architecture Principles

1. **The Cluster coordinates; Modules own truth.** CL-09 has no independent lifecycle table or universal governance aggregate.
2. **Moderation owns the decision; target owners execute their own state changes.** A `ModerationAction` can authorize or request an effect; it does not directly mutate Search, Media, Messaging, Digital Goods, Video, Payment, Order, Offering, Gig, Job, or profile state.
3. **A hold is a stop sign, not the underlying compliance fact.** `ComplianceHold` can block an action because of KYC, tax, dispute, moderation, security, verification, or other source facts, but those source facts remain with their owners.
4. **Hold release is not compliance approval.** The source Module decides whether its condition permits release; Admin Review / Compliance Hold alone changes hold lifecycle status.
5. **Audit evidence is not domain-event truth.** `AuditEvent` and `AccessAuditLog` do not replace `OrderEvent`, `BookingEvent`, `JobInterviewEvent`, `UserSecurityEvent`, `AgreementEvent`, provider processed-event records, access-grant ledgers, or financial ledgers.
6. **Observability is not workflow state.** `SystemEvent`, `IntegrationFailure`, `QueueJob`, logs, metrics, and incidents diagnose execution; they do not replace business statuses.
7. **Provider state is never CL-09 business truth unless CL-09 itself owns that provider boundary.** Provider-owning Modules verify, deduplicate, translate, reconcile, and apply their provider events.
8. **Search remains projection.** Moderation requests de-index/re-index work through Search. CL-09 never writes Typesense or `SearchUpsertEvent` directly.
9. **Media owns file mechanics.** Moderation may require freezing, preserving, or revoking public access; Media / File Access performs file/object operations and signed access.
10. **Sensitive access policy remains with the data/context owner.** Audit records the allow/deny/redact/block outcome; it does not make healthcare, finance, resume, agreement, message, or location decisions.
11. **Privacy orchestrates privacy rights.** Every CL-09 data owner must enumerate and execute privacy instructions against its own records, but must not create a local `PrivacyRequest` workflow.
12. **Shared mechanism does not merge truth.** Idempotency, outbox, queue runners, locks, hashing, append-only persistence, target-validation contracts, and review claims may be reusable, but CL-09 Module records stay distinct.
13. **No unrestricted cross-Module repository.** Typed owner interfaces or owner-emitted events are required for cross-domain reads and writes.
14. **Evidence and telemetry are minimized.** Secrets, OTPs, raw biometric data, raw identity documents, card data, PHI payloads, full resumes, private message bodies, and complete contract documents must not be copied into generic audit or operational metadata.
15. **Legal-gated behavior is not guessed.** DMCA/DSA timing, evidence retention duration, repeat-infringer policy, legal correspondence requirements, and equivalent legal decisions remain explicitly versioned policy or unresolved until approved.

---

## 5. Runtime / Collaboration Topology

### 5.1 Synchronous command path

```text
Request / internal command
  -> resolveAuthenticatedActor                 [Identity & Access]
  -> createRequestContext                      [Observability/platform]
  -> authorizeResourceAction                   [Role / Authority]
  -> owning CL-09 Module command
       -> validate owner-local input/invariants
       -> validateOwnedTargetReference or owner-specific target query
       -> evaluate required external gates
       -> executeIdempotentCommand
       -> authoritative owner transaction
       -> publishDomainEvent / enqueueReliableJob when needed
       -> appendAuditEvent for important action proof
       -> recordSensitiveAccess when protected evidence/data was accessed
       -> requestNotification for user/admin delivery when required
  -> safe result
```

### 5.2 Moderation enforcement topology

```text
Report / LegalNotice
  -> Content Moderation & Legal Notice
  -> ModerationCase
  -> evidence preservation requirement
  -> ModerationAction (decision/action truth)
  -> executeModerationDecision protocol
       -> Media owner handler
       -> Search owner handler
       -> Messaging owner handler
       -> Marketplace/Gig/Hiring owner handler
       -> Digital Goods owner handler
       -> Video owner handler
       -> Compliance Hold request when a stop sign is needed
  <- acknowledgments / completed / failed / restored results
  -> Moderation-owned orchestration correlation
  -> Audit proof
  -> Observability failure if technical execution fails
  -> Notification request
```

The target handler writes its own source state. Moderation stores only its decision and, if the proposed enforcement-correlation ruling is accepted, durable correlation of downstream acknowledgments.

### 5.3 Hold topology

```text
Source Module determines a review/block condition
  -> requestComplianceHold
  -> Hold Module validates request + target + authority + idempotency
  -> ComplianceHold(active)
  -> consuming workflow calls evaluateComplianceHold
  -> source condition later resolves
  -> source Module requests release
  -> Hold Module authorizes + transitions to released
  -> appendAuditEvent
  -> requestNotification if required
```

### 5.4 Operational topology

```text
Every request / job / provider adapter
  -> createRequestContext
  -> writeStructuredLog / emitMetric
  -> on technical failure: recordIntegrationFailure
  -> shared queue runner: recordQueueTelemetry
  -> severe/correlated failures: correlateOpsIncident
  -> requestNotification for operational alerts
```

`QueueJob`, if implemented, is operational visibility only. The owning workflow record remains business truth.

### 5.5 Database access rule

A CL-09 Module may directly use its own repositories. Cross-Module reads use a public query, projection contract, or emitted event. Cross-Module writes use a public command, event handler, or documented protocol. Direct Prisma writes into another Module's tables are prohibited.

---

## 6. Folder / Code Organization

The exact repository prefix must follow root `code-standards.md`. The following is the required **relative ownership shape**, not permission to introduce BTLS or arbitrary project folder conventions.

```text
<module-root>/content-moderation-legal-notice/
  domain/
    report/
    legal-notice/
    moderation-case/
    moderation-action/
    policies/
  application/
    commands/
    queries/
    orchestration/
  public/
    commands.ts
    queries.ts
    contracts.ts
    events.ts
  infrastructure/
    repositories/
    target-resolvers/
  workers/
  ui/admin/
  tests/

<module-root>/admin-review-compliance-hold/
  domain/
    compliance-hold/
    review-policy/
  application/
    commands/
    queries/
  public/
  infrastructure/repositories/
  workers/
  ui/admin/
  tests/

<module-root>/audit-event-ledger/
  domain/
    payload-policy/
    integrity-policy/
  application/
    commands/
    queries/
  public/
  infrastructure/
    repositories/
    append-only-storage/
  workers/
  ui/admin/
  tests/

<module-root>/observability-ops/
  domain/
    failure/
    incident/
    telemetry-policy/
  application/
    ingestion/
    queries/
  public/
  infrastructure/
    logging/
    metrics/
    sentry/
    repositories/
  workers/
  ui/admin/
  tests/

<shared-platform-root>/
  idempotency/
  outbox/
  queue-runner/
  locking/
  request-context/
  crypto/
  shared-contracts/
```

### Organization rules

- Moderation orchestration belongs to Content Moderation & Legal Notice, because that Module owns the review/decision meaning.
- Hold lifecycle code belongs to Admin Review / Compliance Hold.
- Audit append and query code belongs to Audit / Event Ledger.
- Generic logger, Sentry adapter, metrics client, request correlation, and operational-failure recording belong to Observability / approved platform infrastructure.
- Provider adapters for Typesense, R2, payment, calendar, video, notification, verification, or subscriptions do **not** move into CL-09 merely because CL-09 observes or requests effects from them.
- A Cluster-level `shared/`, `utils/`, `services/`, or `repository/` folder is prohibited unless the code maps to an approved shared operation or platform primitive.
- A target-resolver registry may define typed contracts and routing, but each target owner supplies its resolver implementation; it must not become a universal cross-domain Prisma repository.

---

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
| --- | --- | --- | --- |
| Content Moderation & Legal Notice | Reports, legal notices, cases, moderation decisions/actions, legal/moderation workflow policy, enforcement orchestration meaning. | Actor/authority; target summaries; Media preservation/execution; Search refresh; Hold requests; Audit; Notification; Privacy retention decisions. | Target business lifecycles, file/storage mechanics, Typesense, payout execution, generic audit, provider event truth, notification delivery. |
| Admin Review / Compliance Hold | Hold reason/status vocabulary, active hold truth, hold lifecycle, release proof, hold-specific review policy. | Underlying source facts via owner interfaces; authority; Audit; Notification; Privacy; shared review/locking mechanics. | KYC/tax/background/healthcare/moderation/dispute/job-compliance truth; payout execution; local replacement block booleans in consumers. |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog`, access audit action vocabulary, audit payload policy, restricted evidence queries. | Actor identity, authority for viewers, data-owner sensitivity/decision, request context, Privacy retention instruction. | Business lifecycle decisions, domain event ledgers, provider dedupe, operational incident state, authorization decisions. |
| Observability / Ops | Request/correlation context, structured operational telemetry, normalized technical failures, queue visibility, service health, incident grouping. | Owner-emitted operational signals; Audit context; Notification; Privacy; provider tools. | Business status, legal/audit proof, provider-domain meaning, payment/search/calendar/video/media execution, provider-event dedupe. |
| Identity & Access | Authentication, actor/session/step-up truth. | — | Moderation, hold, audit, or incident policy. |
| Role / Authority | Permission interpretation. | Owner-supplied relationship facts. | Hold/readiness/legal decisions or authentication. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense projection, indexing/de-indexing execution and reconciliation. | Moderation/public-readiness decisions and source projections. | Moderation or source lifecycle truth. |
| Media / File Access | `MediaAsset`, file validation/scanning/processing, storage, generic access grants, signed URLs, provider object mechanics. | Moderation preservation/freeze requests, contextual entitlement. | Legal/moderation decision or contextual business entitlement. |
| Notification | Notification routing, persistence, template/channel rendering, delivery and provider state. | Safe CL-09 triggering context. | Moderation, hold, audit, or incident source meaning. |
| Privacy / Data Erasure | `PrivacyRequest`, erasure jobs/targets, retention exemptions, export bundle, orchestration. | CL-09 owner enumeration/execution/retention facts. | Direct mutation of all CL-09 tables without owner executors. |
| Payment / Verification / Healthcare / Job Compliance / Dispute | Their own compliance and business facts. | Hold gate and audit/ops rails. | `ComplianceHold` lifecycle or generic audit/ops truth. |

---

## 8. Data Ownership

### 8.1 Current Prisma-backed CL-09 truth

| Record / enum | Owner | Meaning | Current schema status | Important boundary |
| --- | --- | --- | --- | --- |
| `Report` | Content Moderation & Legal Notice | Report intake truth. | Present. | Not a formal legal notice automatically. |
| `ReportReason` | Content Moderation & Legal Notice | Controlled report reasons. | Present. | Must not be copied into target Modules. |
| `ReportSource` | Content Moderation & Legal Notice | Reporter/source classification. | Present. | Source is not actor authority. |
| `ReportStatus` | Content Moderation & Legal Notice | Report lifecycle vocabulary. | Present. | Transition graph is not fully specified by schema. |
| `LegalNotice` | Content Moderation & Legal Notice | Formal legal-notice workflow truth. | Present. | Downstream disable/hide states do not replace it. |
| `LegalNoticeType` | Content Moderation & Legal Notice | DMCA/DSA/law-enforcement/copyright/other notice types. | Present. | Legal policy requirements are separate/versioned. |
| `LegalNoticeStatus` | Content Moderation & Legal Notice | Notice lifecycle vocabulary. | Present. | Exact legal transition graph and deadlines remain policy-gated. |
| `ModerationCase` | Content Moderation & Legal Notice | Review-container truth. | Present. | Not a `Dispute`, `ComplianceHold`, or `OpsIncident`. |
| `ModerationCaseStatus` | Content Moderation & Legal Notice | Case lifecycle vocabulary. | Present. | Exact transition graph requires owner policy. |
| `ModerationAction` | Content Moderation & Legal Notice | Recorded moderation/legal decision/action. | Present; append-style row. | Does not prove downstream execution succeeded. |
| `ModerationActionType` | Content Moderation & Legal Notice | Controlled moderation action vocabulary. | Present. | Several action effects are executed by other Modules. |
| `ModerationTargetType` | Content Moderation & Legal Notice | Polymorphic target vocabulary. | Present, but schema contains a suspicious `@@map("payout_transfers")` mapping. | Mapping defect must be resolved before a migration relies on it. |
| `ComplianceHold` | Admin Review / Compliance Hold | Platform stop-sign truth. | Present. | Current direct target FKs cover only User, ProfessionalProfile, and Order; claimed scope is broader. |
| `ComplianceHoldReason` | Admin Review / Compliance Hold | Hold reason vocabulary. | Present. | Reason references source conditions but does not replace them. |
| `ComplianceHoldStatus` | Admin Review / Compliance Hold | `active`, `released`, `expired`. | Present. | `expired` has no current expiry timestamp/policy in the model. |
| `AuditEvent` | Audit / Event Ledger | Generic important-action proof. | Present. | `action` and `entityType` are strings; no request ID field. |
| `AccessAuditLog` | Audit / Event Ledger | Sensitive-access proof. | Present. | Has optional `previousHash`/`entryHash`; app-level immutability is not enough. |
| `AccessAuditAction` | Audit / Event Ledger | Controlled sensitive-access action vocabulary. | Present. | Access meaning remains with data owner. |

### 8.1.1 Confirmed owned enum values

The following values are part of the current executable Prisma evidence and must not be renamed, merged, or expanded casually during implementation.

**`ReportReason`**

```text
copyright
illegal_content
counterfeit
fraud
spam
harassment
health_safety
child_safety
terrorism
privacy_violation
other
```

**`ReportSource`**

```text
user
rights_holder
trusted_flagger
admin
system
law_enforcement
```

**`ReportStatus`**

```text
submitted
triaged
under_review
action_taken
dismissed
closed
```

**`LegalNoticeType`**

```text
dmca_takedown
dmca_counter_notice
dsa_notice
law_enforcement
copyright_owner_notice
other
```

**`LegalNoticeStatus`**

```text
received
validating
valid
invalid
action_taken
counter_notice_received
restored
rejected
closed
```

**`ModerationCaseStatus`**

```text
opened
triaged
under_review
waiting_for_counter_notice
escalated
action_taken
dismissed
closed
```

**`ModerationActionType`**

```text
hide
unhide
freeze_content
archive_content
remove_public_url
restore
suspend_profile
pause_payout
freeze_order
apply_takedown
reject_takedown
accept_counter_notice
escalate_to_legal
disable_digital_access
restore_digital_access
revoke_download_grants
disable_course_playback
```

**`ModerationTargetType`**

```text
user
professional_profile
candidate_profile
organization
offering
course_details
product_details
media_asset
message
thread
gig
job
review
digital_download_asset
course_video_asset
course_accessibility_asset
media_upload_session
```

The enum's current Prisma `@@map("payout_transfers")` mapping is not treated as intentional domain meaning; it is tracked as `U-01` and must be resolved against migration/database evidence before implementation relies on it.

**`ComplianceHoldStatus`**

```text
active
released
expired
```

**`ComplianceHoldReason`**

```text
kyc_required
tax_required
payout_account_required
background_check_required
background_check_failed
license_verification_required
license_expired
dmv_check_required
adverse_action_pending
verification_fraud_review
prize_tax_required
reward_tax_required
sweepstakes_rules_review
gamification_fraud_review
points_abuse_review
fraud_review
dispute_open
moderation_review
copyright_dispute
legal_notice_review
chargeback_risk
admin_hold
provider_restricted
tax_reporting_required
mfa_required
phone_verification_required
account_recovery_review
security_lockout
other
```

**`AccessAuditAction`**

```text
file_read
file_download
message_read
thread_opened
video_joined
location_revealed
privacy_export_generated
privacy_erasure_started
privacy_erasure_completed
healthcare_policy_checked
healthcare_payload_redacted
healthcare_payload_blocked
admin_redacted_view
admin_blocked_view
processor_balance_read
payout_account_read
tax_profile_read
tax_dashboard_opened
payout_request_started
sensitive_financial_step_up_verified
phone_number_changed
account_recovery_completed
course_video_started
course_video_completed
live_video_token_issued
digital_download_url_issued
digital_download_denied
digital_download_started
digital_download_completed
course_video_playback_granted
course_video_playback_denied
agreement_viewed
agreement_downloaded
agreement_signed
agreement_hash_verified
agreement_tamper_detected
agreement_manual_opt_out
media_signed_url_issued
media_signed_url_denied
media_upload_rejected
media_malware_detected
media_metadata_scrubbed
media_quarantined
media_promoted_to_ready
calendar_connection_started
calendar_connection_authorized
calendar_connection_revoked
calendar_free_busy_synced
booking_hold_created
booking_confirmed
booking_slot_lock_failed
booking_orchestration_started
booking_orchestration_failed
```

No Observability-specific status or severity enums are confirmed in the supplied Prisma evidence.

### 8.2 Referenced but not owned CL-09 inputs/projections

| Record / concept | Owner outside CL-09 | CL-09 use |
| --- | --- | --- |
| `DataSensitivity` | Shared/schema ownership not cleanly resolved in supplied registry; consumed by Audit and sensitivity owners. | Classifies access evidence. |
| `HealthcareAccessDecision` | Healthcare / Regulated Services | Audit records the healthcare-owned allow/redact/block/deny outcome. |
| `SearchUpsertEvent` | Search / Public Visibility | Search projection queue truth; CL-09 requests work but does not write it. |
| `MediaAsset`, `MediaAccessGrant`, media processing records | Media / File Access | Evidence/file context and execution. |
| `ProcessedStripeEvent`, `ProcessedCalendarEvent`, other processed provider records | Provider-owning Modules | Operational correlation only; never CL-09 dedupe truth. |
| `OrderEvent`, `BookingEvent`, `JobInterviewEvent`, `UserSecurityEvent`, `AgreementEvent` | Their domain Modules | Domain lifecycle evidence that remains separate from generic Audit. |
| `DataRetentionExemption` | Privacy / Data Erasure | Records Privacy-owned exemption after CL-09 owner returns retention facts. |
| `TrackSubscriptionEvent`, `TrackEntitlementGrant` | Track Subscription & Entitlement | Context for subscription failure or entitlement effects; never CL-09 commercial truth. |

### 8.3 Claimed CL-09 records absent from Prisma

| Claimed record | Owner | Architectural meaning | Current status |
| --- | --- | --- | --- |
| `AuditEventType` | Audit / Event Ledger per Deep Module Registry | Claimed controlled audit type vocabulary. | **Unresolved discrepancy:** absent; current `AuditEvent.action` is `String`. |
| `AuditEventActor` | Audit / Event Ledger per Deep Module Registry | Claimed audit actor vocabulary. | **Unresolved discrepancy:** absent; current actor is nullable `actorUserId`. |
| `SystemEvent` | Observability / Ops | Operational event truth. | **Missing from Prisma.** |
| `IntegrationFailure` | Observability / Ops | Normalized technical integration-failure visibility. | **Missing from Prisma.** |
| `QueueJob` | Observability / Ops | Operational queue/job visibility, not domain job truth. | **Missing from Prisma.** |
| `OpsIncident` | Observability / Ops | Grouped operational incident truth. | **Missing from Prisma.** |

### 8.4 Proposed or unresolved additional records

These are **not current source truth** and must not be created without accepting the associated ruling.

| Candidate | Status | Why it is being considered |
| --- | --- | --- |
| Moderation evidence snapshot record pointing to Media-held bytes/hash | **Proposed Ruling** | Current mutable JSON does not prove what content/evidence was preserved before enforcement. |
| Moderation enforcement run/step correlation record | **Proposed Ruling** | `ModerationAction` has no downstream acknowledgment/retry/restoration state. |
| Hold target link or validated polymorphic target representation | **Proposed Ruling** | Current hold FKs cannot represent claimed content, payout, prize, reward, verification, job, or other targets. |
| Hold review work item / claim record | **Unresolved** | Manual review queues/escalation are claimed, but no queue lifecycle schema exists. |
| Repeat-infringer decision/signal record | **Unresolved** | Responsibility is claimed but no schema/policy exists. |
| Content fingerprint/similarity signal record | **Unresolved** | Piracy/duplicate-content concern is stated, but fingerprint ownership/provider/policy is not established. |

---

## 9. Lifecycle Ownership

### 9.1 Report lifecycle

- **Owner:** Content Moderation & Legal Notice.
- **Confirmed statuses:** `submitted`, `triaged`, `under_review`, `action_taken`, `dismissed`, `closed`.
- **Transition authority:** only Content Moderation & Legal Notice commands may change `Report.status` after Role / Authority approval.
- **Other Modules may:** submit a report through the public intake command or react to published report/case events.
- **Must not be confused with:** `LegalNotice`, `ModerationCase`, `ComplianceHold`, or target object status.
- **Transition graph:** the vocabulary is confirmed; the complete allowed graph is not. Implementation must use an explicit owner state machine and may not infer legal semantics from enum ordering.

### 9.2 LegalNotice lifecycle

- **Owner:** Content Moderation & Legal Notice.
- **Confirmed statuses:** `received`, `validating`, `valid`, `invalid`, `action_taken`, `counter_notice_received`, `restored`, `rejected`, `closed`.
- **Transition authority:** Content Moderation & Legal Notice under versioned notice-type policy and authorized reviewer/system rules.
- **Other Modules may:** provide target facts, execute enforcement, deliver notices, or supply restoration acknowledgments.
- **Must not be confused with:** an Offering/media disable status, a report, or an email thread.
- **Transition graph/deadlines:** **Unresolved legal-policy detail.** Do not invent DMCA/DSA timing or transition rules from enum order.

### 9.3 ModerationCase lifecycle

- **Owner:** Content Moderation & Legal Notice.
- **Confirmed statuses:** `opened`, `triaged`, `under_review`, `waiting_for_counter_notice`, `escalated`, `action_taken`, `dismissed`, `closed`.
- **Transition authority:** authorized moderation/legal review commands.
- **Other Modules may:** supply target facts or acknowledge owner-local enforcement effects.
- **Must not be confused with:** `Dispute`, `ComplianceHold`, `OpsIncident`, or a target owner's workflow.
- **Transition graph:** owner must encode it explicitly; exact reopening/reversal rules are unresolved.

### 9.4 ModerationAction record lifecycle

- **Owner:** Content Moderation & Legal Notice.
- **Current shape:** creation-only append-style decision/action row; there is no status field.
- **Transition authority:** none after append except any future correction pattern explicitly approved by architecture; downstream execution must not mutate the meaning of the original action.
- **Must not be confused with:** downstream completion/acknowledgment truth.

### 9.5 ComplianceHold lifecycle

- **Owner:** Admin Review / Compliance Hold.
- **Confirmed statuses:** `active`, `released`, `expired`.
- **Confirmed transition meaning:** an active hold may end by authorized release or by an approved expiry rule.
- **Transition authority:** Hold Module only. Source Modules may request creation/release and provide evidence.
- **Must not be confused with:** KYC/tax/background/healthcare/dispute/moderation/job-compliance state or consumer-local blocked fields.
- **Unresolved:** reopen semantics, expiry condition, target/cardinality model, semantic uniqueness, and review-queue lifecycle.

### 9.6 AuditEvent lifecycle

- **Owner:** Audit / Event Ledger.
- **Statuses:** none; creation-only evidence.
- **Authority:** append through the canonical `appendAuditEvent` operation.
- **Mutation rule:** insert-only evidence. Update/delete by normal app/admin roles is prohibited.
- **Must not be confused with:** domain lifecycle event ledgers or operational failures.

### 9.7 AccessAuditLog lifecycle

- **Owner:** Audit / Event Ledger.
- **Statuses:** none; creation-only evidence.
- **Authority:** append through `recordSensitiveAccess` after the data/context owner makes the access decision.
- **Mutation rule:** insert-only evidence; optional hash fields do not by themselves prove append-only enforcement.
- **Must not be confused with:** `ResumeAccessLog`, Media access event truth, agreement event truth, or authorization result ownership.

### 9.8 Observability lifecycles

| Record | Owner | Status vocabulary | Transition authority | Important separation |
| --- | --- | --- | --- | --- |
| `SystemEvent` | Observability / Ops | **Unresolved; model absent.** Conceptually append an operational observation. | Observability ingestion only. | Never business state. |
| `IntegrationFailure` | Observability / Ops | **Unresolved; model absent.** Needs a defined failure/recovery lifecycle if persisted. | Observability records normalized technical state; provider/business owners keep their own state. | Never provider dedupe or business failure status. |
| `QueueJob` | Observability / Ops / queue infrastructure | **Unresolved; model absent.** Canonical Shared Operations establish it as operational telemetry/projection. | Shared queue runner emits telemetry; workflow owner keeps completion meaning. | Never `DataErasureJob`, search work, booking orchestration, etc. |
| `OpsIncident` | Observability / Ops | **Unresolved; model absent.** Needs explicit open/investigate/mitigate/resolve vocabulary if persisted. | Observability / authorized operators. | Never `ComplianceHold` or `ModerationCase`. |

---

## 10. Public Module Interfaces

“Public” means an internal Workin Ants Module contract, not necessarily an internet route.

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Result kind | Consumers must not infer/recreate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `submitModerationReport` | Content Moderation & Legal Notice | All report-capable Modules; controlled user/external intake | Create report truth. | Actor/reporter context, `ReportSource`, typed target, `ReportReason`, safe details/evidence refs, idempotency key. | `reportId`, status, received timestamp. | Truth | Do not create local report/case rows. |
| `submitLegalNotice` | Content Moderation & Legal Notice | Controlled legal intake/admin | Create formal notice truth. | Notice type, target, submitter/rights-owner fields, claimed work/URL/statements/evidence refs. | `legalNoticeId`, status, received time. | Truth | Do not treat email receipt or target disable status as legal-notice truth. |
| `triageReport` | Content Moderation & Legal Notice | Moderation/admin tools | Apply report triage policy. | Report ID, reviewer, triage decision/note, expected version. | New report state and next action. | Decision + truth | Do not alter target state directly. |
| `openModerationCase` | Content Moderation & Legal Notice | Moderation/legal workflows | Open review container. | Trigger report/notice/admin concern, target, opener, summary. | Case ID/status. | Truth | Do not use Hold/Dispute as the case. |
| `getModerationCase` | Content Moderation & Legal Notice | Authorized reviewers/support | Return owner-composed case/evidence view. | Case ID, viewer context. | Case, related report/notice/actions, minimized target/evidence summaries. | Truth + projection | Do not directly join arbitrary target tables. |
| `listModerationQueue` | Content Moderation & Legal Notice | Admin moderation UI | Return actionable cases. | Filters, viewer authority, cursor. | Paginated cases/assignment/deadline summaries. | Projection | Queue projection is not a new lifecycle. |
| `recordModerationAction` | Content Moderation & Legal Notice | Moderation/legal workflow | Persist approved action/decision. | Case, actor, action type, target, rationale/reference. | Action ID/time. | Truth/evidence | Do not infer downstream execution success. |
| `queryActiveModerationRestriction` | Content Moderation & Legal Notice | Target owners, Search, delivery Modules | Tell a consumer whether moderation/legal restriction applies. | Typed target + action/surface context. | Active restriction decision + source case/action refs. | Decision | Consumer must not rebuild moderation policy from raw cases. |
| `executeModerationDecision` | Protocol owned by Moderation decision; implemented by target owners | Media, Search, Messaging, Marketplace, Digital Goods, Video, other target owners | Apply an authorized moderation action in owner-local truth. | Case/action IDs, typed target, requested effect, reason, idempotency/correlation. | `acknowledged/completed/failed/restored` evidence and owner state reference. | Cross-Module protocol | Moderation must not directly write target tables; target owner must not create competing moderation truth. |
| `requestComplianceHold` | Admin Review / Compliance Hold | Compliance-sensitive Modules | Create authoritative stop sign. | Typed target, reason, source/evidence refs, requested scope, actor/system context, idempotency key. | Hold ID, active status, applicable scope. | Truth | No local hold model or blocked boolean. |
| `evaluateComplianceHold` | Admin Review / Compliance Hold | Any gated workflow | Return active stop signs for target/action. | Target + requested action + context. | Allow/block decision, hold IDs, safe reasons, scope, expiry if applicable. | Decision | Do not reconstruct from foreign links or reasons alone. |
| `releaseComplianceHold` | Admin Review / Compliance Hold | Source Modules/admin review | Release an existing stop sign. | Hold ID, source decision ref, actor, reason, idempotency key. | Released hold + time/actor. | Truth | Release is not underlying compliance approval. |
| `getComplianceHold` / `listActiveComplianceHolds` | Admin Review / Compliance Hold | Authorized consumers/admin | Read hold truth. | Hold/target filters + authority. | Safe hold view(s). | Truth | Do not bypass `evaluateComplianceHold` for action policy. |
| `appendAuditEvent` | Audit / Event Ledger | All Modules | Append generic important-action proof. | Actor/system ref, action, target, request/correlation, safe metadata; canonical registry also calls for outcome. | Audit event ID/time. | Evidence | Do not use as business lifecycle truth. |
| `recordSensitiveAccess` | Audit / Event Ledger | Sensitive data/access owners | Append protected-access outcome proof. | Actor, action, sensitivity, target, owner decision, request context, safe metadata. | Access log ID/time/hash info if enabled. | Evidence | Audit did not authorize the access. |
| `queryAuditEvents` | Audit / Event Ledger | Authorized admin/compliance/support | Query generic action evidence. | Filters, cursor, viewer authority. | Redacted paginated events. | Evidence | Do not infer target current state. |
| `querySensitiveAccessHistory` | Audit / Event Ledger | Authorized compliance/security | Query sensitive-access proof. | Target/actor/action/sensitivity/request/time filters. | Redacted paginated access evidence. | Evidence | Do not infer authorization policy. |
| `createRequestContext` | Observability/platform | All request/job entry points | Create correlation/trace context. | Incoming request/job/provider context. | Safe request/correlation/trace IDs + actor ref. | Platform context | Do not embed domain payloads. |
| `writeStructuredLog` | Observability / Ops | All Modules | Emit structured operational log. | Level, operation, safe dimensions, request context. | Log acknowledgement/provider ref if any. | Telemetry | Log is not source truth. |
| `recordIntegrationFailure` | Observability / Ops | Provider owners/workers | Normalize technical failure visibility. | Provider/integration, operation, source ref, retryability, safe diagnostics, request ID. | Failure record/ref when persistence is approved. | Operational truth | Do not replace business/provider-dedupe state. |
| `recordQueueTelemetry` | Observability / Ops / queue infra | Shared worker runner | Record claim/attempt/heartbeat/retry/completion/dead-letter visibility. | Queue/job type, source ref, attempt/timing/outcome. | Queue visibility record/metric. | Projection/operational truth | Do not infer domain completion. |
| `checkServiceHealth` | Observability coordinates; owner supplies check | Admin/health tooling | Standardize component health. | Registered check + timeout/scope. | Healthy/degraded/unavailable/delayed + safe detail. | Projection | Do not turn health into business lifecycle. |
| `correlateOpsIncident` | Observability / Ops | Ops/admin/system | Group operational signals. | Signals, correlation, severity/context. | Incident ID/status if persistence is approved. | Operational truth | Incident cannot block business actions by itself. |

### Interface conflict notes

- The canonical `appendAuditEvent` build rule calls for request ID and outcome; current `AuditEvent` has neither explicit field. This is a **schema/contract alignment decision** that must be resolved before finalizing the command DTO.
- `requestComplianceHold` / `evaluateComplianceHold` require typed target + scope, while current `ComplianceHold` does not represent the claimed target breadth. This is a **blocking architecture decision** for a general-purpose hold API.
- Observability public interfaces are canonically named, but their four claimed persistence records are absent. Persistence and lifecycle vocabulary must be ruled before repository implementation.

---

## 11. Canonical Shared Operations Used by This Cluster

The current Canonical Shared Operations Architecture supplies canonical **operation names** rather than permanent `SH-###` identifiers. Do not invent numeric IDs in code or context until the registry supplies them.

### 11.1 Confirmed operations

| Canonical operation | Plain-English meaning | Canonical owner | CL-09 consumers | Reusable mechanism | Local policy retained in CL-09 | Invocation point | Must not be duplicated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Resolve provider session/system credential to trusted Workin Ants actor context. | Identity & Access | All four Modules | Request middleware + actor context | Which CL-09 action is being attempted. | Every protected entry point. | Local `currentUser`, moderator-auth, hold-auth, audit-auth helpers. |
| `authorizeResourceAction` | Decide platform/org/participant/ownership-scoped permission. | Role / Authority | All four Modules | Typed authorization decision | Moderation/hold/audit/ops action vocabulary and owner relationship facts. | Before protected query/mutation. | Feature-local admin/role engines. |
| `requireStepUpForSensitiveAction` | Require fresh high-assurance authentication for designated high-risk action. | Identity & Access | Sensitive audit export/evidence review or hold release where policy requires | Step-up/session mechanism | Which CL-09 actions require step-up. | After authority, before high-risk action. | Local MFA/OTP/passkey checks. |
| `evaluateComplianceHold` | Return active stop signs applicable to target/action. | Admin Review / Compliance Hold | Moderation and all external workflow consumers | One hold decision API | Hold reason-to-action applicability. | Before blocked business action or moderation effect requiring a stop sign. | Local `isBlocked`, payout/job/content hold checks. |
| `requestComplianceHold` | Request an authoritative stop sign. | Admin Review / Compliance Hold | Moderation and external compliance owners | Typed idempotent hold command | Whether source facts justify requesting a hold. | After owner decision, before affected action continues. | Per-feature hold creation tables/services. |
| `releaseComplianceHold` | Release hold after source condition resolved. | Admin Review / Compliance Hold | Source owners/admin review | Typed idempotent release command | Hold release policy. | After source decision. | Direct status writes from consumers. |
| `appendAuditEvent` | Append generic important-action proof. | Audit / Event Ledger | Moderation, Hold, Ops admin actions | Insert-only command | Audit action/metadata schema. | Immediately after/within owner transaction boundary as appropriate. | `moderationAudit`, `holdAudit`, generic log tables. |
| `recordSensitiveAccess` | Append protected-access outcome proof. | Audit / Event Ledger | Moderation evidence viewers, Hold sensitive review, Ops sensitive diagnostics | `AccessAuditLog` append | Data sensitivity and owner access outcome. | After decision; record allow/deny/redact/block or credential issuance. | PHI/finance/resume/file-specific generic audit tables. |
| `createRequestContext` | Propagate correlation/trace/request/actor IDs. | Observability/platform | All four Modules | Async request context | None beyond safe dimensions. | Request/job/provider entry. | Per-module correlation ID utilities. |
| `writeStructuredLog` | Emit safe machine-readable operational logs. | Observability / Ops | All four Modules | One logger | Operation-specific safe fields. | Throughout execution. | Separate loggers/formatters. |
| `sanitizeTelemetryMetadata` | Remove or reject secrets/sensitive payloads from audit/telemetry. | Observability / Ops + Audit payload policy | Audit + Ops; every producer | Allowlists/redaction/truncation | Allowed metadata per audit action/sensitivity. | Before persistence/transmission. | Local ad hoc redactors. |
| `captureException` | Send exception to monitoring provider with safe context. | Observability / Ops | All four Modules | One provider adapter | Error classification/context. | Unexpected exception boundary. | Independent Sentry clients. |
| `emitMetric` | Publish operational metric. | Observability / Ops | All four Modules | One metrics client | Metric meaning/threshold source. | Request/job/provider lifecycle points. | Per-module metrics clients. |
| `recordIntegrationFailure` | Persist normalized technical failure/degradation evidence. | Observability / Ops | Moderation enforcement workers and all provider-owning Modules | Common failure record contract | Domain owner retryability/business result. | After normalized technical failure. | Generic failure tables in each Module. |
| `recordQueueTelemetry` | Record shared queue execution visibility. | Observability / Ops / queue infrastructure | CL-09 workers | Shared worker instrumentation | Domain job completion meaning. | Queue claim/attempt/heartbeat/retry/terminal state. | Local queue-monitor ledgers. |
| `checkServiceHealth` | Standardize dependency/component health response. | Observability coordinates; owner supplies check | Ops admin surfaces | Health registry | What healthy means for each component. | Health/readiness endpoints and dashboard. | Per-module health frameworks. |
| `correlateOpsIncident` | Group related failures/queue/system signals into incident. | Observability / Ops | Ops tooling | Correlation/incident mechanism | Incident criteria and operator workflow. | After severity/correlation threshold. | Local generic incident tables. |
| `requestNotification` | Submit safe alert for delivery. | Notification | Moderation, Hold, Audit integrity, Ops incidents | Delivery request/templating | Trigger and message meaning. | After authoritative event/decision. | SES/SMS/push dispatch inside CL-09. |
| `executeIdempotentCommand` | Ensure retries produce one business effect. | Platform app infrastructure | All CL-09 mutations | Idempotency claim/result | Semantic key/equivalence/conflict policy. | Mutating public commands. | Per-module idempotency stores. |
| `deduplicateDomainEvent` | Prevent repeated consumer side effects from same event. | Platform event infrastructure + consumer inbox | CL-09 event handlers | Inbox claims | Handler/version and side effect. | Event consumption. | Ad hoc processed-event tables unless provider/domain-specific truth requires them. |
| `publishDomainEvent` | Reliably publish versioned event after source transaction commits. | Platform outbox infrastructure | Moderation, Hold, Audit/ops only where meaningful | Transactional outbox | Event names/payload/emission conditions. | After source write. | Fire-and-forget event publishing. |
| `enqueueReliableJob` | Persist async work with retries/leases/dead-letter visibility. | Shared queue infrastructure | Moderation deadline/enforcement workers, Audit integrity/export, Ops monitors | Queue client/worker shell | Payload, completion meaning, legal retry constraints. | When work must be asynchronous. | Per-module queue frameworks. |
| `executeRetryWithBackoff` | Retry transient failures safely. | Shared queue/platform | CL-09 workers | Backoff/jitter/max attempts | Retryability and side-effect legality. | Technical failure. | Hand-written retry loops. |
| `orchestrateWorkflowSteps` | Run multi-step cross-Module workflow without owning participants' truth. | Workflow owner using shared runner | Moderation enforcement | Run/step/retry/compensation plumbing | Required steps, order, compensation/restoration meaning. | After `ModerationAction` authorizes multi-owner effects. | Universal saga policy or ad hoc chained calls. |
| `acquireAggregateLock` | Serialize conflicting commands. | Shared persistence infrastructure | Moderation cases, holds, incident transitions | DB lock mechanism | Lock key/conflict behavior. | Before conflicting transition. | In-memory mutexes. |
| `withOptimisticConcurrency` | Reject stale writes. | Shared persistence infrastructure | Moderation cases/notices, holds, incidents | CAS/version mechanism | Retry/merge/conflict policy. | Mutation of mutable lifecycle rows. | Custom inconsistent concurrency checks. |
| `transitionLifecycleState` | Reusable state-machine plumbing while owner retains graph. | Shared mechanism | Moderation, Hold, Ops incident once statuses exist | Transition validation + transactional update hooks | Each lifecycle's valid graph. | Every owner status transition. | One generic global lifecycle policy. |
| `runDeadlineExpiration` | Find records past owner-defined deadline and invoke owner transition. | Shared scheduler/queue | Legal notice deadlines if policy sets `actionDueAt`; hold expiry if approved | Scheduler/batching | Deadline rules and legal meaning. | Scheduled scan. | Per-module cron engines. |
| `hashCanonicalPayload` | Produce stable digest over canonical fields. | Shared crypto capability | Audit/evidence snapshot | Canonical serialization/hash | What the hash proves and included fields. | Evidence snapshot/integrity creation. | Local hash implementations. |
| `validateOwnedTargetReference` | Validate cross-Module target through its owner. | Target owner | Moderation, Hold | Shared contract/separate implementations | Allowed relationship/action for target. | Before persisting polymorphic target reference or executing action. | Cross-domain Prisma target lookup. |
| `requestSearchProjectionRefresh` | Request index/update/hide/remove/restore work. | Search / Public Visibility | Moderation | Search command | Moderation decision/reason and source version. | After action requiring public visibility change. | Typesense calls or `SearchUpsertEvent` writes in CL-09. |
| `executePrivacyInstruction` | Execute Privacy-owned instruction against owner records. | Privacy orchestrates; each owner executes | All four CL-09 data owners | Common request/result protocol | Record-specific erase/anonymize/retain/export behavior. | During Privacy target execution. | CL-09-local privacy-request workflows. |
| `enumerateSubjectData` | Enumerate owner-held subject data and supported dispositions. | Each data owner through Privacy contract | All four CL-09 data owners | Shared enumeration contract | Schema relationships and export meaning. | Privacy discovery. | Global DB crawler. |
| `evaluateRetentionRequirement` | Return owner facts requiring retention; Privacy records exemption. | Data owner + Privacy | Moderation, Hold, Audit, Ops | Shared contract | Legal/security/fraud/audit retention fact. | Before erasure. | Local retention-exemption tables. |
| `anonymizePersonalFields` | Apply approved field-level anonymization. | Shared primitive; record owner maps fields | CL-09 data owners | Versioned field mapping mechanism | Which fields can change without breaking proof. | Privacy executor. | Ad hoc erasure helpers. |
| `submitModerationReport` | Submit typed abuse/legal allegation. | Content Moderation & Legal Notice | Platform Modules | Intake contract | Report reason/source/evidence requirements. | Report creation. | Local report models. |
| `executeModerationDecision` | Apply moderation/legal effect inside each target owner. | Moderation decision + target owner execution | Moderation and target owners | Dispatch/ack protocol | Decision semantics and owner-local execution. | After `ModerationAction`. | Direct cross-module writes. |

### 11.2 Proposed shared operations relevant to CL-09

These appear in the Canonical Shared Operations synthesis as **Proposed Ruling**, not confirmed implementation authority.

| Operation | Proposed owner / classification | CL-09 use | Rule until accepted |
| --- | --- | --- | --- |
| `claimWorkItem` | Shared work-queue/locking capability | Manual moderation/hold review claim and lease. | Do not build a universal review queue schema or competing per-Module claim primitive until accepted. Module-owned assignment fields may still be used where already present. |
| `resolveModerationTarget` | Target registry contract; owner-specific resolvers | Safe minimized target context for moderators. | Prefer owner-specific interfaces now; do not create universal cross-domain repository. |
| `preserveEvidenceSnapshot` | Shared evidence mechanism; decision owner retains proof meaning | Immutable moderation/hold decision evidence using Media + hash primitives. | Do not create a generic Audit-owned evidence table. |
| `correlateEnforcementResult` | Content Moderation & Legal Notice cluster-local orchestration | Durable acknowledgment/retry/restoration tracking for one moderation action. | No new execution schema until accepted; do not overload `ModerationAction` with downstream owner truth. |
| `hashChainRecords` | Shared cryptographic capability; owner unresolved | Tamper-evident AccessAuditLog/Agreement chains. | Optional hash fields must not be treated as proof of a complete chain until partition/sequence/algorithm/verification policy is approved. |
| `returnDecisionResult` | Shared contract; policy owner varies | Consistent hold/moderation/readiness result shape. | May inspire DTO shape; do not create global policy engine. |

### 11.3 Unresolved shared capability

`computeContentFingerprint` remains unresolved. Exact checksums may be Media-owned mechanics, but perceptual matching/provider choice, threshold policy, persistence, and infringement meaning are not established. A fingerprint match may only be a signal; it must never automatically become legal infringement truth or a moderation action.

---

## 12. Cross-Module Data Flows

### 12.1 User or system report to moderation decision

1. **Trigger — source Module or controlled intake:** an actor reports a typed target.
2. **Identity — Identity & Access:** `resolveAuthenticatedActor` when an authenticated actor exists; controlled external notice/report intake uses its separately approved identity/evidence rules.
3. **Authority — Role / Authority:** authorize the intake or admin action.
4. **Intake write — Moderation:** `submitModerationReport` validates target via owner interface and writes `Report(submitted)` idempotently.
5. **Audit — Audit:** append a generic intake action if policy requires; do not copy full evidence payload.
6. **Triage — Moderation:** reviewer/system applies owner triage policy and may open `ModerationCase`.
7. **Case evidence read — target owners/Media:** return minimized target summary and protected evidence through owner access rules; sensitive reads call `recordSensitiveAccess`.
8. **Decision — Moderation:** authorized reviewer records `ModerationAction` and required case transition.
9. **Outbox — Moderation/platform:** publish domain event or enqueue enforcement workflow after the authoritative transaction commits.
10. **Downstream requests — target owners:** use `executeModerationDecision`; each target owner changes its own state.
11. **Search — Search owner:** moderation requests projection refresh/removal; Search writes `SearchUpsertEvent` and Typesense state.
12. **Hold — Hold owner:** if a reusable block is required, moderation calls `requestComplianceHold`.
13. **Notification — Notification:** moderation requests safe notices to affected parties/reviewers.
14. **Ops — Observability:** technical failures become `recordIntegrationFailure`/queue telemetry; business rejection remains in owner result.
15. **Reconciliation — Moderation:** if the proposed enforcement-correlation capability is accepted, track missing/failed acknowledgments and restoration work.

### 12.2 Formal legal notice and counter-notice

1. Controlled intake creates `LegalNotice(received)`.
2. Moderation validates required fields under a versioned legal policy; exact legal sufficiency is owner/legal-gated.
3. A `ModerationCase` is opened or linked as allowed by approved cardinality rules.
4. Evidence is preserved before destructive or externally visible enforcement.
5. A `ModerationAction` records takedown/rejection/escalation decision.
6. Target owners execute hide/freeze/public-URL removal/download/playback/search effects.
7. Notification delivers required notices; delivery is not proof of legal sufficiency by itself.
8. Counter-notice intake updates legal/case truth only through Moderation.
9. Deadline work uses `actionDueAt` only under approved legal policy and shared scheduler.
10. Restoration uses a new moderation action and target-owner restoration commands; original action history is preserved.

### 12.3 Compliance hold creation and gating

1. Source owner evaluates its own fact: e.g. dispute open, tax required, verification review, moderation review.
2. Source owner calls `requestComplianceHold` with typed target, reason, source/evidence refs, and idempotency key.
3. Hold Module validates target/authority/semantic duplicate policy and writes `ComplianceHold(active)`.
4. Hold Module appends generic audit proof.
5. Any consuming business action calls `evaluateComplianceHold` rather than reading a local boolean.
6. Consumer receives allow/block plus safe hold references and applies its own lifecycle behavior.
7. When source fact resolves, source owner calls `releaseComplianceHold`; Hold Module alone transitions status.
8. Notification/Audit are requested as required. Hold release does not mutate the source compliance record.

### 12.4 Sensitive evidence access

1. Viewer requests audit evidence, moderation evidence, hold review context, or protected operational diagnostics.
2. Identity resolves actor; Role / Authority evaluates general permission.
3. Data/context owner evaluates contextual entitlement/redaction and optional step-up requirement.
4. Media issues any file URL only after owner decision; it never infers legal entitlement from a case ID alone.
5. Audit writes `AccessAuditLog` with action, target, sensitivity, access decision if applicable, request ID, and minimized metadata.
6. Caller receives allowed/redacted/blocked/denied result.

### 12.5 Operational failure to incident

1. Source Module/provider adapter performs its own business/provider operation.
2. Provider owner verifies/deduplicates/translates provider state where applicable.
3. Technical failure is normalized and sent to `recordIntegrationFailure` with source ref and request ID.
4. Shared worker runner records queue telemetry for attempts/retries/dead-letter.
5. Structured log/metric/error provider receive sanitized telemetry.
6. Observability correlates repeated/severe signals into `OpsIncident` if persistence/rules are approved.
7. Notification sends operational alert if alert policy requires it.
8. Provider/business owner remains responsible for reconciliation and business-state repair.

### 12.6 Audit integrity flow

1. Audit append command validates/sanitizes input.
2. Insert occurs under append-only storage permissions.
3. If approved hash chaining applies, shared hash primitive calculates chain values using Audit-owned chain scope/canonical fields.
4. Integrity verifier recomputes chain in background.
5. Integrity failure creates operational failure/incident and protected audit evidence; it never rewrites the historical row to “fix” it.

---

## 13. Cross-Cluster Bridges

| Source | Destination | Information / command | Authoritative owner | Interface / event | Forbidden coupling |
| --- | --- | --- | --- | --- | --- |
| CL-01 Identity & Access | CL-09 | Actor/session/step-up assurance. | Identity & Access | `resolveAuthenticatedActor`, `requireStepUpForSensitiveAction`. | CL-09 auth/session logic. |
| CL-01 Role / Authority | CL-09 | Permission decisions for moderation, hold, audit, ops. | Role / Authority | `authorizeResourceAction`. | Local admin-role interpretation. |
| CL-01 Track Subscription & Entitlement | CL-09 Observability/Moderation context | Entitlement/subscription source refs and provider failure signals where relevant. | Track Subscription & Entitlement | Owner event/query; Observability failure ingestion. | CL-09 entitlement policy or premium flags. |
| CL-02 Search / Public Visibility | Moderation | Execute de-index/re-index after decision. | Search | `requestSearchProjectionRefresh`; Search-owned worker. | Direct `SearchUpsertEvent`/Typesense writes from Moderation. |
| CL-03 Marketplace Supply | Moderation/Hold | Offering/product/course target summary and owner-local enforcement. | Marketplace Supply | Owner target query + `executeModerationDecision` handler. | Moderation directly changing Offering lifecycle. |
| CL-03 Payment / Payout / Tax | Hold/Audit/Ops | Financial readiness facts, hold requests/gates, sensitive-access evidence, provider failures. | Payment for financial truth; Hold/Audit/Ops for their separate truth. | `request/evaluate/releaseComplianceHold`, `recordSensitiveAccess`, `recordIntegrationFailure`. | Reading Stripe state to decide holds inside CL-09. |
| CL-03 Trust Verification / Healthcare | Hold/Audit | Verification/healthcare decision facts and sensitive access outcome. | Trust/Healthcare | Owner readiness/decision query; hold/audit commands. | CL-09 reinterpreting provider or healthcare policy. |
| CL-04 Transaction / Order | Hold/Audit/Moderation | Order target facts; disputes may request holds; contract access is audited. | Transaction / Order, Review / Dispute | Owner queries/events + CL-09 commands. | AuditEvent or Hold as Order truth. |
| CL-05 Media / File Access | Moderation/Audit | Preserve/freeze/revoke public URL; deliver protected evidence; media access proof. | Media for mechanics; Moderation for decision; Audit for generic access proof. | `executeModerationDecision`, Media public commands, `recordSensitiveAccess`. | Moderation R2 calls or local signed URLs. |
| CL-05 Digital Goods / Video | Moderation | Disable/revoke/restore grants/playback after moderation decision. | Digital Goods / Video for execution truth. | `executeModerationDecision` owner handlers. | Moderation writing grant tables. |
| CL-05 Booking / Calendar | Audit/Ops | Sensitive booking/calendar action proof and integration failure signals. | Booking for lifecycle/provider truth. | Audit/ops commands. | CL-09 processed-calendar-event state. |
| CL-06 Hiring / Candidate | Moderation/Hold/Audit | Reported Job/message/media/candidate context; job-compliance hold signals; protected resume access evidence. | Hiring/Candidate/Job Compliance. | Owner query, hold command, audit command. | CL-09 resume access authorization or Job lifecycle changes. |
| CL-07 Messaging | Moderation/Audit | Message/thread target context and restriction execution; sensitive read evidence. | Messaging | Target query + moderation execution handler + `recordSensitiveAccess`. | Moderation mutating Message/Thread rows. |
| CL-07 Notification | All CL-09 | Deliver user/admin/legal/ops messages. | Notification | `requestNotification`. | SES/SMS/push code in CL-09. |
| CL-08 Privacy / Data Erasure | All CL-09 data owners | Privacy target discovery, retention decision recording, erasure/anonymization/export execution. | Privacy for request/orchestration; CL-09 owners for their records. | `enumerateSubjectData`, `evaluateRetentionRequirement`, `executePrivacyInstruction`. | Privacy directly rewriting every CL-09 table; CL-09 local PrivacyRequest. |
| CL-08 Location Safety | Audit/Moderation context | Location-reveal access evidence or reported location-sensitive target context. | Location Safety | Owner decision + `recordSensitiveAccess`. | Audit deciding reveal eligibility. |
| CL-10 Sweepstakes / Rewards | Hold/Audit/Ops | Prize/reward tax/fraud hold requests and operational evidence. | Sweepstakes/Rewards for domain truth; Hold/Audit/Ops separate. | Hold/audit/ops contracts. | Local prize/reward block flags replacing hold. |

---

## 14. Authentication and Authorization

### Authentication dependency

Every authenticated CL-09 request begins with `resolveAuthenticatedActor`. System/service actors must use a typed trusted system context; nullable user IDs in audit or moderation records do not authorize anonymous mutations.

### Authorization dependency

`authorizeResourceAction` is the general authority engine. CL-09 Modules supply action and relationship facts, for example:

- report submission versus report review;
- legal-notice review versus legal-notice status lookup;
- moderation case assignment/action/closure;
- hold creation, release, queue review, or escalation;
- audit viewer, sensitive-access viewer, evidence export;
- ops dashboard versus incident mutation.

CL-09 must not infer authority from `UserRole`/`PlatformRole` alone.

### Contextual facts

- Moderation target owners supply ownership/participant/visibility/sensitivity facts.
- Hold source owners supply the source condition and evidence reference.
- Audit caller supplies data sensitivity and the owner-owned access outcome.
- Observability callers supply safe source references and retryability/business context; Observability does not reinterpret business permission.

### High-risk operations

`requireStepUpForSensitiveAction` is available for actions designated by security policy, including potentially high-impact hold release, legal evidence export, financial/healthcare diagnostic review, or security-sensitive audit export. Which exact actions require step-up is **not established by CL-09 evidence** and must be defined by Identity/Security policy rather than guessed.

### Service-role actions

Service-role server actions may perform system transitions only through the same owner application services and validation paths. A service role is not a bypass for owner invariants, target validation, append-only rules, or audit evidence.

---

## 15. Compliance and Readiness Composition

| Fact / gate | Truth owner | CL-09 role | What CL-09 must not do |
| --- | --- | --- | --- |
| Moderation/legal notice validity and action | Content Moderation & Legal Notice | Primary decision/proof owner for DMCA/DSA moderation workflow. | Treat target disable state or Notification delivery as legal truth. |
| Reusable platform hold | Admin Review / Compliance Hold | Primary hold lifecycle owner. | Decide KYC/tax/background/healthcare/dispute facts itself. |
| KYC / tax / payout readiness | Payment / Payout / Tax | May trigger/request/evaluate hold; audit sensitive financial access. | Interpret provider state or recreate financial readiness. |
| Verification / screening | Trust Verification / Screening | Hold consumer/requester and moderation context only. | Treat TrustBadge as truth or run provider checks. |
| Healthcare access/readiness | Healthcare / Regulated Services | Audit records decision; hold may block action. | Decide PHI redaction/allow/block. |
| Job compliance | Job Compliance | Can request a hold/review; moderation may separately handle content/legal report. | Turn `ModerationCase` into job-compliance truth. |
| Dispute | Review / Dispute | May request/release hold; moderation may handle content reports separately. | Treat `ComplianceHold` as dispute lifecycle. |
| Consent | Consent & Disclosure | CL-09 may query proof where a legal/sensitive workflow requires it. | Treat consent proof as permission or compliance approval. |
| Track entitlement | Track Subscription & Entitlement | Operational failure/audit support only unless a workflow explicitly gates by entitlement. | Create local premium/entitlement booleans. |
| Sensitive access proof | Audit / Event Ledger | Primary generic access evidence owner. | Become the authorization policy owner. |
| Provider failure visibility | Observability / Ops | Primary generic operational visibility owner. | Replace provider-owner reconciliation or business state. |

### ComplianceHold composition rule

A source Module may request a hold when its own policy says review/blocking is required. A consuming Module may call `evaluateComplianceHold` as one input to its own action. Neither side may interpret hold reason alone as proof that the underlying condition currently exists.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### 16.1 Event principles

- Use `publishDomainEvent` with a transactional outbox for events that other Modules must reliably consume.
- The event name/payload belongs to the source Module; there is no single “CL09Event”.
- Exact event names are not supplied in current evidence. Coding agents must not establish a permanent event registry by convention alone.
- Recommended **event classes**, not binding names:
  - report submitted/triaged;
  - legal notice received/validated/actioned/counter-notice received/restored;
  - moderation case opened/assigned/closed;
  - moderation action recorded;
  - hold created/released/expired;
  - audit integrity anomaly detected;
  - integration failure recorded/recovered;
  - queue work stalled/dead-lettered;
  - ops incident opened/updated/resolved.

### 16.2 Transactional outbox

An authoritative source mutation and its required domain event/outbox entry must commit atomically where downstream effects are required. Do not publish first and then attempt the source write.

### 16.3 Queue responsibilities

Use `enqueueReliableJob` and the shared worker shell. CL-09 workers may include:

- moderation enforcement dispatch/reconciliation;
- legal-notice deadline scans when approved policy supplies `actionDueAt`;
- hold expiration when a valid expiry model exists;
- audit integrity verification if hash chaining is accepted;
- bounded audit evidence export generation if implemented;
- operational stalled-job/health/index-lag/provider-health monitors;
- admin projection refresh jobs where needed.

### 16.4 Retries and dead-letter handling

- `executeRetryWithBackoff` handles transient technical errors.
- Domain/provider owner classifies retryable versus terminal/manual-review failures.
- Every asynchronous command has an idempotency key or event inbox identity.
- Dead-lettered work must be visible through Observability and retain source references/correlation IDs.
- A retry must not create a second moderation action, second hold, duplicate notification meaning, or repeated downstream destructive effect.

### 16.5 Concurrency

Use database locks/optimistic concurrency for:

- competing moderation-case transitions/actions;
- duplicate hold requests and release/expiry races;
- incident transition races;
- enforcement step replay and restoration races.

### 16.6 Workflow/saga boundary

Moderation is the principal CL-09 multi-Module workflow owner. `orchestrateWorkflowSteps` may supply execution plumbing, but Content Moderation & Legal Notice owns which steps are required, the meaning of partial completion, restoration/compensation policy, and when a case can close.

A universal saga that owns moderation, privacy, booking, dispute, and hold policy is prohibited.

---

## 17. Provider Integrations

### 17.1 Direct CL-09 providers

| Owning Module | Provider-neutral port | Adapter/provider | Normalized result | Domain/ops effect |
| --- | --- | --- | --- | --- |
| Observability / Ops | Error monitoring port | Sentry (confirmed technology) | Safe provider event/reference | Exception visibility; optional `SystemEvent`/incident correlation. |
| Observability / Ops | Structured logging port | Provider not fixed in evidence | Structured safe log result | Operational diagnostics only. |
| Observability / Ops | Metrics port | Provider not fixed in evidence | Metric emission result | Operational health/alerts only. |
| Shared queue infrastructure / Observability telemetry | Queue runtime port | Provider/runtime not fixed in evidence | Claim/attempt/retry/dead-letter telemetry | Queue execution + `QueueJob` operational visibility if implemented. |

### 17.2 Indirect provider effects

Moderation may cause R2 public access revocation, Typesense de-indexing, notification delivery, video/download revocation, payment holds, or other provider-facing work, but it must do so through the **provider-owning Module**.

```text
Moderation decision
  -> target owner public command
  -> owner provider-neutral port
  -> owner provider adapter
  -> external provider
  -> verified / normalized result
  -> owner source transition
  -> moderation acknowledgment
  -> Observability failure on technical degradation
```

### 17.3 Webhook verification and dedupe

- The provider-owning Module owns webhook endpoint policy, signature algorithm, dedupe record, status translation, and reconciliation.
- Shared `verifyProviderWebhookSignature` and `deduplicateProviderEvent` mechanics may be reused, but `ProcessedStripeEvent`, `ProcessedCalendarEvent`, video/subscription/notification processed events remain separate truth.
- Observability may record a normalized failure but must not mark a provider event processed or recovered in the provider owner's dedupe table.

### 17.4 Status translation and reconciliation

Provider payload types must terminate at their adapter boundary. The owning Module translates them to domain/operational result types. `reconcileProviderState` remains owner-specific even when the worker framework is shared.

---

## 18. Search / Projection Boundaries

- Search / Public Visibility owns `SearchUpsertEvent`, Typesense adapters, projection execution, reconciliation, and query surfaces.
- Moderation owns the decision that a target should be hidden, removed, restored, or otherwise restricted; it calls `requestSearchProjectionRefresh`.
- The source Module continues to own the source projection. Search may compose owner-issued public-readiness decisions; it must not reconstruct moderation policy by scanning `ModerationCase` tables.
- Compliance holds may be one input to a source Module's public-readiness decision where that source policy says so. Search should consume a decision, not interpret raw hold reasons.
- Audit records and Observability records are not searchable-public-source records.
- Re-indexing/restoration must use current source truth and current moderation/privacy/readiness decisions; it must not simply “undo” a historical delete by replaying an old document.

---

## 19. Media / File Boundaries

### Contextual ownership

- A report/legal notice/moderation case owns the **meaning** of its evidence references.
- Media / File Access owns `MediaAsset`, validation, malware scanning, metadata scrubbing, quarantine, private storage, object deletion/revocation, generic access grants, and signed URLs.

### Moderation enforcement

- `freeze_content`, `remove_public_url`, `restore`, digital access disablement, and similar decisions are Moderation truth.
- File/object/public URL execution is Media truth and occurs through Media public commands/adapters.
- Permanent public links must not be introduced for protected evidence.

### Evidence preservation

**Proposed Ruling:** where legal/moderation evidence must survive source mutation, Content Moderation & Legal Notice should own an immutable evidence-snapshot proof record or equivalent immutable reference containing the source target/version, canonical hash, captured-at time, policy/version, MediaAsset/private-object reference, and retention classification. Media owns bytes/object mechanics; Audit owns generic access proof; neither absorbs the moderation/legal meaning.

Until accepted, do not pretend mutable `evidenceJson` or `statementJson` provides immutable snapshot proof.

### Sensitive file access

1. Role / Authority checks general viewer permission.
2. Moderation/Hold/context owner decides business/legal entitlement and redaction.
3. Media validates asset/grant/readiness and issues short-lived access.
4. Audit records `recordSensitiveAccess` with minimized context.

---

## 20. Privacy / Retention

### 20.1 Privacy orchestration rule

Privacy / Data Erasure owns:

- `PrivacyRequest` lifecycle;
- target enumeration orchestration;
- erasure job/target status;
- `DataRetentionExemption` truth;
- export-bundle orchestration and completion.

Each CL-09 Module must implement owner-local privacy contracts:

- `enumerateSubjectData`;
- `evaluateRetentionRequirement`;
- `executePrivacyInstruction`;
- owner-specific export serialization if requested.

### 20.2 Content Moderation & Legal Notice

- Enumerate reports, notices, cases, actions, and approved evidence-snapshot records linked to the subject.
- Legal/evidence retention may override erasure, but the exact duration/basis is **Unresolved** and must come from legal policy.
- Where retention is required, return the fact to Privacy so Privacy records an exemption; do not create a local `retainForever` flag.
- Anonymize nonessential personal fields where allowed while preserving required legal chain/evidence.

### 20.3 Admin Review / Compliance Hold

- Enumerate holds where subject is target, requester, releaser, or evidence subject as the eventual schema permits.
- Financial/fraud/security/legal proof may require retention; exact rules are **Unresolved**.
- Release history must not be silently deleted if required to explain a historic block.

### 20.4 Audit / Event Ledger

- Audit proof needed to prove security access or privacy fulfillment may require `security_audit` or `legal_obligation` retention treatment.
- The Privacy owner decides the request workflow; Audit returns what can be erased/anonymized versus retained.
- Avoid erasing the only proof that a privacy erasure occurred.
- Hash chains, if enabled, need a defined anonymization strategy because changing a row can invalidate integrity. This is unresolved until chain scope and retention rules are approved.

### 20.5 Observability / Ops

- Telemetry must minimize personal identifiers at ingestion.
- Privacy may instruct deletion/anonymization of persisted operational records and supported external-provider references.
- External logging/Sentry/metrics deletion capabilities are adapter concerns; their retention cannot substitute for Workin Ants policy.

### 20.6 Current privacy-target schema gap

The current `DataErasureTargetType` vocabulary does not provide specific CL-09 target types for reports, notices, cases, holds, audit records, or the claimed Observability records. **Unresolved:** either extend that vocabulary with stable CL-09 target types or approve a typed `other` convention. Coding agents must not choose inconsistent ad hoc strings.

---

## 21. Audit and Observability

These surfaces must remain separate.

| Surface | Owner | Purpose | Mutable? | Not a substitute for |
| --- | --- | --- | --- | --- |
| `AuditEvent` | Audit / Event Ledger | Generic actor/system action proof. | Insert-only requirement. | Domain event or operational failure truth. |
| `AccessAuditLog` | Audit / Event Ledger | Sensitive access/credential issuance/deny/redact/block proof. | Insert-only requirement. | Authorization policy or owner-specific access ledger. |
| Domain event ledgers | Domain owner | Lifecycle-specific history. | Usually append-style per owner. | Generic AuditEvent. |
| `SystemEvent` | Observability / Ops | Operational observation. | Lifecycle/mutability unresolved. | Business event or AuditEvent. |
| `IntegrationFailure` | Observability / Ops | Normalized technical failure/recovery visibility. | Lifecycle unresolved. | Provider dedupe or business failure state. |
| `QueueJob` | Observability / queue infra | Operational queue execution visibility. | Projection/lifecycle unresolved. | Domain job/workflow truth. |
| `OpsIncident` | Observability / Ops | Group correlated operational signals. | Incident lifecycle unresolved. | Moderation case or hold. |
| Structured logs / Sentry / metrics | Observability / Ops | Diagnostics/telemetry. | Provider-dependent. | Any Workin Ants source record. |

### Generic audit requirements

- All audit writes pass metadata sanitization.
- App/admin roles cannot update or delete sensitive access records.
- Restricted queries apply Role / Authority and field-level redaction.
- Sensitive reads of audit evidence may themselves require `recordSensitiveAccess`.
- Request/correlation IDs should link owner action, audit proof, job, and operational trace where schema supports it.

### Operational telemetry requirements

- One logger, Sentry adapter, metrics client, request-context mechanism, health registry, and generic integration-failure interface.
- Telemetry must include correlation/source references rather than copying domain payloads.
- Provider or queue failures must remain visible even when the user-facing workflow handles them gracefully.
- A technical failure that also changes business state requires **both** the business-domain record and operational evidence.

---

## 22. Security Boundaries

1. All CL-09 mutations validate input server-side with strict schemas.
2. UUID target references are not trusted merely because they parse; the target owner validates existence and permitted relationship.
3. Polymorphic target types use controlled vocabularies and owner resolvers; no arbitrary table-name lookup.
4. Public/controlled report and legal-notice intake is rate-limited and abuse-protected.
5. Report/legal evidence JSON is size-limited and allowlisted; binary evidence goes through Media rather than raw JSON/base64.
6. Audit and telemetry metadata are sanitized before storage and before third-party transmission.
7. Secrets, card data, raw PHI, SSNs, OTPs, raw biometrics, raw identity documents, full resumes, full private message bodies, and full contract/PDF content are prohibited in generic logs/metadata.
8. Sensitive audit/moderation/hold evidence queries require server-side authorization and owner-specific redaction.
9. Step-up assurance is applied where Identity/Security policy designates a CL-09 action as high risk.
10. `AuditEvent` and `AccessAuditLog` must have database-level insert-only protection for normal app/admin roles, not only service-layer conventions.
11. Hashes use `hashCanonicalPayload`; chain hashing uses `hashChainRecords` only after the proposed chain policy is accepted.
12. Encryption/hashing keys are managed by shared security infrastructure; they are never stored in Module source or telemetry.
13. Service-role actions cannot bypass Module state machines or target validation.
14. Async work is idempotent and replay-safe; destructive effects require owner-local idempotency.
15. Webhook authentication and replay protection remain with the provider-owning Module.
16. External provider credentials remain in the provider adapter boundary; Moderation never receives R2/Typesense/payment credentials merely to request an effect.
17. Admin exports use bounded scope, strict authorization, safe serialization, private delivery, and access audit.
18. Observability dimensions avoid high-cardinality personal identifiers unless a protected diagnostic need is explicitly approved.

---

## 23. Testing Architecture

### Module unit tests

**Content Moderation & Legal Notice**
- report/legal notice validation;
- target/action compatibility policy;
- report/case/notice transition guards;
- legal-policy version selection when established;
- moderation decision generation;
- restoration/counter-notice rules after approved policy;
- evidence-preservation requirements.

**Admin Review / Compliance Hold**
- reason/action applicability;
- create/evaluate/release transitions;
- semantic duplicate handling;
- release is not source approval;
- expiration policy if adopted;
- review escalation policy if modeled.

**Audit / Event Ledger**
- action/target validation;
- metadata allowlist/redaction;
- append-only repository behavior;
- sensitive action/sensitivity compatibility;
- restricted query redaction;
- hash/integrity functions if adopted.

**Observability / Ops**
- telemetry sanitization;
- failure normalization;
- incident grouping;
- queue telemetry state mapping;
- health-check timeout/failure behavior;
- provider adapter redaction.

### Public-interface contract tests

- Every CL-09 public command/query has a versioned DTO/response contract.
- Target owners must pass shared protocol tests for moderation execution and target validation.
- Hold consumers pass `evaluateComplianceHold` contract tests rather than reading hold tables.
- Audit callers verify required safe fields and prohibited payload rejection.
- Observability ingestion accepts normalized technical facts but rejects domain payload leakage.

### Lifecycle transition tests

- Assert allowed transitions and reject all unspecified transitions.
- Concurrency tests for double action, double hold creation, release/expiry race, stale case close, stale incident update.
- Transaction tests verify state + outbox/audit coupling where required.

### Cross-Module integration tests

At minimum:

1. Report -> case -> moderation action -> Search removal request -> Search acknowledgment.
2. Moderation action -> Media freeze/public URL removal -> evidence remains privately available to authorized reviewer.
3. Moderation action -> hold request -> downstream action blocked by `evaluateComplianceHold`.
4. Source compliance resolution -> hold release -> consumer proceeds without interpreting source state locally.
5. Sensitive moderation evidence read -> Media signed access -> `AccessAuditLog` created.
6. Provider/worker failure -> Observability failure/queue telemetry -> incident/alert path without altering business state.
7. Privacy request -> CL-09 enumeration -> retention decision -> erase/anonymize/retain result.

### Provider adapter tests

- Sentry/error adapter strips prohibited fields and preserves request correlation.
- Logging/metrics adapters enforce dimension/payload allowlists.
- Indirect provider integrations are tested in their owning Modules; CL-09 tests the public contract and failure acknowledgment, not raw provider payloads.

### Idempotency / concurrency tests

- repeated report submission with same idempotency key;
- repeated hold request/release;
- repeated moderation enforcement delivery;
- queue retry after partial target-owner execution;
- duplicate domain event consumption;
- stale transition conflict handling.

### Compliance/privacy tests

- evidence is preserved before destructive action where policy requires it;
- report vs legal notice remains distinct;
- hold does not overwrite underlying compliance truth;
- audit does not become domain ledger;
- sensitive access logs are insert-only;
- privacy erasure does not delete required legal/security proof without a Privacy-owned exemption;
- restricted evidence exports cannot expose prohibited payloads.

### Critical E2E flows

- user report to admin decision and public de-indexing;
- controlled legal notice to takedown, counter-notice, and restoration using approved policy fixtures;
- compliance hold creation -> blocked action -> release -> allowed action;
- admin audit/sensitive-access history review with redaction;
- provider/worker failure visible in ops view and correlated to request/source record.

---

## 24. Invariants

### Rules coding agents must never violate

1. CL-09 does not own a Cluster-level business lifecycle.
2. `Report`, `LegalNotice`, `ModerationCase`, and `ModerationAction` remain owned only by Content Moderation & Legal Notice.
3. `ComplianceHold` remains the single reusable platform stop sign.
4. A feature Module must not create `isBlocked`, `payoutBlocked`, `moderationHold`, `jobHold`, `contentHold`, or equivalent source-of-truth booleans instead of using the hold interface.
5. Hold release is not proof that KYC, tax, verification, healthcare, dispute, or moderation facts are approved.
6. A `ModerationAction` is not proof that Search/Media/Payment/Digital/Video/Messaging execution completed.
7. Moderation must never directly write another Module's business table.
8. Search projection work is requested through Search; CL-09 never writes Typesense or `SearchUpsertEvent` directly.
9. Media/object work is requested through Media; CL-09 never performs R2 business operations directly.
10. Notification delivery is always requested through Notification.
11. Provider dedupe records remain with provider-owning Modules.
12. `AuditEvent` does not replace a domain event ledger.
13. `AccessAuditLog` does not replace the data owner's access policy or owner-specific access ledger.
14. Observability records/logs/metrics do not replace business or compliance state.
15. `QueueJob` is operational visibility, never the authoritative domain job.
16. `OpsIncident` is not a `ComplianceHold` and cannot block business actions by itself.
17. `ModerationCase` is not an Order dispute, job-compliance check, or hold.
18. A casual `Report` is not a formal `LegalNotice`.
19. Accused content must not be destructively deleted before required evidence preservation and legal/admin workflow.
20. Mutable generic JSON must not be misrepresented as immutable legal evidence.
21. Polymorphic targets must be validated through owner interfaces; no arbitrary cross-domain repository.
22. Admin/service roles do not bypass owner authorization, state-machine, target-validation, privacy, or audit requirements.
23. All CL-09 mutations are idempotent where retries can occur.
24. All async CL-09 work is observable, correlated, and has bounded retry/dead-letter behavior.
25. Only lifecycle owners change lifecycle statuses.
26. Audit metadata and telemetry must exclude prohibited sensitive payloads.
27. Sensitive audit/access records are insert-only for normal app/admin roles.
28. Hash fields do not prove tamper-evidence unless canonical fields, chain scope, sequence, hash algorithm/version, and verification are implemented.
29. Privacy / Data Erasure alone owns `PrivacyRequest`, `DataErasureJob`, and `DataRetentionExemption` truth.
30. CL-09 owners execute privacy instructions only against records/providers they own.
31. A privacy erase request must not silently destroy retained legal/security proof.
32. Consent proof is never interpreted by CL-09 as permission logic unless the owning workflow explicitly says that proof is a precondition.
33. Track entitlement truth must never be copied into CL-09 premium/plan booleans.
34. Provider payload types cannot become CL-09 domain types.
35. Technical failure recovery cannot mark a provider event processed in another Module's dedupe table.
36. Legal deadlines, repeat-infringer policy, content-fingerprint thresholds, and retention periods must not be invented from general knowledge.
37. Proposed Shared Operations are not treated as confirmed until explicitly accepted.
38. Schema discrepancies identified in this document must be resolved explicitly, not normalized silently in code.

---

## 25. Prohibited Duplicate Implementations

Coding agents must not create any of the following inside CL-09 or its consumers when a canonical owner already exists:

- `requireAdmin.ts`, `isAdmin.ts`, `moderationAuth.ts`, `holdAdminAuth.ts`, or a second permission engine instead of `authorizeResourceAction`;
- CL-09-specific session/current-user helpers instead of `resolveAuthenticatedActor`;
- local MFA/OTP/passkey verification for sensitive admin actions instead of `requireStepUpForSensitiveAction`;
- `payoutHold`, `jobBlock`, `moderationBlock`, `contentHold`, `isBlocked`, or local hold tables instead of `ComplianceHold`;
- `moderationAudit.ts`, `holdAudit.ts`, `adminAuditLogger.ts`, generic `event_log` tables, or PHI/finance access logs instead of `appendAuditEvent` / `recordSensitiveAccess`;
- a generic audit table that absorbs `OrderEvent`, `BookingEvent`, `JobInterviewEvent`, `AgreementEvent`, `UserSecurityEvent`, or provider processed-event records;
- feature-local structured loggers or independent Sentry clients;
- generic `integration_failures` tables in Payment, Calendar, Media, Search, Notification, Video, Subscription, or Moderation instead of Observability's canonical interface once persistence is ruled;
- feature-local `queue_job` telemetry tables or queue dashboards that replace `recordQueueTelemetry`;
- local generic incident systems;
- direct Typesense clients/de-index workers in Moderation;
- direct Cloudflare R2 client calls for moderation evidence/freeze/public URL removal;
- direct SES/SMS/push delivery in Moderation/Hold/Ops;
- a universal `findTargetByTypeAndId` Prisma repository spanning all domains;
- a global processed-webhook table shared by Stripe, calendar, video, subscription, or notification;
- local privacy-request/retention-exemption tables in any CL-09 Module;
- duplicated hashing/canonicalization, retry/backoff, idempotency, locking, outbox, queue-runner, or request-context utilities;
- a generic review queue schema that merges Moderation, Hold, Job Compliance, Healthcare, and Verification review truth before `claimWorkItem`/review ownership is approved.

---

## 26. Deferred / Unresolved Decisions

| # | Question | Why unresolved | Missing/conflicting evidence | What it blocks |
| --- | --- | --- | --- | --- |
| U-01 | What is the correct Prisma DB mapping for `ModerationTargetType`? | Current enum maps to `"payout_transfers"`, inconsistent with its meaning. | No migration history or explicit intended map supplied. | Safe schema migration/DB enum verification. |
| U-02 | How should `ModerationActionType` effects target Order, payout, download grants, and video grants when those are absent from `ModerationTargetType`? | Action vocabulary exceeds target vocabulary. | No parent-target or child-grant targeting rule. | Durable moderation enforcement contract for these effects. |
| U-03 | Can one `ModerationCase` aggregate multiple reports, and how are they linked? | Current schema has one optional `reportId`. | No cardinality ruling/join model. | Multi-report case consolidation. |
| U-04 | What immutable record proves moderation evidence preservation? | `evidenceJson`/`statementJson` are mutable generic JSON; no snapshot record exists. | Snapshot ownership/storage/retention schema absent. | Strong DMCA/DSA evidence-preservation implementation. |
| U-05 | How is legal-notice validation decision/provenance/version stored? | Status fields exist, but no explicit validation result/policy version. | Legal requirements/policy versioning not supplied. | Auditable legal validation beyond simple status. |
| U-06 | What durable record tracks downstream moderation action execution/acknowledgments? | `ModerationAction` has no execution status. | `correlateEnforcementResult` is only proposed. | Reliable multi-owner enforcement/reconciliation. |
| U-07 | What is repeat-infringer truth? | Responsibility claimed; no schema or policy. | No source record, threshold, legal policy, or hold relationship. | Repeat-infringer automation/escalation. |
| U-08 | Is duplicate/piracy fingerprinting MVP, and who owns it? | Registry desire exists; canonical `computeContentFingerprint` unresolved. | Provider/algorithm/threshold/persistence/owner absent. | Proactive duplicate-content detection. |
| U-09 | Is legal correspondence a dedicated timeline, Messaging thread, or Notification-only delivery? | Current models do not capture replies/supplements as legal workflow history. | No correspondence ownership ruling. | Complete legal communication history. |
| U-10 | What typed target model/cardinality should `ComplianceHold` use? | Current direct FKs cover only User/Profile/Order; canonical interface expects typed target/action/scope. | Claimed target breadth exceeds schema. | General-purpose `request/evaluateComplianceHold`. |
| U-11 | What persistent review queue/claim/escalation model backs Hold review? | Manual review queues/escalation are claimed but absent. | `claimWorkItem` is proposed, no schema. | Concurrent reviewer claim/escalation workflow. |
| U-12 | What creation/source evidence belongs on `ComplianceHold`? | No creator, requester Module, source record, decision version, or idempotency field. | Registry claims admin release proof only; canonical command requires richer request. | Strong provenance/idempotency. |
| U-13 | What does hold `expired` mean and how is it proven? | Enum includes `expired`; model lacks `expiresAt` or expiry-condition reference. | No time/event/manual expiry policy. | Expiry worker and transition. |
| U-14 | What prevents semantically duplicate active holds? | No unique constraint/idempotency field. | Equivalence key not defined. | Safe concurrent hold creation. |
| U-15 | Which candidate/resume actions can a hold block and what target represents them? | Module listed as consumer but target mapping absent. | No candidate/application/resume hold rule. | Candidate/resume hold integration. |
| U-16 | Should `AuditEventType` and `AuditEventActor` exist? | Registry claims ownership; Prisma has strings/nullable user ID instead. | No migration or enum definitions. | Canonical audit vocabulary migration. |
| U-17 | How should canonical `appendAuditEvent` store request ID and outcome? | Shared Operations require them; current model does not. | No explicit fields or approved metadata convention. | Final audit command/schema contract. |
| U-18 | What is AccessAuditLog hash-chain scope/sequence/algorithm/version/anchoring? | Optional hash fields exist, but chain policy absent. | `hashChainRecords` only proposed. | Claiming tamper-evident chain compliance. |
| U-19 | Where do `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` persist? | Registry/glossary claim them; Prisma omits all. | External-vs-Postgres authority not ruled. | Observability repositories/admin queries. |
| U-20 | What are Observability statuses/severities/lifecycle transitions? | No enums supplied. | Models absent. | Incident/failure/queue lifecycle code. |
| U-21 | Which queue runtime/provider executes shared jobs? | Shared queue infrastructure is canonical, provider is unspecified. | No chosen runtime/storage. | Production queue adapter, not domain semantics. |
| U-22 | What incident grouping/alert thresholds are automatic vs manual? | Incident grouping is confirmed capability but thresholds absent. | No operational policy. | Automated incident opening/alerts. |
| U-23 | Which logging/metrics backend is authoritative for diagnostics? | Sentry is named for errors; logging/metrics providers are not. | No provider selection. | Production adapters only; interfaces can be built first. |
| U-24 | Which CL-09 records must be added to Privacy target vocabulary and how long are they retained? | Current `DataErasureTargetType` lacks CL-09-specific values; legal/security durations absent. | Privacy schema/policy gap. | Production privacy executor/retention behavior. |
| U-25 | What legal deadlines govern `LegalNotice.actionDueAt` and counter-notice restoration? | Field exists; legal timing policy not supplied. | Legal review required. | Production deadline worker. |

---

## 27. Architecture Decision Summary

### Binding confirmed rulings

1. CL-09 contains exactly four Deep Modules: Content Moderation & Legal Notice, Admin Review / Compliance Hold, Audit / Event Ledger, and Observability / Ops.
2. Each Module preserves its own source-of-truth records; the Cluster owns none.
3. `ComplianceHold` is the reusable platform stop sign. Feature-local competing block systems are prohibited.
4. Moderation owns legal/moderation decision truth; target owners execute their own state changes through public contracts.
5. `AuditEvent`/`AccessAuditLog` remain generic evidence; domain ledgers and provider-event ledgers remain separate.
6. Observability owns generic operational visibility; operational records never replace business status.
7. Search, Media, Notification, Privacy, Identity, Role / Authority, and Track Entitlement remain separate owners and are consumed through their public interfaces.
8. Canonical shared idempotency, outbox, queue, retry, locking, request-context, logging, audit, notification, search-refresh, privacy, and target-validation mechanisms must be reused rather than rebuilt.
9. `QueueJob` is operational visibility, not the authoritative workflow/job lifecycle.
10. Sensitive access is decided by the data/context owner and recorded by Audit.
11. Provider-specific verification, deduplication, translation, and reconciliation remain with provider-owning Modules.
12. Normal app/admin roles must not update/delete sensitive audit evidence.

### Proposed Rulings requiring explicit acceptance

**PR-CL09-01 — Moderation target resolver contract.** Adopt `resolveModerationTarget` as a typed registry contract with owner-supplied resolvers; prohibit a universal cross-domain repository.

**PR-CL09-02 — Moderation evidence snapshots.** Add an immutable Moderation-owned evidence proof/reference shape backed by Media and `hashCanonicalPayload`; Media owns bytes, Moderation owns legal meaning.

**PR-CL09-03 — Moderation enforcement correlation.** Add durable Moderation-owned run/step correlation for downstream acknowledgments, retries, failures, and restoration; target owners retain execution truth.

**PR-CL09-04 — ComplianceHold target representation.** Replace/augment current narrow target FKs with one validated typed target representation capable of the confirmed/claimed hold scope, with exactly one primary target per hold unless a later explicit multi-target rule is approved.

**PR-CL09-05 — Observability canonical persistence.** Persist the four registry/glossary-owned operational records in Workin Ants PostgreSQL/Prisma while treating Sentry/logging/metrics as secondary provider telemetry. Exact model/status designs still require approval before migration.

**PR-CL09-06 — Shared review claim mechanism.** Use `claimWorkItem` for claim/lease mechanics only after accepted; reviewer eligibility and review lifecycle remain with Moderation/Hold/other review owners.

**PR-CL09-07 — Audit hash chaining.** Use `hashChainRecords` only after an Audit-owned chain partition, canonical field set, sequence, algorithm/version, integrity verification, and privacy-retention policy are approved.

Until accepted, these proposals are not permission for a coding agent to invent a schema.

---

## 28. Coding-Agent Usage

Before changing CL-09, an implementation agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry / Architecture;
5. this Cluster `architecture.md`;
6. this Cluster `build-plan.md`;
7. the target Module `module-architecture.md`;
8. the target Module `implementation-plan.md`;
9. relevant dependency Module public-interface sections, especially Identity, Role / Authority, Search, Media, Notification, Privacy, Payment, Healthcare, Verification, Job Compliance, Messaging, Digital Goods, Video, and Track Entitlement as applicable;
10. the progress tracker and previous feature completion report.

The agent must then:

- verify that any Proposed Ruling required by the feature has been explicitly accepted;
- verify the previous numbered feature exit gate;
- inspect current Prisma/migrations before changing schema;
- refuse to resolve an Unresolved Decision by coding convention alone;
- implement only the owning Module's truth and the approved public contracts;
- reuse canonical shared operations rather than creating feature-local equivalents;
- update this architecture only when a binding architecture decision actually changes.
