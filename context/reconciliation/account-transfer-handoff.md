# Workin Ants — account-transfer operational handoff

Snapshot: 2026-10-15. This is a transfer checkpoint, **not Development Ready certification**. The sweep was deliberately stopped for account migration. No product implementation or deployment is complete or authorized by this document.

## A. Repository and exact snapshot identity

- Repository: **saybenn/Workin-Ants-V2**, remote `https://github.com/saybenn/Workin-Ants-V2.git`.
- Dedicated branch: **codex/development-readiness-2026-09-29**. Do not merge into main.
- Stable pre-transfer base: **55c0036715ec6bdec2c61b43811f251fee32d7e9**. The transfer commit is a descendant containing this document and all saved work. Obtain its exact SHA with `git log -1 --format=%H -- context/reconciliation/account-transfer-handoff.md`; final publication SHA is reported outside this self-referential document.
- Remote verified before transfer: only `main`, at **526bb1ab30480d66ca8b7da08d16badc6e613c1d**. Fetch succeeded; no remote dedicated branch existed. Do not assume this stays true after publication.
- Eight local-only commits before packaging, oldest first: `2517479`, `20702dc`, `e351620`, `b627088`, `5332959`, `aadac09`, `b416b4f`, `55c0036`. Publication must include their ancestry, not just a patch of the latest files.
- The pre-transfer tree contained extensive unstaged readiness edits and new reconciliation documents/scripts, with no staged changes. `account-transfer-manifest.json` lists exact intended paths, hashes, pre-transfer status and commit IDs. No other developer work was discarded.
- User explicitly authorized committing and pushing this dedicated branch for this transfer on 2026-10-15, superseding earlier refusal/no-push checkpoints. No force-push, history rewrite, main merge, branch deletion, migration execution or deployment is authorized.

## B. Current readiness state

Workin Ants is a multi-module marketplace and hiring platform: Users have distinct actor tracks; Professionals sell Offerings; Customers buy through Orders and post Gigs; Organizations hire through Jobs; Candidates apply. Ten Clusters and 34 Module architecture/plan pairs govern its lifecycles. Read actual owners rather than treating this overview as replacement architecture.

| Gate | Verified state | Remaining |
|---|---|---|
| 0 Current-state audit | Completed inventory baseline | Do not restart; new evidence may refine it |
| 1 Shared Operations namespace/reference | Complete | 132 contracts remain conservatively qualified, not all frozen |
| 2 Handoff adjudication | Partial: all records reviewed | 23 partial records in two canonical concerns; additional bridge findings below remain outside this decision-section metric |
| 3 Apply rulings | Extensive application through WA-R075 | Final source/consumer and stale-text reconciliation still required, including interrupted event-propagation review |
| 4 Final bridges | Extraction and normalization complete, semantic review partial | Final integrated inventory, domain review, current bilateral status and final rail matrices |
| 5 Platform-wide audit | Partial targeted reviews only | Fresh whole-platform convergence after Gate 4; no final pass claimed |
| 6 Database posture | D, scoped external gate established | Live target/provenance evidence before baseline/deployment strategy selection |
| 7 Root architecture | Not created | Only after cross-Cluster convergence |
| 8 Root build plan / lane map | Not created | Dependency-first plan and qualified lane boundaries |
| 9 Harness | Partial | Checks, standards and provider guide drafted; root-plan alignment, traceability and final instructions remain |
| 10 Final readiness | Not passed | No active implementation lanes |

Current machine evidence (`normalization-metrics.json`, `handoff-adjudication.json/md`):

- **661** historical decision-section records: **638 ADJUDICATED, 23 PARTIAL, 0 PENDING**. ADJUDICATED includes identified external requirements and deferred implementation, not executable readiness.
- The original normalization slice is **323** unfinished records (299 pending + 24 partial at `b416b4f`), preserved as **92 evidence facets / 76 canonical concerns**.
- **2 unresolved architecture concerns**: COM-13 migration representation and CF-ROOT (FH-04 / RAILS-12) root/runtime/harness synthesis. The source facet COM-15 already treats missing root artifacts as a scheduled dependency, not a domain choice.
- **11 external-requirement families**, plus explicit database provenance gate; **13 unresolved families** under the metric's architecture-plus-external union.
- **22 existing-ruling record closures; 0 deduplication-only record closures; 16 duplicate concern facets collapsed**. Grouping is not falsely counted as a closed evidence record.
- **50 AI-resolved canonical families; 1 AI_RESOLVED_WITH_PRODUCT_JUDGMENT family (FH-29 / R073)**; **36 new ruling IDs since normalization baseline (R040–R075)**.
- **0 genuinely unresolved product-owner choices** currently queued. Newly discovered bridge architecture gaps are not product escalations.
- **563 historical bridge records**, all preserved with raw source spans/hashes and inherited profiles. **268 conservative boundary families**, 121 canonical-SH operation review packages, 14 paired concern groups. These are directional contract facets, not 268 independent product decisions.
- Report-only rails review covers **78 families / 257 historical records / 17 packages**. The complementary **190-family domain review was interrupted and has no completed report**. Do not claim all 268 families reconciled.
- Shared registry: SH-001–SH-132, 109 Confirmed / 23 Proposed ruling identities. Qualification index: no interface promoted to frozen; no parallel product lane activated. Check actual JSON for exact current per-contract status.

## C. Authority by concern and canonical loading order

1. [context-map.md](../context-map.md) routes exact Module/Cluster paths; preserve existing directory spellings. [AGENTS.md](../../AGENTS.md) and [CLAUDE.md](../../CLAUDE.md) govern execution.
2. Ubiquitous Language governs terminology; project overview provides orientation. Follow their actual paths from context-map, not remembered paths.
3. Module architectures own their entities, invariants, lifecycles, public ports and contextual joins. Cluster architectures coordinate those owners. Plans sequence work and cannot override architecture.
4. [shared-operations.md](../shared/shared-operations.md) owns permanent SH identity/name/class/reuse boundaries. Do not trust remembered IDs from a conversation or rename/reuse them. [shared-operation-contract-status.json](shared-operation-contract-status.json) owns qualification evidence and gaps, not business lifecycle truth.
5. [platform-architecture-rulings.md](platform-architecture-rulings.md) is the single integration ledger. Its concern-specific amendments and corresponding owner edits supersede stale historical questions only within their scope. Original handoffs under `clusters/` remain immutable evidence indexes.
6. [handoff-adjudication.json](handoff-adjudication.json) preserves all 661 source identities/hashes/dispositions. [handoff-families.json](handoff-families.json) preserves 323-record family coverage and canonical group relationships. Neither grouping nor ADJUDICATED implies runtime readiness.
7. [database-readiness.md](database-readiness.md), Prisma schema/migrations and the deep Module/Cluster registries govern database facts/stewardship. One integration owner sequences shared schema changes. A registry ownership correction is not a migration.
8. Root architecture will own global invariants; root build plan will own rollout and lanes. They do not yet exist and must not precede convergence.

Cross-owner access uses named commands/queries, immutable events, owner facts and typed receipts. No foreign repositories, consumer-local permission/entitlement/provider copies, or generic polymorphic Media ownership. Source owners retain truth; projections are rebuildable; Notification delivery and provider callbacks do not become business truth. Shared infrastructure owns mechanisms, not domain workflows. Protected disclosure requires current authority, applicable consent/entitlement/safety and durable access proof where mandated. Legal sufficiency and actual provider capability require external evidence.

Parallel implementation requires qualified versioned contracts, clear file/model ownership, migration integration ownership, negative/compatibility fixtures and explicit merge gates. A contract fake cannot invent an unresolved interface. Architecture-review parallelism already used does not authorize product-development parallelism.

## D. Binding decisions and provenance

Read the complete [product-owner-decisions.md](product-owner-decisions.md), [platform rulings](platform-architecture-rulings.md), and corresponding owner architectures. The compact index below is routing, not a replacement for full clarifications.

| Decisions | Binding subject / ruling route |
|---|---|
| P01–P03 | Priority scheduling, purchased session cardinality and contract-Job meaning; R011–R013 |
| P04–P05 | One User-wide point balance; no launch expiration; R015 |
| P06–P08 | 1–5 whole-star inputs/fractional aggregate; publication plus immutable revision/restoration rules; one Order Dispute case with authorized cycles; R026 |
| P09–P11 | Approved digital refund/finality policy, one unit per logical download, seller acceptance before capture; R029 |
| P12–P13 | Paid-through premium, no unpaid grace, acquired rights preserved; Free Candidate 15 successful durable applications per UTC month, idempotent usage preserved across Premium/Free; R032 |
| P14–P15 | Proposal edits until terminal decision, latest-presented immutable acceptance; reject others when award capacity exhausted; R040 |
| P16–P19 | Attributed contestable completion/no-show reports, separate consequences; discovery opt-in default off; no timed invitation expiry but no stale-slot acceptance; Order participant conversation reuse with restricted private adjudication; R042 |
| 2026-10-12 operating instruction | Autonomous ordinary product judgment and batched consequential choices; operating-policy.md |
| 2026-10-15 transfer instruction | Preserve/publish dedicated branch and bootstrap; no new sweep in this transfer |

All R001–R075 are in the canonical ledger. R043–R065 cover Hiring, Commerce, communication/privacy, moderation/holds/rewards and foundation; R066/R067 integrate Notification and Moderation; R068/R069 action/event matrices; R070–R073 source descriptors, Location, compatibility stewardship and Interview timing; R074 contextual Customer/Gig queries; R075 Hold action/readiness mapping. Appendices are incorporated by reference where the owner documents say so.

R073/FH-29 is explicitly **AI_RESOLVED_WITH_PRODUCT_JUDGMENT**: no implicit pre/post-session Interview grace, half-open authorized interval, versioned future policy, with provider TTL/revocation qualification separately gated. Reasoning, alternatives, evidence, reversibility and affected files are retained in the ruling, `lane-reports/applied-remaining.json` and record disposition. It is not presented as a new human approval.

`lane-reports/` retains detailed application evidence. Earlier reports may say PARTIAL or pending where later root integration applied the same concern. Canonical rulings/record ledger plus actual owner files control; reports remain provenance, not competing authority. `remaining-semantics-review.md` and `cross-contract-review.md` are historical proposals now applied in the corresponding rulings, except explicit remaining qualification. Recommendations not integrated into rulings remain recommendations.

[external-requirements.md](external-requirements.md) and database-readiness.md isolate legal/provider/database gates. Numerical security/provider configuration, legal deadlines/retention and jurisdiction policy must not be fabricated. There is no current genuine owner decision packet to answer.

## E. Completed work and artifacts

- Applied P01–P19 and 75 scoped architecture rulings to relevant Module/Cluster architectures and plans; preserved source handoffs and permanent SH namespace.
- Integrated five original lane reports and later cross-contract/authority/remaining-semantics results. Corrected sensitivity intersection (categories are not ranked), private export handoff, event/notification intent semantics, moderation receipts and contextual conversation boundaries.
- Corrected registry stewardship for JobMedia, JobApplicationViewEvent and Interview participant records. `prisma/schema.prisma` and migration SQL were not changed in the transfer working batch.
- Added `authority-event-contracts.md`, `context-query-contracts.md`, `hold-action-contracts.md`, `operating-policy.md`, `external-requirements.md`, code-standards.md and library-docs.md.
- Extracted bridge-catalog.json/md; normalized bridge-family-index.json/md; preserved rail review in bridge-review-rails.json/md. **cross-cluster-bridge-inventory.md still contains only the old five-bridge slice**, not the final catalog.
- Added/extended `scripts/check-context.py`, `check-handoff-adjudication.py`, `check-handoff-families.py`, `check-bridge-catalog.py`, `render-handoff-progress.py`. Context check invokes the other structural checks; renderer updates human metrics from machine ledgers.

## F. Interrupted work, conversation-only findings now preserved

No agent must resume hidden session state. All agents were stopped for transfer. A previous account repeatedly exhausted usage while agents worked; files may be complete even when an agent reported a limit. Inspect saved artifacts, not agent completion labels.

1. **R068/R069 pending propagation was applied by root** after the owner writer stopped. `lane-reports/authority-events-pending-propagation.json` now says APPLIED_BY_ROOT_AFTER_OWNER_EDITS; its 26 appendices are present. `applied-authority-events-owner-integration.json` still has an older APPLIED_EXCEPT_COORDINATED_APPENDS status. The agent's final targeted consistency review was interrupted: verify each producer/subscriber list against the exact registry rows (especially Search versus Track usage) before declaring all event symmetry complete. Privacy executor assurance was corrected to bind approved Privacy generation, not invent universal human step-up. Generic Professional moderation permission is not inferred from a row.
2. **Canonical R064 wording was narrowed** to Identity-owned security/platform-role changes, preserving R031's no speculative Role stream/cache. Check other older cached-authority wording for stale references during final audit, not a new product choice.
3. **R074 applied** contextual `getCustomerContextDisplay.v1` and `getGigParticipationRequirements.v1` to owners/consumers. This addresses BF-007 and BF-075. R075 applied Hold typed action/source-readiness mapping; the old rail report's pending R070–073 Hold assumption is outdated (those rulings did not address Hold; R075 does).
4. **BF-220 remains a proposed architectural gap**, not adopted R076: Payment still describes tax-location facts as “Location/checkout evidence owner” around its §9 dependency row. R037 defines provenance but not the actual collector. Recommendation: Order owns private checkout tax-location evidence bound to quote/Order revision; Payment validates/maps it under tax policy; Location public/fuzzy/reveal output is never inferred tax evidence. Required field/validation/legal/provider rules remain external. Inspect both owner sides and apply only after review.
5. **BF-035 remains unintegrated**: Track already exposes `assignDefaultFreeTrack` (§10.6) and R030 free enrollment, but R069 lacks explicit Professional/Candidate actor-created fact or reliable post-creation command feeding it. Bind User/track/profile/revision and semantic identity with retry recovery; no new product choice.
6. **BF-265 is optional** Order-context prize-entry display. Sweepstakes has `getUserDrawingEntries`; no contextual Order projection is registered. Recommendation: explicitly keep optional contextual display disabled until its approved typed projection, without inventing a new required feature. Not yet a new ruling.
7. **BF-046/052/072/170** contain old Taxonomy exact-event/enumerator gaps. R070 applied enumerator/source descriptors; R069 source events must be compared before resolving any remaining vocabulary or stale source text. Do not blanket-close from an SH match.
8. **Bridge index candidate-title bug corrected:** `candidate_existing_rulings.title` had included the entire remaining ledger; root trimmed JSON title values to the first line. Candidate matches are unverified provenance only. Review index Markdown for stale derived formatting; do not use a candidate title match as semantic evidence.
9. **Privacy field/action coverage remains an activation requirement.** Generic protocol is defined under R020/057; actual field-by-field serializer/executor coverage is not proven by R070–073. The rail report's claim that those pending rulings would complete it is inaccurate. Preserve default-deny/unregistered-target behavior, full inventory completeness and external legal disposition; distinguish physical executor fixtures from missing architectural policy.
10. COM-13 contains physical migration questions for Order source XOR, Agreement legacy evidence, Booking nullable buyer/slot links and reserved states, Video URLs/course identity, Media version/upload representation and digital buyer context. Many semantics are already settled; review against those rulings and distinguish deferred physical representation from externally gated baseline/data migration. It has **not** been blanket-closed.

The original scratch helpers and upload paths are not required inputs. `close_families.py` was an integration convenience, not a canonical tool; edit canonical JSON with explicit provenance and run validators. Lane reports needed for recovery are saved in the repository.

## G. Ordered continuation from the earliest incomplete gate

| Work | Inputs | Expected output / acceptance | Safe next action |
|---|---|---|---|
| Gate 2 remaining families | handoff-adjudication.json, handoff-families.json, R048–R075, database-readiness.md | Each COM-13 row gets evidence-backed resolved/deferred/external disposition; CF-ROOT remains explicit until root artifacts exist | Review the eleven COM-13 source records as one migration family; do not migrate or request product approval for table naming |
| Gate 3 application finish | authority-event-contracts.md, lane-reports, actual owner pairs | Producer/subscriber registrations agree; applied markers and ledger reflect actual files; no unapproved scope | Finish interrupted R068/R069 targeted check, preserve existing owner edits |
| Gate 4 domain bridges | bridge-catalog/index, rails review, specific BF findings above | Complementary domain report covers all 190 families; integrated inventory covers all 563 records exactly once with owner/source/contract/obligations/failure/privacy/sequence/status; four rail matrices | Resolve BF-220, BF-035, BF-265 and Taxonomy candidate gaps, then merge with rails report; no matching-only closure |
| Gate 5 global reconciliation | Current owners, applied rulings, final bridges | Fresh report classifies conflicts/stale references/missing contracts/schema mismatch; no AI-resolvable actual conflict remains | Check whole-platform symmetry, rights, receipts, event identity, privacy and cycle-free sequencing |
| Gate 6 DB posture | database-readiness.md, schema/migrations, external evidence if supplied | D remains explicit or evidence supports A/B/C; one migration strategy owner | Preserve D unless actual target identity/data preservation/ledger/schema-only comparison arrives; continue unrelated work |
| Gate 7 root architecture | Reconciled owners/bridges, root shared-runtime obligations | `context/architecture.md` names global invariants and shared-runtime stewardship, no lifecycle takeover | Write only after cross-Cluster reconciliation; this will settle part of CF-ROOT |
| Gate 8 root plan / lanes | Root architecture, SH qualification, DB/external gates | `context/build-plan.md`, explicit dependency/parallel lane map, entry/exit/merge boundaries and first bounded slice | Separate sequential contract/foundation qualification from conditionally parallel consumers; do not demand entire upstream Cluster maturity |
| Gate 9 harness | AGENTS/CLAUDE, standards/guide, scripts, root plan | Traceable feature/lane completion, migration/contract change discipline and current progress; context checks cover intended invariants | Align harness to approved root sequencing; no feature runtime work just to simulate readiness |
| Gate 10 final validation | All above | Honest ready-for-controlled-parallel, sequential-only, externally-gated or not-ready result; exact next implementation slice | Run relevant checks and cold-start review; state unrun provider/runtime/DB checks; no blanket freeze |

## H. Operating instructions

Read [operating-policy.md](operating-policy.md), the binding 2026-10-12 instruction. Continue ordinary decisions/gates autonomously. Use AI_RESOLVED_WITH_PRODUCT_JUDGMENT for justified ordinary reversible/versioned defaults; record evidence, owner, reasoning, rejected alternatives, consequences, reversibility and artifacts. Validators require its provenance fields.

Reserve PRODUCT_OWNER_CHOICE for consequential changes to monetization/payers/fees/liability, major capabilities/business structure, materially different rights, significant privacy/data destruction, trust/safety or substantial strategic launch scope. First inspect rulings, owner, both bridge sides, comparable decisions and duplicates. Queue consequential choices; return only at ten, when all remaining work depends on them, when the gate cannot materially progress, or when the sweep is otherwise complete. External facts gate affected paths and do not stop unrelated work.

Adjudicate → canonical ledger → owner architecture → affected consumers/plans → validate → continue. One integration owner edits canonical ledgers. Parallel agents own disjoint files or return patches for sequential integration. Do not repeat historical audits, reopen P01–P19, overwrite another agent, or mark a document as implemented behavior. Keep source handoffs unchanged. Use logical commits; publishing authorization here is for this transfer, not main merge/deployment.

## I. Validation and known limits

At transfer preparation, all four structural check scripts passed with 10 Clusters, 34 Modules, 132 SH IDs, 661 decision records, 323 family-covered records and 563 hashed bridge records. Renderer reproduced current metrics. Whitespace check identified one trailing blank line in the ruling ledger and it was removed; final validation is recorded in `account-transfer-validation.json`.

Database facts: 177 models, 207 enums; one SQL migration creates 53 tables/31 enums; 124 mapped models lack checked-in CREATE TABLE coverage. This is not a deployed schema mismatch proof. No Prisma CLI validation, disposable replay, live provenance comparison, runtime tests, provider qualification, legal approval or deployment performed. No interface is frozen merely because architecture text exists.

`development-readiness-status.md`, `progress-tracker.md`, readiness-inventory fingerprints and lane reports contain dated checkpoints. Their old counts/stop reasons are historical. This transfer handoff and current machine ledgers identify the current stopping point; authority-by-concern is unchanged. The transfer does not certify the unfinished domain bridge review.

## J. Immediate next action

**The next Work agent should begin by…** reading this handoff and verifying the dedicated branch/transfer commit, then finish the interrupted R068/R069 producer/subscriber consistency check using `authority-event-contracts.md`, `lane-reports/authority-events-pending-propagation.json`, `lane-reports/applied-authority-events-owner-integration.json` and the exact owner paths in `context-map.md`. Confirm the 26 coordinated appendices are already applied rather than applying them twice. Correct only actual registration mismatches and update the integration report. Then adjudicate COM-13 as a family and resume the complementary domain bridge review at the named BF findings above. Expected edits are owner architecture before paired plans, integration report, canonical ruling/disposition only where warranted, and current metrics. Do not start by re-auditing all 10 Clusters.

Validate each meaningful batch with:

```bash
python scripts/render-handoff-progress.py
python scripts/check-context.py
python scripts/check-handoff-adjudication.py
python scripts/check-handoff-families.py
python scripts/check-bridge-catalog.py
git diff --check
```

Do not run migration/seed/reset, publish a production release, merge main or begin product features as part of resuming this readiness sweep.

## Publication outcome and portable fallback

The first transfer commit was saved locally as `2f05c0e` but Git push failed because no Git transport credentials were available (`could not read Username for https://github.com`). No dedicated remote branch was created. This handoff is followed by a recovery-record commit; the final exact local SHA is in the delivered package RECOVERY.md and final response. See [account-transfer-recovery.md](account-transfer-recovery.md). The delivered complete-history bundle is the usable transfer path until an authenticated environment pushes the branch. Do not mistake the repository/branch URL for verified publication. The original eight readiness commits plus transfer/recovery commits remain preserved without rewrite.
