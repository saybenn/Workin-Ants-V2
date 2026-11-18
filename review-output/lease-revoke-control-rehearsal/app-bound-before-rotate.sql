SELECT 'WA_LR_BEFORE_APP_BOUND_BEFORE_ROTATE';
WITH changed AS (INSERT INTO platform.runtime_work_item (id,outbox_message_id,handler_name,semantic_work_key,state,fence,attempt_count) VALUES ('84f4bdd6-1ae3-596c-be85-03f813ec485b'::uuid,'4fb987b5-d5c7-500d-abd0-0cd168013c1d'::uuid,'assignDefaultFreeTrack.v1','customer_buyer_profile/ecf86e2e-63cb-5fad-a553-42fa370907af/default-free-enrollment/v1','pending',0,0) RETURNING 1) SELECT jsonb_build_object('changed',count(*)) FROM changed;
SELECT 'WA_LR_AFTER_APP_BOUND_BEFORE_ROTATE';
COMMIT;
