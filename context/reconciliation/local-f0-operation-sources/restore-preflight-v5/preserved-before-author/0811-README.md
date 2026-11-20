# CTX01 proposed finite source packet

This packet is source-only and NOT_RUN. It selects existing P0C-CTX-01 only.
Every operation requires a separately reviewed coordinator and fresh owned target.
The original source packet, canonical SQL and 32 worker ACL rows are unchanged.

The actual app creates one complete Customer source group, first rolling that
same group back, then committing a fresh authorization in a new xid on the same
backend. Only after closure may an independent observer check the complete group.
The actual app schedules one pending job; the actual worker reads it under its
existing transport claim scope. No lease, claim, worker loop or Track enrollment.

A savepoint rollback clears the local hash, while the independently committed
grant survives. Rebinding the same grant in that live xid is allowed. A new xid
needs a new grant. GUCs cannot create a missing issuer row: the context hash is
transport for the independently committed exact tuple, never a second authority.

Grant retention is deliberately a runtime-only fixed query contract, not a query
with fake IDs: grant UUIDs and secrets are freshly allocated per issuance. Its
reviewed implementation is a mandatory missing coordinator dependency, not PASS.

Customer resolve is an existing SELECT-only purpose. Its otherwise exact UPDATE
caps must still update zero rows. This proves only that scoped SQL boundary;
missing update result codecs, owner adapters and broader read purposes stay held.

Plain English: A key works for one real trip. Going back to a bookmark may erase
the key from the pocket, but the same trip may pick it up again. A new trip needs
a new key. Writing a pretend name on paper cannot make a real key.
