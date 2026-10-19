# Greenfield database evaluation and reproducible migration/RLS strategy

Status: **PROPOSED EVALUATION; POSTURE D; NO BASELINE SELECTED OR EXECUTED.** Directive006-A prefers a brand-new isolated development database while preserving the old Supabase target and all Git/schema/migration history. No target has been contacted, provisioned, reset, seeded or migrated. The installed Prisma7.8.0 validates the current177-model source using an environment-free config; this proves syntax/relations accepted by that CLI, not physical architectural compliance or live schema/security.

## Evidence packet and source reconciliation

[database-provenance-requirements.json](database-provenance-requirements.json) assigns12 concrete requirements to environment, migration, security and source owners. Actual identity, isolation, preservation obligations, ledger and structural/security comparison are NOT_OBTAINED. Identify a distinct development project/database and sanitize the evidence; no passwords, tokens, connection strings or personal rows belong in the packet. “New” must be proven by actual namespace/data/ledger evidence. Managed Supabase/Auth schemas may already exist and must not be recreated or treated as application-owned emptiness.

[greenfield-model-security-inventory.json](greenfield-model-security-inventory.json) covers177/177 unique current models and source owners, 53 historical table creations and124 static gaps. Every row starts denied to direct browser access and requires exact source-owned port/security qualification. Twelve compatibility mirrors retain the prior reconciled authoritative sources. No model count, an enum, Prisma validate or a directory name adopts a fresh baseline.

Before proposed DDL: reconcile the R003 screening Order source/participant XOR, normalized Agreement/effect references, purchased access/Booking/Video/Media contextual ownership, generation/currentness, durable execution/fencing/receipts and actual Privacy field/action coverage with owning architecture. Preserve explicit Media joins and professional-only Offering sellers; Organizations hire and Candidates apply. Ops QueueJob stays a projection; logical Role/AI/Ops references do not automatically create tables. A new physical record requires an approved owner/contract rationale, not an invented duplicate of source truth. All12 compatibility mirror cases require explicit keep/remove/derived/source-reference physical decisions and tests. Their architecture is settled; this is physical qualification.

## One reproducible history

1. **Identity gate.** Record the actual isolated target, provider/region/Postgres/extension versions, managed schemas, preservation/disposal obligations, application ownership and empty-or-existing migration ledger. Compare it with the previously referenced target. Preference alone cannot promote posture D.
2. **Candidate gate.** One integration owner collects proposed source-model constraints, ownership, action/field access, semantic idempotency, revision/fence/effect uniqueness, deletion/retention and expected indexes. Resolve physical representation under existing rulings; keep optional/externally gated capabilities inactive. Review all 177 current rows plus justified architecture-required storage. Pin exact schema, CLI, SQL and test inputs in Git.
3. **Generate/review gate.** Only after candidate approval, use the installed 7.8 CLI's source-only `prisma migrate diff --from-empty --to-schema <reviewed-candidate> --script` to draft DDL for review. Add required RLS/grants/functions/triggers/constraints not represented by Prisma in the same ordered migration history. No live/config-datasource/migrations/shadow comparison is authorized under current D. No baseline SQL is generated or adopted in this checkpoint.
4. **History routing gate.** Preserve the original migrations and checksums unchanged. If actual evidence supports a separate fresh baseline, use a reviewed distinct candidate history/config and record which target it owns; do not run it alongside the old history against one database. There is one active steward and one ordered adopted stream including security changes. Never resolve a migration as applied to simulate replay, reset an unidentified target, or use db push to bypass reviewed history.
5. **Disposable replay gate.** After explicit target/evidence authorization, reproduce a disposable database matching the exact chosen Postgres/extensions/Auth setup. Apply the complete reviewed stream from empty application state, capture migration ledger/checksums and normalized catalog. Apply deploy again and prove no pending migration. Compare tables, columns/defaults/nullability, enums, PK/FK/check/unique constraints, indexes, views, functions, triggers, extensions, ownership, grants/default privileges, RLS and policies. A Prisma-only diff cannot establish all these dimensions. Test migration failure and restart/forward-repair procedure on this disposable identity; no destructive reset is a recovery shortcut for retained data.
6. **Security/invariant gate.** Run the actual allowed/denied matrix below under distinct database roles/JWT contexts. Prove transaction/constraint/concurrency/fencing/outbox/receipt invariants before real owner ports or a shared runtime are qualified. Retain exact commands, source/build IDs, fixture identities, outcomes and failed regressions without personal data or secrets.
7. **Adoption gate.** The integrator records the evidence-supported posture/greenfield decision, exact target/history/schema/RLS versions, rollback/forward-repair and data/retention constraints. An operationally empty test database is not production readiness. No migration deployment, provider activation or parallel domain lane follows automatically. Revisit Gate10 after actual dependent qualifications.

The current npm database-write aliases fail closed and execute no database command. The preserved old seed and check SQL must not be run against the proposed fresh target. Existing `prisma.config.ts` is retained for historical comparison; `prisma.offline.config.ts` intentionally has no datasource URL or environment loading. Future connection credentials belong in a controlled secret handoff, never in this plan.

## RLS, grants and owner boundaries

Start app tables/functions/views with no anonymous/authenticated direct privilege unless an exact reviewed public contract requires that surface. Inventory actual exposed schemas and default privileges rather than assuming provider defaults. Grants and row policies are both required for a permitted Data API surface. Enable/qualify RLS for exposed tables; tests must use actual anon/authenticated and least-privileged server roles, not an administrative or service role that bypasses the intended policy. Evaluate FORCE RLS/table ownership and BYPASSRLS deliberately against the selected provider setup.

Private resume, exact Location, Agreement/tax/healthcare evidence, protected Media and exports remain server-owner/proof-mediated where required. Row access alone does not authorize fields, purposes or disclosure. Server commands repeat current source authority/consent/entitlement/Hold/security-generation checks; client IDs/claims/public flags and downstream projections never supply authority. A service credential does not substitute for these checks.

Review ordinary views for invoking-role security where supported by the actual Postgres version; otherwise deny browser access/unexpose them. Materialized views and privileged functions need their own explicit access design. Revoke unintended PUBLIC function execution, use a pinned safe search_path with schema-qualified references for reviewed privileged functions, and prevent caller-controlled object resolution. Inspect triggers, ownership and role inheritance. Keep Supabase-managed/Auth objects outside application migrations.

## Required real security and recovery tests

| Matrix | Required assertion before adoption |
|---|---|
| Each177 current model/default-private surface | Anon and unapproved authenticated SELECT/INSERT/UPDATE/DELETE deny; distinguish no privilege from policy-filtered results and never leak private existence |
| Selected real owner action | Exact allowed case through approved boundary; other User/Organization/Professional/Candidate and foreign owner mutation denied |
| Current authority | Removed member, revoked session/grant, stale revision/generation, missing consent, unsupported purpose/field, Hold and entitlement unknown deny appropriately |
| Public projections | Only current approved published fields; removed/hidden/revoked/tombstoned data absent; projection cannot authorize source action |
| Privileged surfaces | View/function/trigger grants, search_path/object substitution and BYPASSRLS cannot broaden browser or unregistered server access |
| Economic/execution invariants | Identical/conflicting replay, CAS races, fenced late commit/noncommit, unique economic effect, source/history/outbox atomicity, worker crash/reclaim and no network under DB locks |
| Privacy and preservation | Actual field/action/provider inventory, lawful retained/omitted accounting, exact export bytes/generation/digest and backup/restore/removal behavior; protocol fixtures alone never complete this |
| Migration recovery | Exact disposable target identity, partial-failure evidence, safe forward repair/restart, unchanged applied checksums, deterministic no-pending replay and complete catalog comparison |

These are required tests, **not executed results**. The only new Prisma result here is environment-free source validation. The13 externally gated SHs and11 historical external concern families remain independent actual provider/legal/account/retention gates.

## Primary guidance and version limits

- Installed Prisma7.8.0 `validate --help` and `migrate diff --help`: exact flags inspected2026-10-19. Current unversioned Prisma pages may describe a later CLI, so they cannot silently upgrade this strategy.
- https://docs.prisma.io/docs/orm/v7/prisma-migrate/getting-started — v7 migration context; source-to-empty draft does not perform a replay.
- https://supabase.com/docs/guides/database/postgres/row-level-security — privileges/policies and actual role tests.
- https://supabase.com/docs/guides/database/views — invoking-role view permissions.
- https://supabase.com/docs/guides/database/functions — privileged function/search_path review.

Web references retrieved 2026-10-19 are general primary guidance, not evidence about this user's target. Actual environment and provider capabilities remain unverified.
