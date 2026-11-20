SELECT jsonb_build_object('read13_marker','G6-B'::text,'position','BEFORE'::text);
INSERT INTO app.consent_presentation (action,action_owner,content_revision_id,context_id,context_kind,context_owner,id,render_version,rendered_hash,rendered_text,user_id) VALUES ('SH-004.v1','customer_buyer_profile','1b4b3688-b9c6-5ac7-9af1-dda84b5acf50','9d6a8241-8c72-5540-b494-55dca1468442','CustomerProfile','customer_buyer_profile','6a167adf-6699-5ac9-92f6-e3728b6becb9','read13-fixture-v1','14786ff8b96e31c8ed3cb3461a9ae94f8e124daad2c963a4892910ebf19978fb','Read13 synthetic fixture B; not legal disclosure or business acceptance.','f43120a8-db4f-5202-9172-fd5ec7787940');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G6-B'::text,'position','AFTER'::text);
COMMIT;
