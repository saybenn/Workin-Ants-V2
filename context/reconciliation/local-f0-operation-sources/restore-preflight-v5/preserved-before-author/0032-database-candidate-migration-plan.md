# Coordinated migration, replay and adoption plan — not executed

> Current amendment P0-C-03A: [corrected SQL source review](foundation-sql-draft-review.md) and [retained directive](directives/brain-directive-p0-c-03a.md) supersede earlier drafting-stage gaps/next actions in this historical source plan. Source and SQL drafts only; posture D; all 451 database/runtime cases NOT_RUN. Independent Identity currentness, narrowly enumerated read-only Boolean ports, append-only age evidence and both added owner revisions are present for re-review, not execution-approved. No human setup task.

## Selected execution path

Use the installed, pinned **Prisma 7.10.1 Migrate SQL history** as the sole application schema/security executor. Each adopted migration.sql contains both structural SQL and reviewed grants/RLS/functions/triggers/checks/indexes. Supabase CLI/MCP must not independently apply application DDL or maintain a competing application history. They may later inspect provider state or help run explicitly approved local parity tests; they are not another migration owner.

Preserve prisma/schema.prisma and prisma/migrations/20260602021702_phase_2_database_truth_layer/migration.sql unchanged as historical evidence. Neither is the selected fresh-project execution path. Never run that June migration on the new target by default, mark it applied to simulate a baseline, db push, reset, or use a live/shadow introspection shortcut.

The review full schema is the staged physical target, not one first-deploy command. **The first proposed application cut is foundation-candidate.prisma: 40 parent-FK-closed models.** The remaining reviewed models are later owner-ordered migrations, with child-directed/prize launch-disabled stages explicitly preserved. An enum or table in a review file is not feature activation.

## Tooling and safe source generation

Current tool evidence: Node 24.22.1, npm 11.9.0, Prisma/client 7.10.1. Existing lock and P0-B security disposition are preserved. Offline review configs import only defineConfig and set a source schema path; neither loads dotenv, a datasource URL, migrations or a shadow database. The candidate has no client generator. Installed validate/help were inspected before use. This review ran validate, never migrate diff/deploy/dev, db push, introspection or db execute.

After Brain approves the exact source hashes, request **source-only SQL generation**, using the pinned binary and the environment-free config:

```bash
node node_modules/prisma/build/index.js migrate diff \
  --from-empty \
  --to-schema prisma/review/foundation-candidate.prisma \
  --config prisma.foundation-review.config.ts \
  --script \
  --output review-output/foundation-structure.sql
```

This is a proposed future command, **NOT RUN**. It has no datasource, migrations or shadow input. Review the complete generated SQL, then add the selected SQL-companion requirements before anything is executable. This command would produce a review draft, not adopt a history or grant execution permission.

Prisma's live unversioned documentation now redirects some workflow pages to a newer command family. That does not upgrade this repository. The inspected 7.10.1 CLI still exposes migrate deploy and the source-diff flags above. Use [versioned v7 unsupported-feature guidance](https://www.prisma.io/docs/orm/v7/prisma-migrate/workflows/unsupported-database-features) and installed help. Do not substitute newer db migrate/contract commands or use migrate dev --create-only, which can require a shadow/live database.

## One application history and ownership bootstrap

The future adopted application history is **prisma/foundation/migrations/** with an explicitly selected foundation schema/config. That directory/config does not exist yet as an execution path. The integration owner assigns migration IDs only after review and preserves exact generated/edited bytes, checksums and source hashes. Every later owner migration appends to this same history; the current root historical history remains inactive for this target.

Before application migration, an approved environment bootstrap creates only the narrowly defined deployment/runtime/issuer/helper roles and application namespaces. It is versioned and fingerprinted as an environment prerequisite. It creates no domain tables or alternate application ledger and does not alter provider-managed ownership. Runtime/worker never receive owner membership or DDL authority.

The migrator maintains its private Prisma metadata ledger in public. Its creator defaults grant no API access; the provider's public auto-RLS behavior is captured and tested. Only the migrator owns/updates that metadata; it is a documented deployment exception, not a business source or browser table. App/platform tables and private functions are created under explicit transaction-local wa_schema_owner ownership. The owner has only the approved namespaces. Remove/review redundant generated CREATE SCHEMA statements when bootstrap already owns those namespaces; record that draft edit before execution.

Every initial application migration is explicitly transactional. Within it, install reviewed table/type structure, immutable/context/source constraints, policies and privileges before commit. All objects remain internal; there is no public API exposure window. Transaction-local ownership ends before the engine updates its own ledger. Context helpers may be assigned the separate nonlogin helper owner with bounded SELECT only, never grant writes. Issuer grants require immutable nonnullable login/PID/xid at INSERT; runtime/worker receive helper EXECUTE only. The READ COMMITTED tuple-capture / separate issuer COMMIT / helper-validate order precedes business reads and source locks; rollback and savepoint reuse must fail the later real P0-C tests. The role bootstrap and any provider-setting exception are separate object scopes under the qualification manifest, never another writer/history for application tables.

For the later adopted config, datasource credentials come through **WA_PHASE0_DATABASE_URL** in a secure environment. It must name the exact approved disposable or hosted identity. The current environment-free review configs never become live merely by setting a variable. Root db:migrate/db:seed/db:check guards stay blocked until a separately authorized adoption slice deliberately replaces them with target safeguards.

## Proposed disposable environment

Prefer a local, loopback-only disposable PostgreSQL **17.11** environment with synthetic fixtures. Resolve and record the immutable image/binary digest, actual cluster/database identity, port and tool versions before execution. Docker/Postgres server execution tooling is not available in this workspace; no container/cluster has been created. No invented digest or replay result is supplied.

The qualified manifest must explicitly forbid **sdceenkakajslwpctbgl** and must not use **lyalfdmfheevpahywuhv** as a shadow/disposable target. No existing managed records are considered disposable. Any teardown/reset/drop permission is limited to the exact approved synthetic local identity; no generic cleanup command may select a target by a mutable environment flag alone.

Local provider role/extension/Auth/Storage/Realtime/event-trigger setup must be labeled an emulation with an explicit differences list. The F0 schema uses only captured PostgreSQL/native capabilities; it does not require live Auth users or provider accounts. The later scheduling exclusion selects btree_gist, which is not in the captured installed extensions and must be verified/authorized at that later stage; it does not block F0. Local success is never hosted Supabase parity.

## Ordered replay actions requested after approval

1. Pin candidate, generator, SQL-companion, evidence-schema, test-plan and draft SQL hashes. Validate 40-model dependency closure and reject any historical/alternate history input. Approve the generated SQL and environment-role prerequisites.
2. Provision only the approved disposable identity, resolve exact tool/image digests and record baseline catalog. Confirm no retained user/provider data. Create narrowly scoped test logins through the approved secret path; never place passwords/tokens in artifacts.
3. Apply the approved environment bootstrap, then the **single** F0 Prisma migration/security history as the dedicated migrator. Capture exact command/exit, source/history hashes, start/finish and actual migration ledger. Run deploy a second time: no pending migration, no checksum change and no duplicate source objects.
4. Capture a schema-only catalog and compare the full physical result with the approved expected manifest, including all SQL-only requirements. Record every managed/emulated exclusion. Prisma diff alone is insufficient.
5. Load only approved synthetic User/security/Customer/Track/Consent/request fixtures. Run the P0-C database tests under actual separate runtime/worker/issuer logins, plus labeled provider-role simulations. Require positive owner cases and denied foreign/missing/stale/privileged cases.
6. Test native constraints, atomic source/history/outbox, immutable proof and CAS races with actual concurrent sessions. Source SQL fixtures do not claim the P0-D worker/owner adapters are implemented.
7. Inject failure and exercise verified recovery only on a separately approved disposable clone. Prove actual backup/restore coverage and marker replay before serving restored data.
8. Produce one comparison/qualification report. Seek the next explicit hosted-development adoption/execution decision only after the initial scope's evidence passes and its actual backup/preservation/access obligations are known. No production, vendor activation, main merge or parallel lane follows automatically.

All steps above are **NOT RUN** under P0-C-01.

## Complete structural comparison

Expected application objects are the selected cut plus its reviewed SQL objects; the full staged candidate is not silently used as expected installed state. Compare schema/name/type, columns/order/native types/defaults/nullability, enums/labels, PK/unique/FK/check/exclusion constraints, FK actions/validation/deferral, indexes/predicates/validity, views and security_invoker, function signatures/body hashes/owner/security/search_path/ACL, triggers/events/enabled state, roles/membership/BYPASSRLS, schema/table/column/sequence/function/default privileges, RLS/FORCE/policy expressions, and installed extension/version prerequisites.

Normalize representation differences deliberately, not by deleting mismatches: ordering of catalog rows, provider-generated OIDs, generated constraint names with recorded mapping and PostgreSQL formatting may be normalized. Semantically different defaults, enum values, grants, predicates or deferrability may not. Exclude provider-owned Auth/Storage/Realtime/vault/extensions from application ownership comparison while separately asserting preserved identity/owner/fingerprint and recording supported provider drift. Unknown/missing visibility is a gap, not success.

## Failure, repair and applied history

Before each deploy, compare target allowlist, namespace/catalog fingerprint, applied ledger/checksums and the approved pending history. A nonzero command, unfinished migration or unexpected object denies qualification. Never ignore an engine error or infer success from a connection/redirect.

Initial transactional failure must leave no committed application structure from that failed transaction. Preserve actual migration failure metadata and sanitized evidence. Only after verifying rollback and exact disposable identity may the approved recovery procedure record that failed migration rolled back and retry reviewed bytes. That is not permission to mark a migration applied without real objects. If any operation was nontransactional or partially committed, stop for a reviewed forward-repair plan based on actual catalog/ledger evidence; do not reset retained targets.

After a migration has applied, its checksum is immutable. Corrections append a new reviewed migration; never regenerate or edit the applied file to make a check pass. Backup/restore is separately tested with artifacts/digests/access controls, RPO/RTO/retention limitations and privacy restore markers. No provider backup availability or deletion promise is inferred from the account tier or a catalog query.

## Adoption decision

P0-C posture changes only after the selected schema/SQL history, real replay, complete comparison, actual role/invariant tests and relevant preservation/restore obligations support a recorded integrator decision. P0-D workers, P0-E owner-adapter parity, P0-F full Privacy/provider execution and P0-G integration retain separate evidence. Database qualification must not require the whole product runtime to exist, and database success must not be used to claim that runtime exists.
