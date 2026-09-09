# Workin Ants Project Overview

> **Repository location:** `context/project-overview.md`  
> **Project name:** Workin Ants  
> **Project state:** Greenfield MVP architecture planning  
> **Architecture:** One multi-actor marketplace platform, one managed codebase  
> **Primary audience:** Codex, developers, reviewers, maintainers, and future AI agents  
> **Current cluster registry:** `v2.3-customer-subscription`  
> **Current Deep Module count:** 34 in the current cluster registry  
> **Legal posture:** Working architecture guide; not legal advice

---

## Purpose of This File

This file is the front door for the Workin Ants `/context` folder.

Use it to understand what Workin Ants is, who it serves, what it is trying to build, which workflows matter, and which product/architecture boundaries must not be violated.

This file is intentionally compressed. It does **not** replace:

- `architecture.md` for full cluster, Deep Module, schema, ownership, and compliance boundaries.
- `build-plan.md` for phase order and implementation sequencing.
- `library-docs.md` for provider and API usage.
- the Ubiquitous Language Pack for full glossary definitions.
- the Cluster Digestion / Handout documents for presentation-level explanations.

Agents should read this file first, then read the rest of `/context` before implementation.

---

## Source Basis

This overview is based on the current Workin Ants planning materials:

- Ubiquitous Language Pack v2.2
- Deep Module Registry / refreshed module JSON
- cleaned `schema.prisma`
- Cluster Registry `v2.3-customer-subscription`
- Compliance Inventory / Legal Homework Map
- Cluster Digestion and Individual Cluster Handout direction

The latest cluster registry preserves the 10-cluster map while adding two important foundation modules:

- `customer_buyer_profile`
- `track_subscription_entitlement`

This means the current platform model should treat `CustomerProfile` as buyer actor truth and `TrackSubscription` / `TrackEntitlementGrant` as commercial policy truth.

---

## Product Definition

Workin Ants is a trust-aware marketplace and work platform that connects customers, professionals, candidates, and hiring organizations through paid work, sellable offerings, formal jobs, bookings, digital goods, messaging, payments, verification, privacy, compliance, subscriptions, rewards, prizes, and operational controls.

The platform supports several actor branches from one base account identity:

```text
User
→ CustomerProfile for buying, posting Gigs, placing Orders, bookings, reviews, and disputes
→ ProfessionalProfile for selling Offerings, responding to Gigs, receiving Orders, and payouts
→ CandidateProfile for applying to Jobs and managing resume/application identity
→ OrganizationMember for acting inside an Organization that posts Jobs
```

Workin Ants is not only a job board, not only a gig marketplace, not only ecommerce, and not only an ATS. It is a single platform where commerce, hiring, digital delivery, compliance, public discovery, and communication are connected while remaining cleanly owned by separate source-of-truth modules.

---

## Product Promise

Workin Ants should let people safely discover, buy, sell, hire, apply, communicate, deliver, and get paid in one platform without mixing up identity, transaction truth, compliance proof, or delivery access.

The platform should make these questions answerable for any workflow:

```text
Who is acting?
Under which actor profile or organization role?
What are they trying to do?
Which source record owns the lifecycle?
Which gates must pass?
What proof must be stored?
Which downstream modules may consume the result?
```

A healthy Workin Ants build should make platform reality clear instead of relying on scattered booleans, provider objects, frontend state, or duplicated business logic.

---

## The Problem It Solves

### Before Workin Ants

A marketplace/work platform can easily collapse into unclear ownership:

- `User` gets overloaded as buyer, seller, applicant, admin, contractor, and organization member.
- `isVerified`, `isPremium`, `canPayout`, `isPaid`, and `isHealthcareProvider` booleans spread across random tables.
- Stripe, search, calendar, video, SMS, email, AI, and storage providers get treated as source of truth.
- Gigs, Jobs, Offerings, Applications, Bookings, and Orders blur together.
- Consent, privacy, verification, tax, healthcare, moderation, and audit proof live in generic logs or frontend checkbox state.
- Public search indexes stale, private, or compliance-blocked data.
- Digital goods are delivered with permanent links instead of entitlement-controlled access.
- Subscription perks leak into local `premium` flags instead of being controlled by plan and entitlement records.

### After Workin Ants

Workin Ants gives each lifecycle a clear owner:

- `User` is account identity.
- `CustomerProfile` is buyer/customer identity.
- `ProfessionalProfile` is seller identity.
- `CandidateProfile` is applicant identity.
- `Organization` is hiring entity.
- `Offering` is sellable supply.
- `Gig` is paid public demand.
- `Job` is formal hiring.
- `Order` is transaction truth.
- `Booking` is scheduling truth.
- `VerificationCheck` is trust-screening truth.
- `KycVerification`, `TaxProfile`, `PayoutAccount`, `PayoutRequest`, and `PayoutTransfer` are financial compliance truth.
- `ConsentLog` is consent/version proof.
- `PrivacyRequest` and `DataErasureJob` are privacy-rights truth.
- `SearchUpsertEvent` is search projection queue truth.
- `ComplianceHold` is the reusable platform stop sign.
- `TrackSubscription` and `TrackEntitlementGrant` are subscription/entitlement truth.

---

## Non-Negotiable Architecture Rules

1. **One owner per lifecycle.** Every lifecycle has one module that owns status changes; other modules consume state.
2. **Order is transaction truth.** Stripe and other processors are rails. `Order` and `OrderEvent` remain platform truth.
3. **User is not every identity.** Use actor branches: `CustomerProfile`, `ProfessionalProfile`, `CandidateProfile`, and `OrganizationMember`.
4. **Profile is not verification.** `VerificationCheck`, `KycVerification`, `TaxProfile`, `PayoutAccount`, and `HealthcareComplianceProfile` hold compliance truth.
5. **Consent is proof, not permission logic.** `ConsentLog` records accepted versions; feature modules own the action unlocked by that consent.
6. **ComplianceHold is the reusable stop sign.** Do not scatter local block flags across modules.
7. **Product deletion is not legal erasure.** `deletedAt` is product deletion; `erasedAt`, `PrivacyRequest`, and `DataErasureJob` belong to privacy/legal erasure.
8. **Search is projection.** Typesense/search documents are derived from source records.
9. **Healthcare is a lane, not a user type.** Trigger healthcare handling from taxonomy/offering/profile/data boundaries, not a blanket `User` flag.
10. **TrustBadge is display.** `VerificationCheck` is truth.
11. **Processor-held funds are not a wallet or escrow.** Use `ProfessionalBalanceLedgerEntry`, `PayoutRequest`, and `PayoutTransfer`.
12. **Track entitlements are policy truth.** Use `TrackSubscription` and `TrackEntitlementGrant`; do not create local premium booleans.

---

## Platform Operating Model

```text
One Workin Ants application
→ many Users
→ multiple actor branches per User
→ marketplace, hiring, subscription, delivery, compliance, and communication workflows
→ source-of-truth records owned by Deep Modules
→ Clusters used for planning, presentation, and controlled agent context
```

The platform should be built as one managed codebase with clear domain boundaries. Agents should not create separate mini-systems for payments, permissions, messaging, file access, search, subscriptions, moderation, or audit when a Deep Module already owns that responsibility.

---

## Primary Users and Actors

## Base User

A `User` is the base account identity. It handles authentication, security posture, recovery, passkeys/MFA, and platform-level role attachment. A `User` is not automatically a seller, candidate, customer, or organization actor.

## Customer / Buyer

A `CustomerProfile` represents buyer-side marketplace activity: posting Gigs, purchasing Offerings, creating Orders, booking services, receiving digital goods, reviewing, and disputing.

## Professional / Seller

A `ProfessionalProfile` is the seller identity. It creates Offerings, responds to Gigs, receives Orders, and becomes payout-eligible only after required eligibility, verification, tax, KYC, healthcare, subscription, and compliance gates pass.

## Candidate / Applicant

A `CandidateProfile` is the applicant identity for formal hiring. It applies to Jobs, submits resumes, participates in interviews, and may consume candidate-track entitlements such as application limits, boosts, and application-view tracking.

## Organization / Hiring Entity

An `Organization` is a hiring entity. It posts Jobs and manages candidate workflows. It does not sell Offerings.

## Organization Member

An `OrganizationMember` is a User acting inside one Organization with an organization-scoped role. Role interpretation belongs to Role / Authority.

## Admin / Support

Admins and support users operate moderation, compliance holds, legal notices, support review, audit visibility, and operational tooling. Admin capability does not mean unrestricted access to healthcare, financial, resume, contract, or private message data.

---

## Product Structure: 10 Clusters

Clusters are not source-of-truth owners. They are controlled context fields that group Deep Modules for planning, explanation, Bubble Map presentation, and agent work.

| Cluster | Name | Role |
| --- | --- | --- |
| CL-01 | Identity, Authority, Consent & Entitlements | Establishes actor identity, permissions, consent proof, security posture, customer/buyer profile, and subscription/entitlement policy. |
| CL-02 | Discovery, Classification & Visibility | Classifies platform objects, validates AI suggestions, and projects approved public records into search. |
| CL-03 | Professional Supply & Readiness | Turns a User’s seller ambition into a compliant, verified, financially ready ProfessionalProfile with sellable Offerings. |
| CL-04 | Customer Demand, Order & Resolution | Turns customer demand or purchases into Orders, agreements, reviews, disputes, and transaction outcome records. |
| CL-05 | Scheduling, Media & Digital Delivery | Delivers bookings, video rooms, files, course playback, and digital downloads after entitlement is established. |
| CL-06 | Organization Hiring & Candidate Pipeline | Handles Organizations, Jobs, job compliance, CandidateProfiles, applications, resumes, and interviews. |
| CL-07 | Messaging & Notification Rail | Carries conversations and alerts across workflows without owning the business event that caused them. |
| CL-08 | Privacy & Location Safety | Handles privacy requests, erasure/export workflows, retention exemptions, fuzzy public location, and exact-location reveal. |
| CL-09 | Moderation, Holds, Audit & Ops | Acts as the control tower for reports, legal notices, holds, audit logs, access logs, system failures, and incidents. |
| CL-10 | Incentives, Rewards & Prize Economy | Handles points, rewards, leaderboards, challenges, sweepstakes entries, prize drawings, and prize/reward tax coordination. |

### Clean Visual Spine

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

Guardrails:

```text
CL-08 Privacy & Location Safety
CL-09 Moderation, Holds, Audit & Ops
```

Side ecosystem:

```text
CL-10 Incentives, Rewards & Prize Economy
```

---

## Plain-English Cluster Effects

## CL-01 — Identity, Authority, Consent & Entitlements

This cluster takes an anonymous or partially known person and digests them into an authenticated account, actor branch, permission context, consent proof, and entitlement policy. It answers: who is acting, what profile/track are they acting under, what can they do, and what proof exists?

## CL-02 — Discovery, Classification & Visibility

This cluster takes raw platform objects such as Offerings, Gigs, Jobs, Organizations, Professionals, and Candidates and turns them into classified, compliant, searchable public projections.

## CL-03 — Professional Supply & Readiness

This cluster takes raw professional ambition — a User wanting to sell — and digests it through eligibility, verification, healthcare gates, marketplace supply, payout/tax readiness, and entitlement rules until what comes out is a compliant, searchable, sellable Professional Offering that can safely become an Order.

## CL-04 — Customer Demand, Order & Resolution

This cluster takes buyer demand — a Gig, accepted assignment, or direct Offering purchase — and turns it into transaction truth: an Order, agreement, events, files, reviews, disputes, refunds, and payout-affecting outcomes.

## CL-05 — Scheduling, Media & Digital Delivery

This cluster takes an established entitlement and delivers the actual thing: a booked time slot, video room, uploaded file, signed media access grant, course playback, or downloadable digital product.

## CL-06 — Organization Hiring & Candidate Pipeline

This cluster takes formal hiring intent and turns it into compliant Jobs, private applications, protected resume access, candidate pipeline state, and scheduled interviews.

## CL-07 — Messaging & Notification Rail

This cluster takes workflow events and routes the human communication around them through threads, messages, notifications, subscriptions, and delivery attempts.

## CL-08 — Privacy & Location Safety

This cluster takes sensitive personal data and exact location risk and turns them into controlled erasure/export workflows, retention decisions, fuzzy public locations, and gated exact-location reveals.

## CL-09 — Moderation, Holds, Audit & Ops

This cluster takes risk, reports, legal notices, sensitive access, provider failures, and operational problems and turns them into cases, stop signs, logs, incidents, and review queues.

## CL-10 — Incentives, Rewards & Prize Economy

This cluster takes engagement mechanics and turns them into ledgered points, rewards, challenges, leaderboards, sweepstakes entries, prize winnings, and tax-aware fulfillment without creating paid prize odds or gambling risk.

---

## Core User Flows

## Flow 1 — Account Creation and Actor Branching

A person creates a User account, passes required age/security checks, accepts required disclosures, and then branches into one or more actor profiles: CustomerProfile, ProfessionalProfile, CandidateProfile, or OrganizationMember.

## Flow 2 — Professional Onboarding and Selling Readiness

A User creates a ProfessionalProfile, selects categories/tags, completes required verification, healthcare, tax, KYC, payout, and subscription/entitlement gates, and becomes eligible to publish Offerings or respond to Gigs.

## Flow 3 — Offering Creation and Publication

A Professional creates an Offering with service/product/course details, pricing tiers, media, taxonomy, digital goods policy where needed, verification/healthcare checks where triggered, and search projection only when eligible.

## Flow 4 — Customer Gig to Order

A CustomerProfile posts a Gig. Professionals respond. The customer accepts one response. The accepted GigAssignment can become an Order after required payment/agreement steps.

## Flow 5 — Direct Offering Purchase to Order

A CustomerProfile buys an Offering. Stripe/payment provider acts as the rail, but Workin Ants records the Order as transaction truth. Required agreement, tax, fee-waiver, commission, entitlement, and delivery effects are snapshotted or linked.

## Flow 6 — Booking and Live Delivery

A paid or eligible Order can create a BookingHold, BookingSlotLock, Booking, calendar writeback, video room, notification, and location reveal where allowed.

## Flow 7 — Digital Product or Course Delivery

A paid digital good or course creates controlled download/playback grants. Files and videos remain private and are delivered through short-lived, entitlement-checked access.

## Flow 8 — Organization Hiring

An Organization creates a Job, passes job compliance gates, receives CandidateProfile applications, protects resumes, tracks application stages, and schedules interviews through the hiring lane.

## Flow 9 — Messaging and Notification

Business modules create source events. Messaging carries conversation context. Notification creates alerts and delivery attempts. Neither replaces the source business lifecycle.

## Flow 10 — Privacy, Location, Moderation, and Holds

Privacy requests, location reveals, legal notices, reports, compliance holds, audit logs, and incidents route through the guardrail clusters without replacing the source modules they affect.

## Flow 11 — Subscription, Entitlement, and Usage

A User or actor profile subscribes to a track. TrackSubscription and TrackEntitlementGrant control feature access, limits, waivers, boosts, usage metering, and revocation. Consuming modules check entitlements but do not own plan truth.

## Flow 12 — Incentives, Rewards, and Prizes

Platform activity can create point ledger entries, challenge progress, rewards, or sweepstakes entries. Chance-based prize flows stay separate from ordinary gamification and must preserve AMOE/no-purchase and tax controls.

---

## Features In Scope

## Foundation

- Authentication and account security
- MFA/passkeys and step-up sessions
- Account recovery
- Role and authority interpretation
- Consent/version proof
- CustomerProfile, ProfessionalProfile, CandidateProfile, OrganizationMember actor branching
- Track plans, subscriptions, entitlements, grants, usage events, counters, and subscription events

## Marketplace and Commerce

- Professional onboarding and readiness
- Offerings for services, products, courses, and bundles
- Gigs, responses, and assignments
- Orders as transaction truth
- Agreements, signatures, document snapshots, and access grants
- Reviews and disputes
- Stripe/payment provider integration as rails
- KYC, tax, payout accounts, payout requests, payout transfers, and sales tax calculations

## Delivery

- Availability rules, busy windows, booking holds, slot locks, and bookings
- Calendar sync boundaries
- Video rooms and course playback grants
- Media upload policy, validation, scanning, processing, and private access grants
- Digital goods policies, downloads, download grants, terms acceptance, child-directed declarations, and accessibility assets

## Hiring

- Organizations and organization membership
- Jobs and job compliance checks
- Pay transparency / EEOC / fair chance support
- Candidate profiles, job applications, resumes, resume parsing, resume access logs, candidate search projections
- Job interviews and hiring-side interview events

## Discovery and Communication

- Taxonomy domains, categories, and tags
- AI taxonomy suggestions and classification logs
- SearchUpsertEvent and Typesense projections
- Threads, messages, message media
- Notifications, subscriptions, delivery attempts, push/web/SMS/email support

## Compliance, Governance, and Ops

- Privacy requests, erasure jobs, targets, retention exemptions, and exports
- Fuzzy public location and exact location reveal
- Reports, legal notices, moderation cases, moderation actions
- Compliance holds
- Audit events and sensitive access logs
- System events, integration failures, queue jobs, ops incidents

## Incentives

- Gamification programs, rules, point ledger entries, challenges, leaderboards, rewards, and reward redemptions
- Sweepstakes drawings, entry methods, prize entries, prize winnings, and prize tax summaries

---

## Features Out of Scope for Initial MVP

The following should not be built unless later context explicitly brings them into scope:

- True Workin Ants wallet or escrow system
- Custom payment custody
- Custom tax calculator replacing Stripe Tax/Avalara/provider rails
- Fully automated legal/compliance decisioning
- Full legal drafting system
- General-purpose CRM
- Full project management suite
- Public permanent URLs for paid digital goods or private files
- Unreviewed AI classification as platform truth
- Automated hiring decisions from resume parsing
- Healthcare platform-wide mode applied to every user
- Search as source-of-truth data store
- One-off local hold/block/premium booleans inside feature modules
- Separate mini identity systems inside feature modules
- Arbitrary provider object state replacing Workin Ants source records

---

## Tech Stack Summary

## Application

- Next.js App Router
- React
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui
- Radix UI primitives
- Zod validation

## Data, Identity, and Authorization

- Supabase Auth
- Supabase PostgreSQL
- Prisma
- PostgreSQL Row-Level Security
- Server-side authorization helpers
- Postgres helper functions where appropriate
- (Developer input note) For background checks and license verifs. Certn and Checkr

## Payments, Tax, and Subscriptions

- Stripe
- Stripe Connect
- Stripe Billing
- Stripe Checkout
- Stripe Customer Portal
- Stripe Tax
- Stripe webhooks with signature verification
- Avalara or tax provider later if needed

## Search and AI

- Typesense
- Search indexing workers
- Search backfill/debug tools
- AWS Bedrock or equivalent AI provider for taxonomy/classification suggestions
- Prompt templates and JSON schema validation

## Calendar, Video, Media, and Delivery

- Cronofy for calendar sync/free-busy/writeback
- Daily.co for MVP video rooms
- AWS CHime SDK future utility cost cut(developer note)
- Mux for on-demand course video
- Cloudflare R2 for private object storage
- Presigned URLs / signed playback tokens
- Puppeteer for agreement generation
- `file-type` for binary file validation
- `sharp` for image processing and EXIF/GPS scrubbing

## Communication and Ops

- AWS SES for Email and SMS
- AWS Lambda for notifications(Developer Overide Note)
- Web Push / FCM / OneSignal or WonderPush if chosen
- Supabase Realtime for messaging where useful
- Sentry for error tracking
- Structured logging
- Queue/background worker system
- Health routes, request IDs, metrics, and admin ops dashboard

## Testing

- TypeScript type checks
- ESLint / formatting
- Vitest
- React Testing Library
- Playwright for critical journeys
- RLS / authorization tests
- Provider webhook idempotency tests

---

## Analytics and Product Events

Analytics events measure product usage. They do not replace audit records, domain events, or business source-of-truth tables.

Example event families:

```text
identity.account_created
identity.actor_profile_created
subscription.created
subscription.entitlement_granted
professional.onboarding_started
professional.offering_published
gig.created
gig.response_submitted
order.created
order.paid
booking.confirmed
digital_download.grant_created
job.created
job.application_submitted
resume.viewed
message.sent
notification.delivered
privacy_request.created
moderation_case.opened
compliance_hold.created
reward.redeemed
prize.entry_created
```

Do not send secrets, private message bodies, PHI, raw resume text, tax details, OTPs, full agreement text, or unnecessary personal data to analytics.

---

## Success Criteria

## Platform and Architecture

- Every lifecycle has a clear owning module.
- No feature module creates duplicate identity, payment, messaging, search, file, entitlement, hold, or audit systems.
- Protected workflows check actor profile, role/authority, entitlement, and compliance gates server-side.
- Source-of-truth records remain in PostgreSQL/Prisma-owned models, not provider objects or frontend state.

## Marketplace and Commerce

- Users can create the appropriate actor branch before acting in a workflow.
- Professionals cannot sell, publish, receive money, or respond to gated work before readiness gates pass.
- Customers can post Gigs, purchase Offerings, create Orders, book services, receive digital access, review, and dispute.
- Orders remain transaction truth even when Stripe, tax, delivery, review, or dispute flows are involved.

## Hiring

- Organizations can post compliant Jobs.
- Candidate applications, resume privacy, resume parsing, and interviews stay separate from Gigs and marketplace transactions.
- Candidate search and boosts are privacy-safe and entitlement-aware.

## Compliance and Safety

- Consent, privacy, verification, healthcare, tax, file access, location, moderation, and audit proof live in explicit source records.
- ComplianceHold is used as the reusable stop sign.
- Public search and public media surfaces respond to privacy, moderation, compliance, and source-status changes.

## Operations

- External provider failures are visible.
- Webhooks are idempotent.
- Queues, integrations, indexing, uploads, and background jobs have failure tracking.
- Sensitive data access is audited.
- Critical user journeys have automated tests.

---

## Launch Calibration Metrics

Initial metrics should be calibrated from real usage, not invented before launch. Start by measuring:

- Account creation completion rate
- Actor profile creation rate by type
- Professional onboarding completion rate
- Offering publication success rate
- Gig-to-response rate
- GigAssignment-to-Order rate
- Offering purchase-to-Order rate
- Booking confirmation success rate
- Digital download/playback grant success rate
- Job publication pass/fail rate
- Application submission rate
- Resume view/audit completeness
- Subscription conversion and cancellation rate
- Entitlement check failure rate
- Usage-limit hit rate
- Stripe webhook success/failure rate
- Search indexing lag and failure rate
- Privacy request completion time
- Compliance hold creation/release time
- Provider failure count by integration
- Critical Playwright journey pass rate

---

## Relationship to the Other `/context` Files

## `architecture.md`

Use this for the deep architecture: 10 Clusters, 34 Deep Modules, schema ownership, module boundaries, source-of-truth rules, dependency bridges, compliance rails, and Bubble Map interpretation.

## `build-plan.md`

Use this for the implementation sequence: phases, vertical slices, dependencies, checkpoints, and what must be built before each major workflow can work.

## `code-standards.md`

Use this for naming, folder structure, services, server actions, validation, error handling, RLS, tests, provider adapter rules, and source-of-truth enforcement.

## `library-docs.md`

Use this for practical implementation notes for Supabase, Prisma, Stripe, Typesense, Cronofy, Mux, Cloudflare R2, Sentry, AI providers, notifications, testing, and background jobs.

## `ui-tokens.md`

Use this for visual tokens: colors, typography, spacing, radii, shadows, component states, layout rhythm, and theme rules.

## `ui-rules.md`

Use this for interaction rules, page patterns, loading/empty/error states, accessibility, responsive behavior, and dashboard UX patterns.

## `ui-registry.md`

Use this for reusable screen/component inventory and where each UI object lives.

## `progress-tracker.md`

Use this as the living state of the build: completed work, current phase, current branch, known blockers, next tasks, and agent handoff notes.

---

## Final Product Definition

Workin Ants is a multi-actor marketplace and work platform where:

```text
identity branches into the right actor role
→ classification makes objects discoverable
→ professional readiness makes supply safe
→ customer demand becomes transaction truth
→ orders unlock delivery
→ hiring stays in its own formal lane
→ messaging and notifications carry communication
→ privacy, location, moderation, holds, audit, and ops protect the system
→ subscriptions and entitlements control commercial policy
→ incentives and prizes reward activity without corrupting compliance
```

The product succeeds when users can buy, sell, hire, apply, book, communicate, receive digital goods, get paid, and participate in rewards while developers can still answer one question clearly:

> Which source record owns this truth?
