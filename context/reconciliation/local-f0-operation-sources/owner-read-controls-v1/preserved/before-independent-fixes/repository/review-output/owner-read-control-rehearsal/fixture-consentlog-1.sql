SELECT 'WA_OR_BEFORE_FIXTURE_CONSENTLOG_1';
INSERT INTO app.consent_logs (id,user_id,type,version,accepted_at,acceptance_key,fingerprint,action_owner,action,context_owner,context_kind,context_id,presentation_hash,content_revision_id,presentation_id) VALUES ('06f4eb9c-7c65-5620-af16-cfa72d077234','078052af-7e37-53e9-a1ae-462cceb06d30','terms','owner-read-1',clock_timestamp()+interval '1 second','owner-read-1','48d84cd2f97653568cf0f8c4351db0b3cefc65e74405c3ecbae6e5220bce7ed8','consent_disclosure','SH-007.v1','consent_disclosure','ConsentLog','06f4eb9c-7c65-5620-af16-cfa72d077234',encode(sha256(convert_to('Synthetic exact owner-read rendering; no actual UI rendered.','UTF8')),'hex'),'fd95bcef-6d6e-5a7d-b560-d4770c720604','8eab887c-82a4-5010-96b4-f47c29d1054e');
SELECT jsonb_build_object('inserted_fixture',1);
SELECT 'WA_OR_AFTER_FIXTURE_CONSENTLOG_1';
COMMIT;
