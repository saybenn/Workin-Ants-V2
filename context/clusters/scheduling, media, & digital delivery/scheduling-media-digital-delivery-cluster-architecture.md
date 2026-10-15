# Scheduling, Media & Digital Delivery Architecture

> **Cluster ID:** CL-05  
> **Cluster name:** Scheduling, Media & Digital Delivery  
> **Cluster type:** delivery infrastructure / access grant / file / video / booking  
> **Document status:** Target cluster architecture for the Workin Ants MVP, grounded in the current Project Overview, Cluster Registry, Deep Module Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, CL-05 Module extracts, and Canonical Shared Operations Registry  
> **Audience:** coding agents, developers, reviewers, maintainers, and architecture reviewers  
> **Update rule:** update this file whenever a binding CL-05 ownership, contract, lifecycle, provider, security, or cross-Cluster decision changes. Build progress must not silently redefine this architecture.

This document coordinates the four Deep Modules inside CL-05. It does **not** make the Cluster a source-of-truth owner and does **not** transfer any Module lifecycle to a Cluster-level service.

Evidence labels used below:

- **Confirmed** — directly supported by current source-of-truth architecture, schema, glossary, registry, or repeated Module evidence.
- **Proposed Ruling** — a necessary implementation-grade ruling strongly supported by evidence but not yet cleanly settled across all sources.
- **Unresolved** — the evidence establishes a question or conflict but not a safe final answer.

---

## 1. Document Status and Scope

CL-05 coordinates delivery after a buyer, professional, candidate, organization member, Order, entitlement, consent, healthcare boundary, or other source Module has established the facts that permit delivery.

The Cluster contains:

1. `booking_calendar` — Booking & Calendar Module
2. `video_session` — Video Session Module (registry/legacy alias: Video Infrastructure Module)
3. `media_file_access` — Media / File Access Module
4. `digital_goods_access` — Digital Goods Access Module

The Cluster exists to make these Modules collaborate coherently around scheduling, private files, live rooms, streaming playback, and paid downloads. It does not own the upstream commercial or compliance facts that unlock those capabilities.

This architecture is subordinate to root Workin Ants architecture. Where this file and root architecture later conflict, root architecture wins unless the root architecture is explicitly changed. The Prisma schema remains executable schema evidence; this file explains semantic ownership, integration boundaries, and how coding agents must use that schema.

Module-specific architecture remains authoritative for Module-local lifecycle rules. This Cluster file may coordinate interfaces and order of collaboration, but it must not collapse Module-local records into Cluster-generic records.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

Safely deliver scheduled time, live video, private files, course streaming, and paid digital downloads after the necessary business and compliance gates are established.

### Goal

Produce reliable, entitlement-controlled delivery without turning external providers, signed URLs, audit logs, search documents, or Cluster coordination records into business source truth.

### What enters CL-05

Typical inputs are:

- authenticated actor context from Identity & Access;
- authorization decisions from Role / Authority;
- `CustomerProfile`, `ProfessionalProfile`, `CandidateProfile`, or `OrganizationMember` context;
- authoritative `Order` entitlement and Agreement readiness;
- track entitlement decisions such as priority scheduling or live-streaming access;
- consent proof for calendar connection or other versioned disclosures;
- healthcare readiness/data-boundary decisions where a healthcare lane is active;
- ComplianceHold decisions;
- location-reveal decisions for in-person service delivery;
- `Offering`, `ProductDetails`, and `CourseDetails` references from Marketplace Supply;
- `JobInterview` context from Organization Hiring & Candidate Pipeline;
- moderation/legal decisions;
- privacy instructions;
- validated uploaded bytes or provider callbacks.

### What leaves CL-05

Typical outputs are:

- conflict-free `BookingHold`, `BookingSlotLock`, and authoritative `Booking` records;
- calendar connection and normalized free/busy state;
- calendar writeback results;
- Booking-owned orchestration evidence;
- video-room records and short-lived join credentials;
- course-video provider assets and short-lived playback grants;
- safe, ready `MediaAsset` records and processed derivatives;
- generic temporary `MediaAccessGrant` records and short-lived signed object URLs;
- `DigitalDownloadAsset`, `DigitalDownloadGrant`, and `DigitalDownloadEvent` records;
- versioned digital-goods policy/acceptance proof;
- child-directed-control and accessibility records;
- provider-event dedupe records owned by the relevant provider Module;
- domain events/outbox requests, notifications, search refresh requests, audit events, and operational failure evidence.

### Major transformation

```text
Authoritative upstream entitlement / context
→ CL-05 owner validates local readiness
→ local source-of-truth record or temporary reservation is created
→ provider work is requested through owner-controlled adapters
→ provider result is verified, deduplicated, translated, and reconciled
→ short-lived delivery credential is issued when allowed
→ domain access/lifecycle evidence is appended
→ downstream notification/search/audit/ops effects are requested
```

### What CL-05 explicitly does not own

CL-05 does not own:

- authentication or general authorization;
- buyer, seller, candidate, or organization identity lifecycles;
- Offering, ProductDetails, CourseDetails, JobInterview, or Job lifecycles;
- Order payment/transaction truth;
- Agreement legal lifecycle or signature completion;
- payment-provider or tax truth;
- track plans, subscriptions, entitlement grants, or usage-period truth;
- generic consent/version truth;
- healthcare eligibility or BAA legal approval;
- exact-location reveal policy;
- moderation/legal decision truth;
- PrivacyRequest or DataErasureJob orchestration;
- generic AuditEvent or AccessAuditLog truth;
- Notification delivery mechanics;
- SearchUpsertEvent or Typesense/search projection truth;
- generic operational incident/failure truth.

### Scheduling nuance

Although the Cluster is primarily a delivery layer, `BookingHold` and `BookingSlotLock` intentionally support a **pre-confirmation reservation window**. They may exist while Order/payment/agreement completion is still in progress. This does not make a hold a paid entitlement. A `Booking` may be confirmed only after the required upstream Order and Agreement gates pass.

---

## 3. Module Inventory

| Module ID | Module name | Module type | Purpose | Owned truth | Primary responsibility in CL-05 | Major inbound dependencies | Major outbound consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `booking_calendar` | Booking & Calendar Module | `domain_capability_hybrid` | Own paid live-service scheduling, professional availability, calendar blocking, slot reservation, booking lifecycle, calendar synchronization, and booking-specific orchestration. | Availability rules, busy windows, calendar connection state, booking holds, slot locks, Booking, BookingEvent, calendar-provider dedupe, booking orchestration records. | Turn availability plus upstream transaction/readiness facts into one conflict-free Booking and maintain external calendar synchronization. | Identity/Authority, Customer Profile, Professional Profile, Consent, Order/Agreement, Track Entitlement, Location Safety, Video, Notification, Messaging, Audit/Ops. | Transaction/Order, Video Session, Notification, Messaging, Professional Eligibility, Location Safety. |
| `video_session` | Video Session Module (registry/legacy alias: Video Infrastructure Module) | `capability` | Own provider-neutral live-room and on-demand streaming mechanics. | BookingVideoRoom, JobInterviewVideoRoom, CourseVideoAsset, CourseVideoPlaybackGrant, CourseVideoPlaybackEvent, ProcessedVideoProviderEvent and video-provider status mappings. | Provision rooms/assets, issue short-lived join/playback credentials, process video-provider events, and preserve video-specific access evidence. | Booking, JobInterview, Order entitlement, CourseDetails, MediaAsset, Track Entitlement, Healthcare, Audit, Privacy, Digital Goods. | Booking, Job Interview, Digital Goods, support/review later. |
| `media_file_access` | Media / File Access Module | `capability_compliance_support` | Own file mechanics, upload policy, private storage, validation/scanning/processing, generic file grants, and short-lived signed file access. | MediaAsset, upload/validation/scan/processing records, MediaAccessGrant, MediaAccessEvent, storage/provider mechanics. | Turn untrusted uploaded bytes into a safe private/processed MediaAsset and expose it only through approved short-lived access mechanics. | Identity/Authority, contextual owner decisions, ComplianceHold, Healthcare, Moderation, Privacy, Audit/Ops. | Marketplace Supply, Order, Candidate/Resume, Messaging, Healthcare, Moderation, Digital Goods, Video. |
| `digital_goods_access` | Digital Goods Access Module | `domain_capability_compliance_hybrid` | Own buyer-facing paid digital access, product/course policy proof, expiring download grants, digital delivery events, child-directed declarations, privacy controls, and accessibility assets. | DigitalGoodsPolicy, DigitalGoodsTermsAcceptance, DigitalDownloadAsset, DigitalDownloadGrant, DigitalDownloadEvent, ChildDirectedContentDeclaration, MinorPrivacyControl, CourseAccessibilityAsset. | Convert an authoritative purchase/access basis plus safe MediaAsset into controlled downloadable access and digital-policy proof. | Identity/Authority, Customer Profile, Order, Offering/Product/Course, Consent, Media, Video, Moderation, Privacy, Audit. | Marketplace Supply, Order, Media, Video, Payment/Tax, Consent, Moderation, Privacy, Search. |

---

## 4. Cluster Architecture Principles

1. **The Cluster coordinates; Modules own truth.** No `DeliveryService`, `DeliveryStatus`, or `ClusterDeliveryRecord` may become an umbrella source of truth.
2. **Booking is scheduling truth.** Cronofy or another calendar provider is a rail. Provider events do not become Booking truth until Booking & Calendar verifies, deduplicates, translates, and applies them.
3. **One scheduling lane per parent domain.** `Booking` is paid service scheduling; `JobInterview` remains hiring-side scheduling. Video may serve both without owning either parent lifecycle.
4. **Video provider state stays video-owned.** `BookingVideoRoom`, `JobInterviewVideoRoom`, `CourseVideoAsset`, and `ProcessedVideoProviderEvent` remain Video truth.
5. **MediaAsset is file truth.** It is not purchase entitlement, course-streaming truth, Agreement proof, resume-access truth, or message-participant truth.
6. **Signed delivery is not entitlement.** A signed URL or playback/join token is issued only after the contextual owner and local delivery owner both approve.
7. **Temporary grants share mechanics, not records.** `MediaAccessGrant`, `DigitalDownloadGrant`, `CourseVideoPlaybackGrant`, `AgreementAccessGrant`, `SensitiveActionSession`, and `LocationReveal` must remain separate source records.
8. **Order remains purchase truth.** Digital download or playback access consumes `authorizeOrderEntitlement`; CL-05 never infers payment by reading Stripe/provider objects.
9. **Track entitlement remains external policy truth.** Priority scheduling and live-streaming perks are resolved through Track Subscription & Entitlement. CL-05 may snapshot the applied decision but may not create `isPremium`, `priorityCustomer`, or `canStream` truth.
10. **Consent is proof.** `ConsentLog` remains Consent & Disclosure truth. `DigitalGoodsTermsAcceptance` is contextual digital-goods evidence, not a competing generic consent system.
11. **ComplianceHold is the reusable stop sign.** Delivery Modules map an active hold into their own denial/freeze/revocation behavior rather than introducing local generic blocked flags.
12. **Healthcare policy remains healthcare-owned.** CL-05 enforces the returned provider/data-boundary decision; it does not decide whether a service is healthcare-regulated.
13. **Location reveal remains Location Safety-owned.** Booking may retain scheduling-context fields permitted by schema, but reveal permission and reveal proof must come from Location Safety.
14. **Audit is evidence, not lifecycle truth.** AccessAuditLog supplements MediaAccessEvent, DigitalDownloadEvent, CourseVideoPlaybackEvent, BookingEvent, and provider dedupe ledgers; it does not replace them.
15. **Observability is operational.** `IntegrationFailure`, queue telemetry, logs, metrics, and incidents never replace Booking, Media, Video, or Digital Goods status.
16. **Search remains projection.** CL-05 requests Search refresh where a delivery-owned fact affects public readiness; it never writes Typesense directly or owns SearchUpsertEvent.
17. **Privacy orchestration remains Privacy-owned.** Each CL-05 Module enumerates subject data and executes owner-specific instructions.
18. **Provider payloads are not domain types.** Cronofy, Daily/Agora, Mux, R2, or scanner payloads terminate at adapters.
19. **All asynchronous/provider work is idempotent and reconcilable.** A provider timeout must not cause duplicate rooms, slots, grants, assets, or revocations.
20. **UTC is authoritative for instants.** IANA timezone values provide recurrence/display context. Local-time strings must not become Booking truth.

---

## 5. Runtime / Collaboration Topology

### Primary request topology

```text
Browser / Server Action / Route Handler / Worker
        │
        ├─ SH-001 resolveAuthenticatedActor
        ├─ SH-002 authorizeResourceAction
        └─ runtime validation
                │
                ▼
        Owning Module application service
                │
                ├─ public queries to upstream truth owners
                ├─ CL-05 domain rules
                ├─ Prisma transaction against owner records
                ├─ SH-031 appendDomainLifecycleEvent where applicable
                ├─ SH-046 publishDomainEvent/outbox where applicable
                └─ SH-047 enqueueReliableJob where slow/provider-dependent
                         │
                         ▼
                  Owner worker / adapter
                         │
                         ├─ SH-059 verifyProviderWebhookSignature
                         ├─ SH-060 deduplicateProviderEvent
                         ├─ SH-061 translateProviderStatus
                         └─ owner-specific provider port
                                │
                                ▼
                          External provider
```

### Delivery authorization topology

```text
Authenticated actor
→ Role / Authority decision
→ contextual owner decision
   - Order entitlement
   - JobInterview participant facts
   - Messaging participant facts
   - Agreement entitlement
   - Digital Goods access basis
→ compliance gates where applicable
   - ComplianceHold
   - Healthcare readiness
   - consent proof
   - track entitlement
   - Location Safety reveal
→ CL-05 local readiness
   - booking state / join window
   - MediaAsset ready/not frozen/not erased
   - video asset/room state
   - DigitalDownloadGrant state/expiry/usage
→ short-lived credential issuance
→ domain access event
→ sensitive access audit when required
```

### Cross-Module database rule

The default integration path is a typed Module public interface or domain event. A CL-05 Module must not import another Module’s repository and issue direct cross-domain Prisma reads merely because the tables live in the same database.

A single Prisma transaction may span tightly coupled records only when the root architecture explicitly permits the owning services to participate in that transaction. Otherwise use public commands/events plus idempotent workflow orchestration.

### Cluster-local coordination

Cluster-local code is permitted only for orchestration that does not own durable business truth. `BookingOrchestrationRun` and `BookingOrchestrationStep` are **not** Cluster-generic orchestration; they are Booking-owned records and remain under `booking_calendar`.

---

## 6. Folder / Code Organization

The exact repository root naming must follow root Workin Ants `architecture.md` and `code-standards.md`. If those files use a different module layout, preserve the root convention. The following is the proposed CL-05 shape and boundary, not permission to create a second competing repository pattern.

```text
src/
├── modules/
│   ├── booking-calendar/
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   └── services/
│   │   ├── domain/
│   │   │   ├── policies/
│   │   │   ├── transitions/
│   │   │   └── events/
│   │   ├── infrastructure/
│   │   │   ├── repositories/
│   │   │   ├── calendar/
│   │   │   │   ├── calendar-port.ts
│   │   │   │   └── cronofy-adapter.ts
│   │   │   └── workers/
│   │   ├── public/
│   │   │   ├── commands.ts
│   │   │   ├── queries.ts
│   │   │   └── contracts.ts
│   │   └── tests/
│   ├── video-session/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   │   ├── live-video/
│   │   │   ├── streaming-video/
│   │   │   └── workers/
│   │   ├── public/
│   │   └── tests/
│   ├── media-file-access/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   │   ├── object-storage/
│   │   │   ├── malware-scan/
│   │   │   ├── image-processing/
│   │   │   └── workers/
│   │   ├── public/
│   │   └── tests/
│   └── digital-goods-access/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       ├── public/
│       └── tests/
│
├── clusters/
│   └── cl-05-delivery/
│       ├── contracts/        # only genuinely Cluster-level composition contracts
│       └── tests/            # cross-Module workflow tests; no source repositories
│
└── platform/
    ├── shared-operations/    # canonical SH-### implementations only
    ├── queue/
    ├── events/
    ├── security/
    ├── observability/
    └── database/
```

### Organization rules

- Domain/application code that changes `Booking`, `CourseVideoAsset`, `MediaAsset`, or `DigitalDownloadGrant` stays with its owning Module.
- Provider adapters stay with the Module that owns the provider relationship: calendar adapters with Booking; video providers with Video; object storage/scanning with Media.
- Shared queue, idempotency, locking, hashing, request context, and similar primitives must implement the canonical Shared Operations Registry rather than be recreated inside a Module.
- Cluster-local `contracts/` may define orchestration envelopes that coordinate the four Modules but may not define a second lifecycle.
- Tests that prove multiple Module contracts may live under Cluster tests; unit and lifecycle tests stay with the owner.
- Do not create a generic `shared/delivery`, `shared/access`, or `shared/providers` dumping ground.

---

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
| --- | --- | --- | --- |
| Booking & Calendar | Availability, BusyWindow, CalendarConnection, BookingHold, BookingSlotLock, Booking, BookingEvent, ProcessedCalendarEvent, Booking orchestration state | Order/Agreement readiness, Customer/Professional facts, consent, track entitlement, location decision, Video interface, Notification/Messaging, audit/ops | Video-room/provider truth, payment truth, Agreement lifecycle, JobInterview lifecycle, generic auth, location reveal truth, notification delivery |
| Video Session | Live room and streaming provider resource state, provider mapping, playback grant, video access event, ProcessedVideoProviderEvent | Booking facts, JobInterview facts, Order entitlement, CourseDetails, Media readiness, healthcare decision, track entitlement, audit/ops | Booking/Interview lifecycle, Order/payment truth, course business structure, MediaAsset storage truth, healthcare/BAA approval |
| Media / File Access | MediaAsset storage metadata, upload policy/session, validation/scan/process proof, generic media grant, signed media URL mechanics, MediaAccessEvent | contextual access decision, healthcare decision, ComplianceHold, moderation instruction, privacy instruction, audit/ops | purchase entitlement, OrderFile meaning, resume policy, message participation, Agreement lifecycle, DigitalDownloadGrant, CourseVideoPlaybackGrant, moderation/legal decision, PrivacyRequest lifecycle |
| Digital Goods Access | Digital goods policy, terms acceptance context, digital download asset/grant/event, child-directed declaration/control, course accessibility asset | Order entitlement, Offering/Product/Course facts, ConsentLog, Media readiness/signed URL, Video playback, moderation/privacy, audit | Offering lifecycle, file storage mechanics, streaming provider lifecycle, payment/tax truth, DMCA decision, general platform age gate, generic consent lifecycle |
| Transaction / Order | Order and OrderEvent, transaction entitlement, Agreement truth | Delivery outcomes | Booking, media, video, or digital delivery lifecycles |
| Track Subscription & Entitlement | Plan/subscription/grant/usage truth | CL-05 usage semantics | local booking/video premium booleans |
| Healthcare / Regulated Services | healthcare-lane readiness, BAA/data-boundary decisions | delivery provider/resource facts | Media/Video provider resource state |
| Location Safety | exact-location reveal/fuzzying policy and reveal proof | Booking context | Booking lifecycle |
| Consent & Disclosure | generic versioned consent proof | contextual acceptance references | DigitalGoodsTermsAcceptance or CalendarConnection state |
| Content Moderation & Legal Notice | moderation/legal decision and case/action lifecycle | CL-05 target facts and execution acknowledgment | direct mutation of CL-05 source tables |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob/Target/RetentionExemption orchestration | CL-05 data inventory and execution results | direct cross-owner deletion policy |
| Audit / Event Ledger | AuditEvent and AccessAuditLog | safe CL-05 evidence | BookingEvent, MediaAccessEvent, DigitalDownloadEvent, CourseVideoPlaybackEvent, provider dedupe ledgers |
| Observability / Ops | logs, metrics, IntegrationFailure, QueueJob telemetry, OpsIncident | CL-05 operation context | delivery business status |
| Notification | Notification and NotificationDelivery | CL-05 trigger meaning | Booking/delivery lifecycle |
| Search / Public Visibility | projection request/queue/execution/provider documents | approved source projections | source delivery truth |

---

## 8. Data Ownership

### 8.1 Booking & Calendar-owned records

| Record / enum | Meaning | Ownership note |
| --- | --- | --- |
| `AvailabilityRule` / `AvailabilityRuleSource` | Recurring professional availability | Booking & Calendar truth. Recurrence policy stays local. |
| `CalendarConnection` | Linked external calendar state and granted integration context | Booking-owned connection lifecycle; `ConsentLog` remains Consent-owned. |
| `CalendarConnectionStatus` | `pending_consent`, `active`, `disconnected`, `revoked`, `failed`, `expired` | Booking-owned lifecycle. |
| `CalendarSourceProvider`, `CalendarIntegrationProvider`, `CalendarSyncDirection`, `CalendarAccessMode`, `CalendarConnectionProviderStatus` | Calendar configuration/provider vocabulary | Booking-owned adapter/state vocabulary. Provider-native status still must be translated. |
| `BusyWindow` / `BusyWindowSource` | Unavailable time derived from manual, external calendar, Booking, or system | Booking-owned scheduling truth; external event details are not copied wholesale. |
| `BookingHold` / `BookingHoldStatus` | Temporary selected-slot reservation | Booking-owned. Statuses: `active`, `converted`, `expired`, `released`, `failed`. |
| `BookingSlotLock` / `BookingSlotLockStatus` | Atomic scarce interval reservation | Booking-owned policy over shared/Postgres interval-lock mechanism. Statuses: `active`, `converted`, `released`, `expired`, `failed`. |
| `Booking` / `BookingStatus` | Authoritative paid service appointment | Booking-owned. Statuses: `draft`, `held`, `awaiting_agreement`, `awaiting_payment`, `confirmed`, `rescheduled`, `completed`, `cancelled`, `no_show`, `expired`, `external_sync_failed`. |
| `BookingLocationType` | `video`, `phone`, `in_person` | Schema evidence ties this to Booking even though the Deep Module ownership list omits the enum. Treat as Booking-owned unless root architecture rules otherwise. |
| `BookingEvent` | Append-only Booking transition/timeline evidence | Booking domain truth, not generic audit. |
| `CalendarEventSyncStatus` | External calendar writeback status | Booking-owned provider-integration state. |
| `ProcessedCalendarEvent` | Calendar-provider dedupe ledger | Booking-owned provider-event truth; not AuditEvent. |
| `BookingOrchestrationRun`, `BookingOrchestrationStep` | Booking-owned downstream request/ack workflow | May use SH-049/050 mechanics. Does not own Agreement, Video, Notification, Thread, or Location truth. |
| Booking orchestration enums | Run/step states and step types | Booking-owned workflow semantics. |

`Booking.prioritySchedulingApplied`, `priorityEntitlementGrantId`, and `priorityRank` are historical scheduling-effect fields. They must be populated from Track Entitlement decisions and must not be used as current subscription truth.

### 8.2 Video Session-owned records

| Record / enum | Meaning | Ownership note |
| --- | --- | --- |
| `BookingVideoRoom` / `BookingVideoRoomStatus` / `BookingVideoProvider` | Live room resource attached one-to-one to a Booking | Video truth. Booking controls appointment state; Video controls room/provider state. |
| `JobInterviewVideoRoom` / corresponding provider/status enums | Live room resource attached to a JobInterview | Video truth. JobInterview remains CL-06 hiring lifecycle. |
| `CourseVideoAsset` / `CourseVideoAssetStatus` / `CourseVideoProvider` | On-demand streaming-provider asset state | Video truth; raw/source bytes remain Media truth. |
| `CourseVideoPlaybackGrant` / status enum | Short-lived stream access | Video-owned temporary grant; must not merge with DigitalDownloadGrant or MediaAccessGrant. |
| `CourseVideoPlaybackEvent` / event enum | Video-specific access/provider delivery evidence | Video domain access truth; generic sensitive AccessAuditLog may also be required. |
| `ProcessedVideoProviderEvent` / provider/status enums | Video webhook dedupe truth | Separate from calendar/payment/provider-event ledgers. |
| `CourseVideoPlaybackPolicy` | Video delivery mode such as `signed`, `public`, `drm`, `external_private` | Video delivery policy, but commercial product policy remains Digital Goods/Marketplace. |

`BookingVideoRoom` and `JobInterviewVideoRoom` are intentionally separate current source records. A future consolidated `VideoSession` model is not approved by this Cluster architecture.

### 8.3 Media / File Access-owned records

| Record / enum | Meaning | Ownership note |
| --- | --- | --- |
| `MediaAsset` / `MediaAssetStatus` | File/storage metadata and base lifecycle | Media truth. Statuses: `uploaded`, `quarantined`, `validating`, `processing`, `ready`, `rejected`, `failed`, `frozen`, `deleted`. `erasedAt` remains privacy-erasure effect, distinct from product deletion. |
| `MediaUploadPolicy` / status / context enums | Versioned upload/security policy by use context | Media owns technical acceptance rules, not contextual business entitlement. |
| `MediaUploadSession` | Upload attempt/progress proof | Media truth. |
| `MediaValidationResult` / `MediaValidationStatus` | Binary/MIME/size/policy validation proof | Media security proof, not moderation or verification truth. |
| `MediaScanResult` / `MediaScanStatus` | Malware scanning proof | Media security proof. Required scans fail closed. |
| `MediaProcessingResult` / action/status enums | Metadata scrubbing/derivative processing proof | Media truth. |
| `MediaAccessGrant` / status enum | Generic temporary MediaAsset access mechanics | Media truth; contextual entitlement remains external. |
| `MediaAccessEvent` / event enum | Media-specific issuance/read/download/denial evidence | Media domain access truth, not AccessAuditLog replacement. |
| storage visibility/bucket/rejection enums | Technical storage and validation vocabulary | Media-owned. |

#### Contextual media joins — conflict register

The current Deep Module Registry lists several contextual join tables (`OfferingMedia`, `GigMedia`, `JobMedia`, `MessageMedia`, profile media joins, and similar) under Media schema responsibility. The Ubiquitous Language join rule and canonical SH-090 state that contextual business meaning belongs to the contextual owner while Media owns `MediaAsset` mechanics.

**Proposed Ruling:** preserve existing schema placement until a root ownership decision explicitly moves it, but treat lifecycle/semantic policy for a contextual attachment as owned by the contextual Module. Media validates the asset and supplies file mechanics; it must not infer Offering, Message, Job, resume, or Order business meaning. No migration should be introduced solely to make this Cluster diagram cleaner.

### 8.4 Digital Goods Access-owned records

| Record / enum | Meaning | Ownership note |
| --- | --- | --- |
| `DigitalGoodsPolicy` / license/refund enums | Versioned commercial delivery/license/refund configuration attached to an Offering | Digital Goods truth. Legal text and policy approval remain legally gated. |
| `DigitalGoodsTermsAcceptance` / `DigitalGoodsTermsAcceptanceStatus` | Contextual acceptance proof tying user/order/offering/policy/version/hash to digital delivery | Digital Goods truth. Generic `ConsentLog` remains Consent-owned. |
| `DigitalDownloadAsset` / status / storage-provider enum | Downloadable delivery object attached to safe MediaAsset | Digital Goods truth; Media still owns the file. |
| `DigitalDownloadGrant` / status | Buyer/user-specific temporary paid download access | Digital Goods truth. Statuses: `active`, `used`, `expired`, `revoked`, `denied`. |
| `DigitalDownloadEvent` / event type | Digital delivery evidence | Digital Goods domain access truth. |
| `ChildDirectedContentDeclaration` / status | Product/course child-directed declaration and review state | Digital Goods truth; general platform age gate remains Identity-owned. |
| `MinorPrivacyControl` | Applied child-directed product-surface controls | Digital Goods projection/control record; must not become global privacy truth. |
| `CourseAccessibilityAsset` / type/status | Captions/transcripts/audio-description/descriptive assets | Digital Goods truth for accessibility tracking; backing file remains Media truth. |

#### Consent ownership correction

The Deep Module Registry lists several `ConsentType.*` values under Digital Goods schema responsibility. This conflicts with the canonical rule that Consent & Disclosure owns generic consent/version proof and controlled consent vocabulary.

**Binding interpretation:** Digital Goods may consume the relevant consent types and may persist `DigitalGoodsTermsAcceptance` contextual proof, but it must not own or fork the `ConsentType` enum or `ConsentLog` lifecycle.

### 8.5 External records referenced but not owned

The following are important CL-05 inputs but remain external truth:

- `User`, `CustomerProfile`, `ProfessionalProfile`, `CandidateProfile`, `OrganizationMember`;
- `Order`, `OrderEvent`, Agreement records and agreement access grants;
- `Offering`, `ProductDetails`, `CourseDetails`, `PricingTier`;
- `JobInterview` and its participant/event records;
- `TrackSubscription`, `TrackEntitlementGrant`, `TrackUsageEvent`, `TrackUsageCounter`;
- `ConsentLog`;
- `HealthcareDataBoundary`, `BaaAgreement`;
- `LocationReveal`, `FuzzyLocationCache`;
- `ComplianceHold`;
- `ModerationCase`, `ModerationAction`, `LegalNotice`;
- `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`;
- `AuditEvent`, `AccessAuditLog`;
- `Notification`, `NotificationDelivery`;
- `SearchUpsertEvent`;
- `IntegrationFailure`, `QueueJob`, `OpsIncident`.

---

## 9. Lifecycle Ownership

### 9.1 CalendarConnection lifecycle

**Owner:** Booking & Calendar  
**States:** `pending_consent → active → disconnected/revoked/expired/failed`, with provider status recorded separately.  
**Transition authority:** Booking & Calendar application service after Consent proof and provider adapter results.  
**May request/react:** Consent supplies proof; provider callback may trigger owner command; Privacy may instruct disconnection/deletion.  
**Must not be confused with:** `ConsentLog`, provider OAuth state, or a BusyWindow.

### 9.2 BookingHold lifecycle

**Owner:** Booking & Calendar  
**States:** `active → converted | expired | released | failed`.  
**Transition authority:** Booking & Calendar.  
**May request/react:** buyer selection, Order/Agreement progression, expiration worker, cancellation, conflict outcome.  
**Must not be confused with:** Booking, Order payment reservation, or BookingSlotLock.

### 9.3 BookingSlotLock lifecycle

**Owner:** Booking & Calendar.  
**States:** `active → converted | released | expired | failed`.  
**Transition authority:** Booking & Calendar using SH-058 interval-lock mechanism and database constraints.  
**May request/react:** BookingHold creation/conversion/expiration.  
**Must not be confused with:** generic QueueJob, Track usage counter, or JobInterview scheduling truth.

### 9.4 Booking lifecycle

**Owner:** Booking & Calendar.  
**States:** `draft`, `held`, `awaiting_agreement`, `awaiting_payment`, `confirmed`, `rescheduled`, `completed`, `cancelled`, `no_show`, `expired`, `external_sync_failed`.  
**Transition authority:** Booking & Calendar only. It consumes Order/Agreement facts rather than mutating them.  
**May request/react:** Order entitlement, Agreement readiness, cancellation/reschedule request, calendar provider failure, downstream video/notification/thread/location results.  
**Must not be confused with:** Order status, calendar provider event status, BookingVideoRoom status, or orchestration-run status.

### 9.5 BookingOrchestrationRun / Step lifecycles

**Owner:** Booking & Calendar.  
**Run states:** `pending`, `running`, `completed`, `partially_completed`, `failed`, `cancelled`.  
**Step states:** `pending`, `running`, `completed`, `skipped`, `failed`, `retrying`, `cancelled`.  
**Transition authority:** Booking worker/application service using shared workflow mechanics.  
**May request/react:** public commands to Calendar, Video, Notification, Messaging, Location Safety, and Agreement owner as applicable.  
**Must not be confused with:** the downstream target’s own lifecycle. A completed `create_video_room` step proves the Booking workflow received a successful result; it does not own `BookingVideoRoom.status`.

### 9.6 ProcessedCalendarEvent lifecycle

**Owner:** Booking & Calendar.  
**Purpose:** provider-event dedupe/processing proof.  
**Authority:** calendar webhook processor after signature verification.  
**Must not be confused with:** AuditEvent, BookingEvent, or provider source truth.

### 9.7 BookingVideoRoom lifecycle

**Live credential boundary (R011; also applies to JobInterviewVideoRoom):** persisted `roomUrl` and `*JoinUrl` fields may contain only non-authorizing metadata/opaque references, never reusable bearer access authority. Video mints actor/role/room/time-scoped short-lived participant credentials on demand. Evidence retains hashes/metadata, not reusable plaintext secrets. Later column removal, repurposing, or encryption remains a separate schema decision.

**Owner:** Video Session.  
**States:** `pending → active | failed | expired | cancelled`.  
**Transition authority:** Video Session after parent Booking facts and provider result.  
**May request/react:** Booking orchestration; provider webhook; privacy/moderation/security deletion command.  
**Must not be confused with:** Booking lifecycle or provider-native room state.

### 9.8 JobInterviewVideoRoom lifecycle

**Owner:** Video Session.  
**States:** `pending → active | failed | expired | cancelled`.  
**Transition authority:** Video Session.  
**May request/react:** Job Interview public command/event and provider callbacks.  
**Must not be confused with:** JobInterview lifecycle; CL-05 does not schedule hiring interviews.

### 9.9 CourseVideoAsset lifecycle

**Approved relationship contract (R008):** `CourseDetails.offeringId` is the canonical CourseDetails identity and identifies the owning Offering. `CourseVideoAsset.courseDetailsId` identifies that value. Its nullable `offeringId` is redundant: when present it must equal that identity and never identify another Offering. Video exposes owner-validated relationship facts through `getCourseVideoProcessingStatus` so Digital Goods can validate accessibility associations without querying Video repositories. Removing or constraining the redundant field is later schema work.

**Owner:** Video Session.  
**States:** `draft`, `upload_pending`, `uploading`, `processing`, `ready`, `failed`, `disabled`, `archived`, `deleted`.  
**Transition authority:** Video Session after Media source readiness and provider adapter results.  
**May request/react:** Marketplace/Digital Goods registration, Mux/provider webhook, moderation/privacy deletion instruction.  
**Must not be confused with:** `MediaAsset.status`, `DigitalDownloadAsset.status`, Offering status, or CourseDetails lifecycle.

### 9.10 CourseVideoPlaybackGrant lifecycle

**Separate grant semantics (R014):** the shared `used` label does not establish a universal CL-05 meaning. Media, Video, and Digital Goods own separate use events, terminality, concurrent-grant and replay rules. Grant/credential issuance is not automatically business consumption. Unapproved use rules and Digital Goods `final_after_access` remain unresolved; SH-057/088/089 do not settle them.

**Owner:** Video Session.  
**States:** `active → used | expired | revoked | denied`.  
**Transition authority:** Video Session after Order/contextual entitlement and local video readiness checks.  
**May request/react:** order refund/dispute/entitlement change, moderation/privacy, expiration.  
**Must not be confused with:** MediaAccessGrant or DigitalDownloadGrant.

### 9.11 ProcessedVideoProviderEvent lifecycle

**Owner:** Video Session.  
**States:** `received`, `processed`, `ignored_duplicate`, `failed`.  
**Authority:** Video provider webhook processor.  
**Must not be confused with:** video domain event or generic audit.

### 9.12 MediaAsset lifecycle

**Owner:** Media / File Access.  
**States:** `uploaded`, `quarantined`, `validating`, `processing`, `ready`, `rejected`, `failed`, `frozen`, `deleted`.  
**Transition authority:** Media application service/workers after policy validation, scan, processing, moderation/privacy instructions.  
**May request/react:** contextual upload initiation, scanner/processor result, moderation freeze, privacy erasure.  
**Must not be confused with:** `deletedAt` on contextual records, legal erasure (`erasedAt`), or business publication/access status.

### 9.13 MediaUploadPolicy lifecycle

**Owner:** Media / File Access.  
**States:** `draft`, `active`, `paused`, `retired`.  
**Transition authority:** Media administrative policy interface.  
**Must not be confused with:** runtime MediaAsset state.

### 9.14 Media upload/validation/scan/processing proof

**Owner:** Media / File Access.  
**Records:** MediaUploadSession, MediaValidationResult, MediaScanResult, MediaProcessingResult.  
**Upload-session separation (R010):** MediaUploadSession is an upload-attempt lifecycle, distinct from MediaAsset. A dedicated session-status representation is required in a later schema/migration pass. Current `MediaAssetStatus` storage reuse is legacy only and must remain behind Media-owned typed mapping; no consumer may depend on that coupling.
**Transition authority:** Media worker/adapters.  
**Important rule:** proof records support the MediaAsset transition but do not become moderation, trust verification, or healthcare approval.

### 9.15 MediaAccessGrant lifecycle

**Owner:** Media / File Access.  
**States:** `active → used | expired | revoked | denied`.  
**Transition authority:** Media after a contextual owner authorizes the requested file action.  
**Must not be confused with:** contextual entitlement itself.

### 9.16 DigitalGoodsTermsAcceptance lifecycle

**Owner:** Digital Goods Access.  
**States:** `accepted → revoked | voided`.  
**Transition authority:** Digital Goods contextual policy; generic consent acceptance remains Consent & Disclosure.  
**Must not be confused with:** AgreementElectronicConsent or ConsentLog.

### 9.17 DigitalDownloadAsset lifecycle

**Owner:** Digital Goods Access.  
**States:** `draft`, `upload_pending`, `ready`, `disabled`, `disabled_by_dmca`, `disabled_by_moderation`, `archived`, `deleted`.  
**Transition authority:** Digital Goods, consuming Media readiness and authorized Moderation decisions.  
**Must not be confused with:** MediaAsset status or Offering status.

### 9.18 DigitalDownloadGrant lifecycle

**Owner:** Digital Goods Access.  
**States:** `active → used | expired | revoked | denied`.  
**Transition authority:** Digital Goods after Order/contextual access authorization, usage count, refund/moderation/privacy effects.  
**Must not be confused with:** Order status, MediaAccessGrant, or Track entitlement.

### 9.19 ChildDirectedContentDeclaration lifecycle

**Owner:** Digital Goods Access.  
**States:** `not_declared`, `declared_not_child_directed`, `declared_child_directed`, `admin_review_required`, `approved`, `rejected`, `disabled`.  
**Transition authority:** Digital Goods/admin review process as later specified.  
**Must not be confused with:** Identity age gate, PrivacyRequest, or global moderation state.

### 9.20 CourseAccessibilityAsset lifecycle

**Owner:** Digital Goods Access.  
**States:** `missing`, `uploaded`, `processing`, `ready`, `failed`, `rejected`, `waived`, `not_required`.  
**Transition authority:** Digital Goods, using Media for backing file safety/storage.  
**Must not be confused with:** CourseVideoAsset or MediaAsset lifecycle.

---

## 10. Public Module Interfaces

Exact transport (Server Action, internal TypeScript interface, Route Handler, event handler) follows root code standards. The interface names below are the proposed stable application/public contract names except where CL-05 reconciliation rulings explicitly approve the owner contracts documented here. They express already-established responsibilities and must not be bypassed with cross-domain repository access.

| Interface | Owner | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `listBookableSlots` | Booking & Calendar | Marketplace/checkout UI, Order flow | Calculate currently bookable intervals from availability, busy windows, active locks, and policy | professionalProfileId, date range, requested duration, timezone/context | UTC intervals plus display timezone/context and freshness | Projection/decision | raw calendar-event details or direct provider free/busy policy |
| `createBookingHold` | Booking & Calendar | Order/checkout | Reserve a selected interval temporarily | actor/customer, professional, interval, optional order, idempotency key, priority entitlement decision | BookingHold + BookingSlotLock refs, expiry, priority snapshot | Truth | interval locking, entitlement policy, or Booking state |
| `confirmBooking` | Booking & Calendar | Order/Agreement workflow | Convert eligible hold/lock into authoritative Booking | hold/lock, Order entitlement evidence, Agreement readiness if required, actor, idempotency | Booking ref/status + orchestration request ref | Truth | payment truth or Agreement truth |
| `cancelBooking` / `rescheduleBooking` | Booking & Calendar | buyer/professional/support | Apply Booking-owned cancellation/reschedule transitions | booking, actor, expected version, reason/new interval | updated Booking + event + downstream work refs | Truth | downstream provider state |
| `connectCalendar` / `disconnectCalendar` | Booking & Calendar | Professional settings | Manage active external-calendar connection | professional, consent proof, provider/scopes/access mode, idempotency | CalendarConnection state and provider redirect/result | Truth | ConsentLog lifecycle or provider payload semantics |
| `applyCalendarProviderEvent` | Booking & Calendar | webhook worker | Apply verified/deduped provider changes | normalized provider event + processed-event claim | updated BusyWindow/connection/sync refs | Truth/evidence | direct provider state |
| `getBookingOwnerFacts` | Booking & Calendar | Video and authorized owner-fact consumers | Supply current parent/timing facts without transferring scheduling ownership | Booking reference and authorized request context | Booking ID/version or freshness marker, status, scheduled start/end, authorized participants, overtimeGraceMinutes | Owner facts | a local overtime default or direct Booking repository access; SH-003 remains Proposed |
| `provisionBookingVideoRoom` | Video Session | Booking orchestration | Create/get room for confirmed video Booking | current Booking ID/version or freshness marker, status, scheduled start/end, authorized participants, overtimeGraceMinutes, healthcare decision, entitlement if applicable, idempotency | BookingVideoRoom | Truth | Booking lifecycle |
| `provisionInterviewVideoRoom` | Video Session | Job Interview | Create/get room for Interview | interview facts/participants, healthcare decision if applicable, idempotency | JobInterviewVideoRoom | Truth | interview scheduling lifecycle |
| `issueVideoJoinCredential` | Video Session | Booking/Interview UI | Issue short-lived participant-specific join token/URL | room, actor, parent-context authorization, current time | credential + expiry + safe room metadata | Decision/evidence | parent authorization or provider permanent link |
| `getCourseVideoProcessingStatus` | Video Session | Marketplace/Digital Goods | Return safe processing and owner-validated relationship facts | CourseVideoAsset ID or approved course reference | asset ID/status, canonical courseDetailsId (= CourseDetails.offeringId and owning Offering ID), redundant offeringId equality validation | Owner facts | direct Video repository access or a second course identity |
| `registerCourseVideoSource` | Video Session | Marketplace/Digital Goods | Start streaming-provider ingest from ready MediaAsset | course/offering refs, source media decision, actor | CourseVideoAsset | Truth | MediaAsset lifecycle or CourseDetails lifecycle |
| `authorizeContextualResourceAccess` | Digital Goods Access | Video; Media/file consumers | Digital Goods-owned SH-026 contextual authorization for playback or file access | actor, target/action context, applicable owner facts/evidence | allow/deny, safe reason, applicable policy/acceptance evidence refs, evaluation freshness/expiry where applicable, owner-defined delivery constraints | Decision | Order payment truth or a generic cross-domain entitlement engine |
| `issueCoursePlaybackGrant` | Video Session | Digital Goods/course UI | Grant temporary signed streaming access | user, asset, Order entitlement or approved alternate basis, Digital Goods SH-026 playback decision, TTL, idempotency | CourseVideoPlaybackGrant + playback credential metadata | Truth/decision | Order entitlement or Digital Goods policy |
| `getMediaReadiness` | Media / File Access | all contextual modules | Return whether a MediaAsset is safe/ready for intended use | mediaAssetId, required context/action | status, validation/scan/process evidence refs, sensitivity, allowed next action | Decision | contextual business entitlement |
| `createMediaUploadSession` | Media / File Access | all upload surfaces | Create quarantine-first upload attempt | actor, upload context, file metadata, policy key | upload session + private upload instruction/object key | Truth | business attachment |
| `completeMediaUpload` | Media / File Access | upload route/worker | Validate, scan, process, and promote/reject uploaded bytes | upload session/object confirmation | MediaAsset state + proof refs | Truth | moderation or contextual attachment |
| `requestMediaAccess` | Media / File Access | contextual owner/UI | Public composite: validate the contextual owner’s decision and Media readiness/grant proof, then invoke SH-087 internally | actor, MediaAsset, contextual owner authorization decision/evidence, action, bounded TTL, idempotency key | short-lived credential + expiry + Media grant/access evidence references, or typed denial | Delivery credential/decision/evidence | contextual authorization logic or a second public signing call |
| `registerDigitalDownloadAsset` | Digital Goods Access | Marketplace Supply | Link a safe MediaAsset to a downloadable Offering/Course/Product | offering/context refs, media readiness, actor, access policy | DigitalDownloadAsset | Truth | Media lifecycle or Offering lifecycle |
| `recordDigitalGoodsTermsAcceptance` | Digital Goods Access | checkout/access flow | Preserve digital product policy/version acceptance context | user/order/offering/policy versions, Consent proof if required, text hash | DigitalGoodsTermsAcceptance | Evidence | generic consent lifecycle or Agreement state |
| `issueDigitalDownloadGrant` | Digital Goods Access | Order fulfillment | Create buyer/user download grant | user/customer, digital asset, Order entitlement or approved alternate basis, acceptance evidence, TTL/max use, idempotency | DigitalDownloadGrant | Truth | Order/payment state |
| `issueDigitalDownloadAccess` | Digital Goods Access | buyer download UI | Consume/validate grant then call Media `requestMediaAccess` | grant, actor, request context | delivery result + DigitalDownloadEvent + Media URL ref | Decision/evidence | object-store signing or Media safety rules |
| `applyVideoModerationDecision` | Video Session | Moderation | Video-owned SH-103 execution boundary: targeted asset disable/restore, affected grant revocation, other specifically targeted Video-owned transitions | authorized case/action/target instruction and replay identity | acknowledgment/completion/failure evidence, idempotent replay | Execution evidence | moderation/legal policy or direct Moderation writes to Video tables |
| `applyDigitalModerationDecision` | Digital Goods Access | Moderation | Apply authoritative action to download asset/grants | moderation action ID, target, action, idempotency | updated DigitalDownloadAsset/grants + acknowledgment | Truth/evidence | DMCA/legal validity |
| `executeCl05PrivacyInstruction` (owner-specific handlers, not one generic repository) | each CL-05 Module | Privacy | Execute Privacy-owned target instruction against owner data/provider | Privacy target command, subject, disposition, retention decision | erased/anonymized/retained/failed result + evidence | Execution result | PrivacyRequest/DataErasureJob lifecycle |

### Public interface rule

Where a canonical SH operation already defines the interface (`SH-025`, `SH-067`, `SH-068`, `SH-082`–`SH-090`, etc.), the Module public interface must reuse that contract or deliberately wrap it without creating a competing semantic operation.

---

## 11. Canonical Shared Operations Used by This Cluster

Only CL-05-relevant operations are listed. Full definitions remain in `context/shared/shared-operations.md`.

| ID / operation | Meaning / canonical owner | CL-05 consumers | Reusable mechanism | Local policy that remains local | Invocation point | Must not duplicate |
| --- | --- | --- | --- | --- | --- | --- |
| **SH-001 `resolveAuthenticatedActor`** | Trusted actor context — Identity & Access | all four Modules | canonical auth/session context | requested CL-05 action | every protected entry point | `bookingAuth.ts`, `mediaAuth.ts`, `videoAuth.ts`, `downloadAuth.ts` |
| **SH-002 `authorizeResourceAction`** | Permission interpretation — Role / Authority | all four | typed resource-action decision | owner relationship facts and action vocabulary | before protected query/mutation | local permission engines such as `canViewFile.ts` or `bookingPermissions.ts` |
| **SH-004 `resolveCustomerActor`** | User → CustomerProfile — Customer / Buyer Profile | Booking, Digital Goods, selected Video | buyer actor resolver | which customer receives/uses delivery | buyer-side hold/grant creation | `buyerResolver.ts`, `customerContext.ts` |
| **SH-005 `resolveEntitlement`** | effective plan perk — Track Subscription & Entitlement | Booking, Video; Digital Goods only for explicitly defined plan perks | typed entitlement decision | effect of priority/live-streaming decision | before priority scheduling or plan-gated streaming | `premiumBookingService`, `canLiveStream`, local premium booleans |
| **SH-006 `consumeMeteredEntitlement`** | atomic metered usage proof — Track Subscription & Entitlement | Booking/Video only when the entitlement definition is metered | usage event/counter transaction | exact business event that counts | after the perk actually affects delivery | local TrackUsageEvent writers/counters |
| **SH-007 `recordConsentProof`** | generic versioned consent proof — Consent & Disclosure | Booking/calendar and Digital Goods where generic consent required | canonical consent command | contextual reason and downstream record link | consent acceptance | local ConsentLog tables/services |
| **SH-008 `queryConsentProof`** | retrieve valid consent proof — Consent & Disclosure | Booking, Digital Goods | canonical consent query | whether proof is sufficient for current action | calendar connection / contextual terms gate | consent reconstruction from booleans |
| **SH-011 `evaluateComplianceHold`** | reusable stop sign — Admin Review / Compliance Hold | all four where action/target is hold-sensitive | canonical hold query | local denial/freeze/revocation behavior | before protected delivery/mutation | `isBlocked`, `mediaHoldService`, local generic blocked fields |
| **SH-020 `evaluateHealthcareReadiness`** | healthcare/BAA/data-boundary decision — Healthcare | Video, Media; Booking when healthcare context affects downstream delivery | decision contract | provider/resource enforcement | before healthcare file/video access/provisioning | HIPAA policy recreation inside CL-05 |
| **SH-025 `authorizeOrderEntitlement`** | Order permits delivery action — Transaction / Order | Booking, Video playback, Digital Goods, contextual Media | authoritative Order decision | local grant/booking eligibility and historical snapshot | before confirmation/grant/playback/download | `isOrderPaid`, `checkPurchase`, provider payment reads |
| **SH-026 `authorizeContextualResourceAccess`** | context owner permits protected resource access — relevant owner | Media and Video | shared decision shape | context-specific policy remains with owner | before Media grant/video join | universal access service that infers all contexts |
| **SH-027 `resolveLocationReveal`** | exact-location reveal decision/proof — Location Safety | Booking | location gate API | Booking supplies confirmed scheduling context | before displaying/decrypting exact in-person location | `canShowAddress`, Booking-owned reveal logic |
| **SH-029 `appendAuditEvent`** | generic action evidence — Audit / Event Ledger | all four where material | append-only audit API | which domain actions require generic audit | after material admin/security action | local generic audit loggers |
| **SH-030 `recordSensitiveAccess`** | sensitive read/download/join evidence — Audit / Event Ledger | Media, Video, Digital Goods; Booking/location where needed | AccessAuditLog API | target/action/sensitivity context | every required protected access attempt | `videoAuditLog`, `fileAccessLogger` |
| **SH-031 `appendDomainLifecycleEvent`** | append domain-owned lifecycle evidence — shared mechanism, domain truth local | Booking and delivery access-event owners as applicable | transaction hook/repository convention | event vocabulary/meaning | with authoritative transition | replacing BookingEvent/DigitalDownloadEvent/etc. with AuditEvent |
| **SH-032 `createRequestContext`** | request/correlation context — platform | all four | correlation propagation | safe operation metadata only | request/worker start | local request-ID systems |
| **SH-034 `sanitizeTelemetryMetadata`** | redact unsafe telemetry — Observability/Audit policy | all four | allowlist/redaction | Module sensitivity labels | before logs/audit/provider diagnostics | raw provider/personal payload logging |
| **SH-037 `recordIntegrationFailure`** | operational integration failure — Observability / Ops | all provider-backed CL-05 work | normalized failure record | owner still sets business failure state | terminal/retryable provider failure | `calendarFailureTable`, `muxErrorLog`, `mediaProviderFailure` |
| **SH-041 `requestNotification`** | canonical alert request — Notification | Booking, Media, Video, Digital Goods | typed notification request | trigger meaning and safe variables | after user-relevant outcome | Module-specific mail/SMS/push services |
| **SH-044 `executeIdempotentCommand`** | one business effect per retried command — platform | all four | idempotency claim/result replay | semantic key and replay rules | create hold, booking, room, grant, revocation, provider command | per-Module idempotency stores |
| **SH-045 `deduplicateDomainEvent`** | idempotent event consumer — platform | CL-05 subscribers | inbox claim | consumer side effect | domain-event consumption | ad hoc event dedupe |
| **SH-046 `publishDomainEvent`** | transactional outbox event publication — platform | all source-owning CL-05 Modules | outbox/envelope | event name/payload/privacy | after committed source transition | per-Module fire-and-forget event buses |
| **SH-047 `enqueueReliableJob`** | durable async work — shared queue | all four | queue/lease/dead-letter | payload and completion semantics | validation/scan/process/sync/provider/revocation/expiry | Module queue frameworks |
| **SH-048 `executeRetryWithBackoff`** | bounded transient retry — shared platform | provider workers | retry shell | retryability classification | transient provider/storage failure | custom retry loops |
| **SH-049 `orchestrateWorkflowSteps`** | persistent multi-step runner — shared mechanism | Booking orchestration; privacy/moderation only through their owners | run/step runner | Booking step graph/terminal meaning | Booking downstream workflow | generic `bookingSaga` that owns downstream truth |
| **SH-050 `reconcileWorkflowStatus`** | aggregate child steps — shared helper | Booking | deterministic aggregation | Booking partial/failure semantics | after step completion/failure | universal workflow status table |
| **SH-051 `acquireAggregateLock`** | serialize conflicting aggregate commands — platform | Booking, grants/media policy updates where needed | DB lock/advisory lock | lock key/conflict behavior | high-contention mutations | in-memory mutexes |
| **SH-052 `withOptimisticConcurrency`** | reject stale writes — platform | all mutable CL-05 lifecycles as adopted | compare-and-set/version | retry/merge/conflict policy | admin/user concurrent edits/transitions | ad hoc last-write-wins helpers |
| **SH-053 `transitionLifecycleState`** | shared state-machine plumbing — lifecycle owner supplies graph | all four | validation/update/event hook | each Module transition graph | any status mutation | generic cross-domain state machine policy table |
| **SH-055 `runDeadlineExpiration`** | expire time-bound owner records — shared scheduler | Booking holds/locks, Media grants, video grants, digital grants | batch scheduler | owner transition semantics | expiration sweep | per-Module cron frameworks |
| **SH-057 `consumeCounterAtomically`** | bounded counter increment — shared DB primitive | DigitalDownloadGrant max-download enforcement | atomic count/receipt | what counts as a download and exhaustion behavior | download attempt/completion per policy | `downloadCounter.ts` race-prone logic |
| **SH-058 `acquireIntervalLock`** | reserve interval without prohibited overlap — Booking policy over Postgres | Booking | range/exclusion/transaction mechanism | active-status/conflict policy | BookingHold/SlotLock creation | `bookingMutex`, in-memory slot locks |
| **SH-059 `verifyProviderWebhookSignature`** | authenticate raw webhook — shared shell + adapter algorithm | Booking, Video | raw-body verification contract | Cronofy/Mux/Daily/etc. secret/algorithm/tolerance | webhook entry before parse/side effect | route-local signature logic |
| **SH-060 `deduplicateProviderEvent`** | claim provider event exactly once — provider-owning Module | Booking, Video | unique provider/event primitive | ProcessedCalendarEvent vs ProcessedVideoProviderEvent remain separate | after signature verification, before domain mutation | generic provider-event table shared across domains |
| **SH-061 `translateProviderStatus`** | provider-native → owner vocabulary — provider adapter | Booking, Video, Media/storage where relevant | adapter mapping pattern | Module-specific mappings | adapter result/webhook normalization | central global provider-status mapper |
| **SH-062 `reconcileProviderState`** | compare/repair provider vs Workin Ants state — provider owner | Booking, Video, Media | reconciliation worker framework | auto-repair safety rules | scheduled/manual reconciliation | provider state treated as source truth |
| **SH-064 `authorizeExternalProviderConnection`** | initiate hosted/OAuth provider connection — provider owner | Booking calendar connection | state/nonce/redirect shell | calendar scopes/access mode | connect-calendar flow | generic OAuth flow that owns CalendarConnection |
| **SH-067 `invokeCalendarProvider`** | provider-neutral calendar create/update/cancel/sync — Booking & Calendar | Booking | calendar port + Cronofy adapter | booking/calendar mapping | availability sync and writeback | Cronofy calls outside Booking adapter |
| **SH-068 `invokeVideoProvider`** | provider-neutral room/asset/token operations — Video | Video | live/on-demand video ports | provider/resource mapping, token claims | room/asset/grant work | Daily/Agora/Mux calls from Booking/Digital Goods |
| **SH-070 `deleteProviderResource`** | delete/revoke external resource — provider owner | Booking, Video, Media where provider deletion exists | adapter delete method | resulting owner state | privacy/moderation/security deletion | Privacy directly calling video/storage providers |
| **SH-072 `hashCanonicalPayload`** | stable cryptographic digest — shared security | Media, Video, Digital Goods, provider dedupe | canonical hashing | what the hash proves | checksum/token/acceptance/provider evidence | local crypto helpers |
| **SH-074 `generateSecureToken`** | cryptographically secure secret, hash retained — shared security | Media, Video, Digital Goods | token generator/verifier | TTL/binding/usage | temporary grant issuance | `downloadToken.ts`, `videoTokenHelper.ts` with custom randomness |
| **SH-075 `encryptSensitiveValue`** | managed envelope encryption — shared security | Booking only where exact address snapshot is approved; sensitive Media/provider creds through proper owners | KMS/envelope primitive | necessity/access/retention | sensitive field persistence | `bookingEncryption.ts`, custom crypto |
| **SH-078 `minimizeAndRedactProviderInput`** | minimum purpose-bound provider payload — shared serializer + source policy | Booking, Video, Media | allowlisted provider DTO | exact fields permitted by owner/sensitivity lane | before provider calls | raw domain object forwarding |
| **SH-080 `manageVersionedRules`** | immutable/effective upload-policy versions — Media policy using shared versioning mechanism | MediaUploadPolicy | effective-version resolution, activation/retirement | Media technical policy meaning and exact applied-version evidence | policy administration/upload policy selection; future schema prerequisite | mutable historical policy or local versioning framework |
| **SH-082 `validateUploadedFile`** | size/MIME/binary/context validation — Media | all upload consumers | MediaUploadPolicy pipeline | contextual suitability after Media readiness | upload completion | file validators in Digital Goods/Video/etc. |
| **SH-083 `scanFileForMalware`** | malware scan/quarantine — Media | upload consumers | scanner adapter/result | policy says required/skipped | after validation before ready | per-context scanner services |
| **SH-084 `scrubFileMetadata`** | EXIF/GPS/PDF metadata removal — Media | public/cross-user media flows | processing pipeline | required actions by upload context | processing before ready/public derivative | `stripExif.ts` in feature Modules |
| **SH-085 `generatePrivateObjectKey`** | opaque storage key — Media/storage primitive | upload consumers through Media | key generator | bucket/context | upload session creation | user filename as object key |
| **SH-086 `calculateChecksum`** | binary integrity hash — shared primitive/Media | Media, Agreement verification consumer as appropriate | SHA-256 bytes | Media checksum meaning | upload/derivative | duplicate hash utility |
| **SH-087 `issueSignedMediaUrl`** | short-lived private object URL — Media | consumers through Media `requestMediaAccess` only | Media-internal R2/S3 presign adapter | Media readiness/grant/action/TTL | final file delivery | `r2SignedUrl.ts` in contextual Modules |
| **SH-088 `manageTemporaryAccessGrant`** | shared grant issue/use/expire/revoke mechanics; separate truth | Media, Video, Digital Goods | common grant helper | each grant schema/policy | temporary grant operations | one generic grant table |
| **SH-089 `revokeTemporaryAccessGrant`** | revoke domain grant after external instruction — each grant owner | Media, Video, Digital Goods | typed revocation pattern | owner transition/evidence | refund/moderation/privacy/security | direct cross-owner status mutation |
| **SH-090 `attachValidatedMedia`** | attach ready MediaAsset to contextual owner | Digital Goods and other context Modules | validated attach contract | contextual join meaning | digital asset/accessibility registration | Media inferring all attachment policy |
| **SH-091 `requestSearchProjectionRefresh`** | request index/update/hide/remove — Search | Digital Goods and Media only when their source change affects searchable public entity | Search public command | why delivery state affects public readiness | ready/disabled/restored events | direct Typesense/SearchUpsertEvent writes |
| **SH-095 `executePrivacyInstruction`** | owner executes Privacy-requested disposition | all four | privacy target protocol | owner erasure/anonymization/provider behavior | Privacy target execution | local PrivacyRequest workflows |
| **SH-096 `enumerateSubjectData`** | owner enumerates subject records/provider refs | all four | privacy inventory protocol | CL-05 schema/export meaning | privacy discovery/export | global crawler bypassing owner policy |
| **SH-097 `evaluateRetentionRequirement`** | owner supplies retention facts; Privacy records exemption | all four as relevant | retention decision contract | domain retention need | privacy disposition | local DataRetentionExemption |
| **SH-103 `executeModerationDecision`** | owner applies authoritative Moderation action | Media, Video, Digital Goods | signed action envelope | local disable/freeze/revoke transition | after ModerationAction | local DMCA/legal decision engine |
| **SH-109 `snapshotExternalDecision`** | freeze external policy decision historically — consuming owner | Booking primarily; other CL-05 use where needed | snapshot pattern | applied priority/entitlement value | hold/lock/booking creation | current-entitlement lookup masquerading as historical truth |
| **SH-113 `ensureContextThread`** | idempotent Messaging thread for context — Messaging | Booking orchestration | Messaging public interface | Booking participants/context | downstream communication setup | `bookingChatService.ts` |
| **SH-123 `validateOwnedTargetReference`** | validate cross-Module target through owner | all four | typed owner query | allowed relationship | linking Order/Offering/Interview/etc. | direct target repository imports |
| **SH-125 `recordDomainAccessEvent`** | domain-specific access/delivery proof — domain owner | Media, Video, Digital Goods | append-only access event mechanism | event vocabulary/provider/usage meaning | credential issuance/access attempt | using AccessAuditLog as sole delivery history |

### Conditional shared operation

`SH-014 requireStepUpForSensitiveAction` must be used where root security policy marks an admin/provider/security operation as step-up protected. CL-05 does not independently define the global step-up matrix.

---

## 12. Cross-Module Data Flows

### 12.1 Manual availability to BookingHold

```text
Customer selects proposed time
→ Booking & Calendar: resolve actor/customer + authorize action
→ Booking & Calendar: read AvailabilityRule + BusyWindow + active BookingSlotLock
→ Booking & Calendar: resolve priority entitlement if the product uses it
→ Booking & Calendar: SH-058 acquireIntervalLock
→ Booking & Calendar: create BookingSlotLock + BookingHold in authoritative transaction
→ Booking & Calendar: snapshot applied priority decision if relevant
→ Booking & Calendar: publish hold-created event / expiration job
→ Notification may be requested if product UX requires
```

Owner at every durable scheduling step: Booking & Calendar.

### 12.2 Booking confirmation

```text
Order/Agreement path indicates readiness
→ Transaction / Order: SH-025 authorizeOrderEntitlement
→ Agreement owner: return required agreement readiness
→ Booking & Calendar: re-check hold/lock/availability and holds
→ Booking & Calendar: confirm Booking; convert hold + slot lock
→ Booking & Calendar: append BookingEvent in same transaction
→ Booking & Calendar: create BookingOrchestrationRun/required steps
→ transactional outbox
→ workers request calendar writeback, video room, thread, location check, notification as applicable
→ orchestration step results acknowledged without absorbing downstream truth
```

### 12.3 External calendar connection and free/busy sync

```text
Professional requests connection
→ Consent: active calendar consent version + proof
→ Booking: SH-064 provider connection request
→ Cronofy adapter authorization/callback
→ Booking: CalendarConnection becomes active only after normalized result
→ provider push/webhook
→ SH-059 verify signature
→ Booking: SH-060 claim ProcessedCalendarEvent
→ adapter translates provider event
→ Booking updates BusyWindow / connection / sync state using free-busy-minimized data
→ audit/ops/notification effects as required
```

### 12.4 Calendar writeback

```text
Confirmed/rescheduled/cancelled Booking
→ Booking orchestration step
→ SH-067 invokeCalendarProvider
→ provider result translated
→ Booking externalSyncStatus/provider refs updated
→ transient failure queued/retried
→ terminal failure updates Booking-owned externalSyncStatus, fails/retries the applicable orchestration step, and records SH-037 IntegrationFailure
→ core Booking.status does not transition to external_sync_failed; that schema value remains reserved under the approved Booking lifecycle
→ reconciliation later compares provider state
```

### 12.5 Confirmed video Booking to live room

```text
Booking orchestration requests video room
→ Video queries Booking getBookingOwnerFacts for current ID/version or freshness marker, status, scheduled start/end, authorized participants, and overtimeGraceMinutes
→ Video uses the owner-provided overtime value, never a local schema-default policy, room-state inference, or direct Booking repository read
→ Role/context + healthcare + track entitlement gates as applicable
→ Video creates/persists BookingVideoRoom pending
→ SH-068 live-video adapter creates room
→ translated result updates Video-owned room active/failed
→ join request later re-authorizes parent participant + time window
→ Video issues short-lived join credential
→ Video-owned append-only live access evidence for successful or denied credential issuance; AccessAuditLog is supplemental when sensitive
```

Successful or denied Booking/Interview credential issuance must persist Video-owned append-only domain evidence under SH-125: room, parent context, actor/participant, action/decision, relevant provider context, expiry/access window, and time/request correlation. SH-030 alone is insufficient. The exact record/model name remains for a later schema pass; persistent Video evidence is a live-delivery prerequisite.

### 12.6 JobInterview to live video room

```text
CL-06 JobInterview owner requests room
→ Video validates owner-supplied interview/participant facts
→ healthcare gate if applicable
→ Video creates JobInterviewVideoRoom
→ live-video adapter provisions provider resource
→ Video controls join credential issuance
→ JobInterview remains the interview lifecycle owner
```

### 12.7 Upload to ready MediaAsset

```text
Context Module requests upload
→ Media resolves actor/authorization
→ Media selects active MediaUploadPolicy by MediaUploadContext
→ create quarantine object key + MediaUploadSession
→ client uploads to private/quarantine storage
→ Media worker inspects exact bytes
→ SH-082 validateUploadedFile
→ SH-083 scanFileForMalware when required
→ SH-084 scrubFileMetadata / create derivative where policy requires
→ checksum and proof records persisted
→ MediaAsset becomes ready only after required gates pass
→ contextual Module may attach validated media
```

### 12.8 Contextual file access

```text
Actor requests protected file
→ resource/context owner returns SH-026 authorization decision
→ consumer calls Media requestMediaAccess (public composite; no second signing call)
→ Media checks MediaAsset ready/not frozen/not erased + hold/healthcare gates
→ Media creates/validates MediaAccessGrant
→ Media SH-087 issues short-lived signed URL
→ MediaAccessEvent appended
→ SH-030 AccessAuditLog appended when sensitive
```

### 12.9 Paid digital download

```text
Order becomes delivery-entitled
→ Digital Goods validates DigitalGoodsPolicy and required terms acceptance
→ Order owner returns SH-025 decision
→ Digital Goods validates DigitalDownloadAsset ready/enabled
→ Media returns MediaAsset ready decision
→ Digital Goods creates DigitalDownloadGrant with TTL/max downloads
→ download request atomically enforces grant status/usage
→ Digital Goods calls Media requestMediaAccess with its contextual authorization/grant evidence; Media invokes SH-087 internally
→ DigitalDownloadEvent + MediaAccessEvent written separately
→ sensitive access audit if required
```

Default architectural TTL from current schema/module evidence: 24 hours for digital download grants unless approved DigitalGoodsPolicy overrides it.

### 12.10 Course video ingest and playback

```text
Course/Offering registers raw source MediaAsset
→ Media confirms ready/private source
→ Video creates CourseVideoAsset
→ Media authorizes and mediates a bounded source handoff; production transport remains unresolved
→ Video owns provider ingest from that handoff with purpose-minimized source information; no direct R2 access or permanent source URL
→ verified/deduped provider event marks asset ready/failed
→ playback request
→ Order owner authorizes purchase entitlement
→ Digital Goods returns its SH-026 authorizeContextualResourceAccess playback decision (allow/deny, safe reason, policy/acceptance evidence, freshness/expiry, delivery constraints)
→ Video combines that decision with SH-025 and its readiness/authority/healthcare/hold gates; it does not interpret raw Digital Goods rows
→ Video creates CourseVideoPlaybackGrant
→ Video issues signed playback credential
→ CourseVideoPlaybackEvent + sensitive audit when required
```

Default signed playback TTL from current schema/module evidence: 60 minutes unless approved policy overrides it.

### 12.11 Moderation/legal access removal

```text
Content Moderation creates authoritative decision
→ SH-103 dispatch to affected owners
→ Media may freeze/revoke public or signed access
→ Digital Goods may set asset disabled_by_dmca/disabled_by_moderation and revoke grants
→ Video may disable/delete streaming asset or room/provider resource when instructed
→ Search receives refresh/removal request from appropriate source owner
→ each owner returns execution acknowledgment
→ Moderation retains decision lifecycle
```

### 12.12 Privacy erasure/export

```text
Privacy verifies request and creates DataErasureJob/targets
→ SH-096 asks each CL-05 owner to enumerate subject data/provider refs
→ owner returns retention facts through SH-097
→ Privacy records exemptions/target dispositions
→ SH-095 owner-specific executor runs
   Booking: anonymize/disconnect/delete provider refs where allowed
   Video: revoke grants/delete provider resources where allowed
   Media: erase/anonymize asset metadata/delete storage objects where allowed
   Digital Goods: revoke/anonymize/delete delivery records where allowed
→ owner returns result/evidence
→ Privacy aggregates final request truth
```

---

## 13. Cross-Cluster Bridges

| Source | Destination | Information / command | Authoritative owner | Public interface / event | Forbidden coupling |
| --- | --- | --- | --- | --- | --- |
| CL-01 Identity & Access | CL-05 | authenticated actor | Identity & Access | SH-001 | feature-local current-user helpers |
| CL-01 Role / Authority | CL-05 | permission decision | Role / Authority | SH-002 + owner facts | direct permission booleans in CL-05 |
| CL-01 Customer Profile | Booking/Digital Goods/Video | buyer actor | Customer Profile | SH-004 | treating `User` alone as buyer truth where CustomerProfile is required |
| CL-01 Consent | Booking/Digital Goods | consent version/proof | Consent | SH-007/008 | local ConsentLog copies |
| CL-01 Track Entitlement | Booking/Video | priority/live-streaming/other defined perk decision | Track Entitlement | SH-005/006 | local premium flags/counters |
| CL-03 Marketplace Supply | Video/Digital Goods/Media | Offering/Product/Course identity and attachment context | Marketplace Supply | target-validation/public facts interface | CL-05 editing Offering lifecycle |
| CL-03 Healthcare | Media/Video/Booking | healthcare readiness/data-boundary decision | Healthcare | SH-020 | provider lane decided inside Media/Video |
| CL-04 Transaction / Order | Booking/Video/Digital Goods/Media | delivery entitlement, Order participant/item facts, refund/dispute effects | Order | SH-025 + domain events | Stripe reads, local paid booleans |
| CL-04 Agreement | Booking/Media | agreement readiness/access decision | Transaction / Order | Order public readiness/access interface; SH-112 stays Order-internal/background | Booking generating/owning Agreement proof |
| CL-06 Job Interview | Video | interview/participant/time context | Job Interview | owner facts + Video public command | Video scheduling/interview transitions |
| CL-07 Messaging | Booking | context thread | Messaging | SH-113 | Booking-owned chat/thread tables |
| CL-07 Notification | all four | alert delivery | Notification | SH-041 | direct SES/SMS/push clients in CL-05 |
| CL-08 Location Safety | Booking | exact/fuzzy location decision/proof | Location Safety | SH-027/028 | decrypt/show exact address locally |
| CL-08 Privacy | all four | privacy target instruction/retention disposition | Privacy | SH-095–099 protocols | local PrivacyRequest/DataErasureJob |
| CL-09 Compliance Hold | all four | stop-sign decision | Admin Review / Compliance Hold | SH-011 | local generic blocked state |
| CL-09 Moderation | Media/Video/Digital Goods | enforcement decision | Moderation | SH-103 | direct cross-owner mutation or local DMCA adjudication |
| CL-09 Audit | all four | generic/sensitive evidence | Audit / Event Ledger | SH-029/030 | replacing domain access/lifecycle ledgers |
| CL-09 Observability | all four | operational failure/telemetry | Observability / Ops | SH-032–039 | operational records as business truth |
| CL-02 Search | Digital Goods/Media indirectly | public projection refresh | Search | SH-091 | direct Typesense writes |

---

## 14. Authentication and Authorization

### Authentication

Every protected CL-05 request uses `SH-001 resolveAuthenticatedActor`. Provider webhooks authenticate through provider signature verification rather than end-user actor auth and execute as a narrowly scoped system/provider actor after verification and dedupe.

### Authorization

`SH-002 authorizeResourceAction` interprets platform/organization/participant/ownership permission. Each source owner supplies the minimum relationship facts needed for the decision.

Examples of contextual facts CL-05 must supply or obtain:

- Booking buyer/customer and Professional relationships;
- Booking owner/participant status for cancel/reschedule/join;
- JobInterview candidate/interviewer participant facts from CL-06;
- Offering ownership for upload/policy administration;
- Order participant/item facts for purchased delivery;
- contextual attachment owner decision for Media access.

### Sensitive/admin operations

Administrative or sensitive actions must not rely on platform role alone. They require the relevant resource authorization plus healthcare/privacy/hold/context decisions. Where root security policy marks an operation as high risk, use `SH-014 requireStepUpForSensitiveAction`.

Likely step-up candidates include provider-connection changes, access to highly sensitive identity/healthcare/legal files, and destructive provider deletion, but the exact global matrix is not defined by CL-05.

### RLS / database enforcement

RLS and database constraints should reinforce public application authorization where root architecture requires it. RLS must not encode another Module’s complete business readiness policy or bypass its public interface.

---

## 15. Compliance and Readiness Composition

CL-05 composes upstream facts only to decide whether a delivery action may proceed.

| Gate | Fact owner | CL-05 use |
| --- | --- | --- |
| Authenticated actor | Identity & Access | prerequisite for protected user actions |
| Resource action permission | Role / Authority | permission to manage/view/use CL-05 target |
| Customer buyer identity | Customer Profile | buyer-side Booking/download context |
| Order entitlement | Transaction / Order | confirms paid/eligible delivery basis |
| Agreement readiness | Transaction / Order | required before Booking confirmation where applicable |
| Calendar consent | Consent & Disclosure | proof required before linked calendar connection/scopes |
| Priority/live-streaming entitlement | Track Subscription & Entitlement | action-specific perk decision and optional usage proof |
| Healthcare readiness | Healthcare | selects/permits regulated provider/data boundary |
| ComplianceHold | Admin Review / Compliance Hold | reusable stop sign for applicable actions |
| Exact location reveal | Location Safety | controls decrypt/display and reveal evidence |
| Moderation/legal decision | Moderation | instructs disable/freeze/revoke/delete action |
| Privacy disposition | Privacy | instructs erase/anonymize/retain/revoke/delete-provider action |

CL-05 does not re-evaluate professional verification, financial KYC/tax readiness, or Job compliance unless the owning Module exposes a decision explicitly required by a CL-05 action. In most delivery flows those gates should already be reflected in Order/Offering/parent readiness.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Domain events

Source Modules publish versioned events after committed truth changes through SH-046. Example event families may include:

- booking hold created/expired/released;
- Booking confirmed/rescheduled/cancelled/completed/no-show;
- calendar connection activated/revoked/failed;
- media ready/rejected/frozen/erased;
- video room/asset ready/failed/expired;
- digital asset enabled/disabled;
- digital/playback/media grant issued/revoked/expired;
- digital terms acceptance recorded/revoked;
- child-directed control applied.

Exact event names and payload versions belong to the owning Module and must be defined in Module architecture/specification before implementation.

### Transactional outbox

Use SH-046 when a committed domain change requires asynchronous external effects. The source transaction writes domain truth and the outbox atomically. Never perform a critical provider side effect and then hope to persist source truth afterward.

### Workers

Shared worker infrastructure provides leases, heartbeat, retry/backoff, dead-letter, correlation, and telemetry. Owner workers provide business meaning.

Likely workers:

- BookingHold/BookingSlotLock expiration;
- calendar sync/writeback/reconciliation;
- Booking orchestration steps;
- media validation/scanning/processing/promotion/cleanup;
- MediaAccessGrant expiration/cleanup;
- live-video provisioning/cleanup/reconciliation;
- course-video provider ingest/webhook/reconciliation;
- playback/download grant expiration/revocation;
- moderation enforcement execution;
- privacy execution/provider deletion;
- search refresh request handling through Search owner.

### Retry policy

Retry only technical failures classified as transient. Business denials, invalid lifecycle transitions, failed authorization, expired entitlement, malware detections, and legal blocks are not retryable technical failures.

### Dead-letter handling

Dead-letter is operational state, not domain state. Terminal worker failure must:

1. retain owner business status appropriate to the failure;
2. record IntegrationFailure;
3. expose queue/dead-letter telemetry;
4. permit safe admin retry/reconciliation where allowed;
5. avoid duplicate source effects.

### Concurrency

- interval contention uses SH-058 and database constraints;
- grant/counter contention uses DB transactions/locks and SH-057 where bounded usage exists;
- mutable aggregate conflicts use SH-051/052 as appropriate;
- provider command duplication uses SH-044 plus stable provider request keys;
- provider callbacks use SH-060 owner-specific dedupe ledgers.

### Workflow / saga boundary

BookingOrchestrationRun/Step is the only current CL-05 durable saga truth explicitly established by schema. Do not create a generic `DeliveryWorkflow` table to unify Media, Video, Digital Goods, Booking, Privacy, or Moderation.

---

## 17. Provider Integrations

### 17.1 Calendar

```text
Booking & Calendar
→ CalendarProviderPort / SH-067
→ Cronofy adapter
→ Cronofy
→ verified/deduped/normalized result
→ CalendarConnection / BusyWindow / Booking sync transition
```

**Current provider:** Cronofy is the current canonical MVP calendar provider in Project/Shared Operations evidence. `Nylas` and `direct` appear as enum/future alternatives but are not additional MVP integrations unless root architecture changes.

- webhook verification: shared SH-059 shell + Cronofy adapter algorithm;
- dedupe truth: `ProcessedCalendarEvent`;
- status translation: Booking adapter;
- reconciliation: Booking-owned SH-062 worker;
- privacy rule: free/busy-only where possible; do not persist external event descriptions, locations, or attendees merely to block time.

### 17.2 Live video

```text
Video Session
→ LiveVideoProviderPort / SH-068
→ live provider adapter
→ provider
→ verified/deduped/normalized result
→ BookingVideoRoom or JobInterviewVideoRoom transition
```

The schema defaults Booking/Interview room provider to `daily`; the current Project Overview names Daily.co for MVP. Other evidence also mentions Agora and AWS Chime.

**Proposed Ruling:** implement a provider-neutral live-video port and treat Daily.co as the current MVP default adapter because it is the current Project Overview/schema default. Do not implement Agora or AWS Chime in the same MVP slice without an explicit root provider decision. See Unresolved Decisions.

### 17.3 On-demand course video

```text
Video Session
→ StreamingVideoProviderPort / SH-068
→ Mux adapter
→ Mux
→ verified/deduped processing result
→ CourseVideoAsset transition
→ signed playback grant/credential
```

Mux is the current MVP on-demand provider in project/module evidence. Raw source media remains R2/Media-owned; provider asset state remains Video-owned.

### 17.4 Object storage

```text
Media / File Access
→ ObjectStoragePort
→ Cloudflare R2 S3-compatible adapter
→ R2
→ normalized storage result
→ MediaAsset / MediaUploadSession / MediaAccessGrant state
```

Cloudflare R2 private storage is the current selected storage rail. Contextual Modules do not instantiate R2 clients or generate their own presigned URLs.

### 17.5 Malware scanning / file processing

```text
Media / File Access
→ MalwareScannerPort / processing ports
→ selected scanner / local processor
→ normalized scan/processing result
→ MediaScanResult / MediaProcessingResult
→ MediaAsset transition
```

The architecture requires the scanner adapter and fail-closed behavior when the active policy requires scanning. The exact production malware scanner provider is unresolved.

### Provider-wide rules

- raw provider webhooks must be verified before parsing/side effects;
- provider events must be claimed in the provider-owning Module’s separate dedupe ledger;
- unknown provider statuses fail closed or enter owner-defined review/failure state;
- secrets never enter domain records or telemetry;
- provider calls carry request/correlation IDs and idempotency where supported;
- provider-specific IDs are evidence/references, not the primary Workin Ants lifecycle;
- every provider owner must support reconciliation for missed callbacks or partial failures before production readiness.

---

## 18. Search / Projection Boundaries

CL-05 is not a search owner.

A CL-05 state change may affect whether a Marketplace Supply entity is safely publishable or discoverable. Examples:

- a required digital asset becomes ready or disabled;
- a moderation action removes public delivery;
- a child-directed control changes allowed public-surface behavior;
- a processed public media derivative becomes available or revoked.

When such a change matters:

```text
CL-05 owner/source workflow
→ SH-091 requestSearchProjectionRefresh
→ Search owner validates request
→ Search obtains approved source projection/readiness from source owners
→ Search writes/removes Typesense projection
```

CL-05 must not:

- call Typesense directly;
- write `SearchUpsertEvent` directly if the canonical Search command owns that creation;
- reconstruct Marketplace Supply publication policy;
- expose exact location, raw private media, provider URLs, access tokens, or paid delivery URLs in search documents.

---

## 19. Media / File Boundaries

### Contextual attachment ownership

A business Module decides **why** a file is attached and whether the current actor/context is entitled to it. Media decides whether the file is technically safe, ready, private/public-processed, frozen/erased, and deliverable through a generic grant.

### Upload security pipeline

```text
MediaUploadPolicy
→ MediaUploadSession
→ quarantine object
→ binary/size/type validation
→ malware scan when required
→ metadata scrub / derivative processing when required
→ checksum/proof
→ MediaAsset.ready
```

No contextual Module may mark a MediaAsset ready directly.

### Storage

- paid/sensitive/private files use private buckets;
- original filenames do not become object keys;
- untrusted bytes are never written to executable/public application directories;
- public images should use scrubbed/processed derivatives rather than raw originals;
- raw course video is private source media and not the streaming playback system.

### Signed URL issuance

Media issues signed object access through SH-087 only after:

1. authenticated actor and authority decision;
2. contextual owner entitlement decision;
3. ComplianceHold/healthcare gates where applicable;
4. MediaAsset status/readiness/freeze/erasure checks;
5. valid MediaAccessGrant or equivalent owner-approved access context;
6. TTL/action validation.

Current module evidence suggests a 15-minute default for sensitive generic media URLs. This is a default policy target, not a license for contextual Modules to hard-code their own TTLs.

### Sensitive access proof

MediaAccessEvent is Media domain evidence. AccessAuditLog is generic sensitive-access proof. When policy requires both, write both; never merge them.

---

## 20. Privacy / Retention

### Privacy target executor contract

Each CL-05 Module must implement:

- `enumerateSubjectData(subject)`;
- `evaluateRetentionRequirement(target)` where it has retention facts;
- `executePrivacyInstruction(target, disposition)`;
- export serialization where requested;
- external-provider resource deletion/revocation where applicable.

### Owner responsibilities

**Booking & Calendar**

- enumerate Bookings, holds, locks, calendar connections, BusyWindows, provider refs, and relevant orchestration/event records;
- disconnect provider connections when instructed;
- anonymize personal scheduling fields where permitted;
- preserve required transaction/safety records when Privacy records an exemption;
- never own the PrivacyRequest.

**Video Session**

- enumerate rooms, provider refs, assets, playback grants/events, dedupe evidence as policy permits;
- revoke grants;
- delete provider rooms/assets where instructed and allowed;
- anonymize retained access events where permitted.

**Media / File Access**

- enumerate assets, object keys, upload/scan/process/access records;
- delete object-storage resources where allowed;
- preserve retention-locked legal/financial evidence objects when Privacy records an exemption;
- mark/record erasure effects distinctly from normal product deletion.

**Digital Goods Access**

- enumerate policy acceptances, assets, grants/events, child-directed records, controls, accessibility records;
- revoke access before destructive cleanup where required;
- retain required acceptance/transaction evidence only through the Privacy retention process.

### Retention rules

DataRetentionExemption is Privacy-owned. CL-05 Modules supply domain retention facts; they do not create local `legalHold`, `keepForever`, or competing exemption records.

---

## 21. Audit and Observability

### Audit

Use Audit / Event Ledger for:

- generic material administrative actions (`AuditEvent`);
- sensitive file/video/location/access attempts (`AccessAuditLog`).

Audit metadata must be minimized and sanitized. Do not store raw signed URLs, access tokens, room secrets, exact healthcare content, full provider payloads, or unnecessary file names.

### Domain evidence remains separate

- `BookingEvent` — Booking lifecycle truth;
- `MediaAccessEvent` — Media delivery/access truth;
- `DigitalDownloadEvent` — digital download truth;
- `CourseVideoPlaybackEvent` — streaming access truth;
- `ProcessedCalendarEvent` — calendar webhook dedupe truth;
- `ProcessedVideoProviderEvent` — video webhook dedupe truth.

### Observability

Operational telemetry includes:

- request/correlation ID;
- owner Module and operation;
- safe target ID;
- provider/adapter name;
- duration and attempt count;
- retryability and normalized error category;
- queue depth/age and dead-letter count;
- reconciliation discrepancies;
- provider health/degradation.

`IntegrationFailure`, QueueJob telemetry, logs, metrics, and OpsIncident are operational proof only. A provider failure that changes a domain outcome must also update the owner’s business status.

---

## 22. Security Boundaries

1. Validate every server/API/job input with approved runtime schemas.
2. Authorize every protected user action server-side.
3. Keep provider credentials and signing keys server-only and outside domain records.
4. Use canonical secure-token, hash, and encryption primitives; no Module-local cryptography.
5. Never store reusable signed URLs or join/playback secrets as permanent truth; store hash/evidence metadata where required.
6. Use short-lived credentials bound to actor, target, purpose, and expiry where provider capabilities permit.
7. Validate upload bytes server-side; browser MIME/extension is untrusted.
8. Quarantine first; required validation/scan/processing must complete before `MediaAsset.ready`.
9. Scan-required policy fails closed when scanning is unavailable.
10. Strip EXIF/GPS and other disallowed metadata before cross-user/public image exposure.
11. Use private storage for paid/sensitive/raw course/legal files.
12. Verify provider webhook signature on raw bytes before parsing.
13. Deduplicate provider callbacks before side effects.
14. Protect against replay with provider event IDs, idempotency keys, timestamp tolerance, and hashed payload evidence.
15. Avoid overbroad provider scopes; calendar free/busy access is preferred where possible.
16. Minimize provider payloads and never send unnecessary healthcare/private data.
17. Enforce rate limits on upload-session creation, signed-access issuance, playback/join token issuance, and webhook/public endpoints as defined by root platform policy.
18. In-person exact location is never exposed solely because a Booking row contains location fields; Location Safety must authorize reveal.
19. Telemetry and audit pipelines apply sensitive-data redaction.
20. Destructive provider deletion requires authorized source instruction and idempotent result handling.

---

## 23. Testing Architecture

### Module unit tests

Each Module tests its domain transition graph, decision rules, expiry behavior, local policy mapping, provider result translation, and failure classification.

### Public-interface contract tests

Required contract suites include:

- Booking ↔ Order entitlement/Agreement readiness;
- Booking ↔ Track entitlement priority snapshot;
- Booking ↔ Location Safety reveal;
- Booking ↔ Video room request;
- Video ↔ JobInterview owner facts;
- Video ↔ Order entitlement for playback;
- Video ↔ Healthcare readiness;
- Digital Goods ↔ Order entitlement;
- Digital Goods ↔ Media readiness/signed access;
- Media ↔ contextual resource authorization;
- all four ↔ Privacy target protocol;
- Media/Video/Digital Goods ↔ Moderation enforcement;
- all four ↔ Audit/Notification/Ops canonical interfaces.

### Lifecycle transition tests

Test every legal and illegal state transition for:

- CalendarConnection;
- BookingHold;
- BookingSlotLock;
- Booking;
- BookingOrchestrationRun/Step;
- BookingVideoRoom and JobInterviewVideoRoom;
- CourseVideoAsset and CourseVideoPlaybackGrant;
- MediaAsset and MediaAccessGrant;
- DigitalGoodsTermsAcceptance;
- DigitalDownloadAsset and DigitalDownloadGrant;
- ChildDirectedContentDeclaration;
- CourseAccessibilityAsset.

### Concurrency/idempotency tests

At minimum:

- two users/requests cannot acquire conflicting booking intervals;
- retrying hold/booking confirmation returns one semantic result;
- retrying room/asset/grant creation produces one resource/record;
- duplicate webhooks create no repeated side effects;
- concurrent digital downloads cannot exceed max-download policy;
- expiration and use/revocation races produce deterministic final state.

### Provider adapter tests

Use recorded/synthetic fixtures only; do not couple domain tests to live providers. Test unknown statuses, signature failures, timeouts, retryable vs terminal errors, missed callback reconciliation, and provider-not-found deletion.

### Compliance/privacy tests

- calendar connection denied without required consent;
- healthcare file/video blocked when Healthcare denies;
- active ComplianceHold blocks mapped actions without local generic flags;
- exact location reveal denied without Location Safety decision;
- moderation decision disables/revokes delivery without Content Moderation mutating CL-05 tables directly;
- privacy executor respects retention exemption and provider deletion result;
- sensitive access writes AccessAuditLog without leaking secrets.

### Critical E2E workflows

1. safe upload → ready MediaAsset → authorized short-lived download;
2. paid digital Order → terms proof → DigitalDownloadGrant → file download;
3. paid course Order → ready CourseVideoAsset → signed playback;
4. availability → atomic hold/lock → Order/Agreement gate → confirmed Booking;
5. confirmed video Booking → room → participant token → expiry;
6. calendar connection → free/busy sync → Booking conflict prevention → writeback;
7. moderation/refund/privacy revocation prevents subsequent delivery.

---

## 24. Invariants

### Rules coding agents must never violate

1. CL-05 is not a source-of-truth owner.
2. Only Booking & Calendar changes Booking lifecycle state.
3. Only Video Session changes BookingVideoRoom, JobInterviewVideoRoom, CourseVideoAsset, and CourseVideoPlaybackGrant lifecycle state.
4. Only Media / File Access changes MediaAsset technical lifecycle and generic MediaAccessGrant state.
5. Only Digital Goods Access changes DigitalDownloadAsset/Grant and digital-goods policy/acceptance lifecycles.
6. Booking must not create or mutate video-provider resources directly.
7. Video must not transition Booking or JobInterview.
8. Media must not infer Order/payment, resume, message, Agreement, or digital purchase entitlement.
9. Digital Goods must not generate object-store signed URLs directly.
10. `MediaAsset` is not a Mux/video provider asset.
11. `ProductDetails.fileAssetId` or a MediaAsset reference alone never grants paid download access.
12. A provider room URL, playback URL, or presigned object URL is not durable entitlement truth.
13. Order is the authoritative paid transaction gate.
14. Track Subscription & Entitlement is the authoritative plan/perk gate; no local premium booleans.
15. ConsentLog is generic consent truth; DigitalGoodsTermsAcceptance remains contextual proof.
16. ComplianceHold is the reusable stop sign; do not add generic local `blocked`/`onHold` truth.
17. Healthcare decides regulated-lane readiness; Media/Video enforce rather than recreate it.
18. Location Safety decides exact-location reveal; Booking does not decrypt/display exact location independently.
19. Search is projection; no CL-05 Module calls Typesense directly.
20. Privacy owns request/job/target/retention-exemption lifecycles; CL-05 only executes owner instructions.
21. Moderation owns legal/moderation decisions; CL-05 executes resulting delivery transitions.
22. AuditEvent and AccessAuditLog do not replace BookingEvent, MediaAccessEvent, DigitalDownloadEvent, CourseVideoPlaybackEvent, or provider dedupe records.
23. IntegrationFailure/QueueJob/OpsIncident do not replace business status.
24. ProcessedCalendarEvent and ProcessedVideoProviderEvent remain separate provider-event truths.
25. Temporary grant schemas remain separate even if they use SH-088 shared mechanics.
26. Provider payloads must terminate at adapters and never become domain DTOs.
27. Webhooks are verified before parsing and deduplicated before side effects.
28. Slow/provider-dependent work uses durable jobs, not long request-bound workflows.
29. All retryable commands are idempotent.
30. UTC DateTime values are authoritative for scheduling instants; timezone is display/recurrence context.
31. Active Booking interval overlap policy must be enforced atomically at the database/application boundary.
32. Raw uploaded files never become ready from browser-declared MIME/extension alone.
33. Required malware scans fail closed.
34. Original filenames are not storage keys.
35. Paid/private/sensitive files do not receive permanent public URLs.
36. Raw course video does not receive public `.mp4`-style delivery URLs.
37. Public/cross-user images use required metadata-scrubbed derivatives.
38. Sensitive access credentials are short-lived and secrets are not persisted/logged as reusable values.
39. A refund/dispute/moderation/privacy/security event that invalidates delivery must revoke affected owner grants idempotently.
40. Search/public removal is not evidence deletion; retained evidence follows Privacy/Moderation retention policy.
41. BookingOrchestrationRun/Step may track downstream request completion but never becomes downstream source truth.
42. No direct cross-Module repository read is introduced when an owner public interface exists or is required.
43. Do not consolidate BookingVideoRoom and JobInterviewVideoRoom into a new generic model without a binding architecture change.
44. Do not move contextual join tables solely for aesthetic Cluster consistency; resolve the ownership conflict first.
45. Legal-gated Digital Goods behavior may not invent final legal text, thresholds, or child-directed compliance rules.

---

## 25. Prohibited Duplicate Implementations

Coding agents must reference the canonical Shared Operations Registry and must not create local equivalents such as:

| Duplicate risk | Do not create | Reuse / owner |
| --- | --- | --- |
| Authentication | `bookingAuth.ts`, `videoAuth.ts`, `mediaAuth.ts`, `downloadAuth.ts`, `getCurrentUser.ts` | SH-001 Identity & Access |
| Authorization | `bookingPermissionService.ts`, `mediaPermissions.ts`, `canViewFile.ts`, `videoParticipantGuard.ts` as independent policy engines | SH-002 Role / Authority + owner facts |
| Track perk checks | `premiumBookingService.ts`, `isPriorityCustomer.ts`, `canLiveStream.ts`, `subscriptionVideoGate.ts` | SH-005/006 Track Entitlement |
| Generic hold | `isBlocked.ts`, `mediaHoldService.ts`, local `blocked` column | SH-011 Compliance Hold |
| Order/payment gate | `isOrderPaid.ts`, `checkPurchase.ts`, `downloadEntitlement.ts`, Stripe reads in delivery code | SH-025 Transaction / Order |
| Location reveal | `canShowAddress.ts`, `bookingAddressReveal.ts` | SH-027 Location Safety |
| Generic audit | `calendarAuditLogger.ts`, `videoAuditLog.ts`, `fileAccessLogger.ts` | SH-029/030 Audit / Event Ledger |
| Queue/retry/idempotency | `mediaQueue.ts`, `muxQueue.ts`, `bookingIdempotencyService.ts`, custom `retry.ts` | SH-044/047/048 shared platform |
| Slot mutex | `bookingMutex.ts`, in-memory lock, `availabilityLock.ts` | SH-058 + Postgres interval constraint |
| Webhook verification/dedupe | `webhookAuthUtil.ts`, generic shared processed-event business table | SH-059/060; separate owner ledgers |
| Calendar provider calls | Cronofy SDK from Booking routes/components outside adapter | SH-067 Booking provider port |
| Video provider calls | Daily/Agora/Mux SDK from Booking/Digital Goods/Job Interview | SH-068 Video provider port |
| Crypto/signing | `bookingEncryption.ts`, `downloadToken.ts`, `hashVideoUrl.ts`, local SHA helpers | SH-072/074/075/086 |
| File validators/scanners | `validateResumeFile.ts`, `videoFileValidator.ts`, `downloadFileCheck.ts`, feature-local ClamAV | SH-082/083 Media |
| Metadata scrubbing | `stripExif.ts`, `sanitizeImage.ts` outside Media pipeline | SH-084 Media |
| Storage keys/presigned URLs | `r2SignedUrl.ts`, `s3Service.ts`, `getPrivateFileUrl.ts` in contextual Modules | SH-085/087 Media |
| Generic access-grant table | `TemporaryGrant`, `AccessGrant` replacing domain grants | SH-088 shared mechanics; separate truth |
| Search sync | `typesenseSync.ts`, `reindexMedia.ts`, `searchUpdate.ts` | SH-091 Search |
| Privacy workflow | `videoPrivacyService.ts`, `bookingEraseJob.ts`, `gdprMediaCleanup.ts` owning request lifecycle | SH-095–099 Privacy protocols |
| DMCA/legal decision engine | `dmcaHandler.ts` in Media/Digital Goods/Video | SH-103 Moderation decision owner |
| Booking chat | `bookingChatService.ts` that owns Thread | SH-113 Messaging |
| Generic delivery event log | `deliveryLog.ts` replacing domain events/access records | SH-031/125 + owner-specific ledgers |

---

## 26. Deferred / Unresolved Decisions

### 26.1 Live-video provider conflict

**Question:** Is Daily.co the binding MVP live-room provider, or should Agora/AWS Chime be implemented instead?  
**Why unresolved:** current Project Overview and Prisma defaults point to Daily.co; other Module evidence lists Agora and AWS Chime.  
**Current Proposed Ruling:** use a provider-neutral `LiveVideoProviderPort` and implement Daily.co as the current MVP adapter. Treat Agora/Chime as deferred alternatives.  
**Evidence missing:** explicit root provider ADR confirming the current live provider.  
**Blocks:** provider-specific production implementation if the Proposed Ruling is not accepted. It does not block domain/port implementation or test adapter.

### 26.2 Malware scanner provider

**Question:** Which production scanner/provider satisfies required MediaUploadPolicy scanning?  
**Why unresolved:** evidence requires scan proof and fail-closed behavior but names ClamAV/other provider only as optional/later.  
**Evidence missing:** root provider selection and production operating constraints.  
**Blocks:** production readiness for upload contexts whose active policy requires malware scanning. It does not block adapter, fake scanner, validation, quarantine, or processing implementation.

### 26.3 Contextual media join stewardship

**Question:** Which Module is schema/code steward for `OfferingMedia`, `GigMedia`, `JobMedia`, `MessageMedia`, profile-media joins, and similar contextual joins?  
**Why unresolved:** Deep Module Registry lists them under Media schema responsibility; glossary/shared-operation rules say contextual Modules own business attachment meaning.  
**Proposed Ruling:** retain current schema placement until root architecture decides; contextual owners own semantics and authorization, Media owns MediaAsset/file mechanics.  
**Blocks:** folder/repository placement for new join-specific mutation code, not MediaAsset implementation.

### 26.4 Booking exact-location storage

**Question:** Should `Booking.exactAddressEncrypted`, `fuzzyLat`, `fuzzyLng`, and `locationRevealStatus` remain Booking snapshots, or should exact location be fully centralized under Location Safety?  
**Why unresolved:** Prisma contains Booking location fields; Module shared-operation evidence questions whether Booking should store exact address at all; root rule clearly gives Location Safety reveal policy.  
**Proposed Ruling:** treat Booking fields as a permitted scheduling snapshot/cache only; Location Safety remains reveal/decryption decision owner.  
**Blocks:** production in-person exact-address read/write/reveal implementation until the snapshot contract is explicitly approved. Video/phone scheduling is unaffected.

### 26.5 Optional Order links on delivery grants

**Question:** Which approved non-purchase bases may issue `DigitalDownloadGrant` or `CourseVideoPlaybackGrant` when `orderId` is null?  
**Why unresolved:** schema permits null and Module evidence mentions explicit admin/test access, but no canonical alternate entitlement taxonomy is defined.  
**Evidence missing:** Digital Goods/Order product policy.  
**Blocks:** complimentary/admin/library access modes. Normal purchased delivery uses Order entitlement and is not blocked.

### 26.6 Digital goods legal content and child-directed rules

**Question:** What exact license/refund disclosures, terms versions, child-directed review criteria, waiver criteria, and jurisdictional legal text are approved?  
**Why unresolved:** `digital_goods_access` is `mvp_active_legal_gated`; architecture provides records and controls, not legal advice.  
**Evidence missing:** approved legal/compliance content and policy versions.  
**Blocks:** production activation of legally gated terms/review behavior. Schema, versioning, test policy, and workflow mechanics can be implemented.

### 26.7 Step-up matrix for sensitive CL-05 actions

**Question:** Which exact file/video/provider/admin actions require fresh MFA/passkey assurance?  
**Why unresolved:** canonical SH-014 exists, but CL-05-specific action matrix is not supplied.  
**Blocks:** final security policy for selected sensitive admin actions; normal authorization architecture is unaffected.

### 26.8 Digital Goods consent-type registry conflict

**Question:** Are the currently referenced electronic-record/signature/agreement consent values intended to be consumed by Digital Goods, Agreement flows, or both?  
**Binding boundary:** Consent & Disclosure owns `ConsentType`; Digital Goods cannot own it.  
**Evidence missing:** final consent taxonomy mapping.  
**Blocks:** exact consent key selection in digital-goods UI; does not block `DigitalGoodsTermsAcceptance` contextual evidence model.

### 26.9 Media-to-Video production ingest transport — R004

Media must authorize and mediate bounded source retrieval; Video owns provider ingest and receives only purpose-minimized source information. Video may not read R2 directly or receive a permanent source URL. Signed source URL, server stream, provider upload destination, and other transports remain unselected. Production ingest is blocked pending the handoff decision; test/fake adapters remain permitted.

### 26.10 Retention-safe cascade behavior — R013

A database cascade never authorizes erasure of compliance/delivery evidence. Before destructive production deletion, each owner enumerates affected records, supplies retention facts, receives Privacy's retain/anonymize/delete disposition, and executes it safely. Any cascade that could remove retained evidence is blocked from production reliance until target-specific retention behavior is approved. Record coverage, retention periods, anonymization, and exact FK/cascade changes remain unresolved.

### 26.11 Terminal live-room failure recovery — R015

Once Video commits a room to terminal `failed`, technical retry authority ends. SH-048 does not permit `failed → pending`; reconciliation does not permit duplicate rooms. Reset, replacement/generation, or another recovery design remains unresolved and requires a separate Video lifecycle ruling.

### 26.12 Historical Digital Goods legal content — R016

The accepted-text owner must preserve immutable historical content. Generic Consent-owned disclosures come from the Consent version catalog. Contextual Digital Goods license/refund/access text remains Digital Goods-owned unless explicitly classified as Consent-owned disclosure. A linked ConsentLog does not imply storage of that contextual text, and `acceptedTextHash` alone cannot reconstruct it. The owner-controlled persistence/retrieval mechanism remains unresolved; production legal-content activation is blocked until that source exists.


---

## 27. Architecture Decision Summary

### Binding rulings

- CL-05 is a delivery coordination boundary, not a lifecycle owner.
- Booking & Calendar owns availability, calendar connection, booking hold/lock, Booking, calendar provider dedupe, and Booking orchestration truth.
- Video Session owns live-room and streaming-provider resource truth and short-lived video playback/join grants.
- Media / File Access owns MediaAsset, file safety/processing/storage, generic Media access grants, and signed object access mechanics.
- Digital Goods Access owns digital policy/acceptance context, downloadable asset/grant/event truth, child-directed controls, and accessibility tracking.
- Order remains purchase/transaction entitlement truth.
- Track Subscription & Entitlement remains plan/perk/usage truth.
- Consent & Disclosure remains generic consent/version truth.
- Location Safety remains exact-location reveal truth.
- Healthcare remains healthcare readiness/data-boundary truth.
- ComplianceHold remains the generic stop sign.
- Moderation owns legal/moderation decisions; CL-05 executes owner-local effects.
- Privacy owns legal privacy orchestration and retention exemptions; CL-05 executes against owner records/providers.
- Audit and Observability remain separate from domain lifecycle and access-event truth.
- Search is a projection and is updated only through Search public interfaces.
- Provider webhooks are verified, deduplicated in provider-owner ledgers, translated, and reconciled before affecting Workin Ants truth.
- All temporary grant schemas remain distinct.
- Cronofy is the current calendar integration target; provider access remains behind Booking-owned adapter ports.
- Mux is the current on-demand course video target; provider access remains behind Video-owned adapter ports.
- Cloudflare R2 is the current private object-storage target; provider access remains behind Media-owned adapter ports.
- Digital download grants default to 24-hour access and signed course playback defaults to 60 minutes unless approved policy overrides them.
- `ConsentType` remains Consent & Disclosure-owned even where Digital Goods consumes specific consent values.

### Proposed rulings requiring root/architecture approval

- Daily.co is the current MVP live-video adapter behind a provider-neutral port; Agora/AWS Chime remain deferred.
- Booking location fields are snapshots/caches only; Location Safety remains reveal/decryption decision owner.
- contextual media join schema placement remains unchanged for now, while contextual Modules own attachment semantics and Media owns file mechanics.

---

## 28. Coding-Agent Usage

Before changing CL-05, an implementation agent must read, in order:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. `context/shared/shared-operations.md`;
5. this Cluster `architecture.md`;
6. this Cluster `build-plan.md`;
7. the target Module architecture;
8. the target Module implementation plan/specification;
9. relevant dependency Module public-interface sections, especially Identity/Authority, Customer Profile, Track Entitlement, Order/Agreement, Marketplace Supply, Healthcare, Job Interview, Location Safety, Privacy, Moderation, Audit/Ops, Messaging/Notification, and Search;
10. `context/progress-tracker.md`.

Before implementation, the agent must answer:

- Which Module owns the lifecycle I am changing?
- Which source record is authoritative?
- Which SH-### operations are consumed?
- Which owner public interfaces must be called instead of direct database reads?
- Which provider adapter owns the external call?
- What are the idempotency and concurrency boundaries?
- Which domain event/access record must be appended?
- Which generic audit/ops evidence is also required?
- Which privacy/moderation/hold/healthcare/location/entitlement gates apply?
- Does the requested work depend on an unresolved decision above?

If implementation would contradict a binding rule, stop the feature implementation, record the conflict, and update architecture only after a legitimate architecture decision is made.


## WA-R011 — Approved early-access scheduling (P01)

Product-owner ruling approved 2026-09-29: premium priority affects **when eligible customers may access newly released availability**. It never overrides an existing Booking, displaces a customer, reserves inventory permanently, or bypasses eligibility/conflict rules. This closes U-BC-05 / U-CL01-31 / CL-05-U017's product-effect choice.

Track owns the effective Customer-track benefit and returns eligibility, entitlement/grant evidence, policy version, evaluation time and expiry. Booking owns the release schedule and enforces the resulting access time on both slot queries and hold/confirmation commands. An early-access decision is not a slot reservation. Unavailable entitlement evidence cannot grant early access; ordinary access remains available once general release is reached, subject to normal gates. Existing holds follow their original bounded expiry; premium expiry cannot displace an already confirmed Booking.

Technical ruling: store timezone-independent release instants and a versioned release-window policy. Resolve the benefit against server time when creating a hold, bind evidence to that hold, and recheck normal conversion gates. No quota is consumed by this access-time benefit; SH-006 is not invoked unless a separately approved metered product is later introduced. Do not translate legacy priorityRank into request ordering. Missing release-window configuration disables early release for that availability; it does not invent a duration or disable ordinary booking. Exact window configuration is a launch prerequisite, not another ownership decision.

Implementation acceptance: premium/nonpremium boundary instants; expired/unavailable entitlement; concurrent claims; direct-command bypass attempts; replay of hold creation; no displacement; ordinary access at general release. Schema/API work must represent these facts before activation; this ruling is not implementation evidence.


## WA-R012 — Purchased session allowance and Booking cardinality (P02)

Product-owner ruling approved 2026-09-29: an Order may authorize multiple scheduled sessions **only when the purchased Offering/package explicitly includes them**. Four purchased sessions permit at most four allocated session entitlements, not unlimited Bookings. This closes U-BC-02 / CL-05-U014's product choice. Do not add uniqueness on Booking.orderId.

Supply owns the offered package description. Order validates and snapshots the purchased positive integer session allowance, source/version and applicable fulfillment/cancellation/refund terms; later Offering edits cannot change the purchase. Booking owns each appointment and its conflict, hold and scheduling lifecycle. Neither a paid flag nor counting local Booking rows supplies purchase authorization.

Technical ruling: Order owns durable per-session authorization identities bounded by the purchased allowance. An idempotent reservation command binds Order/session identity to one Booking command intent and reports authorized, exhausted, denied, or unavailable with the Order version. Concurrent attempts cannot reserve the same session twice or exceed the allowance. Booking persists the reservation identity with its local conversion; an outbox acknowledgement confirms attachment. An uncertain cross-owner outcome remains reserved until reconciliation queries Booking's durable result; never release merely on transport timeout. Failed conversion with proven absence can release its reservation idempotently. This is a recoverable workflow, not a cross-owner Prisma transaction.

Rescheduling retains the session authorization through the replacement chain and does not consume another session. A completed, cancelled or no-show appointment does not itself restore allowance or prove full Order completion. Order applies the purchased terms and owner-confirmed session outcomes; refunds and cancellation adjustments are Order decisions through Payment's rail. No automatic equal-price-per-session refund or forfeiture policy is invented. Packages cannot activate without explicit applicable terms. A normal SlotLock converts at most once (U-BC-03); that safety invariant is separate from Order multiplicity.

Implementation acceptance: four-session package permits four distinct authorizations and rejects a concurrent fifth; retry returns the same identity; single-session package remains bounded; reschedule reuses authorization; timeout recovery avoids double release/allocation; source edits do not rewrite terms; partial fulfillment does not finish the whole Order; refund/cancel outcome follows snapshotted terms. Current schema lacks this complete contract; the coordinated database pass must implement it before package activation.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


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


## WA-R025 — Location consumer alignment and reveal evidence

Class: **AI_RESOLVED** from the binding location product ruling and canonical SH-027/028/131. U-08-13/14's product predicate/directionality is settled: exact service location is disclosed only to the authenticated Professional/provider legitimately performing the active in-person service, within its service-performance window. No buyer, Organization, Search or public-map entitlement to another party's exact location is implied. Completion ends that justification; cancellation, refund or dispute masks/revokes it. Rescheduling requires a fresh current decision. Payment, Booking confirmation or a cached flag alone is insufficient authorization.

Source Modules own their protected location facts/references. Booking's exact/fuzzy/precision/reveal fields are non-authoritative scheduling snapshots or compatibility fields; neither Booking nor Order operates a second reveal lifecycle. Location queries current typed participant, service-state, time-window and source-location facts through owners. Missing/stale/inconsistent facts deny disclosure. Each supported service context has a typed identity; an attached Booking and Order must be consistent, not arbitrarily XOR when both legitimately describe the service. A nullable context pair never permits context-free disclosure. Non-Booking source contexts require an explicitly supported service-performance contract; Job/Organization address fields do not automatically qualify.

Location stores current per-viewer/service/source decision plus immutable decision/revocation history using its owned lifecycle and SH-031 mechanism. The semantic current key includes viewer, typed service context and source reference; an owner source/policy token binds the decision. Atomically reject stale Location writes; revoke/expiry wins over a replayed old allow. Replays may reproduce proof identity but must never re-disclose exact data without a current authorization evaluation. Rescheduling updates evidence in the same owner lifecycle rather than creating a parallel reveal flag. WA-R023 requires durable sensitive-access proof before returning exact data. This resolves U-08-11/12/15/16/19 architecture; exact fields/constraints and coordinated migration remain implementation prerequisites.

Fuzzy generation uses a versioned Location policy per supported typed source, stable for the same source/policy generation. Radius/precision and refresh/expiry settings must be explicitly configured and validated before public use. Source/policy changes, privacy removal and expiry invalidate old results. SH-131 returns only current approved projection fields with source/policy version and validity; absent/stale data is unavailable, never exact fallback or read-triggered generation. Consumers use SH-028 only for generation/invalidation commands. The target-kind registry names actual source owners and validators; free-form target strings cannot broaden support. U-08-17/18 policy structure is AI_RESOLVED; numerical deployment settings are deferred configuration, and geocoder/KMS/vendor evidence is externally gated.

Acceptance: wrong viewer or source relation, absent context, Booking/Order mismatch, completed/cancelled/refunded/disputed service, reschedule, stale source/policy and delayed events, duplicate reveal after revocation, audit failure and expired public projection. Exact location remains absent from Search, notification payloads and telemetry. Legal retention/Privacy dispositions are not selected by this ruling.


## WA-R026 — Approved Review and multi-episode Dispute policy (P06–P08)

**Binding product-owner ruling, 2026-10-01.** Review input is a whole-number 1–5 star rating. Zero and half-star input are invalid; aggregate/reputation values may be fractional. Review owns the rating calculation; Professional and Search consume its versioned result, not separate scales or calculators.

Automatically publish an otherwise eligible Review after completed-Order, buyer-author and applicable safety/moderation checks pass. An author may revise rating or comment. Every proposed revision is immutable history and passes the same applicable checks before becoming the public/reputation-bearing revision. Promotion is atomic against the expected Review version; a delayed check for an older revision cannot supersede a newer one. A rejected/unavailable revision does not overwrite the previously accepted public revision; an active restriction independently controls whether any revision is public. Author editing never restores hidden/removed state or bypasses a restriction. Restoration is an explicitly authorized Review owner/Moderation action. Revisions update the contribution of the same Review; they never add another rating count. Hiding/removal withdraws its contribution; restoration uses the current eligible accepted revision.

The Order's buyer Customer or seller Professional may open a commercial dispute. Authorized support may record one on behalf of an identified participant where policy allows; preserve both actual support actor and represented participant. There is **one durable Dispute case container per Order at launch**, not one dispute episode for the Order's lifetime. Authorized reviewers may reopen that case for new evidence, a correction, or a later episode associated with the same Order, including another session of a multi-session package.

Persist a distinct immutable cycle/episode identity for each review/adjudication/settlement cycle, with opening/reopening reason, initiating/represented actor, relevant Order version, session references where applicable, evidence, decisions and outcomes. The case's current state is a projection of its current cycle; reopening never overwrites prior closed decisions or settlement proof. Serialize cycle creation and adjudication per case. A current pending cycle can receive new evidence; it does not require competing active refund/release decisions. Any concurrency policy must preserve one authoritative current case decision path.

Every financial effect requires valid current owner authorization and an idempotent identity bound to the specific cycle/decision/effect, with prior effects retained for reconciliation. Never key a new valid effect only by case ID, and never mint a fresh identity merely to retry an old effect. Reopening itself cannot replay a previous refund, charge, payout adjustment, settlement or hold-release effect. Order/Payment validate cumulative amounts and remaining authorized source value across all cycles; a new cycle is not permission to exceed the purchased/refundable amount. Dispute decides, Order coordinates transaction effects, Payment executes its rail, and Holds retains its own action-scoped lifecycle.

Opening/appeal windows remain separately versioned product policy; no numerical deadline is introduced. Bind the applicable policy version to each cycle. Product case windows do not redefine statutory/provider rights. Current Prisma's one-case relation is compatible with the container rule but does not supply cycle/revision proof; the coordinated database pass must add that representation before activation.

Acceptance: ratings 0/6/fractions rejected, fractional aggregate allowed; two revisions race without double counting; failed safety check leaves the accepted revision unchanged; hidden/removed edit cannot restore; buyer/seller/support attribution; unrelated actor denied; later-session episode reuses the case with a new cycle; old cycle remains reconstructible; replay of old financial result cannot affect the new cycle; valid new effect has its own authorization and respects cumulative Order limits. These are required implementation checks, not claims of executed feature tests.

Duplicate collapse: CL04-U034/035/036/038/040 and owner §9/§35 product questions; CL04-U039 retains its versioned configuration gate. WA-R022/023 technical proof, financial finality and assurance rules remain binding. Classification: PRODUCT_OWNER_CHOICE — RESOLVED by explicit approval; enforcement/revision/cycle identity details AI_RESOLVED.

## WA-R028 — Digital delivery evidence and policy separation

Classification: AI_RESOLVED_WITH_TRADEOFF. Resolves the technical evidence/text-storage boundary while preserving PRODUCT_OWNER_CHOICE P09/P10 for refund finality and allowance consumption. It does not activate either policy.

Digital Goods owns an immutable contextual policy-content revision with Offering/policy identity, locale/jurisdiction applicability, terms/refund/license versions, exact retained content or immutable Media document/version reference, checksum and effective interval. Acceptance binds the precise revision/rendered presentation and contextual Order/User evidence. Do not overwrite accepted content on policy edit or use an unresolvable hash/version as historical proof. Consent owns generic disclosure content/proof separately; neither owner's proof implies the other's requirements passed. Actual legal text, applicable rights and retention remain external activation requirements. This supplies the persistence direction missing from Digital Goods §35.9; exact relational names follow coordinated schema conventions.

Separate grant issuance, download intent, transfer attempt, observed delivery outcome and policy evaluation. Digital Goods owns each immutable logical delivery identity bound to actor, asset version, Order entitlement reference, grant and policy revision. Media owns storage/transport evidence and returns a normalized authenticated receipt correlated to that identity; a browser assertion is untrusted. Video playback progress and byte serving are different observations and cannot silently stand in for Digital Goods delivery. Preserve observed byte/range/completion evidence with adapter capability and timestamps; an adapter that cannot establish completion returns unknown rather than manufactures success. Completion of server delivery never claims the person read or understood the content.

A signed URL or accepted terms is not proof of download completion. Record it as the distinct event it is. Retries/resumptions for the same logical intent retain identity and attempt history; conflicting asset/actor bindings reject. Finite-allowance implementations must account for in-flight reservations under the grant lock so concurrent requests cannot bypass the approved cap; do not release an unknown outcome merely on client timeout. Reconcile durable owner/Media evidence before deciding release/consumption. The exact consumption event is P10, not chosen by this technical protocol. Unknown evidence cannot automatically make a purchase non-refundable. No `used`, URL or playback projection grants Order refund authority.

Expose delivery evidence to Order/Review as a versioned owner query containing logical identity, asset version, accepted policy/proof reference, grant state, observations and their reliability, with minimal actor/context references. Order/Review apply their approved refund/dispute policy and current authorization; Media and Digital Goods do not execute financial refunds or declare legal finality. P08 case reopening may add a new interpretation/decision cycle while retaining the original observations. Corrections append evidence and reevaluate projections; they never rewrite the old observation or repeat an old financial effect.

Acceptance before activation: URL issued without bytes, aborted transfer, range resume, duplicate receipt, unknown completion, concurrent last-allowance requests, changed policy after purchase, stale/revoked Order entitlement and later dispute cycle. These tests establish technical truthfulness; approved P09/P10 behavior and actual provider capabilities remain separate prerequisites.

## WA-R029 — Approved digital refund, download and seller-acceptance policies (P09–P11)

Binding product-owner ruling: 2026-10-01 America/New_York (2026-10-02 UTC). Supersedes the open P09–P11 alternatives and contrary conceptual payment/acceptance sequences. WA-R028 continues to govern truthful delivery evidence.

P09: At launch, digital access, grant issuance, streaming and download completion never automatically make a purchase non-refundable. Delivery/access evidence may inform authorized refund/dispute review but never determines the result alone. Apply the applicable product/refund policy, dispute facts and required external/legal rules. An approved refund or revocation triggers only the downstream access consequences specified by the owning Order/Digital Goods policy. Download history alone neither revokes access nor preserves it against an authorized revocation. No automatic `final_after_access` denial is enabled by a stored enum value.

P10: Consume one allowance only when one user-initiated logical download successfully completes with verified delivery. Retries, resumes, range requests, duplicate transport attempts and recovery of the same logical download consume no additional allowance. Failed or unverified delivery consumes zero. A genuinely new user-initiated download after a completed one may consume another allowance only when the applicable product policy actually limits download count. Finite `used` means allowance exhausted; unlimited grants are not exhausted by first use. Completion observation proves delivery, not human reading or legal acceptance.

Digital Goods mints and persists the logical-download identity at explicit user initiation, with actor/asset-version/grant/Order/policy binding. Transport retries cannot mint a new identity. Atomically convert that intent's reservation to one consumption on its first verified completion; a unique consumption reference prevents duplicates. Resumes retain the same identity. A new explicit post-completion initiation is a new logical identity, subject to policy and current authorization. Unverified attempts remain zero-consumption even while their in-flight reservation is reconciled. Bound reservation lifetime through server-side access expiry/revocation and reconcile before releasing capacity; never strand allowance indefinitely or release while an old transfer remains capable of independently completing. Late receipts reconcile to the original identity and cannot charge another allowance. Provider evidence incapable of proving the approved completion event cannot support finite-count consumption; do not substitute URL issuance, elapsed time or client claims. This capability requirement gates that delivery adapter, not P10's product meaning.

P11: For live or seller-performed services, final capture requires seller acceptance. Acceptance is either explicit approval of the specific Order/Gig/service request or valid precommitted acceptance: the seller intentionally configured an approved instant-book/availability/product policy and the frozen requested transaction satisfies all its constraints. A matching accepted Gig award satisfies acceptance; merely publishing a service does not. Published standalone downloads and self-paced digital courses/products may auto-accept because fulfillment requires no later seller performance decision. Payment authorization/holds may precede acceptance where Payment architecture permits; authorization is not final capture. Platform screening has its separate approved source, with no fabricated seller.

Order records immutable acceptance evidence: seller/context, explicit decision or intentional precommit policy identity/version, frozen scope/price/package version, applicability result and timestamp. A precommit must be active and applicable when accepted, scoped to the actual seller/product, and cannot be inferred from a premium flag or open calendar alone. Policy changes do not rewrite already recorded acceptance; material requested scope/price changes require fresh acceptance of the changed terms. Recheck current financial capability, cancellation/hold and payment authorization validity immediately before capture. Payment accepts a uniquely identified Order-authorized capture intent with acceptance proof; retries preserve that effect identity and uncertain outcomes reconcile before any new capture. No capture from stale acceptance for different terms or from mere Booking existence.

Order remains transaction truth and Booking owns individual scheduled sessions. Acceptance is evidence within Order, not a second Order/Booking lifecycle or a separate booking authority. A multi-session package acceptance binds purchased scope; each Booking still uses current eligibility/conflict checks and bounded Order session authorization. Instant booking does not bypass locks, consume nonexistent availability or displace customers. Decline/expiry releases only valid owner reservations/authorizations; any already captured amount follows an independently authorized refund. Numerical response windows remain versioned policy, not invented here.

Implementation acceptance requirements: access/completion cannot auto-deny refund; authorized revocation follows current owner policy; aborted/unverified delivery zero consumption; range/resume/replay one consumption; new post-completion initiation counts only under bounded policy; concurrent last allowance; late receipt reconciliation; explicit versus valid precommitted acceptance; absent/revoked/inapplicable precommit denied; changed terms need new acceptance; Gig acceptance matching; authorization-before-acceptance permitted but capture-before-acceptance denied; capture retries idempotent; Booking conflict rules unchanged. These are required tests, not executed runtime claims.

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

## WA-R035 — Supply lifecycle, history and source projections

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

This ruling supersedes the proposed/unresolved lifecycle and projection alternatives named below; implementation still requires forward schema coverage and contract fixtures. Professional graph: create→draft; draft→active after current activation readiness; active→paused; paused→active after current readiness; draft/active/paused→suspended only by an authorized source restriction; draft/active/paused→archived by owner-authorized retirement. Archiving a suspended record may record retirement intent but cannot remove the restriction. Archived→draft is an explicit owner restore command, never implicit activation. Suspended→draft requires authorized release of all applicable restriction sources; subsequent activation rechecks readiness. Preserve previously acquired transactions and obligations. Ordinary dependency loss invalidates the affected action/public decision and requests reevaluation, not an automatic Profile status change. Only an explicit source policy may instruct suspension.

Offering graph: draft→active by publish; active→paused; paused→active by resume, each activation requiring current composed gates. Draft/active/paused may enter under_moderation/disabled_by_moderation/disabled_by_dmca only from a valid Moderation decision. Those restriction states may change to another restriction state only with a superseding valid decision. Restriction clearance restores to draft, preserving all other restriction sources; publication is a separate fresh command. Rejected→draft is an explicit correction/resubmission command after the rejecting owner permits it. Draft/active/paused/rejected→archived; archived→draft by explicit restore. Retirement never clears restrictions, destroys Order snapshots or grants a refund. An Offering kind can change in draft only before any Order, delivery or durable external reference; otherwise create a new Offering. isPublic is seller publication intent; effective visibility additionally requires active lifecycle, current SH-024 decision and no applicable restriction. Moderation timestamps are evidence, not independent allow flags.

Adopt immutable owner lifecycle histories for ProfessionalProfile and Offering, with aggregate version, prior/next state, command/source decision identity, actor, timestamp and policy/decision references. Mutations commit history and outbox atomically using expected opaque version plus row serialization for competing transitions; updatedAt alone is not the concurrency token. Publication/activation and seller Order acceptance retain immutable minimized gate decisions/source versions; current actions still reevaluate. Legacy financial/Trust columns remain non-authoritative compatibility projections until a measured reader inventory and forward migration remove them; never backfill authoritative readiness from a legacy boolean.

onboardingCompleteAt is the first successful owner activation after required onboarding facts pass, immutable except an audited data correction. It is not current readiness. ProfileCompleted.v1 may qualify one Gamification rule per profile and rule revision, containing profileId, subject User reference, firstCompletionAt, aggregateVersion, eventId; no raw onboarding facts. Gamification decides awards and source-event dedupe. Reinstatement does not emit another first completion. Dependency changes are owner outbox facts carrying target, changed dimension and source version; Professional/Supply consume idempotently and reevaluate current truth. Do not propagate a copied allow decision indefinitely. Booking availability is not an eligibility prerequisite; a public availability presentation uses Booking's separately authorized query and never changes Professional status.

Public Professional projection allowlist: professionalProfileId, slug, display name, approved biography, accepted active taxonomy IDs/labels/revisions, owner-supplied public avatar rendition reference, Review-owned ratingAverage/ratingCount with reputation version, and SH-131 fuzzy public location when allowed. Public Offering projection: offeringId, professionalProfileId, slug, title, approved summary, kind, accepted taxonomy IDs/labels/revisions, current public pricing summary/currency, approved public rendition references and public delivery/location mode. Each includes sourceVersion and current public-readiness evidence. Exclude User IDs, contact details, exact location, credential documents, provider refs, financial/Healthcare/hold reasons. Search must obtain URLs through approved Media/public rendition rules; no private original URL. Review→Professional transport is an outbox-triggered owner query getProfessionalReputation.v1 returning profileId, ratingAverage, ratingCount, projectionVersion, then a version-checked Professional projection command; stale events trigger current query rather than regress values.

priceFromCents is a rebuildable minimum of currently eligible active pricing options in one currency, not purchase truth. Missing or mixed-currency options produce no priceFrom value, never zero/implicit conversion. Orders bind the selected immutable price/package. isFeatured has no ranking or commercial effect at launch; promotion is deferred pending a separately approved owner policy. Heterogeneous bundle Offering creation remains disabled; this does not disable P02 multi-session packages within supported kinds. No new seller entitlement gates: supported effects remain approved Professional commission terms; unknown keys cannot gate drafting or fabricate quota. SH-016 action keys are activate_profile, public_visibility, publish_offering, respond_to_gig, participate_in_order; payout stays Payment-owned.

Owner status/remediation notifications use committed source-event identity, generic status/remediation template and safe authenticated destination; no sensitive provider/Healthcare/hold details. Notifications do not prove readiness. No generic admin force-ready override: each source owner must authorize and record its own correction, followed by reevaluation. Required verification includes stale-resume versus restriction, archive/restore preserving obligations, projection field exclusion, duplicate first-completion award, and reputation version replay. These are implementation acceptance criteria, not tests already executed.

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.

## WA-R038 — Trust evidence provenance and screening boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

VerificationConsent remains a screening-context linkage: canonical ConsentLogId, identified User/subject, check type, provider, purpose, requirement/package revision and linked check. Generic acceptedAt/IP/user-agent fields are compatibility evidence only and cannot independently validate consent. New linkage requires canonical consent proof and current applicability checks; migration preserves unknown provenance without inventing consent. Each check has exactly one typed subject consistent with its User and optional Professional/Candidate profile; employer-requested screening additionally requires identified Organization/requester membership, Job/Application context, purpose and approved permissible-purpose evidence. Employer sponsorship is not activated by this technical representation.

Adopt the existing minimum Trust §9 check/package/badge graphs. Terminal checks never reopen; recheck is a new linked attempt with current consent/payment/requirement proof. License credential identity stays stable, but every verification/refresh/revocation creates an immutable evidence revision linked explicitly to its establishing VerificationCheck or authorized manual evidence decision. Current credential projection points to a valid revision; expired/revoked proof is never silently overwritten. Trust owns explicit check/credential-to-Media evidence join records, document kind, evidence revision and retention classification. Media owns bytes/scanning/access. No generic Media ownerType/ownerId joins are introduced.

Trust owns append-only check, credential, package/requirement and badge lifecycle histories with aggregate revision and source evidence, committed with outbox. Its provider effect receipt uses provider/account/eventId/handlerVersion uniqueness, fingerprint, check/credential target, normalized event kind, receivedAt, processing and attempt/recovery status, committed transition/effect refs. Unknown subject/events are quarantined; provider callbacks cannot mark a check passed from an unrecognized state. Short-lived provider report access is fetched on demand through an authorized adapter where supported. If persistence is necessary, reportToken is envelope-encrypted secret material with expiry/key version/rotation and restricted audited access; never public DTO/log/Search. Exact provider capability and retention remain external activation evidence.

Requirement rules are immutable schema-versioned records keyed to supported action, typed subject/target, jurisdiction and accepted classification revision; no free-form JSON policy or new implicit mandatory screening. Supported action vocabulary includes profile activation/publication, Offering publication, Gig response/acceptance, Order participation, Booking participation, Job application and Interview participation only where an explicitly approved requirement policy applies. Optional self-initiated Candidate/Professional screening remains optional; action enum presence does not mandate it. Single provider per package at launch; mixed-provider packages are deferred. Provider selection/check-type/jurisdiction rollout must be evidenced before activation, not inferred from a vendor enum.

Identity checks establish only their named verified identity claim; financial readiness stays Payment-owned; a healthcare credential check establishes that credential only, never BAA or Healthcare lane clearance. Broad platform_verified/gold_trust_check/healthcare_verified badges have no launch issuance or authorization effect without explicit scoped claim definitions; preserve legacy facts without minting misleading composite assurance. Public badge DTOs contain the approved claim label/type, subject profile reference, validity and evidence revision only. A badge never replaces current owner readiness.

FCRA technical evidence must link immutable notice template/version/content hash, identified recipient, approved purpose/check/report revision, delivery attempt and verified delivery outcome, policy/jurisdiction version, legally determined timing anchors, dispute submissions and outcome, final-action authorization and history. Notification delivery receipt is evidence, not a legal conclusion. Exact notice content, channels, required waits, adverse-action transitions and retention remain EXTERNAL_REQUIREMENT; no numeric windows or automated adverse decisions are approved here. Required tests cover consent-link mismatch, recheck history, expired supporting evidence, duplicate/late callback, secret exclusion and subject-context mismatch.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P16

A Professional may report completion or no-show for an authorized service session. Authorized support may confirm, correct or adjudicate the service-performance state where policy permits; the Customer can contest the report. Preserve immutable report/correction history, reporting actor and authority, occurrence/recorded time, evidence references, affected session and which participant allegedly failed to attend. A correction references the original; it does not erase it. Reported outcome and contested/adjudicated status are distinguishable, so a Professional assertion is never represented as independent support verification.

Completion/no-show status alone must not automatically trigger refund, charge, payout release, forfeiture, review eligibility or any other financial consequence. Order, Payment/Payout, Review/Dispute, Booking and the applicable policy owner each evaluate their owned consequences from current authorized evidence. A single session report never proves full multi-session Order completion. Clock passage does not fabricate a performance report.


## WA-R049 — Calendar connections, parent references and Location reads

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Booking owns CalendarConnection semantics and provider event mappings through SH-067. Canonical access mode is a controlled enum mapped to allowed operations; freeBusyOnly/metadataReadAllowed/eventWriteAllowed and legacy accessMode text are derived compatibility projections, never independent authority. Effective permission is the intersection of current canonical Consent proof, requested canonical mode, current provider scopes and current Role authority. Conflicting legacy fields block writes until normalized; scope strings alone never establish Consent. Preserve consent version/proof and provider account/calendar identity privately.

Expose `synchronizeContextCalendarEvent.v1` and `cancelContextCalendarEvent.v1` through the Booking-owned Calendar service. Input: authenticated owner service context, typed parent `{kind: booking|job_interview, id, revision}`, canonical connection reference, current schedule `{start,end,timeZone}`, operation idempotency key and owner-issued participant/authority decision references. The service validates the parent through its owner and connection permissions; Interview remains its lifecycle owner and is never converted into Booking. Output: normalized pending/applied/rejected/reconcile_required state, stable mapping ID, parent revision, effect receipt and safe reason. No raw OAuth secret or provider response leaves the adapter. Provider event IDs are private mapping attributes, distinct from Booking/Interview IDs, connection IDs and orchestration IDs. Legacy provider reference fields are read-only correlation projections pending migration.

One mapping per connection/calendar/typed parent is current; record every schedule revision and provider effect receipt. Serializing on that mapping and rejecting stale revisions prevents an old reschedule from overwriting the new one. Cancellation targets the mapped event and revision, including replacement lineage; retries reuse logical effect identity. Ambiguous provider timeout produces reconcile_required and owner provider-state lookup before a second create. Disconnect/revocation disables further writes and invalidates sync readiness; provider deletion acknowledgement is distinct from local disconnect. A provider success never changes Booking or Interview acceptance/performance state. Interview's P18 past-slot guard belongs to Interview even when a calendar entry remains visible.

Booking exact-location data is a non-authorizing cache of Location's versioned source reference. Keep Location-owned record identity/source revision and minimal scheduling metadata, not an independent reveal policy. `getBookingOwnerFacts` supplies Booking id/revision, Order/session authorization reference, current status, start/end, participant references and overtime policy. Location combines fresh facts with its own reveal rules. An unavailable/mismatched Location decision denies exact disclosure; cached exact coordinates/address cannot bypass it. Location revocation or source change invalidates caches and credentials; delayed events require current owner revalidation at use. Exact addresses, provider event payloads and credentials stay out of public events/search.

Verify consent withdrawal versus sync, mismatched legacy modes, replacement/cancel race, ambiguous create response, old provider callback, cross-parent mapping attempts and reveal after cache revocation. Provider capability verification, numerical TTL configuration and forward mapping migration remain required before production.


## WA-R050 — Media stewardship, access evidence and export artifacts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Physical code/repository stewardship for contextual attachment joins follows their semantic owner: OrderFile belongs in Transaction / Order; MessageMedia in Messaging; ProfessionalProfileMedia in Professional Eligibility; OfferingMedia in Marketplace Supply; candidate/resume associations in Candidate Application. Any additional explicit association is placed in its parent business owner, not in a generic Media ownership repository. Prisma remains one coordinated schema/migration surface; storage placement is not lifecycle ownership. Media repositories mutate only Media assets, versions, renditions, upload sessions, grants and technical proof. Owners create/detach contextual joins after Media readiness checks; cross-owner cascade deletion is prohibited without Privacy disposition. This settles MFA-UR-03 without requesting cosmetic table migration.

Keep three distinct identities: contextual owner authorization/grant, Media transport grant/token, and actual delivery observation. `requestMediaAccess` receives authenticated actor/service, exact Media version, purpose/action, owner context and current decision proof; Media rechecks safety, sensitivity, expiry and revocation. Agreement document-view/download grants are reusable within bounded validity and current authorization; a renewed grant is a new decision linked to its predecessor. No perpetual renewal or automatic download entitlement follows possession. Issuance alone never marks `used` or completion. For reusable access, first-use is observation evidence, not terminal state; one-time transport policy may consume its own token atomically only when expressly specified, without consuming a Digital Goods logical-download allowance. Old ambiguous `used` values require migration classification and cannot silently deny an otherwise approved reusable flow.

Digital Goods duplicate filename/mime/size/checksum/version fields are immutable purchased/delivered version snapshots only. Current Media availability, safety, quarantine, deletion and access decisions govern each serving attempt; historical snapshot values never authorize bytes. The source identity cannot drift to a new asset version under an old purchase merely because metadata matches.

Privacy export bundle creation uses existing `createMediaUploadSession` with Privacy job/bundle/version context and owner authorization, then uploads through the returned Media-owned bounded mechanism, then `completeMediaUpload`. Completion is asynchronous if validation/scanning/processing remains; `getMediaUploadStatus` and `getMediaReadiness` return finalized version/readiness evidence. Privacy may report artifact-ready only for a private ready version and its complete owner contribution manifest, never merely upload acceptance. Logical key is Privacy job+bundle revision; same key replays session/artifact result, changed bytes conflict or require a new revision. A failed scan prevents distribution; incomplete upload resumes/retries the same session where supported, otherwise supersedes it with recorded lineage. Privacy evaluates export requester/current authority, Media applies SH-127, and sensitive proof follows WA-R023. No public export URL is persisted.

Upload-session state is separate from MediaAsset state: initiated→uploading→uploaded→validating→scanning (when required)→processing (when required)→completed, with failed/rejected/cancelled/expired terminal attempts. Required stages cannot be skipped by provider success. A retry after terminal failure creates a linked new attempt; ready/frozen/deleted are asset states only. Immutable policy revision identity is stored on the attempt; changes do not rewrite historical validation criteria, while current safety can still block serving. Scanner callbacks are required only if a selected provider uses callbacks; when used they pass canonical verification/dedupe/normalization.

Production scanner selection, encryption/key qualification, legal retention and broad public-original exposure remain separately gated; do not infer vendor approval. Verify detached associations retaining shared bytes, concurrent access/revocation, grant renewal, failed download not consuming allowance, stale snapshot quarantine, export failure/retry and policy revision replay before activation.


## WA-R051 — Video generation recovery and controlled delivery

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Retain terminal live room generations. Authorized recovery of failed/expired/cancelled infrastructure creates a new monotonically identified generation under the same Booking or JobInterview parent, after current owner readiness/authority permits recovery. It does not reset the terminal generation or the parent lifecycle. Exactly one current generation selector exists per typed parent, changed under aggregate serialization; one provider-create effect identity per generation prevents duplicate rooms on retry. Ambiguous create outcome must reconcile that same generation before another provision. Once a generation is superseded, credentials for it are ineligible and revocation/closure is requested from the adapter. Existing parent-unique room rows require a forward generation representation; no implementation may bypass their constraint by duplicate insert.

`provisionBookingVideoRoom` / `provisionInterviewVideoRoom` bind parent ID/revision, generation, owner readiness proof, authorized participant scope and logical provisioning key; output generation ID/state/effect receipt. `issueVideoJoinCredential` rechecks current parent schedule/status/participant rights and current generation. Validity is bounded by the parent-owned approved join policy and server time; Booking supplies overtimeGraceMinutes, Interview supplies its own current schedule policy. No local early-join/overtime default exists; missing required numerical policy blocks activation of that path. Persistent Video access proof records actor, typed parent/revision, room generation, action, allow/deny reason, policy/decision refs, issuance expiry, request time and provider effect confirmation where present. Domain proof commits before credential disclosure; Audit transport cannot substitute it. Provider membership observation is separate from issuance and from service completion.

For on-demand ingest, Video requests purpose-bound Media access for an exact ready source version through SH-127. Default architectural transport is a bounded server-side transfer coordinated by Media to the qualified StreamingVideoProviderPort upload destination; an adapter may use a short-lived provider-fetch URL only when Media authorizes that purpose and selected provider capability verifies it. Video never reads R2 credentials/keys or exposes permanent source URLs. Retries bind source version/checksum and ingest effect identity; source quarantine/revocation prevents new transfer, and conflicting late callbacks cannot activate superseded content. Provider capability/limits/expiry and sensitive-content qualification remain external gates, not assumed vendor behavior.

Thumbnails use an explicit Media rendition/asset reference owned by the Video presentation relationship. Provider thumbnailUrl is private correlation only. The source owner must approve public-safe rendition eligibility and Media safety before client/Search exposure; no direct provider URL projection. CourseDetails.offeringId remains canonical course identity; any redundant Video offeringId must agree, with mismatches quarantined for migration. isDownloadable remains non-authorizing compatibility metadata and cannot bypass Digital Goods policy.

Playback grants are reusable within approved validity, current Order/Digital Goods entitlement and Video readiness. Multiple independently authorized playback grants may coexist; no single-device/session product restriction is invented. Same logical grant issuance replays; fresh session request can create a new grant. First credential use is evidence, not a terminal used status. Revocation/expiry denies subsequent issuance even if a worker is late; provider credential limits must bound already-issued exposure. Playback is not a logical file download and does not consume P10 allowances. Retain start/completion proof at its correct evidence strength; a client progress callback alone cannot prove verified completion. High-frequency progress is optional sampled/coalesced analytics, off until privacy/volume policy exists, and never required authoritative lifecycle history.

Verify concurrent recovery, old-generation join, unknown provider result, provider-create timeout, cancelled/past parent, fresh participant revocation, quarantined ingest, superseded callback, private thumbnail leak and repeated playback without false consumption. Healthcare vendor approval, live provider choice, retained-proof durations and adapter revocation/TTL capability remain prerequisites.


## WA-R052 — Commerce source events and projection contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Owner events carry immutable eventId, event name/schemaVersion, aggregate ID/revision, occurredAt, causationId/correlationId, safe typed actor reference and minimum immutable outcome evidence. Write owner history and outbox atomically. Consumers retain durable semantic effect identity and last applied source version beyond transport inbox expiry; duplicate aliases cannot repeat effects. Public commands and queries remain distinct from facts.

| Producer contract | Minimum scoped payload | Consumer effect |
| --- | --- | --- |
| order.outcome_changed.v1 | Order ID/revision, source kind/id, frozen purchase revision, operational outcome, dispute cycle reference if relevant, authorized disposition reference | Gig records matching assignment projection; Digital Goods/Booking reevaluate their own current rights; no automatic financial or review action |
| booking.performance_reported.v1 | Booking ID/revision, Order/session authorization ref, completed/no_show allegation, reporting actor, alleged absentee for no-show, evidence ref, contest state | Order records evidence and evaluates policy; never treats allegation as automatic package completion |
| booking.performance_adjudicated.v1 | same identity plus support authority, prior report ref, correction/adjudication outcome and evidence | Order reevaluates; preserve original report and prior decisions |
| booking.confirmed.v1 / rescheduled.v1 / cancelled.v1 | Booking ID/revision, Order/session ref, schedule revision, authorized participant refs, safe reason | Video/calendar/Messaging setup or invalidation through their owners; Notification receives source-directed safe recipient references |
| review.reputation_changed.v1 | Professional ID, source/projection version and changed Review ID/revision; no private comment/evidence | Professional/Search refresh via getProfessionalReputation.v1, apply only current version |

Booking owns BookingEventActor and BookingLocationType vocabularies. Domain actor values distinguish customer/professional/support/system and retain authenticated User attribution where lawful; no free-text role can authorize a transition. Its existing completed/no_show event aliases normalize to performance-report facts, not adjudicated or commercial-completion facts. Existing proposed booking.* / calendar.* names in §12 become the owner event namespace; only the specific registered semantics qualify integration. Existing OrderCreated/OrderCompleted-style aliases normalize at ingress to their owner versioned equivalent with original event identity, never publish duplicate semantic facts. This table is architecture, not evidence of implemented producer/consumer compatibility.

Review owns `getProfessionalReputation.v1`: request Professional ID with caller context and optional known projection version; response ratingAverage (nullable when count=0), ratingCount, source revision, projection revision, asOf and readiness/staleness result. Fractional aggregate is valid under P06. A refresh event invalidates/reloads this query; consumers cannot recompute from private Review rows or mistake missing/unready result for a zero rating. Hidden/removed Reviews withdraw exactly their existing contribution; revision updates do not add a rating count. Bilateral race, tombstone and replay fixtures are required before freeze.

Notification routing remains source-selected and asynchronous: material accepted-term/proposal changes and appointment/case participant-visible changes carry an authorized destination and affected participant references; failure to deliver cannot roll back owner truth. Private adjudication/evidence never enters participant notifications. P19 uses the Order conversation with Booking/case links; those links do not expand access. Optional viewed/shortlisted alerts stay inactive absent an approved trigger/template policy. This identifies source facts; final template/recipient fan-out matrix remains with Notification convergence.

Gamification may qualify Order completion or eligible reputation changes only through its versioned rule catalog and original source event identity; propagated Gig completion is not a second earning fact. Hold consumers evaluate scoped action decisions and preserve restriction provenance; release only triggers reevaluation, never automatic restoration. Moderation commands use authorized target/action/revision plus durable receipt and local owner execution. Exact shared action, assurance, reward rule and Notification contracts still require canonical cross-rail convergence; this owner event contract does not promote adjacent proposed SH operations.

## WA-R071 — Purpose-specific Location facts and disclosure

Booking supplies fresh versioned schedule/participant/performance/source facts to Location; source caches never authorize. Missing active-service evidence denies exact disclosure.

## WA-R072 — Hiring compatibility and forward migration stewardship

Hiring owns JobMedia association stewardship; Media remains byte/readiness/access owner. Forward compatibility migration is additive, provenance-qualified and integration-owned; no schema change is implied.

## WA-R073 — Interview access interval and bounded credentials

Interview is the parent authority for Video credentials. Launch join interval is half-open scheduled time, without implicit grace; bound credential expiry to parent/current authority/provider limits and qualify revocation/disconnect separately.
