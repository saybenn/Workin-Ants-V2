BEGIN;
GRANT wa_private_helper_owner,wa_customer_verifier,wa_track_verifier TO wa_schema_owner WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;
COMMIT;
