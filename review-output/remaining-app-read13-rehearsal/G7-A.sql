SELECT jsonb_build_object('read13_marker','G7-A'::text,'position','BEFORE'::text);
INSERT INTO app.consent_disposition (fingerprint,id,kind,presentation_id,proof_id,semantic_key,user_id) VALUES ('a3a04a02ce64d23ab5b748b0cfb5835f0eeb9a52c2f5dfffef162c21de75602c','0d227778-2dcc-5dbb-b7d6-a10509ed527f','declined','128c8a77-f59a-5a02-bc2b-92237ac491c4',NULL,'read13/d848e852-f857-4c03-8288-4893e2e8aa0c/A/declined/v1','7d36437b-1a82-5632-a6a7-f6f74da0137c');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G7-A'::text,'position','AFTER'::text);
COMMIT;
