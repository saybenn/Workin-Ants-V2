# Dormant UNIQUE transport

`run-unique-control-rehearsal.py` is a proposed actual subprocess transport for
the five finite races in the frozen UNIQUE packet. Source review, mocks and this
document authorize no execution. The external integration operator must review
the literal run plan, independently establish the fresh owned target and native
PASS, and handle resources, independent credentials, installation/finalization
and cleanup. The coordinator creates none of those things. Posture D and every
original database/control status remain unchanged.

The packet remains `fixtures.json` SHA-256
`5eb0ae5413e917cd50ab35d1e3be2b9f0b38006c2ce93241f589b863647c6875`,
with source/prepared-file aggregate
`bbb26d95da0f0592f542fb6e9e23e963519a5a8a6a5effb9c07870cecc82f79a`.
It contains 49 SQL files, its README and the manifest. No packet SQL, canonical
SQL, object definitions or permissions are changed by the transport. No Customer
UPDATE/CAS result, owner-generation port, app Attempt/Inbox route or worker loop
is implemented or qualified.

## Closed external plan

The explicit `--execute-reviewed-unique-controls`, `--reviewed-run-plan` and
fresh external `--evidence-directory` arguments are mandatory. The plan has
exactly these fields; no additional field is accepted:

```text
schema: workinants.unique-control-run.v1
scope: FIVE_FINITE_UNIQUE_SQL_STORAGE_RACES_ONLY
run_id: fresh lowercase UUIDv4
source_commit: reviewed full 40-hex source identity
source_tree: reviewed full 40-hex source identity
packet_sha256: reviewed full 64-hex operational packet identity
reviewed_packet_sha256: 5eb0ae5413e917cd50ab35d1e3be2b9f0b38006c2ce93241f589b863647c6875
reviewed_content_sha256: bbb26d95da0f0592f542fb6e9e23e963519a5a8a6a5effb9c07870cecc82f79a
source_modules_sha256: exact MODULES path -> reviewed raw-byte SHA-256 map
target_manifest: reviewed workinants.local-f0-run.v1 manifest
immutable_container_id: exact independently created full 64-hex container ID
native_snapshot: {path: external absolute path, sha256: reviewed raw-byte hash}
native_comparison: {path: external absolute path, sha256: reviewed raw-byte hash}
native_attestation: {path: external absolute path, sha256: reviewed raw-byte hash}
race_names: the exact ordered five packet race names
```

All external paths resolve inside the shared task directory and outside the
checkout. The native comparator must report full PASS, positive typed PASS count,
zero/missing FAIL and INCOMPLETE counts, empty findings and the exact expected
source digest. PG17.11, direct original-superuser collection and the canonical
native snapshot digest are mandatory. A comparison alone has no target identity;
the separately reviewed attestation must have exactly:

```text
schema: workinants.unique-native-attestation.v1
run_id, container_id, source_commit, source_tree, packet_sha256: exact plan values
collector_sha256: exact source_modules_sha256 collector pin
source_expected_sha256: 3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433
native_snapshot_sha256: canonical digest of the reviewed snapshot
native_comparison_file_sha256: exact plan comparison raw-byte hash
original_grantor_finalized: true
operation_backends_absent: true
comparison_status: PASS
```

The current frozen CTX transport and pure UNIQUE protocol have additional fixed
source hashes in the coordinator. Every module (including the complete
CTX/first-rehearsal/diagnostic and migration/history helper chains), packet file,
source input and native asset is read and hash-checked before any helper is
executed. Import and help execute only standard-library code. Helpers compile
the verified cached bytes. Every later SQL read verifies the raw bytes and
executes that same decoded read; collector and canonical diagnostic-source reads
follow the same rule. End-of-run hashes are additional preservation checks.

## Actual finite transaction transport

The original reviewed CTX Session provides bounded queue readers, the real
restricted app connection, exact actual login/PID/full-xid/backend-start capture,
random post-statement acknowledgements and independent exact-backend absence
checks. Only the exact immutable container ID is used for every psql call. The
live endpoint, image, mounts, labels and resource identity are rechecked, then
the original six-role authentication controls, logging/SCRAM settings,
finalization, full native parity, exact fixture-trigger restoration and fresh
synthetic namespace are required. Reuse is refused.

Only the two packet-declared Identity owner-commit triggers are bypassed by the
pinned setup transaction; physical/native guards remain active. Setup must
commit and close, then the exact four source-defined triggers/functions/enabled
states plus absence of any disabled project trigger are independently observed.
Restoration is checked before protected group/command execution and after both
operation connections close. No additional bypass or repair exists.

Each of ten app transactions captures its own tuple. A separate actual issuer
transaction creates a fresh private handle/hash and exact bounded grant, commits
and closes before that same app connection binds it. The pinned CTX path uses
the original issuer's `INSERT RETURNING` to retain only the source trigger's
generated `created_at` privately; it never assumes the supplied timestamp
survives. All other twenty grant fields remain source/actual-tuple expectations.
The same issuer later compares all twenty-one immutable fields, ownership,
nonrevocation and expiration, emitting only fixed Boolean/count outcomes. No
issuer ID, token, tuple or timestamp enters evidence.

For a collision, A's complete group is constraint-checked but remains open. B's
actual INSERT is sent asynchronously; only its exact BEFORE marker may appear.
At most forty privileged metadata observations within two seconds must prove
the actual B backend is active, waiting on a transaction-ID lock, and blocked
only by the actual A backend, which is idle in its transaction. Both actual
PID/backend-start identities are used in the predicate. Each observer subprocess
is bounded by the remaining deadline (at most one second), with fixed 500 ms
statement/lock limits. Captured full xids are bound through issuer grants; a
32-bit `backend_xid` is never compared with a full xid8.

A then commits or rolls back and closes. Commit requires B's exact psql exit 3,
no acknowledgement or later marker, native SQLSTATE 23505, exact source-bound
schema/table/unique-index diagnostic and `_bt_check_unique` in `nbtinsert.c`.
With RLS enabled PG17.11 omits key DETAIL; any DETAIL, unrelated/malformed/extra
error, control byte or other output refuses the verdict. Rollback requires B's
AFTER marker and acknowledgement, then B completes its complete group and
commits. The distinct-subject race requires both complete groups ready before
either commit and does not use a collision barrier.

## Evidence and stopping

Both app clients must exit and their exact backends must be independently absent
before business counts/coherence or partial rollback observations. Every winner
requires the packet's complete root/command/history/evidence/outbox coherence,
all five actual captured transaction witnesses and no Track enrollment. Native
catalog parity, trigger restoration and immutable issuer rows are independently
rechecked. A successful A commit is persisted immediately; an unexpected later
B failure cannot turn that winner into an assumed rollback.

Any unexpected result stops later races. Remaining sessions close before
bounded partial counts are attempted; unknown closure suppresses observations.
The exclusive external evidence directory receives atomic, incremental sanitized
JSON, including completed protocol snapshots, current stage, exact bounded
comparison outcomes, commit acknowledgements, closure and allowlisted diagnostic
metadata. Raw output, arbitrary errors, statement bodies, credentials, grant
handles/IDs, PIDs, xids and timestamps remain private or are discarded. Cleanup
always remains the external operator's responsibility.

Even all five component outcomes do not qualify production idempotency,
Customer CAS or the entire selected control. The pure source protocol labels
and original selected-control status intentionally remain NOT_RUN pending Brain
review of actual bounded evidence.
