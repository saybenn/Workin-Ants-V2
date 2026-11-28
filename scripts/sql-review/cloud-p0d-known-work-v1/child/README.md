# Cloud known-work child source draft

Source author /root/pending_packets. The bundle holds one synthetic Customer and one known WorkItem on a fresh source8 target at posture D. Runtime remains `NOT_RUN`. It requires the separate owning wrapper, exact source and literal review, and actual independent observations. The draft grants no operation approval.

The checked-in transaction owner and work-lease module are copied through stable ES2022/CommonJS compilation with the reviewed TypeScript 5.9.3 compiler and archived Node 24.22.1. The exact accepted Node-smoke fixture supplies the first six Customer statements. The emitter compares their six parsed INSERTs with the accepted App source, removes its seventh effect statement, and proves the remaining 179-field list equals the accepted App Customer source grant. Keep the existing two-migration source8 archive, the 32-row Worker ACL, and the accepted Worker service bootstrap. The same Work ID uses the exact 25-field App grant, 20-field claim grants and 16-field renewal grant. The prior accepted Worker and renewal suites provide SQL and authority provenance.

## Owning wrapper handoff

Use the exact source8 no-op hook before cleanup. Bind the committed child manifest and pristine archive, owned fresh CID and volume birth, no network/published ports, the exact cached image/daemon/socket, genuine two-migration identity, effective finalizer, real role and wrong-password evidence, all-client closure and authorized exact cleanup. Before the child starts, verify all 42 empty application fingerprints, the exact independent User seed from the App packet, both restored trigger identities, native parity, and the accepted `wa_identity_service_authority` service bootstrap. Verify the single authorization and receipt in the same XID at generation 0 with the exact linked reference and no revocation or predecessors. This step makes no WorkItem.

Use the six files in `runtime_files` at one distinct reviewed container path with exact owner/mode/size/hash inventory. Bind the exact archived Node binary and all 37 Postgres.js runtime files before dispatch. As UID/GID 65534, use an empty process environment and the exact existing command-line driver path with stdio pipes and no PTY. Provide one initial ASCII line listing `phase`=`INIT` then `app`, `worker`, `issuer` credentials in their canonical order. Send no stdout echo, DB URL, output token, or command argument containing credentials. The child uses one fixed private Node process and at most one active runtime/issuer pool pair. The Node process retains the original lease preimage in memory through the controlled sequence. The relay sends one compact command and waits for exact acknowledgement, global backend absence and independent SQL evidence before advancing.

| Phase | Expected committed database observation |
| --- | --- |
| INIT | Ready without opening a database connection. |
| SOURCE | Six committed Customer rows use exactly one runtime XID linked to the grant. The exact source/customer projection passes and no work/effect exists. |
| SCHEDULE | One pending work row links the committed default-Free intent. Fence and attempt both equal zero, lease and effect empty. |
| REPLAY | The replay returns `already_scheduled` at fence zero and leaves that entire work row unchanged. |
| CLAIM | Fence and attempt both become one, same work identity, an independently observed live exact deadline and digest, and the new grant's runtime XID. |
| LIVE_RECLAIM | The actual existing lease still has server time remaining and the current function returns `unavailable`. The entire row is unchanged. |
| RENEW | The deadline advances while the same lease is live. Fence, attempt, token digest, identity and every other business field remain exact. Only deadline and physical mutation XID change. |
| COPIED_HASH_RENEW | Present the already known stored hash as a synthetic wrong credential inside the Node process while the real lease is live. The current function returns `unavailable` and independently observed work remains unchanged. |
| RECLAIM | Observe actual server expiration of the same renewed row before dispatch. The new holder independently writes fence and attempt two with a fresh live deadline and different token digest, exact same work identity, and the new grant's runtime XID. |
| STALE_RENEW | Replay the old fence/preimage with its original grant scope against the still-live fence-two work. The function returns `unavailable` and the reclaimed row remains unchanged. |
| FINISH | Close stdin, then require exit zero, exact terminal PASS, empty stderr and closed pipes. No acknowledgement follows. |

`validate.phase_message` emits fixed phase lines. Clock steps require the server millisecond sample, within five seconds of the child's current clock. Each lease uses the fixed offset in `validate.CLOCK_OFFSETS`. Require a two-second server reserve at entry to live-denial and renewal phases. Reclaim waits only on a bounded monotonic clock for a read-only probe of the actual renewed deadline. A child timer closes stdin at 90 seconds. The owning wrapper enforces a hard monotonic session deadline including active calls and pool closure. Each driver has finite connection, statement, lock and idle timeouts. Expiration is observed from the database clock without modifying its value.

Before each continuation, stop on malformed framing, forbidden diagnostic, process/pipe uncertainty or a global client-closure failure. A successful nonterminal exchange returns one bounded JSON record and a final exact `WA_P0D_WORK_ACK|PHASE` line. INIT uses ordinal zero. EXIT1 STOP returns a bounded safe code and two booleans, with no ACK. Any validated sticky uncertainty suppresses further SQL and requires the enclosing exact cleanup. A closed typed STOP with no uncertainty preserves first failure and permits only the exact required closure checks. Finish requires EOF and the actual exit-zero status. Final output exposes no lease preimages, raw token hashes, pool passwords, or unrestricted provider text. The typed WorkItem observation uses a SHA-256 checksum of the stored hash, not the raw stored hash.

Use `observe-grants.sql` at each checkpoint and bind its single new exact grant XID with `validate.grant_observation`. Verify frozen grant fields and append-only prior grant rows, distinct issuers/runtime XIDs, and no foreign grants. `observe-work.sql` returns the independent source count/XID, server sample, zero-client and side effect counts, and the framed one-row WorkItem projection. `validate.work_observation` checks its exact transition. Every side effect count stays zero, including all Track effect/inbox/attempt/enrollment rows. The accepted App `complete-state-observe.sql` supplies 42-table counts and hashes. SOURCE changes only the grant table and five exact source tables. SCHEDULE/CLAIM/RENEW/RECLAIM change only the grant and WorkItem tables. All other steps add only their exactly verified grant. Retain bounded typed proof before semantic comparison fails. After FINAL PASS and all-client absence re-observe the full native catalog, both migrations and all eight ledger columns, and exact owned cleanup.

This route qualifies only the bounded known-work schedule, same-row replay, serial claim/renew and real-time reclaim module smoke if the later literal actual evidence passes. It supplies zero assertion promotions and no integrated dispatcher, stale completion, overlapping holders, process-crash recovery, hosted authority, release, or business Track processing claim.

## Offline verification

On a fresh Linux amd64 Cloud checkout with CPython 3.12, install the repository's exact toolchain and parser. Apply the export command each setup script prints.

```bash
bash scripts/setup-cloud-phase0-v1.sh
bash scripts/setup-cloud-f0-parser-v1.sh
```

From the checkout root, reproduce the tools archive and stage the offline compiler and models in private scratch. Both models use the generated `bundle` directory.

```bash
wa_checkout=$(pwd -P)
wa_tools=$(mktemp -d /workspace/scratch/wa-known-work-tools.XXXXXX)
wa_child=$(mktemp -d /workspace/scratch/wa-known-work-child.XXXXXX)
wa_archive="$wa_tools/pinned-prisma-tools-cloud-v2.tar.gz"
wa_source="$wa_checkout/scripts/sql-review/cloud-p0d-known-work-v1/child"

python -B scripts/sql-review/package-cloud-prisma-tools-v2.py \
  --source-root "$wa_checkout" --npm-cache "$npm_config_cache" \
  --node "$(command -v node)" --output "$wa_archive"

cp -- "$wa_source"/{README.md,prepare.py,validate.py,observe-work.sql,observe-grants.sql,test_validate.py} "$wa_child/"
for wa_leaf in emit.cjs known-work-child.mjs test-child.mjs; do
  cp -- "$wa_source/$wa_leaf.txt" "$wa_child/$wa_leaf"
done

(
  umask 077
  cd -- "$wa_child"
  python -B prepare.py --source-root "$wa_checkout" --tool-archive "$wa_archive" "$wa_child/bundle"
  bundle/node test-child.mjs
  python -B -m unittest -v test_validate
)
```

The compiler verifies the exact checkout sources, archive and archived Node bytes. It prints the SHA-256 of the generated `bundle/manifest.json`. The Node model runs the compiled owners with a simulated driver. The Python tests exercise receipt validation, grant and transaction bindings, and WorkItem state comparisons. These commands require no database or Docker access.
