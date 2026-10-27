# P0-C — fresh database evidence handoff

Updated 27 October 2026. **Posture D; fresh target identity/environment and empty application namespace verified; no writes or migration/replay performed.** Four provenance requirements have scoped verification, five have partial evidence and three remain pending. Current results and limits are in [Checkpoint 009](checkpoint-009.md).

## Fresh target verified

The owner supplied project `lyalfdmfheevpahywuhv`, URL `https://lyalfdmfheevpahywuhv.supabase.co`, for the existing fresh-development assignment. Supabase confirms **Workin Ants MVP**, organization **sayben codes**, us-west-2, creation 27 October 2026 UTC, and healthy status. SQL reports PostgreSQL 17.11. This ID and endpoint differ from the preserved June project.

Two read-only transactions confirm no tables/views/sequences in public/app, no app schema, no Prisma ledger anywhere in the captured namespaces and no Supabase migration history. Provider-managed Auth/Storage and other schemas remain intact; no claim about their record contents is made. The [fresh-target observation](database-observations/2026-10-27/manifest.json) preserves the exact queries, provider metadata and catalog/access evidence. No fresh baseline has been adopted.

Public RLS automation is enabled in metadata and its inspected definition covers public only. Default API CRUD grants for postgres-created public tables are removed; supabase_admin-created objects retain broad defaults, and function/PUBLIC execution still requires review. This verifies configuration facts, not working row policies, complete Data API exposure or safe application access.

## Preserved legacy target — historical observation

Supabase access is connected. The owner-supplied project `sdceenkakajslwpctbgl`, URL `https://sdceenkakajslwpctbgl.supabase.co`, is named Workin Ants in organization **sayben codes**. Provider metadata records creation on 2 June 2026 and region us-west-2. Three read-only SQL transactions collected catalog, effective privileges and the existing Prisma ledger; all ended with rollback. No raw application rows were read or exported.

This is the existing June application database: its 53 application table identities match the historical migration, and its Prisma ledger retains the same migration name and SHA-256 checksum as Git. It is not an empty application namespace or a separately created fresh target. Do not use it for clean replay, reset it, erase it, or mark it adopted. Data-preservation obligations remain unknown.

The [observation manifest](database-observations/2026-10-26/manifest.json) records actual supplied-target facts separately from the 12 requirements for a fresh target. RLS is disabled on all 53 app tables, while effective schema and SELECT/INSERT/UPDATE/DELETE grants are absent for anon, authenticated and service_role. Live Data API configuration/behavior is unverified; do not repeat the generic table tool's claim that these tables are necessarily publicly accessible. The retained advisor findings and public event-trigger definition require review, not automatic remediation.

## Next action — Work-owned candidate review

No further target ID, project creation or pasted credential is needed for safe source review. The owner has already created and identified the fresh project. Work now reconciles the physical candidate against the existing 177-model inventory, 12 compatibility cases and architecture-required storage, following the existing greenfield strategy. Preserve all historical migrations and the legacy target; do not apply the June migration or current Prisma schema as an assumed fresh baseline.

Actual backup/restore settings, retention/preservation obligations and any destructive disposable-replay action still require their own evidence and applicable authorization before affected execution. Continue independent candidate/security design work around those limits. Do not convert the project-name suffix MVP into public-release authorization.

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

DBP-01, DBP-02, DBP-04 and DBP-05 are VERIFIED for their stated identity/environment/catalog scope. DBP-03, DBP-06, DBP-07, DBP-08 and DBP-11 are PARTIAL with explicit limits. DBP-09, DBP-10 and DBP-12 remain NOT_OBTAINED. The catalog probe has now run read-only on each separately identified target; neither observation establishes migration baseline adoption, replay, RLS behavior or production readiness.
