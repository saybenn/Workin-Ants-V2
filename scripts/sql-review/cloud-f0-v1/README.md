# Cloud F0 capability probe v1

Run from the Cloud checkout with Bash, Python 3.11 or later, native Git, and the managed rootless Linux/amd64 Docker service. Use the existing checkout and leave the legacy database write aliases gated. For the app, run `bash scripts/setup-cloud-phase0-v1.sh`, export the toolchain path printed by the script, then run `npm run check`, `npm run test:foundation`, and `npm run db:validate`. The usual development entry is `npm run dev -- --hostname 127.0.0.1`. Use only process-local smoke checks when no Cloud portal is needed.

## Operational scope

The probe creates one new synthetic PostgreSQL database inside an isolated container and verifies that the Cloud route supports actual restricted connections, denial, concurrent observation, and recovery after a deliberate crash. There is no Workin Ants candidate migration, application schema, or business qualification. The published Windows runner, image manifest, history, and approvals remain historical inputs. This separate profile binds the observed Unix socket and rootless daemon to one reviewed operation.

Before preparing, cache the pinned immutable image on the managed daemon. This pull preserves the platform registry and TLS configuration.

```sh
env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  docker --host=unix:///var/run/docker.sock pull --platform linux/amd64 \
  docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1

python -B -m unittest discover -s scripts/sql-review/cloud-f0-v1 -v
python -B scripts/sql-review/cloud-f0-v1/probe.py prepare
```

Prepare reads exact current and committed source bytes, inspects the live daemon and cached image, and writes a fresh private manifest. Have an independent reviewer examine the actual manifest and contained operations. To approve, the reviewer writes an owner-only `review.json` beside it using schema `workinants.cloud-f0-literal-review.v1`, decision `APPROVE`, their own reviewer identity, the exact `manifest_sha256`, and the four ordered `APPROVALS` fields in the runner.

```sh
python -B scripts/sql-review/cloud-f0-v1/probe.py execute \
  --manifest /workspace/scratch/wa-cloud-f0-probe-RUN/manifest.json \
  --review /workspace/scratch/wa-cloud-f0-probe-RUN/review.json
```

Each manifest allows a single attempt. The report retains allowlisted results, source and resource identities, successful prefixes and a stopped stage if applicable. A missing receipt or an unexpected result leaves that case unqualified. After any interruption verify the recorded daemon, exact container ID and labels, volume creation identity, and private path before attempting recovery. Check both Docker inventories and private-path absence before admitting cleanup. Retain the pinned image. Never print client credentials or use broad cleanup commands.
