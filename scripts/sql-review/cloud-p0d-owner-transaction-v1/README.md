# Cloud P0-D owner transaction smoke test

This test uses one fresh disposable PostgreSQL 17.11 container under Posture D. It exercises the server transaction boundary with two separate restricted Postgres.js 3.4.7 connections. Fixtures use the existing synthetic Customer and exact work identities. The only privileged mutations prepare the reviewed synthetic Identity rows and restore the two affected trigger settings in the same transaction.

Use the pinned Cloud parser and Prisma tool archive from the [Cloud checklist](../../../context/reconciliation/cloud-phase0-execution.md). Prepare an exact-source packet from the committed branch.

```bash
python -B scripts/sql-review/cloud-p0d-owner-transaction-v1/run.py prepare --tool-archive "$verified_prisma_archive"
python -B scripts/sql-review/cloud-p0d-owner-transaction-v1/run.py verify --packet "$held_packet"
```

The `--draft` prepare and verify option permits offline review of work before commit. An independent reviewer verifies the committed source, cached tools, exact live daemon and single-use resource names, then writes the owner-only source and literal receipts beside `operation.json`. Receipt schemas, exact bindings, and scopes are defined by `run.py`.

```bash
python -B scripts/sql-review/cloud-p0d-owner-transaction-v1/run.py execute \
  --execute-reviewed-cloud-p0d-owner-transaction-v1 --packet "$held_packet"
```

Inside the owned target, the genuine two-migration cycle and unchanged no-op precede the test. Node reads the two synthetic passwords over standard input and connects to the isolated loopback database as application runtime and context issuer. The test checks actual restricted commits, context isolation between transactions, and rollback. Native, ledger, client closure, and exact resource cleanup are recorded separately. The evidence covers the transaction boundary and exercised fixtures. Integrated dispatch, hosted authority and production use require separate evidence.
