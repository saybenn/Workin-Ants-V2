# Identity, Authority, Consent & Entitlements Architecture

> **Cluster ID:** `CL-01`  
> **Cluster name:** Identity, Authority, Consent & Entitlements  
> **Cluster type:** `foundation_access_control_consent_entitlement_policy`  
> **Repository target:** `context/clusters/identity, authority, & consent/identity-authority-consent-architecture.md`\
> **Document status:** Target MVP Cluster architecture. Confirmed facts, Proposed Rulings, and Unresolved Decisions are labeled.  
> **Audience:** coding agents, developers, reviewers, maintainers, security/compliance reviewers, and architects  
> **Update rule:** update this file whenever a binding ownership, lifecycle, public-interface, provider, security, privacy, consent, entitlement, or cross-Cluster decision changes. Build progress must not silently redefine architecture.

---

## 1. Document Status and Scope

CL-01 coordinates five Deep Modules:

1. `identity_access` — Identity & Access
2. `role_authority` — Role / Authority
3. `consent_disclosure` — Consent & Disclosure
4. `customer_buyer_profile` — Customer / Buyer Profile
5. `track_subscription_entitlement` — Track Subscription & Entitlement

It answers related but different questions:

```text
Who is the account actor?
→ Which actor/profile/organization context is being used?
→ May that actor attempt this resource action?
→ What exact consent/disclosure proof exists?
→ What commercial entitlement, quota, waiver, boost, commission, priority, or perk applies?
```

A Cluster is a planning, integration, and controlled-context boundary. **It does not own a lifecycle.** Do not create a CL-01 aggregate, generic access state, generic policy ledger, or all-purpose `authService` that becomes source truth above its Modules.

This file is subordinate to root Workin Ants architecture and code standards. Prisma remains executable schema evidence; this file explains semantic ownership and integration constraints Prisma cannot express. Target Module architecture remains authoritative for Module-internal behavior unless a confirmed higher-level ruling explicitly constrains it.

Evidence labels:

- **Confirmed** — established by the current Project Overview, Cluster Registry v2.3, Deep Module Registry, Prisma, Ubiquitous Language/Compliance Inventory, Module extracts, or Canonical Shared Operations.
- **Reasonable inference** — necessary/strongly implied, but not yet a binding lifecycle/schema decision.
- **Proposed Ruling** — architecture choice needed where sources conflict or are incomplete.
- **Unresolved Decision** — no safe final answer; dependent production behavior stays fail-closed or disabled.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

Establish trusted User identity, account-security proof, server-side authority, buyer actor identity, durable consent/disclosure proof, and track-based commercial entitlement policy before marketplace, hiring, delivery, discovery, financial, or administrative workflows rely on them.

### Goal

Every protected workflow should obtain typed, source-owned answers to:

```text
Who is acting?
Under which User / CustomerProfile / CandidateProfile / ProfessionalProfile / Organization context?
May this actor attempt this action?
Has the exact required disclosure/version been accepted?
What current commercial policy applies?
What evidence supports each answer?
```

without recreating identity, permission, consent, buyer identity, subscription, or entitlement truth.

### Inputs

- age-gate declarations and minimized request evidence;
- verified provider sessions/system credentials;
- OAuth/provider identity references;
- passkey/WebAuthn and OTP results;
- recovery provider evidence;
- action/resource identifiers;
- platform roles from Identity;
- organization membership facts from Organization Hiring;
- thread participant facts from Messaging;
- owner/participant facts from resource Modules;
- consent type/version/presentation reference;
- plan/price/entitlement configuration;
- verified Stripe Billing events;
- customer/candidate/professional actor-track context;
- entitlement resolution/metering requests;
- ComplianceHold decisions;
- Privacy-owned target instructions;
- authorized admin/system commands.

### Outputs

- authenticated actor context;
- provisioned User/security posture;
- safe auth-method/passkey state;
- step-up and temporary sensitive-action proof;
- recovery state/security history;
- authority decisions;
- CustomerProfile buyer context;
- ConsentLog proof;
- effective consent version/presentation after that model is approved;
- Track plan/subscription/grant/usage truth;
- effective entitlement decisions and usage receipts;
- owner domain events/outbox effects;
- requests to Audit, Notification, Search, Privacy, Hold, or Ops through public contracts.

### Transformation

```text
anonymous/external person
→ age/account gate
→ User + security posture
→ actor/profile resolution
→ resource authority decision
→ required consent/entitlement gates
→ downstream action owner receives decision/evidence
```

### Explicit non-ownership

CL-01 does not own Professional eligibility; verification; healthcare readiness; Gig, Job, Application, Interview, Order, Booking, Review, or Dispute lifecycles; general payment/payout/tax truth; PrivacyRequest orchestration; ComplianceHold lifecycle; MediaAsset mechanics; Search execution; Notification delivery; generic AuditEvent/AccessAuditLog; Ops incident truth; or digital/video/file access-grant lifecycles.

---

## 3. Module Inventory

| Module | Type | Purpose | Owned truth | CL-01 responsibility | Major inbound dependencies | Major outbound consumers |
|---|---|---|---|---|---|---|
| `identity_access` — Identity & Access | `capability_security` | Establish account identity/security proof | `User`; structural `UserRole`/`PlatformRole`; age-gate; security profile; provider links; passkeys; step-up; sensitive sessions; recovery; security events | Authenticate and resolve actor; protect sensitive actions | Supabase Auth/OAuth, WebAuthn, OTP, recovery provider, Role/Consent/Hold/Audit/Privacy/Ops | all protected Modules |
| `role_authority` — Role / Authority | `capability_security` | Interpret authority facts | action vocabulary, authorization policy/decision contracts, route/RLS semantics | Decide whether actor may attempt a named action | Identity roles/context; owner facts from Organization Hiring, Messaging, resource owners | all protected business/admin Modules |
| `consent_disclosure` — Consent & Disclosure | `compliance` | Preserve versioned acceptance proof | `ConsentLog`, `ConsentType`; proof interfaces; version/presentation capability | Record/query exact proof; present standalone disclosures | Identity, Role, version catalog, Audit/Privacy/Notification | security, screening, calendar, agreements, subscriptions, healthcare, notifications, prizes/rewards |
| `customer_buyer_profile` — Customer / Buyer Profile | `domain_actor_profile` | Maintain buyer identity branch | `CustomerProfile`; provisioning; buyer resolution; CustomerProfile transition policy | Supply customer commercial actor | Identity, Role, Media, Privacy/Hold, downstream obligation facts | Gig, Order, Booking, Digital Goods, Review/Dispute, Track |
| `track_subscription_entitlement` — Track Subscription & Entitlement | `commercial_policy_capability` | Own account-track commercial policy | Track plans/prices/definitions/mappings; subscriptions; grants; usage events/counters; subscription events | Single commercial policy rail for customer/candidate/professional | Identity/profile owners, Role, Consent/Hold, Stripe Billing, Audit/Ops/Privacy/Notification | Search, Professional, Marketplace, Order, Booking, Candidate, Video, Digital Goods |

```text
Identity proves who the actor is.
Role decides what that actor may attempt.
Customer identifies the buyer actor branch.
Consent proves what exact version was accepted.
Track decides current commercial access/perks/limits.
The downstream owner still owns the business action.
```

---

## 4. Cluster Architecture Principles

1. One owner per lifecycle.
2. Authentication and authorization remain separate.
3. Authorization is not consent, entitlement, compliance readiness, payment, healthcare clearance, or hold clearance.
4. `User` is account identity, not every actor identity.
5. `CustomerProfile` is buyer actor truth.
6. Organization membership and thread participation remain with their domain owners; Role interprets them.
7. Consent is proof, not permission.
8. Track is the only current commercial entitlement owner.
9. No local premium, fee-waiver, commission, quota, boost, or priority truth.
10. Consumer Modules own historical snapshots of Track decisions.
11. `TrackUsageEvent` is immutable usage proof; `TrackUsageCounter` is rebuildable projection.
12. Provider state is an input, not Workin Ants domain truth.
13. Provider webhook verification/dedupe may share mechanics while provider-owning Modules retain event truth.
14. `ComplianceHold` is the reusable stop sign.
15. Module status must not become a competing universal hold.
16. Privacy owns orchestration; data owners execute.
17. Media owns file mechanics; contextual Modules own business meaning.
18. Search is projection only.
19. Audit does not replace domain event/history truth.
20. Observability does not replace business lifecycle truth.
21. Canonical Shared Operations are reused, not locally reimplemented.
22. Direct cross-Module Prisma access is not the default.
23. Shared response contracts do not imply shared policy.
24. Temporary grants may share technical mechanics while remaining distinct domain records.
25. Domain ledgers may share append-only mechanics while retaining separate lifecycle meaning.
26. Client flags, redirects, browser permission state, or provider dashboards never establish source truth.
27. High-risk unresolved behavior fails closed.

---

## 5. Runtime / Collaboration Topology

### Protected synchronous request

```text
caller
→ validation/request context
→ Identity.resolveAuthenticatedActor
→ action owner obtains minimum owner facts
→ Role.authorizeResourceAction
→ action owner composes required gates:
     Consent.queryConsentProof
     Track.resolveEntitlement / consumeMeteredEntitlement
     Hold.evaluateComplianceHold
     other readiness owners
→ action owner performs authoritative operation
→ owner records domain history/outbox
→ Audit / Notification / Search / Ops effects
```

Actor resolution is not authorization; authorization is not consent; consent is not entitlement; entitlement is not the business transition.

### Owner-fact pattern

```text
resource owner
→ owner-specific queryOwnerFacts DTO
→ Role policy
→ typed decision
```

Role must not become a universal cross-domain repository.

### Provider callback pattern

```text
raw callback
→ verifyProviderWebhookSignature
→ owner adapter
→ deduplicateProviderEvent (shared mechanism + owner-specific truth)
→ translateProviderStatus
→ owner aggregate lock/idempotency
→ owner lifecycle transition
→ domain ledger/outbox
→ consumers
```

Raw provider events are not domain events.

---

## 6. Folder / Code Organization

Logical organization; exact root prefix follows root code standards:

```text
<application-root>/
  modules/
    identity-access/
      application/ domain/ contracts/
      infrastructure/auth-providers/
      infrastructure/passkeys/
      infrastructure/otp/
      infrastructure/recovery-verification/
      workers/ tests/

    role-authority/
      application/ domain/policies/ domain/action-vocabulary/
      contracts/ infrastructure/rls-policy-bindings/ tests/

    consent-disclosure/
      application/ domain/ contracts/ infrastructure/ tests/

    customer-buyer-profile/
      application/ domain/ contracts/ workers/ tests/

    track-subscription-entitlement/
      application/ domain/ contracts/
      infrastructure/billing/
      workers/ tests/

  platform/
    request-context/ idempotency/ events/ queue/ crypto/
    provider-webhooks/ observability/

  contracts/
    decision-envelope/ event-envelope/ privacy-target/ provider-result/
```

Rules:

- Module repositories own only their own lifecycle records.
- Cross-Module facts travel through public contracts/minimal DTOs.
- Shared code must correspond to a canonical Shared Operation or genuine root platform primitive.
- Provider adapters live with the Module whose domain transition they affect; low-level webhook security/retry may be shared.
- Do not create generic `shared/auth`, `shared/permissions`, `shared/consent`, `shared/premium`, or `shared/subscriptions` as alternate owners.

**Proposed Ruling PR-CL01-01:** preserve the five Deep Module directories; no generic CL-01 domain service/repository.

---

## 7. System and Module Boundaries

| Area | Owns | May consume | Must not own |
|---|---|---|---|
| Identity | User/auth/security/passkey/step-up/recovery truth | Consent proof, Role/Hold decisions, Audit/Notification/Privacy/Ops | permission interpretation, org membership, Track, payment/KYC/tax, generic audit |
| Role | authorization policy/action vocabulary/decision/RLS semantics | Identity roles/context, owner facts | auth, `UserRole` lifecycle, org/thread lifecycles, readiness, Track, Hold/Audit |
| Consent | `ConsentLog`, `ConsentType`, generic versioned acceptance proof | Identity/Role, version catalog, Privacy/Audit/Notification | provider connection, browser permission, Agreement/Verification/Subscription/Privacy lifecycles |
| Customer | `CustomerProfile`, buyer identity/provisioning/local transitions | User, Role, Track decisions, Media validation, obligation facts, Privacy/Hold | auth, Gigs/Orders/Bookings/Reviews/Disputes, Track truth, file mechanics, search execution |
| Track | catalog/subscription/grant/usage truth | actor profiles, Role, Consent/Hold, billing adapter, support rails | Order/Booking/Application lifecycle, general finance, Search index, delivery grants, PrivacyRequest/Hold |
| Organization Hiring | OrganizationMember/OrganizationRole lifecycle under PR-CL01-02 | Role decisions | Role policy |
| Messaging | ThreadParticipant lifecycle under PR-CL01-02 | Role decisions | global authorization policy |
| Privacy | request/job/target/exemption/export orchestration | CL-01 owner executors | uncontrolled direct rewrites of owner tables |
| Hold | ComplianceHold lifecycle | CL-01 target facts | CL-01 source lifecycles |
| Audit | AuditEvent/AccessAuditLog | safe CL-01 metadata | security/consent/subscription/usage truth |
| Ops | IntegrationFailure/SystemEvent/QueueJob/OpsIncident | safe operational context | CL-01 business statuses |
| Search | SearchUpsertEvent/index/reconciliation | Track boost/source-safe projections | Track/customer truth |
| Media | MediaAsset/upload/scan/storage/signed access | Customer attachment context | CustomerProfile lifecycle |

### Role ownership conflict

The Deep Module Registry historically assigns `OrganizationMember`, `OrganizationRole`, and `ThreadParticipant` to Role. The Ubiquitous Language and adjacent Modules assign membership to Organization Hiring and thread participation to Messaging.

**Confirmed Ruling PR-CL01-02 (WA-R001, 2026-09-29):** Organization Hiring owns OrganizationMember/OrganizationRole lifecycle; Messaging owns ThreadParticipant lifecycle; Role owns permission interpretation only. Role consumes owner facts and must never mutate these foreign lifecycles. SH-003 remains a proposed generic shape; concrete owner queries do not wait for its adoption.

---

## 8. Data Ownership

### Identity-owned

`User`, `UserRole`, `PlatformRole`, `AgeGateAttempt`, `AgeGateResult`, `AgeGateBlock`, `AuthProviderType`, `AuthCredentialStatus`, `UserSecurityTier`, `StepUpActionType`, `StepUpChallengeType`, `StepUpChallengeStatus`, `StepUpFailureReason`, `AccountRecoveryStatus`, `AccountRecoveryReason`, `AccountRecoveryIdentityProvider`, `SecurityEventType`, `UserSecurityProfile`, `AuthProviderAccount`, `PasskeyCredential`, `StepUpChallenge`, `SensitiveActionSession`, `AccountRecoveryRequest`, `UserSecurityEvent`.

`UserRole`/`PlatformRole` are structurally Identity-owned; Role interprets them. `UserSecurityEvent` is domain security history, not generic audit.

### Role-owned

Role has no clean foreign lifecycle schema that should be made authoritative. Its durable meaning is policy/action vocabulary plus server/RLS enforcement. Do not invent configurable RBAC tables without an explicit requirement.

### Consent-owned

`ConsentLog`, `ConsentType`, exact acceptance proof. A persisted active version/content model is missing and unresolved. Contextual records such as `VerificationConsent`, `AgreementElectronicConsent`, BAA, Calendar connection state, Notification subscription, and Track subscription remain with their owners.

Current `ConsentLog.user` uses `onDelete: Cascade`; this conflicts with possible retention of consent proof and must be resolved before destructive privacy operations.

### Customer-owned

`CustomerProfile` and its buyer actor lifecycle. Customer uses `ProfileStatus`, but glossary ownership is conflicted. Customer owns its transition policy; exclusive enum ownership is unresolved.

`avatarMediaId` is a contextual reference only; Media owns file truth.

**Proposed Ruling PR-CL01-03:** Customer owns CustomerProfile transition policy even if `ProfileStatus` remains a shared controlled vocabulary.

### Track-owned

`TrackPlan`, `TrackPlanPrice`, `TrackEntitlementDefinition`, `TrackPlanEntitlement`, `TrackSubscription`, `TrackEntitlementGrant`, `TrackUsageEvent`, `TrackUsageCounter`, `TrackSubscriptionEvent`; plus `AccountTrack`, `TrackPlanStatus`, `TrackBillingModel`, `TrackBillingProvider`, `TrackSubscriptionStatus`, `TrackEntitlementValueType`, `TrackEntitlementGrantStatus`, `TrackUsageEventType`, `TrackUsagePeriod`.

Important schema gaps:

- `TrackSubscriptionEvent.providerEventId` is indexed, not unique, so it is not sufficient dedupe truth by itself.
- exactly-one matching profile for a subscription/grant is not fully enforced.
- active-subscription uniqueness is not fully established.
- typed entitlement value fields are not visibly constrained to the selected value type.
- current counter uniqueness may not distinguish all overlapping grant/subscription cases.

### Not owned by CL-01

`ComplianceHold`; Privacy request/job/target/exemption/export records; `AuditEvent`; `AccessAuditLog`; Ops records; `SearchUpsertEvent`; Media records; general Payment/Payout/Tax `ProcessedStripeEvent`.

---

## 9. Lifecycle Ownership

| Lifecycle | Owner | States | Transition authority | Must not be confused with |
|---|---|---|---|---|
| age gate/block | Identity | allowed/blocked/manual review + block expiry | Identity | User status / ComplianceHold |
| auth provider link | Identity | active/disabled/revoked/expired/compromised | Identity | provider dashboard |
| passkey | Identity | register/use/revoke metadata | Identity | raw biometrics |
| step-up challenge | Identity | pending/verified/failed/expired/cancelled/locked | Identity | authorization/business entitlement |
| sensitive action session | Identity | valid/expired/revoked by scope | Identity | file/video/Track grant |
| account recovery | Identity | initiated through completed/failed/manual-review states | Identity | KYC/screening |
| UserRole attachment | Identity | row attachment; full history unresolved | Identity/admin policy | OrganizationRole |
| authorization decision | Role | stateless decision | Role policy | business lifecycle |
| consent acceptance | Consent | append acceptance proof | Consent | downstream status |
| consent version publication | Consent capability | unresolved persistence/status | Consent after ruling | contextual consent lifecycle |
| CustomerProfile | Customer | draft/active/paused/suspended/archived | Customer under approved matrix | User status / universal hold |
| Track plan | Track | draft/active/retired/archived | Track | subscription |
| Track subscription | Track | active/trialing/past_due/cancelled/expired/paused/incomplete/incomplete_expired | Track | Stripe object |
| Track grant | Track | active/expired/revoked/suspended/consumed | Track | delivery grant |
| Track usage event | Track | immutable | Track usage service | source business event |
| Track usage counter | Track | derived | Track projection worker | usage proof |
| Track subscription event | Track | append-only | Track transition service | provider dedupe/audit |

---

## 10. Public Module Interfaces

| Interface | Owner | Purpose | Minimum input | Minimum output | Returns | Consumers must not recreate |
|---|---|---|---|---|---|---|
| SH-001 `resolveAuthenticatedActor` | Identity | map trusted session/system credential to actor | session/request credential | user/context/assurance | truth/context | local current-user logic |
| `provisionUserAfterAgeGate` | Identity | idempotent User/provider provisioning | age decision + provider identity | User/provider mapping | truth | bypass age gate |
| `getUserSecurityPosture` | Identity | safe security readiness summary | actor/target | tier/method/lock summary | truth/projection | raw credential truth |
| passkey commands | Identity | register/use/list/revoke passkeys | actor + verified ceremony | credential result/ref | truth/evidence | biometrics |
| SH-014 `requireStepUpForSensitiveAction` | Identity | action-scoped recent stronger auth | actor/action/target | allowed/challenge/session evidence | decision/evidence | business permission |
| recovery commands/query | Identity | own recovery workflow | request/provider result | recovery state | truth | KYC/screening |
| SH-002 `authorizeResourceAction` | Role | action/resource authority | actor/action/owner facts | decision/reasons | decision | consent/entitlement/readiness |
| owner-specific SH-003 `queryOwnerFacts` (Proposed ruling) | each source owner | supply relationship facts | resource/purpose | minimal DTO | truth | foreign repository |
| SH-007 `recordConsentProof` | Consent | persist exact acceptance | user/type/version/evidence | proof ID/ref | evidence | permission |
| SH-008 `queryConsentProof` | Consent | query exact required version | user/type/version | accepted + proof ref | evidence | active version logic |
| SH-009 `resolveActiveConsentVersion` | Consent | resolve current version/config | type/context | version/hash/effective metadata | policy/config | “latest log” inference |
| SH-010 `presentStandaloneConsent` | Consent | return required disclosure | type/context | renderable version | config/projection | provider state |
| SH-004 `resolveCustomerActor` | Customer | resolve User→CustomerProfile | User | profile ID/status | truth | buyer from User fields |
| `provisionDefaultCustomerProfile` | Customer | ensure one profile | eligible User | profile result | truth | direct Identity insert |
| Customer profile commands/query | Customer | read/update/status | actor/profile/patch | profile/result | truth | file/search/commerce lifecycles |
| SH-005 `resolveEntitlement` | Track | current typed commercial policy | track/profile/key/context | value/reason/source/evidence | decision/truth | local premium switch |
| SH-006 `consumeMeteredEntitlement` | Track | atomic quota + usage proof | entitlement/quantity/idempotency target | permit/deny + usage receipt | decision/evidence | local counter |
| Track catalog/subscription queries | Track | current plan/subscription state | user/profile/track | provider-neutral DTO | truth | Stripe object |
| Track subscription commands | Track | start/change/cancel | actor/plan/proof refs | initiation/result | command result | success redirect = active |
| `quoteOrderTrackPolicy` | Track | fee/commission current policy | buyer/professional/order context | typed policy/evidence | decision | Order mutation/current-plan recalculation |

---

## 11. Canonical Shared Operations Used by This Cluster

`context/shared/shared-operations.md` provides the permanent SH IDs, canonical names, owners, and statuses used below. References preserve those registry boundaries; citing a Proposed ruling does not approve it. Shared contracts and mechanisms do not transfer Module truth.

| Operation | Meaning | Canonical owner/class | CL-01 use | Local policy stays with | Must not be rebuilt as |
|---|---|---|---|---|---|
| SH-001 `resolveAuthenticatedActor` | trusted session→actor | Identity / platform capability | protected entry | Identity mapping/assurance | current-user helpers |
| SH-002 `authorizeResourceAction` | resource/action permission | Role / cross-cutting | all protected actions | Role action policy + owner facts | isAdmin/isOwner/org/thread helpers |
| SH-003 `queryOwnerFacts` (Proposed ruling) | minimum relationship facts | each source owner / shared contract, separate implementations | Role reads | source owner | universal repository |
| SH-004 `resolveCustomerActor` | User→buyer profile | Customer public interface | customer workflows | Customer status/access | buyer-from-User logic |
| SH-007 `recordConsentProof` | exact acceptance evidence | Consent | acceptance | Consent version policy | per-feature consent store |
| SH-008 `queryConsentProof` | exact proof lookup | Consent | consent gates | Consent | local consent query |
| SH-009 `resolveActiveConsentVersion` | effective version/config | Consent | presentation | Consent context rules | latest-log inference |
| SH-010 `presentStandaloneConsent` | standalone disclosure | Consent | security/screening/calendar/Track | Consent wording/version | buried feature terms |
| SH-005 `resolveEntitlement` | typed commercial policy | Track | current perks/waivers/boosts | Track precedence | isPremium |
| SH-006 `consumeMeteredEntitlement` | atomic quota + usage proof | Track | application/usage limits | Track period/counting | local counter |
| SH-014 `requireStepUpForSensitiveAction` | scoped stronger auth | Identity | sensitive actions | Identity assurance matrix | payout/admin OTP service |
| SH-011 `evaluateComplianceHold` | stop-sign decision | Hold owner | hold-sensitive CL-01 actions | Hold + target policy | local blocked flags |
| SH-029 `appendAuditEvent` | generic action audit | Audit | material admin/security actions | audit selection/safe metadata | CL-01 audit table |
| SH-030 `recordSensitiveAccess` | sensitive-access proof | Audit | sensitive reads | access policy | local access log |
| SH-031 `appendDomainLifecycleEvent` | shared append mechanics | shared mechanism, owner truth | Identity/Track/Customer domain history | domain owner | generic event truth |
| SH-044 `executeIdempotentCommand` | semantic replay safety | platform | provisioning/consent/metering/provider commands | caller key/result | local idempotency subsystem |
| SH-047 `enqueueReliableJob` | durable background work | platform | expiry/backfill/reconciliation/privacy | owner job payload | custom job truth |
| SH-048 `executeRetryWithBackoff` | retry + dead letter | platform/Ops | workers/providers | owner failure classification | ad-hoc retry loops |
| SH-059 `verifyProviderWebhookSignature` | authenticate callback | shared provider security | recovery/Stripe Billing | provider adapter config | custom route verifier |
| SH-060 `deduplicateProviderEvent` | prevent repeat side effects | shared mechanism, owner event truth | recovery/Billing | owner event identity | one global provider truth |
| SH-061 `translateProviderStatus` | provider→domain input | owner adapter/shared pattern | Identity/Track | lifecycle owner | scattered provider enums |
| SH-037 `recordIntegrationFailure` | operational failure proof | Ops | provider/worker failures | safe owner context | domain failure status |
| SH-076 `normalizeAndHashIdentifier` | stable nonplaintext comparison | crypto primitive | age/rate/recovery evidence | owner normalization/retention | local hash |
| SH-074 `generateSecureToken` | purpose-bound secure secret | security primitive | recovery/security when needed | owner TTL/binding | token helper |
| SH-078 `minimizeAndRedactProviderInput` | minimum provider payload | source policy + shared serializer | identity provider calls | Identity sensitivity policy | raw User object export |
| SH-096 `enumerateSubjectData` | owner subject inventory | each owner via Privacy | Identity/Consent/Customer/Track | owner schema meaning | Privacy direct table crawl |
| SH-095 `executePrivacyInstruction` | owner erase/export/etc | Privacy orchestrates; owner executes | CL-01 executors | owner invariants | local PrivacyRequest |
| SH-097 `evaluateRetentionRequirement` | owner retention facts | owner + Privacy | destructive privacy prep | owner legal facts | local exemption workflow |
| SH-098 `anonymizePersonalFields` | field pseudonymization | shared primitive + owner map | privacy execution | owner fields/invariants | global crawler |
| SH-041 `requestNotification` | semantic delivery request | Notification | security/profile/subscription notices | source business trigger | direct email/SMS/push client |

SH-003 `queryOwnerFacts` (Proposed ruling) is shared contract/separate policy. Webhook verification/dedupe is shared mechanism/separate truth. Decision envelopes may be shared response contracts but never share policy.

---

## 12. Cross-Module Data Flows

### Account creation

```text
signup
→ Identity age gate
→ AgeGateAttempt / optional AgeGateBlock
→ verified auth provider result
→ idempotent User + AuthProviderAccount + UserSecurityProfile
→ Identity event/outbox
→ Customer default-profile provisioning
```

### Protected action

```text
actor resolution
→ owner facts
→ Role decision
→ action-owner consent/entitlement/hold/readiness composition
→ authoritative action-owner write
→ owner domain event/outbox
→ support effects
```

### Step-up

```text
authorized sensitive attempt
→ Identity step-up requirement
→ challenge
→ verified OTP/passkey result
→ StepUpChallenge transition
→ action/target/expiry-bound SensitiveActionSession
→ original action re-attempt
```

### Recovery

```text
AccountRecoveryRequest
→ required recovery disclosure proof
→ email/provider verification
→ verified normalized result
→ recovery transition/manual review
→ phone/security profile update
→ security event + notification/audit/ops
```

### Customer provisioning

```text
User provisioned
→ Customer idempotent provisioning
→ CustomerProfile
→ resolveCustomerActor
→ downstream consumers store/use customerProfileId after approved cutover
```

### Consent

```text
resolve active version
→ present standalone disclosure where required
→ explicit acceptance
→ recordConsentProof
→ ConsentLog
→ consumer continues only after its own remaining gates
```

### Entitlement

```text
consumer action
→ actor/authority/hold/readiness
→ Track.resolveEntitlement
→ current typed policy/evidence
→ consumer performs/denies its own action
→ consumer snapshots only historical decision if needed
```

### Metered entitlement

```text
consumer determines business event counts
→ consumeMeteredEntitlement
→ DB lock/transaction
→ resolve grant/period
→ capacity check
→ immutable TrackUsageEvent
→ TrackUsageCounter update
→ usage receipt
```

### Paid Billing callback

```text
Stripe callback
→ signature verification
→ Track Billing adapter
→ shared dedupe + Track-specific receipt truth
→ status translation
→ TrackSubscription lock/transition
→ grant materialization/suspension/revocation
→ TrackSubscriptionEvent + outbox
→ Search/Notification/Audit/Ops effects
```

**Proposed Ruling PR-CL01-04:** Track owns Stripe Billing subscription adapter/status translation; Payment/Payout/Tax keeps general financial/Order payment/payout/tax truth.

### Customer avatar

```text
Customer authorized update
→ Media attachment validation
→ Customer avatar reference write
→ Media handles signed/public access
```

### Privacy

```text
Privacy request/job/target
→ owner enumerateSubjectData
→ owner retention facts
→ Privacy exemption/order
→ owner executePrivacyInstruction
→ Privacy records target/job result
```

---

## 13. Cross-Cluster Bridges

| Source | Destination | Transfer | Authoritative owner | Interface | Forbidden coupling |
|---|---|---|---|---|---|
| Identity | all clusters | actor/security assurance | Identity | actor/step-up | feature-local auth |
| Role | all protected clusters | permission decision | Role | authorization | local role interpretation |
| CL-06 Org Hiring | Role | membership facts | Org Hiring | owner facts | Role mutation |
| CL-07 Messaging | Role | participant facts | Messaging | owner facts | Role mutation |
| Customer | CL-04 | buyer actor | Customer identity; destination lifecycle | customer actor | Customer owning Order/Gig/etc |
| Customer | CL-05 | buyer actor | Customer | customer actor | Customer owning Booking/delivery |
| Track | CL-02 | boost policy | Track; Search projection | entitlement event/refresh | Track writing Typesense |
| Track | CL-03 | selling/commission/etc policy | Track; Professional/Marketplace action | entitlement query | Track owning profile/offering |
| Track | CL-04 | fee waiver/commission | Track current; Order historical snapshot | order policy quote | Track mutating Order |
| Track | CL-05 | priority/live/delivery commercial permission | Track; delivery owners own grants | entitlement query | Track owning Booking/video/download grants |
| Track | CL-06 | application quota/boost/view tracking | Track | resolve/consume | candidate module local quota |
| Privacy CL-08 | CL-01 owners | privacy instruction | Privacy workflow; owner data | privacy protocol | direct uncontrolled SQL |
| Audit/Hold/Ops CL-09 | CL-01 | support decisions/evidence | respective owner | public contracts | support records replacing domain truth |
| Consent | many clusters | exact proof | Consent | consent query | consumer generic proof store |

---

## 14. Authentication and Authorization

All protected operations begin with SH-001 `resolveAuthenticatedActor` unless explicitly anonymous (age gate/auth entry/verified provider callback).

`UserRole`/`PlatformRole` are structurally Identity-owned; Role interprets them. Admin/support never imply unrestricted access to PHI, tax, resumes, agreements, private messages, or financial records.

Role policies distinguish platform, organization, participant/thread, resource-owner, and support/admin scopes. Resource owners provide relationship facts.

Identity owns step-up. A timestamp summary such as “last stepped up” must not replace action/target-scoped proof. RLS and server authorization must have parity tests wherever both enforce the same access.

---

## 15. Compliance and Readiness Composition

| Fact/gate | Owner | CL-01 responsibility |
|---|---|---|
| authenticated actor/security | Identity | owns |
| resource authority | Role | owns interpretation |
| consent proof | Consent | owns evidence only |
| buyer actor | Customer | owns |
| commercial entitlement/quota | Track | owns current policy |
| ComplianceHold | Hold Module | consumes |
| Professional readiness | Professional Eligibility | external; Track is one input |
| verification | Trust Verification | external; Consent may prove disclosure |
| KYC/tax/payout | Payment/Payout/Tax | external; Identity may provide step-up |
| healthcare | Healthcare | external |
| job compliance | Job Compliance | external |

The action-owning Module composes required facts. There is no universal CL-01 `canDoEverything` decision.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

Domain meaning stays local:

- `UserSecurityEvent` — Identity security history.
- `ConsentLog` — consent proof.
- `TrackSubscriptionEvent` — Track subscription history.
- `TrackUsageEvent` — Track usage proof.
- Customer-specific lifecycle events, if added, remain Customer-owned.
- AuditEvent remains generic and separate.

Reliable cross-Module effects use the canonical transactional outbox/consumer inbox. Raw provider webhooks are never public domain events.

Expected workers include security/session expiry, recovery expiry/reconciliation, Customer backfill/reconciliation, consent re-consent after versioning exists, free Track assignment if async, grant expiry, usage counter rebuild, Stripe reconciliation, privacy-target execution, and migration integrity scans.

All DB-owned races use transactions/constraints/locks, never in-memory locks.

---

## 17. Provider Integrations

### Identity

```text
Identity
→ provider-neutral auth/passkey/OTP/recovery port
→ Supabase Auth / Google / Apple / WebAuthn / Twilio / recovery provider
→ verified normalized result
→ Identity-owned transition
```

No raw password/biometric image/provider payload becomes domain truth.

### Track Billing

```text
Track
→ provider-neutral subscription port
→ Stripe Checkout/Billing/Portal
→ verified callback
→ Track adapter/status translation
→ TrackSubscription transition
```

Success redirects do not activate subscriptions. Reconciliation is required.

Webhook rules: raw signature verification first; dedupe before side effects; explicit status mapping; unknown statuses fail closed; owner-specific event receipt truth; periodic reconciliation; Ops failure reporting.

---

## 18. Search / Projection Boundaries

Track owns candidate/search boost entitlement truth. Search owns `SearchUpsertEvent`, indexing, de-indexing, provider documents, and reconciliation.

```text
Track policy change
→ Track event/outbox
→ Search projection-refresh interface
→ Search-owned projection work
```

Search must not reconstruct grant precedence or store a local premium boolean.

**Proposed Ruling PR-CL01-05:** CustomerProfile public indexing remains disabled until a dedicated public-visibility architecture is approved. Display fields do not imply publication.

---

## 19. Media / File Boundaries

Customer owns avatar/reference meaning. Media owns upload, validation, MIME checks, malware scan, processing, EXIF/GPS scrubbing, storage, object deletion, generic grants, and signed URL issuance.

CL-01 must not create a customer file scanner, R2/S3 client, or presign service. Identity must never treat avatar/media/notification-device state as authentication.

---

## 20. Privacy / Retention

Privacy owns request verification, job/target orchestration, exemptions, export aggregation, and completion. Identity, Consent, Customer, and Track each implement:

- subject-data enumeration;
- export serializer;
- retention fact evaluation;
- idempotent privacy instruction execution;
- erase/anonymize/restrict/revoke/detach/retain outcomes;
- provider deletion/detachment where applicable.

Identity security/age/recovery retention is unresolved. Consent has a cascade-delete/retention conflict. Customer must consider retained commerce obligations. Track may have billing/legal retention. Feature Modules never create separate PrivacyRequest workflows.

---

## 21. Audit and Observability

Audit and domain history remain separate. Use AuditEvent for important platform/admin actions and AccessAuditLog for sensitive reads where required. Never copy raw secrets, provider payloads, consent text, PHI, or financial details into generic audit metadata.

Observability captures safe correlation IDs, operation, result class, latency, retry counts, provider-safe codes, and aggregate references. IntegrationFailure/SystemEvent/QueueJob/OpsIncident never become CL-01 lifecycle truth.

---

## 22. Security Boundaries

- Server-side validation on every mutation/external trust boundary.
- Never trust client user/role/profile IDs.
- RLS + server authorization parity where applicable.
- No raw passwords, OTPs, recovery secrets, provider secrets, session tokens, or biometric images in app tables/logs.
- Canonical token/hash/encryption primitives only.
- Provider credentials server-only and environment isolated.
- Rate-limit age/auth/recovery/OTP/admin entry points per approved policy.
- SensitiveActionSession must be action/target/expiry scoped.
- Verify provider callbacks before parsing/business effects; replay protect them.
- Minimize provider payloads and telemetry.
- Use DB transactions/constraints/locks for concurrency.
- Translate provider failures into stable result categories.
- Sensitive admin/support access requires Role plus step-up/access audit where policy requires.

---

## 23. Testing Architecture

Required test layers:

- Module unit tests for each transition/policy.
- Public-interface contract tests with consumer fixtures.
- Lifecycle transition tests, including invalid/terminal transitions.
- Identity→Role, User→Customer, Consent→consumer, Track→consumer integration tests.
- Provider adapter tests: success, failure, unknown status, forged signature, duplicate/out-of-order event, timeout, reconciliation.
- Idempotency/concurrency tests: duplicate User/Profile provisioning, step-up double-verify, recovery races, consent replay, quota boundary, billing event replay, counter rebuild.
- Compliance/privacy tests: age gate before User creation, standalone consent, no consent-as-permission, retention-safe privacy, no secret/biometric leakage, Hold enforcement.
- Critical E2E: signup→CustomerProfile, blocked signup, scoped authorization, passkey/step-up, recovery, consent acceptance, free Track entitlement, quota boundary, paid Billing callback, Privacy target harness.

---

## 24. Invariants

### Rules coding agents must never violate

1. A Cluster never becomes lifecycle owner.
2. User remains account identity only.
3. Identity owns authentication; Role owns permission interpretation.
4. Identity structurally owns UserRole/PlatformRole.
5. Role must not mutate OrganizationMember/OrganizationRole/ThreadParticipant under PR-CL01-02.
6. Authorization never substitutes for consent/entitlement/readiness/payment/hold clearance.
7. ConsentLog proves an exact acceptance only.
8. Latest ConsentLog must not be treated as active version.
9. CustomerProfile is buyer actor truth after approved cutover.
10. Customer owns CustomerProfile transitions; shared ProfileStatus ownership is not silently rewritten.
11. Track is sole commercial entitlement owner for customer/candidate/professional tracks.
12. No local premium/fee/commission/quota/boost/priority truth.
13. TrackUsageEvent is immutable.
14. TrackUsageCounter is derived/rebuildable.
15. Historical consumer snapshots are not retroactively recalculated from current plans.
16. Provider state/payloads never replace domain truth/types.
17. Provider callbacks are verified and deduped before side effects.
18. Shared dedupe mechanics do not create one universal provider-event truth.
19. Success redirects/browser permission/provider dashboards never transition domain state.
20. SensitiveActionSession is not business permission/entitlement.
21. No raw biometric images, passwords, OTPs, provider secrets, or raw recovery tokens.
22. ComplianceHold remains the reusable stop sign.
23. Privacy owns orchestration; CL-01 owners execute their records.
24. Product archive/delete is not legal erasure.
25. Media owns file mechanics.
26. Search owns projection mechanics.
27. CustomerProfile stays out of public search until approved.
28. Audit/AccessAudit never replace domain evidence.
29. Observability never replaces lifecycle state.
30. No normal direct foreign Prisma repository.
31. Shared-operation aliases do not become separate services.
32. Async effects use durable outbox/idempotency/retry when reliability matters.
33. DB-owned concurrency never uses process memory locks.
34. Unknown action/provider status/policy/value type fails closed.
35. Destructive migration/User deletion never bypasses retention/privacy review.
36. Build progress cannot redefine architecture.

---

## 25. Prohibited Duplicate Implementations

| Prohibited duplicate | Use instead |
|---|---|
| `currentUser.ts`, route-local session parser, marketplace auth helper | SH-001 `resolveAuthenticatedActor` |
| `isAdmin`, `isOwner`, org/thread permission helpers | SH-002 `authorizeResourceAction` |
| Role mutation repository for OrganizationMember/ThreadParticipant | source-owner interface + Role policy |
| `acceptedTerms`, local FCRA/calendar/subscription consent booleans/tables | Consent public interfaces |
| consumer active-consent-version selector | SH-009 `resolveActiveConsentVersion` |
| buyer reconstruction from User fields | SH-004 `resolveCustomerActor` |
| Customer R2/S3/presign/scanner service | Media / File Access |
| `isPremium`, plan-name switches, local fee/commission/boost/priority rules | SH-005 `resolveEntitlement` |
| feature-local quota counter | SH-006 `consumeMeteredEntitlement` |
| Order current-plan fee/commission calculator | Track policy quote → Order snapshot |
| Track Typesense client | Search public interface |
| Track generic payment/payout/tax service | Payment / Payout / Tax |
| custom webhook verifier/retry in Track/Identity | canonical provider-webhook primitives |
| local generic `blocked` flags | ComplianceHold |
| CL-01 PrivacyRequest/erase-everywhere service | Privacy protocols |
| CL-01 audit/access tables | Audit / Event Ledger |
| provider failure fields used as domain statuses | Ops + owner lifecycle |
| generic `cl01Service` owning auth+consent+entitlement+readiness | owner Module composition |

---

## 26. Deferred / Unresolved Decisions

| ID | Question | Why unresolved | Blocks |
|---|---|---|---|
| U-CL01-01 | Canonical provider subject ↔ User mapping? | provider/schema mapping incomplete | edge-case provisioning/migrations |
| U-CL01-02 | Canonical email truth/sync/conflict policy? | Supabase/User/provider copies | email-change/merge edge cases |
| U-CL01-03 | AuthProviderAccount uniqueness/merge rules? | provider subjects can conflict | safe multi-provider linking |
| U-CL01-04 | OAuth/social age-gate sequencing? | age gate must precede User creation | social signup production |
| U-CL01-05 | Age-gate policy version/jurisdiction proof? | current proof lacks full provenance | final compliance proof schema |
| U-CL01-06 | Session revocation/assurance/security-lock semantics? | local/provider state interaction incomplete | high-risk sessions |
| U-CL01-07 | Step-up action matrix/TTL/attempt/fallback/OTP policy? | enums exist, policy incomplete | production sensitive actions |
| U-CL01-08 | Recovery provider-event receipt/dedupe/manual-review model? | no clear processed-event truth | live recovery callbacks |
| U-CL01-09 | Identity security/age/recovery retention? | legal/security retention absent | destructive Identity privacy |
| U-CL01-10 | Single authorization policy source + RLS generation/parity method? | code/SQL drift risk | broad production authorization |
| U-CL01-11 | RESOLVED by WA-R001: PR-CL01-02 is confirmed | SH-002 and owner architectures agree; registry corrected | owner-specific DTO completion only; foreign mutation remains forbidden |
| U-CL01-12 | UserRole assignment/revocation history model? | current structure incomplete | advanced admin role history |
| U-CL01-13 | Consent version/content/hash/effective-date catalog model? | only log version string exists | active version/presentation/re-consent |
| U-CL01-14 | Consent retry idempotency vs legitimate re-acceptance? | no semantic uniqueness rule | production consent mutation |
| U-CL01-15 | Consent retention vs User cascade delete? | privacy conflict | destructive privacy/User deletion |
| U-CL01-16 | Withdraw/decline/re-consent rules? | current model acceptance-only | withdrawal/re-consent |
| U-CL01-17 | When must consumer persist consentLogId vs query current proof? | contextual needs differ | Agreement/Verification/Track binding |
| U-CL01-18 | CustomerProfile provisioning synchronous or outbox/worker? | choreography missing | production default provisioning |
| U-CL01-19 | CustomerProfile cutover/backfill for legacy User buyer refs? | legacy relations remain | new buyer source constraints |
| U-CL01-20 | ProfileStatus enum ownership after CustomerProfile addition? | glossary conflict | enum refactor |
| U-CL01-21 | CustomerProfile transition/access/hold/archive matrix? | statuses lack rules | status/archive production |
| U-CL01-22 | User vs Customer display precedence/avatar/public visibility? | duplicate fields/no visibility lifecycle | sync/public search |
| U-CL01-23 | Customer privacy behavior with retained obligations? | commerce references may remain | destructive Customer privacy |
| U-CL01-24 | Free Track representation? | plan/subscription/grant semantics incomplete | default Track provisioning |
| U-CL01-25 | Active-subscription + exactly-one matching profile constraints? | schema does not fully enforce | subscription mutation |
| U-CL01-26 | Entitlement catalog/value constraints/grant precedence? | value/preference rules incomplete | broad resolver/grants |
| U-CL01-27 | Plan revision/effective-date history? | current plans can change | safe live plan edits |
| U-CL01-28 | Track subscription transition table + Stripe receipt/dedupe + consent binding? | statuses exist, provider semantics incomplete | live paid subscriptions |
| U-CL01-29 | Usage period/timezone/refund/reversal/idempotency/counter uniqueness? | quota semantics incomplete | production metering |
| U-CL01-30 | Buyer-fee/pro commission rounding/basis-point snapshot rules? | impacts historical Order truth | Order bridge |
| U-CL01-31 | RESOLVED P01 / WA-R011: early-access benefit, no queue rank/quota | Track eligibility; Booking release instants | implement and validate Booking bridge |
| U-CL01-32 | Track billing/subscription retention/anonymization? | legal minimum/duration absent | destructive Track privacy |
| U-CL01-33 | RESOLVED product model (WA-R005): separate Organization ATS commercial lane | Track remains commercial-policy owner; Organization is not a fourth User track | Organization-scoped persistence, pricing/quotas/feature allocation and billing contracts remain deferred |

When a feature reaches an unresolved item, update architecture with a ruling first or keep dependent production behavior disabled/fail-closed.

---

## 27. Architecture Decision Summary

### Confirmed binding rulings

1. CL-01 contains exactly the five listed Modules.
2. CL-01 coordinates but owns no lifecycle.
3. Identity owns User/auth/security/passkey/step-up/recovery truth.
4. Role owns permission interpretation.
5. Identity structurally owns UserRole/PlatformRole; Role interprets.
6. Consent owns exact version-specific acceptance proof, not permission.
7. Customer owns CustomerProfile buyer actor truth.
8. Track owns current plan/subscription/grant/usage policy.
9. No local premium/fee/commission/quota/boost/priority truth.
10. TrackUsageEvent is immutable; TrackUsageCounter is projection.
11. Consumers own business lifecycles/historical snapshots.
12. Hold, Privacy, Audit, Ops, Notification, Search, and Media retain their canonical ownership.
13. Canonical Shared Operations are reused.
14. Provider callbacks use shared verification/dedupe mechanics plus owner-specific processing/truth.
15. Search remains projection; Audit/Ops remain support evidence.

### Proposed Rulings

- **PR-CL01-01:** feature-first five-Module organization; no generic CL-01 domain service.
- **PR-CL01-02:** Organization Hiring owns OrganizationMember/OrganizationRole; Messaging owns ThreadParticipant; Role interprets.
- **PR-CL01-03:** Customer owns CustomerProfile transition policy even if ProfileStatus is shared.
- **PR-CL01-04:** Track owns Stripe Billing subscription adapter/status translation; Payment/Payout/Tax keeps general financial truth.
- **PR-CL01-05:** CustomerProfile public search stays disabled until dedicated visibility architecture.

### Conservative posture

No permissive auth fallback, no Customer actor cutover without migration rules, no public Customer search, no invented consent-version model, no live paid Track state machine before its gates, no unresolved entitlement defaults, and no hard delete bypassing Privacy/retention.

---

## 28. Coding-Agent Usage

Before changing CL-01, read:

1. `context/project-overview-v3.md`
2. root `architecture.md`
3. root `code-standards.md`
4. Canonical Shared Operations Registry
5. this Cluster `architecture.md`
6. this Cluster `build-plan.md`
7. Target Module architecture
8. Target Module implementation plan
9. relevant dependency Module public-interface sections
10. progress tracker

Also inspect current Prisma schema/migrations before data changes. If code and architecture disagree, record the discrepancy, determine which is stale, update binding context first when a real decision changed, then implement.


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
