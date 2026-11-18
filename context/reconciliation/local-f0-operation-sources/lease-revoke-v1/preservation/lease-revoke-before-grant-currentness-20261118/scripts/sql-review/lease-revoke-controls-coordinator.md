This is a dormant finite SQL rehearsal for selected `P0C-TRACK-01` and
`P0C-CTX-02`. Those are the actual register IDs; `P0C-LEASE-01` and
`P0C-REVOKE-01` are not register entries. All source and runtime statuses remain
NOT_RUN until actual independently reviewed evidence is produced. Posture D
remains. No production worker, Identity adapter, owner-generation operation,
new permission, schema change or enrollment loop is supplied here.

The source packet contains three fresh complete Customer create groups, their
source-derived observers, one actual application-scheduled lease work item and
two application-service scheduler targets. User fixture setup is a separate
privileged transaction that restores only the reviewed users/security
`owner_commit` triggers before committing; the exact complete four-trigger
contract and absence of disabled project triggers are independently observed.
Every Customer source is created through actual `wa_app_runtime` under its own
user-principal grant. It commits command, Customer, history, evidence and two
typed outbox messages together. It never substitutes a service principal for
the Customer principal guard.

The new source generator uses exact pinned Customer/schema/worker-capability
helpers. It changes the synthetic namespace and generates new artifacts only.
Every worker token comes from the unchanged 32-row ACL ceiling. Claim fields
are the exact state/fence/hash/deadline/attempt fields; renewal changes only the
deadline. Select fields and exact predecessor revision are separately bound.
No old source packet or admitted operation is rewritten.

The fixed 19-protocol order is in `lease_revoke_control_protocol.py`. The worker
claims with a runtime 256-bit preimage, fence 1/attempt 1 and a 12-second actual
server-clock lease; a fresh renew grant extends it to 40 seconds. A live reclaim
denies. An old holder then captures/binds its original renew context without a
protected read/action lock. Its idle timeout is explicitly bounded at 60 seconds
to cover the at-most-45-second clock observer and the finite reclaim exchange;
statement and lock timeouts remain the pinned transport's 5 seconds/1 second.
The observer polls only `lease_expires_at<=clock_timestamp()` and fixed state
Booleans. It first requires the lease still live after the old holder binds,
then observes actual expiry. It never edits an expiry or uses privileged work updates.

After actual expiry, a separately closed renewal attempt must hit the exact
live-lease guard. The old idle holder remains open for the immediately following
declared concurrency step; its exact rollback work state/xid is independently
observed after the affected failed-renew backend closes, while the original
holder remains idle. The expired-renew result explicitly defers full state
observation to that step. A distinct actual worker PID/xid claims with a fresh
preimage, fence 2/attempt 2, commits and closes. The original holder then sees zero
work rows and updates zero rows under its old revision/fence capabilities before
rolling back and closing. Only after both close is the exact new state observed,
including the reclaim's captured mutation xid. This is the actual transport RLS
fence/CAS refusal. `worker_lease_valid()` requires a Track processing action, so
this packet does not label an always-false call under a renew grant as a proof.

The current holder renews to 90 seconds, then finite shortening, copied-hash,
old-secret, hash-change and attempt-only operations must fail at their exact
source guards. There is no attach/complete/effect/inbox/enrollment operation.
After completed finite protocols the full Customer groups remain coherent,
work/source outbox/semantic links match, attempts and Track footprint stay zero,
all trigger states and full native metadata are unchanged. Counters/fences are
compared to exact values; generic P0001/42501 alone never pass a denial.

Application revocation uses a separate synthetic service authorization and the
actual application scheduler scope, supported by the canonical source. Its
baseline work commits through the real app login. A separate actual issuer
revokes its own fresh tuple-bound read grant and commits before the original
app transaction's protected read; it must reveal zero rows. Grant retention
preserves every immutable field and compares the declared one-way revocation
plus trigger-assigned mutation xid to the captured revoker transaction.

For service-currentness, an actual separate narrow Identity authority commits
bootstrap, rotate 0→1, revoke 1→2 and recover 2→3, with exact immutable predecessor
receipts and receipt/authorization timestamp+xid linkage. A bound old application
scheduler grant cannot insert work after rotate/revoke. Old/revoked generation
binds fail at the exact binder guard. Fresh current generation reads and a fresh
recovered scheduler commit succeed only in their prepared scope. The current
synthetic service receipts are not production upstream authorization or a
qualified Identity owner adapter.

`control.security_generation_schedule` and `control.source_generation_schedule`
remain unprepared here. The current UserSecurityProfile owner transition and
committed Customer UPDATE result/no-result identity/codec cannot be invented.
The Customer generator's
`CUSTOMER_UPDATE_RECEIPT_NO_RESULT_IDENTITY_AND_CODEC_NOT_REGISTERED` gate is
preserved. Lease attach/recovery and the rest of the compound Track assertions
are outside this packet. Existing read-only worker currentness/first-claim
results keep their original partial meaning.

Future Root invocation must use:

```text
python scripts/sql-review/run-lease-revoke-control-rehearsal.py
  --execute-reviewed-lease-revoke-controls
  --reviewed-run-plan <fresh external reviewed JSON>
  --evidence-directory <fresh external directory>
```

The exact `workinants.lease-revoke-run.v1` plan has these closed fields:
`schema`, `scope`, `run_id`, `source_commit`, `source_tree`, `packet_sha256`,
`reviewed_packet_sha256`, `reviewed_content_sha256`, `source_modules_sha256`,
`target_manifest`, `immutable_container_id`, `native_snapshot`,
`native_comparison`, `native_attestation`, `case_names`. Scope is exactly
`FINITE_LEASE_AND_APPLICATION_CURRENTNESS_SQL_ONLY`.

`packet_sha256` identifies the full committed Root operation; the two reviewed
packet fields identify this fixture file and its recorded source/prepared-file
content aggregate separately. All eight module pins include this coordinator,
the pure protocol, the fixed CTX coordinator and its complete API/host/diagnostic/
history/collector chain. The source packet pins all used source/schema/context
inputs and every prepared file. Complete admission and same-run native proof
verification precede helper compilation; helpers compile cached bytes only.

Native references contain only `path` and `sha256`. The full comparison requires
the exact source expected digest, positive typed PASS count, no FAIL/INCOMPLETE
or findings, and the snapshot's canonical digest. Root must separately hash an
exact `workinants.lease-revoke-native-attestation.v1` envelope with run, created
CID, source commit/tree, full operation packet, collector and expected-source
hashes, native canonical/file comparisons, original-grantor finalization and
operation-backend absence. Its field shape is fixed in `load_inputs()`.
Root must complete genuine canonical install, original-grantor finalization,
full native/ACL/TEXT/expression/private-ledger proof, SCRAM/correct/wrong-password
controls and exact resource safeguards first. This coordinator creates or removes
no resource and changes no privilege.

The existing independently reviewed CTX transport captures the actual restricted
login/PID/xid before protected locks, commits issuance on a separate real issuer
connection, binds the same original connection, closes each actual backend and
retains exact grant rows. Secrets, raw handles, PID/xid values, timestamps and
arbitrary probe dictionaries stay private. Evidence contains only fixed source
diagnostics/markers, bounded comparisons and counts. Failure stops later cases,
closes all owned sessions, verifies permitted trigger/native preservation only
after closure, and retains safe partial evidence for Root's exact owned cleanup.
Closure uncertainty stops all further state observers. The final positive status
means the finite protocols completed, never that either selected compound case,
the 94-case selection or all 451 cases passed.

Plain English: We try a timed work ticket, hand it to a new worker after it runs
out, and make sure the old ticket cannot work again. We also cancel a permission
and check that it stops working. These small games have not run, and missing
owner features still have to be built and checked.
