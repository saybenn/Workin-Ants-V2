# Product-owner decisions

Current checkpoint: 2026-10-01 America/New_York. P01–P13 are binding approvals. WA-R032 applies P12/P13 including paid-recovery timing and Premium-period usage on downgrade. P01–P15 are binding approvals; WA-R040 applies all P14/P15 clarifications. Earlier alternatives are historical.

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


## P09 — Digital access and refund finality (APPROVED — WA-R029)

**Recommended:** no automatic `final_after_access` refund denial at launch. Preserve access evidence for Order/Dispute adjudication under the applicable approved policy. Neither accepting terms, issuing a URL, starting playback/download nor a delivery observation alone denies a refund. This does not promise unconditional refunds or override applicable rights/provider rules. A later automatic finality policy requires an explicitly approved event, exceptions, applicable jurisdictions, disclosure and legal review.

**Alternative:** enable automatic finality at a separately selected access event, subject to approved legal policy and exceptions. Selecting this requires defining that event; the enum alone is insufficient.

**Why the owner must choose:** changes the buyer's refund experience and the seller's commercial risk. WA-R028 defines reliable observations, not the commercial consequence. Blocks automatic access-based refund decisions only; evidence mechanics can proceed.

**Evidence:** CL-05-U045; Digital Goods architecture §35.1–35.2; Order and Review consume digital delivery evidence, not Media refund decisions.

## P10 — Download allowance consumption (APPROVED — WA-R029)

**Recommended:** consume one allowance for a successfully completed logical download established by trusted server/provider delivery evidence. Retries/resumptions of that same logical download count once. URL issuance, terms acceptance, failed or unverified delivery do not consume it. Reserve in-flight capacity to enforce the cap; reconcile unknown outcomes before releasing capacity. `used` means a finite allowance is exhausted. Unlimited grants end through expiry/revocation rather than first use. Existing authorization and security checks apply on each access.

**Alternative:** consume an allowance when an authorized transfer starts, with an explicit support/compensation policy for failed transfers. This tolerates less delivery observability but may charge an allowance for an unsuccessful download.

**Why the owner must choose:** determines what the buyer receives and whether failure costs a purchased allowance. A completion-based choice requires a qualified delivery adapter; unknown cannot be fabricated as success. No assertion that bytes delivered proves human consumption. This consumption rule is independent of refund finality in P09.

**Evidence:** CL-05-U045/U046; Digital Goods architecture §8.4, §35.2/35.3 and proposed finite-exhaustion interpretation. WA-R028 supplies reservation/retry/evidence mechanics without adopting a consumption threshold.

## P11 — Seller acceptance before payment capture (APPROVED — WA-R029)

**Recommended source policy:** live/service purchases require the seller's acceptance of the frozen scope before payment capture and fulfillment. An explicit Gig award accepted by that Professional satisfies acceptance for its matching frozen Order; do not demand duplicate consent. Approved published standalone downloads/self-paced courses can accept automatically. Platform screening has no fabricated seller acceptance. For an explicitly sold multi-session service package, purchase acceptance covers the package; each Booking still requires current scheduling/eligibility/conflict checks.

A payment authorization/reservation before acceptance is permitted only where the qualified payment flow supports it; it is not capture or a guarantee of fulfillment. Seller decline or expiry cancels the pending purchase and releases/voids only its outstanding reservations/authorizations through their owners. Any already captured amount follows an independently authorized refund workflow. Response windows are versioned product policy; no numerical timeout is invented. Required Agreement/Consent/readiness checks still apply.

**Alternative:** capture payment before seller acceptance and handle decline/timeout through an approved refund workflow. This differs materially in buyer experience, funds handling and dispute exposure.

**Why the owner must choose:** determines whether a customer is charged before a Professional agrees to perform. `awaiting_seller` and `paid` enum values do not select that experience. Blocks source-specific acceptance/payment transitions, not ordinary Order drafting or evidence design.

**Evidence:** CL04-U019; Order architecture §9.1 (non-binding conceptual progression) and §35 item 10. P02 defines purchased session count but does not decide when a seller accepts the purchase. Neither recommendation activates payment/provider behavior.

**Approved:** P09–P11 with the full owner clarifications in WA-R029. The seller-acceptance ruling includes valid intentional instant-book/precommitted policies; the earlier recommendation is superseded where narrower. No deployment, publication or legal certification is implied.


## P12 — Paid subscription cancellation, renewal failure and benefit timing (APPROVED — WA-R032)

**Recommended launch policy:** free→paid benefits start only after verified successful paid enrollment. Cancellation or downgrade to free takes effect at the end of the already-paid benefit period; paid benefits continue until that boundary. Failed renewal creates no additional unpaid grace period: after the paid-through boundary, fall back to the explicit free baseline. Core account access/security and existing purchased Order rights remain available under their owners. Preserve the fee/commission/benefit snapshots already bound to an accepted purchase; a later subscription change does not reprice it.

Do not automatically offer trials, paid pauses, prorated refunds or paid-to-paid plan changes at launch without an approved policy. This does not block free→paid enrollment or normal period-end cancellation, and does not override an authorized billing correction/refund or required external rule. Immediate security/Hold restrictions remain separate from commercial cancellation.

**Alternative:** immediate cancellation/downgrade with an approved unused-period credit/refund policy, and/or a specified grace period after failed renewal. Those choices change paid customer rights and must state the financial/access consequences.

**Why this requires the product owner:** buying a month, cancelling and losing benefits immediately differs from retaining the paid term; unpaid renewal grace is also a commercial promise. Neither Stripe status nor a local enum decides it. No grace duration, proration amount or automatic refund is inferred. WA-R030 has already resolved catalog/versioning/receipt/storage architecture independently.

**Affected records:** CL-01 U-CL01-28; CL-06-U050 and other consumers of effective paid benefit periods. **Scoped block:** final paid subscription transition/access policy; free representation, provider-neutral foundations and unrelated readiness work are not thereby blocked.

## P13 — Candidate application monthly quota and withdrawals (APPROVED — WA-R032)

**Recommended launch policy:** the free allowance is 15 successfully submitted applications per UTC calendar month. A successful submission consumes one; editing it, a retry or duplicate transport does not consume another. A failed or never-committed submission consumes nothing. Withdrawal or employer rejection does not restore an allowance after successful submission. Any permitted later genuinely new application follows Candidate's own submission eligibility and counts as a new successful submission; this ruling does not independently permit reapplying.

Paid Candidate participation is unlimited while effective. Keep same-period usage history across upgrades/downgrades, so switching plans never resets a free quota. No destructive monthly reset. WA-R030 already defines atomic reservation/commit/reconcile and authorized corrections for proven erroneous/duplicate consumption; such corrections are not a general withdrawal refund.

**Alternatives:** use an enrollment/billing-anniversary month instead of UTC calendar month, and/or restore allowance when the Candidate withdraws. State those choices explicitly if preferred; they change reset timing and how reusable the free allowance is.

**Why this requires the product owner:** “15 applications/month” does not say when a month starts or whether one allowance can repeatedly be reused by withdrawing. These determine the actual free benefit, while timezone implementation and race safety follow the selected policy.

**Affected records:** U-CL01-29; CL-06-U049. **Scoped block:** live Candidate quota activation/withdrawal accounting; technical quota and application protocol architecture is already resolved.

**Approved:** P12/P13 with the full clarifications in WA-R032. No deployment, publication or database-baseline authorization is implied.


## P14 — Gig proposal revisions after viewing (APPROVED — WA-R040)

**Question:** May a Professional revise a proposal after the customer has viewed or shortlisted it?

**Recommended A:** allow revisions while submitted/viewed/shortlisted, until acceptance, rejection or withdrawal. Preserve every revision; show that terms changed; acceptance binds the exact latest revision and rejects stale acceptance attempts. Accepted terms cannot be edited through this command.

**Alternative B:** lock proposal terms once viewed; changes require a separately approved replacement workflow. A narrower alternative locks only when shortlisted.

**Why this needs you:** both protect accepted contracts, but one lets a Professional change a proposal under consideration while the other promises the customer stable terms once reviewed. Architecture cannot choose that customer experience.

**Blocked:** response revision eligibility, UI promises and the complete revise-versus-accept contract. **Evidence:** CL04-U003; Gig architecture §9.3 and §35. WA-R039 resolves versioning, immutable history and race safety independently.

## P15 — Other Gig proposals after an award (APPROVED — WA-R040)

**Question:** What should happen to the other proposals when the customer accepts one?

**Recommended A:** automatically mark remaining nonterminal proposals rejected with reason another_response_selected, preserving history. Already withdrawn/rejected proposals remain unchanged. Any notification follows the source-owner/Notification contract.

**Alternative B:** retain their statuses as inactive historical proposals, with further acceptance disabled while the winner exists; do not imply they are still competing for the awarded Gig.

**Why this needs you:** single-award controls how many win, but does not determine the outcome shown to other Professionals. This changes their proposal status and customer experience.

**Blocked:** full award side effects and nonwinning-response presentation. Neither choice authorizes re-award or automatic reopening after cancellation. **Evidence:** CL04-U003 and confirmed CL-04-R002 explicitly leave losing-response treatment unresolved; WA-R039 resolves the single-winner database and transaction contract.


P14/P15 approved with immutable latest-presented revision binding, visible material changes, and ANOTHER_RESPONSE_SELECTED rejection only on award-capacity exhaustion. See WA-R040; launch remains single-award.


## P16 — Booking completion and no-show authority (OPEN)

**Question:** Who may confirm that a service session was completed or missed?

**Recommended:** either participant may submit an outcome report. The Professional or authorized support may confirm the operational session outcome; the Customer may confirm or contest it. A contest preserves both reports and routes to the existing Order/Review dispute process. A report, elapsed appointment time or no-show label alone does not authorize payout, forfeiture, refund or full multi-session Order completion.

**Alternative:** require Customer confirmation before final session completion, with an approved support-resolution route for nonresponse. This changes whether the Professional depends on a Customer response to close a session.

**Blocked:** final Booking completion/no-show action authority and contested-outcome behavior. Evidence: CL-05-U026; Booking architecture §10 PR-BC-03 and §36. State enums and general Role policy do not select this product promise. Recommended policy remains unadopted; no numeric response window is invented.

## P17 — Candidate employer-search participation (OPEN)

**Question:** Must Candidates choose to appear in employer search?

**Recommended:** explicit opt-in, off by default. Opt-out removes the searchable projection; submitting an application does not silently opt the Candidate into discovery. Existing application access remains governed by Candidate/Organization workflow rights. Search participation does not expose the raw resume or bypass audience permissions.

**Alternative:** profiles become searchable by eligible employers by default, with clear notice and opt-out. This materially changes the privacy expectation.

**Blocked:** Candidate search activation/default and participation control. Evidence: CL-06-U010; Candidate architecture U-CL06-10 (§35), §25 and projection lifecycle. Existing WA-R034 protects transport/audience but does not approve participation. Legal sufficiency of any required disclosure remains a separate external gate.

## P18 — Interview invitation expiration (OPEN)

**Question:** Should unanswered interview proposals automatically expire at launch?

**Recommended:** no automatic expiration at launch. Authorized organizers may cancel or replace a pending proposal; any manual no-response record must preserve the actual invitation/response evidence and cannot imply that the recipient read it. Scheduling validity and passed appointment time still constrain acceptance.

**Alternative:** automatic expiration under an explicitly approved deadline policy, shown to participants. A deadline and its anchor must be chosen before that feature activates; no numeric duration is inferred.

**Blocked:** expiration worker and no_response transition policy only. Evidence: CL-06-U039; Job Interview architecture §22.1 and U-JI-10. Other Interview contracts can continue independently.


## P19 — Booking and Dispute conversations (OPEN)

**Question:** Should service-session and commercial-dispute discussion share the Order conversation or have separate conversations?

**Recommended:** reuse the Order conversation for participant discussion about its Bookings and Dispute, with clear context labels. Private support/adjudication notes remain in their authorized owner workflow and never enter the participant thread automatically. Current authorized thread membership still controls every disclosure; a case assignment does not silently add support to participant conversation.

**Alternative:** separate Booking and Dispute conversations, requiring explicit participant membership, history visibility and context contracts.

**Blocked:** creation/routing of Booking-specific and Dispute-specific conversations only. Evidence: CL-07 U-CL07-02; Messaging architecture §35 questions 3/4. Existing typed FK uniqueness and consumer references do not choose the customer conversation experience. This question does not approve unsolicited direct/group admission, a support-case product, or multi-thread expansion.
