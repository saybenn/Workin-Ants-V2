SELECT jsonb_build_object('read13_marker','G6-B'::text,'position','BEFORE'::text);
INSERT INTO app.consent_presentation (action,action_owner,content_revision_id,context_id,context_kind,context_owner,id,render_version,rendered_hash,rendered_text,user_id) VALUES ('SH-004.v1','customer_buyer_profile','53bd0b00-c5ea-5477-aed5-a0d089ab7558','fdb9d7da-2124-5a29-a0d5-ca2e1a3ecc22','CustomerProfile','customer_buyer_profile','d90aa745-7230-5809-a910-781c30f79252','read13-fixture-v1','14786ff8b96e31c8ed3cb3461a9ae94f8e124daad2c963a4892910ebf19978fb','Read13 synthetic fixture B; not legal disclosure or business acceptance.','d74b5d30-94cf-5a35-9c5e-1247e02b13e9');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G6-B'::text,'position','AFTER'::text);
COMMIT;
