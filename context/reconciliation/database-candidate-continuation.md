# Continuation — first P0-D slice and remaining evidence

> Current amendment P0-C-03A: [corrected SQL source review](foundation-sql-draft-review.md) and [retained directive](directives/brain-directive-p0-c-03a.md) supersede earlier drafting-stage gaps/next actions in this historical source plan. Source and SQL drafts only; posture D; all 451 database/runtime cases NOT_RUN. Independent Identity currentness, narrowly enumerated read-only Boolean ports, append-only age evidence and both added owner revisions are present for re-review, not execution-approved. No human setup task.

This is a recommendation and test specification, not runtime implementation or activation permission.

## Smallest coherent owner slice

Use the actual **Customer buyer-profile provisioning → default-Free Track enrollment** handoff from WF-01 and WA-R019/R030/R078. It needs no fabricated business domain, real payment, screening vendor, therapy, prize system or product screen.

Producer: **customer_buyer_profile**, resolveCustomerActor/provisionDefaultCustomerProfile. Public/shared contracts: **SH-004.v1**, **SH-114.v1**, **SH-044.v1**, **SH-031.v1**, **SH-046.v1**, **SH-047.v1** (enqueueReliableJob), **SH-051.v1** and **SH-052.v1** where locking/CAS applies. Trusted actor/policy/Consent prerequisites remain SH-001/002/007/008/009 as applicable. The Customer leaf fact variant is exactly **customer_buyer_profile.authority_facts.v1** in family-variants.json; it does not load foreign repositories or recursively authorize itself.

Consumer: **track_subscription_entitlement**, existing **assignDefaultFreeTrack.v1** command under R078. This is a registered owner command intent, not a newly invented actor-created event. Its payload binds source owner, User, customer track/profile, source creation revision/receipt and the original semantic identity. The source lifecycle fact uses the existing **customer.lifecycle_changed.v1** vocabulary; SH-046's event shape is not misused for a command. Both kinds share the same outbox/work persistence family with distinct registered schemas.

Proposed path:

1. Resolve trusted current actor and applicable source/Consent/Hold scope. Open READ COMMITTED and capture the actual connection/xid tuple before business reads/source locks; the separately credentialed issuer commits immutable tuple-bound context, then the source transaction validates it before taking locks. Reject a client-selected foreign userId or supplied grant/role assertion.
2. SH-004/114 creates one CustomerProfile under unique userId, or returns the existing source identity. SH-044 holds the scoped semantic key/fingerprint. Same key/body replays; changed meaning conflicts.
3. On actual creation, one local transaction commits CustomerProfile, CustomerProfileLifecycleEvent, minimal OwnerMutationEvidence, durable command result, the required lifecycle fact and assignDefaultFreeTrack command intent. No synchronous Track or provider wait. A pure resolve/replay does not create a second source event or enrollment intent.
4. Shared worker claims RuntimeWorkItem under a lease and increasing fence. It validates the message kind/name/schema and obtains current service/owner authority. Track rechecks the Customer leaf facts and exact source/User/profile correspondence, not merely the message's assertion.
5. The source fact check occurs before network/source locks. Within the coordinated database transaction a narrow owner-approved fixed Customer binding/currentness check prevents a stale source from committing after its relevant generation changed. No raw foreign Prisma repository, global owner loader or network call under locks. The integration owner specifies consistent source/selection lock ordering in the implementation slice.
6. Track serializes User/track, retains one TrackBaseSelection, creates explicit provider-neutral Free enrollment only if appropriate, and commits TrackEnrollmentReceipt, required Track history, semantic effect receipt and inbox receipt atomically. A valid current Free or paid base is preserved. Delayed Free cannot downgrade paid selection or reset same-period usage.
7. Worker acknowledgment follows actual receipt. Crash/lost acknowledgment replays the same effect identity. Unknown/unavailable stays pending/reconcile-required; it is not implicit Free or a reason to release an unresolved reservation.

Acceptance goal: **no repeated committed business effect despite retries**. Network delivery remains at least once; no exactly-once promise is made.

## Exact proposed file boundary

These are planned files, currently **not implemented**:

- features/customer_buyer_profile/application/resolve-customer-actor.ts
- features/customer_buyer_profile/domain/customer-profile.ts
- features/customer_buyer_profile/infrastructure/customer-repository.ts
- features/track_subscription_entitlement/application/assign-default-free-track.ts
- features/track_subscription_entitlement/infrastructure/track-enrollment-repository.ts
- server/platform/persistence/owner-transaction.ts
- server/platform/runtime/command-receipts.ts
- server/platform/runtime/outbox.ts
- server/platform/runtime/work-leases.ts
- server/platform/runtime/inbox-effects.ts
- server/platform/security/database-action-context.ts
- tests/integration/phase0/customer-default-free.postgres.test.ts
- tests/support/phase0/synthetic-authority.ts

The migration integrator alone authors any approved schema/history/security change. This recommendation activates no candidate lane and does not let these owners modify canonical contracts or foreign source tables. Existing archival Customer commands are not implemented merely to test a stale source; the approved synthetic fixture setup can represent an archived/revoked source for the consumer's denial tests.

## Minimum security and Privacy entry conditions

The approved F0 schema and SQL history must first pass real P0-C installation/catalog/role/invariant tests. Context issuer and runtime credentials are distinct, application/worker have no bypass/ownership/DDL rights, transactions isolate pooled context, and payload/field schemas reject untrusted actor/source claims. Exact required source/Consent proof and current generations are checked. Proof/receipt bootstrap is nonrecursive; optional Ops never becomes an authorization prerequisite.

Synthetic Identity/authority fixtures may be provided by an explicitly test-only trusted attestor in an isolated environment. They exercise actual database logins and owner guards, not a fake production domain. They do not qualify a live Supabase authentication provider or authorize a public endpoint. Before production scope, actual SH-001/002 and applicable age/eligibility/Consent/provider evidence must replace that test-only authority boundary. The owner command must never silently accept fixture authority in a production build.

No real resumes, health/tax records, payment details or private source bodies belong in this slice. Customer metadata, subject identifiers and grants remain internal. Owner generation/field-map/retained receipt handling must already prevent stale restoration or unauthorized export/deletion of the slice's data; broader P0-F inventories and provider/backup outcomes remain separately gated. Draft legal content is nonproduction-only and never turns into final production acceptance.

## Planned runtime tests

The machine plan names P0D-REPLAY-01, CRASH-01, FENCE-01, DOWNSTREAM-01, ROLLBACK-01 and SOURCE-REVOKED-01. Each is **NOT_RUN**. They cover identical/conflicting replay, simultaneous creation/update, failure inside the owner transaction, crash before/after consumer commit, lost result, reclaim, stale worker late execution, wrong/archived/revoked source, unavailable Track, Free/paid race and unchanged same-period usage. There must be one Customer source and one recognized enrollment effect; pending work remains durable until an actual explained result.

P0-C tests exercise real schema/roles/constraints using SQL fixtures and do not claim this worker/adapter loop exists. P0-D tests implement and exercise the loop. P0-E adds full actual actor/owner/field/server-RLS parity; P0-F adds actual complete privacy/provider/bytes/backup execution. This separates prerequisites and avoids requiring the whole runtime to qualify its own persistence.

## DBP-01–12 continuation

- DBP-01/02/04/05 retain Checkpoint 009's scoped target/environment/version/empty-namespace evidence. They do not approve a schema or hosted execution.
- DBP-03 remains partial: preserve the older target and every managed namespace; actual preservation/backup/disposal obligations must be established before affected recovery/destructive actions.
- DBP-06/07/08 now have concrete candidate, SQL-only, access and comparison specifications, but actual post-install comparison, API exposure/role behavior and privileged-function disposition are NOT_RUN.
- DBP-09 has a complete source-review package ready for Brain review: all 177 original models, individual compatibility dispositions and required/staged additions. Candidate approval/adoption and physical behavior remain unproven.
- DBP-10 has a concrete disposable replay/fixture/test plan. Actual identity/image digest/tooling, execution and recovery evidence remain NOT_OBTAINED.
- DBP-11 retains connected access evidence but no proved hosted backup/restore/retention guarantees. Synthetic local recovery can be tested separately; it does not close hosted requirements.
- DBP-12 remains NOT_OBTAINED: no adopted migration/schema/RLS/build decision or runtime freeze.

No missing future legal/provider rule blocks this source review. Real legal retention, identity/provider production capability, screening, tax, regulated data, therapy and prize activation still gate only the affected behavior. Initial scope remains U.S., 18+; prescribing, child-directed features, licensed therapy and prize competitions stay disabled. Ordinary rewards remain distinct. UI is in its separate thread.

## What would authorize the next step

Brain approval of the exact review hashes and ordinary technical choices is required before the separately specified **source-only SQL generation**. Then the edited structural/security SQL, environment bootstrap and exact disposable identity/actions require explicit execution authorization. P0-C-01 itself authorizes neither. Hosted project migration or provider-setting changes require their later scoped decision and relevant evidence. This checkpoint does not request product feature development or a broad launch approval.
