SELECT jsonb_build_object('read13_marker','G6-A'::text,'position','BEFORE'::text);
INSERT INTO app.consent_presentation (action,action_owner,content_revision_id,context_id,context_kind,context_owner,id,render_version,rendered_hash,rendered_text,user_id) VALUES ('SH-004.v1','customer_buyer_profile','58ba0b62-b277-5953-994e-cf155a3d0057','d4fd559a-4273-5e9b-9c4d-4a66e0760626','CustomerProfile','customer_buyer_profile','128c8a77-f59a-5a02-bc2b-92237ac491c4','read13-fixture-v1','b2159e405907569aff03a73c11cf3b017ba8833364da446758ef516078efcc6e','Read13 synthetic fixture A; not legal disclosure or business acceptance.','7d36437b-1a82-5632-a6a7-f6f74da0137c');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G6-A'::text,'position','AFTER'::text);
COMMIT;
