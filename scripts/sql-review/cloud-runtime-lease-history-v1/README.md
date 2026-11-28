# Cloud two-migration Prisma launcher

This packet prepares the inner launcher for P0-C checkpoint 3.8. It takes the two existing migration SQL files, the provider lock and the existing foundation schema. The migration IDs, paths and checksums are preserved. The compiler checks the historical guard, runner and config hashes before rendering three Cloud-specific files. The fresh history manifest is the eighth file. Its effective native expectation remains `cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4`.

The runner accepts only `deploy` and `status` for the synthetic `wa_p0c_rehearsal` database through the restricted `wa_migrator` login on the verified container's loopback. The candidate requires a reviewed Cloud host controller to establish target ownership, exact mounts, credentials, original-grantor finalization, native and ledger evidence, process closure and cleanup. Preparation and offline tests leave runtime at `NOT_RUN`.

## Prepare the held packet

Use the tool archive reconstructed from the checked-in [Cloud v2 tool closure](../../../context/reconciliation/local-f0-tooling/cloud-v2/prisma-tools-closure.json). It binds the reviewed Effect 3.22.1 dependency and the original pinned Node, Prisma and PostgreSQL schema engine. Its size is 113,920,987 bytes and its SHA-256 is `5a5deaff7aa721dd3b26be84f3ab1e9da1c1880ad902bced3be39dd5cc9e15f5`. The compiler independently verifies all 10,300 paths, hashes and exact lengths against the approved inventory.

From the repository root, call the preparer with a fresh UUIDv4 and the daemon observation object measured by the Cloud Docker guard in this session:

```sh
python -B scripts/sql-review/cloud-runtime-lease-history-v1/prepare.py \
  --run-id "$run_id" \
  --daemon-observation "$daemon_observation" \
  --tool-archive "$tool_archive"
```

`daemon_observation` and `tool_archive` are canonical absolute paths under `/workspace/scratch`. The observation file contains the daemon object itself. It carries `daemon_id`, `version`, `os`, `architecture`, `rootless`, `docker_binary_sha256` and the observed socket object with `real_path`, `device`, `inode`, `uid`, `gid` and `mode`. The host must compare fresh measurements before use. The generated operation directory is `/workspace/scratch/wa-cloud-f0-two-history-<run-id>`. Its three entries bind the held run manifest, exact eight-member source tar and their fingerprints. Keep the `private` child absent until the owning controller begins reviewed resource creation.

`prepare.build(root, run_id, daemon, tool_archive)` returns the parsed manifest, its canonical bytes and the eight path-to-bytes entries. `prepare.archive_source(files)` produces the exact public archive. Bind the compiler inputs, archive and manifest to the full committed and independently reviewed host packet before creating resources.

## Call from the reviewed host controller

Use the target names, labels and bootstrap path in the manifest. Start only the exact newly inspected container and volume on the measured local Docker socket. In the container, the independently reviewed host/controller must stage the eight source files in `/run/wa-f0-source` and the 10,300 pinned tool files in `/run/wa-f0-tools`. Use root-owned regular files with the archive modes and retain the exact run-bound source inventory.

Use `prepare.attest(manifest, observed, operation)` to encode stdin for one invocation. The `observed` record comes from fresh host inspection and has these fields.

- `endpoint` is `unix:///var/run/docker.sock`, and `daemon` is the live daemon observation matching the plan.
- `container_id` is the full engine-assigned ID. `container_name`, `volume_name` and `volume_created_at` come from exact container and volume inspection.
- `image` is the pinned qualified image reference. `image_id` is its measured local store identity.
- `network` is `none`, `published_ports` is false and `labels` matches the run labels.
- `bootstrap_secret_host_path` is the exact POSIX bind source and `bootstrap_readonly` is true.

Stage the no-newline restricted-login URL at `/run/wa-secrets/wa-cloud-runtime-lease-history-v1-migrator-url` in the private root-owned mode-`0700` tmpfs. The URL file is mode `0600`. Size this mount in the reviewed operation profile for the complete attestation and Prisma's private cache. Pass the URL through the controller's private credential writing route. Supply the attestation JSON over stdin and use a cleared launcher environment in the exact container as uid 0:

```sh
/usr/bin/env -i /run/wa-f0-tools/node/bin/node \
  /run/wa-f0-source/scripts/sql-review/cloud-runtime-lease-history-v1/runner.mjs \
  --execute-reviewed-cloud-f0-runtime-lease-history-v1 --operation "$operation"
```

Before dispatch, the inner guard verifies the container hostname, loopback-only interfaces, private tmpfs and read-only bootstrap mount, file modes and the full source and tool archives. It checks the credential route, manifest and operation binding. The host verifies the result's operation, attestation hash, daemon and resource IDs, source hashes, client closure and exit status. Catalog, ledger and repeated-deployment comparisons still supply the independent proof for the database behavior.

## Offline verification

```sh
python -B scripts/sql-review/cloud-runtime-lease-history-v1/test-prepare.py --tool-archive "$tool_archive"
```

The focused suite uses the actual 10,300 extracted tool hashes, source bytes and pinned Node 24.22.1. It demonstrates that exact streaming reads accept the 126,879,696-byte Node and 23,516,472-byte engine while preserving the smaller bound for ordinary files. Container identity, mounts, credentials and child dispatch are modeled. The result covers the launcher and its guards. The host operation and database evidence are pending.
