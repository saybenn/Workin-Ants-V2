-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.
BEGIN;
SET LOCAL search_path=pg_catalog;
DELETE FROM "app"."age_gate_blocks" WHERE "id"='fa5ae422-2763-50fc-bfcb-0a910eacacce'::pg_catalog.uuid RETURNING 1;
ROLLBACK;
