# Booking & Calendar Module Implementation Plan

> **Module ID:** `booking_calendar`  
> **Module:** Booking & Calendar Module  
> **Primary Cluster:** `CL-05 — Scheduling, Media & Digital Delivery`  
> **Companion architecture:** `module-architecture.md`  
> **Repository target:** `context/clusters/scheduling-media-digital-delivery/modules/booking_calendar/implementation-plan.md`  
> **Plan status:** Module-level implementation sequence subordinate to the root Workin Ants build plan and CL-05 build plan. It does not independently change Cluster sequence or ownership.

---

## Core Principle

Implement Booking & Calendar through narrow, verifiable owner slices:

```text
public / observable scheduling behavior
→ validated command/query
→ Booking-owned policy
→ Booking-owned authoritative read/write
→ canonical SH-### operations and owner interfaces
→ BookingEvent / outbox / downstream requests
→ tests
→ explicit exit gate
```

A slice is complete only when its source-of-truth behavior, authorization, concurrency/idempotency, failure path, and cross-Module contract are proven. A UI happy path is not completion by itself.

This Module plan is deliberately narrower than CL-05 `build-plan.md`. It implements only Booking & Calendar truth and its owned calendar integration/orchestration. It does **not** implement Video Session rooms/tokens, Order/payment state, Agreement generation/signature, Notification delivery, Messaging lifecycle, Location Safety policy, Privacy orchestration, or generic shared infrastructure.

---

## Build Rules

1. Follow root project overview, root architecture/build plan/code standards, Canonical Shared Operations, CL-05 architecture/build plan, and `module-architecture.md`.
2. Booking & Calendar writes only its declared source truth.
3. Cross-Module reads/commands use approved public interfaces; do not import foreign repositories for convenience.
4. Reuse canonical SH-### operations. If a required canonical implementation is missing, depend on its interface/test double or coordinate the owner prerequisite; do not create a Booking-local substitute.
5. All mutations validate input, resolve trusted actor/system context, authorize server-side, and enforce Booking-owned invariants.
6. The normal MVP pre-confirmation lifecycle is `BookingHold` + `BookingSlotLock`; do not create a pre-confirmation `Booking` row for `held`, `awaiting_agreement`, or `awaiting_payment`.
7. Booking confirmation occurs only after authoritative Order entitlement and required Agreement readiness succeed.
8. Database constraints/transactions—not in-memory locks—enforce slot contention.
9. Provider details remain behind `CalendarProviderPort`; Cronofy payloads do not spread through domain/application contracts.
10. Every provider callback is signature-verified, owner-deduplicated, translated, and then applied.
11. Slow/provider-dependent work uses the shared reliable-job/retry framework.
12. Every Booking lifecycle mutation writes required `BookingEvent` atomically and publishes downstream facts through the transactional outbox where needed.
13. External effects are idempotent and reconcilable.
14. `CalendarConnection`, `BusyWindow`, and Booking external sync state may reflect provider effects; provider failure does not silently redefine Booking transaction/scheduling truth.
15. Track entitlement remains external policy truth. Booking may snapshot the applied priority decision, not the current plan/subscription lifecycle.
16. `ComplianceHold` remains the reusable stop sign; do not add generic local block flags.
17. Location Safety remains exact-location reveal/decryption owner.
18. Privacy / Data Erasure remains request/job/exemption owner; Booking implements only its owner executor.
19. Every numbered feature ends with automated tests, workflow/contract verification, documentation/progress update, and an explicit exit gate.
20. Unresolved architecture must be surfaced rather than guessed. If a feature reaches a blocking unresolved decision, implement only the noncontroversial contract/mechanism and mark the remainder blocked.

---

## Preconditions

### Hard platform dependencies

The following must exist in production form or as stable canonical interfaces/test doubles before the relevant feature begins:

- Prisma/PostgreSQL migration pipeline and transaction support;
- runtime validation and strict TypeScript conventions;
- SH-001 authenticated actor context;
- SH-002 Role / Authority decision interface;
- SH-004 CustomerProfile resolver;
- SH-029/030 Audit interfaces;
- SH-032/034/037/038 Observability/queue telemetry interfaces;
- SH-044 idempotent-command primitive;
- SH-046 transactional outbox/domain event publication;
- SH-047/048 durable queue/retry framework;
- SH-051/052 persistence concurrency helpers;
- SH-053 lifecycle transition plumbing;
- SH-055 deadline-expiration runner;
- SH-056/058 atomic reservation / interval lock capability;
- secret management for provider credentials.

Booking must not become the temporary owner of any of these systems.

### Hard owner-interface dependencies by phase

Before **reservation/confirmation**:

- Professional/target owner validation/facts interface;
- CustomerProfile resolver;
- Track Entitlement SH-005 and SH-006 if priority scheduling is enabled;
- Order SH-025 booking entitlement;
- Agreement readiness interface if required by Order policy;
- ComplianceHold SH-011.

Before **calendar provider integration**:

- Consent SH-007/008;
- provider authorization SH-064;
- webhook raw-body route support;
- Cronofy credentials/configuration;
- SH-059–062 provider security/dedupe/translation/reconciliation framework.

Before **orchestration**:

- Messaging SH-113;
- Notification SH-041;
- Location Safety SH-027 where in-person flow requires evaluation;
- Video Session public command contract may initially be a stub until CL-05 Feature 11 is implemented.

Before **privacy/hardening**:

- Privacy SH-095–097 protocol;
- approved root security/step-up matrix where sensitive manual retries require SH-014;
- production Cronofy configuration and reconciliation access.

### Schema prerequisites / review items

The current Prisma schema contains Booking-owned models, but implementation must inspect existing migrations rather than recreating them blindly.

Before Feature 03, verify or add an explicit database overlap/exclusion mechanism for active `BookingSlotLock`/Booking intervals.

Do **not** silently resolve these schema questions inside a feature:

- `BookingHold.lockId` versus relation through `BookingSlotLock.bookingHoldId`;
- `BookingSlotLock.bookings[]` / nonunique `Booking.slotLockId` cardinality;
- one Order to one versus many Bookings;
- exact-location snapshot fields;
- duplicate CalendarConnection access-mode fields;
- provider reference field semantics;
- `BookingStatus.external_sync_failed` cleanup;
- orchestration-step durable idempotency column.

### Provider posture

Cronofy is the current Booking & Calendar MVP provider. `Nylas`/`direct` enum values do not authorize parallel adapters.

Manual availability/holds/Booking lifecycle must be implementable before Cronofy so provider availability does not block Booking source-truth work.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Booking Contracts, Schema Readiness, and Owner Boundary

### Objective

Establish the executable Booking & Calendar boundary: owned repositories/models, stable public contracts, reason codes, lifecycle policies, and database invariants needed by later features without implementing full user workflows yet.

### Observable Result

Tests/dev harness can instantiate Booking-owned repositories/services against the current schema, validate the owner boundary, and exercise typed contract stubs without importing Order, Consent, Video, Messaging, Notification, Location, Hold, Entitlement, or Privacy repositories.

### Cluster Build-Plan Link

- Prerequisite to CL-05 Feature **07**.
- Supports root schema/source-of-truth baseline and root delivery Phase 7.
- Does not reorder CL-05; it prepares the Booking owner for Feature 07 implementation.

### Dependencies

- current Prisma schema/migration tooling;
- `module-architecture.md` unresolved-decision register;
- SH-031, SH-044, SH-046, SH-051–053 interface availability;
- root/shared validation and error patterns.

### In Scope

- Booking-owned module directory and public contract boundary;
- repository interfaces for owned models;
- typed action vocabulary and reason codes;
- lifecycle transition definitions for Hold, SlotLock, Booking, CalendarConnection, orchestration run/step;
- normalized owner-facts DTO for Booking consumers;
- BookingEvent append convention;
- transactional outbox hook contract;
- migration/constraint audit for Booking-owned tables;
- schema conflict report for unresolved items;
- test fixtures/builders for owned records.

### Out of Scope

- visible slot picker;
- actual BookingHold acquisition;
- Order-gated confirmation;
- Cronofy calls;
- Video, Messaging, Notification, Location implementations;
- schema changes that settle unresolved cardinality/location/access-mode questions without approval.

### Module-Owned Data

Review/use:

- `AvailabilityRule`;
- `CalendarConnection`;
- `BusyWindow`;
- `BookingHold`;
- `BookingSlotLock`;
- `Booking`;
- `BookingEvent`;
- `ProcessedCalendarEvent`;
- `BookingOrchestrationRun`;
- `BookingOrchestrationStep`;
- owned enums listed in Module architecture.

### Public Interfaces

Introduce contract definitions for:

```text
upsertAvailabilityRule
deactivateAvailabilityRule
listBookableSlots
evaluateSlotAvailability
createBookingHold
releaseBookingHold
confirmBooking
cancelBooking
rescheduleBooking
completeBooking
markBookingNoShow
getBooking
getBookingOwnerFacts
listCustomerBookings
listProfessionalBookings
connectCalendar
completeCalendarConnection
disconnectCalendar
getCalendarConnection
applyCalendarProviderEvent
startBookingOrchestration
retryBookingOrchestrationStep
getBookingDeliverySetupStatus
```

Interfaces may be unimplemented/stubbed in this feature, but types and ownership must be stable enough for dependency contract tests.

### Shared Operations Used

- **SH-031 `appendDomainLifecycleEvent`** — define how BookingEvent is written transactionally; local policy is event vocabulary/metadata.
- **SH-044 `executeIdempotentCommand`** — define semantic-key requirements for commands; no local idempotency framework.
- **SH-046 `publishDomainEvent`** — define Booking outbox envelope contract; no local event bus.
- **SH-051 / SH-052 / SH-053** — define aggregate locking, stale-write, and state-machine integration points; Booking retains its transition graph.
- **SH-123 `validateOwnedTargetReference`** — define foreign owner-validation contracts rather than foreign repositories.

### Domain Logic

- Encode the binding MVP rule: no normal Booking row exists before confirmation.
- Define legal Hold/SlotLock/Booking transition graphs.
- Define BookingEvent actor/reason/metadata requirements.
- Define stable reason-code taxonomy.
- Define provider-independent Booking contracts.
- Define `getBookingOwnerFacts` minimum fields and explicitly exclude payment/location reveal/video truth.

### Authorization / Compliance

- Define Booking action vocabulary to be interpreted by SH-002 later.
- Do not encode platform role logic locally.
- Mark exact-location fields as blocked behind U-BC-07.
- Mark step-up-requiring actions as unresolved until root matrix exists.

### Database / Transaction Behavior

- Confirm migration state for owned tables/indexes/unique constraints.
- Verify `ProcessedCalendarEvent(provider, providerEventId)` uniqueness.
- Verify `BookingOrchestrationRun.idempotencyKey` uniqueness.
- Confirm `BookingHold.booking` relation/unique source hold behavior.
- Produce explicit pending migration note for overlap exclusion if not present.
- Do not add uniqueness to `orderId` or `slotLockId` without approved cardinality ruling.

### Events / Jobs

No production worker required. Establish job payload/owner contracts for later expiration, provider sync, orchestration, reconciliation, and privacy execution.

### Provider Integration

Define `CalendarProviderPort` only. No Cronofy client call yet.

### UI / Admin Surface

No user UI required. A development contract harness or tests are sufficient.

### Failure Behavior

- unresolved schema conflict → fail feature exit gate only if it blocks the next feature; otherwise record explicit deferred decision;
- foreign owner dependency missing → use typed test fake, not direct Prisma;
- incompatible existing migration → record/prepare owner migration rather than hiding mismatch.

### Tests

- Type-level/public contract tests;
- lifecycle transition unit tests;
- prohibited import/dependency boundary test if repo tooling supports it;
- BookingEvent metadata validation tests;
- reason-code exhaustiveness tests;
- migration/schema inspection tests;
- clean Prisma validate/generate/migrate test where available.

### Documentation Updates

- update Module architecture if a schema ownership conflict is legitimately ruled;
- update Shared Operations only if a genuinely missing canonical operation is discovered;
- record unresolved schema decisions in progress tracker.

### Acceptance Criteria

- Booking owner code can compile/test without foreign repositories;
- every Booking-owned lifecycle has an explicit transition policy;
- public contracts do not expose Prisma/provider payloads directly;
- reason codes and owner-facts DTO are stable;
- overlap-constraint state is explicitly known;
- unresolved cardinality/location/access-mode questions remain documented rather than guessed.

### Exit Gate

**PASS only if:**

- module boundary compiles and tests;
- source-truth ownership matches architecture;
- no duplicate shared infrastructure is introduced;
- BookingEvent/public contract patterns are established;
- database overlap work required for Feature 03 is clearly identified;
- all blocking unresolved issues for Feature 02 are either resolved or proven irrelevant to manual availability/slot projection.

---

## 02 Professional Availability and Bookable Slot Projection

### Objective

Implement recurring professional availability and server-owned slot calculation before any slot reservation or external calendar integration.

### Observable Result

An authorized Professional can create/deactivate recurring availability. An authorized consumer can query candidate slots over a date range and receive UTC intervals rendered with explicit timezone context. Existing manual/system BusyWindows and confirmed Bookings are subtracted.

### Cluster Build-Plan Link

Supports the first half of CL-05 Feature **07 — Professional Availability, Slot Search, and Atomic Booking Holds**.

### Dependencies

- Feature 01;
- SH-001/002 actor and authorization;
- Professional owner target/facts interface via SH-123;
- timezone library already approved by root/Cluster (`date-fns-tz` or Luxon evidence exists; use repository-selected one, do not add both casually).

### In Scope

- `upsertAvailabilityRule`;
- `deactivateAvailabilityRule`;
- recurrence expansion;
- DST-safe UTC conversion;
- candidate slot generation for requested duration;
- subtraction of BusyWindow, confirmed Booking, and active reservation blockers when present;
- `listBookableSlots`;
- `evaluateSlotAvailability` read decision;
- UI: minimal professional availability editor and buyer/test slot picker if surrounding UI foundation exists.

### Out of Scope

- BookingHold/SlotLock writes;
- priority scheduling behavior beyond contract placeholder;
- Order entitlement;
- Cronofy connection/sync;
- exact location;
- Booking confirmation.

### Module-Owned Data

- `AvailabilityRule` / `AvailabilityRuleSource`;
- read `BusyWindow`;
- read confirmed Booking intervals;
- read active BookingSlotLock/BookingHold if present from fixtures/future feature.

### Public Interfaces

- implement `upsertAvailabilityRule`;
- implement `deactivateAvailabilityRule`;
- implement `listBookableSlots`;
- implement `evaluateSlotAvailability`.

### Shared Operations Used

- **SH-001 `resolveAuthenticatedActor`** — professional/user context.
- **SH-002 `authorizeResourceAction`** — manage availability / protected slot query context.
- **SH-044** — idempotent rule mutation when mutation transport retries.
- **SH-123** — Professional target validation/facts.
- SH-032/034 — safe request/telemetry context.

No Booking-local auth/time infrastructure may be created.

### Domain Logic

- validate `weekday` and local time format;
- require valid IANA timezone;
- enforce `startTime < endTime` under the defined recurrence-day semantics;
- effectiveUntil cannot precede effectiveFrom;
- expand recurring rules only inside requested date range;
- convert candidate interval instants to UTC;
- handle DST gap/fold deterministically and test the chosen behavior;
- subtract BusyWindows and existing blocking intervals;
- never expose raw external calendar event metadata;
- return freshness/evaluatedAt to communicate that slot list is a projection;
- client must not infer reservation guarantee from slot presence.

### Authorization / Compliance

- only authorized Professional actor manages their availability;
- public/buyer slot query reveals only approved availability intervals, not private BusyWindow sources/details;
- exact address/calendar provider details are absent.

### Database / Transaction Behavior

- AvailabilityRule create/update follows unique constraint `(professionalProfileId, weekday, startTime, endTime, timezone)`;
- mutations use expected version/updatedAt if repo standard requires stale-write protection;
- slot query is read-only and does not acquire reservation locks.

### Events / Jobs

No job required. A future availability-change domain event may be added only when a concrete consumer needs it and PR-BC-04 event namespace is approved.

### Provider Integration

None.

### UI / Admin Surface

If UI foundation exists:

- Professional availability editor with timezone label;
- buyer slot picker using returned UTC intervals;
- empty/no-availability state;
- invalid-time/timezone feedback.

Do not show BusyWindow source event text.

### Failure Behavior

- invalid timezone/time range → validation denial;
- unauthorized Professional mutation → forbidden;
- stale rule mutation → conflict;
- malformed recurrence → fail closed;
- slot query with no availability → successful empty result, not error.

### Tests

- recurrence by weekday;
- effective date bounds;
- multiple rules/day;
- DST spring-forward and fall-back fixtures;
- timezone conversion;
- BusyWindow subtraction;
- confirmed Booking subtraction;
- private metadata non-exposure;
- authorization matrix;
- query contract/freshness result.

### Documentation Updates

Document the exact DST recurrence behavior if implementation clarifies it beyond architecture text.

### Acceptance Criteria

- professional availability can be created/deactivated through owner command;
- returned slot instants are UTC and carry display timezone context;
- BusyWindows/confirmed Bookings remove candidate intervals;
- no provider or transaction truth is required;
- no private BusyWindow/provider details leak.

### Exit Gate

**PASS only if:** timezone/DST unit suite, authorization tests, slot-projection integration tests, typecheck/lint/build checks applicable to the repository all pass and no reservation write exists in the slot-query path.

---

# Phase 2 — Atomic Reservation

## 03 Atomic BookingHold and BookingSlotLock

### Objective

Let an authenticated customer atomically reserve one eligible interval using BookingHold + BookingSlotLock, with deterministic expiration, idempotency, conflict handling, and external priority-entitlement snapshot plumbing.

### Observable Result

A buyer selects a currently bookable slot and receives an active hold with expiry. Two concurrent prohibited reservations for the same Professional/interval cannot both succeed. A duplicate request returns the original semantic reservation. Expired/released holds cannot later convert.

### Cluster Build-Plan Link

Completes CL-05 Feature **07**.

### Dependencies

- Features 01–02;
- SH-004 CustomerProfile resolver;
- SH-005 priority entitlement resolver;
- SH-006 only if approved priority usage is metered at hold time;
- SH-056/058 database atomic reservation;
- real DB migration implementing overlap protection;
- SH-055 expiration worker framework.

### In Scope

- `createBookingHold`;
- `releaseBookingHold`;
- active hold/lock expiration owner commands;
- DB overlap/exclusion migration if missing and architecture-approved;
- priority decision lookup + historical snapshot fields;
- idempotency key/fingerprint behavior;
- hold countdown/read model;
- concurrency tests under real database transactions.

### Out of Scope

- Booking confirmation;
- payment/Agreement mutation;
- undefined priority scheduling behavior beyond safe snapshot plumbing;
- external calendar calls;
- location reveal;
- Video room.

### Module-Owned Data

- `BookingHold` / `BookingHoldStatus`;
- `BookingSlotLock` / `BookingSlotLockStatus`;
- priority snapshot fields;
- `providerAvailabilityHash` only if a clear freshness use is defined.

### Public Interfaces

- implement `createBookingHold`;
- implement `releaseBookingHold`;
- internal `expireBookingHold` / `expireBookingSlotLock` owner commands;
- expose safe hold read/status if UI requires it.

### Shared Operations Used

- SH-001 / SH-002 — authenticated authorized customer action;
- **SH-004 `resolveCustomerActor`** — commercial buyer context;
- **SH-005 `resolveEntitlement`** — priority scheduling decision;
- SH-006 — only if approved usage policy says reservation consumes a metered unit;
- **SH-044 `executeIdempotentCommand`** — one semantic hold per idempotency key/fingerprint;
- **SH-051 `acquireAggregateLock`** — constrained resource locking if required by chosen DB implementation;
- **SH-056 `executeAtomicReservation`** — scarce interval reservation mechanism;
- **SH-058 `acquireIntervalLock`** — Booking-specific overlap policy over Postgres;
- **SH-055 `runDeadlineExpiration`** — durable expiration sweep;
- **SH-109 `snapshotExternalDecision`** — historical priority effect/reference;
- SH-123 — validate Professional/optional Order target.

Prohibited duplicate: in-memory/Redis-only `bookingMutex`, local plan checker, local usage counter, custom scheduler framework.

### Domain Logic

1. Resolve actor → CustomerProfile.
2. Validate Professional and requested UTC interval.
3. Re-run `evaluateSlotAvailability` inside the reservation path.
4. Resolve priority entitlement if enabled.
5. Apply only an approved Booking-local priority effect; if U-BC-05 is unresolved, persist decision/snapshot plumbing without enabling undefined advantage.
6. In one transaction acquire prohibited-overlap protection and create Hold/SlotLock pair.
7. Set authoritative `expiresAt`.
8. Return hold ID/expiry/safe display data.
9. Every later command validates `expiresAt > serverNow` even if worker status is stale.
10. Release/expire transitions both hold and lock consistently.

### Authorization / Compliance

- buyer must resolve to CustomerProfile;
- priority is external truth and cannot bypass overlap;
- ComplianceHold may be consulted if Cluster policy marks hold creation as hold-sensitive; if not yet approved, confirmation remains the mandatory hold gate and hold-creation policy stays explicit;
- no payment status is written/read from Stripe.

### Database / Transaction Behavior

Required:

- overlap constraint/range strategy enforced by PostgreSQL;
- unique idempotency key on SlotLock used as part of semantic execution;
- hold and lock created atomically;
- one relation path is used consistently; do not write both `BookingHold.lockId` and the relational FK unless the schema ruling explicitly requires it;
- `expiresAt` indexed for sweeps;
- interval checks use half-open range semantics `[start,end)` unless root DB policy says otherwise, allowing back-to-back bookings without overlap.

### Events / Jobs

- durable hold/lock expiration worker using SH-055/047;
- optional hold-created/released/expired outbox facts only after PR-BC-04 event namespace approval;
- queue lag cannot extend business validity.

### Provider Integration

None.

### UI / Admin Surface

- buyer hold countdown/expiry state;
- clean `slot_unavailable` conflict;
- professional/admin diagnostic may show lock IDs/status without sensitive buyer details beyond authority.

### Failure Behavior

- stale slot list → `slot_unavailable`, no partial rows;
- parallel conflict → one winner, others conflict;
- duplicate identical command → replay same reservation result;
- same idempotency key/different payload → idempotency conflict;
- entitlement service temporary failure → fail/return retryable according to product policy, never invent priority;
- expiration worker delayed → command-time expiry still denies conversion;
- DB transaction failure → no orphan hold or lock.

### Tests

- parallel 2/10/50-client same-slot contention as practical;
- adjacent interval non-overlap;
- partial-overlap conflicts;
- duplicate command/fingerprint mismatch;
- hold release/expire terminal behavior;
- expiry boundary with controlled clock;
- CustomerProfile requirement;
- priority snapshot/no-bypass;
- migration constraint test from clean DB;
- E2E slot → hold; second client conflict.

### Documentation Updates

- record exact Postgres exclusion/range implementation in architecture if previously unresolved;
- update schema relationship ruling if `lockId` cleanup is approved;
- update priority policy only if U-BC-05 is actually resolved.

### Acceptance Criteria

- prohibited overlapping reservations cannot both commit;
- Hold and SlotLock are one atomic reservation effect;
- command retries do not duplicate reservations;
- server time controls expiry;
- priority truth is externally resolved and only snapshotted;
- no provider/payment/Agreement truth is introduced.

### Exit Gate

**PASS only if:** real database concurrency tests prove the overlap invariant, expiration/release/idempotency tests pass, clean migration passes, and a buyer can hold a slot without any Cronofy/Stripe/Video implementation.

---

# Phase 3 — Booking Lifecycle

## 04 Order-Gated Booking Confirmation

### Objective

Convert one valid active hold/lock into one authoritative `Booking(status=confirmed)` only after authoritative upstream transaction/legal gates succeed.

### Observable Result

A valid eligible Order can confirm its held slot into a Booking. Ineligible/refunded/disputed/not-ready Orders, incomplete required Agreements, active blocking holds, expired reservations, and duplicate/stale confirmation attempts cannot create a second or invalid Booking.

### Cluster Build-Plan Link

First half of CL-05 Feature **08 — Order-Gated Booking Confirmation and Booking Lifecycle**.

### Dependencies

- Feature 03;
- SH-025 Order entitlement;
- Agreement readiness public interface;
- SH-011 ComplianceHold;
- SH-031/046 event/outbox;
- SH-051/052/053 concurrency/transition primitives.

### In Scope

- `confirmBooking`;
- confirmation gate composition;
- Booking source record creation at `confirmed`;
- Hold/SlotLock conversion;
- initial `BookingEvent`;
- outbox fact;
- `getBooking` and `getBookingOwnerFacts` confirmed-state reads;
- CustomerProfile/buyer snapshot population according to current schema and owner contract.

### Out of Scope

- pre-confirmation Booking statuses;
- direct payment/Stripe logic;
- Agreement generation/signature logic;
- calendar writeback;
- Video room;
- exact-location reveal;
- Notification delivery.

### Module-Owned Data

- `Booking`;
- `BookingEvent`;
- converted `BookingHold`;
- converted `BookingSlotLock`;
- priority/timezone/local approved snapshots.

### Public Interfaces

- implement `confirmBooking`;
- implement `getBooking`;
- implement `getBookingOwnerFacts`.

### Shared Operations Used

- SH-001/002 — actor and authorization where user-triggered;
- **SH-011 `evaluateComplianceHold`** — reusable stop sign;
- **SH-025 `authorizeOrderEntitlement`** — authoritative transaction booking gate;
- SH-123 — target/relationship validation if needed;
- **SH-031 `appendDomainLifecycleEvent`** — BookingEvent in transaction;
- **SH-044** — confirmation idempotency;
- **SH-046** — transactional outbox after source change;
- **SH-051 / SH-052 / SH-053** — reservation locks/stale transition/lifecycle plumbing;
- SH-109 — carry historically material priority decision snapshot.

### Domain Logic

1. Resolve/authorize actor or trusted system workflow.
2. Lock/read Hold + SlotLock.
3. Validate both are active and unexpired at server time.
4. Obtain current SH-025 Order booking-entitlement decision and source evidence/version.
5. Obtain Agreement readiness if Order requires it.
6. Evaluate applicable ComplianceHold.
7. Revalidate reservation relationship/Professional/customer.
8. Create one `Booking(status=confirmed)`; standard MVP does not create held/awaiting Booking first.
9. Convert Hold/Lock.
10. Append BookingEvent `confirmed`.
11. Persist outbox fact atomically.
12. Return Booking result. Provider/downstream setup is not part of the confirmation transaction.

### Authorization / Compliance

- Order participant relationship comes from Order owner, not client claims;
- exact location remains hidden;
- active applicable hold denies confirmation;
- no healthcare/location provider behavior is inferred yet;
- buyer/professional/admin/system authorization matrix follows SH-002 action contracts.

### Database / Transaction Behavior

Within one Booking-owned DB transaction:

- lock Hold/SlotLock row(s);
- assert current active/unexpired state;
- assert no Booking already exists for source hold where schema unique relation applies;
- create Booking;
- convert Hold/SlotLock;
- append BookingEvent;
- insert outbox record through canonical infrastructure.

Cross-Module Order/Agreement data is not directly locked via foreign repository. Carry authoritative decision evidence/version; if interface cannot safely support the race, record that contract blocker rather than cross-domain locking.

### Events / Jobs

- emit/persist `booking.confirmed.v1` after PR-BC-04 approval;
- no provider job is required for confirmation itself;
- orchestration consumer may initially be a test subscriber until Feature 08.

### Provider Integration

None.

### UI / Admin Surface

- Booking confirmation status/detail;
- denial reason/remediation for expired hold, Order not entitled, Agreement not ready, hold blocked;
- do not surface Stripe/Cronofy provider state as confirmation truth.

### Failure Behavior

- Order not entitled → no Booking, reservation handling follows explicit policy (keep until expiry or release if terminal denial);
- Agreement incomplete → no Booking;
- expired/released Hold/Lock → conflict, never resurrect;
- duplicate confirm → replay same Booking;
- stale/competing conversion → conflict;
- outbox dispatch delayed → Booking remains committed; publisher retries.

### Tests

- Order allow/deny/refund/dispute contract matrix;
- Agreement required/not-required/ready/not-ready;
- ComplianceHold block/release decision;
- expiry/confirm race;
- duplicate concurrent confirmation;
- Booking + BookingEvent + converted reservation atomicity;
- outbox persistence atomicity;
- public owner-facts minimization;
- E2E hold → confirm.

### Documentation Updates

If Order/Agreement public contract needs a new source-version/revalidation token, update owner interface docs rather than direct-querying foreign tables.

### Acceptance Criteria

- no Booking exists before required gates;
- exactly one confirmed Booking results from one reservation;
- BookingEvent is present atomically;
- Order/Agreement state remains external;
- confirmation works with calendar/video providers completely offline/unimplemented.

### Exit Gate

**PASS only if:** all gate/transaction/idempotency/concurrency tests pass and code review confirms zero direct Stripe/Agreement/foreign repository mutation inside Booking.

---

## 05 Cancellation, Reschedule, Completion, and No-Show

### Objective

Complete the core Booking lifecycle after confirmation with deterministic transitions, reschedule safety, event history, and downstream facts while keeping financial/dispute/provider consequences external.

### Observable Result

Authorized actors can cancel, reschedule, complete, or mark no-show according to the approved initial action matrix. Reschedule never loses the original confirmed Booking if the new slot reservation fails. Booking history clearly shows the transition chain.

### Cluster Build-Plan Link

Completes CL-05 Feature **08**.

### Dependencies

- Feature 04;
- Feature 03 reservation mechanics reused for reschedule;
- SH-002 action authorization;
- SH-031/046 lifecycle evidence/outbox;
- SH-051/052/053 concurrency/transition plumbing;
- Order owner public command/event contract for any downstream financial/business reaction, without Booking mutation of Order.

### In Scope

- `cancelBooking`;
- `rescheduleBooking`;
- `completeBooking`;
- `markBookingNoShow`;
- list customer/professional bookings;
- reschedule chain and old/new Booking event history;
- cancellation deadline scheduling semantics (not refund consequence);
- stable stale-transition conflicts.

### Out of Scope

- refund calculation/issuance;
- dispute adjudication;
- payout effects;
- calendar writeback (Feature 08);
- Video cancellation mechanics (Video owner);
- buyer self-reported no-show authority beyond approved policy.

### Module-Owned Data

- `Booking` status/timestamps;
- `BookingEvent`;
- new Hold/SlotLock for reschedule;
- new confirmed Booking with `rescheduledFromBookingId`;
- old Booking → `rescheduled`.

### Public Interfaces

- implement `cancelBooking`;
- implement `rescheduleBooking`;
- implement `completeBooking`;
- implement `markBookingNoShow`;
- implement `listCustomerBookings`;
- implement `listProfessionalBookings`.

### Shared Operations Used

- SH-001/002 — actor/authorization;
- SH-011 — hold gate where action policy requires;
- SH-025 — re-check current Order entitlement where a reschedule requires it;
- SH-031/044/046 — event/idempotency/outbox;
- SH-051/052/053 — transition concurrency;
- SH-056/058 — new interval reservation for reschedule;
- SH-109 — preserve priority snapshot if new reservation applies current policy.

### Domain Logic

#### Cancel

- allowed only from current confirmed state under initial MVP graph;
- record `cancelledAt` and BookingEvent;
- cancellation deadline may affect a reason/result or downstream Order request, but Booking does not decide refund amount/status;
- publish cancellation fact for later orchestration.

#### Reschedule

1. authorize action;
2. reserve new interval using the same safe Hold/SlotLock mechanism;
3. re-check Order/Agreement/hold gates as required;
4. in a transaction create new confirmed Booking linked from old; mark old `rescheduled`; convert new reservation; append events/outbox;
5. if any pre-switch step fails, old Booking remains confirmed/unmodified.

#### Complete

- transition confirmed → completed under approved actor policy;
- publish fact; Order owner decides any transaction completion effect.

#### No-show

- transition confirmed → no_show under PR-BC-03 initial restricted actor policy;
- record reason/evidence references safely;
- financial/dispute consequence external.

### Authorization / Compliance

Initial policy per PR-BC-03:

- professional/admin/trusted system may complete/no-show subject to SH-002;
- buyer can cancel/reschedule where product action policy permits;
- buyer self-report is not final no-show truth until dispute semantics are approved;
- admin/support actions are audited if policy requires.

### Database / Transaction Behavior

- use expected version or locked aggregate for each transition;
- append BookingEvent atomically;
- reschedule old/new Booking state + reservation conversion + events/outbox must commit consistently;
- prevent double-reschedule via stale version conflict;
- never overwrite old slot timestamps as sole reschedule history.

### Events / Jobs

- `booking.cancelled.v1`;
- `booking.rescheduled.v1` with old/new Booking IDs and safe times;
- `booking.completed.v1`;
- `booking.no_show.v1`;
- orchestration will consume facts in Feature 08.

### Provider Integration

None in lifecycle transaction.

### UI / Admin Surface

- Booking detail/timeline;
- cancel/reschedule controls;
- completion/no-show controls only for authorized roles;
- stale/conflict feedback;
- reschedule shows new Booking while preserving historical prior Booking.

### Failure Behavior

- invalid terminal transition → `invalid_transition`;
- stale version → `stale_version`;
- new reschedule slot unavailable → original Booking unchanged;
- upstream gate changes during reschedule → no switch;
- downstream outbox consumer unavailable → source transition remains committed.

### Tests

- complete transition matrix and prohibited shortcuts;
- concurrent cancel vs reschedule;
- concurrent reschedule vs reschedule;
- failed new reservation preserves old Booking;
- reschedule chain integrity;
- BookingEvent atomicity/order;
- actor authorization matrix;
- E2E confirm → reschedule/cancel/complete/no-show representative flows.

### Documentation Updates

Update Module architecture only if actor matrix/cancellation semantics are formally approved beyond current Proposed Ruling.

### Acceptance Criteria

- all lifecycle paths are owner-controlled and evented;
- reschedule is reservation-before-switch;
- no Order/refund/provider truth is mutated directly;
- stale concurrent transitions are deterministic.

### Exit Gate

**PASS only if:** transition/concurrency/E2E tests pass, reschedule failure never corrupts original Booking, and external financial/provider effects are represented only as downstream contracts/events.

---

# Phase 4 — Calendar Provider Boundary

## 06 Calendar Connection, Consent, and Provider Authorization

### Objective

Create the Cronofy-backed `CalendarConnection` lifecycle with standalone consent proof, least-privilege scopes, secure provider authorization, and normalized connection state—without yet relying on webhook-driven BusyWindow synchronization.

### Observable Result

An authorized Professional can connect and disconnect a calendar. The UI/API shows Workin Ants connection/provider/access state. A connection cannot become active without required Consent proof and successful provider authorization. Provider credentials never appear in client data.

### Cluster Build-Plan Link

First half of CL-05 Feature **09 — Cronofy Calendar Connection and Free/Busy Synchronization**.

### Dependencies

- Feature 01 contracts;
- Consent SH-007/008;
- SH-064 provider connection framework;
- SH-067 CalendarProviderPort;
- Cronofy credentials/config;
- secret store/providerCredential reference;
- raw callback route and redirect allowlist.

### In Scope

- `connectCalendar`;
- `completeCalendarConnection`;
- `disconnectCalendar`;
- `getCalendarConnection`;
- CalendarProviderPort + Cronofy adapter authorization/disconnect methods;
- least-privilege scope/access-mode mapping;
- `CalendarConnection` lifecycle and provider status mapping;
- security/audit/telemetry around connection management.

### Out of Scope

- free/busy import;
- provider webhook BusyWindow mutation;
- calendar writeback for Booking events;
- Nylas/direct adapter;
- storing raw external event details.

### Module-Owned Data

- `CalendarConnection`;
- `CalendarConnectionStatus`;
- `CalendarConnectionProviderStatus`;
- source/integration provider, sync direction, access-mode/scope evidence;
- safe provider references.

### Public Interfaces

- implement `connectCalendar`;
- implement `completeCalendarConnection`;
- implement `disconnectCalendar`;
- implement `getCalendarConnection`;
- implement CalendarProviderPort authorization/disconnect contract.

### Shared Operations Used

- SH-001/002 — Professional actor and authority;
- **SH-007 / SH-008** — record/query current calendar disclosure consent;
- **SH-064 `authorizeExternalProviderConnection`** — state/nonce/redirect/scopes;
- **SH-067 `invokeCalendarProvider`** — only provider access point;
- SH-044 — idempotent connection command/callback;
- SH-029/030 — audit/sensitive access where policy requires;
- SH-032/034/037 — request context/redaction/provider failure;
- SH-075 only for any recoverable sensitive value explicitly approved; raw provider tokens should remain in managed secret/provider storage rather than Booking columns.

### Domain Logic

- resolve active consent type/version before provider authorization;
- create/update connection in `pending_consent`/pending provider state as appropriate;
- generate/verify state/nonce;
- request minimal scopes, preferring free/busy-only plus writeback only when required;
- map provider authorization result to canonical statuses;
- set `active` only after provider success + valid consent proof;
- disconnect/revoke stops future sync/writeback;
- no automatic silent reauthorization.

### Authorization / Compliance

- only authorized Professional manages their CalendarConnection;
- ConsentLog remains external proof;
- provider scopes are minimized;
- free/busy privacy intent is explicit;
- raw credentials/tokens are server-only;
- access-mode duplicate schema fields are written through one centralized mapping function, not independently across call sites.

### Database / Transaction Behavior

- connection status/provider status update is owner transaction;
- callback idempotency prevents duplicate connection activation;
- do not make `ConsentLog` mutation directly through Prisma;
- provider references updated only after normalized adapter result.

### Events / Jobs

- optional `calendar.connection_authorized/disconnected/revoked` outbox facts after PR-BC-04 approval;
- no sync worker yet beyond perhaps a one-time connection validation probe.

### Provider Integration

Cronofy adapter must test:

- authorization URL/flow construction;
- state/nonce;
- redirect allowlist;
- normalized account/calendar references;
- revoked/expired/denied/provider-error mapping;
- disconnect/revoke behavior;
- secrets never returned/logged.

### UI / Admin Surface

- connect/disconnect calendar settings;
- source provider selection supported by current adapter/config;
- access mode/scope summary in user-safe terms;
- status/last failure safe message;
- no raw token/provider payload inspector.

### Failure Behavior

- missing/invalid consent → `calendar_consent_required`;
- state/nonce mismatch → security rejection, no connection activation;
- denied provider auth → canonical denied/failed state;
- provider outage → retryable provider error with IntegrationFailure;
- revoked connection → no silent reconnect.

### Tests

- consent version required;
- state/nonce/redirect security;
- scope minimization;
- provider mapping table including unknown result;
- duplicate callback idempotency;
- authorization owner checks;
- secret/log redaction scan;
- provider contract tests with fake adapter and Cronofy test fixture where available.

### Documentation Updates

If access-mode field normalization is approved, update architecture and schema migration notes before changing fields.

### Acceptance Criteria

- active connection requires valid Consent + provider success;
- only Cronofy adapter accesses provider APIs;
- credentials/tokens are absent from client/logs;
- disconnect/revoke behavior is owner-controlled and idempotent.

### Exit Gate

**PASS only if:** connection security/consent/provider contract tests pass and no CalendarConnection can become `active` from client/provider state without Booking owner transition logic.

---

## 07 Free/Busy Synchronization, Calendar Webhooks, and Reconciliation

### Objective

Normalize Cronofy free/busy data into privacy-minimized `BusyWindow` truth and safely process/reconcile provider events without letting provider state become Booking truth.

### Observable Result

External busy intervals appear as BusyWindows and disappear from `listBookableSlots`. A verified provider event is applied once. Duplicate/invalid callbacks have no repeated side effect. Missed/inconsistent provider state can be detected through reconciliation.

### Cluster Build-Plan Link

Completes CL-05 Feature **09**.

### Dependencies

- Features 02 and 06;
- SH-059–062;
- SH-047/048 reliable jobs/retry;
- Cronofy free/busy/webhook support;
- ProcessedCalendarEvent uniqueness.

### In Scope

- `syncCalendarBusyWindows` internal/public owner command as appropriate;
- `applyCalendarProviderEvent`;
- `reconcileCalendarProviderState`;
- BusyWindow upsert/delete/reconciliation;
- ProcessedCalendarEvent owner ledger;
- periodic sync/reconciliation workers;
- slot projection reacts to synchronized windows;
- provider sync health/state.

### Out of Scope

- calendar writeback Booking events (Feature 08);
- raw event descriptions/attendees/locations;
- Booking status transition based solely on provider state;
- Nylas/direct adapters.

### Module-Owned Data

- `BusyWindow`;
- `ProcessedCalendarEvent`;
- CalendarConnection last sync/webhook/provider state;
- Booking external sync fields only when event specifically refers to a Booking writeback later.

### Public Interfaces

- implement `applyCalendarProviderEvent`;
- internal `syncCalendarBusyWindows`;
- implement `reconcileCalendarProviderState`;
- provider webhook route delegates to verification/dedupe/owner command.

### Shared Operations Used

- **SH-059 `verifyProviderWebhookSignature`** — verify raw body before parse/side effect;
- **SH-060 `deduplicateProviderEvent`** — atomically claim provider+event ID into ProcessedCalendarEvent;
- **SH-061 `translateProviderStatus`** — Cronofy mapping stays adapter-local;
- **SH-062 `reconcileProviderState`** — compare and safely repair;
- SH-067 — fetch free/busy/provider state;
- SH-072 — provider payload/version/availability hash where needed;
- SH-044/047/048 — idempotent sync/jobs/retry;
- SH-030 — sensitive access audit where calendar policy requires;
- SH-032/034/037/038/039 — telemetry/failure/queue/health.

### Domain Logic

- only active/authorized CalendarConnections sync;
- fetch minimum free/busy interval data;
- normalize authoritative BusyWindow `startAt/endAt` in UTC;
- store provider IDs/version/hash only for reconciliation;
- assert `freeBusyOnly=true` and `storesPrivateMetadata=false` for free/busy paths;
- never persist descriptions, attendees, private locations, notes;
- provider event claim occurs before BusyWindow/connection mutation;
- duplicate callback returns success/no-op without changing original ProcessedCalendarEvent outcome under PR-BC-05;
- unknown provider event/status fails safe and records IntegrationFailure;
- reconciliation defaults to dry-run/discrepancy detection; auto-repair only approved safe differences.

### Authorization / Compliance

- webhook authenticity is provider security, not User authorization;
- manual sync/reconcile admin actions require SH-002 and step-up if root policy later requires;
- provider scopes/privacy minimization are continuously enforced;
- exact locations from external events are never copied in free/busy mode.

### Database / Transaction Behavior

Provider callback transaction should:

1. claim ProcessedCalendarEvent unique provider+event;
2. lock affected connection/window where necessary;
3. apply deterministic owner update;
4. mark ProcessedCalendarEvent processed/failed;
5. persist outbox fact if owner state change matters externally.

BusyWindow upsert identity/version strategy must be centralized; do not create duplicates from repeated syncs.

### Events / Jobs

- scheduled/triggered busy-window sync;
- provider webhook job if route hands off after secure claim;
- periodic reconciliation;
- `calendar.busy_windows_changed.v1` / `calendar.sync_failed.v1` facts if PR-BC-04 approved;
- dead-letter visible through shared queue telemetry.

### Provider Integration

Test Cronofy adapter free/busy, event normalization, connection revoke/expire, rate limit/outage, and reconciliation calls.

### UI / Admin Surface

- connection last sync/degraded/error state;
- no raw external event inspector for normal users;
- Ops/admin reconciliation discrepancy summary uses safe IDs/statuses only.

### Failure Behavior

- invalid signature → reject before parse;
- duplicate callback → no repeated domain effect;
- provider unavailable → local Booking/availability truth remains, connection may show degraded sync, retry/reconcile;
- revoked auth → transition connection owner state and stop sync;
- malformed/unknown provider payload → safe failure, no guessed mapping;
- missed webhook → reconciliation detects/repairs only if safe.

### Tests

- raw signature rejection;
- unique/deduped provider event replay;
- original ProcessedCalendarEvent state preserved on duplicates;
- free/busy metadata minimization fixture assertions;
- sync add/update/delete BusyWindows;
- slot list changes after sync;
- revoked/expired connection;
- missed webhook reconciliation dry run/repair;
- provider outage/retry/dead-letter;
- privacy/log redaction.

### Documentation Updates

Record finalized BusyWindow provider identity/version/upsert semantics if current schema field meanings become binding.

### Acceptance Criteria

- verified provider events cause at most one owner effect;
- free/busy intervals block slots;
- no unnecessary external event metadata is stored;
- reconciliation can detect a missed/inconsistent state;
- provider outage cannot change a valid Booking’s business status by itself.

### Exit Gate

**PASS only if:** webhook replay/security, free/busy minimization, slot integration, provider failure, and reconciliation tests pass with one semantic effect per provider event.

---

# Phase 5 — Cross-Module Booking Orchestration

## 08 Booking Orchestration, Calendar Writeback, Messaging, Location, Notification, and Video Handoff

### Objective

Reliably turn Booking facts into Booking-owned downstream setup/change requests while preserving every downstream Module’s lifecycle ownership.

### Observable Result

A confirmed/rescheduled/cancelled Booking creates one semantic `BookingOrchestrationRun`. Required steps progress independently. Calendar writeback occurs through Cronofy; Messaging/Notification/Location/Video are called through public interfaces. Partial failures are visible/retryable, and retry does not duplicate downstream effects.

### Cluster Build-Plan Link

- Implements CL-05 Feature **10** for Booking-owned orchestration and calendar writeback.
- Establishes the Booking→Video handoff needed by CL-05 Feature **11**, but does **not** implement Video room/provider/token behavior.

### Dependencies

- Features 04–07;
- SH-049/050 workflow runner;
- SH-113 Messaging;
- SH-041 Notification;
- SH-027 Location Safety;
- Video Session booking-room public command contract/test fake;
- optional Agreement owner command only for an approved post-confirmation use; required pre-confirmation Agreement generation remains out of scope per U-BC-06.

### In Scope

- `startBookingOrchestration`;
- `retryBookingOrchestrationStep`;
- `getBookingDeliverySetupStatus`;
- BookingOrchestrationRun/Step planning/execution/aggregation;
- calendar create/update/cancel writeback via SH-067;
- `ensureContextThread` request;
- Notification request;
- Location Safety evaluation request when workflow requires it;
- Video room provisioning/cancel request through public Video contract only;
- idempotent step semantic keys/correlation;
- authorized admin/system retry;
- external sync state update independent from Booking status.

### Out of Scope

- Thread/Message writes;
- Notification provider/channel implementation;
- LocationReveal direct write/decryption;
- Video provider room/token implementation;
- Agreement generation required before confirmation;
- generic saga/workflow business engine outside SH-049/050.

### Module-Owned Data

- `BookingOrchestrationRun`;
- `BookingOrchestrationStep`;
- Booking external calendar event references and `externalSyncStatus`;
- Booking request timestamps such as videoRoomRequestedAt/confirmationSentAt only as historical request evidence, not downstream truth.

### Public Interfaces

- implement `startBookingOrchestration`;
- implement `retryBookingOrchestrationStep`;
- implement `getBookingDeliverySetupStatus`;
- CalendarProviderPort writeback methods;
- outbound contracts to SH-113/041/027 and Video booking-room command.

### Shared Operations Used

- **SH-049 `orchestrateWorkflowSteps`** — shared runner; Booking owns step graph/truth;
- **SH-050 `reconcileWorkflowStatus`** — deterministic run aggregation; Booking owns partial/critical policy;
- SH-044/047/048 — idempotent durable step execution/retry;
- SH-046 — trigger/outbox facts;
- **SH-067** — Booking-owned calendar writeback;
- **SH-113** — idempotent Messaging Thread;
- **SH-041** — Notification request;
- **SH-027** — Location Safety decision/proof;
- SH-037/038 — IntegrationFailure/queue telemetry;
- SH-031 — BookingEvent remains separate from workflow-step state;
- SH-032/034 — correlation and safe metadata.

### Domain Logic

#### Run identity

Create at most one semantic run per triggering Booking fact/version/action, e.g. confirmed-vN, rescheduled-vN, cancelled-vN.

#### Step planning

Required steps derive from Booking facts/policy:

- `create_calendar_event` / update/cancel writeback;
- `write_busy_window` if Booking local policy requires a Booking-sourced BusyWindow;
- `create_thread`;
- `send_confirmation_notification` or change notification;
- `location_reveal_check` only for approved in-person workflow;
- `create_video_room` only for `locationType=video` through Video owner;
- `generate_agreement` is **not** used for an Agreement required before confirmation unless U-BC-06 is resolved by architecture.

#### Criticality

Booking policy must explicitly mark which step failures make the run `failed` versus `partially_completed`. A notification failure should generally not roll back a confirmed Booking; calendar writeback failure updates external sync state but not core Booking status under PR-BC-02.

#### Idempotency

Every step dispatch carries a stable semantic key. Downstream owner commands must also be idempotent. If canonical SH-044/queue storage cannot durably express per-step identity, resolve U-BC-11 before production.

### Authorization / Compliance

- system worker acts under trusted system context;
- manual retry uses SH-002 and SH-029; SH-014 if root step-up policy requires;
- exact location is not stored in orchestration metadata;
- Thread participants come from authoritative owner facts, not client array;
- Notification variables exclude exact address/tokens/provider secrets;
- Video receives Booking owner facts, not Booking repository access.

### Database / Transaction Behavior

- run creation uses unique idempotency key;
- step transitions use expected status/version;
- no transaction directly spans downstream Module repositories;
- external acknowledgment updates only orchestration step and Booking-owned sync/request snapshot fields;
- `Booking.status` does not change merely because a downstream setup step fails.

### Events / Jobs

- outbox subscriber or explicit start command creates run;
- durable step jobs use shared queue/retry;
- dead-letter terminal step remains visible;
- publish orchestration completed/partial/failed facts if approved;
- calendar writeback result updates external sync fields and may publish `calendar.sync_failed` fact.

### Provider Integration

Calendar writeback only through Cronofy adapter/SH-067:

- create event for confirmed Booking;
- update/move event for reschedule/new Booking as policy requires;
- cancel/remove event for cancelled Booking;
- stable provider request keys;
- safe event description/minimal data.

Video provider integration is **not** in this Module; only Video public command is invoked.

### UI / Admin Surface

- Booking detail “delivery setup” projection;
- step status: pending/running/completed/skipped/retrying/failed;
- safe failure reason/remediation;
- admin/support retry action with authority;
- no raw provider payload/token.

### Failure Behavior

- transient downstream/provider failure → bounded retry;
- business denial → no blind retry; step failed/skipped by explicit policy;
- Notification/Messaging unavailable → no rollback of Booking;
- Calendar writeback unavailable → `externalSyncStatus=failed`/operational evidence, not Booking core failure;
- Video unavailable → Video/setup step failure; Booking remains scheduling truth;
- duplicate run/step trigger → replay/no duplicate downstream effect;
- dead-letter → visible Ops + safe manual retry/reconcile.

### Tests

- run idempotency;
- step graph by Booking location type/action;
- workflow aggregation matrix;
- Messaging/Notification/Location/Video contract tests;
- calendar create/update/cancel adapter tests;
- downstream duplicate-effect prevention;
- partial failure/retry/dead-letter;
- no direct downstream Prisma writes static/integration proof;
- safe metadata/log scan;
- E2E confirmed Booking → orchestration completed with fakes/real available owner interfaces.

### Documentation Updates

- if PR-BC-04 event namespace approved, mark event contracts binding;
- if U-BC-11 requires schema key, update architecture/migration before implementing it;
- do not repurpose `generate_agreement` without U-BC-06 resolution.

### Acceptance Criteria

- one Booking trigger → one semantic orchestration run;
- retries do not duplicate calendar event/thread/notification/video-room request;
- downstream truth remains owner-controlled;
- provider/location secrets absent from workflow metadata;
- Booking remains valid under noncritical setup failure.

### Exit Gate

**PASS only if:** workflow/contract/retry/dead-letter tests pass, direct cross-owner database mutation is absent, calendar writeback is idempotent, and Video/Location/Messaging/Notification are consumed solely through public interfaces.

---

# Phase 6 — Module Integration, Guardrails, and Privacy

## 09 External Decision Bridges and Booking Privacy Executor

### Objective

Prove Booking reacts safely to current external policy/lifecycle decisions and participates in Privacy-owned workflows without creating duplicate guardrail or privacy truth.

### Observable Result

Representative Order/hold/entitlement/privacy changes affect Booking actions through owner interfaces/events. Privacy can inventory Booking/calendar data and execute approved disconnect/erase/anonymize/retain instructions with typed results. No local `PrivacyRequest`, `ComplianceHold`, entitlement, or moderation system exists.

### Cluster Build-Plan Link

- Booking participation in CL-05 Feature **13 — Entitlement Loss, Moderation, Search, Notification, and Hold Bridge Verification**.
- Booking portion of CL-05 Feature **14 — Privacy Target Executors, Retention, and Provider Deletion**.

### Dependencies

- Features 03–08;
- SH-011 current hold decisions;
- SH-025 current Order entitlement;
- SH-005/006 entitlement interface where priority matters;
- SH-045 event consumer dedupe for event-driven owner facts;
- SH-095–097 Privacy protocol;
- Cronofy disconnect/provider deletion support;
- SH-029/030/037 audit/ops.

### In Scope

- representative access/action revalidation for current Order/hold/entitlement before sensitive Booking operations;
- owner event handlers where approved, deduped through SH-045;
- `enumerateBookingSubjectData`;
- `evaluateBookingRetentionRequirement` owner facts;
- `executeBookingPrivacyInstruction`;
- disconnect/delete calendar provider refs/BusyWindows as instructed;
- anonymize or clear permitted Booking personal/location snapshot fields;
- retain only under Privacy-owned exemption reference;
- export-safe Booking contribution if Privacy contract requires it;
- audit/telemetry for destructive actions.

### Out of Scope

- Privacy request identity verification/deadlines/job status;
- retention legal adjudication;
- Moderation/legal decisioning;
- Search projection implementation (no Booking search projection confirmed);
- entitlement plan lifecycle;
- Order refund/dispute adjudication.

### Module-Owned Data

Potentially affected:

- AvailabilityRule;
- CalendarConnection;
- BusyWindow;
- BookingHold/SlotLock;
- Booking personal/timezone/location snapshot fields;
- BookingEvent safe actor metadata;
- ProcessedCalendarEvent target/provider refs;
- Orchestration actor/target/provider refs.

### Public Interfaces

- implement Booking Privacy SH-096 inventory;
- implement SH-097 owner retention facts;
- implement SH-095 owner privacy execution;
- event/command handlers for authoritative external decisions only where architecture approves;
- no broad new public API.

### Shared Operations Used

- SH-005/006 — current priority entitlement/usage semantics;
- SH-011 — current reusable stop sign;
- SH-025 — current Order entitlement where action requires revalidation;
- **SH-045 `deduplicateDomainEvent`** — owner event inbox;
- SH-046 — publish resulting Booking fact when Booking truth changes;
- **SH-095 `executePrivacyInstruction`** — owner execution protocol;
- **SH-096 `enumerateSubjectData`** — inventory;
- **SH-097 `evaluateRetentionRequirement`** — owner facts, Privacy-owned exemption;
- SH-044/047/048 — idempotent/retryable destructive/provider work;
- SH-029/030 — audit/sensitive access;
- SH-037 — provider execution failure.

### Domain Logic

#### External decision handling

- never copy current entitlement/hold/order state into a new generic Booking blocked flag;
- for actions requiring current validation, query the owner at action time;
- event-driven changes may trigger owner-local effects only through explicit mapping;
- duplicate owner events are no-op after inbox claim;
- source decision remains authoritative even if a noncritical downstream notification fails.

#### Privacy inventory

Return stable target records/provider refs, subject relation, sensitivity, supported dispositions, and owner version/cursor.

#### Privacy execution

- revoke/stop access/provider activity before destructive deletion where needed;
- disconnect calendar and remove provider refs under instruction;
- delete external-derived BusyWindows where allowed;
- anonymize retained Booking actor/location metadata to minimum fields where approved;
- preserve relation/integrity for retained Order-linked Booking records;
- return `erased | anonymized | retained | skipped | failed` plus source evidence; do not mark parent Privacy job complete.

### Authorization / Compliance

- only Privacy-authorized system workflow can execute destructive privacy instruction;
- manual retry requires SH-002 and SH-014 if root policy requires;
- retention exception must be Privacy-owned and traceable to proper source basis;
- exact address fields remain blocked by U-BC-07 until Location Safety snapshot contract approved;
- sensitive provider refs not exposed in normal UI.

### Database / Transaction Behavior

- privacy execution is idempotent by target/action ID;
- anonymization/delete transaction preserves required FK integrity;
- provider disconnect/delete can be multi-step durable work; local DB outcome and provider outcome are reconciled safely;
- retained records are not deleted merely because a user relation is being erased.

### Events / Jobs

- owner event inbox/dedupe for approved external decisions;
- privacy provider deletion/disconnect job;
- reconciliation after provider deletion failure;
- audit/IntegrationFailure;
- no Search request unless a future Booking-owned public projection is explicitly introduced.

### Provider Integration

- Cronofy disconnect/delete provider reference where supported;
- already-absent provider resource is idempotent success semantics;
- provider outage returns retryable Privacy target result; Privacy parent remains owner of partial completion.

### UI / Admin Surface

No standalone Booking privacy UI. Privacy/admin tooling consumes typed result. Booking may expose a safe debug executor trace only under authorized admin tooling.

### Failure Behavior

- retention required → `retained` with source reason reference, no silent delete;
- provider unavailable → retryable failure/partial target, not fake success;
- duplicate privacy instruction → same semantic result;
- owner event duplicate → no repeated Booking effect;
- unknown external decision → no guessed transition; record failure/manual review.

### Tests

- subject-data inventory completeness;
- calendar disconnect/provider ref deletion;
- BusyWindow deletion;
- anonymize retained Booking fixture;
- retention exemption contract;
- duplicate destructive instruction;
- provider absent/outage/retry;
- external owner event dedupe;
- ComplianceHold current-action denial;
- no local privacy/hold/entitlement tables/static checks;
- E2E Privacy harness → Booking executor result.

### Documentation Updates

Update retention field map only when approved legal/owner facts are known. Any new moderation/search effect requires architecture update first.

### Acceptance Criteria

- Privacy can enumerate and execute Booking-owned targets through typed protocol;
- retention remains Privacy-owned;
- provider deletion/disconnect is idempotent/retryable;
- current guardrail decisions are consumed, not copied;
- no new local generic blocked/privacy truth exists.

### Exit Gate

**PASS only if:** privacy integration tests and external-decision dedupe/hold revalidation tests pass, provider deletion failures are observable/retryable, and a schema scan confirms no Booking-local PrivacyRequest/ComplianceHold/entitlement substitute was added.

---

# Phase 7 — Module Hardening and Production Verification

## 10 Booking Production Hardening, Reconciliation, Security, and Performance

### Objective

Harden Booking & Calendar under concurrency, retries, provider degradation, stale state, reconciliation, privacy/security boundaries, and realistic load without expanding product scope.

### Observable Result

The scheduling subsystem remains deterministic under parallel reservations/transitions, Cronofy outages/missed callbacks, duplicate webhooks, queue retries/dead letters, privacy deletion races, and downstream service failures. Operators can see safe health/reconciliation state and perform authorized retry without provider state becoming business truth.

### Cluster Build-Plan Link

Booking portion of CL-05 Feature **15 — Provider Reconciliation, Security, Concurrency, Audit, Performance, and Production Readiness**.

### Dependencies

- Features 01–09;
- production Cronofy config;
- root security/step-up policy finalized enough for sensitive Booking actions;
- real shared Ops/queue/outbox/audit infrastructure;
- realistic seeded data and migration pipelines;
- Video/Messaging/Notification/Location contracts available for integrated failure testing where launch-critical.

### In Scope

- load/concurrency tuning for slot search/locking/Booking transitions;
- Cronofy reconciliation scheduled/admin dry-run + safe repair;
- provider outage/circuit/rate-limit behavior;
- webhook security/replay testing;
- orchestration dead-letter/replay safety;
- secret/log/telemetry redaction audit;
- authorization/RLS alignment;
- expiration sweep performance;
- index/query tuning;
- migration-from-clean and migration-on-realistic-seed tests;
- privacy/retention destructive-race testing;
- safe Ops health/reconciliation views;
- finalize all launch-blocking unresolved Booking decisions or explicitly feature-flag blocked behavior out of launch.

### Out of Scope

- new calendar providers for redundancy;
- a generic incident-management UI;
- JobInterview scheduling consolidation;
- new pricing/payment/refund policies;
- new location/privacy legal policy;
- converting Booking into a general scheduling platform.

### Module-Owned Data

Tune/review existing Booking-owned tables only. Any new column/table must have explicit owner/architecture justification.

Priority review:

- BookingSlotLock overlap/exclusion constraint and active-state predicate;
- Hold/Lock expiry indexes;
- Booking professional/date/status indexes;
- ProcessedCalendarEvent unique/status/date indexes;
- CalendarConnection provider/status indexes;
- BusyWindow professional/date indexes;
- Orchestration run/step status indexes;
- destructive cascade behavior;
- safe data retention/anonymization relationships.

### Public Interfaces

No broad new surface by default. Harden existing contracts plus:

- authorized reconciliation dry-run/repair command;
- health/readiness check registration;
- safe operational read model;
- authorized dead-letter/manual retry hooks through shared Ops framework.

### Shared Operations Used

Emphasize:

- SH-014 where approved sensitive actions require step-up;
- SH-032–039 telemetry/health/failure;
- SH-044–053 idempotency/event/queue/locking/lifecycle;
- SH-055/056/058 expiration/atomic reservation/interval locking;
- SH-059–062 provider security/dedupe/translation/reconciliation;
- SH-072/075 security primitives where applicable;
- SH-095–097 privacy protocol;
- SH-029/030 audit/sensitive evidence.

No hardening task may create Booking-local copies of these mechanisms.

### Domain Logic

- every time-sensitive action validates server clock at request time;
- reconciliation repairs only approved safe differences;
- unknown provider discrepancies require manual review rather than provider-truth overwrite;
- no current access/action decision relies solely on stale entitlement snapshot when current validation is required;
- Booking core state remains independent of external calendar availability;
- dead-letter replay must be semantically idempotent;
- rate limits protect slot/hold/calendar endpoints without turning rate-limit state into Booking truth.

### Authorization / Compliance

Security review verifies:

- least-privilege provider scopes;
- secret rotation/provider credential lifecycle;
- SH-002 and RLS/server authorization consistency;
- root step-up matrix implementation;
- exact-location boundary/feature flag;
- free/busy minimization;
- audit coverage;
- privacy executor coverage;
- ComplianceHold current action coverage;
- telemetry redaction.

### Database / Transaction Behavior

- benchmark overlap transactions under realistic parallel load;
- verify deadlock handling/retry semantics;
- validate optimistic conflict behavior for Booking transitions;
- confirm no lock is held across external network calls;
- test expiration queries/indexes with realistic volume;
- verify all unique/idempotency constraints on clean and seeded migrations;
- destructive privacy migrations/cascades reviewed against retention.

### Events / Jobs

Production schedule/worker readiness for:

- Hold/SlotLock expiration;
- free/busy sync;
- provider webhook work;
- Booking orchestration;
- calendar reconciliation;
- Privacy provider execution/retry;
- queue dead-letter visibility.

### Provider Integration

Cronofy production verification:

- credentials/scopes;
- rate limits/backoff;
- webhook signature/timestamp tolerance;
- duplicate/missed event behavior;
- provider says missing while local connection/event exists;
- provider has event while local Booking cancelled/deleted;
- dry-run reconciliation and safe repair;
- provider outage does not corrupt Booking core state.

### UI / Admin Surface

- safe calendar/provider health summary integrated with Ops;
- reconciliation discrepancy dry-run view;
- authorized retry link/action;
- no raw secrets/event payload dumping.

### Failure Behavior

Explicitly verify:

- provider unavailable vs degraded vs delayed;
- missed/duplicate webhook;
- local/provider divergence;
- concurrent hold/confirm/expire;
- concurrent cancel/reschedule/complete;
- downstream Notification/Messaging/Video unavailable;
- queue retry exhaustion;
- privacy target partially failed;
- reconciliation unsafe discrepancy requiring manual review;
- stale actor/entitlement/hold state.

### Tests

- load tests for slot search and interval lock;
- parallel reservation/confirmation/transition tests;
- authorization/RLS matrix;
- webhook replay/security/fuzz fixtures;
- provider chaos/degradation adapter tests;
- reconciliation dry-run/repair;
- queue dead-letter replay;
- secret/token/URL/log scan;
- privacy destructive/race/retention tests;
- audit completeness matrix;
- E2E critical journeys under provider retry/failure;
- clean migration + realistic seeded migration;
- full typecheck/lint/unit/integration/contract/provider/privacy/concurrency/E2E/build suite.

### Documentation Updates

Before production readiness, all launch-blocking unresolved decisions must be either:

- resolved and reflected in `module-architecture.md`, CL-05/root context as needed; or
- explicitly feature-flagged out of launch with safe behavior documented.

Update provider docs/runbooks and progress tracker with reconciliation/manual-retry procedures.

### Acceptance Criteria

- database overlap invariant passes parallel load;
- duplicate webhook/command/job results in one semantic effect;
- Cronofy reconciliation can detect and safely repair approved discrepancies;
- provider outage does not become Booking business status;
- privacy/retention flows pass end-to-end;
- sensitive data/secrets absent from logs/telemetry;
- authorization/audit coverage is complete for launch matrix;
- dead letters and provider failures are visible/recoverable;
- launch-blocking unresolved decisions are closed or safely disabled.

### Exit Gate

**PASS only if all are true:**

- clean + seeded migrations pass;
- typecheck/lint/unit/integration/contract/provider/privacy/concurrency/E2E/build pass;
- slot overlap test passes under parallel load;
- webhook replay produces one business effect;
- orchestration replay cannot duplicate downstream semantic effects;
- Cronofy missed/inconsistent state is reconcilable;
- secret/log scan is clean;
- privacy executor and retention paths pass;
- audit/ops/dead-letter visibility is proven;
- no unresolved decision required for launch remains silently implemented.

---

# Module Integration Phase Summary

The integration burden for Booking & Calendar is intentionally spread across owner features rather than implemented as one cross-domain service:

| Integration | Proven in Module feature | Owner boundary proved |
| --- | --- | --- |
| CustomerProfile + Track Entitlement | 03 | customer/priority truth remains external |
| Order + Agreement + ComplianceHold | 04–05 | Booking confirms only after owner gates |
| Cronofy | 06–08 | provider rail remains Booking-owned adapter, not Booking truth |
| Messaging | 08 | Thread created through SH-113, not Booking repository |
| Notification | 08 | delivery requested through SH-041 |
| Location Safety | 08 | exact reveal remains Location owner |
| Video Session | 08 | Booking requests room; Video implements Feature 11 |
| External guardrail events | 09 | owner decision consumed/deduped, no local blocked truth |
| Privacy | 09 | Booking executes owner targets; Privacy owns orchestration |
| Audit/Ops | all, hardened in 10 | evidence/ops remains separate from BookingEvent/source truth |

A cross-Module integration test must fail if the Booking service reaches directly into a neighboring Module repository where a public interface exists.

---

# Module Hardening Phase Summary

Feature 10 is not a catch-all feature for unfinished product scope. It exists only to harden already-proven Booking behavior:

- concurrency and transaction races;
- command/event/job replay;
- Cronofy outage/reconciliation;
- webhook security;
- secret/sensitive telemetry safety;
- privacy/retention execution;
- authorization/RLS alignment;
- audit completeness;
- query/index performance;
- migration safety;
- operator recovery through shared Ops tooling.

Any new business behavior discovered during hardening must return to architecture/plan rather than being hidden inside “hardening.”

---

# Phase Summary

| Phase | Name | Features |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | **01** Booking Contracts, Schema Readiness, and Owner Boundary; **02** Professional Availability and Bookable Slot Projection |
| 2 | Atomic Reservation | **03** Atomic BookingHold and BookingSlotLock |
| 3 | Booking Lifecycle | **04** Order-Gated Booking Confirmation; **05** Cancellation, Reschedule, Completion, and No-Show |
| 4 | Calendar Provider Boundary | **06** Calendar Connection, Consent, and Provider Authorization; **07** Free/Busy Synchronization, Calendar Webhooks, and Reconciliation |
| 5 | Cross-Module Booking Orchestration | **08** Booking Orchestration, Calendar Writeback, Messaging, Location, Notification, and Video Handoff |
| 6 | Module Integration, Guardrails, and Privacy | **09** External Decision Bridges and Booking Privacy Executor |
| 7 | Module Hardening and Production Verification | **10** Booking Production Hardening, Reconciliation, Security, and Performance |

**Total numbered Module features: 10.**

### Cluster sequencing correspondence

```text
Module 01–03 → CL-05 Feature 07
Module 04–05 → CL-05 Feature 08
Module 06–07 → CL-05 Feature 09
Module 08    → CL-05 Feature 10 (+ Booking-side handoff for Feature 11)
Module 09    → CL-05 Features 13–14 Booking participation
Module 10    → CL-05 Feature 15 Booking hardening
```

This mapping is a decomposition of Cluster work, not a replacement for Cluster sequence.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root Project Overview.
2. Read root architecture/build plan/code standards.
3. Read Canonical Shared Operations Registry.
4. Read CL-05 architecture and build plan.
5. Read this Module architecture and implementation plan.
6. Read public-interface sections for direct dependencies used by the feature.
7. Read current progress tracker and previous completion report.
8. Confirm the prior feature exit gate passed or an explicit approved exception exists.
9. Check Module unresolved decisions for feature blockers.
10. Write the concise implementation specification for **only this feature**.
11. Confirm schema/migration state, permissions, SH-### dependencies, provider ports, transaction boundaries, and failure semantics.
12. Implement only the numbered feature.
13. Run required type/lint/unit/integration/contract/concurrency/provider/E2E checks applicable to the feature.
14. Verify the complete happy + denial + retry/idempotency workflow.
15. Update progress.
16. Update architecture only when a binding decision legitimately changed.
17. Record assumptions, known failures, unresolved risks, and deferred work.

Do not start adjacent “helpful” features simply because files are nearby.

---

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise implementation specification containing:

- **Objective** — the one result this feature must achieve.
- **Observable result** — what a user/test/consumer can prove after completion.
- **Dependencies** — prior Module features, owner public interfaces, shared operations, schemas, providers.
- **In scope** — exact work allowed.
- **Out of scope** — neighboring responsibilities prohibited.
- **Owned data affected** — Booking-owned models/enums/events/snapshots.
- **Public contracts** — commands/queries/events/executor changes.
- **Shared operations consumed** — SH IDs, invocation point, local policy, prohibited duplicate.
- **Permissions/compliance** — actor, authority, CustomerProfile, Order, Agreement, Consent, Entitlement, Hold, Location, Healthcare, Privacy as applicable.
- **Primary workflow** — step-by-step source truth transformation.
- **Provider integration** — port/adapter calls, only when relevant.
- **Jobs/events** — outbox/inbox/worker/retry/dead-letter/correlation.
- **Idempotency/concurrency** — semantic key, lock/constraint/version, replay result.
- **Error behavior** — stable reason codes, retryability, conflict behavior.
- **Tests** — exact unit/integration/contract/provider/concurrency/privacy/E2E scope.
- **Acceptance criteria** — observable requirements.
- **Documentation updates** — context/progress/ADR/shared-op changes if decisions changed.

Do not generate implementation specifications for all future features in advance. The numbered plan supplies guardrails; the implementation specification resolves immediate file-level execution when that feature begins.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed:** number and name.
- **Files added.**
- **Files changed.**
- **Database changes.**
- **Migrations / constraints added or modified.**
- **Dependencies added.**
- **Module public interfaces added/changed.**
- **Dependency Module contracts consumed.**
- **Shared operations reused, by SH-### ID.**
- **Events/outbox/inbox handlers added.**
- **Jobs/workers/schedules added.**
- **Provider port/adapter changes.**
- **UI/admin/debug surface changes.**
- **Tests added/changed.**
- **Commands run.**
- **Manual/contract/workflow verification performed.**
- **Authorization/compliance/privacy/security verification.**
- **Documentation/progress updated.**
- **Assumptions.**
- **Known failures.**
- **Remaining risks.**
- **Unresolved decisions encountered.**
- **Deferred work.**
- **Exit-gate result:** `PASS` or `FAIL`, with every failed criterion named.

A feature is not complete because its happy path works. A failed exit gate means the feature remains incomplete unless the progress tracker contains an explicit architecture-approved exception.

---

# Final Quality Check

Before declaring the Booking & Calendar Module implementation complete, verify:

1. `Booking`, `BookingHold`, `BookingSlotLock`, CalendarConnection/BusyWindow, BookingEvent, ProcessedCalendarEvent, and Booking orchestration each have exactly one owner.
2. No Order/payment/Agreement/Video/Messaging/Notification/Location/Consent/Entitlement/Hold/Privacy truth was absorbed.
3. Every canonical shared operation is consumed rather than duplicated.
4. Shared interval locking, lifecycle plumbing, provider dedupe, workflow runner, audit, queue, privacy, and snapshot mechanisms preserve separate Booking truth.
5. Commands/queries have clear Booking ownership and stable contracts.
6. Cross-Module reads use owner interfaces, not foreign repositories.
7. Cronofy payloads terminate at the adapter and never become Booking business types.
8. BookingEvent, AuditEvent/AccessAuditLog, ProcessedCalendarEvent, and IntegrationFailure remain distinct.
9. Privacy orchestration remains Privacy-owned.
10. No Booking Search/Typesense projection was invented.
11. Standard pre-confirmation flow uses Hold/SlotLock and creates Booking only after Order/Agreement gates.
12. Slot contention is enforced in PostgreSQL, not process memory.
13. Every external effect is idempotent/reconcilable.
14. Provider writeback failure does not silently redefine Booking business status.
15. Free/busy storage contains no unnecessary external event metadata.
16. Exact-location behavior remains disabled/guarded until the Location Safety snapshot contract is approved.
17. Every numbered feature has automated tests and an exit-gate result.
18. Module feature order remains aligned to CL-05 Feature 07→08→09→10→13/14→15.
19. Launch-blocking unresolved decisions are resolved or safely feature-flagged out.
20. A coding agent can implement the next feature without inventing ownership, provider, transaction, or shared-operation architecture.
