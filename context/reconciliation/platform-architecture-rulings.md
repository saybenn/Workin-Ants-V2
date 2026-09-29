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
