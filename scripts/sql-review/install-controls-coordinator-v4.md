# INSTALL V4: immutable binding closure and source semantic parity

All controls are **NOT_RUN**. Posture D applies. Root is the sole executor and
Git writer. The new generator, pure protocol, coordinator and mocked checks
change no canonical migration, historical provenance, role policy or existing
Prisma guard. Independent source review and a fresh literal operation review
must precede any execution.

`prepare-install-control-rehearsal.py --prepare` creates a new packet exclusively.
Its pure `prepare_history(root, manifest_bytes, variant)` returns seven new files
using the unchanged hash-pinned history helper. It never writes Root history.
The original canonical checksum is
`5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad`.

The packet contains three exact derivations:

- `canonical`: every original byte.
- `division_failure`: inserts `SELECT 1/0;` immediately before the last
  `RESET ROLE; COMMIT;`. All function setup precedes this immutable injected
  non-permission failure.
- `late_function_grant`: removes one exact existing EXECUTE grant for
  `bind_request_context(text)` and moves those same bytes immediately after its
  existing ownership transfer. No other grant or revocation is changed. The
  source owner role has NOINHERIT; its three temporary memberships have
  INHERIT FALSE. The transferred owner replaces the prior owner ACL entry, and
  default PUBLIC EXECUTE was revoked. A warning is unexpected. Qualification
  requires the actual server's exact native function permission failure.

The PostgreSQL 17 [GRANT documentation](https://www.postgresql.org/docs/17/sql-grant.html)
distinguishes an error when a nonowner has no privilege from a warning when
some privilege exists without grant option. The pinned PostgreSQL 17.11
[aclchk.c](https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/aclchk.c)
implements that distinction in `restrict_and_check_grant` and formats
`permission denied for function %s` in `aclcheck_error`. This is the expected
source branch, not a claim about any historical unretained error.

The dormant CLI is:

```
python scripts/sql-review/run-install-control-rehearsal-v4.py \
  --execute-reviewed-install-controls \
  --reviewed-run-plan <external reviewed JSON> \
  --evidence-directory <fresh external child directory>
```

The closed plan schema is `workinants.install-controls-run.v1`, with exactly
`schema`, `scope`, `run_id`, `source_commit`, `source_tree`, `packet_sha256`,
`reviewed_packet_sha256`, `source_modules_sha256`, `targets`, `histories`, and
`credential_bundle`. Scope is `FINITE_INSTALL_HISTORY_AND_AUTHORITY_CONTROLS`.
Source commit/tree and the full operation packet are pinned and independently
verified by the outer operator before it creates anything or calls this CLI.
The coordinator separately verifies the closed nine-module graph, every packet
input/artifact and every immutable seven-file archive before executing any
project helper. The context loader supplies verified cached transitive imports.
The generator/history helper also consume the same cached admitted bytes.

`targets` has exactly `canonical`, `division_failure`, and `late_function_grant`.
Each value has `name`, `volume`, and immutable `container_id`. Names are exactly
`wa-p0c-<run8>-install-good`, `-install-division`, and `-install-order`, with their
corresponding `-data` volumes. All three immutable IDs must differ. The outer
operator creates all targets from the independently verified pinned Postgres
17.11 Linux/amd64 image with network none, no ports, root private tmpfs,
readonly run-owned bootstrap binds and owner-only private host files. It owns
the original-grantor finally path, exact CID/name/labels/volume CreatedAt
cleanup, secret deletion and independent absence confirmation.

The outer operator must **not** call the old all-role bootstrap activation
function. It initially starts only the original postgres login. The coordinator
requires empty app namespaces, no `wa_` roles and no existing ledger, then runs
the unchanged bootstrap as postgres in its own connection. It sets only the
dedicated migrator password. The other four LOGIN roles keep NULL verifiers.
Candidate passwords can already be in protected private files; that does not
activate a database login.

`credential_bundle` names the same run's owner-only
`private/install-role-passwords.json`, a closed target-to-role map of eighteen
independent 64-character hexadecimal candidates. Passwords stay in RAM and
private files. They are never argv, URLs, exported diagnostics or evidence.
Before invocation, Root installs a root-0600 `pgpass` file and six distinct
`wrong-<role>.pgpass` files under root-0700 `/run/wa-secrets`, plus the fixed
private migrator URL required by the unchanged host/Node guard. Both correct
and incorrect candidates are synthetic and must be included in outer secret
scanning/cleanup. The coordinator checks actual SCRAM `system_user` identity,
loopback endpoints, rejected wrong-password startups, and global closure.

`histories` has exactly `canonical`, `division_failure`, `late_function_grant`,
and `division_recovery`. Each value has `manifest` and `source_archive` bindings
with exactly `path`/`sha256`, plus the exact seven `source_files_sha256` entries.
`division_recovery` binds separately preserved canonical bytes to the SAME run
and immutable division target. Every manifest is an unchanged guarded
`workinants.local-f0-run.v1` manifest, with the exact immutable variant checksum,
fresh helper-generated provenance, the exact runtime three and original 10,300
tool closure. Root provisions only the reviewed tooling before invocation.
Each staged archive is hashed/read once and sent as those same binary bytes to
the fixed in-container directory; no mutable file path is reopened by Docker.
The old host archive and seven-file fault snapshot remain preserved forever.

For the positive target, the closed actual Prisma result must succeed before
the activation gate can record install completion. The gate still refuses
activation until postgres separately finalizes and observers independently
confirm all three temporary memberships and all leaf CREATE privileges absent.
Before that cleanup, the exact original finalizer is attempted as wa_migrator:
only its source-bound P0001 original-grantor refusal qualifies, and all original
temporary edges/options must remain unchanged. Four actual rejected startups
and a NULL-verifier observer prove inactivity before install and again after
cleanup but before activation. Only then can one actual activation occur, with
all four correct/wrong SCRAM controls. A genuine second deploy must report no
pending work, preserve the complete minimized ledger and preserve the schema
dump fingerprint. This proves the wrapper's activation order, not prevention
of a hypothetical privileged administrator changing passwords.

For each failing target, original-grantor finalization precedes the safe state
observers. Failure qualification requires a closed nonzero actual Prisma result,
the exact source-bound primary server diagnostic, one actual failed immutable
ledger row/checksum and zero app relations of EVERY kind, functions, types,
enums and other clients. The server uses the fixed terse `WA_F0_DIAG` prefix,
`log_statement=none`, `log_min_error_statement=panic`, `lc_messages=C`, and exact
17.11. Only fixed typed counts escape log parsing. Unknown bodies, identifiers,
DETAIL/HINT/CONTEXT and SQL are discarded. A measured secondary 25P02 plus
actual NULL logs is a separately labeled observed masking path; P3018 is claimed
only if it appeared in the actual bounded CLI result. Historical 196c and other
unretained error causes keep their existing meanings.

The division rollback proof is written canonically to the fresh evidence
directory and waits at most 240 seconds for an independent reviewer. Approval
is `workinants.install-independent-rollback-review.v1`, with exactly `schema`,
`decision`, `run_id`, `container_id`, `source_sql_sha256`, `proof_sha256`, and
`reviewer`. Decision must be `APPROVED_STANDARD_RESOLVE_ROLLED_BACK`; all
identities and the exact canonical proof hash must match. Root executor is not
an allowed reviewer. No standard resolve or recovery SQL precedes this review.

Recovery first uses the unchanged standard `resolve-rolled-back` command against
the FAULT manifest, verifies only rolled-back state changed in the retained
failed row, then rearms ONLY the original three temporary memberships through
postgres. Their exact grantor/admin/inherit/set options and absent CREATE are
observed. It stages the separate approved canonical history, genuinely deploys,
finalizes, verifies the retained failed row plus one canonical finished row,
activates only after verified success cleanup, and genuinely deploys again.
Complete ledger and DDL fingerprints must remain identical. Applied checksums
are never edited. No direct ledger mutation, absent-object adoption, reset,
db push, shadow or hosted target is supported.

Every database/Prisma process boundary has a global all-databases/all-roles/
all-tags client-absence observer before a verdict or subsequent state observer.
Observer errors retain fixed unconfirmed flags. The finally path independently
attempts original-grantor cleanup for every attempted bootstrap and global
closure for every target; uncertainty stops and cannot produce PASS. The outer
operator must still clean exact owned resources on any returned/throwing error.

The finite result deliberately remains
`PASS_FINITE_INSTALL_PROTOCOLS_PENDING_FULL_NATIVE_COMPARISON`. It does not
substitute object counts or a schema fingerprint for the separately reviewed
full native ACL/structure/oracle/ledger comparison. The old 42501 masked-ledger
adapter is immutable and is not reused as an invented 22012 proof. A fresh outer
operator and applicable source-derived native/ledger expectation remain needed
before qualifying private-ledger/ACL criteria or a compound whole case. No
source-only assertion, whole 94/451 inventory, owner API or production readiness
is promoted here.

Plain English: Try one good toy setup and two broken copies. Keep four keys off
until the good setup and cleanup are checked. Keep the failure ticket when a
reviewer allows a retry. These steps and their database checks have not run.

V2 closes INSTALL-SOURCE-01. Before the first project helper compiler runs,
all four cached nested manifests must carry exactly the same 10,300 paths and
hashes as the cached source-pinned `prisma-tools-closure.json`. That JSON is an
explicit packet dependency. Reduced, same-count changed-critical, and cross-target
whitelists reject even when their manifests/provenance/archives are rehashed.
Existing host/Node guards and every SQL/control protocol remain unchanged.


V3 immutable independent review transport
---------------------------------------
The outer operator completes and closes install-coordinator-run-plan.json,
then publishes the minimal independent-review-outer-identity.json. The child
binds both exact files to its actual run, packet and three captured CIDs.
After actual division failure, original-grantor finalization, zero inventory,
retained failed ledger and inactive runtime gates, it writes the canonical
rollback proof. It completes the review-hold evidence save, takes those exact
completed bytes as independent-review-child-snapshot.json, and publishes the
fixed independent-review-ready.json LAST. Every input is a fresh regular
non-symlink single-link bounded file. Windows non-overwriting rename publishes
closed fsynced temporary files; hardlinks and replacement are forbidden.

Only after ready publication finishes does the unchanged240-second clock
start. The child performs no saves, stages, records, mutable reads or writes
during the hold. The versioned disk-only watcher polls only ready existence,
then reads the closed immutable ready/proof/snapshot/identity/plan with strict
UTF8 JSON, duplicate/nonfinite rejection and exact hashes. All read handles
close before detached data is reviewed. Its conservative deadline is220 seconds
after the last verified marker absence. Root monitors stdout and executor
completion only, never live outer or child reports. Immutable files remain
unchanged through timeout, failure, standard resolve and cleanup.

Transport validation is not rollback approval. A distinct eligible reviewer
must inspect the actual failure, ledger, source, CID, native observations and
original authority, then explicitly provide the existing seven-field decision
under unchanged install_control_protocol_v2.py. Atomic approval publication
rechecks all immutable inputs, remaining deadline and zero open read handles.
The watcher default never constructs or issues approval. No actual approval is
prepared by source tests. All source gates remain PENDING until independent
review, publication, pinning and a fresh operational literal.

The watcher stdout receipt includes its source and arming digests, exact ready
digest and the already-computed conservative monotonic deadline. The eligible
reviewer retains that receipt and supplies that same deadline to the separate
publish_explicit_approval action; it must never start a fresh220-second budget.
The action reopens only immutable inputs, closes them, validates protocol6c's
exact seven fields, and checks the retained deadline again immediately before
the non-overwriting atomic rename. The receipt is timing evidence only and is
never a rollback approval. The operation literal must bind the watcher source,
arming bytes and distinct assigned reviewer before launch.

The outer first-save diagnostic records only the first failing phase, a closed
exception-class enum and allowlisted Windows error5/32/33 or null. It never
copies exception strings, paths, arguments, credentials or stack traces. It
does not retry, overwrite a primary exception or clear sticky evidence failure.
INSTALL7923's original cause remains unobserved; preserved held-reader scratch
failures establish only that readers must close before mutable saves resume.

Plain English: Finish writing a sealed note before the checker opens it. The
checker closes the note before handing back a separate signed answer. The
working notebook can then change without bumping into an open reader.

The V4 child and generator preserve the previous behavioral functions and all
11 SQL artifacts byte for byte. The V2 pure transport binds the exact five new
owned-parity-v4 filenames; the V3 disk watcher preserves the same explicit
seven-field review authority, sealed handoff and conservative 220/240-second
deadlines. Old protocol, watcher, coordinator and histories remain intact.

The new outer comparison runs only after canonical and recovered targets each
pass their full source comparator, 416 expression oracle, complete ledger proof,
original-grantor finalization and all-client closure. It retains the original
raw snapshots and their distinct hashes. Its additional keyed semantic view
validates every source-derived internal trigger identity and its exact per-row
generated prefix plus digits, then omits only that validated internal name from
cross-target equality. All 20 other fields, all source-declared external trigger
names and fields, and all 26 other sections remain exact. Duplicate, missing,
extra, unknown or malformed rows stop. No result or runtime approval is inherited
from the closed b778 attempt. All new runtime remains NOT_RUN under Posture D.

Plain English: The database gives hidden safety triggers new number tags in each
new box. We still check every trigger and every safety detail. We compare what
each trigger does, keep both original reports, and ask a reviewer before a new try.
