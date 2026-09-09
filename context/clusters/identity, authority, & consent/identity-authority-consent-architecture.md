# Identity, Authority, Consent & Entitlements Architecture

> **Cluster ID:** `CL-01`  
> **Cluster name:** Identity, Authority, Consent & Entitlements  
> **Cluster type:** `foundation_access_control_consent_entitlement_policy`  
> **Repository target:** `context/clusters/identity-authority-consent-entitlements/architecture.md`  
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

**Proposed Ruling PR-CL01-02:** Organization Hiring owns OrganizationMember/OrganizationRole lifecycle; Messaging owns ThreadParticipant lifecycle; Role owns interpretation only. Until approved/amended, Role may implement read-only owner-fact contracts but no mutations.

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
| `resolveAuthenticatedActor` | Identity | map trusted session/system credential to actor | session/request credential | user/context/assurance | truth/context | local current-user logic |
| `provisionUserAfterAgeGate` | Identity | idempotent User/provider provisioning | age decision + provider identity | User/provider mapping | truth | bypass age gate |
| `getUserSecurityPosture` | Identity | safe security readiness summary | actor/target | tier/method/lock summary | truth/projection | raw credential truth |
| passkey commands | Identity | register/use/list/revoke passkeys | actor + verified ceremony | credential result/ref | truth/evidence | biometrics |
| `requireStepUpForSensitiveAction` | Identity | action-scoped recent stronger auth | actor/action/target | allowed/challenge/session evidence | decision/evidence | business permission |
| recovery commands/query | Identity | own recovery workflow | request/provider result | recovery state | truth | KYC/screening |
| `authorizeResourceAction` | Role | action/resource authority | actor/action/owner facts | decision/reasons | decision | consent/entitlement/readiness |
| owner-specific `queryOwnerFacts` | each source owner | supply relationship facts | resource/purpose | minimal DTO | truth | foreign repository |
| `recordConsentProof` | Consent | persist exact acceptance | user/type/version/evidence | proof ID/ref | evidence | permission |
| `queryConsentProof` | Consent | query exact required version | user/type/version | accepted + proof ref | evidence | active version logic |
| `resolveActiveConsentVersion` | Consent | resolve current version/config | type/context | version/hash/effective metadata | policy/config | “latest log” inference |
| `presentStandaloneConsent` | Consent | return required disclosure | type/context | renderable version | config/projection | provider state |
| `resolveCustomerActor` | Customer | resolve User→CustomerProfile | User | profile ID/status | truth | buyer from User fields |
| `provisionDefaultCustomerProfile` | Customer | ensure one profile | eligible User | profile result | truth | direct Identity insert |
| Customer profile commands/query | Customer | read/update/status | actor/profile/patch | profile/result | truth | file/search/commerce lifecycles |
| `resolveEntitlement` | Track | current typed commercial policy | track/profile/key/context | value/reason/source/evidence | decision/truth | local premium switch |
| `consumeMeteredEntitlement` | Track | atomic quota + usage proof | entitlement/quantity/idempotency target | permit/deny + usage receipt | decision/evidence | local counter |
| Track catalog/subscription queries | Track | current plan/subscription state | user/profile/track | provider-neutral DTO | truth | Stripe object |
| Track subscription commands | Track | start/change/cancel | actor/plan/proof refs | initiation/result | command result | success redirect = active |
| `quoteOrderTrackPolicy` | Track | fee/commission current policy | buyer/professional/order context | typed policy/evidence | decision | Order mutation/current-plan recalculation |

---

## 11. Canonical Shared Operations Used by This Cluster

The supplied registry exposes canonical names; no stable SH-### identifiers are visible in the supplied version, so this file does not invent them.

| Operation | Meaning | Canonical owner/class | CL-01 use | Local policy stays with | Must not be rebuilt as |
|---|---|---|---|---|---|
| `resolveAuthenticatedActor` | trusted session→actor | Identity / platform capability | protected entry | Identity mapping/assurance | current-user helpers |
| `authorizeResourceAction` | resource/action permission | Role / cross-cutting | all protected actions | Role action policy + owner facts | isAdmin/isOwner/org/thread helpers |
| `queryOwnerFacts` | minimum relationship facts | each source owner / shared contract, separate implementations | Role reads | source owner | universal repository |
| `resolveCustomerActor` | User→buyer profile | Customer public interface | customer workflows | Customer status/access | buyer-from-User logic |
| `recordConsentProof` | exact acceptance evidence | Consent | acceptance | Consent version policy | per-feature consent store |
| `queryConsentProof` | exact proof lookup | Consent | consent gates | Consent | local consent query |
| `resolveActiveConsentVersion` | effective version/config | Consent | presentation | Consent context rules | latest-log inference |
| `presentStandaloneConsent` | standalone disclosure | Consent | security/screening/calendar/Track | Consent wording/version | buried feature terms |
| `resolveEntitlement` | typed commercial policy | Track | current perks/waivers/boosts | Track precedence | isPremium |
| `consumeMeteredEntitlement` | atomic quota + usage proof | Track | application/usage limits | Track period/counting | local counter |
| `requireStepUpForSensitiveAction` | scoped stronger auth | Identity | sensitive actions | Identity assurance matrix | payout/admin OTP service |
| `evaluateComplianceHold` | stop-sign decision | Hold owner | hold-sensitive CL-01 actions | Hold + target policy | local blocked flags |
| `appendAuditEvent` | generic action audit | Audit | material admin/security actions | audit selection/safe metadata | CL-01 audit table |
| `recordSensitiveAccess` | sensitive-access proof | Audit | sensitive reads | access policy | local access log |
| `appendDomainLifecycleEvent` | shared append mechanics | shared mechanism, owner truth | Identity/Track/Customer domain history | domain owner | generic event truth |
| `executeIdempotentCommand` | semantic replay safety | platform | provisioning/consent/metering/provider commands | caller key/result | local idempotency subsystem |
| `enqueueReliableJob` | durable background work | platform | expiry/backfill/reconciliation/privacy | owner job payload | custom job truth |
| `executeRetryWithBackoff` | retry + dead letter | platform/Ops | workers/providers | owner failure classification | ad-hoc retry loops |
| `verifyProviderWebhookSignature` | authenticate callback | shared provider security | recovery/Stripe Billing | provider adapter config | custom route verifier |
| `deduplicateProviderEvent` | prevent repeat side effects | shared mechanism, owner event truth | recovery/Billing | owner event identity | one global provider truth |
| `translateProviderStatus` | provider→domain input | owner adapter/shared pattern | Identity/Track | lifecycle owner | scattered provider enums |
| `recordIntegrationFailure` | operational failure proof | Ops | provider/worker failures | safe owner context | domain failure status |
| `normalizeAndHashIdentifier` | stable nonplaintext comparison | crypto primitive | age/rate/recovery evidence | owner normalization/retention | local hash |
| `generateSecureToken` | purpose-bound secure secret | security primitive | recovery/security when needed | owner TTL/binding | token helper |
| `minimizeAndRedactProviderInput` | minimum provider payload | source policy + shared serializer | identity provider calls | Identity sensitivity policy | raw User object export |
| `enumerateSubjectData` | owner subject inventory | each owner via Privacy | Identity/Consent/Customer/Track | owner schema meaning | Privacy direct table crawl |
| `executePrivacyInstruction` | owner erase/export/etc | Privacy orchestrates; owner executes | CL-01 executors | owner invariants | local PrivacyRequest |
| `evaluateRetentionRequirement` | owner retention facts | owner + Privacy | destructive privacy prep | owner legal facts | local exemption workflow |
| `anonymizePersonalFields` | field pseudonymization | shared primitive + owner map | privacy execution | owner fields/invariants | global crawler |
| `requestNotification` | semantic delivery request | Notification | security/profile/subscription notices | source business trigger | direct email/SMS/push client |

`queryOwnerFacts` is shared contract/separate policy. Webhook verification/dedupe is shared mechanism/separate truth. Decision envelopes may be shared response contracts but never share policy.

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

All protected operations begin with `resolveAuthenticatedActor` unless explicitly anonymous (age gate/auth entry/verified provider callback).

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
| `currentUser.ts`, route-local session parser, marketplace auth helper | `resolveAuthenticatedActor` |
| `isAdmin`, `isOwner`, org/thread permission helpers | `authorizeResourceAction` |
| Role mutation repository for OrganizationMember/ThreadParticipant | source-owner interface + Role policy |
| `acceptedTerms`, local FCRA/calendar/subscription consent booleans/tables | Consent public interfaces |
| consumer active-consent-version selector | `resolveActiveConsentVersion` |
| buyer reconstruction from User fields | `resolveCustomerActor` |
| Customer R2/S3/presign/scanner service | Media / File Access |
| `isPremium`, plan-name switches, local fee/commission/boost/priority rules | `resolveEntitlement` |
| feature-local quota counter | `consumeMeteredEntitlement` |
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
| U-CL01-11 | Is PR-CL01-02 accepted? | registry/glossary conflict | foreign lifecycle mutation; read-only policy can proceed |
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
| U-CL01-31 | Priority scheduling rank/ties/quota/expiry meaning? | entitlement lacks scheduling semantics | Booking bridge |
| U-CL01-32 | Track billing/subscription retention/anonymization? | legal minimum/duration absent | destructive Track privacy |
| U-CL01-33 | Organization commercial access stays OrganizationFeatureAccess or becomes a Track? | outside current 3-track model | future org plans only |

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

1. root `project-overview.md`
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
