# P0-C — fresh database evidence handoff

Updated 26 October 2026. **Posture D; supplied existing target inspected read-only; no provisioning, migration, seed, reset or replay performed.** The fresh-target verification requirements are still unsatisfied. Current results and limitations are in [Checkpoint 008](checkpoint-008.md).

## Supplied target and verified access

Supabase access is connected. The owner-supplied project `sdceenkakajslwpctbgl`, URL `https://sdceenkakajslwpctbgl.supabase.co`, is named Workin Ants in organization **sayben codes**. Provider metadata records creation on 2 June 2026 and region us-west-2. Three read-only SQL transactions collected catalog, effective privileges and the existing Prisma ledger; all ended with rollback. No raw application rows were read or exported.

This is the existing June application database: its 53 application table identities match the historical migration, and its Prisma ledger retains the same migration name and SHA-256 checksum as Git. It is not an empty application namespace or a separately created fresh target. Do not use it for clean replay, reset it, erase it, or mark it adopted. Data-preservation obligations remain unknown.

The [observation manifest](database-observations/2026-10-26/manifest.json) records actual supplied-target facts separately from the 12 requirements for a fresh target. RLS is disabled on all 53 app tables, while effective schema and SELECT/INSERT/UPDATE/DELETE grants are absent for anon, authenticated and service_role. Live Data API configuration/behavior is unverified; do not repeat the generic table tool's claim that these tables are necessarily publicly accessible. The retained advisor findings and public event-trigger definition require review, not automatic remediation.

## First action for the WorkinAnts account/environment owner

Select the organization for a separate development-only project; the recommended organization is the existing **sayben codes**. Work must check the actual creation cost and obtain any required cost approval before provisioning. Alternatively, supply an already-created fresh development project. Preserve the supplied existing target. Do not ask for its ID again or request credentials in chat.

For the fresh target, Work collects provider identity/region/creation metadata, verifies its separation and checks actual namespace/ledger/security state. The account/data owner confirms purpose and any preservation/disposal obligations that technical evidence cannot establish. Supabase-managed schemas are preserved even on a fresh project.

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

All 12 ledger items remain `NOT_OBTAINED` for qualification of the separate fresh target. The catalog probe has been executed only against the owner-supplied existing project, and its output is retained separately; it has not qualified a fresh database, migration baseline or security behavior.
