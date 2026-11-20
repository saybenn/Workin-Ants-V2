The optional ledger proof closes the genuine Prisma client-ledger exception only.
It neither initializes nor repairs a ledger. It executes no process or SQL.
Missing native evidence remains INCOMPLETE; invalid evidence fails. Public-schema
baseline and application catalog/expression checks remain independent gates.

Expected structure comes from Prisma engine commit
`d1b3f377ca835d73fd50954a5e22128b9ebdd6b8`, identified by the pinned local package
and the reviewed runtime tool attestation. `prisma_ledger_proof.py` records exact
primary-source URLs for its eight columns, the one successful step per script,
failure/rollback write shapes and exact new-checksum codec. PostgreSQL REL_17_11
supplies native defaults, primary-index conventions and eight table privileges,
including MAINTAIN. No first-observed table becomes an expected baseline.

Root prepares a registration BEFORE the collector operation, with exact approved
source bytes and expected history. For the one-success initial migration:

```python
registration = prisma_ledger_proof.build_registration(
    [{"path": "prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql",
      "migration_name": "20261117000100_f0_local_initial",
      "sha256": approved_migration_script_sha256,
      "state": "applied", "count": 1}],
    run_id=reviewed_run_id,
    target_attestation_sha256=reviewed_live_target_attestation_sha256,
    source_expected_sha256=source_manifest["expected_sha256"],
)
```

The exact checksum must come from reviewed source, never the database row.
Registration rereads raw bytes as strict UTF-8; CRLF/BOM bytes are not stripped.
The engine's historical checksum matching compatibility is deliberately not a
fallback for this fresh exact-source experiment. State/count expectations may
also describe a retained failed or formally rolled-back attempt using its own
approved source copy. Mark-applied/baseline adoption is unsupported. These inputs
describe existing evidence expectations and authorize no additional execution.

Default failed/rolled_back expectations require NONEMPTY logs. A failure inside
the canonical BEGIN can also abort the cached connection before the engine's
subsequent record_failed_step UPDATE; PostgreSQL can then reject that UPDATE
with25P02, leaving the started row's log column NULL. A later standard resolve
changes rolled_back_at without writing logs. This is a source-supported possible
path, not a retrospective cause or log-class finding for the old0c run, whose
complete log class and cause remain UNOBSERVED.

The optional registration mode is deliberately narrow: a failed/rolled_back row
may add `failure_mode: ABORTED_TRANSACTION_FAILED_STEP_PERSISTENCE` and a
`failure_proof_sha256` of one independently reviewed constructor-output artifact.
It permits exactly one zero-step, unfinished row with NULL logs. Registration
also requires a `failure_binding` pinning container_id, source_commit/tree,
packet_sha256 and the reviewed migration_server_diagnostics.py module SHA256.
The masked history expectation is registered before ledger collection and is
never selected by inspecting the history row.

For this mode only, the evidence envelope must add
`failed_step_persistence_proofs`, one artifact per masked expectation. The pinned
pure server-error module validates its closed protocol; the ledger adapter also
requires its exact predeclared hash, same run/container/source/packet/migration
directory/application hash, MASKED classification and NULL log class. The proof
requires the real owned terse-error channel's one exact allowlisted SET ROLE
42501 and at least one secondary25P02, no unrelated/malformed/private diagnostic
body, closed nonzero CLI, finalized original grantor and zero application objects.
This mode does not accept a NORMAL proof as masked evidence, reuse one proof
for multiple attempts, infer cause from NULL alone, or qualify a resolve command
without the root's separately reviewed genuine resolve provenance.

The independently reviewed root wrapper must establish genuine CLI provenance,
the exact local run/resources/image/database, authentication, finalization and
immutable source/tool mounts. Registration cannot prove those external facts.
The ledger must already exist in public with owner wa_migrator. The separately
reviewed `collect_prisma_ledger.sql` runs as the direct original bootstrap
superuser login in a repeatable-read READ ONLY transaction, after migration
connections exit. It first holds an ACCESS SHARE metadata lock, then runs a
catalog-only anonymous assertion of direct superuser identity, an ordinary
persistent heap table with correct owner and no inheritance/rewrite/RLS, and the
exact eight builtin column types. It stops before row reads on an unknown,
missing, view, foreign or unexpected type shape. History reads use FROM ONLY,
so an inheritance child cannot supply rows or code. It queries catalog
structure/ACL and minimized history only; it creates no persistent object.

The collector exports eight exact columns/default hashes, the sole PK and index
with their linkage/key/default-opclass/flags, complete table and column ACLs,
and absence of extra triggers/policies/rules/inheritance. It compares effective
table ACL, including PostgreSQL's NULL-ACL default expansion; it does not require
one stored NULL-versus-explicit owner-only representation. Dependent generated
type metadata is outside this narrow ledger proof.

History output contains hashes of migration name and checksum, UUID-v4/unique
and timestamp-order Booleans, step count and NULL/EMPTY/NONEMPTY log class.
It returns no raw migration IDs, migration names/checksums, timestamps or logs.
Complete normalized history is compared as a multiset, so missing, extra,
duplicate, unfinished, wrong-checksum or wrong-state records cannot pass merely
because one matching row exists. Per-row time ordering is checked; cross-attempt
execution sequencing remains part of the root's genuine command evidence.

The wrapper emits exactly this envelope, with no arbitrary extra metadata:

```text
format: workinants.prisma-ledger-evidence.v1
registration_sha256: SHA256 of canonical registration JSON
collector_sql_sha256: exact reviewed collector SHA256
run_id: exact registration run ID
target_attestation_sha256: exact reviewed target attestation SHA256
native_catalog_before_sha256: canonical full main native snapshot SHA256
native_catalog_after_sha256: the same canonical snapshot SHA256
observation: the single parsed minimized collector JSON value
```

Canonical JSON is UTF-8 `json.dumps(value, sort_keys=True,
separators=(',', ':'), ensure_ascii=False)`. Before and after snapshots must both
equal the actual main snapshot given to the comparator. The root wrapper must
collect them independently, verify target/connection exit, and stop on any
unexpected result. Merely writing equal hash strings is not a runtime proof.

Pass `--ledger-registration` and `--ledger-evidence` to the native comparator.
Legacy relation-only registration intentionally stays INCOMPLETE. Valid ledger
evidence removes only its own ledger gap; every other unqualified catalog,
runtime, replay, Privacy, usage, provider or deployment gate remains unchanged.
All runtime evidence is NOT_RUN until the root performs a separately reviewed
bounded collector operation. Posture D stays pending Brain evidence review.

Plain English: The migration tool keeps a small notebook. We know the notebook's
shape from the tool's own source and know the expected page from our approved
file. We compare those facts without copying private notes or changing a page.
