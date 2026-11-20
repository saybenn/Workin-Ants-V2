SELECT jsonb_build_object('read13_marker','G7-B'::text,'position','BEFORE'::text);
INSERT INTO app.consent_disposition (fingerprint,id,kind,presentation_id,proof_id,semantic_key,user_id) VALUES ('c119af16c36728d99c3709d513d7a6a8069ffc40b766ade015152c3ac71822d5','6212d5c0-8c07-50d3-ba59-65a8427b1520','declined','d90aa745-7230-5809-a910-781c30f79252',NULL,'read13/0b7c519e-68be-4c44-ac42-83adcfe0def4/B/declined/v1','d74b5d30-94cf-5a35-9c5e-1247e02b13e9');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G7-B'::text,'position','AFTER'::text);
COMMIT;
