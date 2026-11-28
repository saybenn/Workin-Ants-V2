# Cloud TWO owning source preparation

This source stage reproduces the exact two-history PostgreSQL migration and verification inputs for independent review. The manifest marks every operation `NOT_RUN` and records posture D. It covers only the migration machinery subset in P0-C checkpoint 3.8. Application and worker qualification remain separately pending.

## Prepare and inspect

Use the task's observed Cloud daemon JSON matching the Cloud probe's actual version, keep the operation root under `/workspace/scratch`, and supply the exact patched Effect v2 archive. Set `PYTHONPATH` to the approved isolated Linux pglast 7.21 install used for the source check. The preparer records the parser's current version and installed file hashes for nonauthor review.

```sh
python -B -m unittest discover -s scripts/sql-review/cloud-two-history-owned-v1 -v

python -B scripts/sql-review/cloud-two-history-owned-v1/packet.py prepare \
  --daemon-observation "$daemon_observation" \
  --tool-archive "$patched_tool_archive"

python -B scripts/sql-review/cloud-two-history-owned-v1/packet.py verify "$packet"
```

Both commands require exact current and committed source bytes by default. Use the explicit `--draft` switch on both commands to prepare and read back worktree sources during review. A draft records no commit identity and remains a draft after verification. Prepare writes only new owner-private artifacts under the fresh run directory. Verification reproduces the complete source map, patched tool archive binding, parser pin, native sources, and eight source files. It reads back each file and binds the archive bytes.

The forty-two-table expected catalog remains `cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4`. Preparation reproduces all six independently reviewed native assets and the 416-expression oracle. The two SQL migrations retain their original bytes and ordering. Patched tools use their separate Cloud v2 archive and complete 10,300-member inventory. The original 435-file evidence graph and three historical review receipts remain byte-pinned.

## Operational gate

The old peer report includes a fractional timing and nested source maps. The new reader checks its exact historical bytes and typed decision fields. A fresh nonauthor source receipt and a fresh literal operational receipt must each bind the reviewed Cloud bytes and scope. Both receipts remain pending. The old Windows decisions carry source provenance only.

The initial Cloud source packet describes the inner guard's current bootstrap bind expectation. The actual Cloud probe could not prove that the owner-only host file arrived with the expected in-container ownership. The next version must bind the independent finding and reviewed startup gate with a credential placed in private tmpfs over standard input. The manifest stays held until both the inner guard and the owning controller consume that observed Cloud identity.

The proposed attestation is over one megabyte because it includes the full tool closure. The TWO profile reflects an eight-megabyte private tmpfs with the same no-execute, no-device, no-setuid and owner-only settings. This capacity remains pending operational review with the completed Cloud host controller.

The bridge is a pure callback adapter. It constructs only the run-bound source hash check, source length check, and cleared-environment inner launcher requests. It checks the exact Cloud receipt schema, daemon ID, source digests, standard-input digest, and both exit states. Child closure uncertainty stays latched after a missing or invalid receipt. The older finalizer, all-role closure checks, native and ledger logic, and exact resource cleanup remain the controller's responsibility. The current source tool exposes no execute command.

The required next owner work is to integrate the observed v2 bootstrap route, bounded transport and run-owned resource creation and cleanup. Preserve first-failure evidence, original-grantor finalization before activation, all 416 oracle comparisons, 29,089 native-check expectations at their recorded scope, and exact two-history ledger observations followed by real no-op deployment and eight-column parity. The controlled rehearsal follows independent review of the final source graph and live operational plan.
