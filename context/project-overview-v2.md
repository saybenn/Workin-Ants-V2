# Workin Ants Project Overview

> **Repository location:** `context/project-overview.md`  
> **Project name:** Workin Ants  
> **Project state:** Greenfield MVP architecture planning  
> **Architecture:** One multi-actor marketplace platform, one managed codebase  
> **Primary audience:** Codex, developers, reviewers, maintainers, and future AI agents  
> **Current cluster registry:** `v2.3-customer-subscription`  
> **Current Deep Module count:** 34  
> **Current schema snapshot:** 177 Prisma models and 207 Prisma enums parsed from the uploaded schema  
> **Legal posture:** Working architecture guide; not legal advice

---

## Source Basis

This file is derived from the current Workin Ants architecture resources:

- Ubiquitous Language Pack v2.2
- Deep Module Registry / refreshed module JSON
- cleaned `schema.prisma`
- Cluster Registry `v2.3-customer-subscription`
- Compliance Inventory / Legal Homework Map
- Cluster Digestion and Cluster Handout direction from planning conversations

This file is not the full architecture specification. It is the plain-English project anchor that every agent should read before using `architecture.md`, `build-plan.md`, or feature-specific context.

---

## How Agents Should Use This File

Read this file first to understand what Workin Ants is, who it serves, what the major workflows are, and which boundaries must never be violated.

Then read the other `/context` files before implementation:

```text
/context/project-overview.md
/context/architecture.md
/context/build-plan.md
/context/code-standards.md
/context/library-docs.md
/context/ui-tokens.md
/context/ui-rules.md
/context/ui-registry.md
/context/progress-tracker.md
```

Do not begin feature work from memory or from a single file. The project depends on controlled context: product overview, architecture, build sequence, code standards, library usage, UI rules, and progress must stay aligned.

---

## Product Definition

Workin Ants is a trust-aware marketplace and work platform that connects customers, professionals, candidates, and hiring organizations through paid work, sellable offerings, formal jobs, bookings, digital goods, messaging, payments, verification, privacy, compliance, and operational controls.

The platform supports multiple actor lanes from a base `User` account:

```text
User
→ CustomerProfile for buying, posting Gigs, placing Orders, bookings, reviews, and disputes
→ ProfessionalProfile for selling Offerings, responding to Gigs, receiving Orders, and payouts
→ CandidateProfile for applying to Jobs and managing resume/application identity
→ OrganizationMember for acting inside an Organization that posts Jobs
```

The product is not a simple job board, not only a gig marketplace, not only an ecommerce store, and not only a hiring ATS. It is a single platform where commerce, hiring, delivery, compliance, identity, subscriptions, and public discovery are kept connected but cleanly owned.

---

## Product Promise

Workin Ants helps users:

- Find services, professionals, gigs, jobs, courses, and digital products through trusted discovery.
- Buy or sell work through source-of-truth Orders rather than scattered payment records.
- Separate buyer, seller, candidate, and organization identities without overloading `User`.
- Let Professionals sell only when profile, verification, healthcare, financial, tax, and compliance gates permit it.
- Let Organizations post compliant Jobs and manage candidate applications without mixing hiring with gigs.
- Deliver paid services, files, videos, courses, and downloads through entitlement-aware access grants.
- Use subscriptions and track entitlements without scattering premium booleans throughout the codebase.
- Preserve legal/compliance proof for consent, privacy, verification, payments, tax, files, messaging, location safety, audit, moderation, rewards, prizes, and healthcare-sensitive workflows.

The system should make platform state explainable:

```text
Who is acting?
Under which actor profile?
What are they trying to do?
What source record owns the lifecycle?
What gates must pass?
What proof must be stored?
What downstream modules may consume the result?
```

---

## The Problem It Solves

### Before Workin Ants

A marketplace or work platform can easily become a tangle of overlapping concepts:

- A single `User` record tries to mean buyer, seller, applicant, admin, contractor, and organization member.
- `isVerified`, `isPaid`, `isPremium`, `canPayout`, and `isHealthcareProvider` booleans spread through random tables.
- Stripe, search, calendar, video, email, SMS, file storage, and AI provider state get treated as business truth.
- Gigs, Jobs, Offerings, Orders, Applications, and Bookings get mixed together.
- Compliance proof lives in frontend checkbox state or generic logs instead of source records.
- Public search indexes private or stale data.
- Payouts, rewards, prizes, taxes, and disputes become financially and legally ambiguous.
- Digital products are delivered by permanent URLs instead of entitlement-controlled grants.
- Healthcare-sensitive workflows leak into general messaging, media, video, and admin tooling without boundaries.
- Privacy erasure is confused with normal product deletion.

### After Workin Ants

Workin Ants gives each lifecycle a clear owner:

- `User` is the base account identity.
- `CustomerProfile` is the buyer/customer actor.
- `ProfessionalProfile` is the seller actor.
- `CandidateProfile` is the applicant actor.
- `Organization` is the hiring entity.
- `Offering` is sellable supply.
- `Gig` is paid public demand.
- `Job` is formal hiring.
- `Order` is transaction truth.
- `Booking` is scheduling truth.
- `VerificationCheck` is trust-screening truth.
- `KycVerification`, `TaxProfile`, `PayoutAccount`, `PayoutRequest`, and `PayoutTransfer` are financial compliance truth.
- `ConsentLog` is consent proof.
- `PrivacyRequest` and `DataErasureJob` are privacy-rights truth.
- `SearchUpsertEvent` is search projection queue truth.
- `ComplianceHold` is the reusable stop sign.
- `TrackSubscription` and `TrackEntitlementGrant` are subscription and entitlement truth.

The result is a platform where agents and developers can build without inventing new local ownership rules.

---

## Core Architecture Principle

Deep Modules remain the source-of-truth architecture.

Clusters are the presentation, planning, and controlled-context layer.

That means:

- A Deep Module owns lifecycles, schemas, statuses, invariants, and proof records.
- A Cluster groups related Deep Modules so humans and AI agents can reason about a controlled field of context.
- Clusters do not override ownership.
- A schema should not be duplicated into multiple ownership zones.
- A bridge between clusters means “consume this state,” not “copy this lifecycle.”

---

## Canonical Architecture Rules

1. **One owner per lifecycle.** Every lifecycle has exactly one module that owns status changes; other modules consume state.
2. **Order is transaction truth.** Stripe and other processors are payment rails. `Order` and `OrderEvent` remain platform transaction truth.
3. **User is not every identity.** `CustomerProfile`, `ProfessionalProfile`, `CandidateProfile`, and `OrganizationMember` are actor/context identities.
4. **Profile is not verification.** Display readiness can be cached, but `VerificationCheck`, `KycVerification`, `TaxProfile`, `PayoutAccount`, and `HealthcareComplianceProfile` hold compliance truth.
5. **Consent is proof, not permission logic.** `ConsentLog` records acceptance/version proof; feature modules own the action unlocked by that consent.
6. **ComplianceHold is the reusable stop sign.** Do not scatter local block flags across feature modules.
7. **deletedAt is product deletion; erasedAt is privacy erasure.** Legal erasure is orchestrated through privacy workflows.
8. **Search is projection.** Typesense/search documents are derived from source models and must be re-indexed or de-indexed when source truth changes.
9. **Healthcare is a lane, not a user type.** Sensitivity is triggered by taxonomy/offering/profile/data boundary, not a blanket `User` flag.
10. **TrustBadge is display; VerificationCheck is truth.**
11. **Processor-held funds are not a Workin Ants wallet or escrow.** Use `PayoutRequest`, `PayoutTransfer`, and `ProfessionalBalanceLedgerEntry`.
12. **Track entitlements are policy truth.** Use `TrackSubscription` and `TrackEntitlementGrant`; do not create local `isPremium`, `canBoost`, or `hasFeature` booleans.

---

## Product Structure

The platform is organized around 10 Clusters.

| Cluster | Name | Type | Included Deep Modules |
| --- | --- | --- | --- |
| CL-01 | Identity, Authority, Consent & Entitlements | foundation / access / control / consent / entitlement / policy | identity_access, role_authority, consent_disclosure, customer_buyer_profile, track_subscription_entitlement |
| CL-02 | Discovery, Classification & Visibility | discovery / taxonomy / projection | taxonomy_classification, ai_taxonomy, search_public_visibility |
| CL-03 | Professional Supply & Readiness | core / marketplace / supply / eligibility / regulated / readiness | professional_eligibility, trust_verification_screening, marketplace_supply, payment_payout_tax, healthcare_regulated_services |
| CL-04 | Customer Demand, Order & Resolution | core / customer / demand / commerce / transaction / dispute | gig_demand, transaction_order, review_dispute |
| CL-06 | Organization Hiring & Candidate Pipeline | hiring / domain / candidate / privacy / job / compliance | organization_hiring, job_compliance, candidate_application_resume_privacy, job_interview |
| CL-05 | Scheduling, Media & Digital Delivery | delivery / infrastructure / access / grant / file / video / booking | booking_calendar, video_session, media_file_access, digital_goods_access |
| CL-07 | Messaging & Notification Rail | cross / cutting / communication / rail | messaging, notification |
| CL-08 | Privacy & Location Safety | privacy / compliance / safety / control | privacy_data_erasure, location_safety |
| CL-09 | Moderation, Holds, Audit & Ops | governance / compliance / stop / sign / audit / observability | content_moderation_legal_notice, admin_review_compliance_hold, audit_event_ledger, observability_ops |
| CL-10 | Incentives, Rewards & Prize Economy | feature / ecosystem / prize / compliance / reward / ledger | sweepstakes_prize, gamification_rewards |

---

## Clean Visual Spine

The main platform story should be explained in this order:

```text
CL-01 Identity, Authority, Consent & Entitlements
        ↓
CL-02 Discovery, Classification & Visibility
        ↓
CL-03 Professional Supply & Readiness
        ↓
CL-04 Customer Demand, Order & Resolution
        ↓
CL-05 Scheduling, Media & Digital Delivery
        ↓
CL-07 Messaging & Notification Rail
```

Guardrails wrap the platform:

```text
CL-08 Privacy & Location Safety
CL-09 Moderation, Holds, Audit & Ops
```

The feature ecosystem sits beside the core flow:

```text
CL-10 Incentives, Rewards & Prize Economy
```

---

## Cluster Effects in Plain English

### CL-01 — Identity, Authority, Consent & Entitlements

This cluster answers: **who is acting, under which actor branch, what can they do, and what consent or entitlement proof exists?**

It takes a raw person entering the platform and turns them into an authenticated account with actor branches, permissions, consent proof, security posture, and plan/track entitlement rules. Without it, every workflow would invent its own identity, permission, consent, and premium-access logic.

### CL-02 — Discovery, Classification & Visibility

This cluster answers: **how should platform objects be classified, suggested, and safely projected into public search?**

It takes raw platform objects and turns them into accepted categories, tags, AI suggestions, and search projections. Without it, search becomes source truth, AI suggestions become uncontrolled truth, and compliance-sensitive categories get missed.

### CL-03 — Professional Supply & Readiness

This cluster answers: **can this ProfessionalProfile sell this Offering, pass required gates, and receive money?**

It takes raw professional ambition and digests it through professional profile readiness, marketplace supply, verification, healthcare gates, payout readiness, tax state, and track entitlements until the output is sellable, compliant supply. Without it, users sell directly, high-risk work goes public unsafely, and payout readiness becomes a scattered boolean mess.

### CL-04 — Customer Demand, Order & Resolution

This cluster answers: **what customer demand or purchase became an Order, what pricing/entitlement policy was snapshotted, and what happened after?**

It takes raw buyer demand, accepted gig assignments, pricing selections, and agreement requirements and turns them into transaction truth, reviewable outcomes, and dispute-aware resolution. Without it, Stripe becomes mistaken for the business transaction and disputes/refunds/payout holds lose a stable anchor.

### CL-05 — Scheduling, Media & Digital Delivery

This cluster answers: **once an actor is entitled, how does the platform safely deliver the booking, file, video, or digital good?**

It takes paid or entitled access and turns it into time slots, video rooms, signed playback, private media grants, validated uploads, and expiring download access. Without it, delivery becomes permanent URLs, public files, duplicate bookings, unbounded video links, and unsafe uploads.

### CL-06 — Organization Hiring & Candidate Pipeline

This cluster answers: **how does an Organization post compliant Jobs and move CandidateProfiles through applications, resume review, and interviews?**

It takes raw hiring intent and turns it into compliant Job posts, private candidate applications, resume access proof, candidate search projection, and interview workflows. Without it, hiring gets mixed with gig work and resumes become unsafe attachments.

### CL-07 — Messaging & Notification Rail

This cluster answers: **how do people talk and get alerted without the communication layer owning business decisions?**

It takes business events and turns them into context-bound Threads, Messages, Notifications, Subscriptions, and Delivery attempts. Without it, every module invents its own chat, email, SMS, and push logic.

### CL-08 — Privacy & Location Safety

This cluster answers: **what must be erased, retained, exported, fuzzed, or revealed only after a gate?**

It takes sensitive user data, exact location, and privacy requests and turns them into formal erasure/export jobs, retention exemptions, fuzzy public projections, and gated exact-location reveal records. Without it, product deletion gets confused with legal erasure and public search can leak location.

### CL-09 — Moderation, Holds, Audit & Ops

This cluster answers: **what must stop, what proof must be preserved, what needs admin review, and what failed operationally?**

It takes reports, legal notices, compliance issues, sensitive access events, system failures, and provider failures and turns them into cases, holds, audit records, incidents, queues, and operational visibility. Without it, each module invents its own stop sign, legal workflow, log, and failure dashboard.

### CL-10 — Incentives, Rewards & Prize Economy

This cluster answers: **how can the platform reward engagement without accidentally creating illegal prize odds or tax ambiguity?**

It takes engagement events and turns them into points, challenges, leaderboards, rewards, sweepstakes entries, prize drawings, prize winnings, and tax-aware fulfillment. Without it, rewards and prizes blur together and paid activity can accidentally affect chance-based prize odds.

---

## Deep Module Roster

The current registry contains 34 Deep Modules.

| Module ID | Module Name | Type | Build Status |
| --- | --- | --- | --- |
| identity_access | Identity & Access Module | capability_security | mvp_active |
| role_authority | Role / Authority Module | capability_security | mvp_active |
| consent_disclosure | Consent & Disclosure Module | compliance | mvp_active |
| privacy_data_erasure | Privacy / Data Erasure Module | compliance | mvp_active_legal_gated |
| taxonomy_classification | Taxonomy & Classification Module | capability | mvp_active |
| professional_eligibility | Professional Eligibility Module | compliance_domain_gate | mvp_active |
| trust_verification_screening | Trust Verification / Screening Module | compliance_trust_capability | mvp_active_legal_gated |
| marketplace_supply | Marketplace Supply Module | domain | mvp_active |
| gig_demand | Gig / Demand Module | domain | mvp_active |
| transaction_order | Transaction / Order Module | domain | mvp_active |
| payment_payout_tax | Payment / Payout / Tax Module | capability_compliance | mvp_active_legal_gated |
| booking_calendar | Booking & Calendar Module | domain_capability_hybrid | mvp_active |
| video_session | Video Infrastructure Module | capability | mvp_active |
| organization_hiring | Organization Hiring Module | domain | mvp_active |
| job_compliance | Job Compliance Module | compliance | mvp_active_legal_gated |
| candidate_application_resume_privacy | Candidate Application & Resume Privacy Module | domain_compliance_hybrid | mvp_active |
| job_interview | Job Interview Module | domain_capability_hybrid | mvp_active |
| messaging | Messaging Module | capability | mvp_active |
| notification | Notification Module | capability | mvp_active |
| media_file_access | Media / File Access Module | capability_compliance_support | mvp_active |
| search_public_visibility | Search / Public Visibility Module | capability | mvp_active |
| review_dispute | Review / Dispute Module | domain_compliance_support | mvp_active |
| content_moderation_legal_notice | Content Moderation & Legal Notice Module | compliance_ops | mvp_active_legal_gated |
| audit_event_ledger | Audit / Event Ledger Module | capability_ops_compliance_support | mvp_active |
| admin_review_compliance_hold | Admin Review / Compliance Hold Module | ops_compliance | mvp_active |
| sweepstakes_prize | Sweepstakes / Prize Module | compliance_feature_ecosystem | mvp_active_legal_gated |
| gamification_rewards | Gamification / Rewards Module | feature_compliance | mvp_active_legal_gated |
| healthcare_regulated_services | Healthcare / Regulated Services Module | compliance | mvp_active_legal_gated |
| location_safety | Location Safety Module | compliance | mvp_active |
| ai_taxonomy | AI Taxonomy Module | capability | mvp_active |
| observability_ops | Observability / Ops Module | ops_capability | mvp_active |
| digital_goods_access | Digital Goods Access Module | domain_capability_compliance_hybrid | mvp_active_legal_gated |
| customer_buyer_profile | Customer / Buyer Profile Module | domain_actor_profile | mvp_active |
| track_subscription_entitlement | Track Subscription & Entitlement Module | commercial_policy_capability | mvp_active |

---

## Platform Operating Model

```text
One Workin Ants application
→ many Users
→ actor profiles and organization memberships
→ track plans, subscriptions, and entitlement grants
→ marketplace supply, customer demand, hiring workflows, delivery workflows
→ compliance, privacy, audit, moderation, observability, and incentive rails
```

A single `User` may have multiple roles or actor contexts, but those contexts are not the same thing:

```text
User = account identity
CustomerProfile = buyer/customer identity
ProfessionalProfile = seller identity
CandidateProfile = applicant identity
OrganizationMember = role inside one hiring Organization
```

The platform should always ask which actor context is being used before allowing an action.

---

## Account Tracks and Entitlements

Workin Ants uses track subscriptions and entitlement grants as commercial policy truth.

Expected track lanes include:

- Customer / buyer track
- Professional / seller track
- Candidate / applicant track
- Organization / hiring track
- Platform/admin/support track

Plans, prices, grants, usage events, and counters live in the Track Subscription & Entitlement module.

Feature modules consume entitlement decisions but do not own plan truth.

Examples:

- A Professional plan may allow selling, change commission rates, enable live streaming, unlock custom domain support, or allow internal ads.
- A Customer plan may waive buyer-side transaction fees or provide priority scheduling.
- A Candidate plan may increase application limits, enable application view tracking, or boost candidate search visibility.
- Search may project boost metadata, but it does not own boost truth.
- Orders may snapshot buyer fee waiver or professional commission rules, but they do not own subscription truth.
- Delivery modules may unlock live video or digital access after entitlement and order gates pass, but they do not own plan truth.

Avoid these names:

```text
isPremium
canBoost
hasProPlan
buyerFeeWaivedBoolean
commissionRateInProfile
applicationsLeftAsTruth
```

Use:

```text
TrackSubscription
TrackEntitlementGrant
TrackUsageEvent
TrackUsageCounter
TrackPlanEntitlement
```

---

## Users and Actors

## Base User

The base authenticated account. A `User` can sign in, hold platform roles, accept consent, receive notifications, and become attached to actor profiles. It should not be overloaded as a seller, candidate, customer, or organization.

## Customer / Buyer

A customer acts through `CustomerProfile`. The customer can browse, post Gigs, purchase Offerings, create Orders, hold bookings, receive digital downloads, leave reviews, open disputes, and consume buyer-side track entitlements.

## Professional / Seller

A professional acts through `ProfessionalProfile`. The professional can create Offerings, respond to Gigs, receive Orders, schedule paid services, deliver files or courses, receive Reviews, manage payout readiness, and consume professional-track entitlements.

## Candidate / Applicant

A candidate acts through `CandidateProfile`. The candidate can apply to Jobs, upload resumes, appear in privacy-safe candidate search where permitted, use application limits, and participate in JobInterviews.

## Organization

An organization is a hiring entity. It posts Jobs, manages OrganizationMembers, reviews JobApplications, accesses resumes through authorized controls, and schedules interviews. It does not sell Offerings.

## Organization Member

An organization member is a User acting inside one Organization. Their OrganizationRole determines organization-scoped hiring authority, but Role / Authority interprets permissions.

## Platform Admin / Support

A platform admin or support actor uses server-side authority checks, audit logs, moderation tools, compliance holds, and ops dashboards. Admin/support access must not bypass healthcare redaction, financial step-up, privacy rules, or sensitive access audit.

---

## Pages and Route Families

The exact route structure may evolve, but the MVP should roughly organize around these page families.

### Public and Authentication

```text
/
→ Public landing or product entry

/sign-in
→ User authentication

/sign-up
→ Account creation with age gate and default profile/track provisioning

/invite
→ Invitation acceptance where needed

/forgot-password
→ Recovery request

/reset-password
→ Password reset

/recovery/phone-change
→ Changed-phone or lost-access recovery flow

/legal/terms
→ Terms and disclosure surfaces

/legal/privacy
→ Privacy policy

/legal/sweepstakes/[drawingId]
→ Official rules / AMOE path where active
```

### Main App Shell

```text
/app
→ Actor-aware dashboard / profile switcher

/app/account
→ User account, security, consent, notifications, subscriptions

/app/account/security
→ Passkeys, MFA, recovery, security events

/app/account/subscription
→ Current track, plan, billing portal, entitlement summary

/app/account/privacy
→ Privacy requests, export, deletion/erasure status
```

### Customer / Buyer Workspace

```text
/customer
→ Customer overview

/customer/gigs
→ Posted Gigs and demand history

/customer/gigs/new
→ Create a Gig

/customer/orders
→ Orders as buyer

/customer/bookings
→ Upcoming and past bookings

/customer/downloads
→ Digital goods and course access

/customer/reviews
→ Reviews left or pending

/customer/disputes
→ Buyer-side disputes
```

### Professional Workspace

```text
/professional
→ Professional readiness overview

/professional/profile
→ ProfessionalProfile details and status

/professional/offerings
→ Offering inventory

/professional/offerings/new
→ Create Offering

/professional/offerings/[offeringId]
→ Offering edit/detail

/professional/gig-responses
→ Gig responses and assignments

/professional/orders
→ Orders as seller

/professional/bookings
→ Availability, bookings, calendar sync

/professional/payouts
→ Balance projection, payout requests, transfers

/professional/tax
→ Tax profile and documents

/professional/verification
→ Verification requirements/checks/trust badges

/professional/healthcare
→ Healthcare compliance profile, BAA, data boundaries where applicable
```

### Marketplace / Discovery

```text
/marketplace
→ Public discovery entry

/marketplace/offerings
→ Offering search

/marketplace/professionals
→ Professional search

/gigs
→ Public Gig discovery

/jobs
→ Public Job discovery

/organizations
→ Public Organization discovery where applicable
```

### Organization Hiring

```text
/org
→ Organization switcher / overview

/org/[organizationId]
→ Hiring dashboard

/org/[organizationId]/jobs
→ Job inventory

/org/[organizationId]/jobs/new
→ Create Job

/org/[organizationId]/jobs/[jobId]
→ Job detail and compliance state

/org/[organizationId]/applications
→ Applicant tracking

/org/[organizationId]/applications/[applicationId]
→ Application/resume detail

/org/[organizationId]/interviews
→ JobInterview scheduling and history

/org/[organizationId]/settings
→ Organization users, roles, settings, feature access
```

### Candidate Workspace

```text
/candidate
→ Candidate overview

/candidate/profile
→ CandidateProfile detail

/candidate/applications
→ Submitted applications

/candidate/applications/[applicationId]
→ Application detail

/candidate/resume
→ Resume upload, parse result, privacy controls

/candidate/interviews
→ Interview schedule and video access

/candidate/subscription
→ Candidate plan, application limits, search boost, view tracking
```

### Messaging and Notifications

```text
/messages
→ Thread list

/messages/[threadId]
→ Context-bound conversation

/notifications
→ Notifications and delivery preferences
```

### Admin / Compliance / Ops

```text
/admin
→ Admin overview

/admin/users
→ Users, roles, security/admin support

/admin/profiles
→ Customer, Professional, Candidate, Organization actor review

/admin/taxonomy
→ Domains, categories, tags, AI suggestions

/admin/verification
→ Verification checks, packages, adverse-action workflows

/admin/healthcare
→ Healthcare profiles, BAAs, data boundaries, redaction policy

/admin/moderation
→ Reports, legal notices, moderation cases

/admin/holds
→ Compliance holds and review queues

/admin/audit
→ AuditEvent and AccessAuditLog review

/admin/ops
→ SystemEvent, IntegrationFailure, QueueJob, OpsIncident

/admin/search
→ Search projection/debug/reindex tools

/admin/subscriptions
→ Track plans, entitlement definitions, subscriptions, grants, usage
```

### Technical Endpoints

```text
/api/health
→ Application health

/api/webhooks/stripe
→ Stripe payments, Connect, Billing, tax, subscription events

/api/webhooks/cronofy
→ Calendar connection/free-busy/writeback events

/api/webhooks/video
→ Mux/Agora/Daily provider events

/api/webhooks/email
→ Email delivery/bounce events if provider supports it

/api/webhooks/sms
→ SMS delivery/inbound events if SMS provider supports it

/api/search/reindex
→ Admin/system reindex path

/api/uploads/presign
→ Server-side signed upload route

/api/media/access-grant
→ Short-lived signed file access route

/api/digital/download-grant
→ Short-lived digital download grant route

/api/video/playback-grant
→ Short-lived course playback grant route
```

---

## Navigation

Navigation should be actor-aware and permission-aware, but hidden navigation is never authorization.

### Primary App Navigation

```text
Overview
Marketplace
Gigs
Orders
Bookings
Messages
Notifications
Account
```

### Customer Navigation

```text
Customer Overview
My Gigs
Orders
Bookings
Downloads / Courses
Reviews
Disputes
Subscription / Perks
```

### Professional Navigation

```text
Professional Overview
Profile Readiness
Offerings
Gig Responses
Orders
Bookings / Availability
Media / Delivery
Verification
Healthcare
Payouts
Tax
Subscription / Seller Plan
```

### Candidate Navigation

```text
Candidate Overview
Profile
Applications
Resume
Interviews
Search Visibility
Subscription / Application Limits
```

### Organization Navigation

```text
Organization Overview
Jobs
Applications
Candidates
Interviews
Members
Settings
Feature Access
```

### Admin Navigation

```text
Users and Actor Profiles
Organizations
Taxonomy
Search
Verification
Healthcare
Payments / Payouts / Tax
Moderation and Legal Notices
Compliance Holds
Privacy Requests
Audit and Sensitive Access
Subscriptions and Entitlements
Operations
```

---

## Core User Flows

## Flow 1 — Account Creation and Actor Branching

1. A person starts registration.
2. Identity & Access applies age-gate requirements before account creation when active.
3. Supabase Auth creates the authentication identity.
4. Workin Ants creates the base `User`.
5. Default security profile and account records are created.
6. Default actor branches may be provisioned according to product rules.
7. `CustomerProfile` can be created as the buyer/customer actor lane.
8. The user may later create or activate `ProfessionalProfile` or `CandidateProfile`.
9. Organization membership is created only through Organization workflows.
10. Track subscription/entitlement defaults are seeded where required.
11. Consent records are captured as `ConsentLog`, not as loose booleans.

## Flow 2 — Professional Onboarding and Selling Readiness

1. A User starts Professional onboarding.
2. The platform creates or resumes a `ProfessionalProfile`.
3. The user selects categories/tags or receives AI suggestions.
4. Taxonomy determines whether healthcare, verification, or high-risk gates apply.
5. Trust Verification creates required `VerificationRequirement` and `VerificationCheck` workflows.
6. FCRA/background checks require standalone consent and adverse-action handling if restrictive.
7. Healthcare-sensitive supply requires `HealthcareComplianceProfile`, `BaaAgreement`, and healthcare data boundaries.
8. Payment/Payout/Tax collects payout account, KYC, and tax readiness through provider-backed records.
9. Track entitlements determine seller plan, selling access, commission policy, live-streaming access, custom domain, internal ads, or other professional perks.
10. Professional Eligibility composes readiness without owning every proof record.
11. Marketplace Supply allows public Offering activation only after required gates pass.
12. Search receives `SearchUpsertEvent` only when the public projection is safe.

## Flow 3 — Offering Creation and Publication

1. A Professional creates an `Offering`.
2. The Offering is shaped as service, product, course, or bundle.
3. `ServiceDetails`, `ProductDetails`, or `CourseDetails` define offering-specific behavior.
4. `PricingTier` defines purchasable price choices.
5. Taxonomy/category tags are attached.
6. Media/File Access validates uploads and controls file access.
7. Digital Goods Access attaches policies for downloads, courses, child-directed controls, license/refund terms, and accessibility assets where needed.
8. Video Infrastructure handles course/video assets and signed playback if needed.
9. Professional Eligibility checks profile, verification, healthcare, payout, tax, holds, and entitlement requirements.
10. Active, compliant, public Offerings can be indexed by Search.

## Flow 4 — Customer Gig to Order

1. A CustomerProfile posts a `Gig`.
2. The Gig receives taxonomy, visibility, media, and location handling.
3. Professionals respond through `GigResponse`.
4. Professional Eligibility checks whether the Professional can respond or accept.
5. The Customer selects a response.
6. `GigAssignment` records the accepted relationship.
7. Transaction / Order creates or updates the `Order`.
8. Agreements, pricing, buyer fee waivers, and professional commission snapshots are attached where required.
9. Stripe/payment rails confirm payment, but the `Order` remains transaction truth.
10. Booking, media, video, or digital delivery modules unlock only after order/entitlement gates pass.
11. Review or Dispute workflows attach to the Order after outcome.

## Flow 5 — Direct Offering Purchase to Order

1. A Customer selects an active, compliant `Offering`.
2. The Customer selects a `PricingTier`.
3. Track entitlements may apply buyer fee waiver or priority access.
4. Payment/Payout/Tax calculates applicable sales tax through provider-backed records.
5. Transaction / Order creates an `Order`.
6. Agreement/e-sign gates run where required.
7. Stripe confirms payment through webhook.
8. `OrderEvent` records lifecycle changes.
9. Delivery modules provide booking, file, video, or digital access.
10. Payment/Payout/Tax updates professional balance projection and payout eligibility.

## Flow 6 — Paid Service Booking

1. An entitled Order requires a live service.
2. Booking & Calendar checks `AvailabilityRule` and `BusyWindow`.
3. Calendar connection consent and free/busy privacy boundaries are respected.
4. Booking creates a `BookingHold` and `BookingSlotLock`.
5. Order and agreement gates complete.
6. The hold becomes a `Booking`.
7. Calendar writeback, video room creation, notifications, and downstream orchestration are recorded.
8. Location Safety reveals exact/sensitive location only after the required gate.
9. Video Infrastructure creates tokenized room access if needed.

## Flow 7 — Digital Product or Course Delivery

1. An Order grants access to a digital product or course.
2. Digital Goods Access checks license/refund terms acceptance.
3. Media/File Access stores private files and produces short-lived access grants.
4. Video Infrastructure produces signed playback grants for course videos.
5. Accessibility assets are attached separately from video/file source truth.
6. Download/playback events are recorded.
7. Public permanent URLs are avoided.
8. Moderation/legal workflows can freeze access if DMCA or illegal-content workflow requires it.

## Flow 8 — Organization Hiring

1. A User creates or joins an Organization.
2. OrganizationMember gives the user an organization-scoped role.
3. Organization creates a Job.
4. Job Compliance checks pay transparency, EEOC, fair-chance/ban-the-box, and salary/benefits disclosure rules.
5. Search indexes only Jobs that pass public visibility rules.
6. CandidateProfiles apply through JobApplications.
7. Resume files stay private through Media/File Access.
8. ResumeParseResult extracts metadata but does not make hiring decisions.
9. OrganizationMembers view resumes only through authorized access, creating ResumeAccessLog and possibly AccessAuditLog.
10. JobInterview handles hiring-side interview lifecycle.
11. Video Infrastructure provides meeting rooms where needed.

## Flow 9 — Messaging and Notification

1. A business workflow creates a need to communicate or alert.
2. Messaging creates or uses a context-bound Thread.
3. ThreadParticipant controls who may read/write messages.
4. MessageMedia attaches MediaAsset files with proper access rules.
5. Notification creates alerts over email, SMS, in-app, or push.
6. NotificationDelivery records provider attempts.
7. Notification payloads avoid sensitive message bodies, PHI, resume content, tax data, OTPs, or contract text.
8. Business modules own the event; communication rails carry it.

## Flow 10 — Privacy Request and Data Erasure

1. A User submits a PrivacyRequest.
2. Privacy / Data Erasure verifies and classifies the request.
3. DataErasureJob orchestrates cross-service actions.
4. DataErasureTarget records each target.
5. DataRetentionExemption documents retained tax, contract, security, dispute, fraud, or legal records.
6. Media, Search, Messaging, Payment, Video, Subscription, and other modules execute erasure/export where allowed.
7. The platform preserves proof that the privacy workflow ran.

## Flow 11 — Moderation, Legal Notice, and Compliance Hold

1. A user, admin, rights-holder, or authority creates a Report or LegalNotice.
2. Content Moderation opens a ModerationCase.
3. Evidence is preserved before destructive action.
4. ModerationAction hides, freezes, restores, de-indexes, disables access, or routes further review.
5. ComplianceHold blocks target actions where needed.
6. Audit/Event Ledger records important actions.
7. Search and Media execute projection/file-access changes.
8. Notification alerts affected parties where required.
9. Ops tracks provider failures or broken workflow execution.

## Flow 12 — Subscription, Entitlement, and Usage

1. A User selects a track plan.
2. Stripe Billing or Checkout creates/updates provider state.
3. Webhooks update `TrackSubscription`.
4. Plan mappings create or revoke `TrackEntitlementGrant` records.
5. Feature modules call server-side entitlement lookup.
6. Usage-limited actions write `TrackUsageEvent`.
7. Counters update in `TrackUsageCounter`.
8. Monthly or period resets run through workers.
9. Search reindexes boost-related entitlement changes.
10. Orders snapshot fee-waiver or commission policy where necessary.
11. Feature modules never store standalone premium booleans.

## Flow 13 — Incentives, Rewards, and Prizes

1. A GamificationRule reacts to an allowed event.
2. PointLedgerEntry records earned/spent/reversed points.
3. Leaderboards and point balances are projections from ledgered activity.
4. Users redeem Rewards through RewardRedemption.
5. Sweepstakes entries use PrizeEntry and SweepstakesEntryMethod.
6. Free/AMOE entry must remain separate and equivalent where required.
7. PrizeWinning records winners.
8. Tax and ComplianceHold gates can block prize or reward fulfillment.
9. Points, rewards, and prizes remain separate concepts.

---

## Data Architecture

The Prisma schema is the executable database shape. This overview lists key nouns and source-of-truth meanings. The full schema and `architecture.md` should be used for implementation-level relationships, fields, enums, and constraints.

| Schema / Parent Noun | Project Meaning |
| --- | --- |
| User | Base account identity. User is not the seller, applicant, buyer, or organization identity by itself. It anchors authentication and account-level audit. |
| CustomerProfile | Buyer/customer actor profile. It represents the customer lane for Gigs, Orders, Bookings, Reviews, Disputes, and buyer-side subscriptions or perks. |
| ProfessionalProfile | Seller identity. A User must have a ProfessionalProfile before they can sell Offerings, respond to Gigs commercially, receive Orders, or become payout-ready. |
| CandidateProfile | Applicant identity. It supports formal job applications, resume privacy, candidate search projection, and hiring-side workflows. |
| Organization | Hiring entity. It posts Jobs and manages recruiting workflows. It does not sell Offerings. |
| OrganizationMember | A User’s membership and role inside an Organization. Organization Hiring owns the row; Role / Authority interprets permissions. |
| ConsentLog | Versioned proof that a User accepted a disclosure, agreement, consent, or policy. It is proof, not permission logic. |
| TrackPlan | Commercial plan catalog entry for a user/account track. It defines what can be sold, metered, granted, or billed. |
| TrackSubscription | A User/profile/track subscription enrollment and lifecycle record, usually connected to Stripe Billing. |
| TrackEntitlementGrant | The source of truth for active plan permissions, perks, limits, boosts, fee waivers, commissions, and feature access. Feature modules consume it; they do not store local premium booleans. |
| TrackUsageEvent | A proof record that something consumed a plan-limited entitlement, such as an application submission or premium action. |
| TrackUsageCounter | A usage projection/counter for plan limits. It supports fast checks, but usage events remain important proof. |
| TaxonomyDomain | Top-level classification vocabulary. |
| TaxonomyCategory | Middle classification vocabulary. It can trigger healthcare, verification, high-risk, or visibility rules. |
| TaxonomyTag | Specific classification label used for discovery, filtering, matching, and compliance triggers. |
| AiSuggestion | AI-proposed classification that must be validated before becoming accepted taxonomy truth. |
| SearchUpsertEvent | Search projection queue truth. It tells workers to update or remove Typesense/search projections. |
| Offering | Sellable supply item created by a ProfessionalProfile. It can be a service, product, course, or bundle. |
| ServiceDetails | Service-specific shape for an Offering. |
| ProductDetails | Product-specific shape for an Offering. |
| CourseDetails | Course-specific shape for an Offering. |
| PricingTier | Purchasable price option for an Offering. |
| Gig | Customer/User-created paid public request. It is demand, not supply and not employment. |
| GigResponse | Professional response/proposal to a Gig. |
| GigAssignment | Accepted relationship between a Gig and a ProfessionalProfile. It can become the source for an Order. |
| Order | Paid transaction truth for money exchanged around an Offering or GigAssignment. Stripe is a rail; Order is platform truth. |
| OrderEvent | Order lifecycle event ledger. |
| Agreement | Contract or binding agreement attached to an Order. |
| AgreementDocumentSnapshot | Immutable generated/signed agreement file proof with tamper-evident hash. |
| Review | Post-order reputation feedback. |
| Dispute | Conflict case attached to an Order that can trigger holds, refunds, messaging, and payout blocks. |
| KycVerification | Payout identity/business verification truth. It is not Trust Verification. |
| TaxProfile | Tax readiness record for payouts, prizes, rewards, and reporting. |
| PayoutAccount | External processor account a ProfessionalProfile uses to receive funds. |
| ProfessionalBalanceLedgerEntry | Internal accounting projection of processor-held available/held/released professional funds. It is not a Workin Ants wallet. |
| PayoutRequest | Professional intent to withdraw available processor-held funds. |
| PayoutTransfer | Provider-mediated attempted/completed movement of funds. |
| SalesTaxCalculation | Provider-backed checkout/order sales-tax calculation proof. |
| AvailabilityRule | Professional recurring availability pattern. |
| BusyWindow | Time block when a Professional is unavailable, often synced from calendar free/busy data. |
| BookingHold | Temporary reservation while agreement/payment/checkout gates complete. |
| Booking | Scheduled paid live-service appointment attached to an Order. |
| BookingSlotLock | Server-side atomic lock preventing overlapping paid bookings. |
| BookingVideoRoom | Video room attached to a Booking. Video Infrastructure owns room mechanics. |
| Job | Formal employment opportunity posted by an Organization. |
| JobComplianceCheck | Compliance scan/review for a Job before publication. |
| JobApplication | CandidateProfile application submitted to a Job. |
| ResumeParseResult | Parsed resume metadata. It must not become an automated hiring decision. |
| ResumeAccessLog | Resume-specific access proof. |
| CandidateSearchProjection | Privacy-safe projection for candidate search when allowed. |
| JobInterview | Hiring-side interview lifecycle attached to a JobApplication. |
| Thread | Context-bound conversation between authorized Users. |
| ThreadParticipant | User allowed to participate in or read a Thread. |
| Message | Message sent inside a Thread. |
| Notification | System alert intended for a User or Organization. |
| NotificationDelivery | A channel/provider delivery attempt for a Notification. |
| MediaAsset | Storage metadata for uploaded files. File access must be private/signed unless explicitly public-safe. |
| MediaUploadPolicy | Upload rule set for context: max size, MIME/extension allowlist, scan, scrub, storage, TTL. |
| MediaAccessGrant | Short-lived signed access grant for a private MediaAsset. |
| DigitalGoodsPolicy | Digital product/course license, refund, access TTL, and child-directed/privacy policy. |
| DigitalDownloadAsset | Paid downloadable asset attached to a digital Offering. |
| DigitalDownloadGrant | Short-lived buyer access grant for a downloadable digital asset. |
| CourseVideoAsset | Streaming-provider video asset attached to CourseDetails. |
| CourseVideoPlaybackGrant | Short-lived signed playback access grant. |
| PrivacyRequest | Formal user request for access, export, erasure, correction, or restriction. |
| DataErasureJob | Cross-service privacy workflow execution record. |
| DataErasureTarget | One target inside a DataErasureJob. |
| DataRetentionExemption | Documented reason a record cannot be erased yet. |
| FuzzyLocationCache | Derived approximate public coordinate projection for search/maps. |
| LocationReveal | Proof that exact/sensitive location was revealed or revoked under a gate. |
| Report | User/admin/rights-holder flag against a platform object. |
| LegalNotice | Formal legal/legal-adjacent notice such as DMCA, counter-notice, DSA, or law enforcement request. |
| ModerationCase | Review container for reports, legal notices, or admin concerns. |
| ModerationAction | Specific action taken during moderation/legal workflow. |
| ComplianceHold | Reusable platform stop sign that blocks target actions without replacing the source compliance fact. |
| AuditEvent | Generic audit trail for important platform actions. |
| AccessAuditLog | Sensitive access proof for reads, downloads, redactions, blocks, joins, and sensitive workflow access. |
| SystemEvent | Operational event for diagnosing system behavior without becoming business truth. |
| IntegrationFailure | Operational failure/degradation record for external integrations. |
| QueueJob | Operational visibility record/projection for worker jobs and retries. |
| OpsIncident | Grouped operational incident for support/diagnostics. |
| GamificationProgram | Configured points/challenges/leaderboards/rewards system. |
| PointLedgerEntry | Ledger of earned/spent/reversed/expired/adjusted points. Do not use mutable balance as truth. |
| Reward | Redeemable benefit. |
| RewardRedemption | User claim of a real platform reward. |
| PrizeDrawing | Giveaway/sweepstakes/chance-based drawing container. |
| SweepstakesEntryMethod | Entry method, including free/AMOE routes. |
| PrizeEntry | One user entry into a PrizeDrawing. |
| PrizeWinning | Record that a user won a prize. |
| HealthcareComplianceProfile | Healthcare lane readiness record for a ProfessionalProfile. |
| BaaAgreement | Business Associate Agreement proof record. |
| HealthcareDataBoundary | Marker that a target contains or belongs to healthcare-sensitive data. |
| HealthcareAdminAccessPolicy | Policy for allowing, redacting, or blocking admin access to healthcare-sensitive payloads. |
| VerificationRequirement | Rule declaring required verification checks for category/tag/offering/gig/job. |
| VerificationCheck | Auditable trust, credential, background, DMV, identity, or license screening truth. |
| VerificationConsent | Standalone screening consent linkage. |
| ProfessionalLicenseCredential | Credential/license verification record. |
| TrustBadge | Display projection derived from verification state. |
| FcraAdverseActionWorkflow | Pre-adverse/final-adverse workflow state for restrictive background-check outcomes. |

---

## Features In Scope

## Identity, Access, Consent, and Entitlements

- Supabase Auth-backed User identity
- Actor profile branching
- Role and authority checks
- Organization membership permissions
- Thread participant authority
- Age-gate support
- MFA/passkey/step-up readiness
- Changed-phone recovery flow
- Consent/version proof
- Track plans
- Track subscriptions
- Entitlement grants
- Usage events and counters
- Stripe Billing/Checkout/customer portal integration
- Subscription webhook handling

## Marketplace Supply

- ProfessionalProfile lifecycle
- Offering creation and publication
- Services, products, courses, and bundles
- Pricing tiers
- Taxonomy/category/tag attachments
- Publish eligibility gates
- Trust and healthcare requirements
- Seller entitlement checks
- Search-safe public projection

## Customer Demand and Commerce

- CustomerProfile buyer lane
- Gig creation
- Professional Gig responses
- Accepted Gig assignments
- Direct Offering purchases
- Orders as transaction truth
- Order events
- Agreements and e-sign proof
- Reviews
- Disputes
- Refund status attachment
- Buyer fee-waiver and commission snapshots

## Payment, Payout, and Tax

- Stripe payment rail integration
- Stripe Connect payout path
- Webhook dedupe
- KYC tracking
- Tax profile and documents
- Tax year summaries
- Payout accounts
- Balance projections
- Payout requests
- Payout transfers
- Sales tax calculation records
- Marketplace facilitator tax posture where applicable
- Financial step-up access support

## Booking, Calendar, Video, and Delivery

- Availability rules
- Busy windows
- Calendar connections
- Calendar consent/free-busy boundaries
- Booking holds
- Atomic slot locks
- Bookings
- Booking orchestration
- Video rooms
- Course video assets
- Signed playback grants
- Private media storage
- Upload validation/scanning/processing
- Digital goods policies
- Digital download grants
- Course accessibility assets
- Child-directed product controls

## Organization Hiring and Candidate Pipeline

- Organization lifecycle
- OrganizationMember roles
- Job creation and lifecycle
- Job compliance checks
- Pay transparency, EEOC, and fair-chance finding support
- CandidateProfile lifecycle
- JobApplications
- Resume upload and parsing
- Resume access logs
- Candidate search projection
- JobInterviews
- Candidate subscription limits/search boost/view tracking where entitled

## Communication

- Context-bound Threads
- ThreadParticipants
- Messages
- MessageMedia
- Notifications
- Notification subscriptions
- Notification delivery attempts
- Web push/PWA readiness
- Privacy-safe notification payloads

## Privacy, Safety, Moderation, Audit, and Ops

- Privacy requests
- Data erasure/export jobs
- Retention exemptions
- Fuzzy location
- Exact location reveal gates
- Reports
- Legal notices
- Moderation cases
- Moderation actions
- Compliance holds
- Generic audit events
- Sensitive access logs
- System events
- Integration failures
- Queue visibility
- Ops incidents

## Incentives, Rewards, and Prizes

- Gamification programs
- Rules
- Point ledger
- Challenges
- Leaderboards
- Rewards
- Reward redemptions
- Sweepstakes/prize drawings
- AMOE/free entry methods
- Prize entries
- Prize winnings
- Prize/reward tax support

---

## Features Out of Scope for Initial MVP

These may exist later, but should not be assumed in the first build unless moved into scope.

- Native mobile apps
- Full enterprise SSO beyond planned identity provider boundaries
- True legal escrow or Workin Ants-held wallet/custody
- Custom tax calculator replacing Stripe Tax/Avalara/provider-backed tax
- Custom video hosting infrastructure
- Full custom ATS competing with enterprise recruiting suites
- Automated hiring decisions from resume parsing
- Automated legal judgment for job compliance, DMCA, FCRA, healthcare, or sweepstakes
- Unreviewed AI classification becoming platform truth
- Public permanent URLs for paid digital goods or sensitive files
- Full moderation/legal department tooling beyond structured MVP intake/workflow
- Advanced fraud/risk engine beyond basic holds, logs, and provider signals
- Full multi-region tax/remittance implementation without legal review
- Complex algorithmic ranking marketplace optimization
- Social-network-style feed
- Real-time collaborative course/content editor
- Public candidate resumes by default
- General wallet, stored balance, or escrow models
- General `isPremium` feature flags scattered through feature modules
- Healthcare workflows without BAA/vendor/legal review
- Comprehensive international compliance coverage without jurisdiction-specific legal review

---

## Tech Stack

The exact implementation stack may evolve, but current architecture points to the following technologies.

### Application

- Next.js App Router
- React
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui
- Radix UI primitives
- Zod for runtime validation
- Prisma for database access

### Data, Identity, and Authorization

- Supabase PostgreSQL
- Supabase Auth
- Supabase Row-Level Security
- Postgres helper functions
- Server-side authorization utilities
- Service-role server actions only where appropriate
- Policy test suite

### Payments, Payouts, Tax, and Subscriptions

- Stripe
- Stripe Connect
- Stripe Billing
- Stripe Checkout
- Stripe Customer Portal
- Stripe webhooks with signature verification
- Stripe Tax
- Avalara optional later
- Provider-backed tax-code mapping
- Webhook idempotency records

### Calendar and Scheduling

- Cronofy
- Nylas optional if chosen later
- Calendar webhooks
- Free/busy access mode where possible
- UTC storage
- Timezone display utilities such as Luxon or date-fns-tz
- Postgres row-level transactions
- Postgres overlap/exclusion constraints

### Video

- Agora SDK / Agora token server
- Daily.co optional for live video
- Mux Video API
- Mux signed playback / JWT playback access
- Mux webhooks
- Healthcare-capable/BAA-capable vendor configuration only after review

### Media and Storage

- Cloudflare R2
- Cloudflare Workers
- S3-compatible AWS SDK
- Presigned upload/download URLs
- Private object keys
- `file-type` for binary MIME/signature inspection
- `sharp` for image processing and metadata stripping
- Optional ClamAV or scanning provider

### Search and AI

- Typesense
- Search API
- Index worker
- Backfill worker
- Search debug/admin viewer
- AWS Bedrock for taxonomy/classification suggestions
- Prompt templates
- JSON schema validation
- Zod validation for AI outputs

### Messaging and Notification

- Supabase Realtime
- Email provider
- SMS provider
- Twilio Verify or equivalent SMS OTP provider
- Web Push
- W3C Push API
- Web Notifications API
- Service Worker API
- Firebase Cloud Messaging
- OneSignal or WonderPush optional
- VAPID keys
- PWA manifest and iOS PWA guidance

### Observability and Operations

- Sentry
- Structured logger
- Request IDs
- Queue dashboard
- Health routes
- Metrics
- Admin ops dashboard
- Integration failure tracking
- System event logging
- Ops incident records

### Background Work

- Queue/worker system
- Cron/periodic jobs
- Idempotency keys
- Webhook dedupe processors
- Monthly usage reset worker
- Search reindex worker
- Privacy erasure worker
- Tax/reporting workers
- Media processing workers
- Notification cleanup workers

### Testing

- Type checking
- Linting
- Unit tests
- Integration tests
- Policy/authorization tests
- Playwright E2E tests
- Webhook idempotency tests
- Cross-tenant access tests
- File upload security tests

---

## Analytics and Product Events

Analytics events measure product usage and operational health. They do not replace audit records, lifecycle events, compliance proof, or source-of-truth schemas.

Do not send secrets, PHI, resume bodies, private message content, tax data, full contract text, OTPs, raw identity documents, or unnecessary personal data to product analytics.

### Identity and Account

```text
auth.sign_in_succeeded
auth.sign_in_failed
auth.sign_up_started
auth.age_gate_passed
auth.age_gate_blocked
auth.invitation_accepted
account.security_updated
account.passkey_registered
account.step_up_succeeded
account.recovery_started
account.recovery_completed
```

### Actor Profiles

```text
customer_profile.created
professional_profile.created
professional_profile.activated
candidate_profile.created
organization.created
organization_member.added
organization_member.role_changed
```

### Subscription and Entitlement

```text
track_plan.viewed
track_subscription.started
track_subscription.updated
track_subscription.cancelled
track_entitlement.granted
track_entitlement.revoked
track_usage.recorded
track_usage.limit_reached
billing.portal_opened
```

### Marketplace and Demand

```text
offering.created
offering.published
offering.paused
gig.created
gig.published
gig_response.created
gig_assignment.accepted
search.result_clicked
```

### Orders, Payment, and Payout

```text
order.created
order.awaiting_agreement
order.payment_started
order.payment_confirmed
order.completed
order.disputed
order.refunded
agreement.generated
agreement.signed
payout_request.created
payout_transfer.succeeded
payout_transfer.failed
sales_tax.calculated
```

### Booking, Delivery, Media, and Video

```text
booking_hold.created
booking.confirmed
booking.cancelled
calendar.connected
calendar.sync_failed
media.upload_started
media.validation_failed
media.scan_failed
media.ready
digital_download_grant.created
digital_download.used
course_playback_grant.created
video_room.created
video_join_token.issued
```

### Hiring

```text
job.created
job.compliance_check_started
job.compliance_blocked
job.published
job_application.submitted
resume.uploaded
resume.viewed
candidate_search_projection.updated
job_interview.scheduled
job_interview.completed
```

### Communication

```text
thread.created
message.sent
notification.created
notification.delivery_succeeded
notification.delivery_failed
push_subscription.created
push_subscription.revoked
```

### Privacy, Moderation, Audit, and Ops

```text
privacy_request.created
data_erasure_job.started
data_erasure_job.completed
location_reveal.created
report.created
legal_notice.created
moderation_case.opened
moderation_action.applied
compliance_hold.created
compliance_hold.released
access_audit.recorded
integration_failure.created
queue_job.failed
ops_incident.opened
ops_incident.resolved
```

### Incentives, Rewards, and Prizes

```text
point_ledger_entry.created
challenge.joined
challenge.completed
reward_redemption.created
reward_redemption.fulfilled
prize_drawing.created
prize_entry.created
prize_winning.created
prize_winning.fulfilled
```

---

## Success Criteria

## Platform and Architecture

- The platform supports 34 Deep Modules without collapsing ownership into generic services.
- Every lifecycle has a clear owning module.
- All 10 Clusters are represented in context and build planning.
- Developers can explain whether a schema is source truth, projection, ledger, access grant, compliance proof, or operational visibility.
- No feature module stores local premium booleans instead of consuming Track Entitlement truth.
- Search remains projection, not source truth.
- Payment providers remain rails, not platform transaction truth.
- The codebase avoids `User` overload by using actor profiles.

## Identity, Authority, and Consent

- Users authenticate through Supabase Auth.
- Account identity, actor identity, organization membership, and thread participation remain distinct.
- Permissions are enforced server-side.
- Consent proof is versioned and stored in `ConsentLog`.
- Financial step-up and sensitive routes cannot be satisfied by frontend state alone.
- Age gate and changed-phone recovery have source records where enabled.

## Marketplace and Commerce

- A User cannot sell directly without ProfessionalProfile.
- Offerings can only become public when eligibility, taxonomy, verification, healthcare, payout/tax, entitlement, and hold checks allow it.
- Gigs remain demand/request truth and do not become Jobs or Offerings.
- Orders remain transaction truth across payment, agreements, delivery, reviews, disputes, refunds, and payouts.
- Buyer fee waivers and professional commission policy are snapshotted from entitlement truth.

## Payment, Payout, Tax, and Subscriptions

- Stripe webhooks are idempotent.
- Stripe success redirects are never treated as payment truth.
- Payouts use processor-held funds, PayoutRequest, PayoutTransfer, and ProfessionalBalanceLedgerEntry.
- No Wallet or Escrow models are created.
- KYC, tax profile, payout account, and sales tax are separate concepts.
- Subscription and entitlement lifecycle changes are processed through source records and audit/ops visibility.

## Delivery and Access

- Bookings use server-side availability checks, holds, and slot locks.
- Calendar sync stores minimal free/busy data where possible.
- Video rooms and playback access use short-lived tokens or grants.
- Paid digital downloads use private storage and expiring grants.
- Uploads are validated, scanned, scrubbed where needed, and stored outside public/executable paths.
- Healthcare-sensitive delivery obeys healthcare boundaries and access audit rules.

## Hiring

- Organization Hiring remains separate from marketplace commerce.
- Jobs cannot be public unless compliance visibility rules permit it.
- Resume files are private.
- Resume parsing does not make hiring decisions.
- Resume access is authorized and logged.
- Candidate subscription limits and boosts are metered through Track Usage and Entitlement records.

## Privacy, Safety, Moderation, and Compliance

- PrivacyRequest initiates formal workflows.
- DataErasureJob coordinates erasure/export/correction targets.
- Retention exemptions are explicit.
- Public search uses fuzzy location, not exact private address data.
- Exact location reveal is gated and recorded.
- Reports, LegalNotices, ModerationCases, and ModerationActions are distinct.
- ComplianceHold is the reusable stop sign across modules.
- Sensitive access writes AccessAuditLog where required.

## Operations

- Every major external integration has webhook dedupe and failure visibility.
- Background jobs expose operational state.
- Sentry/structured logs surface errors without replacing source-of-truth schemas.
- Ops incidents group meaningful operational failures.
- Logs do not expose secrets, card data, PHI, SSNs, private messages, raw resumes, or contract contents.

---

## Launch Calibration Metrics

Exact targets should be established from real usage. Initial measurement should include:

- Account signup completion rate
- Age-gate block/pass rate where enabled
- Actor profile creation rate by type
- ProfessionalProfile activation rate
- Offering publish success/failure rate
- Verification completion rate
- KYC/payout onboarding completion rate
- Tax profile completion rate
- Subscription conversion by track
- Entitlement usage by plan
- Application limit usage and limit-hit rate
- Search boost reindex success rate
- Gig creation rate
- Gig response rate
- GigAssignment conversion rate
- Order creation rate
- Checkout completion rate
- Agreement completion rate
- Booking hold-to-booking conversion rate
- Double-booking conflict rate
- Digital download grant usage rate
- Course playback grant usage rate
- Job compliance pass/block rate
- JobApplication submission rate
- Resume view/access event rate
- Notification delivery success/failure rate
- Privacy request completion time
- Search indexing lag
- Integration failure rate
- Queue retry exhaustion rate
- ComplianceHold open/release time
- Dispute rate
- Payout transfer success/failure rate
- Reward redemption rate
- Prize fulfillment/tax-block rate

---

## Source-of-Truth Boundaries

Use this table as a fast lint rule during development.

| Area | Source-of-Truth Rule |
|---|---|
| Account identity | `User`, not profile tables |
| Customer identity | `CustomerProfile`, not `User` |
| Seller identity | `ProfessionalProfile`, not `User` |
| Applicant identity | `CandidateProfile`, not `User` |
| Hiring organization | `Organization`, not `ProfessionalProfile` |
| Platform authority | `UserRole` plus Role / Authority interpretation |
| Organization authority | `OrganizationMember` plus Role / Authority interpretation |
| Thread authority | `ThreadParticipant` plus Role / Authority interpretation |
| Consent proof | `ConsentLog`, not frontend checkbox state |
| Subscription enrollment | `TrackSubscription`, not Stripe alone |
| Entitlement truth | `TrackEntitlementGrant`, not local premium booleans |
| Usage proof | `TrackUsageEvent`, not counter alone |
| Usage projection | `TrackUsageCounter`, not lifecycle truth by itself |
| Sellable supply | `Offering`, not Gig or Job |
| Public demand | `Gig`, not Offering or Job |
| Employment opportunity | `Job`, not Gig |
| Candidate application | `JobApplication`, not GigResponse |
| Transaction | `Order`, not Stripe |
| Order timeline | `OrderEvent`, not generic AuditEvent |
| Payout identity | `KycVerification`, not TrustBadge |
| Trust screening | `VerificationCheck`, not `is_verified` |
| Trust display | `TrustBadge`, not source truth |
| Healthcare lane | `HealthcareComplianceProfile` and `HealthcareDataBoundary`, not `User.is_healthcare_provider` |
| Payout intent | `PayoutRequest`, not PayoutTransfer |
| Payout execution | `PayoutTransfer`, not Order |
| Balance projection | `ProfessionalBalanceLedgerEntry`, not Workin Ants custody |
| Sales tax | `SalesTaxCalculation`, not TaxProfile |
| Scheduling | `Booking`, `BookingHold`, `BookingSlotLock`, not calendar provider state |
| Calendar webhook dedupe | `ProcessedCalendarEvent`, not AuditEvent |
| Payment webhook dedupe | `ProcessedStripeEvent`, not AuditEvent |
| Video webhook dedupe | `ProcessedVideoProviderEvent`, not AuditEvent |
| Search projection | `SearchUpsertEvent` and Typesense, not database source truth |
| File truth | `MediaAsset`, not public URLs |
| Resume-specific access | `ResumeAccessLog`, not MediaAccessGrant alone |
| Private file access | `MediaAccessGrant`, not permanent download URL |
| Digital download access | `DigitalDownloadGrant`, not ProductDetails.fileAssetId |
| Course playback access | `CourseVideoPlaybackGrant`, not public video URL |
| Privacy rights workflow | `PrivacyRequest`, not account deletion |
| Legal erasure | `DataErasureJob` / `DataErasureTarget`, not normal `deletedAt` |
| Retention exception | `DataRetentionExemption`, not “keep because maybe” |
| Location public projection | `FuzzyLocationCache`, not exact private coordinates |
| Exact location reveal | `LocationReveal`, not an address-shown flag |
| Legal notice | `LegalNotice`, not Report |
| Moderation workflow | `ModerationCase`, not ComplianceHold |
| Platform stop sign | `ComplianceHold`, not local blocked booleans |
| Generic audit | `AuditEvent`, not domain event ledgers |
| Sensitive access proof | `AccessAuditLog`, not generic logs |
| Operational failure | `IntegrationFailure`, `QueueJob`, `OpsIncident`, not business truth |
| Points | `PointLedgerEntry`, not mutable balance |
| Reward claim | `RewardRedemption`, not PrizeWinning |
| Prize entry | `PrizeEntry`, not PointLedgerEntry |
| Prize win | `PrizeWinning`, not RewardRedemption |

---

## Naming Rules and Terms to Avoid

Avoid these patterns:

```text
is_verified
is_healthcare_provider
escrow
wallet
delete user
taxApproved
canPayout as truth
backgroundPassed
reward/prize as one thing
chat delete = privacy erasure
SearchDoc as truth
isPremium
hasFeature
canBoost
applicationsLeft as truth
stripeReady
fileUrl as truth
publicPlaybackUrl
contractPdfOnly
```

Prefer these source records:

```text
VerificationCheck.status plus TrustBadge projection
HealthcareComplianceProfile plus Offering/TaxonomyCategory healthcare triggers
Processor-held funds / payment hold / pending transfer / payout transfer
ProfessionalBalanceLedgerEntry plus processor-held available balance
PrivacyRequest → DataErasureJob with retention exemptions
TaxProfile.status and TaxDocument records
Computed payout readiness from KycVerification, TaxProfile, PayoutAccount, PayoutTransfer, and ComplianceHold
FcraAdverseActionWorkflow where applicable
RewardRedemption for rewards and PrizeWinning for prizes
Message.deletedAt for product deletion and Message.erasedAt for privacy erasure
SearchUpsertEvent and Typesense projections only
TrackSubscription and TrackEntitlementGrant for plan/feature truth
TrackUsageEvent and TrackUsageCounter for metered usage
```

---

## Relationship to the Other `/context` Files

## `architecture.md`

Should contain the full cluster/module/schema ownership architecture:

- 10 Cluster map
- 34 Deep Modules
- module ownership
- key schemas
- dependencies
- compliance proof
- bridge rules
- source-of-truth boundaries

## `build-plan.md`

Should turn the architecture into phased implementation:

- foundation first
- then taxonomy/discovery
- then profiles/readiness
- then commerce
- then delivery
- then hiring
- then communication
- then guardrails and incentives
- with migration/testing/review checkpoints

## `code-standards.md`

Should define implementation rules:

- TypeScript strictness
- schema/service/action boundaries
- RLS and server authorization
- validation
- test requirements
- file/folder conventions
- prohibited shortcuts

## `library-docs.md`

Should define approved third-party usage:

- Supabase
- Prisma
- Stripe
- Cronofy
- Typesense
- Mux/Agora/Daily
- Cloudflare R2
- AWS Bedrock
- Sentry
- notification providers
- testing libraries

## `ui-tokens.md`

Should define visual system primitives:

- colors
- typography
- spacing
- radius
- shadows
- semantic states
- cluster color ideas
- dark/light behavior

## `ui-rules.md`

Should define interface behavior:

- actor switching
- cluster-aware navigation
- source-truth display
- empty states
- form rules
- admin/compliance UI
- sensitive data redaction
- accessibility

## `ui-registry.md`

Should list reusable components:

- app shell
- actor switcher
- profile status cards
- readiness cards
- entitlement banners
- order timeline
- audit table
- file access components
- moderation/admin tools
- cluster/bubble map components

## `progress-tracker.md`

Should update after every build session:

- completed work
- current feature
- decisions made
- next steps
- blockers
- affected files
- tests run
- context changes required

---

## Final Product Definition

Workin Ants is a marketplace operating system for trusted work, hiring, delivery, and digital commerce.

It connects:

```text
Account identity
→ actor profile
→ track subscription and entitlement
→ classification and discovery
→ professional supply or customer demand
→ order and agreement
→ payment, payout, and tax
→ booking, file, video, or digital delivery
→ messaging and notification
→ review, dispute, moderation, audit, privacy, and operational control
→ incentives, rewards, and prize economy
```

Its value depends on preserving clear ownership:

```text
Deep Modules own truth.
Clusters organize context.
Providers are rails.
Search is projection.
Consent is proof.
ComplianceHold is the stop sign.
TrackEntitlementGrant is commercial policy truth.
Order is transaction truth.
```

Any implementation that violates those boundaries should be treated as architectural drift.
