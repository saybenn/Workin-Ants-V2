# Product-owner decisions — scoped checkpoint

Date: 2026-09-29, America/New_York. **P01–P03 APPROVED by the product owner on 2026-09-29.** The recorded recommendation options below are decision history, not open alternatives. The approved directions and tighter constraints are applied as WA-R011–013 in the owner/consumer architectures and plans. Schema implementation, legal facts and provider evidence remain separately gated.

## P01 — What should Hive Club priority scheduling actually do?

**Why it matters:** the paid benefit is approved, but Booking cannot implement it without choosing a customer experience. Track can resolve/snapshot the entitlement independently.

- **A — Earlier access to newly available appointment slots (recommended).** Premium customers can book before the general release. Existing confirmed bookings and slot-conflict rules remain protected. The release-window duration can be configured later.
- **B — Priority when waiting/competing for the same opening.** Premium affects the ordering of eligible requests. This requires an explicit waiting/competition workflow; it must not silently displace existing bookings.
- **C — Premium-reserved appointment inventory.** Professionals or platform policy reserve some slots for premium customers; allocation/release rules must then be specified.

**Former product-choice gate (now closed; implementation prerequisites remain):** Booking's priority effect, consumption policy if any, and its exact Track-to-Booking contract. Ordinary booking conflict safety and entitlement resolution are not blocked.

**Evidence:** Booking architecture U-BC-05 explicitly lists materially different effects and forbids inventing one; Track architecture §11.7 and U-CL01-31 defer that same effect; canonical registry approves priority as a benefit without selecting its mechanics. Collapse: CL-05-U017, U-BC-05, U-CL01-31. No legal/provider lookup can select the intended customer benefit.

## P02 — Can one paid Order cover several scheduled sessions?

**Why it matters:** this determines whether a purchased service/package can schedule multiple appointments and how fulfillment is measured. A nonunique database foreign key is not product approval.

- **A — Yes, when the purchased offering/package explicitly includes multiple sessions (recommended).** One Order can have bounded sessions consistent with what was sold. This does not allow unlimited duplicate bookings or merge individual Booking lifecycles.
- **B — No, one scheduled session per Order for the initial release.** Additional sessions require separate Orders. Any later package support needs an explicit contract expansion.

**Former product-choice gate (now closed; implementation prerequisites remain):** Order-to-Booking cardinality constraints, multi-session fulfillment and corresponding refund/cancellation interpretation. An ordinary SlotLock must still not be converted twice; that separate invariant is not an answer to Order multiplicity.

**Evidence:** Booking architecture §8 / U-BC-02 says `Booking.orderId` is nonunique but requires a business ruling before code relies on multiplicity; Booking implementation prerequisites preserve that gate; CL-05-U014 repeats it. Order owns transaction truth, not the number of appointments implied by an unspecified sold package.

## P03 — What does a “contract” Job mean?

**Why it matters:** fixed-term employment and independent-contractor hiring are different products and need distinguishable compliance inputs. The existing `EmploymentType.contract` label does not distinguish them.

- **A — Support both with distinct labels (recommended).** Separate fixed-term employment from independent-contractor hiring; a precise value mapping follows the decision.
- **B — Fixed-term employment only.** “Contract” means an employee position with a defined term.
- **C — Independent-contractor hiring only.** “Contract” means a contractor engagement posted by an Organization.

**Former product-choice gate (now closed; implementation prerequisites remain):** ambiguous contract-type Job publication, related form/filter semantics and compliance-input mapping. Other defined employment types and CompensationPeriod handling are not blocked. Legal classification rules remain external evidence after the product vocabulary is chosen; a selected label does not determine legal worker status.

**Evidence:** CL-06 U-CL06-07; Organization Hiring architecture U-CL06-07; Job Compliance architecture U-CL06-07 / PR-JC-03; the glossary lists `contract` without choosing between these meanings. WA-R010 independently resolves CompensationPeriod stewardship; it does not choose a product meaning. Collapse: CL-06-U007 and U-CL06-07's employment-type portion.

## Response shorthand

`P01 A, P02 A, P03 A` accepts the recommended behavior directions. Exact DTOs, field names, provider adapters and migration mechanics remain the orchestrator's responsibility. These decisions do not authorize deployment, a destructive migration, or GitHub publication.


## Accepted ruling and application

- P01 A → WA-R011: access timing only; no displacement or eligibility/conflict bypass.
- P02 A → WA-R012: explicit purchased bounded session allowance; Order owns purchase, Booking owns each appointment.
- P03 A → WA-R013: distinct fixed-term employment and independent-contractor concepts; generic CONTRACT is not a canonical substitute.

Source: product-owner message approving all three recommendations with the tighter architectural constraints. This is affirmative product approval, not inferred consent. No deployment, destructive migration or remote publication is authorized by these decisions.


## P04 — Can earned points be spent across programs? OPEN PRODUCT_OWNER_CHOICE

**Recommendation:** one User-wide point balance. Program and ProfessionalProfile references describe how points were earned; they do not create separate wallets. Reward-specific eligibility still applies, points are not cash, points cannot be purchased, and deterministic points do not improve prize odds.

**Alternative:** separate balances per User + Program; points earned in one program cannot fund another program's rewards. Profile-scoped balances would be another explicit product model, not an inference from an optional foreign key.

**Why your decision is required:** this changes what users can buy with earned points. It determines the account identity, balance query and atomic spending boundary, so it cannot be deferred as schema naming. Current architecture expressly prohibits selecting User-only or Program-only scope from the schema. Recommendation is NOT adopted.

**Evidence:** current Gamification architecture §35 U-GR-01 and §24 lock-key warning; CL-10 handoff U-GR-01. Glossary PointLedgerEntry/Reward/RewardRedemption entries establish ledger ownership and redemption, but not cross-program spendability. Master product rules settle Track benefits and prize-odds separation, not point fungibility. WA-R014 resolves technical ledger math/provenance independently.

**Blocks:** final point-account contract, production balance/earn/spend/redemption integration. Other readiness work is not implicitly certified or blocked.

## P05 — Do points expire? OPEN PRODUCT_OWNER_CHOICE

**Recommendation:** no automatic point expiration in the initial release. Do not introduce an expiration worker or silently expire existing value. Any future expiration policy must be explicitly approved, disclosed and implemented prospectively under applicable legal requirements.

**Alternative:** points expire under an explicit program policy. If selected, the policy must specify the expiration basis/window and treatment of already-earned points before activation; the technical lot/spend/reversal implementation will follow that ruling.

**Why your decision is required:** expiration removes earned user value; the existence of an `expired` enum is not authorization. Recommendation is NOT adopted. This question gates only expiration behavior, not all Gamification work.

**Evidence:** Gamification architecture §35 U-GR-05, expiration-worker gate and CL-10 handoff U-GR-05; glossary lists expired as a possible entry type without a product policy. No numerical retention/expiration period is inferred.

Response shorthand for these new choices: **P04 User-wide; P05 no initial expiration** accepts both recommendations. P01–P03 remain approved and must not be reopened.
