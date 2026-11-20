SELECT jsonb_build_object('read13_marker','G5-AB'::text,'position','BEFORE'::text);
INSERT INTO app.consent_content_revision (content_hash,content_text,effective_from,effective_until,id,jurisdiction_scope,legal_approval_ref,locale,review_state,type,version) VALUES ('b2159e405907569aff03a73c11cf3b017ba8833364da446758ef516078efcc6e','Read13 synthetic fixture A; not legal disclosure or business acceptance.',transaction_timestamp()-interval '1 day',NULL,'e005a594-3116-5a54-a827-bf9c576a29ad','fixture:US',NULL,'en-US','test_only','terms','read13-fixture-A-v1');
INSERT INTO app.consent_content_revision (content_hash,content_text,effective_from,effective_until,id,jurisdiction_scope,legal_approval_ref,locale,review_state,type,version) VALUES ('14786ff8b96e31c8ed3cb3461a9ae94f8e124daad2c963a4892910ebf19978fb','Read13 synthetic fixture B; not legal disclosure or business acceptance.',transaction_timestamp()-interval '1 day',NULL,'53bd0b00-c5ea-5477-aed5-a0d089ab7558','fixture:US',NULL,'en-US','test_only','terms','read13-fixture-B-v1');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G5-AB'::text,'position','AFTER'::text);
COMMIT;
