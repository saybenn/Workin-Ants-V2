BEGIN;
UPDATE platform.database_action_grant SET revoked_at=clock_timestamp() WHERE id='__WA_OWN_GRANT_ID__'::uuid RETURNING 1;
ROLLBACK;
