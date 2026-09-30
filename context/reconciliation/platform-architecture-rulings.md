# Platform architecture rulings

Status: **IN PROGRESS — not Gate 2 completion**. Date: 2026-09-29.
Evidence baseline: `526bb1ab30480d66ca8b7da08d16badc6e613c1d` (`main`).

Authority follows `context/context-map.md`. These rulings record explicit applications to named concerns; neither this ledger nor the historical handoffs replaces owner architecture. Unlisted handoff decisions remain unadjudicated. No product implementation or contract freeze is implied.

## WA-R001 — Organization membership and permission interpretation

- Class: **AI_RESOLVED**; finding: stale ownership/status references.
- Decision: Organization Hiring owns `OrganizationMember` and the assigned `OrganizationRole` lifecycle/vocabulary; Messaging owns `ThreadParticipant`; Role interprets owner facts and does not mutate these lifecycles.
- Evidence: canonical SH-002; Organization Hiring architecture §1, §8.2 and membership commands; Role architecture ownership boundary; refresh report C01; prior CL-06-R001 / CL-07-R017.
- Applied: remove OrganizationMember/OrganizationRole from Role's owned-schema registry array and retain references; confirm PR-CL01-02 in CL-01/Role architecture; close U-CL01-11's ownership question.
- Duplicate collapse: CL-01 PR-CL01-02, U-CL01-11, refresh C01 ownership portion. SH-003 universal DTO status is unchanged; owner-specific contracts still require concrete agreement.
- Not changed: model structure, permissions assigned to any actor, Module identity/membership, historical glossary source. The glossary's older ownership lists remain evidence, not approval to reverse this reconciled lifecycle split.

## WA-R002 — Commercial reward grants

- Class: **AI_RESOLVED** by existing product-owner adjudication; finding: stale SH-119 owner/status.
- Decision: Track owns SH-119 and authoritative commercial grants. Gamification owns earning/redemption; affected features apply Track-resolved benefits. Each reward specifies duration extension, quota increase, separate scope, or no additional effect for equivalent benefits. No automatic stacking, base-plan rewrite, local premium state, or sweepstakes odds benefit.
- Evidence: canonical SH-119 and “Adjudicated Product and Ownership Rules”; Track architecture §15; Gamification architecture §15 and U-GR-10; CL-10 U-CL10-06; refresh C27/H04 are superseded on this matter.
- Applied: Track, Gamification, CL-10 architecture and plans now reference the confirmed owner. Old ownership approval gates become execution-contract prerequisites.
- Duplicate collapse: U-CL10-06, U-GR-10, CL01-HU-023, CL03-HD085 and historical refresh C27/H04 **only as to grant ownership and approved commercial-benefit policy**. Broader reward-type fulfillment remains open where no supported effect exists.
- Remaining: bilateral grant/effect/replay/compensation contracts; activation of specific unsupported reward types. These are not a reopened product-owner question about whether rewards can grant benefits.

## WA-R003 — Screening is an approved Order source family

- Class: **AI_RESOLVED** by existing product-owner adjudication; finding: actual stale exclusion in Order architecture.
- Decision: exactly one conceptual source family per Order: seller-backed Offering, seller-backed accepted GigAssignment, or platform-facilitated screening service. Screening uses a Trust-owned package/quote and no Professional seller. Trust owns screening, Order owns transaction truth, Payment owns processor execution. Payment does not prove clearance.
- Evidence: canonical SH-107 and adjudicated screening rules; Trust architecture paid-screening inputs/§15 and Order's old CL-04-R008 source invariant.
- Applied: amend CL-04-R008's marketplace-only scope in Order and CL-04 architecture; add screening source, prerequisite and exit-test sections to Order/Cluster plans and Trust pair. Do not manufacture schema fields or claim migration completion.
- Duplicate collapse: refresh C23/H05 screening source/payer portion; Trust-to-Order bridge expectations and older marketplace-only Order-source exclusions. Voluntary Candidate/Professional screening is self-initiated/self-paid; other sponsorship remains a separately approved workflow.
- Remaining: source-specific representation/constraints, frozen quote contract, paid-result correlation, replay/refund/recovery behavior, legal/provider gates. Existing Prisma has only offering/gig_assignment; paid-screening activation remains blocked until the representation is implemented and verified.

## Preserved decisions that must not be reopened

The canonical registry already establishes Organization ATS as a separate commercial lane (Free/Plus/Pro placeholders), content similarity as optional after launch, contextual Consent, device biometrics without raw biometric storage, and Location's active-service-only reveal policy. The old refresh report's H04–H08 are not current product questions. Exact ATS configuration and owner-specific technical work remain scoped prerequisites.

## Remaining adjudication

All 10 handoffs remain evidence indexes. Rulings above close only their named portions. Do not bulk-label remaining records “implementation detail” merely because their text mentions a schema/DTO. A missing producer, lifecycle graph, permission decision, or source owner can be architectural. Review both owner and consumer before classifying or freezing.

## WA-R004 — Content similarity scope

Class: **AI_RESOLVED** by existing product adjudication. Canonical SH-106 is Proposed ruling and optional after launch; SH-086 owns exact-byte checksum integrity. Launch uses report-driven Moderation / Legal Notice. CL-09 architecture and Moderation's SH table now reflect that scope/status. Final adapter ownership, provider, thresholds and persistence remain later technical/provider gates. Duplicate collapse: CL-09 U-08 / CL-09-D007 and refresh C22/H08 as to product launch scope only. No automatic infringement/enforcement inference is allowed.

## WA-R005 — Separate Organization ATS lane

Class: **AI_RESOLVED** by canonical adjudicated product rules. Organization ATS is a separate Organization-scoped commercial lane with Free/Plus/Pro placeholders; it is not a fourth User AccountTrack. Track owns commercial policy; Hiring owns Organization/hiring truth. CL-01 and Track architecture now close U-CL01-33's product-model question. Organization-scoped persistence, billing, exact limits/prices and feature allocation remain deferred prerequisites; do not infer paid/free status from absent billing or local flags. This does not certify all Hiring/Search consumer contracts as aligned.

## WA-R006 — Search reads Location; consumers do not call Agreement internals

Class: **AI_RESOLVED**, STALE_REFERENCE. SH-028 produces/invalidates fuzzy public projections; SH-131 is the side-effect-free read. Updated all CL-02 Search/Cluster architecture and plan references at their read sites. Source generation remains Location-owned, and no read-triggered recursion or exact fallback is permitted. Evidence: canonical SH-028/131, Location architecture public contracts, Search's prior SH-028 dependency tables, refresh C09; duplicate collapse CL-02 D055 and the corresponding CL-08/CL-05 read/generate ambiguity, only as to boundary identity. Freshness/schema completion remains a bounded technical prerequisite.

Also corrected CL-05's Agreement bridge: consumers call Order's public readiness/access interfaces; SH-112 remains internal/background integrity verification. This closes the public-exposure ambiguity in CL-05-U058, not any missing consumer DTO.

## WA-R007 — Remove competing contextual attachment ownership claims

Class: **AI_RESOLVED**, STALE_REFERENCE. Removed Media's duplicate owned claims for OfferingMedia, GigMedia, OrganizationMedia and CandidateProfileMedia and retained them as references. Existing contextual owners stay Marketplace Supply, Gig Demand, Organization Hiring and Candidate Application. Evidence: Media architecture §3.2 / MFA-PR-01, SH-090 and the corresponding registry owner entries. Prisma placement and runtime code are unchanged. ProfessionalProfileMedia and MessageMedia already have their contextual owners and need no registry move. ProfileStatus is shared vocabulary, not a shared lifecycle: each profile owner keeps its own transition policy; one coordinated schema steward handles enum changes.

## WA-R008 — Public file-access consumers use the composite Media boundary

Class: **AI_RESOLVED**, STALE_REFERENCE / MISSING_CONTRACT distinction. Order Agreement retrieval, Candidate resume access, and Privacy export delivery now name SH-127 `requestMediaAccess` in their architecture and plan call sites. SH-087 remains Media-internal. Context owners authorize business access; Media independently gates readiness/grants/expiry/revocation and produces bounded credentials/proof. No new signer or blanket grant is introduced.

Evidence: Media `requestMediaAccess` public contract, canonical SH-026/087/127, existing bilateral Messaging/Digital Goods access rulings, and direct signing references in the three consuming pairs. Duplicate collapse: refresh C08 and CL-05-U059 public-wrapper identity. Exact caller bindings/access-log meanings remain technical requirements; legal meaning of access remains a separate external/product question. SH-127 is not promoted to Confirmed by replacing a stale call name.

### WA-R008 additional consumer application

Applied the same public-access correction to remaining external protected-file consumers (Customer, Supply, Gig, Review/Dispute, Trust, Healthcare, Payment and CL-08 composition) while retaining explicit Media-internal/transitive signing references. Media deletion is a separate owner contract, not a signing side effect. Existing CL-05/Digital Goods/Messaging descriptions that already invoke signing inside the composite remain valid.

## WA-R009 — Jurisdiction is shared normalization, separate policy

Class: **AI_RESOLVED**, STALE_REFERENCE. Canonical SH-120 is Proposed ruling with per-purpose owner interpretation, not an Unresolved universal jurisdiction authority. Aligned CL-03/CL-06 consumer references and added explicit owner-binding gates. Evidence: canonical SH-120; refresh C17 as superseded by final adjudication; Payment/Job Compliance jurisdiction dependency and unresolved sections. Legal facts/provider capabilities remain EXTERNAL_REQUIREMENT; exact DTO/representation is DEFERRED_IMPLEMENTATION_DETAIL after source evidence and purpose are bound. This closes only stale identity/ownership/status, not legal applicability.

## WA-R010 — CompensationPeriod belongs to the Job fact owner

Class: **AI_RESOLVED** for structural vocabulary stewardship, independently of the product meaning of `EmploymentType.contract`. Adopt PR-JC-03: Organization Hiring owns CompensationPeriod; Job Compliance consumes/snapshots it. Registry and CL-06/Hiring/Compliance pairs now state this split. No enum values or database columns changed.

Evidence: Job Compliance architecture §3 and U-CL06-07/PR-JC-03; Hiring Job-source truth; Prisma Job compensation fields; glossary controlled-vocabulary entries. Duplicate collapse: CL-06-U007 and U-CL06-07 ownership portion. **P03** retains the genuinely different product interpretations of `contract`; selecting storage or enum ownership cannot decide that meaning.


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

## WA-R013 — Explicit work arrangements (P03)

Product-owner ruling approved 2026-09-29: distinguish **fixed-term employment** and **independent-contractor work** as separate canonical concepts. A generic CONTRACT/contract value must not hide the distinction. This closes the product-meaning portion of U-CL06-07 / CL-06-U007. WA-R010 already assigns CompensationPeriod stewardship to Organization Hiring.

Hiring owns the work-arrangement vocabulary and source selection. The canonical concepts are FIXED_TERM_EMPLOYMENT and INDEPENDENT_CONTRACTOR; exact persisted enum spelling follows schema conventions in the coordinated database pass. Job Compliance consumes the explicit arrangement, preserves it in evaluated input/rule evidence and applies the relevant approved rule set. A selected label is not a legal determination of worker classification. Applicable jurisdictional legal rules remain an external gate.

Search projects the explicit owner-provided concepts and presents distinct filters/labels; it cannot derive them from job title, compensation period, or old contract text. Legacy EmploymentType.contract is ambiguous: preserve historical value, require authorized source clarification before affected republication/re-evaluation, and do not silently map every old row to either new concept. Reindex only after owner correction. Existing unambiguous employment types remain unchanged. Organization contractor Jobs remain Hiring work, not automatically Gigs or Offerings.

Implementation acceptance: distinct create/edit/publication and query/filter paths; exact compliance input and evidence for each concept; ambiguous historical rows blocked from new publication until clarified; no mass inferred backfill; no legal conclusion based only on employer-selected label. Prisma's present enum is implementation reality, not evidence that this ruling has been migrated.

Classification for WA-R011–013: **PRODUCT_OWNER_CHOICE — RESOLVED by explicit owner approval**, with AI_RESOLVED technical enforcement and recovery details as stated. Historical duplicate IDs remain readable in handoffs; their product-choice labels no longer govern. Applied to both owner pairs and their Cluster pairs; WA-R012 also Supply/Order, WA-R013 also Search. No schema edit or activation is implied.


## WA-R014 — Point ledger arithmetic and historical causation

Class: **AI_RESOLVED** for signed-delta convention, durable causation, reversal linkage and acceptance proof. Does not select spend scope (P04), expiration policy (P05), reward effect or compensation policy.

Gamification owns an append-only signed point ledger. `earned` is strictly positive; `spent` and an authorized `expired` entry are strictly negative; `adjusted` is a nonzero signed delta with authorized reason/evidence. A `reversed` entry refers to one original entry in the same approved account and has exactly its opposite signed value. Ordinary reversal is full, at most once per original, and cannot target another reversal. Partial corrections use an explicitly authorized adjustment with causation rather than pretending to be a full reversal. No zero-value ledger rows or mutation of an original amount. This closes U-GR-02 and the linkage/double-reversal portion of U-GR-04; downstream compensation and insufficiency behavior remain U-GR-16 and cannot be guessed from these signs.

Every award binds the owner source-event identity/version, beneficiary, rule identity and immutable effective rule version (including exact evaluated rule content/hash), evaluation time and semantic effect key. Duplicate delivery through SH-045 or repeated commands through SH-044 cannot create a second effect. Persist award and owner outbox atomically; shared inbox/idempotency infrastructure supplies the mechanism, not a competing Gamification-wide event bus. Historical proof survives mutable rule edits. This resolves U-GR-03's evidence strategy; exact schema fields/indexes are DEFERRED_IMPLEMENTATION_DETAIL in the coordinated database pass.

For terms-dependent redemption, persist the exact accepted terms version/content identity and Consent proof reference bound to that redemption and acceptance context. Runtime lookup of today's active terms or a generic audit event alone is insufficient proof of what was accepted. Consent owns acceptance proof; Gamification owns the redemption's contextual binding. This resolves U-GR-14's proof strategy without choosing retention duration or a cascade-delete behavior.

Implementation acceptance: all sign/type combinations, sum equals available-effect projection under the approved account policy, duplicate event/key returns original effect, conflicting key payload rejected, concurrent reversal yields exactly one opposite entry, cross-account/reversal-of-reversal rejected, rule/terms changes do not rewrite historical proof. Production earning/spending still waits for P04; expiration waits for P05 and any applicable legal policy. These are architecture requirements, not test execution claims.

Evidence: Gamification architecture §35 U-GR-02/03/04/14, append-only truth/invariants; CL-10 handoff records with the same IDs; canonical SH-044/045/046, SH-007/008. Applied to Gamification and CL-10 architecture/plan pairs. U-GR-01/05 require distinct product choices; their current blockers are recorded in the product decision packet.
