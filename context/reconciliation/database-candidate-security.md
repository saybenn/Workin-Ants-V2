# Database candidate security — review only

This package specifies controls; it has executed none of them. [The object/role/access matrix](database-candidate-access-matrix.json) covers every candidate table, enum/schema, required view, function/trigger family and the absence of application sequences. [The SQL companion](database-candidate-sql-objects.json) names exact enforcement obligations and positive/negative outcomes. These extend the existing model/security inventory; they do not replace Role, Identity, Privacy or source-owner authority.

## Physical ownership and connections

Business ownership is not PostgreSQL ownership. One application object owner, **wa_schema_owner**, owns app/platform/private application objects and is NOLOGIN/NOBYPASSRLS. It is not a Module. A dedicated **wa_migrator** login can explicitly assume that role only for approved DDL; application and worker connections cannot. The private Prisma migration ledger is a documented migrator-owned metadata exception, with no browser/API grants.

**wa_app_runtime** and **wa_worker** are separate NOINHERIT/NOBYPASSRLS logins, own no application tables/functions, receive no DDL/TRUNCATE/REFERENCES/TRIGGER/MAINTAIN privileges and cannot SET ROLE to the owner, issuer or helper. They receive only selected owner-action or handler operations. Direct application use of postgres, a Supabase service key, BYPASSRLS or an object owner is prohibited.

**wa_context_issuer** has only the protected capability issue/revoke path. It cannot mutate business tables. **wa_private_helper_owner** is NOLOGIN/NOBYPASSRLS and has only context binding/lookup and minimal current Identity-generation reads. It receives no arbitrary source-repository privilege. A later **wa_privacy_executor** connection uses explicit owner field/action mappings under a current verified Privacy request; it is not a blanket delete role.

Privileged support is an application action with actual step-up, target, field/purpose and proof obligations. No generic support database superuser or one PostgreSQL role per Module is introduced. Existing Supabase-managed roles, including service_role's bypass capability, are observed facts; their ownership or definitions are not changed. Internal app/platform objects grant them no access.

## Trusted context through a Prisma pool

A direct Prisma connection does not carry a Supabase user's identity. Never base a policy on a caller-provided userId, JWT user_metadata or an arbitrary SET LOCAL actor ID.

Proposed flow:

1. Server middleware resolves actual credentials under SH-001 and current Identity generation. Role/source owners authorize the exact registered action/purpose/target/fields, including applicable Consent, entitlement and Hold checks. A client body cannot supply its own trusted context.
2. Before the source transaction, the restricted issuer creates a **DatabaseActionGrant** containing a digest of an unguessable handle, the approved user-or-service principal, expected database login role, source/security generations, field scope, policy version and expiry. No production TTL is invented here. A grant is transport evidence for a prior owner decision, not a new policy engine.
3. Prisma opens one interactive transaction on one physical connection. A parameterized private binding call validates the handle and atomically binds it to session_user, backend PID and the actual PostgreSQL transaction ID. A local setting transports only the secret handle/opaque binding; helpers resolve the protected grant row. A role cannot manufacture authority by changing a GUC.
4. Operation-specific RLS USING/WITH CHECK, column privileges and field guards check that binding and current owner state. The helper reads only its bounded Identity-generation facts. Source-specific currentness/relationship checks use fixed typed owner bindings, never a generic foreign repository or a client flag.
5. Source state, source history, command/effect receipts and required messages commit in the same transaction. PostgreSQL stamps mutationTransactionId; callers cannot spoof it. No network/provider/issuer call is held inside source locks. Issuer attestation is not a substitute for the current source check at commit.
6. SET LOCAL state ends at commit or rollback; the bound transaction cannot authorize a later pooled request. A retry obtains fresh context but reuses the original semantic command/effect identity. Missing, stale, expired or revoked context denies.

The private bind/lookup functions have a pinned pg_catalog search_path, fully qualified application/extension references, fixed object names and narrow signatures. PUBLIC execution is revoked; only named runtime roles can use the permitted helper. The helper owner cannot log in or run arbitrary source writes. App/worker cannot read arbitrary grant rows, insert issuer assertions or assume the issuer role. Actual issuer login and app login credentials are separate and remain outside source/logs.

**Bootstrap is nonrecursive.** Issuer operations use an explicit restricted issuer policy and do not require a context they are trying to create. Core command/outbox/lease/evidence and Audit append paths use their narrow infrastructure invariants; they do not recursively emit proofs/outbox messages about every internal proof. Domain source mutations use their registered finite history/message obligations. Optional Ops telemetry cannot prevent context denial, command recovery or the proof store from starting. Audit's own protected read emits one bounded nonrecursive access receipt.

This capability transport is a proposed implementation choice under DB-C04. Its unforgeability, pooling behavior, revocation, privilege boundary and actual source checks must pass the disposable tests before adoption. It is not runtime security proof.

## Every application object starts restricted

All app/platform tables have explicit ENABLE and FORCE RLS, stable owner keys and no browser/Data API grants. Actor IDs remain protected internal source references. Policies are per operation and current relation; TO authenticated alone is never sufficient authorization. A writable path needs a real positive case as well as missing/foreign/stale-context denials.

Immutable evidence is not ordinary mutable state. Correct with retained new evidence. Lawful Privacy redaction/deletion is separately authorized by actual field/action/retention policy; preserving evidence is not permission to keep every personal field forever. RESTRICT FKs prevent accidental cascade loss, while coordinated owner executors explicitly anonymize/delete approved dependents or preserve required pseudonymous identity stubs.

Context-sensitive field access is enforced in the owner port plus permitted SQL operations/column masks. RLS alone does not authorize resume fields, exact location, tax documents, agreements or private media. Protected delivery requires durable proof and exact artifact/current-generation validation. No private table becomes exposed to make a test easier.

Every JSON column has an explicit admission rule in database-candidate-json-boundaries.json. In the initial Customer slice, only exact registered command-result, outbox-payload and per-model evidence shapes may be nonnull; other F0 metadata and JSON-valued entitlements stay null. Deferred nonnullable JSON blocks its table migration until its exact closed schema is reviewed. This is an explicit staged restriction, not an arbitrary JSON fallback.

All candidate views/functions/triggers appear in the object matrix. The Ops queue view is SECURITY INVOKER and read-only, with no payload/credential fields. Privileged context helpers have explicit limited exceptions; source mutation/evidence triggers use fixed source bindings and SECURITY INVOKER. All keys, references, source schema bodies and actual policy/serializer versions are compared at adoption. No application sequences are needed; any future sequence needs its own explicit grant review.

## Creator-specific defaults from Checkpoint 009

The retained catalog shows postgres-created public tables no longer inherit default API CRUD grants, but TRUNCATE/REFERENCES/TRIGGER/MAINTAIN privileges remain. supabase_admin-created objects retain broad defaults, and function execution can still come from PUBLIC. This is why the checkbox is not a security contract.

For new application objects, the selected creator is wa_schema_owner under an explicitly controlled migration role. Its global function defaults and each actual function ACL must deny PUBLIC execution; table/sequence/object defaults in the application namespaces grant no API access. Review every role that can inherit/SET ROLE into that creator. An operator creating app objects as postgres/supabase_admin instead of the selected owner produces an adoption failure, not permission to assume that creator's defaults were hardened. Do not broadly revoke grants on managed Auth/Storage/Realtime/provider objects.

The observed auto-RLS trigger covers public only and can log a failure without proving table protection. Application migrations explicitly install/verify app/platform RLS and policies. Metadata that a trigger is enabled is not a positive table-behavior test.

## Disposition of the two auto-RLS advisor warnings

Retain exact observed facts: public.rls_auto_enable() returns **event_trigger**, is SECURITY DEFINER, is owned by **postgres**, pins **pg_catalog**, is linked to enabled **ensure_rls**, and has PUBLIC/anon/authenticated execution grants. The captured current body uses quoted identifiers for its public-table operation. The two advisor findings are grant observations; ordinary RPC reachability or exploitability was not demonstrated. No direct invocation or remediation occurred here.

Propose one narrow environment-control change for later review: on a disposable copy, revoke direct PUBLIC and explicit browser/API execution **only on this exact function**, preserve its type/body/owner/trigger, and repeat legitimate DDL-role CREATE TABLE/AS tests. Verify unauthorized ordinary invocation fails and auto-RLS still works. If provider lifecycle rules prohibit the change or behavior differs, retain the warning with its evidence and obtain the provider-supported disposition; do not disable the trigger, change unrelated managed objects or create another auto-RLS implementation merely to clear a linter.

This public environment setting is not absorbed into application ownership. Any later exact-function environment change has a separate scope/approval in the same qualification manifest; the application schema still has only one Prisma migration stream. It cannot silently become a second writer of application objects.

Advisor references: [anonymous execution](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable), [authenticated execution](https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable). Primary guidance: [PostgreSQL 17 RLS](https://www.postgresql.org/docs/17/ddl-rowsecurity.html) and [SET LOCAL lifetime](https://www.postgresql.org/docs/17/sql-set.html). These sources explain mechanisms, not the user's live qualification.

## Required verification

The [test plan](database-candidate-tests.json) has named positive and negative cases for every candidate table, scoped to its migration stage. F0 tests use actual separate least-privileged database logins and synthetic issuer/Identity fixtures. SET ROLE from an administrative session alone is insufficient proof of login/pool isolation. They test context spoofing/reuse, ownership reassignment, cross-user/source access, privileged-call boundaries and atomic evidence.

Future stages add actual foreign-Organization resume tests, Booking interval exclusion, media generation/revocation, privacy exports and provider callbacks. These are staged obligations, not a requirement that the entire product runtime exist before P0-C can qualify its initial 40-model database cut. P0-D/P0-E/P0-F adapter and worker/provider tests remain separately named. Every database behavior test currently says **NOT_RUN**.
