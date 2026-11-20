BEGIN;
SET LOCAL search_path=pg_catalog;
UPDATE platform.database_action_grant SET "principal_user_id"='__WA_CHANGED_VALUE__'::pg_catalog.uuid WHERE id='__WA_OWN_GRANT_ID__'::uuid RETURNING 1;
ROLLBACK;
