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
| CL-04 Agreement | Booking/Media | agreement readiness/access decision | Transaction / Order | owner public interface; SH-112 for hash verification | Booking generating/owning Agreement proof |
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
