> Current review pointer (2026-10-15): `bridge-review-domain.md/json` records seven prioritized domain families under R077–R080; 183 domain families and rail integration remain. The historical five-bridge slice below is not the final 563-record inventory.

# Cross-cluster bridge inventory — partial adjudicated slice

2026-09-29. **IN PROGRESS, not the final Gate 4 inventory.** These records capture the newly approved P01–P03 boundaries and keep schema/implementation requirements distinct from product decisions. Remaining historical bridge records and rail matrices are not yet fully adjudicated. No parallel lane is activated.

The canonical owner architecture/plan paths are indexed in context/context-map.md; WA-R011–013 are applied to both endpoints and their Clusters. Interface descriptions below are semantic contracts, not newly registered SH identities or claims that executable DTOs already exist.

| ID | Producer → consumer | Purpose / source truth | Boundary / contract | Sequence | Parallel status |
|---|---|---|---|---|---|
| BR-PO-01 | CL-01 Track → CL-05 Booking | Early-access eligibility; Track owns commercial benefit, Booking owns availability release time | QUERY / SH-005, evaluatePriorityScheduling, WA-R011 | FOUNDATION_CAPABILITY: effective benefit resolver, then Booking enforcement | UNSTABLE until concrete DTO, release policy storage and bilateral fixtures are verified; product meaning resolved |
| BR-PO-02 | CL-03 Supply → CL-04 Order | Explicit package session count/terms; Supply source, immutable Order purchase snapshot | DATA_FACTS / chargeable source quote into SH-107, WA-R012 | CONTRACT_ONLY for contract work; live sale requires validated source and Order persistence | UNSTABLE pending versioned quote schema and purchase-validation fixtures |
| BR-PO-03 | CL-04 Order → CL-05 Booking | Bounded purchased-session authorization; Order owns allowance/reservations | COMMAND + QUERY / Order session reservation/reconciliation interface, WA-R012 | FOUNDATION_CAPABILITY: durable Order authorization before paid Booking conversion | UNSTABLE pending atomic constraints, typed results and recovery fixtures |
| BR-PO-04 | CL-05 Booking → CL-04 Order | Session attachment/outcome; Booking owns appointment lifecycle | BACKGROUND_WORKFLOW / idempotent acknowledgment and authoritative Booking outcome, WA-R012 | CONTRACT_ONLY to design; real recovery requires both owner persistence paths | UNSTABLE pending acknowledgment/outcome payload, delivery and compensation tests |
| BR-PO-05 | CL-06 Hiring → CL-02 Search | Explicit work-arrangement filter values; Hiring owns Job source | PROJECTION / SH-094 + SH-091, WA-R013 | CONTRACT_ONLY for projection fixtures; real indexing after schema/source clarification | UNSTABLE pending projection version, index mapping and stale-value removal tests |

## Endpoint obligations, failure and security

**BR-PO-01.** Track provides Customer-track subject, eligibility, grant/policy evidence, evaluation and expiry; Booking checks server-side release instants, normal eligibility and interval conflicts. No benefit consumption or priority queue is implied. Unavailable evidence denies early access, not ordinary access after general release. Persist minimal evidence on a hold and recheck normal conversion gates. Do not expose subscription/provider details in public availability responses. Test release boundaries, direct-command bypass, expiry and concurrent claims.

**BR-PO-02.** Supply exposes a positive bounded session count only for a package that actually sells those sessions. Order validates and snapshots count, source/version and applicable terms. Missing/ambiguous terms cannot create an unbounded package. Later source edits do not rewrite the purchase. Read only an authorized source quote; never copy private seller/provider data wholesale. Test explicit four-session and single-session purchases, missing count, source edit and replay.

**BR-PO-03.** Order allocates one durable session identity per permitted unit with idempotent command identity; result distinguishes authorized/exhausted/denied/unavailable. Booking binds it to one conversion intent. Missing/unknown result cannot authorize scheduling. Order rechecks source-specific readiness at the action boundary; caller credentials alone cannot reserve another buyer's purchase. Atomic bound/uniqueness tests must reject a concurrent fifth authorization for a four-session package.

**BR-PO-04.** Booking atomically persists its local conversion/outbox and sends durable attachment/outcome evidence. Order reconciles unknown outcomes by querying Booking's durable result; a timeout alone cannot release a reservation. Rescheduling retains session identity; cancellation/refund does not restore allowance by default. Completion of one session does not imply completion of the entire Order. Each owner validates counterpart identity, correlation, source version and duplicate semantics without foreign Prisma reads. Test crash points, duplicate delivery, reschedule and partial fulfillment; apply snapshotted terms for financial effects.

**BR-PO-05.** Hiring emits distinct fixed-term employment and independent-contractor concepts and a source version. Search projects those safe facts, removes stale representations and offers distinct filters. Ambiguous legacy contract is not silently remapped; owner clarification precedes affected republication. Legal worker classification remains Job Compliance's approved rule evaluation, not a Search inference. Test source correction, projection replay, stale contract removal and no title-based guessing. Job Compliance is an intra-CL-06 consumer of the same explicit input; both owner architectures carry WA-R013.

## Remaining qualification

All five are architecture-aligned in their stated product meaning, but none is FROZEN_FOR_IMPLEMENTATION yet. Database provenance remains the existing scoped Gate 6 evidence requirement. Complete the rest of Gate 1/2, then consolidate all bridges and the CL-01/07/08/09 rail matrices; do not treat this bounded slice as platform-wide symmetry proof.
