SELECT 'WA_OR_BEFORE_FIXTURE_CONSENTLOG_0';
INSERT INTO app.consent_logs (id,user_id,type,version,accepted_at,acceptance_key,fingerprint,action_owner,action,context_owner,context_kind,context_id,presentation_hash,content_revision_id,presentation_id) VALUES ('0d4c2bf9-73a1-5305-9812-ebeaf6aee155','078052af-7e37-53e9-a1ae-462cceb06d30','terms','owner-read-0',clock_timestamp()+interval '1 second','owner-read-0','ae38495ea42df3a717e0e78cb26bf6a0ec20c4a44a36339f229999be8a0ab297','consent_disclosure','SH-007.v1','consent_disclosure','ConsentLog','0d4c2bf9-73a1-5305-9812-ebeaf6aee155',encode(sha256(convert_to('Synthetic exact owner-read rendering; no actual UI rendered.','UTF8')),'hex'),'0b3122ab-b71d-5181-b5ab-0ab8801e1069','d81e95df-189f-55b8-8010-9e0fbd116be8');
SELECT jsonb_build_object('inserted_fixture',1);
SELECT 'WA_OR_AFTER_FIXTURE_CONSENTLOG_0';
COMMIT;
