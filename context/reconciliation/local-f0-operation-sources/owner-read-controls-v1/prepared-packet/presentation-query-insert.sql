SELECT 'WA_OR_BEFORE_PRESENTATION_QUERY_INSERT';
INSERT INTO app.consent_presentation (id,content_revision_id,user_id,action_owner,action,render_version,rendered_text,rendered_hash,context_owner,context_kind,context_id) VALUES ('d9e1b1ad-84da-5316-b401-23411fb2e05c','0b3122ab-b71d-5181-b5ab-0ab8801e1069','078052af-7e37-53e9-a1ae-462cceb06d30','consent_disclosure','SH-007.v1','owner-read.v1','Synthetic exact owner-read rendering; no actual UI rendered.',encode(sha256(convert_to('Synthetic exact owner-read rendering; no actual UI rendered.','UTF8')),'hex'),'consent_disclosure','ConsentLog','0d4c2bf9-73a1-5305-9812-ebeaf6aee155');
SELECT 'WA_OR_AFTER_PRESENTATION_QUERY_INSERT';
COMMIT;
