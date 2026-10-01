# Product-owner decisions

Current checkpoint: 2026-10-01. P01–P08 are binding approvals. P09–P11 below are new open PRODUCT_OWNER_CHOICE records; recommendations are not adopted. The P06–P08 options are historical decision context; the owner approved them on 2026-10-01 with the tighter constraints recorded in WA-R026. Only P09–P11 are currently open in this packet.

## Approved — do not reopen

| ID | Binding ruling | Application |
|---|---|---|
| P01 | Premium means earlier access to newly released availability; no displacement or conflict/eligibility bypass | WA-R011; Track eligibility, Booking release policy |
| P02 | Multiple sessions per Order only when explicitly included in the bounded purchased package | WA-R012; Order owns allowance/terms, Booking owns each appointment |
| P03 | Distinguish fixed-term employment and independent-contractor work; generic CONTRACT cannot hide the distinction | WA-R013; Hiring source, Compliance interpretation, Search projection |
| P04 | One User-wide points balance across programs; programs define earning/eligibility, not separate currencies. No automatic cash, entitlement, prize-entry or chance-odds benefit; conversion follows its approved owner | WA-R015; User-scoped atomic accounting, SH-119 Track commercial grants |
| P05 | No automatic expiration at launch. Points remain valid unless spent/reversed/otherwise adjusted through approved ledger operations. Future expiration requires approved applicability, notice, effective dates, existing-balance treatment and auditable ledger behavior | WA-R015; launch expiration disabled |

Sources: explicit owner approvals on 2026-09-29 (P01–P03) and 2026-09-30 (P04/P05). Earlier alternatives are preserved in Git history. No schema deployment or remote publication is authorized by those approvals.

## P06 — Rating scale

**Question:** What rating scale should a buyer use for a completed Order?

- **A — Recommended:** whole-number 1–5 stars; no zero, half-star input or unrated Review with an implicit zero. Aggregate averages may be fractional.
- **B:** whole-number 1–10 ratings.
- **C:** binary positive/negative feedback.

**Why it matters / blocked:** Review input/DB validation, public display and reputation aggregation must use one meaning. An Int field cannot choose it. Existing source truth says post-Order feedback affects Professional reputation but supplies no range.

**Evidence:** CL04-U034; Review / Dispute architecture §35 rating-scale question; Prisma Review.rating Int; glossary Review entry and completed-Order example. Search and Professional Eligibility consume Review's aggregate, not a competing scale. WA-R022 settles the aggregate owner/transport/version boundary without choosing the scale.

## P07 — Review publication and author revisions

**Question:** Should eligible buyer reviews publish immediately, and may the author revise them?

- **A — Recommended:** automatically publish after completed-Order, buyer-author and applicable safety checks; allow author rating/comment revisions with immutable history and the same checks. Editing never restores a hidden/removed review or bypasses a restriction. Staff can hide/remove through the owner/Moderation boundary.
- **B:** staff approval before each initial publication and before revised content becomes public.
- **C:** automatic eligible publication, but no author edits at launch; corrections require authorized support.

**Why it matters / blocked:** these are different customer experiences and staffing needs. Schema default pending is not approval of a permanent pre-moderation workflow. Blocks the publication/revision transition policy and corresponding reputation updates. Authorized restoration of a moderation restriction still requires the original owner decision/evidence; it is not granted by an author edit.

**Evidence:** CL04-U035/036; Review / Dispute architecture §9.1 and §35 explicitly leave auto-publication/edit/restoration open. WA-R022 now provides durable revision/history and stale-projection protection; it does not select the product workflow.

## P08 — Who can dispute, and how does a case reopen?

**Question:** Which participant/case model should launch use?

- **A — Recommended:** the Order's buyer Customer or seller Professional may open a commercial dispute; authorized support may record one on behalf of an identified participant. Keep one case identity per Order, with an authorized reviewer able to reopen that case for new evidence or a documented correction. Preserve each decision/settlement cycle; no automatic second financial effect on reopening.
- **B:** buyer-initiated disputes only, one case per Order, with the same controlled reviewer reopening.
- **C:** both participants may open, but permit separate sequential case identities per Order; at most one active case.

**Why it matters / blocked:** participant permissions and whether an old case is reopened versus replaced cannot be chosen from orderId uniqueness. Blocks dispute-opening authorization and case/reopen constraints. Recommendations do not allow unrelated parties or an arbitrary system actor to start cases.

Opening/appeal windows are explicit versioned product-policy configuration that must be approved before activation; no numerical deadline is invented here. Platform case policy does not determine statutory/provider dispute rights. WA-R022 independently resolves adjudication versus settlement versus closed and preserves the evidence needed for any selected model.

**Evidence:** CL04-U038/039/040; Review / Dispute architecture §9.2/§35 and CL-04-R007 actor representation; current Prisma orderId uniqueness; glossary Dispute is an Order-attached commercial conflict, not a ModerationCase.

## Response shorthand and boundary

**P06 A, P07 A, P08 A are approved.** WA-R026 incorporates whole-number 1–5 input, safety-checked immutable revisions, authorized restoration, both Order participants, represented support, one durable case with repeat cycles including later sessions, independently authorized idempotent financial effects, and versioned opening/appeal policy without invented deadlines. No deployment or remote publication is authorized. Remaining handoff review is not implicitly complete.


## P09 — Digital access and refund finality (OPEN)

**Recommended:** no automatic `final_after_access` refund denial at launch. Preserve access evidence for Order/Dispute adjudication under the applicable approved policy. Neither accepting terms, issuing a URL, starting playback/download nor a delivery observation alone denies a refund. This does not promise unconditional refunds or override applicable rights/provider rules. A later automatic finality policy requires an explicitly approved event, exceptions, applicable jurisdictions, disclosure and legal review.

**Alternative:** enable automatic finality at a separately selected access event, subject to approved legal policy and exceptions. Selecting this requires defining that event; the enum alone is insufficient.

**Why the owner must choose:** changes the buyer's refund experience and the seller's commercial risk. WA-R028 defines reliable observations, not the commercial consequence. Blocks automatic access-based refund decisions only; evidence mechanics can proceed.

**Evidence:** CL-05-U045; Digital Goods architecture §35.1–35.2; Order and Review consume digital delivery evidence, not Media refund decisions.

## P10 — Download allowance consumption (OPEN)

**Recommended:** consume one allowance for a successfully completed logical download established by trusted server/provider delivery evidence. Retries/resumptions of that same logical download count once. URL issuance, terms acceptance, failed or unverified delivery do not consume it. Reserve in-flight capacity to enforce the cap; reconcile unknown outcomes before releasing capacity. `used` means a finite allowance is exhausted. Unlimited grants end through expiry/revocation rather than first use. Existing authorization and security checks apply on each access.

**Alternative:** consume an allowance when an authorized transfer starts, with an explicit support/compensation policy for failed transfers. This tolerates less delivery observability but may charge an allowance for an unsuccessful download.

**Why the owner must choose:** determines what the buyer receives and whether failure costs a purchased allowance. A completion-based choice requires a qualified delivery adapter; unknown cannot be fabricated as success. No assertion that bytes delivered proves human consumption. This consumption rule is independent of refund finality in P09.

**Evidence:** CL-05-U045/U046; Digital Goods architecture §8.4, §35.2/35.3 and proposed finite-exhaustion interpretation. WA-R028 supplies reservation/retry/evidence mechanics without adopting a consumption threshold.

## P11 — Seller acceptance before payment capture (OPEN)

**Recommended source policy:** live/service purchases require the seller's acceptance of the frozen scope before payment capture and fulfillment. An explicit Gig award accepted by that Professional satisfies acceptance for its matching frozen Order; do not demand duplicate consent. Approved published standalone downloads/self-paced courses can accept automatically. Platform screening has no fabricated seller acceptance. For an explicitly sold multi-session service package, purchase acceptance covers the package; each Booking still requires current scheduling/eligibility/conflict checks.

A payment authorization/reservation before acceptance is permitted only where the qualified payment flow supports it; it is not capture or a guarantee of fulfillment. Seller decline or expiry cancels the pending purchase and releases/voids only its outstanding reservations/authorizations through their owners. Any already captured amount follows an independently authorized refund workflow. Response windows are versioned product policy; no numerical timeout is invented. Required Agreement/Consent/readiness checks still apply.

**Alternative:** capture payment before seller acceptance and handle decline/timeout through an approved refund workflow. This differs materially in buyer experience, funds handling and dispute exposure.

**Why the owner must choose:** determines whether a customer is charged before a Professional agrees to perform. `awaiting_seller` and `paid` enum values do not select that experience. Blocks source-specific acceptance/payment transitions, not ordinary Order drafting or evidence design.

**Evidence:** CL04-U019; Order architecture §9.1 (non-binding conceptual progression) and §35 item 10. P02 defines purchased session count but does not decide when a seller accepts the purchase. Neither recommendation activates payment/provider behavior.

**Requested decision:** approve or amend P09, P10 and P11 as product rulings. No request for deployment, publishing or legal certification is included.
