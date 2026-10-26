# P0-C — fresh database evidence handoff

Prepared 26 October 2026. **Posture D; no target contacted and no provisioning, migration, seed, reset or replay performed.** This turns the existing 12-item requirement ledger into a concrete next action. It does not create a second migration plan or approve the current 177-model schema as a baseline.

## First action for the WorkinAnts account/environment owner

Identify the brand-new, development-only database/project to evaluate. Supply its nonsecret project identifier, provider, region, intended use, account owner, creation date and separation from the old target. State whether either target holds data that must survive and who can approve disposal. Never send passwords, tokens, connection strings or customer records in chat or commit them to Git. Use the approved secret channel for eventual limited technical access.

The account owner does not need to decide database architecture. Work/the migration integrator handles catalog collection, ownership reconciliation, migration design and tests after the actual target and access are available. The earlier approval of clean isolation is already recorded; do not ask the client to redesign it.

## Read-only evidence collection after target identity is verified

The database steward can inspect [the prepared catalog query](../../scripts/collect-database-provenance.sql) and run it manually in the confirmed isolated target's SQL console. It opens a read-only transaction, inspects system catalogs and rolls back. It reads no application rows, executes no migration and does not connect itself. Review output before sharing. Do not point it at the old target merely because an old connection is available.

Attach the resulting JSON to the controlled engineering handoff together with:

1. The target identity/isolation and preservation facts above (**DBP-01–03**).
2. Actual provider/Postgres/extension/managed Auth details and the catalog output (**DBP-04, 06–08**). The probe covers structure, grants, policies, ownership, role membership and privileged-function signatures/configuration fingerprints. It deliberately excludes function bodies and view definitions; the integrator must review those separately in a safe channel before approving security or full structural parity. Object absence, access errors or insufficient visibility remain gaps.
3. The actual migration ledger (**DBP-05**). If the catalog confirms an application-owned `_prisma_migrations` table, the steward may separately export only migration names, checksums, start/finish/rollback times and applied-step counts from that exact qualified table. Do not export logs or application rows. If absent, record actual absence. No object or ledger presence/absence proves that application tables contain no records.
4. Account/provider backup and restore settings, retention, secret-access/handover and synthetic-fixture obligations (**DBP-11**). A retention proposal is not approved policy and the catalog cannot prove backup deletion.

## Work-owned review and later exit criteria

**DBP-09:** Reconcile the existing [177-model ownership/security inventory](greenfield-model-security-inventory.json), 12 compatibility cases and architecture-required representations. Current Prisma validation proves syntax/relations only. Preserve the screening Order source separation, explicit Media joins, canonical owner repositories and actual generation/economic-effect constraints.

**DBP-10:** Pin the actual disposable replay target, reviewed candidate schema, exact Prisma CLI, one ordered migration/RLS history and safe fixtures. Candidate DDL review precedes execution. Preserve historical migration checksums. The complete replay must prove no pending migrations on a second deploy, full catalog parity, allowed/denied role behavior, constraints, concurrency and safe failure recovery. Do not use reset, db push or a fabricated applied ledger to hide gaps.

**DBP-12:** Record an evidence-supported adoption decision and exact source/migration/RLS/build versions. The current query and handoff do not satisfy this item. Only actual reviewed evidence can change posture D. P0-D database-backed runtime tests, P0-E permissions/RLS and P0-F actual Privacy execution remain dependent on their relevant real prerequisites.

All 12 ledger items remain `NOT_OBTAINED` until the responsible owner supplies and reviews actual evidence. The probe is prepared and **not executed**; this is no database or security qualification claim.
