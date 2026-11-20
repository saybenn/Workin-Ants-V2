SELECT jsonb_build_object('read13_marker','G7-A'::text,'position','BEFORE'::text);
INSERT INTO app.consent_disposition (fingerprint,id,kind,presentation_id,proof_id,semantic_key,user_id) VALUES ('a3a04a02ce64d23ab5b748b0cfb5835f0eeb9a52c2f5dfffef162c21de75602c','39c1897f-137b-5f63-9806-799d488d2647','declined','a34cbb12-fce5-5c24-9495-680edb4d956f',NULL,'read13/0b7c519e-68be-4c44-ac42-83adcfe0def4/A/declined/v1','69cd9608-d6ac-5008-8f3f-b8e93b909590');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G7-A'::text,'position','AFTER'::text);
COMMIT;
