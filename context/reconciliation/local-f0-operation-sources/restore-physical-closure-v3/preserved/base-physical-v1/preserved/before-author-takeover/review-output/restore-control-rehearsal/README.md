# RESTORE01 proposed physical synthetic rehearsal

Source-only NOT_RUN proposal; no executable coordinator is included. A separately
reviewed root operator/literal source, staging, target and private-artifact manifest
is mandatory before any creation. Existing P0C-RESTORE-01 remains NOT_RUN.

Create a real whole-cluster pg_basebackup with streamed WAL and SHA256 manifest;
verify it using the same pinned 17.11 tools. A protected archive contains role
password verifiers: keep it outside Git under owner-only protection, export only
aggregate hashes/counts, and destroy every exact owned copy/PGDATA volume at end.
Restore into an empty owned volume, verify again, then start under an admin-only
HBA. Never run initdb, bootstrap, application SQL or a migration on restored data.
Compare all42 table rows, catalog, ledger and role authority before any transition.

Rotate all six target credentials independently before restricted diagnostics.
Actual Identity SQL performs a clearly synthetic revoke/recover simulation before
any other restored service login. Five finite diagnostic probes use the existing
Customer SELECT and pending-work SELECT scopes only; no worker claim or serving.
Old-source tuple denial requires its exact still-unexpired grant and unchanged user
generation. An expired grant cannot be relabeled as proof of tuple invalidation.

The whole SERVICE-RESTORE vector and real Privacy generation/marker replay remain
blocked by P0F_PRIVACY_RESTORE_GENERATION_PORT. This proposal never fabricates a
Privacy marker or treats an empty Privacy inventory as proof. Every case, assertion
and proposed subprobe stays NOT_RUN; synthetic SQL does not qualify owner adapters.

The proposal JSON specifies exact stages, copies, expected state and controlled
deltas, HBA order, tools, protections, STOP rules and owned cleanup. Physical backup
is selected because it preserves cluster roles/globals; a logical variant needs a
separate globals/ownership design. No production restore or RPO/RTO is claimed.

Plain English: Make a real locked copy of the toy database. Put the copy in a new
locked box. Check that every piece came back. Change all keys before testing a few
doors. Keep the box closed because the real privacy repair work is still missing.
