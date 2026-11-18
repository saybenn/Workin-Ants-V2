SELECT 'WA_OR_BEFORE_CONSENT_PRESENTATION_MISSING_FIELD';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.consent_presentation WHERE id='d81e95df-189f-55b8-8010-9e0fbd116be8'),'foreign',(SELECT count(*) FROM app.consent_presentation WHERE id='8eab887c-82a4-5010-96b4-f47c29d1054e'),'ConsentContentRevision_related',(SELECT count(*) FROM app.consent_content_revision WHERE id='0b3122ab-b71d-5181-b5ab-0ab8801e1069'),'ConsentContentRevision_foreign_related',(SELECT count(*) FROM app.consent_content_revision WHERE id='fd95bcef-6d6e-5a7d-b560-d4770c720604'));
SELECT 'WA_OR_AFTER_CONSENT_PRESENTATION_MISSING_FIELD';
COMMIT;
