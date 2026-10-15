# Copy-ready bootstrap for the receiving Work account

Copy the prompt below into a new Work thread with GitHub access to `saybenn/Workin-Ants-V2`.

---

Resume **Workin Ants Development Readiness orchestration** from the transferred repository state. You have no prior conversation memory; the repository is the continuity source. Do not implement product features yet.

1. Read `context/reconciliation/account-transfer-handoff.md` **first** from branch `codex/development-readiness-2026-09-29`. Repository: `https://github.com/saybenn/Workin-Ants-V2`. Do not use main as the readiness snapshot.
2. Fetch safely and establish branch, HEAD, remote branch SHA and working tree. The stable base is `55c0036715ec6bdec2c61b43811f251fee32d7e9`; the transfer is a descendant. Locate its exact commit with `git log -1 --format=%H -- context/reconciliation/account-transfer-handoff.md`. Compare that snapshot with current remote HEAD; inspect any later commits and preserve them. Never reset, force-push or overwrite another agent's work to make the snapshot match.
3. Read `AGENTS.md`, `CLAUDE.md`, `context/context-map.md`, `context/reconciliation/operating-policy.md`, current machine ledgers and canonical rulings. Resolve exact Module/Cluster paths through the map. Use the handoff's decision index to read full P01–P19 clarifications in `product-owner-decisions.md` and `platform-architecture-rulings.md`. Do not reopen them or treat historical recommendations as approvals.
4. Current transfer checkpoint: 10 Clusters/34 Modules; SH-001–SH-132 permanent; 661 decision records with 638 adjudicated, 23 partial, zero pending; two canonical architecture concerns still partial plus scoped external gates. These are snapshot counts: recompute, do not assume. Bridge extraction covers 563 records/268 boundary facets; only the 78-family rails review is complete as a report. The 190-family domain review is unfinished. No interface freeze or active implementation lane is certified.
5. Begin with the handoff's **Immediate next action**: finish the interrupted R068/R069 exact producer/subscriber check. Use `authority-event-contracts.md`, `lane-reports/authority-events-pending-propagation.json`, `lane-reports/applied-authority-events-owner-integration.json` and current owner pairs. The 26 coordinated appendices were already applied by root; do not duplicate them. Preserve R031's no speculative Role stream/cache and Privacy's owner-bound verification policy. Update stale integration report status only after checking actual files.
6. Then resolve the COM-13 migration-representation family against existing rulings without running migrations. Continue the domain bridge review at BF-220 checkout tax-location ownership, BF-035 actor-created/default-Free Track handoff, BF-265 optional Order prize-entry projection and the Taxonomy event/enumerator facets named in the handoff. These are unintegrated findings, not approvals. R074 contextual Customer/Gig queries and R075 Hold scope/readiness have already been applied.
7. Proceed autonomously through Gates 2/3 → full bridges/rail matrices → fresh platform reconciliation → database posture → root architecture → root build plan/lane map → harness → final readiness. Do not restart settled audits or stop at ordinary gates. Root architecture must follow final cross-Cluster convergence.
8. Follow `operating-policy.md`: ordinary sound reversible/versioned product defaults may be AI_RESOLVED_WITH_PRODUCT_JUDGMENT. Record evidence, owner, rationale, alternatives, consequences, reversibility/configurability and affected files. Reserve consequential owner choices for the specified monetization/rights/privacy/safety/business-scope categories after searching existing rulings and both bridge sides. Queue/batch them at ten or the documented dependency/sweep limits. External legal/provider/database facts gate affected paths; continue unrelated work. There is no current owner decision packet awaiting answers.
9. Maintain one canonical ruling/disposition integration owner. Parallel architecture work may use disjoint ownership or report/patch-only lanes. Product implementation parallelism requires a qualified root lane map, stable contracts, schema/merge ownership, fixtures and integration gates; reviews running in parallel do not prove those conditions. Preserve permanent SH IDs and all historical source evidence.
10. Apply decisions before reporting them: ruling → owner architecture → consumers/plans → traceability → validation. Update `handoff-adjudication.json`, `handoff-families.json` and derived metrics only when actual evidence supports closure. Do not equate grouping with closure or ADJUDICATED with implemented behavior. Run:

```bash
python scripts/render-handoff-progress.py
python scripts/check-context.py
python scripts/check-handoff-adjudication.py
python scripts/check-handoff-families.py
python scripts/check-bridge-catalog.py
git diff --check
```

11. Database posture D remains external: actual environment identity, preservation constraints, migration ledger and schema-only comparison are needed before choosing baseline/continuation/recovery. Never reset a database or infer live mismatch from static table counts. One integration owner sequences migrations. Do not expose credentials or private provider/connection details.
12. Commit logical authorized local batches on the dedicated branch. The prior user authorized pushing the transfer branch, not merging main or deployment. Do not force-push, rewrite history, delete branches, deploy, execute destructive migrations, or begin full product development. Finish with honest readiness classification and an unambiguous next bounded implementation slice, including what can later run in parallel and which external gates remain.

Your job is to continue from the recorded unfinished contracts, not reconstruct the project from scratch. If GitHub is newer than this handoff, reconcile the delta by concern and preserve later work before proceeding.

If the dedicated branch is not yet on GitHub: the source push was blocked by missing Git transport authentication. Upload/extract the delivered `Workin_Ants_Account_Transfer.zip` in this Work thread and follow `RECOVERY.md` to clone its full-history bundle. Verify exact HEAD, set the original GitHub remote, then use the same bootstrap above. Publish from an authenticated environment without forcing or rewriting history; do not recreate the project from main alone.
