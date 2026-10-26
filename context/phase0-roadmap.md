# Master roadmap and Phase 0 continuation

Recorded 26 October 2026 from the project owner's supplied 20-step roadmap. [The root build plan](build-plan.md) remains the detailed construction sequence. [Launch scope](reconciliation/launch-scope-baseline.md) supplies the approved first-release restrictions. Progress and validation record actual evidence separately.

| Step | Work | State |
|---|---|---|
| 1 | Project overview | Done |
| 2 | 132 Shared Operations | Specified; runtime qualification separate |
| 3 | 10 Cluster architectures | Done |
| 4 | 10 Cluster build plans | Done |
| 5 | 34 Module architectures | Done |
| 6 | 34 Module implementation plans | Done |
| 7 | Cluster reconciliation | Done |
| 8 | Handoff extraction | Done |
| 9 | Shared Operations refresh | Done |
| 10 | Shared Operations rulings | Done |
| 11 | Handoff decisions | Architecture complete; outside legal/provider/database requirements tracked and still require actual evidence |
| 12 | Apply approved decisions | Done for the architecture baseline; new scope decisions recorded separately |
| 13 | Cross-Cluster bridges | Done |
| 14 | Platform reconciliation | Done |
| 15 | Resolve architecture conflicts | Done for the reconciled baseline |
| 16 | Root architecture | Done |
| 17 | Root build plan | Done |
| 18 | Predevelopment validation | Actual foundation qualification unfinished |
| 19 | Codex harness | Prepared; actual runtime proof pending |
| Phase 0 | Qualify the real foundation | Current phase; precedes Step 20 |
| 20 | Authorized feature development | Not authorized |

## Required Phase 0 order

1. **P0-A — Architecture and contract preparation.** Preserve completed specifications/offline tests for all 132 operations. Do not restart architecture reconciliation or equate fixtures with production handlers.
2. **P0-B — Clean app and toolchain.** Checkpoint 006 passed functional checks. Recheck current advisories, remediate the exact dependency graph with a reviewed bounded diff, then repeat clean install, lint, strict typecheck, build, dev/production route and security regressions. Current results belong in the Phase 0 evidence, not in overwritten historical results.
3. **P0-C — Database foundation.** Use the preferred fresh, isolated development target. Obtain the 12 actual provenance items, reconcile physical constraints/owner boundaries, review one migration/security history and prove disposable replay, structural parity and role-specific denial. Posture D persists until evidence supports a recorded change. Existing database write aliases remain blocked.
4. **P0-D — Shared runtime.** Qualify canonical command/inbox/outbox/job/lease/CAS/reservation/proof machinery on proven Postgres prerequisites. Exercise replay/conflict, crash/reclaim, fences, economic-effect uniqueness, unknown external outcomes and safe retry. An in-memory model does not satisfy this step.
5. **P0-E — Permissions and security.** Prove actual registered owner/consumer adapters, action/purpose/field scopes, current membership/revocation, proof-before-disclosure, denial and server/RLS parity.
6. **P0-F — Privacy and protected data.** Map real owner fields/actions/vendors and approved retention; test actual export bytes, erasure/retained dispositions, generation receipts and failure/backup/restore behavior. Draft policies do not establish lawful production timers or vendor deletion capability.
7. **P0-G — Integration and final qualification.** Exercise the actual required producer/consumer paths and applicable provider/legal capabilities; pin the qualified subset. Revisit readiness and separately authorize only development paths whose prerequisites pass.

Legal drafting and UI work may proceed independently. Their drafts do not clear engineering gates. Vendor onboarding occurs when the relevant integration requires it. A scoped external block does not reopen finished Steps 1–17 or permit bypassing a dependency. At the current baseline there are eight candidate lanes and zero authorized lanes, zero runtime-qualified/frozen operations, and no public-release authorization.
