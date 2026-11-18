SELECT 'WA_OR_BEFORE_FIXTURE_CONSENTPRESENTATION_1';
INSERT INTO app.consent_presentation (id,content_revision_id,user_id,action_owner,action,render_version,rendered_text,rendered_hash,context_owner,context_kind,context_id) VALUES ('8eab887c-82a4-5010-96b4-f47c29d1054e','fd95bcef-6d6e-5a7d-b560-d4770c720604','078052af-7e37-53e9-a1ae-462cceb06d30','consent_disclosure','SH-007.v1','owner-read.v1','Synthetic exact owner-read rendering; no actual UI rendered.',encode(sha256(convert_to('Synthetic exact owner-read rendering; no actual UI rendered.','UTF8')),'hex'),'consent_disclosure','ConsentLog','06f4eb9c-7c65-5620-af16-cfa72d077234');
SELECT jsonb_build_object('inserted_fixture',1);
SELECT 'WA_OR_AFTER_FIXTURE_CONSENTPRESENTATION_1';
COMMIT;
