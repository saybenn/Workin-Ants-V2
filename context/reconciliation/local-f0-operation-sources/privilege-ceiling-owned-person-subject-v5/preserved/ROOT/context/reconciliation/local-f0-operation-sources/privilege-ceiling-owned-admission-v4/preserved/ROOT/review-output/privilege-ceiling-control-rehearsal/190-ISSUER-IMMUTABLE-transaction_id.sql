BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE platform.database_action_grant SET "transaction_id"='__WA_CHANGED_VALUE__'::pg_catalog.text WHERE id='__WA_OWN_GRANT_ID__'::uuid RETURNING 1;
ROLLBACK;
