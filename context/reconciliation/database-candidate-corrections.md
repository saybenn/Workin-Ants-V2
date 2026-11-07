# P0-C-02 — B010-01/02/03 source corrections

> Current amendment P0-C-03A: [corrected SQL source review](foundation-sql-draft-review.md) and [retained directive](directives/brain-directive-p0-c-03a.md) supersede earlier drafting-stage gaps/next actions in this historical source plan. Source and SQL drafts only; posture D; all 451 database/runtime cases NOT_RUN. Independent Identity currentness, narrowly enumerated read-only Boolean ports, append-only age evidence and both added owner revisions are present for re-review, not execution-approved. No human setup task.

Authority: the owner's “Execute corrections and publish” amendment, received 1 November 2026. It authorizes isolated restoration, these source corrections, applicable offline checks, commits and normal publication of `codex/p0c-candidate-corrections-2026-10-31` to `saybenn/Workin-Ants-V2`. The earlier P0-C-02 text was not in the Checkpoint 010 package; this document does not invent its absent sections or grant broader authority. Candidate approval remains pending, posture D remains and the pre-DDL stop remains.

The preserved starting commit is `879336673f4c0408276ea8d31ddbc508fa8f0d9c`, tree `8af073cb833bedb92524a1ffef4b9f10b07b08f0`. The complete bundle and evidence ZIP remain unchanged. The old OneDrive checkout and its changes are outside this working copy. These corrections alter review-only schemas/specifications, not an installed database, production adapter, canonical Shared Operation or accepted business decision.

## B010-01: rollback-safe transaction authorization transport

The old proposal issued an unbound grant, then updated its backend/transaction binding inside the source transaction. Full rollback or rollback of a savepoint containing that update could restore the unbound row. Clearing a local setting did not prevent the original secret from being presented again in a later transaction. The original recorded source checks did not establish this database behavior.

Chosen correction: **issuer-committed immutable transaction tuple**. `DatabaseActionGrant.databaseLoginRole`, `backendPid` and `transactionId` identify the one intended transaction at insertion; PID and xid are required, not nullable. The tuple and all issued authority fields are immutable. Runtime and worker never get direct grant-table access, and the helper never writes a grant.

The implementable future sequence is:

1. Actual credentials, current Identity, Role and owner authorization resolve the actor/service and exact action, purpose, target and fields through the existing canonical boundaries.
2. Open a READ COMMITTED interactive transaction on the runtime or worker's single physical connection. Before business reads or source locks, capture `session_user`, `pg_backend_pid()` and `pg_current_xact_id()::text` through the trusted server bridge. A client cannot choose or submit authoritative tuple values. The xid8 text includes its epoch; PID alone is never an identity.
3. The separately credentialed issuer rechecks authorization/currentness, then commits the exact tuple-bound grant using its own connection and transaction. It has no business-source write privileges. No business lock is held while this separate issuance occurs. Issuer failure or timeout aborts the source attempt; no provisional local grant is accepted.
4. A subsequent statement in the source transaction calls the narrow bind helper. It reads the already committed grant, compares the complete tuple/scope/currentness and sets only local opaque transport. READ COMMITTED is explicit because the grant was committed after the tuple-capture statement; Repeatable Read/Serializable are rejected by this protocol until separately designed and qualified. The helper uses original `session_user`, not its DEFINER `current_user`.
5. Source-specific currentness/relationship locks, RLS, field guards, Consent/entitlement/Hold and proof checks still precede protected effects and commit. Atomic source/history/receipt/outbox obligations are unchanged. There is no issuer/provider/network call while business locks are held.
6. Commit, full rollback, failed bind or rollback of the bind's savepoint cannot undo the issuer's committed tuple. Every later transaction has another xid, so the old handle fails even on the same pooled backend. Rebinding in the same live transaction is idempotent; it does not widen authority. A new attempt gets fresh authorization and a new tuple-bound handle while preserving semantic command/effect identity.

`mutationTransactionId` on the grant is the issuer's INSERT transaction; `transactionId` is the separately captured intended source transaction. They serve different purposes and must not be equated. An orphan grant after a source crash conveys no later authority. Revocation is irreversible, scope cannot be widened, and cleanup/retention and production TTL remain separately approved policies.

Rejected alternatives: a bind-time consumed flag has the same rollback problem; an autonomous transaction is not an assumed PostgreSQL facility; session state alone leaks/replays across pooled requests; holding source locks across issuer/network operations violates the existing boundary. The chosen solution adds one issuer round trip before business work, with explicit pool/timeouts/failure tests still required. It does not require a new model or a database script now.

Primary PostgreSQL 17 references checked for this design: [session and transaction identity functions](https://www.postgresql.org/docs/17/functions-info.html#FUNCTIONS-TXID-SNAPSHOT) and [READ COMMITTED statement snapshots](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-READ-COMMITTED). These support the design rationale; actual database qualification remains NOT_RUN.

## B010-02: exact presentation and acceptance coherence

ConsentPresentation previously had content and context but no accepting User or action, while SQL-05 required those comparisons. It is now an immutable per-user/action presentation rather than an implicitly reusable template. Added fields are the existing User reference and registered `actionOwner`/`action`; the context fields remain explicit.

ConsentLog retains the acknowledged `presentationHash` and adds `contextOwner` so action owner and context owner are not silently conflated. Its composite `(presentationId, contentRevisionId, userId)` FK points to the matching unique presentation key. This natively prevents wrong-user/content substitution. SQL-05 additionally requires equal actionOwner/action/contextOwner/contextKind, null-safe contextId equality and `presentationHash = renderedHash`. NULL is a registered global context only, never a wildcard. ConsentContentRevision type/version/applicability and exact actually rendered bytes remain owner-verified facts.

The existing acceptance key remains scoped to User. Its fingerprint covers exact presentation ID/hash/content/user/action/context. Identical replay returns the original proof; changed meaning conflicts; intentional reacceptance uses a new key. Decline/withdrawal remains append-only and binds the same subject/presentation and prior proof where supplied. A matching submitted hash or FK is not evidence of actual display, affirmative action, legal approval or authorization for another business action.

No new IP, device, email or free-text personal evidence is added. Existing historical source schema and past results are preserved. Canonical SH wire contracts remain unchanged; actual adapters and legal/Privacy field dispositions require their existing later gates.

## B010-03: exact role/operation test paths

The access matrix and table cases now carry the same `operations_by_role` and `direct_denials_by_role` data. No case uses “runtime or the narrowly registered purpose role.” Every role has a concrete path or an explicit empty list:

| Role | DatabaseActionGrant permitted path | Explicit exclusions |
|---|---|---|
| wa_context_issuer | Authorized tuple-bound INSERT, SELECT its own issued rows, UPDATE revokedAt only from NULL to a timestamp | Scope/tuple rewriting, deletion and source business writes |
| wa_private_helper_owner | Bounded SELECT only through the two named DEFINER functions | LOGIN, grant INSERT/UPDATE/DELETE and generic source access |
| wa_app_runtime | EXECUTE bind_request_context; policy receives context_allows Boolean | Direct grant SELECT/INSERT/UPDATE/DELETE; SET ROLE issuer/helper/owner |
| wa_worker | The same helper-only transport, for its own authorized tuple and handler scope | The same direct grant and role-escalation denials |
| anon/authenticated/service_role | No direct grant or helper access | Grant CRUD and helper EXECUTE |

Candidate/Professional FK-only prerequisites in F0 require an exact permitted SELECT, not future feature mutations. Worker actions additionally require their actual registered handler and current fence; no permission follows from an empty role list. Table-level positive/negative cases remain 428 IDs, and the complete register remains 451 tests, all NOT_RUN.

The existing context case now explicitly includes full rollback after bind, savepoint/bind/rollback-to-savepoint/full-rollback, failed bind, commit/pool reuse, backend/xid mismatch, wrong isolation and fresh-grant retry. The privilege case separately exercises issuer, NOLOGIN helper, runtime and worker paths. The immutable Consent case covers subject/content/action/context/hash mismatch, NULL wildcard rejection and append-only withdrawal. Wider Agreement/financial branches remain in their later stages, consistent with the separate 94-case handoff clarification. That clarification is not silently rewritten or treated as execution approval.

## Evidence and limits

The three source generators now write explicit UTF-8/LF, making raw fingerprints stable on Windows and Linux. The initial pristine Windows restoration was rewritten from its Git index blobs solely to restore exact original bytes after the machine's CRLF checkout conversion; no old OneDrive file was touched.

Original `checkpoint-010-validation.json` and `database-candidate-native-validation.json` remain historical evidence. Current native output is recorded separately in `database-candidate-corrections-native-validation.json`; current check output is in `database-candidate-corrections-validation.json`. The existing candidate manifest fingerprints current review artifacts and identifies the preserved base. Generator reproducibility and semantic adversarial checks are offline evidence, not RLS, concurrency, actual role login, restore or runtime proof.

No component/API/classes/token change is made. No database script, migration, container, database connection, hosted setting or broad product feature is authorized or executed by this correction. Return the corrected commit to Brain for review. Future SQL generation and all execution remain separate gates.

The [original separate 94-ID handoff selection](checkpoint-010-first-replay-selection.original.json) is now available here byte-for-byte so review needs no extra upload. The [current selection wrapper](database-candidate-corrections-first-replay-selection.json) preserves its 94 IDs and pins the corrected 451-case register; all remain proposed and NOT_RUN. The recovery ZIP/bundle are unchanged.

Publication review: the repository is public. Incoming GitHub Actions workflow files were checked, along with remote main's workflow directory; none exists at these tips. Commits use `[skip ci]`. A minimal `vercel.json` disables Git deployments for this correction branch only under [Vercel's documented git.deploymentEnabled setting](https://vercel.com/docs/project-configuration/git-configuration); it changes no other branch or hosted setting. Pattern scanning plus targeted history review distinguishes deliberate nonconnecting test canaries from real credentials. No private account data or key material is authorized for publication.

### Windows context-check portability repair

The first current suite passed candidate, 48 candidate adversarial, foundation, foundation adversarial, Phase 0 and Phase 0 adversarial checks, but the context aggregator rejected historical handoff identities because `str(relative_path)` emits Windows backslashes. The stored source identities use portable forward slashes; original source byte hashes matched. `check-handoff-adjudication.py` now compares `relative_path.as_posix()`. No historical source, adjudication, architecture ruling or past result was rewritten. The [failed attempt](database-candidate-corrections-validation-attempt-1.json) is retained separately, followed by current rerun output. This repairs a check's portability, not a reopened architecture or P0-B acceptance decision.

## Targeted completion after Brain review of 72e7673

The [retained review](directives/brain-review-72e7673-targeted-completion.md) accepts B010-01's immutable issuer-committed transaction tuple and B010-02's exact consent representation at source-design level. Both review schemas, SQL-02/05/06 definitions, binding protocol and grant-role design remain unchanged. Whole-candidate approval, database posture D and the stop before DDL remain.

### Track enrollment worker boundary

The previous owner-wide default-Free operation was too broad: it included immutable usage records and catalog administration. It is replaced by explicit per-model SQL verbs, exact input columns, target scopes, currentness/semantic-identity/fence guards and Customer-only F0 handler binding. The existing WA-R078 / Track section 10.6 and continuation remain the authority; no new commercial or lifecycle decision is introduced.

| Model | Stage | Default-Free worker operations |
|---|---|---|
| OrganizationFeatureAccess | LATER_OWNER_ORDERED_SLICE | NONE |
| TrackPlan | F0_FOUNDATION | SELECT |
| TrackPlanPrice | LATER_OWNER_ORDERED_SLICE | NONE |
| TrackEntitlementDefinition | F0_FOUNDATION | SELECT |
| TrackPlanEntitlement | F0_FOUNDATION | SELECT |
| TrackSubscription | F0_FOUNDATION | SELECT, INSERT |
| TrackEntitlementGrant | F0_FOUNDATION | SELECT, INSERT |
| TrackUsageEvent | F0_FOUNDATION | NONE |
| TrackUsageCounter | F0_FOUNDATION | NONE |
| TrackSubscriptionEvent | F0_FOUNDATION | INSERT |
| TrackBaseSelection | F0_FOUNDATION | SELECT, INSERT, UPDATE |
| TrackEnrollmentReceipt | F0_FOUNDATION | SELECT, INSERT |
| TrackUsageReservation | F0_FOUNDATION | NONE |

TrackPlan, TrackEntitlementDefinition and TrackPlanEntitlement are SELECT-only for the particular approved Free revision/benefits and existing selected plan facts. Existing valid selection is not invalidated just because catalog publication changes. PlanPrice and OrganizationFeatureAccess are outside this F0 handler and receive no permission.

TrackSubscription and TrackEntitlementGrant admit only the appropriate new provider-neutral Free enrollment and exact typed approved benefit rows. Existing subscriptions and grants are never updated/deleted by this handler. TrackBaseSelection permits missing-row INSERT, or a CAS UPDATE of subscriptionId/revision/sourceGeneration only when no valid current Free or paid selection exists and the new Free subscription belongs to this same command transaction. User/track/profile binding cannot change; revision advances exactly once. A competing valid paid selection is preserved.

TrackEnrollmentReceipt is read by its original source/profile semantic key and appended only when that receipt is absent. Identical replay is read-only and changed fingerprint conflicts. TrackSubscriptionEvent admits only new history for actual new enrollment, not updates/deletes or manufactured replay events. Existing semantic receipts, grants and history are preserved. Server-stamped mutation identity is not an input column.

This handler has no SELECT/INSERT/UPDATE/DELETE on TrackUsageEvent, TrackUsageCounter or TrackUsageReservation. It never meters, resets, repairs or rewrites usage. Separately authorized test observers establish unchanged-usage assertions. Approved nonproduction catalog fixture preparation is a separate authorized step, never enrollment-worker catalog authority. Exact operations/columns/guards and denials appear in the regenerated access matrix and test setup, not an ambiguous combined INSERT_OR_UPDATE label.

The candidate checker contains a separately reviewed WA-R078 security oracle. It does not import the permission generator or derive its expected limits from matrix/test agreement. It checks allowed verbs, write columns, immutable/catalog/usage bans, handler/stage/row scope and preservation/CAS/identity guards. Adversarial cases inject the same forbidden operation into BOTH artifacts while keeping their operation lists equal, and require the independent policy rule to reject it. Counts are obtained from actual cases; no target count is invented.

### P0C-CTX-02 connection and ordering correction

Connection A runs once for each actual runtime/worker login: open READ COMMITTED, capture actual login/PID/xid before business reads/source locks, let separate issuer I authorize and COMMIT its immutable bound grant, then bind through A's permitted helper. Only after that do separate mutation connections commit one of three distinguishable scenarios before A's next protected statement:

- R uses the issuer credential only for the existing one-way own-grant revokedAt update and COMMIT.
- G uses a separately authorized Identity owner security-generation transition, with its own fresh tuple-bound grant and required CAS/evidence.
- G instead uses an authorized Customer owner source mutation with its own grant/CAS/history/intents. The synthetic case binds the tested sourceGeneration to CustomerProfile.revision; it defines no universal generation mapping for other owners.

Generation mutations are not issuer business-table writes. If an approved P0-C owner fixture operation is absent, that scenario stays NOT_RUN rather than inventing broader privileges. Each change commits before A attempts its original now-stale protected action. The action must deny without unauthorized source mutation, effect or disclosure. The legitimate separate change is not confused with a forbidden effect or rolled back by A. Current-spec regressions reject the superseded pre-source-transaction issuance setup, reversed order, wrong mutation credential, missing own grant and missing committed-change synchronization. Historical evidence is not scanned as if it were current instructions.

### Current evidence

The previous current native/source records are retained byte-for-byte as `database-candidate-corrections-native-validation-72e7673.json` and `database-candidate-corrections-validation-72e7673.json`. Fresh current records report the actual runs. The selection wrapper retains the existing proposed IDs and fingerprints the regenerated register. Runtime/database cases remain NOT_RUN. No new bundle/ZIP, schema, SQL body, runtime, container, database connection or hosted change is part of this continuation.
