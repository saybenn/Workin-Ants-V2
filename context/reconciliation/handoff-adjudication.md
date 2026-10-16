# Handoff adjudication coverage

P01–P19 approved and binding. Canonical dispositions live in handoff-adjudication.json and applied rulings in platform-architecture-rulings.md. Grouping is not closure; ADJUDICATED includes scoped external requirements.

## Current metrics

- raw_pending: 0
- raw_partial: 12
- family_candidates: 92
- normalized_families: 76
- unresolved_architecture_families: 0
- scheduled_readiness_families: 1
- external_requirement_families: 11
- unresolved_families: 12
- closed_existing_ruling: 22
- closed_deduplication: 0
- new_rulings: 48
- ai_resolved_families: 50
- ai_resolved_with_product_judgment_families: 1
- duplicate_facets_collapsed: 16
- product_questions: 0

Full ledger: 649 adjudicated, 12 partial, 0 pending (661 total). New-ruling count is since the normalization baseline (WA-R040 onward). Original 323-record coverage is preserved. Deduplication means verified alias closure, not just merging concern groups.

Scheduled readiness families retain partial source records for uncompleted plan/harness/runtime obligations; architectural route resolution is not implementation closure.

## Canonical family facets

| Evidence family | Canonical concern | Records | Classification | Integration |
|---|---|---:|---|---|
| COM-01 — Gig graph and award lifecycle | COM-01 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-02 — Money arithmetic and immutable monetary effects | COM-02 | 4 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| COM-03 — Context attachment stewardship | COM-03 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-04 — Location facts and proof | CF-LOCATION | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-05 — Track snapshots and catalog | COM-05 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-06 — Reputation query transport | COM-06 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-07 — Execution receipts and claims | COM-07 | 5 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| COM-08 — Digital content and consent proof | COM-08 | 2 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| COM-09 — Booking availability does not determine professional eligibility | COM-09 | 1 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| COM-10 — Privacy disposition and retention | COM-10 | 3 | EXTERNAL_REQUIREMENT | APPLIED |
| COM-11 — Legal content and manual execution | COM-11 | 5 | EXTERNAL_REQUIREMENT | APPLIED |
| COM-12 — Provider qualification | COM-12 | 5 | EXTERNAL_REQUIREMENT | APPLIED |
| COM-13 — Migration representation work | COM-13 | 11 | DEFERRED_IMPLEMENTATION_DETAIL | APPLIED |
| COM-14 — Inactive optional scope | COM-14 | 9 | DEFERRED_IMPLEMENTATION_DETAIL | APPLIED |
| COM-15 — Missing root artifacts | CF-ROOT | 2 | DEFERRED_IMPLEMENTATION_DETAIL | APPLIED |
| COM-16 — Booking completion and no-show authority | COM-16 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-17 — Order legal lifecycle and dispute restoration | COM-17 | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-18 — Agreement identity and requirements | COM-18 | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-19 — Provider references on Order | COM-19 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-20 — Owner event contracts | CF-EVENT | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-21 — Typed contextual communications | CF-THREAD | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-22 — Sensitive action matrix | CF-AUTH | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-23 — Hold and moderation integration | CF-MOD | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-24 — Reward event qualification | CF-REWARD-EVENT | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-25 — Notification triggers | CF-NOTIFY | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-26 — Calendar reference and consent normalization | CF-CALENDAR | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-27 — Live room recovery and proof | COM-27 | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-28 — Video source transport and thumbnails | COM-28 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-29 — Media and playback grant semantics | COM-29 | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-30 — Telemetry minimization | COM-30 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-31 — Sensitivity vocabulary | COM-31 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-32 — Digital asset snapshots | COM-32 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| COM-33 — Privacy export artifact protocol | CF-EXPORT | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-01 — Age eligibility provider and legal qualification | FH-01 | 4 | EXTERNAL_REQUIREMENT | APPLIED |
| FH-02 — Action catalog and assurance implementation | CF-AUTH | 7 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-03 — Bilateral event contracts | CF-EVENT | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-04 — Root infrastructure synthesis | CF-ROOT | 2 | AI_RESOLVED_WITH_TRADEOFF | PARTIALLY_APPLIED |
| FH-05 — Optional hash chain | FH-05 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-06 — Owner moderation executors | CF-MOD | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-07 — Recipient and device contracts | CF-NOTIFY | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-08 — Owner assignment and enumeration adapters | FH-08 | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-09 — Organization verification owner | FH-09 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-10 — Employment legal purpose | FH-10 | 2 | EXTERNAL_REQUIREMENT | APPLIED |
| FH-11 — Organization owner transfer | FH-11 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-12 — Compliance proof and publication | FH-12 | 6 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-13 — Work-arrangement vocabulary | FH-13 | 1 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| FH-14 — Non-authoritative compatibility and registry cleanup | FH-14 | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-15 — Candidate search participation | FH-15 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-16 — Application graph and immutable history | FH-16 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-17 — Application view and resume access proof | FH-17 | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-18 — Interview participation and successor scheduling | FH-18 | 5 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-19 — Calendar and meeting attachment boundary | CF-CALENDAR | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-20 — Job and Organization history | FH-20 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-21 — Candidate profile graph | FH-21 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-22 — Current candidate projection | FH-22 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-23 — Resume parser attempts and roles | FH-23 | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-24 — Hiring retention and privacy routing | FH-24 | 4 | EXTERNAL_REQUIREMENT | APPLIED |
| FH-25 — Interview proposal expiry | FH-25 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-26 — Hiring location privacy | CF-LOCATION | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| FH-27 — Protected candidate transport | FH-27 | 1 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| FH-28 — Candidate tag metadata | FH-28 | 1 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| FH-29 — Interview credential timing | FH-29 | 1 | AI_RESOLVED_WITH_PRODUCT_JUDGMENT | APPLIED |
| FH-30 — Review claims and temporary grants | FH-30 | 2 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| RAILS-01 — Conversation product cardinality and admission | CF-THREAD | 6 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-02 — Messaging current truth and immutable change evidence | RAILS-02 | 6 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-03 — Messaging restrictions, sensitivity and disclosure | RAILS-03 | 6 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-04 — Communication provider activation | RAILS-04 | 4 | EXTERNAL_REQUIREMENT | APPLIED |
| RAILS-05 — Subscription credential integrity | RAILS-05 | 1 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-06 — Notification owner interaction and safe intent | CF-NOTIFY | 7 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-07 — Events and realtime integration | CF-EVENT | 5 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-08 — Privacy target registry coverage | RAILS-08 | 5 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-09 — Retention and legal Privacy policy | RAILS-09 | 12 | EXTERNAL_REQUIREMENT | APPLIED |
| RAILS-10 — Communication optional capabilities | RAILS-10 | 4 | DEFERRED_IMPLEMENTATION_DETAIL | APPLIED |
| RAILS-11 — Legal notification proof | RAILS-11 | 7 | EXTERNAL_REQUIREMENT | APPLIED |
| RAILS-12 — Root/runtime and deployment gates | CF-ROOT | 10 | AI_RESOLVED_WITH_TRADEOFF | PARTIALLY_APPLIED |
| RAILS-13 — Current consent selection | RAILS-13 | 1 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| RAILS-14 — Privacy verification and request lifecycle | RAILS-14 | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-15 — Privacy resolved protocol portions | RAILS-15 | 4 | ALREADY_RESOLVED | CLOSED_BY_EXISTING_RULING |
| RAILS-16 — Export artifact handoff | CF-EXPORT | 3 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-17 — Location source facts | CF-LOCATION | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-18 — Geocoder and KMS activation | RAILS-18 | 1 | EXTERNAL_REQUIREMENT | APPLIED |
| RAILS-19 — Moderation execution and immutable evidence | CF-MOD | 10 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-20 — Moderation report/case lifecycle | RAILS-20 | 2 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-21 — Hold targets, history and release protocol | RAILS-21 | 12 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-22 — Audit vocabulary and integrity baseline | RAILS-22 | 6 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-23 — Ops/Audit capabilities and assurance | CF-AUTH | 6 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-24 — Sweepstakes rules and draw evidence | RAILS-24 | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-25 — Reward stock and fulfillment mechanics | RAILS-25 | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-26 — Reward participation and configuration | RAILS-26 | 7 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-27 — Prize legal policy and tax recognition | RAILS-27 | 6 | EXTERNAL_REQUIREMENT | APPLIED |
| RAILS-28 — Redemption and winning lifecycle safety | RAILS-28 | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |
| RAILS-29 — Reward qualifying source facts | CF-REWARD-EVENT | 4 | AI_RESOLVED_WITH_TRADEOFF | APPLIED |

## Remaining work

- **FH-04:** CF-ROOT architecture route is resolved by WA-R086 and context/architecture.md. Root build plan, executable harness, runtime/provider and database qualifications remain incomplete; no parallel implementation permission.
- **RAILS-12:** CF-ROOT architecture route is resolved by WA-R086 and context/architecture.md. Root build plan, executable harness, runtime/provider and database qualifications remain incomplete; no parallel implementation permission.

Bridge evidence is separately inventoried in bridge-catalog.json/md; extraction does not imply bilateral reconciliation or freeze. No product implementation, external approval, provider qualification or deployment is certified here.
