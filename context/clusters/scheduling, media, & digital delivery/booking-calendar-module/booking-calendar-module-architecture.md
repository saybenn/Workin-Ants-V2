# Booking & Calendar Module Architecture

> **Module ID:** `booking_calendar`  
> **Module name:** Booking & Calendar Module  
> **Module type:** `domain_capability_hybrid`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Repository target:** `context/clusters/scheduling, media, & digital delivery/booking-calendar-module/booking-calendar-module-architecture.md`\
> **Document status:** Target Module architecture derived from the current Workin Ants Project Overview, Deep Module Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Registry, Booking Module Architecture Extract, and CL-05 architecture/build plan. Proposed rulings and unresolved decisions are explicitly labeled.  
> **Intended audience:** coding agents, developers, reviewers, maintainers, architecture reviewers, and engineers implementing Booking-owned provider/workflow behavior.  
> **Update rule:** update this file whenever a binding Booking ownership boundary, lifecycle rule, public contract, concurrency rule, provider contract, privacy behavior, or cross-Module dependency changes. Build progress must not silently redefine this architecture.

---

## 1. Module Header

### Relationship to root architecture

This Module is subordinate to the root Workin Ants architecture and project-wide source-of-truth rules. Root architecture owns platform-wide decisions such as actor identity, shared infrastructure, code standards, database conventions, authorization structure, and cross-cutting operation ownership.

If this file conflicts with a binding root rule:

1. preserve confirmed source-of-truth ownership;
2. record the conflict;
3. update the affected architecture before implementation proceeds;
4. do not make implementation convenience the deciding authority.

The current Project Overview confirms the platform laws that materially constrain this Module: `Order` is transaction truth, `CustomerProfile` is buyer actor truth, `TrackEntitlementGrant` is commercial-policy truth, `ConsentLog` is consent proof, `ComplianceHold` is the reusable stop sign, and providers are rails rather than Workin Ants source truth.

### Relationship to CL-05 architecture

CL-05 coordinates Booking & Calendar, Video Session, Media / File Access, and Digital Goods Access. The Cluster does not own Booking lifecycle state. This Module architecture is the implementation authority for Booking-local policies while remaining subordinate to Cluster sequencing and cross-Module rulings.

The CL-05 build plan places Booking implementation primarily in Cluster features:

- **07** Professional Availability, Slot Search, and Atomic Booking Holds;
- **08** Order-Gated Booking Confirmation and Booking Lifecycle;
- **09** Cronofy Calendar Connection and Free/Busy Synchronization;
- **10** Booking Orchestration, Calendar Writeback, Thread, Location Check, and Notification Requests;
- later participation in **13** cross-Cluster guardrail verification, **14** Privacy target execution, and **15** production hardening.

### Evidence-status vocabulary

- **Confirmed** — directly established by the current Deep Module Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, Project Overview, CL-05 architecture/build plan, or a confirmed Canonical Shared Operation.
- **Reasonable inference** — strongly implied by confirmed records and workflows but not itself a binding schema or lifecycle ruling.
- **Proposed Ruling** — a necessary implementation-grade decision supported by current evidence but not yet independently approved as binding architecture.
- **Unresolved Decision** — current evidence identifies a conflict or missing rule that must not be silently settled by implementation.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own paid live-service scheduling attached to Orders, including professional recurring availability, external-calendar blocking, temporary slot reservation, atomic overlap prevention, Booking lifecycle truth, calendar connection/synchronization state, calendar-provider deduplication, and Booking-specific downstream orchestration evidence.

### Goal

Turn a requested service interval into one authoritative, conflict-free `Booking` only after required external business gates pass, while ensuring calendar providers, Order/payment state, Agreement state, entitlements, video rooms, exact-location policy, notifications, messaging, audit, and privacy orchestration remain owned by their proper Modules.

### What enters

Typical authoritative inputs are:

- authenticated actor context from Identity & Access;
- authorization decisions from Role / Authority;
- `CustomerProfile` buyer actor context;
- `ProfessionalProfile` seller/service-provider context;
- service scheduling facts such as duration or delivery mode from the appropriate source owner;
- requested interval and IANA display/recurrence timezone;
- current `Order` booking entitlement and participant facts;
- Agreement readiness when the Order requires an Agreement;
- active `TrackEntitlementGrant` decisions such as priority scheduling;
- calendar consent/version proof;
- `ComplianceHold` decisions where the requested action is hold-sensitive;
- Location Safety decisions for exact-location reveal;
- provider callbacks and free/busy data from Cronofy through the Booking-owned provider adapter;
- privacy instructions from Privacy / Data Erasure;
- downstream acknowledgments from Messaging, Notification, Video Session, and other owner interfaces.

### What leaves

The Module produces:

- recurring `AvailabilityRule` truth;
- normalized `BusyWindow` intervals;
- `BookingHold` temporary reservations;
- `BookingSlotLock` atomic interval reservations;
- authoritative `Booking` records;
- append-only `BookingEvent` history;
- `CalendarConnection` source/provider connection state;
- `ProcessedCalendarEvent` provider-event dedupe truth;
- calendar writeback state attached to Booking;
- `BookingOrchestrationRun` and `BookingOrchestrationStep` records describing Booking-owned downstream request progress;
- versioned domain events/outbox messages describing Booking facts that occurred;
- notification, messaging, location, video, audit, and observability requests through owner interfaces;
- privacy inventory/execution results for Booking-owned records and calendar-provider references.

### Business/capability transformation

```text
Professional recurring availability
+ BusyWindow exclusions
+ buyer/customer actor
+ requested UTC interval
+ current priority entitlement decision
+ atomic interval reservation

→ BookingHold + BookingSlotLock

then

valid active hold/lock
+ authoritative Order booking entitlement
+ required Agreement readiness
+ applicable ComplianceHold decision

→ authoritative confirmed Booking + BookingEvent

then

Booking transition
→ Booking-owned orchestration run
→ calendar writeback + owner-interface requests
→ provider/domain acknowledgments
→ deterministic orchestration status
```

### Why this deserves its own Module boundary

Scheduling has its own durable truth and invariants that neither Order nor external calendar providers can safely own:

- recurring availability is different from transaction entitlement;
- time-interval contention requires database-level concurrency control;
- external free/busy data must be privacy-minimized and normalized;
- booking confirmation is a domain transition, not a provider callback;
- rescheduling/cancellation is scheduling truth even when downstream payment/refund effects occur elsewhere;
- calendar webhook dedupe and calendar connection lifecycle are specific provider-domain responsibilities;
- downstream orchestration must track requests without taking ownership of Video, Agreement, Notification, Messaging, or Location truth.

---

## 3. Owned Truth

### Owned models / records

| Record | Plain-English meaning | Ownership status |
| --- | --- | --- |
| `AvailabilityRule` | Recurring local-wall-clock availability for a `ProfessionalProfile`, interpreted using an IANA timezone and effective dates. | Confirmed |
| `CalendarConnection` | Workin Ants record of a linked professional calendar, granted access mode/scopes, provider references, and connection/sync state. | Confirmed |
| `BusyWindow` | UTC interval during which a Professional is unavailable, sourced manually, from a Booking, an external calendar, or system logic. | Confirmed |
| `BookingHold` | Temporary reservation of a selected service interval while upstream Order/Agreement steps complete. | Confirmed |
| `BookingSlotLock` | Server-side atomic reservation preventing prohibited overlapping paid bookings for the same Professional/time interval. | Confirmed |
| `Booking` | Authoritative Workin Ants scheduled paid live-service appointment attached to an `Order`. | Confirmed |
| `BookingEvent` | Append-only domain history of meaningful Booking lifecycle transitions/actions. | Confirmed |
| `ProcessedCalendarEvent` | Booking-owned dedupe/processing record for one provider calendar event. | Confirmed |
| `BookingOrchestrationRun` | Durable record that a Booking transition triggered a set of Booking-owned downstream requests. | Confirmed |
| `BookingOrchestrationStep` | Durable status of one Booking orchestration request/acknowledgment, without owning the downstream target lifecycle. | Confirmed |

### Owned enums / vocabularies

Confirmed by the Deep Module Registry:

- `AvailabilityRuleSource`
- `CalendarConnectionStatus`
- `CalendarSourceProvider`
- `CalendarIntegrationProvider`
- `CalendarSyncDirection`
- `BusyWindowSource`
- `BookingHoldStatus`
- `BookingStatus`
- `CalendarEventSyncStatus`
- `CalendarAccessMode`
- `CalendarConnectionProviderStatus`
- `BookingSlotLockStatus`
- `BookingOrchestrationStatus`
- `BookingOrchestrationStepType`
- `BookingOrchestrationStepStatus`
- `CalendarProviderEventType`
- `CalendarProviderEventStatus`

**Proposed Ruling PR-BC-01:** `BookingEventActor` and `BookingLocationType` are Booking-owned vocabulary even though the Deep Module registry’s owned-enum list omits them. The Prisma schema uses them only for Booking-owned records and the Ubiquitous Language associates `BookingLocationType` with Booking.

### Lifecycles owned

- Calendar connection lifecycle.
- Booking hold lifecycle.
- Booking slot-lock lifecycle.
- Booking lifecycle.
- Calendar-provider event processing lifecycle.
- Booking orchestration run/step lifecycles.
- Availability rule activation/deactivation behavior, although `AvailabilityRule` currently uses `isActive` rather than a lifecycle enum.

### Source-of-truth records

- `Booking` — paid-service scheduling truth.
- `BookingHold` — pre-confirmation selected-slot reservation truth.
- `BookingSlotLock` — atomic slot-reservation truth.
- `CalendarConnection` — linked-calendar state within Workin Ants.
- `BusyWindow` — normalized unavailability truth used by Booking slot computation.
- `ProcessedCalendarEvent` — calendar-provider event dedupe truth.
- `BookingOrchestrationRun/Step` — Booking workflow request/acknowledgment truth.

### Domain event / ledger truth

`BookingEvent` is Booking-domain evidence. It must not be replaced by:

- generic `AuditEvent`;
- `AccessAuditLog`;
- `ProcessedCalendarEvent`;
- `IntegrationFailure`;
- queue/job state;
- Cronofy/provider event history.

### Projections / snapshots owned

Booking may own local historical snapshots that explain a scheduling decision, including:

- buyer/professional display timezones;
- priority scheduling result applied to the hold/lock/booking;
- source entitlement/grant reference where schema supports it;
- provider availability hash where used to detect stale slot data;
- calendar writeback references/state;
- permitted scheduling-context location snapshot fields subject to the Location Safety ruling below.

Historical snapshots must never be used as current subscription/entitlement truth when a current re-check is required.

### Policies and invariants owned

Booking & Calendar owns:

- recurrence expansion rules for `AvailabilityRule`;
- UTC normalization for authoritative instants;
- which BusyWindow/Booking/lock states block a slot;
- server-side availability recheck immediately before reservation;
- interval-conflict policy for paid service bookings;
- hold duration/expiration policy once approved/configured;
- hold-to-lock pairing and conversion semantics;
- Booking transition graph;
- reschedule reservation-before-switch rule;
- calendar connection state mapping after provider results;
- free/busy minimization policy inside the calendar adapter;
- calendar webhook application rules after verification/dedupe;
- which downstream orchestration steps are required for a Booking transition;
- which orchestration failures are critical versus noncritical;
- Booking-specific idempotency semantic keys;
- safe reason-code mapping for public Booking decisions.

---

## 4. Explicit Non-Ownership

Coding agents must not move the following responsibilities into Booking & Calendar.

| Adjacent owner | Truth that remains external | Booking may consume / request | Booking must not create |
| --- | --- | --- | --- |
| Identity & Access | `User`, authentication/session/security truth | resolved actor | `bookingAuth.ts`, local session parser, local identity records |
| Role / Authority | platform/organization/ownership permission interpretation | authorization decision using Booking-supplied relationship facts | local RBAC engine, `isAdmin` helper, duplicated permission middleware |
| Customer / Buyer Profile | `CustomerProfile` lifecycle and buyer actor identity | resolved commercial buyer | buyer-profile shadow table or `isCustomer` flag |
| Professional Eligibility | Professional seller/readiness composition | Professional facts/readiness if action requires it | local professional-ready boolean or copied compliance logic |
| Track Subscription & Entitlement | plans, subscriptions, grants, usage periods/counters | priority scheduling decision and usage receipt | `isPriorityCustomer`, `isPremium`, local quota/plan truth |
| Transaction / Order | `Order`, `OrderEvent`, purchase/payment/refund/dispute transaction truth | booking entitlement and Order participants; booking reference attachment through public interface | payment status, Stripe checks, refund logic, Order mutations |
| Transaction / Order Agreement | Agreement templates, generation, electronic consent, signatures, final document state | Agreement readiness or an explicit Agreement command | PDF generation, signature state, Agreement repository |
| Video Session | `BookingVideoRoom`, provider room state, join tokens | room provisioning/cancel request through Video public interface | Daily/Agora room client, token generation, VideoRoom mutation |
| Job Interview | hiring-side interview schedule/lifecycle | no ownership; may share low-level calendar mechanisms only through approved contracts | reuse Booking/BookingHold/BookingSlotLock for interviews |
| Consent & Disclosure | generic `ConsentLog`, active consent versions | consent proof / record proof via canonical shared operations | calendar-specific consent table or generic consent repository |
| Location Safety | `LocationReveal`, fuzzying/reveal/decryption policy | reveal decision/proof | `canShowAddress`, local reveal lifecycle, local location safety engine |
| Notification | `Notification`, `NotificationDelivery`, channel/provider delivery | notification request with safe payload | SES/SMS/push provider code, delivery attempts |
| Messaging | `Thread`, `ThreadParticipant`, `Message` | ensure context Thread | booking-specific chat store or participant authorization engine |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog` | append generic/sensitive evidence | booking audit tables duplicating generic audit |
| Observability / Ops | `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident` | structured telemetry/failure recording | local generic failure/incident/queue ledger |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption` | privacy instruction execution protocol | `bookingPrivacyRequest`, local retention exemption system |
| Healthcare / Regulated Services | healthcare readiness/data-boundary policy | conditional decision when a Booking context is healthcare-sensitive | Booking healthcare boolean or healthcare policy engine |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense/search projection | no Booking projection confirmed; request refresh only if later approved | Typesense client/indexer or SearchUpsertEvent writes |
| Content Moderation / Legal Notice | moderation/legal case and decision truth | owner-local execution only if a future moderation action targets Booking data | local moderation adjudication or DMCA logic |

### Provider non-ownership

Cronofy is calendar infrastructure, not scheduling truth. Provider availability, OAuth state, event IDs, and writeback results are inputs/evidence applied by Booking & Calendar. They never replace `AvailabilityRule`, `BusyWindow`, `BookingHold`, `BookingSlotLock`, `Booking`, or `BookingEvent`.

---

## 5. Module Architecture Principles

1. **Booking is scheduling truth; Order is transaction truth.** Booking never decides payment success from Stripe/provider state.
2. **Pre-confirmation reservation lives in BookingHold/BookingSlotLock.** A temporary hold is not a paid Booking.
3. **Authoritative instants are UTC.** Local-wall-clock strings are allowed only for recurring availability; IANA timezone identifies recurrence/display context.
4. **Every slot is rechecked server-side at reservation time.** UI slot lists are advisory projections, not reservation truth.
5. **Overlap prevention is a database invariant.** Never use in-memory mutexes for paid scheduling.
6. **Priority scheduling cannot bypass overlap or Order gates.** It changes only the locally approved scheduling policy and is snapshotted from external entitlement truth.
7. **Provider data is minimized.** Free/busy sync does not persist external event descriptions, attendee lists, private locations, or unnecessary provider payloads.
8. **Provider callbacks are verified, deduplicated, translated, then applied.** No provider callback directly mutates Booking truth before these gates.
9. **Provider failure is not business failure.** A confirmed Workin Ants Booking remains confirmed when calendar writeback is temporarily unavailable unless an explicit Booking-domain rule says otherwise.
10. **BookingEvent is domain history.** Audit and observability supplement it rather than replacing it.
11. **Downstream orchestration owns sequence, not participant truth.** A completed step proves a request/acknowledgment; it does not own the downstream aggregate’s state.
12. **Cross-Module reads use public interfaces.** Shared database placement is not permission for direct repository access.
13. **All external effects are idempotent and reconcilable.** Provider timeouts and retries must not create duplicate calendar events, threads, notifications, or video rooms.
14. **Exact location remains Location Safety-controlled.** Booking may hold only the explicitly approved scheduling snapshot/cache fields.
15. **Privacy orchestration remains Privacy-owned.** Booking only inventories and executes against its own records/provider references.
16. **No generic delivery engine.** Booking logic remains under Booking & Calendar; CL-05 does not gain a second lifecycle.

### Binding MVP interpretation of pre-confirmation states

The CL-05 build plan states that a valid hold/lock is converted into an authoritative Booking **after** Order/Agreement readiness passes.

**Binding Module rule:** the standard MVP flow must not create a `Booking` row merely to represent `held`, `awaiting_agreement`, or `awaiting_payment` state. `BookingHold`/`BookingSlotLock` remain pre-confirmation truth. A new normal Booking is created as `confirmed` only after the required gate succeeds. Existing schema enum values `draft`, `held`, `awaiting_agreement`, and `awaiting_payment` are reserved/legacy until a later binding workflow explicitly requires them.

This avoids two competing pre-confirmation lifecycles.

---

## 6. Proposed Folder / Code Structure

The root repository/code standards remain final authority. If root conventions differ, map the responsibilities below into the root structure rather than creating a second style.

```text
src/
└── modules/
    └── booking-calendar/
        ├── components/
        │   ├── availability-editor/
        │   ├── slot-picker/
        │   ├── calendar-settings/
        │   ├── booking-status/
        │   └── delivery-setup-status/
        ├── actions/
        │   └── thin server-action adapters only
        ├── application/
        │   ├── commands/
        │   │   ├── upsert-availability-rule.ts
        │   │   ├── create-booking-hold.ts
        │   │   ├── release-booking-hold.ts
        │   │   ├── confirm-booking.ts
        │   │   ├── cancel-booking.ts
        │   │   ├── reschedule-booking.ts
        │   │   ├── complete-booking.ts
        │   │   ├── mark-booking-no-show.ts
        │   │   ├── connect-calendar.ts
        │   │   ├── disconnect-calendar.ts
        │   │   └── retry-orchestration-step.ts
        │   ├── queries/
        │   │   ├── list-bookable-slots.ts
        │   │   ├── get-booking.ts
        │   │   ├── list-customer-bookings.ts
        │   │   ├── list-professional-bookings.ts
        │   │   ├── get-calendar-connection.ts
        │   │   └── get-booking-delivery-setup-status.ts
        │   └── services/
        │       ├── booking-confirmation-service.ts
        │       ├── booking-reschedule-service.ts
        │       └── booking-orchestration-service.ts
        ├── domain/
        │   ├── policies/
        │   │   ├── availability-policy.ts
        │   │   ├── slot-conflict-policy.ts
        │   │   ├── booking-transition-policy.ts
        │   │   ├── priority-scheduling-policy.ts
        │   │   └── orchestration-policy.ts
        │   ├── transitions/
        │   │   ├── booking-hold-transitions.ts
        │   │   ├── booking-slot-lock-transitions.ts
        │   │   ├── booking-transitions.ts
        │   │   └── calendar-connection-transitions.ts
        │   ├── events/
        │   │   ├── booking-event-names.ts
        │   │   └── booking-domain-events.ts
        │   └── errors/
        │       └── booking-reason-codes.ts
        ├── contracts/
        │   ├── public-commands.ts
        │   ├── public-queries.ts
        │   ├── owner-facts.ts
        │   ├── domain-events.ts
        │   ├── calendar-provider-port.ts
        │   └── privacy-executor.ts
        ├── infrastructure/
        │   ├── repositories/
        │   │   ├── availability-repository.ts
        │   │   ├── booking-reservation-repository.ts
        │   │   ├── booking-repository.ts
        │   │   ├── calendar-connection-repository.ts
        │   │   └── orchestration-repository.ts
        │   ├── calendar/
        │   │   └── cronofy-adapter.ts
        │   └── workers/
        │       ├── expire-booking-holds.ts
        │       ├── expire-booking-slot-locks.ts
        │       ├── sync-calendar-busy-windows.ts
        │       ├── process-calendar-provider-event.ts
        │       ├── run-booking-orchestration.ts
        │       └── reconcile-calendar-state.ts
        ├── privacy/
        │   ├── enumerate-booking-subject-data.ts
        │   ├── evaluate-booking-retention.ts
        │   └── execute-booking-privacy-instruction.ts
        └── tests/
            ├── unit/
            ├── contract/
            ├── integration/
            ├── concurrency/
            ├── provider/
            ├── privacy/
            └── e2e/
```

### Folder constraints

- Do not add a `payments/`, `agreements/`, `video/`, `notifications/providers/`, `auth/`, `rbac/`, or `privacy-workflow/` implementation under this Module.
- `cronofy-adapter.ts` may contain provider-specific mapping. `calendar-provider-port.ts` must remain provider-neutral.
- Shared queue/idempotency/locking/telemetry/crypto implementations live under the canonical platform shared-operation owners, not inside this tree.
- UI/actions stay thin; domain/application services own transitions and transactions.

---

## 7. Internal Boundaries

| Layer / area | Owns | Must not own |
| --- | --- | --- |
| Delivery/UI | Availability editor, slot picker, Booking status, calendar settings, safe setup/failure states | lifecycle decisions, authorization truth, provider secrets, payment/Agreement state |
| Actions / route handlers | request parsing, runtime validation, actor resolution handoff, application-service call | complete business workflows, direct Prisma mutations across layers |
| Application commands | orchestration of one Booking-owned mutation and external owner decisions | foreign Module persistence, provider-native business logic |
| Application queries | authorized Booking-owned reads and projections | arbitrary cross-domain repository joins |
| Domain policies | slot validity, conflict semantics, Booking transitions, local priority effect, orchestration criticality | entitlement truth, payment truth, generic authorization, Location Safety policy |
| Repositories | Booking-owned Prisma tables and transaction helpers | repositories for Order, Consent, Video, Messaging, Notification, Privacy, Holds |
| Workers | Booking-owned expiration, provider sync, orchestration, reconciliation | generic queue framework, Notification delivery worker, Video provider worker |
| Calendar adapter | Cronofy request/response mapping, minimal scopes, provider IDs, webhook algorithm hooks | Booking transition policy, user-facing provider error leakage |
| Public contracts | stable Booking commands, queries, owner facts, events, privacy executor | hidden Prisma types or provider payload types |
| Privacy executor | Booking-owned data inventory/disposition execution | PrivacyRequest/DataErasureJob lifecycle or independent retention exemptions |

---

## 8. Data Model

### `AvailabilityRule`

**Purpose:** recurring professional availability definition.

**Key relationships:** belongs to `ProfessionalProfile`.

**Authoritative fields:** `professionalProfileId`, `source`, `weekday`, `startTime`, `endTime`, `timezone`, effective dates, `isActive`.

**Important constraints:** unique `(professionalProfileId, weekday, startTime, endTime, timezone)`; index on professional/status.

**Meaning:** `startTime` and `endTime` are recurring local-wall-clock values, not authoritative Booking instants. The Module must validate their format and IANA timezone, expand recurrence deterministically, and handle DST.

**Retention/privacy:** low sensitivity relative to calendar contents but still professional scheduling data; included in subject export/erasure inventory as applicable.

### `CalendarConnection`

**Purpose:** Workin Ants link to one professional external calendar account/calendar and the access granted to Booking & Calendar.

**Key relationships:** `ProfessionalProfile`, optional `ConsentLog`, `BusyWindow`, `Booking`, `ProcessedCalendarEvent`.

**Authoritative lifecycle fields:** `status`, `providerStatus`, `syncDirection`, `accessModeEnum`, timestamps for consent/disconnect/revoke/expire/sync.

**Provider reference fields:** external/Cronofy IDs and opaque `providerCredentialId`.

**Security rule:** `providerCredentialId` is an opaque secret-store/provider credential reference. Raw OAuth access/refresh tokens must never be stored in this model or returned to clients.

**Privacy rule:** requested/granted scopes and free-busy flags must reflect least privilege. Free/busy-only connections must not result in durable storage of titles, descriptions, attendees, or private event locations.

**Schema conflict:** both free-form `accessMode` and enum `accessModeEnum`, plus `freeBusyOnly`, `metadataReadAllowed`, and `eventWriteAllowed`, represent overlapping access semantics. See unresolved decisions.

### `BusyWindow`

**Purpose:** normalized UTC unavailable interval.

**Key relationships:** belongs to `ProfessionalProfile`; may reference `CalendarConnection`.

**Authoritative fields:** `startAt`, `endAt`, `source`, `isPrivate`, provider/source IDs only as needed for reconciliation.

**Privacy fields:** `freeBusyOnly` and `storesPrivateMetadata` support the rule that external calendar content is not copied merely to block time.

**Concurrency:** slot search and hold creation must treat applicable BusyWindows as blockers in the authoritative server-side recheck.

**Retention:** external-calendar-derived windows should generally be deletable/disconnectable through the privacy executor; exact policy follows Privacy instructions and retention facts.

### `BookingHold`

**Purpose:** temporary pre-confirmation selected-slot reservation.

**Key relationships:** optional `Order`, buyer `User`, optional `CustomerProfile`, `ProfessionalProfile`, one SlotLock relation, eventual `Booking`.

**Authoritative fields:** `status`, `slotStartAt`, `slotEndAt`, `expiresAt`, conversion/release timestamps.

**Historical snapshot fields:** `prioritySchedulingApplied`, `priorityEntitlementGrantId`, `priorityRank`, timezones, optional provider availability hash.

**Concurrency:** creation is transactionally paired with the interval lock. An expired hold is invalid even if the expiration worker has not yet updated its status.

**Schema conflict:** `lockId` and `slotLock`/`BookingSlotLock.bookingHoldId` create two possible relationship paths. Do not rely on both. See unresolved decisions.

### `BookingSlotLock`

**Purpose:** database-backed atomic reservation of a Professional/time interval.

**Key relationships:** Professional, optional buyer/order/customer, optional one BookingHold, Booking relation(s).

**Authoritative fields:** `startsAt`, `endsAt`, `status`, `idempotencyKey`, expiration/conversion/release timestamps.

**Uniqueness/concurrency:** `idempotencyKey` is unique; `bookingHoldId` is unique. Database migrations must implement a real non-overlap invariant for states the Booking policy treats as active.

**Critical rule:** an ordinary B-tree index over start/end does not prove overlap prevention. The database must enforce exclusion/range-lock behavior or equivalent serializable transaction semantics.

**Schema concern:** current relation allows `bookings[]`; the intended one-lock-to-one-Booking semantics are not explicitly enforced. See unresolved decisions.

### `Booking`

**Purpose:** authoritative confirmed paid live-service appointment.

**Key relationships:** required `Order`, buyer `User`, optional current `CustomerProfile`, `ProfessionalProfile`, optional CalendarConnection, one source BookingHold, optional SlotLock, optional Video-owned `BookingVideoRoom`, BookingEvent history, orchestration runs/steps, reschedule chain.

**Authoritative fields:** `status`, `locationType`, `slotStartAt`, `slotEndAt`, cancellation/completion/no-show timestamps, reschedule link.

**Historical snapshot fields:** customer/user references, priority decision fields, buyer/professional timezones, permitted location snapshot/cache fields.

**Provider-integration fields:** external calendar/provider IDs and `externalSyncStatus`/error.

**Business rule:** provider writeback state must not substitute for `Booking.status`.

**Cardinality questions:** `orderId` is indexed but not unique, allowing multiple Bookings per Order; `slotLockId` is not unique. Both require explicit business rulings before code relies on multiplicity.

### `BookingEvent`

**Purpose:** append-only Booking transition/action history.

**Authoritative fields:** booking, actor, from/to status, event name, reason, safe metadata, timestamp.

**Transaction rule:** a Booking lifecycle transition and its required BookingEvent append occur in the same database transaction.

**Privacy/audit:** metadata is allowlisted/minimized; it must not contain raw provider payloads, exact address, secrets, or unrelated personal data.

### `ProcessedCalendarEvent`

**Purpose:** calendar-provider event claim/dedupe and processing outcome.

**Uniqueness:** `(provider, providerEventId)` is unique.

**Authoritative fields:** provider/event ID/type, status, target references, payload hash, request ID, processing/failure timestamps.

**Rule:** the provider event must be signature-verified before this record can authorize side effects.

**Schema concern:** enum includes `ignored_duplicate`, but uniqueness prevents a second duplicate row. Updating the original processed row to `ignored_duplicate` would destroy the original result. See Proposed Ruling PR-BC-05.

### `BookingOrchestrationRun`

**Purpose:** one idempotent Booking-owned cross-Module setup/update workflow triggered by a Booking fact/version.

**Key fields:** Booking/Order/triggering actor, `status`, `triggerSource`, unique `idempotencyKey`, timestamps/failure reason.

**Rule:** this record owns workflow progress only. It does not own downstream target state.

### `BookingOrchestrationStep`

**Purpose:** one durable downstream request/acknowledgment within a Booking orchestration run.

**Key fields:** run, Booking, type, status, target/provider references, attempts, safe metadata.

**Concurrency/idempotency:** every external step must have a stable semantic command key even though the current table does not expose a dedicated step idempotency column. The shared idempotent command/job mechanisms must provide it; schema extension may be required if durable per-step identity cannot otherwise be guaranteed.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 AvailabilityRule activation

Current schema uses `isActive` rather than a status enum.

```text
create active rule
→ update recurring definition while authorized
→ deactivate
→ optionally reactivate if business policy allows
```

Rules:

- do not use local-time strings as Booking truth;
- validate `weekday`, `startTime < endTime`, IANA timezone, effective date range;
- changes affect future slot projection and must not rewrite existing Bookings.

### 9.2 CalendarConnection lifecycle

```text
pending_consent
  → active
  → disconnected | revoked | expired | failed
```

Transition owner: Booking & Calendar application service after Consent/provider results.

Provider status is separate:

```text
pending → authorized | denied | revoked | expired | disconnected | provider_error
```

Rules:

- `active` requires required Consent proof plus successful provider authorization;
- `revoked`/`expired` stop future sync until an explicitly authorized reconnection flow occurs;
- provider errors do not silently recreate authorization;
- no client-controlled direct status changes.

### 9.3 BookingHold lifecycle

```text
active
  → converted
  → expired
  → released
  → failed
```

- `converted` only as part of successful Booking confirmation.
- `expired` if server clock is past `expiresAt`; worker lag cannot keep it usable.
- `released` for explicit abandonment/cancellation/gate failure.
- `failed` is reserved for owner-local reservation failure requiring explicit reason.
- terminal states do not reopen; a new hold is created instead.

### 9.4 BookingSlotLock lifecycle

```text
active
  → converted
  → released
  → expired
  → failed
```

- acquisition is atomic with reservation proof;
- an active lock blocks prohibited overlap;
- conversion is part of Booking confirmation transaction;
- released/expired/failed locks never reactivate;
- a new reservation receives a new lock.

### 9.5 Booking lifecycle — binding MVP graph

Under the binding pre-confirmation rule, normal MVP creation begins at `confirmed`.

```text
(no Booking row)
  → confirmed
      → completed
      → cancelled
      → no_show
      → rescheduled  -- old Booking becomes historical terminal record
                       and a new confirmed Booking is created for the new slot
```

Reserved/nonstandard enum values in the current schema:

- `draft`
- `held`
- `awaiting_agreement`
- `awaiting_payment`
- `expired`
- `external_sync_failed`

They must not be introduced into the normal MVP transition graph without an architecture update.

**Proposed Ruling PR-BC-02:** `external_sync_failed` should not be used as core Booking lifecycle state. `externalSyncStatus=failed` already represents calendar provider/writeback failure. A provider outage must not transform a valid confirmed appointment into a different business lifecycle. If schema cleanup is approved later, deprecate/remove the BookingStatus value rather than migrating confirmed Bookings into it.

### 9.6 Reschedule semantics

Reschedule is not an in-place timestamp overwrite.

```text
confirmed Booking A
→ acquire new hold/interval lock for requested slot
→ validate current Order/Agreement/hold gates
→ create confirmed Booking B with rescheduledFromBookingId=A.id
→ mark Booking A = rescheduled
→ append BookingEvent(s)
→ publish downstream change facts
```

If the new reservation fails, Booking A remains unchanged.

### 9.7 ProcessedCalendarEvent lifecycle

Expected original event lifecycle:

```text
received → processed | ignored_out_of_scope | failed
```

**Proposed Ruling PR-BC-05:** duplicate callbacks do not change the first event’s status to `ignored_duplicate`. The unique provider/event claim rejects a duplicate before domain side effects; duplicate observation belongs in telemetry or a separate attempt log if later required. Treat `ignored_duplicate` as reserved until the schema contract is clarified.

### 9.8 BookingOrchestrationRun

```text
pending → running → completed
                  → partially_completed
                  → failed
                  → cancelled
```

Run aggregation policy remains Booking-owned.

### 9.9 BookingOrchestrationStep

```text
pending → running → completed
                  → skipped
                  → retrying → running
                  → failed
                  → cancelled
```

Transient technical failures may retry. Business denials or invalid target lifecycle states are not blindly retried.

---

## 10. Commands

The signatures below are stable conceptual contracts; transport follows root code standards.

### `upsertAvailabilityRule`

- **Purpose:** create/update a professional recurring availability rule.
- **Actor/context:** authenticated actor authorized for the `ProfessionalProfile`.
- **Inputs:** professionalProfileId, weekday, local start/end, IANA timezone, effective range, source where allowed.
- **Preconditions:** valid target, authority, valid recurrence fields.
- **Writes:** `AvailabilityRule`.
- **Shared operations:** SH-001, SH-002, SH-123, SH-044.
- **Events/audit:** optional owner event when downstream systems need availability-change facts; admin changes may use SH-029.
- **Idempotency:** semantic rule identity/fingerprint; retry returns same resulting rule/version.
- **Failure modes:** invalid_time_range, invalid_timezone, forbidden, stale_update, duplicate_rule_conflict.

### `deactivateAvailabilityRule`

- Sets `isActive=false` for future slot computation.
- Does not cancel existing holds/Bookings automatically unless an explicit business workflow later requires that effect.

### `createBookingHold`

- **Purpose:** atomically reserve a selected slot before confirmation.
- **Actor/context:** authenticated buyer resolved to `CustomerProfile`.
- **Inputs:** customer/buyer, Professional, UTC interval, duration/context, optional Order, idempotency key.
- **Preconditions:** target validity, authorization, current availability, no BusyWindow/active conflict, current priority decision if applicable.
- **Writes:** `BookingHold` + `BookingSlotLock` atomically.
- **Shared operations:** SH-001, SH-002, SH-004, SH-005, SH-006 when metered semantics require, SH-044, SH-051, SH-056, SH-058, SH-109, SH-123.
- **Events/audit:** optional `booking.hold_created` domain event through SH-046 after event namespace approval; generic audit only when policy requires.
- **Idempotency:** same semantic key returns same active/terminal reservation result; no duplicate hold/lock.
- **Failure modes:** slot_unavailable, outside_availability, busy_window_conflict, customer_profile_required, priority_denied, invalid_interval.

### `releaseBookingHold`

- Releases active hold and lock in one transaction.
- Terminal hold/lock replay is idempotent.
- Does not mutate Order/payment truth.

### `confirmBooking`

- **Purpose:** convert a valid active hold/lock into authoritative confirmed Booking.
- **Actor/context:** authorized system/application workflow or authorized participant according to the final action matrix.
- **Inputs:** holdId, expected lock/hold version, Order reference, locationType, approved scheduling snapshots, idempotency key.
- **Preconditions:** hold/lock active and unexpired; authoritative SH-025 Order booking entitlement; Agreement readiness if required; applicable SH-011 hold decision; relationship facts valid.
- **Writes:** new `Booking(status=confirmed)`, hold/lock converted, `BookingEvent`, outbox event in one transaction.
- **Shared operations:** SH-001/002 when actor-driven, SH-011, SH-025, SH-031, SH-044, SH-046, SH-051/052/053, SH-109.
- **Failure modes:** order_not_entitled, agreement_not_ready, compliance_hold, hold_expired, slot_lock_invalid, stale_transition, duplicate_confirmation_conflict.

### `cancelBooking`

- **Purpose:** transition confirmed Booking to cancelled.
- **Preconditions:** authorized actor/action; current transition valid; cancellation policy/deadline evaluated locally for scheduling consequence; any financial consequence requested from Order owner rather than decided here.
- **Writes:** Booking + BookingEvent + outbox.
- **External effects:** orchestration later handles calendar update, notification, video cancellation request, location revocation request where applicable.

### `rescheduleBooking`

- Uses reservation-before-switch semantics.
- Never overwrites `slotStartAt/slotEndAt` on the original confirmed Booking as the sole history mechanism.
- Creates new Booking and marks old record rescheduled only after new hold/lock and upstream gates succeed.

### `completeBooking`

- Transitions confirmed → completed when the authorized completion policy is satisfied.
- Any Order completion/payout effect is a separate owner interface/event.

### `markBookingNoShow`

- Transitions confirmed → no_show under an approved actor/evidence policy.
- Financial/refund consequences remain external.

**Proposed Ruling PR-BC-03:** initial MVP authority for completion/no-show should be restricted to the Professional, authorized admin/support, or trusted system workflow; buyer self-report alone should not be authoritative until dispute policy is defined.

### `connectCalendar`

- Requires authenticated professional authority and current calendar consent proof.
- Creates/updates `CalendarConnection` in pre-authorized state and invokes provider connection through SH-064/SH-067.
- Raw credentials never enter Booking business contracts.

### `completeCalendarConnection`

- Handles verified provider callback result.
- Activates the connection only after nonce/state/provider result and consent requirements pass.

### `disconnectCalendar`

- Transitions connection to disconnected/revoked as appropriate and invokes provider disconnect when supported; approved external resource deletion/revocation uses SH-070 `deleteProviderResource` through the Booking-owned provider adapter.
- Removes/stops future external busy synchronization under owner policy.

### `applyCalendarProviderEvent`

- Receives a signature-verified, dedupe-claimed, normalized provider event.
- Updates only Booking-owned calendar/BusyWindow/Booking sync state allowed by the mapping.

### `startBookingOrchestration`

- Creates one run keyed by triggering Booking fact/version.
- Plans required steps using Booking policy and public owner contracts.
- Does not directly write downstream owner tables.

### `retryBookingOrchestrationStep`

- Authorized admin/system operation.
- Replays one semantically idempotent step through shared queue/retry primitives.
- Does not reset downstream state by assumption.

### Privacy commands

- `enumerateBookingSubjectData`
- `evaluateBookingRetentionRequirement`
- `executeBookingPrivacyInstruction`

These implement the Privacy-owned protocol and never create a parallel privacy request/job lifecycle.

---

## 11. Queries / Decisions

### `listBookableSlots`

- **Consumers:** marketplace/checkout UI, Order flow, internal Booking UI.
- **Input:** Professional, date range, requested duration, display timezone/context.
- **Result:** calculated UTC intervals plus safe display metadata/freshness.
- **Type:** projection/decision, not reservation truth.
- **Must not infer:** a returned slot is not guaranteed until `createBookingHold` rechecks and acquires a database interval lock.

### `evaluateSlotAvailability`

- **Consumers:** hold creation and internal diagnostics.
- **Input:** exact Professional/UTC interval/context.
- **Result:** allow/deny plus stable Booking reason code and blockers safe to expose.
- **Type:** domain decision based on Booking-owned source truth plus minimal external decision inputs.

### `getBooking`

- Returns authorized Booking source truth plus explicitly approved owner facts/read models.
- Does not expose provider secrets, encrypted exact address, or downstream provider payloads.

### `getBookingOwnerFacts`

Booking’s implementation of SH-003-style owner facts for consumers such as Video, Location Safety, Notification/Messaging composition, or Order.

Required current facts for Video include Booking ID/version or freshness marker, status, scheduled start/end, authorized participant facts, and `overtimeGraceMinutes`. Video must consume the owner-provided overtime value, never a local default, room-state inference, or a direct Booking repository read. This owner-specific query does not promote proposed SH-003.

Other authorized consumers receive the minimum relevant fields from:

- bookingId;
- status/version;
- orderId;
- customerProfileId/buyerUserId as permitted;
- professionalProfileId;
- UTC start/end;
- `overtimeGraceMinutes` supplied by Booking for Video join-window enforcement;
- locationType;
- participant relationship facts;
- cancellation/completion state;
- safe timezone context;
- current external sync summary only when relevant.

Consumers must not infer payment, entitlement, location reveal, or Video room status from these facts.

### `listCustomerBookings`

- Customer-facing authorized read.
- Uses `CustomerProfile` as buyer commercial context and User only as auth/audit identity.

### `listProfessionalBookings`

- Professional-facing authorized read by date/status.

### `getCalendarConnection`

- Returns normalized connection/access/sync state without credentials or raw provider tokens.

### `getBookingDeliverySetupStatus`

- Derived projection over `BookingOrchestrationRun/Step` and Booking sync state.
- Must clearly label downstream request status rather than claiming target lifecycle state.

### Stable reason codes

Public Booking decisions should map to stable categories such as:

```text
unauthenticated
forbidden
customer_profile_required
target_not_found
invalid_interval
invalid_timezone
outside_availability
busy_window_conflict
slot_unavailable
hold_not_active
hold_expired
slot_lock_invalid
order_not_entitled
agreement_not_ready
compliance_hold
invalid_transition
stale_version
calendar_consent_required
calendar_connection_unavailable
provider_temporarily_unavailable
provider_configuration_error
location_reveal_not_permitted
privacy_retained
internal_error
```

Provider-native error strings must not become public reason codes.

---

## 12. Public Module Interface

### Public commands

- `upsertAvailabilityRule`
- `deactivateAvailabilityRule`
- `createBookingHold`
- `releaseBookingHold`
- `confirmBooking`
- `cancelBooking`
- `rescheduleBooking`
- `completeBooking`
- `markBookingNoShow`
- `connectCalendar`
- `completeCalendarConnection`
- `disconnectCalendar`
- `applyCalendarProviderEvent`
- `startBookingOrchestration`
- `retryBookingOrchestrationStep`

### Public queries

- `listBookableSlots`
- `evaluateSlotAvailability`
- `getBooking`
- `getBookingOwnerFacts`
- `listCustomerBookings`
- `listProfessionalBookings`
- `getCalendarConnection`
- `getBookingDeliverySetupStatus`

### Emitted domain events

Exact event names are an architectural contract, not an implementation afterthought.

**Proposed Ruling PR-BC-04 — event namespace:** use versioned `booking.*` and `calendar.*` facts with minimized payloads. Initial event set:

```text
booking.hold_created.v1
booking.hold_released.v1
booking.hold_expired.v1
booking.confirmed.v1
booking.rescheduled.v1
booking.cancelled.v1
booking.completed.v1
booking.no_show.v1
calendar.connection_authorized.v1
calendar.connection_disconnected.v1
calendar.connection_revoked.v1
calendar.busy_windows_changed.v1
calendar.sync_failed.v1
booking.orchestration_completed.v1
booking.orchestration_partially_completed.v1
booking.orchestration_failed.v1
```

Events report facts. They must not be named as commands such as `createVideoRoomNow`.

### Privacy executor

Booking exposes Privacy-defined protocol implementations:

- enumerate subject-held data/provider refs;
- evaluate owner-known retention facts;
- execute erase/anonymize/detach/disconnect/provider-delete/retain instruction;
- contribute export-safe data where required.

### Provider-facing interfaces owned

`CalendarProviderPort` / SH-067 must cover only provider-neutral calendar operations needed by Booking, such as:

- start authorization / create connection request;
- exchange/complete authorization where provider requires;
- fetch availability/free-busy intervals;
- create/update/cancel Booking calendar event;
- disconnect/revoke connection;
- normalize webhook/provider event;
- fetch provider state for reconciliation.

Cronofy-specific types terminate at `cronofy-adapter.ts`.

---

## 13. Inbound Dependencies

| Owning Module / capability | Public operation consumed | Why required | Minimum information | May block? | Booking must not copy |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | establish trusted actor | actor ID/type/security context | yes | sessions/current-user helpers |
| Role / Authority | SH-002 `authorizeResourceAction` | permission for Booking/calendar actions | actor, action, Booking/Professional relationship facts | yes | RBAC policy engine |
| Customer / Buyer Profile | SH-004 `resolveCustomerActor` | buyer commercial identity | customerProfileId + active context | yes for buyer Booking flow | customer lifecycle |
| Track Subscription & Entitlement | SH-005 / SH-006 | priority scheduling and metered use if defined | key/value/grant/evaluatedAt/usage receipt | yes when feature requires | plan/grant/counter truth |
| Consent & Disclosure | SH-007/008 | calendar access disclosure/proof | consent type/version/proof ID | yes for calendar connection | ConsentLog table/version catalog |
| Admin Review / Compliance Hold | SH-011 | reusable stop sign | applicable hold IDs/reasons/scope | yes | local `isBlocked` flags |
| Transaction / Order | SH-025 `authorizeOrderEntitlement` | confirm Booking is permitted by transaction truth | order status, participants, qualifying item, refund/dispute effects, evidence | yes | payment/Order state machine |
| Agreement owner | owner public readiness query | required Agreement gate | order/agreement ID, readiness decision/evidence | yes where required | Agreement generation/signatures |
| Professional/Marketplace owner | SH-123 target validation / owner facts | validate Professional/service scheduling context | IDs, active/eligible scheduling facts, duration if applicable | yes | Offering/Professional repository |
| Location Safety | SH-027 | exact location reveal | reveal decision/proof/precision | yes for reveal, not for basic confirmation | location reveal lifecycle |
| Healthcare | SH-020 when triggered | healthcare-sensitive scheduling/provider handling | allow/redact/block decision + policy evidence | conditionally | healthcare flags/policy |
| Video Session | public booking-video command | create/cancel room after Booking fact | booking owner facts, participants, interval | downstream setup only | VideoRoom/provider state |
| Messaging | SH-113 `ensureContextThread` | create/retrieve Booking/Order context thread | context type/id + participants | downstream setup | Thread lifecycle |
| Notification | SH-041 | send Booking business notifications | recipients/template/safe variables/idempotency | noncritical unless policy says otherwise | provider/channel delivery |
| Audit / Event Ledger | SH-029/030 | generic/sensitive evidence | safe actor/action/target/outcome | should not decide Booking | AuditEvent/AccessAuditLog schema |
| Observability / Ops | SH-032/034/037/038/039 | correlation/failure/queue/health | safe operation/provider/job dimensions | no business authority | incidents/queue truth |
| Privacy / Data Erasure | SH-095–097 protocol | legal privacy orchestration instructions | target/disposition/retention reference | destructive action only through protocol | privacy workflow/retention exemptions |

---

## 14. Outbound Consumers and Effects

### Transaction / Order

May consume:

- valid BookingHold/Booking reference;
- Booking confirmation/cancellation/completion facts;
- owner facts needed to coordinate service delivery.

Booking must not directly mutate Order state. Any Order response is a public command/event handled by the Order owner.

### Video Session

Consumes `Booking` facts for confirmed video appointments. Video owns `BookingVideoRoom` and join credentials. Booking orchestration may request room setup but does not infer room success from provider IDs in Booking.

### Messaging

Booking may request a canonical context thread through SH-113. Messaging owns uniqueness, participants, and message lifecycle.

### Notification

Booking supplies business trigger and safe variables for confirmation, reschedule, cancellation, calendar connection problems, or user-relevant setup outcomes. Notification owns persistence/routing/provider delivery.

### Location Safety

Consumes Booking/Order context when deciding exact reveal. Booking may request evaluation but never self-authorizes.

### Professional Eligibility / Marketplace

The historical registry lists Professional Eligibility as a Booking consumer, but the exact need is not well defined. No direct dependency should be introduced unless a concrete public query such as `hasBookableAvailability` is approved.

### Privacy / Data Erasure

Consumes Booking data inventory and execution results.

### Audit / Observability

Consume safe domain references and execution facts only.

### Search

No Booking-owned public search projection is currently confirmed. Do not introduce Booking→Typesense writes. If a later discovery feature needs availability freshness, define an explicit source projection/public readiness contract first.

---

## 15. Canonical Shared Operations Used

Only operations materially used by Booking & Calendar are listed here. Global definitions remain authoritative in `context/shared/shared-operations.md`.

### SH-001 — `resolveAuthenticatedActor`
- **Owner:** Identity & Access
- **Classification:** canonical shared capability
- **Why used:** establish buyer, professional, admin/support, or trusted system actor.
- **Invocation:** every actor-driven command/query before Booking policy.
- **Local policy:** which Booking action/resource facts are being authorized.
- **Expected result:** typed actor context.
- **Do not build:** `bookingAuth.ts`, `getCurrentBookingUser`, custom session parser.

### SH-002 — `authorizeResourceAction`
- **Owner:** Role / Authority
- **Classification:** cross-cutting capability
- **Invocation:** availability management, Booking read/mutate, calendar connection management, admin retry.
- **Local policy:** Booking supplies owner/participant/Professional relationship facts and action names.
- **Do not build:** `bookingPermissionService`, `calendarRoleGuard`, local `isAdmin` checks.

### SH-003 — `queryOwnerFacts`
- **Owner:** each source Module; **status:** Proposed ruling in canonical registry.
- **Use:** pattern for minimal Order/Professional/Booking facts across boundaries.
- **Local policy:** Booking defines its own owner-facts DTO.
- **Do not build:** universal polymorphic cross-domain repository.

### SH-004 — `resolveCustomerActor`
- **Owner:** Customer / Buyer Profile
- **Use:** buyer-side hold/Booking reads and creation.
- **Local policy:** Booking uses returned CustomerProfile as commercial buyer context and retains User only for auth/audit linkage.
- **Do not build:** local buyer-profile resolver/table.

### SH-005 — `resolveEntitlement`
- **Owner:** Track Subscription & Entitlement
- **Use:** resolve priority scheduling.
- **Invocation:** slot ranking/hold creation where priority applies.
- **Local policy:** effect of the returned priority value on Booking ranking/reservation; it may never bypass conflict safety.
- **Do not build:** `isPriorityCustomer`, `premiumBookingService`, local plan lookup.

### SH-006 — `consumeMeteredEntitlement`
- **Owner:** Track Subscription & Entitlement
- **Use:** only if priority scheduling is metered/consumable under approved policy.
- **Local policy:** exact business moment at which a priority use counts.
- **Do not build:** local usage counter/event.

### SH-007 / SH-008 — `recordConsentProof` / `queryConsentProof`
- **Owner:** Consent & Disclosure
- **Use:** calendar sync/free-busy/writeback consent.
- **Local policy:** which consent version/access mode is required for the requested connection action.
- **Do not build:** `CalendarConsent`, `acceptedCalendarTerms` boolean.

### SH-011 — `evaluateComplianceHold`
- **Owner:** Admin Review / Compliance Hold
- **Use:** gate configured Booking actions without local blocked flags.
- **Local policy:** which hold scopes block hold creation, confirmation, reschedule, calendar access, or admin actions.
- **Do not build:** `bookingBlocked`, `calendarSuspended` generic flags.

### SH-020 — `evaluateHealthcareReadiness`
- **Owner:** Healthcare / Regulated Services
- **Use:** conditional healthcare-sensitive Booking/calendar handling.
- **Local policy:** how returned allow/redact/block affects Booking operation/provider use.
- **Do not build:** `isHealthcareBooking` as compliance truth.

### SH-025 — `authorizeOrderEntitlement`
- **Owner:** Transaction / Order
- **Use:** authoritative gate before Booking confirmation and any later Order-sensitive scheduling action.
- **Local policy:** Booking still validates slot/hold/transition state.
- **Do not build:** Stripe payment check, local `orderPaid` inference.

### SH-027 — `resolveLocationReveal`
- **Owner:** Location Safety
- **Use:** exact-location reveal for in-person Booking.
- **Local policy:** Booking supplies confirmed scheduling context.
- **Do not build:** `canShowAddress`, decrypt/reveal logic inside Booking.

### SH-029 / SH-030 — `appendAuditEvent` / `recordSensitiveAccess`
- **Owner:** Audit / Event Ledger
- **Use:** material admin actions and sensitive calendar/location access as policy requires.
- **Local policy:** action/sensitivity/target/outcome metadata.
- **Do not build:** booking audit tables/writers.

### SH-031 — `appendDomainLifecycleEvent`
- **Owner:** shared persistence mechanism; Booking owns truth.
- **Use:** append `BookingEvent` transactionally with Booking transitions.
- **Local policy:** Booking event names, from/to statuses, reason/metadata.
- **Do not build:** generic lifecycle table replacing BookingEvent.

### SH-032 / SH-033 / SH-034 / SH-036 / SH-037 / SH-038 / SH-039
- **Owners:** Observability/platform.
- **Use:** correlation, structured logs, redaction, metrics, provider failures, queue telemetry, health checks.
- **Local policy:** Booking metric/error dimensions and retry classification.
- **Do not build:** Booking-specific logger/Sentry/queue telemetry/incident store.

### SH-041 — `requestNotification`
- **Owner:** Notification
- **Use:** confirmation/reschedule/cancellation/calendar degradation notifications.
- **Local policy:** business trigger, recipients, safe template variables.
- **Do not build:** Booking email/SMS/push provider clients.

### SH-044 — `executeIdempotentCommand`
- **Owner:** platform application infrastructure
- **Use:** hold creation/release, Booking transitions, calendar connection, orchestration start/retry.
- **Local policy:** semantic idempotency key and valid replay result.
- **Do not build:** Booking-only idempotency table/framework.

### SH-045 — `deduplicateDomainEvent`
- **Owner:** platform event infrastructure / consumer inbox
- **Use:** later consumption of authoritative refund/hold/entitlement/moderation/privacy-related events where event-driven handling is approved.
- **Local policy:** handler/version and Booking effect.
- **Do not build:** ad hoc event-consumption ledger.

### SH-046 — `publishDomainEvent`
- **Owner:** platform outbox infrastructure
- **Use:** publish Booking facts after source transaction commit.
- **Local policy:** event names/payloads/emission conditions.
- **Do not build:** Booking-only event bus/outbox.

### SH-047 / SH-048 — `enqueueReliableJob` / `executeRetryWithBackoff`
- **Owner:** shared queue/platform infrastructure
- **Use:** hold expiry, calendar sync/writeback, provider processing, orchestration, reconciliation, privacy provider actions.
- **Local policy:** job payload, completion meaning, retryable vs terminal failure.
- **Do not build:** Booking queue/retry/dead-letter framework.

### SH-049 / SH-050 — `orchestrateWorkflowSteps` / `reconcileWorkflowStatus`
- **Owner:** shared mechanism; Booking owns workflow truth
- **Use:** `BookingOrchestrationRun/Step` execution and aggregation.
- **Local policy:** step graph, criticality, partial-completion semantics.
- **Do not build:** generic `DeliveryWorkflow` or global saga business table.

### SH-051 / SH-052 / SH-053
- **Owners:** shared persistence/state-machine mechanisms
- **Use:** aggregate lock, optimistic concurrency, lifecycle transition plumbing.
- **Local policy:** lock keys, Booking transition graph, stale-write behavior.
- **Do not build:** in-memory mutex or generic policy table owning Booking states.

### SH-055 — `runDeadlineExpiration`
- **Owner:** shared scheduler/queue
- **Use:** hold/slot-lock expiration.
- **Local policy:** which records are expired and owner command invoked.
- **Do not build:** Booking-specific scheduler framework.

### SH-056 / SH-058 — `executeAtomicReservation` / `acquireIntervalLock`
- **Owner:** shared DB primitive; Booking owns interval policy
- **Use:** scarce interval reservation and overlap rejection.
- **Local policy:** professional key, active blocking states, time range, release/convert semantics.
- **Do not build:** in-memory lock, Redis-only source of truth, JobInterview reuse of BookingSlotLock.

### SH-059 / SH-060 / SH-061 / SH-062
- **Use:** provider webhook signature verification, owner-specific dedupe, status translation, reconciliation.
- **Local policy:** Cronofy accepted events, mapping tables, safe repair rules.
- **Do not build:** generic global status mapper or reuse another Module’s processed-provider ledger.

### SH-064 — `authorizeExternalProviderConnection`
- **Owner:** provider-owning Module pattern; Booking is calendar owner
- **Use:** calendar OAuth/hosted authorization start/callback controls.
- **Local policy:** calendar scopes, consent requirement, connection lifecycle.
- **Do not build:** unscoped redirect/token flow.

### SH-067 — `invokeCalendarProvider`
- **Owner:** Booking & Calendar
- **Classification:** Module provider interface
- **Use:** all Cronofy free/busy/writeback/disconnect/reconciliation operations.
- **Local policy:** Booking/provider mapping and safe event descriptions.
- **Do not build:** direct Cronofy calls scattered across commands/workers/UI.

### SH-070 — `deleteProviderResource`
- **Owner:** provider-owning Module (Booking & Calendar for calendar resources).
- **Status:** Confirmed.
- **Use:** approved calendar-provider disconnect/deletion/revocation, including Privacy instructions.
- **Local policy:** calendar target mapping and resulting Booking-owned state; return typed deleted, absent, retained, retryable-failure, or terminal-failure evidence.
- **Do not build:** provider deletion in Privacy or a separate Booking deletion framework.

### SH-078 — `minimizeAndRedactProviderInput`
- **Owner:** source-data owner supplies policy; shared serializer enforces.
- **Status:** Confirmed.
- **Use:** before calendar authorization, free/busy, writeback, deletion, or reconciliation provider requests.
- **Local policy:** purpose-bound calendar field allowlists and scope/data minimization; secrets and unrelated event details do not enter telemetry.
- **Do not build:** a local generic provider serializer/redactor.

### SH-072 — `hashCanonicalPayload`
- **Owner:** shared cryptography capability
- **Use:** provider payload/availability hashes and integrity/idempotency evidence where needed.
- **Local policy:** canonical input and semantic meaning.
- **Do not build:** `bookingHashUtil`.

### SH-075 — `encryptSensitiveValue`
- **Owner:** shared security capability
- **Use:** only if the approved Location Safety snapshot contract permits `Booking.exactAddressEncrypted`.
- **Local policy:** necessity/retention/access; Location Safety still owns reveal/decryption decision.
- **Do not build:** custom address crypto.

### SH-095 / SH-096 / SH-097
- **Owner:** Privacy protocol / data owner execution
- **Use:** privacy instruction, subject inventory, retention facts.
- **Local policy:** Booking-owned fields/provider resources and supported dispositions.
- **Do not build:** local PrivacyRequest/DataErasureJob/retention-exemption lifecycle.

### SH-109 — `snapshotExternalDecision`
- **Owner:** consuming domain owner
- **Use:** priority scheduling and other historically material external decisions.
- **Local policy:** fields preserved and why the historical decision matters.
- **Do not build:** current entitlement cache used as policy truth.

### SH-113 — `ensureContextThread`
- **Owner:** Messaging
- **Use:** Booking/Order context thread during orchestration.
- **Local policy:** source context/participants supplied from owner facts.
- **Do not build:** Booking chat/thread store.

### SH-123 — `validateOwnedTargetReference`
- **Owner:** target owner
- **Use:** validate Professional/Order/other references without direct foreign repositories.
- **Local policy:** relationship requested by Booking.
- **Do not build:** cross-domain Prisma repository.

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `expandAvailabilityRules` | convert local recurrence into candidate UTC intervals | rules, range, duration | candidate intervals | none | recurrence semantics are Booking policy |
| `subtractBusyIntervals` | remove BusyWindow/Booking/lock conflicts | intervals + blockers | free intervals | none | scheduling-specific set logic |
| `evaluateSlotAvailability` | authoritative exact-slot decision | professional, interval, state snapshot | allow/deny reason | none | Booking owns conflict policy |
| `buildPrioritySchedulingEffect` | map entitlement decision to local scheduling behavior | SH-005 decision + request context | local priority effect/snapshot | hold/lock snapshot | Track owns entitlement; Booking owns its local effect |
| `convertReservationToBooking` | atomic hold/lock conversion | hold, lock, upstream gate evidence | confirmed Booking | hold, lock, Booking, BookingEvent | core Booking transaction |
| `planRescheduleReservation` | reserve new slot before old Booking changes | Booking + requested interval | new hold/lock plan | hold/lock | preserves scheduling invariant |
| `translateCalendarEventToBusyWindowChange` | map normalized provider event to local unavailable-time change | normalized event | upsert/delete decision | BusyWindow | provider mapping remains Booking-specific |
| `planBookingOrchestration` | determine required downstream steps | Booking fact/version | step definitions | orchestration records | sequence is Booking workflow truth |
| `classifyOrchestrationFailure` | determine retry/skip/fail/partial behavior | step + normalized failure | classification | orchestration state | criticality is Booking policy |
| `buildBookingOwnerFacts` | minimize facts for consumers | Booking aggregate | typed DTO | none | Booking owns what its consumers may safely rely on |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Lifecycle plumbing:** SH-053 may validate/apply transitions, but Booking owns the transition graph and `BookingStatus` meaning.
2. **Domain ledger:** SH-031 provides append mechanics; `BookingEvent` remains distinct from OrderEvent, JobInterviewEvent, AuditEvent, and provider ledgers.
3. **Provider dedupe:** SH-060 provides claim mechanics; `ProcessedCalendarEvent` remains separate from ProcessedStripeEvent and ProcessedVideoProviderEvent.
4. **Atomic reservation:** SH-056/058 provide DB mechanics; `BookingSlotLock` remains Booking truth and cannot become a generic interval table shared with JobInterview.
5. **Workflow runner:** SH-049/050 provide execution/aggregation mechanics; `BookingOrchestrationRun/Step` retain Booking-specific step types and status semantics.
6. **Snapshots:** SH-109 provides a pattern; priority snapshot meaning remains Booking-specific and does not transfer entitlement ownership.
7. **Provider status translation:** SH-061 is a contract pattern; calendar mappings stay in the Booking calendar adapter.
8. **Privacy execution:** SH-095–097 define protocol; Booking owns only its data/provider effects, not PrivacyRequest/DataErasureJob.
9. **Audit:** generic audit may record a Booking action; it never replaces BookingEvent.
10. **Observability:** IntegrationFailure may record Cronofy failure; it never replaces CalendarConnection/Booking sync fields.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

All user-initiated commands and protected queries call SH-001. Provider callbacks use a trusted provider/system context after signature verification rather than pretending to be a User.

### Role / Authority integration

Booking defines action vocabulary and resource facts; Role / Authority decides permission.

Suggested action vocabulary:

```text
booking.availability.manage
booking.slot.view
booking.hold.create
booking.hold.release
booking.view
booking.cancel
booking.reschedule
booking.complete
booking.no_show.mark
booking.calendar.connect
booking.calendar.disconnect
booking.orchestration.retry
booking.admin.view
```

### Resource ownership/context

- Customer actions are anchored to `CustomerProfile`/buyer relationship.
- Professional actions are anchored to `ProfessionalProfile` relationship.
- Order participant facts come from Order owner.
- Booking consumer facts are exposed through a minimized owner-facts query.
- Admin/support authority never implies unrestricted exact-location or provider-secret access.

### Step-up

No exact Booking-specific step-up matrix is currently approved. SH-014 may be required for sensitive admin retry, credential management, or exact-location operations, but implementation must follow root security policy rather than inventing local MFA flags.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Truth owner | Query consumed | Booking action gated | Local composition |
| --- | --- | --- | --- | --- |
| Buyer identity | Customer / Buyer Profile | SH-004 | hold creation/customer reads | require valid CustomerProfile; User is auth/audit identity |
| Authority | Role / Authority | SH-002 | all protected actions | Booking supplies relationship facts/action |
| Priority scheduling | Track Subscription & Entitlement | SH-005, optionally SH-006 | slot ranking/hold creation | apply only approved local effect; never bypass overlap |
| Calendar consent | Consent & Disclosure | SH-008 (SH-007 for acceptance flow) | calendar connection/writeback scope | require matching type/version/access scope |
| Compliance hold | Admin Review / Compliance Hold | SH-011 | configured hold/confirm/reschedule/calendar/admin actions | map hold scope to deny without local blocked flag |
| Order entitlement | Transaction / Order | SH-025 | Booking confirmation and current Order-sensitive actions | Order decision plus Booking-local slot/lifecycle checks |
| Agreement readiness | Transaction / Order Agreement | owner readiness query | Booking confirmation when required | deny confirmation until ready; do not generate/sign locally |
| Exact location | Location Safety | SH-027 | reveal exact address | Booking supplies confirmed context; Location creates reveal proof |
| Healthcare | Healthcare | SH-020 when triggered | sensitive Booking/provider access | enforce allow/redact/block, no local healthcare truth |

---

## 20. Provider Integrations

### Provider-neutral port

All external calendar calls use `CalendarProviderPort` / SH-067. Their purpose-bound payloads use SH-078 `minimizeAndRedactProviderInput`; approved calendar-resource deletion/disconnection uses SH-070 `deleteProviderResource` within that provider boundary.

### Current adapter

Cronofy is the current canonical MVP calendar integration target. `Nylas`, `direct`, and `other` exist in enum/future evidence but must not be implemented as parallel MVP adapters without an architecture change.

### Credentials

- provider secrets remain server-only;
- `providerCredentialId` is opaque;
- OAuth state/nonce and redirect allowlist are mandatory;
- least-privilege scopes are requested;
- client responses never include refresh/access tokens.

### Webhook verification

1. receive raw body;
2. SH-059 verifies provider signature/timestamp using Cronofy adapter algorithm;
3. create request/correlation context;
4. SH-060 atomically claims provider+event ID into `ProcessedCalendarEvent`;
5. SH-061 translates provider event/status to normalized Booking vocabulary;
6. Booking owner applies allowed BusyWindow/connection/sync transition;
7. mark provider event processed/failed;
8. publish any resulting domain fact after source transaction.

### Provider-event dedupe truth

`ProcessedCalendarEvent` is canonical. No Redis-only dedupe, generic webhook table, or reuse of another provider ledger is permitted as source truth.

### Status/error translation

Provider statuses/errors are normalized inside the Cronofy adapter. Unknown statuses fail safe and record IntegrationFailure. Public consumers receive Booking reason codes, not Cronofy strings.

### Reconciliation

Booking owns a scheduled/manual reconciliation command using SH-062. It may:

- compare connection authorization state;
- detect missing/stale BusyWindows;
- detect missing/duplicate writeback resource references;
- repair only discrepancies explicitly marked safe;
- produce a dry-run discrepancy report;
- route unsafe discrepancies to Ops/manual review.

Provider state is evidence, not authority to overwrite Booking blindly.

### Privacy deletion/disconnection

Privacy instructions may require disconnecting a calendar, deleting provider references, or deleting normalized BusyWindows. Execution is idempotent and reports deleted/absent/retained/retryable/terminal outcomes back to Privacy.

---

## 21. Events and Outbox

### BookingEvent vs domain events

`BookingEvent` is the Booking aggregate’s append-only history. Published domain events are cross-Module facts used for asynchronous consumers. Both may originate from the same transaction but serve different purposes.

### Transactional outbox

When a Booking/hold/calendar source change requires downstream reaction, source truth + required `BookingEvent` + outbox message are committed atomically. SH-046 publishes after commit.

### Event envelope expectations

Every published event should include:

- event ID;
- schema/event version;
- aggregate type and ID;
- aggregate/source version or authoritative `updatedAt` token;
- occurredAt;
- correlation ID;
- causation ID when applicable;
- actor category/ID only when safe/needed;
- minimized domain fields required by consumers;
- no exact address, provider tokens, raw calendar event data, or unnecessary personal data.

### Consumer idempotency

Consumers must use SH-045 or their owner-specific equivalent. Booking must not assume at-most-once delivery.

### Events are facts, not commands

Good: `booking.confirmed.v1`.  
Bad: `create_video_room_now`.

Commands to Video/Messaging/Notification/Location are explicit public interface calls executed by Booking orchestration, not disguised events.

---

## 22. Background Jobs / Scheduled Work

| Worker | Purpose | Input/owner key | Idempotency | Retryable failures | Permanent failures | Dead-letter/manual behavior | Business truth affected | Telemetry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hold expiration | expire past-due active holds | hold ID / due cursor | owner command key | transient DB/queue | already terminal is success/no-op | dead-letter visible; next sweep may retry | BookingHold, SlotLock | counts/lag/failures |
| Slot-lock expiration | release expired active locks | lock ID | owner command key | transient DB | converted/terminal no-op | ops visibility | BookingSlotLock | lock age/conflicts |
| Busy-window sync | refresh external free/busy | connection + cursor/window | connection/window key | provider outage/rate limit | revoked/invalid connection | dead-letter + reconcile | BusyWindow, sync timestamps | provider latency/sync lag |
| Provider-event processing | apply normalized calendar event | provider+event ID | ProcessedCalendarEvent unique claim | transient DB/downstream | invalid signature/out-of-scope/unsupported | record safe failure; no duplicate effect | connection/BusyWindow/sync state | duplicate/failure rates |
| Calendar writeback | create/update/cancel external event | booking/version/action | semantic provider request key | provider outage/rate limit | invalid/revoked connection if not recoverable | orchestration step failed + IntegrationFailure | externalSyncStatus/ref | latency/failures |
| Booking orchestration | execute downstream steps | run/step IDs | run key + per-step semantic key | transient owner/provider failures | business denial/invalid target | bounded retry/dead-letter/manual retry | orchestration run/step only | step timings/failure |
| Calendar reconciliation | compare local/provider state | connection/provider cursor | reconciliation run ID + repair keys | provider outage | unsupported discrepancy | dry-run/manual review | only safe owner repairs | discrepancy metrics |
| Privacy provider execution | disconnect/delete provider refs | Privacy target ID | Privacy target/action key | provider outage | retention/unsupported delete | report to Privacy; dead-letter ops | owner fields/provider refs | safe result counts |

Generic queue mechanics must use SH-047/048/038.

---

## 23. Concurrency and Idempotency

### Races that must be prevented

1. Two buyers reserve the same Professional/time interval.
2. Hold expires while confirmation tries to convert it.
3. Two confirmation requests convert one hold/lock.
4. Cancel/reschedule/complete race on the same Booking.
5. Two reschedules reserve/change the same Booking concurrently.
6. Calendar webhook and scheduled sync update the same BusyWindow/provider version.
7. Duplicate provider callback repeats side effects.
8. Orchestration retry duplicates calendar event/thread/notification/video room.
9. Privacy deletion/disconnect races with provider sync/reconciliation.

### Interval lock key

`professionalProfileId + [startsAt, endsAt)` under Booking’s active conflict policy.

### Database strategy

- use Postgres range/exclusion constraint or equivalent transactionally enforced overlap rule;
- use row/advisory locks or serializable transactions through SH-051 where required;
- use unique `BookingSlotLock.idempotencyKey` and provider-event unique keys;
- use expected version / compare-and-set through SH-052 for stale Booking transitions;
- never depend on application-process mutexes.

### Confirmation transaction boundary

At minimum, one transaction must validate/lock the reservation state and then:

1. ensure hold active and `expiresAt > now`;
2. ensure slot lock active and compatible;
3. ensure no competing converted state;
4. create confirmed Booking;
5. transition hold/lock → converted;
6. append BookingEvent;
7. persist outbox event.

External Order/Agreement decisions are obtained before the write transaction, with source version/evidence carried into the command. If their decision can become invalid during the transaction, the public contract must provide a version/token or the cross-Module orchestration must define a safe revalidation strategy; Booking must not solve this by directly locking foreign tables.

### Command replay

A repeated idempotency key with the same semantic fingerprint returns the original result. Same key + conflicting payload returns an idempotency conflict rather than silently applying new work.

---

## 24. Media / Storage

Booking & Calendar does not own file storage or `MediaAsset` mechanics.

Possible Booking-related files—Order files, Agreement PDFs, attachments, evidence—remain with their contextual owner plus Media / File Access.

Booking must not:

- upload files directly to R2;
- issue signed Media URLs;
- validate MIME/malware;
- treat Agreement PDF as Booking truth;
- create a Booking-specific file grant.

If future Booking UI attaches media, the contextual attachment meaning must be explicitly assigned and Media operations consumed through canonical interfaces.

---

## 25. Search / Projection

No public Booking search projection is currently confirmed.

`listBookableSlots` is a Booking-owned computed read projection, not a Search/Typesense document.

Rules:

- do not write `SearchUpsertEvent` directly;
- do not call Typesense from Booking;
- do not publish exact availability/calendar details into public search without a separate approved privacy/readiness contract;
- if a future Offering search ranking uses bookability, Search must consume an owner-issued minimized projection/readiness fact rather than reconstruct Booking/Calendar state from tables.

---

## 26. Notification

Booking owns **when** a Booking-related notification is warranted and the safe business meaning. Notification owns persistence, templates/channel rendering, routing, provider delivery, retries, and `NotificationDelivery` state.

Candidate triggers:

- Booking confirmed;
- Booking rescheduled;
- Booking cancelled;
- calendar connection revoked/expired when user action is required;
- user-relevant orchestration failure only when product policy requires;
- reminders only when a separate scheduling/reminder policy is approved.

Safe payload intent may include:

- booking ID;
- generalized date/time/timezone;
- participant-safe display names/links where owner contracts allow;
- action route.

Never include:

- exact private address before Location Safety authorization;
- provider access tokens;
- raw Cronofy IDs unless operational/admin-only;
- signed URLs/video join tokens;
- external calendar event contents.

---

## 27. Audit and Sensitive Access

### Domain truth

`BookingEvent` records Booking lifecycle actions/transitions.

### Generic audit

Use SH-029 for material actions that require platform audit beyond BookingEvent, such as:

- admin/support override/retry;
- security-sensitive calendar connection management;
- privacy destructive retry if policy requires;
- architecture-defined exceptional transition.

### Sensitive access

Use SH-030 when policy classifies calendar/provider/location access as sensitive. Location Safety may itself create/trigger location-specific evidence. Do not duplicate that proof inside BookingEvent metadata.

### Separation rule

One action may legitimately create:

```text
BookingEvent        — Booking lifecycle fact
AuditEvent          — generic important-action proof
AccessAuditLog      — sensitive access proof
IntegrationFailure — provider/worker operational failure
```

These records answer different questions and must not collapse into one generic log.

---

## 28. Privacy and Retention

### Subject-data inventory

Booking-owned subject data includes, as applicable:

- `AvailabilityRule` and Professional scheduling preferences;
- `CalendarConnection` provider/account/calendar references and scope state;
- `BusyWindow` normalized intervals/provider refs;
- BookingHold/SlotLock buyer/customer/professional relationships and timezones;
- Booking participant/time/location snapshot data;
- BookingEvent actor references and safe metadata;
- provider event links/request IDs/payload hashes;
- orchestration actor/target/provider references.

### Privacy executor

Booking implements SH-096 inventory and SH-095 execution for owner records/provider effects.

Supported dispositions may include:

- erase/delete where allowed;
- anonymize participant metadata while preserving retained transaction/scheduling proof;
- disconnect calendar provider;
- delete provider references;
- delete external-calendar BusyWindows;
- revoke/clear sensitive location snapshot data where allowed;
- retain specific records only when Privacy records an approved exemption from the proper source basis;
- export safe Booking/calendar data for subject access where approved.

### Retention

Booking does not independently decide tax/contract/dispute/legal retention. It supplies facts to SH-097 and follows Privacy’s exemption record.

Potential retained records may include Booking/BookingEvent links associated with legally retained Orders/Agreements/disputes; the exact retention period/basis must come from the appropriate owner/legal policy.

### Product deletion vs privacy erasure

Normal cancellation/archival is not privacy erasure. Provider disconnect is not proof that all subject data was erased. Privacy completion remains Privacy-owned.

---

## 29. Observability

### Structured logs

Every request/job/provider operation propagates SH-032 correlation context. Logs use SH-033/034.

Safe dimensions:

- operation name;
- Booking/calendar connection status;
- provider name;
- result/reason code;
- retryability;
- request/correlation IDs;
- coarse job/step type;
- duration.

Avoid high-cardinality or sensitive values such as exact address, raw user email, provider tokens, external event text, complete payloads, or private attendee data.

### Metrics

Recommended operational metrics:

- slot evaluation count/denial reason;
- interval conflict rate;
- hold created/converted/released/expired counts;
- hold age/expiration lag;
- Booking confirmation success/denial reason;
- reschedule conflict rate;
- calendar connection success/revoke/failure;
- free/busy sync latency and lag;
- provider webhook verified/invalid/duplicate/failure;
- calendar writeback success/failure/latency;
- orchestration completion/partial/failure by step type;
- reconciliation discrepancy count/repair/manual-review count.

### IntegrationFailure

Use SH-037 for Cronofy/API/worker failures. It never becomes `Booking.status` or `CalendarConnection.status` by itself.

### Health checks

Provider/worker readiness checks may report healthy/degraded/unavailable/delayed through SH-039 without leaking credentials.

---

## 30. Security Boundaries

1. Validate all public command/query inputs at the delivery boundary and again at domain invariants where appropriate.
2. Enforce SH-001/002 server-side; never trust frontend actor/role flags.
3. Provider credentials are server-only opaque references.
4. OAuth/provider authorization uses state/nonce, redirect allowlist, least-privilege scopes, and callback validation.
5. Webhooks require raw-body signature verification before parsing/side effects.
6. Provider payloads are minimized and never stored wholesale merely for debugging.
7. Free/busy sync must not persist unnecessary event metadata.
8. Exact address encryption, if approved, uses SH-075; reveal/decryption remains Location Safety-controlled.
9. Idempotency keys are not authorization tokens.
10. Rate-limit public slot/hold/calendar connection endpoints according to root security standards.
11. Orchestration metadata cannot contain provider secrets, exact location, signed credentials, or private message bodies.
12. Admin/support operational views expose provider references only as needed and respect step-up policy when finalized.

---

## 31. Error / Decision Result Pattern

Public interfaces should return a normalized result rather than leaking Prisma/provider exceptions.

Conceptual shape:

```ts
type BookingDecision<T> =
  | {
      ok: true
      value: T
      evaluatedAt: string
      sourceVersion?: string
      warnings?: BookingWarning[]
    }
  | {
      ok: false
      reason: BookingReasonCode
      retryable: boolean
      remediation?: string
      conflictVersion?: string
      evidenceRefs?: SafeEvidenceRef[]
    }
```

Rules:

- authorization denial and not-found must remain distinguishable where security policy permits;
- provider errors map to safe retryable/nonretryable categories;
- `slot_unavailable` is a first-class conflict, not a generic 500;
- stale versions return conflict, not silent last-write-wins;
- Agreement/Order/hold denials retain owner-safe reason/evidence without copying owner policy;
- internal provider payload/error text stays in sanitized telemetry only.

---

## 32. Testing Architecture

### Domain unit tests

- AvailabilityRule format/effective-period validation.
- recurrence expansion across DST/timezone boundaries.
- BusyWindow subtraction.
- interval conflict policy.
- BookingHold/SlotLock transition matrices.
- Booking transition matrix.
- reschedule reservation-before-switch policy.
- orchestration critical/noncritical aggregation.
- provider status/event mapping tables.

### State-transition tests

Every lifecycle validates legal and illegal transitions, terminal-state behavior, actor/reason requirements, and event append.

### Public contract tests

- CustomerProfile resolver contract.
- Order entitlement/Agreement readiness contracts.
- Location Safety contract.
- Messaging SH-113.
- Notification SH-041.
- Video booking-room command contract.
- Privacy executor contract.

### Database/integration tests

- migration applies cleanly;
- overlap/exclusion constraint under concurrent transactions;
- hold/lock atomic creation/release/conversion;
- BookingEvent atomicity;
- provider-event unique claim;
- orchestration idempotency key;
- reschedule transaction behavior.

### Authorization tests

- professional availability owner vs unrelated actor;
- customer hold/read vs unrelated customer;
- buyer/professional Booking actions;
- admin/support limited actions;
- unauthorized provider/admin routes;
- RLS/server policy alignment where root architecture requires RLS.

### Compliance tests

- calendar consent mandatory;
- ComplianceHold mapping;
- priority entitlement does not bypass overlap;
- exact location unavailable without Location Safety;
- healthcare conditional gate when marked sensitive;
- free/busy payload minimization.

### Idempotency/concurrency tests

- parallel same-slot holds;
- duplicate hold command;
- confirm vs expiration;
- duplicate confirmation;
- concurrent cancel/reschedule/complete;
- duplicate webhook;
- duplicate orchestration run/step;
- reconciliation vs provider callback.

### Provider adapter tests

- OAuth state/nonce/redirect;
- minimal scopes;
- signature verification;
- mapping known/unknown provider events;
- provider timeout/rate limit/revoked authorization;
- free/busy minimization;
- writeback idempotency;
- reconciliation dry-run/repair.

### Privacy tests

- subject inventory completeness;
- calendar disconnect/provider reference deletion;
- erase vs anonymize vs retain;
- retained record only with Privacy exemption reference;
- duplicate destructive instruction;
- telemetry redaction.

### E2E participation tests

- professional availability → buyer slot list → hold;
- second concurrent buyer denied;
- eligible Order → Booking confirmation;
- cancel/reschedule/complete flows;
- calendar connection → BusyWindow → slot disappears;
- provider duplicate webhook causes one effect;
- confirmed Booking → orchestration requests through public interfaces;
- privacy harness invokes Booking executor.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `Booking` is paid-service scheduling truth; Cronofy is never Booking truth.
2. `Order` is transaction truth; Booking never infers payment success from Stripe or frontend redirect state.
3. Standard MVP pre-confirmation reservation is `BookingHold` + `BookingSlotLock`, not a pre-confirmation `Booking` row.
4. A normal Booking cannot be created until required Order and Agreement gates pass.
5. A listed slot is never reservation truth; hold creation rechecks availability server-side.
6. Prohibited overlapping active reservations/Bookings for the same Professional must be blocked by database concurrency controls.
7. An expired hold/lock is invalid even if an expiration worker has not yet updated status.
8. Priority scheduling never bypasses availability, overlap, Order, Agreement, authority, or hold gates.
9. Priority/entitlement truth remains external; Booking may preserve only historical effect/reference snapshots.
10. All authoritative Booking/BusyWindow instants are UTC.
11. `AvailabilityRule.startTime/endTime` are recurrence-local values only and require an IANA timezone.
12. External free/busy sync must not persist event descriptions, attendees, or private locations merely to block time.
13. Calendar provider callbacks are verified and deduplicated before Booking side effects.
14. `ProcessedCalendarEvent` remains separate from AuditEvent, BookingEvent, and other provider dedupe ledgers.
15. Provider writeback failure does not silently invalidate a confirmed Booking.
16. Booking lifecycle changes and required BookingEvent append are transactionally atomic.
17. Rescheduling reserves the new interval before changing the existing Booking.
18. The original Booking remains historical truth after reschedule; it is not overwritten in place without a reschedule chain.
19. Booking must not directly mutate Order, Agreement, VideoRoom, Thread, Notification, LocationReveal, ConsentLog, ComplianceHold, PrivacyRequest, or AuditEvent records.
20. BookingOrchestrationRun/Step own only Booking workflow request/ack state.
21. Every downstream orchestration step is idempotent; retry cannot duplicate the downstream semantic effect.
22. Provider payloads/types terminate at the calendar adapter.
23. Raw provider credentials/tokens never enter Booking tables, logs, or client responses.
24. Exact-location reveal/decryption remains Location Safety-owned.
25. Audit/observability records never replace Booking lifecycle or provider dedupe truth.
26. Privacy / Data Erasure owns legal request/job/exemption lifecycle; Booking only executes owner instructions.
27. JobInterview scheduling never uses Booking/BookingHold/BookingSlotLock as hiring truth.
28. No local premium/priority, blocked, authorization, consent, queue, retry, audit, or webhook framework may be created when a canonical SH operation exists.

---

## 34. Prohibited Duplicate Implementations

Do not create any of the following inside Booking & Calendar:

```text
bookingAuth.ts
calendarAuth.ts
getCurrentBookingUser.ts
bookingPermissionService.ts
calendarPermissionHelper.ts
isAdminBooking.ts
premiumBookingService.ts
priorityCustomerService.ts
isPriorityCustomer.ts
bookingUsageCounter.ts
calendarConsentService.ts       # generic consent truth replacement
bookingConsentLog.ts
bookingBlocked.ts
bookingComplianceHold.ts
orderPaidForBooking.ts
stripeBookingService.ts
bookingAgreementService.ts      # Agreement generation/signature owner theft
bookingVideoRoomService.ts      # Video owner theft
bookingChatService.ts           # Messaging owner theft
bookingEmailService.ts
calendarSmsService.ts
bookingNotificationProvider.ts
bookingAuditLog.ts
calendarAccessLog.ts            # generic audit replacement
bookingQueue.ts
bookingRetry.ts
bookingDeadLetter.ts
bookingIdempotencyStore.ts
bookingMutex.ts
slotMutex.ts
calendarWebhookDeduper.ts       # if separate from canonical SH-060 + ProcessedCalendarEvent
processedWebhook.ts             # generic competing provider ledger
globalProviderStatusMapper.ts
bookingEncryption.ts
addressCrypto.ts
bookingPrivacyRequest.ts
bookingErasureJob.ts
bookingRetentionExemption.ts
deliveryWorkflow.ts
genericDeliveryStatus.ts
calComAdapter.ts                # not approved MVP provider
nylasAdapter.ts                 # unless later explicitly approved
```

Provider-specific `cronofy-adapter.ts` is allowed because Booking owns the calendar provider relationship and SH-067 requires an adapter.

---

## 35. Unresolved Decisions

### U-BC-01 — CustomerProfile requiredness

Cluster/root rules establish `CustomerProfile` as buyer actor truth and current Booking-related schema has optional `customerProfileId` alongside `buyerUserId`.

**Question:** when does `customerProfileId` become database-required for BookingHold, BookingSlotLock, and Booking?

**Current safe rule:** new buyer workflows resolve and populate CustomerProfile; User remains auth/audit identity. Do not remove `buyerUserId` or make schema-requiredness changes without an approved migration decision.

### U-BC-02 — One Order to one or many Bookings

`Booking.orderId` is not unique.

**Question:** does one Order intentionally support multiple scheduled sessions?

**Blocks:** code that assumes one Booking per Order or adds uniqueness.

### U-BC-03 — One SlotLock to one or many Bookings

Current `BookingSlotLock.bookings[]` and nonunique `Booking.slotLockId` permit more than one Booking reference.

**Proposed Ruling:** ordinary hold conversion should produce exactly one Booking per SlotLock; add/confirm a uniqueness constraint if no approved multi-Booking use case exists.

### U-BC-04 — BookingHold duplicate lock reference

`BookingHold.lockId` coexists with relation through `BookingSlotLock.bookingHoldId`.

**Question:** which field is canonical and should the redundant path be removed?

**Safe implementation:** treat `BookingSlotLock.bookingHoldId`/relation as the authoritative relation and do not build behavior that requires both until migration is approved.

### U-BC-05 — Priority scheduling semantics

Entitlement truth exists, but the exact local effect of `priorityRank` is not defined.

Possible meanings—earlier booking window, queue ordering, reserved inventory, ranking, or tie-break—are materially different.

**Rule:** do not invent the effect. Implement entitlement lookup/snapshot plumbing and feature-flag/disable behavior that requires undefined semantics.

### U-BC-06 — Agreement generation orchestration step

`BookingOrchestrationStepType.generate_agreement` exists, but confirmed Cluster sequencing requires Agreement readiness **before** Booking confirmation when the Order requires it, while Booking orchestration Feature 10 is post-transition.

**Rule:** post-confirmation Booking orchestration must not generate a required pre-confirmation Agreement. The enum value remains reserved for an explicitly approved optional/post-confirmation use or later architecture revision.

### U-BC-07 — Booking exact-location snapshot contract

Current Booking fields include `exactAddressEncrypted`, `fuzzyLat`, `fuzzyLng`, and `locationRevealStatus`; Location Safety owns reveal/decryption truth.

**Proposed Ruling:** Booking fields are scheduling snapshots/caches only. Production in-person exact-address read/write/reveal remains blocked until the permitted snapshot fields, update source, retention, and decryption contract are explicitly approved.

### U-BC-08 — Calendar access-mode duplication

`accessMode`, `accessModeEnum`, `freeBusyOnly`, `metadataReadAllowed`, `eventWriteAllowed`, requested/granted scopes overlap.

**Question:** which fields are canonical policy, provider evidence, and compatibility data?

Do not add more parallel fields.

### U-BC-09 — Provider event/reference field semantics

Booking/BusyWindow include several external/provider event IDs, UIDs, calendar IDs, and versions.

**Question:** define the distinct semantic purpose and uniqueness/reconciliation rule for each before new writes depend on all of them.

### U-BC-10 — BookingEvent controlled vocabulary

`BookingEvent.name` is a free-form string.

**Proposed Ruling:** the Module event-name registry should be a controlled TypeScript union/constant set with versioning even if Prisma remains `String`; do not permit ad hoc names from call sites.

### U-BC-11 — Step-level durable idempotency identity

`BookingOrchestrationRun` has unique `idempotencyKey`; `BookingOrchestrationStep` does not.

**Question:** can the canonical idempotent job/command store fully guarantee per-step replay identity, or should the step schema receive a durable semantic command key?

### U-BC-12 — Step-up matrix

The exact calendar/admin/location actions requiring SH-014 fresh assurance are not supplied.

### U-BC-13 — BookingStatus cleanup

Current enum includes pre-confirmation and provider-failure states that the stronger CL-05 build sequence does not need in normal MVP.

**Question:** retain as reserved values or migrate/deprecate after existing data review?

### U-BC-14 — Professional Eligibility consumes Booking

Historical registry lists Professional Eligibility as a Booking consumer, but no exact contract is established.

Do not introduce a reverse dependency until a concrete need such as `hasBookableAvailability` is approved.

---

## 36. Architecture Decision Summary

### Binding rulings

- `booking_calendar` owns availability, BusyWindow, CalendarConnection, BookingHold, BookingSlotLock, Booking, BookingEvent, ProcessedCalendarEvent, and Booking orchestration truth.
- Standard MVP pre-confirmation state is BookingHold/SlotLock; new normal Booking rows are created only after required upstream confirmation gates and begin as `confirmed`.
- Booking is scheduling truth; Order is transaction truth.
- Cronofy is the current calendar provider target behind a provider-neutral Booking-owned port.
- Calendar provider callbacks are verified, deduplicated, translated, and applied before changing owner state.
- Free/busy sync stores intervals/provider reconciliation references, not unnecessary external calendar content.
- Atomic double-booking prevention is a database invariant using SH-058/Postgres mechanisms.
- BookingEvent remains separate domain history.
- Booking orchestration may request Calendar/Messaging/Notification/Location/Video/Agreement-owner operations but may not mutate their truth.
- CustomerProfile supplies buyer commercial context; User remains authentication/audit identity.
- Track entitlement supplies priority policy; Booking owns only the historical applied effect/snapshot.
- Location Safety remains exact-location reveal/decryption owner.
- Consent & Disclosure owns ConsentLog proof.
- ComplianceHold remains the reusable stop sign.
- Privacy owns PrivacyRequest/DataErasureJob/retention-exemption lifecycle; Booking implements the owner executor only.
- Audit/Observability remain evidence/ops, not Booking truth.

### Proposed rulings requiring approval before dependent schema/code commitment

- PR-BC-01: `BookingEventActor` and `BookingLocationType` are Booking-owned vocabularies.
- PR-BC-02: `BookingStatus.external_sync_failed` should not be used as core Booking lifecycle; `externalSyncStatus` represents provider writeback state.
- PR-BC-03: completion/no-show authority starts with Professional/admin/trusted system until buyer-report/dispute semantics are approved.
- PR-BC-04: adopt the versioned `booking.*` / `calendar.*` domain event namespace defined in Section 12.
- PR-BC-05: duplicate provider callbacks do not overwrite the original ProcessedCalendarEvent state with `ignored_duplicate`; duplicate observation remains operational unless a separate attempt model is approved.

### Implementation blockers / deferred decisions

- exact in-person location snapshot/read/write/reveal contract;
- priority scheduling behavioral semantics;
- BookingHold lock relationship cleanup;
- SlotLock→Booking cardinality;
- Order→Booking cardinality assumptions;
- access-mode/provider-reference field normalization;
- required-vs-post-confirmation Agreement orchestration semantics;
- exact step-up matrix;
- durable orchestration-step idempotency representation.

---

## 37. Coding-Agent Usage

Before implementing or modifying Booking & Calendar, use [context-map.md](../../../context-map.md) for authority by concern and actual artifact routing. Read:

1. [Project overview V3](../../../project-overview-v3.md), with V2 as routed supporting evidence;
2. [Canonical Shared Operations](../../../shared/shared-operations.md);
3. [CL-05 architecture](../scheduling-media-digital-delivery-cluster-architecture.md);
4. [CL-05 build plan](../scheduling-media-digital-delivery-cluster-build-plan.md);
5. [Booking architecture](booking-calendar-module-architecture.md);
6. [Booking implementation plan](booking-calendar-module-implementation-plan.md);
7. public-interface sections for direct dependencies, especially Identity/Authority, Customer Profile, Track Entitlement, Order/Agreement, Professional/Marketplace facts, Location Safety, Video Session, Messaging, Notification, Audit/Ops, Privacy, and Healthcare when applicable.

Root architecture/build plan, code standards, and a dedicated progress tracker are currently unavailable at the paths described by the context map. Their absence does not authorize a replacement global phase or precedence rule.

Before coding a feature, answer:

```text
Which Booking-owned record changes?
Which transition is allowed?
What upstream owner decision is required?
Which SH-### operations are invoked?
What is the idempotency key?
What is the database concurrency boundary?
What BookingEvent/domain event must be written?
What provider or downstream effect happens asynchronously?
What failure is retryable vs business denial?
What audit/ops evidence is additional but not source truth?
Does this feature touch an unresolved ruling?
```

If the requested implementation would decide an unresolved item, contradict an owner boundary, or require a new shared operation, stop that portion, record the architecture issue, and update context before committing the conflicting behavior.
