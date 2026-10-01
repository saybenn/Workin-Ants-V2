# Product-owner decisions

Current checkpoint: 2026-10-01. P01–P05 are binding approvals. P06–P08 below are recommendations only; no answer is inferred. Architecture and code may not silently adopt them.

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

**P06 A, P07 A, P08 A** approves the three recommendations. Modify individual parts if needed. These are genuine PRODUCT_OWNER_CHOICE records; technical persistence, audit/retry, ownership and projection questions around them have been ruled separately. This packet does not claim all remaining handoff rows are adjudicated or that these are the final possible product questions in the uncompleted review.
