-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "platform"."owner_mutation_evidence" WHERE "id"='c5cf03a7-ebee-5a21-b1bb-35033da4fe45'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
