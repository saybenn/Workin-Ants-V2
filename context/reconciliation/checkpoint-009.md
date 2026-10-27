# Checkpoint 009 — fresh Supabase identity and empty application namespace verified

Prepared 27 October 2026. **P0-C advanced; posture D remains.** This checkpoint verifies metadata and the pre-migration application namespace. It does not select, generate or apply a migration baseline, qualify RLS behavior or authorize feature development.

## Verified target

Owner-supplied project **lyalfdmfheevpahywuhv**, URL **https://lyalfdmfheevpahywuhv.supabase.co**, is confirmed by the connected provider as **Workin Ants MVP** in organization **sayben codes**, region **us-west-2**, ACTIVE_HEALTHY. Creation timestamp: **2026-10-27 01:54:00.623595 UTC**. Provider release: **17.11.0.003**; actual server version: **PostgreSQL 17.11**. This project is distinct from the preserved existing June project sdceenkakajslwpctbgl.

Read-only catalogs confirm no public/app application tables, views, materialized views, sequences or foreign tables. The app schema is absent. No Prisma migration ledger relation appears in the captured namespaces; the Supabase migration tool reports an empty history. This proves an empty application namespace at collection time, not absence of Auth users, stored files or other provider-managed records. Those records were not read or erased.

Installed extensions and versions: pg_stat_statements 1.11, pgcrypto 1.3, plpgsql 1.0, supabase_vault 0.3.1, uuid-ossp 1.1. Provider-managed Auth/Storage/Realtime/extension and other schemas remain outside application ownership.

## Security defaults actually observed

For objects created by **postgres** in public, default SELECT/INSERT/UPDATE/DELETE grants to anon/authenticated/service_role are absent. Other table privileges such as TRUNCATE/REFERENCES/TRIGGER/MAINTAIN remain. For **supabase_admin**, broad default table and sequence grants remain. A toggle must therefore not replace creator-specific privilege review in the adopted migration history.

The enabled ensure_rls event trigger calls public.rls_auto_enable(). Its inspected definition enables RLS for newly created **public** tables only. The trigger catches/logs errors; installed configuration alone does not prove successful behavior. No test table was created. Future app-schema tables still require explicit reviewed RLS/grant setup.

The public function is SECURITY DEFINER, returns event_trigger and has a pinned pg_catalog search_path. Anon/authenticated have EXECUTE privilege, and the security advisor returns the corresponding two warnings. Ordinary RPC invocation/reachability or exploitability was not established, and no function was invoked or changed. [Anonymous grant advisor](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable); [authenticated grant advisor](https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable).

Live Data API exposure settings, actual role policy behavior, field/purpose authorization and server-owner checks remain unverified. Administrative catalog collection as postgres is not a browser-role or least-privileged owner runtime test.

## Provenance requirement disposition

| Requirement | State | Evidence and limit |
|---|---|---|
| DBP-01 target identity | VERIFIED | Exact provider ID/URL, distinct from old target; no adoption inferred |
| DBP-02 environment/isolation | VERIFIED | Owner-designated Phase0 purpose, provider organization/region and distinct logical project/endpoint; no physical provider-infrastructure isolation claim |
| DBP-03 preservation | PARTIAL | Preserve legacy and provider-managed objects; no disposal authorized; backup/retention obligations still unverified |
| DBP-04 version/managed objects | VERIFIED | Actual server/extension/catalog evidence; managed objects excluded from app ownership |
| DBP-05 ledger/namespace | VERIFIED | Empty application namespace and no migration histories; no claim about managed record contents |
| DBP-06 structural comparison | PARTIAL | Pre-migration catalog captured; candidate and post-replay parity pending |
| DBP-07 privileged objects | PARTIAL | Signatures/ownership/trigger metadata and public trigger definition reviewed; adopted app object design pending |
| DBP-08 API/grants/RLS | PARTIAL | Creator-specific defaults and trigger configuration captured; API/role/RLS behavior pending |
| DBP-09 physical source candidate | NOT_OBTAINED | Existing 177-model routing and 12 compatibility cases are specifications; actual candidate reconciliation pending |
| DBP-10 disposable replay | NOT_OBTAINED | No replay target/action or execution proof |
| DBP-11 backup/restore/access | PARTIAL | Connected access and sanitized capture proven; backup/restore/retention evidence pending |
| DBP-12 adoption decision | NOT_OBTAINED | No reviewed baseline/schema/RLS/replay adoption |

VERIFIED applies only to the named requirement and its limits. Four scoped requirements are verified, five are partial and three remain pending; this is not four twelfths of production readiness.

## Next Work-owned action

Continue the existing [greenfield strategy](greenfield-database-strategy.md) at its candidate gate. Reconcile the [177-model ownership/security inventory](greenfield-model-security-inventory.json), 12 compatibility cases and architecture-required source/economic-effect/generation/shared-runtime/Privacy storage against current owner contracts. Preserve original migration checksums and source authority. Do not replay the June migration or blindly deploy the present Prisma schema into the fresh project.

Candidate approval precedes DDL generation, review, ordered migration/security history, disposable replay, complete structural comparison and actual allowed/denied role/invariant tests. Backup/restore/preservation obligations and permission for affected destructive replay actions must be resolved before those actions. No new target ID, account creation or pasted credential is needed for independent source review.

P0-B remains passed within its prior recorded scope. P0-C posture D remains; P0-D persistent runtime, P0-E security, P0-F Privacy and P0-G integration still await their prerequisites. All 132 operations remain runtime-unqualified/unfrozen, zero lanes are active and Step 20 is unapproved. Legal drafts, vendor/legal requirements and UI remain separate bounded work.

## Evidence and execution boundary

The [fresh-target observation manifest](database-observations/2026-10-27/manifest.json) fingerprints provider metadata, full catalog, explicit default-grant/access review, table/migration summaries, advisors and exact SQL. Two read-only transactions ended with rollback. No application-row read, key retrieval, DDL/DML, migration, seed, reset, replay, provisioning or provider configuration change occurred. The prior existing-target packet is unchanged; this turn contacted only the newly supplied target.

Repository source begins at Checkpoint 008 ee973d01cebf2d69f05ad0efb37366f9b08fb2e3. Static validators now accept scoped fresh-target evidence while rejecting altered identity/catalogs, nonempty application namespace, non-read-only capture and premature baseline/replay approval. Product/framework/dependency/schema/migration/owner-contract/UI source bytes are unchanged.

Validation passed: context, foundation, **34 adversarial mutations** and diff hygiene. [Exact validation output](checkpoint-009-validation.json) records commands and scope. Recovery identities are retained in the delivered checkpoint manifest; no remote push, merge or deployment is claimed.
