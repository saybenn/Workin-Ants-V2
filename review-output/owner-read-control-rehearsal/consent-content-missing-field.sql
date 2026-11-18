SELECT 'WA_OR_BEFORE_CONSENT_CONTENT_MISSING_FIELD';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.consent_content_revision WHERE id='0b3122ab-b71d-5181-b5ab-0ab8801e1069'),'foreign',(SELECT count(*) FROM app.consent_content_revision WHERE id='fd95bcef-6d6e-5a7d-b560-d4770c720604'));
SELECT 'WA_OR_AFTER_CONSENT_CONTENT_MISSING_FIELD';
COMMIT;
