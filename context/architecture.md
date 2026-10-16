# Workin Ants — root architecture

Status: **Gate 7 architectural synthesis, 2026-10-16.** Basis: Gate 5 architectural convergence and Gate 6 posture confirmation D. This document synthesizes current lower-level invariants; it does not certify executable contracts, development readiness, a root build plan, parallel implementation, database deployment or provider activation.

## Authority and evidence

Authority follows the concern as routed by [context-map.md](context-map.md). Module architecture owns its source records, policy, lifecycle and public contracts. Cluster architecture coordinates boundaries. [Shared Operations](shared/shared-operations.md) owns permanent SH identities/reuse boundaries. [Canonical rulings](reconciliation/platform-architecture-rulings.md), including approved P01–P19, resolve stated conflicts; plans sequence those decisions and progress records evidence. This synthesis cannot silently replace a lower-level owner or make a proposed operation executable.

The basis is [platform-convergence-review.md](reconciliation/platform-convergence-review.md), its structured evidence, [the action matrix](reconciliation/platform-lifecycle-action-matrix.md), [the typed graph](reconciliation/platform-dependency-graph.md), and [the finalized bridge inventory](reconciliation/cross-cluster-bridge-inventory.md). Coverage is 34 Modules / 10 Clusters / 132 permanent Shared Operations, 268 bridge families and all 563 unique historical records. R069 registers 47 committed events. All interfaces remain unqualified for parallel implementation: no `FROZEN_FOR_IMPLEMENTATION` designation follows from documentation consistency.

## Platform ownership and topology

| Cluster | Source owners | Coordination invariant |
|---|---|---|
| CL-01 | Identity, Role, Consent, Customer, Track | Account identity, permission, proof, buyer identity and entitlement are distinct. Identity owns role assignments; Role interprets policy. |
| CL-02 | Taxonomy, AI Taxonomy, Search | Controlled vocabulary and contextual assignment precede derived discovery; AI is advisory; Search never owns source lifecycle or permission. |
| CL-03 | Professional, Marketplace, Payment, Trust, Healthcare | Seller identity/supply, money, verification and regulated coverage retain separate truth. Readiness composes action-specific current facts. |
| CL-04 | Gig, Order, Review/Dispute | Accepted demand source, transaction truth and adjudication are distinct. Order coordinates refunds through Payment. |
| CL-05 | Booking/Calendar, Digital Goods, Media, Video | Appointment, purchased access, exact file bytes and provider media/room state remain separate lifecycles. |
| CL-06 | Hiring, Candidate, Job Compliance, Interview | Hiring owns Organization/membership/Job; Candidate owns applications/resume/participation; compliance evaluates immutable Job input; Interview owns appointment/participants. |
| CL-07 | Messaging, Notification | Contextual conversation/history and delivery intents/endpoints/attempts are separate. Source participants and outcomes remain with their owners. |
| CL-08 | Privacy, Location | Privacy orchestrates lawful owner execution; Location owns purpose-bound public projection and protected reveal. Neither becomes a universal source repository. |
| CL-09 | Moderation, Hold, Audit, Ops | Decisions, independent protective causes, durable proof and diagnostics are separate. No operational state grants domain authority. |
| CL-10 | Gamification, Sweepstakes | User-wide points/redemption and chance-based entry/drawing/winning retain independent rules, ledgers and actual fulfillment evidence. |

Users are account holders. ProfessionalProfiles sell Offerings. Organizations hire and post Jobs; CandidateProfiles apply. Gigs are public paid requests, neither Jobs nor Offerings. Orders are transaction truth; CustomerProfile is the commercial buyer identity while User is the credential principal. R003 platform-screening Orders use a distinct source/participant representation without a fake Professional seller. That representation is architecture, not a claim that the current schema implements it. Media attachments are explicit owner-held joins. Shared enums do not merge lifecycles. R087 routes OrganizationFeatureAccess commercial responsibility to Track; monetized ATS remains disabled/unqualified and never becomes a fourth User AccountTrack.

Supabase/Postgres is source truth. A shared database does not authorize foreign repositories, generic polymorphic source loaders or cross-owner mutations. Each consumer uses the actual owner contract, not provider SDKs, local premium/blocked/eligibility flags, raw Prisma entities or a downstream projection. Compatibility fields are nonauthorizing mirrors; the twelve reviewed cases and all 177 model ownership routes are indexed in platform-schema-compatibility-review.json. Physical constraints/backfill remain separate work.

## Contract and action composition

Every protected action identifies its owner, supported actor relationship, source transition, incoming facts, currentness tokens, applicable consent/entitlement/Hold/regulated checks, proof obligation, emitted fact/command, consumer consequence and failure/recovery protocol. The action matrix is the complete reviewed architecture scope; runtime per-port DTOs and fixtures are still required.

Identity authenticates; Role authorizes a registered action from current owner facts; the owner checks its own lifecycle and remaining substantive gates. Unknown action, stale/unavailable required facts, unregistered purpose or unsupported target never becomes allow. A server credential is not permission to skip policy. Admin/support status grants only explicitly registered actions. Sensitive financial/security/override actions require action/target/current-generation-bound assurance. Privacy statutory verification is a separate evidence requirement.

R085 source-fact queries terminate: a narrowly registered service/purpose/target/field scope yields source-owned facts without recursively invoking the composed gate being evaluated. They are not anonymous endpoints or a blanket service bypass. Ordinary protected views still enforce full authorization. Media readiness and contextual relationship facts never issue credentials; credential issuance consumes current owner permission and durable proof. Hold source-cause evidence does not require its own Hold already released, but cannot waive that cause, another condition or the final downstream Hold check.

Contract stages are separate:

| Stage | Meaning | What it does not prove |
|---|---|---|
| Architecture agreed | Owner, semantic fields/effects, failures, boundaries and sequence reviewed | Compiled request/result compatibility, runtime safety or freeze |
| Contract-only dependency | A narrow fixture/schema can support isolated qualification work | Actual upstream implementation or a production adapter |
| Port implementation dependency | Consumer action needs the real owner port plus applicable tests and external policy | Whole upstream Module/Cluster maturity |
| End-to-end activation gate | Specific workflow proves real storage, authorization, concurrency and provider behavior | Unrelated workflows or platform-wide readiness |

No connection implies a full-neighbor startup requirement. A missing implementation cannot be bypassed with a duplicate local source. Disabled facets remain disabled: public Customer location, Gig AI, reverse mandatory Booking availability eligibility, private Messaging Search, unspecified Digital→Payment tax policy, unnamed reward effects/providers and reverse Sweepstakes entry display into Order. Existing allowed adjacent mechanisms do not enable those facets.

## Durable execution and shared runtime

WA-R018/086 select one platform-owned persistent command/inbox/outbox/job/locking/reservation mechanism backed by coordinated Postgres persistence. The platform integration owner stewards composition and the single migration stream; this responsibility is not an additional Module or Cluster. Each Module retains semantic identity, source state/history, effect policy and recovery. Ops owns operational records and adapters; QueueJob is a runner projection, not another queue.

An owner mutation commits its source change, retained history and required outbox/proof intent atomically. No database transaction spans a provider/network call. At-least-once delivery is assumed. Same scoped command key/fingerprint replays the original receipt; changed fingerprint conflicts. Subscriber event deduplication is additional to the economic/business-effect identity that prevents duplicate money, quota, points, fulfillment or session allocation. Lease/fence/CAS checks prevent a stale worker/reviewer from committing.

The bootstrap dependency route is configuration/pure schemas → persistence/crypto/verification primitives → registered owner fact/proof adapters → policy/owner services → dispatch/workers → optional delivery/diagnostics. Register callbacks without invoking business actions during construction. A required port outage fails the affected action closed; unavailable optional telemetry cannot prevent its own supporting primitive from starting. Liveness, action-scoped readiness and downstream lag are separate health observations. Runner/vendor/configuration/performance qualification remains open; no hosting choice is inferred here.

Unknown external outcomes reconcile using the original semantic identity before another effect. Acceptance, queue acknowledgment, provider redirect, attempted delivery and telemetry success never prove business completion. Reservations remain held until actual committed success or durable fenced noncommit prevents any late source commit. Retries reauthorize current source scope as required; they do not acquire an Ops override.

## Critical lifecycle coordination

| Workflow | Required sequence | Safety boundary |
|---|---|---|
| Profile and Track | Profile source/history/outbox commit → typed default-Free enrollment → dependent current entitlement query | No creation wait on Track, inferred Free, paid downgrade or quota reset. |
| Candidate submission | Current Job/subject eligibility → stable intent → current UTC-period Track reservation → one Candidate acceptance → consumption receipt | Unknown stays reserved; late confirmation uses actual acceptance month; withdrawal gives no quota credit. |
| Offering publication | Immutable source requirements/context → actual Professional/Digital/Video readiness → owner publication → Search refresh | Requirements query never asks the same publication decision. |
| Paid screening | Trust package/actual participant facts → separate screening Order → qualified paid outcome → Trust provider check | No Professional seller gate or completed-check prerequisite to buy that check; legal purpose/consent remain required. |
| Marketplace purchase | Immutable source/pricing/terms → seller acceptance and required Agreement evidence → Payment instruction → actual normalized result → Order transition | No provider-owned Order lifecycle, retrospective Track repricing or automatic settlement dispatch. |
| Purchased Booking | Preliminary slot hold → current purchased entitlement/agreement → Order session reservation → Booking attachment/receipt | Unknown conversion cannot release allowance; reschedule preserves authorization; performance allegation is not Order completion. |
| Refund/dispute | Review adjudication → Order SH-108 coordination → Payment effect → Order result → Review settlement | Hold release or dispute release decision cannot itself send money. |
| Job publication | Hiring immutable source snapshot → Job Compliance source/rule-bound evaluation → Hiring checks all gates → publication | Compliance disclosure/check is not originating compensation truth; stale check cannot publish. |
| Interview | Current application/member facts → committed parent/schedule/participant revision → Calendar/Video desired-state setup | Provider setup and Interview outcome cannot assign Application status; no elapsed-start acceptance or expiration timer. |
| Protected delivery | Current exact asset/parent facts → context permission/category intersection → durable access proof → credential issuance | URL is not actual bytes, playback is not download, cache is not permission; provider revocation capability must be qualified. |
| Privacy | Verified request → complete owner inventory → generation instruction → actual owner/provider receipts or lawful disposition → complete export/erasure accounting | Protocol agreement is not field/action executor coverage; accepted is not completed; unknown backup/provider scope stays unresolved. |
| Moderation/Hold | Retained decision/evidence → typed owner effect/receipt; separate source-cause release → fresh business reevaluation | Restoration is a new checked effect; no source write from Search, event, Hold release or Ops success. |
| Rewards/prizes | Qualified original fact/rule → immutable ledger/population/reservation → supported actual effect → recognition/correction | No duplicate reward from a mirrored outcome; no silent redraw, odds benefit or unsupported fulfillment. |

The typed graph retains 18 critical cycle reviews. A whole-Module SCC contains all 34 Modules because reciprocal facts, shared controls and asynchronous recovery are normal. The reviewed synchronous action projection and bootstrap graph have no unresolved cycles. This architecture judgment does not assert that future implementations cannot deadlock; executable call-chain, concurrency and failure tests must demonstrate compliance.

## Events, projections and currentness

R069 is the selected committed-fact vocabulary and subscriber registry. Source state/history/outbox commit together. The envelope has stable event identity, exact versioned name, producer, typed aggregate, owner revision, occurrence/effective times, causation/correlation and correction lineage. Private bodies, exact coordinates, provider tokens, raw screening/resume/evidence or credentials are excluded. Subscriber-specific field minimization applies; an event is not a public/client broadcast.

Consumers dedupe event plus effect identity, reject changed fingerprints, retain revision/generation tombstones and recover gaps through owner snapshot/replay. Owner tokens are opaque; unrelated revisions are not globally comparable. Event lag does not grant authorization. Protected actions and Search results recheck current applicable source policy. Search owns derived indexing/work only; complete enumeration is necessary before orphan removal, and queue acknowledgment is not removal evidence. Source mutations never wait for successful indexing.

Messaging emits only authorized minimal realtime invalidation after commit and checks current audience at subscribe/emission/reconnect/refetch. Notification uses separate finite source intents, safe recipients/templates/action routes, channel attempts and endpoint generations. It cannot decide source success or legal service. Revocation/currentness versus in-flight external delivery has an explicit qualified effect boundary; asynchronous invalidation alone cannot promise instantaneous cancellation of an already issued provider credential.

## Cross-cutting privacy, security and regulated data

The four rail matrices in the bridge inventory and platform review are binding composition evidence. CL-01 authority/consent/entitlement, CL-07 communications, CL-08 Privacy/Location and CL-09 moderation/Hold/Audit/Ops must all preserve current source ownership.

Sensitive disclosure requires durable Audit acceptance first; if proof cannot persist, withhold protected output. Privileged irreversible mutation requires retained owner decision/history and atomic audit/outbox intent before commit; later Audit transport retries do not roll back a real external effect. Audit's own protected evidence reads produce one nonrecursive receipt. Diagnostics never manufacture legal, transaction or privacy proof.

Data-sensitivity categories are not an ordered universal rank. Owners declare actual field/context classification; Healthcare determines regulated applicability/coverage and access owners enforce every relevant category. Adapter configuration facts are not legal/BAA approval. Current source ancestry cannot be weakened by attachment or copied cache. Unknown required policy/capability fails closed for that exposure.

Exact service location uses current consistent Order/Booking facts and the performing Professional/window policy; Interview location uses its separately approved current participant/purpose. Public fuzzy Location reads never regenerate or fall back to exact data. Private checkout tax location remains Order evidence consumed by Payment. Media-produced public derivatives require actual metadata-scrubbing proof.

Privacy retains request verification, orchestration, lawful exemptions and final accounting. Each real source/provider owner enumerates and executes only its data and returns durable generation-bound receipts. Full field/action inventories, serializer mappings and provider/backup outcomes are not established by R070 or this root architecture. Export-ready binds a complete manifest to actual bytes and exact ready Media artifact. A restore must reapply erasure/restriction generations before serving data. Retention law and actual backup dispositions remain external evidence.

## Database, provider and implementation boundaries

[Gate 6 evidence](reconciliation/database-posture-confirmation-2026-10-16.json) retains **D**. Repository facts are 177 models / 207 enums, one SQL migration creating 53 tables / 31 enums, with 124 mapped model tables lacking checked-in creation statements. These are not a live schema comparison or replay proof. No migration/seed/reset, environment discovery or provider execution occurred in this review.

One integration owner sequences coordinated schema changes only after actual environment identity, preservation requirements, migration ledger and schema-only comparison support a baseline/continuation decision. Preserve used migration history and required data. RLS/grants need a complete exposed-relation inventory and server/RLS semantic parity fixtures; server credentials do not waive owner checks. No database posture A/B/C or disposal assumption is made here.

Provider lifecycle stays with its registered owner: Identity security, Track Billing, Payment financial/tax rails, Trust screening, Healthcare BAA, AI inference, Search indexing, Location geocoding, Booking Calendar, Media storage/scanning, Video media/rooms, Notification delivery and Ops monitoring. Shared verification/retry helpers do not move source ownership or prove provider capabilities. Credentials and SDK bodies stay inside adapters. Regulated coverage, signature/webhook/callback behavior, cancellation/deletion, revocation, idempotency, reconciliation, rate limits and actual account/configuration require evidence before activation.

## Exit and remaining gates

Root synthesis is permitted and this Gate 7 document is supported by the recorded Gate 5/6 evidence. CF-ROOT architecture placement is resolved. Its root build plan, executable harness, production runtime/provider choice and rollout qualification remain scheduled readiness obligations. Handoff records retain 649 ADJUDICATED / 12 PARTIAL / 0 PENDING; the partial CF-ROOT facets are not falsely closed because a root document now exists.

The next readiness work is Gate 8 root build-plan synthesis and Gate 9 harness alignment under the master sequence. Entry requires this root architecture and current lower-level traceability to remain consistent, explicit port/feature qualification gates, and migration posture D honored. Producing or approving parallel lanes requires qualified executable contracts and actual prerequisite evidence; documentation consistency alone cannot satisfy that gate. This checkpoint creates no root build plan, does not start product implementation and does not authorize deployment, migrations, main merge or interface freeze.

All eleven external families remain in [external-requirements.md](reconciliation/external-requirements.md). Outstanding DTO/schema, concurrent effect/reservation/fence, RLS, Privacy executor, provider and runtime tests are retained in the platform review. OPS-GIT-AUTH-001 remains an independent operational limitation: local commit/recovery bundle is not GitHub publication; only a fresh remote HEAD comparison proves publication.
