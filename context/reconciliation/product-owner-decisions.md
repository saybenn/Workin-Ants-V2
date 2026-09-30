# Product-owner decisions — scoped checkpoint

Date: 2026-09-29, America/New_York. Each item is a **PRODUCT_OWNER_CHOICE**, not a technical implementation question. Recommendations are not adopted defaults. No answer is inferred from this document. Other readiness work remains possible; these decisions gate only the named behaviors.

## P01 — What should Hive Club priority scheduling actually do?

**Why it matters:** the paid benefit is approved, but Booking cannot implement it without choosing a customer experience. Track can resolve/snapshot the entitlement independently.

- **A — Earlier access to newly available appointment slots (recommended).** Premium customers can book before the general release. Existing confirmed bookings and slot-conflict rules remain protected. The release-window duration can be configured later.
- **B — Priority when waiting/competing for the same opening.** Premium affects the ordering of eligible requests. This requires an explicit waiting/competition workflow; it must not silently displace existing bookings.
- **C — Premium-reserved appointment inventory.** Professionals or platform policy reserve some slots for premium customers; allocation/release rules must then be specified.

**Blocked until answered:** Booking's priority effect, consumption policy if any, and its exact Track-to-Booking contract. Ordinary booking conflict safety and entitlement resolution are not blocked.

**Evidence:** Booking architecture U-BC-05 explicitly lists materially different effects and forbids inventing one; Track architecture §11.7 and U-CL01-31 defer that same effect; canonical registry approves priority as a benefit without selecting its mechanics. Collapse: CL-05-U017, U-BC-05, U-CL01-31. No legal/provider lookup can select the intended customer benefit.

## P02 — Can one paid Order cover several scheduled sessions?

**Why it matters:** this determines whether a purchased service/package can schedule multiple appointments and how fulfillment is measured. A nonunique database foreign key is not product approval.

- **A — Yes, when the purchased offering/package explicitly includes multiple sessions (recommended).** One Order can have bounded sessions consistent with what was sold. This does not allow unlimited duplicate bookings or merge individual Booking lifecycles.
- **B — No, one scheduled session per Order for the initial release.** Additional sessions require separate Orders. Any later package support needs an explicit contract expansion.

**Blocked until answered:** Order-to-Booking cardinality constraints, multi-session fulfillment and corresponding refund/cancellation interpretation. An ordinary SlotLock must still not be converted twice; that separate invariant is not an answer to Order multiplicity.

**Evidence:** Booking architecture §8 / U-BC-02 says `Booking.orderId` is nonunique but requires a business ruling before code relies on multiplicity; Booking implementation prerequisites preserve that gate; CL-05-U014 repeats it. Order owns transaction truth, not the number of appointments implied by an unspecified sold package.

## P03 — What does a “contract” Job mean?

**Why it matters:** fixed-term employment and independent-contractor hiring are different products and need distinguishable compliance inputs. The existing `EmploymentType.contract` label does not distinguish them.

- **A — Support both with distinct labels (recommended).** Separate fixed-term employment from independent-contractor hiring; a precise value mapping follows the decision.
- **B — Fixed-term employment only.** “Contract” means an employee position with a defined term.
- **C — Independent-contractor hiring only.** “Contract” means a contractor engagement posted by an Organization.

**Blocked until answered:** ambiguous contract-type Job publication, related form/filter semantics and compliance-input mapping. Other defined employment types and CompensationPeriod handling are not blocked. Legal classification rules remain external evidence after the product vocabulary is chosen; a selected label does not determine legal worker status.

**Evidence:** CL-06 U-CL06-07; Organization Hiring architecture U-CL06-07; Job Compliance architecture U-CL06-07 / PR-JC-03; the glossary lists `contract` without choosing between these meanings. WA-R010 independently resolves CompensationPeriod stewardship; it does not choose a product meaning. Collapse: CL-06-U007 and U-CL06-07's employment-type portion.

## Response shorthand

`P01 A, P02 A, P03 A` accepts the recommended behavior directions. Exact DTOs, field names, provider adapters and migration mechanics remain the orchestrator's responsibility. These decisions do not authorize deployment, a destructive migration, or GitHub publication.
