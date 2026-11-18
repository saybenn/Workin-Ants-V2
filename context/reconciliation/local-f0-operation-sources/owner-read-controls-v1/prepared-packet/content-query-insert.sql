SELECT 'WA_OR_BEFORE_CONTENT_QUERY_INSERT';
INSERT INTO app.consent_content_revision (id,type,version,locale,jurisdiction_scope,content_text,content_hash,review_state,effective_from) VALUES ('ce8e0289-565e-5039-b363-b380f57b607f','terms','owner-read-denied','en','synthetic','Synthetic owner-read consent text; no legal or publisher qualification.',encode(sha256(convert_to('Synthetic owner-read consent text; no legal or publisher qualification.','UTF8')),'hex'),'test_only',clock_timestamp()-interval '1 day');
SELECT 'WA_OR_AFTER_CONTENT_QUERY_INSERT';
COMMIT;
