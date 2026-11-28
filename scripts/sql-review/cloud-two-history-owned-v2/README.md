# Cloud TWO owned rehearsal v2

This is the owning controller for one P0-C two-history migration machinery experiment. It carries the real Cloud stdin-to-tmpfs startup evidence from capability run `862971a5` and verifies its independent cleanup record. Each TWO run adopts a fresh UUID, volume and container on the separately inspected daemon. The packet binds the two immutable migrations, exact current committed source, the patched Cloud v2 tool archive, the isolated parser and both independent Cloud reviews.

The controller uses the byte-pinned capability startup and cleanup implementation, with the TWO synthetic database name and the original conservative server log settings. The container has only the owned data mount and eight-megabyte mode-`0700` private tmpfs. A measured kernel check gates the exclusive bootstrap credential over standard input. The controller proves PostgreSQL is PID 1 and the bootstrap file is absent before proceeding. All database connections use the named verified container's loopback and synthetic reviewed roles.

## Prepare and inspect

Set `PYTHONPATH` to the approved isolated Linux pglast 7.21 install. Its files and Python version are bound into the packet. Provide the reconstructed Cloud v2 tool archive whose SHA-256 is `5a5deaff7aa721dd3b26be84f3ab1e9da1c1880ad902bced3be39dd5cc9e15f5`.

```sh
python -B -m unittest discover -s scripts/sql-review/cloud-two-history-owned-v2 -v
python -B scripts/sql-review/cloud-two-history-owned-v2/plan.py prepare --tool-archive "$tool_archive"
python -B scripts/sql-review/cloud-two-history-owned-v2/plan.py verify "$packet"
```

The normal plan requires all source bytes to match the current Git commit. Use `--draft` for offline source checks before a commit. Draft verification preserves the draft status. Every prepared plan starts with all runtime checks `NOT_RUN`.

## Bind both fresh reviews

After exact current source and capability checks, the nonauthor source reviewer writes `source-review.json` with schema `workinants.cloud-f0-two-history-source-review.v2`. The independent operational reviewer examines the exact current packet and live socket, daemon, image and resource absence before writing `literal-review.json` with schema `workinants.cloud-f0-two-history-literal-review.v2`. Each owner-private mode-`0600` file has these fields.

- `schema` and `decision` use the named schema and `APPROVE`.
- `reviewer` and `source_author` carry distinct actual identities.
- `bindings` exactly matches the output of `plan.review_bindings(operation, raw_operation_bytes)`. The literal review also binds `source_review_sha256`, the exact source review file hash.
- `scopes` exactly matches `plan.SOURCE_SCOPES` or `plan.LITERAL_SCOPES`, respectively.

The old independently reviewed full report and its fractional timing remain byte-pinned historical inputs. Fresh Cloud scopes and literal approval govern this operation. The operator claims a single-use receipt before provisioning.

```sh
python -B scripts/sql-review/cloud-two-history-owned-v2/operation.py \
  --execute-reviewed-cloud-f0-two-history-owned-v2 --packet "$packet"
```

The retained logical sequence gates role credential activation on a closed first two-history deployment, original-grantor finalization, and actual two applied ledger rows. It uses the original independently reviewed native catalogue, 416-expression oracle, and ledger registration and checks. It verifies real Prisma status and a second deployment with the no-pending marker, all eight ledger columns and the native comparison. Sanitized evidence retains exact artifact identities and the first failure. An unclear transport or inner Prisma closure ends the experiment, suppresses later SQL, and goes to exact run-owned cleanup. Source comparisons and the original covered native expectations have offline test coverage. Docker and PostgreSQL execute only under the fresh independent reviews and live checks.
