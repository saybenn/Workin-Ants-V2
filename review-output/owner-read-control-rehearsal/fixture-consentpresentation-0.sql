SELECT 'WA_OR_BEFORE_FIXTURE_CONSENTPRESENTATION_0';
INSERT INTO app.consent_presentation (id,content_revision_id,user_id,action_owner,action,render_version,rendered_text,rendered_hash,context_owner,context_kind,context_id) VALUES ('d81e95df-189f-55b8-8010-9e0fbd116be8','0b3122ab-b71d-5181-b5ab-0ab8801e1069','078052af-7e37-53e9-a1ae-462cceb06d30','consent_disclosure','SH-007.v1','owner-read.v1','Synthetic exact owner-read rendering; no actual UI rendered.',encode(sha256(convert_to('Synthetic exact owner-read rendering; no actual UI rendered.','UTF8')),'hex'),'consent_disclosure','ConsentLog','0d4c2bf9-73a1-5305-9812-ebeaf6aee155');
SELECT jsonb_build_object('inserted_fixture',1);
SELECT 'WA_OR_AFTER_FIXTURE_CONSENTPRESENTATION_0';
COMMIT;
