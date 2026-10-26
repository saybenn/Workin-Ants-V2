# Checkpoint 008 — Supabase access verified; supplied target is the existing database

Prepared 26 October 2026. **P0-C remains externally gated, posture D.** Connected access is verified. No database or provider configuration was changed, and no project was created.

## What the actual evidence establishes

The project owner supplied `sdceenkakajslwpctbgl` and `https://sdceenkakajslwpctbgl.supabase.co`. Supabase confirms that exact ID and URL, project name **Workin Ants**, organization **sayben codes**, region **us-west-2**, healthy status and creation at **2026-06-02 00:10:38 UTC**. The provider release is 17.6.1.127; the database reports PostgreSQL **17.6**.

The application namespace already contains **53 tables, 31 enum types, 432 columns, 143 constraints and 184 indexes**. Table identities match the June migration's 53 created tables. This is a table-name comparison, not proof of complete column/constraint/security parity.

The actual `public._prisma_migrations` row records `20260602021702_phase_2_database_truth_layer`, finished 2 June 2026 with one applied step and no rollback. Its checksum, `5b4f44a1b1f989743df227c487a6ecb3dd793e9915d9a635d8e32b99304b2055`, matches the checked-in migration bytes. The Supabase migration tool separately returns an empty Supabase-managed migration history; that does not erase or contradict the Prisma ledger. Table-tool row estimates, including its zero estimate for the migration table, are not emptiness proof.

**The supplied project is therefore the existing June application database. It does not satisfy the planned separate fresh-target requirement.** No conclusion about the presence or absence of application records or permission to discard data follows.

## Read-only collection and retained evidence

Three explicit read-only SQL transactions collected catalog structure, effective grants and sanitized migration metadata; each ended with rollback. Catalog/access outputs record `transaction_read_only = on`. Queries read system catalogs and the migration ledger, not application/customer rows. No key retrieval, application-row export, DDL, DML, seed, reset, migration, provisioning, RLS change, API behavior test or provider activation occurred.

The [observation manifest](database-observations/2026-10-26/manifest.json) fingerprints retained provider responses, catalog, access review, ledger, advisors, table summary and the exact queries. It records collection scope rather than approving an environment. The system event-trigger definition retained in the access review was inspected as data; it was not invoked or applied.

## Security findings and limits

All **53 app tables have RLS disabled**, with no app row policies. Effective `USAGE` on schema app and SELECT/INSERT/UPDATE/DELETE on every app table are **absent for anon, authenticated and service_role**. This contradicts the table tool's generic assertion that disabled RLS alone proves those tables are fully exposed. Live Data API exposure settings and behavior were not available through the retained database settings and remain unverified. No public-key request or customer-data access was used to test exposure.

The security advisor reports an informational no-policy finding for the private Prisma ledger and warnings about anon/authenticated EXECUTE grants on `public.rls_auto_enable()`. The retained function returns `event_trigger`, is SECURITY DEFINER with `search_path = pg_catalog`, and is attached to an enabled DDL event trigger. The grants are recorded; ordinary RPC reachability or exploitability was not established. Do not blindly enable RLS, add permissive policies, remove a provider trigger or change grants under this observation assignment.

Public-schema default privileges grant broad future-object privileges to browser roles for postgres/supabase_admin-created objects. The event trigger's RLS automation covers public, not app. These are inputs to a reviewed future privilege/migration design, not permission to reuse the old environment or a claim of production security qualification. Administrative collection as postgres/BYPASSRLS proves no browser/server-role authorization behavior.

Advisor references: [private RLS without policy](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy), [anonymous SECURITY DEFINER grant](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable), [authenticated SECURITY DEFINER grant](https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable). Primary access-control reference: [Supabase API security](https://supabase.com/docs/guides/api/securing-your-api).

## Next concrete step

Use a separate development project; suggested name: **Workin Ants Phase0 Dev**, suggested organization: **sayben codes**. The owner must select the organization before the creation-cost lookup. Check the actual quote and obtain any required cost approval before provisioning. No creation price, region choice, project capacity or approval is assumed from the existing organization's free plan. Alternatively, the owner can identify an already-created fresh isolated project.

Work then verifies that new identity, preservation obligations, namespace and ledger, reconciles the candidate model/security design, and follows the existing reviewed migration/replay sequence. Keep the supplied project intact. All 12 qualification requirements remain open for that fresh target; existing-target observations are recorded separately to avoid falsely closing them.

P0-B stays qualified in its recorded bounded scope. P0-D persistent runtime, P0-E security/RLS, P0-F Privacy execution, P0-G integration and Step 20 feature development remain unqualified/unapproved. No contract was frozen and no parallel lane activated.

## Repository continuity and verification scope

This continuation restores from the available independently verified Checkpoint 007 copy at `d39da52c46088f3ddee56943c91dbf0f5984e4c1`. The earlier local target-receipt commit `801e09d` is reported in the conversation but absent from that recovery bundle; the owner's ID/URL and its now-superseding actual evidence are carried forward here. No published history was rewritten.

Static validation now distinguishes a fingerprinted read-only existing-target observation from write authorization or fresh-target qualification. It rejects missing/changed evidence, changed project identity, non-read-only capture, writes, premature adoption and invented fresh-target approval. The framework/application/schema/migration/dependency bytes and historical P0-B results are unchanged; no new build or runtime qualification is claimed.

Validation passed: `python scripts/check-context.py`, `python scripts/check-foundation.py`, `python scripts/check-phase0-negative.py` (**29 rejected mutations**) and `git diff --check`. The initial context check rejected a status note in the pinned historical greenfield strategy; removing that note preserved the approved basis fingerprint. Current findings remain in this checkpoint and the live handoff. [Exact validation output](checkpoint-008-validation.json) retains the checks and scope.

The recovery-bundle identity is recorded in the checkpoint manifest delivered with this checkpoint. Local commits and bundles are not a remote push, main merge or deployment.
