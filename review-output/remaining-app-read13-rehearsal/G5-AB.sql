SELECT jsonb_build_object('read13_marker','G5-AB'::text,'position','BEFORE'::text);
INSERT INTO app.consent_content_revision (content_hash,content_text,effective_from,effective_until,id,jurisdiction_scope,legal_approval_ref,locale,review_state,type,version) VALUES ('b2159e405907569aff03a73c11cf3b017ba8833364da446758ef516078efcc6e','Read13 synthetic fixture A; not legal disclosure or business acceptance.',transaction_timestamp()-interval '1 day',NULL,'58ba0b62-b277-5953-994e-cf155a3d0057','fixture:US',NULL,'en-US','test_only','terms','read13-fixture-A-v1');
INSERT INTO app.consent_content_revision (content_hash,content_text,effective_from,effective_until,id,jurisdiction_scope,legal_approval_ref,locale,review_state,type,version) VALUES ('14786ff8b96e31c8ed3cb3461a9ae94f8e124daad2c963a4892910ebf19978fb','Read13 synthetic fixture B; not legal disclosure or business acceptance.',transaction_timestamp()-interval '1 day',NULL,'1b4b3688-b9c6-5ac7-9af1-dda84b5acf50','fixture:US',NULL,'en-US','test_only','terms','read13-fixture-B-v1');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G5-AB'::text,'position','AFTER'::text);
COMMIT;
