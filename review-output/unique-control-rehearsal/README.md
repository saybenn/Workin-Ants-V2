# Proposed finite UNIQUE races

Source-only, NOT_RUN. Exact existing P0C-UNIQUE-01 only, with the existing closed
SH004 result and complete Customer group. Five finite schedules: identical and
changed fingerprint collisions with holder COMMIT or ROLLBACK; identical text key
under two separate legitimate Customer subjects where both complete groups commit.
The privileged wait observer proves actual overlapping transactions; a timeout or
sequential duplicate is not concurrency evidence. No protected row is privileged-seeded.

Native23505 proves only storage uniqueness. It is never a production idempotency
API response. Existing Customer UPDATE/CAS missing result codecs, owner-generation
ports, usage/Privacy and worker-loop paths remain held. The concurrency matrix
distinguishes missing owner contracts from separately preparable lease/revoke work.

Only two exact owner_commit triggers are bypassed for synthetic Identity facts;
all physical guards remain. Exact trigger restoration and complete native parity
are required before any actual restricted operation. A separate reviewed target,
authentication, transport/diagnostic/barrier wrapper and cleanup remain mandatory.

Native diagnostic and wait SQL builders are source-only helpers in the proposed
protocol. PG17.11 BuildIndexValueDescription suppresses key DETAIL when RLS is
enabled; this actual restricted app path therefore expects no key-value DETAIL.
The native B-tree unique error still identifies the exact schema/table/index.
Primary source: https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/access/index/genam.c
and https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/access/nbtree/nbtinsert.c

Plain English: Two real keys try to save the same ticket at once. We first prove
one is waiting for the other. Keeping the first ticket blocks a duplicate; tearing
it up lets the waiting ticket finish. Different customers may use the same words.
