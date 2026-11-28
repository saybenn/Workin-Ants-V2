# Cloud Customer predecessor owning packet

This version assembles the corrected twelve-file Customer test packet, the canonical initial migration, a derived seven-file runner archive, and the audited Cloud Prisma tool archive. The historical owning source, frozen reviews, SQL, and strict ordered 42-table check retain their committed bytes. The preparer binds the live daemon observation, exact checked-out and committed source, artifacts, fixture identity, and a distinct attempt identity.

From the repository root, run the offline tests. The database rehearsal also uses the pinned PostgreSQL 17 parser, `pglast==7.21`, in the Python path.

```sh
python -B -m unittest discover -s scripts/sql-review/cloud-customer-stale-predecessor-owned-v2 -v
```

After committing the complete source set, supply the exact rootless daemon observation in a JSON file and the patched Prisma tool archive produced by the Cloud tool packager. The daemon observation must match the reviewed Cloud capability receipt. The driver also checks the daemon and resource namespace before starting the actual attempt.

```sh
python -B scripts/sql-review/cloud-customer-stale-predecessor-owned-v2/prepare.py \
  --daemon-evidence "$daemon_observation" --tool-archive "$tool_archive"
python -B scripts/sql-review/cloud-customer-stale-predecessor-owned-v2/operate.py \
  --plan "$operation_plan"
```

The verification command reproduces the plan and files from committed inputs, checks local copies, and compiles the inherited source with narrowly specified Cloud changes. An independent reviewer supplies `independent-review.json` in the private run directory. The record binds the plan hash, run ID, source commit, source inventory hash, and approval of source, owned resources, safety SQL, binary transport, and operational literals. Evidence from the Windows run retains its historical identity.

The earlier Cloud probe stopped on an unexpected owner or mode for the host-mounted bootstrap file. The subsequent reviewed capability probe passed with an owned named volume and root-private tmpfs. This packet uses its same startup, kernel-check and stdin credential recipes under a new run identity. It validates the mounts before dispatch and removes the bootstrap inside the container before Prisma starts. The credential tmpfs is sized at 8 MiB for the complete attestation and private runtime files. Database execution and evidence admission remain pending.

An exact independent operational review and current Git source are required for the execution command. An attempt directory is used once.

```sh
python -B scripts/sql-review/cloud-customer-stale-predecessor-owned-v2/operate.py \
  --plan "$operation_plan" --review "$independent_review" --execute-reviewed-cloud-csp
```

The intended operation exercises correct and wrong passwords for the restricted roles, the initial migration, the original grantor's finalization after client closure, native catalog and expression checks, measured one-row migration history, the one-history Customer creation observer, three explicit rollback controls, read-only post-state proof, and exact resource cleanup. The maximum evidence remains one Customer stale-predecessor assertion. Posture D and the qualification counts remain at the admitted checkpoint.
