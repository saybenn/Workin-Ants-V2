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


## WA-R015 — User-wide points and no launch expiration (P04/P05)

**Binding product-owner ruling, approved 2026-09-30.** One User-wide Workin Ants points balance applies across Gamification/Rewards programs. Programs independently define earning rules and reward eligibility; they do not create separate point currencies or balances. This closes U-GR-01 / P04. Account identity and the atomic spending/ledger lock scope are User ID; optional program/profile references are provenance or eligibility context, never alternate wallets. All program-specific earning events credit the same account; reward eligibility is checked separately from point sufficiency. Cross-program spending uses the same canonical balance and cannot bypass a reward's eligibility conditions.

Points do not automatically function as cash, a Track/commercial entitlement, a purchased sweepstakes entry, or a mechanism for increasing chance-based prize odds. A separately approved conversion to a commercial benefit follows the explicit boundary and owner: Gamification owns redemption, Track owns commercial grants (SH-119), and the affected feature applies the granted benefit. No direct premium flag, implicit currency conversion, or automatic prize-entry creation is permitted.

**No automatic point expiration at launch.** Existing points remain valid unless spent, reversed or otherwise adjusted through an approved ledger operation. This closes U-GR-05 / P05 for launch. The `expired` enum remains reserved; launch commands, scheduled jobs and rules cannot append expiration effects. Program closure, inactivity, tier changes or profile changes do not expire a User's points. A future expiration feature requires explicit approved policy covering applicability, notice, effective dates, existing balances and auditable ledger behavior. Retention of proof is a separate concern and cannot be used to erase spendable value.

Technical application: calculate balance from the append-only owner ledger under WA-R014; serialize spending by User account, enforce sufficient available points atomically, and use immutable idempotent spend proof tied to redemption. Programs remain metadata/eligibility predicates, not lock partitions. Rebuildable balance/leaderboard projections never become source truth. Do not infer existing production balances or run a migration/backfill from this ruling.

Acceptance requirements: earnings from two programs combine into one balance; concurrent redemptions across programs cannot overspend it; reward eligibility can deny redemption despite sufficient points; profile/track changes preserve the account; program closure does not expire points; launch expiration attempts are rejected; replay creates no second spend; approved commercial conversion uses Track and never changes prize odds. These are future implementation tests, not a completion claim.

Classification: PRODUCT_OWNER_CHOICE — RESOLVED by explicit approval. Applied: Gamification, Track, Sweepstakes and CL-01/CL-10 architecture/plan pairs. Duplicate collapse: U-GR-01 and U-GR-05 across owner/CL-10 records. Programs and profiles do not redefine account scope.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


## WA-R017 — Owner facts and decision contracts

Class: **AI_RESOLVED**.

SH-003 is a family of small owner-specific queries, not a mandatory universal DTO. Each query takes authenticated caller/purpose and a typed owner resource reference, exposes only required authorized facts with an owner-issued source token, and distinguishes unavailable/stale from absence or denial. Consumers do not load foreign Prisma records. SH-015 remains a reusable result pattern, not a universal domain enum: carry a decision category, stable owner reason code, evidence/source token and evaluation time; payload variants remain owner-specific. Domain outcomes such as Job Compliance warning/review_required and Healthcare redacted/blocked retain their distinct meaning. An unavailable prerequisite never becomes allow. Exact wire names/runtime schemas are DEFERRED_IMPLEMENTATION_DETAIL inside these constraints and must be fixed in producer/consumer fixtures before parallel integration.

Adopt this interpretation for all references that formerly treated SH-003/015 proposal status as an unconditional blocker on owner-specific interfaces. Neither SH status is promoted. New generic repositories, universal authorization or generic business-policy dispatch are forbidden. Grouped owner-specific contracts do not become interchangeable because their envelopes look similar.

Duplicate-collapse scope: CL01-HU-004/005/015; CL02-D048; CL03-HD079; CL04-U046; CL-05-U053; CL-06-U041/042; CL-07-H17; CL-08-HU-14/15; CL-09-D060; CL-10-HU045. Only the stated concern is adjudicated; adjacent legal/product questions are not silently closed.


## WA-R018 — Durable execution, receipts and operational evidence

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Use one platform-owned persistent command-idempotency/inbox/outbox/job mechanism with Postgres transactional persistence in the coordinated database pass. Module application/domain boundaries own effect semantics. A successful owner mutation atomically stores its domain change and outbox record; no transaction is held across provider/network calls. Consumers atomically claim a stable source event plus effect identity and commit their owner effect. Unknown outcomes reconcile before a new business attempt. Same scoped command key plus same canonical fingerprint replays the original result; different fingerprint conflicts. Owner/operation/subject scope is part of the key. At-least-once delivery is assumed; never promise global exactly-once execution.

Provider callbacks use verified provider/account/event identity, payload fingerprint, receipt state and separate effect/attempt state under the provider-owning Module (SH-059/060). A received/claimed record is not proof of completed effect. Duplicates preserve original proof; telemetry records observations. A retry of one semantic effect reuses its downstream idempotency identity. A genuinely new business attempt has a new identity linked to the prior result and cannot silently overwrite history. Booking workflow steps likewise carry a stable run/step/effect key. Exact tables/index names and runner library are implementation details; production runtime evaluation remains a scoped provider/operational gate, not a reason to build Module-local queues.

Adopt Ops-owned Postgres persistence for operational SystemEvent, IntegrationFailure and OpsIncident; QueueJob remains an operational projection of the platform runner, not a second executable queue. SystemEvent is append-only; correction references the original. IntegrationFailure separates occurrence identity from recovery observations; recording the same occurrence replays, another actual attempt creates another occurrence. Incident operator state is open/triaged/mitigated/resolved, with explicit authorized reopening recorded as a new transition; automatic grouping/alerts require versioned configured rules. Ops success/recovery cannot finish a business workflow. Tradeoff: durable local diagnostic queries require migrations/storage; provider dashboards remain secondary. Accept PR-CL09-05 persistence direction without claiming schema deployment or selecting retention periods.

Acceptance: concurrent identical/conflicting keys, crash after receipt and before effect, crash after domain commit and before dispatch, duplicate/out-of-order callback, lease recovery, retry exhaustion and reconciliation. Do not activate a consumer merely because a queue accepted its job.

Duplicate-collapse scope: CL01-HU-021 and U-CL01-08/U-IA-09 mechanism portion; CL02-D050/051/056 mechanism portion; CL03-HD004/043/044/048/075; CL04-U055/063; CL-05-U022/027; CL-07-H08/H14/H31 and U-CL07-13/14; CL-08-HU-05; CL-09-D018/019/039/040/041; CL-10-U13 and U-GR-17 mechanism portion. Only the stated concern is adjudicated; adjacent legal/product questions are not silently closed.


## WA-R019 — Consent catalog, acceptance causation and buyer provisioning

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Consent owns an immutable version/content catalog, including consent type, version, exact content or immutable content reference/hash, locale, jurisdiction applicability and effective interval. Existing logs cannot prove an unrecorded presentation. Bind acceptance to the catalog entry and the actual rendered presentation identity/version, subject, action/context and time; preserve an immutable rendering descriptor where composition changes presentation. SH-009 selects applicable content, SH-007 stores acceptance, and SH-008 queries proof. Same acceptance command key/fingerprint replays; a new intentional re-acceptance is a new command/proof, not a uniqueness collision on User+type+version. Current-state eligibility queries use current applicable proof; Orders, screening authorizations, digital terms, redemptions and other historically binding actions preserve their specific proof reference/content-version binding. A generic audit log alone is not that binding.

Withdrawal/decline is recorded separately as an append-only disposition, not by rewriting an earlier acceptance; the consuming policy evaluates its effect. Legal re-consent/material-change obligations and retention periods are external facts. ConsentType.age_gate can prove acknowledgment only; Identity separately evaluates age eligibility. This resolves proof/catalog/retry architecture, not legal sufficiency for every category.

Customer provisioning uses the Customer owner synchronously and idempotently at the first buyer action (SH-004), with durable uniqueness on User. Optional registration-time outbox provisioning can warm the profile but never substitutes for this precondition. Customer aggregate views use the existing SH-126 Customer application facade over authorized owner queries; default to query composition, introducing a durable projection only with a demonstrated query need and invalidation contract. Legacy backfill/deletion awaits the database-evidence gate; User remains authentication identity. Tradeoff: first buyer action depends on Customer availability, but avoids an eventually missing commercial actor and duplicate local provisioning.

Duplicate-collapse scope: U-CL01-13/14/17/18; U-CD-01/02/03; CD-PR-02/03/04; CBP-U-03; CL01-HU-016; CL04-U054; CL-05-U012; CL-07-H32; CL-10-HU030; U-GR-14 proof portion. Only the stated concern is adjudicated; adjacent legal/product questions are not silently closed.


## WA-R020 — Privacy executor identity and truthful completion

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Privacy persists an immutable target descriptor with request identity, owner Module ID, registered owner target kind, opaque source ID/version, permitted action and descriptor/executor schema version. Each owner validates its own reference and field map. Typed child targets may be enumerated separately or included in an explicit versioned parent executor contract listing all covered child kinds; arbitrary `other`, a crawler or assumed cascade never supplies coverage. Deduplicate by request+owner+target-kind+source-id+action+source-version; preserve a new generation when re-evaluation changes an instruction. This is Privacy dispatch metadata, not polymorphic Media ownership.

Persist per-target attempts and final owner receipts independently of queue telemetry. A receipt names target/instruction identity, source version observed, action/outcome, executor version, completion time, evidence reference and any owner retention basis. Correction/restriction are explicit outcomes, never mislabeled deletion. Search acceptance is pending until Search returns its actual required projection outcome; Media artifact readiness similarly requires actual finalize/readiness proof. Retention is complete only when Privacy accepts an evidence-backed lawful exemption, not merely because an owner requested one.

Aggregate completion means every required target has either verified execution or an accepted lawful disposition. Summaries/exports disclose retained or restricted categories and reasons safely; `completed` never means all data was erased. Outstanding/failed targets prevent completed. A lawful fully accounted exemption does not by itself mean technical partial failure. An incomplete export stays pending/retryable or failed; no silent serializer omission or ready download. Any future deliberate partial-export product must explicitly distinguish partial from complete. This chooses correctness over premature delivery.

One request may have multiple execution/artifact generations for retries or refreshes; generations are immutable, correlated and only the current authorized ready artifact is offered. Revoke superseded access. Per-subject conflicting mutations serialize and re-evaluate owner state; do not reject or erase a legal request merely because another exists. Statutory verification, deadlines, restriction entitlement, backup completion wording, retention schedules and final User disposition remain EXTERNAL_REQUIREMENT. Identity markers are projections of Privacy outcomes, not a second rights lifecycle. Exact target enums/schema fields are deferred implementation constrained by this protocol.

Acceptance: restart routing, duplicate targets, changed source version, missing child coverage, failed serializer, lawful exemption versus unproven retention, Search queue acknowledgment versus completion, stale bundle access and concurrent conflicting instructions. No blanket claim of complete privacy coverage is authorized until all owner target/field matrices are reviewed.

Duplicate-collapse scope: U-08-03/04/07; CL-08-HU-01/03/04/05/06/08/12/17 protocol portions; CL-07-H12/H34; CL-10-HU033 protocol portion. Only the stated concern is adjudicated; adjacent legal/product questions are not silently closed.


## WA-R021 — Notification recipient and attempt model

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Use one logical Notification per resolved User recipient and semantic source intent; channels are deliveries of that notification. Organization is source/context, not an inbox principal. Hiring supplies the authorized recipient set and source-policy version; Notification expands/deduplicates User recipients and snapshots the resolved routing context. Revalidate current sensitive access before including protected payload or dereferencing context; a historical fan-out snapshot grants no future access. Source Modules own recipient eligibility and message meaning; Notification owns safe rendering, channel routing and provider mechanics.

Each delivery attempt has its own immutable attempt identity and correlation to logical notification, recipient, channel, destination generation and semantic send key. Retrying unknown provider outcomes reconciles before resending. Provider acceptance is not confirmed delivery or user interaction. Notification summary separately tracks pending/in-progress, partial success, all required routable deliveries successful, or exhausted failure; dismiss/read state remains independent and never alters source workflow status. The database pass must provide a representation for partial delivery rather than mapping it to total success. Policy may mark a channel optional; that requirement is snapshotted before dispatch, not rewritten to hide failure.

Persist dismissedAt/expiresAt when these actions/policies apply. User interaction is Notification-owned append-only evidence separate from Delivery receipts. Template versions are immutable and schema-validated; source supplies a registered semantic template intent plus allowlisted variables. Generic external channels carry minimal safe summaries/deep links, never raw message bodies, financial/tax documents, exact addresses or regulated data by default. Identity challenge-provider transport stays Identity-owned. Concrete provider selection/configuration and legally sufficient notice delivery remain external prerequisites.

Tradeoff: explicit parent/attempt representation needs schema alignment but avoids multiple inbox items per channel and false completion. Acceptance: organization fan-out dedupe, removed member sensitive access, duplicate send, partial channel failure, expiry/dismissal independence, callback before/after retry, unsupported channel and secret redaction.

Duplicate-collapse scope: U-CL07-09/10/11/12/13/14/19/20/21; CL01-HU-025 delivery portion; CL-07-H13/H21 contract mechanism portion; optional source trigger choices and legal notice proof remain separately gated. Only the stated concern is adjudicated; adjacent legal/product questions are not silently closed.


## WA-R022 — Review and Dispute durable adjudication

Class: **AI_RESOLVED**.

New buyer Reviews bind the Order's authoritative CustomerProfile author and ProfessionalProfile target; User is authentication/audit identity. Review owns append-only revision/lifecycle evidence using SH-031, while the current Review record is its present state. This does not authorize user editing or a publication policy: those product choices remain explicit. Professional reputation consumes Review's versioned aggregate (ProfessionalProfile ID, rating sum/count or derived average/count, projection/source version); use an idempotent owner command/public contract, not direct profile writes. Exact transport name is implementation detail; older aggregate versions cannot overwrite newer ones.

Dispute owns immutable case events, adjudication decisions and workflow-step evidence: actor/authority proof, decision/reason/basis/time, amount/currency/basis where applicable, source Order version, semantic command identity and required Hold/Order settlement correlations. Mutable adminNotes is not adjudication or history. Keep authorized notes as append-only records with controlled reason codes and minimized text; corrections reference previous entries. Use an owner version token checked atomically on competing adjudications. Shared execution handles retries; Dispute records whether each required effect is pending, completed or failed.

`resolved_refund`/`resolved_release` represent the committed adjudication outcome, not completed financial movement. `closed` requires all required downstream outcomes confirmed/reconciled, or a durable authorized determination that none apply. Dismissal must state a controlled basis and require no outstanding effects before closure. A failed/refused/timed-out refund does not become closed success; retry/reconciliation stays visible. Financial effects go through Order/Payment and Hold owners with idempotent correlations. This resolves the proof/finality distinction without selecting eligible openers, case multiplicity, deadlines or appeal/reopen product policy.

Database migration must supply owner history and workflow evidence rather than extending generic Audit into a dispute ledger. Review/Event and Dispute/Event names are conceptual owner records, with exact models/FKs/indexes deferred until the coordinated database pass. Acceptance: mutually exclusive adjudications, audit versus domain-proof distinction, downstream timeout, duplicate refund result, stale reputation aggregate and reconstruction after restart.

Duplicate-collapse scope: CL04-U037/041/042/043/045; CL03-HD082; CL-04-R010 persistence strategy; review-author portion of CL-04-R007. Unnamed adjacent questions are not closed.


## WA-R023 — Sensitive disclosure and audit failure boundaries

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Require a durable sensitive-access audit acceptance before returning exact private location, protected file/playback/join credentials, resumes, healthcare-sensitive fields, tax/identity/Agreement evidence, or sensitive admin exports. If required proof cannot be durably recorded, withhold the protected response and return a retriable unavailable result; never return the secret and log later. Record safe allowed/denied/redacted/blocked/unavailable outcomes under Audit-owned vocabulary without importing Healthcare enums as generic authorization. Include service/system/provider actor attribution and request correlation, not nullable User alone. A denied request must still disclose no target-existence details; audit trouble never changes denial into access.

Privileged irreversible mutations require durable owner decision/history plus atomic audit-outbox intent before committing owner state. If that local durable write fails, roll back the mutation. Later Audit transport failure retries/reconciles; it does not roll back an already executed external financial/legal effect or erase domain evidence. Where a legal action specifically requires pre-action Audit acceptance, its owner contract adds that stricter gate; legal deadlines/recovery remain scoped requirements. Low-risk diagnostics are best effort and never recursively produce infinite failures.

Identity owns fresh action-bound assurance; Role still authorizes the action. Require step-up for security-factor/recovery changes, financial adjudication/movement, privileged permission changes, bulk sensitive evidence export and administrative override/release of protective controls. Existing sessions or admin roles do not substitute. Exact assurance methods/lifetimes and action registration are security implementation policy, with provider capability checked before activation. Ordinary read access is not automatically all step-up; owner-specific policy may require it. Privacy identity verification is a separate statutory proof requirement.

Tradeoff: protected access becomes dependent on durable audit availability; this is preferable to an unprovable sensitive disclosure. Acceptance: audit unavailable before response, durable intent failure before mutation, outbox delivery outage after commit, privileged service actor, retry without duplicate effect, denied-target anti-enumeration and redaction-safe evidence. These rules amend failure/assurance portions only; per-owner legal retention and complete target/action matrices remain separate work.

Duplicate-collapse scope: CL01-HU-006/007/008/012 security portions; CL02-D025/044/056; CL04-U032; CL-05-U007/062; CL-06-U048/055; CL-08-U16 and HU-09/19; CL-09-D016/030/031/032/035/043/046; CL-10-HU031/PR-CL10-09. Unnamed adjacent questions are not closed.


## WA-R024 — Financial readiness is action-specific

Class: **AI_RESOLVED_WITH_TRADEOFF** from the approved separation of Identity, optional screening, Professional readiness and financial execution. Preserve the existing Professional identity/KYC baseline; do not equate optional background screening with KYC. Payment's financial decision identifies the named action and the applicable KYC, tax, account and restriction dimensions, rather than exposing one timeless professional-is-financially-ready boolean.

Profile editing/drafting never requires payout readiness. Public activation/publication/Gig response uses the applicable Professional identity, Track, taxonomy/Trust/Healthcare and Hold policies; incomplete payout-account or tax setup alone is not a new universal nonfinancial block unless an explicit applicable requirement demands it. Paid acceptance/checkout must meet Payment's current charge/recipient capability for that flow; payout execution requires current recipient/account/KYC/tax/hold requirements. The purchaser cannot be charged through an unsupported recipient capability merely because a listing is visible. UI shows the owner-provided unavailable transaction state without leaking the seller's private KYC/tax details.

Tradeoff: discoverability and action readiness can differ; each attempted financial action re-evaluates current Payment facts. This avoids silently extending payout-only requirements to every public profile or treating a public listing as financial clearance. Provider/regulatory prerequisites may tighten the financial action and remain EXTERNAL_REQUIREMENT. No legal threshold, automatic KYC approval or alternative sponsorship flow is invented.

This resolves the universal-versus-action-specific architecture in CL03-HD001 / CL-03 U-01 / PE-U01 / Payment UD-01. Implement the action/dimension matrix and owner fixtures before activation; do not treat this as proof that the selected provider permits a particular charge/transfer. Existing settled optional screening and explicit free Track baselines remain binding.


## WA-R025 — Location consumer alignment and reveal evidence

Class: **AI_RESOLVED** from the binding location product ruling and canonical SH-027/028/131. U-08-13/14's product predicate/directionality is settled: exact service location is disclosed only to the authenticated Professional/provider legitimately performing the active in-person service, within its service-performance window. No buyer, Organization, Search or public-map entitlement to another party's exact location is implied. Completion ends that justification; cancellation, refund or dispute masks/revokes it. Rescheduling requires a fresh current decision. Payment, Booking confirmation or a cached flag alone is insufficient authorization.

Source Modules own their protected location facts/references. Booking's exact/fuzzy/precision/reveal fields are non-authoritative scheduling snapshots or compatibility fields; neither Booking nor Order operates a second reveal lifecycle. Location queries current typed participant, service-state, time-window and source-location facts through owners. Missing/stale/inconsistent facts deny disclosure. Each supported service context has a typed identity; an attached Booking and Order must be consistent, not arbitrarily XOR when both legitimately describe the service. A nullable context pair never permits context-free disclosure. Non-Booking source contexts require an explicitly supported service-performance contract; Job/Organization address fields do not automatically qualify.

Location stores current per-viewer/service/source decision plus immutable decision/revocation history using its owned lifecycle and SH-031 mechanism. The semantic current key includes viewer, typed service context and source reference; an owner source/policy token binds the decision. Atomically reject stale Location writes; revoke/expiry wins over a replayed old allow. Replays may reproduce proof identity but must never re-disclose exact data without a current authorization evaluation. Rescheduling updates evidence in the same owner lifecycle rather than creating a parallel reveal flag. WA-R023 requires durable sensitive-access proof before returning exact data. This resolves U-08-11/12/15/16/19 architecture; exact fields/constraints and coordinated migration remain implementation prerequisites.

Fuzzy generation uses a versioned Location policy per supported typed source, stable for the same source/policy generation. Radius/precision and refresh/expiry settings must be explicitly configured and validated before public use. Source/policy changes, privacy removal and expiry invalidate old results. SH-131 returns only current approved projection fields with source/policy version and validity; absent/stale data is unavailable, never exact fallback or read-triggered generation. Consumers use SH-028 only for generation/invalidation commands. The target-kind registry names actual source owners and validators; free-form target strings cannot broaden support. U-08-17/18 policy structure is AI_RESOLVED; numerical deployment settings are deferred configuration, and geocoder/KMS/vendor evidence is externally gated.

Acceptance: wrong viewer or source relation, absent context, Booking/Order mismatch, completed/cancelled/refunded/disputed service, reschedule, stale source/policy and delayed events, duplicate reveal after revocation, audit failure and expired public projection. Exact location remains absent from Search, notification payloads and telemetry. Legal retention/Privacy dispositions are not selected by this ruling.

Duplicate collapse: CL-08 U-08-11–19 and HU-13 predicate/structure portions; CL-05-U004 and U-BC-07; CL04-U051; CL02-D055. Source contracts/fixtures, legal retention and KMS/geocoder facts remain scoped gates, not new product choices.
