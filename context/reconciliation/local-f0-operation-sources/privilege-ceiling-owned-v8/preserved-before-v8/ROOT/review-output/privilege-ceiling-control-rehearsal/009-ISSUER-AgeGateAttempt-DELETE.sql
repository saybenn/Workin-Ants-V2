-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."age_gate_attempts" WHERE "id"='fed3a5b0-1787-53de-8605-28dd0e1a2220'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
