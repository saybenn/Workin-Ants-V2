# Cloud two-migration launcher with private stdin bootstrap

This version uses the bootstrap delivery demonstrated by probe `862971a5-3cdf-4cca-8189-e40e3318b081` at `fc5b5879abb5bd764fc0e5f5c1a03f95e2b0b7c8`. The compiler binds the exact startup and credential-write script digests, the named data volume, and the private memory-backed mount. The owning controller must independently verify the complete operation after the volume and container exist. The historical Cloud v1 host-bind port retains its own source and receipt identities.

The compiled archive has eight files. The two ordered SQL files, provider lock, Prisma schema and expected native catalog identity retain their original bytes and values. Config, guard, runner and run-bound history manifest use the Cloud v2 paths and schemas. The installer uses the exact patched Effect 3.22.1 tool archive with the same Prisma, pinned Node and schema-engine versions.

## Held preparation

Use a fresh UUID4 and the measured daemon record. Supply the exact Cloud v2 tool archive reproduced by the [Cloud tool-closure compiler](../package-cloud-prisma-tools-v2.py). The archive SHA-256 is `5a5deaff7aa721dd3b26be84f3ab1e9da1c1880ad902bced3be39dd5cc9e15f5`.

```sh
python -B scripts/sql-review/cloud-runtime-lease-history-v2/prepare.py \
  --run-id "$run_id" --daemon-observation "$daemon_observation" \
  --tool-archive "$tool_archive"
```

The command writes the manifest, eight-file archive and fingerprint binding to the fresh private scratch packet directory. Use `prepare.build(root, run_id, daemon, tool_archive)`, `prepare.target_for(run_id)` and `prepare.archive_source(files)` from an owning controller that manages its own exact packet. These commands produce only held source. Runtime and candidate qualification remain `NOT_RUN`.

## Owning controller bindings

The controller uses the real daemon record and exact host network, container and volume checks. Use `target.bootstrap` to bind the reviewed probe scripts and exact tmpfs options. The controller must verify the running kernel mount and loopback isolation before writing the bootstrap credential through exact container stdin. It must remove its bootstrap and pending leaves and verify their absence before Prisma dispatch. The operation profile uses eight megabytes for the protected mount. The synthetic full-closure attestation exceeds one megabyte.

`prepare.attest(manifest, observed, operation, packet_sha256=..., literal_review_sha256=...)` accepts only the current observed daemon, container and volume and the exact operation. Use the existing standard observation fields for daemon, image, resource IDs and labels. For the bootstrap observation supply `bootstrap` matching the target, `bootstrap_removed` true and `mount_destinations` equal to `["/run/wa-secrets","/var/lib/postgresql/data"]` after the controller verifies the complete actual mount inventory. Bind the source packet SHA and separately approved literal review SHA before this call. The hashes record which reviewed bytes the controller used.

The reviewed controller stages the exact eight source files and pinned tool files and checks their lengths and hashes before dispatch. It places the private mode-`0600` migrator URL at `/run/wa-secrets/wa-cloud-runtime-lease-history-v2-migrator-url`. Use the verified container and uid 0 with a cleared environment:

```sh
/usr/bin/env -i /run/wa-f0-tools/node/bin/node \
  /run/wa-f0-source/scripts/sql-review/cloud-runtime-lease-history-v2/runner.mjs \
  --execute-reviewed-cloud-f0-runtime-lease-history-v2 --operation "$operation"
```

The inner launcher checks the kernel mounts, private directory permissions, absence of both bootstrap leaves, exact tool paths, hashes and sizes, local restricted URL, daemon and run identity, source bytes, and the bound operation. It returns the Cloud v2 receipt with the operation, source hashes, packet and literal review hashes, stdin hash, daemon and container IDs, client status and bounded diagnostics. The controller verifies both process exits and the receipt. Ledger, native catalog, role closure, finalization, no-op and resource cleanup evidence remain separate from the launcher result.

The separate refusal receipt records only the finite phase, cause family and allowlisted code. It includes the stdin hash after bounded input is received and includes reviewed target and release bindings after the complete attestation is verified. Entering the child dispatch phase makes a refusal's child state unconfirmed. The controller retains its conservative stop and closure requirements on every refusal.

## Focused offline verification

```sh
python -B scripts/sql-review/cloud-runtime-lease-history-v2/test-prepare.py \
  --tool-archive "$tool_archive"
```

The test verifies both actual probe script pins, the eight source files and all 10,300 actual extracted tool hashes. It exercises the new attestation and review digest fields, mount layout, bootstrap-file absence and bounded runner behavior with modeled kernel and child process inputs. Candidate database evidence and operational review of the full owning composition remain pending.
