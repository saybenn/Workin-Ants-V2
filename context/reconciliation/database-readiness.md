# Database readiness

Date: 2026-09-29. Evidence: baseline `526bb1ab30480d66ca8b7da08d16badc6e613c1d`.

**Ruling: D — blocked pending external database evidence, for deployment/baseline decisions.** This does not stop read-only analysis, architecture reconciliation, or offline harness work.

## Verified repository facts

- Prisma declares 177 models and 207 enums.
- One SQL migration, `20260602021702_phase_2_database_truth_layer`, creates 53 tables and 31 enums.
- Static mapping of model `@@schema`/`@@map` to SQL CREATE TABLE statements identifies 124 model tables without a checked-in creation statement.
- This is structural coverage, not a live database comparison or replay proof. Equal counts would not prove column, enum-value, FK, index, trigger, function or RLS parity.
- `docs/phase-2-database-truth-layer.md` records a previous live Supabase database and past migrate-status/seed/integrity checks. It explicitly records no disposable replay. These are historical claims, not checks rerun now.
- The product overview says greenfield MVP planning. That does not establish that an existing database is disposable.
- Current `OrderSourceType` and participant structure do not yet represent the approved screening source. Architecture permission is not deployed structure.

## Required evidence before selecting A, B or C

Obtain the intended database/environment identity, whether its data must survive, its migration ledger and a schema-only structural comparison. No table-row/customer-data export is required for this decision. Compare that evidence with Git history before choosing a new baseline, continuation, or history recovery. Never reset/drop the existing database to make the repository appear consistent.

## Coordinated migration policy

One integration owner sequences all shared-schema changes. A feature lane proposes its owned model/constraint change with architecture evidence and contract impact; it does not independently publish or apply competing migrations. The integration owner reconciles proposals against current main, authors the ordered migration, proves disposable replay and preservation of required existing data, and updates the source schema atomically with the migration checkpoint.

Shared-model changes require all affected owner/consumer contracts to be reconciled first. Enum reuse does not transfer lifecycle ownership. Historical migrations are not rewritten after use. Real deployment and destructive operations require their own authorization; this readiness task performs neither.

## Validation remaining

Prisma CLI validation, clean disposable database replay, full structural diff and live provenance reconciliation have **not** been performed by this audit. No live credentials were accessed and no migration/seed/db-integrity command was run against Supabase.

## COM-13 source review — 2026-10-15

WA-R076 adjudicates all eleven source records: ten physical representation details are deferred with explicit owner invariants; CL04-U048 remains an external migration-provenance requirement. This closes the COM-13 architecture family, not its implementation or database activation. Posture D is unchanged. The historical 177-model/53-table coverage evidence still does not prove a live mismatch. No schema, migration SQL, environment or database data was changed in this review.

## Gate 6 posture confirmation — 2026-10-16

Repository-only checks reconfirm 177 models / 207 enums, one SQL migration creating 53 tables / 31 enums, and 124 mapped models without a checked-in CREATE TABLE. Schema and migration bytes are unchanged from `731491b393df205478c012bd2d5998ca08181ed2`. Evidence: database-posture-confirmation-2026-10-16.json.

**Gate 6 posture confirmation is complete; posture D remains externally gated.** No live environment, migration ledger, structural comparison, disposable replay, Prisma CLI validation, migration/seed/reset or credentials check was performed. This is not database readiness for implementation or deployment. Required environment identity, preservation obligations, ledger and schema-only comparison remain outstanding. Gate 5 permits root architectural synthesis despite this scoped limitation; root may not choose A/B/C, migration baseline or destructive policy.
