# Checkpoint 010 — physical candidate ready for Brain review

27 October 2026. Brain Directive P0-C-01 is completed within its source-only boundary. **Candidate ready for Brain review; posture D remains.** No target was contacted and no DDL was generated or executed. P0-B retains its prior acceptance; P0-D–G remain unqualified, all 132 operations remain runtime-unqualified/unfrozen, no lane is active and Step 20 remains unapproved.

## 1. What changed from the declared schema?

The original schema contains **177 models/207 enums**. All models, source fields, owners and 12 compatibility cases are accounted for in the existing inventory's new physical_candidate_review section. Its original inventory and compatibility records remain intact. The review-only target contains **214 models/219 enums**: the original 177 reconciled models plus 37 justified additions. The initial proposed foundation is a **40-model parent-FK-closed cut**, not the entire product schema.

Material changes are:

- Exact immutable Consent content/presentation/acceptance proof and separate withdrawal/decline evidence; versioned Media/policy/purchase/agreement proof rather than mutable labels or URLs.
- The approved platform-screening Order source, coherent self-paid subject/package and nullable seller only for that source; required fresh Customer buyer identity; immutable purchased scope/units and Payment-owned effect identities.
- Removed redundant financial/signature/PDF/finding/lock aliases and reusable plaintext participant or Notification credentials. Explicitly retained compatibility/projection fields cannot authorize business actions. QueueJob remains architecture-only as a protected SQL view, never another executable table/queue.
- Durable shared command/outbox/work/lease/fence/inbox/effect/reservation records, typed economic receipts, source revision/generation/transaction identities and atomic source/history/required-message obligations.
- Explicit provider-neutral Free enrollment/current selection and retained usage, complete fiscal aggregation dimensions, typed Privacy instructions/actual owner receipts/restore markers/export accounting, Media object generations and Ops incident/effect records.
- Restrictive FK deletion/key changes, UTC instants and CAS revisions. Private discovery/tracking defaults and unapproved commercial/legal defaults were reconciled; no new fee, tax liability, refund timer, retention period or product behavior was adopted.

Every model has exact candidate fields/keys/FKs, owner/purpose/classification, sensitive fields, Privacy executor, changes, authority and stage. Every source field has a disposition. [The decisions](database-candidate-decisions.md) distinguish technical choices from settled product meaning and external activation gates. JSON is explicitly bounded per field; deferred nonnullable payloads block their own table migration until an exact closed schema is reviewed. Initial F0 permits only registered result/outbox/evidence JSON; other metadata and JSON-valued entitlements stay null.

## 2. Is it ready for Brain review?

**Yes, for review of these exact artifacts, not adoption.** Both candidate schemas pass the installed **Prisma 7.10.1** validator using configs with no datasource URL, dotenv, migrations or shadow target. They contain no client generator. The model/field ledger, individual compatibility dispositions, 18 SQL-only enforcement specifications, 869 object/access entries, JSON boundaries, tests and migration/continuation plans are connected and fingerprinted in [the packet manifest](database-candidate-manifest.json).

No ordinary physical-design choice is left as an unexplained alternative. For example, pooled context uses a restricted issuer's unguessable transaction-bound grant; scheduling selects a native GiST exclusion with a separately gated later btree_gist prerequisite. Future legal/provider/serializer-specific activation remains explicitly staged. A staged table's presence is not permission to activate it or skip its pending policies/tests.

## 3. Which security findings have proposed dispositions?

Checkpoint 009's captured defaults are creator-specific. The candidate selects one nonlogin application object owner and a dedicated migrator; runtime, worker and issuer have separate credentials, no ownership/DDL/BYPASSRLS and no owner inheritance. New internal app/platform objects receive no browser/API grants and explicit ENABLE/FORCE RLS. The public auto-RLS trigger is only a safeguard, not app-schema protection. No per-Module PostgreSQL roles are introduced.

A plain actor-ID GUC supplies no authority. A restricted issuer's scoped grant is bound to session_user, backend PID and transaction ID, with current owner/security/source checks, operation/field guards and pinned private helpers. Bootstrap/proof paths are nonrecursive. Actual positive access, pooling, spoofing, revocation and privilege tests remain required; static review does not prove them.

The two advisor warnings concern the exact public.rls_auto_enable(): event_trigger return type, postgres ownership, SECURITY DEFINER, pg_catalog search path, execution grants and enabled ensure_rls relationship are preserved. A grant warning is not demonstrated RPC exploitability. Propose testing an exact-function direct-EXECUTE revocation on an explicitly approved disposable emulation, preserving the body/owner/trigger and verifying legitimate CREATE TABLE/AS plus denied unauthorized invocation. No warning was cleared and no provider object was changed. [Full security analysis](database-candidate-security.md).

## 4. What actions are requested next?

First, Brain reviews/approves the exact candidate and ordinary technical choices. Only then request the specified **source-only pinned Prisma migrate diff --from-empty --to-schema foundation-candidate.prisma**, using the environment-free config and script output to a review draft. The exact proposed command is in [the migration plan](database-candidate-migration-plan.md); it was **NOT RUN**.

Next review the complete generated structural SQL together with explicit constraints, policies, grants, helpers/triggers and environment-role prerequisites. One future **prisma/foundation/migrations/** Prisma history coordinates application structure and security; Supabase CLI/MCP is not a second application DDL writer. The historical June migration remains preserved/inactive and no migration is marked applied to simulate objects.

Execution requires its own approved exact synthetic disposable PostgreSQL 17.11 identity, immutable tool/image digest, scoped actions and preservation/recovery boundaries. No environment has been provisioned; Docker/Postgres execution tooling is unavailable here. Neither hosted project is a shadow/disposable target. Apply only the reviewed history, repeat deploy, compare the complete physical catalog, test actual role access/invariants/concurrency and prove failure/recovery/restore. Managed Auth/Storage/Realtime/extensions remain outside application ownership. Local emulation cannot establish hosted parity.

## 5. What remains externally gated?

DBP-01/02/04/05 retain scoped VERIFIED evidence. DBP-03/06/07/08/09/11 are PARTIAL; DBP-10/12 remain NOT_OBTAINED. DBP-09 now has complete source-review evidence, but candidate approval/physical qualification is still pending. A concrete replay plan is not DBP-10 execution. Backup/restore/retention and any destructive disposable action require actual facts and their scoped authorization before use.

Future legal retention, vendor capabilities, production credential/age/Consent evidence, tax/screening/regulated integrations and prize rules gate their dependent behavior. They do not block this completed source review or an isolated synthetic foundation test. U.S./18+ scope remains; therapy, prescribing, child-directed features and prize competitions remain launch-disabled. Draft legal content is nonproduction test material. UI stays in its separate thread.

The recommended first P0-D slice is the actual **Customer provisioning → assignDefaultFreeTrack.v1** handoff under WF-01/R078, using SH-004/114/044/046/047 and applicable locking/authority contracts. The source transaction commits history, evidence, durable result and required outbox; a fenced worker processes Track's deduplicated effect without downgrading paid selection or resetting usage. [Exact owner/files/tests and minimal security/Privacy prerequisites](database-candidate-continuation.md) are specified, not implemented. The goal is no repeated committed business effect under retries; network delivery remains at least once.

## 6. What was actually validated?

Offline native Prisma validation passed for both final schemas. Source validators checked original-model/field ownership, foundation FK closure, compatibility dispositions, essential physical invariants, JSON restrictions, object/role boundaries, SQL requirements, test staging, native proof hashes and source preservation. **28 adversarial semantic candidate mutations** and **36 Phase 0 source/evidence regression mutations** pass. The candidate mutations disable fingerprint checks and require the specific semantic rejection. All three review generators reproduce their artifacts exactly. Context/foundation/Phase 0 checks and diff hygiene pass. Exact commands, outputs, preservation and scope are in [the validation report](checkpoint-010-validation.json).

During preparation, native validation caught orphaned Agreement relations/indexes and long Notification constraint-name collisions; those were corrected. Consistency checks then corrected the payout effect-receipt link and required source-revision evidence fields. Final schemas/checks pass. No unchanged application/dependency tests were rerun to imply new runtime evidence.

**451 database/worker/adapter/executor tests are specified and all are NOT_RUN.** No real installation, catalog parity, SQL enforcement, least-privileged RLS behavior, migration failure/recovery, backup/restore, worker/provider/Privacy execution or runtime freeze is claimed.

## Git preservation and recovery

Entry was clean at Checkpoint 009 **a067dd52d14f6313e4f350a33750c3486426d91f**, tree **1a6ac891c0caf149dabd360dbb1f09eddec55f3c**, on codex/phase0-clean-foundation-2026-10-19. Checkpoint 008 **ee973d01cebf2d69f05ad0efb37366f9b08fb2e3** is an ancestor. Checkpoint 009's full-history bundle was verified. No earlier history was reset or replaced.

Repository metadata identifies the GitHub repository as public. Authenticated git transport is unavailable: normal push preflight failed because no HTTPS username/credential was available with terminal prompting disabled. No push, main merge or deployment is claimed. The final downloadable full-history bundle and recovery manifest pin actual HEAD/tree, checksums, verification and restoration commands. New work is preserved in logical commits on the same dedicated branch; the final self-referential commit identity is reported outside the committed packet.

Review entry: [packet index](database-candidate-review-index.md). Stop point: **before DDL generation**, as P0-C-01 requires.
