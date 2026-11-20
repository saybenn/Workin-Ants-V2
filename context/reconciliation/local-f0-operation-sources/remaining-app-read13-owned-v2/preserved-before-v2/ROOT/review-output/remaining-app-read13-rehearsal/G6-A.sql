SELECT jsonb_build_object('read13_marker','G6-A'::text,'position','BEFORE'::text);
INSERT INTO app.consent_presentation (action,action_owner,content_revision_id,context_id,context_kind,context_owner,id,render_version,rendered_hash,rendered_text,user_id) VALUES ('SH-004.v1','customer_buyer_profile','e005a594-3116-5a54-a827-bf9c576a29ad','76b7a107-ed42-5471-9d24-946e10c38a4f','CustomerProfile','customer_buyer_profile','a34cbb12-fce5-5c24-9495-680edb4d956f','read13-fixture-v1','b2159e405907569aff03a73c11cf3b017ba8833364da446758ef516078efcc6e','Read13 synthetic fixture A; not legal disclosure or business acceptance.','69cd9608-d6ac-5008-8f3f-b8e93b909590');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G6-A'::text,'position','AFTER'::text);
COMMIT;
